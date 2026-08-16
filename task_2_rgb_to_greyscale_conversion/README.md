# Task 2: Standard RGB to Greyscale Image Conversion
**Author**: Anuj Bajpayee ([anujbajpayee14@gmail.com](mailto:anujbajpayee14@gmail.com))

## 📖 Overview

Transforming a three-channel trichromatic ($RGB$) digital image into a single-channel monochromatic (greyscale) representation is one of the cornerstone techniques in digital image processing, computer vision, and visual neuroscience. 

This module provides a scientific and engineering implementation of all standard greyscale conversion algorithms, including:
1. **ITU-R Recommendation BT.601** (Standard Definition Video / PAL / NTSC)
2. **ITU-R Recommendation BT.709** (High Definition & sRGB Display Standard)
3. **Simple Arithmetic Average**
4. **HSL Lightness / Desaturation Model**
5. **Linearized Gamma-Corrected Perceptual Luminance**
6. **Single Channel Extractions (Red, Green, Blue)**

---

## 👁️ 1. Human Visual Perception & Biological Foundations

Human vision does **not** perceive all wavelengths of visible light with equal brightness. Color perception is mediated by three classes of retinal cone photoreceptors:

```
                            HUMAN RETINA
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
          ROD CELLS (~120M)                 CONE CELLS (~6M)
     - Scotopic (dim-light) vision      - Photopic (daylight) vision
     - Achromatic (intensity only)      - Chromatic (color perception)
     - High light sensitivity           - High spatial & temporal acuity
```

### 1.1 Spectral Sensitivities of Retinal Cones:
1. **S-Cones (Short Wavelength / Blue)**: Peak sensitivity $\lambda_{\text{peak}} \approx 420\text{ nm}$.
2. **M-Cones (Medium Wavelength / Green)**: Peak sensitivity $\lambda_{\text{peak}} \approx 534\text{ nm}$.
3. **L-Cones (Long Wavelength / Red)**: Peak sensitivity $\lambda_{\text{peak}} \approx 564\text{ nm}$.

### 1.2 The Luminous Efficiency Function $V(\lambda)$:
Standardized by CIE (1931), the photopic luminous efficiency curve shows peak human sensitivity at **$\lambda_{\text{max}} = 555\text{ nm}$ (Green-Yellow spectrum)**.
- **Green light** accounts for **$\approx 59\% - 72\%$** of perceived subjective brightness.
- **Red light** accounts for **$\approx 21\% - 30\%$**.
- **Blue light** accounts for only **$\approx 7\% - 11\%$**.

---

## 📐 2. Mathematical Formulations & Standards

```
+-----------------------------------------------------------------------------------------------+
| Method                | Formula                                                 | Standard     |
| --------------------------------------------------------------------------------------------- |
| ITU-R BT.601 Luma     | Y = 0.299*R + 0.587*G + 0.114*B                        | SDTV / NTSC  |
| ITU-R BT.709 Luma     | Y = 0.2126*R + 0.7152*G + 0.0722*B                     | HDTV / sRGB  |
| Simple Average        | Y = (R + G + B) / 3                                    | Naive Mean   |
| HSL Lightness         | Y = (max(R,G,B) + min(R,G,B)) / 2                      | Desaturation |
| Gamma-Corrected Luma  | Y = 255 * (0.2126*R_lin + 0.7152*G_lin + 0.0722*B_lin)^(1/gamma) | Perceptual |
+-----------------------------------------------------------------------------------------------+
```

### 2.1 ITU-R BT.601 (SDTV Standard)
$$Y_{601} = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$
Developed for cathode-ray tubes (CRTs) and broadcast systems, assigning dominant weight ($58.7\%$) to green.

### 2.2 ITU-R BT.709 (HDTV / Modern sRGB Monitors)
$$Y_{709} = 0.2126 \cdot R + 0.7152 \cdot G + 0.0722 \cdot B$$
Matches the purer phosphors and LED/OLED chromaticities of modern computer displays, raising green's weight to $71.52\%$.

### 2.3 The Flaw of Simple Average
$$Y_{\text{avg}} = \frac{R + G + B}{3}$$
Assigns equal $33.3\%$ weight to Blue and Green. Under this formula, pure saturated Blue `(0, 0, 255)` produces the same greyscale value ($85$) as pure Green `(0, 255, 0)`, creating unnatural flat tones and destroying photographic contrast.

### 2.4 Gamma Correction & Linear Radiant Flux
Standard sRGB image files store non-linearly encoded pixel values ($C_{\text{sRGB}} \approx C_{\text{linear}}^{1/\gamma}$ with $\gamma \approx 2.2$).
True physical energy conservation requires:
1. **Gamma Expansion**: Converting sRGB values to linear radiometric energy $C_{\text{linear}} = (C/255)^\gamma$.
2. **Linear Weighting**: Calculating linear luminance $Y_{\text{linear}} = 0.2126 R_{\text{linear}} + 0.7152 G_{\text{linear}} + 0.0722 B_{\text{linear}}$.
3. **Gamma Compression**: Re-encoding to perceptual non-linear display space $Y = 255 \cdot Y_{\text{linear}}^{1/\gamma}$.

---

## 📊 3. Response Across Pure Primary Colors

| Input Color | $(R, G, B)$ | Rec. 601 | Rec. 709 | Average | Lightness | Gamma Corrected |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pure White** | `(255, 255, 255)` | **255** | **255** | **255** | **255** | **255** |
| **Pure Black** | `(0, 0, 0)` | **0** | **0** | **0** | **0** | **0** |
| **Pure Green** | `(0, 255, 0)` | **150** | **182** | **85** | **128** | **219** |
| **Pure Red** | `(255, 0, 0)` | **76** | **54** | **85** | **128** | **125** |
| **Pure Blue** | `(0, 0, 255)` | **29** | **18** | **85** | **128** | **74** |
| **Pure Yellow** | `(255, 255, 0)` | **226** | **237** | **170** | **128** | **244** |
| **Pure Cyan** | `(0, 255, 255)` | **179** | **201** | **170** | **128** | **227** |
| **Pure Magenta** | `(255, 0, 255)` | **105** | **73** | **170** | **128** | **139** |

---

## 💻 4. Code Structure & Usage

### Files in this Module:
- [`grayscale.py`](grayscale.py): Core conversion algorithms implemented in vectorized NumPy with pure Python fallbacks.
- [`visualizer.py`](visualizer.py): Calibrated color target synthesizer, landscape generator, and side-by-side 9-panel composite grid visualizer.
- [`main.py`](main.py): CLI interface for image conversion and statistical reporting.
- [`test_grayscale.py`](test_grayscale.py): Pytest unit test suite.
- [`outputs/`](outputs/): Output pictures for all conversion variants and side-by-side comparison grids.

### Running via CLI:

```bash
# 1. Synthesize calibration test charts and generate all greyscale variants
python task_2_rgb_to_greyscale_conversion/main.py --generate-test-patterns

# 2. Convert any custom user image
python task_2_rgb_to_greyscale_conversion/main.py --input path/to/image.jpg --output-dir task_2_rgb_to_greyscale_conversion/outputs
```

### Running Unit Tests:
```bash
pytest task_2_rgb_to_greyscale_conversion/test_grayscale.py -v
```

---

## 🖼️ 5. Generated Output Pictures

All generated images are organized in [`outputs/`](outputs/):
- `color_chart_original_rgb.png` (Original RGB target)
- `color_chart_rec601.png` (ITU-R Rec. 601)
- `color_chart_rec709.png` (ITU-R Rec. 709)
- `color_chart_average.png` (Simple Average)
- `color_chart_lightness.png` (HSL Lightness)
- `color_chart_gamma.png` (Gamma-Corrected Linear Luma)
- `color_chart_comparison_grid.png` (9-Panel side-by-side composite grid)
- `scenery_original_rgb.png` (Landscape scenery)
- `scenery_comparison_grid.png` (9-Panel landscape comparison grid)
