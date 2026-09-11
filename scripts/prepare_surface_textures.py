"""Rectify clean, unobstructed source floor samples; remove low frequency captured lighting."""
from pathlib import Path
import json,numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter
from scipy.spatial.transform import Rotation
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];Image.MAX_IMAGE_PIXELS=None
stations=json.loads((ROOT/'research/camera-registration.json').read_text())['stations'];off=json.loads((ROOT/'research/registration-cad.json').read_text())['ply_to_scene_matrix'][2][3]
specs=[('living-parquet',8,(-5.40,7.26),1.16),('corridor-stone',2,(-2.07,1.64),.66),('fashion-stone',3,(-6.28,1.28),1.0),('bar-wood',4,(.35,1.2),.50)]
for name,station,center,size in specs:
 s=stations[station-1];q=s['quaternion_wxyz'];rot=Rotation.from_quat(q[1:]+q[:1]);pos=np.array(s['translation_xyz_m']);pos[2]+=off
 with Image.open(ROOT/f'data/panorama/{station}.jpg') as im:
  rgb=np.asarray(im)
 N=1024;xx,yy=np.meshgrid(center[0]+(np.arange(N)/N-.5)*size,center[1]-(np.arange(N)/N-.5)*size)
 ray=np.stack([xx-pos[0],yy-pos[1],np.full_like(xx,-pos[2])],axis=-1);local=rot.inv().apply(ray.reshape(-1,3)).reshape(N,N,3);local/=np.linalg.norm(local,axis=-1)[...,None]
 u=(np.arctan2(local[...,0],local[...,2])/(2*np.pi)+.5)%1;v=np.arccos(-local[...,1])/np.pi
 out=np.stack([map_coordinates(rgb[...,i],[v*(rgb.shape[0]-1),u*(rgb.shape[1]-1)],order=1,mode='wrap') for i in range(3)],axis=-1)
 out=out.astype(np.float32)/255
 illum=gaussian_filter(out.mean(-1),65);out=out/np.maximum(illum[...,None],.03)*float(np.mean(illum));out=np.clip(out,0,1)
 Image.fromarray((out*255).astype('uint8')).save(ROOT/f'output/assets/{name}.png')
print('Rectified four unobstructed floor samples; physical sample dimensions recorded in script.')
