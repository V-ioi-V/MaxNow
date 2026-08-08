# 闻道抢课 Agent 规则

处理闻道课程查询、预约、抢课、候补、取消、转课，或修改相关执行入口前，必须完整阅读本文件。本文件只规定认证通道、操作顺序和代码维护边界，不扩大 Owner 对任何写操作的授权。

## Session 优先级

- MaxNow 服务器已有有效、受保护的闻道 Session 时，所有已获 Owner 明确授权的闻道查询或写操作，都优先使用该 Session。
- 现有 runner 没有实现某项功能，只代表 runner 能力不足，不代表 Session 或闻道官方协议不支持该操作；不得因此直接改用微信、浏览器或其他交互登录渠道。
- 正确顺序固定为：先用保存的 Session 只读获取当前官方 HTML / 脚本并确认精确协议，再在 Owner 已授权范围内执行最小化、单次提交、失败关闭的写操作，最后用独立实时查询复核结果。
- 只有保存的 Session 不存在、已失效，或官方流程确实强制要求交互授权、验证码等步骤时，才可以考虑微信或浏览器；切换前必须先向 Owner 说明具体阻碍。
- PHPSESSID 继续按约课网站密码处理：不得写入 Git、前端、日志、聊天、环境变量或命令参数，不得输出其值或可识别指纹。

## 当前入口与能力边界

- `scripts/query_ballet_live.py` / `scripts/run_ballet_live_query.sh`：使用服务器保存的 Session 做最小范围实时只读查询和写后复核。
- `scripts/book_ballet.py` / `scripts/run_ballet_booking.sh`：Owner 显式指定课程后的普通预约入口；课程与按钮必须在同一 `.classtable` 块内原子绑定。
- `scripts/book_ballet_fast.py` / `scripts/run_ballet_booking_fast.sh`：周日 14:20 自动抢课入口；读取版本化目标配置，真实 mutation 严格串行并在结束后统一实时核验。
- `config/ballet-booking-fast.json`、`server/maxnow-ballet-booking-fast.*`：Fast Path 的目标与调度入口，不得绕过 Session、时间窗、唯一匹配、幂等和失败关闭边界。
- 当前 runner 没有取消、转课或支付能力。Owner 明确授权这类操作时，应先按本文件的 Session 优先顺序确认官方协议，再实现或使用最小受限入口；不能把 runner 的现状解释为必须操作微信。

## 维护规则

- 新增、删除或修改上述闻道抢课相关脚本、runner、配置、systemd 入口、Session 使用方式、匹配规则、mutation 协议或写后复核流程时，必须在同一分支同步更新本文件。
- 更新至少要反映受影响入口的当前职责、能力边界和安全顺序；如果行为未改变，也要确认本文件仍准确，不能让实现与 Agent 入口说明漂移。
- `AGENTS.md` 只保留指向本文件的条件路由，不在总入口重复展开本文件内容。

## 变更记录

- 2026-08-08：建立专用入口；固化服务器 Session 优先、协议先只读确认、单次最小提交、独立实时复核和交互登录降级边界，并纳入普通预约与 Fast Path 现有入口。
