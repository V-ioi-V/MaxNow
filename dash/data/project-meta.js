window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-02 23:07",
  "version": "1.0.8.27",
  "versionLabel": "v1.0.8.27",
  "branch": "feature/ballet-training-stats",
  "commit": "282c6c6",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-training-stats · commit 282c6c6 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-08-02",
      "title": "训练概览只统计刷新前已上完课程",
      "summary": "芭蕾顶部原“本周训练”改为六项训练概览：本周训练次数、本周训练时长、本周最喜欢的课、总训练次数、总训练时长和全部时间最喜欢的课。"
    },
    {
      "date": "2026-08-02",
      "title": "调整芭蕾周记录入口并加快首次出图",
      "summary": "`week N` 入口从标题左侧移到“已同步”右侧，字号、字重、高度和色彩直接继承顶部状态胶囊，避免与相邻标题割裂。"
    },
    {
      "date": "2026-08-02",
      "title": "完成芭蕾周记录封面",
      "summary": "芭蕾页顶部标题左侧新增 `week N` 入口；点击后以固定粉色手作底图和透明手绘数字在浏览器本地生成 `1280×1710` PNG，支持预览、下载和剪贴板复制。"
    },
    {
      "date": "2026-08-02",
      "title": "建立芭蕾周记录手绘数字素材库",
      "summary": "以当前封面效果中的手绘 `2` 为基准，完成酒红色透明 PNG `0–9` 数字；统一高度和基线，保留自然字宽，后续可由浏览器脚本稳定拼接任意周数。"
    },
    {
      "date": "2026-08-02",
      "title": "修复 Windows Codex 用量上报假成功",
      "summary": "修复 `scripts/report_codex_usage.ps1` 未检查 Git / Python 原生命令退出码的问题；fetch、生成、检查、暂存和提交任一步骤失败都会让计划任务返回非零，不再把 push 拒绝记录成成功。"
    }
  ]
};
