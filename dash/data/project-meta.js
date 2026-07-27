window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-27 20:39",
  "version": "1.0.5.19",
  "versionLabel": "v1.0.5.19",
  "branch": "feature/ballet-bookings-merge",
  "commit": "bee3c0a",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-bookings-merge · commit bee3c0a · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-27",
      "title": "合并下一节与所有预约",
      "summary": "删除独占整行且与列表重复的“下一节预约”卡，将“所有预约”移到芭蕾页顶部；列表第一条作为下一节，用浅粉背景和“下一节”标识突出，并保留取消截止时间。"
    },
    {
      "date": "2026-07-27",
      "title": "按使用优先级重排芭蕾页面",
      "summary": "页面顺序调整为：更新时间与下一节课 → 本周训练 / 课程卡 → 所有预约 → 上课统计 → 上课历史 → PHPSESSID 实验详情。"
    },
    {
      "date": "2026-07-27",
      "title": "删除芭蕾重复标题卡",
      "summary": "删除芭蕾内容区重复的 “Ballet Progress / 芭蕾 / 已同步”标题卡，只保留一行低权重数据更新时间。"
    },
    {
      "date": "2026-07-27",
      "title": "修正课程卡预测口径",
      "summary": "删除没有业务依据的固定“近 28 天节奏”：它会把开卡前日期当成未上课，还会让不同课程卡共享全局上课样本。"
    },
    {
      "date": "2026-07-27",
      "title": "补齐芭蕾只读训练闭环",
      "summary": "将“课前 N 小时可取消”按课程开课时间换算成真实绝对截止时间；无法解析时原样显示。候补课程在可用时展示“排队第 N 位”，不再只显示笼统的“排队中”。"
    }
  ]
};
