window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-09-13 16:13",
  "version": "1.0.11.28",
  "versionLabel": "v1.0.11.28",
  "branch": "bugfix/ballet-active-booking-pagination",
  "commit": "f451dd20",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "bugfix/ballet-active-booking-pagination · commit f451dd20 · 干净",
  "recentUpdates": [
    {
      "date": "2026-09-13",
      "title": "活动预约统一读取全部分页",
      "summary": "同步、实时查询和 Fast Path 写后复核统一调用活动预约分页读取器：先校验预约页声明的总数与固定 `newbookrecord` contract，再按已加载条数翻页、跨页合并去重，最后只读取预约 / 候补详情。"
    },
    {
      "date": "2026-09-13",
      "title": "抢课平均耗时与本次耗时分开展示",
      "summary": "“抢课助手”的“上次抢课耗时”改为“抢课平均耗时”，读取历次真实 Fast Path 执行关键路径耗时的平均值并显示累计样本数。"
    },
    {
      "date": "2026-09-13",
      "title": "周安排支持前后五周切换",
      "summary": "周安排从上周 / 本周 / 下周三档扩展为两周前 / 上周 / 本周 / 下周 / 两周后五档，默认仍定位本周，左右箭头在窗口两端自动禁用并同步更新无障碍说明。"
    },
    {
      "date": "2026-09-13",
      "title": "周六自动抢课收窄至 18:00 前",
      "summary": "Fast Path 新增周六结束门槛：只处理开课时间严格早于 18:00 的标准芭蕾 L1、L1.5 与精确“软开 / 软开课”，18:00 整及之后的周六课程一律排除。"
    },
    {
      "date": "2026-09-13",
      "title": "手动补录 9 月 13 日芭蕾 L1",
      "summary": "按 Owner 提供的课表截图，手动补录 `2026-09-13 10:00–11:30` 李俊老师大教室“芭蕾L1-入门”，记录状态为已上课，并使用 `manual` 稳定键保存在服务器私有上课台账中。"
    }
  ]
};
