# 芭蕾周记录封面模板

页面运行时读取 `template.json`，提供两张可左右滑动并最终导出为 `1280×1710` PNG 的图片：

- 浏览器加载轻量 `template-v1.webp`，与 `digits/` 中的透明手绘数字拼成 `week N` 封面；同名 PNG 是高质量源底图，不直接下发。
- 浏览器加载轻量 `brief-template-v1.webp`；同名 PNG 源底图固定标题、六个指标名称与全部布艺装饰，运行时只填周数、日期、本周训练次数 / 时长 / 最爱课程和截至该周的总次数 / 总时长 / 最爱课程。

周简报动态字统一使用项目内置的 `dash/assets/fonts/zhi-mang-xing/ZhiMangXing-Weekly.woff2`。`Zhi Mang Xing` 的笔画更松、更长，毛笔感更接近固定底图里的“芭蕾周记录”；网页子集不依赖访问设备安装字体，完整 TTF、子集字符清单和 `OFL.txt` 作为源文件与许可保留。后续周简报继续复用这一字体，不随周数或课程数据更换。

## 更换底图

1. 新底图必须是没有周数数字的 `1280×1710` PNG，并保留数字区域的自然底纹；发布前另生成同名 WebP 供浏览器加载。
2. 使用新文件名，例如 `template-v2.png`，不要覆盖旧文件名。
3. 在 `template.json` 中同步修改 `templateVersion` 与 `templateFile`；如数字位置变化，再调整 `numberCenterX`、`numberBaselineY` 和 `digitScale`。
4. 页面每次打开封面时都会重新检查 `template.json`；版本未变化且仍是同一周时复用当前页面缓存，版本变化后立即重新合成。

周简报底图升级时保留新的 `brief-template-vN.png` 源文件，生成 `brief-template-vN.webp` 并让 `briefTemplateFile` 指向 WebP，同时提升 `briefTemplateVersion`；动态字坐标由 `briefWeekNumber*`、`briefDate*`、`briefColumnCenters` 和两组 `brief*ValueBaselineY` 配置控制。页眉日期固定使用 `MM.DD–MM.DD` 纯数字格式；动态周数的基线需与底图“第 / 周”视觉对齐。

进入芭蕾页时只空闲预生成默认封面；周简报等 Owner 切换到该页时才生成。不得同时下载两张底图和完整字体，避免较慢网络一直停在空白画布。

周数以北京时间计算：`2026-07-27` 至 `2026-08-02` 为 `week 2`，每周一进入下一周。周简报固定取最近一个已经到达的周日 `20:00` 截止点；生产 rolling timer 在该时刻额外刷新一次脱敏芭蕾数据，浏览器再复用训练概览口径合成图片。服务器不保存 PNG 成品，也不会接收浏览器生成的图片。
