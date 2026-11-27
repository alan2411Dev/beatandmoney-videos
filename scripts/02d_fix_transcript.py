#!/usr/bin/env python3
"""Corrige erros recorrentes de transcrição (nome do canal, termos da marca) usando
brand/asr_corrections.json. Funciona em .srt (texto) ou no .json de palavras (word-level).

Uso: python3 scripts/02d_fix_transcript.py <entrada.srt|entrada.json> <saida>
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

CORRECTIONS_PATH = Path(__file__).resolve().parent.parent / "brand" / "asr_corrections.json"


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(word: str) -> str:
    return strip_accents(word.lower().strip(".,!?;:\"'"))


def fix_text(text: str, phrases) -> str:
    for wrong, right in phrases:
        text = re.sub(re.escape(wrong), right, text, flags=re.IGNORECASE)
    return text


def fix_words(words, swaps):
    swaps = sorted(swaps, key=lambda s: -len(s["wrong"]))
    out = []
    i = 0
    n = len(words)
    while i < n:
        matched = False
        for swap in swaps:
            wlen = len(swap["wrong"])
            if i + wlen > n:
                continue
            candidate = [norm(words[i + k]["word"]) for k in range(wlen)]
            if candidate == swap["wrong"]:
                rlen = len(swap["right"])
                for k in range(rlen):
                    src = words[i + k] if k < wlen else words[i + wlen - 1]
                    out.append({"word": swap["right"][k], "start": src["start"], "end": src["end"]})
                i += wlen
                matched = True
                break
        if not matched:
            out.append(words[i])
            i += 1
    return out


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 scripts/02d_fix_transcript.py <entrada.srt|entrada.json> <saida>")
        sys.exit(1)

    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    corrections = json.loads(CORRECTIONS_PATH.read_text(encoding="utf-8"))

    if src.suffix == ".json":
        words = json.loads(src.read_text(encoding="utf-8"))
        fixed = fix_words(words, corrections["word_swaps"])
        out.write_text(json.dumps(fixed, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(words)} -> {len(fixed)} palavras. Salvo em {out}")
    else:
        text = src.read_text(encoding="utf-8")
        fixed = fix_text(text, corrections["text_phrases"])
        out.write_text(fixed, encoding="utf-8")
        print(f"Correções aplicadas. Salvo em {out}")


if __name__ == "__main__":
    main()
