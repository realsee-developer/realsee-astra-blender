# Realsee × GPT-6 Astra × Blender

[简体中文](README.md) | English

[Read the website](https://realsee-developer.github.io/realsee-astra-blender/) · [Original Realsee space](https://realsee.ai/O3eeL2R3)

Use Realsee exports as reference and let GPT-6 Astra run Blender locally to build a 3D space you can keep editing.

This repository shares the prompts, tutorial, space-modeling code, and previews from a real project. The focus is on walls, floors, ceilings, doors, windows, and connections between rooms. Furniture and small objects come afterward.

![Reconstructed space](docs/assets/overview.jpg)

## Start here

1. Install [Blender](https://www.blender.org/download/) and use an Astra session that can read local files and run commands. This case used Codex and Blender 5.2.1 LTS.
2. Create `data/` in this repository. Add your Realsee models and textures, point clouds, panoramas, CAD files, and other exports, keeping their original folder structure.
3. Open the project in Codex and send Astra the [quickstart prompt](prompts/quickstart.en.md).
4. Review the overall space first, then ask for changes. Save the finished project as `output/reconstruction_native.blend`.

The [illustrated tutorial](docs/tutorial.en.md) walks through downloading the inputs, writing the prompt, and refining the result. You can also use the [detailed English prompt](ASTRA_BLENDER_GOAL_PROMPT.txt) or its [Chinese version](ASTRA_BLENDER_GOAL_PROMPT.zh.txt). Those prompts retain the input descriptions from this case; ask Astra to adapt them to your own data.

## Check your local setup

The preparation tools use the Python 3.10+ standard library. You do not need the analysis dependencies to run them. From the repository root:

```sh
python3 tools/project.py doctor
python3 tools/project.py inventory
python3 tools/project.py smoke
```

- `doctor` finds Blender and reads its version.
- `inventory` lists the contents of `data/` and writes `output/source-inventory.json`.
- `smoke` creates a test wall in a new output directory. Three separate Blender processes save it, reopen and edit it, and reopen it again to check the edit.

`smoke` checks the environment without touching existing models. Reconstruction starts with your source files and prompt. If Blender is not on PATH, add `--blender` followed by its executable path to `doctor` or `smoke`. See the [environment guide](docs/environment.en.md) for analysis dependencies.

## Repository contents

| Directory | Contents |
|---|---|
| [prompts/](prompts/quickstart.en.md) | A ready-to-use prompt focused on modeling the space |
| [docs/](docs/tutorial.en.md) | Tutorial, code guide, previews, and artifact notes |
| [tools/](tools/project.py) | Environment checks, input inventory, and Blender save/edit smoke test |
| [scripts/](scripts/README.en.md) | Selected reference code for source analysis, modeling, comparisons, animation, and export |
| [artifacts/](docs/releases.en.md) | Native scenes, walkthrough video, USDZ, and material notices; large files are provided through Git LFS |
| [tests/](tests/test_project.py) | Lightweight tests for the preparation tools |
| `data/`, `research/`, `output/` | Local inputs and generated files, ignored by Git |

The scripts record the implementation for this particular space. Some use specific object names, coordinates, and historical intermediate files. Follow the [code guide](docs/code-map.en.md) for reading order and prerequisites. With your own inputs, ask Astra to adapt the methods to your space.

## See the results

![Plan view of the native Blender scene](docs/assets/plan.png)

The case produced a native `.blend`, an editable walkthrough project, an 85-second video, and an initial USDZ export. Code, tutorials, previews, models, and video are available. Large files are provided through Git LFS; see the [artifact list](docs/releases.en.md).

The full original scan and panorama dataset stays local. The repository currently includes curated code, articles, previews, and public deliverables. Code, prompts, and original documentation use the [MIT license](LICENSE). See [data and licensing](docs/data-and-license.en.md) for the scope of the case assets.

## Development and contributions

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_public_tree.py
```

Neither check requires Blender or the original scene data. If you change how Blender is invoked, also run `smoke`. Contributions to input organization, modeling prompts, and tooling are welcome; see [CONTRIBUTING.en.md](CONTRIBUTING.en.md).
