# LTX-2 AMD Video — Windows Setup Guide

> **Target:** Windows 11 + AMD Radeon RX 9060 XT (8 GB VRAM) + 32 GB RAM
>
> **Python NOT required for end users** — download the pre-built EXE from Releases.
> This guide is for developers who want to build from source.

---

## 📦 Quick Start (End User)

1. Go to **Releases** on GitHub
2. Download `LTX-AmD-Video-Windows.zip`
3. Extract and run `LTX-AmD-Video.exe`
4. Click **Browse** to select your models folder
5. Click **Generate Video**

---

## 🔧 Build from Source (Developer)

### Prerequisites

| Item | Version | Notes |
|------|---------|-------|
| Windows 11 | 23H2+ | Required for AMD DirectML |
| Python | 3.12.8 | Recommended (3.10–3.12 works) |
| Git | Latest | |
| AMD Driver | Adrenalin 24.6.1+ | DirectML support required |
| Vulkan SDK | Optional | Only for GGML models |

### Step 1 — Clone

```cmd
git clone https://github.com/all4nmr/ltx-amd-video.git
cd ltx-amd-video
```

### Step 2 — Python Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install PyTorch (CPU first, then DirectML)

```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install torch-directml
```

### Step 4 — Install LTX-2 Packages

```cmd
pip install -e packages\ltx-pipelines
pip install -e packages\ltx-core
```

### Step 5 — Install GUI Dependencies

```cmd
pip install gradio tk
```

### Step 6 — Download Models

Create a `models\` folder and download:

| File | Source | Size |
|------|--------|------|
| `ltx-2.3-22b-dev.safetensors` | [Lightricks/LTX-2.3](https://huggingface.co/Lightricks/LTX-2.3) | ~22 GB (FP8: ~12 GB) |
| `ltx-2.3-spatial-upscaler-x2-1.0.safetensors` | [Lightricks/LTX-2.3](https://huggingface.co/Lightricks/LTX-2.3) | ~1 GB |
| Gemma 3 12B IT (FP4) | [Comfy-Org/ltx-2](https://huggingface.co/Comfy-Org/ltx-2/tree/main/split_files/text_encoders) | ~9.5 GB |

> **8 GB VRAM tip:** Use the GGUF Q4 variant (ltx-2-19b-distilled_Q4_K_M.gguf, ~12 GB on disk but only ~5 GB VRAM at inference).

### Step 7 — Apply DirectML Patches

```cmd
python apply_directml_patches.py
```

### Step 8 — Launch GUI

```cmd
python rooster_gui.py --device directml
```

Or with the Gradio Web UI:

```cmd
python web_ui_v4.py
```

---

## 📁 Project Structure

```
ltx-amd-video/
├── helpers.py                  # Device detection (DirectML/CUDA)
├── rooster_gui.py              # Native Tkinter GUI (737 lines)
├── apply_directml_patches.py   # Auto-patcher (35 patch points)
├── SETUP_WINDOWS.md            # This file
├── web_ui_v2.py                # Gradio Web UI v2 (original)
├── web_ui_v4.py                # Gradio Web UI v4 (original)
├── music_maker_ui.py           # Music-to-Video UI (original)
├── film_maker_ui_v4.py         # CinemaMaker UI (original)
├── packages/
│   ├── ltx-core/               # Core LTX-2 model code
│   └── ltx-pipelines/          # Inference pipelines
├── models/                     # 📁 Create this folder (not tracked)
│   ├── ltx-2.3-22b-dev.safetensors
│   ├── ltx-2.3-spatial-upscaler-x2-1.0.safetensors
│   └── gemma3/                 # Text encoder
├── output/                     # Generated videos
└── .github/workflows/
    └── build.yml               # GitHub Actions → Windows EXE
```

---

## 🎬 Usage

### Native GUI (Recommended)

```cmd
python rooster_gui.py --device directml
```

Features:
- Device selection: Auto / CUDA / DirectML / CPU
- File picker for models folder, input image, output folder
- Duration slider (1–120 seconds)
- Auto 30-second segment splitting + stitching
- Progress bar + status log
- Cancel button

### CLI Mode

```cmd
python rooster_gui.py --device directml
```

### Gradio Web UI

```cmd
python web_ui_v4.py
```
Then open http://localhost:7860 in your browser.

---

## ⚙️ 8 GB VRAM Settings

For AMD RX 9060 XT (8 GB):

| Setting | Value |
|---------|-------|
| Resolution | 1280 × 704 (Safe Mode) |
| Max Frames | 257 (~10 s @ 25 fps) |
| Steps | 8 |
| CFG | 1.0 |
| FPS | 25 |
| Preview Method | None (`--preview-method none`) |

For longer videos, the **SegmentManager** automatically splits into segments.

---

## 🧪 Performance Estimates

| Resolution | Frames | Time (8 GB AMD) |
|------------|--------|-----------------|
| 640 × 360 | 257 | ~5 min |
| 1280 × 704 | 257 | ~7 min |
| 1536 × 1024 | 185 | ~8 min |
| 1920 × 1088 | 121 | ~10 min |

*(Estimates based on RTX 3070 Ti laptop benchmarks; AMD DirectML may be 1.5–3× slower.)*

---

## 🏗️ Build EXE

```cmd
pyinstaller --onefile --windowed ^
  --add-data "models;models" ^
  --add-data "packages;packages" ^
  --hidden-import torch_directml ^
  --name "LTX-AmD-Video" ^
  rooster_gui.py
```

Or use GitHub Actions: push to `main` → automatic build → downloadable artifact.

---

## ❗ Known Issues

- **DirectML on Windows**: ~1.5–3× slower than CUDA on equivalent NVIDIA hardware.
- **Korean input in cmd**: Run `chcp 65001` before Python commands (CP949 encoding issue).
- **OOM at high resolution**: Use Safe Mode presets (1280 × 704 max).
- **No audio in GUI**: Audio generation is supported via `music_maker_ui.py` (Gradio UI).
