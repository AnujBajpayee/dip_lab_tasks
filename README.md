# Digital Image Processing & Algorithmic Lab Tasks (`dip_lab_tasks`) 🚀

[![CI Pipeline](https://github.com/anujbajpayee14/dip_lab_tasks/actions/workflows/ci.yml/badge.svg)](https://github.com/anujbajpayee14/dip_lab_tasks/actions)
[![Live Interactive Web App](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages%20App-6366f1.svg?logo=github&logoColor=white)](https://anujbajpayee.github.io/dip_lab_tasks/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-green.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Author](https://img.shields.io/badge/author-Anuj%20Bajpayee-orange.svg)](mailto:anujbajpayee14@gmail.com)

**Author**: **Anuj Bajpayee** ([anujbajpayee14@gmail.com](mailto:anujbajpayee14@gmail.com))  
**Institution**: **Indian Institute of Information Technology, Nagpur (IIITN)**

> ### 🌐 Live Interactive Web App: [**https://anujbajpayee.github.io/dip_lab_tasks/**](https://anujbajpayee.github.io/dip_lab_tasks/)
> Click the link above to directly access any DIP script in your browser and see real-time operations (Wavelet Transform, Histogram Equalization, Bit-Planes, Greyscale) executed on the official **IIIT Nagpur Logo** with live compute telemetry and zero installation required!

---

## ⚡ Direct Task Matrix & IIIT Nagpur Logo Operations

Directly explore any task script, documentation, and the corresponding processed output on the **IIIT Nagpur Logo**:

| Task Module | Core Script | Operation & Mathematical Model | Processed IIITN Logo Output | Documentation |
| :--- | :--- | :--- | :--- | :--- |
| **Task 5: Wavelet Transform** | [`wavelet.py`](task_5_wavelet_transform/wavelet.py) | **2D DWT**: $LL, LH, HL, HH$ Subband Decomposition & IDWT | [🖼️ Subband Grid](task_5_wavelet_transform/outputs/iiitn_logo_subband_grid.png) • [📉 Compression Grid](task_5_wavelet_transform/outputs/iiitn_logo_compression_grid.png) | [`task_5_wavelet_transform/README.md`](task_5_wavelet_transform/README.md) |
| **Task 4: Histogram Equalization** | [`histogram.py`](task_4_histogram_equalization/histogram.py) | **Contrast Enhancement**: GHE, BBHE, CLAHE, Color HSV | [🖼️ Equalization Comparison Grid](task_4_histogram_equalization/outputs/iiitn_logo_comparison_grid.png) | [`task_4_histogram_equalization/README.md`](task_4_histogram_equalization/README.md) |
| **Task 3: Bit-Plane Slicing** | [`bit_plane.py`](task_3_bit_plane_slicing/bit_plane.py) | **8-Bit Decomposition**: $b_k = (f \gg k)\ \&\ 1$ & LSB Steganography | [🖼️ 9-Panel Bit-Plane Grid](task_3_bit_plane_slicing/outputs/iiitn_logo_bit_planes_grid.png) • [🔒 Steganography](task_3_bit_plane_slicing/outputs/iiitn_logo_steganography_demo.png) | [`task_3_bit_plane_slicing/README.md`](task_3_bit_plane_slicing/README.md) |
| **Task 2: RGB to Greyscale** | [`grayscale.py`](task_2_rgb_to_greyscale_conversion/grayscale.py) | **Luminosity**: ITU-R BT.601 ($0.299R+0.587G+0.114B$), BT.709, Gamma | [🖼️ 9-Panel Greyscale Grid](task_2_rgb_to_greyscale_conversion/outputs/iiitn_logo_comparison_grid.png) | [`task_2_rgb_to_greyscale_conversion/README.md`](task_2_rgb_to_greyscale_conversion/README.md) |
| **Task 1: Tambola Ticket Generator** | [`generator.py`](task_1_tambola_ticket_generator/generator.py) | **CSP Engine**: $3 \times 9$ Ticket & 6-Ticket Strip (1-90) | [🎲 Generated Strip](task_1_tambola_ticket_generator/outputs/sample_strip_of_6.txt) • [📊 Benchmark](task_1_tambola_ticket_generator/outputs/algorithm_benchmark.txt) | [`task_1_tambola_ticket_generator/README.md`](task_1_tambola_ticket_generator/README.md) |

---

## 📂 Repository Structure & Segmentation

```
dip_lab_tasks/
│
├── docs/                              # Standalone GitHub Pages Live Web Workstation
│   ├── index.html                     # Live in-browser interactive DIP Explorer
│   ├── style.css                      # Design system & responsive layout styles
│   ├── app.js                         # In-browser DWT, CLAHE, Bit-Plane & Greyscale engine
│   └── assets/
│       └── iiitn_logo.png             # Official IIIT Nagpur emblem benchmark asset
│
├── app.py                             # Local Flask Web Dashboard with live CPU & RAM Telemetry
├── templates/
│   └── index.html                     # Modern dark-theme DIP Workstation UI
├── static/
│   ├── style.css                      # Styling for local Flask web app
│   └── app.js                         # Client logic for Flask backend
├── assets/
│   └── iiitn_logo.png                 # Official IIIT Nagpur benchmark logo asset
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
├── task_5_wavelet_transform/
│   ├── README.md                      # 2D DWT subband theory (LL, LH, HL, HH), Mallat algorithm, energy analysis
│   ├── wavelet.py                     # Self-contained 2D DWT, 2D IDWT, multi-level quadtree & thresholding
│   ├── visualizer.py                  # 4-subband composite grids, quadtree mosaics, and compression benchmarks
│   ├── main.py                        # Standalone CLI runner for Task 5
│   ├── test_wavelet.py                # Pytest unit tests for Task 5
│   └── outputs/                       # Subband decompositions, multi-level mosaics, and compression grids
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
└── run_all.py                         # Single runner to execute all 5 tasks & update all outputs
```

---

## 🎯 Task Summaries

### [Task 1: Tambola (Housie) Ticket Generator](task_1_tambola_ticket_generator/)
- **Description**: $3 \times 9$ Tambola ticket construction with 15 numbers, 5 per row, ascending column ranges (Col 0: $[1, 9]$, ..., Col 8: $[80, 90]$).
- **The 0/1 Random Array Journey**: Documents why naive random binary arrays fail ($\approx 28.5\% - 62.4\%$ rejection rate), and solves it via a deterministic **Constraint-Satisfaction bipartite matching engine** generating full 6-ticket strips (numbers $1 \dots 90$) with zero collisions or omissions.
- **Detailed Documentation**: See [`task_1_tambola_ticket_generator/README.md`](task_1_tambola_ticket_generator/README.md).

### [Task 2: Standard RGB to Greyscale Image Conversion](task_2_rgb_to_greyscale_conversion/)
- **Description**: Standard DIP algorithms for trichromatic RGB to greyscale conversion based on human retinal physiology (L, M, S cone sensitivities with peak photopic luminous efficiency $V(\lambda)$ at $555\text{ nm}$ green).
- **Algorithms**: ITU-R BT.601, ITU-R BT.709 / sRGB, Simple Average, HSL Lightness, Gamma-Corrected Luma, and Single-Channel extraction.
- **Detailed Documentation**: See [`task_2_rgb_to_greyscale_conversion/README.md`](task_2_rgb_to_greyscale_conversion/README.md).

### [Task 3: 8-Bit Plane Slicing & Digital Steganography](task_3_bit_plane_slicing/)
- **Description**: Mathematical decomposition of 8-bit images into 8 binary matrices ($b_k = (f \gg k)\ \&\ 1$), isolating structural geometry in MSB and noise in LSB.
- **Applications**: Selective multi-plane reconstruction, lossy compression ($>94\%$ energy in top 4 bits), and imperceptible Least Significant Bit (LSB) digital watermarking ($\text{PSNR} > 50\text{ dB}$).
- **Detailed Documentation**: See [`task_3_bit_plane_slicing/README.md`](task_3_bit_plane_slicing/README.md).

### [Task 4: Histogram Equalization Types & Execution](task_4_histogram_equalization/)
- **Description**: Practical contrast enhancement algorithms: Global Histogram Equalization (GHE), Brightness Preserving Bi-Histogram Equalization (BBHE), Contrast Limited Adaptive Histogram Equalization (CLAHE), Histogram Matching (Specification), and Color-Preserving HSV Equalization.
- **Detailed Documentation**: See [`task_4_histogram_equalization/README.md`](task_4_histogram_equalization/README.md).

### [Task 5: 2D Discrete Wavelet Transform (DWT & IDWT)](task_5_wavelet_transform/)
- **Description**: Space-frequency localization decomposing images into approximation ($LL$) and directional edge subbands ($LH$: Horizontal, $HL$: Vertical, $HH$: Diagonal).
- **Applications**: Multi-level dyadic quad-tree decomposition, lossless mathematical reconstruction ($f = \text{IDWT}(\text{DWT}(f))$), subband energy distribution analysis ($E(LL) > 96\%$), and wavelet coefficient thresholding / compression.
- **Detailed Documentation**: See [`task_5_wavelet_transform/README.md`](task_5_wavelet_transform/README.md).

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/AnujBajpayee/dip_lab_tasks.git
cd dip_lab_tasks

# Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run All 5 Tasks in One Command
```bash
python run_all.py
```

### 3. Run Local Web App (Flask Dashboard)
```bash
python app.py
```

### 4. Run Automated Unit Tests
```bash
pytest task_1_tambola_ticket_generator/test_tambola.py -v
pytest task_2_rgb_to_greyscale_conversion/test_grayscale.py -v
pytest task_3_bit_plane_slicing/test_bit_plane.py -v
pytest task_4_histogram_equalization/test_histogram.py -v
pytest task_5_wavelet_transform/test_wavelet.py -v
```

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
