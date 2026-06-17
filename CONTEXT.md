# MaxNow 上下文总览

这个文件主要给 Codex / 代理接力使用，用来快速恢复 MaxNow 的项目上下文；Owner 也可以阅读，但它不是汇报文档。

它回答一个问题：MaxNow 的上下文分别放在哪里、谁来维护、什么时候更新。

## 当前目标

MaxNow 要成为一个私人状态工作站，而不是新闻站或通用仪表盘。

它应该帮助 Owner 每天快速看见：

- 我今天处在什么状态。
- 我当前正在推进哪些主线。
- 今天和本周发生了什么重要事情。
- 最近 30 天有哪些持续主线、决定和卡点。
- OpenClaw、服务器、数据同步和 Token 使用是否正常。
- 有哪些外部 AI / 工具信号值得稍后注意。

## 上下文分层

### 1. 产品长期上下文

这些文件保存“MaxNow 是什么”和“为什么这样做”，其中 `CONTEXT.md` 主要服务于代理接力。

- `SPEC.md`：已经确定的产品定义、页面边界、数据契约和实现约束。
- `ROADMAP.md`：当前可执行路线图，保存 Now / Next / Later / Blocked / Done。
- `IDEAS.md`：尚未确定的想法、未来入口、待研究问题。
- `UPDATE_LOG.md`：重要产品方向、规则、结构变化的更新记录。
- `SERVER_RUNBOOK.md`：服务器 SSH、nginx、静态站部署和排障说明。
- `CONTEXT.md`：上下文地图，也就是当前这个文件。

维护方式：

- `CONTEXT.md` 主要面向 Codex / 代理接力，使用中文以便 Owner 随时检查。
- `SPEC.md`、`ROADMAP.md`、`IDEAS.md`、`UPDATE_LOG.md` 主要面向 Owner 和 Codex 共同阅读。
- Codex 或 Owner 可以更新。
- OpenClaw 日常任务不能修改这些文件。

### 2. 代理执行上下文

这些文件告诉 Codex / OpenClaw 怎么工作。

- `AGENTS.md`：本仓库的通用代理规则。
- `openclaw/maxnow-dashboard/SKILL.md`：OpenClaw 更新 dashboard / ai-news 数据时的执行规则。
- `openclaw/last-30/SKILL.md`：OpenClaw 更新 Last-30 滚动记忆时的执行规则。
- `scripts/check.py`：本地一致性校验脚本。
- `scripts/sync_wiki_todos.py`：通过 GitHub CLI 读取 private personal-wiki 并刷新 `data/wiki-todos.*`。
- `scripts/sync_system_status.py`：采集 nginx、HTTPS、git commit、磁盘、内存和 wiki-todos 同步状态，只刷新 dashboard 的系统状态字段。
- `SERVER_RUNBOOK.md`：服务器操作和部署排障手册，改服务器前先读。

维护方式：

- 面向代理执行，可以使用英文。
- 规则要短、明确、可执行。
- 当产品边界变化时，要同步更新这些文件。

### 3. 每日状态上下文

这些文件驱动当前网页。

- `data/dashboard.json`：个人状态、主线、今日推进、日常记录、时间点、系统状态、Token 使用。
- `data/dashboard.js`：从 `dashboard.json` 生成的浏览器 wrapper。
- `data/ai-news.json`：外部 AI 输入。
- `data/ai-news.js`：从 `ai-news.json` 生成的浏览器 wrapper。
- `data/wiki-todos.json`：从 private personal-wiki `wiki/tasks/todo.json` 同步而来的近期待办只读缓存。
- `data/wiki-todos.js`：从 `wiki-todos.json` 生成的浏览器 wrapper。
- `scripts/sync_wiki_todos.py`：通过本地或服务器 `gh` 登录态刷新 `data/wiki-todos.*`，避免前端暴露 GitHub token。

维护方式：

- OpenClaw 日常任务可以更新。
- 每次更新后必须校验 JSON，并重新生成对应 `.js` wrapper。
- 这里保存“今天要看的状态”，不要塞长期产品讨论。
- private personal-wiki 待办不能由前端直接读取；需要先运行 `python scripts/sync_wiki_todos.py` 生成 MaxNow 本地缓存。
- 服务器已安装并授权 GitHub CLI，账号 `V-ioi-V` 可读取 private personal-wiki；服务器上已验证 `python3 scripts/sync_wiki_todos.py` 能成功生成待办缓存。
- 系统状态可以由 `python scripts/sync_system_status.py` 自动采集，但它只能更新 `automation` 和 `system`，不能覆盖今日判断、当前主线、今日推进或日常记录。

### 4. 滚动记忆上下文

这是下一阶段要持续完善的上下文层。数据文件和 OpenClaw skill 已建立，页面展示和自动更新仍在推进。

已经新增：

- `data/last-30.json`
- `data/last-30.js`
- `openclaw/last-30/SKILL.md`

它负责保存：

- 今日大事。
- 本周大事。
- 近 30 天主线。
- 重要决定。
- 卡点 / 等待项。
- 需要 Owner 确认的判断。

维护方式：

- 不要每天从零总结 30 天。
- 用“昨天已有滚动摘要 + 今天新增事实”做增量更新。
- 每条记录尽量带来源、置信度、是否需要 Owner 确认。

## 上下文更新规则

- 不要直接在 `main` 上修改代码或文档；先从最新 `main` 拉短期工作分支。
- 新功能分支使用 `feature/<short-demand-name>`，修复分支使用 `bugfix/<short-bug-name>`，除非 Owner 指定别的名字。
- 工作完成并检查后，再合回 `main`；如果改动有风险，先询问 Owner。
- 确定的产品行为写进 `SPEC.md`。
- 当前待做、下一步、卡点和阶段路线写进 `ROADMAP.md`。
- 未确定的产品想法写进 `IDEAS.md`。
- 重要变更写进 `UPDATE_LOG.md`。
- 会影响代理接力、文件职责、自动化边界或下一步路线的上下文写进 `CONTEXT.md`。
- 每天变化的数据写进 `data/*.json`；MaxNow 功能待办、产品路线和“下一步要实现什么”不要写进数据文件。
- 本地一致性校验逻辑写进 `scripts/check.py`。
- 自动化执行边界写进 `AGENTS.md` 和对应 OpenClaw skill。
- 服务器 SSH、nginx、域名部署和排障步骤写进 `SERVER_RUNBOOK.md`。
- 给 Owner 看的内容用中文；给代理执行的规则可以用英文。

## 当前缺口

- Home 页面已接入“今日 / 本周 / 近 30 天大事”的展示模块，但还需要 Owner 视觉确认和必要微调。
- wiki-todos 的手动同步链路已跑通，但服务器定时自动同步还没有落地：需要决定用 cron 还是 systemd timer，并补日志与失败提醒。
- 系统状态采集脚本已建立，但还没有接入服务器定时任务。
- `data/dashboard.json` 里的信息仍是旧快照，更新时间停留在 2026-05-26。
- 前端静态站已部署到 `dash.maxnow.cn`，使用 nginx 指向 `/var/www/maxnow-dashboard`。
- 服务器 GitHub CLI 已授权，可以读取 private personal-wiki；后续重点是把同步命令固化为定时任务。
- MaxNow 功能待办以 `ROADMAP.md` 为准，不应混入 dashboard / last-30 运行数据。
- 当前可执行任务以 `ROADMAP.md` 为准。

## 建议下一步

1. 给 `scripts/sync_wiki_todos.py` 和 `scripts/sync_system_status.py` 接服务器 cron 或 systemd timer，并记录日志路径。
2. 让 Home 系统状态显示服务器定时采集后的 nginx、HTTPS、git commit、磁盘、内存和最近同步状态。
3. 补一个本地/服务器数据更新工具，减少手工重写 wrapper 的错误。
