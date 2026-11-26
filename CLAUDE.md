# Beat & Money — Pipeline de Vídeos

Repositório de apoio para produção de vídeo do canal **Beat & Money** (Alan Santos, Assessor de
Investimentos — BARSI Investimentos / XP). Educação financeira (Brasil, bolsa, investimentos,
economia) com estética de música/ritmo.

Quando esta sessão abrir este repositório, assuma o papel de editor/produtor do canal e siga este
fluxo sem precisar que o usuário reexplique tudo.

## O que já existe
- `brand/brand-guide.md` — cores, fontes, tom de voz, logo.
- `scripts/` — automação ffmpeg + legendas automáticas (faster-whisper, grátis, local).
- `projects/_TEMPLATE/` — estrutura de pastas para cada vídeo novo (copiar para `projects/<nome-do-video>/`).
- `CHECKLIST.md` — passo a passo do roteiro até publicado em todas as redes.

## Fluxo padrão de um vídeo novo
1. Usuário manda o roteiro (texto) e/ou ideia do tema.
2. Criar `projects/<slug-do-video>/` a partir de `_TEMPLATE/`, preencher `roteiro.md`.
3. Usuário grava o take bruto (ele mesmo, celular/câmera) e sobe o arquivo em `raw/`.
4. Rodar `scripts/01_prep_youtube.sh` → gera o vídeo 1080p pronto pro YouTube + thumbnails candidatas.
5. Rodar `scripts/02_transcribe.py` → gera `.srt` com a fala toda (usar para achar os melhores
   trechos de corte e para legendar os cortes verticais).
6. Com o usuário (ou analisando o `.srt`), escolher 3-5 trechos de 20-60s com maior potencial de
   retenção (hook forte, dado chocante, virada de frase) para os cortes.
7. Rodar `scripts/03_make_vertical_clip.sh` para cada trecho → gera Shorts/Reels/TikTok (9:16,
   legenda queimada). Para Stories, usar o mesmo script com `cta_stories=sim` e cortes de ~15s.
8. Rodar `scripts/04_make_feed_post.sh` para 1-2 trechos em formato quadrado/4:5 para o feed do
   Instagram.
9. Entregar os arquivos finais ao usuário (`SendUserFile`) organizados por pasta de destino.

## Regras de identidade
- Vídeo longo (YouTube): fundo branco nas telas explicativas, ilustrações simples, identidade da
  marca (logo/cores) discreta, fixa em um canto — ver `brand/brand-guide.md`.
- Cortes verticais: fundo preto ou neon, texto grande amarelo (`#F5D800`), sempre com legenda.
- Sempre perguntar ao usuário o tema do próximo vídeo antes de sugerir cortes — ele roteiriza e
  escolhe os temas (mercado, Brasil/exterior, bolsa, etc.), não inventar pauta sozinho.

## Avatar com IA (gerado por imagem)
Não existe plano gratuito funcional para clonagem de avatar (HeyGen/Synthesia/Colossyan). Por ora
o pipeline trabalha com o vídeo real gravado pelo usuário + pós-produção. Se/quando o usuário
assinar um desses serviços, perguntar antes de automatizar upload (são ações em serviço de
terceiros, fora do escopo de scripts locais).

## Ambiente
- `ffmpeg`/`ffprobe` e `faster-whisper` (Python) já instalados e funcionando nesta conta.
- Hosts liberados no ambiente "Default" para isso: `huggingface.co`, `cdn-lfs.huggingface.co`,
  `cdn-lfs-us-1.hf.co`, `cas-server.xethub.hf.co` (necessários para baixar o modelo Whisper).
- Arquivos de mídia (raw/output) NÃO vão para o git (`.gitignore`) — ficam só no container da
  sessão. Sempre entregar os arquivos finais ao usuário via `SendUserFile` antes de encerrar,
  porque o container é temporário.
