# Space modeling: a ready-to-use prompt

[简体中文](quickstart.zh.md) | English

Put your Realsee exports in the project's `data/` folder. Open the project in an Astra session that can access local files and run Blender, then send the prompt below. CAD, point clouds, panoramas, and textured scans serve different purposes; keep the downloaded folder structure intact.

```text
Use the current project directory as PROJECT_ROOT. Inspect the Realsee exports in data/ and discover the Blender executable installed locally.

Reconstruct the scanned space as an editable, native Blender scene. Run Blender and do the modeling. Focus on the whole space: first understand how the areas connect, then build the walls, floors, ceilings, doors, windows, and openings. Add the main furniture afterward, leaving small objects until later.

Review the available CAD, point clouds, scan models, and panoramas, and align their positions and scale. Model only spaces evidenced by the inputs. Record unclear areas instead of inventing additional rooms.

Create walls, floors, ceilings, doors, and windows as separately selectable and editable native objects, organized by area. Use the photos to reproduce the main surface materials and light sources. Keep a copy of the original scan as a reference, hidden by default.

Show previews of the overall space and its main areas so I can compare them with the source and request changes. Continue refining the scene from that feedback; do not stop at a plan or a script.

Save the final scene as output/reconstruction_native.blend. Reopen the saved file and actually edit a wall section and a door to confirm they can be changed independently. Then provide the model and preview images.
```

After reviewing the first previews, you can follow up with:

> Hide the furniture and show me a plan view of the entire space, then show the connections from the entrance to each room. Fix the walls, openings, and ceilings I point out, then restore the furniture and materials.

For the full case requirements, see the [detailed English prompt](../ASTRA_BLENDER_GOAL_PROMPT.txt). See [data and licensing](../docs/data-and-license.en.md) for how local inputs and public files are organized.
