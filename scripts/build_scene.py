"""Executed integrated reconstruction. Project root is always derived from this file."""
from pathlib import Path
import bpy,sys,json,math
from mathutils import Vector,Quaternion,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from native_api import NativeAPI
from build_structure import build_structure
from build_living import build_living
from build_living_details import build_living_details
from build_game import build_game
from build_corridor import build_corridor
from build_bar import build_bar
from build_fashion import build_fashion
from build_observed_details import build_observed_details
from build_surface_materials import build_surface_materials
from refine_appearance import refine_appearance
from final_structural_fixtures import apply_structural_fixtures
from final_visual_alignment import apply_visual_alignment
from final_game_illumination import apply_game_illumination
from final_bar_entry import apply_bar_entry
from final_living_detail_alignment import apply_living_detail_alignment
from final_fashion_tray import apply_fashion_tray
from final_living_identification import apply_living_identification
from final_fashion_accessories import apply_fashion_accessories
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/checkpoints/00_scan_import.blend'))
ref=bpy.data.objects['REFERENCE_HighResolution_OriginalOBJ'];reg=json.loads((ROOT/'research/registration-cad.json').read_text());offset=reg['ply_to_scene_matrix'][2][3];ref.location.z=offset
ref.hide_render=True;ref.hide_set(True);ref['source_to_scene_matrix']=json.dumps(reg['ply_to_scene_matrix']);ref['unmodified_geometry']=True
ref.users_collection[0].hide_render=True
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
arch=build_structure(ROOT)
a=NativeAPI(ROOT,ref,offset)
for fn in [build_living,build_living_details,build_game,build_corridor,build_bar,build_fashion,build_observed_details]:
 print('BUILDING',fn.__name__,flush=True);fn(ROOT,a)
# True geometric camera poses registered by image-content checks and E57 world transforms.
cc=bpy.data.collections.new('Registered_Cameras');scene.collection.children.link(cc)
bases={'f':((0,0,1),(1,0,0),(0,1,0)),'r':((1,0,0),(0,0,-1),(0,1,0)),'b':((0,0,-1),(-1,0,0),(0,1,0)),'l':((-1,0,0),(0,0,1),(0,1,0)),'u':((0,-1,0),(1,0,0),(0,0,1)),'d':((0,1,0),(1,0,0),(0,0,-1))}
for st in json.loads((ROOT/'research/camera-registration.json').read_text())['stations']:
 q=Quaternion(st['quaternion_wxyz']);pos=Vector(st['translation_xyz_m']);pos.z+=offset
 for face,(f,r,d) in bases.items():
  name=f'STATION_{st["embedded_index"]:02}_{face}';data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);cc.objects.link(ob);ob.location=pos
  right=q@Vector(r);up=-(q@Vector(d));back=-(q@Vector(f));ob.rotation_euler=Matrix((right,up,back)).transposed().to_euler();data.lens=18;data.sensor_width=36;data.sensor_fit='HORIZONTAL';data.clip_start=.015;data.clip_end=100
  ob['source']=f'data/cube-map/{st["embedded_index"]}_{face}.jpg';ob['E57_scan_GUID']=st['scan_guid'];ob['pose_status']='verified image content and projection'
scene.camera=bpy.data.objects['STATION_08_f'];scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Site ambient');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.50,.53,.59,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.15
# Physical illumination supplementation placed inside observed ceiling diffuser locations.
for area,locations,color,power in [('LivingDining',[(-5.3,7.65,2.40),(-1.7,8.0,2.4)],(1,.84,.63),140),('Game',[(-5.6,4.45,2.40)],(.50,.26,1),100),('Corridor',[(-2.2,1.2,2.68),(-2.0,4.5,2.68),(1.5,.05,2.68)],(.9,.94,1),120)]:
 a.area_collection(area+'_Illumination','photographic lighting appearance; power inferred')
 for i,loc in enumerate(locations):a.area_light(f'LIGHT_FILL_{area}_{i}',loc,power,color,1.7)
build_surface_materials(ROOT)
refine_appearance(ROOT,a)
apply_structural_fixtures(ROOT,a)
apply_visual_alignment(ROOT)
apply_game_illumination(ROOT)
apply_bar_entry(ROOT,a)
apply_living_detail_alignment(ROOT,a)
apply_fashion_tray(ROOT)
apply_living_identification(ROOT)
apply_fashion_accessories(ROOT,a)
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
# Default saved UI opens a meaningful native scene view; all scan references remain disabled.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.clip_end=100;area.spaces.active.region_3d.view_distance=16;area.spaces.active.region_3d.view_location=(-2.5,4.3,1.0);area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA'
scene['reconstruction_status']='Native site reconstruction; see acceptance-report.md for executed verification and source uncertainties'
scene['editing_instructions']='EDITING.md (also embedded as a Blender Text datablock)'
text=bpy.data.texts.new('START_HERE_Editing_Instructions');text.write((ROOT/'output/EDITING.md').read_text())
scene['source_inventory']='research/source-audit.json';scene['coverage_inventory']='research/visual-coverage.json';scene['all_source_transforms']='research/registration-cad.json;research/camera-registration.json'
bpy.ops.file.pack_all()
for image in bpy.data.images:
 if image.source=='FILE' and image.filepath:
  image.filepath=bpy.path.relpath(image.filepath,start=str(ROOT/'output'))
# All material resources packed; raw photos/points remain tracked in data/.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/reconstruction_native.blend'))
manifest=[]
for o in bpy.data.objects:
 manifest.append({'name':o.name,'type':o.type,'area':o.get('area'),'source':o.get('source'),'evidence_status':o.get('evidence_status'),'geometry_class':o.get('geometry_class'),'parent':o.parent.name if o.parent else None,'dimensions_m':list(o.dimensions),'collections':[c.name for c in o.users_collection]})
(ROOT/'output/reports/scene-manifest.json').write_text(json.dumps(manifest,indent=2))
scene.render.filepath=str(ROOT/'output/previews/integrated_station_08_f.png');bpy.ops.render.render(write_still=True)
print('INTEGRATED FILE SAVED',len(bpy.data.objects),flush=True)
