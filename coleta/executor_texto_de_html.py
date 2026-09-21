# -*- coding: utf-8 -*-
"""EXECUTOR — TEXTO DE HTML. A quarta espécie que a Collection sabe abrir.

O DEFEITO, MEDIDO NA BIG COLLECTION 2 (20/09/2026)
--------------------------------------------------
46 observações `text/html` chegaram à porta canónica com bytes preservados e
saíram da etapa DERIVED como `NOT_APPLICABLE` (`DERIVACAO_ESPECIE_NAO_SUPORTADA`):
nenhum executor declarava `text/html` em `ACEITA_MEDIA_TYPES`. A Admissão
recebeu, para cada uma, um documento sem texto — e respondeu `NAO_SEI` a uma
pergunta que nunca chegou a fazer. Não era falha da régua: era material que não
existia na língua que a régua lê.

    UM DOCUMENTO SEM TEXTO NÃO É JULGADO. É ADIADO.
    A MISSÃO DESTE EXECUTOR É DAR À RÉGUA MATERIAL JULGÁVEL — DEPOIS A RÉGUA DECIDE.

O QUE ELE É, E O QUE NÃO É
--------------------------
É a mesma ficha de capacidade e a mesma ponte forward de
`coleta/executor_texto_de_pdf.py` — `CAPACIDADE`, `extrair()`, `derivar_um()` —
para outra espécie. O dono da escrita continua a ser
`guarda/preservar_derivado.py`; este executor produz o texto e nada mais.

NÃO é um extractor de artigos, NÃO adivinha o «conteúdo principal», NÃO segue
ligações, NÃO vai à rede (`NETWORK_REQUIRED: NO`). Lê os bytes que a porta já
preservou e devolve o texto visível: tudo o que não é `script`, `style`,
`noscript`, `template` e comentários, com as entidades decodificadas e o
espaço em branco normalizado. Uma página de navegação dá o texto da navegação
— e é a régua, não este ficheiro, que decide se isso vale alguma coisa.

Mede-se o que se pode medir sem interpretar: quantos caracteres, quantos sem
espaço, quantas ligações, quantos caracteres em blocos de parágrafo. Essas
medidas vão no recibo (`HTML_KIND` é uma leitura delas, dita como leitura).

Só biblioteca-padrão (`html.parser`): não há dependência nova, e não há um
segundo parser — antes deste ficheiro não havia nenhum em produção.
"""
from __future__ import annotations

import html as _html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import artefato as art  # noqa: E402

EXECUTOR_ID = "texto-de-html"
EXECUTOR_VERSION = "1"
PIPELINE_VERSION = "1"

CAPACIDADE = {
    "EXECUTOR_ID": EXECUTOR_ID,
    "VERSION": EXECUTOR_VERSION,
    "SUPPORTS": ["HTML_RAW"],
    # A espécie na língua que `coleta/ingresso.executor_para` lê: o
    # `media_type` do `raw_asset`. Um só dono da declaração, legível dos dois
    # lados — a mesma disciplina do executor de PDF.
    "ACEITA_MEDIA_TYPES": ("text/html", "application/xhtml+xml"),
    "PRODUCES": ["TEXT_EXTRACTED"],
    "NETWORK_REQUIRED": "NO",
    "OCR": "NO",
    "CHECKPOINT": art.NAO_SE_APLICA,
    "COST_CLASS": "LOCAL",
    "FERRAMENTA_EXTERNA": "nenhuma (html.parser da biblioteca-padrao)",
}

# O que NÃO é texto visível. `head` fica de fora do corpo, mas o `title`
# entra: é a única linha da cabeça que uma pessoa lê.
_INVISIVEIS = {"script", "style", "noscript", "template", "svg", "canvas", "iframe", "object"}
# Elementos que separam blocos de texto: onde acaba um, entra uma quebra.
_BLOCOS = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6",
           "tr", "td", "th", "table", "section", "article", "header", "footer",
           "nav", "aside", "main", "blockquote", "pre", "dt", "dd", "figcaption",
           "title", "option", "hr", "form", "fieldset", "legend", "summary", "details"}
# Blocos de PARÁGRAFO: o texto que vive aqui é o que se mede como «corpo».
# `li`, `td` e `th` ficam de fora de propósito: é onde vive a navegação (menus,
# listas de ligações, tabelas de índice). Medido nas seis primeiras páginas da
# Big Collection 2: com eles dentro, uma página de PEC e uma lista de comunicados
# liam-se como CONTENT.
_PARAGRAFO = {"p", "blockquote", "pre", "dd", "h1", "h2", "h3", "h4", "h5", "h6", "figcaption"}


class _Leitor(HTMLParser):
    """Um leitor que só sabe uma coisa: o que é texto visível e onde ele quebra."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pedacos = []
        self.escondido = 0          # dentro de script/style/...
        self.paragrafo = 0          # dentro de p/li/h*/...
        self.chars_paragrafo = 0
        self.ligacoes = 0
        self.titulo = None
        self._no_titulo = False
        self._buf_titulo = []

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in _INVISIVEIS:
            self.escondido += 1
        if t == "a":
            self.ligacoes += 1
            self.pedacos.append(" ")
        if t in _PARAGRAFO:
            self.paragrafo += 1
        if t in _BLOCOS:
            self.pedacos.append("\n")
        if t == "title":
            self._no_titulo = True

    def handle_startendtag(self, tag, attrs):
        if tag.lower() in _BLOCOS:
            self.pedacos.append("\n")

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in _INVISIVEIS and self.escondido:
            self.escondido -= 1
        if t in _PARAGRAFO and self.paragrafo:
            self.paragrafo -= 1
        if t in _BLOCOS:
            self.pedacos.append("\n")
        if t == "title":
            self._no_titulo = False
            self.titulo = " ".join("".join(self._buf_titulo).split()) or None

    def handle_data(self, data):
        if self.escondido:
            return
        if self._no_titulo:
            self._buf_titulo.append(data)
        # Quebras de linha DENTRO do texto sao espaco: so os blocos quebram.
        self.pedacos.append(data.replace("\r", " ").replace("\n", " "))
        if self.paragrafo:
            self.chars_paragrafo += len("".join(data.split()))

    def handle_comment(self, data):
        return


def _decodificar(dados: bytes) -> str:
    """UTF-8 primeiro (com BOM tolerado); senão o charset declarado; senão latin-1.

    Nunca falha por causa da codificação: um byte que não se lê vira U+FFFD e
    conta como caractere — a régua vê o que há, não uma página vazia.
    """
    if dados.startswith(b"\xef\xbb\xbf"):
        dados = dados[3:]
    try:
        return dados.decode("utf-8")
    except UnicodeDecodeError:
        pass
    m = re.search(rb"charset=[\"']?([A-Za-z0-9_.:-]+)", dados[:4096], re.I)
    if m:
        try:
            return dados.decode(m.group(1).decode("ascii", "ignore"), "replace")
        except (LookupError, UnicodeDecodeError):
            pass
    return dados.decode("latin-1", "replace")


# ── PUBLISHED_AT: a data que a PRÓPRIA página declara como publicação ─────
# AQUISICAO-DETALHE-V1 (PASSO 6), medido no canário de 21/09/2026: 66 de 87
# páginas de artigo traziam a data de publicação explícita no HTML, e nenhum
# executor a preservava. A régua da Bíblia (COL-LAW-031) é uma só:
#
#     PUBLISHED_AT != FACT_TIME.  FACT_TIME NÃO TEM FALLBACK.
#
# Por isso isto entra nas MEDIDAS, com o nome PUBLISHED_AT e a base ao lado, e
# NUNCA toca em FACT_TIME. `og:updated_time` fica de fora de propósito: é
# «actualizado», não «publicado». Prosa nunca vira data: só campos declarados.
_SINAIS_DE_PUBLICACAO = (
    ("META_ARTICLE_PUBLISHED_TIME",
     re.compile(r"<meta[^>]+property=[\"']article:published_time[\"'][^>]+content=[\"']([^\"']+)", re.I)),
    ("META_ARTICLE_PUBLISHED_TIME",
     re.compile(r"<meta[^>]+content=[\"']([^\"']+)[\"'][^>]+property=[\"']article:published_time[\"']", re.I)),
    ("JSONLD_DATE_PUBLISHED",
     re.compile(r"\"datePublished\"\s*:\s*\"([^\"]+)\"", re.I)),
    ("TIME_DATETIME_PUBDATE",
     re.compile(r"<time[^>]+(?:pubdate|itemprop=[\"']datePublished[\"'])[^>]*datetime=[\"']([^\"']+)", re.I)),
    ("TIME_DATETIME_PUBDATE",
     re.compile(r"<time[^>]+datetime=[\"']([^\"']+)[\"'][^>]*(?:pubdate|itemprop=[\"']datePublished[\"'])", re.I)),
    ("META_DATE",
     re.compile(r"<meta[^>]+name=[\"'](?:date|dc\.date(?:\.issued)?|pubdate|publish-date|DC\.date\.issued)[\"'][^>]+content=[\"']([^\"']+)", re.I)),
)
_FORMA_DE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?$")


def data_de_publicacao(fonte: str) -> tuple[str | None, str | None]:
    """→ (PUBLISHED_AT, PUBLISHED_AT_BASIS) ou (None, None). Só o que a página DECLARA."""
    for base, rx in _SINAIS_DE_PUBLICACAO:
        m = rx.search(fonte)
        if not m:
            continue
        valor = m.group(1).strip()
        if _FORMA_DE_DATA.match(valor):
            return valor, base
    return None, None


def texto_de_html(dados: bytes) -> tuple[str, dict]:
    """→ (texto visível, medidas). Puro: sem ficheiro, sem rede, sem banco."""
    fonte = _decodificar(dados)
    published_at, published_at_basis = data_de_publicacao(fonte)
    leitor = _Leitor()
    leitor.feed(fonte)
    leitor.close()
    bruto = "".join(leitor.pedacos)
    linhas = [" ".join(l.split()) for l in bruto.split("\n")]
    texto = "\n".join(l for l in linhas if l)
    if leitor.titulo and not texto.startswith(leitor.titulo):
        texto = leitor.titulo + "\n" + texto
    sem_brancos = len("".join(texto.split()))
    medidas = {
        "CHARACTERS": len(texto),
        "NON_WHITESPACE_CHARACTERS": sem_brancos,
        "PARAGRAPH_CHARACTERS": leitor.chars_paragrafo,
        "LINKS": leitor.ligacoes,
        "TITLE": leitor.titulo,
        "HTML_BYTES": len(dados),
        # Uma LEITURA das medidas, dita como leitura e não como veredito. A
        # régua não a usa; quem audita, sim.
        "HTML_KIND": _kind(sem_brancos, leitor.chars_paragrafo, leitor.ligacoes),
        # A data que a página declara como publicação, e de onde veio. É
        # PUBLICATION_TIME. Não é, e nunca promove, FACT_TIME. None = a página
        # não declara — UNKNOWN continua UNKNOWN.
        "PUBLISHED_AT": published_at,
        "PUBLISHED_AT_BASIS": published_at_basis,
    }
    return texto, medidas


def _kind(sem_brancos: int, paragrafo: int, ligacoes: int) -> str:
    if sem_brancos == 0:
        return "EMPTY"
    if paragrafo >= 800 and paragrafo >= 0.35 * sem_brancos:
        return "CONTENT"
    if ligacoes and sem_brancos / max(ligacoes, 1) < 40:
        return "NAVIGATION"
    return "MIXED"


def extrair(caminho: Path) -> tuple[str, str, str, dict]:
    """Tenta tirar o texto. Devolve (texto, estado, erro, medidas).

      TEXT_LAYER_PRESENT   havia texto visível, e saiu
      TEXT_LAYER_ABSENT    abriu bem e não há texto visível nenhum
      EXTRACTION_ERROR     não se conseguiu ler o ficheiro — problema nosso
    """
    try:
        dados = Path(caminho).read_bytes()
    except OSError as e:
        return "", art.EXTRACTION_ERROR, f"nao consegui ler o ficheiro: {e}", {}
    try:
        texto, medidas = texto_de_html(dados)
    except Exception as e:                                       # noqa: BLE001
        return "", art.EXTRACTION_ERROR, f"html.parser falhou: {e}", {}
    if medidas["NON_WHITESPACE_CHARACTERS"] == 0:
        return texto, art.TEXT_LAYER_ABSENT, "", medidas
    return texto, art.TEXT_LAYER_PRESENT, "", medidas


def derivar_um(raw_asset_id, html, armazem, memoria, relogio=None,
               contexto_da_passagem=None) -> dict:
    """Um HTML, um pai canónico, um derivado — pelo dono da escrita.

    Mesma ponte, mesma doutrina do executor de PDF: este executor entrega a
    receita e os bytes; `parent_sha256`, `parameters_hash`, `sha256` do filho,
    `derived_at` e `storage_path` são do dono. `contexto_da_passagem` é
    transporte opaco — não se lê aqui.
    """
    from guarda.preservar_derivado import agora_utc, preservar_derivado
    texto, estado, erro, medidas = extrair(Path(html))
    if estado != art.TEXT_LAYER_PRESENT:
        return {"ESTADO": "SEM_DERIVADO", "MOTIVO_DO_EXECUTOR": estado,
                "ERRO": erro, "MEDIDAS": medidas}
    return preservar_derivado(
        {**(contexto_da_passagem or {}),
         "raw_asset_id": raw_asset_id,
         "kind": "TEXT_EXTRACTION",
         "producer": EXECUTOR_ID,
         "producer_version": EXECUTOR_VERSION,
         "pipeline_version": PIPELINE_VERSION,
         "parameters": None,
         "serie_posicao": None,
         "media_type": "text/plain"},
        texto.encode("utf-8"), armazem, memoria,
        relogio=relogio or agora_utc)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        t, estado, erro, m = extrair(Path(arg))
        print(f"{estado:20} {m.get('HTML_KIND', '-'):10} chars={m.get('NON_WHITESPACE_CHARACTERS', 0):7} "
              f"par={m.get('PARAGRAPH_CHARACTERS', 0):7} links={m.get('LINKS', 0):4} {arg[-60:]} {erro}")
