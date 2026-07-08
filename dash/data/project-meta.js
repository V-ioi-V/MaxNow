window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-08 20:55",
  "version": "1.0.0.39",
  "versionLabel": "v1.0.0.39",
  "branch": "main",
  "commit": "8763e91",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "main · commit 8763e91 · 干净",
  "recentUpdates": [
    {
      "date": "2026-07-08",
      "title": "标准化 Home Widget 尺寸",
      "summary": "Home 右侧 `home-side-stack` 从单列大卡改为 widget 网格：`widget-compact` 占半宽，`widget-wide` / `wide-*` / `mid-*` 占满右列。"
    },
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
    }
  ]
};
