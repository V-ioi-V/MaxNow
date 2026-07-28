window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-28 10:46",
  "version": "1.0.5.30",
  "versionLabel": "v1.0.5.30",
  "branch": "bugfix/macos-token-report-recovery",
  "commit": "2513a5b",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/macos-token-report-recovery · commit 2513a5b · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-28",
      "title": "修复 macOS Codex Token 上报中断死锁",
      "summary": "macOS 专用上报 clone 若在生成 `codex-macos-usage.*` 后、提交前被检查中断，下一轮会先确认没有越界改动，再恢复这两个任务自有生成文件并继续拉取、重新生成和上报。"
    },
    {
      "date": "2026-07-28",
      "title": "区分课表“可排队”与本人“排队中”",
      "summary": "修正源站普通“可排队”按钮被误判为本人候补的问题：普通课程保留“可排队”状态但不高亮，只有预约快照确认的本人候补课程才使用橙色整卡高亮；正式预约继续使用粉玫瑰整卡高亮。"
    },
    {
      "date": "2026-07-28",
      "title": "增加芭蕾周课表与周日发布刷新",
      "summary": "芭蕾页新增包含源站全部课程的粉白周课表，桌面使用时间 × 日期网格，移动端按日期分组；当天高亮、过去日期淡化、未来日期保持普通状态，已预约整卡使用粉玫瑰高亮，排队中整卡使用橙色高亮。"
    },
    {
      "date": "2026-07-28",
      "title": "统一所有预约行并补齐取消截止",
      "summary": "删除第一条预约的大号主卡和“下一节”特殊标识，让所有未来预约使用同一紧凑行样式；每条预约都在时间与老师下方增加小字号真实最晚取消时间。"
    },
    {
      "date": "2026-07-28",
      "title": "默认展开 PHPSESSID 实验详情",
      "summary": "芭蕾页底部 `PHPSESSID 实验详情` 改为进入页面时默认展开，同时保留原生折叠箭头和手动收起能力；版本提升到 `1.0.5.26`。"
    }
  ]
};
