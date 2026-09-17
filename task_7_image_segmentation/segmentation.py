"""
Digital Image Segmentation Engine
=================================
Rigorous implementations of primary spatial and feature-space image segmentation techniques:
1. Global Otsu's Variance Maximization Thresholding
2. Adaptive Local Window Thresholding
3. K-Means Color / Intensity Feature Clustering
4. Seeded Region Growing Segmentation
5. Sobel Spatial Gradient Edge-Boundary Extraction
"""

from __future__ import annotations
import math
from typing import List, Tuple, Dict, Any, Optional, Set
from collections import deque

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# =============================================================================
# 1. Otsu's Global Optimum Thresholding
# =============================================================================

def otsu_thresholding(image: np.ndarray) -> Tuple[np.ndarray, int, float]:
    """
    Computes optimal global binarization threshold t* by maximizing inter-class variance:
        sigma_B^2(t) = omega_0(t) * omega_1(t) * (mu_0(t) - mu_1(t))^2

    Returns:
        (binary_mask, optimal_threshold, max_interclass_variance)
    """
    if not HAS_NUMPY:
        raise ImportError("NumPy required.")

    img_gray = np.clip(np.round(image), 0, 255).astype(np.uint8)
    if img_gray.ndim == 3:
        img_gray = np.clip(0.299 * img_gray[:, :, 0] + 0.587 * img_gray[:, :, 1] + 0.114 * img_gray[:, :, 2], 0, 255).astype(np.uint8)

    hist, _ = np.histogram(img_gray.flatten(), bins=256, range=(0, 256))
    total_pixels = img_gray.size

    # Cumulative probabilities and means
    prob = hist.astype(np.float64) / float(total_pixels)
    cum_prob = np.cumsum(prob)
    cum_mean = np.cumsum(prob * np.arange(256))
    global_mean = cum_mean[-1]

    best_thresh = 0
    max_var = -1.0

    for t in range(256):
        w0 = cum_prob[t]
        w1 = 1.0 - w0
        if w0 > 0.0 and w1 > 0.0:
            mu0 = cum_mean[t] / w0
            mu1 = (global_mean - cum_mean[t]) / w1
            var_between = w0 * w1 * ((mu0 - mu1) ** 2)

            if var_between > max_var:
                max_var = var_between
                best_thresh = t

    binary_mask = np.where(img_gray > best_thresh, 255, 0).astype(np.uint8)
    return binary_mask, best_thresh, float(max_var)


# =============================================================================
# 2. Adaptive Local Window Thresholding
# =============================================================================

def adaptive_local_thresholding(
    image: np.ndarray,
    block_size: int = 15,
    c: float = 5.0
) -> np.ndarray:
    """
    Performs spatially varying thresholding using local neighborhood mean:
        T(x, y) = mean_local(x, y) - C
    """
    img_gray = np.clip(np.round(image), 0, 255).astype(np.float64)
    if img_gray.ndim == 3:
        img_gray = 0.299 * img_gray[:, :, 0] + 0.587 * img_gray[:, :, 1] + 0.114 * img_gray[:, :, 2]

    h, w = img_gray.shape
    rad = block_size // 2
    padded = np.pad(img_gray, rad, mode="reflect")

    # Integral image for O(1) box filtering
    integral = np.pad(np.cumsum(np.cumsum(padded, axis=0), axis=1), ((1, 0), (1, 0)), mode="constant")

    output = np.zeros((h, w), dtype=np.uint8)
    area = block_size * block_size

    for y in range(h):
        y0, y1 = y, y + block_size
        for x in range(w):
            x0, x1 = x, x + block_size
            local_sum = integral[y1, x1] - integral[y0, x1] - integral[y1, x0] + integral[y0, x0]
            local_mean = local_sum / area
            output[y, x] = 255 if img_gray[y, x] > (local_mean - c) else 0

    return output


# =============================================================================
# 3. K-Means Feature-Space Color/Intensity Clustering
# =============================================================================

def kmeans_segmentation(
    image: np.ndarray,
    k: int = 4,
    max_iters: int = 20,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Clusters pixel colors/intensities into K disjoint centroid classes.
    """
    np.random.seed(seed)
    is_color = (image.ndim == 3 and image.shape[2] >= 3)
    orig_shape = image.shape

    if is_color:
        pixels = image[:, :, :3].reshape(-1, 3).astype(np.float64)
    else:
        pixels = image.reshape(-1, 1).astype(np.float64)

    n_samples = pixels.shape[0]
    init_indices = np.random.choice(n_samples, size=k, replace=False)
    centroids = pixels[init_indices].copy()

    labels = np.zeros(n_samples, dtype=np.int32)

    for _ in range(max_iters):
        dists = np.linalg.norm(pixels[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
        new_labels = np.argmin(dists, axis=1)

        if np.array_equal(labels, new_labels):
            break
        labels = new_labels

        for cluster_id in range(k):
            members = pixels[labels == cluster_id]
            if len(members) > 0:
                centroids[cluster_id] = np.mean(members, axis=0)

    segmented_flat = centroids[labels]
    if is_color:
        segmented_img = segmented_flat.reshape(orig_shape[0], orig_shape[1], 3)
    else:
        segmented_img = segmented_flat.reshape(orig_shape[0], orig_shape[1])

    return np.clip(np.round(segmented_img), 0, 255).astype(np.uint8), centroids


# =============================================================================
# 4. Seeded Region Growing Segmentation
# =============================================================================

def region_growing_segmentation(
    image: np.ndarray,
    seed_points: Optional[List[Tuple[int, int]]] = None,
    tolerance: float = 30.0
) -> np.ndarray:
    """
    Segments connected regions starting from seed pixels based on intensity similarity predicate:
        |f(x, y) - mu_region| <= tolerance
    """
    img_gray = np.clip(np.round(image), 0, 255).astype(np.float64)
    if img_gray.ndim == 3:
        img_gray = 0.299 * img_gray[:, :, 0] + 0.587 * img_gray[:, :, 1] + 0.114 * img_gray[:, :, 2]

    h, w = img_gray.shape
    visited = np.zeros((h, w), dtype=bool)
    segmented_mask = np.zeros((h, w), dtype=np.uint8)

    if not seed_points:
        seed_points = [(h // 2, w // 2), (h // 4, w // 4), (h // 2, w // 4), (3 * h // 4, w // 2)]

    for seed_y, seed_x in seed_points:
        if seed_y < 0 or seed_y >= h or seed_x < 0 or seed_x >= w:
            continue
        if visited[seed_y, seed_x]:
            continue

        seed_val = img_gray[seed_y, seed_x]
        queue: deque[Tuple[int, int]] = deque([(seed_y, seed_x)])
        visited[seed_y, seed_x] = True
        region_sum = seed_val
        region_count = 1

        while queue:
            cy, cx = queue.popleft()
            segmented_mask[cy, cx] = 255
            current_mean = region_sum / region_count

            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                    val = img_gray[ny, nx]
                    if abs(val - current_mean) <= tolerance:
                        visited[ny, nx] = True
                        region_sum += val
                        region_count += 1
                        queue.append((ny, nx))

    return segmented_mask


# =============================================================================
# 5. Sobel Spatial Gradient Edge-Boundary Extraction
# =============================================================================

def edge_based_segmentation(
    image: np.ndarray,
    threshold: float = 60.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes spatial gradient magnitude using 3x3 Sobel convolution operators:
        G_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        G_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
        M(x, y) = sqrt(G_x^2 + G_y^2)
    """
    img_gray = np.clip(np.round(image), 0, 255).astype(np.float64)
    if img_gray.ndim == 3:
        img_gray = 0.299 * img_gray[:, :, 0] + 0.587 * img_gray[:, :, 1] + 0.114 * img_gray[:, :, 2]

    sobel_x = np.array([[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]], dtype=np.float64)
    sobel_y = np.array([[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]], dtype=np.float64)

    padded = np.pad(img_gray, 1, mode="reflect")
    h, w = img_gray.shape

    gx = np.zeros((h, w), dtype=np.float64)
    gy = np.zeros((h, w), dtype=np.float64)

    for i in range(3):
        for j in range(3):
            sub = padded[i:i + h, j:j + w]
            gx += sobel_x[i, j] * sub
            gy += sobel_y[i, j] * sub

    grad_mag = np.sqrt(gx ** 2 + gy ** 2)
    grad_norm = np.clip(grad_mag / (np.max(grad_mag) if np.max(grad_mag) > 0 else 1.0) * 255.0, 0, 255).astype(np.uint8)
    binary_edges = np.where(grad_norm >= threshold, 255, 0).astype(np.uint8)

    return grad_norm, binary_edges
