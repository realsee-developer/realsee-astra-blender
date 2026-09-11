# Realsee × GPT-6 Astra × Blender

简体中文 | [English](README.md)

[在线阅读网站](https://realsee-developer.github.io/realsee-astra-blender/zh/) · [实景与三维预览](https://realsee-developer.github.io/realsee-astra-blender/zh/#original-space) · [Discord 交流](https://discord.gg/2BcZpmdZj)

用 Realsee 的附加产物作为参考，让 GPT-6 Astra 调用本地 Blender，建立可以继续编辑的三维空间。

这里整理了一次实际项目的提示词、上手教程、空间建模代码和成果预览。重点是墙、地面、顶面、门窗和区域连接，家具与小物件作为补充。

![空间重建效果](docs/assets/overview.jpg)

## 从这里开始

1. 安装 [Blender](https://www.blender.org/download/)，准备能读取本地文件、执行命令的 Astra 会话。本案例使用 Codex 与 Blender 5.2.1 LTS。
2. 在本仓库下创建 `data/`，放入自己的 Realsee 模型与贴图、点云、全景图、CAD 等资料，保留原来的目录结构。
3. 在 Codex 中打开这个项目，把[快速提示词](prompts/quickstart.zh.md)发给 Astra。
4. 先看整体空间预览，再提出修改意见；完成的工程保存到 `output/reconstruction_native.blend`。

具体怎么下载资料、发提示词、看预览继续改，见[图文上手教程](docs/tutorial.zh.md)。想使用本项目更完整的任务要求，可参考[中文详细提示词](ASTRA_BLENDER_GOAL_PROMPT.zh.txt)和[英文版](ASTRA_BLENDER_GOAL_PROMPT.txt)。详细版保留了这次案例的资料说明，使用时让 Astra 按自己的数据调整。

## 先试一下本地环境

准备工具使用 Python 3.10+ 标准库，不需要先安装分析依赖。在仓库根目录运行：

```sh
python3 tools/project.py doctor
python3 tools/project.py inventory
python3 tools/project.py smoke
```

- `doctor` 找到 Blender 并读取版本。
- `inventory` 盘点 `data/`，清单写到 `output/source-inventory.json`。
- `smoke` 在新建的临时输出目录里创建一个测试墙段，经过三个独立 Blender 进程完成保存、重开编辑、再次重开检查。

`smoke` 是环境小测试。正式空间重建从资料和提示词开始；它不会触碰已有模型。如果 Blender 不在 PATH 中，可以在 `doctor` 或 `smoke` 后加 `--blender` 指定实际可执行文件路径。更多分析依赖见[环境说明](docs/environment.md)。

## 仓库里有什么

| 目录 | 内容 |
|---|---|
| [prompts/](prompts/quickstart.zh.md) | 以空间建模为主的快速提示词 |
| [docs/](docs/tutorial.zh.md) | 上手教程、代码导读、案例预览与文件说明 |
| [tools/](tools/project.py) | 环境检查、输入盘点、Blender 保存/编辑小测试 |
| [scripts/](scripts/README.md) | 从项目中选出的空间分析、建模、对照、动画及导出参考代码 |
| [artifacts/](docs/releases.md) | 原生工程、漫游视频、USDZ 与素材说明；大型文件通过 Git LFS 提供 |
| [tests/](tests/test_project.py) | 准备工具的轻量测试 |
| `data/`、`research/`、`output/` | 使用时在本地生成或放入，Git 默认忽略 |

`scripts/` 记录的是这个空间的具体实现，部分代码包含场景对象名、区域坐标和历史中间文件依赖。阅读顺序与运行条件见[代码导读](docs/code-map.md)；用自己的资料时，由 Astra 参考这些方法生成适合当前空间的建模操作。

## 看看成果

![原生空间俯视图](docs/assets/plan.png)

案例最终产物包括原生 `.blend`、可编辑漫游工程、85 秒视频和 USDZ 首版。代码、教程、预览图及大型模型和视频现已公开；大型文件通过 Git LFS 提供。文件清单见[案例文件说明](docs/releases.md)。

整套原始扫描及全景数据留在本地，仓库当前包含经整理的代码、文章、预览和公开成果。代码、提示词和原创文档采用 [MIT](LICENSE)，示例模型与素材的范围见[数据与许可](docs/data-and-license.md)。

## 开发与贡献

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_public_tree.py
```

这两项检查不需要 Blender 或原始场景数据。修改 Blender 调用流程时，再执行上面的 `smoke`。欢迎分享自己的数据组织、建模提示词或工具改进；提交方式见 [CONTRIBUTING.md](CONTRIBUTING.md)。
