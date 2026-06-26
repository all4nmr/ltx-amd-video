# 모델 파일 다운로드 목록 (MODELS NEEDED)

이 워크플로우를 실행하려면 아래 모델 파일들을 다운로드하여 ComfyUI/models/ 아래 지정된 폴더에 넣어야 합니다.

---

## 1. 메인 UNet 모델 (필수)

| 항목 | 내용 |
|------|------|
| **파일명** | `ltx-2.3-22b-distilled-Q5_K_M.gguf` |
| **크기** | ~14.3 GB |
| **저장 위치** | `ComfyUI/models/unet/` |
| **다운로드** | [HuggingFace - unsloth/LTX-2.3-GGUF](https://huggingface.co/unsloth/LTX-2.3-GGUF/resolve/main/distilled/ltx-2.3-22b-distilled-Q5_K_M.gguf?download=true) |
| **대체 (Q4_K_M)** | [ltx-2.3-22b-distilled-UD-Q4_K_M.gguf](https://huggingface.co/unsloth/LTX-2.3-GGUF/resolve/main/distilled/ltx-2.3-22b-distilled-UD-Q4_K_M.gguf?download=true) (~15.1 GB, 같은 quant 수준) |

> **참고:** VRAM 8GB 기준 Q5_K_M 권장. Q4_K_M으로 낮추면 VRAM 사용량이 줄어듭니다.
> VRAM이 부족하면 Q4_K_M을 사용하세요. Q5_K_M은 8GB RX 9060 XT에서 약간 빡빡할 수 있습니다.

---

## 2. 텍스트 인코더 (필수)

| 항목 | 내용 |
|------|------|
| **파일명** | `gemma-3-12b-it-IQ4_XS.gguf` |
| **크기** | ~9.5 GB |
| **저장 위치** | `ComfyUI/models/text_encoders/` |
| **다운로드** | [HuggingFace - unsloth/gemma-3-12b-it-GGUF](https://huggingface.co/unsloth/gemma-3-12b-it-GGUF/resolve/main/gemma-3-12b-it-IQ4_XS.gguf?download=true) |

---

## 3. 텍스트 프로젝션 (필수)

| 항목 | 내용 |
|------|------|
| **파일명** | `ltx-2.3_text_projection_bf16.safetensors` |
| **크기** | **2.31 GB** |
| **저장 위치** | `ComfyUI/models/text_encoders/` |
| **다운로드** | [HuggingFace - Kijai/LTX2.3_comfy](https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/text_encoders/ltx-2.3_text_projection_bf16.safetensors?download=true) |

---

## 4. 비디오 VAE (필수)

| 항목 | 내용 |
|------|------|
| **파일명** | `LTX23_video_vae_bf16.safetensors` |
| **크기** | ~1.2 GB |
| **저장 위치** | `ComfyUI/models/vae/` |
| **다운로드** | [HuggingFace - Kijai/LTX2.3_comfy](https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/vae/LTX23_video_vae_bf16.safetensors?download=true) |
| **대체 (HF 원본)** | [unsloth/LTX-2.3-GGUF - vae](https://huggingface.co/unsloth/LTX-2.3-GGUF/resolve/main/vae/ltx-2.3-22b-distilled_video_vae.safetensors?download=true) |

---

## 5. 오디오 VAE (필수)

| 항목 | 내용 |
|------|------|
| **파일명** | `LTX23_audio_vae_bf16.safetensors` |
| **크기** | ~0.5 GB |
| **저장 위치** | `ComfyUI/models/checkpoints/` |
| **다운로드** | [HuggingFace - Kijai/LTX2.3_comfy](https://huggingface.co/Kijai/LTX2.3_comfy/resolve/main/checkpoints/LTX23_audio_vae_bf16.safetensors?download=true) |
| **대체 (HF 원본)** | [unsloth/LTX-2.3-GGUF - audio vae](https://huggingface.co/unsloth/LTX-2.3-GGUF/resolve/main/vae/ltx-2.3-22b-distilled_audio_vae.safetensors?download=true) |

---

## 6. LoRA — Talking Head (필수 - 립싱크)

| 항목 | 내용 |
|------|------|
| **파일명** | `LTX-2.3-22b-AV-LoRA-talking-head-v1.safetensors` |
| **크기** | ~0.2 GB |
| **저장 위치** | `ComfyUI/models/loras/` |
| **다운로드** | [HuggingFace - elix3r/LTX-2.3-22b-AV-LoRA-talking-head](https://huggingface.co/elix3r/LTX-2.3-22b-AV-LoRA-talking-head/resolve/main/LTX-2.3-22b-AV-LoRA-talking-head-v1.safetensors?download=true) |

---

## 최종 폴더 구조

다운로드 완료 후 `ComfyUI/models/` 아래가 다음과 같이 되어 있어야 합니다:

```
ComfyUI/models/
├── unet/
│   └── ltx-2.3-22b-distilled-Q5_K_M.gguf              (14.3 GB)
├── text_encoders/
│   ├── gemma-3-12b-it-IQ4_XS.gguf                     (9.5 GB)
│   └── ltx-2.3_text_projection_bf16.safetensors        (0.2 GB)
├── vae/
│   └── LTX23_video_vae_bf16.safetensors                (1.2 GB)
├── checkpoints/
│   └── LTX23_audio_vae_bf16.safetensors                (0.5 GB)
└── loras/
    └── LTX-2.3-22b-AV-LoRA-talking-head-v1.safetensors (0.2 GB)
```

**총 다운로드 용량: ~26 GB**
**총 디스크 사용량: ~26 GB**

---

## 참고: VRAM 사용량 가이드

| 모델 양자 | 예상 VRAM | RX 9060 XT 8GB |
|-----------|-----------|----------------|
| Q5_K_M (권장) | ~7.2 GB | ✅ 가능 (약간 여유) |
| Q4_K_M (안전) | ~6.5 GB | ✅ 여유 있음 |
| Q3_K_M (저사양) | ~5.5 GB | ✅ 넉넉함 |

**팁:** VRAM이 부족하면 512x512 낮은 해상도로 시작하고, 이미지 크기를 960x540으로 올려보세요.
