window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-10-11 18:53",
  "version": "1.0.11.78",
  "versionLabel": "v1.0.11.78",
  "branch": "feature/remove-dounai",
  "commit": "aea6b733",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/remove-dounai · commit aea6b733 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-10-11",
      "title": "豆奶功能下线",
      "summary": "按 Owner 要求删除豆奶 tab、首页摘要、专用页面 / 样式、数据加载、健康来源及数据文件；旧链接回首页并清除原浏览器缓存。同步移除 Cloud 采集任务说明和 OpenClaw 数据写入授权。"
    },
    {
      "date": "2026-10-11",
      "title": "截图圈选周六课程取消",
      "summary": "Owner 红框指定 10 月 17 日 15:30–17:00「芭蕾L1.5 - 入门+」，徐老师 / 大教室。实时活动预约唯一匹配，dry-run ready、mutationAttempts=0；单次取消 mutation 返回 cancelled，18:37:20 独立活动预约查询确认目标消失，周六上午 L1 预约仍在。"
    },
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
    }
  ]
};
