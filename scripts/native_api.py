"""Native mesh/curve constructors and measured scan-part extraction used by executed build scripts."""
from pathlib import Path
import bpy, bmesh, math, json
import numpy as np
from mathutils import Vector
class NativeAPI:
 def __init__(self,root,reference,floor_offset=1.40):
  self.root=Path(root);self.reference=reference;self.offset=floor_offset;self.collection=None;self.area='';self.source='';self.parent=None
  m=reference.data
  self.v=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',self.v);self.v=self.v.reshape(-1,3);self.v[:,2]+=self.offset
  self.f=np.array([p.vertices[:] for p in m.polygons],dtype=np.int32)
  self.cent=self.v[self.f].mean(1)
  self.material_indices=np.array([p.material_index for p in m.polygons])
  self.uv=np.empty(len(m.loops)*2,dtype=np.float32);m.uv_layers.active.data.foreach_get('uv',self.uv);self.uv=self.uv.reshape(-1,2)
 def area_collection(self,name,source):
  self.area=name;self.source=source;self.parent=None
  c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
  if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
  self.collection=c;return c
 def mat(self,name,color,roughness=.5,metallic=0,emission=0):
  m=bpy.data.materials.get(name)
  if m:return m
  m=bpy.data.materials.new(name);m.diffuse_color=(*color[:3],1);m.use_nodes=True
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color[:3],1);bs.inputs['Roughness'].default_value=roughness;bs.inputs['Metallic'].default_value=metallic
  if emission:bs.inputs['Emission Color'].default_value=(*color[:3],1);bs.inputs['Emission Strength'].default_value=emission
  return m
 def tag(self,o,name,mat=None,status='inferred completion constrained by registered scan and cube photographs'):
  o.name=name
  for c in list(o.users_collection):c.objects.unlink(o)
  self.collection.objects.link(o)
  if mat:o.data.materials.append(mat)
  o['stable_id']=name;o['area']=self.area;o['source']=self.source;o['evidence_status']=status
  if self.parent:o.parent=self.parent;o.matrix_parent_inverse=self.parent.matrix_world.inverted()
  return o
 def group(self,name,loc=(0,0,0)):
  o=bpy.data.objects.new(name,None);self.collection.objects.link(o);o.location=loc;o['stable_id']=name;o['area']=self.area;o['source']=self.source
  bpy.context.view_layer.update();self.parent=o;return o
 def box(self,name,loc,size,mat,bevel=0,rot=0):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler.z=rot
  self.tag(o,name,mat)
  if bevel:
   m=o.modifiers.new('Editable edge radius','BEVEL');m.width=bevel;m.segments=3
  return o
 def mesh(self,name,verts,faces,mat=None):
  m=bpy.data.meshes.new(name+'_Mesh');m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);self.collection.objects.link(o);self.tag(o,name,mat);return o
 def cyl(self,name,loc,radius,depth,mat,vertices=32,rot=None,r2=None):
  bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=radius if r2 is None else r2,depth=depth,location=loc);o=bpy.context.object
  if rot:o.rotation_euler=rot
  self.tag(o,name,mat)
  for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
  return o
 def ball(self,name,loc,scale,mat):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=loc);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);self.tag(o,name,mat)
  for p in o.data.polygons:p.use_smooth=True
  return o
 def rod(self,name,a,b,r,mat,vertices=12):
  a,b=Vector(a),Vector(b);o=self.cyl(name,(a+b)/2,r,(b-a).length,mat,vertices);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
 def curve(self,name,pts,r,mat,cyclic=False):
  c=bpy.data.curves.new(name+'_Curve','CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(pts)-1)
  for p,co in zip(s.points,pts):p.co=(*co,1)
  s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,c);self.collection.objects.link(o);return self.tag(o,name,mat)
 def lathe(self,name,loc,profile,mat,n=32):
  vs=[(loc[0]+r*math.cos(j*2*math.pi/n),loc[1]+r*math.sin(j*2*math.pi/n),loc[2]+z) for r,z in profile for j in range(n)];fs=[]
  for i in range(len(profile)-1):
   for j in range(n):a=i*n+j;b=i*n+(j+1)%n;fs.append((a,b,b+n,a+n))
  fs.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+j for j in range(n))]);o=self.mesh(name,vs,fs,mat)
  for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
  return o
 def scan_part(self,name,bounds,mat=None,flat_axis=None,flat_value=None):
  """Extract local triangles, keep exact source UVs, remove coincident vertices. Bounds in scene meters."""
  low,high=np.array(bounds[0]),np.array(bounds[1]);sel=np.all((self.cent>=low)&(self.cent<=high),axis=1);fi=np.nonzero(sel)[0]
  if not len(fi):raise ValueError(f'No source triangles for {name} {bounds}')
  faces=self.f[fi];unique,inverse=np.unique(faces,return_inverse=True);verts=self.v[unique].copy();center=(verts.min(0)+verts.max(0))/2
  if flat_axis is not None:verts[:,flat_axis]=flat_value;center[flat_axis]=flat_value
  verts-=center;o=self.mesh(name,verts.tolist(),inverse.reshape(-1,3).tolist());o.location=center
  materials=sorted(set(self.material_indices[fi].tolist()))
  for mi in materials:o.data.materials.append(self.reference.data.materials[mi])
  uv=o.data.uv_layers.new(name='SourceScanUV')
  uv.data.foreach_set('uv',self.uv[(fi[:,None]*3+np.arange(3)).reshape(-1)].ravel())
  for p,mi in zip(o.data.polygons,self.material_indices[fi]):p.material_index=materials.index(int(mi))
  bm=bmesh.new();bm.from_mesh(o.data)
  # Clip long scan triangles at semantic part boundaries, preserving interpolated source UV.
  for axis in range(3):
   for val,sign in [(low[axis],-1),(high[axis],1)]:
    co=Vector((0,0,0));co[axis]=float(val-center[axis]);normal=Vector((0,0,0));normal[axis]=sign
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=co,plane_no=normal,clear_outer=True,clear_inner=False)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00001);bm.to_mesh(o.data);bm.free()
  o['evidence_status']='measured scan surface; segmented and cleaned; occluded backs unknown';o['source_triangle_count']=len(fi);o['source_bounds_scene_m']=json.dumps(bounds);o['geometry_class']='scan-derived complex local surface';return o
 def area_light(self,name,loc,power,color,size=1,rotation=(0,0,0)):
  d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);self.collection.objects.link(o);o.location=loc;o.rotation_euler=rotation;return o
 def photo_plane(self,name,center,u_vec,v_vec,station,frame_mat=None):
  """Planar printed graphic with photograph-projected native UVs; no structure is baked."""
  from mathutils import Quaternion
  data=json.loads((self.root/'research/camera-registration.json').read_text())['stations'][station-1]
  pos=Vector(data['translation_xyz_m']);pos.z+=self.offset;q=Quaternion(data['quaternion_wxyz']).inverted()
  center=Vector(center);u=Vector(u_vec);v=Vector(v_vec);verts=[];uvs=[];faces=[];n=12
  for j in range(n+1):
   for i in range(n+1):
    p=center+u*(i/n-.5)+v*(j/n-.5);ray=q@(p-pos);ray.normalize();verts.append(tuple(p));uvs.append(((math.atan2(ray.x,ray.z)/(2*math.pi)+.5)%1,1-math.acos(max(-1,min(1,-ray.y)))/math.pi))
  for j in range(n):
   for i in range(n):k=j*(n+1)+i;faces.append((k,k+1,k+n+2,k+n+1))
  name_mat=f'PhotoGraphicStation{station}';m=bpy.data.materials.get(name_mat)
  if not m:
   m=self.mat(name_mat,(1,1,1),.7);nt=m.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(self.root/f'output/assets/panorama-{station}-material.jpg'),check_existing=True);nt.links.new(tex.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color'])
  o=self.mesh(name,verts,faces,m);uv=o.data.uv_layers.new(name='RegisteredPhotoProjection')
  for p in o.data.polygons:
   for li in p.loop_indices:uv.data[li].uv=uvs[o.data.loops[li].vertex_index]
  o['evidence_status']='planar graphic photo-projected from verified E57 camera; frame modeled separately';o['station']=station
  if frame_mat:
   normal=u.cross(v).normalized()
   corners=[center-u/2-v/2,center+u/2-v/2,center+u/2+v/2,center-u/2+v/2]
   self.curve(name+'.Frame',[tuple(p+normal*.008) for p in corners],.013,frame_mat,True)
  return o
