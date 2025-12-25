"""Centralised configuration and block definitions for the Ursina voxel demo."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from ursina import color

# Asset paths
ASSETS_DIR = Path(__file__).parent / "assets"
TEXTURES_DIR = ASSETS_DIR / "textures"


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
    texture_name: Optional[str] = None  # Just the filename, not full path


def get_texture_path(filename: str) -> Optional[Path]:
    """Return texture path if file exists, else None."""
    path = TEXTURES_DIR / filename
    return path if path.exists() else None


BLOCK_LIBRARY: Dict[BlockId, BlockDefinition] = {
    BlockId.GRASS: BlockDefinition(
        name=BlockId.GRASS,
        base_color=color.rgb(95, 159, 53),
        highlight_color=color.rgb(123, 190, 82),
        texture_name="grass_top.png",
    ),
    BlockId.DIRT: BlockDefinition(
        name=BlockId.DIRT,
        base_color=color.rgb(151, 106, 68),
        highlight_color=color.rgb(181, 141, 102),
        texture_name="dirt.png",
    ),
    BlockId.STONE: BlockDefinition(
        name=BlockId.STONE,
        base_color=color.rgb(130, 130, 130),
        highlight_color=color.rgb(169, 169, 169),
        texture_name="stone.png",
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
