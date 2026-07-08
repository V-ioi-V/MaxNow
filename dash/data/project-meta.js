window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-08 15:21",
  "version": "1.0.0.31",
  "versionLabel": "v1.0.0.31",
  "branch": "bugfix/market-indices-tencent",
  "commit": "0de955e",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/market-indices-tencent · commit 0de955e · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-08",
      "title": "修正 Home 市场涨幅数据源",
      "summary": "将市场涨幅同步切到腾讯公开行情接口，服务器可同时刷新国内和美股指数 quote 与分钟线。"
    },
    {
      "date": "2026-07-08",
      "title": "新增 Home 市场涨幅卡",
      "summary": "Home 主内容区顶部改为 Token 热力格 + 市场涨幅双列，右侧展示纳指100、标普500、上证指数、深证成指和创业板指。"
    },
    {
      "date": "2026-07-08",
      "title": "优化 Dash 首屏加载链路",
      "summary": "Dash 首屏不再同步加载 `dash/data/*.js` wrapper，也不再等待 Token、同行记、生活页等隐藏视图数据后才渲染 Home。"
    },
    {
      "date": "2026-07-08",
      "title": "将 Today Status 改为自动态势",
      "summary": "Home 顶部 Today Status 不再依赖过期 `dashboard.json.today` 手填字段作为主状态，改为基于今日 Todo、自动化状态、当前时段、ROADMAP 和 Token 活跃自动生成模式、节奏、焦点和摘要。"
    },
    {
      "date": "2026-07-07",
      "title": "收窄今日 Todo 日期口径",
      "summary": "今日 Todo 只展示 `due_at` 等于浏览器当天日期的未完成待办，不再混入过期未完成项。"
    }
  ]
};
