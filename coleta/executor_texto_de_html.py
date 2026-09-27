#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O TERCEIRO EXECUTOR A FALAR A LÍNGUA COMUM — texto a partir de HTML.

ISTO NÃO É UM EXTRATOR NOVO. É UMA LIGAÇÃO.
--------------------------------------------
A peça que transforma HTML em texto **já existia nesta árvore** desde antes
desta missão: `coleta/texto_fonte.py::limpar(dados, ctype)`. Ela tira
`<script>`/`<style>`, tira as marcas, desfaz as entidades e normaliza os
espaços. Medido a 2026-09-21, antes de este ficheiro existir:

    `limpar()` tinha ZERO chamadores no código de produção.
    O único que lhe chamava era um MEDIDOR
    (`medidas/porque_a_sala_nao_recebeu.py`), que mede e não colhe.

    CAPABILITY EXISTS != EDGE EXISTS.
    UMA CAPACIDADE QUE NINGUÉM CHAMA NÃO É UMA ETAPA DA ESTRADA.

Por isso a classificação do bloqueio é `MISSING_ROUTE`, e **não**
`NOT_IMPLEMENTED` (a capacidade existe) nem `NOT_APPLICABLE` (a derivação
APLICA-SE: dos 85 documentos HTML medidos, 85 dão texto, com 6 328 caracteres
de média).

⚠️ E NÃO SE DUPLICOU `limpar()`. Este ficheiro **importa-a**. Copiar as seis
linhas de expressão regular para aqui daria dois donos da mesma pergunta, e no
dia em que um deles aprendesse a tratar `<noscript>` os dois divergiam em
silêncio — que é o pecado que esta casa já nomeou (`O8C`).

    ONE CONCEPT -> ONE OWNER. QUEM SABE EXTRAIR É QUEM DIZ COMO SE EXTRAI.

O EXECUTOR NÃO JULGA
--------------------
Como o de PDF e o de mídia: aqui não se decide se um documento é relevante.
Isso é da porta de admissão. Aqui respondem-se quatro perguntas técnicas:

    consegui ler?   de qual original?   quanto texto saiu?   houve erro?

A FORMA É A DOS OUTROS DOIS, DE PROPÓSITO
------------------------------------------
`EXECUTOR_ID` · `CAPACIDADE` · `derivar_um(raw_asset_id, ..., armazem,
memoria, relogio, contexto_da_passagem)`. A posição dos parâmetros é a mesma
de `executor_texto_de_pdf.derivar_um` e de
`executor_transcricao_midia.derivar_um`, para que
`coleta/derivacao_forward.correr()` possa chamar os três sem saber qual tem na
mão.

    DOIS EXECUTORES COM A MESMA FORMA SÃO UM PONTO DE ESCOLHA.
    DOIS COM FORMAS DIFERENTES SÃO DOIS CAMINHOS, E AÍ ALGUÉM ESCREVE O `if`.

⚠️ DECLARAR NÃO É LIGAR. `SUPPORTS` viveu um ano inteiro em
`executor_texto_de_pdf.py` com zero leitores, e o próprio ficheiro escreveu o
preço disso. Por isso a ficha abaixo **não** basta: este executor só está
ligado porque o nome do módulo entrou em
`coleta/ingresso.py::_DONOS_DA_DERIVACAO`, e há prova de runtime —
`ingresso.executor_para("text/html")` tem de devolver **este** módulo.

SEM REDE
--------
Nenhuma ligação. `limpar()` não abre socket nenhum: só o `main()` de
`texto_fonte.py` é que vai à rede, e esse não é chamado daqui. O que entra são
bytes que o armazém já tem.

CORRER
------
    py coleta/executor_texto_de_html.py --ficha            # a capacidade
    py coleta/executor_texto_de_html.py --seco <ficheiro>  # só olha e conta
"""
from __future__ import annotations

import datetime
import html
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import artefato as art  # noqa: E402
import proveniencia as pv  # noqa: E402

from coleta.texto_fonte import limpar  # noqa: E402 — O DONO ÚNICO DA EXTRAÇÃO

# ── A FICHA DE CAPACIDADE ───────────────────────────────────────────────────
EXECUTOR_ID = "texto-de-html"
# ⚠️ "2" DESDE 26/09 (DEDUP-PARA-INSTALAR). Medido na Sala real: os derivados
# 66 (20/09) e 1060 (25/09) da IT-T9-011 dizem os dois `texto-de-html` "1",
# mas o 66 nasceu SEM parametros e o 1060 COM a receita de `receita()` (ligada
# em f0c6ea6f, 21/09). A receita mudou e a versao nao: "1" nomeava duas
# derivacoes diferentes. `tests/test_a_receita_tem_versao.py` reprova quem
# voltar a mudar a receita sem subir isto.
#
#     RECEITA NOVA = VERSAO NOVA.
EXECUTOR_VERSION = "2"
PIPELINE_VERSION = "1"

#: As espécies exactas que esta ponte abre.
#:
#: ⚠️ POR TIPO EXACTO, E NÃO POR FAMÍLIA — e a escolha é medida, não estética.
#: O executor de mídia declara-se por família (`audio`, `video`) porque a lista
#: exacta nunca fecha. Aqui é o contrário: a família `text` inclui
#: `text/plain`, `text/csv` e `text/markdown`, e **nenhum** desses precisa
#: desta ferramenta — `limpar()` sobre `text/csv` devolveria o CSV inteiro com
#: os espaços mexidos e chamar-lhe-ia extração.
#:
#:     UMA FAMÍLIA QUE APANHA MAIS DO QUE SE SABE ABRIR
#:     NÃO É GENEROSIDADE: É UMA RECLAMAÇÃO DE CAPACIDADE FALSA.
#:
#: `IT-T4-001` é `text/csv` e está medido nesta casa como `MISSING_ROUTE` de
#: outro dono — declarar `text` aqui roubava-lhe a rota e produzia lixo com ar
#: de texto.
ACEITA = ("text/html", "application/xhtml+xml")

CAPACIDADE = {
    "EXECUTOR_ID": EXECUTOR_ID,
    "VERSION": EXECUTOR_VERSION,
    # `HTML_RAW` segue a forma de `PDF_RAW` — o nome da espécie para gente ler.
    "SUPPORTS": ["HTML_RAW"],
    # E o MESMO facto na língua que a porta lê: o `media_type` que o
    # `raw_asset` guarda. Não é um segundo dono da capacidade: é a mesma
    # declaração, legível pelos dois lados.
    "ACEITA_MEDIA_TYPES": ACEITA,
    "ACEITA_FAMILIAS": (),
    "PRODUCES": ["TEXT_EXTRACTED"],
    "NETWORK_REQUIRED": "NO",
    "OCR": "NO",
    "CHECKPOINT": art.NAO_SE_APLICA,
    "COST_CLASS": "LOCAL",
    # ⚠️ NÃO HÁ FERRAMENTA DE FORA, e por isso este executor não tem o estado
    # `FERRAMENTA_AUSENTE` que o de PDF tem. `limpar()` é Python puro da
    # biblioteca padrão (`re`, `html`, `zlib`). Numa máquina sem `pdftotext` o
    # executor de PDF devolve `EXECUTOR_UNAVAILABLE`; este não pode ficar
    # indisponível por falta de instalação.
    "FERRAMENTA_EXTERNA": None,
    # Quem realmente extrai. Aponta-se para o dono em vez de o repetir — a
    # mesma disciplina do `ASR_OWNER` do executor de mídia.
    "TEXT_OWNER": "coleta/texto_fonte.py::limpar",
}

#: O `kind` da linha do derivado, na língua da tabela.
#:
#: ⚠️ PROCUROU-SE ANTES DE CRIAR, e a casa já tinha o nome — e não por acaso:
#: `supabase/migrations/022_o_derivado_ganha_casa.sql` escreve, à frente do
#: valor, o comentário `-- pdftotext, html->texto`. O vocabulário reservou a
#: palavra para este caso antes de existir quem a usasse.
#:
#:     ANTES DE CRIAR UM NOME, PROCURAR SE A CASA JÁ TEM UM.
KIND = "TEXT_EXTRACTION"

#: A espécie do texto que sai daqui, lida do dono do vocabulário
#: (`regras/proveniencia.py`) e não escrita aqui.
#:
#:     PAGE_TEXT      texto que estava numa PÁGINA publicada
#:     ORIGINAL       ninguém traduziu nada: é a língua em que foi publicado
#:
#: ⚠️ `TEXT_KIND_BASIS = DECLARED_BY_ROUTE`, e não `NOT_DECLARED`. A rota
#: declarou que aqueles bytes são `text/html` — a espécie do texto sai dessa
#: declaração, e não de alguém a ler o texto para adivinhar o que ele é. É
#: exactamente o limite que o dono escreveu: «QUAL CAMPO EU LI É UM FACTO
#: SOBRE MIM, NÃO UM PALPITE SOBRE O CONTEÚDO» — e ele justifica a ESPÉCIE,
#: nunca a LÍNGUA, que continua `UNKNOWN`.
TEXT_KIND = pv.PAGE_TEXT
TEXT_RELATION = pv.ORIGINAL
TEXT_BASIS = pv.DECLARED_BY_ROUTE

#: Como o texto nasceu. `EXTRACTED_FROM_DOCUMENT` e não
#: `SCRAPED_FROM_RENDERED_PAGE`: esta casa **não renderizou** página nenhuma.
#: Leram-se os bytes do documento arquivado no armazém. Dizer «raspado da
#: página renderizada» prometeria um navegador que não correu.
METODO = pv.EXTRAIDO_DO_DOCUMENTO

#: A ferramenta, obrigatória porque `EXTRACTED_FROM_DOCUMENT` é método de
#: máquina e o dono do vocabulário recusa máquina sem máquina declarada.
FERRAMENTA = "coleta/texto_fonte.py::limpar"

# ── OS MOTIVOS DE «NÃO SAIU DERIVADO» ───────────────────────────────────────
# ⚠️ NÃO SE REUTILIZOU `art.TEXT_LAYER_ABSENT`, E A RAZÃO ESTÁ ESCRITA AO LADO
# DELE: `leis/artefato.py:102` anota-o com `# → NEEDS_OCR`. Um HTML sem texto
# **não precisa de OCR** — ou é uma casca que monta o conteúdo com JavaScript,
# ou é uma página vazia. Herdar o nome faria o recibo mandar alguém comprar
# reconhecimento óptico para um ficheiro que não tem imagem nenhuma.
#
#     UM NOME EMPRESTADO TRAZ A CONCLUSÃO DE QUEM O CUNHOU.
#
#: O documento não trazia texto. Facto sobre o ORIGINAL — a ferramenta não
#: falhou. Irmão de `SEM_FAIXA_DE_AUDIO` no executor de mídia.
SEM_TEXTO_NO_DOCUMENTO = "SEM_TEXTO_NO_DOCUMENTO"

#: Os bytes não são HTML, e a espécie declarada dizia que eram.
#:
#: ⚠️ ISTO EXISTE PARA NÃO ROUBAR O TRABALHO AO DONO CERTO. `limpar()` tem um
#: ramo de PDF lá dentro (`_pdf`), e ele dispara pelos bytes — `%PDF-` — mesmo
#: quando o `ctype` diz HTML. Sem esta guarda, um PDF mal declarado entraria
#: aqui e sairia com uma extração pobre, feita por quem não é o dono de PDF
#: nesta casa, e a linha do derivado ficaria carimbada `texto-de-html`.
#:
#:     DOIS EXTRACTORES A ABRIR A MESMA ESPÉCIE SÃO DOIS DONOS,
#:     E O SEGUNDO GANHA POR ACIDENTE DE DECLARAÇÃO.
BYTES_NAO_SAO_HTML = "BYTES_NAO_SAO_HTML"

#: A unidade de texto não passou no dono do vocabulário. Mesmo nome, mesmo
#: significado e mesmo destino do executor de mídia — a forma da unidade é que
#: falhou, e isso é um facto sobre NÓS.
UNIDADE_RECUSADA = "UNIDADE_RECUSADA"

#: Os oito primeiros bytes que identificam um PDF, sem ambiguidade.
ASSINATURA_PDF = b"%PDF-"


def aceita(media_type) -> bool:
    """Esta ficha abre esta espécie? → bool. A mesma regra que a porta aplica."""
    tipo = str(media_type or "").split(";")[0].strip().lower()
    return tipo in ACEITA


def extrair(dados: bytes, media_type: str = "text/html") -> tuple:
    """Tenta tirar o texto. Devolve `(texto, estado, erro, medidas)`.

    Três saídas, e nenhuma delas é «não serve»:

        TEXT_LAYER_PRESENT      saiu texto
        SEM_TEXTO_NO_DOCUMENTO  leu bem, e não havia letra nenhuma
        EXTRACTION_ERROR        a extração partiu-se — problema NOSSO

    ⚠️ `TEXT_LAYER_PRESENT` é reaproveitado de propósito (é de
    `leis/artefato.py` e diz exactamente isto: saiu texto), enquanto o estado
    de ausência tem nome próprio, porque o de lá promete OCR.
    """
    if dados[:5] == ASSINATURA_PDF:
        # ⚠️ `%%PDF-` E NAO `%PDF-`: esta e uma string de formato, e o `%P`
        # fazia-a rebentar com `unsupported format character 'P'`. O defeito
        # transformava uma RECUSA LIMPA numa excecao — e uma guarda que
        # rebenta em vez de recusar deixa de ser guarda.
        return ("", BYTES_NAO_SAO_HTML,
                "os bytes comecam por %%PDF- e a especie declarada era %r. O "
                "dono de PDF nesta casa e coleta/executor_texto_de_pdf.py"
                % media_type, {"BYTES": len(dados)})
    try:
        texto = limpar(dados, media_type or "text/html")
    except Exception as e:                                       # noqa: BLE001
        return ("", art.EXTRACTION_ERROR,
                "%s: %s" % (type(e).__name__, str(e)[:200]),
                {"BYTES": len(dados)})

    # PRODUZIR FICHEIRO VAZIO NÃO É SUCESSO — a mesma lei do executor de PDF.
    sem_brancos = len("".join(texto.split()))
    medidas = {"BYTES": len(dados),
               "CHARACTERS": len(texto),
               "NON_WHITESPACE_CHARACTERS": sem_brancos}
    if sem_brancos == 0:
        return texto, SEM_TEXTO_NO_DOCUMENTO, "", medidas
    return texto, art.TEXT_LAYER_PRESENT, "", medidas


# ── PUBLICATION_TIME — QUANDO A FONTE PUBLICOU, E SÓ ISSO (D61) ─────────────
#
#     PUBLICATION_TIME != FACT_TIME != OBSERVATION_TIME != COLLECTION_TIME
#
# Medido na Sala real a 25/09: 78 itens, `published_at = NAO SEI` em 78/78. A
# página trazia a data e ninguém a lia: o coletor não a procura, o adaptador
# italiano (`italy_executor.traduzir`) leva quatro campos e nenhum é este, e
# `raw_asset` não tem coluna para ela.
#
# ⚠️ PORQUE O DONO É ESTE EXECUTOR, E NÃO O COLETOR. Três razões, medidas:
#   1. É aqui que estão os bytes que FICARAM guardados — os mesmos de onde sai
#      o texto que a Sala recebe. Ler a data no coletor obrigaria a fazê-la
#      atravessar `raw_asset`, que não a tem (quatro donos a alargar).
#   2. O retrato do detector já faz este trajecto, provado:
#      derivado → estruturação → porta. A data vai pelo mesmo trilho.
#   3. Um HTML já guardado ganha a data num reprocessamento, sem ir à rede.
#
# A ORDEM é a da D61, e cada nível só fala se tiver UMA resposta:
#     1  JSON-LD `datePublished`
#     2  <meta property|name="article:published_time">
#     3  <time datetime="...">
#     3b <meta itemprop="datePublished" content="...">   (microdados schema.org)
#     4  a data do item no ÍNDICE, quando quem chama a entregar
#
# ⚠️ O 3b É DEPOIS DO <time> DE PROPÓSITO (LEITOR-DATA-YOUTUBE, 26/09/2026; a peça
# era da DA-6 e o coordenador passou-a). Medido no acervo: 603 das 612 páginas de
# vídeo do YouTube fora da Sala trazem a data só aqui — nem JSON-LD, nem
# `article:published_time`, nem `<time>`. Posto no fim, o 3b só fala onde os níveis
# da D61 se calavam: NENHUMA data já lida muda de valor nem de base.
#
# ⚠️ UM NÍVEL COM DUAS RESPOSTAS DIFERENTES NÃO RESPONDE. Medido nos HTML reais
# de IT-T7-021: os `<time datetime>` da página são da barra lateral «últimos
# posts» — cinco datas, nenhuma do artigo. Ficar com a primeira seria dar ao
# artigo a data de outro. O nível cala-se, diz porquê, e passa ao seguinte.
#
# ⚠️ E NADA DAQUI VIRA FACT_TIME. Uma notícia publicada a 11/07 pode relatar
# uma geada de 02/07. Este valor vai para `published_at`, e só para lá.
BASE_JSON_LD = "JSON-LD datePublished"
BASE_META = "meta article:published_time"
BASE_TIME = "<time datetime>"
BASE_ITEMPROP = "meta itemprop datePublished"
BASE_INDICE = "INDICE"
ORDEM_DA_PUBLICACAO = (BASE_JSON_LD, BASE_META, BASE_TIME, BASE_ITEMPROP, BASE_INDICE)

_RE_LD = re.compile(
    r"<script[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.I | re.S)
_RE_META = re.compile(r"<meta\b[^>]*>", re.I)
_RE_TIME = re.compile(r"<time\b[^>]*>", re.I)
_RE_ATTR = re.compile(r"([a-zA-Z_:.-]+)\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)")
_RE_ISO = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})"
    r"(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?\s*(Z|[+-]\d{2}:?\d{2})?)?$")


def _atributos(tag: str) -> dict:
    fora = {}
    for nome, v in _RE_ATTR.findall(tag):
        fora[nome.lower()] = html.unescape(v.strip("\"'"))
    return fora


def normalizar_instante(valor) -> tuple:
    """Uma data escrita pela fonte, em ISO 8601. → `(iso, precisao)` ou `(None, porque)`.

    Três respostas, e nenhuma inventa o que a fonte não disse:

        com hora E fuso   → `2026-08-11T12:30:19+00:00`   precisão INSTANTE
        só o dia          → `2026-08-11`                  precisão DIA
        hora SEM fuso     → `2026-08-11`                  precisão DIA
                            (a hora sem fuso não é um instante; fica o dia
                            que a fonte escreveu, e não se inventa o `Z`)

    Qualquer outra coisa — «14 luglio 2026», vazio, lixo — é `None`: ler
    datas em prosa é outra régua, com outra prova.

    ⚠️ D62: DATA RELATIVA NÃO VIRA DATA. «ieri», «la settimana scorsa», «2
    giorni fa» não se convertem aqui nem em lado nenhum desta régua — o dono
    não autorizou. Esta régua só lê METADADO da página, nunca o texto; a
    expressão relativa, quando for guardada como evidência, é de outra peça.
    """
    s = str(valor or "").strip()
    m = _RE_ISO.match(s)
    if not m:
        return None, "nao e ISO 8601: %r" % s[:40]
    a, me, d, h, mi, se, fuso = m.groups()
    try:
        datetime.date(int(a), int(me), int(d))
    except ValueError:
        return None, "data impossivel: %r" % s[:40]
    dia = "%s-%s-%s" % (a, me, d)
    if h is None or fuso is None:
        return dia, "DIA"
    if fuso == "Z":
        fuso = "+00:00"
    elif ":" not in fuso:
        fuso = fuso[:3] + ":" + fuso[3:]
    if int(h) > 23 or int(mi) > 59 or int(se or 0) > 59:
        return None, "hora impossivel: %r" % s[:40]
    return "%sT%s:%s:%s%s" % (dia, h, mi, se or "00", fuso), "INSTANTE"


# CONSERTO-REGUA (SALA-VERIFICA, 26/09): so um ARTIGO publica. Medido na Sala (IT-T7-013, CONAF): a pagina
# institucional «Consiglio dell'Ordine» traz no JSON-LD um no `WebPage` com datePublished 2009-12-18 — a
# data em que a PAGINA foi criada — e a Sala recebeu PUBLISHED_AT = 2009. Um `WebPage`/`WebSite` sozinho
# nao prova quando um CONTEUDO foi publicado: a data dele fica como evidencia (`_datas_de_pagina_json_ld`)
# e o leitor passa ao nivel seguinte (meta, <time>), e sem nada: NAO SEI com o porque.
TIPOS_QUE_PUBLICAM = frozenset((
    "article", "newsarticle", "blogposting", "report", "scholarlyarticle", "techarticle",
    "analysisnewsarticle", "reportagenewsarticle", "opinionnewsarticle", "backgroundnewsarticle",
    "reviewnewsarticle", "askpublicnewsarticle", "livebloposting", "liveblogposting", "socialmediaposting",
    "medicalscholarlyarticle", "satiricalarticle", "advertisertcontentarticle"))


def _tipos(no) -> set:
    t = no.get("@type") if isinstance(no, dict) else None
    t = t if isinstance(t, list) else [t]
    return {str(x).lower() for x in t if x}


def _datas_json_ld_por_tipo(texto: str) -> tuple:
    """(datas de nos que PUBLICAM, datas de nos que sao so PAGINA/SITE)."""
    publica, pagina = [], []

    def _andar(no, tipos_herdados):
        if isinstance(no, dict):
            tipos = _tipos(no) or tipos_herdados
            for k, v in no.items():
                if k == "datePublished" and isinstance(v, str):
                    # so se afasta o no com tipo DECLARADO que nao publica (WebPage, WebSite…);
                    # um no sem tipo continua a valer, como antes (nao ha medicao que o condene)
                    (pagina if tipos and not (tipos & TIPOS_QUE_PUBLICAM) else publica).append(v)
                else:
                    _andar(v, tipos)
        elif isinstance(no, list):
            for x in no:
                _andar(x, tipos_herdados)

    for bloco in _RE_LD.findall(texto):
        try:
            _andar(json.loads(bloco.strip()), set())
        except (ValueError, RecursionError):
            continue            # um bloco partido não apaga os outros
    return publica, pagina


def _datas_do_json_ld(texto: str) -> list:
    return _datas_json_ld_por_tipo(texto)[0]


def _datas_de_pagina_json_ld(texto: str) -> list:
    return _datas_json_ld_por_tipo(texto)[1]


def _datas_do_meta(texto: str) -> list:
    fora = []
    for tag in _RE_META.findall(texto):
        a = _atributos(tag)
        chave = (a.get("property") or a.get("name") or "").strip().lower()
        if chave == "article:published_time" and a.get("content"):
            fora.append(a["content"])
    return fora


def _datas_do_itemprop(texto: str) -> list:
    """`<meta itemprop="datePublished" content="...">` — a forma do YouTube (e de
    qualquer página com microdados schema.org). Só `datePublished`: o `uploadDate`
    diz quando o ficheiro subiu, não quando foi publicado, e não é lido aqui."""
    fora = []
    for tag in _RE_META.findall(texto):
        a = _atributos(tag)
        if (a.get("itemprop") or "").strip().lower() == "datepublished" and a.get("content"):
            fora.append(a["content"])
    return fora


def _datas_do_time(texto: str) -> list:
    return [a["datetime"] for a in map(_atributos, _RE_TIME.findall(texto))
            if a.get("datetime")]


def tempo_de_publicacao(dados, data_no_indice=None) -> dict:
    """PUBLICATION_TIME de uma página HTML, com a BASE. Nunca inventa.

    Devolve sempre `{"VALOR", "BASE", "PRECISAO", "ORIGINAL", "PORQUE"}`.
    Sem resposta: `VALOR = BASE = NAO SEI`, e `PORQUE` diz o que cada nível viu
    — um `NAO SEI` com razão é uma medição; sem razão é desleixo.

    `data_no_indice` é a data que o ÍNDICE mostrava ao lado do link, quando o
    coletor a tiver. Hoje nenhum produtor a entrega (ver `GAPS` no relatório):
    o parâmetro existe para o quarto nível ter sítio, e não para ser adivinhado.
    """
    if isinstance(dados, bytes):
        texto = dados.decode("utf-8", errors="replace")
    else:
        texto = str(dados or "")
    niveis = (
        (BASE_JSON_LD, _datas_do_json_ld(texto)),
        (BASE_META, _datas_do_meta(texto)),
        (BASE_TIME, _datas_do_time(texto)),
        (BASE_ITEMPROP, _datas_do_itemprop(texto)),
        (BASE_INDICE, [data_no_indice] if data_no_indice else []),
    )
    viu = []
    so_pagina = _datas_de_pagina_json_ld(texto)
    for base, brutas in niveis:
        if not brutas:
            viu.append("%s: ausente" % base + (
                " (só um nó WebPage/WebSite com datePublished %s — é a data da PÁGINA, "
                "não a de um artigo publicado)" % ", ".join(sorted(set(so_pagina))[:3])
                if base == BASE_JSON_LD and so_pagina else ""))
            continue
        # A chave de comparação é o INSTANTE, e não a letra: `12:30+00:00` e
        # `14:30+02:00` são a mesma publicação escrita em dois fusos.
        boas = {}
        for b in brutas:
            iso, prec = normalizar_instante(b)
            if iso:
                chave = (datetime.datetime.fromisoformat(iso)
                         .astimezone(datetime.timezone.utc).isoformat()
                         if prec == "INSTANTE" else iso)
                boas.setdefault(chave, (iso, prec, b))
        if not boas:
            viu.append("%s: %d valor(es), nenhum ISO 8601" % (base, len(brutas)))
            continue
        if len(boas) > 1:
            viu.append("%s: AMBIGUO, %d datas diferentes (%s)"
                       % (base, len(boas), ", ".join(sorted(boas)[:4])))
            continue
        (iso, prec, original), = boas.values()
        return {"VALOR": iso, "BASE": base, "PRECISAO": prec,
                "ORIGINAL": original,
                "PORQUE": "; ".join(viu + ["%s: %s" % (base, original)])}
    return {"VALOR": art.NAO_SEI, "BASE": art.NAO_SEI, "PRECISAO": art.NAO_SEI,
            "ORIGINAL": art.NAO_SEI,
            "PORQUE": "NAO SEI — " + "; ".join(viu)}


def publicacao_para_o_contrato(r: dict) -> dict:
    """O recibo de `tempo_de_publicacao`, nos nomes do contrato comum.

    → `{"PUBLISHED_AT": iso, "PUBLISHED_AT_BASIS": base}` quando há valor;
      `{"PUBLISHED_AT_BASIS": "NAO SEI — <porquê>"}` quando não há.

    ⚠️ SÓ ATRAVESSAM AFIRMAÇÕES (a regra de `ingresso.NAO_E_AFIRMACAO`): um
    `PUBLISHED_AT = "NAO SEI"` escrito no item seria lido como valor. O porquê
    do `NAO SEI` viaja na BASE, como `FACT_TIME_BASIS` já faz.

    ⚠️ E NÃO HÁ `FACT_TIME` AQUI, NEM HAVERÁ. Quando a fonte publicou não é
    quando o facto aconteceu; esta saída não tem chave para o segundo.
    """
    # D62: a PRECISÃO viaja sempre. A Intelligence tem de saber o grau de
    # cada item (INSTANTE · DIA · NAO SEI) — e nenhum grau reprova o item:
    # faltar a data não descarta nada, só diz que a precisão é menor.
    if r.get("VALOR") in (art.NAO_SEI, "", None):
        return {"PUBLISHED_AT_BASIS": r.get("PORQUE") or art.NAO_SEI,
                "PUBLISHED_AT_PRECISION": art.NAO_SEI}
    return {"PUBLISHED_AT": r["VALOR"], "PUBLISHED_AT_BASIS": r["BASE"],
            "PUBLISHED_AT_PRECISION": r.get("PRECISAO") or art.NAO_SEI}


# ── D63 · A DATA RELATIVA DO TEXTO, CONTADA A PARTIR DA PUBLICAÇÃO ─────────
#
# O dono (25/09, D63): «Ontem ou semana passada pode ser considerada data do
# fato sim, desde que o sistema pegue a data da publicação e faça a conta.»
#
#     CONTA = PUBLICATION_TIME + a expressão, e SÓ com a publicação PROVADA.
#
# ⚠️ DA-6: ESTE RAMO NÃO ESCREVE FACT_TIME. O facto a partir do texto tem um
# dono só (o extrator local `lugar-fato-v1`). Aqui a conta sai como EVIDÊNCIA
# (`RELATIVE_TIME_*`, base `RELATIVA_A_PUBLICACAO` + a expressão original),
# para esse dono decidir. A publicação continua à parte.
#
# PRECISÃO HONESTA: «ieri» é um dia; «la settimana scorsa» é a semana anterior
# INTEIRA (segunda a domingo, em intervalo ISO 8601 `início/fim`) — nunca um
# dia inventado dentro dela.
#
# ⚠️ E UM TEXTO COM DUAS CONTAS DIFERENTES NÃO RESPONDE («ieri» e «la settimana
# scorsa» no mesmo artigo): não se sabe qual é a do facto. NAO SEI, com porquê.
#
# ⚠️ «l'anno scorso» FICA DE FORA: «rispetto all'anno scorso» é comparação de
# safra e raramente data o facto. NAO SEI até haver caso medido.
# «oggi» entra só nos moldes da D64 (ver `_RELATIVAS`); hoje-em-dia não conta.
BASE_RELATIVA = "RELATIVA_A_PUBLICACAO"

_NUM = {"un": 1, "uno": 1, "una": 1, "due": 2, "tre": 3, "quattro": 4,
        "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "nove": 9, "dieci": 10}
_N = r"(\d{1,2}|un|uno|una|due|tre|quattro|cinque|sei|sette|otto|nove|dieci)"
_APOS = r"[’'`]\s?"

_DIAS_IT = ("lunedi", "martedi", "mercoledi", "giovedi", "venerdi", "sabato",
            "domenica")
_DIA_DA_SEMANA = r"lunedì|lunedi|martedì|martedi|mercoledì|mercoledi|giovedì|giovedi|venerdì|venerdi|sabato|domenica"


def _oggi_com_dia(m, dia):
    """«oggi, lunedì» conta 0 dias — só se o dia nomeado FOR o da publicação.

    Se o texto diz «oggi, lunedì» e a página foi publicada numa quarta, as
    duas afirmações contradizem-se: não se escolhe, não se conta.
    """
    nome = m.group(1).lower().replace("ì", "i")
    return 0 if _DIAS_IT.index(nome) == dia.weekday() else None


#: (padrão, espécie, como contar). A ORDEM importa: «l'altro ieri» antes de
#: «ieri», para o segundo não roubar metade do primeiro.
_RELATIVAS = (
    (r"\b(?:l" + _APOS + r"altro\s?ieri|altroieri|ieri\s+l" + _APOS + r"altro)\b",
     "DIA", lambda m, d: 2),
    (r"\b(?:ieri|ontem|yesterday)\b", "DIA", lambda m, d: 1),
    # D64: «oggi» SÓ quando o texto diz que é o próprio dia — «oggi, lunedì»
    # (e o dia da semana tem de bater com a publicação) ou «oggi è stato/a».
    # «ad oggi», «al giorno d'oggi», «oggi i consumatori» = hoje-em-dia, e
    # não casam com nenhum destes dois moldes.
    (r"\boggi,?\s+(" + _DIA_DA_SEMANA + r")\b", "DIA", _oggi_com_dia),
    (r"\boggi\s+(?:è|e'|é)\s+stat[oaie]\b", "DIA", lambda m, d: 0),
    (r"\b" + _N + r"\s+giorni\s+fa\b", "DIA", lambda m, d: _NUM.get(m.group(1).lower()) or int(m.group(1))),
    (r"\b(?:la\s+)?(?:settimana\s+scorsa|scorsa\s+settimana)\b|\b(?:semana\s+passada|last\s+week)\b",
     "SEMANA", lambda m, d: 1),
    (r"\b" + _N + r"\s+settimane\s+fa\b", "SEMANA",
     lambda m, d: _NUM.get(m.group(1).lower()) or int(m.group(1))),
    (r"\b(?:il\s+|lo\s+)?(?:mese\s+scorso|scorso\s+mese)\b|\b(?:m[eê]s\s+passado|last\s+month)\b",
     "MES", lambda m, d: 1),
)


def _dia_da_publicacao(pub: dict):
    """O DIA em que a fonte publicou, no fuso que ela escreveu. `None` sem prova."""
    if not pub or pub.get("VALOR") in (art.NAO_SEI, "", None) \
            or pub.get("BASE") in (art.NAO_SEI, "", None):
        return None
    try:
        return datetime.date.fromisoformat(str(pub["VALOR"])[:10])
    except ValueError:
        return None


def _conta(dia, especie, n):
    if especie == "DIA":
        d = dia - datetime.timedelta(days=n)
        return d.isoformat(), d, d
    if especie == "SEMANA":
        seg = dia - datetime.timedelta(days=dia.weekday() + 7 * n)
        dom = seg + datetime.timedelta(days=6)
        return "%s/%s" % (seg.isoformat(), dom.isoformat()), seg, dom
    a, m = dia.year, dia.month - n                     # MES
    while m < 1:
        a, m = a - 1, m + 12
    ini = datetime.date(a, m, 1)
    fim = (datetime.date(a + (m == 12), m % 12 + 1, 1)
           - datetime.timedelta(days=1))
    return "%s/%s" % (ini.isoformat(), fim.isoformat()), ini, fim


#: Os nomes com que um ITEM pode trazer a publicação e a base dela (D64): a
#: língua da porta, a do contrato comum e o nome que o leitor do facto usa.
NOMES_DA_PUBLICACAO = (("publication_time", "publication_time_basis"),
                       ("published_at", "published_at_basis"),
                       ("PUBLICATION_TIME", "PUBLICATION_TIME_BASIS"),
                       ("PUBLISHED_AT", "PUBLISHED_AT_BASIS"))


def publicacao_do_item(item: dict) -> dict:
    """`{VALOR, BASE}` da publicação, lida da interface do ITEM (D64).

    O leitor do facto recebe um item, não o recibo do extrator. Valor SEM base
    não é publicação provada — e sem prova não há conta (D63). Dois nomes com
    valores diferentes no mesmo item: não se escolhe, NAO SEI.
    """
    achados = set()
    for nv, nb in NOMES_DA_PUBLICACAO:
        v, b = (item or {}).get(nv), (item or {}).get(nb)
        if v in (None, "", art.NAO_SEI) or b in (None, "", art.NAO_SEI):
            continue
        if str(b).startswith(art.NAO_SEI):
            continue
        achados.add((str(v), str(b)))
    if len(achados) != 1:
        return {"VALOR": art.NAO_SEI, "BASE": art.NAO_SEI}
    (v, b), = achados
    return {"VALOR": v, "BASE": b}


def conta_relativa_a_publicacao(texto, publicacao: dict) -> dict:
    """A expressão relativa do texto, contada a partir da PUBLICATION_TIME provada.

    D63/D64 dizem COMO contar; a DA-6 diz que o facto é de outro dono. Isto
    devolve a conta como EVIDÊNCIA (ver `evidencia_relativa`), nunca FACT_TIME.

    → `{"VALOR", "BASE", "PRECISAO", "EXPRESSAO", "INICIO", "FIM", "PORQUE"}`.
    `VALOR` é um dia ISO (`2026-09-19`) ou um intervalo ISO (`início/fim`).
    `PRECISAO` é `CALCULADA:DIA` · `CALCULADA:SEMANA` · `CALCULADA:MES`.
    Sem publicação provada, sem expressão, ou com contas que se contradizem:
    tudo `NAO SEI`, e `PORQUE` diz qual das três.
    """
    nada = {"VALOR": art.NAO_SEI, "BASE": art.NAO_SEI, "PRECISAO": art.NAO_SEI,
            "EXPRESSAO": art.NAO_SEI, "INICIO": art.NAO_SEI, "FIM": art.NAO_SEI}
    dia = _dia_da_publicacao(publicacao)
    if dia is None:
        return dict(nada, PORQUE="NAO SEI — sem PUBLICATION_TIME provada nao ha "
                                 "de onde contar (D63)")
    t = str(texto or "")
    tomado = [False] * len(t)
    contas = {}
    for padrao, especie, quanto in _RELATIVAS:
        for m in re.finditer(padrao, t, re.I):
            if any(tomado[m.start():m.end()]):
                continue
            for i in range(m.start(), m.end()):
                tomado[i] = True
            n = quanto(m, dia)
            if n is None:
                continue
            valor, ini, fim = _conta(dia, especie, n)
            contas.setdefault(valor, (especie, m.group(0), ini, fim))
    if not contas:
        return dict(nada, PORQUE="NAO SEI — o texto nao traz expressao relativa "
                                 "reconhecida")
    if len(contas) > 1:
        return dict(nada, PORQUE="NAO SEI — AMBIGUO: %d contas diferentes no texto "
                                 "(%s); nao se sabe qual e a do facto"
                    % (len(contas), "; ".join("«%s» -> %s" % (e[1], v)
                                             for v, e in sorted(contas.items()))))
    (valor, (especie, expr, ini, fim)), = contas.items()
    return {"VALOR": valor, "BASE": BASE_RELATIVA,
            "PRECISAO": "CALCULADA:%s" % especie, "EXPRESSAO": expr,
            "INICIO": ini.isoformat(), "FIM": fim.isoformat(),
            "PORQUE": "%s: «%s» contado a partir da publicacao %s (%s)"
                      % (BASE_RELATIVA, expr, publicacao["VALOR"],
                         publicacao["BASE"])}


def evidencia_relativa(r: dict) -> dict:
    """A conta de `conta_relativa_a_publicacao` como EVIDÊNCIA — nunca como facto.

    ⚠️ DA-6 (coordenador, 25/09): FACT_TIME / FACT_LOCATION a partir do texto
    têm UM dono só — o extrator local `lugar-fato-v1`. Este ramo é dono SÓ de
    PUBLICATION_TIME (+ base, precisão) e SOURCE_LOCATION (+ base). Por isso
    esta saída NÃO tem chave `FACT_*`: leva a expressão encontrada e a conta
    feita a partir da publicação, com nomes de evidência, para o dono do
    facto decidir. Escrever `fact_time` aqui seria um segundo dono.

    → `{"RELATIVE_TIME_EXPRESSION", "RELATIVE_TIME_COMPUTED",
        "RELATIVE_TIME_PRECISION", "RELATIVE_TIME_BASIS"}`; sem conta, só a BASE
      com o porquê.
    """
    if r.get("VALOR") in (art.NAO_SEI, "", None):
        return {"RELATIVE_TIME_BASIS": r.get("PORQUE") or art.NAO_SEI}
    return {"RELATIVE_TIME_EXPRESSION": r["EXPRESSAO"],
            "RELATIVE_TIME_COMPUTED": r["VALOR"],
            "RELATIVE_TIME_PRECISION": r["PRECISAO"],
            "RELATIVE_TIME_BASIS": "%s «%s»" % (r["BASE"], r["EXPRESSAO"])}


def receita():
    """Os PARAMETROS da derivacao — a receita que a 022 guarda no `parameters_hash`.

    Um so sitio: `derivar_um` usa-a para escrever e `coleta/extratores_de_texto.py`
    para re-extrair (D79). Mudar isto sem subir `EXECUTOR_VERSION` reprova em
    `tests/test_a_receita_tem_versao.py`.
    """
    return {
        "TEXT_KIND": TEXT_KIND,
        "TEXT_RELATION": TEXT_RELATION,
        "TEXT_BASIS": TEXT_BASIS,
        "DERIVATION_METHOD": METODO,
        "TEXT_OWNER": CAPACIDADE["TEXT_OWNER"],
    }


def derivar_um(raw_asset_id, html, armazem, memoria, relogio=None,
               contexto_da_passagem=None) -> dict:
    """Um HTML, um pai canónico, um texto — pelo dono da escrita.

    O segundo parâmetro chama-se `html` e não `pdf` porque é o que é — mas a
    POSIÇÃO é a mesma dos outros dois executores, e é isso que deixa
    `derivacao_forward.correr()` chamar os três sem um `if`.

    ⚠️ O QUE ESTE EXECUTOR NÃO CALCULA, E POR ISSO NÃO PODE MENTIR:
    `parent_sha256`, `sha256` do filho, `parameters_hash`, `derived_at` e
    `storage_path` são todos do dono da escrita
    (`guarda/preservar_derivado.py`). Ele entrega a RECEITA e os BYTES.

    `contexto_da_passagem` é um envelope OPACO que este executor não lê.
    Viaja daqui para o dono da escrita e nada mais.
    """
    from guarda.preservar_derivado import agora_utc, preservar_derivado

    contexto = contexto_da_passagem or {}
    # ⚠️ A ESPÉCIE DE ENTRADA NÃO SE LÊ AQUI, E ISSO É DELIBERADO.
    # `contexto_da_passagem` é um envelope OPACO (a doutrina está escrita em
    # `executor_texto_de_pdf.derivar_um`): ler lá dentro quebrá-la-ia. E não é
    # preciso — quem escolhe este executor é `ingresso.executor_para`, que só
    # o escolhe para as espécies de `ACEITA`, e `limpar()` trata `text/html` e
    # `application/xhtml+xml` da mesma maneira.
    #
    #     TRANSPORTAR NÃO É CONHECER.
    media_type = "text/html"

    try:
        with open(html, "rb") as fh:
            dados = fh.read()
    except OSError as e:
        # ⚠️ NÃO CONSEGUIR ABRIR O FICHEIRO É AVARIA NOSSA, e não um documento
        # vazio. Um executor que confunde «não tenho os bytes» com «não há
        # texto» mente sobre o acervo, e a mentira fica guardada.
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": art.EXTRACTION_ERROR,
                "ERRO": "nao consegui ler %s: %s" % (html, e),
                "PORQUE": "nao consegui ler %s: %s" % (html, e),
                "NAO_SIGNIFICA": "que o documento nao tem texto.",
                "MEDIDAS": {}}

    texto, estado, erro, medidas = extrair(dados, media_type)
    if estado != art.TEXT_LAYER_PRESENT:
        # Sem texto não há artefato. Isso é um facto sobre o ORIGINAL (ou sobre
        # a declaração da espécie), e vai no recibo — não vira linha de
        # derivado.
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": estado,
                "ERRO": erro,
                "PORQUE": erro or "o documento nao trazia texto",
                "NAO_SIGNIFICA": ("que a Admissao recusou. A Admissao nem foi "
                                  "chamada."),
                "MEDIDAS": medidas}

    # ── A RECEITA ───────────────────────────────────────────────────────────
    # ⚠️ SÓ ENTRA AQUI O QUE DEFINE O ARTEFATO, NUNCA O QUE MEDE A MÁQUINA.
    # `parameters` é hasheado para `parameters_hash`, e esse hash é metade da
    # identidade da receita. `CHARACTERS` não entra: é medida, e o mesmo
    # documento extraído duas vezes pela mesma régua tem de reencontrar a
    # primeira linha em vez de escrever uma segunda.
    #
    #     O QUE VARIA ENTRE DUAS CORRIDAS IGUAIS NÃO É IDENTIDADE: É MEDIDA.
    parametros = receita()

    # ── A UNIDADE DE TEXTO, MONTADA E CONFERIDA PELO DONO ───────────────────
    # O construtor e o validador vêm de `regras/proveniencia.py`, e correm
    # ANTES de `preservar_derivado` de propósito: apanha-se a unidade inválida
    # enquanto ainda não se escreveu byte nenhum no armazém.
    unidade = pv.unidade_de_texto(
        texto=texto,
        kind=TEXT_KIND,
        kind_basis=TEXT_BASIS,
        relation=TEXT_RELATION,
        # ⚠️ A LÍNGUA NÃO SE DEDUZ DO TEXTO, e este executor não tem por onde a
        # saber: nenhum provedor a declarou a estes bytes. Fica `UNKNOWN`, que
        # é a resposta certa — «texto italiano não prova `it`».
        language=None,
        raw_observation_id=raw_asset_id,
        derivation_method=METODO,
        # A morada dentro desta observação, com produtor e versão: duas
        # extrações do MESMO HTML por réguas diferentes são duas unidades
        # legítimas.
        unit_id="TU-%s-%s" % (EXECUTOR_ID, EXECUTOR_VERSION),
        tool=FERRAMENTA)

    problemas = pv.conferir_unidade_de_texto(unidade)
    if problemas:
        return {"ESTADO": "SEM_DERIVADO",
                "MOTIVO_DO_EXECUTOR": UNIDADE_RECUSADA,
                "ERRO": "; ".join(str(p) for p in problemas)[:300],
                "PORQUE": "; ".join(str(p) for p in problemas)[:300],
                "NAO_SIGNIFICA": ("que o documento nao tem texto, nem que a "
                                  "Admissao recusou. A unidade de texto e que "
                                  "nao passou no dono do vocabulario."),
                "MEDIDAS": medidas}

    recibo = preservar_derivado(
        {**contexto,
         "raw_asset_id": raw_asset_id,
         "kind": KIND,
         "producer": EXECUTOR_ID,
         "producer_version": EXECUTOR_VERSION,
         "pipeline_version": PIPELINE_VERSION,
         "parameters": parametros,
         "serie_posicao": None,
         "media_type": "text/plain"},
        texto.encode("utf-8"), armazem, memoria,
        relogio=relogio or agora_utc)

    # A espécie do texto viaja no recibo TAMBÉM, e não só dentro de
    # `parameters`: quem lê o recibo não tem de desempacotar um hash para saber
    # que isto é `PAGE_TEXT` e não uma `CAPTION`.
    return {**recibo,
            "TEXT_KIND": TEXT_KIND,
            "TEXT_RELATION": TEXT_RELATION,
            "TEXT_UNIT": unidade,
            "LANGUAGE": None,
            "LANGUAGE_SOURCE": None,
            "MEDIDAS": medidas,
            # ⚠️ O VEREDITO DO DETECTOR «MATERIA vs PAGINA DE ENTRADA» (Q1, D11).
            # Nasce AQUI porque e aqui que estao os bytes do HTML — e o executor e
            # chamado tambem quando o derivado e REUSED, por isso o retrato viaja
            # igualmente no replay. O executor NAO decide nada com ele: transporta.
            # Quem julga e a porta de admissao (pergunta `materia`).
            "RETRATO_DO_DETECTOR": _retrato(dados)}


def _retrato(dados: bytes) -> dict | None:
    """O retrato do detector de capa (dono: curadoria/retrato_html.py, LD3), sem copia.
    `None` se o detector nao carregar: a ausencia e dita, e a porta le-a como «nao se aplica»."""
    import importlib.util  # noqa: PLC0415
    f = os.path.join(RAIZ, "curadoria", "retrato_html.py")
    try:
        spec = importlib.util.spec_from_file_location("retrato_html", f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m.retrato_do_html(dados)
    except Exception:                                            # noqa: BLE001
        return None


def _seco(caminho):
    """Olha o ficheiro e conta o que daria — sem escrever, sem banco."""
    if not os.path.isfile(caminho):
        return {"FICHEIRO": caminho, "EXISTE": False}
    with open(caminho, "rb") as fh:
        dados = fh.read()
    _, estado, erro, medidas = extrair(dados)
    return {
        "FICHEIRO": os.path.basename(caminho),
        "EXISTE": True,
        "ESTADO": estado,
        "ERRO": erro,
        "MEDIDAS": medidas,
        "TEXT_KIND_QUE_SAIRIA": TEXT_KIND,
        "TEXT_RELATION_QUE_SAIRIA": TEXT_RELATION,
        "KIND_QUE_SAIRIA": KIND,
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--ficha" in args or not args:
        print(json.dumps(CAPACIDADE, ensure_ascii=False, indent=1, default=str))
        raise SystemExit(0)
    if "--seco" in args:
        alvo = [a for a in args if a != "--seco"]
        if not alvo:
            print("uso: --seco <ficheiro>")
            raise SystemExit(2)
        print(json.dumps(_seco(alvo[0]), ensure_ascii=False, indent=1,
                         default=str))
        raise SystemExit(0)
    print("uso: --ficha | --seco <ficheiro>")
    raise SystemExit(2)
