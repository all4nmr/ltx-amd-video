@echo off
title LTX 2.3 AMD GGUF Auto Setup
chcp 65001 >nul
color 0A

echo ============================================
echo   LTX 2.3 AMD GGUF - ComfyUI Auto Setup
echo ============================================
echo.

:: ------------------------------------------------------------------
:: Step 0: Detect ComfyUI location
:: ------------------------------------------------------------------
set "COMFY_DIR="

:: Check common locations
if exist "%~dp0..\ComfyUI\main.py" set "COMFY_DIR=%~dp0..\ComfyUI"
if exist "%~dp0..\..\ComfyUI\main.py" set "COMFY_DIR=%~dp0..\..\ComfyUI"
if exist "C:\ComfyUI\main.py" set "COMFY_DIR=C:\ComfyUI"
if exist "C:\AI\ComfyUI\main.py" set "COMFY_DIR=C:\AI\ComfyUI"
if exist "D:\ComfyUI\main.py" set "COMFY_DIR=D:\ComfyUI"
if exist "E:\ComfyUI\main.py" set "COMFY_DIR=E:\ComfyUI"

if "%COMFY_DIR%"=="" (
    echo [INFO] ComfyUI not found in common locations.
    echo.
    echo Please enter the full path to your ComfyUI folder:
    echo (e.g. C:\ComfyUI_windows_portable\ComfyUI)
    set /p "COMFY_DIR=^> "
)

if not exist "%COMFY_DIR%\main.py" (
    echo [ERROR] ComfyUI not found at: %COMFY_DIR%
    echo.
    echo Please make sure you have extracted ComfyUI first.
    echo Download from: https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_amd.7z
    echo.
    pause
    exit /b 1
)

echo [OK] ComfyUI found at: %COMFY_DIR%
echo.

:: ------------------------------------------------------------------
:: Step 1: Create model folders
:: ------------------------------------------------------------------
echo [Step 1/4] Creating model folders...
mkdir "%COMFY_DIR%\models\unet" 2>nul
mkdir "%COMFY_DIR%\models\text_encoders" 2>nul
mkdir "%COMFY_DIR%\models\vae" 2>nul
mkdir "%COMFY_DIR%\models\loras" 2>nul
mkdir "%COMFY_DIR%\models\checkpoints" 2>nul
echo [OK] Model folders ready.
echo.

:: ------------------------------------------------------------------
:: Step 2: Install custom nodes
:: ------------------------------------------------------------------
echo [Step 2/4] Installing custom nodes...

:: ComfyUI-Manager
if not exist "%COMFY_DIR%\custom_nodes\ComfyUI-Manager" (
    echo   - Installing ComfyUI-Manager...
    cd /d "%COMFY_DIR%\custom_nodes"
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
) else (
    echo   [SKIP] ComfyUI-Manager already installed
)

:: ComfyUI-GGUF
if not exist "%COMFY_DIR%\custom_nodes\ComfyUI-GGUF" (
    echo   - Installing ComfyUI-GGUF...
    cd /d "%COMFY_DIR%\custom_nodes"
    git clone https://github.com/iamkaijun/ComfyUI-GGUF.git
) else (
    echo   [SKIP] ComfyUI-GGUF already installed
)

:: CG-Use-Everywhere
if not exist "%COMFY_DIR%\custom_nodes\CG-Use-Everywhere" (
    echo   - Installing CG-Use-Everywhere...
    cd /d "%COMFY_DIR%\custom_nodes"
    git clone https://github.com/chrisgoringe/CG-Use-Everywhere.git
) else (
    echo   [SKIP] CG-Use-Everywhere already installed
)

:: ComfyUI-KJNodes
if not exist "%COMFY_DIR%\custom_nodes\ComfyUI-KJNodes" (
    echo   - Installing ComfyUI-KJNodes...
    cd /d "%COMFY_DIR%\custom_nodes"
    git clone https://github.com/kijai/ComfyUI-KJNodes.git
) else (
    echo   [SKIP] ComfyUI-KJNodes already installed
)

:: ComfyUI-VideoHelperSuite
if not exist "%COMFY_DIR%\custom_nodes\ComfyUI-VideoHelperSuite" (
    echo   - Installing ComfyUI-VideoHelperSuite...
    cd /d "%COMFY_DIR%\custom_nodes"
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
) else (
    echo   [SKIP] ComfyUI-VideoHelperSuite already installed
)

:: rgthree-comfy
if not exist "%COMFY_DIR%\custom_nodes\rgthree-comfy" (
    echo   - Installing rgthree-comfy...
    cd /d "%COMFY_DIR%\custom_nodes"
    git clone https://github.com/rgthree/rgthree-comfy.git
) else (
    echo   [SKIP] rgthree-comfy already installed
)

echo [OK] Custom nodes installed.
echo.

:: ------------------------------------------------------------------
:: Step 3: Install Python dependencies for custom nodes
:: ------------------------------------------------------------------
echo [Step 3/4] Installing Python dependencies...

echo   - ComfyUI-GGUF requirements...
if exist "%COMFY_DIR%\custom_nodes\ComfyUI-GGUF\requirements.txt" (
    cd /d "%COMFY_DIR%"
    "%COMFY_DIR%\..\python_embeded\python.exe" -m pip install -r "%COMFY_DIR%\custom_nodes\ComfyUI-GGUF\requirements.txt" --quiet 2>nul
)

echo   - VideoHelperSuite requirements...
if exist "%COMFY_DIR%\custom_nodes\ComfyUI-VideoHelperSuite\requirements.txt" (
    cd /d "%COMFY_DIR%"
    "%COMFY_DIR%\..\python_embeded\python.exe" -m pip install -r "%COMFY_DIR%\custom_nodes\ComfyUI-VideoHelperSuite\requirements.txt" --quiet 2>nul
)

echo   - KJNodes requirements...
if exist "%COMFY_DIR%\custom_nodes\ComfyUI-KJNodes\requirements.txt" (
    cd /d "%COMFY_DIR%"
    "%COMFY_DIR%\..\python_embeded\python.exe" -m pip install -r "%COMFY_DIR%\custom_nodes\ComfyUI-KJNodes\requirements.txt" --quiet 2>nul
)

echo [OK] Dependencies installed.
echo.

:: ------------------------------------------------------------------
:: Step 4: Copy workflow JSON
:: ------------------------------------------------------------------
echo [Step 4/4] Copying workflow JSON...

set "WORKFLOW_SRC=%~dp0LTX_2.3_IA2V_lip_Syncing.json"
set "WORKFLOW_DST=%COMFY_DIR%\web_custom_workflows\"

if not exist "%WORKFLOW_DST%" mkdir "%WORKFLOW_DST%"

if exist "%WORKFLOW_SRC%" (
    copy /Y "%WORKFLOW_SRC%" "%WORKFLOW_DST%LTX_2.3_IA2V_lip_Syncing.json" >nul
    echo [OK] Workflow copied to: %WORKFLOW_DST%
) else (
    echo [WARN] Workflow JSON not found at: %WORKFLOW_SRC%
    echo        Please manually copy the workflow file.
)

echo.
echo ============================================
echo   SETUP COMPLETE!
echo ============================================
echo.
echo Follow the remaining steps in MODELS_NEEDED.md
echo to download models, then:
echo.
echo   1. Open ComfyUI (run_amd_gpu.bat or main.py --directml)
echo   2. Load workflow: LTX_2.3_IA2V_lip_Syncing
echo   3. Set your input image and audio
echo   4. Click Queue Prompt / Generate
echo.
echo ============================================
echo.
pause
