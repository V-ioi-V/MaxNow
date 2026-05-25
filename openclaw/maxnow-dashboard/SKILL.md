---
name: maxnow-dashboard-maintainer
description: Maintain the MaxNow personal dashboard data. Use when OpenClaw needs to summarize daily tasks, feeds, projects, and server state for the static MaxNow dashboard by updating data/dashboard.json without changing page code.
---

# MaxNow Dashboard Maintainer

Maintain the personal dashboard deployed at `dash.maxnow.cn`.

The dashboard is a static website. Do not edit `index.html`, `styles.css`, or `app.js` during routine daily maintenance. Update only the data file:

```text
data/dashboard.json
```

## Goal

Create a concise daily operating snapshot for MaxNow:

- today's brief
- priority tasks
- schedule rhythm
- useful feed summaries
- active projects
- server and automation status

The website reads `data/dashboard.json` in the browser. A valid JSON update is enough for the page to refresh on next load.

## Hard Rules

1. Only write `data/dashboard.json` for routine updates.
2. Keep valid UTF-8 JSON. Do not add comments or trailing commas.
3. Do not include secrets, tokens, private keys, passwords, cookies, or internal IPs.
4. Keep text short. The dashboard is for scanning, not reading long reports.
5. Preserve all top-level fields even when some sections have no new data.
6. If a data source fails, keep the last known safe value or write a short fallback note.
7. Validate JSON before finishing.

## Data Shape

Write this complete structure:

```json
{
  "brief": "一句今日摘要。",
  "feedSource": "OpenClaw Daily",
  "automation": {
    "status": "正常",
    "summary": "OpenClaw 本次做了什么。",
    "lastRun": "YYYY-MM-DD HH:mm"
  },
  "tasks": [
    {
      "title": "任务标题",
      "note": "一句说明。",
      "label": "Focus",
      "status": "active"
    }
  ],
  "timeline": [
    {
      "time": "09:30",
      "title": "事项标题",
      "note": "一句说明。"
    }
  ],
  "feeds": [
    {
      "source": "RSS / GitHub / Server / OpenClaw",
      "title": "信息标题",
      "summary": "一句摘要。",
      "url": ""
    }
  ],
  "projects": [
    {
      "name": "项目名",
      "note": "当前推进状态。",
      "progress": 50,
      "status": "MVP"
    }
  ],
  "system": [
    {
      "key": "server",
      "name": "轻量服务器",
      "value": "Online",
      "note": "2C / 2G / 40G"
    }
  ]
}
```

## Field Guidance

`brief`: one sentence, usually 25-60 Chinese characters.

`automation.status`: use `正常`, `部分失败`, or `需要关注`.

`automation.summary`: describe the maintenance result, not implementation details.

`automation.lastRun`: use local server time in `YYYY-MM-DD HH:mm`.

`tasks`: keep 3-6 items. Use status values:

- `active`: should be handled soon
- `waiting`: blocked or waiting
- `done`: completed

`timeline`: keep 3-5 time blocks. Use 24-hour `HH:mm`.

`feeds`: keep 3-6 high-signal items. Include a URL only when it is safe and useful.

`projects`: keep 1-5 active projects. `progress` must be an integer from 0 to 100.

`system`: include at least:

- `server`
- `storage`
- `tls`
- `openclaw` when available

## Daily Workflow

1. Read the existing `data/dashboard.json`.
2. Gather available daily inputs: tasks, notes, RSS, GitHub activity, server state, and OpenClaw run result.
3. Summarize aggressively. Prefer fewer, clearer items.
4. Rewrite the full JSON object.
5. Validate the file.
6. Leave page code untouched.

## Validation

Before finishing, parse the JSON. Example:

```bash
python -m json.tool data/dashboard.json >/dev/null
```

If validation fails, restore the previous valid JSON and report the error.

## Deployment Model

The expected production path is similar to:

```text
/var/www/maxnow-dashboard/data/dashboard.json
```

The page code is deployed from GitHub. Daily data is maintained on the server by OpenClaw.

Do not run `git pull`, `git push`, or edit repository code unless the user explicitly asks for a site code change.

## Good Output Style

Use calm operational language:

- "今天优先处理部署闭环和数据自动化。"
- "OpenClaw 已刷新任务、信息流和服务状态。"
- "TLS 配置待确认。"

Avoid hype, long explanations, markdown, and multi-paragraph text inside JSON fields.
