window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-10-12 22:09",
  "version": "1.0.11.82",
  "versionLabel": "v1.0.11.82",
  "branch": "bugfix/ballet-l2-second-pass",
  "commit": "34ebc374",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/ballet-l2-second-pass · commit 34ebc374 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-10-12",
      "title": "L2 在全周 L1.5 / 软开之后处理",
      "summary": "按 Owner 明确的两轮顺序：第一轮周一 L1.5 → 软开、周二 L1.5 → 软开，依次至周六；全部轮完后第二轮周一至周六 L2。执行配置新增 deferredCourses，并将轮次置于日期之前排序，避免周一 L2 提前于后续日期的 L1.5 / 软开。"
    },
    {
      "date": "2026-10-12",
      "title": "抢课日期按周一至周六顺序",
      "summary": "Owner 将日期优先级改为周一 → 周二 → 周三 → 周四 → 周五 → 周六；首轮只允许周一 L1.5 提前提交，其余课型 / 日期等待发现窗口结束。每日 L1.5 → 软开 / 软开课 → L2、老师平等、旧卡顺延、时间限制和提交保护不变。"
    },
    {
      "date": "2026-10-12",
      "title": "抢课课型与日期优先级调整",
      "summary": "长期目标改为每天 L1.5 → 软开 / 软开课 → L2，移除 L1；周六优先，工作日按周一至周五的日期顺序处理。所有老师平等，未标注老师也不归入李俊优先；同一天同课型按开始时间，同名同时段仍按大教室优先 / 小教室兜底并唯一匹配。"
    },
    {
      "date": "2026-10-12",
      "title": "周二三课取消并重新预约 L2",
      "summary": "按 Owner 红框精确取消 10 月 13 日李俊 / 大教室 18:45–19:45 软开候补、19:45–21:15 L1 预约，以及张瀚泽 / 小教室 18:45–20:15 L2 预约。三次 dry-run 均 ready / mutationAttempts=0，逐课各一次取消并独立实时查询确认消失。"
    },
    {
      "date": "2026-10-11",
      "title": "豆奶功能下线",
      "summary": "按 Owner 要求删除豆奶 tab、首页摘要、专用页面 / 样式、数据加载、健康来源及数据文件；旧链接回首页并清除原浏览器缓存。同步移除 Cloud 采集任务说明和 OpenClaw 数据写入授权。"
    }
  ]
};
