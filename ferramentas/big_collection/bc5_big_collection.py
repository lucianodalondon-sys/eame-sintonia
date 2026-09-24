# -*- coding: utf-8 -*-
"""BC5 passo B — a Big Collection da 1.a onda, UMA fonte de cada vez, pela porta canonica.

Corre com cwd = arvore do bot (source-curator-service-v1), com as 5 variaveis da Sala.
Disjuntores (BIG-COLLECTION-RUNBOOK §6):
  egresso sai de IT (antes/depois)   -> PARA TUDO
  alguma contagem da Sala DESCE       -> PARA TUDO (rollback R e do coordenador)
  corrida > 30 min                    -> PARA TUDO
  3 fontes seguidas FAILED            -> PARA TUDO
  C6 (bypass) != PASS                 -> PARA TUDO
  proveniencia: C4 com cadeia partida -> PARA TUDO
  pedidos por site > teto             -> PARA TUDO
  gate no instante != ELIGIBLE        -> a fonte nao corre (o proprio correr recusa)
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "scripts/micro_coleta")
import micro_coleta as M      # noqa: E402
import ensaio_offline as E    # noqa: E402

SAIDA = Path(r"C:\bc5\big")
SAIDA.mkdir(parents=True, exist_ok=True)
COORTE = [x["SOURCE_ID"] for x in json.load(open(r"C:\bc\COORTE-BIG-COLLECTION.json", encoding="utf-8"))["COORTE"]]
AVISO = Path(r"C:\Users\London1\auditoria-madrugada\bc4-aviso-vivo.txt")
LEDGER = Path("data/collection-ledger/italy/runs.ndjson")


def agora():
    return datetime.now().strftime("%H:%M:%S")


def foto():
    return {k: v["LINHAS"] for k, v in E.fotografia().items()}


def avisar(txt):
    with open(AVISO, "a", encoding="utf-8") as f:
        f.write("\nBC5 -> COORDENADOR (%s): %s\n" % (agora(), txt))


def cortesia_do_run(run_id):
    for l in reversed(LEDGER.read_text(encoding="utf-8").splitlines()):
        try:
            d = json.loads(l)
        except ValueError:
            continue
        if d.get("RUN_ID") == run_id:
            return d.get("CORTESIA") or {}, d.get("VPN_COUNTRY")
    return {}, None


def main():
    falta = M.precondicoes()
    if falta:
        print("PRECONDICOES", falta)
        return 2
    estado = {"INICIO": agora(), "SALA_INICIO": foto(), "FONTES": [], "PAROU": None}
    falhas_seguidas = 0
    for i, s in enumerate(COORTE, 1):
        antes = foto()
        t0 = time.time()
        r = M.correr([s], autorizado=True, saida=SAIDA / s)
        seg = round(time.time() - t0)
        depois = foto()
        c = (r.get("CORRIDAS") or [{}])[0]
        rel = r.get("RELATORIO") or {}
        C = rel.get("CRITERIOS") or {}
        cort, vpn = cortesia_do_run(c.get("RUN_ID")) if c.get("RUN_ID") else ({}, None)
        linha = {
            "N": i, "SOURCE_ID": s, "HORA": agora(), "SEGUNDOS": seg,
            "CORREU": c.get("CORREU"), "STATUS": c.get("STATUS"), "RUN_ID": c.get("RUN_ID"),
            "PORQUE_NAO_CORREU": c.get("PORQUE"),
            "GATE": c.get("GATE_NO_INSTANTE"),
            "EGRESSO": [(c.get("EGRESSO_ANTES") or {}).get("PAIS"), (c.get("EGRESSO_DEPOIS") or {}).get("PAIS")],
            "VPN_NO_COLETOR": vpn, "PEDIDOS_POR_SITE": cort.get("PEDIDOS_POR_HOST"),
            "TETO": cort.get("TETO_POR_HOST"),
            "ROBOTS": [x.get("ESTADO") for x in (cort.get("ROBOTS") or {}).values()],
            "RAW": (rel.get("CONTAGENS") or {}).get("RAW_CREATED"),
            "DERIVED": (C.get("C4_PROVENIENCIA_COMPLETA") or {}).get("COM_DERIVADO"),
            "ADMISSION": ((C.get("C7_PROPORCAO_POR_FONTE_E_CLASSE") or {}).get("POR_FONTE") or {}).get(s, {}),
            "SALA_ANTES": antes["sala_de_espera"], "SALA_DEPOIS": depois["sala_de_espera"],
            "C4": (C.get("C4_PROVENIENCIA_COMPLETA") or {}),
            "CRITERIOS": {k: (v.get("ESTADO") or ("PASS" if v.get("PASSA") else "FAIL")) for k, v in C.items()},
            "COLETOR": {k: ((rel.get("CONTAGENS") or {}).get("COLETOR") or {}).get(k) for k in
                        ("DETAIL_DOCUMENTS", "NETWORK_REQUESTS", "SKIPPED_KNOWN", "UNNECESSARY_REFETCHES", "SOURCES_FAILED")},
        }
        estado["FONTES"].append(linha)
        (SAIDA / "BIG-COLLECTION-ESTADO.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1, default=str),
                                                          encoding="utf-8")
        print("%02d %s %s %s %ss sala %s->%s adm %s pedidos %s" % (
            i, s, linha["STATUS"], linha["RUN_ID"], seg, antes["sala_de_espera"], depois["sala_de_espera"],
            linha["ADMISSION"], linha["PEDIDOS_POR_SITE"]), flush=True)

        # ── disjuntores ─────────────────────────────────────────────
        parar = None
        if c.get("CORREU") and linha["EGRESSO"] != ["IT", "IT"]:
            parar = "EGRESSO_SAIU_DE_IT %s" % linha["EGRESSO"]
        elif c.get("PORQUE") == "EGRESSO_NAO_IT":
            parar = "EGRESSO_NAO_IT antes da fonte"
        elif any(depois[k] < antes[k] for k in antes):
            parar = "SALA_DESCEU %s -> %s" % (antes, depois)
        elif seg > 1800:
            parar = "CORRIDA_MAIS_DE_30_MIN"
        elif C and C.get("C6_ZERO_BYPASS", {}).get("PASSA") is False:
            parar = "C6_BYPASS"
        elif C and linha["C4"].get("SALA_LINHAS") != linha["C4"].get("SALA_COM_CADEIA_INTEIRA"):
            parar = "PROVENIENCIA_PARTIDA %s" % linha["C4"]
        elif cort and any(v > (cort.get("TETO_POR_HOST") or 5) for v in (cort.get("PEDIDOS_POR_HOST") or {}).values()):
            parar = "PEDIDOS_ACIMA_DO_TETO %s" % cort.get("PEDIDOS_POR_HOST")
        falhas_seguidas = falhas_seguidas + 1 if linha["STATUS"] == "FAILED" else 0
        if falhas_seguidas >= 3:
            parar = "TRES_FONTES_SEGUIDAS_FAILED"
        if parar:
            estado["PAROU"] = {"FONTE": s, "PORQUE": parar, "HORA": agora()}
            (SAIDA / "BIG-COLLECTION-ESTADO.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1, default=str),
                                                              encoding="utf-8")
            avisar("DISJUNTOR na fonte %d (%s): %s. PARADO." % (i, s, parar))
            print("PAROU", parar, flush=True)
            return 1
        if i % 6 == 0:
            avisar("%d/18 fontes feitas; Sala %s -> %s; ultima %s %s." % (
                i, estado["SALA_INICIO"]["sala_de_espera"], depois["sala_de_espera"], s, linha["STATUS"]))
    estado["FIM"] = agora()
    estado["SALA_FIM"] = foto()
    (SAIDA / "BIG-COLLECTION-ESTADO.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1, default=str),
                                                      encoding="utf-8")
    print("FIM", estado["SALA_INICIO"], "->", estado["SALA_FIM"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
