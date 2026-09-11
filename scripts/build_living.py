"""Living/dining furnishings reconstructed from registered scan and station 8."""
import math,bpy

def build_living(ROOT,a):
 a.area_collection('LivingDining_Furniture','data/cube-map/8_f.jpg;8_r.jpg;8_b.jpg;8_l.jpg;8_d.jpg;data/model/obj-high-resolution-model/block_0.obj')
 wood=a.mat('Living honey oak',(.42,.18,.065),.38);black=a.mat('Charcoal equipment',(.012,.014,.018),.32);cream=a.mat('Sofa cream woven upholstery',(.78,.72,.61),.85);tan=a.mat('Sofa caramel leather shell',(.47,.22,.095),.56);cane=a.mat('Natural woven cane',(.61,.43,.22),.65);metal=a.mat('Satin black metal',(.02,.025,.026),.3,.7);white=a.mat('Appliance white',(.86,.85,.8),.28)
 # Two independent sofa sections; separate carcass, feet, seat, back, arm and decorative cushions.
 for k,(x,w) in enumerate([(-5.66,1.30),(-4.36,1.30)],1):
  a.group(f'LIV.SOFA.{k:02}',(x,8.7,0))
  a.box(f'LIV.SOFA.{k:02}.Carcass',(x,8.75,.24),(w,.88,.25),tan,.085)
  a.box(f'LIV.SOFA.{k:02}.BackShell',(x,9.035,.54),(w,.15,.44),tan,.05)
  for dx in [-w/2+.13,w/2-.13]:
   for y in [8.41,9.01]:a.cyl(f'LIV.SOFA.{k:02}.Foot.{dx:.2f}.{y}',(x+dx,y,.11),.029,.20,wood,16)
  for j in range(2):
   xx=x+(j-.5)*w/2
   a.box(f'LIV.SOFA.{k:02}.Seat.{j+1}',(xx,8.64,.38),(w/2-.04,.73,.16),cream,.095)
   o=a.box(f'LIV.SOFA.{k:02}.BackCushion.{j+1}',(xx,8.97,.59),(w/2-.03,.23,.38),cream,.095);o.rotation_euler.x=-.13
  if k==1:xx=x-w/2+.08
  else:xx=x+w/2-.08
  a.box(f'LIV.SOFA.{k:02}.Arm',(xx,8.73,.49),(.16,.81,.23),cream,.07)
  a.parent=None
 # Captured loose cushions are independently segmented rather than merging into carcass.
 for i,(x1,x2) in enumerate([(-6.29,-5.99),(-5.94,-5.62),(-5.51,-5.20),(-4.83,-4.45),(-4.34,-3.99)],1):
  a.scan_part(f'LIV.CUSHION.{i:02}',[[x1,8.36,.45],[x2,9.04,.80]])
 # Source8f: paired drawers at each end, two independently sliding ribbed panels.
 console=a.group('LIV.TVConsole',(-5.21,6.14,0))
 for name,z in [('Top',.510),('Bottom',.196)]:a.box('LIV.TVConsole.'+name,(-5.21,6.18,z),(2.18,.40,.036),wood,.010)
 a.box('LIV.TVConsole.Back',(-5.21,5.995,.351),(2.18,.025,.276),wood,.005)
 for j,x in enumerate([-6.285,-5.835,-4.585,-4.135]):a.box(f'LIV.TVConsole.Partition.{j}',(x,6.18,.351),(.030,.37,.276),wood,.004)
 for x in [-6.20,-4.22]:
  for y in [6.04,6.31]:a.cyl(f'LIV.TVConsole.Foot.{x}.{y}',(x,y,.103),.024,.198,wood,16,r2=.018)
 brass=a.mat('Console brass knobs',(.31,.24,.075),.29,.7)
 for j,x in enumerate([-6.06,-4.36],1):
  for k,z in enumerate([.274,.423],1):
   a.box(f'LIV.TVConsole.Drawer.{j}.{k}',(x,6.363,z),(.415,.030,.134),wood,.006)
   a.box(f'LIV.TVConsole.Pull.{j}.{k}',(x,6.389,z+.008),(.029,.025,.012),brass,.002)
 rib=a.mat('TV console ribbed translucent olive glass',(.26,.24,.13),.32,.05)
 bs=rib.node_tree.nodes['Principled BSDF'];bs.inputs['Transmission Weight'].default_value=.38;bs.inputs['IOR'].default_value=1.48
 rail=a.mat('TV console aluminum rails',(.42,.43,.40),.28,.8)
 for z in [.220,.484]:a.rod(f'LIV.TVConsole.SliderRail.{z}',(-5.82,6.389,z),(-4.60,6.389,z),.005,rail)
 for j,(x,y) in enumerate([(-5.52,6.380),(-4.92,6.394)],1):
  a.parent=console;panel=a.box(f'LIV.TVConsole.SlidingPanel.{j}',(x,y,.350),(.609,.010,.254),rib,.001)
  panel['operation']='Translate X independently along front rails; rib geometry and pull follow panel';bpy.context.view_layer.update();a.parent=panel
  for k in range(77):a.cyl(f'LIV.TVConsole.SlidingPanel.{j}.Flute.{k}',(x-.300+k*.0078,y+.006,.350),.0022,.254,rib,6)
  a.box(f'LIV.TVConsole.SlidingPanel.{j}.Pull',(x+(-.25 if j==1 else .25),y+.020,.35),(.020,.028,.010),brass,.002)
 a.parent=None
 a.box('LIV.TV.Panel',(-4.91,6.09,1.43),(1.18,.057,.70),black,.015)
 a.box('LIV.TV.Screen',(-4.91,6.123,1.43),(1.15,.009,.67),a.mat('TV reflective screen',(.008,.012,.017),.13,.30),.006)
 for i,x in enumerate([-6.00]):
  a.box(f'LIV.Speaker.{i+1}',(x,6.21,.72),(.23,.22,.25),wood,.016);a.cyl(f'LIV.Speaker.{i+1}.Cone',(x,6.335,.72),.069,.01,black,32,rot=(math.pi/2,0,0))
 # Wicker low oval coffee table, glass surface and woven lower shelf.
 a.group('LIV.CoffeeTable',(-3.37,8.11,0));rim=a.mat('Coffee table pale rattan',(.75,.65,.44),.57)
 for z in [.15,.408]:
  pts=[(-3.37+.35*math.cos(t),8.11+.35*math.sin(t),z) for t in [j*2*math.pi/80 for j in range(80)]];a.curve(f'LIV.CoffeeTable.Rim.{z}',pts,.028,rim,True)
  for i in range(-10,11):
   x=i*.031;h=.323*math.sqrt(max(0,1-(x/.35)**2));a.rod(f'LIV.CoffeeTable.Slat.{z}.{i}',(-3.37+x,8.11-h,z),(-3.37+x,8.11+h,z),.005,rim)
 for dx in [-.23,.23]:
  for dy in [-.23,.23]:a.rod(f'LIV.CoffeeTable.Leg.{dx}.{dy}',(-3.37+dx,8.11+dy,.03),(-3.37+dx,8.11+dy,.408),.022,rim)
 a.parent=None
 # Dining table length follows raw scan top footprint.
 a.group('LIV.DiningTable',(-1.91,8.17,0));a.box('LIV.DiningTable.Top',(-1.91,8.17,.76),(.79,1.78,.055),wood,.028)
 for x in [-2.23,-1.59]:
  for y in [7.42,8.91]:a.box(f'LIV.DiningTable.Leg.{x}.{y}',(x,y,.38),(.055,.055,.73),wood,.008)
 a.parent=None
 # Four cane-back chairs; hand-shaped curved back outlines and woven crossings.
 for n,(x,y,ang) in enumerate([(-2.69,8.62,-math.pi/2),(-2.72,7.86,-math.pi/2),(-1.13,8.57,math.pi/2),(-1.08,7.77,math.pi/2)],1):
  a.group(f'LIV.DiningChair.{n}',(x,y,0))
  def P(v):return (x+v[0]*math.cos(ang)-v[1]*math.sin(ang),y+v[0]*math.sin(ang)+v[1]*math.cos(ang),v[2])
  a.box(f'LIV.DiningChair.{n}.Seat',P((0,0,.45)),(.42,.44,.045),wood,.06,ang)
  for dx in [-.17,.17]:
   for dy in [-.17,.17]:a.rod(f'LIV.DiningChair.{n}.Leg.{dx}.{dy}',P((dx*1.13,dy*1.12,.015)),P((dx,dy,.44)),.020,wood)
  outline=[(-.215,.17,.49),(-.224,.19,.79),(-.18,.20,.89),(.18,.20,.89),(.224,.19,.79),(.215,.17,.49)]
  a.curve(f'LIV.DiningChair.{n}.BackFrame',[P(v) for v in outline],.026,wood)
  for j in range(17):
   xx=-.18+j*.0225;a.rod(f'LIV.DiningChair.{n}.CaneV.{j}',P((xx,.194,.61)),P((xx,.194,.85)),.0025,cane,6)
  for j in range(12):
   zz=.61+j*.022;a.rod(f'LIV.DiningChair.{n}.CaneH.{j}',P((-.18,.193,zz)),P((.18,.193,zz)),.0025,cane,6)
  a.parent=None
 # Three cabinet bays against dining north wall with distinct doors/shelves/rattan fronts.
 for n,(x,w,h) in enumerate([(-2.00,.59,1.09),(-1.41,.59,.88),(-.82,.59,.88)],1):
  a.group(f'LIV.Cabinet.{n}',(x,8.96,0))
  a.box(f'LIV.Cabinet.{n}.Back',(x,9.14,h/2+.10),(w,.035,h),wood,.008)
  for xx in [x-w/2+.025,x+w/2-.025]:a.box(f'LIV.Cabinet.{n}.Side.{xx}',(xx,8.975,h/2+.10),(.04,.37,h),wood,.008)
  for z in [.13,h+.10]:a.box(f'LIV.Cabinet.{n}.Shelf.{z}',(x,8.975,z),(w,.40,.04),wood,.008)
  for xx in [x-w*.37,x+w*.37]:a.box(f'LIV.Cabinet.{n}.Foot.{xx}',(xx,8.97,.07),(.05,.29,.14),wood,.008)
  if n==1:
   for z in [.57,.91]:a.box(f'LIV.Cabinet.{n}.Shelf.{z}',(x,8.975,z),(w,.40,.035),wood)
  else:
   a.box(f'LIV.Cabinet.{n}.Door',(x,8.755,.55),(w-.09,.03,.66),wood,.012)
   for j in range(18):
    xx=x-w*.40+j*w*.8/17;a.rod(f'LIV.Cabinet.{n}.RattanV.{j}',(xx,8.733,.28),(xx,8.733,.81),.0025,cane,6)
   for j in range(23):
    zz=.28+j*.53/22;a.rod(f'LIV.Cabinet.{n}.RattanH.{j}',(x-w*.4,8.734,zz),(x+w*.4,8.734,zz),.0025,cane,6)
  a.parent=None
 # Individual book spines and equipment above cabinets from exact scan; meaningful local geometry.
 for i,(lo,hi) in enumerate([([-2.29,8.78,1.20],[-1.72,9.14,1.44]),([-1.71,8.78,.995],[-1.56,9.14,1.36]),([-1.55,8.78,.995],[-1.41,9.14,1.36]),([-1.40,8.78,.995],[-1.24,9.14,1.39]),([-1.23,8.78,.995],[-1.09,9.14,1.36]),([-1.08,8.78,.995],[-.91,9.14,1.37]),([-.90,8.78,.995],[-.55,9.14,1.30])],1):a.scan_part(f'LIV.CabinetContent.{i:02}',[lo,hi])
 # Three clear drink bottles, labels and screw caps remain independent editable parts.
 glass=a.mat('Clear water bottle',(.82,.88,.92),.16);bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=.75
 for i,(xx,yy,h) in enumerate([(-2.02,8.64,.22),(-1.91,8.59,.23),(-1.78,8.31,.25)],1):
  a.lathe(f'LIV.TableBottle.{i}.Body',(xx,yy,.79),[(.028,0),(.03,.03),(.03,h-.05),(.013,h-.02),(.013,h)],glass,24)
  a.cyl(f'LIV.TableBottle.{i}.Cap',(xx,yy,.79+h),.016,.014,white,20)
  if i<3:a.cyl(f'LIV.TableBottle.{i}.PaperLabel',(xx,yy,.79+h*.45),.0305,.05,white,24)
 a.box('LIV.TableScanner.Base',(-1.89,7.57,.80),(.43,.17,.034),black,.012)
 a.box('LIV.TableScanner.Upright',(-1.89,7.60,.90),(.43,.055,.19),black,.015)
 a.curve('LIV.TableScanner.Cable',[(-1.66,7.57,.81),(-1.54,7.58,.80),(-1.52,7.76,.80),(-1.69,7.81,.80),(-1.81,7.72,.80)],.004,black)
 a.box('LIV.TablePhone',(-2.02,8.38,.80),(.14,.07,.01),black,.009)
 a.curve('LIV.TableCameraStrap',[(-2.04,8.31,.80),(-2.19,8.34,.80),(-2.16,8.62,.80),(-2.06,8.57,.80)],.006,black)
 a.box('LIV.TableCandy',(-1.95,8.12,.80),(.07,.035,.012),a.mat('Pink packet',(.77,.2,.28)),.005)
 # Accent chair and plants are complex measured meshes, parted by function.
 for name,bounds in [
  ('LIV.AccentChair.Seat',[[-7.49,8.65,.25],[-6.97,9.20,.55]]),('LIV.AccentChair.Back',[[-7.49,8.81,.55],[-6.97,9.20,1.13]])]:a.scan_part(name,bounds)
 for x in [-7.4,-7.05]:
  for y in [8.75,9.07]:a.cyl(f'LIV.AccentChair.Foot.{x}.{y}',(x,y,.13),.022,.25,wood,12)
 a.box('LIV.OrangeStool.Seat',(-7.24,6.73,.45),(.34,.33,.07),a.mat('Orange fabric',(.73,.27,.055)),.025)
 for x in [-7.37,-7.11]:
  for y in [6.61,6.85]:a.rod(f'LIV.OrangeStool.Leg.{x}.{y}',(x,y,.02),(x,y,.42),.02,wood)
 # Draped curtains as actual wavy fabric surfaces, full height, separate two leaves.
 for n,(y0,y1) in enumerate([(5.98,7.22),(7.77,9.17)],1):
  vs=[];fs=[];N=64
  for z in [.03,2.44]:
   for j in range(N+1):
    y=y0+(y1-y0)*j/N;vs.append((-7.42+.032*math.sin(j*math.pi/2),y,z))
  for j in range(N):fs.append((j,j+1,N+j+2,N+j+1))
  o=a.mesh(f'LIV.Curtain.{n}',vs,fs,cream);m=o.modifiers.new('Editable cloth thickness','SOLIDIFY');m.thickness=.003
 # Home appliance near doorway, independent tank/lid/base.
 a.group('LIV.CylindricalAppliance',(-.77,7.18,0));a.lathe('LIV.CylindricalAppliance.Body',(-.77,7.18,.07),[(.15,0),(.17,.04),(.165,.47),(.14,.50)],white);a.cyl('LIV.CylindricalAppliance.Lid',(-.77,7.18,.58),.16,.04,black);a.box('LIV.CylindricalAppliance.Window',(-.77,7.005,.26),(.19,.018,.18),a.mat('Appliance translucent blue gray',(.16,.20,.22)),.025);a.parent=None
 for i in range(2):
  a.box(f'LIV.Appliance.PowerAdapter.{i}',(-1.10+i*.13,7.02,.043),(.095,.067,.055),black,.007)
  a.curve(f'LIV.Appliance.PowerLead.{i}',[(-1.10+i*.13,7.02,.025),(-1.12+i*.16,6.90,.022),(-.95,6.85,.021),(-.75,7.05,.035)],.003,black)
