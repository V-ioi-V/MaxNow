# MaxNow Agent Notes

Read this file before making code changes in this repository.

## First Checks

- Run `git status --short` before editing.
- Do not make code or document changes directly on `main`.
- Before editing, create or switch to a short-lived branch from the latest `main`.
- Use `feature/<short-demand-name>` for new features and `bugfix/<short-bug-name>` for fixes, unless the owner asks for another branch name.
- After the work is checked, merge the branch back into `main` or ask the owner before merging if the change is risky.
- 当 Owner 表达“没问题了，合进去吧”“合码”“合入主分支”等意图时，固定理解为：把已完成工作合入远端 `origin/main`，然后切回本地 `main` 并执行 `git pull`，让本地 `main` 与远端保持一致。
- 当 Owner 要求“记录一下”“加个待办”“记个待办”等轻量文档记录时，完成文档更新和必要检查后，默认直接合入远端 `origin/main`，不要停在本地分支或 PR，除非本次改动存在明显风险、包含无关改动、或 Owner 明确要求不要合并。
- If there are unrelated user changes, preserve them and work around them.
- Read `SPEC.md` before changing product behavior.
- Read `STYLE_CONTEXT.md` before changing Dash or Blog frontend styles.
- For Dash or Blog UI changes, treat `STYLE_CONTEXT.md` as an execution checklist: new or moved cards/widgets must inherit their component family's hover/focus selectors, transitions, border/shadow treatment, responsive constraints, and cache-version updates.
- When UI elements are meant to align in one row, verify geometry in the browser or DOM measurements, including same top, same bottom, same height, and no horizontal overflow; do not rely on visual placement alone.
- Read `CONTEXT.md` when the task depends on project direction, context strategy, automation scope, or next-step planning.
- Read `ROADMAP.md` when the task asks what remains, what to do next, or how to sequence work.
- Read `SERVER_RUNBOOK.md` before operating the MaxNow server over SSH or changing nginx/server deployment state.
- For OpenClaw behavior, read `openclaw/maxnow-dashboard/SKILL.md`.

## Completion Records

- After completing a feature, server operation, automation setup, data pipeline, or project-structure change, update the repository records in the same branch before finishing.
- Move completed work out of `ROADMAP.md` Now / Next / Blocked and into Done when applicable.
- Add an `UPDATE_LOG.md` entry for meaningful changes to page behavior, data flow, server state, deployment, automation, or repository rules.
- Update `CONTEXT.md` when the change affects agent handoff context, current gaps, file responsibilities, automation boundaries, server state, or recommended next steps.
- Update `SERVER_RUNBOOK.md` when the change affects SSH, nginx, GitHub CLI, deployment, cron/systemd timers, server paths, auth state, or operational commands.
- Do not leave completed work only in chat. If the owner asks to "记个待办", "优化待办", "做完了", "服务器搞好了", or similar, reflect that in the relevant repository documents.

## Project Shape

MaxNow is a private status workstation for `dash.maxnow.cn`.

- Page code is maintained by Codex or the owner.
- OpenClaw only updates data files.
- The site is static for v1: no login, database, or backend API.

## File Boundaries

Codex or the owner may edit:

```text
dash/index.html
dash/styles.css
dash/app.js
dash/data/ricky.json
dash/data/ricky.js
blog/preview.html
blog/preview.css
SPEC.md
STYLE_CONTEXT.md
README.md
DEPLOY.md
SERVER_RUNBOOK.md
scripts/check.py
scripts/update_data.py
scripts/sync_system_status.py
scripts/sync_wiki_todos.py
scripts/sync_openclaw_usage.py
scripts/sync_codex_usage.py
scripts/sync_token_usage.py
scripts/report_codex_usage.ps1
scripts/install_local_codex_usage_task.ps1
scripts/sync_project_meta.py
scripts/sync_weather.py
scripts/sync_ricky_travel.py
VERSION
CONTEXT.md
ROADMAP.md
IDEAS.md
UPDATE_LOG.md
openclaw/maxnow-dashboard/SKILL.md
openclaw/last-30/SKILL.md
```

OpenClaw routine jobs may edit only data files allowed by the active skill:

```text
dash/data/dashboard.json
dash/data/dashboard.js
dash/data/ai-news.json
dash/data/ai-news.js
dash/data/last-30.json
dash/data/last-30.js
dash/data/wiki-todos.json
dash/data/wiki-todos.js
dash/data/openclaw-usage.json
dash/data/openclaw-usage.js
dash/data/codex-usage.json
dash/data/codex-usage.js
dash/data/token-usage.json
dash/data/token-usage.js
dash/data/project-meta.json
dash/data/project-meta.js
```

OpenClaw routine jobs must not edit page code or documentation.

## Data Rules

- `dash/data/dashboard.json` owns personal state, mainlines, actions, daily log, timeline, system status, Home weather, and Token usage.
- `dash/data/ai-news.json` owns AI external inputs only.
- `dash/data/last-30.json` owns the rolling 30-day external AI signal memory: daily AI signals, weekly AI changes, 30-day AI mainlines, impact notes, and watch items.
- `dash/data/wiki-todos.json` owns the read-only MaxNow cache generated from personal-wiki `wiki/tasks/todo.json`.
- `dash/data/openclaw-usage.json` owns OpenClaw token usage aggregates and OpenRouter-equivalent cost estimates generated from server-side OpenClaw trajectory logs.
- `dash/data/codex-usage.json` owns Codex token usage aggregates and OpenAI API-equivalent cost estimates generated from local or server `.codex/sessions` `token_count` plus `turn_context.model` events; it must not export prompt or response body text.
- `dash/data/token-usage.json` owns the combined Token page ledger generated from OpenClaw and Codex source ledgers.
- `dash/data/project-meta.json` owns the displayed MaxNow version, deploy note, and recent update summaries generated from `VERSION`, Git state, and `UPDATE_LOG.md`.
- `dash/data/ricky.json` owns the read-only "我和 Ricky" map, places, trip records, notes, and optional photo/source links.
- Do not update `dash/data/*.json` or `dash/data/*.js` when the owner asks for MaxNow project todos, feature planning, roadmap updates, or "what should MaxNow build next"; update `ROADMAP.md`, `IDEAS.md`, `CONTEXT.md`, or `UPDATE_LOG.md` instead.
- For Last-30 AI external signals, prefer free public sources first: official blogs/RSS, GitHub releases, Hacker News, Reddit/public community sources, arXiv, GDELT or similar free indexes. Do not make X/Twitter a hard dependency unless the owner explicitly approves paid API usage.
- Only change data files when the owner explicitly asks to update the displayed dashboard/status data, or when running an approved data maintenance task.
- Regenerate each `.js` wrapper from its matching JSON file.
- Validate JSON before finishing data changes.
- Use `python scripts/sync_wiki_todos.py` to refresh `dash/data/wiki-todos.*` from private personal-wiki through the local or server `gh` login; never put GitHub tokens in frontend code.
- Use `python scripts/sync_system_status.py` to refresh machine-collected `automation` and `system` fields in `dash/data/dashboard.*`; do not let it overwrite owner judgment fields such as today, mainlines, actions, or journal.
- Use `python scripts/sync_weather.py` or `python scripts/update_data.py weather` to refresh the Home weather card for Beijing Haidian District; `runtime` also runs this refresh.
- Use `python scripts/sync_openclaw_usage.py` or `python scripts/update_data.py openclaw-usage` on the server to refresh OpenClaw token usage from `/root/.openclaw`; costs are estimates using OpenRouter model prices, not real provider billing.
- Use `python scripts/sync_codex_usage.py` or `python scripts/update_data.py codex-usage` to refresh Codex token usage from `.codex/sessions`; export only token usage, model name, timestamp, source label, and equivalent cost fields, never prompt or response body text.
- Use `python scripts/sync_token_usage.py` or `python scripts/update_data.py token-usage` to merge OpenClaw and Codex ledgers into the unified Token page ledger.
- Use `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_local_codex_usage_task.ps1` on the owner's Windows machine to install local Codex usage reporting. The scheduled task runs `scripts/report_codex_usage.ps1`, may only commit `dash/data/codex-usage.*` and `dash/data/token-usage.*`, and must not refresh server-side Codex usage when deploying the merged Token ledger.
- Use `python scripts/sync_project_meta.py` or `python scripts/update_data.py project-meta` to refresh the MaxNow version and recent update module.
- Use `python scripts/sync_ricky_travel.py` or `python scripts/update_data.py ricky-travel` to refresh the "我和 Ricky" travel map from personal-wiki `wiki/relationships/ricky-travel.json`.
- Use `python scripts/sync_ai_last30.py` or `python scripts/update_data.py ai-last30` to refresh free external AI signals into `dash/data/ai-news.*` and `dash/data/last-30.*`.
- Prefer `python scripts/update_data.py runtime` for server runtime refreshes, including wiki todos, Ricky travel records, weather, system status, and project metadata; use `python scripts/update_data.py wrap all` for wrapper regeneration, and `python scripts/update_data.py project-status` only when the owner wants Home project status refreshed from `ROADMAP.md`.
- Use `python scripts/check.py` for local consistency checks when data wrappers or docs change.

## Product Direction

- Home is about personal status, not news.
- Token is an independent usage page.
- AI daily picks are secondary external inputs, capped at 3 visible items.
- Keep the interface calm, compact, and operational.
- Record new product ideas in `IDEAS.md`.
- Record executable next steps and phase planning in `ROADMAP.md`.
- Record intentional project updates in `UPDATE_LOG.md`.
- Keep the context map in `CONTEXT.md` current when the project structure or context strategy changes.
- Treat `CONTEXT.md` primarily as agent handoff context, not as an owner-facing report.

## Language Rules

- Owner-facing product documents should be written in Chinese.
- Agent-facing operational instructions may remain in English.
- When a document is meant for both the owner and agents, prefer Chinese for product meaning and concise English for execution rules only when useful.
