# MaxNow 更新记录

这个文件记录 MaxNow 的重要更新，让产品方向、数据边界和实现决定可以被追溯。

## 使用规则

- 只要 Codex、Owner 或其他维护者改变了产品方向、页面代码、数据结构或操作规则，就在这里补一条。
- 每条记录保持简短、具体。
- 有必要时写清楚涉及哪些文件。
- 原始未来想法写进 `IDEAS.md`；已经确认的产品行为再同步进 `SPEC.md`。

## 2026-07-10

### 完成 AI 前沿线上部署与旧规则清理

- 线上部署目录从旧提交 `a19dad6` 快进到 `538dc40`，先备份并暂存服务器运行数据，再只恢复 dashboard、豆奶、行情、同行记和 Wiki Todo，未恢复旧 `ai-news.*` / `last-30.*`。
- 服务器重新生成中文 AI 前沿数据并通过 `scripts/check.py` 与 `nginx -t`；最新发布为 GPT-5.6、ChatGPT Work 和 GPT-Live，数据中不再出现“关注它”等套话。
- 清理 `SERVER_RUNBOOK.md` 与 `CONTEXT.md` 中残留的“当天优先 / 英文外部输入”旧口径，将 `VERSION` 从 `1.0.3.00` 提升到 `1.0.3.01`。

### 将 Last-30 重构为中文 AI 前沿简报

- Home 原“外部输入”改为“AI 前沿”，三栏固定展示“最新发布 / 本周前沿 / 近 30 天关键进展”，只保留中文事实标题、具体变化、日期和来源。
- 采集器新增事件类型与优先级：模型、产品、API / Agent 正式发布优先，客户案例、合作、泛采用、纯 SDK 版本号和 updated packages 不再挤占前沿位置。
- 同一事件跨三栏按主题去重，近 30 天移除 `active`、候选数量和关键词自动归类；当前数据已把 GPT-5.6、ChatGPT Work 和 GPT-Live 放在最新发布。
- 新增采集器 self-test 和 `scripts/check.py` 中文文案 / 禁用套话 / 跨栏去重校验；样式缓存提升到 `styles.css?v=128`，脚本缓存提升到 `app.js?v=110`。
- 将 `VERSION` 从 `1.0.2.03` 提升到 `1.0.3.00`。

### 修正 Today Status 时间轴方向与当前时间对齐

- 将 00:00-24:00 今日进度轴统一为从上向下推进，当前时间圆点、时间文字和进度填充共用同一坐标方向。
- 修复晚间当前时间错误停在时间轴顶部、与时段信号行挤在一起的问题；样式缓存提升到 `styles.css?v=127`。
- 将 `VERSION` 从 `1.0.2.02` 提升到 `1.0.2.03`。

### 修复海淀降雨被显示为阴天

- 北京天气从 Open-Meteo 默认 Best Match 切换到中国气象局 CMA / GRAPES 模型；同一时刻默认模型返回阴且降水为 0，CMA 模型返回阵雨和 2.3mm 降水。
- 天气同步新增当前 `precipitation / rain / showers` 字段；当天气码仍为云但降水大于 0 时，按雨或阵雨展示。
- 将 `VERSION` 从 `1.0.2.01` 提升到 `1.0.2.02`。

### 收紧 Token 来源更新时间卡

- Token 页头右侧来源更新时间卡改为 `410px` 内容宽度，不再按比例铺满半行；说明文字移到四行来源时间上方。
- `860px` 以下继续随页头切为单列并占满可用宽度，样式缓存版本提升到 `styles.css?v=126`。
- 将 `VERSION` 从 `1.0.2.00` 提升到 `1.0.2.01`。

### 用 MaxNow 风格登录页替代浏览器原生认证弹窗

- 新增双栏登录页，复用 MaxNow 的浅蓝灰背景、白卡片、语义色小图标、输入框 focus 和轻量 hover；`760px` 以下自动切换单栏。
- 新增仅监听服务器本机的最小认证服务，复用现有 htpasswd 校验密码并签发 7 天 HttpOnly 会话 Cookie；密码、密码哈希和会话密钥均不进入前端或 Git。
- nginx 改用 `auth_request` 统一保护 Dash 页面、静态资源和 `/data/`，保留 Blog 公开，并为登录接口增加限速。
- Dashboard 顶栏新增退出入口；系统状态采集将跳转登录页识别为认证正常。
- 将 `VERSION` 从 `1.0.1.02` 提升到 `1.0.2.00`。

### 轮换私人 Dash 访问密码

- 已轮换 `dash.maxnow.cn` 的 nginx Basic Auth 密码；用户名保持 `maxnow`，真实密码和哈希均未写入仓库。
- `nginx -t` 通过并完成 reload；新凭据访问 Dash 返回 200，未认证 Dash 与 `/data/` 返回 401，Blog 保持 200。
- 将 `VERSION` 从 `1.0.1.01` 提升到 `1.0.1.02`。

### 为私人 Dash 启用账号密码访问保护

- nginx Basic Auth 已覆盖 `dash.maxnow.cn` 首页、静态资源和 `/data/`；未认证请求与直接源站访问均返回 401，正确凭据返回 200。
- `blog.maxnow.cn` 继续公开；Dash 新增 CSP、`X-Content-Type-Options`、`Referrer-Policy`、`X-Frame-Options`、`Permissions-Policy` 和 HSTS，并通过 `server_tokens off` 隐藏 nginx 版本。
- `maxnow.cn` nameserver 已恢复为 DNSPod；Cloudflare Access / Tunnel 不进入当前生产链路。
- `scripts/sync_system_status.py` 将带 `WWW-Authenticate` 的 401 识别为预期健康状态，避免 Home 把访问保护误报成 HTTPS 故障。
- 将 `project-status.*` 纳入服务器自动生成数据白名单，避免状态刷新后被 deploy check 误判为代码脏改动。
- 补充密码轮换、紧急恢复、源站绕过检查和响应头维护说明；真实凭据不进入仓库。
- 将 `VERSION` 从 `1.0.0.52` 提升到 `1.0.1.00`。

原因：

- Dash 包含个人待办、旅行、Token 和服务器状态，必须在源站统一拦截未认证访问，同时保持 Blog 公开。

### 统一 Token 活跃时长与固定小时上报周期

- Codex collector 新增 `task_complete.duration_ms` 统计，Token 页按 1d / 7d / 30d / all 展示已完成任务的活跃时长，并在来源与会话中展示对应时长；轮次间空闲时间不计入。
- 固定上报周期调整为 macOS `:00`、Windows `:02`、服务器 OpenClaw / Codex server 源采集 `:05`、统一总账发布 `:10`，避免两台本机同时 push。
- macOS launchd 从相对 `StartInterval` 改为固定 `StartCalendarInterval`；Windows 任务改为整点偏移触发并设置 10 分钟执行上限。
- 本机 Git 增加 HTTP 低速边界和 SSH keepalive，避免一次 `git pull` / `push` 卡死占住后续小时周期。
- 修复 Token 最近 30 天图表在 390px 移动端把整页撑宽的问题；宽图改为卡片内部横向滚动。
- 云服务页同步更新 Token 自动化时间和锁 / 日志说明，Dash 缓存版本提升到 `styles.css?v=124`、`app.js?v=109`。
- 已部署到服务器并手动跑通一轮：root `:05`、ubuntu `:10` cron 生效，线上总账写入 macOS 与 Server Codex 活跃时长；macOS launchd 已按 `Minute=0` 重装并首次上报成功。

原因：

- 原本本机按安装时刻每 3600 秒运行、服务器每 10 分钟合并，两套时钟错位；一次本机 Git 卡住还会阻止后续上报，导致来源时间和总账时间互相误导。

### 修复 Home 项目状态过期和已完成任务误报

- 新增独立 `dash/data/project-status.*`，从 `ROADMAP.md` 生成 Home 主线和待推进事项，不再把自动生成结果写入 `dashboard.*` 或修改 `dashboard.today`。
- 项目状态新增 ROADMAP 来源更新时间、生成时间、7 天过期阈值和内容指纹；Home 待推进卡展示同步状态，过期数据停止驱动 Today Status 推荐。
- `scripts/check.py` 新增 ROADMAP 一致性检查：项目状态必须来自 Now / Next，不能引用 Done，ROADMAP 变化但未刷新时校验失败。
- 移除旧的“Last-30 还是 2026-06-14 草稿”和“补充 Token 使用页真实数据”，当前待推进改为访问保护、数据健康闭环和前端自动测试。
- 更新 `AGENTS.md` 和 OpenClaw skill，要求 ROADMAP Now / Next / Done 变化后刷新 `project-status.*`，服务器日常 `runtime` 和 OpenClaw 不得覆盖它。
- 将 Dash 缓存版本提升到 `styles.css?v=123` 和 `app.js?v=108`，并将 `VERSION` 从 `1.0.0.50` 提升到 `1.0.0.51`。
- 已部署提交 `eade306` 到 `dash.maxnow.cn`；部署前备份服务器运行数据到 `/home/ubuntu/maxnow-deploy-backups/20260710-104139-before-home-project-status`，恢复后移除旧 `dashboard.mainlines/actions`，重新生成 dashboard wrapper 和 project-meta。
- 线上验证 `project-status.json` 为 200，待推进为访问保护、数据健康闭环和前端自动测试；`python3 scripts/check.py`、`nginx -t`、nginx reload 和站点 HTTP 200 均正常。

原因：

- Home 的自动建议必须与当前 ROADMAP 和已完成功能一致，不能让过期项目状态误导 Owner 的每日判断。

### 记录 MaxNow 整体体检后的优化路线

- 在 `ROADMAP.md` 增加 Dash 访问保护、Home 项目状态可信度、数据失败与新鲜度闭环、前端自动测试 / 无障碍 / 移动端验证、外部依赖和链接安全等可执行任务。
- 在 `IDEAS.md` 增加“可信状态工作站”长期方向，明确现有六个一级入口稳定前不以继续增加页面为主要目标。
- 更新 `CONTEXT.md` 的当前缺口和建议下一步，将私人访问保护和状态可信度列为后续最高优先级。

原因：

- Owner 要求把 MaxNow 整体审查发现的 Bug、优化建议和长期展望记录进仓库，避免只停留在聊天里。

### 调整 Home 版本更新模块位置

- 将“最近更新”改名为“版本更新”，并移动到外部输入模块下方。
- 两个模块继续沿用左侧 `home-lane-primary` 的 `wide-short` 卡型，只调整卡片顺序，不改变现有视觉和响应式规则。
- 将 Dash 样式缓存版本提升到 `styles.css?v=122`，并将 `VERSION` 从 `1.0.0.48` 提升到 `1.0.0.49`。
- 已随合并提交 `008ed5a` 部署到 `dash.maxnow.cn`；部署前备份并恢复服务器运行数据，Codex Server 账本保持 11 次会话和 4,993,467 Token。

原因：

- Owner 希望先查看外部输入，再在其下方查看 MaxNow 自身的版本更新。

### 修复 Today Status 当前时间与进度轴重叠

- 将 00:00、当前时间和 24:00 的右边缘统一锚定在进度轴左侧，并为当前时间与进度圆点保留固定间距。
- 将 Dash 样式缓存版本提升到 `styles.css?v=121`，并将 `VERSION` 从 `1.0.0.47` 提升到 `1.0.0.48`。

原因：

- 当前时间原先按容器左边缘定位，四位时间文本会侵入进度条和圆点区域。

## 2026-07-09

### 替换 Home 顶部状态小卡

- Home 顶部状态条前两张小卡从“当前主线 / 待推进”改为“今日执行 / 数据同步”。
- “今日执行”读取 personal-wiki 今日明确执行日期待办数量，“数据同步”聚合 Wiki Todo、Token、天气、市场、Last-30 和项目元信息的新鲜度。
- 将 Dash 缓存版本提升到 `styles.css?v=120` 和 `app.js?v=107`，并将 `VERSION` 从 `1.0.0.46` 提升到 `1.0.0.47`。

原因：

- Owner 认为“当前主线 / 待推进”作为独立数字小卡信息重复；首屏状态条应更直接回答今天是否有明确执行任务、关键数据是否新鲜。

## 2026-07-08

### 将 Today Status 竖线改为今日时间轴

- Today Status 右侧竖线改为按 00:00-24:00 推进的今日进度轴，显示 00:00、当前时间和 24:00。
- 右侧时段、推进、Token、自动化信号用节点挂在时间轴旁；顶部横线继续承担 Today Status 卡片的状态强调，不再和竖线混用同一套含义。
- 将 Dash 缓存版本提升到 `styles.css?v=119` 和 `app.js?v=106`，并将 `VERSION` 从 `1.0.0.45` 提升到 `1.0.0.46`。

原因：

- Owner 指出中间竖线应该表达“今天已经过了多久”，不是普通分隔线或随机状态色装饰。

### 移除 Home 今日记录模块

- 从 Home 左侧内容流移除“今日记录 / Daily Log”模块，避免静态项目原则被误认为当天真实日志。
- 同步移除 `journal-list` 首页渲染入口和 `home-card-journal` 专属样式；`dashboard.json` 中历史 `journal` 字段暂不删除，保留数据兼容。
- 更新 `SPEC.md`、`STYLE_CONTEXT.md` 和 `CONTEXT.md`，明确 Home 不再保留独立“今日记录”卡片，真正的当天判断由顶部今日状态承载。
- 将 Dash 缓存版本提升到 `styles.css?v=118` 和 `app.js?v=105`，并将 `VERSION` 从 `1.0.0.44` 提升到 `1.0.0.45`。

原因：

- Owner 确认“今日记录”当前只是 `dashboard.json.journal` 静态内容，不会自动成为当天日志，没必要继续占用 Home。

### 调整 Token 来源同步位置

- Token 页“各来源最后同步”改回显示具体时间 `YYYY-MM-DD HH:mm`，不再使用“今天 / 昨天 / X 分钟前”这类相对时间。
- 来源更新时间列表移动到同步卡片右侧区域，并改为从上到下 4 条纵向排列，减少左侧标题区拥挤。
- 将 Dash 缓存版本提升到 `styles.css?v=117` 和 `app.js?v=104`，并将 `VERSION` 从 `1.0.0.43` 提升到 `1.0.0.44`。

原因：

- Owner 希望保留明确更新时间，并要求四个来源更新时间放到 Token 页头右侧空白位置纵向展示。

### 移除 Home 稍后留意模块

- 从 Home 左侧内容流移除“稍后留意 / Links”模块，避免 Roadmap 任务、服务器链路和文档入口重复占用首页空间。
- 同步移除 `feed-list` 首页渲染入口和 `home-card-feeds` 专属样式；`dashboard.json` 中的 feeds 数据暂不删除，避免影响历史数据边界。
- 更新 `SPEC.md`、`STYLE_CONTEXT.md` 和 `CONTEXT.md`，明确 Home 不再保留单独“稍后留意”卡片：待办线索进入待推进 / Roadmap，系统链路进入云服务 / 系统状态，文档入口进入最近更新或项目状态。
- 将 Dash 缓存版本提升到 `styles.css?v=116` 和 `app.js?v=103`，并将 `VERSION` 从 `1.0.0.42` 提升到 `1.0.0.43`。

原因：

- Owner 确认“稍后留意”模块信息重复且 UI 不喜欢，Home 应留给每天扫一眼真正有用的内容。

### 优化 Token 来源同步时间

- Token 页“各来源最后同步”从完整日期改为自然时间表达：刚同步显示“刚刚 / X 分钟前”，当天显示“今天 HH:mm”，昨天显示“昨天 HH:mm”，更早显示“M月D日 HH:mm”。
- 来源同步区从彩色 pill 改为两列轻量状态行：来源、自然时间和小色点并列展示，减少标签堆叠感。
- 每个来源保留完整同步时间的 hover 提示，便于需要精确排查时查看原始时间；超过 72 小时未同步的来源会弱化显示。
- 将 Dash 缓存版本提升到 `styles.css?v=115` 和 `app.js?v=102`，并将 `VERSION` 从 `1.0.0.41` 提升到 `1.0.0.42`。

原因：

- Owner 指出 Token 页来源刷新时间“看着不太友好”，并且不喜欢原来的彩色 pill UI。

### 调整 Home Todo 和 Token 长条布局

- 将 Home 右侧 `Today Todo` 和 `Tokens` 从半宽 `widget-compact` 改为整行 `widget-wide`，让它们在右侧栈里上下显示为两个长条。
- 系统自动化聚合状态现在按 `正常 / 注意 / 异常` 切换绿色、橙色、红色；异常时不再继续显示绿色强调。
- 修正顶部 Token 范围切换被通用 `.range-tabs` 样式覆盖的问题，确保 `1d / 7d / 30d / all` 只在 Token 页显示。
- 补齐系统状态和项目元信息的运行数据白名单，避免 macOS Codex、Life foods、market indices 等自动生成数据把 `deploy` 误报为异常。
- 将 Dash 缓存版本提升到 `styles.css?v=114` 和 `app.js?v=101`，并将 `VERSION` 从 `1.0.0.40` 提升到 `1.0.0.41`。

原因：

- Owner 指出 Home 中部的 Todo / Tokens 区域应改成上下两个长条，并询问系统自动化为什么显示异常；线上当前异常来源为系统状态聚合里的 `deploy` 检查误报。

### 回填 Home 左侧内容流

- 将最近更新、外部输入和稍后留意从右侧 widget 栈移回左侧 `home-lane-primary`，避免右侧一路下排时左列出现大面积空白。
- 右侧 `home-side-stack` 固定只承载市场、今日 Todo、近期用量、豆奶和系统状态等短扫读状态入口；内容型长模块优先进入左列。
- 更新 `STYLE_CONTEXT.md`、`SPEC.md` 和 `CONTEXT.md`，明确 Home 新增模块必须先区分“内容流”与“短状态 widget”。
- 将 Dash 样式缓存版本提升到 `styles.css?v=113`，并将 `VERSION` 从 `1.0.0.39` 提升到 `1.0.0.40`。

### 标准化 Home Widget 尺寸

- Home 右侧 `home-side-stack` 从单列大卡改为 widget 网格：`widget-compact` 占半宽，`widget-wide` / `wide-*` / `mid-*` 占满右列。
- 顶部 Today Status 比例调宽，天气和小日历保持紧凑 widget，不再把右侧两个小组件拉成大卡。
- 更新 `STYLE_CONTEXT.md`、`SPEC.md` 和 `CONTEXT.md`，明确后续 Home 模块必须先声明卡型尺寸，不能随手用二列或三列拉伸。
- 将 Dash 样式缓存版本提升到 `styles.css?v=112`，并将 `VERSION` 从 `1.0.0.38` 提升到 `1.0.0.39`。

### 改为 Home 两列主版式

- Home 主内容从三列视觉布局调整为两列外壳：左列承载个人主任务，右列用 `home-side-stack` 纵向承载市场 / 用量 / 更新和 Todo / 豆奶 / 系统状态。
- Home 顶部 Today Status 与天气 / 小日历沿用同一套两列比例，避免时间卡右侧出现未对齐空白。
- 更新 `STYLE_CONTEXT.md`、`SPEC.md` 和 `CONTEXT.md`，明确后续 Home 模块先选语义 lane，不再为了三列对齐硬挤出右侧窄栏。
- 将 Dash 样式缓存版本提升到 `styles.css?v=111`，并将 `VERSION` 从 `1.0.0.37` 提升到 `1.0.0.38`。

### 调整 Home 顶部左右比例

- 收窄 Home 顶部 Today Status 卡片的横向占比，提高右侧天气卡和小日历 widget 组的桌面最小宽度。
- 保持 1320px 以下堆叠规则不变，避免中小屏产生横向溢出。
- 将 Dash 样式缓存版本提升到 `styles.css?v=110`，并将 `VERSION` 从 `1.0.0.36` 提升到 `1.0.0.37`。

### 修正 Home Board 三 lane 版式

- Home 状态条下方从单张跨行 `grid-template-areas` 网格改为 `home-lane-primary` / `home-lane-signal` / `home-lane-rail` 三条独立纵向 lane，避免高卡把同一行短卡撑出大块空白。
- 右侧状态 rail 保留最小宽度，豆奶和近期用量的小指标卡不再被压成窄条；1320px 以下切换为两列 / 单列响应式。
- 更新 `STYLE_CONTEXT.md`、`SPEC.md` 和 `CONTEXT.md`，把 Home 新增模块规则改为先选 lane 再选卡型，禁止再用固定 `grid-area` 拼不同高度模块。
- 将 Dash 缓存版本提升到 `styles.css?v=109`，并将 `VERSION` 从 `1.0.0.35` 提升到 `1.0.0.36`。

### 统一 Home Board 版式规则

- Home 状态条下方改为统一 `home-board`：Token、市场、今日 Todo、Personal Wiki、豆奶、待推进、近期用量、外部输入、最近更新、今日记录、稍后留意和系统状态都在同一个响应式网格里声明位置。
- 新增并沉淀页面版式协议：模块必须先选卡型和 grid-area，不能再用局部左右列、局部栈、固定高度或空白补丁拼页面。
- Personal Wiki 首页展示固定为前 4 条未完成待办，长标题截断，更多内容进入外链，避免首页被列表自由撑高。
- 将 Dash 缓存版本提升到 `styles.css?v=106` 和 `app.js?v=100`，并将 `VERSION` 从 `1.0.0.34` 提升到 `1.0.0.35`。

### 填补 Home Token 热力格下方空白

- Home 顶部主内容改为左侧 Token 热力格 + Personal Wiki 近期待办竖向栈、右侧市场涨幅卡，避免市场卡撑高整行后左侧出现大面积空白。
- 新增 `.home-signal-stack` 作为无视觉层的布局容器，移动端仍按单列自然堆叠。
- 将 Dash 样式缓存版本提升到 `styles.css?v=105`，并将 `VERSION` 从 `1.0.0.33` 提升到 `1.0.0.34`。

### 调整 Home Token 热力格为 90 天

- Home Token 活动热力格从近 180 天改回近 90 天，保持 3 行展示，避免左侧卡片内格子过小。
- 去掉 Home 热力图固定最小高度，并让格子间距随宽度轻微缩放，减少卡片底部空白。
- 将 Dash 缓存版本提升到 `styles.css?v=104` 和 `app.js?v=99`，并将 `VERSION` 从 `1.0.0.32` 提升到 `1.0.0.33`。

### 修正 Token 范围切换 fallback

- Token 页不再回退到 `dashboard.json.tokenUsage` 里的旧模拟范围，避免真实总账加载前显示过期的中文小时范围。
- 删除 `dash/data/dashboard.*` 中过期的 `tokenUsage` mock，真实 Token 页只读取 `dash/data/token-usage.*`。
- 范围按钮按 key 和 label 校验后重建，确保始终显示 `1d / 7d / 30d / all`。
- 将 Dash 脚本缓存版本提升到 `app.js?v=98`，并将 `VERSION` 从 `1.0.0.31` 提升到 `1.0.0.32`。

### 修正 Home 市场涨幅数据源

- 将市场涨幅同步切到腾讯公开行情接口，服务器可同时刷新国内和美股指数 quote 与分钟线。
- 将 `VERSION` 从 `1.0.0.30` 提升到 `1.0.0.31`。

### 新增 Home 市场涨幅卡

- Home 主内容区顶部改为 Token 热力格 + 市场涨幅双列，右侧展示纳指100、标普500、上证指数、深证成指和创业板指。
- 新增 `dash/data/market-indices.*` 和 `scripts/sync_market_indices.py`，通过腾讯公开行情接口生成点位、涨跌幅和压缩后的日内走势；`runtime` 每 10 分钟一并刷新。
- 云服务页基础运行同步卡补充行情日志和写入范围，`scripts/check.py` 校验行情数据形状和 wrapper 一致性。
- 将 Dash 缓存版本提升到 `styles.css?v=103` 和 `app.js?v=97`，并将 `VERSION` 从 `1.0.0.29` 提升到 `1.0.0.30`。

### 优化 Dash 首屏加载链路

- Dash 首屏不再同步加载 `dash/data/*.js` wrapper，也不再等待 Token、同行记、生活页等隐藏视图数据后才渲染 Home。
- 将 JSON 读取从时间戳 `no-store` 改为正常 URL + `cache: no-cache`，配合 ETag / Last-Modified 做 revalidate；Token、Ricky、Life 和 Leaflet 改为按视图加载。
- 更新部署文档中的 nginx 示例，建议启用 gzip，并将 `/data/` 改为短缓存 revalidate。
- 将 Dash 脚本缓存版本提升到 `app.js?v=96`，并将 `VERSION` 从 `1.0.0.28` 提升到 `1.0.0.29`。

### 将 Today Status 改为自动态势

- Home 顶部 Today Status 不再依赖过期 `dashboard.json.today` 手填字段作为主状态，改为基于今日 Todo、自动化状态、当前时段、ROADMAP 和 Token 活跃自动生成模式、节奏、焦点和摘要。
- `dashboard.json.today` 仅作为当天人工 override；旧日期判断会被忽略，不再显示“待刷新 N 天”占据首页主状态。
- 将 Dash 缓存版本提升到 `styles.css?v=101` 和 `app.js?v=95`，并将 `VERSION` 从 `1.0.0.27` 提升到 `1.0.0.28`。

## 2026-07-07

### 收窄今日 Todo 日期口径

- 今日 Todo 只展示 `due_at` 等于浏览器当天日期的未完成待办，不再混入过期未完成项。
- 无日期和过期未完成待办继续留在“近期待办”卡片，避免今日入口变成补债清单。
- 将 Dash 脚本缓存版本提升到 `app.js?v=94`，并将 `VERSION` 从 `1.0.0.26` 提升到 `1.0.0.27`。

### 将 Home 时间点替换为今日 Todo

- 移除 Home 右侧静态 `Schedule / 时间点` 模块，不再展示旧的固定节奏说明。
- 新增“今日 Todo”卡片，从 `wiki-todos` 里筛选当天明确执行日期待办，只读展示。
- 将 Dash 缓存版本提升到 `styles.css?v=100` 和 `app.js?v=93`，并将 `VERSION` 从 `1.0.0.25` 提升到 `1.0.0.26`。

### 让 Home 今日状态卡更灵动

- Today Status 卡仍读取 `dashboard.json.today`，但前端新增当前时段、判断新鲜度、待推进、Token 和自动化状态信号。
- 当 `today.updatedAt` 不是近期数据时，卡片会直接显示“待刷新 N 天”，避免旧判断看起来像今日实时状态。
- 将 Dash 缓存版本提升到 `styles.css?v=99` 和 `app.js?v=92`，并将 `VERSION` 从 `1.0.0.24` 提升到 `1.0.0.25`。

### 修复 macOS Codex 定时上报运行目录

- 将 Owner macOS 的 launchd 任务改为指向专用 clone `/Users/bytedance/.maxnow-token-report`，避免 Desktop 路径被 macOS 隐私权限拦截。
- 手动触发验证成功，`Codex macOS` 来源已更新到 `2026-07-07 17:32`，服务器 Token 总账已刷新到 `2026-07-07 17:42`。
- 将 `VERSION` 从 `1.0.0.23` 提升到 `1.0.0.24`。

### 调整 Home Token 热力格为 180 天

- Home Token 活动热力格从近 90 天调整为近 180 天，保持 3 行展示，让格子更小、更适合宽卡片。
- 修正热力格内部 grid 宽度计算，移除底部横向滚动条。
- 将 Dash 缓存版本提升到 `styles.css?v=98` 和 `app.js?v=91`，并将 `VERSION` 从 `1.0.0.22` 提升到 `1.0.0.23`。

### 将 Token 热力格移到 Home 主线位

- Home 原“当前主线”卡片替换为近 90 天每日 Token 活动热力格，格子横向铺满卡片，悬浮可查看日期和 token 数。
- Home 顶部 `Token 7天` 状态卡和右侧“近期用量”卡保留原有 1d / 7d / all 摘要。
- Token 页底部恢复为最近 30 天折线图，用于观察日级峰值和连续变化。
- 将 Dash 缓存版本提升到 `styles.css?v=97` 和 `app.js?v=90`，并将 `VERSION` 从 `1.0.0.21` 提升到 `1.0.0.22`。

### 加固服务器 Token 总账刷新 pull 超时

- `scripts/refresh_token_usage_on_server.sh` 的 `git pull --ff-only origin main` 增加默认 120 秒超时，避免 GitHub 网络偶发挂起时长期占住刷新锁。
- 支持通过 `--pull-timeout` 或 `GIT_PULL_TIMEOUT_SECONDS` 调整服务器拉取超时时间。
- 将 `VERSION` 从 `1.0.0.20` 提升到 `1.0.0.21`。

### 拆开本机 Codex 上报与服务器 Token 总账刷新

- Windows / macOS 本机 Codex 上报脚本改为只提交各自源账本：`codex-usage.*` / `codex-macos-usage.*`，推送后不再 SSH 触发服务器合并。
- 新增 `scripts/refresh_token_usage_on_server.sh`，由服务器每 10 分钟拉取最新源账本、保护 OpenClaw / Codex server 运行态账本，并重新合并 `token-usage.*`。
- 云服务页新增“Token 总账刷新”卡片，展示 `MAXNOW-TOKEN-USAGE-REFRESH`、锁和日志路径。
- 更新 `SPEC.md`、`CONTEXT.md`、`ROADMAP.md` 和 `SERVER_RUNBOOK.md` 中的自动化边界。
- 将 `VERSION` 从 `1.0.0.19` 提升到 `1.0.0.20`。

### 将 Token 趋势改为活动热力格

- 将 Token 页底部“最近 30 天”折线图替换为近 12 个自然月的 Token 活动热力格，按月份铺开每日格子。
- 新增“每日 / 每周 / 累计”强度切换，继续复用统一 `token-usage.*` 总账，不改变数据采集和合并脚本。
- 更新 `SPEC.md`、`STYLE_CONTEXT.md`、`CONTEXT.md` 和 `ROADMAP.md` 中的 Token 展示口径。
- 将 Dash 缓存版本提升到 `styles.css?v=96` 和 `app.js?v=89`，并将 `VERSION` 从 `1.0.0.18` 提升到 `1.0.0.19`。

### 修复 OpenClaw Token 来源回退为空

- 复查发现线上 `openclaw-usage.*` 被仓库中的空基线覆盖，导致统一 `token-usage.*` 只剩 Codex 来源，Token 页来源费用面板过滤掉 0 用量的 OpenClaw。
- 在服务器用 root 重新运行 `python3 scripts/update_data.py openclaw-usage`，恢复 OpenClaw 用量账本；当前采集到 346 个 OpenClaw runs，并重新合并统一 Token 总账。
- 加固 Windows / macOS 本机 Codex 上报脚本的服务器合并段：运行时账本改用带时间戳的备份目录；空备份不会覆盖已有非空账本；若服务器 OpenClaw 账本为空且 `/root/.openclaw` 可读，会用 sudo 刷新 OpenClaw 源账本后再合并 Token。
- 新增 `.gitattributes` 强制 `*.sh` 使用 LF 行尾，避免 Windows 工作区把 macOS 上报脚本转换成 CRLF 后在 bash 中失败。
- 将恢复后的 `openclaw-usage.*` / `token-usage.*` 同步回仓库，避免 `origin/main` 继续保存空 OpenClaw 基线。
- 将 `VERSION` 从 `1.0.0.17` 提升到 `1.0.0.18`。

## 2026-07-06

### 统一 Dash 页面主间距

- 新增 Dash 页面级 spacing 变量，统一主内容页边距、模块间距和同层卡片 grid gap。
- 将 Home、Token、豆奶、云服务、生活、同行记的大块间距收敛到 16px 节奏，去掉同行记单独左右 padding，避免不同页面主列位置漂移。
- 将 Dash 样式缓存版本提升到 `styles.css?v=95`，并将 `VERSION` 从 `1.0.0.16` 提升到 `1.0.0.17`。

### 拆开 Token 页头信息 tab

- 将 Token 页头外层从白底大卡改为透明 grid 容器，让“Token 用量”和“各来源最后同步”成为两张真正独立的同级 tab 卡片。
- 两张页头 tab 继承同组卡片边框、阴影和 hover 反馈，视觉上对齐 Home 顶部独立卡片模式。
- 将 Dash 样式缓存版本提升到 `styles.css?v=94`，并将 `VERSION` 从 `1.0.0.15` 提升到 `1.0.0.16`。

### 修复 Windows Codex 用量自动上报

- 修复 `D:\Personal\MaxNow-token-report` 专用 clone 直连 GitHub 时 `git pull` 卡住或连接重置的问题：为该 clone 补齐 repo-local `http.proxy` / `https.proxy` 到 `http://127.0.0.1:7897`。
- 清理 22:03 卡住的计划任务进程，并处理该 clone 中未推送生成物提交造成的 `main` 分叉；旧提交已保留到本地备份分支，随后用当前 `.codex/sessions` 重新生成账本。
- 手动启动 `MaxNow-Local-Codex-Usage-Report` 验证通过：2026-07-06 22:18 完成上报，`LastTaskResult=0`，线上 `Codex Windows` 来源更新时间更新到 `2026-07-06 22:18`。
- 将 `VERSION` 从 `1.0.0.14` 提升到 `1.0.0.15`。

### 调整 Token 页头和范围切换位置

- 将 Token 页 `1d / 7d / 30d / all` 范围切换移动到顶部栏右侧，只在 Token 页显示，和 Blog / 刷新入口同层。
- Token 页头改为两个并列信息 tab：左侧“Token 用量”展示总账合并时间，右侧“各来源最后同步”展示来源账本更新时间。
- 移除页头里右侧孤立的范围切换区域，让页面标题、同步信息和全局工具各归其位。
- 将 Dash 缓存版本提升到 `styles.css?v=93` 和 `app.js?v=88`，并将 `VERSION` 从 `1.0.0.13` 提升到 `1.0.0.14`。

### 优化 Token 页头来源同步布局

- Token 页头左侧更新时间文案从“更新于”改为“总账合并于”，明确它表示 `token-usage.*` 总账合并时间。
- 将各来源最后同步时间收进页头中间的“各来源最后同步”信息组，避免一排来源 pill 悬浮在页头空白区域。
- 保留右侧 `1d / 7d / 30d / all` 范围切换为紧凑控件，并将 Dash 缓存版本提升到 `styles.css?v=92` 和 `app.js?v=87`。
- 将 `VERSION` 从 `1.0.0.12` 提升到 `1.0.0.13`。

### 修复豆奶 Playwright 运行时缺失

- 复查确认 root crontab 仍保留豆奶 09:00 签到和 00:05 traffic closeout，但 2026-07-06 两个任务都因 Playwright 缺少 `/root/.cache/ms-playwright/chromium_headless_shell-1208` 失败。
- 在服务器 root 环境运行 `python3 -m playwright install chromium`，补齐 `chromium_headless_shell-1208` 和 `ffmpeg-1011`，并用 Playwright headless launch smoke test 确认 Chromium 可启动。
- 使用不发微信通知的 `/root/.openclaw/daily_checkin.sh` 手动补跑 2026-07-06 豆奶签到和数据同步；今日记录为 768 MB、1 豆丁、有效期延长 2.96 小时。
- 手动运行 `gen_checkin_data.py --traffic-only --exclude-today` 补跑真实流量日结，线上 `dounai_checkin.json` 的 `account` / `traffic_usage` 已清除 `stale` 和 `last_error`。
- 更新 `SERVER_RUNBOOK.md` 和 `CONTEXT.md`，记录 Playwright 浏览器缓存与豆奶自动化之间的依赖。
- 将 `VERSION` 从 `1.0.0.11` 提升到 `1.0.0.12`。

### 拆分 macOS Codex 独立账本

- 新增 `dash/data/codex-macos-usage.*`，macOS 本机 Codex 用量不再写入 Windows 兼容账本 `dash/data/codex-usage.*`。
- 新增 `python scripts/update_data.py codex-macos-usage`，采集 macOS 本机 `.codex/sessions` 后合并统一 `token-usage.*`。
- `scripts/sync_token_usage.py` 合并 OpenClaw、Codex Windows、Codex macOS 和 Codex server 多个来源，Token 页来源更新时间会显示各自账本更新时间。
- macOS launchd 上报脚本只允许提交 `dash/data/codex-macos-usage.*` 和 `dash/data/token-usage.*`，避免每小时上报覆盖 Windows 用量。
- 当前本机验证采集到 284 个 macOS Codex sessions，统一总账新增 `Codex macOS` 来源。
- 将 `VERSION` 从 `1.0.0.10` 提升到 `1.0.0.11`。

### 修正 Token 自然日范围和来源更新时间

- Token 页 `1d` 改为以当前浏览器本地日期 00:00 为边界，只统计今天自然日；`7d` / `30d` 改为包括今天在内的最近 7 / 30 个自然日。
- 当今天暂无 token 数据时，`1d` 显示 0，不再回退到最近一个有数据的日期。
- Token 页头新增分来源更新时间列表，展示 Codex Windows / macOS、OpenClaw、Codex server 等来源账本的最后同步时间。
- `scripts/sync_token_usage.py` 在统一总账的 `sources` 中保留来源 `updatedAt`，并为暂无 runs 的已知来源保留更新时间。
- 将 Dash 缓存版本提升到 `styles.css?v=91` 和 `app.js?v=86`，并将 `VERSION` 从 `1.0.0.09` 提升到 `1.0.0.10`。

### 新增 macOS 本机 Codex Token 上报

- 新增 `scripts/report_codex_usage.sh`，在 macOS 本机刷新 `dash/data/codex-macos-usage.*` 和 `dash/data/token-usage.*`，只允许提交这四个 usage 数据文件。
- 新增 `scripts/install_local_codex_usage_launchd.sh`，注册 `cn.maxnow.local-codex-usage-report` launchd 任务，默认每 1 小时运行一次本机上报。
- macOS 上报复用现有 Codex session `token_count` 采集和 Token 总账合并口径，来源默认显示为 `Codex macOS`，不导出 prompt / response 正文。
- 更新 `AGENTS.md`、`SPEC.md`、`CONTEXT.md`、`DEPLOY.md`、`SERVER_RUNBOOK.md`、`ROADMAP.md` 和 `scripts/check.py`，让后续代理和部署说明都能识别 macOS 上报入口。
- 将 `VERSION` 从 `1.0.0.08` 提升到 `1.0.0.09`。

## 2026-07-05

### 收敛 Home 外部输入和待推进重复项

- Home 不再单独展示“AI 外部输入”卡，外部 AI 信号统一进入 Last-30 的“最新信号 / 本周观察 / 近 30 天主线”三列模块。
- 将 Last-30 卡标题改为“外部输入”，让它成为首页唯一的外部信号入口。
- Home 渲染“待推进”时会跳过和“当前主线”同名的项目，避免同一条主线在相邻卡片重复出现。
- 将 Dash 缓存版本提升到 `styles.css?v=90` 和 `app.js?v=85`。

原因：

- Owner 确认首页的 AI 外部信号和主线/行动存在重复，需要先做低风险收敛，让 Home 更像状态工作站。

### 修正版本卡运行数据误报

- `scripts/sync_project_meta.py` 将 AI 信号、Last-30、服务器 Codex 用量和 Life foods 等自动生成数据纳入运行数据白名单。
- 服务器只有这些数据文件被自动化刷新时，版本卡不再误报为“有未提交代码改动”。

原因：

- 部署 Token 单位换算后复查发现，服务器运行数据恢复会让版本元数据误判为代码 dirty，需要修正生成器口径。

### 优化 Token 数值单位进位

- Token 页总量、来源、模型、会话和趋势图统一使用同一个数值格式化规则。
- 当 Token 数值达到 10 亿级时显示为 `B`，避免 `1009M` 这类难读表达。
- 将 Dash 脚本缓存版本提升到 `app.js?v=84`。

原因：

- Owner 指出 Token 总量超过 1000M 后没有单位换算，页面需要更自然地显示大额用量。

### 将 Last-30 摘要改回 AI 大事口径

- `scripts/sync_ai_last30.py` 不再外露“适合进入近 30 天观察池”这类采集器内部筛选话术。
- Last-30 左栏和本周栏优先选择模型、agent、研究、API、成本和开发者生态的实质 AI 变化。
- SDK release、普通 GitHub 开源更新和底层工程文章被降权；只有明确涉及模型、agent、MCP、API 或成本变化时才作为补充进入 AI 大事列表。
- 摘要文案改成“发生了什么 + 为什么值得看”，而不是“为什么被采集器收录”。

原因：

- Owner 指出 Last-30 是用来看 AI 大事的，不应该显示“适合进入 30 天观察池”等内部判断，也不应该让低层 SDK release 主导页面。

### 收紧 Last-30 外露信息口径

- 将 Last-30 左栏静态标签从 `Today` 改为 `Latest`，默认标题改为“最新信号”，避免最近 7 天回退数据被误读为当天信号。
- `scripts/sync_ai_last30.py` 生成左栏时最多展示 3 条最新信号，并把摘要改为“当前候选收录”，不再使用像完整统计一样的表达。
- 前端不再展示 `high confidence` / `medium confidence`，改为“来源较稳 / 自动观察 / 待核实”，强调这是来源和自动归类口径，不是 Owner 已确认判断。
- 近 30 天主线改为“当前候选中约 X 条相关信号”，并说明它是关键词自动归类，不等同于完整趋势统计。
- 将 Dash 脚本缓存版本提升到 `app.js?v=83`。

原因：

- Owner 询问 Last-30 当前外露信息是否准确；复核后确认单条来源事实基本可用，但栏目名、置信度和右侧数字容易显得过度确定，需要降为轻量观察雷达口径。

### 将本机 Codex 上报迁到专用 main clone

- 新增本机专用上报目录 `D:\Personal\MaxNow-token-report`，该目录保持在 `main`，只供 `MaxNow-Local-Codex-Usage-Report` 计划任务运行。
- 将 Windows Task Scheduler 的上报入口改为专用目录下的 `scripts/report_codex_usage_hidden.vbs`，避免日常开发分支影响本机 Codex Token 自动上报。
- 保留上报脚本的 `main` 与干净工作区保护：每次上报前仍会 `git pull --ff-only origin main`，只提交 `codex-usage.*` / `token-usage.*`，再推送到 `origin/main`。
- 加固服务器合并步骤：拉取 `origin/main` 前也暂存服务器本地生成的 `project-meta.*`，避免运行时元数据改动阻断本机 Token 上报。
- 将 `VERSION` 从 `1.0.0.01` 提升到 `1.0.0.03`，覆盖本次本机自动化运行目录调整和服务器合并加固。

### 建立 MaxNow 版本提升规则

- 将 `VERSION` 从 `1.0.0.00` 提升到 `1.0.0.01`，覆盖最近的云服务页重构和豆奶真实流量日结。
- 明确任何 Owner 可见或运维相关改动都要升 MaxNow 版本，并刷新 `dash/data/project-meta.*`。
- 小 UI / 文案 / 布局调整、新页面能力、新数据源和新自动化默认升最后两位；重要功能模块稳定落地升 patch；大版本阶段切换升 minor / major。
- 更新 `AGENTS.md`、`SPEC.md`、`CONTEXT.md` 和 `SERVER_RUNBOOK.md`，让后续 Codex 执行时有固定规则。

### 确认 OpenClaw Token 用量定时任务已接入

- 复查 root crontab 的 `MAXNOW-OPENCLAW-USAGE`，确认每天 00:20 运行 `python3 scripts/update_data.py openclaw-usage`。
- 服务器日志显示 2026-07-03、2026-07-04、2026-07-05 均以 `maxnow openclaw usage sync ok` 完成，线上 `openclaw-usage.json` 已更新到 2026-07-05 00:20。
- 云服务页 OpenClaw Token 用量状态从“待验证”改为“已接入”，文案改为 root crontab 已运行的事实口径。
- 将 Dash 脚本缓存版本提升到 `app.js?v=82`。

### 移除云服务页定时任务分组标题

- 移除云服务页“Cron Jobs / 定时任务”中段标题，让任务卡自然接在“系统与托管”卡后面，减少页面断层感。
- 清理不再使用的 `.cloud-section-head` 样式。
- 将 Dash 样式缓存版本提升到 `styles.css?v=89`，脚本缓存版本提升到 `app.js?v=81`。

### 清理服务器资源和 Chromium 重启风暴

- 停止并禁用失败循环的 `lighthouse-chromium.service`，该服务每 3 秒尝试启动 Chromium 但因 `/root/.openclaw/browser-existing-session/SingletonLock` 已被现有 OpenClaw 浏览器会话占用而退出。
- 将 systemd journal 从约 2.8G vacuum 到约 264M，根盘使用率从约 66% 降到约 56%。
- 清理 apt、npm、pnpm 和部分 Playwright 缓存；保留正在运行的 `/root/.cache/ms-playwright/chromium-1208`，避免打断现有 OpenClaw Chromium 会话。
- 复查后 `lighthouse-chromium.service` 状态为 `disabled / inactive`，最近日志不再继续刷失败重启。

### 精简云服务系统与托管细节

- 云服务“系统与托管”模块移除根目录、nginx 配置和托管检查三条低频实现细节。
- 云服务页的 nginx 状态只保留 `Active` 值，不再展示 `systemctl reports nginx is active` 说明。
- 将 Dash 脚本缓存版本提升到 `app.js?v=80`。

### 整理云服务页任务分组

- 云服务页第一张大卡从“系统状态”升级为“系统与托管”，合并 Host、站点域名、部署根目录、nginx 配置、托管检查和运行状态快照。
- 删除独立的 `TLS / nginx` 站点托管卡，让下方“定时任务”区域只保留真正按 cron 运行的任务。
- 豆奶任务卡标题从“豆奶签到”改为“豆奶自动化”，内部按 `00:05` 流量日结和 `09:00` 签到快照拆开说明。
- OpenClaw Token 用量状态从“待确认”收敛为“待验证”，表示 cron 已记录但仍需连续运行观察。
- 将 Dash 样式缓存版本提升到 `styles.css?v=88`，脚本缓存版本提升到 `app.js?v=79`。

### 收敛云服务页顶部摘要

- 移除云服务页顶部 Host / Runtime / Daily AI / Dounai 四个摘要卡，避免和下方任务详情卡重复。
- Host 信息改为云服务“系统状态”模块里的第一条，和 nginx、证书、CPU、磁盘、内存、运行时间等状态放在同一层级。
- 将 Dash 样式缓存版本提升到 `styles.css?v=87`，脚本缓存版本提升到 `app.js?v=78`。

### 增加豆奶真实流量 00:05 日结和前端图表

- 服务器 `/root/.openclaw/gen_checkin_data.py` 已备份到 `/root/.openclaw/gen_checkin_data.py.bak-20260705-traffic-closeout`，并新增 `--traffic-only --exclude-today` 模式。
- root crontab 已备份到 `/root/.openclaw/root-crontab-20260705-traffic-closeout.bak`，并新增 `MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT`：每天 00:05 只更新昨天及更早的真实流量使用量。
- 00:05 日结会从 `traffic_usage.daily` 和 `traffic_usage_history` 中剔除当天，避免当天 00:05 的不完整值污染历史。
- 豆奶详情页新增“近 30 天实际使用流量”图，放在“近 30 天日均可用流量”前面，并在前端排除当天。
- 云服务 tab 已补充豆奶 09:00 签到和 00:05 traffic closeout 两个 root 定时任务；`AGENTS.md` 新增规则：以后调整服务器 cron/systemd 时必须同步更新云服务 tab。

### 接入豆奶真实流量使用抓取

- 重新登录豆奶用户区后确认：`/user/trafficlog` 页面直接展示最近 7 天真实使用量，`/user/trafficlog?ajax=1` 返回近 12 小时节点活跃和节点流量占比数据。
- 已在服务器备份 `/root/.openclaw/gen_checkin_data.py` 到 `/root/.openclaw/gen_checkin_data.py.bak-20260705-traffic-usage`，并扩展该脚本读取流量日志。
- 线上 `dash/data/dounai_checkin.json` 已写入 `traffic_usage` 和 `traffic_usage_history`；当前有 2026-06-29 到 2026-07-05 的 7 条 direct daily usage。
- 后续每日豆奶自动化会把最近 7 天 direct usage 按日期合并进 `traffic_usage_history`，最多保留 60 天；00:05 traffic-only 日结负责把口径稳定在昨天及更早的完整日期。
- 这次没有新增前端入口，也没有增加账号写入、订阅重置、购买或手动录入；只是复用服务器登录态做只读抓取。

### 完成豆奶近 30 天真实流量使用调研

- 第一轮只读检查线上 `dash/data/dounai_checkin.json`、root 豆奶签到脚本、`gen_checkin_data.py` 和当天签到日志时，只能确认签到奖励记录与账号余量快照。
- 随后不局限于既有数据，登录豆奶用户区继续检查菜单和接口，发现 `流量日志` 页面就是可用的真实使用量来源。
- 账号余量差分口径保留为兜底估算说明；真实用量主口径改为 `traffic_usage_history`。

## 2026-07-02

### 新增生活 tab 和吃啥随机选择器

- Dash 左侧导航新增“生活”tab，放在云服务和同行记之间，当前功能区为“吃啥”。
- personal-wiki 新增 `wiki/life/food-picker.md`，首批候选为粉面菜蛋、红烧牛肉面、满小饱肥汁土豆粉、糟粕醋米粉。
- 新增 `scripts/sync_life_foods.py`、`dash/data/life-foods.*` 和 `python scripts/update_data.py life-foods`；`runtime`、`wrap all` 与 `scripts/check.py` 已纳入该数据集。
- 前端默认全选候选、数量默认 1；Owner 可以临时取消勾选部分菜品，点击“吃啥”后从当前勾选项中随机选取一个或多个不重复结果。
- 吃啥功能区调整为“抽签台”设计：结果舞台前置放大、候选变成可勾选菜品筹码、数量改为步进器，并在点击“吃啥”时使用从快到慢的滚轮动画，最终停在要吃的菜品上；数量为多个时展示上下叠放的独立滚轮，避免长轨道露出，选项和滚轮项使用一致的菜品颜色。
- 将 Dash 样式缓存版本提升到 `styles.css?v=86`，脚本缓存版本提升到 `app.js?v=76`。

### Personal Wiki 待办移除逐条打开入口

- Home 的“近期待办”条目改为纯展示卡片，不再追加每条待办的“打开”链接。
- 待办卡片本身也不作为跳转入口，只保留标题、模块和截止 / 状态标签。
- 同步更新 `SPEC.md` 中近期待办展示口径。
- 将 Dash 脚本缓存版本提升到 `app.js?v=71`。

原因：

- Owner 指出待办列表不需要每条都出现“打开”，点击页卡也不需要打开源页面。

### 同行记地图铺满地图卡宽度

- 同行记真实地图从固定正方形居中展示改为铺满地图卡横向宽度，并使用响应式高度约束。
- 同步更新 `STYLE_CONTEXT.md` 中的同行记地图样式约定，避免后续回退到正方形居中。
- 将 Dash 样式缓存版本提升到 `styles.css?v=83`。

原因：

- Owner 指出同行记页面地图没有铺满可用宽度，地图卡右侧出现大面积空白。

### 侧边栏豆奶和 Token 改回描述文案

- 左侧导航里的豆奶副文案固定为“签到状态”，不再显示今日流量。
- 左侧导航里的 Token 副文案固定为“用量概览”，不再显示当前范围 token 总量。
- 将 Dash 脚本缓存版本提升到 `app.js?v=70`。

原因：

- Owner 指出侧边栏这里只需要放描述，不需要展示多少流量或多少 token；具体数值保留在对应页面和首页卡片里。

### 优化 Last-30 条目摘要和点击行为

- Home 的 Last-30 条目改为整张卡片可点击，移除条目内部单独的“打开”链接。
- 条目补充显示来源和置信度元信息，并让摘要最多展示 4 行，提升扫读时的信息密度。
- 今日 / 本周列最多展示 4 条，近 30 天主线最多展示 5 条，减少右侧主线列空白。
- 将 Dash 样式缓存版本提升到 `styles.css?v=82`，脚本缓存版本提升到 `app.js?v=69`。

原因：

- Owner 希望 Last-30 能直接看到更多详细内容或摘要，不要在卡片里放单独“打开”文本，点击页卡本身即可跳转。

### 同步侧边栏 Token 范围口径

- 侧边栏 Token 小摘要改为显示范围前缀，例如 `1d 86M` / `7d 137M`，避免裸数字被误解。
- Token 页面切换 `1d / 7d / 30d / all` 时，侧边栏同步当前选中范围；其他页面默认显示 `7d` 摘要。
- 将 Dash 脚本缓存版本提升到 `app.js?v=68`。

原因：

- Owner 指出 Token 页当前选中 `1d` 且主卡显示 `86M`，但侧边栏仍显示 `137M`；原逻辑固定展示 7 天总量且没有标注范围。

### 修正 Home hover 主题色优先级

- 修正 Home 顶部指标卡 hover 主题色被 `.status-strip article` 通用规则覆盖的问题；“待推进 / Token / 系统自动化”现在分别使用橙色、紫色、绿色。
- 天气卡 hover 按天气语义色走，晴天使用橙色，阴 / 雾使用青色，雨雪使用蓝色；时间卡使用橙色。
- 将 Dash 样式缓存版本提升到 `styles.css?v=81`。

原因：

- Owner 指出全局主题色 hover 后首页看起来没有被覆盖；实际是 Home 部分模块进入了 hover 规则，但语义色变量被通用选择器覆盖，视觉上仍像默认蓝色。

### 压缩 Home 当前主线模块高度

- Home 的“当前主线”模块改为更紧凑的内容自适应样式，减少只有一条主线时的大面积空白。
- 同步压缩“待推进”条目的垂直留白，让首屏信息密度更接近状态工作站。
- 将 Dash 样式缓存版本提升到 `styles.css?v=80`。

原因：

- Owner 指出“当前主线”只有少量内容却占据过大位置，影响首屏扫读。

### 移除顶栏系统自动化重复状态

- 删除 Dash 顶栏右侧 `系统自动化 正常` 状态 badge，避免和 Home 首屏的“系统自动化”状态卡重复。
- 保留 Home 状态卡作为系统自动化健康入口，继续展示状态、更新时间和 hover 提示。
- 将 Dash 脚本缓存版本提升到 `app.js?v=67`。

原因：

- Owner 指出顶栏状态和下方系统自动化卡表达重复，要求删除顶部那个。

### 全局统一模块主题色 hover

- Dash 全局卡片 hover 改为使用模块自己的 `--card-color` / `--card-border`，内部条目使用自身 `data-tone` 或所在模块语义色。
- Home、Token、云服务、豆奶、同行记等主要模块补齐主题色 hover；内部任务、wiki 待办、AI 信号、Last-30、模型、调用、系统项、云服务 meta 和同行记条目也获得对应主题色悬浮反馈。
- 修正 Token 命中率摘要卡使用不存在的 `--green` 变量，改为 `--ok`。
- 将 Dash 缓存版本提升到 `styles.css?v=79` / `app.js?v=66`。

原因：

- Owner 希望 MaxNow 所有模块都像 Token 来源卡一样，鼠标悬浮时大模块用大模块主题色，内部模块用内部模块主题色。

### Last-30 今日列改为最新信号回退

- `scripts/sync_ai_last30.py` 的 Last-30 左列优先显示当天 AI 信号；如果当天暂无新条目，则回退为“最新 AI 信号”，从最近 7 天内选择最新高相关条目。
- 更新 `SPEC.md` 和 `CONTEXT.md`，记录该列不是严格空白的当天桶，而是“当天优先、最新回退”的扫读入口。

原因：

- Owner 发现 Last-30 的 Today 左列长期空白；服务器任务通常在 00:00 刷新，免费公开源当天还没有新条目时，严格按当天日期过滤会导致页面空白。

### 将 Home 今日推进改为待推进

- Home 指标卡和列表标题从“今日推进”改为“待推进”，避免误解为当天已完成事项或每日自动排班。
- 待推进仍读取 `dash/data/dashboard.json` 的 `actions`，数据来自 `ROADMAP.md` 的 Now / Next，并由 `python scripts/update_data.py project-status` 显式刷新。
- 更新 `scripts/update_data.py`、`SPEC.md`、`CONTEXT.md` 和 `ROADMAP.md` 中的对应口径。
- 将 Dash 缓存版本提升到 `styles.css?v=78` / `app.js?v=65`。

原因：

- Owner 询问“今日推进”到底是今天要做还是今天已完成，并指出每天看到的数据相同；原标题不符合它的 ROADMAP 来源和非自动日更语义。

### 澄清 Home 系统自动化状态口径

- 顶栏状态从 `OpenClaw 正常` 改为 `系统自动化 正常`，避免把服务器自动化聚合状态误解成 OpenClaw agent 本体状态。
- Home 指标卡标题从“自动化”改为“系统自动化”，和 `dashboardData.automation` 的实际含义对齐。
- 顶栏状态和 Home 系统自动化卡增加 hover 提示，展示 nginx、证书、部署、cron、失败日志和资源快照等聚合摘要。
- 将 Dash 缓存版本提升到 `styles.css?v=77` / `app.js?v=64`。

原因：

- Owner 询问顶栏 `OpenClaw 正常` 和 Home `自动化 正常` 分别指服务器、OpenClaw 还是自动化链路；原文案会混淆来源。

### 移除 Token 来源面板底部说明

- Token 页来源费用面板不再显示“费用为估算值；缓存命中率按可缓存输入计算。”说明，避免只有一个来源时形成突兀的底部说明条。
- 缓存命中率继续保留在顶部摘要卡，来源面板只展示来源、Token、估算费用和 runs。
- 将 Dash 缓存版本提升到 `styles.css?v=76` / `app.js?v=63`。

原因：

- Owner 反馈这句说明放在来源费用面板底部位置不合理。

### 避免 Home 自动化状态停留在旧异常

- Home 顶部指标卡将“数据”改为“自动化”，和它实际展示的 `dashboardData.automation.status` 对齐。
- Dash 前端新增每 5 分钟自动重新拉取数据，复用已有 `cache: no-store` 取数逻辑，避免浏览器长时间停留在旧页面时持续显示已恢复的异常状态。
- 将 Dash 缓存版本提升到 `styles.css?v=75` / `app.js?v=62`。

原因：

- Owner 发现 Home 右侧状态卡一直显示 `异常`；线上数据已经恢复为 `正常`，但旧页面没有自动刷新，容易误导。

### 修正 OpenClaw 异常误报

- `scripts/sync_system_status.py` 的部署状态检查补充 `codex-server-usage.*` 和 `ricky.*` 运行态数据白名单，避免服务器自动化生成的数据文件让 deploy check 误判失败。
- 失败日志检查忽略自身写入或运行日志捕获到的 `[ok] status ... checks failed` 摘要，避免上一轮状态摘要反复触发 `failure-log` 失败。
- 部署状态检查忽略 Python 运行时生成的 `__pycache__` / `.pyc` 文件，避免只读诊断命令留下缓存后触发异常。
- `scripts/update_data.py runtime` 将 system-status 调整到运行态同步最后执行，避免先检查、后改写 project-meta / ricky 等数据造成短暂误报。
- system-status 摘要现在会输出失败项名称，例如 `checks failed: deploy`，避免只有失败数量但不可定位。
- 失败日志检查改为按每个日志的最新 ok / fail 结果判断；如果天气等同步曾经失败但后续已经成功，不再持续显示 `OpenClaw 异常`。

原因：

- Owner 发现顶栏长期显示 `OpenClaw 异常`；排查后确认是系统状态聚合脚本误报，不是 nginx、证书、cron 或 OpenClaw 本体故障。

### 收紧 Token 来源费用布局

- Token 页将“来源费用”移动到和“模型占比”“调用消耗”同一行，形成三个并列信息面板。
- 删除来源列表独占整行的布局，避免 `1d` 只有一个来源时占用一整条空白行。
- 将费用 / 缓存命中率说明改为来源面板底部的短中文提示，不再使用英文横向说明条。
- 将 Dash 缓存版本提升到 `styles.css?v=74` / `app.js?v=61`。

原因：

- Owner 反馈来源费用应和模型占比、Calls 同层展示，否则只有一个来源时浪费页面空间。

### 修正 Token 来源卡展示和范围口径

- 将 Dash 缓存版本提升到 `styles.css?v=73` / `app.js?v=60`，避免线上继续使用旧 CSS 导致来源列表以裸文本显示。
- Token 来源列表改为按当前 `1d` / `7d` / `30d` / `all` 范围聚合，来源 token、费用和 runs 不再固定显示全量。
- `scripts/sync_token_usage.py` 在统一总账的每日数据中写入 `bySource`，供前端准确计算分来源范围小计。
- 本机 Codex collector 默认按采集机器平台命名来源：当前 Windows 本机显示为 `Codex Windows`，后续 macOS 采集端可显示为 `Codex macOS`。

原因：

- Owner 反馈 Token 页来源列表居中裸排不好看，并且来源量级也应跟随顶部范围切换。

### 接入服务器 Codex Token 用量

- 新增 `dash/data/codex-server-usage.*`，作为服务器 `/root/.codex/sessions` 的独立 Codex 用量账本，避免覆盖本机 `dash/data/codex-usage.*`。
- `scripts/update_data.py` 新增 `codex-server-usage` 命令，使用 `codex-server` 来源 ID 刷新服务器账本并合并 `dash/data/token-usage.*`。
- `scripts/sync_token_usage.py` 将 OpenClaw、Codex local、Codex server 三路来源合并进统一 Token 总账。
- Token 页面新增来源列表，显式展示 OpenClaw、Codex local、Codex server 的总量、估算费用和 runs；后续已修正为按当前范围展示并用平台名区分本机 Codex。
- 云服务页新增 Codex Server Token 用量卡，记录 cron 标记、锁、日志和写入文件。
- 本机 Codex 上报脚本的服务器合并步骤会保留 `codex-server-usage.*`，避免本机每小时上报覆盖服务器账本。
- 更新 `AGENTS.md`、`SPEC.md`、`CONTEXT.md`、`ROADMAP.md` 和 `SERVER_RUNBOOK.md`，记录服务器 Codex collector、root cron、日志、锁、权限和分源展示边界。

原因：

- Owner 希望先完成服务器侧 Codex 用量接入，并让 Token 页清楚区分本机 Codex 和服务器 Codex。

## 2026-06-27

### 收敛豆奶日均流量图 y 轴刻度

- 豆奶“近 30 天日均可用流量”图保留动态缩放，但 y 轴边界改为整数 GB，例如 4GB 到 5GB，避免左侧出现 4.16GB、4.20GB 等过细刻度。
- 点位标签继续保留两位小数，方便看见每日实际波动。
- 将 Dash 脚本缓存版本提升到 `app.js?v=58`。

原因：

- Owner 反馈放大波动后 y 轴至少应保持整数刻度，例如 4-5，而不是小数刻度。

### 优化图表刻度和 Token 默认范围

- 折线图 y 轴新增动态刻度：当数据长期处在高位小幅波动时，不再强制从 0 开始，避免豆奶日均可用流量这种 4GB 左右的波动被压成一条直线。
- Token 页面默认范围从 `7d` 改为 `1d`，进入页面后直接展示当天用量。
- 将 Dash 脚本缓存版本提升到 `app.js?v=57`。

原因：

- Owner 反馈豆奶日均可用流量图左侧刻度固定为 0-5GB，看不出 4GB 左右的细微变化；Token 页每次打开默认 7d，不符合当前查看习惯。

### 本机 Codex Token 定期上报

- 新增 `scripts/report_codex_usage.ps1`，在 Windows 本机刷新 Codex 用量账本，只允许提交 `dash/data/codex-usage.*` 和 `dash/data/token-usage.*`，遇到无关脏文件会停止。
- 新增 `scripts/install_local_codex_usage_task.ps1`，注册 `MaxNow-Local-Codex-Usage-Report` 计划任务，默认每 1 小时静默上报一次本机 Codex Token 用量。
- 计划任务注册为 hidden task，并使用 `powershell.exe -WindowStyle Hidden`，避免自动运行时弹出命令行窗口。
- 2026-07-02 将计划任务 action 改为 `wscript.exe scripts/report_codex_usage_hidden.vbs`，由 VBS 以 window style 0 启动 PowerShell 上报脚本，避免 `powershell.exe -WindowStyle Hidden` 仍可能出现的一瞬间 console 闪窗。
- 上报脚本推送后通过 SSH 让服务器拉取最新 `main`，并只运行 `python3 scripts/update_data.py token-usage` 合并现有源账本，避免在服务器上刷新空的本机 Codex 数据。
- 首次手动上报采集到 86 个本机 Codex usage sessions；随后修复 PowerShell 远端 bash 脚本 CRLF 和 SSH 失败未冒泡问题。
- 2026-06-27 进一步修复静默任务：远端合并改为 base64 SSH payload，服务器输出进入 `logs/local-codex-usage-report.log`，`git pull` 的 stderr 进度不再被误判为失败；隐藏计划任务手动启动验证 `LastTaskResult=0`。
- 更新 `SPEC.md`、`CONTEXT.md`、`ROADMAP.md`、`DEPLOY.md`、`SERVER_RUNBOOK.md`、`AGENTS.md` 和 `scripts/check.py`，记录本机定期上报边界与剩余服务器 Codex collector 待办。

## 2026-06-24

### 接入本机 Codex Token 统计

- 新增 `scripts/sync_codex_usage.py`，从 `.codex/sessions` 的 `token_count` 事件生成 `dash/data/codex-usage.*`，只导出 token 统计，不导出 prompt / response 正文。
- Codex 模型名优先读取 `turn_context.model`，模型占比和调用列表展示 `gpt-5.5` 等具体模型，而不是工具名 `Codex`。
- Codex 费用按 OpenAI API 等价价格估算，缓存命中率按 `cached input / cacheable input` 展示。
- 新增 `scripts/sync_token_usage.py` 和 `dash/data/token-usage.*`，把 OpenClaw 与 Codex 源账本合并成 Token 页统一总账。
- Token 页优先读取 `token-usage.*`，保留原有 1d / 7d / 30d / all、模型占比、最近调用和 30 天趋势。
- `scripts/update_data.py` 新增 `codex-usage` 和 `token-usage` 命令，`scripts/check.py` 纳入新账本和 wrapper 校验。
- 将 Dash 缓存版本提升到 `app.js?v=55`。

原因：

- Owner 希望在已有 OpenClaw Token 消耗上报基础上统计 Codex 流量，并先把未落地的自动化记录为后续待办。

### 修正同行记地图标签和比例

- personal-wiki 的 Ricky 旅行地点新增 `map_label`，MaxNow 同步为 `mapLabel`，地图 marker 不再自动截取地点名前两个字。
- 当前 11 个地点的地图标签明确为：北京、札幌、东京、北海、大理、大同、天路、天津、沈阳、布统、阿那亚。
- 同行记地图容器改为正方形，居中展示，保留 Leaflet 真实地图和 SVG fallback。
- 将 Dash 缓存版本提升到 `styles.css?v=71`、`app.js?v=54`。

原因：

- Owner 反馈不应只修北海道，所有 marker 都要举一反三检查；乌兰布统不能被截成“乌兰”，地图比例希望改成正方形。

### 调整同行记地图展示

- 将北海道地图点的显示名缩短为“北海”，减少札幌附近 marker 挤压。
- 同行记页面左右留白收窄，地图高度提高，并降低地图自动 fit 的最大缩放，让地图更宽、更能显示周边区域。
- 将 Dash 缓存版本提升到 `styles.css?v=70`、`app.js?v=53`。

原因：

- Owner 反馈北海道 marker 文字过长，且当前地图略小，希望明显更宽并显示更多一点。

### 新增我和 Ricky 的同行记 tab

- Dash 左侧导航新增“同行记”tab，副标题为“我和 Ricky”。
- 新增同行记页面，包含真实地图和统计卡片；地点与旅行记录暂时只进入地图 marker / popup，不单独铺列表。
- personal-wiki 新增 `wiki/relationships/ricky-travel.json`，从 `wiki/relationships/ricky.md` 抽取旅行、出游、地点和待确认日期。
- 新增 `scripts/sync_ricky_travel.py` 和 `python scripts/update_data.py ricky-travel`，将 personal-wiki 旅行数据同步到 `dash/data/ricky.json` / `dash/data/ricky.js`；当前同步得到 12 个地点和 4 条记录。
- `scripts/update_data.py runtime`、`wrap all` 与 `scripts/check.py` 已纳入 `ricky` 数据刷新 / wrapper 校验。
- 地图改为 Leaflet + OpenStreetMap 真实地图，使用 personal-wiki 中的经纬度渲染 12 个 marker；内置 SVG 地图保留为 fallback。
- 地图瓦片改用更柔和的 CARTO Voyager 样式，并替换默认 marker 为圆润彩色自定义 marker，让同行记页面更接近卡通 / 手账感。
- 撤下页面右侧的地点列表和旅行记录列表，让同行记先保持地图优先。
- 左侧导航顺序调整为：首页、豆奶、Token、云服务、同行记，将同行记放到最后一个 tab。
- 将 Dash 缓存版本提升到 `styles.css?v=69`、`app.js?v=52`。
- 更新 `AGENTS.md`、`SPEC.md`、`STYLE_CONTEXT.md`、`CONTEXT.md` 和 `ROADMAP.md`，记录新入口、数据边界和后续维护口径。

原因：

- Owner 希望不要新增泛旅行 tab，而是新增一个“我和 Ricky”的独立左侧入口，用来承载两人的旅行记录和世界地图。

### 记录噗噗每日待办提醒待办

- 更新 `ROADMAP.md`，加入“让噗噗每日提醒 personal-wiki 待办”后续项。
- 初步方向是由服务器 cron 汇总当天或近期未完成待办，再让噗噗 / OpenClaw 主动提醒 Owner。
- 记录提醒渠道、发送时间、消息格式、失败日志和发送确认边界，避免自动消息越界。

### 让 Home 系统状态跳转云服务

- Home 系统状态卡支持点击、Enter 和 Space 直接进入“云服务”页。
- 云服务页新增系统状态卡，复用 `dashboardData.system` 展示 nginx、证书、部署版本、CPU、磁盘、内存和运行时间等快照。
- 将 Dash 缓存版本提升到 `styles.css?v=65`、`app.js?v=47`。

### 调整 Home 卡片右上操作

- Personal Wiki 近期待办右上入口从“查看”改为“更多”。
- Home Token 近期用量卡去掉右上“查看”按钮，改为显示 Token 数据更新时间。
- 将 Dash 缓存版本提升到 `styles.css?v=64`、`app.js?v=46`。

原因：

- Owner 希望近期待办入口文案更像列表扩展，Token 摘要右上角像豆奶签到一样显示更新时间。

### 调整云服务卡片信息层级

- 强化云服务页自动化卡片顶部的频率、标题、状态和说明文案。
- 弱化底部日志、写入、边界等明细行，让它们作为辅助信息呈现。
- 将 Dash 样式版本提升到 `styles.css?v=63`。

原因：

- Owner 希望云服务卡片底部明细弱一点，顶部主信息更突出。

### 云服务页补充天气同步展示

- 在“基础运行同步”卡里显式列出天气日志 `logs/weather.log`。
- 补充该 cron 写入 `dash/data/dashboard.*`、`wiki-todos.*` 和 `project-meta.*`，避免误以为天气没有被定时任务覆盖。

原因：

- Owner 发现云服务页只写了 `runtime` 和总日志，没有把天气同步单独展示出来。

### 天气卡显示更新时间

- Home 天气卡增加短更新时间，展示为 `HH:mm 更新`，用于区分“天气源当前如此”和“数据同步卡住”。
- 天气更新时间读取 `dashboard.json.weather.updatedAt`，不新增前端天气请求。
- 将 Dash 缓存版本提升到 `styles.css?v=62`、`app.js?v=45`。

原因：

- Owner 希望直接在天气卡里看到自动同步时间。

### 修复豆奶顶部间距和 Token 范围选项

- 恢复 Token 页头的“标题 + 右侧范围切换”布局，避免 `1d / 7d / 30d / all` 铺满整行。
- 给豆奶详情页顶部三块 tab 显式补充外层间距，避免今日签到、账号余量和签到累计贴得过近。
- 更新 `STYLE_CONTEXT.md`，记录 Token 范围切换应保持右侧紧凑选项。
- 将 Dash 样式版本提升到 `styles.css?v=61`。

原因：

- Home 顶部 widget 拆分时共享页头样式误伤 Token 页头，同时豆奶顶部继承后缺少外层 grid gap。

### 新增云服务 tab

- Dash 左侧导航在 Token 下方新增“云服务”tab。
- 新增云服务只读页面，列出服务器上的基础运行同步、Last-30 AI 信号、豆奶签到、OpenClaw Token 用量方案、nginx / HTTPS 托管等自动化与日志边界。
- 将 Dash 缓存版本提升到 `styles.css?v=60`，沿用最新脚本版本 `app.js?v=44`。
- 更新 `SPEC.md` 和 `CONTEXT.md`，记录云服务页的定位和只读边界。
- 已将云服务 tab 部署到 `dash.maxnow.cn`，服务器快进到提交 `8aa8400`，并通过 `python3 scripts/check.py`、`sudo nginx -t` 和 nginx reload。

原因：

- Owner 希望把服务器上已有自动化集中列成一个新 tab，并放在 Token 下面。

### 优化天气卡底部自适应

- 天气卡底部信息行增加自动适配：当地点、天气状态和低温 / 高温接近溢出时，前端会把该行字号从正常尺寸逐级收小，优先保持单行可扫读。
- 将 Dash 缓存版本提升到 `styles.css?v=60`、`app.js?v=44`。

原因：

- Owner 反馈“小毛毛雨”等较长天气状态接近卡片边界时，应自动减小字号而不是挤出卡片。

## 2026-06-23

### 优化 Home 天气卡层级

- 为天气卡底部的地点、天气状态和低温 / 高温之间加入轻量分隔点，让“海淀 / 小毛毛雨 / 19°/29°”这类信息在同一行里更容易扫读。
- 调整天气卡结构，把地点和天气图标合并为顶部弱信息行，中间突出当前温度，下方展示天气状态和今日高低温。
- 天气卡字号、间距和主数字层级对齐右侧小日历，避免图标和文本竖向堆叠后显得突兀。
- 进一步放大天气图标、适当收小温度字号，并把天气状态和今日高低温收敛到同一行。
- 将天气卡调整为左侧大图标、右侧地点 + 当前温度同组展示，并把温度范围改为低温 / 高温顺序。
- 将天气卡改为三排：第一排最大天气图标，第二排当前温度，第三排地点、天气状态和低温 / 高温。
- 放大天气卡和小日历内部内容，不改变两个 widget 的外框尺寸和顶部等高约束。
- 继续放大天气卡和小日历内部内容，让两个 widget 的信息量更饱满。
- 将 Dash 样式缓存版本提升到 `styles.css?v=58`。

原因：

- Owner 反馈天气卡内部元素观感奇怪，和右侧日期卡不搭。

### 记录 UI widget 约束和验收规则

- 更新 `STYLE_CONTEXT.md`，明确新增或移动卡片 / widget 时必须继承同族组件规则，包括圆角、边框、阴影、hover / focus、transition、语义色、响应式约束和缓存版本。
- 补充 Home 顶部天气卡 / 小日历这一组 widget 的等高规则：桌面端必须与 Today Status 卡片同顶、同底、等高，并保持同组悬浮反馈。
- 更新 `AGENTS.md`，要求 UI 改动把 `STYLE_CONTEXT.md` 当执行清单，并用浏览器或 DOM measurement 验证同排卡片的 top、bottom、height 和横向溢出。

原因：

- Owner 反馈新增天气卡和小日历漏套既有卡片约束，导致高度不齐、hover 反馈不一致；以后同类改动需要在仓库规则里直接拦住。

### Home 顶部增加海淀天气卡和定时刷新

- 将天气从小日历中拆出，放到 Home 顶部右侧、小日历左边的独立天气卡。
- 将天气卡和小日历从 Today Status / 整理模式卡片中拆出，作为顶部同级小组件展示。
- 对齐顶部小组件区和 Home 右侧栏宽度，并为天气卡、小日历补齐统一 hover 悬浮效果。
- 将顶部天气卡、小日历和 Today Status 卡片高度锁为同一行等高。
- 天气卡增加 SVG 图标，支持晴、多云 / 阴、雨、雷阵雨、雪、雾等状态。
- 新增 `scripts/sync_weather.py`，用 Open-Meteo 免费 forecast API 刷新北京市海淀区天气、温度、今日高低温和图标类型。
- `python scripts/update_data.py weather` 可单独刷新天气，`runtime` 也会一并刷新，因此服务器现有 10 分钟定时任务部署后即可更新天气。
- 前端只读取本地数据展示，不在浏览器端请求外部天气接口。
- 将 Dash 缓存版本提升到 `styles.css?v=52`、`app.js?v=41`。

原因：

- Owner 希望天气放在小日历左侧独立区域，并带太阳、多云、下雨等对应图标，同时具备定时更新逻辑。

### 记录近 30 天流量使用调研待办

- 更新 `ROADMAP.md`，加入“调研近 30 天流量使用情况”待办。
- 明确该任务先确认是否能拿到真实使用量，避免和现有豆奶签到获取流量、账号剩余流量、日均可用流量混淆。

原因：

- Owner 希望看看能不能拿到近 30 天流量使用情况。

### 补充轻量记录直接合入规则

- 更新 `AGENTS.md`，明确 Owner 要求“记录一下”“加个待办”“记个待办”等轻量文档记录时，完成文档更新和必要检查后默认直接合入远端 `origin/main`。
- 如果改动存在明显风险、包含无关改动，或 Owner 明确要求不要合并，则仍需先停下来确认。

原因：

- Owner 希望这类轻量记录请求不再停在本地分支或 PR，而是完成后直接同步到远端主分支。

### 记录旅行地图待办

- 更新 `ROADMAP.md`，将“我和 77 一起去过哪里”的旅行地图加入 `Next`。
- v1 定位为只读地点地图，先记录地点、时间、同行人、简短备注和可选照片入口，不扩展成完整游记或社交分享。

原因：

- Owner 希望给 MaxNow 增加一个记录两人共同旅行足迹的待办。

### 接入 AI Last-30 每日 0 点同步

- 服务器 `ubuntu` 用户 crontab 新增 `MAXNOW-AI-LAST30-SYNC` 标记块。
- 每天服务器本地时间 00:00 运行 `python3 scripts/update_data.py ai-last30`。
- 日志写入 `/var/www/maxnow-dashboard/logs/ai-last30.log`。
- 同步更新 `SERVER_RUNBOOK.md`、`CONTEXT.md` 和 `ROADMAP.md` 中的自动化状态记录。

### 补充 UI 交付质检清单

- 在 `STYLE_CONTEXT.md` 增加 UI 质检清单，覆盖 4px 间距、图标对齐、少量颜色变量、字体层级、轻量微动效、资产导出和标识方向边界。
- 明确这些内容作为样式检查 checklist 使用，不升级为复杂设计系统或年度趋势驱动的 logo 改造。

原因：

- Owner 希望把 GPT 推荐的设计规范中真正有用的部分沉淀到 MaxNow 项目上下文里。

## 2026-06-22

### 接入免费 AI 外部信号版 Last-30

- 新增 `scripts/sync_ai_last30.py`，用免费公开源抓取、打分、去重并刷新 `dash/data/ai-news.*` 和 `dash/data/last-30.*`。
- 新增 `python scripts/update_data.py ai-last30` 统一入口，并把脚本纳入 `scripts/check.py` 必要文件检查。
- 将 Last-30 产品口径调整为“AI 外部信号滚动记忆”，不再默认记录 MaxNow 内部项目流水。
- 明确 X / Twitter 暂不作为基础来源；只有 Owner 批准付费 API 和博主白名单后再接入。
- 采集脚本本身不调用模型、不消耗 token；若后续让 OpenClaw 二次摘要，应只处理少量候选。

### 微调左侧导航对齐

- 品牌区增加和导航项一致的左侧内缩，让 MaxNow 图标 / 文本与下方导航图标 / 文本共用同一组视觉轴。
- 轻微收紧导航项高度，降低选中态胶囊在收窄侧栏里的视觉重量。
- 将 Dash 样式缓存版本提升到 `styles.css?v=48`。

#### 背景

- Owner 反馈收窄后的侧栏看起来有点怪；实际原因是品牌区与导航项的横向对齐轴不一致，选中态背景放大了这种错位。

### 完成时间卡片特殊日期和侧栏收窄

- Home 时间卡片新增 `dashboard.json.specialDates` 支持，可按固定公历日期或一次性日期显示生日、纪念日等当天提醒。
- 没有命中特殊日期时继续显示“今日无节日”，不扩展为完整日历。
- Dash 左侧导航栏桌面宽度从 238px 收窄到 210px，并同步收紧图标、padding 和 nav item 间距。
- 将 Dash 缓存版本提升到 `styles.css?v=47`、`app.js?v=39`。

#### 背景

- Owner 指定下一步处理“时间卡片显示纪念日 / 生日等特殊日期”和“收窄左侧导航栏”。

### 精简系统状态版本展示

- Home 系统状态里的 `MaxNow 版本` 只保留版本号，不再显示 branch、commit 和运行数据说明。
- `scripts/sync_system_status.py` 后续生成系统状态时也不再为版本项写入说明文本。

#### 背景

- Owner 希望系统状态卡片里的版本展示更干净，只看版本号即可。

### 修正豆奶日均可用显示

- 豆奶账号余量里的“日均可用”改为 GB/TB 两位小数展示，例如 `4.20 GB/d`。
- 近 30 天日均可用流量图的点位标签同步改为两位小数。
- 折线图 x 轴始终显示首尾日期，避免只有两条账号余量快照时末尾日期（如 6/22）被省略。

#### 背景

- Owner 反馈日均可用精度不够，并且日均可用图的最新日期没有显示。

### 增加 MaxNow 版本和最近更新模块

- 新增根目录 `VERSION`，版本号格式固定为 `x.x.x.xx`，当前为 `1.0.0.00`。
- 新增 `scripts/sync_project_meta.py` 和 `dash/data/project-meta.*`，从 `VERSION`、Git 状态和 `UPDATE_LOG.md` 生成前端可读的项目元信息。
- Home 右侧新增“MaxNow 最近更新”模块，展示版本号、部署说明和最近更新摘要。
- 系统状态里的部署项改为显示 `MaxNow 版本`，主值使用 `v1.0.0.00`，commit 和工作区状态放进说明。
- Home Token 摘要改为三格：`1d`、`7d`、`all day`。

#### 背景

- Owner 希望部署版本显示更直白，并能在 Home 看见 MaxNow 最近做了什么。

### 记录左侧导航栏收窄待办

- 更新 `ROADMAP.md`，将“收窄左侧导航栏”加入 `Next`。
- 明确只做宽度和响应式检查，不额外引入折叠侧栏等交互。

原因：

- Owner 反馈当前左侧栏过宽，希望适当短一点，把空间让给主内容区。

### 记录时间卡片特殊日期待办

- 更新 `ROADMAP.md`，将“时间卡片智能显示纪念日、生日等特殊日期”加入 `Next`。
- 明确该能力只服务首页时间卡片的今日提醒，不扩展成完整日历。

原因：

- Owner 希望当前时间区域不只显示农历和节日，还能智能提示当天是否有纪念日、谁的生日等个人特殊日期。

## 2026-06-21

### 微调 Token 趋势和调用列表

- Token 最近 30 天折线图在进入 Token 页后会二次按实际容器宽度重绘，避免首次进入时图表只占左半边。
- Token 顶部 `缓存读` 改名为 `缓存`。
- 调用列表从“会话消耗”改为“调用消耗”，单条记录标题补时间，避免同类 OpenClaw 调用看起来像同一个 session。
- Home Token 摘要数字缩小到和豆奶摘要同级，并将 Dash 缓存版本提升到 `styles.css?v=45`、`app.js?v=35`。
- 在 `ROADMAP.md` 补充 Codex 用量接入待办：先确认本地 / 服务器 Codex usage 来源，再生成独立日账本并合并进统一 Token 总账。

#### 背景

- Owner 反馈 Token 折线图首次进入宽度不足、调用列表名称重复易误解、缓存字段命名和 Home Token 摘要尺寸需要继续对齐。

### 对齐 Home Token 摘要样式

- Home 右侧 Token 摘要卡改为和豆奶摘要一致的指标结构：标题前补小图标，标题和数字居中。
- 统一 Token 指标卡的数字大小、语义色和白底小卡片质感。
- 将 Dash 样式版本提升到 `styles.css?v=44`。

#### 背景

- Owner 希望 Token 摘要里的字体、大小、颜色和标题前图标对齐豆奶摘要卡。

### 调整 Token 页结构和统计口径

- Token 顶部统计从总量 / 输入 / 输出 / 费用扩展为总量 / 输入 / 输出 / 缓存 / 费用，解释 OpenClaw total 与 input + output 的差异。
- 将模型占比缩短为左侧紧凑模块，并新增会话消耗模块，与模型占比并排展示。
- 最近 30 天趋势改为独立长模块折线图，避免条形列表把右侧卡片拉得过长。
- 将 Dash 脚本版本提升到 `app.js?v=34`。

#### 背景

- Owner 发现总量与输入 / 输出不相等，需要把 cacheRead 单独展示，同时希望 Token 页的布局更适合扫读。

### 接入 OpenClaw Token 页面和每日刷新

- Token 页面改为优先读取 `dash/data/openclaw-usage.*`，提供 1d / 7d / 30d / all 范围切换。
- 模型占比会随当前范围变化，趋势图展示最近 30 天日桶。
- Home 的 Token 摘要从 24 小时改为 1 天 / 30 天。
- `scripts/sync_openclaw_usage.py` 默认采集长期窗口，让 all 覆盖当前可读的全部 OpenClaw trajectory。
- 服务器侧新增 root 计划任务：每天 00:20 单独运行 `python3 scripts/update_data.py openclaw-usage`，日志写入 `logs/openclaw-usage.log`；任务结束后把生成的数据文件归属恢复为 `ubuntu:www-data`。

#### 背景

- Owner 希望 Token 页直接展示 OpenClaw 真实用量，并按 1d / 7d / 30d / all 查看，同时每天自动更新。

### 调整豆奶详情页今日签到区

- 将豆奶详情页顶部左侧从单纯“豆奶签到”标题卡改为今日签到指标区。
- 新增今日流量、今日豆丁、今日延长三张白底小指标卡，和 Home 豆奶摘要使用同一份今日数据。
- 顶栏 tab 标题从“豆奶签到”收敛为“豆奶”，并将 Dash 缓存版本提升到 `styles.css?v=43`、`app.js?v=32`。

#### 背景

- Owner 希望去掉豆奶页左侧大标题里的“豆奶签到”，改成参考 Home 摘要的小卡片布局。

### 建立 OpenClaw Token 用量账本

- 新增 `scripts/sync_openclaw_usage.py`，从服务器 OpenClaw trajectory 只读解析 `usage.input`、`usage.output`、`usage.cacheRead` 和 `usage.total`。
- 新增 `dash/data/openclaw-usage.json` 和 `dash/data/openclaw-usage.js`，按北京时间日桶、模型和任务聚合 OpenClaw 用量，并保留 `futureSources.codex` 作为后续 Codex 用量接入基础。
- 费用字段统一标记为 `pricingBasis: openrouter-equivalent`，通过 OpenRouter 模型价格估算，不作为真实扣费账单。
- 将 `openclaw-usage` 纳入 `scripts/update_data.py` 和 `scripts/check.py`，并更新 `AGENTS.md`、`SPEC.md`、`CONTEXT.md`、`ROADMAP.md`、`SERVER_RUNBOOK.md` 的数据边界和运行说明。

#### 背景

- Owner 希望先看到 OpenClaw 每日 token 消耗、模型来源和按 OpenRouter 标准折算的费用，同时为后续统计本地 / 服务器 Codex 用量预留统一结构。

### 修正豆奶桌面指标宽度

- 恢复豆奶详情页桌面端顶部三块 tab 的原始横排比例，避免大屏下账号余量和签到累计被压成窄小卡片。
- 保持账号余量和签到累计内部 3 个指标在桌面端三列铺满；仅在中小屏外层空间不足时自动换行。
- 将 Dash 样式版本提升到 `styles.css?v=42`。

#### 背景

- 上一版自适应修复解决了小宽度溢出，但让大屏指标卡变窄，需要按断点区分桌面和中小屏布局。

### 修复豆奶顶部自适应

- 将豆奶详情页顶部三块 tab 改为按可用宽度自动换行，避免中等宽度下挤出页面。
- 将账号余量和签到累计内部指标改为自适应列数，窄卡片下自动换成两列或一列。
- 将 Dash 样式版本提升到 `styles.css?v=41`。

#### 背景

- Owner 发现豆奶详情页顶部指标在浏览器较窄时没有自适应，右侧累计卡片会溢出。

### 移除 Dash 顶栏域名提示

- 移除 Dash 顶栏左侧的 `dash.maxnow.cn` eyebrow 文案，避免每个 tab 都重复展示当前域名。
- 保留当前 tab 标题和右侧 Blog / OpenClaw 状态入口。

#### 背景

- Owner 认为浏览器地址栏已经能看到域名，页面顶栏不需要再重复展示。

### 放大 Home 小日历

- 放大 Home 顶部右侧小日历的整体卡片尺寸。
- 提升时间、农历和节日文字层级，并让移动端也保持居中。
- 将 Dash 样式版本提升到 `styles.css?v=40`。

#### 背景

- Owner 希望 Home 右上角小日历的元素和整体框都更大一些。

### 恢复豆奶指标小卡片

- 将豆奶详情页顶部账号余量和签到累计 6 个指标恢复为独立白底小卡片。
- 首页右侧豆奶摘要 6 个指标同步改为白底小卡片，内容居中显示。
- 更新 `STYLE_CONTEXT.md`，明确豆奶指标采用图一参考风格的小卡片，而不是无内框指标。
- 将 Dash 样式版本提升到 `styles.css?v=39`。

#### 背景

- Owner 希望豆奶指标按照参考图一处理：用框框起来，并让卡片内部内容居中。

### 调整侧边导航顺序

- 将 Dash 左侧导航顺序调整为 Home、豆奶、Token。
- 同步更新 `SPEC.md` 中的一级入口顺序。

#### 背景

- Owner 希望豆奶入口放到 Token 之前，作为侧边导航第二位。

### Home 时间卡增加农历和节日

- 将 Home 顶部右侧时间卡扩展为小日历，展示公历日期、当前时间、农历日期和当天节日。
- 前端运行时计算固定公历节日、父亲节 / 母亲节，以及春节、端午、中秋等常见农历节日。
- 将 Dash 资源版本提升到 `styles.css?v=38` 和 `app.js?v=31`。

#### 背景

- Owner 希望在时间卡里看到父亲节、端午节、春节等节日，并补充阴历信息。

### 调整豆奶指标为无内框结构

- 将豆奶详情页顶部参数从独立小框改为无内框指标：左侧 icon + 右侧标题，数值在下一行。
- Home 豆奶摘要同步改为同样的无内框指标结构。
- 统一让指标 icon 和数值使用同一个语义色，并将 Dash 样式版本提升到 `styles.css?v=37`。
- 更新 `STYLE_CONTEXT.md`，明确豆奶指标不要再做“小框套小框”。

原因：

- Owner 希望豆奶指标参考用户中心卡片样式，不要单独用边框框住每个指标。

### 新增前端样式上下文

- 新增 `STYLE_CONTEXT.md`，专门记录 Dash / Blog 的前端视觉约定。
- 文档覆盖品牌图标、卡片圆角、hover 悬浮、语义配色、豆奶顶部参数配色、Home 豆奶摘要布局和样式检查项。
- 在 `AGENTS.md`、`SPEC.md` 和 `CONTEXT.md` 中补充 `STYLE_CONTEXT.md` 的职责入口。

原因：

- Owner 希望把颜色多样化、tab hover 悬浮、豆奶语义配色等前端样式口径沉淀为可复用上下文，避免后续改动回退。

### 调整豆奶紧凑单位和 Home 摘要布局

- 将豆奶相关的天 / 小时显示统一为紧凑英文单位，例如 `55d`、`3d 16h`、`1.50h`、`4.2 GB/d`。
- 将 Home 右侧豆奶摘要改为两行三列：第一排展示今日流量、今日豆丁、今日延长，第二排展示累计签到、累计流量、累计延长。
- 将 Dash 缓存版本提升到 `styles.css?v=36`、`app.js?v=30`。

原因：

- Owner 希望豆奶紧凑卡片使用 `d` / `h`，并让 Home 豆奶摘要布局更规整。

### 豆奶参数加图标并统一圆角

- 为豆奶详情页顶部 6 个参数补充小 SVG 图标，沿用对应语义色。
- 将 Dash / Blog / Blog Preview 的卡片圆角基准从 8px 调整为 14px，导航小图标容器圆角调整为 12px。
- 将 Dash 样式版本提升到 `styles.css?v=35`，Blog 样式版本提升到 `styles.css?v=17`，Blog Preview 样式版本提升到 `preview.css?v=3`。

原因：

- Owner 希望豆奶参数像参考图一样在文字前带小 icon，并希望 Dash / Blog 的页卡和内部元素圆角更接近参考视觉。

### 丰富豆奶顶部指标配色

- 将豆奶详情页顶部账号余量和签到累计的小指标改为蓝、橙、青、紫、蓝、绿的语义分色。
- 为豆奶顶部指标补充 `orange` 和 `green` tone，并将 Dash 样式版本提升到 `styles.css?v=34`。

原因：

- Owner 反馈豆奶顶部指标颜色太单一，希望像 Home 状态卡一样更有区分度。

### 修复豆奶摘要数值溢出

- 将 Home 右侧豆奶摘要的 5 个小指标从固定五列改为自适应列宽。
- 允许较长的中文单位数值在小卡片内换行，并使用响应式字号避免撑出容器。
- 将 Dash 样式版本提升到 `styles.css?v=33`。

原因：

- Owner 反馈「累计延长」显示为 `3 天 16 小时` 后在窄侧栏摘要卡中挤出小格。

### 缩小品牌图标并刷新缓存

- 将 Dash 和 Blog 左侧品牌图标从 34px 继续缩小到 28px，使视觉重量更接近 `MaxNow` 字体。
- 将 Dash 样式版本提升到 `styles.css?v=32`，Blog 样式版本提升到 `styles.css?v=16`，Blog 预览页提升到 `preview.css?v=2`。

原因：

- Owner 反馈图标仍然偏大，且 Blog 可能因为旧样式缓存继续显示蓝色底框，需要强制刷新样式。

### 调整 MaxNow 品牌区尺寸

- 将 Dash 和 Blog 左侧品牌图标从 42px 缩小到 34px，让图标视觉重量与 `MaxNow` 字体更匹配。
- 移除 Blog 左侧品牌区的 `blog.maxnow.cn` 副标题，使 Blog 与 Dash 的品牌区保持同一结构。
- 保持正式深蓝 `M/N` 图标无额外底框显示。

原因：

- Owner 反馈新图标在侧边栏里偏大，Blog 品牌区还残留底色感和网址副标题，需要跟 Dash 对齐。

### 替换 MaxNow 正式品牌图标

- 使用 Owner 确认的深蓝 `M/N` 标识生成透明背景 PNG 资产，并分别放入 Dash 与 Blog 的 `assets/maxnow-icon.png`。
- 将 Dash 和 Blog 左侧品牌区改为使用正式图标，去掉旧 `brand-mark` 自带的浅蓝底框样式。
- 在 `CONTEXT.md` 记录该图标是 MaxNow 后续正式 icon，不再回退到旧版浅蓝 `M` SVG。

原因：

- Owner 明确指定该图作为 MaxNow 之后的 icon，并要求替换 Dash 和 Blog。

### 更新 MaxNow 品牌图标

- 重新绘制 Dash 和 Blog 共用的 `maxnow-mark.svg`，替换左侧品牌区的小 `M` 图标。
- 新图标保留浅蓝圆角基调，加入更清晰的 MaxNow 山形字标和即时状态点，适配 40px 侧边栏尺寸。

原因：

- Owner 希望左上角品牌位置使用一个新的图标。

### 统一豆奶每日单位文案

- 将豆奶趋势图右上角单位从 `MB / 日`、`小时 / 日` 改为 `MB / 天`、`小时 / 天`。
- 提升前端脚本缓存版本，确保累计延长和趋势图单位都刷新为中文“天”口径。

原因：

- Owner 希望豆奶页所有每日/累计时长单位统一使用“天”，不要混用 `d` 或“日”。

### 调整豆奶累计延长单位

- 将豆奶累计延长的显示从 `d / h` 英文短单位改为 `天 / 小时` 中文单位。
- 提升前端脚本缓存版本，避免浏览器继续显示旧格式。

原因：

- Owner 反馈顶部累计延长应显示中文“天”，不要使用 `d`。

### 修复豆奶图表绘图区宽度

- 将豆奶趋势图的 SVG 坐标系宽度改为按实际图表容器宽度生成，而不是只按数据点数量估算。
- 切换到豆奶页和窗口尺寸变化时会重绘图表，让坐标轴、网格线和折线在宽屏下铺满图表区域。

原因：

- Owner 反馈图表卡片虽然铺满，但内部绘图区仍在宽屏下留下明显右侧空白。

### 调整豆奶趋势图顺序

- 将豆奶详情页「近 30 天日均可用流量」趋势图移动到「近 30 天获取流量」之前，作为趋势区第一张图。
- 将该图标题从「近 30 天账号日均可用流量」简化为「近 30 天日均可用流量」，并提升前端脚本缓存版本。

原因：

- Owner 希望账号日均可用趋势排在获取流量前面，并让标题更简洁。

### 增加豆奶日均可用趋势

- 将豆奶顶部三个大 tab 的 hover 反馈改为卡片自身上浮，避免只让内部小指标响应鼠标。
- 新增「近 30 天账号日均可用流量」趋势图，从 `dash/data/dounai_checkin.json` 的 `account_history` 读取每日 `daily_available_mb`。
- 扩展服务器 `/root/.openclaw/gen_checkin_data.py`，每天生成 `account` 时同步按日期覆盖 / 追加 `account_history`，用于长期维护账号日均可用趋势。
- 更新 `SPEC.md`、`CONTEXT.md`、`SERVER_RUNBOOK.md`、OpenClaw skill 和 `scripts/check.py`，记录新的数据契约与校验。
- 将 Dash 样式版本提升到 `styles.css?v=31`、脚本版本提升到 `app.js?v=25`。

原因：

- Owner 希望三个顶部 tab 分别具有和其他卡片一致的 hover 上浮效果，并希望每天更新账号日均可用流量趋势。

### 修复豆奶页头整体悬浮

- 覆盖豆奶详情页顶部外层 `.dounai-page-head` 的 hover 效果，避免鼠标移入时三个顶部区域作为整体上浮。
- 保留内部小指标和普通卡片的 hover 反馈。
- 将 Dash 样式版本提升到 `styles.css?v=30`，避免线上缓存继续显示旧 hover 行为。

原因：

- Owner 反馈鼠标移到豆奶顶部区域时整个 tab 都会悬空，交互反馈过重。

### 修复豆奶趋势图宽度

- 将豆奶趋势图 SVG 从固定内容宽度调整为桌面端铺满图表容器，同时保留 920px 最小宽度以支持窄屏横向滚动。
- 将 Dash 样式版本提升到 `styles.css?v=29`，避免线上缓存继续显示右侧留白。

原因：

- Owner 反馈豆奶趋势图在宽屏下没有铺满卡片，右侧出现明显空白。

### 调整豆奶趋势图标题口径

- 将豆奶详情页趋势图标题从「近 30 天流量 / 近 30 天时长」调整为「近 30 天获取流量 / 近 30 天获取时长」。
- 同步更新图表 aria title，并将 Dash 脚本版本提升到 `app.js?v=24`。

原因：

- Owner 希望标题强调这是签到获取的流量和时长，而不是账号当前使用或剩余口径。

### 给豆奶顶部卡片补分区标题

- 在豆奶详情页顶部的账号余量卡中增加 `Account / 账号余量` 标题。
- 在签到累计卡中增加 `Total / 签到累计` 标题。
- 将 Dash 样式版本提升到 `styles.css?v=28`，避免线上缓存继续显示无标题版本。

原因：

- Owner 反馈右侧两个顶部卡也需要类似图表卡片的 eyebrow / 小标题，便于识别分区。

### 拆分豆奶页顶部为三段

- 将豆奶详情页顶部从一组 6 个连续小 tab 调整为三个同级区域：标题信息、账号余量、签到累计。
- 账号余量区域继续展示剩余流量、VIP 到期和日均可用；签到累计区域继续展示累计签到、累计流量和累计延长。
- 外层页头不再作为大卡片，三个区域各自使用统一卡片样式，减少信息关系混在一起的问题。
- 将 Dash 样式版本提升到 `styles.css?v=27`、脚本版本提升到 `app.js?v=23`，避免线上缓存继续显示旧布局。

原因：

- Owner 希望顶部拆成三个小 tab：一个放豆奶签到标题，一个放余量，一个放累计，而不是把所有信息放在同一个大区域。

### 统一豆奶页顶部摘要样式

- 将豆奶详情页顶部的账号余量大卡改为 3 个独立小 tab，并和累计签到、累计流量、累计延长组成同一组 6 个顶部小 tab。
- 移除账号余量外层大框和单独标题行，避免出现“卡片套卡片”的视觉层级。
- 将 Dash 样式版本提升到 `styles.css?v=26`、脚本版本提升到 `app.js?v=22`，避免线上缓存继续显示旧布局。

原因：

- Owner 反馈账号余量模块和右侧统计卡不统一，希望顶部拆成小 tab 而不是集中放进一个大 tab。

### 豆奶页增加账号余量模块

- 在豆奶详情页顶部空白区域新增账号余量模块，展示剩余可用流量、VIP 到期日和按剩余天数折算的每日可用流量。
- 扩展 `dash/data/dounai_checkin.json`，允许 `account` 字段保存 `remaining_flow_mb`、`account_expires_at`、`vip_expires_at`、`effective_expires_at`、`days_remaining` 和 `daily_available_mb`。
- 更新服务器 `/root/.openclaw/gen_checkin_data.py`，使用现有豆奶登录态只读抓取豆奶用户面板中的账号余量字段，并写入 `/root/MaxNow/dash/data/dounai_checkin.json` 与 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。
- 当前服务器实测可读取：剩余流量 `1.29TB`、账号有效期 `2027-05-01 20:04:52`、VIP 有效期 `2027-04-30 10:15:41`、日均可用 `4321.61MB`。
- 更新 `SPEC.md`、`CONTEXT.md`、`SERVER_RUNBOOK.md`、OpenClaw skill 和 `scripts/check.py`，记录新的数据契约与校验。

原因：

- Owner 希望在豆奶页顶部空白处看到当前还剩多少流量、什么时候到期，以及平均每天可用多少流量。

### 移除当前主线标题状态摘要

- 移除 Home「当前主线」标题右侧的自动化状态摘要胶囊，避免 nginx、证书、部署版本、CPU、磁盘、内存和失败检查等系统信息挤在主线模块标题区。
- 保留系统状态数据和右侧系统模块展示，仅收敛主线卡片标题区的信息噪音。
- 将 Dash 样式版本提升到 `styles.css?v=24`、脚本版本提升到 `app.js?v=20`，避免线上缓存继续显示旧状态。

原因：

- Owner 反馈首页当前主线区域出现一串系统状态文案，影响主线信息扫描，希望去掉。

### 部署当前主线标题修复

- 已将当前主线标题状态摘要修复推送到 `origin/main`，并在服务器 `/var/www/maxnow-dashboard` 快进部署。
- 服务器部署提交：`8809daa Remove mainline automation summary pill`。
- 服务器已运行 `python3 scripts/check.py`、`sudo nginx -t` 和 `sudo systemctl reload nginx`，检查通过。

## 2026-06-19

### 修复豆奶签到线上数据路径

- 排查确认 2026-06-19 豆奶签到已在 root/OpenClaw 侧成功执行，结果为 846 MB、1 豆丁、有效期延长 2.46 小时，但线上 `dash.maxnow.cn` 仍读取停在 2026-06-18 的 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。
- 已在服务器将 `/root/.openclaw/gen_checkin_data.py` 调整为双写：同时更新 `/root/MaxNow/dash/data/dounai_checkin.json` 和 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。
- 立即重跑生成脚本并通过 `/var/www/maxnow-dashboard/scripts/check.py` 校验，线上部署目录已经包含 2026-06-19 的豆奶签到记录。
- 更新 `SERVER_RUNBOOK.md` 和 `CONTEXT.md`，记录豆奶签到由 root/OpenClaw 维护、线上页面读取 `/var/www/maxnow-dashboard` 数据出口。

### 修复线上静态资源缓存

- 将 Dash `app.js` 从 `v=18` 提升到 `v=19`、`styles.css` 从 `v=22` 提升到 `v=23`，避免浏览器继续使用旧脚本导致豆奶详情页无法切换、时长字段不更新。
- 将 Blog 页面统一引用 `styles.css?v=15`，确保专题 / 总览页能加载最新白底卡片、hover 和左侧导航颜色样式。
- 将 Dash 小统计卡的 hover 阴影和数值色改为按卡片语义色变化，避免 Token / 豆奶页的小卡全部显示成同一种蓝色。

### 部署豆奶和 Blog 视觉更新

- 已将豆奶详情页、首页豆奶摘要、Blog 卡片 hover、品牌图标和白底卡片视觉更新部署到 `dash.maxnow.cn` / `blog.maxnow.cn`。
- 线上部署提交：`8d099f1`；服务器执行 `git pull --ff-only origin main`、`python3 scripts/check.py`、`sudo nginx -t` 和 `sudo systemctl reload nginx` 后，`dash.maxnow.cn`、`blog.maxnow.cn`、`blog.maxnow.cn/topics.html` 均返回 200。

### 品牌图标改为轻量线性风格

- 将 Dash 和 Blog 左上角 MaxNow 标识从重渐变方块改为浅蓝底线性图标，和侧栏业务图标保持更一致的简约风格。
- 补齐 Dash 小统计卡片的 hover 反馈，让首页状态条、Token 摘要条和右侧小格也具备统一的边框、阴影和轻微上浮效果。
- 统一 Dash / Blog 卡片底色为白色；补强 Blog 专题、总览卡片 hover 效果，并让 Blog 左侧导航的选中态、色条和 icon 底色更接近 Dash 的交互反馈。

### Blog 卡片增加悬浮反馈

- 给 Blog 正式页和方案预览页的主要卡片增加统一 hover 效果：蓝色边框、阴影增强和轻微上浮。

## 2026-06-18

### Home 增加豆奶签到模块

- Home 右侧新增只读“签到”卡片，从 `dash/data/dounai_checkin.json` 读取豆奶每日签到数据。
- 卡片展示今日/累计流量、今日/累计有效期延长时长和累计签到天数，并作为豆奶详情 tab 的入口；首页不再放无坐标趋势图。
- 新增豆奶详情 tab，展示近 30 天流量和时长折线图，包含 x / y 轴和每日数值；豆丁只保留在原始数据中，不进入页面展示口径。
- 更新 `SPEC.md`、`CONTEXT.md` 和 `scripts/check.py`，记录豆奶签到数据归属，并校验签到 JSON 合法性。

### 移除 Blog 首页说明卡

- 移除 `blog/index.html` 首屏的大块说明卡，让首页直接进入文章流和随机换一批入口。
- 将首页样式版本提升到 `styles.css?v=14`，并为文章流补独立顶部间距，避免内容贴住 topbar。

### 给 Blog 首页增加随机换一批

- 新增 `blog/random-articles.js`，从四个专题分类二级页读取现有文章卡片，点击首页“换一批”后随机抽取 10 篇文章展示。
- 首页文章流增加 `data-article-feed` 标记和顶部“换一批”按钮；样式版本提升到 `styles.css?v=13`，避免线上缓存。
- 更新 `README.md`、`CONTEXT.md` 和 `scripts/check.py`，把随机文章脚本纳入项目结构和校验清单。

### 补齐 Blog 专题细分标签索引

- 新增 `blog/topic-tags.js`，在专题分类二级页内读取现有文章卡片的标签，生成细分标签索引，并按主标签重排文章列表。
- 更新 `blog/styles.css` 和专题页引用，让算法、计算机基础、算法短板、工程笔记四个分类页都支持“分类 -> 细分标签 -> 文章”的浏览层级。
- 更新 `README.md`、`CONTEXT.md`、`ROADMAP.md` 和 `scripts/check.py`，把该前端增强脚本纳入项目结构和校验清单。

### 固定 Home 系统状态展示项

- Home 右侧系统状态只保留 Owner 指定的 `nginx`、证书、部署版本、CPU、磁盘、内存和运行时间。
- HTTPS、最近拉取、定时同步、wiki 待办、失败日志、云位置和计费等细节不再写入首页 `system` 列表，避免系统状态区过载。

### 收尾系统状态和数据更新入口

- 扩展 `scripts/sync_system_status.py`，让 Home 系统状态展示 nginx、HTTPS、证书、部署 commit、最近 pull、cron、wiki-todos 同步、失败日志、CPU、磁盘、内存、uptime、云位置和计费状态。
- 新增 `scripts/update_data.py`，统一提供 `runtime`、`project-status`、`wrap all` 等数据更新入口；`runtime` 不覆盖 Owner 判断字段。
- 服务器 crontab 的 `MAXNOW-DASHBOARD-SYNC` 改为调用 `python3 scripts/update_data.py runtime`，保留分日志和总日志。
- 更新 Home 系统状态项的异常/未知视觉状态，让失败日志或同步异常能直接在页面中显色。
- 用 `python scripts/update_data.py project-status` 将当前主线 / 今日推进显式刷新为 `ROADMAP.md` 中的当前任务。
- 更新 `AGENTS.md`、`SPEC.md`、`README.md`、`DEPLOY.md`、`SERVER_RUNBOOK.md`、`CONTEXT.md` 和 `ROADMAP.md`，记录新的工具入口、cron 命令和完成状态。

### 接入 wiki-todos 服务器自动同步

- 在服务器 `/var/www/maxnow-dashboard` 上为 `ubuntu` 用户配置 crontab 标记块 `MAXNOW-DASHBOARD-SYNC`。
- 当前频率为每 10 分钟一次，执行 `scripts/sync_wiki_todos.py`、`scripts/sync_system_status.py` 和 `scripts/check.py`。
- 运行日志写入 `logs/maxnow-sync.log`，并分别追加 `logs/wiki-todos.log` 与 `logs/system-status.log`。
- 已验证自动同步链路：cron 在 `2026-06-18T19:00:01+08:00` 自动运行成功，personal-wiki 待办缓存开放待办从 8 条变为 7 条。
- 更新 `DEPLOY.md`、`SERVER_RUNBOOK.md`、`CONTEXT.md` 和 `ROADMAP.md`，把自动同步从待办移动到已完成记录。

## 2026-06-17

### 优化博客文章图片边框和尺寸

- 移除文章详情页图片容器的浅色背景和边框，避免缩图后露出一圈明显色块。
- 将文章图片最大宽度从 780px 调整到 900px，最大高度同步放宽，并继续保持居中显示。
- 将文章详情页样式版本提升到 `styles.css?v=14`。

原因：

- Owner 反馈文章图片缩小后外侧出现一圈深色/灰色区域，且图片略小。

### 调整博客文章流和专题层级

- 将 `blog/index.html` 从卡片拼版改为文章预览流：首页按文章逐条展示，适合持续向下浏览。
- 将博客左侧导航整理为 `文章 / 专题 / 总览` 三个同级 tab；归档统计后续放在独立总览页，不放在文章页 sidebar 卡片。
- 将 `blog/topics.html` 调整为专题分类索引页；新增 `blog/topic-algorithm.html`、`blog/topic-cs.html`、`blog/topic-algorithm-gap.html` 和 `blog/topic-engineering.html` 作为分类二级页。
- 分类二级页展示该分类下的文章列表，并提供返回专题索引的入口。
- 更新 `scripts/check.py`、`README.md`、`CONTEXT.md` 和 `ROADMAP.md`，覆盖新增页面和新的浏览结构。

原因：

- Owner 希望博客首页更像文章归档流；专题先展示分类，点击分类后进入二级页查看具体文章，并能返回上一级。

### 优化博客文章 cell 点击和两列布局

- 删除文章卡片里的单独“阅读全文”按钮，改为整张文章 cell 可点击进入文章详情。
- 首页和专题分类二级页的文章列表在桌面端改为一行两篇，减少大屏空白。
- 新增 `blog/post-preview.html` 作为临时文章详情页预览，后续真实发布时由每篇文章自己的 slug 页面替代。
- 将博客样式版本提升到 `styles.css?v=4`，避免旧样式缓存影响预览。
- 专题分类二级页改为从旧博客 front matter 生成真实列表：算法 145 篇、CS 大学生必备 55 篇、算法短板 6 篇、工程 / 总结 / 未分类 5 篇，不再只放少量示例。

原因：

- Owner 希望点击文章 cell 任意位置都能进入文章，不再依赖小按钮；同时希望大屏下一行两篇文章，提升信息密度。
- Owner 发现算法分类写着 145 篇但页面只显示几篇，容易误解为数据缺失。

### 调整博客总览为左侧独立 tab

- 新增 `blog/overview.html` 作为博客左侧 `总览` tab，展示原始文章数、缓存图片数、专题分类数和发布状态。
- 从 `blog/index.html` 和 `blog/topics.html` 移除归档/分类统计 sidebar 卡片，左侧只保留 `文章 / 专题 / 总览` 导航。
- 将博客样式版本提升到 `styles.css?v=5`，覆盖新的总览页和导航结构。

原因：

- Owner 明确希望总览是左侧独立 tab，而不是放在左侧栏里的信息卡片。

### 补齐博客文章详情页正文预览

- 将 `blog/post-preview.html` 从占位说明改为真实文章正文预览，使用旧博客文章 `20200403-以太网、IP、TCP、UDP头部格式.md` 的内容。
- 补充文章页正文样式，覆盖小节、段落、列表、来源提示和图片展示。
- 将文章详情页样式版本提升到 `styles.css?v=6`，避免旧缓存继续显示空壳详情页。

原因：

- Owner 发现点击文章 cell 后详情页没有正文内容，阅读体验像空页面。

### 修复博客左侧 tab 点击抖动

- 为博客页面预留稳定滚动条槽，避免在不同页面高度之间切换时整体横向跳动。
- 固定 sidebar 和左侧 tab 的宽度，并隔离 tab 内部布局绘制，减少 active 状态切换造成的视觉抖动。
- 将正式博客页统一提升到 `styles.css?v=7`，避免不同页面引用旧样式版本造成切换不一致。

原因：

- Owner 反馈每次点击博客左侧 tab 时，tab 区域会跳动一下。

### 统一博客公开品牌为 MaxNow

- 将博客页左上角品牌、浏览器标题和可访问名称从 `V-ioi-V Blog` 调整为 `MaxNow Blog`。
- 新增 `blog/assets/maxnow-mark.svg` 作为博客左侧品牌图标，替换原来的单字母方块。
- 更新博客品牌图标样式，并将正式博客页样式版本提升到 `styles.css?v=8`。

原因：

- Owner 希望公开博客这里使用 MaxNow 品牌，不再展示 V-ioi-V。

### 修复博客刷新时整页跳动

- 移除博客页面的 Google Fonts 外部加载链路，改用系统字体栈，避免字体加载完成后整页文字重新排版。
- 给品牌图标、顶栏和首屏信息块补充稳定尺寸约束，减少刷新期间的布局重排。
- 将正式博客页样式版本提升到 `styles.css?v=9`。

原因：

- Owner 反馈每次刷新博客页面时，页面上的所有元素都会跳一下。

### 调整博客文章详情页宽度和来源状态

- 将 `blog/post-preview.html` 详情阅读面板从 920px 放宽到 1180px，减少大屏下文章只占左侧一小块的问题。
- 文章流入口链接增加 `from=articles`，专题分类页入口链接增加 `from=topics`。
- 详情页根据入口来源高亮左侧 `文章` 或 `专题` tab，并同步调整返回按钮文案和目标。
- 将正式博客页样式版本提升到 `styles.css?v=10`。

原因：

- Owner 反馈文章点进去显示太窄，并且从专题进入文章后左侧高亮错误地跳到了文章 tab。

### 统一 Dash 和 Blog 为轻量用户中心风格

- 参考 Owner 给出的用户中心截图，统一 Dash 与 Blog 的视觉语言：浅蓝灰背景、白色侧栏、柔和卡片、淡边框和轻阴影。
- 将 Dash 侧栏拓宽到 238px，并替换为 MaxNow SVG 品牌图标；移除 Dash 的 Google Fonts 外部字体依赖。
- 优化 Dash 的侧栏导航、顶部栏、状态卡片、内嵌列表项、按钮和 Token 卡片质感。
- 同步 Blog 的侧栏、顶部栏、首页文章流、专题卡片、总览卡片和文章详情页间距与卡片风格。
- 将 Dash 样式版本提升到 `styles.css?v=21`，Blog 正式页样式版本提升到 `styles.css?v=11`。

原因：

- Owner 希望 Dash 和 Blog 都按照参考截图的清爽用户中心风格优化。

### 部署参考风格版本到服务器

- 已推送 `main` 到 GitHub，并在服务器 `/var/www/maxnow-dashboard` 快进到 `2290eca Merge reference style refresh`。
- 已运行 `python3 scripts/check.py`，JSON wrapper 一致性通过；服务器未启动 4173 本地预览服务，因此本地预览 URL 检查按预期跳过。
- 已执行 `sudo nginx -t` 并 reload nginx。
- 已验证 `https://dash.maxnow.cn`、`https://blog.maxnow.cn`、`https://blog.maxnow.cn/topics.html` 和 `https://blog.maxnow.cn/post-preview.html?from=topics` 返回 200。

原因：

- Owner 确认参考风格版本可以部署上线。

### 放宽博客文章详情页到内容区全宽

- 移除 `blog/post-preview.html` 详情卡片、标题和正文 section 的窄 `max-width` 限制，让文章详情页在宽屏下占满内容区。
- 将文章详情页样式版本提升到 `styles.css?v=12`。

原因：

- Owner 反馈线上文章详情页在宽屏下仍然只占左侧一半。

### 缩小并居中博客文章图片

- 将文章详情页图片限制为最大 780px 宽、最大 460px 高，并保持原始比例。
- 将图片容器改为居中布局，让图片在容器内水平和垂直居中。
- 将文章详情页样式版本提升到 `styles.css?v=13`。

原因：

- Owner 反馈文章详情页放宽后，正文图片过大，需要缩小并上下居中。

### 调整 Dash 的 Blog 入口位置

- 将 `dash.maxnow.cn` 左侧导航里的 `Blog` 外链移到顶部右侧，和博客页里的 `Dash` 外链保持同一类弱入口处理。
- 左侧导航只保留 Dash 内部页面：`首页` 和 `Token`。
- 更新 `CONTEXT.md` 和 `ROADMAP.md`，将博客入口描述从左侧导航改为顶部右侧弱外链。

原因：

- Owner 反馈 Blog 放在 Dash 左侧导航里不合适，和博客页中 Dash 外链的边界问题相同。

### 部署博客预览到服务器

- 将博客首页和专题页预览合入 `origin/main`，服务器 `/var/www/maxnow-dashboard` 已拉取到提交 `6017791`。
- 调整 nginx：`dash.maxnow.cn` 指向 `/var/www/maxnow-dashboard/dash`，`blog.maxnow.cn` 指向 `/var/www/maxnow-dashboard/blog`。
- 为 `blog.maxnow.cn` 通过 certbot 启用 HTTPS，证书到期日为 2026-09-15，并由 certbot 自动续期。
- 部署前备份服务器旧路径运行数据到 `~/maxnow-deploy-backups/20260617-180826`，并恢复到新的 `dash/data/dashboard.*` 与 `dash/data/wiki-todos.*` 路径。
- 验证 `https://dash.maxnow.cn`、`https://blog.maxnow.cn` 和 `https://blog.maxnow.cn/topics.html` 均返回 200。

原因：

- Owner 要求先提交合码，再将当前测试改动部署到服务端。

### 新增博客首页预览

- 新增 `blog/index.html` 和 `blog/styles.css`，生成更接近正式 `blog.maxnow.cn` 的博客首页预览。
- 首页预览使用旧博客归档里的真实内容分布和候选文章：算法、CS 大学生必备、算法短板、工程 / 总结 / 未分类等。
- 保留 `blog/preview.html` 和 `blog/preview.css` 作为方案说明页，用于展示发布链路和边界。
- 更新根目录本地入口 `index.html`，同时提供 Blog 首页预览和 Blog Plan 入口。
- 更新 `scripts/check.py`，校验 `blog/index.html`、`blog/styles.css` 和本地 `/blog/` 访问。
- 新增 `blog/topics.html` 专题页预览，让左侧“文章 / 专题”导航成为真实分页面切换，而不是在首页内滚动或筛选。
- 调整博客导航边界：左侧只保留博客栏目，`Dash` 不再作为左侧栏目卡片，改为顶部弱外链。

原因：

- Owner 希望再看一个更像真实博客首页的预览，而不是只有方案说明界面。
- Owner 反馈左侧“专题”点起来和文章页区别不明显，因此改成独立专题页。
- Owner 反馈 `Dash` 放在博客左侧栏目导航里不合适，因此降低为顶部外部入口。

### 拆分 Dash 和 Blog 目录

- 将 dashboard 页面代码和运行数据移动到 `dash/`：`dash/index.html`、`dash/styles.css`、`dash/app.js`、`dash/data/*`。
- 将博客方案预览移动到 `blog/preview.html` 和 `blog/preview.css`，作为 `blog.maxnow.cn` 发布层工作区的起点。
- 根目录新增本地开发入口 `index.html`，只负责跳转到 Dash 和 Blog Preview，不再作为线上 dashboard 本体。
- 更新 `scripts/check.py`、`scripts/sync_wiki_todos.py` 和 `scripts/sync_system_status.py`，统一使用 `dash/data/*`。
- 更新 `AGENTS.md`、`SPEC.md`、`CONTEXT.md`、`ROADMAP.md`、`DEPLOY.md`、`SERVER_RUNBOOK.md`、OpenClaw skill 和 README，记录新的文件边界和部署根目录。
- 明确当前 MD 文件不需要拆目录：根目录文档继续分别承担规则、规格、路线、上下文、想法、更新记录、部署和服务器操作说明。

原因：

- Owner 希望先在一个 repo 内拆分 dash 和 blog 内容，同时判断当前上下文、待办、更新日志和 agent 文档是否冗余。

### 确定个人博客技术方案

- 将个人博客推荐域名确定为 `blog.maxnow.cn`，不挂在 `dash.maxnow.cn/blog`，也暂时不新买独立域名。
- 明确 `dash.maxnow.cn` 继续作为私人状态工作站；博客完整阅读体验属于独立公开站，dashboard 最多展示发布状态和跳转入口。
- 在 `dash.maxnow.cn` 左侧导航增加 `Blog` 外链，指向 `https://blog.maxnow.cn`，不新增 dashboard 内部博客页面。
- 确认内容源使用 private personal-wiki 的 `raw/blog-vioiv`，当前包含旧 Hexo Markdown 211 篇和缓存图片 167 个。
- 更新 `SPEC.md`、`ROADMAP.md`、`IDEAS.md`、`CONTEXT.md` 和 `DEPLOY.md`，记录内容归属、发布边界、部署目录和后续待办。
- 新增 `blog/preview.html` 和 `blog/preview.css`，作为接近当前 MaxNow 风格的博客首页视觉预览，不作为正式线上入口。

原因：

- Owner 希望基于 personal-wiki 旧博客内容启动个人博客，并先确认域名结构、技术方案、文档待办和页面风格。

### 优化系统状态数值文案

- 调整 CPU 负载展示：把 Linux load average 按核心数换算为百分比，显示为 `1/5/15 分钟负载 x% / y% / z%`。
- 调整运行时间展示：不再使用 `uptime -p` 的英文 weeks/days/hours 输出，改为从 `/proc/uptime` 生成中文短格式，例如 `48 天 17 小时`。
- 运行时间说明从 `system uptime` 改为 `持续运行`，避免卡片左侧出现英文命令行描述。

原因：

- Owner 觉得运行时间英文天数太丑，CPU 负载原始小数也不直观，希望用百分比表达。

### 收敛系统状态卡片

- 调整 `scripts/sync_system_status.py`，`dash/data/dashboard.*` 的 `system` 字段只写入 nginx、CPU、磁盘、内存和运行时间。
- 系统状态摘要也只根据这 5 项判断，不再受服务器详情、HTTPS、部署版本、wiki 同步、证书、定时任务等隐藏检查影响。
- 优化 CPU 说明，把 load average 写成 `1/5/15 min load` 供前端翻译为 `1/5/15 分钟负载`。
- 优化磁盘说明：根目录 `/` 不再显示“挂载点 /”，只有非根挂载点才显示挂载位置。
- 更新 `SPEC.md`，明确 Home 系统状态只保留轻量机器健康项。

原因：

- Owner 希望系统状态卡片减少噪音，只保留 nginx、CPU、磁盘、内存和运行时间，并希望 CPU 负载和磁盘可用量更容易理解。

### 调整卡片标签位置

- 调整普通信息卡片和 AI 外部输入卡片的标题区结构，将来源 / 状态标签统一放到标题行右侧，不再作为正文第一行显示。
- 保留 AI 外部输入的发布日期，并让日期跟随来源标签在右侧对齐。
- 更新样式版本号，避免线上浏览器继续使用旧 CSS。

原因：

- Owner 发现 AI 外部输入和稍后留意等卡片里的标签位置像“图标漂在内容上方”，影响扫描和观感。

### 修正 personal-wiki 待办展示数量

- 调整 Home 左侧 `Personal Wiki / 近期待办` 模块，显示当前全部未完成待办，不再只截取前 6 条。
- 更新 `SPEC.md`，将 personal-wiki 待办入口的规则改为只读展示当前未完成集合；如果后续数量明显过多，再增加折叠或分页。

原因：

- Owner 发现左侧模块只显示 6 条，但系统状态里的 wiki 待办显示 `8 open`，两处口径不一致容易误解。

### 补充服务器云位置和计费信息

- 更新 `scripts/sync_system_status.py`，从腾讯云 metadata 读取实例 ID、公网 IP、region、zone、计费类型、创建时间和 termination time。
- 系统状态模块新增“云位置”和“计费/有效期”信息；当前服务器是 `ap-singapore-2`，按量计费，无固定到期时间。
- 继续补充证书到期、最近 git pull 时间、定时任务状态、失败日志摘要和系统 uptime，方便 Owner 在线上先看一版再决定保留哪些卡片。
- 优化系统状态百分比项展示：CPU、磁盘、内存使用率用环形进度呈现，并将容量说明改为更易读的中文。
- 删除侧边栏品牌下的“私人看板”副标题，弱化顶部域名标签。
- 更新 `SERVER_RUNBOOK.md`，记录相关 metadata 查询命令和当前服务器可读到的信息。

原因：

- Owner 希望在系统状态里看到服务器位置、有效期，并理解系统状态前几项的含义。

### 优化动态数据待办顺序

- 更新 `ROADMAP.md`，把近期实现顺序调整为：服务器自动同步 wiki-todos、系统状态动态化、统一数据 wrapper 工具。
- 将 Token 真实数据、AI 外部输入、Last-30 增量更新等任务放入后续队列，避免在数据来源未明确前先做复杂页面能力。
- 标记服务器 GitHub CLI 已具备读取 private personal-wiki 的条件，服务器定时任务剩余重点转为 cron / systemd timer、日志和失败提醒。
- 新增 `scripts/sync_system_status.py`，用于采集 nginx、HTTPS、git commit、磁盘、内存和 wiki-todos 同步状态，并只更新 dashboard 的 `automation` / `system` 字段。
- 更新 `SPEC.md`、`CONTEXT.md`、`SERVER_RUNBOOK.md` 和 `ROADMAP.md`，记录系统状态脚本的边界、手动运行命令和后续定时化任务。
- 更新 `AGENTS.md`，要求完成功能、服务器操作、自动化或数据链路后，同步维护 `ROADMAP.md`、`UPDATE_LOG.md`、`CONTEXT.md` 和必要的 runbook，不允许只停留在聊天记录。
- 更新 `CONTEXT.md` 和 `SERVER_RUNBOOK.md`，记录服务器 GitHub CLI 已安装授权、本地预览可通过 `127.0.0.1:8000` 访问、服务器可读取 private personal-wiki 并运行 `scripts/sync_wiki_todos.py`。

原因：

- Owner 希望根据当前页面模块和现有数据链路，重新整理哪些待办现在最值得推进。
- Owner 指出完成实际功能或服务器操作后，必须同步更新仓库里的待办、已完成记录、日志和上下文。

## 2026-06-16

### 增加 personal-wiki 近期待办入口

- 在 Home 主内容区新增 `Personal Wiki / 近期待办` 紧凑模块，位于“当前主线”和“今日推进”之间。
- 新增 `scripts/sync_wiki_todos.py`，通过本地或服务器 `gh api` 读取 private personal-wiki `wiki/tasks/todo.json`。
- 新增 `dash/data/wiki-todos.json` 和 `dash/data/wiki-todos.js`，作为 MaxNow 前端可静态读取的待办缓存。
- 模块只读展示 `dash/data/wiki-todos.json` 中的未完成待办，并提供跳转入口。
- 顶部刷新按钮会重新读取本地缓存；前端不直接访问 private GitHub raw，不做自动轮询，也不支持编辑或标记完成。
- 补充 `SPEC.md`，记录入口位置、只读边界和刷新策略。
- 更新 `AGENTS.md`、`CONTEXT.md` 和 `ROADMAP.md`，纳入新的数据文件、同步脚本和维护边界。
- 在 `ROADMAP.md` 记录服务器还需要安装并授权 GitHub CLI，才能自动读取 Owner 的 private personal-wiki 仓库。

原因：

- Owner 希望 MaxNow Home 能看见 personal-wiki 的近期待办，但不要把 Home 做成完整 todo app。

### 明确“合码 / 合入主分支”的 Git 语义

- 更新 `AGENTS.md`，记录 Owner 表达“没问题了，合进去吧”“合码”“合入主分支”等意图时的固定流程。
- 这类表达表示：把已完成工作合入远端 `origin/main`，然后切回本地 `main` 并执行 `git pull`，让本地 `main` 与远端保持一致。

原因：

- 避免代理误解为只在当前分支、本地 `main` 或其他集成分支上直接操作；主分支合入目标始终是远端 `origin/main`。

### 合并 personal-wiki 中的 MaxNow 待办

- 更新 `ROADMAP.md`，把 personal-wiki 中 7 个开放待办合并进 MaxNow 仓库路线图。
- 将 personal-wiki 近期代办入口、资源监控、OpenClaw / personal-wiki 同步链路列为 MaxNow 侧可执行待办。
- 将 API key 额度、豆奶流量到期、Token 使用量合并为资源监控模块的子项，避免重复拆任务。
- 将个人博客模块拆分为：内容筛选和隐私判断留在 personal-wiki，模块开发和状态入口归 MaxNow。
- 把入口位置、待办数据格式、编辑权限、OpenClaw 写入方式、博客公开范围和旧文筛选策略放入待确认。

原因：

- Owner 希望把偏产品开发的 MaxNow 待办迁到本仓库，personal-wiki 只保留内容筛选、长期方向、数据归属和待确认策略。

### 部署前端静态站到服务器

- 在服务器安装 nginx，并将 `main` 分支部署到 `/var/www/maxnow-dashboard`。
- 配置 `dash.maxnow.cn` 的 nginx HTTP 静态站点，当前访问 `http://dash.maxnow.cn` 返回 MaxNow 页面。
- 新增 `SERVER_RUNBOOK.md`，记录 SSH 连接方式、部署命令、更新命令和常见排障。
- 更新 `AGENTS.md`、`CONTEXT.md` 和 `DEPLOY.md`，把 `SERVER_RUNBOOK.md` 纳入服务器操作上下文。

原因：

- Owner 要求先部署前端页面，并记录 Codex 是如何在服务器上执行部署的。

## 2026-06-15

### 约束 MaxNow 功能待办的维护位置

- 更新 `AGENTS.md`，明确当 Owner 询问 MaxNow 项目待办、功能规划或下一步实现内容时，不要修改 `dash/data/*.json` 或 `dash/data/*.js`。
- 更新 `ROADMAP.md`，将当前 MaxNow 功能待办整理为：服务器自动更新链路、数据更新工具、Home 真实项目状态、Token 真数据、访问控制、运行日志和 Last-30 视觉确认。
- 更新 `CONTEXT.md`，强调 MaxNow 功能待办以 `ROADMAP.md` 为准，运行数据仍归 `dash/data/*.json`。

原因：

- Owner 明确指出“MaxNow 待办”指的是要给 MaxNow 实现哪些功能，不是要改首页写死展示数据。

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
- 将 `dash/data/last-30.*` 和 `openclaw/last-30/SKILL.md` 纳入项目文件边界和数据契约。
- 更新 `CONTEXT.md`，标记 Last-30 数据文件和 skill 已建立，下一步重点转为首页展示和服务器自动更新。

原因：

- Owner 要求直接开始做，并要求后续分支名按需求语义命名。

### 补充项目上下文地图

- 新增 `CONTEXT.md`，说明 MaxNow 的上下文分层、文件职责、维护者和当前缺口。
- 明确 `CONTEXT.md` 主要给 Codex / 代理接力使用，Owner 可以检查但它不是汇报文档。
- 将 `CONTEXT.md` 纳入 `AGENTS.md` 和 `SPEC.md` 的文件边界。
- 在 `SPEC.md` 中补充 “Last-30 滚动记忆” 未来方向。
- 在 `IDEAS.md` 中记录 Last-30 滚动记忆想法。
- 修复 `dash/data/dashboard.json` 的中文内容，使它和 `dash/data/dashboard.js` 保持一致，避免页面读取 JSON 后出现乱码。
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

## 2026-06-16

### 启用 HTTPS 访问

- 使用 Let's Encrypt certbot 为 `dash.maxnow.cn` 签发 SSL 证书。
- 更新 nginx 配置，启用 HTTPS 访问。
- 设置 HTTP 到 HTTPS 的 301 跳转。
- certbot 已自动配置证书自动续期。

原因：

- `dash.maxnow.cn` 需要通过 HTTPS 提供访问，并保留 HTTP 请求的稳定跳转路径。
