#!/usr/bin/env python3
"""REROUTE-T1T2 · replay OFFLINE da regua T5 C1 (D129/D130) sobre o que a Sala ja tem.

SO LE. Sem rede, sem banco, sem `adm.escrever()`, sem Sala. A chave `REGUA_T5_EXIGE_AGRO` NAO e
ligada: o replay chama `admissao.regua_t5_agro()` directamente, item a item.

Entrada (versionada pelo coordenador, so leitura):
  docs/lab-insumos/reroute-prova/SALA-T5-EXPORT.json    os 180 T5 da Sala (item_id, source_id, texto)
  docs/lab-insumos/reroute-prova/LAB-ROTULOS-V1.json    os rotulos do LAB para os 22 de 28/09
  docs/lab-insumos/reroute-prova/CONFRONTO-T5-MEDIDO.json  quais sao os 22 de 28/09

⚠️ O export NAO traz media_type nem retrato do detector. Por isso o replay mede TRES leituras e diz qual e
qual, em vez de adivinhar quem e pagina HTML:
  CORPO_ESTRITO        todo item lido como pagina HTML: o assunto agro so conta no `corpo()`; sem corpo
                       separavel -> NAO_SEI (e a porta, com a chave ligada, numa pagina HTML)
  CORPO_SENAO_INTEIRO  corpo quando separavel; senao o texto inteiro (NAO e o que a porta faz: mede o
                       que se ganharia consertando o extrator — REROUTE-T1T2.md §3)
  TEXTO_INTEIRO        o texto inteiro sempre (a leitura do LAB; e o que a porta faz num PDF)
Em todas as leituras as palavras T5 casam no INICIO de palavra (regra C1 · 1).

    py provas/reroute_t1t2/replay_t5_c1.py  -> provas/reroute_t1t2/REPLAY-T5-C1.json
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — as gavetas do processo no caminho

import admissao as adm  # noqa: E402

LAB = RAIZ / "docs" / "lab-insumos" / "reroute-prova"
SAIDA = Path(__file__).resolve().parent / "REPLAY-T5-C1.json"
FICA = adm.SIM


def _item(x: dict, html: bool) -> dict:
    it = {"id": x["item_id"], "texto": x["texto"], "source_id": x["source_id"]}
    if html:
        it["media_type"] = "text/html"
    return it


def julgar(x: dict) -> dict:
    palavras = adm.PERGUNTAS_DO_UNIVERSO["T5"]
    inteiro = _item(x, html=False)
    lingua = adm._lingua_do_item(inteiro)
    antes = adm._do_universo(inteiro, "T5", palavras, lingua=lingua)
    fora = {"ANTES_SUBSTRING": antes[0], "ANTES_PALAVRAS": antes[2].get("palavras")}
    for nome, it, modo in (("CORPO_ESTRITO", _item(x, True), "NAO_SEI"),
                           ("CORPO_SENAO_INTEIRO", _item(x, True), "TEXTO_INTEIRO"),
                           ("TEXTO_INTEIRO", inteiro, "NAO_SEI")):
        r, motivo, ev = adm.regua_t5_agro(it, palavras, lingua=lingua, sem_corpo=modo)
        fora[nome] = r
        fora[nome + "_MOTIVO"] = motivo.split(":")[0] if r != FICA else "SIM"
        if nome == "TEXTO_INTEIRO":
            fora["PALAVRAS_T5_INICIO"] = ev.get("palavras")
            fora["AGRO_NO_TEXTO_INTEIRO"] = ev.get("assunto_agro")
    fora["LINGUA"] = lingua
    fora["TITULO"] = " ".join(x["texto"].split())[:160]
    return fora


def reroute_t1(x: dict) -> dict:
    """O que o reroute T1 (cultura, D130) diria do item — lido como HTML e lido inteiro."""
    fora = {}
    for nome, it in (("COMO_HTML", _item(x, True)), ("TEXTO_INTEIRO", _item(x, False))):
        r, motivo, ev = adm.julgar_reroute(it, "T1")
        fora[nome] = {"RESULTADO": r, "MOTIVO": motivo[:300], "PALAVRAS": ev.get("palavras"),
                      "CULTURA": ev.get("cultura")}
    return fora


def main() -> int:
    sala = json.loads((LAB / "SALA-T5-EXPORT.json").read_text(encoding="utf-8"))
    rot = json.loads((LAB / "LAB-ROTULOS-V1.json").read_text(encoding="utf-8"))["SALA_HOJE"]
    hoje = [r[0] for r in json.loads((LAB / "CONFRONTO-T5-MEDIDO.json").read_text(encoding="utf-8"))]
    por_id = {x["item_id"]: x for x in sala}
    linhas = []
    for x in sala:
        j = julgar(x)
        j.update({"ITEM": x["item_id"], "SOURCE_ID": x["source_id"], "POUSADO_EM": x.get("pousado_em"),
                  "ADMITIDO_POR": x.get("admitido_por"), "DE_28_09": x["item_id"] in hoje})
        if x["item_id"] in rot:
            j["LAB_AGRO"] = rot[x["item_id"]]["AGRO"]
            j["LAB_GAVETA_T5"] = rot[x["item_id"]]["GAVETA_T5"]
        linhas.append(j)

    def resumo(sub, leitura):
        c = collections.Counter()
        for l in sub:
            c[("FICA" if l[leitura] == FICA else "SAI", l.get("LAB_AGRO", "SEM_ROTULO"))] += 1
        return {"%s·%s" % k: v for k, v in sorted(c.items())}

    def por_grupo(sub, leitura):
        g = collections.defaultdict(lambda: {"FICA": 0, "SAI": 0})
        for l in sub:
            chave = "EU-T5" if l["SOURCE_ID"].startswith("EU-") else l["SOURCE_ID"]
            g[chave]["FICA" if l[leitura] == FICA else "SAI"] += 1
        return dict(sorted(g.items()))

    leituras = ("CORPO_ESTRITO", "CORPO_SENAO_INTEIRO", "TEXTO_INTEIRO")
    de_hoje = [l for l in linhas if l["DE_28_09"]]
    fora_hoje = [l for l in linhas if not l["DE_28_09"]]
    out = {
        "REPLAY": "REPLAY-T5-C1", "REGUA": adm.VERSAO_DA_REGUA_T5, "CHAVE_NA_PORTA": adm.REGUA_T5_EXIGE_AGRO,
        "ENTRADA": "docs/lab-insumos/reroute-prova/SALA-T5-EXPORT.json (%d itens)" % len(sala),
        "LEITURAS": {"CORPO_ESTRITO": "a porta numa pagina HTML",
                     "CORPO_SENAO_INTEIRO": "se o extrator separasse o corpo (nao e a porta de hoje)",
                     "TEXTO_INTEIRO": "a porta num PDF; a leitura do LAB"},
        "HUMAN_REVIEW": "NOT_DONE (rotulos do LAB sao de modelo — D110)",
        "OS_22_DE_28_09": {k: {"POR_ROTULO_LAB": resumo(de_hoje, k), "POR_FONTE": por_grupo(de_hoje, k)}
                           for k in leituras},
        "OS_158_DE_ANTES": {k: {"FICA": sum(l[k] == FICA for l in fora_hoje),
                                "SAI": sum(l[k] != FICA for l in fora_hoje),
                                "POR_FONTE": por_grupo(fora_hoje, k)} for k in leituras},
        "CANARIO_1149": {"PEDIDO_T5": {k: next(l for l in linhas if l["ITEM"] == "derived:1149")[k]
                                       for k in ("ANTES_SUBSTRING", "ANTES_PALAVRAS", "PALAVRAS_T5_INICIO",
                                                 "AGRO_NO_TEXTO_INTEIRO") + leituras
                                       + tuple(x + "_MOTIVO" for x in leituras)},
                         "REROUTE_T1": reroute_t1(por_id["derived:1149"])},
        "ITENS": linhas,
    }
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("OS_22_DE_28_09", "OS_158_DE_ANTES", "CANARIO_1149")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
