# DeepSeek 桌宠（Codex 版和桌面版）

用两幅拼豆像素画制作的双形态动态桌宠：普通形态和铁锅形态。仓库提供独立 Windows 桌面程序，以及可装入 Codex 的两个宠物包。这是个人制作的非官方项目，与 DeepSeek、OpenAI 或 Codex 官方无隶属关系。

![普通形态待机](lanlan-codex/normal/idle.gif) ![铁锅形态待机](lanlan-codex/pot/idle.gif)

## 两种使用方式

- **Windows 桌面版**：双击角色切换形态，拖动移动，右键可跳跃、挥手、散步、调整大小和退出。入口在 [`dual-form-pet/`](dual-form-pet/README.md)。
- **Codex 版**：安装 `lanlan-codex/normal` 与 `lanlan-codex/pot` 两个 v2 宠物包，在 Codex 宠物列表中切换。安装说明见 [`USAGE.md`](USAGE.md)。Codex 版的图集本身不能给宠物添加双击变身手势。

项目设计见 [`DESIGN.md`](DESIGN.md)，完整安装和使用步骤见 [`USAGE.md`](USAGE.md)。

## 素材与许可

最初用于取色的两张拼豆图**没有上传**。仓库只包含桌宠运行所需的透明像素图、动画图集和预览。程序代码与文档按 [MIT 许可证](LICENSE)发布；网络图像及其衍生的视觉素材不在 MIT 授权范围内，详见 [`ASSETS.md`](ASSETS.md)。

本项目的帧是基于原像素画做的局部动作。指针方向动画比较轻微；图集通过 Codex v2 结构与透明度验证，尚未完成独立的方向语义盲测。
