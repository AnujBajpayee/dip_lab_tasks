"""
Unit Tests for Task 4: Histogram Equalization Types & Execution
"""

import pytest
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from task_4_histogram_equalization.histogram import (
    compute_histogram,
    compute_cdf,
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
    draw_histogram_bar,
)


def test_compute_histogram_and_cdf():
    img = np.array([[10, 10, 20], [20, 30, 30]], dtype=np.uint8)
    hist = compute_histogram(img, bins=256)
    assert hist[10] == 2
    assert hist[20] == 2
    assert hist[30] == 2
    assert hist[0] == 0

    cdf = compute_cdf(hist)
    assert cdf[10] == 2
    assert cdf[20] == 4
    assert cdf[30] == 6
    assert cdf[255] == 6


def test_global_histogram_equalization():
    # Low-contrast image concentrated in [10, 50]
    np.random.seed(42)
    low_contrast = np.random.randint(10, 50, (30, 30), dtype=np.uint8)
    equalized = global_histogram_equalization(low_contrast)

    assert equalized.shape == (30, 30)
    assert equalized.dtype == np.uint8
    # Global HE should expand the range across [0, 255]
    assert np.min(equalized) <= 5
    assert np.max(equalized) >= 250
    assert np.std(equalized) > np.std(low_contrast)


def test_bbhe_mean_preservation():
    # Dark image with low mean
    np.random.seed(100)
    dark_img = np.random.randint(20, 60, (40, 40), dtype=np.uint8)
    orig_mean = np.mean(dark_img)

    ghe_out = global_histogram_equalization(dark_img)
    bbhe_out = bi_histogram_equalization(dark_img)

    ghe_mean = np.mean(ghe_out)
    bbhe_mean = np.mean(bbhe_out)

    # BBHE mean should stay closer to orig_mean than GHE
    assert abs(bbhe_mean - orig_mean) < abs(ghe_mean - orig_mean)


def test_clahe_contrast_enhancement():
    np.random.seed(2026)
    img = np.random.randint(50, 100, (64, 64), dtype=np.uint8)
    clahe_out = clahe(img, clip_limit=2.0, tile_grid_size=(4, 4))

    assert clahe_out.shape == (64, 64)
    assert clahe_out.dtype == np.uint8
    assert np.std(clahe_out) > np.std(img)


def test_histogram_matching():
    np.random.seed(777)
    src = np.random.randint(0, 50, (30, 30), dtype=np.uint8)
    target = np.random.randint(200, 255, (30, 30), dtype=np.uint8)

    matched = histogram_matching(src, target)
    assert matched.shape == (30, 30)
    # Matched image intensities should shift into target range [200, 255]
    assert np.mean(matched) >= 180


def test_color_histogram_equalization():
    color_img = np.zeros((20, 20, 3), dtype=np.uint8)
    color_img[:, :, 0] = 50   # Red dominant low-contrast
    color_img[:, :, 1] = 20
    color_img[:, :, 2] = 20

    eq_color = color_histogram_equalization(color_img, method="clahe")
    assert eq_color.shape == (20, 20, 3)
    # Red should remain dominant over green and blue
    assert np.all(eq_color[:, :, 0] >= eq_color[:, :, 1])
    assert np.all(eq_color[:, :, 0] >= eq_color[:, :, 2])


def test_pure_python_fallback():
    py_img = [[10, 20], [30, 40]]
    ghe_py = global_histogram_equalization(py_img)
    assert len(ghe_py) == 2
    assert len(ghe_py[0]) == 2
    assert ghe_py[0][0] == 0
    assert ghe_py[1][1] == 255

    bbhe_py = bi_histogram_equalization(py_img)
    assert len(bbhe_py) == 2


def test_visualizer_and_grids(tmp_path):
    scene = create_low_contrast_scene(320, 240)
    assert scene.size == (320, 240)

    plot = draw_histogram_bar(np.array(scene), width=320, height=60)
    assert plot.size == (320, 60)

    grid_p = str(tmp_path / "hist_grid.png")
    eq_dict = {"Global HE (GHE)": global_histogram_equalization(np.array(scene))}
    create_histogram_comparison_grid(scene, eq_dict, output_path=grid_p)
    assert Path(grid_p).exists()
