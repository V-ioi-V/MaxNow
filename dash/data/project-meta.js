window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-28 17:38",
  "version": "1.0.7.02",
  "versionLabel": "v1.0.7.02",
  "branch": "feature/ballet-share-card-todo",
  "commit": "1cb3c9b",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-share-card-todo · commit 1cb3c9b · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-28",
      "title": "记录芭蕾分享图待办",
      "summary": "芭蕾 Later 新增分享图功能：从现有脱敏数据选择下一节、本周训练、阶段节数 / 时长、主要课型和近期记录等关键信息，浏览器本地生成可预览、可下载的图片。"
    },
    {
      "date": "2026-07-28",
      "title": "自动抢课改为逐课独立并增加安全重试",
      "summary": "周日 fast path 将三节目标拆为独立失败域：第一节课程级失败或预约结果未知不会阻止第二、第三节；只有登录失效、配置错误或闻道页面协议变化才全局停止。"
    },
    {
      "date": "2026-07-28",
      "title": "增加周日自动抢课 Fast Path",
      "summary": "新增服务器本地 `book_ballet_fast.py` 与精确定时 systemd service / timer：周日 14:19:35 预热，14:20:00 按“周六 > 周日 > 周五 > 其他日期”顺序逐课即时校验并提交；关键路径不经过 Codex、Skill 或 SSH。初版未知结果会停止后续，随后同日按上方记录改为逐课独立安全重试。"
    },
    {
      "date": "2026-07-28",
      "title": "增加芭蕾对话式显式预约",
      "summary": "新增精确课程预约脚本与 hardened transient runner；单课或多课先统一实时预检已有预约、余位、唯一课程卡和闻道规则，全部通过后再按输入顺序逐节提交并实时复核。"
    },
    {
      "date": "2026-07-28",
      "title": "记录芭蕾 Apple 日历与多课预约待办",
      "summary": "芭蕾 Later 新增私有 ICS / `webcal://` 订阅：Apple 设备首次确认后自动刷新预约和候补，链接可撤销且不得暴露 PHPSESSID、会员标识或源记录 ID。"
    }
  ]
};
