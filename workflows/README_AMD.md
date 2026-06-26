# LTX 2.3 IA2V Lip-Sync — AMD 설정 가이드 (한국어)

AMD RX 9060 XT 8GB에서 LTX 2.3 Image-to-Audio-Video 립싱크 워크플로우를 실행하는 방법입니다.

---

## 목차

1. [ComfyUI AMD Portable 설치](#1-comfyui-amd-portable-설치)
2. [자동 셋업 스크립트 실행](#2-자동-셋업-스크립트-실행)
3. [모델 파일 다운로드](#3-모델-파일-다운로드)
4. [ComfyUI 실행](#4-comfyui-실행)
5. [워크플로우 로드 및 실행](#5-워크플로우-로드-및-실행)
6. [트러블슈팅](#6-트러블슈팅)

---

## 1. ComfyUI AMD Portable 설치

> Python을 따로 설치할 필요가 없습니다. portable 버전에 Python이 내장되어 있습니다.

1. **링크 열기:** [ComfyUI AMD Portable 최신 버전 다운로드](https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_amd.7z)
2. **압축 풀기:**
   - [7-Zip](https://7-zip.org/)을 설치하세요 (Windows 기본 압축 풀기로도 가능)
   - `ComfyUI_windows_portable_amd.7z` 파일을 우클릭 → "압축 풀기"
   - 압축을 풀면 `ComfyUI_windows_portable` 폴더가 생성됩니다
   - **권장 위치:** `C:\ComfyUI_windows_portable\` (경로에 한글/공백이 없게)

3. **확인:** 폴더 안에 `ComfyUI/` 폴더가 있고, 그 안에 `main.py`가 있는지 확인하세요.

---

## 2. 자동 셋업 스크립트 실행

이 프로젝트에 포함된 `setup_comfyui_amd.bat`이 대부분의 셋업을 자동으로 처리합니다.

1. **스크립트 위치 확인:** `workflows/setup_comfyui_amd.bat`
2. **실행:** 더블클릭 (또는 명령 프롬프트에서 실행)
3. **스크립트가 하는 일:**
   - ComfyUI 폴더 자동 탐색 (없으면 직접 경로 입력)
   - 모델 폴더 생성 (`unet/`, `text_encoders/`, `vae/`, `loras/`, `checkpoints/`)
   - 커스텀 노드 자동 설치 (git clone):
     - **ComfyUI-Manager** — 노드 관리
     - **ComfyUI-GGUF** — GGUF 모델 로더
     - **CG-Use-Everywhere** — 와이어 자동 연결
     - **ComfyUI-KJNodes** — VAE 로더 등
     - **ComfyUI-VideoHelperSuite** — 비디오 출력
     - **rgthree-comfy** — 라벨 노드
   - Python 의존성 자동 설치
   - 워크플로우 JSON을 `web_custom_workflows/`로 복사

> **참고:** 만약 git 명령어가 없다면 [Git for Windows](https://git-scm.com/download/win)를 설치하세요.

---

## 3. 모델 파일 다운로드

아래 파일들을 다운로드해서 각각 지정된 폴더에 넣어야 합니다.

자세한 내용은 **`MODELS_NEEDED.md`** 파일을 참고하세요.

### 요약

| 파일 | 크기 | 저장 위치 |
|------|------|-----------|
| `ltx-2.3-22b-distilled-Q5_K_M.gguf` | 14.3 GB | `ComfyUI/models/unet/` |
| `gemma-3-12b-it-IQ4_XS.gguf` | 9.5 GB | `ComfyUI/models/text_encoders/` |
| `ltx-2.3_text_projection_bf16.safetensors` | 0.2 GB | `ComfyUI/models/text_encoders/` |
| `LTX23_video_vae_bf16.safetensors` | 1.2 GB | `ComfyUI/models/vae/` |
| `LTX23_audio_vae_bf16.safetensors` | 0.5 GB | `ComfyUI/models/checkpoints/` |
| `LTX-2.3-22b-AV-LoRA-talking-head-v1.safetensors` | 0.2 GB | `ComfyUI/models/loras/` |

**총 약 26 GB** 다운로드 필요합니다. 시간이 오래 걸리니 여유를 두고 진행하세요.

### 다운로드 팁

- **HuggingFace**에서 다운로드: 각 파일의 링크를 클릭하거나 `Download` 버튼을 누르세요
- **다운로드가 느리다면:** `hf_transfer`나 `aria2c`를 사용하거나, VPN을 켜보세요
- 각 파일을 **정확한 이름**으로 저장하세요 (일부 VAE 파일은 이름을 바꿔야 할 수 있음)

---

## 4. ComfyUI 실행

### AMD GPU 모드로 실행 (권장)

`ComfyUI_windows_portable` 폴더에서:

```
ComfyUI_windows_portable
├── ComfyUI/          ← ComfyUI 본체
├── python_embeded/   ← 내장 Python
├── run_nvidia_gpu.bat   ← (무시, NVIDIA 전용)
└── run_cpu.bat          ← (느림, 비상용)
```

**AMD용 실행 방법 1 — main.py 직접 실행:**

`ComfyUI/` 폴더로 이동한 후:
```batch
..\python_embeded\python.exe main.py --directml --dont-upcast-attention
```

**AMD용 실행 방법 2 — 배치 파일 만들기 (편의용):**

`ComfyUI_windows_portable/` 폴더에 `run_amd_gpu.bat` 파일을 만들고:
```batch
@echo off
cd /d "%~dp0ComfyUI"
..\python_embeded\python.exe main.py --directml --dont-upcast-attention
pause
```

> **중요:** `--directml` 플래그가 없으면 ComfyUI가 CUDA를 찾으려고 시도하고 실패합니다.

### 브라우저 열기

ComfyUI 실행 후 브라우저에서 `http://127.0.0.1:8188`을 엽니다.

---

## 5. 워크플로우 로드 및 실행

### 방법 A — Load 버튼 사용
1. ComfyUI 화면에서 **"Load"** 버튼 클릭
2. `workflows/LTX_2.3_IA2V_lip_Syncing.json` 파일 선택
3. 워크플로우가 로드됩니다

### 방법 B — 워크플로우 드래그
1. `LTX_2.3_IA2V_lip_Syncing.json` 파일을 ComfyUI 화면에 드래그 앤 드롭

### 워크플로우 구성

로드되면 다음과 같은 구조가 보입니다:

```
─────────────────────────────────────────────────────
[입력]                     [처리]                   [출력]
─────────────────────────────────────────────────────
LoadImage ──► LTXVCropGuides ──► SamplerCustomAdvanced ──► LTXVSeparateAVLatent
LoadAudio ──► TrimAudio         │                          ├──► VAEDecodeTiled ──► VHS_VideoCombine
            CLIPTextEncode ───► LTXVConditioning           └──► LTXVAudioVAE ──►
            UnetLoaderGGUF ──► LoraLoaderModelOnly         Decode
            (Q5_K_M.gguf)     (AV-LoRA talking-head)
            DualCLIPLoaderGGUF
            (gemma-3-12b + projection)
─────────────────────────────────────────────────────
```

### 실행 전 확인사항

1. **LoadImage 노드**: 자신의 입력 이미지 선택 (얼굴이 선명하게 보이는 사진)
2. **LoadAudio 노드**: 자신의 오디오 파일 선택 (말하기/노래 WAV 또는 MP3)
3. **VHS_VideoCombine 노드**: 출력 포맷 확인
   - `format`: `video/h264-amf-mp4` (AMD 하드웨어 인코딩)
   - 또는 `video/h264-mp4` (CPU 인코딩, 더 느림)
   - **절대** `video/nvenc_h264-mp4` 사용 금지 (NVIDIA 전용)

4. **Generate 클릭!** → Queue Prompt 버튼

### 실행 시간 예상

| 해상도 | 프레임 수 | RX 9060 XT 예상 시간 |
|--------|-----------|----------------------|
| 960x540 | 24프레임 (1초) | ~2-3분 |
| 512x512 | 24프레임 (1초) | ~1-2분 |
| 960x540 | 73프레임 (3초) | ~8-12분 |

---

## 6. 트러블슈팅

### "No module named 'torch_directml'"
- `ComfyUI_windows_portable_amd.7z` 버전을 사용했는지 확인하세요 (NVIDIA 버전 아님)
- AMD 버전이 맞다면: `python_embeded\python.exe -m pip install torch-directml --quiet`

### "CUDA error: no kernel image"
- `--directml` 플래그를 빼먹었습니다. 실행 명령어에 추가하세요.

### "OutOfMemory" / "CUDA out of memory"
- 모델 양자 수준 낮추기: Q5_K_M → Q4_K_M
- 이미지 크기 줄이기: 960x540 → 512x512
- 프레임 수 줄이기: 73 → 24
- `--dont-upcast-attention` 플래그 추가 (RX 9060 XT에 중요)

### "Could not find node type: UnetLoaderGGUF"
- ComfyUI-GGUF가 설치되지 않았습니다. `setup_comfyui_amd.bat`를 다시 실행하거나 수동 설치:
  ```batch
  cd ComfyUI/custom_nodes
  git clone https://github.com/iamkaijun/ComfyUI-GGUF.git
  ```

### VideoHelperSuite "ffmpeg not found"
- VideoHelperSuite가 ffmpeg를 자동 다운로드합니다. 실패하면 수동으로 ffmpeg를 설치하세요.
- [ffmpeg.org](https://ffmpeg.org/download.html)에서 다운로드, PATH에 추가

### "Error: The following models could not be found"
- 모델 파일이 정확한 폴더에 있는지 확인하세요 (MODELS_NEEDED.md 참고)
- 파일명이 정확한지 확인하세요 (대소문자 구분)

### VHS VideoCombine "Unknown encoder 'h264_amf'"
- AMD GPU 드라이버가 최신인지 확인 (Adrenalin 24.10.1 이상 권장)
- `format`을 `video/h264-mp4`로 변경 (CPU 인코딩)

---

## 폴더 구조 최종 확인

```
ComfyUI_windows_portable/
├── ComfyUI/
│   ├── main.py
│   ├── custom_nodes/
│   │   ├── ComfyUI-Manager/
│   │   ├── ComfyUI-GGUF/
│   │   ├── CG-Use-Everywhere/
│   │   ├── ComfyUI-KJNodes/
│   │   ├── ComfyUI-VideoHelperSuite/
│   │   └── rgthree-comfy/
│   ├── models/
│   │   ├── unet/
│   │   │   └── ltx-2.3-22b-distilled-Q5_K_M.gguf
│   │   ├── text_encoders/
│   │   │   ├── gemma-3-12b-it-IQ4_XS.gguf
│   │   │   └── ltx-2.3_text_projection_bf16.safetensors
│   │   ├── vae/
│   │   │   └── LTX23_video_vae_bf16.safetensors
│   │   ├── checkpoints/
│   │   │   └── LTX23_audio_vae_bf16.safetensors
│   │   └── loras/
│   │       └── LTX-2.3-22b-AV-LoRA-talking-head-v1.safetensors
│   └── web_custom_workflows/
│       └── LTX_2.3_IA2V_lip_Syncing.json
├── python_embeded/
├── run_amd_gpu.bat          ← 본인이 만들어야 함
└── run_nvidia_gpu.bat       ← 무시
```

---

## 참고 링크

| 항목 | 링크 |
|------|------|
| ComfyUI GitHub (공식) | https://github.com/comfyanonymous/ComfyUI |
| AMD Portable 다운로드 | https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_amd.7z |
| ComfyUI-GGUF | https://github.com/iamkaijun/ComfyUI-GGUF |
| CG-Use-Everywhere | https://github.com/chrisgoringe/CG-Use-Everywhere |
| ComfyUI-KJNodes | https://github.com/kijai/ComfyUI-KJNodes |
| VideoHelperSuite | https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite |
| LTX 2.3 GGUF 모델 | https://huggingface.co/unsloth/LTX-2.3-GGUF |
| elix3r AV-LoRA | https://huggingface.co/elix3r/LTX-2.3-22b-AV-LoRA-talking-head |
| ComfyUI-Manager | https://github.com/ltdrdata/ComfyUI-Manager |
