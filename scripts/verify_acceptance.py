"""Audit or perform persisted practical edits in an isolated acceptance copy.
Blender usage: blender -b FILE --python scripts/verify_acceptance.py -- --mode audit|edit|verify
Run edit on final source; it writes only output/acceptance/edit_test.blend.
Run verify in a NEW Blender process opened on that temporary file.
"""
from pathlib import Path
import argparse,sys,json,math,hashlib
import bpy,bmesh
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
arg=argparse.ArgumentParser();arg.add_argument('--mode',choices=['audit','edit','verify'],required=True);arg.add_argument('--output',default='output/acceptance');args=arg.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=ROOT/args.output;OUT.mkdir(parents=True,exist_ok=True)
def is_reference(o):return o.name.startswith('REFERENCE_') or any('Reference' in c.name or 'Reference' in str(c.get('category','')) for c in o.users_collection)
def mesh_hash(o):
 h=hashlib.sha256()
 if o.type=='MESH':
  for v in o.data.vertices:h.update((','.join(f'{x:.8f}' for x in v.co)+';').encode())
  for p in o.data.polygons:h.update(bytes(str(tuple(p.vertices)),'utf8'))
 elif o.type=='CURVE':
  data=o.data
  h.update(str((data.dimensions,data.resolution_u,data.bevel_depth,data.bevel_resolution,data.extrude,data.fill_mode)).encode())
  for spline in data.splines:
   h.update(str((spline.type,spline.use_cyclic_u,spline.order_u,spline.resolution_u)).encode())
   for point in spline.points:
    h.update(str(tuple(round(float(x),8) for x in point.co)+(round(point.radius,8),round(point.tilt,8))).encode())
   for point in spline.bezier_points:
    h.update(str(tuple(round(float(x),8) for values in [point.co,point.handle_left,point.handle_right] for x in values)+(round(point.radius,8),round(point.tilt,8),point.handle_left_type,point.handle_right_type)).encode())
 return h.hexdigest()
def matrix(o):return [[float(v) for v in row] for row in o.matrix_world]
def digest(o):
 return {'matrix':matrix(o),'geometry':mesh_hash(o),'materials':[m.name if m else None for m in o.data.materials] if o.type in ['MESH','CURVE'] else []}
def descendants(o):
 found={o.name}
 for child in o.children:found.update(descendants(child))
 return found

def evidence_views(subjects,complex_index):
 """Fixed before/after camera recipes; all subjects are real saved native parts."""
 recipes={}
 for key in ['wall','door','furniture','material','complex']:
  name=subjects[{'material':'furniture','complex':'complex_asset'}.get(key,key)]
  ob=bpy.data.objects[name];names=descendants(ob)
  if key=='door':names.update(o.name for o in bpy.data.objects if o.name.startswith('FRAME_Game'))
  if key=='furniture':names.update(o.name for o in bpy.data.objects if o.name.startswith('LIV.DiningChair'))
  objects=[bpy.data.objects[n] for n in sorted(names)
           if bpy.data.objects[n].type in ['MESH','CURVE']
           and not bpy.data.objects[n].get('native_coverage_excluded')
           and not bpy.data.objects[n].hide_render
           and not any(c.hide_render for c in bpy.data.objects[n].users_collection)
           and not is_reference(bpy.data.objects[n])]
  points=[];deps=bpy.context.evaluated_depsgraph_get()
  for o in objects:
   ev=o.evaluated_get(deps);mesh=ev.to_mesh()
   try:points.extend(ev.matrix_world@v.co for v in mesh.vertices)
   finally:ev.to_mesh_clear()
  lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)));center=(lo+hi)/2;extent=max(hi-lo)
  direction=Vector((1,-1,1.4)).normalized()
  if key=='door':direction=Vector((.12,.08,1)).normalized();extent=max(extent,2.4)
  if key=='wall':direction=Vector((.2,-1,.4)).normalized()
  if key=='complex':
   vertex=ob.data.vertices[complex_index];center=ob.matrix_world@vertex.co;direction=(ob.matrix_world.to_3x3().inverted().transposed()@vertex.normal).normalized();extent=.15
   if direction.length<.5:direction=Vector((0,-1,0))
   tangent=direction.cross(Vector((0,0,1)))
   if tangent.length<.5:tangent=direction.cross(Vector((1,0,0)))
   # Oblique view makes the12 mm normal displacement visible in screen space.
   direction=(direction+tangent.normalized()*.8).normalized()
  recipes[key]={'objects':[o.name for o in objects],'center':list(center),'camera_location':list(center+direction*max(3,extent*2)),'ortho_scale':extent*1.42,'method':'Cycles actual material nodes' if key=='material' else ('actual mesh edge Wireframe modifier on render-only copy' if key=='complex' else 'Workbench actual native geometry'),'complex_vertex_index':complex_index if key=='complex' else None}
 return recipes

def render_edit_evidence(recipes,prefix):
 """Render temporary linked copies in a disposable scene, leaving test data untouched."""
 results={}
 for key,r in recipes.items():
  scene=bpy.data.scenes.new('Temporary acceptance visual evidence');copies=[];extra_meshes=[]
  for name in r['objects']:
   source=bpy.data.objects[name];cp=source.copy();cp.parent=None;cp.matrix_world=source.matrix_world.copy();scene.collection.objects.link(cp);cp.hide_render=False;cp.hide_viewport=False;copies.append(cp)
   if key=='complex':
    cp.data=source.data.copy();extra_meshes.append(cp.data)
    for modifier in list(cp.modifiers):cp.modifiers.remove(modifier)
    wire=cp.modifiers.new('Acceptance actual edited edge geometry','WIREFRAME');wire.thickness=.0005;wire.use_boundary=True;wire.use_replace=True
  camdata=bpy.data.cameras.new('Temporary acceptance evidence camera');cam=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(cam);cam.location=r['camera_location'];cam.rotation_euler=(Vector(r['center'])-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=r['ortho_scale'];camdata.clip_start=.001;scene.camera=cam;copies.append(cam)
  scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
  if key=='material':
   scene.render.engine='CYCLES';scene.cycles.samples=20;scene.cycles.use_denoising=True;scene.cycles.device='CPU';scene.render.threads_mode='FIXED';scene.render.threads=8
   world=bpy.data.worlds.new('Temporary evidence world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.65,.65,1);world.node_tree.nodes['Background'].inputs[1].default_value=.6;scene.world=world
   lightdata=bpy.data.lights.new('Temporary evidence area light','AREA');lightdata.energy=500;lightdata.shape='DISK';lightdata.size=4;light=bpy.data.objects.new(lightdata.name,lightdata);scene.collection.objects.link(light);light.location=Vector(r['center'])+Vector((0,-2,4));light.rotation_euler=(Vector(r['center'])-light.location).to_track_quat('-Z','Y').to_euler();copies.append(light)
  else:
   scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world=bpy.data.worlds.new('Temporary evidence world');scene.world.color=(.055,.055,.055)
  path=OUT/f'{prefix}_{key}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True,scene=scene.name);results[key]=str(path.relative_to(ROOT))
  world=scene.world
  for cp in copies:bpy.data.objects.remove(cp,do_unlink=True)
  bpy.data.scenes.remove(scene);bpy.data.cameras.remove(camdata);bpy.data.worlds.remove(world)
  if key=='material':bpy.data.lights.remove(lightdata)
  for mesh in extra_meshes:bpy.data.meshes.remove(mesh)
 return results

def audit():
 report={'opened_file':str(Path(bpy.data.filepath).relative_to(ROOT)),'opened_file_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'factory_startup':'--factory-startup' in sys.argv,'blender_version':bpy.app.version_string,'native_objects':0,'native_meshes':0,'native_curves':0,'scan_derived_complex_parts':[],'missing_images':[],'unpacked_render_images':[],'bad_material_indices':[],'negative_volume_closed_meshes':[],'inconsistent_winding_closed_meshes':[],'degenerate_faces':[],'nonmanifold_structural_solids':[],'open_surface_notes':[],'reference_render_disabled':True,'references':[],'geometry_types':{},'limitations':['Geometric intersections and omitted objects additionally require the area-by-area visual source review. Selective surface-distance statistics are in research/registration-cad.json and cad-area-surface-statistics.json.']}
 report['prior_model_archive']=[]
 for o in bpy.data.objects:
  if o.get('native_coverage_excluded'):
   assert o.hide_render or any(c.hide_render for c in o.users_collection),f'Archived prior model is visible: {o.name}'
   report['prior_model_archive'].append(o.name);continue
  if is_reference(o):
   report['references'].append({'name':o.name,'hidden_render':o.hide_render,'vertices':len(o.data.vertices) if o.type=='MESH' else 0});report['reference_render_disabled'] &= o.hide_render or all(c.hide_render for c in o.users_collection);continue
  report['native_objects']+=1;report['geometry_types'][o.type]=report['geometry_types'].get(o.type,0)+1
  if o.type=='CURVE':report['native_curves']+=1
  if o.type!='MESH':continue
  report['native_meshes']+=1
  if 'scan-derived' in str(o.get('geometry_class','')):report['scan_derived_complex_parts'].append({'name':o.name,'vertices':len(o.data.vertices),'source_triangle_count':o.get('source_triangle_count')})
  if any(p.material_index>=len(o.data.materials) for p in o.data.polygons) and len(o.data.materials):report['bad_material_indices'].append(o.name)
  bm=bmesh.new();bm.from_mesh(o.data);non=sum(not e.is_manifold for e in bm.edges);deg=sum(f.calc_area()<1e-12 for f in bm.faces)
  if deg:report['degenerate_faces'].append({'object':o.name,'count':deg})
  if not non and any(not e.is_contiguous for e in bm.edges):report['inconsistent_winding_closed_meshes'].append(o.name)
  if not non and len(bm.faces) and bm.calc_volume(signed=True)<-1e-9:report['negative_volume_closed_meshes'].append(o.name)
  structural=o.get('category') in ['Walls','Floors','Ceilings','Openings'] or o.name.startswith(('WALL_','FLOOR_','CEILING_','COLUMN_','DOOR_','FRAME_','LINTEL_'))
  if structural and non:report['nonmanifold_structural_solids'].append({'object':o.name,'count':non,'modifiers':[m.type for m in o.modifiers]})
  elif non:report['open_surface_notes'].append({'object':o.name,'count':non,'status':str(o.get('geometry_class',o.get('evidence_status',''))),'modifiers':[m.type for m in o.modifiers]})
  bm.free()
 # Check images used by native materials, excluding the original reference-only textures.
 mats={m for o in bpy.data.objects if not is_reference(o) and o.type in ['MESH','CURVE'] for m in o.data.materials if m}
 used={n.image for m in mats if m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
 for im in used:
  if im.source in ['GENERATED','VIEWER']:continue
  packed=bool(im.packed_file or getattr(im,'packed_files',None));file=Path(bpy.path.abspath(im.filepath))
  if not packed:
   if not file.is_file():report['missing_images'].append({'image':im.name,'path':im.filepath})
   report['unpacked_render_images'].append({'image':im.name,'path':im.filepath,'relative':im.filepath.startswith('//'),'exists':file.is_file()})
 report['native_render_image_count']=len(used)
 report['mechanical_checks_pass']=not any(report[k] for k in ['missing_images','bad_material_indices','negative_volume_closed_meshes','inconsistent_winding_closed_meshes','degenerate_faces','nonmanifold_structural_solids']) and report['reference_render_disabled']
 (OUT/'file_audit.json').write_text(json.dumps(report,indent=2));print('ACCEPTANCE_AUDIT',json.dumps({k:v for k,v in report.items() if k not in ['open_surface_notes','scan_derived_complex_parts']},indent=2))
 assert report['mechanical_checks_pass'],'Mechanical audit failed; inspect file_audit.json.'

def edit():
 assert Path(bpy.data.filepath).resolve()!=(OUT/'edit_test.blend').resolve(),'Run edit from the original saved final file.'
 bpy.ops.object.mode_set(mode='OBJECT') if bpy.context.object and bpy.context.object.mode!='OBJECT' else None
 names={'wall':'WALL_570_photo_game','door':'DOOR_Game_hinged_leaf','furniture':'LIV.DiningTable','furniture_surface':'LIV.DiningTable.Top'}
 for k,v in names.items():assert v in bpy.data.objects,f'Missing acceptance subject {k}: {v}'
 complexob=bpy.data.objects['FAS-GARMENT-05']
 assert complexob.type=='MESH' and len(complexob.data.vertices)>100,'Required source-constrained garment mesh is unavailable.'
 names['complex_asset']=complexob.name
 wall,door,furniture,surface=[bpy.data.objects[names[k]] for k in ['wall','door','furniture','furniture_surface']]
 expected=set([wall.name,complexob.name,surface.name]);expected.update(descendants(door));expected.update(descendants(furniture))
 baseline={o.name:digest(o) for o in bpy.data.objects if o.name not in expected}
 complex_index=len(complexob.data.vertices)//2
 untouched_vertices_sha256=hashlib.sha256(json.dumps([(v.index,list(v.co)) for v in complexob.data.vertices if v.index!=complex_index]).encode()).hexdigest()
 recipes=evidence_views(names,complex_index)
 before_images=render_edit_evidence(recipes,'edit_before')
 report={'source_file':str(Path(bpy.data.filepath).relative_to(ROOT)),'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'test_copy':str((OUT/'edit_test.blend').relative_to(ROOT)),'subjects':names,'unchanged_subject_count':len(baseline),'baseline_other_objects':baseline,'tests':{},'visual_evidence_cameras':recipes,'before_images':before_images}
 # Change local structural geometry; no generation script is needed to retain the change.
 before_wall_dimensions=list(wall.dimensions);old=[v.co.copy() for v in wall.data.vertices];maxx=max(v.x for v in old);ids=[i for i,v in enumerate(old) if v.x>maxx-.02]
 assert ids
 for i in ids:wall.data.vertices[i].co.x+=.050
 wall.data.update();report['tests']['wall_dimension']={'modified_vertex_indices':ids,'local_delta_m':[.05,0,0],'before_geometry_hash':hashlib.sha256(str([list(v) for v in old]).encode()).hexdigest(),'after_geometry_hash':mesh_hash(wall),'before_dimensions_m':before_wall_dimensions}
 # Physical hinge point remains fixed; child handle transforms follow leaf.
 door_origin=door.matrix_world.translation.copy();before=float(door.rotation_euler.z);door.rotation_euler.z+=math.radians(17);report['tests']['door_rotation']={'hinge_world_m':list(door_origin),'before_z_radians':before,'after_z_radians':float(door.rotation_euler.z),'delta_degrees':17}
 before=list(furniture.location);furniture.location+=Vector((.12,-.05,0));report['tests']['independent_furniture_move']={'before_location_m':before,'after_location_m':list(furniture.location)}
 assert surface.data.materials and surface.data.materials[0];oldmat=surface.data.materials[0];newmat=oldmat.copy();newmat.name='ACCEPTANCE temporary blue tabletop material';newmat.diffuse_color=(.08,.22,.55,1);newmat.use_nodes=True;input=newmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'];removed_links=len(input.links)
 for link in list(input.links):newmat.node_tree.links.remove(link)
 input.default_value=(.08,.22,.55,1);surface.data.materials[0]=newmat;report['tests']['furniture_material']={'before_name':oldmat.name,'after_name':newmat.name,'base_color':[.08,.22,.55,1],'incoming_base_color_links_removed':removed_links,'expected_linked_base_color':False}
 # Actual Edit Mode BMesh modification, saved and checked after a fresh process reload.
 bpy.ops.object.select_all(action='DESELECT');complexob.hide_set(False);complexob.select_set(True);bpy.context.view_layer.objects.active=complexob;bpy.ops.object.mode_set(mode='EDIT');bm=bmesh.from_edit_mesh(complexob.data);bm.verts.ensure_lookup_table();bm.normal_update()
 idx=complex_index;v=bm.verts[idx];before=list(v.co);normal=v.normal.copy()
 if normal.length<.5:normal=Vector((0,0,1))
 v.co+=normal.normalized()*.012;bmesh.update_edit_mesh(complexob.data,loop_triangles=True,destructive=False);bpy.ops.object.mode_set(mode='OBJECT')
 report['tests']['complex_Edit_Mode']={'object':complexob.name,'vertex_index':idx,'before_vertex_local_m':before,'after_vertex_local_m':list(complexob.data.vertices[idx].co),'after_geometry_hash':mesh_hash(complexob),'entered_Edit_Mode':True,'delta_length_m':(complexob.data.vertices[idx].co-Vector(before)).length}
 report['tests']['complex_Edit_Mode']['untouched_vertices_sha256']=untouched_vertices_sha256
 report['tests']['complex_Edit_Mode']['untouched_vertex_count']=len(complexob.data.vertices)-1
 bpy.context.view_layer.update();report['expected_after']={name:digest(bpy.data.objects[name]) for name in expected if name in bpy.data.objects};report['tests']['wall_dimension']['after_dimensions_m']=list(wall.dimensions)
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'edit_test.blend'));(OUT/'editing_test_state.json').write_text(json.dumps(report,indent=2));print('EDIT_TEST_SAVED',report['test_copy'],names)

def verify():
 assert Path(bpy.data.filepath).resolve()==(OUT/'edit_test.blend').resolve(),'Fresh process must open only the temporary editing-test copy.'
 r=json.loads((OUT/'editing_test_state.json').read_text());fail=[]
 for name,state in r['baseline_other_objects'].items():
  if name not in bpy.data.objects:fail.append([name,'unrelated object missing']);continue
  current=digest(bpy.data.objects[name])
  if current!=state:fail.append([name,'unrelated object changed'])
 for name,state in r['expected_after'].items():
  if name not in bpy.data.objects or digest(bpy.data.objects[name])!=state:fail.append([name,'intended edit not persisted'])
 door=bpy.data.objects[r['subjects']['door']]
 if (door.matrix_world.translation-Vector(r['tests']['door_rotation']['hinge_world_m'])).length>1e-6:fail.append(['door','hinge moved'])
 source=ROOT/r['source_file'];preserved=hashlib.sha256(source.read_bytes()).hexdigest()==r['source_sha256']
 if not preserved:fail.append(['source final file','changed during edit test'])
 surface=bpy.data.objects[r['subjects']['furniture_surface']];material=surface.data.materials[0];color=material.node_tree.nodes['Principled BSDF'].inputs['Base Color']
 if material.name!=r['tests']['furniture_material']['after_name'] or color.is_linked or any(abs(a-b)>1e-6 for a,b in zip(color.default_value,r['tests']['furniture_material']['base_color'])):fail.append(['material','copied material shader color/link state did not persist'])
 complex_test=r['tests']['complex_Edit_Mode'];complexob=bpy.data.objects[complex_test['object']]
 untouched=hashlib.sha256(json.dumps([(v.index,list(v.co)) for v in complexob.data.vertices if v.index!=complex_test['vertex_index']]).encode()).hexdigest()
 if untouched!=complex_test['untouched_vertices_sha256'] or len(complexob.data.vertices)-1!=complex_test['untouched_vertex_count']:fail.append(['complex local edit','vertices outside the single intended local edit changed'])
 complex_test['all_other_vertices_preserved_after_reopen']=untouched==complex_test['untouched_vertices_sha256'] and len(complexob.data.vertices)-1==complex_test['untouched_vertex_count']
 after_images=render_edit_evidence(r['visual_evidence_cameras'],'edit_after_reopened')
 report={'fresh_process_reopened_copy':str(Path(bpy.data.filepath).relative_to(ROOT)),'source_delivery_sha256':r['source_sha256'],'factory_startup':'--factory-startup' in sys.argv,'blender_version':bpy.app.version_string,'source_file_preserved':preserved,'unrelated_objects_checked':len(r['baseline_other_objects']),'expected_objects_checked':len(r['expected_after']),'tests':r['tests'],'before_images':r['before_images'],'after_images':after_images,'material_shader_verified':not color.is_linked and material.name==r['tests']['furniture_material']['after_name'],'failures':fail,'all_edit_tests_pass':not fail}
 (OUT/'editing_test_results.json').write_text(json.dumps(report,indent=2));print('EDIT_TEST_REOPEN_RESULTS',json.dumps(report,indent=2))
 assert report['all_edit_tests_pass'],'Persisted editing checks failed; inspect editing_test_results.json.'
{'audit':audit,'edit':edit,'verify':verify}[args.mode]()
