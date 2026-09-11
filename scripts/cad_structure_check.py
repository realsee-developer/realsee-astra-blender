from pathlib import Path
import sys,json,bpy,bmesh
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts'))
from build_structure import build_structure
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
r=build_structure(ROOT)
errors=[]
for o in r['objects']:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 bad=sum(not e.is_manifold for e in bm.edges)
 if bm.calc_volume(signed=True)<-1e-9:errors.append((o.name,'negative_volume'))
 if bad:errors.append((o.name,'nonmanifold',bad))
 if sum(f.calc_area()<1e-12 for f in bm.faces):errors.append((o.name,'degenerate'))
 bm.free()
print('STRUCTURE_CHECK',len(r['objects']),errors)
assert not errors,'Standalone structural topology checks failed.'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/checkpoints/structure_agent.blend'))
(ROOT/'research/cad-structure-check.json').write_text(json.dumps({'object_count':len(r['objects']),'mesh_check_errors':errors},indent=2))
# Workbench plan from real built mesh, roofs hidden by collection.
for k,c in r['collections'].items():
 if k.endswith('/Ceilings') or k.endswith('/Lighting') or k.endswith('/Services'):c.hide_render=True
bpy.ops.object.camera_add(location=(-2.4,4.5,25));cam=bpy.context.object;cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=16;cam.rotation_euler=(0,0,0);bpy.context.scene.camera=cam
bpy.context.scene.render.engine='BLENDER_WORKBENCH';bpy.context.scene.display.shading.light='STUDIO';bpy.context.scene.display.shading.color_type='MATERIAL';bpy.context.scene.display.shading.show_shadows=True;bpy.context.scene.render.resolution_x=1600;bpy.context.scene.render.resolution_y=1300;bpy.context.scene.render.resolution_percentage=100;bpy.context.scene.render.filepath=str(ROOT/'research/cad-structure-native-plan.png');bpy.ops.render.render(write_still=True)
