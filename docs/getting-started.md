---
layout: page
title: Getting Started
permalink: /getting-started/
---

# Getting Started

## Install the beta

1. Download `Home_Model_Workshop_Blender_5_2_2_v0_1_0.zip` from the GitHub Releases page.
2. In Blender, open **Edit → Preferences → Extensions**, open the menu in the upper-right, and choose **Install from Disk**.
3. Select the downloaded ZIP, install it, and enable **Home Model Workshop**.
4. In the 3D Viewport, open the **Home Model Workshop** tab in the N-panel.

The extension manifest declares Blender 4.2.0 as the minimum version. Blender 5.2.2 is the tested development target for this beta; compatibility with Blender 4.2 remains unverified.

## Create your first layout

1. Expand **House & Construction** and set the guide dimensions and wall/floor sizes.
2. Expand **Room Selection & Starting Guide**. Choose Box, L, H, or U and select the room types and counts.
3. Optionally add named rooms under **Custom Room Program**.
4. Choose **Create Rooms & Shape Guide**.
5. Move and resize the separate room footprints. Use axis-aligned rectangles; do not rotate them.
6. Choose **Validate Project**, adjust any overlapping rooms, then choose **Build / Rebuild House Model**.

The initial placement is a starting arrangement. The shape outline does not move, clip, or constrain room footprints. Empty gaps stay open, and shared room edges produce one wall.

## Add doors and windows

Build the walls first, then use the **Doors & Windows** section to place a frame on a wall. Adjust its position or size and rebuild to apply the cutout. See [Doors and Windows]({{ '/user-guide/' | relative_url }}#adding-doors-and-windows) for details.

For a walkthrough of every setting, continue to the [User Guide]({{ '/user-guide/' | relative_url }}).
