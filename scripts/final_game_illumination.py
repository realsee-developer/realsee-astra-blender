"""Match the observed warm cove and purple strip illumination without adding fixtures."""
import bpy

def apply_game_illumination(ROOT):
 for o in bpy.data.objects:
  if o.type=='LIGHT' and o.name.startswith('COVE_BOUNCE_Game'):
   o.data.energy=80*max(o.data.size,o.data.size_y);o.data.color=(1,.68,.25);o['evidence_status']='inferred cove radiant power from source6_u appearance, within the observed LED cove'
  if o.type=='LIGHT' and o.name.startswith('LIGHT_FILL_Game'):
   o.data.energy=85;o.data.color=(.47,.16,1);o['evidence_status']='inferred indirect violet illumination from photographed wall LED strips'
 p=bpy.data.materials['Lilac LED'].node_tree.nodes['Principled BSDF'];p.inputs['Emission Strength'].default_value=12
