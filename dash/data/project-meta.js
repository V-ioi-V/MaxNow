window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-07 11:41",
  "version": "1.0.0.19",
  "versionLabel": "v1.0.0.19",
  "branch": "main",
  "commit": "fd53256",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "main · commit fd53256 · 干净",
  "recentUpdates": [
    {
      "date": "2026-07-07",
      "title": "将 Token 趋势改为活动热力格",
      "summary": "将 Token 页底部“最近 30 天”折线图替换为近 12 个自然月的 Token 活动热力格，按月份铺开每日格子。"
    },
    {
      "date": "2026-07-07",
      "title": "修复 OpenClaw Token 来源回退为空",
      "summary": "复查发现线上 `openclaw-usage.*` 被仓库中的空基线覆盖，导致统一 `token-usage.*` 只剩 Codex 来源，Token 页来源费用面板过滤掉 0 用量的 OpenClaw。"
    },
    {
      "date": "2026-07-06",
      "title": "统一 Dash 页面主间距",
      "summary": "新增 Dash 页面级 spacing 变量，统一主内容页边距、模块间距和同层卡片 grid gap。"
    },
    {
      "date": "2026-07-06",
      "title": "拆开 Token 页头信息 tab",
      "summary": "将 Token 页头外层从白底大卡改为透明 grid 容器，让“Token 用量”和“各来源最后同步”成为两张真正独立的同级 tab 卡片。"
    },
    {
      "date": "2026-07-06",
      "title": "修复 Windows Codex 用量自动上报",
      "summary": "修复 `D:\\Personal\\MaxNow-token-report` 专用 clone 直连 GitHub 时 `git pull` 卡住或连接重置的问题：为该 clone 补齐 repo-local `http.proxy` / `https.proxy` 到 `http://127.0.0.1:7897`。"
    }
  ]
};
