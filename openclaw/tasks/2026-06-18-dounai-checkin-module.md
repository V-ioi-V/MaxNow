# Codex 任务：MaxNow 增加豆奶签到模块

## 背景
豆奶（dounai.pro）每日签到数据已经自动保存到 `/root/MaxNow/dash/data/dounai_checkin.json`，由 OpenClaw 每天早上 9:00 签到后更新。

## 要求

### 1. 数据文件
数据已就位：`dash/data/dounai_checkin.json`

格式：
```json
{
  "updatedAt": "2026-06-18 22:32",
  "today": {
    "date": "2026-06-18",
    "flow_mb": 751,
    "beans": 1,
    "hours": 2.32,
    "note": ""
  },
  "total": {
    "days": 52,
    "flow_mb": 28534,
    "beans": 52,
    "hours": 102.48
  },
  "records": [
    { "date": "2026-06-18", "flow_mb": 751, "beans": 1, "hours": 2.32, "note": "" }
  ]
}
```

### 2. 需要做的事
- 在 MaxNow 首页（Home）新增一个 **签到** 模块/卡片
- 展示内容：
  - 今日签到流量（如"今日: 751 MB"）
  - 累计签到天数（如"累计签到: 52 天")
  - 累计获得流量（如"累计流量: 27.9 GB")
  - 可选的：近7天流量迷你趋势图
- 数据从 `./data/dounai_checkin.json` 读取（跟 dashboard.json 同级）

### 3. 参考已有的数据加载模式
看 `app.js` 中如何加载 `dashboard.json`、`ai-news.json` 等，保持同样的模式。

### 4. 需要更新的文件
- `index.html` — 在首页添加签到模块
- `styles.css` — 签到模块的样式
- `app.js` — 加载 dounai_checkin.json 并渲染
- `UPDATE_LOG.md` — 记录本次更新
- 可选的：`SPEC.md`、`ROADMAP.md` 等

### 5. 注意事项
- 只读展示，不做编辑功能
- 数据每天 9:00 自动更新（由 OpenClaw cron 触发）
- 遵循现有 MaxNow 的视觉风格
- **不要修改 OpenClaw 的签到脚本或 cron 配置**，这些已经由 OpenClaw 管理好了
