
@echo off
setlocal
title ViralClipsAI - Compilador Windows 64 bits
cd /d "%~dp0"

echo ==========================================
echo VIRALCLIPSAI - COMPILACION WINDOWS
echo ==========================================

where python >nul 2>nul
if errorlevel 1 (
    echo No se encontro Python para compilar.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

if errorlevel 1 goto fail

python -m PyInstaller --noconfirm --clean --windowed --name ViralClipsAI --icon assets\viralclips.ico --collect-all yt_dlp --collect-all faster_whisper --collect-all imageio_ffmpeg --collect-all av --add-data "assets;assets" app.py

if errorlevel 1 goto fail

echo.
echo Compilacion terminada.
echo Ejecutable: dist\ViralClipsAI\ViralClipsAI.exe

where ISCC >nul 2>nul
if errorlevel 1 (
    echo No se encontro Inno Setup.
    pause
    exit /b 0
)

ISCC installer.iss
if errorlevel 1 goto fail

echo Instalador creado correctamente.
pause
exit /b 0

:fail
echo ERROR DURANTE LA COMPILACION.
pause
exit /b 1
