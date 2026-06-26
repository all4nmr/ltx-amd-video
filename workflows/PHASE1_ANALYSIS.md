# LTX 2.3 IA2V Lip-Sync Workflow — Phase 1 분석 결과

## 1. 필요한 커스텀 노드 (ComfyUI Custom Nodes)

| 노드 타입 | 소스 | 개수 | 설명 |
|-----------|------|------|------|
| `UnetLoaderGGUF` | **ComfyUI-GGUF** | 1 | 메인 GGUF 모델 로더 (Q5_K_M) |
| `DualCLIPLoaderGGUF` | **ComfyUI-GGUF** | 1 | GGUF 텍스트 인코더 로더 (Gemma 3 12B) |
| `Anything Everywhere` | **CG-Use-Everywhere** | 2 | 모델/CLIP/VAE 자동 라우팅 |
| `VAELoaderKJ` | **ComfyUI-KJNodes** | 1 | 비디오 VAE 로더 |
| `DiffusionModelLoaderKJ` | **ComfyUI-KJNodes** | 1 | FP8 모델 로더 (현재 미연결 — GGUF가 활성 경로) |
| `VHS_VideoCombine` | **ComfyUI-VideoHelperSuite** | 1 | 비디오/오디오 합성 출력 |
| `Label (rgthree)` | **rgthree-comfy** | 1 | 라벨 노드 (없어도 작동) |

### 빌트인 노드 (추가 설치 불필요)
`LTXVAudioVAELoader`, `LTXVAudioVAEDecode`, `LTXVConditioning`, `LTXVSeparateAVLatent`, `LTXVCropGuides`, `LoadAudio`, `LoadImage`, `CLIPTextEncode` (x2), `LoraLoaderModelOnly`, `VAEDecodeTiled`, `SamplerCustomAdvanced`, `RandomNoise`, `KSamplerSelect`, `ManualSigmas`, `CFGGuider`, `ComfyMathExpression`, `PrimitiveInt` (x3), `PrimitiveFloat`, `TrimAudioDuration`, `RecordAudio`, `Reroute`, `MarkdownNote`, `07d8e67d-572c-4680-85cd-1d5cac0ab295` (커스텀 ID 노드 x2)

## 2. 필요한 모델 파일

| # | 파일명 | 노드 | 저장 폴더 | 비고 |
|---|--------|------|-----------|------|
| 1 | `ltx-2.3-22b-distilled-Q5_K_M.gguf` | UnetLoaderGGUF (448) | `ComfyUI/models/unet/` | ~14.3 GB (Q5_K_M distilled) |
| 2 | `gemma-3-12b-it-IQ4_XS.gguf` | DualCLIPLoaderGGUF (397) | `ComfyUI/models/text_encoders/` | ~9.5 GB |
| 3 | `ltx-2.3_text_projection_bf16.safetensors` | DualCLIPLoaderGGUF (397) | `ComfyUI/models/text_encoders/` | ~0.2 GB |
| 4 | `LTX23_video_vae_bf16.safetensors` | VAELoaderKJ (399) | `ComfyUI/models/vae/` | ~1.2 GB |
| 5 | `LTX23_audio_vae_bf16.safetensors` | LTXVAudioVAELoader (370) | `ComfyUI/models/checkpoints/` | ~0.5 GB |
| 6 | `LTX-2.3-22b-AV-LoRA-talking-head-v1.safetensors` | LoraLoaderModelOnly (446) | `ComfyUI/models/loras/` | ~0.2 GB (elix3r AV-LoRA) |

### 입력 파일 (사용자 제공)
| 파일 | 노드 | 설명 |
|------|------|------|
| `*.png` | LoadImage (269) | 입력 이미지 (얼굴 사진) |
| `S4.mp3` | LoadAudio (276) | 입력 오디오 파일 (원하는 음성/노래) |

## 3. GGUF 교체 분석

**이미 GGUF 기반으로 구성되어 있습니다.** 현재 워크플로우는:

- **UnetLoaderGGUF (448)** 가 `ltx-2.3-22b-distilled-Q5_K_M.gguf` 를 로드 → 활성 경로
- **DiffusionModelLoaderKJ (396)** 가 FP8 safetensors (`ltx-2.3-22b-distilled_transformer_only_fp8_input_scaled_v3.safetensors`)를 로드하지만 **연결이 끊어져 있음** (미사용)
- **DualCLIPLoaderGGUF (397)** 가 GGUF 텍스트 인코더 사용

→ GGUF로의 추가 교체 불필요. 이미 최적화되어 있습니다.

## 4. AMD DirectML 호환성

### 문제점 있음 ⚠️

| 이슈 | 설명 | 해결 |
|------|------|------|
| **VHS_VideoCombine NVENC** | `video/nvenc_h264-mp4` 사용 — NVIDIA NVENC 전용, AMD GPU에서 작동 불가 | `video/h264-mp4` (CPU) 또는 `video/h264-amf-mp4` (AMD AMF)로 변경 필요 |
| **VAEDecodeTiled** | 특별한 CUDA 의존성 없음 → DirectML에서 정상 작동 |
| **ComfyUI-GGUF** | llama.cpp 기반 → DirectML에서도 정상 작동 |
| **LTXV 노드들** | ComfyUI 빌트인 → DirectML 지원 |

### 권장 조치
1. VHS_VideoCombine의 format을 `video/h264-amf-mp4`로 변경 (AMD 하드웨어 인코딩)
2. 또는 `video/h264-mp4`로 변경 (CPU 소프트웨어 인코딩, 더 느리지만 호환성 최고)

---

## 워크플로우 데이터 흐름 요약

```
[UnetLoaderGGUF] ──MODEL──→ [LoraLoaderModelOnly] ──MODEL──→ [Anything Everywhere]
ltx-2.3-22b-distilled-Q5_K_M.gguf      + AV-LoRA (strength 0.88)

[DualCLIPLoaderGGUF] ──CLIP──→ [Anything Everywhere]
gemma-3-12b-it-IQ4_XS.gguf + projection

[CLIPTextEncode] ──COND──→ [LTXVConditioning] ──→ [CFGGuider] ──→ [SamplerCustomAdvanced]
(positive prompt + negative prompt)              + [ManualSigmas]  + [RandomNoise]

[VAELoaderKJ] ──VAE──→ [VAEDecodeTiled] ──IMAGE──→ [VHS_VideoCombine]
LTX23_video_vae_bf16.safetensors                    format: h264-amf-mp4

[LTXVAudioVAELoader] ──VAE──→ [LTXVAudioVAEDecode] ──AUDIO──→ [VHS_VideoCombine]
LTX23_audio_vae_bf16.safetensors

[LoadImage] ──IMAGE──→ [LTXVCropGuides] (latent 공간으로)
[LoadAudio] ──AUDIO──→ [TrimAudioDuration] → [LTXVAudioVAEEncode] → [LTXVCropGuides]
```

**결론**: 이 워크플로우는 이미 GGUF에 최적화되어 있으며, VHS Video Combine의 출력 포맷만 AMD 호환으로 변경하면 AMD RX 9060 XT에서 구동 가능합니다.
