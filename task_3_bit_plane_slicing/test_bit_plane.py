"""
Unit Tests for Task 3: Bit Plane Slicing & Digital Steganography
"""

import pytest
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from task_3_bit_plane_slicing.bit_plane import (
    extract_bit_plane,
    extract_all_bit_planes,
    reconstruct_from_bit_planes,
    reconstruct_cumulative_msb,
    compute_mse_psnr,
    compute_bit_plane_metrics,
    embed_watermark_lsb,
    extract_watermark_lsb,
    BIT_WEIGHTS,
    BIT_ENERGY_PERCENTAGES,
)
from task_3_bit_plane_slicing.visualizer import (
    create_rich_test_pattern,
    create_watermark_pattern,
    create_bit_plane_grid,
    create_cumulative_reconstruction_grid,
    create_steganography_grid,
)


def test_bit_weights_and_energy():
    assert BIT_WEIGHTS == (1, 2, 4, 8, 16, 32, 64, 128)
    assert sum(BIT_WEIGHTS) == 255
    assert pytest.approx(sum(BIT_ENERGY_PERCENTAGES), 0.01) == 100.0
    assert pytest.approx(BIT_ENERGY_PERCENTAGES[7], 0.01) == 50.20
    assert pytest.approx(BIT_ENERGY_PERCENTAGES[0], 0.01) == 0.39


def test_single_pixel_bit_slicing():
    # Value 133 = 128 + 4 + 1 -> binary 10000101
    val = np.array([[133]], dtype=np.uint8)
    
    assert extract_bit_plane(val, 7, scale_to_255=False)[0, 0] == 1
    assert extract_bit_plane(val, 6, scale_to_255=False)[0, 0] == 0
    assert extract_bit_plane(val, 5, scale_to_255=False)[0, 0] == 0
    assert extract_bit_plane(val, 4, scale_to_255=False)[0, 0] == 0
    assert extract_bit_plane(val, 3, scale_to_255=False)[0, 0] == 0
    assert extract_bit_plane(val, 2, scale_to_255=False)[0, 0] == 1
    assert extract_bit_plane(val, 1, scale_to_255=False)[0, 0] == 0
    assert extract_bit_plane(val, 0, scale_to_255=False)[0, 0] == 1

    # Scaled to 255
    assert extract_bit_plane(val, 7, scale_to_255=True)[0, 0] == 255
    assert extract_bit_plane(val, 6, scale_to_255=True)[0, 0] == 0


def test_lossless_mathematical_identity():
    """Verify that sum(2^k * b_k) perfectly reconstructs the original image."""
    np.random.seed(42)
    original = np.random.randint(0, 256, (32, 32), dtype=np.uint8)
    
    planes_binary = extract_all_bit_planes(original, scale_to_255=False)
    reconstructed = reconstruct_from_bit_planes(planes_binary, list(range(8)))

    assert np.array_equal(original, reconstructed)
    mse, psnr = compute_mse_psnr(original, reconstructed)
    assert mse == 0.0
    assert psnr == float("inf")


def test_pure_python_fallback():
    py_img = [
        [0, 128, 255],
        [1, 64, 192]
    ]
    plane_7 = extract_bit_plane(py_img, 7, scale_to_255=False)
    assert plane_7 == [
        [0, 1, 1],
        [0, 0, 1]
    ]

    all_planes = extract_all_bit_planes(py_img, scale_to_255=False)
    reconstructed = reconstruct_from_bit_planes(all_planes, list(range(8)))
    assert reconstructed == py_img


def test_cumulative_reconstruction_monotonicity():
    np.random.seed(123)
    img = np.random.randint(0, 256, (20, 20), dtype=np.uint8)
    
    results = reconstruct_cumulative_msb(img)
    assert len(results) == 8

    prev_mse = float("inf")
    for idx, (label, recon) in enumerate(results):
        mse, psnr = compute_mse_psnr(img, recon)
        assert mse <= prev_mse, f"MSE must be monotonically decreasing (step {idx})"
        prev_mse = mse
    
    # Final reconstruction should be exact 0 MSE
    assert prev_mse == 0.0


def test_steganography_lossless_extraction():
    np.random.seed(999)
    cover = np.random.randint(0, 256, (64, 64), dtype=np.uint8)
    watermark = np.random.choice([0, 255], size=(64, 64)).astype(np.uint8)

    stego = embed_watermark_lsb(cover, watermark, bit_plane=0)
    
    # Stego image must be very close to cover (MSE <= 1.0)
    mse, psnr = compute_mse_psnr(cover, stego)
    assert mse <= 1.0
    assert psnr >= 48.0

    # Extracted watermark must be 100% identical to original watermark
    extracted = extract_watermark_lsb(stego, bit_plane=0, scale_to_255=True)
    assert np.array_equal(watermark, extracted)


def test_invalid_parameters():
    img = np.zeros((10, 10), dtype=np.uint8)
    with pytest.raises(ValueError):
        extract_bit_plane(img, 8)
    with pytest.raises(ValueError):
        extract_bit_plane(img, -1)
    with pytest.raises(ValueError):
        reconstruct_from_bit_planes([img]*8, [8])


def test_visualizers_and_grids(tmp_path):
    pattern = create_rich_test_pattern(320, 240)
    assert pattern.size == (320, 240)

    wm = create_watermark_pattern(320, 240)
    assert wm.size == (320, 240)

    planes = extract_all_bit_planes(np.array(pattern), scale_to_255=True)
    grid_p = str(tmp_path / "bit_grid.png")
    create_bit_plane_grid(pattern, planes, output_path=grid_p)
    assert Path(grid_p).exists()

    cumul_p = str(tmp_path / "cumul_grid.png")
    cumul_results = reconstruct_cumulative_msb(np.array(pattern))
    create_cumulative_reconstruction_grid(pattern, cumul_results, output_path=cumul_p)
    assert Path(cumul_p).exists()

    stego_p = str(tmp_path / "stego_grid.png")
    stego_arr = embed_watermark_lsb(np.array(pattern), np.array(wm), bit_plane=0)
    extracted_arr = extract_watermark_lsb(stego_arr, bit_plane=0, scale_to_255=True)
    create_steganography_grid(pattern, wm, stego_arr, extracted_arr, output_path=stego_p)
    assert Path(stego_p).exists()
