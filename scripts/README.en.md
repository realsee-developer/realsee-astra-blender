# Script guide

[简体中文](README.md) | English

This selection contains 60 Python scripts and one walkthrough route from the project, showing how an AI agent turns scan data into a native Blender scene. Start with the spatial structure, then explore materials, objects, and exports as needed. The scripts remain in their original locations so their imports are easy to follow.

These are **case-study scripts for one real space**. CAD entities, scan positions, coordinates, and object names have already been established from its source data. For your own Realsee project, have the agent analyze the inputs again and adapt the model. The [original scans, photographs, and source textures](../data/README.md) are available through Git LFS. The script selection includes local Python import dependencies; historical measurement JSON, prepared material assets, and `.blend` checkpoints remain local. It is not a one-command replay of the final project.

## 1. Spatial source data

| Start here | Input → output |
| --- | --- |
| [source_audit.py](source_audit.py) | The `e57` action extracts poses, GUIDs, and embedded previews from `data/point-cloud.e57`; `inventory` only inspects an existing inventory |
| [cad_analysis.py](cad_analysis.py) | DXF, PLY → CAD entities, point-cloud planes, and alignment matrices; includes this case's layers, entity ranges, and PLY layout |
| [match_cubes.py](match_cubes.py) | E57 pose records, panoramas, cube faces, RAW → camera records matched by image content; fixed at eight scan positions in this case |
| [camera_projection_check.py](camera_projection_check.py) | E57 point cloud, panoramas, camera records → projection-direction checks |
| [visual_inventory.py](visual_inventory.py), [develop_raw_previews.py](develop_raw_previews.py) | Cube faces / panoramas / RAW → previews for visual inspection; RAW development requires rawpy |
| [cad_fixture_measurements.py](cad_fixture_measurements.py) | Manually identified light-fixture pixels, ceiling planes, and camera poses → fixture measurement records |
| [cad_niche_measurements.py](cad_niche_measurements.py), [cad_bar_post_measurements.py](cad_bar_post_measurements.py) | This case's CAD and point cloud → analysis of local architectural components |
| [write_visual_coverage.py](write_visual_coverage.py) | A manually observed and confirmed case inventory → JSON mapping sources to spaces and objects; this is not an automatic recognition tool |

## 2. Native space modeling

Read [inspect_scan.py](inspect_scan.py) → [build_structure.py](build_structure.py) → [native_api.py](native_api.py). The first retains the original scan reference. The structure module demonstrates walls, floors, ceilings, and door and window openings. NativeAPI shows methods for Mesh, Curve, local scan extraction, and texture projection.

`build_structure(ROOT)` depends on `research/registration-cad.json`, `cad-entities.json`, `cad-areas.json`, and light-fixture measurement records. It creates structure in the current Blender scene without saving it. Room outlines and component selections come from this case; revisit them when modeling a different space.

[build_scene.py](build_scene.py) is an **early example of whole-scene integration**. It reads `output/checkpoints/00_scan_import.blend` and writes `output/reconstruction_native.blend`. The final deliverable underwent further visual revisions, so this entry point illustrates organization but does not directly produce the final refined version. It writes to the deliverable path; adapt its inputs and outputs in your own working copy before using it.

For structure, start with [build_structure.py](build_structure.py), [final_plenum_height.py](final_plenum_height.py), and [final_structural_fixtures.py](final_structural_fixtures.py). For photo-based materials, see [prepare_surface_textures.py](prepare_surface_textures.py), [prepare_photo_textures.py](prepare_photo_textures.py), [build_surface_materials.py](build_surface_materials.py), [refine_appearance.py](refine_appearance.py), and [final_floor_albedo.py](final_floor_albedo.py). Photograph sample locations and texture assets are specific to this case.

The following modules are also included to preserve the integration example's imports. Explore furniture and props if they interest you:

- Area builders: [build_corridor.py](build_corridor.py), [build_fashion.py](build_fashion.py), [build_bar.py](build_bar.py), [build_game.py](build_game.py), [build_living.py](build_living.py), [build_living_details.py](build_living_details.py), and [build_observed_details.py](build_observed_details.py).
- Early integration dependencies: [final_bar_entry.py](final_bar_entry.py), [final_bar_seats.py](final_bar_seats.py), [final_case_detail.py](final_case_detail.py), [final_chair_material.py](final_chair_material.py), [final_fan_pose.py](final_fan_pose.py), [final_fashion_accessories.py](final_fashion_accessories.py), [final_fashion_tray.py](final_fashion_tray.py), [final_game_illumination.py](final_game_illumination.py), [final_helmet_detail.py](final_helmet_detail.py), [final_living_detail_alignment.py](final_living_detail_alignment.py), [final_living_identification.py](final_living_identification.py), [final_small_fixture_poses.py](final_small_fixture_poses.py), and [final_visual_alignment.py](final_visual_alignment.py).

## 3. Comparisons and actual editing

| Script | Purpose and prerequisites |
| --- | --- |
| [render_comparisons.py](render_comparisons.py), [render_comparison_contacts.py](render_comparison_contacts.py) | Open the native scene, render quick/full/structure/solid views from recorded poses, then arrange them alongside source images; requires source images and camera/alignment JSON |
| [cad_structure_check.py](cad_structure_check.py) | Clear the current process's scene, call the structure builder, inspect topology, and save a structure checkpoint; use a separate Blender process |
| [verify_acceptance.py](verify_acceptance.py) | `audit` inspects the scene; `edit` modifies a temporary copy; `verify` reopens that copy in a new process to confirm the edits persisted. Test object names come from this case |
| [verify_reference.py](verify_reference.py), [verify_source_preservation.py](verify_source_preservation.py) | Check the retained scan reference and original file hashes; requires original data and the initial inventory |
| [cad_structural_measurements.py](cad_structural_measurements.py), [cad_native_distance.py](cad_native_distance.py), [cad_outlier_diagnosis.py](cad_outlier_diagnosis.py) | Compare local parts of the case's native structure with CAD/point-cloud data; read these for a closer look at validation methods |
| [check_mesh_exports.py](check_mesh_exports.py), [export_scene_manifest.py](export_scene_manifest.py) | Inspect geometry from different source formats and export a scene object inventory, respectively; both depend on this case's paths and object organization |

## 4. Walkthrough animation

[create_walkthrough.py](create_walkthrough.py) reads the completed native scene and [walkthrough-route.json](walkthrough-route.json), creates camera keyframes, and checks the route. [render_walkthrough.py](render_walkthrough.py) reads the saved animation and review records, then renders preview and final stages. [encode_walkthrough.py](encode_walkthrough.py) checks the frame sequence and uses ffmpeg/ffprobe to encode and inspect the video.

The route is specific to this space. The authoring script retains the backup-hash checks used to protect the earlier deliverable, and the rendering script uses Metal. These three entry points illustrate how the animation work was organized. For your own scene, adapt the route, device, and output management together; they cannot simply be run in sequence from a clean clone.

## 5. USDZ export extension

[export_usdz_v1_base.py](export_usdz_v1_base.py) exports visible meshes from the final native scene. [author_usdz_v1_physics.py](author_usdz_v1_physics.py) sets mass and collision properties using this case's object hierarchy. [package_usdz_v1.py](package_usdz_v1.py) packages a prepared USD stage. [verify_usdz_v1_package.py](verify_usdz_v1_package.py) reopens and inspects the package in a new process. [render_usdz_v1_roundtrip.py](render_usdz_v1_roundtrip.py) imports the actual USDZ for image checks.

This selection demonstrates export, physics grouping, and reopening checks. It **does not include the complete historical material baking and repair pipeline**. The final USDZ also used intermediate material and texture results from the original project, so these five files are not a one-command reproduction of the final export. Object counts, names, and review SHA hashes are case-specific checks; inspecting a USD package also does not amount to testing it on a device.

## Environment and execution

Analysis code runs in ordinary Python; scripts involving `bpy` run in Blender's bundled Python. Common dependencies include NumPy, SciPy, Pillow, Matplotlib, and ezdxf, with pye57, rawpy, and pyquaternion used in particular steps. The USD stage requires pxr. Libraries installed in system Python may not be available to Blender's Python.

Read a script's inputs and output destinations before running it in a separate process. Most scripts begin work at module level; do not bulk-import them or discover them automatically as pytest tests. Keep the project root as the working directory and let your local agent discover the actual Blender installation. See the [code map](../docs/code-map.en.md) for a shorter dependency overview.
