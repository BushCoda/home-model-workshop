---
layout: page
title: User Guide
permalink: /user-guide/
---

# Home Model Workshop User Guide

Home Model Workshop creates an editable house blockout from rectangular room footprints. You arrange the rooms; the selected Box, L, H, or U shape is a visual placement guide. The guide does not constrain wall or floor generation.

## Quick start

1. Open the **Home Model Workshop** tab in the 3D Viewport's N-panel.
2. Expand **House & Construction** to set the guide's width and depth, wall height, wall thickness, and floor thickness.
3. In **Room Selection & Starting Guide**, choose a shape and select the standard room types and counts.
4. Optionally open **Custom Room Program** and add named rooms to the next generated starter plan.
5. Choose **Create Rooms & Shape Guide**. If a room layout already exists, confirm that you want to replace its footprints.
6. Move and resize the separate room footprints into the arrangement you want. Keep them axis-aligned; do not rotate them.
7. Click **Validate Project** to check the layout, then **Build / Rebuild House Model**.

The first generated positions are a starting arrangement. You can change their positions and dimensions freely before building. If you need another room after generation, use **Add Room to Layout**; it asks for a name, width, and depth.

## N-panel sections

Each section has an arrow control and remembers its open or closed state in the current `.blend` scene.

### Quick Start & Help

Shows a short version of the workflow and the main placement rules.

### House & Construction

- **Workflow**: choose Architecture or Game Asset. This setting is currently descriptive and does not change generated geometry.
- **House Width / Depth**: set the dimensions of the visual guide. Width also controls when the initial room staging arrangement wraps to a new row.
- **Wall Height / Thickness**: dimensions used when building walls.
- **Floor Thickness**: slab thickness used for room floors.

The selected guide shape uses these width and depth values. They do not scale, clip, or constrain individual room footprints.

### Room Selection & Starting Guide

Choose the Box, L, H, or U guide shape, then select the standard rooms to include in the next starter plan. Ensuite and Walk-in Robe are associated with the first bedroom and are disabled when the bedroom count is zero.

The starter rooms use separate, practical default dimensions and are spaced apart for manual placement. The guide is a non-rendering outline in its own collection. Some rooms may start outside the guide when the requested room program is larger than the guide; move them into the desired arrangement before building.

The starter dimensions are initial sizing suggestions, in metres:

| Room | Initial width x depth |
| --- | ---: |
| Entry Hall | 2.2 x 2.0 |
| Master Bedroom | 4.6 x 4.2 |
| Other bedrooms | 3.4 x 3.2 |
| Bathroom | 2.5 x 2.4 |
| Ensuite | 2.4 x 2.0 |
| Walk-in Robe | 2.4 x 1.8 |
| Living Room | 5.0 x 4.0 |
| Kitchen / Dining Room | 3.4 x 3.0 |
| Laundry | 2.4 x 2.0 |
| Study | 3.0 x 3.0 |
| Garage | 6.0 x 5.8 |
| Other or custom room | 4.0 x 3.0 |

The initial staging arrangement leaves about 0.4 m between footprints. Home Model Workshop does not currently add hallways automatically. Add a hallway through the Custom Room Program or **Add Room to Layout**, then place it manually.

Creating a new starter plan replaces the current Home Model Workshop room footprints and shape guide after confirmation. It does not automatically delete the last generated model.

### Custom Room Program

Add a name, quantity, and zone for rooms you want included the next time you create a starter plan. The zone is stored as room metadata; it does not currently change the room's starting position.

This list is a recipe for future starter-plan generation. It does not add a room to an already generated plan. To add a room to the current plan, use **Add Room to Layout** in the Room Selection section.

The direct **Add Room to Layout** command starts with a 4.0 x 3.0 m footprint unless changed in its dialog.

### Import Existing Layout

Select one or more mesh room blocks and choose **Use Selected Objects as Rooms**. Home Model Workshop creates rectangular footprints from each object's world-space XY bounds. The selected original meshes are left in the scene. Check their size and placement before building; rotated or irregular source meshes are reduced to axis-aligned bounding rectangles.

### Model Output

- **Room Floor Slabs**: build one floor slab for each room footprint.
- **Room Names**: include room labels in the generated model.
- **Build / Rebuild House Model**: replace the generated output from the current room positions, sizes, and opening guides.
- **Validate Project**: check for overlapping rooms and issues with opening guides without building.
- **Clear Generated Model**: remove Home Model Workshop's generated model while preserving room footprints and opening guides.

The generated floors, walls, and optional labels are joined into one mesh object named `HF_House_Model`.

## Room placement and wall rules

- **Open gaps stay open.** Home Model Workshop creates no wall or floor for empty space between footprints.
- **Shared edges create one wall.** A room boundary shared by adjacent footprints is represented by one wall segment.
- **Overlaps are blocked.** Any positive-area overlap between room footprints prevents a rebuild. Home Model Workshop displays the overlapping room pairs and leaves the previous generated model intact. Move or resize the footprints, then build again.
- **Duplicate room IDs are repaired.** Duplicating a Blender room object copies its custom properties; Home Model Workshop assigns the duplicate a new ID during validation or build.
- **Footprints must be axis-aligned rectangles.** Use object move and scale to arrange them. Rotating a footprint is unsupported and its axis-aligned bounds may not reflect the intended room.
- Room footprint extents must be larger than 0.2 m in both horizontal dimensions to be included.

Rooms do not need to fill the guide outline. The guide can be hidden or removed without changing what the wall builder uses.

## Adding doors and windows

Home Model Workshop does not add doors or windows automatically. It creates wall cutouts from manually placed opening frames.

1. Build the house model so there are walls to click.
2. Expand **Doors & Windows**. Enable Doorway Placement or Window Placement and set the desired width, height, and (for windows) sill height.
3. Click **Place Door Frame** or **Place Window Frame**.
4. In the 3D Viewport, click a vertical face on a generated wall. Press Esc to cancel placement.
5. Move or resize the frame if needed, then rebuild the model to apply the opening.

Frames remain separate editable objects. A frame that does not sit on a matching wall will not create a cutout, so place it directly on a vertical Home Model Workshop wall face. **Remove All Frames** deletes all Home Model Workshop door and window guides; rebuild afterward to restore solid walls.

## Troubleshooting

| Message or result | What to do |
| --- | --- |
| No valid room footprints | Generate a starter plan, add a room, or import selected mesh objects as rooms. |
| Rooms overlap | Use the popup's room/object names, then move or resize those footprints until they no longer overlap. |
| A duplicate-ID warning appears | Validate or build again; duplicate room IDs are regenerated automatically. If it persists, save a copy and inspect the room objects' `hf_room_id` custom properties. |
| No wall cutout appears | Confirm the correct opening type is enabled, the frame is on a vertical Home Model Workshop wall, its dimensions fit the wall, and rebuild. |
| A guide shape has no effect on the walls | This is expected. The shape is visual only; room footprints define the generated model. |
| A room starts outside the outline | Move it into place. A large room selection can require more space than the guide dimensions. |

## Generated scene data

Home Model Workshop stores room footprints in `HF_Room_Layout`, the placement outline in `HF_Layout_Guide`, and generated output in `HF_Generated_Model`. The guide collection is separate and is not used as input to wall generation.
