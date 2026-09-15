# 数据与许可

简体中文 | [English](data-and-license.en.md)

这个仓库分享用 Realsee 附加产物协同 Astra、Blender 重建空间的方法、提示词和代码。代码、提示词及原创文档采用 [MIT 许可证](../LICENSE)。

## 文件放在哪里

| 内容 | 安排 |
| --- | --- |
| 提示词、代码、原创文档 | 随 Git 仓库发布，采用 MIT。 |
| `docs/assets/` 中的案例预览 | 已获授权公开，便于浏览建模效果；素材许可范围见下文。 |
| 最终模型与视频 | 已整理的公开副本通过 Git LFS 提供，文件与下载说明见[案例文件](releases.md)。 |
| `data/` | 已授权公开的案例原始资料通过 Git LFS 提供，见[数据说明](../data/README.zh-CN.md)。其他使用者的私人导出仍不提交，除非明确授权并经过公开审查。 |
| `output/`、`research/` | 本地模型、中间文件、分析记录和日志，不提交到 Git；公开内容另行挑选整理。 |
| 虚拟环境、缓存、凭据文件 | 留在本地，不提交到 Git。 |

体验流程时，按[数据说明](../data/README.zh-CN.md)下载案例输入，或放入自己的 CAD、点云、全景图和扫描模型，不覆盖已公开的文件。保留原始目录及模型与贴图的相对位置，再使用[快速提示词](../prompts/quickstart.zh.md)。

案例原始资料包含 396 个文件，共 6,079,895,800 字节（约 5.66 GiB），不含 `.DS_Store`。这些资料已获授权按原样公开，包含现场二维码。现有预览、最终模型与视频仍为先前经过审查、脱敏的副本：未知用途的现场二维码已去除，部分包装字样和扫描参考的照片颜色因此省略。公开原始资料不会替换这些副本。

## 代码与素材分开说明

MIT 适用于本项目的代码、提示词和原创文档正文，不会自动改变 Realsee 原始导出、照片纹理、第三方生成资产或其他第三方内容的权利。已授权公开的案例原始资料、预览和最终模型可作为案例展示与学习参考；素材权利仍属于对应来源，公开不构成新的商业再许可。详见[原始数据说明](../data/README.zh-CN.md)及[案例素材说明](../artifacts/NOTICE.txt)，不将原始数据集或整个模型包统一标为 MIT。

写作过程参考了 [ComposioHQ 的 Content Research Writer](https://github.com/ComposioHQ/awesome-claude-skills/blob/master/content-research-writer/SKILL.md)。仓库保留来源链接，不再分发该技能全文。外部工具和依赖继续使用各自的许可证。

网页 GLB 仅从已审查的公开 USDZ 派生，沿用同一素材说明。网站中的 Three.js 使用 MIT 许可（随站点分发于 `vendor/three/LICENSE`），Draco 解码器使用 [Apache 2.0 许可](../site/DRACO_LICENSE.txt)。
