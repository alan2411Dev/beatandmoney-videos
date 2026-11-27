#!/usr/bin/env python3
"""Remove pausas longas (silêncio) do vídeo, tipo corte de ritmo (jump cut) de editor.

Mantém pausas curtas e naturais de respiração; corta só os "brancos" longos (pensando,
lendo o roteiro, etc). Processa um segmento de cada vez (baixo consumo de memória) e
depois junta tudo com concat demuxer (sem recodificar de novo).

Uso:
  python3 scripts/06_remove_silence.py <entrada.mp4> <saida.mp4> \
      [--min-gap 1.8] [--noise -30dB] [--pad 0.12] [--start S] [--end E]
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

SIL_START = re.compile(r"silence_start:\s*([\-0-9.]+)")
SIL_END = re.compile(r"silence_end:\s*([\-0-9.]+)")


def detect_silences(path, noise, start, end):
    cmd = ["ffmpeg", "-v", "info"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if end is not None:
        cmd += ["-to", str(end)]
    cmd += ["-i", path, "-af", f"silencedetect=noise={noise}:d=0.3", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stderr

    starts, ends = [], []
    for line in out.splitlines():
        m = SIL_START.search(line)
        if m:
            starts.append(float(m.group(1)))
        m = SIL_END.search(line)
        if m:
            ends.append(float(m.group(1)))

    n = min(len(starts), len(ends))
    return list(zip(starts[:n], ends[:n]))


def build_keep_segments(silences, min_gap, pad, duration):
    cuts = [(s, e) for s, e in silences if (e - s) >= min_gap]
    cuts.sort()

    keep = []
    cursor = 0.0
    for s, e in cuts:
        seg_end = max(cursor, min(s + pad, duration))
        if seg_end > cursor + 0.05:
            keep.append((cursor, seg_end))
        cursor = max(cursor, e - pad)
    if duration - cursor > 0.05:
        keep.append((cursor, duration))
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--min-gap", type=float, default=1.8, help="pausas >= isso (seg) são cortadas")
    ap.add_argument("--noise", default="-30dB")
    ap.add_argument("--pad", type=float, default=0.12, help="respiro mantido em cada lado do corte")
    ap.add_argument("--start", type=float, default=None, help="início do trecho de origem (seg)")
    ap.add_argument("--end", type=float, default=None, help="fim do trecho de origem (seg)")
    args = ap.parse_args()

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.input],
        capture_output=True, text=True,
    )
    full_duration = float(probe.stdout.strip())
    start = args.start or 0.0
    end = args.end if args.end is not None else full_duration
    duration = end - start

    print("Detectando silêncios...")
    silences = detect_silences(args.input, args.noise, args.start, args.end)
    keep = build_keep_segments(silences, args.min_gap, args.pad, duration)

    removed = duration - sum(e - s for s, e in keep)
    print(f"{len(silences)} silêncios detectados; mantendo {len(keep)} trechos "
          f"(cortes >= {args.min_gap}s). Removendo ~{removed:.1f}s de {duration:.1f}s.")

    tmpdir = tempfile.mkdtemp(prefix="jumpcut_")
    try:
        list_path = os.path.join(tmpdir, "list.txt")
        with open(list_path, "w") as list_f:
            for i, (s, e) in enumerate(keep):
                seg_path = os.path.join(tmpdir, f"seg_{i:03d}.mp4")
                abs_s, abs_e = start + s, start + e
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", f"{abs_s:.3f}", "-to", f"{abs_e:.3f}", "-i", args.input,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k",
                    seg_path, "-loglevel", "error",
                ]
                subprocess.run(cmd, check=True)
                list_f.write(f"file '{seg_path}'\n")
                print(f"  [{i + 1}/{len(keep)}] {abs_s:.2f}-{abs_e:.2f}s ok")

        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
            "-c", "copy", "-movflags", "+faststart",
            args.output, "-loglevel", "warning", "-stats",
        ]
        subprocess.run(cmd, check=True)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"Pronto: {args.output} (nova duração ~{duration - removed:.1f}s)")


if __name__ == "__main__":
    main()
