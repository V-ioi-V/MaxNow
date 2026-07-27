window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-27 20:09",
  "version": "1.0.5.18",
  "versionLabel": "v1.0.5.18",
  "branch": "feature/ballet-layout-priority",
  "commit": "7144dd5",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-layout-priority · commit 7144dd5 · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-07-27",
      "title": "修复卡片 hover 丢失语义底色",
      "summary": "根因是共享 hover 规则强制写入纯白背景，导致粉白、紫白、青白等轻主题卡在鼠标移入时突然变白；原本就是白底的条目则看不出变化，造成同页反馈不一致。"
    }
  ]
};
