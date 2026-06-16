# MaxNow 路线图

这个文件记录 MaxNow 接下来真正要推进的事情。

它不是灵感池，也不是更新历史：

- 新想法先放进 `IDEAS.md`。
- 已确定的产品规则放进 `SPEC.md`。
- 代理接力上下文放进 `CONTEXT.md`。
- 已发生的重要变更放进 `UPDATE_LOG.md`。
- 当前要做、下一步要做、暂时卡住的事放在这里。

## 更新规则

- 每次开始一组新工作前，先看这里。
- 做完一项后，把它从 `Now` 或 `Next` 移到 `Done`，并在 `UPDATE_LOG.md` 记录重要变更。
- 如果一项需要 Owner 权限、服务器权限或外部信息，放进 `Blocked`。
- 不要把聊天里的临时判断长期留在这里；只记录可执行任务和阶段路线。

## Now

### 接服务器自动更新链路

- 建议分支：`feature/server-auto-update`
- 决定日常更新由 OpenClaw cron、普通脚本 cron，还是其他执行器触发。
- 明确服务器路径、运行用户、日志路径、失败提醒方式和部署命令。
- 在服务器安装并配置 GitHub CLI，让服务器能用受控登录态读取 Owner 的 private personal-wiki 仓库内容。
- 将实际命令补进 `DEPLOY.md`。
- 保持 OpenClaw 日常任务只改允许的数据文件。

### 增加资源监控能力

- 来源 ID：`maxnow-resource-monitoring`
- 建议分支：`feature/resource-monitoring`
- 统一设计资源监控模块，先明确哪些指标进入 Home 摘要，哪些进入详情视图或 Token 页面。
- 合并子项：
  - `maxnow-api-key-quota`：补充 API key 剩余额度查询。
  - `maxnow-dounai-traffic-expiry`：补充豆奶剩余流量与到期时间查询。
  - `maxnow-token-usage`：补充已使用 token 数量查询，并与现有 Token 真实数据任务合并。
- 先定义数据来源、权限边界、刷新频率和失败展示方式，再接入页面。

### 做本地/服务器数据更新工具

- 建议分支：`feature/data-update-tooling`
- 提供一个明确命令，用来从 JSON 重新生成对应 `.js` wrapper。
- 让命令可以单独更新 dashboard、ai-news、last-30，也可以一次更新全部数据 wrapper。
- 在命令结束时自动跑 `python scripts/check.py`，减少手工维护出错。

## Next

### 让 Home 支持更真实的项目状态

- 把 Home 的“今日推进 / 当前主线”表达稳定下来，明确哪些字段是手动判断，哪些字段来自自动采集。
- 让系统状态能显示最近一次数据更新时间、最近一次自动化运行结果和异常摘要。
- 让 Last-30 模块只承担滚动上下文，不抢首页主信息层级。

### 补充 Token 使用页真实数据

- 来源 ID：`maxnow-token-usage`
- 明确 Token 数据来源、读取方式、权限边界和刷新频率。
- 将当前占位数据替换成可追溯的真实数据或明确标记为手动快照。
- 保留 1h / 24h / 7d / 30d、模型占比、趋势和异常峰值展示。
- 这项是资源监控的一部分；实现时避免和资源监控模块重复建两套数据链路。

### 设计手机端 OpenClaw 更新 personal-wiki 链路

- 来源 ID：`maxnow-openclaw-sync`
- 建议分支：`feature/wiki-openclaw-sync`
- 方案文档和数据归属策略留在 personal-wiki；MaxNow 仓库负责实现与展示相关的接口、入口和服务器侧操作说明。
- 明确手机端如何触发 OpenClaw 记录 / 更新待办，以及 OpenClaw 如何受控操作同服务器上的 MaxNow。
- 先形成最小闭环：记录待办、同步到 personal-wiki、MaxNow 读取或跳转查看。

### 补充访问控制和隐私策略

- 选择 v1 的保护方式：Basic Auth、VPN、IP 限制、反代鉴权或其他方式。
- 明确 HTTPS / 域名 / 反代配置。
- 更新 `DEPLOY.md`。

### 补充自动化运行日志

- 定义 OpenClaw 或自动更新脚本的运行日志格式。
- 至少记录：运行时间、更新文件、是否成功、错误摘要。
- 让 Home 的系统状态能反映最近一次自动更新。

### 视觉确认 Last-30 首页模块

- 在浏览器里检查 Last-30 模块的位置、密度和移动端表现。
- 如果 Owner 觉得信息太重，调整显示数量或层级。
- 目标是让它辅助 Home，而不是压过今日状态和当前主线。

## Later

### 个人博客联动

- 来源 ID：`maxnow-blog-module`
- 个人博客属于未来公开表达方向，不并入 MaxNow v1 的私人状态工作站范围。
- 拆分归属：旧博客 211 篇文章的内容筛选、清理和隐私判断留在 personal-wiki；博客模块开发、发布状态入口和必要的页面能力放在 MaxNow。
- 后续可以考虑只在 MaxNow 中显示博客迁移 / 发布进度，而不是把完整博客阅读体验塞进私人 Home。

### 桌面伴随入口

- macOS：顶部状态栏 app，点击后出现下拉个人面板。
- Windows：桌面壁纸式个人看板，作为平静常驻的状态层。
- 两个平台尽量复用 `data/*.json` 的同一套数据契约。

### 公开 MaxNow 主页或灵感宇宙

- 仅在私人工作站稳定后再考虑。
- 不要让公开表达影响 `dash.maxnow.cn` 的私人状态工作站定位。

## Blocked

### personal-wiki 待办接入待确认

- 是否只读展示，还是允许从 MaxNow 进入后编辑 / 标记完成。
- MaxNow 仓库内开发待办采用 issue、Markdown、JSON 还是其他机器可读格式，并如何与 personal-wiki 待办在界面上区分。

### personal-wiki / OpenClaw 同步策略待确认

- OpenClaw 更新 personal-wiki 时采用直接 commit、PR，还是其他受控写入方式。
- 手机端触发更新时的权限、回滚和失败提醒方式。
- 同服务器上的 MaxNow 被 OpenClaw 操作时，哪些动作允许自动执行，哪些必须 Owner 确认。

### 个人博客模块待确认

- 个人博客面向自己、公开访客，还是两者兼有。
- 博客读取 personal-wiki 的哪些知识页面，以及是否需要发布 / 隐私筛选机制。
- 旧博客 211 篇文章中，哪些适合公开发布、哪些只保留归档、哪些需要拆成长期 wiki 知识页。

### 服务器定时任务

- 阻塞原因：需要 Owner 提供服务器访问方式、目标路径、运行环境，以及可读取 private personal-wiki 的 GitHub CLI 授权方式。
- 可先在本地准备脚本和部署文档，真正落地时再连接服务器。

### Token 使用自动化

- 阻塞原因：需要明确 Token 数据来源、读取方式和权限边界。
- 当前先用静态数据占位，不把 Token 页面做成不可靠的实时系统。

## Done

### 已完成的基础能力

- 在 Home 主内容区增加 personal-wiki 近期待办入口，位于“当前主线”和“今日推进”之间，当前为只读展示 / 跳转，不支持编辑或标记完成。
- 新增 `scripts/sync_wiki_todos.py` 和 `data/wiki-todos.*`，用 `gh api` 从 private personal-wiki 生成 MaxNow 可静态读取的待办缓存。
- 建立 `AGENTS.md`，固定分支、语言、文件边界和 OpenClaw 边界。
- 建立 `CONTEXT.md`，保存代理接力用的项目上下文地图。
- 建立 `IDEAS.md`，记录未来想法和桌面伴随入口。
- 建立 `UPDATE_LOG.md`，记录重要项目更新。
- 建立 `openclaw/maxnow-dashboard/SKILL.md`，约束 dashboard / ai-news 数据维护。
- 建立 `openclaw/last-30/SKILL.md`，约束 Last-30 滚动记忆维护。
- 建立 `data/last-30.*`，承载今日、本周、近 30 天上下文。
- 在 Home 页面接入 Last-30 模块。
- 中文化 `README.md` 和 `DEPLOY.md`。
- 新增 `scripts/check.py`，用于本地一致性校验。
