window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-02 19:04",
  "version": "1.0.8.24",
  "versionLabel": "v1.0.8.24",
  "branch": "feature/ballet-week-digits",
  "commit": "a48c239",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-week-digits · commit a48c239 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-08-02",
      "title": "建立芭蕾周记录手绘数字素材库",
      "summary": "以当前封面效果中的手绘 `2` 为基准，完成酒红色透明 PNG `0–9` 数字；统一高度和基线，保留自然字宽，后续可由浏览器脚本稳定拼接任意周数。"
    },
    {
      "date": "2026-08-02",
      "title": "修复 Windows Codex 用量上报假成功",
      "summary": "修复 `scripts/report_codex_usage.ps1` 未检查 Git / Python 原生命令退出码的问题；fetch、生成、检查、暂存和提交任一步骤失败都会让计划任务返回非零，不再把 push 拒绝记录成成功。"
    },
    {
      "date": "2026-08-02",
      "title": "训练趋势卡与历史卡统一样式",
      "summary": "“8 月上课节数热力图”标题移入左侧卡片内，并增加 `Training trend` 眉题；左侧趋势卡与右侧上课历史卡同顶同底、共用边框和背景。"
    },
    {
      "date": "2026-08-02",
      "title": "代抢改为普通内容标题",
      "summary": "“代抢 / 上次抢课结果”继续双栏并列，但移除居中粉色胶囊式伪 Tab；改用与“抢课”一致的英文眉题、左对齐中文标题和右侧节数状态。"
    },
    {
      "date": "2026-08-02",
      "title": "课表当前时间标签不再遮挡课程",
      "summary": "当前时间数字从课程区时间线内部拆出，固定放入最左侧时间轴列；细玫瑰线继续横穿课程区，但文字不再进入任何课程卡。"
    }
  ]
};
