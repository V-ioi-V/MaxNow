window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-27 16:39",
  "version": "1.0.5.14",
  "versionLabel": "v1.0.5.14",
  "branch": "bugfix/card-hover-deploy-record",
  "commit": "1724fb7",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/card-hover-deploy-record · commit 1724fb7 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-27",
      "title": "修复卡片 hover 丢失语义底色",
      "summary": "根因是共享 hover 规则强制写入纯白背景，导致粉白、紫白、青白等轻主题卡在鼠标移入时突然变白；原本就是白底的条目则看不出变化，造成同页反馈不一致。"
    },
    {
      "date": "2026-07-27",
      "title": "将下一节预约改为自适应信息布局",
      "summary": "撤销固定 `470px` 内容块的机械居中，右侧 tab 改为“紧凑日期 / 弹性课程信息 / 状态”三段式布局；标题与课程信息共享左基线，元素会随卡片宽度自然分配空间。"
    },
    {
      "date": "2026-07-27",
      "title": "居中芭蕾下一节预约内容",
      "summary": "将右侧“下一节预约”tab 的标题与“日期 + 课程信息”内容组整体横向居中，状态 pill 继续固定在右上角，减少内容偏左造成的空洞感。"
    },
    {
      "date": "2026-07-27",
      "title": "将芭蕾顶部改为两个独立等宽 tab",
      "summary": "修正此前对“各占一半”的理解：芭蕾标题与“下一节预约”改为两个同级独立 tab，不再把课程模块嵌套在标题卡内部。"
    },
    {
      "date": "2026-07-27",
      "title": "区分预约状态颜色并重排星期",
      "summary": "“所有预约”中的“已预约”保留粉玫瑰色，“排队中”改用橙色，候补状态不再与正式预约使用相同颜色。"
    }
  ]
};
