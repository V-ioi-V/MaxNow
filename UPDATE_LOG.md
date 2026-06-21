# MaxNow 更新记录

这个文件记录 MaxNow 的重要更新，让产品方向、数据边界和实现决定可以被追溯。

## 使用规则

- 只要 Codex、Owner 或其他维护者改变了产品方向、页面代码、数据结构或操作规则，就在这里补一条。
- 每条记录保持简短、具体。
- 有必要时写清楚涉及哪些文件。
- 原始未来想法写进 `IDEAS.md`；已经确认的产品行为再同步进 `SPEC.md`。

## 2026-06-21

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
