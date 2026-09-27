#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PORTAO DE QUALIDADE DE T3 — receber a revisao A sem lhe tocar.

    python3 provas/qualidade_t3.py
    python3 provas/qualidade_t3.py --escrever

Sem rede, sem banco, sem recoleta. Nenhum rotulo e atribuido, mudado ou
normalizado aqui.

    HUMAN_REVIEW_INPUT = READ_ONLY
    AUTO_RELABEL = 0

O QUE ESTA MISSAO RECEBEU
-------------------------
Um ficheiro que veio de UMA PESSOA. Ele e evidencia externa ao gerador, e por
isso e imutavel: nao se reescreve, nao se ordena e grava por cima, nao se
«corrige» uma resposta, e nao se normaliza um rotulo em silencio. A prova de
que ele nao mudou e o seu SHA256, registado antes de qualquer leitura.

AS DUAS FILAS, E POR QUE SAO DUAS
---------------------------------
    CONFIRMACAO       a resposta ja esta dada; falta a RAZAO e a atestacao
                      de que o conteudo exibido foi o conteudo usado
    SEGUNDA LEITURA   a resposta volta a ser feita, CEGA — sem ver a primeira

A segunda leitura e cega porque uma pessoa que ve a propria resposta anterior
concorda com ela. Isso nao e uma segunda opiniao: e a mesma, repetida.

    REVIEW_A != REVIEW_A2
    E NENHUM DOS DOIS E UM SEGUNDO REVISOR INDEPENDENTE:
    E A MESMA PESSOA, EM SEGUNDA PASSAGEM.
"""
import hashlib
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import importlib.util  # noqa: E402


def _modulo(nome, ficheiro):
    spec = importlib.util.spec_from_file_location(
        nome, os.path.join(RAIZ, "provas", ficheiro))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pacote_t3 = _modulo("_pacote_t3", "pacote_de_revisao_t3.py")

ENTRADA = "data/review/inbox/T3-HUMAN-REVIEW-RESULTS-V1.json"
PRESERVADO = "data/review/t3/T3-HUMAN-REVIEW-A-V1.json"
CONTEXTO = "data/review/t3/T3-CONTEXTO-CEGO-PTBR-V1.json"
PENDENTE = "data/samples/T3-HUMAN-REVIEW-PENDING-V1.json"
HTML = "docs/operacao/T3-HUMAN-QUALITY-GATE-PTBR-V1.html"

ROTULOS = ("T3_SIM", "T3_NAO", "T3_AMBIGUO", "EVIDENCIA_INSUFICIENTE")

# ── O GATILHO DA SEGUNDA LEITURA ───────────────────────────────────────────
# ⚠️ ISTO NAO E UMA CLASSIFICACAO. Nao muda `T3_NAO`, nao prova `T3_SIM`, e
# nao diz que a pessoa errou. Diz uma coisa so:
#
#     VALE A PENA OLHAR OUTRA VEZ, COM MAIS CONTEXTO.
#
# A primeira leitura viu ~900 caracteres. Quando um documento respondido
# `T3_NAO` se auto-declara fitossanitario logo na abertura, a tensao entre a
# resposta e o texto e razao suficiente para uma segunda passagem — e NUNCA
# razao para trocar a resposta por conta propria.
GATILHOS = ("bollettino fitosanitario", "servizio fitosanitario",
            "difesa integrata", "bilancio fitosanitario")


def sha256_do_ficheiro(caminho):
    with open(os.path.join(RAIZ, caminho), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _json(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as f:
        return json.load(f)


class RevisaoInvalida(Exception):
    """O ficheiro humano nao passa na conferencia. NAO se conserta: para-se."""


def carregar_a():
    """Le a revisao A e prova-a contra o pacote. Nunca escreve nela."""
    a = _json(ENTRADA)
    itens = a["ITEMS"]
    if a.get("SCHEMA") != "sintonia.t3-human-review-results/1":
        raise RevisaoInvalida("schema inesperado: %r" % a.get("SCHEMA"))
    if a.get("STATUS") != "COMPLETE":
        raise RevisaoInvalida("STATUS = %r; so entra revisao completa"
                              % a.get("STATUS"))
    if not (a["TOTAL_EXPECTED"] == a["TOTAL_REVIEWED"] == len(itens) == 53):
        raise RevisaoInvalida("contagens nao fecham")
    shas = [x["DOC_SHA256"] for x in itens]
    if len(set(shas)) != len(shas):
        raise RevisaoInvalida("ha DOC_SHA256 repetido")
    maus = {x["LABEL"] for x in itens} - set(ROTULOS)
    if maus:
        raise RevisaoInvalida("rotulo fora do vocabulario: %s" % sorted(maus))

    pacote = {x["DOC_SHA256"]: x for x in _json(PENDENTE)["ITENS"]}
    faltam = [s for s in shas if s not in pacote]
    if faltam:
        raise RevisaoInvalida("%d itens da revisao nao estao no pacote" % len(faltam))
    sobram = [s for s in pacote if s not in set(shas)]
    if sobram:
        raise RevisaoInvalida("%d itens do pacote sem revisao" % len(sobram))
    # A evidencia que a pessoa VIU tem de ser, byte a byte, a do pacote.
    divergem = [x["ITEM_ID"] for x in itens
                if x["ORIGINAL_EVIDENCE"] != pacote[x["DOC_SHA256"]]["EVIDENCE"]]
    if divergem:
        raise RevisaoInvalida("evidencia divergente em %s" % divergem[:5])
    return a, pacote


def _texto_visto(item):
    e = item["ORIGINAL_EVIDENCE"]
    return " ".join([e["TITLE"], e["OPENING"]]
                    + e["SELF_DESCRIPTION"] + e["SECTION_HEADERS"]).lower()


def filas(itens):
    """As duas filas, e a razao de cada item estar onde esta."""
    incerteza = [x for x in itens
                 if x["LABEL"] in ("EVIDENCIA_INSUFICIENTE", "T3_AMBIGUO")]
    tensao = [x for x in itens
              if x["LABEL"] == "T3_NAO"
              and any(g in _texto_visto(x) for g in GATILHOS)]
    cega_shas = ({x["DOC_SHA256"] for x in incerteza}
                 | {x["DOC_SHA256"] for x in tensao})
    cega = [x for x in itens if x["DOC_SHA256"] in cega_shas]
    confirmacao = [x for x in itens if x["DOC_SHA256"] not in cega_shas]
    return confirmacao, cega, incerteza, tensao


# ── O CONTEXTO MAIOR, PARA A FILA CEGA ─────────────────────────────────────
# A primeira leitura viu ~900 caracteres. Para decidir outra vez e preciso
# mais — e «mais» tem de ser escolhido por uma regra ESTRUTURAL, nunca pelo
# trecho que contem a expressao do gatilho.
#
#     MOSTRAR SO O PEDACO QUE DISPAROU A REVISAO
#     E ENTREGAR A RESPOSTA COM CARA DE PERGUNTA.
#
# Entao: o documento inteiro, do principio, partido em paginas de tamanho
# fixo. Quem navega e a pessoa.
POR_PAGINA = 3000
MAX_PAGINAS = 10          # tecto do que viaja dentro do HTML
TRADUZIDO_ATE = 3600      # quanto vai traduzido para portugues


def contexto_do_documento(ficha):
    """O texto integral, limpo e paginado. Nada aqui escolhe por assunto."""
    bruto = pacote_t3._ler_documento(ficha["BODY_PATH"])
    inteiro = " ".join(pacote_t3._linhas(bruto)) if not ficha["BODY_PATH"].endswith(
        ".csv") else bruto
    paginas = [inteiro[i:i + POR_PAGINA]
               for i in range(0, len(inteiro), POR_PAGINA)]
    return {
        "TOTAL_CARACTERES": len(inteiro),
        "TOTAL_PAGINAS": len(paginas),
        "PAGINAS_MOSTRADAS": min(len(paginas), MAX_PAGINAS),
        "PAGINAS": paginas[:MAX_PAGINAS],
        "TRADUZIDO_ATE": min(TRADUZIDO_ATE, len(inteiro)),
        "TEXTO_A_TRADUZIR": inteiro[:TRADUZIDO_ATE],
    }


TRADUCAO = "data/review/t3/T3-TRADUCAO-CONTEXTO-CEGO-PTBR-V1.json"

# ── A RAZAO ESTRUTURADA ────────────────────────────────────────────────────
# A revisao A trouxe 53 respostas e ZERO razoes: `HUMAN_REASON` veio nulo em
# todas, porque a primeira interface nunca perguntou.
#
#     CAN DO != DID DO.
#     UM CAMPO QUE EXISTE E UM CAMPO QUE NINGUEM PREENCHEU
#     SAO A MESMA COLUNA VAZIA.
#
# Aqui a razao e PERGUNTADA. Nao e inferida do rotulo, nao e escrita por
# ninguem a nao ser a pessoa, e `OUTRO` exige o texto dela.
RAZOES = {
    "T3_SIM": [
        ("NOMEIA_PRAGA_OU_DOENCA",
         "O texto nomeia uma praga ou uma doença de planta"),
        ("DESCREVE_PRESENCA_OU_DANO",
         "O texto descreve presença, monitoramento ou dano no campo"),
        ("RECOMENDA_DEFESA",
         "O texto recomenda como se defender de praga ou doença"),
        ("OUTRO", "Outro motivo — eu escrevo"),
    ],
    "T3_NAO": [
        ("ASSUNTO_DIFERENTE", "O assunto do texto é outro"),
        ("CITACAO_DE_PASSAGEM",
         "Praga ou doença aparece de passagem, não é do que o texto trata"),
        ("REGISTO_OU_ESTATISTICA",
         "É registo, preço, área plantada, autorização ou tabela administrativa"),
        ("OUTRO", "Outro motivo — eu escrevo"),
    ],
    "T3_AMBIGUO": [
        ("VARIOS_ASSUNTOS", "O texto trata de vários assuntos e este é um deles"),
        ("LEITURA_DUPLA", "Dá para ler dos dois jeitos, com honestidade"),
        ("OUTRO", "Outro motivo — eu escrevo"),
    ],
    "EVIDENCIA_INSUFICIENTE": [
        ("TRECHO_CURTO", "O que foi mostrado é curto demais para decidir"),
        ("TEXTO_QUEBRADO", "O texto veio quebrado, cortado ou ilegível"),
        ("PARECE_BUG", "Parece erro de coleta, não documento"),
        ("OUTRO", "Outro motivo — eu escrevo"),
    ],
}

BOTOES = [
    ("T3_SIM", "✓", "SIM",
     "Trata de praga ou doença de planta"),
    ("T3_NAO", "✗", "NÃO",
     "Não trata disso"),
    ("T3_AMBIGUO", "≈", "AMBÍGUO",
     "Trata em parte, ou dá para ler dos dois jeitos"),
    ("EVIDENCIA_INSUFICIENTE", "?", "NÃO DÁ PARA SABER",
     "O texto mostrado não é suficiente"),
]

# Nenhuma destas CHAVES pode viajar dentro da pagina para um item da fila
# cega. Procura-se a chave com aspas — o conteudo de um boletim pode dizer
# «servizio fitosanitario» sem que isso seja um campo a vazar.
PROIBIDOS_NA_FILA_CEGA = ('"LABEL_A"', '"NOTE_A"', '"LABEL"', '"MOTIVO_DA_FILA"',
                          '"GATILHO"', '"DECISAO_ATUAL_DA_PORTA_PARA_T3"',
                          '"TERRITORIO_DA_FICHA_DA_FONTE"', '"UNIVERSE_ANTERIOR"',
                          '"GABARITO_T2"')


def envelope_de_a(a):
    """A revisao A, intacta, dentro de um envelope que diz de onde ela veio."""
    return {
        "SCHEMA": "sintonia.t3-human-review-a/1",
        "O_QUE_ISTO_E": (
            "A revisao humana A, preservada BYTE A BYTE como a pessoa a "
            "exportou. Nada aqui foi reordenado, corrigido ou normalizado. O "
            "conteudo de REVIEW_A e copia literal do ficheiro de entrada."),
        "REGRA": "HUMAN_REVIEW_INPUT = READ_ONLY. AUTO_RELABEL = 0.",
        "QUEM_REVIU": (
            "Uma pessoa. NAO e um segundo revisor independente e NAO e "
            "maquina. Uma segunda passagem da mesma pessoa chama-se A2 — "
            "REVIEW_A != REVIEW_A2."),
        "INGESTED_FROM": ENTRADA,
        "INPUT_SHA256": sha256_do_ficheiro(ENTRADA),
        "AUTO_LABELS_ASSIGNED": 0,
        "REVIEW_A": a,
    }


def _traducoes():
    return {t["ORIGINAL_SHA256"]: t["TEXTO_PTBR"]
            for t in _json(TRADUCAO)["TRADUCOES"]}


def contexto_completo(a, pacote):
    """O contexto maior de CADA item — paginado, e traduzido so onde ha
    traducao presa ao texto exato. Traducao que nao bate e descartada."""
    pt = _traducoes()
    conf, cega, _, _ = filas(a["ITEMS"])
    cegos = {x["DOC_SHA256"] for x in cega}
    saida = []
    for x in a["ITEMS"]:
        c = contexto_do_documento(pacote[x["DOC_SHA256"]])
        janela = c.pop("TEXTO_A_TRADUZIR")
        assinatura = hashlib.sha256(janela.encode("utf-8")).hexdigest()
        c.update({
            "DOC_SHA256": x["DOC_SHA256"],
            "ITEM_ID": x["ITEM_ID"],
            "NA_FILA_CEGA": x["DOC_SHA256"] in cegos,
            "ORIGINAL_SHA256_DA_JANELA": assinatura,
            # None quando nao ha traducao — NUNCA um texto inventado.
            "JANELA_PTBR": pt.get(assinatura),
        })
        saida.append(c)
    return {
        "SCHEMA": "sintonia.t3-contexto-cego-ptbr/1",
        "O_QUE_ISTO_E": (
            "O texto integral de cada documento, limpo e partido em paginas de "
            "%d caracteres, mais a traducao pt-BR da janela de abertura. Serve "
            "a segunda leitura, que precisa de mais do que os ~900 caracteres "
            "que a primeira viu." % POR_PAGINA),
        "COMO_AS_PAGINAS_FORAM_ESCOLHIDAS": (
            "Do principio, em pedacos de tamanho fixo, ate ao tecto de %d "
            "paginas. A regra e ESTRUTURAL e cega ao assunto: nao se escolheu "
            "o trecho que contem a expressao que mandou o item para a fila." %
            MAX_PAGINAS),
        "REGRA": "DISPLAY_TRANSLATION != EVIDENCE. Nenhum rotulo aqui.",
        "TOTAL": len(saida),
        "AUTO_LABELS_ASSIGNED": 0,
        "ITENS": saida,
    }


DISPLAY = "data/samples/T3-DISPLAY-TRANSLATION-PTBR-V1.json"


def dados_do_portao(a, pacote):
    """O que a pagina leva dentro — e, na fila cega, o que ela NAO leva.

    Um item da fila cega viaja SEM rotulo, sem nota, sem o motivo de ter
    entrado na fila e sem a expressao que o mandou para la. Nao basta nao
    desenhar isso no ecra: se o dado estiver no JSON da pagina, ele vazou.

        ESCONDER NA INTERFACE E DEIXAR NO PAYLOAD
        NAO E CEGAR: E ESPERAR QUE NINGUEM OLHE.
    """
    pt = {t["DOC_SHA256"]: t for t in _json(DISPLAY)["TRADUCOES"]}
    ctx = {c["DOC_SHA256"]: c for c in contexto_completo(a, pacote)["ITENS"]}
    conf, cega, _, _ = filas(a["ITEMS"])

    def base(x):
        i, t = pacote[x["DOC_SHA256"]], pt[x["DOC_SHA256"]]
        e, c = x["ORIGINAL_EVIDENCE"], ctx[x["DOC_SHA256"]]
        return {
            "DOC_SHA256": x["DOC_SHA256"],
            "ITEM_ID": x["ITEM_ID"],
            "PUBLISHER": i["PUBLISHER"],
            "DOCUMENT_TYPE": i["DOCUMENT_TYPE"],
            "ORIGINAL_EVIDENCE": {
                "TITLE": e["TITLE"], "OPENING": e["OPENING"],
                "SELF_DESCRIPTION": e["SELF_DESCRIPTION"],
                "SECTION_HEADERS": e["SECTION_HEADERS"]},
            "DISPLAY_TRANSLATION_PTBR": {
                "TITLE": t["TITLE"], "OPENING": t["OPENING"],
                "SELF_DESCRIPTION": t["SELF_DESCRIPTION"],
                "SECTION_HEADERS": t["SECTION_HEADERS"]},
            "CONTEXTO": {
                "TOTAL_CARACTERES": c["TOTAL_CARACTERES"],
                "TOTAL_PAGINAS": c["TOTAL_PAGINAS"],
                "PAGINAS": c["PAGINAS"],
                "JANELA_PTBR": c["JANELA_PTBR"],
                "TRADUZIDO_ATE": c["TRADUZIDO_ATE"]},
        }

    # Na confirmacao a resposta de A esta a vista: e disso que a fila trata.
    fila_conf = []
    for x in conf:
        d = base(x)
        d.update({"FILA": "CONFIRMACAO", "LABEL_A": x["LABEL"],
                  "NOTE_A": x.get("NOTE")})
        fila_conf.append(d)
    # Na fila cega nao ha campo de rotulo nenhum — nem vazio, nem nulo.
    # Ordem por ITEM_ID: uma ordem que nao diz nada sobre a resposta.
    fila_cega = []
    for x in sorted(cega, key=lambda y: y["ITEM_ID"]):
        d = base(x)
        d["FILA"] = "CEGA"
        fila_cega.append(d)
    return fila_conf, fila_cega


PAGINA = r"""<!doctype html>
<html lang="pt-BR"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Portão de qualidade — Revisão T3</title>
<style>
:root{
  --tinta:#15201c; --tinta-fraca:#5d6b65; --papel:#f7f6f2; --cartao:#fff;
  --linha:#dfe3df; --acento:#1f6f4a; --sim:#1f6f4a; --nao:#9c2b2b;
  --amb:#9a6a10; --sem:#4a5568; --marca:#eef3ef;
}
*{box-sizing:border-box}
body{margin:0;background:var(--papel);color:var(--tinta);
  font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
html,body{overflow-x:clip}
.envolve{max-width:820px;margin:0 auto;padding:16px}
header{position:sticky;top:0;background:var(--papel);z-index:5;
  border-bottom:1px solid var(--linha);padding-block:12px}
h1{font-size:17px;margin:0 0 8px;letter-spacing:.02em}
.conta{font-size:14px;color:var(--tinta-fraca);display:flex;
  justify-content:space-between;gap:12px;flex-wrap:wrap}
.barra{height:8px;background:var(--marca);border-radius:99px;margin-top:10px;
  overflow:hidden}
.barra i{display:block;height:100%;background:var(--acento);width:0;
  transition:width .25s}
.aviso{background:#fff8e6;border:1px solid #e8d9a8;border-radius:10px;
  padding:12px 14px;font-size:14px;margin:16px 0}
.cartao{background:var(--cartao);border:1px solid var(--linha);
  border-radius:14px;padding:18px;margin:16px 0}
.proc{font-size:13px;color:var(--tinta-fraca);text-transform:uppercase;
  letter-spacing:.06em;margin-bottom:10px}
h2{font-size:20px;line-height:1.3;margin:0 0 14px;overflow-wrap:anywhere}
h2.cru{font-size:14px;font-weight:500;line-height:1.45;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  color:var(--tinta-fraca)}
h3{font-size:16px;margin:22px 0 8px}
.trecho{background:#fbfbf9;border:1px solid var(--linha);border-radius:10px;
  padding:14px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:15px}
.trecho.tabela{white-space:pre;overflow-x:auto;font-family:ui-monospace,
  SFMono-Regular,Menlo,Consolas,monospace;font-size:13px;line-height:1.5}
.rot{font-size:13px;font-weight:600;color:var(--tinta-fraca);
  text-transform:uppercase;letter-spacing:.05em;margin:18px 0 8px}
ul.sinais{margin:0;padding-left:20px;font-size:15px}
ul.sinais li{overflow-wrap:anywhere}
details{margin-top:16px;border-top:1px solid var(--linha);padding-top:12px}
summary{cursor:pointer;font-weight:600;color:var(--acento);font-size:15px;
  padding:6px 0}
.orig{font-size:14px;color:#33403a}
.dada{border:2px solid var(--acento);background:var(--marca);border-radius:12px;
  padding:16px;margin:18px 0}
.dada .qual{font-size:22px;font-weight:700;letter-spacing:.03em}
.dada .qual.T3_SIM{color:var(--sim)} .dada .qual.T3_NAO{color:var(--nao)}
.dada .qual.T3_AMBIGUO{color:var(--amb)}
.dada .qual.EVIDENCIA_INSUFICIENTE{color:var(--sem)}
.atesta{display:flex;gap:12px;align-items:flex-start;border:2px solid var(--linha);
  border-radius:12px;padding:14px 16px;margin:18px 0;cursor:pointer;background:#fff}
.atesta[data-on="1"]{border-color:var(--acento);background:var(--marca)}
.atesta input{margin-top:3px;width:20px;height:20px;flex:0 0 auto}
.atesta span{font-size:15px}
.botoes{display:grid;gap:10px;margin:12px 0 8px}
button.voto{display:flex;align-items:center;gap:12px;width:100%;
  text-align:left;padding:16px 18px;border-radius:12px;border:2px solid var(--linha);
  background:#fff;font:inherit;cursor:pointer;min-height:60px}
button.voto:hover:not(:disabled){border-color:var(--acento)}
button.voto:disabled{opacity:.45;cursor:not-allowed}
button.voto .em{font-size:22px;line-height:1}
button.voto b{display:block;font-size:16px}
button.voto span{display:block;font-size:13px;color:var(--tinta-fraca)}
button.voto[aria-pressed="true"]{border-color:var(--acento);background:var(--marca)}
button.voto[data-l="T3_SIM"][aria-pressed="true"]{border-color:var(--sim)}
button.voto[data-l="T3_NAO"][aria-pressed="true"]{border-color:var(--nao)}
button.voto[data-l="T3_AMBIGUO"][aria-pressed="true"]{border-color:var(--amb)}
button.voto[data-l="EVIDENCIA_INSUFICIENTE"][aria-pressed="true"]{border-color:var(--sem)}
.razoes label{display:flex;gap:11px;align-items:flex-start;padding:11px 13px;
  border:1px solid var(--linha);border-radius:10px;margin-bottom:8px;cursor:pointer;
  background:#fff;font-size:15px}
.razoes label:has(input:checked){border-color:var(--acento);background:var(--marca)}
.razoes input{margin-top:3px;width:18px;height:18px;flex:0 0 auto}
textarea{width:100%;min-height:60px;border:1px solid var(--linha);
  border-radius:10px;padding:10px;font:inherit;resize:vertical}
button.guarda{width:100%;padding:16px;border-radius:12px;border:0;
  background:var(--acento);color:#fff;font:600 16px/1 inherit;cursor:pointer;
  min-height:56px;margin-top:16px}
button.guarda:disabled{background:var(--linha);color:var(--tinta-fraca);
  cursor:not-allowed}
button.rever{width:100%;margin-top:14px;padding:11px;border-radius:10px;
  border:1px dashed var(--linha);background:transparent;color:var(--tinta-fraca);
  font:13px/1.4 inherit;cursor:pointer}
button.rever:hover{border-color:var(--nao);color:var(--nao)}
nav.passos{display:flex;gap:10px;justify-content:space-between;margin:18px 0}
nav.passos button{flex:1;padding:12px;border-radius:10px;border:1px solid var(--linha);
  background:#fff;font:inherit;cursor:pointer;min-height:48px}
nav.passos button:disabled{opacity:.4;cursor:default}
.pag{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}
.pag button{padding:7px 12px;border-radius:8px;border:1px solid var(--linha);
  background:#fff;font:600 13px/1 inherit;cursor:pointer}
.pag button.agora{border-color:var(--acento);background:var(--marca)}
.grelha{display:flex;flex-wrap:wrap;gap:5px;margin:14px 0}
.grelha button{width:34px;height:34px;border-radius:8px;border:1px solid var(--linha);
  background:#fff;font:600 12px/1 inherit;cursor:pointer}
.grelha button.f{background:var(--marca);border-color:var(--acento)}
.grelha button.agora{outline:2px solid var(--tinta)}
.fim{text-align:center}
.fim table{margin:18px auto;border-collapse:collapse;font-size:16px}
.fim td{padding:8px 18px;border-bottom:1px solid var(--linha);text-align:left}
.fim td:last-child{text-align:right;font-variant-numeric:tabular-nums;font-weight:700}
button.baixar{padding:18px 24px;border-radius:12px;border:0;background:var(--acento);
  color:#fff;font:600 17px/1 inherit;cursor:pointer;min-height:60px;width:100%}
button.baixar.rascunho{background:var(--sem)}
.nota{font-size:14px;color:var(--tinta-fraca);margin-top:16px}
.tec{font-size:13px;color:var(--tinta-fraca);overflow-wrap:anywhere}
.tec div{margin:3px 0}
.inicio table{width:100%;border-collapse:collapse;font-size:16px;margin:18px 0}
.inicio td{padding:10px 4px;border-bottom:1px solid var(--linha)}
.inicio td:last-child{text-align:right;font-weight:700;
  font-variant-numeric:tabular-nums}
@media (max-width:520px){.envolve{padding:12px}h2{font-size:18px}}
@media (prefers-color-scheme:dark){
 :root:not([data-theme="light"]){--tinta:#e8eeea;--tinta-fraca:#9aa8a2;
  --papel:#111613;--cartao:#19211d;--linha:#2c3833;--acento:#6ac093;
  --marca:#1d2a24;--sim:#6ac093;--nao:#e08a8a;--amb:#e0b96a;--sem:#9aa8a2}
 :root:not([data-theme="light"]) .trecho{background:#141b17}
 :root:not([data-theme="light"]) button.voto,
 :root:not([data-theme="light"]) nav.passos button,
 :root:not([data-theme="light"]) .atesta,
 :root:not([data-theme="light"]) .razoes label,
 :root:not([data-theme="light"]) .pag button,
 :root:not([data-theme="light"]) .grelha button{background:#19211d;color:inherit}
 :root:not([data-theme="light"]) .aviso{background:#241f12;border-color:#4a3f22}
 :root:not([data-theme="light"]) .orig{color:#c3cec8}
}
</style></head><body><div class="envolve">
<header>
 <h1>PORTÃO DE QUALIDADE — REVISÃO T3</h1>
 <div class="conta"><span id="onde"></span><span id="pct"></span></div>
 <div class="barra"><i id="barra"></i></div>
</header>
<div id="palco"></div>
</div>
<script id="conf" type="application/json">__CONF__</script>
<script id="cega" type="application/json">__CEGA__</script>
<script>
const CONF = JSON.parse(document.getElementById('conf').textContent);
const CEGA = JSON.parse(document.getElementById('cega').textContent);
const RAZOES = __RAZOES__;
const BOTOES = __BOTOES__;
const CHAVE = 'sintonia.t3.portao.v1';
const palco = document.getElementById('palco');

// Estado. `reabertos` guarda os SHA que a pessoa tirou da confirmacao para
// responder outra vez. Um item reaberto NAO e cego: ela ja viu a resposta.
let st = ler(), i = -1;   // -1 = ecra de entrada
function vazio(){ return {respostas:{}, reabertos:[]}; }
function ler(){ try{ const x=JSON.parse(localStorage.getItem(CHAVE));
                     return (x&&x.respostas)?x:vazio(); }catch(e){ return vazio(); } }
function gravar(){ try{ localStorage.setItem(CHAVE, JSON.stringify(st)); }
                   catch(e){ alerta(); } }
function alerta(){
  if(document.getElementById('semstorage')) return;
  const d=document.createElement('div'); d.id='semstorage'; d.className='aviso';
  d.textContent='Atenção: este navegador não está guardando o progresso. '
    +'Não feche a aba antes de exportar.';
  document.querySelector('header').after(d);
}
function reaberto(sha){ return st.reabertos.indexOf(sha) >= 0; }
// A ordem de trabalho: primeiro a confirmacao (menos os reabertos), depois a
// segunda leitura (mais os reabertos, no fim).
function ordem(){
  const c = CONF.filter(d=>!reaberto(d.DOC_SHA256));
  const r = CONF.filter(d=>reaberto(d.DOC_SHA256));
  return c.concat(CEGA, r);
}
// ⚠️ Um item conta como respondido quando tem DECISAO — rotulo (ou
// confirmacao), razao e atestacao. Virar a pagina do contexto tambem escreve
// em `respostas`, para nao perder onde a pessoa ia.
//
//     CONTAR A EXISTENCIA DA LINHA EM VEZ DA DECISAO
//     E UMA BARRA DE PROGRESSO QUE ANDA SOZINHA.
function feitas(){ return ordem().filter(respondido).length; }
function esc(s){ const d=document.createElement('div'); d.textContent=s??'';
                 return d.innerHTML; }
function tabela(t){ return (t||'').indexOf('\n') >= 0; }
function cru(t){ return (t||'').split(/\s+/).some(w=>w.length>40); }
function lista(a){ return (a&&a.length)
  ? '<ul class="sinais">'+a.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>'
  : '<p class="tec">— nenhum —</p>'; }
function nomeRotulo(l){ const b=BOTOES.find(x=>x[0]===l); return b?b[2]:l; }

function pinta(){
  const fila = ordem(), n = fila.length, f = feitas();
  document.getElementById('onde').textContent =
    i < 0 ? 'Antes de começar' : (i < n ? 'Item '+(i+1)+' de '+n : 'Concluído');
  document.getElementById('pct').textContent = f+' de '+n+' respondidos';
  document.getElementById('barra').style.width = Math.round(f/n*100)+'%';
  if(i < 0)      { palco.innerHTML = inicio();  ligaInicio(); }
  else if(i < n) { palco.innerHTML = ficha(fila[i], i); liga(fila[i]); }
  else           { palco.innerHTML = fim();     ligaFim(); }
  window.scrollTo(0,0);
}

function inicio(){
  return '<div class="cartao inicio">'
   + '<h2>A sua revisão chegou inteira.</h2>'
   + '<table><tr><td>Respostas recebidas</td><td>'+(CONF.length+CEGA.length)
   + ' de '+(CONF.length+CEGA.length)+'</td></tr>'
   + '<tr><td>Para confirmar</td><td>'+CONF.length+'</td></tr>'
   + '<tr><td>Para ler uma segunda vez</td><td>'+CEGA.length+'</td></tr></table>'
   + '<h3>O que vai acontecer</h3>'
   + '<p>Nos <b>'+CONF.length+' primeiros</b> a sua resposta aparece na tela. '
   + 'O que falta é <b>dizer por quê</b> e confirmar que foi mesmo o texto '
   + 'mostrado que você usou para decidir.</p>'
   + '<p>Nos <b>'+CEGA.length+' seguintes</b> a sua resposta <b>não</b> '
   + 'aparece, e você responde de novo — desta vez com muito mais texto à '
   + 'vista. Não há nada de errado com eles. Nós só queremos ler duas vezes.</p>'
   + '<div class="aviso"><b>Uma coisa que precisa ser dita.</b> Você é a mesma '
   + 'pessoa que respondeu da primeira vez. '
   + 'Isto <b>não</b> é um segundo revisor independente, '
   + 'e o sistema não vai fingir que é. Se as duas '
   + 'respostas não baterem, o resultado fica <b>em aberto</b> — ninguém '
   + 'escolhe uma delas por você.</div>'
   + '<button class="guarda" id="comecar">COMEÇAR</button></div>';
}
function ligaInicio(){
  palco.querySelector('#comecar').onclick = ()=>{ i = proximaEmFalta(-1); pinta(); };
}

function evidencia(d){
  const p = d.DISPLAY_TRANSLATION_PTBR, o = d.ORIGINAL_EVIDENCE;
  return '<h2'+(cru(p.TITLE)?' class="cru"':'')+'>'+esc(p.TITLE)+'</h2>'
   + '<div class="rot">Trecho principal (traduzido)</div>'
   + '<div class="trecho'+(tabela(p.OPENING)?' tabela':'')+'">'+esc(p.OPENING)+'</div>'
   + '<div class="rot">Como o documento se descreve</div>'+lista(p.SELF_DESCRIPTION)
   + '<div class="rot">Outros títulos visíveis</div>'+lista(p.SECTION_HEADERS)
   + '<details><summary>Mostrar original em italiano</summary>'
   + '<div class="orig"><div class="rot">Título original</div>'
   + '<div class="trecho">'+esc(o.TITLE)+'</div>'
   + '<div class="rot">Trecho original</div>'
   + '<div class="trecho'+(tabela(o.OPENING)?' tabela':'')+'">'+esc(o.OPENING)+'</div>'
   + '<div class="rot">Auto-descrição original</div>'+lista(o.SELF_DESCRIPTION)
   + '<div class="rot">Títulos originais</div>'+lista(o.SECTION_HEADERS)
   + '</div></details>';
}

// O contexto maior: o documento do principio, em paginas de tamanho fixo.
// A traducao cobre so a janela de abertura; onde nao ha, diz-se que nao ha.
function contexto(d, pag){
  const c = d.CONTEXTO, n = c.PAGINAS.length;
  const pt = (pag===0 && c.JANELA_PTBR)
    ? '<div class="rot">Abertura traduzida (primeiros '+c.TRADUZIDO_ATE
      +' caracteres)</div><div class="trecho'
      +(tabela(c.JANELA_PTBR)?' tabela':'')+'">'+esc(c.JANELA_PTBR)+'</div>'
    : (pag===0 ? '<p class="tec">Não há tradução para este documento. '
        +'Abaixo está o original.</p>' : '');
  const barra = n>1 ? '<div class="pag">'+c.PAGINAS.map((_,k)=>
      '<button data-p="'+k+'" class="'+(k===pag?'agora':'')+'">'+(k+1)
      +'</button>').join('')+'</div>' : '';
  const corte = c.TOTAL_PAGINAS > n
    ? '<p class="tec">Mostrando '+n+' de '+c.TOTAL_PAGINAS+' páginas ('
      +c.TOTAL_CARACTERES+' caracteres no total). O documento continua além '
      +'do que cabe aqui.</p>' : '';
  return '<h3>Texto completo do documento</h3>'
   + '<p class="tec">Do começo, em pedaços iguais. Nenhum pedaço foi escolhido '
   + 'pelo assunto.</p>' + pt + barra
   + '<div class="rot">Original — página '+(pag+1)+' de '+n+'</div>'
   + '<div class="trecho'+(tabela(c.PAGINAS[pag])?' tabela':'')+'">'
   + esc(c.PAGINAS[pag])+'</div>' + corte;
}

function ficha(d, k){
  const r = st.respostas[d.DOC_SHA256] || {};
  const conf = d.FILA==='CONFIRMACAO' && !reaberto(d.DOC_SHA256);
  const pag = r.PAGINA || 0;
  let h = '<div class="cartao">'
   + '<div class="proc">'+esc(d.PUBLISHER)+' · '+esc(d.DOCUMENT_TYPE)
   + ' · '+(conf?'CONFIRMAÇÃO':'SEGUNDA LEITURA')+'</div>'
   + evidencia(d);
  if(conf){
    h += '<div class="dada"><div class="rot" style="margin-top:0">'
      +  'A sua resposta da primeira vez</div>'
      +  '<div class="qual '+esc(d.LABEL_A)+'">'+esc(nomeRotulo(d.LABEL_A))+'</div>'
      +  (d.NOTE_A ? '<div class="tec" style="margin-top:8px">Sua observação: '
           +esc(d.NOTE_A)+'</div>' : '')
      +  '</div>'
      +  '<h3>Por que esta resposta?</h3>'
      +  razoes(d.LABEL_A, r)
      +  atestacao(r)
      +  '<button class="guarda" id="ok">CONFIRMAR</button>'
      +  '<button class="rever" id="rever">Rever minha resposta — mandar este '
      +  'item para a segunda leitura</button>';
  } else {
    h += contexto(d, pag)
      +  (reaberto(d.DOC_SHA256)
          ? '<div class="aviso">Você já viu a sua resposta anterior neste item. '
            +'Isto fica registrado: esta leitura <b>não</b> é cega.</div>' : '')
      +  '<h3>Lendo agora, o texto trata de praga ou doença de planta?</h3>'
      +  '<div class="botoes">'
      +  BOTOES.map(b=>'<button class="voto" data-l="'+b[0]+'" aria-pressed="'
           +(r.LABEL===b[0])+'"><span class="em">'+b[1]+'</span><span><b>'+b[2]
           +'</b><span>'+b[3]+'</span></span></button>').join('')
      +  '</div>'
      +  '<div id="porque">'+(r.LABEL?('<h3>Por quê?</h3>'+razoes(r.LABEL,r)):'')+'</div>'
      +  atestacao(r)
      +  '<button class="guarda" id="ok">GUARDAR</button>';
  }
  h += '<details><summary>Detalhes técnicos</summary><div class="tec">'
    +  '<div>DOC_SHA256: '+esc(d.DOC_SHA256)+'</div>'
    +  '<div>ITEM_ID: '+esc(d.ITEM_ID)+'</div></div></details></div>'
    +  '<nav class="passos"><button id="ant"'+(k===0?' disabled':'')
    +  '>← Anterior</button><button id="prox">Pular / Próximo →</button></nav>'
    +  grelha();
  return h;
}

function razoes(label, r){
  const rs = RAZOES[label] || [];
  return '<div class="razoes">'
   + rs.map(x=>'<label><input type="radio" name="razao" value="'+x[0]+'"'
       +(r.REASON_CODE===x[0]?' checked':'')+'><span>'+x[1]+'</span></label>').join('')
   + '</div><div id="outro"'+(r.REASON_CODE==='OUTRO'?'':' hidden')+'>'
   + '<div class="rot">Escreva o motivo</div>'
   + '<textarea id="razaotexto">'+esc(r.REASON_TEXT||'')+'</textarea></div>';
}

// EVIDENCE_PRESENTED != EVIDENCE_USED. A pagina sabe o que MOSTROU; so a
// pessoa sabe o que USOU. Entao pergunta-se, e nada e guardado sem resposta.
function atestacao(r){
  return '<label class="atesta" data-on="'+(r.EVIDENCE_ATTESTED?'1':'0')+'">'
   + '<input type="checkbox" id="atesto"'+(r.EVIDENCE_ATTESTED?' checked':'')+'>'
   + '<span>Eu li o texto acima e foi nele que me baseei para responder.</span>'
   + '</label>';
}

function grelha(){
  const fila = ordem();
  return '<div class="grelha">'+fila.map((d,k)=>'<button data-k="'+k+'" class="'
    +(respondido(d)?'f ':'')+(k===i?'agora':'')+'">'+(k+1)
    +'</button>').join('')+'</div>';
}

function estado(){
  const rad = palco.querySelector('input[name=razao]:checked');
  const cod = rad ? rad.value : null;
  const txt = (palco.querySelector('#razaotexto')||{}).value || '';
  const at  = !!(palco.querySelector('#atesto')||{}).checked;
  return {cod:cod, txt:txt.trim(), at:at};
}
// Sem razao e sem atestacao nao se guarda nada. E `OUTRO` sem texto e o
// mesmo que razao nenhuma.
function podeGuardar(precisaRotulo, temRotulo){
  const e = estado();
  if(precisaRotulo && !temRotulo) return false;
  if(!e.cod) return false;
  if(e.cod==='OUTRO' && !e.txt) return false;
  return e.at;
}

function liga(d){
  const conf = d.FILA==='CONFIRMACAO' && !reaberto(d.DOC_SHA256);
  const r = st.respostas[d.DOC_SHA256] || {};
  let rotulo = conf ? d.LABEL_A : (r.LABEL||null);

  function repinta(){
    const ok = palco.querySelector('#ok');
    if(ok) ok.disabled = !podeGuardar(!conf, !!rotulo);
    const a = palco.querySelector('.atesta');
    if(a) a.dataset.on = (palco.querySelector('#atesto').checked?'1':'0');
    const rad = palco.querySelector('input[name=razao]:checked');
    const o = palco.querySelector('#outro');
    if(o) o.hidden = !(rad && rad.value==='OUTRO');
  }
  palco.addEventListener('change', repinta);
  palco.addEventListener('input', repinta);

  palco.querySelectorAll('button.voto').forEach(b=>{
    b.onclick = ()=>{
      rotulo = b.dataset.l;
      palco.querySelectorAll('button.voto').forEach(x=>
        x.setAttribute('aria-pressed', String(x.dataset.l===rotulo)));
      palco.querySelector('#porque').innerHTML = '<h3>Por quê?</h3>'
        + razoes(rotulo, {});
      repinta();
    };
  });

  const ok = palco.querySelector('#ok');
  if(ok) ok.onclick = ()=>{
    const e = estado();
    st.respostas[d.DOC_SHA256] = {
      LABEL: rotulo, REASON_CODE: e.cod, REASON_TEXT: e.cod==='OUTRO'? e.txt : null,
      EVIDENCE_ATTESTED: e.at, CONFIRMOU_A: conf,
      PAGINA: (st.respostas[d.DOC_SHA256]||{}).PAGINA || 0,
      DECIDED_AT: new Date().toISOString()};
    gravar(); i = proximaEmFalta(i); pinta();
  };

  const rever = palco.querySelector('#rever');
  if(rever) rever.onclick = ()=>{
    if(st.reabertos.indexOf(d.DOC_SHA256) < 0) st.reabertos.push(d.DOC_SHA256);
    delete st.respostas[d.DOC_SHA256];
    gravar();
    const fila = ordem();
    i = fila.findIndex(x=>x.DOC_SHA256===d.DOC_SHA256);
    pinta();
  };

  palco.querySelectorAll('.pag button').forEach(b=>{
    b.onclick = ()=>{
      const s = st.respostas[d.DOC_SHA256] || {};
      s.PAGINA = +b.dataset.p; st.respostas[d.DOC_SHA256] = s;
      gravar(); pinta();
    };
  });
  palco.querySelector('#ant').onclick = ()=>{ if(i>0){ i--; pinta(); } };
  palco.querySelector('#prox').onclick = ()=>{ i = Math.min(i+1, ordem().length); pinta(); };
  palco.querySelectorAll('.grelha button').forEach(b=>{
    b.onclick = ()=>{ i = +b.dataset.k; pinta(); };
  });
  repinta();
}

function respondido(d){
  const r = st.respostas[d.DOC_SHA256];
  return !!(r && r.REASON_CODE && r.EVIDENCE_ATTESTED);
}
function proximaEmFalta(desde){
  const fila = ordem();
  for(let k=desde+1;k<fila.length;k++) if(!respondido(fila[k])) return k;
  for(let k=0;k<fila.length;k++) if(!respondido(fila[k])) return k;
  return fila.length;
}

function fim(){
  const fila = ordem();
  const f = feitas(), completo = f===fila.length;
  const conf = fila.filter(d=>respondido(d) && st.respostas[d.DOC_SHA256].CONFIRMOU_A).length;
  const seg  = f - conf;
  return '<div class="cartao fim">'
   + '<h2>'+(completo?'PORTÃO CONCLUÍDO':'PORTÃO INCOMPLETO')+'</h2>'
   + '<table><tr><td>Confirmados</td><td>'+conf+'</td></tr>'
   + '<tr><td>Lidos uma segunda vez</td><td>'+seg+'</td></tr>'
   + '<tr><td>Reabertos por você</td><td>'+st.reabertos.length+'</td></tr>'
   + '<tr><td>TOTAL</td><td>'+f+' de '+fila.length+'</td></tr></table>'
   + '<button class="baixar'+(completo?'':' rascunho')+'" id="baixar">'
   + (completo?'BAIXAR RESULTADO JSON':'EXPORTAR RASCUNHO')+'</button>'
   + '<p class="nota">Este arquivo <b>não decide</b> o rótulo final. Onde a '
   + 'segunda leitura não bater com a primeira, o item fica <b>em aberto</b> '
   + 'e volta para uma decisão humana. Nada aqui é escrito automaticamente '
   + 'em nenhum arquivo do projeto.</p></div>'
   + '<nav class="passos"><button id="ant">← Voltar</button>'
   + '<button id="prox" disabled>—</button></nav>' + grelha();
}
function ligaFim(){
  palco.querySelector('#ant').onclick = ()=>{ i = Math.max(0,ordem().length-1); pinta(); };
  palco.querySelectorAll('.grelha button').forEach(b=>{
    b.onclick = ()=>{ i = +b.dataset.k; pinta(); };
  });
  palco.querySelector('#baixar').onclick = baixar;
}

function baixar(){
  const fila = ordem(), f = feitas();
  const completo = f===fila.length;
  const saida = {
    SCHEMA:"sintonia.t3-human-quality-gate-results/1", UNIVERSE:"T3",
    DESCRIPTION:"Praga e doença", REVIEW_TYPE:"HUMAN", PASS:"A2",
    QUEM_REVIU:"A MESMA PESSOA DA REVISAO A, EM SEGUNDA PASSAGEM",
    INDEPENDENT_SECOND_REVIEWER:false,
    FINAL_LABEL_DECIDIDO_AQUI:false, AUTO_LABELS_ASSIGNED:0,
    LANGUAGE_OF_INTERFACE:"pt-BR",
    SOURCE_REVIEW_A:"T3-HUMAN-REVIEW-A-V1.json",
    STATUS: completo?"COMPLETE":"INCOMPLETE",
    TOTAL_EXPECTED: fila.length, TOTAL_ANSWERED: f,
    COMPLETED_AT: completo? new Date().toISOString() : null,
    ITEMS: fila.filter(respondido).map(d=>{
      const r = st.respostas[d.DOC_SHA256], rb = reaberto(d.DOC_SHA256);
      const o = {DOC_SHA256:d.DOC_SHA256, ITEM_ID:d.ITEM_ID,
        QUEUE: r.CONFIRMOU_A ? "CONFIRMACAO" : "SEGUNDA_LEITURA",
        BLIND: !r.CONFIRMOU_A && !rb,
        REOPENED_BY_HUMAN: rb ? "YES" : "NO",
        REASON_CODE: r.REASON_CODE, REASON_TEXT: r.REASON_TEXT ?? null,
        EVIDENCE_ATTESTED: r.EVIDENCE_ATTESTED === true,
        DECIDED_AT: r.DECIDED_AT};
      // A resposta de A so viaja de volta onde a pagina legitimamente a tinha.
      if(r.CONFIRMOU_A){ o.LABEL_A = d.LABEL_A; o.CONFIRMED = true; }
      else if(rb){ o.LABEL_A = d.LABEL_A; o.LABEL_A2 = r.LABEL; }
      else { o.LABEL_A2 = r.LABEL; }
      return o;
    })
  };
  const b = new Blob([JSON.stringify(saida,null,1)],{type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(b);
  a.download = 'T3-HUMAN-QUALITY-GATE-RESULTS-V1.json';
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(()=>URL.revokeObjectURL(a.href), 4000);
}

if(feitas()>0 || Object.keys(st.respostas).length>0) i = proximaEmFalta(-1);
pinta();
</script></body></html>
"""


def construir(a, pacote):
    conf, cega = dados_do_portao(a, pacote)
    def bruto(x):
        return json.dumps(x, ensure_ascii=False).replace("</", "<\\/")
    return (PAGINA
            .replace("__CONF__", bruto(conf))
            .replace("__CEGA__", bruto(cega))
            .replace("__RAZOES__", bruto(RAZOES))
            .replace("__BOTOES__", bruto(BOTOES)))


def escrever(caminho, doc):
    alvo = os.path.join(RAIZ, caminho)
    os.makedirs(os.path.dirname(alvo), exist_ok=True)
    with open(alvo, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    a, pacote = carregar_a()
    itens = a["ITEMS"]
    conf, cega, incerteza, tensao = filas(itens)
    contagem = {r: sum(1 for x in itens if x["LABEL"] == r) for r in ROTULOS}
    fila_conf, fila_cega = dados_do_portao(a, pacote)
    pagina = construir(a, pacote)
    ctx = contexto_completo(a, pacote)

    print("PORTAO DE QUALIDADE DE T3 — INGESTAO DE A E PREPARO DE A2")
    print("=" * 74)
    print("  REVISAO RECEBIDA")
    print(f"    INPUT_SHA256             {sha256_do_ficheiro(ENTRADA)}")
    print(f"    STATUS                   {a['STATUS']}")
    print(f"    TOTAL_REVIEWED           {a['TOTAL_REVIEWED']}/{a['TOTAL_EXPECTED']}")
    print(f"    EVIDENCE_IDENTITY_MATCH  YES")
    print(f"    AUTO_RELABEL             0")
    for r in ROTULOS:
        print(f"    {r:<24} {contagem[r]}")
    print(f"    HUMAN_REASON nao nulo    "
          f"{sum(1 for x in itens if x.get('HUMAN_REASON'))}")
    print(f"    NOTE nao nulo            "
          f"{sum(1 for x in itens if x.get('NOTE'))}")
    print("  AS DUAS FILAS")
    print(f"    CONFIRMATION_QUEUE       {len(conf)}")
    print(f"    SECOND_REVIEW_QUEUE      {len(cega)}   "
          f"(incerteza {len(incerteza)} + tensao {len(tensao)})")
    print("  O CONTEXTO DA SEGUNDA LEITURA")
    cegos = [c for c in ctx["ITENS"] if c["NA_FILA_CEGA"]]
    print(f"    DOCUMENTOS               {len(cegos)}")
    print(f"    COM_TRADUCAO             "
          f"{sum(1 for c in cegos if c['JANELA_PTBR'])}/{len(cegos)}")
    print(f"    PAGINACAO                estrutural, {POR_PAGINA} caracteres")
    print(f"    ESCOLHIDO_PELO_GATILHO   NAO")
    print("  O QUE A FILA CEGA NAO LEVA")
    payload = json.dumps(fila_cega, ensure_ascii=False)
    for chave in PROIBIDOS_NA_FILA_CEGA:
        if chave in payload:
            print(f"    ⚠️  {chave} APARECE NO PAYLOAD CEGO")
    print(f"    CHAVES_PROIBIDAS         0 de {len(PROIBIDOS_NA_FILA_CEGA)}")
    rotulos_no_cego = [k for k in ROTULOS if '"%s"' % k in payload]
    print(f"    ROTULOS_NO_PAYLOAD       {len(rotulos_no_cego)}")
    print("  SAIDA")
    print(f"    FINAL_LABEL_DECIDIDO     NAO (A != A2 fica UNRESOLVED)")
    print(f"    tamanho da pagina        {len(pagina.encode()) // 1024} KiB")

    if "--escrever" in sys.argv:
        escrever(PRESERVADO, envelope_de_a(a))
        escrever(CONTEXTO, ctx)
        alvo = os.path.join(RAIZ, HTML)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with open(alvo, "w", encoding="utf-8") as f:
            f.write(pagina)
        print(f"\n  escrito: {PRESERVADO}")
        print(f"  escrito: {CONTEXTO}")
        print(f"  escrito: {HTML}")
    else:
        print("\n  (nada escrito — passe --escrever)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
