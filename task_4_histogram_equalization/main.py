"""
Task 4: Histogram Equalization Types & Execution CLI Runner
===========================================================
"""

from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

# Configure UTF-8 stdout for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image
import numpy as np

from task_4_histogram_equalization.histogram import (
    global_histogram_equalization,
    bi_histogram_equalization,
    clahe,
    histogram_matching,
    color_histogram_equalization,
)
from task_4_histogram_equalization.visualizer import (
    create_low_contrast_scene,
    create_uneven_illumination_scene,
    create_histogram_comparison_grid,
)
from task_2_rgb_to_greyscale_conversion.visualizer import (
    create_scenery_test_image,
    compute_image_statistics,
)


def process_image_equalizations(
    input_img: Image.Image,
    output_dir: str,
    prefix: str = "img"
) -> None:
    """Executes all Histogram Equalization algorithms and generates comparison grids."""
    os.makedirs(output_dir, exist_ok=True)
    is_color = input_img.mode in ("RGB", "RGBA")

    if is_color:
        img_rgb = input_img.convert("RGB")
        np_input = np.array(img_rgb)
        orig_path = os.path.join(output_dir, f"{prefix}_original_rgb.png")
        img_rgb.save(orig_path)
    else:
        img_gray = input_img.convert("L")
        np_input = np.array(img_gray)
        orig_path = os.path.join(output_dir, f"{prefix}_original.png")
        img_gray.save(orig_path)

    print(f"  • Saved Original Input Image: {orig_path}")

    # Compute Equalizations
    equalizations: Dict[str, np.ndarray] = {}

    if not is_color:
        ghe_out = global_histogram_equalization(np_input)
        bbhe_out = bi_histogram_equalization(np_input)
        clahe_out = clahe(np_input, clip_limit=2.5, tile_grid_size=(8, 8))

        # Histogram matching to a linear ramp target
        ramp_target = np.linspace(0, 255, 256, dtype=np.uint8)
        hm_out = histogram_matching(np_input, ramp_target)

        equalizations["Global HE (GHE)"] = ghe_out
        equalizations["Bi-Histogram Equalization (BBHE)"] = bbhe_out
        equalizations["CLAHE (Adaptive Local)"] = clahe_out
        equalizations["Histogram Matching"] = hm_out

        Image.fromarray(ghe_out).save(os.path.join(output_dir, f"{prefix}_ghe.png"))
        Image.fromarray(bbhe_out).save(os.path.join(output_dir, f"{prefix}_bbhe.png"))
        Image.fromarray(clahe_out).save(os.path.join(output_dir, f"{prefix}_clahe.png"))
        Image.fromarray(hm_out).save(os.path.join(output_dir, f"{prefix}_matching.png"))

    else:
        color_ghe = color_histogram_equalization(np_input, method="ghe")
        color_bbhe = color_histogram_equalization(np_input, method="bbhe")
        color_clahe = color_histogram_equalization(np_input, method="clahe", clip_limit=2.5, tile_grid_size=(8, 8))

        equalizations["Global HE (GHE)"] = color_ghe
        equalizations["Bi-Histogram Equalization (BBHE)"] = color_bbhe
        equalizations["Color HSV Equalization"] = color_clahe

        Image.fromarray(color_ghe).save(os.path.join(output_dir, f"{prefix}_color_ghe.png"))
        Image.fromarray(color_bbhe).save(os.path.join(output_dir, f"{prefix}_color_bbhe.png"))
        Image.fromarray(color_clahe).save(os.path.join(output_dir, f"{prefix}_color_clahe.png"))

    # Generate composite comparison grid
    grid_path = os.path.join(output_dir, f"{prefix}_comparison_grid.png")
    create_histogram_comparison_grid(input_img, equalizations, output_path=grid_path)
    print(f"  • Saved Histogram Equalization Comparison Grid: {grid_path}")

    # Print statistical table
    print(f"\n{'Algorithm':<32} | {'Mean':>6} | {'StdDev':>7} | {'Min':>4} | {'Max':>4} | {'Entropy':>8}")
    print("-" * 75)

    input_gray = np.array(input_img.convert("L"))
    orig_stats = compute_image_statistics(input_gray)
    print(f"{'Original Input':<32} | {orig_stats['mean']:>6.2f} | {orig_stats['std_dev']:>7.2f} | {orig_stats['min']:>4.0f} | {orig_stats['max']:>4.0f} | {orig_stats['entropy']:>8.4f}")

    for name, out_arr in equalizations.items():
        arr_for_stats = np.array(Image.fromarray(out_arr).convert("L")) if out_arr.ndim == 3 else out_arr
        stats = compute_image_statistics(arr_for_stats)
        print(f"{name:<32} | {stats['mean']:>6.2f} | {stats['std_dev']:>7.2f} | {stats['min']:>4.0f} | {stats['max']:>4.0f} | {stats['entropy']:>8.4f}")


def main():
    parser = argparse.ArgumentParser(description="Task 4: Histogram Equalization CLI Runner")
    parser.add_argument("--input", type=str, help="Path to input image")
    parser.add_argument("--generate-test-patterns", action="store_true", help="Synthesize low-contrast test patterns & scenery")
    parser.add_argument("--output-dir", type=str, default="task_4_histogram_equalization/outputs", help="Output directory")
    parser.add_argument("--prefix", type=str, default="output", help="Output prefix")

    args = parser.parse_args()

    if args.generate_test_patterns or not args.input:
        print("\n" + "=" * 70)
        print("🖼️ SYNTHESIZING LOW-CONTRAST TEST PATTERNS & EQUALIZATION BENCHMARKS")
        print("=" * 70)

        # 1. Low-Contrast Shadow Scene
        low_scene = create_low_contrast_scene(640, 480)
        print("\n--- Processing Under-Exposed Low-Contrast Night Scene ---")
        process_image_equalizations(low_scene, args.output_dir, prefix="low_contrast")

        # 2. Uneven Illumination Scene
        uneven_scene = create_uneven_illumination_scene(640, 480)
        print("\n--- Processing Uneven Illumination Scene ---")
        process_image_equalizations(uneven_scene, args.output_dir, prefix="uneven_illumination")

        # 3. Low-Contrast Color Scenery
        color_scene = create_scenery_test_image(640, 480)
        # Artificially compress contrast for scenery to simulate haze
        np_scenery = np.array(color_scene).astype(np.float64)
        np_scenery = np.clip(np_scenery * 0.4 + 50, 0, 255).astype(np.uint8)
        color_hazy = Image.fromarray(np_scenery)
        print("\n--- Processing Hazy Low-Contrast Color Landscape ---")
        process_image_equalizations(color_hazy, args.output_dir, prefix="color_haze")

    elif args.input:
        if not os.path.exists(args.input):
            print(f"Error: File not found {args.input}")
            sys.exit(1)
        img = Image.open(args.input)
        print(f"\n--- Processing User Image: {args.input} ---")
        process_image_equalizations(img, args.output_dir, prefix=args.prefix)


if __name__ == "__main__":
    main()
