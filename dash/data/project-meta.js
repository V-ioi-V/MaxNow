window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-31 21:49",
  "version": "1.0.7.62",
  "versionLabel": "v1.0.7.62",
  "branch": "feature/update-ballet-booking-targets",
  "commit": "97fc6f0",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/update-ballet-booking-targets · commit 97fc6f0 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-31",
      "title": "更新周日自动抢课目标",
      "summary": "根据 Owner 标注的周课表，将周日 14:20 自动抢课目标替换为 5 节：周二王嘉豪软开 + 芭蕾 L1、周四李俊软开、周五李俊软开 + 王嘉豪芭蕾 L1，均为大教室晚间课；原周六 11:30 软开不再自动预约。"
    },
    {
      "date": "2026-07-30",
      "title": "将有效期圆环数字改为单行",
      "summary": "圆环内当前天数与总天数从上下两行改为横向单行 `N /总天数`，两段使用 `2px` 间距并整体居中；总天数下移 `1px` 做光学对齐。"
    },
    {
      "date": "2026-07-30",
      "title": "放大课程卡有效期圆环并收小正文",
      "summary": "有效期圆环从 `50px` 放大到 `66px`，环内当前天数与总天数继续保持 `15px / 8px`，增加留白而不放大环内文字。"
    },
    {
      "date": "2026-07-30",
      "title": "拆开课程卡有效进度文字与圆环",
      "summary": "有效进度卡改为三行网格：首行仅放“有效进度”和右上 `50px` 小圆环，“第 N / 总天数”与到期节奏说明分别独占后两行，不再把完整文字组和圆环挤在同一横行。"
    },
    {
      "date": "2026-07-30",
      "title": "分离课程卡舞者与事实区并缩小圆环数字",
      "summary": "中等及宽课程卡取消舞者插画右侧遮罩，改为互不重叠的左右分区：`330px–649px` 使用 `44% / 45%` 的舞者宽度与事实区起点，`650px` 以上使用 `40% / 42%`，日期、标题和指标卡从横向脚尖之后开始，完整保留抬手、横向脚尖和支撑腿足尖。"
    }
  ]
};
