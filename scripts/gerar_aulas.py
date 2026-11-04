#!/usr/bin/env python3
"""Gera dez videoaulas curtas de JavaScript em MP4 (16:9, 720p, 30 s)."""
from pathlib import Path
import re, subprocess, zipfile, unicodedata
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos"
TMP = ROOT / ".cache" / "aulas_js"
W, H = 1280, 720
BG = (8, 9, 12)
PANEL = (18, 20, 25)
PANEL2 = (23, 25, 30)
WHITE = (245, 245, 238)
MUTED = (158, 162, 168)
YELLOW = (255, 211, 0)
GREEN = (160, 226, 153)
BLUE = (129, 194, 255)
PURPLE = (204, 164, 255)
ORANGE = (255, 168, 91)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

def f(path, size): return ImageFont.truetype(path, size)

def wrap(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = word if not line else line + " " + word
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            line = test
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def syntax_color(line):
    s = line.strip()
    if s.startswith("//"): return MUTED
    if any(x in s for x in ('"', "'", '`')): return GREEN
    if re.search(r"\b(const|let|var|function|return|if|else|for|of|in|async|await|import|from|export|default|new|true|false|null|undefined|try|catch)\b", s): return BLUE
    if re.search(r"\d", s): return ORANGE
    return WHITE

def paint_bg(im, idx, scene):
    d = ImageDraw.Draw(im)
    # geometric editorial grid and discreet yellow orbit marks
    for x in range(32, W, 48):
        for y in range(34, H, 48):
            if ((x // 48) * 7 + (y // 48) * 3 + idx) % 11 == 0:
                d.ellipse((x, y, x+2, y+2), fill=(43, 44, 45))
    d.rectangle((0, 0, W, 7), fill=YELLOW)
    # vertical accent and a subtle corner ring
    d.line((1210, 0, 1210, H), fill=(24, 26, 29), width=1)
    d.arc((1072, -110, 1375, 193), 20, 225, fill=(35, 34, 23), width=2)
    d.ellipse((1124, 0, 1130, 6), fill=YELLOW)

def make_slide(lesson, scene, slide_no, lesson_no, total):
    im = Image.new("RGB", (W, H), BG)
    paint_bg(im, slide_no, scene)
    d = ImageDraw.Draw(im)
    # header branding
    rounded(d, (72, 40, 111, 79), 10, YELLOW)
    d.text((81, 45), "JS", font=f(MONOB, 19), fill=BG)
    d.text((126, 47), "CÓDIGO DIRETO", font=f(BOLD, 16), fill=WHITE)
    d.text((126, 68), "JAVASCRIPT · AULAS RÁPIDAS", font=f(FONT, 10), fill=MUTED)
    d.text((1037, 53), f"AULA {lesson_no:02d}  /  10", font=f(MONOB, 14), fill=YELLOW)
    d.line((72, 99, 1208, 99), fill=(43, 45, 48), width=1)

    # lesson heading and short spoken-style caption
    d.text((76, 119), scene["eyebrow"].upper(), font=f(MONOB, 13), fill=YELLOW)
    title_font = f(BOLD, 39 if len(scene["title"]) < 25 else 34)
    title_lines = wrap(d, scene["title"], title_font, 790)
    y = 147
    for line in title_lines[:2]:
        d.text((74, y), line, font=title_font, fill=WHITE)
        y += 48
    body_font = f(FONT, 18)
    by = max(y + 3, 207)
    for line in wrap(d, scene["body"], body_font, 760)[:2]:
        d.text((77, by), line, font=body_font, fill=MUTED)
        by += 27

    # code sample panel
    rounded(d, (72, 302, 824, 617), 17, PANEL, outline=(48, 50, 54), width=1)
    d.ellipse((94, 322, 104, 332), fill=(255, 99, 91))
    d.ellipse((112, 322, 122, 332), fill=(255, 189, 46))
    d.ellipse((130, 322, 140, 332), fill=(39, 201, 63))
    d.text((165, 317), scene.get("file", "script.js"), font=f(MONO, 13), fill=MUTED)
    d.line((91, 348, 805, 348), fill=(43, 45, 49), width=1)
    code = scene["code"][:9]
    start_y = 367
    line_gap = 26 if len(code) > 7 else 29
    for n, line in enumerate(code, 1):
        yy = start_y + (n-1)*line_gap
        d.text((94, yy), f"{n:02}", font=f(MONO, 14), fill=(92, 97, 103))
        clipped = line[:53]
        d.text((137, yy-1), clipped, font=f(MONO, 18), fill=syntax_color(line))

    # compact learning card at right
    rounded(d, (850, 302, 1208, 617), 17, PANEL2, outline=(48, 50, 54), width=1)
    d.text((879, 332), scene.get("tag", "IDEIA-CHAVE").upper(), font=f(MONOB, 12), fill=YELLOW)
    d.line((879, 359, 1177, 359), fill=(54, 55, 57), width=1)
    note_font = f(BOLD, 23)
    ny = 381
    for line in wrap(d, scene["note"], note_font, 294)[:4]:
        d.text((879, ny), line, font=note_font, fill=WHITE)
        ny += 31
    ny += 14
    detail_font = f(FONT, 15)
    for line in wrap(d, scene["detail"], detail_font, 294)[:5]:
        d.text((879, ny), line, font=detail_font, fill=MUTED)
        ny += 23
    # yellow terminal-like prompt
    rounded(d, (879, 559, 1178, 589), 8, (35, 33, 17))
    d.text((893, 565), scene.get("micro", "→ pratique agora"), font=f(MONOB, 12), fill=YELLOW)

    # progress strip and chapter timeline
    d.text((75, 647), "APRENDA  ·  TESTE  ·  CONSTRUA", font=f(MONOB, 11), fill=MUTED)
    d.text((1108, 644), f"{slide_no+1:02d} / {total:02d}", font=f(MONOB, 12), fill=WHITE)
    x0, x1, y0 = 75, 1069, 670
    d.rounded_rectangle((x0, y0, x1, y0+5), radius=2, fill=(47, 48, 51))
    d.rounded_rectangle((x0, y0, x0 + int((x1-x0)*(slide_no+1)/total), y0+5), radius=2, fill=YELLOW)
    for i in range(total):
        x = x0 + int((x1-x0)*i/total)
        d.ellipse((x-2, y0-2, x+2, y0+7), fill=YELLOW if i <= slide_no else (75, 76, 78))
    return im

LESSONS = [
("Variáveis: guarde valores", "let x const", [
 {"eyebrow":"01 · primeiros passos", "title":"Dê um nome aos seus dados", "body":"Variáveis guardam valores para você usar e atualizar ao longo do programa.", "code":["const curso = 'JavaScript';", "let aulas = 10;", "aulas = aulas + 1;", "console.log(curso, aulas);"], "note":"Use const por padrão", "detail":"Escolha let quando o valor realmente precisar mudar. Evite var em código novo.", "micro":"→ nomes claros ajudam"},
 {"eyebrow":"01 · declare", "title":"const cria uma referência", "body":"Perfeito para dados que não serão reatribuídos depois da criação.", "code":["const nome = 'Lia';", "const ano = 2026;", "// nome = 'Ana'  → erro", "console.log(nome);"], "note":"Não reatribua", "detail":"const não torna um objeto imutável; impede trocar a variável por outro valor.", "micro":"→ valor protegido"},
 {"eyebrow":"01 · atualize", "title":"let permite reatribuir", "body":"Use let em contadores, estados e valores que vão evoluir.", "code":["let pontos = 0;", "pontos = pontos + 5;", "pontos += 2;", "console.log(pontos); // 7"], "note":"Mude com intenção", "detail":"A atribuição simples (=) guarda um novo valor na variável.", "micro":"→ contador clássico"},
 {"eyebrow":"01 · boas práticas", "title":"Prefira nomes que expliquem", "body":"camelCase é o padrão comum para variáveis e funções em JavaScript.", "code":["const nomeDoAluno = 'Rui';", "let totalDePontos = 0;", "totalDePontos += 10;", "console.log(nomeDoAluno);"], "note":"Código legível vence", "detail":"Use nomes específicos, sem abreviações misteriosas ou letras soltas.", "micro":"→ diga o que representa"},
 {"eyebrow":"01 · experimente", "title":"Veja o resultado no console", "body":"No navegador: abra as ferramentas do desenvolvedor e teste linha por linha.", "code":["const linguagem = 'JS';", "let nivel = 1;", "nivel += 1;", "console.log(linguagem, nivel);"], "note":"Saída: JS 2", "detail":"console.log ajuda a inspecionar valores enquanto você aprende e depura.", "micro":"→ Ctrl + Shift + J"},
 {"eyebrow":"01 · revisão rápida", "title":"Const para fixo. Let para mudança.", "body":"Você já pode guardar, nomear e atualizar os primeiros valores.", "code":["const meta = 'aprender';", "let progresso = 0;", "progresso += 1;", "console.log(meta, progresso);"], "note":"Agora é com você", "detail":"Crie uma variável com sua meta e incremente um contador de estudos.", "micro":"→ próxima: tipos de dados"}
]),
("Tipos de dados essenciais", "strings numbers", [
 {"eyebrow":"02 · tipos", "title":"Todo valor tem um tipo", "body":"Conhecer o tipo evita surpresas em comparações, cálculos e mensagens.", "code":["const nome = 'Nina';", "const idade = 24;", "const ativo = true;", "const apelido = null;"], "note":"Texto, número, booleano", "detail":"Strings usam aspas. Números não. Booleanos representam verdadeiro ou falso.", "micro":"→ quatro valores comuns"},
 {"eyebrow":"02 · string", "title":"Texto entre aspas", "body":"Use template strings para misturar texto e variáveis com facilidade.", "code":["const nome = 'Nina';", "const frase = `Olá, ${nome}!`;", "console.log(frase);", "// Olá, Nina!"], "note":"Crases interpolam", "detail":"A expressão dentro de ${...} é calculada antes de montar o texto.", "micro":"→ template literal"},
 {"eyebrow":"02 · number", "title":"Números fazem contas", "body":"Inteiros e decimais pertencem ao mesmo tipo number.", "code":["const preco = 19.9;", "const quantidade = 3;", "const total = preco * quantidade;", "console.log(total); // 59.7"], "note":"Atenção à precisão", "detail":"Decimais binários podem ter pequenas imprecisões; em dinheiro use centavos inteiros.", "micro":"→ 1990 × 3 centavos"},
 {"eyebrow":"02 · boolean", "title":"true ou false", "body":"Um booleano expressa uma condição que pode ser verdadeira ou falsa.", "code":["const temAcesso = true;", "const expirado = false;", "console.log(temAcesso);", "// true"], "note":"Base das decisões", "detail":"Você vai usar booleanos dentro de if, filtros e validações.", "micro":"→ sem aspas"},
 {"eyebrow":"02 · ausência", "title":"null não é undefined", "body":"Os dois indicam ausência, mas contam histórias diferentes.", "code":["let resposta;", "const selecionado = null;", "console.log(resposta); // undefined", "console.log(selecionado); // null"], "note":"Ainda não definido", "detail":"undefined costuma ser ausência não atribuída; null é uma escolha explícita.", "micro":"→ contexto importa"},
 {"eyebrow":"02 · revisão rápida", "title":"Pergunte ao JavaScript", "body":"typeof ajuda a descobrir o tipo de um valor durante o desenvolvimento.", "code":["typeof 'oi';      // string", "typeof 42;        // number", "typeof true;      // boolean", "typeof undefined; // undefined"], "note":"Teste no console", "detail":"Experimente também typeof null: um comportamento histórico peculiar da linguagem.", "micro":"→ próxima: decisões"}
]),
("Decisões com if e else", "comparisons", [
 {"eyebrow":"03 · condições", "title":"Faça o código escolher", "body":"if executa um bloco somente quando a condição é verdadeira.", "code":["const idade = 20;", "if (idade >= 18) {", "  console.log('Pode entrar');", "}"], "note":"Condição entre parênteses", "detail":"As chaves agrupam as instruções que pertencem à decisão.", "micro":"→ teste o limite"},
 {"eyebrow":"03 · comparadores", "title":"Compare sem armadilhas", "body":"Prefira igualdade estrita: compara valor e tipo ao mesmo tempo.", "code":["5 === 5;   // true", "5 === '5'; // false", "5 !== 3;   // true", "7 >= 7;    // true"], "note":"Use === e !==", "detail":"Evite == no início: a coerção automática pode gerar resultados inesperados.", "micro":"→ tipo + valor"},
 {"eyebrow":"03 · alternativa", "title":"Cubra os dois caminhos", "body":"else roda quando a condição do if não é satisfeita.", "code":["const saldo = 12;", "if (saldo >= 20) {", "  console.log('Comprar');", "} else { console.log('Guardar'); }"], "note":"Sempre pense no caso falso", "detail":"Uma alternativa bem definida deixa o comportamento previsível.", "micro":"→ dois caminhos"},
 {"eyebrow":"03 · várias opções", "title":"Encadeie com else if", "body":"Avalie regras em ordem; a primeira condição verdadeira vence.", "code":["const nota = 82;", "if (nota >= 90) faixa = 'A';", "else if (nota >= 70) faixa = 'B';", "else faixa = 'C';"], "note":"Ordem faz diferença", "detail":"Coloque critérios mais específicos ou altos antes dos mais abrangentes.", "micro":"→ faixas de nota"},
 {"eyebrow":"03 · operador lógico", "title":"Combine condições", "body":"&& exige que ambas sejam verdadeiras; || aceita uma delas.", "code":["const temIngresso = true;", "const naLista = false;", "if (temIngresso || naLista) {", "  console.log('Bem-vinda!');", "}"], "note":"&& = E · || = OU", "detail":"Use ! para inverter um booleano: !false resulta em true.", "micro":"→ combine regras"},
 {"eyebrow":"03 · revisão rápida", "title":"Condição, bloco, alternativa", "body":"Escreva uma decisão clara e verifique também o que acontece no else.", "code":["const chuva = false;", "if (chuva) {", "  console.log('Leve guarda-chuva');", "} else { console.log('Bom passeio'); }"], "note":"Teste valores-limite", "detail":"Experimente idade 17, 18 e 19 para conferir cada caminho da regra.", "micro":"→ próxima: repetição"}
]),
("Repetição com laços", "loops", [
 {"eyebrow":"04 · repetição", "title":"Automatize tarefas repetidas", "body":"Laços executam o mesmo bloco várias vezes sem copiar e colar código.", "code":["for (let i = 0; i < 3; i++) {", "  console.log('Olá!');", "}", "// aparece 3 vezes"], "note":"Inicialize, teste, atualize", "detail":"No for: comece com i, verifique a condição, depois incremente.", "micro":"→ i++ soma um"},
 {"eyebrow":"04 · passo a passo", "title":"Entenda as três partes", "body":"O contador começa em zero e para antes de alcançar três.", "code":["for (let i = 0;", "     i < 3;", "     i++) {", "  console.log(i); // 0, 1, 2", "}"], "note":"Condição de parada", "detail":"A cada volta, i++ atualiza o contador antes do próximo teste.", "micro":"→ evite laço infinito"},
 {"eyebrow":"04 · percorra listas", "title":"for...of lê cada item", "body":"Mais simples quando você quer os valores de um array, sem índice.", "code":["const cores = ['preto', 'ouro'];", "for (const cor of cores) {", "  console.log(cor);", "}"], "note":"Um item por volta", "detail":"Use for...of para arrays e outros iteráveis, como strings.", "micro":"→ legível e direto"},
 {"eyebrow":"04 · continue", "title":"Saia na hora certa", "body":"break encerra o laço; continue pula para a próxima volta.", "code":["for (let n = 1; n <= 5; n++) {", "  if (n === 3) continue;", "  if (n === 5) break;", "  console.log(n); // 1, 2, 4", "}"], "note":"Use com intenção", "detail":"Controle de fluxo funciona, mas condições claras costumam ser melhores.", "micro":"→ evite surpresas"},
 {"eyebrow":"04 · cuidado", "title":"Verifique a condição de parada", "body":"Um contador que nunca chega ao limite pode travar a página.", "code":["let tentativas = 0;", "while (tentativas < 3) {", "  console.log(tentativas);", "  tentativas++;", "}"], "note":"Atualize o estado", "detail":"No while, a responsabilidade de alterar a condição é sua.", "micro":"→ progresso a cada volta"},
 {"eyebrow":"04 · revisão rápida", "title":"Escolha o laço mais simples", "body":"for para contagem. for...of para percorrer valores. while para condição.", "code":["const nomes = ['Bia', 'Caio'];", "for (const nome of nomes) {", "  console.log(`Oi, ${nome}`);", "}"], "note":"Menos código duplicado", "detail":"Teste um array curto e acompanhe no console cada iteração.", "micro":"→ próxima: funções"}
]),
("Funções que reutilizam", "arrow functions", [
 {"eyebrow":"05 · funções", "title":"Agrupe uma tarefa com nome", "body":"Uma função recebe dados, executa instruções e pode devolver um resultado.", "code":["function saudar(nome) {", "  return `Olá, ${nome}!`;", "}", "saudar('Lia');"], "note":"Escreva uma vez", "detail":"Depois chame a função sempre que precisar repetir aquele comportamento.", "micro":"→ entrada e saída"},
 {"eyebrow":"05 · parâmetros", "title":"Passe dados pela chamada", "body":"Parâmetros são variáveis locais que recebem os argumentos informados.", "code":["function somar(a, b) {", "  return a + b;", "}", "const total = somar(4, 6); // 10"], "note":"Pequena e previsível", "detail":"Uma função ideal resolve uma tarefa e deixa explícito o que recebe.", "micro":"→ reutilize a lógica"},
 {"eyebrow":"05 · arrow", "title":"Sintaxe curta com =>", "body":"Funções arrow são comuns em callbacks e transformações de listas.", "code":["const dobrar = (n) => {", "  return n * 2;", "};", "dobrar(5); // 10"], "note":"Arrow function", "detail":"Com uma expressão, você pode omitir chaves e return.", "micro":"→ expressão direta"},
 {"eyebrow":"05 · return", "title":"Devolva o valor calculado", "body":"return encerra a função e entrega um resultado para quem chamou.", "code":["const dobrar = n => n * 2;", "const resultado = dobrar(5);", "console.log(resultado);", "// 10"], "note":"Sem return: undefined", "detail":"console.log mostra algo; return permite usar o valor em outras partes.", "micro":"→ são coisas diferentes"},
 {"eyebrow":"05 · valor padrão", "title":"Prepare um padrão útil", "body":"Parâmetros padrão entram em ação quando o argumento não é informado.", "code":["function cumprimentar", "  (nome = 'pessoa') {", "  return `Oi, ${nome}!`;", "}", "cumprimentar();"], "note":"Evite entrada vazia", "detail":"A chamada sem argumento usa 'pessoa' como nome automaticamente.", "micro":"→ default parameter"},
 {"eyebrow":"05 · revisão rápida", "title":"Entrada → processamento → saída", "body":"Dê nomes claros e prefira funções pequenas, focadas em uma tarefa.", "code":["const aplicarDesconto =", "  (preco, taxa) => preco * (1 - taxa);", "aplicarDesconto(100, 0.1);", "// 90"], "note":"Componha ideias", "detail":"Experimente criar uma função para calcular frete ou total de uma compra.", "micro":"→ próxima: arrays"}
]),
("Arrays: map e filter", "arrays methods", [
 {"eyebrow":"06 · arrays", "title":"Guarde uma lista em um array", "body":"Arrays mantêm uma sequência de valores e começam a contar no índice zero.", "code":["const frutas = ['uva', 'pera'];", "frutas.push('manga');", "console.log(frutas[0]);", "// uva"], "note":"Primeiro índice é 0", "detail":"push adiciona um item ao final; length informa quantos itens há.", "micro":"→ listas organizadas"},
 {"eyebrow":"06 · map", "title":"Transforme cada elemento", "body":"map retorna um novo array com o resultado de cada transformação.", "code":["const precos = [10, 20, 30];", "const comTaxa = precos.map", "  (preco => preco * 1.1);", "// [11, 22, 33]"], "note":"Mesmo tamanho", "detail":"Use map quando cada item de saída corresponde a um item de entrada.", "micro":"→ transforme os dados"},
 {"eyebrow":"06 · filter", "title":"Mantenha só os que passam", "body":"filter cria uma lista nova com os elementos que satisfazem a condição.", "code":["const idades = [12, 18, 25];", "const adultos = idades.filter", "  (idade => idade >= 18);", "// [18, 25]"], "note":"Resultado pode ser menor", "detail":"A função de callback deve responder true para manter o elemento.", "micro":"→ selecione com regra"},
 {"eyebrow":"06 · encadeie", "title":"Transforme e depois filtre", "body":"Métodos de array podem formar uma sequência legível de operações.", "code":["const valores = [2, 5, 8];", "const resultado = valores", "  .map(n => n * 2)", "  .filter(n => n > 10);", "// [16]"], "note":"Leia de cima para baixo", "detail":"Primeiro dobramos todos os números, depois guardamos os maiores que 10.", "micro":"→ pipeline de dados"},
 {"eyebrow":"06 · sem mutação", "title":"Preserve a lista original", "body":"map e filter retornam um array novo e não alteram o original.", "code":["const original = [1, 2, 3];", "const dobro = original.map", "  (n => n * 2);", "console.log(original); // [1, 2, 3]"], "note":"Imutabilidade ajuda", "detail":"Evitar alterações inesperadas facilita entender e depurar o programa.", "micro":"→ origem intacta"},
 {"eyebrow":"06 · revisão rápida", "title":"Map transforma. Filter seleciona.", "body":"São duas ferramentas essenciais para trabalhar com listas no dia a dia.", "code":["const nomes = ['ana', 'bia'];", "nomes.map(nome =>", "  nome.toUpperCase());", "// ['ANA', 'BIA']"], "note":"Experimente encadear", "detail":"Crie uma lista de preços, aplique um desconto e filtre os valores baixos.", "micro":"→ próxima: objetos"}
]),
("Objetos e desestruturação", "objects", [
 {"eyebrow":"07 · objetos", "title":"Agrupe dados relacionados", "body":"Objetos associam valores a chaves, ótimos para representar entidades.", "code":["const pessoa = {", "  nome: 'Ivo',", "  idade: 31,", "  ativo: true", "};"], "note":"Chave e valor", "detail":"Cada propriedade descreve um aspecto da entidade representada.", "micro":"→ como um cadastro"},
 {"eyebrow":"07 · acesse", "title":"Leia uma propriedade", "body":"Use ponto para nomes conhecidos ou colchetes para uma chave dinâmica.", "code":["console.log(pessoa.nome);", "// Ivo", "const chave = 'idade';", "console.log(pessoa[chave]); // 31"], "note":"Ponto é mais comum", "detail":"Colchetes avaliam uma expressão entre eles antes de buscar a propriedade.", "micro":"→ chave dinâmica"},
 {"eyebrow":"07 · atualize", "title":"Mude uma propriedade", "body":"Atribua outro valor ou adicione uma nova chave ao objeto.", "code":["pessoa.idade = 32;", "pessoa.cidade = 'Teresina';", "delete pessoa.ativo;", "console.log(pessoa);"], "note":"Objetos são mutáveis", "detail":"const protege a referência, não congela automaticamente as propriedades internas.", "micro":"→ escolha mutação conscientemente"},
 {"eyebrow":"07 · desestruture", "title":"Extraia só o que precisa", "body":"A desestruturação cria variáveis a partir de propriedades do objeto.", "code":["const { nome, idade } = pessoa;", "console.log(nome);", "console.log(idade);", "// Ivo · 32"], "note":"Menos repetição", "detail":"Os nomes entre chaves correspondem às propriedades que serão extraídas.", "micro":"→ leitura mais limpa"},
 {"eyebrow":"07 · espalhe", "title":"Copie e combine propriedades", "body":"O spread cria um novo objeto com propriedades de outro objeto.", "code":["const atualizado = {", "  ...pessoa,", "  ativo: true", "};", "console.log(atualizado);"], "note":"Crie uma cópia rasa", "detail":"Propriedades posteriores sobrescrevem as anteriores com a mesma chave.", "micro":"→ padrão muito usado"},
 {"eyebrow":"07 · revisão rápida", "title":"Dados organizados em uma entidade", "body":"Leia, atualize e extraia propriedades com a sintaxe que deixa a intenção clara.", "code":["const produto = {", "  nome: 'Caderno', preco: 24", "};", "const { preco } = produto;"], "note":"Nomeie com sentido", "detail":"Use objetos para agrupar informações que fazem parte da mesma coisa.", "micro":"→ próxima: interatividade"}
]),
("DOM e eventos", "browser events", [
 {"eyebrow":"08 · navegador", "title":"Conecte JavaScript à página", "body":"O DOM é a representação da página que seu código pode consultar e alterar.", "code":["const titulo =", "  document.querySelector('h1');", "titulo.textContent =", "  'Olá, web!';"], "note":"Selecione um elemento", "detail":"querySelector encontra o primeiro elemento que corresponde ao seletor CSS.", "micro":"→ use no navegador"},
 {"eyebrow":"08 · seletores", "title":"Encontre pelo id ou classe", "body":"Seletores CSS familiares ajudam a localizar partes específicas do HTML.", "code":["const botao =", "  document.querySelector('#salvar');", "const card =", "  document.querySelector('.card');"], "note":"# id · . classe", "detail":"Se não houver correspondência, querySelector retorna null; confira antes de usar.", "micro":"→ nomes consistentes"},
 {"eyebrow":"08 · eventos", "title":"Responda a uma interação", "body":"addEventListener executa uma função quando um evento acontece.", "code":["const botao =", "  document.querySelector('#salvar');", "botao.addEventListener('click', () => {", "  console.log('Salvo!');", "});"], "note":"Evento + callback", "detail":"'click' é o evento; a função é chamada quando o usuário clica.", "micro":"→ resposta imediata"},
 {"eyebrow":"08 · formulário", "title":"Leia o valor digitado", "body":"O evento input acompanha alterações em um campo de texto.", "code":["const campo =", "  document.querySelector('#nome');", "campo.addEventListener('input', () => {", "  console.log(campo.value);", "});"], "note":"Propriedade value", "detail":"Use um formulário real para coletar dados e validar antes de enviar.", "micro":"→ interaja com o campo"},
 {"eyebrow":"08 · atualize", "title":"Altere texto com segurança", "body":"textContent atualiza texto sem interpretar o conteúdo como HTML.", "code":["const status =", "  document.querySelector('#status');", "status.textContent = 'Pronto';", "status.classList.add('ok');"], "note":"Evite innerHTML", "detail":"Para conteúdo vindo de usuários, prefira textContent e reduza riscos de injeção.", "micro":"→ segurança primeiro"},
 {"eyebrow":"08 · revisão rápida", "title":"Selecione → escute → atualize", "body":"Essa sequência transforma uma página estática em uma interface interativa.", "code":["const botao = document", "  .querySelector('#tema');", "botao.addEventListener('click', () =>", "  document.body.classList.toggle('dark'));"], "note":"Teste na página", "detail":"Coloque o script com defer ou carregue-o depois do HTML para encontrar os elementos.", "micro":"→ próxima: assíncrono"}
]),
("Async, await e fetch", "async await", [
 {"eyebrow":"09 · assincronia", "title":"Espere sem travar a página", "body":"Uma requisição leva tempo; Promises representam um resultado que chegará depois.", "code":["fetch('/api/itens')", "  .then(resposta => resposta.json())", "  .then(dados => console.log(dados));"], "note":"Fetch retorna Promise", "detail":".then encadeia etapas que rodam quando a resposta fica disponível.", "micro":"→ tempo de rede varia"},
 {"eyebrow":"09 · async", "title":"Marque uma função assíncrona", "body":"Dentro de async, await deixa o fluxo de Promises mais fácil de ler.", "code":["async function carregar() {", "  const resposta =", "    await fetch('/api/itens');", "  return resposta;", "}"], "note":"await pausa essa função", "detail":"O restante da interface continua livre enquanto a função espera a rede.", "micro":"→ não bloqueia o navegador"},
 {"eyebrow":"09 · leia JSON", "title":"Converta a resposta", "body":"A resposta HTTP precisa ser convertida para dados JSON separadamente.", "code":["const resposta =", "  await fetch('/api/itens');", "const dados = await resposta.json();", "console.log(dados);"], "note":"json() também é async", "detail":"A conversão é outra Promise; também precisa de await.", "micro":"→ dois awaits comuns"},
 {"eyebrow":"09 · erros", "title":"Trate falhas de rede", "body":"Use try/catch para lidar com erros em uma função async.", "code":["try {", "  const resposta =", "    await fetch('/api/itens');", "  if (!resposta.ok) throw Error('HTTP');", "} catch (erro) {", "  console.error(erro);", "}"], "note":"Fetch não falha em 404", "detail":"Verifique resposta.ok: fetch rejeita por falhas de rede, não por status HTTP.", "micro":"→ confira o status"},
 {"eyebrow":"09 · exemplo completo", "title":"Carregue dados com feedback", "body":"Mostre ao usuário que a aplicação está carregando e trate o resultado.", "code":["async function carregar() {", "  try {", "    const r = await fetch('/api');", "    if (!r.ok) throw Error();", "    return await r.json();", "  } catch { console.log('Tente novamente'); }", "}"], "note":"UX + tratamento", "detail":"Em apps reais, atualize o estado visual de carregamento e erro.", "micro":"→ faça a rede falhar"},
 {"eyebrow":"09 · revisão rápida", "title":"Async → await → try/catch", "body":"Leia o fluxo com clareza e prepare-se para respostas lentas ou indisponíveis.", "code":["async function buscar() {", "  const r = await fetch('/api');", "  if (!r.ok) throw Error('Falhou');", "  return await r.json();", "}"], "note":"Sempre valide a resposta", "detail":"Teste com uma URL correta, um status 404 e sem conexão.", "micro":"→ próxima: organize o projeto"}
]),
("Módulos e projeto final", "modules project", [
 {"eyebrow":"10 · módulos", "title":"Divida o código em arquivos", "body":"Módulos deixam responsabilidades claras e partes fáceis de reutilizar.", "code":["// calculos.js", "export const somar = (a, b) => a + b;", "", "// app.js", "import { somar } from './calculos.js';"], "note":"Exporta e importa", "detail":"Cada arquivo vira um módulo com entradas e saídas explícitas.", "micro":"→ mantenha a organização"},
 {"eyebrow":"10 · export", "title":"Exporte o que será reutilizado", "body":"Named exports permitem compartilhar várias funções pelo nome.", "code":["// utils.js", "export const dobro = n => n * 2;", "export const triplo = n => n * 3;", "// export nomeado"], "note":"API pequena e clara", "detail":"Exporte só as ferramentas que outros arquivos realmente precisam.", "micro":"→ responsabilidade única"},
 {"eyebrow":"10 · import", "title":"Importe pelo caminho relativo", "body":"O caminho aponta para o arquivo que oferece os recursos exportados.", "code":["import { dobro, triplo }", "  from './utils.js';", "console.log(dobro(4));", "// 8"], "note":"Chaves = named exports", "detail":"No navegador, use type='module' no script HTML para habilitar import/export.", "micro":"→ ./ arquivo local"},
 {"eyebrow":"10 · default", "title":"Use export default para um principal", "body":"Um módulo pode ter um export padrão, importado sem chaves.", "code":["// saudacao.js", "export default nome => `Oi, ${nome}`;", "// app.js", "import saudar from './saudacao.js';"], "note":"Um default por arquivo", "detail":"Os dois estilos existem; mantenha o padrão consistente no projeto.", "micro":"→ nome escolhido no import"},
 {"eyebrow":"10 · mini projeto", "title":"Junte as peças aprendidas", "body":"Um contador simples usa DOM, evento, função e variável atualizável.", "code":["let total = 0;", "const tela = document.querySelector('#total');", "document.querySelector('#mais')", "  .addEventListener('click', () => {", "    total++; tela.textContent = total;", "  });"], "note":"Já é uma aplicação", "detail":"Adicione diminuir, zerar e um estilo visual próprio ao contador.", "micro":"→ construa e compartilhe"},
 {"eyebrow":"10 · parabéns!", "title":"Você já tem a base para construir", "body":"Variáveis · condições · laços · funções · dados · DOM · rede · módulos.", "code":["const curiosidade = true;", "while (curiosidade) {", "  aprender();", "  construir();", "}"], "note":"Continue praticando", "detail":"Faça um projeto pequeno, com objetivo real. Leia erros, teste hipóteses e evolua.", "micro":"→ próximo passo: seu projeto"}
])
]

def encode_video(lesson_num, title, scenes):
    images = []
    for i, scene in enumerate(scenes):
        path = TMP / f"aula{lesson_num:02d}_slide{i+1}.png"
        make_slide(title, scene, i, lesson_num, len(scenes)).save(path, optimize=True)
        images.append(path)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    # Five 0.36-second crossfades produce a seamless 30-second, 24 fps lesson.
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error"]
    for image in images:
        cmd += ["-loop", "1", "-framerate", "24", "-t", "5.3", "-i", str(image)]
    filters = []
    for i in range(len(images)):
        filters.append(f"[{i}:v]fps=24,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{i}]")
    prev = "v0"
    for i in range(1, len(images)):
        out = f"x{i}"
        offset = 4.94 * i
        filters.append(f"[{prev}][v{i}]xfade=transition=fade:duration=0.36:offset={offset:.2f}[{out}]")
        prev = out
    cmd += ["-filter_complex", ";".join(filters), "-map", f"[{prev}]", "-t", "30", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-r", "24", "-movflags", "+faststart", "-metadata", f"title=Aula {lesson_num:02d} - {title}", "-metadata", "comment=Videoaula de JavaScript em português, 30 segundos, 16:9", str(OUT / f"aula-{lesson_num:02d}-{re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode().lower()).strip('-')}.mp4")]
    subprocess.run(cmd, check=True)


def main():
    OUT.mkdir(exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    for i, (title, slug, scenes) in enumerate(LESSONS, 1):
        print(f"Gerando aula {i:02d}/10: {title}", flush=True)
        encode_video(i, title, scenes)
    archive = OUT / "10-aulas-javascript-mp4.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3) as z:
        for video in sorted(OUT.glob("aula-*.mp4")):
            z.write(video, video.name)
    print(f"Pronto: {OUT} · {archive.stat().st_size / 1_000_000:.1f} MB no ZIP")

if __name__ == "__main__": main()
