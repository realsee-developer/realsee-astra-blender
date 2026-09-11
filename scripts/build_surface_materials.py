from pathlib import Path
import bpy

def build_surface_materials(ROOT):
 for area,sample,size,roughness in [('LivingDining','living-parquet',1.16,.44),('Corridor','corridor-stone',.66,.46),('Game','corridor-stone',.66,.46),('Photography','fashion-stone',1.0,.45),('Bar','bar-wood-clean',.28,.47)]:
  m=bpy.data.materials.new('FloorSurface_'+area);m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=roughness
  coord=nt.nodes.new('ShaderNodeTexCoord');mult=nt.nodes.new('ShaderNodeVectorMath');mult.operation='MULTIPLY';mult.inputs[1].default_value=(1/size,-1/size,1/size);nt.links.new(coord.outputs['Object'],mult.inputs[0])
  tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(Path(ROOT)/f'output/assets/{sample}.png'),check_existing=True);tex.extension='REPEAT';tex.interpolation='Linear';nt.links.new(mult.outputs[0],tex.inputs['Vector']);
  from final_floor_albedo import TONES
  tone=nt.nodes.new('ShaderNodeMixRGB');tone.blend_type='MULTIPLY';tone.inputs[0].default_value=1;tone.inputs[2].default_value=TONES[area];nt.links.new(tex.outputs['Color'],tone.inputs[1]);nt.links.new(tone.outputs[0],p.inputs['Base Color']);tone.label='Estimated albedo correction from registered floor comparison'

  bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.09;bump.inputs['Distance'].default_value=.0015;nt.links.new(tex.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
  obj=bpy.data.objects['FLOOR_'+area];obj.data.materials.clear();obj.data.materials.append(m);m['source']='unobstructed sample from registered source panorama; physical planar rectification; low-frequency illumination normalized';m['editable_texture_scale_m']=size
