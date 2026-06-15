# MaxNow 服务器操作说明

这个文件记录 MaxNow 服务器的 SSH 连接方式、前端静态站部署方式和常用排障命令。

## 服务器

```text
Host: 43.160.240.244
User: ubuntu
Domain: dash.maxnow.cn
Site root: /var/www/maxnow-dashboard
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

2026-06-16 已完成首次静态站部署：

```text
/var/www/maxnow-dashboard
```

该目录来自 GitHub 仓库：

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
http://dash.maxnow.cn
```

当前还没有配置 HTTPS。后续需要补充证书和 HTTPS 跳转。

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
  listen 80;
  server_name dash.maxnow.cn;

  root /var/www/maxnow-dashboard;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /data/ {
    add_header Cache-Control "no-store";
  }
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
```

本地 Windows 检查域名：

```powershell
Invoke-WebRequest -Uri "http://dash.maxnow.cn" -UseBasicParsing
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
- nginx 配置没有指向 `/var/www/maxnow-dashboard`。
- 域名已解析，但站点配置未启用。

检查：

```bash
sudo nginx -t
sudo systemctl status nginx --no-pager
ls -la /etc/nginx/sites-enabled
ls -la /var/www/maxnow-dashboard
```

## 后续待补

- 配置 HTTPS 证书。
- 决定是否加 Basic Auth、VPN、IP 限制或其他访问保护。
- 做数据更新工具和服务器定时任务，让 `data/*.json` 与 `.js` wrapper 自动保持一致。
