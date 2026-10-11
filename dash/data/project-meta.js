window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-10-11 16:15",
  "version": "1.0.11.72",
  "versionLabel": "v1.0.11.72",
  "branch": "feature/ballet-parallel-refresh",
  "commit": "2674ba8e",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-parallel-refresh · commit 2674ba8e · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-10-11",
      "title": "芭蕾整体刷新使用少量并行读取",
      "summary": "历史详情、预约详情与每日课表最多 3 路并行，分页保留顺序，历史 / 课程卡 / 预约 / 课表范围不减少。共享 Session 和请求计数加锁，身份失效阻止后续网络尝试，真实约课提交仍串行。"
    },
    {
      "date": "2026-10-11",
      "title": "芭蕾自动刷新仅限首次进入",
      "summary": "每次打开或重新加载 MaxNow，仅首次进入芭蕾页自动刷新；切到豆奶等页面再返回不重新同步。触发前记录当前页面内存标记，失败后切页也不重复触发。"
    },
    {
      "date": "2026-10-11",
      "title": "芭蕾定时刷新收敛为每周一次",
      "summary": "按 Owner 要求，业务定时仅保留北京时间周日 14:30 抢课后的 rolling 同步；移除每日五次与周日晚间日程，停用月度 full timer，取消抢课成功 / 失败即时同步钩子。"
    },
    {
      "date": "2026-10-11",
      "title": "确认手动待上课为已完成",
      "summary": "Owner 确认 10 月 11 日 10:00–11:30 李俊老师大教室「芭蕾 L1 入门」已上完；复用既有 manual 稳定键，由 planned 改为 active / attended，不新增第二条记录。"
    },
    {
      "date": "2026-10-11",
      "title": "芭蕾统一刷新状态与减少课表请求",
      "summary": "实测页面同步 15:48:05–15:49:06 共 61 秒；顶部只保留一个状态，刷新时显示已等待时分秒，完成恢复已同步，失败显示刷新失败。取消重复状态和弹出通知；静态数据重新渲染不得覆盖正在刷新的状态，六分钟等待上限后明确报超时。"
    }
  ]
};
