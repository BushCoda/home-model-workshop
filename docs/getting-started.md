---
layout: page
title: Getting Started
permalink: /getting-started/
---

<div class="hero-card">

# Getting Started

Home Model Workshop gives you a guided starting point for laying out rooms in Blender. This page walks through install, first setup, validation, and building your first house blockout.

> **Beta note:** Home Model Workshop 0.1.0 was built and smoke-tested in Blender 5.2.2. Blender 4.2.0 is the declared minimum version in the extension manifest, but compatibility with Blender 4.2 has not been independently verified.

</div>

## 1. Install and open the add-on

1. Download the installable ZIP from the GitHub Releases page after a release is published.
2. In Blender, use **Edit → Preferences → Extensions → Install from Disk**, select the ZIP, install it, and enable **Home Model Workshop**.
3. Open the **Home Model Workshop** tab in the 3D Viewport’s N-panel.

## 2. Set house and construction dimensions

Open **House & Construction** and set:

- **House Width / Depth** for the guide size and initial room staging area
- **Wall Height / Thickness** for generated walls
- **Floor Thickness** for room floor slabs

Guide dimensions control the visual Box, L, H, or U outline and the initial staging behavior. They do not resize, clip, or constrain the final room arrangement.

## 3. Choose the starter rooms

Open **Room Selection & Starting Guide** and choose a Box, L, H, or U guide shape. Then select the standard room types and counts you want in the starter plan.

- **Ensuite** and **Walk-in Robe** belong with the first bedroom / master suite.
- **Custom Room Program** is a list of named rooms to include the next time a starter plan is created.
- **Add Room to Layout** adds a room to the current plan.
- The Custom Room Program list is a recipe for future plan generation.

## 4. Create and arrange the layout

Choose **Create Rooms & Shape Guide** to create separate movable rectangular room footprints.

If a starter plan already exists, confirm that you want to replace the current Home Model Workshop footprints and guide. This does not automatically remove the previously built model.

Beginner-friendly Blender steps:

1. Click a room footprint to select it.
2. Press **G** to move it, then move it along X and Y.
3. Press **S** to resize it if needed.
4. Do **not** rotate footprints.

Rooms may start outside the guide, so place them manually into the layout you want.

Hallways / corridors are not generated automatically. If your plan needs circulation between the entry and the other rooms, add a hallway through **Custom Room Program** or **Add Room to Layout**, then place it manually.

Check that each room is reachable in your plan. The current validation does not perform an automatic room-connectivity or access check.

## 5. Validate and build

Choose **Validate Project** to check for room overlaps and opening-guide problems.

- Overlapping rooms block rebuilding.
- The message identifies the affected rooms.
- A rejected rebuild preserves the previous generated model.

Geometry rules to keep in mind:

- Open gaps remain open; no wall or floor fills them.
- Shared room edges produce one shared wall.
- Rooms do not need to fill the guide.
- The guide does not define the final building outline; the room footprints do.

Choose **Build / Rebuild House Model** to create or replace the generated floors, walls, and optional room labels from the current footprint positions and sizes.

## 6. Add doors and windows

Build the walls first.

In **Doors & Windows**:

- Enable **Doorway Placement** or **Window Placement**
- Set the width and height for doors or windows
- For windows, set the **Window Sill Height**

Then use **Place Door Frame** or **Place Window Frame**:

1. Click the button.
2. In the 3D Viewport, click a vertical face on a generated wall.
3. Press **Esc** to cancel placement.
4. Move or resize the frame if needed.
5. Rebuild the model to apply the cutout.

Frames stay editable, and a rebuild applies the cutouts. A frame must sit on a matching generated wall for a cutout to appear; doors and windows are not added automatically.

## 7. Save and reopen

Save your `.blend` file after arranging rooms and building the model.

The editable room footprints, guide, generated model, labels, and opening frames are scene objects saved with the project.

## 8. Troubleshooting

- **No room footprints:** create a starter plan, add a room, or import selected mesh objects.
- **Overlap warning:** use the room names in the message and move or resize the named footprints.
- **No cutout:** check frame type, wall contact, size, and rebuild.
- **Study or another room is isolated:** add and arrange a hallway, then check access manually.
- **Room starts outside guide:** move it into the intended layout.
