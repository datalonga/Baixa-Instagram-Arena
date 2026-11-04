# Aula de demonstração — Arquivos, HTML e variáveis

**Objetivo:** mostrar como o curso combina texto falado igual à legenda, criação simulada de arquivos, digitação de código e prévia do navegador.

## Narração e legendas sincronizadas

1. Vamos criar uma pequena página e guardar dados com JavaScript.
2. Primeiro, observe a árvore de arquivos.
3. A pasta minha-aula terá dois arquivos: index ponto html e app ponto js.
4. Vou criar o HTML para dar estrutura à página, adicionar um título e um espaço onde o resultado aparece.
5. Agora, conecto o script app ponto js com o atributo defer, para o navegador executar o código depois de ler a página.
6. No editor, crio a constante nome e guardo o texto Ana.
7. Como esse valor não precisa mudar, uso const.
8. Em seguida, crio a variável visitas com let, porque o contador vai ser atualizado.
9. Somo um à variável e escrevo o resultado dentro do elemento da página.
10. Repare: o texto falado aparece igual na legenda, e o código surge com uma animação de digitação.
11. Por fim, confira a árvore de arquivos, execute a página e veja Ana, uma visita.
12. Esse é o ciclo: criar o arquivo, escrever uma instrução e observar o resultado.

## HTML criado no exemplo

```html
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Minha aula</title>
</head>
<body>
  <h1>Olá, <span id="nome"></span>!</h1>
  <p>Visitas: <strong id="visitas"></strong></p>
  <script src="app.js" defer></script>
</body>
</html>
```

## JavaScript digitado no exemplo

```js
const nome = 'Ana';
let visitas = 0;
visitas += 1;
document.querySelector('#nome').textContent = nome;
document.querySelector('#visitas').textContent = visitas;
```

## Saída esperada no navegador

Olá, Ana!  
Visitas: 1
