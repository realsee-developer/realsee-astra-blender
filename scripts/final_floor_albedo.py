"""Source-comparison albedo estimates, keeping every floor material independently editable."""
import bpy
TONES={'LivingDining':(.58,.52,.42,1),'Corridor':(.45,.54,.61,1),'Game':(.45,.54,.61,1),'Photography':(.70,.70,.66,1),'Bar':(.42,.36,.28,1)}

def apply_floor_albedo(ROOT):
 for area,color in TONES.items():
  m=bpy.data.materials['FloorSurface_'+area];nt=m.node_tree
  if area=='LivingDining':tone=next(n for n in nt.nodes if n.type=='MIX_RGB')
  else:
   tone=nt.nodes.new('ShaderNodeMixRGB');tone.blend_type='MULTIPLY';tone.inputs[0].default_value=1
   tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');nt.links.new(tex.outputs['Color'],tone.inputs[1]);nt.links.new(tone.outputs[0],nt.nodes['Principled BSDF'].inputs['Base Color'])
  tone.inputs[2].default_value=color;tone.label='Estimated albedo correction from registered floor comparison'
  m['albedo_correction_status']='inferred from registered source-floor appearance; reduces residual captured illumination, not a measured spectral albedo'
 return TONES
