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
- 下一节芭蕾课是什么、最近实际训练节奏如何。
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
- `BALLET_GROWTH_SCORING.md`：芭蕾成长进度卡的独立计算标准，集中保存自动升班课次、规律 / 间歇口径与 Lv.1–Lv.10 课次门槛。
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
- Home 主内容区的稳定版式是 `home-board` 两列外壳：左列为 `home-lane-primary`，右列为 `home-side-stack`。左列承载个人主任务和内容型长模块，当前包括 Token 热力格、Personal Wiki、待推进、AI 前沿和版本更新，其中版本更新固定放在 AI 前沿下方；右列只承载短扫读状态入口。`home-lane-signal` / `home-lane-rail` 在右列内只作为语义分组，视觉上展平成 widget 网格；`widget-compact` 占半宽，`widget-wide` / `mid-*` 占满右列。Home 不再保留单独“稍后留意”或“今日记录”卡片，待办线索进入待推进 / Roadmap，系统链路进入云服务 / 系统状态，静态项目原则进入规格、上下文或版本更新。所有首页模块必须先归入语义 lane，保留 `home-card-*` 语义类和 `data-card-size`，不能再用固定 `grid-area`、临时局部左右列、固定空白或强行二列 / 三列来拼卡片。
- 暂时不把文档移入 `docs/`，因为根目录文档更容易被 Owner 和代理第一时间发现；等文档数量继续增长后再考虑整理目录。

### 2. 代理执行上下文

这些文件告诉 Codex / OpenClaw 怎么工作。

- `AGENTS.md`：本仓库的通用代理规则。
- `openclaw/maxnow-dashboard/SKILL.md`：OpenClaw 更新 dashboard / ai-news 数据时的执行规则。
- `openclaw/last-30/SKILL.md`：OpenClaw 更新 Last-30 滚动记忆时的执行规则。
- `scripts/check.py`：本地一致性校验脚本。
- `scripts/update_data.py`：统一数据更新入口；`runtime` 用于服务器定时刷新 wiki-todos、Ricky 旅行记录、生活页吃啥候选、天气、行情指数、系统状态和项目元信息，`wrap all` 重生成 wrapper，`project-status` 显式从 `ROADMAP.md` 刷新独立的 Home 项目状态数据。
- `scripts/sync_wiki_todos.py`：通过 GitHub CLI 读取 private personal-wiki 并刷新 `dash/data/wiki-todos.*`。
- `scripts/sync_system_status.py`：采集 nginx、HTTPS、git commit、磁盘、内存、11 个 Owner 可见数据源状态和关键自动化连续失败次数，只刷新 dashboard 的 `automation` / `system` 字段；Home 系统状态卡作为入口，云服务页复用同一份快照展示更完整的服务器状态。
- `scripts/sync_openclaw_usage.py`：只读服务器 `/root/.openclaw` 轨迹，生成 OpenClaw Token 用量账本和 OpenRouter 等价费用估算。
- `scripts/sync_codex_usage.py`：只读 `.codex/sessions` 中的 `token_count`、`turn_context.model` 和 `task_complete.duration_ms`，按累计快照增量和事件日期生成 Codex Token 用量与已完成任务活跃时长；同一会话树内去重分叉文件继承的历史，不导出 prompt / response 正文。
- `scripts/sync_token_usage.py`：合并 OpenClaw / Codex Windows / macOS / server 源账本，生成 Token 页面优先读取的统一总账。
- `scripts/report_codex_usage.ps1`：Owner Windows 本机的 Codex 用量上报脚本；只刷新并提交本机 `codex-usage.*` 源账本，推送后不再 SSH 触发服务器合并。
- `scripts/report_codex_usage_hidden.vbs`：Task Scheduler 使用的无窗口 launcher，通过 `wscript.exe` 以 window style 0 启动 PowerShell 上报脚本，避免瞬时命令行窗口。
- `scripts/install_local_codex_usage_task.ps1`：注册 Windows Task Scheduler 任务 `MaxNow-Local-Codex-Usage-Report`，默认每小时 `:02` 静默运行。
- `scripts/report_codex_usage.sh`：Owner macOS 本机的 Codex 用量上报脚本；只刷新并提交本机 `codex-macos-usage.*` 源账本，推送后不再 SSH 触发服务器合并。
- `scripts/install_local_codex_usage_launchd.sh`：注册 macOS launchd 任务 `cn.maxnow.local-codex-usage-report`，默认每小时 `:00` 运行。
- `scripts/refresh_token_sources_on_server.sh`：root 每小时 `:05` 刷新 OpenClaw / Codex server 源账本，不提前拉取本机账本。
- `scripts/refresh_token_usage_on_server.sh`：服务器侧 Token 总账刷新脚本；拉取最新本机源账本，保护 `openclaw-usage.*` / `codex-server-usage.*` 运行态账本，并合并 `token-usage.*`。
- `scripts/sync_weather.py`：从 Open-Meteo 的中国气象局 CMA / GRAPES 模型刷新北京市海淀区天气，写入 `dash/data/dashboard.*` 的 `weather` 字段，并用当前降水量修正漏报为云的天气码。
- `scripts/sync_market_indices.py`：从腾讯公开行情接口刷新纳指100、标普500、上证指数、深证成指和创业板指，生成 Home 市场涨幅卡读取的 `dash/data/market-indices.*`。
- `SERVER_RUNBOOK.md`：服务器操作和部署排障手册，改服务器前先读。

维护方式：

- 面向代理执行，可以使用英文。
- 规则要短、明确、可执行。
- 当产品边界变化时，要同步更新这些文件。

### 3. 每日状态上下文

这些文件驱动当前网页。

- `dash/data/dashboard.json`：人工个人状态、日常记录、系统状态、历史 Token 字段、Home 天气卡和 Home 时间卡片的手动特殊日期列表。
- `dash/data/dashboard.js`：从 `dashboard.json` 生成的浏览器 wrapper。
- `dash/data/ai-news.json`：首页展示用的外部 AI 输入，取免费 AI 外部信号中的 0-3 条高相关内容。
- `dash/data/ai-news.js`：从 `ai-news.json` 生成的浏览器 wrapper。
- `dash/data/wiki-todos.json`：从 private personal-wiki `wiki/tasks/todo.json` 同步而来的近期待办只读缓存。
- `dash/data/wiki-todos.js`：从 `wiki-todos.json` 生成的浏览器 wrapper。
- `dash/data/openclaw-usage.json`：OpenClaw 每日 token 用量、按模型 / 任务拆分和 OpenRouter 等价费用估算。
- `dash/data/codex-usage.json`：Windows 兼容本机 Codex 每日 token 用量、按模型 / 任务拆分；来源为本机 `.codex/sessions` 的 `token_count` 事件。
- `dash/data/codex-macos-usage.json`：macOS 本机 Codex 每日 token 用量、按模型 / 任务拆分；来源为 macOS 本机 `.codex/sessions` 的 `token_count` 事件，分叉 session 的继承历史不重复计入。
- `dash/data/codex-server-usage.json`：服务器 Codex 每日 token 用量、按模型 / 任务拆分；来源为服务器 `/root/.codex/sessions` 的 `token_count` 事件。
- `dash/data/token-usage.json`：OpenClaw / Codex 合并后的统一 Token 总账，Token 页面优先读取它。
- `dash/data/*-usage.js`：从对应 usage JSON 生成的浏览器 wrapper。
- `dash/data/market-indices.json`：Home 市场涨幅卡片的只读指数缓存，由 `scripts/sync_market_indices.py` 从腾讯公开行情接口生成，只保存点位、涨跌、涨幅、更新时间和压缩后的日内走势点。
- `dash/data/market-indices.js`：从 `market-indices.json` 生成的浏览器 wrapper。
- `dash/data/project-meta.json`：MaxNow 当前版本、部署说明和版本更新摘要，由 `scripts/sync_project_meta.py` 从 `VERSION`、Git 状态和 `UPDATE_LOG.md` 生成。
- `dash/data/project-meta.js`：从 `project-meta.json` 生成的浏览器 wrapper。
- `dash/data/project-status.json`：从 `ROADMAP.md` 显式生成的 Home 项目主线和待推进事项，附带来源时间、生成时间、过期阈值和内容指纹。
- `dash/data/project-status.js`：从 `project-status.json` 生成的浏览器 wrapper。
- `dash/data/dounai_checkin.json`：豆奶每日签到记录、账号余量快照、账号日均可用历史和直接流量使用记录，由 OpenClaw / root 侧豆奶自动化更新；Home 只读展示今日流量、今日豆丁、今日账号有效期延长时长、累计签到天数、累计流量和累计账号有效期延长时长，并作为豆奶详情页入口。豆奶详情页展示近 30 天实际使用流量、账号日均可用、签到流量和签到时长折线图，以及剩余流量、有效期和每日可用预算。2026-07-05 已接入 `dounai.pro/user/trafficlog` 只读抓取：`traffic_usage.daily` 保存豆奶页面直接展示的近 7 天真实使用量，`traffic_usage_history` 会随同步累积最多 60 天；00:05 traffic-only closeout 会排除当天，只保留已完成日期用于近 30 天实际使用图。
- `dash/data/ricky.json`：同行记页面的只读数据源，由 `scripts/sync_ricky_travel.py` 从 personal-wiki `wiki/relationships/ricky-travel.json` 生成，维护“我和 Ricky”的世界地图点位、地点、旅行记录、统计和可选照片 / 来源链接。
- `dash/data/ricky.js`：从 `ricky.json` 生成的浏览器 wrapper。
- `dash/data/life-foods.json`：生活页“吃啥”随机选择器的只读候选数据，由 `scripts/sync_life_foods.py` 从 personal-wiki `wiki/life/food-picker.md` 生成。
- `dash/data/life-foods.js`：从 `life-foods.json` 生成的浏览器 wrapper。
- `dash/data/ballet.json`：芭蕾页面与 Home 摘要读取的脱敏 read model，保存同步状态、累计 / 月度 / 年度聚合、实际上课记录、预约 / 候补与取消截止、本周训练摘要、课程卡预测和周课表。课表通常为本周 7 天；周日 14:30 只读同步拿到下周课程后变为本周日 + 下周 7 天。桌面课表卡占满内容区，以小时为标尺并按实际起止分钟定位课程，时间轴同时显示首个与最后一个结束整点；每天固定分为大教室 / 小教室两列，同教室重叠课程只在对应教室列内继续分轨；整周无课程实际占用的连续小时压缩成单个时间范围列，全部小时与 7 天课程无内部滚动直接平铺。不保存 Cookie、会员卡号、会员标识、源记录 ID 或原始响应。
- `dash/data/ballet-session.json`：Cloud 页“芭蕾 Session 实验”折叠详情的本地 / Git 安全 fallback；生产同 schema 状态由专用非 root 用户写入 `/var/lib/maxnow-ballet-session-status/public`，经已有登录校验的 nginx alias 提供。它只保存已确认时长、时间、间隔、样本计数和安全状态；不改变 `ballet.json` 的课程新鲜度，也不保存 Session、指纹、unit、日志路径或响应摘要。
- `dash/data/ballet-booking-fast.json`：芭蕾“抢课”工作区与 Cloud 自动抢课运维卡共用的安全 fallback；生产状态由周日 fast-path service 写入独立 public 目录，经登录校验和 `no-store` exact alias 提供。芭蕾页用它渲染累计已抢到、累计候补、上次执行关键路径总耗时与逐目标平均值，并同时渲染脱敏代抢目标和上次抢课结果两个独立列表；累计值分别读取 `totalBooked` / `totalWaitlisted`，不与 `ballet.json` 当前未来预约 / 候补列表数量混用。Cloud 读取启用状态、优先级、上次 / 下次执行和累计数；该数据不作为课程余位事实源。
- `dash/data/ballet.js`：从 `ballet.json` 生成的浏览器 wrapper。
- `dash/login.html` / `dash/login.js`：MaxNow 私人访问入口；只提交用户名和密码到同源 `/auth/login`，不在浏览器保存或读取会话 Cookie。
- `scripts/maxnow_auth_service.py`：服务器本机认证服务；读取 htpasswd、签发和校验 7 天 HttpOnly 会话，不读取 Dashboard 数据。
- `server/maxnow-*`：systemd、nginx 限速、认证 location 和站点配置的仓库内可复现模板。
- `scripts/sync_wiki_todos.py`：通过本地或服务器 `gh` 登录态刷新 `dash/data/wiki-todos.*`，避免前端暴露 GitHub token。
- `scripts/sync_ricky_travel.py`：通过本地相邻 personal-wiki checkout 或服务器 `gh` 登录态读取 `wiki/relationships/ricky-travel.json`，刷新 `dash/data/ricky.*`。
- `scripts/sync_life_foods.py`：通过本地相邻 personal-wiki checkout 或服务器 `gh` 登录态读取 `wiki/life/food-picker.md`，刷新 `dash/data/life-foods.*`。
- `scripts/sync_ballet.py`：只访问已确认的闻道 GET 页面，从服务器私有 canonical ledger 增量去重并刷新脱敏 `dash/data/ballet.*`；同时读取预约、候补、上课记录、课程卡概览和严格日期路径的周课表，解析相对取消规则并计算绝对截止时间，不调用预约、取消、候补或转课写接口。
- `scripts/query_ballet_live.py` / `scripts/run_ballet_live_query.sh`：面向对话请求的实时只读入口。通过临时 systemd unit 解密服务器 host-bound PHPSESSID，按课表、当前预约、上课记录或课程卡最小范围直接读取闻道并输出脱敏 JSON；不读取或写入 Dashboard 缓存与服务器私有账本。
- `scripts/book_ballet.py` / `scripts/run_ballet_booking.sh`：Owner 当前请求中明确指定课程后的实时预约入口。只接受日期、起止时间、课程名、老师和教室精确匹配，统一预检后按输入顺序逐节提交并实时复核；不使用 Dashboard 缓存，不输出源 ID，不盲目重试未知结果。
- `scripts/book_ballet_fast.py` / `server/maxnow-ballet-booking-fast.*`：周日 14:20 无人值守自动抢课关键路径。14:19:35 启动并预热，先按课程 `芭蕾 L1 > 软开`、再按同课程日期 `周六 > 周日 > 周五 > 其他日期` 排序；三个日期课表最多 3 路并发且同日共享，课程卡与规则最多 2 路并发预检并设 8 秒有效期，HTTPS 保持最多 3 条 keep-alive 连接，真实 mutation 始终严格串行，最后预约详情最多 3 路并发只读核验。目标按日期、课型 / 等级、起止时间和教室唯一匹配，老师不参与匹配或 occurrence 幂等键；目标课可预约则预约、仅可排队则候补，已预约 / 已排队不重复提交；可确认未产生 mutation 的临时失败最多重试 3 次，mutation 结果未知不重复提交但不阻止后续课程，全部结束后统一核验 booked / waitlist；私有幂等状态和公开脱敏状态分目录保存。
- `openclaw/maxnow-ballet-live/SKILL.md`：芭蕾数据询问、显式预约和自动抢课状态的强制路由。课程数据仍要求 `source=wenda-live`、`live=true` 和当前 `fetchedAt`，失败时禁止回退缓存；自动抢课状态只允许回答计划和结果，不得替代实时课程余位。
- `scripts/sync_weather.py`：抓取北京市海淀区天气、温度、当前降水、高低温和天气图标类型，只刷新 dashboard 的 `weather` 字段。
- `scripts/sync_market_indices.py`：抓取国内外指数行情和 1 日 5 分钟走势，刷新 `dash/data/market-indices.*`；接口失败时保留旧缓存并标记 `stale`。
- `scripts/sync_ai_last30.py`：抓取免费公开 AI 信号源，按正式发布 / 客户案例等事件类型排序，生成中文事实标题与摘要，并跨“最新 / 本周 / 近 30 天”去重；采集脚本本身不调用模型，不消耗 token。

维护方式：

- OpenClaw 日常任务可以更新。
- 每次更新后必须校验 JSON，并重新生成对应 `.js` wrapper。
- 这里保存“今天要看的状态”，不要塞长期产品讨论。
- Home 顶部天气卡读取 `dash/data/dashboard.json.weather`，展示在小日历左侧；前端不直接请求外部天气接口。
- private personal-wiki 待办不能由前端直接读取；需要先运行 `python scripts/update_data.py runtime` 或 `python scripts/sync_wiki_todos.py` 生成 MaxNow 本地缓存。
- 服务器已安装并授权 GitHub CLI，账号 `V-ioi-V` 可读取 private personal-wiki；服务器上已验证 `python3 scripts/sync_wiki_todos.py` 能成功生成待办缓存。
- 系统状态可以由 `python scripts/sync_system_status.py` 自动采集，但它只能更新 `automation` 和 `system`，不能覆盖今日判断、当前主线、待推进事项或日常记录。
- 天气可以由 `python scripts/update_data.py weather` 或服务器 `runtime` 定时刷新，数据源是 Open-Meteo 的 CMA / GRAPES 模型。
- 市场涨幅可以由 `python scripts/update_data.py market-indices` 或服务器 `runtime` 定时刷新，数据源是腾讯公开行情接口；前端只读 `dash/data/market-indices.json`，不直接请求第三方行情接口。
- OpenClaw 用量可以由 `python scripts/update_data.py openclaw-usage` 刷新。脚本读取 OpenClaw trajectory 中的 `usage.input`、`usage.output`、`usage.cacheRead` 和 `usage.total`，按 Asia/Shanghai 日期聚合；费用字段使用 OpenRouter 当前或缓存价格估算，不能当作真实供应商扣费。服务器 root crontab 的 `MAXNOW-TOKEN-SOURCE-REFRESH` 每小时 `:05` 与 Codex server 一起刷新来源账本，日志写入 `logs/token-source-refresh.log`。
- MaxNow 版本号由根目录 `VERSION` 手动维护，格式为 `x.x.x.xx`；`python scripts/update_data.py project-meta` 会刷新 Home 的版本与版本更新模块。任何已完成的 Owner 可见或运维相关改动都要升版本：小 UI / 文案 / 布局调整、新页面能力、新数据源和新自动化默认升最后两位；重要功能模块稳定落地升 patch；大版本阶段切换升 minor / major。
- Windows / macOS / server Codex 都从 `.codex/sessions` 读取 token、模型和 `task_complete.duration_ms`；活跃时长只统计已完成任务，排除用户停留、休眠和轮次之间的空闲时间，不导出对话正文。
- Token 自动化使用同一固定小时周期：macOS `:00`、Windows `:02`、root server sources `:05`、ubuntu ledger merge `:10`。本机任务继续使用专用 main clone；Git HTTP 低速边界和 SSH keepalive 防止 `git pull` / `push` 无限挂起，Windows 任务最长运行 10 分钟。macOS 上报若因并发 push 留下本地生成提交，只在提交标题和文件边界都确认属于该任务时自动回到最新 `origin/main`、重新生成并有限重试；若上次运行只留下未提交的 `codex-macos-usage.*` 生成文件，也会在确认没有越界改动后恢复并重新生成。人工提交或其他文件改动一律阻断自动 reset / restore。
- 服务器 root crontab 使用 `MAXNOW-TOKEN-SOURCE-REFRESH` 和 `/tmp/maxnow-token-source-refresh.lock`，日志写入 `logs/token-source-refresh.log`；ubuntu crontab 使用 `MAXNOW-TOKEN-USAGE-REFRESH` 和 `/tmp/maxnow-token-usage-refresh.lock`，每小时 `:10` 拉取并合并总账。总账拉取对并发 Git 引用更新等瞬时失败最多尝试 3 次，持续失败仍会退出并保留旧总账。
- `dash/data/token-usage.json` 是 Token 页统一入口；OpenClaw、Codex Windows / macOS、Codex server 和后续其他来源都应合入这个总账。Token 页 `1d` 按当前浏览器本地日期 00:00 起算，`7d` / `30d` 包括今天在内的最近 7 / 30 个自然日；来源费用面板和模型占比、调用消耗同层并列展示，并且来源 token、费用和 runs 跟随当前范围更新。页头展示各来源账本的最后更新时间。
- 2026-07-10 起，Dash Home 首批读取 dashboard / project-status / last-30 / wiki-todos / dounai_checkin / market-indices / project-meta 小数据并渲染；Token 总账、Ricky、生活页数据和 Leaflet 地图资源按当前视图需要再加载。`.js` wrapper 仍由脚本生成并校验，但主要作为数据一致性和静态兜底资产，不要重新放回首屏同步脚本列表。
- 2026-07-08 起，Home 状态条下方主内容采用统一 `home-board` 两列版式：左列 `home-lane-primary` 放 Token 热力格、Personal Wiki、待推进、AI 前沿和版本更新，版本更新固定排在 AI 前沿下方；右列 `home-side-stack` 视觉上是 widget 网格，按优先级放市场涨幅、今日 Todo、近期用量、豆奶和系统状态。两列外壳负责大块对齐，左列负责吸收内容型长模块，右列 widget 卡型负责半宽 / 满宽短状态入口，避免左列空着而右列继续下排，也避免所有卡片被二列布局拉成大卡。后续新增 Home 卡片必须先选 lane，再选 `wide-short` / `wide-tall` / `mid-short` / `mid-tall` / `widget-compact` / `widget-wide` 卡型。
- 2026-07-10 线上已部署提交 `538dc40`，AI 前沿功能版本为 `1.0.3.00`、Dash 缓存为 `styles.css?v=128` / `app.js?v=110`；部署前完整备份并暂存服务器运行数据，只恢复不与 AI 前沿冲突的 dashboard、豆奶、行情、同行记和 Wiki Todo，随后重新生成 `ai-news.*`、`last-30.*` 与 `project-meta.*`。
- 豆奶签到展示只读取 `dash/data/dounai_checkin.json` 中的流量、豆丁、时长、累计签到天数、账号余量快照、账号日均可用历史、直接流量使用记录和近 30 天 records；豆丁只进入 Home 摘要，不进入豆奶详情页展示口径，不要在 MaxNow 前端增加签到写入、账号操作或 cron 管理。真实流量消耗优先使用 `traffic_usage_history`，不要再用账号余量快照差分作为主口径；余量差分只可作为缺数据时的估算说明。
- 同行记页面只读取 `dash/data/ricky.json`，不在前端编辑、不回写 personal-wiki、不依赖外部在线地图服务；事实来源归 personal-wiki 的 `wiki/relationships/ricky-travel.json`。
- 生活页“吃啥”只读取 `dash/data/life-foods.json`；前端允许本次会话内临时勾选 / 取消勾选和随机，但不回写 personal-wiki，候选长期来源归 `wiki/life/food-picker.md`。
- 服务器上的豆奶签到由 root/OpenClaw 侧脚本维护；`/root/.openclaw/gen_checkin_data.py` 会把生成结果同时写入 `/root/MaxNow/dash/data/dounai_checkin.json` 和线上部署目录 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。线上页面读取后者。2026-06-21 已扩展该脚本，让它用现有豆奶登录态只读抓取账号有效期和余量快照，并按日期维护 `account_history`；2026-07-21 起，余量优先从现有订阅的 `subscription-userinfo` header 读取字节级 `total / upload / download` 后计算，数据只保存精确字节、换算值和 `byte` 精度标记，绝不保存订阅地址或令牌，响应头不可用时才降级到面板两位 TB / GB 标签。2026-07-26 起，日均预算改用快照时刻到有效期的 `remaining_days_exact` 精确剩余时长计算，`days_remaining` 只作整天摘要，避免签到延长有效期后整数分母未变化造成预算曲线假下降。2026-07-05 已继续扩展脚本，读取 `/user/trafficlog` 的近 7 天真实使用量并合并到 `traffic_usage_history`，同时读取 `?ajax=1` 的近 12 小时节点活跃分布；同日新增 root cron `MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT`，每天 00:05 执行 `gen_checkin_data.py --traffic-only --exclude-today`，专门更新昨天及更早的真实使用量。2026-07-06 已确认豆奶脚本依赖 root 的 Playwright `chromium_headless_shell-1208`；清理服务器浏览器缓存后需要运行 `python3 -m playwright install chromium` 并做 headless launch smoke test，补签应优先用不发通知的 `/root/.openclaw/daily_checkin.sh`。

### 4. AI 前沿简报与滚动记忆

这是 Last-30 当前定位：保存最新、本周和近 30 天的 AI 前沿正式发布。它不是 MaxNow 内部项目日志、英文 RSS 搬运或关键词观察报告；只保留模型、API、Agent、开发者工具、成本和重要研究的实质变化。

已经新增：

- `dash/data/last-30.json`
- `dash/data/last-30.js`
- `openclaw/last-30/SKILL.md`

它负责保存：

- 最新发布：最近 3 天最重要的 1-3 条正式发布。
- 本周前沿：补充最新发布未覆盖的本周高信号事项。
- 近 30 天关键进展：展示具体里程碑，不展示自动关键词分类。
- 中文事实标题和具体能力 / 开放范围摘要；官方英文标题保存在 `originalTitle` 便于追溯。
- 需要继续观察或 Owner 确认的信号。

维护方式：

- 免费版由 `scripts/sync_ai_last30.py` 抓取官方 RSS / 博客、GitHub releases、Hacker News、GDELT、arXiv 等免费公开源，写入 `dash/data/ai-news.*` 和 `dash/data/last-30.*`。
- 服务器已通过 `ubuntu` 用户 crontab 接入 `MAXNOW-AI-LAST30-SYNC`：每天服务器本地时间 00:00 运行 `python3 scripts/update_data.py ai-last30`，日志写入 `/var/www/maxnow-dashboard/logs/ai-last30.log`。
- 脚本先做本地抓取、事件类型与优先级判断、主题去重和中文事实摘要，不调用模型；采集本身不消耗 token。
- 如果让 OpenClaw 二次总结，只应喂少量候选，避免把新闻全文直接交给模型。
- X / Twitter 官方 API 暂不接入，除非 Owner 明确批准付费 API 和博主白名单。
- 每条记录尽量带来源、日期、官方链接和 `originalTitle`；前端只显示来源与日期，不显示内部置信度。
- “最新 / 本周”优先模型发布、API / Agent 能力、价格与开放范围；客户案例、合作、泛采用、纯 SDK 版本号和 updated packages 不进入主列表。

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

### 6. 芭蕾学习模块上下文

Owner 已开始在 MaxNow 落地芭蕾模块。产品定义从原来的“远端自动约课”扩展为“学习记录 + 课程计划 + 受控约课”：

- 闻道微信公众号 H5 提供课程表、当前预约、候补 / 余位、上课记录和会员课次等机器事实；已验证课程、预约和上课记录可以分别读取。
- personal-wiki 负责当前级别、阶段目标、课堂笔记、老师纠正、动作标签、练习记录和 Owner 人工判断；MaxNow 只做单向同步与只读展示。
- 芭蕾等级机制的唯一人类可读协议放在独立的 `BALLET_GROWTH_SCORING.md`，课程指南提供课程路径与成人建议课次。顶部右侧固定使用两张独立面板，成长等级在上、课程等级在下。蓝色“课程等级”显示当前级别已完成课次 / 目标课次和距离下一课程级别的剩余课次，达到当前采用目标后自动升级且不因后续训练频率下降而回退；紫色“成长等级”只按全部实际上课数量推进，规则内部与页面都使用 `Lv.1–Lv.10`。页面标题只显示当前 `Lv.N`，下方展示本级进度与距离下一等级的剩余课次，不在标题重复下一等级，也不铺开全部十级；Lv.10 在累计 200 节时达成。十张透明 PNG 小天鹅成长状态依次模拟灰色绒毛雏鹅、灰白换羽和白色成年天鹅，宠物固定在成长等级面板右上角，与进度条区域分离；前端先把小天鹅舞台与 `Lv.N` 按中心线排列，再按每张素材的透明像素可见中心做百分比光学位移，使可见主体中心与文字中心一致。任何升班课次 / 规律判定 / 成长等级门槛变更，都必须在同一分支同步修改 `dash/app.js`、`BALLET_GROWTH_SCORING.md` 和 `UPDATE_LOG.md`；`scripts/check.py` 对代码常量、成长素材与独立文档表格做一致性校验。
- 课表课程色只表达课型，Owner 预约状态通过同色三档实心底表达：普通保持浅色、排队为中深色、已预约与已上完为明显深色，不能依赖小徽标才能分辨；状态徽标仍使用独立语义色。
- 课表课程卡始终保留课程名后的独立老师行，包括中等桌面、60 分钟紧凑卡和重叠窄卡；起止时间也必须完整显示，不能被状态徽标挤成省略号。宽卡让完整时间与状态同排，中等桌面紧凑卡空间不足时把状态放到时间下一行；人数 / 排队仍可优先压缩。这个显示规则与自动抢课是否限制老师相互独立。
- 芭蕾数据由服务器隔离采集器生成脱敏 read model，前端不直连闻道、不回写 personal-wiki，也不因打开页面而触发请求或预约。
- 独立 `secondary-view` 页面名称“芭蕾”、副标题“课程与进度”，入口位于 Token 与云服务之间；完整顺序为首页 → 豆奶 → Token → 芭蕾 → 云服务 → 生活 → 同行记。页面使用粉玫瑰 + 白卡语义但不另做宣传型视觉；导航图标用舞鞋而非心形。
- 只读 MVP 的页面顺序是：顶部概览（本周训练 + 课程卡 + 成长 / 课程等级）→ 课程计划（左“课程预约” + 右“抢课”）→ 本周课程表 → 训练记录（统计 + 历史）。抢课区顶部以三个等宽摘要卡显示累计已抢到、累计候补和上次关键路径总耗时，前两项分别读取自动抢课状态的 `totalBooked` / `totalWaitlisted`，耗时副说明保留目标数与逐目标平均值；下面用“代抢”和“上次抢课结果”两个独立列表区同时呈现目标与结果，宽时左右并列、窄时自然堆叠，课程名称共用固定左边缘。课程表固定倒数第二，训练记录固定最后。本周训练上方为已完成、已预约、候补和训练时长 2 × 2 指标；训练时长只按已完成分钟统计，副说明显示已完成节数，已预约与候补不计入。底部课程类型仍按已完成与已预约汇总，完成率仍按已完成 /（已完成 + 已预约）计算。训练记录同时展示课型、展示级别和老师三组分布；底层无级别仍保留事实值，页面以软开、肌肉素质、技术技巧等真实课型替代“无级别”。训练图表固定为“本月日历热力 / 今年按月折线 / 全部按有记录年份折线”；今年只显示 1 月至当前月，未来月份不绘制，所选范围有记录就展示、无记录才进入空状态。桌面周课表使用日期横排、时间纵排的留白周日历，每天固定分为大教室 / 小教室两列，首尾整点文字与网格线共坐标。课程类型与芭蕾级别决定卡片色相：L1 / L1.5 绿色、L2 蓝色、L3 杏桃色、L4 紫色、L5 玫瑰色，软开灰米、肌肉素质浅黄、技巧课柔粉；普通、本人排队中、已预约 / 已上完分别使用同色浅、中、深三档实心底。课程内状态徽标独立使用绿 / 橙棕 / 深灰紫 / 红区分可约 / 可排队 / 已满 / 已取消，并用粉玫瑰 / 橙 / 绿区分已预约 / 排队中 / 已上完；浅色外描边负责在相近课程底色上保持边界。过去日期把课程卡和状态徽标一起降饱和、降透明度，保持色相但明确弱于今天和未来课程。课程卡把源站报名数 / 容量和明确 `Wait` 数字放入独立人数行，老师另起弱信息行，时间 / 状态固定在底部；空 `Wait` 不显示为 `0`，也不得用溢出人数推断队列。本人候补状态从预约快照匹配序号并显示 `排队中 N`，不复用全班排队数；宽桌面恢复 60 分钟课程的老师名，仅中等桌面和重叠窄卡允许隐藏。`1200px` 以下切换为逐日、再按教室分组的列表。
- 桌面周课表的日期边界和同日教室边界都使用 `1px` 细线，日期线以稍深暖灰粉、教室线以接近背景的浅灰粉形成自然层级；移动端继续由逐日卡片承担日期分组。
- 芭蕾内容不并入“生活 / 吃啥”。Home 只显示下一节课、本周进度和状态；芭蕾页承载课程与学习业务；Cloud 承载采集、自动抢课运行态和 Session 实验详情。芭蕾更新时间与薄连接状态收进全局顶部栏标题旁，不在内容区独占一行；课程计划保留自动抢课目标与逐课业务结果。
- 服务器私有 canonical ledger 是上课事实唯一机器真相：首次全量回填，日常重扫最近 60 个逻辑日并幂等 upsert，每月 1 日 00:47 全量校验；rolling 任务每天 `09:00 / 12:00 / 15:00 / 18:00 / 22:00` 运行，并在周日 14:30 额外检查抢课后发布的下周课表。同步失败保留上次成功账本与聚合，只更新独立 `sync-state.json`；预约、课程卡与课表分别保存脱敏快照。
- 月、年和全局的节数 / 分钟以及课程分类在同步时预聚合；前端不重复遍历全历史。人类可读文档若需要，只从账本单向生成，不成为第二份可编辑事实源。
- 固定 25 分钟的旧会话阶段已于 2026-07-26 23:28 返回登录失效并停止，最后认证为 23:03、已确认有效 3 小时 56 分 06 秒。Owner 于 2026-07-27 重新打开闻道并退出微信后，本机提取到不同的新会话；v6 自 00:26:55 起按每 20 分钟独立计时，2026-07-28 20:23 安全交接到同凭据代次的 v7 无限期阶段。v7 不设计划结束时间，但身份失效或连续 3 次未知 / 网络异常仍会停止；旧三阶段与当前凭据代次不能合并寿命，也不能据此证明精确空闲寿命或滑动续期。unit、原始日志、凭据挂载和停止方式只在 `SERVER_RUNBOOK.md` 维护。
- Cloud 页展示 `ballet-session.*` 的脱敏实验卡：持续时间只计算到最后一个 `authenticated` 样本，页面每 5 分钟读取静态状态，服务器本地发布器不访问闻道。文案使用“自动检查”，不能将正常样本解释成已证明 Session 自动续期。
- 状态发布器以专用无登录账号运行；已停止实验的日志 inode 使用 root-owned 只读硬链接或快照保存，当前 v7 活动日志由独立 root oneshot 每 5 分钟原子复制为只读脱敏快照，再由非 root 发布器生成页面状态。两项本地任务都不访问闻道，`/var/lib/private` 继续保持 `0700`。
- `dash/data/ballet.*` 只能保存脱敏前端读模型与预聚合统计；同步状态同时保存最近尝试、最近成功、数据变更时间、逻辑日期、抓取窗口、连续失败和安全错误码。课程卡只允许输出名称、有效期、总 / 剩余 / 已用课次和由该卡自身有效期 / 使用量推导的计划与实际节奏；不同卡不能共享消耗样本，开卡未满 28 天时实际节奏字段保持空值。`PHPSESSID`、Cookie、OAuth code、openid、unionid、memberId、手机号、会员卡号、源记录 ID、原始响应正文和真实执行参数必须只留在服务器隔离运行态，不能进入前端、仓库、日志或聊天。
- 生产凭据已于 2026-07-27 使用新会话重新密封为 host-bound systemd 加密凭据，通过 `LoadCredentialEncrypted` 注入。enable gate 已保留；rolling timer 为每天 `09:00 / 12:00 / 15:00 / 18:00 / 22:00` + 周日 14:30，月度 full 保持每月 1 日 00:47。2026-08-01 10:40 部署新日程时，systemd 因 `Persistent=true` 自动补跑一次已错过的 09:00 rolling，只读同步成功且未执行预约类动作；后续下一次为 12:00。身份失效时采集器保留旧缓存、记录脱敏错误并停止重试，直到检测到非敏感凭据版本变化。
- 2026-07-28 已部署 `maxnow-ballet-live` Skill 与实时查询 CLI：以后 Owner 在对话中询问芭蕾课程数据时，必须 SSH 到 MaxNow 服务器并用当前 PHPSESSID 查询闻道，不再读取前端缓存。服务器 OpenClaw Skill 入口已指向仓库版本；查询只允许既有 GET allowlist，输出无源记录 ID、会员标识、响应正文或凭据痕迹，实时失败即明确失败。Owner 泛问“有什么课程 / 有什么可以约的课”时默认展示全部课型，只有明确要求“只看 / 仅看 / 只想看”某类课程时才筛选；直约课按日期分组并固定展示开始–结束时间、课程名、老师、教室和余位。最终当天课表验收返回 7 节课，且 Dashboard 缓存、私有账本和临时凭据目录均未留下改动。
- 2026-07-28 芭蕾 Later 包含 Apple 日历订阅和分享图：前者提供私有、可撤销的 ICS / `webcal://` 链接，Owner 首次在 Apple 设备确认订阅后自动同步正式预约与候补；后者从现有脱敏 read model 选择下一节、本周训练和阶段统计等关键信息，在浏览器本地生成可预览、可下载的图片，不上传服务器，具体比例、模板和默认字段在实现前确认。受控多课预约与自动抢课均已落地，见 Done。
- 2026-07-28 已完成对话式显式预约：单课和多课先统一实时预检，再按输入顺序逐节提交，每节最多一次 `do_addbook` 并即时读取预约记录验证。首次真实单课执行与独立复核均成功。
- 2026-08-02 Owner 将无人值守自动抢课的老师条件改为“不限老师”，随后确认先按课程 `芭蕾 L1 > 软开`、再按同课程日期 `周六 > 周日 > 周五 > 其他日期` 排序；当前 mutation 顺序是周五 L1、周二 L1、周五软开、周二软开、周四软开，均为原晚间时段和大教室。生产 fast path 仍于周日 14:19:35 启动、14:20:00 提交；目标日期课表最多 3 路并发且同日共享，卡与规则最多 2 路并发预检并设 8 秒有效期，HTTPS 最多 3 条 keep-alive 连接，真实 mutation 严格串行，最终详情最多 3 路并发只读核验。匹配与 occurrence 幂等键只使用日期、课型 / 等级、起止时间和教室；老师临时变化不会阻止预约或候补，其他字段仍必须唯一命中。每节独立执行，可预约则预约、可排队则候补；可确认安全的临时失败最多重试 3 次。单节失败或 mutation 结果未知继续后续课程，未知 mutation 本身不重试，最后统一核验预约 / 候补与候补位次。身份失效、配置错误或页面结构变化仍全局停止；不取消、转课或支付。
- 2026-08-02 训练趋势图统一改为内容驱动的紧凑卡：本月热力图桌面最大 `840px` 并左对齐；今年与全部折线图按实际时间点数量动态收窄，同样以 `840px` 为上限，数据越少宽度越短；手机端继续占满可用宽度。热力格高度与间距收紧，未来尚未同步的日期只保留低对比浅底虚线格，不再用密集斜纹和重复破折号占据视觉焦点。
- 2026-08-02 训练记录详情改为桌面“趋势图 + 紧凑历史”并排：左侧图表单独决定整行高度，右侧历史用脱离网格行高计算的绝对铺满层保持同高，主页面只看最近 5 节，完整当前范围记录进入右侧独立滚动抽屉。历史跟随“本月 / 今年 / 全部”切换并显示范围总数；`1100px` 以下上下排列，手机主页面只看最近 3 节，记录再多也不再把训练面板持续拉长。
- 2026-08-02 抢课区的“代抢 / 上次抢课结果”明确为两个同时展示的 Tab 面板：“代抢”是左侧固定标题而非切换按钮，每块外框独立包住标题和列表；宽时等分同高并排，窄时上下排列，继续不隐藏任何一侧。
- 2026-08-01 Owner 已把“动态调整自动抢课方式”加入正式待办：目标是让稳定执行引擎与可变课程配置分离，Owner 可在 MaxNow 中增删目标、调整优先级、逐课设置候补、配置单周覆盖或暂停，而不再每次请 Codex 修改脚本。推荐由服务器版本化运行配置作为唯一可编辑来源，前端通过独立低权限的最小配置接口读写；接口不能访问闻道凭据、网络或预约执行能力。周日任务在 14:19:35 前冻结配置快照，配置管理不能进入 14:20 关键路径；详细任务与验收边界以 `ROADMAP.md` Next 为准，当前功能尚未实现。

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

- 2026-07-25 已完成 OpenClaw 与服务器入口加固：腾讯云仅公开 80/443，SSH 仅允许 Owner 当前公网 IPv4 `/32`；Gateway 只监听 loopback，关闭不安全认证和设备认证绕过，增加认证限速，关闭浏览器私网 SSRF 放行，并将非内置插件收敛到 `memory-tencentdb` / `openclaw-weixin` allowlist。配置与会话文件为 `0600`、目录为 `0700`，Gateway 使用 `UMask=0077`；腾讯文档脚本已从 shell 字符串拼接改为参数数组执行。Dash 未登录数据请求仍为 `401`，噗噗和微信通道复验正常。后续如需 Control UI，只通过 Owner 白名单网络上的 SSH 隧道访问，不恢复公网 12123/16980/3000。
- 2026-07-26 已完成并部署“芭蕾学习模块 + 受控约课”的只读层；2026-07-27 进一步补齐完整“所有预约”、候补序号、真实取消截止、独立课程卡、本周训练摘要和到期前用完节奏判断，并把分散数字卡、分类与趋势合并为“本月 / 今年 / 全部 × 节数 / 时间”的整体统计面板。机器事实使用首次全量 / 60 日滚动 upsert / 每月全量校验的本地账本；Owner 明确补录且闻道不存在的实际上课记录使用 `manual` 稳定键，参与统计且不受闻道 full-sync tombstone。目标入口是微信公众号内 H5 而非小程序，通过微信 `snsapi_base` OAuth 建立 `PHPSESSID` 网站会话。
- 2026-07-26 19:07 开始第一阶段服务器持续活动实验；19:41 从 10 分钟安全交接到 20 分钟，23:03 再按 Owner 要求交接到 25 分钟。v5 首条即时验证为 HTTP 200 / authenticated 后才停止 v4；23:28 首个标准 25 分钟样本返回 HTTP 307 / expired，探针写入 `stopped_identity_expired` 并以退出码 2 停止，服务凭据目录已消失。三阶段样本为 4 / 11 / 2，共 17 个；最后成功认证仍是 23:03，已确认有效 14,166 秒，未观察到 Session 变化、`Set-Cookie` 或网络重试。原计划截止 2026-08-25 19:07:15 已被提前终止；不同阶段 HMAC 只能各自纵向比较。2026-07-26 21:23 密封的生产加密副本属于同一代、现已失效的凭据，值未输出或下载，生产 timer / enable gate 仍关闭。
- 2026-07-27 00:26:55 启动独立 v6 新会话实验，固定每 20 分钟；首条只读课程列表样本于 00:26:56 返回 HTTP 200 / authenticated、`attempts=1`、无 `Set-Cookie`、无会话变化。2026-07-28 20:23:14 在同一凭据代次内安全交接到 v7：新单元先以 `duration_seconds=null` 启动并于 20:23:17 完成首轮 HTTP 200 / authenticated 验证，状态发布确认 `scheduledEndAt=null` 后才停止 v6。v7 不设时间截止，但仍是 transient unit，服务器重启后不会自动恢复。凭据仅以 root `0600` 的 host-bound 加密文件保存在服务器，没有输出 Cookie 明文。2026-07-27 12:01 的首次真实同步额外访问过预约 / 上课记录 GET，因此此实验只能表述为“持续只读活动寿命”，不能继续声称请求来源只有固定课程列表探针。
- 2026-07-27 14:23 已在不访问闻道、不读取凭据的前提下向服务器私有 ledger 补入 Owner 确认的 2026-07-25 11:30–12:30 李俊软开课；2026-07-30 20:21 补入 2026-07-30 18:45–19:45 李俊大教室软开课。第二次补录曾因 root 原子替换把 `attendance-ledger.json` 留成 `root:root 0600`，导致 2026-08-01 00:00 rolling 任务无法以 `ubuntu` 读取并报 `parse_error`。00:39 已恢复 `ubuntu:www-data 0600` 并以服务用户校验，00:40 rolling 只读同步成功；代码与运维规则现要求 root 原子写继承原属主、手工维护后固定用 `ubuntu` 复验，预检失败也要保留旧数据并在顶部明确显示“同步失败”。两条手工记录继续使用 `manual` 稳定键并在 full sync 中保留。
- 这些实验和生产同步都没有提交预约 / 候补 / 取消 / 转课，也不能证明精确静默闲置寿命。Owner 已批准启用每天 `09:00 / 12:00 / 15:00 / 18:00 / 22:00`、周日额外 14:30 rolling 和每月 1 日 00:47 full 只读 timer；周日 rolling 已与 14:20 自动抢课错开。`PHPSESSID` 必须按约课网站密码处理，不得进入 Git、前端、日志、备份、聊天、环境变量或命令参数；删除本地凭据不等于吊销闻道服务端会话。
- 2026-07-15 已补齐 JSON 读取失败与新鲜度闭环：前端区分已同步、暂无记录、请求失败、数据过期和尚未同步，并按来源保留浏览器最后成功响应；Home 数据健康覆盖 Wiki、Token、天气、市场、Last-30、版本、Roadmap、豆奶、同行记和生活。服务器状态会把 Dashboard runtime、AI Last-30、Token sources、Token ledger 连续失败 3 次升级为异常。`.js` wrapper 保留生成一致性用途，不再作为运行时失败的主要兜底。
- 2026-07-10 整体体检推动 MaxNow 从“继续增加功能”转向“可信状态工作站”。`dash.maxnow.cn` 和 `/data/` 已由自定义登录页、nginx `auth_request` 和服务器本机 Cookie 认证服务保护，Blog 保持公开；后续重点转为自动测试、无障碍状态和外部依赖安全。Home 项目状态可信度已通过独立 `project-status.*`、ROADMAP 指纹校验和过期提示完成修复；可执行条目以 `ROADMAP.md` 为准。
- Home 页面已将旧外部输入重构为单一中文 AI 前沿模块：三栏数据分别为最新发布、本周前沿和近 30 天关键进展，栏头只显示蓝色时间范围“最近 3 天 / 本周 / 近 30 天”，不再重复黑色栏目名和栏目简介；新闻卡片只展示中文事实标题、具体变化、来源和日期，英文原题仅保存在数据里追溯，页面不再出现 `confidence`、候选数量、关键词自动归类或“关注它”等套话。
- Home 右侧已接入豆奶签到只读摘要卡片，点击可进入豆奶详情 tab；详情页展示近 30 天实际使用流量、日均可用、签到流量和签到时长折线图。数据来自 `dash/data/dounai_checkin.json`，签到脚本由 9:00 cron 管理，真实流量日结由 00:05 traffic-only cron 管理。
- 2026-07-05 已接入豆奶真实流量使用抓取和 00:05 日结：登录后 `/user/trafficlog` 页面直接展示最近 7 天使用量；`--traffic-only --exclude-today` 模式会把当天从 direct daily 和 `traffic_usage_history` 中剔除，避免 00:05 的当天碎片污染近 30 天实际使用口径。`?ajax=1` 返回近 12 小时节点分布，不等同于 30 天总量。
- 2026-07-06 已修复豆奶 Playwright 运行时缺失：补齐 `/root/.cache/ms-playwright/chromium_headless_shell-1208` 后，手动跑 `/root/.openclaw/daily_checkin.sh` 补入当天签到，今日数据为 768 MB、1 豆丁、延长 2.96 小时；随后运行 `gen_checkin_data.py --traffic-only --exclude-today`，线上 `account` 和 `traffic_usage` 不再带 `stale` / `last_error`。
- 2026-07-05 已处理服务器资源占用：`lighthouse-chromium.service` 因和现有 OpenClaw Chromium 会话争用同一个 profile 而失败重启，现已停用并禁用；systemd journal 已限制到约 300M，低风险缓存已清理。后续不要直接删除 `/root/.cache/ms-playwright/chromium-1208` 或当前 Playwright 需要的 `chromium_headless_shell-*`，除非安排 OpenClaw 浏览器维护窗口并做 launch smoke test。
- 2026-06-19 已修复豆奶签到数据路径分叉：当天签到成功写入 `/root/MaxNow`，但线上部署目录仍停在 2026-06-18；现在 root 数据生成脚本会双写旧工作区和 `/var/www/maxnow-dashboard`。
- wiki-todos 服务器自动同步已落地：`ubuntu` 用户 crontab 每 10 分钟运行一次 `MAXNOW-DASHBOARD-SYNC`，通过 `python3 scripts/update_data.py runtime` 刷新 `dash/data/wiki-todos.*`、系统状态缓存并执行 `scripts/check.py`。
- Last-30 AI 外部信号服务器自动同步已落地：`ubuntu` 用户 crontab 每天 00:00 运行一次 `MAXNOW-AI-LAST30-SYNC`，通过 `python3 scripts/update_data.py ai-last30` 刷新 `dash/data/ai-news.*` 和 `dash/data/last-30.*`。
- 系统状态采集已接入 Home：页面展示 nginx、HTTPS、证书、部署 commit、最近 pull、cron、wiki-todos 同步、失败日志、资源和云服务器状态。
- Token 用量账本已建立并接入 Token 页面：`scripts/sync_openclaw_usage.py` 可在服务器读取 `/root/.openclaw` 轨迹并生成 `dash/data/openclaw-usage.*`；`scripts/sync_codex_usage.py` 可读取本机或服务器 `.codex/sessions` 的 `token_count` 事件，分别生成 Windows 兼容 `dash/data/codex-usage.*`、macOS `dash/data/codex-macos-usage.*` 和服务器 `dash/data/codex-server-usage.*`；`scripts/sync_token_usage.py` 合并为 `dash/data/token-usage.*`。本机 Codex 用量已补 Windows Task Scheduler 和 macOS launchd 上报入口，服务器 Codex 用量已补 root crontab 自动刷新。Token 页支持 1d / 7d / 30d / all、总量 / 输入 / 输出 / 缓存读 / 缓存命中率 / 费用、按范围更新的来源费用面板、模型占比、会话消耗和最近 30 天折线图。Home 原“当前主线”位置展示近 90 天 Token 活动热力格。OpenClaw 费用为 OpenRouter 等价估算，Codex 费用为 OpenAI API 等价估算。
- Dash 左侧导航顺序为首页、豆奶、Token、芭蕾、云服务、生活、同行记。云服务页只读列出服务器自动化、数据同步、站点托管和日志边界，不从前端触发服务器操作；页面不再保留顶部重复摘要卡，Host 与站点域名归入“系统与托管”模块，后续任务卡自然排列，不再插入独立“定时任务”分组标题。系统与托管模块不展示部署根目录、nginx 配置路径、采集器说明等低频实现细节。
- Dash 左侧导航已新增“同行记”tab，副标题为“我和 Ricky”。该页用 Leaflet + OpenStreetMap 真实地图和轻量统计承载两人的共同足迹，地点和旅行记录暂时只进入 marker / popup 数据，不单独铺列表；内置 SVG 地图只作为 fallback。
- Dash 左侧导航已新增“生活”tab，副标题为“吃啥”。该页当前提供“吃啥”随机选择器：默认全选、数量默认 1，可临时取消候选并从勾选项中随机选取一个或多个结果；候选从 personal-wiki `wiki/life/food-picker.md` 同步。
- 豆奶、Token、芭蕾、云服务、生活和同行记统一使用 `secondary-view` 视觉协议：轻色渐变白底、统一圆角 / 阴影 / hover 与状态 pill；芭蕾顶部栏已有页面名称，因此内容区不再重复标题卡，只保留低权重数据时间与连接状态。芭蕾顶部“本周训练 / 课程卡”在 `1501px` 以上各占内容区三分之一，右侧第三格纵向放置成长等级与课程等级两张独立面板；`1101px–1500px` 前两张各占一半，两个等级面板在下一行上下排列，`1100px` 以下全部单列。课程卡以暖象牙芭蕾票券作为唯一外壳，标题与有效卡数量也在票券内，不再保留普通白色 `panel` 外框、内层票根线或侧边半圆缺口；有效卡标签使用玫瑰金色系。票券底色与本地 `membership-ballerina.webp` 的暖象牙纸色一致，插画不用混合模式。容器达到 `330px` 后左侧完整舞者和右侧事实区使用互不重叠的物理分区，事实区从横向脚尖之后开始且不再使用遮罩补救覆盖；窄卡保留完整缩放的左侧淡背景，不允许放大裁成局部影子。所有卡名、有效期、课次、有效天数和计划结论仍由脱敏数据动态渲染，不能写死在图片中；有效进度卡首行只放标签与右上圆环，主比例和到期说明各占一整行；圆环使用更大的视觉面积，正文主比例缩小，环内当前天数和总天数固定单行横排并整体居中。成长规则语义来自 private personal-wiki 的李俊芭蕾课程指南，前端只从现有脱敏上课记录计算自动升班课次与十级成长课次，不读取 private GitHub。随后依次是课程计划、周课表和训练记录；课程表是倒数第二个模块，训练记录是最后一个模块。训练记录的课程类型、展示级别和授课老师三张分布卡共用范围与节数 / 时间口径；自动抢课运行态与 Session 详情归 Cloud。7 天周课表在 `1101px` 以上使用全宽弹性网格一次平铺全部小时列，面板内部不设置滚动；`1100px` 以下切换为自然展开的逐日列表。2026-07-11 起所有 Dash tab 卡片统一取消顶部彩色横条，语义色只保留在文字、数值、图标、状态点、pill 和轻背景中。
- 2026-07-27 起 Dash 七个主页面与登录入口共用全局微调基线：系统可变字体回退、等宽数字、轻量分层阴影、统一键盘 focus ring / 按压反馈、可识别空状态和 reduced-motion 兜底。生活页结果台收紧为桌面 `300px` / 窄屏 `240px`；后续新模块优先继承 `STYLE_CONTEXT.md` 的全局规则，不在局部另起相近视觉协议。
- Home 项目主线和待推进事项由 `python scripts/update_data.py project-status` 从 `ROADMAP.md` 显式刷新到 `dash/data/project-status.*`；ROADMAP Now / Next / Done 变化后校验会要求同步刷新。定时任务只运行 `runtime`，不覆盖项目状态或 `dashboard.today` 的 Owner 人工判断。
- Home 顶部 Today Status 卡已改为自动推导主状态：今日 Todo 优先，其次参考自动化异常、当前时段、ROADMAP 待推进 / 主线和 Token 活跃生成执行、巡检、复盘、推进、探索等模式。宽桌面使用左文案 / 正中央圆环 / 右信号三列，圆环中心与状态卡内容区中心重合，当前时间用独立 pill 显示在环下方；`自动生成` 新鲜度 pill 位于左侧 eyebrow 旁。右侧四条信号等高排列，彩色节点进入第一行网格并与标签、主值对齐。状态条四张小卡固定为今日执行、数据同步、Token 7 天、系统自动化，不再保留重复的“当前主线 / 待推进”数字卡。`dashboard.json.today` 只作为当天人工 override；旧日期判断会被忽略，不再显示“待刷新 N 天”。
- Home 右侧原“时间点”静态模块已替换为“今日 Todo”：从 `dash/data/wiki-todos.json` 里只筛选 `due_at` 等于浏览器当天日期的未完成待办；过期未完成和无日期待办仍留在近期待办卡，不进入今日 Todo。
- Home 时间卡片已支持 `dashboard.json.specialDates`：固定月日用于每年重复的生日 / 纪念日，`repeat: "monthly"` 用于每月重复日期，一次性事项使用完整公历日期。第一行显示当天内置节日和个人特殊日期，第二行独立显示严格晚于当天的最近一项；候选会统一比较母亲节、父亲节、农历节日、生日、纪念日和续费日。MaxNow 已录入 personal-wiki 中的 77 / Max 生日和三项关系纪念日，并记录每月 25 日为 Codex 续费日。
- Home 顶部已新增北京市海淀区天气卡：地点、天气、当前温度、今日高低温和图标来自 `dashboard.json.weather`，并由 `runtime` 定时刷新。
- Home 主内容区顶部已拆成左侧 Token 热力格 + Personal Wiki 近期待办竖向栈、右侧市场涨幅卡：左侧上方展示近 90 天 Token 活动，左侧下方展示 personal-wiki 近期待办，右侧展示纳指100、标普500、上证指数、深证成指和创业板指；行情数据来自 `dash/data/market-indices.json` 并由 `runtime` 每 10 分钟刷新。
- Home 左侧导航栏已收窄到更紧凑的桌面宽度，当前保留七个一级入口，不做折叠侧栏；芭蕾上线时需验证短屏侧栏滚动，以及 `720px` / `768px` 高度和 `860px` / `390px` 宽度下的导航与图表几何。
- 前端静态站已部署到 `dash.maxnow.cn`；仓库位于 `/var/www/maxnow-dashboard`，nginx 应指向 `/var/www/maxnow-dashboard/dash`。
- Dash 访问保护由 `dash/login.html`、`scripts/maxnow_auth_service.py`、nginx `auth_request` 和 7 天 HttpOnly 会话 Cookie 共同负责，覆盖页面、静态资源和 `/data/`；认证服务只监听 `127.0.0.1:8765`，复用现有 htpasswd 哈希，不读取 Dashboard 数据。真实凭据和会话密钥不进入仓库，Blog 不继承 Dash 认证策略。
- `maxnow.cn` 权威 DNS 继续由 DNSPod 托管，nameserver 为 `achernar.dnspod.net` / `cylinder.dnspod.net`；Cloudflare Access 评估已停止，不属于当前访问链路。
- 服务器 GitHub CLI 已授权，可以读取 private personal-wiki；同步命令已固化为 crontab，失败日志会进入 Home 系统状态。
- 个人博客已确定推荐走 `blog.maxnow.cn`，但还缺发布 manifest / front matter 策略、构建脚本、nginx 子域名配置和第一批公开文章清单。
- 同行记已经有页面、数据契约和 personal-wiki 同步脚本；后续重点是继续在 personal-wiki 补真实地点、日期、备注和照片入口。
- 生活页已经有第一个功能区“吃啥”；后续若增加其他生活工具，应继续保持轻量、只读数据源和本地临时交互，不让 Home 变重。
- MaxNow 功能待办以 `ROADMAP.md` 为准，不应混入 dashboard / last-30 运行数据。
- 当前可执行任务以 `ROADMAP.md` 为准。

## 建议下一步

1. 继续完成 Blog 发布 manifest、front matter 策略、第一批公开文章清单和静态构建链路。
2. 实现芭蕾自动抢课动态配置：服务器单一配置源、最小低权限接口、MaxNow 编辑面板、配置冻结与失败回退；保持 14:20 抢课关键路径不依赖配置接口。
3. 补前端 smoke test、JavaScript 语法检查、移动端几何回归和无障碍状态，再扩展新的一级页面。
4. 闻道 v7 会话生命周期实验正在按每 20 分钟无限期运行；持续观察身份失效、Session 轮换与 `Set-Cookie`。生产每天 `09:00 / 12:00 / 15:00 / 18:00 / 22:00`、周日额外 14:30 rolling 与每月 full timer 已启用；后续观察课表发布和身份阻断，再决定是否推进 personal-wiki 学习记录同步。
