# MaxNow Dashboard

一个部署在子域名上的个人看板。页面本身是纯静态文件，日常变化的数据由 OpenClaw 写入 `data/dashboard.json`。

## 本地预览

```powershell
python -m http.server 4173
```

打开：

```text
http://127.0.0.1:4173
```

## 自动化思路

代码和数据分开维护：

```text
GitHub 仓库
  index.html
  styles.css
  app.js
  DEPLOY.md
  data/dashboard.json

服务器
  /var/www/maxnow-dashboard
    页面文件
    data/dashboard.json
```

推荐流程：

1. 你在本地修改页面代码。
2. 用 Git 推到 GitHub。
3. 服务器从 GitHub 拉取最新代码。
4. OpenClaw 每天整理任务、信息流、项目和系统状态。
5. OpenClaw 覆盖服务器上的 `data/dashboard.json`。
6. 访问 `dash.maxnow.cn` 时，页面自动读取最新 JSON。

## OpenClaw 数据入口

OpenClaw 只需要更新这个文件：

```text
data/dashboard.json
```

建议在服务器上限制 OpenClaw 的写权限，只允许它写入 `data/` 目录，而不是整个站点目录。

## 推荐子域名

```text
dash.maxnow.cn
```

主域名 `maxnow.cn` 可以先保留给未来公开主页。
