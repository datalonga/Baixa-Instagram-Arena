/* ==========================================================================
   VaultReel — script.js
   JavaScript puro (sem bibliotecas, sem backend).

   O que este código faz:
   - Valida um arquivo de vídeo escolhido pelo usuário OU uma URL direta de vídeo.
   - Mostra a prévia em <video controls> usando URL.createObjectURL (arquivo local)
     ou a própria URL (arquivo remoto).
   - Permite baixar o vídeo com <a download>.
   - Explica com clareza quando o link colado é de uma publicação do Instagram
     (esse tipo de link NÃO fornece o arquivo de vídeo para uma página estática).

   O que este código NÃO faz:
   - Não faz scraping do Instagram nem chama endpoints não oficiais.
   - Não contorna login, permissões, CORS ou DRM.
   - Não pede nem guarda senha, cookie ou token de rede social.
   ========================================================================== */

"use strict";

/* --------------------------------------------------------------------------
   1. Referências do DOM
   -------------------------------------------------------------------------- */
const el = {
  formulario: document.getElementById("formulario"),
  status: document.getElementById("status"),

  radiosFonte: Array.from(document.querySelectorAll('input[name="fonte"]')),
  corpoArquivo: document.querySelector('[data-corpo="arquivo"]'),
  corpoUrl: document.querySelector('[data-corpo="url"]'),

  inputArquivo: document.getElementById("arquivo"),
  dropzone: document.getElementById("dropzone"),

  inputUrl: document.getElementById("url"),
  urlErro: document.getElementById("url-erro"),

  btnPreparar: document.getElementById("preparar"),
  btnLimpar: document.getElementById("limpar"),
  btnBaixar: document.getElementById("baixar"),
  linkAbrir: document.getElementById("abrir"),

  alertaInstagram: document.getElementById("alerta-instagram"),
  btnIrParaArquivo: document.getElementById("ir-para-arquivo"),

  resultado: document.getElementById("resultado"),
  video: document.getElementById("video"),
  infoNome: document.getElementById("info-nome"),
  infoTipo: document.getElementById("info-tipo"),
  infoTamanho: document.getElementById("info-tamanho"),
  infoOrigem: document.getElementById("info-origem"),
};

/* --------------------------------------------------------------------------
   2. Constantes e estado
   -------------------------------------------------------------------------- */
const EXTENSOES_VIDEO = ["mp4", "m4v", "webm", "mov", "ogv", "ogg", "3gp", "mkv", "avi"];
const TEMPO_LIMITE_PREVIA_MS = 12000; // tempo máximo para a prévia remota responder
const TAMANHO_MAXIMO_FETCH_MB = 200; // acima disso, não baixamos via fetch (memória)

/** Estado da aplicação. */
const estado = {
  ocupado: false, // impede cliques duplicados durante uma operação
  fonte: "arquivo", // "arquivo" | "url"
  arquivo: null, // File selecionado
  urlObjeto: null, // URL temporária criada com createObjectURL
  urlRemota: null, // URL direta validada
  prevendo: false, // prévia pronta para download
  urlBlobDownload: null, // URL de blob criada durante o download remoto
  timerPrevia: null, // temporizador da prévia remota
  timerTravado: null, // temporizador do evento "stalled"
};

/* --------------------------------------------------------------------------
   3. Utilitários
   -------------------------------------------------------------------------- */

/** Formata bytes em uma unidade legível (pt-BR). */
function formatarTamanho(bytes) {
  if (typeof bytes !== "number" || !Number.isFinite(bytes) || bytes <= 0) return "—";
  const unidades = ["B", "KB", "MB", "GB"];
  let valor = bytes;
  let indice = 0;
  while (valor >= 1024 && indice < unidades.length - 1) {
    valor /= 1024;
    indice += 1;
  }
  return `${valor.toLocaleString("pt-BR", { maximumFractionDigits: indice === 0 ? 0 : 1 })} ${unidades[indice]}`;
}

/** Extrai o nome de arquivo de uma URL (sem query string) ou devolve um padrão. */
function nomeDeArquivoDaUrl(url) {
  try {
    const caminho = new URL(url).pathname;
    const ultimo = decodeURIComponent(caminho.split("/").filter(Boolean).pop() || "");
    if (ultimo && ultimo.includes(".")) return ultimo.slice(0, 120);
  } catch (_) {
    /* URL inválida: cai no nome padrão */
  }
  return "video.mp4";
}

/** Devolve a extensão (minúscula, sem ponto) de um nome de arquivo. */
function extensaoDe(nome) {
  const partes = String(nome || "").toLowerCase().split(".");
  return partes.length > 1 ? partes.pop() : "";
}

/** Limpa os listeners de carga/erro da prévia remota e os temporizadores. */
function limparListenersRemotos() {
  if (estado.timerPrevia) {
    clearTimeout(estado.timerPrevia);
    estado.timerPrevia = null;
  }
  if (estado.timerTravado) {
    clearTimeout(estado.timerTravado);
    estado.timerTravado = null;
  }
  el.video.removeEventListener("loadeddata", aoCarregarPrevia);
  el.video.removeEventListener("loadedmetadata", aoCarregarPrevia);
  el.video.removeEventListener("error", aoFalharPrevia);
  el.video.removeEventListener("stalled", aoTravarPrevia);
}

/** Libera URLs temporárias criadas por nós. */
function revogarUrlObjeto() {
  if (estado.urlObjeto) {
    URL.revokeObjectURL(estado.urlObjeto);
    estado.urlObjeto = null;
  }
}

function revogarUrlBlob() {
  if (estado.urlBlobDownload) {
    URL.revokeObjectURL(estado.urlBlobDownload);
    estado.urlBlobDownload = null;
  }
}

/* --------------------------------------------------------------------------
   4. Mensagens acessíveis (aria-live)
   -------------------------------------------------------------------------- */
/** Caminhos dos ícones decorativos (SVG criado via DOM, sem HTML injetado). */
const ICONES = {
  erro: ["M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18", "M12 7.5v5.5", "M12 16.4h.01"],
  sucesso: ["M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18", "m8 12.4 2.6 2.6L16 9.6"],
  info: ["M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18", "M12 11v5.5", "M12 7.6h.01"],
  carregando: ["M12 3a9 9 0 1 0 9 9"],
};

const SVG_NS = "http://www.w3.org/2000/svg";

/** Cria o ícone SVG de um tipo de mensagem. */
function criarIcone(tipo) {
  const caminhos = ICONES[tipo];
  if (!caminhos) return null;
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("width", "18");
  svg.setAttribute("height", "18");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", "2");
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  svg.setAttribute("aria-hidden", "true");
  caminhos.forEach((d) => {
    const path = document.createElementNS(SVG_NS, "path");
    path.setAttribute("d", d);
    svg.appendChild(path);
  });
  return svg;
}

/**
 * Exibe uma mensagem na região de status (aria-live).
 * Todo o conteúdo é montado com a API do DOM, nunca com HTML dinâmico.
 */
function mostrarMensagem(tipo, texto, { focar = false } = {}) {
  el.status.textContent = "";

  const caixa = document.createElement("div");
  caixa.className = `mensagem mensagem--${tipo}`;

  const icone = criarIcone(tipo);
  if (icone) caixa.appendChild(icone);

  const span = document.createElement("span");
  span.textContent = texto;
  caixa.appendChild(span);

  el.status.appendChild(caixa);
  if (focar) el.status.focus();
}

function limparMensagem() {
  el.status.textContent = "";
}

/** Mostra/oculta o erro específico do campo de URL. */
function definirErroCampoUrl(texto) {
  if (texto) {
    el.urlErro.textContent = texto;
    el.urlErro.hidden = false;
    el.inputUrl.setAttribute("aria-invalid", "true");
  } else {
    el.urlErro.textContent = "";
    el.urlErro.hidden = true;
    el.inputUrl.removeAttribute("aria-invalid");
  }
}

/* --------------------------------------------------------------------------
   5. Controle de estado da interface (botões ocupados)
   -------------------------------------------------------------------------- */

/** Habilita/desabilita botões e marca visualmente o carregamento. */
function definirOcupado(ocupado, botao = null, rotulo = null) {
  estado.ocupado = ocupado;
  const alvos = [el.btnPreparar, el.btnBaixar];
  alvos.forEach((b) => {
    b.disabled = ocupado;
    b.dataset.carregando = ocupado && b === botao ? "true" : "false";
  });
  if (ocupado && botao && rotulo) {
    const rotuloEl = botao.querySelector(".botao__rotulo");
    if (rotuloEl) {
      botao.dataset.rotuloOriginal = rotuloEl.textContent;
      rotuloEl.textContent = rotulo;
    }
  } else {
    alvos.forEach((b) => {
      const rotuloEl = b.querySelector(".botao__rotulo");
      if (rotuloEl && b.dataset.rotuloOriginal) {
        rotuloEl.textContent = b.dataset.rotuloOriginal;
        delete b.dataset.rotuloOriginal;
      }
    });
  }
}

/* --------------------------------------------------------------------------
   6. Validações
   -------------------------------------------------------------------------- */

/** O texto parece um link de publicação do Instagram? (usado só para avisar) */
function ehLinkDePublicacaoInstagram(texto) {
  const padroes = [
    /instagram\.com/i,
    /instagr\.am/i,
    /fb\.watch/i,
    /\/(p|reel|reels|tv|stories)\//i,
  ];
  return padroes.some((padrao) => padrao.test(texto));
}

/** Verifica se o File escolhido é de vídeo (por MIME e, se preciso, por extensão). */
function validarArquivoVideo(arquivo) {
  if (!arquivo) {
    return { ok: false, motivo: "Escolha um arquivo de vídeo para continuar." };
  }
  if (arquivo.size === 0) {
    return { ok: false, motivo: "O arquivo selecionado está vazio (0 byte). Escolha outro vídeo." };
  }
  const tipo = (arquivo.type || "").toLowerCase();
  const extensao = extensaoDe(arquivo.name);
  const ehVideoPorMime = tipo.startsWith("video/");
  const ehVideoPorExtensao = EXTENSOES_VIDEO.includes(extensao);

  if (!ehVideoPorMime && !ehVideoPorExtensao) {
    return {
      ok: false,
      motivo: `"${arquivo.name}" não parece ser um vídeo (tipo detectado: ${tipo || "desconhecido"}). Use MP4, WebM, MOV, M4V ou OGV.`,
    };
  }
  return { ok: true, tipo: tipo || `video/${extensao || "mp4"}` };
}

/**
 * Valida uma URL direta de vídeo.
 * Regras: sintaxe válida (URL()), HTTPS para URLs externas e não pode ser
 * um link de publicação de rede social.
 */
function validarUrlDireta(valorBruto) {
  const valor = String(valorBruto || "").trim();
  if (!valor) {
    return { ok: false, motivo: "Informe uma URL direta para o arquivo de vídeo." };
  }

  let url;
  try {
    url = new URL(valor);
  } catch (_) {
    return { ok: false, motivo: "URL inválida. Verifique se ela começa com https:// e está completa." };
  }

  if (ehLinkDePublicacaoInstagram(url.href)) {
    return { ok: false, motivo: "instagram", url };
  }

  // Em arquivo aberto localmente, o contexto é "null"/file://: só aceitamos https.
  if (url.protocol !== "https:") {
    if (url.protocol === "http:") {
      return { ok: false, motivo: "Por segurança, use apenas URLs HTTPS (a sua começa com http://)." };
    }
    return { ok: false, motivo: `Protocolo "${url.protocol}" não é suportado. Use uma URL https://.` };
  }

  const extensao = extensaoDe(nomeDeArquivoDaUrl(url.href));
  return { ok: true, url, extensao };
}

/* --------------------------------------------------------------------------
   7. Pré-visualização
   -------------------------------------------------------------------------- */

/** Preenche a lista de informações do arquivo/URL. */
function preencherInformacoes({ nome, tipo, tamanho, origem }) {
  el.infoNome.textContent = nome || "—";
  el.infoTipo.textContent = tipo || "—";
  el.infoTamanho.textContent = tamanho || "—";
  el.infoOrigem.textContent = origem || "—";
}

/** Prepara a prévia de um arquivo local (blob URL temporária). */
function prepararArquivoLocal(arquivo) {
  const validacao = validarArquivoVideo(arquivo);
  if (!validacao.ok) {
    mostrarMensagem("erro", validacao.motivo, { focar: true });
    return;
  }

  revogarUrlObjeto(); // revoga a URL anterior antes de criar uma nova
  try {
    estado.urlObjeto = URL.createObjectURL(arquivo);
  } catch (erro) {
    mostrarMensagem("erro", "Este navegador não permitiu criar a prévia do arquivo. Tente abrir a página em outro navegador.", { focar: true });
    return;
  }

  estado.arquivo = arquivo;
  estado.fonte = "arquivo";
  estado.urlRemota = null;

  el.video.src = estado.urlObjeto;
  el.video.load();
  mostrarResultado(true);

  preencherInformacoes({
    nome: arquivo.name,
    tipo: validacao.tipo,
    tamanho: formatarTamanho(arquivo.size),
    origem: "Arquivo local (URL temporária no navegador)",
  });

  el.linkAbrir.hidden = true;
  el.btnBaixar.disabled = false;
  estado.prevendo = true;

  mostrarMensagem("sucesso", `Vídeo "${arquivo.name}" pronto para download.`);
  el.btnLimpar.hidden = false;
  focarResultado();
}

/** Prepara a prévia de uma URL direta remota. */
function prepararUrlRemota(validacao) {
  const url = validacao.url;

  revogarUrlObjeto();
  estado.arquivo = null;
  estado.urlObjeto = null;
  estado.fonte = "url";
  estado.urlRemota = url.href;
  estado.prevendo = false;

  el.btnBaixar.disabled = true;
  el.linkAbrir.href = url.href;
  el.linkAbrir.hidden = false;

  mostrarResultado(true);
  preencherInformacoes({
    nome: nomeDeArquivoDaUrl(url.href),
    tipo: validacao.extensao ? `vídeo (.${validacao.extensao})` : "a confirmar",
    tamanho: "a confirmar após o carregamento",
    origem: "URL direta informada por você",
  });

  mostrarMensagem("carregando", "Carregando a prévia do vídeo…");
  definirOcupado(true, el.btnPreparar, "Carregando…");

  // Listeners de sucesso/falha da prévia (removidos assim que um deles dispara).
  el.video.addEventListener("loadeddata", aoCarregarPrevia, { once: true });
  el.video.addEventListener("loadedmetadata", aoCarregarPrevia, { once: true });
  el.video.addEventListener("error", aoFalharPrevia, { once: true });
  el.video.addEventListener("stalled", aoTravarPrevia, { once: true });

  estado.timerPrevia = setTimeout(() => {
    aoFalharPrevia(null, "tempo esgotado");
  }, TEMPO_LIMITE_PREVIA_MS);

  el.video.src = url.href; // única requisição feita: o próprio player carrega o vídeo
  el.video.load();
  focarResultado();
}

/** Prévia remota carregou com sucesso. */
function aoCarregarPrevia() {
  limparListenersRemotos();
  definirOcupado(false);
  estado.prevendo = true;
  el.btnBaixar.disabled = false;
  el.btnLimpar.hidden = false;

  // Completa as informações que só o player conhece.
  const duracao = Number.isFinite(el.video.duration) ? el.video.duration : 0;
  el.infoTipo.textContent = `${el.infoTipo.textContent} — ${el.video.videoWidth}×${el.video.videoHeight}px`;
  if (duracao > 0) {
    const minutos = Math.floor(duracao / 60);
    const segundos = Math.round(duracao % 60);
    el.infoTamanho.textContent = `duração ${minutos}min ${String(segundos).padStart(2, "0")}s`;
  }

  mostrarMensagem("sucesso", "Prévia carregada. Você já pode baixar o vídeo.");
}

/** Prévia remota falhou (bloqueio do servidor, CORS, URL que não é vídeo etc.). */
function aoFalharPrevia(_evento, motivoExtra = null) {
  limparListenersRemotos();
  definirOcupado(false);
  estado.prevendo = false;
  el.btnBaixar.disabled = true;
  el.video.removeAttribute("src");
  el.video.load();

  if (motivoExtra === "tempo esgotado") {
    mostrarMensagem(
      "erro",
      "A prévia demorou demais para responder. O servidor pode estar bloqueando o acesso direto ao vídeo. Não tentamos contornar bloqueios: hospede o arquivo em um serviço que permita acesso direto ou selecione um arquivo local.",
      { focar: true }
    );
    return;
  }

  mostrarMensagem(
    "erro",
    "Não foi possível carregar a prévia. A URL pode não apontar direto para um arquivo de vídeo, o servidor pode exigir autenticação ou pode estar bloqueando o acesso de outros sites (CORS/hotlink). Verifique o endereço ou selecione um arquivo local.",
    { focar: true }
  );
}

/** O carregamento travou (servidor lento ou que não entrega o arquivo). */
function aoTravarPrevia() {
  if (estado.prevendo || estado.timerTravado) return;
  // Dá alguns segundos para a conexão se recuperar antes de declarar falha.
  estado.timerTravado = setTimeout(() => {
    if (!estado.prevendo) aoFalharPrevia(null, "tempo esgotado");
  }, 6000);
}

/** Mostra ou esconde a área de resultado. */
function mostrarResultado(visivel) {
  el.resultado.hidden = !visivel;
}

function focarResultado() {
  // tabindex="-1" já está no HTML: move o foco para a prévia sem quebrar a leitura.
  el.resultado.focus({ preventScroll: true });
}

/* --------------------------------------------------------------------------
   8. Download
   -------------------------------------------------------------------------- */

/** Dispara um clique em um <a download> criado na hora. */
function baixarComLink(href, nomeDoArquivo) {
  const link = document.createElement("a");
  link.href = href;
  link.download = nomeDoArquivo; // respeitado pelo navegador para same-origin/blob
  link.rel = "noopener";
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

/** Handler do botão "Baixar vídeo". */
async function aoClicarBaixar() {
  if (estado.ocupado || !estado.prevendo) return; // impede cliques duplicados

  if (estado.fonte === "arquivo" && estado.urlObjeto && estado.arquivo) {
    baixarComLink(estado.urlObjeto, estado.arquivo.name || "video.mp4");
    mostrarMensagem("sucesso", "Download iniciado. Confira a pasta de downloads do seu navegador.");
    return;
  }

  if (estado.fonte === "url" && estado.urlRemota) {
    await baixarUrlRemota(estado.urlRemota);
  }
}

/**
 * Tenta baixar a URL direta como blob (funciona quando o servidor permite CORS).
 * Se o servidor bloquear, avisamos o usuário e indicamos o player — sem
 * tentar contornar o bloqueio.
 */
async function baixarUrlRemota(url) {
  definirOcupado(true, el.btnBaixar, "Baixando…");
  mostrarMensagem("carregando", "Preparando o arquivo para download…");

  const nomeDoArquivo = nomeDeArquivoDaUrl(url);
  revogarUrlBlob();

  try {
    const resposta = await fetch(url, { mode: "cors", credentials: "omit", cache: "no-store" });

    if (!resposta.ok) {
      throw new Error(`HTTP ${resposta.status}`);
    }

    const declarado = Number(resposta.headers.get("content-length") || 0);
    if (declarado > TAMANHO_MAXIMO_FETCH_MB * 1024 * 1024) {
      throw new Error("arquivo grande demais para download em memória");
    }

    const blob = await resposta.blob();

    if (!blob.type.startsWith("video/") && !EXTENSOES_VIDEO.includes(extensaoDe(nomeDoArquivo))) {
      throw new Error("o endereço não devolveu um arquivo de vídeo");
    }

    estado.urlBlobDownload = URL.createObjectURL(blob);
    baixarComLink(estado.urlBlobDownload, nomeDoArquivo);
    mostrarMensagem("sucesso", `Download iniciado: ${nomeDoArquivo} (${formatarTamanho(blob.size)}).`);
  } catch (erro) {
    const motivo = erro && erro.message ? erro.message : "falha desconhecida";
    mostrarMensagem(
      "info",
      `O servidor não liberou o download direto (${motivo}). Isso é comum quando o site bloqueia outros domínios (CORS) ou exige autenticação. Use os controles do player acima (menu de três pontos ou botão direito → "Salvar vídeo como…") ou abra o vídeo em nova aba para salvá-lo.`,
      { focar: true }
    );
  } finally {
    definirOcupado(false);
    // A URL do blob pode ser liberada logo após o clique do download.
    setTimeout(revogarUrlBlob, 4000);
  }
}

/* --------------------------------------------------------------------------
   9. Reset e troca de fonte
   -------------------------------------------------------------------------- */

/** Limpa tudo e volta ao estado inicial. */
function limparTudo({ mensagem = true } = {}) {
  limparListenersRemotos();
  revogarUrlObjeto();
  revogarUrlBlob();

  estado.arquivo = null;
  estado.urlRemota = null;
  estado.prevendo = false;

  el.video.removeAttribute("src");
  el.video.load();
  el.inputArquivo.value = "";
  if ("files" in el.inputArquivo) el.inputArquivo.files = null;
  el.inputUrl.value = "";
  definirErroCampoUrl("");
  mostrarResultado(false);
  el.btnLimpar.hidden = true;
  el.alertaInstagram.hidden = true;
  el.linkAbrir.hidden = true;
  el.btnBaixar.disabled = true;
  definirOcupado(false);
  preencherInformacoes({ nome: "—", tipo: "—", tamanho: "—", origem: "—" });
  selecionarFonte("arquivo"); // volta à opção padrão

  if (mensagem) {
    mostrarMensagem("info", "Tudo limpo. Escolha um arquivo ou informe uma URL direta.");
  } else {
    limparMensagem();
  }
}

/** Descobre qual fonte está marcada no formulário (padrão: "arquivo"). */
function lerFonteSelecionada() {
  const marcados = el.radiosFonte.filter((radio) => radio.checked);
  if (!marcados.length) return "arquivo";
  const valor = marcados[marcados.length - 1].value;
  return valor === "url" ? "url" : "arquivo";
}

/** Alterna a fonte ativa e mostra apenas o corpo correspondente. */
function selecionarFonte(fonte, { focar = false } = {}) {
  estado.fonte = fonte;
  const radio = el.radiosFonte.find((r) => r.value === fonte);
  if (radio) {
    radio.checked = true;
    if (focar) radio.focus();
  }
  // Reforço visual (o CSS já trata com :has, mas garantimos o fallback).
  el.corpoArquivo.hidden = fonte !== "arquivo";
  el.corpoUrl.hidden = fonte !== "url";
}

/* --------------------------------------------------------------------------
   10. Envio do formulário ("Preparar download")
   -------------------------------------------------------------------------- */
function aoEnviarFormulario(evento) {
  evento.preventDefault();
  if (estado.ocupado) return; // impede envio duplicado

  estado.fonte = lerFonteSelecionada();
  const fonte = estado.fonte;
  el.alertaInstagram.hidden = true;

  if (fonte === "arquivo") {
    const arquivo = el.inputArquivo.files && el.inputArquivo.files[0];
    if (!arquivo) {
      definirErroCampoUrl("");
      mostrarMensagem("erro", "Nenhum arquivo selecionado. Clique em \"Escolher arquivo\" e selecione um vídeo.", { focar: true });
      el.inputArquivo.focus();
      return;
    }
    definirErroCampoUrl("");
    prepararArquivoLocal(arquivo);
    return;
  }

  const validacao = validarUrlDireta(el.inputUrl.value);

  if (!validacao.ok) {
    estado.prevendo = false;
    el.btnBaixar.disabled = true;

    // Caso especial: link de publicação do Instagram.
    if (validacao.motivo === "instagram") {
      definirErroCampoUrl("Este é um link de publicação, não um arquivo de vídeo.");
      el.alertaInstagram.hidden = false;
      mostrarMensagem(
        "info",
        "Não é possível extrair o vídeo de um link de publicação do Instagram nesta página. Selecione um arquivo de vídeo do seu dispositivo ou informe uma URL que termine no arquivo (por exemplo, .mp4).",
        { focar: true }
      );
      el.alertaInstagram.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }

    definirErroCampoUrl(validacao.motivo);
    mostrarMensagem("erro", validacao.motivo, { focar: true });
    el.inputUrl.focus();
    return;
  }

  definirErroCampoUrl("");
  prepararUrlRemota(validacao);
}

/* --------------------------------------------------------------------------
   11. Eventos
   -------------------------------------------------------------------------- */
el.formulario.addEventListener("submit", aoEnviarFormulario);

// Troca de fonte via radio (teclado e clique).
el.radiosFonte.forEach((radio) => {
  radio.addEventListener("change", () => {
    selecionarFonte(radio.value);
    el.alertaInstagram.hidden = true;
    definirErroCampoUrl("");
    limparMensagem();
  });
});

// Limpeza ao digitar a URL (o alerta volta se o novo texto ainda for um link de rede social).
el.inputUrl.addEventListener("input", () => {
  definirErroCampoUrl("");
  el.alertaInstagram.hidden = !ehLinkDePublicacaoInstagram(el.inputUrl.value);
});

// Ao trocar o arquivo, a URL temporária anterior é revogada em prepararArquivoLocal.
el.inputArquivo.addEventListener("change", () => {
  const arquivo = el.inputArquivo.files && el.inputArquivo.files[0];
  if (!arquivo) {
    // O usuário cancelou a seleção: volta ao estado limpo.
    if (!estado.urlRemota) limparTudo({ mensagem: false });
    return;
  }
  const validacao = validarArquivoVideo(arquivo);
  if (!validacao.ok) {
    mostrarMensagem("erro", validacao.motivo, { focar: true });
    el.inputArquivo.value = "";
    return;
  }
  // Prévia imediata: o botão "Preparar download" continua disponível.
  prepararArquivoLocal(arquivo);
});

// Arrastar e soltar sobre a dropzone.
["dragenter", "dragover"].forEach((tipo) => {
  el.dropzone.addEventListener(tipo, (evento) => {
    evento.preventDefault();
    el.dropzone.classList.add("dropzone--sobre");
  });
});

["dragleave", "drop"].forEach((tipo) => {
  el.dropzone.addEventListener(tipo, (evento) => {
    evento.preventDefault();
    el.dropzone.classList.remove("dropzone--sobre");
  });
});

el.dropzone.addEventListener("drop", (evento) => {
  const arquivos = evento.dataTransfer && evento.dataTransfer.files;
  if (!arquivos || !arquivos.length) return;
  selecionarFonte("arquivo");
  try {
    el.inputArquivo.files = arquivos; // sincroniza com o campo, quando o navegador permite
  } catch (_) {
    /* alguns navegadores bloqueiam a atribuição; o handler abaixo cuida disso */
  }
  prepararArquivoLocal(arquivos[0]);
});

// Botões auxiliares.
el.btnLimpar.addEventListener("click", () => limparTudo());
el.btnBaixar.addEventListener("click", aoClicarBaixar);
el.btnIrParaArquivo.addEventListener("click", () => {
  selecionarFonte("arquivo", { focar: true });
  el.alertaInstagram.hidden = true;
  mostrarMensagem("info", "Selecione o arquivo de vídeo salvo no seu dispositivo para preparar o download.");
  el.corpoArquivo.scrollIntoView({ behavior: "smooth", block: "center" });
});

// Atalho: Enter dentro do campo de URL envia o formulário (comportamento nativo).
// Revoga a URL temporária ao sair da página.
window.addEventListener("pagehide", () => {
  limparListenersRemotos();
  revogarUrlObjeto();
  revogarUrlBlob();
});

// Em segundo plano prolongado, também liberamos memória.
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden" && !estado.prevendo) {
    revogarUrlBlob();
  }
});

/* --------------------------------------------------------------------------
   12. Inicialização
   -------------------------------------------------------------------------- */
(function iniciar() {
  selecionarFonte("arquivo");
  definirOcupado(false);
  mostrarResultado(false);
  el.btnBaixar.disabled = true;
  el.btnLimpar.hidden = true;
  // Mensagem inicial de boas-vindas na região aria-live.
  mostrarMensagem("info", "Escolha um arquivo de vídeo ou informe uma URL direta (https://) para começar.");
})();
