---
name: maxnow-last30
description: Maintain MaxNow rolling 30-day external AI signal data. Use when OpenClaw updates AI news, weekly AI changes, 30-day AI mainlines, impact notes, and watch items without changing page code or product documents.
---

# MaxNow Last-30

Maintain rolling external AI signal context for the private MaxNow workstation.

This skill updates the Last-30 data files only. It does not update page code, product documents, or the main dashboard data unless explicitly instructed by the owner. Last-30 is for external AI signals, not MaxNow internal project logs.

## Hard Boundary

Routine Last-30 runs may update only:

```text
dash/data/last-30.json
dash/data/last-30.js
```

Routine Last-30 runs must not edit:

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
dash/data/dashboard.json
dash/data/dashboard.js
dash/data/ai-news.json
dash/data/ai-news.js
```

If the data shape, page structure, or product boundary needs to change, stop and report it. Do not modify code or documentation during routine runs.

## Goal

Keep a concise rolling Chinese frontier-news memory of:

- the latest 1-3 concrete AI releases
- this week's additional, non-duplicate frontier changes
- recent 30-day concrete milestones, not keyword buckets
- potential impact on MaxNow, Codex, OpenClaw, model choices, or token cost
- watch items and uncertain signals
- judgments that still need owner confirmation

Prefer free public sources first: official blogs/RSS, GitHub releases, Hacker News, Reddit/public community sources, arXiv, GDELT, or similar free indexes. X/Twitter is not a hard dependency; do not use paid X API unless the owner explicitly approves budget and account list.

Do not feed large full-text news dumps into the model. Use scripts or source snippets to prefilter candidates, then summarize only a small candidate set.

## Data Files

`dash/data/last-30.json` is the source of truth. `dash/data/last-30.js` must contain the same object assigned to `window.MAXNOW_LAST30_DATA`.

## Data Shape

Preserve this shape when possible:

```json
{
  "updatedAt": "YYYY-MM-DD HH:mm",
  "sourceSummary": "Last-30 rolling context",
  "today": {
    "date": "YYYY-MM-DD",
    "title": "最新发布",
    "summary": "一句话摘要。",
    "items": [
      {
        "date": "YYYY-MM-DD",
        "title": "短标题",
        "summary": "事实或低风险摘要。",
        "source": "Owner / GitHub / OpenClaw / Token / Server",
        "confidence": "high",
        "needsOwnerConfirm": false,
        "url": ""
      }
    ]
  },
  "week": {
    "range": "YYYY-MM-DD/YYYY-MM-DD",
    "title": "本周前沿",
    "summary": "一句话摘要。",
    "items": []
  },
  "last30": {
    "range": "YYYY-MM-DD/YYYY-MM-DD",
    "title": "近 30 天关键进展",
    "summary": "一句话摘要。",
    "mainlines": [],
    "decisions": [],
    "waiting": []
  }
}
```

Common item fields:

- `title`: short operational title
- `summary`: one concise sentence
- `source`: where the fact came from
- `confidence`: `high`, `medium`, or `low`
- `needsOwnerConfirm`: true when the item contains judgment, priority, intent, or unclear personal meaning
- `url`: optional supporting link

## Update Policy

Prefer automatic facts:

- official AI model/API/tool announcements
- GitHub releases for relevant AI developer tools
- high-signal Hacker News or public community links
- arXiv/research signals when relevant to agents, coding, models, or cost
- GDELT/free news index results when available
- already-collected candidates from `scripts/sync_ai_last30.py`

Visible output rules:

- Use Chinese fact titles and concrete Chinese summaries; brand names and product identifiers may stay in English.
- Prioritize official model launches, API/agent capability changes, pricing/access changes, major open-source releases, and material research results.
- Exclude customer stories, partnerships, generic enterprise adoption, education events, pure SDK version numbers, and updated-package releases.
- Deduplicate the same topic across latest, week, and 30-day groups.
- Never emit `active`, `自动归类`, `来源较稳`, `自动观察`, or generic advice such as `关注它的影响` as user-facing content.
- Preserve official links and optional `originalTitle` for traceability.

Be careful with judgments:

- Do not invent impact on the owner.
- Do not decide true priority for the owner.
- Do not mark a signal as important unless it has a clear relation to tools, models, agents, developer workflow, or cost.
- Use `needsOwnerConfirm: true` for inferred importance, uncertain impact, and subjective conclusions.

Keep arrays compact:

- `today.items`: 1-3
- `week.items`: 0-4
- `last30.mainlines`: 0-5
- `last30.decisions`: 0-6
- `last30.waiting`: 0-6

## Validation

Before finishing every routine update:

```bash
python -m json.tool dash/data/last-30.json >/dev/null
```

Regenerate the wrapper:

```bash
python -c "import json; from pathlib import Path; d=json.loads(Path('dash/data/last-30.json').read_text(encoding='utf-8')); Path('dash/data/last-30.js').write_text('window.MAXNOW_LAST30_DATA = '+json.dumps(d, ensure_ascii=True, indent=2)+';\n', encoding='ascii')"
```

If a source fails, keep the last safe value and add a short waiting item if the failure matters. Do not clear the file.

## Good Output Style

Use short factual Chinese inside JSON string fields. Prefer “OpenAI 正式发布 GPT-5.6” and “已向 ChatGPT、Codex 与 API 开放” over raw English titles or generic “建议关注” language. Avoid hype, long reports, and markdown.
