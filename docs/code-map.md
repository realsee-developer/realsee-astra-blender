# 代码地图

简体中文 | [English](code-map.en.md)

公开目录精选 60 个 Python 脚本和 1 份路线 JSON。它保留早期空间构建示例及其本地导入依赖，另收录来源阅读、对照、编辑验证与扩展示例。原始扫描、照片、测量结果和历史检查点不随代码提供。详细输入见 [脚本导航](../scripts/README.md)。

```text
自己的 Realsee 附加产物
  ├─ CAD / 点云 ── 实体提取与配准 ─┐
  ├─ E57 / 全景 / 六面图 ── 位姿 ─┼─ 空间证据 → 墙地顶、开口、区域连接
  └─ 带纹理的扫描 ── 保留参考 ────┘                 │
                                       原生 Blender 场景
                                           ├─ 源图 / 平面 / 结构对照
                                           ├─ 保存、重开、实际编辑
                                           └─ 可选：漫游、USDZ
```

## 先读这几个文件

1. [source_audit.py](../scripts/source_audit.py)、[cad_analysis.py](../scripts/cad_analysis.py)、[match_cubes.py](../scripts/match_cubes.py)：资料如何变成可追踪的空间依据。本案例的格式、点位和实体选择已经确定。
2. [inspect_scan.py](../scripts/inspect_scan.py)、[build_structure.py](../scripts/build_structure.py)、[native_api.py](../scripts/native_api.py)：保留扫描，并创建可编辑的墙地顶、开口及几何组件。
3. [build_scene.py](../scripts/build_scene.py)：早期整场组织方式。它依赖检查点、证据 JSON、材质资产和区域模块，且写交付文件；最终精修经历了额外迭代。
4. [render_comparisons.py](../scripts/render_comparisons.py)、[verify_acceptance.py](../scripts/verify_acceptance.py)：怎样看出建模是否接近来源，以及修改能否在重开后保存。
5. [create_walkthrough.py](../scripts/create_walkthrough.py)、[export_usdz_v1_base.py](../scripts/export_usdz_v1_base.py)：在完成的场景上扩展动画和导出。路线、物理分组、审核记录与材质处理中间结果都需要按自己的项目处理。

## 导入关系与数据依赖

`build_scene` 导入区域构建、`build_structure`、`native_api`、材质和早期细节模块；这些模块的本地 Python 导入依赖都保留在精选目录中。`cad_structure_check` 依赖 `build_structure`；两项局部 CAD 测量依赖 `cad_analysis`；USDZ 重开渲染复用 `render_comparisons` 的相机设置。

本地导入完整不等于数据链完整。建模还会读取 `research/` 的配准、区域和测量 JSON，`output/assets/` 的来源纹理，以及 `output/checkpoints/` 的旧场景。动画需要已完成场景与审核记录；USDZ 案例的完整材质烘焙/修补过程未纳入本次精选。将这些文件当作方法参考，让 agent 针对自己的资料重新组织步骤。

## 为什么不把全部历史脚本放进主目录

项目曾为一个空间做过多轮候选、局部修补、渲染和审稿。公开版挑选空间建模主线，并保留直接依赖；其余迭代仍留在本地项目。没有收录外部生成任务提交和密钥读取脚本，也没有把一次性诊断当作通用测试框架。

脚本暂不搬成多层 Python 包，因为它们通过自身位置定位项目并导入同目录模块。这样的整理先让参考代码易读，避免改目录时无意改变实际行为。
