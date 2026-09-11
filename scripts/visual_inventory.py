from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import subprocess,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research'/'visual-previews'
OUT.mkdir(exist_ok=True)
Image.MAX_IMAGE_PIXELS=None
for station in range(1,9):
    sheet=Image.new('RGB',(2100,1460),'#202020'); draw=ImageDraw.Draw(sheet)
    for k,face in enumerate('frblud'):
        p=ROOT/'data'/'cube-map'/f'{station}_{face}.jpg'
        with Image.open(p) as im:
            im.thumbnail((700,700)); sheet.paste(im,((k%3)*700,(k//3)*730+30))
        draw.text(((k%3)*700+10,(k//3)*730+8),p.name,fill='white')
    sheet.save(OUT/f'cube-station-{station}.jpg',quality=94)
meta=subprocess.check_output(['exiftool','-json','-ImageWidth','-ImageHeight','-SubfileType','-PreviewImage','-JpgFromRaw','-ThumbnailImage',str(ROOT/'data'/'panorama-raw')],text=True)
(OUT/'raw-metadata.json').write_text(meta)
info=subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(ROOT/'data'/'gen-vr-video.mp4')],text=True)
(OUT/'video-metadata.json').write_text(info)
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(ROOT/'data'/'gen-vr-video.mp4'),'-vf','fps=1/5,scale=720:-1','-y',str(OUT/'video-%03d.jpg')],check=True)
frames=sorted(OUT.glob('video-*.jpg'))
rows=(len(frames)+3)//4
sheet=Image.new('RGB',(2880,rows*435),'#202020'); draw=ImageDraw.Draw(sheet)
for i,p in enumerate(frames):
    with Image.open(p) as im: sheet.paste(im,((i%4)*720,(i//4)*435+30))
    draw.text(((i%4)*720+10,(i//4)*435+8),f'{i*5} sec',fill='white')
sheet.save(OUT/'video-contact.jpg',quality=94)
print('Created cube contact sheets, RAW metadata, and video frames:',len(frames))
