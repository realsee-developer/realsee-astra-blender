# Working in this reference project

- Keep the main tutorial focused on using Realsee exports with a local AI agent and Blender. Space modeling comes before furniture and small props.
- Resolve project paths from the repository root. Discover Blender through PATH or an explicit executable argument.
- Start with `README.md`, `prompts/quickstart.en.md`, and `docs/code-map.en.md`.
- `tools/` contains the standalone preparation helpers. `scripts/` is curated case-study code with scene-specific inputs and historical output dependencies; read its navigation before executing anything.
- Do not run all case scripts or import them as a test suite. Some operate on a loaded Blender scene or write output at module load time.
- Preserve original input data and existing models. Use a separate output copy for experiments and edit tests.
- Keep input data, environments, credentials, intermediate models, and render sequences out of Git. New public case scripts must be added to the explicit list in `.gitignore` and documented.
- For preparation-tool changes, run `python3 -m unittest discover -s tests -v` and `python3 tools/check_public_tree.py`. For Blender execution changes, also run `python3 tools/project.py smoke` when Blender is available.
- Report checks actually executed. A synthetic environment test does not establish full reconstruction or visual equivalence.
- Public preview assets and Git LFS models have separate material/provenance notes in `docs/data-and-license.md`. Do not publish external data or credentials as a side effect of testing.
