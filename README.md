# 10 aulas rápidas de JavaScript

Dez videoaulas em português, cada uma com **30 segundos**, formato **16:9 (1280 × 720)** e entrega em **MP4/H.264**. Visual editorial em preto, amarelo e branco, com exemplos de código e transições entre seis telas por aula. Os vídeos são legendados na tela e não têm narração nem faixa de áudio.

## Conteúdo

1. Variáveis: `const` e `let`
2. Tipos de dados essenciais
3. Decisões com `if` e `else`
4. Repetição com laços
5. Funções e arrow functions
6. Arrays: `map` e `filter`
7. Objetos e desestruturação
8. DOM e eventos
9. `async`, `await` e `fetch`
10. Módulos e mini projeto final

Os MP4 individuais estão em [`videos/`](videos/). Para baixar o conjunto, use [`videos/10-aulas-javascript-mp4.zip`](videos/10-aulas-javascript-mp4.zip).

## Regenerar os vídeos

Com Python 3 e uma fonte DejaVu Sans instalados:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/gerar_aulas.py
```

O script usa Pillow para criar as telas e `imageio-ffmpeg` para codificar e empacotar os MP4.
