"""Compose already rendered comparisons; never modifies source images."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'output/previews/comparisons';Image.MAX_IMAGE_PIXELS=None
arg=argparse.ArgumentParser();arg.add_argument('--quick',action='store_true');args=arg.parse_args()
faces=['f','r'] if args.quick else ['f','r','b','l','u','d'];size=340;columns=2 if args.quick else 3;rows=(len(faces)+columns-1)//columns
for i in range(1,9):
 canvas=Image.new('RGB',(columns*size*2,rows*(size+42)),(26,27,29));d=ImageDraw.Draw(canvas)
 for j,f in enumerate(faces):
  x=(j%columns)*size*2;y=(j//columns)*(size+42);d.text((x+8,y+6),f'Station {i} / {f} — Source | Native, Reference hidden',fill=(245,245,245))
  src=Image.open(ROOT/f'data/cube-map/{i}_{f}.jpg');src.draft('RGB',(size,size));canvas.paste(src.convert('RGB').resize((size,size)),(x,y+32))
  file=P/f'native-{i}_{f}.png'
  if file.is_file():canvas.paste(Image.open(file).convert('RGB').resize((size,size)),(x+size,y+32))
  else:d.text((x+size+10,y+70),'NOT YET RENDERED',fill=(255,155,90))
 canvas.save(P/f'station-{i}-{"quick" if args.quick else "all-directions"}.jpg',quality=90)
print('Comparison contacts written',P)
