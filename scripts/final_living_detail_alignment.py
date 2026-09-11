"""Correct source8_r cabinet contents, visible inserts and wall-shelf greenery."""
import bpy,math,json
from mathutils import Vector,Quaternion,Matrix

def apply_living_detail_alignment(ROOT,a):
 a.area_collection('LivingDining_Details','data/cube-map/8_r.jpg; source-measured shelf footprint and visible cabinet details')
 wood=bpy.data.materials['Living honey oak'];stem=bpy.data.materials['Living plant stems']
 green=a.mat('Small wall-shelf leaves',(.045,.145,.012),.65)
 white=bpy.data.materials['Appliance white']
 station=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'][7]
 origin=Vector(station['translation_xyz_m']);origin.z+=a.offset;q=Quaternion(station['quaternion_wxyz']);basis=station['cube_faces']['r']
 def ray(pixel,y):
  d=q@(Vector(basis['canonical_local_center'])+(pixel[0]/800-1)*Vector(basis['canonical_local_right'])+(pixel[1]/800-1)*Vector(basis['canonical_local_down']))
  return origin+d*(y-origin.y)/d.y
 ledge=bpy.data.objects['LIV.CatWallShelf.Ledge'];ledge.location=ray((692,730),9.08);ledge.dimensions=(.266,.10,.021)
 ledge['evidence_status']='source8_r1600px shelf center(692,730) projected to front wall-shelf planeY9.08; depth inferred'
 vase=bpy.data.objects['LIV.CatWallShelf.Vase'];base=ray((667,723),9.06);vase.location=base-Vector((-3.02,9.06,1.696))
 vase['evidence_status']='source8_r1600px vase base(667,723), on measured wall-shelf ledge'
 for o in list(bpy.data.objects):
  if o.name.startswith(('LIV.CatWallShelf.Branch.','LIV.CatWallShelf.Leaf.')):bpy.data.objects.remove(o,do_unlink=True)
 root=base+Vector((0,0,.12));tips=[ray(p,9.05) for p in [(563,518),(559,606),(681,554),(722,600)]]
 for i,tip in enumerate(tips):
  start=root+Vector((0,.002,.018*i));mid=start.lerp(tip,.50)+Vector((.017*(-1 if i%2 else 1),-.012,.012))
  a.curve(f'LIV.CatWallShelf.Branch.{i}',[start,mid,tip],.0018,stem)
  count=6 if i==0 else 4
  for j in range(count):
   t=.30+.65*j/max(1,count-1);center=start.lerp(tip,t);direction=(tip-start).normalized();side=Vector((direction.z,0,-direction.x)).normalized()
   for sign in [-1,0,1]:
    leaf_direction=(side*sign*.75+direction*.66+Vector((0,-.25,0))).normalized();length=.042 if j<count-1 else .030
    leaf_start=center;leaf_tip=center+leaf_direction*length;cross=leaf_direction.cross(Vector((0,1,0))).normalized();vs=[]
    for n in range(7):
     tt=n/6;spine=leaf_start.lerp(leaf_tip,tt)+Vector((0,-.003*math.sin(math.pi*tt),0));width=.011*max(.025,math.sin(math.pi*tt)**.8)
     for k in [-1,0,1]:vs.append(tuple(spine+cross*width*k+Vector((0,.0015*abs(k)*math.sin(math.pi*tt),0))))
    faces=[]
    for n in range(6):
     for k in range(2):v=n*3+k;faces.append((v,v+1,v+4,v+3))
    ob=a.mesh(f'LIV.CatWallShelf.Leaf.{i}.{j}.{sign}',vs,faces,green);mod=ob.modifiers.new('Editable leaf thickness','SOLIDIFY');mod.thickness=.0006
    ob['evidence_status']='observed branching greenery, source silhouette constrained; individual occluded leaf shapes inferred'
 # The old packages sat below the upper shelf surface and were obscured by it.
 # Preserve the two identified contents as separate editable folded packages.
 for n,bounds in [(1,[[-2.255,8.770,.935],[-2.015,9.065,1.100]]),(2,[[-2.014,8.770,.935],[-1.735,9.065,1.100]])]:
  bpy.data.objects.remove(bpy.data.objects[f'LIV.CabinetCubbyContent.{n}'],do_unlink=True)
  o=a.scan_part(f'LIV.CabinetCubbyContent.{n}',bounds)
  o['source']+='; original high-resolution mesh and UV preserve visible folded yellow/blue packages'
  o['evidence_status']='measured segmented folded package surfaces from original mesh, verified against source8_r; occluded undersides unknown'
 # Tall cabinet's visible drawer has a horizontal ribbed dark insert.
 dark=a.mat('Cabinet smoked ribbed insert',(.032,.037,.035),.30,.06)
 dark.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=.35
 dark.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.48
 dark['evidence_status']='observed dark ribbed insert; optical transmission and roughness inferred from appearance'
 a.group('LIV.Cabinet.1.Drawer',(-2.0,8.91,.73));a.parent.parent=bpy.data.objects['LIV.Cabinet.1'];a.parent.matrix_parent_inverse=a.parent.parent.matrix_world.inverted()
 for x in [-2.245,-1.755]:a.box(f'LIV.Cabinet.1.Drawer.Stile.{x}',(x,8.745,.739),(.035,.045,.275),wood,.003)
 for z in [.610,.868]:a.box(f'LIV.Cabinet.1.Drawer.Rail.{z}',(-2,8.745,z),(.525,.045,.036),wood,.003)
 a.box('LIV.Cabinet.1.Drawer.Insert',(-2,8.736,.739),(.455,.012,.226),dark,.001)
 for i in range(25):
  z=.630+i*.0088;a.rod(f'LIV.Cabinet.1.Drawer.Rib.{i}',(-2.223,8.725,z),(-1.777,8.725,z),.0018,dark,8)
 a.box('LIV.Cabinet.1.Drawer.Bottom',(-2,8.94,.608),(.49,.34,.016),wood,.002)
 a.parent=None
 # Middle door is a vertical ribbed translucent insert, distinct from the cane door.
 door=bpy.data.objects['LIV.Cabinet.2.Door']
 for o in list(bpy.data.objects):
  if o.name.startswith(('LIV.Cabinet.2.RattanV.','LIV.Cabinet.2.RattanH.')):bpy.data.objects.remove(o,do_unlink=True)
 a.parent=bpy.data.objects['LIV.Cabinet.2']
 cutter=a.box('LIV.Cabinet.2.InsertOpeningTool',(-1.41,8.755,.55),(.395,.15,.51),wood);cutter.hide_render=True;cutter.hide_set(True);cutter['geometry_class']='non-rendering editable Boolean tool'
 mod=door.modifiers.new('Real opening around ribbed insert','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
 a.box('LIV.Cabinet.2.RibbedInsert',(-1.41,8.750,.55),(.396,.007,.512),dark,.001)
 for i in range(45):
  x=-1.604+i*.0088;a.rod(f'LIV.Cabinet.2.GlassRib.{i}',(x,8.742,.299),(x,8.742,.801),.0022,dark,8)
 a.parent=None
 # Real open cane infill and useful local hinge origins for both cabinet leaves.
 # Concealed hinge sides are inferred, and stored as such instead of measured facts.
 cane_door=bpy.data.objects['LIV.Cabinet.3.Door'];a.parent=bpy.data.objects['LIV.Cabinet.3']
 cut=a.box('LIV.Cabinet.3.InsertOpeningTool',(-.82,8.755,.55),(.430,.15,.51),wood);cut.hide_render=True;cut.hide_set(True);cut['geometry_class']='non-rendering editable Boolean tool'
 mod=cane_door.modifiers.new('Real opening behind woven cane','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;a.parent=None
 bpy.context.view_layer.update()
 for n,x in [(2,-1.660),(3,-.570)]:
  leaf=bpy.data.objects[f'LIV.Cabinet.{n}.Door'];old=leaf.matrix_world.copy();pivot=Vector((x,8.755,.55));delta=old.inverted()@pivot
  for v in leaf.data.vertices:v.co-=delta
  old.translation=pivot;leaf.matrix_world=old;leaf['hinge_evidence']='concealed hinge side inferred; native local Z origin at outer stile for independent opening'
  bpy.context.view_layer.update()
  for ob in bpy.data.objects:
   if ob.name.startswith(tuple(f'LIV.Cabinet.{n}.{s}' for s in ['RattanV.','RattanH.','RibbedInsert','GlassRib.','InsertOpeningTool'])):
    world=ob.matrix_world.copy();ob.parent=leaf;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_world=world
 bpy.context.view_layer.update()
 report={'source':'data/cube-map/8_r.jpg','shelf_center_source_pixel1600':[692,730],'ledge_center_scene_m':list(ledge.location),'vase_base_source_pixel1600':[667,723],'vase_base_scene_m':list(base),'branch_tip_scene_m':[list(p) for p in tips],'cubby_packages':'two independently segmented native meshes preserve original visible folds and UV; source bounds stored in their custom properties','upper_shelf_top_z_m':.9275,'cabinet_details':'separate tall drawer with horizontal ribbed insert; middle door vertical ribbed insert; cane retained on right cabinet only','limits':'Cabinet sections, hidden drawer interior and individual botanical leaves inferred from visible appearance; source counts and locations preserved.'}
 (ROOT/'research/living-detail-alignment.json').write_text(json.dumps(report,indent=2));bpy.context.view_layer.update();return report
