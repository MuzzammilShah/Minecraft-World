"""Procedural terrain creation and block bookkeeping."""
from __future__ import annotations

from math import floor
from typing import Dict, Tuple

from perlin_noise import PerlinNoise
from ursina import Entity, Vec3

from .game_config import BLOCK_LIBRARY, BlockId, GameConfig
from .voxel_block import VoxelBlock

GridPosition = Tuple[int, int, int]


class TerrainManager(Entity):
    """Generates a small voxel terrain chunk and manages edits."""

    def __init__(self, config: GameConfig, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config
        self._noise = PerlinNoise(
            octaves=config.perlin_octaves,
            seed=config.perlin_seed,
        )
        self._blocks: Dict[GridPosition, VoxelBlock] = {}
        self._generate_initial_chunk()

    def _generate_initial_chunk(self) -> None:
        half_size = self.config.chunk_size // 2
        for x in range(-half_size, half_size):
            for z in range(-half_size, half_size):
                height = self._sample_height(x, z)
                column_top = height - 1
                for y in range(height):
                    block_id = self._choose_block_for_layer(y, column_top)
                    self._spawn_block(Vec3(x, y, z), block_id)

    def _sample_height(self, x: int, z: int) -> int:
        scale = self.config.perlin_scale
        amplitude = self.config.terrain_amplitude
        noise_value = self._noise([x / scale, z / scale])
        return floor((noise_value + 1.0) * amplitude) + (self.config.chunk_height // 2)

    def _choose_block_for_layer(self, layer: int, column_top: int) -> BlockId:
        if layer == column_top:
            return self.config.default_block
        if column_top - layer <= 2:
            return self.config.secondary_block
        return self.config.foundation_block

    def _grid_key(self, position: Vec3) -> GridPosition:
        snapped = Vec3(round(position.x), round(position.y), round(position.z))
        return int(snapped.x), int(snapped.y), int(snapped.z)

    def _spawn_block(self, position: Vec3, block_id: BlockId) -> VoxelBlock:
        key = self._grid_key(position)
        if key in self._blocks:
            return self._blocks[key]
        block = VoxelBlock(
            position=Vec3(*key),
            block_id=block_id,
            parent=self,
            on_destroy=self._handle_block_destroy,
        )
        self._blocks[key] = block
        return block

    def place_adjacent_block(self, position: Vec3, normal: Vec3, block_id: BlockId) -> None:
        target = Vec3(*(Vec3(position) + Vec3(normal)))
        key = self._grid_key(target)
        if key in self._blocks:
            return
        self._spawn_block(Vec3(*key), block_id)

    def remove_block(self, block: VoxelBlock) -> None:
        key = self._grid_key(block.position)
        if key not in self._blocks:
            return
        block.destroy_block()

    def _handle_block_destroy(self, block: VoxelBlock) -> None:
        key = self._grid_key(block.position)
        self._blocks.pop(key, None)

    def block_at(self, position: Vec3) -> VoxelBlock | None:
        return self._blocks.get(self._grid_key(position))

    def active_block_count(self) -> int:
        return len(self._blocks)
