"""Reopened-file validation that the canonical reference retains source geometry and UVs."""
from pathlib import Path
import bpy,json,numpy as np,hashlib
ROOT=Path(__file__).resolve().parents[1]
ref=bpy.data.objects['REFERENCE_HighResolution_OriginalOBJ'];m=ref.data
v=[];uv=[];face=[];faceuv=[]
with (ROOT/'data/model/obj-high-resolution-model/block_0.obj').open() as f:
 for line in f:
  if line.startswith('v '):v.append([float(x) for x in line.split()[1:4]])
  elif line.startswith('vt '):uv.append([float(x) for x in line.split()[1:3]])
  elif line.startswith('f '):
   row=[x.split('/') for x in line.split()[1:]];face.append(tuple(int(x[0])-1 for x in row));faceuv.extend(int(x[1])-1 for x in row)
v=np.asarray(v,dtype=np.float32);uv=np.asarray(uv,dtype=np.float32);model=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',model);model=model.reshape(-1,3)
uvmodel=np.empty(len(m.loops)*2,dtype=np.float32);m.uv_layers.active.data.foreach_get('uv',uvmodel);uvmodel=uvmodel.reshape(-1,2)
maxv=float(np.max(np.abs(v-model))) if v.shape==model.shape else None
maxuv=float(np.max(np.abs(uv[np.array(faceuv)]-uvmodel))) if len(faceuv)==len(m.loops) else None
samefaces=len(face)==len(m.polygons) and all(x==tuple(y.vertices) for x,y in zip(face,m.polygons))
report={'source':'data/model/obj-high-resolution-model/block_0.obj','opened_file':str(Path(bpy.data.filepath).relative_to(ROOT)),'source_vertices':len(v),'native_reference_vertices':len(m.vertices),'source_faces':len(face),'native_reference_faces':len(m.polygons),'vertex_max_abs_difference_m':maxv,'face_connectivity_and_order_exact':samefaces,'uv_max_abs_difference':maxuv,'matrix_world':[list(row) for row in ref.matrix_world],'reference_hidden_render':ref.hide_render,'reference_collection_hidden_render':all(c.hide_render for c in ref.users_collection),'passes':maxv==0 and samefaces and maxuv is not None and maxuv<1e-6}
report['linked_libraries']=[library.filepath for library in bpy.data.libraries]
report['source_file_sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
report['reference_hidden_viewport']=ref.hide_get() or ref.hide_viewport or all(c.hide_viewport for c in ref.users_collection)
original_images={node.image.name:node.image for material in m.materials if material and material.use_nodes for node in material.node_tree.nodes if node.type=='TEX_IMAGE' and node.image}
# Packed images have no external render dependency. Resolve the original
# canonical OBJ material texture names against PROJECT_ROOT, not the .blend's
# output directory or its historical loader path.
source_dir=ROOT/'data/model/obj-high-resolution-model'
mtl_names=[line.split(maxsplit=1)[1].strip()for line in (source_dir/'block_0.obj').read_text().splitlines()if line.startswith('mtllib ')]
source_texture_names=set()
for name in mtl_names:
 for line in (source_dir/name).read_text().splitlines():
  if line.startswith('map_Kd '):source_texture_names.add(line.split(maxsplit=1)[1].strip())
assert len(source_texture_names)==75
texture_checks=[]
for image in original_images.values():
 source_name=Path(image.filepath).name
 assert source_name in source_texture_names,('Reference image not in original OBJ material table',image.name,image.filepath)
 source_path=(source_dir/source_name).resolve()
 source_hash=hashlib.sha256(source_path.read_bytes()).hexdigest()
 packed_hash=hashlib.sha256(bytes(image.packed_file.data)).hexdigest() if image.packed_file else None
 texture_checks.append({'image':image.name,'historical_loader_path':image.filepath,'external_render_dependency':False,'source':str(source_path.relative_to(ROOT)),'source_sha256':source_hash,'packed_sha256':packed_hash,'exact':source_hash==packed_hash})
report['original_texture_checks']=texture_checks
report['original_textures_byte_exact']=bool(texture_checks) and all(row['exact'] for row in texture_checks)
report['unpacked_file_images']=[image.name for image in bpy.data.images if image.source=='FILE' and not (image.packed_file or getattr(image,'packed_files',None))]
report['passes']=report['passes'] and not report['linked_libraries'] and not report['unpacked_file_images'] and report['original_textures_byte_exact']
(ROOT/'output/acceptance/reference-preservation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passes'], 'Canonical reference differs from original geometry or UVs'
