#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JANELAS-68 · passo 3: fecho — por fonte, que ramo resolve (medido e revisto) e, se nenhum, a menor mudanca.

Sem rede. Junta JANELAS-68-FORMAS-V1, -CRUZAMENTO-V1 e -MEDICAO-V1 com a revisao humana dos itens que
o canario aprovou (titulo lido nos bytes guardados). Escreve JANELAS-68-RELATORIO-V1.json.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
C = RAIZ / "curadoria"
SAIDA = C / "JANELAS-68-RELATORIO-V1.json"

# Revisao humana (25/09) do item que o canario aprovou, pelo titulo nos bytes guardados.
REVISAO_DO_ITEM = {
    "IT-T3-041": ("FALSO", "pagina fixa «Produzioni qualita certificate», nao boletim"),
    "IT-T3-047": ("FALSO", "pagina de servico «Attivita produzione e commercio vegetali (AVIV)»"),
    "IT-T3-049": ("FALSO", "«Accessibilita e uso del sito»"),
    "IT-T3-052": ("FALSO", "pagina fixa «Attivita vivaistica»"),
    "IT-T3-060": ("REAL", "noticia «7o Forum Internazionale Gestione del Rischio in Agricoltura»"),
    "IT-T9-024": ("REAL", "artigo «Cambiamento climatico: come aiutare le piante...» (2026-05-15)"),
    "IT-T2-135": ("FALSO", "«Altri impianti di gestione rifiuti» — nao e agrometeo"),
    "IT-T2-157": ("REAL", "«Notizia | Agrometeo» (18/03/2026)"),
    "IT-T2-159": ("FALSO", "pagina fixa «Le attivita» do SIARL"),
}

PROPOSTA_POR_FORMA = {
    "PDF": "escrever o contrato PDF (OUTPUT_TYPE PDF + LISTAGEM) na rota PDF que a janela-formas-v1 ja liga; "
           "anexos allegato.aspx/ServeAttachment/documents/ contam como PDF; Google Drive (FEM) precisa de o host "
           "entrar na lista da rota",
    "PAGINA_BOLETIM": "a entrada registada e a pagina institucional; trocar CANONICAL_ENTRY_URL pela pagina que "
                      "tem o boletim datado (medida na P1g) e so entao usar PAGINA_E_BOLETIM da janela-formas-v1",
    "MENU": "trocar a entrada pela listagem de noticias/bollettini do mesmo site (menu nao tem familia de itens); "
            "sem isso nenhum molde acerta",
    "JS_API": "rota JSON/API nova (o estudo C-JS da t2-boletins-v1 ja achou a API publica do ER); o HTML vem vazio",
    "REPARADO_A_REVER": "revisao humana do item (trava R1): so aprovar onde o item e noticia/boletim",
    "LISTA_NOTICIA": "a lista existe mas o molde nao a acerta; ARSAC mudou para arsac.calabria.it (boletins 2026 "
                     "lidos pela janela-formas-v1) — trocar a entrada",
    "NAO_SEI": "FAMILIA_ESTATICA: so ha paginas fixas na entrada; trocar a entrada pela listagem de avvisi/bollettini",
}


def main():
    formas = {l["SOURCE_ID"]: l for l in json.loads((C / "JANELAS-68-FORMAS-V1.json").read_text(encoding="utf-8"))["FONTES"]}
    cruz = {l["SOURCE_ID"]: l for l in json.loads((C / "JANELAS-68-CRUZAMENTO-V1.json").read_text(encoding="utf-8"))["FONTES"]}
    med_doc = json.loads((C / "JANELAS-68-MEDICAO-V1.json").read_text(encoding="utf-8"))
    med = {l["SOURCE_ID"]: l for l in med_doc["FONTES"]}
    nao_medidas = set(med_doc["NAO_MEDIDAS_OUTRA_DO_MESMO_DOMINIO"])
    sem_contrato = set(med_doc["SEM_CONTRATO_NO_LIVRO_VIVO"])
    linhas = []
    for sid, f in formas.items():
        cz = cruz[sid]
        resolve, prova = None, None
        for v in cz["VEREDITOS"]:
            if v["RESULTADO"] == "PASS":
                resolve, prova = v["RAMO"], "%s (%s, medido pelo proprio ramo)" % (v["ROTA"], v["PORQUE"][:60])
        m = med.get(sid)
        estado = None
        if resolve:
            estado = "RESOLVE_" + resolve
        elif m and m.get("DESFECHO") == "PADRAO_NOVO" and (m.get("CANARIO") or {}).get("PASS"):
            rev, porque = REVISAO_DO_ITEM.get(sid, ("NAO_REVISTO", ""))
            estado = "RESOLVE_receitas-182-v1" if rev == "REAL" else "CANARIO_PASSA_MAS_ITEM_%s" % rev
            resolve = "receitas-182-v1" if rev == "REAL" else None
            prova = "reparo geral + canario medidos aqui (1 por dominio); item: %s" % porque
        elif m:
            estado = "NENHUM_RAMO"
            prova = "reparo geral medido aqui: %s %s" % (m.get("DESFECHO"), m.get("MOTIVO") or "")
        elif sid in nao_medidas:
            estado = "NAO_MEDIDA_OUTRA_DO_MESMO_DOMINIO"
        elif sid in sem_contrato:
            estado = "SEM_CONTRATO_NO_LIVRO_VIVO"
        else:
            estado = "NENHUM_RAMO"
            prova = "; ".join("%s %s %s" % (v["RAMO"], v["ROTA"], v["RESULTADO"]) for v in cz["VEREDITOS"])
        linhas.append({"SOURCE_ID": sid, "NOME": f["NOME"], "URL": f["URL"], "FORMA": f["FORMA"],
                       "PORQUE_DA_FORMA": f["PORQUE_DA_FORMA"], "FORMA_NA_RECEITAS_182": cz["FORMA_R182"],
                       "ESTADO": estado, "RESOLVE": resolve, "PROVA": prova,
                       "PROPOSTA": None if resolve else PROPOSTA_POR_FORMA.get(f["FORMA"])})
    por = Counter(l["ESTADO"] for l in linhas)
    out = {"DATASET": "JANELAS-68-RELATORIO-V1", "N": len(linhas),
           "RESOLVIDAS": {r: sum(1 for l in linhas if l["RESOLVE"] == r) for r in ("janela-formas-v1", "receitas-182-v1", "t2-boletins-v1")},
           "POR_ESTADO": dict(por.most_common()),
           "POR_FORMA": dict(Counter(l["FORMA"] for l in linhas).most_common()),
           "FALSOS_POSITIVOS_DO_REPARO_GERAL": [s for s, (r, _) in REVISAO_DO_ITEM.items() if r == "FALSO"],
           "MEDICAO": {k: med_doc[k] for k in ("EM", "CODIGO", "VIGIAS", "PEDIDOS_TOTAL", "MAX_POR_DOMINIO", "MEDIDAS")},
           "PROPOSTA_POR_FORMA": PROPOSTA_POR_FORMA, "FONTES": linhas}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("RESOLVIDAS", out["RESOLVIDAS"]); print("POR_ESTADO", out["POR_ESTADO"])
    print("SEM RAMO por forma:", dict(Counter(l["FORMA"] for l in linhas if not l["RESOLVE"]).most_common()))


if __name__ == "__main__":
    main()
