# 芭蕾周记录封面模板

页面运行时读取 `template.json`，把 `template-v1.png` 与 `digits/` 中的透明手绘数字在浏览器本地拼成 `1280×1710` PNG。底图已经固定“芭蕾周记录”和小写 `week`，运行时只替换右侧周数。

## 更换底图

1. 新底图必须是没有周数数字的 `1280×1710` PNG，并保留数字区域的自然底纹。
2. 使用新文件名，例如 `template-v2.png`，不要覆盖旧文件名。
3. 在 `template.json` 中同步修改 `templateVersion` 与 `templateFile`；如数字位置变化，再调整 `numberCenterX`、`numberBaselineY` 和 `digitScale`。
4. 页面每次打开封面时都会重新检查 `template.json`；版本未变化且仍是同一周时复用当前页面缓存，版本变化后立即重新合成。

周数以北京时间计算：`2026-07-27` 至 `2026-08-02` 为 `week 2`，每周一进入下一周。无需服务器定时任务，也不会保存或逐周删除服务器成品图。
