window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-27 15:19",
  "version": "1.0.5.10",
  "versionLabel": "v1.0.5.10",
  "branch": "feature/ballet-booking-status-colors",
  "commit": "d3fee11",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-booking-status-colors · commit d3fee11 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-27",
      "title": "区分预约状态颜色并重排星期",
      "summary": "“所有预约”中的“已预约”保留粉玫瑰色，“排队中”改用橙色，候补状态不再与正式预约使用相同颜色。"
    },
    {
      "date": "2026-07-27",
      "title": "压缩下一节预约并移入芭蕾页头",
      "summary": "将独占整行的“下一节预约”大卡移入芭蕾页头右半区；桌面端标题与课程各占约 1/2，保留日期、时间、课程、老师、级别和预约状态。"
    },
    {
      "date": "2026-07-27",
      "title": "修复排队课程未进入所有预约",
      "summary": "实时只读诊断确认闻道约课列表完整返回 3 条“已预约”、1 条“排队中”和 1 条“已上课”；排队课程详情页的状态实际为“等候中, 排队序号 4”，旧归一化因只接受精确的“排队中 / 候补中”而将其过滤。"
    },
    {
      "date": "2026-07-27",
      "title": "重做芭蕾预约与上课统计",
      "summary": "“后续预约”改为“所有预约”，完整列出所有尚未上课的已预约 / 排队中课程，包括下一节主卡中的课程；已结束或已取消课程不进入该列表。"
    },
    {
      "date": "2026-07-27",
      "title": "部署多节预约并完成首次真实同步",
      "summary": "服务器已快进到 `e5d10258`，上线“下一节预约 + 后续预约”展示；部署前完整备份运行时数据并恢复非项目元信息数据，服务器 Git remote 从失效的 SSH 地址切回与现有 `gh` 登录一致的 HTTPS。"
    }
  ]
};
