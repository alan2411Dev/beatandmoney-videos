#!/usr/bin/env python3
"""Recorta um trecho de uma legenda .srt e realinha o tempo para começar em 0.

Necessário sempre que você corta um trecho do vídeo longo: a legenda original
tem timestamps absolutos do vídeo inteiro, mas o clipe cortado começa do zero.

Uso: python3 scripts/02b_slice_srt.py <entrada.srt> <inicio_seg> <fim_seg> <saida.srt>
"""
import re
import sys
from pathlib import Path

TS_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")

def to_seconds(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def fmt_ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def parse_srt(text):
    blocks = re.split(r"\n\s*\n", text.strip())
    entries = []
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        m = TS_RE.findall(lines[1])
        if len(m) < 2:
            continue
        start = to_seconds(*m[0])
        end = to_seconds(*m[1])
        text_lines = "\n".join(lines[2:])
        entries.append((start, end, text_lines))
    return entries

def main():
    if len(sys.argv) != 5:
        print("Uso: python3 scripts/02b_slice_srt.py <entrada.srt> <inicio_seg> <fim_seg> <saida.srt>")
        sys.exit(1)

    src = Path(sys.argv[1])
    start = float(sys.argv[2])
    end = float(sys.argv[3])
    out = Path(sys.argv[4])

    entries = parse_srt(src.read_text(encoding="utf-8"))
    out_entries = []
    for s, e, text in entries:
        if e <= start or s >= end:
            continue
        new_s = max(s, start) - start
        new_e = min(e, end) - start
        out_entries.append((new_s, new_e, text))

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for i, (s, e, text) in enumerate(out_entries, start=1):
            f.write(f"{i}\n{fmt_ts(s)} --> {fmt_ts(e)}\n{text}\n\n")

    print(f"{len(out_entries)} legendas recortadas em {out}")

if __name__ == "__main__":
    main()
