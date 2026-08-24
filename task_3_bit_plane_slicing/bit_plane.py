"""
Bit Plane Slicing & Digital Steganography Algorithms
=====================================================
Rigorous, scientific implementation of 8-bit digital image bit-plane slicing,
selective multi-plane reconstruction, progressive cumulative decoding,
energy contribution analysis, and LSB digital watermarking.
"""

from __future__ import annotations
import math
from typing import List, Tuple, Dict, Union, Any, Optional, Sequence

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# Theoretical energy contribution of each bit in standard 8-bit linear representation
# Bit k has positional weight 2^k out of total sum 255
BIT_WEIGHTS: Tuple[int, ...] = (1, 2, 4, 8, 16, 32, 64, 128)
BIT_ENERGY_PERCENTAGES: Tuple[float, ...] = tuple(
    (2**k / 255.0) * 100.0 for k in range(8)
)


def _validate_bit_index(bit_idx: int) -> None:
    if not (0 <= bit_idx <= 7):
        raise ValueError(f"Bit plane index must be between 0 (LSB) and 7 (MSB), got {bit_idx}")


# =============================================================================
# 1. Individual Bit Plane Extraction
# =============================================================================

def extract_bit_plane(
    image: Any,
    bit_idx: int,
    scale_to_255: bool = True
) -> Any:
    """
    Extracts the k-th bit plane from an 8-bit image.

    Mathematical Definition:
        b_k(x, y) = floor( f(x, y) / 2^k ) mod 2 = (f(x, y) >> k) & 1

    Args:
        image: 2D or 3D image as NumPy ndarray (uint8) or nested Python list.
        bit_idx: Integer index of bit plane (0 = LSB, 7 = MSB).
        scale_to_255: If True, maps binary values {0, 1} to {0, 255} for visual rendering.
                      If False, returns raw boolean / binary values {0, 1}.

    Returns:
        Extracted bit plane with identical spatial dimensions as input.
    """
    _validate_bit_index(bit_idx)

    if HAS_NUMPY and isinstance(image, np.ndarray):
        return _extract_bit_plane_numpy(image, bit_idx, scale_to_255)
    elif isinstance(image, list):
        return _extract_bit_plane_pure_python(image, bit_idx, scale_to_255)
    else:
        raise TypeError(f"Unsupported image type: {type(image)}. Expected numpy.ndarray or list.")


def _extract_bit_plane_numpy(
    image: np.ndarray,
    bit_idx: int,
    scale_to_255: bool
) -> np.ndarray:
    """Vectorized NumPy extraction for single bit plane."""
    img_uint8 = np.clip(np.round(image), 0, 255).astype(np.uint8) if image.dtype != np.uint8 else image
    # Bitwise shift and mask
    bit_plane = (img_uint8 >> bit_idx) & 1
    
    if scale_to_255:
        return (bit_plane * 255).astype(np.uint8)
    return bit_plane.astype(np.uint8)


def _extract_bit_plane_pure_python(
    image: List[Any],
    bit_idx: int,
    scale_to_255: bool
) -> List[Any]:
    """Pure Python extraction fallback."""
    multiplier = 255 if scale_to_255 else 1

    def _process_elem(val: Any) -> Any:
        if isinstance(val, (int, float)):
            int_val = max(0, min(255, int(round(val))))
            return ((int_val >> bit_idx) & 1) * multiplier
        elif isinstance(val, list):
            return [_process_elem(sub) for sub in val]
        else:
            raise TypeError(f"Unexpected pixel element type: {type(val)}")

    return [_process_elem(row) for row in image]


# =============================================================================
# 2. Extract All 8 Bit Planes
# =============================================================================

def extract_all_bit_planes(
    image: Any,
    scale_to_255: bool = True
) -> List[Any]:
    """
    Extracts all 8 bit planes (from Bit 0 / LSB to Bit 7 / MSB).

    Returns:
        List of 8 bit planes: [plane_0, plane_1, ..., plane_7]
    """
    return [extract_bit_plane(image, k, scale_to_255=scale_to_255) for k in range(8)]


# =============================================================================
# 3. Arbitrary Multi-Plane Reconstruction
# =============================================================================

def reconstruct_from_bit_planes(
    bit_planes: Sequence[Any],
    plane_indices: Sequence[int]
) -> Any:
    """
    Reconstructs an image by selectively summing the specified bit planes.

    Mathematical Formulation:
        f_reconstructed(x, y) = sum_{k in plane_indices} ( 2^k * b_k(x, y) )

    Args:
        bit_planes: Sequence of 8 bit planes (indexed 0 to 7). If bit planes were
                    scaled to {0, 255}, they will be normalized back to {0, 1}.
        plane_indices: List or sequence of bit indices to include in reconstruction, e.g. [7, 6, 5, 4].

    Returns:
        Reconstructed uint8 image.
    """
    for idx in plane_indices:
        _validate_bit_index(idx)

    if HAS_NUMPY and isinstance(bit_planes[0], np.ndarray):
        shape = bit_planes[0].shape
        dtype = np.uint8
        reconstructed = np.zeros(shape, dtype=np.int32)

        for k in plane_indices:
            plane = bit_planes[k]
            # Normalize if plane values are in 0..255
            if np.max(plane) > 1:
                binary_plane = (plane > 127).astype(np.int32)
            else:
                binary_plane = plane.astype(np.int32)
            reconstructed += (1 << k) * binary_plane

        return np.clip(reconstructed, 0, 255).astype(dtype)

    elif isinstance(bit_planes[0], list):
        # Pure Python fallback
        height = len(bit_planes[0])
        width = len(bit_planes[0][0])
        is_3d = isinstance(bit_planes[0][0][0], list)

        if is_3d:
            channels = len(bit_planes[0][0][0])
            result = [[[0 for _ in range(channels)] for _ in range(width)] for _ in range(height)]
            for r in range(height):
                for c in range(width):
                    for ch in range(channels):
                        val = 0
                        for k in plane_indices:
                            raw = bit_planes[k][r][c][ch]
                            bin_val = 1 if raw > 127 or raw == 1 else 0
                            val += (1 << k) * bin_val
                        result[r][c][ch] = max(0, min(255, val))
            return result
        else:
            result = [[0 for _ in range(width)] for _ in range(height)]
            for r in range(height):
                for c in range(width):
                    val = 0
                    for k in plane_indices:
                        raw = bit_planes[k][r][c]
                        bin_val = 1 if raw > 127 or raw == 1 else 0
                        val += (1 << k) * bin_val
                    result[r][c] = max(0, min(255, val))
            return result
    else:
        raise TypeError(f"Unsupported bit plane structure type: {type(bit_planes[0])}")


# =============================================================================
# 4. Progressive / Cumulative Reconstruction
# =============================================================================

def reconstruct_cumulative_msb(image: Any) -> List[Tuple[str, Any]]:
    """
    Progressively reconstructs the image starting from the Most Significant Bit (MSB 7)
    down to the Least Significant Bit (LSB 0).

    Returns:
        List of 8 tuples: (label, reconstructed_image), representing:
        - Bits [7]      (1 bit  = 50.2% energy)
        - Bits [7..6]   (2 bits = 75.3% energy)
        - Bits [7..5]   (3 bits = 87.8% energy)
        - Bits [7..4]   (4 bits = 94.1% energy)
        - Bits [7..3]   (5 bits = 97.3% energy)
        - Bits [7..2]   (6 bits = 98.8% energy)
        - Bits [7..1]   (7 bits = 99.6% energy)
        - Bits [7..0]   (8 bits = 100.0% perfect reconstruction)
    """
    raw_planes = extract_all_bit_planes(image, scale_to_255=False)
    results = []

    cumulative_indices: List[int] = []
    for k in range(7, -1, -1):
        cumulative_indices.append(k)
        recon = reconstruct_from_bit_planes(raw_planes, cumulative_indices)
        num_bits = 8 - k
        energy_pct = sum(BIT_ENERGY_PERCENTAGES[i] for i in cumulative_indices)
        label = f"Bits 7..{k} ({num_bits}b - {energy_pct:.1f}%)" if k < 7 else f"Bit 7 Only (1b - {energy_pct:.1f}%)"
        results.append((label, recon))

    return results


# =============================================================================
# 5. Image Fidelity & Bit Contribution Metrics
# =============================================================================

def compute_mse_psnr(original: np.ndarray, reconstructed: np.ndarray) -> Tuple[float, float]:
    """Computes Mean Squared Error (MSE) and Peak Signal-to-Noise Ratio (PSNR in dB)."""
    orig_f = original.astype(np.float64)
    recon_f = reconstructed.astype(np.float64)
    mse = float(np.mean((orig_f - recon_f) ** 2))
    if mse == 0.0:
        return 0.0, float("inf")
    psnr = float(10.0 * np.log10((255.0 ** 2) / mse))
    return round(mse, 2), round(psnr, 2)


def compute_bit_plane_metrics(image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Computes comprehensive empirical and theoretical metrics for all 8 bit planes.
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy is required for computing quantitative metrics.")

    img_uint8 = np.clip(np.round(image), 0, 255).astype(np.uint8)
    raw_planes = extract_all_bit_planes(img_uint8, scale_to_255=False)
    
    metrics = []
    cumulative_indices: List[int] = []

    for k in range(7, -1, -1):
        cumulative_indices.append(k)
        recon = reconstruct_from_bit_planes(raw_planes, cumulative_indices)
        mse, psnr = compute_mse_psnr(img_uint8, recon)

        plane_k = raw_planes[k]
        active_ratio = float(np.mean(plane_k)) * 100.0

        # Bit plane entropy
        p1 = active_ratio / 100.0
        p0 = 1.0 - p1
        entropy = 0.0
        if p0 > 0:
            entropy -= p0 * math.log2(p0)
        if p1 > 0:
            entropy -= p1 * math.log2(p1)

        metrics.append({
            "bit_index": k,
            "bit_name": f"Bit {k}" + (" (MSB)" if k == 7 else " (LSB)" if k == 0 else ""),
            "weight": 1 << k,
            "theoretical_energy_pct": round(BIT_ENERGY_PERCENTAGES[k], 2),
            "cumulative_bits": f"7..{k}",
            "cumulative_energy_pct": round(sum(BIT_ENERGY_PERCENTAGES[i] for i in cumulative_indices), 2),
            "active_pixels_pct": round(active_ratio, 2),
            "entropy": round(entropy, 4),
            "cumulative_mse": mse,
            "cumulative_psnr_db": psnr,
        })

    return metrics


# =============================================================================
# 6. Digital Steganography / LSB Watermarking
# =============================================================================

def embed_watermark_lsb(
    cover_image: np.ndarray,
    watermark_binary: np.ndarray,
    bit_plane: int = 0
) -> np.ndarray:
    """
    Embeds a 2D binary watermark image/pattern into a designated bit plane (typically LSB 0).

    Mathematical Operation:
        stego(x, y) = (cover(x, y) & ~(1 << k)) | ((watermark(x, y) > 0) << k)

    Args:
        cover_image: 2D uint8 grayscale image.
        watermark_binary: 2D binary image (same size as cover, {0, 1} or {0, 255}).
        bit_plane: Bit index to embed into (default 0 for least perceptible alteration).

    Returns:
        Stego image with embedded payload.
    """
    _validate_bit_index(bit_plane)

    cover_uint8 = cover_image.astype(np.uint8)
    wm_binary = (watermark_binary > 127).astype(np.uint8) if np.max(watermark_binary) > 1 else watermark_binary.astype(np.uint8)

    if cover_uint8.shape[:2] != wm_binary.shape[:2]:
        raise ValueError(
            f"Cover shape {cover_uint8.shape[:2]} and Watermark shape {wm_binary.shape[:2]} must match."
        )

    # Clear target bit plane
    mask = ~(1 << bit_plane) & 0xFF
    cleared = cover_uint8 & mask

    # Insert watermark bit
    stego = cleared | (wm_binary << bit_plane)
    return stego.astype(np.uint8)


def extract_watermark_lsb(
    stego_image: np.ndarray,
    bit_plane: int = 0,
    scale_to_255: bool = True
) -> np.ndarray:
    """
    Extracts the binary watermark embedded in the designated bit plane.

    Mathematical Operation:
        extracted(x, y) = (stego(x, y) >> k) & 1

    Args:
        stego_image: Stego image containing the watermark.
        bit_plane: Bit plane index (default 0).
        scale_to_255: If True, scales {0, 1} to {0, 255} for visualization.

    Returns:
        Recovered binary watermark image.
    """
    return extract_bit_plane(stego_image, bit_plane, scale_to_255=scale_to_255)
