"""Source-registered bar switch, room labels and emergency luminaire; no saves."""
from pathlib import Path
import bpy,math

def apply_corridor_small_poses(ROOT,a):
 ROOT=Path(ROOT)
 for suffix,dims in [('Frame',(.017,.286,.207)),('Insert',(.004,.262,.183))]:
  ob=bpy.data.objects['COR.RoomPlaque.1.'+suffix];ob.location=(-3.404 if suffix=='Frame' else -3.393,2.284,1.345);ob.dimensions=dims;ob['pose_evidence']='Source5_f corners129,284..212,344 at600, rays toX−3.390'
 for suffix,dims in [('Frame',(.282,.017,.202)),('Insert',(.258,.004,.178))]:
  ob=bpy.data.objects['COR.RoomPlaque.2.'+suffix];ob.location=(-.542 if suffix=='Frame' else -.553,.919,1.341);ob.dimensions=dims;ob.rotation_euler.z=math.pi/2;ob['pose_evidence']='Source2_l rectangle558,383..648,443 at800; west frontX−.553 on measured entry return'
 housing=bpy.data.objects['COR.EmergencyLamp.Housing'];housing.location=(-3.405,2.390,2.401);housing.dimensions=(.060,.30,.135)
 for i,y in enumerate([2.298,2.463],1):
  stem=bpy.data.objects[f'COR.EmergencyLamp.Stem.{i}'];stem.location=(-3.405,y,2.48);stem.dimensions.z=.11
  head=bpy.data.objects[f'COR.EmergencyLamp.Head.{i}'];head.location=(-3.37,y,2.534)
 a.collection=bpy.data.collections['Corridor_Contents'];a.area='Corridor_Contents';a.source='data/cube-map/2_b.jpg;data/cube-map/5_f.jpg;research/small-fixture-pose-measurements.json';a.parent=None
 for i,y in enumerate([2.298,2.463],1):a.cyl(f'COR.EmergencyLamp.Lens.{i}',(-3.347,y,2.534),.035,.004,a.mat('Emergency reflector lens',(.73,.76,.71),.15,.35),32,(0,math.pi/2,0))
 a.photo_plane('COR.EmergencyLamp.PrintedLabel',(-3.369,2.390,2.401),(0,-.282,0),(0,0,.115),2)
 bpy.context.view_layer.update()
 return ['COR.RoomPlaque.1','COR.RoomPlaque.2','COR.EmergencyLamp']

def apply_bar_switch_pose(ROOT,a):
 ob=bpy.data.objects['BAR-SWITCH'];ob.location=(-.418,.993788,1.317765);ob.dimensions=(.089,.012,.082);ob.rotation_euler.z=math.pi/2;ob['pose_evidence']='Source4_b rectangle772,795..809,855 at1600; return inside/front planeX−.417; center790,824'
 bpy.context.view_layer.update()
 return ['BAR-SWITCH']

def apply_small_fixture_poses(ROOT,a):
 return apply_corridor_small_poses(ROOT,a)+apply_bar_switch_pose(ROOT,a)
