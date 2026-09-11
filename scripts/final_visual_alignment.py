"""Bounded source-measured corrections, applied after every furniture refinement.

No file saves. All generated hardware remains independently editable and parented
in the hinged door's local frame. Input/reference objects are never modified.
"""
from pathlib import Path
import bpy, math, json
from mathutils import Vector, Quaternion, Matrix


def apply_visual_alignment(ROOT):
 ROOT=Path(ROOT)
 poses=json.loads((ROOT/'research/camera-registration.json').read_text())['stations']
 offset=1.396564007
 def material(name,color,roughness=.5,metallic=0):
  m=bpy.data.materials.get(name)
  if m:return m
  m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
  bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness;bs.inputs['Metallic'].default_value=metallic
  return m
 black=material('Observed hardware black',(.008,.009,.011),.32,.35)
 silver=material('Observed door key metal',(.40,.43,.44),.24,.9)
 tan=material('Game tan information plaque',(.45,.29,.16),.7)
 def remove(name):
  o=bpy.data.objects.get(name)
  if o:bpy.data.objects.remove(o,do_unlink=True)
 def tag(o,name,collection,source,mat,parent=None):
  o.name=name
  for c in list(o.users_collection):c.objects.unlink(o)
  collection.objects.link(o);o.data.materials.append(mat)
  o['stable_id']=name;o['source']=source;o['area']='Game_ObservedDetails' if 'Game' in collection.name else 'LivingDining_ObservedDetails'
  o['evidence_status']='visible photographed component; local thickness and key teeth inferred'
  if parent:o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4)
  return o
 def box(name,loc,size,collection,source,mat,parent=None,bevel=0):
  remove(name);bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.scale=size
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  tag(o,name,collection,source,mat,parent);o.location=loc
  if bevel:m=o.modifiers.new('Editable edge radius','BEVEL');m.width=bevel;m.segments=3
  return o
 def cylinder(name,loc,radius,depth,collection,source,mat,parent=None):
  remove(name);bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth);o=bpy.context.object
  tag(o,name,collection,source,mat,parent);o.location=loc;o.rotation_euler.x=math.pi/2
  for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
  return o
 def curve(name,pts,radius,collection,source,mat,parent=None,cyclic=False):
  remove(name);d=bpy.data.curves.new(name+'.Curve','CURVE');d.dimensions='3D';d.bevel_depth=radius;d.bevel_resolution=3;s=d.splines.new('POLY');s.points.add(len(pts)-1)
  for p,co in zip(s.points,pts):p.co=(*co,1)
  s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,d);collection.objects.link(o);tag(o,name,collection,source,mat,parent);return o
 # Both vents were measured from registered cube rays at the actual ceiling.
 vents={}
 for label,target in [('entry',(-4.573,1.237,2.758)),('far',(-7.424,1.225,2.758))]:
  frame=bpy.data.objects[f'FAS-VENT-{label}_frame'];delta=Vector(target)-frame.location.copy()
  names=[]
  for o in bpy.data.objects:
   if o.name.startswith(f'FAS-VENT-{label}'):
    o.location+=delta;o['alignment_source']='data/cube-map/3_u.jpg' if label=='entry' else 'data/cube-map/3_f.jpg';names.append(o.name)
  vents[label]={'center_m':target,'components':len(names)}
 # Source3_f detector center ray; preserve the modeled underside height.
 smoke=bpy.data.objects['FAS-SMOKE'];delta=Vector((-6.738,1.200,smoke.location.z))-smoke.location.copy()
 for o in bpy.data.objects:
  if o.name.startswith('FAS-SMOKE'):o.location+=delta;o['alignment_source']='source3_f1600px(549,85); XY measured at ceilingZ2.758m'
 # South plaque is a tan insert within a black frame; its prior estimated
 # center was 0.42 m east and 0.14 m low relative to the photographed rectangle.
 plaque=bpy.data.objects['GAME.ControlPlate.South'];plaque.location=(-5.992,2.925,1.362);plaque.dimensions=(.286,.018,.200)
 plaque['source_measurement']='source6_f1600px border(1065,768),(1148,777),(1145,863),(1063,861), planeY2.925m'
 box('GAME.ControlPlate.South.Insert',(-5.992,2.938,1.362),(.262,.006,.176),plaque.users_collection[0],'data/cube-map/6_f.jpg',tan,bevel=.001)
 east=bpy.data.objects['GAME.Plaque.East.Insert'];east.location.x=-3.570;east['alignment_note']='Insert exposed toward negative X into the photographed room, ahead of frame.'
 # Cycles verification shows the second east emitter needs a 17 mm room-side
 # offset to remain exposed. Preserve its measured vertical endpoints and Y.
 east_led=bpy.data.objects['GAME.WallLED.East.2'];east_led.location.x=-3.570
 east_led['alignment_note']='Final source6_b visibility check: 17mm room-side offset exposes second emitter; measured Y and Z unchanged.'
 # Reproject the small green framed print using its actual station8 footprint.
 original=bpy.data.objects['LIV.GreenFrame'];collection=original.users_collection[0]
 remove('LIV.GreenFrame');remove('LIV.GreenFrame.Frame')
 center=Vector((-.52,7.4856,1.4287));u=Vector((0,-.2888,0));v=Vector((0,0,.1964));station=poses[7]
 pos=Vector(station['translation_xyz_m']);pos.z+=offset;q=Quaternion(station['quaternion_wxyz']).inverted()
 verts=[];uvs=[];faces=[];n=12
 for j in range(n+1):
  for i in range(n+1):
   p=center+u*(i/n-.5)+v*(j/n-.5);ray=q@(p-pos);ray.normalize();verts.append(tuple(p));uvs.append(((math.atan2(ray.x,ray.z)/(2*math.pi)+.5)%1,1-math.acos(max(-1,min(1,-ray.y)))/math.pi))
 for j in range(n):
  for i in range(n):k=j*(n+1)+i;faces.append((k,k+1,k+n+2,k+n+1))
 me=bpy.data.meshes.new('LIV.GreenFrame.Mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('LIV.GreenFrame',me);collection.objects.link(o)
 tag(o,'LIV.GreenFrame',collection,'data/cube-map/8_b.jpg',bpy.data.materials['PhotoGraphicStation8'])
 uv=me.uv_layers.new(name='RegisteredPhotoProjection')
 for p in me.polygons:
  for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
 o['evidence_status']='planar printed graphic with source8 registered UV; source border rays determine position and dimensions'
 o['source_measurement']='source8_b1600px TL(644,733),BR(765,817), planeX-0.52m'
 corners=[tuple(p+Vector((-.008,0,0))) for p in [center-u/2-v/2,center+u/2-v/2,center+u/2+v/2,center-u/2+v/2]]
 curve('LIV.GreenFrame.Frame',corners,.009,collection,'data/cube-map/8_b.jpg',black,cyclic=True)
 box('LIV.GreenFrame.Backing',(-.512,7.4856,1.4287),(.012,.290,.198),collection,'data/cube-map/8_b.jpg',black)
 # All appliance children must already exist when the assembly is turned.
 appliance=bpy.data.objects['LIV.CylindricalAppliance'];appliance.rotation_euler.z=-math.pi/2
 appliance['orientation_evidence']='source8_b: visible dark front panel faces west (-X); group rotated -90deg about native local Z after all grille and control children exist'
 # Visible doors have round lever rosettes plus lower key cylinders/rings.
 # Keys are modeled only on the camera-visible side; concealed hardware is not duplicated.
 hardware={}
 bpy.context.view_layer.update()
 for name,number,face in [('Game',6,'f'),('LivingDining',8,'b')]:
  door=bpy.data.objects[f'DOOR_{name}_hinged_leaf'];collection=door.users_collection[0];source=f'data/cube-map/{number}_{face}.jpg'
  width=float(door['clear_width_m']);hx=-width+.05
  for side in [-1,1]:
   cylinder(f'HANDLE_ROSETTE_{name}{side}',(hx,side*.028,1.015),.025,.014,collection,source,black,door)
  cp=Vector(poses[number-1]['translation_xyz_m']);cp.z+=offset;side=1 if (door.matrix_world.inverted()@cp).y>=0 else -1
  cylinder(f'HANDLE_{name}.LockRosette',(hx,side*.030,.915),.023,.016,collection,source,black,door)
  cylinder(f'HANDLE_{name}.LockCylinder',(hx,side*.040,.915),.009,.007,collection,source,silver,door)
  box(f'HANDLE_{name}.Key.InsertedBlade',(hx,side*.057,.915),(.006,.034,.0025),collection,source,silver,door)
  # Silver bow/ring and two independently editable hanging keys; the specific
  # key-bitting pattern is unresolvable at source resolution and is inferred.
  pts=[(hx+.016*math.cos(t*math.tau/40),side*.076,.897+.016*math.sin(t*math.tau/40)) for t in range(40)]
  curve(f'HANDLE_{name}.Key.Ring',pts,.0018,collection,source,silver,door,True)
  for i,dx in enumerate([-.010,.009],1):
   yy=side*(.078+i*.002)
   pts=[(hx+dx+.008*math.cos(t*math.tau/24),yy,.881+.008*math.sin(t*math.tau/24)) for t in range(24)]
   curve(f'HANDLE_{name}.Key.{i}.Bow',pts,.002,collection,source,silver,door,True)
   box(f'HANDLE_{name}.Key.{i}.Shaft',(hx+dx,yy,.852),(.005,.0026,.046),collection,source,silver,door)
   for k in range(3):box(f'HANDLE_{name}.Key.{i}.Tooth.{k}',(hx+dx+.003,yy,.833+k*.006),(.007,.0026,.003),collection,source,silver,door)
  hardware[name]={'parent':door.name,'camera_visible_side_local_Y':side,'keys':2,'source':source,'uncertainty':'Fine bitting and exact occluded key overlap inferred; observed ring and dangling metal silhouette retained.'}
 bpy.context.view_layer.update()
 return {'module':'final_visual_alignment','vent_centers_m':vents,'south_plaque_center_m':list(plaque.location),'green_frame_center_m':list(center),'appliance_rotation_z_deg':-90,'smoke_detector_center_m':list(smoke.location),'east_second_LED_X_m':-3.570,'door_hardware':hardware}
