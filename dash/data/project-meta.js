window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-09-27 20:05",
  "version": "1.0.11.36",
  "versionLabel": "v1.0.11.36",
  "branch": "feature/tuesday-booking-priority",
  "commit": "e9ef3031",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/tuesday-booking-priority · commit e9ef3031 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-09-27",
      "title": "抢课优先周二，其次周六",
      "summary": "日期顺序调整为周二 → 周六 → 周五 → 周一 → 周三 → 周四；每天仍为 L1 → L1.5 → 软开。周安排中周二为优先 01–03、周六为 04–06，其他日期编号保持不变。"
    },
    {
      "date": "2026-09-26",
      "title": "手动录入王嘉豪老师芭蕾 L1 课程",
      "summary": "根据 Owner 截图，唯一匹配并手动录入 `2026-09-26 17:30–19:00` 大教室「芭蕾L1-入门」，老师王嘉豪，时长 90 分钟。"
    },
    {
      "date": "2026-09-20",
      "title": "移除芭蕾周简报",
      "summary": "根据 Owner 要求删除周简报切换、定时生成、画布绘制和专用模板 / 字体；芭蕾周记录弹窗回到单张 `week N` 封面，继续支持复制和下载 PNG。"
    },
    {
      "date": "2026-09-20",
      "title": "抢课改为按天优先",
      "summary": "日期顺序改为周六 → 周二 → 周五 → 周一 → 周三 → 周四，每天内部依次 L1 → L1.5 → 软开；周安排准备抢的 18 个优先级编号与实际提交排序一致。"
    },
    {
      "date": "2026-09-14",
      "title": "周六抢课门槛改按结束时间判断",
      "summary": "根据 Owner 澄清，周六“18:00 前”改为检查课程结束时间：仅结束时间严格早于 18:00 的标准芭蕾 L1、L1.5 与精确“软开 / 软开课”进入 Fast Path，18:00 整结束也排除。"
    }
  ]
};
