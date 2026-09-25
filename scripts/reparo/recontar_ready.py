#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1 · RECONTAR AS 25 READY — em copia, SO com o portao de egresso = PASS IT.

    py scripts/reparo/recontar_ready.py --foto <pasta com os livros do vivo> --sha <commit> [--bancas 4]

Porque existe: o plano de instalacao sobre 55b50a63 diz «25 READY» pela medicao
das 20:28Z (codigo do robo e livros identicos). A VPN caiu para BR antes de se
poder re-contar com rede. Este script faz essa recontagem quando a VPN voltar:

  0. PORTAO. Mede o portao de egresso por consenso (superficie/rede.py). Se nao
     for PASS IT, escreve «ESPERA VPN» e sai com 3 — ZERO pedidos as fontes.
  1. Monta N bancas: `git archive <sha>` + os livros da foto por cima.
  2. Corre medir_em_copia.py em cada banca (fatia de anfitriao; 2 s por anfitriao).
  3. Mede o portao outra vez no fim: se caiu durante a corrida, o resultado sai
     marcado VPN_CAIU_DURANTE (os pedidos podem ter saido por outro pais).
  4. Junta (juntar_bancas.py) e confere com a revisao (curadoria/REVISAO-READY-V1.json):
       esperado = so LIMPA + ACESSO_PARCIAL chegam a READY; nenhuma suspeita.
  5. Escreve --saida (default scripts/reparo/R1-RECONTAGEM-<sha>.json) e apaga as bancas.

A foto: os livros do vivo (curadoria/*.json + candidatas/FONTES-CANDIDATAS.json)
copiados ANTES de o bot correr a R1 — p.ex. %TEMP%/r1v5-snap-20260924T202844Z.
Depois de instalada a R1 no vivo, uma foto nova ja traz o reparo feito; a
recontagem em copia deixa de medir o mesmo.
"""
from __future__ import annotations

import argparse
import collections
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ESPERA_VPN = 3


def portao() -> dict:
    sys.path.insert(0, str(RAIZ / "superficie"))
    import rede  # noqa: PLC0415
    return rede.portao_de_egresso("IT")


def _passou(p: dict) -> bool:
    return p.get("EGRESS_GATE") == "PASS"


def montar(banca: Path, sha: str, foto: Path) -> None:
    banca.mkdir(parents=True)
    arq = subprocess.run(["git", "archive", sha], cwd=RAIZ, capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(banca)], input=arq, check=True)
    for p in foto.glob("*.json"):
        destino = banca / ("candidatas" if p.name == "FONTES-CANDIDATAS.json" else "curadoria") / p.name
        shutil.copy2(p, destino)


def conferir(juntado: dict, revisao: dict) -> dict:
    classe = {x["SOURCE_ID"]: x["CLASSE"] for x in revisao["FONTES"]}
    ready = {r["SOURCE_ID"] for r in juntado["READY_NOVAS"]}
    aceites = {s for s, c in classe.items() if c in ("LIMPA", "ACESSO_PARCIAL")}
    suspeitas_ready = sorted(s for s in ready if classe.get(s) not in (None, "LIMPA", "ACESSO_PARCIAL"))
    fora = sorted(s for s in ready if s not in classe)
    return {"READY_NOVAS": len(ready), "ESPERADAS": len(aceites),
            "POR_CLASSE": dict(collections.Counter(classe.get(s, "FORA_DA_REVISAO") for s in ready)),
            "ACEITES_QUE_NAO_CHEGARAM": sorted(aceites - ready),
            "SUSPEITAS_QUE_SAIRAM_READY": suspeitas_ready, "READY_FORA_DA_REVISAO": fora,
            "VEREDITO": "PASS" if not suspeitas_ready and not fora else "FAIL"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--foto", required=True)
    ap.add_argument("--sha", required=True)
    ap.add_argument("--bancas", type=int, default=4)
    ap.add_argument("--saida")
    a = ap.parse_args(argv)
    foto = Path(a.foto)
    if not (foto / "LIFECYCLE-LEDGER-V1.json").exists():
        print("foto sem LIFECYCLE-LEDGER-V1.json: %s" % foto)
        return 2
    p0 = portao()
    print("PORTAO ANTES:", p0.get("EGRESS_GATE"), p0.get("EGRESS_COUNTRY_CODE"), flush=True)
    if not _passou(p0):
        print("ESPERA VPN — portao de egresso = %s (%s); nenhum pedido as fontes"
              % (p0.get("EGRESS_GATE"), p0.get("EGRESS_COUNTRY_CODE")))
        return ESPERA_VPN
    base = Path(tempfile.mkdtemp(prefix="r1-recontagem-"))
    bancas = [base / ("banca-%d" % k) for k in range(a.bancas)]
    try:
        for b in bancas:
            montar(b, a.sha, foto)
        procs = [subprocess.Popen([sys.executable, "-u", "scripts/reparo/medir_em_copia.py", "--banca", str(b),
                                   "--particao", "%d/%d" % (k, a.bancas)], cwd=b,
                                  stdout=open(b / "medicao.log", "w", encoding="utf-8"), stderr=subprocess.STDOUT,
                                  env={**__import__("os").environ, "PYTHONUTF8": "1"})
                 for k, b in enumerate(bancas)]
        rcs = [p.wait() for p in procs]
        p1 = portao()
        print("PORTAO DEPOIS:", p1.get("EGRESS_GATE"), p1.get("EGRESS_COUNTRY_CODE"), flush=True)
        saida_j = base / "juntado.json"
        subprocess.run([sys.executable, str(RAIZ / "scripts" / "reparo" / "juntar_bancas.py"), "--foto", str(foto),
                        *sum((["--banca", str(b)] for b in bancas), []), "--saida", str(saida_j)], check=True)
        juntado = json.loads(saida_j.read_text(encoding="utf-8"))
        revisao = json.loads((RAIZ / "curadoria" / "REVISAO-READY-V1.json").read_text(encoding="utf-8"))
        conf = conferir(juntado, revisao)
        out = {"DATASET": "R1-RECONTAGEM", "SHA": a.sha, "FOTO": str(foto),
               "MEDIDO_EM": datetime.now(timezone.utc).isoformat(), "RCS_DAS_BANCAS": rcs,
               "PORTAO_ANTES": {k: p0.get(k) for k in ("EGRESS_GATE", "EGRESS_COUNTRY_CODE")},
               "PORTAO_DEPOIS": {k: p1.get(k) for k in ("EGRESS_GATE", "EGRESS_COUNTRY_CODE")},
               "VPN_CAIU_DURANTE": not _passou(p1),
               "READY_ANTES": juntado["READY_ANTES"], "READY_DEPOIS": juntado["READY_DEPOIS"],
               "CONFERENCIA": conf, "JUNTADO": juntado}
        saida = Path(a.saida or RAIZ / "scripts" / "reparo" / ("R1-RECONTAGEM-%s.json" % a.sha[:8]))
        saida.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print("READY %d -> %d · conferencia %s · VPN caiu durante: %s · %s"
              % (out["READY_ANTES"], out["READY_DEPOIS"], conf["VEREDITO"], out["VPN_CAIU_DURANTE"], saida))
        return 0 if conf["VEREDITO"] == "PASS" and not out["VPN_CAIU_DURANTE"] else 1
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
