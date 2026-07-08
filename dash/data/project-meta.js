window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-08 20:19",
  "version": "1.0.0.38",
  "versionLabel": "v1.0.0.38",
  "branch": "bugfix/home-two-column-layout",
  "commit": "fc84d76",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/home-two-column-layout · commit fc84d76 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-08",
      "title": "改为 Home 两列主版式",
      "summary": "Home 主内容从三列视觉布局调整为两列外壳：左列承载个人主任务，右列用 `home-side-stack` 纵向承载市场 / 用量 / 更新和 Todo / 豆奶 / 系统状态。"
    },
    {
      "date": "2026-07-08",
      "title": "调整 Home 顶部左右比例",
      "summary": "收窄 Home 顶部 Today Status 卡片的横向占比，提高右侧天气卡和小日历 widget 组的桌面最小宽度。"
    },
    {
      "date": "2026-07-08",
      "title": "修正 Home Board 三 lane 版式",
      "summary": "Home 状态条下方从单张跨行 `grid-template-areas` 网格改为 `home-lane-primary` / `home-lane-signal` / `home-lane-rail` 三条独立纵向 lane，避免高卡把同一行短卡撑出大块空白。"
    },
    {
      "date": "2026-07-08",
      "title": "统一 Home Board 版式规则",
      "summary": "Home 状态条下方改为统一 `home-board`：Token、市场、今日 Todo、Personal Wiki、豆奶、待推进、近期用量、外部输入、最近更新、今日记录、稍后留意和系统状态都在同一个响应式网格里声明位置。"
    },
    {
      "date": "2026-07-08",
      "title": "填补 Home Token 热力格下方空白",
      "summary": "Home 顶部主内容改为左侧 Token 热力格 + Personal Wiki 近期待办竖向栈、右侧市场涨幅卡，避免市场卡撑高整行后左侧出现大面积空白。"
    }
  ]
};
