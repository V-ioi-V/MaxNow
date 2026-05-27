# MaxNow Spec

MaxNow is a private status workstation deployed at `dash.maxnow.cn`. It is not a public home page, a news site, or a generic dashboard. Its job is to show the owner what state they are in, what they are moving forward, what the automation system is doing, and whether AI/tool usage looks normal.

## Product Positioning

- Audience: the site owner only.
- Primary use: open several times a day and understand the current personal/system state in a few seconds.
- Core value: persistent personal context, not one-off notifications.
- Tone: calm, compact, operational, and maintainable.
- First screen priority: personal state, current mainlines, today's actions, time points, system state, and a small amount of external input.

## System Roles

MaxNow has three parts:

1. Page code
   - `index.html`
   - `styles.css`
   - `app.js`
   - Maintained by Codex or the owner.
   - Responsible for structure, styling, rendering, and interaction.

2. Data files
   - `data/dashboard.json`
   - `data/dashboard.js`
   - `data/ai-news.json`
   - `data/ai-news.js`
   - They are the contract between the page and automation.

3. OpenClaw skill
   - `openclaw/maxnow-dashboard/SKILL.md`
   - Tells OpenClaw what MaxNow is, which data files to update, which files are forbidden, and how to validate output.

## Navigation

Keep only two top-level entries:

1. Home
   - Personal status workstation.
   - Default page.
2. Token
   - Token usage detail page.

Do not add a new page unless it answers a separate question that cannot fit on Home without hurting the daily scan.

## Home Page

Home answers these questions, in this order:

1. What state am I in today?
2. What are my current mainlines?
3. What should move forward today?
4. What time points matter today?
5. Are OpenClaw, the server, data sync, and Token usage normal?
6. What external inputs are worth noticing later?

Required modules:

- Today Status: mode, energy, focus, one-sentence summary, updated time.
- Current Mainlines: 1-3 important threads with status, next step, and blocker when useful.
- Today's Actions: 1-3 actions that should move today. This is not a full todo app.
- Daily Log: short notes that preserve personal context and decisions.
- Time Points: schedule items, deadlines, and automation run times.
- System Status: OpenClaw last run, server state, data sync state, GitHub/deployment state when available.
- External Inputs: links, signals, and AI daily picks that may matter later.

## AI Daily Picks

AI daily picks are a small part of External Inputs, not a news product.

- Default update time: 00:10 local server time.
- Show at most 3 items on Home.
- Prefer official sources and high-signal developer/community sources.
- X/Twitter is useful for early signals, but is not a hard dependency.
- If X/Twitter is unavailable, use official blogs/RSS, Hacker News, GitHub, Reddit, project releases, and research labs.
- Secondary news sites are only for supplemental verification.

Each item should explain why it is relevant to the owner, current projects, tools, model choices, or costs.

## Token Page

Token page answers only Token-related questions:

- last 1 hour usage
- last 24 hours usage
- last 7 days usage
- last 30 days usage
- input/output/total/cost
- model share
- recent 7-day trend
- unusual spikes when available

Do not duplicate the full Token page on Home. Home may show only a compact usage status.

## Data Contract

OpenClaw may update these files during routine maintenance:

```text
data/dashboard.json
data/dashboard.js
data/ai-news.json
data/ai-news.js
```

OpenClaw must not update these files during routine maintenance:

```text
index.html
styles.css
app.js
SPEC.md
README.md
DEPLOY.md
```

`data/dashboard.json` owns personal state, mainlines, actions, daily log, timeline, system status, and Token usage.

`data/ai-news.json` owns external AI inputs only.

Each `.js` wrapper must be generated from the matching JSON file and expose the same object to the browser:

```text
window.MAXNOW_DASHBOARD_DATA
window.MAXNOW_AI_NEWS_DATA
```

## Data Source Policy

The dashboard should not depend on daily manual data entry. The intended split is:

- Automatic: Token usage, GitHub activity, server state, OpenClaw run state, AI external inputs, timestamps.
- Semi-automatic: current mainlines, daily log draft, project progress summary.
- Manual: today's one-sentence judgment, energy/state, true priority, and important decisions.

OpenClaw records facts and drafts summaries. The owner keeps final judgment.

## Visual Rules

- Dark, compact, operational interface.
- No marketing hero, no decorative dashboard filler.
- Cards exist only for real information modules.
- Border radius stays at or below 8px.
- External inputs must remain visually secondary to personal status.
- The first screen should prioritize state, mainlines, and today's actions.

## Implementation Guardrails

- Keep Home and Token as the only pages for v1.
- Keep the site static: no database, login, or backend API in v1.
- Any new daily-maintained data field must be documented here and in the OpenClaw skill.
- Page code changes require Codex or owner intent; OpenClaw never changes page structure.
