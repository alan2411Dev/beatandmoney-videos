#!/usr/bin/env python3
"""Gera um corte vertical com legenda estilo 'palavra-pop' (1-2 palavras grandes por vez,
sincronizadas com a fala) + cartela de título opcional + destaque de palavra-chave.

Uso:
  python3 scripts/05_pop_captions.py <raw.mp4> <inicio_seg> <fim_seg> <words.json> <saida.mp4> \
      [--title "TEXTO"] [--highlight palavra1,palavra2] [--cta]

--title     : cartela preta com o texto em destaque (amarelo), ~1.1s, antes do corte.
--highlight : palavras (sem acento/case) que aparecem com caixa amarela + texto preto (destaque).
--cta       : adiciona "Assista completo no YouTube" no rodapé (uso em Stories).
"""
import json
import subprocess
import sys
import unicodedata


def display_dims(path: str):
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:stream_side_data=rotation",
        "-of", "json", path,
    ]))
    s = info["streams"][0]
    w, h = s["width"], s["height"]
    rot = 0
    for sd in s.get("side_data_list", []):
        if "rotation" in sd:
            rot = abs(int(sd["rotation"])) % 360
            break
    if rot in (90, 270):
        w, h = h, w
    return w, h


def compute_crop(w: int, h: int, ratio_w: float, ratio_h: float):
    cw = h * ratio_w / ratio_h
    if cw <= w:
        ch = h
    else:
        cw = w
        ch = w * ratio_h / ratio_w
    return int(cw), int(ch)

BRAND_YELLOW = "0xF5D800"
FONT = "DejaVu Sans Bold"


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(word: str) -> str:
    return strip_accents(word.lower().strip(".,!?;:\"'"))


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def group_words(words, max_per_chunk=2, gap_break=0.45):
    chunks = []
    cur = []
    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > gap_break or len(cur) >= max_per_chunk):
            chunks.append(cur)
            cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    return chunks


def main():
    args = sys.argv[1:]
    if len(args) < 5:
        print(__doc__)
        sys.exit(1)

    raw, start_s, end_s, words_json, out_path = args[:5]
    start, end = float(start_s), float(end_s)
    rest = args[5:]

    title = None
    highlight = set()
    cta = False
    i = 0
    while i < len(rest):
        if rest[i] == "--title":
            title = rest[i + 1]
            i += 2
        elif rest[i] == "--highlight":
            highlight = {norm(w) for w in rest[i + 1].split(",")}
            i += 2
        elif rest[i] == "--cta":
            cta = True
            i += 1
        else:
            i += 1

    with open(words_json, encoding="utf-8") as f:
        all_words = json.load(f)

    words = [w for w in all_words if w["end"] > start and w["start"] < end]
    for w in words:
        w["start"] = max(0.0, w["start"] - start)
        w["end"] = min(end - start, w["end"] - start)

    chunks = group_words(words)

    drawtexts = []
    for idx, chunk in enumerate(chunks):
        text = esc(" ".join(w["word"] for w in chunk).upper())
        c_start = chunk[0]["start"]
        c_end = chunk[-1]["end"]
        if c_end - c_start < 0.28:
            c_end = c_start + 0.28
        next_start = chunks[idx + 1][0]["start"] if idx + 1 < len(chunks) else c_end + 0.3
        c_end = min(c_end + 0.12, next_start)

        is_hot = any(norm(w["word"]) in highlight for w in chunk)
        if is_hot:
            style = f"fontcolor=black:fontsize=96:box=1:boxcolor={BRAND_YELLOW}:boxborderw=24"
        else:
            style = f"fontcolor={BRAND_YELLOW}:fontsize=78:borderw=6:bordercolor=black"

        drawtexts.append(
            f"drawtext=font='{FONT}':text='{text}':{style}:"
            f"x=(w-text_w)/2:y=h*0.62-text_h/2:enable='between(t,{c_start:.3f},{c_end:.3f})'"
        )

    if cta:
        drawtexts.append(
            "drawtext=font='DejaVu Sans':text='Assista completo no YouTube':"
            "fontcolor=white:fontsize=34:borderw=2:bordercolor=black:"
            "x=(w-text_w)/2:y=h-150"
        )

    src_w, src_h = display_dims(raw)
    cw, ch = compute_crop(src_w, src_h, 9, 16)
    main_vf = f"crop={cw}:{ch},scale=1080:1920"
    if drawtexts:
        main_vf += "," + ",".join(drawtexts)

    if title:
        title_text = esc(title.upper())
        title_dur = 1.2
        filter_complex = (
            f"[0:v]drawtext=font='{FONT}':text='{title_text}':fontcolor={BRAND_YELLOW}:"
            f"fontsize=140:x=(w-text_w)/2:y=(h-text_h)/2[title_v];"
            f"[2:v]{main_vf}[main_v];"
            f"[title_v][1:a][main_v][2:a]concat=n=2:v=1:a=1[outv][outa]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:d={title_dur}",
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={title_dur}",
            "-ss", str(start), "-to", str(end), "-i", raw,
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
            out_path, "-loglevel", "warning", "-stats",
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start), "-to", str(end), "-i", raw,
            "-vf", main_vf,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
            out_path, "-loglevel", "warning", "-stats",
        ]

    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Pronto: {out_path}")


if __name__ == "__main__":
    main()
