# -*- coding: utf-8 -*-
"""
附件1数据可视化 - 时间序列散点图
温度使用开尔文（K）单位
"""

import matplotlib
matplotlib.use('Agg')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150


def load_data():
    """加载附件1数据"""
    # 根据脚本位置获取数据路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, "data/raw/附件1.xlsx")

    wb = openpyxl.load_workbook(data_path, data_only=True)
    ws = wb.active
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]

    t = np.array([r[0] for r in rows], float)  # 时间(s)
    T_celsius = np.array([r[1] for r in rows], float)  # 温度(°C)
    C = np.array([r[2] for r in rows], float)  # 水分浓度(kg/kg)

    # 将摄氏度转换为开尔文
    T_kelvin = T_celsius + 273.15

    return t, T_kelvin, T_celsius, C


def plot_scatter():
    """绘制时间序列散点图"""
    t, T_K, T_C, C = load_data()

    # 创建输出目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, "outputs/analysis/time_series")
    os.makedirs(output_dir, exist_ok=True)

    # 创建图表
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle('附件1 时间序列散点图', fontsize=16, fontweight='bold')

    # 子图1：时间 vs 温度（开尔文）
    ax1.scatter(t, T_K, s=30, alpha=0.6, c='red', edgecolors='darkred', linewidth=0.5)
    ax1.set_xlabel('时间 t (s)', fontsize=12)
    ax1.set_ylabel('温度 T (K)', fontsize=12)
    ax1.set_title(f'温度随时间变化（开尔文温标）\n范围: {T_K.min():.2f} ~ {T_K.max():.2f} K',
                  fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')

    # 添加辅助信息：对应的摄氏度
    ax1_twin = ax1.twinx()
    ax1_twin.set_ylabel('温度 (°C)', fontsize=12, color='blue')
    ax1_twin.set_ylim(T_C.min() - 5, T_C.max() + 5)
    ax1_twin.tick_params(axis='y', labelcolor='blue')

    # 子图2：时间 vs 水分浓度
    ax2.scatter(t, C, s=30, alpha=0.6, c='blue', edgecolors='darkblue', linewidth=0.5)
    ax2.set_xlabel('时间 t (s)', fontsize=12)
    ax2.set_ylabel('水分浓度 w (kg/kg)', fontsize=12)
    ax2.set_title(f'水分浓度随时间变化\n范围: {C.min():.6f} ~ {C.max():.6f} kg/kg',
                  fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()

    # 保存图表
    output_path = os.path.join(output_dir, "附件1_时间序列散点图_开尔文.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 图表已保存: {output_path}")
    plt.close()

    # 创建单独的温度图（更大）
    fig2, ax = plt.subplots(figsize=(14, 6))
    ax.scatter(t, T_K, s=40, alpha=0.6, c='red', edgecolors='darkred', linewidth=0.5)
    ax.set_xlabel('时间 t (s)', fontsize=13)
    ax.set_ylabel('温度 T (K)', fontsize=13)
    ax.set_title(f'温度随时间变化（开尔文温标）\n{T_K.min():.2f} K ~ {T_K.max():.2f} K  |  {T_C.min():.2f}°C ~ {T_C.max():.2f}°C',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')

    # 添加统计信息
    textstr = f'数据点数: {len(t)}\n平均温度: {T_K.mean():.2f} K ({T_C.mean():.2f}°C)\n温度标准差: {T_K.std():.2f} K'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)

    plt.tight_layout()
    output_path2 = os.path.join(output_dir, "附件1_温度散点图_开尔文_单独.png")
    plt.savefig(output_path2, dpi=300, bbox_inches='tight')
    print(f"✓ 图表已保存: {output_path2}")
    plt.close()

    # 创建单独的水分图（更大）
    fig3, ax = plt.subplots(figsize=(14, 6))
    ax.scatter(t, C, s=40, alpha=0.6, c='blue', edgecolors='darkblue', linewidth=0.5)
    ax.set_xlabel('时间 t (s)', fontsize=13)
    ax.set_ylabel('水分浓度 w (kg/kg)', fontsize=13)
    ax.set_title(f'水分浓度随时间变化\n{C.min():.6f} ~ {C.max():.6f} kg/kg',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')

    # 添加统计信息
    textstr = f'数据点数: {len(t)}\n平均水分: {C.mean():.6f} kg/kg\n标准差: {C.std():.6f}'
    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)

    plt.tight_layout()
    output_path3 = os.path.join(output_dir, "附件1_水分散点图_单独.png")
    plt.savefig(output_path3, dpi=300, bbox_inches='tight')
    print(f"✓ 图表已保存: {output_path3}")
    plt.close()

    # 打印统计信息
    print("\n" + "="*70)
    print("数据统计信息")
    print("="*70)
    print(f"数据点数: {len(t)}")
    print(f"\n时间范围: {t.min():.0f} ~ {t.max():.0f} s  ({t.max()/60:.1f} 分钟)")
    print(f"\n温度统计 (开尔文):")
    print(f"  最小值: {T_K.min():.2f} K  ({T_C.min():.2f}°C)")
    print(f"  最大值: {T_K.max():.2f} K  ({T_C.max():.2f}°C)")
    print(f"  平均值: {T_K.mean():.2f} K  ({T_C.mean():.2f}°C)")
    print(f"  标准差: {T_K.std():.2f} K")
    print(f"  温升: {T_K.max() - T_K.min():.2f} K  ({T_C.max() - T_C.min():.2f}°C)")
    print(f"\n水分浓度统计:")
    print(f"  最小值: {C.min():.6f} kg/kg")
    print(f"  最大值: {C.max():.6f} kg/kg")
    print(f"  平均值: {C.mean():.6f} kg/kg")
    print(f"  标准差: {C.std():.6f}")
    print(f"  变化量: {C.max() - C.min():.6f} kg/kg ({(C.max() - C.min())/C.min()*100:.1f}% 增长)")
    print("="*70)


if __name__ == "__main__":
    plot_scatter()
    print("\n✓ 所有图表生成完成！")
