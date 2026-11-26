#!/usr/bin/env bash
# Confere se as ferramentas da esteira estão prontas.
set -e
ok() { echo "OK   - $1"; }
fail() { echo "FALTA- $1"; }

command -v ffmpeg >/dev/null 2>&1 && ok "ffmpeg" || fail "ffmpeg"
command -v ffprobe >/dev/null 2>&1 && ok "ffprobe" || fail "ffprobe"
command -v python3 >/dev/null 2>&1 && ok "python3" || fail "python3"
python3 -c "import faster_whisper" >/dev/null 2>&1 && ok "faster-whisper (legendas automáticas)" || fail "faster-whisper (rode: pip3 install faster-whisper)"
