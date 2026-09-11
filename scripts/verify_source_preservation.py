from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
inventory=json.loads((ROOT/'research/source-audit.json').read_text());bad=[]
for row in inventory['files']:
 p=ROOT/row['path'];h=hashlib.sha256()
 with p.open('rb') as f:
  for data in iter(lambda:f.read(8*1024*1024),b''):h.update(data)
 if h.hexdigest()!=row['sha256']:bad.append(row['path'])
report={'substantive_sources_checked':len(inventory['files']),'all_original_source_hashes_preserved':not bad,'changed_sources':bad,'method':'SHA256 of every substantive input compared to initial source audit'}
(ROOT/'output/acceptance/source-preservation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));assert not bad
