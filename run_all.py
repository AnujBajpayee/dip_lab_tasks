"""
DIP Lab Tasks: Master Runner
============================
Executes all 7 Digital Image Processing & Computational Algorithm tasks:
- Task 1: Tambola Ticket Generator & CSP Engine
- Task 2: Standard RGB to Greyscale Conversion (Rec.601, Rec.709, Gamma, Channels)
- Task 3: 8-Bit Plane Slicing & Digital Steganography
- Task 4: Histogram Equalization Types & Execution (GHE, BBHE, CLAHE, Color HSV)
- Task 5: 2D Discrete Wavelet Transform (DWT & IDWT)
- Task 6: Shannon-Fano & Huffman Image Entropy Coding
- Task 7: Digital Image Segmentation (Otsu, Adaptive, K-Means, Region Growing, Sobel)

All image-processing tasks exclusively process and output benchmarks using the
official IIIT Nagpur Logo.
"""

from __future__ import annotations
import os
import sys
import json
import time
from pathlib import Path

# Configure UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))

# Task 1 Imports
from task_1_tambola_ticket_generator.generator import generate_ticket, generate_strip, validate_ticket, validate_strip
from task_1_tambola_ticket_generator.naive_generator import simulate_naive_generation
from task_1_tambola_ticket_generator.visualizer import ticket_to_ascii, ticket_to_svg, ticket_to_png, strip_to_ascii

# Task 2 Imports
from task_2_rgb_to_greyscale_conversion.grayscale import (
    to_rec601_luminance,
    to_rec709_luminance,
    to_average_grayscale,
    to_lightness_grayscale,
    to_gamma_corrected_grayscale,
    extract_channel,
)
from task_2_rgb_to_greyscale_conversion.visualizer import create_comparison_grid

# Task 3 Imports
from task_3_bit_plane_slicing.bit_plane import (
    extract_all_bit_planes,
    reconstruct_cumulative_msb,
    embed_watermark_lsb,
    extract_watermark_lsb,
)
from task_3_bit_plane_slicing.visualizer import (
    create_bit_plane_grid,
    create_cumulative_reconstruction_grid,
    create_steganography_grid,
    create_watermark_pattern,
)

# Task 4 Imports
from task_4_histogram_equalization.histogram import (
    global_histogram_equalization,
    bi_histogram_equalization,
    clahe,
    histogram_matching,
)
from task_4_histogram_equalization.visualizer import create_histogram_comparison_grid

# Task 5 Imports
from task_5_wavelet_transform.wavelet import (
    dwt2,
    idwt2,
    wavedec2,
)
from task_5_wavelet_transform.visualizer import (
    create_subband_decomposition_grid,
    create_multilevel_quadtree_image,
    create_wavelet_compression_grid,
    normalize_subband_for_display,
)

# Task 6 Imports
from task_6_shannon_huffman_coding.coding import (
    compute_symbol_probabilities,
    compute_entropy,
    build_shannon_fano_codebook,
    build_huffman_codebook,
    compute_coding_metrics,
)
from task_6_shannon_huffman_coding.visualizer import create_shannon_huffman_comparison_grid

# Task 7 Imports
from task_7_image_segmentation.visualizer import create_segmentation_comparison_grid

import numpy as np
from PIL import Image


def get_iiitn_logo() -> Image.Image:
    """Loads the IIIT Nagpur logo asset."""
    logo_path = os.path.join(base_dir, "assets", "iiitn_logo.png")
    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"IIITN Logo asset not found at {logo_path}")
    return Image.open(logo_path)


def run_task_1(output_dir: str = "task_1_tambola_ticket_generator/outputs") -> None:
    print("\n" + "=" * 70)
    print("🎲 RUNNING TASK 1: TAMBOLA TICKET GENERATOR & BENCHMARK")
    print("=" * 70)
    os.makedirs(output_dir, exist_ok=True)

    # 1. Single Ticket
    ticket = generate_ticket(seed=2026, ticket_id="TKT-2026-IIITN")
    print(f"\n• Generated Valid Single Tambola Ticket:")
    print(ticket_to_ascii(ticket))

    with open(os.path.join(output_dir, "sample_ticket_1.txt"), "w", encoding="utf-8") as f:
        f.write(ticket_to_ascii(ticket))
    with open(os.path.join(output_dir, "sample_ticket_1.json"), "w", encoding="utf-8") as f:
        json.dump(ticket.to_dict(), f, indent=2)
    ticket_to_svg(ticket, output_path=os.path.join(output_dir, "sample_ticket_1.svg"))
    ticket_to_png(ticket, output_path=os.path.join(output_dir, "sample_ticket_1.png"))
    print("  -> Saved TXT, JSON, SVG, PNG sample tickets in task 1 outputs.")

    # 2. Strip of 6 Tickets (Numbers 1-90)
    strip = generate_strip(seed=9999, strip_id="STRIP-MASTER-01")
    with open(os.path.join(output_dir, "sample_strip_of_6.txt"), "w", encoding="utf-8") as f:
        f.write(strip_to_ascii(strip))
    with open(os.path.join(output_dir, "sample_strip_of_6.json"), "w", encoding="utf-8") as f:
        json.dump(strip.to_dict(), f, indent=2)
    print("  -> Saved Full 6-Ticket Strip (all 90 numbers) in task 1 outputs.")

    # 3. Naive 0/1 Simulation Benchmark
    stats = simulate_naive_generation(num_trials=10000, seed=42)
    bench_report = [
        "=" * 60,
        "TAMBOLA ALGORITHM COMPARISON & REJECTION RATE BENCHMARK",
        "=" * 60,
        f"Total Monte-Carlo Trials:        {stats.total_trials:,}",
        f"Valid Binary Masks (Successes):  {stats.successful_trials:,} ({stats.success_rate_percent}%)",
        f"Empty Column Failures (Rejected): {stats.failed_empty_column:,} ({stats.rejection_rate_percent}%)",
        f"Avg Attempts per Valid Mask:     {stats.average_attempts_until_success:.2f} iterations",
        f"Benchmark Execution Time:        {stats.elapsed_seconds:.4f}s",
        "-" * 60,
        "Conclusion: Naive 0/1 random selection fails ~28.5%-62.4% due to column",
        "starvation. The CSP engine deterministically solves all constraints in O(1) time.",
        "=" * 60,
    ]
    with open(os.path.join(output_dir, "algorithm_benchmark.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(bench_report))
    print("  -> Saved Naive vs CSP Benchmark report in task 1 outputs.")


def run_task_2(output_dir: str = "task_2_rgb_to_greyscale_conversion/outputs") -> None:
    print("\n" + "=" * 70)
    print("🎨 RUNNING TASK 2: RGB TO GREYSCALE CONVERSION (IIITN LOGO)")
    print("=" * 70)
    os.makedirs(output_dir, exist_ok=True)

    img_pil = get_iiitn_logo()
    np_rgb = np.array(img_pil.convert("RGB"))

    orig_file = "iiitn_logo_original_rgb.png"
    img_pil.save(os.path.join(output_dir, orig_file))

    conversions = {
        "Rec.601 Luminosity": (to_rec601_luminance(np_rgb), "iiitn_logo_rec601.png"),
        "Rec.709 Luminosity": (to_rec709_luminance(np_rgb), "iiitn_logo_rec709.png"),
        "Simple Average": (to_average_grayscale(np_rgb), "iiitn_logo_average.png"),
        "HSL Lightness": (to_lightness_grayscale(np_rgb), "iiitn_logo_lightness.png"),
        "Gamma-Corrected": (to_gamma_corrected_grayscale(np_rgb), "iiitn_logo_gamma.png"),
        "Red Channel": (extract_channel(np_rgb, "red"), "iiitn_logo_channel_red.png"),
        "Green Channel": (extract_channel(np_rgb, "green"), "iiitn_logo_channel_green.png"),
        "Blue Channel": (extract_channel(np_rgb, "blue"), "iiitn_logo_channel_blue.png"),
    }

    conversions_for_grid = {}
    for name, (gray_arr, filename) in conversions.items():
        out_path = os.path.join(output_dir, filename)
        Image.fromarray(gray_arr).save(out_path)
        conversions_for_grid[name] = gray_arr

    grid_file = "iiitn_logo_comparison_grid.png"
    create_comparison_grid(img_pil, conversions_for_grid, output_path=os.path.join(output_dir, grid_file))
    print(f"  -> Saved all greyscale variants and comparison grid: {grid_file}")


def run_task_3(output_dir: str = "task_3_bit_plane_slicing/outputs") -> None:
    print("\n" + "=" * 70)
    print("🔬 RUNNING TASK 3: 8-BIT PLANE SLICING & STEGANOGRAPHY (IIITN LOGO)")
    print("=" * 70)
    os.makedirs(output_dir, exist_ok=True)

    img_pil = get_iiitn_logo().convert("L")
    np_gray = np.array(img_pil)
    width, height = img_pil.size

    orig_file = "iiitn_logo_original.png"
    img_pil.save(os.path.join(output_dir, orig_file))

    # Bit Planes 0 to 7
    planes_scaled = extract_all_bit_planes(np_gray, scale_to_255=True)
    for k in range(8):
        plane_file = f"iiitn_logo_plane_{k}.png"
        Image.fromarray(planes_scaled[k]).save(os.path.join(output_dir, plane_file))

    # Composite Bit Planes Grid
    grid_file = "iiitn_logo_bit_planes_grid.png"
    create_bit_plane_grid(img_pil, planes_scaled, output_path=os.path.join(output_dir, grid_file))

    # Cumulative Multi-Bit Reconstruction Grid
    cumul_results = reconstruct_cumulative_msb(np_gray)
    recon_grid_file = "iiitn_logo_cumulative_reconstruction_grid.png"
    create_cumulative_reconstruction_grid(img_pil, cumul_results, output_path=os.path.join(output_dir, recon_grid_file))

    # Steganography Demo
    wm_pil = create_watermark_pattern(width, height, label="IIIT NAGPUR 2026")
    wm_np = np.array(wm_pil)
    wm_pil.save(os.path.join(output_dir, "iiitn_logo_watermark_original.png"))

    stego_np = embed_watermark_lsb(np_gray, wm_np, bit_plane=0)
    Image.fromarray(stego_np).save(os.path.join(output_dir, "iiitn_logo_stego_embedded.png"))

    extracted_np = extract_watermark_lsb(stego_np, bit_plane=0, scale_to_255=True)
    Image.fromarray(extracted_np).save(os.path.join(output_dir, "iiitn_logo_extracted_watermark.png"))

    stego_grid_file = "iiitn_logo_steganography_demo.png"
    create_steganography_grid(img_pil, wm_pil, stego_np, extracted_np, output_path=os.path.join(output_dir, stego_grid_file))
    print(f"  -> Saved Bit Planes, Progressive Reconstruction, and Steganography grids for IIITN Logo.")


def run_task_4(output_dir: str = "task_4_histogram_equalization/outputs") -> None:
    print("\n" + "=" * 70)
    print("📈 RUNNING TASK 4: HISTOGRAM EQUALIZATION (IIITN LOGO)")
    print("=" * 70)
    os.makedirs(output_dir, exist_ok=True)

    iiitn_img = get_iiitn_logo()
    np_iiitn_gray = np.array(iiitn_img.convert("L"))
    iiitn_img.save(os.path.join(output_dir, "iiitn_logo_original.png"))

    iiitn_eqs = {
        "Global HE (GHE)": global_histogram_equalization(np_iiitn_gray),
        "Bi-Histogram Equalization (BBHE)": bi_histogram_equalization(np_iiitn_gray),
        "CLAHE (Adaptive Local)": clahe(np_iiitn_gray, clip_limit=2.5, tile_grid_size=(8, 8)),
        "Histogram Matching": histogram_matching(np_iiitn_gray, np.linspace(0, 255, 256, dtype=np.uint8)),
    }
    create_histogram_comparison_grid(iiitn_img, iiitn_eqs, output_path=os.path.join(output_dir, "iiitn_logo_comparison_grid.png"))
    print("  -> Saved Histogram Equalization Comparison Grid for IIITN Logo.")


def run_task_5(output_dir: str = "task_5_wavelet_transform/outputs") -> None:
    print("\n" + "=" * 70)
    print("🌊 RUNNING TASK 5: 2D DISCRETE WAVELET TRANSFORM (IIITN LOGO)")
    print("=" * 70)
    os.makedirs(output_dir, exist_ok=True)

    img_pil = get_iiitn_logo().convert("L")
    np_gray = np.array(img_pil)

    img_pil.save(os.path.join(output_dir, "iiitn_logo_original.png"))

    coeffs = dwt2(np_gray, wavelet="haar")
    ll, (lh, hl, hh) = coeffs

    Image.fromarray(normalize_subband_for_display(ll, is_ll=True)).save(os.path.join(output_dir, "iiitn_logo_subband_ll.png"))
    Image.fromarray(normalize_subband_for_display(lh, is_ll=False)).save(os.path.join(output_dir, "iiitn_logo_subband_lh.png"))
    Image.fromarray(normalize_subband_for_display(hl, is_ll=False)).save(os.path.join(output_dir, "iiitn_logo_subband_hl.png"))
    Image.fromarray(normalize_subband_for_display(hh, is_ll=False)).save(os.path.join(output_dir, "iiitn_logo_subband_hh.png"))

    create_subband_decomposition_grid(img_pil, coeffs, wavelet="haar", output_path=os.path.join(output_dir, "iiitn_logo_subband_grid.png"))

    m_coeffs = wavedec2(np_gray, wavelet="haar", level=2)
    create_multilevel_quadtree_image(m_coeffs, output_path=os.path.join(output_dir, "iiitn_logo_multilevel_quadtree_level2.png"))

    create_wavelet_compression_grid(img_pil, wavelet="haar", output_path=os.path.join(output_dir, "iiitn_logo_compression_grid.png"))
    print("  -> Saved Subband Decomposition, Quadtree Mosaic, and Compression Grid for IIITN Logo.")


def run_task_6(output_dir: str = "task_6_shannon_huffman_coding/outputs") -> None:
    print("\n" + "=" * 70)
    print("📊 RUNNING TASK 6: SHANNON-FANO & HUFFMAN ENTROPY CODING (IIITN LOGO)")
    print("=" * 70)
    os.makedirs(output_dir, exist_ok=True)

    img_pil = get_iiitn_logo()
    create_shannon_huffman_comparison_grid(img_pil, output_path=os.path.join(output_dir, "iiitn_logo_comparison_grid.png"))
    print("  -> Saved Shannon-Fano & Huffman Lossless Coding Comparison Grid for IIITN Logo.")


def run_task_7(output_dir: str = "task_7_image_segmentation/outputs") -> None:
    print("\n" + "=" * 70)
    print("✂️ RUNNING TASK 7: DIGITAL IMAGE SEGMENTATION (IIITN LOGO)")
    print("=" * 70)
    os.makedirs(output_dir, exist_ok=True)

    img_pil = get_iiitn_logo()
    create_segmentation_comparison_grid(img_pil, output_path=os.path.join(output_dir, "iiitn_logo_comparison_grid.png"))
    print("  -> Saved Image Segmentation Comparison Grid for IIITN Logo.")


def main():
    start = time.perf_counter()
    print("=" * 70)
    print("🚀 DIP LAB TASKS: MASTER DEMONSTRATION RUNNER (TASKS 1 - 7)")
    print("=" * 70)
    run_task_1()
    run_task_2()
    run_task_3()
    run_task_4()
    run_task_5()
    run_task_6()
    run_task_7()
    print(f"\n✨ All 7 tasks executed successfully in {time.perf_counter() - start:.2f}s!\n")


if __name__ == "__main__":
    main()
