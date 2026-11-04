#!/usr/bin/env python3
"""Nova amostra: aula de JavaScript apresentada como motion graphics."""
from pathlib import Path
import re, subprocess, math
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
AUDIO = HERE / "narracao.mp3"
VIDEO = HERE / "aula-exemplo-motion.mp4"
SRT = HERE / "legendas-motion.srt"
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1280, 720, 24
BG=(7,10,17); WHITE=(245,247,251); MUTED=(155,168,187); YELLOW=(255,211,0)
CYAN=(67,220,242); PURPLE=(178,142,255); GREEN=(140,235,169); ORANGE=(255,174,94)
PANEL=(17,24,37); PANEL2=(22,31,47); BORDER=(52,67,88); DEEP=(11,16,27)
F_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_MONO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
F_MONOB="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
CAPTIONS=[
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
HTML=["<!doctype html>",'<html lang="pt-BR">',"<head>",'  <meta charset="UTF-8">',"  <title>Minha aula</title>","</head>","<body>",'  <h1>Olá, <span id="nome"></span>!</h1>','  <p>Visitas: <strong id="visitas"></strong></p>','  <script src="app.js" defer></script>',"</body>","</html>"]
JS=["const nome = 'Ana';","let visitas = 0;","visitas += 1;","document.querySelector('#nome').textContent = nome;","document.querySelector('#visitas').textContent = visitas;"]

def ft(path,size): return ImageFont.truetype(path,max(1,int(size)))
def smooth(v):
    v=max(0,min(1,v)); return v*v*(3-2*v)
def mix(a,b,p): return a+(b-a)*p
def clamp(v,a=0,b=1): return max(a,min(b,v))
def centered(draw,xy,text,font,fill):
    bb=draw.textbbox((0,0),text,font=font); draw.text((xy[0]-(bb[2]-bb[0])/2,xy[1]),text,font=font,fill=fill)
def rounded(draw,box,r,fill,outline=None,width=1): draw.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)
def wrap(draw,text,font,width):
    lines=[]; cur=""
    for word in text.split():
        test=word if not cur else cur+" "+word
        if draw.textbbox((0,0),test,font=font)[2]<=width: cur=test
        else:
            if cur: lines.append(cur)
            cur=word
    if cur: lines.append(cur)
    return lines

def duration_of_audio(path):
    r=subprocess.run([FF,"-hide_banner","-i",str(path)],capture_output=True,text=True)
    m=re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)",r.stderr)
    if not m: raise RuntimeError("Não foi possível medir a narração")
    h,mi,s=m.groups(); return int(h)*3600+int(mi)*60+float(s)

def spans_for(duration):
    weights=[len(s.split())+0.15*s.count(',') for s in CAPTIONS]
    total=sum(weights); t=0; spans=[]
    for sentence,w in zip(CAPTIONS,weights):
        end=t+duration*w/total; spans.append((t,end,sentence)); t=end
    return spans

def srt_time(t):
    ms=max(0,int(round(t*1000))); hh,ms=divmod(ms,3600000); mm,ms=divmod(ms,60000); ss,ms=divmod(ms,1000)
    return f"{hh:02}:{mm:02}:{ss:02},{ms:03}"
def save_srt(spans):
    with SRT.open("w",encoding="utf-8") as f:
        for i,(a,b,s) in enumerate(spans,1): f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{s}\n\n")

def line_color(s):
    if any(q in s for q in ("'",'"')): return GREEN
    if re.search(r"\b(const|let|defer|script|html|body)\b",s): return CYAN
    return WHITE

def code_card(d,box,title,lines,progress,active_line=None,scale=1.0):
    x,y,w,h=box; rounded(d,(x,y,x+w,y+h),20,PANEL,outline=BORDER,width=1)
    d.rounded_rectangle((x,y,x+w,y+47),radius=20,fill=PANEL2)
    d.rectangle((x,y+28,x+w,y+47),fill=PANEL2)
    d.text((x+22,y+15),title,font=ft(F_MONOB,12),fill=YELLOW)
    d.text((x+w-52,y+14),"⋯",font=ft(F_BOLD,18),fill=MUTED)
    total=sum(len(q) for q in lines); reveal=int(total*clamp(progress)); used=0
    line_gap=23 if len(lines)>10 else 28
    code_size=13 if len(lines)>10 else 15
    code_font=ft(F_MONO,code_size)
    for i,line in enumerate(lines):
        yy=y+68+i*line_gap
        if yy>y+h-25: break
        visible=max(0,min(len(line),reveal-used))
        if active_line is not None and i<active_line: visible=len(line)
        part=line[:visible]
        d.text((x+23,yy),f"{i+1:02}",font=ft(F_MONO,12),fill=(91,110,131))
        d.text((x+62,yy),part,font=code_font,fill=line_color(line))
        if visible<len(line) and reveal>=used and (active_line is None or i==active_line):
            cx=x+62+d.textbbox((0,0),part,font=code_font)[2]
            d.rectangle((cx,yy+1,cx+2,yy+20),fill=YELLOW)
        used+=len(line)

def icon_file(d,x,y,label,color,scale=1.0):
    w=178*scale; h=55*scale; rounded(d,(x,y,x+w,y+h),11,PANEL2,outline=color,width=1)
    d.rounded_rectangle((x+12*scale,y+13*scale,x+34*scale,y+42*scale),radius=4*scale,fill=color)
    d.text((x+45*scale,y+17*scale),label,font=ft(F_MONOB,12*scale),fill=WHITE)

def draw_bg(d,t):
    # Moving dotted field and diagonal energy traces, kept low-contrast behind content.
    for i in range(32):
        x=(i*83 + int(t*(9+(i%4)*3)))%W
        y=114+(i*47)%390
        r=1+(i%3==0)
        col=(30,40,56) if i%3 else (35,42,55)
        d.ellipse((x-r,y-r,x+r,y+r),fill=col)
    for i in range(5):
        yy=128+i*84+int(5*math.sin(t*.45+i))
        d.line((0,yy,1280,yy-20),fill=(17,24,37),width=1)

def draw_folder_scene(d,t,span):
    u=clamp((t-span[0])/max(.1,span[1]-span[0]))
    x=mix(560,360,smooth(u)); y=268
    # Folder body draws from a traveling stroke.
    w=225*smooth(u); h=140*smooth(u)
    if w>4 and h>4:
        rounded(d,(x-w/2,y-h/2,x+w/2,y+h/2),18,(24,33,49),outline=YELLOW,width=3)
        d.polygon([(x-w/2,y-h/2+17),(x-w/2+58,y-h/2+17),(x-w/2+76,y-h/2),(x-w/2+129,y-h/2),(x-w/2+145,y-h/2+17),(x+w/2,y-h/2+17),(x+w/2,y-h/2+39),(x-w/2,y-h/2+39)],fill=YELLOW)
        centered(d,(x,y+5),"minha-aula",ft(F_MONOB,16),WHITE)
    # Animated links and files pop into a project constellation.
    for j,(label,color,yy) in enumerate([("index.html",CYAN,195),("app.js",PURPLE,337)]):
        start=span[0]+(span[1]-span[0])*(.19+j*.35)
        p=smooth((t-start)/.75)
        if p>0:
            fx=mix(820,922,p); fy=yy+10*math.sin(t*2+j)
            x1=x+w/2-5; y1=y
            d.line((x1,y1,mix(x1,fx,p),mix(y1,fy,p)),fill=color,width=2)
            rr=8+3*math.sin(t*4+j)
            d.ellipse((mix(x1,fx,p)-rr,mix(y1,fy,p)-rr,mix(x1,fx,p)+rr,mix(y1,fy,p)+rr),fill=color)
            if p>.9: icon_file(d,fx,fy-27,label,color)
    centered(d,(640,442),"UMA PASTA  ·  DOIS ARQUIVOS  ·  UM PROJETO",ft(F_MONOB,12),MUTED)

def draw_page_result(d,t,progress):
    # Browser-like page scales in quickly so the result appears during the spoken explanation.
    qprogress=clamp(progress); eased=smooth(qprogress)
    scale=.55+.45*eased; x=710+180*(1-eased); y=185+50*(1-eased)
    w=450*scale; h=260*scale
    if qprogress>.01:
        rounded(d,(x,y,x+w,y+h),20,(246,248,252),outline=(255,255,255),width=1)
        chrome_h=40*scale
        d.rounded_rectangle((x,y,x+w,y+chrome_h),radius=20*scale,fill=(226,232,240))
        d.rectangle((x,y+23*scale,x+w,y+chrome_h),fill=(226,232,240))
        for k,c in enumerate(((255,103,94),(255,190,56),(45,204,96))):
            rr=4*scale; cx=x+(17+15*k)*scale; cy=y+20*scale; d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=c)
        if qprogress>.2:
            inner=x+28*scale
            d.text((inner,y+76*scale),"Olá, Ana!",font=ft(F_BOLD,22*scale),fill=(21,32,48))
            d.text((inner,y+126*scale),"Visitas:",font=ft(F_REG,16*scale),fill=(89,101,119))
            # Counter flips from 0 to 1.
            q=clamp((t-(spans_for_global[10][0]))/.8)
            shown="0" if q<.45 else "1"
            rounded(d,(inner+100*scale,y+115*scale,inner+142*scale,y+153*scale),9*scale,(255,244,184))
            d.text((inner+115*scale,y+120*scale),shown,font=ft(F_MONOB,19*scale),fill=(77,61,0))
            d.line((inner,y+183*scale,inner+360*scale,y+183*scale),fill=(224,230,238),width=max(1,int(scale)))
            d.text((inner,y+201*scale),"JavaScript atualizou a página",font=ft(F_REG,10*scale),fill=(96,109,127))

def draw_frame(t,duration,spans,frame_no):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im); draw_bg(d,t)
    # Minimal moving masthead and a thin progress pulse.
    d.rounded_rectangle((42,27,82,67),radius=11,fill=YELLOW)
    d.text((50,33),"JS",font=ft(F_MONOB,18),fill=BG)
    d.text((98,30),"MOTION GRAPHICS",font=ft(F_BOLD,14),fill=WHITE)
    d.text((98,51),"DO ARQUIVO AO RESULTADO",font=ft(F_REG,10),fill=MUTED)
    d.rounded_rectangle((1087,33,1238,61),radius=14,fill=(33,29,16),outline=(83,69,24),width=1)
    d.text((1105,41),"AULA · AMOSTRA",font=ft(F_MONOB,10),fill=YELLOW)
    d.line((42,83,1238,83),fill=(43,54,72),width=2)
    d.line((42,83,42+1196*clamp(t/duration),83),fill=YELLOW,width=3)

    # Milestone times correspond to the same sentence-by-sentence narration captions.
    t_files=spans[2][0]; t_html=spans[3][0]; t_script=spans[4][0]; t_const=spans[5][0]
    t_let=spans[7][0]; t_dom=spans[8][0]; t_motion=spans[9][0]; t_output=spans[10][0]; t_final=spans[11][0]
    if t<t_files:
        p=smooth(t/max(.1,t_files))
        centered(d,(640,172),"JAVASCRIPT",ft(F_BOLD,74),WHITE)
        centered(d,(640,257),"DO ARQUIVO AO RESULTADO",ft(F_MONOB,17),YELLOW)
        # Kinetic orbit rings and a pulsing folder glyph.
        for j in range(3):
            r=66+j*28+8*math.sin(t*2+j)
            d.arc((640-r,356-r,640+r,356+r),int(t*60+j*80),int(t*60+j*80+240),fill=(YELLOW,CYAN,PURPLE)[j],width=2)
        pulse=1+0.12*math.sin(t*3)
        rounded(d,(585,301,695,411),22,(24,34,51),outline=YELLOW,width=3)
        d.polygon([(598,323),(627,323),(637,313),(666,313),(677,323),(682,323),(682,338),(598,338)],fill=YELLOW)
        centered(d,(640,364),".js",ft(F_MONOB,20*pulse),WHITE)
    elif t<t_html:
        draw_folder_scene(d,t,(t_files,t_html))
    elif t<t_const:
        # The HTML file flies into a motion-code layout and types progressively.
        p=clamp((t-t_html)/max(.1,t_const-t_html))
        slide=smooth(clamp((t-t_html)/1.0))
        cardx=mix(1280,72,slide)
        code_card(d,(cardx,137,708,370),"index.html",HTML,p)
        # Animated HTML hierarchy on the right.
        cx=940; cy=229
        centered(d,(cx,cy-44),"ESTRUTURA DA PÁGINA",ft(F_MONOB,12),MUTED)
        nodes=[("<h1>",CYAN),("<p>",PURPLE),("<script>",YELLOW)]
        for i,(label,col) in enumerate(nodes):
            q=smooth(clamp((p-(.18+i*.22))/.18)); yy=cy+i*74
            if q>0:
                rounded(d,(cx-77*q,yy,cx+77*q,yy+43),12,(22,31,47),outline=col,width=2)
                centered(d,(cx,yy+12),label,ft(F_MONOB,14),WHITE)
                if i<2:
                    d.line((cx,yy+44,cx,yy+70*q),fill=col,width=2)
        centered(d,(cx,481),"CONTEÚDO EM CAMADAS",ft(F_MONOB,10),MUTED)
    elif t<t_let:
        # Const is treated as a stable value: code tokens snap into a value card.
        p=clamp((t-t_const)/max(.1,t_let-t_const))
        centered(d,(640,150),"UM VALOR COM NOME",ft(F_MONOB,14),MUTED)
        code="const nome = 'Ana';"
        reveal=int(len(code)*smooth(p))
        rounded(d,(180,212,1100,311),20,PANEL,outline=BORDER,width=1)
        d.text((220,245),code[:reveal],font=ft(F_MONOB,34),fill=CYAN)
        if reveal<len(code) and (frame_no//12)%2==0:
            xx=220+d.textbbox((0,0),code[:reveal],font=ft(F_MONOB,34))[2]
            d.rectangle((xx,249,xx+3,285),fill=YELLOW)
        # Tokens detach, travel, and assemble into a value card.
        q=smooth(clamp((p-.28)/.65))
        rounded(d,(254,361,489,441),16,(23,33,50),outline=CYAN,width=2)
        centered(d,(371,386),"const  →  fixo",ft(F_MONOB,16),CYAN)
        d.line((489,401,644,401),fill=YELLOW,width=3)
        for j in range(7):
            xx=500+j*20
            if xx<644*q+500: d.ellipse((xx,396,xx+9,405),fill=YELLOW)
        rounded(d,(653,350,1016,455),20,(30,26,49),outline=PURPLE,width=2)
        d.text((682,373),"nome",font=ft(F_MONOB,13),fill=MUTED)
        centered(d,(834,407),"Ana",ft(F_BOLD,30),WHITE)
        # Lock icon emphasizes stable assignment.
        if p>.7:
            d.arc((1042,367,1101,426),180,360,fill=YELLOW,width=4)
            rounded(d,(1037,397,1107,450),10,(45,37,12),outline=YELLOW,width=2)
            centered(d,(1072,409),"✓",ft(F_BOLD,25),YELLOW)
    elif t<t_output:
        # let counter animates and DOM connections draw toward a page.
        p=clamp((t-t_let)/max(.1,t_output-t_let))
        centered(d,(640,132),"UM VALOR QUE MUDA",ft(F_MONOB,14),MUTED)
        code="let visitas = 0;"
        code2="visitas += 1;"
        rounded(d,(99,177,735,267),19,PANEL,outline=BORDER,width=1)
        d.text((131,206),code[:int(len(code)*smooth(clamp(p*2)))],font=ft(F_MONOB,27),fill=PURPLE)
        rounded(d,(99,281,735,371),19,PANEL,outline=BORDER,width=1)
        d.text((131,310),code2[:int(len(code2)*smooth(clamp((p-.28)*1.6)))],font=ft(F_MONOB,24),fill=CYAN)
        # Counter flips 0 -> 1 in a luminous circle.
        cx,cy=956,276; r=95+5*math.sin(t*3)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(24,31,47),outline=YELLOW,width=4)
        amount=smooth(clamp((p-.38)/.35)); number="1" if amount>.72 else "0"
        centered(d,(cx,cy-42),number,ft(F_BOLD,91),YELLOW)
        centered(d,(cx,cy+59),"VISITAS",ft(F_MONOB,12),MUTED)
        # Arrow of data flow.
        d.line((735,326,832,326),fill=CYAN,width=3)
        d.polygon([(832,326),(817,317),(817,335)],fill=CYAN)
    elif t<t_final:
        # DOM code and the preview move into a single causal composition.
        p=clamp((t-t_output)/max(.1,t_final-t_output))
        html_progress=1.0
        code_lines=JS
        code_card(d,(58,136,710,374),"app.js",code_lines,html_progress)
        draw_page_result(d,t,p)
        # Data wires travel from selector code to the rendered text and counter.
        start=(732,292)
        end=(815,317)
        q=clamp((t-t_dom)/max(.1,t_final-t_dom))
        mid=(mix(start[0],end[0],q),mix(start[1],end[1],q))
        d.line((start[0],start[1],mid[0],mid[1]),fill=CYAN,width=3)
        d.ellipse((mid[0]-6,mid[1]-6,mid[0]+6,mid[1]+6),fill=YELLOW)
        rounded(d,(458,470,814,509),13,(20,31,46),outline=(57,88,112),width=1)
        centered(d,(636,482),"CÓDIGO  →  DOM  →  RESULTADO",ft(F_MONOB,11),CYAN)
    else:
        # Closing loop: an orbiting four-step sequence.
        centered(d,(640,139),"O CICLO DE QUEM PROGRAMA",ft(F_BOLD,30),WHITE)
        labels=[("CRIAR",CYAN),("ESCREVER",PURPLE),("EXECUTAR",YELLOW),("OBSERVAR",GREEN)]
        cx,cy=640,322; rad=244
        d.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),outline=(37,49,67),width=2)
        for i,(label,color) in enumerate(labels):
            angle=-math.pi/2+i*math.pi/2+t*.20
            x=cx+rad*math.cos(angle); y=cy+rad*math.sin(angle)
            rr=68+4*math.sin(t*2+i)
            d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(20,29,44),outline=color,width=3)
            centered(d,(x,y-11),label,ft(F_MONOB,12),WHITE)
            # Orbiting dot travels along each arc.
            a=angle+0.26*math.sin(t*2)
            ox=cx+(rad+5)*math.cos(a); oy=cy+(rad+5)*math.sin(a)
            d.ellipse((ox-6,oy-6,ox+6,oy+6),fill=color)
        rounded(d,(477,279,803,366),19,(18,26,40),outline=BORDER,width=1)
        centered(d,(640,296),"PREVER  ·  TESTAR  ·  APRENDER",ft(F_MONOB,13),YELLOW)

    # Exact, sentence-level caption; animated entrance, unchanged wording.
    current_index=next((i for i,s in enumerate(spans) if s[0]<=t<s[1]),len(spans)-1)
    start,end,caption=spans[current_index]
    entr=smooth(clamp((t-start)/.24)); cy=544+int((1-entr)*20)
    rounded(d,(36,cy,1244,700),18,(13,20,32),outline=(53,68,88),width=1)
    d.rounded_rectangle((56,cy+19,61,cy+137),radius=2,fill=YELLOW)
    d.text((78,cy+16),"FALA · TEXTO EXATO",font=ft(F_MONOB,10),fill=YELLOW)
    cfont=ft(F_BOLD,24)
    lines=wrap(d,caption,cfont,1110)
    y=cy+44 if len(lines)<=2 else cy+35
    for line in lines[:3]:
        d.text((78,y),line,font=cfont,fill=WHITE); y+=34
    return im

def main():
    duration=duration_of_audio(AUDIO); spans=spans_for(duration); save_srt(spans)
    global spans_for_global
    spans_for_global=spans
    nframes=math.ceil(duration*FPS)
    cmd=[FF,"-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",str(AUDIO),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart","-metadata","title=Aula exemplo JavaScript - Motion Graphics","-metadata","comment=Motion graphics dinâmico; narração e legenda idênticas; 1280x720",str(VIDEO)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(nframes):
            t=min(duration-0.001,i/FPS)
            frame=draw_frame(t,duration,spans,i)
            proc.stdin.write(frame.tobytes())
        proc.stdin.close(); code=proc.wait()
        if code: raise subprocess.CalledProcessError(code,cmd)
    except Exception:
        if proc.poll() is None: proc.kill()
        raise
    print(f"Renderizado: {VIDEO} · {duration:.2f}s · 1280×720 · 24fps")

if __name__=="__main__": main()
