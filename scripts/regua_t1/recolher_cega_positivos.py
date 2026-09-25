#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1B · PROVA CEGA DE POSITIVOS — boletins NOVOS pela rede (regra commitada ANTES da corrida).

    py scripts/regua_t1/recolher_cega_positivos.py

REGRA (fixa, escrita antes de qualquer pedido):
  * so PDFs pelas ROUTE_TEMPLATE dos contratos da casa (`regras/italy_contracts.mjs`), nas
    EDICOES/ZONAS que NAO estao no acervo nem nos gabaritos T1/T2 (lista abaixo, com a razao);
  * por anfitriao: robots.txt (1) + ate 4 PDFs = no maximo 5 visitas; 2 s de pausa;
  * egresso pelo DONO (`superficie/rede.py::portao_de_egresso`, consenso) antes de CADA site;
    se nao for PASS, PARA tudo e nada se pede;
  * `%PDF` obrigatorio; 404 = edicao inexistente, contado;
  * bytes fora do Git (%USERPROFILE%/sintonia-gabarito/REGUA-T1-V1/cega-positivos/), sha256 no
    manifesto `scripts/regua_t1/RECOLHA-CEGA-POSITIVOS-V1.json`; o texto NAO passa pela regua
    aqui — rotula-se antes, noutro passo.
⚠️ Sao edicoes NOVAS das MESMAS series do gabarito (mesmos moldes): a prova mede o que a regua
faz com texto que nunca viu, nao com um tipo de documento que nunca viu. Dito assim.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ), str(RAIZ / "curadoria")]
import _gavetas  # noqa: E402,F401
import canario as CAN  # noqa: E402
import gate_de_rota as GATE  # noqa: E402

_sp = importlib.util.spec_from_file_location("rede", RAIZ / "superficie" / "rede.py")
REDE = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(REDE)
_sp = importlib.util.spec_from_file_location("inv", RAIZ / "scripts" / "regua_t2" / "inventariar_t2.py")
INV = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(INV)

PASTA = Path.home() / "sintonia-gabarito" / "REGUA-T1-V1" / "cega-positivos"
SAIDA = AQUI / "RECOLHA-CEGA-POSITIVOS-V1.json"
PAUSA_S = 2.0
_CAMP = "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/pdf/%s.pdf"
_ARIF = ("https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/2026/"
         "Notiziario_Agrometeorologico_N%s_%s.pdf")
_APOL = "http://www.apol.it/documenti/notizie/Bollettino_Mosca_dellOlivo_n_%s_del_%s_2026.pdf"
_ARPAV = "https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_%s.pdf"
_ARPAE = ("https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/"
          "bollettini-agrometeo/bollettini-2026/%s_boll_agro_%s.pdf")
SERIES = [
    ("IT-T3-002", "Campania · SFR por provincia (edicoes 16/09 e 23/09 que faltam)",
     [_CAMP % x for x in ("AV-23-09", "NA-23-09", "CE-16-09", "BN-16-09")]),
    ("IT-T3-008", "Puglia · notiziario ARIF (edicoes de agosto: N32 e N33 nao estao; N31, N34)",
     [_ARIF % ("31", "29-07-2026"), _ARIF % ("32", "05-08-2026"), _ARIF % ("33", "12-08-2026"),
      _ARIF % ("34", "19-08-2026")]),
    ("IT-T3-010", "Puglia · APOL mosca da oliveira (n. 5 a 8; o acervo tem 9, 10, 11)",
     [_APOL % ("8", "31_08"), _APOL % ("7", "24_08"), _APOL % ("6", "17_08"), _APOL % ("5", "10_08")]),
    ("IT-T2-002", "ARPAV · Agrometeo Informa (zonas 02, 03, 04, 06 que nao estao)",
     [_ARPAV % z for z in ("02", "03", "04", "06")]),
    ("IT-T2-001", "ARPAE · boletim agrometeorologico (N30 a N33 que nao estao)",
     [_ARPAE % ("33", "20260817"), _ARPAE % ("32", "20260810"), _ARPAE % ("31", "20260803"),
      _ARPAE % ("30", "20260727")]),
]


def main() -> int:
    PASTA.mkdir(parents=True, exist_ok=True)
    sites, itens = [], []
    for sid, nome, urls in SERIES:
        eg = REDE.portao_de_egresso("IT")
        reg = {"SOURCE_ID": sid, "SERIE": nome, "PEDIDOS": 0,
               "EGRESSO": {"GATE": eg["EGRESS_GATE"], "VOTOS": [(v["VERIFICADOR"], v["PAIS"]) for v in eg["VOTOS"]]}}
        sites.append(reg)
        if eg["EGRESS_GATE"] != "PASS":
            reg["PARADO"] = "EGRESSO NAO PASS — recolha interrompida"
            print("PARAGEM egresso", reg["EGRESSO"], flush=True)
            break
        rp, txt = GATE.robots_de(urlparse(urls[0]).hostname)
        reg["PEDIDOS"] += 1
        if "inacessivel" in txt:
            reg["PARADO"] = "robots: " + txt[:100]
            continue
        for u in urls[:4]:
            if not GATE.permitido(u, rp):
                reg.setdefault("RECUSAS", []).append("robots proibe " + u)
                continue
            time.sleep(PAUSA_S)
            st, c, err = CAN.buscar(u)
            reg["PEDIDOS"] += 1
            if st != 200 or c[:5] != b"%PDF-":
                reg.setdefault("RECUSAS", []).append("HTTP %s %s %s" % (st, "sem %PDF" if st == 200 else err, u))
                print("%-10s %s %s" % (sid, st, u[-55:]), flush=True)
                continue
            sha = hashlib.sha256(c).hexdigest()
            f = PASTA / (sha[:16] + ".pdf")
            f.write_bytes(c)
            norm = INV.normalizar(INV.extrair(c)[0])
            (PASTA / (sha[:16] + ".txt")).write_text(norm, encoding="utf-8")
            itens.append({"SOURCE_ID": sid, "SERIE": nome, "URL": u, "BYTES": len(c), "SHA256": sha,
                          "FICHEIRO_FORA_DO_GIT": str(f), "TEXTO_FORA_DO_GIT": str(PASTA / (sha[:16] + ".txt")),
                          "TEXTO_SHA256": hashlib.sha256(norm.encode("utf-8")).hexdigest(),
                          "NON_WHITESPACE_CHARACTERS": len(norm.replace(" ", "")),
                          "OBTIDO_EM": datetime.now(timezone.utc).isoformat()})
            print("%-10s PDF %d B %s" % (sid, len(c), u[-55:]), flush=True)
        time.sleep(PAUSA_S)
    out = {"DATASET": "RECOLHA-CEGA-POSITIVOS-V1", "REGRA": "ver docstring (commitada antes da corrida)",
           "BYTES_EM": str(PASTA), "SITES": sites, "ITENS": itens,
           "CONTAGEM": {"ITENS": len(itens), "PEDIDOS": sum(s["PEDIDOS"] for s in sites),
                        "MAX_PEDIDOS_POR_SITE": max((s["PEDIDOS"] for s in sites), default=0)}}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8", newline=chr(10))
    print(json.dumps(out["CONTAGEM"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
