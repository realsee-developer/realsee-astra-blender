# 案例文件与 Git LFS

简体中文 | [English](releases.en.md)

[案例原始数据](../data/README.zh-CN.md)也已通过 Git LFS 提供，共 396 个文件，约 5.66 GiB，可以用来开始自己的重建。下方列出的是重建后的模型与视频，与原始资料分开下载。

## 案例文件

以下公开成果已通过 Git LFS 提供。点击文件名打开 GitHub 文件页面下载，或按下方说明克隆仓库。

| 文件 | 大小 | 用途 |
|---|---:|---|
| [reconstruction_native.blend](../artifacts/reconstruction_native.blend) | 252 MB | 原生空间工程，包含独立几何、材质、打包贴图和默认隐藏的扫描参考 |
| [reconstruction_roaming.blend](../artifacts/reconstruction_roaming.blend) | 252 MB | 保留相机路线与关键帧的漫游工程 |
| [reconstruction_roaming.mp4](../artifacts/reconstruction_roaming.mp4) | 44 MB | 85 秒、24 fps、1280×720 的空间漫游 |
| [reconstruction_physics_v1.usdz](../artifacts/reconstruction_physics_v1.usdz) | 560 MB | 带刚体、碰撞和材质设置的交换文件首版 |
| [reconstruction_web.glb](../artifacts/reconstruction_web.glb) | 17.2 MB | 从公开 USDZ 生成的轻量网页预览，隐藏顶面，压缩几何与贴图 |

网页首页可直接浏览原始实景、旋转三维模型并播放漫游视频。GLB 只用于浏览展示；编辑组件请使用 Blender 工程，物理数据保留在完整 USDZ 中。

合计约 1.13 GB。文件大小和 SHA256 见 [manifest.json](../artifacts/manifest.json) 与 [SHA256SUMS](../artifacts/SHA256SUMS)。

## 下载模型与视频

安装 [Git LFS](https://git-lfs.com/) 后，下载重建后的模型与视频：

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/realsee-developer/realsee-astra-blender.git
cd realsee-astra-blender
git lfs install --local
git lfs pull --include='artifacts/**' --exclude=''
```

已有本地仓库时，在仓库根目录执行最后两条命令即可。建模输入的下载方式见[原始数据说明](../data/README.zh-CN.md)。

完成后直接用 Blender 打开 `artifacts/reconstruction_native.blend`。继续加工时，把新版本保存到本地 `output/`。USDZ 的动力学需要支持 USD Physics 的软件，普通模型查看器主要用于看模型。

如果下载 ZIP 后模型只有几行文本，那是 LFS 指针。请改用 Git 克隆并运行上述命令，或在 GitHub 文件页面下载实际文件。GitHub 源码压缩包是否包含 LFS 实体由仓库设置决定，见[官方说明](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)。

公开模型已去除现场二维码：纸张和包装保留几何，相关材质改为纯色；包含二维码的部分扫描贴图也已移除，隐藏扫描参考保留几何。视频使用局部遮罩处理对应区域。

公开模型包含其余随工程打包的现场纹理及隐藏扫描参考。[原始点云、全景、RAW 和其他导出资料](../data/README.zh-CN.md)已在 `data/` 中按原样公开，包含现场二维码；上述模型与视频保留已有去码处理。素材范围见[数据与许可](data-and-license.md)。

## 维护者更新文件

`.gitattributes` 已为 `artifacts/` 下的 `.blend`、`.usdz`、`.mp4` 和 `.glb` 配置 LFS。`.gitignore` 只放行已审查的文件名；新增成果时同步更新这份清单和校验信息。

更新时，将经过审查的公开副本放入 `artifacts/`，同步更新 `manifest.json` 与 `SHA256SUMS`，再暂存并检查：

```sh
git add .gitattributes artifacts/
git lfs ls-files
python3 tools/check_public_tree.py
```

检查器会确认暂存区保存的是 LFS 指针，并核对工作区实体的大小与 SHA256。源码检查支持只检出指针；网站构建只拉取网页 GLB 与 MP4，不下载大型 Blender 工程和 USDZ。确认后再自行提交和推送；Git LFS 的 pre-push hook 会上传相应的大文件。配置方式见 [GitHub 官方指南](https://docs.github.com/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage)。
