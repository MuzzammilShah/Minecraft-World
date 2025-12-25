"""Minimal Ursina test to debug rendering on macOS."""
from ursina import Ursina, Entity, color, camera

app = Ursina()

# Create a simple cube
cube = Entity(
    model='cube',
    color=color.red,
    position=(0, 0, 5),
    scale=2
)

print(f"Cube position: {cube.position}")
print(f"Camera position: {camera.position}")
print(f"Camera forward: {camera.forward}")

app.run()
