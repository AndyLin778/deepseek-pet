# 使用说明

## Windows 桌面版

1. 安装 Python 3，并确保 `python.exe` 和 `pythonw.exe` 在 PATH 中。
2. 在仓库根目录安装 Pillow：`python -m pip install -r dual-form-pet/requirements.txt`。
3. 双击 `dual-form-pet/start-pet.vbs`。也可以进入该目录运行 `python pet.py` 来查看错误输出。

操作：双击角色在普通和铁锅形态间切换；按住左键拖动；右键打开跳跃、挥手、散步、暂停、大小和退出菜单。退出时保存形态、大小和位置到本机的 `settings.json`，该文件不会提交到仓库。程序不联网，也不设置开机启动。

## Codex 版

把每个形态的 `pet.json` 和 `spritesheet.webp` 放入各自的宠物目录：

```powershell
$pets = Join-Path $env:USERPROFILE '.codex\pets'
New-Item -ItemType Directory -Force (Join-Path $pets 'lanlan-normal'), (Join-Path $pets 'lanlan-pot') | Out-Null
Copy-Item .\lanlan-codex\normal\pet.json, .\lanlan-codex\normal\spritesheet.webp (Join-Path $pets 'lanlan-normal')
Copy-Item .\lanlan-codex\pot\pet.json, .\lanlan-codex\pot\spritesheet.webp (Join-Path $pets 'lanlan-pot')
```

上述命令在仓库根目录执行。重启 Codex 后，在宠物列表选择“蓝蓝 · 普通”或“蓝蓝 · 铁锅”。Codex 目前通过列表切换这两个包；双击变身属于独立桌面版。

## 重新生成动画图集

先安装 Pillow，然后在仓库根目录运行 `python lanlan-codex/build.py`。脚本读取 `dual-form-pet/normal-transparent.png` 与 `dual-form-pet/pot-transparent.png`，生成两套 1536×2288 的 v2 图集和预览。重新生成后，把更新的 `spritesheet.webp` 复制到桌面版的 `atlas-normal.webp`、`atlas-pot.webp`，以及上面的 Codex 宠物目录。

最初的拼豆图不在仓库中；重新生成动画只依赖已提取的透明像素图。
