"""Voxel block entity with click-aware behaviour."""
from __future__ import annotations

from typing import Callable, Dict, Optional

from ursina import Entity, Texture, Vec3, color, load_texture

from .game_config import BLOCK_LIBRARY, BlockDefinition, BlockId, get_texture_path

# Cache loaded textures to avoid reloading
_texture_cache: Dict[str, Optional[Texture]] = {}


def _load_block_texture(texture_name: Optional[str]) -> Optional[Texture]:
    """Load and cache a block texture."""
    if texture_name is None:
        return None
    
    if texture_name in _texture_cache:
        return _texture_cache[texture_name]
    
    texture_path = get_texture_path(texture_name)
    if texture_path and texture_path.exists():
        try:
            tex = load_texture(str(texture_path))
            _texture_cache[texture_name] = tex
            return tex
        except Exception as e:
            print(f"Failed to load texture {texture_name}: {e}")
            _texture_cache[texture_name] = None
            return None
    
    _texture_cache[texture_name] = None
    return None


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
        # Remove parent from kwargs if present, we always parent to scene
        kwargs.pop("parent", None)
        
        # Try to load texture, fall back to color if not available
        texture = _load_block_texture(block_definition.texture_name)
        use_texture = texture is not None
        
        super().__init__(
            parent=scene,
            position=position,
            model="cube",
            texture=texture,
            color=color.white if use_texture else block_definition.base_color,
            collider="box",
            **kwargs,
        )
        self.block_id = block_id
        self.block_definition = block_definition
        self.on_destroy = on_destroy
        self._has_texture = use_texture
        self._base_color = color.white if use_texture else block_definition.base_color
        self._highlight_color = color.rgb(200, 200, 150) if use_texture else block_definition.highlight_color

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
