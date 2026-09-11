"""Correct the source-measured fan head pose and hanging power cord; never save."""
from pathlib import Path
import bpy,json,math
from mathutils import Matrix,Vector

def apply_fan_pose(ROOT,a):
 ROOT=Path(ROOT);measure=json.loads((ROOT/'research/fan-pose-measurements.json').read_text())
 old=Vector(measure['old_guard_center_m']);new=Vector(measure['fit_center_m']);rx,rz=measure['fit_rotation_xz_radians'];scale=measure['fit_radius_m']/measure['old_guard_radius_m']
 transform=Matrix.Translation(new)@Matrix.Rotation(rz,4,'Z')@Matrix.Rotation(rx,4,'X')@Matrix.Diagonal((scale,scale,scale,1))@Matrix.Translation(-old)
 bpy.context.view_layer.update()
 head=[o for o in bpy.data.objects if o.name.startswith('BAR-FAN-') and o.name not in ['BAR-FAN-Foot','BAR-FAN-Mast']]
 for ob in head:
  ob.matrix_world=transform@ob.matrix_world
  ob['pose_evidence']='research/fan-pose-measurements.json; registered4_b outline and source PLY depth'
 # Independent telescoping mast remains a cylinder, shortened beneath the measured motor/guard.
 mast=bpy.data.objects['BAR-FAN-Mast'];m=mast.matrix_world.copy();m.translation.z=.39;m.translation.x=new.x; mast.matrix_world=m; mast.dimensions.z=.72
 # The source has a separate flexible cable hanging behind the fan head and mast.
 a.collection=bpy.data.collections['BAR'];a.parent=bpy.data.objects['BAR-FAN'];a.area='BAR';a.source='data/cube-map/4_b.jpg; research/fan-pose-measurements.json'
 black=bpy.data.objects['BAR-FAN-Mast'].active_material
 # Dense photographed wire cage: retain the existing24 radial wires and insert72 thin wires.
 for ob in head:
  if ob.name.startswith('BAR-FAN-GuardSpoke-'):ob.scale.x*=.48;ob.scale.y*=.48
  if ob.name.startswith('BAR-FAN-GuardRing-') and not ob.name.endswith('0.216'):ob.data.bevel_depth=.0014
 for k in range(96):
  if k%4==0:continue
  th=k*math.tau/96;p1=transform@Vector((old.x+.025*math.cos(th),1.12,old.z+.025*math.sin(th)));p2=transform@Vector((old.x+.215*math.cos(th),1.085,old.z+.215*math.sin(th)))
  a.rod(f'BAR-FAN-GuardWire-{k:02}',p1,p2,.0011,black,6)
 a.curve('BAR-FAN-PowerCord',[(new.x-.035,1.015,.885),(new.x-.09,.94,.65),(new.x-.10,.965,.50),(new.x-.065,1.015,.475),(new.x+.04,1.02,.48),(new.x+.06,.98,.12),(new.x+.06,.95,.025)],.004,black)
 a.parent=None
 bpy.context.view_layer.update()
 return {'head_parts_corrected':len(head),'new_guard_center_m':list(new),'old_guard_center_m':list(old),'guard_radius_m':measure['fit_radius_m'],'head_drop_m':old.z-new.z,'hanging_power_cord':'BAR-FAN-PowerCord'}
