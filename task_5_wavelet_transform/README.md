# Task 5: 2D Discrete Wavelet Transform (DWT & IDWT)
**Author**: Anuj Bajpayee ([anujbajpayee14@gmail.com](mailto:anujbajpayee14@gmail.com))

## 📖 Overview
Performs 2D Discrete Wavelet Transform (2D DWT) and Inverse DWT (IDWT) to decompose images into an approximation subband ($LL$) and directional high-frequency detail subbands ($LH, HL, HH$) for multi-resolution analysis and compression.

---

## 🖼️ Visual Benchmarks on IIIT Nagpur Logo

### 1. 4-Subband Decomposition Grid

![IIIT Nagpur Logo Subband Grid](outputs/iiitn_logo_subband_grid.png)

---

### 2. Wavelet Sparsity & Compression Benchmark

![IIIT Nagpur Logo Compression Grid](outputs/iiitn_logo_compression_grid.png)

---

## 📐 1. Mathematical Formulation & Mallat Decomposition

For an image $f(x, y)$, 2D DWT applies low-pass filter $h_0$ and high-pass filter $h_1$ along rows and columns followed by dyadic downsampling ($\downarrow 2$):

$$LL(x, y) = \sum_{m, n} h_0[m] h_0[n] f(2x + m, 2y + n) \quad \text{(Approximation)}$$

$$LH(x, y) = \sum_{m, n} h_0[m] h_1[n] f(2x + m, 2y + n) \quad \text{(Horizontal Edges)}$$

$$HL(x, y) = \sum_{m, n} h_1[m] h_0[n] f(2x + m, 2y + n) \quad \text{(Vertical Edges)}$$

$$HH(x, y) = \sum_{m, n} h_1[m] h_1[n] f(2x + m, 2y + n) \quad \text{(Diagonal Details)}$$

---

## 📊 2. Subband Energy Distribution (Parseval's Relation)

$$E_{\text{total}} = \sum_{x, y} |f(x, y)|^2 = E(LL) + E(LH) + E(HL) + E(HH)$$

| Subband | Operator | Energy % | Structural Role |
| :---: | :--- | :---: | :--- |
| **$LL$** | Low-pass $\ast$ Low-pass ($\downarrow 2$) | **$> 96.0\%$** | Coarse image approximation and global morphology. |
| **$LH$** | Low-pass $\ast$ High-pass ($\downarrow 2$) | **$1.0\% - 2.5\%$** | Horizontal high-frequency edges and row transitions. |
| **$HL$** | High-pass $\ast$ Low-pass ($\downarrow 2$) | **$1.0\% - 2.5\%$** | Vertical high-frequency edges and column transitions. |
| **$HH$** | High-pass $\ast$ High-pass ($\downarrow 2$) | **$< 0.5\%$** | Diagonal textures, sharp corners, and high-frequency noise. |

---

## 💻 3. CLI Execution & Testing

```bash
# Run 2D DWT and IDWT compression benchmarks on IIIT Nagpur logo
python task_5_wavelet_transform/main.py

# Transform a custom user image
python task_5_wavelet_transform/main.py --input path/to/image.png --wavelet haar --level 2

# Run unit tests
pytest task_5_wavelet_transform/test_wavelet.py -v
```

---

## 📜 License
This task is part of `dip_lab_tasks` licensed under the **MIT License**.
