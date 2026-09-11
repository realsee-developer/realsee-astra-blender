from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS=None
(ROOT/'output/assets').mkdir(exist_ok=True)
for i in [1,2,5,6,7,8]:
 p=ROOT/f'output/assets/panorama-{i}-material.jpg'
 if not p.exists():
  with Image.open(ROOT/f'data/panorama/{i}.jpg') as im:
   im.thumbnail((6000,3000));im.save(p,quality=95)
