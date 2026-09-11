# 中药材烘干问题 - 项目结构树

```
cumcm-herbal-drying/
│
├── 📄 README.md                          项目总说明
├── 📄 README_NEW.md                      更新后的README
├── 📄 requirements.txt                   Python依赖列表
├── 📄 .gitignore                        Git忽略配置
├── 📄 PROJECT_RESTRUCTURE.md            重构方案文档
│
├── 📁 data/                             数据目录
│   ├── 📁 raw/                          原始数据
│   │   ├── 附件1.xlsx                   实验数据（温度、水分）
│   │   └── 附件2.xlsx                   补充数据
│   └── 📁 processed/                    处理后的数据
│
├── 📁 src/                              源代码
│   ├── 📄 __init__.py
│   │
│   ├── 📁 q1_preheat/                   问题1：预热阶段
│   │   ├── 📄 __init__.py
│   │   └── 🐍 solver_q1.py             PDE数值求解器
│   │                                    - 有限体积法
│   │                                    - Crank-Nicolson
│   │                                    - Picard迭代
│   │
│   ├── 📁 analysis/                     数据分析模块
│   │   ├── 📄 __init__.py
│   │   ├── 🐍 moisture_temperature.py  水分-温度拟合
│   │   │                                R²=0.99798
│   │   ├── 🐍 time_series_analysis.py  时间序列分析
│   │   └── 🐍 statistical_analysis.py  统计分析
│   │
│   └── 📁 utils/                        工具函数
│       ├── 📄 __init__.py
│       ├── 🐍 data_loader.py           数据加载（待开发）
│       └── 🐍 plotting.py              绘图工具（待开发）
│
├── 📁 outputs/                          输出结果
│   ├── 📁 q1/                           问题1数值结果
│   │   ├── result1_k1.xlsx
│   │   ├── q1_k1.npz
│   │   └── ...
│   │
│   └── 📁 analysis/                     分析结果
│       └── 📁 moisture_vs_temperature/
│           ├── 拟合模型对比表.xlsx
│           ├── 水分vs温度_拟合对比图.png
│           ├── 你们模型的残差分析.png
│           └── 分析总结.txt
│
├── 📁 docs/                             文档目录
│   ├── 📁 model/                        模型文档
│   │   ├── 问题1模型推导.md
│   │   ├── 问题1模型推导.html
│   │   └── 问题1_v2修订.md
│   │
│   ├── 📁 changelog/                    变更记录
│   │   ├── 代码修改总结.md              预热阶段修改
│   │   ├── 问题修复说明.md              bug修复记录
│   │   └── 项目重构完成总结.md          本次重构
│   │
│   ├── 📁 setup/                        配置说明
│   │   ├── GITHUB_SETUP.md
│   │   └── PUSH_ERROR_SOLUTION.md
│   │
│   └── 📁 reports/                      分析报告（预留）
│
├── 📁 scripts/                          脚本
│   ├── 🔧 build_q1.mjs                 构建脚本
│   └── 🐍 check_results.py            结果检查
│
├── 📁 tests/                            测试（预留）
│   ├── test_solver.py
│   └── test_fitting.py
│
└── 📁 archive/                          归档（预留）
    └── old_versions/

```

## 图例说明

- 📄 普通文件
- 🐍 Python源代码
- 🔧 脚本文件
- 📁 目录

## 核心模块

### 1️⃣ 数值模拟
**位置**: `src/q1_preheat/solver_q1.py`  
**功能**: PDE求解，输出温度场和水分场

### 2️⃣ 数据拟合
**位置**: `src/analysis/moisture_temperature.py`  
**功能**: 预热阶段水分-温度拟合分析

### 3️⃣ 数据存储
**位置**: `data/raw/`  
**内容**: 附件1.xlsx（实验数据）

### 4️⃣ 结果输出
**位置**: `outputs/`  
**内容**: Excel表格、图表、数值结果

## 快速导航

| 想要... | 查看文件 |
|---------|---------|
| 运行PDE求解 | `src/q1_preheat/solver_q1.py` |
| 数据拟合分析 | `src/analysis/moisture_temperature.py` |
| 了解模型原理 | `docs/model/问题1模型推导.md` |
| 查看修改历史 | `docs/changelog/` |
| 安装依赖 | `requirements.txt` |
| 查看结果 | `outputs/` |
