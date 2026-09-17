"""
Task 7: Image Segmentation CLI Runner & Profiler
================================================
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

from task_7_image_segmentation.segmentation import (
    otsu_thresholding,
    adaptive_local_thresholding,
    kmeans_segmentation,
    region_growing_segmentation,
    edge_based_segmentation,
)
from task_7_image_segmentation.visualizer import create_segmentation_comparison_grid


def process_image_segmentation(
    input_img: Image.Image,
    output_dir: str,
    prefix: str = "iiitn_logo"
) -> None:
    """Executes all image segmentation algorithms and generates benchmark grids."""
    os.makedirs(output_dir, exist_ok=True)
    np_rgb = np.array(input_img.convert("RGB"))
    np_gray = np.array(input_img.convert("L"))

    # 1. Otsu's Thresholding
    otsu_mask, otsu_t, otsu_var = otsu_thresholding(np_gray)

    # 2. Adaptive Local Thresholding
    adapt_mask = adaptive_local_thresholding(np_gray, block_size=21, c=8.0)

    # 3. K-Means Clustering (K=4)
    kmeans_img, centroids = kmeans_segmentation(np_rgb, k=4, max_iters=25)

    # 4. Region Growing Segmentation
    h, w = np_gray.shape
    seeds = [(int(h * 0.45), int(w * 0.5)), (int(h * 0.5), int(w * 0.28))]
    region_mask = region_growing_segmentation(np_gray, seed_points=seeds, tolerance=35.0)

    # 5. Sobel Edge Extraction
    grad_norm, edge_binary = edge_based_segmentation(np_gray, threshold=40.0)

    # Save Composite Grid
    grid_path = os.path.join(output_dir, f"{prefix}_comparison_grid.png")
    create_segmentation_comparison_grid(input_img, output_path=grid_path)
    print(f"  • Saved Image Segmentation Comparison Grid: {grid_path}")

    # Print Statistical Table
    print(f"\n{'Segmentation Technique':<32} | {'Optimal Parameters':<28} | {'Output Representation'}")
    print("-" * 95)
    print(f"{'1. Otsu Global Thresholding':<32} | {f'Threshold t* = {otsu_t} (Var={otsu_var:.1f})':<28} | Binary Mask (0 or 255)")
    print(f"{'2. Adaptive Window Thresholding':<32} | {'Block = 21x21, C = 8.0':<28} | Spatially-Varying Mask")
    print(f"{'3. K-Means Color Clustering':<32} | {f'K = 4 Centroid Clusters':<28} | 4-Color Quantized Map")
    print(f"{'4. Seeded Region Growing':<32} | {'Tolerance = 35.0, Seeds = 2':<28} | Connected Region Mask")
    print(f"{'5. Sobel Gradient Boundary':<32} | {'Kernel = 3x3, Edge Thresh = 40':<28} | High-Contrast Contours")


def main():
    parser = argparse.ArgumentParser(description="Task 7: Image Segmentation CLI Runner")
    parser.add_argument("--input", type=str, help="Path to input image")
    parser.add_argument("--output-dir", type=str, default="task_7_image_segmentation/outputs", help="Output directory")
    parser.add_argument("--prefix", type=str, default="iiitn_logo", help="Output prefix")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("✂️ RUNNING IMAGE SEGMENTATION BENCHMARK SUITE")
    print("=" * 70)

    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: File not found: {args.input}")
            sys.exit(1)
        img = Image.open(args.input)
    else:
        logo_path = "assets/iiitn_logo.png"
        if not os.path.exists(logo_path):
            print(f"Error: Benchmark logo not found at {logo_path}")
            sys.exit(1)
        img = Image.open(logo_path)

    process_image_segmentation(img, args.output_dir, prefix=args.prefix)


if __name__ == "__main__":
    main()
