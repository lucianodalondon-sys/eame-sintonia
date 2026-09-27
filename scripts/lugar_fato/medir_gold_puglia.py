#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BOLETIM-POR-SECAO · quanto do GOLD-FIXTURE-PUGLIA-V1 passa ANTES e DEPOIS. Sem rede.

    py scripts/lugar_fato/medir_gold_puglia.py [--base=REV]   -> scripts/lugar_fato/MEDIDA-GOLD-PUGLIA-V1.json

ANTES = os ficheiros de `leis/` na revisao `--base` (por omissao 8a0727e, a base desta missao), lidos como a
base os entregava: POR DOCUMENTO — as pragas e culturas de `ler_boletim(texto)` do documento inteiro e o
`fact_location` de `fato_do_texto.campos_do_fato(texto)`. A base nao tinha ENTITY_SOURCE nem LOCATION_SOURCE:
essas chaves saem «NAO_PRODUZIDO» e contam como FAIL (o ESPERADO pede-as).
DEPOIS = `ler_afirmacao` da arvore de trabalho. O harness (qual texto, qual trecho, que chaves) e o MESMO nos
dois lados: `scripts/lugar_fato/gold_puglia.py`.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
SAIDA = AQUI / "MEDIDA-GOLD-PUGLIA-V1.json"
UNRESOLVED, NAO = "UNRESOLVED", "NAO_PRODUZIDO"


def _medir(leis: str, modo: str) -> dict:
    """Corre NUM PROCESSO NOVO, com `leis` a frente do caminho (modulos da base e da arvore nao se misturam)."""
    sys.path[:0] = [leis, str(AQUI)]
    import boletim_do_campo as BCX  # noqa: PLC0415  (o da revisao medida)
    import gold_puglia as G         # noqa: PLC0415
    sys.path.insert(0, str(RAIZ / "leis"))
    if modo == "afirmacao":
        return G.correr(BCX)
    import fato_do_texto as FTX     # noqa: PLC0415
    import importlib.util as u      # noqa: PLC0415
    sp = u.spec_from_file_location("bc_harness", RAIZ / "leis" / "boletim_do_campo.py")
    BCH = u.module_from_spec(sp)
    sp.loader.exec_module(BCH)      # so para achar o trecho e contar nomes: o mesmo harness dos dois lados

    def por_documento(d):
        b = BCX.ler_boletim(d["TEXTO"])
        lugar = FTX.campos_do_fato(d["TEXTO"])["fact_location"]
        lugar = UNRESOLVED if lugar == "NAO SEI" else lugar
        return {"PRAGAS": {"VALOR": b["PROBLEMAS_NAO_AUSENTES"] or "UNKNOWN", "ENTITY_SOURCE": NAO},
                "CULTURA": {"VALOR": b["CULTURAS"] or "UNKNOWN", "ENTITY_SOURCE": NAO},
                "FACT_LOCATION": {"VALOR": lugar, "LOCATION_SOURCE": NAO, "LOCATION_EXPRESSION_RAW": NAO,
                                  "PONTO_NO_MAPA": lugar != UNRESOLVED}}
    return G.correr(BCH, ler=por_documento)


def main():
    if len(sys.argv) > 1 and sys.argv[1].startswith("--interno="):
        leis, modo = sys.argv[1].split("=", 1)[1].split("|")
        print(json.dumps(_medir(leis, modo), ensure_ascii=False))
        return
    base = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--base=")), "8a0727e")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    with tempfile.TemporaryDirectory() as tmp:
        arq = subprocess.run(["git", "archive", base, "leis"], cwd=RAIZ, capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", tmp], input=arq, check=True)
        lados = {}
        for nome, leis, modo in (("ANTES", os.path.join(tmp, "leis"), "documento"),
                                 ("DEPOIS", str(RAIZ / "leis"), "afirmacao")):
            p = subprocess.run([sys.executable, __file__, "--interno=%s|%s" % (leis, modo)], cwd=RAIZ, env=env,
                               capture_output=True, text=True, encoding="utf-8", check=True)
            lados[nome] = json.loads(p.stdout)
    base_sha = subprocess.run(["git", "rev-parse", base], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    out = {"DATASET": "MEDIDA-GOLD-PUGLIA-V1", "GOLD_SET": lados["DEPOIS"]["GOLD_SET"],
           "VERSAO_DO_GOLD": lados["DEPOIS"]["VERSAO"], "BASE": base_sha,
           "ANTES": {"LEITURA": "por DOCUMENTO (ler_boletim + campos_do_fato da base)",
                     "PLACAR": lados["ANTES"]["PLACAR"],
                     "CASOS": {c["CASO"]: c["VEREDITO"] for c in lados["ANTES"]["CASOS"]}},
           "DEPOIS": {"LEITURA": "por AFIRMACAO (boletim_do_campo.ler_afirmacao)",
                      "PLACAR": lados["DEPOIS"]["PLACAR"],
                      "CASOS": {c["CASO"]: c["VEREDITO"] for c in lados["DEPOIS"]["CASOS"]}},
           "DETALHE_ANTES": lados["ANTES"]["CASOS"], "DETALHE_DEPOIS": lados["DEPOIS"]["CASOS"]}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: out[k]["PLACAR"] for k in ("ANTES", "DEPOIS")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
