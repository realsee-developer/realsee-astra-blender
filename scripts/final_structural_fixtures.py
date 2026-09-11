"""Source-comparison corrections to bar fixtures, grid section and exposed finishes.
Call after all area builders; changes native geometry only and never saves the file.
"""
from pathlib import Path
import json,math
import bpy
from mathutils import Vector,Matrix,Quaternion

def apply_structural_fixtures(ROOT,a):
 ROOT=Path(ROOT);poses=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'];pose=poses[3];q=Quaternion(pose['quaternion_wxyz']);origin=Vector(pose['translation_xyz_m']);origin.z+=a.offset
 def project(face,pixel,z):
  basis=pose['cube_faces'][face];direction=q@(Vector(basis['canonical_local_center'])+Vector(basis['canonical_local_right'])*(pixel[0]/800-1)+Vector(basis['canonical_local_down'])*(pixel[1]/800-1));return origin+direction*(z-origin.z)/direction.z
 def world_position(ob,position):
  matrix=ob.matrix_world.copy();matrix.translation=position;ob.matrix_world=matrix
 gray=bpy.data.materials['ARCH charcoal corridor paint'];black=bpy.data.materials['ARCH matte black metal'];changed=[]
 for name,axis,sign in [('LINTEL_game',0,1),('LINTEL_photo',0,1),('LINTEL_living',1,-1)]:
  ob=bpy.data.objects[name]
  if gray.name not in [m.name for m in ob.data.materials]:ob.data.materials.append(gray)
  index=list(ob.data.materials).index(gray)
  for polygon in ob.data.polygons:
   if polygon.normal[axis]*sign>.5:polygon.material_index=index
  ob['source']+='; source5_f/7_l corridor-facing gray finish';changed.append(name)
 for ob in bpy.data.objects:
  if not ob.name.startswith('GRID_'):continue
  axis=0 if ob.dimensions.x<ob.dimensions.y else 1;size=ob.dimensions.copy();size[axis]=.0035;ob.dimensions=size;ob['source']='source1_u,2_u,4_u visible thin open-grid edges;130 mm pitch retained';ob['grid_slat_width_m']=.0035;ob['evidence_status']='observed grid; slat section estimated from registered source appearance';changed.append(ob.name)
 neutral=a.mat('BAR neutral white ceiling diffuser',(.86,.93,1),.3,emission=3)
 round_center=project('u',(1175,1068),2.752);group=bpy.data.objects['BAR-LIGHT-ROUND'];group.location.x=round_center.x;group.location.y=round_center.y;bpy.context.view_layer.update()
 rim=bpy.data.objects['BAR-LIGHT-ROUND-Rim'];rim.dimensions=(.430,.430,.027)
 diffuser=bpy.data.objects['BAR-LIGHT-ROUND-Diffuser'];diffuser.dimensions=(.386,.386,.009);diffuser.data.materials[0]=neutral
 group['source']='source4_u center pixel1175,1068 at1600 square; ray atZ2.752';group['evidence_status']='measured center; diameter0.430 m from projected rim extent';changed.append(group.name)
 square_measurements=[('u',(988,482)),('u',(548,1060)),('r',(431,396)),('f',(1488,322))];squares=[]
 for i,(face,pixel) in enumerate(square_measurements,1):
  point=project(face,pixel,2.771);squares.append({'number':i,'source':f'data/cube-map/4_{face}.jpg','pixel_at1600':list(pixel),'scene_center_m':list(point)})
  for part,z in [('Housing',2.79),('Emitter',2.771)]:
   ob=bpy.data.objects[f'BAR-LIGHT-SQUARE-{i}-{part}'];world_position(ob,Vector((point.x,point.y,z)));ob['source']=f'source4_{face} pixel{pixel} at1600 square; ray atZ2.771';ob['evidence_status']='measured center';changed.append(ob.name)
   if part=='Emitter' and i in [1,4]:ob.data.materials[0]=neutral
 # Bright PLY fixture band:244 selected points, medianZ2.711874; body follows its measured1.16 m span.
 group=bpy.data.objects['BAR-LIGHT-LINE'];group.location=(2.56,1.90,2.738);bpy.context.view_layer.update()
 for part,center,size in [('Housing',(2.56,1.90,2.738),(.04,1.16,.030)),('Diffuser',(2.56,1.90,2.718),(.032,1.14,.014))]:
  ob=bpy.data.objects['BAR-LIGHT-LINE-'+part];world_position(ob,Vector(center));ob.dimensions=size;ob['source']='PLY bright linear fixture band + source4_f/4_r; research/cad-bar-linear-light-ply.npz';ob['evidence_status']='measured center and elevation; section inferred';changed.append(ob.name)
 for i,y in enumerate([1.39,2.41]):
  ob=bpy.data.objects[f'BAR-LIGHT-LINE-Suspension-{i}'];world_position(ob,Vector((2.56,y,2.7715)));ob.dimensions=(.004,.004,.037);changed.append(ob.name)
 a.area_collection('Bar_Entry_Structure','data/cube-map/4_u.jpg;4_b.jpg; registered entry beam and frame')
 beam=a.box('BEAM_Bar_entrance',(-.65,1.90,2.78),(.12,2.36,.11),black,.004);beam['area']='Bar';beam['category']='Ceilings';beam['evidence_status']='observed beam; registered approximate extent and section';changed.append(beam.name)
 # Enclose the service void above the annotated room finish, preventing white world gaps.
 # These hidden perimeter completions follow the measured floor outline, not a new room.
 areas=json.loads((ROOT/'research/cad-areas.json').read_text())
 for area,bottom,top in [('Bar',2.780,3.081),('Corridor',3.020,3.102)]:
  poly=next(item for item in areas if item['name']==area)['polygon_scene_m']
  for i,(p1,p2) in enumerate(zip(poly,poly[1:]+poly[:1])):
   dx,dy=p2[0]-p1[0],p2[1]-p1[1];length=math.hypot(dx,dy);center=((p1[0]+p2[0])/2+dy/length*.015,(p1[1]+p2[1])/2-dx/length*.015,(bottom+top)/2)
   ob=a.box(f'PLENUM_{area}_perimeter_{i}',center,(length,.030,top-bottom),black,rot=math.atan2(dy,dx));ob['area']=area;ob['category']='Ceilings';ob['source']='source upward views + measured upper plane; opaque service-void side completion inferred';ob['evidence_status']='inferred hidden plenum closure';changed.append(ob.name)
 # Three source7_f black hinge assemblies remain children of the editable living leaf.
 a.area_collection('Living_Door_Hardware','data/cube-map/7_f.jpg; three visible black hinge plates')
 leaf=bpy.data.objects['DOOR_LivingDining_hinged_leaf']
 for i,z in enumerate([.25,1.08,1.91],1):
  for sign in [-1,1]:
   ob=a.box(f'HINGE_Living_plate_{i}_{sign}',(0,0,0),(.047,.010,.090),black,.002);ob.parent=leaf;ob.matrix_parent_inverse=Matrix.Identity(4);ob.location=(-.021,sign*.026,z);ob['area']='LivingDining';ob['category']='Openings';ob['evidence_status']='observed hinge count; hardware section and hidden side inferred';changed.append(ob.name)
  ob=a.cyl(f'HINGE_Living_knuckle_{i}',(0,0,0),.009,.095,black,24);ob.parent=leaf;ob.matrix_parent_inverse=Matrix.Identity(4);ob.location=(.003,0,z);ob['area']='LivingDining';ob['category']='Openings';changed.append(ob.name)
 evidence={'opened_scene':str(Path(bpy.data.filepath).relative_to(ROOT)) if bpy.data.filepath else 'unsaved build','changes':changed,'bar_round_center_scene_m':list(round_center),'bar_round_outer_diameter_m':.430,'bar_squares':squares,'linear_fixture':{'source':'data/point-cloud.ply','selection':'rawXY1.9<X<2.8,1<Y<2.8; scene2.35<Z<2.8;R>160,G>140','selected_count':244,'median_scene_xyz_m':[2.5648845434,1.9617462158,2.7118738890],'scene_z_10th_90th_m':[2.7068618774,2.7333691597],'native_diffuser_bottom_z_m':2.711,'native_housing_center_m':[2.56,1.90,2.738],'native_length_m':1.16},'grid_section':'3.5 mm width, existing55 mm height and130 mm pitch; estimated from source upward-view edge ratio','beam':'Observed entry beam, approximate native section120×110 mm and span2.36 m; hidden connection inferred','plenum_perimeters':'Opaque native strips close the unobserved service void above room finish level; follow existing CAD area outlines and measured upper planes. This prevents impossible white world leaks between grid and upper backing.','gray_lintels':'Only corridor-facing polygons changed; room-side finish and structural geometry retained','living_hinges':'Three source7_f black hinge assemblies with inferred concealed leaf plates'}
 (ROOT/'research/cad-final-fixture-corrections.json').write_text(json.dumps(evidence,indent=2));bpy.context.view_layer.update();return evidence
