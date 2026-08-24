# Digital Image Processing & Algorithmic Lab Tasks (`dip_lab_tasks`) 🚀

[![CI Pipeline](https://github.com/anujbajpayee14/dip_lab_tasks/actions/workflows/ci.yml/badge.svg)](https://github.com/anujbajpayee14/dip_lab_tasks/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-green.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Author](https://img.shields.io/badge/author-Anuj%20Bajpayee-orange.svg)](mailto:anujbajpayee14@gmail.com)

**Author**: **Anuj Bajpayee** ([anujbajpayee14@gmail.com](mailto:anujbajpayee14@gmail.com))

This repository contains the laboratory assignments and algorithmic implementations for Digital Image Processing (DIP) and Computational Algorithms. Each task is segregated into its own self-contained directory with dedicated code, extensive documentation, unit tests, and generated visual outputs.

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
│   └── outputs/
│       ├── sample_ticket_1.txt        # ASCII formatted ticket
│       ├── sample_ticket_1.json       # JSON ticket payload
│       ├── sample_ticket_1.svg        # Scalable Vector Graphics ticket card
│       ├── sample_ticket_1.png        # High-resolution PNG ticket
│       ├── sample_strip_of_6.txt      # 6-ticket strip containing numbers 1-90
│       ├── sample_strip_of_6.json     # JSON strip payload
│       └── algorithm_benchmark.txt    # Naive 0/1 mask rejection benchmark log
│
├── task_2_rgb_to_greyscale_conversion/
│   ├── README.md                      # Comprehensive guide on human vision, ITU-R standards, gamma
│   ├── grayscale.py                   # ITU-R BT.601, BT.709, Average, Lightness, Gamma, Channels
│   ├── visualizer.py                  # Calibration target synthesizer & 9-panel comparison grid with formulas
│   ├── main.py                        # Standalone CLI runner for Task 2
│   ├── test_grayscale.py              # Pytest unit tests for Task 2
│   └── outputs/
│       ├── color_chart_original_rgb.png     # Input RGB color test target
│       ├── color_chart_rec601.png           # Rec.601 Luma output
│       ├── color_chart_rec709.png           # Rec.709 Luma output
│       ├── color_chart_average.png          # Simple Average output
│       ├── color_chart_lightness.png        # HSL Lightness output
│       ├── color_chart_gamma.png            # Linear Gamma-corrected output
│       ├── color_chart_channel_red.png      # Red channel decomposition
│       ├── color_chart_channel_green.png    # Green channel decomposition
│       ├── color_chart_channel_blue.png     # Blue channel decomposition
│       ├── color_chart_comparison_grid.png  # 9-Panel side-by-side comparison grid with formulas
│       ├── scenery_original_rgb.png         # Input scenery image
│       └── scenery_comparison_grid.png      # 9-Panel scenery comparison grid
│
├── task_3_bit_plane_slicing/
│   ├── README.md                      # 8-bit decomposition theory, visible input/output grids, steganography
│   ├── bit_plane.py                   # Bit extraction (0-7), progressive reconstruction, entropy & LSB
│   ├── visualizer.py                  # Synthesizer for rich targets, watermarks & 9-panel composite grids
│   ├── main.py                        # Standalone CLI runner for Task 3
│   ├── test_bit_plane.py              # Pytest unit tests for Task 3
│   └── outputs/
│       ├── test_pattern_original.png  # Input calibrated test pattern
│       ├── test_pattern_plane_0.png   # Bit plane 0 (LSB)
│       ├── test_pattern_plane_7.png   # Bit plane 7 (MSB)
│       ├── test_pattern_bit_planes_grid.png # 9-Panel bit plane decomposition grid
│       ├── test_pattern_cumulative_reconstruction_grid.png # Progressive reconstruction grid
│       ├── test_pattern_watermark_original.png # Binary watermark security emblem
│       ├── test_pattern_stego_embedded.png # Stego carrier image (imperceptible LSB watermark)
│       ├── test_pattern_extracted_watermark.png # Exact recovered watermark
│       └── test_pattern_steganography_demo.png # 4-Panel steganography demonstration
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml                     # Multi-OS & Multi-Python CI workflow
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── pyproject.toml
├── requirements.txt
└── run_all.py                         # Single runner to execute all tasks & update all outputs
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
- **Outputs**: Calibrated test target conversions and 9-panel side-by-side composite comparison grids with explicit mathematical formulas printed on each card.
- **Detailed Documentation**: See [`task_2_rgb_to_greyscale_conversion/README.md`](task_2_rgb_to_greyscale_conversion/README.md).

### [Task 3: 8-Bit Plane Slicing & Digital Steganography](task_3_bit_plane_slicing/)
- **Description**: Mathematical decomposition of 8-bit monochromatic images into 8 binary matrices (1-bit planes), isolating geometric structure in high-order bits (MSB) and fine texture/noise in low-order bits (LSB).
- **Applications**: Selective multi-plane reconstruction, lossy image compression (50% bit reduction with $>94\%$ energy conservation), and imperceptible Least Significant Bit (LSB) digital watermarking/steganography ($\text{PSNR} > 50\text{ dB}$).
- **Outputs**: Embedded input patterns, 9-panel bit-plane grids, cumulative progressive decoding grids, and steganography pipelines with operation labels.
- **Detailed Documentation**: See [`task_3_bit_plane_slicing/README.md`](task_3_bit_plane_slicing/README.md).

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

### 2. Run All Tasks in One Command
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
```

### 4. Run Automated Unit Tests
```bash
pytest task_1_tambola_ticket_generator/test_tambola.py -v
pytest task_2_rgb_to_greyscale_conversion/test_grayscale.py -v
pytest task_3_bit_plane_slicing/test_bit_plane.py -v
```

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
