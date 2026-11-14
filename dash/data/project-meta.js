window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-11-14 15:31",
  "version": "1.0.12.02",
  "versionLabel": "v1.0.12.02",
  "branch": "bugfix/restore-wenda-session-check",
  "commit": "3994b406",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/restore-wenda-session-check · commit 3994b406 · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-11-14",
      "title": "恢复闻道同步",
      "summary": "电脑微信重新登录后更新生产加密凭据，实时课表和预约查询通过。芭蕾页面同步于 09:13 完成，数据状态为 fresh。版本 `1.0.11.99`。"
    },
    {
      "date": "2026-11-08",
      "title": "周日抢课增加延迟放课补查",
      "summary": "14:20 的四轮课表扫描均成功且下周一至周六始终无课程时，同一任务在 14:21 再查一次。发现目标课后按原规则预约或候补，仍为空则结束。版本 `1.0.11.98`。"
    }
  ]
};
