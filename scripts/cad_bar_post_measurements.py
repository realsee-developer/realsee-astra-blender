from pathlib import Path
import sys,json,numpy as np
from scipy.spatial.transform import Rotation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts'))
from cad_analysis import read_ply
p,n,c=read_ply();off=json.loads((ROOT/'research/registration-cad.json').read_text())['ply_to_scene_matrix'][2][3];p[:,2]+=off
pose=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'][3];w,x,y,z=pose['quaternion_wxyz'];rot=Rotation.from_quat([x,y,z,w]).as_matrix();o=np.array(pose['translation_xyz_m']);o[2]+=off;b=pose['cube_faces']['b']
local=(p-o)@rot;dep=local@np.array(b['canonical_local_center']);u=800*(1+(local@np.array(b['canonical_local_right']))/dep);v=800*(1+(local@np.array(b['canonical_local_down']))/dep)
mask=(dep>0)&(u>845)&(u<953)&(v>80)&(v<1480)&(p[:,0]>-1)&(p[:,0]<.2)&(p[:,1]>.5)&(p[:,1]<1.3)
sel=p[mask];rgb=c[mask];ns=n[mask];print('post',len(sel),np.quantile(sel,[.01,.05,.5,.95,.99],axis=0));print('normals',np.quantile(ns,[.01,.5,.99],axis=0))
for axis in [0,1]:
 hist,edges=np.histogram(sel[:,axis],bins=np.arange(-1,1.35,.01));print('hist',axis,[(round(edges[i],3),int(hist[i])) for i in np.argsort(hist)[-18:][::-1]])
fig,axs=plt.subplots(1,3,figsize=(15,7))
for ax,(a,baxis) in zip(axs,[(0,1),(0,2),(1,2)]):
 ax.scatter(sel[:,a],sel[:,baxis],c=rgb/255,s=4);ax.set_aspect('equal');ax.grid();ax.set_xlabel('XYZ'[a]);ax.set_ylabel('XYZ'[baxis])
fig.savefig(ROOT/'research/cad-bar-post-ply.png',dpi=150)
np.savez(ROOT/'research/cad-bar-post-ply.npz',points=sel,normals=ns,colors=rgb,pixels=np.column_stack([u[mask],v[mask]]))
for px in [849,875,889,944,950]:
 d=rot@(np.array(b['canonical_local_center'])+np.array(b['canonical_local_right'])*(px/800-1));print('rayx-.65',px,o+d*(-.65-o[0])/d[0])
