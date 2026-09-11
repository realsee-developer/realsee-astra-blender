"""Observed additions from registered station 6 and 8 cube photographs.

Dimensions of small hardware and hidden sliding-panel overlap are inferred;
visible centers are projected onto the measured wall/ceiling planes.
"""
import bpy, math, json
from mathutils import Vector, Quaternion

def build_observed_details(ROOT, a):
 # This module owns these two collections; rebuilding an isolated review copy
 # must not duplicate its previously integrated details.
 for collection_name in ['Game_ObservedDetails','LivingDining_ObservedDetails']:
  collection=bpy.data.collections.get(collection_name)
  if collection:
   for obj in list(collection.objects):bpy.data.objects.remove(obj,do_unlink=True)
 def remove_generated(prefix):
  for o in list(bpy.data.objects):
   if o.name == prefix or o.name.startswith(prefix+'.') or o.name.startswith(prefix+'_'):
    bpy.data.objects.remove(o, do_unlink=True)
 def circle_graphic(name,center,radius,station,frame=None):
  # Native triangulated disk, with photographed graphic UVs and independent rim.
  data=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'][station-1]
  pos=Vector(data['translation_xyz_m']);pos.z+=a.offset
  q=Quaternion(data['quaternion_wxyz']).inverted();c=Vector(center);n=96
  vs=[tuple(c)]+[tuple(c+Vector((radius*math.cos(i*2*math.pi/n),0,radius*math.sin(i*2*math.pi/n)))) for i in range(n)]
  uv=[]
  for p in vs:
   ray=q@(Vector(p)-pos);ray.normalize();uv.append(((math.atan2(ray.x,ray.z)/(2*math.pi)+.5)%1,1-math.acos(max(-1,min(1,-ray.y)))/math.pi))
  o=a.mesh(name,vs,[(0,i+1,(i+1)%n+1) for i in range(n)],bpy.data.materials[f'PhotoGraphicStation{station}'])
  layer=o.data.uv_layers.new(name='RegisteredPhotoProjection')
  for p in o.data.polygons:
   for li in p.loop_indices:layer.data[li].uv=uv[o.data.loops[li].vertex_index]
  o['evidence_status']='circular printed graphic; native disk with verified camera-projected photo UV'
  solid=o.modifiers.new('Editable printed board thickness','SOLIDIFY');solid.thickness=.006
  if frame:a.curve(name+'.Frame',[(x,y-.006,z) for x,y,z in vs[1:]],.006,frame,True)
  return o

 a.area_collection('Game_ObservedDetails','data/cube-map/6_u.jpg;data/cube-map/6_r.jpg;data/cube-map/6_f.jpg;data/cube-map/6_b.jpg')
 white=a.mat('Observed hardware warm white',(.79,.79,.76),.38)
 black=a.mat('Observed hardware black',(.012,.013,.017),.25)
 silver=a.mat('Observed hardware satin aluminum',(.53,.55,.57),.25,.8)
 lens=a.mat('Disco transparent violet lenses',(.30,.18,.55),.17,.25)
 # Two grille bodies are on the high central ceiling plane, running north/south.
 # Replace the earlier single grille at the low soffit with both observed units.
 remove_generated('VENT_Game')
 for i,(x,y,length,grid) in enumerate([(-4.09,4.395,.98,True),(-7.035,4.27,1.16,False)],1):
  a.group(f'VENT_Game.{i}',(x,y,2.755))
  a.box(f'VENT_Game.{i}.Recess',(x,y,2.759),(.205,length,.014),black)
  for sx in [-1,1]:a.box(f'VENT_Game.{i}.FrameLong.{sx}',(x+sx*.115,y,2.750),(.019,length+.035,.020),white,.003)
  for sy in [-1,1]:a.box(f'VENT_Game.{i}.FrameEnd.{sy}',(x,y+sy*(length+.016)/2,2.750),(.23,.019,.020),white,.003)
  for j in range(7):a.box(f'VENT_Game.{i}.SlatLong.{j}',(x-.09+j*.03,y,2.743),(.006,length-.018,.014),white,.001)
  if grid:
   for j in range(30):a.box(f'VENT_Game.{i}.SlatCross.{j}',(x,y-length/2+.025+j*(length-.05)/29,2.742),(.20,.005,.009),white)
  a.parent=None
 # The square fixture and smoke detector centers are registered from 6_r.
 for name,loc in [('LIGHT_Game_square_diffuser',(-6.659,3.621,2.740)),('ILLUM_Game_square',(-6.659,3.621,2.710)),('SMOKE_SENSOR_Game',(-6.083,4.327,2.740))]:
  if name in bpy.data.objects:bpy.data.objects[name].location=loc
 a.group('GAME.Disco',(-5.533,4.309,2.62))
 a.cyl('GAME.Disco.CeilingMount',(-5.533,4.309,2.745),.077,.035,black,40)
 a.cyl('GAME.Disco.Neck',(-5.533,4.309,2.703),.045,.066,black,32)
 center=Vector((-5.533,4.309,2.588))
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=.128,location=center);a.tag(bpy.context.object,'GAME.Disco.FacetedShell',black)
 for ring,(theta,count) in enumerate([(math.pi*.24,10),(math.pi*.43,15),(math.pi*.61,15),(math.pi*.79,11),(.95*math.pi,4)]):
  for j in range(count):
   az=j*2*math.pi/count+(ring%2)*.17;v=Vector((math.sin(theta)*math.cos(az),math.sin(theta)*math.sin(az),math.cos(theta)))
   o=a.cyl(f'GAME.Disco.LensRim.{ring}.{j}',center+v*.126,.0135,.004,silver,16);o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
   o=a.cyl(f'GAME.Disco.Lens.{ring}.{j}',center+v*.129,.0105,.004,lens,16);o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
 a.parent=None
 a.group('GAME.Sprinkler',(-6.682,4.333,2.72))
 a.cyl('GAME.Sprinkler.Escutcheon',(-6.682,4.333,2.753),.027,.010,silver,32)
 a.cyl('GAME.Sprinkler.Stem',(-6.682,4.333,2.728),.010,.044,silver,20)
 a.cyl('GAME.Sprinkler.Deflector',(-6.682,4.333,2.698),.020,.006,silver,20)
 for d in [-1,1]:a.rod(f'GAME.Sprinkler.Yoke.{d}',(-6.682+d*.014,4.333,2.742),(-6.682+d*.014,4.333,2.702),.003,silver)
 a.parent=None
 # Four adjacent rocker buttons, two actual instruction plaques, and two sockets.
 remove_generated('GAME.ControlSwitch')
 for j in range(4):
  yy=4.270-j*.030;a.box(f'GAME.ControlSwitch.{j+1}',(-3.55,yy,1.33),(.015,.029,.091),white,.004)
  a.box(f'GAME.ControlSwitch.{j+1}.Indicator',(-3.540,yy,1.356),(.003,.004,.008),silver,.001)
 a.photo_plane('GAME.ControlSign.Upper',(-3.545,4.076,1.333),(0,-.14,0),(0,0,.092),6)
 a.photo_plane('GAME.ControlSign.Lower',(-3.544,4.076,1.228),(0,-.15,0),(0,0,.104),6)
 a.box('GAME.Plaque.East.Frame',(-3.551,5.134,1.356),(.022,.205,.205),black,.004)
 a.box('GAME.Plaque.East.Insert',(-3.536,5.134,1.356),(.008,.185,.185),a.mat('Game tan information plaque',(.45,.29,.16),.7),.001)
 for i,(x,z) in enumerate([(-5.466,.964),(-5.580,.972)],1):
  a.group(f'GAME.Outlet.{i}',(x,2.913,z));a.box(f'GAME.Outlet.{i}.Plate',(x,2.925,z),(.084,.012,.084),white,.004)
  for dx,dz in [(-.014,.019),(.014,.019),(-.017,-.019),(.017,-.019),(0,-.005)]:
   o=a.box(f'GAME.Outlet.{i}.Socket.{dx}.{dz}',(x+dx,2.933,z+dz),(.0035,.002,.010),black,.001)
   if dz<-.01:o.rotation_euler.y=math.copysign(.40,dx)
  a.parent=None

 a.area_collection('LivingDining_ObservedDetails','data/cube-map/8_f.jpg;data/cube-map/8_r.jpg;data/cube-map/8_d.jpg')
 # The original rough boxes clipped the forward chair seat and selected the
 # curtain above its low back. PLY and source8_f constrain these local surfaces.
 remove_generated('LIV.AccentChair')
 a.group('LIV.AccentChair',(-7.14,8.54,.32))
 a.scan_part('LIV.AccentChair.Seat',[[-7.46,8.14,.245],[-6.70,8.78,.455]])
 a.scan_part('LIV.AccentChair.Back',[[-7.49,8.70,.405],[-7.03,9.145,.775]])
 chairframe=a.mat('Accent chair dark bentwood',(.13,.045,.014),.44)
 back=Vector((-.46,.89,0)).normalized();right=Vector((back.y,-back.x,0));origin=Vector((-7.14,8.54,0))
 for side in [-1,1]:
  def P(t,z):
   p=origin+right*(side*.235)+back*t;p.z=z;return tuple(p)
  a.curve(f'LIV.AccentChair.Frame.Side.{side}',[P(-.36,.025),P(-.32,.28),P(-.20,.31),P(.22,.39),P(.42,.67),P(.39,.735)],.014,chairframe)
  a.curve(f'LIV.AccentChair.Frame.RearFoot.{side}',[P(.18,.375),P(.30,.025)],.015,chairframe)
 a.parent=None
 # Small south-wall touchscreen; source8_l verifies it beside the open doorway.
 remove_generated('LIV.Switch.1')
 a.box('LIV.Switch.1.Bezel',(-2.130,6.001,1.345),(.078,.015,.074),black,.003)
 a.photo_plane('LIV.Switch.1.Screen',(-2.130,6.010,1.345),(.062,0,0),(0,0,.060),8)
 for name in ['LIV.Art.FlowerVase','LIV.Art.CatCup','LIV.Art.OrangeVase','LIV.Art.PinkFlower','LIV.Art.CircularFlowers','LIV.CatWallShelf.Graphic','LIV.TablePhone']:remove_generated(name)
 rays=json.loads((ROOT/'research/living-art-source-rays.json').read_text())
 for name in ['FlowerVase','CatCup','OrangeVase','PinkFlower']:
  record=rays[name];center=record['center'];w,_,h=record['dimensions']
  a.box('LIV.Art.'+name+'.Backing',(center[0],center[1]+.009,center[2]),(w,.016,h),black,.003)
  o=a.photo_plane('LIV.Art.'+name,center,(-w,0,0),(0,0,h),8,black)
  o['measurement_record']='research/living-art-source-rays.json';o['placement_method']='registered source border rays intersect measured north wall'
 circle_graphic('LIV.Art.CircularFlowers',(-4.1217,9.168,1.6261),.1915,8,black)
 circle_graphic('LIV.CatWallShelf.Graphic',(-2.9972,9.160,1.6975),.193,8)
 a.group('LIV.TableDeviceStack',(-2.05,8.44,.82))
 for i,(dx,dy,ang) in enumerate([(0,0,-.08),(.018,.016,.03),(.030,.025,-.04)]):
  a.box(f'LIV.TableDeviceStack.Device.{i+1}',(-2.05+dx,8.44+dy,.802+i*.016),(.265,.205,.014),black,.006,ang)
 a.box('LIV.TableDeviceStack.PowerBlock',(-2.04,8.49,.858),(.12,.060,.034),black,.008)
 a.curve('LIV.TableDeviceStack.Cable',[(-2.04,8.49,.88),(-2.22,8.61,.85),(-2.25,8.36,.84),(-1.77,8.22,.802),(-1.72,8.42,.802),(-1.99,8.50,.86)],.004,black)
 a.parent=None
 a.group('LIV.TableKeypad',(-2.085,7.46,.81))
 a.box('LIV.TableKeypad.Body',(-2.085,7.46,.808),(.071,.114,.020),black,.004)
 for row in range(4):
  for col in range(3):a.box(f'LIV.TableKeypad.Key.{row}.{col}',(-2.108+col*.021,7.425+row*.023,.820),(.017,.018,.003),silver,.001)
 a.curve('LIV.TableKeypad.Lead',[(-2.085,7.52,.813),(-2.10,7.56,.805),(-2.14,7.53,.806),(-2.15,7.60,.817)],.003,black)
 a.parent=None
 # The PLY resolves the broad bay behind the glass. Its actual flat mountain
 # print fronts the two observed backwall distance bands; no terrain is modeled.
 remove_generated('LIV.Niche.Landscape')
 a.box('LIV.Niche.Landscape.Backing',(-8.712,7.555,1.865),(.018,1.31,1.13),white,.003)
 landscape=a.photo_plane('LIV.Niche.Landscape',(-8.700,7.555,1.865),(0,1.31,0),(0,0,1.13),8)
 landscape['evidence_status']='flat printed landscape from source8_f, native backing; broad bay width/depth confirmed by PLY; concealed mounting gap over stepped rear wall inferred'
 landscape['source_measurement']='research/cad-living-niche-ply.png; source8_f lower print edge y820/1600 intersects X=-8.72 atZ1.294m'
 for yy in [7.03,8.05]:
  bracket=a.rod(f'LIV.Niche.Landscape.HiddenMount.{yy}',(-9.005,yy,1.44),(-8.724,yy,1.44),.007,silver)
  bracket['evidence_status']='unobserved local panel mounting inferred to support the flat photograph over measured stepped wall'
 bag=bpy.data.objects.get('LIV.Niche.BlackBag')
 if bag:bag.location=(-8.80,7.09,.12)
 # White sliding assembly is visible ahead of the CAD niche. Hidden overlap is
 # inferred; panels are separate so its opening can be edited without remodeling.
 frame=a.mat('Living sliding frame powdercoat',(.84,.84,.81),.23,.25)
 glass=a.mat('Living clear partition glass',(.91,.97,.98),.045)
 bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45
 a.group('LIV.Sliding.Assembly',(-7.475,7.405,1.195))
 for yy in [6.86,7.955]:a.box(f'LIV.Sliding.OuterJamb.{yy}',(-7.475,yy,1.196),(.080,.038,2.34),frame,.004)
 for z in [.030,2.363]:a.box(f'LIV.Sliding.Track.{z}',(-7.475,7.4075,z),(.09,1.133,.045),frame,.004)
 a.parent=None
 # Right sliding leaf; left leaf is stacked behind curtain at current open state.
 for i,(x,y0,y1) in enumerate([(-7.45,7.68,8.235),(-7.505,6.32,6.875)],1):
  a.group(f'LIV.Sliding.Panel.{i}',(x,(y0+y1)/2,1.20))
  for yy in [y0,y1]:a.box(f'LIV.Sliding.Panel.{i}.Stile.{yy}',(x,yy,1.195),(.038,.029,2.29),frame,.003)
  for z in [.056,2.328]:a.box(f'LIV.Sliding.Panel.{i}.Rail.{z}',(x,(y0+y1)/2,z),(.038,y1-y0,.036),frame,.003)
  a.box(f'LIV.Sliding.Panel.{i}.Glass',(x,(y0+y1)/2,1.193),(.005,y1-y0-.037,2.235),glass)
  hy=y0+.029 if i==1 else y1-.029
  a.box(f'LIV.Sliding.Panel.{i}.HandleBack',(x+.027,hy,1.010),(.014,.020,.127),silver,.003)
  a.rod(f'LIV.Sliding.Panel.{i}.Handle',(x+.039,hy,.965),(x+.039,hy,1.055),.005,frame)
  a.parent=None
 # Match the photographed exposed opening; keep both cloth objects editable.
 for name,newedge in [('LIV.Curtain.1',6.85),('LIV.Curtain.2',7.97)]:
  o=bpy.data.objects.get(name)
  if o:
   coords=[v.co.y for v in o.data.vertices];lo=min(coords);hi=max(coords)
   nlo,nhi=(lo,newedge) if name.endswith('1') else (newedge,hi)
   for v in o.data.vertices:v.co.y=nlo+(v.co.y-lo)/(hi-lo)*(nhi-nlo)
 from final_chair_material import apply_chair_material
 apply_chair_material(ROOT,a)
 return {'module':'observed_details','source_stations':[6,8],'added_categories':['2 game ceiling vents','disco head with individual lenses','sprinkler','4 switches','2 outlets','2 control signs','east plaque','2 circular graphics','device stack','keypad','sliding partition']}
