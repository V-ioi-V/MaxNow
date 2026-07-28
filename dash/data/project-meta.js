window.MAXNOW_PROJECT_META_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-07-28 11:44",
  "version": "1.0.5.35",
  "versionLabel": "v1.0.5.35",
  "branch": "feature/ballet-course-output",
  "commit": "7626f3b",
  "dirty": true,
  "dirtyLevel": "code",
  "deployNote": "feature/ballet-course-output · commit 7626f3b · 有未提交代码改动",
  "recentUpdates": [
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
    },
    {
      "date": "2026-07-28",
      "title": "修复 macOS Codex Token 上报中断死锁",
      "summary": "macOS 专用上报 clone 若在生成 `codex-macos-usage.*` 后、提交前被检查中断，下一轮会先确认没有越界改动，再恢复这两个任务自有生成文件并继续拉取、重新生成和上报。"
    },
    {
      "date": "2026-07-28",
      "title": "区分课表“可排队”与本人“排队中”",
      "summary": "修正源站普通“可排队”按钮被误判为本人候补的问题：普通课程保留“可排队”状态但不高亮，只有预约快照确认的本人候补课程才使用橙色整卡高亮；正式预约继续使用粉玫瑰整卡高亮。"
    }
  ]
};
