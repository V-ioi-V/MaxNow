window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-05 21:00",
  "version": "1.0.0.03",
  "versionLabel": "v1.0.0.03",
  "branch": "bugfix/local-token-server-meta-stash",
  "commit": "cab496c",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/local-token-server-meta-stash · commit cab496c · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-07-05",
      "title": "移除云服务页定时任务分组标题",
      "summary": "移除云服务页“Cron Jobs / 定时任务”中段标题，让任务卡自然接在“系统与托管”卡后面，减少页面断层感。"
    },
    {
      "date": "2026-07-05",
      "title": "清理服务器资源和 Chromium 重启风暴",
      "summary": "停止并禁用失败循环的 `lighthouse-chromium.service`，该服务每 3 秒尝试启动 Chromium 但因 `/root/.openclaw/browser-existing-session/SingletonLock` 已被现有 OpenClaw 浏览器会话占用而退出。"
    }
  ]
};
