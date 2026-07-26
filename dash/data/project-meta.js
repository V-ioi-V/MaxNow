window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-26 10:12",
  "version": "1.0.4.13",
  "versionLabel": "v1.0.4.13",
  "branch": "feature/precise-dounai-daily-budget",
  "commit": "6e0609c",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/precise-dounai-daily-budget · commit 6e0609c · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-07-21",
      "title": "首页小日历增加下一特殊日期",
      "summary": "小日历新增独立的下一特殊日期行，统一比较内置公历 / 农历节日和个人特殊日期，按“x天后是xx日（x月x日）”展示严格晚于今天的最近一项；当天节日 / 特殊日期行继续保留，两者可同时显示。"
    },
    {
      "date": "2026-07-21",
      "title": "将豆奶余量与日均预算切换为字节级精确数据",
      "summary": "服务器豆奶生成脚本不再把用户面板的两位 TB / GB 标签当作精确余量；每天 09:00 的账号快照优先读取现有订阅 `subscription-userinfo` header，以 `total - upload - download` 计算精确剩余字节和日均可用预算。"
    }
  ]
};
