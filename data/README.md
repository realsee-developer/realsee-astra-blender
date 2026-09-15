# Original case data

English | [简体中文](README.zh-CN.md)

These are the original Realsee exports used by the [editable Blender space project](../README.md): **396 files, 6,079,895,800 bytes (about 5.66 GiB)**. The original folder structure and file bytes are preserved. Finder `.DS_Store` files are excluded; the READMEs, manifest, and checksums are publication metadata added here.

## Download

Install Git LFS, then clone without automatically downloading every large artifact:

```sh
git lfs install
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/realsee-developer/realsee-astra-blender.git
cd realsee-astra-blender
git lfs pull --include="data/**" --exclude=""
```

In an existing checkout, run the last command from the repository root. GitHub's source ZIP may contain LFS pointer files; use Git LFS to obtain the actual inputs. The full source-data checkout uses about 5.66 GiB, with additional disk space for the local LFS cache. LFS deduplicates identical content across model export folders.

To begin with a smaller set, download CAD, one textured mesh format, and the panoramas:

```sh
git lfs pull --include="data/cad.dwg,data/cad.dxf,data/model/obj-high-resolution-model/**,data/panorama/**" --exclude=""
```

Add point clouds, cube faces, RAW, or other formats when the modeling task needs them. Keep models and their referenced textures together. Put your own datasets in a separate project or preserve a separate copy before replacing any case inputs.

## Contents

| Input | Purpose |
| --- | --- |
| `cad.dwg`, `cad.dxf`, `schematic-floorplan_floor_1.png` | Plan, layout, dimensions, and structural reference |
| `point-cloud.e57`, `point-cloud.ply` | Captured 3D surfaces; E57 also contains scan/image information |
| `model/` | Basic and high-resolution OBJ, FBX, GLB, and glTF exports with their resources |
| `panorama/` | Eight original panorama JPEGs |
| `cube-map/` | 48 cube-face JPEGs, six per viewpoint |
| `panorama-raw/` | Eight DNG originals, about 4.42 GiB in total |
| `model-orthogonal-image/` | Six rendered plan/elevation reference images |
| `gen-vr-video.mp4` | Source-space video reference, separate from the reconstructed Blender walkthrough |

Different mesh formats describe the same captured space; do not import them as separate rooms. Start with the [quickstart](../prompts/quickstart.en.md). This dataset supplies the source evidence; the selected historical scripts can also require local measurement records and intermediate checkpoints, as explained in the [code map](../docs/code-map.en.md).

## Integrity and sharing scope

[manifest.json](manifest.json) records each source file's path, size, and SHA-256. From the repository root, verify a complete download with:

```sh
shasum -a 256 -c data/SHA256SUMS
```

The originals are publicly shared as-is with the project owner's authorization, including photographed QR codes and original image metadata. Existing models and video in `artifacts/` remain the previously prepared public copies; their earlier QR removals are unchanged.

The case data is provided for demonstration and learning reference. The repository's MIT license covers code, prompts, and original documentation; it does not relicense source scans, photographs, depicted brands, or third-party materials. See [data and licensing](../docs/data-and-license.en.md) for the distinction.
