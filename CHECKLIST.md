# Checklist — do roteiro ao publicado

## 1. Antes de gravar
- [ ] Tema definido (você escolhe — mercado, Brasil/exterior, bolsa, economia...)
- [ ] Roteiro escrito (pode mandar em texto solto pro Claude organizar)
- [ ] Hook forte nos primeiros 3-5 segundos (frase de impacto, no estilo dos seus posts)
- [ ] Vídeo alvo: 8-10 min

## 2. Gravação (seu lado)
- [ ] Gravar o take no celular/câmera, fundo neutro, áudio limpo
- [ ] Subir o arquivo bruto pro Claude Code (anexar no chat ou me mandar o link do Drive)

## 3. Pós-produção (eu faço, dentro do Claude Code)
- [ ] `scripts/01_prep_youtube.sh` → vídeo 1080p + thumbnails candidatas
- [ ] `scripts/02_transcribe.py` → legenda completa (.srt)
- [ ] Escolher 3-5 trechos fortes pra cortar (com você, olhando a transcrição)
- [ ] `scripts/03_make_vertical_clip.sh` × cada trecho → Shorts / Reels / TikTok (com legenda)
- [ ] `scripts/03_make_vertical_clip.sh cta_stories=sim` × 1-2 trechos curtos → Stories
- [ ] `scripts/04_make_feed_post.sh` × 1-2 trechos → post de feed (quadrado/4:5)
- [ ] Revisar thumbnail (ajustar no Canva se precisar de texto/arte por cima)

## 4. Publicação (seu lado)
- [ ] YouTube: título + descrição + thumbnail + tags
- [ ] Reels/Shorts/TikTok: legenda curta + hashtags do nicho
- [ ] Feed Instagram: legenda completa estilo atual (pergunta + contexto + CTA)
- [ ] Stories: sequência com link/menção pro vídeo completo

## 5. Depois de publicar
- [ ] Marcar no `projects/<video>/roteiro.md` a data de publicação e links finais
