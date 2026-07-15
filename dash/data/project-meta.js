window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-15 17:07",
  "version": "1.0.4.06",
  "versionLabel": "v1.0.4.06",
  "branch": "feature/data-health-states",
  "commit": "53c2c52",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/data-health-states · commit 53c2c52 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-15",
      "title": "建立数据失败与新鲜度闭环",
      "summary": "Home 数据同步开始区分已同步、暂无记录、请求失败、数据过期和尚未同步，覆盖 Wiki、Token、天气、市场、Last-30、版本、Roadmap、豆奶、同行记和生活。"
    },
    {
      "date": "2026-07-15",
      "title": "修复 Codex 分叉会话 Token 重复累计",
      "summary": "`scripts/sync_codex_usage.py` 改为按 `total_token_usage` 相邻快照的正向增量记账，并在同一会话树内去重分叉文件继承的历史边。"
    },
    {
      "date": "2026-07-14",
      "title": "修复 macOS Codex 上报分叉后永久停摆",
      "summary": "`scripts/report_codex_usage.sh` 每轮先 fetch 最新 `origin/main`；若本地独有提交全部是该任务生成、提交标题匹配且只修改 `codex-macos-usage.*`，自动丢弃旧生成提交并基于最新主线重新采集。"
    },
    {
      "date": "2026-07-11",
      "title": "移除全部 tab 卡片顶部彩色横条",
      "summary": "Home、豆奶、Token、云服务、生活和同行记的页头卡、摘要卡、普通面板、图表卡与统计卡统一取消顶部 4px 彩色或渐变强调线。"
    },
    {
      "date": "2026-07-11",
      "title": "居中 Today Status 日进度并对齐信号节点",
      "summary": "宽桌面改为左文案、正中央圆环、右信号三列，左右使用等宽弹性区域，让圆环中心与状态卡内容区中心严格重合。"
    }
  ]
};
