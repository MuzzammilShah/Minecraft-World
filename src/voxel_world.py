"""High-level orchestration of the Ursina voxel sandbox."""
from __future__ import annotations

from typing import Dict

from ursina import Entity, Text, Vec3, application, camera, color, mouse, raycast, scene, window
from ursina.prefabs.first_person_controller import FirstPersonController

from .game_config import BLOCK_LIBRARY, BlockId, GameConfig, DEFAULT_CONFIG
from .terrain_manager import TerrainManager
from .voxel_block import VoxelBlock


class PlayerHand(Entity):
    """Visible hand/arm in first-person view."""
    
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera,  # Attach to camera so it moves with view
            model='cube',
            color=color.rgb(210, 180, 140),  # Skin tone
            scale=(0.1, 0.1, 0.3),  # Arm shape
            position=(0.4, -0.3, 0.5),  # Bottom right of view
            rotation=(10, -10, 0),
            **kwargs
        )
        self.original_position = self.position
        self.swing_time = 0
        self.is_swinging = False
    
    def swing(self):
        """Trigger a swing animation."""
        self.is_swinging = True
        self.swing_time = 0.2
    
    def update(self):
        """Animate the hand swing."""
        if self.is_swinging and self.swing_time > 0:
            from ursina import time
            self.swing_time -= time.dt
            # Simple swing animation
            progress = 1 - (self.swing_time / 0.2)
            if progress < 0.5:
                self.rotation_x = 10 + progress * 60
            else:
                self.rotation_x = 10 + (1 - progress) * 60
            if self.swing_time <= 0:
                self.is_swinging = False
                self.rotation_x = 10


class VoxelWorld(Entity):
    """Container entity that owns terrain, player, lighting, and UI."""

    def __init__(self, config: GameConfig | None = None, **kwargs) -> None:
        super().__init__(parent=scene, **kwargs)
        self.config = config or DEFAULT_CONFIG
        self.selected_block = self.config.default_block
        self.terrain = TerrainManager(self.config, parent=scene)
        self.player = self._create_player()
        self.hand = PlayerHand()
        self._setup_environment()
        self._hud: Dict[str, Text] = {}
        self._build_hud()

    def _create_player(self) -> FirstPersonController:
        controller = FirstPersonController(speed=self.config.player_speed)
        controller.gravity = self.config.gravity_strength
        controller.jump_height = self.config.player_jump_height
        controller.y = self.config.chunk_height + 10  # Start above terrain
        
        # Remove camera pitch limits for full 360 look
        controller.camera_pivot.rotation_x = 0
        # Override the mouse look limits
        controller.mouse_sensitivity = Vec3(40, 40, 0)
        
        # Lock mouse for FPS-style controls
        mouse.locked = True
        mouse.visible = False
        controller.cursor.visible = True
        controller.cursor.color = color.azure
        return controller

    def _setup_environment(self) -> None:
        # Sky blue gradient background
        window.color = color.rgb(135, 206, 235)
        
        # Create a simple ground plane far below for depth perception
        ground = Entity(
            parent=scene,
            model='plane',
            scale=500,
            y=-10,
            color=color.rgb(100, 150, 100),
            collider=None
        )

    def _build_hud(self) -> None:
        self._hud_base_text = "Left click: build  |  Right click: remove"
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
            position=(-0.85, 0.4),
            origin=(0, 0),
            background=True,
            color=color.white,
            scale=0.6,
        )

    def input(self, key: str) -> None:  # noqa: D401 - Ursina callback signature.
        if key == "left mouse down":
            self.hand.swing()
            self._attempt_place_block()
        elif key == "right mouse down":
            self.hand.swing()
            self._attempt_remove_block()
        elif key in {"1", "2", "3"}:
            self._select_block_via_hotkey(int(key))
        elif key == "tab":
            mouse.locked = not mouse.locked
            mouse.visible = not mouse.locked
            self.player.cursor.visible = mouse.locked
        elif key == "escape":
            application.quit()

    def update(self) -> None:  # noqa: D401 - Ursina callback signature.
        self._hud["counter"].text = self._format_block_counter()
        # Update hand position for held block preview
        block_def = BLOCK_LIBRARY[self.selected_block]
        self.hand.color = block_def.base_color

    def _attempt_place_block(self) -> None:
        # Use mouse.hovered_entity for reliable hit detection
        if mouse.hovered_entity and isinstance(mouse.hovered_entity, VoxelBlock):
            target = mouse.hovered_entity
            # Get the hit normal from mouse
            if mouse.normal:
                print(f"Place: Adding block adjacent to {target.position}")
                self.terrain.place_adjacent_block(target.position, mouse.normal, self.selected_block)
            return
        # Fallback to raycast
        hit_info = self._cast_from_camera()
        if not hit_info.hit:
            print("Place: No hit detected")
            return
        target_entity = hit_info.entity
        if not isinstance(target_entity, VoxelBlock):
            print(f"Place: Hit non-block entity: {type(target_entity)}")
            return
        print(f"Place: Adding block at {target_entity.position + hit_info.normal}")
        self.terrain.place_adjacent_block(target_entity.position, hit_info.normal, self.selected_block)

    def _attempt_remove_block(self) -> None:
        # Use mouse.hovered_entity for reliable hit detection
        if mouse.hovered_entity and isinstance(mouse.hovered_entity, VoxelBlock):
            target = mouse.hovered_entity
            if target.position.y <= 0:
                print("Remove: Can't remove bedrock layer")
                return
            print(f"Remove: Removing block at {target.position}")
            self.terrain.remove_block(target)
            return
        # Fallback to raycast
        hit_info = self._cast_from_camera()
        if not hit_info.hit:
            print("Remove: No hit detected")
            return
        target_entity = hit_info.entity
        if not isinstance(target_entity, VoxelBlock):
            print(f"Remove: Hit non-block entity: {type(target_entity)}")
            return
        if target_entity.position.y <= 0:
            print("Remove: Can't remove bedrock layer")
            return
        print(f"Remove: Removing block at {target_entity.position}")
        self.terrain.remove_block(target_entity)

    def _cast_from_camera(self):
        return raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=self.config.build_distance,
            ignore=(self.player, self.player.collider),
        )

    def _select_block_via_hotkey(self, index: int) -> None:
        block_ids = list(BLOCK_LIBRARY.keys())
        if 1 <= index <= len(block_ids):
            self.selected_block = block_ids[index - 1]
            self._hud["instructions"].text = self._compose_instruction_text()

    def _format_block_counter(self) -> str:
        total_blocks = self.terrain.active_block_count()
        return f"Blocks: {total_blocks}"

    def _compose_instruction_text(self) -> str:
        block_labels = []
        for index, block_id in enumerate(BLOCK_LIBRARY.keys(), start=1):
            prefix = ">" if block_id == self.selected_block else " "
            block_labels.append(f"[{index}] {prefix}{block_id.value}")
        return f"{self._hud_base_text}  |  {'  '.join(block_labels)}"
