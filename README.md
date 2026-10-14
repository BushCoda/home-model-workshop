# Home Model Workshop

**A Blender add-on for guided room layout and editable house-model blockouts.**

Home Model Workshop helps you start from a room program and a visual placement guide, arrange the rooms yourself, validate the layout, and build floors and walls from the room footprints. It is designed as a blockout and layout tool, not an automatic architectural designer.

> **Home Model Workshop 0.1.0 beta** was built and smoke-tested in Blender 5.2.2. Generated models are editable blockouts and should be reviewed in Blender before further use. Blender 4.2.0 is the declared minimum version in the extension manifest, but compatibility with Blender 4.2 has not been independently verified.

## Features

- Box, L, H, and U visual placement guides
- Standard room selection plus custom room programs
- Separate editable room footprints for user-directed placement
- Overlap validation, open gaps, and single shared walls
- Manually placed door and window frames with rebuild-based cutouts
- Import of selected mesh objects as room footprints
- GitHub Pages documentation for setup and usage

## Documentation

- [Documentation home](https://bushcoda.github.io/home-model-workshop/)
- [Getting Started](https://bushcoda.github.io/home-model-workshop/getting-started/)
- [User Guide](https://bushcoda.github.io/home-model-workshop/user-guide/)
- [Roadmap](https://bushcoda.github.io/home-model-workshop/roadmap/)
- [Developer Guide](https://bushcoda.github.io/home-model-workshop/developer-guide/)

## Install

1. Download the installable extension ZIP from the [GitHub Releases page](https://github.com/BushCoda/home-model-workshop/releases) after a release is published.
2. In Blender, open **Edit → Preferences → Extensions**, open the menu in the upper-right, and choose **Install from Disk**.
3. Select the ZIP, install it, and enable **Home Model Workshop**.
4. Open the **Home Model Workshop** tab in the 3D Viewport's N-panel.

## Quick use

1. Choose a starter guide shape in **Room Selection & Starting Guide**.
2. Select the rooms you want to include.
3. Create the starter plan.
4. Move and resize the room footprints into the layout you want.
5. Validate the layout.
6. Build or rebuild the house model.
7. Add door and window frames after the walls are built, then rebuild to apply cutouts.

## Requirements

- Blender 5.2.2 is the tested development target for this beta.
- The extension manifest declares Blender 4.2.0 as the minimum version.
- Room footprints are axis-aligned rectangles.
- Imported rotated or irregular meshes are reduced to world-space bounding rectangles.

## License

This project is licensed under [GPL-3.0-or-later](LICENSE).
