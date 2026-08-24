"""
Task 3: Bit Plane Slicing & Digital Steganography Entry Point & CLI Runner
==========================================================================
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

from task_3_bit_plane_slicing.bit_plane import (
    extract_bit_plane,
    extract_all_bit_planes,
    reconstruct_from_bit_planes,
    reconstruct_cumulative_msb,
    compute_bit_plane_metrics,
    embed_watermark_lsb,
    extract_watermark_lsb,
    compute_mse_psnr,
)
from task_3_bit_plane_slicing.visualizer import (
    create_rich_test_pattern,
    create_watermark_pattern,
    create_bit_plane_grid,
    create_cumulative_reconstruction_grid,
    create_steganography_grid,
)
from task_2_rgb_to_greyscale_conversion.visualizer import create_scenery_test_image


def process_image_bit_planes(
    input_img: Image.Image,
    output_dir: str,
    prefix: str = "img",
    run_stego: bool = True,
    watermark_img: Image.Image | None = None
) -> None:
    """
    Executes full bit-plane slicing, multi-plane cumulative reconstruction,
    metrics reporting, and optional LSB digital steganography.
    """
    os.makedirs(output_dir, exist_ok=True)
    img_gray = input_img.convert("L")
    np_gray = np.array(img_gray)
    width, height = img_gray.size

    # 1. Save Original Input
    orig_path = os.path.join(output_dir, f"{prefix}_original.png")
    img_gray.save(orig_path)
    print(f"  • Saved Original Input Image: {orig_path}")

    # 2. Extract All 8 Bit Planes
    planes_scaled = extract_all_bit_planes(np_gray, scale_to_255=True)
    planes_binary = extract_all_bit_planes(np_gray, scale_to_255=False)

    for k in range(8):
        plane_name = f"bit_{k}_msb" if k == 7 else f"bit_{k}_lsb" if k == 0 else f"bit_{k}"
        plane_file = os.path.join(output_dir, f"{prefix}_plane_{k}.png")
        Image.fromarray(planes_scaled[k]).save(plane_file)

    # 3. Create 9-Panel Bit Planes Grid
    grid_path = os.path.join(output_dir, f"{prefix}_bit_planes_grid.png")
    create_bit_plane_grid(img_gray, planes_scaled, output_path=grid_path)
    print(f"  • Saved 8-Bit Planes Composite Grid: {grid_path}")

    # 4. Progressive Cumulative Reconstructions
    cumulative_results = reconstruct_cumulative_msb(np_gray)
    recon_grid_path = os.path.join(output_dir, f"{prefix}_cumulative_reconstruction_grid.png")
    create_cumulative_reconstruction_grid(img_gray, cumulative_results, output_path=recon_grid_path)
    print(f"  • Saved Progressive Reconstruction Grid: {recon_grid_path}")

    # 5. Print Quantitative Theoretical vs Empirical Metrics Table
    metrics = compute_bit_plane_metrics(np_gray)
    print(f"\n{'Bit Plane':<14} | {'Weight':>6} | {'Energy %':>9} | {'Cumul. Energy':>14} | {'Active %':>9} | {'Entropy':>8} | {'Cumul. MSE':>11} | {'Cumul. PSNR (dB)':>17}")
    print("-" * 105)
    for m in metrics:
        psnr_str = f"{m['cumulative_psnr_db']:.2f}" if m['cumulative_psnr_db'] != float("inf") else "Lossless (inf)"
        print(
            f"{m['bit_name']:<14} | {m['weight']:>6} | {m['theoretical_energy_pct']:>8.2f}% | "
            f"{m['cumulative_energy_pct']:>13.2f}% | {m['active_pixels_pct']:>8.2f}% | "
            f"{m['entropy']:>8.4f} | {m['cumulative_mse']:>11.2f} | {psnr_str:>17}"
        )

    # 6. LSB Digital Steganography / Watermarking Demonstration
    if run_stego:
        if watermark_img is None:
            watermark_img = create_watermark_pattern(width, height, label="DIP LAB 2026")
        else:
            watermark_img = watermark_img.resize((width, height)).convert("L")

        wm_np = np.array(watermark_img)
        wm_path = os.path.join(output_dir, f"{prefix}_watermark_original.png")
        watermark_img.save(wm_path)

        stego_np = embed_watermark_lsb(np_gray, wm_np, bit_plane=0)
        stego_path = os.path.join(output_dir, f"{prefix}_stego_embedded.png")
        Image.fromarray(stego_np).save(stego_path)

        extracted_np = extract_watermark_lsb(stego_np, bit_plane=0, scale_to_255=True)
        extracted_path = os.path.join(output_dir, f"{prefix}_extracted_watermark.png")
        Image.fromarray(extracted_np).save(extracted_path)

        stego_grid_path = os.path.join(output_dir, f"{prefix}_steganography_demo.png")
        create_steganography_grid(img_gray, watermark_img, stego_np, extracted_np, output_path=stego_grid_path)
        
        mse_stego, psnr_stego = compute_mse_psnr(np_gray, stego_np)
        print(f"  • Steganography Embedded (LSB Bit 0) -> MSE: {mse_stego:.2f}, PSNR: {psnr_stego:.2f} dB (Imperceptible)")
        print(f"  • Saved Steganography Pipeline Grid: {stego_grid_path}\n")


def main():
    parser = argparse.ArgumentParser(description="Task 3: Bit Plane Slicing & Digital Steganography CLI")
    parser.add_argument("--input", type=str, help="Path to input image file")
    parser.add_argument("--watermark", type=str, help="Path to binary watermark image (optional)")
    parser.add_argument("--generate-test-patterns", action="store_true", help="Synthesize rich test target and scenery scenes")
    parser.add_argument("--output-dir", type=str, default="task_3_bit_plane_slicing/outputs", help="Output directory")
    parser.add_argument("--prefix", type=str, default="output", help="Output prefix")

    args = parser.parse_args()

    if args.generate_test_patterns or not args.input:
        print("\n" + "=" * 70)
        print("🖼️ SYNTHESIZING CALIBRATED BIT PLANE TEST PATTERNS & SCENERY")
        print("=" * 70)

        # 1. Calibrated Synthetic Target
        test_pattern = create_rich_test_pattern(640, 480)
        print("\n--- Processing Calibrated Bit-Plane Test Pattern ---")
        process_image_bit_planes(test_pattern, args.output_dir, prefix="test_pattern")

        # 2. Natural Landscape Scenery Scene
        scenery = create_scenery_test_image(640, 480).convert("L")
        print("\n--- Processing Landscape Scenery Scene ---")
        process_image_bit_planes(scenery, args.output_dir, prefix="scenery")

    elif args.input:
        if not os.path.exists(args.input):
            print(f"Error: Input image not found at {args.input}")
            sys.exit(1)
        img = Image.open(args.input)
        wm = Image.open(args.watermark) if args.watermark and os.path.exists(args.watermark) else None
        print(f"\n--- Processing User Image: {args.input} ---")
        process_image_bit_planes(img, args.output_dir, prefix=args.prefix, watermark_img=wm)


if __name__ == "__main__":
    main()
