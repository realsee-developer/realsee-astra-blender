"""Validate the closed USDZ in a fresh process, independent of packaging caches."""
from pathlib import Path
import hashlib,json,posixpath,struct,zipfile
from pxr import Usd,UsdGeom,UsdPhysics,UsdShade,UsdUtils,Sdf
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/usdz-v1'
source=OUT/'scene_physics.usdc'
target=ROOT/'output/reconstruction_physics_v1.usdz'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    entries=z.infolist();names=set(z.namelist())
    assert entries[0].filename.endswith(('.usdc','.usd','.usda'))
    with target.open('rb') as f:
        for row in entries:
            assert row.compress_type==zipfile.ZIP_STORED
            f.seek(row.header_offset);header=f.read(30)
            filename_length,extra_length=struct.unpack_from('<HH',header,26)
            assert (row.header_offset+30+filename_length+extra_length)%64==0,row.filename
stage=Usd.Stage.Open(str(target));assert stage
assert stage.GetDefaultPrim()
assert UsdGeom.GetStageMetersPerUnit(stage)==1
assert UsdPhysics.GetStageKilogramsPerUnit(stage)==1
assert UsdGeom.GetStageUpAxis(stage)=='Z'
prims=list(stage.Traverse())
meshes=[p for p in prims if p.IsA(UsdGeom.Mesh)]
bodies=[p for p in prims if p.HasAPI(UsdPhysics.RigidBodyAPI)]
expected=json.loads((OUT/'physics-authoring-record.json').read_text())
assert len(meshes)==expected['collision_mesh_count']==7728
assert len(bodies)==expected['body_count']
assert not any(p.IsA(UsdGeom.BasisCurves) for p in prims)
assert all(p.HasAPI(UsdPhysics.CollisionAPI) and UsdPhysics.CollisionAPI(p).GetCollisionEnabledAttr().Get() for p in meshes)
assert all(UsdPhysics.MassAPI(p).GetMassAttr().Get()>0 for p in bodies)
assets=[]
for prim in prims:
    for attr in prim.GetAttributes():
        if attr.GetTypeName()!=Sdf.ValueTypeNames.Asset:continue
        value=attr.Get()
        if not value or not value.path:continue
        path=posixpath.normpath(value.path)
        assert not path.startswith('/') and path in names,(str(attr.GetPath()),path)
        assets.append({'attribute':str(attr.GetPath()),'asset':path})
check=UsdUtils.ComplianceChecker(arkit=False)
check.CheckCompliance(str(target))
errors=check.GetErrors();failed=check.GetFailedChecks();warnings=check.GetWarnings()
record={'file':str(target.relative_to(ROOT)),'sha256':sha(target),'bytes':target.stat().st_size,
        'source_blend_sha256':expected['source_sha256'],'source_stage_sha256':sha(source),
        'actual_reopened_usdz':True,'meters_per_unit':1,'kilograms_per_unit':1,'up_axis':'Z',
        'mesh_count':len(meshes),'rigid_body_count':len(bodies),
        'materials':sum(p.IsA(UsdShade.Material) for p in prims),
        'all_asset_references_inside_archive':True,'asset_references':assets,
        'archive_entries':len(entries),'archive_crc_pass':True,'archive_64_byte_alignment_pass':True,
        'compliance_errors':errors,'compliance_failed_checks':failed,'compliance_warnings':warnings,
        'physics_authoring_record_sha256':sha(OUT/'physics-authoring-record.json'),
        'original_blend_preserved':sha(ROOT/'output/reconstruction_native.blend')==expected['source_sha256']}
(OUT/'package-validation.json').write_text(json.dumps(record,indent=2))
assert not errors and not failed,(errors,failed)
assert record['original_blend_preserved']
print('USDZ_PACKAGED_AND_REOPENED',json.dumps({k:v for k,v in record.items() if k not in ['asset_references','compliance_warnings']}),flush=True)
