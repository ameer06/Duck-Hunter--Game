"""
Asset Generator - Creates all game visuals procedurally with Pillow
Run: python generate_assets.py
"""
from PIL import Image, ImageDraw, ImageFilter
import math, os, random

os.makedirs("assets", exist_ok=True)
random.seed(42)  # reproducible art

W, H = 1280, 720

# ─── Helpers ──────────────────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def draw_ellipse_aa(draw, bbox, fill):
    """Anti-aliased ellipse (draw large, scale down)."""
    draw.ellipse(bbox, fill=fill)

# ═══════════════════════════════════════════════════════════════════════════
# 1. BACKGROUND  (gradient sky + mountains + rolling hills)
# ═══════════════════════════════════════════════════════════════════════════
print("Generating background...")
bg = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(bg)

# Sky gradient: deep blue top → warm peach near horizon
sky_top = (40, 80, 160)
sky_mid = (135, 190, 235)
sky_bottom = (245, 195, 140)

for y in range(520):
    t = y / 520
    if t < 0.5:
        color = lerp_color(sky_top, sky_mid, t * 2)
    else:
        color = lerp_color(sky_mid, sky_bottom, (t - 0.5) * 2)
    draw.line([(0, y), (W, y)], fill=color)

# Sun glow
for r in range(80, 0, -1):
    alpha_t = 1 - r / 80
    c = lerp_color((245, 195, 140), (255, 240, 200), alpha_t)
    draw.ellipse([900 - r, 350 - r, 900 + r, 350 + r], fill=c)

# Distant mountains (dark silhouette)
mountain_color = (60, 70, 100)
pts = [(0, 480)]
x = 0
while x <= W:
    peak_y = random.randint(300, 400)
    pts.append((x, peak_y))
    x += random.randint(80, 200)
pts.append((W, 480))
draw.polygon(pts, fill=mountain_color)

# Mid mountains (slightly lighter)
pts2 = [(0, 500)]
x = 0
while x <= W:
    peak_y = random.randint(370, 440)
    pts2.append((x, peak_y))
    x += random.randint(60, 150)
pts2.append((W, 500))
draw.polygon(pts2, fill=(70, 95, 70))

# Rolling hills
hill_base = 500
for i in range(3):
    shade = (34 + i * 15, 120 + i * 20, 34 + i * 10)
    hill_pts = [(0, H)]
    for x in range(0, W + 1, 4):
        y_off = math.sin(x * 0.005 + i * 2) * 30 + math.sin(x * 0.012 + i) * 15
        hill_pts.append((x, hill_base + i * 40 + y_off))
    hill_pts.append((W, H))
    draw.polygon(hill_pts, fill=shade)

# Ground
draw.rectangle([(0, 620), (W, H)], fill=(28, 100, 28))

bg.save("assets/background.png")
print("  ✓ background.png")

# ═══════════════════════════════════════════════════════════════════════════
# 2. TREES  (3 distinct styles, transparent PNG)
# ═══════════════════════════════════════════════════════════════════════════
print("Generating trees...")

def make_pine(w=120, h=300):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w // 2
    # Trunk
    tw = 16
    d.rectangle([cx - tw // 2, h - 80, cx + tw // 2, h], fill=(90, 60, 30))
    # Foliage layers
    layers = [(60, h - 80), (80, h - 140), (100, h - 200), (70, h - 250)]
    for width, top_y in layers:
        base_y = top_y + 80
        peak = top_y
        d.polygon([(cx, peak), (cx - width // 2, base_y), (cx + width // 2, base_y)],
                  fill=(20, random.randint(90, 120), 30))
        # Highlight
        d.polygon([(cx, peak), (cx, base_y), (cx + width // 3, base_y)],
                  fill=(30, random.randint(110, 140), 40))
    return img

def make_oak(w=180, h=280):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w // 2
    # Trunk
    d.rectangle([cx - 12, h - 100, cx + 12, h], fill=(100, 70, 35))
    d.rectangle([cx - 8, h - 100, cx + 8, h], fill=(120, 85, 45))
    # Branches
    d.line([(cx, h - 100), (cx - 50, h - 140)], fill=(100, 70, 35), width=6)
    d.line([(cx, h - 90), (cx + 45, h - 130)], fill=(100, 70, 35), width=5)
    # Foliage (overlapping circles)
    foliage_positions = [
        (cx, h - 180, 55), (cx - 40, h - 150, 45), (cx + 42, h - 145, 48),
        (cx - 20, h - 200, 40), (cx + 25, h - 195, 42),
        (cx, h - 220, 35), (cx - 10, h - 160, 50),
    ]
    for fx, fy, fr in foliage_positions:
        shade = random.randint(0, 30)
        d.ellipse([fx - fr, fy - fr, fx + fr, fy + fr],
                  fill=(30 + shade, 130 + shade, 25 + shade))
    # Highlights
    for fx, fy, fr in foliage_positions[:3]:
        hr = fr // 2
        d.ellipse([fx - hr + 5, fy - hr - 5, fx + hr + 5, fy + hr - 5],
                  fill=(50, 160, 45, 120))
    return img

def make_bush_tree(w=140, h=220):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = w // 2
    # Short trunk
    d.rectangle([cx - 10, h - 60, cx + 10, h], fill=(90, 60, 30))
    # Big bushy top
    positions = [
        (cx, h - 120, 55), (cx - 30, h - 90, 45), (cx + 35, h - 85, 42),
        (cx, h - 70, 40), (cx - 15, h - 140, 35), (cx + 20, h - 145, 38),
    ]
    for fx, fy, fr in positions:
        shade = random.randint(0, 25)
        d.ellipse([fx - fr, fy - fr, fx + fr, fy + fr],
                  fill=(25 + shade, 115 + shade, 20 + shade))
    return img

tree1 = make_pine()
tree2 = make_oak()
tree3 = make_bush_tree()
tree1.save("assets/tree1.png")
tree2.save("assets/tree2.png")
tree3.save("assets/tree3.png")
print("  ✓ tree1.png, tree2.png, tree3.png")

# ═══════════════════════════════════════════════════════════════════════════
# 3. DUCK SPRITE SHEET  (4 frames: wings-up, mid-up, down, mid-down)
# ═══════════════════════════════════════════════════════════════════════════
print("Generating duck sprite sheet...")

FRAME_W, FRAME_H = 120, 100
NFRAMES = 4

def draw_duck_frame(draw, ox, oy, wing_angle):
    """Draw a single duck frame. wing_angle: 0=mid, 1=up, -1=down"""
    cx, cy = ox + 60, oy + 55

    # Body (ellipse)
    body_color = (139, 90, 43)
    body_highlight = (170, 115, 60)
    draw.ellipse([cx - 30, cy - 12, cx + 30, cy + 12], fill=body_color)
    draw.ellipse([cx - 25, cy - 10, cx + 20, cy + 5], fill=body_highlight)

    # Tail feathers
    tail_pts = [(cx - 30, cy), (cx - 45, cy - 8), (cx - 42, cy + 5)]
    draw.polygon(tail_pts, fill=(80, 60, 30))

    # Head (green, mallard style)
    head_cx, head_cy = cx + 32, cy - 18
    draw.ellipse([head_cx - 12, head_cy - 12, head_cx + 12, head_cy + 12],
                 fill=(0, 120, 60))
    draw.ellipse([head_cx - 10, head_cy - 10, head_cx + 10, head_cy + 6],
                 fill=(0, 150, 75))

    # White neck ring
    draw.arc([head_cx - 13, head_cy + 4, head_cx + 13, head_cy + 16],
             0, 180, fill=(255, 255, 255), width=2)

    # Eye
    draw.ellipse([head_cx + 3, head_cy - 6, head_cx + 8, head_cy - 1],
                 fill=(255, 200, 0))
    draw.ellipse([head_cx + 5, head_cy - 5, head_cx + 7, head_cy - 3],
                 fill=(0, 0, 0))

    # Beak
    beak_pts = [(head_cx + 12, head_cy - 2), (head_cx + 24, head_cy + 1),
                (head_cx + 12, head_cy + 4)]
    draw.polygon(beak_pts, fill=(230, 160, 30))

    # Wings (angle-based)
    wing_y_offset = int(wing_angle * 22)
    # Left wing (upper)
    w_pts = [
        (cx - 10, cy - 5),
        (cx + 5, cy - 28 + wing_y_offset),
        (cx - 20, cy - 20 + wing_y_offset),
    ]
    draw.polygon(w_pts, fill=(120, 80, 40))
    # Feather detail
    w_pts2 = [
        (cx - 5, cy - 8),
        (cx + 8, cy - 32 + wing_y_offset),
        (cx - 25, cy - 24 + wing_y_offset),
    ]
    draw.polygon(w_pts2, fill=(100, 70, 35))

    # Purple speculum (wing patch)
    spec_pts = [
        (cx - 15, cy - 4),
        (cx - 5, cy - 12 + wing_y_offset // 2),
        (cx + 10, cy - 8 + wing_y_offset // 2),
        (cx + 5, cy + 2),
    ]
    draw.polygon(spec_pts, fill=(90, 50, 130))

    # Feet (tucked in flight)
    draw.line([(cx + 5, cy + 12), (cx + 12, cy + 18)], fill=(230, 130, 30), width=2)
    draw.line([(cx - 2, cy + 12), (cx + 5, cy + 18)], fill=(230, 130, 30), width=2)


sheet = Image.new("RGBA", (FRAME_W * NFRAMES, FRAME_H), (0, 0, 0, 0))
sheet_draw = ImageDraw.Draw(sheet)

wing_angles = [1.0, 0.3, -1.0, -0.3]  # up, mid, down, mid
for i, angle in enumerate(wing_angles):
    draw_duck_frame(sheet_draw, i * FRAME_W, 0, angle)

sheet.save("assets/duck_sheet.png")
print("  ✓ duck_sheet.png (4 frames)")

# ═══════════════════════════════════════════════════════════════════════════
# 4. FOREGROUND GRASS  (semi-transparent strip)
# ═══════════════════════════════════════════════════════════════════════════
print("Generating foreground grass...")
grass = Image.new("RGBA", (W, 140), (0, 0, 0, 0))
gd = ImageDraw.Draw(grass)

# Base grass fill
gd.rectangle([(0, 50), (W, 140)], fill=(22, 90, 22, 240))
gd.rectangle([(0, 70), (W, 140)], fill=(18, 75, 18, 255))

# Grass blades along top edge
for x in range(0, W, 3):
    blade_h = random.randint(20, 55)
    lean = random.randint(-8, 8)
    shade = random.randint(0, 40)
    color = (20 + shade, 80 + shade, 15 + shade, 220)
    gd.line([(x, 55), (x + lean, 55 - blade_h)], fill=color, width=2)

# Some thicker clumps
for x in range(0, W, 40):
    for _ in range(5):
        bx = x + random.randint(-15, 15)
        blade_h = random.randint(30, 60)
        lean = random.randint(-12, 12)
        shade = random.randint(0, 30)
        color = (15 + shade, 95 + shade, 10 + shade, 240)
        gd.line([(bx, 50), (bx + lean, 50 - blade_h)], fill=color, width=3)

grass.save("assets/grass_fg.png")
print("  ✓ grass_fg.png")

# ═══════════════════════════════════════════════════════════════════════════
# 5. CROSSHAIR  (sleek red + white)
# ═══════════════════════════════════════════════════════════════════════════
print("Generating crosshair...")
ch_size = 80
ch = Image.new("RGBA", (ch_size, ch_size), (0, 0, 0, 0))
cd = ImageDraw.Draw(ch)
cc = ch_size // 2

# Outer ring
cd.ellipse([6, 6, ch_size - 6, ch_size - 6], outline=(255, 50, 50, 200), width=3)
# Inner ring
cd.ellipse([18, 18, ch_size - 18, ch_size - 18], outline=(255, 255, 255, 160), width=2)
# Cross lines
for dx, dy in [(0, 1), (1, 0)]:
    cd.line([(cc + dx * 12, cc + dy * 12), (cc + dx * 34, cc + dy * 34)],
            fill=(255, 60, 60, 220), width=2)
    cd.line([(cc - dx * 12, cc - dy * 12), (cc - dx * 34, cc - dy * 34)],
            fill=(255, 60, 60, 220), width=2)
# Center dot
cd.ellipse([cc - 3, cc - 3, cc + 3, cc + 3], fill=(255, 80, 80, 255))

ch.save("assets/crosshair.png")
print("  ✓ crosshair.png")

print("\n🎮 All assets generated successfully!")
