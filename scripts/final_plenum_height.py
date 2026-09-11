"""Bounded native ceiling-plenum correction from measured PLY upper returns."""
from pathlib import Path
import json
import bpy,numpy as np

def apply_plenum_height(ROOT):
 ROOT=Path(ROOT);sample=np.load(ROOT/'research/cad-ply-sample.npz');points=sample['points'];normals=sample['normals'];registration=json.loads((ROOT/'research/registration-cad.json').read_text());z=points[:,2]+registration['ply_to_scene_matrix'][2][3];areas=json.loads((ROOT/'research/cad-areas.json').read_text());results=[]
 for area,target,grid,cad_height in [('Bar',3.021,2.780,2.812),('Corridor',3.042,2.800,3.021)]:
  polygon=next(a for a in areas if a['name']==area)['polygon_scene_m'];inside=np.zeros(len(points),dtype=bool)
  for a,b in zip(polygon,polygon[1:]+polygon[:1]):
   if a[1]==b[1]:continue
   crossing=((a[1]>points[:,1])!=(b[1]>points[:,1]))&(points[:,0]<(b[0]-a[0])*(points[:,1]-a[1])/(b[1]-a[1])+a[0]);inside^=crossing
  selected=z[inside&(abs(normals[:,2])>.985)&(z>2.97)&(z<3.10)]
  assert len(selected)>50,'Insufficient source evidence for plenum plane '+area
  ob=bpy.data.objects['CEILING_'+area+'_dark_plenum'];before=min((ob.matrix_world@v.co).z for v in ob.data.vertices);ob.location.z+=target-before;ob['source']='data/point-cloud.ply upper horizontal return band; research/cad-plenum-height-evidence.json';ob['evidence_status']='measured underside level; inferred continuous completion across sparse upper returns';ob['underside_elevation_m']=target;ob['grid_underside_elevation_m']=grid;ob['CAD_CH_annotation_m']=cad_height
  results.append({'area':area,'object':ob.name,'source_samples':len(selected),'source_quantiles_05_50_95_m':np.quantile(selected,[.05,.5,.95]).tolist(),'native_underside_after_m':target,'physical_grid_underside_m':grid,'CAD_CH_annotation_m':cad_height,'native_upper_plane_minus_CAD_CH_m':target-cad_height,'CAD_relation':'CAD height annotation is retained separately. In Bar it approximates the suspended grid level; in Corridor it is about21 mm below the upper observed band. Point-cloud evidence distinguishes the lower open grid from the higher physical backing.'})
 report={'source':'data/point-cloud.ply','cached_sample':'research/cad-ply-sample.npz','sampling':'Every fifth original PLY record, source scan coordinate frame plus documented Z datum. XY inside the CAD room polygon; abs(source normal z)>0.985; scene2.97<Z<3.10 m. Quantiles and counts recomputed when this function runs.','grid_unchanged':True,'scope':'Only translate the two named native black plenum slabs vertically; no walls, room polygons, floors, fixtures, materials or original scan are changed.','results':results}
 (ROOT/'research/cad-plenum-height-evidence.json').write_text(json.dumps(report,indent=2));return report
