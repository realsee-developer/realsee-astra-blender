"""Run in isolated Blender background process; does not save or modify any .blend."""
import bpy, json, sys
from pathlib import Path
import numpy as np
ROOT=Path.cwd().resolve();OUT=ROOT/'research/export-checks';OUT.mkdir(exist_ok=True)
paths=[p for p in (ROOT/'data/model').rglob('*') if p.suffix.lower() in ['.obj','.gltf','.glb','.fbx']]
rows=[]
for path in sorted(paths):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if path.suffix=='.obj': bpy.ops.wm.obj_import(filepath=str(path),forward_axis='Y',up_axis='Z')
 elif path.suffix in ['.gltf','.glb']:bpy.ops.import_scene.gltf(filepath=str(path))
 else:bpy.ops.import_scene.fbx(filepath=str(path))
 verts=[];tris=[];count=0; row={'path':str(path.relative_to(ROOT)),'objects':[]}
 for ob in bpy.data.objects:
  if ob.type!='MESH':continue
  me=ob.data;v=np.empty((len(me.vertices),3),dtype=np.float64);me.vertices.foreach_get('co',v.ravel());v=v@np.array(ob.matrix_world)[:3,:3].T+np.array(ob.matrix_world)[:3,3]
  me.calc_loop_triangles();t=np.empty((len(me.loop_triangles),3),dtype=np.int32);me.loop_triangles.foreach_get('vertices',t.ravel());tris.append(t+count);verts.append(v);count+=len(v)
  row['objects'].append({'name':ob.name,'vertices':len(v),'triangles':len(t),'matrix_world':[list(r) for r in ob.matrix_world]})
 v=np.concatenate(verts);t=np.concatenate(tris);row['imported_bounds_min']=v.min(0).tolist();row['imported_bounds_max']=v.max(0).tolist()
 # Observed source OBJ/PLY are Z-up. Undo importer-assumed Y-up for glTF/FBX after verifying ranges.
 if path.suffix in ['.gltf','.glb','.fbx']:
  v=v[:,[0,2,1]]*np.array([1,1,-1]);row['to_raw_transform']='raw_xyz=(Blender_import_x,Blender_import_z,-Blender_import_y)'
 else:row['to_raw_transform']='identity (explicit OBJ forward Y / up Z)'
 row['canonical_bounds_min']=v.min(0).tolist();row['canonical_bounds_max']=v.max(0).tolist();row['vertices']=len(v);row['triangles']=len(t)
 row['images']=[{'name':im.name,'exists':Path(bpy.path.abspath(im.filepath)).exists(),'filepath':bpy.path.relpath(im.filepath)} for im in bpy.data.images if im.source=='FILE']
 name=path.parent.name;np.savez_compressed(OUT/(name+'.npz'),vertices=v,triangles=t)
 rows.append(row);(OUT/'imports.json').write_text(json.dumps(rows,indent=2));print('AUDIT_IMPORTED',row['path'],row['vertices'],row['triangles'],row['canonical_bounds_min'],row['canonical_bounds_max'],flush=True)
