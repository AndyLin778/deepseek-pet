# Codex 双形态桌宠

`normal/` 和 `pot/` 是两个可选的 Codex v2 宠物包。它们分别保留拼豆图中的普通形态和铁锅形态。Codex 宠物选择器中切换两项即可换形态；独立桌宠的双击切换在仓库的 `dual-form-pet/` 项目中。

每包包含 `pet.json`、1536×2288 的 `spritesheet.webp`、PNG 源图、动画 GIF 预览和验证报告。帧采用原拼豆图逐格采样后制作，不改变角色的主要像素造型。

两包都已通过 `validate_atlas.py --require-v2` 的结构与透明度检查。动画以整体弹跳、位移、眨眼和局部像素动作实现；指针方向的头部动作较轻微，尚未经过技能要求的独立盲测，因此不能声称通过完整视觉 QA。

安装时将 `normal/pet.json`、`normal/spritesheet.webp` 复制到 `%USERPROFILE%\.codex\pets\lanlan-normal`；将 `pot/pet.json`、`pot/spritesheet.webp` 复制到 `%USERPROFILE%\.codex\pets\lanlan-pot`。重启 Codex 后在宠物列表中选择形态。

在仓库根目录运行 `python lanlan-codex/build.py` 可重新生成图集。需要 Pillow，输入来自 `dual-form-pet/normal-transparent.png` 和 `dual-form-pet/pot-transparent.png`。
