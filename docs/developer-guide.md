---
layout: page
title: Developer Guide
permalink: /developer-guide/
---

# Home Model Workshop Developer Guide

Home Model Workshop is a single-module Blender add-on. Its core data is ordinary Blender objects with custom properties; the add-on can therefore rebuild geometry from a saved or manually edited room layout.

## Module map

The implementation is in `__init__.py`.

| Area | Main symbols | Responsibility |
| --- | --- | --- |
| Scene/object helpers | `get_or_create_collection`, `make_box`, `room_bounds` | Create output collections, mesh boxes, and evaluate room bounds in world space. |
| Starter-plan inputs | `HF_CustomRoomDefinition`, `HF_Settings`, `build_room_program` | Store scene settings and turn standard and custom room choices into named room records. |
| Starter footprints and guide | `starter_rooms`, `layout_guide_outline`, `create_layout_guide`, `create_room_footprint` | Stage separate room rectangles and create a separate wire outline for the selected shape. |
| Validation and topology | `collect_room_records`, `room_overlap_pairs`, `touching_edge_rooms`, `make_wall_segments` | Read room objects, repair missing/duplicate IDs, reject footprint overlaps, and derive unique wall segments from room edges. |
| Openings | `create_opening_frame`, `find_opening_host`, `opening_segment_match`, `HF_OT_add_opening` | Place editable frame objects and match them to generated wall segments during rebuild. |
| Build and project operations | `HF_OT_build_model`, `HF_OT_validate_project`, `HF_OT_clear_model`, `HF_OT_clear_openings` | Validate, build, and clear generated geometry or opening guides. |
| User interface | `HF_PT_main_panel`, `HF_Settings.ui_show_*` | Draw the N-panel and retain each section's expanded state in the scene. |
| Add-on lifecycle | `classes`, `register`, `unregister` | Register classes and scene properties with Blender. |

## Data flow

1. `build_room_program(settings)` reads standard room controls and the custom-room list.
2. `starter_rooms(...)` gives each room a default rectangle and leaves a placement gap between the staged footprints. `layout_shape` is used to draw the guide, not to partition rooms.
3. Each room footprint is a mesh object in `HF_Room_Layout` with `houseforge_room`, `hf_room_id`, `room_name`, and `hf_room_zone` properties. The primary-suite grouping is stored in `hf_suite_id` where applicable.
4. `collect_room_records()` calculates world-space XY bounds and ensures each included footprint has a unique room ID. Duplicating a Blender object copies its properties, so duplicates must be detected and assigned fresh IDs before topology is built.
5. `room_overlap_pairs()` compares the rectangles. A non-zero intersection beyond `EPS` blocks both validation and model generation. The build check runs before the old generated collection is cleared.
6. `make_wall_segments()` splits candidate boundaries at footprint coordinates. `touching_edge_rooms()` records which room lies on each side. An occupied boundary interval becomes one segment; it is marked internal when rooms touch on both sides. Empty regions between edges do not become walls.
7. `HF_OT_build_model` creates optional room slabs, walls and labels in `HF_Generated_Model`, applies valid opening frames, and joins generated mesh geometry into `HF_House_Model`.

## Important behavior contracts

- Room footprints are interpreted as axis-aligned XY rectangles from `matrix_world` bounds. Rotation is unsupported; non-rectangular input meshes are reduced to bounding rectangles when imported.
- The outline mesh in `HF_Layout_Guide` is visual-only and must never be included in `collect_room_records()` or wall generation.
- Gaps are intentional. Do not fill empty space with walls or floors implicitly.
- Shared wall edges should be emitted once, independent of which adjacent room is visited first.
- Any detected room overlap must stop a build before clearing the existing generated model. Keep the names and object identifiers available in the error popup to distinguish repeated room labels.
- Opening frames are independent objects. Keep their IDs unique and preserve their host metadata through rebuilds unless a frame is explicitly reattached.
- UI expansion flags (`ui_show_*`) belong to `HF_Settings`; they are scene state, not global preferences.

## Adding or changing a feature

- Add user-facing settings to `HF_Settings` with a concise Blender `name` and `description`.
- If a new operator is user-invokable, provide a useful `bl_label`, `bl_description`, clear reports, and register it in `classes`.
- Keep the N-panel grouped with `HF_PT_main_panel.section(...)`. Put controls in the matching section and add usage guidance to the Quick Start & Help area and user guide.
- Preserve the three separate collections for footprints, visual guide, and generated output.
- When changing a layout/build behavior, update the user guide and this data-flow/behavior documentation together.
- Update both `bl_info["version"]` and `blender_manifest.toml` when packaging a release. Keep the packaged `__init__.py` identical to the repository root `__init__.py`.

## Compatibility

The extension manifest declares Blender 4.2 as the minimum version and is developed/tested against Blender 5.2.2. The extension ID, operator IDs, and scene-property keys retain the legacy `houseforge` prefix to preserve compatibility with existing installs and saved scenes. UI grouping uses boolean properties and disclosure-arrow buttons stored on the scene so the collapsible sections work in the target Blender runtime.
