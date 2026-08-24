window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-24 22:20",
  "version": "1.0.11.06",
  "versionLabel": "v1.0.11.06",
  "branch": "bugfix/ballet-timetable-card-labels",
  "commit": "cbfcdc2",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "bugfix/ballet-timetable-card-labels · commit cbfcdc2 · 干净",
  "recentUpdates": [
    {
      "date": "2026-08-24",
      "title": "确保一小时课程卡状态标签始终可见",
      "summary": "继续保留“已预约 / 已约”等状态标签；将 60 分钟及以下卡片的报名 / 排队与完整时间字号由 `5px` 收至 `4.5px`，并收紧内部行间距，避免短课卡底部再次被裁切。"
    },
    {
      "date": "2026-08-23",
      "title": "修复部署覆盖芭蕾训练记录",
      "summary": "19:33 的并行代码部署将服务器运行时 `ballet.json` / `.js` 覆盖为仓库内 7 月 30 日兜底快照，页面因此从 19 节 / 23.5 小时回退为 4 节 / 5 小时；课程源记录和私有账本没有丢失。"
    },
    {
      "date": "2026-08-23",
      "title": "自动抢课加入工作日李俊老师优先级",
      "summary": "保持课程优先级 `L1 > L1.5 > 软开` 不变；每一课程层内调整为周六全部课程、周一至周五李俊课程、周一至周五其他老师课程，老师字段为空按李俊处理，各组内继续按原日期与开始时间排序。"
    },
    {
      "date": "2026-08-23",
      "title": "周简报数字改为正常常规字重",
      "summary": "周简报的动态周数、日期、训练次数和时长不再使用偏粗的毛笔字与同色描边，改为常规字重的 UI 字体直接填色，数字更正常、清爽。"
    },
    {
      "date": "2026-08-23",
      "title": "修复一小时课程卡底部状态裁切",
      "summary": "正式课表实测发现部分 60 分钟课程内容仍比卡片高 `4px`；统一将一小时卡的报名 / 排队与完整时间缩至 `5px`，上下内边距收至 `2px` 并压紧行高，保证状态标签在最底部完整显示。"
    }
  ]
};
