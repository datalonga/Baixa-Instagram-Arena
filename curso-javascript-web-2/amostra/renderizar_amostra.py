#!/usr/bin/env python3
"""Renderiza a aula-modelo com digitação animada, criação de arquivos e legendas."""
from pathlib import Path
import re, subprocess, math, textwrap
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
AUDIO = HERE / "narracao.mp3"
VIDEO = HERE / "aula-exemplo.mp4"
SRT = HERE / "legendas.srt"
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1280, 720, 24
BG = (7, 10, 17); PANEL = (14, 19, 29); PANEL_ALT = (19, 25, 37)
BORDER = (42, 52, 69); TEXT = (243, 246, 250); MUTED = (147, 160, 179)
YELLOW = (255, 211, 0); CYAN = (82, 218, 239); PURPLE = (172, 144, 255)
GREEN = (139, 230, 164); ORANGE = (255, 173, 92)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

CAPTIONS = [
    "Vamos criar uma pequena página e guardar dados com JavaScript.",
    "Primeiro, observe a árvore de arquivos.",
    "A pasta minha-aula terá dois arquivos: index ponto html e app ponto js.",
    "Vou criar o HTML para dar estrutura à página, adicionar um título e um espaço onde o resultado aparece.",
    "Agora, conecto o script app ponto js com o atributo defer, para o navegador executar o código depois de ler a página.",
    "No editor, crio a constante nome e guardo o texto Ana.",
    "Como esse valor não precisa mudar, uso const.",
    "Em seguida, crio a variável visitas com let, porque o contador vai ser atualizado.",
    "Somo um à variável e escrevo o resultado dentro do elemento da página.",
    "Repare: o texto falado aparece igual na legenda, e o código surge com uma animação de digitação.",
    "Por fim, confira a árvore de arquivos, execute a página e veja Ana, uma visita.",
    "Esse é o ciclo: criar o arquivo, escrever uma instrução e observar o resultado."
]
HTML_LINES = [
    "<!doctype html>",
    '<html lang="pt-BR">',
    "<head>",
    '  <meta charset="UTF-8">',
    "  <title>Minha aula</title>",
    "</head>",
    "<body>",
    '  <h1>Olá, <span id="nome"></span>!</h1>',
    '  <p>Visitas: <strong id="visitas"></strong></p>',
    '  <script src="app.js" defer></script>',
    "</body>",
    "</html>",
]
JS_LINES = [
    "const nome = 'Ana';",
    "let visitas = 0;",
    "visitas += 1;",
    "document.querySelector('#nome').textContent = nome;",
    "document.querySelector('#visitas').textContent = visitas;",
]

def font(path, size): return ImageFont.truetype(path, size)

def ffmpeg_duration(path):
    r = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", r.stderr)
    if not m: raise RuntimeError("Não foi possível medir a duração do MP3.")
    h, mm, ss = m.groups()
    return int(h)*3600 + int(mm)*60 + float(ss)

def wrapped(draw, text, ft, max_width):
    words = text.split()
    out, line = [], ""
    for word in words:
        test = word if not line else line + " " + word
        if draw.textbbox((0,0), test, font=ft)[2] <= max_width:
            line = test
        else:
            if line: out.append(line)
            line = word
    if line: out.append(line)
    return out

def timecode(t):
    ms = max(0, int(round(t*1000)))
    hh, ms = divmod(ms, 3600000)
    mm, ms = divmod(ms, 60000)
    ss, ms = divmod(ms, 1000)
    return f"{hh:02}:{mm:02}:{ss:02},{ms:03}"

def build_caption_timing(duration):
    # Speech cadence is estimated by word count; each full sentence is shown verbatim.
    weights = [max(1, len(s.split()) + 0.15*s.count(',')) for s in CAPTIONS]
    total = sum(weights)
    spans, t = [], 0.0
    for sentence, weight in zip(CAPTIONS, weights):
        end = t + duration * weight / total
        spans.append((t, end, sentence))
        t = end
    return spans

def make_srt(spans):
    with SRT.open("w", encoding="utf-8") as f:
        for i, (start, end, sentence) in enumerate(spans, 1):
            f.write(f"{i}\n{timecode(start)} --> {timecode(end)}\n{sentence}\n\n")

def color_for_line(line):
    if "//" in line: return MUTED
    if any(q in line for q in ("'", '"')): return GREEN
    if re.search(r"\b(const|let|defer|doctype|html|head|body|script)\b", line): return CYAN
    if re.search(r"\d", line): return ORANGE
    return TEXT

def draw_text_clipped(draw, xy, text, ft, fill, max_width):
    # Preserve source text but prevent accidental panel overflow.
    draw.text(xy, text, font=ft, fill=fill)

def draw_frame(t, duration, spans, frame_no):
    im = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(im)
    # Subtle grid, glow-like corner accents, and progress rail.
    for x in range(16, W, 40):
        for y in range(15, H, 40):
            if ((x//40)*5 + (y//40)*3) % 17 == 0:
                d.ellipse((x,y,x+2,y+2), fill=(28,37,52))
    d.rectangle((0,0,W,6), fill=YELLOW)
    d.arc((1070,-130,1390,190), 30, 225, fill=(42,38,25), width=2)
    d.line((36,91,1244,91), fill=BORDER, width=1)
    d.rounded_rectangle((36,23,78,65), radius=11, fill=YELLOW)
    d.text((45,29), "JS", font=font(MONOB_PATH,19), fill=BG)
    d.text((92,28), "AULA-EXEMPLO", font=font(BOLD_PATH,15), fill=TEXT)
    d.text((92,49), "DO ARQUIVO AO RESULTADO · DEMONSTRAÇÃO VISUAL", font=font(FONT_PATH,10), fill=MUTED)
    d.rounded_rectangle((1095,28,1244,60), radius=15, fill=(36,31,15), outline=(81,68,23), width=1)
    d.text((1111,37), "AMOSTRA 01", font=font(MONOB_PATH,11), fill=YELLOW)
    d.rounded_rectangle((36,78,1244,82), radius=2, fill=(35,43,56))
    d.rounded_rectangle((36,78,36+int(1208*min(1,t/duration)),82), radius=2, fill=YELLOW)

    # Three panes: file tree, animated editor, live browser preview.
    d.rounded_rectangle((36,108,269,535), radius=15, fill=PANEL, outline=BORDER, width=1)
    d.rounded_rectangle((282,108,838,535), radius=15, fill=PANEL, outline=BORDER, width=1)
    d.rounded_rectangle((851,108,1244,535), radius=15, fill=PANEL, outline=BORDER, width=1)

    # File explorer and file-creation animation.
    d.text((55,126), "EXPLORER", font=font(MONOB_PATH,11), fill=MUTED)
    d.text((55,154), "PROJETO", font=font(BOLD_PATH,12), fill=TEXT)
    folder_t = spans[2][0]
    folder_done = t >= folder_t + 0.15
    if folder_done:
        d.text((57,190), "⌄", font=font(BOLD_PATH,18), fill=YELLOW)
        d.text((79,191), "minha-aula", font=font(BOLD_PATH,13), fill=YELLOW)
        d.rounded_rectangle((54,222,253,258), radius=7, fill=(28,38,54) if t < spans[3][0] else (21,28,39))
        d.text((74,231), "◈  index.html", font=font(MONO_PATH,12), fill=CYAN)
    else:
        d.text((57,190), "+", font=font(BOLD_PATH,18), fill=YELLOW)
        d.text((80,194), "criar pasta...", font=font(FONT_PATH,12), fill=MUTED)
    if t >= spans[2][0] + 1.0:
        d.rounded_rectangle((54,262,253,298), radius=7, fill=(28,38,54) if t >= spans[5][0] else (21,28,39))
        d.text((74,271), "JS   app.js", font=font(MONO_PATH,12), fill=PURPLE)
    else:
        d.text((80,274), "arquivo novo...", font=font(FONT_PATH,11), fill=MUTED)
    d.line((56,324,249,324), fill=BORDER, width=1)
    d.text((56,341), "ETAPAS", font=font(MONOB_PATH,10), fill=MUTED)
    steps = [("01", "Criar pasta", 0.0), ("02", "index.html", spans[3][0]), ("03", "app.js", spans[5][0]), ("04", "Executar", spans[10][0])]
    for n,(num,label,start) in enumerate(steps):
        yy=369+n*35
        active = start <= t
        d.ellipse((57,yy,76,yy+19), fill=YELLOW if active else (39,48,61))
        d.text((61,yy+3), "✓" if active else num, font=font(BOLD_PATH,9), fill=BG if active else MUTED)
        d.text((86,yy+2), label, font=font(FONT_PATH,12), fill=TEXT if active else MUTED)

    # Editor chrome and tabs.
    d.rounded_rectangle((282,108,838,151), radius=15, fill=(22,29,42))
    d.rectangle((282,137,838,151), fill=(22,29,42))
    active_html = t < spans[5][0]
    d.rounded_rectangle((294,116,451,149), radius=8, fill=PANEL if active_html else (22,29,42))
    d.text((306,125), "‹›  index.html", font=font(MONO_PATH,11), fill=CYAN if active_html else MUTED)
    d.rounded_rectangle((458,116,575,149), radius=8, fill=(22,29,42) if active_html else PANEL)
    d.text((470,125), "JS  app.js", font=font(MONO_PATH,11), fill=MUTED if active_html else PURPLE)
    d.text((796,125), "⋯", font=font(BOLD_PATH,16), fill=MUTED)

    # Determine code typing progress from narration beats.
    if t < spans[3][0]:
        code_lines=[]; filename="index.html"; p=0.0; active_file="HTML"
    elif t < spans[5][0]:
        filename="index.html"; active_file="HTML"
        p=min(1,max(0,(t-spans[3][0])/(spans[5][0]-spans[3][0])))
        code_lines=HTML_LINES
    else:
        filename="app.js"; active_file="JS"
        p=min(1,max(0,(t-spans[5][0])/(spans[10][0]-spans[5][0])))
        code_lines=JS_LINES
    d.text((302,164), filename, font=font(MONOB_PATH,10), fill=YELLOW)
    # Add lines character by character, retaining a moving caret at the insertion point.
    code_font=font(MONO_PATH,14)
    visible_chars=int(sum(len(x) for x in code_lines)*p) if code_lines else 0
    consumed=0; cursor_xy=None
    for i,line in enumerate(code_lines):
        yy=190+i*27
        show=max(0,min(len(line),visible_chars-consumed))
        part=line[:show]
        d.text((303,yy), f"{i+1:02}", font=font(MONO_PATH,11), fill=(92,106,124))
        d.text((340,yy), part, font=code_font, fill=color_for_line(line))
        if show < len(line) and cursor_xy is None and p < 1:
            caret_x=340+d.textbbox((0,0),part,font=code_font)[2]
            cursor_xy=(caret_x,yy+2)
        consumed += len(line)
    if cursor_xy and (frame_no//12)%2==0:
        d.rectangle((cursor_xy[0],cursor_xy[1],cursor_xy[0]+2,cursor_xy[1]+18), fill=YELLOW)
    if not code_lines:
        d.text((303,191), "// o código aparece enquanto é explicado", font=font(MONO_PATH,13), fill=MUTED)
    d.rounded_rectangle((302,492,815,519), radius=8, fill=(18,27,39))
    d.text((316,499), "DIGITAÇÃO AO VIVO", font=font(MONOB_PATH,10), fill=CYAN if active_file=="HTML" else PURPLE)
    d.text((496,499), "⌨ cursor + sintaxe", font=font(FONT_PATH,10), fill=MUTED)

    # Browser preview demonstrates the effect of the code.
    d.rounded_rectangle((851,108,1244,151), radius=15, fill=(22,29,42))
    d.rectangle((851,137,1244,151), fill=(22,29,42))
    for j,c in enumerate(((255,99,91),(255,189,46),(39,201,63))):
        d.ellipse((868+j*18,122,878+j*18,132), fill=c)
    d.rounded_rectangle((933,117,1224,140), radius=11, fill=(13,18,28))
    d.text((949,121), "file:///minha-aula", font=font(FONT_PATH,9), fill=MUTED)
    d.text((872,169), "PRÉVIA DO NAVEGADOR", font=font(MONOB_PATH,10), fill=MUTED)
    preview_ready=t >= spans[10][0]
    if preview_ready:
        # Softly reveal live result in the page pane.
        alpha=min(1.0,(t-spans[10][0]+0.2)/0.8)
        d.rounded_rectangle((870,198,1226,480), radius=12, fill=(248,250,252))
        d.rounded_rectangle((887,218,1209,455), radius=9, fill=(255,255,255))
        d.text((907,247), "Olá, Ana!", font=font(BOLD_PATH,24), fill=(23,31,46))
        d.text((907,294), "Visitas:", font=font(FONT_PATH,17), fill=(80,91,105))
        d.rounded_rectangle((1001,286,1046,322), radius=9, fill=(255,244,184))
        d.text((1016,291), "1", font=font(MONOB_PATH,19), fill=(72,57,0))
        d.line((907,347,1185,347), fill=(225,230,236), width=1)
        d.text((907,367), "Resultado atualizado pelo JavaScript", font=font(FONT_PATH,10), fill=(92,106,122))
    else:
        d.rounded_rectangle((870,198,1226,480), radius=12, fill=(12,18,29), outline=(36,48,66), width=1)
        d.text((898,275), "Sua página ganha vida", font=font(BOLD_PATH,17), fill=(89,105,125))
        d.text((898,305), "quando o script é executado.", font=font(FONT_PATH,13), fill=(74,89,109))
        d.rounded_rectangle((898,354,1079,382), radius=8, fill=(19,31,46))
        d.text((912,362), "aguardando app.js...", font=font(MONO_PATH,10), fill=CYAN)
    d.rounded_rectangle((870,492,1226,519), radius=8, fill=(18,27,39))
    d.ellipse((883,501,893,511), fill=GREEN if preview_ready else ORANGE)
    d.text((903,499), "EXECUTADO" if preview_ready else "AGUARDANDO", font=font(MONOB_PATH,10), fill=GREEN if preview_ready else ORANGE)

    # Exact spoken sentence is the visible caption (same source string).
    current=next((s for s in spans if s[0] <= t < s[1]), spans[-1])
    sentence=current[2]
    d.rounded_rectangle((36,552,1244,700), radius=17, fill=(13,19,30), outline=(54,67,86), width=1)
    d.rounded_rectangle((55,571,60,681), radius=2, fill=YELLOW)
    d.text((77,568), "NARRAÇÃO · LEGENDA LITERAL", font=font(MONOB_PATH,10), fill=YELLOW)
    caption_font=font(BOLD_PATH,25)
    lines=wrapped(d,sentence,caption_font,1110)
    y=594 if len(lines)<=2 else 586
    for line in lines[:3]:
        d.text((77,y), line, font=caption_font, fill=TEXT)
        y+=34
    return im

def main():
    if not AUDIO.exists(): raise FileNotFoundError(AUDIO)
    duration=ffmpeg_duration(AUDIO)
    spans=build_caption_timing(duration)
    make_srt(spans)
    total_frames=math.ceil(duration*FPS)
    cmd=[FF,"-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",str(AUDIO),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart","-metadata","title=Aula de exemplo - JavaScript visual e sincronizado","-metadata","comment=Narração em português brasileiro; legenda textual sincronizada; exemplo de digitação animada",str(VIDEO)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(total_frames):
            t=min(duration-0.001,i/FPS)
            frame=draw_frame(t,duration,spans,i)
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        status=proc.wait()
        if status: raise subprocess.CalledProcessError(status,cmd)
    except Exception:
        if proc.poll() is None: proc.kill()
        raise
    print(f"Vídeo: {VIDEO} ({duration:.1f} s, 1280x720)")
    print(f"Legendas: {SRT} ({len(CAPTIONS)} frases literais)")

if __name__ == "__main__": main()
