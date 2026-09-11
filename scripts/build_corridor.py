import math,bpy,json
from mathutils import Vector

def build_corridor(ROOT,a):
 a.area_collection('Corridor_Contents','data/cube-map/1_*.jpg;2_*.jpg;5_*.jpg;7_*.jpg;data/point-cloud.ply')
 black=a.mat('Roadcase black phenolic',(.014,.018,.02),.62);chrome=a.mat('Roadcase aluminum edging',(.46,.5,.55),.25,.8);wood=a.mat('Gallery natural frame',(.42,.24,.095),.52);dark=a.mat('Gallery black frames',(.015,.014,.013),.43);tan=a.mat('Gallery blank labels',(.5,.34,.16),.8)
 # Individual front panels, lid, hinges, reinforcement rails, catches, handles and four casters.
 a.group('COR.Roadcase',(-2.51,-.19,0));a.box('COR.Roadcase.Body',(-2.51,-.21,.425),(1.55,.49,.63),black,.012)
 a.box('COR.Roadcase.Lid',(-2.51,-.21,.95),(1.55,.49,.38),black,.012)
 for x in [-3.28,-1.74]:
  for y in [-.453,.033]:a.rod(f'COR.Roadcase.CornerRail.{x}.{y}',(x,y,.12),(x,y,1.13),.012,chrome)
 for z in [.14,.745,.766,1.14]:
  for y in [-.465,.045]:a.rod(f'COR.Roadcase.HorizontalRail.{z}.{y}',(-3.28,y,z),(-1.74,y,z),.014,chrome)
  for x in [-3.29,-1.73]:a.rod(f'COR.Roadcase.SideRail.{z}.{x}',(x,-.45,z),(x,.03,z),.013,chrome)
 for x in [-3.14,-1.89]:
  a.box(f'COR.Roadcase.Catch.{x}',(x,.057,.756),(.082,.023,.13),chrome,.014)
  a.box(f'COR.Roadcase.CatchPivot.{x}',(x,.074,.756),(.04,.017,.035),black,.005)
 for z in [.52,1.095]:
  a.box(f'COR.Roadcase.HandleRecess.{z}',(-2.52,.057,z),(.25,.015,.10),chrome,.015)
  a.rod(f'COR.Roadcase.Handle.{z}',(-2.62,.089,z),(-2.42,.089,z),.012,chrome)
 for x in [-3.13,-1.91]:
  for y in [-.37,-.04]:
   a.cyl(f'COR.Roadcase.Caster.{x}.{y}',(x,y,.069),.053,.04,black,20,(math.pi/2,0,0));a.box(f'COR.Roadcase.CasterFork.{x}.{y}',(x,y,.10),(.034,.04,.06),chrome,.004)
 a.parent=None
 # Blue safety hardhat: open hemispherical shell, native thickness, thin elliptical visor brim.
 blue=a.mat('Safety blue hardhat',(.008,.09,.59),.25);a.group('COR.Hardhat',(-2.10,-.18,1.144))
 n=64;vs=[]
 for j in range(9):
  phi=j/9*math.pi/2
  for k in range(n):t=k*math.tau/n;vs.append((-2.10+.134*math.cos(phi)*math.cos(t),-.18+.104*math.cos(phi)*math.sin(t),1.145+.150*math.sin(phi)))
 vs.append((-2.10,-.18,1.295));fs=[]
 for j in range(8):
  for k in range(n):q=j*n+k;fs.append((q,j*n+(k+1)%n,(j+1)*n+(k+1)%n,q+n))
 for k in range(n):fs.append((8*n+k,8*n+(k+1)%n,9*n))
 shell=a.mesh('COR.Hardhat.Shell',vs,fs,blue);sol=shell.modifiers.new('Hardhat shell thickness','SOLIDIFY');sol.thickness=.0035
 for face in shell.data.polygons:face.use_smooth=True
 vs=[]
 for z,outer in [(1.141,True),(1.145,True),(1.145,False),(1.141,False)]:
  for k in range(n):
   t=k*math.tau/n;rx,ry=(.160,.134) if outer else(.127,.097);vs.append((-2.10+rx*math.cos(t),(-.157 if outer else-.18)+ry*math.sin(t),z))
 fs=[]
 for j in range(4):
  for k in range(n):fs.append((j*n+k,j*n+(k+1)%n,((j+1)%4)*n+(k+1)%n,((j+1)%4)*n+k))
 a.mesh('COR.Hardhat.Brim',vs,fs,blue)
 for dx in [-.042,.042]:a.curve(f'COR.Hardhat.Rib.{dx}',[(-2.10+dx,-.27,1.192),(-2.10+dx,-.23,1.267),(-2.10+dx,-.18,1.290),(-2.10+dx,-.13,1.267),(-2.10+dx,-.09,1.192)],.0045,blue)
 a.parent=None
 fabric=a.mat('Equipment backpack fabric',(.014,.019,.022),.96)
 for n,(x,y) in enumerate([(-1.57,-.14),(-1.40,.11)],1):
  a.group(f'COR.Backpack.{n}',(x,y,0));a.box(f'COR.Backpack.{n}.Main',(x,y,.28),(.33,.23,.51),fabric,.09);a.box(f'COR.Backpack.{n}.Pocket',(x,y+.126,.24),(.27,.08,.30),fabric,.05)
  for dx in [-.09,.09]:a.curve(f'COR.Backpack.{n}.Strap.{dx}',[(x+dx,y-.10,.48),(x+dx,y-.22,.41),(x+dx,y-.22,.15),(x+dx,y-.10,.10)],.017,fabric)
  a.curve(f'COR.Backpack.{n}.Handle',[(x-.06,y,.50),(x-.05,y,.56),(x+.05,y,.56),(x+.06,y,.50)],.011,fabric);a.parent=None
 # Unloaded tripod at the bar opening is separate from the photo-room softbox stand.
 a.group('COR.Tripod',(-.80,2.75,0));a.rod('COR.Tripod.Column',(-.80,2.75,.36),(-.80,2.75,1.19),.014,black)
 for k in range(3):
  t=k*2*math.pi/3;a.rod(f'COR.Tripod.Leg.{k}',(-.80,2.75,.55),(-.80+.32*math.cos(t),2.75+.32*math.sin(t),.02),.011,black)
 a.cyl('COR.Tripod.Head',(-.80,2.75,1.21),.022,.05,black,16);a.parent=None
 # Registered planar prints use native subdivided plane UVs and independent frames.
 # PLY wall scans determine rectangle extents; every image is a physical print once.
 def gallery_print(name,cx,y,z,w,h,station,mat,facing):
  a.group(name,(cx,y,z));a.box(name+'.Backing',(cx,y-facing*.012,z),(w,.018,h),dark,.003)
  a.photo_plane(name+'.Print',(cx,y,z),(-w if facing>0 else w,0,0),(0,0,h),station)
  for side,xx in enumerate([cx-w/2,cx+w/2]):a.box(name+f'.FrameVertical.{side}',(xx,y+facing*.009,z),(.016,.029,h+.02),mat,.003)
  for side,zz in enumerate([z-h/2,z+h/2]):a.box(name+f'.FrameHorizontal.{side}',(cx,y+facing*.009,zz),(w+.02,.029,.016),mat,.003)
  a.parent=None
 for ident,cx,y,z,w,h,station in [('BlueBlueprint',-2.50,-.489,1.55,.81,.82,2),('WhiteArchitecturalSection',-.92,-.492,1.49,.80,1.00,2),('EiffelDrawing',.76,-.501,1.49,.84,1.00,1),('BlackBlueprint',2.175,-.515,1.49,.69,.99,1)]:
  gallery_print('COR.Art.'+ident,cx,y,z,w,h,station,wood if 'White' in ident or 'Eiffel' in ident else dark,1)
 for ident,cx,y in [('YellowStillLife',.61,.599),('GreenStillLife',1.79,.591),('PinkStillLife',2.96,.584)]:
  gallery_print('COR.Art.'+ident,cx,y,1.39,.80,1.20,1,wood if ident.startswith('Yellow') else dark,-1)
 a.group('COR.Art.TokyoMap',(-3.371,4.925,1.415));a.box('COR.Art.TokyoMap.Backing',(-3.385,4.925,1.415),(.018,.78,1.60),dark,.004)
 a.photo_plane('COR.Art.TokyoMap.Print',(-3.371,4.925,1.415),(0,.78,0),(0,0,1.60),7)
 for side,yy in enumerate([4.535,5.315]):a.box(f'COR.Art.TokyoMap.FrameVertical.{side}',(-3.359,yy,1.415),(.03,.017,1.62),dark,.003)
 for side,zz in enumerate([.615,2.215]):a.box(f'COR.Art.TokyoMap.FrameHorizontal.{side}',(-3.359,4.925,zz),(.03,.80,.017),dark,.003)
 a.parent=None
 # Source-derived exact diagonal pillar planes.
 reg=json.loads((ROOT/'research/registration-cad.json').read_text());ent=json.loads((ROOT/'research/cad-entities.json').read_text());M=reg['cad_mm_to_scene_matrix'];ls={l['handle']:l for l in ent['lines']}
 def point(x):return Vector((M[0][0]*x[0]+M[0][1]*x[1]+M[0][3],M[1][0]*x[0]+M[1][1]*x[1]+M[1][3],0))
 sides=[]
 for h in ['59A','59B','59C','59D','59E']:
  p,q=point(ls[h]['a']),point(ls[h]['b']);v=q-p
  if v.length>.2:sides.append((p,q,(p+q)/2))
 # Calligraphy faces station5 southwest; StarryNight faces station7 northwest.
 for name,st in [('Calligraphy',5),('StarryNight',7)]:
  station=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'][st-1];c=Vector((*station['translation_xyz_m'][:2],0));p,q,mid=min(sides,key=lambda s:(s[2]-c).length);u=(q-p).normalized();normal=Vector((-u.y,u.x,0))
  if normal.dot(c-mid)<0:normal=-normal;u=-u
  ctr=mid+normal*.026;ctr.z=1.42;a.photo_plane('COR.Art.'+name,ctr,-u*.89,(0,0,1.40),st,wood if st==5 else dark)
 # Blank room labels and small visible entrance switches.
 for n,loc,sz in [(1,(-3.404,2.60,1.16),(.017,.26,.17)),(2,(-.39,3.015,1.18),(.26,.017,.17))]:
  a.box(f'COR.RoomPlaque.{n}.Frame',loc,sz,dark,.006)
  inset=(loc[0]+.011,loc[1],loc[2]) if n==1 else(loc[0],loc[1]-.011,loc[2]);a.box(f'COR.RoomPlaque.{n}.Insert',inset,(.004,.232,.143) if n==1 else(.232,.004,.143),tan,.002)
 for i in range(2):a.box(f'COR.EntranceSwitch.{i}',(3.48+i*.075,.599,1.16),(.068,.015,.08),a.mat('Off white switchplate',(.81,.81,.77)),.004)
 # Safety fixtures visible in all gallery views, with separate housings and heads.
 white=a.mat('Off white switchplate',(.81,.81,.77));green=a.mat('Exit green diffuser',(.015,.32,.05),.4,0,1)
 for n,c,u,station in [(1,(3.937,.004,2.350),(0,-.36,0),1),(2,(-2.064,-.420,2.490),(-.34,0,0),2)]:
  dims=(.023,.38,.17) if n==1 else (.36,.023,.17);a.box(f'COR.ExitSign.{n}.Housing',c,dims,black,.008);graphic=a.photo_plane(f'COR.ExitSign.{n}.Graphic',(c[0]-.014,c[1]+.014,c[2]),u,(0,0,.14),station)
  m=graphic.data.materials[0].copy();m.name=f'COR ExitSign {n} illuminated graphic';graphic.data.materials[0]=m;nt=m.node_tree;tex=next(node for node in nt.nodes if node.type=='TEX_IMAGE');nt.links.new(tex.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Emission Color']);nt.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=.45
  for side in [-1,1]:
   anchor=(c[0],c[1]+side*.12,c[2]+.085) if n==1 else(c[0]+side*.12,c[1],c[2]+.085);a.rod(f'COR.ExitSign.{n}.Suspension.{side}',anchor,(anchor[0],anchor[1],2.78),.002,chrome,8)
  cable_start=(c[0],c[1]+.12,c[2]+.085) if n==1 else(c[0]+.12,c[1],c[2]+.085)
  cable=[(cable_start[0]+.009*math.sin(k*math.pi/2),cable_start[1]+.006*math.cos(k*math.pi/2),cable_start[2]+(2.775-cable_start[2])*k/16) for k in range(17)]
  a.curve(f'COR.ExitSign.{n}.SupplyCable',cable,.0025,white)
 a.box('COR.EmergencyLamp.Housing',(-3.405,2.94,2.40),(.06,.24,.10),white,.01)
 for i,yy in enumerate([2.866,3.014],1):
  a.rod(f'COR.EmergencyLamp.Stem.{i}',(-3.405,yy,2.42),(-3.405,yy,2.50),.009,white)
  a.cyl(f'COR.EmergencyLamp.Head.{i}',(-3.37,yy,2.52),.045,.04,chrome,24,(0,math.pi/2,0))
 # Every visible gallery fixture is registered from actual E57 photo rays.
 # Nine former generic structure lamps are removed; these are the sole corridor lights.
 lighting=json.loads((ROOT/'research/corridor-lighting-registration.json').read_text())
 gunmetal=a.mat('COR track gunmetal',(.025,.030,.033),.27,.72)
 lens_cool=a.mat('COR spotlight cool lens',(.83,.91,1),.24,0,6)
 lens_warm=a.mat('COR spotlight warm lens',(1,.71,.38),.24,0,6)
 square_diffuser=a.mat('COR square warm diffuser',(1,.72,.38),.28,0,5)
 a.group('COR.Lighting.Tracks')
 track_segments=[((-2.63,-.21,2.785),(3.25,-.21,2.785)),((.20,.29,2.785),(3.20,.29,2.785)),((-2.35,3.73,2.785),(-1.35,2.745,2.785)),((-1.35,2.745,2.785),(-.37,3.715,2.785)),((-2.35,4.185,2.785),(-1.59,4.94,2.785)),((-3.10,4.49,2.785),(-3.10,5.20,2.785))]
 for i,(p,q) in enumerate(track_segments,1):
  p,q=Vector(p),Vector(q);v=q-p;mid=(p+q)/2
  a.box(f'COR.Lighting.Track.{i}.Rail',mid,(v.length,.031,.027),gunmetal,.002,math.atan2(v.y,v.x))
  a.curve(f'COR.Lighting.Track.{i}.Conductor',[p+Vector((0,0,-.016)),q+Vector((0,0,-.016))],.003,black)
 a.parent=None
 spots=[f for f in lighting['fixtures'] if f['kind']=='spot'];squares=[f for f in lighting['fixtures'] if f['kind']=='square']
 for i,f in enumerate(spots,1):
  c=Vector(f['position']);name=f'COR.Lighting.Spot.{i:02}';group=a.group(name,c)
  group['source_registration']=f['fixture_id'];group['position_status']=f['position_status'];group['source_stations']=','.join(map(str,sorted(set(o['station'] for o in f['observations']))))
  if 'ray_RMS_m' in f:group['source_ray_rms_m']=f['ray_RMS_m']
  if c.y<.0:target=Vector((c.x,-.51,1.55))
  elif c.y<1:target=Vector((c.x,.60,1.40))
  elif c.x<-2.6:target=Vector((-3.37,4.925,1.42))
  elif c.y>4:target=Vector((-1.74,4.33,1.42))
  elif c.x<-1.3:target=Vector((-1.76,3.60,1.42))
  else:target=Vector((-.98,3.57,1.42))
  direction=(target-c).normalized();rear=c-direction*.130;warm=3.0<c.y<3.5 and c.x<-1.3
  a.rod(name+'.Barrel',rear,c-direction*.011,.038,gunmetal,40)
  a.rod(name+'.Bezel',c-direction*.016,c,.042,gunmetal,40)
  a.rod(name+'.Reflector',c,c+direction*.002,.033,chrome,40)
  a.rod(name+'.Lens',c+direction*.003,c+direction*.005,.028,lens_warm if warm else lens_cool,40)
  a.box(name+'.TrackAdapter',(rear.x,rear.y,2.768),(.075,.032,.030),black,.004)
  a.rod(name+'.Swivel',rear+Vector((0,0,.020)),(rear.x,rear.y,2.757),.010,gunmetal,20)
  a.cyl(name+'.Pivot',rear,.017,.080,gunmetal,24,(math.pi/2,0,0))
  d=bpy.data.lights.new(name+'.Photometric','SPOT');d.energy=8;d.color=(1,.76,.49) if warm else(.84,.92,1);d.spot_size=math.radians(55);d.spot_blend=.45;d.shadow_soft_size=.025
  ob=bpy.data.objects.new(name+'.Photometric',d);a.collection.objects.link(ob);ob.location=c+direction*.012;ob.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();a.tag(ob,ob.name)
  a.parent=None
 for i,f in enumerate(squares,1):
  x,y,_=f['position'];name=f'COR.Lighting.Square.{i:02}';group=a.group(name,(x,y,2.800));group['source_registration']=f['fixture_id'];group['position_status']=f['position_status'];group['source_stations']=','.join(map(str,sorted(set(o['station'] for o in f['observations']))))
  if 'ray_RMS_m' in f:group['source_ray_rms_m']=f['ray_RMS_m']
  a.box(name+'.Housing',(x,y,2.815),(.146,.146,.055),gunmetal,.008)
  a.box(name+'.Rim',(x,y,2.785),(.153,.153,.014),black,.007)
  a.box(name+'.Diffuser',(x,y,2.776),(.112,.112,.005),square_diffuser,.005)
  light=a.area_light(name+'.Photometric',(x,y,2.768),15,(1,.76,.48),.102);a.tag(light,light.name)
  a.parent=None
 # The two white ceiling discs above each exit sign are suspension cups,
 # visibly linked to the sign, rather than extra emergency lamp heads.
 for n,c in [(1,(3.937,.004,2.350)),(2,(-2.064,-.420,2.490))]:
  for side in [-1,1]:
   anchor=(c[0],c[1]+side*.12,2.775) if n==1 else(c[0]+side*.12,c[1],2.775)
   a.cyl(f'COR.ExitSign.{n}.SuspensionCup.{side}',anchor,.027,.015,white,24)
   for dx in [-.017,.017]:a.cyl(f'COR.ExitSign.{n}.SuspensionScrew.{side}.{dx}',(anchor[0]+dx,anchor[1],2.766),.003,.003,gunmetal,12)

 # Reproducible source-measured final retention details; root also applies this
 # same callable once to the already-building v3 checkpoint.
 from final_helmet_detail import add_helmet_detail
 add_helmet_detail(ROOT,a)

 from final_case_detail import apply_case_detail
 apply_case_detail(ROOT,a)
 from final_small_fixture_poses import apply_corridor_small_poses
 apply_corridor_small_poses(ROOT,a)
