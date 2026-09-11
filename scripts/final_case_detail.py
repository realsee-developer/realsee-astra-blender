"""Apply source-registered roadcase correction without saving the caller's scene."""
import bpy,math,json
from mathutils import Vector

def apply_case_detail(ROOT,a):
 a.area_collection('Corridor_Contents','data/cube-map/1_l.jpg;2_f.jpg;5_l.jpg;data/point-cloud.ply;research/case-detail-measurements.json;research/visual-previews/case-east-rectified.jpg')
 case=bpy.data.objects['COR.Roadcase'];case.location=(-2.245,-.225,0);case.scale.x=1.4/1.55
 case['evidence_status']='PLY bounds x[-2.945,-1.545],y[-.49,.015],top1.14m; hardware registered from1_l end and5_l long-side photographs'
 for i,(x,y) in enumerate([(-1.370,-.345),(-1.365,-.035)],1):
  bag=bpy.data.objects[f'COR.Backpack.{i}'];bag.location=(x,y,0);bag.rotation_euler.z=-math.pi/2;bag.scale.z=.72;bag['evidence_status']='1_l and PLY: two small bags beside east case end, facing+X; top approximately0.40m'
 bpy.context.view_layer.update()
 # The broad photographed side has catches only. The three lift handles belong
 # on its east end, which the initial rough modeling placed on the wrong face.
 for z in [.52,1.095]:
  for stem in ['HandleRecess','Handle']:bpy.data.objects.remove(bpy.data.objects[f'COR.Roadcase.{stem}.{z}'],do_unlink=True)
 black=a.mat('Roadcase black phenolic',(.014,.018,.02),.62);silver=a.mat('Roadcase aluminum edging',(.46,.5,.55),.25,.8);rubber=a.mat('Roadcase handle black grip',(.009,.010,.012),.72)
 a.parent=case
 for ob in list(bpy.data.objects):
  if ob.name.startswith('COR.Roadcase.CasterFork.'):
   ob.data.materials.clear();ob.data.materials.append(silver)
  elif ob.name.startswith('COR.Roadcase.Caster.'):
   center=ob.matrix_world.translation;a.cyl(ob.name+'.Hub',center,.024,.043,silver,24,(math.pi/2,0,0))
 for i,(y,z) in enumerate([(-.239,.955),(-.365,.459),(-.122,.459)],1):
  name=f'COR.Roadcase.EndHandle.{i}';x=-1.524
  a.box(name+'.Recess',(x-.011,y,z),(.012,.150,.094),rubber,.010)
  for side in [-1,1]:
   a.box(name+f'.FrameSide.{side}',(x,y+side*.073,z),(.009,.017,.101),silver,.006)
   a.box(name+f'.FrameHorizontal.{side}',(x,y,z+side*.046),(.009,.151,.015),silver,.006)
  for yy in [-.048,.048]:a.rod(name+f'.HingeArm.{yy}',(x+.004,y+yy,z+.031),(x+.014,y+yy,z-.022),.008,silver,16)
  a.rod(name+'.Grip',(x+.014,y-.048,z-.018),(x+.014,y+.048,z-.018),.010,rubber,24)
  a.rod(name+'.UpperPivot',(x+.008,y-.053,z+.028),(x+.008,y+.053,z+.028),.005,silver,16)
  for jj,(dy,dz) in enumerate([(-.071,-.035),(-.071,.035),(.071,-.035),(.071,.035),(-.030,.046),(.030,.046),(-.030,-.046),(.030,-.046)]):a.cyl(name+f'.Rivet.{jj}',(x+.006,y+dy,z+dz),.004,.003,silver,12,(0,math.pi/2,0))
 # Wide metal edging on the end, including actual corner plates and fasteners.
 for j,y in enumerate([-.477,.007]):
  a.box(f'COR.Roadcase.EndEdge.Vertical.{j}',(-1.535,y,.65),(.016,.024,1.0),silver,.002)
  for k,z in enumerate([.14,.745,.766,1.13]):
   a.box(f'COR.Roadcase.EndCorner.Vertical.{j}.{k}',(-1.523,y+(.011 if j==0 else-.011),z),(.004,.039,.067),silver,.004)
   for dd in [-.022,.022]:a.cyl(f'COR.Roadcase.EndCorner.Rivet.{j}.{k}.{dd}',(-1.519,y+(.011 if j==0 else-.011),z+dd),.004,.003,silver,12,(0,math.pi/2,0))
 for i,z in enumerate([.14,.745,.766,1.13]):a.box(f'COR.Roadcase.EndEdge.Horizontal.{i}',(-1.535,-.235,z),(.016,.50,.022),silver,.002)
 for y in [-.477,.007]:
  for z in [.14,1.13]:a.ball(f'COR.Roadcase.EndCorner.Cap.{y}.{z}',(-1.529,y,z),(.022,.024,.022),silver)
 red=a.mat('Roadcase red identification tape',(.35,.008,.005),.85)
 a.box('COR.Roadcase.RedTape.End',(-1.513,-.402,1.07),(.0015,.023,.135),red)
 a.box('COR.Roadcase.RedTape.Lid',(-1.55,-.402,1.144),(.075,.023,.0015),red)
 # Small detached black item on the lid. Its identity remains unknown; physical
 # silhouette and measured source-ray location are sufficient to reconstruct it.
 a.parent=None;a.group('COR.CaseLooseItem',(-1.675,-.063,1.147));group=a.parent;group['evidence_status']='observed loose black rounded rectangular case/device; exact function unknown;2_f pixel ray intersects lid plane'
 a.box('COR.CaseLooseItem.Body',(-1.675,-.063,1.156),(.058,.121,.018),black,.007,rot=.37)
 a.box('COR.CaseLooseItem.Top',(-1.675,-.063,1.1655),(.055,.118,.002),rubber,.006,rot=.37)
 a.parent=None
 measurement=json.loads((ROOT/'research/case-detail-measurements.json').read_text())
 for i,key in enumerate(['small_paper_label','large_paper_label'],1):
  row=measurement['lid_items'][key];p=[Vector(v) for v in row['world_corners_m']];u=(p[1]-p[0]+p[2]-p[3])/2;v=(p[3]-p[0]+p[2]-p[1])/2;c=sum(p,Vector())/4
  ob=a.photo_plane(f'COR.Roadcase.LidPaperLabel.{i}',c,u,v,2);ob['evidence_status']='observed separate flat paper label; source-projected print, independent native mesh';ob.parent=case;ob.matrix_parent_inverse=case.matrix_world.inverted()
 # Gray temporary tape on the broad lid panel is visible in5_l.
 a.parent=case;gray=a.mat('Roadcase gray identification tape',(.32,.33,.31),.88)
 a.box('COR.Roadcase.FrontTape.Vertical',(-2.02,.018,.985),(.012,.0015,.24),gray)
 a.box('COR.Roadcase.FrontTape.Foot',(-2.045,.018,.87),(.06,.0015,.012),gray)
 a.parent=None
