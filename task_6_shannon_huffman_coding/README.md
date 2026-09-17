# Task 6: Shannon-Fano & Huffman Image Entropy Coding
**Author**: Anuj Bajpayee ([anujbajpayee14@gmail.com](mailto:anujbajpayee14@gmail.com))

## 📖 Overview

Entropy coding is a class of lossless data compression algorithms that exploits statistical redundancy by assigning variable-length prefix-free codewords to pixel intensity values based on their occurrence probabilities. More frequent symbols receive shorter codewords, while rarer symbols receive longer codewords.

This module implements, benchmarks, and verifies:
1. **Shannon Information Entropy Analysis** ($H(X)$).
2. **Shannon-Fano Recursive Partition Coding**.
3. **Huffman Optimal Min-Heap Tree Coding**.
4. **Full Bitstream Encoding & Exact Lossless Reconstruction** ($\text{MSE} = 0.0$, $\text{PSNR} = \infty$).
5. **Coding Efficiency ($\eta$) and Theoretical Compression Ratio ($\text{CR}$)**.

---

## 🖼️ Visual Demonstration & Benchmark on IIIT Nagpur Logo

Comparison grid displaying gray level probability distribution, Shannon-Fano & Huffman prefix code assignment tables, and lossless decoded reconstruction:

![Shannon-Fano and Huffman Coding Benchmark on IIITN Logo](outputs/iiitn_logo_comparison_grid.png)

---

## 📐 1. Mathematical Foundations & Metrics

### Shannon Information Entropy
The fundamental theoretical lower bound for the average number of bits per pixel:

$$H(X) = -\sum_{i=1}^{K} p_i \log_2(p_i) \quad [\text{bits/pixel}]$$

### Average Codeword Length
The expected length of the variable-length prefix code:

$$L_{\text{avg}} = \sum_{i=1}^{K} p_i \cdot l_i \quad [\text{bits/pixel}]$$

### Coding Efficiency & Redundancy

$$\eta = \left( \frac{H(X)}{L_{\text{avg}}} \right) \times 100\% \le 100\%$$

$$R = L_{\text{avg}} - H(X) \ge 0 \quad [\text{bits/pixel}]$$

### Theoretical Compression Ratio
Comparing variable-length coding against standard uncompressed 8-bit representation ($8.0\text{ bits/pixel}$):

$$\text{CR} = \frac{8.0}{L_{\text{avg}}} : 1, \quad \text{Savings } \% = \left( 1 - \frac{L_{\text{avg}}}{8.0} \right) \times 100\%$$

---

## 📊 2. Shannon-Fano vs Huffman Comparison

| Feature | Shannon-Fano Coding | Huffman Optimal Coding |
| :--- | :--- | :--- |
| **Tree Construction** | Top-Down recursive partitioning $\min \|\sum_{S_1} p_i - \sum_{S_2} p_j\|$ | Bottom-Up binary min-heap merging lowest probability pairs $\min(w_1 + w_2)$ |
| **Optimality** | Sub-optimal (may not achieve minimal $L_{\text{avg}}$) | **Mathematically Optimal** minimum-redundancy prefix code |
| **Theorem Bound** | $H(X) \le L_{\text{avg}} \le H(X) + 2$ | $H(X) \le L_{\text{avg}} < H(X) + 1$ |
| **Reconstruction** | Exact Lossless ($\text{MSE} = 0.0$) | Exact Lossless ($\text{MSE} = 0.0$) |

---

## 💻 3. Code Structure & CLI Execution

### Files in this Module:
- [`coding.py`](coding.py): Entropy calculation, Shannon-Fano generator, Huffman priority tree, bitstream encoder/decoder.
- [`visualizer.py`](visualizer.py): Symbol probability plots, codebook summary tables, and lossless decoded comparison grids.
- [`main.py`](main.py): Standalone CLI runner with statistical reporting.
- [`test_coding.py`](test_coding.py): Pytest unit tests verifying prefix-free properties, entropy, and exact reconstruction.
- [`outputs/`](outputs/): Generated visual benchmarks and comparison grids.

### Running via CLI:

```bash
# Run Shannon-Fano and Huffman coding on the IIIT Nagpur logo
python task_6_shannon_huffman_coding/main.py

# Run on custom user image
python task_6_shannon_huffman_coding/main.py --input path/to/image.png
```

### Running Unit Tests:
```bash
pytest task_6_shannon_huffman_coding/test_coding.py -v
```

---

## 📜 License
This task is part of `dip_lab_tasks` licensed under the **MIT License**.
