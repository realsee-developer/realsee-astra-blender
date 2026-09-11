"""Read-only source audit. Run from project root; original data are never modified."""
from pathlib import Path
import argparse, hashlib, io, json, math, struct, subprocess, sys, xml.etree.ElementTree as ET
ROOT = Path.cwd().resolve()
assert (ROOT/'data').is_dir()
OUT=ROOT/'research'; OUT.mkdir(exist_ok=True)
NS={'e':'http://www.astm.org/COMMIT/E57/2010-e57-v1.0'}
def xmltext(n,path):
    q=n.find(path,NS); return q.text if q is not None and q.text is not None else ''
def read_e57_bytes(f,offset,length):
    """E57 physical offsets count four CRC bytes at each 1024-byte page end."""
    f.seek(offset); out=bytearray()
    while len(out)<length:
        pos=f.tell(); n=min(length-len(out),1020-pos%1024)
        if n<=0: f.seek(1024-pos%1024,1);continue
        out.extend(f.read(n))
        if f.tell()%1024==1020:f.seek(4,1)
    return bytes(out)
def e57_images():
    from PIL import Image
    Image.MAX_IMAGE_PIXELS=None
    with (ROOT/'data/point-cloud.e57').open('rb') as f:
        sig,major,minor,length,xoff,xlen,page=struct.unpack('<8sIIQQQQ',f.read(48))
        raw=read_e57_bytes(f,xoff,xlen)
        (OUT/'e57-metadata-current.xml').write_bytes(raw)
        xml=ET.fromstring(raw)
        scans={}
        for s in xml.findall('e:data3D/e:vectorChild',NS):
            scans[xmltext(s,'e:guid')]={'scan_name':xmltext(s,'e:name'),'scan_guid':xmltext(s,'e:guid'),
                'point_count':int(s.find('e:points',NS).get('recordCount')),
                'quaternion_wxyz':[float(xmltext(s,'e:pose/e:rotation/e:'+a) or 0) for a in 'wxyz'],
                'translation_xyz_m':[float(xmltext(s,'e:pose/e:translation/e:'+a) or 0) for a in 'xyz']}
        rows=[]
        for i,n in enumerate(xml.findall('e:images2D/e:vectorChild',NS),1):
            img=n.find('e:sphericalRepresentation/e:jpegImage',NS);off=int(img.get('fileOffset'));length=int(img.get('length'))
            blob=read_e57_bytes(f,off+16,length)
            assert blob[:2]==b'\xff\xd8',blob[:40]
            out=OUT/'e57-previews'/f'embedded-{i}.jpg';out.parent.mkdir(exist_ok=True)
            im=Image.open(io.BytesIO(blob)); im.draft('RGB',(2400,1200)); im.thumbnail((2400,1200)); im.save(out,quality=93)
            row=scans[xmltext(n,'e:associatedData3DGuid')].copy();row.update({'image_guid':xmltext(n,'e:guid'),'image_name':xmltext(n,'e:name'),'embedded_index':i,'embedded_jpeg_sha256':hashlib.sha256(blob).hexdigest(),'preview':str(out.relative_to(ROOT)), 'embedded_bytes':length});rows.append(row)
        (OUT/'camera-registration.json').write_text(json.dumps({'status':'E57 GUID association verified; external content matching pending','stations':rows},indent=2))
        print(json.dumps(rows,indent=2))
def inventory():
    old=json.loads((OUT/'data-inventory.json').read_text()); print(type(old),list(old)[:15])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['e57','inventory']);a=p.parse_args()
    {'e57':e57_images,'inventory':inventory}[a.action]()
