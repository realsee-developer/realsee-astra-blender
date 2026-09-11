"""Native completion of the photographed mint shoulder bag and three shoe pairs.
All bodies, flaps, straps, foot openings, uppers, soles and ornaments are editable.
The incomplete scan cuts are replaced; original reference remains untouched.
"""
from pathlib import Path
import bpy,math,json
from mathutils import Vector,Quaternion

def apply_fashion_accessories(ROOT,a):
 ROOT=Path(ROOT);a.area_collection('Fashion_Fixtures','data/cube-map/3_l.jpg; data/cube-map/3_d.jpg; source-ray constrained native accessory completion')
 ids=['FAS-BAG-CYAN','FAS-SHOES-BLACK','FAS-SHOES-CREAM-S','FAS-SHOES-CREAM-N']
 for o in list(bpy.data.objects):
  if any(o.name==n or o.name.startswith(n+'.') for n in ids):bpy.data.objects.remove(o,do_unlink=True)
 mint=a.mat('Fashion pale mint shoulder bag leather',(.69,.82,.79),.43)
 mint_edge=a.mat('Fashion pale mint edge piping',(.76,.86,.83),.49)
 black=a.mat('Fashion black pump leather',(.008,.010,.011),.26)
 sole=a.mat('Fashion black shoe outsole',(.004,.006,.007),.5)
 cream=a.mat('Fashion cream pump leather',(.75,.70,.57),.38)
 lining=a.mat('Fashion warm beige shoe lining',(.56,.48,.36),.8)
 trim=a.mat('Fashion shoe ornament gunmetal',(.11,.12,.13),.22,.80)
 gold=a.mat('Fashion tiny warm metal fittings',(.48,.32,.11),.25,.82)
 # Small structured shoulder bag, observed upright behind its looped strap.
 bag=a.group('FAS-BAG-CYAN',(-6.18,-.25,.09));bag['coverage_id']='FAS-BAG-CYAN'
 a.box('FAS-BAG-CYAN.Body',(-6.185,-.255,.180),(.210,.098,.178),mint,.026)
 a.box('FAS-BAG-CYAN.FrontFlap',(-6.185,-.200,.216),(.204,.012,.115),mint,.021)
 pts=[]
 for cx,cz,start in [(-6.270,.252,math.pi/2),(-6.270,.115,math.pi),(-6.100,.115,3*math.pi/2),(-6.100,.252,0)]:
  for j in range(9):
   t=start+j*math.pi/16;pts.append((cx+.014*math.cos(t),-.193,cz+.014*math.sin(t)))
 a.curve('FAS-BAG-CYAN.EdgePiping',pts,.0013,mint_edge,True)
 a.box('FAS-BAG-CYAN.FlapClosure',(-6.185,-.190,.176),(.017,.007,.009),gold,.002)
 for i,xx in enumerate([-6.292,-6.078],1):a.curve(f'FAS-BAG-CYAN.StrapRing.{i}',[(xx,-.255+.006*math.cos(k*math.tau/24),.252+.008*math.sin(k*math.tau/24)) for k in range(24)],.0017,gold,True)
 # Smooth shoulder strap follows the photographed loop, rather than an angular cord.
 pose=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'][2];cam=Vector(pose['translation_xyz_m']);cam.z+=1.396564007;q=Quaternion(pose['quaternion_wxyz'])
 def source_point(x,y,z,face='l'):
  f=pose['cube_faces'][face];d=q@(Vector(f['canonical_local_center'])+Vector(f['canonical_local_right'])*(x/800-1)+Vector(f['canonical_local_down'])*(y/800-1));return cam+d*((z-cam.z)/d.z)
 strap_pts=[Vector((-6.291,-.255,.252)),source_point(1155,1387,.11),source_point(1158,1410,.091),source_point(1125,1420,.09),source_point(1080,1395,.10),Vector((-6.078,-.255,.252))]
 d=bpy.data.curves.new('FAS-BAG-CYAN.ShoulderStrap.Curve','CURVE');d.dimensions='3D';d.resolution_u=20;d.bevel_depth=.0045;d.bevel_resolution=3;s=d.splines.new('BEZIER');s.bezier_points.add(len(strap_pts)-1)
 for p,co in zip(s.bezier_points,strap_pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 ob=bpy.data.objects.new('FAS-BAG-CYAN.ShoulderStrap',d);a.collection.objects.link(ob);a.tag(ob,ob.name,mint_edge)
 # Observed pale fluffy bag charm; separate native volumes and fine chain.
 fur=a.mat('Fashion cream fur charm',(.74,.63,.42),1)
 a.ball('FAS-BAG-CYAN.FurCharm.Upper',(-6.020,-.218,.204),(.026,.022,.028),fur)
 a.ball('FAS-BAG-CYAN.FurCharm.Lower',(-6.045,-.199,.166),(.020,.018,.023),fur)
 for i in range(5):a.curve(f'FAS-BAG-CYAN.CharmChain.{i}',[(-6.075+i*.010+.004*math.cos(k*math.tau/20),-.210,.245-i*.008+.005*math.sin(k*math.tau/20)) for k in range(20)],.0009,gold,True)
 a.parent=None
 # Source pointed shoes have a real open foot cavity, a sloped closed toe and a
 # low heel. Native shell/lining/sole geometry replaces flattened scan remnants.
 configs=[('FAS-SHOES-BLACK',black,[((-5.84373,-.26408),(-5.90871,-.46281)),((-5.92965,-.19653),(-6.03152,-.43197))],.230,.018,'round'),('FAS-SHOES-CREAM-S',cream,[((-4.94071,-.24768),(-4.905,-.495)),((-5.01503,-.26508),(-4.985,-.507))],.250,.035,'square'),('FAS-SHOES-CREAM-N',cream,[((-5.33722,2.31091),(-5.31936,2.55815)),((-5.24793,2.31631),(-5.25583,2.55394))],.250,.032,'square')]
 report=[]
 for ident,leather,poses,L,heel_lift,ornament in configs:
  a.parent=None;pair=a.group(ident,(sum(p[0][0] for p in poses)/2,sum(p[0][1] for p in poses)/2,.08));pair['coverage_id']=ident
  for number,(toe_xy,heel_xy) in enumerate(poses,1):
   toe=Vector((*toe_xy,.081));axis=Vector((toe_xy[0]-heel_xy[0],toe_xy[1]-heel_xy[1],0)).normalized();side=Vector((-axis.y,axis.x,0));heel=toe-axis*L;N=64
   def world(x,y,z):return heel+side*x+axis*y+Vector((0,0,z-.081))
   bottom=[];outer=[];opening=[];foot=[]
   for j in range(N):
    t=j*math.tau/N;v=(math.sin(t)+1)/2;y=L*v;x=.040*math.cos(t)*(1-.40*max(0,math.sin(t)))
    bottom.append(world(x,y,.084+heel_lift*(1-v)**2))
    outer.append(world(x*.96,y,.086+heel_lift*(1-v)+.065*(1-v)**.60+.005*v))
    iy=L*.37+L*.305*math.sin(t);ix=.024*math.cos(t);z=.117+heel_lift*(1-iy/L)+.026*(1-iy/L)
    opening.append(world(ix,iy,z));foot.append(world(ix*.96,iy,.091+heel_lift*(1-iy/L)))
   prefix=f'{ident}.Shoe.{number}'
   vs=bottom+outer+opening;fs=[]
   for ring in range(2):
    for j in range(N):k=ring*N+j;kk=ring*N+(j+1)%N;fs.append((k,kk,kk+N,k+N))
   o=a.mesh(prefix+'.Upper',[tuple(p) for p in vs],fs,leather)
   for p in o.data.polygons:p.use_smooth=True
   o['evidence_status']='native pointed pump shell with open foot cavity; outline and pair pose constrained by source3_l/3_d; fine hidden geometry inferred'
   o=a.mesh(prefix+'.Lining',[tuple(p) for p in opening+foot],[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]+[tuple(range(N,2*N))],lining)
   for p in o.data.polygons:p.use_smooth=True
   low=[p-Vector((0,0,.004)) for p in bottom]
   sole_faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N) for j in range(N)]
   a.mesh(prefix+'.Outsole',[tuple(p) for p in low+bottom],[tuple(reversed(f)) for f in sole_faces],sole)
   a.curve(prefix+'.OpeningPiping',[tuple(p) for p in opening],.0012,leather,True)
   h=world(0,L*.08,.081+heel_lift/2);heel_obj=a.box(prefix+'.LowHeel',h,(.044,.045,heel_lift),sole,.004);heel_obj.rotation_euler.z=math.atan2(axis.y,axis.x)-math.pi/2
   ornament_center=world(0,L*.755,.131)
   if ornament=='square':
    points=[ornament_center+side*x+axis*y for x,y in [(-.016,-.013),(.016,-.013),(.016,.013),(-.016,.013)]]
    a.curve(prefix+'.SquareBuckle',[tuple(p) for p in points],.0037,black,True)
   else:
    a.curve(prefix+'.ToeBrooch',[tuple(ornament_center+side*(.013*math.cos(k*math.tau/40))+axis*(.011*math.sin(k*math.tau/40))) for k in range(40)],.0028,trim,True)
    for j in range(10):
     t=j*math.tau/10;a.ball(prefix+f'.BroochStone.{j}',ornament_center+side*(.013*math.cos(t))+axis*(.011*math.sin(t))+Vector((0,0,.002)),(.0018,.0018,.0020),trim)
   report.append({'id':ident,'shoe':number,'toe_m':list(toe),'heel_m':list(heel),'length_m':L})
  if ident=='FAS-SHOES-CREAM-S':
   # These shoes rest on the observed black shoebox, not the rack's lower slab.
   # Scale along camera rays to raise the sole without changing its source outline.
   factor=(cam.z-.136)/(cam.z-.080);pair.location=cam+(pair.location-cam)*factor;pair.scale=(factor,)*3
   pair['support_evidence']='Native shoe box topZ0.135m; camera-ray scaling preserves source3_l silhouette while placing soles on it.'
   for row in report:
    if row['id']==ident:
     row['toe_m']=list(cam+(Vector(row['toe_m'])-cam)*factor);row['heel_m']=list(cam+(Vector(row['heel_m'])-cam)*factor);row['length_m']*=factor
   carton=bpy.data.objects['FAS-SHOE-BOX-BLACK'];carton.location.y=-.245;carton.dimensions.y=.36
  a.parent=None
 bpy.context.view_layer.update()
 return {'module':'final_fashion_accessories','inventory_rows':ids,'bag_components':'native rounded body/flap/piping/closure, two strap rings, smooth strap and fluffy charm','shoes':report,'method':'Fully native editable accessory silhouettes with separate foot cavities/linings/soles; incomplete source fragments removed; original scan reference preserved.'}

def correct_existing_outsole_winding(ROOT):
 """Reverse only inward closed outsole faces; preserve all vertices/materials."""
 import bmesh
 result=[]
 for ident in ['FAS-SHOES-BLACK','FAS-SHOES-CREAM-S','FAS-SHOES-CREAM-N']:
  for number in [1,2]:
   name=f'{ident}.Shoe.{number}.Outsole';o=bpy.data.objects[name]
   bm=bmesh.new();bm.from_mesh(o.data)
   assert all(e.is_manifold for e in bm.edges),name
   before=bm.calc_volume(signed=True)
   if before<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   after=bm.calc_volume(signed=True);assert after>0,name
   bm.to_mesh(o.data);bm.free();o.data.update()
   result.append({'object':name,'signed_volume_before':before,'signed_volume_after':after})
 return result
