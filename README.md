# ViralClipsAI 1.0

Aplicación de escritorio para Windows 10/11 de 64 bits. Descarga contenido accesible mediante yt-dlp, transcribe voz en español con faster-whisper, puntúa ventanas de conversación y crea clips verticales MP4 con subtítulos ASS y captions.

## Requisitos para COMPILAR
- Windows 10/11 x64
- Python 3.11 x64
- Inno Setup 6 (para crear el instalador EXE)
- Conexión a Internet durante la compilación y el primer análisis

El usuario final no necesita instalar Python: PyInstaller empaqueta el runtime. El modelo Whisper `small` se descarga la primera vez que se analiza un video; se guarda en la carpeta local de la aplicación.

## Compilar
1. Extrae el ZIP en una carpeta local.
2. Instala Python 3.11 de 64 bits y marca "Add Python to PATH".
3. Instala Inno Setup 6.
4. Haz doble clic en `build_windows.bat`.
5. El instalador aparecerá en `dist/ViralClipsAI_Setup_Windows10_64bit.exe`.

## Uso
1. Abre ViralClipsAI.
2. Pega el enlace de un video/VOD público que tengas derecho a procesar.
3. Escribe el nombre del proyecto y pulsa Analizar y crear.
4. Espera la descarga, transcripción y renderizado.
5. Selecciona un clip para ver su caption; usa Abrir video, Copiar caption o Descargar todos.

## Alcance y limitaciones
- El acceso depende de las reglas, disponibilidad, región y cambios técnicos de YouTube, Twitch y Kick. No se eluden inicios de sesión, DRM, restricciones de pago ni controles de acceso.
- La selección de momentos es una primera versión basada en señales del texto (palabras de énfasis, preguntas, exclamaciones y densidad de diálogo); no garantiza detectar con precisión sarcasmo, polémicas o emociones.
- El modelo de voz se descarga en el primer uso. El procesamiento en CPU puede ser lento en videos largos; se recomienda 8 GB de RAM o más.
- El encuadre vertical usa recorte central. No incluye seguimiento inteligente de rostros en esta versión.
- Los subtítulos se sincronizan con palabras reconocidas por Whisper. La precisión depende del audio.
- Los captions son sugerencias automáticas y conviene revisarlos antes de publicar.
- Respeta derechos de autor, términos de servicio y permisos de los creadores.

## Solución de problemas
- "No se pudo acceder": el enlace puede ser privado, restringido o no compatible temporalmente.
- "No se detectó voz": comprueba que el video tenga diálogo claro en español.
- Error de FFmpeg: vuelve a ejecutar la compilación; imageio-ffmpeg provee el ejecutable empaquetado.
- Si Windows SmartScreen muestra una advertencia, verifica que el instalador proceda de una fuente confiable. El instalador inicial no está firmado digitalmente.
