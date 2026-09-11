# 项目重构方案

## 目标结构

```
cumcm-herbal-drying/
│
├── README.md                          # 项目总说明
├── requirements.txt                   # Python依赖
├── .gitignore                        # Git忽略规则
│
├── data/                             # 数据目录
│   ├── raw/                          # 原始数据
│   │   └── 附件1.xlsx
│   │   └── 附件2.xlsx
│   └── processed/                    # 处理后的数据
│
├── src/                              # 源代码
│   ├── q1_preheat/                   # 问题1：预热阶段
│   │   ├── __init__.py
│   │   ├── solver_q1.py              # PDE数值求解器
│   │   ├── data_fitting.py           # 数据拟合分析
│   │   └── visualization.py          # 可视化
│   │
│   ├── analysis/                     # 数据分析模块
│   │   ├── __init__.py
│   │   ├── moisture_temperature.py   # 水分-温度分析
│   │   └── statistical_analysis.py   # 统计分析
│   │
│   └── utils/                        # 工具函数
│       ├── __init__.py
│       ├── data_loader.py            # 数据加载
│       └── plotting.py               # 绘图工具
│
├── outputs/                          # 输出结果
│   ├── q1/                           # 问题1结果
│   │   ├── figures/                  # 图表
│   │   ├── tables/                   # 表格
│   │   └── results/                  # 数值结果
│   └── analysis/                     # 分析结果
│       ├── moisture_vs_temperature/
│       └── statistical_reports/
│
├── docs/                             # 文档
│   ├── model/                        # 模型文档
│   │   ├── 问题1模型推导.md
│   │   └── PDE数值方法说明.md
│   │
│   ├── changelog/                    # 变更记录
│   │   ├── 代码修改总结.md
│   │   └── 问题修复说明.md
│   │
│   ├── setup/                        # 配置说明
│   │   ├── GITHUB_SETUP.md
│   │   └── 环境配置说明.md
│   │
│   └── reports/                      # 分析报告
│       └── 预热阶段拟合分析报告.md
│
├── scripts/                          # 脚本
│   ├── run_q1.sh                     # 运行问题1
│   ├── build_q1.mjs                  # 构建脚本
│   └── check_results.py              # 结果检查
│
├── tests/                            # 测试
│   ├── test_solver.py
│   └── test_fitting.py
│
└── archive/                          # 归档（旧版本）
    └── old_versions/
```

## 文件分类与映射

### 核心代码 → src/
| 当前文件 | 新位置 | 说明 |
|---------|--------|------|
| solver_q1.py | src/q1_preheat/solver_q1.py | PDE求解器 |
| analyze_moisture_vs_temperature.py | src/analysis/moisture_temperature.py | 水分-温度拟合 |
| data_analysis_with_your_model.py | src/analysis/time_series_analysis.py | 时间序列分析 |
| data_analysis.py | src/analysis/statistical_analysis.py | 统计分析 |

### 数据 → data/
| 当前文件 | 新位置 |
|---------|--------|
| A题/附件/*.xlsx | data/raw/ |
| outputs/* | outputs/ (重组) |

### 文档 → docs/
| 当前文件 | 新位置 |
|---------|--------|
| README.md | README.md (保留根目录) |
| docs/代码修改总结.md | docs/changelog/代码修改总结.md |
| docs/问题修复说明.md | docs/changelog/问题修复说明.md |
| 药材烘干_问题1模型推导.md | docs/model/问题1模型推导.md |
| 药材烘干_问题1模型推导.html | docs/model/问题1模型推导.html |
| GITHUB_SETUP.md | docs/setup/GITHUB_SETUP.md |
| PUSH_ERROR_SOLUTION.md | docs/setup/PUSH_ERROR_SOLUTION.md |

### 脚本 → scripts/
| 当前文件 | 新位置 |
|---------|--------|
| build_q1.mjs | scripts/build_q1.mjs |
| check_q1_results.py | scripts/check_results.py |

### 需要清理的目录
- `.mimosa/` → 添加到 .gitignore
- `__pycache__/` → 添加到 .gitignore
- `node_modules/` → 添加到 .gitignore
- `http-v2/` → 添加到 .gitignore (pip缓存)
- `selfcheck/` → 添加到 .gitignore

## 新增文件

### 1. requirements.txt
```txt
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
openpyxl>=3.0.0
```

### 2. .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Environments
.env
venv/
env/

# IDE
.vscode/
.idea/
*.swp

# Project specific
.mimosa/
http-v2/
selfcheck/
node_modules/
outputs/*.png
outputs/*.xlsx

# OS
.DS_Store
Thumbs.db
```

### 3. src/__init__.py, src/q1_preheat/__init__.py 等
空文件，标记为Python包

## 迁移步骤

1. 创建新目录结构
2. 移动文件到新位置
3. 更新import路径
4. 更新README.md
5. 测试所有脚本
6. 提交到Git

## 优势

✅ **模块化**：按功能分类，清晰明确
✅ **可扩展**：便于添加问题2、问题3等
✅ **标准化**：符合Python项目规范
✅ **易维护**：文档、代码、数据分离
✅ **可复用**：工具函数独立
