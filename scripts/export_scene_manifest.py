"""Export the actual reopened scene, excluding no objects from the evidence record."""
from pathlib import Path
import bpy,json,argparse,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',default='output/reports/scene-manifest.json');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
rows=[]
for o in bpy.data.objects:
 rows.append({'name':o.name,'type':o.type,'area':o.get('area'),'source':o.get('source'),'evidence_status':o.get('evidence_status'),'geometry_class':o.get('geometry_class'),'parent':o.parent.name if o.parent else None,'dimensions_m':list(o.dimensions),'curve_spline_count':len(o.data.splines) if o.type=='CURVE' else None,'collections':[c.name for c in o.users_collection],'native_coverage_excluded':bool(o.get('native_coverage_excluded')),'render_hidden':bool(o.hide_render or any(c.hide_render for c in o.users_collection))})
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(rows,indent=2))
out.with_suffix('.record.json').write_text(json.dumps({'opened_file':str(Path(bpy.data.filepath).relative_to(ROOT)),'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'blender_version':bpy.app.version_string,'object_count':len(rows),'archive_count':sum(x['native_coverage_excluded'] for x in rows)},indent=2))
print('MANIFEST',str(out.relative_to(ROOT)),len(rows))
