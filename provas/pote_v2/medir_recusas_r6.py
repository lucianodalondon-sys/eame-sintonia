#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P7 medido: quantas das 46 recusas do POTE-R6 voltam, numa corrida SINTETICA equivalente.

    python3 provas/pote_v2/medir_recusas_r6.py --escrever      # (re)gera a fixture, deterministica
    python3 provas/pote_v2/medir_recusas_r6.py [--base <ref>]  # corre o gerador da base e o desta arvore

⚠️ DADO SINTETICO DECLARADO. O POTE-R6 real vive na maquina do coordenador e NAO esta no repositorio;
dele so ha as CHAVES e as CONTAGENS (docs/intelligence/pote-v2/FORMATOS-MEDIDOS.md: entrada com archive 23,
windows 2, science 2, market 6, future 10, portfolio 3, sources 47; saida com 46 RECUSADOS). A fixture
repete essas contagens e o que o relatorio de 27/09 disse das recusas (o cruzamento «nao» da APOL recusado;
o Registro delle fonti com 3 de 47 fontes). O MOTIVO de cada recusa real e NAO SEI: as chaves nao o
trazem. A 46.a recusa real (a que nao e fonte nem APOL) e NAO SEI; aqui ela e um SINAL de arquivo com o
tempo por ancorar — um CONTROLO, que tem de continuar recusado depois do conserto.

Escreve tests/fixtures/pote/CORRIDA-SINTETICA-R6-EQUIVALENTE.json (com --escrever) e imprime a medida.
"""
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FIXTURE = RAIZ / "tests" / "fixtures" / "pote" / "CORRIDA-SINTETICA-R6-EQUIVALENTE.json"
BASE_PADRAO = "f357712"   # lote 4 final + merge da ponte (antes do POTE-V2-UNICO)
C = "EXPERIMENTAL_CANDIDATE"


def _item(n, fonte, g0="PASSOU", falta=()):
    lin = {"ITEM_ID": f"SINT-R6-IT-{n:04d}", "CORRIDA_UPSTREAM": "SINT-R6-UP", "RAW_OBSERVATION_ID": f"SINT-R6-RAW-{n:04d}",
           "SOURCE_ID": fonte, "G0": g0, "G0_FALTA": list(falta)}
    prova = {k: lin[k] for k in ("ITEM_ID", "CORRIDA_UPSTREAM", "RAW_OBSERVATION_ID", "SOURCE_ID")}
    prova.update(DOCUMENT_ID=f"SINT-R6-DOC-{n:04d}", URL=f"https://sint.example/r6/{n:04d}", PUBLISHED_AT="2026-09-10")
    return lin, prova


def fixture() -> dict:
    linhagem, itens, n = [], {}, 0

    def novo(fonte, g0="PASSOU", falta=()):
        nonlocal n
        n += 1
        lin, prova = _item(n, fonte, g0, falta)
        linhagem.append(lin)
        return prova

    tempo = ("FACT_TIME:SEM_BASE",)
    obj = lambda oid, esp, provas, **kw: dict({"OBJETO_ID": oid, "ESPECIE": esp, "ESTADO": C, "CHAVES": {},  # noqa: E731
                                               "PROVA": provas}, **kw)
    itens["archive"] = [obj(f"SINT-R6-ARQ-{i:02d}", "SINAL", [novo("SINT-R6-SRC-00")]) for i in range(22)]
    # CONTROLO: um sinal com o tempo por ancorar. Sinal EXIGE tempo; continua recusado.
    itens["archive"].append(obj("SINT-R6-ARQ-TEMPO", "SINAL", [novo("SINT-R6-SRC-00", "BLOQUEADO_EM_G0", tempo)]))
    itens["windows"] = [obj(f"SINT-R6-WIN-{i}", "SINAL", [novo("SINT-R6-SRC-00")]) for i in range(2)]
    itens["science"] = [obj(f"SINT-R6-SCI-{i}", "SINAL", [novo("SINT-R6-SRC-00")]) for i in range(2)]
    # P8: seis precos soltos (um ponto cada), como os 6 do Polso da R6.
    itens["market"] = [obj(f"SINT-R6-MK-{i}", "SINAL", [novo("SINT-R6-SRC-00")],
                           CHAVES={"PERIOD": "2026-W37", "PRICE": f"SINT-{200 + i}", "UNIT": "EUR/t"}) for i in range(6)]
    itens["future"] = [obj(f"SINT-R6-FUT-{i}", "FATO_PRESENTE_SOBRE_O_FUTURO",
                           [novo("SINT-R6-SRC-00", "BLOQUEADO_EM_G0", ("FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA",))])
                       for i in range(10)]
    itens["portfolio"] = [obj(f"SINT-R6-CR-{i}", "CROSSING", [novo("SINT-R6-SRC-00")],
                              CHAVES={"PRODUCT_ID": f"SINT-R6-PROD-{i}", "CROSSING_STATE": "CASA"}) for i in range(2)]
    # o cruzamento «nao» (o da APOL, na R6): resultado honesto sobre um item sem tempo ancorado
    itens["portfolio"].append(obj("SINT-R6-CR-NAO", "CROSSING", [novo("SINT-R6-SRC-00", "BLOQUEADO_EM_G0", tempo)],
                                  CHAVES={"PRODUCT_ID": "SINT-R6-PROD-APOL", "CROSSING_STATE": "NAO"}))
    itens["sources"] = []
    for f in range(47):
        fonte = f"SINT-R6-SRC-{f + 1:02d}"
        # 3 fontes com os itens todos ancorados; 44 com pelo menos um item sem tempo ancorado
        provas = [novo(fonte), novo(fonte)] + ([novo(fonte)] if f < 3 else [novo(fonte, "BLOQUEADO_EM_G0", tempo)])
        itens["sources"].append(obj(f"SINT-R6-REND-{f + 1:02d}", "RENDIMENTO_DE_FONTE", provas,
                                    CHAVES={"SOURCE_ID": fonte, "ITENS_LIDOS": 3,
                                            "ITENS_QUE_PASSARAM_G0": 3 if f < 3 else 2, "OBJETOS_PRODUZIDOS": 0}))
    return {
        "_AVISO": "DADO SINTETICO DECLARADO — equivalente, em CONTAGENS, a entrada do POTE-R6 (27/09), gerado por "
                  "provas/pote_v2/medir_recusas_r6.py. Todo id comeca por SINT-, SINTETICA = true; nenhum valor e real. "
                  "O motivo real de cada recusa da R6 e NAO SEI (so as chaves foram medidas).",
        "SCHEMA": "CORRIDA_DA_INTELLIGENCE/v2-SINTETICA", "SINTETICA": True,
        "INTELLIGENCE_RUN_ID": "SINT-IR-R6-EQUIVALENTE", "SOURCE_HEAD": "SINT-R6-HEAD", "CORTE": "2026-09-27T00:00:00+00:00",
        "RESULT_STATE": "DONE", "LINEAGE": linhagem, "SIGNALS": [], "REQUIREMENTS": [], "GAPS": [],
        "ITENS_POR_FERRAMENTA": itens,
    }


def _gerador_da_base(ref: str, pasta: Path):
    """O gerador (e a ponte que ele chama) como estavam em `ref`, importados de uma pasta a parte. O resto
    (a espinha, as leis) vem desta arvore: o POTE-V2-UNICO nao lhe toca."""
    for rel in ("pacote/pote_intelligence_casco.py", "pacote/ponte_intelligence_casco.py"):
        (pasta / rel).parent.mkdir(parents=True, exist_ok=True)
        (pasta / rel).write_bytes(subprocess.run(["git", "-C", str(RAIZ), "show", f"{ref}:{rel}"],
                                                 capture_output=True, check=True).stdout)
    return pasta


def _correr(pasta: Path, corrida: dict) -> dict:
    guardado = dict(sys.modules)
    if str(RAIZ) not in sys.path:
        sys.path.insert(0, str(RAIZ))
    importlib.import_module("_gavetas")   # as gavetas DESTA arvore (espinha, leis) no caminho
    sys.path[:0] = [str(pasta), str(pasta / "pacote")]
    try:
        for m in ("pote_intelligence_casco", "ponte_intelligence_casco"):
            sys.modules.pop(m, None)
        P = importlib.import_module("pote_intelligence_casco")
        return P.adaptar(json.loads(json.dumps(corrida)))
    finally:
        del sys.path[:2]
        sys.modules.clear()
        sys.modules.update(guardado)


def medir(base: str) -> dict:
    corrida = json.loads(FIXTURE.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as d:
        antes = _correr(_gerador_da_base(base, Path(d)), corrida)
    depois = _correr(RAIZ, corrida)
    ra = {(r["COMPARTIMENTO"], r["OBJETO_ID"]) for r in antes["RECUSADOS"]}
    rd = {(r["COMPARTIMENTO"], r["OBJETO_ID"]) for r in depois["RECUSADOS"]}
    obj = lambda p: {k: len(e["OBJETOS"]) for k, e in p["COMPARTIMENTOS"].items() if e["OBJETOS"]}  # noqa: E731
    mk = Counter(o["MERCADO"]["LEITURA"] for o in depois["COMPARTIMENTOS"]["market"]["OBJETOS"])
    return {
        "BASE": base, "ENTRADA": {k: len(v) for k, v in corrida["ITENS_POR_FERRAMENTA"].items()},
        "RECUSAS_ANTES": len(ra), "RECUSAS_DEPOIS": len(rd),
        "VOLTAM": sorted(ra - rd), "CONTINUAM_RECUSADAS": sorted(ra & rd), "NOVAS_RECUSAS": sorted(rd - ra),
        "MOTIVOS_ANTES": dict(Counter(r["MOTIVO"] for r in antes["RECUSADOS"])),
        "OBJETOS_ANTES": obj(antes), "OBJETOS_DEPOIS": obj(depois),
        "FONTES_NO_REGISTRO": [len(antes["COMPARTIMENTOS"]["sources"]["OBJETOS"]),
                               len(depois["COMPARTIMENTOS"]["sources"]["OBJETOS"])],
        "POLSO_DEPOIS": dict(mk),
        "POLSO_ANTES_TEM_LEITURA_DE_SERIE": any("MERCADO" in o for o in antes["COMPARTIMENTOS"]["market"]["OBJETOS"]),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escrever", action="store_true")
    ap.add_argument("--base", default=BASE_PADRAO)
    a = ap.parse_args(argv)
    if a.escrever:
        FIXTURE.write_text(json.dumps(fixture(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"escrita: {FIXTURE.relative_to(RAIZ)}")
        return 0
    m = medir(a.base)
    voltam = len(m["VOLTAM"])
    print(json.dumps({k: v for k, v in m.items() if k not in ("VOLTAM", "CONTINUAM_RECUSADAS")}, ensure_ascii=False))
    print("continuam recusadas:", m["CONTINUAM_RECUSADAS"])
    print(f"P7: {voltam} de {m['RECUSAS_ANTES']} recusas voltam · Registro {m['FONTES_NO_REGISTRO'][0]} -> "
          f"{m['FONTES_NO_REGISTRO'][1]} de 47 fontes · Polso depois {m['POLSO_DEPOIS']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
