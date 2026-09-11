"""Run by Blender after opening actual saved scene to measure structure."""
import bpy,json,math,hashlib,sys,argparse,statistics
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--output',default='research/cad-structural-measurements.json');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
reg=json.loads((ROOT/'research/registration-cad.json').read_text());a=reg['cad_to_ply_xy_rotation_radians'];c,s=math.cos(a),math.sin(a);tx,ty=reg['cad_to_ply_xy_translation_m']
def verts(o):return [o.matrix_world@v.co for v in o.data.vertices]
def visible_native(o):return not o.get('native_coverage_excluded') and not o.hide_render and not any(c.hide_render for c in o.users_collection)
def cadxy(p):return ((c*(p.x-tx)+s*(p.y-ty)),(-s*(p.x-tx)+c*(p.y-ty)))
checks=[]
def add(name,ref,actual,source):checks.append({'name':name,'reference_m':ref,'model_m':actual,'difference_mm':(actual-ref)*1000,'source':source,'pass_10mm':abs(actual-ref)<=.01})
p=verts(bpy.data.objects['FLOOR_Photography']);q=verts(bpy.data.objects['FLOOR_Corridor']);l=verts(bpy.data.objects['FLOOR_LivingDining']);
add('Net east-west width',13.203,max(cadxy(v)[0] for v in q)-min(cadxy(v)[0] for v in p),'CAD text392 13203mm lower total dimension')
add('Net north-south depth',9.730,max(cadxy(v)[1] for v in l)-min(cadxy(v)[1] for v in p),'CAD text3C2 9730mm left total dimension')
for name,ref in [('Photography',2.774),('Game_center',2.786),('LivingDining_center',2.792)]:
 o=bpy.data.objects['CEILING_'+name];add('Ceiling '+name,ref,min(v.z for v in verts(o)),'CAD location-specific CH')
# DW/DH are compared with the actual timber leaf. The Living width has a
# separately evidenced CAD/photo conflict, retained below. The
# projecting casing is larger; the earlier checks incorrectly equated trim
# outside dimensions with door dimensions and therefore certified short leaves.
for name,ref in [('Game',2.171),('LivingDining',2.166)]:
 o=bpy.data.objects['DOOR_'+name+'_hinged_leaf'];add('Door leaf top above floor '+name,ref,max(v.z for v in verts(o)),'CAD DH; original PLY leaf upper edge, research/realism-opening-dimension-definitions.md')
for name,ref in [('Game',.911),('LivingDining',.901)]:
 o=bpy.data.objects['DOOR_'+name+'_hinged_leaf']
 components=[o]
 if name=='Game':components.append(bpy.data.objects['DOOR_Game_hinged_leaf.SourceTerminalStrip'])
 width_axis=(o.matrix_world.to_3x3()@Vector((1,0,0))).normalized()
 projected=[width_axis.dot(v)for component in components for v in verts(component)]
 add('Door leaf width '+name,ref,max(projected)-min(projected),'CAD nominal DW compared with actual complete saved timber leaf; definition and adopted source construction recorded below')
 checks[-1]['measured_components']=[component.name for component in components]
 checks[-1]['measurement_method']='Union of actual world-space timber component vertices projected along the leaf width axis; hardware and trim excluded.'
# Preserve the failed CAD width comparison. The photo/PLY terminal correction
# has an independent recorded source construction and is not a new CAD value.
leaf=bpy.data.objects['DOOR_LivingDining_hinged_leaf']
assert 'source_terminal_extension_m' in leaf,'This current check requires the source-corrected Living leaf.'
source_path=ROOT/'output/realism/corridor-followups/leaf-terminal-occlusion-diagnosis.json'
source_terminal=json.loads(source_path.read_text())
assert len(source_terminal['terminal_extension_m_per_sample'])==len(source_terminal['registered_source_8_l_edge_samples_1000'])==5
extension=statistics.median(source_terminal['terminal_extension_m_per_sample'])
assert abs(extension-source_terminal['median_terminal_extension_m'])<1e-9
chosen_width=source_terminal['old_width_m']+extension
assert abs(chosen_width-source_terminal['derived_width_m'])<1e-9
conflict=next(row for row in checks if row['name']=='Door leaf width LivingDining')
conflict.update(source_conflict=True,chosen_source_reference_m=chosen_width,
 chosen_source_difference_mm=(conflict['model_m']-chosen_width)*1000,
 chosen_source_pass_10mm=abs(conflict['model_m']-chosen_width)<=.01,
 source_record=str(source_path.relative_to(ROOT)),source_record_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
 conflict_explanation='CAD DW901 is retained unchanged. Five registered8_l terminal-edge rays and98 original timber returns support an additional17.186mm hinge-end extent while preserving the broad front plane and free edge. Adopted source width is a fitted interpretation, not independent holdout metrology; traced points span12.514–20.477mm extension. This does not meet the10mm CAD target and is reported as a source conflict.')
game_path=ROOT/'output/realism/bar-game-final-source-finish/door-frame-vertical-edge-alignment.json'
game_source=json.loads(game_path.read_text())
assert set(game_source['leaf_component_names'])=={'DOOR_Game_hinged_leaf','DOOR_Game_hinged_leaf.SourceTerminalStrip'}
game_width=game_source['old_native_leaf_width_m']+game_source['source_terminal_extension_m']
assert abs(game_width-game_source['adopted_complete_leaf_width_m'])<1e-9
game=next(row for row in checks if row['name']=='Door leaf width Game')
game.update(source_conflict=True,comparison_class='CAD-to-physical-component definition uncertain',
 chosen_source_reference_m=game_width,chosen_source_difference_mm=(game['model_m']-game_width)*1000,
 chosen_source_pass_10mm=abs(game['model_m']-game_width)<=.01,
 source_record=str(game_path.relative_to(ROOT)),source_record_sha256=hashlib.sha256(game_path.read_bytes()).hexdigest(),
 independent_definition_audit='output/realism/review-v18/game-door-CAD-source-audit.json',
 historical_primary_mesh_width_m=max(v.co.x for v in bpy.data.objects['DOOR_Game_hinged_leaf'].data.vertices)-min(v.co.x for v in bpy.data.objects['DOOR_Game_hinged_leaf'].data.vertices),
 conflict_explanation='CAD DW911 and its911x124mm plan rectangle between wall stops remain unchanged. No separate42mm timber leaf or hinge axis is drawn. Earlier2718-point PLY face fit excludedX>-3.57m and therefore did not measure the complete hinge terminal; the earlier independent911mm leaf-width claim is withdrawn. The full saved leaf includes the source terminal strip. Adopted width retains the old free edge and fits the terminal corner to registered6_l/7_b rays. It is a source-constrained construction with uncertain CAD component correspondence, not an independently surveyed19.87mm CAD error. The historical main-mesh-only measurement is retained separately.')
source_exceptions=[conflict,game]
o=bpy.data.objects['FRAME_Photography_L'];vs=verts(o);add('Photography opening frame height',2.714,max(v.z for v in vs)-min(v.z for v in vs),'CAD DH; broad photographed opening without visible leaf')
o=bpy.data.objects['FRAME_Photography_head'];add('Photography opening frame width',1.377,max(v.co.x for v in o.data.vertices)-min(v.co.x for v in o.data.vertices),'CAD DW; broad photographed opening without visible leaf')
# Measure actual saved top faces, including applied column cut and source-corrected bay.
floor_areas={}
for ob in bpy.data.objects:
 if ob.type!='MESH' or not visible_native(ob) or not ob.name.startswith(('FLOOR_','THRESHOLD_')):continue
 total=0;ob.data.calc_loop_triangles()
 for triangle in ob.data.loop_triangles:
  if ob.data.polygons[triangle.polygon_index].normal.z<.9:continue
  points=[ob.matrix_world@ob.data.vertices[i].co for i in triangle.vertices]
  total+=(points[1]-points[0]).cross(points[2]-points[0]).length/2
 floor_areas[ob.name]=total
area=sum(floor_areas.values())
height_rows=[]
def height_row(name,objects,cad_handle,cad_label,cad_m,source_reference,status):
 lows=[min(v.z for v in verts(ob)) for ob in objects];highs=[max(v.z for v in verts(ob)) for ob in objects];actual=min(lows)
 height_rows.append({'name':name,'objects':[ob.name for ob in objects],'native_underside_m':actual,'native_underside_range_m':[min(lows),max(lows)],'native_top_range_m':[min(highs),max(highs)],'CAD_text_handle':cad_handle,'CAD_exact_label':cad_label,'CAD_annotation_m':cad_m,'native_minus_CAD_mm':(actual-cad_m)*1000,'source_reference_m':source_reference,'native_minus_source_reference_mm':(actual-source_reference)*1000,'source_agreement_within_10mm':abs(actual-source_reference)<=.01,'status':status})
for room,height,handle in [('Game',2.470,'5D5'),('LivingDining',2.486,'5D2')]:
 height_row(room+' cove underside',[bpy.data.objects[f'COVE_{room}_{side}'] for side in ['south','north','west','east']],handle,f'CH: {round(height*1000)}mm',height,height,'Native cove underside agrees with the local CAD low-ceiling annotation; main ceiling is checked separately.')
height_row('Bar physical open-grid underside',[ob for ob in bpy.data.objects if visible_native(ob) and ob.name.startswith('GRID_Bar_')],'5D7','CH: 2812mm',2.812,2.780444,'Native grid follows the measured PLY lower grid plane. CAD2812 is32 mm above this lower edge and is retained as a local source discrepancy; it is distinct from the higher plenum backing.')
height_row('Bar upper physical backing',[bpy.data.objects['CEILING_Bar_dark_plenum']],'5D7','CH: 2812mm',2.812,3.021450,'Higher physical backing is independently observed in sparse upper PLY returns; CAD2812 belongs to the lower suspended-ceiling zone. Continuous hidden closure is inferred.')
height_row('Corridor physical open-grid underside',[ob for ob in bpy.data.objects if visible_native(ob) and ob.name.startswith('GRID_Corridor_')],'5D9','CH: 2812mm',2.812,2.795542,'CAD5D9 labels the long corridor suspended-ceiling zone. Native grid follows the observed lower plane,12 mm below that label. CAD5D4 separately labels a3021 mm upper level near the vertical hall.')
height_row('Corridor upper physical backing',[bpy.data.objects['CEILING_Corridor_dark_plenum']],'5D4','CH: 3021mm',3.021,3.041899,'Native backing follows the upper PLY band,21 mm above CAD5D4. Both values and their distinct source meanings are retained; no plane was moved to conceal the difference.')
result={'loaded_blend':Path(bpy.data.filepath).name,'opened_file_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'factory_startup':'--factory-startup' in sys.argv,'linear_checks':checks,'all_linear_checks_pass':all(c['pass_10mm'] for c in checks),'all_nonconflicting_CAD_linear_checks_pass':all(row['pass_10mm'] for row in checks if not row.get('source_conflict',False)),'source_conflicts':source_exceptions,'all_chosen_source_conflicts_pass':all(row['chosen_source_pass_10mm']for row in source_exceptions),'supplementary_ceiling_height_checks':height_rows,'all_supplementary_heights_match_chosen_source_within_10mm':all(c['source_agreement_within_10mm'] for c in height_rows),'CAD_total_area_m2':87.25,'native_floor_area_m2':area,'actual_saved_top_face_areas_m2':floor_areas,'area_difference_m2':area-87.25,'area_difference_explanation':'Photographed and PLY-supported broader living bay replaces the under-traced0.416 m CAD recess. Native measured surfaces take precedence; CAD area is retained as an explicit discrepancy.','pointcloud_registration_report':'research/registration-cad.json','ceiling_source_reports':['research/cad-area-surface-statistics.json','research/cad-plenum-height-evidence.json']}
(ROOT/args.output).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert result['all_nonconflicting_CAD_linear_checks_pass'],'A nonconflicting CAD linear target failed; inspect the saved measurement report.'
assert result['all_chosen_source_conflicts_pass'],'A source-conflict model differs from its recorded chosen source interpretation.'
assert result['all_supplementary_heights_match_chosen_source_within_10mm'],'An actual native ceiling height differs from its chosen source plane.'
