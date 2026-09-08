window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-09-08 20:30",
  "version": "1.0.11.18",
  "versionLabel": "v1.0.11.18",
  "branch": "bugfix/dounai-readonly-readback",
  "commit": "4bd0b943",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/dounai-readonly-readback · commit 4bd0b943 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-09-08",
      "title": "修复手动签到后豆奶页面未更新",
      "summary": "确认 Owner 已于 20:03 手动签到；豆奶 `/user/record` 的只读变更记录显示本次获得 865 MB、1 豆丁，基础与 VIP 有效期各延长 1.07 小时。"
    },
    {
      "date": "2026-09-08",
      "title": "豆奶改为手动签到并仅保留流量统计",
      "summary": "按 Owner 决定移除 root crontab 的 09:00 `MAXNOW-DOUNAL-CHECKIN`，服务器不再尝试签到或发送验证码提醒；原 crontab 已备份为 `/root/.openclaw/root-crontab-20260908-manual-checkin.bak`。"
    },
    {
      "date": "2026-09-08",
      "title": "恢复豆奶 09:00 签到预检与人工提醒",
      "summary": "修复 `/root/.openclaw/dounai_cron.sh` 在 `set -e` 下提前退出、验证码异常提醒无法可靠送达的问题；脚本现在显式保留签到退出码，再按成功、已签到、需要验证码和其他异常分别处理。"
    },
    {
      "date": "2026-09-08",
      "title": "恢复豆奶登录态并让流量同步失败关闭",
      "summary": "排查确认豆奶登录态于 9 月初失效，00:05 流量日结把 HTTP 401 页面解析成 0 条记录并继续写入新时间，导致“更新时间正常、实际流量停在 9 月 3 日”且 60 天历史逐日缩短。"
    },
    {
      "date": "2026-08-31",
      "title": "全部训练记录改为每周热力图",
      "summary": "“全部”范围把辨识度较低的历年单点折线改为周一至周日聚合的热力图，按年份分组并补齐首个训练周到最近成功同步周之间的零课周。"
    }
  ]
};
