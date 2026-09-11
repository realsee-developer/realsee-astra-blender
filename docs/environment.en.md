# Environment setup

[简体中文](environment.md) | English

## Quick start

The preparation tools use the Python 3.10+ standard library. They look for `blender` on PATH, or accept an executable path with `--blender`. Symbolic links are resolved to the actual executable so Blender can find its own resources.

```sh
python3 tools/project.py doctor
python3 tools/project.py smoke
```

`smoke` uses three separate background processes to create a test wall, reopen and edit it, then reopen it again to check the result. It writes to a new `output/smoke-*/` directory and leaves existing reconstruction scenes untouched.

## Case-study analysis code

The dependency versions from this project's analysis environment are recorded in [requirements-analysis.txt](../requirements-analysis.txt). To explore the CAD, point-cloud, and image-processing code in `scripts/`, install them in a separate virtual environment:

```sh
python3 -m venv .venv-analysis
.venv-analysis/bin/python -m pip install -r requirements-analysis.txt
```

These commands are for macOS/Linux. On Windows, the virtual environment's Python executable is `.venv-analysis/Scripts/python.exe`. This is a snapshot of the case-study dependencies; use the [code map](code-map.en.md) to choose the parts you want to explore.

Blender's `bpy`, `bmesh`, and `mathutils` run in Blender's own Python environment. Libraries installed in a system virtual environment are not automatically available there. Additional libraries used by case scripts, such as SciPy, Pillow, and USD `pxr`, must be available in the environment running those scripts. Video encoding also uses FFmpeg/ffprobe.

## Checks performed

During repository preparation, the preparation tools and the three-process editing smoke test were run locally with Blender 5.2.1 LTS. The analysis dependencies were taken from the existing project environment. The full scene reconstruction, walkthrough rendering, and historical repair scripts were not rerun during that preparation. Automated checks discover tests only under `tests/`; they do not import the case-study scripts.
