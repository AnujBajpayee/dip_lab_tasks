# Task 7: Digital Image Segmentation
**Author**: Anuj Bajpayee ([anujbajpayee14@gmail.com](mailto:anujbajpayee14@gmail.com))

## 📖 Overview

Image segmentation partitions a digital image into multiple disjoint, visually meaningful, and homogeneous regions with respect to intensity, color, texture, or spatial gradient boundaries.

This module implements and benchmarks 5 fundamental segmentation paradigms:
1. **Global Otsu's Variance Maximization Thresholding**
2. **Adaptive Local Window Thresholding**
3. **K-Means Feature-Space Color/Intensity Clustering**
4. **Seeded Region Growing Segmentation**
5. **Sobel Spatial Gradient Edge-Boundary Extraction**

---

## 🖼️ Visual Demonstration & Benchmark on IIIT Nagpur Logo

Comparison grid displaying original input, global binarization, adaptive local thresholding, $K=4$ color clustering, seeded region growing, and Sobel edge boundaries:

![Digital Image Segmentation Benchmark on IIITN Logo](outputs/iiitn_logo_comparison_grid.png)

---

## 📐 1. Mathematical Foundations & Formulations

### 1. Otsu's Inter-Class Variance Maximization
Finds the global threshold $t^*$ that maximizes between-class variance between background ($\omega_0$) and foreground ($\omega_1$):

$$\sigma_B^2(t) = \omega_0(t) \cdot \omega_1(t) \cdot \left( \mu_0(t) - \mu_1(t) \right)^2$$

$$t^* = \arg\max_{0 \le t < 256} \sigma_B^2(t)$$

### 2. Adaptive Local Window Thresholding
Calculates spatially varying thresholds over local $W \times W$ window neighborhoods to handle non-uniform illumination:

$$T(x, y) = \mu_{\text{local}}(x, y) - C = \left( \frac{1}{W^2} \sum_{i, j \in W} f(x+i, y+j) \right) - C$$

### 3. K-Means Feature-Space Clustering
Minimizes total within-cluster Euclidean sum-of-squares in RGB/intensity feature space:

$$J = \sum_{k=1}^{K} \sum_{x_i \in C_k} \| x_i - \mu_k \|^2$$

### 4. Seeded Region Growing
Iteratively merges 4-connected / 8-connected neighboring pixels satisfying the homogeneity predicate:

$$\text{Predicate: } | f(x, y) - \mu_{\text{region}} | \le T_{\text{tolerance}}$$

### 5. Sobel Spatial Gradient Edge Extraction
Computes first-order spatial derivative vectors using separable $3 \times 3$ convolution kernels:

$$G_x = \begin{bmatrix} -1 & 0 & +1 \\ -2 & 0 & +2 \\ -1 & 0 & +1 \end{bmatrix} * f, \quad G_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ +1 & +2 & +1 \end{bmatrix} * f$$

$$M(x, y) = \sqrt{G_x^2 + G_y^2} \ge T_{\text{edge}}$$

---

## 📊 2. Algorithmic Comparison & Taxonomy

| Segmentation Technique | Input Domain | Key Advantage | Typical Use Case |
| :--- | :--- | :--- | :--- |
| **Otsu Global Thresholding** | 1D Intensity Histogram | Fully automatic, non-parametric, optimal for bimodal distributions. | Document scanning, background isolation. |
| **Adaptive Local Window** | 2D Spatial Neighborhood | Robust against severe shadows and non-uniform lighting gradients. | Unevenly lit microscopy, outdoor scenes. |
| **K-Means Feature Clustering** | 3D Color Vector Space | Natural grouping into $K$ perceptual color segments without spatial bias. | Satellite land-cover, object classification. |
| **Seeded Region Growing** | Spatial Connectivity + Intensity | Guaranteed spatially connected and contiguous object segments. | Medical lesion extraction, organ isolation. |
| **Sobel Edge Boundary** | 2D Spatial Derivatives | Preserves fine structural contours, geometric boundaries, and corners. | Shape analysis, boundary detection. |

---

## 💻 3. Code Structure & CLI Execution

### Files in this Module:
- [`segmentation.py`](segmentation.py): Otsu, Adaptive, K-Means, Region Growing, and Sobel algorithms.
- [`visualizer.py`](visualizer.py): 6-panel composite comparison grid generator.
- [`main.py`](main.py): Standalone CLI runner with parameter logging.
- [`test_segmentation.py`](test_segmentation.py): Pytest unit test suite.
- [`outputs/`](outputs/): Generated visual benchmarks and comparison grids.

### Running via CLI:

```bash
# Run all segmentation methods on the IIIT Nagpur logo
python task_7_image_segmentation/main.py

# Run on custom user image
python task_7_image_segmentation/main.py --input path/to/image.png
```

### Running Unit Tests:
```bash
pytest task_7_image_segmentation/test_segmentation.py -v
```

---

## 📜 License
This task is part of `dip_lab_tasks` licensed under the **MIT License**.
