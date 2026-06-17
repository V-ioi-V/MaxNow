# MaxNow 更新记录

这个文件记录 MaxNow 的重要更新，让产品方向、数据边界和实现决定可以被追溯。

## 使用规则

- 只要 Codex、Owner 或其他维护者改变了产品方向、页面代码、数据结构或操作规则，就在这里补一条。
- 每条记录保持简短、具体。
- 有必要时写清楚涉及哪些文件。
- 原始未来想法写进 `IDEAS.md`；已经确认的产品行为再同步进 `SPEC.md`。

## 2026-06-17

### 补充服务器云位置和计费信息

- 更新 `scripts/sync_system_status.py`，从腾讯云 metadata 读取实例 ID、公网 IP、region、zone、计费类型、创建时间和 termination time。
- 系统状态模块新增“云位置”和“计费/有效期”信息；当前服务器是 `ap-singapore-2`，按量计费，无固定到期时间。
- 继续补充证书到期、最近 git pull 时间、定时任务状态、失败日志摘要和系统 uptime，方便 Owner 在线上先看一版再决定保留哪些卡片。
- 更新 `SERVER_RUNBOOK.md`，记录相关 metadata 查询命令和当前服务器可读到的信息。

原因：

- Owner 希望在系统状态里看到服务器位置、有效期，并理解系统状态前几项的含义。

### 优化动态数据待办顺序

- 更新 `ROADMAP.md`，把近期实现顺序调整为：服务器自动同步 wiki-todos、系统状态动态化、统一数据 wrapper 工具。
- 将 Token 真实数据、AI 外部输入、Last-30 增量更新等任务放入后续队列，避免在数据来源未明确前先做复杂页面能力。
- 标记服务器 GitHub CLI 已具备读取 private personal-wiki 的条件，服务器定时任务剩余重点转为 cron / systemd timer、日志和失败提醒。
- 新增 `scripts/sync_system_status.py`，用于采集 nginx、HTTPS、git commit、磁盘、内存和 wiki-todos 同步状态，并只更新 dashboard 的 `automation` / `system` 字段。
- 更新 `SPEC.md`、`CONTEXT.md`、`SERVER_RUNBOOK.md` 和 `ROADMAP.md`，记录系统状态脚本的边界、手动运行命令和后续定时化任务。
- 更新 `AGENTS.md`，要求完成功能、服务器操作、自动化或数据链路后，同步维护 `ROADMAP.md`、`UPDATE_LOG.md`、`CONTEXT.md` 和必要的 runbook，不允许只停留在聊天记录。
- 更新 `CONTEXT.md` 和 `SERVER_RUNBOOK.md`，记录服务器 GitHub CLI 已安装授权、本地预览可通过 `127.0.0.1:8000` 访问、服务器可读取 private personal-wiki 并运行 `scripts/sync_wiki_todos.py`。

原因：

- Owner 希望根据当前页面模块和现有数据链路，重新整理哪些待办现在最值得推进。
- Owner 指出完成实际功能或服务器操作后，必须同步更新仓库里的待办、已完成记录、日志和上下文。

## 2026-06-16

### 增加 personal-wiki 近期待办入口

- 在 Home 主内容区新增 `Personal Wiki / 近期待办` 紧凑模块，位于“当前主线”和“今日推进”之间。
- 新增 `scripts/sync_wiki_todos.py`，通过本地或服务器 `gh api` 读取 private personal-wiki `wiki/tasks/todo.json`。
- 新增 `data/wiki-todos.json` 和 `data/wiki-todos.js`，作为 MaxNow 前端可静态读取的待办缓存。
- 模块只读展示 `data/wiki-todos.json` 中的未完成待办，并提供跳转入口。
- 顶部刷新按钮会重新读取本地缓存；前端不直接访问 private GitHub raw，不做自动轮询，也不支持编辑或标记完成。
- 补充 `SPEC.md`，记录入口位置、只读边界和刷新策略。
- 更新 `AGENTS.md`、`CONTEXT.md` 和 `ROADMAP.md`，纳入新的数据文件、同步脚本和维护边界。
- 在 `ROADMAP.md` 记录服务器还需要安装并授权 GitHub CLI，才能自动读取 Owner 的 private personal-wiki 仓库。

原因：

- Owner 希望 MaxNow Home 能看见 personal-wiki 的近期待办，但不要把 Home 做成完整 todo app。

### 明确“合码 / 合入主分支”的 Git 语义

- 更新 `AGENTS.md`，记录 Owner 表达“没问题了，合进去吧”“合码”“合入主分支”等意图时的固定流程。
- 这类表达表示：把已完成工作合入远端 `origin/main`，然后切回本地 `main` 并执行 `git pull`，让本地 `main` 与远端保持一致。

原因：

- 避免代理误解为只在当前分支、本地 `main` 或其他集成分支上直接操作；主分支合入目标始终是远端 `origin/main`。

### 合并 personal-wiki 中的 MaxNow 待办

- 更新 `ROADMAP.md`，把 personal-wiki 中 7 个开放待办合并进 MaxNow 仓库路线图。
- 将 personal-wiki 近期代办入口、资源监控、OpenClaw / personal-wiki 同步链路列为 MaxNow 侧可执行待办。
- 将 API key 额度、豆奶流量到期、Token 使用量合并为资源监控模块的子项，避免重复拆任务。
- 将个人博客模块拆分为：内容筛选和隐私判断留在 personal-wiki，模块开发和状态入口归 MaxNow。
- 把入口位置、待办数据格式、编辑权限、OpenClaw 写入方式、博客公开范围和旧文筛选策略放入待确认。

原因：

- Owner 希望把偏产品开发的 MaxNow 待办迁到本仓库，personal-wiki 只保留内容筛选、长期方向、数据归属和待确认策略。

### 部署前端静态站到服务器

- 在服务器安装 nginx，并将 `main` 分支部署到 `/var/www/maxnow-dashboard`。
- 配置 `dash.maxnow.cn` 的 nginx HTTP 静态站点，当前访问 `http://dash.maxnow.cn` 返回 MaxNow 页面。
- 新增 `SERVER_RUNBOOK.md`，记录 SSH 连接方式、部署命令、更新命令和常见排障。
- 更新 `AGENTS.md`、`CONTEXT.md` 和 `DEPLOY.md`，把 `SERVER_RUNBOOK.md` 纳入服务器操作上下文。

原因：

- Owner 要求先部署前端页面，并记录 Codex 是如何在服务器上执行部署的。

## 2026-06-15

### 约束 MaxNow 功能待办的维护位置

- 更新 `AGENTS.md`，明确当 Owner 询问 MaxNow 项目待办、功能规划或下一步实现内容时，不要修改 `data/*.json` 或 `data/*.js`。
- 更新 `ROADMAP.md`，将当前 MaxNow 功能待办整理为：服务器自动更新链路、数据更新工具、Home 真实项目状态、Token 真数据、访问控制、运行日志和 Last-30 视觉确认。
- 更新 `CONTEXT.md`，强调 MaxNow 功能待办以 `ROADMAP.md` 为准，运行数据仍归 `data/*.json`。

原因：

- Owner 明确指出“MaxNow 待办”指的是要给 MaxNow 实现哪些功能，不是要改首页写死展示数据。

## 2026-06-14

### 新增路线图文档

- 新增 `ROADMAP.md`，用 Now / Next / Later / Blocked / Done 维护当前可执行路线。
- 将 `ROADMAP.md` 纳入 `AGENTS.md`、`CONTEXT.md`、`SPEC.md` 和 `README.md` 的文档边界。
- 明确 `CONTEXT.md` 负责代理接力上下文，`ROADMAP.md` 负责待做事项和阶段路线。

原因：

- Owner 询问当前 md 是否都有用，需要把“待做事项”从聊天里固定成可持续维护的文档。

### 整理说明文档和本地校验

- 中文化并重写 `README.md`。
- 中文化并重写 `DEPLOY.md`。
- 新增 `scripts/check.py`，用于检查必要文件、JSON 合法性、wrapper 一致性和本地预览可访问性。
- 将 `scripts/check.py` 纳入 `AGENTS.md`、`SPEC.md` 和 `CONTEXT.md` 的项目边界。

原因：

- 在接服务器自动更新前，先把本地说明和一键校验补齐，降低后续部署风险。

### 固定分支工作流

- 新增规则：不要直接在 `main` 上修改代码或文档。
- 每次改动前先从最新 `main` 拉一个短期工作分支。
- 新功能分支使用 `feature/<short-demand-name>`，修复分支使用 `bugfix/<short-bug-name>`，除非 Owner 指定别的名字。
- 改完检查后再合回 `main`；如果改动有风险，先询问 Owner。

原因：

- Owner 明确要求先从主分支拉分支修改，避免直接改坏主分支。

### 启动 Last-30 首页展示分支

- 创建 `feature/last-30-home-context` 分支，继续推进 Last-30 首页展示。
- 将 `data/last-30.*` 和 `openclaw/last-30/SKILL.md` 纳入项目文件边界和数据契约。
- 更新 `CONTEXT.md`，标记 Last-30 数据文件和 skill 已建立，下一步重点转为首页展示和服务器自动更新。

原因：

- Owner 要求直接开始做，并要求后续分支名按需求语义命名。

### 补充项目上下文地图

- 新增 `CONTEXT.md`，说明 MaxNow 的上下文分层、文件职责、维护者和当前缺口。
- 明确 `CONTEXT.md` 主要给 Codex / 代理接力使用，Owner 可以检查但它不是汇报文档。
- 将 `CONTEXT.md` 纳入 `AGENTS.md` 和 `SPEC.md` 的文件边界。
- 在 `SPEC.md` 中补充 “Last-30 滚动记忆” 未来方向。
- 在 `IDEAS.md` 中记录 Last-30 滚动记忆想法。
- 修复 `data/dashboard.json` 的中文内容，使它和 `data/dashboard.js` 保持一致，避免页面读取 JSON 后出现乱码。
- 将 OpenClaw dashboard skill 的内部名字从 `maxnow-dashboard-maintainer` 缩短为 `maxnow-data`。

原因：

- Owner 希望整体补齐项目上下文，避免目标、数据、自动化和产品记忆分散在聊天里。

## 2026-06-13

### 调整文档语言分工

- 面向 Owner 阅读的产品文档使用中文。
- 面向 Codex / OpenClaw 等代理执行的规则文档可以继续使用英文。
- 将 `SPEC.md`、`IDEAS.md` 和 `UPDATE_LOG.md` 改为中文。
- 将语言分工写入 `AGENTS.md`，作为本仓库后续代理工作的固定规则。

原因：

- Owner 明确要求“给我看的用中文，你自己看的用英文”。

## 2026-06-12

### 增加长期想法记录和更新记录

- 新增 `IDEAS.md`，作为长期产品想法记录。
- 新增 `UPDATE_LOG.md`，作为项目更新记录。
- 记录“桌面伴随面板”方向：
  - macOS 顶部状态栏下拉个人面板。
  - Windows 桌面壁纸式个人看板。
- 更新项目规则，让未来维护者知道这两个文件需要持续维护。
- 更新 OpenClaw 维护边界，明确日常自动化不能编辑这些记忆文档。

原因：

- Owner 不希望新的 MaxNow 想法或项目更新在不同会话之间丢失。

## 2026-06-16

### 启用 HTTPS 访问

- 使用 Let's Encrypt certbot 为 `dash.maxnow.cn` 签发 SSL 证书。
- 更新 nginx 配置，启用 HTTPS 访问。
- 设置 HTTP 到 HTTPS 的 301 跳转。
- certbot 已自动配置证书自动续期。

原因：

- `dash.maxnow.cn` 需要通过 HTTPS 提供访问，并保留 HTTP 请求的稳定跳转路径。
