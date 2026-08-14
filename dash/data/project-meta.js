window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-14 23:06",
  "version": "1.0.9.14",
  "versionLabel": "v1.0.9.14",
  "branch": "bugfix/ballet-aug7-teacher",
  "commit": "91aca72",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/ballet-aug7-teacher · commit 91aca72 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-08-14",
      "title": "校正 8 月 7 日课程老师",
      "summary": "Owner 将 2026-08-07 19:45–21:15 芭蕾 L1 的老师明确校正为“张瀚泽”；这条记录不再使用空老师默认李俊。"
    },
    {
      "date": "2026-08-14",
      "title": "统一实际上课历史的空老师口径",
      "summary": "Owner 确认闻道实际上课历史未填写老师时统一按“李俊”处理；明确填写的老师和 Owner 手工补录老师保持原值，未来课表、当前预约与候补不套用该默认值。"
    },
    {
      "date": "2026-08-09",
      "title": "自动抢课增加小教室兜底",
      "summary": "周日 17:30 芭蕾 L1 与 19:00 肌肉素质不再固定要求大教室；同一日期、课程和时间优先唯一匹配大教室，大教室没有时再唯一匹配小教室。"
    },
    {
      "date": "2026-08-09",
      "title": "修复 Token 总账拉取失败后归零",
      "summary": "服务器 Git remote 切换到 GitHub SSH 443 后缺少对应凭据，每小时 `:10` 总账任务在 `git pull` 阶段失败；旧脚本又已先暂存运行态账本，导致线上退回仓库内 7 月 7 日旧总账，Token 页当天范围显示为 0。"
    },
    {
      "date": "2026-08-09",
      "title": "自动抢课改为箭头所示两节周日课程",
      "summary": "Owner 明确只抢周日大教室 17:30–19:00 芭蕾 L1 与 19:00–20:00 肌肉素质，均不限老师；此前周二、周四、周五及旧周日晚间目标全部移除。"
    }
  ]
};
