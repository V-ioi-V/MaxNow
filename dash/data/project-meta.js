window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-28 23:53",
  "version": "1.0.7.15",
  "versionLabel": "v1.0.7.15",
  "branch": "feature/ballet-timetable-gap-compression",
  "commit": "5f6f7f5",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-timetable-gap-compression · commit 5f6f7f5 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-28",
      "title": "周课表改为一小时时段并压缩空档",
      "summary": "桌面周课表横轴由零散开始时间改为固定一小时段，课程按开始时间归入对应小时；同一天同一小时内的多节课程改为上下排列。"
    },
    {
      "date": "2026-07-28",
      "title": "转置并恢复全宽周课表",
      "summary": "桌面周课表恢复为内容区全宽，横轴改为课程开始时间，纵轴改为星期与日期；时间表头行和星期日期首列保持固定，多时间列只在课表面板内部滚动。"
    },
    {
      "date": "2026-07-28",
      "title": "修正课表宽度、表头与同时间课程布局",
      "summary": "`1501px` 以上把本周课程表收为内容区约三分之二宽，`861px–1500px` 继续使用全宽保证 7 天完整显示，`860px` 以下保持逐日列表。"
    },
    {
      "date": "2026-07-28",
      "title": "错开周日只读同步与自动抢课",
      "summary": "芭蕾 rolling 只读同步由周日 14:20 调整为 14:30，避开 14:19:35 预热与 14:20:00 自动抢课关键窗口；每日 00:00、每月 1 日 00:47 和自动抢课时间保持不变。"
    },
    {
      "date": "2026-07-28",
      "title": "课程表适配约三分之二屏宽",
      "summary": "芭蕾 7 天周课表在 `861px–1500px` 视口收紧时间列、日期列最小宽度和网格间距，使约 `1280px–1365px` 的窗口无需横向滚动即可完整查看；8 天等超额日期仍保留面板内部滚动，`860px` 以下继续使用逐日列表。"
    }
  ]
};
