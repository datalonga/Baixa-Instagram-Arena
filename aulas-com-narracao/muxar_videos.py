#!/usr/bin/env python3
"""Combine the original 30-second lessons with their Portuguese voiceovers."""
from pathlib import Path
import subprocess
import zipfile
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "videos"
HERE = Path(__file__).resolve().parent
VOICE = HERE / "narracoes"
OUTPUT = HERE / "videos"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source_files = sorted(SOURCE.glob("aula-*.mp4"))
    if len(source_files) != 10:
        raise SystemExit(f"Esperava 10 vídeos originais; encontrei {len(source_files)}.")

    for video in source_files:
        num = video.name.split("-")[1]
        audio = VOICE / f"aula-{num}.mp3"
        if not audio.is_file():
            raise SystemExit(f"Narração não encontrada: {audio}")
        destination = OUTPUT / video.name
        print(f"Adicionando narração à aula {num}...", flush=True)
        subprocess.run([
            FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(video), "-i", str(audio),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
            "-af", "apad=whole_dur=30,atrim=duration=30",
            "-t", "30", "-movflags", "+faststart",
            "-metadata", f"title=Aula {num} de JavaScript com narração",
            "-metadata", "comment=Locução em português brasileiro; 30 segundos; 16:9",
            str(destination)
        ], check=True)

    archive = HERE / "videos-com-narracao.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3) as bundle:
        for video in sorted(OUTPUT.glob("aula-*.mp4")):
            bundle.write(video, video.name)
    print(f"Pronto: {len(source_files)} vídeos em {OUTPUT}")


if __name__ == "__main__":
    main()
