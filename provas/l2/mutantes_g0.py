#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACAO DO G0 POR AFIRMACAO — os 12 mutantes da DIRETIVA-G0-POR-AFIRMACAO (§2) e dois a mais; cada um tem de
fazer `tests.test_g0_da_afirmacao` REPROVAR. O mesmo harness de provas/l2/mutantes.py (alvo unico em LF e em CRLF,
restauro byte a byte conferido por SHA-256, testes com -B).

    py provas/l2/mutantes_g0.py        # grava provas/l2/MUTANTES-G0.json
"""
import json
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from mutantes import aplicar, sha  # noqa: E402

RAIZ = AQUI.parents[1]
SAIDA = AQUI / "MUTANTES-G0.json"
TESTE = "tests.test_g0_da_afirmacao"
G0 = "motor/g0_da_afirmacao.py"
MOT = "motor/motor_das_capacidades.py"
POTE = "pacote/pote_intelligence_casco.py"
PONTE = "pacote/ponte_intelligence_casco.py"

MUTANTES = [
 ("G1", G0, "o G0 da afirmacao usa o FACT_TIME do item",
  "    ft = ft_bloco.get(\"VALOR\")\n", "    ft = item.get(\"FACT_TIME\")\n"),
 ("G2", POTE, "prova de afirmacao admitida pelo G0 do item (pote)",
  "        if e.get(\"G0_DA_AFIRMACAO\") != \"PASSOU\":", "        if e.get(\"G0_DO_ITEM\") != \"PASSOU\":"),
 ("G3", G0, "afirmacao com RAW_SHA256 diferente do item aceite",
  "    elif af.get(\"RAW_SHA256\") != raw_sha256:", "    elif False:"),
 ("G4", G0, "TRECHO que nao bate com o texto aceite",
  "    elif str(texto or \"\")[a:b] != trecho:", "    elif False:"),
 ("G5", G0, "PAPEL != ACONTECIMENTO com FACT_TIME aceite",
  "        if papel != PAPEL_QUE_E_FACTO:", "        if False:"),
 ("G6", G0, "ORIGEM LITERAL com BASIS fora do trecho aceite",
  "            if origem == LITERAL and not (", "            if False and not ("),
 ("G7", G0, "RELATIVO_D63 servindo ACT_NOW",
  "        bloqueados[\"ACT_NOW\"] = RELATIVO_D63", "        pass"),
 ("G8", G0, "afirmacao duplicada contada duas vezes",
  "            dup = trechos.get(", "            dup = None and trechos.get("),
 ("G9", MOT, "REGION_ID cunhado a partir do lugar",
  "           \"REGION_ID\": _entidade(NAO_SEI, \"CASCO\", de),",
  "           \"REGION_ID\": _entidade(sg[\"FACT_LOCATION\"], \"AFIRMACAO.FACT_LOCATION\", de),"),
 ("G10", MOT, "sem AFIRMACOES.json o pote muda (archive vazio aparece)",
  "    if idx_af is not None:\n        objetos[\"archive\"] = [",
  "    objetos[\"archive\"] = []\n    if idx_af is not None:\n        objetos[\"archive\"] = ["),
 ("G11", MOT, "FACT_TIME := PUBLISHED_AT no objeto da afirmacao",
  "           \"FACT_TIME\": _entidade(sg[\"FACT_TIME\"], \"AFIRMACAO.FACT_TIME\", de)}",
  "           \"FACT_TIME\": _entidade(_v(ready.get(\"PUBLISHED_AT\")), \"AFIRMACAO.FACT_TIME\", de)}"),
 ("G12", G0, "afirmacao sem CLAIM_ID aceite",
  "    if _ign(af.get(\"CLAIM_ID\")):", "    if False:"),
 # ── a mais ──
 ("G13", MOT, "prova de afirmacao admitida pelo G0 do item (conferencia do motor)",
  "                    if l.get(\"G0_DA_AFIRMACAO\") != \"PASSOU\":", "                    if l.get(\"G0_DO_ITEM\") != \"PASSOU\":"),
 ("G14", PONTE, "a entrada da afirmacao entra no indice do ITEM (os dois G0 misturados)",
  "        if isinstance(e, dict) and \"CLAIM_ID\" in e:\n            continue\n", ""),
]


def _correr_teste():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, "-B", "-m", "unittest", TESTE], cwd=RAIZ, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=900, env=env)


def main() -> int:
    ficheiros = sorted({m[1] for m in MUTANTES})
    antes = {f: sha(RAIZ / f) for f in ficheiros}
    base = _correr_teste()
    out = {"TESTE": TESTE, "BASE_VERDE": base.returncode == 0, "MUTANTES": []}
    if base.returncode:
        print(base.stderr[-2000:])
        out["ESTADO"] = "BASE_VERMELHA"
        SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        return 1
    for mid, f, finge, velho, novo in MUTANTES:
        p = RAIZ / f
        original = p.read_bytes()
        mutado, n = aplicar(original, velho, novo)
        if n != 1:
            out["MUTANTES"].append({"ID": mid, "FICHEIRO": f, "FINGE": finge, "ESTADO": "ALVO_NAO_UNICO (%d)" % n})
            print(mid, "ALVO_NAO_UNICO", n, finge, flush=True)
            continue
        try:
            p.write_bytes(mutado)
            r = _correr_teste()
            quem = [l.split("(")[0].replace("FAIL: ", "").replace("ERROR: ", "").strip()
                    for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
            out["MUTANTES"].append({"ID": mid, "FICHEIRO": f, "FINGE": finge,
                                    "ESTADO": "MORTO" if r.returncode else "SOBREVIVEU", "APANHADO_POR": quem[:4]})
        finally:
            p.write_bytes(original)
        print(mid, out["MUTANTES"][-1]["ESTADO"], finge, flush=True)
    depois = {f: sha(RAIZ / f) for f in ficheiros}
    mortos = sum(1 for m in out["MUTANTES"] if m["ESTADO"] == "MORTO")
    out.update({"MORTOS": mortos, "TOTAL": len(MUTANTES), "RESTAURADOS_IGUAIS": antes == depois,
                "ESTADO": "PASS" if mortos == len(MUTANTES) and antes == depois else "FAIL"})
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("MORTOS %d/%d · restaurados iguais: %s" % (mortos, len(MUTANTES), antes == depois))
    return 0 if out["ESTADO"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
