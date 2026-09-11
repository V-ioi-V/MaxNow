window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-09-11 18:59",
  "version": "1.0.11.20",
  "versionLabel": "v1.0.11.20",
  "branch": "bugfix/ballet-expired-membership-card",
  "commit": "a47db689",
  "dirty": false,
  "dirtyLevel": "clean",
  "deployNote": "bugfix/ballet-expired-membership-card · commit a47db689 · 干净",
  "recentUpdates": [
    {
      "date": "2026-09-11",
      "title": "课程卡支持展示已失效旧卡",
      "summary": "修复闻道会员卡页同时返回使用中卡与已失效旧卡时，旧卡缺少总次数导致全部芭蕾数据同步失败的问题。"
    },
    {
      "date": "2026-09-08",
      "title": "按当前页面懒加载 Dashboard 数据",
      "summary": "修复直接打开 `#ballet`、Token、豆奶等二级页时仍先等待整套 Home 数据的问题；现在先显示目标页，再只读取该页所需的数据源，芭蕾首开由 10 份数据请求收敛为 3 份，Token / 豆奶 / 生活各为 1 份。"
    },
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
    }
  ]
};
