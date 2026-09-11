"""Render saved native camera animation with the discovered Metal GPU."""
from pathlib import Path
import argparse, hashlib, json, sys, time
import bpy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output/animation/realism'
parser = argparse.ArgumentParser()
parser.add_argument('stage',choices=['preview','final'])
parser.add_argument('--resume-record', help='Verified consecutive PNGs from the interrupted final render')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
assert not args.resume_record or args.stage == 'final'
manifest = json.loads((OUT/'animation-manifest.json').read_text())
opened = Path(bpy.data.filepath)
assert hashlib.sha256(opened.read_bytes()).hexdigest() == manifest['animation_blend_sha256']
scene = bpy.context.scene
assert scene.camera.name == manifest['camera']
assert scene.frame_end == manifest['frame_count']
assert not [im.name for im in bpy.data.images if im.source == 'FILE' and not im.packed_file]
assert all(o.hide_render for o in scene.objects if o.name.startswith('REFERENCE_'))
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'
prefs.refresh_devices()
for d in prefs.devices:
    d.use = d.type == 'METAL'
assert any(d.type == 'METAL' for d in prefs.devices)
scene.cycles.device = 'GPU'
scene.cycles.denoising_use_gpu = True
scene.render.use_persistent_data = True
if args.stage == 'preview':
    scene.render.resolution_percentage = 62
    frames = [1,145,260,310,385,550,620,715,815,1028,1125,1175,1230,1300,1495,1585,1730,1900,2010,2040]
    folder = OUT/'preview-frames'
else:
    # A complete camera preview cannot accept unresolved source geometry defects.
    # The previous full render was stopped after final source reviews rejected it.
    final_review = json.loads((ROOT/'output/acceptance/final-visual-review.json').read_text())
    assert final_review['source_delivery_sha256'] == manifest['source_sha256']
    assert final_review['all_required_views_reviewed'] and not final_review['unresolved_observable_defects']
    final_audit = json.loads((ROOT/'output/acceptance/file_audit.json').read_text())
    assert final_audit['opened_file_sha256'] == manifest['source_sha256'] and final_audit['mechanical_checks_pass']
    review = json.loads((OUT/'preview-visual-review.json').read_text())
    assert review['animation_blend_sha256'] == manifest['animation_blend_sha256']
    assert review['all_preview_frames_reviewed'] and not review['unresolved_route_defects']
    frames = list(range(scene.frame_start,scene.frame_end+1))
    folder = OUT/'frames'
folder.mkdir(parents=True,exist_ok=True)
record = {'animation_blend_sha256':manifest['animation_blend_sha256'],
          'source_reconstruction_sha256':manifest['source_sha256'],
          'factory_startup':'--factory-startup' in sys.argv,
          'stage':args.stage,'render_engine':scene.render.engine,
          'device':[d.name for d in prefs.devices if d.use],
          'samples':scene.cycles.samples,'gpu_denoising':scene.cycles.denoising_use_gpu,'frames':[]}
if args.resume_record:
    partial_path = ROOT / args.resume_record
    partial = json.loads(partial_path.read_text())
    assert partial['stage'] == 'interrupted-final' and partial['factory_startup']
    assert partial['animation_blend_sha256'] == manifest['animation_blend_sha256']
    assert partial['source_reconstruction_sha256'] == manifest['source_sha256']
    assert partial['render_engine'] == scene.render.engine and partial['samples'] == scene.cycles.samples
    assert [r['frame'] for r in partial['frames']] == list(range(1, partial['next_frame']))
    assert 1 < partial['next_frame'] <= scene.frame_end
    for row in partial['frames']:
        assert row['path'] == f'output/animation/realism/frames/frame_{row["frame"]:04d}.png'
        assert row['decoded_png_verified']
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['image_sha256']
    for key in ['log', 'original_renderer']:
        assert hashlib.sha256((ROOT / partial[key]).read_bytes()).hexdigest() == partial[key + '_sha256']
    record['frames'] = partial['frames']
    record['resumed_from'] = {'record': args.resume_record,
        'record_sha256': hashlib.sha256(partial_path.read_bytes()).hexdigest(),
        'previous_actual_frames': len(partial['frames']), 'first_new_frame': partial['next_frame']}
    record['timing_scope'] = 'elapsed_seconds measures this fresh continuation process only; interrupted batch save timestamps remain in its preserved record.'
    scene.frame_start = partial['next_frame']
    print('RESUMING_VERIFIED_FINAL_FRAMES', scene.frame_start, scene.frame_end, flush=True)
start = time.monotonic()
last_write = start

def record_frame(scene):
    global last_write
    frame = scene.frame_current
    now = time.monotonic()
    row = {'frame':frame,'path':str((folder/f'frame_{frame:04d}.png').relative_to(ROOT)),
           'seconds':round(now-last_write,3)}
    row['image_sha256'] = hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()
    record['frames'].append(row)
    last_write = now
    if args.stage == 'preview' or frame % 24 == 0:
        print('ANIMATION_PROGRESS',json.dumps({'frame':frame,'total':len(frames),
              'elapsed_seconds':round(now-start,1),'last_frame_seconds':row['seconds']}),flush=True)

if args.stage == 'final':
    scene.render.filepath = str(folder/'frame_')
    scene.render.use_overwrite = True
    bpy.app.handlers.render_write.append(record_frame)
    try:
        bpy.ops.render.render(animation=True)
    finally:
        bpy.app.handlers.render_write.remove(record_frame)
else:
    for frame in frames:
        scene.frame_set(frame)
        scene.render.filepath = str(folder/f'frame_{frame:04d}.png')
        bpy.ops.render.render(write_still=True)
        record_frame(scene)
assert [r['frame'] for r in record['frames']] == frames
record['elapsed_seconds'] = time.monotonic()-start
record['animation_file_unchanged'] = hashlib.sha256(opened.read_bytes()).hexdigest() == manifest['animation_blend_sha256']
record['original_reconstruction_unchanged'] = hashlib.sha256((ROOT/manifest['source']).read_bytes()).hexdigest() == manifest['source_sha256']
assert record['animation_file_unchanged'] and record['original_reconstruction_unchanged']
(OUT/f'render-{args.stage}.json').write_text(json.dumps(record,indent=2))
print('ANIMATION_RENDER_COMPLETE',args.stage,len(frames),'frames',round(record['elapsed_seconds'],1),'seconds',flush=True)
