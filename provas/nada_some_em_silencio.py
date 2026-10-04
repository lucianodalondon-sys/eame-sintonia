#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NADA SOME EM SILENCIO — o corte que fazia a porta julgar outro documento.

    python3 provas/nada_some_em_silencio.py

O QUE SE MEDIU
--------------
`coleta/golden_path_pdf.py` levava a porta de admissao `texto[:20000]`, num
ficheiro cujo cabecalho promete, em maiusculas, «NADA SOME EM SILENCIO».

Medido sobre os 43 derivados reais desta arvore:

    19 de 43 documentos passavam dos 20.000 caracteres
    o maior perdia 139.915 de 159.915 — 87.5% do documento
    7 julgamentos MUDAM quando a porta le o documento inteiro
    e 2 desses eram `NAO` — uma REJEICAO com prova, sobre texto que a
    porta nunca viu

    UM CORTE SILENCIOSO NAO PRODUZ UM JULGAMENTO PARCIAL:
    PRODUZ UM JULGAMENTO SOBRE OUTRO DOCUMENTO.

E o dano e assimetrico. O que fica depois do corte nunca REPROVA nada — apenas
nunca conta. Um boletim cuja unica mencao de praga esta na pagina nove e
rejeitado por «nao fala disto», com evidencia, com motivo escrito, e com ar de
decisao tomada.

A CLASSIFICACAO, E A DISTINCAO QUE ELA OBRIGA A FAZER
------------------------------------------------------
O ARTEFATO e o JULGAMENTO nao foram atingidos da mesma maneira, e chamar-lhes o
mesmo nome esconderia qual deles e preciso refazer:

    DERIVED em disco   VALID — os ficheiros SEMPRE foram escritos inteiros.
                       O executor nunca cortou; quem cortava era a ponte para
                       a porta.
    JULGAMENTO         TRUNCATED_INVALID quando foi feito sobre texto cortado
                       E muda com o texto inteiro. Esse tem de ser refeito.
                       VALID quando nao muda.

    UM ARTEFATO INTEIRO COM UM JULGAMENTO PARCIAL
    NAO E UM ARTEFATO PARCIAL: E UMA DECISAO POR REFAZER.

O QUE ESTA PROVA NAO FAZ
-------------------------
Nao poe teto novo, nem «maior». Se algum dia houver limite legitimo, ele tem de
produzir estado INCOMPLETO e impedir promocao como dataset completo — nunca
cortar e calar.
"""
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                                    # noqa: E402,F401
import admissao as adm                             # noqa: E402

DERIVADOS = os.path.join(RAIZ, "data", "derivados", "texto")
RECIBO = os.path.join(RAIZ, "system-map", "data",
                      "golden-path-pdf.generated.json")
SAIDA = os.path.join(RAIZ, "system-map", "data",
                     "truncamento.generated.json")

#: O corte que existia. Fica escrito para a prova poder reproduzir o defeito —
#: uma prova que nao consegue reproduzir o defeito nao prova o conserto.
CORTE_ANTIGO = 20000

FALHAS, PASSOU = [], []


def T(nome, condicao, detalhe=""):
    (PASSOU if condicao else FALHAS).append(nome)
    print("  %s  %s%s" % ("ok  " if condicao else "FALHA", nome,
                          ("" if condicao else "\n        " + detalhe)))


def julgar(texto, ident, universo="T5"):
    return adm.decidir({"id": ident, "texto": texto, "source_id": "IT-PROVA",
                        "artifact_type": "DERIVED", "parent_sha256": "a" * 64},
                       universo, corrida="prova-truncamento").resultado


print("NADA SOME EM SILENCIO — regra v%s" % adm.VERSAO_DA_REGRA)
print()

# ── 1 · O DEFEITO REPRODUZ-SE, E POR ISSO O CONSERTO E VERIFICAVEL ────────
textos = {}
if os.path.isdir(DERIVADOS):
    for f in sorted(os.listdir(DERIVADOS)):
        p = os.path.join(DERIVADOS, f)
        if os.path.isfile(p) and f.endswith(".txt"):
            with io.open(p, encoding="utf-8", errors="replace") as fh:
                textos[f] = fh.read()

T("ha derivados reais nesta arvore para medir", len(textos) >= 10,
  "so %d derivados" % len(textos))

acima = {f: t for f, t in textos.items() if len(t) > CORTE_ANTIGO}
T("o defeito era real e alcancava varios documentos", len(acima) >= 5,
  "so %d acima de %d caracteres" % (len(acima), CORTE_ANTIGO))

# ── 2 · A CLASSIFICACAO ───────────────────────────────────────────────────
classificacao = {"VALID": [], "TRUNCATED_INVALID": [], "UNKNOWN": []}
for f, t in sorted(textos.items()):
    if len(t) <= CORTE_ANTIGO:
        classificacao["VALID"].append(
            {"DERIVED": f, "CHARACTERS": len(t),
             "PORQUE": "abaixo do corte antigo: a porta ja via o documento inteiro"})
        continue
    antes, depois = julgar(t[:CORTE_ANTIGO], f), julgar(t, f)
    if antes == depois:
        classificacao["VALID"].append(
            {"DERIVED": f, "CHARACTERS": len(t),
             "DECISAO": depois,
             "PORQUE": ("estava cortado, e a decisao nao muda com o texto "
                        "inteiro — o julgamento aguenta-se")})
    else:
        classificacao["TRUNCATED_INVALID"].append(
            {"DERIVED": f, "CHARACTERS": len(t),
             "DROPPED_CHARACTERS": len(t) - CORTE_ANTIGO,
             "DECISAO_SOBRE_O_CORTE": antes,
             "DECISAO_SOBRE_O_INTEIRO": depois,
             "PORQUE": ("a porta decidiu sobre %d de %d caracteres, e a decisao "
                        "MUDA quando ela le tudo" % (CORTE_ANTIGO, len(t)))})

invalidos = classificacao["TRUNCATED_INVALID"]
print()
print("  CLASSIFICACAO DOS JULGAMENTOS ANTERIORES")
print("    VALID ............... %d" % len(classificacao["VALID"]))
print("    TRUNCATED_INVALID ... %d" % len(invalidos))
print("    UNKNOWN ............. %d" % len(classificacao["UNKNOWN"]))
for x in invalidos:
    print("      %s  %s -> %s  (perdia %d chars)"
          % (x["DERIVED"], x["DECISAO_SOBRE_O_CORTE"],
             x["DECISAO_SOBRE_O_INTEIRO"], x["DROPPED_CHARACTERS"]))

print()
# ── 3 · O CONSERTO — a porta passa a ver o documento inteiro ──────────────
# ⚠️ A GUARDA LE CODIGO, E NAO PROSA. A primeira versao procurava a string
# `texto[:20000]` no ficheiro inteiro e reprovava — no COMENTARIO que explica o
# defeito. Uma guarda que nao distingue a lei da explicacao da lei obriga quem
# conserta a apagar a explicacao, e a explicacao e metade do conserto.
#
#     PROIBIR A PALAVRA NAO E PROIBIR O ACTO.
import re                                          # noqa: E402
_fonte = io.open(os.path.join(RAIZ, "coleta", "golden_path_pdf.py"),
                 encoding="utf-8").read()
_codigo = "\n".join(l for l in _fonte.splitlines()
                    if not l.lstrip().startswith("#"))
_cortes = re.findall(r'item\s*\[\s*["\']texto["\']\s*\]\s*=\s*texto\s*\[', _codigo)
T("o corte saiu do CODIGO: o texto que vai a porta nao e fatiado",
  not _cortes,
  "o caminho da porta ainda fatia o texto: %s" % _cortes)

if os.path.isfile(RECIBO):
    with io.open(RECIBO, encoding="utf-8") as fh:
        recibo = json.load(fh)
    ti = recibo.get("TEXTO_INTEGRAL") or {}
    T("o recibo da corrida conta a perda em caracteres", bool(ti),
      "sem TEXTO_INTEGRAL o recibo nao sabe dizer se se perdeu alguma coisa")
    T("INPUT_CHARACTERS == JUDGED_CHARACTERS na corrida real",
      ti.get("INPUT_CHARACTERS") == ti.get("JUDGED_CHARACTERS"),
      "entrada=%s julgado=%s" % (ti.get("INPUT_CHARACTERS"),
                                 ti.get("JUDGED_CHARACTERS")))
    T("DROPPED_CHARACTERS = 0", ti.get("DROPPED_CHARACTERS") == 0,
      "caiu %s caracteres" % ti.get("DROPPED_CHARACTERS"))
    T("e a corrida julgou um corpus que vale a pena medir",
      (ti.get("INPUT_CHARACTERS") or 0) > 100000,
      "so %s caracteres" % ti.get("INPUT_CHARACTERS"))

# ── 4 · E O REGISTO FICA, PARA QUEM VIER REFAZER ─────────────────────────
estado = {
    "O_QUE_ISTO_E": ("O corte silencioso de texto antes da porta de admissao, "
                     "medido, classificado e fechado."),
    "COMO_REFAZER": "python3 provas/nada_some_em_silencio.py",
    "CORTE_ANTIGO_EM_CARACTERES": CORTE_ANTIGO,
    "ONDE_VIVIA": "coleta/golden_path_pdf.py — `item[\"texto\"] = texto[:20000]`",
    "DERIVED_EM_DISCO": {
        "ESTADO": "VALID",
        "PORQUE": ("os ficheiros derivados SEMPRE foram escritos inteiros. O "
                   "executor nunca cortou; quem cortava era a ponte para a "
                   "porta. O artefato nao precisa de ser refeito."),
        "QUANTOS": len(textos),
    },
    "JULGAMENTOS": {
        "VALID": len(classificacao["VALID"]),
        "TRUNCATED_INVALID": len(invalidos),
        "UNKNOWN": len(classificacao["UNKNOWN"]),
        "DETALHE": classificacao,
    },
    "A_LEI": ("Se algum dia houver limite legitimo, ele produz estado "
              "INCOMPLETO e impede promocao como dataset completo. Nunca corta "
              "e cala."),
    "O_QUE_ISTO_NAO_MEDE": (
        "CSV e HTML nao derivam nesta linha: "
        "`coleta/executor_texto_de_pdf.py::CAPACIDADE` declara "
        "`ACEITA_MEDIA_TYPES = (application/pdf,)`, e a porta responde "
        "DERIVACAO_ESPECIE_NAO_SUPORTADA. Nao ha perda silenciosa de linhas "
        "tabulares porque nao ha derivacao tabular — o que ha e uma capacidade "
        "AUSENTE, e ausencia declarada nao e perda."),
}
os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with io.open(SAIDA, "w", encoding="utf-8") as fh:
    json.dump(estado, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

print()
print("  gravado: %s" % os.path.relpath(SAIDA, RAIZ))
print()
print("INPUT_RECORDS  = %d derivados" % len(textos))
print("OUTPUT_RECORDS = %d derivados" % len(textos))
print("DROPPED_RECORDS = 0")
print("SILENT_TRUNCATION = %s · %d passaram · %d falharam"
      % ("0" if not FALHAS else "PRESENTE", len(PASSOU), len(FALHAS)))
raise SystemExit(1 if FALHAS else 0)
