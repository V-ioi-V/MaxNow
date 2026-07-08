window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-08 23:42",
  "version": "1.0.0.45",
  "versionLabel": "v1.0.0.45",
  "branch": "feature/remove-home-journal",
  "commit": "9986633",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/remove-home-journal · commit 9986633 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-08",
      "title": "移除 Home 今日记录模块",
      "summary": "从 Home 左侧内容流移除“今日记录 / Daily Log”模块，避免静态项目原则被误认为当天真实日志。"
    },
    {
      "date": "2026-07-08",
      "title": "调整 Token 来源同步位置",
      "summary": "Token 页“各来源最后同步”改回显示具体时间 `YYYY-MM-DD HH:mm`，不再使用“今天 / 昨天 / X 分钟前”这类相对时间。"
    },
    {
      "date": "2026-07-08",
      "title": "移除 Home 稍后留意模块",
      "summary": "从 Home 左侧内容流移除“稍后留意 / Links”模块，避免 Roadmap 任务、服务器链路和文档入口重复占用首页空间。"
    },
    {
      "date": "2026-07-08",
      "title": "优化 Token 来源同步时间",
      "summary": "Token 页“各来源最后同步”从完整日期改为自然时间表达：刚同步显示“刚刚 / X 分钟前”，当天显示“今天 HH:mm”，昨天显示“昨天 HH:mm”，更早显示“M月D日 HH:mm”。"
    },
    {
      "date": "2026-07-08",
      "title": "调整 Home Todo 和 Token 长条布局",
      "summary": "将 Home 右侧 `Today Todo` 和 `Tokens` 从半宽 `widget-compact` 改为整行 `widget-wide`，让它们在右侧栈里上下显示为两个长条。"
    }
  ]
};
