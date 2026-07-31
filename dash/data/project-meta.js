window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-01 01:10",
  "version": "1.0.8.02",
  "versionLabel": "v1.0.8.02",
  "branch": "feature/dynamic-ballet-booking-config",
  "commit": "30189fd",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/dynamic-ballet-booking-config · commit 30189fd · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-08-01",
      "title": "记录自动抢课动态配置待办",
      "summary": "`ROADMAP.md` Next 新增自动抢课动态配置任务：后续把稳定抢课引擎与目标课程分开，由服务器版本化配置作为唯一可编辑来源，并在 MaxNow 提供增删目标、优先级、逐课候补、单周覆盖和暂停能力。"
    },
    {
      "date": "2026-08-01",
      "title": "修复芭蕾同步账本权限并补齐失败可见性",
      "summary": "修复 7 月 30 日手工补录后私有 `attendance-ledger.json` 被 root 原子替换为 `root:root 0600` 的问题；恢复 `ubuntu:www-data 0600` 并以真实服务用户完成 JSON / ledger 校验后，手动执行一次 rolling 只读同步成功，数据更新到 `2026-08-01 00:39:46`，保留 4 条上课记录、3 条未来预约和 7 天课表。"
    },
    {
      "date": "2026-07-31",
      "title": "自动抢课支持目标课候补",
      "summary": "Owner 授权周日自动任务在 5 个精确配置目标仅可排队时自动候补；目标可预约时仍正常预约，已预约 / 已排队时不重复提交，普通实时查询和对话式预约仍不允许候补写入。"
    },
    {
      "date": "2026-07-31",
      "title": "更新周日自动抢课目标",
      "summary": "根据 Owner 标注的周课表，将周日 14:20 自动抢课目标替换为 5 节：周二王嘉豪软开 + 芭蕾 L1、周四李俊软开、周五李俊软开 + 王嘉豪芭蕾 L1，均为大教室晚间课；原周六 11:30 软开不再自动预约。"
    },
    {
      "date": "2026-07-30",
      "title": "将有效期圆环数字改为单行",
      "summary": "圆环内当前天数与总天数从上下两行改为横向单行 `N /总天数`，两段使用 `2px` 间距并整体居中；总天数下移 `1px` 做光学对齐。"
    }
  ]
};
