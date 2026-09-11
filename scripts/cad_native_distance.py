"""Measure selected source PLY samples against actual saved native structural triangles.
Run in fresh factory-startup Blender opened on output/reconstruction_native.blend.
This is a conditional surface-fit metric, separate from CAD registration residuals.
"""
from pathlib import Path
import sys,json,hashlib,collections
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
assert bpy.data.filepath,'Open the actual saved delivery file before running this check.'
assert Path(bpy.data.filepath).resolve()==(ROOT/'output/reconstruction_native.blend').resolve(),'This check must inspect the actual delivery file.'
assert '--factory-startup' in sys.argv,'Acceptance check requires factory-startup Blender.'
with (ROOT/'data/point-cloud.ply').open('rb') as stream:
 header=[]
 while True:
  line=stream.readline().decode('ascii').strip();header.append(line)
  if line=='end_header':break
 count=int(next(line.split()[-1] for line in header if line.startswith('element vertex')))
 cloud=np.fromfile(stream,dtype=[(k,'<f4') for k in ['x','y','z','nx','ny','nz']]+[(k,'u1') for k in ['r','g','b']],count=count)
points=np.column_stack([cloud[k] for k in ['x','y','z']]);normals=np.column_stack([cloud[k] for k in ['nx','ny','nz']])
registration=json.loads((ROOT/'research/registration-cad.json').read_text());points[:,2]+=registration['ply_to_scene_matrix'][2][3]
length=np.linalg.norm(normals,axis=1);valid=length>.5;normals[valid]/=length[valid,None]
deps=bpy.context.evaluated_depsgraph_get()

def structural_kind(ob):
 if ob.type!='MESH' or ob.get('native_coverage_excluded') or ob.hide_render or ob.name.startswith('REFERENCE_') or any(c.hide_render or 'Reference' in c.name for c in ob.users_collection):return None
 if ob.name.startswith(('FLOOR_','THRESHOLD_')):return 'floor'
 if ob.name.startswith(('WALL_','COLUMN_','LivingBay_back_step')):return 'wall'
 if ob.get('category')=='Ceilings' or ob.name.startswith(('CEILING_','COVE_lip_','GRID_')):return 'ceiling'

trees={};owners={};triangle_counts={};objects_used={}
for kind in ['floor','wall','ceiling']:
 vertices=[];triangles=[];owner=[];names=[]
 for ob in bpy.data.objects:
  if structural_kind(ob)!=kind:continue
  evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();transform=evaluated.matrix_world;start=len(vertices);vs=[transform@v.co for v in mesh.vertices];vertices.extend(vs);added=0
  for triangle in mesh.loop_triangles:
   a,b,c=[vs[i] for i in triangle.vertices];normal=(b-a).cross(c-a).normalized()
   if kind=='floor' and normal.z<.985:continue
   if kind=='wall' and abs(normal.z)>.08:continue
   if kind=='ceiling' and abs(normal.z)<.985:continue
   triangles.append(tuple(start+i for i in triangle.vertices));owner.append((ob.name,str(ob.get('area','unassigned'))));added+=1
  evaluated.to_mesh_clear()
  if added:names.append(ob.name)
 trees[kind]=BVHTree.FromPolygons(vertices,triangles,all_triangles=True);owners[kind]=owner;triangle_counts[kind]=len(triangles);objects_used[kind]=names

rules={'floor':{'abs_normal_z_min':.985,'scene_z_range_m':[-.045,.045],'maximum_nearest_distance_m':.12,'minimum_absolute_normal_dot':.985},'wall':{'abs_normal_z_max':.08,'scene_z_range_m':[.40,2.30],'maximum_nearest_distance_m':.12,'minimum_absolute_normal_dot':.985},'ceiling':{'abs_normal_z_min':.985,'scene_z_range_m':[2.30,3.50],'maximum_nearest_distance_m':.08,'minimum_absolute_normal_dot':.985}}
def statistics(values):
 if not values:return {'count':0}
 values=np.array(values)
 return {'count':len(values),'median_m':float(np.median(values)),'p95_m':float(np.quantile(values,.95)),'mean_m':float(np.mean(values)),'rms_m':float(np.sqrt(np.mean(values**2))),'maximum_m':float(np.max(values))}

results={};diagnostic_names=['WALL_599_Game','COLUMN_diamond','WALL_LivingBay_North_lower','LivingBay_back_step_ledge','WALL_57D_Corridor','WALL_58D_LivingDining','WALL_591_LivingDining','WALL_Bar_observed_south_entry_return'];diagnostic_samples=[]
for kind,rule in rules.items():
 mask=valid&(points[:,2]>=rule['scene_z_range_m'][0])&(points[:,2]<=rule['scene_z_range_m'][1])
 if 'abs_normal_z_min' in rule:mask&=abs(normals[:,2])>=rule['abs_normal_z_min']
 else:mask&=abs(normals[:,2])<=rule['abs_normal_z_max']
 indices=np.flatnonzero(mask);distances=[];all_nearest=[];by_object=collections.defaultdict(list);by_area=collections.defaultdict(list);bay=[];distance_rejected=0;normal_rejected=0
 for i in indices:
  location,normal,triangle,distance=trees[kind].find_nearest(Vector(points[i]))
  if location is None:raise RuntimeError('Structural BVH unexpectedly has no triangles: '+kind)
  all_nearest.append(distance)
  if distance>rule['maximum_nearest_distance_m']:distance_rejected+=1;continue
  if abs(float(np.dot(normals[i],normal)))<rule['minimum_absolute_normal_dot']:normal_rejected+=1;continue
  name,area=owners[kind][triangle];distances.append(distance);by_object[name].append(distance);by_area[area].append(distance)
  if name in diagnostic_names:diagnostic_samples.append((i,diagnostic_names.index(name),distance))
  if points[i,0]<-7.58 and 6.5<points[i,1]<8.5:bay.append(distance)
 results[kind]={'candidate_count':len(indices),'rejected_beyond_distance':distance_rejected,'rejected_normal_mismatch':normal_rejected,'accepted':statistics(distances),'all_candidate_nearest_distances_before_rejection':statistics(all_nearest),'per_native_owner_area':{k:statistics(v) for k,v in by_area.items()},'per_native_object':{k:statistics(v) for k,v in by_object.items()},'observed_living_bay_subset':statistics(bay),'native_triangles':triangle_counts[kind],'native_objects':objects_used[kind]}
 print('NATIVE_SURFACE_DISTANCE',kind,json.dumps({k:v for k,v in results[kind].items() if k not in ['per_native_object','native_objects']}),flush=True)

report={'opened_delivery_file':str(Path(bpy.data.filepath).relative_to(ROOT)),'opened_file_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'factory_startup':True,'source':'data/point-cloud.ply','source_record_count':count,'point_transform':registration['ply_to_scene_matrix'],'sampling':'Every PLY record satisfying the documented normal and height gates; no stride or random subsampling. Euclidean nearest distance to evaluated triangles of actual saved native structural Mesh objects. Reference objects are excluded.','association_rules':rules,'results':results,'scope_and_limits':['Accepted statistics are conditional on source height/normal gates, nearest-distance gates and agreement with native triangle normals. They are not whole-cloud reconstruction error and must be read with rejected counts.','Source furniture, attached wall art, fixtures, occluded surfaces, mirror/glass returns and clutter can share structural normals. Gates remove distant clutter but cannot semantically identify every point; per-object visual comparisons remain necessary.','Native owner area denotes the object collection/area assignment; a shared partition can include faces observed from its neighboring room.','Bay subset is raw X<−7.58 and6.5<Y<8.5. CAD under-traces this region; actual native floor area and the documented CAD discrepancy are measured separately in cad-structural-measurements.json.','This script opens and inspects delivery data only; it does not modify or save the delivery file.']}
(ROOT/'output/acceptance').mkdir(parents=True,exist_ok=True)
sample_path=ROOT/'output/acceptance/structural_outlier_samples.npz'
np.savez_compressed(sample_path,samples=np.array(diagnostic_samples),object_names=np.array(diagnostic_names))
# Bind the selected source IDs and their structural distances to this producer revision.
report['structural_sample_sha256']=hashlib.sha256(sample_path.read_bytes()).hexdigest()
(ROOT/'output/acceptance/native_surface_distances.json').write_text(json.dumps(report,indent=2))
