window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-05 23:36",
  "version": "1.0.0.08",
  "versionLabel": "v1.0.0.08",
  "branch": "feature/home-input-dedupe",
  "commit": "07c02b7",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/home-input-dedupe · commit 07c02b7 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-05",
      "title": "收敛 Home 外部输入和待推进重复项",
      "summary": "Home 不再单独展示“AI 外部输入”卡，外部 AI 信号统一进入 Last-30 的“最新信号 / 本周观察 / 近 30 天主线”三列模块。"
    },
    {
      "date": "2026-07-05",
      "title": "修正版本卡运行数据误报",
      "summary": "`scripts/sync_project_meta.py` 将 AI 信号、Last-30、服务器 Codex 用量和 Life foods 等自动生成数据纳入运行数据白名单。"
    },
    {
      "date": "2026-07-05",
      "title": "优化 Token 数值单位进位",
      "summary": "Token 页总量、来源、模型、会话和趋势图统一使用同一个数值格式化规则。"
    },
    {
      "date": "2026-07-05",
      "title": "将 Last-30 摘要改回 AI 大事口径",
      "summary": "`scripts/sync_ai_last30.py` 不再外露“适合进入近 30 天观察池”这类采集器内部筛选话术。"
    },
    {
      "date": "2026-07-05",
      "title": "收紧 Last-30 外露信息口径",
      "summary": "将 Last-30 左栏静态标签从 `Today` 改为 `Latest`，默认标题改为“最新信号”，避免最近 7 天回退数据被误读为当天信号。"
    }
  ]
};
