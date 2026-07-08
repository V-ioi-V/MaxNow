window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-08 21:06",
  "version": "1.0.0.40",
  "versionLabel": "v1.0.0.40",
  "branch": "bugfix/home-fill-primary-lane",
  "commit": "fc85e25",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/home-fill-primary-lane · commit fc85e25 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-08",
      "title": "回填 Home 左侧内容流",
      "summary": "将最近更新、外部输入和稍后留意从右侧 widget 栈移回左侧 `home-lane-primary`，避免右侧一路下排时左列出现大面积空白。"
    },
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
    }
  ]
};
