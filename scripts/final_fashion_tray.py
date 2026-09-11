"""Replace the incomplete black-tray scan cut with observed editable components.
Source3_l registered rays determine the tray, spectacles and two bracelet positions.
No file saves; invoked by the final refinement batch after the original fashion build.
"""
from pathlib import Path
import bpy, math
from mathutils import Vector, Matrix

def apply_fashion_tray(ROOT):
 ROOT=Path(ROOT)
 collection=bpy.data.collections['Fashion_Fixtures']
 for o in list(bpy.data.objects):
  if o.name=='FAS-JEWELRY-TRAY' or o.name.startswith('FAS-JEWELRY-TRAY.'):
   bpy.data.objects.remove(o,do_unlink=True)
 old_recess=bpy.data.objects.get('FAS-VENT-entry_dark_recess')
 if old_recess:bpy.data.objects.remove(old_recess,do_unlink=True)
 center=Vector((-5.4455,-.2177,.4715))
 group=bpy.data.objects.new('FAS-JEWELRY-TRAY',None);collection.objects.link(group);group.location=center
 group['stable_id']='FAS-JEWELRY-TRAY';group['coverage_id']='FAS-JEWELRY-TRAY';group['area']='Fashion_Fixtures';group['source']='data/cube-map/3_l.jpg';group['evidence_status']='observed tray, spectacles and two bracelets; source-ray XY measured at native shelf top'
 bpy.context.view_layer.update()
 def mat(name,color,rough=.5,metal=0,transmission=0):
  m=bpy.data.materials.get(name)
  if m:return m
  m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;bs.inputs['Transmission Weight'].default_value=transmission;bs.inputs['IOR'].default_value=1.48;return m
 lining=mat('Fashion jewelry black velvet',(.005,.006,.008),.93)
 base=mat('Fashion jewelry tray gray backing',(.15,.16,.15),.66)
 gold=mat('Fashion jewelry warm gold rim and bracelets',(.56,.32,.058),.24,.87)
 bronze=mat('Fashion spectacles fine bronze wire',(.25,.17,.075),.25,.8)
 lens=mat('Fashion spectacles clear lenses',(.13,.15,.16),.06,0,.86)
 def tag(o,name,material):
  o.name=name;collection.objects.link(o);o.parent=group;o.matrix_parent_inverse=Matrix.Identity(4);o.data.materials.append(material);o['coverage_id']='FAS-JEWELRY-TRAY';o['stable_id']=name;o['area']='Fashion_Fixtures';o['source']='data/cube-map/3_l.jpg';o['evidence_status']='observed separate component; fine thickness and concealed joins inferred';return o
 def box(name,loc,size,material,bevel=0):
  vertices=[(sx*size[0]/2,sy*size[1]/2,sz*size[2]/2) for sz in [-1,1] for sy in [-1,1] for sx in [-1,1]]
  faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
  m=bpy.data.meshes.new(name+'.Mesh');m.from_pydata(vertices,[],faces);m.update();o=tag(bpy.data.objects.new(name,m),name,material);o.location=Vector(loc)-center
  if bevel:mod=o.modifiers.new('Editable tray edge radius','BEVEL');mod.width=bevel;mod.segments=3
  return o
 def curve(name,points,radius,material,closed=False):
  m=bpy.data.curves.new(name+'.Curve','CURVE');m.dimensions='3D';m.bevel_depth=radius;m.bevel_resolution=3;s=m.splines.new('POLY');s.points.add(len(points)-1)
  for p,co in zip(s.points,points):p.co=(*(Vector(co)-center),1)
  s.use_cyclic_u=closed;return tag(bpy.data.objects.new(name,m),name,material)
 prefix='FAS-JEWELRY-TRAY.'
 box(prefix+'Backing',center,(.315,.205,.015),base,.003)
 box(prefix+'Velvet',(-5.4455,-.2177,.4794),(.299,.189,.002),lining,.001)
 for xx in [-5.603,-5.288]:box(prefix+f'Rim.X.{xx}',(xx,-.2177,.480),(.0025,.205,.007),gold,.0008)
 for yy in [-.3202,-.1152]:box(prefix+f'Rim.Y.{yy}',(-5.4455,yy,.480),(.315,.0025,.007),gold,.0008)
 p1=Vector((-5.34177,-.22716,.484));p2=Vector((-5.40407,-.17799,.484));u=(p2-p1).normalized();v=Vector((-u.y,u.x,0))
 for i,c in enumerate([p1,p2],1):
  points=[c+u*(.030*math.cos(k*math.tau/48))+v*(.024*math.sin(k*math.tau/48)) for k in range(48)]
  curve(prefix+f'Spectacles.Rim.{i}',points,.00135,bronze,True)
  m=bpy.data.meshes.new(prefix+f'Spectacles.Lens.{i}.Mesh');m.from_pydata([tuple(p-center) for p in points],[],[tuple(range(48))]);m.update();o=tag(bpy.data.objects.new(prefix+f'Spectacles.Lens.{i}',m),prefix+f'Spectacles.Lens.{i}',lens)
  sol=o.modifiers.new('Editable thin lens','SOLIDIFY');sol.thickness=.0006
 curve(prefix+'Spectacles.Bridge',[p1+u*.028,(p1+p2)/2+Vector((0,0,.003)),p2-u*.028],.0011,bronze)
 for i,c in enumerate([p1-u*.030,p2+u*.030],1):
  curve(prefix+f'Spectacles.FoldedTemple.{i}',[c,c+v*.041+Vector((0,0,.002)),c+v*.068-u*.008],.0012,bronze)
 for i,c in enumerate([Vector((-5.52521,-.23833,.485)),Vector((-5.51956,-.20521,.486))],1):
  curve(prefix+f'Bracelet.{i}',[c+Vector((.027*math.cos(k*math.tau/64),.027*math.sin(k*math.tau/64),0)) for k in range(64)],.0019,gold,True)
 # Visible dark cavity behind the entry grille; its hidden duct depth is unknown.
 vent=bpy.data.objects['FAS-VENT-entry_frame'];vc=vent.matrix_world.translation
 recess=box('FAS-VENT-entry_dark_recess',(vc.x,vc.y,vc.z-.018),(.216,.998,.004),lining)
 bpy.context.view_layer.update();world=recess.matrix_world.copy();recess.parent=None;recess.matrix_world=world
 recess['coverage_id']='FAS-VENT';recess['evidence_status']='source3_u dark grille recess observed; only shallow local backing modeled, unobserved ductwork omitted'
 bpy.context.view_layer.update()
 return {'module':'final_fashion_tray','inventory_id':'FAS-JEWELRY-TRAY','tray_dimensions_m':[.315,.205,.015],'tray_center_m':list(center),'spectacle_lens_centers_m':[list(p1),list(p2)],'bracelets':2,'native_components':len(group.children),'uncertainty':'Fine lens/wire thickness and folded temples inferred; source silhouettes and positions retained.'}
