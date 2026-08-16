"""
RGB to Greyscale Conversion Algorithms
======================================
Scientific and standard industrial implementations of color-to-greyscale
transformations based on human visual sensitivity and ITU-R standards.
"""

from __future__ import annotations
from enum import Enum
from typing import Union, Tuple, List, Optional, Any
import math

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class GrayscaleMethod(str, Enum):
    """Supported greyscale conversion algorithms."""
    REC601 = "rec601"           # ITU-R BT.601 standard luma (NTSC/PAL)
    REC709 = "rec709"           # ITU-R BT.709 / sRGB standard luma (HDTV)
    AVERAGE = "average"         # Simple arithmetic mean (R+G+B)/3
    LIGHTNESS = "lightness"     # Desaturation / HSL model (max+min)/2
    GAMMA_CORRECTED = "gamma"   # Linearized perceptual luminance (sRGB gamma expansion)
    RED_CHANNEL = "red"         # Single red channel extraction
    GREEN_CHANNEL = "green"     # Single green channel extraction
    BLUE_CHANNEL = "blue"       # Single blue channel extraction


# Standard ITU-R BT.601 Weights (SDTV)
REC601_WEIGHTS = (0.299, 0.587, 0.114)

# Standard ITU-R BT.709 Weights (HDTV / sRGB)
REC709_WEIGHTS = (0.2126, 0.7152, 0.0722)


def rgb_to_grayscale_pixel(
    r: float,
    g: float,
    b: float,
    method: GrayscaleMethod | str = GrayscaleMethod.REC601,
    gamma: float = 2.2
) -> float:
    """
    Converts a single (R, G, B) pixel to a greyscale scalar value.
    """
    method = GrayscaleMethod(method)

    if method == GrayscaleMethod.REC601:
        return REC601_WEIGHTS[0] * r + REC601_WEIGHTS[1] * g + REC601_WEIGHTS[2] * b

    elif method == GrayscaleMethod.REC709:
        return REC709_WEIGHTS[0] * r + REC709_WEIGHTS[1] * g + REC709_WEIGHTS[2] * b

    elif method == GrayscaleMethod.AVERAGE:
        return (r + g + b) / 3.0

    elif method == GrayscaleMethod.LIGHTNESS:
        return (max(r, g, b) + min(r, g, b)) / 2.0

    elif method == GrayscaleMethod.GAMMA_CORRECTED:
        scale = 255.0 if max(r, g, b) > 1.0 else 1.0
        r_norm = r / scale
        g_norm = g / scale
        b_norm = b / scale

        r_lin = r_norm ** gamma
        g_lin = g_norm ** gamma
        b_lin = b_norm ** gamma

        y_lin = REC709_WEIGHTS[0] * r_lin + REC709_WEIGHTS[1] * g_lin + REC709_WEIGHTS[2] * b_lin
        y_encoded = (y_lin ** (1.0 / gamma)) * scale
        return y_encoded

    elif method == GrayscaleMethod.RED_CHANNEL:
        return float(r)

    elif method == GrayscaleMethod.GREEN_CHANNEL:
        return float(g)

    elif method == GrayscaleMethod.BLUE_CHANNEL:
        return float(b)

    else:
        raise ValueError(f"Unsupported greyscale method: {method}")


def _rgb_to_grayscale_numpy(
    image: np.ndarray,
    method: GrayscaleMethod | str = GrayscaleMethod.REC601,
    gamma: float = 2.2
) -> np.ndarray:
    """Vectorized NumPy implementation for RGB to Greyscale conversion."""
    method = GrayscaleMethod(method)

    if image.ndim == 2:
        return image.copy()

    if image.ndim != 3 or image.shape[2] < 3:
        raise ValueError(f"Expected 3D array (H, W, C), got {image.shape}")

    r = image[:, :, 0].astype(np.float64)
    g = image[:, :, 1].astype(np.float64)
    b = image[:, :, 2].astype(np.float64)

    is_uint8 = np.issubdtype(image.dtype, np.integer)

    if method == GrayscaleMethod.REC601:
        gray = REC601_WEIGHTS[0] * r + REC601_WEIGHTS[1] * g + REC601_WEIGHTS[2] * b

    elif method == GrayscaleMethod.REC709:
        gray = REC709_WEIGHTS[0] * r + REC709_WEIGHTS[1] * g + REC709_WEIGHTS[2] * b

    elif method == GrayscaleMethod.AVERAGE:
        gray = (r + g + b) / 3.0

    elif method == GrayscaleMethod.LIGHTNESS:
        rgb_stack = np.stack([r, g, b], axis=-1)
        max_c = np.max(rgb_stack, axis=-1)
        min_c = np.min(rgb_stack, axis=-1)
        gray = (max_c + min_c) / 2.0

    elif method == GrayscaleMethod.GAMMA_CORRECTED:
        scale = 255.0 if is_uint8 or np.max(image) > 1.0 else 1.0
        r_norm = np.clip(r / scale, 0.0, 1.0)
        g_norm = np.clip(g / scale, 0.0, 1.0)
        b_norm = np.clip(b / scale, 0.0, 1.0)

        r_lin = np.power(r_norm, gamma)
        g_lin = np.power(g_norm, gamma)
        b_lin = np.power(b_norm, gamma)

        y_lin = REC709_WEIGHTS[0] * r_lin + REC709_WEIGHTS[1] * g_lin + REC709_WEIGHTS[2] * b_lin
        y_lin = np.clip(y_lin, 0.0, 1.0)

        gray = np.power(y_lin, 1.0 / gamma) * scale

    elif method == GrayscaleMethod.RED_CHANNEL:
        gray = r

    elif method == GrayscaleMethod.GREEN_CHANNEL:
        gray = g

    elif method == GrayscaleMethod.BLUE_CHANNEL:
        gray = b

    else:
        raise ValueError(f"Unknown greyscale method: {method}")

    if is_uint8:
        return np.clip(np.round(gray), 0, 255).astype(np.uint8)
    else:
        return gray.astype(image.dtype)


def _rgb_to_grayscale_pure_python(
    image: List[List[List[Union[int, float]]]],
    method: GrayscaleMethod | str = GrayscaleMethod.REC601,
    gamma: float = 2.2
) -> List[List[Union[int, float]]]:
    """Pure Python fallback for nested lists [height][width][channels]."""
    height = len(image)
    if height == 0:
        return []
    
    result: List[List[Union[int, float]]] = []
    for row in image:
        new_row = []
        for pixel in row:
            r, g, b = pixel[0], pixel[1], pixel[2]
            val = rgb_to_grayscale_pixel(r, g, b, method=method, gamma=gamma)
            if isinstance(r, int):
                val = max(0, min(255, int(round(val))))
            new_row.append(val)
        result.append(new_row)
    return result


def rgb_to_grayscale(
    image: Any,
    method: GrayscaleMethod | str = GrayscaleMethod.REC601,
    gamma: float = 2.2
) -> Any:
    """
    Main conversion entry point supporting both NumPy ndarrays and pure Python lists.
    """
    if HAS_NUMPY and isinstance(image, np.ndarray):
        return _rgb_to_grayscale_numpy(image, method=method, gamma=gamma)
    elif isinstance(image, list):
        return _rgb_to_grayscale_pure_python(image, method=method, gamma=gamma)
    else:
        raise TypeError(f"Unsupported image type: {type(image)}.")


def to_rec601_luminance(image: Any) -> Any:
    return rgb_to_grayscale(image, method=GrayscaleMethod.REC601)


def to_rec709_luminance(image: Any) -> Any:
    return rgb_to_grayscale(image, method=GrayscaleMethod.REC709)


def to_average_grayscale(image: Any) -> Any:
    return rgb_to_grayscale(image, method=GrayscaleMethod.AVERAGE)


def to_lightness_grayscale(image: Any) -> Any:
    return rgb_to_grayscale(image, method=GrayscaleMethod.LIGHTNESS)


def to_gamma_corrected_grayscale(image: Any, gamma: float = 2.2) -> Any:
    return rgb_to_grayscale(image, method=GrayscaleMethod.GAMMA_CORRECTED, gamma=gamma)


def extract_channel(image: Any, channel: str) -> Any:
    ch = channel.lower()
    if ch in ["r", "red"]:
        return rgb_to_grayscale(image, method=GrayscaleMethod.RED_CHANNEL)
    elif ch in ["g", "green"]:
        return rgb_to_grayscale(image, method=GrayscaleMethod.GREEN_CHANNEL)
    elif ch in ["b", "blue"]:
        return rgb_to_grayscale(image, method=GrayscaleMethod.BLUE_CHANNEL)
    else:
        raise ValueError(f"Unknown channel: {channel}.")
