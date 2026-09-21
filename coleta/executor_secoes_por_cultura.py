#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O EXECUTOR QUE GUARDA A CULTURA DO CABEÇALHO — secções por cultura de um boletim.

    O DADO CHEGOU. A ESTRUTURA NÃO.        (piloto da Sala, R2, §C)

MEDIDO ANTES DE ESCREVER UMA LINHA (missão C-CROP-E2E-V1, 2026-09-20)
---------------------------------------------------------------------
Os cinco itens `IT-T3` da Sala perderam a cultura, e não a perderam no mesmo
sítio. Três boletins, três padrões, medidos nos bytes guardados:

    IT-T3-002  Salerno   a cultura é a PRIMEIRA COLUNA de uma tabela
                         («COLTURA | N° | Comune | ... »). O `pdftotext` em
                         modo corrido parte as células por linhas: o nome da
                         cultura sobrevive, 0 a 3 linhas depois de «COLTURA»,
                         misturado com os títulos das outras colunas. O
                         cabeçalho está no texto; ninguém o lia.
    IT-T3-010  APOL      o anexo «Difesa integrata Olivo Puglia 2026» tem a
                         cultura NO TÍTULO da tabela; as substâncias vivem
                         nas linhas dessa tabela. O boletim de monitorização
                         acima não nomeia a cultura — nomeia a praga.
    IT-T3-008  ARIF      a cultura de cada bloco é um ÍCONE (imagem 124×129).
                         Zero cabeçalhos de cultura em maiúsculas na camada de
                         texto, em quatro modos do `pdftotext` e no leitor
                         próprio da casa. A prosa diz «mosca dell'olivo»;
                         isso é contexto, não chave.

Por isso este executor faz UMA coisa: preserva a associação que o próprio
documento declara entre um CABEÇALHO DE CULTURA e o BLOCO de texto que lhe
pertence — e diz, secção a secção, com que precisão a sabe.

    CABEÇALHO DE CULTURA  →  BLOCO  →  (o que a Intelligence lê lá dentro)

O QUE ELE NÃO FAZ
-----------------
    NÃO promove menção a cultura. «olivo» no corpo do texto é CANDIDATO
    (`CONTEXT_ONLY`), nunca `CROP_EXPLICIT`. Só um cabeçalho declara.
    NÃO normaliza para `CROP_ID`. A chave que sai é a do vocabulário da casa
    (`leis/regua_italia.py::CULTURAS`), com `CERTEZA = OBSERVADO_NO_CABECALHO`;
    a equivalência com o rótulo é decisão da Intelligence (INT-LAW-080..084).
    NÃO extrai claim, fato, praga nem substância (COL-LAW-202: TARGET).
    NÃO faz OCR. O ícone do ARIF fica `UNKNOWN`, e `UNKNOWN` fica.
    NÃO vai à rede, NÃO conhece banco, NÃO conhece corrida.

POR QUE `kind = TABLE_EXTRACTION`
---------------------------------
A `migration 022` fecha o vocabulário de `derived_artifact.kind`, e inventar
um nome novo dá erro de escrita que se lê como avaria do armazém. O que se
extrai aqui É a associação cabeçalho→linhas da tabela do boletim — a coluna
«COLTURA» de Salerno, o título da tabela do disciplinare da Puglia. É uma
extração de tabela reduzida à única coluna que a Intelligence precisa como
chave. O `producer` distingue-a de qualquer outra extração de tabela.

POR QUE NÃO ESTÁ EM `ingresso._DONOS_DA_DERIVACAO`
-------------------------------------------------
Aquela lista responde «QUEM ABRE esta espécie?», e quem abre o PDF continua a
ser `executor_texto_de_pdf`. Este é uma SEGUNDA leitura do mesmo bruto, com
outra receita, e é chamado por quem rederiva (`provas/a_cultura_atravessa.py`).
Ligá-lo à estrada forward automática é outra decisão, de outro dono.

    py coleta/executor_secoes_por_cultura.py <ficheiro.pdf>     # só olha e conta
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401
import artefato as art  # noqa: E402
import executor_texto_de_pdf as ex  # noqa: E402
import regua_italia as regua  # noqa: E402 — o DONO do vocabulário de culturas

EXECUTOR_ID = "secoes-por-cultura"
EXECUTOR_VERSION = "1"
PIPELINE_VERSION = "1"
SCHEMA = "sintonia.derivado.secoes-por-cultura/1"

#: O `kind` vem do vocabulário fechado da 022. Ver o cabeçalho.
KIND = "TABLE_EXTRACTION"
MEDIA_TYPE = "application/json"

CAPACIDADE = {
    "EXECUTOR_ID": EXECUTOR_ID,
    "VERSION": EXECUTOR_VERSION,
    "SUPPORTS": ["PDF_RAW"],
    "ACEITA_MEDIA_TYPES": ("application/pdf",),
    "PRODUCES": ["CROP_SECTIONS"],
    "NETWORK_REQUIRED": "NO",
    "OCR": "NO",
    "CHECKPOINT": art.NAO_SE_APLICA,
    "COST_CLASS": "LOCAL",
    "FERRAMENTA_EXTERNA": "pdftotext (poppler/xpdf) — a mesma do texto-de-pdf",
    "SEGUNDA_LEITURA_DE": "texto-de-pdf",
}

# ── OS TRÊS ESTADOS, E SÃO MESMO TRÊS ─────────────────────────────────────
EXPLICIT = "EXPLICIT"            # um cabeçalho nomeia a cultura desta secção
CONTEXT_ONLY = "CONTEXT_ONLY"    # há termo de cultura no corpo; ninguém a declarou
UNKNOWN = "UNKNOWN"              # nada — e nada fica nada

# ── OS TIPOS DE SECÇÃO ─────────────────────────────────────────────────────
PREAMBLE = "PREAMBLE"            # o que vem antes do primeiro marcador
SECTION_HEADER = "SECTION_HEADER"  # «COLTURA ...» (tabela de Salerno)
TABLE_TITLE = "TABLE_TITLE"      # «Difesa integrata <cultura> ...» (disciplinare)
CONTEXT_BLOCK = "CONTEXT_BLOCK"  # «Situazione Fenologica:» (bloco do ARIF)

# ── COMO SE SABE ───────────────────────────────────────────────────────────
OBSERVADO_NO_CABECALHO = "OBSERVADO_NO_CABECALHO"
OBSERVADO_NO_CORPO = "OBSERVADO_NO_CORPO"
NAO_SEI = "NAO_SEI"

# Os marcadores. Caixa exacta onde o documento a usa: «coltura» em prosa
# minúscula não é cabeçalho de tabela, e «difesa integrata» no fim de uma
# frase do preâmbulo de Salerno não é título de disciplinare — o título vem
# capitalizado e com o nome da cultura a seguir.
RX_COLTURA = re.compile(r"^COLTURA\b")
RX_TITULO_DIFESA = re.compile(r"^Difesa integrata\s+\S.{0,70}$")
RX_BLOCO = re.compile(r"^Situazione Fenologica\s*:", re.IGNORECASE)

#: Quantas linhas depois de «COLTURA» a célula da cultura ainda pode estar.
#: Medido em 12 de 12 blocos do boletim de Salerno n.27: a célula cai 0 a 8
#: linhas abaixo de «COLTURA» (NOCE, na n.27, cai na oitava). Dez dá margem
#: sem alcançar o bloco seguinte — o mais curto tem 20 linhas.
JANELA_DO_CABECALHO = 10

# No cabeçalho exige-se PALAVRA INTEIRA. O vocabulário da régua casa por
# prefixo («vite» apanha «vitello») porque conta com a âncora e com a
# quarentena; num cabeçalho de uma palavra, «Viterbo» não pode virar VITE.
_CULT_CABECALHO = [(k, re.compile(rx.pattern + r"\b"), anc)
                   for k, rx, anc in regua.CULT_RX]


def _cultura_no_cabecalho(janela: str):
    """→ (chave, termo_como_escrito) da PRIMEIRA cultura que aparece na janela,
    ou (None, None). A janela é o próprio anúncio «COLTURA»/«Difesa
    integrata»: é âncora agrícola por construção, e por isso a quarentena da
    régua não se aplica aqui — aplica-se a palavra inteira."""
    norm = regua._n(janela)
    melhor = None
    for chave, rx, _anc in _CULT_CABECALHO:
        m = rx.search(norm)
        if m and (melhor is None or m.start() < melhor[0]):
            melhor = (m.start(), chave, m.group(0))
    if melhor is None:
        return None, None
    _, chave, termo_norm = melhor
    # O termo COMO ESCRITO: procura-se a forma original na janela, sem acento
    # e sem caixa; se a normalização mudou o comprimento, fica a forma normalizada.
    m = re.search(re.escape(termo_norm), janela, re.IGNORECASE)
    return chave, (m.group(0) if m else termo_norm)


def _candidatos_no_corpo(texto: str):
    """As culturas MENCIONADAS no corpo, pela régua da casa e com a sua
    quarentena. Candidatos, contados — nunca uma chave."""
    norm = regua._n(texto)
    tem_anc = bool(regua.ANCORA.search(norm))
    fora = []
    for chave, termo, _item in regua._casar(norm, regua.CULT_RX, tem_anc):
        rx = dict((k, r) for k, r, _a in regua.CULT_RX)[chave]
        fora.append({"CROP": chave, "TERM": termo, "N": len(rx.findall(norm))})
    fora.sort(key=lambda c: (-c["N"], c["CROP"]))
    return fora, tem_anc


def seccionar(texto: str) -> dict:
    """O texto corrido → as secções, cada uma com a cultura QUE O DOCUMENTO
    DECLAROU para ela, e com que precisão.

    Função pura: sem ficheiro, sem banco, sem rede. É ela que os testes
    atacam.
    """
    linhas = texto.split("\n")
    inicio = []
    pos = 0
    for l in linhas:
        inicio.append(pos)
        pos += len(l) + 1

    marcadores = []
    for i, l in enumerate(linhas):
        s = l.strip()
        if not s:
            continue
        if RX_COLTURA.match(s):
            janela = " ".join(x.strip() for x in linhas[i:i + JANELA_DO_CABECALHO])
            chave, termo = _cultura_no_cabecalho(janela)
            marcadores.append((i, SECTION_HEADER, chave, termo, s, janela))
        elif RX_TITULO_DIFESA.match(s):
            chave, termo = _cultura_no_cabecalho(s)
            marcadores.append((i, TABLE_TITLE, chave, termo, s, s))
        elif RX_BLOCO.match(s):
            marcadores.append((i, CONTEXT_BLOCK, None, None, s, s))

    limites = []
    if not marcadores or marcadores[0][0] > 0:
        limites.append((0, marcadores[0][0] if marcadores else len(linhas),
                        (None, PREAMBLE, None, None, None, None)))
    for n, m in enumerate(marcadores):
        fim = marcadores[n + 1][0] if n + 1 < len(marcadores) else len(linhas)
        limites.append((m[0], fim, m))

    secoes = []
    for ordem, (a, b, m) in enumerate(limites):
        corpo = "\n".join(linhas[a:b])
        if not corpo.strip():
            continue
        _i, kind, chave, termo, cabecalho, janela = m
        candidatos, tem_anc = _candidatos_no_corpo(corpo)
        if chave:
            status, precisao, certeza = EXPLICIT, kind, OBSERVADO_NO_CABECALHO
        elif candidatos:
            status, precisao, certeza = CONTEXT_ONLY, "BODY_MENTION", OBSERVADO_NO_CORPO
        else:
            status, precisao, certeza = UNKNOWN, "NONE", NAO_SEI
        ini = inicio[a]
        fim_char = inicio[b - 1] + len(linhas[b - 1]) if b > a else ini
        secoes.append({
            "ORDEM": ordem,
            "KIND": kind,
            "STATUS": status,
            "CROP_EXPLICIT": chave,
            "CROP_TERM_AS_WRITTEN": termo,
            "CROP_CONTEXT": {
                "HEADER_TEXT": cabecalho,
                "HEADER_WINDOW": janela,
                "CANDIDATES": candidatos,
                "ANCORA_AGRICOLA_NO_CORPO": tem_anc,
            },
            "EVIDENCE_ANCHOR": {
                "LINE_START": a, "LINE_END": b - 1,
                "CHAR_START": ini, "CHAR_END": fim_char,
            },
            "PRECISION": precisao,
            "CERTEZA": certeza,
            "CHARS": len(corpo),
            "TEXTO": corpo,
        })

    explicit = sorted({s["CROP_EXPLICIT"] for s in secoes if s["STATUS"] == EXPLICIT})
    contexto = sorted({c["CROP"] for s in secoes if s["STATUS"] != EXPLICIT
                       for c in s["CROP_CONTEXT"]["CANDIDATES"]})
    return {
        "SCHEMA": SCHEMA,
        "PRODUCER": EXECUTOR_ID,
        "PRODUCER_VERSION": EXECUTOR_VERSION,
        "VOCABULARIO": "leis/regua_italia.py::CULTURAS",
        "TEXTO_SHA256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
        "TEXTO_CHARS": len(texto),
        "FONTE_DO_TEXTO": ("pdftotext -enc UTF-8, a mesma receita do executor "
                           "texto-de-pdf; as âncoras são posições nesse texto"),
        "O_QUE_ISTO_E": ("a associação cabeçalho-de-cultura → bloco, tal como o "
                         "documento a declara. Chave candidata OBSERVADA, não "
                         "normalizada."),
        "O_QUE_ISTO_NAO_E": ("não é FACT, não é CLAIM, não é CROP_ID. Menção no "
                             "corpo é CONTEXT_ONLY; ícone sem texto é UNKNOWN; "
                             "e UNKNOWN fica UNKNOWN."),
        "RESUMO": {
            "SECOES": len(secoes),
            "EXPLICIT": sum(1 for s in secoes if s["STATUS"] == EXPLICIT),
            "CONTEXT_ONLY": sum(1 for s in secoes if s["STATUS"] == CONTEXT_ONLY),
            "UNKNOWN": sum(1 for s in secoes if s["STATUS"] == UNKNOWN),
            "CROPS_EXPLICIT": explicit,
            "CROPS_CONTEXT_ONLY": contexto,
        },
        "SECOES": secoes,
    }


def bytes_do_artefato(seccoes: dict) -> bytes:
    """Bytes determinísticos: chaves ordenadas, LF, sem ASCII forçado."""
    return (json.dumps(seccoes, ensure_ascii=False, indent=1, sort_keys=True)
            + "\n").encode("utf-8")


def extrair(pdf: Path):
    """→ (seccoes | None, estado, erro, medidas). Sem camada de texto não há
    secções — e isso é um facto sobre o ORIGINAL, como no executor de PDF."""
    texto, estado, erro, medidas = ex.extrair(Path(pdf))
    if estado != art.TEXT_LAYER_PRESENT:
        return None, estado, erro, medidas
    return seccionar(texto), estado, "", medidas


def derivar_um(raw_asset_id, pdf, armazem, memoria, relogio=None,
               contexto_da_passagem=None) -> dict:
    """Um PDF, um pai canónico, um derivado de secções — pelo dono da escrita.

    Mesma disciplina de `executor_texto_de_pdf.derivar_um`: este executor
    entrega a receita e os bytes; `parent_sha256`, `sha256`, `derived_at` e
    `storage_path` são do dono. O envelope `contexto_da_passagem` viaja
    fechado.
    """
    from guarda.preservar_derivado import agora_utc, preservar_derivado

    seccoes, estado, erro, medidas = extrair(Path(pdf))
    if seccoes is None:
        return {"ESTADO": "SEM_DERIVADO", "MOTIVO_DO_EXECUTOR": estado,
                "ERRO": erro, "MEDIDAS": medidas}
    return preservar_derivado(
        {**(contexto_da_passagem or {}),
         "raw_asset_id": raw_asset_id,
         "kind": KIND,
         "producer": EXECUTOR_ID,
         "producer_version": EXECUTOR_VERSION,
         "pipeline_version": PIPELINE_VERSION,
         # A receita, e só ela. O sha do texto NÃO entra aqui de propósito:
         # se entrasse, um pdftotext diferente daria uma segunda receita
         # calada em vez de DERIVATION_DRIFT.
         "parameters": {"REGRA": "secoes-por-cultura",
                        "VOCABULARIO": "leis/regua_italia.py::CULTURAS",
                        "TEXTO": "pdftotext -enc UTF-8 (texto-de-pdf)"},
         "serie_posicao": None,
         "media_type": MEDIA_TYPE},
        bytes_do_artefato(seccoes), armazem, memoria,
        relogio=relogio or agora_utc)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print(__doc__)
        return 0
    for caminho in argv:
        seccoes, estado, erro, _m = extrair(Path(caminho))
        print("%s  %s %s" % (caminho, estado, erro))
        if seccoes is None:
            continue
        r = seccoes["RESUMO"]
        print("  secoes=%d explicit=%d context_only=%d unknown=%d"
              % (r["SECOES"], r["EXPLICIT"], r["CONTEXT_ONLY"], r["UNKNOWN"]))
        print("  CROPS_EXPLICIT      = %s" % r["CROPS_EXPLICIT"])
        print("  CROPS_CONTEXT_ONLY  = %s" % r["CROPS_CONTEXT_ONLY"])
        for s in seccoes["SECOES"]:
            print("   #%-2d %-14s %-12s %-10s %s" % (
                s["ORDEM"], s["KIND"], s["STATUS"], s["CROP_EXPLICIT"] or "-",
                (s["CROP_CONTEXT"]["HEADER_TEXT"] or "")[:50]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
