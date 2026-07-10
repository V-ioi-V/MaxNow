---
name: maxnow-data
description: Maintain MaxNow personal status workstation data. Use when OpenClaw updates daily personal state, logs, automation status, token usage, and AI external inputs for the static dashboard without changing page code or roadmap-generated project status.
---

# MaxNow Data

Maintain the data files for the private MaxNow workstation deployed at `dash.maxnow.cn`.

MaxNow is not a news site and not an OpenClaw report page. It is the owner's personal status workstation: today's state, roadmap-generated project status, daily log, time points, system health, Token usage, and a small external-input area.

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
dash/data/project-status.json
dash/data/project-status.js
```

If a page structure or style change is needed, stop and report it. Do not modify page code.

## Goal

Create a concise daily personal status snapshot:

- today's mode, energy, focus, and one-sentence judgment
- preserve roadmap-generated mainlines and next steps; OpenClaw does not write them
- short daily log notes and decisions
- time points and automation rhythm
- OpenClaw/server/data/GitHub state
- Token usage ranges and trends
- AI external inputs when useful

OpenClaw records facts and drafts summaries. The owner keeps final judgment. Do not overwrite owner-confirmed notes unless explicitly asked.

## Data Files

`dash/data/dashboard.json` owns manual personal state and machine status fields used by Home. `dash/data/dashboard.js` must contain the same object assigned to `window.MAXNOW_DASHBOARD_DATA`. Project mainlines and actions live in `dash/data/project-status.*`, generated explicitly from `ROADMAP.md` by Codex or the owner; OpenClaw must not edit them.

`dash/data/ai-news.json` is only for Home AI external inputs. It normally contains 0-3 high-signal items from the free external AI signal collector or Last-30 AI signal memory. `dash/data/ai-news.js` must contain the same object assigned to `window.MAXNOW_AI_NEWS_DATA`.

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
  "weather": {
    "location": "北京市海淀区",
    "district": "海淀",
    "condition": "晴",
    "icon": "sun",
    "tempC": 22,
    "highC": 35,
    "lowC": 23,
    "updatedAt": "YYYY-MM-DD HH:mm",
    "source": "Open-Meteo"
  },
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

Keep arrays short:

- `journal`: 2-5
- `timeline`: 3-5
- `feeds`: 0-3

`specialDates` is optional and manually maintained. It powers only the Home time card's same-day birthday / anniversary hint. Use either fixed Gregorian dates with `month` and `day`, or one-time dates with `date: "YYYY-MM-DD"`. Do not expand it into a calendar system.

`weather` is maintained by `scripts/sync_weather.py` / `python scripts/update_data.py runtime`. Preserve it when editing dashboard data manually. Supported `icon` values are `sun`, `cloud`, `rain`, `storm`, `snow`, and `fog`.

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

Show at most 3 items on the page. Use free public sources first: official blogs/RSS, Hacker News, GitHub releases, Reddit/public community sources, arXiv, GDELT, and research labs. X/Twitter is useful for early signals but is not required and must not be used through paid API unless the owner explicitly approves budget and account list.

## Source Policy

Automatic sources:

- Token usage
- GitHub activity
- server and deployment status
- OpenClaw run result
- AI external inputs
- timestamps

Semi-automatic sources:

- daily log draft
- project progress summary outside roadmap-generated task fields

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
