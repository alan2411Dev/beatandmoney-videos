#!/usr/bin/env python3
"""Transcreve com timestamp por palavra (necessário para legenda 'palavra-pop').

Uso: python3 scripts/02c_word_timestamps.py <entrada.mp4|wav> <saida.json> [modelo]
Gera uma lista JSON: [{"word": "...", "start": 0.0, "end": 0.4}, ...]
"""
import json
import sys


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 scripts/02c_word_timestamps.py <entrada> <saida.json> [modelo]")
        sys.exit(1)

    src = sys.argv[1]
    out_path = sys.argv[2]
    model_size = sys.argv[3] if len(sys.argv) > 3 else "small"

    from faster_whisper import WhisperModel

    print(f"Carregando modelo '{model_size}'...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print("Transcrevendo com timestamp por palavra...")
    segments, info = model.transcribe(src, language="pt", vad_filter=True, word_timestamps=True)

    words = []
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            words.append({"word": w.word.strip(), "start": w.start, "end": w.end})

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=1)

    print(f"{len(words)} palavras salvas em {out_path}")


if __name__ == "__main__":
    main()
