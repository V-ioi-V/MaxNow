window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-31 22:47",
  "version": "1.0.11.14",
  "versionLabel": "v1.0.11.14",
  "branch": "feature/weekly-training-heatmap",
  "commit": "8084329a",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/weekly-training-heatmap · commit 8084329a · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-08-31",
      "title": "全部训练记录改为每周热力图",
      "summary": "“全部”范围把辨识度较低的历年单点折线改为周一至周日聚合的热力图，按年份分组并补齐首个训练周到最近成功同步周之间的零课周。"
    },
    {
      "date": "2026-08-26",
      "title": "周安排不再回填已取消课程的旧抢课状态",
      "summary": "周安排比较芭蕾业务快照与 Fast Path 上次执行时间；当 `ballet.json` 已有更晚的成功同步时，预约、候补、完成与取消状态统一以该业务快照为准。"
    },
    {
      "date": "2026-08-25",
      "title": "最近课程改用深色卡面并让标签按整卡居中",
      "summary": "课程预约右侧标签组改为跨越课程信息与取消提示两行，桌面端以整张课程小卡为基准上下居中；预约 / 候补与级别标签继续保持横向单排。"
    },
    {
      "date": "2026-08-25",
      "title": "课程预约标签单行居中",
      "summary": "课程预约小卡右侧的“最近一节”、预约 / 候补状态与课程级别标签统一保持横向单排，不再让稍长的候补排位标签独占一行。"
    },
    {
      "date": "2026-08-25",
      "title": "居中课程预约日期轨道",
      "summary": "课程预约日期大卡左侧的 `M.D / 星期` 改为在日期轨道内水平、垂直居中，不再贴近左边；`560px` 以下日期移到课程上方后，日期与星期继续作为一组居中。"
    }
  ]
};
