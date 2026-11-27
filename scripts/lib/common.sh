# Funções e constantes compartilhadas pelos scripts da esteira Beat & Money.

BRAND_YELLOW="0xF5D800"
BRAND_WHITE="0xFFFFFF"
BRAND_BLACK="0x0A0A0A"

# Estilo de legenda queimada, bold amarelo com contorno preto grosso (lê fácil em vídeo vertical)
SUB_STYLE="FontName=DejaVu Sans,FontSize=13,PrimaryColour=&H0000D8F5,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=0,Bold=1,Alignment=2,MarginV=90"

require_file() {
  if [ ! -f "$1" ]; then
    echo "Erro: arquivo não encontrado: $1" >&2
    exit 1
  fi
}

# Dimensões REAIS de exibição do vídeo (já considerando rotação do celular/tablet).
# ffprobe reporta width/height do frame codificado, que fica trocado quando o vídeo
# tem metadado de rotação de 90/270 graus (comum em gravação vertical de celular).
get_display_dims() {
  local file="$1"
  python3 - "$file" <<'PYEOF'
import json, subprocess, sys
info = json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-select_streams", "v:0",
    "-show_entries", "stream=width,height:stream_side_data=rotation",
    "-of", "json", sys.argv[1],
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
print(w, h)
PYEOF
}

# Calcula a maior caixa de corte centralizada com a proporção pedida, sem estourar
# os limites reais do vídeo (evita "Invalid too big" quando a fonte é vertical/landscape).
# Uso: read CW CH <<< "$(compute_crop "$W" "$H" "$RATIO_W" "$RATIO_H")"
compute_crop() {
  python3 - "$1" "$2" "$3" "$4" <<'PYEOF'
import sys
w, h, rw, rh = (float(x) for x in sys.argv[1:5])
cw = h * rw / rh
if cw <= w:
    ch = h
else:
    cw = w
    ch = w * rh / rw
print(int(cw), int(ch))
PYEOF
}
