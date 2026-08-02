# MaxNow 服务器操作说明

这个文件记录 MaxNow 服务器的 SSH 连接方式、前端静态站部署方式和常用排障命令。

## 服务器

```text
Host: 43.160.240.244
User: ubuntu
Domain: dash.maxnow.cn
Repo root: /var/www/maxnow-dashboard
Dash web root: /var/www/maxnow-dashboard/dash
Blog web root: /var/www/maxnow-dashboard/blog
Web server: nginx
```

本地 Windows 连接命令：

```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" ubuntu@43.160.240.244
```

一条命令执行远程检查：

```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" ubuntu@43.160.240.244 "hostname && whoami && uptime"
```

如果 SSH 在 `kex_exchange_identification` 阶段断开，先检查本地是否走了代理 / TUN 网卡。之前失败原因是 SSH 流量走了 `Meta` 代理网卡；关闭代理后，连接从 `WLAN` 出口恢复正常。

## 当前部署状态

2026-06-16 已完成首次静态站部署，2026-06-17 已切换为同仓库双出口部署：

```text
/var/www/maxnow-dashboard
```

该目录来自 GitHub 仓库；nginx 的两个站点根目录分别指向：

```text
dash.maxnow.cn -> /var/www/maxnow-dashboard/dash
blog.maxnow.cn -> /var/www/maxnow-dashboard/blog
```

Git 来源：

```text
https://github.com/V-ioi-V/MaxNow.git
branch: main
```

当前 nginx 配置：

```text
/etc/nginx/sites-available/maxnow-dashboard
/etc/nginx/sites-enabled/maxnow-dashboard
```

站点访问：

```text
https://dash.maxnow.cn
https://blog.maxnow.cn
```

当前 HTTPS 已启用，HTTP 请求会跳转到 HTTPS。`blog.maxnow.cn` 证书由 certbot 在 2026-06-17 申请，当前到期日为 2026-09-15，certbot 已配置自动续期。

`maxnow.cn` 当前权威 DNS 仍由 DNSPod 托管：

```text
achernar.dnspod.net
cylinder.dnspod.net
```

2026-07-10 曾短暂评估 Cloudflare Access，最终因 Zero Trust Free 仍要求付款方式而放弃；nameserver 已恢复到 DNSPod。服务器上保留 `cloudflared 2026.7.1` 二进制，但未安装 tunnel service、未配置 token、没有运行进程，不属于当前流量路径。删除该软件包前仍需 Owner 单独确认。

2026-07-10 已将私人 Dash 从浏览器原生 Basic Auth 弹窗升级为 MaxNow 自定义登录页：

```text
dash.maxnow.cn -> 自定义登录页 + nginx auth_request
session auth -> maxnow-auth.service (127.0.0.1:8765)
session cookie -> 7 天，HttpOnly + Secure + SameSite=Strict
dash page / assets / data -> 均需有效会话
blog.maxnow.cn -> 保持公开
credential file -> /etc/nginx/.htpasswd-maxnow (root:www-data 0640)
session secret -> /etc/maxnow-auth/session.key (root:www-data 0640)
security headers -> /etc/nginx/snippets/maxnow-security-headers.conf
nginx version -> hidden by server_tokens off
```

未认证访问 Dash 首页应 `302` 跳转 `/login`，登录页返回 `200`，直接访问 `/data/` 返回 `401` 且不再触发浏览器原生弹窗。`scripts/sync_system_status.py` 会把最终落到 `/login` 识别为 `Login` 健康状态。真实用户名、密码、哈希和会话密钥不得写入仓库或服务器手册。

2026-07-25 已完成 OpenClaw 与服务器入口加固：

```text
Tencent firewall -> 80/443 对公网开放；22 仅允许 Owner 当前公网 IPv4 /32
OpenClaw Gateway -> 仅监听 127.0.0.1:12123 和 [::1]:12123
unused public ports -> 12123/16980/3000 无腾讯云公网放行规则
Control UI -> allowInsecureAuth=false, dangerouslyDisableDeviceAuth=false
gateway auth -> 10 次/分钟，连续失败锁定 5 分钟
browser SSRF -> dangerouslyAllowPrivateNetwork=false
third-party plugin allowlist -> memory-tencentdb, openclaw-weixin
OpenClaw config/session files -> 0600
OpenClaw session directories -> 0700
Gateway service -> UMask=0077
```

Control UI 不再支持从公网直接打开。需要临时维护时，从 Owner 已获准的网络建立 SSH 隧道，并保持 Gateway 仍为 loopback：

```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" -L 12123:127.0.0.1:12123 ubuntu@43.160.240.244
```

本次配置和脚本修改前的 root-only 备份：

```text
/root/.openclaw/openclaw.json.20260725_224341.bak
/root/.openclaw/openclaw.json.20260725_224907.pre-allowlist.bak
/root/.config/systemd/user/openclaw-gateway.service.20260725_224557.bak
/root/.openclaw/workspace/skills/tencent-docs/generate_slide.js.20260725_2304.bak
```

深度审计从 `4 critical / 19 warn` 降至 `2 critical / 12 warn`。剩余两个 critical 均为静态代码模式提示：禁用且未进入 allowlist 的 Discord 插件包含用于音频转码的 `spawn`；腾讯文档幻灯片脚本仍需启动 `mcporter`，但已从 shell 字符串拼接改为 `execFileSync` 参数数组，消除了参数进入 shell 的路径。剩余 warn 主要来自禁用插件安装元数据，以及微信 / 腾讯云记忆插件正常的文件读取和网络发送能力；不要为了清零扫描数字盲目升级或删除插件，变更前应单独评估兼容性。

复验标准：

```text
nginx / maxnow-auth / ssh / openclaw-gateway -> active
ss -> 12123 仅 127.0.0.1 和 ::1；8765 仅 127.0.0.1
https://dash.maxnow.cn/ -> 未登录 302 到 /login
https://dash.maxnow.cn/data/dashboard.json -> 未登录 401
新建 OpenClaw session file -> 0600
噗噗 dedicated session -> 正常回复，不向微信真实通道投递测试消息
```

### 闻道 Session 持续生命周期实验（始于 2026-07-26）

Owner 已批准在 MaxNow 服务器上验证闻道 `PHPSESSID` 在持续活动下的最长寿命。该实验只读访问课程表，不具备预约、候补、取消或转课能力：

当前 v7 沿用 2026-07-27 在本机微信重新打开闻道页面后提取的会话，与 v3-v5 的旧会话属于不同凭据代次，寿命必须分别计算。v7 与 v6 属于同一凭据代次，只是把固定 30 天阶段安全交接为无限期阶段：

```text
current unit -> maxnow-wenda-session-lifetime-20260728-v7.service（active / transient）
credential -> /etc/credstore.encrypted/maxnow-wenda-session-v6.cred（root:root 0600 / host-bound）
probe -> /usr/local/lib/maxnow-wenda-session/probe_ballet_session.py（root:root 0555）
current private log -> /var/lib/maxnow-wenda-session-v7/server-lifetime-20260728-continuous-20min.jsonl（0600）
redacted snapshot -> /var/lib/maxnow-ballet-session-source/v7-continuous-20m.jsonl（root:maxnow-ballet-status 0640）
interval -> 1200 秒
credential-generation start -> 2026-07-27 00:26:55 Asia/Shanghai
v7 phase start -> 2026-07-28 20:23:14 Asia/Shanghai
scheduled end -> none
first v7 sample -> 2026-07-28 20:23:17 / HTTP 200 / authenticated / attempts=1
```

v7 首条样本没有观察到 `Set-Cookie` 或 Session 变化。这个结果只证明 20:23:17 时该会话仍有效；后续正常样本也只能扩展“持续活动下已确认有效”的证据，不能单独证明滑动过期、自动续期或空闲寿命。2026-07-27 12:01 起，该 Session 还执行过一次 Owner 批准的预约 / 上课记录只读同步，因此 12:01 后的证据只能称为“持续只读活动寿命”，不能再声称请求来源只有固定课程列表探针。2026-07-28 20:23 的交接先启动 v7 并确认首条 authenticated 样本及公开状态，再停止 v6；v6 的 132 个样本与 v7 按同一凭据代次连续统计。

上一代 v3-v5 已结束，保留为独立历史证据：

```text
previous terminal unit -> maxnow-wenda-session-lifetime-20260726-v5.service（failed / stopped_identity_expired）
probe -> /usr/local/lib/maxnow-wenda-session/probe_ballet_session.py（root:root 0555）
probe sha256 -> server CRLF bytes `75cf495f1abac3f5a9f2cedb73021a0905f384ad6d19f9cd7438342edc99ede4`；repository LF bytes `2a1451872515865a0edf7cfd79ecbd3399de1d806de8be4f0fb62f3f9a42c3b5`；换行归一化后内容一致
previous terminal log -> /var/lib/maxnow-wenda-session-v5/server-lifetime-20260726-2300-25min.jsonl（只读保留）
historical 10m log -> /var/lib/maxnow-wenda-session/server-lifetime-20260726-1906.jsonl（只读保留）
historical 20m log -> /var/lib/maxnow-wenda-session-v4/server-lifetime-20260726-1941-20min.jsonl（只读保留）
previous final interval -> 1500 秒
original start -> 2026-07-26 19:07:15 Asia/Shanghai
20m handoff -> 2026-07-26 19:41:46 Asia/Shanghai
25m handoff -> 2026-07-26 23:03:21 Asia/Shanghai
absolute end -> 2026-08-25 19:07:15 Asia/Shanghai
actual stop -> 2026-07-26 23:28:22 Asia/Shanghai（identity expired）
```

2026-07-26 19:41 将请求间隔从 600 秒调整为 1200 秒；23:03 再按 Owner 要求从 1200 秒调整为 1500 秒，请求频率降为每小时 2.4 次。v3 完成 4 次、v4 完成 11 次，v5 首次交接验证为第 16 个合并样本；截至 v5 首条，全部为 HTTP 200 / authenticated、`attempts=1`。23:28 的首个标准 25 分钟样本返回 HTTP 307 / expired，探针写入 `stopped_identity_expired` 后立即退出；最后认证仍为 23:03，已确认有效时长为 14,166 秒。三阶段累计 17 个样本，未观察到 `Set-Cookie`、Session 进程内变化、网络错误或重试。每次交接都先启动新 unit 并确认首条脱敏样本成功，才停止旧 unit。

v5 原本继承 30 天绝对截止时间，但身份失效优先触发了提前终止；不得把 2026-08-25 当成实际运行结束。v4 与 v5 的第一条即时请求都只算交接验证，23:28 才是 v5 的首个标准 25 分钟间隔证据。

安全边界：

- systemd 使用 `DynamicUser`、`ProtectSystem=strict`、`ProtectHome=yes`、`NoNewPrivileges` 和空 capability 集运行探针。
- v7 复用 v6 的 host-bound `LoadCredentialEncrypted` 文件，服务器没有持久化明文 Cookie；systemd 只在服务专属 `/run/credentials` 暂时解密，服务退出后自动清理。该凭据最初从本机受限快照经 SSH 标准输入直接转换；v4 / v5 的历史交接使用 `LoadCredential` 从上一运行中服务的凭据挂载读取，没有创建上传明文。
- 脚本只允许固定 URL `https://gm.wendaosoft.com/gm/weixin/classtable/simpleclass/54114/430`，拒绝 query、其他租户 / 课表、其他端口和写接口；凭据只接受单一 `PHPSESSID`，请求使用固定 Referer。
- 代码和 unit 均禁用代理；stdout 设为 `null`，避免脱敏 JSONL 再复制进 journald。日志不保存响应正文、Cookie 或 OAuth 信息，Session 指纹使用仅本次进程可比较的随机 HMAC；v3-v7 的 HMAC 密钥各自独立，禁止跨进程横向比较指纹值。
- 登录有效必须同时命中 `check_cardtypecourse` 与 `do_addbook` 两个课程页结构标记；普通 200、通用 JSON、OAuth / 登录页和无法判断的响应不会误报 authenticated。
- 任务收到身份失效即退出；连续 3 次未知 / 网络异常也会退出，避免页面变化或网络故障后无限请求。
- v7 使用 `WENDA_DURATION_SECONDS=0` 表示不设时间截止，systemd 的 `RuntimeMaxUSec=infinity`；“无限期”只移除计划结束时间，不覆盖上述安全停止条件。
- 这是 transient unit，没有 enable，也不会在服务器重启后自动恢复；因此不列入 Dash 云服务页的长期自动化清单。

`systemctl cat` 的 v7 去敏审计摘要如下。它是 transient unit，不能依赖 `restart` 自动恢复；若退出，先判断是否身份失效，再由 Owner 重新打开微信页面并建立新凭据代次：

```ini
[Service]
Type=simple
DynamicUser=yes
StateDirectory=maxnow-wenda-session-v7
StateDirectoryMode=0700
UMask=0077
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
CapabilityBoundingSet=
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
Restart=no
StandardOutput=null
StandardError=journal
LoadCredentialEncrypted=wenda.json:/etc/credstore.encrypted/maxnow-wenda-session-v6.cred
Environment=WENDA_INTERVAL_SECONDS=1200 WENDA_DURATION_SECONDS=0
ExecStart=/usr/bin/python3 /usr/local/lib/maxnow-wenda-session/probe_ballet_session.py
```

最终只读状态检查，不要为了监控额外请求闻道，也不要直接 `tail` 原始 JSONL：

```bash
sudo systemctl show maxnow-wenda-session-lifetime-20260728-v7.service \
  -p ActiveState -p SubState -p MainPID -p Result -p ExecMainStatus
python3 -m json.tool /var/lib/maxnow-ballet-session-status/public/ballet-session.json
sudo systemctl cat maxnow-wenda-session-lifetime-20260728-v7.service
```

需要人工提前停止时：

```bash
sudo systemctl stop maxnow-wenda-session-lifetime-20260728-v7.service
sudo test ! -e /run/credentials/maxnow-wenda-session-lifetime-20260728-v7.service/wenda.json
```

停止进程和删除本地 / 服务器凭据只能终止后续使用，不能证明闻道服务端 Session 已被吊销；如果没有安全的官方 logout / revoke 接口，结论中必须保留这一残余有效窗口说明。v3-v5 是同一旧会话的连续阶段；v6-v7 是另一代会话的连续阶段，必须从 2026-07-27 00:26:55 重新计时。两代实验验证的都是“持续活动时的寿命”，不能外推静默闲置过期时间，也不能仅凭正常样本宣称已证明自动续期。

#### Cloud 页脱敏 Session 状态发布

Cloud 页使用独立 `dash/data/ballet-session.json` / `.js` 展示实验状态；芭蕾页只保留薄连接状态。不能把实验状态写进课程 `ballet.*`，否则会错误刷新课程 `dataAsOf`。状态发布器只读上述本机 JSONL 与当前 systemd state，不发出任何网络请求：

```text
service -> maxnow-ballet-session-status.service
timer -> maxnow-ballet-session-status.timer
schedule -> 启动 2 分钟后，之后每 5 分钟
live log exporter -> maxnow-ballet-session-log-export.service + .timer（root / 每 5 分钟 / 无网络）
config -> /etc/maxnow-ballet/session-experiment.json（root:maxnow-ballet-status 0640；不含凭据）
deployed script -> /usr/local/lib/maxnow-ballet-session-status/sync_ballet_session_status.py（root:root 0555）
runtime user -> maxnow-ballet-status（system / no-login / no capabilities）
runtime output -> /var/lib/maxnow-ballet-session-status/public/ballet-session.json + ballet-session.js
public URL -> authenticated nginx aliases /data/ballet-session.json + ballet-session.js
```

公开字段使用固定 allowlist：状态、实验 / 阶段起始、最近检查 / 最近认证 / 下次检查、可空计划截止、当前 20 分钟间隔、截至最后认证样本的已验证秒数、阶段 / 总样本数、是否观察到 Session 轮换 / `Set-Cookie`、最近 HTTP / 登录状态和受控错误。当前无限期阶段发布 `scheduledEndAt: null`，Cloud 卡不展示计划结束日期。禁止输出 Session 值或指纹、run ID、unit / 日志路径、URL、响应摘要 / 正文、凭据版本或会员信息。

状态发布 oneshot 不能以 root 运行，也不能直接执行 ubuntu / Git 可更新的仓库脚本。专用无登录用户只运行 root-owned `0555` 固定副本；unit 使用空 capability 集，并以 `InaccessiblePaths` 遮蔽 `/run/credentials` 与 `/etc/credstore.encrypted`。已结束阶段的日志继续以 root-owned 只读硬链接或快照保留证据。活动中的 v7 日志不能硬链接，因为探针会拒绝 link count 大于 1 的日志；root oneshot 每 5 分钟把已经脱敏的 JSONL 原子复制为 `root:maxnow-ballet-status 0640` 快照，发布器随后只读快照。转存 unit 固定读写路径、禁用网络，不能访问凭据；`/var/lib/private` 的 `0700` 边界保持不变。

安装与检查：

先创建只包含实验拓扑、不包含任何 Session / Cookie 的受限配置。当前 v7 配置如下；新凭据代次必须重新设置 `experimentStartedAt`，不能把旧阶段寿命接在新 Session 上：

```json
{
  "schemaVersion": 1,
  "experimentStartedAt": "2026-07-27T00:26:55+08:00",
  "scheduledEndAt": null,
  "currentPhase": "v7-continuous-20m",
  "phases": [
    {
      "key": "v6-20m",
      "unit": "maxnow-wenda-session-lifetime-20260727-v6.service",
      "log": "/var/lib/maxnow-ballet-session-source/v6-20m.jsonl",
      "intervalSeconds": 1200,
      "handoffValidationSamples": 0
    },
    {
      "key": "v7-continuous-20m",
      "unit": "maxnow-wenda-session-lifetime-20260728-v7.service",
      "log": "/var/lib/maxnow-ballet-session-source/v7-continuous-20m.jsonl",
      "intervalSeconds": 1200,
      "handoffValidationSamples": 1
    }
  ]
}
```

v7 已在服务器安装活动日志转存 unit。它只能读取固定的 v7 脱敏 JSONL，并用临时文件 + `mv` 原子替换状态源；不要让非 root 状态发布器直接穿过 `/var/lib/private`，也不要为活动日志创建硬链接。常用检查：

```bash
sudo systemctl cat maxnow-ballet-session-log-export.service \
  maxnow-ballet-session-log-export.timer
sudo systemctl is-active maxnow-ballet-session-log-export.timer \
  maxnow-ballet-session-status.timer \
  maxnow-wenda-session-lifetime-20260728-v7.service
sudo systemctl start maxnow-ballet-session-log-export.service
sudo systemctl start maxnow-ballet-session-status.service
python3 -m json.tool /var/lib/maxnow-ballet-session-status/public/ballet-session.json
sudo test "$(stat -c '%U:%G %a' /var/lib/maxnow-ballet-session-source/v7-continuous-20m.jsonl)" \
  = "root:maxnow-ballet-status 640"
sudo test "$(stat -c '%U:%G %a' /etc/maxnow-ballet/session-experiment.json)" = "root:maxnow-ballet-status 640"
sudo test "$(stat -c '%U:%G %a' /var/lib/maxnow-ballet-session-status/public/ballet-session.json)" = "maxnow-ballet-status:maxnow-ballet-status 644"
sudo -u maxnow-ballet-status test ! -r /etc/credstore.encrypted/maxnow-ballet-wenda.cred
python3 scripts/check.py
```

两个 5 分钟任务只做本地脱敏日志转存和状态发布，不是 20 分钟闻道请求频率，也不是 Session 续期器。探针失效 / 延迟 / 中断后，页面冻结最后一次 `authenticated` 时长并显示安全原因。

### 芭蕾生产只读同步（每日 / 月度定时已启用）

芭蕾页面与脱敏缓存已经部署。生产 rolling timer 每天 09:00、12:00、15:00、18:00、22:00 刷新全部数据，并在周日 14:30 额外读取抢课后发布的下周课表，与 14:20 自动抢课关键窗口错开；原每日 00:00 触发已移除。每月 1 日 00:47 继续执行 full 只读同步。长期 enable gate 为 root `0600`，两个 timer 均应保持 `enabled / active / waiting`。身份失效时同步器会停止后续网络尝试并保留旧数据，直到非敏感凭据版本变化。

目标运行边界：

```text
service -> maxnow-ballet-sync.service
timer -> maxnow-ballet-sync.timer
schedule -> Asia/Shanghai 每天 09:00 / 12:00 / 15:00 / 18:00 / 22:00 + 周日 14:30
monthly service -> maxnow-ballet-full-sync.service
monthly timer -> maxnow-ballet-full-sync.timer
monthly schedule -> Asia/Shanghai 每月 1 日 00:47
private state -> /var/lib/maxnow-ballet/
credential -> /etc/credstore.encrypted/maxnow-ballet-wenda.cred
credential version -> /etc/maxnow-ballet/credential-version
enable gate -> /etc/maxnow-ballet/enable-sync
frontend read model -> /var/www/maxnow-dashboard/dash/data/ballet.json + ballet.js
current state -> 代码 / page 已部署；已保留 2 条 Owner 手工软开课；enable gate 存在且两个生产 timer 为 enabled / active / waiting；2026-08-01 00:40 修复账本属主后 rolling 同步成功
experiment status -> v7 每 20 分钟课程列表探针无限期运行；2026-07-27 12:01 曾执行一次额外预约 / 上课记录只读同步；本地 exporter / status timer 每 5 分钟转存并发布 ballet-session.*，不访问闻道
```

同步器只允许已确认的闻道只读 GET 页面：

- 上课记录索引：`/gm/weixin/my/checkrecord/54114`
- 预约记录索引：`/gm/weixin/my/bookrecord/54114`
- 课程卡概览：`/gm/weixin/my/mycard/54114`
- 日期课表：`/gm/weixin/classtable/simpleclass/54114/430/YYYY-MM-DD`
- 从预约索引发现的同租户数字详情：`/gm/weixin/my/bookrecordone/54114/<digits>`

禁止 POST，禁止调用预约、取消、候补、转课、会员登录、课程卡详情或未知接口。日期课表路径必须严格匹配 ISO 日期。平时抓取本周 7 天；课表仍以周日 14:20 为发布边界，生产定时任务在 14:30 额外抓取下周 7 天，只有下周存在课程时才输出“本周日 + 下周”8 天。同步失败只更新安全状态，不清空最后成功的 records、summary、aggregates、预约、课程卡或课表快照。

生产凭据规则：

- `PHPSESSID` 只能以服务器 host-bound systemd 加密凭据保存，并由 `LoadCredentialEncrypted` 放入服务专属 `/run/credentials`；不得写入 Git、普通配置文件、环境变量、命令参数、日志、前端、备份或聊天。
- 创建或刷新凭据时，应从受控输入流直接交给 `systemd-creds encrypt --with-key=host`，写入临时文件后以 root `0600` 原子替换 `/etc/credstore.encrypted/maxnow-ballet-wenda.cred`。不要 `echo`、`cat`、打印或复制明文值，也不要把值留进 shell history。
- 只允许记录非敏感的 `credentialVersion`（例如加密文件版本 / 修改代次）；不得记录 Session 原文、可逆摘要或跨系统可关联指纹。
- Owner 刷新流程是：在电脑微信重新登录并打开闻道页面，使用本地受控提取流程取得新会话，再通过不回显的加密输入流更新服务器凭据。任何文档、日志和聊天只记录“凭据已更新”和安全版本，不记录值。

私有账本手工维护规则：

- `/var/lib/maxnow-ballet/*.json` 的生产写入身份固定为 `ubuntu:www-data`；私有账本和状态快照固定 `0600`。手工补录优先使用 `sudo -u ubuntu -g www-data` 运行仓库内归一化、校验和原子写入逻辑，禁止直接用 `sudo python3` 写完后只以 root 复验。
- `scripts/sync_ballet.py` 的原子写入会在 root 替换已有普通单链接文件时继承原 uid / gid，避免临时文件替换把属主改成 root；这只是防误操作兜底，不能替代写后检查。
- 每次手工维护完成后固定执行下面的属主、服务用户读取和 schema 校验。任一项失败就停止，不启动同步，也不能宣称维护完成：

```bash
sudo test "$(stat -c '%U:%G %a' /var/lib/maxnow-ballet/attendance-ledger.json)" = "ubuntu:www-data 600"
sudo -u ubuntu test -r /var/lib/maxnow-ballet/attendance-ledger.json
cd /var/www/maxnow-dashboard
sudo -u ubuntu python3 -B - <<'PY'
from pathlib import Path
from scripts import sync_ballet as ballet
ledger = ballet.safe_read_json(
    Path("/var/lib/maxnow-ballet/attendance-ledger.json"),
    ballet.empty_ledger(),
)
ballet.validate_ledger(ledger)
print("service-user-ledger-read=ok")
PY
```

- 最近一次同步失败时，先看 `systemctl show` 的 `Result / ExecMainStatus` 和脱敏 `ballet-sync.log`，再检查上述属主与服务用户读取。同步器必须保留最后成功课程数据，并尽力把安全错误状态发布到 `ballet.*`；芭蕾页顶部应显示红色“同步失败”，不能继续显示“已同步”。

2026-08-01 00:00 rolling 同步曾因 2026-07-30 手工补录通过 root 原子替换 `attendance-ledger.json`、留下 `root:root 0600` 而以 `parse_error / exit 4` 失败。00:39 将该文件恢复为 `ubuntu:www-data 0600`，以 `ubuntu` 完成 JSON 与 ledger 校验后，于 00:40 手动启动既有 rolling 只读同步；结果为 `success / exit 0`，`dataAsOf=2026-08-01T00:39:46+08:00`、4 条上课记录、3 条未来预约和 7 天课表，未提交预约、候补、取消或转课。后续代码补上 root 原子写属主继承、预检失败公开状态和页面“同步失败”标识。

2026-08-01 Owner 将 rolling 整体刷新日程调整为每天 09:00、12:00、15:00、18:00、22:00，并明确保留周日 14:30 抢课后刷新；每日 00:00 触发删除。月度 full、20 分钟 Session 探针和 14:20 自动抢课均不变。主分支 `6491a96` 通过 Git bundle 快进部署，备份位于 `/home/ubuntu/maxnow-deploy-backups/20260801-103950-ballet-refresh-schedule`，运行态 project meta / status 的部署 stash 为 `159313f124754113baa447215e0e1a44c7468590`。切换 timer 时虽然没有手动启动 service，但 `Persistent=true` 仍将当天已错过的 09:00 判定为待补跑，于 10:40:13 自动执行一次 rolling 只读同步，10:40:28 以 `success / exit 0` 结束并将 `dataAsOf` 更新为 10:40:13；没有提交预约、候补、取消或转课。后续下一次触发为 12:00，六个 `OnCalendar` 均正确。以后在白天调整 persistent timer 且不希望补跑时，必须先停止旧 timer，再更新 stamp、安装 unit、`daemon-reload` 并重新启动 timer；不能在旧 timer 仍 active 时只触碰 stamp。

2026-07-26 21:23 已在服务器内部把 v4 生命周期实验当前的临时 systemd credential 密封为上述 host-bound 加密凭据，并用只写临时输出的解密自检确认可用后立即删除临时明文；全过程没有把值输出、下载或写入仓库。加密文件为 root `0600`。本机没有完整 TPM 保护，systemd host key 位于服务器 root 管理的 `/var/lib/systemd/credential.secret`；因此它能防止普通文件读取和误入 Git / 日志，但拥有服务器 root 权限的人仍可解密，不能把它描述成硬件不可导出密钥。生产同步仍未发起任何请求。

2026-07-26 22:12 已部署主分支 `7a57225`（版本 `1.0.5.00`），安装四个生产 unit 模板并完成 `systemd-analyze verify`、Linux fixture tests、`scripts/check.py`、`nginx -t` 与前端 read model 脱敏校验。两个 timer 均为 `disabled / inactive`，两个 service 均为 `inactive`，enable gate 不存在；部署过程没有启动同步器，也没有向闻道增加请求。部署前服务器运行数据备份保留在 `/home/ubuntu/maxnow-deploy-backups/20260726-220836-before-ballet-module`，原有 runtime 数据已恢复。部署完成时 v4 实验仍为 active，权威日志更新时间在一个 20 分钟周期内。

2026-07-27 00:14 已部署主分支 `46f8dce`（版本 `1.0.5.03`）的脱敏 Session 状态发布器。`maxnow-ballet-session-status.timer` 为 `enabled / active / waiting`，oneshot 最近结果为 `success / 0`；它每 5 分钟只读本机日志，不访问闻道。三份已停止日志的 inode 固定为 `root:maxnow-ballet-status 0440`，通过 `/var/lib/maxnow-ballet-session-source` 的同 inode 硬链接供专用无登录账号读取，`/var/lib/private` 及三个原目录均保持 `0700`。公开 read model 校验为 `auth_required`、历史间隔 25 分钟、最后认证 23:03:21、最后检查 23:28:22、已确认 14,166 秒、三阶段样本 4 / 11 / 2；无 Session 值、指纹、内部路径或响应正文。`scripts/check.py`、`nginx -t`、源文件与安装副本比对、硬链接设备 / inode、权限和新鲜度均通过；未登录 `/`、`/data/ballet-session.json`、公开 Blog 分别返回 302 / 401 / 200。生产每日 / 月度 timer 继续 `disabled / inactive`，enable gate 不存在，部署未向闻道新增请求。部署备份保留在 `/home/ubuntu/maxnow-deploy-backups/20260727-001331-before-ballet-source-final`。

2026-07-27 00:26 Owner 建立新微信会话后，本机只在内存解密最新 `gm.wendaosoft.com` Cookie 并确认与旧会话不同；新凭据经 SSH 标准输入直接密封为 `/etc/credstore.encrypted/maxnow-wenda-session-v6.cred` 和新的生产 `/etc/credstore.encrypted/maxnow-ballet-wenda.cred`，均为 root `0600`，没有在服务器持久化明文。00:26:55 启动 v6 每 20 分钟 transient 探针，00:26:56 首条为 HTTP 200 / authenticated、`attempts=1`、无 `Set-Cookie` / Session 变化。新增 `maxnow-ballet-session-log-export.timer` 每 5 分钟原子转存活动脱敏日志，随后由非 root 状态发布器生成页面数据；00:29 公开状态为 `running`、间隔 20 分钟、样本 1、下一次 00:46:55。生产每日 / 月度 timer 及 enable gate 继续关闭。

2026-07-27 12:01 已部署主分支 `e5d10258` 的多节预约展示并完成 Owner 批准的首次真实 rolling 同步。部署前运行时数据和 Git 差异备份在 `/home/ubuntu/maxnow-deploy-backups/20260727-bookings-tDzq1X`，服务器 Git remote 从失效的 `ssh.github.com:443` 切回与现有 `gh` 登录一致的 HTTPS。首次启动因非敏感凭据版本包含 `:` / `+` 在网络请求前安全退出；规范化为 `v6-20260727T002655-0800` 后成功，PHPSESSID 加密文件未改动。成功同步发出 7 个 allowlist GET，写入 1 条实际上课记录和 3 条未来正式预约；同步后 gate 已删除，两个生产 timer 仍为 disabled。服务器项目检查和状态发布器 oneshot 均通过。12:01 后的 v6 证据包含这组额外只读请求，不再属于“仅固定课程列表 GET”的纯实验阶段。

2026-07-27 14:23 已部署主分支 `6955c302`（版本 `1.0.5.07`）的“所有预约 + 整体上课统计”页面。部署前 Git 运行数据和 `/var/lib/maxnow-ballet` 私有账本备份在 `/home/ubuntu/maxnow-deploy-backups/20260727-ballet-stats-TqpdiR`；服务器检查通过。随后使用仓库同步模块的本地归一化、校验与原子写入函数补入 Owner 明确提供的 2026-07-25 11:30–12:30 李俊软开课，未访问闻道、未读取 PHPSESSID、未创建 enable gate。手工记录使用 `manual` 稳定键，read model 当前为 2 节 / 150 分钟历史、3 条未来预约和 1 条手工记录；每日 / 月度 timer 继续 disabled，v6 20 分钟探针继续 active。内置浏览器通过临时 SSH loopback 读取服务器静态文件完成真实数据与 390px 几何验收，临时 HTTP 服务和隧道在验收后已停止。

2026-07-27 14:57 临时创建 enable gate 完成一次 Owner 要求的 rolling 只读复查，成功后立即删除 gate；每日 / 月度 timer 继续 disabled。复查缓存仍只有 3 条未来预约，随后用同一 host-bound 凭据在受限 transient unit 中各执行一次约课索引和排队详情 GET，只输出脱敏解析字段：索引实际包含 3 条“已预约”、1 条“排队中”和 1 条“已上课”，排队详情状态为“等候中, 排队序号 4”。根因是同步器只接受精确的“排队中 / 候补中”，已在 `1.0.5.08` 将“等候中”前缀归一为 `waitlist` 并补回归测试。诊断未输出记录 ID、响应正文或凭据，备份位于 `/home/ubuntu/maxnow-deploy-backups/20260727-booking-refresh-rN6L2e`。

2026-07-27 15:04 已部署主分支 `34209b91`（版本 `1.0.5.08`），部署前运行数据和芭蕾私有状态备份在 `/home/ubuntu/maxnow-deploy-backups/20260727-waitlist-fix-mTtO1I`。服务器 12 项芭蕾同步测试和全仓检查通过；随后临时创建 enable gate 执行一次 rolling 只读同步并立即删除。最终 read model 为 2 节 / 150 分钟上课历史、3 条 `booked` 和 1 条 `waitlist`；同步服务 `success / 0`，每日 / 月度 timer 继续 disabled，v6 20 分钟实验仍 active。

2026-07-27 15:18 已部署主分支 `f8f96c83`（版本 `1.0.5.09`）的芭蕾紧凑页头：下一节预约移入页头右半区，原独占整行大卡删除。部署前页面与运行数据备份在 `/home/ubuntu/maxnow-deploy-backups/20260727-ballet-header-L4WEU5`；服务器全仓检查通过，真实预约缓存继续保持 3 条 `booked` + 1 条 `waitlist`。本次部署未访问闻道、未创建 enable gate；每日 / 月度 timer 继续 disabled，v6 20 分钟实验仍 active。

2026-07-27 15:22 已部署主分支 `921769c4`（版本 `1.0.5.10`）的预约状态颜色与星期排版：`booked` 保持粉玫瑰色，`waitlist` 改为橙色，星期移到日期下方。部署前页面与运行数据备份在 `/home/ubuntu/maxnow-deploy-backups/20260727-booking-status-colors-Z1pKnP`；服务器全仓检查通过，预约缓存仍为 3 条 `booked` + 1 条 `waitlist`。本次部署未访问闻道、未创建 enable gate；每日 / 月度 timer 继续 disabled，v6 20 分钟实验仍 active。

2026-07-27 15:27 已部署主分支 `83bb5aaf`（版本 `1.0.5.11`），将芭蕾标题和下一节预约修正为两个同级独立等宽 tab，不再内嵌。部署前页面与运行数据备份在 `/home/ubuntu/maxnow-deploy-backups/20260727-ballet-sibling-tabs-wEvlvr`；服务器全仓检查通过，预约缓存仍为 3 条 `booked` + 1 条 `waitlist`。本次部署未访问闻道、未创建 enable gate；每日 / 月度 timer 继续 disabled，v6 20 分钟实验仍 active。

2026-07-27 15:44 已部署主分支 `04d6413`（版本 `1.0.5.12`），将右侧下一节预约 tab 的标题和课程内容组整体居中，状态 pill 保持右上角。部署前运行数据备份在 `/home/ubuntu/maxnow-deploy-backups/ballet-center-sHXx74sc`；服务器全仓检查通过，预约缓存仍为 3 条 `booked` + 1 条 `waitlist`。本次部署未访问闻道、未创建 enable gate；每日 / 月度 timer 继续 disabled。

2026-07-27 16:24 已部署主分支 `df6fa7e`（版本 `1.0.5.13`），撤销下一节预约的固定宽度居中，改为日期 / 弹性课程信息 / 状态三段式自适应布局，并在 `1200px` 以下提前堆叠顶部两个 tab。部署前运行数据备份在 `/home/ubuntu/maxnow-deploy-backups/ballet-adaptive-z5IQdSnY`；服务器全仓检查通过，预约缓存仍为 3 条 `booked` + 1 条 `waitlist`。本次部署未访问闻道、未创建 enable gate；每日 / 月度 timer 继续 disabled。

2026-07-27 16:38 已部署主分支 `1724fb7`（版本 `1.0.5.14`），移除共享 hover 规则强制覆盖的纯白背景，使各详情页卡片在上浮、加强边框和阴影时继续保留原有白底或轻主题渐变。部署前运行数据备份在 `/home/ubuntu/maxnow-deploy-backups/card-hover-3q1eOwVm`；服务器全仓检查通过，预约缓存仍为 3 条 `booked` + 1 条 `waitlist`。本次部署未访问闻道、未创建 enable gate；每日 / 月度 timer 继续 disabled。

身份与错误处理：

- `AUTH_REQUIRED`、`WX_OAUTH_REQUIRED`、`MEMBER_LOGIN_REQUIRED` 立即停止本轮和后续自动重试，保留旧缓存并将 read model 标记为需要重新登录。
- 在 `credentialVersion` 变化前，timer 即使再次触发也只更新或保留阻断状态，不向闻道发起请求，避免失效凭据反复打站点。
- 页面只显示脱敏原因、最近尝试时间、最后成功时间和“请在电脑微信重新登录并刷新凭据”；不得显示 Cookie、Session 指纹、手机号、会员标识、原始响应或内部凭据路径。
- 网络抖动可以有限重试；页面结构变化、解析歧义或无法确认身份状态时 fail closed，并保留最后成功缓存。

新凭据就绪后的启用顺序：

1. 先按本节规则写入新的 host-bound 加密凭据，不复用实验 unit 的临时 `/run/credentials` 路径；若重建生命周期探针，按 Owner 最新要求使用 1200 秒（20 分钟），不要改写已结束 v5 的 1500 秒历史配置或日志。
2. 用本地脱敏样本完成 parser / 去重测试；首次真实同步只允许已确认的 GET 路径。
3. 检查私有账本 `0600`、read model 无敏感字段、重复同步不增加历史数量、失败时旧缓存仍在。
4. 创建 root 管理的 `/etc/maxnow-ballet/enable-sync` 后，启用并启动 `maxnow-ballet-sync.timer` 与 `maxnow-ballet-full-sync.timer`，确认 rolling timer 包含每天 09:00、12:00、15:00、18:00、22:00 和周日额外 14:30，且不再包含每日 00:00；full timer 为每月 1 日 00:47。不要把测试性即时请求算作定时任务证据。
5. 更新 Cloud 页自动化清单和系统状态来源，并在 `UPDATE_LOG.md` 记录真实启用时间与脱敏结果。

#### 芭蕾对话式实时查询

Owner 在对话中询问芭蕾课表、预约 / 候补、上课记录、老师、余位或课程卡时，使用独立实时查询入口，不读取 `dash/data/ballet.*`、`/var/lib/maxnow-ballet`、浏览器缓存或旧对话结果：

```bash
cd /var/www/maxnow-dashboard
scripts/run_ballet_live_query.sh timetable --from-date 2026-07-28 --through-date 2026-08-03
scripts/run_ballet_live_query.sh bookings
scripts/run_ballet_live_query.sh attendance --from-date 2026-07-01 --through-date 2026-07-31
scripts/run_ballet_live_query.sh membership
```

从 Owner 电脑调用时固定先 SSH 到 `ubuntu@43.160.240.244`，再在仓库根目录运行同一入口。成功结果必须同时包含 `source: wenda-live`、`status: success`、`live: true` 和当前 `fetchedAt`；任何失败都明确表示本次没有实时数据，禁止回退缓存。

运行器为每次查询创建 `--collect` 临时 systemd unit，通过 `LoadCredentialEncrypted` 把 `/etc/credstore.encrypted/maxnow-ballet-wenda.cred` 解密到 unit 专属 `%d` 目录。unit 使用 `DynamicUser`、`ProtectSystem=strict`、`ProtectHome=yes`、`NoNewPrivileges`、空 capability 集和 120 秒运行上限；命令结束后 unit 与解密凭据目录一并清理。查询脚本不接受输出文件或状态目录，不读取 / 写入 Dashboard 缓存和私有账本。

实时入口只允许四种 scope、ISO 日期和既有 GET allowlist；课表单次最多 14 天，预约 / 上课明细最多 200 条。输出不得包含源记录 ID、会员标识、原始 HTML、Cookie、响应正文、凭据路径、unit 名称或内部日志。不要直接解密、打印、复制或散列 PHPSESSID。

#### 芭蕾对话式显式预约

只在 Owner 当前请求中明确要求预约精确课程时使用。输入最多 10 节，每节必须同时给出日期、开始 / 结束时间、课程名、老师和教室。先以 `confirm:false` 做实时统一预检；全部目标为 `ready` 或 `already_booked` 且 `mutationAttempts=0` 后，再将同一份输入仅改为 `confirm:true` 执行：

```bash
cd /var/www/maxnow-dashboard
printf '%s' '{"courses":[{"date":"2026-08-20","startTime":"19:00","endTime":"20:00","courseName":"示例课程","teacher":"示例老师","venue":"示例教室"}],"confirm":false}' \
  | scripts/run_ballet_booking.sh dry-run

printf '%s' '{"courses":[{"date":"2026-08-20","startTime":"19:00","endTime":"20:00","courseName":"示例课程","teacher":"示例老师","venue":"示例教室"}],"confirm":true}' \
  | scripts/run_ballet_booking.sh execute
```

runner 使用与实时查询相同的 host-bound 加密凭据和 hardened transient systemd unit。dry-run 可调用闻道固定的课程卡资格与规则检查 POST，但不会调用 `do_addbook`。execute 在统一预检通过后按输入顺序逐节重检并提交，每节最多一次 `do_addbook`，随后从实时预约记录验证；任何身份失效、规则变化或未知结果都会停止后续课程，未知结果禁止重试。脚本不支持取消、转课、支付、登录、候补写入或任意 POST，也不把多课预约伪装成可回滚事务。

成功后运行 `scripts/run_ballet_live_query.sh bookings` 做独立实时复核，并启动一次 `maxnow-ballet-sync.service` 刷新页面脱敏预约快照。不得在命令、日志或记录中保存 PHPSESSID、卡片 / 会员 / 课程源 ID、原始响应或真实执行参数。

2026-07-28 16:44 已部署主分支 `5389624`（版本 `1.0.6.00`）的芭蕾对话式显式预约。部署前公开运行数据与 root-only 芭蕾私有状态备份在 `/home/ubuntu/maxnow-deploy-backups/20260728-1643-ballet-booking`；拉取后恢复服务器运行数据，并保留新版本 `project-meta.*` / `project-status.*`。首次真实单课提交只产生一次 mutation，脚本内验证和独立实时预约查询均为 `booked`；最终代码再次 dry-run 返回 `already_booked` 且 `mutationAttempts=0`。生产 rolling service 随后成功刷新页面脱敏预约快照，目标记录为 `booked`、`dataAsOf=2026-07-28T16:43:38+08:00`。服务器全仓检查与 `nginx -t` 通过，Dash 匿名访问 `302`、Blog `200`。

#### 芭蕾周日自动抢课 Fast Path

Owner 已单独批准当前五节固定课程在北京时间每周日 14:20 无人值守预约。关键路径不经过 Codex、Skill、OpenClaw 或 SSH：

```text
service -> maxnow-ballet-booking-fast.service
timer -> maxnow-ballet-booking-fast.timer
arm -> Sunday 14:19:35 Asia/Shanghai
submit -> script waits until 14:20:00 Asia/Shanghai
enable gate -> /etc/maxnow-ballet/enable-fast-booking
config -> /var/www/maxnow-dashboard/config/ballet-booking-fast.json
private state -> /var/lib/maxnow-ballet-booking-fast/state.json（root 0600）
public state -> /var/lib/maxnow-ballet-booking-fast-public/ballet-booking-fast.json + .js
public URL -> authenticated no-store aliases /data/ballet-booking-fast.json + .js
credential -> /etc/credstore.encrypted/maxnow-ballet-wenda.cred
```

固定优先级先按课程 `芭蕾 L1 > 软开`，再在同一课程内按日期 `周六 > 周日 > 周五 > 其他日期`。当前实际提交顺序：

1. 周五 19:45–21:15，芭蕾 L1，大教室，不限老师。
2. 周二 19:45–21:15，芭蕾 L1，大教室，不限老师。
3. 周五 18:45–19:45，软开，大教室，不限老师。
4. 周二 18:45–19:45，软开，大教室，不限老师。
5. 周四 18:45–19:45，软开，大教室，不限老师。

服务在 14:19:35 先用当前日期课表做一次只读会话预热；14:20 后用最多 3 个 worker 并发读取三个目标日期课表，同一日期的多个目标共享一次课表响应。课程卡资格和闻道规则由最多 2 个 worker 提前预检，完成超过 8 秒则在提交前重新预检。HTTPS 连接池最多保留 3 条 keep-alive 连接。随后严格按上述顺序逐节执行唯一语义确认和 `do_addbook`；任意时刻最多只有一个真实预约 / 候补 mutation。全部提交后，预约详情可以最多 3 路并发只读核验。匹配字段为日期、课型 / 等级、起止时间和教室，并且必须恰好命中一节；老师不参与匹配或 occurrence 幂等键，临时代课不会阻止目标执行。`available` 执行预约；`queue_available` 只有在仓库配置显式设置 `allowWaitlist=true` 时执行候补；已预约或已排队不重复提交。网络波动、发布延迟、课程卡尚未开放、规则短暂未就绪或 mutation 明确返回 `NOTOPEN` 时，首次失败后最多重试 3 次，间隔为 80 / 160 / 320ms；明确已满、已停止、无卡或不可约时直接进入下一节。

每节是独立失败域：一节失败或 mutation 结果未知都继续后续目标。未知 mutation 可能已经被闻道接受，因此本节绝不重复 POST，只在全部课程处理结束后统一查询实时预约记录；若查到则按 `bookingStatus=booked` 或 `waitlist` 回填，候补存在正整数位次时同时发布 `waitlistPosition`，否则保留“结果待确认”。只有 `auth_required`、配置错误或页面结构变化等全局问题才停止后续课程。fast path 单请求超时为 5 秒，避免一次网络故障长期占住后续高优先级目标。

私有 occurrence 哈希和 `terminalOutcomes` 只用于避免同一周目标重复提交并区分预约 / 候补结果；公开状态不得包含 course / class table / customer / card ID、PHPSESSID、响应正文、凭据路径、unit 名或日志路径。累计预约数与累计候补数分开记录，以闻道明确成功号或统一核验结果为准；统一核验不可用时页面显示“已提交，待核验”，不能重试。公开逐课结果可记录预约 / 候补状态、候补位次、尝试次数和脱敏耗时，不能保存请求 URL、源 ID 或响应正文。

安装与首次启用：

```bash
cd /var/www/maxnow-dashboard
sudo install -m 0644 server/maxnow-ballet-booking-fast.service \
  /etc/systemd/system/maxnow-ballet-booking-fast.service
sudo install -m 0644 server/maxnow-ballet-booking-fast.timer \
  /etc/systemd/system/maxnow-ballet-booking-fast.timer
sudo install -d -m 0700 /var/lib/maxnow-ballet-booking-fast
sudo install -d -m 0750 -o root -g www-data \
  /var/lib/maxnow-ballet-booking-fast-public
sudo touch /etc/maxnow-ballet/enable-fast-booking
sudo chown root:root /etc/maxnow-ballet/enable-fast-booking
sudo chmod 0600 /etc/maxnow-ballet/enable-fast-booking
sudo systemctl daemon-reload
sudo systemd-analyze verify \
  /etc/systemd/system/maxnow-ballet-booking-fast.service \
  /etc/systemd/system/maxnow-ballet-booking-fast.timer
sudo -u root -g www-data /usr/bin/python3 -B \
  scripts/book_ballet_fast.py preview
sudo systemctl enable --now maxnow-ballet-booking-fast.timer
```

`preview` 只计算下次日期并发布安全计划，不加载凭据、不访问闻道、不增加运行 / 成功计数。不要为验收手动运行 `execute`，也不要手动 `systemctl start maxnow-ballet-booking-fast.service`；真实 mutation 只由周日 timer 在时间窗内触发。自动化状态可用无网络 runner 查询：

```bash
scripts/run_ballet_booking_fast.sh status
sudo systemctl is-enabled maxnow-ballet-booking-fast.timer
sudo systemctl is-active maxnow-ballet-booking-fast.timer
sudo systemctl list-timers maxnow-ballet-booking-fast.timer --all --no-pager
sudo systemctl show maxnow-ballet-booking-fast.timer \
  -p NextElapseUSecRealtime -p LastTriggerUSec
sudo stat -c '%U:%G %a %n' \
  /var/lib/maxnow-ballet-booking-fast/state.json \
  /var/lib/maxnow-ballet-booking-fast-public/ballet-booking-fast.json
```

如果 Owner 要修改目标或顺序，先改仓库配置与 Skill，补 fixture 测试和页面 fallback，部署后运行 `preview` 刷新状态；不得直接在服务器热改 JSON。运行结果的 `timings` 会按课表、课程卡、规则、mutation 和最终核验给出脱敏分段耗时，用于判断慢在源站还是本地排队，不保存 URL、ID 或响应正文。暂停自动抢课时删除 enable gate 并 disable timer，不删除私有幂等账本：

```bash
sudo systemctl disable --now maxnow-ballet-booking-fast.timer
sudo rm /etc/maxnow-ballet/enable-fast-booking
```

2026-07-28 17:20 已部署主分支 `b51295a`（版本 `1.0.7.00`）的周日自动抢课 Fast Path。公开运行数据、root-only 芭蕾私有状态和原 nginx auth location 备份在 `/home/ubuntu/maxnow-deploy-backups/20260728-1720-ballet-fast-path`，运行数据拉取后原样恢复并重新生成 `project-meta.*` / `project-status.*`。新 enable gate 为 `root:root 0600`，私有目录为 `root:root 0700`，公开 JSON 为 `root:www-data 0640`；nginx worker 可读，匿名 `/data/ballet-booking-fast.json` 返回 `401`。`preview` 发布的下一次计划为 2026-08-02 14:20，三项目标日期为 8 月 8 日周六、8 月 7 日周五、8 月 4 日周二，累计运行 / 成功均为 0。随后 isolated live dry-run 只发出 3 个目标日期课表 GET，因下周课尚未发布均为 `course_not_unique`，`mutationAttempts=0`。timer 已 `enabled / active`，首次触发为 2026-08-02 14:19:35；service 保持 `inactive`、`LastTriggerUSec` 为空，部署和验收未调用 `do_addbook`。服务器全仓检查、unit verify 和 `nginx -t` 通过。

2026-07-28 17:33 已部署主分支 `b95a5a13`（版本 `1.0.7.01`）的逐课独立与安全重试。部署备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-173317-ballet-fast-retry`，服务器运行数据、私有幂等状态和公开状态在拉取前均已备份，运行数据随后原样恢复并刷新 `project-meta.*` / `project-status.*`。本机与服务器 13 项预约测试、全仓检查、unit verify 和 `nginx -t` 均通过；匿名状态接口保持 `401`。生产时区为 `Asia/Shanghai`、NTP 已同步，timer 为 `enabled / active`，精度 `1s`，下次 2026-08-02 14:19:35 启动，service 保持 `inactive / success` 且从未真实触发。隔离 live dry-run 在下周课程尚未发布时让三项目标各完成首次匹配与 3 次重试，共 12 个实时 GET、`mutationAttempts=0`，逐课耗时 4.138 / 4.576 / 5.374 秒，关键路径总耗时 14.087 秒；没有调用 `do_addbook`，累计运行和累计成功仍为 0。

2026-07-28 19:18 已部署主分支 `20e212ba`（版本 `1.0.7.03`）的芭蕾信息架构收敛。芭蕾页顺序调整为下一节 / 本周训练、课程计划、周课表、训练记录和课程卡；自动抢课运维与 Session 实验详情移入 Cloud。服务器运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-ballet-ia-cdeZmE`，拉取后原样恢复并重新生成 `project-meta.*` / `project-status.*`。本机浏览器验证无横向溢出，顶部双卡同顶同底等高，少于 5 节时趋势正确收起；服务器全仓检查和 `nginx -t` 通过。自动抢课 timer 保持 `active`，下次触发仍为 2026-08-02 14:19:35；本次只部署静态页面，没有访问闻道或触发预约。

2026-07-28 已部署主分支 `feb15738`（版本 `1.0.7.04`）的 Cloud 芭蕾运维卡布局调整。“芭蕾自动抢课”与“芭蕾 Session 实验”在宽桌面左右各占半宽，Session 展开后仍留在右半列；`1320px` 以下继续单列。服务器运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-cloud-session-card-zjyuog`，拉取后原样恢复并重新生成 `project-meta.*` / `project-status.*`。本地浏览器在 1920px 下验证两卡各宽约 782px、同顶同底等高且无横向溢出，1280px 下正常退回单列；服务器全仓检查与 `nginx -t` 通过。自动抢课 timer 保持 `active`，下次触发仍为 2026-08-02 14:19:35；本次只部署静态样式，没有访问闻道或触发预约。

2026-07-28 已部署主分支 `e09a1526`（版本 `1.0.7.05`）的 Cloud 重复页头删除。内容区不再显示“Cloud Services / 云服务 / dash.maxnow.cn”标题卡，进入页面后直接展示“系统与托管”；专用样式与页面协议已同步清理。服务器运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-remove-cloud-head-Kbth2T`，拉取后原样恢复并重新生成 `project-meta.*` / `project-status.*`。本地 1920px / 1280px 验证首卡直接顶上、无横向溢出；服务器全仓检查与 `nginx -t` 通过。自动抢课 timer 保持 `active`，下次触发仍为 2026-08-02 14:19:35；本次没有访问闻道或触发预约。

2026-07-28 已部署主分支 `d37f60c7`（版本 `1.0.7.06`）的 Cloud Session 默认展开修复。芭蕾 Session 实验首次进入页面即显示有效时长、检查时间、间隔和状态，同时保留手动收起能力。服务器运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-open-session-default-e4vKal`，拉取后原样恢复并重新生成 `project-meta.*` / `project-status.*`。Codex 内置浏览器验证默认 `open`、详情可见、手动收起后卡片正常缩短且无横向溢出；服务器全仓检查与 `nginx -t` 通过。自动抢课 timer 保持 `active`，下次触发仍为 2026-08-02 14:19:35；本次没有访问闻道或触发预约。

2026-07-28 已部署主分支 `7761ba91`（版本 `1.0.7.07`）的预约教室展示。芭蕾“下一节”和“所有预约”现在按“时间 · 老师 · 教室”显示闻道同步的 `venue`，缺失时不猜测。服务器运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-ballet-booking-venue-cBLvuv`，拉取后原样恢复并重新生成 `project-meta.*` / `project-status.*`。Codex 内置浏览器验证当前预约同时正确显示“大教室”和“小教室”，且无横向溢出；服务器全仓检查与 `nginx -t` 通过。自动抢课 timer 保持 `active`，下次触发仍为 2026-08-02 14:19:35；本次没有访问闻道或触发预约。

2026-07-28 已部署主分支 `4deb08e6`（版本 `1.0.7.08`）的芭蕾顶部概览调整。独立“下一节”面板已删除，顶部改为等宽“本周训练 / 课程卡”，课程卡使用适配半宽的纵向布局；预约列表首行改为唯一的“最近一节”高亮入口。服务器运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-ballet-week-card-M75b0h`，拉取后恢复除项目元信息外的运行数据并重新生成 `project-meta.*` / `project-status.*`。Codex 内置浏览器在 1280px 下确认两卡同顶、同底、等宽且无横向溢出，4 条预约中只有首条带高亮；服务器全仓检查和 `nginx -t` 通过。自动抢课、每日同步和月度同步 timer 均保持 `active`，自动抢课下次触发仍为 2026-08-02 14:19:35；本次没有访问闻道或触发预约。

2026-07-28 已部署主分支 `25bdd77c`（版本 `1.0.7.09`）的紧凑状态课表。课表移到芭蕾页最底部，桌面内容区限制为约 `58vh` 并固定日期行 / 时间列，移动端逐日列表同样限高；普通课程按课型使用不同颜色描边，已预约 / 已上完 / 排队中分别使用粉玫瑰 / 绿色 / 橙色实心卡。服务器运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-ballet-timetable-compact-9CaUYS`，拉取后恢复除项目元信息外的运行数据并重新生成 `project-meta.*` / `project-status.*`。Codex 内置浏览器使用服务器现有 7 天 55 节脱敏课表验证：1280 × 720 下内部课表高约 403px、整卡约 555px且页面无横向溢出；临时合成的已上完记录正确显示绿色实心卡。服务器全仓检查和 `nginx -t` 通过，三个芭蕾 timer 均保持 `active`，自动抢课下次触发仍为 2026-08-02 14:19:35；本次没有访问闻道或触发预约。

2026-07-28 已部署主分支 `c5a79be0`（版本 `1.0.7.10`）的 Session 无限期运行。运行态配置与安装脚本备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-session-indefinite-oouvxQ`，静态部署运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-session-indefinite-deploy-Ajs04y`。v7 于 20:23:14 启动并在 20:23:17 完成首轮 HTTP 200 / authenticated 验证，公开状态确认 `scheduledEndAt=null`、20 分钟间隔和累计 133 个样本后才停止 v6；v7 当前 `active / running`、`RuntimeMaxUSec=infinity`，v6 为 `inactive / dead`。Cloud 卡已删除计划结束信息，Codex 内置浏览器确认对应 DOM 节点为 0、无残留文案和横向溢出。服务器全仓检查、`nginx -t`、安装副本比对和六个芭蕾相关 timer / unit 状态均通过；未登录 Dash / Session 数据仍为 `302 / 401`。交接只执行了 v7 首轮只读课程列表 GET，没有提交预约、候补、取消或转课。

2026-07-28 已部署主分支 `cdb0fdb`（版本 `1.0.7.11`）的三分之二屏宽课表适配，其中页面改动提交为 `a554311`。部署通过本地 Git bundle 将服务器从 `7658219` 快进，部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-220641-ballet-compact-width`；恢复服务器权威运行数据后重新生成 `project-meta.*` 并合并 `token-usage.*`。服务器全仓检查与 `nginx -t` 通过，未登录 Dash / 芭蕾数据 / Blog 分别保持 `302 / 401 / 200`；自动抢课、每日同步、月度同步、Session 状态和活动日志转存五个 timer 均为 `active`，自动抢课下次触发仍为 2026-08-02 14:19:35。本次只部署静态样式和文档，没有访问闻道或触发预约。

2026-07-28 已部署功能提交 `af2e78a`（版本 `1.0.7.12`），将 rolling 只读同步的周日额外触发从 14:20 调整到 14:30，与自动抢课关键窗口错开。部署前运行数据和原 timer 备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-222003-ballet-sync-1430`；恢复服务器权威运行数据后重新生成 `project-meta.*` / `project-status.*` 并合并 `token-usage.*`。安装副本与仓库 unit 一致，`systemd-analyze` 确认下一次周日只读触发为 2026-08-02 14:30；自动抢课仍于 14:19:35 启动并在 14:20:00 提交。两个 service 均保持 `inactive / dead`，只读 timer 的 `LastTriggerUSec` 仍为 2026-07-28 00:17:01，自动抢课 `LastTriggerUSec` 仍为空，说明部署没有触发同步或预约。服务器全仓检查、unit verify 与 `nginx -t` 通过，未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`；本次未访问闻道。

2026-07-28 已部署主分支 `622502f`（版本 `1.0.7.13`）的课表宽度与重叠修正。`1501px` 以上课表卡占同级全宽卡的 `66.67%`，`1365px` / `1280px` 保持全宽且 7 天无内部横向滚动，`860px` / `390px` 切换逐日列表且无整页溢出；同日同开始时间课程双列同顶并排，滚动 420px 后 sticky 日期栏仍完整且不露出上方课程内容。浏览器验收使用服务器现有 7 天 55 节脱敏 read model，只读复制到本地临时测试服务，没有访问闻道。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-224747-ballet-timetable-layout`，恢复服务器权威数据后重新生成 `project-meta.*` / `project-status.*` 并合并 `token-usage.*`。本地 46 项芭蕾测试、完整检查、服务器全仓检查与 `nginx -t` 通过；未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`，自动抢课下次触发仍为 2026-08-02 14:19:35。

2026-07-28 已部署主分支 `f3bcb0d`（版本 `1.0.7.14`）的全宽转置周课表。桌面课表改为横轴开始时间、纵轴星期日期，卡片恢复内容区全宽；同一星期同一开始时间的多节课程按整列扩宽后双列并排，时间表头、格子和课程卡保持严格对齐。浏览器使用服务器现有 7 天 55 节脱敏 read model 验证：`2048px` / `1365px` / `1280px` 均为全宽桌面课表且整页无横向溢出，时间列只在面板内部滚动；`860px` / `390px` 保持逐日列表，sticky 时间表头与星期首列滚动后位置不变。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-2343-ballet-timetable-transpose`，恢复服务器权威数据后重新生成 `project-meta.*` / `project-status.*` 并合并 `token-usage.*`。本地 46 项芭蕾测试、完整检查、服务器全仓检查与 `nginx -t` 通过；未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`，五个芭蕾 timer 均为 `active`，自动抢课下次触发仍为 2026-08-02 14:19:35；本次没有访问闻道或触发预约。

2026-07-28 已部署主分支 `8794a99`（版本 `1.0.7.15`）的一小时时段周课表。桌面横轴按 `xx:00–xx:00` 固定一小时分列，课程按开始时间归入对应小时，同一天同一小时内的课程上下排列；整周没有课程开始的连续小时合并为一个窄斜纹跳过列，当前 7 天 55 节脱敏课表生成 10 个正常小时列以及 `13:00–14:00`、`16:00–17:00` 两个跳过列。Codex 内置浏览器确认 `2048px` 全部小时列一次显示且无内部横向滚动，`1365px` / `1280px` 只在课表面板内部滚动，`860px` / `390px` 保持逐日列表；同小时两张课程卡同宽上下排列，sticky 时间表头与星期首列滚动后保持固定。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260728-2356-ballet-hourly-gap`，恢复服务器权威数据后重新生成 `project-meta.*` / `project-status.*` 并合并 `token-usage.*`。本地 46 项芭蕾测试、完整检查、服务器全仓检查与 `nginx -t` 通过；未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`，五个芭蕾 timer 均为 `active`，自动抢课下次触发仍为 2026-08-02 14:19:35；部署前确认 rolling / full / 自动抢课 service 均为 `inactive`，本次没有访问闻道或触发预约。

2026-07-29 已部署主分支 `2e8555a`（版本 `1.0.7.16`）的无内部滚动周课表。桌面课表取消固定高度、sticky 表头与面板内横纵滚动，全部一小时时段和 7 天课程按内容区宽度直接平铺，面板随内容自然增高；`1100px` 以下切换为同样无内部滚动的逐日列表。Codex 内置浏览器使用服务器现有 7 天 55 节脱敏 read model 验证：`2048px` / `1365px` / `1280px` / `1101px` 下课表 `clientWidth = scrollWidth`、`clientHeight = scrollHeight`，同小时课程保持上下排列，`1100px` / `860px` / `390px` 自然展开且整页无横向溢出，控制台无错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-001608-ballet-no-scroll`，恢复服务器权威数据后重新生成 `project-meta.*` / `project-status.*` 并合并 `token-usage.*`。本地 61 项芭蕾测试、完整检查、服务器全仓检查与 `nginx -t` 通过；未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`。五个芭蕾 timer 均为 `active`，rolling 的 `LastTriggerUSec` 在部署前后均为 2026-07-29 00:00:01，自动抢课 `LastTriggerUSec` 在部署前后均为空且下次仍为 2026-08-02 14:19:35；本次没有访问闻道或触发同步、预约。

2026-07-29 已部署主分支 `044efb1`（版本 `1.0.7.17`）的芭蕾顶部双卡宽度收敛。`1501px` 以上“本周训练 / 课程卡”进入三等分栅格前两格，每张各占内容区三分之一，`1101px–1500px` 继续各半，`1100px` 以下继续单列。Codex 内置浏览器使用服务器现有脱敏 read model 验证：`2048px` 内容区为 1701px、两卡各约 556px，`1600px` 内容区为 1280px、两卡各约 416px；两卡在宽桌面同顶、同底、等高，`1501px / 1500px / 1101px / 1100px / 390px` 断点均符合预期且无整页横向溢出，控制台无错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-002548-ballet-summary-thirds`，恢复服务器权威数据后重新生成 `project-meta.*` / `project-status.*` 并合并 `token-usage.*`。本地和服务器完整检查、`nginx -t` 均通过，未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`；rolling 的 `LastTriggerUSec` 仍为 2026-07-29 00:00:01，自动抢课 `LastTriggerUSec` 仍为空且下次为 2026-08-02 14:19:35，本次没有访问闻道或触发同步、预约。

2026-07-29 已部署主分支 `78ab7a2`（版本 `1.0.7.20`）的芭蕾成长进度、上课历史对齐与分钟级课表。成长卡按 personal-wiki 课程指南展示升班参考与 XP；上课历史课程列保持统一起点；桌面周课表按实际起止分钟定位和伸展课程卡，半点落在小时中线，时间重叠课程自动分轨，空档只在整周没有课程实际占用时压缩。本地浏览器使用服务器现有 7 天 55 节脱敏 read model 验证：一小时课程宽约 120px、90 分钟课程宽约 180px，比例为 `1.5`，`09:30` 左边界与小时中点误差小于 `0.01px`；`2048px / 1501px / 1500px / 1101px` 使用桌面时间轴，`1100px / 390px` 使用逐日列表，均无整页横向溢出且控制台无页面错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-time-scaled-timetable-093239`，恢复服务器权威运行数据后重新生成 `project-meta.*` / `project-status.*`；部署恢复 stash 保留为 `before-78ab7a2-runtime-data`。本地与服务器完整检查、`nginx -t` 均通过，未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`，五个芭蕾 timer 与 v7 Session 实验保持 active，rolling / full / 自动抢课 service 保持 inactive；本次没有访问闻道或触发同步、预约。

2026-07-29 已部署主分支 `b8dcd16`（版本 `1.0.7.21`）的芭蕾顶部刷新状态收纳。紧凑的“更新 7/29 00:00 · 已同步”移到全局顶部栏“芭蕾”标题旁，完整时间保留在悬停提示，正常状态不再在内容区独占空白行；异常告警仍保留为内容区首项。Codex 浏览器使用服务器现有脱敏 read model 验证：`2048px / 1501px / 1500px / 1101px / 1100px / 860px / 390px` 下状态均可见，三卡栅格分别按三列 / 两列 / 单列切换，整页无横向溢出。部署通过本地 Git bundle 将服务器从 `ab28b1a` 快进，运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-ballet-header-095001`，恢复服务器权威数据后重新生成 `project-meta.*` / `project-status.*`；部署 stash 保留为 `0e4baac186d1d151f2183221d2f837fc72fc65be`。本地与服务器完整检查、`nginx -t` 及 reload 均通过，未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`，五个芭蕾 timer 保持 `enabled / active`，rolling / full / 自动抢课 service 保持 `inactive`；v7 Session unit 在部署前后均为 `inactive`。本次没有访问闻道或触发同步、预约。

2026-07-29 已部署主分支 `9a42f10`（版本 `1.0.7.22`）的芭蕾成长评分协议。`SPEC.md` 现完整记录升班输入与公式、规律 / 间歇判定、L1–L5 课次与基础月份、全部 XP 课型权重、六级阈值和效果，并明确运行分数不写死、100 分只提示老师测评；`scripts/check.py` 会把规范表格与 `dash/app.js` 常量直接对照，单边修改会使检查失败。部署通过本地 Git bundle 将服务器从 `26a7e89` 快进，运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-growth-contract-100118`，恢复服务器权威数据后重新生成 `project-meta.*` / `project-status.*`；部署 stash 保留为 `3a6263d3fe56a979860b68f1804b80bdfe09633c`。本地与服务器完整检查、评分协议一致性检查、`nginx -t` 及 reload 均通过，未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`，五个芭蕾 timer 保持 `enabled / active`，rolling / full / 自动抢课 service 保持 `inactive`；本次没有访问闻道或触发同步、预约。

2026-07-29 已部署主分支 `c8e4abb`（版本 `1.0.7.23`）的独立芭蕾成长评分文档。根目录新增 `BALLET_GROWTH_SCORING.md`，集中记录有效数据、当前级别判断、规律 / 间歇口径、升班公式、L1–L5 参数、XP、六级效果与修改清单；`SPEC.md` 仅保留产品边界和入口，避免维护两份参数。`scripts/check.py` 已改为直接对照独立文档与 `dash/app.js` 常量。部署通过本地 Git bundle 将服务器从 `6547987` 快进，运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-growth-guide-100953`，恢复服务器权威数据后重新生成 `project-meta.*` / `project-status.*`；部署 stash 保留为 `3ba2e051e02de4f0dd9a22f17d9e28555ee0bc1f`。本地与服务器完整检查、独立文档一致性检查、`nginx -t` 及 reload 均通过，未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`，五个芭蕾 timer 保持 `enabled / active`，rolling / full / 自动抢课 service 保持 `inactive`；本次没有访问闻道或触发同步、预约。

2026-07-29 11:10 已部署主分支 `27cf7e9`（版本 `1.0.7.25`）的详情页顶栏收纳与芭蕾课表连续背景。服务器每小时 `:10` 的 Token 总账任务按既有流程暂存运行态账本、快进拉取 `origin/main`、恢复服务器权威账本并完成总账刷新；静态文件直接生效，无需触发芭蕾同步或预约。线上已登录页面确认资源从 `styles.css?v=174` / `app.js?v=147` 更新为 `styles.css?v=176` / `app.js?v=149`：Token、生活、同行记均删除内容区重复标题卡并将更新时间 / 状态移入全局顶栏，Token 四来源更新时间条正常；芭蕾小时背景连续、课程卡仍按实际分钟横跨时段。四个页面整页横向溢出均为 0，控制台无警告或错误；未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`。本次公司网络出口在 `61.213.176.9`、`.12`、`.13` 间动态轮换，未为 SSH 扩大防火墙范围，因此未重复执行服务器侧 timer / service 状态检查。

2026-07-29 15:10 已部署主分支 `2661544`（版本 `1.0.7.26`）的芭蕾周课表配色收敛。服务器每小时 `:10` 的 Token 总账任务从 `origin/main` 拉取静态代码后直接生效，没有触发闻道同步或预约。线上公开 `styles.css?v=177` 与本地发布文件 SHA-256 均为 `5b5f592405404201417f7ae9272ca72c5bf0bf2181bc18fa6145c24b5bae59e6`，且命中新深玫瑰“今天”样式；未登录 Dash / 芭蕾数据 / 样式资源 / Blog 分别保持 `302 / 401 / 200 / 200`。公司网络对 SSH 目的地址使用动态企业 NAT，即使临时加入网页查询到的两个 `/32` 仍无法直连，因此本次不扩大 22 端口范围，也未重复执行服务器侧 timer / service 检查。

2026-07-29 19:20 已部署主分支 `d7e4163`（版本 `1.0.7.27`）的留白日历式芭蕾周课表。桌面改为日期横排、时间纵排的标准周日历，课程按实际分钟纵向伸展并在同日重叠时并排；`1200px` 以下切换逐日列表。已预约 / 排队中 / 已上完继续使用粉玫瑰 / 橙色 / 绿色实心状态卡。Codex 内置浏览器以 55 节合成周课表验证 `1600px / 1280px / 1201px / 1200px / 1100px / 860px / 390px`：所有断点整页横向溢出、课程裁切和移动卡片裁切均为 0，控制台无错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-192034-ballet-timetable-minimal`，恢复服务器权威运行数据并重新生成 `project-meta.*` 后，服务器完整检查与 `nginx -t` 通过；未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`，`maxnow-ballet-sync.timer`、`maxnow-ballet-full-sync.timer` 与 nginx 均为 `active`。本次只部署静态页面，没有访问闻道或触发同步、预约、排队、取消或转课。

2026-07-29 20:05 已部署主分支 `7c928a7`（版本 `1.0.7.28`）的芭蕾课表时间轴与边框修正。整点文字现与对应横向分界线共用坐标，普通课程移除额外左侧色条并改为四边同色、同宽的课型纯色描边；已预约 / 排队中 / 已上完继续保持粉玫瑰 / 橙色 / 绿色实心状态。Codex 内置浏览器使用服务器现有 7 天 55 节脱敏 read model 验证：整点文字中心与网格分界线最大误差为 `0px`，普通课程四边颜色和宽度一致，`1201px / 1200px / 860px / 390px` 无整页横向溢出或课程裁切，控制台无错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-2005-ballet-grid-alignment`，恢复服务器权威运行数据并重新生成 `project-meta.*` 后，服务器完整检查与 `nginx -t` 通过；未登录 Dash / 芭蕾数据 / Blog 保持 `302 / 401 / 200`，`maxnow-ballet-sync.timer`、`maxnow-ballet-full-sync.timer` 与 nginx 均为 `active`。本次只部署静态页面，没有访问闻道或触发同步、预约、排队、取消或转课。

2026-07-29 20:27 已部署主分支 `fbb15ae`（版本 `1.0.7.29`）的芭蕾教室分栏与纯课次升班进度。桌面周课表在每天日期下固定分为“大教室 / 小教室”两列，同教室重叠课程只在自己的列内继续分轨；`1200px` 以下按日期、再按教室分组。成长进度移除基础月份与 100 分换算，只显示当前级别已上课次 / 目标课次，课程路径继续为 `L1 → L1.5 → L2 → L3 → L4 → L5`，XP 保持独立。Codex 内置浏览器使用生产 7 天 55 节脱敏 read model 验证：33 节大教室、22 节小教室全部归位，未识别教室为 0，整点误差为 `0px`；预约 / 排队 / 已上完仍为粉玫瑰 / 橙 / 绿实心状态，`2048px / 1600px / 1201px / 1200px / 860px / 390px` 无整页横向溢出。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-202704-ballet-room-count`，恢复服务器权威运行数据并重新生成 `project-meta.*` 后，服务器完整检查与 `nginx -t` 通过；未登录 Dash / 登录页 / 芭蕾数据 / Blog 保持 `302 / 200 / 401 / 200`，nginx、认证服务和芭蕾 rolling / full timer 均为 `active`。本次只部署静态页面，没有访问闻道或触发同步、预约、排队、取消或转课。

2026-07-29 21:00 已部署主分支 `3ee4b27`（版本 `1.0.7.30`）的芭蕾课表结束刻度与状态对比增强。桌面时间轴在最后一个小时底部补齐结束整点，当前生产 7 天 55 节脱敏课表明确显示 `22:00`；表头增加可约 / 可排队 / 已满 / 已取消图例，课程内状态标签使用绿 / 橙棕 / 深灰紫 / 红实心色并配对应浅底，已预约 / 排队中 / 已上完继续保留粉玫瑰 / 橙 / 绿实心整卡。Codex 内置浏览器验证 `22:00` 中心与最后一条网格线误差为 `0px`，14 个日期教室表头和 55 节课全部保留，`2048px / 1600px / 1201px / 1200px / 860px / 390px` 无整页横向溢出，控制台无警告或错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-210052-ballet-end-status`，恢复服务器权威运行数据并重新生成 `project-meta.*` 后，服务器完整检查与 `nginx -t` 通过；未登录 Dash / 登录页 / 芭蕾数据 / Blog 保持 `302 / 200 / 401 / 200`，nginx、认证服务和芭蕾 rolling / full timer 均为 `active`。本次只部署静态页面，没有访问闻道或触发同步、预约、排队、取消或转课。

2026-07-29 21:12 已部署主分支 `541b850`（版本 `1.0.7.31`）的芭蕾课表日期分界增强。桌面每天开始位置改为较深 `2px` 玫瑰灰竖线，同一天大教室 / 小教室之间保留浅色 `1px` 细线；日期表头、教室表头和时间网格的 7 条边界使用同一横坐标连续贯穿。Codex 内置浏览器使用生产 7 天 55 节脱敏课表验证：日期线为 `2px / rgb(212, 173, 190)`，教室线保持浅色细线，14 个教室表头与 55 节课全部保留，`2048px / 1600px / 1201px / 1200px / 860px / 390px` 无整页横向溢出，移动端逐日卡片不变，控制台无警告或错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-211242-ballet-day-divider`，恢复服务器权威运行数据并重新生成 `project-meta.*` 后，服务器完整检查与 `nginx -t` 通过；未登录 Dash / 登录页 / 芭蕾数据 / Blog 保持 `302 / 200 / 401 / 200`，nginx、认证服务和芭蕾 rolling / full timer 均为 `active`。本次只部署静态样式，没有访问闻道或触发同步、预约、排队、取消或转课。

2026-07-29 21:56 已部署主分支 `4a17c8a`（版本 `1.0.7.32`）的芭蕾课表日期分界柔化。撤销贯穿课表全高的 `2px` 玫瑰粗线，日期边界和同日教室边界统一使用 `1px` 细线，分别以 `rgb(223, 204, 212)` 和 `rgb(244, 238, 241)` 的暖灰粉深浅建立层级，课程卡、状态色和时间定位保持不变。Codex 内置浏览器使用生产 7 天 55 节脱敏课表验证：14 个教室表头和 55 节课全部保留，`2048px / 1600px / 1201px / 1200px / 860px / 390px` 无整页横向溢出，桌面 / 移动端切换正常，控制台无警告或错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-215604-ballet-day-divider-soft`，恢复服务器权威运行数据并重新生成 `project-meta.*` 后，服务器完整检查与 `nginx -t` 通过；未登录 Dash / 登录页 / 芭蕾数据 / Blog 保持 `302 / 200 / 401 / 200`，nginx、认证服务和芭蕾 rolling / full timer 均为 `active`。本次只部署静态样式，没有访问闻道或触发同步、预约、排队、取消或转课。

2026-07-29 22:18 已部署主分支 `ae9e4bf`（版本 `1.0.7.33`）的芭蕾课表报名与排队人数。同步器从课表源页面原有报名数 / 容量之外，新增解析独立 `Wait` 数字为脱敏 `waitlistCount`；前端显示为 `报名数/容量人 · 排N`，源站未提供时不推断。Codex 内置浏览器使用生产 7 天 55 节脱敏课表验证：45 节旧快照人数在 `2048px / 1600px / 1500px / 1365px / 1280px / 1201px / 1200px / 860px / 390px` 全部可见，课程内容裁切和整页横向溢出均为 0；源站格式测试值正确显示 `20/12人 · 排8`，控制台无警告或错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-222400-ballet-class-counts`，服务器 18 项芭蕾测试、完整检查与 `nginx -t` 通过。随后通过既有 rolling service 执行一次只读同步，结果为 `success / exit 0`，22:18:41 的 55 节课中 37 节带报名 / 容量、19 节带明确排队人数；自动预约 service 全程保持 `inactive`，没有提交预约、候补、取消或转课。未登录 Dash / 登录页 / 芭蕾数据 / Blog 保持 `302 / 200 / 401 / 200`，nginx、认证服务与 rolling / full timer 均为 `active`。

2026-07-29 22:45 已部署主分支 `ccadb21`（版本 `1.0.7.34`）的芭蕾课程卡信息分层。课程卡改为课程名、独立人数行、低权重老师行、底部时间 / 状态四层结构；空 `waitlistCount` 不再被转换成 `排队 0`，只有源站明确 `Wait` 才显示排队人数。Codex 内置浏览器使用生产 7 天 55 节脱敏课表在 `2048px / 1280px / 390px` 验证：37 节报名 / 容量与 19 节明确排队人数全部保留，课程卡内容溢出和整页横向溢出均为 0；中等桌面与 60 分钟紧凑卡隐藏老师但保留课程名、人数、时间和状态。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-224500-ballet-card-layout`，服务器完整检查、认证自检与 `nginx -t` 通过；未登录 Dash / 登录页 / 芭蕾数据 / Blog 保持 `302 / 200 / 401 / 200`，nginx、认证服务与 rolling / full timer 均为 `active`，自动预约 service 保持 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-29 23:10 已部署主分支 `6c982a6`（版本 `1.0.7.35`）的本人候补位次与紧凑课程老师修复。课表状态从预约快照匹配脱敏 `waitlistPosition` 并显示 `排队中 N`，与课程全班 `Wait` 人数保持独立；同步器后续直接把本人候补序号合入对应课表记录。宽桌面恢复 60 分钟课程老师名，`1101px–1500px` 中等桌面和重叠窄卡继续隐藏。Codex 内置浏览器使用生产 7 天 55 节脱敏课表验证当前本人候补为第 4 位，`2048px / 1280px / 390px` 均无课程内容或整页横向溢出。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260729-231019-ballet-waitlist-position`，恢复服务器权威运行数据后重新生成 `project-meta.*` 并合并 `token-usage.*`；部署 stash 为 `e8c5ddc7aee32f40d31e76dad9e0ba148857055b`。服务器 18 项芭蕾测试、完整检查、认证自检与 `nginx -t` 通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog 保持 `302 / 200 / 401 / 200`；nginx、认证服务、rolling / full / 自动抢课 timer 均为 `active`，自动抢课 service 保持 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-30 00:02 已部署主分支 `b45b71f`（版本 `1.0.7.36`）的课次自动升班与十级小天鹅成长。升班进度达到当前规律 / 间歇目标后自动沿 `L1 → L1.5 → L2 → L3 → L4 → L5` 前进，已达成的规律升级不会因之后训练频率下降而回退；成长等级取消 XP 权重，全部实际上课每节计 1 节，并按 `0 / 10 / 25 / 45 / 70 / 95 / 120 / 145 / 170 / 200` 节进入 `Lv.1–Lv.10`，满 200 节到达满级。页面新增随十级演化的代码内 SVG 小天鹅和十段进度指示。Codex 内置浏览器验证 `2048px / 1501px / 1101px / 1100px / 390px` 布局与断点无横向溢出；实际代码边界验证覆盖 `9→Lv.1`、`10→Lv.2`、`199→Lv.9`、`200→Lv.10`、规律 / 间歇升班以及暂停后不回退。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-000155-ballet-auto-level-swan`，恢复服务器权威运行数据后重新生成 `project-meta.*`；部署 stash 为 `9db0b5a8a001d4587ad6d9c53fc91fad6cf31dd3`。服务器 61 项芭蕾测试、完整检查、成长规则一致性检查与 `nginx -t` 通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog 保持 `302 / 200 / 401 / 200`，nginx、认证服务与 rolling / full / 自动抢课 timer 均为 `active`，相关 service 保持 `inactive`。部署前已等待 00:00 计划同步自然完成并确认 `success / exit 0`；部署本身没有额外访问闻道，也没有触发预约、候补、取消或转课。

2026-07-30 11:00 已部署主分支功能提交 `8618631`（版本 `1.0.7.37`）的十阶段自然成长小天鹅图像。Owner 确认的二维粉嫩成长图已固化为 `dash/assets/ballet/swan-growth-sheet.png` 与十张 `512×512` 透明 PNG，前端随 `Lv.1–Lv.10` 确定性切换，不依赖运行时生成；Lv.1–Lv.3 为灰色绒毛雏鹅，Lv.4–Lv.6 为灰白换羽，Lv.7–Lv.9 为白色青年天鹅，Lv.10 为带克制光环的成年天鹅。Codex 内置浏览器验证桌面 `82×82`、手机 `70×70` 显示均无图片或整页溢出，控制台无错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-1100-ballet-swan-growth-art`，恢复服务器权威运行数据后重新生成 `project-meta.*`；部署 stash 为 `9b310c3f356945e0f607114f3d261cf38bfd473e`。服务器 61 项芭蕾测试、完整检查与 `nginx -t` 均通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog 为 `302 / 200 / 401 / 200`，Lv.1 / Lv.10 图片资源均为 `200`；nginx、认证服务和三个相关 timer 为 `active`，rolling / full / 自动抢课 service 均为 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-30 11:30 已部署主分支功能提交 `1e544b6`（版本 `1.0.7.38`）的小天鹅成长图视觉重心修正。成长等级块把“小天鹅 + 十段进度”整体在桌面端光学上提 `10px`、窄屏上提 `6px`，补偿低等级透明 PNG 顶部留白偏多造成的视觉下沉；十张素材、成长比例与等级切换逻辑未变。Codex 内置浏览器在 `1280px / 1100px / 390px` 验证可见小天鹅与右侧进度内容中心对齐、整页无横向溢出且控制台无错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-1130-ballet-swan-align`，恢复服务器权威运行数据后重新生成 `project-meta.*`；部署 stash 为 `89b13724999c840e5262e8a6b2da1d267ce323f6`。服务器 61 项芭蕾测试、完整检查与 `nginx -t` 均通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog / `styles.css?v=196` 为 `302 / 200 / 401 / 200 / 200`；nginx、认证服务和三个相关 timer 为 `active`，rolling / full / 自动抢课 service 均为 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-30 20:06 已部署主分支功能提交 `3b861eb` 与 `1080293` 的成长卡小天鹅可见主体对齐、课表排队 / 预约色阶加深，并以版本 `1.0.7.49` 补记生产发布状态。服务器此前停在 `9161113 / 1.0.7.46 / styles.css?v=203`，因此 Owner 仍看到旧的统一像素位移；本次发布升级为按十张 PNG 各自透明上边界百分比上提，并加载 `styles.css?v=205`。生产运行数据按服务器修改清单备份至 `/home/ubuntu/maxnow-deploy-backups/20260730-2006-swan-colors`，恢复后重新生成 `project-meta.*` 与合并 `token-usage.*`。本地与服务器完整检查、18 项芭蕾同步测试、`nginx -t`、生产脱敏数据视觉回环和访问边界均通过；`Lv.1` 可见主体与标题顶部基线偏差小于 `0.03px`，`2048px / 1200px / 390px` 无整页横向溢出，未登录 Dash / 登录页 / 芭蕾数据 / Blog 为 `302 / 200 / 401 / 200`。部署没有访问闻道，也没有触发同步、预约、排队、取消或转课。

2026-07-30 20:10 已部署版本 `1.0.7.50` 的成长等级视觉中心修正。上一版把小天鹅可见顶部与 `Lv.N` 顶部对齐，但生产数据回环测得 `Lv.1` 鸭子可见主体中心仍比文字中心低约 `6.7px`；本次把等级摘要改为中心线排列，并按十张透明 PNG 的各自可见像素中心设置 `-21%` 至 `-1%` 的光学位移。生产运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-2010-swan-center`，恢复后重新生成 `project-meta.*` 与合并 `token-usage.*`。生产数据视觉回环确认桌面与手机端中心偏差均小于 `0.03px`，`1280px / 390px` 无整页横向溢出；服务器完整检查、18 项芭蕾同步测试、`nginx -t` 与访问边界通过。部署没有访问闻道，也没有触发同步、预约、排队、取消或转课。

2026-07-30 16:16 已部署主分支功能提交 `f049424`（版本 `1.0.7.45`）的成长等级与课程等级模块拆分。原“成长进度”总卡改为上下两张独立 `panel`，成长等级固定在上、课程等级在下；小天鹅移到成长等级右上角，经验条恢复完整内容宽度。Codex 内置浏览器在 `1600px / 1501px / 1500px / 1101px / 1100px / 390px` 验证模块顺序、断点布局、宠物与轨道分离、宽屏同顶同底及无横向溢出，控制台无错误。部署通过本地 Git bundle 将服务器从 `98f9f3e` 快进，运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-1620-ballet-growth-modules`，除重新生成的 `project-meta.*`、`project-status.*` 与 `token-usage.*` 外恢复后与备份逐文件一致；部署 stash 为 `d2164f6ae8d8fb5c0d3ac484807503de546158bd`。服务器完整检查、`nginx -t`、运行数据一致性与访问边界均通过，未登录 Dash / 登录页 / 芭蕾数据 / `styles.css?v=202` / Blog 为 `302 / 200 / 401 / 200 / 200`；nginx、认证服务和三个相关 timer 为 `active`，rolling / full / 自动抢课 service 均为 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-30 15:56 已部署主分支功能提交 `1f770e3`（版本 `1.0.7.44`）的本周当前训练时长与课程类型。训练时长改为已完成加已预约的确定小时，移除最喜欢的老师，底部以水平条展示同口径课程类型，并与低饱和完成率圆环组合。部署通过本地 Git bundle 将服务器从 `708a888` 快进，运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-1552-ballet-week-course-types`，除重新生成的 `project-meta.*` 外恢复后与备份逐文件一致；部署 stash 为 `497c5eed12921241c1c20ca319b342300df46bc5`。生产脱敏数据回环预览确认训练时长 `5 小时`、已确定 `4 节`、课程类型“芭蕾 2 节 / 肌肉素质 1 节 / 软开 1 节”和完成率 `25%`；`1600px` 三张概览卡同顶、同底、等高且无整页横向溢出，控制台无错误。服务器完整检查、`nginx -t`、运行数据一致性与访问边界均通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog 为 `302 / 200 / 401 / 200`；nginx、认证服务、rolling / full timer 为 `active`，自动抢课 timer 与 rolling / full / 自动抢课 service 为 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-30 15:35 已部署主分支功能提交 `708a888`（版本 `1.0.7.43`）的本周训练洞察与过去课程层级。顶部“本周训练”新增按实际上完课程统计的最喜欢老师和低饱和圆形完成率，预计训练改为以小时为主值的“训练时长”；过去日期下包括已上完在内的全部课程统一降饱和。部署通过本地 Git bundle 将服务器从 `ab1e6c7` 快进，运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-153542-ballet-week-insights`，恢复后除重新生成的 `project-meta.*` 外与备份逐文件一致；部署 stash 为 `fa30ac2d0e4b7caca5fad5a330818c759e44ae32`。生产脱敏数据回环预览确认“王嘉豪 · 1 节 · 1.5 小时”、完成率 `25%`、训练时长 `5–6.5 小时`，过去已上完课程为 `opacity 0.58 + saturate(0.52)`；`1600px` 三张概览卡同顶、同底、等高且无整页横向溢出，控制台无错误。服务器完整检查、`nginx -t`、运行数据哈希与访问边界均通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog 为 `302 / 200 / 401 / 200`；nginx、认证服务和三个相关 timer 为 `active`，rolling / full / 自动抢课 service 为 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-30 15:13 已部署主分支功能提交 `b258a12`（版本 `1.0.7.42`）的成长进度条对齐修复。紫色进度条移出“小天鹅 + 文字”两列布局并占满内层卡片宽度，小天鹅只留在轨道下方的信息行；Codex 内置浏览器在 `1600px` 实测蓝色与紫色轨道的左边、右边和总宽度差值均为 `0px`，`1280px / 1100px / 390px` 无整页横向溢出且控制台无错误。部署验证时服务器已由定时拉取快进到该提交，运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-151335-ballet-growth-bar-alignment`。服务器 61 项芭蕾测试、完整检查与 `nginx -t` 均通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog 为 `302 / 200 / 401 / 200`；三个相关 timer 为 `active`，rolling / full / 自动抢课 service 均为 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-30 14:37 已部署主分支功能提交 `784dbde`（版本 `1.0.7.41`）的成长等级文案修正。紫色“成长等级”标题只显示当前 `Lv.N`，不再显示“第 N 阶段 → 第 M 阶段”；下方分别展示“本级 N / M 节”和“还差 N 节升级到 Lv.M”。Codex 内置浏览器宽屏预览确认标题仅为 `Lv.1`、整页无横向溢出且控制台无错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-143720-ballet-growth-level-copy`，恢复服务器权威运行数据后重新生成 `project-meta.*`；部署 stash 为 `41878e66df06723b0030823b69c6be8890dbbdf6`。服务器 61 项芭蕾测试、完整检查与 `nginx -t` 均通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog 为 `302 / 200 / 401 / 200`；三个相关 timer 为 `active`，rolling / full / 自动抢课 service 均为 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-30 14:27 已部署主分支功能提交 `a05ab97`（版本 `1.0.7.40`）的成长等级聚焦改版。紫色“成长等级”删除 `1–10` 全量编号与重复说明，只保留“当前阶段 → 下一阶段”、本阶段已上 / 目标课次、剩余课次和当前阶段小天鹅；成长卡底部自动更新说明同步删除。Codex 内置浏览器在 `1600px / 1280px / 1100px / 390px` 验证三张宽屏概览卡同顶同底等高、成长区无全量等级、整页无横向溢出且控制台无错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-142706-ballet-growth-next-step`，恢复服务器权威运行数据后重新生成 `project-meta.*`；部署 stash 为 `04df458fa25657b04550a7cbdf9e873c99f70436`。服务器 61 项芭蕾测试、完整检查与 `nginx -t` 均通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog 为 `302 / 200 / 401 / 200`；三个相关 timer 为 `active`，rolling / full / 自动抢课 service 均为 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-30 12:47 已部署主分支功能提交 `dea362b`（版本 `1.0.7.39`）的成长进度信息区分。成长卡顶部删除重复的 `Lv.N`；蓝色块改为“课程等级”，显示课程路径、已上 / 目标课次和距离下一课程等级的剩余课次；紫色块继续叫“成长等级”，用 `1–10` 十个编号节点和“第 N 阶段”替代第二条相似进度条，直接显示累计课次与距离下一成长阶段的剩余课次。规则内部仍保持 `L1 → L1.5 → L2 → L3 → L4 → L5` 和 `Lv.1–Lv.10` / 200 节满级。Codex 内置浏览器在 `1280px / 1100px / 390px` 验证十个阶段完整显示、两块信息无横向溢出且控制台无错误。部署前运行数据备份位于 `/home/ubuntu/maxnow-deploy-backups/20260730-124721-ballet-growth-clarity`，恢复服务器权威运行数据后重新生成 `project-meta.*`；部署 stash 为 `64b100d5c2415f8126d6d618536b0b83d42779e9`。服务器 61 项芭蕾测试、完整检查与 `nginx -t` 均通过，未登录 Dash / 登录页 / 芭蕾数据 / Blog / `styles.css?v=197` 为 `302 / 200 / 401 / 200 / 200`；nginx、认证服务和三个相关 timer 为 `active`，rolling / full / 自动抢课 service 均为 `inactive`。本次没有访问闻道，也没有触发同步、预约、候补、取消或转课。

2026-07-28 已部署主分支 `87bd4aa`（版本 `1.0.5.33`）的芭蕾实时查询 Skill。三轮部署前备份分别位于 `/home/ubuntu/maxnow-deploy-backups/20260728-ballet-live-ef5323`、`/home/ubuntu/maxnow-deploy-backups/20260728-ballet-live-fix-RDxVpv` 和 `/home/ubuntu/maxnow-deploy-backups/20260728-ballet-live-marker-pp8CNr`；运行数据按服务器权威来源精确恢复。服务器 OpenClaw Skill 入口已链接到仓库 `openclaw/maxnow-ballet-live`。首次验收依次发现 transient 命令参数不展开 `%d`、课表中文标题不稳定，最终改为读取 `CREDENTIALS_DIRECTORY` 与校验 `classtable` 结构；预约实时查询成功返回 4 条脱敏记录，课表实时查询于 11:12:34 返回当天 7 节课。最终结果为 `source=wenda-live`、`live=true`、单次 1 个 GET；查询前后 `dash/data/ballet.*` 与 `/var/lib/maxnow-ballet` 五个私有状态文件哈希不变，临时 `wenda-session.json` 凭据挂载已清理，服务器全仓检查通过。

2026-07-28 已部署主分支 `93570a7`（版本 `1.0.5.29`）的芭蕾周课表与状态校准。两次部署前的公开运行数据分别备份在 `/home/ubuntu/maxnow-deploy-backups/20260728-ballet-timetable-GvlS8U` 和 `/home/ubuntu/maxnow-deploy-backups/20260728-ballet-status-fix-scTpbO`，私有账本另存 root-only 备份。生产 rolling 同步成功，当前课表为 2026-07-27 至 2026-08-02 共 7 天、55 节；源站日期选择器可见至 2026-10-31，但实际有课只到 2026-08-02。状态校准后仅 3 节本人已预约使用粉玫瑰高亮、1 节本人候补使用橙色高亮，20 节普通“可排队”课程保留状态但不高亮。`maxnow-ballet-sync.timer` 已安装每日 00:00 与周日 14:20 两个 `OnCalendar`，月度 full 保持每月 1 日 00:47；两个 timer 与 v6 Session 探针均为 active。服务器 18 项同步测试、全仓检查、`systemd-analyze verify`、`nginx -t`、脱敏字段断言和访问边界均通过。

2026-07-27 17 时完成芭蕾只读训练闭环的正式验证与 timer 启用。部署前 `dash/data` 和 `/var/lib/maxnow-ballet` 已备份至 `/home/ubuntu/maxnow-deploy-backups/ballet-readonly-loop-cvbcBr`；服务器 14 项同步器测试、全仓检查与一次 production rolling service 均通过。正式 read model 保留 2 条实际上课、3 条正式预约、1 条候补第 4 位；四条未来课程均解析出 2 / 11 小时相对取消规则对应的绝对截止时间；课程卡为 39 / 40 次、有效至 2027-01-23，本周预计 3–4 节、240–330 分钟。read model 无 PHPSESSID、会员卡号、会员 / 源记录标识或原始响应。`/etc/maxnow-ballet/enable-sync` 为 `root:root 0600`；两个 timer 已 `enabled / active / waiting`，下次触发分别为 2026-07-28 00:17 和 2026-08-01 00:47。隔离验证使用的 `/tmp/maxnow-sync-ballet-preview-20260727.py`、`/var/lib/maxnow-ballet-preview-20260727` 及其 private StateDirectory 已删除。

2026-07-27 课程卡预测改为按卡独立计算。部署前 `dash/data` 和 `/var/lib/maxnow-ballet` 已备份至 `/home/ubuntu/maxnow-deploy-backups/ballet-card-forecast-eYFyLE`；服务器 15 项同步器测试、全仓检查和一次 production rolling service 均通过。当前卡明确以 2026-07-26 为开卡日，页面显示第 2 / 182 天、到期前所需 1.5 节 / 周、按每周 2 节预计 2026-12-10 用完，以及每周 1 节时到期约剩 13 节。因为开卡未满 28 天，`observedClassesPerWeek` 和 `observedCanFinish` 均为空，read model 不再包含固定窗口 `historyWindowDays` / `currentClassesPerWeek`。每日和月度 timer 保持 `active`。

2026-07-27 删除芭蕾内容区重复标题卡。部署前页面文件已备份至 `/home/ubuntu/maxnow-deploy-backups/ballet-compact-header-kS2cEb`；线上只保留低权重“数据更新”时间，下一节预约成为首个全宽有效模块，不再显示 `Ballet Progress / 芭蕾 / 已同步` 重复信息。服务器全仓检查与 `nginx -t` 通过，匿名访问边界保持 Dash `302`、`ballet.json` `401`、Blog `200`，页面缓存为 `styles.css?v=148` / `app.js?v=124`。

2026-07-27 按使用优先级重排芭蕾页面。部署前页面文件已备份至 `/home/ubuntu/maxnow-deploy-backups/ballet-layout-priority-NT0sXO`；线上顺序为更新时间 / 下一节课、本周训练 / 课程卡、所有预约、上课统计、上课历史、PHPSESSID 实验详情。1280px 下本周训练与课程卡分别约 313px / 650px 宽、均为 414px 高；1200px 及以下按顺序堆叠。PHPSESSID 详情默认收起，摘要可聚焦并保留异常状态。服务器全仓检查与 `nginx -t` 通过，匿名访问边界保持 Dash `302`、`ballet.json` `401`、Blog `200`，样式缓存为 `styles.css?v=149`。

2026-07-27 合并“下一节预约”与“所有预约”。部署前页面文件已备份至 `/home/ubuntu/maxnow-deploy-backups/20260727-ballet-bookings-merge-98RqR9`；线上不再重复渲染独立下一节卡，“所有预约”移到页面顶部，第一条以“下一节”和浅粉背景突出，并保留绝对取消截止时间。1280px 下首条高约 93px；390px 下列表自然单列，文档宽度与视口内容宽度均为 375px，无横向溢出。服务器全仓检查与 `nginx -t` 通过，匿名访问边界保持 Dash `302`、`ballet.json` `401`、Blog `200`，三个芭蕾 timer 均保持 `active`，页面缓存为 `styles.css?v=150` / `app.js?v=125`。

2026-07-27 部署主分支 `9a872ee`（版本 `1.0.5.20`），将顶部预约区重新拆为两个同级面板：左侧约 1/3 展示下一节，右侧约 2/3 展示全部预约且包含下一节。部署前页面和整份运行数据备份在 `/home/ubuntu/maxnow-deploy-backups/20260727-ballet-booking-tabs-0oS30D`；服务器运行数据在拉取后原样恢复。1440px 下两面板同顶同底、宽度比约 `1:1.92`；390px 下单列堆叠且无横向溢出。服务器全仓检查与 `nginx -t` 通过，匿名访问边界保持 Dash `302`、`ballet.json` `401`、Blog `200`；每日、月度和 Session 状态三个芭蕾 timer 均保持 `enabled / active`，enable gate 继续存在，部署过程未访问闻道。页面缓存为 `styles.css?v=151` / `app.js?v=126`。

2026-07-27 部署主分支 `187419f`（版本 `1.0.5.21`），将芭蕾页顶部改为“下一节预约 / 本周训练 / 课程卡”三个同级等宽面板，并把“所有预约”下移为独立全宽面板。部署前页面与整份运行数据备份在 `/home/ubuntu/maxnow-deploy-backups/20260727-225549-ballet-top-three-tabs`；服务器运行数据在拉取后原样恢复并重新生成 `project-meta.*`。本地浏览器验证 2048px 下三卡同顶、同底、等高且各宽约 556px，`1200px` 及以下按使用顺序堆叠，`860px` / `390px` 无横向溢出；服务器全仓检查与 `nginx -t` 通过，匿名访问边界保持 Dash `302`、`ballet.json` `401`、Blog `200`。每日、月度和 Session 状态三个芭蕾 timer 均保持 `enabled / active`，enable gate 继续存在，部署过程未访问闻道。页面缓存为 `styles.css?v=152` / `app.js?v=126`。

2026-07-27 部署主分支 `56b8e23`（版本 `1.0.5.22`），移除独立“下一节预约”卡，将“所有预约 / 本周训练 / 课程卡”合并为首屏三列；预约列表第一节（周二 7 月 28 日）作为“下一节”突出显示，桌面高度 `190px`，其余预约为 `60px` 紧凑行，移动端 `390px` 下大小对比约 `2.18` 倍，所有检查宽度均无横向溢出。部署前备份到 `/home/ubuntu/maxnow-deploy-backups/20260727-230759-ballet-booking-hierarchy`；恢复运行时数据时按服务器实际修改路径精确恢复，保留了并发提交 `5295795` 更新的 `codex-usage.*`。服务器 `scripts/check.py`、`nginx -t`、nginx reload、访问边界（Dash `302` / 芭蕾数据 `401` / Blog `200`）及芭蕾三个 timer 的 `enabled + active` 状态均通过，未访问闻道业务接口。静态缓存版本为 `styles.css?v=153` 与 `app.js?v=127`。

2026-06-17 晚间已部署参考风格刷新版本：

```text
deployed commit: 2290eca Merge reference style refresh
dash.maxnow.cn: 200 MaxNow
blog.maxnow.cn: 200 MaxNow Blog
nginx: config test ok, reload ok
```

2026-06-19 已部署豆奶详情页和 Blog / Dash 视觉微调版本：

```text
deployed commit: 8d099f1 Merge dounai and blog UI polish
dash.maxnow.cn: 200
blog.maxnow.cn: 200
blog.maxnow.cn/topics.html: 200
nginx: config test ok, reload ok
```

2026-06-19 已修复豆奶签到数据写入路径分叉问题：

```text
root 签到脚本: /root/.openclaw/daily_checkin.sh
root 数据生成脚本: /root/.openclaw/gen_checkin_data.py
备份: /root/.openclaw/gen_checkin_data.py.bak-20260619-dounai-sync
旧数据出口: /root/MaxNow/dash/data/dounai_checkin.json
线上数据出口: /var/www/maxnow-dashboard/dash/data/dounai_checkin.json
```

豆奶签到仍由 root 的 OpenClaw 自动化在每天 9 点左右执行。`gen_checkin_data.py` 现在会把同一份 `dounai_checkin.json` 同时写入旧 OpenClaw 工作区和 nginx 正在读取的线上部署目录，避免页面继续停留在旧记录。

2026-06-21 已扩展 `/root/.openclaw/gen_checkin_data.py`：生成 `dounai_checkin.json` 时会用现有豆奶登录态只读打开 `https://dounai.pro/user/panel`，抓取 `剩余流量(主)`、`账号有效期 (0级)` 和 `VIP有效期 (1级)`，写入 `account` 字段。页面据此展示剩余可用流量、到期日和按剩余天数折算的每日可用流量。脚本也会按日期维护 `account_history`，每天覆盖 / 追加当天账号快照，用于展示近 30 天账号日均可用流量趋势。脚本更新前已备份到：

```text
/root/.openclaw/gen_checkin_data.py.bak-20260621-account-summary
/root/.openclaw/gen_checkin_data.py.bak-20260621-account-history
```

当前已验证抓到的账号快照：

```text
remaining_flow_label: 1.29TB
account_expires_at: 2027-05-01 20:04:52
vip_expires_at: 2027-04-30 10:15:41
daily_available_mb: 4321.61
```

2026-06-21 已部署 Dash 顶栏和豆奶详情页自适应微调版本：

```text
changes: 移除 Dash 顶栏重复域名；豆奶详情页顶部 tab 和内部指标改为按宽度自适应换行
dash styles version: styles.css?v=41
```

同日已补充部署桌面端豆奶指标宽度修正：

```text
changes: 恢复豆奶详情页桌面端顶部 tab 原始横排比例；内部指标桌面端三列铺满，中小屏再换行
dash styles version: styles.css?v=42
```

2026-06-23 已部署 Home 顶部天气卡和小日历 widget 调整版本：

```text
deployed commit: f7ee6bb Scale top widget content further
changes: Home 顶部新增北京市海淀区天气卡；天气卡与小日历拆成独立同级 widget；两个 widget 外框等高，内部内容放大；天气数据由 runtime 定时刷新
dash styles version: styles.css?v=58
dash app version: app.js?v=42
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260623-235840-before-weather-widgets
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200
```

2026-06-24 已部署 Home 天气卡底部信息分隔点微调：

```text
deployed commit: fd7b997 Add weather meta separators
changes: 天气卡底部地点、天气状态和低温 / 高温之间加入轻量小圆点分隔；Dash 样式缓存版本提升到 styles.css?v=59
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署云服务 tab：

```text
feature merge commit: 8aa8400 Merge cloud services dashboard tab
changes: Dash 左侧导航在 Token 下方新增“云服务”tab，只读列出服务器自动化、数据同步、Token 用量采集方案、豆奶签到和 nginx / HTTPS 托管边界
dash styles version: styles.css?v=60
dash app version: app.js?v=44
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200
```

2026-06-24 已部署 Home 天气卡底部文字自适应微调：

```text
deployed commit: c336d60 Merge weather meta text fit
changes: 天气卡底部地点、天气状态和低温 / 高温接近溢出时自动收小字号；Dash 缓存版本提升到 styles.css?v=60、app.js?v=44
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署 Dash tab 间距、天气更新时间和云服务卡片层级修复：

```text
deployed commit: 5ac9126 Merge tab spacing and cloud hierarchy fixes
changes: 修复豆奶顶部 tab 间距；恢复 Token 页范围切换为右侧紧凑选项；Home 天气卡显示 HH:mm 更新时间；云服务页基础运行同步显式列出 logs/weather.log；强化云服务卡片顶部信息并弱化底部明细
dash styles version: styles.css?v=63
dash app version: app.js?v=45
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-092405-before-tab-spacing-cloud
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=63 200；https://dash.maxnow.cn/app.js?v=45 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署 Home 卡片操作和云服务系统状态入口：

```text
deployed commit: c941944 Merge home card actions
changes: Home 近期待办右上入口改为“更多”；Home Token 近期用量右上角改为更新时间；Home 系统状态卡支持点击 / Enter / Space 跳转云服务；云服务页新增系统状态卡复用 dashboardData.system；记录噗噗每日待办提醒后续项
dash styles version: styles.css?v=65
dash app version: app.js?v=47
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-095712-before-home-card-actions
verification: python3 scripts/check.py ok；python3 scripts/update_data.py project-meta ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=65 200；https://dash.maxnow.cn/app.js?v=47 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署我和 Ricky 的同行记页面：

```text
deployed commit: b7d02aa Merge Ricky companion map
changes: Dash 左侧导航新增“同行记”并放在最后一个 tab；页面使用 Leaflet + CARTO Voyager 真实地图展示我和 Ricky 的共同足迹；新增 dash/data/ricky.* 和 scripts/sync_ricky_travel.py，从 private personal-wiki 的 wiki/relationships/ricky-travel.json 同步数据；地点和旅行记录暂时只进入地图 marker / popup，不单独铺列表
dash styles version: styles.css?v=69
dash app version: app.js?v=52
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-210052-before-ricky-map
verification: python3 scripts/update_data.py runtime ok，同步 11 个 Ricky 地点和 4 条记录；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=69 200；https://dash.maxnow.cn/app.js?v=52 200；https://blog.maxnow.cn 200
```

2026-06-24 已部署同行记地图微调：

```text
deployed commit: 72dfbd6 Merge Ricky map display tuning
changes: 北海道地图点显示名缩短为“北海”；同行记页面左右留白收窄，地图高度提高，Leaflet fitBounds 最大缩放从 4 降到 3，让地图更宽并显示更多周边区域
dash styles version: styles.css?v=70
dash app version: app.js?v=53
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-212002-before-ricky-map-tune
runtime data stash before deploy: before-ricky-map-tune-runtime-data
verification: python3 scripts/update_data.py runtime ok，同步 11 个 Ricky 地点和 4 条记录；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/data/ricky.json 200；https://dash.maxnow.cn/styles.css?v=70 200；https://dash.maxnow.cn/app.js?v=53 200
```

2026-06-24 已部署同行记显式地图标签和正方形地图：

```text
deployed commit: df771be Merge explicit Ricky map labels
changes: personal-wiki Ricky 旅行地点新增 map_label；MaxNow 同步为 mapLabel，marker 不再取地点名前两个字；11 个标签为北京、札幌、东京、北海、大理、大同、天路、天津、沈阳、布统、阿那亚；同行记地图容器改为正方形居中展示
dash styles version: styles.css?v=71
dash app version: app.js?v=54
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-214401-before-ricky-labels-square
runtime data stash before deploy: before-ricky-labels-square-runtime-data
verification: python3 scripts/update_data.py runtime ok，同步 11 个 Ricky 地点和 4 条记录；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/data/ricky.json 200；https://dash.maxnow.cn/styles.css?v=71 200；https://dash.maxnow.cn/app.js?v=54 200；线上 ricky.json mapLabel 列表确认正确
```

2026-06-24 已部署 Codex Token 本机可读日志统计：

```text
deployed commit: 5e51d5c Add Codex token usage ledger
changes: 新增 Codex session `token_count` 本机可读日志账本、OpenClaw / Codex 统一 Token 总账和 Token 页统一数据入口；Codex 口径为本机可读 `.codex/sessions` 最终 `total_token_usage`，不导出 prompt / response 正文
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260624-225818-before-codex-token-usage
verification: python3 scripts/check.py ok；python3 scripts/update_data.py token-usage ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=55 200；https://dash.maxnow.cn/data/token-usage.json 200
```

2026-06-24 已部署 Token 缓存命中率和 Codex 模型 / 费用口径修正：

```text
deployed commit: 408cc6a Fix token cache rate and model cost basis
changes: Token 顶部新增缓存命中率；Codex 模型占比和调用列表显示 `gpt-5.5` 等真实模型名；Codex 费用改为 OpenAI API 等价估算并计入总费用
runtime data stash before deploy: before-token-model-cost-runtime-usage
verification: python3 scripts/update_data.py token-usage ok；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=72 200；https://dash.maxnow.cn/app.js?v=56 200；https://dash.maxnow.cn/data/token-usage.json 200；线上 token-usage 显示模型 `gpt-5.5`、缓存命中率 94.49%、估算费用 $590.10
```

2026-06-27 已部署本机 Codex Token 定期上报脚本：

```text
deployed commit: 25859dc Merge local Codex report SSH fix
changes: 新增 Windows 本机 Codex Token 上报脚本和 Task Scheduler 安装脚本；本机任务每 1 小时静默运行，只提交 codex-usage/token-usage 数据；服务器部署侧只合并 token-usage，不在服务器刷新本机 Codex collector；修复 PowerShell 远端 bash 脚本 CRLF 和 SSH 失败未冒泡问题
first manual report: 本机采集 86 个 Codex usage sessions，提交 d3e3f7c Update local Codex token usage，并推送到 origin/main
hourly hidden update: 2026-06-27 将任务改为每 1 小时静默运行；Task Scheduler action 先使用 powershell.exe -WindowStyle Hidden，任务设置 Hidden=true；远端 token 合并改为 base64 SSH payload，并按 SSH exit code 判断成败，避免 CRLF 和 git pull stderr 误判
no-flash update: 2026-07-02 将 Task Scheduler action 改为 wscript.exe scripts/report_codex_usage_hidden.vbs，由 VBS 以 window style 0 启动 PowerShell 上报脚本，避免 powershell.exe 仍可能产生的瞬时 console 闪窗
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/data/token-usage.json 200；隐藏计划任务手动启动后 LastTaskResult=0；服务器 HEAD 17f537d
```

2026-06-27 已部署豆奶图表动态刻度和 Token 默认范围修正：

```text
deployed commit: 613b64c Update local Codex token usage
included code commit: 55a1247 Fix chart scaling and token default range
changes: 折线图 y 轴对高位小波动数据使用动态刻度；豆奶日均可用流量图不再被 0 起点压扁；Token 页面默认范围从 7d 改为 1d
dash app version: app.js?v=57
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=57 200；https://blog.maxnow.cn 200
```

2026-06-27 已部署豆奶 GB 图表整数 y 轴刻度修正：

```text
deployed commit: fbe02f2 Use integer axis for dounai GB chart
changes: 豆奶“近 30 天日均可用流量”图保留动态缩放，但 y 轴边界改为整数 GB；4.19-4.26GB 这类数据展示为 4GB 到 5GB，点位标签仍保留两位小数
dash app version: app.js?v=58
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=58 200；线上 dash/app.js 确认 integerYScale 已启用
```

服务器部署博客预览时，曾将旧路径 `data/dashboard.*` 和 `data/wiki-todos.*` 备份到：

```text
~/maxnow-deploy-backups/20260617-180826
```

拉取新目录结构后，这些运行数据已恢复到 `dash/data/dashboard.*` 和 `dash/data/wiki-todos.*`。因此服务器工作区允许这些数据文件保持未提交状态，由后续同步脚本继续维护。

## GitHub CLI / private 仓库读取

2026-06-17 已确认服务器安装了 GitHub CLI：

```bash
command -v gh
gh auth status
```

当前服务器上的 `gh` 已授权为 `V-ioi-V`，scope 包含 `repo`，可读取 private `V-ioi-V/personal-wiki`。

验证 private personal-wiki 读取：

```bash
gh api 'repos/V-ioi-V/personal-wiki/contents/wiki/tasks/todo.json?ref=main' --jq .name
```

刷新 MaxNow 的 personal-wiki 待办缓存：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/sync_wiki_todos.py
python3 scripts/check.py
```

统一运行入口：

```bash
python3 scripts/update_data.py runtime
python3 scripts/update_data.py weather
python3 scripts/update_data.py market-indices
python3 scripts/update_data.py project-status
python3 scripts/update_data.py openclaw-usage
python3 scripts/update_data.py codex-usage
python3 scripts/update_data.py codex-macos-usage
python3 scripts/update_data.py codex-server-usage
python3 scripts/update_data.py token-usage
python3 scripts/update_data.py ai-last30
python3 scripts/update_data.py project-meta
python3 scripts/update_data.py wrap all
```

`runtime` 是服务器定时任务使用的安全入口，只刷新 wiki-todos、Ricky 旅行记录、生活页吃啥候选、天气、行情指数、系统状态、MaxNow 项目元信息和 wrapper，不覆盖 Owner 的今日判断或独立项目状态。`weather` 会刷新北京市海淀区天气卡，数据源为 Open-Meteo 免费 forecast API。`market-indices` 会刷新纳指100、标普500、上证指数、深证成指和创业板指，数据源为腾讯公开行情接口。`life-foods` 会从 private personal-wiki `wiki/life/food-picker.md` 同步生活页吃啥候选。`project-status` 会从 `ROADMAP.md` 显式刷新 `dash/data/project-status.*` 的当前主线 / 待推进、来源时间、生成时间和内容指纹；ROADMAP Now / Next / Done 变化后必须执行，且不会修改 `dashboard.today`。`openclaw-usage` 刷新 OpenClaw 源账本并合并统一 Token 总账；`codex-usage` 刷新 Windows 兼容本机 Codex 源账本并合并统一 Token 总账；`codex-macos-usage` 刷新 macOS 本机 Codex 源账本并合并统一 Token 总账；`codex-server-usage` 刷新服务器 Codex 源账本并合并统一 Token 总账；`token-usage` 只合并现有源账本。`ai-last30` 会刷新中文 AI 前沿简报和 Last-30 滚动记忆，优先正式发布、过滤客户案例并跨栏目去重；采集脚本本身不调用模型、不消耗 token。

刷新服务器 Codex Token 用量：

```bash
cd /var/www/maxnow-dashboard
sudo python3 scripts/update_data.py codex-server-usage
python3 scripts/check.py
```

本机 Windows 可直接在仓库目录运行：

```powershell
python scripts/update_data.py codex-usage
python scripts/check.py
```

本机 Windows 定期上报可以安装计划任务：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_local_codex_usage_task.ps1
```

默认任务名为 `MaxNow-Local-Codex-Usage-Report`，固定每小时 `:02` 静默运行。安装脚本会注册 hidden task，最长运行 10 分钟。Owner Windows 机器上当前使用专用 clone `D:\Personal\MaxNow-token-report`；Task Scheduler action 使用 `wscript.exe "D:\Personal\MaxNow-token-report\scripts\report_codex_usage_hidden.vbs"`，VBS launcher 再以 window style 0 启动 `scripts/report_codex_usage.ps1`。该任务要求运行目录在 `main` 且无无关脏文件，只提交 `dash/data/codex-usage.*` 源账本并推送到 `origin/main`。不要在服务器运行 `python3 scripts/update_data.py codex-usage`，否则会用服务器 `.codex` 覆盖 Windows 账本。

2026-07-06 修复过一次 Windows 专用 clone 上报卡住：主工作区 `D:\Personal\MaxNow` 配有 repo-local GitHub 代理，但 `D:\Personal\MaxNow-token-report` 缺少同样配置，导致计划任务在 `git pull --ff-only origin main` 处卡住或报 `Recv failure: Connection was reset`。当前该 clone 已设置：

```powershell
git -C D:\Personal\MaxNow-token-report config http.proxy http://127.0.0.1:7897
git -C D:\Personal\MaxNow-token-report config https.proxy http://127.0.0.1:7897
```

如果任务显示长时间 `Running` 且日志停在 `pull latest origin/main`，先检查 `git-remote-https` 是否卡住，再确认上述 proxy 仍存在。若专用 clone 因未推送生成物提交出现 `[origin/main: ahead ..., behind ...]`，先给当前 HEAD 建本地备份分支，再让 `main` 回到 `origin/main`，最后重新运行计划任务，由当前 `.codex/sessions` 重新生成 `codex-usage.*` 和 `token-usage.*`。2026-07-06 22:18 手动验证成功，`LastTaskResult=0`，线上 `Codex Windows` 来源更新时间为 `2026-07-06 22:18`。

本机 macOS 可直接在仓库目录运行：

```bash
python3 scripts/update_data.py codex-macos-usage
python3 scripts/check.py
```

本机 macOS 定期上报可以安装 launchd 任务：

```bash
bash scripts/install_local_codex_usage_launchd.sh
```

默认 label 为 `cn.maxnow.local-codex-usage-report`，通过 `StartCalendarInterval` 固定每小时 `:00` 运行。launchd 调用 `scripts/report_codex_usage.sh`，要求专用工作区位于 `main` 且无无关脏文件，只提交 `dash/data/codex-macos-usage.*` 并推送到 `origin/main`。Git HTTP 低速边界和 SSH keepalive 会让网络卡住后失败退出；日志写入 `~/Library/Logs/MaxNow/local-codex-usage-report.log`。

2026-07-14 起，macOS 上报会在每轮开始 fetch 最新 `origin/main`。如果专用 clone 因上次 push 被并发提交抢占而分叉，脚本只在所有本地独有提交标题均为 `Update macOS Codex token usage`、且只修改 `dash/data/codex-macos-usage.json/.js` 时自动 reset 到最新主线并重新生成；push 冲突同一轮最多重试 3 次。任何人工提交、其他提交标题或越界文件都会阻断自动恢复并写入日志，必须人工检查，禁止直接扩大自动 reset 范围。

2026-07-28 修复 macOS 上报专用 clone 的中断残留死锁：若上一次运行在生成 `dash/data/codex-macos-usage.json/.js` 后、提交前被一致性检查中断，下一轮会先确认没有任何越界改动，再恢复这两个任务自有生成文件并继续 fetch / 重新生成。任何代码、文档或其他数据文件改动仍会阻断自动恢复。该修复用于避免旧主线中的一次 Ballet 自检权限错误留下生成文件后，使任务永远停在“工作区不干净”阶段。

2026-07-07 已将 Owner macOS 的 launchd 任务改为使用专用 clone `/Users/bytedance/.maxnow-token-report`，plist 位于 `~/Library/LaunchAgents/cn.maxnow.local-codex-usage-report.plist`。原先指向 `/Users/bytedance/Desktop/Personal/MaxNow` 时，launchd 被 macOS Desktop 隐私权限拦截，日志出现 `Operation not permitted`，`launchctl print gui/501/cn.maxnow.local-codex-usage-report` 显示 `last exit code = 126`。修复命令为：

```bash
git clone git@github.com:V-ioi-V/MaxNow.git /Users/bytedance/.maxnow-token-report
bash scripts/install_local_codex_usage_launchd.sh --repo-root /Users/bytedance/.maxnow-token-report --run-now
```

修复后手动触发验证成功：`launchctl` 上次退出码为 `0`，`~/Library/Logs/MaxNow/local-codex-usage-report.log` 记录 `2026-07-07 17:32` 成功提交 `Update macOS Codex token usage`，线上 `token-usage.json` 的 `Codex macOS` 来源更新时间为 `2026-07-07 17:32`。

Codex collector 只读取 `.codex/sessions/**/*.jsonl` 中的 `token_count`、`turn_context.model` 和 `task_complete.duration_ms`，按 `total_token_usage` 相邻快照的正向增量与原始事件日期记账，并在同一会话树内去重分叉文件继承的历史；导出 token、已完成任务活跃时长、时间、来源、模型和费用估算，活跃时长不包含轮次之间空闲时间，不导出 prompt / response 正文。Windows、macOS、server 继续使用三个独立源账本。

2026-07-10 将 OpenClaw / Codex server 合并为固定小时源采集，标记块为 `MAXNOW-TOKEN-SOURCE-REFRESH`：

```cron
# BEGIN MAXNOW-TOKEN-SOURCE-REFRESH
5 * * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-token-source-refresh.lock /bin/bash scripts/refresh_token_sources_on_server.sh >> /var/www/maxnow-dashboard/logs/token-source-refresh.log 2>&1
# END MAXNOW-TOKEN-SOURCE-REFRESH
```

ubuntu crontab 在每小时 `:10` 拉取本机源账本并发布统一 Token 总账：

```cron
# BEGIN MAXNOW-TOKEN-USAGE-REFRESH
10 * * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-token-usage-refresh.lock /bin/bash scripts/refresh_token_usage_on_server.sh >> /var/www/maxnow-dashboard/logs/token-usage-refresh.log 2>&1
# END MAXNOW-TOKEN-USAGE-REFRESH
```

固定周期为 macOS `:00`、Windows `:02`、服务器源采集 `:05`、总账发布 `:10`。总账任务保留服务器运行态 `openclaw-usage.*` / `codex-server-usage.*`，再运行 `python3 scripts/update_data.py token-usage`；`git pull` 单次默认 120 秒超时，遇到并发 Git 更新等瞬时失败时最多尝试 3 次。

2026-07-28 11:10 的总账发布曾与另一条 Git 更新并发，`git pull` 因 `cannot lock ref 'refs/remotes/origin/main'` 退出，导致已经上报到 `origin/main` 的 macOS 源账本没有进入线上总账。11:28 使用原 cron 锁手动补跑后，总账更新为 `11:28`，Codex macOS 来源时间更新为 `11:00`；随后为拉取步骤增加有限重试，避免一次引用锁竞争漏掉整小时发布。

2026-07-02 已部署 Token 来源卡范围口径修正：

```text
deployed commit: 5ff48a9 Merge token source range display fix
changes: Token 来源卡恢复卡片样式；Dash 缓存版本提升到 styles.css?v=73、app.js?v=60；来源卡按当前 1d / 7d / 30d / all 范围聚合；本机来源显示为 Codex Windows，后续 macOS 采集端可显示为 Codex macOS
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260702-111659-before-token-source-range
verification: python3 scripts/update_data.py token-usage ok；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=73 200；https://dash.maxnow.cn/app.js?v=60 200；https://dash.maxnow.cn/data/token-usage.json 200；线上 token-usage 有 46 个 day 写入 bySource；线上 1d 来源为 Codex Windows 36M，7d 来源为 Codex Windows 79M / OpenClaw 8.0M / Codex server 614K
```

2026-07-02 已部署 Token 来源费用并列面板：

```text
deployed commit: 79ba56f Merge token source inline panel
changes: Token 页将来源费用移动到和模型占比、调用消耗同一行；删除独占横向说明条；说明收敛为来源面板底部短中文提示；Dash 缓存版本提升到 styles.css?v=74、app.js?v=61
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260702-113616-before-token-inline-panel
verification: python3 scripts/update_data.py token-usage ok；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn/styles.css?v=74 200；https://dash.maxnow.cn/app.js?v=61 200；本地浏览器验证 Token 三个 detail 面板同顶同高、无横向溢出
```

2026-07-02 已修正顶栏 `OpenClaw 异常` 误报：

```text
deployed commit: d3aeae3 Treat recovered sync logs as clear
changes: system-status 将 codex-server/ricky 等运行态数据纳入 deploy 白名单；忽略 Python __pycache__；failure-log 只按每个日志最新 ok/fail 结果判断，旧 weather TLS 超时后续成功后不再持续告警；runtime 将 system-status 放在运行态同步末尾执行
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260702-114519-before-openclaw-status-false-alarm
verification: python3 scripts/update_data.py runtime ok；python3 scripts/check.py ok；线上 dashboard automation.status=正常，summary=nginx Active；cert 73d；deploy v1.0.0.00；CPU 0%；disk 62%；memory 50%
```

2026-07-02 已部署全局主题色 hover：

```text
deployed commit: e41223e Merge global themed hover states
changes: Dash 大模块和内部模块统一使用主题色 hover；大模块按自身主题色，内部条目优先按 data-tone / 模型来源语义色；Token 来源卡、模型卡、调用卡和 Home / 云服务 / 豆奶 / 同行记模块保持一致；Dash 缓存版本提升到 styles.css?v=79、app.js?v=66
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=79 200；https://dash.maxnow.cn/app.js?v=66 200；本地浏览器验证 Home / Token / 云服务 / 豆奶 / 同行记桌面和移动端无横向溢出，抽样 hover 使用对应主题色
```

2026-07-02 已移除顶栏系统自动化重复状态：

```text
deployed commit: 7566242 Merge duplicate automation badge removal
changes: 删除 Dash 顶栏右侧 `系统自动化 正常` badge；保留 Home 首屏“系统自动化”状态卡作为唯一健康状态入口；Dash 缓存版本提升到 app.js?v=67
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=67 200；线上 dash/index.html 和 dash/app.js 确认无 operator-status 残留
```

2026-07-02 已压缩 Home 当前主线模块：

```text
deployed commit: 9e015ee Merge compact home mainline panel
changes: Home “当前主线”模块在桌面端改为标题和内容同一行的紧凑状态条；减少只有一条主线时的大面积空白；同步收紧待推进条目的垂直留白；Dash 缓存版本提升到 styles.css?v=80
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=80 200；本地浏览器测量桌面 #focus 高度约 101px，页面无横向溢出
```

2026-07-02 已修正 Home hover 主题色优先级：

```text
deployed commit: a72cc8b Merge home hover theme fix
changes: Home 指标卡 hover 不再被 status-strip 通用规则覆盖；待推进 / Token / 系统自动化分别使用橙色 / 紫色 / 绿色；天气卡按天气语义色 hover，时间卡使用橙色；Dash 缓存版本提升到 styles.css?v=81
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=81 200；本地浏览器抽样确认天气、时间、待推进、Token、系统自动化、wiki、豆奶、近期 Token 均使用对应主题色 hover
```

2026-07-02 已部署侧边栏 Token 范围口径同步：

```text
deployed commit: 4883cea Merge sidebar token range sync
changes: 侧边栏 Token 摘要增加范围前缀；Token 页切换 1d / 7d / 30d / all 时同步当前范围；其他页面默认显示 7d 摘要；Dash 缓存版本提升到 app.js?v=68
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/app.js?v=68 200；本地浏览器验证 Token 页 1d 显示 1d 86M，切换 7d 后侧边栏与主卡同步，回 Home 显示 7d 摘要
```

2026-07-02 已部署 Home / 同行记轻量交互整理：

```text
deployed commit: 7472f26 Remove wiki todo item links
changes: Last-30 条目改为整卡跳转并展示来源 / 置信度摘要；侧边栏豆奶和 Token 改回描述文案；同行记地图铺满地图卡宽度；Personal Wiki 近期待办移除逐条“打开”链接且卡片不跳转
dash styles version: styles.css?v=83
dash app version: app.js?v=71
verification: git pull --ff-only origin main ok；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=83 200；https://dash.maxnow.cn/app.js?v=71 200；https://blog.maxnow.cn 200
```

2026-07-02 已部署生活 tab 和吃啥随机选择器：

```text
deployed commit: 7a8a26f Keep existing life foods when wiki source is unavailable
feature commits: ff52586 Add life food picker；7a8a26f Keep existing life foods when wiki source is unavailable
changes: Dash 左侧导航新增“生活”tab；新增“吃啥”随机选择器、personal-wiki 菜品同步脚本和 dash/data/life-foods.*；吃啥结果区使用真实纵向滚动动画，数量为多个时上下叠放独立滚轮；脚本在服务器读不到 personal-wiki 源文件时保留现有 life-foods 缓存，避免 runtime 失败。
dash styles version: styles.css?v=86
dash app version: app.js?v=76
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260702-231615-before-life-food-picker
runtime data stash before deploy: before-life-food-picker-runtime-data
verification: git pull --ff-only origin main ok；python3 scripts/update_data.py runtime ok（life-foods 使用现有缓存，gh api 404 已降级为 warn）；python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/styles.css?v=86 200；https://dash.maxnow.cn/app.js?v=76 200；https://dash.maxnow.cn/data/life-foods.json 200；https://blog.maxnow.cn 200
```

2026-07-08 已部署 Dash 首屏加载优化：

```text
deployed commit: b0592ef Refresh project meta
feature commit: 03fda7c Optimize dash initial load
changes: Dash 首屏移除 data/*.js wrapper 同步加载，只保留 app.js?v=96；Home 先渲染核心小数据，Token / Ricky / Life / Leaflet 按视图加载；JSON fetch 改为正常 URL + cache:no-cache。
nginx changes: dash server block 启用 gzip；静态 css/js/png 设置 private, max-age=3600；/data/ 设置 private, max-age=60, must-revalidate。
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260708-124622-before-fast-load
nginx config backup before reload: /etc/nginx/sites-available/maxnow-dashboard.bak-20260708-fast-load
verification: python3 scripts/check.py ok；本地 Chrome headless 可执行并渲染 Token 热力格；服务器 nginx -t ok；reload ok；https://dash.maxnow.cn 200；线上 index 只引用 app.js?v=96；app.js?v=96 gzip 约 30KB；token-usage.json gzip 约 33KB；响应头确认 Cache-Control 和 Content-Encoding 生效。
```

2026-07-10 已部署 Today Status 时间轴和 Home 版本更新布局修复：

```text
deployed commit: 008ed5a Merge version update layout fixes
changes: 修复 Today Status 当前时间与进度条重叠；将“最近更新”改名为“版本更新”并移到外部输入下方；Dash 样式缓存版本提升到 styles.css?v=122；MaxNow 版本提升到 1.0.0.49。
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260710-093053-before-version-update
runtime data stash before deploy: before-version-update-deploy-20260710-093053
runtime preservation: 恢复 ai-news、dashboard、豆奶、Last-30、市场、OpenClaw、Codex Server、Ricky、Token 和 Wiki Todo 运行数据；重新生成 project-meta；Codex Server 账本保持 11 次会话和 4,993,467 Token。
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；nginx active；https://dash.maxnow.cn 200；https://blog.maxnow.cn 200；线上 VERSION 1.0.0.49；styles.css?v=122 已生效。
```

2026-07-10 已部署 Home 项目状态可信度修复：

```text
deployed commit: eade306 Fix Home project status freshness
changes: ROADMAP 生成状态从 dashboard.* 拆到独立 project-status.*；新增来源时间、生成时间、7 天过期阈值和内容指纹；过期状态不再驱动 Today Status；scripts/check.py 拒绝 Done 或与 ROADMAP 不一致的事项
dash styles version: styles.css?v=123
dash app version: app.js?v=108
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260710-104139-before-home-project-status
runtime preservation: 恢复 ai-news、dashboard、豆奶、Last-30、市场、Ricky 和 Wiki Todo；从 dashboard 运行态移除旧 mainlines/actions 后重生成 wrapper；重新生成 project-meta
verification: python3 scripts/check.py ok；nginx -t ok；reload ok；https://dash.maxnow.cn 200；https://dash.maxnow.cn/data/project-status.json 200；线上 VERSION 1.0.0.51；待推进为访问保护、数据健康闭环、前端自动测试
```

2026-07-10 已部署 Token 活跃时长和固定小时周期：

```text
deployed commit: cacd002 Update macOS Codex token usage
feature commit: 178bbd0 Add token runtime and fixed reporting cycle
changes: Codex 账本新增 task_complete.duration_ms 活跃时长；固定周期为 macOS :00、Windows :02、服务器源采集 :05、总账发布 :10；本机 Git 增加低速和 SSH keepalive 边界；Token 页新增 Codex 时长并修复 390px 图表横向溢出
dash styles version: styles.css?v=124
dash app version: app.js?v=109
runtime data backup before deploy: /home/ubuntu/maxnow-deploy-backups/20260710-115834-before-token-runtime
root crontab backup: /home/ubuntu/maxnow-deploy-backups/20260710-115913-root-crontab-before-token-cycle
ubuntu crontab backup: /home/ubuntu/maxnow-deploy-backups/20260710-115913-ubuntu-crontab-before-token-cycle
runtime preservation: 恢复 dashboard、AI、Last-30、Wiki、市场、同行记、生活、豆奶、OpenClaw 和 Codex Server 运行态数据；重新生成 project-meta 和 token-usage
verification: macOS launchd StartCalendarInterval Minute=0、首次运行 exit 0；root :05 / ubuntu :10 cron 生效且旧 Token cron 已移除；OpenClaw 373 runs、Codex Server 11 sessions；总账 activeSeconds=226868、completedTurns=3738；python3 scripts/check.py ok；nginx -t ok；https://dash.maxnow.cn 200；线上 v1.0.0.52、1d Codex 时长 20m、无横向溢出
```

2026-07-10 已部署中文 AI 前沿简报：

```text
deployed commit: 538dc40 Update Codex usage data
feature commit: 1cde610 feat: turn Last-30 into AI frontier brief
changes: Home “外部输入”改为“AI 前沿”，固定展示“最新发布 / 本周前沿 / 近 30 天关键进展”；页面只显示中文事实标题、具体变化、来源和日期，过滤客户案例、纯 SDK 版本和“关注它”等套话。
runtime data backup before deploy: /tmp/maxnow-pre-ai-frontier-20260710-223503
runtime data stash before deploy: pre-ai-frontier-deploy-20260710-223503
runtime preservation: 只恢复 dashboard、豆奶、行情、同行记和 Wiki Todo；不恢复旧 ai-news、last-30、project-meta，随后重新生成 AI 前沿与项目元信息。
verification: python3 scripts/sync_ai_last30.py ok（1 个免费源部分失败）；python3 scripts/update_data.py project-meta ok；python3 scripts/check.py ok；nginx -t ok；线上目录包含“AI 前沿”，最新发布为 GPT-5.6、ChatGPT Work、GPT-Live，禁用套话检查为 false。
```

2026-07-10 已部署 Today Status 倒序时间轴与节点对齐修复：

```text
deployed commit: 1249e0f fix: reverse Today status timeline
changes: 时间轴改为上方 24:00、下方 00:00，当前时间点和已过时间填充从下向上推进；右侧信号节点中心与各行首行文字中心对齐；缓存提升到 styles.css?v=129 / app.js?v=111，版本提升到 1.0.3.02。
runtime data backup before deploy: /tmp/maxnow-pre-today-axis-20260710-225813
runtime data stash before deploy: pre-today-axis-20260710-225813
runtime preservation: 拉取代码前完整备份并暂存 dash/data，拉取后恢复全部运行数据，再重新生成 project-meta。
verification: python3 scripts/check.py ok；Today axis 回归校验 ok；nginx -t ok；线上源文件确认顶部 24:00、底部 00:00、向上填充和倒序 marker 均已生效。
```

2026-07-10 已部署 AI 前沿栏头精简：

```text
deployed commit: ca6fa87 fix: simplify AI frontier headings
changes: 三栏只保留蓝色时间范围“最近 3 天 / 本周 / 近 30 天”，删除重复的黑色栏目名和栏目简介；缓存提升到 styles.css?v=130 / app.js?v=112，版本提升到 1.0.3.03。
runtime data backup before deploy: /tmp/maxnow-pre-ai-headings-20260710-231228
runtime data stash before deploy: pre-ai-headings-20260710-231228
runtime preservation: 拉取代码前完整备份并暂存 dash/data，拉取后恢复全部运行数据，再重新生成 project-meta。
verification: python3 scripts/check.py ok；nginx -t ok；线上源文件确认三个蓝色时间标签均存在，冗余栏目名和栏目简介均不存在。
```

2026-07-10 已部署 Today Status 圆形日进度：

```text
deployed commit: a32a0ed feat: replace Today axis with progress ring
changes: 用青色 24 小时圆形进度环替换竖向时间轴，环内显示今天已过去的整数百分比，当前时间显示在环外；桌面 / 窄屏圆环分别为 112px / 96px；缓存提升到 styles.css?v=131 / app.js?v=113，版本提升到 1.0.3.04。
runtime data backup before deploy: /tmp/maxnow-pre-today-ring-20260710-232018
runtime data stash before deploy: pre-today-ring-20260710-232018
runtime preservation: 拉取代码前完整备份并暂存 dash/data，拉取后恢复全部运行数据，再重新生成 project-meta。
verification: python3 scripts/check.py ok；nginx -t ok；线上源文件确认圆环、环内百分比、环外时间均存在，旧竖轴代码已移除。
```

2026-07-10 已部署全部非首页页面统一视觉：

```text
deployed commit: 18c8c67 feat: unify secondary tab styling
changes: 豆奶、Token、云服务、生活和同行记统一使用 secondary-view / secondary-page-head；共用顶部 4px 主题线、轻色渐变白底、圆角、阴影、hover / focus 和状态 pill，各页保留自己的语义色；缓存提升到 styles.css?v=132，版本提升到 1.0.4.00。
runtime data backup before deploy: /tmp/maxnow-pre-secondary-style-20260710-233245
runtime data stash before deploy: pre-secondary-style-20260710-233245
runtime preservation: 拉取代码前完整备份并暂存 dash/data，拉取后恢复全部运行数据，再重新生成 project-meta。
verification: 五页桌面并列卡同顶同底；390px 窄屏全部单列且 overflow=0；python3 scripts/check.py ok；nginx -t ok；线上源文件确认五个 secondary view / page head 均存在，Home 未继承该外壳。
```

2026-07-10 已部署 Today Status 留白与响应式分区修复：

```text
deployed commit: 889d065 fix: space Today status signals
changes: 将“自动生成”移回 Today Status 标识旁；圆环列扩为 140px，与四条等高信号保留 30px；当前时间改为环下独立 pill；1500px 及以下让天气与日历整组换到状态卡下方；缓存提升到 styles.css?v=133，版本提升到 1.0.4.01。
runtime data backup before deploy: /tmp/maxnow-pre-today-spacing-20260710-235037
runtime data stash before deploy: pre-today-spacing-20260710-235037
runtime preservation: 拉取代码前完整备份并暂存 dash/data，拉取后恢复全部运行数据，再重新生成 project-meta。
verification: 2048px 下圆环与信号列间距 30px、四行高度一致且无重叠；1366px 下状态文案宽度 626px、天气与日历下移；390px 窄屏 overflow=0；python3 scripts/check.py ok；nginx -t ok；线上源文件确认 v133、summary-kicker、140px 圆环列和四条等分行均存在。
```

2026-07-11 已部署 Today Status 圆环居中与信号首行对齐：

```text
deployed commit: e89cb2a fix: center Today status ring
changes: 1501px 以上使用左文案 / 140px 圆环 / 右信号三列，左右区域等宽以保证圆环位于状态卡内容区正中央；彩色节点改为第一行网格项，与标签和主值对齐；缓存提升到 styles.css?v=134，版本提升到 1.0.4.02。
runtime data backup before deploy: /tmp/maxnow-pre-center-ring-20260711-001014
runtime data stash before deploy: pre-center-ring-20260711-001014
runtime preservation: 拉取代码前完整备份并暂存 dash/data，拉取后恢复全部运行数据，再重新生成 project-meta。
verification: 2048px 下圆环中心与状态卡中心误差小于 0.001px，四行标签与主值基线最大误差约 0.09px；1366px / 390px 无横向溢出；python3 scripts/check.py ok；nginx -t ok；线上源文件确认 v134、等宽三列和第一行节点规则均存在。
```

2026-07-11 已部署全部 tab 卡片顶部彩条移除：

```text
deployed commit: ce4ea10 style: remove card top accent bars
changes: Home、豆奶、Token、云服务、生活和同行记的页头卡、摘要卡、普通面板、图表卡与统计卡统一取消顶部 4px 彩色或渐变强调线；保留文字、数值、图标、状态点、pill、边框反馈和轻背景中的语义色；缓存提升到 styles.css?v=135，版本提升到 1.0.4.03。
runtime data backup before deploy: /tmp/maxnow-pre-clean-cards-20260711-002837
runtime data stash before deploy: pre-clean-cards-20260711-002837
runtime preservation: 拉取代码前完整备份并暂存 dash/data，拉取后恢复全部运行数据，再重新生成 project-meta。
verification: 2048px 与 390px 下逐页检查 6 个 tab，卡片顶部彩条计数均为 0、横向溢出均为 0、控制台无报错；python3 scripts/check.py ok；nginx -t ok；线上源文件确认 v135 且旧顶条选择器均不存在。
```

2026-07-15 已部署数据失败与新鲜度闭环：

```text
deployed commit: bad3b3b Avoid deployment bytecode artifacts
changes: 10 个 Owner 可见数据源统一区分已同步、暂无记录、读取失败、数据过期和尚未同步；关键自动化连续 3 次失败时进入异常；最近成功日志可清除历史失败；检查脚本不再生成 Python 字节码产物；版本提升到 1.0.4.08。
runtime data backups before deploy: /home/ubuntu/maxnow-deploy-backups/20260715-171334-before-data-health；/home/ubuntu/maxnow-deploy-backups/20260715-171558-before-data-health-recovery-fix
runtime preservation: 拉取代码前备份并暂存 dash/data，拉取后恢复运行数据，再执行 runtime 生成和一致性检查。
verification: python3 scripts/update_data.py runtime ok；python3 scripts/check.py ok；nginx -t 与 reload ok；automation-failures 为 Clear；data-health 为 9/10 正常，Life 数据因 personal-wiki 源读取 404 保留旧缓存并显示数据过期，系统总状态因此为“注意”。
```

刷新 Home 天气卡：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py weather
python3 scripts/check.py
```

天气卡读取 `dash/data/dashboard.json.weather`，由 `scripts/sync_weather.py` 写入并同步生成 `dash/data/dashboard.js`。当前位置固定为北京市海淀区，坐标约 `39.96, 116.30`。前端只读本地数据，不直接请求天气接口。

刷新 Home 市场涨幅卡：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py market-indices
python3 scripts/check.py
```

市场涨幅卡读取 `dash/data/market-indices.json`，由 `scripts/sync_market_indices.py` 写入并同步生成 `dash/data/market-indices.js`。当前指数为纳指100、标普500、上证指数、深证成指和创业板指；脚本保存点位、昨收、涨跌幅和压缩后的 1 日分钟走势点。前端只读本地数据，不直接请求第三方行情接口。

刷新中文 AI 前沿简报和 Last-30：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py ai-last30
python3 scripts/check.py
```

当前免费源包括官方 RSS / 博客、GitHub releases、Hacker News、GDELT 和 arXiv 等。免费源偶发超时或限流时，脚本会记录部分失败并保留其他结果；X / Twitter 暂不作为基础来源。

2026-06-23 已用 `ubuntu` 用户 crontab 接入 AI Last-30 免费外部信号同步，标记块为 `MAXNOW-AI-LAST30-SYNC`：

```cron
0 0 * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-ai-last30.lock /bin/bash -lc 'set -o pipefail; echo "[$(date -Is)] maxnow ai-last30 sync start"; python3 scripts/update_data.py ai-last30; echo "[$(date -Is)] maxnow ai-last30 sync ok"' >> /var/www/maxnow-dashboard/logs/ai-last30.log 2>&1
```

该任务每天服务器本地时间 00:00 刷新 `dash/data/ai-news.*` 和 `dash/data/last-30.*`。脚本只使用免费公开源，本身不调用模型、不消耗 token。输出固定分为“最新发布 / 本周前沿 / 近 30 天关键进展”，以中文事实标题和具体变化为展示口径；同一事件跨栏去重，客户案例、泛采用、纯 SDK 版本号和关键词关注套话不得占据前沿位置。

刷新 MaxNow 版本号和最近更新模块：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py project-meta
python3 scripts/check.py
```

版本号由仓库根目录 `VERSION` 手动维护，格式为 `x.x.x.xx`，例如 `1.0.0.00`。`scripts/sync_project_meta.py` 会读取 `VERSION`、Git 状态和 `UPDATE_LOG.md`，生成 `dash/data/project-meta.json` / `dash/data/project-meta.js`。

版本提升规则：

- 小 UI / 文案 / 布局调整：升最后两位，例如 `1.0.0.00` -> `1.0.0.01`。
- 新增页面能力 / 新数据源 / 新自动化：升最后两位。
- 重要功能模块稳定落地：升 patch，并把最后两位归零，例如 `1.0.0.12` -> `1.0.1.00`。
- 大版本阶段切换：升 minor 或 major，并重置后续位。
- 每次完成 Owner 可见或运维相关改动后，都要同步更新 `VERSION` 并运行 `python scripts/update_data.py project-meta`。

刷新 OpenClaw Token 用量账本：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/update_data.py openclaw-usage
python3 scripts/check.py
```

`scripts/sync_openclaw_usage.py` 只读 `/root/.openclaw/agents/main/sessions/*.trajectory.jsonl`、cron runs 和 sessions 元数据，生成 `dash/data/openclaw-usage.json` / `dash/data/openclaw-usage.js`。它按 Asia/Shanghai 日期聚合 input / output / cacheRead / total token，并用 OpenRouter 模型价格生成 `openrouter-equivalent` 费用估算。该费用不是真实供应商账单。默认采集长期窗口，Token 页面再切分 1d / 7d / 30d / all。

OpenClaw trajectory 位于 `/root/.openclaw`，普通 `ubuntu` 用户不能读取，因此由 root 的 `MAXNOW-TOKEN-SOURCE-REFRESH` 每小时 `:05` 与 Codex server 一起刷新；任务结束后恢复前端数据文件归属：

```cron
# BEGIN MAXNOW-TOKEN-SOURCE-REFRESH
5 * * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-token-source-refresh.lock /bin/bash scripts/refresh_token_sources_on_server.sh >> /var/www/maxnow-dashboard/logs/token-source-refresh.log 2>&1
# END MAXNOW-TOKEN-SOURCE-REFRESH
```

2026-07-07 修复：线上 `openclaw-usage.*` 曾被仓库空基线覆盖，导致 Token 页只剩 Codex 来源。已用 root 重新运行 `python3 scripts/update_data.py openclaw-usage`，恢复 346 个 OpenClaw runs，并加固本机 Codex 上报脚本的服务器合并逻辑：空运行时备份不会覆盖非空账本，OpenClaw 为空时会优先用 `/root/.openclaw` 刷新源账本。

2026-07-05 复查：`logs/openclaw-usage.log` 显示 2026-07-03、2026-07-04、2026-07-05 均完成 `maxnow openclaw usage sync ok`，线上 `dash/data/openclaw-usage.json` 已更新到 2026-07-05 00:20。

刷新 MaxNow 的系统状态缓存：

```bash
cd /var/www/maxnow-dashboard
python3 scripts/sync_system_status.py
python3 scripts/check.py
```

`scripts/sync_system_status.py` 只更新 `dash/data/dashboard.json` / `dash/data/dashboard.js` 中的 `automation` 和 `system` 字段，用来展示 nginx、HTTPS、证书到期、腾讯云位置、计费/有效期、git commit、最近拉取、wiki-todos 同步、定时任务、失败日志、CPU、磁盘、内存和 uptime。它不应该覆盖 `dashboard.today`、日常记录或独立的 `project-status.*`。

在腾讯云服务器上，它还会通过 metadata 服务读取：

```bash
curl http://metadata.tencentyun.com/latest/meta-data/instance-id
curl http://metadata.tencentyun.com/latest/meta-data/public-ipv4
curl http://metadata.tencentyun.com/latest/meta-data/placement/region
curl http://metadata.tencentyun.com/latest/meta-data/placement/zone
curl http://metadata.tencentyun.com/latest/meta-data/payment/charge-type
curl http://metadata.tencentyun.com/latest/meta-data/payment/termination-time
curl http://metadata.tencentyun.com/latest/meta-data/payment/create-time
```

当前服务器可读到：`ap-singapore` / `ap-singapore-2`，实例 `ins-2814k2h0`，按量计费 `POSTPAID_BY_HOUR`，`termination-time=null`，因此没有固定包年包月到期日。

证书到期由脚本直接检查 `https://dash.maxnow.cn` 的 TLS 证书。最近拉取时间来自 `.git/FETCH_HEAD` 的修改时间。

## 服务器资源清理记录

2026-07-05 已处理一次磁盘和内存占用排查：

- 根盘清理前约 `25G / 40G`，使用率约 66%；清理后约 `21G / 40G`，使用率约 56%。
- `lighthouse-chromium.service` 曾以 `Restart=always` 每 3 秒失败重启，24 小时内产生大量 journal。失败原因是该服务使用 `/root/.openclaw/browser-existing-session` 作为 Chromium profile，但已有 OpenClaw Chromium 会话持有 `SingletonLock`。
- 已执行 `sudo systemctl stop lighthouse-chromium.service` 和 `sudo systemctl disable lighthouse-chromium.service`，复查状态为 `disabled` / `inactive`。
- 已用 `sudo journalctl --vacuum-size=300M` 将 systemd journal 从约 2.8G 降到约 264M。
- 已清理 apt cache、npm cache、pnpm metadata cache，并删除 Playwright 中未被当前进程使用的 `ffmpeg-1011` 和 `chromium_headless_shell-1208`。
- 已保留 `/root/.cache/ms-playwright/chromium-1208`，因为当前 OpenClaw Chromium 进程仍从该目录运行；不要在未安排 OpenClaw 浏览器维护窗口时删除它。

后续如果确实需要恢复 `lighthouse-chromium.service`，应先确认 9222 端口和 Chromium profile 归属，只保留一个浏览器 owner，或给该 service 配置独立 `--user-data-dir`，避免再次与 OpenClaw 浏览器会话争用同一个 profile。

2026-07-06 已修复一次豆奶自动化 Playwright 浏览器缺失：

- 现象：09:00 豆奶签到和 00:05 traffic closeout 均报 `BrowserType.launch: Executable doesn't exist`，路径指向 `/root/.cache/ms-playwright/chromium_headless_shell-1208/...`；`dash/data/dounai_checkin.json` 的 `updatedAt` 会变化，但 `today`、账号快照和真实流量仍停在旧日期，并可能出现 `stale` / `last_error`。
- 原因：清理服务器缓存后只保留了 `/root/.cache/ms-playwright/chromium-1208`，但当前 Python Playwright 1.58.0 的脚本启动 headless Chromium 时需要 `chromium_headless_shell-1208`。
- 修复：以 root 执行 `python3 -m playwright install chromium`，补齐 `/root/.cache/ms-playwright/chromium_headless_shell-1208` 和 `/root/.cache/ms-playwright/ffmpeg-1011`，再用 `sync_playwright().chromium.launch(headless=True)` 做 smoke test。
- 补数：使用 `/root/.openclaw/daily_checkin.sh` 手动补跑签到和 MaxNow 数据同步；该脚本不发微信通知。不要为了补数直接运行 `/root/.openclaw/dounai_cron.sh`，因为它会向 WeChat 发送签到通知。
- 日结：补签后可运行 `python3 /root/.openclaw/gen_checkin_data.py --traffic-only --exclude-today`，让真实流量历史继续排除当天不完整数据。
- 清理规则：以后清理 Playwright 缓存前，先用 `python3 -m playwright --version` 和一次 headless launch smoke test 确认当前脚本需要的浏览器目录；不要只凭目录名判断 `chromium_headless_shell-*` 可删除。

2026-06-18 已用 `ubuntu` 用户 crontab 接入 dashboard 数据同步，标记块为 `MAXNOW-DASHBOARD-SYNC`：

```cron
*/10 * * * * cd /var/www/maxnow-dashboard && /usr/bin/flock -n /tmp/maxnow-dashboard-sync.lock /bin/bash -lc 'set -o pipefail; echo "[$(date -Is)] maxnow dashboard sync start"; python3 scripts/update_data.py runtime; echo "[$(date -Is)] maxnow dashboard sync ok"' >> /var/www/maxnow-dashboard/logs/maxnow-sync.log 2>&1
```

该任务会通过 `runtime` 一并刷新 wiki-todos、Ricky 旅行记录、生活页吃啥候选、北京市海淀区天气、系统状态和项目元信息。

查看当前 crontab：

```bash
crontab -l
```

失败日志目前按以下位置检测：

```text
/var/www/maxnow-dashboard/logs/ai-last30.log
/var/www/maxnow-dashboard/logs/wiki-todos.log
/var/www/maxnow-dashboard/logs/weather.log
/var/www/maxnow-dashboard/logs/market-indices.log
/var/www/maxnow-dashboard/logs/system-status.log
/var/www/maxnow-dashboard/logs/maxnow-sync.log
```

`scripts/sync_system_status.py` 会从这些日志以及 `token-source-refresh.log` / `token-usage-refresh.log` 中识别成对的 `start` / `ok` 记录。Dashboard runtime、AI Last-30、Token sources 或 Token ledger 任一任务连续 3 次没有成功结束时，Home 系统自动化状态变为异常，并在“连续失败”项显示任务名和次数。`scripts/update_data.py` 的子同步失败后会补跑一次系统状态采集，让连续失败在故障轮次内写入 Dashboard；最近一次仍可能正在执行且没有明确错误的 20 分钟内未闭合记录不计入连续失败，避免瞬时误报。

同一状态采集还会读取 11 个 Owner 可见数据源的最后成功时间，输出已同步、暂无记录、读取失败、数据过期、需要重新登录或尚未同步。前端 JSON 请求失败属于浏览器侧状态，会继续展示浏览器保存的最后成功数据；服务器文件读取失败则进入 `data-health` 系统状态。

如果只想预览将采集到的状态，不写文件：

```bash
python3 scripts/sync_system_status.py --dry-run
```

注意：运行同步脚本会改写 `dash/data/wiki-todos.*` 或 `dash/data/dashboard.*`。如果只是验证能力而不想保留工作区改动，可以执行：

```bash
git checkout -- dash/data/wiki-todos.json dash/data/wiki-todos.js dash/data/dashboard.json dash/data/dashboard.js
```

## 豆奶签到数据同步

豆奶签到自动化不由 `ubuntu` 用户的 `MAXNOW-DASHBOARD-SYNC` cron 直接执行；它由 root/OpenClaw 侧脚本维护：

```bash
sudo crontab -l
sudo tail -120 /root/.openclaw/checkin.log
sudo tail -120 /root/.openclaw/traffic_closeout.log
sudo python3 /root/.openclaw/gen_checkin_data.py
sudo python3 /root/.openclaw/gen_checkin_data.py --traffic-only --exclude-today
```

日常预期：

- 签到脚本先更新 `/root/.openclaw/dounai_weekly.json`。
- `gen_checkin_data.py` 从 weekly 数据生成最近 60 天的 `dounai_checkin.json`。
- 同一份结果同时写入 `/root/MaxNow/dash/data/dounai_checkin.json` 和 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。
- `gen_checkin_data.py` 还会抓取豆奶用户面板上的剩余流量和有效期，写入 `account` 字段，并维护最近 60 天 `account_history`；如果抓取失败，会尽量保留上一份 `account` 和 `account_history`，并标记 `stale` / `last_error`。
- root crontab 里有两个豆奶任务：09:00 的 `MAXNOW-DOUNAL-CHECKIN` 负责签到、账号快照和完整生成；00:05 的 `MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT` 只运行 `gen_checkin_data.py --traffic-only --exclude-today`，专门更新昨天及更早的真实流量使用量。
- 线上 `dash.maxnow.cn` 读取 `/var/www/maxnow-dashboard/dash/data/dounai_checkin.json`。

2026-07-21 已把账号余量和日均可用预算切换为字节级精确口径：

- `/root/.openclaw/gen_checkin_data.py` 先从用户面板已有的“查看地址”入口读取专属订阅，再只读取标准 `subscription-userinfo` header 的 `total / upload / download`；`remaining_flow_bytes = total - upload - download`，`remaining_flow_mb` 和 `daily_available_mb` 均从该精确值换算。
- 生成数据成功时写入 `remaining_flow_precision: byte` 和 `source: dounai.pro/subscription-userinfo`；订阅地址、查询参数和令牌不写入数据文件或日志。响应头不可用时保留原用户面板解析作为降级，并标记 `remaining_flow_precision: rounded-label`。
- `account_history` 从 2026-07-21 起同步保存 `remaining_flow_bytes` 和精度标记；此前只有两位 TB / GB 标签的历史点保持原样，不伪造精确历史。
- 正式脚本备份：`/root/.openclaw/gen_checkin_data.py.bak-20260721-precise-traffic`；首次刷新前数据备份：`/tmp/dounai_checkin-before-precise-20260721.json`。
- 首次线上验证得到 `remaining_flow_precision=byte`，`remaining_flow_bytes=1368690004659`，`daily_available_mb=4563.93`（约 `4.46 GB/d`），两份输出均成功写入并通过 `python3 scripts/check.py`。

2026-07-26 已把日均可用预算的时间分母切换为精确剩余时长：

- `/root/.openclaw/gen_checkin_data.py` 新增 `remaining_days_exact`，按账号快照时刻到 `effective_expires_at` 的剩余秒数除以 86400 得到。
- `daily_available_mb` 改为 `remaining_flow_mb / remaining_days_exact`；`days_remaining` 继续保留为整天摘要，但不再参与预算计算，避免签到延长有效期后连续两天整数分母相同而产生锯齿式假下降。
- `account` 和当天 `account_history` 保存同一精确时长字段；2026-07-25 及更早历史点保持原口径，不回填伪造的精确时长。

2026-07-05 已做只读调研并接入直接流量使用抓取，确认当前数据边界：

- `records` 保存签到奖励记录，当前线上有 61 天。
- `account_history` 从 2026-06-21 开始保存账号余量快照，截至 2026-07-05 只有 15 天，不足完整 30 天。
- 重新登录后确认豆奶用户区有 `流量日志`：`https://dounai.pro/user/trafficlog` 直接展示最近 7 天真实使用量。
- `https://dounai.pro/user/trafficlog?ajax=1` 返回近 12 小时节点活跃和节点流量占比；这个窗口不是 7 天或 30 天总量。
- 已备份 `/root/.openclaw/gen_checkin_data.py` 到 `/root/.openclaw/gen_checkin_data.py.bak-20260705-traffic-usage`，并扩展脚本写入 `traffic_usage` 和 `traffic_usage_history`。
- 2026-07-05 已再次备份 `/root/.openclaw/gen_checkin_data.py` 到 `/root/.openclaw/gen_checkin_data.py.bak-20260705-traffic-closeout`，新增 `--traffic-only --exclude-today` 模式。
- 2026-07-05 已备份 root crontab 到 `/root/.openclaw/root-crontab-20260705-traffic-closeout.bak`，并新增 `MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT`：
- 2026-07-06 手动恢复后线上 `today` 为 `2026-07-06`，`account.synced_at` 为 `2026-07-06 21:28`，`traffic_usage.synced_at` 为 `2026-07-06 21:29`，并确认 `account` / `traffic_usage` 不再带 `stale` 或 `last_error`。

```cron
# BEGIN MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT
5 0 * * * cd /root/.openclaw && /usr/bin/flock -n /tmp/maxnow-dounai-traffic-closeout.lock /bin/bash -lc 'set -o pipefail; echo "[$(date -Is)] dounai traffic closeout start"; python3 /root/.openclaw/gen_checkin_data.py --traffic-only --exclude-today; chown ubuntu:www-data /var/www/maxnow-dashboard/dash/data/dounai_checkin.json; echo "[$(date -Is)] dounai traffic closeout ok"' >> /root/.openclaw/traffic_closeout.log 2>&1
# END MAXNOW-DOUNAI-TRAFFIC-CLOSEOUT
```

- 00:05 traffic closeout 会从 `traffic_usage.daily` 和 `traffic_usage_history` 中剔除当天，只保留昨天及更早日期；每日 9 点豆奶自动化仍可用于签到和账号快照。前端实际使用量图也会排除当天。
- 账号余量差分口径只作为缺数据时的兜底估算说明；真实使用量展示优先使用 `traffic_usage_history`。

验证今天是否进入线上页面：

```bash
sudo python3 - <<'PY'
import json
from pathlib import Path
for path in [
    Path('/root/MaxNow/dash/data/dounai_checkin.json'),
    Path('/var/www/maxnow-dashboard/dash/data/dounai_checkin.json'),
]:
    data = json.loads(path.read_text(encoding='utf-8'))
    print(path, data.get('updatedAt'), data.get('today'))
PY

cd /var/www/maxnow-dashboard
python3 scripts/check.py
```

## 首次部署命令

这些命令已在服务器上执行过，记录在这里方便复现：

```bash
sudo apt-get update
sudo apt-get install -y nginx git

sudo rm -rf /var/www/maxnow-dashboard
sudo git clone --branch main https://github.com/V-ioi-V/MaxNow.git /var/www/maxnow-dashboard
sudo chown -R ubuntu:www-data /var/www/maxnow-dashboard

sudo tee /etc/nginx/sites-available/maxnow-dashboard >/dev/null <<'EOF'
server {
  server_name dash.maxnow.cn;

  root /var/www/maxnow-dashboard/dash;
  index index.html;

  gzip on;
  gzip_vary on;
  gzip_min_length 1024;
  gzip_types text/css application/javascript application/json image/svg+xml;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location ~* \.(?:css|js|png)$ {
    add_header Cache-Control "private, max-age=3600";
    try_files $uri =404;
  }

  location /data/ {
    add_header Cache-Control "private, max-age=60, must-revalidate";
  }

  listen 443 ssl;
  ssl_certificate /etc/letsencrypt/live/dash.maxnow.cn/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/dash.maxnow.cn/privkey.pem;
  include /etc/letsencrypt/options-ssl-nginx.conf;
  ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
  listen 80;
  server_name dash.maxnow.cn;
  return 301 https://$host$request_uri;
}

server {
  server_name blog.maxnow.cn;

  root /var/www/maxnow-dashboard/blog;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  listen 443 ssl;
  ssl_certificate /etc/letsencrypt/live/blog.maxnow.cn/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/blog.maxnow.cn/privkey.pem;
  include /etc/letsencrypt/options-ssl-nginx.conf;
  ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

server {
  listen 80;
  server_name blog.maxnow.cn;
  return 301 https://$host$request_uri;
}
EOF

sudo ln -sf /etc/nginx/sites-available/maxnow-dashboard /etc/nginx/sites-enabled/maxnow-dashboard
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl reload nginx || sudo systemctl restart nginx
```

## 更新前端页面

当 `main` 已经在 GitHub 上更新后，在服务器执行：

```bash
cd /var/www/maxnow-dashboard
git pull --ff-only origin main
python3 scripts/check.py
sudo nginx -t
sudo systemctl reload nginx
```

如果出现 Git ownership 保护错误，确认目录归属：

```bash
sudo chown -R ubuntu:www-data /var/www/maxnow-dashboard
```

## 验证命令

服务器本地检查 nginx：

```bash
sudo nginx -t
sudo systemctl status nginx --no-pager
curl -I -H 'Host: dash.maxnow.cn' http://127.0.0.1/
curl -I https://dash.maxnow.cn
curl -I https://blog.maxnow.cn
curl -I https://blog.maxnow.cn/topics.html
```

本地 Windows 检查域名：

```powershell
Invoke-WebRequest -Uri "http://dash.maxnow.cn" -UseBasicParsing
Invoke-WebRequest -Uri "https://blog.maxnow.cn" -UseBasicParsing
```

正常结果应返回 HTTP 200，页面标题为 `MaxNow`。

## 常见问题

### SSH 端口通但连接被关闭

现象：

```text
kex_exchange_identification: Connection closed by remote host
```

排查：

```powershell
Test-NetConnection 43.160.240.244 -Port 22 | Format-List
```

如果 `InterfaceAlias` 是代理 / TUN 网卡，先关闭代理或让 SSH 直连。

服务器侧检查：

```bash
sudo systemctl status ssh --no-pager
sudo journalctl -u ssh -n 100 --no-pager
sudo tail -n 100 /var/log/auth.log
```

### 域名返回 502

可能原因：

- nginx 没有安装或没有运行。
- nginx 配置没有指向 `/var/www/maxnow-dashboard/dash`。
- 域名已解析，但站点配置未启用。

检查：

```bash
sudo nginx -t
sudo systemctl status nginx --no-pager
ls -la /etc/nginx/sites-enabled
ls -la /var/www/maxnow-dashboard
```

## 后续待补

- 给定时同步补失败提醒，或让 Home 更明确展示最近一次自动同步结果。
- 做数据更新工具，让 `dash/data/*.json` 与 `.js` wrapper 自动保持一致。

## Dash 自定义登录运维

当前 nginx 配置与回滚备份：

```text
/etc/nginx/sites-available/maxnow-dashboard
/etc/nginx/sites-available/maxnow-dashboard.bak-20260710-basic-auth
/etc/nginx/sites-available/maxnow-dashboard.bak-20260710-custom-login
/etc/nginx/nginx.conf.bak-20260710-basic-auth
/etc/nginx/snippets/maxnow-security-headers.conf
/etc/nginx/snippets/maxnow-auth-locations.conf
/etc/nginx/conf.d/maxnow-auth-rate-limit.conf
/etc/nginx/.htpasswd-maxnow
/etc/maxnow-auth/session.key
/etc/systemd/system/maxnow-auth.service
```

仓库内可复现配置：

```text
dash/login.html
dash/login.js
scripts/maxnow_auth_service.py
server/maxnow-auth.service
server/maxnow-auth-rate-limit.conf
server/maxnow-auth-locations.conf
server/maxnow-dashboard.conf
```

首次安装或重新部署认证服务：

```bash
sudo install -d -o root -g www-data -m 0750 /etc/maxnow-auth
sudo openssl rand -out /etc/maxnow-auth/session.key 48
sudo chown root:www-data /etc/maxnow-auth/session.key
sudo chmod 640 /etc/maxnow-auth/session.key
sudo install -m 0644 server/maxnow-auth.service /etc/systemd/system/maxnow-auth.service
sudo install -m 0644 server/maxnow-auth-rate-limit.conf /etc/nginx/conf.d/maxnow-auth-rate-limit.conf
sudo install -m 0644 server/maxnow-auth-locations.conf /etc/nginx/snippets/maxnow-auth-locations.conf
sudo install -m 0644 server/maxnow-dashboard.conf /etc/nginx/sites-available/maxnow-dashboard
sudo systemctl daemon-reload
sudo systemctl enable --now maxnow-auth.service
sudo nginx -t && sudo systemctl reload nginx
```

已有 `/etc/maxnow-auth/session.key` 时不要重复执行 `openssl rand`，否则会让所有现有会话立即失效。认证服务每次登录都会重新读取 htpasswd，因此只轮换密码不需要重启服务。

轮换密码时使用交互输入，避免明文进入 history：

```bash
read -rsp "New MaxNow password: " password && echo
hash=$(printf %s "$password" | openssl passwd -6 -stdin)
unset password
echo "<username>:$hash" | sudo tee /etc/nginx/.htpasswd-maxnow >/dev/null
unset hash
sudo chown root:www-data /etc/nginx/.htpasswd-maxnow
sudo chmod 640 /etc/nginx/.htpasswd-maxnow
sudo nginx -t && sudo systemctl reload nginx
```

验证矩阵：

```bash
curl -I https://dash.maxnow.cn/                         # 302 -> /login
curl -I https://dash.maxnow.cn/login                    # 200
curl -I https://dash.maxnow.cn/data/dashboard.json      # 401
curl -I https://blog.maxnow.cn/                         # 200
sudo systemctl is-active maxnow-auth.service            # active
curl -I http://127.0.0.1:8765/health                    # 204
```

完整登录验证时交互输入密码，避免进入 history：

```bash
read -rsp "MaxNow password: " password && echo
curl -sS -c /tmp/maxnow-cookie -o /dev/null -w '%{http_code}\n' \
  -X POST \
  --data-urlencode 'username=maxnow' \
  --data-urlencode "password=$password" \
  --data-urlencode 'next=/' \
  https://dash.maxnow.cn/auth/login                     # 303
unset password
curl -b /tmp/maxnow-cookie -I https://dash.maxnow.cn/   # 200
rm -f /tmp/maxnow-cookie
```

需要强制退出全部设备时，重新生成会话密钥并重启认证服务：

```bash
sudo openssl rand -out /etc/maxnow-auth/session.key 48
sudo chown root:www-data /etc/maxnow-auth/session.key
sudo chmod 640 /etc/maxnow-auth/session.key
sudo systemctl restart maxnow-auth.service
```

需要验证源站无法绕过时，从可信管理机运行：

```bash
curl --resolve dash.maxnow.cn:443:43.160.240.244 -I https://dash.maxnow.cn/data/dashboard.json
```

未认证 `/data/` 仍应返回 401。紧急回滚只能恢复已知备份并先执行 `sudo nginx -t`；不要只保护首页，也不要让 `/data/` 单独公开。若认证服务异常，nginx 必须失败关闭并拒绝 Dash，不能临时绕过 `auth_request`。

2026-07-10 已部署 MaxNow 自定义登录页：

```text
deployed commit: b3451f8 Add MaxNow custom login
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260710-before-custom-login
runtime data stash: before-custom-login-runtime-data
nginx backup: /etc/nginx/sites-available/maxnow-dashboard.bak-20260710-custom-login
service: maxnow-auth.service active；127.0.0.1:8765/health 返回 204
verification: 首页未登录 302 -> /login；登录页 / 样式 / 脚本 200；未登录 auth/check 与 /data/ 401；源站直连 /data/ 401；Blog 200；无 WWW-Authenticate
full flow: 正确密码登录 303；带会话访问首页与 /data/ 均为 200；退出 303；退出后首页恢复 302
```

2026-07-10 已收紧 Token 来源更新时间卡：

```text
deployed commit: b5b2986 Compact Token update card
changes: Token 页头右侧来源更新时间卡收紧为 410px；说明文字移到四行来源时间上方；860px 以下保持单列满宽
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260710-before-token-update-card
runtime data stash: before-token-update-card-runtime-data
verification: 本地 1280px 下右卡宽 410px 且与左卡同顶同底；390px 下单列宽 362px、无横向溢出；线上 styles.css?v=126 返回 200；nginx -t 和认证服务均正常
```

2026-07-10 已修复海淀降雨被显示为阴天：

```text
deployed commit: f6714d8 Use CMA weather for Beijing
changes: 北京天气从 Open-Meteo 默认 Best Match 切换到 CMA / GRAPES；新增 precipitation / rain / showers；有降水但天气码仍为云时按雨或阵雨展示
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260710-before-cma-weather
runtime data stash: before-cma-weather-runtime-data
verification: 默认模型 14:45 返回阴、0mm；CMA 15:00 返回阵雨、1.7mm；服务器 weather 刷新后 code=80、icon=rain、temp=28°C、今日摘要雷阵雨
```

2026-07-30 20:21 使用仓库 `scripts/sync_ballet.py` 的本地归一化、ledger 校验、read model 校验和原子写入函数，手动补入 Owner 确认的 `2026-07-30 18:45–19:45` 李俊大教室软开课。写入前确认目标不存在，并把私有 `attendance-ledger.json` 与公开 `ballet.*` 备份到 `/home/ubuntu/maxnow-deploy-backups/20260730-manual-attendance-UvM4Jf`；记录使用 `manual` 稳定键，公开数据校验为累计 `4 节 / 300 分钟`、本周完成 `2 节 / 150 分钟`、2 条手工记录，课表目标课程可匹配为“已上完”，成长进度为 `4 / 10`。第一次输入因 Windows 管道编码把中文变为问号，校验发现课程类型误判后立即从上述备份完整回滚；随后改用 Unicode 转义重新写入并复验正确，错误记录未保留。全过程未读取 PHPSESSID、未访问闻道、未触发同步，也没有提交预约、排队、取消或转课。

2026-07-30 已部署课表三档高对比色阶与暖色软开课：

```text
deployed commit: d2f9600 Increase ballet timetable color contrast
version: 1.0.7.52
changes: 普通课程保持浅色；排队态改为 24% 基色 + 76% 边框色的中深实心；已预约 / 已上完改为 72% 边框色 + 28% 暖深灰的深色实心并使用暖白文字；软开课由冷灰改为浅奶咖 / 深暖棕
asset cache: styles.css?v=207
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260730-ballet-contrast-warm-UJ4rGq
local visual verification: 2048×1200 与 390×844 下共检查 55 张课程卡；页面和卡片内容均无横向溢出；排队示例文字对比度 7.25，深色已预约 / 已上完示例 5.70
server verification: scripts/check.py 全部通过；scripts/test_sync_ballet.py 18 项通过；nginx -t 通过；首页 302、登录页 200、未认证 ballet 数据 401、styles.css?v=207 200、Blog 200
safety: 仅修改静态样式、契约文档与版本记录；未读取 PHPSESSID、未访问闻道，也未提交预约、排队、取消或转课
```

2026-07-30 已部署训练记录分类与页面顺序调整：

```text
deployed commit: b8f7df7 Refine ballet training breakdowns
version: 1.0.7.53
changes: 无等级课程在展示级别中改用软开 / 肌肉素质 / 技术技巧等真实课型；新增授课老师分布并共用本月 / 今年 / 全部与节数 / 时间切换；本周课程表移到倒数第二，训练记录移到最后
asset cache: styles.css?v=208；app.js?v=169
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260730-210136-ballet-training-breakdowns
runtime data stash: predeploy-ballet-training-breakdowns-20260730-210136（部署后保留，运行时数据已恢复为未暂存改动）
local visual verification: 1585px 宽桌面下三张分布卡同顶、同底、同高且无溢出；375px 实际内容宽下三卡单列、课程表在训练记录之前、页面无横向溢出；节数与时间切换分别验证为 L1 2 节 / 3 小时、软开 2 节 / 2 小时、李俊 3 节 / 3.5 小时、王嘉豪 1 节 / 1.5 小时
server verification: scripts/check.py 全部通过；scripts/test_sync_ballet.py 18 项通过；nginx -t 通过；首页 302、登录页 200、未认证 ballet 数据 401、styles.css?v=208 200、受保护 app.js?v=169 未认证 302、Blog 200；nginx 与 maxnow-auth 均 active
safety: 仅部署静态页面、脱敏聚合和文档；未读取 PHPSESSID、未访问闻道，也未提交预约、排队、取消或转课
```

2026-07-30 已部署暖象牙芭蕾票券课程卡：

```text
deployed commit: ccbc136 Redesign ballet membership card
version: 1.0.7.54
changes: 课程卡升级为暖象牙票券、淡香槟金描边、侧边缺口和低透明芭蕾线稿；课程使用改为动态水平进度，有效天数改为动态环形进度，计划结论收敛为建议周课次、预计用完日期和预计提前天数
asset cache: styles.css?v=209；app.js?v=170
art asset: dash/assets/ballet/membership-ballerina.webp（720×1080 WebP，26,934 bytes；纯装饰，不承载动态文字或数据）
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260730-214043-ballet-membership-ticket
runtime data stash: predeploy-ballet-membership-ticket-20260730-214043（部署后保留，运行时数据已恢复为未暂存改动）
local visual verification: 1585px 与 1265px 实际内容宽下课程卡和本周训练卡同顶、同底、同高；1085px 下概览正常单列；375px 实际内容宽下两项指标改为单列；各尺寸页面与课程卡均无横向溢出，浏览器控制台无 warning / error
server verification: scripts/check.py 全部通过；scripts/test_sync_ballet.py 18 项通过；nginx -t 通过；首页 302、登录页 200、未认证 ballet 数据 401、styles.css?v=209 200、受保护 app.js?v=170 未认证 302、芭蕾插画 200、Blog 200；nginx 与 maxnow-auth 均 active
safety: 仅部署静态页面、脱敏课程卡展示和本地装饰素材；未读取 PHPSESSID、未访问闻道，也未提交预约、排队、取消或转课
```

2026-07-30 已修复芭蕾票券人物被裁切和遮淡：

```text
deployed commit: f1041fa Align membership artwork and responsive checks
version: 1.0.7.55
changes: 插画层移到票券底色之上并改用 contain 完整缩放；宽卡左图右信息且两项指标并排，中等卡宽在舞者右侧纵排指标，手机端将完整人物缩入标题左侧
asset cache: styles.css?v=210；app.js?v=170
art asset: dash/assets/ballet/membership-ballerina.webp（720×1080 WebP，26,934 bytes；从手尖到足尖完整显示）
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260730-215915-membership-artwork
runtime data stash: 0d6b9a5ed088d79e20f04df4a838d45023d738ab（部署后保留，除 project-meta.* 外的服务器运行时数据已按原路径恢复）
local visual verification: 2560×1440 宽卡按参考方向呈现左侧完整舞者与右侧双指标；2048×1200、1600×1000、1280×900 中等卡宽显示完整舞者并在右侧纵排指标；390×844 将完整舞者缩入标题左侧；桌面概览卡同顶、同底、等高，全部尺寸无横向溢出且浏览器控制台无 warning / error
server verification: 61 项芭蕾测试和 scripts/check.py 全部通过；nginx -t 通过；首页 302、登录页 200、未认证 ballet 数据 401、styles.css?v=210 200、芭蕾插画 200、Blog 200；nginx、maxnow-auth 与三个芭蕾 timer 均 active，rolling / full / 自动抢课 service 均 inactive
safety: 仅部署静态样式、响应式契约和文档；未读取 PHPSESSID、未访问闻道，也未触发同步、预约、候补、取消或转课
```

2026-07-30 已取消课程卡外层面板并扩展票券内容：

```text
deployed commit: a78bff3 Simplify ballet membership ticket
version: 1.0.7.56
changes: 删除课程卡外围普通白色 panel；Course Card / 课程卡 / 有效卡数量并入暖象牙票券顶部；删除左右半圆缺口；事实区向左扩展；手机端重置事实区偏移，修复 20px 横向溢出
asset cache: styles.css?v=211；app.js?v=171
runtime data backup: /var/backups/maxnow-dashboard-predeploy-a78bff3-20260730-2215.tgz（部署前完整备份 dash/data）
local visual verification: 2048×1200、1600×1000、1280×900、390×844 下均无整页横向溢出；2048px / 1600px 三个概览格同顶、同底、同高；课程卡内部无内容溢出、半圆缺口节点为 0、浏览器控制台无 warning / error
server verification: 61 项芭蕾测试和 scripts/check.py 全部通过；nginx -t 通过；首页 302、登录页 200、未认证 ballet 数据 401、styles.css?v=211 200、受保护 app.js?v=171 未认证 302、芭蕾插画 200、Blog 200；nginx 与 rolling / full / Session 状态 / 自动抢课 timer 均 active
safety: 仅部署静态页面、脱敏课程卡展示和文档；未读取 PHPSESSID、未访问闻道，也未触发同步、预约、候补、取消或转课
```

2026-07-30 已修正课程票券色差、插画、圆环和内框：

```text
deployed commit: 53ee68f Polish ballet membership ticket
version: 1.0.7.57
changes: 票券底色改为与插画纸色一致的 #fefaf4 并取消图片混合模式；宽卡遮罩延后到横向脚尖之后；有效卡标签改为玫瑰金；圆环两行数字改为 flex 纵向居中；删除顶部内分隔线和右侧票根虚线
asset cache: styles.css?v=212；app.js?v=172
runtime data backup: /var/backups/maxnow-dashboard-predeploy-53ee68f-20260730-2300.tgz（部署前完整备份 dash/data）
local visual verification: 3840×1400、2048×1200、1600×1000、390×844 均无整页或课程卡内容溢出；2048px / 1600px 三个概览格同顶同底等高；圆环当前天数与总天数保持 1px 间隔；内框线节点为 0；控制台无 warning / error
server verification: 61 项芭蕾测试和 scripts/check.py 全部通过；nginx -t 通过；首页 302、登录页 200、未认证 ballet 数据 401、styles.css?v=212 200、受保护 app.js?v=172 未认证 302、芭蕾插画 200、Blog 200；nginx、maxnow-auth 与四个芭蕾 timer 均 active
safety: 仅部署静态页面、脱敏课程卡展示和文档；未读取 PHPSESSID、未访问闻道，也未触发同步、预约、候补、取消或转课
```

2026-07-30 已分离课程票券舞者与事实区并缩小圆环数字：

```text
deployed commit: a7ac5bd Separate membership artwork and facts
version: 1.0.7.58
changes: 330px 以上课程票券取消舞者右侧遮罩，改为互不重叠的左右物理分区；中等卡使用 44% 舞者宽度与 45% 事实区起点，宽卡使用 40% 舞者宽度与 42% 事实区起点，标题、日期和指标从横向脚尖之后开始；有效天数圆环当前天数从 24px 缩至 18px，总天数为 9px
asset cache: styles.css?v=213；app.js?v=172
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260730-membership-foot-ring-a7ac5bd/dash-data.tgz（部署前完整备份 dash/data）
local visual verification: 3840×1400 宽卡的舞者区域与事实区保持 25.89px 正向间距；2048×1200 与 1600×1000 三个概览格同顶、同底、等高，事实区与舞者区分别保持 7.35px / 5.95px 间距；390×844 无整页横向溢出；圆环数字为 18px / 9px 并保持 1px 纵向间距
server verification: 61 项芭蕾测试和 scripts/check.py 全部通过；nginx -t 通过；首页 302、登录页 200、未认证 ballet 数据 401、styles.css?v=213 200、受保护 app.js?v=172 未认证 302、芭蕾插画 200、Blog 200；nginx、maxnow-auth 与四个芭蕾 timer 均 active，rolling / full / 自动抢课 service 均 inactive
safety: 仅部署静态页面、脱敏课程卡展示和文档；未读取 PHPSESSID、未访问闻道，也未触发同步、预约、候补、取消或转课
```

2026-07-30 已拆开课程票券有效进度文字与圆环：

```text
deployed commit: e860e36 Separate membership progress ring layout
version: 1.0.7.59
changes: 有效进度卡改为三行网格，首行仅放标签和右上 50px 小圆环，主比例与到期说明分别独占后两行；圆环内当前天数从 18px 缩至 15px，总天数从 9px 缩至 8px
asset cache: styles.css?v=214；app.js?v=172
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260730-membership-ring-layout-e860e36/dash-data.tgz（部署前完整备份 dash/data）
local visual verification: 3840×1400、2048×1200、1600×1000、390×844 下主比例位于圆环下方并保持至少 8px 间距；到期说明均保持单行；卡内和整页横向溢出为 0；2048px / 1600px 三个概览格同顶、同底、同高
server verification: 61 项芭蕾测试和 scripts/check.py 全部通过；nginx -t 通过；首页 302、登录页 200、未认证 ballet 数据 401、styles.css?v=214 200、Blog 200；nginx、maxnow-auth 与四个芭蕾 timer 均 active，rolling / full / 自动抢课 service 均 inactive
safety: 仅部署静态页面、脱敏课程卡展示和文档；未读取 PHPSESSID、未访问闻道，也未触发同步、预约、候补、取消或转课
```

2026-07-30 已放大课程票券有效期圆环并收小正文：

```text
deployed commit: 7623f43 Rebalance membership progress scale
version: 1.0.7.60
changes: 有效期圆环从 50px 放大至 66px，环内数字继续保持 15px / 8px；正文主数字从最高 38px 收至最高 30px，前后文字为 12px，到期说明为 10px
asset cache: styles.css?v=215；app.js?v=172
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260730-membership-ring-scale-7623f43/dash-data.tgz（部署前完整备份 dash/data）
local visual verification: 3840×1400、2048×1200、1600×1000、390×844 下圆环与标签保持 8–10px 间距，正文位于圆环下方；卡内和整页横向溢出为 0；2048px / 1600px 三个概览格同顶、同底、同高
server verification: 61 项芭蕾测试和 scripts/check.py 全部通过；nginx -t 通过；styles.css?v=215 200、首页 302、登录页 200、未认证 ballet 数据 401、Blog 200；nginx、maxnow-auth 与四个芭蕾 timer 均 active，rolling / full / 自动抢课 service 均 inactive
safety: 仅部署静态页面、脱敏课程卡展示和文档；未读取 PHPSESSID、未访问闻道，也未触发同步、预约、候补、取消或转课
```

2026-07-30 已将课程票券圆环比例改为单行：

```text
deployed commit: d913c74 Align membership ring ratio inline
version: 1.0.7.61
changes: 圆环内当前天数与总天数从上下两行改为单行横排 N /总天数；两段间距 2px，总天数下移 1px 做光学对齐
asset cache: styles.css?v=216；app.js?v=172
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260730-membership-ring-inline-d913c74/dash-data.tgz（部署前完整备份 dash/data）
local visual verification: 2048×1200、1600×1000、390×844 下当前天数与总天数保持同一行，两段中心高度差不超过 1px，组合中心与圆心误差小于 0.01px；卡内和整页横向溢出为 0
server verification: 61 项芭蕾测试和 scripts/check.py 全部通过；nginx -t 通过；styles.css?v=216 200、首页 302、登录页 200、未认证 ballet 数据 401、Blog 200
safety: 仅部署静态页面、脱敏课程卡展示和文档；未读取 PHPSESSID、未访问闻道，也未触发同步、预约、候补、取消或转课
```

2026-07-31 已部署周日自动抢课五节目标：

```text
deployed commit: 417c83c Update Sunday ballet booking targets
version: 1.0.7.62
changes: 自动抢课目标替换为周五李俊软开、周五王嘉豪 L1、周二王嘉豪软开、周二王嘉豪 L1、周四李俊软开，均为大教室晚间课；当前实际顺序为周五两节、周二两节、周四一节
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260731-ballet-booking-targets-417c83c（完整 dash/data、变更前配置、私有状态与公开状态）
runtime data stash: predeploy-ballet-booking-targets-20260731（部署后保留；除 project-meta.* 与自动抢课 fallback 外的服务器运行数据已恢复）
live verification: 2026-07-31 21:48 北京时间通过 wenda-live 只读核对截图周二 / 周四 / 周五五节的时间、老师和教室；8 月 4–7 日下周目标课当时尚未发布
server verification: scripts/check.py 全部通过；nginx -t 通过；安全 preview 发布 8 月 2 日 14:20 计划且 totalRuns / totalBooked 仍为 0；timer enabled / active / waiting，service inactive，LastTriggerUSec 为空；首页 / 登录页 / 未认证自动抢课状态 / Blog 为 302 / 200 / 401 / 200
safety: 仅执行闻道课表 GET 与本地无网络 preview；未手动启动自动抢课 service，未提交预约、候补、取消或转课
```

2026-07-31 已部署精确目标自动候补：

```text
deployed commit: ab6d02d feat: auto-waitlist configured ballet targets
version: 1.0.8.00
changes: 五个固定目标命中 available 时预约、命中 queue_available 时候补；已预约 / 已排队不重复提交，统一实时核验区分 booked / waitlist 并保留安全候补位次；Cloud 分开展示累计预约与候补
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260731-auto-waitlist-ab6d02d（完整 dash/data、变更前配置、自动抢课私有状态与公开状态）
runtime data stash: predeploy-auto-waitlist-20260731（部署后保留；服务器运行数据已恢复，project-meta.* 已按新版本重新生成）
local verification: 11 项 fast-path fixture 测试与 scripts/check.py 全部通过；1600×900 和 390×844 下 Cloud 卡、三项指标与“0 约 · 0 候”无卡内或整页横向溢出
server verification: 11 项 fast-path fixture 测试、scripts/check.py 与 nginx -t 全部通过；无网络 preview 发布 waitlistEnabled=true、五个目标与 8 月 2 日 14:20 计划，totalRuns / totalBooked / totalWaitlisted 均为 0；私有状态 0600、公开状态 root:www-data 0640；timer enabled / active / waiting，service inactive，LastTriggerUSec 为空；首页 / 登录页 / 未认证自动抢课状态 / Blog 为 302 / 200 / 401 / 200
safety: 未手动运行 execute、未启动自动抢课 service、未读取凭据、未访问闻道；部署与验收没有提交预约、候补、取消或转课，真实 mutation 仍只允许由周日 timer 处理精确配置目标
```

2026-08-02 已部署课程优先与并发预检 Fast Path：

```text
deployed commit: 3f97fa7 Speed up ballet booking fast path
version: 1.0.8.08
changes: 一级优先级改为芭蕾 L1 > 软开，二级按同课程日期周六 > 周日 > 周五 > 其他日期；课表最多 3 路并发且同日共享，卡 / 规则最多 2 路并发预检并设 8 秒有效期，HTTPS 最多 3 条 keep-alive，最终详情最多 3 路并发只读核验；真实 mutation 严格串行
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-145710-booking-fast-pipeline（完整 dash/data、自动抢课私有状态与公开状态）
runtime data stash: predeploy-booking-fast-pipeline-20260802-145710（部署后保留；服务器权威运行数据已恢复，project-meta.* / project-status.* 与自动抢课公开状态按新版本重新生成）
local verification: 22 项预约测试与 scripts/check.py 全部通过；1600px 下自动抢课 / Session 双卡同顶同底等高，390px 下正常单列，长优先级文案和整页均无横向溢出
server verification: 22 项预约测试、scripts/check.py、systemd-analyze verify 与 nginx -t 全部通过；无网络 preview 保留 totalRuns=1 / totalBooked=4 / totalWaitlisted=1 / lastStatus=success，发布下一次 2026-08-09 14:20 计划和新顺序；私有状态 root:www-data 0600、公开状态 root:www-data 0640；timer enabled / active，下次 14:19:35，service inactive；未认证状态接口 401
safety: 部署与验收只运行无网络 preview；未手动运行 execute、未启动自动抢课 service、未读取凭据、未访问闻道，也没有提交预约、候补、取消或转课
```

2026-08-02 已部署芭蕾课程预约 / 抢课双工作区：

```text
deployed commit: 6acd378 feat: split ballet booking workspace into tabs
version: 1.0.8.09
changes: 课程计划左侧改为课程预约；右侧抢课新增累计已抢到、当前已预约、上次平均耗时两张摘要卡，以及代抢 / 上次抢课结果两个互斥 Tab；上次结果直接读取执行记录自身课程日期
asset cache: styles.css?v=219；app.js?v=180
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-151842-ballet-booking-tabs/dash-data.tgz
runtime data stash: e4c69791b53d727bd3e62152a91267e0f7204602（部署后保留；服务器权威运行数据已恢复，project-meta.* / project-status.* 按新版本重新生成）
local visual verification: 1600×1000 下课程预约 / 抢课两栏同顶同底，双摘要卡同高；390×844 下课程区与摘要卡单列、两个内容 Tab 仍并排，课程行与整页无横向溢出；Tab 切换、空结果与控制台均正常
server verification: scripts/check.py 与 nginx -t 全部通过；未登录 Dash / 登录页 / 自动抢课状态 / styles.css?v=219 / Blog 为 302 / 200 / 401 / 200 / 200；nginx 与 maxnow-auth active，自动抢课 timer enabled / active、下次 2026-08-09 14:19:35，service inactive
safety: 仅部署静态页面、脱敏状态展示和文档；未运行 preview / execute、未启动自动抢课 service、未读取凭据、未访问闻道，也未提交预约、候补、取消或转课
```

2026-08-02 已部署紧凑版本月训练热力图：

```text
deployed commit: 28d21cf fix: compact ballet training heatmap
version: 1.0.8.10
changes: 热力图外框在桌面收敛为最大 840px 并左对齐，格子高度、间距和内边距同步压缩；未纳入同步的日期改为低对比浅底虚线格并隐藏重复破折号，手机端仍占满可用宽度
asset cache: styles.css?v=220；app.js?v=180
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-152810-ballet-heatmap-compact
runtime data stash: ea2ea3ebf81d57c879a20c1e42915a4f19fef022（部署后保留；服务器权威运行数据已恢复，project-meta.* / project-status.* 按新版本重新生成）
local visual verification: 1600×1000 下热力图外框宽 840px、内部无多余横向空白，训练趋势卡仍为 1234px；390×844 下图表宽 301px、七列网格宽 280px，图表、格子和整页均无横向溢出；控制台无错误或警告
server verification: scripts/check.py 与 nginx -t 全部通过；未登录 Dash / 登录页 / styles.css?v=220 / Blog 为 302 / 200 / 200 / 200；自动抢课 timer enabled / active、下次 2026-08-09 14:19:35，service inactive
safety: 仅部署静态样式和文档；未运行 preview / execute、未启动自动抢课 service、未读取凭据、未访问闻道，也未提交预约、候补、取消、转课或课程同步
```

2026-08-02 已部署三等分抢课摘要与总耗时口径：

```text
deployed commit: 836b339 feat: clarify ballet booking metrics
version: 1.0.8.11
changes: 抢课摘要改为累计抢到 / 当前已预约 / 上次抢课耗时三张等宽卡；上次耗时优先显示 criticalPathMilliseconds 总耗时，66,107 ms 展示为 66.1 s，并补充 5 个目标、平均 13.2 s/节；结果行课程名使用稳定日期列比例统一左边缘
asset cache: styles.css?v=221；app.js?v=181
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-155324-ballet-booking-metrics-tabs/dash-data.tgz
runtime data stash: cefee324d51da19945517481461fa34fe751eafd（部署后保留；服务器权威运行数据已恢复，project-meta.* / project-status.* 按新版本重新生成）
local visual verification: 1600×1000 下三张摘要卡同顶、同底、等宽、等高，五条结果课程名横坐标一致，状态徽标右边缘一致；390×844 下仍为三等分且卡片、摘要区和整页横向溢出均为 0
server verification: scripts/check.py 与 nginx -t 全部通过；权威公开状态保留 totalBooked=4 / totalWaitlisted=1 / criticalPathMilliseconds=66107 / 5 records；未登录 Dash / 登录页 / 自动抢课状态 / styles.css?v=221 / app.js?v=181 / Blog 为 302 / 200 / 401 / 200 / 302 / 200；nginx 与 maxnow-auth active，自动抢课 timer active、下次 2026-08-09 14:19:35，service inactive
safety: 仅部署静态页面、脱敏状态展示和文档；未运行 preview / execute、未启动自动抢课 service、未读取凭据、未访问闻道，也未提交预约、候补、取消、转课或课程同步
```

2026-08-02 已部署课表紧凑卡老师姓名保留修复：

```text
deployed commit: 107b0b8 fix: keep timetable teachers visible
version: 1.0.8.12
changes: 课程卡顺序调整为课程名 / 老师 / 人数与排队 / 时间与状态；移除 1101px–1500px 和重叠窄卡隐藏老师的规则；60 分钟卡的人数与底部事实分别固定单行，空间不足只压缩次级人数文字
asset cache: styles.css?v=222；app.js?v=182
deployment path: 主分支推送后服务器已自动更新到相同提交；服务器原有 dash/data 运行时改动保持存在，本次未手动 stash、覆盖或刷新课表数据
local visual verification: 2048px 下 60 分钟已预约软开卡同时显示王嘉豪、15/12 人、排队 4、19:00–20:00 和已预约且卡内无溢出；1280px 老师行继续显示；390px 下 23 张紧凑卡老师全部可见，整页横向溢出为 0
server verification: 20 项芭蕾测试、scripts/check.py 与 nginx -t 全部通过；未登录 Dash / 登录页 / 芭蕾数据 / styles.css?v=222 / app.js?v=182 / Blog 为 302 / 200 / 401 / 200 / 302 / 200；课程同步和自动抢课 service inactive，自动抢课 timer active
safety: 仅部署静态页面、样式、脱敏展示逻辑和文档；未访问闻道、未运行课程同步、未启动自动抢课 service，也未提交预约、候补、取消或转课
```

2026-08-02 已部署训练趋势与上课历史同高并排布局：

```text
deployed commit: d8ed019 feat: compact ballet history beside training chart
version: 1.0.8.17
changes: 桌面训练详情改为左侧图表决定行高、右侧紧凑历史绝对铺满同高区域；主页面最近 5 节、手机最近 3 节，完整当前范围历史进入右侧独立滚动抽屉；本月 / 今年 / 全部同步筛选历史和总数
asset cache: styles.css?v=226；app.js?v=187
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-171930-training-history-drawer/dash-data.tgz
runtime data stash: 3643f3bd5b848cf7890be7a884512d3cb3aa5d21（部署后保留；服务器权威运行数据已恢复，project-meta.* 按新版本重新生成）
local visual verification: 1440px 下图表 / 历史同顶同底且均高 386px，向预览临时追加到 44 条后整行仍为 386px；1000px 下上下排列；390px 下只显示最近 3 条、抽屉占满可用宽度，整页无横向溢出；抽屉 Esc 关闭后焦点返回入口
server verification: 20 项芭蕾测试、scripts/check.py 与 nginx -t 全部通过；线上并排详情、历史抽屉与最多 5 条预览标记存在；未登录 Dash / 登录页 / 芭蕾数据 / styles.css?v=226 / Blog 为 302 / 200 / 401 / 200 / 200；nginx 与 maxnow-auth active，课程同步与自动抢课 service inactive，自动抢课 timer active、下次 2026-08-09 14:19:35
safety: 仅部署静态页面、样式、脱敏展示逻辑和文档；未访问闻道、未运行课程同步、未启动自动抢课 service，也未提交预约、候补、取消或转课
```

2026-08-02 已部署今年 / 全部训练折线图紧凑宽度：

```text
deployed commit: 9174284 fix: compact ballet trend charts
version: 1.0.8.13
changes: 今年折线按 8 个已显示月份收敛为 776px；全部只有 1 个年份时收敛为 420px；两者均左对齐、最大 840px，手机端占满可用宽度
asset cache: styles.css?v=223；app.js?v=183
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-162356-ballet-trend-compact/dash-data.tgz
local visual verification: 2048px 下本月 / 今年 / 全部图表宽度分别为 840px / 776px / 420px，均左对齐且整页横向溢出为 0；390px 下三种图表均为可用宽度 301px，图表与整页横向溢出均为 0
server verification: 20 项芭蕾测试、scripts/check.py 与 nginx -t 全部通过；未登录 Dash / 登录页 / 芭蕾数据 / styles.css?v=223 / Blog 为 302 / 200 / 401 / 200 / 200；课程同步与自动抢课 service 均 inactive，自动抢课 timer active、下次 2026-08-09 14:19:35
safety: 仅部署静态页面、样式、脱敏展示逻辑和文档；未访问闻道、未运行课程同步、未启动自动抢课 service，也未提交预约、候补、取消或转课
```

2026-08-02 已部署抢课摘要累计候补口径修复：

```text
deployed commit: 11ad94b fix: show cumulative ballet waitlist total
version: 1.0.8.14
changes: 抢课中间摘要卡从当前未来预约 / 候补列表数量改为自动抢课累计 totalWaitlisted；线上显示累计抢到 4 节、累计候补 1 节
asset cache: styles.css?v=223；app.js?v=184
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-163704-ballet-waitlist-summary/dash-data.tgz
local visual verification: 2048px 与 390px 下“累计抢到 / 累计候补 / 上次抢课耗时”三张摘要卡同顶同底等宽，摘要区与整页横向溢出均为 0
server verification: 17 项自动抢课测试、20 项芭蕾测试、scripts/check.py 与 nginx -t 全部通过；权威脱敏状态 totalBooked=4 / totalWaitlisted=1；未登录 Dash / 登录页 / 自动抢课状态 / Blog 为 302 / 200 / 401 / 200；课程同步与自动抢课 service inactive，自动抢课 timer active、下次 2026-08-09 14:19:35
safety: 仅部署静态页面、脱敏状态展示和文档；未访问闻道、未运行课程同步、未启动自动抢课 service，也未提交预约、候补、取消或转课
```

2026-08-02 已部署代抢与上次结果并列展示：

```text
deployed commit: 9dfe541 feat: show ballet booking results side by side
version: 1.0.8.15
changes: 移除“代抢 / 上次抢课结果”点击切换与隐藏面板，改为两个始终同时渲染的独立列表；容器可容纳时左右等分并列，空间不足时自然上下排列，两列各自保留标题与数量且不设置内部滚动
asset cache: styles.css?v=224；app.js?v=185
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-165136-ballet-booking-parallel/dash-data.tgz
local visual verification: 1280px 视口下抢课卡可用宽度约 425px，两组列表自动上下排列并同时可见，Tab 按钮数量和组件 / 整页横向溢出均为 0；自适应网格在容器可容纳两个 360px 最小列时切换为左右等分
server verification: 17 项自动抢课测试、20 项芭蕾测试、scripts/check.py 与 nginx -t 全部通过；线上新双列表结构存在、旧 Tab 状态与事件逻辑不存在，权威脱敏状态保留 totalBooked=4 / totalWaitlisted=1 / 5 records / criticalPathMilliseconds=66107；未登录 Dash / 登录页 / 自动抢课状态 / styles.css?v=224 / app.js?v=185 / Blog 为 302 / 200 / 401 / 200 / 302 / 200；nginx 与 maxnow-auth active，课程同步与自动抢课 service inactive，自动抢课 timer active、下次 2026-08-09 14:19:35
safety: 仅部署静态页面、样式、脱敏展示逻辑和文档；未访问闻道、未运行课程同步、未启动自动抢课 service，也未提交预约、候补、取消或转课
```

2026-08-02 已部署课表紧凑卡完整时间修复：

```text
deployed commit: 406f766 fix: keep timetable times visible
version: 1.0.8.16
changes: 60 分钟课程起止时间改为不可收缩事实并禁止省略号；宽桌面完整时间与状态同排，1101px–1500px 窄卡把状态放到完整时间下一行，老师姓名继续保留，人数 / 排队仍为优先压缩项
asset cache: styles.css?v=225；app.js?v=186
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-170334-timetable-time-visible/dash-data.tgz
local visual verification: 1280px 下 23 张 60 分钟紧凑卡全部得到完整 HH:MM–HH:MM 时间；最窄卡约 57px，时间与状态均在卡片边界内，老师缺失 0 条，卡片与整页横向溢出均为 0；已预约软开明确显示 19:00–20:00
server verification: 20 项芭蕾测试、scripts/check.py 与 nginx -t 全部通过；线上时间标记与 text-overflow: clip 规则存在，macOS 用量 17:00 自动更新同时保留；未登录 Dash / 登录页 / 芭蕾数据 / styles.css?v=225 / app.js?v=186 / Blog 为 302 / 200 / 401 / 200 / 302 / 200；nginx 与 maxnow-auth active，课程同步与自动抢课 service inactive，自动抢课 timer active、下次 2026-08-09 14:19:35
safety: 仅部署静态页面、样式、脱敏展示逻辑和文档；未访问闻道、未运行课程同步、未启动自动抢课 service，也未提交预约、候补、取消或转课
```

2026-08-02 已部署抢课双 Tab 面板边界：

```text
deployed commit: 3f60fe5 style: frame ballet booking tabs
version: 1.0.8.18
changes: “代抢”和“上次抢课结果”改为两个始终同时展示、各自带完整外框的 Tab 面板；“代抢”固定作为左侧标题，宽时等分同高并排，窄时自然上下排列
asset cache: styles.css?v=227；app.js?v=187
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-173434-booking-tab-panels/dash-data.tgz
runtime data stash: 4621479660ff13b53e4c2bea9a996c6dd8ff5aa0（部署后保留；服务器权威运行数据已恢复，project-meta.* 按新版本重新生成）
local visual verification: 2048px 下双面板同顶同底、各占一半且高度均为 567px；1000px 与 390px 下上下排列并同时可见，页面横向溢出为 0，控制台无错误或警告
server verification: 20 项芭蕾测试、scripts/check.py 与 nginx -t 全部通过；线上双面板与 styles.css?v=227 标记存在；未登录 Dash / 登录页 / 芭蕾数据 / styles.css?v=227 为 302 / 200 / 401 / 200；课程同步、完整同步和自动抢课 service 均 inactive，三个 timer 均 active，自动抢课下次 2026-08-09 14:19:35
safety: 仅部署静态页面、样式和文档；未访问闻道、未运行课程同步、未启动自动抢课 service，也未提交预约、候补、取消或转课
```

2026-08-02 已部署训练历史两列条件预览：

```text
deployed commit: 33c7912 fix: compact ballet history preview
version: 1.0.8.19
changes: 1501px 以上图表轨道按热力图 / 折线实际宽度收敛，历史紧接右侧；删除重复“节 / h”单位徽标；历史桌面两列最多 8 条、手机单列最多 3 条，只有超量时显示“查看更多”
asset cache: styles.css?v=229；app.js?v=188
runtime data backup: /home/ubuntu/maxnow-deploy-backups/20260802-175003-history-grid/dash-data.tgz；并额外保留 post-fast-forward-data.tgz
runtime data stashes: 0b31102e8361af6002ea58f831e79a93b0f376b9（部署前完整数据）；1a9de77bd65730ff82ce97f0e2eeec7e124c0bc7（部署中途定时刷新数据）
runtime recovery: 首次恢复数据时撞上 Dashboard / 行情 / Ricky 定时刷新并安全停止；随后应用部署前完整 stash，再从中途 stash 精确恢复较新的 dashboard.*、market-indices.*、ricky.*，project-meta.* 按新版本重新生成
local visual verification: 2048px 下热力图宽 840px、历史紧邻且占满剩余 799px，中间仅保留 16px 正常间距；4 条历史为两行两列且不显示入口；390px 下 4 条记录只预览 3 条并显示“查看更多”；1500px 上下排列，全部场景横向溢出为 0且控制台无错误
server verification: 20 项芭蕾测试、scripts/check.py 与 nginx -t 全部通过；未登录 Dash / 登录页 / 芭蕾数据 / styles.css?v=229 / app.js?v=188 为 302 / 200 / 401 / 200 / 302；课程同步、完整同步和自动抢课 service 均 inactive，三个 timer 均 active
safety: 仅部署静态页面、脱敏展示逻辑和文档；未访问闻道、未运行课程同步、未启动自动抢课 service，也未提交预约、候补、取消或转课
```

2026-08-02 已部署课表当前时间标签防遮挡修复：

```text
deployed source commit: 28e1d1f fix: keep timetable now label clear
version: 1.0.8.20
changes: 当前时间数字改为最左侧时间轴第 1 列的独立网格项；玫瑰色横线只跨第 2 列至末列，课程卡与时间标签在结构上不再共用网格列
asset cache: styles.css?v=230；app.js?v=189
deployment path: 推送远端 main 后服务器自动更新到相同提交；服务器 dash/data 权威运行数据保持存在，本次未手动覆盖或刷新课程数据
local visual verification: 2048px 与 1280px 下标签 / 横线分别从第 1 / 第 2 网格列开始，间距均为 7px；时间标签与全部课程卡交集数量为 0，课表与整页横向溢出均为 0
server verification: 20 项芭蕾测试、scripts/check.py 与 nginx -t 全部通过；未登录首页 / 芭蕾数据为 302 / 401；nginx 与 maxnow-auth active，课程同步、完整同步和自动抢课 service 均 inactive，三个 timer 均 active
safety: 仅部署静态页面、样式、脱敏展示逻辑和文档；未访问闻道、未运行课程同步、未启动自动抢课 service，也未提交预约、候补、取消或转课
```
