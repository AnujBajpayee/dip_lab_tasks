"""
DIP Lab Tasks: Interactive Flask Web Application & Telemetry Profiler
=====================================================================
Provides an interactive web interface for uploading images and running all
digital image processing tasks (RGB Greyscale, Bit-Plane Slicing, Histogram Equalization,
2D Wavelet Transform, and Tambola Ticket Generation) with live CPU utilization,
execution timing, and memory telemetry.
"""

from __future__ import annotations
import os
import io
import sys
import time
import base64
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# Configure UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import psutil
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify, render_template, send_from_directory

base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))

# Task 1 Imports
from task_1_tambola_ticket_generator.generator import generate_ticket, generate_strip
from task_1_tambola_ticket_generator.visualizer import ticket_to_svg, ticket_to_ascii, strip_to_ascii

# Task 2 Imports
from task_2_rgb_to_greyscale_conversion.grayscale import (
    to_rec601_luminance,
    to_rec709_luminance,
    to_average_grayscale,
    to_lightness_grayscale,
    to_gamma_corrected_grayscale,
    extract_channel,
)
from task_2_rgb_to_greyscale_conversion.visualizer import (
    create_comparison_grid,
    compute_image_statistics,
    create_color_palette_test_image,
    create_scenery_test_image,
)

# Task 3 Imports
from task_3_bit_plane_slicing.bit_plane import (
    extract_all_bit_planes,
    reconstruct_cumulative_msb,
    embed_watermark_lsb,
    extract_watermark_lsb,
    compute_bit_plane_metrics,
    compute_mse_psnr,
)
from task_3_bit_plane_slicing.visualizer import (
    create_bit_plane_grid,
    create_cumulative_reconstruction_grid,
    create_steganography_grid,
    create_watermark_pattern,
    create_rich_test_pattern,
)

# Task 4 Imports
from task_4_histogram_equalization.histogram import (
    global_histogram_equalization,
    bi_histogram_equalization,
    clahe,
    histogram_matching,
    color_histogram_equalization,
)
from task_4_histogram_equalization.visualizer import (
    create_histogram_comparison_grid,
    create_low_contrast_scene,
    create_uneven_illumination_scene,
)

# Task 5 Imports
from task_5_wavelet_transform.wavelet import (
    dwt2,
    idwt2,
    wavedec2,
    compute_wavelet_energy,
    threshold_wavelet_coefficients,
)
from task_5_wavelet_transform.visualizer import (
    create_subband_decomposition_grid,
    create_multilevel_quadtree_image,
    create_wavelet_compression_grid,
    normalize_subband_for_display,
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload


# =============================================================================
# Telemetry & Profiler Helper
# =============================================================================

class PerformanceProfiler:
    """Tracks CPU utilization %, wall-clock execution time (ms), and RAM footprint."""
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_wall = 0.0
        self.start_cpu_time = 0.0
        self.start_rss = 0.0
        self.end_wall = 0.0
        self.end_cpu_time = 0.0
        self.end_rss = 0.0

    def __enter__(self):
        # Warmup CPU measurement
        psutil.cpu_percent(interval=None)
        self.start_wall = time.perf_counter()
        cpu_times = self.process.cpu_times()
        self.start_cpu_time = cpu_times.user + cpu_times.system
        self.start_rss = self.process.memory_info().rss / (1024.0 * 1024.0)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_wall = time.perf_counter()
        cpu_times = self.process.cpu_times()
        self.end_cpu_time = cpu_times.user + cpu_times.system
        self.end_rss = self.process.memory_info().rss / (1024.0 * 1024.0)

    @property
    def elapsed_ms(self) -> float:
        return (self.end_wall - self.start_wall) * 1000.0

    @property
    def cpu_utilization_pct(self) -> float:
        wall_delta = self.end_wall - self.start_wall
        if wall_delta <= 1e-6:
            return 0.0
        cpu_delta = self.end_cpu_time - self.start_cpu_time
        num_cores = psutil.cpu_count(logical=True) or 1
        pct = (cpu_delta / wall_delta) * 100.0 / num_cores
        return min(100.0, max(0.0, pct))

    @property
    def memory_rss_mb(self) -> float:
        return self.end_rss

    @property
    def memory_delta_mb(self) -> float:
        return self.end_rss - self.start_rss


def pil_to_base64(img: Image.Image, format: str = "PNG") -> str:
    """Encodes PIL image to Base64 data URI string."""
    buffered = io.BytesIO()
    img.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"


def numpy_to_base64(arr: np.ndarray) -> str:
    """Encodes NumPy array to Base64 PNG."""
    if arr.dtype != np.uint8:
        arr_uint8 = np.clip(np.round(arr), 0, 255).astype(np.uint8)
    else:
        arr_uint8 = arr
    img = Image.fromarray(arr_uint8)
    return pil_to_base64(img, "PNG")


# =============================================================================
# Web Routes
# =============================================================================

@app.route("/")
def index():
    """Renders the main interactive DIP workstation dashboard."""
    return render_template("index.html")


@app.route("/assets/<path:filename>")
def serve_asset(filename: str):
    """Serves static assets such as sample images and IIITN logo."""
    return send_from_directory(os.path.join(base_dir, "assets"), filename)


@app.route("/api/sample-images", methods=["GET"])
def get_sample_images():
    """Returns metadata for default preset images."""
    samples = [
        {
            "id": "iiitn_logo",
            "name": "🎓 IIIT Nagpur Official Logo",
            "path": "/assets/iiitn_logo.png",
            "desc": "Official IIITN Emblem (Vibrant Purple & Orange Geometric Shapes)"
        },
        {
            "id": "color_chart",
            "name": "🎨 Calibrated Color Chart",
            "path": "/assets/color_chart_preview.png",
            "desc": "Multi-hued synthetic color wheel and step wedges"
        },
        {
            "id": "test_pattern",
            "name": "🔬 Multi-Bit Decomposition Target",
            "path": "/assets/test_pattern_preview.png",
            "desc": "Concentric rings, Siemens star, and fine typography"
        },
        {
            "id": "low_contrast",
            "name": "🌙 Low-Contrast Night Scene",
            "path": "/assets/low_contrast_preview.png",
            "desc": "Under-exposed shadow scene with hidden structures"
        }
    ]
    return jsonify({"success": True, "samples": samples})


@app.route("/api/process", methods=["POST"])
def process_image():
    """
    Main DIP processing API endpoint.
    Accepts uploaded file or sample ID, runs requested task algorithm,
    and returns processed image + real-time performance telemetry.
    """
    task = request.form.get("task", "task_5_wavelet")
    algo = request.form.get("algorithm", "default")
    sample_id = request.form.get("sample_id", "")
    params_str = request.form.get("params", "{}")

    try:
        params = json.loads(params_str)
    except Exception:
        params = {}

    # 1. Load Input Image
    input_img: Optional[Image.Image] = None
    if "image" in request.files and request.files["image"].filename != "":
        file = request.files["image"]
        input_img = Image.open(file.stream)
    elif sample_id:
        if sample_id == "iiitn_logo":
            p = os.path.join(base_dir, "assets", "iiitn_logo.png")
            input_img = Image.open(p)
        elif sample_id == "color_chart":
            input_img = create_color_palette_test_image(640, 480)
        elif sample_id == "test_pattern":
            input_img = create_rich_test_pattern(640, 480)
        elif sample_id == "low_contrast":
            input_img = create_low_contrast_scene(640, 480)
        elif sample_id == "uneven_illumination":
            input_img = create_uneven_illumination_scene(640, 480)
        elif sample_id == "scenery":
            input_img = create_scenery_test_image(640, 480)

    if input_img is None:
        # Default fallback to IIITN logo
        p = os.path.join(base_dir, "assets", "iiitn_logo.png")
        if os.path.exists(p):
            input_img = Image.open(p)
        else:
            input_img = create_rich_test_pattern(640, 480)

    orig_w, orig_h = input_img.size
    is_color = input_img.mode in ("RGB", "RGBA")
    np_input = np.array(input_img.convert("RGB") if is_color else input_img.convert("L"))

    # Response data containers
    result_img_base64 = ""
    extra_images: Dict[str, str] = {}
    stats: Dict[str, Any] = {}
    formula_info = ""
    algo_title = ""

    profiler = PerformanceProfiler()

    # =========================================================================
    # Task Execution with Telemetry Profiling
    # =========================================================================
    with profiler:
        # ---------------------------------------------------------------------
        # TASK 2: RGB TO GREYSCALE CONVERSION
        # ---------------------------------------------------------------------
        if task in ("task_2_rgb_to_greyscale", "task_2"):
            np_rgb = np.array(input_img.convert("RGB"))
            if algo == "rec601":
                algo_title = "ITU-R BT.601 Luminosity"
                formula_info = "Y = 0.299·R + 0.587·G + 0.114·B"
                out_arr = to_rec601_luminance(np_rgb)
            elif algo == "rec709":
                algo_title = "ITU-R BT.709 / sRGB Standard"
                formula_info = "Y = 0.2126·R + 0.7152·G + 0.0722·B"
                out_arr = to_rec709_luminance(np_rgb)
            elif algo == "average":
                algo_title = "Simple Average"
                formula_info = "Y = (R + G + B) / 3"
                out_arr = to_average_grayscale(np_rgb)
            elif algo == "lightness":
                algo_title = "HSL Lightness / Desaturation"
                formula_info = "Y = [max(R,G,B) + min(R,G,B)] / 2"
                out_arr = to_lightness_grayscale(np_rgb)
            elif algo == "gamma":
                algo_title = "Gamma-Corrected Linear Luma (γ=2.2)"
                formula_info = "Y = [0.2126·R^γ + 0.7152·G^γ + 0.0722·B^γ]^(1/γ)"
                out_arr = to_gamma_corrected_grayscale(np_rgb)
            elif algo in ("channel_red", "channel_green", "channel_blue"):
                ch = algo.split("_")[1]
                algo_title = f"{ch.capitalize()} Single Channel"
                formula_info = f"Y = {ch.upper()} channel intensity"
                out_arr = extract_channel(np_rgb, ch)
            else:
                # Full 9-panel comparison grid
                algo_title = "9-Panel Conversion Benchmark Grid"
                formula_info = "Comparison across all 8 photometric models"
                conversions = {
                    "Rec.601 Luminosity": to_rec601_luminance(np_rgb),
                    "Rec.709 Luminosity": to_rec709_luminance(np_rgb),
                    "Simple Average": to_average_grayscale(np_rgb),
                    "HSL Lightness": to_lightness_grayscale(np_rgb),
                    "Gamma-Corrected": to_gamma_corrected_grayscale(np_rgb),
                    "Red Channel": extract_channel(np_rgb, "red"),
                    "Green Channel": extract_channel(np_rgb, "green"),
                    "Blue Channel": extract_channel(np_rgb, "blue"),
                }
                grid = create_comparison_grid(input_img, conversions)
                result_img_base64 = pil_to_base64(grid)
                out_arr = conversions["Rec.601 Luminosity"]

            if not result_img_base64:
                result_img_base64 = numpy_to_base64(out_arr)
            stats = compute_image_statistics(out_arr)

        # ---------------------------------------------------------------------
        # TASK 3: 8-BIT PLANE SLICING & STEGANOGRAPHY
        # ---------------------------------------------------------------------
        elif task in ("task_3_bit_plane_slicing", "task_3"):
            np_gray = np.array(input_img.convert("L"))
            planes = extract_all_bit_planes(np_gray, scale_to_255=True)

            if algo.startswith("plane_"):
                k = int(algo.split("_")[1])
                algo_title = f"Bit-Plane {k} ({'MSB' if k==7 else 'LSB' if k==0 else 'Mid-order'})"
                formula_info = f"b_{k} = (f(x, y) >> {k}) & 1"
                out_arr = planes[k]
                result_img_base64 = numpy_to_base64(out_arr)
            elif algo == "progressive_reconstruction":
                algo_title = "Progressive Cumulative MSB Reconstruction"
                formula_info = "f_k = sum_{i=7-k}^7 2^i · b_i"
                cumul = reconstruct_cumulative_msb(np_gray)
                grid = create_cumulative_reconstruction_grid(input_img, cumul)
                result_img_base64 = pil_to_base64(grid)
            elif algo == "steganography":
                algo_title = "Least Significant Bit (LSB) Steganography"
                formula_info = "f_stego = (f & 0xFE) | watermark_bit"
                wm_text = params.get("watermark_text", "IIIT NAGPUR 2026")
                wm_pil = create_watermark_pattern(orig_w, orig_h, label=wm_text)
                wm_np = np.array(wm_pil)
                stego_np = embed_watermark_lsb(np_gray, wm_np, bit_plane=0)
                extracted_np = extract_watermark_lsb(stego_np, bit_plane=0, scale_to_255=True)
                grid = create_steganography_grid(input_img, wm_pil, stego_np, extracted_np)
                result_img_base64 = pil_to_base64(grid)
                mse, psnr = compute_mse_psnr(np_gray, stego_np)
                stats["Stego_MSE"] = round(mse, 4)
                stats["Stego_PSNR_dB"] = round(psnr, 2)
            else:
                # 9-panel bit-plane grid
                algo_title = "9-Panel Bit-Plane Decomposition Grid"
                formula_info = "b_k = (f >> k) & 1 for k ∈ [0, 7]"
                grid = create_bit_plane_grid(input_img, planes)
                result_img_base64 = pil_to_base64(grid)

            metrics = compute_bit_plane_metrics(np_gray)
            stats["bit_planes_energy"] = metrics

        # ---------------------------------------------------------------------
        # TASK 4: HISTOGRAM EQUALIZATION
        # ---------------------------------------------------------------------
        elif task in ("task_4_histogram_equalization", "task_4"):
            if is_color and algo in ("color_clahe", "color_ghe", "color_bbhe"):
                np_rgb = np.array(input_img.convert("RGB"))
                if algo == "color_ghe":
                    algo_title = "Color-Preserving Global HE (HSV V-Channel)"
                    formula_info = "V_new = GHE(V_old) • RGB_new = RGB · (V_new / V_old)"
                    out_arr = color_histogram_equalization(np_rgb, method="ghe")
                elif algo == "color_bbhe":
                    algo_title = "Color-Preserving Bi-Histogram HE (HSV)"
                    formula_info = "V_new = BBHE(V_old) • RGB_new = RGB · (V_new / V_old)"
                    out_arr = color_histogram_equalization(np_rgb, method="bbhe")
                else:
                    clip_lim = float(params.get("clip_limit", 2.5))
                    algo_title = f"Color-Preserving CLAHE (Clip={clip_lim})"
                    formula_info = "V_new = CLAHE(V_old) • RGB_new = RGB · (V_new / V_old)"
                    out_arr = color_histogram_equalization(np_rgb, method="clahe", clip_limit=clip_lim)
                result_img_base64 = numpy_to_base64(out_arr)
            else:
                np_gray = np.array(input_img.convert("L"))
                if algo == "ghe":
                    algo_title = "Global Histogram Equalization (GHE)"
                    formula_info = "s_k = round( 255 · [CDF(r_k) - CDF_min] / [N - CDF_min] )"
                    out_arr = global_histogram_equalization(np_gray)
                    result_img_base64 = numpy_to_base64(out_arr)
                elif algo == "bbhe":
                    algo_title = "Brightness Preserving Bi-Histogram HE (BBHE)"
                    formula_info = "Split at mean μ: Equalize [0, μ] & [μ+1, 255] independently"
                    out_arr = bi_histogram_equalization(np_gray)
                    result_img_base64 = numpy_to_base64(out_arr)
                elif algo == "clahe":
                    clip_lim = float(params.get("clip_limit", 2.5))
                    algo_title = f"Contrast Limited Adaptive HE (CLAHE, Clip={clip_lim})"
                    formula_info = "Tile-Clipped CDF + Bilinear Interpolation (8x8 Tiles)"
                    out_arr = clahe(np_gray, clip_limit=clip_lim, tile_grid_size=(8, 8))
                    result_img_base64 = numpy_to_base64(out_arr)
                elif algo == "matching":
                    algo_title = "Histogram Matching (Specification)"
                    formula_info = "z = G^-1( T(r) ) with target linear ramp"
                    ramp_target = np.linspace(0, 255, 256, dtype=np.uint8)
                    out_arr = histogram_matching(np_gray, ramp_target)
                    result_img_base64 = numpy_to_base64(out_arr)
                else:
                    # Comparison grid
                    algo_title = "Histogram Equalization Comparison Grid"
                    formula_info = "Side-by-side comparison across GHE, BBHE, CLAHE, Matching"
                    eqs = {
                        "Global HE (GHE)": global_histogram_equalization(np_gray),
                        "Bi-Histogram Equalization (BBHE)": bi_histogram_equalization(np_gray),
                        "CLAHE (Adaptive Local)": clahe(np_gray, clip_limit=2.5, tile_grid_size=(8, 8)),
                        "Histogram Matching": histogram_matching(np_gray, np.linspace(0, 255, 256, dtype=np.uint8)),
                    }
                    grid = create_histogram_comparison_grid(input_img, eqs)
                    result_img_base64 = pil_to_base64(grid)
                    out_arr = eqs["CLAHE (Adaptive Local)"]

            stats = compute_image_statistics(out_arr if out_arr.ndim == 2 else np.array(Image.fromarray(out_arr).convert("L")))

        # ---------------------------------------------------------------------
        # TASK 5: 2D DISCRETE WAVELET TRANSFORM (DWT)
        # ---------------------------------------------------------------------
        elif task in ("task_5_wavelet_transform", "task_5_wavelet", "task_5"):
            np_gray = np.array(input_img.convert("L"))
            w_family = params.get("wavelet", "haar")
            coeffs = dwt2(np_gray, wavelet=w_family)
            ll, (lh, hl, hh) = coeffs

            if algo == "subband_ll":
                algo_title = f"LL Subband (Approximation, {w_family.upper()})"
                formula_info = "LL = (f * h0 · h0^T) ↓2 (Low Frequencies & Geometry)"
                out_arr = normalize_subband_for_display(ll, is_ll=True)
                result_img_base64 = numpy_to_base64(out_arr)
            elif algo == "subband_lh":
                algo_title = f"LH Subband (Horizontal Details, {w_family.upper()})"
                formula_info = "LH = (f * h0 · h1^T) ↓2 (Horizontal Edges)"
                out_arr = normalize_subband_for_display(lh, is_ll=False)
                result_img_base64 = numpy_to_base64(out_arr)
            elif algo == "subband_hl":
                algo_title = f"HL Subband (Vertical Details, {w_family.upper()})"
                formula_info = "HL = (f * h1 · h0^T) ↓2 (Vertical Edges)"
                out_arr = normalize_subband_for_display(hl, is_ll=False)
                result_img_base64 = numpy_to_base64(out_arr)
            elif algo == "subband_hh":
                algo_title = f"HH Subband (Diagonal Details, {w_family.upper()})"
                formula_info = "HH = (f * h1 · h1^T) ↓2 (Diagonal Textures & Noise)"
                out_arr = normalize_subband_for_display(hh, is_ll=False)
                result_img_base64 = numpy_to_base64(out_arr)
            elif algo == "multilevel_quadtree":
                lvl = int(params.get("level", 2))
                algo_title = f"Multi-Level Quadtree Mosaic (Level {lvl}, {w_family.upper()})"
                formula_info = "Recursive Dyadic 2D Quadtree Decomposition"
                m_coeffs = wavedec2(np_gray, wavelet=w_family, level=lvl)
                grid = create_multilevel_quadtree_image(m_coeffs)
                result_img_base64 = pil_to_base64(grid)
            elif algo == "compression_grid":
                algo_title = f"Wavelet Compression Benchmark ({w_family.upper()})"
                formula_info = "Thresholding detail coefficients (90%, 95%, 99% zeroed)"
                grid = create_wavelet_compression_grid(input_img, wavelet=w_family)
                result_img_base64 = pil_to_base64(grid)
            else:
                # 4-subband composite grid
                algo_title = f"4-Subband 2D DWT Decomposition Grid ({w_family.upper()})"
                formula_info = "LL1 (Approximation) + LH1 (Horiz) + HL1 (Vert) + HH1 (Diag)"
                grid = create_subband_decomposition_grid(input_img, coeffs, wavelet=w_family)
                result_img_base64 = pil_to_base64(grid)

            energy_stats = compute_wavelet_energy(coeffs)
            stats["subband_energies"] = energy_stats

    # Input image as base64 preview
    input_b64 = pil_to_base64(input_img)

    return jsonify({
        "success": True,
        "task": task,
        "algorithm": algo,
        "title": algo_title,
        "formula": formula_info,
        "input_image": input_b64,
        "output_image": result_img_base64,
        "extra_images": extra_images,
        "stats": stats,
        "telemetry": {
            "cpu_utilization_pct": round(profiler.cpu_utilization_pct, 2),
            "execution_time_ms": round(profiler.elapsed_ms, 2),
            "memory_rss_mb": round(profiler.memory_rss_mb, 2),
            "memory_delta_mb": round(profiler.memory_delta_mb, 3),
            "logical_cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "cpu_freq_mhz": round(psutil.cpu_freq().current, 1) if psutil.cpu_freq() else "N/A",
            "image_resolution": f"{orig_w} × {orig_h}",
            "color_mode": input_img.mode,
        }
    })


@app.route("/api/tambola/generate", methods=["GET"])
def generate_tambola_api():
    """Generates a Tambola ticket or 6-ticket strip with performance telemetry."""
    mode = request.args.get("mode", "single")
    profiler = PerformanceProfiler()

    with profiler:
        if mode == "strip":
            strip = generate_strip()
            ascii_rep = strip_to_ascii(strip)
            data = {"mode": "strip", "tickets": [t.to_dict() for t in strip.tickets], "ascii": ascii_rep}
        else:
            ticket = generate_ticket()
            ascii_rep = ticket_to_ascii(ticket)
            svg_str = ticket_to_svg(ticket)
            data = {"mode": "single", "ticket": ticket.to_dict(), "ascii": ascii_rep, "svg": svg_str}

    return jsonify({
        "success": True,
        "data": data,
        "telemetry": {
            "cpu_utilization_pct": round(profiler.cpu_utilization_pct, 2),
            "execution_time_ms": round(profiler.elapsed_ms, 2),
            "memory_rss_mb": round(profiler.memory_rss_mb, 2),
        }
    })


def main():
    parser = argparse.ArgumentParser(description="DIP Lab Tasks Interactive Flask App")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=5000, help="Port number")
    parser.add_argument("--test-mode", action="store_true", help="Run automated API self-test and exit")
    args = parser.parse_args()

    if args.test_mode:
        print("\n⚡ Running Flask Web App Self-Test...")
        with app.test_client() as client:
            # 1. Test index page
            res_idx = client.get("/")
            assert res_idx.status_code == 200
            print("  ✓ Index page responds (200 OK)")

            # 2. Test samples API
            res_samples = client.get("/api/sample-images")
            assert res_samples.status_code == 200
            print("  ✓ Sample images endpoint responds (200 OK)")

            # 3. Test Process API for Task 5 Wavelet
            res_dwt = client.post("/api/process", data={
                "task": "task_5_wavelet",
                "algorithm": "default",
                "sample_id": "iiitn_logo"
            })
            assert res_dwt.status_code == 200
            dwt_json = res_dwt.get_json()
            assert dwt_json["success"] is True
            assert "telemetry" in dwt_json
            assert "cpu_utilization_pct" in dwt_json["telemetry"]
            print(f"  ✓ Process API (Task 5 DWT) executed in {dwt_json['telemetry']['execution_time_ms']}ms with {dwt_json['telemetry']['cpu_utilization_pct']}% CPU utilization")

            # 4. Test Tambola API
            res_tam = client.get("/api/tambola/generate?mode=single")
            assert res_tam.status_code == 200
            print("  ✓ Tambola API responds (200 OK)")

        print("✨ All Web App self-tests passed successfully!\n")
        return

    print("=" * 70)
    print(f"🌐 Starting DIP Lab Tasks Interactive Dashboard on http://{args.host}:{args.port}")
    print("=" * 70)
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
