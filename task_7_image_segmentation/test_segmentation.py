"""
Unit Tests for Task 7: Image Segmentation Engine
"""

import pytest
import sys
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from task_7_image_segmentation.segmentation import (
    otsu_thresholding,
    adaptive_local_thresholding,
    kmeans_segmentation,
    region_growing_segmentation,
    edge_based_segmentation,
)
from task_7_image_segmentation.visualizer import create_segmentation_comparison_grid


def test_otsu_thresholding_bimodal():
    # Construct distinct bimodal image (50% at 30, 50% at 220)
    img = np.zeros((40, 40), dtype=np.uint8)
    img[:20, :] = 30
    img[20:, :] = 220

    mask, t_opt, max_var = otsu_thresholding(img)
    # Optimal threshold should cleanly lie in the valley between 30 and 220
    assert 30 <= t_opt <= 220
    assert max_var > 0
    assert np.all(mask[:20, :] == 0)
    assert np.all(mask[20:, :] == 255)


def test_adaptive_thresholding():
    # Gradient background with sharp feature in center
    img = np.zeros((50, 50), dtype=np.uint8)
    for x in range(50):
        img[:, x] = int(x * 4)  # gradient 0 to 200
    img[20:30, 20:30] = 255  # bright local square

    mask = adaptive_local_thresholding(img, block_size=15, c=10.0)
    assert mask.shape == (50, 50)
    assert mask.dtype == np.uint8
    # Center square should be foreground
    assert np.all(mask[22:28, 22:28] == 255)


def test_kmeans_clustering():
    np.random.seed(42)
    # 3 distinct color regions
    img_rgb = np.zeros((30, 30, 3), dtype=np.uint8)
    img_rgb[:10, :, :] = [255, 0, 0]    # Red
    img_rgb[10:20, :, :] = [0, 255, 0]  # Green
    img_rgb[20:, :, :] = [0, 0, 255]    # Blue

    segmented, centroids = kmeans_segmentation(img_rgb, k=3, max_iters=20)
    assert segmented.shape == (30, 30, 3)
    assert len(centroids) == 3


def test_region_growing():
    img = np.zeros((40, 40), dtype=np.uint8)
    # Central island
    img[15:25, 15:25] = 200

    mask = region_growing_segmentation(img, seed_points=[(20, 20)], tolerance=20.0)
    assert mask.shape == (40, 40)
    # Region growing should accurately capture the central island
    assert np.all(mask[16:24, 16:24] == 255)
    # Background should remain 0
    assert np.all(mask[:10, :10] == 0)


def test_edge_based_sobel_gradient():
    img = np.zeros((30, 30), dtype=np.uint8)
    img[:, 15:] = 255  # Vertical sharp step edge at x=15

    grad_norm, binary_edges = edge_based_segmentation(img, threshold=50.0)
    assert grad_norm.shape == (30, 30)
    # High gradient response along boundary column 14-15
    assert np.all(binary_edges[:, 14:16] == 255)


def test_visualizer_comparison_grid(tmp_path):
    img = Image.new("RGB", (64, 64), color=(50, 100, 150))
    grid_p = str(tmp_path / "seg_grid.png")
    create_segmentation_comparison_grid(img, output_path=grid_p)
    assert Path(grid_p).exists()
