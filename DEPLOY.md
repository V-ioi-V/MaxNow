# MaxNow 部署说明

推荐部署到：

```text
dash.maxnow.cn
```

主域名 `maxnow.cn` 先保留给未来公开主页或个人发布入口。

## 站点性质

MaxNow v1 是纯静态站点：

- 不需要登录系统。
- 不需要数据库。
- 不需要后端 API。
- 页面读取 `data/*.json`。
- `.js` wrapper 作为静态兜底。

## 服务器目录

推荐目录：

```text
/var/www/maxnow-dashboard
  index.html
  styles.css
  app.js
  data/
    dashboard.json
    dashboard.js
    ai-news.json
    ai-news.js
    last-30.json
    last-30.js
```

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

## OpenClaw 写权限

建议把 OpenClaw 的写权限限制到数据文件。

Dashboard 任务可写：

```text
data/dashboard.json
data/dashboard.js
data/ai-news.json
data/ai-news.js
```

Last-30 任务可写：

```text
data/last-30.json
data/last-30.js
```

OpenClaw 不应修改：

```text
index.html
styles.css
app.js
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
- `data/*.js` wrapper 是否和对应 JSON 一致。
- 如果本地 4173 服务正在运行，页面是否返回 200。

## Caddy 示例

```caddyfile
dash.maxnow.cn {
  root * /var/www/maxnow-dashboard
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
  root /var/www/maxnow-dashboard;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /data/ {
    add_header Cache-Control "no-store";
  }
}
```

## 隐私建议

MaxNow 是私人状态工作站。如果里面包含个人状态、Token 使用、项目进展或其他私密信息，建议至少使用一种访问限制：

- Basic Auth
- 内网 / VPN
- 服务器防火墙限制来源 IP
- 反向代理访问控制
