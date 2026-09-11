"""Package the authored scene; verification runs in a separate fresh process."""
from pathlib import Path
from pxr import UsdUtils,Sdf
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'output/usdz-v1/scene_physics.usdc'
target=ROOT/'output/reconstruction_physics_v1.usdz'
assert not target.exists()
assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(source)),str(target))
print('USDZ_PACKAGE_CREATED',target.stat().st_size,flush=True)
