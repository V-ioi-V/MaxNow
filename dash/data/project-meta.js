window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-14 10:51",
  "version": "1.0.4.04",
  "versionLabel": "v1.0.4.04",
  "branch": "bugfix/codex-macos-report-self-heal",
  "commit": "480dd89",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/codex-macos-report-self-heal · commit 480dd89 · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-07-10",
      "title": "拉开 Today Status 右侧信息层级",
      "summary": "将“自动生成”新鲜度 pill 从圆环旁收回 `Today Status` eyebrow 旁，避免左侧状态与右侧进度争抢视觉中心。"
    },
    {
      "date": "2026-07-10",
      "title": "统一全部非首页页面视觉",
      "summary": "豆奶、Token、云服务、生活和同行记新增共享 `secondary-view` / `secondary-page-head` 外壳，统一顶部 4px 主题线、轻色渐变白底、圆角、阴影、hover / focus 和状态 pill。"
    }
  ]
};
