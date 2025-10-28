# Pre-commit Hooks 使用指南

本项目使用 [pre-commit](https://pre-commit.com/) 框架在 git 提交前自动运行代码质量检查，避免将有问题的代码提交到仓库。

## 🎯 自动检查内容

每次 `git commit` 时会自动运行：

1. **代码格式检查**
   - 文件末尾空行
   - 行尾空白字符
   - YAML/JSON 格式验证

2. **Python 代码质量**
   - ✅ Flake8 代码风格检查（最大行长120字符）
   - ✅ isort 导入排序检查

3. **预制件特定检查**
   - ✅ Manifest 验证（`prefab-manifest.json` 与 `src/main.py` 一致性）
   - ✅ 单元测试（所有测试必须通过）
   - ✅ 版本同步检查（manifest 与 pyproject.toml 版本一致）

4. **安全检查**
   - 🚫 阻止直接提交到 main/master 分支
   - 🚫 检查合并冲突标记
   - 🚫 检查大文件（>5MB）

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用 uv 安装所有开发依赖（包括 pre-commit）
uv sync --dev
```

### 2. 安装 Git Hooks

```bash
# 在项目根目录执行
uv run pre-commit install

# 你会看到：
# pre-commit installed at .git/hooks/pre-commit
```

### 3. 开始使用

安装完成后，每次 `git commit` 都会自动运行检查：

```bash
git add .
git commit -m "feat: add new feature"

# 自动运行检查...
# ✅ 所有检查通过 → 提交成功
# ❌ 有检查失败 → 提交被阻止，需要修复
```

## 📝 使用示例

### 正常提交流程

```bash
$ git add src/main.py
$ git commit -m "feat: add new function"

[INFO] Installing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Installing environment for https://github.com/PyCQA/flake8.
Trim Trailing Whitespace.................................Passed
Fix End of Files.........................................Passed
Check Yaml...............................................Passed
Check JSON...............................................Passed
Check for merge conflicts................................Passed
Check for added large files..............................Passed
Don't commit to branch...................................Passed
flake8...................................................Passed
isort....................................................Passed
Validate prefab-manifest.json............................Passed
Run pytest...............................................Passed
Check version sync.......................................Passed

[main 5a3c2e1] feat: add new function
 1 file changed, 10 insertions(+), 2 deletions(-)
```

### 检查失败的情况

```bash
$ git commit -m "fix: update code"

flake8...................................................Failed
- hook id: flake8
- exit code: 1

src/main.py:28:1: F401 'typing.Dict' imported but unused
src/main.py:28:1: F401 'typing.Any' imported but unused

# 提交被阻止！需要先修复这些问题
```

## 🔧 常用命令

### 手动运行所有检查

```bash
# 对所有文件运行检查（不仅仅是暂存的文件）
uv run pre-commit run --all-files
```

### 跳过检查（不推荐）

```bash
# 仅在紧急情况下使用
git commit --no-verify -m "emergency fix"
```

### 运行特定检查

```bash
# 只运行 flake8
uv run pre-commit run flake8 --all-files

# 只运行单元测试
uv run pre-commit run pytest --all-files

# 只验证 manifest
uv run pre-commit run validate-manifest
```

### 更新 hooks

```bash
# 更新所有 hooks 到最新版本
uv run pre-commit autoupdate
```

### 卸载 hooks

```bash
# 如果需要移除 pre-commit hooks
uv run pre-commit uninstall
```

## ⚙️ 配置说明

### 自定义检查规则

编辑 `.pre-commit-config.yaml` 文件修改配置：

```yaml
repos:
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']  # 可以修改行长度限制
```

### 跳过特定检查

在提交时跳过特定的 hook：

```bash
# 跳过 pytest（但仍运行其他检查）
SKIP=pytest git commit -m "WIP: work in progress"

# 跳过多个检查
SKIP=pytest,flake8 git commit -m "WIP"
```

### 针对特定文件

Pre-commit 会自动智能判断：
- 只检查你修改的文件
- Python hooks 只运行在 `.py` 文件上
- Manifest 验证仅在相关文件修改时运行

## 🐛 故障排除

### 问题：hooks 安装失败

```bash
# 重新安装 pre-commit
uv sync --dev --force-reinstall
uv run pre-commit install
```

### 问题：某个检查一直失败

```bash
# 查看详细错误信息
uv run pre-commit run <hook-id> --all-files --verbose

# 例如：
uv run pre-commit run flake8 --all-files --verbose
```

### 问题：hooks 运行很慢

```bash
# Pre-commit 会缓存环境，首次运行较慢是正常的
# 后续提交会快很多

# 清理缓存（如果需要）
uv run pre-commit clean
```

### 问题：需要在 CI 中运行相同检查

GitHub Actions 工作流已包含这些检查：

```yaml
# .github/workflows/build-and-release.yml
- name: Run Flake8
  run: uv run --with flake8 flake8 src/
```

## 📚 最佳实践

1. **始终安装 pre-commit hooks**
   - 克隆项目后第一件事：`uv run pre-commit install`

2. **提交前手动测试**
   - 运行 `uv run pytest tests/` 确保测试通过

3. **小步提交**
   - 每次提交只包含一个逻辑变更
   - 更容易通过检查

4. **修复而不是跳过**
   - 不要使用 `--no-verify` 跳过检查
   - 修复问题比绕过检查更有价值

5. **保持 hooks 更新**
   - 定期运行 `uv run pre-commit autoupdate`

## 🔗 相关链接

- [Pre-commit 官方文档](https://pre-commit.com/)
- [支持的 Hooks 列表](https://pre-commit.com/hooks.html)
- [Flake8 文档](https://flake8.pycqa.org/)
- [isort 文档](https://pycqa.github.io/isort/)

## ❓ 常见问题

### Q: pre-commit 会影响提交速度吗？

A: 首次运行时会安装环境（较慢），之后会使用缓存，通常只需 2-5 秒。相比发现问题后再修复，这个时间是值得的。

### Q: 可以只对某些分支启用吗？

A: Pre-commit hooks 对所有分支生效。但你可以针对不同分支配置不同的 CI/CD 流程。

### Q: 团队成员必须安装吗？

A: 强烈建议！即使不安装，CI/CD 仍会运行相同检查。本地安装可以更早发现问题，避免 CI 失败。

### Q: 如何在 CI 中运行 pre-commit？

A: 可以在 GitHub Actions 中添加：

```yaml
- name: Run pre-commit
  run: |
    uv run pre-commit install
    uv run pre-commit run --all-files
```

---

**💡 提示**: 遇到问题？查看 [Issues](https://github.com/your-org/prefab-template/issues) 或提交新问题。
