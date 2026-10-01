#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Corre o leitor semantico sobre os itens de um lote fixado, numa COPIA so-leitura da Sala. Sombra: escreve so na
pasta de saida dada (fora da Sala, fora de PARA-O-CASCO*). O leitor ve SO o texto (o lote e os rotulos nao lhe chegam).
    python provas/reader-sombra/correr_rodada.py <SALA_ATUAL.json> <LOTE.json|TODOS> <saida.json> [--paralelo N]"""
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "leis"))
import leitor_semantico as L  # noqa: E402


def main(argv):
    sala, lote, saida = Path(argv[0]), argv[1], Path(argv[2])
    par = int(argv[argv.index("--paralelo") + 1]) if "--paralelo" in argv else 1
    S = json.loads(sala.read_text(encoding="utf-8"))
    ult = {}
    for i, x in enumerate(S):
        ult[x["item_id"]] = i
    if lote == "TODOS":
        alvo = [(None, n) for n in sorted(set(ult.values()))]
        lote_sha = "TODOS (ultima linha de cada item_id da copia)"
    else:
        d = json.loads(Path(lote).read_text(encoding="utf-8"))
        alvo = [(x["ID"], x["N"]) for x in d["ITENS"]]
        lote_sha = hashlib.sha256(Path(lote).read_bytes()).hexdigest()
    t0 = time.time()

    def um(par_):
        lid, n = par_
        s = S[n]
        r = L.ler(s["item_id"], s["texto"] or "", s.get("captured_at"))
        r.update(LOTE_ID=lid, N=n)
        return r

    with ThreadPoolExecutor(max_workers=par) as ex:
        res = list(ex.map(um, alvo))
    out = {"CONTRATO": "RODADA_DO_LEITOR_SEMANTICO/v1", "MARCA": "SOMBRA · NAO_PARA_CLIENTE",
           "COPIA": str(sala), "COPIA_SHA256": hashlib.sha256(sala.read_bytes()).hexdigest(), "LOTE": lote,
           "LOTE_SHA256": lote_sha, "MODELO": L.MODELO, "PROMPT_VERSAO": L.PROMPT_VERSAO,
           "PROMPT_SHA256": L.PROMPT_SHA256, "SCHEMA_SHA256": L.SCHEMA_SHA256, "PARALELO": par,
           "INICIO": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
           "SEGUNDOS_PAREDE": round(time.time() - t0, 1), "LEITURAS": res}
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ac = sum(1 for r in res if r["FACT_TIME"].get("JUIZ") == "ACEITE")
    print("LEITURAS %d · ACEITES %d · %ss" % (len(res), ac, out["SEGUNDOS_PAREDE"]))


if __name__ == "__main__":
    main(sys.argv[1:])
