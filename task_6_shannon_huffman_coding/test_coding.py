"""
Unit Tests for Task 6: Shannon-Fano & Huffman Image Entropy Coding
"""

import pytest
import sys
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
from task_3_bit_plane_slicing.bit_plane import compute_mse_psnr


def _is_prefix_free(codebook: dict) -> bool:
    """Helper to verify that no codeword is a prefix of any other codeword."""
    codes = list(codebook.values())
    for i in range(len(codes)):
        for j in range(len(codes)):
            if i != j and codes[j].startswith(codes[i]):
                return False
    return True


def test_entropy_computation():
    # Uniform 4-symbol distribution -> Entropy = - 4 * (0.25 * log2(0.25)) = 2.0 bits
    probs_uniform = {0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25}
    assert pytest.approx(compute_entropy(probs_uniform), rel=1e-4) == 2.0

    # Deterministic single symbol -> Entropy = 0.0
    probs_single = {100: 1.0}
    assert compute_entropy(probs_single) == 0.0


def test_shannon_fano_prefix_free():
    np.random.seed(42)
    img = np.random.randint(0, 16, (32, 32), dtype=np.uint8)
    probs = compute_symbol_probabilities(img)
    codebook = build_shannon_fano_codebook(probs)

    assert len(codebook) == len(probs)
    assert _is_prefix_free(codebook)


def test_huffman_optimality_and_prefix_free():
    np.random.seed(123)
    img = np.random.randint(0, 32, (40, 40), dtype=np.uint8)
    probs = compute_symbol_probabilities(img)

    sf_codebook = build_shannon_fano_codebook(probs)
    hf_codebook = build_huffman_codebook(probs)

    assert _is_prefix_free(hf_codebook)

    h_x = compute_entropy(probs)
    sf_metrics = compute_coding_metrics(probs, sf_codebook)
    hf_metrics = compute_coding_metrics(probs, hf_codebook)

    # Huffman code length should be less than or equal to Shannon-Fano code length
    assert hf_metrics["avg_length_bits"] <= sf_metrics["avg_length_bits"] + 1e-4
    # Shannon's Source Coding Theorem: H(X) <= L_avg < H(X) + 1
    assert hf_metrics["avg_length_bits"] >= h_x - 1e-4
    assert hf_metrics["avg_length_bits"] < h_x + 1.0


def test_lossless_encode_decode_pipeline():
    np.random.seed(777)
    original = np.random.randint(0, 64, (28, 28), dtype=np.uint8)
    probs = compute_symbol_probabilities(original)
    codebook = build_huffman_codebook(probs)

    bitstream, shape = encode_image(original, codebook)
    decoded = decode_image(bitstream, codebook, shape)

    assert np.array_equal(original, decoded)
    mse, psnr = compute_mse_psnr(original, decoded)
    assert mse == 0.0
    assert psnr == float("inf")


def test_visualizer_comparison_grid(tmp_path):
    img = Image.new("L", (64, 64), color=100)
    grid_p = str(tmp_path / "sf_hf_grid.png")
    create_shannon_huffman_comparison_grid(img, output_path=grid_p)
    assert Path(grid_p).exists()
