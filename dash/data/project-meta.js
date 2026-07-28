window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-28 19:37",
  "version": "1.0.7.05",
  "versionLabel": "v1.0.7.05",
  "branch": "bugfix/remove-cloud-page-head",
  "commit": "9ed16c8",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/remove-cloud-page-head · commit 9ed16c8 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-28",
      "title": "移除 Cloud 重复页头",
      "summary": "删除 Cloud 内容区重复的“Cloud Services / 云服务 / dash.maxnow.cn”标题卡，进入页面后直接展示“系统与托管”，释放首屏高度；同步清理专用样式和页面协议。样式缓存提升到 `styles.css?v=162`，版本提升到 `1.0.7.05`。"
    },
    {
      "date": "2026-07-28",
      "title": "收紧 Cloud 芭蕾运维卡布局",
      "summary": "“芭蕾自动抢课”与“芭蕾 Session 实验”在宽桌面改为左右各半宽并排；Session 展开后仍留在右侧半列，`1320px` 以下继续自然堆叠。样式缓存提升到 `styles.css?v=161`，版本提升到 `1.0.7.04`。"
    },
    {
      "date": "2026-07-28",
      "title": "收敛芭蕾模块信息架构",
      "summary": "芭蕾页按学习决策顺序重排为“下一节 + 本周训练 → 课程计划 → 本周课程表 → 训练记录 → 课程卡”；正式预约 / 候补与周日待抢目标、逐课结果合并进课程计划。"
    },
    {
      "date": "2026-07-28",
      "title": "记录芭蕾分享图待办",
      "summary": "芭蕾 Later 新增分享图功能：从现有脱敏数据选择下一节、本周训练、阶段节数 / 时长、主要课型和近期记录等关键信息，浏览器本地生成可预览、可下载的图片。"
    },
    {
      "date": "2026-07-28",
      "title": "自动抢课改为逐课独立并增加安全重试",
      "summary": "周日 fast path 将三节目标拆为独立失败域：第一节课程级失败或预约结果未知不会阻止第二、第三节；只有登录失效、配置错误或闻道页面协议变化才全局停止。"
    }
  ]
};
