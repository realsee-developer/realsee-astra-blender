"""Source comparison corrections to material albedo and observed living fixture details."""
import bpy,math

def refine_appearance(ROOT,a):
 palettes={'Living honey oak':(.19,.067,.015),'Sofa caramel leather shell':(.29,.105,.031),'Natural woven cane':(.31,.18,.065),'Coffee table pale rattan':(.47,.35,.16),'Living plant green':(.012,.066,.004),'Sofa cream woven upholstery':(.67,.62,.53),'Cushion terracotta orange':(.52,.10,.012),'Cushion ocher yellow':(.63,.34,.02),'Appliance white':(.72,.72,.69)}
 for name,color in palettes.items():
  m=bpy.data.materials.get(name)
  if m:
   m.diffuse_color=(*color,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
 # Subtle editable fine texture: wood grain and cotton weave.
 for name in ['Living honey oak','Sofa cream woven upholstery','Sofa caramel leather shell','Natural woven cane']:
  m=bpy.data.materials[name];nt=m.node_tree;p=nt.nodes.get('Principled BSDF');co=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(5,95,3) if name=='Living honey oak' else (1,1,1);nt.links.new(co.outputs['Object'],scale.inputs[0]);tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5 if name=='Living honey oak' else 170;tex.inputs['Detail'].default_value=2;nt.links.new(scale.outputs[0],tex.inputs['Vector']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.0007;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
  if name=='Living honey oak':
   ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.08,.026,.005,1);ramp.color_ramp.elements[1].color=(.26,.10,.026,1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
 for o in bpy.data.objects:
  if o.name.startswith('LIV.BroadLeafPlant.Leaf.'):
   for p in o.data.polygons:p.use_smooth=True
  if o.type=='LIGHT' and o.name.startswith('LIGHT_FILL'):
   o.visible_camera=False;o.visible_glossy=False
   if 'Game' in o.name:o.data.color=(.86,.83,1);o.data.energy=50
   elif 'LivingDining' in o.name:o.data.color=(1,.94,.84);o.data.energy=85
  if o.type=='MESH' and ('Cushion' in o.name or '.Seat.' in o.name) and o.name.startswith('LIV.SOFA'):
   for mod in o.modifiers:
    if mod.type=='BEVEL':mod.segments=5
 a.area_collection('LivingDining_Details','data/cube-map/8_f.jpg;8_r.jpg; actual source comparison')
 cane=bpy.data.materials['Natural woven cane'];black=bpy.data.materials['Charcoal equipment'];wood=bpy.data.materials['Living honey oak']
 # Real woven basket around the pot, represented by physical separate strands.
 def basket_radius(z):return (.10+.875*z if z<.04 else .135+.015*(z-.04)/.18)+.004
 for j in range(12):
  z=.028+j*.017;r=basket_radius(z)
  a.curve(f'LIV.Basket.HorizontalWeave.{j}',[(-3.90+r*math.cos(k*2*math.pi/64),6.18+r*math.sin(k*2*math.pi/64),z) for k in range(64)],.003,cane,True)
 for j in range(40):
  t=j*2*math.pi/40;a.curve(f'LIV.Basket.VerticalWeave.{j}',[(-3.90+(basket_radius(z)+.003*math.sin(z*math.pi/.017))*math.cos(t),6.18+(basket_radius(z)+.003*math.sin(z*math.pi/.017))*math.sin(t),z) for z in [.01+k*.012 for k in range(20)]],.0024,cane)
 # The speaker front faces along the console, as seen in the registered source image.
 box=bpy.data.objects.get('LIV.Speaker.1')
 if box:
  cone=bpy.data.objects['LIV.Speaker.1.Cone'];cone.location=(-5.875,6.21,.72);cone.rotation_euler=(0,math.pi/2,0)
  for j,xx in enumerate([-6.06,-5.96]):
   a.cyl(f'LIV.Speaker.SideDriver.{j}',(xx,6.335,.72),.042,.007,black,32,(math.pi/2,0,0))
 # Clear bottle transmission, no opaque white proxy.
 m=bpy.data.materials.get('Clear water bottle')
 if m:
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.333;p.inputs['Roughness'].default_value=.07
 # Fifteen photographed track heads need physical light emission, in addition to visible diffuser meshes.
 # Source fixture geometry supplies every position/orientation; intensities are appearance estimates.
 from mathutils import Vector
 a.area_collection('Fashion_Illumination','data/cube-map/3_f.jpg;3_u.jpg; actual fifteen track luminaires')
 for i in range(1,16):
  surface=bpy.data.objects[f'FAS-SPOT-{i:02}_diffuser'];name=f'FAS-SPOT-{i:02}_Light';d=bpy.data.lights.new(name,'SPOT');d.energy=25;d.color=(.96,.96,1);d.spot_size=math.radians(85);d.spot_blend=.6;d.shadow_soft_size=.028
  o=bpy.data.objects.new(name,d);a.collection.objects.link(o);direction=surface.rotation_euler.to_matrix()@Vector((0,0,1));o.location=surface.location+direction*.006;o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();o.visible_camera=False;o.visible_glossy=False;o['source']=surface['source'];o['evidence_status']='observed luminaire; emitted power inferred from source appearance'

 # Broad neutral camera-invisible bounce approximates the photographed white room exposure.
 fill=a.area_light('FAS_WhiteRoom_Bounce',(-6.25,1.30,2.64),180,(.96,.98,1),2.5)
 fill.visible_camera=False;fill.visible_glossy=False;fill['evidence_status']='inferred photographic bounced illumination; not an additional fixture'
 m=bpy.data.materials.get('ARCH matte black metal')
 if m:
  p=m.node_tree.nodes['Principled BSDF'];p.inputs['Metallic'].default_value=.05;p.inputs['Roughness'].default_value=.7

 a.area_collection('LivingDining_Details','data/cube-map/8_b.jpg; source appliance top grille and controls')
 appliance=bpy.data.objects['LIV.CylindricalAppliance'];a.parent=appliance
 dark=bpy.data.materials['Charcoal equipment']
 for j in range(64):
  t=j*2*math.pi/64
  a.rod(f'LIV.CylindricalAppliance.TopGrille.{j}',(-.77+.059*math.cos(t),7.18+.059*math.sin(t),.606),(-.77+.151*math.cos(t),7.18+.151*math.sin(t),.606),.0024,dark,6)
 a.cyl('LIV.CylindricalAppliance.TopDial',(-.77,7.18,.619),.043,.018,dark,40)
 a.curve('LIV.CylindricalAppliance.DialRing',[(-.77+.036*math.cos(j*2*math.pi/64),7.18+.036*math.sin(j*2*math.pi/64),.629) for j in range(64)],.0013,bpy.data.materials['Appliance white'],True)
 a.box('LIV.CylindricalAppliance.BaseDisplay',(-.77,7.021,.10),(.14,.014,.035),dark,.012)
 a.box('LIV.CylindricalAppliance.StatusWindow',(-.84,7.017,.135),(.014,.013,.026),dark,.004)
 a.parent=None
