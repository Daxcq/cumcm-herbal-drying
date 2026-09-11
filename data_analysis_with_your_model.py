# -*- coding: utf-8 -*-
"""
药材烘干数据分析（使用你们的拟合方程）
====================================================
对比你们的指数拟合模型与其他候选模型
"""

import matplotlib
matplotlib.use('Agg')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
import openpyxl
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")


# 你们的拟合方程
def your_model(t, a, b, c):
    """你们的模型: w = a + b*e^(c*t)"""
    return a + b * np.exp(c * t)


# 其他候选模型
def logistic_model(t, a, b, c):
    """Logistic: a/(1+b*e^(-c*t))"""
    return a / (1 + b * np.exp(-c * t))


def neg_exp_model(t, a, b, c):
    """负指数: a - b*e^(-c*t)"""
    return a - b * np.exp(-c * t)


def poly3_model(t, a, b, c, d):
    """三次多项式"""
    return a + b*t + c*t**2 + d*t**3


def double_exp_model(t, a, b1, c1, b2, c2):
    """双指数"""
    return a + b1 * np.exp(c1 * t) + b2 * np.exp(c2 * t)


def load_data(use_preheat_only=True):
    """加载附件1数据

    Args:
        use_preheat_only: 如果为True，只使用前130个数据点（预热阶段）
    """
    wb = openpyxl.load_workbook("D:/mcm-kitpip-cache/A题/附件/附件1.xlsx", data_only=True)
    ws = wb.active
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]

    t = np.array([r[0] for r in rows], float)
    T = np.array([r[1] for r in rows], float)
    C = np.array([r[2] for r in rows], float)

    # 只使用预热阶段数据（前130个点）
    if use_preheat_only:
        t = t[:130]
        T = T[:130]
        C = C[:130]

    return t, T, C


def calculate_metrics(y_true, y_pred):
    """计算评估指标"""
    residuals = y_true - y_pred
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)

    r2 = 1 - (ss_res / ss_tot)
    rmse = np.sqrt(np.mean(residuals**2))
    mae = np.mean(np.abs(residuals))
    mape = np.mean(np.abs(residuals / y_true)) * 100 if np.all(y_true != 0) else np.inf

    n = len(y_true)
    k = 3  # 假设3个参数
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k - 1)
    aic = n * np.log(ss_res / n) + 2 * k
    bic = n * np.log(ss_res / n) + k * np.log(n)

    return {
        'R²': r2,
        'Adj_R²': adj_r2,
        'RMSE': rmse,
        'MAE': mae,
        'MAPE': mape,
        'AIC': aic,
        'BIC': bic,
        'residuals': residuals
    }


def main():
    print("="*70)
    print("使用你们的拟合方程进行对比分析")
    print("="*70)

    # 加载数据
    t, T, C = load_data()
    print(f"\n✓ 数据加载完成: {len(t)} 个数据点")

    import os
    output_dir = "outputs/data_analysis_comparison"
    os.makedirs(output_dir, exist_ok=True)

    # ========== 水分含量拟合对比 ==========
    print("\n" + "="*70)
    print("水分含量拟合对比")
    print("="*70)

    # 你们的模型（使用你们的参数）
    a_your = 0.01332  # 用户确认的值
    b_your = 9.421e-4  # 0.0009421
    c_your = 0.07311   # 正数，不是负数

    C_pred_your = your_model(t, a_your, b_your, c_your)
    metrics_your = calculate_metrics(C, C_pred_your)

    print(f"\n【你们的模型】 w = {a_your} + {b_your}*e^({c_your}*t)")
    print(f"  R² = {metrics_your['R²']:.8f}")
    print(f"  RMSE = {metrics_your['RMSE']:.6f}")
    print(f"  MAE = {metrics_your['MAE']:.6f}")
    print(f"  MAPE = {metrics_your['MAPE']:.2f}%")

    # 测试其他模型
    models_C = {}

    # 标准指数（重新拟合优化参数）
    try:
        popt, _ = curve_fit(your_model, t, C, p0=[C[-1], C[0]-C[-1], -0.001], maxfev=50000)
        C_pred = your_model(t, *popt)
        metrics_C['标准指数（优化参数）'] = calculate_metrics(C, C_pred)
        metrics_C['标准指数（优化参数）']['params'] = popt
    except:
        pass

    # Logistic模型
    try:
        popt, _ = curve_fit(logistic_model, t, C, p0=[0.05, 1.5, 0.0006], maxfev=50000)
        C_pred = logistic_model(t, *popt)
        metrics_C['Logistic模型'] = calculate_metrics(C, C_pred)
        metrics_C['Logistic模型']['params'] = popt
        metrics_C['Logistic模型']['y_pred'] = C_pred
    except:
        pass

    # 负指数
    try:
        popt, _ = curve_fit(neg_exp_model, t, C, p0=[0.05, 0.03, 0.0004], maxfev=50000)
        C_pred = neg_exp_model(t, *popt)
        metrics_C['负指数模型'] = calculate_metrics(C, C_pred)
        metrics_C['负指数模型']['params'] = popt
        metrics_C['负指数模型']['y_pred'] = C_pred
    except:
        pass

    # 三次多项式
    try:
        popt, _ = curve_fit(poly3_model, t, C, maxfev=50000)
        C_pred = poly3_model(t, *popt)
        metrics_C['三次多项式'] = calculate_metrics(C, C_pred)
        metrics_C['三次多项式']['params'] = popt
        metrics_C['三次多项式']['y_pred'] = C_pred
    except:
        pass

    # 双指数
    try:
        popt, _ = curve_fit(double_exp_model, t, C,
                           p0=[C[0], (C[-1]-C[0])/2, 0.001, (C[-1]-C[0])/2, -0.001],
                           maxfev=50000)
        C_pred = double_exp_model(t, *popt)
        metrics_C['双指数模型'] = calculate_metrics(C, C_pred)
        metrics_C['双指数模型']['params'] = popt
        metrics_C['双指数模型']['y_pred'] = C_pred
    except:
        pass

    # 打印对比表
    print("\n模型对比:")
    print("-"*70)
    comparison_data = []

    # 添加你们的模型
    comparison_data.append({
        '模型': '你们的指数模型 ⭐',
        'R²': metrics_your['R²'],
        'RMSE': metrics_your['RMSE'],
        'MAE': metrics_your['MAE'],
        'MAPE': metrics_your['MAPE']
    })

    # 添加其他模型
    for name, metrics in metrics_C.items():
        comparison_data.append({
            '模型': name,
            'R²': metrics['R²'],
            'RMSE': metrics['RMSE'],
            'MAE': metrics['MAE'],
            'MAPE': metrics['MAPE']
        })

    df_comp = pd.DataFrame(comparison_data)
    df_comp = df_comp.sort_values('R²', ascending=False)
    print(df_comp.to_string(index=False))

    # 保存对比表
    df_comp.to_excel(f"{output_dir}/水分拟合对比_含你们模型.xlsx", index=False)

    # ========== 绘制对比图 ==========
    print("\n正在生成图表...")

    # 准备所有模型的数据
    all_models = {
        '你们的模型': {
            'y_pred': C_pred_your,
            'residuals': metrics_your['residuals'],
            'R²': metrics_your['R²'],
            'RMSE': metrics_your['RMSE']
        }
    }

    for name, metrics in metrics_C.items():
        if 'y_pred' in metrics:
            all_models[name] = {
                'y_pred': metrics['y_pred'],
                'residuals': metrics['residuals'],
                'R²': metrics['R²'],
                'RMSE': metrics['RMSE']
            }

    # 绘制对比图（2行N列）
    n_models = len(all_models)
    fig, axes = plt.subplots(2, n_models, figsize=(5*n_models, 10))
    if n_models == 1:
        axes = axes.reshape(-1, 1)

    for idx, (model_name, model_data) in enumerate(all_models.items()):
        # 拟合曲线
        axes[0, idx].scatter(t, C, alpha=0.5, s=20, label='实测数据', color='blue')
        axes[0, idx].plot(t, model_data['y_pred'], 'r-', linewidth=2, label='拟合曲线')

        # 特别标注你们的模型
        if '你们' in model_name:
            axes[0, idx].set_title(f'{model_name} ⭐\nR²={model_data["R²"]:.6f}',
                                   fontsize=12, fontweight='bold', color='red')
        else:
            axes[0, idx].set_title(f'{model_name}\nR²={model_data["R²"]:.6f}',
                                   fontsize=11, fontweight='bold')

        axes[0, idx].set_xlabel('时间 (s)', fontsize=10)
        axes[0, idx].set_ylabel('水分含量 (kg/kg)', fontsize=10)
        axes[0, idx].legend(fontsize=9)
        axes[0, idx].grid(alpha=0.3)

        # 残差图
        axes[1, idx].scatter(t, model_data['residuals'], alpha=0.5, s=20, color='purple')
        axes[1, idx].axhline(y=0, color='r', linestyle='--', linewidth=2)
        axes[1, idx].set_title(f'残差图\nRMSE={model_data["RMSE"]:.6f}',
                              fontsize=11, fontweight='bold')
        axes[1, idx].set_xlabel('时间 (s)', fontsize=10)
        axes[1, idx].set_ylabel('残差', fontsize=10)
        axes[1, idx].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/水分拟合对比图_含你们模型.png", dpi=300, bbox_inches='tight')
    print(f"✓ 已保存: {output_dir}/水分拟合对比图_含你们模型.png")
    plt.close()

    # ========== 详细的残差分析 ==========
    print("\n" + "="*70)
    print("你们模型的残差分析")
    print("="*70)

    residuals = metrics_your['residuals']
    print(f"残差均值: {np.mean(residuals):.6e} (应接近0)")
    print(f"残差标准差: {np.std(residuals):.6f}")
    print(f"残差最大值: {np.max(residuals):.6f}")
    print(f"残差最小值: {np.min(residuals):.6f}")

    # 正态性检验
    if len(residuals) >= 3:
        stat, p_value = stats.shapiro(residuals)
        result = "服从正态分布" if p_value > 0.05 else "不服从正态分布"
        print(f"Shapiro-Wilk检验: W={stat:.4f}, p={p_value:.6f} → 残差{result}")

    # Durbin-Watson检验
    dw = np.sum(np.diff(residuals)**2) / np.sum(residuals**2)
    print(f"Durbin-Watson统计量: {dw:.4f} (接近2表示无自相关)")

    # 绘制残差分析图
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 残差vs拟合值
    axes[0, 0].scatter(C_pred_your, residuals, alpha=0.5)
    axes[0, 0].axhline(y=0, color='r', linestyle='--', linewidth=2)
    axes[0, 0].set_xlabel('拟合值', fontsize=11)
    axes[0, 0].set_ylabel('残差', fontsize=11)
    axes[0, 0].set_title('残差 vs 拟合值', fontsize=12, fontweight='bold')
    axes[0, 0].grid(alpha=0.3)

    # 残差直方图
    axes[0, 1].hist(residuals, bins=30, density=True, alpha=0.6, color='skyblue', edgecolor='black')
    mu, sigma = np.mean(residuals), np.std(residuals)
    x = np.linspace(residuals.min(), residuals.max(), 100)
    axes[0, 1].plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, label='正态分布')
    axes[0, 1].set_xlabel('残差', fontsize=11)
    axes[0, 1].set_ylabel('频率密度', fontsize=11)
    axes[0, 1].set_title('残差分布', fontsize=12, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    # Q-Q图
    stats.probplot(residuals, dist="norm", plot=axes[1, 0])
    axes[1, 0].set_title('残差Q-Q图（正态性检验）', fontsize=12, fontweight='bold')
    axes[1, 0].grid(alpha=0.3)

    # 残差vs时间
    axes[1, 1].scatter(t, residuals, alpha=0.5)
    axes[1, 1].axhline(y=0, color='r', linestyle='--', linewidth=2)
    axes[1, 1].set_xlabel('时间 (s)', fontsize=11)
    axes[1, 1].set_ylabel('残差', fontsize=11)
    axes[1, 1].set_title('残差 vs 时间（检查时间依赖性）', fontsize=12, fontweight='bold')
    axes[1, 1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/你们模型的残差分析图.png", dpi=300, bbox_inches='tight')
    print(f"✓ 已保存: {output_dir}/你们模型的残差分析图.png")
    plt.close()

    # ========== 绘制单独的对比图（你们的 vs 最优的） ==========
    if 'Logistic模型' in metrics_C:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # 你们的模型
        axes[0].scatter(t, C, alpha=0.5, s=30, label='实测数据', color='blue')
        axes[0].plot(t, C_pred_your, 'r-', linewidth=2.5, label='你们的拟合')
        axes[0].set_title(f'你们的指数模型 ⭐\nR²={metrics_your["R²"]:.6f}, RMSE={metrics_your["RMSE"]:.6f}',
                         fontsize=13, fontweight='bold', color='red')
        axes[0].set_xlabel('时间 (s)', fontsize=12)
        axes[0].set_ylabel('水分含量 (kg/kg)', fontsize=12)
        axes[0].legend(fontsize=11)
        axes[0].grid(alpha=0.3)

        # Logistic模型
        axes[1].scatter(t, C, alpha=0.5, s=30, label='实测数据', color='blue')
        axes[1].plot(t, metrics_C['Logistic模型']['y_pred'], 'g-', linewidth=2.5, label='Logistic拟合')
        axes[1].set_title(f'Logistic模型（对比）\nR²={metrics_C["Logistic模型"]["R²"]:.6f}, RMSE={metrics_C["Logistic模型"]["RMSE"]:.6f}',
                         fontsize=13, fontweight='bold', color='green')
        axes[1].set_xlabel('时间 (s)', fontsize=12)
        axes[1].set_ylabel('水分含量 (kg/kg)', fontsize=12)
        axes[1].legend(fontsize=11)
        axes[1].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/你们的模型_vs_Logistic对比.png", dpi=300, bbox_inches='tight')
        print(f"✓ 已保存: {output_dir}/你们的模型_vs_Logistic对比.png")
        plt.close()

    print("\n" + "="*70)
    print(f"✓ 所有分析完成！结果已保存到: {output_dir}")
    print("="*70)


if __name__ == "__main__":
    main()
