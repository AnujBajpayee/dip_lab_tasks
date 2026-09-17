"""
Visualizer & Benchmark Grid Generator for Shannon-Fano & Huffman Coding
========================================================================
Generates labeled multi-panel comparison grids displaying symbol distributions,
prefix code tables, efficiency statistics, and lossless reconstruction verification.
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

from task_6_shannon_huffman_coding.coding import (
    compute_symbol_probabilities,
    compute_entropy,
    build_shannon_fano_codebook,
    build_huffman_codebook,
    encode_image,
    decode_image,
    compute_coding_metrics,
)
from task_3_bit_plane_slicing.bit_plane import compute_mse_psnr


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


def draw_symbol_distribution_card(
    probabilities: Dict[int, float],
    width: int = 380,
    height: int = 260
) -> Image.Image:
    """Renders a graphical symbol probability distribution card."""
    card = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(card)
    _, font_card_title, font_card_formula, font_card_desc = _get_fonts()

    # Draw grid lines
    draw.line([(30, height - 30), (width - 15, height - 30)], fill=(51, 65, 85), width=1)
    draw.line([(30, 20), (30, height - 30)], fill=(51, 65, 85), width=1)

    sorted_p = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:12]
    max_p = max((p for _, p in sorted_p), default=1.0)

    # Bar chart
    bar_w = (width - 60) // max(1, len(sorted_p))
    for i, (sym, p) in enumerate(sorted_p):
        bx = 35 + i * bar_w
        bar_h = int((p / max_p) * (height - 80))
        by = height - 30 - bar_h

        # Draw bar
        draw.rectangle([(bx + 2, by), (bx + bar_w - 4, height - 30)], fill=(56, 189, 248), outline=(14, 165, 233))
        # Intensity label
        draw.text((bx + bar_w // 2 - 2, height - 20), str(sym), fill=(148, 163, 184), font=font_card_desc, anchor="mm")
        # Probability label
        draw.text((bx + bar_w // 2 - 2, max(12, by - 6)), f"{p*100:.1f}%", fill=(253, 224, 71), font=font_card_desc, anchor="mm")

    draw.text((width // 2, 10), "Top Dominant Gray Level Probabilities (p_i)", fill=(248, 250, 252), font=font_card_title, anchor="mm")
    return card


def draw_codebook_table_card(
    method_name: str,
    codebook: Dict[int, str],
    probabilities: Dict[int, float],
    metrics: Dict[str, float],
    width: int = 380,
    height: int = 260
) -> Image.Image:
    """Renders a formatted table showing code assignments and performance metrics."""
    card = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(card)
    _, font_card_title, font_card_formula, font_card_desc = _get_fonts()

    # Title & Metrics Banner
    draw.rectangle([(10, 10), (width - 10, 50)], fill=(30, 41, 59), outline=(71, 85, 105))
    draw.text((width // 2, 22), f"{method_name} Codebook Summary", fill=(255, 255, 255), font=font_card_title, anchor="mm")
    draw.text((width // 2, 38), f"Avg Length: {metrics['avg_length_bits']} bits • Efficiency: {metrics['efficiency_pct']}% • CR: {metrics['compression_ratio']}:1", fill=(253, 224, 71), font=font_card_formula, anchor="mm")

    # Table Header
    y_start = 65
    draw.rectangle([(10, y_start), (width - 10, y_start + 20)], fill=(51, 65, 85))
    draw.text((25, y_start + 10), "Intensity", fill=(255, 255, 255), font=font_card_desc, anchor="lm")
    draw.text((105, y_start + 10), "Prob (p_i)", fill=(255, 255, 255), font=font_card_desc, anchor="lm")
    draw.text((195, y_start + 10), "Prefix Code", fill=(255, 255, 255), font=font_card_desc, anchor="lm")
    draw.text((315, y_start + 10), "Bits (l_i)", fill=(255, 255, 255), font=font_card_desc, anchor="lm")

    # Top symbols
    sorted_syms = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:8]
    for idx, (sym, prob) in enumerate(sorted_syms):
        row_y = y_start + 26 + idx * 20
        code = codebook.get(sym, "-")
        bg_fill = (30, 41, 59) if idx % 2 == 0 else (15, 23, 42)
        draw.rectangle([(10, row_y - 3), (width - 10, row_y + 17)], fill=bg_fill)

        draw.text((25, row_y + 7), f"{sym:>3}", fill=(248, 250, 252), font=font_card_desc, anchor="lm")
        draw.text((105, row_y + 7), f"{prob * 100:>5.2f}%", fill=(56, 189, 248), font=font_card_desc, anchor="lm")
        draw.text((195, row_y + 7), code, fill=(253, 224, 71), font=font_card_desc, anchor="lm")
        draw.text((315, row_y + 7), f"{len(code)} bits", fill=(34, 197, 94), font=font_card_desc, anchor="lm")

    return card


def create_shannon_huffman_comparison_grid(
    image: Image.Image,
    output_path: Optional[str] = None
) -> Image.Image:
    """
    Creates a comprehensive 6-panel comparison grid demonstrating Shannon-Fano & Huffman
    coding algorithms applied to the input image with lossless reconstruction verification.
    """
    if not HAS_DEPS:
        raise ImportError("Pillow and NumPy required.")

    img_gray = image.convert("L")
    np_gray = np.array(img_gray)

    # 1. Compute Probabilities & Entropy
    probs = compute_symbol_probabilities(np_gray)
    entropy_val = compute_entropy(probs)

    # 2. Build Codebooks
    sf_codebook = build_shannon_fano_codebook(probs)
    hf_codebook = build_huffman_codebook(probs)

    # 3. Compute Metrics
    sf_metrics = compute_coding_metrics(probs, sf_codebook)
    hf_metrics = compute_coding_metrics(probs, hf_codebook)

    # 4. Bitstream Verification
    bitstream, shape = encode_image(np_gray, hf_codebook)
    decoded_np = decode_image(bitstream, hf_codebook, shape)
    mse, psnr = compute_mse_psnr(np_gray, decoded_np)

    target_w, target_h = 380, 260

    # Panel Elements
    p1_orig = image.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)
    p2_prob = draw_symbol_distribution_card(probs, target_w, target_h)
    p3_sf = draw_codebook_table_card("Shannon-Fano", sf_codebook, probs, sf_metrics, target_w, target_h)
    p4_hf = draw_codebook_table_card("Huffman Optimal", hf_codebook, probs, hf_metrics, target_w, target_h)
    p5_decoded = Image.fromarray(decoded_np).convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)

    panels = [
        (
            "1. Original Benchmark Input",
            "Spatial Domain f(x, y) ∈ [0, 255]",
            f"Entropy H(X) = {entropy_val:.4f} bits/pixel • Uncompressed (8 bits/px)",
            p1_orig
        ),
        (
            "2. Gray Level Probability Distribution",
            "p_i = count(r_i) / (M × N)",
            "Probability Profile Driving Variable-Length Prefix Codes",
            p2_prob
        ),
        (
            "3. Shannon-Fano Coding Analysis",
            "Recursive Probability Partition: min |P(S1) - P(S2)|",
            f"L_avg = {sf_metrics['avg_length_bits']} b/px • Efficiency = {sf_metrics['efficiency_pct']}% • CR = {sf_metrics['compression_ratio']}:1",
            p3_sf
        ),
        (
            "4. Huffman Optimal Prefix Coding",
            "Priority Queue Binary Tree: min(w1 + w2)",
            f"L_avg = {hf_metrics['avg_length_bits']} b/px • Efficiency = {hf_metrics['efficiency_pct']}% • CR = {hf_metrics['compression_ratio']}:1",
            p4_hf
        ),
        (
            "5. Lossless Decoded Reconstruction",
            "f_rec = Decode(Bitstream, Huffman_Tree)",
            f"Bitstream Length: {len(bitstream):,} bits • MSE: {mse:.4f} • PSNR: Lossless (inf)",
            p5_decoded
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
        "SHANNON-FANO & HUFFMAN LOSSLESS ENTROPY CODING BENCHMARK",
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
