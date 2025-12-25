"""Generate simple Minecraft-style block textures."""
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    exit(1)


def create_grass_texture(size: int = 16) -> Image.Image:
    """Create a grass block top texture."""
    img = Image.new('RGB', (size, size), (95, 159, 53))
    draw = ImageDraw.Draw(img)
    # Add some variation
    import random
    random.seed(42)
    for _ in range(size * 2):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        shade = random.randint(-20, 20)
        base = (95 + shade, 159 + shade, 53 + shade // 2)
        base = tuple(max(0, min(255, c)) for c in base)
        draw.point((x, y), fill=base)
    return img


def create_dirt_texture(size: int = 16) -> Image.Image:
    """Create a dirt block texture."""
    img = Image.new('RGB', (size, size), (134, 96, 67))
    draw = ImageDraw.Draw(img)
    import random
    random.seed(43)
    for _ in range(size * 3):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        shade = random.randint(-25, 25)
        base = (134 + shade, 96 + shade, 67 + shade // 2)
        base = tuple(max(0, min(255, c)) for c in base)
        draw.point((x, y), fill=base)
    return img


def create_stone_texture(size: int = 16) -> Image.Image:
    """Create a stone block texture."""
    img = Image.new('RGB', (size, size), (128, 128, 128))
    draw = ImageDraw.Draw(img)
    import random
    random.seed(44)
    # Add gray variation and cracks
    for _ in range(size * 4):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        shade = random.randint(-30, 30)
        gray = 128 + shade
        gray = max(80, min(180, gray))
        draw.point((x, y), fill=(gray, gray, gray))
    # Add some darker spots for depth
    for _ in range(size // 2):
        x, y = random.randint(0, size-2), random.randint(0, size-2)
        draw.rectangle([x, y, x+1, y+1], fill=(100, 100, 100))
    return img


def create_grass_side_texture(size: int = 16) -> Image.Image:
    """Create a grass block side texture (dirt with grass on top)."""
    img = create_dirt_texture(size)
    draw = ImageDraw.Draw(img)
    # Add grass strip on top
    import random
    random.seed(45)
    for x in range(size):
        grass_height = random.randint(2, 4)
        for y in range(grass_height):
            shade = random.randint(-15, 15)
            green = (95 + shade, 159 + shade, 53 + shade // 2)
            green = tuple(max(0, min(255, c)) for c in green)
            draw.point((x, y), fill=green)
    return img


def main():
    """Generate all textures."""
    output_dir = Path(__file__).parent / "assets" / "textures"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    textures = {
        "grass_top.png": create_grass_texture(16),
        "grass_side.png": create_grass_side_texture(16),
        "dirt.png": create_dirt_texture(16),
        "stone.png": create_stone_texture(16),
    }
    
    for name, img in textures.items():
        # Scale up for better visibility
        img_scaled = img.resize((64, 64), Image.NEAREST)
        img_scaled.save(output_dir / name)
        print(f"Created {name}")
    
    print(f"\nTextures saved to {output_dir}")


if __name__ == "__main__":
    main()
