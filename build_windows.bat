@echo off
setlocal
title ViralClipsAI - Compilador Windows 64 bits
cd /d "%~dp0"
echo ==========================================
echo   VIRALCLIPSAI - COMPILACION WINDOWS
echo ==========================================
where python >nul 2>nul
if errorlevel 1 (
 echo No se encontro Python. Instala Python 3.11 de 64 bits para COMPILAR.
 echo El usuario final NO necesitara instalar Python si usa el instalador.
 pause
 exit /b 1
)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --name ViralClipsAI --icon assets\viralclips.ico --collect-all yt_dlp --collect-all faster_whisper --collect-all imageio_ffmpeg --collect-all av --add-data "assets;assets" app.py
if errorlevel 1 goto fail
where ISCC >nul 2>nul
if errorlevel 1 (
 echo PyInstaller termino. Para crear el instalador Setup instala Inno Setup 6 y vuelve a ejecutar este archivo.
 pause
 exit /b 0
)
ISCC installer.iss
if errorlevel 1 goto fail
echo Instalador creado en dist\ViralClipsAI_Setup_Windows10_64bit.exe
pause
exit /b 0
:fail
echo Hubo un error durante la compilacion.
pause
exit /b 1
