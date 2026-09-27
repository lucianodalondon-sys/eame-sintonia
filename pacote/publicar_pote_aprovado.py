#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O POTE APROVADO VAI AO AR · a unica porta entre um pote da Intelligence e o portal publico.

    python3 pacote/publicar_pote_aprovado.py              # escreve o ficheiro publicado
    python3 pacote/publicar_pote_aprovado.py --conferir   # 0 = o ficheiro commitado e o destes insumos

    le     docs/casco/r7/POTE-R7.json        (POTE_INTELLIGENCE_CASCO/v2, gerador ce775ff5)
           docs/casco/r7/ANALISE-R7.json     (os 86 cruzamentos da MESMA corrida, com o estado)
           docs/casco/r7/MANIFESTO-R7.json   (o que o gerador disse que enviou)
    grava  italia-portale/client/sintonia-pote-publicado.js

PORQUE EXISTE
-------------
O pote de uma corrida vive fora do Git e fora do deploy (`sintonia-pote.js`,
tres trancas): e dado EXPERIMENTAL e ninguem o aprovou para o publico. A
decisao D114 do dono aprovou UM pote — o da rodada 7 — para ir ao ar:

    «portal vai ao ar hoje com o maximo de informacoes e cruzamoentos possiveis»

Isto nao abre as trancas. `sintonia-pote.js`, o gerador e as pastas
PARA-O-CASCO continuam fora. Abre-se uma porta com nome, para um pote com nome,
e o ficheiro que ela escreve diz de onde veio, quem o aprovou e o que nao
confere.

O QUE ESTE FICHEIRO NAO FAZ
---------------------------
Nao gera pote, nao refaz crossing, nao muda estado, nao completa NAO SEI, nao
escolhe o que e candidata: COPIA o pote e a analise tal como a Intelligence os
escreveu (INT-LAW-023 / INT-LAW-280) e recusa se eles se contradisserem. O
casco le; quem decide e a Intelligence.

O SHA DO MANIFESTO E O DOS BYTES CRLF — MEDIDO, NAO SUPOSTO
-----------------------------------------------------------
O MANIFESTO-R7 declara para o POTE-R7 o sha `2610af4b…`; o ficheiro no Git
da `01899678…`. A causa foi medida (missao ACERVO-ORGANIZADO, item 6): o
gerador escreveu o pote em Windows com fim de linha CRLF e fez o hash desses
bytes; o Git guardou-o com LF. Trocar cada LF por CRLF nos bytes do Git da
EXATAMENTE `2610af4b…` — nenhuma outra transformacao foi precisa.

A conferencia aceita, por isso, DUAS formas e so duas, e diz qual:

    IGUAL_BYTE_A_BYTE              sha(bytes) == sha do manifesto
    IGUAL_APOS_FIM_DE_LINHA_CRLF   o ficheiro nao tem CR nenhum, e
                                   sha(bytes com LF -> CRLF) == sha do manifesto

Qualquer outro byte mudado da DIFERENTE, e a tela di-lo. Nao e uma
normalizacao solta (nada de espacos, indentacao ou reserializar JSON): e a
unica troca que o proprio sistema de ficheiros do gerador faz. `.gitattributes`
fixa `docs/casco/** -text` para que um checkout em Windows nao volte a trocar
os bytes em disco.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = Path(os.path.dirname(HERE))

DECISAO = {
    "ID": "D114",
    "TEXTO": "portal vai ao ar hoje com o maximo de informacoes e cruzamoentos possiveis",
    "DATA": "2026-09-27",
    "DATA_BASE": "o dia da missao CASCO-AO-AR-R7 que a transmitiu; a decisao nao esta escrita noutro sitio do repositorio",
}
RODADA = "R7"
POTE = RAIZ / "docs/casco/r7/POTE-R7.json"
ANALISE = RAIZ / "docs/casco/r7/ANALISE-R7.json"
MANIFESTO = RAIZ / "docs/casco/r7/MANIFESTO-R7.json"
ORIGEM_DA_ANALISE = ("ramo nuvem-cruzamentos-max-v1 @ a09d383d, docs/intelligence/r7/ANALISE-R7.json "
                     "(blob 80001e9d), trazido so este ficheiro")
DESTINO = RAIZ / "italia-portale/client/sintonia-pote-publicado.js"

CONTRATO = "POTE_INTELLIGENCE_CASCO/v2"
MARCA = "EXPERIMENTAL · NAO_PARA_CLIENTE"
DOZE = ("meeting", "future", "windows", "market", "voices", "competitors", "science",
        "portfolio", "archive", "sources", "field", "casa")
ESTADOS_DO_CRUZAMENTO = ("POSSIBLE_ANSWER_YES_A_CONFIRMAR", "POSSIBLE_ANSWER_NO",
                         "PARTIAL_GRAO_INCOMPATIVEL", "NOT_POSSIBLE")


class Recusado(Exception):
    pass


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def conferir_sha_do_manifesto(bruto: bytes, declarado) -> dict:
    """As duas formas aceites, e so elas (ver o topo). Devolve o modo e os dois sha medidos."""
    lf = hashlib.sha256(bruto).hexdigest()
    crlf = None if b"\r" in bruto else hashlib.sha256(bruto.replace(b"\n", b"\r\n")).hexdigest()
    if declarado and lf == declarado:
        modo = "IGUAL_BYTE_A_BYTE"
    elif declarado and crlf is not None and crlf == declarado:
        modo = "IGUAL_APOS_FIM_DE_LINHA_CRLF"
    else:
        modo = "DIFERENTE"
    return {"MODO": modo, "SHA256_BYTES": lf, "SHA256_BYTES_EM_CRLF": crlf}


def _rel(p: Path) -> str:
    return p.relative_to(RAIZ).as_posix()


def conferir(pote: dict, analise: dict, manifesto: dict) -> list:
    """Contradicoes entre os tres insumos. Vazia = passa. Nao julga o conteudo: so a coerencia."""
    v = []
    if pote.get("SCHEMA") != CONTRATO:
        v.append(f"pote nao e {CONTRATO}")
    if pote.get("MARCA") != MARCA or pote.get("NAO_PARA_CLIENTE") is not True:
        v.append("pote sem a marca " + MARCA)
    if pote.get("CORRIDA_SINTETICA") is not False:
        v.append("pote sintetico (ou sem o dizer) nao vai ao ar")
    run = pote.get("INTELLIGENCE_RUN_ID")
    if not run or run == "NAO SEI":
        v.append("pote sem INTELLIGENCE_RUN_ID")
    if analise.get("INTELLIGENCE_RUN_ID") != run:
        v.append(f"a analise e de outra corrida ({analise.get('INTELLIGENCE_RUN_ID')} != {run})")
    if not str(manifesto.get("CHAVE", "")).startswith(str(run) + "@"):
        v.append("o manifesto e de outra corrida")
    comps = pote.get("COMPARTIMENTOS") or {}
    if set(comps) != set(DOZE):
        v.append("o pote nao traz os doze compartimentos")
    for k, e in comps.items():
        objs = e.get("OBJETOS") or []
        if not objs and (e.get("ESTADO") != "VAZIO" or not e.get("PORQUE_VAZIO")):
            v.append(f"{k}: vazio sem o porque")
        m = (manifesto.get("POR_COMPARTIMENTO") or {}).get(k)
        if m is None:
            v.append(f"{k}: o manifesto nao o conhece")
        elif m.get("OBJETOS") != len(objs) or m.get("RECUSADOS_AQUI") != e.get("RECUSADOS_AQUI"):
            v.append(f"{k}: o pote tem {len(objs)} objetos/{e.get('RECUSADOS_AQUI')} recusados, "
                     f"o manifesto diz {m.get('OBJETOS')}/{m.get('RECUSADOS_AQUI')}")
        for o in objs:
            for p in o.get("PROVA") or []:
                if p.get("INTELLIGENCE_RUN_ID") != run:
                    v.append(f"{k}/{o.get('OBJETO_ID')}: prova de outra corrida")
    cruz = analise.get("CROSSINGS") or []
    resumo = analise.get("CROSSINGS_RESUMO") or {}
    if len(cruz) != resumo.get("TOTAL"):
        v.append(f"a analise lista {len(cruz)} cruzamentos e o resumo diz {resumo.get('TOTAL')}")
    contagem = {}
    for c in cruz:
        est = c.get("ESTADO_R7")
        if est not in ESTADOS_DO_CRUZAMENTO:
            v.append(f"{c.get('OBJETO_ID')}: estado desconhecido {est!r}")
        contagem[est] = contagem.get(est, 0) + 1
        if c.get("INTELLIGENCE_RUN_ID") != run:
            v.append(f"{c.get('OBJETO_ID')}: cruzamento de outra corrida")
    if contagem != (resumo.get("POR_ESTADO") or {}):
        v.append(f"estados contados {contagem} != resumo {resumo.get('POR_ESTADO')}")
    ids = [c.get("OBJETO_ID") for c in cruz]
    if len(set(ids)) != len(ids):
        v.append("cruzamento repetido na analise")
    return v


def publicado() -> str:
    pote = json.loads(POTE.read_text(encoding="utf-8"))
    analise = json.loads(ANALISE.read_text(encoding="utf-8"))
    manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    falhas = conferir(pote, analise, manifesto)
    if falhas:
        raise Recusado("; ".join(falhas))
    sha_manifesto = (manifesto.get("SHA256") or {}).get("POTE-R7.json")
    conf = conferir_sha_do_manifesto(POTE.read_bytes(), sha_manifesto)
    sha_pote = conf["SHA256_BYTES"]
    meta = {
        "SCHEMA": "POTE_PUBLICADO/v1",
        "DECISAO": DECISAO,
        "RODADA": RODADA,
        "INTELLIGENCE_RUN_ID": pote["INTELLIGENCE_RUN_ID"],
        "CHAVE": manifesto.get("CHAVE"),
        "GERADOR_DO_POTE": manifesto.get("GERADOR"),
        "CONFERIR_POTE_DO_DONO": manifesto.get("CONFERIR_POTE_DO_DONO"),
        "CONFERIR_POTE_DO_DONO_DITO_POR": "MANIFESTO-R7.json",
        "POTE_FICHEIRO": _rel(POTE),
        "POTE_SHA256": sha_pote,
        "SHA256_DECLARADO_NO_MANIFESTO": sha_manifesto,
        "POTE_SHA256_EM_CRLF": conf["SHA256_BYTES_EM_CRLF"],
        "SHA256_CONFERENCIA": conf["MODO"],
        "SHA256_CONFERE_COM_O_MANIFESTO": conf["MODO"] != "DIFERENTE",
        "CONTAGENS_CONFEREM_COM_O_MANIFESTO": True,
        "ANALISE_FICHEIRO": _rel(ANALISE),
        "ANALISE_SHA256": _sha(ANALISE),
        "ANALISE_ORIGEM": ORIGEM_DA_ANALISE,
        "O_QUE_NAO_ATRAVESSA": "o gerador, a entrada do pote, as pastas PARA-O-CASCO e sintonia-pote.js continuam fora do Git e do deploy",
    }
    corpo = dict(meta, POTE=pote, ANALISE=analise)
    return ("/* GERADO por pacote/publicar_pote_aprovado.py — nao editar a mao.\n"
            f"   POTE APROVADO PARA O PUBLICO pela decisao {DECISAO['ID']} do dono ({DECISAO['DATA']}).\n"
            f"   Rodada {RODADA} · corrida {pote['INTELLIGENCE_RUN_ID']} · {CONTRATO} · o pote continua {MARCA}.\n"
            "   Com ?pote=local no endereco, o pote local da corrida (sintonia-pote.js) manda, e este cala-se. */\n"
            "window.SINTONIA_POTE_PUBLICADO = " + json.dumps(corpo, ensure_ascii=False, indent=1) + ";\n"
            "(function () {\n"
            "  var local = false;\n"
            "  try { local = /[?&]pote=local(?:&|$)/.test(window.location.search); } catch (e) { local = false; }\n"
            "  if (!local && !window.SINTONIA_POTE) window.SINTONIA_POTE = window.SINTONIA_POTE_PUBLICADO.POTE;\n"
            "})();\n")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        texto = publicado()
    except Recusado as e:
        print("RECUSADO: " + str(e))
        return 3
    if "--conferir" in argv:
        atual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if atual != texto:
            print(f"DIFERENTE: {_rel(DESTINO)} nao e o que estes insumos produzem — corra sem --conferir")
            return 1
        print(f"IGUAL: {_rel(DESTINO)} e o destes insumos")
        return 0
    DESTINO.write_text(texto, encoding="utf-8")
    print(f"PUBLICADO {_rel(DESTINO)} · {DECISAO['ID']} · rodada {RODADA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
