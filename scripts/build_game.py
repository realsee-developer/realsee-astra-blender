import math,bpy

def build_game(ROOT,a):
 a.area_collection('Game_Fixtures','data/cube-map/6_f.jpg;6_r.jpg;6_b.jpg;6_l.jpg;6_u.jpg;6_d.jpg;data/model/obj-high-resolution-model/block_0.obj')
 black=a.mat('Game black laminate',(.017,.012,.024),.36);silver=a.mat('Foosball polished metal',(.48,.50,.55),.22,.86);green=a.mat('Foosball green pitch',(.20,.46,.12),.6);line=a.mat('Pitch ivory lines',(.91,.93,.81),.65);blue=a.mat('Foosball blue team',(.025,.10,.52),.28);red=a.mat('Foosball red team',(.42,.025,.03),.34);lilac=a.mat('Game ribbed lilac',(.46,.30,.64),.62);led=a.mat('Lilac LED',(.55,.17,1),.25,0,4);edge=a.mat('Game white edge trims',(.8,.7,.87),.42)
 # One table, the far-wall second appearance is a reflection.
 x,y=-5.94,4.31;a.group('GAME.Foosball',(x,y,0))
 for dx in [-.57,.57]:
  for dy in [-.27,.27]:
   a.box(f'GAME.Foosball.Leg.{dx}.{dy}',(x+dx,y+dy,.37),(.085,.085,.72),black,.008)
   a.cyl(f'GAME.Foosball.Foot.{dx}.{dy}',(x+dx,y+dy,.025),.051,.035,silver,16)
 a.box('GAME.Foosball.Field',(x,y,.835),(1.16,.66,.028),green,.004)
 for dy in [-.40,.40]:
  a.box(f'GAME.Foosball.LongSide.{dy}',(x,y+dy,.82),(1.42,.075,.34),black,.015)
  a.box(f'GAME.Foosball.TopRail.{dy}',(x,y+dy,.99),(1.42,.082,.025),silver,.008)
 for dx in [-.70,.70]:
  a.box(f'GAME.Foosball.End.{dx}',(x+dx,y,.82),(.06,.78,.34),black,.012)
  # Goal mouth represented by independent dark recessed opening and surrounding frame.
  a.box(f'GAME.Foosball.Goal.{dx}',(x+dx-math.copysign(.031,dx),y,.865),(.009,.19,.095),black)
  for dy in [-.29,.29]:a.box(f'GAME.Foosball.CornerCap.{dx}.{dy}',(x+dx,y+dy,1.005),(.12,.23,.025),silver,.025)
 # pitch markings genuine thin curves
 a.curve('GAME.Foosball.PitchBoundary',[(x-.555,y-.30,.853),(x+.555,y-.30,.853),(x+.555,y+.30,.853),(x-.555,y+.30,.853)],.003,line,True)
 a.rod('GAME.Foosball.CenterLine',(x,y-.3,.853),(x,y+.3,.853),.003,line)
 a.curve('GAME.Foosball.CenterCircle',[(x+.11*math.cos(j*2*math.pi/48),y+.11*math.sin(j*2*math.pi/48),.854) for j in range(48)],.003,line,True)
 rows=[(-.51,1,red),(-.39,2,red),(-.25,3,blue),(-.09,5,red),(.09,5,blue),(.25,3,red),(.39,2,blue),(.51,1,blue)]
 for k,(dx,count,mat) in enumerate(rows,1):
  xx=x+dx;a.rod(f'GAME.Foosball.Rod.{k}',(xx,y-.73,.952),(xx,y+.66,.952),.007,silver)
  side=-1 if mat==blue else 1;a.rod(f'GAME.Foosball.Handle.{k}',(xx,y+side*.54,.952),(xx,y+side*.73,.952),.017,mat)
  for j in range(count):
   yy=y+(j-(count-1)/2)*min(.17,.51/max(1,count-1))
   a.ball(f'GAME.Foosball.Player.{k}.{j}.Head',(xx,yy,1.018),(.021,.021,.025),mat)
   a.box(f'GAME.Foosball.Player.{k}.{j}.Torso',(xx,yy,.970),(.037,.027,.065),mat,.008)
   a.box(f'GAME.Foosball.Player.{k}.{j}.Foot',(xx,yy,.91),(.037,.018,.067),mat,.005)
 for dx,mat in [(-.60,red),(.60,blue)]:
  a.rod(f'GAME.Foosball.ScoreRail.{dx}',(x+dx,y-.23,1.047),(x+dx,y+.23,1.047),.004,silver)
  for j in range(10):a.ball(f'GAME.Foosball.ScoreBead.{dx}.{j}',(x+dx,y-.20+j*.035,1.047),(.012,.013,.013),mat)
 # Correct table height against local horizontal PLY returns (field median 0.777m).
 table=bpy.data.objects['GAME.Foosball']
 for o in table.children:
  if '.Foot.' in o.name:continue
  if '.Leg.' in o.name:o.location.z-=.035;o.scale.z*=.65/.72
  else:o.location.z-=.070
 for dx in [-.70,.70]:
  end=bpy.data.objects[f'GAME.Foosball.End.{dx}']
  cutter=a.box(f'GAME.Foosball.GoalOpeningCutter.{dx}',(x+dx,y,.795),(.14,.19,.105),black)
  cutter.hide_render=True;cutter.hide_set(True);cutter['geometry_class']='non-rendering editable Boolean tool'
  mod=end.modifiers.new('Editable real goal mouth','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
  recess=bpy.data.objects[f'GAME.Foosball.Goal.{dx}'];recess.hide_render=True;recess.hide_set(True)
 a.parent=None
 # Chamfered mirror, no photograph reflection is used as geometry.
 mirror=a.mat('Game mirror',(.9,.87,.93),.012,1)
 yz=[(2.98,.002),(5.67,.002),(5.75,.082),(5.75,2.255),(5.66,2.345),(3.09,2.345),(2.98,2.255)]
 o=a.mesh('GAME.Mirror.Glass',[(-7.53,yy,zz) for yy,zz in yz],[tuple(range(len(yz)))],mirror);sol=o.modifiers.new('Mirror glass thickness','SOLIDIFY');sol.thickness=.006
 a.curve('GAME.Mirror.Perimeter',[(-7.513,yy,zz) for yy,zz in yz],.021,edge,True)
 a.box('GAME.Mirror.BlackBase',(-7.505,4.55,.28),(.022,1.34,.24),black)
 # Galaxy wall graphics are actual source photographs projected onto flat printed panels.
 a.photo_plane('GAME.GalaxyBackdrop',(-5.56,5.80,1.28),(4.02,0,0),(0,0,2.48),6)
 # Central ribbed wall sculptural panel with angled shoulders, actual local geometry.
 poly=[(-6.59,2.42),(-4.83,2.42),(-4.83,1.86),(-5.21,1.50),(-5.21,.07),(-6.22,.07),(-6.22,1.50),(-6.59,1.84)]
 o=a.mesh('GAME.RibbedPanel.Body',[(xx,5.795,z) for xx,z in poly],[tuple(reversed(range(len(poly))))],lilac);sol=o.modifiers.new('Panel backing thickness','SOLIDIFY');sol.thickness=.008
 for j in range(57):
  xx=-6.57+j*1.72/56
  low=.07 if -6.22<=xx<=-5.21 else (1.50+(-6.22-xx)*.34/.37 if xx< -6.22 else 1.50+(xx+5.21)*.36/.38)
  a.rod(f'GAME.RibbedPanel.Flute.{j}',(xx,5.784,low),(xx,5.784,2.40),.003,lilac,8)
 a.curve('GAME.RibbedPanel.LEDOutline',[(xx,5.784,z) for xx,z in poly],.008,led,True)
 # South wall floor-to-high vertical light strips; spacing from registered scan/photo.
 for j,xx in enumerate([-7.223,-6.739,-6.257,-5.765,-5.289,-4.797],1):
  o=a.box(f'GAME.WallLED.South.{j}',(xx,2.891,.9835),(.017,.012,1.867),led,.003);o['source']='data/cube-map/6_f.jpg; research/game-led-source-rays.json';o['evidence_status']='measured registered photograph ray intersection; top1.917m, bottom0.05m'
 # East wall one strip beside controls. Switches remain separate.
 for j,(yy,zz,height) in enumerate([(5.363,1.006,1.8435),(4.875,.995,1.8615)],1):
  o=a.box(f'GAME.WallLED.East.{j}',(-3.553,yy,zz),(.012,.017,height),led,.003);o['source']='data/cube-map/6_b.jpg; research/game-led-source-rays.json';o['evidence_status']='measured registered photograph ray intersections'
 for j in range(3):a.box(f'GAME.ControlSwitch.{j+1}',(-3.557,4.82+j*.085,1.19),(.014,.075,.09),edge,.003)
 a.box('GAME.ControlPlate.South',(-5.58,2.913,1.22),(.21,.018,.13),black,.003)
 # Discrete waste carton and liner near northeast corner.
 carton=a.mat('Cardboard dusty mauve',(.46,.28,.35),.95);a.group('GAME.WasteCarton',(-3.83,5.52,0))
 for xx in [-4.04,-3.62]:a.box(f'GAME.WasteCarton.Side.{xx}',(xx,5.50,.18),(.012,.35,.35),carton)
 for yy in [5.33,5.68]:a.box(f'GAME.WasteCarton.Side.{yy}',(-3.83,yy,.18),(.42,.012,.35),carton)
 a.scan_part('GAME.WasteCarton.Bag',[[-4.08,5.26,.27],[-3.58,5.74,.55]])
 a.parent=None
