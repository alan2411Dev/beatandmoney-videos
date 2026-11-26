#!/usr/bin/env bash
# Gera recorte para o feed do Instagram (quadrado 1:1 ou retrato 4:5) a partir de um trecho do vídeo.
#
# Uso: scripts/04_make_feed_post.sh <entrada.mp4> <inicio> <fim> <saida.mp4> <formato:square|4x5>
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/lib/common.sh"

IN="$1"; START="$2"; END="$3"; OUT="$4"; FORMATO="${5:-square}"
[ -z "$IN" ] || [ -z "$START" ] || [ -z "$END" ] || [ -z "$OUT" ] && {
  echo "Uso: $0 <entrada.mp4> <inicio> <fim> <saida.mp4> <formato:square|4x5>"; exit 1; }
require_file "$IN"
mkdir -p "$(dirname "$OUT")"

if [ "$FORMATO" = "4x5" ]; then
  VF="crop=ih*4/5:ih,scale=1080:1350"
else
  VF="crop=ih:ih,scale=1080:1080"
fi

ffmpeg -y -ss "$START" -to "$END" -i "$IN" \
  -vf "$VF" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 160k \
  -movflags +faststart \
  "$OUT" -loglevel warning -stats

echo "Pronto: $OUT"
