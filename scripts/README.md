# 脚本导航

这里精选本项目的 60 个 Python 脚本与 1 份漫游路线，方便阅读 AI agent 如何把扫描资料转成 Blender 原生场景。先看空间结构，再按需要浏览材质、物件和导出。脚本保留原位置，便于追踪彼此的导入关系。

这些是**同一个实际空间的案例代码**：CAD 实体、点位、坐标和对象名已按项目资料确定。自己的 Realsee 项目需要让 agent 重新分析资料、调整模型。精选代码保留了本地 Python 导入依赖，但没有附带私有扫描、照片、测量 JSON、纹理和历史 `.blend` 检查点；它不构成最终工程的一键重放包。

## 1. 空间资料

| 从这里读 | 输入 → 结果 |
| --- | --- |
| [source_audit.py](source_audit.py) | `e57` 动作从 `data/point-cloud.e57` 提取位姿、GUID 与嵌入预览；`inventory` 动作仅检查已有清单 |
| [cad_analysis.py](cad_analysis.py) | DXF、PLY → CAD 实体、点云平面与配准矩阵；包含本案例的图层、实体范围及 PLY 布局 |
| [match_cubes.py](match_cubes.py) | E57 位姿记录、全景、六面图、RAW → 内容匹配后的相机记录；本例固定 8 个点位 |
| [camera_projection_check.py](camera_projection_check.py) | E57 点云、全景、相机记录 → 投影方向检查 |
| [visual_inventory.py](visual_inventory.py)、[develop_raw_previews.py](develop_raw_previews.py) | 六面图/全景/RAW → 便于人工阅读的预览；RAW 开发需要 rawpy |
| [cad_fixture_measurements.py](cad_fixture_measurements.py) | 手工识别的灯具像素、天花平面和相机位姿 → 灯具测量记录 |
| [cad_niche_measurements.py](cad_niche_measurements.py)、[cad_bar_post_measurements.py](cad_bar_post_measurements.py) | 本例 CAD 和点云 → 局部建筑构件分析 |
| [write_visual_coverage.py](write_visual_coverage.py) | 已人工观察确认的案例清单 → 来源与空间/物件对应 JSON；并非自动识别器 |

## 2. 原生空间建模

推荐顺序是 [inspect_scan.py](inspect_scan.py) → [build_structure.py](build_structure.py) → [native_api.py](native_api.py)。前者保留原始扫描参考；结构模块展示如何建立墙、地板、天花、门窗开口；NativeAPI 展示 Mesh、Curve、局部扫描提取与贴图投影方法。

`build_structure(ROOT)` 依赖 `research/registration-cad.json`、`cad-entities.json`、`cad-areas.json` 和灯具测量记录，在当前 Blender 场景中创建结构，不自行保存。房间轮廓与构件选择来自本案例，换空间时从这里重新建模。

[build_scene.py](build_scene.py) 是**早期整场集成示例**，读取 `output/checkpoints/00_scan_import.blend`，并写入 `output/reconstruction_native.blend`。最终交付后来经历了更多视觉修改，所以阅读这个入口可以理解组织方式，直接执行不会得到最终精修版。它会保存交付路径，应在自己的工作副本中改好输入和输出后使用。

结构优先读 [build_structure.py](build_structure.py)、[final_plenum_height.py](final_plenum_height.py)、[final_structural_fixtures.py](final_structural_fixtures.py)。照片材质示例见 [prepare_surface_textures.py](prepare_surface_textures.py)、[prepare_photo_textures.py](prepare_photo_textures.py)、[build_surface_materials.py](build_surface_materials.py)、[refine_appearance.py](refine_appearance.py)、[final_floor_albedo.py](final_floor_albedo.py)。照片样本位置与纹理资产均属于本例。

为保留集成示例的导入关系，同时公开以下模块；家具与摆件可按兴趣阅读：

- 区域构建：[build_corridor.py](build_corridor.py)、[build_fashion.py](build_fashion.py)、[build_bar.py](build_bar.py)、[build_game.py](build_game.py)、[build_living.py](build_living.py)、[build_living_details.py](build_living_details.py)、[build_observed_details.py](build_observed_details.py)。
- 早期集成依赖：[final_bar_entry.py](final_bar_entry.py)、[final_bar_seats.py](final_bar_seats.py)、[final_case_detail.py](final_case_detail.py)、[final_chair_material.py](final_chair_material.py)、[final_fan_pose.py](final_fan_pose.py)、[final_fashion_accessories.py](final_fashion_accessories.py)、[final_fashion_tray.py](final_fashion_tray.py)、[final_game_illumination.py](final_game_illumination.py)、[final_helmet_detail.py](final_helmet_detail.py)、[final_living_detail_alignment.py](final_living_detail_alignment.py)、[final_living_identification.py](final_living_identification.py)、[final_small_fixture_poses.py](final_small_fixture_poses.py)、[final_visual_alignment.py](final_visual_alignment.py)。

## 3. 对照与实际编辑

| 脚本 | 作用与前提 |
| --- | --- |
| [render_comparisons.py](render_comparisons.py)、[render_comparison_contacts.py](render_comparison_contacts.py) | 打开原生场景，按登记位姿渲染 quick/full/structure/solid 视图，再与源图排成对照；需要源图和相机/配准 JSON |
| [cad_structure_check.py](cad_structure_check.py) | 清空当前进程场景，调用结构构建，检查拓扑并保存结构检查点；请在独立 Blender 进程中使用 |
| [verify_acceptance.py](verify_acceptance.py) | audit 检查场景；edit 修改临时副本；verify 在新进程重开副本确认编辑保存。测试对象名来自本例 |
| [verify_reference.py](verify_reference.py)、[verify_source_preservation.py](verify_source_preservation.py) | 核对保留的扫描参考及原始文件哈希；需要原始资料和最初的清单 |
| [cad_structural_measurements.py](cad_structural_measurements.py)、[cad_native_distance.py](cad_native_distance.py)、[cad_outlier_diagnosis.py](cad_outlier_diagnosis.py) | 对案例原生结构与 CAD/点云做局部比较；想深入了解验证方法时再看 |
| [check_mesh_exports.py](check_mesh_exports.py)、[export_scene_manifest.py](export_scene_manifest.py) | 分别检查不同来源格式的几何、导出场景对象清单；都依赖本例路径与对象组织 |

## 4. 漫游动画

[create_walkthrough.py](create_walkthrough.py) 读取已完成的原生场景和 [walkthrough-route.json](walkthrough-route.json)，创建相机关键帧并检查路线。[render_walkthrough.py](render_walkthrough.py) 读取保存后的动画和审核记录，分预览/最终阶段渲染；[encode_walkthrough.py](encode_walkthrough.py) 核对帧序列后用 ffmpeg/ffprobe 编码及检查视频。

路线是本空间专用的。作者脚本保留了当时保护旧交付的备份哈希检查；渲染脚本使用 Metal。这三个入口适合参考动画的组织方式，使用自己的场景时需要同时调整路线、设备和产物管理，不能在干净克隆中直接串起来运行。

## 5. USDZ 导出扩展

[export_usdz_v1_base.py](export_usdz_v1_base.py) 从最终原生场景导出可见网格；[author_usdz_v1_physics.py](author_usdz_v1_physics.py) 按本案例对象层级设置质量和碰撞；[package_usdz_v1.py](package_usdz_v1.py) 打包已准备好的 USD stage；[verify_usdz_v1_package.py](verify_usdz_v1_package.py) 在新进程重开并检查包；[render_usdz_v1_roundtrip.py](render_usdz_v1_roundtrip.py) 导入真正的 USDZ 做图像检查。

这个精选版本展示导出、物理分组和重开验证的方法，**未收录完整历史材质烘焙与修补链**。最终 USDZ 的形成还用到了原项目的中间材质和纹理结果；不要把上面五个文件当作最终导出的一键复现步骤。对象数、对象名及审核 SHA 是案例检查项，普通 USD 包检查也不等于设备实测。

## 环境与运行方式

分析代码使用普通 Python；涉及 `bpy` 的脚本由 Blender 自带 Python 执行。常用依赖是 NumPy、SciPy、Pillow、Matplotlib、ezdxf，特定步骤另用 pye57、rawpy、pyquaternion；USD 阶段需要 pxr。安装在系统 Python 的库不一定能被 Blender 的 Python 使用。

先阅读脚本的输入和写入目标，再用独立进程执行。多数脚本在文件顶层就开始工作，不要批量 import 或自动发现为 pytest 测试。保持项目目录为工作目录，并让本地 agent 发现 Blender 的实际安装位置。更简短的依赖总览见 [代码地图](../docs/code-map.md)。
