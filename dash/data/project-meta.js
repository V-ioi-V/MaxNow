window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-10 23:17",
  "version": "1.0.3.04",
  "versionLabel": "v1.0.3.04",
  "branch": "feature/today-progress-ring",
  "commit": "44302a0",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/today-progress-ring · commit 44302a0 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-10",
      "title": "将 Today Status 时间轴改为圆形日进度",
      "summary": "用青色 24 小时圆形进度环替换竖向时间轴，环内显示今天已过去的整数百分比，当前时间单独显示在环外。"
    },
    {
      "date": "2026-07-10",
      "title": "精简 AI 前沿三栏栏头",
      "summary": "三栏只保留蓝色时间范围“最近 3 天 / 本周 / 近 30 天”，删除重复的黑色栏目名和栏目简介，新闻卡片直接接在时间范围下方。"
    },
    {
      "date": "2026-07-10",
      "title": "反转 Today Status 时间轴并校正信号节点",
      "summary": "Today Status 时间轴改为上方 `24:00`、下方 `00:00`，当前时间圆点与已过时间填充从下向上推进。"
    },
    {
      "date": "2026-07-10",
      "title": "完成 AI 前沿线上部署与旧规则清理",
      "summary": "线上部署目录从旧提交 `a19dad6` 快进到 `538dc40`，先备份并暂存服务器运行数据，再只恢复 dashboard、豆奶、行情、同行记和 Wiki Todo，未恢复旧 `ai-news.*` / `last-30.*`。"
    },
    {
      "date": "2026-07-10",
      "title": "将 Last-30 重构为中文 AI 前沿简报",
      "summary": "Home 原“外部输入”改为“AI 前沿”，三栏固定展示“最新发布 / 本周前沿 / 近 30 天关键进展”，只保留中文事实标题、具体变化、日期和来源。"
    }
  ]
};
