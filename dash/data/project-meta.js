window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-08 17:11",
  "version": "1.0.0.34",
  "versionLabel": "v1.0.0.34",
  "branch": "bugfix/home-fill-token-column-gap",
  "commit": "dd81718",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/home-fill-token-column-gap · commit dd81718 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-08",
      "title": "填补 Home Token 热力格下方空白",
      "summary": "Home 顶部主内容改为左侧 Token 热力格 + Personal Wiki 近期待办竖向栈、右侧市场涨幅卡，避免市场卡撑高整行后左侧出现大面积空白。"
    },
    {
      "date": "2026-07-08",
      "title": "调整 Home Token 热力格为 90 天",
      "summary": "Home Token 活动热力格从近 180 天改回近 90 天，保持 3 行展示，避免左侧卡片内格子过小。"
    },
    {
      "date": "2026-07-08",
      "title": "修正 Token 范围切换 fallback",
      "summary": "Token 页不再回退到 `dashboard.json.tokenUsage` 里的旧模拟范围，避免真实总账加载前显示过期的中文小时范围。"
    },
    {
      "date": "2026-07-08",
      "title": "修正 Home 市场涨幅数据源",
      "summary": "将市场涨幅同步切到腾讯公开行情接口，服务器可同时刷新国内和美股指数 quote 与分钟线。"
    },
    {
      "date": "2026-07-08",
      "title": "新增 Home 市场涨幅卡",
      "summary": "Home 主内容区顶部改为 Token 热力格 + 市场涨幅双列，右侧展示纳指100、标普500、上证指数、深证成指和创业板指。"
    }
  ]
};
