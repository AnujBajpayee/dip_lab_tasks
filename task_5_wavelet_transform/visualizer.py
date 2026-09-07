"""
Visualizer, Subband Mosaic & Compression Grid Generator for 2D Wavelet Transforms
==================================================================================
Generates labeled multi-panel subband grids (LL, LH, HL, HH), multi-level quad-tree
mosaics, and wavelet coefficient thresholding / compression benchmark grids.
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

from task_3_bit_plane_slicing.bit_plane import compute_mse_psnr
from task_5_wavelet_transform.wavelet import (
    dwt2,
    idwt2,
    wavedec2,
    compute_wavelet_energy,
    threshold_wavelet_coefficients,
)


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


def normalize_subband_for_display(
    subband: np.ndarray,
    is_ll: bool = False
) -> np.ndarray:
    """Normalizes subband coefficients into uint8 [0, 255] for visual clarity."""
    arr = subband.astype(np.float64)
    if is_ll:
        min_v = np.min(arr)
        max_v = np.max(arr)
        if max_v > min_v:
            norm = (arr - min_v) / (max_v - min_v) * 255.0
        else:
            norm = arr
        return np.clip(np.round(norm), 0, 255).astype(np.uint8)
    else:
        # For high-pass detail coefficients (LH, HL, HH): amplify absolute amplitude or center around 128
        abs_arr = np.abs(arr)
        max_v = np.percentile(abs_arr, 99.5) if abs_arr.size > 0 else 1.0
        max_v = max(1e-5, max_v)
        norm = np.clip((abs_arr / max_v) * 255.0, 0, 255)
        return np.round(norm).astype(np.uint8)


# =============================================================================
# 1. Subband Decomposition Grid (5 Panels)
# =============================================================================

def create_subband_decomposition_grid(
    original_image: Image.Image,
    coeffs: Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]],
    wavelet: str = "haar",
    output_path: Optional[str] = None
) -> Image.Image:
    """
    Creates a labeled composite grid showing the Original image and the 4 DWT subbands:
    - LL1: Low-Low Approximation
    - LH1: Low-High Horizontal Details
    - HL1: High-Low Vertical Details
    - HH1: High-High Diagonal Details
    """
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    ll, (lh, hl, hh) = coeffs
    energy_stats = compute_wavelet_energy(coeffs)

    target_w, target_h = 360, 260
    orig_gray = original_image.convert("L").resize((target_w, target_h), Image.Resampling.LANCZOS)

    ll_disp = Image.fromarray(normalize_subband_for_display(ll, is_ll=True)).resize((target_w, target_h), Image.Resampling.LANCZOS)
    lh_disp = Image.fromarray(normalize_subband_for_display(lh, is_ll=False)).resize((target_w, target_h), Image.Resampling.LANCZOS)
    hl_disp = Image.fromarray(normalize_subband_for_display(hl, is_ll=False)).resize((target_w, target_h), Image.Resampling.LANCZOS)
    hh_disp = Image.fromarray(normalize_subband_for_display(hh, is_ll=False)).resize((target_w, target_h), Image.Resampling.LANCZOS)

    panels = [
        (
            "Original Reference Image",
            "Spatial Domain: f(x, y) ∈ [0, 255]",
            "Full Resolution Monochromatic Input (100% Total Signal)",
            orig_gray
        ),
        (
            f"LL Subband (Approximation, {wavelet.upper()})",
            "Formula: LL = (f * h0 · h0^T) ↓2",
            f"Energy: {energy_stats['LL']['energy_pct']:.2f}% • Coarse Geometry & Low Frequencies",
            ll_disp
        ),
        (
            f"LH Subband (Horizontal Details, {wavelet.upper()})",
            "Formula: LH = (f * h0 · h1^T) ↓2",
            f"Energy: {energy_stats['LH']['energy_pct']:.2f}% • Horizontal Edges & Contours",
            lh_disp
        ),
        (
            f"HL Subband (Vertical Details, {wavelet.upper()})",
            "Formula: HL = (f * h1 · h0^T) ↓2",
            f"Energy: {energy_stats['HL']['energy_pct']:.2f}% • Vertical Edges & Boundaries",
            hl_disp
        ),
        (
            f"HH Subband (Diagonal Details, {wavelet.upper()})",
            "Formula: HH = (f * h1 · h1^T) ↓2",
            f"Energy: {energy_stats['HH']['energy_pct']:.2f}% • Diagonal Textures & High-Frequency Noise",
            hh_disp
        ),
    ]

    cols = 3
    rows = 2
    margin = 16
    header_h = 52
    total_w = cols * target_w + (cols + 1) * margin
    total_h = rows * (target_h + header_h) + (rows + 1) * margin + 60

    composite = Image.new("RGB", (total_w, total_h), color=(15, 23, 42))
    draw = ImageDraw.Draw(composite)

    font_title, font_card_title, font_card_formula, font_card_desc = _get_fonts()

    draw.text(
        (total_w // 2, 30),
        f"2D DISCRETE WAVELET TRANSFORM (DWT-2D) SUBBAND DECOMPOSITION [{wavelet.upper()}]",
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
# 2. Multi-Level Quadtree Mosaic Visualizer
# =============================================================================

def create_multilevel_quadtree_image(
    coeffs_multilevel: List[Any],
    output_path: Optional[str] = None
) -> Image.Image:
    """
    Constructs the standard recursive 2D Wavelet Quadtree mosaic layout.
    """
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    # Top-level approximation
    ll_top = coeffs_multilevel[0]
    mosaic = normalize_subband_for_display(ll_top, is_ll=True)

    for details in coeffs_multilevel[1:]:
        lh, hl, hh = details
        lh_d = normalize_subband_for_display(lh, is_ll=False)
        hl_d = normalize_subband_for_display(hl, is_ll=False)
        hh_d = normalize_subband_for_display(hh, is_ll=False)

        top_row = np.hstack([mosaic, lh_d])
        bot_row = np.hstack([hl_d, hh_d])
        mosaic = np.vstack([top_row, bot_row])

    img = Image.fromarray(mosaic)
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        img.save(output_path, "PNG")

    return img


# =============================================================================
# 3. Wavelet Compression / Thresholding Grid
# =============================================================================

def create_wavelet_compression_grid(
    original_image: Image.Image,
    wavelet: str = "haar",
    output_path: Optional[str] = None
) -> Image.Image:
    """
    Demonstrates wavelet-based image compression by thresholding detail coefficients.
    Compares 100% coefficients, 20% retained (80% zeroed), 5% retained (95% zeroed), 1% retained (99% zeroed).
    """
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    orig_np = np.array(original_image.convert("L"))
    coeffs = dwt2(orig_np, wavelet=wavelet)

    # 1. Full Lossless IDWT
    recon_full = np.clip(np.round(idwt2(coeffs, wavelet=wavelet, target_shape=orig_np.shape)), 0, 255).astype(np.uint8)
    mse_full, psnr_full = compute_mse_psnr(orig_np, recon_full)

    # 2. Retain 20% (80% zeroed)
    coeffs_20, th20 = threshold_wavelet_coefficients(coeffs, keep_fraction=0.20, mode="hard")
    recon_20 = np.clip(np.round(idwt2(coeffs_20, wavelet=wavelet, target_shape=orig_np.shape)), 0, 255).astype(np.uint8)
    mse_20, psnr_20 = compute_mse_psnr(orig_np, recon_20)

    # 3. Retain 5% (95% zeroed, 20:1 compression)
    coeffs_05, th05 = threshold_wavelet_coefficients(coeffs, keep_fraction=0.05, mode="hard")
    recon_05 = np.clip(np.round(idwt2(coeffs_05, wavelet=wavelet, target_shape=orig_np.shape)), 0, 255).astype(np.uint8)
    mse_05, psnr_05 = compute_mse_psnr(orig_np, recon_05)

    # 4. Retain 1% (99% zeroed, 100:1 compression)
    coeffs_01, th01 = threshold_wavelet_coefficients(coeffs, keep_fraction=0.01, mode="hard")
    recon_01 = np.clip(np.round(idwt2(coeffs_01, wavelet=wavelet, target_shape=orig_np.shape)), 0, 255).astype(np.uint8)
    mse_01, psnr_01 = compute_mse_psnr(orig_np, recon_01)

    target_w, target_h = 380, 260
    panels = [
        (
            "1. Reference Ground Truth",
            "Spatial Domain f(x, y)",
            "Original Uncompressed 8-Bit Image",
            original_image.convert("L").resize((target_w, target_h), Image.Resampling.LANCZOS)
        ),
        (
            "2. Full 2D IDWT Reconstruction",
            f"Formula: f = IDWT(LL, LH, HL, HH) [{wavelet.upper()}]",
            f"100% Coefficients Retained • MSE: {mse_full:.2f} • PSNR: Lossless (inf)",
            Image.fromarray(recon_full).resize((target_w, target_h), Image.Resampling.LANCZOS)
        ),
        (
            "3. Wavelet Compression (80% Zeroed)",
            f"Retained: Top 20% Coefficients (Threshold = {th20:.1f})",
            f"MSE: {mse_20:.2f} • PSNR: {psnr_20:.2f} dB (High Quality)",
            Image.fromarray(recon_20).resize((target_w, target_h), Image.Resampling.LANCZOS)
        ),
        (
            "4. Wavelet Compression (95% Zeroed)",
            f"Retained: Top 5% Coefficients (Threshold = {th05:.1f})",
            f"MSE: {mse_05:.2f} • PSNR: {psnr_05:.2f} dB (20:1 Data Reduction)",
            Image.fromarray(recon_05).resize((target_w, target_h), Image.Resampling.LANCZOS)
        ),
        (
            "5. Wavelet Compression (99% Zeroed)",
            f"Retained: Top 1% Coefficients (Threshold = {th01:.1f})",
            f"MSE: {mse_01:.2f} • PSNR: {psnr_01:.2f} dB (100:1 Data Reduction)",
            Image.fromarray(recon_01).resize((target_w, target_h), Image.Resampling.LANCZOS)
        ),
    ]

    cols = 3
    rows = 2
    margin = 16
    header_h = 52
    total_w = cols * target_w + (cols + 1) * margin
    total_h = rows * (target_h + header_h) + (rows + 1) * margin + 60

    composite = Image.new("RGB", (total_w, total_h), color=(15, 23, 42))
    draw = ImageDraw.Draw(composite)

    font_title, font_card_title, font_card_formula, font_card_desc = _get_fonts()

    draw.text(
        (total_w // 2, 30),
        f"WAVELET COEFFICIENT THRESHOLDING & COMPRESSION BENCHMARK [{wavelet.upper()}]",
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
