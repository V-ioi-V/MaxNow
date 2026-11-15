window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-11-15 09:16",
  "version": "1.0.12.04",
  "versionLabel": "v1.0.12.04",
  "branch": "feature/skip-ballet-nov15",
  "commit": "fb01b68e",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/skip-ballet-nov15 · commit fb01b68e · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-11-15",
      "title": "本次周日自动抢课跳过",
      "summary": "跳过 11 月 15 日 14:20 的预约及候补批次。11 月 22 日 14:20 起恢复每周自动约课。版本 `1.0.12.04`。"
    },
    {
      "date": "2026-11-14",
      "title": "换闻道凭据后自动恢复检查",
      "summary": "systemd 监测生产凭据版本，换票后自动切换为新一轮只读检查，间隔 20 分钟。状态卡按新会话计时。版本 `1.0.12.03`。"
    },
    {
      "date": "2026-11-14",
      "title": "恢复闻道每 20 分钟会话检查",
      "summary": "新会话通过实时课表、活动预约及芭蕾完整同步验证。会话状态卡切到新一轮只读检查，时间和样本从新会话起算，间隔为 20 分钟。版本 `1.0.12.02`。"
    },
    {
      "date": "2026-11-14",
      "title": "闻道请求出口拦截会员卡激活",
      "summary": "MaxNow 的闻道 HTTP 白名单在建立连接前拒绝激活、激活预检和未知端点。清除 OpenClaw 仍允许自动激活的旧指引。版本 `1.0.12.01`。"
    },
    {
      "date": "2026-11-14",
      "title": "闻道会员卡改为手动激活",
      "summary": "普通预约和周日自动抢课只使用已激活卡，继续按到期日顺延。仅有需激活的适用卡时提示手动激活。版本 `1.0.12.00`。"
    }
  ]
};
