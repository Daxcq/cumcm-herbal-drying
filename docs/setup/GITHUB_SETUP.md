# GitHub 仓库同步步骤

## 方法一：通过GitHub网站创建（推荐）

### 1. 在GitHub上创建新仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **仓库名称**: `mcm-herbal-drying` 或 `药材烘干建模`
   - **描述**: 药材烘干过程的数学建模与数值模拟 (Mathematical modeling and numerical simulation of herbal drying process)
   - **可见性**: 选择 Public（公开）或 Private（私有）
   - ⚠️ **不要**勾选 "Add a README file"（我们已经有了）
   - ⚠️ **不要**选择 .gitignore 或 license（我们已经有了）
3. 点击 "Create repository"

### 2. 连接本地仓库到GitHub

创建仓库后，GitHub会显示一个页面，选择 "…or push an existing repository from the command line" 部分的命令。

**或者直接运行以下命令**（把 YOUR_USERNAME 替换成你的GitHub用户名）：

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/mcm-herbal-drying.git

# 推送到GitHub
git push -u origin master
```

### 3. 后续更新

以后每次修改后，使用以下命令同步：

```bash
# 查看修改
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "更新说明"

# 推送到GitHub
git push
```

---

## 方法二：使用SSH密钥（更安全，推荐长期使用）

### 1. 生成SSH密钥（如果还没有）

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

按提示操作，可以直接按回车使用默认设置。

### 2. 添加SSH密钥到GitHub

```bash
# 复制公钥内容
cat ~/.ssh/id_ed25519.pub
```

然后：
1. 访问 https://github.com/settings/keys
2. 点击 "New SSH key"
3. 粘贴公钥内容
4. 点击 "Add SSH key"

### 3. 使用SSH URL连接

```bash
# 添加远程仓库（SSH方式）
git remote add origin git@github.com:YOUR_USERNAME/mcm-herbal-drying.git

# 推送
git push -u origin master
```

---

## 当前仓库状态

✅ 已初始化 Git 仓库
✅ 已创建初始提交
✅ 已配置 .gitignore
✅ 已添加 README.md

**提交信息**：
- Commit: d84e4b9
- 包含文件: 8个
- 代码行数: 1804行

**已包含的主要文件**：
- solver_q1.py（问题1求解器）
- data_analysis.py（数据分析）
- analyze_moisture_vs_temperature.py（拟合分析）
- README.md（项目说明）
- .gitignore（忽略配置）

---

## 常用Git命令速查

```bash
# 查看状态
git status

# 查看提交历史
git log --oneline

# 添加所有修改
git add .

# 提交
git commit -m "提交说明"

# 推送到远程
git push

# 拉取远程更新
git pull

# 查看远程仓库
git remote -v

# 创建新分支
git checkout -b 新分支名

# 切换分支
git checkout 分支名
```

---

## 注意事项

⚠️ **大文件警告**：
- `outputs/` 文件夹已在 .gitignore 中排除
- `.npz` 数据文件已排除
- Excel临时文件已排除

⚠️ **敏感信息**：
- 确保不要提交包含个人信息的文件
- 不要提交密码、API密钥等

✅ **推荐做法**：
- 每次完成一个功能模块就提交一次
- 提交信息使用中文，清晰描述改动内容
- 定期推送到GitHub备份

---

## 遇到问题？

### 问题1：推送时要求输入用户名密码

**解决**：GitHub已不支持密码验证，需要使用：
- 个人访问令牌 (Personal Access Token)
- SSH密钥（推荐）

创建个人访问令牌：https://github.com/settings/tokens

### 问题2：push被拒绝

```bash
# 先拉取远程更新
git pull origin master --rebase

# 再推送
git push
```

### 问题3：合并冲突

```bash
# 查看冲突文件
git status

# 手动解决冲突后
git add 冲突文件
git commit -m "解决冲突"
git push
```

---

**下一步**：请按照"方法一"的步骤在GitHub上创建仓库，然后运行连接命令！
