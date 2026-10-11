window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-10-11 15:58",
  "version": "1.0.11.68",
  "versionLabel": "v1.0.11.68",
  "branch": "feature/ballet-confirm-attendance",
  "commit": "2049c4b5",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-confirm-attendance · commit 2049c4b5 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-10-11",
      "title": "确认手动待上课为已完成",
      "summary": "Owner 确认 10 月 11 日 10:00–11:30 李俊老师大教室「芭蕾 L1 入门」已上完；复用既有 manual 稳定键，由 planned 改为 active / attended，不新增第二条记录。"
    },
    {
      "date": "2026-10-11",
      "title": "芭蕾统一刷新状态与减少课表请求",
      "summary": "实测页面同步 15:48:05–15:49:06 共 61 秒；顶部只保留一个状态，刷新时显示已等待时分秒，完成恢复已同步，失败显示刷新失败。取消重复状态和弹出通知；静态数据重新渲染不得覆盖正在刷新的状态，六分钟等待上限后明确报超时。"
    },
    {
      "date": "2026-10-11",
      "title": "芭蕾进入页面自动同步与手动整体刷新",
      "summary": "每次打开芭蕾页面或从其他页面进入时，自动同步课程卡、预约 / 候补、上课历史和课表；右上角刷新按钮触发同一同步，完成后重新读取全部芭蕾展示源。过程中保留最后成功数据，状态区显示刷新中 / 已刷新 / 刷新失败。"
    },
    {
      "date": "2026-10-11",
      "title": "接入多卡顺延与单次自动激活",
      "summary": "普通约课与周日 Fast Path 共用选卡：真实到期日由近到远，明确规则拦截后换卡；每次预约前重检，避免先前预约占用旧卡额度。"
    },
    {
      "date": "2026-10-11",
      "title": "确认多卡约课与自动激活规则",
      "summary": "使用中适用卡按最早到期 → 第二早到期 → 最晚到期逐卡预检；明确不可约才在提交前顺延，同到期日优先剩余课次少的卡。"
    }
  ]
};
