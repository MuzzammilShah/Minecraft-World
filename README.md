# Ursina Voxel Sandbox

A lightweight Minecraft-style sandbox built with [Ursina](https://www.ursinaengine.org/) and the `perlin-noise` library. The project targets macOS on Apple Silicon and ships with a simple procedural terrain, First Person controls, and hotkeys for switching block materials.

## Prerequisites
- Python 3.12 (the repo assumes a `.venv` virtual environment already exists)
- macOS 13+ on Apple Silicon (OpenGL 3.3 capable)
- Git (for version control)

## Setup
1. Activate your virtual environment:
   ```bash
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run The Game
Execute the entry module through Python:
```bash
python -m src.main
```
Controls:
- `WASD` to move, `Space` to jump, `Mouse` to look
- `Left click` to place a block, `Right click` to remove a block (above the bedrock layer)
- Number keys `1-3` to switch block material
- `Esc` (or closing the window) to exit

## Project Layout
```
src/
  __init__.py           Package marker for module imports
  game_config.py        Engine configuration and block definitions
  main.py               Application entrypoint
  terrain_manager.py    Procedural terrain generator and block registry
  voxel_block.py        Click-aware voxel entity
  voxel_world.py        Scene composition, HUD, and input routing
```

## GitHub Workflow
1. Check repo status: `git status`
2. Stage changes: `git add src .gitignore requirements.txt README.md`
3. Commit with a clear message: `git commit -m "Add Ursina voxel sandbox scaffold"`
4. Push to GitHub: `git push origin <branch>`

## Next Steps
- Experiment with chunked terrain generation and mesh combining for larger worlds (`Entity.combine()` in Ursina).
- Import custom textures and assign them in `BLOCK_LIBRARY`.
- Add audio cues for placing/removing blocks.
