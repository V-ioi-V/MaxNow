window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-23 16:07",
  "version": "1.0.10.28",
  "versionLabel": "v1.0.10.28",
  "branch": "bugfix/ballet-hour-card-density",
  "commit": "2e337f2",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "bugfix/ballet-hour-card-density · commit 2e337f2 · 干净",
  "recentUpdates": [
    {
      "date": "2026-08-23",
      "title": "放松一小时课程卡的排版密度",
      "summary": "本周课程表不再把完整 60 分钟课程压成短课紧凑模式，并适度放大宽屏分钟刻度；一小时课程获得约 `99px` 的真实高度并恢复标准字号、内边距和状态信息层级，只有不足 60 分钟的课程继续使用紧凑排版，长空档仍按原规则压缩。"
    },
    {
      "date": "2026-08-23",
      "title": "统一隐藏周安排课程人数",
      "summary": "“课程计划 / 周安排”中的真实预约与候补课程卡统一隐藏报名人数、容量和全班候补人数，只保留课程、老师、时间及个人预约 / 候补状态；下方完整课程表继续正常展示人数统计。"
    },
    {
      "date": "2026-08-23",
      "title": "修复分批放课漏课并优化整批抢课流水线",
      "summary": "Fast Path 不再在日期页出现任意目标后停止刷新：第一轮课表完成后立即串行处理已发现 L1，同时在放课后第 2 / 6 / 10 秒以最多 2 路只读 GET 后台刷新六个日期；稳定快照补入稍后发布的课程后，再保持 `L1 → L1.5 → 软开` 完成整批提交。"
    },
    {
      "date": "2026-08-23",
      "title": "补抢漏掉的周六 L1.5 并刷新芭蕾数据",
      "summary": "对 2026-08-29 15:30–17:00 徐老师大教室「芭蕾L1.5 - 入门+」完成实时唯一匹配 dry-run，确认 `status=ready`、`mutationAttempts=0` 后按 Owner 授权提交一次；runner 返回 `status=booked`、`bookingStatus=booked`、`mutationAttempts=1`，独立实时预约查询再次确认成功。"
    },
    {
      "date": "2026-08-23",
      "title": "自动抢课加入芭蕾 L1.5",
      "summary": "在现有长期周规则中加入全部标准芭蕾 L1.5，课程优先级调整为 `芭蕾 L1 > 芭蕾 L1.5 > 软开 / 软开课`。"
    }
  ]
};
