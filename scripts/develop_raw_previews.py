"""Actual RAW exposure/appearance inspection; uses installed analysis environment rawpy."""
from pathlib import Path
import rawpy
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/visual-previews';OUT.mkdir(exist_ok=True)
for station in range(1,9):
 with rawpy.imread(str(ROOT/f'data/panorama-raw/{station}.dng')) as raw:
  rgb=raw.postprocess(half_size=True,use_camera_wb=True,no_auto_bright=False,output_bps=8)
 im=Image.fromarray(rgb);im.thumbnail((2400,1200));im.save(OUT/f'raw-developed-{station}.jpg',quality=94)
