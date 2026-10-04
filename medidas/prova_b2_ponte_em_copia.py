#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVA B2 — uma volta REAL da ponte sobre COPIAS dos livros vivos.

    NAO TOCAR NOS SERVICOS VIVOS. So leitura, por copia.

Monta numa pasta temporaria:
    <tmp>/canon/  LEDGER, EVIDENCE e CONTRATOS do portao (bancada da ponte)
    <tmp>/bot/curadoria/  LEDGER, EVIDENCE e CONTRATOS do bot
a partir de uma fotografia com sha256 (~/sintonia-gabarito/B1-SNAPSHOT-*), aponta
os modulos para la e corre `ponte_automatica.uma_volta(forcar=True)` — o MESMO
codigo que o observador corre. Mede o portao antes e depois.

Nada e escrito fora de <tmp>. Os ficheiros reais do repositorio sao conferidos
por sha256 antes e depois.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import lifecycle as LC               # noqa: E402
import ready_split as RS             # noqa: E402
import reconciliar_livros as R       # noqa: E402
import collection_gate as CG         # noqa: E402
import ponte_automatica as PA        # noqa: E402

REAIS = [RAIZ / "curadoria" / n for n in ("LIFECYCLE-LEDGER-V1.json", "LIFECYCLE-EVIDENCE-V1.json",
                                          "italy_contracts_curator.json")]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "AUSENTE"


def montar(snap: Path, tmp: Path) -> None:
    canon, bot = tmp / "canon", tmp / "bot" / "curadoria"
    canon.mkdir(parents=True)
    bot.mkdir(parents=True)
    for dst, pref in ((canon, "ponte-curador-v1_curadoria_"), (bot, "source-curator-service-v1_curadoria_")):
        for n in ("LIFECYCLE-LEDGER-V1.json", "LIFECYCLE-EVIDENCE-V1.json", "italy_contracts_curator.json"):
            shutil.copy(snap / (pref + n), dst / n)
    LC.LIVRO = canon / "LIFECYCLE-LEDGER-V1.json"
    R.EVIDENCIA_A = RS.EVIDENCIA = canon / "LIFECYCLE-EVIDENCE-V1.json"
    R.CONTRATOS_A = RS.CONTRATOS = canon / "italy_contracts_curator.json"
    R.SAIDA = tmp / "RECONCILIACAO.json"
    PA.ESTADO = tmp / "ESTADO.json"
    PA.DIARIO = tmp / "DIARIO.ndjson"


def correr(snap: Path) -> dict:
    antes_reais = {p.name: _sha(p) for p in REAIS}
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        montar(snap, tmp)
        antes = CG.elegiveis()
        painel_antes = CG.painel()
        r = PA.uma_volta(lane=tmp / "bot", forcar=True)
        depois = CG.elegiveis()
        inv = {l["SOURCE_ID"]: l for l in CG.inventario()}
        out = {
            "FOTOGRAFIA": str(snap),
            "VOLTA": {k: r.get(k) for k in ("ACCAO", "LIVRO_CANONICO", "PROVAS_IMPORTADAS",
                                             "CONTRATOS_IMPORTADOS", "COLISOES_DE_DONO", "PORTAO")},
            "PAINEL_ANTES": painel_antes, "PAINEL_DEPOIS": CG.painel(),
            "ENTRARAM": sorted(set(depois) - set(antes)),
            "SAIRAM": sorted(set(antes) - set(depois)),
            "MOTIVOS_DEPOIS": {},
        }
        for l in inv.values():
            out["MOTIVOS_DEPOIS"][l["MOTIVO"]] = out["MOTIVOS_DEPOIS"].get(l["MOTIVO"], 0) + 1
        out["ENTRARAM_DETALHE"] = [{"SOURCE_ID": s, "READY_RULE": inv[s]["READY_RULE"],
                                    "PORQUE": inv[s]["PORQUE"]} for s in out["ENTRARAM"]]
    depois_reais = {p.name: _sha(p) for p in REAIS}
    out["FICHEIROS_REAIS_INTOCADOS"] = antes_reais == depois_reais
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    snap = Path(argv[0])
    out = correr(snap)
    print(json.dumps(out, ensure_ascii=False, indent=1)[:6000])
    if len(argv) > 1:
        Path(argv[1]).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
