import math,bpy
from mathutils import Vector

def build_living_details(ROOT,a):
 a.area_collection('LivingDining_Details','data/cube-map/8_f.jpg;8_r.jpg;8_b.jpg;8_l.jpg;8_u.jpg;8_d.jpg;data/point-cloud.ply')
 wood=a.mat('Living honey oak',(.42,.18,.065));black=a.mat('Charcoal equipment',(.012,.014,.018));white=a.mat('Appliance white',(.86,.85,.8));cane=a.mat('Natural woven cane',(.61,.43,.22));cream=a.mat('Sofa cream woven upholstery',(.78,.72,.61))
 # Broad leaf plant: pot shell, soil, individual stems and curved editable leaf meshes.
 green=a.mat('Living plant green',(.05,.15,.015),.58);stem=a.mat('Living plant stems',(.23,.17,.055),.69)
 a.group('LIV.BroadLeafPlant',(-3.90,6.18,0))
 a.lathe('LIV.BroadLeafPlant.Pot',(-3.9,6.18,.005),[(.10,0),(.135,.04),(.15,.22),(.143,.25),(.125,.245),(.12,.215),(.09,.025)],cane,40)
 a.cyl('LIV.BroadLeafPlant.Soil',(-3.90,6.18,.21),.12,.015,a.mat('Plant soil',(.045,.025,.012)),24)
 for i,(dx,dy,h,w) in enumerate([(-.15,.02,1.55,.14),(.13,-.01,1.40,.16),(.0,.12,1.29,.13),(-.20,.10,1.19,.16),(.21,.13,1.05,.13),(.12,-.11,.91,.14),(-.12,-.11,.82,.12),(.24,.02,.71,.12)],1):
  root=Vector((-3.90,6.18,.19));base=Vector((-3.90+dx*.65,6.18+dy*.65,h*.52));tip=Vector((-3.90+dx,6.18+dy,h));a.rod(f'LIV.BroadLeafPlant.Stem.{i}',root,tip,.006,stem)
  tangent=Vector((-dy,dx,0)).normalized();vs=[];fs=[]
  for j in range(13):
   t=j/12;mid=base.lerp(tip,t);mid.y+=.035*math.sin(math.pi*t);ww=w*math.sin(math.pi*t)**.75
   for side in [-1,0,1]:vs.append(tuple(mid+tangent*ww*side+Vector((0,.014*abs(side)*math.sin(math.pi*t),0))))
  for j in range(12):
   for k in range(2):n=j*3+k;fs.append((n,n+1,n+4,n+3))
  o=a.mesh(f'LIV.BroadLeafPlant.Leaf.{i}',vs,fs,green);sol=o.modifiers.new('Leaf thickness','SOLIDIFY');sol.thickness=.001
 # Each leaf retains a longitudinal UV coordinate and an actual central vein.
  uv=o.data.uv_layers.new(name='LeafLongitudinal')
  for poly in o.data.polygons:
   for li in poly.loop_indices:
    vi=o.data.loops[li].vertex_index;uv.data[li].uv=((vi%3)/2,(vi//3)/12)
  veinmat=a.mat('Broadleaf yellow green vein',(.10,.18,.025),.72)
  a.curve(f'LIV.BroadLeafPlant.Vein.{i}',[(v[0],v[1]-.002,v[2]) for v in vs[1::3]],.0017,veinmat)
 a.parent=None
 # Thin secondary venation remains editable in native shader nodes rather than captured wall colors.
 nt=green.node_tree;bs=nt.nodes['Principled BSDF'];uvn=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uvn.outputs['UV'],sep.inputs[0])
 sub=nt.nodes.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=.5;nt.links.new(sep.outputs['X'],sub.inputs[0]);ab=nt.nodes.new('ShaderNodeMath');ab.operation='ABSOLUTE';nt.links.new(sub.outputs[0],ab.inputs[0]);slant=nt.nodes.new('ShaderNodeMath');slant.operation='MULTIPLY';slant.inputs[1].default_value=.18;nt.links.new(ab.outputs[0],slant.inputs[0]);phase=nt.nodes.new('ShaderNodeMath');phase.operation='ADD';nt.links.new(sep.outputs['Y'],phase.inputs[0]);nt.links.new(slant.outputs[0],phase.inputs[1]);freq=nt.nodes.new('ShaderNodeMath');freq.operation='MULTIPLY';freq.inputs[1].default_value=300;nt.links.new(phase.outputs[0],freq.inputs[0]);wave=nt.nodes.new('ShaderNodeMath');wave.operation='SINE';nt.links.new(freq.outputs[0],wave.inputs[0]);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.008,.042,.003,1);ramp.color_ramp.elements[1].color=(.026,.102,.007,1);nt.links.new(wave.outputs[0],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.0008;nt.links.new(wave.outputs[0],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
 # Small cane side table: two shallow round trays, actual legs.
 a.group('LIV.RoundSideTable',(-6.67,6.24,0))
 for z in [.19,.53]:
  a.cyl(f'LIV.RoundSideTable.Tray.{z}',(-6.67,6.24,z),.205,.018,cane,48)
  a.curve(f'LIV.RoundSideTable.Rim.{z}',[(-6.67+.205*math.cos(j*2*math.pi/64),6.24+.205*math.sin(j*2*math.pi/64),z+.026) for j in range(64)],.011,cane,True)
 for k in range(3):
  t=k*2*math.pi/3;a.rod(f'LIV.RoundSideTable.Leg.{k}',(-6.67+.17*math.cos(t),6.24+.17*math.sin(t),.02),(-6.67+.17*math.cos(t),6.24+.17*math.sin(t),.55),.012,cane)
 a.parent=None
 # Four additional individually editable cushions plus observed black throw.
 orange=a.mat('Cushion terracotta orange',(.69,.20,.025),.9);yellow=a.mat('Cushion ocher yellow',(.84,.51,.04),.9)
 for n,loc,size,mat in [('Round',(-6.17,8.62,.59),(.21,.08,.21),orange),('Square',(-6.22,8.84,.65),(.20,.07,.19),orange),('Yellow',(-4.86,8.57,.49),(.27,.085,.12),yellow),('SmallPatterned',(-5.97,8.79,.56),(.13,.065,.16),cream)]:
  o=a.ball('LIV.CUSHION.'+n,loc,size,mat)
  if n=='Round':
   for vertex in o.data.vertices:
    theta=math.atan2(vertex.co.z,vertex.co.x);rr=(vertex.co.x**2+vertex.co.z**2)**.5;fac=1+.055*math.cos(theta*16)*(rr/.21)**3;vertex.co.x*=fac;vertex.co.z*=fac
 a.box('LIV.Sofa.BlackThrow',(-5.96,8.88,.72),(.30,.23,.10),a.mat('Black cotton throw',(.008,.009,.009),.94),.038)
 # North-wall artwork rectangles at measured printed regions, genuine flat source graphics.
 for name,x,z,w,h in [('FlowerVase',-6.15,1.63,.43,.76),('CatCup',-5.63,2.05,.37,.43),('OrangeVase',-5.63,1.48,.39,.65),('PinkFlower',-5.11,1.71,.46,.65),('CircularFlowers',-4.62,1.81,.35,.35)]:
  a.photo_plane('LIV.Art.'+name,(x,9.168,z),(-w,0,0),(0,0,h),8,wood)
 # Illustrated circular shelf: flat graphic, actual ledge and separate vase/sprigs.
 a.photo_plane('LIV.CatWallShelf.Graphic',(-3.02,9.16,1.72),(-.34,0,0),(0,0,.34),8)
 a.box('LIV.CatWallShelf.Ledge',(-3.02,9.08,1.68),(.32,.15,.025),wood,.008)
 a.lathe('LIV.CatWallShelf.Vase',(-3.02,9.06,1.696),[(.02,0),(.047,.055),(.028,.105),(.022,.12)],white)
 for i in range(5):
  dx=(i-2)*.07;tip=(-3.02+dx,9.05,2.10-abs(dx)*.6);a.rod(f'LIV.CatWallShelf.Branch.{i}',(-3.02,9.06,1.80),tip,.003,stem)
  for j in range(3):a.ball(f'LIV.CatWallShelf.Leaf.{i}.{j}',(-3.02+dx*(j+1)/3,9.03,1.86+j*.075),(.033,.01,.016),green)
 # Tall display cabinet surface objects, each identifiable item has its own mesh.
 # Replace broad scan top fragments with native books/cartons/tins; keep original reference only.
 for o in list(bpy.data.objects):
  if o.name.startswith('LIV.CabinetContent.'):bpy.data.objects.remove(o,do_unlink=True)
 palette=[(.63,.16,.095),(.7,.68,.54),(.07,.12,.20),(.74,.71,.64),(.16,.27,.33),(.74,.58,.48)]
 for i in range(18):
  x=-1.72+i*.045;h=.26+(.055 if i%4==1 else .0)-(.03 if i%5==3 else 0);m=a.mat(f'Book cover tone {i%6}',palette[i%6],.8)
  a.box(f'LIV.DisplayBook.{i+1:02}.Pages',(x,8.94,.99+h/2),(.038,.22,h),cream,.001)
  for dx in [-.021,.021]:a.box(f'LIV.DisplayBook.{i+1:02}.Cover.{dx}',(x+dx,8.94,.99+h/2),(.003,.224,h+.007),m)
  a.box(f'LIV.DisplayBook.{i+1:02}.Spine',(x,8.826,.99+h/2),(.044,.006,h+.007),m)
  a.photo_plane(f'LIV.DisplayBook.{i+1:02}.Title',(x,8.822,.99+h/2),(-.041,0,0),(0,0,h),8)
 for i in range(9):
  x=-2.26+i*.045;m=a.mat(f'Tea carton tone{i%3}',[(.63,.035,.022),(.035,.26,.11),(.68,.49,.16)][i%3]);a.box(f'LIV.TeaCarton.{i+1}',(x,9.06,1.263),(.043,.057,.12),m,.002)
 for i in range(5):a.cyl(f'LIV.TeaTin.{i+1}',(-2.25+i*.066,8.91,1.222),.029,.04,a.mat('Green tea tins',(.08,.38,.19)),24)
 a.cyl('LIV.Cabinet.WhiteCup',(-1.83,8.91,1.264),.032,.13,white,32)
 a.lathe('LIV.Cabinet.PaleJar',(-1.78,9.04,1.20),[(.034,0),(.045,.03),(.044,.14),(.036,.15)],cream);a.cyl('LIV.Cabinet.JarLid',(-1.78,9.04,1.36),.04,.016,white)
 for i in range(3):a.box(f'LIV.BlackFolio.{i+1}',(-.75,8.95,1.015+i*.028),(.31,.26,.025),black,.012)
 a.box('LIV.UprightSoftCase',(-.61,9.01,1.145),(.22,.10,.30),black,.05)
 for n,x in enumerate([-1.51,-1.10,-.71],1):a.photo_plane(f'LIV.LeaningDisplayPrint.{n}',(x,8.712,.61),(-.29,0,0),(0,0,.37),8,black)
 for n,(x,z) in enumerate([(-2.14,.89),(-1.91,.89),(-2.12,.54),(-1.91,.54)],1):
  a.box(f'LIV.CabinetCubbyContent.{n}',(x,8.92,z),(.20,.23,.10),a.mat(f'Cubby packaging {n}',palette[n]),.03)
 a.box('LIV.Cabinet.FlatBook',(-1.39,8.85,1.005),(.23,.18,.013),a.mat('Printed paper warm',(.79,.36,.2)),.002)
 a.rod('LIV.Cabinet.Pen',(-.95,8.88,1.022),(-.83,8.88,1.022),.003,black)
 a.box('LIV.Cabinet.Clamp',(-1.35,8.8,1.04),(.035,.044,.067),black,.004)
 # Plaques, alarms and utility items observed on walls.
 for n,(c,u) in enumerate([((-6.92,6.00,1.37),(.20,0,0)),((-3.15,5.97,1.38),(.23,0,0)),((-6.88,9.17,1.38),(-.20,0,0)),((-1.28,9.165,1.39),(-.26,0,0))],1):a.photo_plane(f'LIV.Plaque.{n}',c,u,(0,0,.17),8,black)
 a.photo_plane('LIV.GreenFrame',(-.52,8.39,1.41),(0,-.24,0),(0,0,.18),8,black)
 a.rod('LIV.RiserPipe',(-7.28,9.11,.02),(-7.28,9.11,2.48),.025,white)
 a.rod('LIV.RiserPipe.Branch',(-7.28,9.11,2.13),(-7.07,9.11,2.13),.024,white)
 red=a.mat('Alarm red plastic',(.62,.018,.015),.4)
 a.box('LIV.Alarm.High',(-6.75,9.165,2.22),(.07,.04,.105),white,.008);a.box('LIV.Alarm.Lens',(-6.75,9.137,2.21),(.041,.02,.041),red,.007)
 a.box('LIV.Alarm.Callpoint',(-6.56,9.15,1.36),(.105,.025,.10),red,.005)
 for i,(x,y) in enumerate([(-3.3,9.16),(-6.9,6.01),(-.53,7.12),(-8.75,7.70)],1):a.box(f'LIV.Outlet.{i}',(x,y,.29),(.08,.018,.08),white,.003)
 for i,(x,y) in enumerate([(-.54,6.45),(-6.95,6.01)],1):a.box(f'LIV.Switch.{i}',(x,y,1.21),(.08,.019,.08),black,.004)
 a.box('LIV.Console.PowerStrip',(-4.43,6.21,.524),(.20,.05,.023),white,.009)
 a.curve('LIV.TV.Lead',[(-4.84,6.06,1.03),(-4.80,6.03,.83),(-4.61,6.08,.70),(-4.58,6.20,.52)],.004,black)
 a.box('LIV.Speaker.Remote',(-6.0,6.21,.86),(.09,.033,.009),black,.003)
 a.photo_plane('LIV.Niche.Landscape',(-8.98,7.502,1.44),(0,.398,0),(0,0,1.02),8)
 a.box('LIV.Niche.BlackBag',(-8.77,7.52,.12),(.33,.23,.22),black,.04)
