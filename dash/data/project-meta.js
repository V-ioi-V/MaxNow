window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-09-08 19:53",
  "version": "1.0.11.16",
  "versionLabel": "v1.0.11.16",
  "branch": "bugfix/dounai-checkin-reminder",
  "commit": "195a7cd9",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "bugfix/dounai-checkin-reminder · commit 195a7cd9 · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-08-26",
      "title": "周安排不再回填已取消课程的旧抢课状态",
      "summary": "周安排比较芭蕾业务快照与 Fast Path 上次执行时间；当 `ballet.json` 已有更晚的成功同步时，预约、候补、完成与取消状态统一以该业务快照为准。"
    },
    {
      "date": "2026-08-25",
      "title": "最近课程改用深色卡面并让标签按整卡居中",
      "summary": "课程预约右侧标签组改为跨越课程信息与取消提示两行，桌面端以整张课程小卡为基准上下居中；预约 / 候补与级别标签继续保持横向单排。"
    }
  ]
};
