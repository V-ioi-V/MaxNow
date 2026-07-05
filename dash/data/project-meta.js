window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-05 22:31",
  "version": "1.0.0.05",
  "versionLabel": "v1.0.0.05",
  "branch": "main",
  "commit": "f86b2e7",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "main · commit f86b2e7 · 干净",
  "recentUpdates": [
    {
      "date": "2026-07-05",
      "title": "将 Last-30 摘要改回 AI 大事口径",
      "summary": "`scripts/sync_ai_last30.py` 不再外露“适合进入近 30 天观察池”这类采集器内部筛选话术。"
    },
    {
      "date": "2026-07-05",
      "title": "收紧 Last-30 外露信息口径",
      "summary": "将 Last-30 左栏静态标签从 `Today` 改为 `Latest`，默认标题改为“最新信号”，避免最近 7 天回退数据被误读为当天信号。"
    },
    {
      "date": "2026-07-05",
      "title": "将本机 Codex 上报迁到专用 main clone",
      "summary": "新增本机专用上报目录 `D:\\Personal\\MaxNow-token-report`，该目录保持在 `main`，只供 `MaxNow-Local-Codex-Usage-Report` 计划任务运行。"
    },
    {
      "date": "2026-07-05",
      "title": "建立 MaxNow 版本提升规则",
      "summary": "将 `VERSION` 从 `1.0.0.00` 提升到 `1.0.0.01`，覆盖最近的云服务页重构和豆奶真实流量日结。"
    },
    {
      "date": "2026-07-05",
      "title": "确认 OpenClaw Token 用量定时任务已接入",
      "summary": "复查 root crontab 的 `MAXNOW-OPENCLAW-USAGE`，确认每天 00:20 运行 `python3 scripts/update_data.py openclaw-usage`。"
    }
  ]
};
