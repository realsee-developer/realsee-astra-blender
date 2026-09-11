"""Encode and verify the completed Blender frame sequence as an H.264 MP4."""
from pathlib import Path
import hashlib, json, shutil, subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output/animation/realism'
manifest = json.loads((OUT/'animation-manifest.json').read_text())
render = json.loads((OUT/'render-final.json').read_text())
assert render['animation_blend_sha256'] == manifest['animation_blend_sha256']
assert render['source_reconstruction_sha256'] == manifest['source_sha256']
assert render['animation_file_unchanged'] and render['original_reconstruction_unchanged']
assert [r['frame'] for r in render['frames']] == list(range(1,manifest['frame_count']+1))
for row in render['frames']:
    assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['image_sha256']
video = OUT/'verified-roaming.mp4'
duration = manifest['duration_seconds']
subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','warning','-xerror','-n',
    '-framerate',str(manifest['fps']),'-start_number','1','-i',str(OUT/'frames/frame_%04d.png'),
    '-frames:v',str(manifest['frame_count']),'-vf',f'fade=t=in:st=0:d=0.6,fade=t=out:st={duration-.8}:d=0.8',
    '-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p',
    '-movflags','+faststart','-an',str(video)],check=True)
probe = json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error',
    '-count_frames','-show_streams','-show_format','-of','json',str(video)],text=True))
stream = next(s for s in probe['streams'] if s['codec_type']=='video')
assert stream['codec_name']=='h264'
assert [stream['width'],stream['height']]==manifest['resolution']
assert int(stream['nb_read_frames'])==manifest['frame_count']
assert abs(float(probe['format']['duration'])-duration)<.05
subprocess.run([shutil.which('ffmpeg'),'-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
assert hashlib.sha256((ROOT/manifest['source']).read_bytes()).hexdigest()==manifest['source_sha256']
assert hashlib.sha256((ROOT/manifest['animation_blend']).read_bytes()).hexdigest()==manifest['animation_blend_sha256']
delivery=ROOT/'output/reconstruction_roaming.mp4';backup=ROOT/'output/checkpoints/06_before_realism_roaming.mp4'
assert backup.is_file() and hashlib.sha256(delivery.read_bytes()).hexdigest()==hashlib.sha256(backup.read_bytes()).hexdigest(), 'Preserve the exact previous video before replacement.'
shutil.copy2(video,delivery)
assert hashlib.sha256(video.read_bytes()).hexdigest()==hashlib.sha256(delivery.read_bytes()).hexdigest()
video=delivery
verification = {'video':str(video.relative_to(ROOT)),
    'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
    'codec':stream['codec_name'],'resolution':manifest['resolution'],
    'fps':stream['avg_frame_rate'],'duration_seconds':float(probe['format']['duration']),
    'decoded_frames':int(stream['nb_read_frames']),
    'all_frames_decode_without_errors':True,'original_reconstruction_preserved':True,
    'animation_blend_sha256':manifest['animation_blend_sha256'],
    'render_record':'output/animation/realism/render-final.json',
    'camera_clearance':'output/animation/realism/path-clearance.json',
    'audio':'Silent architectural walkthrough',
    'finishing':'0.6-second opening fade and0.8-second closing fade; no interpolated animation frames'}
(OUT/'video-verification.json').write_text(json.dumps(verification,indent=2))
(OUT/'README.md').write_text(f'''# Roaming animation

Open [the MP4](../../reconstruction_roaming.mp4) to play the {duration:g}-second, 1280×720, 24 fps tour.
Open [the Blender animation](../../reconstruction_roaming.blend) to edit it.

The camera travels continuously from the entrance through the bar, photography room, game room and living/dining area. All frames were rendered in Blender Cycles. The video is silent.

Select `Roaming_Camera` and use the Graph Editor or Dope Sheet to edit its native position and rotation keyframes. Timeline markers identify room entries, pauses and gaze cues. `Roaming_Route_Guide` is a viewport-only curve. The animation starts at frame1 and ends at frame{manifest['frame_count']}. Camera height is1.50m and focal length21mm.

The original `reconstruction_native.blend` remains unchanged. Model geometry, materials, packed textures and the hidden original scan reference are preserved in the animation copy.

Camera clearance was checked against evaluated native geometry at all {manifest['frame_count']} frames, at three body heights. Preview frames were visually checked after reopening the saved animation. `video-verification.json` records the encoded duration, frame count, hashes and successful full-video decode.

Executed scripts: `../../../scripts/create_walkthrough.py`, `../../../scripts/render_walkthrough.py`, `../../../scripts/encode_walkthrough.py`. Authoring waypoints: `../../../scripts/walkthrough-route.json`. Rendered PNG sequence: `frames/`. The prior video, animation file and frame directory are preserved separately.
''')
print(json.dumps(verification,indent=2))
