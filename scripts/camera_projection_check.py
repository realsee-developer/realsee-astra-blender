from pathlib import Path
import json, math
import numpy as np
from PIL import Image
import pye57
ROOT=Path.cwd().resolve();Image.MAX_IMAGE_PIXELS=None
r=pye57.E57(str(ROOT/'data/point-cloud.e57'))
rows=json.loads((ROOT/'research/camera-registration.json').read_text())
for row in rows['stations']:
 i=row['embedded_index'];d=r.read_scan_raw(i-1,ignore_unsupported_fields=True)
 p=np.column_stack([d['cartesian'+a] for a in 'XYZ']);c=np.column_stack([d['color'+a] for a in ['Red','Green','Blue']]).astype(float)
 im=Image.open(ROOT/f'data/panorama/{i}.jpg');im.draft('RGB',(2048,1024));im=im.resize((2048,1024));img=np.asarray(im,dtype=float)
 theta=np.arctan2(p[:,0],p[:,2]);v=np.arccos(-p[:,1]/np.linalg.norm(p,axis=1))/np.pi
 sample=np.arange(0,len(p),10); vv=np.clip((v[sample]*1024).astype(int),0,1023)
 tests=[]
 for sign in [-1,1]:
  for offset in np.arange(0,1,1/180):
   uu=((sign*theta[sample]/(2*np.pi)+offset)%1*2048).astype(int)
   err=np.mean(abs(c[sample]-img[vv,uu]));tests.append((float(err),sign,float(offset)))
 best=min(tests);base=best[2]
 for offset in np.arange(base-1/180,base+1/180,1/4096):
  uu=((best[1]*theta[sample]/(2*np.pi)+offset)%1*2048).astype(int);err=np.mean(abs(c[sample]-img[vv,uu])); tests.append((float(err),best[1],float(offset)))
 best=min(tests);row['panorama_projection']={'color_MAE_255':best[0], 'theta_sign':best[1], 'u_offset':best[2], 'formula':'u=(theta_sign*atan2(local_x,local_z)/(2*pi)+u_offset)%1; v=acos(-local_y/r)/pi; local ray=[sin(theta)*sin(pi*v),-cos(pi*v),cos(theta)*sin(pi*v)]; world ray=E57 quaternion @ local ray'}
 print(i,best,flush=True)
rows['status']='E57 GUID association, external JPG match and local ray projection verified against colored E57 points'
(ROOT/'research/camera-registration.json').write_text(json.dumps(rows,indent=2))
