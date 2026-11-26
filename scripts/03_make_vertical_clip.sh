#!/usr/bin/env bash
# Corta um trecho do vídeo longo e gera clipe vertical 9:16 (Shorts/Reels/TikTok/Stories) com legenda queimada.
#
# Uso: scripts/03_make_vertical_clip.sh <entrada.mp4> <inicio> <fim> <saida.mp4> [legenda.srt] [cta_stories:sim|nao]
#   inicio/fim no formato 00:01:23 ou em segundos.
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/lib/common.sh"

IN="$1"; START="$2"; END="$3"; OUT="$4"; SRT="$5"; CTA="${6:-nao}"
[ -z "$IN" ] || [ -z "$START" ] || [ -z "$END" ] || [ -z "$OUT" ] && {
  echo "Uso: $0 <entrada.mp4> <inicio> <fim> <saida.mp4> [legenda.srt] [cta_stories:sim|nao]"; exit 1; }
require_file "$IN"
mkdir -p "$(dirname "$OUT")"

VF="crop=ih*9/16:ih,scale=1080:1920"
if [ -n "$SRT" ] && [ -f "$SRT" ]; then
  VF="${VF},subtitles=${SRT}:force_style='${SUB_STYLE}'"
fi
if [ "$CTA" = "sim" ]; then
  VF="${VF},drawtext=text='Assista completo no YouTube':fontcolor=white:fontsize=34:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-160"
fi

ffmpeg -y -ss "$START" -to "$END" -i "$IN" \
  -vf "$VF" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 160k \
  -movflags +faststart \
  "$OUT" -loglevel warning -stats

echo "Pronto: $OUT"
