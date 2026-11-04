#!/usr/bin/env python3
"""Renderiza o primeiro lote do curso: vídeos longos com narração em PT-BR."""
from pathlib import Path
import re, subprocess, zipfile
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
VOICE = HERE / "narracoes"
OUT = HERE / "videos"
TMP = ROOT / ".cache" / "curso_javascript"
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1280, 720
BG = (8, 9, 12); PANEL = (19, 21, 26); PANEL2 = (24, 26, 31)
WHITE = (246, 246, 240); MUTED = (166, 169, 174); YELLOW = (255, 211, 0)
GREEN = (164, 229, 160); BLUE = (134, 198, 255); ORANGE = (255, 177, 101)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, ft, width):
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textbbox((0, 0), trial, font=ft)[2] <= width:
            current = trial
        else:
            if current: lines.append(current)
            current = word
    if current: lines.append(current)
    return lines


def draw_card(lesson, no, scene, slide, total, filename):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for x in range(35, W, 48):
        for y in range(30, H, 48):
            if ((x//48)*7 + (y//48)*3 + slide) % 13 == 0:
                d.ellipse((x, y, x+2, y+2), fill=(42, 43, 45))
    d.rectangle((0, 0, W, 7), fill=YELLOW)
    d.arc((1070, -120, 1380, 190), 20, 225, fill=(39, 36, 22), width=2)
    d.rounded_rectangle((72, 38, 112, 78), radius=10, fill=YELLOW)
    d.text((81, 44), "JS", font=font(MONOB, 18), fill=BG)
    d.text((127, 45), "JAVASCRIPT PARA WEB", font=font(BOLD, 15), fill=WHITE)
    d.text((127, 66), "CURSO DO ZERO · AULAS COMPLETAS", font=font(FONT, 10), fill=MUTED)
    d.text((1025, 51), f"AULA {no:02d} / 08", font=font(MONOB, 14), fill=YELLOW)
    d.line((72, 96, 1208, 96), fill=(45, 47, 50), width=1)

    d.text((76, 116), scene["kicker"].upper(), font=font(MONOB, 12), fill=YELLOW)
    ft = font(BOLD, 37 if len(scene["title"]) < 28 else 32)
    y = 143
    for line in wrap(d, scene["title"], ft, 1080)[:2]:
        d.text((75, y), line, font=ft, fill=WHITE)
        y += 46
    body_ft = font(FONT, 18)
    by = max(y+2, 197)
    for line in wrap(d, scene["body"], body_ft, 1100)[:2]:
        d.text((77, by), line, font=body_ft, fill=MUTED)
        by += 26

    # Explanatory code pane
    d.rounded_rectangle((72, 285, 831, 615), radius=17, fill=PANEL, outline=(49, 51, 56), width=1)
    for x, c in [(96,(255,99,91)),(114,(255,189,46)),(132,(39,201,63))]:
        d.ellipse((x, 305, x+10, 315), fill=c)
    d.text((164, 300), scene.get("filename", "app.js"), font=font(MONO, 13), fill=MUTED)
    d.line((92, 328, 810, 328), fill=(44, 46, 50), width=1)
    code = scene.get("code", [])[:9]
    for i, line in enumerate(code):
        yy = 349 + i*27
        s = line.strip()
        color = MUTED if s.startswith("//") else GREEN if any(q in s for q in ("'", '"', '`')) else BLUE if re.search(r"\b(const|let|if|else|for|of|return|true|false|typeof|script|defer)\b", s) else ORANGE if re.search(r"\d", s) else WHITE
        d.text((95, yy), f"{i+1:02}", font=font(MONO, 13), fill=(91, 95, 100))
        d.text((137, yy-2), line[:59], font=font(MONO, 17), fill=color)

    # Key idea card
    d.rounded_rectangle((855, 285, 1208, 615), radius=17, fill=PANEL2, outline=(49, 51, 56), width=1)
    d.text((883, 313), scene.get("tag", "IDEIA-CHAVE").upper(), font=font(MONOB, 12), fill=YELLOW)
    d.line((883, 339, 1179, 339), fill=(55, 57, 60), width=1)
    h = 369
    for line in wrap(d, scene["note"], font(BOLD, 22), 295)[:4]:
        d.text((883, h), line, font=font(BOLD, 22), fill=WHITE); h += 30
    h += 11
    for line in wrap(d, scene["detail"], font(FONT, 15), 295)[:6]:
        d.text((883, h), line, font=font(FONT, 15), fill=MUTED); h += 22
    d.rounded_rectangle((883, 565, 1180, 590), radius=7, fill=(37, 34, 18))
    d.text((895, 570), scene.get("prompt", "→ teste no navegador"), font=font(MONOB, 11), fill=YELLOW)

    d.text((75, 643), "ENTENDA  ·  TESTE  ·  PRATIQUE", font=font(MONOB, 11), fill=MUTED)
    d.text((1118, 640), f"{slide+1:02d}/{total:02d}", font=font(MONOB, 12), fill=WHITE)
    x0, x1, y0 = 75, 1069, 670
    d.rounded_rectangle((x0,y0,x1,y0+5), radius=2, fill=(46,48,51))
    d.rounded_rectangle((x0,y0,x0+int((x1-x0)*(slide+1)/total),y0+5), radius=2, fill=YELLOW)
    im.save(filename, optimize=True)


LESSONS = {
1: {
 "title":"Seu ambiente e a primeira página", "audio":["aula-01-parte-1.mp3","aula-01-parte-2.mp3","aula-01-parte-3.mp3","desafio-final-comum.mp3"], "pause":38,
 "sections":[
  [
   {"kicker":"01 · mapa da web", "title":"HTML, CSS e JavaScript trabalham juntos", "body":"HTML descreve o conteúdo; CSS define a apresentação; JavaScript cria comportamento.", "code":["index.html  → conteúdo", "styles.css  → aparência", "app.js      → comportamento"], "note":"Três ferramentas, papéis diferentes", "detail":"Nesta aula vamos preparar os arquivos e executar JavaScript no navegador.", "prompt":"→ primeiro projeto"},
   {"kicker":"01 · primeiros passos", "title":"Crie uma pasta de projeto", "body":"Comece simples: uma página HTML e um arquivo JavaScript ligado a ela.", "filename":"meu-projeto/", "code":["meu-projeto/", "├── index.html", "└── app.js"], "note":"Organização mínima", "detail":"Crie os arquivos no editor que já usa. Por enquanto não precisa instalar frameworks.", "prompt":"→ nomes exatos"},
   {"kicker":"01 · objetivo", "title":"Vamos executar a primeira instrução", "body":"O navegador lê a página e executa o arquivo app.js que vamos conectar.", "filename":"o que vamos construir", "code":["página HTML", "     ↓", "app.js", "     ↓", "console do navegador"], "note":"O console será nosso laboratório", "detail":"Ele mostra resultados e erros para ajudar a entender o que o código está fazendo.", "prompt":"→ abra o DevTools"}
  ],
  [
   {"kicker":"02 · conecte os arquivos", "title":"Use a tag script com defer", "body":"O atributo defer espera o HTML ficar pronto antes de executar o JavaScript.", "filename":"index.html", "code":["<!doctype html>", "<html lang=\"pt-BR\">", "<head><title>Meu projeto</title></head>", "<body>", "  <h1>Olá, web!</h1>", "  <script src=\"app.js\" defer></script>", "</body>", "</html>"], "note":"Defer evita corrida", "detail":"O navegador baixa o script em paralelo e o executa depois de ler a página.", "prompt":"→ confira o caminho"},
   {"kicker":"02 · execute", "title":"Abra a página no navegador", "body":"Salve os arquivos e abra index.html. O título deve aparecer na página.", "filename":"app.js", "code":["console.log('Olá, JavaScript!');"], "note":"Uma linha já é JavaScript", "detail":"Se o console não mostrar a mensagem, confira o nome do arquivo e o atributo src.", "prompt":"→ salve e atualize"},
   {"kicker":"02 · ferramentas", "title":"Encontre a aba Console", "body":"Clique com o botão direito na página e escolha Inspecionar ou Inspecionar elemento.", "filename":"DevTools · Console", "code":["console.log('Olá, JavaScript!');", "// Olá, JavaScript!"], "note":"Observe a saída", "detail":"Também dá para digitar expressões no console e executá-las sem alterar o arquivo.", "prompt":"→ experimente 8 + 4"}
  ],
  [
   {"kicker":"03 · depuração", "title":"Leia erros com curiosidade", "body":"Uma mensagem vermelha aponta o arquivo e, muitas vezes, a linha que precisa de atenção.", "filename":"app.js", "code":["console.log('Olá');", "console.log(8 + 4);", "// Saída: 12"], "note":"Erro não é fracasso", "detail":"Confira aspas, parênteses, chaves, nomes de arquivos e se a alteração foi salva.", "prompt":"→ um ajuste por vez"},
   {"kicker":"03 · pratique", "title":"Sua vez: personalize a página", "body":"Escreva duas mensagens no console e uma conta. Antes de executar, preveja a saída.", "filename":"desafio", "code":["console.log('Meu nome é...');", "console.log(8 + 4);", "// O que aparece?"], "note":"Pause e tente sozinho", "detail":"Não copie ainda. Digite o exemplo, execute e explique o que aconteceu.", "prompt":"→ pausa para praticar"},
   {"kicker":"03 · solução", "title":"Compare e explique o resultado", "body":"A primeira instrução mostra o texto; a segunda calcula a soma e mostra doze.", "filename":"app.js", "code":["console.log('Meu nome é Ana');", "console.log(8 + 4);", "// Meu nome é Ana", "// 12"], "note":"Prever → executar → observar", "detail":"Esse ciclo de prática vai acompanhar você nas próximas aulas do curso.", "prompt":"→ próxima: valores e variáveis"}
  ]
 ],
 "challenge": {"title":"Desafio final: primeira mensagem", "body":"Personalize o texto e registre no console o resultado de uma conta.", "code":["console.log('Olá, meu nome é ...');", "console.log(8 + 4);"], "solution":["console.log('Olá, meu nome é Bia');", "console.log(8 + 4); // 12"], "note":"Pause o vídeo e faça no seu app.js"}
},
2: {
 "title":"Variáveis, tipos e operadores", "audio":["aula-02-parte-1.mp3","aula-02-parte-2.mp3","aula-02-parte-3.mp3","desafio-final-comum.mp3"], "pause":20,
 "sections":[
  [
   {"kicker":"01 · variáveis", "title":"Guarde valores com nomes claros", "body":"Uma variável dá um nome a um valor para que o programa possa consultá-lo depois.", "filename":"app.js", "code":["const curso = 'JavaScript';", "let pontos = 0;", "pontos += 5;"], "note":"Const por padrão", "detail":"Use let apenas quando for reatribuir o valor, como num contador.", "prompt":"→ nomes comunicam intenção"},
   {"kicker":"01 · declare", "title":"Const protege a referência", "body":"Use const quando não pretende atribuir um valor diferente a essa variável.", "filename":"const.js", "code":["const nome = 'Lia';", "const ano = 2026;", "console.log(nome);"], "note":"Sem reatribuição", "detail":"Prefira valores e nomes que descrevam o problema que seu código resolve.", "prompt":"→ padrão recomendado"},
   {"kicker":"01 · atualize", "title":"Let é para valores que mudam", "body":"Contadores e estados que evoluem ao longo do programa podem usar let.", "filename":"let.js", "code":["let pontos = 0;", "pontos = pontos + 5;", "pontos += 2;", "console.log(pontos); // 7"], "note":"Atualize com intenção", "detail":"O operador mais igual soma à variável e grava o novo valor nela.", "prompt":"→ teste no console"}
  ],
  [
   {"kicker":"02 · tipos", "title":"Texto, número e booleano", "body":"Os tipos básicos afetam como o JavaScript interpreta cada valor.", "filename":"tipos.js", "code":["const nome = 'Nina'; // string", "const idade = 24;    // number", "const ativo = true;  // boolean"], "note":"Aspas significam texto", "detail":"Booleanos são true ou false. Números podem ser inteiros ou decimais.", "prompt":"→ sem aspas no número"},
   {"kicker":"02 · ausência", "title":"Null e undefined têm contextos", "body":"Ambos aparecem quando não há um valor, mas não significam a mesma situação.", "filename":"ausencia.js", "code":["let resposta;", "const escolhido = null;", "typeof resposta; // undefined"], "note":"Ausência definida ou não", "detail":"typeof ajuda a investigar o tipo de um valor durante o desenvolvimento.", "prompt":"→ faça seus próprios testes"},
   {"kicker":"02 · template string", "title":"Monte mensagens com variáveis", "body":"Crases e cifrão com chaves inserem o valor dentro de uma frase.", "filename":"mensagem.js", "code":["const nome = 'Lia';", "const frase = `Olá, ${nome}!`;", "console.log(frase);"], "note":"Interpolação legível", "detail":"A expressão entre chaves é calculada antes de a mensagem ser exibida.", "prompt":"→ tente outro nome"}
  ],
  [
   {"kicker":"03 · operadores", "title":"Faça contas e comparações", "body":"Operadores aritméticos calculam; comparadores devolvem true ou false.", "filename":"operadores.js", "code":["10 + 2;  // 12", "10 * 2;  // 20", "10 >= 18; // false"], "note":"Separe valor e resultado", "detail":"Teste cada expressão no console para criar intuição sobre os tipos.", "prompt":"→ maior, menor, igual"},
   {"kicker":"03 · igualdade", "title":"Prefira a comparação estrita", "body":"Três sinais de igual comparam valor e tipo, sem coerção automática.", "filename":"comparacao.js", "code":["5 === 5;   // true", "5 === '5'; // false", "5 !== 3;   // true"], "note":"Evite surpresas", "detail":"Dois sinais de igual podem converter tipos. No início, escolha === e !==.", "prompt":"→ tipo também importa"},
   {"kicker":"03 · prática", "title":"Combine regras com e e ou", "body":"Use && quando as duas partes precisam ser verdadeiras, e || quando basta uma.", "filename":"logica.js", "code":["idade >= 18 && temConvite", "temConta || modoConvidado", "!estaCarregando"], "note":"Teste os casos possíveis", "detail":"Nomeie condições complexas para deixar a regra mais fácil de entender.", "prompt":"→ próxima: if e laços"}
  ]
 ],
 "challenge": {"title":"Desafio final: total e elegibilidade", "body":"Calcule três itens e verifique se o cliente atingiu o valor mínimo.", "code":["const total = 12 + 8 + 5;", "const elegivel = total >= 25;"], "solution":["const total = 12 + 8 + 5; // 25", "const elegivel = total >= 25; // true"], "note":"Preveja os tipos e o resultado"}
},
3: {
 "title":"Decisões e laços de repetição", "audio":["aula-03-parte-1.mp3","aula-03-parte-2.mp3","aula-03-parte-3.mp3","desafio-final-comum.mp3"], "pause":36,
 "sections":[
  [
   {"kicker":"01 · if", "title":"Escolha um caminho com uma condição", "body":"O bloco if executa somente quando a expressão entre parênteses resulta em true.", "filename":"acesso.js", "code":["const idade = 20;", "if (idade >= 18) {", "  console.log('Pode entrar');", "}"], "note":"Condição dentro dos parênteses", "detail":"As chaves agrupam as instruções que pertencem a esse caminho.", "prompt":"→ experimente 17 e 18"},
   {"kicker":"01 · else", "title":"Defina também o caso contrário", "body":"O bloco else roda quando a condição do if é falsa.", "filename":"acesso.js", "code":["if (idade >= 18) {", "  console.log('Pode entrar');", "} else {", "  console.log('Ainda não');", "}"], "note":"Cubra os dois caminhos", "detail":"Pense no que deve ocorrer para verdadeiro e falso, não apenas no caso feliz.", "prompt":"→ teste valores-limite"},
   {"kicker":"01 · alternativas", "title":"Encadeie regras com else if", "body":"Quando há várias faixas, avalie primeiro a regra mais alta.", "filename":"nota.js", "code":["if (nota >= 90) faixa = 'A';", "else if (nota >= 70) faixa = 'B';", "else faixa = 'C';"], "note":"A ordem é importante", "detail":"Uma condição ampla pode capturar valores antes da regra mais específica.", "prompt":"→ teste 69, 70 e 90"}
  ],
  [
   {"kicker":"02 · lógica", "title":"Combine mais de uma regra", "body":"&& representa E; || representa OU; ! inverte um booleano.", "filename":"promocao.js", "code":["const elegivel = cadastrado", "  && total >= 100;", "const liberado = admin", "  || temConvite;"], "note":"Traduza a regra em voz alta", "detail":"Parênteses e nomes descritivos deixam expressões complexas mais legíveis.", "prompt":"→ enumere os resultados"},
   {"kicker":"02 · casos de teste", "title":"Verifique combinações diferentes", "body":"Cubra ambos verdadeiros, ambos falsos e cada caso em que só um é verdadeiro.", "filename":"teste-logico.js", "code":["true && true;   // true", "true && false;  // false", "true || false;  // true", "!false;         // true"], "note":"Raciocine com uma tabela", "detail":"Essa prática reduz bugs em acesso, descontos, filtros e validações.", "prompt":"→ mude uma condição"},
   {"kicker":"02 · clareza", "title":"Dê nome a condições importantes", "body":"Se a expressão estiver difícil de ler, divida-a em valores booleanos nomeados.", "filename":"regra.js", "code":["const temConvite = convite !== null;", "const compraElegivel = total >= 100;", "const podeEntrar = temConvite", "  || compraElegivel;"], "note":"Código é comunicação", "detail":"Um nome claro explica a regra sem exigir que alguém decifre cada operador.", "prompt":"→ facilite o futuro você"}
  ],
  [
   {"kicker":"03 · for", "title":"Repita uma quantidade conhecida", "body":"O for combina início, condição e atualização do contador numa estrutura compacta.", "filename":"contagem.js", "code":["for (let i = 0; i < 3; i++) {", "  console.log(i);", "}", "// 0, 1, 2"], "note":"Comece, teste, atualize", "detail":"A condição fica falsa antes de imprimir três, porque usamos menor que.", "prompt":"→ preveja antes de rodar"},
   {"kicker":"03 · for of", "title":"Percorra valores com for of", "body":"Quando o índice não importa, for of destaca o valor atual em cada repetição.", "filename":"cores.js", "code":["const cores = ['preto', 'ouro'];", "for (const cor of cores) {", "  console.log(cor);", "}"], "note":"Uma cor por volta", "detail":"Use esse padrão para arrays e outras coleções iteráveis.", "prompt":"→ acrescente uma cor"},
   {"kicker":"03 · exercício", "title":"Junte decisão e repetição", "body":"Percorra várias notas e classifique cada valor com uma condição.", "filename":"desafio.js", "code":["const notas = [62, 70, 95];", "for (const nota of notas) {", "  // classifique com if", "}"], "note":"Prever → executar → revisar", "detail":"Confira a solução depois de tentar. Erros ajudam a descobrir a lógica.", "prompt":"→ próxima: funções"}
  ]
 ],
 "challenge": {"title":"Desafio final: classifique três notas", "body":"Use for of e if/else para mostrar aprovado ou em recuperação.", "code":["const notas = [62, 70, 95];", "for (const nota of notas) {", "  // escreva a condição"], "solution":["for (const nota of notas) {", "  if (nota >= 70) console.log('Aprovado');", "  else console.log('Recuperação');", "}"], "note":"Pause e escreva sem copiar"}
}
}


def duration_seconds(path):
    result = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    if not match:
        raise RuntimeError(f"Não consegui ler a duração de {path}")
    h, m, s = match.groups()
    return int(h)*3600 + int(m)*60 + float(s)


def render_one(no, data):
    OUT.mkdir(parents=True, exist_ok=True); TMP.mkdir(parents=True, exist_ok=True)
    part_paths = [VOICE / name for name in data["audio"]]
    for path in part_paths:
        if not path.exists(): raise FileNotFoundError(path)
    durations = [duration_seconds(p) for p in part_paths]
    scene_groups = data["sections"]
    scenes = [s for group in scene_groups for s in group]
    total_slides = len(scenes) + 2
    image_paths, durations_for_video = [], []
    index = 0
    for group_index, group in enumerate(scene_groups):
        chunk_duration = durations[group_index]
        for scene in group:
            p = TMP / f"a{no:02d}_s{index+1:02d}.png"
            draw_card(data["title"], no, scene, index, total_slides, p)
            image_paths.append(p)
            durations_for_video.append(chunk_duration / len(group))
            index += 1
    challenge = data["challenge"]
    intro = {"kicker":"DESAFIO FINAL · TENTE ANTES DA SOLUÇÃO", "title":challenge["title"], "body":challenge["body"], "filename":"desafio.js", "code":challenge["code"], "note":challenge["note"], "detail":"Pause se quiser mais tempo. A próxima tela mostra uma solução possível.", "prompt":"→ sua vez de programar"}
    p = TMP / f"a{no:02d}_desafio.png"; draw_card(data["title"], no, intro, index, total_slides, p)
    image_paths.append(p); durations_for_video.append(durations[3] + data["pause"] * 0.65); index += 1
    solution = {"kicker":"SOLUÇÃO POSSÍVEL · HÁ OUTRAS RESPOSTAS", "title":"Confira uma forma de resolver", "body":challenge["body"], "filename":"solucao.js", "code":challenge["solution"], "note":"O mais importante é entender por quê", "detail":"Compare sua previsão com a saída e explique cada linha com suas palavras.", "prompt":"→ pronto para a próxima aula"}
    p = TMP / f"a{no:02d}_solucao.png"; draw_card(data["title"], no, solution, index, total_slides, p)
    image_paths.append(p); durations_for_video.append(data["pause"] * 0.35)

    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error"]
    for image, duration in zip(image_paths, durations_for_video):
        cmd += ["-loop", "1", "-framerate", "24", "-t", f"{duration:.3f}", "-i", str(image)]
    audio_start = len(image_paths)
    for audio in part_paths:
        cmd += ["-i", str(audio)]
    nslides = len(image_paths)
    filters=[]
    for i in range(nslides):
        filters.append(f"[{i}:v]fps=24,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{i}]")
    vinputs = "".join(f"[v{i}]" for i in range(nslides))
    filters.append(f"{vinputs}concat=n={nslides}:v=1:a=0[vout]")
    ain = []
    for i in range(len(part_paths)):
        filters.append(f"[{audio_start+i}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]")
        ain.append(f"[a{i}]")
    filters.append(f"{''.join(ain)}concat=n={len(part_paths)}:v=0:a=1[aout]")
    video_duration = sum(durations_for_video)
    cmd += ["-filter_complex", ";".join(filters), "-map", "[vout]", "-map", "[aout]", "-t", f"{video_duration:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-metadata", f"title=Aula {no:02d} - {data['title']}", "-metadata", "comment=Curso de JavaScript para iniciantes; português brasileiro; aula completa", str(OUT / f"aula-{no:02d}.mp4")]
    subprocess.run(cmd, check=True)
    print(f"Aula {no:02d} pronta: {video_duration/60:.1f} min", flush=True)


def main():
    for no in (1,2,3): render_one(no, LESSONS[no])
    archive = HERE / "modulos-01-a-03.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3) as z:
        for p in sorted(OUT.glob("aula-*.mp4")): z.write(p, f"videos/{p.name}")
        for p in sorted(VOICE.glob("*.mp3")): z.write(p, f"narracoes/{p.name}")
        z.write(HERE / "README.md", "README.md")
        z.write(HERE / "roteiros.md", "roteiros.md")
    print(f"Pacote pronto: {archive}")

if __name__ == "__main__": main()
