window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-02 20:13",
  "version": "1.0.8.25",
  "versionLabel": "v1.0.8.25",
  "branch": "feature/ballet-week-digits",
  "commit": "db538cf",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-week-digits · commit db538cf · 有未提交代码改动",
  "recentUpdates": [
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
    }
  ]
};
