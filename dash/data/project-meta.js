window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-27 12:04",
  "version": "1.0.5.06",
  "versionLabel": "v1.0.5.06",
  "branch": "feature/ballet-bookings-sync-record",
  "commit": "e5d1025",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-bookings-sync-record · commit e5d1025 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-27",
      "title": "部署多节预约并完成首次真实同步",
      "summary": "服务器已快进到 `e5d10258`，上线“下一节预约 + 后续预约”展示；部署前完整备份运行时数据并恢复非项目元信息数据，服务器 Git remote 从失效的 SSH 地址切回与现有 `gh` 登录一致的 HTTPS。"
    },
    {
      "date": "2026-07-27",
      "title": "展示多节未来预约",
      "summary": "“下一节预约”继续只突出最近一节有效预约；当缓存中还有其他已预约 / 候补课程时，芭蕾页在概览下方新增“后续预约”列表，展示日期、时间、课程、老师、级别和状态，不与实际上课历史混排。"
    },
    {
      "date": "2026-07-27",
      "title": "刷新闻道会话并启动 v6 每 20 分钟实验",
      "summary": "Owner 在微信内重新打开闻道页面并完全退出微信后，本机从最新微信资料目录安全提取新一代 `PHPSESSID`；仅比较脱敏哈希确认它与旧会话不同，未在终端、日志、聊天或 Git 输出 Cookie 值。"
    },
    {
      "date": "2026-07-26",
      "title": "增加 PHPSESSID 活跃实验状态卡并降频至 25 分钟",
      "summary": "芭蕾页新增独立粉白状态卡，展示 PHPSESSID 从原始起点到最后一次认证样本的“已确认有效时长”、实验起始、最近 / 下次自动检查和当前间隔；页面不会按当前时间外推证据，也不会把持续活动仍有效表述为已证明自动续期。"
    },
    {
      "date": "2026-07-26",
      "title": "上线芭蕾只读学习模块",
      "summary": "左侧导航顺序调整为首页 → 豆奶 → Token → 芭蕾 → 云服务 → 生活 → 同行记，取代当天较早记录的 Home 下方候选位置；芭蕾页沿用 `secondary-view`，使用粉玫瑰 + 白卡语义，并提供 Home 紧凑摘要。"
    }
  ]
};
