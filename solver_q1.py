# -*- coding: utf-8 -*-
"""
问题1 预热平衡阶段求解器 v2（P0 修订版）
====================================================
模型（附录2 逐字核对后）：
  温度:  dT/dt = alpha * (1/r) d/dr(r dT/dr),  alpha = k/(rho*cp) = 常数
  水分:  dC/dt = (1/r) d/dr(r D(C) dC/dr),     D(C) = 7e-9 * exp(-0.89/C)
  初值:  T(r,0)=28 (题面,药材),  C(r,0)=2.55
  边界:  r=0 对称;  r=R Robin:
         温度  k dT/dr = h (T_inf - T)          （无潜热项——附录2未给）
         水分  D dC/dr = h_m (C_inf - C)
  附件1: T_inf(t), C_inf(t) 线性插值（t=0 时烘房恰为 28°C/0.01963，与药材初值巧合相等）
离散（P0②节点中心制）：
  节点 r_j = j*dr, j=0..n-1, R=(n-1)*dr; 输出网格 dr=0.1cm (n=21)
  有限体积（轴对称、约去2π、单位高度）：
    V0 = dr^2/4,  Vj = 2*j*dr^2 (1<=j<=n-2),  Vn = ((n-1)-1/4)*dr^2
    界面面积 A = r_face;  界面系数：温度 alpha，水分 D 的调和平均（P0③）
    轴线节点即 L'Hopital 形式 2d/dr^2*(phi1-phi0)
  时间：Crank-Nicolson，前2步全隐式（Rannacher）
  非线性：每步 Picard 迭代（欠松弛0.5，容差1e-12），C 下限 1e-6 防溢出
"""
import numpy as np
import openpyxl
from scipy.linalg import solve_banded

# ---------- 附录2 参数（逐字核对） ----------
RHO, CP, K = 820.0, 2600.0, 0.36      # kg/m3, J/(kg K), W/(m K)
H_T, H_M = 25.0, 8e-7                 # W/(m2 K), m/s
ALPHA = K / (RHO * CP)                # 1.6854e-7 m2/s
T0, C0 = 28.0, 2.55
R = 0.02                              # m
D_MIN_CAP = 1e-6                      # C 下限保护（kg/kg）
T_END = 1800.0


def D_of_C(C):
    """附录2 原式: D = 7e-9 * exp(-0.89/C)  （注意 C 在分母！）"""
    return 7e-9 * np.exp(-0.89 / np.maximum(C, D_MIN_CAP))


def load_env(path="A题/附件/附件1.xlsx"):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]
    t = np.array([r[0] for r in rows], float)
    T = np.array([r[1] for r in rows], float)
    C = np.array([r[2] for r in rows], float)
    return t, T, C


def assemble(r_node, d_node, gS):
    """
    任意（非均匀）节点位置的守恒型有限体积算子，向量化。
    返回三对角分量 (sub, dia, sup)（1/s）与表面源系数 svec（1/s）。
    约定：r_node[0]=0（轴线，节点即边界），r_node[-1]=R（表面，节点即边界）。
    界面 r_f[j]=(r[j-1]+r[j])/2；控制体 V_j=(r_R^2-r_L^2)/2；界面面积 A=r_f（约去2π）。
    表面 Robin 项以 gS = h*R/V_last（水分）或 h*R/(rho*cp*V_last)（温度）传入。
    """
    n = r_node.size
    rf = np.empty(n + 1)
    rf[0] = 0.0
    rf[1:n] = 0.5 * (r_node[:-1] + r_node[1:])
    rf[n] = r_node[-1]
    h = np.diff(r_node)                              # 节点间距，长度 n-1
    d_int = np.empty(n + 1)                          # 界面扩散系数（调和平均）
    d_int[0] = 0.0
    d_int[1:n] = 2.0 * d_node[:-1] * d_node[1:] / (d_node[:-1] + d_node[1:])
    d_int[n] = d_node[-1]
    V = np.empty(n)
    V[0] = rf[1] ** 2 / 2.0
    V[1:n - 1] = (rf[2:n] ** 2 - rf[1:n - 1] ** 2) / 2.0
    V[-1] = (rf[n] ** 2 - rf[n - 1] ** 2) / 2.0
    sub = np.zeros(n); dia = np.zeros(n); sup = np.zeros(n); svec = np.zeros(n)
    # 轴线节点 j=0: 左界面 A=0
    c0 = d_int[1] * rf[1] / (V[0] * h[0])
    dia[0] = -c0; sup[0] = c0
    # 内点
    cL = d_int[1:n - 1] * rf[1:n - 1] / (V[1:n - 1] * h[0:n - 2])
    cR = d_int[2:n] * rf[2:n] / (V[1:n - 1] * h[1:n - 1])
    sub[1:n - 1] = cL; sup[1:n - 1] = cR; dia[1:n - 1] = -(cL + cR)
    # 表面节点：左界面 + Robin
    cLs = d_int[n - 1] * rf[n - 1] / (V[-1] * h[-1])
    sub[-1] = cLs; dia[-1] = -cLs - gS; svec[-1] = gS
    return sub, dia, sup, svec


def thomas(ab, d):
    n = d.size
    cp_ = np.zeros(n - 1); dp_ = np.zeros(n)
    dp_[0] = d[0] / ab[0, 1]
    if n > 1:
        cp_[0] = ab[0, 2] / ab[0, 1]
    for i in range(1, n):
        den = ab[i, 1] - ab[i, 0] * cp_[i - 1]
        dp_[i] = (d[i] - ab[i, 0] * dp_[i - 1]) / den
        if i < n - 1:
            cp_[i] = ab[i, 2] / den
    x = np.empty(n); x[-1] = dp_[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp_[i] - cp_[i] * x[i + 1]
    return x


def apply_tri(sub, dia, sup, x):
    """三对角矩阵-向量乘 L@x"""
    n = x.size
    y = dia * x
    y[:-1] += sup[:-1] * x[1:]
    y[1:] += sub[1:] * x[:-1]
    return y


def step_cn(x, tri, svec, amb_new, amb_old, dt, theta):
    sub, dia, sup = tri
    ab = np.zeros((3, x.size))
    ab[0, 1:] = -theta * dt * sup[:-1]
    ab[1, :] = 1.0 - theta * dt * dia
    ab[2, :-1] = -theta * dt * sub[1:]
    Lx = apply_tri(sub, dia, sup, x)
    rhs = x + (1 - theta) * dt * Lx + dt * svec * (theta * amb_new + (1 - theta) * amb_old)
    return solve_banded((1, 1), ab, rhs)


def build_nodes(k=1):
    """
    计算网格：包含全部 21 个输出节点（r=0..2.0cm 步长0.1cm），
    表面侧区间按 k 倍细分（水分边界层早期深度 sqrt(D*t) 在 t=1s 仅 ~70um，
    均匀 1mm 网格无法解析 -> 表面列一阶误差；聚类后恢复二阶）。
    返回 (节点数组, 输出节点索引)。
    """
    base = np.arange(21) * 0.001
    subs = [1] * 20
    subs[15] = 4 * k; subs[16] = 6 * k; subs[17] = 10 * k
    subs[18] = 20 * k; subs[19] = 40 * k
    nodes = [0.0]; out_idx = [0]
    for j in range(20):
        m = subs[j]
        for s in range(1, m + 1):
            nodes.append(base[j] + (base[j + 1] - base[j]) * s / m)
        out_idx.append(len(nodes) - 1)
    return np.array(nodes), np.array(out_idx)


def run(k=1, dt=0.25, cn=True):
    r_node, out_idx = build_nodes(k)
    n = r_node.size
    R = r_node[-1]
    t_env, T_env, C_env = load_env()
    times = np.arange(0.0, T_END + 1e-9, dt)
    T_amb = np.interp(times, t_env, T_env)
    C_amb = np.interp(times, t_env, C_env)
    Vn = (R ** 2 - ((r_node[-2] + R) / 2.0) ** 2) / 2.0
    gS_T = H_T * R / (RHO * CP * Vn)
    gS_C = H_M * R / Vn
    out_t = np.arange(0.0, T_END + 1e-9, 1.0)
    save_every = int(round(1.0 / dt))

    # ---- 温度（线性）----
    sub, dia, sup, s_T = assemble(r_node, np.full(n, ALPHA), gS_T)
    tri_T = (sub, dia, sup)
    T_out = np.zeros((out_t.size, 21)); x = np.full(n, T0); T_out[0] = x[out_idx]
    for i in range(1, times.size):
        theta = 1.0 if (i <= 2 or not cn) else 0.5
        x = step_cn(x, tri_T, s_T, T_amb[i], T_amb[i - 1], dt, theta)
        if i % save_every == 0:
            T_out[i // save_every] = x[out_idx]

    # ---- 水分（非线性 Picard）----
    C_out = np.zeros((out_t.size, 21)); x = np.full(n, C0); C_out[0] = x[out_idx]
    max_it = 0
    for i in range(1, times.size):
        theta = 1.0 if (i <= 2 or not cn) else 0.5
        guess = x.copy(); err = 1.0; it = 0
        while err > 1e-10 and it < 60:
            Dc = D_of_C(np.maximum(guess, D_MIN_CAP))
            tri_C = assemble(r_node, Dc, gS_C)
            xn = step_cn(x, tri_C[:3], tri_C[3], C_amb[i], C_amb[i - 1], dt, theta)
            err = np.max(np.abs(xn - guess))
            guess = 0.5 * guess + 0.5 * xn
            it += 1
        max_it = max(max_it, it)
        x = np.maximum(guess, 0.0)
        if i % save_every == 0:
            C_out[i // save_every] = x[out_idx]
    return out_t, out_idx, T_out, C_out, max_it


def tables(out_t, r_node, T, C):
    idx_t = [int(t) for t in (100, 300, 600, 900, 1200, 1500, 1800)]
    idx_r = [0, 5, 10, 15, 20]
    print("表1 温度（行=时间s，列=r=0,0.5,1,1.5,2 cm）")
    for t in idx_t:
        print(f"{t:5d}", " ".join(f"{T[t, j]:9.4f}" for j in idx_r))
    print("表2 水分浓度")
    for t in idx_t:
        print(f"{t:5d}", " ".join(f"{C[t, j]:9.4f}" for j in idx_r))


def write_xlsx(path, out_t, T, C):
    wb = openpyxl.Workbook()
    for name, field in (("温度", T), ("水分浓度", C)):
        ws = wb.create_sheet(name)
        ws.append(["时间\\到药材中心的距离"] + [round(j * 0.1, 1) for j in range(21)])
        for i in range(1, out_t.size):
            ws.append([int(out_t[i])] + [round(float(v), 4) for v in field[i]])
        for row in ws.iter_rows(min_row=2, min_col=2):
            for c in row:
                c.number_format = "0.0000"
    del wb["Sheet"]
    wb.save(path)
    print("written:", path)


if __name__ == "__main__":
    import sys
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    dt = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
    out_t, out_idx, T, C, max_it = run(k=k, dt=dt)
    print(f"k={k}, dt={dt}, Picard最大迭代={max_it}")
    tables(out_t, None, T, C)
    write_xlsx(f"outputs/q1/result1_k{k}.xlsx", out_t, T, C)
    np.savez(f"outputs/q1/q1_k{k}.npz", t=out_t, T=T, C=C)
