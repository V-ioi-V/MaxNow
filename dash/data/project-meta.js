window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-10-11 16:35",
  "version": "1.0.11.74",
  "versionLabel": "v1.0.11.74",
  "branch": "feature/ballet-incremental-refresh",
  "commit": "744bd871",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-incremental-refresh · commit 744bd871 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-10-11",
      "title": "芭蕾减少重复历史详情与课表请求",
      "summary": "页面 / 手动刷新使用 smart 增量：完整读取历史列表及分页，只重读新增或索引变化的历史详情；预约、候补和课程卡保持实时读取。课表原始快照最多复用 5 分钟，不推进采集时间，取消导致旧本人状态时重读。"
    },
    {
      "date": "2026-10-11",
      "title": "芭蕾刷新复用连接并重叠课表读取",
      "summary": "同次完整刷新共用最多 3 条固定站点 HTTPS 连接，服务端关闭或读取失败时重建；全局连接池限制各阶段合计并发，不扩大只读范围或重试次数。"
    },
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
    }
  ]
};
