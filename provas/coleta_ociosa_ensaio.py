# -*- coding: utf-8 -*-
"""COLETA-OCIOSA · ENSAIO A SECO do ciclo 30 (28/09/2026 15:50 -03) — 0 rede, 0 Sala, 0 robo.

    py provas/coleta_ociosa_ensaio.py                                   (a reconstrucao, antes x depois)
    py provas/coleta_ociosa_ensaio.py --plano=<copia RODADAS-PLANO.json> --estado=<copia COLETA-CONTINUA-ESTADO.json>
          --livro=<copia do livro da cortesia / TETO-24H.json> [--agora=<ISO>] [--antes=<ref>] [--saida=<json>]

A MESMA pergunta ao agendador de ANTES (`--antes`, por omissao fd8c9469, a base do vivo) e ao desta arvore:
com este plano, este estado da linha SITES e este livro de 24 h, que fontes corre o ciclo? Cada um corre
`coleta_continua.ciclo(..., a_seco=True)` num processo seu, sobre COPIAS dos ficheiros (os originais so se leem).

SEM ARGUMENTOS (os ficheiros vivos NAO estao no repositorio) — RECONSTRUIDO do relato do coordenador:
  · PLANO: a tabela commitada `ferramentas/big_collection/onda4/ORDEM-RENDIMENTO-ONDA4.md` (64 fontes, 15 de
    edagricole.it). O vivo tem 61 — as 3 que faltam: NAO SEI (nenhuma e edagricole: as 15 batem).
  · ESTADO: SITES em PASSAGEM 2 com TODAS as nao-edagricole feitas (49 aqui, 46 no vivo).
  · LIVRO: 36 reservas de edagricole.it, a mais antiga 28/09 11:12:10Z (ABRE_EM 29/09 11:12:10Z com 5 pedidos
    e orcamento 40). As horas das outras 35 e o resto do livro vivo: NAO SEI (so mudam QUANTAS cabem depois).
"""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BC = RAIZ / "ferramentas" / "big_collection"
AGORA_CICLO_30 = "2026-09-28T15:50:00-03:00"
MAIS_ANTIGA_EDAG = "2026-09-28T11:12:10+00:00"
ANTES = "fd8c9469"
SAIDA = RAIZ / "provas" / "COLETA-OCIOSA-ENSAIO.json"

# corre dentro da arvore escolhida (a de antes ou esta): so o agendador, a seco
DRIVER = r'''
import json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import coleta_continua as C
plano = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
base = Path(sys.argv[3])
cands = {l["LINHA"]: [] for l in C.LINHAS}
cands["SITES"] = C.candidatas_do_plano(plano)
agora = datetime.fromisoformat(sys.argv[5]).astimezone(timezone.utc)
r = C.ciclo(base, plano.get("COORTE_SHA256", ""), cands, pecas={"ram": lambda: C.RAM_MINIMA_GB},
            livro_24h=Path(sys.argv[4]), livros=base, agora_utc=agora, a_seco=True, janela_h=None,
            ligacao=lambda l: {"LIGADA": True, "PORQUE": "ensaio: so o agendador"})
print(json.dumps(r, ensure_ascii=False, default=str))
'''


def reconstruir(pasta: Path) -> tuple:
    sys.path.insert(0, str(BC))
    import ensaio_coleta_continua as ECC                           # noqa: E402 — o plano da tabela commitada
    plano = ECC.plano_do_documento()
    fontes = [f for r in plano["RODADAS"] for f in r["FONTES"]]
    edag = [f["SOURCE_ID"] for f in fontes if "edagricole.it" in f["DOMINIOS"]]
    estado = {"N_CICLO": 29, "PAROU": None, "LINHAS": {"SITES": {
        "PASSAGEM": 2, "FEITAS_NA_PASSAGEM": [f["SOURCE_ID"] for f in fontes if f["SOURCE_ID"] not in edag],
        "RECONSTRUIDO": "relato do ciclo 30 (coordenador, 28/09 15:50)"}}}
    t0 = datetime.fromisoformat(MAIS_ANTIGA_EDAG).timestamp()
    ev = []
    for i in range(36):
        ev.append({"TIPO": "RESERVA", "DOMINIO": "edagricole.it", "HOST": "edagricole.it", "EM": t0 + 60 * i,
                   "RUN_ID": "RECONSTRUIDO-%02d" % i, "LINHA": "SITES"})
        ev.append({"TIPO": "RESPOSTA", "DOMINIO": "edagricole.it", "EM": t0 + 60 * i + 5, "STATUS": 200, "SINAIS": [],
                   "RUN_ID": "RECONSTRUIDO-%02d" % i, "LINHA": "SITES"})
    (pasta / "RODADAS-PLANO.json").write_text(json.dumps(plano, ensure_ascii=False), encoding="utf-8")
    (pasta / "COLETA-CONTINUA-ESTADO.json").write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
    (pasta / "TETO-24H.json").write_text("".join(json.dumps(e) + "\n" for e in ev), encoding="utf-8")
    return pasta / "RODADAS-PLANO.json", pasta / "COLETA-CONTINUA-ESTADO.json", pasta / "TETO-24H.json"


def arvore_de(ref: str, pasta: Path) -> Path:
    tar = subprocess.run(["git", "-C", str(RAIZ), "archive", "--format=tar", ref, "ferramentas/big_collection",
                          "coleta", "provas", "regras", "scripts"], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(pasta)
    return pasta / "ferramentas" / "big_collection"


def perguntar(codigo: Path, plano: Path, estado: Path, livro: Path, agora: str, tmp: Path) -> dict:
    base = tmp / "base"
    base.mkdir()
    shutil.copy(estado, base / "COLETA-CONTINUA-ESTADO.json")      # a COPIA: o a_seco nao escreve, mas por via das duvidas
    copia_livro = tmp / "TETO-24H.json"
    shutil.copy(livro, copia_livro)
    env = {k: v for k, v in os.environ.items() if not k.startswith("SINTONIA_")}   # sem teto manual: o orcamento vigente
    env.update(HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9", PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-c", DRIVER, str(codigo), str(plano), str(base), str(copia_livro), agora],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=600)
    if r.returncode != 0:
        raise SystemExit("o agendador de %s nao correu:\n%s" % (codigo, r.stderr[-2000:]))
    reg = json.loads(r.stdout.strip().splitlines()[-1])
    s = reg["LINHAS"]["SITES"]
    esp = {}
    for x in reg["ESPERAM"]:
        for d, f in (x.get("DOMINIOS_FECHADOS") or {}).items():
            e = esp.setdefault(d, {"FONTES": 0, "PORQUE": set(), "ABRE_EM": f["ABRE_EM"]})
            e["FONTES"] += 1
            e["PORQUE"].add(f["PORQUE"])
            for k in ("GASTO_24H", "ORCAMENTO_24H"):
                if k in f:
                    e[k] = f[k]
    return {"ESTADO": s["ESTADO"], "FONTES_QUE_CORRERIAM": len(s["FONTES"]), "FONTES": s["FONTES"],
            "PEDIDOS_PREVISTOS": s.get("PEDIDOS_PREVISTOS"), "PASSAGEM_NOVA": s.get("PASSAGEM_NOVA"),
            "ESPERAM": len(reg["ESPERAM"]),
            "ESPERAM_POR_DOMINIO": {d: dict(v, PORQUE=sorted(v["PORQUE"])) for d, v in sorted(esp.items())},
            "PROXIMO_A_ABRIR": reg.get("PROXIMO_A_ABRIR"), "ORCAMENTO_DO_CICLO": reg.get("ORCAMENTO_DO_CICLO")}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    agora = arg.get("agora") or AGORA_CICLO_30
    tmp = Path(tempfile.mkdtemp(prefix="coleta-ociosa-ensaio-"))
    try:
        if arg.get("plano"):
            plano, estado, livro = Path(arg["plano"]), Path(arg["estado"]), Path(arg["livro"])
            origem = {"RECONSTRUIDO": False, "PLANO": str(plano), "ESTADO": str(estado), "LIVRO": str(livro)}
        else:
            (tmp / "rec").mkdir()
            plano, estado, livro = reconstruir(tmp / "rec")
            origem = {"RECONSTRUIDO": True, "PLANO": "onda4/ORDEM-RENDIMENTO-ONDA4.md (64 fontes; o vivo tem 61)",
                      "ESTADO": "SITES PASSAGEM 2, todas as nao-edagricole feitas",
                      "LIVRO": "36 reservas edagricole.it, a mais antiga %s (uma por minuto)" % MAIS_ANTIGA_EDAG}
        ref = arg.get("antes") or ANTES
        (tmp / "a").mkdir()
        (tmp / "d").mkdir()
        (tmp / "arvore-antes").mkdir()
        antes = perguntar(arvore_de(ref, tmp / "arvore-antes"), plano, estado, livro, agora, tmp / "a")
        depois = perguntar(BC, plano, estado, livro, agora, tmp / "d")
        f = json.loads(Path(estado).read_text(encoding="utf-8"))["LINHAS"]["SITES"]
        out = {"AGORA": agora, "ORIGEM": origem, "ESTADO_DE_PARTIDA": {"PASSAGEM": f.get("PASSAGEM"),
               "FEITAS_NA_PASSAGEM": len(f.get("FEITAS_NA_PASSAGEM") or [])},
               "ANTES": dict(antes, CODIGO=ref), "DEPOIS": dict(depois, CODIGO="esta arvore")}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    saida = Path(arg["saida"]) if arg.get("saida") else SAIDA
    saida.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    for k in ("ANTES", "DEPOIS"):
        x = out[k]
        print("%-6s %-14s correriam %2d fontes (%s pedidos) · esperam %2d · passagem nova: %s" % (
            k, x["ESTADO"], x["FONTES_QUE_CORRERIAM"], x["PEDIDOS_PREVISTOS"], x["ESPERAM"],
            (x["PASSAGEM_NOVA"] or {}).get("MOTIVO")))
        for d, e in x["ESPERAM_POR_DOMINIO"].items():
            print("         espera %-16s %2d fontes %s gasto %s/%s abre %s" % (
                d, e["FONTES"], e["PORQUE"], e.get("GASTO_24H"), e.get("ORCAMENTO_24H"), e["ABRE_EM"]))
    print("escrito:", saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
