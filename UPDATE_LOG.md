# MaxNow 更新记录

这个文件记录 MaxNow 的重要更新，让产品方向、数据边界和实现决定可以被追溯。

## 使用规则

- 只要 Codex、Owner 或其他维护者改变了产品方向、页面代码、数据结构或操作规则，就在这里补一条。
- 每条记录保持简短、具体。
- 有必要时写清楚涉及哪些文件。
- 原始未来想法写进 `IDEAS.md`；已经确认的产品行为再同步进 `SPEC.md`。

## 2026-06-14

### 新增路线图文档

- 新增 `ROADMAP.md`，用 Now / Next / Later / Blocked / Done 维护当前可执行路线。
- 将 `ROADMAP.md` 纳入 `AGENTS.md`、`CONTEXT.md`、`SPEC.md` 和 `README.md` 的文档边界。
- 明确 `CONTEXT.md` 负责代理接力上下文，`ROADMAP.md` 负责待做事项和阶段路线。

原因：

- Owner 询问当前 md 是否都有用，需要把“待做事项”从聊天里固定成可持续维护的文档。

### 整理说明文档和本地校验

- 中文化并重写 `README.md`。
- 中文化并重写 `DEPLOY.md`。
- 新增 `scripts/check.py`，用于检查必要文件、JSON 合法性、wrapper 一致性和本地预览可访问性。
- 将 `scripts/check.py` 纳入 `AGENTS.md`、`SPEC.md` 和 `CONTEXT.md` 的项目边界。

原因：

- 在接服务器自动更新前，先把本地说明和一键校验补齐，降低后续部署风险。

### 固定分支工作流

- 新增规则：不要直接在 `main` 上修改代码或文档。
- 每次改动前先从最新 `main` 拉一个短期工作分支。
- 新功能分支使用 `feature/<short-demand-name>`，修复分支使用 `bugfix/<short-bug-name>`，除非 Owner 指定别的名字。
- 改完检查后再合回 `main`；如果改动有风险，先询问 Owner。

原因：

- Owner 明确要求先从主分支拉分支修改，避免直接改坏主分支。

### 启动 Last-30 首页展示分支

- 创建 `feature/last-30-home-context` 分支，继续推进 Last-30 首页展示。
- 将 `data/last-30.*` 和 `openclaw/last-30/SKILL.md` 纳入项目文件边界和数据契约。
- 更新 `CONTEXT.md`，标记 Last-30 数据文件和 skill 已建立，下一步重点转为首页展示和服务器自动更新。

原因：

- Owner 要求直接开始做，并要求后续分支名按需求语义命名。

### 补充项目上下文地图

- 新增 `CONTEXT.md`，说明 MaxNow 的上下文分层、文件职责、维护者和当前缺口。
- 明确 `CONTEXT.md` 主要给 Codex / 代理接力使用，Owner 可以检查但它不是汇报文档。
- 将 `CONTEXT.md` 纳入 `AGENTS.md` 和 `SPEC.md` 的文件边界。
- 在 `SPEC.md` 中补充 “Last-30 滚动记忆” 未来方向。
- 在 `IDEAS.md` 中记录 Last-30 滚动记忆想法。
- 修复 `data/dashboard.json` 的中文内容，使它和 `data/dashboard.js` 保持一致，避免页面读取 JSON 后出现乱码。
- 将 OpenClaw dashboard skill 的内部名字从 `maxnow-dashboard-maintainer` 缩短为 `maxnow-data`。

原因：

- Owner 希望整体补齐项目上下文，避免目标、数据、自动化和产品记忆分散在聊天里。

## 2026-06-13

### 调整文档语言分工

- 面向 Owner 阅读的产品文档使用中文。
- 面向 Codex / OpenClaw 等代理执行的规则文档可以继续使用英文。
- 将 `SPEC.md`、`IDEAS.md` 和 `UPDATE_LOG.md` 改为中文。
- 将语言分工写入 `AGENTS.md`，作为本仓库后续代理工作的固定规则。

原因：

- Owner 明确要求“给我看的用中文，你自己看的用英文”。

## 2026-06-12

### 增加长期想法记录和更新记录

- 新增 `IDEAS.md`，作为长期产品想法记录。
- 新增 `UPDATE_LOG.md`，作为项目更新记录。
- 记录“桌面伴随面板”方向：
  - macOS 顶部状态栏下拉个人面板。
  - Windows 桌面壁纸式个人看板。
- 更新项目规则，让未来维护者知道这两个文件需要持续维护。
- 更新 OpenClaw 维护边界，明确日常自动化不能编辑这些记忆文档。

原因：

- Owner 不希望新的 MaxNow 想法或项目更新在不同会话之间丢失。
