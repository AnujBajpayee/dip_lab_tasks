"""
Unit Tests for Task 2: RGB to Greyscale Image Conversion
"""

import pytest
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from task_2_rgb_to_greyscale_conversion.grayscale import (
    GrayscaleMethod,
    rgb_to_grayscale,
    rgb_to_grayscale_pixel,
    to_rec601_luminance,
    to_rec709_luminance,
    to_average_grayscale,
    to_lightness_grayscale,
    to_gamma_corrected_grayscale,
    extract_channel,
    REC601_WEIGHTS,
    REC709_WEIGHTS,
)
from task_2_rgb_to_greyscale_conversion.visualizer import (
    create_color_palette_test_image,
    create_scenery_test_image,
    create_comparison_grid,
    compute_image_statistics,
)


def test_pixel_conversions():
    # Pure White
    assert rgb_to_grayscale_pixel(255, 255, 255, GrayscaleMethod.REC601) == pytest.approx(255.0)
    assert rgb_to_grayscale_pixel(255, 255, 255, GrayscaleMethod.REC709) == pytest.approx(255.0)
    assert rgb_to_grayscale_pixel(255, 255, 255, GrayscaleMethod.AVERAGE) == pytest.approx(255.0)
    assert rgb_to_grayscale_pixel(255, 255, 255, GrayscaleMethod.LIGHTNESS) == pytest.approx(255.0)

    # Pure Black
    assert rgb_to_grayscale_pixel(0, 0, 0, GrayscaleMethod.REC601) == pytest.approx(0.0)
    assert rgb_to_grayscale_pixel(0, 0, 0, GrayscaleMethod.REC709) == pytest.approx(0.0)

    # Pure Green (0, 255, 0)
    assert rgb_to_grayscale_pixel(0, 255, 0, GrayscaleMethod.REC601) == pytest.approx(149.685)
    assert rgb_to_grayscale_pixel(0, 255, 0, GrayscaleMethod.REC709) == pytest.approx(182.376)


def test_numpy_operations():
    img_uint8 = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
    gray = to_rec601_luminance(img_uint8)
    assert gray.shape == (10, 10)
    assert gray.dtype == np.uint8

    img_float = img_uint8.astype(np.float32) / 255.0
    gray_f = to_rec709_luminance(img_float)
    assert gray_f.shape == (10, 10)
    assert gray_f.dtype == np.float32


def test_channel_extractions():
    img = np.zeros((4, 4, 3), dtype=np.uint8)
    img[:, :, 0] = 50
    img[:, :, 1] = 150
    img[:, :, 2] = 250
    assert np.all(extract_channel(img, "red") == 50)
    assert np.all(extract_channel(img, "green") == 150)
    assert np.all(extract_channel(img, "blue") == 250)


def test_visualizer_and_synthesizer(tmp_path):
    chart = create_color_palette_test_image(320, 240)
    assert chart.size == (320, 240)
    
    scene = create_scenery_test_image(320, 240)
    assert scene.size == (320, 240)

    grid_p = str(tmp_path / "grid.png")
    create_comparison_grid(scene, {"Rec601": to_rec601_luminance(np.array(scene))}, output_path=grid_p)
    assert Path(grid_p).exists()
