# Curso completo de JavaScript para a Web

Curso pensado para quem está começando do zero, com aulas completas em português brasileiro, exemplos de código na tela, desafios e locução masculina selecionada na audição. Cada vídeo é 16:9, 1280 × 720, com duração-alvo de 5 a 8 minutos.

## Programa do curso

1. **Seu ambiente e a primeira página** — HTML, CSS e JavaScript, projeto mínimo, `script defer`, DevTools e console. ✅ Vídeo pronto.
2. **Variáveis, tipos e operadores** — `const`, `let`, tipos primitivos, template strings, comparações e lógica. ✅ Vídeo pronto.
3. **Decisões e laços de repetição** — `if`, `else`, operadores lógicos, `for` e `for...of`. ✅ Vídeo pronto.
4. **Funções e escopo** — parâmetros, retorno, arrow functions, escopo e funções pequenas.
5. **Arrays e objetos** — coleções, `map`, `filter`, `find`, propriedades e desestruturação.
6. **DOM e eventos** — selecionar elementos, atualizar a página e reagir a cliques.
7. **Formulários e estado** — entrada, validação, renderização de listas e `localStorage`.
8. **Fetch e projeto final** — APIs, `async`/`await`, erros, módulos e construção de uma pequena aplicação web.

## Vídeos disponíveis

Os módulos 1 a 3 estão em [`videos/`](videos/). Faixas de narração e textos ficam em [`narracoes/`](narracoes/) e [`roteiros.md`](roteiros.md). O pacote parcial está em [`modulos-01-a-03.zip`](modulos-01-a-03.zip). Os módulos 4 a 8 fazem parte do plano e serão produzidos nos próximos lotes.

As telas dão tempo para acompanhar os exemplos. Cada aula termina com um desafio e uma pausa para praticar antes da solução.

## Regenerar as aulas atuais

Na raiz do repositório, com Python 3:

```bash
python3 -m venv .venv
.venv/bin/pip install pillow imageio-ffmpeg
.venv/bin/python curso-javascript-web/renderizar_curso.py
```
