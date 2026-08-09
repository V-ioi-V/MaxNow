window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-08-09 12:23",
  "version": "1.0.9.10",
  "versionLabel": "v1.0.9.10",
  "branch": "feature/ballet-two-sunday-targets",
  "commit": "b4f7f1b",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-two-sunday-targets · commit b4f7f1b · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-08-09",
      "title": "自动抢课改为箭头所示两节周日课程",
      "summary": "Owner 明确只抢周日大教室 17:30–19:00 芭蕾 L1 与 19:00–20:00 肌肉素质，均不限老师；此前周二、周四、周五及旧周日晚间目标全部移除。"
    },
    {
      "date": "2026-08-09",
      "title": "周简报改为周日 18:00 结算",
      "summary": "芭蕾训练周简报从周日 20:00 提前到周日 18:00 切换本周，页面标签、画布截止时间、模板配置与说明文档同步更新；已完成课程口径保持不变。"
    },
    {
      "date": "2026-08-08",
      "title": "新增闻道单课取消 runner",
      "summary": "新增 `scripts/cancel_ballet.py` / `scripts/run_ballet_cancellation.sh`，只使用服务器 host-bound Session，一次精确处理一节当前活动预约；默认 dry-run，execute 必须显式确认。"
    },
    {
      "date": "2026-08-08",
      "title": "新增闻道抢课专用 Agent 入口",
      "summary": "`AGENTS.md` 只新增一条条件路由：闻道课程查询、预约、候补、取消、转课或相关执行入口变更前，必须完整读取 `WENDA_BOOKING_AGENT.md`，避免把完整操作约束堆进总入口；仓库检查同时把该专用文件列为必需文件。"
    },
    {
      "date": "2026-08-08",
      "title": "修复自动抢课课程与按钮错配",
      "summary": "闻道课表的展示记录曾在解析后排序，而预约按钮仍保持源 HTML 顺序；普通预约与 Fast Path 再按位置配对时，同时间课程可能把目标课程绑定到另一教室课程的按钮，导致语义匹配正确但实际提交错误课程。"
    }
  ]
};
