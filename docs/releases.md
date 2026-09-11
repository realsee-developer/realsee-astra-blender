# 案例文件与 Git LFS

简体中文 | [English](releases.en.md)

## 案例文件

当前仓库先公开代码、教程与预览图。以下四个大型成果已在本地整理完成，将稍后通过 Git LFS 提供；目前仓库不包含这些文件或其 LFS 指针。

| 文件 | 大小 | 用途 |
|---|---:|---|
| `reconstruction_native.blend` | 252 MB | 原生空间工程，包含独立几何、材质、打包贴图和默认隐藏的扫描参考 |
| `reconstruction_roaming.blend` | 252 MB | 保留相机路线与关键帧的漫游工程 |
| `reconstruction_roaming.mp4` | 44 MB | 85 秒、24 fps、1280×720 的空间漫游 |
| `reconstruction_physics_v1.usdz` | 560 MB | 带刚体、碰撞和材质设置的交换文件首版 |

合计约 1.11 GB。文件大小和 SHA256 见 [manifest.json](../artifacts/manifest.json) 与 [SHA256SUMS](../artifacts/SHA256SUMS)。

## 大文件发布后的下载方式

待模型和视频发布后，安装 [Git LFS](https://git-lfs.com/) 并克隆仓库，然后在仓库根目录运行：

```sh
git lfs install --local
git lfs pull
```

完成后直接用 Blender 打开 `artifacts/reconstruction_native.blend`。继续加工时，把新版本保存到本地 `output/`。USDZ 的动力学需要支持 USD Physics 的软件，普通模型查看器主要用于看模型。

如果下载 ZIP 后模型只有几行文本，那是 LFS 指针。请改用 Git 克隆并运行上述命令，或在 GitHub 文件页面下载实际文件。GitHub 源码压缩包是否包含 LFS 实体由仓库设置决定，见[官方说明](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)。

公开模型已去除现场二维码：纸张和包装保留几何，相关材质改为纯色；包含二维码的部分扫描贴图也已移除，隐藏扫描参考保留几何。视频使用局部遮罩处理对应区域。

公开模型包含其余随工程打包的现场纹理及隐藏扫描参考；原始 `data/` 中的整套点云、全景、RAW 和其他下载资料不随仓库提供。素材范围见[数据与许可](data-and-license.md)。

## 维护者更新文件

`.gitattributes` 已为 `artifacts/` 下的 `.blend`、`.usdz` 和 `.mp4` 配置 LFS。`.gitignore` 只放行已审查的文件名；新增成果时同步更新这份清单和校验信息。

准备发布大文件时，先在 `.gitignore` 中放行上表四个文件名，将公开副本放好，再暂存并检查：

```sh
git add .gitattributes artifacts/
git lfs ls-files
python3 tools/check_public_tree.py
```

检查器会确认暂存区保存的是 LFS 指针，并核对工作区实体的大小与 SHA256。CI 只检出指针即可检查源码，不需要下载全部模型。确认后再自行提交和推送；Git LFS 的 pre-push hook 会上传相应的大文件。配置方式见 [GitHub 官方指南](https://docs.github.com/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage)。
