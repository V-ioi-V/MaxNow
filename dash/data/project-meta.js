window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-28 20:25",
  "version": "1.0.7.10",
  "versionLabel": "v1.0.7.10",
  "branch": "feature/indefinite-ballet-session",
  "commit": "055f118",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/indefinite-ballet-session · commit 055f118 · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-07-28",
      "title": "预约列表显示教室",
      "summary": "芭蕾“下一节”和“所有预约”的课程信息行在时间、老师后补充闻道同步的教室，例如“大教室 / 小教室”；源数据缺失时不猜测、不显示空占位。脚本缓存提升到 `app.js?v=136`，版本提升到 `1.0.7.07`。"
    },
    {
      "date": "2026-07-28",
      "title": "默认展开 Cloud Session 实验",
      "summary": "Cloud 的“芭蕾 Session 实验”改为默认展开，进入页面即可直接看到有效时长、检查时间、间隔和实验状态，不再因同排等高留下空白半卡；仍保留手动收起能力。版本提升到 `1.0.7.06`。"
    }
  ]
};
