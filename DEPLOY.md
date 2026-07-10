# MaxNow 部署说明

推荐部署到：

```text
dash.maxnow.cn
```

主域名 `maxnow.cn` 先保留给未来公开主页或个人入口。

公开博客推荐单独部署到：

```text
blog.maxnow.cn
```

`blog.maxnow.cn` 用于发布从 personal-wiki `raw/blog-vioiv` 筛选和转换出来的公开文章；不要把完整博客挂在 `dash.maxnow.cn/blog`。

## 站点性质

MaxNow v1 的业务内容是静态站点：

- 不需要数据库。
- 不需要业务 API。
- 页面读取 `dash/data/*.json`。
- `.js` wrapper 继续由脚本生成并校验，但 Dash 首屏不再预加载这些 wrapper；前端优先按需读取 JSON。
- 私人访问使用单独的最小认证服务：只校验现有 htpasswd 密码并签发 HttpOnly Cookie，不读取业务数据。

公开博客第一阶段也保持纯静态站：

- 不需要登录系统。
- 不需要数据库。
- 不需要后端 API。
- 构建时从受控的发布清单读取文章，不从公开前端直接读取 private personal-wiki。

## 服务器目录

推荐目录：

```text
/var/www/maxnow-dashboard
  dash/index.html
  dash/login.html
  dash/login.js
  dash/styles.css
  dash/app.js
  dash/data/
    dashboard.json
    dashboard.js
    market-indices.json
    market-indices.js
    ai-news.json
    ai-news.js
    last-30.json
    last-30.js
  scripts/maxnow_auth_service.py
  server/maxnow-auth.service
  server/maxnow-auth-rate-limit.conf
  server/maxnow-auth-locations.conf
  server/maxnow-dashboard.conf
```

公开博客当前预览页随同 MaxNow 仓库部署，nginx 指向同仓库下的 `blog/`：

```text
/var/www/maxnow-dashboard/blog
  index.html
  topics.html
  preview.html
  styles.css
  preview.css
```

等公开博客形成独立构建、独立发布节奏和完整文章生成链路后，再考虑迁出到 `/var/www/maxnow-blog` 或独立仓库。

当前服务器操作细节、SSH 命令、nginx 配置和排障步骤见：

```text
SERVER_RUNBOOK.md
```

## 更新流程

推荐流程：

1. Codex 或 Owner 在本地功能分支修改页面、文档或 skill。
2. 检查通过后合并到 `main`。
3. 推送 GitHub。
4. 服务器从 GitHub 拉取最新 `main`。
5. OpenClaw 定时更新允许的数据文件。
6. 每次数据更新后重新生成对应 `.js` wrapper。
7. 运行校验，确认 JSON 和 wrapper 一致。

## 服务器数据同步

`dash.maxnow.cn` 的 personal-wiki 待办缓存由服务器定时任务更新，不由浏览器直接读取 private GitHub。

当前线上配置：

- 运行用户：`ubuntu`
- 触发方式：用户 crontab，标记块 `MAXNOW-DASHBOARD-SYNC`
- 频率：每 10 分钟一次
- 工作目录：`/var/www/maxnow-dashboard`
- 执行内容：`python3 scripts/update_data.py runtime`
- 刷新范围：wiki-todos、Ricky 旅行记录、生活页吃啥候选、北京市海淀区天气、市场指数、系统状态和项目元信息
- 锁：`/tmp/maxnow-dashboard-sync.lock`，避免上一次未结束时重叠执行
- 日志：`/var/www/maxnow-dashboard/logs/maxnow-sync.log`，并分别追加 `logs/wiki-todos.log`、`logs/system-status.log`

手动重跑：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py runtime
```

ROADMAP Now / Next / Done 变化后，需要显式刷新独立的 Home 项目状态数据；该命令不修改 `dashboard.today`：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py project-status
```

需要刷新免费 AI 外部信号和 Last-30 时：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py ai-last30
```

`ai-last30` 使用免费公开源，采集脚本本身不调用模型、不消耗 token。若后续交给 OpenClaw 二次摘要，应只传入少量候选，避免把新闻全文大量喂给模型。

需要在 Owner Windows 本机定期上报 Codex Token 用量时：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_local_codex_usage_task.ps1
```

该计划任务固定在每小时 `:02` 静默刷新本机 `dash/data/codex-usage.*`，注册为 hidden task，并通过 `wscript.exe scripts/report_codex_usage_hidden.vbs` 无窗口启动 PowerShell。它只提交这两个源账本文件并推送到 `origin/main`，最长运行 10 分钟。

需要在 Owner macOS 本机定期上报 Codex Token 用量时：

```bash
bash scripts/install_local_codex_usage_launchd.sh
```

该 launchd 任务固定在每小时 `:00` 运行 `scripts/report_codex_usage.sh`，刷新本机 `dash/data/codex-macos-usage.*`，只提交这两个源账本文件并推送到 `origin/main`。建议在专用 main clone 中安装；日志写入 `~/Library/Logs/MaxNow/local-codex-usage-report.log`。服务器源采集固定在 `:05`，统一总账固定在 `:10` 发布。

## OpenClaw 写权限

建议把 OpenClaw 的写权限限制到数据文件。

Dashboard 任务可写：

```text
dash/data/dashboard.json
dash/data/dashboard.js
dash/data/ai-news.json
dash/data/ai-news.js
```

Last-30 任务可写：

```text
dash/data/last-30.json
dash/data/last-30.js
```

OpenClaw 不应修改：

```text
dash/index.html
dash/styles.css
dash/app.js
AGENTS.md
CONTEXT.md
SPEC.md
IDEAS.md
UPDATE_LOG.md
README.md
DEPLOY.md
openclaw/*/SKILL.md
```

## 本地校验命令

在仓库根目录运行：

```powershell
python scripts/check.py
```

服务器上也可以使用同一个脚本。它会检查：

- 必要文件是否存在。
- JSON 是否可解析。
- `dash/data/*.js` wrapper 是否和对应 JSON 一致。
- 如果本地 4173 服务正在运行，页面是否返回 200。

## Caddy 示例

```caddyfile
dash.maxnow.cn {
  root * /var/www/maxnow-dashboard/dash
  file_server

  header {
    X-Content-Type-Options nosniff
    Referrer-Policy no-referrer-when-downgrade
  }
}
```

## Nginx 示例

```nginx
server {
  listen 80;
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
}
```

博客子域名示例：

```nginx
server {
  listen 80;
  server_name blog.maxnow.cn;
  root /var/www/maxnow-dashboard/blog;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

## 隐私建议

MaxNow 是私人状态工作站。线上 `dash.maxnow.cn` 使用自定义登录页，nginx 通过 `auth_request` 保护首页、静态资源和 `/data/`；`blog.maxnow.cn` 保持公开。认证服务只监听 `127.0.0.1:8765`，复用 `/etc/nginx/.htpasswd-maxnow` 校验密码，并使用 `/etc/maxnow-auth/session.key` 签发 7 天 HttpOnly 会话 Cookie。

凭据文件放在服务器 `/etc/nginx/.htpasswd-maxnow`，权限应为 `root:www-data 0640`。真实用户名、密码和密码哈希不得写入仓库。轮换密码时在服务器交互输入，避免明文进入 shell history：

```bash
read -rsp "New MaxNow password: " password && echo
hash=$(printf %s "$password" | openssl passwd -6 -stdin)
unset password
echo "<username>:$hash" | sudo tee /etc/nginx/.htpasswd-maxnow >/dev/null
unset hash
sudo chown root:www-data /etc/nginx/.htpasswd-maxnow
sudo chmod 640 /etc/nginx/.htpasswd-maxnow
sudo nginx -t && sudo systemctl reload nginx
```

验证时不要把密码放进命令历史；使用浏览器登录，或通过 Cookie jar 做完整表单验证：

```bash
curl -I https://dash.maxnow.cn/                       # 302 -> /login
curl -I https://dash.maxnow.cn/login                  # 200
curl -I https://dash.maxnow.cn/data/dashboard.json    # 401
curl -I https://blog.maxnow.cn/                       # 200
```

预期结果：首页未认证跳转登录页，登录页返回 200，`/data/` 未认证返回 401，登录后 Dash 返回 200，Blog 返回 200。紧急恢复时可以先从备份恢复 nginx 配置，执行 `sudo nginx -t` 后再 reload；不要删除凭据文件、会话密钥或放宽 `/data/` 作为临时绕过。

安全响应头由 `/etc/nginx/snippets/maxnow-security-headers.conf` 统一维护。Dash 当前包含 CSP、`X-Content-Type-Options`、`Referrer-Policy`、`X-Frame-Options`、`Permissions-Policy` 和 HSTS；新增外部脚本、样式或图片源时，需要同步评估 CSP 白名单。

其他可选访问限制仍包括：

- MaxNow 自定义 Cookie 认证
- 内网 / VPN
- 服务器防火墙限制来源 IP
- 反向代理访问控制
