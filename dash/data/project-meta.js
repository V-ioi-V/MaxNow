window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-28 22:16",
  "version": "1.0.7.12",
  "versionLabel": "v1.0.7.12",
  "branch": "feature/ballet-sync-1430",
  "commit": "07de3d1",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-sync-1430 · commit 07de3d1 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-28",
      "title": "错开周日只读同步与自动抢课",
      "summary": "芭蕾 rolling 只读同步由周日 14:20 调整为 14:30，避开 14:19:35 预热与 14:20:00 自动抢课关键窗口；每日 00:00、每月 1 日 00:47 和自动抢课时间保持不变。"
    },
    {
      "date": "2026-07-28",
      "title": "课程表适配约三分之二屏宽",
      "summary": "芭蕾 7 天周课表在 `861px–1500px` 视口收紧时间列、日期列最小宽度和网格间距，使约 `1280px–1365px` 的窗口无需横向滚动即可完整查看；8 天等超额日期仍保留面板内部滚动，`860px` 以下继续使用逐日列表。"
    },
    {
      "date": "2026-07-28",
      "title": "Session 探针改为无限期运行",
      "summary": "闻道 Session 探针新增 `WENDA_DURATION_SECONDS=0` 无限调度模式；2026-07-28 20:23 在首轮 HTTP 200 / authenticated 验证成功后，从 v6 平滑交接到 v7，移除 systemd 运行时上限和计划结束时间。身份失效或连续 3 次未知 / 网络异常仍安全停止，服务器重启后仍不自动恢复。"
    },
    {
      "date": "2026-07-28",
      "title": "压缩并下移本周课程表",
      "summary": "“本周课程表”移到芭蕾页最底部，桌面网格限制在约 `58vh` 内并固定日期行 / 时间列，移动端逐日列表也限制内部高度，减少单个课表撑满整页。"
    },
    {
      "date": "2026-07-28",
      "title": "重排芭蕾顶部概览并突出最近课程",
      "summary": "删除独立“下一节”面板，顶部改为“本周训练 / 课程卡”左右等分；课程卡从页面底部移入右侧，并改为适合半宽的纵向信息布局。"
    }
  ]
};
