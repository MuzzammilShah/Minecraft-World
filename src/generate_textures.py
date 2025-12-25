"""Generate Minecraft-style block textures."""
from pathlib import Path
import random

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    exit(1)


def create_noise_texture(size: int, base_color: tuple, variation: int = 20, seed: int = 42) -> Image.Image:
    """Create a noisy texture with color variation."""
    img = Image.new('RGB', (size, size), base_color)
    draw = ImageDraw.Draw(img)
    random.seed(seed)
    
    for y in range(size):
        for x in range(size):
            # Add random variation to each pixel
            r = max(0, min(255, base_color[0] + random.randint(-variation, variation)))
            g = max(0, min(255, base_color[1] + random.randint(-variation, variation)))
            b = max(0, min(255, base_color[2] + random.randint(-variation, variation)))
            draw.point((x, y), fill=(r, g, b))
    
    return img


def create_grass_texture(size: int = 16) -> Image.Image:
    """Create a grass block top texture - Minecraft style."""
    # Base green with variation
    img = create_noise_texture(size, (89, 166, 48), variation=25, seed=42)
    draw = ImageDraw.Draw(img)
    
    # Add some darker spots for depth
    random.seed(100)
    for _ in range(size):
        x, y = random.randint(0, size-2), random.randint(0, size-2)
        shade = random.randint(60, 80)
        draw.point((x, y), fill=(shade, shade + 40, shade - 20))
    
    return img


def create_dirt_texture(size: int = 16) -> Image.Image:
    """Create a dirt block texture - Minecraft style."""
    img = create_noise_texture(size, (134, 96, 67), variation=20, seed=43)
    draw = ImageDraw.Draw(img)
    
    # Add some darker dirt spots
    random.seed(101)
    for _ in range(size * 2):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        if random.random() > 0.7:
            shade = random.randint(-30, -10)
            r = max(0, 134 + shade)
            g = max(0, 96 + shade)
            b = max(0, 67 + shade)
            draw.point((x, y), fill=(r, g, b))
    
    return img


def create_stone_texture(size: int = 16) -> Image.Image:
    """Create a stone block texture - Minecraft style."""
    img = create_noise_texture(size, (125, 125, 125), variation=15, seed=44)
    draw = ImageDraw.Draw(img)
    
    # Add some darker cracks/spots
    random.seed(102)
    for _ in range(size):
        x, y = random.randint(0, size-2), random.randint(0, size-2)
        gray = random.randint(80, 100)
        draw.rectangle([x, y, x+1, y+1], fill=(gray, gray, gray))
    
    # Add some lighter spots
    for _ in range(size // 2):
        x, y = random.randint(0, size-1), random.randint(0, size-1)
        gray = random.randint(140, 160)
        draw.point((x, y), fill=(gray, gray, gray))
    
    return img


def create_grass_side_texture(size: int = 16) -> Image.Image:
    """Create a grass block side texture (dirt with grass on top)."""
    # Start with dirt
    img = create_dirt_texture(size)
    draw = ImageDraw.Draw(img)
    
    # Add grass strip on top with irregular edge
    random.seed(103)
    for x in range(size):
        grass_height = random.randint(2, 4)
        for y in range(grass_height):
            # Grass color
            r = 89 + random.randint(-15, 15)
            g = 166 + random.randint(-20, 20)
            b = 48 + random.randint(-10, 10)
            draw.point((x, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
        
        # Add hanging grass pixels below the main line
        if random.random() > 0.5:
            y = grass_height
            if y < size:
                r = 89 + random.randint(-20, 10)
                g = 156 + random.randint(-30, 10)
                b = 48 + random.randint(-15, 10)
                draw.point((x, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
    
    return img


def main():
    """Generate all textures."""
    output_dir = Path(__file__).parent / "assets" / "textures"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    size = 16  # Original Minecraft texture size
    scale = 4  # Scale up for better visibility
    
    textures = {
        "grass_top.png": create_grass_texture(size),
        "grass_side.png": create_grass_side_texture(size),
        "dirt.png": create_dirt_texture(size),
        "stone.png": create_stone_texture(size),
    }
    
    for name, img in textures.items():
        # Scale up using NEAREST for that pixelated Minecraft look
        img_scaled = img.resize((size * scale, size * scale), Image.NEAREST)
        img_scaled.save(output_dir / name)
        print(f"Created {name} ({size}x{size} -> {size*scale}x{size*scale})")
    
    print(f"\nTextures saved to {output_dir}")
    print("Now run: python3.12 main.py")


if __name__ == "__main__":
    main()
