"""Run inside Blender. A tiny synthetic edit test, unrelated to the case model."""
import argparse
import json
from pathlib import Path
import sys

import bpy

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--directory", type=Path, required=True)
parser.add_argument("--stage", choices=("create", "edit", "verify"), required=True)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
scene_file = args.directory / "native-wall.blend"

if args.stage == "create":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5))
    wall = bpy.context.object
    wall.name = "Example_Wall"
    wall.scale = (4, 0.2, 3)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    material = bpy.data.materials.new("Wall_Paint")
    material.use_nodes = True
    wall.data.materials.append(material)
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
else:
    bpy.ops.wm.open_mainfile(filepath=str(scene_file))
    wall = bpy.data.objects["Example_Wall"]
    if args.stage == "edit":
        assert abs(wall.dimensions.x - 4) < 1e-5
        for vertex in wall.data.vertices:
            if vertex.co.x > 0:
                vertex.co.x += 0.1
        wall.data.update()
        bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
    else:
        assert wall.type == "MESH" and wall.library is None
        assert abs(wall.dimensions.x - 4.1) < 1e-5
        assert len(wall.data.materials) == 1 and wall.data.materials[0].use_nodes
        result = {"kind": "synthetic_environment_test", "passed": True,
                  "blender_version": bpy.app.version_string,
                  "file": scene_file.name, "wall_width_after_reopen": wall.dimensions.x,
                  "processes": 3}
        (args.directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
