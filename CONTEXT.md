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

### 0. 仓库出口

MaxNow 当前使用一个 GitHub 仓库，同时维护两个站点出口：

- `dash/`：`dash.maxnow.cn` 的私人状态工作站，包含页面代码和 `dash/data/*` 运行数据。
- `blog/`：`blog.maxnow.cn` 的公开博客发布层工作区，当前包含首页预览、专题页预览和方案说明页。
- 根目录：保留项目级文档、脚本、OpenClaw skill 和本地开发入口。

暂时不拆成独立 GitHub 仓库。只有当 blog 形成独立构建、独立部署和明显不同的发布节奏后，再考虑拆 repo。

### 1. 产品长期上下文

这些文件保存“MaxNow 是什么”和“为什么这样做”，其中 `CONTEXT.md` 主要服务于代理接力。

- `SPEC.md`：已经确定的产品定义、页面边界、数据契约和实现约束。
- `ROADMAP.md`：当前可执行路线图，保存 Now / Next / Later / Blocked / Done。
- `IDEAS.md`：尚未确定的想法、未来入口、待研究问题。
- `UPDATE_LOG.md`：重要产品方向、规则、结构变化的更新记录。
- `SERVER_RUNBOOK.md`：服务器 SSH、nginx、静态站部署和排障说明。
- `CONTEXT.md`：上下文地图，也就是当前这个文件。
- 公开博客方向：内容源在 personal-wiki，发布层规划在 MaxNow；当前推荐 `blog.maxnow.cn`，不放进 `dash.maxnow.cn` 一级导航。

维护方式：

- `CONTEXT.md` 主要面向 Codex / 代理接力，使用中文以便 Owner 随时检查。
- `SPEC.md`、`ROADMAP.md`、`IDEAS.md`、`UPDATE_LOG.md` 主要面向 Owner 和 Codex 共同阅读。
- Codex 或 Owner 可以更新。
- OpenClaw 日常任务不能修改这些文件。

文档职责判断：

- 当前 MD 文件不算冗余严重；它们分别承担规则、规格、路线、上下文、想法、更新记录、部署和服务器操作。
- 轻微重叠主要出现在 `SPEC.md` 和 `CONTEXT.md`：`SPEC.md` 写稳定产品规则，`CONTEXT.md` 写代理接手时需要知道的当前状态和文件地图。
- 暂时不把文档移入 `docs/`，因为根目录文档更容易被 Owner 和代理第一时间发现；等文档数量继续增长后再考虑整理目录。

### 2. 代理执行上下文

这些文件告诉 Codex / OpenClaw 怎么工作。

- `AGENTS.md`：本仓库的通用代理规则。
- `openclaw/maxnow-dashboard/SKILL.md`：OpenClaw 更新 dashboard / ai-news 数据时的执行规则。
- `openclaw/last-30/SKILL.md`：OpenClaw 更新 Last-30 滚动记忆时的执行规则。
- `scripts/check.py`：本地一致性校验脚本。
- `scripts/sync_wiki_todos.py`：通过 GitHub CLI 读取 private personal-wiki 并刷新 `dash/data/wiki-todos.*`。
- `scripts/sync_system_status.py`：采集 nginx、HTTPS、git commit、磁盘、内存和 wiki-todos 同步状态，只刷新 dashboard 的系统状态字段。
- `SERVER_RUNBOOK.md`：服务器操作和部署排障手册，改服务器前先读。

维护方式：

- 面向代理执行，可以使用英文。
- 规则要短、明确、可执行。
- 当产品边界变化时，要同步更新这些文件。

### 3. 每日状态上下文

这些文件驱动当前网页。

- `dash/data/dashboard.json`：个人状态、主线、今日推进、日常记录、时间点、系统状态、Token 使用。
- `dash/data/dashboard.js`：从 `dashboard.json` 生成的浏览器 wrapper。
- `dash/data/ai-news.json`：外部 AI 输入。
- `dash/data/ai-news.js`：从 `ai-news.json` 生成的浏览器 wrapper。
- `dash/data/wiki-todos.json`：从 private personal-wiki `wiki/tasks/todo.json` 同步而来的近期待办只读缓存。
- `dash/data/wiki-todos.js`：从 `wiki-todos.json` 生成的浏览器 wrapper。
- `scripts/sync_wiki_todos.py`：通过本地或服务器 `gh` 登录态刷新 `dash/data/wiki-todos.*`，避免前端暴露 GitHub token。

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

- `dash/data/last-30.json`
- `dash/data/last-30.js`
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

### 5. 公开博客上下文

公开博客属于 MaxNow 的公开表达方向，但不属于 `dash.maxnow.cn` 的私人状态工作站本体。

当前方案：

- 域名：`blog.maxnow.cn`。
- 主域名 `maxnow.cn` 继续保留给未来公开主页或个人入口。
- 内容源：private personal-wiki 的 `raw/blog-vioiv`，当前包含旧 Hexo Markdown 211 篇和缓存图片 167 个。
- personal-wiki 负责原始归档、隐私判断、发布筛选和长期知识归属。
- MaxNow 仓库负责公开发布层：构建脚本、文章数据、静态页面、标签、归档、RSS、部署说明和 dashboard 状态入口。
- `blog/index.html` 是当前博客首页预览页，不是自动构建产物。
- `blog/topics.html` 是当前博客专题页预览页，用于确认“文章 / 专题”分页面导航体验。
- `blog/preview.html` 是博客方案说明页，不是正式线上入口。

维护边界：

- 不从公开前端直接读取 private personal-wiki。
- 不把所有旧文一次性公开发布；先通过 public / published 标记或发布 manifest 筛选。
- `dash.maxnow.cn` 顶部右侧可放一个指向 `blog.maxnow.cn` 的弱外部链接；左侧导航只保留 Dash 内部页面。页面内最多展示发布进度、待筛选数量和最近发布摘要。

## 上下文更新规则

- 不要直接在 `main` 上修改代码或文档；先从最新 `main` 拉短期工作分支。
- 新功能分支使用 `feature/<short-demand-name>`，修复分支使用 `bugfix/<short-bug-name>`，除非 Owner 指定别的名字。
- 工作完成并检查后，再合回 `main`；如果改动有风险，先询问 Owner。
- 确定的产品行为写进 `SPEC.md`。
- 当前待做、下一步、卡点和阶段路线写进 `ROADMAP.md`。
- 未确定的产品想法写进 `IDEAS.md`。
- 重要变更写进 `UPDATE_LOG.md`。
- 会影响代理接力、文件职责、自动化边界或下一步路线的上下文写进 `CONTEXT.md`。
- 每天变化的数据写进 `dash/data/*.json`；MaxNow 功能待办、产品路线和“下一步要实现什么”不要写进数据文件。
- 本地一致性校验逻辑写进 `scripts/check.py`。
- 自动化执行边界写进 `AGENTS.md` 和对应 OpenClaw skill。
- 服务器 SSH、nginx、域名部署和排障步骤写进 `SERVER_RUNBOOK.md`。
- 给 Owner 看的内容用中文；给代理执行的规则可以用英文。

## 当前缺口

- Home 页面已接入“今日 / 本周 / 近 30 天大事”的展示模块，但还需要 Owner 视觉确认和必要微调。
- wiki-todos 的手动同步链路已跑通，但服务器定时自动同步还没有落地：需要决定用 cron 还是 systemd timer，并补日志与失败提醒。
- 系统状态采集脚本已建立，但还没有接入服务器定时任务。
- `dash/data/dashboard.json` 里的信息仍是旧快照，更新时间停留在 2026-05-26。
- 前端静态站已部署到 `dash.maxnow.cn`；仓库位于 `/var/www/maxnow-dashboard`，nginx 应指向 `/var/www/maxnow-dashboard/dash`。
- 服务器 GitHub CLI 已授权，可以读取 private personal-wiki；后续重点是把同步命令固化为定时任务。
- 个人博客已确定推荐走 `blog.maxnow.cn`，但还缺发布 manifest / front matter 策略、构建脚本、nginx 子域名配置和第一批公开文章清单。
- MaxNow 功能待办以 `ROADMAP.md` 为准，不应混入 dashboard / last-30 运行数据。
- 当前可执行任务以 `ROADMAP.md` 为准。

## 建议下一步

1. 给 `scripts/sync_wiki_todos.py` 和 `scripts/sync_system_status.py` 接服务器 cron 或 systemd timer，并记录日志路径。
2. 让 Home 系统状态显示服务器定时采集后的 nginx、HTTPS、git commit、磁盘、内存和最近同步状态。
3. 补一个本地/服务器数据更新工具，减少手工重写 wrapper 的错误。
4. 为 `blog.maxnow.cn` 补静态博客构建链路：发布 manifest、Markdown 转换、图片复制、文章列表、标签归档和 nginx 配置。
