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
- `scripts/sync_system_status.py`：采集 nginx、HTTPS、git commit、磁盘、内存和 wiki-todos 同步状态，只刷新 dashboard 的系统状态字段；Home 系统状态卡作为入口，云服务页复用同一份快照展示更完整的服务器状态。
- `scripts/sync_openclaw_usage.py`：只读服务器 `/root/.openclaw` 轨迹，生成 OpenClaw Token 用量账本和 OpenRouter 等价费用估算。
- `scripts/sync_codex_usage.py`：只读 `.codex/sessions` 中的 `token_count`、`turn_context.model` 和 `task_complete.duration_ms`，生成 Codex Token 用量与已完成任务活跃时长；不导出 prompt / response 正文。
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
- `dash/data/codex-macos-usage.json`：macOS 本机 Codex 每日 token 用量、按模型 / 任务拆分；来源为 macOS 本机 `.codex/sessions` 的 `token_count` 事件。
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
- `dash/login.html` / `dash/login.js`：MaxNow 私人访问入口；只提交用户名和密码到同源 `/auth/login`，不在浏览器保存或读取会话 Cookie。
- `scripts/maxnow_auth_service.py`：服务器本机认证服务；读取 htpasswd、签发和校验 7 天 HttpOnly 会话，不读取 Dashboard 数据。
- `server/maxnow-*`：systemd、nginx 限速、认证 location 和站点配置的仓库内可复现模板。
- `scripts/sync_wiki_todos.py`：通过本地或服务器 `gh` 登录态刷新 `dash/data/wiki-todos.*`，避免前端暴露 GitHub token。
- `scripts/sync_ricky_travel.py`：通过本地相邻 personal-wiki checkout 或服务器 `gh` 登录态读取 `wiki/relationships/ricky-travel.json`，刷新 `dash/data/ricky.*`。
- `scripts/sync_life_foods.py`：通过本地相邻 personal-wiki checkout 或服务器 `gh` 登录态读取 `wiki/life/food-picker.md`，刷新 `dash/data/life-foods.*`。
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
- Token 自动化使用同一固定小时周期：macOS `:00`、Windows `:02`、root server sources `:05`、ubuntu ledger merge `:10`。本机任务继续使用专用 main clone；Git HTTP 低速边界和 SSH keepalive 防止 `git pull` / `push` 无限挂起，Windows 任务最长运行 10 分钟。
- 服务器 root crontab 使用 `MAXNOW-TOKEN-SOURCE-REFRESH` 和 `/tmp/maxnow-token-source-refresh.lock`，日志写入 `logs/token-source-refresh.log`；ubuntu crontab 使用 `MAXNOW-TOKEN-USAGE-REFRESH` 和 `/tmp/maxnow-token-usage-refresh.lock`，每小时 `:10` 拉取并合并总账。
- `dash/data/token-usage.json` 是 Token 页统一入口；OpenClaw、Codex Windows / macOS、Codex server 和后续其他来源都应合入这个总账。Token 页 `1d` 按当前浏览器本地日期 00:00 起算，`7d` / `30d` 包括今天在内的最近 7 / 30 个自然日；来源费用面板和模型占比、调用消耗同层并列展示，并且来源 token、费用和 runs 跟随当前范围更新。页头展示各来源账本的最后更新时间。
- 2026-07-10 起，Dash Home 首批读取 dashboard / project-status / last-30 / wiki-todos / dounai_checkin / market-indices / project-meta 小数据并渲染；Token 总账、Ricky、生活页数据和 Leaflet 地图资源按当前视图需要再加载。`.js` wrapper 仍由脚本生成并校验，但主要作为数据一致性和静态兜底资产，不要重新放回首屏同步脚本列表。
- 2026-07-08 起，Home 状态条下方主内容采用统一 `home-board` 两列版式：左列 `home-lane-primary` 放 Token 热力格、Personal Wiki、待推进、AI 前沿和版本更新，版本更新固定排在 AI 前沿下方；右列 `home-side-stack` 视觉上是 widget 网格，按优先级放市场涨幅、今日 Todo、近期用量、豆奶和系统状态。两列外壳负责大块对齐，左列负责吸收内容型长模块，右列 widget 卡型负责半宽 / 满宽短状态入口，避免左列空着而右列继续下排，也避免所有卡片被二列布局拉成大卡。后续新增 Home 卡片必须先选 lane，再选 `wide-short` / `wide-tall` / `mid-short` / `mid-tall` / `widget-compact` / `widget-wide` 卡型。
- 2026-07-10 线上已部署提交 `538dc40`，AI 前沿功能版本为 `1.0.3.00`、Dash 缓存为 `styles.css?v=128` / `app.js?v=110`；部署前完整备份并暂存服务器运行数据，只恢复不与 AI 前沿冲突的 dashboard、豆奶、行情、同行记和 Wiki Todo，随后重新生成 `ai-news.*`、`last-30.*` 与 `project-meta.*`。
- 豆奶签到展示只读取 `dash/data/dounai_checkin.json` 中的流量、豆丁、时长、累计签到天数、账号余量快照、账号日均可用历史、直接流量使用记录和近 30 天 records；豆丁只进入 Home 摘要，不进入豆奶详情页展示口径，不要在 MaxNow 前端增加签到写入、账号操作或 cron 管理。真实流量消耗优先使用 `traffic_usage_history`，不要再用账号余量快照差分作为主口径；余量差分只可作为缺数据时的估算说明。
- 同行记页面只读取 `dash/data/ricky.json`，不在前端编辑、不回写 personal-wiki、不依赖外部在线地图服务；事实来源归 personal-wiki 的 `wiki/relationships/ricky-travel.json`。
- 生活页“吃啥”只读取 `dash/data/life-foods.json`；前端允许本次会话内临时勾选 / 取消勾选和随机，但不回写 personal-wiki，候选长期来源归 `wiki/life/food-picker.md`。
- 服务器上的豆奶签到由 root/OpenClaw 侧脚本维护；`/root/.openclaw/gen_checkin_data.py` 会把生成结果同时写入 `/root/MaxNow/dash/data/dounai_checkin.json` 和线上部署目录 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。线上页面读取后者。2026-06-21 已扩展该脚本，让它用现有豆奶登录态只读抓取剩余流量、账号有效期、VIP 有效期和日均可用流量，写入 `account` 字段，并按日期维护 `account_history`。2026-07-05 已继续扩展脚本，读取 `/user/trafficlog` 的近 7 天真实使用量并合并到 `traffic_usage_history`，同时读取 `?ajax=1` 的近 12 小时节点活跃分布；同日新增 root cron `MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT`，每天 00:05 执行 `gen_checkin_data.py --traffic-only --exclude-today`，专门更新昨天及更早的真实使用量。2026-07-06 已确认豆奶脚本依赖 root 的 Playwright `chromium_headless_shell-1208`；清理服务器浏览器缓存后需要运行 `python3 -m playwright install chromium` 并做 headless launch smoke test，补签应优先用不发通知的 `/root/.openclaw/daily_checkin.sh`。

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

- 2026-07-10 整体体检推动 MaxNow 从“继续增加功能”转向“可信状态工作站”。`dash.maxnow.cn` 和 `/data/` 已由自定义登录页、nginx `auth_request` 和服务器本机 Cookie 认证服务保护，Blog 保持公开；后续重点转为 JSON 读取失败与新鲜度闭环、wrapper 定位、自动测试、无障碍状态和外部依赖安全。Home 项目状态可信度已通过独立 `project-status.*`、ROADMAP 指纹校验和过期提示完成修复；可执行条目以 `ROADMAP.md` 为准。
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
- Dash 左侧导航已新增“云服务”tab，位于 Token 下方。该页只读列出服务器自动化、数据同步、站点托管和日志边界，不从前端触发服务器操作；页面不再保留顶部重复摘要卡，Host 与站点域名归入“系统与托管”模块，后续任务卡自然排列，不再插入独立“定时任务”分组标题。系统与托管模块不展示部署根目录、nginx 配置路径、采集器说明等低频实现细节。
- Dash 左侧导航已新增“同行记”tab，副标题为“我和 Ricky”。该页用 Leaflet + OpenStreetMap 真实地图和轻量统计承载两人的共同足迹，地点和旅行记录暂时只进入 marker / popup 数据，不单独铺列表；内置 SVG 地图只作为 fallback。
- Dash 左侧导航已新增“生活”tab，副标题为“吃啥”。该页当前提供“吃啥”随机选择器：默认全选、数量默认 1，可临时取消候选并从勾选项中随机选取一个或多个结果；候选从 personal-wiki `wiki/life/food-picker.md` 同步。
- 2026-07-10 起，豆奶、Token、云服务、生活和同行记统一使用 `secondary-view` / `secondary-page-head` 视觉协议：顶部 4px 主题线、轻色渐变白底、统一圆角/阴影/hover 与状态 pill；各页只保留自己的语义色和内容结构，Home 不受这组规则影响。
- Home 项目主线和待推进事项由 `python scripts/update_data.py project-status` 从 `ROADMAP.md` 显式刷新到 `dash/data/project-status.*`；ROADMAP Now / Next / Done 变化后校验会要求同步刷新。定时任务只运行 `runtime`，不覆盖项目状态或 `dashboard.today` 的 Owner 人工判断。
- Home 顶部 Today Status 卡已改为自动推导主状态：今日 Todo 优先，其次参考自动化异常、当前时段、ROADMAP 待推进 / 主线和 Token 活跃生成执行、巡检、复盘、推进、探索等模式。右侧信号区使用青色 24 小时圆形进度环，环内显示今天已过去的整数百分比，当前时间显示在环外；右侧信号节点与对应行首行文字按中心对齐，顶部横线只作为卡片状态强调。状态条四张小卡固定为今日执行、数据同步、Token 7 天、系统自动化，不再保留重复的“当前主线 / 待推进”数字卡。`dashboard.json.today` 只作为当天人工 override；旧日期判断会被忽略，不再显示“待刷新 N 天”。
- Home 右侧原“时间点”静态模块已替换为“今日 Todo”：从 `dash/data/wiki-todos.json` 里只筛选 `due_at` 等于浏览器当天日期的未完成待办；过期未完成和无日期待办仍留在近期待办卡，不进入今日 Todo。
- Home 时间卡片已支持 `dashboard.json.specialDates`：用手动维护的公历日期或一次性日期在当天显示生日、纪念日等轻量提醒；没有命中时继续显示“今日无节日”。
- Home 顶部已新增北京市海淀区天气卡：地点、天气、当前温度、今日高低温和图标来自 `dashboard.json.weather`，并由 `runtime` 定时刷新。
- Home 主内容区顶部已拆成左侧 Token 热力格 + Personal Wiki 近期待办竖向栈、右侧市场涨幅卡：左侧上方展示近 90 天 Token 活动，左侧下方展示 personal-wiki 近期待办，右侧展示纳指100、标普500、上证指数、深证成指和创业板指；行情数据来自 `dash/data/market-indices.json` 并由 `runtime` 每 10 分钟刷新。
- Home 左侧导航栏已收窄到更紧凑的桌面宽度，保留原有三个入口，不做折叠侧栏。
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

1. 建立数据读取失败和新鲜度闭环，避免请求失败继续被显示成真实为 0 或“暂无数据”。
2. 补前端 smoke test、JavaScript 语法检查、移动端几何回归和无障碍状态，再继续扩展 Blog 发布链路。
3. 观察自定义登录会话、Last-30 免费源和豆奶 00:05 traffic closeout 的连续稳定性。
