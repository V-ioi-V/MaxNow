window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-09-11 22:59",
  "version": "1.0.11.22",
  "versionLabel": "v1.0.11.22",
  "branch": "bugfix/ballet-history-scroll",
  "commit": "ad45c5da",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "bugfix/ballet-history-scroll · commit ad45c5da · 干净",
  "recentUpdates": [
    {
      "date": "2026-09-11",
      "title": "上课历史预览支持卡片内滑动",
      "summary": "芭蕾训练记录右侧的上课历史不再只渲染最近 8 条；当前筛选范围的全部记录都会进入紧凑列表，并在保持与左侧图表同高的卡片内纵向滑动。"
    },
    {
      "date": "2026-09-11",
      "title": "多张课程卡改为有效卡优先横向滑动",
      "summary": "芭蕾顶部课程卡从纵向堆叠改为一次展示一张的横向吸附轨道；使用中的卡固定排在已失效卡之前，手机可左右滑动，桌面可通过前后按钮、圆点和键盘方向键切换。"
    },
    {
      "date": "2026-09-11",
      "title": "课程卡支持展示已失效旧卡",
      "summary": "修复闻道会员卡页同时返回使用中卡与已失效旧卡时，旧卡缺少总次数导致全部芭蕾数据同步失败的问题。"
    },
    {
      "date": "2026-09-08",
      "title": "按当前页面懒加载 Dashboard 数据",
      "summary": "修复直接打开 `#ballet`、Token、豆奶等二级页时仍先等待整套 Home 数据的问题；现在先显示目标页，再只读取该页所需的数据源，芭蕾首开由 10 份数据请求收敛为 3 份，Token / 豆奶 / 生活各为 1 份。"
    },
    {
      "date": "2026-09-08",
      "title": "修复手动签到后豆奶页面未更新",
      "summary": "确认 Owner 已于 20:03 手动签到；豆奶 `/user/record` 的只读变更记录显示本次获得 865 MB、1 豆丁，基础与 VIP 有效期各延长 1.07 小时。"
    }
  ]
};
