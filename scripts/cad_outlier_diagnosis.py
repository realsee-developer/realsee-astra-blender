"""Compare conditional structural-distance outliers with all actual native surfaces."""
from pathlib import Path
import json,collections,hashlib,sys
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];assert Path(bpy.data.filepath).resolve()==(ROOT/'output/reconstruction_native.blend').resolve()
assert '--factory-startup' in sys.argv
delivery_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()
structural_record=json.loads((ROOT/'output/acceptance/native_surface_distances.json').read_text())
assert structural_record['opened_file_sha256']==delivery_sha
sample_path=ROOT/'output/acceptance/structural_outlier_samples.npz'
sample_sha=hashlib.sha256(sample_path.read_bytes()).hexdigest()
assert structural_record['structural_sample_sha256']==sample_sha,'Outlier sample archive differs from the final structural-distance producer record.'
sample=np.load(sample_path);rows=sample['samples'];names=sample['object_names'].tolist()
with (ROOT/'data/point-cloud.ply').open('rb') as stream:
 while stream.readline().strip()!=b'end_header':pass
 cloud=np.fromfile(stream,dtype=[(k,'<f4') for k in ['x','y','z','nx','ny','nz']]+[(k,'u1') for k in ['r','g','b']])
points=np.column_stack([cloud[k] for k in ['x','y','z']]);points[:,2]+=json.loads((ROOT/'research/registration-cad.json').read_text())['ply_to_scene_matrix'][2][3]
vertices=[];triangles=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.data.objects:
 if ob.type not in ['MESH','CURVE'] or ob.get('native_coverage_excluded') or ob.hide_render or ob.name.startswith('REFERENCE_') or any(c.hide_render or 'Reference' in c.name for c in ob.users_collection):continue
 evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();start=len(vertices);vertices.extend(evaluated.matrix_world@v.co for v in mesh.vertices)
 for triangle in mesh.loop_triangles:triangles.append(tuple(start+i for i in triangle.vertices));owners.append(ob.name)
 evaluated.to_mesh_clear()
tree=BVHTree.FromPolygons(vertices,triangles,all_triangles=True)
def stats(v):
 a=np.array(v);return {'count':len(v),'median_m':float(np.median(a)),'p95_m':float(np.quantile(a,.95))}
groups={}
for code,name in enumerate(names):
 selected=rows[rows[:,1]==code];nearest=collections.defaultdict(list);distances=[]
 for source_index,owner_code,old_distance in selected:
  p=points[int(source_index)];location,normal,triangle,distance=tree.find_nearest(Vector(p));nearest[owners[triangle]].append(distance);distances.append(distance)
 ids=selected[:,0].astype(int);groups[name]={'structural_only_distances':stats(selected[:,2]),'nearest_any_native_surface':stats(distances),'source_xyz_quantiles_05_50_95_m':np.quantile(points[ids],[.05,.5,.95],axis=0).tolist(),'nearest_native_objects':{k:stats(v) for k,v in sorted(nearest.items(),key=lambda item:len(item[1]),reverse=True)[:15]}}
 print('OUTLIER_DIAGNOSIS',name,json.dumps(groups[name]),flush=True)
report={'opened_final':str(Path(bpy.data.filepath).relative_to(ROOT)),'opened_file_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'factory_startup':True,'structural_sample_sha256':sample_sha,'excluded_archives_and_hidden_objects':True,'method':'Use exactly the accepted source sample IDs from the structural BVH check, verified against its structural_sample_sha256; compute nearest distance to evaluated triangles of every actual native Mesh and Curve surface, including mounted artworks, mirrors, curtains, doors, frames and trim. Original reference excluded. This separates a structural plane residual from a nearer photographed mounted object; no new source exclusions are applied.','groups':groups,'diagnosis':'Interpret together with actual source images and native source metadata; neither structural nor all-native nearest distance alone identifies the semantic source of a reflection.'}
(ROOT/'output/acceptance/structural_outlier_diagnosis.json').write_text(json.dumps(report,indent=2))
