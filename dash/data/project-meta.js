window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-11-23 10:43",
  "version": "1.0.12.11",
  "versionLabel": "v1.0.12.11",
  "branch": "codex/remove-server-codex-cli",
  "commit": "acd0382d",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "codex/remove-server-codex-cli · commit acd0382d · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-11-23",
      "title": "停用服务器 Codex CLI 和用量采集",
      "summary": "服务器 Codex CLI 已退出登录并卸载。移除手动采集入口和云服务页的任务卡片，每小时源采集仅刷新 OpenClaw，历史 Codex Server 用量继续纳入总账。版本 `1.0.12.11`。"
    },
    {
      "date": "2026-11-23",
      "title": "周安排补齐课表悬停信息",
      "summary": "周安排复用完整课程表的浮层，显示同一节课的课程信息、报名人数、容量、排队人数和报名头像。版本 `1.0.12.10`。"
    },
    {
      "date": "2026-11-22",
      "title": "课表悬停查看课程信息和报名头像",
      "summary": "课程卡停留 0.5 秒后显示时间、老师、教室和报名状态。提示条下方展示同一节课的闻道报名头像，无头像数据时显示课程信息。版本 `1.0.12.09`。"
    },
    {
      "date": "2026-11-22",
      "title": "周六自动抢课延长至 19:10 前结束",
      "summary": "周六目标课按结束时间筛选，只有严格早于 19:10 的课程进入自动抢课。周安排、公开计划和旧缓存显示同步更新。版本 `1.0.12.08`。"
    },
    {
      "date": "2026-11-22",
      "title": "调整周一、周二芭蕾预约",
      "summary": "按 Owner 圈选取消 11 月 23–24 日三节已预约课程和一节排队课程。闻道实时复核确认四节均已取消，MaxNow 周安排已同步。版本 `1.0.12.07`。"
    }
  ]
};
