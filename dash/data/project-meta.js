window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-10-11 18:35",
  "version": "1.0.11.76",
  "versionLabel": "v1.0.11.76",
  "branch": "bugfix/ballet-booking-record-1011",
  "commit": "fd7f1c5d",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/ballet-booking-record-1011 · commit fd7f1c5d · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-10-11",
      "title": "截图圈选两节课程预约",
      "summary": "Owner 红框指定 10 月 13 日 18:45–20:15「芭蕾L2-零基础」和 10 月 14 日 19:00–20:00「软开课」，均为张瀚泽 / 小教室。实时课表唯一匹配，统一 dry-run 两节 ready、mutationAttempts=0；执行各一次预约，activationAttempts=0，独立活动预约查询均确认 booked。"
    },
    {
      "date": "2026-10-11",
      "title": "芭蕾历史与预约重叠读取",
      "summary": "同步开始即并行读取历史、活动预约与课表，各任务仍共用最多 3 条 HTTPS 连接，不减少预约 / 历史索引 / 课程卡实时读取。"
    },
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
    }
  ]
};
