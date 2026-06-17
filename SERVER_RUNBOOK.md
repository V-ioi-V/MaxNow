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

证书到期由脚本直接检查 `https://dash.maxnow.cn` 的 TLS 证书。最近拉取时间来自 `.git/FETCH_HEAD` 的修改时间。定时任务目前按以下 unit 名称检测：

```text
maxnow-wiki-todos.timer
maxnow-system-status.timer
maxnow-dashboard-sync.timer
```

失败日志目前按以下位置检测：

```text
/var/www/maxnow-dashboard/logs/wiki-todos.log
/var/www/maxnow-dashboard/logs/system-status.log
/var/www/maxnow-dashboard/maxnow-sync.log
```

如果只想预览将采集到的状态，不写文件：

```bash
python3 scripts/sync_system_status.py --dry-run
```

注意：运行同步脚本会改写 `dash/data/wiki-todos.*` 或 `dash/data/dashboard.*`。如果只是验证能力而不想保留工作区改动，可以执行：

```bash
git checkout -- dash/data/wiki-todos.json dash/data/wiki-todos.js dash/data/dashboard.json dash/data/dashboard.js
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
- 给 `scripts/sync_wiki_todos.py` 和 `scripts/sync_system_status.py` 配置 cron 或 systemd timer，并记录日志路径和失败提醒方式。
- 做数据更新工具和服务器定时任务，让 `dash/data/*.json` 与 `.js` wrapper 自动保持一致。
