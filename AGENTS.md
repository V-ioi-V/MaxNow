# MaxNow Agent Notes

Read this file before making code changes in this repository.

## First Checks

- Run `git status --short` before editing.
- Do not make code or document changes directly on `main`.
- Before editing, create or switch to a short-lived branch from the latest `main`.
- Use `feature/<short-demand-name>` for new features and `bugfix/<short-bug-name>` for fixes, unless the owner asks for another branch name.
- After the work is checked, merge the branch back into `main` or ask the owner before merging if the change is risky.
- If there are unrelated user changes, preserve them and work around them.
- Read `SPEC.md` before changing product behavior.
- Read `CONTEXT.md` when the task depends on project direction, context strategy, automation scope, or next-step planning.
- Read `ROADMAP.md` when the task asks what remains, what to do next, or how to sequence work.
- For OpenClaw behavior, read `openclaw/maxnow-dashboard/SKILL.md`.

## Project Shape

MaxNow is a private status workstation for `dash.maxnow.cn`.

- Page code is maintained by Codex or the owner.
- OpenClaw only updates data files.
- The site is static for v1: no login, database, or backend API.

## File Boundaries

Codex or the owner may edit:

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
openclaw/maxnow-dashboard/SKILL.md
openclaw/last-30/SKILL.md
```

OpenClaw routine jobs may edit only data files allowed by the active skill:

```text
data/dashboard.json
data/dashboard.js
data/ai-news.json
data/ai-news.js
data/last-30.json
data/last-30.js
```

OpenClaw routine jobs must not edit page code or documentation.

## Data Rules

- `data/dashboard.json` owns personal state, mainlines, actions, daily log, timeline, system status, and Token usage.
- `data/ai-news.json` owns AI external inputs only.
- `data/last-30.json` owns rolling daily, weekly, and 30-day context.
- Do not update `data/*.json` or `data/*.js` when the owner asks for MaxNow project todos, feature planning, roadmap updates, or "what should MaxNow build next"; update `ROADMAP.md`, `IDEAS.md`, `CONTEXT.md`, or `UPDATE_LOG.md` instead.
- Only change data files when the owner explicitly asks to update the displayed dashboard/status data, or when running an approved data maintenance task.
- Regenerate each `.js` wrapper from its matching JSON file.
- Validate JSON before finishing data changes.
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
