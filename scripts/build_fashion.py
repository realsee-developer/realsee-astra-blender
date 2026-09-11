"""Rebuild photographed fashion display fixtures and independently editable local contents.
Invoked by primary scene build, with raw-PLY XY and floor-normalized Z.
"""
import bpy, math, json
from mathutils import Vector

def build_fashion(ROOT,api):
 api.area_collection('Fashion_Fixtures','data/panorama/3.jpg;data/cube-map/3_f.jpg;data/cube-map/3_r.jpg;data/cube-map/3_b.jpg;data/cube-map/3_l.jpg;data/cube-map/3_u.jpg;data/cube-map/3_d.jpg')
 black=api.mat('Fashion powder-coated charcoal steel',(0.025,.027,.028),.4)
 gold=api.mat('Fashion satin brass',(.62,.39,.075),.32,.72)
 white=api.mat('Fashion off-white painted shelf',(.78,.79,.76),.48)
 silver=api.mat('Fashion aluminum extrusions',(.55,.58,.59),.3,.75)
 rubber=api.mat('Fashion black rubber',(.015,.017,.018),.65)
 gray=api.mat('Fashion pale gray plastic',(.4,.43,.45),.54)
 shelfmat=api.mat('Fashion dark ash shelves',(.032,.035,.036),.6)
 glow=api.mat('Fashion warm-white lamp diffuser',(.88,.9,1),.25,emission=3)
 # Four black rack bays; structural parts remain editable and separately selectable.
 for side,y in [('S',-.205),('N',2.42)]:
  x0,x1=(-6.88,-4.16) if side=='S' else (-7.01,-4.25)
  api.parent=None;api.group('FAS-RACK-'+side,((x0+x1)/2,y,0))
  api.box(f'FAS-RACK-{side}_base',((x0+x1)/2,y,.055),(x1-x0,.53,.05),shelfmat,.008)
  for j,x in enumerate([x0, -5.70 if side=='S' else -5.50, x1]):
   api.box(f'FAS-RACK-{side}_upright_{j+1}',(x,y, .827),(.028,.032,1.544),black,.004)
  api.box(f'FAS-RACK-{side}_top_rail',((x0+x1)/2,y,1.598),(x1-x0,.028,.028),black,.004)
  # two narrow shelf towers; a shared upright is also a bay separator.
  towerxs=[-6.70,-5.48] if side=='S' else [-5.70,-4.46]
  for j,x in enumerate(towerxs):
   for z in [.45,.80,1.20]:api.box(f'FAS-RACK-{side}_shelf{j+1}_{int(z*100)}',(x,y,z),(.43,.53,.025),shelfmat,.003)
   for yy in [y-.18,y+.18]:
    api.box(f'FAS-RACK-{side}_shelfpost{j+1}_{yy:.2f}',(x+.205,yy,.823),(.021,.025,1.515),black,.002)
  for j,x in enumerate([x0+.05,x1-.05]):
   for k,yy in enumerate([y-.2,y+.2]):api.cyl(f'FAS-RACK-{side}_caster{j}{k}',(x,yy,.035),.022,.025,rubber,16,rot=(math.pi/2,0,0))
 # Gold six-level rectangular display cages.
 for side,y in [('S',-.245),('N',2.405)]:
  api.parent=None;api.group('FAS-GOLD-'+side,(-7.62,y,0))
  for k,x in enumerate([-8.16,-7.08]):
   for j,yy in enumerate([y-.235,y+.235]):api.box(f'FAS-GOLD-{side}_corner{k}{j}',(x,yy,1.025),(.018,.018,2.05),gold,.002)
  for k,z in enumerate([.07,.40,.735,1.07,1.405,1.74]):
   api.box(f'FAS-GOLD-{side}_shelf{k+1}',(-7.62,y,z),(1.08,.48,.018),white,.002)
   for yy in [y-.24,y+.24]:api.box(f'FAS-GOLD-{side}_edge{k}_{yy:.2f}',(-7.62,yy,z),(1.10,.017,.02),gold,.002)
  for yy in [y-.24,y+.24]:api.box(f'FAS-GOLD-{side}_top_edge_{yy:.2f}',(-7.62,yy,2.045),(1.10,.018,.018),gold,.002)
  # thin upright bars on sides/back, clearly visible through the shelves
  for j,x in enumerate([-8.16,-7.89,-7.62,-7.35,-7.08]):api.box(f'FAS-GOLD-{side}_backbar{j}',(x,y+(-.235 if side=='S' else .235),1.025),(.010,.010,2.04),gold,.001)
  for k,x in enumerate([-8.16,-7.08]):
   for j,yy in enumerate([y-.08,y+.08]):api.box(f'FAS-GOLD-{side}_sidebar{k}{j}',(x,yy,1.025),(.010,.010,2.04),gold,.001)
 api.parent=None
 # Actual complex source surfaces are isolated item by item, leaving native racks entirely rebuilt.
 # Scan bounds remove rear walls and shelf boards; original captured color/UVs retained locally.
 def cut(name,x0,x1,y0,y1,z0,z1):
  o=api.scan_part(name,[[x0,y0,z0],[x1,y1,z1]])
  o['coverage_id']=name.split('__')[0];o['reconstruction_note']='Identifiable local object surface extracted from registered scan; independent Mesh, original UV; occluded back surfaces not claimed measured.'
  return o
 # Four first-bay garment assemblies plus second-bay layered garments. x cuts follow observed hangers.
 garmentbounds=[('FAS-GARMENT-01',-4.46,-4.20,.40,1.49),('FAS-GARMENT-02',-4.83,-4.46,.38,1.51),('FAS-GARMENT-03',-5.02,-4.83,.32,1.51),('FAS-GARMENT-04',-5.26,-5.02,.27,1.54),('FAS-GARMENT-05',-5.97,-5.72,.66,1.51),('FAS-GARMENT-06',-6.22,-5.97,.68,1.51),('FAS-GARMENT-07',-6.36,-6.22,.72,1.52),('FAS-GARMENT-08',-6.56,-6.36,.78,1.52),('FAS-GARMENT-09',-6.72,-6.56,.83,1.52)]
 for name,x0,x1,z0,z1 in garmentbounds:cut(name,x0,x1,-.46,.12,z0,z1)
 # Native hangers add continuous hooks and triangular supports where the sparse scan missed thin wire.
 for j,x in enumerate([-4.33,-4.64,-4.92,-5.12,-5.84,-6.10,-6.30,-6.46,-6.60]):
  y=-.20
  api.curve(f'FAS-HANGER-S-{j+1:02}',[(x-.16,y,1.43),(x,y,1.51),(x+.16,y,1.43),(x-.16,y,1.43)],.008,api.mat('Fashion stained hanger wood',(.26,.08,.038),.43))
  api.curve(f'FAS-HOOK-S-{j+1:02}',[(x,y,1.51),(x,y,1.565),(x+.02,y,1.589),(x+.04,y,1.57)],.003,silver)
 for j,x in enumerate([-6.96,-6.89,-6.82,-6.75,-6.68,-6.61]):
  api.curve(f'FAS-HANGERS-EMPTY-{j+1:02}',[(x-.12,2.42,1.43),(x,2.42,1.54),(x+.12,2.42,1.43),(x-.12,2.42,1.43)],.009,black)
  api.curve(f'FAS-HANGERS-EMPTY-{j+1:02}_hook',[(x,2.42,1.54),(x,2.42,1.60),(x+.025,2.42,1.62),(x+.04,2.42,1.60)],.0025,silver)
 # Discrete display items, using measured local surfaces where their silhouette is identifiable.
 for spec in [
 ('FAS-HAT-WIDE',-5.68,-5.28,-.46,.16,1.22,1.53),('FAS-CUSHION-WHITE',-5.69,-5.29,-.47,.18,.88,1.24),('FAS-HAT-FEDORA',-6.94,-6.57,-.45,.12,1.205,1.4),
 ('FAS-SHOES-CREAM-S',-5.18,-4.76,-.45,.13,.075,.28),('FAS-SHOES-BLACK',-6.24,-5.93,-.42,.14,.071,.24),('FAS-SHOES-BROWN',-6.91,-6.54,-.46,.13,.475,.7),('FAS-SHOES-OXFORD',-6.95,-6.59,-.47,.15,.15,.37),('FAS-BAG-CYAN',-6.52,-6.23,-.47,.13,.074,.25),
 ('FAS-JEWELRY-TRAY',-5.69,-5.28,-.46,.15,.465,.59),('FAS-PERFUME',-5.70,-5.57,-.43,.1,1.23,1.4),
 ('FAS-BAG-N-DUFFEL',-6.99,-6.35,2.14,2.66,.078,.39),('FAS-BAG-N-WHITE',-6.36,-6.12,2.11,2.67,.077,.24),('FAS-CAP-N',-6.19,-5.99,2.1,2.67,.078,.22),('FAS-SHOES-CREAM-N',-5.36,-5.13,2.09,2.66,.076,.25),('FAS-CUSHION-GRAY',-5.07,-4.61,2.11,2.65,.075,.40),('FAS-FOLDED-SHIRT',-5.17,-5.04,2.06,2.65,.09,.38)]:cut(*spec)
 # Clean native bag bodies, handles and closures replace the source scan's torn/disconnected thin surfaces.
 # Rounded ring meshes preserve bag silhouettes; each bag is an independently movable assembly.
 def bag(name,x,y,z,w,h,d,color,kind='tote',front=-1,pattern=False):
  api.parent=None;grp=api.group(name,(x,y,z));bpy.context.view_layer.update();grp['coverage_id']=name
  mat=api.mat(name+'_leather',color,.48)
  if pattern:
   nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexChecker');tex.inputs['Color1'].default_value=(*color,1);tex.inputs['Color2'].default_value=(*(min(1,c*1.5+.04) for c in color),1);tex.inputs['Scale'].default_value=16;nt.links.new(tex.outputs[0],bs.inputs['Base Color'])
  # three rounded rectangular horizontal rings create taper and actual volume.
  verts=[];N=32
  for k,(zz,scale) in enumerate([(0,.94),(h*.12,1),(h*.78,1),(h,.78 if kind in ('tote','satchel') else .93)]):
   ww,dd=w*scale,d*(.82 if k==3 else 1)
   for j in range(N):
    t=2*math.pi*j/N;cx=math.copysign(abs(math.cos(t))**.32,math.cos(t));cy=math.copysign(abs(math.sin(t))**.32,math.sin(t));verts.append((x+ww*.5*cx,y+dd*.5*cy,z+zz))
  faces=[]
  for k in range(3):
   for j in range(N):faces.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
  faces += [tuple(reversed(range(N))),tuple(range(3*N,4*N))]
  body=api.mesh(name+'_body',verts,faces,mat)
  bevel=body.modifiers.new('Editable leather edge softness','BEVEL');bevel.width=.009;bevel.segments=3
  for f in body.data.polygons:f.use_smooth=True
  handlemat=api.mat(name+'_handle',tuple(c*.70 for c in color),.5)
  for k,yy in enumerate([y-d*.34,y+d*.34]):
   pts=[(x+math.cos(t)*w*.22,yy,z+h+math.sin(t)*h*.42) for t in [math.pi-j*math.pi/20 for j in range(21)]]
   api.curve(name+f'_handle{k+1}',pts,.009 if w>.3 else .006,handlemat)
   for j,xx in enumerate([x-w*.22,x+w*.22]):api.box(name+f'_handle_tab{k}{j}',(xx,yy,z+h*.89),(.025,.012,.07),handlemat,.004)
  if kind in ('satchel','mini','backpack'):
   api.box(name+'_front_flap',(x,y+front*(d/2+.006),z+h*.74),(w*.83,.018,h*.32),mat,.02)
   api.box(name+'_metal_clasp',(x,y+front*(d/2+.02),z+h*.66),(.037,.011,.026),gold,.004)
  else:
   api.curve(name+'_top_zip',[(x-w*.36,y,z+h+.007),(x+w*.36,y,z+h+.007)],.002,silver)
  if kind=='backpack':
   for k,xx in enumerate([x-w*.27,x+w*.27]):api.curve(name+f'_back_strap{k}',[(xx,y-front*d*.4,z+h*.8),(xx,y-front*d*.8,z+h*.45),(xx,y-front*d*.45,z+.04)],.012,handlemat)
  api.parent=None
  return grp
 bag('FAS-BAG-N-TAN',-5.74,2.40,.825,.30,.23,.15,(.45,.28,.11),'tote',-1)
 bag('FAS-BAG-N-TAUPE',-4.46,2.40,.825,.31,.22,.15,(.31,.23,.16),'satchel',-1)
 for side,y,front in [('S',-.22,1),('N',2.40,-1)]:
  specS=[(-7.62,.09,.34,.20,.19,(.63,.68,.67),'satchel',False),(-7.71,.421,.36,.23,.18,(.80,.78,.66),'tote',False),(-7.57,.756,.24,.17,.12,(.87,.87,.81),'mini',False),(-7.70,1.091,.31,.24,.14,(.28,.22,.27),'tote',True),(-7.87,1.426,.32,.23,.15,(.52,.29,.13),'tote',False),(-7.30,1.426,.23,.19,.12,(.04,.47,.57),'mini',False),(-7.64,1.761,.34,.23,.18,(.84,.80,.67),'tote',False)]
  specN=[(-7.87,.09,.25,.16,.15,(.63,.32,.40),'mini',False),(-7.40,.421,.35,.24,.17,(.40,.16,.07),'satchel',False),(-7.63,.756,.38,.24,.17,(.78,.73,.58),'tote',True),(-7.60,1.091,.55,.25,.23,(.23,.12,.06),'duffel',True),(-7.95,1.426,.23,.19,.14,(.49,.22,.10),'satchel',False),(-7.48,1.426,.26,.20,.15,(.22,.14,.11),'satchel',True),(-7.70,1.761,.32,.24,.18,(.38,.56,.31),'backpack',False)]
  for j,(x,z,w,h,d,c,kind,pat) in enumerate(specS if side=='S' else specN):bag(f'FAS-GOLD-{side}-BAG-{j+1:02}',x,y,z,w,h,d,c,kind,front,pat)
 # Pale bottle on top north tower is a thermos, not an extra bag.
 api.lathe('FAS-GOLD-N-THERMOS',(-7.25,2.42,1.758),[(.052,0),(.052,.23),(.037,.25),(.037,.29),(.033,.30)],api.mat('Thermos warm ivory',(.75,.71,.56),.36,.22),24)
 # Small printed cards in clear stands; individual local geometry rather than merged shelf scan.
 orange=api.mat('Price-card orange rim',(.66,.25,.10),.62)
 for side,y in [('S',.035),('N',2.145)]:
  for j,z in enumerate([.095,.425,.76,1.095,1.43,1.765]):
   api.box(f'FAS-PRICE-TAG-{side}-{j+1:02}',(-7.3,y,z+.034),(.086,.008,.055),white,.001)
   for xx in [-7.343,-7.257]:api.box(f'FAS-PRICE-TAG-{side}-{j+1:02}_edge{xx}',(xx,y-.005,z+.034),(.003,.003,.055),orange)
 # Rebuilt presentation cases with distinct base, hinged open lid and contents.
 brown=api.mat('Jewelry case caramel lining',(.32,.14,.05),.6)
 api.box('FAS-JEWELRY-CASE_base',(-5.77,2.40,1.24),(.31,.21,.055),black,.006)
 api.box('FAS-JEWELRY-CASE_lining',(-5.77,2.40,1.270),(.285,.19,.008),brown,.003)
 api.box('FAS-JEWELRY-CASE_open_lid',(-5.77,2.508,1.365),(.31,.018,.23),brown,.006)
 for j,xx in enumerate([-5.85,-5.70]):api.curve(f'FAS-JEWELRY-CASE_spectacle{j}',[(xx+.036*math.cos(t),2.39+.025*math.sin(t),1.282) for t in [i*math.pi/16 for i in range(32)]],.003,silver,True)
 api.box('FAS-WATCHBOX_base',(-4.48,2.39,1.24),(.10,.11,.055),black,.004)
 api.box('FAS-WATCHBOX_lid',(-4.48,2.45,1.31),(.10,.011,.105),black,.004)
 api.cyl('FAS-WATCHBOX_watch',(-4.48,2.39,1.27),.024,.012,silver,20)
 api.box('FAS-REDBOARD',(-4.46,2.61,1.355),(.28,.013,.28),api.mat('Fashion red package',(.62,.024,.055),.6),.002)
 api.box('FAS-ARLETTA',(-5.46,2.43,1.355),(.072,.14,.27),api.mat('Fashion Arletta red spine',(.60,.06,.055),.58),.002)
 # Check-patterned small south shelf handbag and visible shoe boxes.
 bag('FAS-CHECKBAG-S',-6.72,-.20,.818,.28,.19,.10,(.16,.12,.08),'mini',1,True)
 api.box('FAS-SHOE-BOX-BLACK',(-4.98,-.22,.10),(.40,.28,.07),black,.005)
 api.box('FAS-SHOE-BOX-GRAY',(-6.78,-.21,.12),(.38,.30,.09),gray,.005)
 api.box('FAS-TRAY-N_base',(-5.71,2.40,.082),(.33,.28,.011),silver,.001)
 for k in range(18):api.rod(f'FAS-TRAY-N_wire{k}',(-5.86+k*.017,2.265,.09),(-5.86+k*.017,2.535,.09),.0012,gray,8)
 for j,(x,z) in enumerate([(-6.57,1.22),(-6.57,.82)]):api.box(f'FAS-PRICE-TAG-RACK-{j+1}',(x,.048,z+.035),(.082,.008,.052),white,.001)
 # Books are simple native solids with independently editable covers/pages; small print remains decorative.
 pages=api.mat('Fashion book page block',(.72,.71,.68),.8)
 bookcolors=[(.75,.72,.65),(.58,.05,.04),(.13,.15,.17),(.8,.79,.74),(.38,.43,.42)]
 def books(prefix,x,y,z,n,w=.38,d=.29,heights=None,lean=False):
  for j in range(n):
   h=(heights[j] if heights else .026+(j%3)*.006);mat=api.mat(f'Fashion book cover {j%5}',bookcolors[j%5],.55)
   if not lean:
    api.box(f'{prefix}-{j+1:02}_pages',(x,y,z+h/2),(w-.013,d-.006,h),pages,.001)
    for zz in [z,z+h]:api.box(f'{prefix}-{j+1:02}_cover_{zz:.3f}',(x,y,zz),(w,d,.002),mat,.001)
    z+=h+.003
   else:
    o=api.box(f'{prefix}-{j+1:02}',(x+j*.034,y,.20),(.028,.27,.27),mat,.002);o.rotation_euler.y=.21
 books('FAS-BOOKS-S-TOP',-5.48,-.19,.817,4)
 books('FAS-BOOKS-S-BASE',-5.62,-.16,.084,5,lean=True)
 books('FAS-BOOKS-N-MID',-5.73,2.40,.817,3)
 books('FAS-BOOKS-N-LOW',-5.71,2.41,.467,3)
 books('FAS-BOOKS-N-ENTRY',-4.46,2.41,.469,7,w=.31,d=.26)
 # The two wheeled display/reflector rigs at west wall, each separate frame, panel and casters.
 for label,yy in [('A',.53),('B',1.27)]:
  api.parent=None;api.group('FAS-REFLECTOR-'+label,(-8.82,yy,0))
  for k,y in enumerate([yy-.28,yy+.28]):
   api.box(f'FAS-REFLECTOR-{label}_upright{k}',(-8.85,y,1.025),(.032,.032,1.85),silver,.002)
   api.box(f'FAS-REFLECTOR-{label}_foot{k}',(-8.80,y,.10),(.54,.038,.05),silver,.002)
   for j,x in enumerate([-9.03,-8.57]):
    api.cyl(f'FAS-REFLECTOR-{label}_wheel{k}{j}',(x,y,.062),.05,.024,rubber,20,rot=(math.pi/2,0,0))
    api.cyl(f'FAS-REFLECTOR-{label}_hub{k}{j}',(x,y-.014,.062),.028,.026,gold,20,rot=(math.pi/2,0,0))
  for z in [.30,.46,1.57]:api.rod(f'FAS-REFLECTOR-{label}_crossbar{z}',(-8.85,yy-.28,z),(-8.85,yy+.28,z),.014,silver)
  if label=='B':api.box('FAS-REFLECTOR-B_metal_panel',(-8.81,yy,.99),(.012,.57,1.02),silver,.012)
  else:
   for k in range(8):api.box(f'FAS-REFLECTOR-A_white_layer{k}',(-8.82,yy,.49+k*.105),(.032,.59,.09),white,.008)
 api.parent=None
 # Keep the measured local folds, replacing captured gray illumination with
 # independently editable translucent film albedo seen in the photographs.
 for name,bounds,rough,transmission in [
  ('FAS-WRAP-A',(-9.04,-8.50,.10,1.68,1.38,1.73),.38,.38),
  ('FAS-WRAP-FLOOR',(-8.98,-8.40,.55,1.46,.008,.058),.27,.65)]:
  obj=cut(name,*bounds);m=api.mat(name+' translucent packing film',(.80,.82,.81),rough)
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=transmission;bs.inputs['IOR'].default_value=1.46;bs.inputs['Coat Weight'].default_value=.20
  nt=m.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=145;noise.inputs['Detail'].default_value=3
  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.21;bump.inputs['Distance'].default_value=.0015;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
  obj.data.materials.clear();obj.data.materials.append(m)
  for p in obj.data.polygons:p.material_index=0;p.use_smooth=True
  obj['material_note']='Native translucent rough plastic; photographed albedo inferred independently of captured scan illumination; measured local fold geometry and UV retained.'
 # Small low folding table with product cartons beside far display.
 api.group('FAS-BOXTABLE',(-8.49,2.02,0))
 api.box('FAS-BOXTABLE_top',(-8.5,2.05,.42),(.58,.45,.016),white,.003)
 for j,y in enumerate([1.87,2.22]):
  api.rod(f'FAS-BOXTABLE_leg{j}a',(-8.71,y,.04),(-8.31,y,.41),.009,silver)
  api.rod(f'FAS-BOXTABLE_leg{j}b',(-8.30,y,.04),(-8.69,y,.41),.009,silver)
 api.parent=None
 # Five cartons individually native; source printed faces kept as small local image surfaces where available.
 for j,(xx,yy,zz,siz) in enumerate([(-8.66,2.14,.58,(.17,.13,.28)),(-8.47,2.12,.55,(.13,.11,.22)),(-8.29,2.10,.50,(.14,.1,.14)),(-8.62,1.90,.46,(.18,.13,.07)),(-8.42,1.9,.46,(.15,.11,.07)),(-8.32,2.14,.64,(.11,.09,.36))]):api.box(f'FAS-PRODUCT-BOX-{j+1:02}',(xx,yy,zz),siz,white,.002)
 # Lantern studio softbox; real three-dimensional fabric envelope and rib lines.
 api.group('FAS-SOFTBOX',(-4.59,.22,0))
 sx,sy=-4.58,.20
 api.rod('FAS-SOFTBOX_stand_lower',(sx,sy,.12),(sx,sy,1.45),.018,black)
 api.rod('FAS-SOFTBOX_stand_upper',(sx,sy,1.35),(sx,sy,1.84),.012,silver)
 for j,ang in enumerate([.2,2.29,4.38]):api.rod(f'FAS-SOFTBOX_tripod_leg{j}',(sx,sy,.37),(sx+.42*math.cos(ang),sy+.42*math.sin(ang),.035),.012,black)
 fabric=api.mat('Studio softbox white translucent textile',(.89,.9,.89),.75)
 obj=api.ball('FAS-SOFTBOX_fabric',(sx-.07,sy+.05,1.79),(.27,.22,.32),fabric)
 for j in range(8):
  a=j*math.pi/4;pts=[]
  for k in range(33):
   t=-math.pi/2+k*math.pi/32;pts.append((sx-.07+.271*math.cos(t)*math.cos(a),sy+.05+.221*math.cos(t)*math.sin(a),1.79+.321*math.sin(t)))
  api.curve(f'FAS-SOFTBOX_rib{j}',pts,.0025,white)
 api.box('FAS-SOFTBOX_flash_body',(sx+.21,sy+.04,1.84),(.23,.13,.13),black,.014)
 api.parent=None
 for j,xx in enumerate([-4.48,-4.35]):api.box(f'FAS-SOFTBOX-POWER-{j+1}',(xx,-.03,.14),(.11,.16,.23),black,.014)
 api.curve('FAS-SOFTBOX-POWER_cable',[(sx+.2,sy,1.82),(sx+.2,sy,1.14),(sx+.22,sy,.21),(sx+.35,sy+.24,.018),(sx-.1,sy+.4,.018),(sx-.25,sy+.1,.018),(sx+.12,sy-.1,.018),(-4.4,-.03,.2)],.0035,black)
 # Cleaning implements east corners.
 api.group('FAS-CLEAN-MOP',(-3.86,2.45,0))
 api.rod('FAS-CLEAN-MOP_shaft',(-3.86,2.45,.12),(-3.95,2.57,1.33),.008,silver)
 api.rod('FAS-CLEAN-MOP_grip',(-3.944,2.562,1.22),(-3.96,2.584,1.43),.011,black)
 api.box('FAS-CLEAN-MOP_head',(-3.86,2.42,.075),(.16,.47,.052),black,.018)
 for y in [2.31,2.51]:api.rod(f'FAS-CLEAN-MOP_brace{y}',(-3.87,2.45,.41),(-3.86,y,.11),.006,black)
 api.parent=None
 api.rod('FAS-CLEAN-BROOM_handle',(-3.79,-.24,.1),(-3.76,-.29,1.23),.008,silver)
 api.box('FAS-CLEAN-BROOM_head',(-3.79,-.23,.1),(.08,.25,.17),gray,.004)
 for j in range(12):api.box(f'FAS-CLEAN-BROOM_bristle{j}',(-3.78,-.34+j*.019,.059),(.05,.004,.08),gray)
 api.rod('FAS-CLEAN-PAN_handle',(-3.85,-.1,.1),(-3.81,-.18,1.11),.009,white)
 api.box('FAS-CLEAN-PAN_tray',(-3.92,-.05,.06),(.24,.25,.02),white,.005)
 # Two ventilation grilles and actual U-shaped track at lower ceiling, all independent.
 for label,x in [('entry',-4.0),('far',-8.02)]:
  y=1.09;z=2.758
  api.box('FAS-VENT-'+label+'_frame',(x,y,z),(.26,1.04,.023),white,.004)
  if label=='entry':
   for k in range(7):api.box(f'FAS-VENT-{label}_blade{k}',(x-.10+k*.033,y,z-.014),(.007,.99,.018),gray)
   for k in range(27):api.box(f'FAS-VENT-{label}_cross{k}',(x,y-.48+k*.037,z-.02),(.22,.006,.014),gray)
  else:
   for k in range(7):api.box(f'FAS-VENT-{label}_blade{k}',(x-.10+k*.033,y,z-.014),(.009,.99,.014),gray)
 for j,y in enumerate([.20,2.0]):api.box(f'FAS-CEILING-TRACK_long{j}',(-6.38,y,2.744),(3.42,.025,.025),silver,.001)
 api.box('FAS-CEILING-TRACK_far',(-8.09,1.1,2.744),(.025,1.82,.025),silver,.001)
 for j,(x,y) in enumerate([(x,y) for y in [.20,2.0] for x in [-4.74,-5.37,-6.0,-6.63,-7.26,-7.89]]+[(-8.09,y) for y in [.60,1.10,1.60]]):
  api.box(f'FAS-SPOT-{j+1:02}_adapter',(x,y,2.718),(.10,.04,.035),white,.004)
  api.rod(f'FAS-SPOT-{j+1:02}_joint',(x,y,2.70),(x,y,2.665),.006,silver)
  toward=Vector((0,-.11 if y<1 else .11,-.18));origin=Vector((x,y,2.64));end=origin+toward
  o=api.cyl(f'FAS-SPOT-{j+1:02}_housing',(origin+end)/2,.038,toward.length,white,24);o.rotation_euler=toward.to_track_quat('Z','Y').to_euler()
  o=api.cyl(f'FAS-SPOT-{j+1:02}_diffuser',end,.032,.005,glow,24);o.rotation_euler=toward.to_track_quat('Z','Y').to_euler()
 api.cyl('FAS-SMOKE',(-7.06,1.10,2.735),.047,.066,white,24)
 api.cyl('FAS-SPRINKLER',(-7.86,1.13,2.752),.014,.037,silver,16)
 api.box('FAS-SWITCH',(-3.605,-.23,1.18),(.022,.07,.085),black,.004)
 # Exposed junction is visible and not suppressed as an imagined finished fitting.
 api.box('FAS-JUNCTION_recess',(-6.03,2.691,1.66),(.075,.011,.078),gray)
 api.curve('FAS-JUNCTION_cable',[(-6.05,2.68,1.66),(-6.05,2.66,1.69),(-6.01,2.65,1.67),(-6.03,2.64,1.63),(-6.06,2.66,1.64)],.003,api.mat('Blue electrical wire',(.06,.2,.45),.4))
 api.parent=None
 return {'area':'Fashion','collections':['Fashion_Fixtures'],'notes':'Native fixtures, small simple items and lights; actual scan surfaces separated into local garments, bags, shoes, cushions, packaging and small presentation objects. No rack/wall scan substitutes.'}
