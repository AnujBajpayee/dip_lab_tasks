"""
Task 6: Shannon-Fano & Huffman Image Coding CLI Runner
======================================================
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

from task_6_shannon_huffman_coding.coding import (
    compute_symbol_probabilities,
    compute_entropy,
    build_shannon_fano_codebook,
    build_huffman_codebook,
    encode_image,
    decode_image,
    compute_coding_metrics,
)
from task_6_shannon_huffman_coding.visualizer import create_shannon_huffman_comparison_grid


def process_image_coding(
    input_img: Image.Image,
    output_dir: str,
    prefix: str = "iiitn_logo"
) -> None:
    """Performs Shannon-Fano and Huffman coding analysis and generates benchmark grids."""
    os.makedirs(output_dir, exist_ok=True)
    np_gray = np.array(input_img.convert("L"))

    # 1. Probabilities & Entropy
    probs = compute_symbol_probabilities(np_gray)
    entropy_val = compute_entropy(probs)

    # 2. Build Codebooks
    sf_codebook = build_shannon_fano_codebook(probs)
    hf_codebook = build_huffman_codebook(probs)

    # 3. Compute Metrics
    sf_metrics = compute_coding_metrics(probs, sf_codebook)
    hf_metrics = compute_coding_metrics(probs, hf_codebook)

    # 4. Save Lossless Comparison Grid
    grid_path = os.path.join(output_dir, f"{prefix}_comparison_grid.png")
    create_shannon_huffman_comparison_grid(input_img, output_path=grid_path)
    print(f"  • Saved Shannon/Huffman Coding Comparison Grid: {grid_path}")

    # 5. Print Statistical Table
    sf_len_str = f"{sf_metrics['avg_length_bits']} bits"
    sf_eff_str = f"{sf_metrics['efficiency_pct']} %"
    sf_cr_str = f"{sf_metrics['compression_ratio']}:1 ({sf_metrics['savings_pct']}%)"

    hf_len_str = f"{hf_metrics['avg_length_bits']} bits"
    hf_eff_str = f"{hf_metrics['efficiency_pct']} %"
    hf_cr_str = f"{hf_metrics['compression_ratio']}:1 ({hf_metrics['savings_pct']}%)"

    print(f"\n{'Coding Algorithm':<26} | {'Entropy H(X)':>13} | {'Avg Length L_avg':>16} | {'Efficiency η':>12} | {'Compression Ratio':>17}")
    print("-" * 95)
    print(f"{'Uncompressed 8-Bit':<26} | {entropy_val:>13.4f} | {'8.0000 bits':>16} | {'--':>12} | {'1.000:1 (Base)':>17}")
    print(f"{'Shannon-Fano Coding':<26} | {entropy_val:>13.4f} | {sf_len_str:>16} | {sf_eff_str:>12} | {sf_cr_str:>17}")
    print(f"{'Huffman Optimal Coding':<26} | {entropy_val:>13.4f} | {hf_len_str:>16} | {hf_eff_str:>12} | {hf_cr_str:>17}")


def main():
    parser = argparse.ArgumentParser(description="Task 6: Shannon-Fano & Huffman Image Coding CLI Runner")
    parser.add_argument("--input", type=str, help="Path to input image")
    parser.add_argument("--output-dir", type=str, default="task_6_shannon_huffman_coding/outputs", help="Output directory")
    parser.add_argument("--prefix", type=str, default="iiitn_logo", help="Output prefix")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("📊 RUNNING SHANNON-FANO & HUFFMAN LOSSLESS ENTROPY CODING")
    print("=" * 70)

    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: File not found: {args.input}")
            sys.exit(1)
        img = Image.open(args.input)
    else:
        # Default IIITN logo
        logo_path = "assets/iiitn_logo.png"
        if not os.path.exists(logo_path):
            print(f"Error: Benchmark logo not found at {logo_path}")
            sys.exit(1)
        img = Image.open(logo_path)

    process_image_coding(img, args.output_dir, prefix=args.prefix)


if __name__ == "__main__":
    main()
