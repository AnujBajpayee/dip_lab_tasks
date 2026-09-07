/**
 * DIP Lab Workstation Interactive Client Application
 * Handles file uploads, preset selection, algorithm dispatch, and live telemetry rendering.
 */

document.addEventListener("DOMContentLoaded", () => {
  // State
  let currentTask = "task_5_wavelet";
  let currentSampleId = "iiitn_logo";
  let currentUploadedFile = null;

  // DOM Elements
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const presetBtns = document.querySelectorAll(".preset-btn");
  const taskTabBtns = document.querySelectorAll(".task-tab-btn");
  const runBtn = document.getElementById("run-btn");
  const dynamicControls = document.getElementById("dynamic-controls");
  const taskHeadline = document.getElementById("task-headline");
  const taskSubline = document.getElementById("task-subline");
  const formulaDisplay = document.getElementById("formula-display");
  const inputPreview = document.getElementById("input-preview");
  const outputPreview = document.getElementById("output-preview");
  const outputWrapper = document.getElementById("output-wrapper");
  const outputTitle = document.getElementById("output-title");
  const downloadBtn = document.getElementById("download-btn");
  const loadingOverlay = document.getElementById("loading-overlay");
  const tambolaContainer = document.getElementById("tambola-output-container");
  const metricsContainer = document.getElementById("metrics-table-container");

  // Telemetry HUD Elements
  const telemetryCpu = document.getElementById("telemetry-cpu");
  const telemetryCores = document.getElementById("telemetry-cores");
  const cpuProgressFill = document.getElementById("cpu-progress-fill");
  const telemetryTime = document.getElementById("telemetry-time");
  const telemetryRam = document.getElementById("telemetry-ram");
  const telemetryRamDelta = document.getElementById("telemetry-ram-delta");
  const telemetryRes = document.getElementById("telemetry-res");
  const telemetryMode = document.getElementById("telemetry-mode");
  const telemetryActiveTask = document.getElementById("telemetry-active-task");
  const inputTag = document.getElementById("input-tag");

  // =========================================================================
  // Task UI Configurations
  // =========================================================================
  const TASK_CONFIGS = {
    task_5_wavelet: {
      title: "Task 5: 2D Discrete Wavelet Transform (DWT)",
      subtitle: "Multi-resolution frequency decomposition, subband energy analysis, and compression.",
      defaultFormula: "LL = (f * h0 · h0^T) ↓2 • LH = (f * h0 · h1^T) ↓2 • HL = (f * h1 · h0^T) ↓2 • HH = (f * h1 · h1^T) ↓2",
      renderControls: () => `
        <div class="control-group">
          <label class="control-label">Algorithm / Subband</label>
          <select id="ctrl-algo" class="control-select">
            <option value="default" selected>4-Subband Decomposition Grid (LL, LH, HL, HH)</option>
            <option value="subband_ll">LL Subband (Coarse Approximation)</option>
            <option value="subband_lh">LH Subband (Horizontal Details)</option>
            <option value="subband_hl">HL Subband (Vertical Details)</option>
            <option value="subband_hh">HH Subband (Diagonal Textures)</option>
            <option value="multilevel_quadtree">Multi-Level Quadtree Mosaic</option>
            <option value="compression_grid">Wavelet Compression Benchmark Grid</option>
          </select>
        </div>
        <div class="control-group">
          <label class="control-label">Wavelet Family</label>
          <select id="ctrl-wavelet" class="control-select" style="min-width: 140px;">
            <option value="haar" selected>Haar (db1)</option>
            <option value="db2">Daubechies 2 (db2)</option>
          </select>
        </div>
        <div class="control-group">
          <label class="control-label">Decomposition Level</label>
          <select id="ctrl-level" class="control-select" style="min-width: 110px;">
            <option value="2" selected>Level 2</option>
            <option value="3">Level 3</option>
            <option value="1">Level 1</option>
          </select>
        </div>
      `
    },
    task_4_histogram: {
      title: "Task 4: Histogram Equalization Types & Execution",
      subtitle: "Non-linear spatial contrast enhancement across global, brightness-preserving, and adaptive methods.",
      defaultFormula: "s_k = round( [ (CDF(r_k) - CDF_min) / ((M·N) - CDF_min) ] · 255 )",
      renderControls: () => `
        <div class="control-group">
          <label class="control-label">Equalization Method</label>
          <select id="ctrl-algo" class="control-select">
            <option value="default" selected>All Methods Comparison Grid</option>
            <option value="ghe">Global Histogram Equalization (GHE)</option>
            <option value="bbhe">Bi-Histogram Equalization (BBHE, Mean Preserved)</option>
            <option value="clahe">Contrast Limited Adaptive HE (CLAHE)</option>
            <option value="color_clahe">Color HSV Value-Channel CLAHE</option>
            <option value="matching">Histogram Matching (Specification)</option>
          </select>
        </div>
        <div class="control-group">
          <label class="control-label">CLAHE Clip Limit</label>
          <select id="ctrl-clip" class="control-select" style="min-width: 120px;">
            <option value="2.5" selected>2.5 (Balanced)</option>
            <option value="1.5">1.5 (Mild)</option>
            <option value="4.0">4.0 (Aggressive)</option>
          </select>
        </div>
      `
    },
    task_3_bit_plane: {
      title: "Task 3: 8-Bit Plane Slicing & Digital Steganography",
      subtitle: "Decomposes 8-bit monochromatic images into binary matrices and embeds hidden watermarks.",
      defaultFormula: "b_k = (f(x, y) >> k) & 1 for k ∈ [0, 7] • f(x, y) = sum_{k=0}^7 2^k · b_k",
      renderControls: () => `
        <div class="control-group">
          <label class="control-label">Operation Mode</label>
          <select id="ctrl-algo" class="control-select">
            <option value="default" selected>9-Panel Bit-Plane Decomposition Grid</option>
            <option value="progressive_reconstruction">Cumulative MSB Reconstruction Grid</option>
            <option value="steganography">LSB Digital Watermarking / Steganography</option>
            <option value="plane_7">Bit-Plane 7 (MSB - Highest Energy)</option>
            <option value="plane_6">Bit-Plane 6</option>
            <option value="plane_5">Bit-Plane 5</option>
            <option value="plane_4">Bit-Plane 4</option>
            <option value="plane_3">Bit-Plane 3</option>
            <option value="plane_2">Bit-Plane 2</option>
            <option value="plane_1">Bit-Plane 1</option>
            <option value="plane_0">Bit-Plane 0 (LSB - Fine Noise)</option>
          </select>
        </div>
        <div class="control-group" id="stego-text-group">
          <label class="control-label">Watermark Secret Label</label>
          <input type="text" id="ctrl-wm-text" class="control-input" value="IIIT NAGPUR 2026" placeholder="Enter watermark text...">
        </div>
      `
    },
    task_2_grayscale: {
      title: "Task 2: Standard RGB to Greyscale Image Conversion",
      subtitle: "Trichromatic color to single-channel intensity conversion based on human visual perception.",
      defaultFormula: "Y = 0.299·R + 0.587·G + 0.114·B (ITU-R BT.601 Photopic Efficiency)",
      renderControls: () => `
        <div class="control-group">
          <label class="control-label">Photometric Algorithm</label>
          <select id="ctrl-algo" class="control-select">
            <option value="default" selected>9-Panel Comparison Benchmark Grid</option>
            <option value="rec601">ITU-R BT.601 Luminosity (0.299R + 0.587G + 0.114B)</option>
            <option value="rec709">ITU-R BT.709 / sRGB (0.2126R + 0.7152G + 0.0722B)</option>
            <option value="average">Simple Average (R+G+B)/3</option>
            <option value="lightness">HSL Lightness (max+min)/2</option>
            <option value="gamma">Linear Gamma-Corrected (γ=2.2)</option>
            <option value="channel_red">Red Channel Extraction</option>
            <option value="channel_green">Green Channel Extraction</option>
            <option value="channel_blue">Blue Channel Extraction</option>
          </select>
        </div>
      `
    },
    task_1_tambola: {
      title: "Task 1: Tambola (Housie) Ticket Generator & CSP Engine",
      subtitle: "Generates valid 3×9 tickets (15 numbers, 5 per row) and full 6-ticket strips (numbers 1-90).",
      defaultFormula: "CSP Engine: 15 numbers per ticket • 5 numbers per row • Ascending column decades",
      renderControls: () => `
        <div class="control-group">
          <label class="control-label">Generation Mode</label>
          <select id="ctrl-algo" class="control-select">
            <option value="single" selected>Generate Single Tambola Ticket</option>
            <option value="strip">Generate Full 6-Ticket Strip (All 90 Numbers)</option>
          </select>
        </div>
      `
    }
  };

  // =========================================================================
  // Initialize UI & Task Switcher
  // =========================================================================
  function setTask(taskKey) {
    currentTask = taskKey;
    const cfg = TASK_CONFIGS[taskKey];
    taskHeadline.textContent = cfg.title;
    taskSubline.textContent = cfg.subtitle;
    formulaDisplay.textContent = cfg.defaultFormula;
    dynamicControls.innerHTML = cfg.renderControls();

    taskTabBtns.forEach(btn => {
      btn.classList.toggle("active", btn.dataset.task === taskKey);
    });

    telemetryActiveTask.textContent = cfg.title.split(":")[0];

    // Trigger process
    executeProcessing();
  }

  // =========================================================================
  // Event Listeners: Task Tabs & Presets
  // =========================================================================
  taskTabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      setTask(btn.dataset.task);
    });
  });

  presetBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      presetBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentSampleId = btn.dataset.sample;
      currentUploadedFile = null;
      executeProcessing();
    });
  });

  // Drag and Drop Upload
  dropZone.addEventListener("click", () => fileInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    currentUploadedFile = file;
    currentSampleId = "";
    presetBtns.forEach(b => b.classList.remove("active"));
    
    // Preview original
    const reader = new FileReader();
    reader.onload = (ev) => {
      inputPreview.src = ev.target.result;
    };
    reader.readAsDataURL(file);

    executeProcessing();
  }

  runBtn.addEventListener("click", () => {
    executeProcessing();
  });

  // =========================================================================
  // Main Dispatch & Telemetry Processing
  // =========================================================================
  async function executeProcessing() {
    loadingOverlay.classList.add("active");

    if (currentTask === "task_1_tambola") {
      // Execute Tambola API
      const algoSelect = document.getElementById("ctrl-algo");
      const mode = algoSelect ? algoSelect.value : "single";
      try {
        const res = await fetch(`/api/tambola/generate?mode=${mode}`);
        const data = await res.json();
        updateTambolaOutput(data);
      } catch (err) {
        console.error("Tambola generation failed:", err);
      } finally {
        loadingOverlay.classList.remove("active");
      }
      return;
    }

    // Standard Image Tasks (T2, T3, T4, T5)
    outputPreview.style.display = "block";
    tambolaContainer.className = "tambola-output-hidden";

    const formData = new FormData();
    formData.append("task", currentTask);

    const algoSelect = document.getElementById("ctrl-algo");
    if (algoSelect) {
      formData.append("algorithm", algoSelect.value);
    }

    const params = {};
    const waveletSelect = document.getElementById("ctrl-wavelet");
    if (waveletSelect) params.wavelet = waveletSelect.value;

    const levelSelect = document.getElementById("ctrl-level");
    if (levelSelect) params.level = parseInt(levelSelect.value, 10);

    const clipSelect = document.getElementById("ctrl-clip");
    if (clipSelect) params.clip_limit = parseFloat(clipSelect.value);

    const wmInput = document.getElementById("ctrl-wm-text");
    if (wmInput) params.watermark_text = wmInput.value;

    formData.append("params", JSON.stringify(params));

    if (currentUploadedFile) {
      formData.append("image", currentUploadedFile);
    } else {
      formData.append("sample_id", currentSampleId);
    }

    try {
      const response = await fetch("/api/process", {
        method: "POST",
        body: formData
      });
      const result = await response.json();
      if (result.success) {
        renderResults(result);
      }
    } catch (error) {
      console.error("Processing failed:", error);
    } finally {
      loadingOverlay.classList.remove("active");
    }
  }

  // =========================================================================
  // Render Telemetry & UI
  // =========================================================================
  function renderResults(result) {
    // 1. Update Preview Images
    if (result.input_image) {
      inputPreview.src = result.input_image;
    }
    if (result.output_image) {
      outputPreview.src = result.output_image;
      downloadBtn.href = result.output_image;
    }

    outputTitle.textContent = result.title || "Processed Output";
    if (result.formula) {
      formulaDisplay.textContent = result.formula;
    }

    // 2. Update Live Telemetry HUD
    const t = result.telemetry || {};
    const cpuPct = t.cpu_utilization_pct || 0.0;
    telemetryCpu.textContent = `${cpuPct.toFixed(1)}%`;
    telemetryCores.textContent = `${t.logical_cores || "--"} Logical Cores`;
    cpuProgressFill.style.width = `${Math.min(100, Math.max(5, cpuPct))}%`;

    telemetryTime.textContent = `${(t.execution_time_ms || 0).toFixed(1)} ms`;
    telemetryRam.textContent = `${(t.memory_rss_mb || 0).toFixed(1)} MB`;
    telemetryRamDelta.textContent = `Δ ${(t.memory_delta_mb >= 0 ? "+" : "")}${(t.memory_delta_mb || 0).toFixed(2)} MB`;

    telemetryRes.textContent = t.image_resolution || "640 × 640";
    telemetryMode.textContent = t.color_mode || "RGB";
    inputTag.textContent = `Resolution: ${t.image_resolution || "640 × 640"}`;

    // 3. Render Metrics Table
    renderMetricsTable(result);
  }

  function renderMetricsTable(result) {
    const stats = result.stats || {};
    let html = '<table class="metrics-table"><thead><tr><th>Metric Property</th><th>Computed Value</th><th>Diagnostic Note</th></tr></thead><tbody>';

    if (stats.mean !== undefined) {
      html += `<tr><td>Mean Intensity (μ)</td><td class="highlight-val">${stats.mean.toFixed(2)}</td><td>Average pixel brightness level</td></tr>`;
      html += `<tr><td>Standard Deviation (σ)</td><td class="highlight-val">${stats.std_dev.toFixed(2)}</td><td>Contrast dynamic spread</td></tr>`;
      html += `<tr><td>Dynamic Intensity Range</td><td class="highlight-val">[${stats.min}, ${stats.max}]</td><td>Extreme gray level bounds</td></tr>`;
      html += `<tr><td>Shannon Entropy (H)</td><td class="highlight-val">${stats.entropy.toFixed(4)} bits/pixel</td><td>Information content density</td></tr>`;
    }

    if (stats.Stego_PSNR_dB !== undefined) {
      html += `<tr><td>Steganography PSNR</td><td class="highlight-val">${stats.Stego_PSNR_dB} dB</td><td>Imperceptibility metric (>50 dB = invisible)</td></tr>`;
      html += `<tr><td>Steganography MSE</td><td class="highlight-val">${stats.Stego_MSE}</td><td>Mean Squared Reconstruction Error</td></tr>`;
    }

    if (stats.subband_energies) {
      for (const [k, v] of Object.entries(stats.subband_energies)) {
        html += `<tr><td>${v.name}</td><td class="highlight-val">${v.energy_pct}%</td><td>${v.role}</td></tr>`;
      }
    }

    html += '</tbody></table>';
    metricsContainer.innerHTML = html;
  }

  function updateTambolaOutput(res) {
    outputPreview.style.display = "none";
    tambolaContainer.className = "tambola-output-visible";
    tambolaContainer.textContent = res.data.ascii || "Generated Tambola Ticket";

    const t = res.telemetry || {};
    telemetryCpu.textContent = `${(t.cpu_utilization_pct || 0).toFixed(1)}%`;
    telemetryTime.textContent = `${(t.execution_time_ms || 0).toFixed(1)} ms`;
    telemetryRam.textContent = `${(t.memory_rss_mb || 0).toFixed(1)} MB`;
    cpuProgressFill.style.width = "15%";

    formulaDisplay.textContent = "Exact CSP Bipartite Matching: O(1) Deterministic Ticket Construction";
    metricsContainer.innerHTML = '<div style="font-size:12px; color:#94a3b8;">Constraint Satisfaction Solved: 15 unique numbers, 5 per row, ascending decade columns.</div>';
  }

  // Initial load
  setTask("task_5_wavelet");
});
