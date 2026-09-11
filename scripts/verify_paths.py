#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路径验证脚本
检查所有数据文件路径是否正确
"""

import os
import sys

def check_path(file_path, description):
    """检查路径是否存在"""
    exists = os.path.exists(file_path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {file_path}")
    return exists

def main():
    print("="*70)
    print("路径验证检查")
    print("="*70)

    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    print(f"\n项目根目录: {project_root}\n")

    all_ok = True

    # 检查数据文件
    print("📁 数据文件检查:")
    all_ok &= check_path(
        os.path.join(project_root, "data/raw/附件1.xlsx"),
        "附件1.xlsx"
    )
    all_ok &= check_path(
        os.path.join(project_root, "data/raw/附件2.xlsx"),
        "附件2.xlsx"
    )

    # 检查源代码
    print("\n📁 源代码文件检查:")
    all_ok &= check_path(
        os.path.join(project_root, "src/q1_preheat/solver_q1.py"),
        "solver_q1.py"
    )
    all_ok &= check_path(
        os.path.join(project_root, "src/analysis/moisture_temperature.py"),
        "moisture_temperature.py"
    )
    all_ok &= check_path(
        os.path.join(project_root, "src/analysis/time_series_analysis.py"),
        "time_series_analysis.py"
    )
    all_ok &= check_path(
        os.path.join(project_root, "src/analysis/statistical_analysis.py"),
        "statistical_analysis.py"
    )

    # 检查输出目录
    print("\n📁 输出目录检查:")
    output_dirs = [
        "outputs/q1",
        "outputs/analysis",
        "outputs/analysis/moisture_vs_temperature"
    ]
    for dir_path in output_dirs:
        full_path = os.path.join(project_root, dir_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            print(f"✓ 创建目录: {dir_path}")
        else:
            print(f"✓ 目录存在: {dir_path}")

    # 测试相对路径（从不同模块位置）
    print("\n📁 相对路径测试:")

    # 从 src/q1_preheat/ 访问数据
    os.chdir(os.path.join(project_root, "src/q1_preheat"))
    data_path = "../../data/raw/附件1.xlsx"
    all_ok &= check_path(data_path, "从 src/q1_preheat/ 访问附件1")

    # 从 src/analysis/ 访问数据
    os.chdir(os.path.join(project_root, "src/analysis"))
    data_path = "../../data/raw/附件1.xlsx"
    all_ok &= check_path(data_path, "从 src/analysis/ 访问附件1")

    # 恢复工作目录
    os.chdir(project_root)

    print("\n" + "="*70)
    if all_ok:
        print("✅ 所有路径检查通过！")
        return 0
    else:
        print("❌ 部分路径检查失败，请检查文件是否存在")
        return 1

if __name__ == "__main__":
    sys.exit(main())
