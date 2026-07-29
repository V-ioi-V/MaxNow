# MaxNow

MaxNow 是部署在 `dash.maxnow.cn` 的私人状态工作站。它不是公开主页、新闻站，也不是通用仪表盘；它负责把 Owner 的今日状态、当前主线、今日推进、近期大事、系统状态和 Token 使用情况放在一个安静、紧凑的页面里。

## 当前结构

```text
index.html
dash/
  index.html
  styles.css
  app.js
  data/
    dashboard.json
    dashboard.js
    project-status.json
    project-status.js
    ai-news.json
    ai-news.js
    last-30.json
    last-30.js
    wiki-todos.json
    wiki-todos.js
    ballet.json
    ballet.js
blog/
  index.html
  overview.html
  topics.html
  topic-algorithm.html
  topic-cs.html
  topic-algorithm-gap.html
  topic-engineering.html
  post-preview.html
  random-articles.js
  topic-tags.js
  styles.css
  preview.html
  preview.css
openclaw/
  maxnow-dashboard/SKILL.md
  last-30/SKILL.md
scripts/
  check.py
  update_data.py
  sync_system_status.py
  sync_wiki_todos.py
  sync_ai_last30.py
  sync_ballet.py
```

`dash/` 是 `dash.maxnow.cn` 的静态站目录。`blog/` 是 `blog.maxnow.cn` 的发布层工作区，当前先放文章流首页、归档总览、专题索引、分类二级页、细分标签索引和方案说明页预览。根目录 `index.html` 只作为本地开发入口，不是线上 dashboard 本体。

## 本地预览

在仓库根目录运行：

```powershell
python -m http.server 4173
```

然后打开：

```text
http://127.0.0.1:4173/
```

Dash 直达：

```text
http://127.0.0.1:4173/dash/
```

个人博客首页预览页：

```text
http://127.0.0.1:4173/blog/
```

个人博客总览页预览：

```text
http://127.0.0.1:4173/blog/overview.html
```

个人博客专题页预览：

```text
http://127.0.0.1:4173/blog/topics.html
```

专题分类二级页示例：

```text
http://127.0.0.1:4173/blog/topic-algorithm.html
```

文章详情页预览：

```text
http://127.0.0.1:4173/blog/post-preview.html
```

博客方案说明页：

```text
http://127.0.0.1:4173/blog/preview.html
```

Home 页面读取：

- `dash/data/dashboard.json`
- `dash/data/project-status.json`
- `dash/data/ai-news.json`
- `dash/data/last-30.json`
- `dash/data/wiki-todos.json`
- `dash/data/market-indices.json`
- `dash/data/ballet.json`
- `dash/data/ballet-session.json`

对应的 `.js` wrapper 是静态兜底，必须和 JSON 保持一致。

## 数据更新工具

统一入口：

```powershell
python scripts/update_data.py wrap all
python scripts/update_data.py ai-last30
python scripts/update_data.py market-indices
python scripts/update_data.py project-status
python scripts/update_data.py ballet --dry-run
python scripts/update_data.py ballet-session --config <restricted-server-config> --dry-run
python scripts/update_data.py runtime
```

- `wrap all`：只从 JSON 重新生成所有 `.js` wrapper，并运行校验。
- `ai-last30`：从免费公开源刷新首页 AI 输入和 Last-30 AI 外部信号滚动记忆。
- `market-indices`：刷新 Home 市场涨幅卡的国内外指数点位、涨跌幅和迷你走势。
- `project-status`：显式从 `ROADMAP.md` 刷新独立的 `project-status.*`，不修改 `dashboard.today`，也不由服务器日常 cron 自动覆盖。ROADMAP Now / Next / Done 变化后必须运行。
- `ballet --dry-run`：只验证芭蕾同步器配置和 GET-only 边界，不读取凭据、不访问闻道、不写数据；生产同步只能按 `SERVER_RUNBOOK.md` 通过隔离的 systemd unit 运行。
- `ballet-session --config ... --dry-run`：开发 / 检查入口，只读服务器本地 Session 实验配置与 JSONL，生成或预览脱敏状态；生产由专用无登录用户通过 root-owned 固定脚本运行，输出到 `/var/lib/maxnow-ballet-session-status/public`，再经已有登录校验的 nginx alias 提供。它没有网络能力，不会请求闻道，也不会输出 Cookie、指纹或内部路径。
- `runtime`：服务器定时任务使用，刷新 wiki-todos、天气、行情、生活 / 同行记缓存、系统状态和项目元信息，然后运行校验。

## 本地校验

运行：

```powershell
python scripts/check.py
```

校验内容：

- 必要文件是否存在。
- `dashboard` / `ai-news` / `last-30` / `wiki-todos` 的 JSON 是否能解析。
- 每个 `.js` wrapper 是否和对应 JSON 内容一致。
- 如果本地服务正在运行，检查 `http://127.0.0.1:4173/` 是否可访问。

## 数据分工

`dash/data/dashboard.json`：

- 今日状态
- 人工今日状态
- 日常记录
- 时间点
- 系统状态
- Token 使用

`dash/data/project-status.json`：

- 从 `ROADMAP.md` 生成的当前主线和待推进事项
- ROADMAP 来源更新时间、生成时间、过期阈值和内容指纹
- 只允许 Now / Next，不能引用 Done

`dash/data/ai-news.json`：

- 外部 AI / 工具输入
- 最多在首页展示 3 条
- 只保留和 Owner、项目、工具、模型或成本有关的信号

`dash/data/last-30.json`：

- 今日 AI 信号
- 本周 AI 变化
- 近 30 天 AI 主线
- 可能影响 MaxNow、Codex、OpenClaw、模型选择或 token 成本的信号
- 等待观察 / 待 Owner 确认判断

`dash/data/ballet.json`：

- 脱敏的实际上课记录、当前预约 / 候补、取消截止、本周训练摘要、每张课程卡独立的开卡进度 / 余次 / 有效期、计划情景与样本充足后的实际节奏预测、累计 / 月度 / 年度聚合和同步状态
- 不保存 PHPSESSID、Cookie、OAuth 数据、会员标识、源记录 ID 或原始响应
- 私有 canonical ledger 只保存在服务器 `/var/lib/maxnow-ballet`

`dash/data/ballet-session.json`：

- 保存 PHPSESSID 持续活动实验的脱敏状态、已确认有效时长、起始 / 最近 / 下次检查、25 分钟间隔和安全错误
- 与课程缓存分文件维护，不会因为状态卡更新而改写课程数据时间
- 不保存 Session 值或指纹、run ID、unit / 日志路径、URL、响应摘要 / 正文或凭据版本

`scripts/sync_ai_last30.py` 使用免费公开源做本地抓取、关键词打分、去重和短摘要，采集本身不调用模型、不消耗 token。X / Twitter 暂不作为基础来源。

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
- `BALLET_GROWTH_SCORING.md`：芭蕾成长进度卡的独立计算标准。
- `IDEAS.md`：尚未确定的想法。
- `UPDATE_LOG.md`：重要更新记录。
- `DEPLOY.md`：部署说明。
