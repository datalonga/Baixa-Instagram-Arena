# VaultReel — Baixa Instagram (Arena)

Página web **estática e responsiva** para preparar o download de vídeos **que são seus** ou para
os quais você **tem autorização**. Feita apenas com **HTML, CSS e JavaScript puro** — sem
frameworks, sem bibliotecas externas, sem Node.js e sem backend.

> **Aviso de uso:** baixe somente conteúdo próprio ou autorizado. Respeite direitos autorais,
> os termos de uso das plataformas e a legislação aplicável.

## Arquivos

| Arquivo       | Papel                                                        |
| ------------- | ------------------------------------------------------------ |
| `index.html`  | Estrutura da página, textos em pt-BR e marcação acessível.   |
| `styles.css`  | Tema claro, destaque em roxo, layout responsivo.             |
| `script.js`   | Validações, pré-visualização, mensagens e download.          |

## Como usar

1. Salve os três arquivos **na mesma pasta** (por exemplo `vaultreel/`).
2. Abra o `index.html` no navegador (dois cliques ou `Arquivo → Abrir…`).
   Não é preciso servidor, nem internet, nem instalação.
3. Escolha **Selecionar vídeo** (arquivo do seu dispositivo) ou **Usar URL direta**
   (endereço `https://` que aponta direto para o arquivo, ex.: `.../meu-video.mp4`).
4. Clique em **Preparar download**, confira a prévia e as informações do arquivo e
   depois clique em **Baixar vídeo**.

## Limitação importante: links de publicação do Instagram

Links de publicação (`instagram.com/p/...`, `/reel/...`, `fb.watch/...`) apontam para uma
**página**, não para um arquivo de vídeo. O Instagram exige sessão autenticada e não libera o
arquivo para outros sites. Uma página estática no navegador **não consegue** extrair o vídeo
desse tipo de link — e este projeto **não tenta** contornar login, permissões, CORS ou DRM.

Se você colar um link assim, a página explica a limitação e oferece a alternativa correta:
**selecionar o arquivo de vídeo salvo no seu dispositivo**.

Também não solicitamos nem armazenamos senha, cookie ou token de nenhuma rede social, e nenhuma
requisição é feita para extrair dados de páginas de redes sociais.

## O que a página faz

- Valida se o arquivo escolhido é realmente um vídeo (MIME e/ou extensão).
- Valida URLs com `new URL()` e aceita apenas **HTTPS** para endereços externos.
- Cria uma URL temporária com `URL.createObjectURL()` para arquivos locais e a revoga com
  `URL.revokeObjectURL()` ao trocar de arquivo, ao limpar e ao sair da página.
- Mostra a prévia em `<video controls>`; se o servidor bloquear o acesso (CORS, hotlink ou
  autenticação), exibe uma mensagem útil em vez de tentar burlar o bloqueio.
- Baixa com `<a download>`; quando o navegador/servidor não permite o download direto, indica
  os controles do próprio player ou a abertura em nova aba.
- Desabilita os botões durante cada operação e impede cliques duplicados.
- Mensagens de erro, sucesso e carregamento em região `aria-live`, com foco visível,
  atalho "pular para o conteúdo" e navegação completa por teclado.

## Testes rápidos (opcional)

Os testes de lógica rodam em Node.js apenas como verificação de desenvolvimento — **a página em
si não depende de Node.js**:

```bash
node --check script.js
```
