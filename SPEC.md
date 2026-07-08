# MaxNow 产品规格

MaxNow 是部署在 `dash.maxnow.cn` 的私人状态工作站。它不是公开主页、新闻站，也不是通用仪表盘。它的核心任务是让 Owner 快速看见：自己现在处于什么状态、正在推进什么、自动化系统在做什么，以及 AI / 工具使用是否正常。

## 产品定位

- 使用者：Owner 本人。
- 主要使用方式：每天打开几次，用几秒钟理解当前个人和系统状态。
- 核心价值：保存持续的个人上下文，而不是制造一次性提醒。
- 气质：平静、紧凑、偏操作型、可维护。
- 首屏优先级：个人状态、今日执行、数据同步、Token 近期活动、系统状态，以及少量外部输入。

## 仓库结构

MaxNow 采用单仓库、多出口结构：

```text
dash/  -> dash.maxnow.cn 私人状态工作站
blog/  -> blog.maxnow.cn 公开博客发布层
```

根目录保留 `AGENTS.md`、`SPEC.md`、`STYLE_CONTEXT.md`、`ROADMAP.md`、`CONTEXT.md`、`IDEAS.md`、`UPDATE_LOG.md`、`DEPLOY.md` 和 `SERVER_RUNBOOK.md`，用于统一维护产品规则、视觉样式上下文、路线图、上下文、部署和操作记录。暂时不拆成多个 GitHub 仓库。

## 系统组成

MaxNow 由四类文件组成：

1. 页面代码
   - `dash/index.html`
   - `dash/styles.css`
   - `dash/app.js`
   - 由 Codex 或 Owner 维护。
   - 负责页面结构、样式、渲染和交互。

2. 数据文件
   - `dash/data/dashboard.json`
   - `dash/data/dashboard.js`
   - `dash/data/ai-news.json`
   - `dash/data/ai-news.js`
   - `dash/data/last-30.json`
   - `dash/data/last-30.js`
   - `dash/data/wiki-todos.json`
   - `dash/data/wiki-todos.js`
   - `dash/data/openclaw-usage.json`
   - `dash/data/openclaw-usage.js`
   - `dash/data/codex-usage.json`
   - `dash/data/codex-usage.js`
   - `dash/data/codex-macos-usage.json`
   - `dash/data/codex-macos-usage.js`
   - `dash/data/codex-server-usage.json`
   - `dash/data/codex-server-usage.js`
   - `dash/data/token-usage.json`
   - `dash/data/token-usage.js`
   - `dash/data/market-indices.json`
   - `dash/data/market-indices.js`
   - `dash/data/project-meta.json`
   - `dash/data/project-meta.js`
   - `dash/data/dounai_checkin.json`
   - `dash/data/ricky.json`
   - `dash/data/ricky.js`
   - `dash/data/life-foods.json`
   - `dash/data/life-foods.js`
   - 这是页面和自动化之间的数据契约。

3. OpenClaw skill
   - `openclaw/maxnow-dashboard/SKILL.md`
   - `openclaw/last-30/SKILL.md`
   - 告诉 OpenClaw：MaxNow 是什么、可以更新哪些数据文件、哪些文件不能碰、如何校验输出。

4. 校验脚本
   - `scripts/check.py`
   - `scripts/update_data.py`
   - 由 Codex 或 Owner 维护。
   - `scripts/check.py` 用来检查必要文件、JSON 合法性、wrapper 一致性和本地预览可访问性。
   - `scripts/update_data.py` 用来统一刷新运行数据、重生成 `.js` wrapper，并在结束时运行一致性校验。

5. 同步脚本
   - `scripts/sync_wiki_todos.py`
   - `scripts/sync_system_status.py`
   - `scripts/sync_openclaw_usage.py`
   - `scripts/sync_codex_usage.py`
   - `scripts/sync_token_usage.py`
   - `scripts/sync_project_meta.py`
   - `scripts/sync_weather.py`
   - `scripts/sync_market_indices.py`
   - `scripts/sync_ricky_travel.py`
   - `scripts/sync_life_foods.py`
   - 由 Codex 或 Owner 维护。
   - `scripts/sync_wiki_todos.py` 使用本地或服务器的 `gh` 登录态读取 private personal-wiki，并生成 MaxNow 可静态读取的 `dash/data/wiki-todos.*`。
   - `scripts/sync_system_status.py` 采集机器可判断的系统状态，只更新 `dash/data/dashboard.*` 中的 `automation` 和 `system` 字段。
   - `scripts/sync_openclaw_usage.py` 只读 OpenClaw 服务器轨迹，生成 Token 使用账本和 OpenRouter 等价费用估算。
   - `scripts/sync_codex_usage.py` 只读 Codex session `token_count` 事件，生成 Codex Token 使用账本，不导出对话正文。
   - `scripts/sync_token_usage.py` 合并 OpenClaw / Codex 源账本，生成 Token 页面统一总账。
   - `scripts/report_codex_usage.ps1` 在 Owner 的 Windows 本机定时刷新本机 Codex 用量，只提交 `codex-usage.*` 源账本；统一 Token 总账由服务器定时合并。
   - `scripts/report_codex_usage_hidden.vbs` 通过 `wscript.exe` 无窗口启动本机 Codex 用量上报脚本，避免计划任务弹出瞬时命令行窗口。
   - `scripts/install_local_codex_usage_task.ps1` 注册本机 Windows Task Scheduler 任务，默认每 1 小时静默运行一次本机 Codex 用量上报。
   - `scripts/report_codex_usage.sh` 在 Owner 的 macOS 本机刷新 Codex 用量，只提交 `codex-macos-usage.*` 源账本；统一 Token 总账由服务器定时合并。
   - `scripts/install_local_codex_usage_launchd.sh` 注册 macOS launchd 任务，默认每 1 小时运行一次本机 Codex 用量上报。
   - `scripts/refresh_token_usage_on_server.sh` 在服务器拉取最新源账本后保护 OpenClaw / Codex server 运行态账本，并合并 `token-usage.*`。
   - `scripts/sync_project_meta.py` 从 `VERSION`、Git 状态和 `UPDATE_LOG.md` 生成 MaxNow 版本号和最近更新模块数据。
   - `scripts/sync_weather.py` 从 Open-Meteo 免费 forecast API 刷新北京市海淀区天气，只更新 `dash/data/dashboard.*` 中的 `weather` 字段。
   - `scripts/sync_market_indices.py` 从腾讯公开行情接口刷新纳指100、标普500和 A 股主指数，只生成 `dash/data/market-indices.*`。
   - `scripts/sync_ricky_travel.py` 从 personal-wiki `wiki/relationships/ricky-travel.json` 刷新同行记页面数据，只生成 `dash/data/ricky.*`。
   - `scripts/sync_life_foods.py` 从 personal-wiki `wiki/life/food-picker.md` 刷新生活页吃啥候选，只生成 `dash/data/life-foods.*`。

6. 产品记忆文档
   - `CONTEXT.md`
   - `STYLE_CONTEXT.md`
   - `ROADMAP.md`
   - `IDEAS.md`
   - `UPDATE_LOG.md`
   - 由 Codex 或 Owner 维护。
   - 用来跨会话保存上下文地图、前端视觉约定、路线图、未来想法和项目更新记录。

## 导航

v1 保留六个一级入口：

1. Home
   - 私人状态工作站。
   - 默认页面。
2. 豆奶
   - 豆奶签到详情页，展示近 30 天流量和账号有效期延长时长。
3. Token
   - Token 使用详情页。
4. 云服务
   - 服务器自动化详情页，只读列出云服务器上的系统与托管状态、定时任务、数据同步和运行边界；不保留与下方任务卡重复的顶部摘要卡。
5. 生活
   - 轻量生活工具页；当前先承载“吃啥”随机选择器。
6. 同行记
   - “我和 Ricky”的只读共同记录页，当前先承载地图和轻量统计。

不要随便新增页面。只有当某个问题无法放进 Home，且会明显伤害日常扫读体验时，才考虑新增页面。

公开博客不属于 `dash.maxnow.cn` 的内部页面。博客应作为独立公开站点发布到 `blog.maxnow.cn`；`dash.maxnow.cn` 只允许放紧凑的外部跳转入口、发布状态或最近发布摘要，不承载完整博客阅读体验。

## Home 页面

Home 按顺序回答这些问题：

1. 我今天处在什么状态？
2. 我当前最重要的主线是什么？
3. 今天应该推进什么？
4. 今天有哪些个人待办需要处理？
5. OpenClaw、服务器、数据同步和 Token 使用是否正常？
6. 有哪些外部输入值得稍后注意？

必备模块：

- 今日状态：由前端根据今日 Todo、当前时段、ROADMAP 待推进 / 主线、Token 活跃和自动化状态自动推导“执行 / 推进 / 复盘 / 探索 / 巡检”等模式；右侧信号区使用 00:00-24:00 的今日进度轴表达当天已过时间，时段、推进、Token、自动化信号作为节点挂在轴旁；`dashboard.json.today` 只作为当天人工 override，旧日期判断不再占据主状态。
- 顶部状态条：只保留每天扫一眼能决策的短指标：今日执行、数据同步、Token 7 天和系统自动化。今日执行读取 personal-wiki 中 `due_at` 等于浏览器当天日期的未完成待办；数据同步聚合 Wiki Todo、Token、天气、市场、Last-30 和项目元信息的新鲜度，不再把“当前主线 / 待推进”做成独立数字小卡。
- 顶部天气卡：Home 顶部右侧、时间卡左边展示北京市海淀区今日天气、当前温度、今日高低温和对应天气图标；天气来自 `dash/data/dashboard.json` 的 `weather` 字段，由 `scripts/sync_weather.py` 或 `python scripts/update_data.py runtime` 定时刷新，前端不实时请求外部天气接口。
- 今日小日历：Home 顶部右侧展示公历日期、当前时间、农历日期、当天节日和当天命中的个人特殊日期；节日用于提示父亲节、端午节、春节等常见日期，不依赖数据文件写入。个人特殊日期采用 `dash/data/dashboard.json` 中的 `specialDates` 手动维护，只服务“今天是否需要提醒”，不扩展成完整日历。
- Home 主内容版式：状态条下方使用统一 `home-board` 两列外壳，`home-lane-primary` 承载左侧主任务和内容型长模块，右侧 `home-side-stack` 只承载短扫读次级信号和状态入口；`home-lane-signal` / `home-lane-rail` 只作为语义分组，视觉上展平成右侧 widget 网格。所有 Home 模块都保留 `home-card-*` 和 `data-card-size`，右侧小组件用 `widget-compact` 占半宽，需要内部指标网格或列表宽度的短状态模块用 `widget-wide` 或 `mid-*` 占满右列。最近更新和外部输入属于左侧内容流；不要再保留单独“稍后留意”卡片，待办线索进入待推进 / Roadmap，系统链路进入云服务 / 系统状态，文档入口进入最近更新或项目状态。不要再用固定 `grid-area`、局部左右列、固定高度或空白补丁拼模块，也不要为了二列或三列对齐硬拉大所有卡片。新增模块必须先在 `STYLE_CONTEXT.md` 的页面版式协议中确认语义 lane 和卡型。
- Token 近期活动：Home `wide-short` 卡展示近 90 天每日 Token 活动热力格，替代原“当前主线”列表；顶部状态条仍保留 7 天 Token 小摘要。
- 市场涨幅：Home `mid-tall` 卡展示纳指100、标普500、上证指数、深证成指和创业板指的当前点位、涨跌幅和日内迷你走势；数据来自 `dash/data/market-indices.json`，由 `scripts/sync_market_indices.py` 或服务器 `runtime` 每 10 分钟刷新，前端不直接请求行情接口。
- 待推进：1-3 个近期应该移动的 Now / Next 动作；这里不是完整 todo app，也不是已完成记录。
- Home 不再单独展示“今日记录”卡片；静态项目原则和边界说明进入规格、上下文或最近更新，真正的当天个人判断由顶部今日状态承载。
- 今日 Todo：Home 右侧只展示 personal-wiki 同步来的当天明确执行日期待办；以浏览器当天日期匹配 `due_at`，不混入过期未完成或无日期待办。v1 只读展示，不支持在 MaxNow 内编辑或标记完成。
- 系统状态：作为云服务页入口，用来快速判断机器是否健康；点击卡片进入“云服务”页查看“系统与托管”模块，其中包含 Host、站点域名、nginx、证书、部署版本、CPU、磁盘、内存和运行时间等完整服务器状态快照。`TLS / nginx` 不再作为单独任务卡展示，也不展示部署根目录、nginx 配置路径或采集器说明这类低频实现细节。
- 豆奶签到：Home 只展示每日签到摘要入口，第一排展示今日流量、今日豆丁和今日账号有效期延长时长，第二排展示累计签到天数、累计流量和累计账号有效期延长时长；不在 Home 放趋势图。点击卡片进入“豆奶”详情页。数据来自 `dash/data/dounai_checkin.json`。
- 外部输入：Home 只保留一个外部输入模块，由 Last-30 展示最新信号、本周观察和近 30 天主线；不要再单独铺一张重复的 AI 外部输入卡，也不再用“稍后留意”承接杂项链接。
- personal-wiki 近期待办入口：Home `wide-tall` 卡只读展示近期未完成待办的前 4 条，并跳转到 personal-wiki；v1 不支持编辑或标记完成。完整数量只进入状态 pill，不允许用全部待办撑高首页。
- MaxNow 最近更新：Home 左侧内容流展示当前可读版本号、部署说明和最近几条 `UPDATE_LOG.md` 更新摘要；版本号由根目录 `VERSION` 维护，格式为 `x.x.x.xx`。任何已完成的 Owner 可见或运维相关改动都必须升版本并刷新 `project-meta`：小 UI / 文案 / 布局调整、新增页面能力、新数据源和新自动化默认升最后两位；重要功能模块稳定落地升 patch；大版本阶段切换升 minor / major。

## AI 每日精选

AI 每日精选属于外部输入的一小块，不是新闻产品。

- 默认更新时间：服务器本地时间 00:10。
- Home 最多显示 3 条。
- 优先官方来源和高信号开发者 / 社区来源。
- X / Twitter 可以用于早期信号，但不是硬依赖。
- 如果 X / Twitter 不可用，使用官方博客 / RSS、Hacker News、GitHub、Reddit、项目 release、研究机构等来源。
- 二级新闻站只作为补充验证。

每条内容都要说明它为什么和 Owner、当前项目、工具、模型选择或成本有关。

## Token 页面

Token 页面只回答 Token 相关问题：

- 今天自然日使用量
- 包括今天的最近 7 天使用量
- 包括今天的最近 30 天使用量
- 全部已采集使用量
- total / input / output / cacheRead / cost
- 模型占比和会话消耗
- 最近 30 天每日 Token 折线图
- 可用时通过色阶呈现异常高消耗日期
- Home 近 90 天 Token 热力格可用时通过色阶呈现高消耗日期，鼠标悬浮展示日期和 token 数。

Token 真实数据按来源接入，并由统一总账合并展示：

- `dash/data/openclaw-usage.json` 保存 OpenClaw 的 input / output / cacheRead / total token、按天、按模型、按任务拆分，以及按 OpenRouter 价格折算的等价费用。
- `dash/data/codex-usage.json` 保存 Windows 兼容本机 Codex 的 input / output / cacheRead / total token、按天、按模型、按任务拆分；来源为本机 `.codex/sessions` 中的 `token_count` 事件，不导出 prompt / response 正文。
- `dash/data/codex-macos-usage.json` 保存 macOS 本机 Codex 的同类账本，来源为 macOS 本机 `.codex/sessions`，source 固定为 `codex-macos` / `Codex macOS`，避免覆盖 Windows 账本。
- `dash/data/codex-server-usage.json` 保存服务器 Codex 的同类账本；来源为服务器 `/root/.codex/sessions`，由 root cron 刷新，不导出 prompt / response 正文。
- `dash/data/token-usage.json` 保存合并后的统一 Token 总账，Token 页面优先读取这个文件。
- OpenClaw 源账本的 `pricingBasis` 必须标记为 `openrouter-equivalent`，不要把它当作真实扣费账单；Codex 源账本使用 `openai-api-equivalent`，统一总账使用 `mixed`。
- OpenClaw 费用使用 OpenRouter 等价估算；Codex 费用使用 OpenAI API 等价估算。两者都是估算口径，不等同于真实供应商账单或订阅账单。
- 本机 Codex 用量可由 Windows Task Scheduler 或 macOS launchd 定期上报；默认每 1 小时运行一次。Windows Task Scheduler action 使用 `wscript.exe scripts/report_codex_usage_hidden.vbs`，由 VBS 以 window style 0 启动 `scripts/report_codex_usage.ps1`，避免 `powershell.exe` console 瞬时闪窗；macOS launchd 运行 `scripts/report_codex_usage.sh`。Windows 上报脚本只允许提交 `dash/data/codex-usage.*`；macOS 上报脚本只允许提交 `dash/data/codex-macos-usage.*`。遇到无关工作区改动会停止；本机上报成功后只 push 源账本，不再 SSH 触发服务器合并。
- 服务器 Codex 用量由 root crontab 每天刷新 `codex-server-usage.*`；统一 Token 总账由服务器 `MAXNOW-TOKEN-USAGE-REFRESH` 每 10 分钟拉取最新 `origin/main` 后运行 `scripts/refresh_token_usage_on_server.sh` 合并。该脚本会保护服务器运行时 `openclaw-usage.*` / `codex-server-usage.*`：空备份不能覆盖非空账本，OpenClaw 账本为空且 root 状态可读时应先刷新 OpenClaw 源账本，避免用空数据覆盖真实来源。
- Token 页在总量摘要下方显示来源费用面板，和模型占比、调用消耗并列为同一层信息区；至少区分 OpenClaw、Codex Windows / macOS 和 Codex server。来源列表的 token、费用和 runs 必须跟随当前选中的 `1d` / `7d` / `30d` / `all` 范围更新。
- Token 页头的 `1d` 以当前浏览器本地日期的 00:00 为边界，只展示今天自然日；`7d` / `30d` 为包括今天在内的最近 7 / 30 个自然日。范围切换放在顶部栏右侧，只在 Token 页显示，和 Blog / 刷新入口同层。Token 页面页头只保留两个独立信息 tab，不再使用共同外层卡片包住：左侧展示 Token 用量和总账合并时间，右侧展示每个 Token 来源账本的最后更新时间。
- 后续其他来源应复用同类日账本结构，再由汇总层合并 OpenClaw / Codex / 其他来源。

不要把完整 Token 页面复制到 Home。Home 只需要显示紧凑的使用状态。

## 豆奶页面

豆奶页面只回答签到资源相关问题：

- 今日获得流量和账号有效期延长时长。
- 顶部今日签到区展示今日流量、今日豆丁、今日延长，和 Home 豆奶摘要使用同一组今日数据。
- 累计签到天数、累计获得流量和累计延长时长。
- 当前账号剩余可用流量、有效期和按剩余天数折算的每日可用流量。
- 从豆奶 `流量日志` 直接抓取的近 7 天真实使用量，并随每日同步累积成最多 60 天的 `traffic_usage_history`，展示为“近 30 天实际使用流量”折线图；该图默认排除当天，只展示已完成日期。
- 近 30 天账号日均可用流量折线图，数据来自服务器侧每日账号余量快照。
- 近 30 天签到流量折线图，必须有 x / y 轴、日期刻度和每日具体数值。
- 近 30 天账号有效期延长时长折线图，必须有 x / y 轴、日期刻度和每日具体数值。

不要在豆奶页面加入签到操作、账号登录、豆丁展示或 cron 管理。豆丁只进入 Home 摘要，不进入豆奶详情页展示口径。账号余量只能从 OpenClaw / 服务器侧登录态生成的数据快照读取，前端不直接访问豆奶站点。

## 同行记页面

同行记页面只回答“我和 Ricky 一起去过哪里、留下过什么记录”：

- 左侧导航显示为“同行记”，副标题为“我和 Ricky”。
- 页面标题使用“我和 Ricky”，不做通用旅行社交产品。
- v1 为只读静态页面：真实地图和少量统计；地点与旅行记录先只作为地图点位和 popup 数据，不在页面上单独铺列表。
- 数据来自 `dash/data/ricky.json`，由 `scripts/sync_ricky_travel.py` 从 personal-wiki `wiki/relationships/ricky-travel.json` 同步；前端不编辑、不回写、不直接读取 private personal-wiki。
- 地点点位优先使用 `lat` / `lng` 放在 Leaflet + OpenStreetMap 真实地图上；`x` / `y` 只作为网络或地图脚本不可用时的静态 fallback。
- 地图 marker 显示 `mapLabel`，由 personal-wiki 源数据显式维护，避免用地点名前两个字自动截断出“乌兰”等不完整标签。
- 记录字段优先保持轻量：地点、日期、国家 / 地区、简短备注、可选照片或来源链接；列表展示后续需要时再恢复。

## 生活页面

生活页面承载低负担的个人生活小工具，不和 Home 的状态扫读混在一起。

- 左侧导航显示为“生活”，副标题当前为“吃啥”。
- 当前功能区为“吃啥”：默认勾选所有候选菜品，数量默认 1；Owner 可以临时取消勾选某些菜品，也可以把数量调大，然后点击“吃啥”从当前勾选项中随机选取不重复结果。
- 候选菜品来源是 personal-wiki `wiki/life/food-picker.md`；MaxNow 通过 `scripts/sync_life_foods.py` 生成 `dash/data/life-foods.json` / `dash/data/life-foods.js` 后只读展示。
- 前端只做本次页面会话内的勾选和随机，不编辑、不回写 personal-wiki，也不保存每次随机结果。

## 数据契约

OpenClaw 日常维护只能更新这些文件：

```text
dash/data/dashboard.json
dash/data/dashboard.js
dash/data/ai-news.json
dash/data/ai-news.js
dash/data/last-30.json
dash/data/last-30.js
dash/data/wiki-todos.json
dash/data/wiki-todos.js
dash/data/openclaw-usage.json
dash/data/openclaw-usage.js
dash/data/project-meta.json
dash/data/project-meta.js
dash/data/market-indices.json
dash/data/market-indices.js
dash/data/dounai_checkin.json
```

OpenClaw 日常维护不能更新这些文件：

```text
dash/index.html
dash/styles.css
dash/app.js
SPEC.md
README.md
DEPLOY.md
scripts/check.py
scripts/update_data.py
CONTEXT.md
ROADMAP.md
IDEAS.md
UPDATE_LOG.md
```

`dash/data/dashboard.json` 负责个人状态、主线、行动、时间线、系统状态、Token 使用、Home 天气卡和时间卡片的手动特殊日期列表。历史 `journal` 字段可保留为数据兼容，但 Home 不再读取它生成独立卡片。

其中 `automation` 和 `system` 可以由 `scripts/sync_system_status.py` 自动更新；`mainlines` 和 `actions` 仍保留 Owner 判断或受控草稿，不由系统状态脚本覆盖。`today` 可以保留当天人工 override，但 Home 主状态默认由前端从今日 Todo、ROADMAP、Token 和自动化信号推导，过期 `today` 不再作为主判断。

`specialDates` 是可选数组，用于 Home 时间卡片当天匹配。支持固定公历日期：

```json
{ "month": 7, "day": 18, "title": "77 生日", "type": "birthday" }
```

也支持一次性日期：

```json
{ "date": "2026-07-18", "title": "重要纪念日", "type": "anniversary" }
```

如果提供 `startYear`，页面会在标题后显示周年数。没有命中当天特殊日期时，页面保持“今日无节日”的低干扰提示。

`weather` 是可选对象，用于 Home 顶部天气卡展示北京市海淀区的今日天气摘要：

```json
{
  "location": "北京市海淀区",
  "district": "海淀",
  "condition": "晴",
  "icon": "sun",
  "tempC": 22,
  "highC": 35,
  "lowC": 23,
  "updatedAt": "2026-06-23 20:04",
  "source": "Open-Meteo"
}
```

`icon` 支持 `sun`、`cloud`、`rain`、`storm`、`snow`、`fog`。页面只读取这些字段展示，不从浏览器端请求天气 API。日常刷新由 `scripts/sync_weather.py` 更新 `dashboard.json` 并重新生成 `dashboard.js`；服务器 `runtime` 定时任务会一并运行该刷新。

`dash/data/ai-news.json` 只负责首页展示用的外部 AI 输入，通常取 Last-30 外部信号中的 0-3 条高相关内容。

`dash/data/last-30.json` 负责 AI 外部信号滚动记忆，不记录 MaxNow 内部项目流水。它保存今天、本周和近 30 天的 AI 新闻、模型 / API / agent / 开发者工具 / 成本 / 开源研究变化，以及这些变化对 Owner、MaxNow、Codex、OpenClaw 或模型选择的潜在影响。

`dash/data/wiki-todos.json` 负责 personal-wiki 近期待办的只读缓存，由 `scripts/sync_wiki_todos.py` 从 personal-wiki `wiki/tasks/todo.json` 生成。

`dash/data/openclaw-usage.json` 负责 OpenClaw 用量账本，由 `scripts/sync_openclaw_usage.py` 从服务器 `/root/.openclaw/agents/main/sessions/*.trajectory.jsonl` 等只读轨迹生成。它记录北京时间日桶、模型、任务、input / output / cacheRead / total token，并按 OpenRouter 模型价格生成等价费用估算。该费用不是实际供应商账单。

`dash/data/market-indices.json` 负责 Home 市场涨幅卡片，由 `scripts/sync_market_indices.py` 从腾讯公开行情接口生成。它只保存指数名称、符号、区域、当前点位、昨收、涨跌额、涨跌幅、更新时间、来源 URL 和压缩后的日内走势点；前端只读展示，不直接请求第三方行情接口。服务器 `runtime` 每 10 分钟会一并刷新该数据，接口失败时脚本优先保留旧缓存并标记 `stale`。

`dash/data/project-meta.json` 负责 MaxNow 自身版本和最近更新展示，由 `scripts/sync_project_meta.py` 从 `VERSION`、Git 状态和 `UPDATE_LOG.md` 生成；页面只读展示，不在前端修改版本号。`VERSION` 采用 `x.x.x.xx` 格式，例如 `1.0.0.00`。

版本号执行规则：

- 小 UI / 文案 / 布局调整：升最后两位，例如 `1.0.0.00` -> `1.0.0.01`。
- 新增页面能力 / 新数据源 / 新自动化：升最后两位，例如 `1.0.0.01` -> `1.0.0.02`。
- 重要功能模块稳定落地：升 patch，并把最后两位归零，例如 `1.0.0.12` -> `1.0.1.00`。
- 大版本阶段切换：升 minor 或 major，并重置后续位。
- 每次升版本后必须运行 `python scripts/update_data.py project-meta`，让 Home / 系统状态里的 MaxNow 版本同步到前端数据。

`dash/data/dounai_checkin.json` 负责豆奶每日签到记录、账号余量快照、账号日均可用历史和真实流量使用记录，由 OpenClaw / root 侧豆奶自动化更新；前端只读取流量、豆丁、账号有效期延长时长、累计签到天数、近 30 天 records、剩余可用流量、有效期、每日可用预算、`account_history`、`traffic_usage` 和 `traffic_usage_history`，不编辑、不回写，也不修改签到脚本或 cron。

`traffic_usage` 来自豆奶登录态只读访问 `https://dounai.pro/user/trafficlog` 和 `https://dounai.pro/user/trafficlog?ajax=1`：

```json
{
  "source": "dounai.pro/user/trafficlog",
  "synced_at": "2026-07-05 19:07",
  "window_days": 7,
  "daily": [
    { "date": "2026-07-05", "relative_label": "今天", "used_mb": 1341.44, "used_label": "1.31GB" }
  ],
  "recent_window_label": "12h node activity",
  "recent_log_count": 609,
  "recent_traffic_mb": 938.87,
  "recent_traffic_label": "938.87MB",
  "top_nodes_12h": [
    { "node": "节点名", "traffic_mb": 415.29, "traffic_label": "415.29MB" }
  ]
}
```

`traffic_usage.daily` 是豆奶页面直接展示的近 7 天真实使用量；`traffic_usage_history` 将每日同步得到的 direct daily entries 按日期合并并保留最近 60 天。每天 00:05 的 traffic-only closeout 只合并昨天及更早日期，并从 `traffic_usage_history` 移除当天，避免把 00:05 的极早日内碎片当作当天最终值。前端“近 30 天实际使用流量”图也会排除当天。`traffic_usage?ajax=1` 返回的是近 12 小时节点活跃 / 占比窗口，不等同于完整 7 天或 30 天总用量。

`dash/data/ricky.json` 负责“我和 Ricky”页面的只读地图数据、地点、旅行记录、摘要和可选照片 / 来源链接。它由 `scripts/sync_ricky_travel.py` 从 personal-wiki `wiki/relationships/ricky-travel.json` 生成；本地优先读取相邻 personal-wiki checkout，服务器侧可通过 `gh api` 读取 private personal-wiki。

`dash/data/life-foods.json` 负责生活页“吃啥”候选数据。它由 `scripts/sync_life_foods.py` 从 personal-wiki `wiki/life/food-picker.md` 生成；本地优先读取相邻 personal-wiki checkout，服务器侧可通过 `gh api` 读取 private personal-wiki。

当前带 `.js` wrapper 的数据集必须从对应 JSON 文件生成，并把同一个对象暴露给浏览器：

```text
window.MAXNOW_DASHBOARD_DATA
window.MAXNOW_AI_NEWS_DATA
window.MAXNOW_LAST30_DATA
window.MAXNOW_WIKI_TODO_DATA
window.MAXNOW_OPENCLAW_USAGE_DATA
window.MAXNOW_CODEX_USAGE_DATA
window.MAXNOW_CODEX_SERVER_USAGE_DATA
window.MAXNOW_TOKEN_USAGE_DATA
window.MAXNOW_MARKET_INDICES_DATA
window.MAXNOW_PROJECT_META_DATA
window.MAXNOW_RICKY_DATA
window.MAXNOW_LIFE_FOODS_DATA
```

## 数据来源策略

看板不应该依赖每天大量手动录入。理想分工是：

- 自动：Token 使用、GitHub 活动、服务器状态、OpenClaw 运行状态、AI 外部输入、时间戳。
- 半自动：当前主线、日常记录草稿、项目进展摘要。
- 手动：今日一句话判断、精力 / 状态、真正优先级、重要决定。

OpenClaw 记录事实并起草摘要。最终判断由 Owner 保留。

## personal-wiki 待办入口

Home 可以显示一个紧凑的 personal-wiki 近期待办入口。

边界：

- 入口放在 Home 主内容区左侧，位于 Token 热力格下方，不进入一级导航。
- 只读展示当前未完成待办集合；如果后续数量明显过多，再增加折叠或分页。
- 每条只展示标题、模块和截止状态；不提供逐条“打开”入口，也不让待办卡片整体跳转。
- 不在 MaxNow 中编辑、完成或回写待办。
- 数据来源是 `dash/data/wiki-todos.json`，该文件由 `scripts/sync_wiki_todos.py` 从 personal-wiki 的 `wiki/tasks/todo.json` 生成。

刷新策略：

- 页面加载时读取本地缓存一次。
- 顶部刷新按钮可以重新读取本地缓存。
- 不做前端自动轮询，也不从前端直接访问 private GitHub raw。
- 需要更新内容时，在本地或服务器运行 `python scripts/update_data.py runtime` 或 `python scripts/sync_wiki_todos.py`，由服务器 `gh` 登录态读取 personal-wiki 并重写 `dash/data/wiki-todos.*`。
- GitHub token 不得进入前端页面代码。

## 产品记忆

`CONTEXT.md` 用来说明项目上下文如何分层、哪些文件保存什么、谁负责更新、下一步缺口是什么。

`ROADMAP.md` 用来记录当前待做、下一步、长期方向、阻塞项和已完成的阶段成果。

`IDEAS.md` 用来记录不能丢的产品想法，包括未来入口、暂时搁置的概念、Owner 原始想法和待研究问题。

`UPDATE_LOG.md` 用来记录重要项目更新，尤其是产品方向、页面行为、数据结构、文件边界、部署方式或自动化规则的变化。

当一个新想法变成确定的产品行为时，再把它同步进本规格。在此之前，它只是已记录的想法，不是当前版本范围。

## Last-30：AI 外部信号滚动记忆

MaxNow 需要一层滚动记忆，用来保存今天、本周和最近 30 天的 AI 外部信号。它不是内部项目日志，也不是泛新闻流；只保留和 Owner 当前工具、模型选择、agent 能力、开发者生态或成本有关的信号。

已新增：

```text
dash/data/last-30.json
dash/data/last-30.js
openclaw/last-30/SKILL.md
```

Last-30 负责：

- 最新 AI 信号：左栏固定表达为“最新信号”，优先显示当天捕捉到的 1-3 条 AI 大事候选；如果当天暂无新条目，则回退显示最近 7 天内最新的高相关信号，避免每日 00:00 刷新后空白。不要把回退数据标成“今日”，也不要外露“适合进入观察池”这类内部筛选话术。
- 本周 AI 变化：模型、API、agent、开发者工具、成本、开源和研究方向的本周变化。
- 近 30 天 AI 主线：展示自动候选归类出的观察方向；数量文案只能表达“当前候选中约 X 条相关”，不要伪装成完整、权威的 30 天统计。
- 影响判断：哪些变化可能影响 MaxNow、Codex、OpenClaw、模型选择或 token 成本。
- 等待观察：还不确定、需要继续追踪或需要 Owner 确认是否重要的信号。

更新原则：

- 优先使用免费公开源：官方博客 / RSS、GitHub releases、Hacker News、Reddit / 公开社区、arXiv、GDELT 或类似免费索引。
- X / Twitter 不是硬依赖；只有 Owner 明确批准付费 API 和博主白名单后才接入。
- 先用脚本抓取标题、摘要、链接和时间，做本地关键词过滤和去重；不要把大量全文直接喂给模型。
- SDK release、普通 GitHub 开源更新和底层工程文章只能作为开发者生态补充；除非明确涉及模型、agent、MCP、API 或成本变化，否则不要挤占“最新 / 本周”AI 大事位置。
- 可以让 OpenClaw 对少量候选做二次筛选和压缩，但应控制在 10-20 条候选内。
- 每条记录尽量保存 `source`、`sourceType`、`confidence` 和 `needsOwnerConfirm`。前端展示 `confidence` 时应解释成“来源较稳 / 自动观察 / 待核实”，不要用 `high confidence` 这类容易被误解为内容判断已被确认的文案。
- 自动化可以起草事实和影响摘要，但重要判断最终由 Owner 确认。

## 未来方向：桌面伴随面板

MaxNow 未来可以在浏览器看板之外，增加桌面伴随入口。

macOS 方向：

- 做一个顶部状态栏 app。
- 点击图标后打开紧凑的下拉个人面板。
- 面板显示今日状态、今日 Todo、当前主线、待推进事项和简洁系统状态。

Windows 方向：

- 做一个桌面壁纸式个人看板。
- 它像一个平静、常驻的桌面状态层。
- 显示同一套核心个人状态信息，但适配扫一眼就能懂的使用方式。

共同约束：

- `dash.maxnow.cn` 仍然是 v1 标准入口。
- 桌面入口尽量复用同一套数据契约。
- 个人状态始终优先，外部 AI 输入保持次要。
- 不要把桌面伴随面板变成完整 todo app、新闻墙或社交产品。

## 未来方向：个人博客

MaxNow 可以增加一个公开博客发布层，但它和私人状态工作站分域部署。

推荐结构：

```text
dash.maxnow.cn  -> 私人状态工作站
blog.maxnow.cn  -> 公开博客
maxnow.cn       -> 未来公开主页 / 个人入口
```

内容来源：

- 原始内容来自 private personal-wiki 的 `raw/blog-vioiv`。
- 当前来源包含旧 Hexo Markdown 211 篇和缓存图片 167 个。
- personal-wiki 负责原文归档、隐私判断、发布筛选和长期知识归属。
- MaxNow 负责公开发布层：构建脚本、文章数据、静态页面、标签、归档、RSS 和部署入口。

第一阶段约束：

- 保持静态站，不引入登录、数据库或后端 API。
- 只发布明确筛选为 `public` / `published` 的文章。
- 不从公开前端直接读取 private personal-wiki。
- 不把旧博客全部无筛选发布；每篇文章至少要有标题、日期、slug、分类、标签、来源文件和可发布状态。
- `dash.maxnow.cn` 只能显示指向 `blog.maxnow.cn` 的外部链接、发布状态、待筛选数量和最近发布摘要。

## 视觉规则

- 深色、紧凑、偏操作型界面。
- 不做营销 hero，不做装饰性仪表盘填充物。
- 卡片只用于真实信息模块。
- 圆角保持在 8px 或以下。
- Dash 页面主内容的页边距、模块间距和同层卡片 grid gap 使用统一 4px 网格节奏；详情页大块默认采用 16px 间距，避免同一层级出现 14px、18px、20px、24px 混用。
- 外部输入在视觉上必须弱于个人状态。
- 首屏优先展示状态、主线和待推进事项。

## 实现边界

- v1 保留 Home、豆奶、Token、云服务、生活和同行记。
- v1 保持静态站点：不加登录、数据库或后端 API。
- 任何新的日常维护数据字段，都必须同时写进这里和 OpenClaw skill。
- 页面代码变化需要 Codex 或 Owner 明确意图；OpenClaw 永远不能改变页面结构。
