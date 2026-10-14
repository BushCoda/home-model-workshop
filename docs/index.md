---
layout: page
title: Home
permalink: /
---

# Home Model Workshop

**A Blender add-on for guided room layout and editable house-model blockouts.**

Home Model Workshop helps you start from a room program and a visual placement guide, arrange the rooms yourself, validate the layout, and build floors and walls from the room footprints. It is designed as a blockout and layout tool, not an automatic architectural designer.

> **Beta note:** Home Model Workshop 0.1.0 was built and smoke-tested in Blender 5.2.2. Generated models are editable blockouts and should be reviewed in Blender before further use. Blender 4.2.0 is the declared minimum version in the extension manifest, but compatibility with Blender 4.2 has not been independently verified.

## Start here

- [Getting Started]({{ '/getting-started/' | relative_url }}) — install the add-on and build your first layout
- [User Guide]({{ '/user-guide/' | relative_url }}) — full reference for every panel section and workflow
- [Developer Guide]({{ '/developer-guide/' | relative_url }}) — implementation overview and behavior contracts

## What it does

- Creates editable room footprints from a starter room program or imported meshes
- Uses Box, L, H, and U visual placement guides
- Lets you arrange rooms manually before building the model
- Validates overlaps and opening-guide issues before rebuilds
- Builds floors, walls, and optional room labels from the room footprints
- Lets you place door and window frames manually and rebuild to apply cutouts

## Typical workflow

1. Install and enable the add-on in Blender.
2. Choose a starter guide shape and room set.
3. Create the starter plan.
4. Move and resize the room footprints into the layout you want.
5. Validate the layout.
6. Build or rebuild the house model.
7. Add door and window frames after the walls are built, then rebuild to apply cutouts.

## Notes

- The guide is visual only; the room footprints define the final layout.
- Rooms do not need to fill the guide.
- Hallways and circulation areas are placed manually.
- Open gaps stay open and shared room edges create one wall.

For detailed instructions, continue to the [Getting Started guide]({{ '/getting-started/' | relative_url }}).
