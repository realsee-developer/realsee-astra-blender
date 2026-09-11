from pathlib import Path
import json
import numpy as np
from PIL import Image
ROOT=Path.cwd().resolve();Image.MAX_IMAGE_PIXELS=None
n=192;q=(np.arange(n)+.5)/n*2-1;xx,yy=np.meshgrid(q,q);one=np.ones_like(xx)
bases={'f':([0,0,1],[1,0,0],[0,1,0]),'r':([1,0,0],[0,0,-1],[0,1,0]),'b':([0,0,-1],[-1,0,0],[0,1,0]),'l':([-1,0,0],[0,0,1],[0,1,0]),'u':([0,-1,0],[1,0,0],[0,0,1]),'d':([0,1,0],[1,0,0],[0,0,-1])}
rows=json.loads((ROOT/'research/camera-registration.json').read_text());rawrows=[]
# Compare station identity across all panorama thumbnails; preserve numerical evidence.
external=[];embedded=[]
for i in range(1,9):
 im=Image.open(ROOT/f'data/panorama/{i}.jpg');im.draft('RGB',(1024,512));external.append(np.asarray(im.resize((1024,512)),dtype=float))
 embedded.append(np.asarray(Image.open(ROOT/f'research/e57-previews/embedded-{i}.jpg').resize((1024,512)),dtype=float))
for i,row in enumerate(rows['stations'],1):
 a=embedded[i-1];matches=[]
 for j,b in enumerate(external,1):
  cor=np.fft.irfft(np.fft.rfft(a,axis=1)*np.conj(np.fft.rfft(b,axis=1)),n=1024,axis=1).sum((0,2));shift=int(cor.argmax());mae=float(np.mean(abs(a-np.roll(b,shift,axis=1))));matches.append((mae,j,shift))
 matches.sort();row['external_jpg_content_match']={'source':f'data/panorama/{matches[0][1]}.jpg','RGB_MAE_255':matches[0][0],'horizontal_shift_pixels_at_1024':matches[0][2],'next_best_RGB_MAE_255':matches[1][0],'method':'exhaustive all8 images and all1024 cyclic shifts, 1024x512 RGB'}
 im=Image.open(ROOT/f'data/panorama/{i}.jpg');im.draft('RGB',(4096,2048));im=np.asarray(im.resize((4096,2048)),dtype=float);projected={}
 for face,(center,right,down) in bases.items():
  ray=np.array(center)+xx[:,:,None]*np.array(right)+yy[:,:,None]*np.array(down);ray/=np.linalg.norm(ray,axis=2)[:,:,None]
  u=((np.arctan2(ray[:,:,0],ray[:,:,2])/(2*np.pi)+.5)%1*4096).astype(int);v=np.clip((np.arccos(-ray[:,:,1])/np.pi*2048).astype(int),0,2047);projected[face]=im[v,u]
 row['cube_faces']={}
 for face in bases:
  cube=Image.open(ROOT/f'data/cube-map/{i}_{face}.jpg');cube.draft('RGB',(n,n));cube=np.asarray(cube.resize((n,n)),dtype=float);scores=[]
  for cf,pr in projected.items():
   for k in range(4):
    for mirror in [False,True]:
     cand=np.rot90(pr,k);cand=cand[:,::-1] if mirror else cand
     scores.append((float(np.mean(abs(cube-cand))),cf,k,mirror))
  best=min(scores);center,right,down=bases[best[1]]
  row['cube_faces'][face]={'source':f'data/cube-map/{i}_{face}.jpg','matched_direction':best[1],'rotation_ccw_quarters':best[2],'horizontal_mirror':best[3],'RGB_MAE_255':best[0],'canonical_local_center':center,'canonical_local_right':right,'canonical_local_down':down,'FOV_degrees':90}
  print(i,face,best,flush=True)
 # Verify raw preview independently vs all external stations; exposure transform differs so correlation.
 raw=Image.open(ROOT/f'data/panorama-raw/{i}.dng').convert('RGB').resize((1024,512));raw=np.asarray(raw,dtype=float);scores=[]
 for j,b in enumerate(external,1):
  a=raw-raw.mean(); b=b-b.mean();cor=np.fft.irfft(np.fft.rfft(b,axis=1)*np.conj(np.fft.rfft(a,axis=1)),n=1024,axis=1).sum((0,2));shift=int(cor.argmax());score=cor[shift]/np.sqrt(np.sum(a*a)*np.sum(b*b));scores.append((float(score),j,shift))
 best=max(scores);row['raw_preview_content_match']={'source':f'data/panorama-raw/{i}.dng','matched_external_station':best[1],'cyclic_shift_pixels_at_1024':best[2],'pearson_rgb':best[0],'method':'embedded RGB thumbnail 512x256 resampled1024x512, exposure-independent correlation all stations and shifts'}
(ROOT/'research/camera-registration.json').write_text(json.dumps(rows,indent=2))
