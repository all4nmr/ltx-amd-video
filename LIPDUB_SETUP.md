# LTX-2.3 LipDub Pipeline — Two-stage lip-sync with IC-LoRA

This module wraps the LTX-2.3 LipDub IC-LoRA for use without ComfyUI.
Optimized for 8GB VRAM via GGUF quantized models + CPU offloading.

## Files Required

```
models/
├── ltx-2.3-22b-distilled_Q4_K_M.gguf    # Main model (GGUF, ~12GB disk / ~5GB VRAM)
├── ltx-2.3-spatial-upscaler-x2-1.0.safetensors  # Upscaler
└── loras/
    └── ltx-2.3-22b-ic-lora-lipdub-0.9.safetensors  # LipDub LoRA
```

Gemma 3 text encoder uses GGUF variant (~6.14 GB VRAM at load, ~3.6 GB after offload).

## 8GB VRAM Settings

| Setting | Value |
|---------|-------|
| Resolution | 640×360 (start), upscale later |
| Frame count | 65 (8k+1, ~2.5s) |
| Model | Distilled Q4_K_M GGUF |
| Text encoder | Gemma 3 GGUF |
| Offload | Enabled (CPU for text encoder after encode) |
| Preview | `--preview-method none` |
| Cache | `--cache-lru 10` |

## Pipeline Flow

1. Load distilled GGUF model (VRAM: ~5GB)
2. Load Gemma GGUF → encode prompt → offload to CPU
3. Load LipDub LoRA → fuse into model
4. Load driving video → extract frames + audio
5. Audio VAE encode → append audio reference tokens
6. Stage 1: Low-res diffusion (640×360, ~6GB VRAM)
7. Upscale with spatial upscaler
8. Stage 2: Refine at target resolution (audio frozen)
9. Decode video + audio → save MP4

## Usage

```python
from lipdub_pipeline import LipDubPipeline

pipeline = LipDubPipeline(
    model_path="models/ltx-2.3-22b-distilled_Q4_K_M.gguf",
    lora_path="models/loras/ltx-2.3-22b-ic-lora-lipdub-0.9.safetensors",
    device="directml",  # or "cuda"
    low_vram=True,
)

result = pipeline(
    prompt="A person speaking naturally",
    driving_audio="speech.wav",
    reference_image="portrait.jpg",
    width=640,
    height=360,
    num_frames=65,
)
```
