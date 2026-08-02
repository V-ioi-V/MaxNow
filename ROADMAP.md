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
- `dash.maxnow.cn` 顶部右侧已预留 `Blog` 弱外链，指向 `https://blog.maxnow.cn`；左侧导航只保留 Dash 内部页面：首页、豆奶、Token、芭蕾、云服务、生活、同行记。
- 第一阶段先做只读静态博客：筛选 public/published 文章，转换 front matter，复制必要图片，生成 `blog.maxnow.cn` 页面。
- 首页预览页：`blog/index.html`，用于确认文章流首页的信息架构和视觉风格，首页按文章预览卡片持续向下浏览。
- 文章 cell 交互：整张文章卡片都可点击进入文章详情，桌面端文章流按一行两篇展示。
- 专题索引页：`blog/topics.html`，用于确认分类总览。
- 专题分类二级页：`blog/topic-*.html`，用于确认点击分类后查看该分类文章、细分标签索引、按标签分组文章和返回专题索引的浏览方式。
- 归档总览页：`blog/overview.html`，作为左侧独立 tab 展示原始文章数、缓存图片数、专题分类数和发布状态；不要把这些统计放成左栏信息卡。
- 方案说明页：`blog/preview.html`，用于保留博客发布链路和边界说明，不作为正式线上入口。

## Next

### 让芭蕾自动抢课支持动态配置

- 来源：2026-08-01 Owner 希望以后改课不再由 Codex 修改脚本，而是在 MaxNow 中动态调整抢课方式。
- 建议分支：`feature/dynamic-ballet-booking-config`
- 把稳定的抢课执行引擎与经常变化的目标课程彻底分开；以后增删课程、改优先级或候补策略只更新配置，不修改 Python、systemd unit，也不因普通改课重新部署关键路径。
- 服务器运行配置作为唯一可编辑来源；仓库只保留 schema、默认模板、迁移与校验代码，Dashboard 和后续聊天入口都读取或写入同一份版本化配置，不维护双向副本。
- 在芭蕾页增加“自动预约设置”：支持添加 / 删除目标、拖动优先级、逐课启用候补、区分每周重复与仅下周生效、一键暂停本周，并明确展示下一次执行时间与最终提交顺序。
- 保存前展示结构化变更摘要并要求 Owner 确认；保留配置版本、修改时间、审计历史和上一版回滚。保存失败或配置非法时继续使用最后一份有效配置，并在页面明确标记失败，不能让半写入配置进入周日任务。
- 增加最小配置接口，原则上只需读取和更新脱敏配置；复用现有登录保护，并补 CSRF、版本冲突和原子写入校验。接口使用独立低权限账号，只能访问配置与审计目录，不能读取闻道 Session、访问网络、启动预约服务或执行预约 mutation。
- 周日服务在 14:19:35 前读取并冻结本次配置快照；页面保存、配置接口和审计记录不得进入 14:20 抢课关键路径。提交仍按冻结后的显式优先级串行执行，每节最多一次 mutation，身份失效、页面结构变化或配置不确定继续 fail closed。
- 第二阶段可让噗噗把“下周取消周四软开、增加周六 L1”等自然语言转换为待确认草稿；只有 Owner 确认后才能调用同一配置接口，聊天入口本身不直接改脚本或执行预约。
- 验收覆盖：桌面 / 手机编辑与只读回显、单周覆盖和每周规则、优先级与候补、暂停 / 恢复、并发版本冲突、非法配置回退、审计 / 回滚、14:19:35 配置冻结，以及保存配置绝不触发闻道请求或真实预约。

### 补齐前端自动测试、无障碍与移动端验证

- 来源：2026-07-10 MaxNow 整体体检。
- 建议分支：`feature/frontend-smoke-tests`
- 在 CI 或本地统一命令中启动静态服务，检查 Dash 七个 tab、Blog 主要页面、控制台错误、失效资源和关键交互。
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

### 扩展芭蕾学习闭环与受控约课

- 来源：2026-07-25 至 2026-07-26 Owner 需求、课程 / 预约 / 上课记录只读验证和 Session 生命周期实验。
- 只读学习模块由 `feature/ballet-module` 落地；真实约课能力另用 `feature/ballet-booking`，避免页面数据与写操作一起上线。
- 产品目标不是单纯抢课，而是让 Owner 看清下一节课、本周计划、未来预约、实际上课记录、学习进度和近期重点；自动约课只作为最后一层受控能力。
- 页面入口名称为“芭蕾”、副标题“课程与进度”，位于 Token 与云服务之间；独立页使用粉玫瑰 + 白卡语义，Home 只放紧凑摘要。
- 当前入口是微信公众号内 H5 网页，不是微信小程序：`gm.wendaosoft.com/gm/weixin/home/index/54114` 通过微信 `snsapi_base` OAuth 建立网站会话，再用 `PHPSESSID` 访问会员与课程页面。
- 已验证可读取课程表、当前预约、候补 / 余位信息和独立上课记录；正式数据模型必须把“预约过”和“实际完成”分开，并把剩余名额标记为抓取时快照。
- 阶段 0A-1B｜只读数据与页面：已部署到 MaxNow；每天 09:00 / 12:00 / 15:00 / 18:00 / 22:00 rolling、周日额外 14:30 课表刷新与每月 1 日 00:47 full timer 已启用，刷新预约、候补、上课记录、课程卡和周课表。登录失效后停止请求并保留旧数据。
- 阶段 2｜学习闭环：从 personal-wiki 单向同步阶段目标、课堂重点、老师纠正、动作标签和练习计划；MaxNow 不提供编辑后端，也不把可选身体状态放进 Home。
- 阶段 2.5｜Apple 日历订阅：从脱敏的正式预约 / 候补数据生成私有、可撤销的 ICS 订阅源和 `webcal://` 链接；Owner 在 iPhone 或 Mac 上首次确认订阅后由 Apple 日历自动刷新。课程使用稳定 UID 和北京时间，改期 / 取消可更新原事件；链接不得暴露 PHPSESSID、会员标识或源记录 ID。
- 阶段 2.6｜芭蕾数据型分享图：每周小红书“芭蕾周记录”封面已经完成，见 Done。后续可把 Owner 选定的下一节课、本周训练、本月 / 年度节数与时长、主要课型和近期训练记录排成可选模板；所有分享图均只读取脱敏 read model，不上传服务器，也不包含 PHPSESSID、会员 / 卡片标识、源记录 ID、自动化内部状态或未经选择的私人信息。
- 阶段 3-4｜无人值守自动抢课：Owner 已于 2026-07-28 对当前三节固定课程、周日 14:20 和“周六 > 周日 > 周五 > 其他日期”顺序单独批准启用；fast path、私有幂等账本、逐课安全结果和 MaxNow 状态面板已完成，见 Done。以后新增目标仍需明确配置、测试和 Owner 授权。
- 当前 Session 实验仍只回答“持续活动时最多能维持多久”，不证明静默闲置寿命；生产每天 09:00 / 12:00 / 15:00 / 18:00 / 22:00、周日额外 14:30 与月度 full timer 已启用，具体 unit、日志和停止方式以 `SERVER_RUNBOOK.md` 为唯一运维真相。
- Home 不展示完整课表、历史或运维日志；Cloud 仅展示采集和自动化健康。
- `PHPSESSID` 视为约课网站密码：生产使用 host-bound systemd 加密凭据与 `LoadCredentialEncrypted`，不得进入 Git、前端、环境变量、命令参数、日志、备份或聊天；Cookie、OAuth code、微信标识、手机号、会员卡号和原始响应正文同样禁止外露。
- 默认不自动取消、转课、买卡、支付或报名付费活动；验证码、微信重新授权、页面结构变化或无法判断的响应一律 fail closed。
- 推进学习闭环或受控约课前，还需 Owner 确认当前级别、每周目标、主要课程 / 老师 / 时段偏好、候补和冲突规则、学习笔记格式及通知渠道；导航位置、粉白视觉、Home 摘要边界和统计口径已确认，不再作为阻塞问题。
- 只读验收：同一批源数据重跑后无重复；补录 / 改课可在滚动窗口内正确更新；累计节数与分钟等于明细汇总；月 / 年空档补零；失败不会清空上次成功数据；`720px` / `768px` 高度和 `860px` / `390px` 宽度下侧栏与图表无整页溢出。
- 自动抢课已作为独立受控模块落地；学习目标、课堂纠正、Apple 日历订阅和芭蕾分享图仍按各自阶段推进。自动预约成功不等于学习模块完成。

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

### 已完成芭蕾周记录封面

- 芭蕾页顶部“已同步”右侧提供紧凑 `week N` 入口，并继承状态胶囊的字号、字重和高度；点击后在弹窗中预览固定粉色手作底图，并可复制图片或下载 `1280×1710` PNG。
- `2026-07-27` 至 `2026-08-02` 固定为 `week 2`，北京时间每周一自动加一；浏览器只把版本化底图与透明手绘数字本地拼合，不每周调用 AI，不上传图片，也不依赖服务器定时任务。
- 进入芭蕾页后利用浏览器空闲时间预生成；同周且模板版本未变化时复用当前页面缓存，多个触发动作共享同一个生成任务，进入新周会丢弃旧内存结果。Owner 后续只需放入新的无数字底图并更新 `dash/assets/ballet-week-cover/template.json` 的文件名和版本，页面脚本无需改动。
- 已验证 `1280px × 720px` 与 `390px × 844px`：入口和标题同排，弹窗无横向溢出，画布内部尺寸固定 `1280×1710`，手机按钮可完整操作；剪贴板复制成功。

### 已完成芭蕾周记录手绘数字素材库

- 以 Owner 确认方向中的手绘数字 `2` 为笔触基准，建立酒红色透明 PNG `0–9` 全套数字，统一高度和基线，同时保留各数字自然宽度，支持 `9`、`10`、`100` 等多位周数自动拼接。
- 素材固定保存在 `dash/assets/ballet-week-cover/digits/`，包含 10 个运行时数字、尺寸 / 基线 manifest、维护说明和总览图；绿色色键、生成母版和中间处理文件不进入运行时资产。
- 本项提供长期可复用素材；固定底图、周一自动加一、芭蕾页 Week 入口、下载和剪贴板复制已在后续“芭蕾周记录封面”中完成。

### 已完成芭蕾成长评分与经验等级

- 芭蕾顶部把“成长等级”和“课程等级”拆成两张独立面板，成长等级固定在上、课程等级在下；宽屏共同占据概览第三格，中等宽度在下一行上下排列，窄屏随页面单列。
- 课程等级按实际上课记录计算当前级别课次、目标课次和下一课程级别距离；达到当前目标后自动升级且不因后续训练频率下降而回退。
- 成长等级把全部实际上课每节固定计为 1 节，使用 `Lv.1–Lv.10` 与单段本级进度；小天鹅按当前等级切换本地透明 PNG，并固定放在成长等级面板右上角。

### 已完成芭蕾模块信息架构收敛

- 芭蕾页按学习决策顺序重排为“下一节 + 本周训练 → 课程计划 → 本周课程表 → 训练记录 → 课程卡”；课程计划左侧集中当前预约 / 候补，右侧“抢课”通过摘要卡和“代抢 / 上次抢课结果”Tab 集中自动抢课目标与业务结果。
- 上课统计与上课历史合并为训练记录；所选范围少于 5 节时不展示大趋势图。课程卡收为“课程使用 / 有效进度 / 计划结论”紧凑信息条。
- 自动抢课的下次 / 上次执行、累计成功、优先级和失败边界，以及完整 Session 实验详情，统一移入 Cloud；芭蕾页只保留薄连接状态和与课程直接相关的目标 / 结果。

### 已完成周日自动抢课 Fast Path

- 北京时间每周日 14:19:35 启动服务器本地服务并预热当前闻道 Session，14:20:00 准点先按课程 `芭蕾 L1 > 软开`、再按同课程日期 `周六 > 周日 > 周五 > 其他日期` 顺序预约；关键路径不经过 Codex、Skill 或 SSH。
- 当前固定目标的实际顺序为周五芭蕾 L1、周二芭蕾 L1、周五软开、周二软开、周四软开，均保持原晚间时段和大教室但不限老师。三个日期课表最多 3 路并发并按日期共享，课程卡与规则最多 2 路并发预检且 8 秒过期，HTTPS 使用最多 3 条 keep-alive 连接；真实预约 / 候补 mutation 仍严格串行，最终预约详情最多 3 路并发只读核验。每节按日期、课型 / 等级、起止时间和教室独立即时唯一匹配；老师不进入匹配或 occurrence 幂等键。发布延迟、临时网络失败和明确未开放可安全重试 3 次，单节失败或 mutation 结果未知仍继续后续课程，未知 mutation 本身不重复提交，全部结束后统一实时核验。身份失效或页面协议变化仍全局停止。
- 私有状态维护幂等 occurrence、累计预约数和累计候补数；公开状态只展示启用状态、计划、上次 / 下次执行、目标、逐课结果和累计数，经登录保护的 `no-store` alias 提供给芭蕾课程计划与 Cloud 运维卡。配置目标可预约则预约、仅可排队则候补；取消、转课、支付和登录继续禁止。
- `maxnow-ballet-live` Skill 已记录固定顺序、当前目标和只读状态入口；普通课程查询继续强制实时闻道且禁止缓存回退。

### 已完成芭蕾对话式显式预约

- 新增 `book_ballet.py` 与 hardened transient runner；Owner 在当前请求中明确指定课程后，可用日期、起止时间、课程名、老师和教室做实时精确匹配，统一预检已有预约、余位、唯一课程卡和约课规则。
- 单课或多课按输入顺序逐节预约，每节最多提交一次并立即从实时预约记录复核；预检不通过时整批不写入，执行阶段身份失效、规则变化或结果不明确时停止后续课程并逐节返回状态。
- `maxnow-ballet-live` Skill 已扩展为实时查询与显式预约入口；普通查询继续禁用 POST，预约仅允许固定资格检查、规则检查和 `do_addbook`，不支持自动取消、转课、支付、登录或候补写入。
- 2026-07-28 首次真实单课验收成功，独立实时约课记录复核为 `booked`；周日自动抢课已在后续独立模块落地，Apple 日历订阅仍保留在 Later。

### 已完成芭蕾实时查询 Skill

- 新增 `maxnow-ballet-live` Skill；Owner 询问课表、当前预约 / 候补、上课记录、老师、余位或课程卡时，固定连接 MaxNow 服务器并使用当前 PHPSESSID 实时查询闻道，禁止用 Dashboard 缓存、私有快照或旧对话结果回答。
- 实时查询按课表、预约、上课记录、课程卡选择最小只读范围，通过临时 systemd unit 注入 host-bound 加密凭据并直接返回脱敏 JSON；不读取或改写 `dash/data/ballet.*` 和 `/var/lib/maxnow-ballet`。
- 返回结果必须带 `source=wenda-live`、`live=true` 和当前 `fetchedAt`；身份、网络、页面结构或解析失败时 fail closed，不回退缓存。普通查询仍只使用既有闻道 GET allowlist；只有 Owner 当前请求中明确确认的精确课程才进入独立预约 runner。
- 泛问可约课程时默认展示全部课型，只有 Owner 明确限定“只看 / 仅看 / 只想看”某类课程时才筛选；直约课程固定按日期分组并显示开始–结束时间、课程名、老师、教室和余位。

### 已完成芭蕾只读训练闭环并启用自动同步

- 独立芭蕾页已覆盖下一节与所有预约、候补序号、真实取消截止、实际上课历史、整体训练统计、课程卡与本周训练摘要；每张课程卡独立展示开卡进度、到期前所需节奏和计划情景，开卡未满 28 天时不显示实际节奏，满 28 天后才按该卡自身使用量补充实际预测。
- 页面已增加全宽粉白周课表：桌面横轴按一小时段分列、纵轴为星期日期，同日同小时课程上下排列，整周无课程开始的连续小时压缩成单个时间范围列；全部小时与 7 天课程无内部滚动直接平铺，面板随内容自然增高，当天高亮、过去日期淡化、未来日期保持普通色。平时显示本周，周日 14:30 只读同步确认拿到下周课程后切换为本周日 + 下周一周。
- 闻道只读采集器仅允许已确认的 GET 页面，预约、候补、上课记录与课程卡分别进入脱敏快照和 canonical ledger；前端不包含 PHPSESSID、Cookie、会员卡号、会员 ID、源记录 ID 或原始响应。
- 服务器使用 host-bound systemd 加密凭据、enable gate、单实例锁和 fail-closed 身份阻断。每天 09:00 / 12:00 / 15:00 / 18:00 / 22:00 rolling、周日 14:30 额外刷新与每月 1 日 00:47 full timer 已启用；周日只读刷新与 14:20 自动抢课错开。身份失效立即停止后续请求，保留最后成功数据，直到安全凭据版本变化。
- 首次正式闭环同步保留 2 条实际上课、3 条正式预约和 1 条候补第 4 位；课程卡为 39 / 40 次、有效至 2027-01-23，本周预计 3–4 节、4–5.5 小时。
- PHPSESSID 活跃实验继续独立发布脱敏状态；它只证明每次检查时仍有效，不能推断静默闲置寿命、滑动过期或长期自动续期。

### 已建立数据失败与新鲜度闭环

- Home 数据同步统一区分已同步、暂无记录、请求失败、数据过期和尚未同步；同步成功后的数值 `0` 保持真实数值，不再与空数据混淆。
- 浏览器按数据源保存最后一次成功响应；短时 JSON 请求失败时继续展示旧数据，并在数据同步状态中明确标记“请求失败”和保留时间。
- 系统状态统一汇总 Wiki、Token、天气、市场、Last-30、版本、Roadmap、豆奶、同行记、生活和芭蕾 11 个 Owner 可见来源。
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
