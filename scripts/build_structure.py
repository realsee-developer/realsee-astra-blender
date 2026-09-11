"""Native architectural reconstruction from CAD entities registered against PLY.
Integration: build_structure(Path(PROJECT_ROOT)); does not save or clear a scene.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix

def build_structure(ROOT):
 ROOT=Path(ROOT); reg=json.loads((ROOT/'research/registration-cad.json').read_text()); ent=json.loads((ROOT/'research/cad-entities.json').read_text()); areas=json.loads((ROOT/'research/cad-areas.json').read_text())
 angle=reg['cad_to_ply_xy_rotation_radians'];tx,ty=reg['cad_to_ply_xy_translation_m'];cs,sn=math.cos(angle),math.sin(angle)
 def xy(x,y):return (cs*x/1000-sn*y/1000+tx,sn*x/1000+cs*y/1000+ty)
 def cad(x,y):return ((cs*(x-tx)+sn*(y-ty))*1000,(-sn*(x-tx)+cs*(y-ty))*1000)
 main=bpy.data.collections.new('Native / Architecture');bpy.context.scene.collection.children.link(main)
 collections={}
 def coll(area,cat):
  key=area+'/'+cat
  if key not in collections:
   c=bpy.data.collections.new(key);main.children.link(c);collections[key]=c
  return collections[key]
 def mat(name,color,rough=.6,metal=0,emission=0):
  m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
  if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
  return m
 white=mat('ARCH warm white plaster',(.72,.69,.61));gray=mat('ARCH charcoal corridor paint',(.12,.14,.15));purple=mat('ARCH deep indigo wall',(.036,.025,.13));black=mat('ARCH matte black metal',(.012,.013,.014),.4,.6);silver=mat('ARCH aluminum',(.36,.39,.42),.24,.8);wood=mat('ARCH oak doors',(.37,.17,.067),.45);light=mat('ARCH warm LED diffuser',(1,.72,.38),.25,emission=5);neutral_light=mat('ARCH neutral LED diffuser',(.85,.91,1),.25,emission=5);floor_gray=mat('ARCH gray stone',(.18,.18,.17),.38);floor_white=mat('ARCH fashion pale stone',(.6,.58,.49),.45);floor_wood=mat('ARCH warm parquet',(.35,.13,.041),.4);mirror=mat('ARCH mirror silver',(.91,.93,.96),.045,1)
 # Native procedural grain/stone color and fine surface response.
 for m,iswood in [(wood,True),(floor_wood,True),(floor_gray,False),(floor_white,False)]:
  nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF');tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5 if iswood else 1.7;tex.inputs['Detail'].default_value=3
  coord=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(2,130,3) if iswood else (5,5,5);links.new(coord.outputs['Object'],mapping.inputs[0]);links.new(mapping.outputs[0],tex.inputs['Vector']);bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.008 if iswood else .015;links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],p.inputs['Normal'])
  ramp=nodes.new('ShaderNodeValToRGB');base=m.diffuse_color[:3];ramp.color_ramp.elements[0].color=(*[v*.65 for v in base],1);ramp.color_ramp.elements[1].color=(*[min(v*1.25,1) for v in base],1);links.new(tex.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],p.inputs['Base Color'])
 created=[]
 def register(o,area,cat,source,status='measured'):
  for c in list(o.users_collection):c.objects.unlink(o)
  coll(area,cat).objects.link(o);o['stable_id']=o.name;o['area']=area;o['category']=cat;o['source']=source;o['evidence_status']=status;created.append(o);return o
 def mesh_poly(name,points,z0,z1,area,cat,material,source,status='measured'):
  # Consistent CCW top winding; concave native n-gons remain editable.
  points=list(points);ar=sum(points[i][0]*points[(i+1)%len(points)][1]-points[(i+1)%len(points)][0]*points[i][1] for i in range(len(points)))
  if ar<0:points.reverse()
  n=len(points);verts=[(*p,z) for z in (z0,z1) for p in points];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  me=bpy.data.meshes.new(name+' / editable mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update();o=bpy.data.objects.new(name,me);coll(area,cat).objects.link(o);register(o,area,cat,source,status);return o
 def box(name,center,dims,area,cat,material,source,status='measured',rot=0):
  bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler.z=rot;o.data.materials.append(material);register(o,area,cat,source,status);return o
 def cbox(name,center,dims,area,cat,material,source,status='measured'):
  return box(name,(*xy(center[0],center[1]),center[2]),dims,area,cat,material,source,status,angle)
 def bevel(o,w=.008):
  mod=o.modifiers.new('Editable edge radius','BEVEL');mod.width=w;mod.segments=3
 def wall(name,a,b,thick,h,area,material,source,z0=0,side=1):
  # a,b in CAD mm; right-hand exterior offset used for perimeter.
  av,bv=Vector(a),Vector(b);v=(bv-av).normalized();off=Vector((v.y,-v.x))*thick*1000*side
  pts=[xy(*p) for p in [av,bv,bv+off,av+off]];o=mesh_poly(name,pts,z0,h,area,'Walls',material,source);o['length_m']=(bv-av).length/1000;o['thickness_m']=thick;o['top_elevation_m']=h;return o
 lines={l['handle']:l for l in ent['lines']}
 # Floor surfaces represent annotated FFL0, with observed per-area residuals documented.
 heights={'Photography':2.774,'Game':2.786,'LivingDining':2.792,'Bar':2.812,'Corridor':3.021}
 mats={'Photography':white,'Game':purple,'LivingDining':white,'Bar':gray,'Corridor':gray}
 floor_mats={'Photography':floor_white,'Game':floor_gray,'LivingDining':floor_wood,'Bar':floor_wood,'Corridor':floor_gray}
 # PLY and panorama8 show a broad glazed bay omitted by the narrow CAD trace.
 # Preserve CAD area as a reference and build the observed bay, with inferred side connections.
 living=next(a for a in areas if a['name']=='LivingDining');living['cad_polygon_area_m2']=living['area_m2']
 oldliving=living['polygon_scene_m'];niche_north=(-7.5504,8.02);niche_south=(-7.5563,6.86)
 niche_poly=[niche_south,niche_north,(-9.02,8.20),(-9.02,6.91)]
 living['polygon_scene_m']=oldliving[:4]+[niche_north,(-9.02,8.20),(-9.02,6.91),niche_south]
 pp=living['polygon_scene_m'];living['area_m2']=abs(sum(pp[i][0]*pp[(i+1)%len(pp)][1]-pp[(i+1)%len(pp)][0]*pp[i][1] for i in range(len(pp))))/2
 floor_objects={}
 for ar in areas:
  name=ar['name'];floor_objects[name]=mesh_poly('FLOOR_'+name,ar['polygon_scene_m'],-.085,0,name,'Floors',floor_mats[name],'cad.dxf interior wall coordinates + FFL±0 annotations');floor_objects[name]['net_polygon_area_m2']=ar['area_m2']
 floor_objects['LivingDining']['source']='CAD main room plus PLY-supported broader bay, source8_f; research/cad-living-niche-ply.png';floor_objects['LivingDining']['CAD_area_m2']=living['cad_polygon_area_m2'];floor_objects['LivingDining']['observed_bay_added_area_m2']=living['area_m2']-living['cad_polygon_area_m2'];floor_objects['LivingDining']['evidence_status']='measured main area and back bands; inferred connections across occluded bay sides'
 # Perimeter uses actually measured inner faces; outer depth240mm is CAD conventional offset.
 perimeter=[('577','Photography'),('578','Photography'),('57C','Corridor'),('57D','Corridor'),('57E','Corridor'),('57F','Corridor'),('583','Bar'),('584','Bar'),('58B','LivingDining'),('58C','LivingDining'),('58D','LivingDining'),('591','LivingDining'),('599','Game')]
 walls={}
 for handle,area in perimeter:
  l=lines[handle];walls[handle]=wall('WALL_'+handle+'_'+area,l['a'][:2],l['b'][:2],.240,heights[area],area,mats[area],'cad.dxf LINE '+handle+'; PLY registered; outer thickness CAD offset')
 # Measured perimeter convex corners require explicit native miters between wall strips.
 for name,x,y,sx,sy,area in [('photo_SW',4600.5,-13505,-1,-1,'Photography'),('photo_NW',4600.5,-10258,-1,1,'Photography'),('corridor_SE',17803.5,-13505,1,-1,'Corridor'),('bar_NE',17649.5,-9870,1,1,'Bar'),('living_NE',13126.5,-3775,1,1,'LivingDining'),('living_NW',6076.5,-3775,-1,1,'LivingDining')]:
  pts=[xy(x,y),xy(x+sx*240,y),xy(x+sx*240,y+sy*240),xy(x,y+sy*240)]
  mesh_poly('WALL_CORNER_'+name,pts,0,heights[area],area,'Walls',mats[area],'CAD adjacent perimeter planes and240mm outer offset','inferred')
 # Actual glazed aperture is1.16 m wide; cutting both CAD front remnants avoids false occlusion.
 cutter=box('TEMP_observed_living_bay_opening',(-7.55,7.44,1.171),(.85,1.16,2.342),'LivingDining','Helpers',white,'source8_f measured aperture','measured')
 for handle in ['58D','591']:
  mod=walls[handle].modifiers.new('Observed wider living bay aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;bpy.context.view_layer.objects.active=walls[handle];bpy.ops.object.modifier_apply(modifier=mod.name);walls[handle]['source_conflict']='CAD narrow0.416 m recess is wider in actual PLY and photographs; native aperture follows source8_f'
 created.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
 for name,a,b,z0,z1 in [('Back_lower',(-9.02,8.20),(-9.02,6.91),0,1.60),('Back_upper',(-8.72,8.20),(-8.72,6.91),1.60,2.486),('North_lower',niche_north,(-9.02,8.20),0,1.60),('South_lower',(-9.02,6.91),niche_south,0,1.60),('North_upper',niche_north,(-8.72,8.20),1.60,2.486),('South_upper',(-8.72,6.91),niche_south,1.60,2.486)]:
  ob=wall('WALL_LivingBay_'+name,cad(*a),cad(*b),.12,z1,'LivingDining',white,'PLY bay returns + source8_f; side wall connections inferred',z0=z0);ob['evidence_status']='measured back distance bands; inferred occluded connections'
 box('LivingBay_back_step_ledge',(-8.87,7.555,1.595),(.30,1.29,.010),'LivingDining','Walls',white,'PLY back plane changes from X−9.02 to−8.72 nearZ1.60','inferred connection between measured surfaces')
 # Corridor east wall includes photo-evidenced closed side door omitted from CAD symbols.
 walls['587']=wall('WALL_587_Corridor',lines['587']['a'][:2],lines['587']['b'][:2],.240,3.021,'Corridor',gray,'cad.dxf587 + panorama7_r')
 # Return at bar/corridor edge.
 wall('WALL_bar_entry_return',[13234.5,-9870],[13234.5,-10395],.108,2.812,'Bar',gray,'cad.dxf585,586')
 # Photo north exterior return and shared game/photo partition.
 wall('WALL_photo_north_return',[6049.5,-10258],[4600.5,-10258],.240,2.774,'Photography',white,'cad.dxf576 part')
 shared=wall('WALL_570_photo_game',[6049.5,-10134],[10118.5,-10134],.124,2.786,'Game',purple,'cad.dxf570,576');shared.data.materials.append(white)
 for p in shared.data.polygons:
  if p.normal.y<-.5:p.material_index=1
 # Close the partition termination flush with the corridor finish line.
 # Source5_f showed that leaving the124 mm cap recessed exposed a false indigo strip.
 mesh_poly('WALL_photo_game_corridor_end_cap',[xy(10118.5,-10258),xy(10242.5,-10258),xy(10242.5,-10134),xy(10118.5,-10134)],0,2.786,'Corridor','Walls',gray,'CAD paired corridor finish X10242.5; source5_f gray partition termination')
 # East partitions modeled as separate wall piers and lintels with actual openings.
 for name,y0,y1,area,h in [('photo_south',-13505,-12580,'Photography',2.774),('photo_north',-11203,-10258,'Photography',2.774),('game_south',-10134,-10005,'Game',2.786),('game_north',-9094,-7176,'Game',2.786)]:
  o=wall('WALL_'+name,[10118.5,y1],[10118.5,y0],.124,h,area,mats[area],'cad.dxf paired x10118.5/10242.5',side=-1);o.data.materials.append(gray)
  for p in o.data.polygons:
   if p.normal.x>.5:p.material_index=1
 # Living south partition (both game and hall below).
 for name,x0,x1,below in [('west',6076.5,10118.5,'Game'),('hall',10118.5,11767.5,'Corridor'),('east',12668.5,13126.5,'Corridor')]:
  o=wall('WALL_living_south_'+name,[x0,-7063],[x1,-7063],.113,2.792,'LivingDining',white,'cad.dxf592,594,588');o.data.materials.append(mats[below])
  for p in o.data.polygons:
   if p.normal.y<-.5:p.material_index=1
 # Bar/corridor divider.
 wall('WALL_bar_south',[13274.5,-12216],[17649.5,-12216],.123,2.812,'Bar',gray,'cad.dxf580,582')
 # Diamond structural pillar has a tiny bevel corner exactly recorded in CAD.
 poly=[xy(*lines[h]['a'][:2]) for h in ['59A','59B','59C','59D','59E']]
 pillar=mesh_poly('COLUMN_diamond',poly,0,3.021,'Corridor','Walls',gray,'cad.dxf59A:59E');pillar['measured_plan_area_m2']=1.1333795
 # Remove column footprint from native floor without hidden floor below solid.
 cutter=mesh_poly('TEMP_column_floor_cut',poly,-.15,.02,'Corridor','Helpers',gray,'CAD column', 'inferred')
 mod=floor_objects['Corridor'].modifiers.new('Column footprint opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;bpy.context.view_layer.objects.active=floor_objects['Corridor'];bpy.ops.object.modifier_apply(modifier=mod.name);created.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
 # Rectangular opening/door assembly uses local x as width and y as thickness; hinge origins are geometric hinges.
 def opening(name,center,width,depth,height,rotation,area,material,leaf=False,swing=0,source='',unknown=False):
  # Center and rotation in raw PLY frame; center z floor.
  cx,cy=center;R=Matrix.Rotation(rotation,3,'Z')
  def tr(x,y,z):return Vector((cx,cy,0))+R@Vector((x,y,z))
  framew=.047
  for side in [-1,1]:
   o=box('FRAME_'+name+('_L' if side<0 else '_R'),tr(side*(width/2-framew/2),0,height/2),(framew,depth,height),area,'Openings',material,source,rot=rotation);bevel(o,.005)
  o=box('FRAME_'+name+'_head',tr(0,0,height-framew/2),(width,depth,framew),area,'Openings',material,source,rot=rotation);bevel(o,.005)
  if leaf:
   innerwidth=width-2*framew-.005;innerh=height-framew-.007;hinge=tr(width/2-framew,0,0)
   me=bpy.data.meshes.new('DOOR_'+name+'_editable_leaf');verts=[(x,y,z) for z in [.004,innerh] for y in [-.021,.021] for x in [-innerwidth,0]];faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];me.from_pydata(verts,[],[tuple(reversed(f)) for f in faces]);me.materials.append(material);me.update();o=bpy.data.objects.new('DOOR_'+name+'_hinged_leaf',me);coll(area,'Openings').objects.link(o);o.location=hinge;o.rotation_euler.z=rotation+swing;register(o,area,'Openings',source,'inferred' if unknown else 'measured');o['hinge_axis']='local Z';o['clear_width_m']=innerwidth;o['height_m']=innerh;o['opening_width_m']=width;bevel(o,.007)
   for sign in [-1,1]:
    h=box('HANDLE_'+name+str(sign),(0,0,0),(.12,.018,.018),area,'Openings',black,source,'inferred');h.parent=o;h.location=(-innerwidth+.095,sign*.07,1.02);h.rotation_euler=(0,0,0);bevel(h,.008)
    p=box('HANDLE_ROSETTE_'+name+str(sign),(0,0,0),(.044,.016,.08),area,'Openings',black,source,'inferred');p.parent=o;p.location=(-innerwidth+.05,sign*.028,1.015);bevel(p,.018)
   return o
 # Photography broad doorway: photographs show no physical door leaf, so only frame.
 opening('Photography',xy(10180.5,-11891.5),1.377,.16,2.714,angle+math.pi/2,'Photography',black,False,source='cad.dxf5B2,5B3; panorama3_b no visible leaf')
 wall('LINTEL_photo',[10118.5,-11203],[10118.5,-12580],.124,2.774,'Photography',white,'cad.dxf5B2 DH2714',z0=2.714,side=-1)
 game_leaf=opening('Game',xy(10180.5,-9549.5),.911,.16,2.171,angle-math.pi/2,'Game',wood,True,math.pi/2,'cad.dxf5B9,5BA; panorama6_l; PLY leaf lies west from south hinge at rawY3.02')
 game_leaf.data.materials.append(mat('ARCH lavender game door inner face',(.43,.30,.55),.65))
 for face in game_leaf.data.polygons:
  if face.normal.y>.5:face.material_index=1
 wall('LINTEL_game',[10118.5,-9094],[10118.5,-10005],.124,2.786,'Game',purple,'cad.dxf5B9 DH2171',z0=2.171,side=-1)
 opening('LivingDining',xy(12218,-7119.5),.901,.16,2.166,angle,'LivingDining',wood,True,math.radians(-90),'cad.dxf5C0,5C1; panorama8_l')
 wall('LINTEL_living',[11767.5,-7063],[12668.5,-7063],.113,2.792,'LivingDining',white,'cad.dxf5C0 DH2166',z0=2.166)
 for name,xc,yc,w,d,rot in [('photo',10180.5,-11891.5,1.377,.124,math.pi/2),('game',10180.5,-9549.5,.911,.124,math.pi/2),('living',12218,-7119.5,.901,.113,0)]:
  o=box('THRESHOLD_'+name,(*xy(xc,yc),-.012),(w,d,.024),'Corridor','Floors',floor_gray,'cad.dxf door extent',rot=angle+rot)
 # Closed utility/service door on east corridor wall is clearly observed but CAD omits its opening.
 dc=(-.483,5.208);w=.938;dh=2.190
 cutter=box('TEMP_service_opening',(*dc,dh/2),(w,.70,dh),'Corridor','Helpers',gray,'panorama7_r + point cloud doorway',rot=math.pi/2)
 mod=walls['587'].modifiers.new('Observed service door opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;bpy.context.view_layer.objects.active=walls['587'];bpy.ops.object.modifier_apply(modifier=mod.name);created.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
 opening('Service_closed',dc,w,.21,dh,-math.pi/2,'Corridor',wood,True,0,'panorama7_r + PLY color/surface elevation, no interior observation',True)
 # Game chamfered mirror is owned by build_game.py to avoid duplicate physical panels.
 # CAD south glazing aligns with photographed black blueprint, not a physical opening.
 # Preserve the classification conflict in metadata; the continuous photographed wall remains solid.
 walls['57C']['cad_glazing_conflict']='5C2:5C9 glazing classification rejected here: registered panorama1_r shows black blueprint mounted on continuous wall.'
 # Actual east entrance: photographed gray security leaf, frame, fluted strip, peephole and hardware.
 entrance_material=mat('ARCH graphite entrance enamel',(.115,.122,.129),.34,.35)
 ec=(4.128,-.024);ew=.982;eh=2.060
 cut=box('TEMP_observed_entrance_cut',(*ec,eh/2),(ew,.70,eh),'Corridor','Helpers',gray,'panorama1_r and PLY east wall',rot=math.pi/2)
 mod=walls['57D'].modifiers.new('Photographed entrance opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=walls['57D'];bpy.ops.object.modifier_apply(modifier=mod.name);created.remove(cut);bpy.data.objects.remove(cut,do_unlink=True)
 leaf=opening('East_entrance',ec,ew,.15,eh,-math.pi/2,'Corridor',entrance_material,True,0,'panorama1_r; source rays intersect east PLY wall x4.13; height approximately2.06m',True)
 # Fixed fluted decoration on the same leaf, not an unsupported second door.
 for j in range(11):
  rib=box('ENTRANCE_leaf_fluting_'+str(j),(0,0,0),(.004,.005,eh-.10),'Corridor','Openings',black,'panorama1_r vertical decorative band','inferred');rib.parent=leaf;rib.location=(-.69+j*.008,-.024,eh/2);bevel(rib,.001)
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.016,depth=.008,location=(0,0,0));peephole=bpy.context.object;peephole.name='ENTRANCE_peephole';peephole.data.materials.append(silver);register(peephole,'Corridor','Openings','panorama1_r visible peephole','inferred');peephole.parent=leaf;peephole.location=(-.44,-.026,1.48);peephole.rotation_euler.x=math.pi/2
 # Plaster ceilings and perimeter coves: CAD local heights constrain main+lower planes.
 def slab_rect(name,x0,x1,y0,y1,z,thick,area,material,source):return cbox(name,((x0+x1)/2,(y0+y1)/2,z+thick/2),((x1-x0)/1000,(y1-y0)/1000,thick),area,'Ceilings',material,source)
 # Photo flat ceiling; no inferred cove.
 slab_rect('CEILING_Photography',4600.5,10118.5,-13505,-10258,2.774,.07,'Photography',white,'CH2774 cad5D8 + panorama3_u')
 def cove(area,x0,x1,y0,y1,mainz,lowerz,inset):
  slab_rect('CEILING_'+area+'_center',x0,x1,y0,y1,mainz,.07,area,mats[area],f'CAD CH main {mainz}')
  for nm,xx0,xx1,yy0,yy1 in [('south',x0,x1,y0,y0+inset),('north',x0,x1,y1-inset,y1),('west',x0,x0+inset,y0+inset,y1-inset),('east',x1-inset,x1,y0+inset,y1-inset)]:
   slab_rect('COVE_'+area+'_'+nm,xx0,xx1,yy0,yy1,lowerz,.09,area,mats[area],f'CAD CH low {lowerz}; cove inset inferred from photos')
  # Cove upstands and visible light strips on upper lip.
  for nm,xc,yc,dx,dy in [('south',(x0+x1)/2,y0+inset-.018*1000,(x1-x0-2*inset)/1000,.020),('north',(x0+x1)/2,y1-inset+.018*1000,(x1-x0-2*inset)/1000,.020),('west',x0+inset-.018*1000,(y0+y1)/2,.020,(y1-y0-2*inset)/1000),('east',x1-inset+.018*1000,(y0+y1)/2,.020,(y1-y0-2*inset)/1000)]:
   cbox('COVE_lip_'+area+'_'+nm,(xc,yc,lowerz+.13),(dx,dy,.08),area,'Ceilings',mats[area],'panorama cove photos','inferred');cbox('COVE_LED_'+area+'_'+nm,(xc,yc,lowerz+.176),(dx,dy,.009),area,'Lighting',light,'panorama cove photos','inferred')
   data=bpy.data.lights.new('COVE_BOUNCE_'+area+'_'+nm,'AREA');data.energy=7.5*max(dx,dy);data.color=(1,.70,.40);data.shape='RECTANGLE';data.size=dx;data.size_y=dy;ob=bpy.data.objects.new(data.name,data);coll(area,'Lighting').objects.link(ob);ob.location=(*xy(xc,yc),lowerz+.187);ob.rotation_euler=(math.pi,0,angle);ob.visible_camera=False;ob.visible_glossy=False;ob['source']='Photographed cove LED indirect ceiling illumination';ob['evidence_status']='inferred radiant intensity'
 cove('LivingDining',6076.5,13126.5,-7063,-3775,2.792,2.486,280)
 cove('Game',6049.5,10118.5,-10134,-7176,2.786,2.470,290)
 # The observed broader bay retains an inferred enclosing ceiling at the adjoining low soffit.
 mesh_poly('CEILING_living_curtain_bay',niche_poly,2.486,2.556,'LivingDining','Ceilings',white,'PLY-supported wider bay footprint; height inferred from adjoining cove','inferred')
 # Black suspended open grid: real bars, no baked checkerboard.
 def grid(area,poly,z):
  # Ray intersections against arbitrary footprint clip every slat to actual area.
  def intervals(axis,value):
   other=1-axis;cross=[]
   for i,a in enumerate(poly):
    b=poly[(i+1)%len(poly)]
    if (a[axis]<=value<b[axis]) or (b[axis]<=value<a[axis]):cross.append(a[other]+(value-a[axis])/(b[axis]-a[axis])*(b[other]-a[other]))
   cross.sort();return list(zip(cross[::2],cross[1::2]))
  for axis in [0,1]:
   lo=min(p[axis] for p in poly);hi=max(p[axis] for p in poly);s=lo+60;i=0
   while s<hi:
    for a,b in intervals(axis,s):
     if b-a<10:continue
     x,y=(s,(a+b)/2) if axis==0 else ((a+b)/2,s);d=(.007,(b-a)/1000,.055) if axis==0 else ((b-a)/1000,.007,.055)
     cbox(f'GRID_{area}_{axis}_{i}',(x,y,z+.0275),d,area,'Ceilings',black,'panorama1,2,4,5,7_u; grid spacing estimated130mm','inferred');i+=1
    s+=130
  # High dark plenum is observed incompletely; native reference-free enclosure, explicitly inferred.
  mesh_poly('CEILING_'+area+'_dark_plenum',[xy(*p) for p in poly],z+.40,z+.46,area,'Ceilings',black,'PLY sparse upper returns; plenum completion inferred','inferred')
 grid('Bar',next(a for a in areas if a['name']=='Bar')['polygon_cad_mm'],2.780)
 grid('Corridor',next(a for a in areas if a['name']=='Corridor')['polygon_cad_mm'],2.800)
 # Skirting follows measured wall faces; skip opening edges and mirror base.
 for h,l in lines.items():
  if l['layer']!='A-WALL-LINE' or int(h,16)>=int('59F',16):continue
  a,b=Vector(l['a'][:2]),Vector(l['b'][:2]);length=(b-a).length/1000
  if length<.3 or h in ['59A','59B','59C','59D','59E','599','58D','58E','58F','590','591']:continue
  mid=(a+b)/2;area='Corridor'
  if mid.x<10130 and mid.y<-10200:area='Photography'
  elif 6000<mid.x<10130 and -10200<mid.y<-7100:area='Game'
  elif mid.y>-7100:area='LivingDining'
  elif mid.x>13270 and mid.y>-12300:area='Bar'
  v=(b-a).normalized();off=Vector((-v.y,v.x))*7
  wall('SKIRT_'+h,a+off,b+off,.012,.065,area,white if area in ['Photography','LivingDining'] else black,'panorama skirting + CAD wall '+h,side=-1)
  # move skirting out of Walls collection to trim category
  o=created[-1];coll(area,'Walls').objects.unlink(o);coll(area,'Trim').objects.link(o);o['category']='Trim'
 # Vent grilles with real slats.
 def vent(name,x,y,width,depth,z,area,rot=0):
  o=cbox('VENT_'+name+'_frame',(x,y,z),(width,depth,.030),area,'Services',white,'panorama ceiling vent','inferred');o.rotation_euler.z+=rot
  o=cbox('VENT_'+name+'_dark_recess',(x,y,z-.017),(width-.036,depth-.036,.012),area,'Services',black,'panorama ceiling vent','inferred');o.rotation_euler.z+=rot
  for i in range(max(2,int((depth-.04)/.025))):
   yy=-(depth-.045)/2+i*.025;xx,yy2=math.cos(rot)*0-math.sin(rot)*yy,math.sin(rot)*0+math.cos(rot)*yy
   o=cbox(f'VENT_{name}_slat_{i}',(x+xx*1000,y+yy2*1000,z-.023),(width-.048,.006,.009),area,'Services',silver,'panorama vent slats','inferred');o.rotation_euler.z+=rot
 vent('Game',8110,-7625,1.17,.21,2.445,'Game')
 fixtures=json.loads((ROOT/'research/cad-fixture-measurements.json').read_text())
 # Living grilles face inward on the vertical cove fronts, as observed in8_f and8_b.
 for measured in fixtures['vents']:
  name=measured['name'];x,y,z=measured['scene_center_m'];width=measured['width_m'];height=measured['height_m'];normal=measured['normal_scene'][0]
  box('VENT_'+name+'_cove_mount',(x-normal*.019,y,z),(.045,width+.07,height+.055),'LivingDining','Services',white,measured['source'],'inferred mounting thickness')
  box('VENT_'+name+'_frame',(x,y,z),(.027,width,height),'LivingDining','Services',white,measured['source'],'measured')
  box('VENT_'+name+'_dark_recess',(x+normal*.016,y,z),(.008,width-.027,height-.023),'LivingDining','Services',black,measured['source'],'measured')
  for i in range(5):
   box(f'VENT_{name}_slat_{i}',(x+normal*.022,y,z-height/2+.020+i*(height-.04)/4),(.013,width-.033,.006),'LivingDining','Services',silver,measured['source'],'inferred slat section')
 def lamp(name,x,y,z,area,kind='disc',warm=True,r=.055,aim=None):
  material=light if warm else neutral_light
  if kind=='disc':
   bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=.024,location=(*xy(x,y),z));o=bpy.context.object;o.name='LIGHT_'+name+'_rim';o.data.materials.append(white if area in ['LivingDining','Photography'] else black);register(o,area,'Lighting','panorama light fixture','inferred')
   bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r*.82,depth=.006,location=(*xy(x,y),z-.015));o=bpy.context.object;o.name='LIGHT_'+name+'_diffuser';o.data.materials.append(material);register(o,area,'Lighting','panorama light fixture','inferred')
  else:cbox('LIGHT_'+name+'_diffuser',(x,y,z),(.14,.14,.027),area,'Lighting',material,'panorama light fixture','inferred')
  data=bpy.data.lights.new('LIGHTDATA_'+name,'SPOT' if aim else 'AREA');data.energy=25 if r<.1 else 65;data.color=(1,.83,.62) if warm else (.86,.93,1)
  if aim:data.spot_size=math.radians(100);data.spot_blend=.65;data.shadow_soft_size=.023
  else:data.shape='DISK';data.size=r*1.8
  ob=bpy.data.objects.new('ILLUM_'+name,data);coll(area,'Lighting').objects.link(ob);ob.location=(*xy(x,y),z-.04);ob.visible_camera=False;ob.visible_glossy=False;ob['evidence_status']='inferred illumination intensity'
  if aim:ob.rotation_euler=Vector(aim).to_track_quat('-Z','Y').to_euler()
 # Living perimeter downlights and central square+round fixtures.
 for i,measured in enumerate(fixtures['perimeter_downlights']):
  x,y,z=measured['scene_center_m'];cx,cy=cad(x,y);side=measured['side'];aim={'west':(-.15,0,-1),'east':(.15,0,-1),'south':(0,-.15,-1),'north':(0,.15,-1)}[side]
  lamp('Living_'+side+str(i),cx,cy,z,'LivingDining',r=.040,aim=aim)
  for o in created[-2:]:o['source']=measured['source']+' pixel '+str(measured['pixel_at_1200'])+' at1200px; ray intersection';o['evidence_status']='measured';o['measurement_file']='research/cad-fixture-measurements.json'
 x,y,z=fixtures['round_fixture']['scene_center_m'];cx,cy=cad(x,y);lamp('Living_dining_round',cx,cy,z,'LivingDining',warm=False,r=fixtures['round_fixture']['diameter_m']/2)
 # Living layered fixture measured by projecting its cool-white source8_f pixels onto z2.74.
 # Outer source extent1.38x0.84m, center(-5.139,7.538); native round corners account for luminous bloom.
 for ring,(width,depth,z) in enumerate([(1.30,.77,2.744),(1.10,.60,2.712)]):
  curve=bpy.data.curves.new('Living layered light ring '+str(ring),'CURVE');curve.dimensions='3D';curve.bevel_depth=.026;curve.bevel_resolution=4;sp=curve.splines.new('POLY');pts=[];radius=.095
  for xc,yc,start in [(width/2-radius,depth/2-radius,0),(-width/2+radius,depth/2-radius,90),(-width/2+radius,-depth/2+radius,180),(width/2-radius,-depth/2+radius,270)]:
   for j in range(9):
    theta=math.radians(start+j*90/8);pts.append((-5.139+xc+radius*math.cos(theta),7.538+yc+radius*math.sin(theta),z))
  sp.points.add(len(pts)-1)
  for p,co in zip(sp.points,pts):p.co=(*co,1)
  sp.use_cyclic_u=True;o=bpy.data.objects.new('LIGHT_Living_layered_rectangle_'+str(ring),curve);coll('LivingDining','Lighting').objects.link(o);o.data.materials.append(neutral_light);register(o,'LivingDining','Lighting','panorama8_f cool-white pixel rays intersect z2.74; research/cad-living-square-mask.png','measured')
 panel=box('LIGHT_Living_layered_center_panel',(-5.139,7.538,2.698),(.84,.46,.025),'LivingDining','Lighting',neutral_light,'panorama8_f layered central luminous plate','inferred');bevel(panel,.07)
 lamp('Game_square',8010,-8700,2.745,'Game',kind='square',warm=False,r=.09)
 # Photographed corridor square fixtures and track heads are supplied by build_corridor.py.
 # Ceiling smoke sensors evident in each finished room.
 sx,sy,sz=fixtures['smoke_sensor']['scene_center_m'];scx,scy=cad(sx,sy)
 for area,x,y,z in [('Game',8780,-8820,2.76),('LivingDining',scx,scy,sz)]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.045,depth=.021,location=(*xy(x,y),z));o=bpy.context.object;o.name='SMOKE_SENSOR_'+area;o.data.materials.append(white);register(o,area,'Services','panorama upward cube face','inferred')
 # Accurate source dimensions kept in-scene; native mesh dimensions remain directly editable.
 bpy.context.scene['CAD reference area_m2']=87.25;bpy.context.scene['Native reconstructed net_floor_area_m2']=87.2517385+living['area_m2']-living['cad_polygon_area_m2'];bpy.context.scene['CAD area conflict']='Source8_f and PLY reveal a wider glazed bay than the0.416 m CAD recess. Native geometry follows observed footprint; CAD87.25 m² retained as comparison reference.';bpy.context.scene['CAD reference net_width_m']=13.203;bpy.context.scene['CAD reference net_depth_m']=9.73;bpy.context.scene['source_registration_json']='research/registration-cad.json';bpy.context.scene['floor_datum_PLY_z_m']=reg['ply_floor_datum_m']
 from final_plenum_height import apply_plenum_height
 apply_plenum_height(ROOT)
 return {'objects':created,'collections':collections,'areas':areas,'registration':reg}
