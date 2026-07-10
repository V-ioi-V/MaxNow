window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-10 09:12",
  "version": "1.0.0.48",
  "versionLabel": "v1.0.0.48",
  "branch": "bugfix/today-progress-time-overlap",
  "commit": "8898097",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/today-progress-time-overlap · commit 8898097 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-10",
      "title": "修复 Today Status 当前时间与进度轴重叠",
      "summary": "将 00:00、当前时间和 24:00 的右边缘统一锚定在进度轴左侧，并为当前时间与进度圆点保留固定间距。"
    },
    {
      "date": "2026-07-09",
      "title": "替换 Home 顶部状态小卡",
      "summary": "Home 顶部状态条前两张小卡从“当前主线 / 待推进”改为“今日执行 / 数据同步”。"
    },
    {
      "date": "2026-07-08",
      "title": "将 Today Status 竖线改为今日时间轴",
      "summary": "Today Status 右侧竖线改为按 00:00-24:00 推进的今日进度轴，显示 00:00、当前时间和 24:00。"
    },
    {
      "date": "2026-07-08",
      "title": "移除 Home 今日记录模块",
      "summary": "从 Home 左侧内容流移除“今日记录 / Daily Log”模块，避免静态项目原则被误认为当天真实日志。"
    },
    {
      "date": "2026-07-08",
      "title": "调整 Token 来源同步位置",
      "summary": "Token 页“各来源最后同步”改回显示具体时间 `YYYY-MM-DD HH:mm`，不再使用“今天 / 昨天 / X 分钟前”这类相对时间。"
    }
  ]
};
