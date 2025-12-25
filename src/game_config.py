"""Centralised configuration and block definitions for the Ursina voxel demo."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from ursina import color

# Relative texture path from src folder (where main.py runs)
TEXTURE_PATH_PREFIX = "assets/textures"


class BlockId(str, Enum):
    """Narrow set of block identifiers supported by the demo."""

    GRASS = "grass"
    DIRT = "dirt"
    STONE = "stone"


@dataclass(frozen=True)
class BlockDefinition:
    """Visual and gameplay properties for a voxel block."""

    name: BlockId
    base_color: color.Color
    highlight_color: color.Color
    texture_file: Optional[str] = None  # Filename only (e.g., "grass_top.png")

    @property
    def texture_path(self) -> Optional[str]:
        """Get relative texture path for Ursina."""
        if self.texture_file:
            return f"{TEXTURE_PATH_PREFIX}/{self.texture_file}"
        return None


BLOCK_LIBRARY: Dict[BlockId, BlockDefinition] = {
    BlockId.GRASS: BlockDefinition(
        name=BlockId.GRASS,
        base_color=color.rgb(89, 166, 48),
        highlight_color=color.rgb(120, 200, 80),
        texture_file="grass_top.png",
    ),
    BlockId.DIRT: BlockDefinition(
        name=BlockId.DIRT,
        base_color=color.rgb(134, 96, 67),
        highlight_color=color.rgb(170, 130, 100),
        texture_file="dirt.png",
    ),
    BlockId.STONE: BlockDefinition(
        name=BlockId.STONE,
        base_color=color.rgb(125, 125, 125),
        highlight_color=color.rgb(160, 160, 160),
        texture_file="stone.png",
    ),
}


@dataclass(frozen=True)
class GameConfig:
    """High-level tuning parameters for the voxel world."""

    window_title: str = "Ursina Voxel Sandbox"
    vsync_enabled: bool = True
    show_fps: bool = True
    build_distance: float = 16.0
    chunk_size: int = 20
    chunk_height: int = 8
    perlin_octaves: int = 3
    perlin_seed: int = 3_817
    perlin_scale: float = 48.0
    terrain_amplitude: float = 3.5
    default_block: BlockId = BlockId.GRASS
    secondary_block: BlockId = BlockId.DIRT
    foundation_block: BlockId = BlockId.STONE
    player_speed: float = 6.0
    player_jump_height: float = 2.0
    gravity_strength: float = 1.0


DEFAULT_CONFIG = GameConfig()
