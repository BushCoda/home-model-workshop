---
layout: page
title: Home Model Workshop
permalink: /
---

# Build a house model, room by room

Home Model Workshop is a Blender add-on for arranging editable room footprints and turning the layout into a simple 3D house blockout. You choose a starting room program, arrange the rooms yourself, validate the plan, and build walls and floors when you are ready.

> **Beta 0.1.0:** Generated plans are editable blockouts. Review dimensions, openings, and wall joins in Blender before using a model for further design work.

## Start here

- [Getting Started]({{ '/getting-started/' | relative_url }}): install the beta and create your first room layout.
- [User Guide]({{ '/user-guide/' | relative_url }}): understand every panel section and layout rule.
- [Roadmap]({{ '/roadmap/' | relative_url }}): see planned features and quality improvements.
- [Doors and Windows]({{ '/user-guide/' | relative_url }}#adding-doors-and-windows): place opening frames and generate cutouts.
- [Troubleshooting]({{ '/user-guide/' | relative_url }}#troubleshooting): resolve common validation and opening issues.
- [Developer Guide]({{ '/developer-guide/' | relative_url }}): inspect the add-on structure and behavior contracts.

## How the workflow works

1. Choose the rooms you need and create separate room footprints with a visual shape guide.
2. Move and resize the rooms into the arrangement you want. The guide is only a reference.
3. Validate the layout. Overlaps are reported; open gaps are allowed.
4. Build the model. Shared edges create one wall, and opening frames create cutouts when you rebuild.

## What the add-on creates

- Rectangular, editable room footprints.
- Box, L, H, and U placement guides.
- Floors and walls derived from the room footprints.
- Manually placed door and window opening frames.

The add-on does not automatically design a finished architectural plan. Hallways, room placement, and opening positions are user-directed.
