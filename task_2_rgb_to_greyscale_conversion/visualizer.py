"""
Image Processing Visualizers, Test Image Synthesizers & Comparison Grids
========================================================================
Generates test images and creates labeled side-by-side comparison grids
for multiple RGB-to-Greyscale conversion methods.
"""

from __future__ import annotations
import os
import math
from typing import Dict, Any, Optional, Tuple

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


def create_color_palette_test_image(width: int = 640, height: int = 480) -> Image.Image:
    """Synthesizes a standardized calibrated RGB color test target."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy are required.")

    img = Image.new("RGB", (width, height), color=(20, 24, 33))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (width, 36)], fill=(15, 23, 42))
    try:
        font_title = ImageFont.load_default(size=16)
        font_label = ImageFont.load_default(size=12)
    except Exception:
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()

    draw.text((width // 2, 18), "CALIBRATED RGB COLOR TEST TARGET", fill=(241, 245, 249), font=font_title, anchor="mm")

    # Primary & Secondary Colors
    colors = [
        ("Red (255,0,0)", (255, 0, 0)),
        ("Green (0,255,0)", (0, 255, 0)),
        ("Blue (0,0,255)", (0, 0, 255)),
        ("Yellow (255,255,0)", (255, 255, 0)),
        ("Cyan (0,255,255)", (0, 255, 255)),
        ("Magenta (255,0,255)", (255, 0, 255)),
    ]
    block_w = (width - 40) // len(colors)
    for i, (name, col) in enumerate(colors):
        x0 = 20 + i * block_w
        x1 = x0 + block_w - 6
        draw.rectangle([(x0, 45), (x1, 135)], fill=col, outline=(255, 255, 255), width=1)

    # Continuous Rainbow Hue Spectrum
    grad_arr = np.zeros((50, width - 40, 3), dtype=np.uint8)
    for x in range(width - 40):
        hue = (x / (width - 40)) * 360.0
        c = 1.0
        hp = hue / 60.0
        x_val = c * (1.0 - abs((hp % 2) - 1.0))
        if 0 <= hp < 1:
            r, g, b = c, x_val, 0
        elif 1 <= hp < 2:
            r, g, b = x_val, c, 0
        elif 2 <= hp < 3:
            r, g, b = 0, c, x_val
        elif 3 <= hp < 4:
            r, g, b = 0, x_val, c
        elif 4 <= hp < 5:
            r, g, b = x_val, 0, c
        else:
            r, g, b = c, 0, x_val
        grad_arr[:, x, 0] = int(r * 255)
        grad_arr[:, x, 1] = int(g * 255)
        grad_arr[:, x, 2] = int(b * 255)

    grad_img = Image.fromarray(grad_arr)
    img.paste(grad_img, (20, 145))
    draw.rectangle([(20, 145), (width - 20, 195)], outline=(255, 255, 255), width=1)

    # Grayscale Ramp
    gray_steps = 8
    g_block_w = (width - 40) // gray_steps
    for i in range(gray_steps):
        val = int((i / (gray_steps - 1)) * 255)
        x0 = 20 + i * g_block_w
        x1 = x0 + g_block_w - 4
        draw.rectangle([(x0, 205), (x1, 265)], fill=(val, val, val), outline=(100, 116, 139), width=1)

    # Natural Swatches
    natural_tones = [
        ("Skin Pale", (255, 219, 172)),
        ("Skin Olive", (198, 134, 66)),
        ("Skin Dark", (141, 85, 36)),
        ("Sky Blue", (135, 206, 235)),
        ("Foliage Green", (34, 139, 34)),
        ("Deep Orange", (255, 69, 0)),
        ("Lavender", (186, 85, 211)),
        ("Teal", (0, 128, 128)),
    ]
    n_block_w = (width - 40) // len(natural_tones)
    for i, (name, col) in enumerate(natural_tones):
        x0 = 20 + i * n_block_w
        x1 = x0 + n_block_w - 4
        draw.rectangle([(x0, 275), (x1, 370)], fill=col, outline=(51, 65, 85), width=1)

    # Resolution Pattern
    pat_w = width - 40
    pat_y0 = 380
    pat_y1 = 465
    draw.rectangle([(20, pat_y0), (20 + pat_w, pat_y1)], fill=(0, 0, 0), outline=(255, 255, 255), width=1)
    for x in range(25, 180, 4):
        draw.line([(x, pat_y0 + 5), (x, pat_y1 - 5)], fill=(255, 255, 255), width=2)
    for y in range(pat_y0 + 5, pat_y1 - 5, 4):
        draw.line([(200, y), (355, y)], fill=(255, 255, 255), width=2)

    cx, cy = 440, (pat_y0 + pat_y1) // 2
    for r in range(35, 5, -6):
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(255, 255, 255), width=2)

    for offset in range(0, 80):
        color_grad = (int(offset * 3.1), int(255 - offset * 3.1), 180)
        draw.line([(520 + offset, pat_y0 + 5), (520 + offset, pat_y1 - 5)], fill=color_grad, width=2)

    return img


def create_scenery_test_image(width: int = 640, height: int = 480) -> Image.Image:
    """Synthesizes a realistic landscape test scene."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Sunset Sky
    sky_arr = np.zeros((int(height * 0.6), width, 3), dtype=np.uint8)
    for y in range(sky_arr.shape[0]):
        ratio = y / sky_arr.shape[0]
        r = int(20 * (1 - ratio) + 255 * ratio)
        g = int(50 * (1 - ratio) + 160 * ratio)
        b = int(120 * (1 - ratio) + 60 * ratio)
        sky_arr[y, :, :] = [r, g, b]

    sky_img = Image.fromarray(sky_arr)
    img.paste(sky_img, (0, 0))

    # Sun
    sun_cx, sun_cy = int(width * 0.7), int(height * 0.35)
    for r in range(60, 0, -5):
        draw.ellipse(
            [(sun_cx - r, sun_cy - r), (sun_cx + r, sun_cy + r)],
            fill=(255, 235, 150) if r < 30 else (255, 180, 80)
        )

    # Mountains
    mountain_pts_back = [
        (0, int(height * 0.55)), (int(width * 0.2), int(height * 0.38)),
        (int(width * 0.45), int(height * 0.48)), (int(width * 0.65), int(height * 0.36)),
        (int(width * 0.85), int(height * 0.46)), (width, int(height * 0.40)),
        (width, height), (0, height)
    ]
    draw.polygon(mountain_pts_back, fill=(70, 60, 105))

    mountain_pts_mid = [
        (0, int(height * 0.52)), (int(width * 0.3), int(height * 0.44)),
        (int(width * 0.55), int(height * 0.52)), (int(width * 0.8), int(height * 0.42)),
        (width, int(height * 0.50)), (width, height), (0, height)
    ]
    draw.polygon(mountain_pts_mid, fill=(45, 80, 95))

    # Hills
    hill_pts_1 = [
        (0, int(height * 0.62)), (int(width * 0.4), int(height * 0.58)),
        (int(width * 0.75), int(height * 0.66)), (width, int(height * 0.60)),
        (width, height), (0, height)
    ]
    draw.polygon(hill_pts_1, fill=(34, 139, 34))

    hill_pts_2 = [
        (0, int(height * 0.72)), (int(width * 0.35), int(height * 0.66)),
        (int(width * 0.7), int(height * 0.74)), (width, int(height * 0.68)),
        (width, height), (0, height)
    ]
    draw.polygon(hill_pts_2, fill=(46, 170, 50))

    # Lake
    lake_pts = [
        (0, int(height * 0.78)), (int(width * 0.5), int(height * 0.75)),
        (width, int(height * 0.82)), (width, int(height * 0.94)), (0, int(height * 0.96))
    ]
    draw.polygon(lake_pts, fill=(30, 110, 180))

    for y_refl in range(int(height * 0.79), int(height * 0.92), 6):
        draw.line([(int(width * 0.55), y_refl), (int(width * 0.8), y_refl)], fill=(255, 200, 100), width=2)

    # Meadow
    meadow_pts = [(0, int(height * 0.93)), (int(width * 0.4), int(height * 0.88)), (width, int(height * 0.91)), (width, height), (0, height)]
    draw.polygon(meadow_pts, fill=(20, 100, 25))

    np.random.seed(42)
    flower_colors = [(255, 50, 50), (255, 230, 0), (230, 50, 230), (50, 220, 255), (255, 140, 0)]
    for _ in range(80):
        fx = int(np.random.uniform(0, width))
        fy = int(np.random.uniform(int(height * 0.89), height - 5))
        f_col = flower_colors[np.random.randint(len(flower_colors))]
        r = np.random.randint(2, 5)
        draw.ellipse([(fx - r, fy - r), (fx + r, fy + r)], fill=f_col)

    return img


def create_comparison_grid(
    original_image: Image.Image,
    conversions: Dict[str, np.ndarray],
    output_path: Optional[str] = None
) -> Image.Image:
    """Creates a composite multi-panel comparison grid with labeled banners."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    target_w, target_h = 400, 300
    orig_resized = original_image.resize((target_w, target_h), Image.Resampling.LANCZOS)

    items = [("Original RGB", orig_resized)]
    for label, gray_arr in conversions.items():
        if isinstance(gray_arr, np.ndarray):
            gray_img = Image.fromarray(gray_arr).resize((target_w, target_h), Image.Resampling.LANCZOS)
        elif isinstance(gray_arr, Image.Image):
            gray_img = gray_arr.resize((target_w, target_h), Image.Resampling.LANCZOS)
        else:
            gray_img = Image.fromarray(np.array(gray_arr, dtype=np.uint8)).resize((target_w, target_h), Image.Resampling.LANCZOS)
        items.append((label, gray_img))

    cols = 3
    rows = (len(items) + cols - 1) // cols
    margin = 15
    header_h = 35
    total_w = cols * target_w + (cols + 1) * margin
    total_h = rows * (target_h + header_h) + (rows + 1) * margin + 50

    composite = Image.new("RGB", (total_w, total_h), color=(15, 23, 42))
    draw = ImageDraw.Draw(composite)

    try:
        font_title = ImageFont.load_default(size=20)
        font_card = ImageFont.load_default(size=14)
    except Exception:
        font_title = ImageFont.load_default()
        font_card = ImageFont.load_default()

    draw.text(
        (total_w // 2, 25),
        "RGB TO GREYSCALE ALGORITHMIC COMPARISON BENCHMARK",
        fill=(248, 250, 252),
        font=font_title,
        anchor="mm"
    )

    for idx, (label, img_panel) in enumerate(items):
        r = idx // cols
        c = idx % cols
        x = margin + c * (target_w + margin)
        y = 55 + margin + r * (target_h + header_h + margin)

        draw.rectangle([(x - 2, y - 2), (x + target_w + 2, y + target_h + header_h + 2)], fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.rectangle([(x, y), (x + target_w, y + header_h)], fill=(51, 65, 85))
        draw.text((x + target_w // 2, y + header_h // 2), label, fill=(255, 255, 255), font=font_card, anchor="mm")
        composite.paste(img_panel, (x, y + header_h))

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        composite.save(output_path, "PNG")

    return composite


def compute_image_statistics(image_arr: np.ndarray) -> Dict[str, float]:
    arr = image_arr.astype(np.float64)
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))

    hist, _ = np.histogram(image_arr.flatten(), bins=256, range=(0, 256), density=True)
    hist = hist[hist > 0]
    entropy = float(-np.sum(hist * np.log2(hist))) if len(hist) > 0 else 0.0

    return {
        "mean": round(mean_val, 2),
        "std_dev": round(std_val, 2),
        "min": round(min_val, 2),
        "max": round(max_val, 2),
        "entropy": round(entropy, 4),
    }
