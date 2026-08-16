window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-16 14:26",
  "version": "1.0.10.05",
  "versionLabel": "v1.0.10.05",
  "branch": "feature/ballet-course-plan-equal-columns",
  "commit": "80ef11e",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-course-plan-equal-columns · commit 80ef11e · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-08-16",
      "title": "课程预约与抢课恢复等宽",
      "summary": "“课程计划”桌面两栏从预约三分之一 / 抢课三分之二恢复为各占一半，`860px` 以下继续上下排列；微型代抢课表和上次结果课表的内容、状态与优先级保持不变。"
    },
    {
      "date": "2026-08-16",
      "title": "统一代抢与上次结果微型课表",
      "summary": "“代抢”微型课表重新收紧为居中日期、课程与时段的轻量网格，每节目标以 `8px` 小字标出实际 `优先 01–12` 执行顺序，周六仅保留低权重“周末优先”提示。"
    },
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
    }
  ]
};
