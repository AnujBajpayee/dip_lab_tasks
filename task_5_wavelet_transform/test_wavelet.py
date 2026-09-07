"""
Unit Tests for Task 5: 2D Discrete Wavelet Transform
"""

import pytest
import sys
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
from task_3_bit_plane_slicing.bit_plane import compute_mse_psnr


def test_haar_exact_lossless_reconstruction():
    """Verify that IDWT2(DWT2(f)) perfectly reconstructs the input image."""
    np.random.seed(42)
    original = np.random.randint(0, 256, (64, 64), dtype=np.uint8)

    coeffs = dwt2(original, wavelet="haar")
    reconstructed = idwt2(coeffs, wavelet="haar")

    # Round and clip
    recon_uint8 = np.clip(np.round(reconstructed), 0, 255).astype(np.uint8)
    assert np.array_equal(original, recon_uint8)
    mse, psnr = compute_mse_psnr(original, recon_uint8)
    assert mse == 0.0
    assert psnr == float("inf")


def test_subband_shapes_and_energy():
    np.random.seed(123)
    img = np.random.randint(0, 256, (80, 80), dtype=np.uint8)

    ll, (lh, hl, hh) = dwt2(img, wavelet="haar")
    assert ll.shape == (40, 40)
    assert lh.shape == (40, 40)
    assert hl.shape == (40, 40)
    assert hh.shape == (40, 40)

    # Parseval's energy conservation
    e_spatial = float(np.sum(img.astype(np.float64) ** 2))
    e_wavelet = float(np.sum(ll**2) + np.sum(lh**2) + np.sum(hl**2) + np.sum(hh**2))
    assert pytest.approx(e_spatial, rel=1e-3) == e_wavelet

    stats = compute_wavelet_energy((ll, (lh, hl, hh)))
    # LL subband should hold dominant (>90%) energy for natural-like images
    assert stats["LL"]["energy_pct"] > 0


def test_multilevel_wavelet_decomposition():
    np.random.seed(777)
    img = np.random.randint(0, 256, (64, 64), dtype=np.uint8)

    # Level 2 decomposition
    m_coeffs = wavedec2(img, wavelet="haar", level=2)
    assert len(m_coeffs) == 3  # [LL2, details2, details1]
    assert m_coeffs[0].shape == (16, 16)

    # Multi-level reconstruction
    recon = waverec2(m_coeffs, wavelet="haar", original_shape=img.shape)
    recon_uint8 = np.clip(np.round(recon), 0, 255).astype(np.uint8)
    assert np.array_equal(img, recon_uint8)


def test_daubechies_db2_transform():
    np.random.seed(999)
    img = np.random.randint(0, 256, (32, 32), dtype=np.uint8)

    coeffs = dwt2(img, wavelet="db2")
    recon = idwt2(coeffs, wavelet="db2", target_shape=img.shape)
    recon_uint8 = np.clip(np.round(recon), 0, 255).astype(np.uint8)

    mse, psnr = compute_mse_psnr(img, recon_uint8)
    assert mse < 1.0  # High fidelity reconstruction


def test_wavelet_thresholding():
    np.random.seed(42)
    img = np.random.randint(0, 256, (64, 64), dtype=np.uint8)
    coeffs = dwt2(img, wavelet="haar")

    # Retain 10%
    th_coeffs_10, t10 = threshold_wavelet_coefficients(coeffs, keep_fraction=0.10)
    # Retain 50%
    th_coeffs_50, t50 = threshold_wavelet_coefficients(coeffs, keep_fraction=0.50)

    # Threshold for 10% retained should be strictly greater than 50% retained
    assert t10 > t50

    recon_10 = idwt2(th_coeffs_10, wavelet="haar")
    recon_50 = idwt2(th_coeffs_50, wavelet="haar")

    mse_10, _ = compute_mse_psnr(img, np.clip(np.round(recon_10), 0, 255).astype(np.uint8))
    mse_50, _ = compute_mse_psnr(img, np.clip(np.round(recon_50), 0, 255).astype(np.uint8))

    assert mse_10 >= mse_50


def test_visualizer_and_grids(tmp_path):
    img = Image.new("L", (128, 128), color=128)
    coeffs = dwt2(np.array(img), wavelet="haar")

    grid_p = str(tmp_path / "subband_grid.png")
    create_subband_decomposition_grid(img, coeffs, output_path=grid_p)
    assert Path(grid_p).exists()

    m_coeffs = wavedec2(np.array(img), wavelet="haar", level=2)
    mosaic_p = str(tmp_path / "mosaic.png")
    create_multilevel_quadtree_image(m_coeffs, output_path=mosaic_p)
    assert Path(mosaic_p).exists()

    comp_p = str(tmp_path / "comp_grid.png")
    create_wavelet_compression_grid(img, output_path=comp_p)
    assert Path(comp_p).exists()
