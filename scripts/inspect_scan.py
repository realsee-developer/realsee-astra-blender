from pathlib import Path
import bpy, numpy as np, json
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=str(ROOT/'data/model/obj-high-resolution-model/block_0.obj'), forward_axis='Y', up_axis='Z', use_split_objects=False, use_split_groups=False)
obj=bpy.context.selected_objects[0]
obj.name='REFERENCE_HighResolution_OriginalOBJ'
ref=bpy.data.collections.new('Reference_OriginalScan'); bpy.context.scene.collection.children.link(ref)
for col in list(obj.users_collection): col.objects.unlink(obj)
ref.objects.link(obj)
a=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',a);a=a.reshape(-1,3)
info={'vertices':len(a),'faces':len(obj.data.polygons),'matrix_world':[list(r) for r in obj.matrix_world], 'bounds':[a.min(0).tolist(),a.max(0).tolist()], 'quantiles':np.quantile(a,[0,.01,.1,.5,.9,.99,1],axis=0).tolist()}
hist,edges=np.histogram(a[:,2],bins=220)
info['z_hist_peaks']=sorted([(int(n),float((edges[i]+edges[i+1])/2)) for i,n in enumerate(hist)],reverse=True)[:30]
(ROOT/'research/scan-inspection.json').write_text(json.dumps(info,indent=2))
obj['source']='data/model/obj-high-resolution-model/block_0.obj';obj['status']='unmodified reference';obj['axis']='raw coordinates preserved; Z up pending source verification'
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='METERS'
# Working inspection camera views are in raw coordinates; saved original material nodes stay untouched.
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'output/checkpoints/00_scan_import.blend'))
print(json.dumps(info,indent=2))
# render texture as emission for the captured scan, only in temporary process state
for mat in obj.data.materials:
 if mat and mat.use_nodes:
  nt=mat.node_tree; tex=next((n for n in nt.nodes if n.type=='TEX_IMAGE'),None)
  out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
  if tex:
   em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs['Color'],em.inputs[0]);nt.links.new(em.outputs[0],out.inputs['Surface'])
scene.render.engine='CYCLES';scene.cycles.samples=4
scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('InspectionWhite');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1)
scene.view_settings.view_transform='Standard'
# clip section above 1.7 raw z by removing vertices on separate render-only mesh
cut=obj.copy();cut.data=obj.data.copy();ref.objects.link(cut);obj.hide_render=True
import bmesh
bm=bmesh.new();bm.from_mesh(cut.data);bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z>0.5],context='VERTS');bm.to_mesh(cut.data);bm.free()
camd=bpy.data.cameras.new('InspectionCamera');cam=bpy.data.objects.new('InspectionCamera',camd);scene.collection.objects.link(cam);scene.camera=cam
cam.location=(-2.5,4.3,18);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=15.5
scene.render.filepath=str(ROOT/'research/previews/scan_plan_raw.png');bpy.ops.render.render(write_still=True)
