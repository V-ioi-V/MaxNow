window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-30 14:31",
  "version": "1.0.7.41",
  "versionLabel": "v1.0.7.41",
  "branch": "feature/ballet-growth-next-step",
  "commit": "a05ab97",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-growth-next-step · commit a05ab97 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-30",
      "title": "成长等级标题只显示当前 Lv",
      "summary": "紫色“成长等级”标题从“第 N 阶段 → 第 M 阶段”改为只显示当前 `Lv.N`；下方改为“本级 N / M 节”，下一等级仅在“还差 N 节升级到 Lv.M”中出现。"
    },
    {
      "date": "2026-07-30",
      "title": "成长等级只保留到下一阶段的距离",
      "summary": "紫色“成长等级”移除 `1–10` 全量编号，只展示“当前阶段 → 下一阶段”、本阶段已上 / 目标课次和还差多少节，保留当前阶段的小天鹅图像。"
    },
    {
      "date": "2026-07-30",
      "title": "区分课程等级与小天鹅成长阶段",
      "summary": "成长卡移除顶部重复的 `Lv.N`；蓝色块改名“课程等级”，直接显示已上课次和“再上 N 节升级到下一课程等级”，保留规律 / 保守课次口径。"
    },
    {
      "date": "2026-07-30",
      "title": "上提小天鹅成长图视觉重心",
      "summary": "成长等级块把“小天鹅 + 十段进度”作为一组在桌面端光学上提 `10px`、窄屏上提 `6px`，补偿低等级透明 PNG 上方留白偏多造成的视觉下沉；十张素材的尺寸、成长比例和切换逻辑保持不变。"
    },
    {
      "date": "2026-07-30",
      "title": "小天鹅改为十阶段自然成长图像",
      "summary": "用 Owner 确认的二维粉嫩小天鹅成长图替换代码内 SVG：Lv.1–Lv.3 为灰色绒毛雏鹅，Lv.4–Lv.6 逐步灰白换羽，Lv.7–Lv.9 形成白色成熟体态，Lv.10 为带克制光环与星点的成年天鹅。"
    }
  ]
};
