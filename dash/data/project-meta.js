window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-30 20:22",
  "version": "1.0.7.51",
  "versionLabel": "v1.0.7.51",
  "branch": "feature/ballet-manual-attendance-20260730",
  "commit": "bcb343b",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-manual-attendance-20260730 · commit bcb343b · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-30",
      "title": "手动补录 7 月 30 日软开课",
      "summary": "按 Owner 提供的课表截图，手动补录 `2026-07-30 18:45–19:45` 李俊老师大教室“软开课”，记录状态为已上课，并使用 `manual` 稳定键保存在服务器私有上课台账中。"
    },
    {
      "date": "2026-07-30",
      "title": "按视觉中心对齐等级与小天鹅",
      "summary": "修正上一版只对齐可见主体顶部仍会让较高小天鹅视觉重心下沉的问题；`Lv.N` 与小天鹅舞台改为中心线排列，十张素材再按各自透明像素可见中心做百分比位移。"
    },
    {
      "date": "2026-07-30",
      "title": "将成长卡对齐与课表深色状态发布到生产",
      "summary": "生产服务器从仍使用统一像素位移与旧课表色阶的 `1.0.7.46 / styles.css?v=203`，升级到按十张小天鹅素材透明边界对齐并使用明显排队 / 预约深浅的 `styles.css?v=205`。"
    },
    {
      "date": "2026-07-30",
      "title": "拉开课表排队与预约色阶",
      "summary": "保留课程类型与级别决定色相的规则，把 Owner 排队课程统一改为由浅底色与课型描边色按 `56:44` 混合出的中深实心底，把已预约与已上完课程改为按 `18:82` 混合出的明显深色实心底。"
    },
    {
      "date": "2026-07-30",
      "title": "按可见主体对齐十级小天鹅",
      "summary": "成长等级右上角不再对十张透明 PNG 的完整画布做统一像素位移，改为按每张素材的透明上边界设置百分比光学上提。"
    }
  ]
};
