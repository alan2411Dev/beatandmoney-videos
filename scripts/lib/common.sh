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
