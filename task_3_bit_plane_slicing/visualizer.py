"""
Visualizer, Synthesizer & Composite Grid Generator for Bit Plane Slicing
========================================================================
Generates calibrated test targets, binary security watermarks, and composite
comparison grids for bit planes, cumulative reconstructions, and steganography
with explicit mathematical formulas and operation labels.
"""

from __future__ import annotations
import os
import math
from typing import List, Tuple, Dict, Any, Optional

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

from task_3_bit_plane_slicing.bit_plane import (
    BIT_WEIGHTS,
    BIT_ENERGY_PERCENTAGES,
    compute_mse_psnr
)


def _get_fonts() -> Tuple[Any, Any, Any, Any]:
    """Helper to safely load default fonts across platforms."""
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
# 1. Test Pattern & Watermark Synthesizers
# =============================================================================

def create_rich_test_pattern(width: int = 640, height: int = 480) -> Image.Image:
    """Synthesizes a rich calibrated test target engineered specifically for bit plane analysis."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy are required.")

    img = Image.new("L", (width, height), color=20)
    draw = ImageDraw.Draw(img)
    font_title, font_card_title, font_card_formula, _ = _get_fonts()

    margin = max(10, int(width * 0.03))
    header_h = max(24, int(height * 0.07))

    # 1. Header Banner
    draw.rectangle([(0, 0), (width, header_h)], fill=0)
    draw.text((width // 2, header_h // 2), "CALIBRATED BIT-PLANE DECOMPOSITION TEST TARGET", fill=255, font=font_title, anchor="mm")

    # 2. Continuous 0 to 255 Gradient Ramp
    ramp_y0 = header_h + 8
    ramp_h = max(25, int(height * 0.09))
    ramp_w = width - 2 * margin
    grad_arr = np.zeros((ramp_h, ramp_w), dtype=np.uint8)
    for x in range(ramp_w):
        grad_arr[:, x] = int((x / max(1, ramp_w - 1)) * 255)
    grad_img = Image.fromarray(grad_arr)
    img.paste(grad_img, (margin, ramp_y0))
    draw.rectangle([(margin, ramp_y0), (margin + ramp_w, ramp_y0 + ramp_h)], outline=255, width=1)

    # 3. Discrete Stepped Intensity Blocks (16 steps)
    steps = 16
    step_y0 = ramp_y0 + ramp_h + 8
    step_h = max(25, int(height * 0.09))
    block_w = ramp_w // steps
    for i in range(steps):
        val = int(i * (255 / (steps - 1)))
        x0 = margin + i * block_w
        x1 = x0 + block_w - 2
        draw.rectangle([(x0, step_y0), (x1, step_y0 + step_h)], fill=val, outline=180, width=1)

    # Mid section split into 3 zones
    mid_y0 = step_y0 + step_h + 10
    mid_h = max(80, int(height * 0.32))
    zone_w = (width - 4 * margin) // 3

    # 4. Zone 1: Concentric Rings
    z1_x0 = margin
    cx = z1_x0 + zone_w // 2
    cy = mid_y0 + mid_h // 2 - 8
    max_r = min(zone_w // 2 - 6, mid_h // 2 - 16)
    if max_r > 8:
        for r in range(max_r, 0, -max(3, max_r // 12)):
            val = 255 if ((r // max(3, max_r // 12)) % 2 == 0) else 40
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=val, width=2)
    draw.text((cx, mid_y0 + mid_h - 6), "Zone Rings", fill=220, font=font_card_formula, anchor="mm")

    # 5. Zone 2: Starburst Lines
    z2_x0 = margin * 2 + zone_w
    sx = z2_x0 + zone_w // 2
    sy = cy
    radius = max_r
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        ex = sx + int(radius * math.cos(rad))
        ey = sy + int(radius * math.sin(rad))
        col = 255 if (deg // 15) % 2 == 0 else 80
        draw.line([(sx, sy), (ex, ey)], fill=col, width=2)
    draw.text((sx, mid_y0 + mid_h - 6), "Radial Lines", fill=220, font=font_card_formula, anchor="mm")

    # 6. Zone 3: Smooth 2D Sine Surface + Subtle Low-Bit Noise
    z3_x0 = margin * 3 + 2 * zone_w
    grid_w = zone_w
    grid_h = mid_h - 20
    np.random.seed(2026)
    x_coords = np.linspace(0, 4 * np.pi, max(1, grid_w))
    y_coords = np.linspace(0, 4 * np.pi, max(1, grid_h))
    xx, yy = np.meshgrid(x_coords, y_coords)
    sine_surface = (np.sin(xx) * np.cos(yy) + 1.0) * 0.5 * 240.0
    noise = np.random.randint(0, 4, (grid_h, grid_w))
    synth_patch = np.clip(sine_surface + noise, 0, 255).astype(np.uint8)
    img.paste(Image.fromarray(synth_patch), (z3_x0, mid_y0))
    draw.rectangle([(z3_x0, mid_y0), (z3_x0 + grid_w, mid_y0 + grid_h)], outline=255, width=1)
    draw.text((z3_x0 + grid_w // 2, mid_y0 + mid_h - 6), "Sine + Noise (b0..b1)", fill=220, font=font_card_formula, anchor="mm")

    # Bottom section
    bot_y0 = mid_y0 + mid_h + 10
    bot_h = height - bot_y0 - margin
    if bot_h > 30:
        col_w = (width - 3 * margin) // 2

        # 7. Left Bottom: Natural Gradient Scenery Wave
        p_arr = np.zeros((bot_h, col_w), dtype=np.uint8)
        for y in range(bot_h):
            for x in range(col_w):
                v = int(128 + 60 * math.sin(x / 15.0) + 50 * math.cos(y / 20.0))
                p_arr[y, x] = max(0, min(255, v))
        img.paste(Image.fromarray(p_arr), (margin, bot_y0))
        draw.rectangle([(margin, bot_y0), (margin + col_w, bot_y0 + bot_h)], outline=255, width=1)

        # 8. Right Bottom: Typography & Info Box
        r_x0 = margin * 2 + col_w
        draw.rectangle([(r_x0, bot_y0), (r_x0 + col_w, bot_y0 + bot_h)], fill=240, outline=255, width=1)
        draw.text((r_x0 + 10, bot_y0 + 10), "DIP LAB: TASK 3", fill=0, font=font_title)
        draw.text((r_x0 + 10, bot_y0 + 30), "Bit-Plane Slicing (b7..b0)", fill=40, font=font_card_title)
        if bot_h > 70:
            draw.text((r_x0 + 10, bot_y0 + 50), "MSB = Topological Geometry (b7)", fill=60, font=font_card_formula)
        if bot_h > 90:
            draw.text((r_x0 + 10, bot_y0 + 70), "LSB = Subtle Textures & Noise (b0)", fill=80, font=font_card_formula)

    return img


def create_watermark_pattern(width: int = 640, height: int = 480, label: str = "DIP LAB") -> Image.Image:
    """Synthesizes a high-contrast binary security watermark badge."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy are required.")

    img = Image.new("L", (width, height), color=0)
    draw = ImageDraw.Draw(img)

    font_title, font_card_title, _, _ = _get_fonts()

    margin = max(10, int(width * 0.05))
    draw.rectangle([(margin, margin), (width - margin, height - margin)], outline=255, width=max(2, int(width * 0.006)))

    cx, cy = width // 2, height // 2
    dx = int(width * 0.3)
    dy = int(height * 0.28)
    diamond_pts = [(cx, cy - dy), (cx + dx, cy), (cx, cy + dy), (cx - dx, cy)]
    draw.polygon(diamond_pts, outline=255, fill=0)

    draw.text((cx, cy - max(20, int(height * 0.08))), "AUTHENTICATED", fill=255, font=font_card_title, anchor="mm")
    draw.text((cx, cy), label, fill=255, font=font_title, anchor="mm")
    draw.text((cx, cy + max(20, int(height * 0.08))), "SECRET WATERMARK", fill=255, font=font_card_title, anchor="mm")

    return img


# =============================================================================
# 2. Composite Bit Plane Grid (9 Panels)
# =============================================================================

def create_bit_plane_grid(
    original_image: Image.Image,
    bit_planes_scaled: List[np.ndarray],
    output_path: Optional[str] = None
) -> Image.Image:
    """Creates a 3x3 labeled composite comparison grid showing the Original image and all 8 bit planes."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    target_w, target_h = 380, 260
    orig_gray = original_image.convert("L").resize((target_w, target_h), Image.Resampling.LANCZOS)

    panels: List[Tuple[str, str, str, Image.Image]] = [
        (
            "Original Input Image",
            "f(x, y) ∈ [0, 255] (8-Bit Grayscale)",
            "Full 256 Dynamic Range (100% Total Signal)",
            orig_gray
        )
    ]

    plane_roles = [
        "Pseudorandom Noise • Stego Carrier",
        "Sensor Thermal Noise • Micro Dither",
        "High-Frequency Texture & Roughness",
        "Fine Detail & Minor Spatial Variations",
        "Fine Midtones & Shading (50% Bitrate)",
        "Secondary Lighting & Shadow Falloffs",
        "Major Tonal Gradients & Surface Forms",
        "Topological Geometry & Structural Edges",
    ]

    for k in range(7, -1, -1):
        plane_arr = bit_planes_scaled[k]
        plane_img = Image.fromarray(plane_arr).resize((target_w, target_h), Image.Resampling.NEAREST)
        name = f"Bit Plane {k}" + (" (MSB)" if k == 7 else " (LSB)" if k == 0 else "")
        formula = f"Operation: bk = (f >> {k}) & 1"
        desc = f"Weight: 2^{k}={BIT_WEIGHTS[k]} • {BIT_ENERGY_PERCENTAGES[k]:.2f}% Energy • {plane_roles[k]}"
        panels.append((name, formula, desc, plane_img))

    cols = 3
    rows = (len(panels) + cols - 1) // cols
    margin = 16
    header_h = 52
    total_w = cols * target_w + (cols + 1) * margin
    total_h = rows * (target_h + header_h) + (rows + 1) * margin + 60

    composite = Image.new("RGB", (total_w, total_h), color=(15, 23, 42))
    draw = ImageDraw.Draw(composite)

    font_title, font_card_title, font_card_formula, font_card_desc = _get_fonts()

    draw.text(
        (total_w // 2, 30),
        "8-BIT PLANE SLICING & BITWISE DECOMPOSITION BENCHMARK",
        fill=(248, 250, 252),
        font=font_title,
        anchor="mm"
    )

    for idx, (title, formula, subtitle, img_panel) in enumerate(panels):
        r = idx // cols
        c = idx % cols
        x = margin + c * (target_w + margin)
        y = 60 + margin + r * (target_h + header_h + margin)

        # Card container
        draw.rectangle([(x - 2, y - 2), (x + target_w + 2, y + target_h + header_h + 2)], fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.rectangle([(x, y), (x + target_w, y + header_h)], fill=(51, 65, 85))

        draw.text((x + target_w // 2, y + 14), title, fill=(255, 255, 255), font=font_card_title, anchor="mm")
        draw.text((x + target_w // 2, y + 30), formula, fill=(253, 224, 71), font=font_card_formula, anchor="mm")
        draw.text((x + target_w // 2, y + 43), subtitle, fill=(148, 163, 184), font=font_card_desc, anchor="mm")

        composite.paste(img_panel.convert("RGB"), (x, y + header_h))

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        composite.save(output_path, "PNG")

    return composite


# =============================================================================
# 3. Cumulative Reconstruction Grid (9 Panels)
# =============================================================================

def create_cumulative_reconstruction_grid(
    original_image: Image.Image,
    cumulative_pairs: List[Tuple[str, np.ndarray]],
    output_path: Optional[str] = None
) -> Image.Image:
    """Creates a 3x3 composite grid showing progressive image reconstruction with explicit summation formulas."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    target_w, target_h = 380, 260
    orig_np = np.array(original_image.convert("L"))
    orig_resized = original_image.convert("L").resize((target_w, target_h), Image.Resampling.LANCZOS)

    panels: List[Tuple[str, str, str, Image.Image]] = [
        (
            "Reference Ground Truth",
            "f(x, y) = Sum_{k=0}^7 (2^k · bk)",
            "Original 8-Bit Image (Lossless Target)",
            orig_resized
        )
    ]

    reconstruct_formulas = [
        "Formula: f_hat = 128 · b7",
        "Formula: f_hat = 128·b7 + 64·b6",
        "Formula: f_hat = Sum_{k=5}^7 (2^k · bk)",
        "Formula: f_hat = Sum_{k=4}^7 (2^k · bk) [50% Compression]",
        "Formula: f_hat = Sum_{k=3}^7 (2^k · bk)",
        "Formula: f_hat = Sum_{k=2}^7 (2^k · bk)",
        "Formula: f_hat = Sum_{k=1}^7 (2^k · bk)",
        "Formula: f_hat = Sum_{k=0}^7 (2^k · bk) = f(x, y)",
    ]

    for idx, (label, recon_arr) in enumerate(cumulative_pairs):
        mse, psnr = compute_mse_psnr(orig_np, recon_arr)
        psnr_str = f"PSNR: {psnr:.2f} dB" if psnr != float("inf") else "PSNR: Lossless (inf)"
        formula = reconstruct_formulas[idx] if idx < len(reconstruct_formulas) else "Progressive Summation"
        desc = f"MSE: {mse:.1f} • {psnr_str}"
        recon_img = Image.fromarray(recon_arr).resize((target_w, target_h), Image.Resampling.NEAREST)
        panels.append((label, formula, desc, recon_img))

    cols = 3
    rows = (len(panels) + cols - 1) // cols
    margin = 16
    header_h = 52
    total_w = cols * target_w + (cols + 1) * margin
    total_h = rows * (target_h + header_h) + (rows + 1) * margin + 60

    composite = Image.new("RGB", (total_w, total_h), color=(15, 23, 42))
    draw = ImageDraw.Draw(composite)

    font_title, font_card_title, font_card_formula, font_card_desc = _get_fonts()

    draw.text(
        (total_w // 2, 30),
        "PROGRESSIVE MULTI-BIT RECONSTRUCTION & FORMULA BENCHMARK",
        fill=(248, 250, 252),
        font=font_title,
        anchor="mm"
    )

    for idx, (title, formula, subtitle, img_panel) in enumerate(panels):
        r = idx // cols
        c = idx % cols
        x = margin + c * (target_w + margin)
        y = 60 + margin + r * (target_h + header_h + margin)

        draw.rectangle([(x - 2, y - 2), (x + target_w + 2, y + target_h + header_h + 2)], fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.rectangle([(x, y), (x + target_w, y + header_h)], fill=(51, 65, 85))

        draw.text((x + target_w // 2, y + 14), title, fill=(255, 255, 255), font=font_card_title, anchor="mm")
        draw.text((x + target_w // 2, y + 30), formula, fill=(253, 224, 71), font=font_card_formula, anchor="mm")
        draw.text((x + target_w // 2, y + 43), subtitle, fill=(148, 163, 184), font=font_card_desc, anchor="mm")

        composite.paste(img_panel.convert("RGB"), (x, y + header_h))

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        composite.save(output_path, "PNG")

    return composite


# =============================================================================
# 4. Steganography Demonstration Grid (4 Panels)
# =============================================================================

def create_steganography_grid(
    cover_image: Image.Image,
    watermark_image: Image.Image,
    stego_image: np.ndarray,
    extracted_image: np.ndarray,
    output_path: Optional[str] = None
) -> Image.Image:
    """Creates a 2x2 side-by-side composite grid demonstrating LSB watermarking operations."""
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    target_w, target_h = 440, 310
    cover_np = np.array(cover_image.convert("L"))
    mse, psnr = compute_mse_psnr(cover_np, stego_image)

    panels = [
        (
            "Step 1: Original Cover Image",
            "Carrier Matrix: f(x, y) ∈ [0, 255]",
            "Standard 8-Bit Monochromatic Image",
            cover_image.convert("L")
        ),
        (
            "Step 2: Binary Watermark Payload",
            "Security Emblem: w(x, y) ∈ {0, 1}",
            "High-Contrast Binary Secret Authentication Key",
            watermark_image.convert("L")
        ),
        (
            "Step 3: LSB Stego Carrier Image",
            "Embedding: Stego = (f & ~1) | (w & 1)",
            f"Embedded in Bit 0 (LSB) • PSNR: {psnr:.2f} dB (Imperceptible)",
            Image.fromarray(stego_image)
        ),
        (
            "Step 4: Losslessly Extracted Watermark",
            "Extraction: Extracted = Stego & 1",
            "Decoded Directly from Bit Plane 0 (100% Lossless Recovery)",
            Image.fromarray(extracted_image)
        ),
    ]

    cols = 2
    rows = 2
    margin = 20
    header_h = 52
    total_w = cols * target_w + (cols + 1) * margin
    total_h = rows * (target_h + header_h) + (rows + 1) * margin + 65

    composite = Image.new("RGB", (total_w, total_h), color=(15, 23, 42))
    draw = ImageDraw.Draw(composite)

    font_title, font_card_title, font_card_formula, font_card_desc = _get_fonts()

    draw.text(
        (total_w // 2, 32),
        "LSB DIGITAL STEGANOGRAPHY & EMBEDDING/EXTRACTION PIPELINE",
        fill=(248, 250, 252),
        font=font_title,
        anchor="mm"
    )

    for idx, (title, formula, subtitle, img_panel) in enumerate(panels):
        r = idx // cols
        c = idx % cols
        x = margin + c * (target_w + margin)
        y = 65 + margin + r * (target_h + header_h + margin)

        draw.rectangle([(x - 2, y - 2), (x + target_w + 2, y + target_h + header_h + 2)], fill=(30, 41, 59), outline=(71, 85, 105), width=1)
        draw.rectangle([(x, y), (x + target_w, y + header_h)], fill=(51, 65, 85))

        draw.text((x + target_w // 2, y + 14), title, fill=(255, 255, 255), font=font_card_title, anchor="mm")
        draw.text((x + target_w // 2, y + 30), formula, fill=(253, 224, 71), font=font_card_formula, anchor="mm")
        draw.text((x + target_w // 2, y + 43), subtitle, fill=(148, 163, 184), font=font_card_desc, anchor="mm")

        resized_panel = img_panel.resize((target_w, target_h), Image.Resampling.LANCZOS)
        composite.paste(resized_panel.convert("RGB"), (x, y + header_h))

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        composite.save(output_path, "PNG")

    return composite
