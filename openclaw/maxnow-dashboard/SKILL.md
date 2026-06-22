---
name: maxnow-data
description: Maintain MaxNow personal status workstation data. Use when OpenClaw updates daily personal state, current mainlines, actions, logs, automation status, token usage, and AI external inputs for the static dashboard without changing page code.
---

# MaxNow Data

Maintain the data files for the private MaxNow workstation deployed at `dash.maxnow.cn`.

MaxNow is not a news site and not an OpenClaw report page. It is the owner's personal status workstation: today's state, current mainlines, today's actions, daily log, time points, system health, Token usage, and a small external-input area.

## Hard Boundary

Routine OpenClaw runs may update only:

```text
dash/data/dashboard.json
dash/data/dashboard.js
dash/data/ai-news.json
dash/data/ai-news.js
dash/data/dounai_checkin.json
```

Routine OpenClaw runs must not edit:

```text
dash/index.html
dash/styles.css
dash/app.js
SPEC.md
README.md
DEPLOY.md
CONTEXT.md
IDEAS.md
UPDATE_LOG.md
dash/data/last-30.json
dash/data/last-30.js
```

If a page structure or style change is needed, stop and report it. Do not modify page code.

## Goal

Create a concise daily personal status snapshot:

- today's mode, energy, focus, and one-sentence judgment
- current mainlines and next steps
- 1-3 actions that should move today
- short daily log notes and decisions
- time points and automation rhythm
- OpenClaw/server/data/GitHub state
- Token usage ranges and trends
- AI external inputs when useful

OpenClaw records facts and drafts summaries. The owner keeps final judgment. Do not overwrite owner-confirmed notes unless explicitly asked.

## Data Files

`dash/data/dashboard.json` is the main data source for Home and Token. `dash/data/dashboard.js` must contain the same object assigned to `window.MAXNOW_DASHBOARD_DATA`.

`dash/data/ai-news.json` is only for AI external inputs. `dash/data/ai-news.js` must contain the same object assigned to `window.MAXNOW_AI_NEWS_DATA`.

`dash/data/dounai_checkin.json` stores Dounai daily check-in results, account balance snapshots, and account daily-budget history. OpenClaw check-in automation may update it, but MaxNow should only display traffic, account-extension hours, cumulative check-in days, remaining usable traffic, expiry, daily traffic budget, daily-budget history, and recent records for charts/tables; beans are raw data only and should not drive UI.

## Dashboard Data Shape

Preserve this shape when possible:

```json
{
  "brief": "今天最重要的一句话判断。",
  "feedSource": "今日整理",
  "today": {
    "mode": "clarify",
    "modeLabel": "整理模式",
    "energy": "中",
    "focus": "MaxNow",
    "summary": "今天主要确认个人看板的定位。",
    "updatedAt": "YYYY-MM-DD HH:mm"
  },
  "automation": {
    "status": "正常",
    "summary": "OpenClaw 已更新今日状态快照。",
    "lastRun": "YYYY-MM-DD HH:mm"
  },
  "mainlines": [
    {
      "title": "MaxNow",
      "note": "当前状态、下一步、卡点。",
      "label": "主线",
      "status": "active"
    }
  ],
  "actions": [
    {
      "title": "今天要推进的动作",
      "note": "一句话说明。",
      "label": "推进",
      "status": "active"
    }
  ],
  "journal": [
    {
      "source": "Owner / OpenClaw / GitHub",
      "title": "记录标题",
      "summary": "一句话记录事实或判断。",
      "url": ""
    }
  ],
  "timeline": [
    {
      "time": "00:10",
      "title": "AI 外部输入更新",
      "note": "OpenClaw 更新 dash/data/ai-news.*。"
    }
  ],
  "specialDates": [
    {
      "month": 7,
      "day": 18,
      "title": "77 生日",
      "type": "birthday"
    }
  ],
  "feeds": [
    {
      "source": "GitHub / RSS / HN / Server",
      "title": "外部输入标题",
      "summary": "为什么值得稍后看。",
      "url": ""
    }
  ],
  "system": [
    {
      "key": "server",
      "name": "轻量服务器",
      "value": "Online",
      "note": "一句话状态。"
    }
  ],
  "tokenUsage": {
    "updatedAt": "YYYY-MM-DD HH:mm",
    "ranges": [],
    "models": [],
    "daily": []
  }
}
```

Status values for `mainlines` and `actions`:

- `active`: should move soon
- `waiting`: blocked or waiting
- `done`: completed

Keep arrays short:

- `mainlines`: 1-3
- `actions`: 1-3
- `journal`: 2-5
- `timeline`: 3-5
- `feeds`: 0-3

`specialDates` is optional and manually maintained. It powers only the Home time card's same-day birthday / anniversary hint. Use either fixed Gregorian dates with `month` and `day`, or one-time dates with `date: "YYYY-MM-DD"`. Do not expand it into a calendar system.

## AI External Input Shape

`dash/data/ai-news.json` should contain:

```json
{
  "updatedAt": "YYYY-MM-DD HH:mm",
  "sourceSummary": "OpenClaw AI external inputs",
  "items": [
    {
      "source": "OpenAI / Anthropic / HN / GitHub / Reddit / X",
      "title": "短标题",
      "summary": "说明它和 owner、项目、工具、模型或成本有什么关系。",
      "url": "https://example.com",
      "publishedAt": "YYYY-MM-DD",
      "signal": "official"
    }
  ]
}
```

Show at most 3 items on the page. X/Twitter is useful for early signals but is not required. If X is unavailable, use official blogs/RSS, Hacker News, GitHub, Reddit, releases, and research labs.

## Source Policy

Automatic sources:

- Token usage
- GitHub activity
- server and deployment status
- OpenClaw run result
- AI external inputs
- timestamps

Semi-automatic sources:

- current mainlines
- daily log draft
- project progress summary

Manual or owner-confirmed fields:

- today's one-sentence judgment
- energy/state
- true priority
- important decisions

Do not invent personal feelings. If unsure, keep a neutral status such as `待确认`.

## Validation

Before finishing every routine update:

```bash
python -m json.tool dash/data/dashboard.json >/dev/null
python -m json.tool dash/data/ai-news.json >/dev/null
python -m json.tool dash/data/dounai_checkin.json >/dev/null
```

Regenerate wrappers from the JSON files:

```bash
python -c "import json; from pathlib import Path; d=json.loads(Path('dash/data/dashboard.json').read_text(encoding='utf-8')); Path('dash/data/dashboard.js').write_text('window.MAXNOW_DASHBOARD_DATA = '+json.dumps(d, ensure_ascii=True, indent=2)+';\n', encoding='ascii')"
python -c "import json; from pathlib import Path; d=json.loads(Path('dash/data/ai-news.json').read_text(encoding='utf-8')); Path('dash/data/ai-news.js').write_text('window.MAXNOW_AI_NEWS_DATA = '+json.dumps(d, ensure_ascii=True, indent=2)+';\n', encoding='ascii')"
```

If a source fails, keep the last safe value or write a short fallback note. Do not clear the dashboard.

## Good Output Style

Use short operational Chinese. Prefer:

- `今天主要确认 MaxNow 的定位和 OpenClaw 数据边界。`
- `下一步是把服务器部署和数据定时更新接起来。`
- `AI 外部输入只保留与工具、模型或成本有关的信号。`

Avoid hype, long reports, marketing language, and markdown inside JSON string fields.
