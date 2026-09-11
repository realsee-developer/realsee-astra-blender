# 环境说明

## 快速开始

准备工具使用 Python 3.10+ 标准库。Blender 通过 PATH 中的 `blender` 查找，也可使用 `--blender` 指定可执行文件；路径中的符号链接会解析到实际程序，帮助 Blender 找到自身资源。

```sh
python3 tools/project.py doctor
python3 tools/project.py smoke
```

`smoke` 使用三个独立后台进程创建测试墙、重开并编辑、再重开检查。结果写入新的 `output/smoke-*/`，已有重建场景不参与这个小测试。

## 案例分析代码

本项目分析环境的依赖版本记录在 [requirements-analysis.txt](../requirements-analysis.txt)。如果需要研究 `scripts/` 中的 CAD、点云与图像处理代码，可以在独立虚拟环境中安装：

```sh
python3 -m venv .venv-analysis
.venv-analysis/bin/python -m pip install -r requirements-analysis.txt
```

上面是 macOS/Linux 命令；Windows 的虚拟环境 Python 位于 `.venv-analysis/Scripts/python.exe`。这是案例依赖快照，按 [代码导读](code-map.md) 选择需要研究的部分即可。

Blender 的 `bpy`、`bmesh` 和 `mathutils` 在 Blender 自己的 Python 环境中运行。系统虚拟环境安装的库不会自动出现在 Blender 里；案例脚本额外使用的 SciPy、Pillow、USD `pxr` 等，需要由运行它的环境提供。视频编码另外使用 FFmpeg/ffprobe。

## 已执行检查

本轮整理在本机 Blender 5.2.1 LTS 中实际运行了准备工具和三进程编辑小测试；分析依赖来自已有项目环境。本轮没有重新运行整场建模、漫游渲染或所有历史修复脚本。自动检查只发现 `tests/` 下的测试，不导入案例脚本。
