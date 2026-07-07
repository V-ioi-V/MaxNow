window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-07 16:51",
  "version": "1.0.0.22",
  "versionLabel": "v1.0.0.22",
  "branch": "feature/home-token-heatmap",
  "commit": "6218575",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/home-token-heatmap · commit 6218575 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-07",
      "title": "将 Token 热力格移到 Home 主线位",
      "summary": "Home 原“当前主线”卡片替换为近 90 天每日 Token 活动热力格，格子横向铺满卡片，悬浮可查看日期和 token 数。"
    },
    {
      "date": "2026-07-07",
      "title": "加固服务器 Token 总账刷新 pull 超时",
      "summary": "`scripts/refresh_token_usage_on_server.sh` 的 `git pull --ff-only origin main` 增加默认 120 秒超时，避免 GitHub 网络偶发挂起时长期占住刷新锁。"
    },
    {
      "date": "2026-07-07",
      "title": "拆开本机 Codex 上报与服务器 Token 总账刷新",
      "summary": "Windows / macOS 本机 Codex 上报脚本改为只提交各自源账本：`codex-usage.*` / `codex-macos-usage.*`，推送后不再 SSH 触发服务器合并。"
    },
    {
      "date": "2026-07-07",
      "title": "将 Token 趋势改为活动热力格",
      "summary": "将 Token 页底部“最近 30 天”折线图替换为近 12 个自然月的 Token 活动热力格，按月份铺开每日格子。"
    },
    {
      "date": "2026-07-07",
      "title": "修复 OpenClaw Token 来源回退为空",
      "summary": "复查发现线上 `openclaw-usage.*` 被仓库中的空基线覆盖，导致统一 `token-usage.*` 只剩 Codex 来源，Token 页来源费用面板过滤掉 0 用量的 OpenClaw。"
    }
  ]
};
