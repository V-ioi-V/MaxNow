window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-29 23:11",
  "version": "1.0.7.35",
  "versionLabel": "v1.0.7.35",
  "branch": "bugfix/ballet-waitlist-position-teacher",
  "commit": "6c982a6",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/ballet-waitlist-position-teacher · commit 6c982a6 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-29",
      "title": "补齐本人候补位次与紧凑课程老师",
      "summary": "周课表把预约快照中的本人候补序号匹配回对应课程，状态由笼统的 `排队中` 改为 `排队中 N`；该数字只表示 Owner 本人的候补位次，与人数行的全班 `Wait` 排队数保持独立。"
    },
    {
      "date": "2026-07-29",
      "title": "疏开课表课程卡信息",
      "summary": "课程卡改为“课程名 → 人数 → 老师 → 时间 / 状态”四层结构；报名 / 容量和排队数使用独立人数行，老师另起弱信息行，时间与状态保留在底部，不再把人数、排队和老师挤成一串。"
    },
    {
      "date": "2026-07-29",
      "title": "课表显示报名与排队人数",
      "summary": "闻道课表解析增加独立 `waitlistCount` 脱敏字段，与现有报名数 / 容量一起进入只读快照；排队人数只读取源站 `Wait` 数字，不再用报名数减容量推断。"
    },
    {
      "date": "2026-07-29",
      "title": "柔化课表日期分界",
      "summary": "撤销贯穿课表全高的 `2px` 玫瑰粗线；日期边界和教室边界统一回到 `1px`，仅用暖灰粉深浅区分两级分组，让课表更接近日历而不是表格。"
    },
    {
      "date": "2026-07-29",
      "title": "加强课表每天之间的分界",
      "summary": "桌面周课表把每天开始位置的竖向分界线加深并增为 `2px`；同一天大教室 / 小教室之间继续使用浅色 `1px` 细线，日期和教室形成明确的两级分组。"
    }
  ]
};
