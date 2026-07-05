window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-05 23:07",
  "version": "1.0.0.06",
  "versionLabel": "v1.0.0.06",
  "branch": "main",
  "commit": "72209dc",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "main · commit 72209dc · 干净",
  "recentUpdates": [
    {
      "date": "2026-07-05",
      "title": "优化 Token 数值单位进位",
      "summary": "Token 页总量、来源、模型、会话和趋势图统一使用同一个数值格式化规则。"
    },
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
    }
  ]
};
