# Data and licensing

[简体中文](data-and-license.md) | English

This repository shares methods, prompts, and code for reconstructing a space with Realsee exports, Astra, and Blender. Code, prompts, and original documentation use the [MIT license](../LICENSE).

## Where files belong

| Content | Arrangement |
| --- | --- |
| Prompts, code, and original documentation | Published in Git under MIT. |
| Case previews in `docs/assets/` | Authorized for public sharing so readers can see the modeling results; see the material licensing scope below. |
| Final models and video | The reviewed public copies are available through Git LFS; see [case files](releases.en.md) for files and download instructions. |
| `data/` | Your own Realsee exports; not committed to Git. |
| `output/` and `research/` | Local models, intermediate files, analysis records, and logs; not committed to Git. Public content is selected and prepared separately. |
| Virtual environments, caches, and credential files | Kept locally and not committed to Git. |

To try the workflow, place your CAD, point clouds, panoramas, and scan models in `data/`, preserving the relative locations of models and textures, then use the [quick-start prompt](../prompts/quickstart.en.md). The complete original scans from this case are not included. On-site QR codes of unknown purpose have been removed from the public copies; as a result, some packaging text and photographic colors in the scan reference are omitted.

## Code and materials have separate licensing scopes

MIT applies to this project's code, prompts, and original documentation text. It does not automatically change the rights to original Realsee exports, photographic textures, third-party generated assets, or other third-party content. The previews and final models authorized for public sharing can serve as case demonstrations and learning references. Use of their materials is governed by the respective sources and the [case asset notice](../artifacts/NOTICE.txt); the entire model package is not labeled MIT.

The writing process drew on [ComposioHQ's Content Research Writer](https://github.com/ComposioHQ/awesome-claude-skills/blob/master/content-research-writer/SKILL.md). This repository links to the source without redistributing the full skill text. External tools and dependencies retain their own licenses.

The browser GLB is derived solely from the reviewed public USDZ and follows the same asset notice. The website includes Three.js under MIT (license distributed at `vendor/three/LICENSE`) and the Draco decoder under the [Apache 2.0 license](../site/DRACO_LICENSE.txt).
