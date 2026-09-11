"""Intersect manually identified source-fixture pixels with measured ceiling planes.
Run from PROJECT_ROOT using .venv-analysis/bin/python.
Pixels refer to 1200x1200 downsampled source cube faces, never generated images.
"""
from pathlib import Path
import json
import numpy as np
from scipy.spatial.transform import Rotation
from PIL import Image

ROOT=Path.cwd();assert (ROOT/'data').is_dir()
pose=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'][7]
offset=json.loads((ROOT/'research/registration-cad.json').read_text())['ply_to_scene_matrix'][2][3]
w,x,y,z=pose['quaternion_wxyz'];rotation=Rotation.from_quat([x,y,z,w]).as_matrix()
origin=np.array(pose['translation_xyz_m']);origin[2]+=offset
def intersect(face,pixel,axis=2,value=2.468):
 basis=pose['cube_faces'][face]
 direction=rotation@(np.array(basis['canonical_local_center'])+np.array(basis['canonical_local_right'])*(pixel[0]/600-1)+np.array(basis['canonical_local_down'])*(pixel[1]/600-1))
 return origin+direction*(value-origin[axis])/direction[axis]

selections={'f':[(345.7,210.4),(486,372.9),(544,443),(644,475),(750,473),(854,469),(1017,423.9),(1179,334.6)],'r':[(949.9,242),(572,274.5),(251,301.6)],'b':[(787.9,177.3),(491.6,207.5),(230.1,230.5)],'u':[(42,235),(124,875)]}
spots=[]
for face,pixels in selections.items():
 for pixel in pixels:
  point=intersect(face,pixel)
  side='west' if point[0]<-7 else ('east' if point[0]>-1 else ('south' if point[1]<7 else 'north'))
  spots.append({'source':f'data/cube-map/8_{face}.jpg','pixel_at_1200':list(pixel),'scene_center_m':point.tolist(),'ceiling_plane_z_m':2.468,'side':side})

im=np.array(Image.open(ROOT/'data/cube-map/8_f.jpg').convert('RGB').resize((1200,1200)))
yy,xx=np.mgrid[:1200,:1200]
mask=(xx>600)&(xx<1020)&(yy>120)&(yy<420)&(im.min(axis=2)>205)&(im[:,:,2]>=im[:,:,0]*.995)
pixels=np.column_stack([xx[mask],yy[mask]])
points=np.array([intersect('f',p,2,2.740) for p in pixels]);lo=points.min(axis=0);hi=points.max(axis=0)
round_center=intersect('u',(775,230),2,2.754)
round_edges=[intersect('u',p,2,2.754) for p in [(664,230),(886,230),(775,119),(775,343)]]
result={'method':'Manually verified fixture centers in actual source cube faces; exact content-verified E57 basis; ray intersection with CAD-supported ceiling Z or observed cove-face X. Optical bloom introduces several-millimeter center and edge uncertainty; no global illumination accuracy claim.','pixel_reference_size':[1200,1200],'perimeter_downlights':spots,'perimeter_downlight_count':len(spots),'layered_fixture':{'source':'data/cube-map/8_f.jpg','mask':'ROI x600..1020,y120..420, minimum RGB>205 and B>=0.995R at1200 square','ceiling_z_m':2.740,'bright_pixel_bounds_m':[lo.tolist(),hi.tolist()],'bright_pixel_center_m':((lo+hi)/2).tolist(),'bright_pixel_extent_m':(hi-lo).tolist(),'native_outer_extent_m':[1.30,.77],'native_bloom_allowance':'Bright pixels include halo; physical outer tubing is slightly inset.'},'round_fixture':{'source':'data/cube-map/8_u.jpg','pixel_at_1200':[775,230],'scene_center_m':round_center.tolist(),'diameter_m':float(np.mean([np.linalg.norm(round_edges[1]-round_edges[0]),np.linalg.norm(round_edges[3]-round_edges[2])]))},'smoke_sensor':{'source':'data/cube-map/8_u.jpg','pixel_at_1200':[895,1033],'scene_center_m':intersect('u',(895,1033),2,2.767).tolist()},'vents':[{'name':'Living_west','source':'data/cube-map/8_f.jpg','pixel_at_1200':[750,448],'scene_center_m':intersect('f',(750,448),0,-7.23).tolist(),'width_m':1.02,'height_m':.13,'normal_scene':[1,0,0]},{'name':'Living_east','source':'data/cube-map/8_b.jpg','pixel_at_1200':[488,102],'scene_center_m':intersect('b',(488,102),0,-.84).tolist(),'width_m':.92,'height_m':.13,'normal_scene':[-1,0,0]}]}
(ROOT/'research/cad-fixture-measurements.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['perimeter_downlights']},indent=2))
