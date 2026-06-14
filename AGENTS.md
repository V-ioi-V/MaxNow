# MaxNow Agent Notes

Read this file before making code changes in this repository.

## First Checks

- Run `git status --short` before editing.
- If there are unrelated user changes, preserve them and work around them.
- Read `SPEC.md` before changing product behavior.
- Read `CONTEXT.md` when the task depends on project direction, context strategy, automation scope, or next-step planning.
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
CONTEXT.md
IDEAS.md
UPDATE_LOG.md
openclaw/maxnow-dashboard/SKILL.md
```

OpenClaw routine jobs may edit only:

```text
data/dashboard.json
data/dashboard.js
data/ai-news.json
data/ai-news.js
```

OpenClaw routine jobs must not edit page code or documentation.

## Data Rules

- `data/dashboard.json` owns personal state, mainlines, actions, daily log, timeline, system status, and Token usage.
- `data/ai-news.json` owns AI external inputs only.
- Regenerate each `.js` wrapper from its matching JSON file.
- Validate JSON before finishing data changes.

## Product Direction

- Home is about personal status, not news.
- Token is an independent usage page.
- AI daily picks are secondary external inputs, capped at 3 visible items.
- Keep the interface calm, compact, and operational.
- Record new product ideas in `IDEAS.md`.
- Record intentional project updates in `UPDATE_LOG.md`.
- Keep the context map in `CONTEXT.md` current when the project structure or context strategy changes.
- Treat `CONTEXT.md` primarily as agent handoff context, not as an owner-facing report.

## Language Rules

- Owner-facing product documents should be written in Chinese.
- Agent-facing operational instructions may remain in English.
- When a document is meant for both the owner and agents, prefer Chinese for product meaning and concise English for execution rules only when useful.
