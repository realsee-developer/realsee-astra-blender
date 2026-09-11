# Contributing

[简体中文](CONTRIBUTING.md) | English

Contributions to the getting-started documentation, prompts, preparation tools, and space-modeling methods are welcome. Describe what changed, which inputs you used, and how you checked the results.

- Put new general-purpose preparation features in `tools/` and their tests in `tests/`.
- `scripts/` contains case-study code. Provide the scene data described in its guide before running it. Do not treat its historical `test_*.py` checks as an automated unit-test suite.
- Use project-relative paths. Discover Blender through PATH or an explicit argument; do not hard-code personal machine directories.
- Do not commit your own `data/`, output models, rendered frame sequences, virtual environments, or access credentials. Put previews in `docs/assets/`. Put reviewed public deliverables in `artifacts/`, update the `.gitignore` allowlist, and use Git LFS.
- This repository uses a public allowlist for `scripts/`. When adding a case script, update both `.gitignore` and the [script guide](scripts/README.en.md).

Before submitting, run:

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_public_tree.py
```

If your change affects Blender execution, also run `python3 tools/project.py smoke`. Report the checks you actually ran, and do not describe scene validation as passed if it was not performed.

## Maintaining the bilingual website

Chinese and English documents live alongside each other. Update the matching translation when changing content. GitHub Pages builds directly from these Markdown files. Page mappings and homepage copy are in [tools/build_site.py](tools/build_site.py); styles are in [site/style.css](site/style.css).

With Node.js, npm, and Git LFS installed, build and preview from the repository root (macOS/Linux):

```sh
python3 -m venv .venv-site
.venv-site/bin/python -m pip install -r requirements-site.txt
npm ci --prefix site --ignore-scripts
git lfs pull --include="artifacts/reconstruction_web.glb,artifacts/reconstruction_roaming.mp4" --exclude=""
.venv-site/bin/python tools/build_site.py
python3 tools/check_site.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory output/site
```

Then open `http://127.0.0.1:8000/`. On Windows, replace `.venv-site/bin/python` with `.venv-site/Scripts/python.exe`.

Generated content goes into `output/site/`, which is rebuilt on each run. The builder copies the three public images, web GLB, walkthrough MP4, styles, viewer code, and the required Three.js runtime files. Site checks cover links, language switches, embedded media, and regional guide URLs. Raw inputs, full Blender projects, and USDZ are excluded from the website package.

English guides target overseas readers (`www.realsee.ai`); Simplified Chinese guides target mainland China (`www.realsee.com`). Keep the UTM convention: `utm_source=realsee-astra-blender`, `utm_medium=referral`, `utm_campaign=editable-space`, and a language/entry-specific `utm_content` such as `en-tutorial-model`.

To regenerate the browser preview from the reviewed public USDZ, run `python3 tools/prepare_web_preview.py` with Python 3.11+, Pillow, and Blender on PATH. Update the artifact manifest and checksums afterward. The script hides ceilings and reduces detail for browser viewing; the source USDZ and Blender projects remain unchanged.

Pull requests run the checks and website build. Pushes to `main` deploy GitHub Pages after all checks pass. Deployment uses GitHub Actions; select **GitHub Actions** as the build source in the repository's Pages settings.
