window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-06 22:39",
  "version": "1.0.0.17",
  "versionLabel": "v1.0.0.17",
  "branch": "bugfix/unify-page-spacing",
  "commit": "8ab6784",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/unify-page-spacing · commit 8ab6784 · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-07-06",
      "title": "调整 Token 页头和范围切换位置",
      "summary": "将 Token 页 `1d / 7d / 30d / all` 范围切换移动到顶部栏右侧，只在 Token 页显示，和 Blog / 刷新入口同层。"
    },
    {
      "date": "2026-07-06",
      "title": "优化 Token 页头来源同步布局",
      "summary": "Token 页头左侧更新时间文案从“更新于”改为“总账合并于”，明确它表示 `token-usage.*` 总账合并时间。"
    }
  ]
};
