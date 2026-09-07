"""
Task 5: 2D Discrete Wavelet Transform CLI Runner & Profiler
===========================================================
"""

from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

# Configure UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image
import numpy as np

from task_5_wavelet_transform.wavelet import (
    dwt2,
    idwt2,
    wavedec2,
    waverec2,
    compute_wavelet_energy,
    threshold_wavelet_coefficients,
)
from task_5_wavelet_transform.visualizer import (
    create_subband_decomposition_grid,
    create_multilevel_quadtree_image,
    create_wavelet_compression_grid,
    normalize_subband_for_display,
)
from task_3_bit_plane_slicing.visualizer import create_rich_test_pattern
from task_2_rgb_to_greyscale_conversion.visualizer import create_scenery_test_image


def process_image_wavelet(
    input_img: Image.Image,
    output_dir: str,
    prefix: str = "img",
    wavelet: str = "haar",
    level: int = 2
) -> None:
    """Executes 2D DWT, IDWT, energy calculation, quadtree mosaic, and compression benchmarking."""
    os.makedirs(output_dir, exist_ok=True)
    img_gray = input_img.convert("L")
    np_gray = np.array(img_gray)

    # 1. Save original
    orig_path = os.path.join(output_dir, f"{prefix}_original.png")
    img_gray.save(orig_path)
    print(f"  • Saved Original Input Image: {orig_path}")

    # 2. 2D Single-Level DWT
    coeffs = dwt2(np_gray, wavelet=wavelet)
    ll, (lh, hl, hh) = coeffs

    # Save individual subbands
    Image.fromarray(normalize_subband_for_display(ll, is_ll=True)).save(os.path.join(output_dir, f"{prefix}_subband_ll.png"))
    Image.fromarray(normalize_subband_for_display(lh, is_ll=False)).save(os.path.join(output_dir, f"{prefix}_subband_lh.png"))
    Image.fromarray(normalize_subband_for_display(hl, is_ll=False)).save(os.path.join(output_dir, f"{prefix}_subband_hl.png"))
    Image.fromarray(normalize_subband_for_display(hh, is_ll=False)).save(os.path.join(output_dir, f"{prefix}_subband_hh.png"))

    # 3. Subband Decomposition Grid
    grid_path = os.path.join(output_dir, f"{prefix}_subband_grid.png")
    create_subband_decomposition_grid(img_gray, coeffs, wavelet=wavelet, output_path=grid_path)
    print(f"  • Saved 4-Subband Decomposition Grid: {grid_path}")

    # 4. Multi-Level Quadtree Mosaic
    m_coeffs = wavedec2(np_gray, wavelet=wavelet, level=level)
    mosaic_path = os.path.join(output_dir, f"{prefix}_multilevel_quadtree_level{level}.png")
    create_multilevel_quadtree_image(m_coeffs, output_path=mosaic_path)
    print(f"  • Saved Level-{level} Wavelet Quadtree Mosaic: {mosaic_path}")

    # 5. Wavelet Compression Benchmark Grid
    comp_grid_path = os.path.join(output_dir, f"{prefix}_compression_grid.png")
    create_wavelet_compression_grid(img_gray, wavelet=wavelet, output_path=comp_grid_path)
    print(f"  • Saved Wavelet Compression Benchmark Grid: {comp_grid_path}")

    # 6. Print Subband Energy Distribution Table
    energy_stats = compute_wavelet_energy(coeffs)
    print(f"\n{'Subband':<26} | {'Energy %':>9} | {'Mean':>7} | {'StdDev':>7} | {'Perceptual Content Role'}")
    print("-" * 95)
    for band_key, stat in energy_stats.items():
        print(f"{stat['name']:<26} | {stat['energy_pct']:>8.2f}% | {stat['mean']:>7.2f} | {stat['std']:>7.2f} | {stat['role']}")


def main():
    parser = argparse.ArgumentParser(description="Task 5: 2D Discrete Wavelet Transform CLI Runner")
    parser.add_argument("--input", type=str, help="Path to input image")
    parser.add_argument("--generate-test-patterns", action="store_true", help="Synthesize test patterns, IIITN logo, and scenery scenes")
    parser.add_argument("--wavelet", type=str, default="haar", choices=["haar", "db1", "db2"], help="Wavelet filter family")
    parser.add_argument("--level", type=int, default=2, help="Multi-level decomposition depth")
    parser.add_argument("--output-dir", type=str, default="task_5_wavelet_transform/outputs", help="Output directory")
    parser.add_argument("--prefix", type=str, default="output", help="Output prefix")

    args = parser.parse_args()

    if args.generate_test_patterns or not args.input:
        print("\n" + "=" * 70)
        print("🖼️ SYNTHESIZING 2D WAVELET TRANSFORM BENCHMARKS & SUBBANDS")
        print("=" * 70)

        # 1. IIIT Nagpur Logo
        iiitn_path = "assets/iiitn_logo.png"
        if os.path.exists(iiitn_path):
            iiitn_img = Image.open(iiitn_path)
            print("\n--- Processing IIIT Nagpur Official Logo ---")
            process_image_wavelet(iiitn_img, args.output_dir, prefix="iiitn_logo", wavelet=args.wavelet, level=args.level)

        # 2. Calibrated Complex Test Target
        test_pattern = create_rich_test_pattern(640, 480)
        print("\n--- Processing Calibrated Test Target ---")
        process_image_wavelet(test_pattern, args.output_dir, prefix="test_pattern", wavelet=args.wavelet, level=args.level)

        # 3. Natural Photographic Scenery
        scenery = create_scenery_test_image(640, 480).convert("L")
        print("\n--- Processing Photographic Scenery Scene ---")
        process_image_wavelet(scenery, args.output_dir, prefix="scenery", wavelet=args.wavelet, level=args.level)

    elif args.input:
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}")
            sys.exit(1)
        img = Image.open(args.input)
        print(f"\n--- Processing User Image: {args.input} ---")
        process_image_wavelet(img, args.output_dir, prefix=args.prefix, wavelet=args.wavelet, level=args.level)


if __name__ == "__main__":
    main()
