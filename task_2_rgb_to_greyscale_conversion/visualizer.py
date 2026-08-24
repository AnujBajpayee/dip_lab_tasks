"""
Image Processing Visualizers, Test Image Synthesizers & Comparison Grids
========================================================================
Generates test images and creates labeled side-by-side comparison grids
for multiple RGB-to-Greyscale conversion methods with explicit formulas.
"""

from __future__ import annotations
import os
import math
from typing import Dict, Any, Optional, Tuple, List

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


METHOD_METADATA: Dict[str, Dict[str, str]] = {
    "Original RGB": {
        "title": "Original RGB Input",
        "formula": "Trichromatic Vector: [R, G, B]",
        "desc": "Full 24-Bit Color Space (8-Bit per Channel)"
    },
    "Rec.601 Luminosity": {
        "title": "ITU-R BT.601 (SDTV / NTSC / PAL)",
        "formula": "Y = 0.299·R + 0.587·G + 0.114·B",
        "desc": "Weights: 29.9% Red • 58.7% Green • 11.4% Blue"
    },
    "Rec.709 Luminosity": {
        "title": "ITU-R BT.709 (HDTV / sRGB Monitors)",
        "formula": "Y = 0.2126·R + 0.7152·G + 0.0722·B",
        "desc": "Weights: 21.3% Red • 71.5% Green • 7.2% Blue"
    },
    "Simple Average": {
        "title": "Simple Arithmetic Average",
        "formula": "Y = (R + G + B) / 3",
        "desc": "Equal 33.3% Weighting (Unweighted Mean)"
    },
    "HSL Lightness": {
        "title": "HSL Lightness (Desaturation)",
        "formula": "Y = [max(R,G,B) + min(R,G,B)] / 2",
        "desc": "Midrange of Extremal RGB Channels"
    },
    "Gamma-Corrected Linear": {
        "title": "Gamma-Corrected Linear Luma (γ=2.2)",
        "formula": "Y = [0.2126·R^γ + 0.7152·G^γ + 0.0722·B^γ]^(1/γ)",
        "desc": "Radiometric Radiant Flux Energy Conservation"
    },
    "Gamma-Corrected": {
        "title": "Gamma-Corrected Linear Luma (γ=2.2)",
        "formula": "Y = [0.2126·R^γ + 0.7152·G^γ + 0.0722·B^γ]^(1/γ)",
        "desc": "Radiometric Radiant Flux Energy Conservation"
    },
    "Red Channel": {
        "title": "Red Channel Extraction",
        "formula": "Y = R",
        "desc": "Long Wavelength Spectrum (600–700 nm, L-Cones)"
    },
    "Green Channel": {
        "title": "Green Channel Extraction",
        "formula": "Y = G",
        "desc": "Peak Photopic Sensitivity (500–600 nm, M-Cones)"
    },
    "Blue Channel": {
        "title": "Blue Channel Extraction",
        "formula": "Y = B",
        "desc": "Short Wavelength Spectrum (400–500 nm, S-Cones)"
    },
}


def _get_fonts() -> Tuple[Any, Any, Any, Any]:
    try:
        font_title = ImageFont.load_default(size=20)
        font_card_title = ImageFont.load_default(size=14)
        font_card_formula = ImageFont.load_default(size=12)
        font_card_desc = ImageFont.load_default(size=10)
    except Exception:
        font_title = ImageFont.load_default()
        font_card_title = ImageFont.load_default()
        font_card_formula = ImageFont.load_default()
        font_card_desc = ImageFont.load_default()
    return font_title, font_card_title, font_card_formula, font_card_desc


def create_color_palette_test_image(width: int = 640, height: int = 480) -> Image.Image:
    """Synthesizes a standardized calibrated RGB color test target."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy are required.")

    img = Image.new("RGB", (width, height), color=(20, 24, 33))
    draw = ImageDraw.Draw(img)

    margin = max(10, int(width * 0.03))
    header_h = max(24, int(height * 0.07))

    draw.rectangle([(0, 0), (width, header_h)], fill=(15, 23, 42))
    font_title, font_card_title, font_card_formula, _ = _get_fonts()

    draw.text((width // 2, header_h // 2), "CALIBRATED RGB COLOR TEST TARGET", fill=(241, 245, 249), font=font_title, anchor="mm")

    # Primary & Secondary Colors
    colors = [
        ("Red (255,0,0)", (255, 0, 0)),
        ("Green (0,255,0)", (0, 255, 0)),
        ("Blue (0,0,255)", (0, 0, 255)),
        ("Yellow (255,255,0)", (255, 255, 0)),
        ("Cyan (0,255,255)", (0, 255, 255)),
        ("Magenta (255,0,255)", (255, 0, 255)),
    ]
    block_w = (width - 2 * margin) // len(colors)
    for i, (name, col) in enumerate(colors):
        x0 = margin + i * block_w
        x1 = x0 + block_w - 4
        draw.rectangle([(x0, header_h + 8), (x1, header_h + 95)], fill=col, outline=(255, 255, 255), width=1)

    # Continuous Rainbow Hue Spectrum
    grad_y0 = header_h + 105
    grad_h = max(35, int(height * 0.10))
    grad_w = width - 2 * margin
    grad_arr = np.zeros((grad_h, grad_w, 3), dtype=np.uint8)
    for x in range(grad_w):
        hue = (x / max(1, grad_w - 1)) * 360.0
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
    img.paste(grad_img, (margin, grad_y0))
    draw.rectangle([(margin, grad_y0), (margin + grad_w, grad_y0 + grad_h)], outline=(255, 255, 255), width=1)

    # Grayscale Ramp (8 steps)
    gray_y0 = grad_y0 + grad_h + 8
    gray_h = max(35, int(height * 0.10))
    gray_steps = 8
    g_block_w = grad_w // gray_steps
    for i in range(gray_steps):
        val = int((i / (gray_steps - 1)) * 255)
        x0 = margin + i * g_block_w
        x1 = x0 + g_block_w - 4
        draw.rectangle([(x0, gray_y0), (x1, gray_y0 + gray_h)], fill=(val, val, val), outline=(100, 116, 139), width=1)

    # Natural Swatches
    swatch_y0 = gray_y0 + gray_h + 8
    swatch_h = max(55, int(height * 0.16))
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
    n_block_w = grad_w // len(natural_tones)
    for i, (name, col) in enumerate(natural_tones):
        x0 = margin + i * n_block_w
        x1 = x0 + n_block_w - 4
        draw.rectangle([(x0, swatch_y0), (x1, swatch_y0 + swatch_h)], fill=col, outline=(51, 65, 85), width=1)

    # Resolution Pattern
    pat_y0 = swatch_y0 + swatch_h + 8
    pat_h = height - pat_y0 - margin
    if pat_h > 20:
        draw.rectangle([(margin, pat_y0), (margin + grad_w, pat_y0 + pat_h)], fill=(0, 0, 0), outline=(255, 255, 255), width=1)
        for x in range(margin + 5, margin + int(grad_w * 0.3), 6):
            draw.line([(x, pat_y0 + 4), (x, pat_y0 + pat_h - 4)], fill=(255, 255, 255), width=2)
        cx, cy = margin + int(grad_w * 0.6), pat_y0 + pat_h // 2
        for r in range(min(35, pat_h // 2 - 4), 4, -6):
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(255, 255, 255), width=2)

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
        ratio = y / max(1, sky_arr.shape[0])
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

    # Lake
    lake_pts = [
        (0, int(height * 0.78)), (int(width * 0.5), int(height * 0.75)),
        (width, int(height * 0.82)), (width, int(height * 0.94)), (0, int(height * 0.96))
    ]
    draw.polygon(lake_pts, fill=(30, 110, 180))

    # Meadow
    meadow_pts = [(0, int(height * 0.93)), (int(width * 0.4), int(height * 0.88)), (width, int(height * 0.91)), (width, height), (0, height)]
    draw.polygon(meadow_pts, fill=(20, 100, 25))

    return img


def create_comparison_grid(
    original_image: Image.Image,
    conversions: Dict[str, np.ndarray],
    output_path: Optional[str] = None
) -> Image.Image:
    """Creates a composite multi-panel comparison grid with explicitly labeled operation formulas."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    target_w, target_h = 380, 260
    orig_resized = original_image.resize((target_w, target_h), Image.Resampling.LANCZOS)

    items: List[Tuple[str, Image.Image]] = [("Original RGB", orig_resized)]
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
    margin = 16
    header_h = 52
    total_w = cols * target_w + (cols + 1) * margin
    total_h = rows * (target_h + header_h) + (rows + 1) * margin + 60

    composite = Image.new("RGB", (total_w, total_h), color=(15, 23, 42))
    draw = ImageDraw.Draw(composite)

    font_title, font_card_title, font_card_formula, font_card_desc = _get_fonts()

    draw.text(
        (total_w // 2, 30),
        "RGB TO GREYSCALE ALGORITHMIC CONVERSION & FORMULA BENCHMARK",
        fill=(248, 250, 252),
        font=font_title,
        anchor="mm"
    )

    for idx, (label, img_panel) in enumerate(items):
        r = idx // cols
        c = idx % cols
        x = margin + c * (target_w + margin)
        y = 60 + margin + r * (target_h + header_h + margin)

        meta = METHOD_METADATA.get(label, {
            "title": label,
            "formula": "Pixel Conversion Operation",
            "desc": ""
        })

        # Card container
        draw.rectangle([(x - 2, y - 2), (x + target_w + 2, y + target_h + header_h + 2)], fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.rectangle([(x, y), (x + target_w, y + header_h)], fill=(51, 65, 85))

        # Title and explicit Formula text
        draw.text((x + target_w // 2, y + 14), meta["title"], fill=(255, 255, 255), font=font_card_title, anchor="mm")
        draw.text((x + target_w // 2, y + 30), meta["formula"], fill=(253, 224, 71), font=font_card_formula, anchor="mm")
        draw.text((x + target_w // 2, y + 43), meta["desc"], fill=(148, 163, 184), font=font_card_desc, anchor="mm")

        composite.paste(img_panel.convert("RGB"), (x, y + header_h))

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
