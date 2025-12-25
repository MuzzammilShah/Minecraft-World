"""Voxel block entity with click-aware behaviour."""
from __future__ import annotations

from typing import Callable, Optional

from ursina import Entity, Vec3, color

from .game_config import BLOCK_LIBRARY, BlockDefinition, BlockId


class VoxelBlock(Entity):
    """Voxel entity with basic hover highlighting."""

    def __init__(
        self,
        position: Vec3,
        block_id: BlockId,
        on_destroy: Optional[Callable[["VoxelBlock"], None]] = None,
        **kwargs,
    ) -> None:
        block_definition: BlockDefinition = BLOCK_LIBRARY[block_id]
        from ursina import scene
        
        # Remove parent from kwargs if present
        kwargs.pop("parent", None)
        
        # Use texture if available (relative path for Ursina)
        texture_path = block_definition.texture_path
        use_texture = texture_path is not None
        
        super().__init__(
            parent=scene,
            position=position,
            model="cube",
            texture=texture_path,
            # Use white color with texture so texture shows properly, otherwise use base_color
            color=color.white if use_texture else block_definition.base_color,
            collider="box",
            **kwargs,
        )
        
        self.block_id = block_id
        self.block_definition = block_definition
        self.on_destroy = on_destroy
        self._has_texture = use_texture
        self._base_color = color.white if use_texture else block_definition.base_color
        self._highlight_color = color.rgb(255, 255, 200) if use_texture else block_definition.highlight_color

    def destroy_block(self) -> None:
        """Remove the block from the scene and notify listeners."""

        if callable(self.on_destroy):
            self.on_destroy(self)
        self.disable()
        self.visible = False
        self.collider = None
        self.color = color.clear
        self.remove_node()

    def on_mouse_enter(self) -> None:  # noqa: D401 - Ursina callback signature.
        self.color = self._highlight_color

    def on_mouse_exit(self) -> None:  # noqa: D401 - Ursina callback signature.
        self.color = self._base_color
