# -*- coding: utf-8 -*-
"""问题二一维径向变物性温湿耦合求解器。

题目要求问题二统一采用附录3经验公式，因此 0--10800 s 全程使用
附录3场相关物性。7200 s 仅作为烘房温度由升温曲线转入恒温平台的
边界切换时刻；药材内部温度和水分状态连续继承，不作重置。
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
from scipy.linalg import solve_banded


RADIUS = 0.02
T0_C = 28.0
C0 = 2.55
H_T = 25.0
H_M = 8.0e-7
T_SWITCH = 7200.0
T_END = 10800.0
T_PLATEAU_C = 323.157 - 273.15
C_FLOOR = 1.0e-6

# 附录2
RHO_2 = 820.0
CP_2 = 2600.0
K_2 = 0.36


def env_temperature(t):
    """问题一采用的烘房温度拟合，返回摄氏温度。"""
    t = np.asarray(t, dtype=float)
    tk = 323.1565 - 21.7257 * np.exp(-((5.2356e-4 * t) ** 1.172624))
    return tk - 273.15


def env_moisture(t):
    """问题一采用的烘房水分浓度拟合。"""
    t = np.asarray(t, dtype=float)
    return 0.05005150 - 0.02983541 * np.exp(-((3.6338e-4 * t) ** 1.312736))


def props_appendix2(c, t_c):
    shape = np.broadcast(c, t_c).shape
    rho = np.full(shape, RHO_2)
    cp = np.full(shape, CP_2)
    k = np.full(shape, K_2)
    d = 7.0e-9 * np.exp(-0.89 / np.maximum(c, C_FLOOR))
    return rho, cp, k, d


def props_appendix3(c, t_c):
    """附录3经验式；Arrhenius 项严格使用开尔文。"""
    c = np.maximum(np.asarray(c, dtype=float), C_FLOOR)
    tk = np.asarray(t_c, dtype=float) + 273.15
    rho = 650.0 + 128.0 * c
    cp = 1450.0 + 2736.0 * c / (c + 1.0)
    k = 0.21 + 0.38 * c / (c + 1.0)
    d = 2.4e-3 * np.exp(-0.45 / c) * np.exp(-3850.0 / tk)
    return rho, cp, k, d


def build_nodes(refine=1):
    """保留0.1 cm输出节点，并在外表面附近加密。"""
    base = np.arange(21, dtype=float) * 0.001
    subdivisions = [1] * 20
    subdivisions[15] = 4 * refine
    subdivisions[16] = 6 * refine
    subdivisions[17] = 10 * refine
    subdivisions[18] = 20 * refine
    subdivisions[19] = 40 * refine
    nodes = [0.0]
    output_indices = [0]
    for j, count in enumerate(subdivisions):
        for s in range(1, count + 1):
            nodes.append(base[j] + (base[j + 1] - base[j]) * s / count)
        output_indices.append(len(nodes) - 1)
    return np.asarray(nodes), np.asarray(output_indices)


def geometry(nodes):
    n = nodes.size
    faces = np.empty(n + 1)
    faces[0] = 0.0
    faces[1:n] = 0.5 * (nodes[:-1] + nodes[1:])
    faces[n] = nodes[-1]
    volumes = 0.5 * (faces[1:] ** 2 - faces[:-1] ** 2)
    return faces, volumes


def harmonic(a, b):
    return 2.0 * a * b / np.maximum(a + b, np.finfo(float).tiny)


def assemble_rate(nodes, diffusivity, storage, boundary_transfer):
    """组装 storage*dphi/dt=div(diffusivity*grad(phi)) 的速率算子。"""
    n = nodes.size
    faces, volumes = geometry(nodes)
    dist = np.diff(nodes)
    interface = harmonic(diffusivity[:-1], diffusivity[1:])
    conductance = interface * faces[1:n] / dist
    mass = storage * volumes

    sub = np.zeros(n)
    dia = np.zeros(n)
    sup = np.zeros(n)
    source = np.zeros(n)
    right = conductance / mass[:-1]
    left = conductance / mass[1:]
    sup[:-1] = right
    sub[1:] = left
    dia[:-1] -= right
    dia[1:] -= left

    surface_rate = boundary_transfer * nodes[-1] / mass[-1]
    dia[-1] -= surface_rate
    source[-1] = surface_rate
    return sub, dia, sup, source


def apply_tridiagonal(tri, x):
    sub, dia, sup = tri
    y = dia * x
    y[:-1] += sup[:-1] * x[1:]
    y[1:] += sub[1:] * x[:-1]
    return y


def implicit_theta(old, tri, source, ambient_new, ambient_old, dt, theta):
    sub, dia, sup = tri
    ab = np.zeros((3, old.size))
    ab[0, 1:] = -theta * dt * sup[:-1]
    ab[1, :] = 1.0 - theta * dt * dia
    ab[2, :-1] = -theta * dt * sub[1:]
    rhs = old + (1.0 - theta) * dt * apply_tridiagonal(tri, old)
    rhs += dt * source * (theta * ambient_new + (1.0 - theta) * ambient_old)
    return solve_banded((1, 1), ab, rhs)


def run(refine=1, dt=0.5, relaxation=0.7, tolerance=1.0e-10):
    nodes, output_indices = build_nodes(refine)
    n = nodes.size
    times = np.arange(0.0, T_END + 0.5 * dt, dt)
    save_every = int(round(1.0 / dt))
    if abs(save_every * dt - 1.0) > 1.0e-12:
        raise ValueError("dt必须整除1 s，以便生成题目要求的逐秒输出")

    t_ambient = env_temperature(times)
    t_ambient[times > T_SWITCH] = T_PLATEAU_C
    c_ambient = env_moisture(times)
    t_ambient[0] = T0_C
    c_ambient[0] = 0.01963

    output_t = np.arange(0, int(T_END) + 1, dtype=float)
    t_output = np.empty((output_t.size, 21))
    c_output = np.empty((output_t.size, 21))
    temperature = np.full(n, T0_C)
    moisture = np.full(n, C0)
    t_output[0] = temperature[output_indices]
    c_output[0] = moisture[output_indices]
    max_iterations = 0

    for step in range(1, times.size):
        t_new = times[step]
        # 起始两步和环境边界切换后的两个时间步用后向Euler抑制阶跃振荡。
        near_switch = T_SWITCH < t_new <= T_SWITCH + 2.0 * dt
        theta = 1.0 if step <= 2 or near_switch else 0.5

        t_guess = temperature.copy()
        c_guess = moisture.copy()
        for iteration in range(1, 81):
            rho, cp, k, d = props_appendix3(c_guess, t_guess)

            tri_t_full = assemble_rate(nodes, k, rho * cp, H_T)
            t_new_field = implicit_theta(
                temperature, tri_t_full[:3], tri_t_full[3],
                t_ambient[step], t_ambient[step - 1], dt, theta,
            )

            # D同时依赖新温度和当前水分猜测。
            _, _, _, d = props_appendix3(c_guess, t_new_field)
            tri_c_full = assemble_rate(nodes, d, np.ones(n), H_M)
            c_new_field = implicit_theta(
                moisture, tri_c_full[:3], tri_c_full[3],
                c_ambient[step], c_ambient[step - 1], dt, theta,
            )
            c_new_field = np.maximum(c_new_field, 0.0)

            error = max(
                np.max(np.abs(t_new_field - t_guess)) / (1.0 + np.max(np.abs(t_new_field))),
                np.max(np.abs(c_new_field - c_guess)) / (1.0 + np.max(np.abs(c_new_field))),
            )
            t_guess = relaxation * t_new_field + (1.0 - relaxation) * t_guess
            c_guess = relaxation * c_new_field + (1.0 - relaxation) * c_guess
            if error < tolerance:
                break
        else:
            raise RuntimeError(f"t={t_new}: Picard迭代未收敛")

        max_iterations = max(max_iterations, iteration)
        temperature = t_guess
        moisture = c_guess
        if step % save_every == 0:
            oi = step // save_every
            t_output[oi] = temperature[output_indices]
            c_output[oi] = moisture[output_indices]

    return output_t, t_output, c_output, max_iterations


def validate(times, temperature, moisture):
    transition = int(T_SWITCH)
    checks = {
        "finite": bool(np.isfinite(temperature).all() and np.isfinite(moisture).all()),
        "temperature_bounds": bool(temperature.min() >= T0_C - 1e-8 and temperature.max() <= T_PLATEAU_C + 1e-6),
        "moisture_nonnegative": bool(moisture.min() >= -1e-10),
        "transition_temperature_jump": float(np.max(np.abs(temperature[transition] - temperature[transition - 1]))),
        "transition_moisture_jump": float(np.max(np.abs(moisture[transition] - moisture[transition - 1]))),
        "final_temperature_radial_monotone": bool(np.all(np.diff(temperature[-1]) >= -1e-8)),
        "final_moisture_radial_monotone": bool(np.all(np.diff(moisture[-1]) <= 1e-8)),
    }
    return checks


if __name__ == "__main__":
    refine = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    dt = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    output = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("../../outputs/q2/q2_continuous.npz")
    output.parent.mkdir(parents=True, exist_ok=True)
    times, temperature, moisture, max_iterations = run(refine=refine, dt=dt)
    checks = validate(times, temperature, moisture)
    np.savez(output, t=times, T=temperature, C=moisture, max_iterations=max_iterations)
    print("max_iterations", max_iterations)
    for key, value in checks.items():
        print(key, value)
    for sec in (1800, 3600, 5400, 7199, 7200, 7201, 9000, 10800):
        print(sec, temperature[sec, [0, 5, 10, 15, 20]], moisture[sec, [0, 5, 10, 15, 20]])
