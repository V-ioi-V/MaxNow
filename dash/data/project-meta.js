window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-26 19:45",
  "version": "1.0.4.15",
  "versionLabel": "v1.0.4.15",
  "branch": "feature/ballet-session-20min",
  "commit": "0e2d94e",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-session-20min · commit 0e2d94e · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-26",
      "title": "将闻道 Session 持续活动探针降频至 20 分钟",
      "summary": "MaxNow 服务器已从 v3 每 10 分钟阶段安全交接到 `maxnow-wenda-session-lifetime-20260726-v4.service` 每 20 分钟阶段，请求频率由每小时 6 次降为 3 次；v4 首条验证为 HTTP 200 / authenticated 后才停止 v3。"
    },
    {
      "date": "2026-07-26",
      "title": "启动闻道 Session 服务器持续活动实验",
      "summary": "新增只允许访问闻道 `simpleclass` 课程表 GET 路径的 `scripts/probe_ballet_session.py`；每条样本仅记录 HTTP / 登录状态、响应摘要、`Set-Cookie` 名称和脱敏 Session 指纹，身份失效或连续 3 次未知 / 网络异常即停止，不具备预约、取消或转课能力。"
    },
    {
      "date": "2026-07-26",
      "title": "修复豆奶日均预算整数天分母造成的假下降",
      "summary": "服务器豆奶生成脚本新增 `remaining_days_exact`，用账号快照到有效期的精确剩余秒数计算日均可用预算；`days_remaining` 只保留为整天摘要，不再参与预算计算。"
    },
    {
      "date": "2026-07-25",
      "title": "收紧 OpenClaw 公网入口、认证与本地文件权限",
      "summary": "腾讯云防火墙仅保留公网 HTTP / HTTPS，以及来源为 Owner 当前公网 IPv4 `/32` 的 SSH；OpenClaw Gateway 改为只监听 `127.0.0.1` / `::1`，12123、16980 和 3000 不再作为公网入口。"
    },
    {
      "date": "2026-07-25",
      "title": "记录 LIJUN 芭蕾远端自动约课方案",
      "summary": "在 `ROADMAP.md` Later 固化微信公众号 H5 自动约课方案，明确会话生命周期验证、课程解析 dry-run、真实预约三阶段，以及课程优先级、候补、幂等、失败停止和通知要求。"
    }
  ]
};
