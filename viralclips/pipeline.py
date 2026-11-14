import json, re, subprocess, shutil, time
from pathlib import Path
from collections import Counter
import yt_dlp
import imageio_ffmpeg
from faster_whisper import WhisperModel
from .config import WORK, OUTPUT

HOOK_WORDS = {
    "increíble": 3, "increible": 3, "nunca": 2, "siempre": 1, "error": 2,
    "dinero": 2, "millones": 2, "secreto": 3, "problema": 2, "笑": 1,
    "espera": 2, "qué": 1, "como": 1, "cómo": 1, "verdad": 2, "imposible": 3,
    "brutal": 2, "vergüenza": 2, "ganar": 2, "perder": 2, "wow": 2,
    "jajaja": 2, "jaja": 2, "no": 1, "pero": 1, "porque": 1, "por qué": 2,
    "increíblemente": 2, "atención": 3, "cuidado": 2, "sorpresa": 3
}
def ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or "Error ejecutando FFmpeg")[-1800:])
    return p

def download_video(url, folder, progress):
    folder.mkdir(parents=True, exist_ok=True)
    opts = {
        "outtmpl": str(folder / "source.%(ext)s"),
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [lambda d: progress(d)],
        "retries": 3,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    candidates = [p for p in folder.glob("source.*") if p.suffix.lower() in (".mp4",".mkv",".webm",".mov")]
    if not candidates:
        raise RuntimeError("No se encontró el video descargado. Puede que la plataforma no permita acceder al enlace.")
    return candidates[0], info

def transcribe(video, work, progress):
    audio = work / "audio.wav"
    run([ffmpeg(), "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(audio)])
    progress("Transcribiendo el audio en español (el primer uso puede descargar el modelo)...")
    model = WhisperModel("small", device="cpu", compute_type="int8", download_root=str(work/"models"))
    segments, info = model.transcribe(str(audio), language="es", word_timestamps=True, vad_filter=True)
    result = []
    for s in segments:
        words = []
        if s.words:
            for w in s.words:
                words.append({"start": float(w.start), "end": float(w.end), "word": w.word.strip()})
        result.append({"start": float(s.start), "end": float(s.end), "text": s.text.strip(), "words": words})
    if not result:
        raise RuntimeError("No se detectó voz en el video.")
    return result

def choose_clips(segments, duration, count=10):
    candidates = []
    step = max(8, min(15, duration / 60))
    start = 0.0
    while start < max(0, duration-5):
        end = min(duration, start + 38)
        selected = [s for s in segments if s["end"] > start and s["start"] < end]
        text = " ".join(s["text"] for s in selected).lower()
        words = re.findall(r"\w+", text, flags=re.UNICODE)
        if len(words) >= 12:
            score = sum(weight for term, weight in HOOK_WORDS.items() if term in text)
            score += min(len(words), 110) / 18
            # Favor conversational density and exclamations/questions.
            score += (text.count("!") + text.count("?")) * 0.7
            score += min(3, len(selected) / 8)
            candidates.append({"start": max(0, start), "end": end, "score": score, "text": text})
        start += step
    candidates.sort(key=lambda x: x["score"], reverse=True)
    chosen = []
    for c in candidates:
        if all(abs(c["start"]-x["start"]) > 30 for x in chosen):
            chosen.append(c)
        if len(chosen) == count: break
    if len(chosen) < count:
        for c in sorted(candidates, key=lambda x:x["start"]):
            if c not in chosen:
                chosen.append(c)
            if len(chosen) == count: break
    return sorted(chosen, key=lambda x:x["score"], reverse=True)

def ass_time(seconds):
    h = int(seconds//3600); m = int((seconds%3600)//60); s = seconds%60
    return f"{h}:{m:02d}:{s:05.2f}"

def make_ass(segments, clip_start, clip_end, path):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,78,&H00FFFFFF,&H0000FFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,65,65,300,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    palette = ["&H0000D7FF", "&H0000FF78", "&H00FFFFFF"]
    for seg in segments:
        for w in seg.get("words", []):
            a=max(0,w["start"]-clip_start); b=min(clip_end-clip_start,w["end"]-clip_start)
            if b <= a: continue
            word = w["word"].replace("{","").replace("}","").replace("\\","")
            if not word: continue
            color = palette[abs(hash(word.lower())) % len(palette)]
            txt = f"{{\\c{color}\\bord5\\shad2}}{word.upper()}"
            lines.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Default,,0,0,0,,{txt}")
    path.write_text("\n".join(lines), encoding="utf-8-sig")

def caption_for(text, idx):
    clean = re.sub(r"\s+", " ", text).strip()
    words = clean.split()
    hook = "Esto es lo que pocos están viendo 👀"
    if words:
        hook = "Espera a escuchar esto: " + " ".join(words[:7]).strip(".,!?") + "…"
    tags = "#viral #clips #momentos #parati #shorts #reels"
    return f"{hook}\n\n{clean[:240]}\n\n{tags}"

def render_clip(video, clip, segments, out, idx):
    ass = out.with_suffix(".ass")
    make_ass(segments, clip["start"], clip["end"], ass)
    start, length = clip["start"], clip["end"]-clip["start"]
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,subtitles=" + str(ass).replace("\\","/").replace(":","\\:")
    run([ffmpeg(), "-y", "-ss", str(start), "-i", str(video), "-t", str(length),
         "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    try: ass.unlink()
    except: pass

def process(url, project_name, callback):
    stamp = time.strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", project_name).strip("_") or "Proyecto"
    work = WORK / (safe_name + "_" + stamp)
    outdir = OUTPUT / (safe_name + "_" + stamp)
    work.mkdir(parents=True, exist_ok=True); outdir.mkdir(parents=True, exist_ok=True)
    callback(5, "Conectando con la plataforma...")
    video, info = download_video(url, work, lambda d: callback(12, "Descargando video..."))
    callback(25, "Video descargado. Preparando análisis...")
    segments = transcribe(video, work, lambda msg: callback(35, msg))
    callback(65, "Buscando los 10 momentos con mayor potencial...")
    duration = float(info.get("duration") or 0)
    if not duration:
        p = run([ffmpeg(), "-i", str(video)])
        m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr or "")
        if m: duration = int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))
    picks = choose_clips(segments, duration, 10)
    if not picks: raise RuntimeError("No se encontraron fragmentos con suficiente diálogo.")
    manifest = []
    for i, clip in enumerate(picks, 1):
        callback(65 + int(30*i/len(picks)), f"Creando clip {i} de {len(picks)}...")
        target = outdir / f"clip_{i:02d}.mp4"
        render_clip(video, clip, segments, target, i)
        caption = caption_for(clip["text"], i)
        (outdir / f"clip_{i:02d}_caption.txt").write_text(caption, encoding="utf-8")
        manifest.append({"file": str(target), "caption": caption, "start": clip["start"], "end": clip["end"], "score": round(clip["score"],2)})
    data = {"name": project_name, "url": url, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "clips": manifest}
    (outdir/"project.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    callback(100, "¡Proceso terminado!")
    return data
