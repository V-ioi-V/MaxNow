# MaxNow

MaxNow 是部署在 `dash.maxnow.cn` 的私人状态工作站。它不是公开主页、新闻站或通用仪表盘；它只服务一个目标：让 Owner 用几秒钟看见今天的个人状态、当前主线、近期上下文、系统运行和 Token 使用情况。

v1 是纯静态站点：没有登录系统、数据库或后端 API。页面代码读取 `data/*.json`，对应的 `data/*.js` wrapper 作为浏览器静态兜底。

## 快速开始

在仓库根目录启动本地预览：

```bash
python -m http.server 4173
```

打开：

```text
http://127.0.0.1:4173/
```

运行一致性校验：

```bash
python scripts/check.py
```

校验会检查必要文件、JSON 解析、JSON 与 `.js` wrapper 是否一致；如果本地 4173 服务正在运行，也会检查页面是否可访问。

## 项目结构

```text
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
openclaw/
  maxnow-dashboard/SKILL.md
  last-30/SKILL.md
scripts/
  check.py
```

页面代码由 Codex 或 Owner 维护。OpenClaw 日常任务只维护允许的数据文件，不修改页面代码和产品文档。

## 数据边界

`data/dashboard.json` 负责首页的个人状态、当前主线、今日推进、日常记录、时间点、系统状态和 Token 使用概览。

`data/ai-news.json` 只负责外部 AI / 工具输入。首页最多展示 3 条，且必须和 Owner、当前项目、工具、模型选择或成本有关。

`data/last-30.json` 负责今日大事、本周大事、近 30 天主线、重要决定和等待项。

每次修改 JSON 后，都要重新生成对应的 `.js` wrapper，并运行：

```bash
python scripts/check.py
```

## 维护规则

不要直接在 `main` 上开发。新功能使用短期分支，修复使用短期修复分支；检查通过后再合回 `main`，有风险的改动先让 Owner 确认。

数据更新和产品规划分开维护：

- 日常展示数据写入 `data/*.json`。
- MaxNow 要做什么、接下来做什么，写入 `ROADMAP.md`。
- 尚未确定的想法写入 `IDEAS.md`。
- 已确定的产品规则写入 `SPEC.md`。
- 重要变更写入 `UPDATE_LOG.md`。

## 文档入口

- `SPEC.md`：产品定位、页面边界、数据契约和已确定规则。
- `CONTEXT.md`：给 Codex / 代理接力使用的上下文地图。
- `ROADMAP.md`：当前可执行路线、下一步、阻塞项和已完成内容。
- `IDEAS.md`：尚未确定但不能丢的产品想法。
- `UPDATE_LOG.md`：重要产品、结构、部署和规则变更。
- `DEPLOY.md`：部署流程和静态站点配置建议。
- `SERVER_RUNBOOK.md`：服务器 SSH、nginx、证书和排障操作。
- `AGENTS.md`：本仓库代理执行规则。

## 部署状态

当前目标域名是：

```text
https://dash.maxnow.cn
```

服务器路径、nginx 配置、HTTPS 证书和更新命令以 `SERVER_RUNBOOK.md` 为准。部署说明以 `DEPLOY.md` 为入口。
