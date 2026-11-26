#!/usr/bin/env bash
# Normaliza o take bruto para publicação no YouTube (1080p) + extrai 3 frames candidatos a thumbnail.
#
# Uso: scripts/01_prep_youtube.sh <entrada.mp4> <saida.mp4>
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/lib/common.sh"

IN="$1"
OUT="$2"
[ -z "$IN" ] || [ -z "$OUT" ] && { echo "Uso: $0 <entrada.mp4> <saida.mp4>"; exit 1; }
require_file "$IN"

mkdir -p "$(dirname "$OUT")"

ffmpeg -y -i "$IN" \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  "$OUT" -loglevel warning -stats

BASE="${OUT%.*}"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
for PCT in 20 50 80; do
  T=$(python3 -c "print($DUR*$PCT/100)")
  ffmpeg -y -ss "$T" -i "$OUT" -frames:v 1 -q:v 2 "${BASE}_thumb_${PCT}.jpg" -loglevel error
done

echo "Pronto: $OUT"
echo "Thumbnails candidatas: ${BASE}_thumb_20.jpg / _50 / _80"
