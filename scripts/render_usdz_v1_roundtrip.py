"""Render the actual packaged USDZ after importing into a fresh empty Blender."""
from pathlib import Path
import hashlib,json,sys,time
import bpy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/usdz-v1/roundtrip'
OUT.mkdir(exist_ok=True)
source=ROOT/'output/reconstruction_physics_v1.usdz'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
result=bpy.ops.wm.usd_import(filepath=str(source),import_materials=True,
    import_cameras=False,import_lights=True,import_textures_mode='IMPORT_PACK')
assert result=={'FINISHED'}
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==7728,len(meshes)
assert not any('REFERENCE' in o.name for o in bpy.context.scene.objects)
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file]
assert not missing,missing
sys.path.insert(0,str(ROOT/'scripts'))
from render_comparisons import setup_registered_cameras
cameras=setup_registered_cameras(ROOT)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.cycles.use_denoising=True;scene.cycles.denoising_use_gpu=True
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL';prefs.refresh_devices()
for d in prefs.devices:d.use=d.type=='METAL'
assert any(d.use for d in prefs.devices)
scene.cycles.device='GPU';scene.render.use_persistent_data=True
devices=[{'name':d.name,'type':d.type,'enabled':bool(d.use)} for d in prefs.devices]
print('USDZ_RENDER_DEVICE',json.dumps(devices),flush=True)
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
display=json.loads((ROOT/'output/usdz-v1/light-transfer.json').read_text())['display']
for key,value in display.items():setattr(scene.view_settings,key,value)
rows=[]
for station,face in [(1,'f'),(3,'f'),(4,'f'),(6,'f'),(8,'f')]:
    scene.camera=cameras[(station,face)];p=OUT/f'usdz-{station}_{face}.png';scene.render.filepath=str(p)
    start=time.monotonic();bpy.ops.render.render(write_still=True)
    rows.append({'station':station,'face':face,'path':str(p.relative_to(ROOT)),
        'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'seconds':time.monotonic()-start})
    print('USDZ_ROUNDTRIP_RENDERED',station,face,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(OUT/'render-record.json').write_text(json.dumps({'usdz_sha256':digest,'fresh_empty_blender_import':True,
    'blender_version':bpy.app.version_string,'cycles_device':scene.cycles.device,'compute_device_type':prefs.compute_device_type,'devices':devices,'native_display_settings':display,
    'mesh_count':len(meshes),'missing_packed_images':missing,'renders':rows,
    'scope':'USDZ imported PBR appearance and geometry; USD Physics is separately tested directly from its schema.'},indent=2))
print('USDZ_ROUNDTRIP_RENDER_COMPLETE',flush=True)
