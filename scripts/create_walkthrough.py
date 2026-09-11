"""Create an editable, collision-checked camera tour in a separate Blender file."""
from pathlib import Path
import bpy, json, math, hashlib, time, shutil
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/animation/realism'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'output/reconstruction_native.blend'
assert Path(bpy.data.filepath).resolve()==SOURCE.resolve(),'Open the saved final native reconstruction before creating its camera tour.'
source_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
route = json.loads((ROOT/'scripts/walkthrough-route.json').read_text())
keys = route['keyframes']
ts = [k['time_s'] for k in keys]
assert ts[0] == 0 and all(b > a for a, b in zip(ts, ts[1:]))


def slopes(values):
    """Shape-preserving cubic slopes; stops at reversals without overshoot."""
    h = [b-a for a,b in zip(ts,ts[1:])]
    d = [(b-a)/dt for a,b,dt in zip(values,values[1:],h)]
    m = [0.0] * len(values)
    for i in range(1,len(values)-1):
        if d[i-1]*d[i] > 0:
            w1 = 2*h[i]+h[i-1]
            w2 = h[i]+2*h[i-1]
            m[i] = (w1+w2)/(w1/d[i-1]+w2/d[i])
    return m


channels = [[k['position'][i] for k in keys] for i in range(3)]
channels += [[k['yaw_deg'] for k in keys], [k['pitch_deg'] for k in keys]]
derivatives = [slopes(v) for v in channels]


def evaluate(t):
    i = min(len(ts)-2, next((i for i in range(len(ts)-1) if t <= ts[i+1]), len(ts)-2))
    h = ts[i+1]-ts[i]
    u = max(0.0,min(1.0,(t-ts[i])/h))
    return [(2*u**3-3*u**2+1)*v[i]+(u**3-2*u**2+u)*h*m[i]
            +(-2*u**3+3*u**2)*v[i+1]+(u**3-u**2)*h*m[i+1]
            for v,m in zip(channels,derivatives)]


scene = bpy.context.scene
fps = route['fps']
frame_end = round(ts[-1]*fps)
samples = [evaluate((f-1)/fps) for f in range(1,frame_end+1)]
# Native evaluated geometry only; references, hidden cutters and light controls
# are excluded. Keep every rendered physical mesh/curve, including glass.
depsgraph = bpy.context.evaluated_depsgraph_get()
vertices, triangles, owners = [], [], []
for o in scene.objects:
    if o.type not in {'MESH','CURVE'} or o.hide_render or any(c.hide_render for c in o.users_collection):
        continue
    if o.name.startswith('REFERENCE_'):
        continue
    eo = o.evaluated_get(depsgraph)
    me = eo.to_mesh()
    try:
        if not me.vertices:
            continue
        me.calc_loop_triangles()
        base = len(vertices)
        vertices.extend(eo.matrix_world @ v.co for v in me.vertices)
        for tri in me.loop_triangles:
            triangles.append(tuple(base+i for i in tri.vertices))
            owners.append(o.name)
    finally:
        eo.to_mesh_clear()
bvh = BVHTree.FromPolygons(vertices,triangles,all_triangles=True)
worst = {'distance_m': float('inf')}
collisions = []
for f,s in enumerate(samples,1):
    for level in [.45,.95,s[2]]:
        p = Vector((s[0],s[1],level))
        found = bvh.find_nearest(p)
        if found[0] is None:
            continue
        hit,normal,index,distance = found
        record = {'frame': f, 'time_s': (f-1)/fps, 'body_sample_z_m': level,
                  'distance_m': distance, 'nearest_object': owners[index],
                  'camera_position': s[:3]}
        if distance < worst['distance_m']:
            worst = record
        if distance < .12:
            collisions.append(record)
validation = {'source_sha256': source_sha, 'frames_checked': len(samples),
              'sample_heights_m': [.45,.95,route['eye_height_m']],
              'minimum_surface_clearance_required_m': .12, 'minimum_clearance': worst,
              'collisions': collisions, 'passed': not collisions,
              'method': 'Nearest evaluated native triangle at three body heights for every animation frame; Reference excluded.'}
(OUT/'path-clearance.json').write_text(json.dumps(validation,indent=2))
print('PATH_CLEARANCE',json.dumps({'passed':not collisions,'minimum':worst,'failures':len(collisions)}),flush=True)
assert not collisions, 'Route has insufficient native geometry clearance; inspect path-clearance.json'

coll = bpy.data.collections.new('Walkthrough_Animation')
scene.collection.children.link(coll)
data = bpy.data.cameras.new('Roaming_Camera')
cam = bpy.data.objects.new('Roaming_Camera',data)
coll.objects.link(cam)
cam.rotation_mode = 'XYZ'
data.lens = route['lens_mm']
data.sensor_width = 36
data.sensor_fit = 'HORIZONTAL'
data.clip_start = .04
data.clip_end = 100
data.dof.use_dof = False
cam['purpose'] = 'Editable continuous eye-height tour through all five reconstructed areas'
cam['route_source'] = 'scripts/walkthrough-route.json'
cam['source_reconstruction_sha256'] = source_sha
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
for f,s in enumerate(samples,1):
    cam.location = s[:3]
    cam.rotation_euler = (math.pi/2+math.radians(s[4]),0,math.radians(s[3])-math.pi/2)
    cam.keyframe_insert(data_path='location',frame=f,group='Roaming position')
    cam.keyframe_insert(data_path='rotation_euler',frame=f,group='Roaming gaze')
for layer in cam.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                for key in fc.keyframe_points:
                    key.interpolation = 'LINEAR'
curve = bpy.data.curves.new('Roaming_Route_Guide','CURVE')
curve.dimensions = '3D'
poly = curve.splines.new('POLY')
poly.points.add(len(samples)-1)
for p,s in zip(poly.points,samples):
    p.co = (*s[:3],1)
guide = bpy.data.objects.new('Roaming_Route_Guide',curve)
coll.objects.link(guide)
guide.hide_render = True
guide.show_in_front = True
guide.color = (1,.32,.04,1)
guide['purpose'] = 'Viewport route guide; not included in renders'
for k in keys:
    if k.get('label'):
        scene.timeline_markers.new(k['label'],frame=round(k['time_s']*fps)+1)
scene.camera = cam
scene.frame_start = 1
scene.frame_end = frame_end
scene.render.fps = fps
scene.render.fps_base = 1
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = .06
scene.cycles.use_animated_seed = False
scene.cycles.seed = 11
scene.render.use_persistent_data = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.compression = 15
scene.render.filepath = '//animation/realism/frames/frame_'
scene.render.threads_mode = 'FIXED'
scene.render.threads = 8
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
for o in bpy.context.selected_objects:
    o.select_set(False)
cam.select_set(True)
bpy.context.view_layer.objects.active = cam
instructions = bpy.data.texts.new('START_HERE_Roaming_Animation')
instructions.write('Roaming animation\n\nPlay the timeline to preview the continuous tour.\n'
    'Select Roaming_Camera to edit its native location/rotation keyframes in the Graph Editor.\n'
    'Timeline markers identify the areas and pauses. The route guide is viewport-only.\n'
    'The original reconstruction_native.blend is preserved separately.\n'
    f'Duration {ts[-1]} seconds; {fps} fps; 1280x720; Cycles 24 samples and denoising.\n'
    'All render images are packed. Source-derived graphics are mapped on native geometry; Reference scan is hidden.\n')
target = ROOT/'output/reconstruction_roaming.blend'
backup=ROOT/'output/realism/rejected-final-33455/output/reconstruction_roaming.blend'
assert backup.is_file(), 'Preserve the current roaming scene before replacement.'
assert hashlib.sha256(target.read_bytes()).hexdigest()==hashlib.sha256(backup.read_bytes()).hexdigest(), 'The preserved roaming checkpoint must match the scene being replaced.'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_sha
metadata = {'source':str(SOURCE.relative_to(ROOT)), 'source_sha256':source_sha,
            'animation_blend':str(target.relative_to(ROOT)),
            'animation_blend_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'fps':fps,'frame_count':frame_end,'duration_seconds':frame_end/fps,
            'resolution':[1280,720],'camera':'Roaming_Camera','render_engine':'CYCLES',
            'samples':24,'original_reconstruction_preserved':True}
(OUT/'animation-manifest.json').write_text(json.dumps(metadata,indent=2))
print('ANIMATION_SAVED',json.dumps(metadata),flush=True)
