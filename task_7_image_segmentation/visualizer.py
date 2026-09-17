"""
Visualizer & Segmentation Comparison Grid Generator
===================================================
Generates labeled multi-panel benchmark grids displaying segmentation results across
Otsu's global binarization, adaptive windowing, K-Means color clustering, region growing,
and spatial gradient edge boundaries.
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

from task_7_image_segmentation.segmentation import (
    otsu_thresholding,
    adaptive_local_thresholding,
    kmeans_segmentation,
    region_growing_segmentation,
    edge_based_segmentation,
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


def create_segmentation_comparison_grid(
    image: Image.Image,
    output_path: Optional[str] = None
) -> Image.Image:
    """
    Creates a 6-panel composite comparison grid showing the original image and 5
    distinct image segmentation techniques with explicit mathematical formulas.
    """
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    np_rgb = np.array(image.convert("RGB"))
    np_gray = np.array(image.convert("L"))

    # 1. Otsu's Global Thresholding
    otsu_mask, otsu_t, otsu_var = otsu_thresholding(np_gray)

    # 2. Adaptive Local Window Thresholding
    adapt_mask = adaptive_local_thresholding(np_gray, block_size=21, c=8.0)

    # 3. K-Means Color Clustering (K=4)
    kmeans_img, _ = kmeans_segmentation(np_rgb, k=4, max_iters=25)

    # 4. Region Growing Segmentation (Seed at Logo Arrow and Tower)
    h, w = np_gray.shape
    seeds = [(int(h * 0.45), int(w * 0.5)), (int(h * 0.5), int(w * 0.28))]
    region_mask = region_growing_segmentation(np_gray, seed_points=seeds, tolerance=35.0)

    # 5. Sobel Edge-Boundary Extraction
    grad_norm, edge_binary = edge_based_segmentation(np_gray, threshold=40.0)

    target_w, target_h = 380, 260

    # Resize panels
    p1 = image.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p2 = Image.fromarray(otsu_mask).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p3 = Image.fromarray(adapt_mask).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p4 = Image.fromarray(kmeans_img).resize((target_w, target_h), Image.Resampling.LANCZOS)
    p5 = Image.fromarray(region_mask).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p6 = Image.fromarray(edge_binary).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)

    panels = [
        (
            "1. Original Benchmark Input",
            "Spatial Domain: f(x, y) ∈ RGB / Monochromatic",
            "Reference Target (IIIT Nagpur Official Emblem)",
            p1
        ),
        (
            "2. Otsu's Global Optimum Thresholding",
            f"max σ_B^2(t) = ω_0·ω_1·(μ_0 - μ_1)^2 → t* = {otsu_t}",
            "Inter-Class Variance Maximization Binarization",
            p2
        ),
        (
            "3. Adaptive Local Window Thresholding",
            "T(x, y) = μ_local(x, y) - C (Block = 21×21, C = 8)",
            "Robust Under Non-Uniform Illumination Gradients",
            p3
        ),
        (
            "4. K-Means Feature-Space Clustering (K = 4)",
            "min Σ || x_i - μ_k ||^2 (Color Centroid Quantization)",
            "Unsupervised Segmentation into 4 Discrete Color Classes",
            p4
        ),
        (
            "5. Seeded Region Growing Segmentation",
            "Predicate: | f(x, y) - μ_region | ≤ 35.0",
            "Spatially Connected Homogeneous Pixel Cluster",
            p5
        ),
        (
            "6. Sobel Spatial Gradient Edge Extraction",
            "M(x, y) = sqrt( G_x^2 + G_y^2 ) ≥ T_edge",
            "First-Order Spatial Derivative Structural Contours",
            p6
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
        "DIGITAL IMAGE SEGMENTATION ALGORITHMIC BENCHMARK",
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

        composite.paste(img_panel, (x, y + header_h))

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        composite.save(output_path, "PNG")

    return composite
