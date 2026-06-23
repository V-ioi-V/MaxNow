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
dash app version: app.js?v=43
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200
```

2026-06-24 已部署 Home 天气卡底部文字自适应微调：

```text
deployed commit: c336d60 Merge weather meta text fit
changes: 天气卡底部地点、天气状态和低温 / 高温接近溢出时自动收小字号；Dash 缓存版本提升到 styles.css?v=60、app.js?v=44
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://blog.maxnow.cn 200
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
python3 scripts/update_data.py project-status
python3 scripts/update_data.py openclaw-usage
python3 scripts/update_data.py ai-last30
python3 scripts/update_data.py project-meta
python3 scripts/update_data.py wrap all
```

`runtime` 是服务器定时任务使用的安全入口，只刷新 wiki-todos、天气、系统状态、MaxNow 项目元信息和 wrapper，不覆盖 Owner 的今日判断。`weather` 会刷新北京市海淀区天气卡，数据源为 Open-Meteo 免费 forecast API。`project-status` 会从 `ROADMAP.md` 显式刷新 Home 的当前主线 / 今日推进，需要手动执行。`ai-last30` 会刷新免费 AI 外部信号和 Last-30 滚动记忆，采集脚本本身不调用模型、不消耗 token。

刷新 Home 天气卡：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py weather
python3 scripts/check.py
```

天气卡读取 `dash/data/dashboard.json.weather`，由 `scripts/sync_weather.py` 写入并同步生成 `dash/data/dashboard.js`。当前位置固定为北京市海淀区，坐标约 `39.96, 116.30`。前端只读本地数据，不直接请求天气接口。

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

该任务每天服务器本地时间 00:00 刷新 `dash/data/ai-news.*` 和 `dash/data/last-30.*`。脚本只使用免费公开源，本身不调用模型、不消耗 token。

刷新 MaxNow 版本号和最近更新模块：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py project-meta
python3 scripts/check.py
```

版本号由仓库根目录 `VERSION` 手动维护，格式为 `x.x.x.xx`，例如 `1.0.0.00`。`scripts/sync_project_meta.py` 会读取 `VERSION`、Git 状态和 `UPDATE_LOG.md`，生成 `dash/data/project-meta.json` / `dash/data/project-meta.js`。

刷新 OpenClaw Token 用量账本：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py openclaw-usage
python3 scripts/check.py
```

`scripts/sync_openclaw_usage.py` 只读 `/root/.openclaw/agents/main/sessions/*.trajectory.jsonl`、cron runs 和 sessions 元数据，生成 `dash/data/openclaw-usage.json` / `dash/data/openclaw-usage.js`。它按 Asia/Shanghai 日期聚合 input / output / cacheRead / total token，并用 OpenRouter 模型价格生成 `openrouter-equivalent` 费用估算。该费用不是真实供应商账单。默认采集长期窗口，Token 页面再切分 1d / 7d / 30d / all。

计划用 root crontab 单独每天刷新一次 OpenClaw 用量，不混进每 10 分钟的 `MAXNOW-DASHBOARD-SYNC`。原因是 OpenClaw trajectory 位于 `/root/.openclaw`，普通 `ubuntu` 用户不能直接读取；任务结束后需要把生成的前端数据文件归属恢复为 `ubuntu:www-data`：

```cron
# BEGIN MAXNOW-OPENCLAW-USAGE
20 0 * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-openclaw-usage.lock /bin/bash -lc 'set -o pipefail; echo "[$(date -Is)] maxnow openclaw usage sync start"; python3 scripts/update_data.py openclaw-usage; chown ubuntu:www-data dash/data/openclaw-usage.json dash/data/openclaw-usage.js logs/openclaw-usage.log; echo "[$(date -Is)] maxnow openclaw usage sync ok"' >> /var/www/maxnow-dashboard/logs/openclaw-usage.log 2>&1
# END MAXNOW-OPENCLAW-USAGE
```

刷新 MaxNow 的系统状态缓存：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/sync_system_status.py
python3 scripts/check.py
```

`scripts/sync_system_status.py` 只更新 `dash/data/dashboard.json` / `dash/data/dashboard.js` 中的 `automation` 和 `system` 字段，用来展示 nginx、HTTPS、证书到期、腾讯云位置、计费/有效期、git commit、最近拉取、wiki-todos 同步、定时任务、失败日志、CPU、磁盘、内存和 uptime。它不应该覆盖今日状态、当前主线、今日推进或日常记录。

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

2026-06-18 已用 `ubuntu` 用户 crontab 接入 dashboard 数据同步，标记块为 `MAXNOW-DASHBOARD-SYNC`：

```cron
*/10 * * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-dashboard-sync.lock /bin/bash -lc 'set -o pipefail; echo "[$(date -Is)] maxnow dashboard sync start"; python3 scripts/update_data.py runtime; echo "[$(date -Is)] maxnow dashboard sync ok"' >> /var/www/maxnow-dashboard/logs/maxnow-sync.log 2>&1
```

该任务会通过 `runtime` 一并刷新 wiki-todos、北京市海淀区天气、系统状态和项目元信息。

查看当前 crontab：

```bash
crontab -l
```

失败日志目前按以下位置检测：

```text
/var/www/maxnow-dashboard/logs/ai-last30.log
/var/www/maxnow-dashboard/logs/wiki-todos.log
/var/www/maxnow-dashboard/logs/weather.log
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
sudo python3 /root/.openclaw/gen_checkin_data.py
```

日常预期：

- 签到脚本先更新 `/root/.openclaw/dounai_weekly.json`。
- `gen_checkin_data.py` 从 weekly 数据生成最近 60 天的 `dounai_checkin.json`。
- 同一份结果同时写入 `/root/MaxNow/dash/data/dounai_checkin.json` 和 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。
- `gen_checkin_data.py` 还会抓取豆奶用户面板上的剩余流量和有效期，写入 `account` 字段，并维护最近 60 天 `account_history`；如果抓取失败，会尽量保留上一份 `account` 和 `account_history`，并标记 `stale` / `last_error`。
- 线上 `dash.maxnow.cn` 读取 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。

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

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /data/ {
    add_header Cache-Control "no-store";
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
