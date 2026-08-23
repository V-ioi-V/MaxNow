window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-23 19:56",
  "version": "1.0.11.05",
  "versionLabel": "v1.0.11.05",
  "branch": "bugfix/preserve-ballet-runtime",
  "commit": "4493ec9",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/preserve-ballet-runtime · commit 4493ec9 · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-08-23",
      "title": "周简报动态字改为端正可爱的马善政字体",
      "summary": "按 Owner 反馈只替换周简报中动态填写的周数、日期、次数、时长和课程名：由歪斜感较强的 Long Cang 改为更端正、圆润和可爱的项目内置 Ma Shan Zheng；底图标题、六项指标名、数据位置、字号和颜色保持不变。"
    }
  ]
};
