window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-28 16:40",
  "version": "1.0.6.00",
  "versionLabel": "v1.0.6.00",
  "branch": "feature/ballet-booking",
  "commit": "7e654e2",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-booking · commit 7e654e2 · 有未提交代码改动",
  "recentUpdates": [
    {
      "date": "2026-07-28",
      "title": "增加芭蕾对话式显式预约",
      "summary": "新增精确课程预约脚本与 hardened transient runner；单课或多课先统一实时预检已有预约、余位、唯一课程卡和闻道规则，全部通过后再按输入顺序逐节提交并实时复核。"
    },
    {
      "date": "2026-07-28",
      "title": "记录芭蕾 Apple 日历与多课预约待办",
      "summary": "芭蕾 Later 新增私有 ICS / `webcal://` 订阅：Apple 设备首次确认后自动刷新预约和候补，链接可撤销且不得暴露 PHPSESSID、会员标识或源记录 ID。"
    },
    {
      "date": "2026-07-28",
      "title": "固定芭蕾实时课表的默认范围与格式",
      "summary": "Owner 泛问“有什么课程 / 有什么可以约的课”时，默认展示闻道实时返回的全部课型，不再只筛芭蕾；只有明确说“只看 / 仅看 / 只想看”某类课程时才按课型筛选。"
    },
    {
      "date": "2026-07-28",
      "title": "修复 Token 总账并发拉取漏更",
      "summary": "macOS 源账本已正常上报，但服务器 `11:10` 总账任务与另一条 Git 更新并发，因远端引用锁竞争退出；手动补跑后线上总账更新到 `11:28`，Codex macOS 来源时间更新到 `11:00`。"
    },
    {
      "date": "2026-07-28",
      "title": "增加芭蕾实时查询 Skill",
      "summary": "新增 `maxnow-ballet-live` Skill 和服务器实时查询入口；以后对话中询问课表、预约 / 候补、上课记录、老师、余位或课程卡时，固定通过 MaxNow 服务器的当前 PHPSESSID 直接读取闻道，不再用 Dashboard 缓存回答。"
    }
  ]
};
