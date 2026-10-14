# Contributing

Thanks for helping improve Home Model Workshop.

## Before opening an issue

- Check the user guide and existing issues for the same problem.
- Include the add-on version and Blender version.
- Describe the room layout and exact steps that reproduce the issue.
- Remove private information from screenshots, logs, and `.blend` files before sharing them.

## Before proposing a change

- Keep the installed extension structure at the repository root: `__init__.py` and `blender_manifest.toml` must stay together.
- Preserve the `houseforge` extension ID and scene-property keys unless a deliberate migration is designed.
- Update the user guide and developer guide when behavior changes.
- Keep `bl_info["version"]` and `blender_manifest.toml` synchronized.

## Pull requests

Describe the user-visible change, the Blender version used for manual verification, and any known limitations. Include screenshots for N-panel or viewport changes when practical.
