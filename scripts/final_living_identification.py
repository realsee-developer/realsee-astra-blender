"""Correct the source-identified power adapter and measured fourth living plaque.
No file saves. The prior keypad interpretation is explicitly superseded by the
full-resolution printed adapter label and three-pin mains lead in source8_d.
"""
from pathlib import Path
import bpy,math,json
from mathutils import Vector,Quaternion,Matrix

def apply_living_identification(ROOT):
 ROOT=Path(ROOT);pose=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'][7]
 camera=Vector(pose['translation_xyz_m']);camera.z+=1.396564007;q=Quaternion(pose['quaternion_wxyz']).inverted()
 def uv_project(o):
  layer=o.data.uv_layers.get('RegisteredPhotoProjection') or o.data.uv_layers.new(name='RegisteredPhotoProjection');uv=[]
  for vert in o.data.vertices:
   ray=q@(o.matrix_world@vert.co-camera);ray.normalize();uv.append(((math.atan2(ray.x,ray.z)/(2*math.pi)+.5)%1,1-math.acos(max(-1,min(1,-ray.y)))/math.pi))
  for poly in o.data.polygons:
   for li in poly.loop_indices:layer.data[li].uv=uv[o.data.loops[li].vertex_index]
  o.data.uv_layers.active=layer;layer.active_render=True
 # The framed rectangle is offset from the earlier estimated photo surface.
 o=bpy.data.objects['LIV.Plaque.4'];xs=[v.co.x for v in o.data.vertices];zs=[v.co.z for v in o.data.vertices];x0,x1=min(xs),max(xs);z0,z1=min(zs),max(zs)
 for v in o.data.vertices:v.co.x=-1.3293+(v.co.x-x0)/(x1-x0)*.3062;v.co.z=1.2794+(v.co.z-z0)/(z1-z0)*.2075
 uv_project(o);o['source_measurement']='source8_r1600px corners(1315,755),(1449,754),(1449,838),(1315,838), planeY9.165m'
 frame=bpy.data.objects['LIV.Plaque.4.Frame'];pts=[(-1.3293,9.154,1.2794),(-1.0231,9.154,1.2794),(-1.0231,9.154,1.4869),(-1.3293,9.154,1.4869)]
 for p,co in zip(frame.data.splines[0].points,pts):p.co=(*co,1)
 frame.data.bevel_depth=.008
 # Replace the false keypad features, retaining the inventory identity.
 for o in list(bpy.data.objects):
  if o.name.startswith('LIV.TableKeypad') or o.name.startswith('LIV.TablePowerAdapter'):bpy.data.objects.remove(o,do_unlink=True)
 collection=bpy.data.collections['LivingDining_ObservedDetails'];center=Vector((-1.9982,7.4595,.812))
 group=bpy.data.objects.new('LIV.TablePowerAdapter',None);collection.objects.link(group);group.location=center
 group['coverage_id']='LIV-DINING-SMALLDEVICE';group['stable_id']='LIV.TablePowerAdapter';group['area']='LivingDining_ObservedDetails';group['source']='data/cube-map/8_d.jpg';group['evidence_status']='black labeled power adapter and three-pin mains lead observed at full source resolution; earlier keypad interpretation rejected'
 bpy.context.view_layer.update()
 def mat(name,color,rough=.5,metal=0):
  m=bpy.data.materials.get(name)
  if m:return m
  m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
 black=mat('Living adapter matte black',(.008,.011,.012),.42);metal=mat('Living mains plug nickel',(.48,.5,.5),.26,.88)
 def tag(o,name,material):
  o.name=name;collection.objects.link(o);o.parent=group;o.matrix_parent_inverse=Matrix.Identity(4);o.data.materials.append(material);o['coverage_id']='LIV-DINING-SMALLDEVICE';o['stable_id']=name;o['source']='data/cube-map/8_d.jpg';o['area']='LivingDining_ObservedDetails';o['evidence_status']='observed component; body thickness and hidden cable overlap inferred';return o
 def box(name,loc,size,material,rot=0,bevel=0):
  vs=[(sx*size[0]/2,sy*size[1]/2,sz*size[2]/2) for sz in [-1,1] for sy in [-1,1] for sx in [-1,1]];fs=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
  me=bpy.data.meshes.new(name+'.Mesh');me.from_pydata(vs,[],fs);me.update();o=tag(bpy.data.objects.new(name,me),name,material);o.location=Vector(loc)-center;o.rotation_euler.z=rot
  if bevel:m=o.modifiers.new('Editable casing edge radius','BEVEL');m.width=bevel;m.segments=3
  return o
 def wire(name,pts,r=.0025):
  d=bpy.data.curves.new(name+'.Curve','CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=3;d.resolution_u=16;s=d.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
  for p,co in zip(s.bezier_points,pts):p.co=Vector(co)-center;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
  return tag(bpy.data.objects.new(name,d),name,black)
 box('LIV.TablePowerAdapter.Case',center,(.057,.064,.043),black,-.21,.006)
 # Rectified source label lies on the real native top surface, rather than keys.
 corners=[(-2.03158,7.43360,.834),(-2.01895,7.49412,.834),(-1.96250,7.48385,.834),(-1.97960,7.42628,.834)]
 me=bpy.data.meshes.new('LIV.TablePowerAdapter.PrintedLabel.Mesh');me.from_pydata([tuple(Vector(p)-center) for p in corners],[],[(0,1,2,3)]);me.update();label=tag(bpy.data.objects.new('LIV.TablePowerAdapter.PrintedLabel',me),'LIV.TablePowerAdapter.PrintedLabel',bpy.data.materials['PhotoGraphicStation8']);bpy.context.view_layer.update();uv_project(label)
 def source_ray(pixel,z):
  f=pose['cube_faces']['d'];ray=Vector(f['canonical_local_center'])+Vector(f['canonical_local_right'])*(pixel[0]/800-1)+Vector(f['canonical_local_down'])*(pixel[1]/800-1);ray=Quaternion(pose['quaternion_wxyz'])@ray
  return camera+ray*((z-camera.z)/ray.z)
 # The visible cable paths and unplugged mains head are independently editable.
 mains_pixels=[(1420,1360),(1470,1310),(1565,1278),(1510,1190),(1460,1165),(1430,1180),(1438,1245),(1460,1270),(1450,1300),(1410,1285),(1380,1230),(1370,1175)]
 mains=[source_ray(p,.795) for p in mains_pixels];mains[0].z=.812;wire('LIV.TablePowerAdapter.MainsLead',mains,.0028)
 output=[source_ray(p,.795) for p in [(1320,1430),(1300,1480),(1300,1540),(1330,1597)]];output[0].z=.812;wire('LIV.TablePowerAdapter.OutputLead',output,.0024)
 plug=source_ray((1370,1175),.802);box('LIV.TablePowerAdapter.MainsPlug.Body',plug,(.027,.020,.019),black,.68,.004)
 # Three metal blades are physical observed plug parts, not an electrical model.
 for i,(dx,dy,rz) in enumerate([(-.007,-.008,-.7),(.007,-.008,.7),(0,.005,0)],1):
  box(f'LIV.TablePowerAdapter.MainsPlug.Pin.{i}',plug+Vector((dx,dy,.014)),(.003,.010,.013),metal,rz,.0004)
 box('LIV.TablePowerAdapter.OutputStrainRelief',output[0],(.013,.012,.014),black,-.21,.002)
 bpy.context.view_layer.update()
 return {'module':'final_living_identification','plaque4_bounds_xz_m':[[-1.3293,1.2794],[-1.0231,1.4869]],'adapter_case_center_m':list(center),'adapter_case_dimensions_m':[.057,.064,.043],'inventory_id':'LIV-DINING-SMALLDEVICE','native_adapter_components':len(group.children),'source_detail':'research/visual-previews/living-small-adapter-source.jpg','observed_identity':'power adapter, printed specification label and three-pin mains lead; no keypad keys'}
