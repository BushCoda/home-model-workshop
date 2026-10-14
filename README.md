# Home Model Workshop

**A Blender add-on for guided room layout and editable house-model blockouts.**

Home Model Workshop starts with a room program and a visual footprint guide. You arrange and resize the rooms, validate the layout, and build the walls and floors when the plan is ready.

> **Planned initial release: 0.1.0 beta.** The release has not yet been published. Generated models are editable blockouts and should be reviewed in Blender.

## Documentation

- [Documentation home](docs/index.md)
- [Getting Started](docs/getting-started.md)
- [User Guide](docs/user-guide.md)
- [Roadmap](docs/roadmap.md)
- [Developer Guide](docs/developer-guide.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

## Features

- Box, L, H, and U visual placement guides.
- Standard and custom room programs.
- Separate room footprints for user-directed placement.
- Overlap validation, open gaps, and single shared walls.
- Manually placed door and window frames with rebuild-based cutouts.
- Import of selected mesh objects as room footprints.

## Repository structure

```text
home-model-workshop/
├── __init__.py                 # Blender add-on code
├── blender_manifest.toml       # Blender extension metadata
├── docs/                       # GitHub Pages site and user/developer guides
├── .github/ISSUE_TEMPLATE/     # Structured bug and feature reports
├── scripts/build-release.ps1   # Creates the installable ZIP in dist/
└── dist/                       # Generated release ZIP; excluded from Git
```
## Requirements

- Minimum Blender version declared in the extension manifest: 4.2.0. Blender 5.2.2 is the development target; compatibility should be confirmed with smoke tests before release.
- Rectangular, axis-aligned room footprints. Rotated or irregular imported meshes are reduced to world-space bounding rectangles.

## Install

Download the installable extension ZIP attached to a release. Do not use GitHub's automatically generated source-code ZIP. In Blender, open **Edit → Preferences → Extensions**, open the menu in the upper-right, and choose **Install from Disk**. Select the extension ZIP, install it, and enable **Home Model Workshop**.

## GitHub Pages documentation

The `/docs` folder is ready to publish as the Pages site. In GitHub, open **Settings → Pages**, choose **Deploy from a branch**, then select **main** and **/docs**. The site uses GitHub Pages' supported Minima Jekyll theme. If the repository slug is different from `home-model-workshop`, update `baseurl` in `docs/_config.yml` to `/<repository-slug>` before publishing.

## Create a release

1. Run `./scripts/build-release.ps1` in PowerShell to create the installable ZIP. The script checks that `bl_info` and `blender_manifest.toml` use the same version.
2. Create a Git tag such as `v0.1.0` and draft a GitHub Release from that tag.
3. Attach the installable extension ZIP and mark the release as a pre-release while the add-on is in beta.

## License

This project is licensed under [GPL-3.0-or-later](LICENSE), as declared in the extension manifest.
