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

### 补齐前端自动测试、无障碍与移动端验证

- 来源：2026-07-10 MaxNow 整体体检。
- 建议分支：`feature/frontend-smoke-tests`
- 在 CI 或本地统一命令中启动静态服务，检查 Dash 六个 tab、Blog 主要页面、控制台错误、失效资源和关键交互。
- 增加 JavaScript 语法检查和关键数据新鲜度 / Roadmap 一致性检查；自动测试环境中本地服务不可达应判失败，不再仅显示 skipped。
- 为 Home 同行卡、Today Status 时间轴和主要网格增加桌面 / 手机几何断言，检查同排卡片上下边缘、高度和水平溢出。
- 为侧栏当前页面补 `aria-current`，为 Token 范围补完整 tab 语义、`aria-selected` 和键盘行为。
- 补 390px 左右手机宽度的真实浏览器回归测试，再决定是否需要移动端导航或卡片密度调整。

### 收紧外部依赖和链接安全

- 来源：2026-07-10 MaxNow 整体体检。
- 建议分支：`bugfix/frontend-external-safety`
- 外部数据中的链接只允许 `https:` / `http:`，拒绝 `javascript:` 等非预期协议，并统一使用 `rel="noopener noreferrer"`。
- 评估把 Leaflet 静态资源放入仓库，减少 unpkg 不可用、供应链变化或 CSP 收紧后导致同行记地图失效的风险。
- 保留地图 fallback，并明确提示当前展示的是真实在线地图还是静态 fallback；评估第三方瓦片请求的隐私影响。
- 为将来的严格 CSP 预先梳理 Dash / Blog 所需的脚本、样式、图片和地图来源，避免上线访问控制后仍保留过宽的外部资源权限。

### 让 Last-30 免费 AI 信号稳定运行

- 中文 AI 前沿简报、正式发布优先排序、三栏主题去重和无用客户案例过滤已经落地；服务器 `MAXNOW-AI-LAST30-SYNC` 继续每天 00:00 自动刷新。
- 观察免费源稳定性：官方 RSS / 博客、GitHub releases、Hacker News、GDELT、arXiv。
- 如果某些免费源长期失败，再替换成更稳定的 RSS 或项目 release 源。
- X / Twitter 暂不接入；只有 Owner 明确批准付费 API 和博主白名单后再做。
- 继续观察通用中文规则对未来新产品名的覆盖；只有规则无法稳定表达时，再让 OpenClaw 对 10-20 条候选做二次摘要，不要把全文大量喂给模型。

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

## Later

### 建立 LIJUN 芭蕾远端自动约课

- 来源：2026-07-25 Owner 需求与只读可行性测试。
- 建议分支：`feature/ballet-booking`
- 目标：在 MaxNow 远端服务器按北京时间每周日 14:20 自动预约 Owner 预先配置的下周课程；正式名额已满时按配置进入候补，不做自动取消或转课。
- 当前入口是微信公众号内 H5 网页，不是微信小程序：`gm.wendaosoft.com/gm/weixin/home/index/54114` 会通过微信 `snsapi_base` OAuth 建立网站会话，再用 `PHPSESSID` 访问会员与课程页面。
- 2026-07-25 已完成一次只读验证：电脑微信退出后，将本机解密出的会话仅经 SSH 标准输入传给服务器内存，服务器访问首页和课程表均返回 `200` 且没有重新跳转 OAuth；课程表最终进入 `/gm/weixin/classtable/simpleclass/54114/430`。
- 已定位课程表读取和预约相关路径，包括 `check_rules`、`getusingcard`、`check_cardtypecourse` 与 `do_addbook`；本次没有调用预约、候补、取消或转课接口，没有在本机临时目录或远端服务器持久化会话。
- 第一阶段正在进行会话生命周期验证：2026-07-26 19:07 已在 MaxNow 服务器启动临时隔离单元，每 10 分钟只读查询一次课程表，身份失效或连续 3 次未知 / 网络异常即停止，最长运行 30 天且服务器重启后不会自动恢复；首条服务器样本为 HTTP 200 / authenticated。
- 当前实验只回答“持续活动时最多能维持多久”，不包含停止请求后的静默失效验证；Session 结束后再根据持续时间、是否收到 `Set-Cookie` 和会话指纹是否轮换，决定是否需要单独做空闲对照实验。
- 第二阶段实现只读课程解析和 dry-run：配置课程名、老师、日期 / 时段、优先级、冲突规则以及“满员后是否候补”，输出计划动作但不提交。
- 第三阶段在 Owner 明确启用后接入真实预约：周日 14:19:50 预热并校时，14:20 开始有限重试；提交前再次校验课程、会员卡和现有预约，使用幂等保护避免重复约课，结果区分正式成功、候补成功、已预约、规则拒绝、登录失效和未知错误。
- `PHPSESSID` 视为约课网站密码：只允许存入服务器专用系统用户可读的 `0600` 凭据文件或 systemd credential，不得进入 Git、前端、环境变量、命令参数、日志、备份或聊天；仅通过 HTTPS 发送，日志最多记录会话哈希和状态。
- 停用自动约课时先停止定时任务，再删除凭据和运行态缓存；若网站提供主动退出或会话吊销入口，应将其纳入撤销流程。长期保活会扩大网站会话暴露窗口，启用前需要 Owner 单独确认这一取舍。
- 上线前至少完成一次非热门课程或测试时段的人工陪同演练；遇到验证码、微信重新授权、页面结构变化或无法判断的响应时立即停止，不自动点击未知按钮。
- 后续还需 Owner 提供实际目标课程、老师 / 时段优先级、冲突处理、候补规则和通知渠道；真实预约提交必须在这些规则确定后再启用。

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

### 已建立数据失败与新鲜度闭环

- Home 数据同步统一区分已同步、暂无记录、请求失败、数据过期和尚未同步；同步成功后的数值 `0` 保持真实数值，不再与空数据混淆。
- 浏览器按数据源保存最后一次成功响应；短时 JSON 请求失败时继续展示旧数据，并在数据同步状态中明确标记“请求失败”和保留时间。
- 系统状态统一汇总 Wiki、Token、天气、市场、Last-30、版本、Roadmap、豆奶、同行记和生活 10 个 Owner 可见来源。
- Dashboard runtime、AI Last-30、Token sources 和 Token ledger 连续失败 3 次时进入自动化异常状态；单次抖动仍保留在失败日志中，不直接升级为连续失败告警。
- `.js` wrapper 继续作为生成一致性资产；运行时短时故障的保底改由浏览器最后成功缓存承担。

### 已将 Last-30 重构为中文 AI 前沿简报

- Home 模块改为“最新发布 / 本周前沿 / 近 30 天关键进展”，只显示中文事实标题、具体摘要、日期和来源。
- 采集器区分正式模型 / 产品 / API 发布与客户案例、合作、泛采用、纯 SDK 版本号，避免品牌关键词越多反而排名越高。
- 三栏按事件主题去重；近 30 天不再显示 `active`、候选数量和关键词自动归类报告。
- 当前简报已将 OpenAI 正式发布 GPT-5.6、ChatGPT Work 和 GPT-Live 放入最新发布。
- `scripts/check.py` 新增中文可见文案、禁用套话、跨栏去重和采集器自检。

### 已完成私人 Dash 自定义登录与访问保护

- MaxNow 风格登录页替代浏览器原生 Basic Auth 弹窗；nginx `auth_request` 统一保护 `dash.maxnow.cn` 页面、静态资源和 `/data/`。
- 服务器本机认证服务复用 `/etc/nginx/.htpasswd-maxnow` 校验密码，签发 7 天 `HttpOnly + Secure + SameSite=Strict` Cookie，不引入数据库或业务 API。
- `blog.maxnow.cn` 保持公开；Dash 新增 CSP、`X-Content-Type-Options`、`Referrer-Policy`、`X-Frame-Options`、`Permissions-Policy` 和 HSTS，并隐藏 nginx 版本号。
- 系统状态采集将跳转到 `/login` 识别为“认证已启用且健康”，避免自动化把预期登录入口误报成 HTTPS 故障。
- 真实用户名和密码只保存在服务器凭据文件与 Owner 密码管理器中，不进入仓库；密码轮换和紧急恢复步骤记录在部署文档与服务器手册。

### 已修复 Home 项目状态可信度

- 2026-07-10 将 ROADMAP 生成的主线和待推进从 `dashboard.*` 拆到独立 `project-status.*`，`dashboard.today` 继续只承担 Owner 当天人工 override。
- `project-status.*` 记录 ROADMAP 来源更新时间、生成时间、7 天过期阈值和内容指纹；过期时 Home 显示“待刷新”，并停止用旧项目状态生成 Today Status 推荐。
- `scripts/check.py` 会验证项目状态仍匹配当前 ROADMAP Now / Next，拒绝 Done 项和同名 active / Done 冲突；ROADMAP 变化后未刷新会直接校验失败。
- 当前错误待推进“Last-30 还是 2026-06-14 草稿”和“补充 Token 使用页真实数据”已从 `dashboard.*` 移除。
- 仓库规则已要求 ROADMAP Now / Next / Done 变化后运行 `python scripts/update_data.py project-status`；服务器日常 `runtime` 和 OpenClaw 不得覆盖项目状态。

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

- 新增 `scripts/sync_codex_usage.py`，只读 `.codex/sessions` 的 `token_count`、模型和 `task_complete.duration_ms`，生成 Token 与已完成任务活跃时长账本。
- 新增 `dash/data/codex-macos-usage.*` 和 `python scripts/update_data.py codex-macos-usage`，将 macOS 本机 Codex 账本拆成独立文件，避免覆盖 Windows 兼容账本。
- 新增 `dash/data/codex-server-usage.*` 和 `python scripts/update_data.py codex-server-usage`，用 `codex-server` 来源 ID 读取服务器 `/root/.codex/sessions` 并生成独立服务器 Codex 账本。
- 新增 `scripts/sync_token_usage.py` 和 `dash/data/token-usage.*`，将 OpenClaw 与 Codex 源账本合并为统一 Token 总账。
- Token 页面优先读取统一总账，保留 1d / 7d / 30d / all、来源费用面板、模型占比、最近调用和最近 30 天折线图，并显式区分 OpenClaw、Codex Windows / macOS、Codex server；来源费用跟随当前范围更新。Home 原“当前主线”位置展示近 180 天每日 Token 活动热力格。
- `scripts/update_data.py codex-usage` 会刷新 Windows 兼容本机 Codex 源账本、统一总账和 wrapper；`scripts/update_data.py codex-macos-usage` 会刷新 macOS 本机 Codex 源账本、统一总账和 wrapper；`scripts/update_data.py codex-server-usage` 会刷新服务器 Codex 源账本、统一总账和 wrapper；`scripts/update_data.py token-usage` 可单独合并现有账本。
- Windows Task Scheduler 固定每小时 `:02` 上报，macOS launchd 固定每小时 `:00` 上报；两端错开推送并设置网络超时 / 任务运行上限。
- macOS 上报已支持生成提交分叉自愈和并发 push 有限重试；只有提交标题与改动文件都严格落在 macOS 源账本边界内才允许自动 reset，人工提交继续要求手工处理。
- 服务器 root crontab 使用 `MAXNOW-TOKEN-SOURCE-REFRESH` 每小时 `:05` 刷新 OpenClaw / Codex server 源账本；ubuntu 使用 `MAXNOW-TOKEN-USAGE-REFRESH` 每小时 `:10` 拉取并发布统一总账。

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
- Token 页面已接入 OpenClaw 用量账本，支持 1d / 7d / 30d / all 范围切换、总量 / 输入 / 输出 / 缓存读 / 费用、模型占比、会话消耗和最近 30 天折线图；Home 同步展示近 180 天每日 Token 活动热力格。
- 服务器 root crontab 已统一为 `MAXNOW-TOKEN-SOURCE-REFRESH`：每小时 `:05` 刷新 OpenClaw / Codex server 来源账本，总账由 ubuntu 在 `:10` 发布。
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
