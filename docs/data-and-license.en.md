# Data and licensing

[简体中文](data-and-license.md) | English

This repository shares methods, prompts, and code for reconstructing a space with Realsee exports, Astra, and Blender. Code, prompts, and original documentation use the [MIT license](../LICENSE).

## Where files belong

| Content | Arrangement |
| --- | --- |
| Prompts, code, and original documentation | Published in Git under MIT. |
| Case previews in `docs/assets/` | Authorized for public sharing so readers can see the modeling results; see the material licensing scope below. |
| Final models and video | The reviewed public copies are available through Git LFS; see [case files](releases.en.md) for files and download instructions. |
| `data/` | Authorized original case inputs through Git LFS; see the [data guide](../data/README.md). Other users’ private exports remain excluded unless explicitly authorized and reviewed for publication. |
| `output/` and `research/` | Local models, intermediate files, analysis records, and logs; not committed to Git. Public content is selected and prepared separately. |
| Virtual environments, caches, and credential files | Kept locally and not committed to Git. |

To try the workflow, download the case inputs using the [data guide](../data/README.md), or add your own CAD, point clouds, panoramas, and scan models without overwriting the published files. Preserve the original directories and the relative locations of models and textures, then use the [quick-start prompt](../prompts/quickstart.en.md).

The original case inputs contain 396 files totaling 6,079,895,800 bytes (about 5.66 GiB), excluding `.DS_Store`. They are authorized for public sharing as-is, including on-site QR codes. The existing previews, final models, and video remain the previously reviewed, redacted copies: unknown-purpose on-site QR codes were removed, and some packaging text and photographic colors in the scan reference were omitted. Publishing the original inputs does not replace those copies.

## Code and materials have separate licensing scopes

MIT applies to this project's code, prompts, and original documentation text. It does not automatically change the rights to original Realsee exports, photographic textures, third-party generated assets, or other third-party content. The original case inputs, previews, and final models authorized for public sharing can serve as case demonstrations and learning references. Their material rights remain with the respective sources; publication does not grant a new commercial sublicense. See the [source data guide](../data/README.md) and the [case asset notice](../artifacts/NOTICE.txt). Neither the source dataset nor the entire model package is labeled MIT.

The writing process drew on [ComposioHQ's Content Research Writer](https://github.com/ComposioHQ/awesome-claude-skills/blob/master/content-research-writer/SKILL.md). This repository links to the source without redistributing the full skill text. External tools and dependencies retain their own licenses.

The browser GLB is derived solely from the reviewed public USDZ and follows the same asset notice. The website includes Three.js under MIT (license distributed at `vendor/three/LICENSE`) and the Draco decoder under the [Apache 2.0 license](../site/DRACO_LICENSE.txt).
