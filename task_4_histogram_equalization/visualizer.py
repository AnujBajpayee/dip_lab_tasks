"""
Visualizer & Composite Grid Generator for Histogram Equalization
=================================================================
Synthesizes low-contrast & challenging illumination test images, computes
histogram distribution plots, and creates side-by-side comparison grids
with explicit mathematical formulas.
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

from task_4_histogram_equalization.histogram import compute_histogram, compute_cdf


EQUALIZATION_METADATA: Dict[str, Dict[str, str]] = {
    "Original (Low Contrast)": {
        "title": "1. Original Low-Contrast Input",
        "formula": "Narrow Dynamic Range: r_k ∈ [r_min, r_max]",
        "desc": "Poor Visibility • Compact Histogram Distribution"
    },
    "Global HE (GHE)": {
        "title": "2. Global Histogram Equalization (GHE)",
        "formula": "s_k = round( 255 · [CDF(r_k) - CDF_min] / [N - CDF_min] )",
        "desc": "Linearized CDF • Maximizes Global Contrast (May Overamplify Noise)"
    },
    "Bi-Histogram Equalization (BBHE)": {
        "title": "3. Brightness Preserving HE (BBHE)",
        "formula": "Split at mean μ: H_L ∈ [0, μ] & H_U ∈ [μ+1, 255]",
        "desc": "Preserves Natural Mean Brightness • Prevents Washout"
    },
    "CLAHE (Adaptive Local)": {
        "title": "4. Contrast Limited Adaptive HE (CLAHE)",
        "formula": "Tile-Clipped CDF + Bilinear Interp (Limit=2.5, Tiles=8x8)",
        "desc": "Local Texture Enhancement • Strict Noise Containment"
    },
    "Color HSV Equalization": {
        "title": "5. Color-Preserving Equalization (HSV V-Channel)",
        "formula": "V_new = CLAHE(V_old) • RGB_new = RGB · (V_new / V_old)",
        "desc": "Enhances Luminance while Preserving Exact Chrominance/Hue"
    },
    "Histogram Matching": {
        "title": "6. Histogram Matching / Specification",
        "formula": "z = G^-1( T(r) ) where G(z) is Target CDF",
        "desc": "Directs Intensity Histogram toward Specified Target Curve"
    },
}


def _get_fonts() -> Tuple[Any, Any, Any, Any]:
    try:
        font_title = ImageFont.load_default(size=18)
        font_card_title = ImageFont.load_default(size=13)
        font_card_formula = ImageFont.load_default(size=11)
        font_card_desc = ImageFont.load_default(size=10)
    except Exception:
        font_title = ImageFont.load_default()
        font_card_title = ImageFont.load_default()
        font_card_formula = ImageFont.load_default()
        font_card_desc = ImageFont.load_default()
    return font_title, font_card_title, font_card_formula, font_card_desc


# =============================================================================
# 1. Low-Contrast Test Image Synthesizers
# =============================================================================

def create_low_contrast_scene(width: int = 640, height: int = 480) -> Image.Image:
    """
    Synthesizes an under-exposed, dark, low-contrast nighttime scene with hidden details:
    - Dark background (intensities 10 to 45)
    - Hidden architectural structures, text, and geometric shapes
    - Faint gradients and fine textures in shadows
    """
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy are required.")

    img = Image.new("L", (width, height), color=15)
    draw = ImageDraw.Draw(img)

    # 1. Subtle horizontal gradient in shadows (10 to 40)
    base_arr = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            base_val = 15 + int(20 * math.sin(x / 80.0) * math.cos(y / 60.0))
            base_arr[y, x] = max(5, min(45, base_val))
    img = Image.fromarray(base_arr)
    draw = ImageDraw.Draw(img)

    # 2. Hidden room / doorway contours (intensities 25 to 55)
    door_w, door_h = 160, 240
    dx0, dy0 = width // 2 - door_w // 2, height - door_h - 40
    draw.rectangle([(dx0, dy0), (dx0 + door_w, dy0 + door_h)], fill=35, outline=48, width=2)
    draw.rectangle([(dx0 + 20, dy0 + 30), (dx0 + door_w - 20, dy0 + door_h - 20)], fill=22, outline=40, width=1)

    # 3. Faint concentric rings in top-left (hidden moonlight halo)
    cx, cy = 140, 130
    for r in range(80, 0, -8):
        val = 42 if (r // 8) % 2 == 0 else 24
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=val, width=2)

    # 4. Hidden fine text message in deep shadows (intensity 48 vs background 20)
    font_title, _, font_formula, _ = _get_fonts()
    draw.text((width // 2, dy0 + 70), "HIDDEN DETAILS", fill=48, font=font_title, anchor="mm")
    draw.text((width // 2, dy0 + 105), "Low-Contrast Shadow Target", fill=44, font=font_formula, anchor="mm")
    draw.text((width // 2, dy0 + 135), "Equalization Uncovers Features", fill=42, font=font_formula, anchor="mm")

    # 5. Fine resolution grid pattern (bottom right)
    rx0, ry0 = width - 200, height - 160
    draw.rectangle([(rx0, ry0), (width - 30, height - 40)], fill=28, outline=45, width=1)
    for lx in range(rx0 + 10, width - 30, 10):
        draw.line([(lx, ry0 + 5), (lx, height - 45)], fill=50, width=1)

    return img


def create_uneven_illumination_scene(width: int = 640, height: int = 480) -> Image.Image:
    """
    Synthesizes an unevenly illuminated scene (harsh light on left, deep shadows on right).
    Demonstrates why GHE washes out, while CLAHE perfectly balances both regions.
    """
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    img = Image.new("L", (width, height))
    arr = np.zeros((height, width), dtype=np.uint8)

    # Gradient from bright left (230) to pitch dark right (15)
    for x in range(width):
        lighting = 220 * (1.0 - (x / width)) + 15
        for y in range(height):
            # Add texture & pattern
            pattern = 25 * math.sin(x / 15.0) * math.cos(y / 15.0)
            val = lighting + pattern
            arr[y, x] = max(0, min(255, int(val)))

    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    _, font_card_title, font_card_formula, _ = _get_fonts()

    # Bright side object
    draw.rectangle([(60, 120), (200, 320)], fill=240, outline=255, width=2)
    draw.text((130, 220), "BRIGHT ZONE", fill=180, font=font_card_title, anchor="mm")

    # Dark side hidden object
    draw.rectangle([(width - 200, 120), (width - 60, 320)], fill=32, outline=48, width=2)
    draw.text((width - 130, 220), "DARK ZONE", fill=52, font=font_card_title, anchor="mm")

    return img


# =============================================================================
# 2. Histogram Graph Plotter (Embedded Visual Curves)
# =============================================================================

def draw_histogram_bar(image_arr: np.ndarray, width: int = 380, height: int = 70) -> Image.Image:
    """Draws a mini 256-bin histogram and cumulative CDF curve on a dark background."""
    hist = compute_histogram(image_arr, bins=256)
    cdf = compute_cdf(hist)
    max_hist = max(1, max(hist))
    max_cdf = max(1.0, cdf[-1])

    plot_img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(plot_img)

    # Draw subtle background grid
    draw.line([(0, height - 1), (width, height - 1)], fill=(51, 65, 85), width=1)
    draw.line([(0, 0), (width, 0)], fill=(51, 65, 85), width=1)

    # Histogram Bars (Cyan)
    for x in range(width):
        bin_idx = int((x / width) * 255)
        bar_h = int((hist[bin_idx] / max_hist) * (height - 8))
        if bar_h > 0:
            draw.line([(x, height - 2), (x, height - 2 - bar_h)], fill=(56, 189, 248), width=1)

    # CDF Curve (Yellow-Orange Line)
    cdf_pts = []
    for x in range(0, width, 2):
        bin_idx = int((x / width) * 255)
        cdf_y = height - 2 - int((cdf[bin_idx] / max_cdf) * (height - 10))
        cdf_pts.append((x, cdf_y))

    if len(cdf_pts) > 1:
        draw.line(cdf_pts, fill=(251, 146, 60), width=2)

    return plot_img


# =============================================================================
# 3. Composite Equalization Comparison Grid
# =============================================================================

def create_histogram_comparison_grid(
    original_image: Image.Image,
    equalized_dict: Dict[str, np.ndarray],
    output_path: Optional[str] = None
) -> Image.Image:
    """
    Creates a multi-panel labeled composite comparison grid showing the Original image
    and all Histogram Equalization variants with embedded histogram/CDF graphs and formulas.
    """
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    target_w, target_h = 380, 240
    plot_h = 60

    items: List[Tuple[str, Image.Image, np.ndarray]] = []

    # Original
    orig_np = np.array(original_image.convert("L"))
    orig_resized = original_image.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    items.append(("Original (Low Contrast)", orig_resized, orig_np))

    for label, eq_arr in equalized_dict.items():
        if eq_arr.ndim == 3:
            eq_img = Image.fromarray(eq_arr).resize((target_w, target_h), Image.Resampling.LANCZOS)
            gray_for_hist = np.array(Image.fromarray(eq_arr).convert("L"))
        else:
            eq_img = Image.fromarray(eq_arr).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
            gray_for_hist = eq_arr
        items.append((label, eq_img, gray_for_hist))

    cols = 2 if len(items) <= 4 else 3
    rows = (len(items) + cols - 1) // cols
    margin = 16
    header_h = 52
    card_h = target_h + plot_h + header_h

    total_w = cols * target_w + (cols + 1) * margin
    total_h = rows * card_h + (rows + 1) * margin + 65

    composite = Image.new("RGB", (total_w, total_h), color=(15, 23, 42))
    draw = ImageDraw.Draw(composite)

    font_title, font_card_title, font_card_formula, font_card_desc = _get_fonts()

    draw.text(
        (total_w // 2, 32),
        "HISTOGRAM EQUALIZATION TYPES & EXECUTION BENCHMARK",
        fill=(248, 250, 252),
        font=font_title,
        anchor="mm"
    )

    for idx, (label, img_panel, hist_arr) in enumerate(items):
        r = idx // cols
        c = idx % cols
        x = margin + c * (target_w + margin)
        y = 65 + margin + r * (card_h + margin)

        meta = EQUALIZATION_METADATA.get(label, {
            "title": label,
            "formula": "Histogram Transformation",
            "desc": ""
        })

        # Card container
        draw.rectangle([(x - 2, y - 2), (x + target_w + 2, y + card_h + 2)], fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.rectangle([(x, y), (x + target_w, y + header_h)], fill=(51, 65, 85))

        # Title & Formula labels
        draw.text((x + target_w // 2, y + 14), meta["title"], fill=(255, 255, 255), font=font_card_title, anchor="mm")
        draw.text((x + target_w // 2, y + 30), meta["formula"], fill=(253, 224, 71), font=font_card_formula, anchor="mm")
        draw.text((x + target_w // 2, y + 43), meta["desc"], fill=(148, 163, 184), font=font_card_desc, anchor="mm")

        # Paste Enhanced Image
        composite.paste(img_panel, (x, y + header_h))

        # Draw & Paste Histogram/CDF Plot at the bottom of the card
        hist_plot = draw_histogram_bar(hist_arr, width=target_w, height=plot_h)
        composite.paste(hist_plot, (x, y + header_h + target_h))

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        composite.save(output_path, "PNG")

    return composite
