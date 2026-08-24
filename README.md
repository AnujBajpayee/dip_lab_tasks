# Digital Image Processing & Algorithmic Lab Tasks (`dip_lab_tasks`) 🚀

[![CI Pipeline](https://github.com/anujbajpayee14/dip_lab_tasks/actions/workflows/ci.yml/badge.svg)](https://github.com/anujbajpayee14/dip_lab_tasks/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-green.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Author](https://img.shields.io/badge/author-Anuj%20Bajpayee-orange.svg)](mailto:anujbajpayee14@gmail.com)

**Author**: **Anuj Bajpayee** ([anujbajpayee14@gmail.com](mailto:anujbajpayee14@gmail.com))

This repository contains the laboratory assignments and algorithmic implementations for Digital Image Processing (DIP) and Computational Algorithms. Each task is segregated into its own self-contained directory with dedicated code, documentation, unit tests, and generated visual outputs.

---

## 📂 Repository Structure & Segmentation

```
dip_lab_tasks/
│
├── task_1_tambola_ticket_generator/
│   ├── README.md                      # Complete description of rules, naive 0/1 array analysis & CSP
│   ├── generator.py                   # Single ticket & 6-ticket strip (1-90) CSP engine
│   ├── naive_generator.py             # Naive 0/1 random array generator & Monte Carlo profiler
│   ├── visualizer.py                  # ASCII, Markdown, SVG, and PNG visual rendering with decade headers
│   ├── main.py                        # Standalone CLI runner for Task 1
│   ├── test_tambola.py                # Pytest unit tests for Task 1
│   └── outputs/                       # Generated sample tickets, JSON, SVG, PNG, strips, and logs
│
├── task_2_rgb_to_greyscale_conversion/
│   ├── README.md                      # Human visual perception, ITU-R standards, gamma expansion
│   ├── grayscale.py                   # ITU-R BT.601, BT.709, Average, Lightness, Gamma, Channels
│   ├── visualizer.py                  # Calibration target synthesizer & 9-panel comparison grid with formulas
│   ├── main.py                        # Standalone CLI runner for Task 2
│   ├── test_grayscale.py              # Pytest unit tests for Task 2
│   └── outputs/                       # Test charts, channel decompositions, and 9-panel comparison grids
│
├── task_3_bit_plane_slicing/
│   ├── README.md                      # 8-bit decomposition theory, visible input/output grids, steganography
│   ├── bit_plane.py                   # Bit extraction (0-7), progressive reconstruction, entropy & LSB
│   ├── visualizer.py                  # Synthesizer for rich targets, watermarks & 9-panel composite grids
│   ├── main.py                        # Standalone CLI runner for Task 3
│   ├── test_bit_plane.py              # Pytest unit tests for Task 3
│   └── outputs/                       # Individual bit planes, progressive grids, and steganography demos
│
├── task_4_histogram_equalization/
│   ├── README.md                      # Concise guide to HE types (GHE, BBHE, CLAHE, Matching, Color)
│   ├── histogram.py                   # Vectorized NumPy implementation of all HE algorithms
│   ├── visualizer.py                  # Synthesizer for low-contrast test scenes & histogram/CDF plots
│   ├── main.py                        # Standalone CLI runner for Task 4
│   ├── test_histogram.py              # Pytest unit tests for Task 4
│   └── outputs/                       # Low-contrast before/after grids and histogram distribution graphs
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml                     # Multi-OS & Multi-Python CI workflow
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── pyproject.toml
├── requirements.txt
└── run_all.py                         # Single runner to execute all 4 tasks & update all outputs
```

---

## 🎯 Task Summaries

### [Task 1: Tambola (Housie) Ticket Generator](task_1_tambola_ticket_generator/)
- **Description**: Detailed analysis of how a standard $3 \times 9$ Tambola ticket is constructed with 15 numbers, 5 numbers per row, column range constraints (Col 0: $[1, 9]$, ..., Col 8: $[80, 90]$), and vertical ascending sorting.
- **The 0/1 Random Array Journey**: Documents how initial naive random binary arrays suffer $\approx 28.5\% - 62.4\%$ rejection rates due to column starvation, and how we evolved to a deterministic **Constraint-Satisfaction bipartite matching engine** capable of generating full 6-ticket strips using numbers $1 \dots 90$ with zero collisions or omissions.
- **Detailed Documentation**: See [`task_1_tambola_ticket_generator/README.md`](task_1_tambola_ticket_generator/README.md).

### [Task 2: Standard RGB to Greyscale Image Conversion](task_2_rgb_to_greyscale_conversion/)
- **Description**: Rigorous implementation of standard digital image processing algorithms for converting trichromatic RGB images to greyscale based on human retinal physiology (L, M, S cone sensitivities with peak photopic luminous efficiency $V(\lambda)$ at $555\text{ nm}$ green).
- **Algorithms**: ITU-R BT.601, ITU-R BT.709 / sRGB, Simple Average, HSL Lightness / Desaturation, Linearized Gamma-Corrected Luma, and Single-Channel decompositions.
- **Outputs**: Calibrated test target conversions and 9-panel side-by-side composite comparison grids with explicit mathematical formulas.
- **Detailed Documentation**: See [`task_2_rgb_to_greyscale_conversion/README.md`](task_2_rgb_to_greyscale_conversion/README.md).

### [Task 3: 8-Bit Plane Slicing & Digital Steganography](task_3_bit_plane_slicing/)
- **Description**: Mathematical decomposition of 8-bit monochromatic images into 8 binary matrices (1-bit planes), isolating geometric structure in high-order bits (MSB) and fine texture/noise in low-order bits (LSB).
- **Applications**: Selective multi-plane reconstruction, lossy image compression (50% bit reduction with $>94\%$ energy conservation), and imperceptible Least Significant Bit (LSB) digital watermarking/steganography ($\text{PSNR} > 50\text{ dB}$).
- **Outputs**: Embedded input patterns, 9-panel bit-plane grids, cumulative progressive decoding grids, and steganography pipelines.
- **Detailed Documentation**: See [`task_3_bit_plane_slicing/README.md`](task_3_bit_plane_slicing/README.md).

### [Task 4: Histogram Equalization Types & Execution](task_4_histogram_equalization/)
- **Description**: Comprehensive practical suite of spatial contrast enhancement algorithms: Global Histogram Equalization (GHE), Brightness Preserving Bi-Histogram Equalization (BBHE), Contrast Limited Adaptive Histogram Equalization (CLAHE), Histogram Matching (Specification), and Color-Preserving HSV Equalization.
- **Outputs**: Low-contrast before/after comparison grids with embedded 256-bin histogram and CDF distribution graphs.
- **Detailed Documentation**: See [`task_4_histogram_equalization/README.md`](task_4_histogram_equalization/README.md).

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/<YOUR_USERNAME>/dip_lab_tasks.git
cd dip_lab_tasks

# Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run All 4 Tasks in One Command
```bash
python run_all.py
```

### 3. Run Individual Tasks
```bash
# Task 1: Tambola Generator
python task_1_tambola_ticket_generator/main.py --ticket
python task_1_tambola_ticket_generator/main.py --strip
python task_1_tambola_ticket_generator/main.py --benchmark

# Task 2: RGB to Greyscale
python task_2_rgb_to_greyscale_conversion/main.py --generate-test-patterns

# Task 3: Bit Plane Slicing & Steganography
python task_3_bit_plane_slicing/main.py --generate-test-patterns

# Task 4: Histogram Equalization Suite
python task_4_histogram_equalization/main.py --generate-test-patterns
```

### 4. Run Automated Unit Tests
```bash
pytest task_1_tambola_ticket_generator/test_tambola.py -v
pytest task_2_rgb_to_greyscale_conversion/test_grayscale.py -v
pytest task_3_bit_plane_slicing/test_bit_plane.py -v
pytest task_4_histogram_equalization/test_histogram.py -v
```

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
