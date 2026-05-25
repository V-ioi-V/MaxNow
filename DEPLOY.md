# MaxNow Dashboard Deploy

建议把这个站点部署到 `dash.maxnow.cn` 或 `now.maxnow.cn`，主域名 `maxnow.cn` 先保留给公开主页。

## 目录结构

```text
index.html
styles.css
app.js
data/dashboard.json
```

页面是纯静态站点，`data/dashboard.json` 是 OpenClaw 后续维护的数据入口。

## OpenClaw 维护方式

让 OpenClaw 定时生成完整 JSON 并覆盖：

```text
data/dashboard.json
```

推荐只给 OpenClaw 这个数据目录的写权限，不让它直接修改页面代码。

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

如果看板包含私密信息，建议给子域名加 Basic Auth 或只通过内网/VPN 访问。
