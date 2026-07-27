window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-27 19:12",
  "version": "1.0.5.17",
  "versionLabel": "v1.0.5.17",
  "branch": "feature/ballet-compact-header",
  "commit": "78e647e",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-compact-header · commit 78e647e · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-27",
      "title": "删除芭蕾重复标题卡",
      "summary": "删除芭蕾内容区重复的 “Ballet Progress / 芭蕾 / 已同步”标题卡，只保留一行低权重数据更新时间。"
    },
    {
      "date": "2026-07-27",
      "title": "修正课程卡预测口径",
      "summary": "删除没有业务依据的固定“近 28 天节奏”：它会把开卡前日期当成未上课，还会让不同课程卡共享全局上课样本。"
    },
    {
      "date": "2026-07-27",
      "title": "补齐芭蕾只读训练闭环",
      "summary": "将“课前 N 小时可取消”按课程开课时间换算成真实绝对截止时间；无法解析时原样显示。候补课程在可用时展示“排队第 N 位”，不再只显示笼统的“排队中”。"
    },
    {
      "date": "2026-07-27",
      "title": "修复卡片 hover 丢失语义底色",
      "summary": "根因是共享 hover 规则强制写入纯白背景，导致粉白、紫白、青白等轻主题卡在鼠标移入时突然变白；原本就是白底的条目则看不出变化，造成同页反馈不一致。"
    },
    {
      "date": "2026-07-27",
      "title": "将下一节预约改为自适应信息布局",
      "summary": "撤销固定 `470px` 内容块的机械居中，右侧 tab 改为“紧凑日期 / 弹性课程信息 / 状态”三段式布局；标题与课程信息共享左基线，元素会随卡片宽度自然分配空间。"
    }
  ]
};
