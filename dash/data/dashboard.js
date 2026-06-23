window.MAXNOW_DASHBOARD_DATA = {
  "brief": "今天主要把 MaxNow 从信息展示页收敛成个人状态工作站，并把 OpenClaw 的数据边界写清楚。",
  "feedSource": "ROADMAP.md",
  "journalSource": "Repo status",
  "today": {
    "mode": "define",
    "modeLabel": "整理模式",
    "energy": "中",
    "focus": "规划个人博客发布链路",
    "summary": "当前优先推进：规划个人博客发布链路。",
    "updatedAt": "2026-06-18 19:53"
  },
  "weather": {
    "city": "北京市",
    "district": "海淀",
    "location": "北京市海淀区",
    "condition": "晴",
    "tempC": 22,
    "highC": 35,
    "lowC": 23,
    "updatedAt": "2026-06-23 20:04",
    "source": "wttr.in",
    "sourceUrl": "https://wttr.in/Haidian,Beijing?format=j1"
  },
  "automation": {
    "status": "正常",
    "summary": "OpenClaw 日常只更新 data/ 下的数据文件",
    "lastRun": "2026-05-26 00:40"
  },
  "mainlines": [
    {
      "title": "规划个人博客发布链路",
      "note": "建议分支：`feature/blog-module-plan`",
      "label": "Now",
      "status": "active"
    }
  ],
  "actions": [
    {
      "title": "规划个人博客发布链路",
      "note": "建议分支：`feature/blog-module-plan`",
      "label": "Now",
      "status": "active"
    },
    {
      "title": "让 Last-30 进入增量更新节奏",
      "note": "当前 `dash/data/last-30.json` 还是 2026-06-14 的草稿，需要进入日常增量更新。",
      "label": "Next",
      "status": "waiting"
    },
    {
      "title": "补充 Token 使用页真实数据",
      "note": "来源 ID：`maxnow-token-usage`",
      "label": "Next",
      "status": "waiting"
    }
  ],
  "journal": [
    {
      "source": "Owner",
      "title": "MaxNow 的主角是个人状态",
      "summary": "AI 每日精选只是附加项，首页不能变成新闻聚合。",
      "url": ""
    },
    {
      "source": "Design",
      "title": "自动记录事实，你只补判断",
      "summary": "Token、GitHub、服务器和 OpenClaw 状态自动更新；今日一句话和优先级由 owner 确认。",
      "url": ""
    },
    {
      "source": "Boundary",
      "title": "OpenClaw 只碰数据",
      "summary": "日常维护只允许写 data/dashboard.* 和 data/ai-news.*，页面结构由 Codex 或人工维护。",
      "url": ""
    }
  ],
  "timeline": [
    {
      "time": "00:10",
      "title": "AI 外部输入更新",
      "note": "OpenClaw 更新 data/ai-news.*，X 不可用时用官方、HN、GitHub、Reddit 补足。"
    },
    {
      "time": "09:30",
      "title": "看一眼今日状态",
      "note": "确认今日模式、主线和真正要推进的 1-3 件事。"
    },
    {
      "time": "22:30",
      "title": "生成今日记录草稿",
      "note": "OpenClaw 根据可用事实写短记录，不覆盖 owner 确认过的判断。"
    }
  ],
  "feeds": [
    {
      "source": "Roadmap",
      "title": "当前可执行任务",
      "summary": "Home 的当前主线和今日推进由 scripts/update_data.py project-status 从 ROADMAP.md 显式刷新。",
      "url": "https://github.com/V-ioi-V/MaxNow/blob/main/ROADMAP.md"
    },
    {
      "source": "Automation",
      "title": "服务器同步链路",
      "summary": "wiki-todos 与系统状态每 10 分钟由服务器 crontab 刷新，失败信息进入系统状态列表。",
      "url": ""
    }
  ],
  "system": [
    {
      "key": "server",
      "name": "轻量服务器",
      "value": "Online",
      "note": "2C / 2G / 40G，适合静态站和轻量定时任务"
    },
    {
      "key": "storage",
      "name": "数据文件",
      "value": "JSON",
      "note": "页面读取 data/*.json，JS wrapper 作为静态兜底"
    },
    {
      "key": "openclaw",
      "name": "OpenClaw",
      "value": "Bounded",
      "note": "只允许更新 data/dashboard.* 和 data/ai-news.*"
    },
    {
      "key": "tls",
      "name": "HTTPS",
      "value": "Pending",
      "note": "部署到 dash.maxnow.cn 后配置"
    }
  ],
  "tokenUsage": {
    "updatedAt": "2026-05-26 00:40",
    "ranges": [
      {
        "key": "1h",
        "label": "近1小时",
        "input": 18200,
        "output": 7400,
        "total": 25600,
        "cost": 0.12,
        "note": "主要消耗在 MaxNow spec 和首页方向收敛。"
      },
      {
        "key": "24h",
        "label": "24小时",
        "input": 148000,
        "output": 53000,
        "total": 201000,
        "cost": 0.94,
        "note": "今天集中在个人看板定位、OpenClaw 边界和数据契约。"
      },
      {
        "key": "7d",
        "label": "7天",
        "input": 512000,
        "output": 188000,
        "total": 700000,
        "cost": 3.26,
        "note": "最近一周以 MaxNow 看板和服务器部署准备为主。"
      },
      {
        "key": "30d",
        "label": "30天",
        "input": 1680000,
        "output": 620000,
        "total": 2300000,
        "cost": 10.85,
        "note": "月度趋势后续由 OpenClaw 按真实账单刷新。"
      }
    ],
    "models": [
      {
        "name": "GPT-5 Codex",
        "total": 515000,
        "share": 74
      },
      {
        "name": "GPT-5",
        "total": 128000,
        "share": 18
      },
      {
        "name": "Other",
        "total": 57000,
        "share": 8
      }
    ],
    "daily": [
      {
        "date": "2026-05-20",
        "label": "5/20",
        "total": 74000
      },
      {
        "date": "2026-05-21",
        "label": "5/21",
        "total": 81000
      },
      {
        "date": "2026-05-22",
        "label": "5/22",
        "total": 69000
      },
      {
        "date": "2026-05-23",
        "label": "5/23",
        "total": 98000
      },
      {
        "date": "2026-05-24",
        "label": "5/24",
        "total": 115000
      },
      {
        "date": "2026-05-25",
        "label": "5/25",
        "total": 201000
      },
      {
        "date": "2026-05-26",
        "label": "今天",
        "total": 25600
      }
    ]
  }
};
