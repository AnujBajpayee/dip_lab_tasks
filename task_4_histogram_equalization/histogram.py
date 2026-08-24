"""
Histogram Equalization Algorithms & Image Enhancement Suite
============================================================
Implementations of standard and advanced Histogram Equalization methods:
1. Global Histogram Equalization (GHE)
2. Brightness Preserving Bi-Histogram Equalization (BBHE)
3. Contrast Limited Adaptive Histogram Equalization (CLAHE)
4. Histogram Matching / Specification (HM)
5. Color-Preserving Equalization (HSV Luminance Channel)
"""

from __future__ import annotations
import math
from typing import List, Tuple, Dict, Union, Any, Optional, Sequence

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# =============================================================================
# 1. Basic Histogram & CDF Utilities
# =============================================================================

def compute_histogram(image: Any, bins: int = 256) -> Any:
    """Computes the 1D intensity histogram of an image."""
    if HAS_NUMPY and isinstance(image, np.ndarray):
        img_uint8 = np.clip(np.round(image), 0, 255).astype(np.uint8)
        hist, _ = np.histogram(img_uint8.flatten(), bins=bins, range=(0, bins))
        return hist.astype(np.int64)
    elif isinstance(image, list):
        hist = [0] * bins
        def _accum(elem: Any) -> None:
            if isinstance(elem, (int, float)):
                v = max(0, min(bins - 1, int(round(elem))))
                hist[v] += 1
            elif isinstance(elem, list):
                for sub in elem:
                    _accum(sub)
        _accum(image)
        return hist
    else:
        raise TypeError(f"Unsupported image type: {type(image)}")


def compute_cdf(hist: Sequence[int | float]) -> Any:
    """Computes the cumulative distribution function (CDF) of a histogram."""
    if HAS_NUMPY and isinstance(hist, np.ndarray):
        return np.cumsum(hist).astype(np.float64)
    else:
        cdf = []
        acc = 0.0
        for val in hist:
            acc += float(val)
            cdf.append(acc)
        return cdf


# =============================================================================
# 2. Global Histogram Equalization (GHE)
# =============================================================================

def global_histogram_equalization(image: Any) -> Any:
    """
    Standard Global Histogram Equalization (GHE).

    Mathematical Formulation:
        s_k = round( ( (CDF(r_k) - CDF_min) / ((M * N) - CDF_min) ) * 255 )
    """
    if HAS_NUMPY and isinstance(image, np.ndarray):
        img_uint8 = np.clip(np.round(image), 0, 255).astype(np.uint8)
        if img_uint8.ndim == 3 and img_uint8.shape[2] >= 3:
            return color_histogram_equalization(img_uint8, method="ghe")

        hist, _ = np.histogram(img_uint8.flatten(), bins=256, range=(0, 256))
        cdf = np.cumsum(hist).astype(np.float64)

        # Mask out zero CDF values to find minimum non-zero CDF
        cdf_masked = np.ma.masked_equal(cdf, 0)
        cdf_min = cdf_masked.min() if cdf_masked.count() > 0 else 0
        total_pixels = img_uint8.size

        if total_pixels == cdf_min:
            return img_uint8.copy()

        # Normalized lookup table [0, 255]
        lut = np.zeros(256, dtype=np.uint8)
        mask = cdf > 0
        if total_pixels > cdf_min:
            lut_vals = (cdf[mask] - cdf_min) / (total_pixels - cdf_min) * 255.0
            lut[mask] = np.clip(np.round(lut_vals), 0, 255).astype(np.uint8)

        return lut[img_uint8]

    elif isinstance(image, list):
        hist = compute_histogram(image, bins=256)
        cdf = compute_cdf(hist)
        total_pixels = cdf[-1] if len(cdf) > 0 else 1
        non_zero_cdfs = [v for v in cdf if v > 0]
        cdf_min = non_zero_cdfs[0] if len(non_zero_cdfs) > 0 else 0

        lut = [0] * 256
        for k in range(256):
            if cdf[k] > 0 and total_pixels > cdf_min:
                lut[k] = max(0, min(255, int(round(((cdf[k] - cdf_min) / (total_pixels - cdf_min)) * 255.0))))

        def _map_elem(elem: Any) -> Any:
            if isinstance(elem, (int, float)):
                v = max(0, min(255, int(round(elem))))
                return lut[v]
            elif isinstance(elem, list):
                return [_map_elem(sub) for sub in elem]
            return elem

        return _map_elem(image)
    else:
        raise TypeError(f"Unsupported image type: {type(image)}")


# =============================================================================
# 3. Brightness Preserving Bi-Histogram Equalization (BBHE)
# =============================================================================

def bi_histogram_equalization(image: Any) -> Any:
    """
    Brightness Preserving Bi-Histogram Equalization (BBHE).
    Partitions the histogram into two sub-histograms around the mean intensity (mu),
    equalizing each sub-histogram independently to maintain natural image brightness.

    Mathematical Formulation:
        mu = round( mean(f) )
        Lower Sub-Histogram H_L: [0, mu]        -> Equalized across [0, mu]
        Upper Sub-Histogram H_U: [mu + 1, 255]  -> Equalized across [mu + 1, 255]
    """
    if HAS_NUMPY and isinstance(image, np.ndarray):
        img_uint8 = np.clip(np.round(image), 0, 255).astype(np.uint8)
        if img_uint8.ndim == 3 and img_uint8.shape[2] >= 3:
            return color_histogram_equalization(img_uint8, method="bbhe")

        mu = int(round(float(np.mean(img_uint8))))
        mu = max(1, min(254, mu))

        hist, _ = np.histogram(img_uint8.flatten(), bins=256, range=(0, 256))
        hist_l = hist[:mu + 1]
        hist_u = hist[mu + 1:]

        cdf_l = np.cumsum(hist_l).astype(np.float64)
        cdf_u = np.cumsum(hist_u).astype(np.float64)

        n_l = cdf_l[-1] if len(cdf_l) > 0 and cdf_l[-1] > 0 else 1.0
        n_u = cdf_u[-1] if len(cdf_u) > 0 and cdf_u[-1] > 0 else 1.0

        cdf_l_min = np.min(cdf_l[cdf_l > 0]) if np.any(cdf_l > 0) else 0.0
        cdf_u_min = np.min(cdf_u[cdf_u > 0]) if np.any(cdf_u > 0) else 0.0

        lut = np.zeros(256, dtype=np.uint8)

        # Map lower partition [0, mu]
        for k in range(0, mu + 1):
            if cdf_l[k] > 0 and n_l > cdf_l_min:
                val = mu * ((cdf_l[k] - cdf_l_min) / (n_l - cdf_l_min))
                lut[k] = max(0, min(mu, int(round(val))))
            else:
                lut[k] = 0

        # Map upper partition [mu + 1, 255]
        for k in range(mu + 1, 256):
            u_idx = k - (mu + 1)
            if cdf_u[u_idx] > 0 and n_u > cdf_u_min:
                val = (mu + 1) + (255 - (mu + 1)) * ((cdf_u[u_idx] - cdf_u_min) / (n_u - cdf_u_min))
                lut[k] = max(mu + 1, min(255, int(round(val))))
            else:
                lut[k] = mu + 1

        return lut[img_uint8]

    elif isinstance(image, list):
        # Pure python fallback
        hist = compute_histogram(image, bins=256)
        total_sum = sum(k * hist[k] for k in range(256))
        total_pixels = sum(hist)
        mu = int(round(total_sum / max(1, total_pixels)))
        mu = max(1, min(254, mu))

        hist_l = hist[:mu + 1]
        hist_u = hist[mu + 1:]

        cdf_l = compute_cdf(hist_l)
        cdf_u = compute_cdf(hist_u)

        n_l = cdf_l[-1] if len(cdf_l) > 0 and cdf_l[-1] > 0 else 1.0
        n_u = cdf_u[-1] if len(cdf_u) > 0 and cdf_u[-1] > 0 else 1.0

        non_zero_l = [v for v in cdf_l if v > 0]
        non_zero_u = [v for v in cdf_u if v > 0]
        cdf_l_min = non_zero_l[0] if len(non_zero_l) > 0 else 0.0
        cdf_u_min = non_zero_u[0] if len(non_zero_u) > 0 else 0.0

        lut = [0] * 256
        for k in range(0, mu + 1):
            if cdf_l[k] > 0 and n_l > cdf_l_min:
                lut[k] = max(0, min(mu, int(round(mu * ((cdf_l[k] - cdf_l_min) / (n_l - cdf_l_min))))))
            else:
                lut[k] = 0

        for k in range(mu + 1, 256):
            u_idx = k - (mu + 1)
            if cdf_u[u_idx] > 0 and n_u > cdf_u_min:
                lut[k] = max(mu + 1, min(255, int(round((mu + 1) + (255 - (mu + 1)) * ((cdf_u[u_idx] - cdf_u_min) / (n_u - cdf_u_min))))))
            else:
                lut[k] = mu + 1

        def _map_elem(elem: Any) -> Any:
            if isinstance(elem, (int, float)):
                v = max(0, min(255, int(round(elem))))
                return lut[v]
            elif isinstance(elem, list):
                return [_map_elem(sub) for sub in elem]
            return elem

        return _map_elem(image)
    else:
        raise TypeError(f"Unsupported image type: {type(image)}")


# =============================================================================
# 4. Contrast Limited Adaptive Histogram Equalization (CLAHE)
# =============================================================================

def _compute_tile_lut(
    tile: np.ndarray,
    clip_limit: float = 2.0
) -> np.ndarray:
    """Computes the clipped and redistributed CDF lookup table for a single tile."""
    hist, _ = np.histogram(tile.flatten(), bins=256, range=(0, 256))
    tile_size = tile.size

    # Calculate clip threshold
    clip_val = max(1, int(round(clip_limit * (tile_size / 256.0))))
    excess = np.sum(np.maximum(hist - clip_val, 0))
    hist_clipped = np.minimum(hist, clip_val)

    # Uniform redistribution of excess pixels
    bonus = excess // 256
    rem = excess % 256
    hist_clipped += bonus
    if rem > 0:
        step = max(1, 256 // rem)
        hist_clipped[:rem * step:step] += 1

    # CDF Calculation
    cdf = np.cumsum(hist_clipped).astype(np.float64)
    total = cdf[-1] if cdf[-1] > 0 else 1.0
    cdf_min = np.min(cdf[cdf > 0]) if np.any(cdf > 0) else 0.0

    lut = np.zeros(256, dtype=np.uint8)
    mask = cdf > 0
    if total > cdf_min:
        lut_vals = (cdf[mask] - cdf_min) / (total - cdf_min) * 255.0
        lut[mask] = np.clip(np.round(lut_vals), 0, 255).astype(np.uint8)
    else:
        lut[mask] = np.clip(np.round(cdf[mask] / total * 255.0), 0, 255).astype(np.uint8)

    return lut


def clahe(
    image: Any,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8)
) -> Any:
    """
    Contrast Limited Adaptive Histogram Equalization (CLAHE).
    Divides the image into grid tiles, clips histogram to prevent noise over-amplification,
    redistributes clipped pixels uniformly, and applies bilinear interpolation between tiles.
    """
    if not HAS_NUMPY:
        return bi_histogram_equalization(image)

    img_uint8 = np.clip(np.round(np.array(image)), 0, 255).astype(np.uint8)
    if img_uint8.ndim == 3 and img_uint8.shape[2] >= 3:
        return color_histogram_equalization(img_uint8, method="clahe", clip_limit=clip_limit, tile_grid_size=tile_grid_size)

    h, w = img_uint8.shape[:2]
    n_tiles_y, n_tiles_x = tile_grid_size
    n_tiles_y = max(1, min(h, n_tiles_y))
    n_tiles_x = max(1, min(w, n_tiles_x))

    tile_h = h / n_tiles_y
    tile_w = w / n_tiles_x

    # 1. Compute LUT for each tile
    tile_luts = np.zeros((n_tiles_y, n_tiles_x, 256), dtype=np.uint8)
    for ty in range(n_tiles_y):
        y0 = int(round(ty * tile_h))
        y1 = int(round((ty + 1) * tile_h))
        for tx in range(n_tiles_x):
            x0 = int(round(tx * tile_w))
            x1 = int(round((tx + 1) * tile_w))
            tile = img_uint8[y0:y1, x0:x1]
            if tile.size > 0:
                tile_luts[ty, tx] = _compute_tile_lut(tile, clip_limit)
            else:
                tile_luts[ty, tx] = np.arange(256, dtype=np.uint8)

    # 2. Bilinear interpolation across tile centers
    output = np.zeros((h, w), dtype=np.uint8)
    for y in range(h):
        ty = (y / tile_h) - 0.5
        y1 = int(math.floor(ty))
        y2 = y1 + 1
        ay = ty - y1

        y1 = max(0, min(n_tiles_y - 1, y1))
        y2 = max(0, min(n_tiles_y - 1, y2))

        for x in range(w):
            tx = (x / tile_w) - 0.5
            x1 = int(math.floor(tx))
            x2 = x1 + 1
            ax = tx - x1

            x1 = max(0, min(n_tiles_x - 1, x1))
            x2 = max(0, min(n_tiles_x - 1, x2))

            val = img_uint8[y, x]

            v11 = float(tile_luts[y1, x1, val])
            v12 = float(tile_luts[y1, x2, val])
            v21 = float(tile_luts[y2, x1, val])
            v22 = float(tile_luts[y2, x2, val])

            top = v11 * (1.0 - ax) + v12 * ax
            bot = v21 * (1.0 - ax) + v22 * ax
            interp_val = top * (1.0 - ay) + bot * ay

            output[y, x] = max(0, min(255, int(round(interp_val))))

    return output


# =============================================================================
# 5. Histogram Matching / Specification (HM)
# =============================================================================

def histogram_matching(
    source_image: np.ndarray,
    reference_image_or_cdf: np.ndarray
) -> np.ndarray:
    """Transforms source image histogram to match reference distribution."""
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for histogram matching.")

    src_uint8 = np.clip(np.round(source_image), 0, 255).astype(np.uint8)

    # Source CDF
    src_hist, _ = np.histogram(src_uint8.flatten(), bins=256, range=(0, 256))
    src_cdf = np.cumsum(src_hist).astype(np.float64)
    src_cdf /= src_cdf[-1] if src_cdf[-1] > 0 else 1.0

    # Reference CDF
    if reference_image_or_cdf.ndim == 1 and len(reference_image_or_cdf) == 256:
        ref_cdf = reference_image_or_cdf.astype(np.float64)
        ref_cdf /= ref_cdf[-1] if ref_cdf[-1] > 0 else 1.0
    else:
        ref_uint8 = np.clip(np.round(reference_image_or_cdf), 0, 255).astype(np.uint8)
        ref_hist, _ = np.histogram(ref_uint8.flatten(), bins=256, range=(0, 256))
        ref_cdf = np.cumsum(ref_hist).astype(np.float64)
        ref_cdf /= ref_cdf[-1] if ref_cdf[-1] > 0 else 1.0

    lut = np.zeros(256, dtype=np.uint8)
    for src_val in range(256):
        target_val = np.argmin(np.abs(src_cdf[src_val] - ref_cdf))
        lut[src_val] = target_val

    return lut[src_uint8]


# =============================================================================
# 6. Color-Preserving Histogram Equalization (HSV Luminance)
# =============================================================================

def color_histogram_equalization(
    rgb_image: np.ndarray,
    method: str = "clahe",
    **kwargs: Any
) -> np.ndarray:
    """Applies histogram equalization strictly to Value/Luminance channel in HSV color space."""
    if not HAS_NUMPY:
        raise ImportError("NumPy is required.")

    img_rgb = np.clip(np.round(rgb_image), 0, 255).astype(np.float64)
    r = img_rgb[:, :, 0]
    g = img_rgb[:, :, 1]
    b = img_rgb[:, :, 2]

    v = np.max(img_rgb, axis=-1)
    v_uint8 = np.clip(np.round(v), 0, 255).astype(np.uint8)

    method_clean = method.lower()
    if method_clean == "ghe":
        v_eq = global_histogram_equalization(v_uint8)
    elif method_clean == "bbhe":
        v_eq = bi_histogram_equalization(v_uint8)
    elif method_clean == "clahe":
        v_eq = clahe(v_uint8, **kwargs)
    else:
        v_eq = clahe(v_uint8)

    scale = np.zeros_like(v, dtype=np.float64)
    mask = v > 0
    scale[mask] = v_eq[mask].astype(np.float64) / v[mask]

    out_rgb = np.zeros_like(img_rgb, dtype=np.uint8)
    out_rgb[:, :, 0] = np.clip(np.round(r * scale), 0, 255).astype(np.uint8)
    out_rgb[:, :, 1] = np.clip(np.round(g * scale), 0, 255).astype(np.uint8)
    out_rgb[:, :, 2] = np.clip(np.round(b * scale), 0, 255).astype(np.uint8)

    return out_rgb
