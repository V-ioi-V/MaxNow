# 芭蕾周记录封面模板

页面运行时读取 `template.json`，提供两张可左右滑动的 `1280×1710` PNG：

- `template-v1.png` 与 `digits/` 中的透明手绘数字拼成 `week N` 封面；底图固定“芭蕾周记录”和小写 `week`，运行时只替换右侧周数。
- `brief-template-v1.png` 固定标题、六个指标名称与全部布艺装饰；运行时只填周数、日期、本周训练次数 / 时长 / 最爱课程和截至该周的总次数 / 总时长 / 最爱课程。

周简报动态字统一使用项目内置的 `dash/assets/fonts/ma-shan-zheng/MaShanZheng-Regular.ttf`，不依赖访问设备安装的字体。字体来自 Google Fonts，许可固定保存在同目录 `OFL.txt`。

## 更换底图

1. 新底图必须是没有周数数字的 `1280×1710` PNG，并保留数字区域的自然底纹。
2. 使用新文件名，例如 `template-v2.png`，不要覆盖旧文件名。
3. 在 `template.json` 中同步修改 `templateVersion` 与 `templateFile`；如数字位置变化，再调整 `numberCenterX`、`numberBaselineY` 和 `digitScale`。
4. 页面每次打开封面时都会重新检查 `template.json`；版本未变化且仍是同一周时复用当前页面缓存，版本变化后立即重新合成。

周简报底图升级时使用新的 `brief-template-vN.png` 文件名，并同步提升 `briefTemplateVersion`；动态字坐标由 `briefWeekNumber*`、`briefDate*`、`briefColumnCenters` 和两组 `brief*ValueBaselineY` 配置控制。

周数以北京时间计算：`2026-07-27` 至 `2026-08-02` 为 `week 2`，每周一进入下一周。周简报固定取最近一个已经到达的周日 `20:00` 截止点；生产 rolling timer 在该时刻额外刷新一次脱敏芭蕾数据，浏览器再复用训练概览口径合成图片。服务器不保存 PNG 成品，也不会接收浏览器生成的图片。
