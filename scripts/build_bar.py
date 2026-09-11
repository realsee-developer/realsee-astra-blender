"""Bar reconstruction. Native components measured in raw scanXY, floor-relative meters.
Source checks: all six registered cube4 faces, detailed shelf crop, PLY projections.
"""
import math,json
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector

def build_bar(ROOT,api):
 a=api;a.area_collection('BAR','data/panorama/4.jpg; data/cube-map/4_{f,r,b,l,u,d}.jpg; data/point-cloud.ply; research/visual-previews/bar-measured.png')
 black=a.mat('BAR black satin laminate',(.012,.015,.017),.32);wood=a.mat('BAR warm oak',(.32,.13,.045),.36);rim=a.mat('BAR bentwood edge',(.19,.063,.028),.4);metal=a.mat('BAR brushed silver',(.44,.46,.46),.28,.8);white=a.mat('BAR white appliance',(.73,.76,.76),.4);gold=a.mat('BAR antique gold frame',(.32,.23,.105),.45,.65);red=a.mat('BAR red plastic',(.42,.008,.007),.35);cream=a.mat('BAR warm paper',(.65,.59,.44),.7);emit=a.mat('BAR warm diffuser',(1,.81,.49),.4,emission=3)
 # Editable procedural wood grain follows each component's native generated coordinates.
 nt=wood.node_tree;tc=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(3,48,3);nt.links.new(tc.outputs['Generated'],mapping.inputs['Vector']);noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4;noise.inputs['Detail'].default_value=4;nt.links.new(mapping.outputs['Vector'],noise.inputs['Vector']);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(.095,.030,.009,1);ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(.32,.145,.054,1);nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.002;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],nt.nodes['Principled BSDF'].inputs['Normal'])
 # Counter carcass split into panel/top/end; real volume behind visible facade remains accessible.
 a.group('BAR-COUNTER',(2.72,1.64,0))
 a.box('BAR-COUNTER-Front',(2.55,1.64,.47),(.065,1.75,.94),black,.012)
 for j,y in enumerate([.79,2.49]):a.box(f'BAR-COUNTER-End-{j+1}',(2.78,y,.47),(.48,.055,.94),black,.009)
 a.box('BAR-COUNTER-Worktop',(2.76,1.65,.961),(.59,1.82,.055),wood,.016)
 a.box('BAR-COUNTER-LowerShelf',(2.79,1.64,.12),(.43,1.66,.035),black,.005)
 a.parent=None
 # Five full-width shelves, four independent uprights and visible brackets.
 a.group('BAR-SHELVES',(3.91,1.90,0))
 for j,z in enumerate([.87,1.27,1.67,2.07,2.47]):
  a.box(f'BAR-SHELVES-Board-{j+1}',(3.815,1.90,z),(.31,2.25,.023),wood,.004)
  for k,y in enumerate([.805,1.50,2.23,3.0]):a.box(f'BAR-SHELVES-Bracket-{j+1}-{k+1}',(3.85,y,z-.047),(.20,.017,.075),metal,.002)
 for j,y in enumerate([.805,1.50,2.23,3.0]):
  a.box(f'BAR-SHELVES-Upright-{j+1}',(3.969,y,1.68),(.018,.027,1.72),metal,.003)
  for k in range(42):a.box(f'BAR-SHELVES-Slot-{j+1}-{k+1}',(3.954,y,.85+k*.04),(.004,.011,.017),black)
 a.parent=None
 # Embossed silver backsplash: backing surface and shallow physical tile relief.
 a.group('BAR-BACKSPLASH',(3.98,1.91,1.13));a.box('BAR-BACKSPLASH-Backing',(3.982,1.91,1.13),(.012,2.25,.93),metal)
 for iy in range(11):
  for iz in range(6):
   y=.9+iy*.20;z=.75+iz*.16
   a.box(f'BAR-BACKSPLASH-Tile-{iy:02}-{iz}',(3.969,y,z),(.011,.190,.14),metal,.01)
   pts=[(3.959,y+.057*math.cos(k*math.pi/6),z+.042*math.sin(k*math.pi/6)) for k in range(12)]
   a.curve(f'BAR-BACKSPLASH-Relief-{iy:02}-{iz}',pts,.004,metal,True)
 a.parent=None
 # Individual lathed bottles of photographed body styles. Labels/caps are independently editable.
 from mathutils import Quaternion
 reg=json.loads((Path(ROOT)/'research/camera-registration.json').read_text())['stations'][3]
 photo_pos=Vector(reg['translation_xyz_m']);photo_pos.z+=a.offset;photo_q=Quaternion(reg['quaternion_wxyz']).inverted()
 labelmat=a.mat('BAR photographed bottle labels',(1,1,1),.65)
 node=labelmat.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(Path(ROOT)/'output/assets/panorama-4-material.jpg'),check_existing=True);labelmat.node_tree.links.new(node.outputs['Color'],labelmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
 colors=[(.26,.085,.015),(.12,.022,.009),(.013,.09,.028),(.30,.17,.022),(.41,.21,.043),(.006,.013,.16),(.36,.14,.03),(.23,.10,.025),(.48,.35,.075)]
 def bottle(name,y,z,h=.28,r=.045,style=0,color_index=0,x=3.795):
  a.group(name,(x,y,z));mat=a.mat('BAR bottle glass '+str(color_index),colors[color_index%len(colors)],.16,0)
  bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Transmission Weight'].default_value=0 if color_index==5 else .28;bs.inputs['IOR'].default_value=1.46
  if style==1:profile=[(.50*r,0),(.93*r,.025*h),(1.05*r,.4*h),(.75*r,.64*h),(.27*r,.77*h),(.25*r,.96*h)]
  elif style==2:profile=[(.65*r,0),(1.10*r,.07*h),(1.25*r,.35*h),(1.16*r,.53*h),(.6*r,.70*h),(.27*r,.78*h),(.25*r,.96*h)]
  else:profile=[(.8*r,0),(r,.025*h),(r,.65*h),(.85*r,.73*h),(.36*r,.8*h),(.32*r,.96*h)]
  body=a.lathe(name+'-Body',(x,y,z),profile,mat,28)
  body['evidence_status']='observed count, position and silhouette; hidden backside and glass thickness inferred'
  # Billboard-free label: thin curved band following the bottle radius.
  rr=r*(1.07 if style==1 else 1.26 if style==2 else 1.01);za=z+h*.17;zb=z+h*.58;vs=[]
  for zz in [za,zb]:
   for k in range(17):ang=math.pi-0.73+k*1.46/16;vs.append((x+rr*math.cos(ang),y+rr*math.sin(ang),zz))
  lab=a.mesh(name+'-Label',vs,[(k,k+1,k+18,k+17) for k in range(16)],labelmat)
  uv=lab.data.uv_layers.new(name='RegisteredLabelGraphic')
  for poly in lab.data.polygons:
   for li in poly.loop_indices:
    p=Vector(vs[lab.data.loops[li].vertex_index]);ray=photo_q@(p-photo_pos);ray.normalize();uv.data[li].uv=((math.atan2(ray.x,ray.z)/(2*math.pi)+.5)%1,1-math.acos(max(-1,min(1,-ray.y)))/math.pi)
  lab['evidence_status']='curved paper label surface with registered photograph UV; no bottle geometry baked'
  mod=lab.modifiers.new('Label paper thickness','SOLIDIFY');mod.thickness=.0004
  a.cyl(name+'-Cap',(x,y,z+h*.986),r*.34,h*.055,gold if color_index%3==0 else black,24)
  a.parent=None
 top_y=[2.88,2.68,2.47,2.18,1.94,1.71,1.46,1.23,.99]
 for i,y in enumerate(top_y):bottle(f'BAR-BOTTLE-TOP-{i+1:02}',y,2.085,[.27,.28,.24,.31,.27,.34,.26,.27,.23][i],[.039,.04,.044,.040,.037,.04,.045,.049,.04][i],0,i)
 for i,y in enumerate([2.88,2.65,2.22,1.96,1.68,1.40,1.13]):bottle(f'BAR-BOTTLE-MID-{i+1:02}',y,1.685,[.27,.24,.25,.21,.23,.27,.23][i],[.043,.062,.047,.076,.067,.066,.04][i],[0,2,0,2,1,1,0][i],i%5)
 for i,y in enumerate([2.88,2.67,2.47,2.23,2.00,1.77,1.58,1.35,1.17]):bottle(f'BAR-BOTTLE-LOW-{i+1:02}',y,1.285,[.27,.24,.27,.28,.24,.23,.28,.27,.27][i],[.065,.06,.058,.042,.073,.069,.038,.04,.035][i],[1,2,1,0,2,1,0,0,0][i],i%5)
 for i,y in enumerate([2.63,2.37,2.05,1.79]):bottle(f'BAR-BOTTLE-BACK-{i+1:02}',y,.885,[.26,.32,.22,.25][i],.04,0,i,x=3.78)
 for i,y in enumerate([1.85,1.74,1.62,1.51,1.40,1.28,1.18,1.08]):bottle(f'BAR-BOTTLE-COUNTER-{i+1:02}',y,.99,[.36,.28,.31,.31,.29,.27,.36,.28][i],[.047,.036,.044,.044,.044,.041,.040,.041][i],0,[5,1,0,2,8,3,1,2][i],x=2.62)
 # Thin gold-capped bottle partially visible behind the rose bottle.
 bottle('BAR-BOTTLE-COUNTER-09',1.28,.99,.31,.023,0,0,x=2.80)
 def books(name,n,y,z,x=3.78,direction=1):
  a.group(name,(x,y,z))
  for i in range(n):
   col=[(.40,.24,.15),(.65,.58,.44),(.09,.085,.07),(.32,.35,.31),(.51,.44,.37)][i%5];m=a.mat('BAR book cloth '+str(i%5),col,.7)
   a.box(f'{name}-{i+1:02}',(x,y+direction*i*.035,z+.13),(.13,.029,.26+(.015 if i%3==0 else 0)),m,.002)
   for dz in [-.09,.09]:a.box(f'{name}-{i+1:02}-SpineRule-{dz}',(x-.067,y+direction*i*.035,z+.13+dz),(.001,.023,.004),cream)
  a.parent=None
 books('BAR-BOOKS-MID',5,.82,1.685);books('BAR-BOOKS-LOW',8,.82,1.285);books('BAR-BOOKS-BOTTOM',6,2.82,.885);books('BAR-BOOKS-COUNTER',5,.81,.99,2.62)
 a.group('BAR-CAN',(2.60,2.03,.99));a.cyl('BAR-CAN-RedBody',(2.60,2.03,1.075),.027,.17,red,32);a.cyl('BAR-CAN-AluminumTop',(2.60,2.03,1.162),.026,.004,metal,32);a.parent=None
 a.cyl('BAR-CAP',(2.72,1.62,1.008),.011,.023,red,20,rot=(0,math.pi/2,0))
 a.group('BAR-MINITRIPOD',(2.80,2.28,.99));a.cyl('BAR-MINITRIPOD-Hub',(2.80,2.28,1.065),.016,.03,black)
 for k in range(3):
  ang=k*2*math.pi/3;a.rod(f'BAR-MINITRIPOD-Leg-{k+1}',(2.8,2.28,1.058),(2.8+.10*math.cos(ang),2.28+.10*math.sin(ang),.99),.008,metal)
 a.parent=None;a.curve('BAR-COUNTER-Cable',[(2.88,.80,1.00),(2.78,1.04,1.00),(2.69,1.29,1.00),(2.7,1.61,1.00)],.004,black)
 a.box('BAR-COUNTER-SPONGE',(2.63,2.34,1.003),(.035,.046,.022),cream,.002)
 # Round cafe table with separately adjustable thickness, pedestal and base.
 a.group('BAR-TABLE',(.935,1.25,0));a.cyl('BAR-TABLE-Top',(.935,1.25,.718),.345,.036,wood,80);a.cyl('BAR-TABLE-Pedestal',(.935,1.25,.36),.041,.68,black);a.cyl('BAR-TABLE-Foot',(.935,1.25,.02),.205,.032,black,64);a.parent=None
 # Three padded bentwood chairs. Distinct seat, bent back, rim, four legs each.
 def chair(idx,x,y,ang):
  name=f'BAR-CHAIR-{idx:02}';a.group(name,(x,y,0));ca,sa=math.cos(ang),math.sin(ang)
  def tr(p):return(x+ca*p[0]-sa*p[1],y+sa*p[0]+ca*p[1],p[2])
  seat=a.ball(name+'-Seat',tr((0,.015,.411)),(.26,.232,.044),black);seat.rotation_euler.z=ang
  under=a.ball(name+'-BentwoodSeat',tr((0,.003,.385)),(.266,.234,.023),rim);under.rotation_euler.z=ang
  # Wrapped curved back with real solid thickness; low open gap above seat is retained.
  vs=[]
  for z,r in [(.505,.252),(.695,.28)]:
   for j in range(21):t=-1.15+j*2.3/20;vs.append(tr((r*math.sin(t),-.16-.08*math.cos(t),z-.06*(abs(t)/1.15)**2)))
  shell=a.mesh(name+'-Backrest',vs,[(j,j+1,j+22,j+21) for j in range(20)],black);mod=shell.modifiers.new('Bentwood shell thickness','SOLIDIFY');mod.thickness=.027;be=shell.modifiers.new('Upholstered edge radius','BEVEL');be.width=.014;be.segments=3
  a.curve(name+'-WoodRim',[tr((.28*math.sin(t),-.16-.08*math.cos(t),.695-.06*(abs(t)/1.15)**2)) for t in np.linspace(-1.15,1.15,32)],.011,rim)
  for k,(xx,yy) in enumerate([(-.19,-.16),(.19,-.16),(-.18,.18),(.18,.18)]):a.rod(name+f'-Leg-{k+1}',tr((xx,yy,.397)),tr((xx*1.15,yy*1.22,.025)),.010,black)
  a.parent=None
 for i,(x,y) in enumerate([(.81,1.93),(1.78,1.95),(1.73,1.23)],1):chair(i,x,y,math.atan2(-(.935-x),1.25-y))
 # Robotics: lower chassis native, mast/head separately operable, scanned control details retained locally.
 for ident,x,w in [('A',-.14,.40),('B',.43,.40)]:
  name='BAR-ROBOT-'+ident;a.group(name,(x,2.76,0))
  a.box(name+'-WhiteBumper',(x,2.73,.066),(w,.48,.105),white,.05);a.box(name+'-Deck',(x,2.74,.133),(w-.05,.42,.07),black,.026)
  if ident=='B':a.box(name+'-RedRearBumper',(x,2.975,.075),(w-.035,.023,.052),red,.013)
  for k,dx in enumerate([-.019,.019]):a.box(name+f'-MastRail-{k}',(x+dx,2.78,.69),(.014,.025,1.10),metal,.004)
  a.box(name+'-MastTopPlate',(x,2.78,1.245),(.080,.055,.016),metal,.007)
  for k,z in enumerate([.25,.78,1.18]):a.box(name+f'-CrossBar-{k}',(x,2.78,z),(.060,.023,.018),metal,.003)
  if ident=='B':
   a.box(name+'-DeviceBody',(x-.035,2.68,1.185),(.14,.075,.315),black,.018,rot=-.70)
   a.box(name+'-StatusDisplay',(x-.064,2.646,1.245),(.10,.003,.080),a.mat('BAR robot LCD',(.013,.019,.032),.25),.006,rot=-.70)
   a.box(name+'-WhiteLabel',(x-.064,2.641,1.148),(.082,.003,.016),white,rot=-.70)
   a.curve(name+'-RedCable',[(x-.025,2.68,1.035),(x+.03,2.68,.92),(x+.07,2.72,.85),(x+.035,2.73,.81),(x-.025,2.70,.83),(x-.06,2.68,.91),(x-.04,2.69,1.00)],.007,red)
   a.curve(name+'-BlackCable',[(x-.06,2.66,1.05),(x-.12,2.62,.96),(x-.10,2.63,.87),(x-.025,2.66,.83),(x+.04,2.69,.88),(x+.05,2.69,.98),(x-.02,2.68,1.04)],.006,black)
  # Local complex control-deck geometry is editable and preserves exact captured UV, excluding wall/floor.
  a.scan_part(name+'-ControlDeck',((x-w/2,2.53,.165),(x+w/2,2.96,.36)))
  a.parent=None
 # Small open carton next to second robot; separate flaps.
 a.group('BAR-CARDBOX',(.81,2.93,0));card=a.mat('BAR brown corrugated cardboard',(.33,.22,.12),.9)
 for j,dx in enumerate([-.095,.095]):a.box(f'BAR-CARDBOX-Side-{j}',(.81+dx,2.92,.092),(.006,.16,.18),card)
 for j,dy in enumerate([-.077,.077]):a.box(f'BAR-CARDBOX-End-{j}',(.81,2.92+dy,.092),(.19,.006,.18),card)
 a.box('BAR-CARDBOX-Bottom',(.81,2.92,.01),(.19,.16,.008),card)
 for j,dx in enumerate([-.12,.12]):fl=a.box(f'BAR-CARDBOX-Flap-{j}',(.81+dx,2.92,.185),(.07,.16,.005),card);fl.rotation_euler.y=(-1 if j else 1)*.45
 a.parent=None
 # White rounded floor appliance, geometry separated from thin QR graphic.
 a.group('BAR-APPLIANCE',(.16,.99,0));a.box('BAR-APPLIANCE-Shell',(.16,.99,.245),(.39,.32,.46),white,.08);a.box('BAR-APPLIANCE-Top',(.16,.99,.474),(.38,.31,.02),white,.06)
 for j in range(10):a.box(f'BAR-APPLIANCE-Vent-{j}',(.16-.135+j*.03,.823,.34),(.010,.007,.10),black,.002)
 a.scan_part('BAR-SIGN-QR',((-.01,.84,.46),(.32,1.18,.70)))
 a.curve('BAR-APPLIANCE-PowerCable',[(.28,.99,.49),(.33,1.03,.51),(.40,1.10,.12),(.39,.91,.025),(.30,.83,.26)],.006,black)
 a.parent=None
 # Pedestal fan. Thin wire guard, five blades, motor, mast, foot are actual geometry.
 a.group('BAR-FAN',(-.27,1.02,0));a.cyl('BAR-FAN-Foot',(-.27,1.02,.025),.145,.04,black,48);a.cyl('BAR-FAN-Mast',(-.27,1.02,.46),.021,.86,black)
 fc=(-.27,1.015,1.02);a.cyl('BAR-FAN-Motor',(-.27,.99,1.02),.070,.12,black,32,rot=(math.pi/2,0,0))
 for rad in [.05,.095,.14,.184,.216]:a.curve('BAR-FAN-GuardRing-'+str(rad),[(fc[0]+rad*math.cos(t),1.10,fc[2]+rad*math.sin(t)) for t in np.linspace(0,math.tau,72,endpoint=False)],.0027,black,True)
 for k in range(24):
  th=k*math.tau/24;a.rod(f'BAR-FAN-GuardSpoke-{k}',(fc[0]+.025*math.cos(th),1.12,fc[2]+.025*math.sin(th)),(fc[0]+.215*math.cos(th),1.085,fc[2]+.215*math.sin(th)),.0025,black,8)
 for k in range(5):
  t=k*math.tau/5;vs=[(fc[0]+r*math.cos(t+dt),1.035,fc[2]+r*math.sin(t+dt)) for r,dt in[(.035,-.15),(.18,-.05),(.20,.34),(.08,.65)]];o=a.mesh(f'BAR-FAN-Blade-{k+1}',vs,[(0,1,2,3)],a.mat('BAR fan dark translucent blades',(.055,.06,.055),.38));m=o.modifiers.new('Blade thickness','SOLIDIFY');m.thickness=.004
 a.cyl('BAR-FAN-CenterCap',(fc[0],1.125,fc[2]),.05,.022,black,32,rot=(math.pi/2,0,0));a.parent=None
 # Ten actual wall prints: localized source UV carries only flat printed artwork; frames native.
 artworks=[('N-01',.19,1.51,.38,.58),('N-02',.60,1.77,.28,.38),('N-03',.60,1.23,.26,.34),('N-04',1.07,1.51,.59,.89),('N-05',1.66,1.51,.37,.56),('S-01',1.63,1.51,.37,.56),('S-02',1.08,1.51,.59,.89),('S-03',.60,1.77,.28,.38),('S-04',.60,1.23,.26,.34),('S-05',.19,1.51,.38,.58)]
 for ident,x,z,w,h in artworks:
  north=ident[0]=='N';y=3.022 if north else.751;name='BAR-ART-'+ident;a.group(name,(x,y,z))
  a.box(name+'-Backing',(x,y,z),(w,.025,h),black,.006)
  for side,xx in enumerate([x-w/2,x+w/2]):a.box(name+f'-FrameVertical-{side}',(xx,y+(-.022 if north else.022),z),(.023,.032,h+.03),black,.005)
  for side,zz in enumerate([z-h/2,z+h/2]):a.box(name+f'-FrameHorizontal-{side}',(x,y+(-.022 if north else.022),zz),(w+.03,.032,.023),black,.005)
  for side,xx in enumerate([x-w/2+.016,x+w/2-.016]):a.box(name+f'-GoldVertical-{side}',(xx,y+(-.041 if north else.041),z),(.005,.003,h-.006),gold)
  a.photo_plane(name+'-PrintedGraphic',(x,y+(-.042 if north else.042),z),(w-.052,0,0),(0,0,h-.05),4);a.parent=None
 # Local outlet plates and switch observed at two low walls and above counter.
 for i,(x,y,z) in enumerate([(.57,3.037,.27),(.67,3.037,.27),(-.16,3.037,.24),(.30,.846,.25),(1.1,.846,.27),(2.0,.846,.24),(3.949,2.25,1.31),(3.949,2.06,1.31),(3.949,1.04,1.31)],1):
  name=f'BAR-OUTLET-{i:02}';a.group(name,(x,y,z));east=x>3.9
  a.box(name+'-Plate',(x,y,z),(.008,.084,.084) if east else(.084,.008,.084),white,.004)
  for k,dx in enumerate([-.017,.017]):a.box(name+f'-Socket-{k}',(x-.006,y+dx,z) if east else(x+dx,y+(-.006 if y>2 else.006),z),(.004,.013,.023) if east else(.013,.004,.023),black,.001)
  a.parent=None
 a.box('BAR-SWITCH',(-.14,.863,1.36),(.075,.012,.115),black,.003)
 # Ceiling fixtures below source-measured grid.
 a.group('BAR-LIGHT-ROUND',(.15,1.84,2.79));a.cyl('BAR-LIGHT-ROUND-Rim',(.15,1.84,2.77),.175,.027,white,64);a.cyl('BAR-LIGHT-ROUND-Diffuser',(.15,1.84,2.752),.15,.009,emit,64);a.parent=None
 for i,(x,y) in enumerate([(1.31,1.17),(1.31,2.67),(3.15,1.15),(3.15,2.68)],1):a.box(f'BAR-LIGHT-SQUARE-{i}-Housing',(x,y,2.79),(.105,.105,.028),black);a.box(f'BAR-LIGHT-SQUARE-{i}-Emitter',(x,y,2.771),(.075,.075,.009),emit)
 a.group('BAR-LIGHT-LINE',(2.93,1.92,2.51));a.box('BAR-LIGHT-LINE-Housing',(2.93,1.92,2.51),(.040,1.75,.030),black,.007);a.box('BAR-LIGHT-LINE-Diffuser',(2.93,1.92,2.491),(.032,1.72,.008),emit)
 for i,y in enumerate([1.17,2.67]):a.rod(f'BAR-LIGHT-LINE-Suspension-{i}',(2.93,y,2.526),(2.93,y,2.79),.002,black,8)
 a.parent=None;a.cyl('BAR-SMOKE',(3.73,.94,2.768),.039,.028,white,24)
 a.area_light('BAR warm counter illumination',(2.6,1.9,2.62),100,(1,.80,.60),1.6);a.area_light('BAR neutral central illumination',(.8,1.9,2.64),130,(.83,.90,1),1.8)
 from final_bar_seats import apply_bar_seats
 apply_bar_seats(ROOT)
 from final_fan_pose import apply_fan_pose
 apply_fan_pose(ROOT,a)
 from final_small_fixture_poses import apply_bar_switch_pose
 apply_bar_switch_pose(ROOT,a)
 return a.collection
