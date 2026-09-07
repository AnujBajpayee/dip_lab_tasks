"""
2D Discrete Wavelet Transform (DWT & IDWT) Engine
=================================================
Rigorous, self-contained implementation of 2D Discrete Wavelet Transforms,
multi-level subband decomposition (LL, LH, HL, HH), exact inverse reconstruction,
subband energy distribution analysis, and wavelet coefficient thresholding.
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
# 1. Wavelet Filter Banks
# =============================================================================

SQRT2 = math.sqrt(2.0)
SQRT3 = math.sqrt(3.0)

def get_wavelet_filters(wavelet: str = "haar") -> Tuple[np.ndarray, np.ndarray]:
    """Returns low-pass (h0) and high-pass (h1) analysis filter coefficients."""
    w_key = wavelet.lower()
    if w_key in ("haar", "db1"):
        h0 = np.array([1.0 / SQRT2, 1.0 / SQRT2], dtype=np.float64)
        h1 = np.array([1.0 / SQRT2, -1.0 / SQRT2], dtype=np.float64)
    elif w_key == "db2":
        # Daubechies 4-tap orthogonal filter
        h0 = np.array([
            (1.0 + SQRT3) / (4.0 * SQRT2),
            (3.0 + SQRT3) / (4.0 * SQRT2),
            (3.0 - SQRT3) / (4.0 * SQRT2),
            (1.0 - SQRT3) / (4.0 * SQRT2),
        ], dtype=np.float64)
        h1 = np.array([h0[3], -h0[2], h0[1], -h0[0]], dtype=np.float64)
    else:
        # Default fallback to Haar
        h0 = np.array([1.0 / SQRT2, 1.0 / SQRT2], dtype=np.float64)
        h1 = np.array([1.0 / SQRT2, -1.0 / SQRT2], dtype=np.float64)

    return h0, h1


# =============================================================================
# 2. 1D Periodic Mallat Matrix Transforms
# =============================================================================

def _dwt1d_axis(arr: np.ndarray, h0: np.ndarray, h1: np.ndarray, axis: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """Applies 1D forward DWT with periodic circular boundary extension along specified axis."""
    n = arr.shape[axis]
    k = n // 2
    l_filt = len(h0)

    if axis == 1:
        # Along rows
        approx = np.zeros((arr.shape[0], k), dtype=np.float64)
        detail = np.zeros((arr.shape[0], k), dtype=np.float64)
        for i in range(k):
            for m in range(l_filt):
                idx = (2 * i + m) % n
                approx[:, i] += h0[m] * arr[:, idx]
                detail[:, i] += h1[m] * arr[:, idx]
    else:
        # Along columns
        approx = np.zeros((k, arr.shape[1]), dtype=np.float64)
        detail = np.zeros((k, arr.shape[1]), dtype=np.float64)
        for i in range(k):
            for m in range(l_filt):
                idx = (2 * i + m) % n
                approx[i, :] += h0[m] * arr[idx, :]
                detail[i, :] += h1[m] * arr[idx, :]

    return approx, detail


def _idwt1d_axis(
    approx: np.ndarray,
    detail: np.ndarray,
    h0: np.ndarray,
    h1: np.ndarray,
    axis: int = 0,
    target_len: Optional[int] = None
) -> np.ndarray:
    """Applies 1D inverse DWT synthesis with orthogonal reconstruction along specified axis."""
    l_filt = len(h0)
    if axis == 1:
        k = approx.shape[1]
        n = target_len if target_len is not None else k * 2
        res = np.zeros((approx.shape[0], n), dtype=np.float64)
        for i in range(k):
            for m in range(l_filt):
                idx = (2 * i + m) % n
                res[:, idx] += approx[:, i] * h0[m] + detail[:, i] * h1[m]
    else:
        k = approx.shape[0]
        n = target_len if target_len is not None else k * 2
        res = np.zeros((n, approx.shape[1]), dtype=np.float64)
        for i in range(k):
            for m in range(l_filt):
                idx = (2 * i + m) % n
                res[idx, :] += approx[i, :] * h0[m] + detail[i, :] * h1[m]

    return res


# =============================================================================
# 3. 2D Single-Level Forward DWT (LL, LH, HL, HH)
# =============================================================================

def dwt2(
    image: np.ndarray,
    wavelet: str = "haar"
) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Computes single-level 2D Discrete Wavelet Transform.

    Mathematical Representation:
        LL (Approximation): Low-pass row, Low-pass col  (Coarse structural content)
        LH (Horizontal):    Low-pass row, High-pass col (Horizontal edges)
        HL (Vertical):      High-pass row, Low-pass col (Vertical edges)
        HH (Diagonal):      High-pass row, High-pass col (Diagonal textures / corners)

    Returns:
        (LL, (LH, HL, HH))
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for DWT computation.")

    img_f = image.astype(np.float64)
    if img_f.ndim != 2:
        raise ValueError(f"Expected 2D grayscale image, got shape {img_f.shape}")

    h, w = img_f.shape
    # Ensure even dimensions
    pad_h = (h % 2)
    pad_w = (w % 2)
    if pad_h > 0 or pad_w > 0:
        img_f = np.pad(img_f, ((0, pad_h), (0, pad_w)), mode="edge")

    h0, h1 = get_wavelet_filters(wavelet)

    # Step 1: 1D DWT along rows (horizontal filtering)
    l_row, h_row = _dwt1d_axis(img_f, h0, h1, axis=1)

    # Step 2: 1D DWT along columns (vertical filtering)
    ll, lh = _dwt1d_axis(l_row, h0, h1, axis=0)
    hl, hh = _dwt1d_axis(h_row, h0, h1, axis=0)

    return ll, (lh, hl, hh)


# =============================================================================
# 4. 2D Single-Level Inverse DWT (IDWT)
# =============================================================================

def idwt2(
    coeffs: Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]],
    wavelet: str = "haar",
    target_shape: Optional[Tuple[int, int]] = None
) -> np.ndarray:
    """
    Computes single-level 2D Inverse Discrete Wavelet Transform.
    Exact lossless mathematical reconstruction: f = IDWT(LL, LH, HL, HH).
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for IDWT computation.")

    ll, (lh, hl, hh) = coeffs
    h0, h1 = get_wavelet_filters(wavelet)

    h_target = target_shape[0] if target_shape else ll.shape[0] * 2
    w_target = target_shape[1] if target_shape else ll.shape[1] * 2

    # Step 1: Invert columns
    l_row = _idwt1d_axis(ll, lh, h0, h1, axis=0, target_len=h_target)
    h_row = _idwt1d_axis(hl, hh, h0, h1, axis=0, target_len=h_target)

    # Step 2: Invert rows
    reconstructed = _idwt1d_axis(l_row, h_row, h0, h1, axis=1, target_len=w_target)

    if target_shape:
        return reconstructed[:target_shape[0], :target_shape[1]]
    return reconstructed


# =============================================================================
# 5. Multi-Level 2D Discrete Wavelet Transform
# =============================================================================

def wavedec2(
    image: np.ndarray,
    wavelet: str = "haar",
    level: int = 2
) -> List[Any]:
    """
    Computes multi-level 2D Discrete Wavelet Transform.

    Returns hierarchical coefficient list:
        [LL_level, (LH_level, HL_level, HH_level), ..., (LH_1, HL_1, HH_1)]
    """
    if level < 1:
        raise ValueError(f"Decomposition level must be >= 1, got {level}")

    current_approx = image.astype(np.float64)
    coeffs_list = []

    for l in range(level):
        ll, (lh, hl, hh) = dwt2(current_approx, wavelet=wavelet)
        coeffs_list.append((lh, hl, hh))
        current_approx = ll

    return [current_approx] + coeffs_list[::-1]


def waverec2(
    coeffs: List[Any],
    wavelet: str = "haar",
    original_shape: Optional[Tuple[int, int]] = None
) -> np.ndarray:
    """Reconstructs image from multi-level wavelet coefficients."""
    ll = coeffs[0]
    detail_levels = coeffs[1:]

    current_approx = ll
    for details in detail_levels:
        current_approx = idwt2((current_approx, details), wavelet=wavelet)

    if original_shape:
        return current_approx[:original_shape[0], :original_shape[1]]
    return current_approx


# =============================================================================
# 6. Subband Energy Analysis & Metrics
# =============================================================================

def compute_wavelet_energy(
    coeffs: Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]]
) -> Dict[str, Dict[str, float]]:
    """Computes energy metrics for all 4 subbands: E(S) = sum |S(x,y)|^2."""
    ll, (lh, hl, hh) = coeffs
    e_ll = float(np.sum(ll ** 2))
    e_lh = float(np.sum(lh ** 2))
    e_hl = float(np.sum(hl ** 2))
    e_hh = float(np.sum(hh ** 2))
    total_e = e_ll + e_lh + e_hl + e_hh
    total_e = total_e if total_e > 0 else 1.0

    return {
        "LL": {
            "name": "LL (Approximation)",
            "energy": e_ll,
            "energy_pct": round((e_ll / total_e) * 100.0, 2),
            "mean": round(float(np.mean(ll)), 2),
            "std": round(float(np.std(ll)), 2),
            "role": "Coarse Geometry & Low-Frequency Structural Content (>90% Energy)"
        },
        "LH": {
            "name": "LH (Horizontal Details)",
            "energy": e_lh,
            "energy_pct": round((e_lh / total_e) * 100.0, 2),
            "mean": round(float(np.mean(lh)), 2),
            "std": round(float(np.std(lh)), 2),
            "role": "Horizontal Edges & Row Discontinuities"
        },
        "HL": {
            "name": "HL (Vertical Details)",
            "energy": e_hl,
            "energy_pct": round((e_hl / total_e) * 100.0, 2),
            "mean": round(float(np.mean(hl)), 2),
            "std": round(float(np.std(hl)), 2),
            "role": "Vertical Edges & Column Discontinuities"
        },
        "HH": {
            "name": "HH (Diagonal Details)",
            "energy": e_hh,
            "energy_pct": round((e_hh / total_e) * 100.0, 2),
            "mean": round(float(np.mean(hh)), 2),
            "std": round(float(np.std(hh)), 2),
            "role": "Diagonal Textures, High-Frequency Corners & Noise"
        },
    }


# =============================================================================
# 7. Wavelet Thresholding & Compression
# =============================================================================

def threshold_wavelet_coefficients(
    coeffs: Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]],
    keep_fraction: float = 0.10,
    mode: str = "hard"
) -> Tuple[Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]], float]:
    """Zeros out the lowest amplitude detail coefficients to achieve compression/denoising."""
    ll, (lh, hl, hh) = coeffs

    all_details = np.concatenate([lh.flatten(), hl.flatten(), hh.flatten()])
    abs_details = np.abs(all_details)

    cutoff_percentile = (1.0 - keep_fraction) * 100.0
    thresh_val = float(np.percentile(abs_details, cutoff_percentile))

    def _apply_thresh(band: np.ndarray) -> np.ndarray:
        if mode == "hard":
            return np.where(np.abs(band) >= thresh_val, band, 0.0)
        else:
            return np.sign(band) * np.maximum(np.abs(band) - thresh_val, 0.0)

    th_lh = _apply_thresh(lh)
    th_hl = _apply_thresh(hl)
    th_hh = _apply_thresh(hh)

    return (ll.copy(), (th_lh, th_hl, th_hh)), thresh_val
