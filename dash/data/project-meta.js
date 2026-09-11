window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-09-11 23:23",
  "version": "1.0.11.23",
  "versionLabel": "v1.0.11.23",
  "branch": "feature/ballet-card-controls-inside",
  "commit": "b8e57d59",
  "dirty": true,
  "dirtyLevel": "generated",
  "deployNote": "feature/ballet-card-controls-inside · commit b8e57d59 · 运行数据已更新",
  "recentUpdates": [
    {
      "date": "2026-09-11",
      "title": "课程卡填满概览格并内置滑动标识",
      "summary": "芭蕾顶部课程卡票券改为填满所在概览格，多张卡仍保持一次一张的横向吸附滑动。"
    },
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
    }
  ]
};
