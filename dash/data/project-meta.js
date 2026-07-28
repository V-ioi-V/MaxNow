window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-29 00:12",
  "version": "1.0.7.16",
  "versionLabel": "v1.0.7.16",
  "branch": "bugfix/ballet-timetable-no-scroll",
  "commit": "87a1812",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/ballet-timetable-no-scroll · commit 87a1812 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-28",
      "title": "周课表取消内部滚动并完整平铺",
      "summary": "桌面周课表取消固定高度、sticky 表头和内部横纵滚动，全部小时列按内容区可用宽度弹性收缩，7 天课程直接平铺并让面板随内容自然增高。"
    },
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
    }
  ]
};
