window.MAXNOW_CODEX_USAGE_DATA = {
  "updatedAt": "2026-10-26 10:32",
  "timezone": "Asia/Shanghai",
  "currency": "USD",
  "pricingBasis": "openai-api-equivalent",
  "pricingSource": "openai-api-pricing",
  "pricingStale": false,
  "sinceDays": 3650,
  "summary": {
    "inputTokens": 5550498,
    "outputTokens": 16621,
    "cacheReadTokens": 5434368,
    "cacheBaseTokens": 5550498,
    "totalTokens": 5567119,
    "estimatedCostUsd": 3.796464,
    "runs": 1,
    "activeSeconds": 717,
    "completedTurns": 2
  },
  "sources": [
    {
      "key": "codex-windows",
      "label": "Codex Windows",
      "inputTokens": 5550498,
      "outputTokens": 16621,
      "cacheReadTokens": 5434368,
      "cacheBaseTokens": 5550498,
      "totalTokens": 5567119,
      "estimatedCostUsd": 3.796464,
      "runs": 1,
      "activeSeconds": 717,
      "completedTurns": 2
    }
  ],
  "days": [
    {
      "date": "2026-10-25",
      "sources": [
        "codex-windows"
      ],
      "inputTokens": 5550498,
      "outputTokens": 16621,
      "cacheReadTokens": 5434368,
      "cacheBaseTokens": 5550498,
      "totalTokens": 5567119,
      "estimatedCostUsd": 3.796464,
      "runs": 1,
      "activeSeconds": 717,
      "completedTurns": 2,
      "byModel": [
        {
          "model": "gpt-5.5",
          "provider": "openai",
          "openrouterModel": null,
          "inputTokens": 5550498,
          "outputTokens": 16621,
          "cacheReadTokens": 5434368,
          "cacheBaseTokens": 5550498,
          "totalTokens": 5567119,
          "estimatedCostUsd": 3.796464,
          "runs": 1,
          "activeSeconds": 717,
          "completedTurns": 2,
          "pricingEstimated": true,
          "pricingModel": "gpt-5.5"
        }
      ],
      "byTask": [
        {
          "kind": "codex-session",
          "label": "MaxNow",
          "model": "gpt-5.5",
          "inputTokens": 5550498,
          "outputTokens": 16621,
          "cacheReadTokens": 5434368,
          "cacheBaseTokens": 5550498,
          "totalTokens": 5567119,
          "estimatedCostUsd": 3.796464,
          "runs": 1,
          "activeSeconds": 717,
          "completedTurns": 2,
          "pricingEstimated": true,
          "pricingModel": "gpt-5.5"
        }
      ],
      "pricingEstimated": true
    }
  ],
  "recentRuns": [
    {
      "date": "2026-10-25",
      "timestamp": "2026-10-25T20:14:38+08:00",
      "source": "codex-windows",
      "provider": "openai",
      "model": "gpt-5.5",
      "openrouterModel": null,
      "sessionId": "01a172f1-0695-7f23-bc6c-3773759366f6",
      "runId": "01a172f1-0695-7f23-bc6c-3773759366f6:2026-10-25",
      "kind": "codex-session",
      "label": "MaxNow",
      "inputTokens": 5550498,
      "outputTokens": 16621,
      "cacheReadTokens": 5434368,
      "cacheBaseTokens": 5550498,
      "reasoningOutputTokens": 3274,
      "totalTokens": 5567119,
      "pricingEstimated": true,
      "pricingModel": "gpt-5.5",
      "contextWindow": 475000,
      "tokenCountEvents": 57,
      "activeSeconds": 717,
      "completedTurns": 2,
      "activeByDate": [
        {
          "date": "2026-10-25",
          "activeSeconds": 717,
          "completedTurns": 2
        }
      ],
      "estimatedCostUsd": 3.796464
    }
  ],
  "pricingSnapshot": [
    {
      "model": "gpt-5.4",
      "pricing": {
        "input": 2.5,
        "cachedInput": 0.25,
        "output": 15.0
      }
    },
    {
      "model": "gpt-5.4-mini",
      "pricing": {
        "input": 0.75,
        "cachedInput": 0.075,
        "output": 4.5
      }
    },
    {
      "model": "gpt-5.5",
      "pricing": {
        "input": 5.0,
        "cachedInput": 0.5,
        "output": 30.0
      }
    }
  ],
  "notes": [
    "Codex usage is collected as per-event deltas from local session token_count events.",
    "Inherited history in forked session files is deduplicated within each session tree.",
    "Active time is the sum of completed task duration_ms values; idle time between turns is excluded.",
    "No prompt or response body is exported into this ledger.",
    "estimatedCostUsd is an OpenAI API-equivalent estimate, not an actual Codex subscription bill."
  ],
  "sourcePath": "C:\\Users\\a\\.codex"
};
