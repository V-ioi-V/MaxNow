# MaxNow 产品规格

MaxNow 是部署在 `dash.maxnow.cn` 的私人状态工作站。它不是公开主页、新闻站，也不是通用仪表盘。它的核心任务是让 Owner 快速看见：自己现在处于什么状态、正在推进什么、自动化系统在做什么，以及 AI / 工具使用是否正常。

## 产品定位

- 使用者：Owner 本人。
- 主要使用方式：每天打开几次，用几秒钟理解当前个人和系统状态。
- 核心价值：保存持续的个人上下文，而不是制造一次性提醒。
- 气质：平静、紧凑、偏操作型、可维护。
- 首屏优先级：个人状态、当前主线、今日推进、时间点、系统状态，以及少量外部输入。

## 系统组成

MaxNow 由四类文件组成：

1. 页面代码
   - `index.html`
   - `styles.css`
   - `app.js`
   - 由 Codex 或 Owner 维护。
   - 负责页面结构、样式、渲染和交互。

2. 数据文件
   - `data/dashboard.json`
   - `data/dashboard.js`
   - `data/ai-news.json`
   - `data/ai-news.js`
   - `data/last-30.json`
   - `data/last-30.js`
   - `data/wiki-todos.json`
   - `data/wiki-todos.js`
   - 这是页面和自动化之间的数据契约。

3. OpenClaw skill
   - `openclaw/maxnow-dashboard/SKILL.md`
   - `openclaw/last-30/SKILL.md`
   - 告诉 OpenClaw：MaxNow 是什么、可以更新哪些数据文件、哪些文件不能碰、如何校验输出。

4. 校验脚本
   - `scripts/check.py`
   - 由 Codex 或 Owner 维护。
   - 用来检查必要文件、JSON 合法性、wrapper 一致性和本地预览可访问性。

5. 同步脚本
   - `scripts/sync_wiki_todos.py`
   - `scripts/sync_system_status.py`
   - 由 Codex 或 Owner 维护。
   - `scripts/sync_wiki_todos.py` 使用本地或服务器的 `gh` 登录态读取 private personal-wiki，并生成 MaxNow 可静态读取的 `data/wiki-todos.*`。
   - `scripts/sync_system_status.py` 采集机器可判断的系统状态，只更新 `data/dashboard.*` 中的 `automation` 和 `system` 字段。

6. 产品记忆文档
   - `CONTEXT.md`
   - `ROADMAP.md`
   - `IDEAS.md`
   - `UPDATE_LOG.md`
   - 由 Codex 或 Owner 维护。
   - 用来跨会话保存上下文地图、路线图、未来想法和项目更新记录。

## 导航

v1 只保留两个一级入口：

1. Home
   - 私人状态工作站。
   - 默认页面。
2. Token
   - Token 使用详情页。

不要随便新增页面。只有当某个问题无法放进 Home，且会明显伤害日常扫读体验时，才考虑新增页面。

## Home 页面

Home 按顺序回答这些问题：

1. 我今天处在什么状态？
2. 我当前最重要的主线是什么？
3. 今天应该推进什么？
4. 今天有哪些重要时间点？
5. OpenClaw、服务器、数据同步和 Token 使用是否正常？
6. 有哪些外部输入值得稍后注意？

必备模块：

- 今日状态：模式、精力、焦点、一句话判断、更新时间。
- 当前主线：1-3 条重要线索，包含状态、下一步和必要时的卡点。
- 今日推进：1-3 个今天应该移动的动作；这里不是完整 todo app。
- 日常记录：保存个人上下文和关键决定的短记录。
- 时间点：日程、截止时间、自动化运行时间。
- 系统状态：OpenClaw 最近运行、服务器状态、数据同步状态、GitHub / 部署状态。
- 外部输入：链接、信号和 AI 每日精选，但必须保持次要。
- personal-wiki 近期待办入口：Home 主内容区的紧凑只读模块，用于查看近期未完成待办和跳转到 personal-wiki；v1 不支持编辑或标记完成。

## AI 每日精选

AI 每日精选属于外部输入的一小块，不是新闻产品。

- 默认更新时间：服务器本地时间 00:10。
- Home 最多显示 3 条。
- 优先官方来源和高信号开发者 / 社区来源。
- X / Twitter 可以用于早期信号，但不是硬依赖。
- 如果 X / Twitter 不可用，使用官方博客 / RSS、Hacker News、GitHub、Reddit、项目 release、研究机构等来源。
- 二级新闻站只作为补充验证。

每条内容都要说明它为什么和 Owner、当前项目、工具、模型选择或成本有关。

## Token 页面

Token 页面只回答 Token 相关问题：

- 最近 1 小时使用量
- 最近 24 小时使用量
- 最近 7 天使用量
- 最近 30 天使用量
- input / output / total / cost
- 模型占比
- 最近 7 天趋势
- 可用时显示异常峰值

不要把完整 Token 页面复制到 Home。Home 只需要显示紧凑的使用状态。

## 数据契约

OpenClaw 日常维护只能更新这些文件：

```text
data/dashboard.json
data/dashboard.js
data/ai-news.json
data/ai-news.js
data/last-30.json
data/last-30.js
data/wiki-todos.json
data/wiki-todos.js
```

OpenClaw 日常维护不能更新这些文件：

```text
index.html
styles.css
app.js
SPEC.md
README.md
DEPLOY.md
scripts/check.py
CONTEXT.md
ROADMAP.md
IDEAS.md
UPDATE_LOG.md
```

`data/dashboard.json` 负责个人状态、主线、行动、日常记录、时间线、系统状态和 Token 使用。

其中 `automation` 和 `system` 可以由 `scripts/sync_system_status.py` 自动更新；`today`、`mainlines`、`actions` 和 `journal` 仍保留 Owner 判断或受控草稿，不由系统状态脚本覆盖。

`data/ai-news.json` 只负责外部 AI 输入。

`data/last-30.json` 负责今日大事、本周大事、近 30 天主线、重要决定和等待项。

`data/wiki-todos.json` 负责 personal-wiki 近期待办的只读缓存，由 `scripts/sync_wiki_todos.py` 从 personal-wiki `wiki/tasks/todo.json` 生成。

每个 `.js` wrapper 必须从对应 JSON 文件生成，并把同一个对象暴露给浏览器：

```text
window.MAXNOW_DASHBOARD_DATA
window.MAXNOW_AI_NEWS_DATA
window.MAXNOW_LAST30_DATA
window.MAXNOW_WIKI_TODO_DATA
```

## 数据来源策略

看板不应该依赖每天大量手动录入。理想分工是：

- 自动：Token 使用、GitHub 活动、服务器状态、OpenClaw 运行状态、AI 外部输入、时间戳。
- 半自动：当前主线、日常记录草稿、项目进展摘要。
- 手动：今日一句话判断、精力 / 状态、真正优先级、重要决定。

OpenClaw 记录事实并起草摘要。最终判断由 Owner 保留。

## personal-wiki 待办入口

Home 可以显示一个紧凑的 personal-wiki 近期待办入口。

边界：

- 入口放在 Home 主内容区，位于“当前主线”和“今日推进”之间，不进入一级导航。
- 只读展示近期未完成待办，最多展示少量条目。
- 每条可跳转到 personal-wiki 源文件或关联页面。
- 不在 MaxNow 中编辑、完成或回写待办。
- 数据来源是 `data/wiki-todos.json`，该文件由 `scripts/sync_wiki_todos.py` 从 personal-wiki 的 `wiki/tasks/todo.json` 生成。

刷新策略：

- 页面加载时读取本地缓存一次。
- 顶部刷新按钮可以重新读取本地缓存。
- 不做前端自动轮询，也不从前端直接访问 private GitHub raw。
- 需要更新内容时，在本地或服务器运行 `python scripts/sync_wiki_todos.py`，由 `gh api` 读取 personal-wiki 并重写 `data/wiki-todos.*`。
- GitHub token 不得进入前端页面代码。

## 产品记忆

`CONTEXT.md` 用来说明项目上下文如何分层、哪些文件保存什么、谁负责更新、下一步缺口是什么。

`ROADMAP.md` 用来记录当前待做、下一步、长期方向、阻塞项和已完成的阶段成果。

`IDEAS.md` 用来记录不能丢的产品想法，包括未来入口、暂时搁置的概念、Owner 原始想法和待研究问题。

`UPDATE_LOG.md` 用来记录重要项目更新，尤其是产品方向、页面行为、数据结构、文件边界、部署方式或自动化规则的变化。

当一个新想法变成确定的产品行为时，再把它同步进本规格。在此之前，它只是已记录的想法，不是当前版本范围。

## 未来方向：Last-30 滚动记忆

MaxNow 需要一层滚动记忆，用来保存今天、本周和最近 30 天的关键上下文。

已新增：

```text
data/last-30.json
data/last-30.js
openclaw/last-30/SKILL.md
```

Last-30 负责：

- 今日大事：今天发生或推进的 1-5 件重要事情。
- 本周大事：本周完成、变化、卡点和重要进展。
- 近 30 天主线：连续出现的项目、方向和长期关注点。
- 重要决定：已经发生的选择、边界或承诺。
- 等待项：卡点、外部依赖、需要 Owner 确认的判断。

更新原则：

- 不要每天从零总结 30 天，避免成本高和上下文漂移。
- 使用“昨天已有滚动摘要 + 今天新增事实”的增量更新方式。
- 每条记录尽量保存 `source`、`confidence` 和 `needsOwnerConfirm`。
- 自动化可以起草事实和摘要，但重要判断最终由 Owner 确认。

## 未来方向：桌面伴随面板

MaxNow 未来可以在浏览器看板之外，增加桌面伴随入口。

macOS 方向：

- 做一个顶部状态栏 app。
- 点击图标后打开紧凑的下拉个人面板。
- 面板显示今日状态、当前主线、今日推进、关键时间点和简洁系统状态。

Windows 方向：

- 做一个桌面壁纸式个人看板。
- 它像一个平静、常驻的桌面状态层。
- 显示同一套核心个人状态信息，但适配扫一眼就能懂的使用方式。

共同约束：

- `dash.maxnow.cn` 仍然是 v1 标准入口。
- 桌面入口尽量复用同一套数据契约。
- 个人状态始终优先，外部 AI 输入保持次要。
- 不要把桌面伴随面板变成完整 todo app、新闻墙或社交产品。

## 视觉规则

- 深色、紧凑、偏操作型界面。
- 不做营销 hero，不做装饰性仪表盘填充物。
- 卡片只用于真实信息模块。
- 圆角保持在 8px 或以下。
- 外部输入在视觉上必须弱于个人状态。
- 首屏优先展示状态、主线和今日推进。

## 实现边界

- v1 只保留 Home 和 Token。
- v1 保持静态站点：不加登录、数据库或后端 API。
- 任何新的日常维护数据字段，都必须同时写进这里和 OpenClaw skill。
- 页面代码变化需要 Codex 或 Owner 明确意图；OpenClaw 永远不能改变页面结构。
