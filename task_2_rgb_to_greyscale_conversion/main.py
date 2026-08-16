"""
Task 2: RGB to Greyscale Image Conversion Entry Point & CLI Runner
=================================================================
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

from task_2_rgb_to_greyscale_conversion.grayscale import (
    GrayscaleMethod,
    rgb_to_grayscale,
    to_rec601_luminance,
    to_rec709_luminance,
    to_average_grayscale,
    to_lightness_grayscale,
    to_gamma_corrected_grayscale,
    extract_channel,
)
from task_2_rgb_to_greyscale_conversion.visualizer import (
    create_color_palette_test_image,
    create_scenery_test_image,
    create_comparison_grid,
    compute_image_statistics,
)


def process_image(
    input_img: Image.Image,
    output_dir: str,
    prefix: str = "img"
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    img_rgb = input_img.convert("RGB")
    np_rgb = np.array(img_rgb)

    algorithms = {
        "Rec.601 Luminosity": (to_rec601_luminance(np_rgb), f"{prefix}_rec601.png"),
        "Rec.709 Luminosity": (to_rec709_luminance(np_rgb), f"{prefix}_rec709.png"),
        "Simple Average": (to_average_grayscale(np_rgb), f"{prefix}_average.png"),
        "HSL Lightness": (to_lightness_grayscale(np_rgb), f"{prefix}_lightness.png"),
        "Gamma-Corrected Linear": (to_gamma_corrected_grayscale(np_rgb), f"{prefix}_gamma.png"),
        "Red Channel": (extract_channel(np_rgb, "red"), f"{prefix}_channel_red.png"),
        "Green Channel": (extract_channel(np_rgb, "green"), f"{prefix}_channel_green.png"),
        "Blue Channel": (extract_channel(np_rgb, "blue"), f"{prefix}_channel_blue.png"),
    }

    orig_path = os.path.join(output_dir, f"{prefix}_original_rgb.png")
    img_rgb.save(orig_path)
    print(f"  • Saved Original RGB: {orig_path}")

    print(f"\n{'Algorithm':<30} | {'Mean':>6} | {'StdDev':>7} | {'Min':>4} | {'Max':>4} | {'Entropy':>8}")
    print("-" * 72)

    conversions_dict = {}
    for name, (gray_arr, filename) in algorithms.items():
        out_path = os.path.join(output_dir, filename)
        Image.fromarray(gray_arr).save(out_path)
        conversions_dict[name] = gray_arr
        
        stats = compute_image_statistics(gray_arr)
        print(f"{name:<30} | {stats['mean']:>6.2f} | {stats['std_dev']:>7.2f} | {stats['min']:>4.0f} | {stats['max']:>4.0f} | {stats['entropy']:>8.4f}")

    grid_path = os.path.join(output_dir, f"{prefix}_comparison_grid.png")
    create_comparison_grid(img_rgb, conversions_dict, output_path=grid_path)
    print(f"\n  • Saved Side-by-Side Comparison Grid: {grid_path}\n")


def main():
    parser = argparse.ArgumentParser(description="Task 2: RGB-to-Greyscale Image Processing CLI")
    parser.add_argument("--input", type=str, help="Path to input image file")
    parser.add_argument("--generate-test-patterns", action="store_true", help="Synthesize color calibration & scenery test images")
    parser.add_argument("--output-dir", type=str, default="task_2_rgb_to_greyscale_conversion/outputs", help="Output directory")
    parser.add_argument("--prefix", type=str, default="output", help="Output prefix")

    args = parser.parse_args()

    if args.generate_test_patterns or not args.input:
        print("\n" + "=" * 60)
        print("🖼️ SYNTHESIZING CALIBRATION TEST PATTERNS & SCENERY")
        print("=" * 60)
        
        chart_img = create_color_palette_test_image(640, 480)
        print("\n--- Processing Calibrated Color Test Chart ---")
        process_image(chart_img, args.output_dir, prefix="color_chart")

        scene_img = create_scenery_test_image(640, 480)
        print("--- Processing Landscape Scenery Scene ---")
        process_image(scene_img, args.output_dir, prefix="scenery")
        
    elif args.input:
        if not os.path.exists(args.input):
            print(f"Error: Input image not found at {args.input}")
            sys.exit(1)
        img = Image.open(args.input)
        print(f"\n--- Processing User Image: {args.input} ---")
        process_image(img, args.output_dir, prefix=args.prefix)


if __name__ == "__main__":
    main()
