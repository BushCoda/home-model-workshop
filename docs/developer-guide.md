---
layout: page
title: Developer Guide
permalink: /developer-guide/
---

<div class="hero-card">
  <h1>Developer Guide</h1>
  <p>This guide explains the add-on structure, the core data model, and the main workflow paths used by Home Model Workshop. It is intended for development, debugging, and future maintenance work.</p>
  <blockquote>
    <p><strong>Beta note:</strong> Home Model Workshop 0.1.0 was built and smoke-tested in Blender 5.2.2. Blender 4.2.0 is the declared minimum version in the extension manifest, but compatibility with Blender 4.2 has not been independently verified.</p>
  </blockquote>
</div>

## Overview

Home Model Workshop follows a layout-first workflow:

1. Create or import room footprints.
2. Arrange the footprints manually.
3. Validate the plan.
4. Build the generated house model.
5. Place opening frames and rebuild to apply cutouts.

The room footprints are the source of truth. The generated house model is derived output and can be rebuilt at any time.

## Add-on structure

The add-on is organized around the Blender extension manifest, the main add-on module, and a documentation site under `docs/`.

### Main pieces

- **`blender_manifest.toml`** — extension metadata, versioning, and minimum Blender requirements
- **`__init__.py`** — add-on registration, operators, panels, properties, and core behavior
- **`docs/`** — GitHub Pages documentation site for users and maintainers
- **`scripts/build-release.ps1`** — release ZIP packaging helper
- **`.github/ISSUE_TEMPLATE/`** — structured issue templates for bugs and feature requests

## Data model

Home Model Workshop stores layout data in scene objects and custom properties.

### Core object groups

- **Room footprints** — separate editable rectangular objects representing room blocks
- **Shape guide** — the visual Box, L, H, or U guide used for staging
- **Generated model** — the built floors, walls, and optional labels
- **Opening frames** — manual door and window frames used to drive cutouts

### Behavioral rules

- Footprints are axis-aligned rectangles.
- Rotating a footprint is unsupported.
- Imported meshes are reduced to world-space XY bounds.
- Open gaps remain open.
- Shared edges produce one wall.
- Overlapping rooms block a rebuild.
- Duplicate room IDs are repaired during validation or build.

## UI sections

The add-on’s N-panel is divided into the following sections:

- **Quick Start & Help** — overview and workflow summary
- **House & Construction** — guide size, wall dimensions, and floor thickness
- **Room Selection & Starting Guide** — starter room selection and guide shape
- **Custom Room Program** — future starter-plan room list
- **Import Existing Layout** — convert selected mesh objects into footprints
- **Model Output** — build options and generated model behavior
- **Doors & Windows** — opening frame placement and cutouts

These sections are intended to support a manual layout workflow, not automated architectural design.

## Validation and rebuild behavior

Validation is currently focused on structural layout problems:

- room overlaps
- duplicate room IDs
- opening-guide issues

It does not guarantee:

- room connectivity
- hallway access
- circulation quality
- architectural correctness

A failed rebuild keeps the previous generated model in place.

## Import workflow

When selected mesh objects are imported as rooms:

1. The add-on reads each object’s world-space XY bounds.
2. It creates a rectangular footprint for each object.
3. The original objects remain in the scene.
4. Rotated or irregular meshes are simplified to axis-aligned rectangles.

This behavior is intentionally conservative so imported geometry can be edited using the same room-footprint workflow as starter plans.

## Generated model workflow

The generated house model is derived from the current footprint arrangement.

- Rebuilds replace the generated floors, walls, and optional labels.
- Room footprints remain editable after building.
- Opening frames stay separate so they can be adjusted before rebuild.
- Frames must align with matching generated walls to produce cutouts.

## Development notes

Keep documentation and user-facing language aligned with the current add-on behavior.

### Important constraints

- Do not describe the tool as an automatic house designer.
- Keep the beta caveat visible in public-facing docs.
- Use the exact Blender UI labels when documenting controls.
- Avoid promising connectivity or architectural validation that the add-on does not currently provide.

## Roadmap alignment

The current direction emphasizes:

- clearer layout validation feedback
- more dependable opening placement
- better support for practical room planning
- improved documentation and usability

Future-feature descriptions should remain clearly marked as planned direction rather than current behavior.

## Related documentation

- [Home]({{ '/' | relative_url }})
- [Getting Started]({{ '/getting-started/' | relative_url }})
- [User Guide]({{ '/user-guide/' | relative_url }})

## Notes for maintainers

The docs site is published from the repository’s `/docs` folder. Keep the Jekyll front matter intact and preserve the `relative_url` style for internal links.
