"""High-level orchestration of the Ursina voxel sandbox."""
from __future__ import annotations

from typing import Dict
import math

from ursina import (
    Entity, Text, Vec3, application, camera, color, 
    mouse, scene, window, time
)
from ursina.prefabs.first_person_controller import FirstPersonController

from .game_config import BLOCK_LIBRARY, BlockId, GameConfig, DEFAULT_CONFIG
from .terrain_manager import TerrainManager
from .voxel_block import VoxelBlock


class HeldBlockDisplay(Entity):
    """Shows the currently held block in first-person view."""
    
    def __init__(self, block_id: BlockId, **kwargs):
        block_def = BLOCK_LIBRARY[block_id]
        super().__init__(
            parent=camera,
            model='cube',
            texture=block_def.texture_path,
            color=color.white if block_def.texture_path else block_def.base_color,
            scale=0.12,
            position=(0.45, -0.3, 0.5),
            rotation=(15, -25, 5),
            **kwargs
        )
        self.block_id = block_id
        self._bob_time = 0
        self._base_y = -0.3
        self._swing_progress = 0
        self._is_swinging = False
    
    def set_block(self, block_id: BlockId):
        """Change the displayed block."""
        self.block_id = block_id
        block_def = BLOCK_LIBRARY[block_id]
        self.texture = block_def.texture_path
        self.color = color.white if block_def.texture_path else block_def.base_color
    
    def swing(self):
        """Trigger swing animation."""
        self._is_swinging = True
        self._swing_progress = 0
    
    def update(self):
        # Gentle bobbing
        self._bob_time += time.dt * 2
        bob = math.sin(self._bob_time) * 0.015
        
        # Swing animation
        swing_offset = 0
        swing_rot = 0
        if self._is_swinging:
            self._swing_progress += time.dt * 8
            if self._swing_progress < 1:
                # Swing down
                swing_rot = math.sin(self._swing_progress * math.pi) * 45
                swing_offset = math.sin(self._swing_progress * math.pi) * 0.1
            else:
                self._is_swinging = False
                self._swing_progress = 0
        
        self.y = self._base_y + bob - swing_offset
        self.rotation_x = 15 + swing_rot


class VoxelWorld(Entity):
    """Container entity that owns terrain, player, lighting, and UI."""

    def __init__(self, config: GameConfig | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.config = config or DEFAULT_CONFIG
        self.selected_block = self.config.default_block
        
        # Setup environment first
        self._setup_environment()
        
        # Create terrain
        self.terrain = TerrainManager(self.config)
        
        # Create player (use built-in FirstPersonController for stability)
        self.player = self._create_player()
        
        # Held block display
        self.held_block = HeldBlockDisplay(self.selected_block)
        
        # HUD
        self._hud: Dict[str, Text] = {}
        self._build_hud()

    def _create_player(self) -> FirstPersonController:
        """Create the first-person player controller."""
        controller = FirstPersonController(
            speed=self.config.player_speed,
            jump_height=self.config.player_jump_height,
            gravity=self.config.gravity_strength,
        )
        
        # Position player above terrain
        controller.position = Vec3(0, self.config.chunk_height + 5, 0)
        
        # Mouse settings
        mouse.locked = True
        mouse.visible = False
        
        # Replace the default cursor with a small crosshair
        controller.cursor.visible = False  # Hide default cursor
        
        # Create a simple crosshair
        self.crosshair = Text(
            text='+',
            parent=camera.ui,
            origin=(0, 0),
            scale=2,
            color=color.white
        )
        
        return controller

    def _setup_environment(self) -> None:
        """Set up sky and environment."""
        # Minecraft-style sky blue
        window.color = color.rgb(120, 170, 255)

    def _build_hud(self) -> None:
        """Create the heads-up display."""
        self._hud["instructions"] = Text(
            text=self._compose_instruction_text(),
            position=(-0.85, 0.45),
            origin=(0, 0),
            background=True,
            color=color.white,
            scale=0.7,
        )
        self._hud["counter"] = Text(
            text=self._format_block_counter(),
            position=(-0.85, 0.38),
            origin=(0, 0),
            background=True,
            color=color.white,
            scale=0.6,
        )
        self._hud["controls"] = Text(
            text="WASD: Move | Space: Jump | 1-3: Select Block | Tab: Unlock Mouse | Esc: Quit",
            position=(0, -0.45),
            origin=(0, 0),
            background=True,
            color=color.white,
            scale=0.5,
        )

    def input(self, key: str) -> None:
        """Handle input events."""
        if key == "left mouse down":
            self.held_block.swing()
            self._attempt_place_block()
        elif key == "right mouse down":
            self.held_block.swing()
            self._attempt_remove_block()
        elif key == "1":
            self._select_block(BlockId.GRASS)
        elif key == "2":
            self._select_block(BlockId.DIRT)
        elif key == "3":
            self._select_block(BlockId.STONE)
        elif key == "tab":
            mouse.locked = not mouse.locked
            mouse.visible = not mouse.locked
        elif key == "escape":
            application.quit()

    def update(self) -> None:
        """Per-frame update."""
        self._hud["counter"].text = self._format_block_counter()

    def _attempt_place_block(self) -> None:
        """Try to place a block where the player is looking."""
        if mouse.hovered_entity and isinstance(mouse.hovered_entity, VoxelBlock):
            target = mouse.hovered_entity
            if mouse.normal:
                self.terrain.place_adjacent_block(
                    target.position, mouse.normal, self.selected_block
                )

    def _attempt_remove_block(self) -> None:
        """Try to remove the block the player is looking at."""
        if mouse.hovered_entity and isinstance(mouse.hovered_entity, VoxelBlock):
            target = mouse.hovered_entity
            # Don't allow removing the bottom layer
            if target.position.y > 0:
                self.terrain.remove_block(target)

    def _select_block(self, block_id: BlockId) -> None:
        """Select a block type."""
        self.selected_block = block_id
        self.held_block.set_block(block_id)
        self._hud["instructions"].text = self._compose_instruction_text()

    def _format_block_counter(self) -> str:
        """Format the block counter text."""
        return f"Blocks: {self.terrain.active_block_count()}"

    def _compose_instruction_text(self) -> str:
        """Compose the block selection text."""
        parts = ["Left click: Place | Right click: Remove"]
        for i, block_id in enumerate(BLOCK_LIBRARY.keys(), start=1):
            marker = ">" if block_id == self.selected_block else " "
            parts.append(f"[{i}]{marker}{block_id.value}")
        return "  ".join(parts)
