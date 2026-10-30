"""Analyze a reference video (a TikTok / Reel link or a local .mp4) to copy what makes it work.

Writes reference/<name>/:
  video.mp4      the video (downloaded with yt-dlp if a link was given)
  sheet.png      one picture per shot, in order (the look: text, colors, images vs footage)
  hook.png       the first 3 seconds, one picture every half second
  transcript.txt every spoken word with its time (faster-whisper)
  report.md      length, shots, cut rhythm, speaking speed, loudness, the hook

Only for studying a video on this PC: never repost it.
Usage (from the project folder):
    .venv-analysis\\Scripts\\python.exe tools\\analyze_reference.py https://www.tiktok.com/@user/video/123
    .venv-analysis\\Scripts\\python.exe tools\\analyze_reference.py C:\\path\\to\\video.mp4
"""
import json
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reference"


def ffmpeg():
    return shutil.which("ffmpeg") or sys.exit("FFmpeg not found.")


def download(url):
    import yt_dlp
    OUT.mkdir(exist_ok=True)
    opts = {"outtmpl": str(OUT / "%(extractor)s_%(id)s.%(ext)s"), "format": "mp4/bestvideo*+bestaudio/best",
            "merge_output_format": "mp4", "quiet": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        path = Path(ydl.prepare_filename(info)).with_suffix(".mp4")
    return path, {"title": info.get("title"), "uploader": info.get("uploader"), "views": info.get("view_count"),
                  "likes": info.get("like_count"), "description": info.get("description")}


def probe(path):
    ffprobe = shutil.which("ffprobe") or str(Path(ffmpeg()).with_stem("ffprobe"))
    out = subprocess.run([ffprobe, "-v", "error", "-show_entries",
                          "format=duration:stream=width,height,codec_type", "-of", "json", str(path)],
                         capture_output=True, text=True).stdout
    data = json.loads(out)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), {})
    return float(data["format"]["duration"]), video.get("width"), video.get("height")


def frame_at(path, seconds, width=360):
    raw = subprocess.run([ffmpeg(), "-v", "error", "-ss", f"{seconds:.2f}", "-i", str(path), "-frames:v", "1",
                          "-vf", f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert("RGB") if raw else None


def sheet(images, labels, cols, out):
    images = [(im, lb) for im, lb in zip(images, labels) if im]
    if not images:
        return
    w, h = images[0][0].size
    rows = (len(images) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * w, rows * (h + 28)), (20, 20, 20))
    d = ImageDraw.Draw(canvas)
    for k, (im, label) in enumerate(images):
        x, y = (k % cols) * w, (k // cols) * (h + 28)
        canvas.paste(im.resize((w, h)), (x, y + 28))
        d.text((x + 8, y + 6), label, fill=(255, 220, 120))
    canvas.save(out)


def shots(path):
    from scenedetect import AdaptiveDetector, ContentDetector, detect
    scenes = detect(str(path), ContentDetector(threshold=27))
    if len(scenes) < 4:  # soft crossfades fool the cut finder: try the more sensitive one
        scenes = detect(str(path), AdaptiveDetector(adaptive_threshold=2.0, min_scene_len=20))
    return [(s.get_seconds(), e.get_seconds()) for s, e in scenes]


def transcribe(path):
    from faster_whisper import WhisperModel
    import numpy as np
    model = WhisperModel("small", device="cpu", compute_type="int8")  # downloaded once (~250 MB)
    # FFmpeg reads the sound (faster-whisper's own reader breaks with the newest PyAV)
    raw = subprocess.run([ffmpeg(), "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    segments, info = model.transcribe(audio, word_timestamps=True, vad_filter=True)
    words = [w for s in segments for w in (s.words or [])]
    return words, info.language


def loudness(path):
    err = subprocess.run([ffmpeg(), "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    found = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    return float(found[-1]) if found else None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    meta = {}
    if re.match(r"https?://", src):
        print("Downloading...")
        path, meta = download(src)
    else:
        path = Path(src)
    folder = OUT / (path.parent.name if path.stem == "video" else path.stem)
    folder.mkdir(parents=True, exist_ok=True)
    if path.parent != folder:
        target = folder / "video.mp4"
        shutil.copy(path, target) if not re.match(r"https?://", src) else shutil.move(path, target)
        path = target

    duration, width, height = probe(path)
    print(f"{duration:.1f}s, {width}x{height}. Finding the shots...")
    cuts = shots(path) or [(0.0, duration)]
    lengths = [e - s for s, e in cuts]
    mids = [(s + e) / 2 for s, e in cuts][:36]
    sheet([frame_at(path, t, 240) for t in mids], [f"{t:.1f}s" for t in mids], 6, folder / "sheet.png")
    hook_times = [i * 0.5 for i in range(6)]
    sheet([frame_at(path, t, 300) for t in hook_times], [f"{t:.1f}s" for t in hook_times], 6, folder / "hook.png")

    print("Listening to the voice (first time: downloads the speech model)...")
    words, language = transcribe(path)
    (folder / "transcript.txt").write_text(
        "\n".join(f"{w.start:6.2f}-{w.end:6.2f}  {w.word.strip()}" for w in words), encoding="utf-8")
    spoken = " ".join(w.word.strip() for w in words)
    talk = (words[-1].end - words[0].start) if words else 0
    hook = " ".join(w.word.strip() for w in words if w.start < 3.0)
    lufs = loudness(path)

    report = [f"# Reference: {path.parent.name}", ""]
    if meta:
        report += [f"- Title: {meta.get('title')}", f"- Account: {meta.get('uploader')}",
                   f"- Views: {meta.get('views')}  Likes: {meta.get('likes')}", ""]
    report += [f"- Length: {duration:.1f} s, {width}x{height}",
               f"- Shots: {len(cuts)}, average {statistics.mean(lengths):.1f} s "
               f"(shortest {min(lengths):.1f} s, longest {max(lengths):.1f} s)",
               f"- First shot changes at {cuts[0][1]:.1f} s; shots in the first 5 s: {sum(1 for s, _ in cuts if s < 5)}",
               f"- Language: {language}; words: {len(words)}; speaking speed: "
               f"{(len(words) / talk if talk else 0):.2f} words/s (ours: about 2.6 with Christopher)",
               f"- Voice starts at {words[0].start:.1f} s" if words else "- No voice found",
               f"- Loudness: {lufs} LUFS (ours: -14)",
               f"- Spoken in the first 3 s (the hook): {hook}", "", "## Full script", "", spoken, ""]
    (folder / "report.md").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report[:12]))
    print(f"\nDone: {folder}")


if __name__ == "__main__":
    main()
