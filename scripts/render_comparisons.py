"""Registered source/native comparison rendering, without saving the delivery file.
Blender: -b output/reconstruction_native.blend --python scripts/render_comparisons.py -- --stage quick|full|structure
Camera-only integration: setup_registered_cameras(PROJECT_ROOT).
Contacts use bundled Pillow if available through the analysis environment afterwards:
  .venv-analysis/bin/python scripts/render_comparison_contacts.py
"""
from pathlib import Path
import bpy,math,json,sys,argparse,time,hashlib
from mathutils import Vector,Quaternion,Matrix

def setup_registered_cameras(ROOT):
 ROOT=Path(ROOT);poses=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'];reg=json.loads((ROOT/'research/registration-cad.json').read_text());offset=reg['ply_to_scene_matrix'][2][3]
 coll=bpy.data.collections.get('Registered_Source_Cameras')
 if not coll:coll=bpy.data.collections.new('Registered_Source_Cameras');bpy.context.scene.collection.children.link(coll)
 cameras={}
 for i,p in enumerate(poses,1):
  q=Quaternion(p['quaternion_wxyz']);location=Vector(p['translation_xyz_m']);location.z+=offset
  for face in ['f','r','b','l','u','d']:
   f=p['cube_faces'][face];assert not f['horizontal_mirror'] and f['rotation_ccw_quarters']==0,'Observed cube basis changed; update registered camera transform explicitly.'
   forward=q@Vector(f['canonical_local_center']);right=q@Vector(f['canonical_local_right']);up=-(q@Vector(f['canonical_local_down']));rotation=Matrix((right,up,-forward)).transposed().to_quaternion()
   name=f'CAM_P{i:02}_{face}';ob=bpy.data.objects.get(name)
   if not ob:
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);coll.objects.link(ob)
   ob.location=location;ob.rotation_mode='QUATERNION';ob.rotation_quaternion=rotation;ob.data.type='PERSP';ob.data.lens_unit='FOV';ob.data.angle=math.radians(90);ob.data.sensor_fit='HORIZONTAL';ob.data.clip_start=.012;ob.data.clip_end=100
   ob['source']=f['source'];ob['scan_guid']=p['scan_guid'];ob['image_guid']=p['image_guid'];ob['cube_match_MAE_255']=f['RGB_MAE_255'];ob['registration']='E57 pose quaternion and content-verified cube basis';cameras[(i,face)]=ob
 return cameras

def render_main():
 ROOT=Path(__file__).resolve().parents[1]
 parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['quick','full','structure','solid'],default='quick');parser.add_argument('--station',type=int,default=0);parser.add_argument('--output',default='output/previews/comparisons');parser.add_argument('--device',choices=['CPU','GPU'],default='CPU');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 P=ROOT/args.output;P.mkdir(parents=True,exist_ok=True)
 scene=bpy.context.scene;original_file=bpy.data.filepath
 assert original_file,'Must open a saved scene first.'
 source_sha256=hashlib.sha256(Path(original_file).read_bytes()).hexdigest()
 for o in bpy.data.objects:
  if o.name.startswith('REFERENCE_') or any('Reference' in c.name for c in o.users_collection):o.hide_render=True;o.hide_set(True)
 scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100;scene.render.film_transparent=False;scene.render.engine='CYCLES';scene.cycles.samples=8 if args.stage=='quick' else 24;scene.cycles.use_denoising=True;scene.cycles.preview_samples=8;scene.render.resolution_x=400 if args.stage=='quick' else 1000;scene.render.resolution_y=scene.render.resolution_x
 scene.cycles.device=args.device;scene.render.threads_mode='FIXED';scene.render.threads=8
 if args.device=='GPU':
  prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.refresh_devices()
  for device in prefs.devices:device.use=device.type=='METAL'
  assert any(device.use for device in prefs.devices),'No enabled local Metal device.'
  scene.cycles.denoising_use_gpu=True;scene.render.use_persistent_data=True
 cameras=setup_registered_cameras(ROOT);records=[]
 if args.stage in ['quick','full','solid']:
  if args.stage=='solid':
   scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=900;scene.render.resolution_y=900;scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.73,.75,.77);scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
  faces=['f','r'] if args.stage in ['quick','solid'] else ['f','r','b','l','u','d'];stations=[args.station] if args.station else list(range(1,9))
  for i in stations:
   for face in faces:
    scene.camera=cameras[(i,face)];prefix='solid' if args.stage=='solid' else 'native';path=P/f'{prefix}-{i}_{face}.png';scene.render.filepath=str(path);start=time.time();bpy.ops.render.render(write_still=True)
    records.append({'station':i,'face':face,'source':f'data/cube-map/{i}_{face}.jpg','native':str(path.relative_to(ROOT)),'seconds':round(time.time()-start,3),'resolution':scene.render.resolution_x,'reference_disabled':True,'engine':scene.render.engine,'samples':scene.cycles.samples});print('COMPARISON_RENDERED',json.dumps(records[-1]),flush=True)
 else:
  # Structural evidence uses actual saved geometry. Only overhead parts are hidden for the plan.
  scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.73,.75,.77);scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.show_object_outline=True;scene.render.resolution_x=1600;scene.render.resolution_y=1200
  scene.world=scene.world.copy();scene.world.color=(1,1,1);scene.display.shading.background_type='WORLD';scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
  orthodata=bpy.data.cameras.new('ComparisonOrthographic');co=bpy.data.objects.new('ComparisonOrthographic',orthodata);scene.collection.objects.link(co);orthodata.type='ORTHO';orthodata.ortho_scale=16;scene.camera=co
  hidden=[]
  for o in bpy.data.objects:
   if o.get('category') in ['Ceilings','Lighting','Services'] or o.name.startswith(('CEILING_','COVE_','GRID_','TRACK_','VENT_','LIGHT_','ILLUM_')):
    if not o.hide_render:hidden.append(o);o.hide_render=True
  co.location=(-2.5,4.4,20);co.rotation_euler=(0,0,0);scene.render.filepath=str(P/'native-structure-plan-solid.png');bpy.ops.render.render(write_still=True);records.append({'view':'plan-solid','path':str(Path(scene.render.filepath).relative_to(ROOT)),'overhead_objects_hidden':len(hidden)})
  # Render actual edge geometry using temporary native Wireframe modifiers on copies.
  wire_copies=[];wire_originals=[]
  wiremat=bpy.data.materials.new('Temporary QA dark wire');wiremat.diffuse_color=(.015,.035,.055,1)
  for o in list(bpy.data.objects):
   if o.type!='MESH' or o.hide_render or any(c.hide_render for c in o.users_collection):continue
   cp=o.copy();cp.data=o.data.copy();scene.collection.objects.link(cp);cp.name='QA_WIRE_'+o.name;cp.data.materials.clear();cp.data.materials.append(wiremat)
   for p in cp.data.polygons:p.material_index=0
   # Keep real opening/overlap corrections in the control-mesh wire view.
   for m in list(cp.modifiers):
    if m.type!='BOOLEAN':cp.modifiers.remove(m)
   wf=cp.modifiers.new('QA actual editable mesh edges','WIREFRAME');wf.thickness=.006;wf.use_replace=True;wf.use_boundary=True;wf.use_even_offset=False
   wire_copies.append(cp);wire_originals.append(o);o.hide_render=True
  scene.display.shading.light='FLAT';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.02,.025,.035);scene.display.shading.show_cavity=False;scene.display.shading.show_shadows=False;scene.render.filepath=str(P/'native-structure-plan-wire.png');bpy.ops.render.render(write_still=True);records.append({'view':'plan-wire','path':str(Path(scene.render.filepath).relative_to(ROOT)),'overhead_objects_hidden':len(hidden),'method':'Editable control-mesh edges with native Boolean openings/overlap corrections retained; other modifiers omitted before temporary Wireframe; flat dark edges on white, delivery data unchanged'})
  for o in wire_copies:bpy.data.objects.remove(o,do_unlink=True)
  for o in wire_originals:o.hide_render=False
  scene.display.shading.light='STUDIO';scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.73,.75,.77);scene.display.shading.show_cavity=True;scene.display.shading.show_shadows=True
  for o in hidden:o.hide_render=False
  for name,loc in [('south',(-2.5,-16,1.8)),('north',(-2.5,24,1.8)),('west',(-24,4.4,1.8)),('east',(20,4.4,1.8))]:
   target=Vector((-2.5,4.4,1.8));co.location=loc;co.rotation_euler=(target-Vector(loc)).to_track_quat('-Z','Y').to_euler();orthodata.ortho_scale=16;scene.render.filepath=str(P/f'native-elevation-{name}.png');bpy.ops.render.render(write_still=True);records.append({'view':name+'-elevation','path':str(Path(scene.render.filepath).relative_to(ROOT)),'reference_disabled':True,'ceiling_visible':True})
 for row in records:
  row['image_sha256']=hashlib.sha256((ROOT/row.get('native',row.get('path'))).read_bytes()).hexdigest()
 final_sha256=hashlib.sha256(Path(original_file).read_bytes()).hexdigest()
 record_path=P/f'render-record-{args.stage}{"-"+str(args.station) if args.station else ""}.json';record_path.write_text(json.dumps({'opened_file':str(Path(original_file).relative_to(ROOT)),'opened_file_sha256':source_sha256,'delivery_sha256_after_render':final_sha256,'factory_startup':'--factory-startup' in sys.argv,'delivery_file_preserved':source_sha256==final_sha256,'saved_delivery_file':False,'renders':records},indent=2));assert source_sha256==final_sha256,'Delivery changed during render batch; this proof belongs to the earlier revision.';print('COMPARISON_BATCH_COMPLETE',str(record_path.relative_to(ROOT)),flush=True)
if __name__=='__main__':render_main()
