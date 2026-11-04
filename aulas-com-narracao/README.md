# Aulas de JavaScript com narração

Esta pasta reúne a nova versão narrada das 10 aulas. Cada MP4 mantém o vídeo original em **16:9, 1280 × 720 e 30 segundos**, agora com locução feminina em português brasileiro, em tom didático e natural. A voz é uma geração sintética com estilo de narração moderna; não é produzida pelo serviço ElevenLabs.

## Arquivos

- `videos/` — 10 aulas narradas em MP4.
- `narracoes/` — faixas MP3 individuais da locução.
- `videos-com-narracao.zip` — pacote com os 10 vídeos narrados.
- `roteiros.md` — textos usados na locução.
- `muxar_videos.py` — script para combinar as faixas com os vídeos originais.

Os vídeos originais e demais arquivos do projeto foram mantidos sem alteração.

## Regenerar os MP4 narrados

Na raiz do repositório, com Python 3:

```bash
python3 -m venv .venv
.venv/bin/pip install imageio-ffmpeg
.venv/bin/python aulas-com-narracao/muxar_videos.py
```
