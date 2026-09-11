"""Export the current native render scene, preserving the source Blend on disk."""
from pathlib import Path
import hashlib, json
import bpy
from pxr import Usd, UsdGeom, UsdShade

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/usdz-v1'
source = ROOT / 'output/reconstruction_native.blend'
digest = hashlib.sha256(source.read_bytes()).hexdigest()
assert Path(bpy.data.filepath) == source
assert digest == json.loads((ROOT/'output/acceptance/final-visual-review.json').read_text())['source_delivery_sha256']
target = OUT / 'scene_mesh.usdc'
assert not target.exists()
OUT.mkdir(exist_ok=True)
bpy.context.view_layer.update()
enabled = set()
def walk(layer, blocked=False):
    blocked = blocked or layer.exclude or layer.collection.hide_render
    if not blocked:
        enabled.add(layer.collection.name)
    for child in layer.children:
        walk(child, blocked)
walk(bpy.context.view_layer.layer_collection)
objects = [o for o in bpy.context.scene.objects
           if o.type in {'MESH','CURVE','EMPTY','LIGHT'}
           and not o.hide_render and not o.get('native_coverage_excluded')
           and any(c.name in enabled for c in o.users_collection)]
assert not any(o.name.startswith('REFERENCE') for o in objects)
for o in bpy.context.scene.objects:
    o.select_set(False)
for o in objects:
    o.hide_set(False)
    o.hide_viewport = False
    o.hide_select = False
    o.select_set(True)
source_mesh_count = sum(o.type == 'MESH' for o in objects)
source_curve_count = sum(o.type == 'CURVE' for o in objects)
object_names = [o.name for o in objects]
curves = [o for o in objects if o.type == 'CURVE']
for o in objects:
    o.select_set(o.type == 'CURVE')
bpy.context.view_layer.objects.active = curves[0]
assert bpy.ops.object.convert(target='MESH') == {'FINISHED'}
objects = [bpy.data.objects[name] for name in object_names]
assert all(o.type != 'CURVE' for o in objects)
for o in objects:
    o.select_set(True)
bpy.context.view_layer.objects.active = next(o for o in objects if o.type == 'MESH')
materials = {slot.material for o in objects if o.type in {'MESH','CURVE'} for slot in o.material_slots if slot.material}
material_info = []
for m in sorted(materials, key=lambda x:x.name):
    nodes = list(m.node_tree.nodes) if m.use_nodes else []
    material_info.append({'name':m.name,'nodes':[n.bl_idname for n in nodes],
        'images':[n.image.name for n in nodes if n.type == 'TEX_IMAGE' and n.image],
        'principled':[{'name':n.name,'linked_inputs':[i.name for i in n.inputs if i.is_linked]} for n in nodes if n.type == 'BSDF_PRINCIPLED']})
(OUT/'mesh-export-inventory.json').write_text(json.dumps({
    'source_sha256':digest,'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None} for o in objects],
    'materials':material_info,'scale_length':bpy.context.scene.unit_settings.scale_length},indent=2))
result = bpy.ops.wm.usd_export(filepath=str(target), selected_objects_only=True,
    export_animation=False, export_materials=True, generate_preview_surface=True,
    generate_materialx_network=False, export_textures_mode='NEW', relative_paths=True,
    export_subdivision='TESSELLATE', export_custom_properties=True, author_blender_name=True,
    export_cameras=False, export_lights=True, export_curves=True, export_points=False,
    export_volumes=False, export_armatures=False, export_shapekeys=False,
    root_prim_path='/Scene', convert_scene_units='METERS', allow_unicode=False,
    evaluation_mode='RENDER', use_instancing=False)
assert result == {'FINISHED'}
stage = Usd.Stage.Open(str(target))
prims = list(stage.Traverse())
record = {'source_sha256':digest,'exported_file':str(target.relative_to(ROOT)),
    'meters_per_unit':UsdGeom.GetStageMetersPerUnit(stage),'up_axis':str(UsdGeom.GetStageUpAxis(stage)),
    'source_objects':len(objects),'source_meshes':source_mesh_count,
    'source_curves':source_curve_count,
    'usd_meshes':sum(p.IsA(UsdGeom.Mesh) for p in prims),
    'usd_curves':sum(p.IsA(UsdGeom.BasisCurves) for p in prims),
    'usd_materials':sum(p.IsA(UsdShade.Material) for p in prims),
    'source_file_preserved':hashlib.sha256(source.read_bytes()).hexdigest()==digest,
    'export_result':list(result)}
assert record['source_file_preserved']
(OUT/'mesh-export-record.json').write_text(json.dumps(record,indent=2))
print('USD_BASE_EXPORTED',json.dumps(record),flush=True)
