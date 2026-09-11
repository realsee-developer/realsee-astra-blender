"""Observed bar entry returns and metal jambs, omitted by the source CAD trace.
Call at the end of the scene build after apply_structural_fixtures. Never saves.
"""
from pathlib import Path
import json
import bpy

def apply_bar_entry(ROOT,a):
 ROOT=Path(ROOT);a.area_collection('Bar_Entry_Structure','data/cube-map/4_b.jpg;4_l.jpg; data/point-cloud.ply')
 gray=bpy.data.materials['ARCH charcoal corridor paint'];black=bpy.data.materials['ARCH matte black metal'];changed=[]
 def box(name,center,size,material,source):
  ob=a.box(name,center,size,material,.002);ob['area']='Bar';ob['category']='Walls' if name.startswith('WALL_') else 'Openings';ob['source']=source;ob['evidence_status']='observed source-registered surfaces; concealed joins and metal section inferred';changed.append(ob.name);return ob
 box('WALL_Bar_observed_south_entry_return',(-.4825,.945,1.406),(.125,.390,2.812),gray,'PLY parallel gray faces X−0.54/−0.425, Y0.77..1.14; source4_b photographed return')
 box('WALL_Bar_entry_south_return_connection',(-.467,.709,1.406),(.156,.143,2.812),gray,'Short concealed connection between PLY return and CAD south wall; inferred join')
 for side,face,center,flange_center in [('south',1.193,1.168,1.147),('north',2.562,2.587,2.619)]:
  box(f'FRAME_Bar_{side}_jamb_body',(-.478,center,1.406),(.172,.050,2.812),black,f'source4_{"b" if side=="south" else "l"}; PLY measured opening-facing plane Y{face}m')
  box(f'FRAME_Bar_{side}_outer_flange',(-.398,flange_center,1.406),(.016,.092,2.812),black,'Source thin black return flange on the bar-facing side; observed profile with inferred section')
  box(f'FRAME_Bar_{side}_edge_bead',(-.409,flange_center,1.406),(.004,.092,2.812),black,'Source visible narrow raised vertical metal bead')
 beam=bpy.data.objects['BEAM_Bar_entrance'];beam.location=(-.478,1.893,2.780);beam.dimensions=(.172,1.47,.110);beam['source']='Source4_b/4_l entry frame; connects PLY-supported south/north jambs atY1.193 and2.562';changed.append(beam.name)
 report={'changes':changed,'sources':['data/cube-map/4_b.jpg','data/cube-map/4_l.jpg','data/point-cloud.ply'],'south_return':{'native_bounds_xy_m':[[-.545,.750],[-.420,1.140]],'observed_gray_face_x_m':[-.54,-.425]},'south_jamb_opening_face_y_m':1.193,'north_jamb_opening_face_y_m':2.562,'clear_opening_between_jambs_m':1.369,'metal_jamb_x_bounds_m':[-.564,-.390],'height_m':2.812,'source_measurements':{'south_face':{'selection':'−.60<X<−.38,1.14<Y<1.23,0.5<sceneZ<2.4,abs(normalY)>0.98','count':1133,'median_y_m':1.18973291,'y_05_95_m':[1.17599497,1.20122612]},'north_dark':{'selection':'−.70<X<−.25,2.4<Y<2.7,0.5<sceneZ<2.4,max(RGB)<90','count':2831,'median_y_m':2.58799076,'y_05_95_m':[2.56653404,2.64935362]},'inspection_plot':'research/cad-bar-post-plan.png'},'CAD_conflict':'The short south return and visible metal jambs are absent in the simplified CAD trace; actual PLY and photographs take precedence. This adds no room. The existing continuous floor top area remains unchanged, with a small portion now covered by the observed return; modeled floor-surface area must not be described as net walkable area.'}
 (ROOT/'research/cad-bar-entry-correction.json').write_text(json.dumps(report,indent=2));bpy.context.view_layer.update();return report
