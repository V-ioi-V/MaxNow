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
   - `dash/login.html`
   - `dash/login.js`
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
   - `dash/data/project-status.json`
   - `dash/data/project-status.js`
   - `dash/data/dounai_checkin.json`
   - `dash/data/ricky.json`
   - `dash/data/ricky.js`
   - `dash/data/life-foods.json`
   - `dash/data/life-foods.js`
   - `dash/data/ballet.json`
   - `dash/data/ballet.js`
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
   - `scripts/sync_ballet.py`
   - `scripts/maxnow_auth_service.py`
   - 由 Codex 或 Owner 维护。
   - `scripts/sync_wiki_todos.py` 使用本地或服务器的 `gh` 登录态读取 private personal-wiki，并生成 MaxNow 可静态读取的 `dash/data/wiki-todos.*`。
   - `scripts/sync_system_status.py` 采集机器可判断的系统状态，只更新 `dash/data/dashboard.*` 中的 `automation` 和 `system` 字段。
   - `scripts/sync_openclaw_usage.py` 只读 OpenClaw 服务器轨迹，生成 Token 使用账本和 OpenRouter 等价费用估算。
   - `scripts/sync_codex_usage.py` 只读 Codex session `token_count`、`turn_context.model` 和 `task_complete.duration_ms`，生成 Codex Token 使用与活跃时长账本，不导出对话正文。
   - `scripts/sync_token_usage.py` 合并 OpenClaw / Codex 源账本，生成 Token 页面统一总账。
   - `scripts/report_codex_usage.ps1` 在 Owner 的 Windows 本机定时刷新本机 Codex 用量，只提交 `codex-usage.*` 源账本；统一 Token 总账由服务器定时合并。
   - `scripts/report_codex_usage_hidden.vbs` 通过 `wscript.exe` 无窗口启动本机 Codex 用量上报脚本，避免计划任务弹出瞬时命令行窗口。
   - `scripts/install_local_codex_usage_task.ps1` 注册本机 Windows Task Scheduler 任务，默认每小时 `:02` 静默运行一次本机 Codex 用量上报。
   - `scripts/report_codex_usage.sh` 在 Owner 的 macOS 本机刷新 Codex 用量，只提交 `codex-macos-usage.*` 源账本；统一 Token 总账由服务器定时合并。
   - `scripts/install_local_codex_usage_launchd.sh` 注册 macOS launchd 任务，默认每小时 `:00` 运行一次本机 Codex 用量上报。
   - `scripts/refresh_token_sources_on_server.sh` 由 root 每小时 `:05` 刷新 OpenClaw / Codex server 源账本。
   - `scripts/refresh_token_usage_on_server.sh` 在服务器拉取最新源账本后保护 OpenClaw / Codex server 运行态账本，并合并 `token-usage.*`。
   - `scripts/sync_project_meta.py` 从 `VERSION`、Git 状态和 `UPDATE_LOG.md` 生成 MaxNow 版本号和版本更新模块数据。
   - `scripts/sync_weather.py` 从 Open-Meteo 免费 forecast API 刷新北京市海淀区天气，只更新 `dash/data/dashboard.*` 中的 `weather` 字段。
   - `scripts/sync_market_indices.py` 从腾讯公开行情接口刷新纳指100、标普500和 A 股主指数，只生成 `dash/data/market-indices.*`。
   - `scripts/sync_ricky_travel.py` 从 personal-wiki `wiki/relationships/ricky-travel.json` 刷新同行记页面数据，只生成 `dash/data/ricky.*`。
   - `scripts/sync_life_foods.py` 从 personal-wiki `wiki/life/food-picker.md` 刷新生活页吃啥候选，只生成 `dash/data/life-foods.*`。
   - `scripts/sync_ballet.py` 只通过已确认的闻道 GET 页面读取预约与实际上课记录，使用服务器私有账本增量去重并生成脱敏 `dash/data/ballet.*`；它不包含预约、取消、候补或转课写操作。
   - `scripts/maxnow_auth_service.py` 仅在服务器本机监听，读取 nginx 密码哈希并签发短期 HttpOnly 会话 Cookie；它不读取 Dashboard 数据，也不提供业务 API。

6. 产品记忆文档
   - `CONTEXT.md`
   - `STYLE_CONTEXT.md`
   - `ROADMAP.md`
   - `IDEAS.md`
   - `UPDATE_LOG.md`
   - 由 Codex 或 Owner 维护。
   - 用来跨会话保存上下文地图、前端视觉约定、路线图、未来想法和项目更新记录。

## 导航

v1 保留七个一级入口：

1. Home
   - 私人状态工作站。
   - 默认页面。
2. 豆奶
   - 豆奶签到详情页，展示近 30 天流量和账号有效期延长时长。
3. Token
   - Token 使用详情页。
4. 芭蕾
   - “课程与进度”只读学习页，展示预约、实际上课记录、累计节数 / 小时、课程细分、趋势和同步状态。
5. 云服务
   - 服务器自动化详情页，只读列出云服务器上的系统与托管状态、定时任务、数据同步和运行边界；不保留与下方任务卡重复的顶部摘要卡。
6. 生活
   - 轻量生活工具页；当前先承载“吃啥”随机选择器。
7. 同行记
   - “我和 Ricky”的只读共同记录页，当前先承载地图和轻量统计。

不要随便新增页面。只有当某个问题无法放进 Home，且会明显伤害日常扫读体验时，才考虑新增页面。

“芭蕾 / 课程与进度”固定放在 Token 与云服务之间，导航顺序为 Home → 豆奶 → Token → 芭蕾 → 云服务 → 生活 → 同行记。这个位置只授予完整的长期学习模块，不授予单一抢课按钮。

公开博客不属于 `dash.maxnow.cn` 的内部页面。博客应作为独立公开站点发布到 `blog.maxnow.cn`；`dash.maxnow.cn` 只允许放紧凑的外部跳转入口、发布状态或最近发布摘要，不承载完整博客阅读体验。

## Home 页面

Home 按顺序回答这些问题：

1. 我今天处在什么状态？
2. 我当前最重要的主线是什么？
3. 今天应该推进什么？
4. 今天有哪些个人待办需要处理？
5. OpenClaw、服务器、数据同步和 Token 使用是否正常？
6. 今天和本周有哪些真正重要的 AI 前沿发布？

必备模块：

- 今日状态：由前端根据今日 Todo、当前时段、ROADMAP 待推进 / 主线、Token 活跃和自动化状态自动推导“执行 / 推进 / 复盘 / 探索 / 巡检”等模式；“自动生成”新鲜度紧邻左侧 `Today Status` 标识。宽桌面使用左文案、正中央圆环、右信号三列，圆环必须落在状态卡内容区的水平中心；圆环表达当天已过比例，百分比显示在环内，当前时间用独立 pill 显示在环外。时段、推进、Token、自动化四条信号等高排列，每个彩色节点进入第一行网格，并与该行的标签和主值居中对齐，而不是按两行内容整体居中。`dashboard.json.today` 只作为当天人工 override，旧日期判断不再占据主状态。
- 顶部状态条：只保留每天扫一眼能决策的短指标：今日执行、数据同步、Token 7 天和系统自动化。今日执行读取 personal-wiki 中 `due_at` 等于浏览器当天日期的未完成待办；数据同步聚合 Wiki Todo、Token、天气、市场、Last-30、项目元信息、Roadmap、豆奶、同行记、生活和芭蕾的新鲜度，不再把“当前主线 / 待推进”做成独立数字小卡。状态必须区分已同步、暂无记录、请求失败、数据过期、需要重新登录和尚未同步；请求失败时展示最后成功数据和时间，不能把失败伪装成数值 `0` 或空列表。
- 顶部天气卡：Home 顶部右侧、时间卡左边展示北京市海淀区今日天气、当前温度、今日高低温和对应天气图标；天气来自 `dash/data/dashboard.json` 的 `weather` 字段，由 `scripts/sync_weather.py` 或 `python scripts/update_data.py runtime` 定时刷新，前端不实时请求外部天气接口。
- 今日小日历：Home 顶部右侧展示公历日期、当前时间、农历日期、当天节日和当天命中的个人特殊日期；另一行始终展示严格晚于今天的最近特殊日期，格式为“x天后是xx日（x月x日）”。两行独立存在，当天命中生日、纪念日或续费日时，下一行仍继续寻找后续日期。候选同时包含父亲节、母亲节、春节等内置节日，以及 `dash/data/dashboard.json.specialDates` 中维护的生日、纪念日和续费日。
- Home 主内容版式：状态条下方使用统一 `home-board` 两列外壳，`home-lane-primary` 承载左侧主任务和内容型长模块，右侧 `home-side-stack` 只承载短扫读次级信号和状态入口；`home-lane-signal` / `home-lane-rail` 只作为语义分组，视觉上展平成右侧 widget 网格。所有 Home 模块都保留 `home-card-*` 和 `data-card-size`，右侧小组件用 `widget-compact` 占半宽，需要内部指标网格或列表宽度的短状态模块用 `widget-wide` 或 `mid-*` 占满右列。外部输入和版本更新属于左侧内容流，版本更新固定放在外部输入下方；不要再保留单独“稍后留意”卡片，待办线索进入待推进 / Roadmap，系统链路进入云服务 / 系统状态，文档入口进入版本更新或项目状态。不要再用固定 `grid-area`、局部左右列、固定高度或空白补丁拼模块，也不要为了二列或三列对齐硬拉大所有卡片。新增模块必须先在 `STYLE_CONTEXT.md` 的页面版式协议中确认语义 lane 和卡型。
- 除 Home 外，豆奶、Token、芭蕾、云服务、生活和同行记统一使用 `secondary-view` 页面协议：共用轻色渐变白底、圆角、阴影、hover / focus 和状态 pill，不使用卡片顶部彩色横条；豆奶、Token、云服务、生活和同行记保留 `secondary-page-head`，芭蕾因顶部栏已有页面名称，不再重复标题卡，只在下一节课上方保留低权重更新时间。hover 只增强边框、阴影和轻微上浮，必须保留组件原有背景，不能统一洗成纯白；每页保留自己的语义色与内容结构，不为了视觉统一改写数据契约或交互。
- Token 近期活动：Home `wide-short` 卡展示近 90 天每日 Token 活动热力格，替代原“当前主线”列表；顶部状态条仍保留 7 天 Token 小摘要。
- 市场涨幅：Home `mid-tall` 卡展示纳指100、标普500、上证指数、深证成指和创业板指的当前点位、涨跌幅和日内迷你走势；数据来自 `dash/data/market-indices.json`，由 `scripts/sync_market_indices.py` 或服务器 `runtime` 每 10 分钟刷新，前端不直接请求行情接口。
- 待推进：1-3 个近期应该移动的 Now / Next 动作；由 `dash/data/project-status.json` 从 `ROADMAP.md` 显式生成，这里不是完整 todo app，也不得包含 Done 项。
- Home 不再单独展示“今日记录”卡片；静态项目原则和边界说明进入规格、上下文或版本更新，真正的当天个人判断由顶部今日状态承载。
- 今日 Todo：Home 右侧只展示 personal-wiki 同步来的当天明确执行日期待办；以浏览器当天日期匹配 `due_at`，不混入过期未完成或无日期待办。v1 只读展示，不支持在 MaxNow 内编辑或标记完成。
- 系统状态：作为云服务页入口，用来快速判断机器是否健康；点击卡片进入“云服务”页查看“系统与托管”模块，其中包含 Host、站点域名、nginx、证书、部署版本、CPU、磁盘、内存和运行时间等完整服务器状态快照。`TLS / nginx` 不再作为单独任务卡展示，也不展示部署根目录、nginx 配置路径或采集器说明这类低频实现细节。
- 豆奶签到：Home 只展示每日签到摘要入口，第一排展示今日流量、今日豆丁和今日账号有效期延长时长，第二排展示累计签到天数、累计流量和累计账号有效期延长时长；不在 Home 放趋势图。点击卡片进入“豆奶”详情页。数据来自 `dash/data/dounai_checkin.json`。
- 芭蕾摘要：在 `home-lane-rail` 使用一张可点击的 `home-card-ballet` / `widget-wide`，最多显示下一节课的日期时间、课程 / 老师、正式 / 候补状态，以及本周进度或最近成功更新时间；历史列表、可约课程、图表、Session 和自动化技术细节不进入 Home。同步失败时保留最后成功内容并明确标记“数据过期”或“需重新登录”，不得显示成“暂无预约”。
- AI 前沿：Home 只保留一个 AI 前沿简报模块，由 Last-30 展示“最新发布 / 本周前沿 / 近 30 天关键进展”三组数据；三栏页面顶部只显示蓝色时间范围“最近 3 天 / 本周 / 近 30 天”，不重复显示黑色栏目名或栏目简介。新闻标题和摘要必须以中文事实为主，品牌、模型名和 API 名可保留英文；不要再单独铺一张重复的 AI 外部输入卡，也不承接杂项链接。
- personal-wiki 近期待办入口：Home `wide-tall` 卡只读展示近期未完成待办的前 4 条，并跳转到 personal-wiki；v1 不支持编辑或标记完成。完整数量只进入状态 pill，不允许用全部待办撑高首页。
- MaxNow 版本更新：Home 左侧内容流在外部输入下方展示当前可读版本号、部署说明和最近几条 `UPDATE_LOG.md` 更新摘要；版本号由根目录 `VERSION` 维护，格式为 `x.x.x.xx`。任何已完成的 Owner 可见或运维相关改动都必须升版本并刷新 `project-meta`：小 UI / 文案 / 布局调整、新增页面能力、新数据源和新自动化默认升最后两位；重要功能模块稳定落地升 patch；大版本阶段切换升 minor / major。

## AI 前沿简报

AI 前沿简报用于回答“最近真正发布了什么”，不是英文 RSS 搬运、客户案例列表或关键词观察报告。

- 默认更新时间：服务器本地时间 00:00。
- “最新发布”最多 3 条，本周和近 30 天只补充不重复的高信号事项。
- 优先模型正式发布、API / Agent 能力、定价与开放范围、重要开源发布和高价值研究；优先使用官方一手来源。
- 客户案例、合作新闻、泛企业采用、教育活动、普通 SDK 版本号和没有明确能力变化的工程文章不得挤占前沿简报。
- 可见标题必须是中文事实句，例如“OpenAI 正式发布 GPT-5.6”；摘要必须说明发布了什么、开放到哪里或具体能力变化，不得追加“关注它的影响”一类通用套话。
- 同一事件在“最新 / 本周 / 近 30 天”之间按主题去重，不能为了填满栏目重复展示。
- X / Twitter 可以用于早期信号，但不是硬依赖。
- 如果 X / Twitter 不可用，使用官方博客 / RSS、Hacker News、GitHub、Reddit、项目 release、研究机构等来源。
- 二级新闻站只作为补充验证。

## Token 页面

Token 页面只回答 Token 相关问题：

- 今天自然日使用量
- 包括今天的最近 7 天使用量
- 包括今天的最近 30 天使用量
- 全部已采集使用量
- total / input / output / cacheRead / cost
- Codex 已完成任务的活跃时长；按 `task_complete.duration_ms` 累计，不包含轮次之间的空闲时间
- 模型占比和会话消耗
- 最近 30 天每日 Token 折线图
- 可用时通过色阶呈现异常高消耗日期
- Home 近 90 天 Token 热力格可用时通过色阶呈现高消耗日期，鼠标悬浮展示日期和 token 数。

Token 真实数据按来源接入，并由统一总账合并展示：

- `dash/data/openclaw-usage.json` 保存 OpenClaw 的 input / output / cacheRead / total token、按天、按模型、按任务拆分，以及按 OpenRouter 价格折算的等价费用。
- `dash/data/codex-usage.json` 保存 Windows 兼容本机 Codex 的 input / output / cacheRead / total token、按天、按模型、按任务拆分；来源为本机 `.codex/sessions` 中的 `token_count` 事件。统计按相邻累计快照的正向增量和原始事件日期记账，同一会话树内必须去重分叉文件继承的历史，不导出 prompt / response 正文。
- `dash/data/codex-macos-usage.json` 保存 macOS 本机 Codex 的同类账本，来源为 macOS 本机 `.codex/sessions`，source 固定为 `codex-macos` / `Codex macOS`，避免覆盖 Windows 账本。
- `dash/data/codex-server-usage.json` 保存服务器 Codex 的同类账本；来源为服务器 `/root/.codex/sessions`，由 root cron 刷新，不导出 prompt / response 正文。
- `dash/data/token-usage.json` 保存合并后的统一 Token 总账，Token 页面优先读取这个文件。
- OpenClaw 源账本的 `pricingBasis` 必须标记为 `openrouter-equivalent`，不要把它当作真实扣费账单；Codex 源账本使用 `openai-api-equivalent`，统一总账使用 `mixed`。
- OpenClaw 费用使用 OpenRouter 等价估算；Codex 费用使用 OpenAI API 等价估算。两者都是估算口径，不等同于真实供应商账单或订阅账单。
- Token 上报采用固定小时周期：macOS launchd 每小时 `:00`，Windows Task Scheduler 每小时 `:02`，root 在服务器每小时 `:05` 刷新 OpenClaw / Codex server 源账本，ubuntu 在每小时 `:10` 拉取并发布统一总账。Windows 和 macOS 错开两分钟，避免同时向 `origin/main` 推送产生竞争。
- Windows Task Scheduler action 使用 `wscript.exe scripts/report_codex_usage_hidden.vbs`，由 VBS 以 window style 0 启动 `scripts/report_codex_usage.ps1`；macOS launchd 运行 `scripts/report_codex_usage.sh`。Windows 上报脚本只允许提交 `dash/data/codex-usage.*`，macOS 只允许提交 `dash/data/codex-macos-usage.*`。本机 Git 网络连接设置低速与 SSH keepalive 边界，计划任务最长运行 10 分钟，单次卡住不能占用后续小时周期。macOS 专用 clone 发生分叉时，只允许自动丢弃标题和文件边界均确认属于上报任务的本地生成提交，并基于最新 `origin/main` 重新生成；人工提交不得自动 reset。
- 服务器 `MAXNOW-TOKEN-SOURCE-REFRESH` 以 root 运行 `scripts/refresh_token_sources_on_server.sh`，统一总账由 `MAXNOW-TOKEN-USAGE-REFRESH` 运行 `scripts/refresh_token_usage_on_server.sh`。总账合并脚本继续保护服务器运行时 `openclaw-usage.*` / `codex-server-usage.*`，空备份不能覆盖非空账本。
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
dash/data/project-status.json
dash/data/project-status.js
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

`dash/data/dashboard.json` 负责人工个人状态、时间线、系统状态、历史 Token 字段、Home 天气卡和时间卡片的手动特殊日期列表。历史 `journal` 字段可保留为数据兼容，但 Home 不再读取它生成独立卡片；生成的主线和待推进事项不再存放在这里。

其中 `automation` 和 `system` 可以由 `scripts/sync_system_status.py` 自动更新；`system` 内的 `data-health` 项保存 11 个 Owner 可见数据源的状态摘要，`automation-failures` 项记录关键任务是否达到连续 3 次失败阈值。`today` 保留当天人工 override。Home 主状态默认由前端从今日 Todo、`project-status.*`、Token 和自动化信号推导，过期 `today` 不再作为主判断。

前端每次成功读取 JSON 后，在同源浏览器存储中保留该数据源的最后成功响应。后续请求失败时继续展示这份响应，并把来源状态标记为“请求失败”；如果从未成功同步则显示“尚未同步”。`.js` wrapper 继续由脚本生成并校验一致性，不再承担运行时请求失败的主要兜底职责。

`dash/data/project-status.json` 负责 Home 的项目主线和待推进事项，由 `python scripts/update_data.py project-status` 从 `ROADMAP.md` 的 Now / Next 显式生成。它必须记录 `sourceUpdatedAt`、`generatedAt`、`staleAfterHours` 和 ROADMAP 内容指纹；前端超过阈值时显示“待刷新”，并停止用过期项目状态生成 Today Status 推荐。`scripts/check.py` 必须验证数据仍匹配当前 ROADMAP，并拒绝指向 Done 的事项。服务器日常 `runtime` 和 OpenClaw 不得覆盖该文件或 `dashboard.today`。

`specialDates` 是可选数组，用于 Home 时间卡片的当天匹配和下一特殊日期计算。生日、纪念日等每年重复的固定公历日期写为：

```json
{ "month": 7, "day": 18, "title": "77 生日", "type": "birthday" }
```

也支持一次性日期：

```json
{ "date": "2026-07-18", "title": "重要纪念日", "type": "anniversary" }
```

每月重复的日期写为：

```json
{ "day": 25, "title": "Codex 续费日", "type": "renewal", "repeat": "monthly" }
```

如果提供 `startYear`，页面会在标题后显示周年数。当天没有命中时，第一行保持“今日无节日”的低干扰提示；下一行仍从内置节日和个人日期中选择最近的未来日期。

`weather` 是可选对象，用于 Home 顶部天气卡展示北京市海淀区的今日天气摘要：

```json
{
  "location": "北京市海淀区",
  "district": "海淀",
  "condition": "晴",
  "icon": "sun",
  "tempC": 22,
  "precipitationMm": 0,
  "rainMm": 0,
  "showersMm": 0,
  "highC": 35,
  "lowC": 23,
  "updatedAt": "2026-06-23 20:04",
  "source": "Open-Meteo / CMA",
  "sourceModel": "CMA GRAPES"
}
```

`icon` 支持 `sun`、`cloud`、`rain`、`storm`、`snow`、`fog`。北京天气使用 Open-Meteo 的中国气象局 CMA / GRAPES 模型，并保存当前 `precipitationMm`、`rainMm`、`showersMm`；当模型天气码仍为云而当前降水量大于 0 时，按雨或阵雨展示，避免正在降水时只显示阴天。页面只读取这些字段展示，不从浏览器端请求天气 API。日常刷新由 `scripts/sync_weather.py` 更新 `dashboard.json` 并重新生成 `dashboard.js`；服务器 `runtime` 定时任务会一并运行该刷新。

`dash/data/ai-news.json` 只负责首页展示用的外部 AI 输入，通常取 Last-30 外部信号中的 0-3 条高相关内容。

`dash/data/last-30.json` 负责 AI 外部信号滚动记忆，不记录 MaxNow 内部项目流水。它保存今天、本周和近 30 天的 AI 新闻、模型 / API / agent / 开发者工具 / 成本 / 开源研究变化，以及这些变化对 Owner、MaxNow、Codex、OpenClaw 或模型选择的潜在影响。

`dash/data/wiki-todos.json` 负责 personal-wiki 近期待办的只读缓存，由 `scripts/sync_wiki_todos.py` 从 personal-wiki `wiki/tasks/todo.json` 生成。

`dash/data/openclaw-usage.json` 负责 OpenClaw 用量账本，由 `scripts/sync_openclaw_usage.py` 从服务器 `/root/.openclaw/agents/main/sessions/*.trajectory.jsonl` 等只读轨迹生成。它记录北京时间日桶、模型、任务、input / output / cacheRead / total token，并按 OpenRouter 模型价格生成等价费用估算。该费用不是实际供应商账单。

`dash/data/market-indices.json` 负责 Home 市场涨幅卡片，由 `scripts/sync_market_indices.py` 从腾讯公开行情接口生成。它只保存指数名称、符号、区域、当前点位、昨收、涨跌额、涨跌幅、更新时间、来源 URL 和压缩后的日内走势点；前端只读展示，不直接请求第三方行情接口。服务器 `runtime` 每 10 分钟会一并刷新该数据，接口失败时脚本优先保留旧缓存并标记 `stale`。

`dash/data/project-meta.json` 负责 MaxNow 自身版本和版本更新展示，由 `scripts/sync_project_meta.py` 从 `VERSION`、Git 状态和 `UPDATE_LOG.md` 生成；页面只读展示，不在前端修改版本号。`VERSION` 采用 `x.x.x.xx` 格式，例如 `1.0.0.00`。

版本号执行规则：

- 小 UI / 文案 / 布局调整：升最后两位，例如 `1.0.0.00` -> `1.0.0.01`。
- 新增页面能力 / 新数据源 / 新自动化：升最后两位，例如 `1.0.0.01` -> `1.0.0.02`。
- 重要功能模块稳定落地：升 patch，并把最后两位归零，例如 `1.0.0.12` -> `1.0.1.00`。
- 大版本阶段切换：升 minor 或 major，并重置后续位。
- 每次升版本后必须运行 `python scripts/update_data.py project-meta`，让 Home / 系统状态里的 MaxNow 版本同步到前端数据。

`dash/data/dounai_checkin.json` 负责豆奶每日签到记录、账号余量快照、账号日均可用历史和真实流量使用记录，由 OpenClaw / root 侧豆奶自动化更新；前端只读取流量、豆丁、账号有效期延长时长、累计签到天数、近 30 天 records、剩余可用流量、有效期、每日可用预算、`account_history`、`traffic_usage` 和 `traffic_usage_history`，不编辑、不回写，也不修改签到脚本或 cron。

账号余量快照每天优先从现有专属订阅响应的标准 `subscription-userinfo` header 读取精确到字节的 `total`、`upload` 和 `download`，用 `total - upload - download` 生成 `remaining_flow_bytes`，再换算 `remaining_flow_mb`。日均可用预算使用快照时刻到有效期的精确剩余时长：`remaining_days_exact = remaining_seconds / 86400`，`daily_available_mb = remaining_flow_mb / remaining_days_exact`；`days_remaining` 只保留为整天摘要，不得再作为日均预算分母，避免有效期延长后整天数未变化造成锯齿式假下降。成功时 `remaining_flow_precision` 固定为 `byte`，`source` 标记为 `dounai.pro/subscription-userinfo`；订阅地址、查询参数和令牌不得写入日志、数据文件或前端。只有精确响应头不可用时，才允许降级解析用户面板两位 TB / GB 标签，并把 `remaining_flow_precision` 标记为 `rounded-label`。`account_history` 从 2026-07-21 起保存同样的余量精度字段，从 2026-07-26 起保存 `remaining_days_exact`；更早的粗略历史不伪造精确值。

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

MaxNow 需要一层滚动记忆，用来保存最新、本周和最近 30 天的 AI 前沿发布。它不是内部项目日志，也不是泛新闻流；只保留模型、API、Agent、开发者工具、成本和重要研究的实质变化。

已新增：

```text
dash/data/last-30.json
dash/data/last-30.js
openclaw/last-30/SKILL.md
```

Last-30 负责：

- 最新发布：显示最近 3 天最重要的 1-3 条正式发布；没有当天内容时允许回退，但不能把旧内容标成“今日”。
- 本周前沿：只补充最新发布未覆盖的本周模型、API、Agent、开发者工具、成本、开源和研究变化。
- 近 30 天关键进展：展示仍值得补看的具体发布或研究，不再展示 `active`、候选数量和关键词自动归类报告。
- 中文事实摘要：保留官方原文链接和可审计的 `originalTitle`，但页面只展示中文事实标题和中文简述。
- 等待观察：还不确定、需要继续追踪或需要 Owner 确认是否重要的信号。

更新原则：

- 优先使用免费公开源：官方博客 / RSS、GitHub releases、Hacker News、Reddit / 公开社区、arXiv、GDELT 或类似免费索引。
- X / Twitter 不是硬依赖；只有 Owner 明确批准付费 API 和博主白名单后才接入。
- 先用脚本抓取标题、摘要、链接和时间，做本地关键词过滤和去重；不要把大量全文直接喂给模型。
- 排序必须区分“正式产品 / 模型发布”和“客户案例 / 合作 / 泛采用”；品牌关键词出现次数不能代替事件重要性。
- SDK release、普通 GitHub 开源更新和底层工程文章只能作为开发者生态补充；纯版本号和 updated packages 不得进入可见简报。
- 可以让 OpenClaw 对少量候选做二次筛选和压缩，但应控制在 10-20 条候选内。
- 每条记录尽量保存 `source`、`sourceType`、`confidence`、`needsOwnerConfirm` 和 `originalTitle`；前端只展示来源与日期，不外露内部置信度、自动观察或归类状态。
- 自动化可以起草事实和影响摘要，但重要判断最终由 Owner 确认。

## 已确认方向：芭蕾学习模块

MaxNow 的芭蕾能力定位为 Owner 的个人学习模块，而不是单独的抢课工具。它要持续回答五个问题：

1. 下一节课是什么，是否已正式预约或仍在候补？
2. 本周计划上几节、已经完成几节、预计训练多久？
3. 过去实际上过哪些课，课程、级别和老师分布如何？
4. 当前学习重点、老师纠正和下次练习事项是什么？
5. 课程数据、登录态和约课自动化是否可信、是否需要人工处理？

页面边界：

- v1 新增独立 `secondary-view` 页面“芭蕾 / 课程与进度”，导航固定放在 Token 与云服务之间。
- 芭蕾内容不并入“生活 / 吃啥”。生活页继续承载低负担临时工具，芭蕾页承载长期学习记录、课程计划和受控自动化。
- Home 最多保留一张紧凑入口卡，只显示下一节课、预约 / 候补状态、本周进度和数据新鲜度；完整课表、上课历史、学习笔记和自动化日志留在芭蕾页。
- Cloud 页面只展示同步任务和 Session 探针的运维健康，不复制课程与学习业务数据。

只读 MVP 信息结构：

- 页面页头：数据截至时间、最近同步结果和是否需要重新登录；不展示 Cookie、Session 指纹、服务单元名或日志路径。
- PHPSESSID 活跃实验：在芭蕾页展示一张脱敏状态卡，主值为截至最后一次 `authenticated` 样本的“已确认有效时长”，并展示原始实验起始、最近自动检查、下一次自动检查和当前检查间隔。该卡只能写“自动检查 / 只读探针”，不能称为“自动续期”；失败或停止后必须冻结在最后成功证据，不能按浏览器当前时间继续外推。服务器每 5 分钟发布一次本地脱敏状态；即使 JSON / localStorage 仍可读，只要 `updatedAt` 超过 15 分钟未更新，前端也必须从绿色运行态降级为检查延迟。
- 下一节课：日期、周几、起止时间、课程、级别、老师、正式预约 / 候补状态、距离开课时间和可取消截止时间。源文案为“课前 N 小时可取消”时，必须以开课时间减去 N 小时计算绝对截止时间；无法可靠解析时保留并显示源文案，不能拼出不完整的“可取消至 前可取消”。
- 本周训练：使用独立全宽面板展示本周已完成、已预约、候补、预计节数和对应时长；预计采用“正式预约”为下限、“正式预约 + 候补”为上限，不能把候补直接算成一定会完成。
- 课程卡：使用独立全宽面板展示卡名、开卡日期、开卡第几天、剩余 / 总课次、已用课次、有效期和同步时间，不内嵌进预约或上课统计。每张卡独立使用自己的有效期和已用课次，不能用全局上课记录推断某张卡的消耗。每天以剩余课次 / 剩余有效周数计算到期前所需周频率，并展示“按建议整数周课次预计何时用完”和“若每周 1 节到期约剩多少”的计划情景。开卡未满 28 天时不展示实际节奏、能否用完或增量结论；满 28 天后才按该卡开卡以来的 `已用课次 / 实际开卡天数` 补充实际节奏预测。不得展示会员卡号、会员 ID 或源记录 ID。
- 上课统计：使用一张统一面板提供“本月 / 今年 / 全部”和“节数 / 时间”切换；主值、课程类型、课程级别和趋势图必须同步采用同一时间范围与指标。时长的权威值始终保存为整数分钟，小时只在展示层换算，避免累计浮点误差；源记录无法确认时长时仍可计入节数，但不得猜测小时，并显示“有 N 节待补时长”。
- 未来课程：芭蕾页最顶部使用两个同级独立 tab，左侧为标题 / 同步信息，右侧为紧凑“下一节预约”，宽桌面各占约 1/2 且同顶、同底、等高，不允许把右侧模块嵌套进左侧标题卡；右侧 tab 按“紧凑日期 / 弹性课程信息 / 状态”三段自适应分配宽度，标题与课程信息共用左基线，不使用固定宽度内容块强行居中；视口不超过 `1200px` 时两个 tab 自然堆叠，避免课程信息被半宽卡片压缩。独立“所有预约”列表同时完整展示所有尚未上课的已预约 / 排队中课程，包括顶部右侧的下一节，不显示已取消或已经结束的课程。列表的日期列上下展示日期与真实星期，课程列只保留时间和老师；“已预约”使用粉玫瑰色，“候补”使用橙色并在存在序号时显示“排队第 N 位”，不能只写笼统的“排队中”。后续按周扩展可预约、满员和已取消状态；剩余名额必须标记为抓取时快照，不能当作持续有效承诺。
- 上课记录：与预约记录分开，只将闻道明确表示已上课 / 已完成的记录计入统计；按日期、课程、级别、老师、起止时间和时长查看原始明细。
- 课程细分使用两条正交维度：`courseType` 至少区分芭蕾、软开、肌肉素质、技术技巧和其他，`level` 至少区分 L1、L1.5、L2、L3、L4 和无级别。保留原课程名；`L1.5` 必须先于 `L1` 匹配。“芭蕾 L1.5”同时计入芭蕾课型与 L1.5 级别，“软开专项”计入软开与无级别，不能强塞进单一类别。
- 学习趋势：一张全宽折线图，提供“月 / 年 / 全部”周期和“节数 / 小时”指标切换，不使用双 Y 轴。月视图按日、年视图按月、全部视图按月或年展示，缺失月份补零，图例和单位随指标切换。
- 课程分布：在统一上课统计面板中用水平条展示所选时间段内的级别 / 课型分布；切换节数 / 时间时，分类值与条形长度同步切换。浏览器读取预聚合结果，不在每次切换时重新扫描全部历史。
- 学习记录：阶段目标、课堂重点、老师纠正、动作标签和下次练习事项；身体状态属于可选敏感信息，不进入 Home。
- 预约自动化：只在页面底部展示 `off` / `dry-run` / `enabled`、下一计划和最近结果的 Owner 可读摘要，完整运维状态留在 Cloud。

缓存、同步与去重：

- 闻道 H5 是课程表、当前预约、候补、上课记录和会员课次事实的外部来源。
- Owner 明确补录且闻道不存在的课程可以作为 `manual` 记录写入服务器私有 canonical ledger；手工记录使用独立稳定键，参与实际上课统计，并在前端历史中标记“手动添加”。闻道全量校验不得因源站缺失而 tombstone 手工记录。
- personal-wiki 是学习目标、课堂笔记、练习记录和 Owner 人工判断的长期来源；MaxNow 只读同步，不在前端回写。
- 服务器私有目录维护一份 canonical attendance ledger，建议路径为 `/var/lib/maxnow-ballet/attendance-ledger.json` 且权限为 `0600`；它保存用于去重的源记录 ID，不进入 Git 或前端。第一次成功同步全量回填历史，之后每天只重扫最近 60 个逻辑日并执行 upsert；每月 1 日 00:47 进行一次全量校验，防止旧记录补录或状态回改。
- 去重键优先级固定为：闻道上课记录 ID → 预约 / 课程实例 ID → `场馆 + 日期 + 起止时间 + 规范化课程名 + 老师` 的哈希。兜底键发生碰撞时同步失败并等待人工确认，不得静默覆盖；出勤状态等可变字段不进入稳定键。若课程名或老师更正导致兜底哈希变化，先用场馆、日期和起止时间寻找唯一旧场次并记录 alias；匹配不唯一时停止合并，不能生成重复历史。
- 另用 `/var/lib/maxnow-ballet/sync-state.json` 保存每次同步尝试结果；失败只能原子更新这个状态文件，不能改成功账本。未来预约 / 下一节课使用独立 `/var/lib/maxnow-ballet/booking-snapshot.json`，课程卡使用独立 `/var/lib/maxnow-ballet/membership-snapshot.json`，二者都不混入 attendance ledger。课程卡快照只保存脱敏课程卡名称、有效期和课次数值，不保存会员卡号、会员 ID 或源记录 ID。
- 逻辑日以 `Asia/Shanghai` 的 00:00 为界，生产日常任务目标为 00:17 运行并结算前一日 23:59:59 前的数据，避开服务器现有 00:00、00:05、00:10 任务并给源站留出入账时间。任务使用单实例锁、有限网络重试；身份失效不重试。当前实验已因身份失效停止，生产任务继续保持未启用，直到凭据安全刷新、首次只读验证通过且 Owner 单独批准。
- 00:17 任务同时刷新当前预约、候补、上课记录和课程卡快照；预约默认 TTL 为 36 小时，成功后记录 `dataAsOf`，失败继续保留上一份并按年龄标记 stale。每月 1 日 00:47 执行全量校验。后续受控约课任务若真实改变预约，必须在结束后刷新该快照；页面打开本身永远不刷新。可约课程属于另一份短期源数据，不纳入历史统计，也不承诺由午夜任务保持实时。
- 日常增量只重算受影响月份、年份和全局累计；前端直接读取预聚合的 `monthly` / `yearly` 序列。课程归类规则带 `classificationVersion`，规则变化时可以从本地账本重新归类，不需要重新请求闻道。
- 每次成功账本写入先校验 schema、稳定键唯一性、记录数和累计分钟，再通过临时文件原子替换。同步失败时不得清空或覆盖上次成功的 records、summary、aggregates 和 `dataAsOf`，只原子更新 `sync-state.json`。
- 全量校验中一次未返回的旧记录先标记为待确认，不立即删除；只有连续两次成功全量校验都缺失，且源站语义确认不是分页 / 查询范围问题后，才能进入 tombstone，避免短暂漏页让历史课时倒退。
- 如果闻道接口实际上只支持全量历史查询，可保留每日全量 GET，但仍必须通过本地 ledger 做幂等 upsert、差异计算和增量聚合，避免重复记录和前端重复计算。

数据契约与状态：

- `dash/data/ballet.json` / `dash/data/ballet.js` 是脱敏 read model；前端只读取它们，不接触服务器私有账本或闻道身份。
- `dash/data/ballet-session.json` / `dash/data/ballet-session.js` 是本地与 Git 的安全 fallback；生产同 schema 文件由非 root 发布器写入 `/var/lib/maxnow-ballet-session-status/public`，nginx 仅在已有登录校验后映射到 `/data/ballet-session.*`。它与课程 `ballet.*` 分离，只保存状态、实验 / 阶段起始、最近检查 / 最近认证 / 下次检查、计划截止、间隔、已验证秒数、样本数、是否观察到轮换 / `Set-Cookie` 和受控错误；不得保存 Session 值或指纹、run ID、unit / 日志路径、URL、响应摘要 / 正文或凭据版本。
- read model 至少区分 `schemaVersion`、`timezone`、`dataAsOf`、`sync`、`classification`、`summary`、`week`、`membership`、`records`、`aggregates`、`upcoming`、`learningLogs`、`authHealth` 和 `automation`；预约状态和上课状态不得混为一类，`classification` 同时保存 `courseType` 与 `level` 规则版本。
- `sync` 至少记录 `logicalDate`、`lastAttemptAt`、`lastSuccessAt`、`lastDataChangeAt`、`lastAttemptStatus`、`cacheState`、`consecutiveFailures`、安全的 `errorCode` / `errorMessage`、抓取窗口和本次源记录 / 合并记录数。
- `cacheState` 只描述最后成功缓存的可用性：`fresh`、`stale`、`unavailable`；`lastAttemptStatus` 只描述本次尝试：`success`、`auth_required`、`network_error`、`source_changed`、`parse_error`。页面必须组合表达两者，例如“本次授权失效；仍显示 7 月 25 日缓存”，不能把错误类型和新鲜度混成一个状态；连续 3 次失败再升级为 Cloud / 系统异常。
- 运行日志只记录时间、状态、耗时、页数、记录数、变更数和安全错误码；不得记录 Cookie、OAuth、完整 URL 参数、会员标识或原始响应正文。
- 采集器只允许已确认的只读 GET 页面；禁止调用预约、取消、候补、转课、登录写接口或未知方法。日常同步计划为北京时间 00:17；固定间隔实验已经结束，但旧凭据已失效，因此仍不得启用，必须先安全刷新凭据并完成一次 Owner 批准的只读验证。
- 生产凭据使用服务器 host-bound systemd 加密凭据与 `LoadCredentialEncrypted` 注入；`PHPSESSID` 不得进入 Git、日志、前端、聊天、环境变量或命令参数。身份失败后保留最后成功缓存并停止重试，直到检测到安全的凭据版本变化；页面只显示脱敏错误和“请在电脑微信重新登录并刷新凭据”。
- 前端永远不直接访问闻道，不保存 Cookie，不提供 Session 输入框，也不允许由页面打开、刷新或按钮点击触发真实预约。
- “维护一个文档”在实现上以单一 JSON 账本为权威，不每天重写一份可手改 Markdown。若以后需要人类可读的芭蕾档案，只允许从账本单向生成 Markdown 摘要，不能形成第二份可编辑事实源。

自动约课只作为后续受控能力：

- 默认模式为 `off`；先实现只读同步，再实现只产生预计动作的 `dry-run`，最后才评估由 Owner 单独批准的 `enabled`。
- dry-run 至少连续覆盖两次周日课表发布，并与 Owner 的人工选择完全一致后，才允许真实提交。
- 真实提交前必须重新校验课程、会员卡、已有预约、时间冲突、每周上限和候补规则；使用幂等账本与有限重试，禁止无限抢课。
- 默认不自动取消、转课、买卡、支付或报名付费活动；遇到验证码、微信重新授权、页面结构变化或无法判断的响应时立即停止。
- `PHPSESSID`、Cookie、OAuth code、openid、unionid、memberId、手机号、会员卡号、原始响应正文和真实执行参数不得进入 Git、前端、日志、备份或聊天；只能进入服务器隔离凭据和最小权限运行态。

验收标准：

- Owner 能在 5 秒内确认下一节课、本周计划和预约状态。
- 当前预约与实际上课记录分别与闻道保持一致，无重复、无错课。
- 相同源数据重复同步后，历史节数、累计分钟和月 / 年聚合完全不变；对最近 60 日的补录或修改能在下一次成功同步后正确 upsert。
- Owner 可切换任意月份或年份查看实际上课节数、小时和课程分布，折线图不因空月份断裂或产生双轴歧义。
- Owner 能看到 PHPSESSID 从当前实验起点到最后一次成功样本的已确认有效时长、最近 / 下次自动检查和当前间隔；当前 v6 使用 20 分钟，只读页面不会把“持续活动仍有效”误写成“已经证明滑动续期”。
- 每项数据都有可信更新时间；失败时最后成功数据仍可查看且明确标旧，不会被当作实时数据。
- 自动化阶段保持零重复预约、零错误课程、零未经确认的取消 / 转课；身份异常时 fail closed。

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

- Dash 业务内容与 Blog 保持静态，不引入数据库或业务 API；`dash.maxnow.cn` 使用 MaxNow 自定义登录页和服务器本机 Cookie 认证服务保护，`blog.maxnow.cn` 继续公开。
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
- v1 的 Dashboard 业务内容保持静态，不加数据库或业务 API；唯一后端是仅供 nginx 调用的最小认证服务，用于校验密码和签发 HttpOnly 会话 Cookie。
- 任何新的日常维护数据字段，都必须同时写进这里和 OpenClaw skill。
- 页面代码变化需要 Codex 或 Owner 明确意图；OpenClaw 永远不能改变页面结构。
