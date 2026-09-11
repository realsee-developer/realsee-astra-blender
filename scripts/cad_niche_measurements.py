"""Document the source-supported wider living bay and the conflicting CAD recess."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from cad_analysis import read_ply

ROOT=Path.cwd();assert (ROOT/'data').is_dir()
points,normals,colors=read_ply();registration=json.loads((ROOT/'research/registration-cad.json').read_text());points[:,2]+=registration['ply_to_scene_matrix'][2][3]
mask=(points[:,0]<-7.20)&(points[:,0]>-9.4)&(points[:,1]>6.5)&(points[:,1]<8.6)&(points[:,2]>.15)&(points[:,2]<2.30)
p=points[mask];rgb=colors[mask]/255
fig,axes=plt.subplots(1,3,figsize=(18,7))
for ax,(a,b) in zip(axes,[(0,1),(0,2),(1,2)]):
 ax.scatter(p[::2,a],p[::2,b],c=rgb[::2],s=1);ax.set_aspect('equal');ax.grid();ax.set_xlabel('XYZ'[a]);ax.set_ylabel('XYZ'[b])
fig.savefig(ROOT/'research/cad-living-niche-ply.png',dpi=150);plt.close(fig)
bins=[]
for xmin,xmax in [(-9.2,-8.6),(-8.6,-8.0),(-8.0,-7.7),(-7.7,-7.5),(-7.5,-7.2)]:
 selected=p[(p[:,0]>=xmin)&(p[:,0]<xmax)]
 bins.append({'x_range_m':[xmin,xmax],'count':len(selected),'y_quantiles_01_50_99_m':np.quantile(selected[:,1],[.01,.5,.99]).tolist(),'z_quantiles_01_50_99_m':np.quantile(selected[:,2],[.01,.5,.99]).tolist()})
report={'source':'data/point-cloud.ply','spatial_gate_scene_m':{'x':[-9.4,-7.2],'y':[6.5,8.6],'z':[.15,2.30]},'selected_points':len(p),'depth_bins':bins,'CAD_recess_width_m':.416,'CAD_recess_depth_m':1.462,'observed_front_aperture':{'source':'data/cube-map/8_f.jpg; exact E57 camera rays measured independently by visual inventory','x_m':-7.55,'y_range_m':[6.86,8.02],'z_range_m':[0,2.342]},'modeled_back_lower':{'x_m':-9.02,'y_range_m':[6.91,8.20],'z_range_m':[0,1.60]},'modeled_back_upper':{'x_m':-8.72,'y_range_m':[6.91,8.20],'z_range_m':[1.60,2.486]},'interpretation':'Actual PLY return bands and photographed glazing demonstrate a wider bay than the narrow CAD trace. Native back distances follow observed points. Side wall connections through occlusion, wall thickness, ceiling closure and step connection are inferred and labeled. The separate flat landscape graphic is modeled as a printed board; no terrain is reconstructed from the picture.','floor_area_policy':'Measure actual saved floor top triangles, report the difference from87.25 m² CAD, and do not force geometry to preserve the prior CAD area.'}
(ROOT/'research/cad-observed-living-niche.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
