# MaxNow 上下文总览

这个文件主要给 Codex / 代理接力使用，用来快速恢复 MaxNow 的项目上下文；Owner 也可以阅读，但它不是汇报文档。

它回答一个问题：MaxNow 的上下文分别放在哪里、谁来维护、什么时候更新。

## 当前目标

MaxNow 要成为一个私人状态工作站，而不是新闻站或通用仪表盘。

它应该帮助 Owner 每天快速看见：

- 我今天处在什么状态。
- 我当前正在推进哪些主线。
- 今天和本周发生了什么重要事情。
- 最近 30 天有哪些持续主线、决定和卡点。
- OpenClaw、服务器、数据同步和 Token 使用是否正常。
- 有哪些外部 AI / 工具信号值得稍后注意。

## 上下文分层

### 1. 产品长期上下文

这些文件保存“MaxNow 是什么”和“为什么这样做”，其中 `CONTEXT.md` 主要服务于代理接力。

- `SPEC.md`：已经确定的产品定义、页面边界、数据契约和实现约束。
- `IDEAS.md`：尚未确定的想法、未来入口、待研究问题。
- `UPDATE_LOG.md`：重要产品方向、规则、结构变化的更新记录。
- `CONTEXT.md`：上下文地图，也就是当前这个文件。

维护方式：

- `CONTEXT.md` 主要面向 Codex / 代理接力，使用中文以便 Owner 随时检查。
- `SPEC.md`、`IDEAS.md`、`UPDATE_LOG.md` 主要面向 Owner 和 Codex 共同阅读。
- Codex 或 Owner 可以更新。
- OpenClaw 日常任务不能修改这些文件。

### 2. 代理执行上下文

这些文件告诉 Codex / OpenClaw 怎么工作。

- `AGENTS.md`：本仓库的通用代理规则。
- `openclaw/maxnow-dashboard/SKILL.md`：OpenClaw 更新 dashboard / ai-news 数据时的执行规则。

维护方式：

- 面向代理执行，可以使用英文。
- 规则要短、明确、可执行。
- 当产品边界变化时，要同步更新这些文件。

### 3. 每日状态上下文

这些文件驱动当前网页。

- `data/dashboard.json`：个人状态、主线、今日推进、日常记录、时间点、系统状态、Token 使用。
- `data/dashboard.js`：从 `dashboard.json` 生成的浏览器 wrapper。
- `data/ai-news.json`：外部 AI 输入。
- `data/ai-news.js`：从 `ai-news.json` 生成的浏览器 wrapper。

维护方式：

- OpenClaw 日常任务可以更新。
- 每次更新后必须校验 JSON，并重新生成对应 `.js` wrapper。
- 这里保存“今天要看的状态”，不要塞长期产品讨论。

### 4. 滚动记忆上下文

这是下一阶段要补齐的上下文层，暂未实现。

建议新增：

- `data/last-30.json`
- `data/last-30.js`
- `openclaw/last-30/SKILL.md`

它负责保存：

- 今日大事。
- 本周大事。
- 近 30 天主线。
- 重要决定。
- 卡点 / 等待项。
- 需要 Owner 确认的判断。

维护方式：

- 不要每天从零总结 30 天。
- 用“昨天已有滚动摘要 + 今天新增事实”做增量更新。
- 每条记录尽量带来源、置信度、是否需要 Owner 确认。

## 上下文更新规则

- 确定的产品行为写进 `SPEC.md`。
- 未确定的产品想法写进 `IDEAS.md`。
- 重要变更写进 `UPDATE_LOG.md`。
- 会影响代理接力、文件职责、自动化边界或下一步路线的上下文写进 `CONTEXT.md`。
- 每天变化的数据写进 `data/*.json`。
- 自动化执行边界写进 `AGENTS.md` 和对应 OpenClaw skill。
- 给 Owner 看的内容用中文；给代理执行的规则可以用英文。

## 当前缺口

- `last-30` 滚动记忆还没有正式数据文件和 skill。
- Home 页面还没有独立展示“今日 / 本周 / 近 30 天大事”的模块。
- 自动更新链路还没有落地：需要决定由 OpenClaw cron、普通脚本 cron，还是其他执行器每天运行。
- `data/dashboard.json` 里的信息仍是旧快照，更新时间停留在 2026-05-26。
- README / DEPLOY 文档仍需要中文化和重新整理。

## 建议下一步

1. 先定义 `last-30` 数据契约。
2. 再写 `openclaw/last-30/SKILL.md`。
3. 然后让 Home 页面读取并展示滚动记忆摘要。
4. 最后接服务器定时任务，让它每天自动更新。
