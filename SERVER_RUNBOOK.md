# MaxNow 服务器操作说明

这个文件记录 MaxNow 服务器的 SSH 连接方式、前端静态站部署方式和常用排障命令。

## 服务器

```text
Host: 43.160.240.244
User: ubuntu
Domain: dash.maxnow.cn
Repo root: /var/www/maxnow-dashboard
Dash web root: /var/www/maxnow-dashboard/dash
Blog web root: /var/www/maxnow-dashboard/blog
Web server: nginx
```

本地 Windows 连接命令：

```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" ubuntu@43.160.240.244
```

一条命令执行远程检查：

```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" ubuntu@43.160.240.244 "hostname && whoami && uptime"
```

如果 SSH 在 `kex_exchange_identification` 阶段断开，先检查本地是否走了代理 / TUN 网卡。之前失败原因是 SSH 流量走了 `Meta` 代理网卡；关闭代理后，连接从 `WLAN` 出口恢复正常。

## 当前部署状态

2026-06-16 已完成首次静态站部署，2026-06-17 已切换为同仓库双出口部署：

```text
/var/www/maxnow-dashboard
```

该目录来自 GitHub 仓库；nginx 的两个站点根目录分别指向：

```text
dash.maxnow.cn -> /var/www/maxnow-dashboard/dash
blog.maxnow.cn -> /var/www/maxnow-dashboard/blog
```

Git 来源：

```text
https://github.com/V-ioi-V/MaxNow.git
branch: main
```

当前 nginx 配置：

```text
/etc/nginx/sites-available/maxnow-dashboard
/etc/nginx/sites-enabled/maxnow-dashboard
```

站点访问：

```text
https://dash.maxnow.cn
https://blog.maxnow.cn
```

当前 HTTPS 已启用，HTTP 请求会跳转到 HTTPS。`blog.maxnow.cn` 证书由 certbot 在 2026-06-17 申请，当前到期日为 2026-09-15，certbot 已配置自动续期。

2026-06-17 晚间已部署参考风格刷新版本：

```text
deployed commit: 2290eca Merge reference style refresh
dash.maxnow.cn: 200 MaxNow
blog.maxnow.cn: 200 MaxNow Blog
nginx: config test ok, reload ok
```

2026-06-19 已部署豆奶详情页和 Blog / Dash 视觉微调版本：

```text
deployed commit: 8d099f1 Merge dounai and blog UI polish
dash.maxnow.cn: 200
blog.maxnow.cn: 200
blog.maxnow.cn/topics.html: 200
nginx: config test ok, reload ok
```

2026-06-19 已修复豆奶签到数据写入路径分叉问题：

```text
root 签到脚本: /root/.openclaw/daily_checkin.sh
root 数据生成脚本: /root/.openclaw/gen_checkin_data.py
备份: /root/.openclaw/gen_checkin_data.py.bak-20260619-dounai-sync
旧数据出口: /root/MaxNow/dash/data/dounai_checkin.json
线上数据出口: /var/www/maxnow-dashboard/dash/data/dounai_checkin.json
```

豆奶签到仍由 root 的 OpenClaw 自动化在每天 9 点左右执行。`gen_checkin_data.py` 现在会把同一份 `dounai_checkin.json` 同时写入旧 OpenClaw 工作区和 nginx 正在读取的线上部署目录，避免页面继续停留在旧记录。

2026-06-21 已扩展 `/root/.openclaw/gen_checkin_data.py`：生成 `dounai_checkin.json` 时会用现有豆奶登录态只读打开 `https://dounai.pro/user/panel`，抓取 `剩余流量(主)`、`账号有效期 (0级)` 和 `VIP有效期 (1级)`，写入 `account` 字段。页面据此展示剩余可用流量、到期日和按剩余天数折算的每日可用流量。脚本也会按日期维护 `account_history`，每天覆盖 / 追加当天账号快照，用于展示近 30 天账号日均可用流量趋势。脚本更新前已备份到：

```text
/root/.openclaw/gen_checkin_data.py.bak-20260621-account-summary
/root/.openclaw/gen_checkin_data.py.bak-20260621-account-history
```

当前已验证抓到的账号快照：

```text
remaining_flow_label: 1.29TB
account_expires_at: 2027-05-01 20:04:52
vip_expires_at: 2027-04-30 10:15:41
daily_available_mb: 4321.61
```

2026-06-21 已部署 Dash 顶栏和豆奶详情页自适应微调版本：

```text
changes: 移除 Dash 顶栏重复域名；豆奶详情页顶部 tab 和内部指标改为按宽度自适应换行
dash styles version: styles.css?v=41
```

同日已补充部署桌面端豆奶指标宽度修正：

```text
changes: 恢复豆奶详情页桌面端顶部 tab 原始横排比例；内部指标桌面端三列铺满，中小屏再换行
dash styles version: styles.css?v=42
```

2026-06-23 已部署 Home 顶部天气卡和小日历 widget 调整版本：

```text
deployed commit: f7ee6bb Scale top widget content further
changes: Home 顶部新增北京市海淀区天气卡；天气卡与小日历拆成独立同级 widget；两个 widget 外框等高，内部内容放大；天气数据由 runtime 定时刷新
dash styles version: styles.css?v=58
dash app version: app.js?v=42
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260623-235840-before-weather-widgets
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200
```

2026-06-24 已部署 Home 天气卡底部信息分隔点微调：

```text
deployed commit: fd7b997 Add weather meta separators
changes: 天气卡底部地点、天气状态和低温 / 高温之间加入轻量小圆点分隔；Dash 样式缓存版本提升到 styles.css?v=59
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署云服务 tab：

```text
feature merge commit: 8aa8400 Merge cloud services dashboard tab
changes: Dash 左侧导航在 Token 下方新增“云服务”tab，只读列出服务器自动化、数据同步、Token 用量采集方案、豆奶签到和 nginx / HTTPS 托管边界
dash styles version: styles.css?v=60
dash app version: app.js?v=44
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200
```

2026-06-24 已部署 Home 天气卡底部文字自适应微调：

```text
deployed commit: c336d60 Merge weather meta text fit
changes: 天气卡底部地点、天气状态和低温 / 高温接近溢出时自动收小字号；Dash 缓存版本提升到 styles.css?v=60、app.js?v=44
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署 Dash tab 间距、天气更新时间和云服务卡片层级修复：

```text
deployed commit: 5ac9126 Merge tab spacing and cloud hierarchy fixes
changes: 修复豆奶顶部 tab 间距；恢复 Token 页范围切换为右侧紧凑选项；Home 天气卡显示 HH:mm 更新时间；云服务页基础运行同步显式列出 logs/weather.log；强化云服务卡片顶部信息并弱化底部明细
dash styles version: styles.css?v=63
dash app version: app.js?v=45
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-092405-before-tab-spacing-cloud
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=63 200；https://dash.maxnow.cn/app.js?v=45 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署 Home 卡片操作和云服务系统状态入口：

```text
deployed commit: c941944 Merge home card actions
changes: Home 近期待办右上入口改为“更多”；Home Token 近期用量右上角改为更新时间；Home 系统状态卡支持点击 / Enter / Space 跳转云服务；云服务页新增系统状态卡复用 dashboardData.system；记录噗噗每日待办提醒后续项
dash styles version: styles.css?v=65
dash app version: app.js?v=47
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-095712-before-home-card-actions
verification: python3 scripts/check.py ok；python3 scripts/update_data.py project-meta ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=65 200；https://dash.maxnow.cn/app.js?v=47 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署我和 Ricky 的同行记页面：

```text
deployed commit: b7d02aa Merge Ricky companion map
changes: Dash 左侧导航新增“同行记”并放在最后一个 tab；页面使用 Leaflet + CARTO Voyager 真实地图展示我和 Ricky 的共同足迹；新增 dash/data/ricky.* 和 scripts/sync_ricky_travel.py，从 private personal-wiki 的 wiki/relationships/ricky-travel.json 同步数据；地点和旅行记录暂时只进入地图 marker / popup，不单独铺列表
dash styles version: styles.css?v=69
dash app version: app.js?v=52
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-210052-before-ricky-map
verification: python3 scripts/update_data.py runtime ok，同步 11 个 Ricky 地点和 4 条记录；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=69 200；https://dash.maxnow.cn/app.js?v=52 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署同行记地图微调：

```text
deployed commit: 72dfbd6 Merge Ricky map display tuning
changes: 北海道地图点显示名缩短为“北海”；同行记页面左右留白收窄，地图高度提高，Leaflet fitBounds 最大缩放从 4 降到 3，让地图更宽并显示更多周边区域
dash styles version: styles.css?v=70
dash app version: app.js?v=53
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-212002-before-ricky-map-tune
runtime data stash before deploy: before-ricky-map-tune-runtime-data
verification: python3 scripts/update_data.py runtime ok，同步 11 个 Ricky 地点和 4 条记录；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/data/ricky.json 200；https://dash.maxnow.cn/styles.css?v=70 200；https://dash.maxnow.cn/app.js?v=53 200
```

2026-06-24 已部署同行记显式地图标签和正方形地图：

```text
deployed commit: df771be Merge explicit Ricky map labels
changes: personal-wiki Ricky 旅行地点新增 map_label；MaxNow 同步为 mapLabel，marker 不再取地点名前两个字；11 个标签为北京、札幌、东京、北海、大理、大同、天路、天津、沈阳、布统、阿那亚；同行记地图容器改为正方形居中展示
dash styles version: styles.css?v=71
dash app version: app.js?v=54
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-214401-before-ricky-labels-square
runtime data stash before deploy: before-ricky-labels-square-runtime-data
verification: python3 scripts/update_data.py runtime ok，同步 11 个 Ricky 地点和 4 条记录；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/data/ricky.json 200；https://dash.maxnow.cn/styles.css?v=71 200；https://dash.maxnow.cn/app.js?v=54 200；线上 ricky.json mapLabel 列表确认正确
```

2026-06-24 已部署 Codex Token 本机可读日志统计：

```text
deployed commit: 5e51d5c Add Codex token usage ledger
changes: 新增 Codex session `token_count` 本机可读日志账本、OpenClaw / Codex 统一 Token 总账和 Token 页统一数据入口；Codex 口径为本机可读 `.codex/sessions` 最终 `total_token_usage`，不导出 prompt / response 正文
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-225818-before-codex-token-usage
verification: python3 scripts/check.py ok；python3 scripts/update_data.py token-usage ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=55 200；https://dash.maxnow.cn/data/token-usage.json 200
```

2026-06-24 已部署 Token 缓存命中率和 Codex 模型 / 费用口径修正：

```text
deployed commit: 408cc6a Fix token cache rate and model cost basis
changes: Token 顶部新增缓存命中率；Codex 模型占比和调用列表显示 `gpt-5.5` 等真实模型名；Codex 费用改为 OpenAI API 等价估算并计入总费用
runtime data stash before deploy: before-token-model-cost-runtime-usage
verification: python3 scripts/update_data.py token-usage ok；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=72 200；https://dash.maxnow.cn/app.js?v=56 200；https://dash.maxnow.cn/data/token-usage.json 200；线上 token-usage 显示模型 `gpt-5.5`、缓存命中率 94.49%、估算费用 $590.10
```

2026-06-27 已部署本机 Codex Token 定期上报脚本：

```text
deployed commit: 25859dc Merge local Codex report SSH fix
changes: 新增 Windows 本机 Codex Token 上报脚本和 Task Scheduler 安装脚本；本机任务每 1 小时静默运行，只提交 codex-usage/token-usage 数据；服务器部署侧只合并 token-usage，不在服务器刷新本机 Codex collector；修复 PowerShell 远端 bash 脚本 CRLF 和 SSH 失败未冒泡问题
first manual report: 本机采集 86 个 Codex usage sessions，提交 d3e3f7c Update local Codex token usage，并推送到 origin/main
hourly hidden update: 2026-06-27 将任务改为每 1 小时静默运行；Task Scheduler action 先使用 powershell.exe -WindowStyle Hidden，任务设置 Hidden=true；远端 token 合并改为 base64 SSH payload，并按 SSH exit code 判断成败，避免 CRLF 和 git pull stderr 误判
no-flash update: 2026-07-02 将 Task Scheduler action 改为 wscript.exe scripts/report_codex_usage_hidden.vbs，由 VBS 以 window style 0 启动 PowerShell 上报脚本，避免 powershell.exe 仍可能产生的瞬时 console 闪窗
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/data/token-usage.json 200；隐藏计划任务手动启动后 LastTaskResult=0；服务器 HEAD 17f537d
```

2026-06-27 已部署豆奶图表动态刻度和 Token 默认范围修正：

```text
deployed commit: 613b64c Update local Codex token usage
included code commit: 55a1247 Fix chart scaling and token default range
changes: 折线图 y 轴对高位小波动数据使用动态刻度；豆奶日均可用流量图不再被 0 起点压扁；Token 页面默认范围从 7d 改为 1d
dash app version: app.js?v=57
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=57 200；https://blog.maxnow.cn 200
```

2026-06-27 已部署豆奶 GB 图表整数 y 轴刻度修正：

```text
deployed commit: fbe02f2 Use integer axis for dounai GB chart
changes: 豆奶“近 30 天日均可用流量”图保留动态缩放，但 y 轴边界改为整数 GB；4.19-4.26GB 这类数据展示为 4GB 到 5GB，点位标签仍保留两位小数
dash app version: app.js?v=58
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=58 200；线上 dash/app.js 确认 integerYScale 已启用
```

服务器部署博客预览时，曾将旧路径 `data/dashboard.*` 和 `data/wiki-todos.*` 备份到：

```text
~/maxnow-deploy-backups/20260617-180826
```

拉取新目录结构后，这些运行数据已恢复到 `dash/data/dashboard.*` 和 `dash/data/wiki-todos.*`。因此服务器工作区允许这些数据文件保持未提交状态，由后续同步脚本继续维护。

## GitHub CLI / private 仓库读取

2026-06-17 已确认服务器安装了 GitHub CLI：

```bash
command -v gh
gh auth status
```

当前服务器上的 `gh` 已授权为 `V-ioi-V`，scope 包含 `repo`，可读取 private `V-ioi-V/personal-wiki`。

验证 private personal-wiki 读取：

```bash
gh api 'repos/V-ioi-V/personal-wiki/contents/wiki/tasks/todo.json?ref=main' --jq .name
```

刷新 MaxNow 的 personal-wiki 待办缓存：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/sync_wiki_todos.py
python3 scripts/check.py
```

统一运行入口：

```bash
python3 scripts/update_data.py runtime
python3 scripts/update_data.py weather
python3 scripts/update_data.py market-indices
python3 scripts/update_data.py project-status
python3 scripts/update_data.py openclaw-usage
python3 scripts/update_data.py codex-usage
python3 scripts/update_data.py codex-macos-usage
python3 scripts/update_data.py codex-server-usage
python3 scripts/update_data.py token-usage
python3 scripts/update_data.py ai-last30
python3 scripts/update_data.py project-meta
python3 scripts/update_data.py wrap all
```

`runtime` 是服务器定时任务使用的安全入口，只刷新 wiki-todos、Ricky 旅行记录、生活页吃啥候选、天气、行情指数、系统状态、MaxNow 项目元信息和 wrapper，不覆盖 Owner 的今日判断或独立项目状态。`weather` 会刷新北京市海淀区天气卡，数据源为 Open-Meteo 免费 forecast API。`market-indices` 会刷新纳指100、标普500、上证指数、深证成指和创业板指，数据源为腾讯公开行情接口。`life-foods` 会从 private personal-wiki `wiki/life/food-picker.md` 同步生活页吃啥候选。`project-status` 会从 `ROADMAP.md` 显式刷新 `dash/data/project-status.*` 的当前主线 / 待推进、来源时间、生成时间和内容指纹；ROADMAP Now / Next / Done 变化后必须执行，且不会修改 `dashboard.today`。`openclaw-usage` 刷新 OpenClaw 源账本并合并统一 Token 总账；`codex-usage` 刷新 Windows 兼容本机 Codex 源账本并合并统一 Token 总账；`codex-macos-usage` 刷新 macOS 本机 Codex 源账本并合并统一 Token 总账；`codex-server-usage` 刷新服务器 Codex 源账本并合并统一 Token 总账；`token-usage` 只合并现有源账本。`ai-last30` 会刷新免费 AI 外部信号和 Last-30 滚动记忆，采集脚本本身不调用模型、不消耗 token。

刷新服务器 Codex Token 用量：

```bash
cd /var/www/maxnow-dashboard
sudo python3 scripts/update_data.py codex-server-usage
python3 scripts/check.py
```

本机 Windows 可直接在仓库目录运行：

```powershell
python scripts/update_data.py codex-usage
python scripts/check.py
```

本机 Windows 定期上报可以安装计划任务：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_local_codex_usage_task.ps1
```

默认任务名为 `MaxNow-Local-Codex-Usage-Report`，固定每小时 `:02` 静默运行。安装脚本会注册 hidden task，最长运行 10 分钟。Owner Windows 机器上当前使用专用 clone `D:\Personal\MaxNow-token-report`；Task Scheduler action 使用 `wscript.exe "D:\Personal\MaxNow-token-report\scripts\report_codex_usage_hidden.vbs"`，VBS launcher 再以 window style 0 启动 `scripts/report_codex_usage.ps1`。该任务要求运行目录在 `main` 且无无关脏文件，只提交 `dash/data/codex-usage.*` 源账本并推送到 `origin/main`。不要在服务器运行 `python3 scripts/update_data.py codex-usage`，否则会用服务器 `.codex` 覆盖 Windows 账本。

2026-07-06 修复过一次 Windows 专用 clone 上报卡住：主工作区 `D:\Personal\MaxNow` 配有 repo-local GitHub 代理，但 `D:\Personal\MaxNow-token-report` 缺少同样配置，导致计划任务在 `git pull --ff-only origin main` 处卡住或报 `Recv failure: Connection was reset`。当前该 clone 已设置：

```powershell
git -C D:\Personal\MaxNow-token-report config http.proxy http://127.0.0.1:7897
git -C D:\Personal\MaxNow-token-report config https.proxy http://127.0.0.1:7897
```

如果任务显示长时间 `Running` 且日志停在 `pull latest origin/main`，先检查 `git-remote-https` 是否卡住，再确认上述 proxy 仍存在。若专用 clone 因未推送生成物提交出现 `[origin/main: ahead ..., behind ...]`，先给当前 HEAD 建本地备份分支，再让 `main` 回到 `origin/main`，最后重新运行计划任务，由当前 `.codex/sessions` 重新生成 `codex-usage.*` 和 `token-usage.*`。2026-07-06 22:18 手动验证成功，`LastTaskResult=0`，线上 `Codex Windows` 来源更新时间为 `2026-07-06 22:18`。

本机 macOS 可直接在仓库目录运行：

```bash
python3 scripts/update_data.py codex-macos-usage
python3 scripts/check.py
```

本机 macOS 定期上报可以安装 launchd 任务：

```bash
bash scripts/install_local_codex_usage_launchd.sh
```

默认 label 为 `cn.maxnow.local-codex-usage-report`，通过 `StartCalendarInterval` 固定每小时 `:00` 运行。launchd 调用 `scripts/report_codex_usage.sh`，要求专用工作区位于 `main` 且无无关脏文件，只提交 `dash/data/codex-macos-usage.*` 并推送到 `origin/main`。Git HTTP 低速边界和 SSH keepalive 会让网络卡住后失败退出；日志写入 `~/Library/Logs/MaxNow/local-codex-usage-report.log`。

2026-07-07 已将 Owner macOS 的 launchd 任务改为使用专用 clone `/Users/bytedance/.maxnow-token-report`，plist 位于 `~/Library/LaunchAgents/cn.maxnow.local-codex-usage-report.plist`。原先指向 `/Users/bytedance/Desktop/Personal/MaxNow` 时，launchd 被 macOS Desktop 隐私权限拦截，日志出现 `Operation not permitted`，`launchctl print gui/501/cn.maxnow.local-codex-usage-report` 显示 `last exit code = 126`。修复命令为：

```bash
git clone git@github.com:V-ioi-V/MaxNow.git /Users/bytedance/.maxnow-token-report
bash scripts/install_local_codex_usage_launchd.sh --repo-root /Users/bytedance/.maxnow-token-report --run-now
```

修复后手动触发验证成功：`launchctl` 上次退出码为 `0`，`~/Library/Logs/MaxNow/local-codex-usage-report.log` 记录 `2026-07-07 17:32` 成功提交 `Update macOS Codex token usage`，线上 `token-usage.json` 的 `Codex macOS` 来源更新时间为 `2026-07-07 17:32`。

Codex collector 只读取 `.codex/sessions/**/*.jsonl` 中的 `token_count`、`turn_context.model` 和 `task_complete.duration_ms`，导出 token、已完成任务活跃时长、时间、来源、模型和费用估算；活跃时长不包含轮次之间空闲时间，不导出 prompt / response 正文。Windows、macOS、server 继续使用三个独立源账本。

2026-07-10 将 OpenClaw / Codex server 合并为固定小时源采集，标记块为 `MAXNOW-TOKEN-SOURCE-REFRESH`：

```cron
# BEGIN MAXNOW-TOKEN-SOURCE-REFRESH
5 * * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-token-source-refresh.lock /bin/bash scripts/refresh_token_sources_on_server.sh >> /var/www/maxnow-dashboard/logs/token-source-refresh.log 2>&1
# END MAXNOW-TOKEN-SOURCE-REFRESH
```

ubuntu crontab 在每小时 `:10` 拉取本机源账本并发布统一 Token 总账：

```cron
# BEGIN MAXNOW-TOKEN-USAGE-REFRESH
10 * * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-token-usage-refresh.lock /bin/bash scripts/refresh_token_usage_on_server.sh >> /var/www/maxnow-dashboard/logs/token-usage-refresh.log 2>&1
# END MAXNOW-TOKEN-USAGE-REFRESH
```

固定周期为 macOS `:00`、Windows `:02`、服务器源采集 `:05`、总账发布 `:10`。总账任务保留服务器运行态 `openclaw-usage.*` / `codex-server-usage.*`，再运行 `python3 scripts/update_data.py token-usage`；`git pull` 默认 120 秒超时。

2026-07-02 已部署 Token 来源卡范围口径修正：

```text
deployed commit: 5ff48a9 Merge token source range display fix
changes: Token 来源卡恢复卡片样式；Dash 缓存版本提升到 styles.css?v=73、app.js?v=60；来源卡按当前 1d / 7d / 30d / all 范围聚合；本机来源显示为 Codex Windows，后续 macOS 采集端可显示为 Codex macOS
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260702-111659-before-token-source-range
verification: python3 scripts/update_data.py token-usage ok；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=73 200；https://dash.maxnow.cn/app.js?v=60 200；https://dash.maxnow.cn/data/token-usage.json 200；线上 token-usage 有 46 个 day 写入 bySource；线上 1d 来源为 Codex Windows 36M，7d 来源为 Codex Windows 79M / OpenClaw 8.0M / Codex server 614K
```

2026-07-02 已部署 Token 来源费用并列面板：

```text
deployed commit: 79ba56f Merge token source inline panel
changes: Token 页将来源费用移动到和模型占比、调用消耗同一行；删除独占横向说明条；说明收敛为来源面板底部短中文提示；Dash 缓存版本提升到 styles.css?v=74、app.js?v=61
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260702-113616-before-token-inline-panel
verification: python3 scripts/update_data.py token-usage ok；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn/styles.css?v=74 200；https://dash.maxnow.cn/app.js?v=61 200；本地浏览器验证 Token 三个 detail 面板同顶同高、无横向溢出
```

2026-07-02 已修正顶栏 `OpenClaw 异常` 误报：

```text
deployed commit: d3aeae3 Treat recovered sync logs as clear
changes: system-status 将 codex-server/ricky 等运行态数据纳入 deploy 白名单；忽略 Python __pycache__；failure-log 只按每个日志最新 ok/fail 结果判断，旧 weather TLS 超时后续成功后不再持续告警；runtime 将 system-status 放在运行态同步末尾执行
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260702-114519-before-openclaw-status-false-alarm
verification: python3 scripts/update_data.py runtime ok；python3 scripts/check.py ok；线上 dashboard automation.status=正常，summary=nginx Active；cert 73d；deploy v1.0.0.00；CPU 0%；disk 62%；memory 50%
```

2026-07-02 已部署全局主题色 hover：

```text
deployed commit: e41223e Merge global themed hover states
changes: Dash 大模块和内部模块统一使用主题色 hover；大模块按自身主题色，内部条目优先按 data-tone / 模型来源语义色；Token 来源卡、模型卡、调用卡和 Home / 云服务 / 豆奶 / 同行记模块保持一致；Dash 缓存版本提升到 styles.css?v=79、app.js?v=66
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=79 200；https://dash.maxnow.cn/app.js?v=66 200；本地浏览器验证 Home / Token / 云服务 / 豆奶 / 同行记桌面和移动端无横向溢出，抽样 hover 使用对应主题色
```

2026-07-02 已移除顶栏系统自动化重复状态：

```text
deployed commit: 7566242 Merge duplicate automation badge removal
changes: 删除 Dash 顶栏右侧 `系统自动化 正常` badge；保留 Home 首屏“系统自动化”状态卡作为唯一健康状态入口；Dash 缓存版本提升到 app.js?v=67
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=67 200；线上 dash/index.html 和 dash/app.js 确认无 operator-status 残留
```

2026-07-02 已压缩 Home 当前主线模块：

```text
deployed commit: 9e015ee Merge compact home mainline panel
changes: Home “当前主线”模块在桌面端改为标题和内容同一行的紧凑状态条；减少只有一条主线时的大面积空白；同步收紧待推进条目的垂直留白；Dash 缓存版本提升到 styles.css?v=80
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=80 200；本地浏览器测量桌面 #focus 高度约 101px，页面无横向溢出
```

2026-07-02 已修正 Home hover 主题色优先级：

```text
deployed commit: a72cc8b Merge home hover theme fix
changes: Home 指标卡 hover 不再被 status-strip 通用规则覆盖；待推进 / Token / 系统自动化分别使用橙色 / 紫色 / 绿色；天气卡按天气语义色 hover，时间卡使用橙色；Dash 缓存版本提升到 styles.css?v=81
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=81 200；本地浏览器抽样确认天气、时间、待推进、Token、系统自动化、wiki、豆奶、近期 Token 均使用对应主题色 hover
```

2026-07-02 已部署侧边栏 Token 范围口径同步：

```text
deployed commit: 4883cea Merge sidebar token range sync
changes: 侧边栏 Token 摘要增加范围前缀；Token 页切换 1d / 7d / 30d / all 时同步当前范围；其他页面默认显示 7d 摘要；Dash 缓存版本提升到 app.js?v=68
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=68 200；本地浏览器验证 Token 页 1d 显示 1d 86M，切换 7d 后侧边栏与主卡同步，回 Home 显示 7d 摘要
```

2026-07-02 已部署 Home / 同行记轻量交互整理：

```text
deployed commit: 7472f26 Remove wiki todo item links
changes: Last-30 条目改为整卡跳转并展示来源 / 置信度摘要；侧边栏豆奶和 Token 改回描述文案；同行记地图铺满地图卡宽度；Personal Wiki 近期待办移除逐条“打开”链接且卡片不跳转
dash styles version: styles.css?v=83
dash app version: app.js?v=71
verification: git pull --ff-only origin main ok；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=83 200；https://dash.maxnow.cn/app.js?v=71 200；https://blog.maxnow.cn 200
```

2026-07-02 已部署生活 tab 和吃啥随机选择器：

```text
deployed commit: 7a8a26f Keep existing life foods when wiki source is unavailable
feature commits: ff52586 Add life food picker；7a8a26f Keep existing life foods when wiki source is unavailable
changes: Dash 左侧导航新增“生活”tab；新增“吃啥”随机选择器、personal-wiki 菜品同步脚本和 dash/data/life-foods.*；吃啥结果区使用真实纵向滚动动画，数量为多个时上下叠放独立滚轮；脚本在服务器读不到 personal-wiki 源文件时保留现有 life-foods 缓存，避免 runtime 失败。
dash styles version: styles.css?v=86
dash app version: app.js?v=76
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260702-231615-before-life-food-picker
runtime data stash before deploy: before-life-food-picker-runtime-data
verification: git pull --ff-only origin main ok；python3 scripts/update_data.py runtime ok（life-foods 使用现有缓存，gh api 404 已降级为 warn）；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=86 200；https://dash.maxnow.cn/app.js?v=76 200；https://dash.maxnow.cn/data/life-foods.json 200；https://blog.maxnow.cn 200
```

2026-07-08 已部署 Dash 首屏加载优化：

```text
deployed commit: b0592ef Refresh project meta
feature commit: 03fda7c Optimize dash initial load
changes: Dash 首屏移除 data/*.js wrapper 同步加载，只保留 app.js?v=96；Home 先渲染核心小数据，Token / Ricky / Life / Leaflet 按视图加载；JSON fetch 改为正常 URL + cache:no-cache。
nginx changes: dash server block 启用 gzip；静态 css/js/png 设置 private, max-age=3600；/data/ 设置 private, max-age=60, must-revalidate。
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260708-124622-before-fast-load
nginx config backup before reload: /etc/nginx/sites-available/maxnow-dashboard.bak-20260708-fast-load
verification: python3 scripts/check.py ok；本地 Chrome headless 可执行并渲染 Token 热力格；服务器 nginx -t ok；reload ok；https://dash.maxnow.cn 200；线上 index 只引用 app.js?v=96；app.js?v=96 gzip 约 30KB；token-usage.json gzip 约 33KB；响应头确认 Cache-Control 和 Content-Encoding 生效。
```

2026-07-10 已部署 Today Status 时间轴和 Home 版本更新布局修复：

```text
deployed commit: 008ed5a Merge version update layout fixes
changes: 修复 Today Status 当前时间与进度条重叠；将“最近更新”改名为“版本更新”并移到外部输入下方；Dash 样式缓存版本提升到 styles.css?v=122；MaxNow 版本提升到 1.0.0.49。
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260710-093053-before-version-update
runtime data stash before deploy: before-version-update-deploy-20260710-093053
runtime preservation: 恢复 ai-news、dashboard、豆奶、Last-30、市场、OpenClaw、Codex Server、Ricky、Token 和 Wiki Todo 运行数据；重新生成 project-meta；Codex Server 账本保持 11 次会话和 4,993,467 Token。
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；nginx active；https://dash.maxnow.cn 200；https://blog.maxnow.cn 200；线上 VERSION 1.0.0.49；styles.css?v=122 已生效。
```

2026-07-10 已部署 Home 项目状态可信度修复：

```text
deployed commit: eade306 Fix Home project status freshness
changes: ROADMAP 生成状态从 dashboard.* 拆到独立 project-status.*；新增来源时间、生成时间、7 天过期阈值和内容指纹；过期状态不再驱动 Today Status；scripts/check.py 拒绝 Done 或与 ROADMAP 不一致的事项
dash styles version: styles.css?v=123
dash app version: app.js?v=108
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260710-104139-before-home-project-status
runtime preservation: 恢复 ai-news、dashboard、豆奶、Last-30、市场、Ricky 和 Wiki Todo；从 dashboard 运行态移除旧 mainlines/actions 后重生成 wrapper；重新生成 project-meta
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/data/project-status.json 200；线上 VERSION 1.0.0.51；待推进为访问保护、数据健康闭环、前端自动测试
```

2026-07-10 已部署 Token 活跃时长和固定小时周期：

```text
deployed commit: cacd002 Update macOS Codex token usage
feature commit: 178bbd0 Add token runtime and fixed reporting cycle
changes: Codex 账本新增 task_complete.duration_ms 活跃时长；固定周期为 macOS :00、Windows :02、服务器源采集 :05、总账发布 :10；本机 Git 增加低速和 SSH keepalive 边界；Token 页新增 Codex 时长并修复 390px 图表横向溢出
dash styles version: styles.css?v=124
dash app version: app.js?v=109
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260710-115834-before-token-runtime
root crontab backup: /home/ubuntu/maxnow-deploy-backups/20260710-115913-root-crontab-before-token-cycle
ubuntu crontab backup: /home/ubuntu/maxnow-deploy-backups/20260710-115913-ubuntu-crontab-before-token-cycle
runtime preservation: 恢复 dashboard、AI、Last-30、Wiki、市场、同行记、生活、豆奶、OpenClaw 和 Codex Server 运行态数据；重新生成 project-meta 和 token-usage
verification: macOS launchd StartCalendarInterval Minute=0、首次运行 exit 0；root :05 / ubuntu :10 cron 生效且旧 Token cron 已移除；OpenClaw 373 runs、Codex Server 11 sessions；总账 activeSeconds=226868、completedTurns=3738；python3 scripts/check.py ok；nginx -t ok；https://dash.maxnow.cn 200；线上 v1.0.0.52、1d Codex 时长 20m、无横向溢出
```

刷新 Home 天气卡：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py weather
python3 scripts/check.py
```

天气卡读取 `dash/data/dashboard.json.weather`，由 `scripts/sync_weather.py` 写入并同步生成 `dash/data/dashboard.js`。当前位置固定为北京市海淀区，坐标约 `39.96, 116.30`。前端只读本地数据，不直接请求天气接口。

刷新 Home 市场涨幅卡：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py market-indices
python3 scripts/check.py
```

市场涨幅卡读取 `dash/data/market-indices.json`，由 `scripts/sync_market_indices.py` 写入并同步生成 `dash/data/market-indices.js`。当前指数为纳指100、标普500、上证指数、深证成指和创业板指；脚本保存点位、昨收、涨跌幅和压缩后的 1 日分钟走势点。前端只读本地数据，不直接请求第三方行情接口。

刷新免费 AI 外部信号和 Last-30：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py ai-last30
python3 scripts/check.py
```

当前免费源包括官方 RSS / 博客、GitHub releases、Hacker News、GDELT 和 arXiv 等。免费源偶发超时或限流时，脚本会记录部分失败并保留其他结果；X / Twitter 暂不作为基础来源。

2026-06-23 已用 `ubuntu` 用户 crontab 接入 AI Last-30 免费外部信号同步，标记块为 `MAXNOW-AI-LAST30-SYNC`：

```cron
0 0 * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-ai-last30.lock /bin/bash -lc 'set -o pipefail; echo "[$(date -Is)] maxnow ai-last30 sync start"; python3 scripts/update_data.py ai-last30; echo "[$(date -Is)] maxnow ai-last30 sync ok"' >> /var/www/maxnow-dashboard/logs/ai-last30.log 2>&1
```

该任务每天服务器本地时间 00:00 刷新 `dash/data/ai-news.*` 和 `dash/data/last-30.*`。脚本只使用免费公开源，本身不调用模型、不消耗 token。Last-30 左列采用“当天优先、最新回退”：当天有高相关信号时显示“今日 AI 信号”；当天暂无条目时显示“最新 AI 信号”，从最近 7 天内选择最新高相关信号，避免 00:00 刷新后空白。

刷新 MaxNow 版本号和最近更新模块：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py project-meta
python3 scripts/check.py
```

版本号由仓库根目录 `VERSION` 手动维护，格式为 `x.x.x.xx`，例如 `1.0.0.00`。`scripts/sync_project_meta.py` 会读取 `VERSION`、Git 状态和 `UPDATE_LOG.md`，生成 `dash/data/project-meta.json` / `dash/data/project-meta.js`。

版本提升规则：

- 小 UI / 文案 / 布局调整：升最后两位，例如 `1.0.0.00` -> `1.0.0.01`。
- 新增页面能力 / 新数据源 / 新自动化：升最后两位。
- 重要功能模块稳定落地：升 patch，并把最后两位归零，例如 `1.0.0.12` -> `1.0.1.00`。
- 大版本阶段切换：升 minor 或 major，并重置后续位。
- 每次完成 Owner 可见或运维相关改动后，都要同步更新 `VERSION` 并运行 `python scripts/update_data.py project-meta`。

刷新 OpenClaw Token 用量账本：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py openclaw-usage
python3 scripts/check.py
```

`scripts/sync_openclaw_usage.py` 只读 `/root/.openclaw/agents/main/sessions/*.trajectory.jsonl`、cron runs 和 sessions 元数据，生成 `dash/data/openclaw-usage.json` / `dash/data/openclaw-usage.js`。它按 Asia/Shanghai 日期聚合 input / output / cacheRead / total token，并用 OpenRouter 模型价格生成 `openrouter-equivalent` 费用估算。该费用不是真实供应商账单。默认采集长期窗口，Token 页面再切分 1d / 7d / 30d / all。

OpenClaw trajectory 位于 `/root/.openclaw`，普通 `ubuntu` 用户不能读取，因此由 root 的 `MAXNOW-TOKEN-SOURCE-REFRESH` 每小时 `:05` 与 Codex server 一起刷新；任务结束后恢复前端数据文件归属：

```cron
# BEGIN MAXNOW-TOKEN-SOURCE-REFRESH
5 * * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-token-source-refresh.lock /bin/bash scripts/refresh_token_sources_on_server.sh >> /var/www/maxnow-dashboard/logs/token-source-refresh.log 2>&1
# END MAXNOW-TOKEN-SOURCE-REFRESH
```

2026-07-07 修复：线上 `openclaw-usage.*` 曾被仓库空基线覆盖，导致 Token 页只剩 Codex 来源。已用 root 重新运行 `python3 scripts/update_data.py openclaw-usage`，恢复 346 个 OpenClaw runs，并加固本机 Codex 上报脚本的服务器合并逻辑：空运行时备份不会覆盖非空账本，OpenClaw 为空时会优先用 `/root/.openclaw` 刷新源账本。

2026-07-05 复查：`logs/openclaw-usage.log` 显示 2026-07-03、2026-07-04、2026-07-05 均完成 `maxnow openclaw usage sync ok`，线上 `dash/data/openclaw-usage.json` 已更新到 2026-07-05 00:20。

刷新 MaxNow 的系统状态缓存：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/sync_system_status.py
python3 scripts/check.py
```

`scripts/sync_system_status.py` 只更新 `dash/data/dashboard.json` / `dash/data/dashboard.js` 中的 `automation` 和 `system` 字段，用来展示 nginx、HTTPS、证书到期、腾讯云位置、计费/有效期、git commit、最近拉取、wiki-todos 同步、定时任务、失败日志、CPU、磁盘、内存和 uptime。它不应该覆盖 `dashboard.today`、日常记录或独立的 `project-status.*`。

在腾讯云服务器上，它还会通过 metadata 服务读取：

```bash
curl http://metadata.tencentyun.com/latest/meta-data/instance-id
curl http://metadata.tencentyun.com/latest/meta-data/public-ipv4
curl http://metadata.tencentyun.com/latest/meta-data/placement/region
curl http://metadata.tencentyun.com/latest/meta-data/placement/zone
curl http://metadata.tencentyun.com/latest/meta-data/payment/charge-type
curl http://metadata.tencentyun.com/latest/meta-data/payment/termination-time
curl http://metadata.tencentyun.com/latest/meta-data/payment/create-time
```

当前服务器可读到：`ap-singapore` / `ap-singapore-2`，实例 `ins-2814k2h0`，按量计费 `POSTPAID_BY_HOUR`，`termination-time=null`，因此没有固定包年包月到期日。

证书到期由脚本直接检查 `https://dash.maxnow.cn` 的 TLS 证书。最近拉取时间来自 `.git/FETCH_HEAD` 的修改时间。

## 服务器资源清理记录

2026-07-05 已处理一次磁盘和内存占用排查：

- 根盘清理前约 `25G / 40G`，使用率约 66%；清理后约 `21G / 40G`，使用率约 56%。
- `lighthouse-chromium.service` 曾以 `Restart=always` 每 3 秒失败重启，24 小时内产生大量 journal。失败原因是该服务使用 `/root/.openclaw/browser-existing-session` 作为 Chromium profile，但已有 OpenClaw Chromium 会话持有 `SingletonLock`。
- 已执行 `sudo systemctl stop lighthouse-chromium.service` 和 `sudo systemctl disable lighthouse-chromium.service`，复查状态为 `disabled` / `inactive`。
- 已用 `sudo journalctl --vacuum-size=300M` 将 systemd journal 从约 2.8G 降到约 264M。
- 已清理 apt cache、npm cache、pnpm metadata cache，并删除 Playwright 中未被当前进程使用的 `ffmpeg-1011` 和 `chromium_headless_shell-1208`。
- 已保留 `/root/.cache/ms-playwright/chromium-1208`，因为当前 OpenClaw Chromium 进程仍从该目录运行；不要在未安排 OpenClaw 浏览器维护窗口时删除它。

后续如果确实需要恢复 `lighthouse-chromium.service`，应先确认 9222 端口和 Chromium profile 归属，只保留一个浏览器 owner，或给该 service 配置独立 `--user-data-dir`，避免再次与 OpenClaw 浏览器会话争用同一个 profile。

2026-07-06 已修复一次豆奶自动化 Playwright 浏览器缺失：

- 现象：09:00 豆奶签到和 00:05 traffic closeout 均报 `BrowserType.launch: Executable doesn't exist`，路径指向 `/root/.cache/ms-playwright/chromium_headless_shell-1208/...`；`dash/data/dounai_checkin.json` 的 `updatedAt` 会变化，但 `today`、账号快照和真实流量仍停在旧日期，并可能出现 `stale` / `last_error`。
- 原因：清理服务器缓存后只保留了 `/root/.cache/ms-playwright/chromium-1208`，但当前 Python Playwright 1.58.0 的脚本启动 headless Chromium 时需要 `chromium_headless_shell-1208`。
- 修复：以 root 执行 `python3 -m playwright install chromium`，补齐 `/root/.cache/ms-playwright/chromium_headless_shell-1208` 和 `/root/.cache/ms-playwright/ffmpeg-1011`，再用 `sync_playwright().chromium.launch(headless=True)` 做 smoke test。
- 补数：使用 `/root/.openclaw/daily_checkin.sh` 手动补跑签到和 MaxNow 数据同步；该脚本不发微信通知。不要为了补数直接运行 `/root/.openclaw/dounai_cron.sh`，因为它会向 WeChat 发送签到通知。
- 日结：补签后可运行 `python3 /root/.openclaw/gen_checkin_data.py --traffic-only --exclude-today`，让真实流量历史继续排除当天不完整数据。
- 清理规则：以后清理 Playwright 缓存前，先用 `python3 -m playwright --version` 和一次 headless launch smoke test 确认当前脚本需要的浏览器目录；不要只凭目录名判断 `chromium_headless_shell-*` 可删除。

2026-06-18 已用 `ubuntu` 用户 crontab 接入 dashboard 数据同步，标记块为 `MAXNOW-DASHBOARD-SYNC`：

```cron
*/10 * * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-dashboard-sync.lock /bin/bash -lc 'set -o pipefail; echo "[$(date -Is)] maxnow dashboard sync start"; python3 scripts/update_data.py runtime; echo "[$(date -Is)] maxnow dashboard sync ok"' >> /var/www/maxnow-dashboard/logs/maxnow-sync.log 2>&1
```

该任务会通过 `runtime` 一并刷新 wiki-todos、Ricky 旅行记录、生活页吃啥候选、北京市海淀区天气、系统状态和项目元信息。

查看当前 crontab：

```bash
crontab -l
```

失败日志目前按以下位置检测：

```text
/var/www/maxnow-dashboard/logs/ai-last30.log
/var/www/maxnow-dashboard/logs/wiki-todos.log
/var/www/maxnow-dashboard/logs/weather.log
/var/www/maxnow-dashboard/logs/market-indices.log
/var/www/maxnow-dashboard/logs/system-status.log
/var/www/maxnow-dashboard/logs/maxnow-sync.log
```

如果只想预览将采集到的状态，不写文件：

```bash
python3 scripts/sync_system_status.py --dry-run
```

注意：运行同步脚本会改写 `dash/data/wiki-todos.*` 或 `dash/data/dashboard.*`。如果只是验证能力而不想保留工作区改动，可以执行：

```bash
git checkout -- dash/data/wiki-todos.json dash/data/wiki-todos.js dash/data/dashboard.json dash/data/dashboard.js
```

## 豆奶签到数据同步

豆奶签到自动化不由 `ubuntu` 用户的 `MAXNOW-DASHBOARD-SYNC` cron 直接执行；它由 root/OpenClaw 侧脚本维护：

```bash
sudo crontab -l
sudo tail -120 /root/.openclaw/checkin.log
sudo tail -120 /root/.openclaw/traffic_closeout.log
sudo python3 /root/.openclaw/gen_checkin_data.py
sudo python3 /root/.openclaw/gen_checkin_data.py --traffic-only --exclude-today
```

日常预期：

- 签到脚本先更新 `/root/.openclaw/dounai_weekly.json`。
- `gen_checkin_data.py` 从 weekly 数据生成最近 60 天的 `dounai_checkin.json`。
- 同一份结果同时写入 `/root/MaxNow/dash/data/dounai_checkin.json` 和 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。
- `gen_checkin_data.py` 还会抓取豆奶用户面板上的剩余流量和有效期，写入 `account` 字段，并维护最近 60 天 `account_history`；如果抓取失败，会尽量保留上一份 `account` 和 `account_history`，并标记 `stale` / `last_error`。
- root crontab 里有两个豆奶任务：09:00 的 `MAXNOW-DOUNAL-CHECKIN` 负责签到、账号快照和完整生成；00:05 的 `MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT` 只运行 `gen_checkin_data.py --traffic-only --exclude-today`，专门更新昨天及更早的真实流量使用量。
- 线上 `dash.maxnow.cn` 读取 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。

2026-07-05 已做只读调研并接入直接流量使用抓取，确认当前数据边界：

- `records` 保存签到奖励记录，当前线上有 61 天。
- `account_history` 从 2026-06-21 开始保存账号余量快照，截至 2026-07-05 只有 15 天，不足完整 30 天。
- 重新登录后确认豆奶用户区有 `流量日志`：`https://dounai.pro/user/trafficlog` 直接展示最近 7 天真实使用量。
- `https://dounai.pro/user/trafficlog?ajax=1` 返回近 12 小时节点活跃和节点流量占比；这个窗口不是 7 天或 30 天总量。
- 已备份 `/root/.openclaw/gen_checkin_data.py` 到 `/root/.openclaw/gen_checkin_data.py.bak-20260705-traffic-usage`，并扩展脚本写入 `traffic_usage` 和 `traffic_usage_history`。
- 2026-07-05 已再次备份 `/root/.openclaw/gen_checkin_data.py` 到 `/root/.openclaw/gen_checkin_data.py.bak-20260705-traffic-closeout`，新增 `--traffic-only --exclude-today` 模式。
- 2026-07-05 已备份 root crontab 到 `/root/.openclaw/root-crontab-20260705-traffic-closeout.bak`，并新增 `MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT`：
- 2026-07-06 手动恢复后线上 `today` 为 `2026-07-06`，`account.synced_at` 为 `2026-07-06 21:28`，`traffic_usage.synced_at` 为 `2026-07-06 21:29`，并确认 `account` / `traffic_usage` 不再带 `stale` 或 `last_error`。

```cron
# BEGIN MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT
5 0 * * * cd /root/.openclaw && /usr/bin/flock -n /tmp/maxnow-dounai-traffic-closeout.lock /bin/bash -lc 'set -o pipefail; echo "[$(date -Is)] dounai traffic closeout start"; python3 /root/.openclaw/gen_checkin_data.py --traffic-only --exclude-today; chown ubuntu:www-data /var/www/maxnow-dashboard/dash/data/dounai_checkin.json; echo "[$(date -Is)] dounai traffic closeout ok"' >> /root/.openclaw/traffic_closeout.log 2>&1
# END MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT
```

- 00:05 traffic closeout 会从 `traffic_usage.daily` 和 `traffic_usage_history` 中剔除当天，只保留昨天及更早日期；每日 9 点豆奶自动化仍可用于签到和账号快照。前端实际使用量图也会排除当天。
- 账号余量差分口径只作为缺数据时的兜底估算说明；真实使用量展示优先使用 `traffic_usage_history`。

验证今天是否进入线上页面：

```bash
sudo python3 - <<'PY'
import json
from pathlib import Path
for path in [
    Path('/root/MaxNow/dash/data/dounai_checkin.json'),
    Path('/var/www/maxnow-dashboard/dash/data/dounai_checkin.json'),
]:
    data = json.loads(path.read_text(encoding='utf-8'))
    print(path, data.get('updatedAt'), data.get('today'))
PY

cd /var/www/maxnow-dashboard
python3 scripts/check.py
```

## 首次部署命令

这些命令已在服务器上执行过，记录在这里方便复现：

```bash
sudo apt-get update
sudo apt-get install -y nginx git

sudo rm -rf /var/www/maxnow-dashboard
sudo git clone --branch main https://github.com/V-ioi-V/MaxNow.git /var/www/maxnow-dashboard
sudo chown -R ubuntu:www-data /var/www/maxnow-dashboard

sudo tee /etc/nginx/sites-available/maxnow-dashboard >/dev/null <<'EOF'
server {
  server_name dash.maxnow.cn;

  root /var/www/maxnow-dashboard/dash;
  index index.html;

  gzip on;
  gzip_vary on;
  gzip_min_length 1024;
  gzip_types text/css application/javascript application/json image/svg+xml;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location ~* \.(?:css|js|png)$ {
    add_header Cache-Control "private, max-age=3600";
    try_files $uri =404;
  }

  location /data/ {
    add_header Cache-Control "private, max-age=60, must-revalidate";
  }

  listen 443 ssl;
  ssl_certificate /etc/letsencrypt/live/dash.maxnow.cn/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/dash.maxnow.cn/privkey.pem;
  include /etc/letsencrypt/options-ssl-nginx.conf;
  ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
  listen 80;
  server_name dash.maxnow.cn;
  return 301 https://$host$request_uri;
}

server {
  server_name blog.maxnow.cn;

  root /var/www/maxnow-dashboard/blog;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  listen 443 ssl;
  ssl_certificate /etc/letsencrypt/live/blog.maxnow.cn/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/blog.maxnow.cn/privkey.pem;
  include /etc/letsencrypt/options-ssl-nginx.conf;
  ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
  listen 80;
  server_name blog.maxnow.cn;
  return 301 https://$host$request_uri;
}
EOF

sudo ln -sf /etc/nginx/sites-available/maxnow-dashboard /etc/nginx/sites-enabled/maxnow-dashboard
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx || sudo systemctl restart nginx
```

## 更新前端页面

当 `main` 已经在 GitHub 上更新后，在服务器执行：

```bash
cd /var/www/maxnow-dashboard
git pull --ff-only origin main
python3 scripts/check.py
sudo nginx -t
sudo systemctl reload nginx
```

如果出现 Git ownership 保护错误，确认目录归属：

```bash
sudo chown -R ubuntu:www-data /var/www/maxnow-dashboard
```

## 验证命令

服务器本地检查 nginx：

```bash
sudo nginx -t
sudo systemctl status nginx --no-pager
curl -I -H 'Host: dash.maxnow.cn' http://127.0.0.1/
curl -I https://dash.maxnow.cn
curl -I https://blog.maxnow.cn
curl -I https://blog.maxnow.cn/topics.html
```

本地 Windows 检查域名：

```powershell
Invoke-WebRequest -Uri "http://dash.maxnow.cn" -UseBasicParsing
Invoke-WebRequest -Uri "https://blog.maxnow.cn" -UseBasicParsing
```

正常结果应返回 HTTP 200，页面标题为 `MaxNow`。

## 常见问题

### SSH 端口通但连接被关闭

现象：

```text
kex_exchange_identification: Connection closed by remote host
```

排查：

```powershell
Test-NetConnection 43.160.240.244 -Port 22 | Format-List
```

如果 `InterfaceAlias` 是代理 / TUN 网卡，先关闭代理或让 SSH 直连。

服务器侧检查：

```bash
sudo systemctl status ssh --no-pager
sudo journalctl -u ssh -n 100 --no-pager
sudo tail -n 100 /var/log/auth.log
```

### 域名返回 502

可能原因：

- nginx 没有安装或没有运行。
- nginx 配置没有指向 `/var/www/maxnow-dashboard/dash`。
- 域名已解析，但站点配置未启用。

检查：

```bash
sudo nginx -t
sudo systemctl status nginx --no-pager
ls -la /etc/nginx/sites-enabled
ls -la /var/www/maxnow-dashboard
```

## 后续待补

- 决定是否加 Basic Auth、VPN、IP 限制或其他访问保护。
- 给定时同步补失败提醒，或让 Home 更明确展示最近一次自动同步结果。
- 做数据更新工具，让 `dash/data/*.json` 与 `.js` wrapper 自动保持一致。
