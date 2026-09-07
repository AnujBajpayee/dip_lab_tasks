# Digital Image Processing & Algorithmic Lab Tasks (`dip_lab_tasks`) 🚀

[![CI Pipeline](https://github.com/anujbajpayee14/dip_lab_tasks/actions/workflows/ci.yml/badge.svg)](https://github.com/anujbajpayee14/dip_lab_tasks/actions)
[![Web Workstation](https://img.shields.io/badge/Web%20App-Interactive%20Workstation-6366f1.svg?logo=flask&logoColor=white)](http://127.0.0.1:5000)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-green.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Author](https://img.shields.io/badge/author-Anuj%20Bajpayee-orange.svg)](mailto:anujbajpayee14@gmail.com)

**Author**: **Anuj Bajpayee** ([anujbajpayee14@gmail.com](mailto:anujbajpayee14@gmail.com))  
**Institution**: **Indian Institute of Information Technology, Nagpur (IIITN)**

> ### 🌐 Interactive Web Workstation: [`http://127.0.0.1:5000`](http://127.0.0.1:5000)
> **Launch Command**: `python app.py`  
> Features drag-and-drop image uploads, standard benchmarks (including the official **IIIT Nagpur Emblem**), side-by-side output visualization, and **real-time CPU Utilization (%), Execution Latency (ms), and RAM Footprint (MB)** across all 5 DIP tasks!

---

## 🌐 Interactive Web Workstation & Telemetry Dashboard

An interactive browser dashboard that allows uploading any custom image or selecting standard benchmarks (such as the official **IIIT Nagpur Logo**) to execute and visualize all DIP tasks with real-time hardware telemetry:
- ⚡ **Live CPU Utilization (%)**: Hardware-accurate processor load tracking.
- ⏱️ **Execution Latency (ms)**: Real-time wall-clock compute timing.
- 💾 **Process Memory (RAM)**: Resident Set Size (RSS) memory delta.
- 🖼️ **Side-by-Side Canvas**: Instant comparison with high-res export.

```bash
# 1. Start the Interactive Web Dashboard
python app.py

# 2. Open in your browser:
http://127.0.0.1:5000
```

---

## 📂 Repository Structure & Segmentation

```
dip_lab_tasks/
│
├── app.py                             # Interactive Flask Web Dashboard with live CPU & RAM Telemetry
├── templates/
│   └── index.html                     # Modern dark-theme DIP Workstation UI
├── static/
│   ├── style.css                      # Design system & responsive layout styles
│   └── app.js                         # Drag-and-drop uploader, API client & telemetry rendering
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
git clone https://github.com/<YOUR_USERNAME>/dip_lab_tasks.git
cd dip_lab_tasks

# Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Interactive Web Dashboard
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000` to upload images, select presets, view subbands, and monitor real-time CPU telemetry!

### 3. Run All 5 Tasks in One Command
```bash
python run_all.py
```

### 4. Run Individual CLI Tasks
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

# Task 5: 2D Discrete Wavelet Transform
python task_5_wavelet_transform/main.py --generate-test-patterns
```

### 5. Run Automated Unit Tests
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
