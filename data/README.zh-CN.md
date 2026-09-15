# 案例原始数据

简体中文 | [English](README.md)

这里是[可编辑 Blender 空间项目](../README.zh-CN.md)实际使用的 Realsee 原始导出：**396 个文件，共 6,079,895,800 字节，约 5.66 GiB**。保留原目录结构和文件字节，排除 Finder 的 `.DS_Store`；本目录的说明、清单和校验和是新增的发布资料。

## 下载

安装 Git LFS，然后克隆仓库，避免自动下载所有大文件成果：

```sh
git lfs install
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/realsee-developer/realsee-astra-blender.git
cd realsee-astra-blender
git lfs pull --include="data/**" --exclude=""
```

已有本地仓库时，在仓库根目录执行最后一条命令即可。GitHub 源码 ZIP 可能只有 LFS 指针，应使用 Git LFS 获取真实数据。完整原始数据工作副本约占 5.66 GiB，本地 LFS 缓存还需额外磁盘空间；不同模型导出目录中的相同内容会被 LFS 去重。

也可以先只下载 CAD、一种带贴图模型及全景图：

```sh
git lfs pull --include="data/cad.dwg,data/cad.dxf,data/model/obj-high-resolution-model/**,data/panorama/**" --exclude=""
```

建模需要时再补点云、六面图、RAW 或其他格式。模型与它引用的贴图需一起保留。自己的数据建议放入另一个项目；替换案例输入前先保留独立副本。

## 文件内容

| 输入 | 用途 |
| --- | --- |
| `cad.dwg`、`cad.dxf`、`schematic-floorplan_floor_1.png` | 平面、布局、尺寸和结构参考 |
| `point-cloud.e57`、`point-cloud.ply` | 采集到的三维表面；E57 还包含扫描及图像信息 |
| `model/` | 基础版与高精度 OBJ、FBX、GLB、glTF 导出及配套资源 |
| `panorama/` | 8 张原始全景 JPEG |
| `cube-map/` | 48 张六面图 JPEG，每个视点 6 张 |
| `panorama-raw/` | 8 份 DNG 原件，合计约 4.42 GiB |
| `model-orthogonal-image/` | 6 张平面、立面参考图 |
| `gen-vr-video.mp4` | 原始空间视频参考，与 Blender 重建漫游不同 |

不同网格格式描述的是同一个采集空间，不要当作不同房间重复导入。从[快速提示词](../prompts/quickstart.zh.md)开始即可。这些数据提供来源证据；精选历史脚本还可能依赖本地测量记录和中间检查点，详见[代码导读](../docs/code-map.md)。

## 完整性与公开范围

[manifest.json](manifest.json) 记录每个来源文件的路径、大小及 SHA-256。完整下载后，在仓库根目录校验：

```sh
shasum -a 256 -c data/SHA256SUMS
```

本次经项目所有者授权，原始资料按原样公开，包含照片中的二维码及原始图像元数据。`artifacts/` 中的模型与视频继续使用此前整理的公开副本，已有去码处理保持不变。

案例数据用于演示与学习参考。仓库 MIT 许可适用于代码、提示词和原创文档，不会重新许可来源扫描、照片、画面中的品牌或第三方素材；范围区分见[数据与许可](../docs/data-and-license.md)。
