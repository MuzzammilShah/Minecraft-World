"""Executable entry point for the Ursina voxel sandbox."""
from __future__ import annotations

import sys
from pathlib import Path

from ursina import Ursina, application, color, window

application.development_mode = False

if __package__ in {None, ""}:  # Allow running via "python main.py" from the src folder.
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.game_config import DEFAULT_CONFIG, GameConfig
    from src.voxel_world import VoxelWorld
else:
    from .game_config import DEFAULT_CONFIG, GameConfig
    from .voxel_world import VoxelWorld


def launch_app(config: GameConfig | None = None) -> None:
    """Configure the engine, build the scene, and start the loop."""

    active_config = config or DEFAULT_CONFIG
    app = Ursina(
        title=active_config.window_title,
        vsync=active_config.vsync_enabled,
        development_mode=False
    )
    window.fps_counter.enabled = active_config.show_fps
    VoxelWorld(config=active_config)
    app.run()


if __name__ == "__main__":
    launch_app()
