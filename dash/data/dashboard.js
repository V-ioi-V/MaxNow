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
    "latitude": 39.96,
    "longitude": 116.3,
    "condition": "阴",
    "summary": "小毛毛雨",
    "icon": "cloud",
    "weatherCode": 3,
    "dailyWeatherCode": 51,
    "tempC": 23.7,
    "highC": 30.8,
    "lowC": 19.8,
    "isDay": false,
    "updatedAt": "2026-06-23 21:46",
    "source": "Open-Meteo",
    "sourceUrl": "https://api.open-meteo.com/v1/forecast?latitude=39.96&longitude=116.3&current=temperature_2m%2Cweather_code%2Cis_day&daily=weather_code%2Ctemperature_2m_max%2Ctemperature_2m_min&timezone=Asia%2FShanghai&forecast_days=1"
  },
  "automation": {
    "status": "正常",
    "summary": "OpenClaw 日常只更新 data/ 下的数据文件",
    "lastRun": "2026-05-26 00:40"
  },
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
  ]
};
