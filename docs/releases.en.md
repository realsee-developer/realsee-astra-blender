# Case files and Git LFS

[简体中文](releases.md) | English

The [original case inputs](../data/README.md) are also available through Git LFS: 396 files, about 5.66 GiB. Use them to start your own reconstruction. The files below are the reconstructed models and video; their downloads are separate from the source data.

## Case files

The following public deliverables are available through Git LFS. Click a filename to download it from its GitHub file page, or follow the cloning instructions below.

| File | Size | Purpose |
|---|---:|---|
| [reconstruction_native.blend](../artifacts/reconstruction_native.blend) | 252 MB | Native space project with separate geometry, materials, packed textures, and a scan reference hidden by default |
| [reconstruction_roaming.blend](../artifacts/reconstruction_roaming.blend) | 252 MB | Walkthrough project with its camera route and keyframes |
| [reconstruction_roaming.mp4](../artifacts/reconstruction_roaming.mp4) | 44 MB | An 85-second walkthrough at 24 fps, 1280×720 |
| [reconstruction_physics_v1.usdz](../artifacts/reconstruction_physics_v1.usdz) | 560 MB | First exchange-file version with rigid bodies, collisions, and material settings |
| [reconstruction_web.glb](../artifacts/reconstruction_web.glb) | 17.2 MB | Lightweight browser preview derived from the public USDZ, with ceilings hidden and geometry/textures compressed |

The homepage embeds the original tour, an interactive 3D model, and the walkthrough video. The GLB is a visual preview; use the Blender projects for component editing and the full USDZ for its authored physics data.

The total is approximately 1.13 GB. File sizes and SHA256 hashes are listed in [manifest.json](../artifacts/manifest.json) and [SHA256SUMS](../artifacts/SHA256SUMS).

## Downloading models and video

Install [Git LFS](https://git-lfs.com/), then download the reconstructed models and video:

```sh
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/realsee-developer/realsee-astra-blender.git
cd realsee-astra-blender
git lfs install --local
git lfs pull --include='artifacts/**' --exclude=''
```

For an existing checkout, run the last two commands from the repository root. To download modeling inputs, follow the [source-data guide](../data/README.md).

Then open `artifacts/reconstruction_native.blend` directly in Blender. Save your own edited versions under the local `output/` directory. USDZ dynamics require software that supports USD Physics; ordinary model viewers are mainly for viewing the geometry.

If a model in a downloaded ZIP contains only a few lines of text, it is an LFS pointer. Clone with Git and run the commands above, or download the actual file from its GitHub file page. Whether GitHub source archives include LFS objects depends on repository settings; see the [official documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage).

On-site QR codes have been removed from the public models. Paper and packaging retain their geometry, with the affected materials changed to solid colors. Scan textures containing QR codes have also been removed, while the hidden scan reference retains its geometry. The corresponding areas in the video are covered with local masks.

The public models include the remaining packed on-site textures and the hidden scan reference. The [original point clouds, panoramas, RAW, and other exports](../data/README.md) are shared as-is in `data/`, including on-site QR codes. The models and video above retain their existing redactions. See [data and licensing](data-and-license.en.md) for the scope of the materials.

## Updating files as a maintainer

`.gitattributes` configures LFS for `.blend`, `.usdz`, `.mp4`, and `.glb` files under `artifacts/`. `.gitignore` allows only reviewed filenames. Update the allowlist and checksums when adding a deliverable.

When updating a deliverable, place the reviewed public copy in `artifacts/`, update `manifest.json` and `SHA256SUMS`, then stage and check it:

```sh
git add .gitattributes artifacts/
git lfs ls-files
python3 tools/check_public_tree.py
```

The checker confirms that the index contains LFS pointers and verifies the size and SHA256 of the working-tree files. Source checks work with pointers only. The website build fetches just the web GLB and MP4, leaving the large Blender projects and USDZ out of its download. Once verified, commit and push when ready; the Git LFS pre-push hook uploads the corresponding large files. See the [official GitHub setup guide](https://docs.github.com/en/repositories/working-with-files/managing-large-files/configuring-git-large-file-storage).
