#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D156 · CASCO CONSUMIDOR — uma ENTREGA DE TESTE em PARA-O-CASCO/, pela forma canonica.

    python3 tests/entrega_de_teste.py --destino <.../PARA-O-CASCO> --caso demo|vazio|sha|falta-pote|falta-manifesto|estado|real
    python3 tests/entrega_de_teste.py --destino <...> --caso real --pote <POTE-R9-PARA_CLIENTE.json>

A forma e a do disparador da Intelligence (admissao/gatilho_da_inteligencia.py:entregar no ramo
claude/l2-disparador-v1; provas/l2/PARA-O-CASCO.md): POTE.json + MANIFESTO.json + SHA256SUMS.txt, escritos numa pasta
AO LADO e trocados INTEIROS por os.replace — nunca meia pasta. Os casos estragados estragam DEPOIS de escrever as
somas, dentro da pasta nova, antes da troca: o casco recebe-os ja inteiros, como receberia um defeito real.

⚠️ DADO SINTETICO DECLARADO nos casos demo/vazio/sha/falta-*/estado: o pote e o de tests/fixtures/pote/ (ids SINT-,
CORRIDA_SINTETICA = true no pote e em cada objeto). So o caso `real` le um pote real, e so do caminho dado.
Cada troca escreve uma linha em <destino>/../ENTREGAS-DE-TESTE.ndjson com a hora exata (T0).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FIX = RAIZ / "tests" / "fixtures" / "pote"
POTES = {"demo": FIX / "POTE-SINTETICO-PUBLICA-SOZINHO.json", "vazio": FIX / "POTE-SINTETICO-VAZIO.json"}
CASOS = ("demo", "vazio", "sha", "falta-pote", "falta-manifesto", "estado", "real")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def entregar(destino: Path, pote_bytes: bytes, caso: str = "demo") -> dict:
    """Escreve a entrega AO LADO de `destino` e troca-a inteira. Devolve {T0, CASO, SHA256_POTE, ...}."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    pote = json.loads(pote_bytes.decode("utf-8"))
    agora = _dt.datetime.now(_dt.timezone.utc)
    nova = destino.parent / (destino.name + ".nova-" + agora.strftime("%Y%m%dT%H%M%S%f"))
    nova.mkdir()
    (nova / "POTE.json").write_bytes(pote_bytes)
    man = {"INTELLIGENCE_RUN_ID": pote.get("INTELLIGENCE_RUN_ID"),
           "RESULT_STATE": "RUNNING" if caso == "estado" else pote.get("RESULT_STATE", "DONE"),
           "CORRIDA_SINTETICA": pote.get("CORRIDA_SINTETICA"),
           "SOURCE_HEAD": pote.get("SOURCE_HEAD"), "CORTE": pote.get("CORTE"),
           "GERADO_EM": agora.strftime("%Y-%m-%dT%H:%M:%SZ"),
           "GERADO_POR": "tests/entrega_de_teste.py (D156, entrega de TESTE, caso %s)" % caso,
           "POTE": {"ARQUIVO": "POTE.json", "SHA256_ARQUIVO": _sha(pote_bytes),
                    "SHA256_CANONICO": _sha(json.dumps(pote, sort_keys=True, ensure_ascii=False,
                                                       separators=(",", ":")).encode("utf-8")),
                    "CONTRATO": "POTE_INTELLIGENCE_CASCO/v2"},
           "VALIDAR_POTE_V2": "PASSA"}
    mb = (json.dumps(man, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    (nova / "MANIFESTO.json").write_bytes(mb)
    (nova / "SHA256SUMS.txt").write_bytes(("%s *POTE.json\n%s *MANIFESTO.json\n" % (_sha(pote_bytes), _sha(mb))).encode())
    if caso == "sha":
        (nova / "POTE.json").write_bytes(pote_bytes + b" ")          # o byte muda depois da soma
    elif caso == "falta-pote":
        (nova / "POTE.json").unlink()
    elif caso == "falta-manifesto":
        (nova / "MANIFESTO.json").unlink()
    velha = None
    if destino.exists():
        velha = destino.parent / (destino.name + ".velha-" + agora.strftime("%Y%m%dT%H%M%S%f"))
        os.replace(destino, velha)
    os.replace(nova, destino)
    t0 = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if velha:
        shutil.rmtree(velha, ignore_errors=True)
    reg = {"T0": t0, "CASO": caso, "DESTINO": str(destino), "INTELLIGENCE_RUN_ID": pote.get("INTELLIGENCE_RUN_ID"),
           "CORRIDA_SINTETICA": pote.get("CORRIDA_SINTETICA"), "SHA256_POTE": _sha(pote_bytes)}
    with open(destino.parent / "ENTREGAS-DE-TESTE.ndjson", "a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")
    return reg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Entrega de TESTE em PARA-O-CASCO/ (D156).")
    ap.add_argument("--destino", required=True)
    ap.add_argument("--caso", required=True, choices=CASOS)
    ap.add_argument("--pote", default=None, help="so no caso `real`: o pote real a entregar")
    a = ap.parse_args(argv)
    if a.caso == "real":
        if not a.pote:
            print("o caso `real` exige --pote")
            return 2
        b = Path(a.pote).read_bytes()
    else:
        b = POTES["vazio" if a.caso == "vazio" else "demo"].read_bytes()
    print(json.dumps(entregar(Path(a.destino), b, a.caso), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
