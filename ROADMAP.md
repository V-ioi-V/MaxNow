# MaxNow 路线图

这个文件记录 MaxNow 接下来真正要推进的事情。

它不是灵感池，也不是更新历史：

- 新想法先放进 `IDEAS.md`。
- 已确定的产品规则放进 `SPEC.md`。
- 代理接力上下文放进 `CONTEXT.md`。
- 已发生的重要变更放进 `UPDATE_LOG.md`。
- 当前要做、下一步要做、暂时卡住的事放在这里。

## 更新规则

- 每次开始一组新工作前，先看这里。
- 做完一项后，把它从 `Now` 或 `Next` 移到 `Done`，并在 `UPDATE_LOG.md` 记录重要变更。
- 如果一项需要 Owner 权限、服务器权限或外部信息，放进 `Blocked`。
- 不要把聊天里的临时判断长期留在这里；只记录可执行任务和阶段路线。

## Now

### 规划个人博客发布链路

- 建议分支：`feature/blog-module-plan`
- 公开博客使用 `blog.maxnow.cn`，不要放进 `dash.maxnow.cn/blog`，也暂时不新买独立域名。
- 内容源使用 private personal-wiki 的 `raw/blog-vioiv`：当前已归档旧 Hexo Markdown 211 篇，图片缓存 167 个。
- MaxNow 仓库负责发布层：构建脚本、公开文章数据、静态页面、归档、标签、RSS、部署说明和 dashboard 发布状态入口。
- `dash.maxnow.cn` 继续作为私人状态工作站；最多显示博客发布进度、待筛选数量和跳转入口，不承载完整博客阅读体验。
- `dash.maxnow.cn` 顶部右侧已预留 `Blog` 弱外链，指向 `https://blog.maxnow.cn`；左侧导航只保留 Dash 内部页面：首页、豆奶、Token、云服务、生活、同行记。
- 第一阶段先做只读静态博客：筛选 public/published 文章，转换 front matter，复制必要图片，生成 `blog.maxnow.cn` 页面。
- 首页预览页：`blog/index.html`，用于确认文章流首页的信息架构和视觉风格，首页按文章预览卡片持续向下浏览。
- 文章 cell 交互：整张文章卡片都可点击进入文章详情，桌面端文章流按一行两篇展示。
- 专题索引页：`blog/topics.html`，用于确认分类总览。
- 专题分类二级页：`blog/topic-*.html`，用于确认点击分类后查看该分类文章、细分标签索引、按标签分组文章和返回专题索引的浏览方式。
- 归档总览页：`blog/overview.html`，作为左侧独立 tab 展示原始文章数、缓存图片数、专题分类数和发布状态；不要把这些统计放成左栏信息卡。
- 方案说明页：`blog/preview.html`，用于保留博客发布链路和边界说明，不作为正式线上入口。

## Next

### 让 Last-30 免费 AI 信号稳定运行

- 当前已新增 `scripts/sync_ai_last30.py`，并已接入服务器 `MAXNOW-AI-LAST30-SYNC` 每天 00:00 自动刷新 `dash/data/ai-news.*` 和 `dash/data/last-30.*`。
- 观察免费源稳定性：官方 RSS / 博客、GitHub releases、Hacker News、GDELT、arXiv。
- 如果某些免费源长期失败，再替换成更稳定的 RSS 或项目 release 源。
- X / Twitter 暂不接入；只有 Owner 明确批准付费 API 和博主白名单后再做。
- 后续可让 OpenClaw 对脚本筛出的 10-20 条候选做二次摘要，但不要把全文大量喂给模型。

### 设计手机端 OpenClaw 更新 personal-wiki 链路

- 来源 ID：`maxnow-openclaw-sync`
- 建议分支：`feature/wiki-openclaw-sync`
- 方案文档和数据归属策略留在 personal-wiki；MaxNow 仓库负责实现与展示相关的接口、入口和服务器侧操作说明。
- 明确手机端如何触发 OpenClaw 记录 / 更新待办，以及 OpenClaw 如何受控操作同服务器上的 MaxNow。
- 先形成最小闭环：记录待办、同步到 personal-wiki、MaxNow 读取或跳转查看。

### 让噗噗每日提醒 personal-wiki 待办

- 来源 ID：`maxnow-pupu-daily-todo-reminder`
- 建议分支：`feature/pupu-daily-todo-reminder`
- 尝试让服务器上的噗噗 / OpenClaw 每天通过 cron 汇总 personal-wiki 当天或近期未完成待办，并主动提醒 Owner。
- 先确认提醒渠道、发送时间、消息格式和失败日志位置；真实发送消息前需要 Owner 明确确认发送目标和内容边界。
- 数据源优先复用现有 `scripts/sync_wiki_todos.py` / `dash/data/wiki-todos.*`，避免前端或 cron 直接暴露 private personal-wiki 权限。

### 补充访问控制和隐私策略

- 选择 v1 的保护方式：Basic Auth、VPN、IP 限制、反代鉴权或其他方式。
- 明确 HTTPS / 域名 / 反代配置。
- 更新 `DEPLOY.md`。

## Later

### 桌面伴随入口

- macOS：顶部状态栏 app，点击后出现下拉个人面板。
- Windows：桌面壁纸式个人看板，作为平静常驻的状态层。
- 两个平台尽量复用 `dash/data/*.json` 的同一套数据契约。

### 公开 MaxNow 主页或灵感宇宙

- 仅在私人工作站稳定后再考虑。
- 不要让公开表达影响 `dash.maxnow.cn` 的私人状态工作站定位。

## Blocked

### personal-wiki 待办接入待确认

- 是否只读展示，还是允许从 MaxNow 进入后编辑 / 标记完成。
- MaxNow 仓库内开发待办采用 issue、Markdown、JSON 还是其他机器可读格式，并如何与 personal-wiki 待办在界面上区分。

### personal-wiki / OpenClaw 同步策略待确认

- OpenClaw 更新 personal-wiki 时采用直接 commit、PR，还是其他受控写入方式。
- 手机端触发更新时的权限、回滚和失败提醒方式。
- 同服务器上的 MaxNow 被 OpenClaw 操作时，哪些动作允许自动执行，哪些必须 Owner 确认。

### 个人博客模块待确认

- 第一批公开文章清单待 Owner 确认：哪些适合直接公开，哪些只保留归档，哪些需要改写成长期 wiki 知识页。
- 旧文章 front matter 规范待定：是否在 personal-wiki 原文里直接补 `visibility` / `status`，还是由 MaxNow 维护一个独立发布清单。
- 博客是否需要评论、订阅邮件、搜索索引、统计分析等公开站能力待后续确认；第一阶段先不做。

## Done

### 已收紧 Last-30 首页外露口径

- 2026-07-05 根据 Owner 对截图的确认，将 Last-30 左栏从 `Today` 改为 `Latest` / “最新信号”，避免把最近 7 天回退数据误读成当天信号。
- 前端不再展示 `high confidence`，改为“来源较稳 / 自动观察 / 待核实”等来源口径，避免把脚本判断误读成事实确认。
- 近 30 天主线文案改为“当前候选中约 X 条相关信号”，明确它是关键词自动归类，不是完整趋势统计。

### 已完成豆奶真实流量日结和前端展示

- 2026-07-05 只读检查豆奶用户区后确认：`/user/trafficlog` 页面直接提供最近 7 天真实使用量，`/user/trafficlog?ajax=1` 提供近 12 小时节点活跃 / 流量占比明细。
- 已在服务器备份 `/root/.openclaw/gen_checkin_data.py` 到 `/root/.openclaw/gen_checkin_data.py.bak-20260705-traffic-usage`，并扩展生成脚本。
- 已在服务器继续备份 `/root/.openclaw/gen_checkin_data.py` 到 `/root/.openclaw/gen_checkin_data.py.bak-20260705-traffic-closeout`，新增 `--traffic-only --exclude-today` 模式。
- root crontab 已新增 `MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT`：每天 00:05 只刷新昨天及更早的真实流量使用量，避免当天 00:05 的不完整值污染历史。
- 线上 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json` 已新增 `traffic_usage` 和 `traffic_usage_history`；每天 9 点签到任务仍可刷新账号快照，00:05 日结任务负责真实使用量口径。
- 豆奶详情页已新增“近 30 天实际使用流量”图，放在“近 30 天日均可用流量”前面，前端默认排除当天。
- 云服务 tab 已补充豆奶 09:00 签到和 00:05 traffic closeout 两个 root 定时任务。
- 云服务 tab 已移除顶部重复摘要卡；Host 信息合并进“系统状态”模块，任务频率保留在各自详情卡中。
- 云服务 tab 已进一步收敛为“系统与托管”后自然排列任务卡：TLS / nginx 不再单独占任务卡，也不再插入独立“定时任务”标题；系统列表保留 Host、站点域名和运行状态，隐藏部署根目录、nginx 配置路径、托管检查采集器说明等低频实现细节。

### 已完成的 Codex Token 本地与服务器统计

- 新增 `scripts/sync_codex_usage.py`，只读 `.codex/sessions` 的 `token_count` 事件，生成 `dash/data/codex-usage.*`。
- 新增 `dash/data/codex-server-usage.*` 和 `python scripts/update_data.py codex-server-usage`，用 `codex-server` 来源 ID 读取服务器 `/root/.codex/sessions` 并生成独立服务器 Codex 账本。
- 新增 `scripts/sync_token_usage.py` 和 `dash/data/token-usage.*`，将 OpenClaw 与 Codex 源账本合并为统一 Token 总账。
- Token 页面优先读取统一总账，保留 1d / 7d / 30d / all、来源费用面板、模型占比、最近调用和 30 天趋势，并显式区分 OpenClaw、Codex Windows / macOS、Codex server；来源费用跟随当前范围更新。
- `scripts/update_data.py codex-usage` 会刷新本机 Codex 源账本、统一总账和 wrapper；`scripts/update_data.py codex-server-usage` 会刷新服务器 Codex 源账本、统一总账和 wrapper；`scripts/update_data.py token-usage` 可单独合并现有账本。
- 新增 `scripts/report_codex_usage.ps1`、`scripts/report_codex_usage_hidden.vbs` 和 `scripts/install_local_codex_usage_task.ps1`，将本机 Codex 用量接入 Windows Task Scheduler 定期上报；默认每 1 小时通过 `wscript.exe` 无窗口刷新本机账本、提交并推送 usage 数据，再让服务器只合并现有 Token 总账。
- 服务器 root crontab 接入 `MAXNOW-CODEX-SERVER-USAGE`，每天 00:40 通过 `/tmp/maxnow-codex-server-usage.lock` 刷新服务器 Codex 用量，日志写入 `logs/codex-server-usage.log`。

### 已完成的同行记入口

- 左侧导航新增“同行记”tab，副标题为“我和 Ricky”，放在最后一个一级入口。
- 新增只读页面展示真实地图和统计卡片，地点与旅行记录暂时只进入地图 marker / popup，不单独铺列表。
- personal-wiki 新增 `wiki/relationships/ricky-travel.json`，从 `wiki/relationships/ricky.md` 抽取旅行、出游、地点和待确认日期。
- 新增 `scripts/sync_ricky_travel.py` 和 `python scripts/update_data.py ricky-travel`，把 personal-wiki 的结构化旅行数据同步成 `dash/data/ricky.json` / `dash/data/ricky.js`。
- `scripts/update_data.py wrap all` 和 `scripts/check.py` 已纳入 `ricky` wrapper 校验；当前同步得到 12 个地点和 4 条记录。

### 已完成的生活入口和吃啥工具

- 左侧导航新增“生活”tab，副标题为“吃啥”，放在云服务和同行记之间。
- personal-wiki 新增 `wiki/life/food-picker.md`，当前候选为粉面菜蛋、红烧牛肉面、满小饱肥汁土豆粉、糟粕醋米粉。
- 新增 `scripts/sync_life_foods.py` 和 `python scripts/update_data.py life-foods`，把 personal-wiki 菜品清单同步成 `dash/data/life-foods.json` / `dash/data/life-foods.js`。
- 生活页“吃啥”默认全选候选、数量默认 1，可临时取消勾选并随机选取一个或多个不重复结果；`runtime` 和 `scripts/check.py` 已纳入 `life-foods` 校验。

### 已完成的近期界面微调

- Home 时间卡片支持 `dashboard.json.specialDates` 手动特殊日期列表，可在当天显示生日、纪念日等轻量提醒；没有命中时保持“今日无节日”。
- 收窄 Dash 左侧导航栏桌面宽度，保持首页 / 豆奶 / Token 三个入口清晰，不新增折叠交互。

### 已完成的结构整理

- 将 dashboard 页面代码移动到 `dash/`，包括 `dash/index.html`、`dash/styles.css`、`dash/app.js` 和 `dash/data/*`。
- 将博客方案预览移动到 `blog/preview.html` 和 `blog/preview.css`，作为 `blog.maxnow.cn` 发布层工作区的起点。
- 根目录 `index.html` 改为本地开发入口，只负责跳转到 Dash 和 Blog Preview，不再作为线上 dashboard 本体。
- 更新 `scripts/check.py`、`scripts/sync_wiki_todos.py` 和 `scripts/sync_system_status.py`，以 `dash/data/*` 为运行数据路径。
- 明确当前仍采用单 GitHub 仓库，不拆 repo；根目录 MD 文件继续承担项目级规则、规格、路线图、上下文、想法、更新记录、部署和服务器操作说明。

### 已完成的基础能力

- 新增 `scripts/sync_ai_last30.py` 和 `python scripts/update_data.py ai-last30`，用免费公开源刷新 AI 外部输入和 Last-30 AI 外部信号滚动记忆；采集脚本本身不调用模型，不消耗 token。
- 服务器已通过 `ubuntu` 用户 crontab 接入 `MAXNOW-AI-LAST30-SYNC`：每天 00:00 自动运行 `python3 scripts/update_data.py ai-last30`，日志写入 `logs/ai-last30.log`。
- 新增 `scripts/sync_openclaw_usage.py` 和 `dash/data/openclaw-usage.*`，可从 OpenClaw trajectory 解析 input / output / cacheRead / total token，按北京时间日桶、模型和任务聚合，并按 OpenRouter 价格生成等价费用估算；数据结构预留 Codex 来源接入。
- Token 页面已接入 OpenClaw 用量账本，支持 1d / 7d / 30d / all 范围切换、总量 / 输入 / 输出 / 缓存读 / 费用、模型占比、会话消耗和最近 30 天折线趋势。
- 服务器 root crontab 已接入 `MAXNOW-OPENCLAW-USAGE`：每天 00:20 刷新 OpenClaw 用量并合并 Token 总账，2026-07-05 复查确认最近三次自动运行均成功。
- 新增 `VERSION`、`scripts/sync_project_meta.py` 和 `dash/data/project-meta.*`，Home 可展示 MaxNow 当前版本和最近更新摘要；版本号采用 `x.x.x.xx` 格式。
- 服务器已安装并授权 GitHub CLI，账号 `V-ioi-V` 可读取 private personal-wiki；已验证服务器能读取 `wiki/tasks/todo.json` 并运行 `scripts/sync_wiki_todos.py`。
- 服务器已通过 `ubuntu` 用户 crontab 接入 `MAXNOW-DASHBOARD-SYNC`：每 10 分钟运行 `python3 scripts/update_data.py runtime`，日志写入 `/var/www/maxnow-dashboard/logs/`。
- 新增 `scripts/update_data.py` 作为统一数据更新入口，支持 `runtime`、`project-status` 和 `wrap all`；服务器 cron 改为调用 `python3 scripts/update_data.py runtime`。
- Home 系统状态已展示 nginx、HTTPS、证书、部署 commit、最近 pull、cron、wiki-todos 同步、失败日志、CPU、磁盘、内存、uptime、云位置和计费状态，异常项会在页面中显色。
- Home 的“当前主线 / 待推进”可通过 `python scripts/update_data.py project-status` 从 `ROADMAP.md` 显式刷新，避免定时任务自动覆盖 Owner 判断。
- 本地预览已可通过 `http://127.0.0.1:8000/` 运行和访问。
- 新增 `scripts/sync_system_status.py`，可采集 nginx、HTTPS、git commit、磁盘、内存和 wiki-todos 同步状态，并只更新 dashboard 的 `automation` / `system` 字段。
- 在 Home 主内容区增加 personal-wiki 近期待办入口，位于“当前主线”和“待推进”之间，当前为只读展示 / 跳转，不支持编辑或标记完成。
- 在 Home 右侧增加豆奶签到只读摘要入口，并新增豆奶详情 tab，展示近 30 天流量/时长折线图。
- 新增 `scripts/sync_wiki_todos.py` 和 `dash/data/wiki-todos.*`，用 `gh api` 从 private personal-wiki 生成 MaxNow 可静态读取的待办缓存。
- 建立 `AGENTS.md`，固定分支、语言、文件边界和 OpenClaw 边界。
- 建立 `CONTEXT.md`，保存代理接力用的项目上下文地图。
- 建立 `IDEAS.md`，记录未来想法和桌面伴随入口。
- 建立 `UPDATE_LOG.md`，记录重要项目更新。
- 建立 `openclaw/maxnow-dashboard/SKILL.md`，约束 dashboard / ai-news 数据维护。
- 建立 `openclaw/last-30/SKILL.md`，约束 Last-30 滚动记忆维护。
- 建立 `dash/data/last-30.*`，承载今日、本周、近 30 天上下文。
- 在 Home 页面接入 Last-30 模块。
- 中文化 `README.md` 和 `DEPLOY.md`。
- 新增 `scripts/check.py`，用于本地一致性校验。
