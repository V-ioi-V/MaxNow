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

MaxNow v1 是纯静态站点：

- 不需要登录系统。
- 不需要数据库。
- 不需要后端 API。
- 页面读取 `dash/data/*.json`。
- `.js` wrapper 作为静态兜底。

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
  dash/styles.css
  dash/app.js
  dash/data/
    dashboard.json
    dashboard.js
    ai-news.json
    ai-news.js
    last-30.json
    last-30.js
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

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /data/ {
    add_header Cache-Control "no-store";
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

MaxNow 是私人状态工作站。如果里面包含个人状态、Token 使用、项目进展或其他私密信息，建议至少使用一种访问限制：

- Basic Auth
- 内网 / VPN
- 服务器防火墙限制来源 IP
- 反向代理访问控制
