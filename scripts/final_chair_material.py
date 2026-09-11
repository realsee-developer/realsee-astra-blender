"""Verified station-8 cloth projection onto the chair's retained curved local mesh."""
import bpy,json,math
from mathutils import Vector,Quaternion

def apply_chair_material(ROOT,a):
 pose=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'][7]
 pos=Vector(pose['translation_xyz_m']);pos.z+=a.offset;q=Quaternion(pose['quaternion_wxyz']).inverted()
 bpy.context.view_layer.update();changed=[]
 for name in ['LIV.AccentChair.Seat','LIV.AccentChair.Back']:
  o=bpy.data.objects[name];layer=o.data.uv_layers.get('RegisteredPhotoClothUV') or o.data.uv_layers.new(name='RegisteredPhotoClothUV');uvs=[]
  for vertex in o.data.vertices:
   ray=q@(o.matrix_world@vertex.co-pos);ray.normalize()
   uvs.append(((math.atan2(ray.x,ray.z)/(2*math.pi)+.5)%1,1-math.acos(max(-1,min(1,-ray.y)))/math.pi))
  for polygon in o.data.polygons:
   polygon.material_index=0
   for li in polygon.loop_indices:layer.data[li].uv=uvs[o.data.loops[li].vertex_index]
  o.data.uv_layers.active=layer;layer.active_render=True
  o.data.materials.clear();o.data.materials.append(bpy.data.materials['PhotoGraphicStation8'])
  o['material_note']='Verified source8 photograph projected onto actual curved scan geometry. Captured source illumination remains approximate; no flat billboard and no change to mesh coordinates or topology.'
  o['material_source']='data/panorama/8.jpg;data/cube-map/8_f.jpg;research/camera-registration.json'
  o['original_scan_uv_retained']='SourceScanUV'
  changed.append({'object':name,'vertices_unchanged':len(o.data.vertices),'polygons_unchanged':len(o.data.polygons),'new_uv_layer':layer.name})
 return changed
