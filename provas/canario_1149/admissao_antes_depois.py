#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O EFEITO DA DERIVAÇÃO NOVA NA ADMISSÃO — o que a v1/v2 declarou «não medi» (D131/D132).

Para cada página HTML guardada no armazém, a porta julga DUAS vezes o mesmo par (página, universo):

    ANTES   o texto da `limpar()` do vivo (limpar/1, achatada — cópia literal conferida contra o
            git em `provas/derivacao_estrutura/replay_acervo.py`, que é quem a guarda)
    DEPOIS  o texto da `limpar()` desta árvore (limpar/3)

com `admissao._do_universo(item, universo, PERGUNTAS_DO_UNIVERSO[universo])` — a mesma chamada de
`admissao.decidir` — no UNIVERSO DO CONTRATO DA FONTE (`TERRITORY` em
`curadoria/italy_contracts_curator.json`; é o universo que a coleta contínua pede para a fonte, ver
`scripts/micro_coleta/micro_coleta.universo_de`). Lista as decisões que MUDAM (SIM -> outra e
outra -> SIM), com as palavras de cada lado.

    py provas/canario_1149/admissao_antes_depois.py --armazem <pasta> --saida <pasta> [--livros "<glob;glob>"]

A FONTE DE CADA PÁGINA: do livro do coletor (`RAW_SHA256 -> SOURCE_ID`, pelo dono
`admissao/reprocessar_tempo_lugar.livros_por_sha`) quando `--livros` é dado; senão, da pasta do
armazém (a primeira das 4 pastas acima da página cujo nome é um contrato: `…/<source-id>/OBSERVATION/`
no armazém, `…/<SOURCE-ID>/<documento>/<versao>/` na árvore) — a base de cada
uma fica escrita. Página sem fonte ou sem contrato NÃO é julgada: sai em `NAO_JULGADAS` com o porquê.

⚠️ ISTO NÃO É A DECISÃO INTEIRA DA PORTA. `decidir` pergunta antes a legibilidade, a origem, a
linhagem e a matéria; aqui mede-se só a pergunta que o texto novo pode mudar — a pertença ao
universo. É isso que o nome da medida diz.

SÓ LEITURA. SEM REDE (a armadilha do socket é a do replay, herdada ao importá-lo). Nada escrito fora
de `--saida`.
"""
import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import collections  # noqa: E402
import datetime  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for g in (RAIZ, os.path.join(RAIZ, "provas", "derivacao_estrutura")):
    if g not in sys.path:
        sys.path.insert(0, g)

import replay_acervo as RA  # noqa: E402 — a copia literal do «antes» e a armadilha da rede
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
from coleta.texto_fonte import REGUA, limpar as limpar_depois  # noqa: E402

CONTRATOS = os.path.join(RAIZ, "curadoria", "italy_contracts_curator.json")
NAO_SEI = "NAO SEI"


def universos_dos_contratos(caminho=CONTRATOS):
    """`{SOURCE_ID: TERRITORY}` do registo de contratos. Só leitura."""
    with open(caminho, encoding="utf-8") as fh:
        fontes = json.load(fh).get("FONTES") or []
    return {f["SOURCE_ID"]: f.get("TERRITORY") or NAO_SEI for f in fontes if f.get("SOURCE_ID")}


def fonte_da_pagina(caminho, dados, livros, contratos):
    """(SOURCE_ID, BASE) — do livro, senão da pasta que for contrato; senão (None, porque)."""
    if livros:
        obs = livros.get(hashlib.sha256(dados).hexdigest())
        if obs and obs.get("SOURCE_ID"):
            return obs["SOURCE_ID"], "LIVRO_DO_COLETOR (RAW_SHA256)"
    # o armazem operacional guarda em `…/<source-id>/OBSERVATION/`; a arvore em
    # `…/<SOURCE-ID>/<documento>/<versao>/`: sobe-se ate a primeira pasta que E um contrato
    por_nome = {s.lower(): s for s in contratos}
    pastas = os.path.normpath(os.path.dirname(caminho)).split(os.sep)
    for pasta in reversed(pastas[-4:]):
        if pasta.lower() in por_nome:
            return por_nome[pasta.lower()], "PASTA_DO_ARMAZEM (%s)" % pasta
    return None, "nem o livro nem as pastas (%s) nomeiam um contrato" % "/".join(pastas[-4:])


def julgar(texto, universo):
    r, motivo, ev = adm._do_universo({"texto": texto}, universo,
                                     adm.PERGUNTAS_DO_UNIVERSO.get(universo, []))
    return {"RESULTADO": r, "PALAVRAS": (ev or {}).get("palavras", []), "MOTIVO": motivo}


def medir(armazem, livros=None, qualquer_html=False):
    contratos = universos_dos_contratos()
    por_pagina, nao_julgadas = [], []
    transicoes = collections.Counter()
    for caminho in RA.paginas(armazem, qualquer_html):
        with open(caminho, "rb") as fh:
            dados = fh.read()
        sid, base = fonte_da_pagina(caminho, dados, livros, contratos)
        u = contratos.get(sid) if sid else None
        rel = os.path.relpath(caminho, armazem)
        if not u or u == NAO_SEI:
            nao_julgadas.append({"PAGINA": rel, "SOURCE_ID": sid,
                                 "PORQUE": base if not sid else "o contrato nao declara TERRITORY"})
            continue
        antes = julgar(RA.limpar_antes(dados, "text/html"), u)
        depois = julgar(limpar_depois(dados, "text/html"), u)
        transicoes["%s -> %s" % (antes["RESULTADO"], depois["RESULTADO"])] += 1
        por_pagina.append({"PAGINA": rel, "SOURCE_ID": sid, "SOURCE_ID_BASE": base, "UNIVERSO": u,
                           "ANTES": antes, "DEPOIS": depois,
                           "MUDOU": antes["RESULTADO"] != depois["RESULTADO"],
                           "PALAVRAS_MUDARAM": antes["PALAVRAS"] != depois["PALAVRAS"]})
    sim = adm.SIM
    saem = [p for p in por_pagina if p["ANTES"]["RESULTADO"] == sim and p["DEPOIS"]["RESULTADO"] != sim]
    entram = [p for p in por_pagina if p["ANTES"]["RESULTADO"] != sim and p["DEPOIS"]["RESULTADO"] == sim]
    resumo = {
        "QUANDO": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ARMAZEM": os.path.abspath(armazem),
        "ANTES": "limpar/1 — copia literal em provas/derivacao_estrutura/replay_acervo.py @ %s "
                 "(COPIA_LITERAL_CONFERIDA=%s)" % (RA.BASE[:9], RA.conferir_copia()),
        "DEPOIS": REGUA,
        "PERGUNTA": "admissao._do_universo (so a pertenca ao universo; versao da regua %s)"
                    % adm.VERSAO_DA_REGRA,
        "UNIVERSO": "TERRITORY do contrato (%s)" % os.path.relpath(CONTRATOS, RAIZ),
        "PAGINAS": len(por_pagina) + len(nao_julgadas),
        "JULGADAS": len(por_pagina), "NAO_JULGADAS": len(nao_julgadas),
        "TRANSICOES": dict(sorted(transicoes.items())),
        "MUDARAM": sum(1 for p in por_pagina if p["MUDOU"]),
        "SIM_PARA_OUTRA": len(saem), "OUTRA_PARA_SIM": len(entram),
        "SO_AS_PALAVRAS_MUDARAM": sum(1 for p in por_pagina
                                      if p["PALAVRAS_MUDARAM"] and not p["MUDOU"]),
    }

    def curto(p):
        return {"PAGINA": p["PAGINA"], "SOURCE_ID": p["SOURCE_ID"], "UNIVERSO": p["UNIVERSO"],
                "ANTES": "%s %s" % (p["ANTES"]["RESULTADO"], p["ANTES"]["PALAVRAS"]),
                "DEPOIS": "%s %s" % (p["DEPOIS"]["RESULTADO"], p["DEPOIS"]["PALAVRAS"]),
                "MOTIVO_DEPOIS": p["DEPOIS"]["MOTIVO"][:200]}
    return {"RESUMO": resumo, "SIM_PARA_OUTRA": [curto(p) for p in saem],
            "OUTRA_PARA_SIM": [curto(p) for p in entram], "NAO_JULGADAS": nao_julgadas,
            "POR_PAGINA": por_pagina}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--armazem", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--livros", help="globs dos observations.ndjson do coletor, separados por ;")
    ap.add_argument("--qualquer-html", action="store_true",
                    help="toda pagina .html, e nao so as de pastas OBSERVATION")
    a = ap.parse_args(argv)
    livros = None
    if a.livros:
        import reprocessar_tempo_lugar as rtl                   # noqa: PLC0415
        livros = rtl.livros_por_sha([p for p in a.livros.split(";") if p])
    fora = medir(a.armazem, livros, a.qualquer_html)
    os.makedirs(a.saida, exist_ok=True)
    nome = os.path.join(a.saida, "ADMISSAO-ANTES-DEPOIS.json")
    with open(nome, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: fora[k] for k in ("RESUMO", "SIM_PARA_OUTRA", "OUTRA_PARA_SIM")},
                     ensure_ascii=False, indent=1))
    print("recibo inteiro: %s" % nome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
