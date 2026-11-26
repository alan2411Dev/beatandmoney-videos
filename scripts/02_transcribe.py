#!/usr/bin/env python3
"""Gera legenda .srt automática (grátis, local) com faster-whisper.

Uso: python3 scripts/02_transcribe.py <entrada.mp4|wav> <saida.srt> [modelo]
Modelo padrão: small (bom equilíbrio para PT-BR). Opções: tiny, base, small, medium.
"""
import sys
from pathlib import Path

def fmt_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 scripts/02_transcribe.py <entrada> <saida.srt> [modelo]")
        sys.exit(1)

    src = sys.argv[1]
    out_srt = Path(sys.argv[2])
    model_size = sys.argv[3] if len(sys.argv) > 3 else "small"

    from faster_whisper import WhisperModel

    print(f"Carregando modelo '{model_size}'...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print("Transcrevendo (pode levar alguns minutos)...")
    segments, info = model.transcribe(src, language="pt", vad_filter=True)

    out_srt.parent.mkdir(parents=True, exist_ok=True)
    with open(out_srt, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n{fmt_ts(seg.start)} --> {fmt_ts(seg.end)}\n{seg.text.strip()}\n\n")

    print(f"Legenda salva em: {out_srt}")

if __name__ == "__main__":
    main()
