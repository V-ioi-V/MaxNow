# MaxNow

MaxNow 是部署在 `dash.maxnow.cn` 的私人状态工作站。它不是公开主页、新闻站，也不是通用仪表盘；它负责把 Owner 的今日状态、当前主线、今日推进、近期大事、系统状态和 Token 使用情况放在一个安静、紧凑的页面里。

## 当前结构

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

## 本地预览

在仓库根目录运行：

```powershell
python -m http.server 4173
```

然后打开：

```text
http://127.0.0.1:4173/
```

Home 页面读取：

- `data/dashboard.json`
- `data/ai-news.json`
- `data/last-30.json`

对应的 `.js` wrapper 是静态兜底，必须和 JSON 保持一致。

## 本地校验

运行：

```powershell
python scripts/check.py
```

校验内容：

- 必要文件是否存在。
- `dashboard` / `ai-news` / `last-30` 的 JSON 是否能解析。
- 每个 `.js` wrapper 是否和对应 JSON 内容一致。
- 如果本地服务正在运行，检查 `http://127.0.0.1:4173/` 是否可访问。

## 数据分工

`data/dashboard.json`：

- 今日状态
- 当前主线
- 今日推进
- 日常记录
- 时间点
- 系统状态
- Token 使用

`data/ai-news.json`：

- 外部 AI / 工具输入
- 最多在首页展示 3 条
- 只保留和 Owner、项目、工具、模型或成本有关的信号

`data/last-30.json`：

- 今日大事
- 本周大事
- 近 30 天主线
- 重要决定
- 等待项 / 待 Owner 确认判断

## OpenClaw 分工

OpenClaw 日常任务只维护数据文件，不维护页面代码和文档。

- `openclaw/maxnow-dashboard/SKILL.md`：维护 `dashboard.*` 和 `ai-news.*`。
- `openclaw/last-30/SKILL.md`：维护 `last-30.*`。

如果页面结构、产品方向或上下文规则需要变化，由 Codex 或 Owner 在功能分支里修改。

## 分支规则

不要直接在 `main` 上开发。

- 新功能：`feature/<short-demand-name>`
- 修复：`bugfix/<short-bug-name>`

改完检查后再合回 `main`。有风险的改动先让 Owner 确认。

## 相关文档

- `AGENTS.md`：代理执行规则。
- `CONTEXT.md`：给 Codex / 代理接力用的项目上下文。
- `ROADMAP.md`：当前待做、下一步、长期方向和阻塞项。
- `SPEC.md`：已确定的产品规格。
- `IDEAS.md`：尚未确定的想法。
- `UPDATE_LOG.md`：重要更新记录。
- `DEPLOY.md`：部署说明。
