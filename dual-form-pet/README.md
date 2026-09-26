# deepseek鲸鱼娘：双形态像素桌宠

Windows 上安装 Python 3 和 Pillow（`python -m pip install -r requirements.txt`），双击 `start-pet.vbs` 启动。`pythonw.exe` 需在 PATH 中。运行时无需联网。

- 双击角色：在普通形态和铁锅形态之间切换，并轻轻弹跳。快速连续点击有防重复处理。
- 按住鼠标左键：拖动位置。
- 右键角色：跳跃、摇摆、开启散步、暂停、调整大小、退出。
- 默认播放从拼豆图制作的待机和眨眼帧；散步时播放左右移动帧。散步默认关闭。
- 退出后记住形态、大小和位置；不设置开机启动。

这是独立 Windows 透明置顶桌宠，不是 Codex 宠物插件，也不读取 Codex 工作状态。
形象来自两张拼豆图的逐格采样；铁锅形态已清理外围浅白杂点并补上细深色轮廓。`atlas-normal.webp` 和 `atlas-pot.webp` 提供逐帧动画。动画主要由原像素画的局部移动、眨眼和弹跳构成，肢体动作较轻微。
仓库仅含桌宠所需的透明像素素材和动画图集；最初两张拼豆图不在项目中。底部色卡编号尚未逐格人工核对。

如果 VBS 启动被系统禁用，可在 PowerShell 运行：

```powershell
pythonw .\pet.py
```
