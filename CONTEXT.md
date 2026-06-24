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
- `blog/`：`blog.maxnow.cn` 的公开博客发布层工作区，当前包含文章流首页、专题索引、分类二级页和方案说明页。
- 根目录：保留项目级文档、脚本、OpenClaw skill 和本地开发入口。

暂时不拆成独立 GitHub 仓库。只有当 blog 形成独立构建、独立部署和明显不同的发布节奏后，再考虑拆 repo。

### 1. 产品长期上下文

这些文件保存“MaxNow 是什么”和“为什么这样做”，其中 `CONTEXT.md` 主要服务于代理接力。

- `SPEC.md`：已经确定的产品定义、页面边界、数据契约和实现约束。
- `STYLE_CONTEXT.md`：Dash / Blog 的前端视觉上下文，记录品牌图标、圆角、hover、语义配色、豆奶展示和样式检查规则。
- `ROADMAP.md`：当前可执行路线图，保存 Now / Next / Later / Blocked / Done。
- `IDEAS.md`：尚未确定的想法、未来入口、待研究问题。
- `UPDATE_LOG.md`：重要产品方向、规则、结构变化的更新记录。
- `SERVER_RUNBOOK.md`：服务器 SSH、nginx、静态站部署和排障说明。
- `CONTEXT.md`：上下文地图，也就是当前这个文件。
- 公开博客方向：内容源在 personal-wiki，发布层规划在 MaxNow；当前推荐 `blog.maxnow.cn`，不放进 `dash.maxnow.cn` 一级导航。

维护方式：

- `CONTEXT.md` 主要面向 Codex / 代理接力，使用中文以便 Owner 随时检查。
- `SPEC.md`、`STYLE_CONTEXT.md`、`ROADMAP.md`、`IDEAS.md`、`UPDATE_LOG.md` 主要面向 Owner 和 Codex 共同阅读。
- Codex 或 Owner 可以更新。
- OpenClaw 日常任务不能修改这些文件。

文档职责判断：

- 当前 MD 文件不算冗余严重；它们分别承担规则、规格、路线、上下文、想法、更新记录、部署和服务器操作。
- 轻微重叠主要出现在 `SPEC.md` 和 `CONTEXT.md`：`SPEC.md` 写稳定产品规则，`CONTEXT.md` 写代理接手时需要知道的当前状态和文件地图。
- 前端视觉规则不要继续散落在聊天或 `CONTEXT.md` 段落里；稳定的样式口径写进 `STYLE_CONTEXT.md`。
- 暂时不把文档移入 `docs/`，因为根目录文档更容易被 Owner 和代理第一时间发现；等文档数量继续增长后再考虑整理目录。

### 2. 代理执行上下文

这些文件告诉 Codex / OpenClaw 怎么工作。

- `AGENTS.md`：本仓库的通用代理规则。
- `openclaw/maxnow-dashboard/SKILL.md`：OpenClaw 更新 dashboard / ai-news 数据时的执行规则。
- `openclaw/last-30/SKILL.md`：OpenClaw 更新 Last-30 滚动记忆时的执行规则。
- `scripts/check.py`：本地一致性校验脚本。
- `scripts/update_data.py`：统一数据更新入口；`runtime` 用于服务器定时刷新 wiki-todos、Ricky 旅行记录、天气、系统状态和项目元信息，`wrap all` 重生成 wrapper，`project-status` 显式从 `ROADMAP.md` 刷新 Home 项目状态。
- `scripts/sync_wiki_todos.py`：通过 GitHub CLI 读取 private personal-wiki 并刷新 `dash/data/wiki-todos.*`。
- `scripts/sync_system_status.py`：采集 nginx、HTTPS、git commit、磁盘、内存和 wiki-todos 同步状态，只刷新 dashboard 的系统状态字段；Home 系统状态卡作为入口，云服务页复用同一份快照展示更完整的服务器状态。
- `scripts/sync_openclaw_usage.py`：只读服务器 `/root/.openclaw` 轨迹，生成 OpenClaw Token 用量账本和 OpenRouter 等价费用估算。
- `scripts/sync_codex_usage.py`：只读 `.codex/sessions` 中的 `token_count` 事件，生成 Codex Token 用量账本；只导出 token 统计，不导出 prompt / response 正文。
- `scripts/sync_token_usage.py`：合并 OpenClaw / Codex 源账本，生成 Token 页面优先读取的统一总账。
- `scripts/sync_weather.py`：从 Open-Meteo 免费 forecast API 刷新北京市海淀区天气，写入 `dash/data/dashboard.*` 的 `weather` 字段。
- `SERVER_RUNBOOK.md`：服务器操作和部署排障手册，改服务器前先读。

维护方式：

- 面向代理执行，可以使用英文。
- 规则要短、明确、可执行。
- 当产品边界变化时，要同步更新这些文件。

### 3. 每日状态上下文

这些文件驱动当前网页。

- `dash/data/dashboard.json`：个人状态、主线、今日推进、日常记录、时间点、系统状态、Token 使用、Home 天气卡和 Home 时间卡片的手动特殊日期列表。
- `dash/data/dashboard.js`：从 `dashboard.json` 生成的浏览器 wrapper。
- `dash/data/ai-news.json`：首页展示用的外部 AI 输入，取免费 AI 外部信号中的 0-3 条高相关内容。
- `dash/data/ai-news.js`：从 `ai-news.json` 生成的浏览器 wrapper。
- `dash/data/wiki-todos.json`：从 private personal-wiki `wiki/tasks/todo.json` 同步而来的近期待办只读缓存。
- `dash/data/wiki-todos.js`：从 `wiki-todos.json` 生成的浏览器 wrapper。
- `dash/data/openclaw-usage.json`：OpenClaw 每日 token 用量、按模型 / 任务拆分和 OpenRouter 等价费用估算。
- `dash/data/codex-usage.json`：Codex 每日 token 用量、按模型 / 任务拆分；来源为 `.codex/sessions` 的 `token_count` 事件。
- `dash/data/token-usage.json`：OpenClaw / Codex 合并后的统一 Token 总账，Token 页面优先读取它。
- `dash/data/*-usage.js`：从对应 usage JSON 生成的浏览器 wrapper。
- `dash/data/project-meta.json`：MaxNow 当前版本、部署说明和最近更新摘要，由 `scripts/sync_project_meta.py` 从 `VERSION`、Git 状态和 `UPDATE_LOG.md` 生成。
- `dash/data/project-meta.js`：从 `project-meta.json` 生成的浏览器 wrapper。
- `dash/data/dounai_checkin.json`：豆奶每日签到记录、账号余量快照和账号日均可用历史，由 OpenClaw 签到自动化每天更新；Home 只读展示今日流量、今日豆丁、今日账号有效期延长时长、累计签到天数、累计流量和累计账号有效期延长时长，并作为豆奶详情页入口。豆奶详情页展示近 30 天流量/时长折线图，以及剩余流量、有效期、每日可用预算和近 30 天账号日均可用趋势。
- `dash/data/ricky.json`：同行记页面的只读数据源，由 `scripts/sync_ricky_travel.py` 从 personal-wiki `wiki/relationships/ricky-travel.json` 生成，维护“我和 Ricky”的世界地图点位、地点、旅行记录、统计和可选照片 / 来源链接。
- `dash/data/ricky.js`：从 `ricky.json` 生成的浏览器 wrapper。
- `scripts/sync_wiki_todos.py`：通过本地或服务器 `gh` 登录态刷新 `dash/data/wiki-todos.*`，避免前端暴露 GitHub token。
- `scripts/sync_ricky_travel.py`：通过本地相邻 personal-wiki checkout 或服务器 `gh` 登录态读取 `wiki/relationships/ricky-travel.json`，刷新 `dash/data/ricky.*`。
- `scripts/sync_weather.py`：抓取北京市海淀区天气、温度、高低温和天气图标类型，只刷新 dashboard 的 `weather` 字段。
- `scripts/sync_ai_last30.py`：抓取免费公开 AI 信号源，刷新 `dash/data/ai-news.*` 和 `dash/data/last-30.*`；采集脚本本身不调用模型，不消耗 token。

维护方式：

- OpenClaw 日常任务可以更新。
- 每次更新后必须校验 JSON，并重新生成对应 `.js` wrapper。
- 这里保存“今天要看的状态”，不要塞长期产品讨论。
- Home 顶部天气卡读取 `dash/data/dashboard.json.weather`，展示在小日历左侧；前端不直接请求外部天气接口。
- private personal-wiki 待办不能由前端直接读取；需要先运行 `python scripts/update_data.py runtime` 或 `python scripts/sync_wiki_todos.py` 生成 MaxNow 本地缓存。
- 服务器已安装并授权 GitHub CLI，账号 `V-ioi-V` 可读取 private personal-wiki；服务器上已验证 `python3 scripts/sync_wiki_todos.py` 能成功生成待办缓存。
- 系统状态可以由 `python scripts/sync_system_status.py` 自动采集，但它只能更新 `automation` 和 `system`，不能覆盖今日判断、当前主线、今日推进或日常记录。
- 天气可以由 `python scripts/update_data.py weather` 或服务器 `runtime` 定时刷新，数据源是 Open-Meteo 免费 forecast API。
- OpenClaw 用量可以由 `python scripts/update_data.py openclaw-usage` 刷新。脚本读取 OpenClaw trajectory 中的 `usage.input`、`usage.output`、`usage.cacheRead` 和 `usage.total`，按 Asia/Shanghai 日期聚合；费用字段使用 OpenRouter 当前或缓存价格估算，不能当作真实供应商扣费。
- MaxNow 版本号由根目录 `VERSION` 手动维护，格式为 `x.x.x.xx`；`python scripts/update_data.py project-meta` 会刷新 Home 的版本与最近更新模块。
- Codex 用量可以由 `python scripts/update_data.py codex-usage` 刷新。脚本默认读取本机 `~/.codex/sessions`，也可用 `CODEX_STATE_DIR`、`MAXNOW_CODEX_SOURCE_KEY` 和 `MAXNOW_CODEX_SOURCE_LABEL` 指向服务器或其他 Codex 状态目录；它优先从 `turn_context.model` 读取具体模型名，只导出 token 统计，不导出对话正文。Codex 费用按 OpenAI API 等价价格估算，刷新后会同步生成 `token-usage.*`。
- `dash/data/token-usage.json` 是 Token 页统一入口；后续服务器 Codex collector、其他来源和自动化都应合入这个总账。
- 豆奶签到展示只读取 `dash/data/dounai_checkin.json` 中的流量、豆丁、时长、累计签到天数、账号余量快照、账号日均可用历史和近 30 天 records；豆丁只进入 Home 摘要，不进入豆奶详情页展示口径，不要在 MaxNow 前端增加签到写入、账号操作或 cron 管理。
- 同行记页面只读取 `dash/data/ricky.json`，不在前端编辑、不回写 personal-wiki、不依赖外部在线地图服务；事实来源归 personal-wiki 的 `wiki/relationships/ricky-travel.json`。
- 服务器上的豆奶签到由 root/OpenClaw 侧脚本维护；`/root/.openclaw/gen_checkin_data.py` 会把生成结果同时写入 `/root/MaxNow/dash/data/dounai_checkin.json` 和线上部署目录 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。线上页面读取后者。2026-06-21 已扩展该脚本，让它用现有豆奶登录态只读抓取剩余流量、账号有效期、VIP 有效期和日均可用流量，写入 `account` 字段，并按日期维护 `account_history`。

### 4. AI 外部信号滚动记忆

这是 Last-30 当前定位：保存今天、本周和近 30 天的 AI 外部信号。它不是 MaxNow 内部项目日志，也不是泛新闻流；只保留和 Owner 当前工具、模型选择、agent 能力、开发者生态或成本有关的信号。

已经新增：

- `dash/data/last-30.json`
- `dash/data/last-30.js`
- `openclaw/last-30/SKILL.md`

它负责保存：

- 今日 AI 信号。
- 本周 AI 变化。
- 近 30 天 AI 主线。
- 对 MaxNow、Codex、OpenClaw、模型选择或 token 成本的潜在影响。
- 需要继续观察或 Owner 确认的信号。

维护方式：

- 免费版由 `scripts/sync_ai_last30.py` 抓取官方 RSS / 博客、GitHub releases、Hacker News、GDELT、arXiv 等免费公开源，写入 `dash/data/ai-news.*` 和 `dash/data/last-30.*`。
- 服务器已通过 `ubuntu` 用户 crontab 接入 `MAXNOW-AI-LAST30-SYNC`：每天服务器本地时间 00:00 运行 `python3 scripts/update_data.py ai-last30`，日志写入 `/var/www/maxnow-dashboard/logs/ai-last30.log`。
- 脚本先做本地抓取、关键词打分、去重和短摘要，不调用模型；采集本身不消耗 token。
- 如果让 OpenClaw 二次总结，只应喂少量候选，避免把新闻全文直接交给模型。
- X / Twitter 官方 API 暂不接入，除非 Owner 明确批准付费 API 和博主白名单。
- 每条记录尽量带来源、置信度、是否需要 Owner 确认。

### 5. 公开博客上下文

公开博客属于 MaxNow 的公开表达方向，但不属于 `dash.maxnow.cn` 的私人状态工作站本体。

当前方案：

- 域名：`blog.maxnow.cn`。
- 主域名 `maxnow.cn` 继续保留给未来公开主页或个人入口。
- 内容源：private personal-wiki 的 `raw/blog-vioiv`，当前包含旧 Hexo Markdown 211 篇和缓存图片 167 个。
- personal-wiki 负责原始归档、隐私判断、发布筛选和长期知识归属。
- MaxNow 仓库负责公开发布层：构建脚本、文章数据、静态页面、标签、归档、RSS、部署说明和 dashboard 状态入口。
- `blog/index.html` 是当前博客文章流首页预览页，不是自动构建产物。
- `blog/random-articles.js` 让 Blog 首页可以从四个专题分类二级页的现有文章卡片里随机抽取一批文章预览，不新增后端或数据库。
- `blog/topics.html` 是当前博客专题索引页，用于确认“分类总览 -> 分类二级页 -> 返回专题索引”的浏览体验。
- `blog/overview.html` 是当前博客归档总览页，作为左侧独立 tab 展示文章数、图片数、分类数和发布状态；不要再把这些统计做成文章页或专题页 sidebar 信息卡。
- `blog/topic-*.html` 是当前专题分类二级页预览；页面通过 `blog/topic-tags.js` 在分类内生成细分标签索引，并把文章按主标签分组展示。
- `blog/post-preview.html` 是临时文章详情页预览；当前使用 `20200403-以太网、IP、TCP、UDP头部格式.md` 的正文做真实内容样例，后续真实构建时再替换为每篇文章自己的 slug 页面。
- 文章详情页会通过 `from=articles` / `from=topics` 保留入口来源：从文章流进入时高亮 `文章`，从专题分类进入时高亮 `专题`，返回按钮也回到对应上一级。
- `blog/preview.html` 是博客方案说明页，不是正式线上入口。
- 博客左侧导航当前为 `文章 / 专题 / 总览` 三个同级 tab；`文章` 看时间流，`专题` 进分类，`总览` 看归档统计。
- Dash 和 Blog 当前视觉基调统一参考轻量用户中心风格：白色 sidebar、浅蓝灰背景、柔和白卡片、淡边框、彩色图标入口和稳定系统字体；不要回退到深色重阴影或外部 Web Font 依赖。
- Dash 和 Blog 当前页卡圆角基准为 14px，内部小图标容器约 12px；豆奶顶部参数使用小 SVG 图标加语义色，不要回退到纯文字参数块。详细前端样式规则以 `STYLE_CONTEXT.md` 为准。
- MaxNow 正式品牌图标使用 Owner 于 2026-06-21 确认的深蓝 `M/N` 标识，资产为 `dash/assets/maxnow-icon.png` 和 `blog/assets/maxnow-icon.png`；左侧品牌区使用 28px 无底框小图标并只显示 `MaxNow`，不要再回退到旧的浅蓝 `M` SVG 或在 Blog 品牌区显示 `blog.maxnow.cn` 副标题。

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
- 本地一致性校验逻辑写进 `scripts/check.py`，数据更新入口写进 `scripts/update_data.py`。
- 自动化执行边界写进 `AGENTS.md` 和对应 OpenClaw skill。
- 服务器 SSH、nginx、域名部署和排障步骤写进 `SERVER_RUNBOOK.md`。
- 给 Owner 看的内容用中文；给代理执行的规则可以用英文。

## 当前缺口

- Home 页面已接入“今日 / 本周 / 近 30 天大事”的展示模块，但还需要 Owner 视觉确认和必要微调。
- Home 右侧已接入豆奶签到只读摘要卡片，点击可进入豆奶详情 tab；详情页展示近 30 天流量/时长折线图。数据来自 `dash/data/dounai_checkin.json`，签到脚本和 9:00 cron 由 OpenClaw 管理。
- 2026-06-19 已修复豆奶签到数据路径分叉：当天签到成功写入 `/root/MaxNow`，但线上部署目录仍停在 2026-06-18；现在 root 数据生成脚本会双写旧工作区和 `/var/www/maxnow-dashboard`。
- wiki-todos 服务器自动同步已落地：`ubuntu` 用户 crontab 每 10 分钟运行一次 `MAXNOW-DASHBOARD-SYNC`，通过 `python3 scripts/update_data.py runtime` 刷新 `dash/data/wiki-todos.*`、系统状态缓存并执行 `scripts/check.py`。
- Last-30 AI 外部信号服务器自动同步已落地：`ubuntu` 用户 crontab 每天 00:00 运行一次 `MAXNOW-AI-LAST30-SYNC`，通过 `python3 scripts/update_data.py ai-last30` 刷新 `dash/data/ai-news.*` 和 `dash/data/last-30.*`。
- 系统状态采集已接入 Home：页面展示 nginx、HTTPS、证书、部署 commit、最近 pull、cron、wiki-todos 同步、失败日志、资源和云服务器状态。
- Token 用量账本已建立并接入 Token 页面：`scripts/sync_openclaw_usage.py` 可在服务器读取 `/root/.openclaw` 轨迹并生成 `dash/data/openclaw-usage.*`；`scripts/sync_codex_usage.py` 可读取 `.codex/sessions` 的 `token_count` 事件并生成 `dash/data/codex-usage.*`；`scripts/sync_token_usage.py` 合并为 `dash/data/token-usage.*`。页面支持 1d / 7d / 30d / all、总量 / 输入 / 输出 / 缓存读 / 缓存命中率 / 费用、模型占比、会话消耗和最近 30 天折线趋势。OpenClaw 费用为 OpenRouter 等价估算，Codex 费用为 OpenAI API 等价估算。
- Dash 左侧导航已新增“云服务”tab，位于 Token 下方。该页只读列出服务器自动化、数据同步、站点托管和日志边界，不从前端触发服务器操作。
- Dash 左侧导航已新增“同行记”tab，副标题为“我和 Ricky”。该页用 Leaflet + OpenStreetMap 真实地图和轻量统计承载两人的共同足迹，地点和旅行记录暂时只进入 marker / popup 数据，不单独铺列表；内置 SVG 地图只作为 fallback。
- `dash/data/dashboard.json` 的项目主线可以用 `python scripts/update_data.py project-status` 从 `ROADMAP.md` 显式刷新；定时任务只运行 `runtime`，不自动覆盖 Owner 判断字段。
- Home 时间卡片已支持 `dashboard.json.specialDates`：用手动维护的公历日期或一次性日期在当天显示生日、纪念日等轻量提醒；没有命中时继续显示“今日无节日”。
- Home 顶部已新增北京市海淀区天气卡：地点、天气、当前温度、今日高低温和图标来自 `dashboard.json.weather`，并由 `runtime` 定时刷新。
- Home 左侧导航栏已收窄到更紧凑的桌面宽度，保留原有三个入口，不做折叠侧栏。
- 前端静态站已部署到 `dash.maxnow.cn`；仓库位于 `/var/www/maxnow-dashboard`，nginx 应指向 `/var/www/maxnow-dashboard/dash`。
- 服务器 GitHub CLI 已授权，可以读取 private personal-wiki；同步命令已固化为 crontab，失败日志会进入 Home 系统状态。
- 个人博客已确定推荐走 `blog.maxnow.cn`，但还缺发布 manifest / front matter 策略、构建脚本、nginx 子域名配置和第一批公开文章清单。
- 同行记已经有页面、数据契约和 personal-wiki 同步脚本；后续重点是继续在 personal-wiki 补真实地点、日期、备注和照片入口。
- MaxNow 功能待办以 `ROADMAP.md` 为准，不应混入 dashboard / last-30 运行数据。
- 当前可执行任务以 `ROADMAP.md` 为准。

## 建议下一步

1. 为 `blog.maxnow.cn` 补静态博客构建链路：发布 manifest、Markdown 转换、图片复制、文章列表、标签归档和 nginx 配置。
2. 观察 Last-30 免费 AI 外部信号的来源稳定性，并在必要时替换长期失败的免费源。
3. 给 Codex Token 统计补自动化：本机 Windows Task Scheduler、服务器 Codex collector / cron、失败日志和部署目录权限。
