"""Author portable USD Physics on the real native-mesh export; masses are estimates."""
from pathlib import Path
import hashlib, json, re, shutil
from pxr import Usd, UsdGeom, UsdPhysics, UsdShade, Gf, Sdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output/usdz-v1'
target = OUT/'scene_physics.usdc'
assert not target.exists()
shutil.copy2(OUT/'scene_mesh.usdc', target)
stage = Usd.Stage.Open(str(target))
assert UsdGeom.GetStageMetersPerUnit(stage) == 1 and UsdGeom.GetStageUpAxis(stage) == 'Z'
UsdPhysics.SetStageKilogramsPerUnit(stage, 1.0)
name_attr = 'userProperties:blender:object_name'
def names():
    return {p.GetAttribute(name_attr).Get():p for p in stage.Traverse() if p.HasAttribute(name_attr)}
objects = names()
cache = UsdGeom.XformCache()
original_meshes = {str(p.GetPath()):p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)}
assert len(original_meshes) == 7728
original_poses = {name:cache.GetLocalToWorldTransform(p) for name,p in objects.items()}
fixed = UsdGeom.Xform.Define(stage, '/Scene/PhysicsBodies').GetPrim()

patterns = [r'BAR-BOTTLE-[A-Z]+-\d{2}',r'BAR-CHAIR-\d{2}',
            r'BAR-BOOKS-(?:BOTTOM|COUNTER|LOW|MID)-\d{2}',
            r'COR.Backpack.\d+',r'FAS-BAG-[A-Z-]+',r'FAS-GOLD-[NS]-BAG-\d{2}',
            r'FAS-BOOKS-[NS]-(?:MID|BASE|TOP)-\d{2}',r'FAS-SHOES-CREAM-[NS]\.Shoe\.\d',
            r'FAS-SHOES-(?:BROWN|OXFORD)\.(?:Left|Right)',
            r'LIV.DiningChair.\d+',r'LIV.SOFA.\d+',r'LIV.TableBottle.\d+',
            r'LIV.DisplayBook.\d+',r'LIV.TeaTin.\d+.JarAssembly']
exact = {'BAR-TABLE','BAR-CAN','BAR-MINITRIPOD','COR.Roadcase','COR.Hardhat','COR.Tripod',
         'COR.CaseLooseItem','FAS-CHECKBAG-S','FAS-WAISTBAG-N','FAS-HAT-FEDORA','FAS-HAT-WIDE',
         'FAS-PERFUME','LIV.AccentChair','LIV.CoffeeTable','LIV.DiningTable',
         'LIV.OrangeStool','LIV.RoundSideTable','LIV.BroadLeafPlant',
         'LIV.CylindricalAppliance','LIV.Speaker','LIV.TableScanner','LIV.TableDeviceStack'}
selected = {name for name in objects if name in exact or any(re.fullmatch(p,name) for p in patterns)}
# The table hierarchy contains loose contents. Give every non-table child its
# own physical owner before moving the table, preserving original world poses.
table = objects['LIV.DiningTable']
table_parts = []
for child in table.GetChildren():
    name = child.GetAttribute(name_attr).Get()
    if not name:
        continue
    if name.startswith('LIV.DiningTable.') and (name.endswith('.Top') or '.Leg.' in name):
        table_parts.append(name)
    else:
        selected.add(name)
assert len(table_parts) == 5, table_parts

def mass(name):
    text=name.lower()
    if 'bottle' in text or 'teatin' in text:return 1.0
    if 'book' in text:return .6
    if 'shoe' in text:return .35
    if 'bag' in text or 'backpack' in text:return .8
    if 'hat' in text:return .3
    if 'sofa' in text:return 35.0
    if 'chair' in text:return 6.0
    if 'diningtable' in text or name=='BAR-TABLE':return 25.0
    if 'coffeetable' in text:return 12.0
    if 'sidetable' in text:return 7.0
    if 'stool' in text:return 4.0
    if 'plant' in text:return 8.0
    if 'roadcase' in text:return 18.0
    if 'tripod' in text:return 3.0
    if 'candy' in text:return .05
    return 1.5

body_records=[]
# Deepest owners first: independent bottles must leave their original table
# hierarchy before its parent becomes a dynamic body.
for name in sorted(selected,key=lambda n:len(str(objects[n].GetPath()).split('/')),reverse=True):
    prim=names()[name]
    old=prim.GetPath()
    world=UsdGeom.XformCache().GetLocalToWorldTransform(prim)
    new=Sdf.Path('/Scene/PhysicsBodies').AppendChild(prim.GetName())
    assert not stage.GetPrimAtPath(new)
    editor=Usd.NamespaceEditor(stage)
    assert editor.MovePrimAtPath(old,new)
    assert editor.CanApplyEdits(),name
    assert editor.ApplyEdits(),name
    prim=stage.GetPrimAtPath(new)
    local=world*UsdGeom.XformCache().GetLocalToWorldTransform(fixed).GetInverse()
    UsdGeom.Xformable(prim).MakeMatrixXform().Set(local)
    rb=UsdPhysics.RigidBodyAPI.Apply(prim)
    rb.CreateRigidBodyEnabledAttr(True)
    rb.CreateKinematicEnabledAttr(False)
    rb.CreateStartsAsleepAttr(True)
    UsdPhysics.MassAPI.Apply(prim).CreateMassAttr(mass(name))
    prim.SetCustomDataByKey('physics_v1:mass_status','estimated kg, adjustable; not measured from the site')
    prim.SetCustomDataByKey('physics_v1:body_rule','One physical item; component colliders form a compound; decorative parts stay attached')
    body_records.append({'source_object':name,'path':str(new),'mass_kg':mass(name),'starts_asleep':True})

scene=UsdPhysics.Scene.Define(stage,'/Scene/PhysicsScene')
scene.CreateGravityDirectionAttr(Gf.Vec3f(0,0,-1))
scene.CreateGravityMagnitudeAttr(9.80665)
physics_material=UsdShade.Material.Define(stage,'/Scene/PhysicsMaterials/EstimatedGeneralContact')
pm=UsdPhysics.MaterialAPI.Apply(physics_material.GetPrim())
pm.CreateStaticFrictionAttr(.65)
pm.CreateDynamicFrictionAttr(.5)
pm.CreateRestitutionAttr(.05)
physics_material.GetPrim().SetCustomDataByKey('estimate_note','Generic contact coefficients, not source measurements; independent of optical PBR roughness.')
colliders=[]
for prim in stage.Traverse():
    if not prim.IsA(UsdGeom.Mesh):continue
    ancestor=prim
    body=None
    while ancestor and ancestor.GetPath()!=Sdf.Path.absoluteRootPath:
        if ancestor.HasAPI(UsdPhysics.RigidBodyAPI):
            body=ancestor;break
        ancestor=ancestor.GetParent()
    UsdPhysics.CollisionAPI.Apply(prim).CreateCollisionEnabledAttr(True)
    approximation='convexHull' if body else 'none'
    UsdPhysics.MeshCollisionAPI.Apply(prim).CreateApproximationAttr(approximation)
    UsdShade.MaterialBindingAPI.Apply(prim).Bind(physics_material,materialPurpose='physics')
    colliders.append({'mesh':str(prim.GetPath()),'body':str(body.GetPath()) if body else None,'approximation':approximation})
for row in body_records:
    row['collider_count']=sum(c['body']==row['path'] for c in colliders)
    assert row['collider_count']>0,row
    prim=stage.GetPrimAtPath(row['path'])
    assert not any(p.HasAPI(UsdPhysics.RigidBodyAPI) for p in Usd.PrimRange(prim) if p!=prim)
updated=names();assert set(updated)==set(original_poses)
cache=UsdGeom.XformCache()
max_pose_error=0.0
for name,old in original_poses.items():
    current=cache.GetLocalToWorldTransform(updated[name])
    error=max(abs(old[i][j]-current[i][j]) for i in range(4) for j in range(4))
    max_pose_error=max(max_pose_error,error)
assert max_pose_error<1e-7,max_pose_error
assert sum(p.IsA(UsdGeom.Mesh) for p in stage.Traverse())==len(original_meshes)
stage.GetRootLayer().Save()
record={'stage':str(target.relative_to(ROOT)),'up_axis':'Z','meters_per_unit':1,'kilograms_per_unit':1,
        'gravity_m_s2':9.80665,'body_count':len(body_records),'bodies':body_records,
        'collision_mesh_count':len(colliders),'static_collision_meshes':sum(c['body'] is None for c in colliders),
        'dynamic_compound_child_colliders':sum(c['body'] is not None for c in colliders),
        'colliders':colliders,'all_original_object_world_transforms_preserved_max_error':max_pose_error,
        'physics_material':str(physics_material.GetPath()),
        'source_sha256':json.loads((OUT/'mesh-export-record.json').read_text())['source_sha256'],
        'limits':['Mass and friction/restitution are adjustable estimates, not measurements.',
                  'Unselected objects, structures, installed equipment, doors and display fixtures remain static colliders.',
                  'Selected furniture, bottles, individual books, bags and shoes are rigid compounds. No cloth/fluid dynamics or articulated internal mechanisms in v1.',
                  'Starts-asleep preserves initial layout until a supporting simulator wakes a body. The USDZ viewer must support USD Physics to simulate.']}
(OUT/'physics-authoring-record.json').write_text(json.dumps(record,indent=2))
print('USD_PHYSICS_AUTHORED',len(body_records),'bodies',len(colliders),'colliders',flush=True)
