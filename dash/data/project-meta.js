window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-09-14 21:21",
  "version": "1.0.11.32",
  "versionLabel": "v1.0.11.32",
  "branch": "bugfix/saturday-end-time-cutoff",
  "commit": "c9386193",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/saturday-end-time-cutoff · commit c9386193 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-09-14",
      "title": "周六抢课门槛改按结束时间判断",
      "summary": "根据 Owner 澄清，周六“18:00 前”改为检查课程结束时间：仅结束时间严格早于 18:00 的标准芭蕾 L1、L1.5 与精确“软开 / 软开课”进入 Fast Path，18:00 整结束也排除。"
    },
    {
      "date": "2026-09-13",
      "title": "周安排准备抢卡显示完整时间边界",
      "summary": "准备抢卡保留公开目标中的规则时段文案，工作日显示“18:40 后”、周六显示“18:00 前”，不再把规则边界裁成普通钟点。"
    },
    {
      "date": "2026-09-13",
      "title": "抢课双栏及八张指标卡统一尺寸",
      "summary": "“抢课助手 / 本次抢课”由原来的约 `56% / 44%` 改为严格各占一半，两张大卡同宽、同高。"
    },
    {
      "date": "2026-09-13",
      "title": "两周后周安排复用准备抢兜底",
      "summary": "移除“准备抢”仅限固定下周偏移的前端判断；五周窗口内任一未来周只要存在日期属于该周的公开 Fast Path 目标、没有真实课程且尚无同周结果，就展示对应准备抢卡。"
    },
    {
      "date": "2026-09-13",
      "title": "活动预约统一读取全部分页",
      "summary": "同步、实时查询和 Fast Path 写后复核统一调用活动预约分页读取器：先校验预约页声明的总数与固定 `newbookrecord` contract，再按已加载条数翻页、跨页合并去重，最后只读取预约 / 候补详情。"
    }
  ]
};
