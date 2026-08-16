window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-17 00:08",
  "version": "1.0.10.15",
  "versionLabel": "v1.0.10.15",
  "branch": "bugfix/ballet-attendance-pagination",
  "commit": "79ef67b",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "bugfix/ballet-attendance-pagination · commit 79ef67b · 干净",
  "recentUpdates": [
    {
      "date": "2026-08-16",
      "title": "适配闻道上课历史分页",
      "summary": "闻道上课记录首屏开始只内嵌最近 10 条，但标题继续报告累计总数；同步器改为校验并调用页面官方固定分页接口，补齐更早的历史摘要。"
    },
    {
      "date": "2026-08-16",
      "title": "平衡抢课摘要宽度与四项排版",
      "summary": "“本地抢课结果 / Local Result”更名为“本次抢课 / This Run”。"
    },
    {
      "date": "2026-08-16",
      "title": "收紧周安排压缩刻度与底部留白",
      "summary": "修正上一版误解：压缩空档只保留起始 `13:00`，删除压缩带下沿的 `18:00` 重复刻度。"
    },
    {
      "date": "2026-08-16",
      "title": "简化周安排压缩空档刻度",
      "summary": "周安排的压缩空档左侧只显示起始整点，例如 `13:00`；移除 `13:00–18:00` 范围文案，空档结束的 `18:00` 继续作为晚间时间轴正常刻度。"
    },
    {
      "date": "2026-08-16",
      "title": "收齐抢课摘要高度并移除周安排底注",
      "summary": "“上次抢课结果”更名为“本地抢课结果”，英文眉题同步改为 `Local Result`。"
    }
  ]
};
