#!/usr/bin/env python3
"""Remove pausas longas (silêncio) do vídeo, tipo corte de ritmo (jump cut) de editor.

Mantém pausas curtas e naturais de respiração; corta só os "brancos" longos (pensando,
lendo o roteiro, etc). Um único ffmpeg, sem perder sincronismo áudio/vídeo.

Uso:
  python3 scripts/06_remove_silence.py <entrada.mp4> <saida.mp4> \
      [--min-gap 1.8] [--noise -30dB] [--pad 0.12] [--start S] [--end E]
"""
import argparse
import re
import subprocess
import sys

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
    # silencedetect timestamps já são relativos ao trecho quando -ss/-to são usados antes de -i
    keep = build_keep_segments(silences, args.min_gap, args.pad, duration)

    removed = duration - sum(e - s for s, e in keep)
    print(f"{len(silences)} silêncios detectados, {len(silences) - len(keep) + 1} cortes aplicados "
          f"(>= {args.min_gap}s). Removendo ~{removed:.1f}s de {duration:.1f}s.")

    if len(keep) <= 1:
        print("Nada relevante para cortar; copiando trecho original.")
        s, e = (keep[0] if keep else (0.0, duration))
        cmd = ["ffmpeg", "-y", "-ss", str(start + s), "-to", str(start + e), "-i", args.input,
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
               args.output, "-loglevel", "warning", "-stats"]
        subprocess.run(cmd, check=True)
        return

    parts = []
    labels = []
    for i, (s, e) in enumerate(keep):
        abs_s, abs_e = start + s, start + e
        parts.append(f"[0:v]trim=start={abs_s:.3f}:end={abs_e:.3f},setpts=PTS-STARTPTS[v{i}];")
        parts.append(f"[0:a]atrim=start={abs_s:.3f}:end={abs_e:.3f},asetpts=PTS-STARTPTS[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    parts.append("".join(labels) + f"concat=n={len(keep)}:v=1:a=1[outv][outa]")
    filter_complex = "".join(parts)

    cmd = [
        "ffmpeg", "-y", "-i", args.input,
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        args.output, "-loglevel", "warning", "-stats",
    ]
    subprocess.run(cmd, check=True)
    print(f"Pronto: {args.output} (nova duração ~{duration - removed:.1f}s)")


if __name__ == "__main__":
    main()
