"""Extract actual modelspace CAD geometry and register to observed point cloud.
Run from PROJECT_ROOT with .venv-analysis/bin/python scripts/cad_analysis.py.
"""
from pathlib import Path
import json, collections
import numpy as np
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
ROOT=Path.cwd().resolve()
assert (ROOT/'data').is_dir()
OUT=ROOT/'research'
def read_ply():
 with (ROOT/'data/point-cloud.ply').open('rb') as f:
  header=[]
  while True:
   line=f.readline().decode('ascii').strip();header.append(line)
   if line=='end_header':break
  n=int(next(s.split()[-1] for s in header if s.startswith('element vertex')))
  a=np.fromfile(f,dtype=[(k,'<f4') for k in ['x','y','z','nx','ny','nz']]+[(k,'u1') for k in ['r','g','b']],count=n)
 return np.column_stack([a[k] for k in ['x','y','z']]),np.column_stack([a[k] for k in ['nx','ny','nz']]),np.column_stack([a[k] for k in ['r','g','b']])
def main():
 doc=ezdxf.readfile(ROOT/'data/cad.dxf');m=doc.modelspace()
 result={'source':'data/cad.dxf','units':doc.header.get('$INSUNITS'),'counts':dict(collections.Counter(e.dxftype() for e in m)),'layers':dict(collections.Counter(e.dxf.layer for e in m)),'lines':[],'texts':[],'hatches':[],'inserts':[],'blocks':[]}
 for block in doc.blocks:
  result['blocks'].append({'name':block.name,'count':len(block),'types':dict(collections.Counter(e.dxftype() for e in block))})
 for e in m:
  d={'handle':e.dxf.handle,'layer':e.dxf.layer}
  if e.dxftype()=='LINE':d.update(a=list(e.dxf.start),b=list(e.dxf.end));result['lines'].append(d)
  elif e.dxftype()=='TEXT':d.update(text=e.dxf.text,at=list(e.dxf.insert),rotation=e.dxf.get('rotation',0));result['texts'].append(d)
  elif e.dxftype()=='HATCH':
   d['paths']=[]
   for p in e.paths:
    if hasattr(p,'vertices'):d['paths'].append({'vertices':[list(v) for v in p.vertices]})
    else:
     ed=[]
     for x in p.edges:
      if hasattr(x,'start'):ed.append({'a':list(x.start),'b':list(x.end)})
     d['paths'].append({'edges':ed})
   result['hatches'].append(d)
  elif e.dxftype()=='INSERT':d.update(name=e.dxf.name,at=list(e.dxf.insert));result['inserts'].append(d)
 (OUT/'cad-entities.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({k:result[k] for k in ['units','counts','layers','inserts']},indent=2),flush=True)
 for e in result['texts']:
  if 'CH:' in e['text'] or 'DH:' in e['text'] or 'DW:' in e['text']:print(e,flush=True)
 fig,ax=plt.subplots(figsize=(16,14))
 colors={'A-WALL':'black','A-WALL-EXTR':'black','A-DOOR':'blue','A-GLAZ':'cyan'}
 for layer in sorted(set(e['layer'] for e in result['lines'])):
  if 'DIMN' in layer or 'ANNO' in layer:continue
  lines=[[[*e['a'][:2]],[*e['b'][:2]]] for e in result['lines'] if e['layer']==layer]
  if lines:ax.add_collection(LineCollection(lines,label=layer,linewidths=1.5))
 for e in result['texts']:
  if e['layer'] in ['A-AREA-TEXT','A-DOOR-DIMN','A-GLAZ-DIMN'] and not e['text'].startswith('FFL'):
   ax.text(*e['at'][:2],e['text'],fontsize=7)
 ax.autoscale();ax.set_aspect('equal');ax.legend();ax.grid();fig.savefig(OUT/'cad-plan.png',dpi=150);plt.close(fig)
 p,n,c=read_ply()
 print('PLY BOUNDS',p.min(0),p.max(0),flush=True)
 print('PLY QUANTILES',np.quantile(p,[.001,.01,.1,.5,.9,.99,.999],axis=0),flush=True)
 np.savez_compressed(OUT/'cad-ply-sample.npz',points=p[::5],normals=n[::5],colors=c[::5])
 fig,axs=plt.subplots(1,3,figsize=(18,8))
 for ax,(i,j) in zip(axs,[(0,1),(0,2),(1,2)]):
  ax.scatter(p[::20,i],p[::20,j],c=c[::20]/255,s=.2);ax.set_aspect('equal');ax.set_xlabel('xyz'[i]);ax.set_ylabel('xyz'[j]);ax.grid()
 fig.savefig(OUT/'cad-ply-projections.png',dpi=180)
if __name__=='__main__':main()

def register():
 from scipy.spatial import cKDTree
 from scipy.optimize import least_squares
 j=json.loads((OUT/'cad-entities.json').read_text())
 p,n,c=read_ply()
 # Only interior CAD surface lines; 59F onward are standardized outer offsets.
 lines=[l for l in j['lines'] if l['layer']=='A-WALL-LINE' and int(l['handle'],16)<int('59F',16)]
 a=np.array([l['a'][:2] for l in lines])/1000;b=np.array([l['b'][:2] for l in lines])/1000
 v=b-a;length=np.linalg.norm(v,axis=1);u=v/length[:,None];perp=np.stack([-u[:,1],u[:,0]],axis=1)
 cand=(abs(n[:,2])<.08)&(p[:,2]>-.8)&(p[:,2]<1.1)
 inds=np.where(cand)[0][::4];pts=p[inds,:2];normals=n[inds,:2]
 def correspondence(par):
  tx,ty,ang=par;co,si=np.cos(ang),np.sin(ang);R=np.array([[co,-si],[si,co]])
  q=(pts-np.array([tx,ty]))@R
  d=q[:,None,:]-a[None,:,:]
  t=(d*u[None,:,:]).sum(2)
  dist=(d*perp[None,:,:]).sum(2)
  valid=(t>.15)&(t<length[None,:]-.15)&(abs(normals@R@perp.T)>.985)
  ds=np.where(valid,abs(dist),100)
  ix=ds.argmin(1);ok=ds.min(1)<.10
  return q,ix,ok
 par=np.array([-13.67,12.97,0.])
 for iteration in range(6):
  q,ix,ok=correspondence(par);pp=pts[ok];ii=ix[ok]
  def residual(params):
   tx,ty,ang=params;co,si=np.cos(ang),np.sin(ang);R=np.array([[co,-si],[si,co]])
   qq=(pp-np.array([tx,ty]))@R
   return ((qq-a[ii])*perp[ii]).sum(1)
  fit=least_squares(residual,par,loss='soft_l1',f_scale=.012,max_nfev=30)
  par=fit.x
  print('FIT',iteration,par,'n',len(pp),'median',np.median(abs(fit.fun)),flush=True)
 tx,ty,ang=par;co,si=np.cos(ang),np.sin(ang);R=np.array([[co,-si],[si,co]])
 floor_mask=(abs(n[:,2])>.985)&(p[:,2]>-1.45)&(p[:,2]<-1.35)
 floor=float(np.median(p[floor_mask,2]));floor_offset=-floor
 q,ix,ok=correspondence(par)
 signed=((q-a[ix])*perp[ix]).sum(1)
 statistics=[]
 for k,l in enumerate(lines):
  sel=ok&(ix==k);ds=signed[sel]
  if len(ds):statistics.append({'handle':l['handle'],'samples':len(ds),'median_signed_m':float(np.median(ds)),'median_abs_m':float(np.median(abs(ds))),'p95_abs_m':float(np.quantile(abs(ds),.95))})
 result={'source':'data/cad.dxf','target_frame':'Raw PLY x,y; PLY z shifted by floor datum','cad_mm_to_scene_matrix':[[co*.001,-si*.001,0,tx],[si*.001,co*.001,0,ty],[0,0,.001,0],[0,0,0,1]],'cad_plan_z_rule':'CAD FFL=0; modeling z uses annotated heights above scene floor; raw PLY receives separate floor translation.','cad_to_ply_xy_rotation_radians':ang,'cad_to_ply_xy_translation_m':[tx,ty],'ply_to_scene_matrix':[[1,0,0,0],[0,1,0,0],[0,0,1,floor_offset],[0,0,0,1]],'ply_floor_datum_m':floor,'floor_samples':int(floor_mask.sum()),'floor_residuals_m':{'median_abs':float(np.median(abs(p[floor_mask,2]-floor))),'p95_abs':float(np.quantile(abs(p[floor_mask,2]-floor),.95))},'registration_method':'Unscaled XY rigid transform fitted against interior CAD segments 570:59E. PLY candidates z(-0.8,1.1), abs(nz)<0.08; every fourth qualifying point; normal agreement >0.985, segment endpoints excluded by 0.15m. Iterative segment associations within 0.10m; soft_l1 robust loss 0.012m. Standardized outer wall offsets excluded.','sampling_candidates':len(pts),'inlier_samples':int(ok.sum()),'residual_summary_m':{'median_abs':float(np.median(abs(signed[ok]))),'p95_abs':float(np.quantile(abs(signed[ok]),.95))},'per_wall_statistics':statistics,'control_points':[]}
 for k in ['577','578','583','584','58C','597']:
  l=next(l for l in lines if l['handle']==k)
  aa=np.array(l['a'][:2])*.001@R.T+[tx,ty];bb=np.array(l['b'][:2])*.001@R.T+[tx,ty]
  result['control_points'].append({'cad_entity':k,'cad_start_mm':l['a'],'scene_start_m':[float(*aa[:1]),float(aa[1]),0],'cad_end_mm':l['b'],'scene_end_m':[float(bb[0]),float(bb[1]),0]})
 (OUT/'registration-cad.json').write_text(json.dumps(result,indent=2))
 fig,ax=plt.subplots(figsize=(15,12));ax.scatter(p[::25,0],p[::25,1],c=c[::25]/255,s=.35)
 aa=a@R.T+[tx,ty];bb=b@R.T+[tx,ty]
 ax.add_collection(LineCollection(np.stack([aa,bb],axis=1),colors='lime',linewidths=1))
 for l,aa1,bb1 in zip(lines,aa,bb):ax.text(*((aa1+bb1)/2),l['handle'],fontsize=6,c='red')
 ax.set_aspect('equal');ax.set_title('Interior CAD surfaces (green), PLY true color; no scale fit');ax.grid();fig.savefig(OUT/'cad-registered-plan.png',dpi=180)
 print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':register()
