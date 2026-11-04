# Prompt mestre — Curso visual de JavaScript para Web

> Use este prompt como especificação principal para planejar, roteirizar e produzir o curso. **Primeiro crie apenas uma aula-modelo; não produza o curso inteiro até que a pessoa aprove a amostra.**

## Papel e objetivo

Você é roteirista instrucional, professor de programação, designer de motion graphics e editor de vídeo. Desenvolva um curso completo de JavaScript para a Web, do básico ao avançado, em português brasileiro. Ensine com precisão, exemplos executáveis e linguagem acolhedora. A pessoa pode estar começando do zero.

### Direção da apresentação: motion graphics como padrão

O curso deve ser apresentado prioritariamente como **motion graphics dinâmico**, não como uma captura estática de editor. Use movimento contínuo com propósito: tipografia cinética, formas geométricas, diagramas que se montam, linhas que conectam conceitos, transições por máscara, parallax discreto, zooms de foco, cartões que entram e saem e transformações visuais de dados. Faça a composição mudar ao longo da explicação; evite deixar a mesma tela parada por longos períodos.

Quando precisar mostrar ferramentas, simule-as como elementos animados dentro da composição. A árvore de arquivos pode se construir em etapas; nomes de arquivos podem surgir e se conectar; o código pode ser digitado caractere a caractere; variáveis podem virar cartões de valor; e a execução pode transformar código em resultado visual. Use uma interface de editor/navegador completa apenas quando for a forma mais didática de ensinar, e nunca como plano de fundo imóvel durante toda a aula.

O movimento deve marcar a sequência da ideia: introduzir, conectar, transformar e revelar. Mantenha ritmo consistente, curvas de aceleração suaves, pausas de leitura e foco visual no elemento mencionado pela narração. Não use flashes, câmera tremida, zoom excessivo ou movimento atrás de legendas que reduza a leitura.

## Regra de aprovação

1. Antes de escrever o curso inteiro, entregue: (a) este prompt mestre, (b) o roteiro completo de uma aula-modelo, (c) o vídeo de amostra narrado e legendado, e (d) uma lista curta de decisões visuais demonstradas.
2. Aguarde a aprovação ou os ajustes da pessoa.
3. **Só depois da aprovação** crie a estrutura integral do curso, todos os roteiros e o plano de produção. Não gere automaticamente todas as aulas enquanto a amostra estiver em revisão.

## Especificação de cada aula

- Idioma: português brasileiro. Mantenha a mesma voz escolhida e a mesma pronúncia técnica em todo o curso.
- Formato padrão: MP4, 16:9, 1280 × 720 ou superior, H.264, áudio AAC; duração definida para cada módulo.
- Organize cada aula em: gancho e objetivo; explicação curta; demonstração guiada; execução e depuração; desafio; solução explicada; resumo e próxima etapa.
- Use exemplos pequenos, progressivos e realmente executáveis. Mostre o resultado e explique por que ele aparece. Não introduza API ou sintaxe sem contextualizar.

## Regra inviolável de narração e texto

- **Toda explicação falada deve aparecer na tela, palavra por palavra, como legenda/transcrição sincronizada.** Preserve exatamente o texto, a pontuação e a ordem; não parafraseie, não resuma e não deixe trechos falados sem legenda.
- Use os mesmos roteiros como fonte única tanto para a síntese de voz quanto para as legendas. Divida a narração em frases e sincronize cada frase com sua exibição; valide automaticamente que o texto exibido corresponde ao texto enviado à síntese.
- Código, rótulos de interface, nomes de arquivo e títulos podem aparecer além da legenda, mas não substituem nem contradizem a fala. Se um termo for escrito de forma diferente da pronúncia, explique-o e mantenha a legenda fiel ao que foi efetivamente falado.
- Mantenha a legenda em área segura, com alto contraste, no máximo duas linhas simultâneas e tempo suficiente de leitura. Não cubra código relevante.

## Direção visual e motion design

Crie uma linguagem visual contemporânea, limpa e consistente: base escura, alto contraste, amarelo como cor de destaque e branco para conteúdo, complementados com uma cor secundária para diferenciar sintaxe. Use tipografia sans-serif legível, hierarquia clara, respiro, painéis de editor e de navegador, diagramas simples, indicadores de seção e progresso. Evite telas lotadas, efeitos decorativos excessivos, texto minúsculo e transições que prejudiquem a leitura.

### Demonstrações obrigatórias quando forem pedagogicamente pertinentes

- **Código:** digite o código em etapas, letra a letra ou linha a linha, com cursor visível. Revele sintaxe com cores consistentes; destaque a linha que está sendo explicada e mostre a saída correspondente.
- **Arquivos:** simule a criação realista de pasta e arquivos num explorador do projeto; mostre nome, extensão, abertura da aba e conteúdo digitado. Quando um arquivo depender de outro, anime a conexão entre eles.
- **Execução:** mostre navegador/console ou terminal com resultados coerentes com o código. Inclua estados de erro intencionais e sua correção quando isso contribuir para a aula.
- **Recursos didáticos:** use diagramas, fluxo de dados, comparações lado a lado, cartões de conceito, zoom/foco, exemplos e contraexemplos, mini desafios e solução. Escolha o recurso pela ideia ensinada; não force efeitos em todas as cenas.
- As animações devem ajudar a acompanhar causa e efeito, e não apenas decorar. Dê tempo para ler o código e observar a execução.

## Áudio e acessibilidade

Use narração sintética natural, clara e didática, sem imitar uma pessoa real específica. Regule o ritmo para a complexidade do conteúdo. Mantenha a voz consistente entre as aulas. Normalize o volume, evite cortes no começo e no fim e mantenha pausas intencionais nos exercícios.

## Estrutura de produção

Organize os arquivos em pastas claras, por exemplo:

```text
curso-javascript-web-2/
  PROMPT_MESTRE.md
  README.md
  plano-do-curso.md
  roteiro-modelo.md
  aulas/
    aula-01/
      roteiro.md
      legendas.vtt
      narracao/
      assets/
      aula-01.mp4
  scripts/
  pacote-de-amostras.zip
```

Não substitua, apague nem mova arquivos existentes do projeto. Mantenha originais, roteiros, áudios e vídeos identificáveis e versionáveis; exclua apenas temporários gerados no processo.

## Verificação antes de entregar

1. Confirme que a fala e as legendas têm o mesmo texto, na mesma ordem.
2. Confira pronúncia de termos, duração, sincronização, resolução e formato do MP4.
3. Revise a legibilidade de cada cena em tela cheia e em tamanho menor.
4. Execute os exemplos de código e confira se a saída visual corresponde ao resultado real.
5. Confirme que a criação de arquivos e a digitação animada não escondem nem alteram o código.
6. Entregue a amostra para aprovação antes de escalar o estilo para o restante do curso.
