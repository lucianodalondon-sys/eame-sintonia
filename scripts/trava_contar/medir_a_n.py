# -*- coding: utf-8 -*-
"""TRAVA-CONTAR · os 14 criterios A..N e as 5 condicoes de destrave, lidos do que os medidores publicam.

    py scripts/trava_contar/medir_a_n.py <saida.json>

Corre DEPOIS dos medidores, cada um no seu processo:
    py system-map/scripts/censo_dos_donos.py
    py system-map/scripts/censo_do_congelamento.py
    py system-map/scripts/censo_das_estradas_it.py
Este leitor NAO mede nada por conta propria: le os ficheiros gerados e o criterio A (calculado agora pelo dono,
`censo_das_estradas_it.criterio_a_no_curador`, com o livro de corridas que ITALY_OPS_ROOT disser), e diz de que
campo sai cada resposta. Nao corre nada da Intelligence. A trava nao e editada.
"""
import importlib.util
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DADOS = os.path.join(RAIZ, "system-map", "data")


def g(nome):
    with open(os.path.join(DADOS, nome + ".generated.json"), encoding="utf-8") as f:
        return json.load(f)


def main():
    spec = importlib.util.spec_from_file_location("cei_an", os.path.join(RAIZ, "system-map", "scripts", "censo_das_estradas_it.py"))
    E = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E)
    a = E.criterio_a_no_curador()
    don = {x["CONCEITO"]: x for x in g("donos")["DETALHE"]}
    est = g("estradas-it")
    con = g("congelamento")["CONTRA_A_FOTOGRAFIA"]
    st = g("state")["COUNTS"]

    def dono(c):
        x = don.get(c) or {}
        return x.get("ESTADO", "NAO SEI"), len(x.get("ESCREVEM") or [])

    rc = est["ROUTE_CLASSES"]
    estr_unknown = [r["ROUTE_CLASS_ID"] for r in rc if (r["STEPS"].get("STRUCTURED") or {}).get("STATE") == "UNKNOWN"]
    git = sum(x["LINHAS"] for x in est["GIT_COMO_BANCO_OPERACIONAL"])
    C = {}

    def poe(k, estado, prova, campo):
        C[k] = {"ESTADO": estado, "PROVA": prova, "CAMPO": campo}

    pr = a["POR_RESOLUCAO"]
    poe("A", "SIM" if a["CRITERIO_A"] == "SIM" else "NAO",
        "%d provadas · %d bloqueadas · %d NAO SEI de %d" % (pr.get("CLASSE_PROVADA", 0), pr.get("BLOQUEADA_COM_RAZAO", 0),
                                                           pr.get("NAO_SEI", 0), a["TOTAL"]),
        "censo_das_estradas_it.criterio_a_no_curador (livro de corridas: %s)" % a["CONFERENCIA_DOS_RESUMOS"]["LIVRO_DE_CORRIDAS"])
    poe("B", "SEM_MEDIDOR", "nenhum ficheiro gerado mede writers improvisados", "-")
    for k, conceito in (("C", "RAW_ASSET"), ("D", "RUN_MANIFEST"), ("E", "CHECKPOINT"), ("F", "DERIVED_ARTIFACT")):
        e, n = dono(conceito)
        poe(k, "SIM" if e == "UM_DONO" else "NAO", "%s = %s (%d escrevem)" % (conceito, e, n), "donos.DETALHE")
    poe("G", "NAO" if estr_unknown else "SIM", "etapa STRUCTURED em UNKNOWN em %s" % estr_unknown, "estradas-it.ROUTE_CLASSES[].STEPS.STRUCTURED")
    eh = [dono(c) for c in ("ROUTE_MODEL", "ORQUESTRADOR")]
    poe("H", "SIM" if all(e == "UM_DONO" for e, _ in eh) else "NAO",
        "ROUTE_MODEL %s (%d) · ORQUESTRADOR %s (%d)" % (eh[0][0], eh[0][1], eh[1][0], eh[1][1]), "donos.DETALHE")
    poe("I", "SIM" if est["APIFY"]["DEFAULT"] == 0 else "NAO", "APIFY DEFAULT=%s FALLBACK=%s" % (est["APIFY"]["DEFAULT"], est["APIFY"]["FALLBACK"]), "estradas-it.APIFY")
    poe("J", "NAO" if git else "SIM", "%d linhas de ndjson operacional no Git %s" % (git, [(x["FICHEIRO"], x["LINHAS"]) for x in est["GIT_COMO_BANCO_OPERACIONAL"]]), "estradas-it.GIT_COMO_BANCO_OPERACIONAL")
    poe("K", "SEM_MEDIDOR", "nenhum dono mede retry", "-")
    poe("L", "SIM" if est["ROUTE_CLASSES_REQUIRED_TOTAL"] == "UNKNOWN" and pr.get("NAO_SEI", 0) >= 0 else "NAO",
        "REQUIRED_TOTAL=%s mantido; o criterio A publica %d NAO SEI em vez de palpite" % (est["ROUTE_CLASSES_REQUIRED_TOTAL"], pr.get("NAO_SEI", 0)),
        "estradas-it.ROUTE_CLASSES_REQUIRED_TOTAL + CRITERIO_A_NO_CURADOR")
    poe("M", "NAO" if st["components_pending"] else "SIM", "%d de %d componentes pendentes" % (st["components_pending"], st["components"]),
        "state.generated.COUNTS (ultimo gerado nesta arvore; a cadeia do mapa nao foi corrida)")
    poe("N", "SIM" if con["CONGELAMENTO_RESPEITADO"] else "NAO", "mudaram %d · sumiram %d · novos %d" % (con["MUDARAM"] if isinstance(con["MUDARAM"], int) else len(con["MUDARAM"]),
        con["SUMIRAM"] if isinstance(con["SUMIRAM"], int) else len(con["SUMIRAM"]), con["NOVOS"] if isinstance(con["NOVOS"], int) else len(con["NOVOS"])),
        "congelamento.CONTRA_A_FOTOGRAFIA")
    tot = {s: sorted(k for k, v in C.items() if v["ESTADO"] == s) for s in ("SIM", "NAO", "SEM_MEDIDOR")}

    abertas = [r["ROUTE_CLASS_ID"] for r in rc if not r["ARCHITECTURE_CLOSED"] and r["OBSERVATION_STATE"] not in ("BLOCKED", "DEBT")]
    nao_obs = [r["ROUTE_CLASS_ID"] for r in rc if r["OBSERVATION_STATE"] == "NOT_OBSERVED"]
    blq_sem = est["VEREDITOS"].get("M1_BLOCKED_SEM_DECISAO_ESCRITA")
    cond = [
        {"N": 1, "CONDICAO": "os 14 criterios A..N cumpridos", "ESTADO": "SIM" if len(tot["SIM"]) == 14 else "NAO",
         "PROVA": "%d de 14" % len(tot["SIM"])},
        {"N": 2, "CONDICAO": "nenhuma classe NECESSARIA em UNKNOWN", "ESTADO": "NAO",
         "PROVA": "o conjunto das necessarias e %s; %d classes nem observadas: %s" % (est["ROUTE_CLASSES_REQUIRED_TOTAL"], len(nao_obs), nao_obs)},
        {"N": 3, "CONDICAO": "nenhuma classe NECESSARIA em OPEN", "ESTADO": "NAO" if abertas else "SIM",
         "PROVA": "%d classes abertas (ARCHITECTURE_CLOSED=false, nem bloqueadas nem divida): %s" % (len(abertas), abertas)},
        {"N": 4, "CONDICAO": "nenhuma NECESSARIA em BLOCKED sem decisao escrita", "ESTADO": "SIM" if blq_sem == [] else "NAO",
         "PROVA": "BLOCKED %s, cada uma com motivo escrito; M1_BLOCKED_SEM_DECISAO_ESCRITA=%s — mas o conjunto das necessarias e desconhecido"
                  % (est["ROUTE_CLASSES_BLOCKED"], blq_sem)},
        {"N": 5, "CONDICAO": "ROUTE_CLASSES_TOTAIS_NECESSARIAS deixou de ser NAO SEI", "ESTADO": "NAO" if est["ROUTE_CLASSES_REQUIRED_TOTAL"] in ("UNKNOWN", "NAO SEI") else "SIM",
         "PROVA": "REQUIRED_TOTAL=%s" % est["ROUTE_CLASSES_REQUIRED_TOTAL"]},
    ]
    out = {"DATASET": "TRAVA-A-N-V1", "COLLECTION_FOUNDATION_CLOSED": est["COLLECTION_FOUNDATION_CLOSED"],
           "CRITERIOS": C, "TOTAIS": {k: len(v) for k, v in tot.items()}, "QUAIS": tot,
           "CONDICOES": cond, "CONDICOES_CUMPRIDAS": sum(1 for c in cond if c["ESTADO"] == "SIM"),
           "CRITERIO_A_CONFERENCIA": a["CONFERENCIA_DOS_RESUMOS"]}
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    for k, v in C.items():
        print(k, v["ESTADO"].ljust(11), v["PROVA"][:110])
    print("TOTAIS", out["TOTAIS"], "· condicoes", out["CONDICOES_CUMPRIDAS"], "de 5 · FOUNDATION_CLOSED", out["COLLECTION_FOUNDATION_CLOSED"])


if __name__ == "__main__":
    main()
