"""Source-verified final helmet placement and independently editable retention parts."""
import bpy,math
from mathutils import Vector

def add_helmet_detail(ROOT,a):
 a.area_collection('Corridor_Contents','data/cube-map/2_f.jpg;data/point-cloud.ply;research/visual-previews/corridor-lid-detail.jpg;research/visual-previews/hardhat-points.png')
 helmet=bpy.data.objects['COR.Hardhat'];helmet.location=(-1.92,-.255,1.161);helmet.scale.z=.90
 helmet['evidence_status']='PLY blue-shell extent x approximately[-2.03,-1.80],y[-.38,-.15],top approximately1.30m; headband and strap visible in2_f'
 bpy.context.view_layer.update();a.parent=helmet
 dark=a.mat('Helmet black retention polymer',(.009,.011,.012),.62)
 strap=a.mat('Helmet gray woven chinstrap',(.48,.49,.45),.97)
 # A real ring with thickness and an open center fits underneath the blue shell.
 n=64;verts=[]
 for z,outer in [(1.143,True),(1.162,True),(1.162,False),(1.143,False)]:
  for k in range(n):
   t=k*math.tau/n;rx,ry=(.114,.084) if outer else(.107,.077);verts.append((-1.92+rx*math.cos(t),-.255+ry*math.sin(t),z))
 faces=[]
 for j in range(4):
  for k in range(n):faces.append((j*n+k,j*n+(k+1)%n,((j+1)%4)*n+(k+1)%n,((j+1)%4)*n+k))
 a.mesh('COR.Hardhat.InnerHeadband',verts,faces,dark)
 # Replace the original coarse rib polylines with conforming curved ridges.
 blue=bpy.data.objects['COR.Hardhat.Shell'].data.materials[0]
 for dx in [-.042,.042]:
  old=bpy.data.objects[f'COR.Hardhat.Rib.{dx}'];bpy.data.objects.remove(old,do_unlink=True)
  pts=[]
  for j in range(49):
   dy=-.089+j/48*.178;z=1.1619+.135*math.sqrt(1-(dx/.134)**2-(dy/.104)**2)+.001
   pts.append((-1.92+dx,-.255+dy,z))
  a.curve(f'COR.Hardhat.Rib.{dx}',pts,.0028,blue)
 points=[(-1.824,-.230,1.168),(-1.780,-.224,1.193),(-1.729,-.194,1.191),(-1.704,-.137,1.159),(-1.746,-.078,1.150),(-1.830,-.079,1.151),(-1.870,-.130,1.155),(-1.862,-.216,1.167)]
 points=[Vector(p) for p in points];verts=[]
 for i,p in enumerate(points):
  tangent=points[min(i+1,len(points)-1)]-points[max(0,i-1)];side=Vector((-tangent.y,tangent.x,0)).normalized()*.010
  verts.extend([tuple(p-side),tuple(p+side)])
 faces=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(points)-1)]
 ob=a.mesh('COR.Hardhat.Chinstrap',verts,faces,strap);smooth=ob.modifiers.new('Smooth fabric drape','SUBSURF');smooth.levels=2;smooth.render_levels=2;mod=ob.modifiers.new('Woven strap thickness','SOLIDIFY');mod.thickness=.0016
 bevel=ob.modifiers.new('Soft fabric edges','BEVEL');bevel.width=.001;bevel.segments=2
 # Strap slider has a real central opening and a separate crossbar.
 x,y,z=-1.808,-.224,1.173
 for side in [-1,1]:
  a.box(f'COR.Hardhat.StrapBuckle.Long.{side}',(x,y+side*.012,z),(.035,.005,.006),dark,.002)
  a.box(f'COR.Hardhat.StrapBuckle.Short.{side}',(x+side*.015,y,z),(.005,.023,.006),dark,.002)
 a.box('COR.Hardhat.StrapBuckle.Crossbar',(x,y,z),(.005,.023,.006),dark,.001)
 a.cyl('COR.Hardhat.AdjustmentWheel',(-1.807,-.255,1.154),.018,.013,dark,24,(0,math.pi/2,0))
 a.parent=None
