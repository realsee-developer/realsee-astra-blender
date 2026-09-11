# Code map

[简体中文](code-map.md) | English

The public selection contains 60 Python scripts and one route JSON file. It includes early examples of building the space and their local import dependencies, alongside examples of source inspection, comparison, editing checks, and extensions. Original scans, photographs, measurements, and historical checkpoints are not included. See the [script guide](../scripts/README.en.md) for detailed inputs.

```text
Your Realsee exports
  ├─ CAD / point clouds ── extraction and alignment ─┐
  ├─ E57 / panoramas / cube faces ── camera poses ──┼─ spatial evidence
  └─ Textured scan ── retained as a reference ──────┘        │
                                      walls, floors, ceilings, openings,
                                               and connected areas
                                                        │
                                               native Blender scene
                                                  ├─ image / plan / structure comparisons
                                                  ├─ save, reopen, and edit
                                                  └─ optional: walkthrough, USDZ
```

## Start with these files

1. [source_audit.py](../scripts/source_audit.py), [cad_analysis.py](../scripts/cad_analysis.py), and [match_cubes.py](../scripts/match_cubes.py): how source files become traceable spatial evidence. Formats, scan positions, and entity selections are already established for this case.
2. [inspect_scan.py](../scripts/inspect_scan.py), [build_structure.py](../scripts/build_structure.py), and [native_api.py](../scripts/native_api.py): retain the scan and create editable walls, floors, ceilings, openings, and geometric components.
3. [build_scene.py](../scripts/build_scene.py): an early example of organizing the whole scene. It depends on checkpoints, evidence JSON, material assets, and area modules, and writes the deliverable file. The final scene went through further refinement.
4. [render_comparisons.py](../scripts/render_comparisons.py) and [verify_acceptance.py](../scripts/verify_acceptance.py): compare the model against its sources and check whether edits persist after reopening.
5. [create_walkthrough.py](../scripts/create_walkthrough.py) and [export_usdz_v1_base.py](../scripts/export_usdz_v1_base.py): add animation and export to a completed scene. Routes, physics groups, review records, and intermediate material results need to be adapted to your own project.

## Imports and data dependencies

`build_scene` imports the area builders, `build_structure`, `native_api`, materials, and early detail modules. Their local Python import dependencies are all included in the selection. `cad_structure_check` depends on `build_structure`; two local CAD measurement scripts depend on `cad_analysis`; the USDZ round-trip renderer reuses camera settings from `render_comparisons`.

Having all local imports does not mean having the entire data pipeline. Modeling also reads alignment, area, and measurement JSON from `research/`, source textures from `output/assets/`, and older scenes from `output/checkpoints/`. Animation requires the completed scene and review records. The full material baking and repair process for the USDZ case is outside this selection. Use these files as method references and let your agent organize the steps around your own data.

## Why the repository includes selected historical scripts

The project went through multiple candidates, local repairs, renders, and reviews for one space. The public version selects the main space-modeling workflow and keeps its direct dependencies; the remaining iterations stay in the local project. Scripts that submit external generation jobs or read credentials are excluded, and one-off diagnostics are not presented as a general test framework.

The scripts remain in a flat directory because they locate the project through their own file location and import neighboring modules. Keeping that layout makes the reference code easier to follow without changing its behavior through a directory move.
