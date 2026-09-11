# 中药材烘干问题 - 数学建模项目

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 项目简介

本项目针对中药材烘干过程建立数学模型，通过偏微分方程(PDE)数值求解和数据拟合分析，研究药材内部温度场和水分场的时空演化规律。

**核心问题**：预热阶段的温度-水分耦合模型

## 项目结构

```
cumcm-herbal-drying/
│
├── README.md                          # 项目说明
├── requirements.txt                   # Python依赖
├── .gitignore                        # Git忽略规则
├── PROJECT_RESTRUCTURE.md            # 重构说明文档
│
├── data/                             # 数据目录
│   ├── raw/                          # 原始数据
│   │   ├── 附件1.xlsx                # 实验数据（温度、水分）
│   │   └── 附件2.xlsx                # 补充数据
│   └── processed/                    # 处理后的数据
│
├── src/                              # 源代码
│   ├── q1_preheat/                   # 问题1：预热阶段分析
│   │   └── solver_q1.py              # PDE数值求解器（有限体积法）
│   │
│   ├── analysis/                     # 数据分析模块
│   │   ├── moisture_temperature.py   # 水分-温度拟合分析
│   │   ├── time_series_analysis.py   # 时间序列分析
│   │   └── statistical_analysis.py   # 统计分析
│   │
│   └── utils/                        # 工具函数
│       ├── data_loader.py            # 数据加载工具
│       └── plotting.py               # 绘图工具
│
├── outputs/                          # 输出结果
│   ├── q1/                           # 问题1数值求解结果
│   └── analysis/                     # 数据分析结果
│       └── moisture_vs_temperature/  # 水分-温度拟合结果
│
├── docs/                             # 文档
│   ├── model/                        # 模型文档
│   │   ├── 问题1模型推导.md
│   │   └── 问题1_v2修订.md
│   │
│   ├── changelog/                    # 变更记录
│   │   ├── 代码修改总结.md
│   │   └── 问题修复说明.md
│   │
│   └── setup/                        # 配置说明
│       ├── GITHUB_SETUP.md
│       └── PUSH_ERROR_SOLUTION.md
│
└── scripts/                          # 脚本
    ├── build_q1.mjs                  # 构建脚本
    └── check_results.py              # 结果检查脚本

```

## 核心功能

### 1. PDE数值求解 (`src/q1_preheat/solver_q1.py`)

**模型方程**：
- 温度场：`dT/dt = α·(1/r)·d/dr(r·dT/dr)`
- 水分场：`dC/dt = (1/r)·d/dr(r·D(C)·dC/dr)`
- 扩散系数：`D(C) = 7×10⁻⁹·exp(-0.89/C)`

**数值方法**：
- 有限体积法（轴对称）
- Crank-Nicolson时间离散
- Picard迭代处理非线性

**运行方式**：
```bash
cd src/q1_preheat
python solver_q1.py 1 0.25
```

### 2. 水分-温度拟合分析 (`src/analysis/moisture_temperature.py`)

**拟合方程**（预热阶段，前130点）：
```
w(T) = 0.0118 + 0.001318 × e^(0.067×T)
```

**数据范围**：
- 时间：t = 0~7740s
- 温度：T = 28.00~49.94°C
- 水分：w = 0.01963~0.04954 kg/kg

**拟合精度**：
- R² = 0.99798
- RMSE = 0.000402 kg/kg
- MAPE = 0.89%
- 比全域参数RMSE降低15.8%

**运行方式**：
```bash
cd src/analysis
python moisture_temperature.py
```

## 安装依赖

```bash
pip install -r requirements.txt
```

**依赖包**：
- numpy >= 1.21.0
- scipy >= 1.7.0
- pandas >= 1.3.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0
- openpyxl >= 3.0.0

## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/Daxcq/cumcm-herbal-drying.git
cd cumcm-herbal-drying
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行数值模拟
```bash
cd src/q1_preheat
python solver_q1.py
```

### 4. 运行数据分析
```bash
cd src/analysis
python moisture_temperature.py
```

## 主要成果

✅ **数学模型**
- 建立温度-水分耦合的PDE模型
- 实现高精度数值求解器（收敛性好）

✅ **数据拟合**
- 预热阶段水分-温度指数拟合（R²>0.997）
- 验证模型的物理合理性（相关系数r=0.985）

✅ **工程化**
- 模块化代码结构
- 完整的文档系统
- 标准化的项目布局

## 关键修改记录

### 2026-09-11：预热阶段数据修正
- ✅ 只使用前130个数据点（预热阶段）
- ✅ 更新拟合参数：a=0.0118, b=0.001318, c=0.067
- ✅ RMSE降低15.8%，R²=0.99798

### 2026-09-11：边界条件改进
- ✅ solver边界条件改用拟合公式 C_fitted(T)
- ✅ 提高边界条件平滑性和物理合理性

详见：[docs/changelog/](docs/changelog/)

## 技术栈

- **语言**：Python 3.8+
- **核心库**：NumPy, SciPy, Pandas, Matplotlib, Seaborn, OpenPyXL
- **数值方法**：有限体积法、Crank-Nicolson、Picard迭代
- **版本控制**：Git, GitHub

## 文档

- [模型推导](docs/model/问题1模型推导.md)
- [代码修改总结](docs/changelog/代码修改总结.md)
- [问题修复说明](docs/changelog/问题修复说明.md)
- [项目重构方案](PROJECT_RESTRUCTURE.md)

## 贡献者

MCM建模团队

## 许可证

MIT License

## 更新日期

2026年9月11日
