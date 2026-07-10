window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-10 20:59",
  "version": "1.0.2.03",
  "versionLabel": "v1.0.2.03",
  "branch": "bugfix/today-status-alignment",
  "commit": "701833d",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/today-status-alignment · commit 701833d · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-10",
      "title": "修正 Today Status 时间轴方向与当前时间对齐",
      "summary": "将 00:00-24:00 今日进度轴统一为从上向下推进，当前时间圆点、时间文字和进度填充共用同一坐标方向。"
    },
    {
      "date": "2026-07-10",
      "title": "修复海淀降雨被显示为阴天",
      "summary": "北京天气从 Open-Meteo 默认 Best Match 切换到中国气象局 CMA / GRAPES 模型；同一时刻默认模型返回阴且降水为 0，CMA 模型返回阵雨和 2.3mm 降水。"
    },
    {
      "date": "2026-07-10",
      "title": "收紧 Token 来源更新时间卡",
      "summary": "Token 页头右侧来源更新时间卡改为 `410px` 内容宽度，不再按比例铺满半行；说明文字移到四行来源时间上方。"
    },
    {
      "date": "2026-07-10",
      "title": "用 MaxNow 风格登录页替代浏览器原生认证弹窗",
      "summary": "新增双栏登录页，复用 MaxNow 的浅蓝灰背景、白卡片、语义色小图标、输入框 focus 和轻量 hover；`760px` 以下自动切换单栏。"
    },
    {
      "date": "2026-07-10",
      "title": "轮换私人 Dash 访问密码",
      "summary": "已轮换 `dash.maxnow.cn` 的 nginx Basic Auth 密码；用户名保持 `maxnow`，真实密码和哈希均未写入仓库。"
    }
  ]
};
