window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-16 13:53",
  "version": "1.0.10.03",
  "versionLabel": "v1.0.10.03",
  "branch": "feature/ballet-booking-mini-timetable",
  "commit": "7cb4862",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-booking-mini-timetable · commit 7cb4862 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-08-16",
      "title": "收紧课程计划与代抢展示",
      "summary": "“课程计划”桌面改为课程预约占三分之一、抢课占三分之二，`860px` 以下继续单列，保留既有面板外壳与响应式边界。"
    },
    {
      "date": "2026-08-16",
      "title": "抢课结束后立即刷新芭蕾面板",
      "summary": "Fast Path systemd 单元增加成功与失败完成钩子；每次真实执行结束后立即启动既有 GET-only rolling 同步，让预约、候补、课程卡和课表状态尽快更新到 MaxNow 芭蕾面板。"
    },
    {
      "date": "2026-08-16",
      "title": "自动抢课改为长期周规则",
      "summary": "Owner 不再每周提供固定课表；Fast Path 每周日放课后动态扫描周一至周六，周一至周五只处理 18:40（含）后开始的课程，周六全天，周日不抢。"
    },
    {
      "date": "2026-08-14",
      "title": "校正 8 月 7 日课程老师",
      "summary": "Owner 将 2026-08-07 19:45–21:15 芭蕾 L1 的老师明确校正为“张瀚泽”；这条记录不再使用空老师默认李俊。"
    },
    {
      "date": "2026-08-14",
      "title": "统一实际上课历史的空老师口径",
      "summary": "Owner 确认闻道实际上课历史未填写老师时统一按“李俊”处理；明确填写的老师和 Owner 手工补录老师保持原值，未来课表、当前预约与候补不套用该默认值。"
    }
  ]
};
