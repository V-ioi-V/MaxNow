window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-27 15:45",
  "version": "1.0.5.12",
  "versionLabel": "v1.0.5.12",
  "branch": "feature/ballet-center-deploy-record",
  "commit": "04d6413",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-center-deploy-record · commit 04d6413 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-27",
      "title": "居中芭蕾下一节预约内容",
      "summary": "将右侧“下一节预约”tab 的标题与“日期 + 课程信息”内容组整体横向居中，状态 pill 继续固定在右上角，减少内容偏左造成的空洞感。"
    },
    {
      "date": "2026-07-27",
      "title": "将芭蕾顶部改为两个独立等宽 tab",
      "summary": "修正此前对“各占一半”的理解：芭蕾标题与“下一节预约”改为两个同级独立 tab，不再把课程模块嵌套在标题卡内部。"
    },
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
    }
  ]
};
