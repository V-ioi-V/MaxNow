window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-11-14 09:23",
  "version": "1.0.12.01",
  "versionLabel": "v1.0.12.01",
  "branch": "bugfix/wenda-activation-transport-block",
  "commit": "b0a0bbd5",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/wenda-activation-transport-block · commit b0a0bbd5 · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-11-07",
      "title": "修正课表老师高亮",
      "summary": "锁定老师后，该老师的课程以原课型颜色和完整不透明度呈现，包括已经过去的课程。去掉锁定描边，其他老师的课继续置灰。解除锁定后，历史课程恢复常规淡化。版本 `1.0.11.97`，样式缓存 `styles.css?v=300`。"
    }
  ]
};
