# -*- coding: utf-8 -*-
"""O MAESTRO SOCIAL — uma rodada social de ponta a ponta, num comando, e retoma de onde parou.

    py ferramentas/maestro_social/maestro_social.py --so-plano [--canario] [--fontes=A,B] [--saida=<pasta>]
    py ferramentas/maestro_social/maestro_social.py --correr --autorizado-pelo-dono --saida=<pasta nova>
            [--canario] [--fontes=A,B] [--videos=IT-T5-192:VIDEOID,...] [--retomar]
    py ferramentas/maestro_social/maestro_social.py --relatorio --estado=<MAESTRO-SOCIAL-ESTADO.json>

O condutor da web (`ferramentas/big_collection/onda_web.py`) no molde social (MAESTRO-SOCIAL, 26/09):

  1. AS RODADAS vem de `curadoria/plano_onda_social.rodadas()`: ate 2 contas LinkedIn (`teto=1` no
     pedido — C2) + 1 video YouTube por ONDA. Dominios diferentes; cada um cabe em 5 (D38/D41).
  2. O FREIO E ANTES DO PEDIDO. Cada onda nomeia o SEU livro (`<saida>/ONDA-nn/TETO-ONDA.json`) em
     SINTONIA_TETO_ONDA; todas as corridas dela (Scrap e o yt-dlp com freio) somam nele e o pedido que
     passaria do teto NAO sai (`coleta/teto_da_onda.py`). O livro e um por onda e a onda e uma.
  3. VPN ANTES E DEPOIS de cada fonte, pelo DONO (`superficie/rede.py`, consenso de 3, via
     `micro_coleta.medir_egresso`). Fora de IT → PARA, nada mais sai.
  4. PROVA-TETO no fim de cada onda (`provas/prova_teto_dominio.verificar` sobre o livro de corridas).
     FAIL ou NAO_SEI → PARA.
  5. O ESTADO (`<saida>/MAESTRO-SOCIAL-ESTADO.json`) e gravado a cada fonte. `--retomar` le-o e continua
     da primeira fonte por decidir, com o MESMO plano e o MESMO livro da onda a meio. O estado tem
     `FONTES[]` no formato que `micro_coleta relatorio --estado=` le (SOURCE_ID, RUN_ID, CORREU,
     STATUS, GATE, EGRESSO).

`--canario`: as contas sociais so ficam READY DEPOIS do canario, e o canario social E uma colheita do
Scrap (o Curator para em CANARY_PENDING por desenho). Com `--canario` entram tambem as fontes SCRAP_FASE
em CANARY_PENDING. Sem ele, so as que o portao diz ELIGIBLE.

YouTube: a listagem (`canal-youtube`) usa a API oficial, cuja chave so vive no GitHub Actions. Sem chave
no ambiente, o maestro corre `audio-youtube` do VIDEO_ID dado em `--videos=SID:ID`; sem nenhum dos dois,
a fonte NAO corre (PORQUE=SEM_VIDEO_E_SEM_CHAVE) — isso nao e FAILED.

Disjuntores: egresso fora de IT (antes/depois) · corrida > 30 min · 3 FAILED seguidas · livro da onda
acima do teto · prova-teto != PASS.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
for _p in ("", "curadoria", "coleta", "provas", "orquestrador", "scripts/micro_coleta"):
    sys.path.insert(0, str(RAIZ / _p) if _p else str(RAIZ))

TETO = 5
ESTADO = "MAESTRO-SOCIAL-ESTADO.json"
ENV_CHAVE_YT = "YOUTUBE_DATA_API_KEY"
LIMITE_S = 1800
AVISO = Path(r"C:\Users\London1\auditoria-madrugada\bc4-aviso-vivo.txt")


def agora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def ledger() -> Path:
    return Path(os.environ.get("ITALY_OPS_ROOT") or RAIZ) / "data" / "collection-ledger" / "italy" / "runs.ndjson"


# ── o plano (sem rede, sem Sala) ─────────────────────────────────────────────
def contratos() -> dict:
    import plano_onda_social as P                                   # noqa: PLC0415
    return {c["SOURCE_ID"]: c for c in json.loads(P.CONTRATOS.read_text(encoding="utf-8"))["FONTES"]}


def linhas_do_plano(*, canario: bool) -> list[dict]:
    """As linhas de `plano_onda_social.plano()`; com `canario`, as SCRAP_FASE em CANARY_PENDING entram."""
    import plano_onda_social as P                                   # noqa: PLC0415
    import lifecycle as LC                                          # noqa: PLC0415
    linhas = P.plano()["LINHAS"]
    for l in linhas:
        l["NA_ONDA_PORQUE"] = "PORTAO_ELIGIBLE" if l["NA_ONDA"] else None
        if canario and not l["NA_ONDA"] and l.get("ESTADO") == LC.CANARY_PENDING \
                and all(f.startswith("PORTAO:") for f in l["FALTA"]):
            l["NA_ONDA"], l["NA_ONDA_PORQUE"] = True, "CANARIO_SOCIAL (CANARY_PENDING, rota do Scrap)"
    return linhas


def escolher(linhas: list[dict], so: list[str] | None) -> list[dict]:
    if so is None:
        return linhas
    if not so:
        raise SystemExit("--fontes vazio: nenhuma fonte escolhida")
    conhecidas = {l["SOURCE_ID"] for l in linhas}
    fora = [s for s in so if s not in conhecidas]
    if fora:
        raise SystemExit("FONTE_FORA_DO_PLANO_SOCIAL: %s" % ",".join(fora))
    return [dict(l, NA_ONDA=l["NA_ONDA"] and l["SOURCE_ID"] in so) for l in linhas]


def plano(*, canario: bool, so: list[str] | None, linhas: list[dict] | None = None) -> dict:
    import plano_onda_social as P                                   # noqa: PLC0415
    linhas = escolher(linhas if linhas is not None else linhas_do_plano(canario=canario), so)
    rod = P.rodadas(linhas)
    return {"DATASET": "MAESTRO-SOCIAL-PLANO", "GERADO_EM": agora(), "CANARIO": canario, "SO_AS_FONTES": so,
            "TETO_POR_DOMINIO_NA_ONDA": TETO, "TETO_LINKEDIN_NO_PEDIDO": P.TETO_LINKEDIN_NA_ONDA,
            "ONDAS": len(rod), "TODAS_CABEM": all(r["CABE_NO_TETO"] for r in rod),
            "FORA_DA_ONDA": sorted(l["SOURCE_ID"] for l in linhas if not l["NA_ONDA"]),
            "RODADAS": rod}


# ── uma fonte (a unica parte com rede) ───────────────────────────────────────
def pedido_da_fonte(c: dict, video: str | None):
    """O Pedido desta fonte. YouTube sem chave: `audio-youtube` do video dado; sem video: None."""
    import plano_onda_social as P                                   # noqa: PLC0415
    from pedido import Pedido                                       # noqa: PLC0415
    aq = c["ACQUISITION"]
    if aq.get("FASE") == "canal-youtube" and not os.environ.get(ENV_CHAVE_YT):
        if not video:
            return None
        return Pedido(alvo=c["TERRITORY"], filtros={"fase": "audio-youtube", "fonte": c["SOURCE_ID"],
                                                    "video": video, "pais": "IT", "universo": c["TERRITORY"]})
    return P.pedido_de(c)


PROG = r"""
import json, sys
sys.path[:0] = [%(raiz)r, %(orq)r]
import _gavetas, orquestrador as O, persistencia
from pedido import Pedido
p = Pedido(alvo=%(alvo)r, filtros=%(filtros)r)
rt = persistencia.dependencias_do_runtime()
r = O.correr(p, memoria=rt.memoria, banco_do_rastro=rt.banco_do_rastro, raiz_do_armazem=rt.raiz_do_armazem)
r.pop('_plano', None)
open(%(recibo)r, 'w', encoding='utf-8').write(json.dumps(r, ensure_ascii=False, default=str, indent=1))
print('MAESTRO_RECIBO', r.get('STATUS'), r.get('RUN_ID'))
"""


def lancar_pelo_orquestrador(sid: str, pedido, pasta: Path) -> dict:
    """Corre UMA fonte pelo orquestrador (D28), noutro processo (o livro da onda vai no ambiente)."""
    pasta.mkdir(parents=True, exist_ok=True)
    recibo = pasta / "RECIBO.json"
    prog = PROG % {"raiz": str(RAIZ), "orq": str(RAIZ / "orquestrador"), "alvo": pedido.alvo,
                   "filtros": dict(pedido.filtros), "recibo": str(recibo)}
    x = subprocess.run([sys.executable, "-c", prog], cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=LIMITE_S + 60)
    (pasta / "SAIDA.txt").write_text((x.stdout or "") + "\n---STDERR---\n" + (x.stderr or ""), encoding="utf-8")
    r = json.loads(recibo.read_text(encoding="utf-8")) if recibo.exists() else {}
    return {"STATUS": r.get("STATUS") or "NAO_SEI", "RUN_ID": r.get("RUN_ID"), "CODIGO": x.returncode}


def linha_do_livro(run_id: str | None) -> dict:
    if not run_id or not ledger().exists():
        return {}
    for l in reversed(ledger().read_text(encoding="utf-8").splitlines()):
        try:
            x = json.loads(l)
        except ValueError:
            continue
        if x.get("RUN_ID") == run_id:
            return x
    return {}


def prova_teto(run_ids: list[str]) -> dict:
    import prova_teto_dominio as PT                                 # noqa: PLC0415
    with open(ledger(), encoding="utf-8") if ledger().exists() else open(os.devnull) as f:
        return PT.verificar(run_ids, PT.ler_livro(f), TETO)


def ler_livro_da_onda(livro: Path) -> dict:
    if not livro.exists():
        return {}
    return json.loads(livro.read_text(encoding="utf-8"))["PEDIDOS_POR_DOMINIO"]


def egresso_do_dono() -> dict:
    import micro_coleta as M                                        # noqa: PLC0415
    return M.medir_egresso()


def precondicoes_do_dono() -> list[str]:
    import micro_coleta as M                                        # noqa: PLC0415
    return M.precondicoes()


def gate_no_instante(sid: str) -> str:
    import collection_gate as GATE                                  # noqa: PLC0415
    return GATE.avaliar(sid, **GATE._contexto()).get("MOTIVO")


# ── correr a rodada ──────────────────────────────────────────────────────────
def correr(saida: Path, *, canario: bool = False, so: list[str] | None = None, videos: dict | None = None,
           retomar: bool = False, egresso=egresso_do_dono, lancar=lancar_pelo_orquestrador,
           precondicoes=precondicoes_do_dono, gate=gate_no_instante, prova=prova_teto,
           contratos_fn=contratos, plano_fn=None) -> int:
    videos = videos or {}
    falta = precondicoes()
    if falta:
        print("PRECONDICOES", falta)
        return 2
    saida.mkdir(parents=True, exist_ok=True)
    caminho = saida / ESTADO
    if retomar:
        estado = json.loads(caminho.read_text(encoding="utf-8"))
        estado["RETOMADAS"] = estado.get("RETOMADAS", []) + [{"QUANDO": agora(), "PAROU_ANTES": estado.get("PAROU")}]
        estado["PAROU"] = None
    else:
        if caminho.exists():
            raise SystemExit("ESTADO_JA_EXISTE: %s — rodada nova tem pasta nova; para continuar, --retomar" % caminho)
        p = (plano_fn or (lambda: plano(canario=canario, so=so)))()
        if not p["TODAS_CABEM"]:
            raise SystemExit("PLANO_NAO_CABE_NO_TETO: %s" % [r["ONDA"] for r in p["RODADAS"] if not r["CABE_NO_TETO"]])
        estado = {"DATASET": "MAESTRO-SOCIAL-ESTADO", "INICIO": agora(), "CANARIO": canario, "SO_AS_FONTES": so,
                  "VIDEOS": videos, "PLANO": p, "ONDAS": [], "FONTES": [], "PAROU": None}

    def grava():
        caminho.write_text(json.dumps(estado, ensure_ascii=False, indent=1, default=str), encoding="utf-8")

    def parar(porque, fonte=None):
        estado["PAROU"] = {"FONTE": fonte, "PORQUE": porque, "QUANDO": agora()}
        grava()
        try:
            with open(AVISO, "a", encoding="utf-8") as f:
                f.write("\nMAESTRO-SOCIAL -> COORDENADOR (%s): PAROU em %s: %s\n" % (agora(), fonte, porque))
        except OSError:
            pass
        print("PAROU", porque, flush=True)
        return 1

    cont = contratos_fn()
    feitas = {f["SOURCE_ID"] for f in estado["FONTES"]}
    ondas_feitas = {o["ONDA"] for o in estado["ONDAS"] if o.get("PROVA_TETO", {}).get("ESTADO") == "PASS"}
    falhas_seguidas = 0
    for rod in estado["PLANO"]["RODADAS"]:
        n = rod["ONDA"]
        if n in ondas_feitas:
            continue
        livro = saida / ("ONDA-%02d" % n) / "TETO-ONDA.json"
        livro.parent.mkdir(parents=True, exist_ok=True)
        os.environ["SINTONIA_TETO_ONDA"] = str(livro)       # herdado: orquestrador -> scrap -> yt-dlp com freio
        for sid in rod["LINKEDIN"] + rod["YOUTUBE"]:
            if sid in feitas:
                continue
            c = cont[sid]
            pedido = pedido_da_fonte(c, videos.get(sid))
            linha = {"ONDA": n, "SOURCE_ID": sid, "FASE": (c.get("ACQUISITION") or {}).get("FASE"),
                     "INICIO": agora(), "CORREU": False}
            if pedido is None:
                linha["PORQUE_NAO_CORREU"] = "SEM_VIDEO_E_SEM_CHAVE"
                estado["FONTES"].append(linha)
                feitas.add(sid)
                grava()
                print("%02d %s SEM_VIDEO_E_SEM_CHAVE" % (n, sid), flush=True)
                continue                                   # nao e FAILED
            antes = egresso()
            if antes.get("PAIS") != "IT":
                return parar("EGRESSO_NAO_IT antes da fonte: %s" % antes.get("PAIS"), sid)
            g = gate(sid)
            t0 = time.time()
            r = lancar(sid, pedido, saida / ("ONDA-%02d" % n) / sid)
            seg = round(time.time() - t0)
            depois = egresso()
            cort = (linha_do_livro(r.get("RUN_ID")).get("CORTESIA") or {})
            livro_agora = ler_livro_da_onda(livro)
            linha.update({"FASE_DO_PEDIDO": pedido.filtros.get("fase"), "FILTROS": dict(pedido.filtros),
                          "CORREU": True, "STATUS": r.get("STATUS"), "RUN_ID": r.get("RUN_ID"),
                          "CODIGO": r.get("CODIGO"), "SEGUNDOS": seg, "GATE": g,
                          "EGRESSO": [antes.get("PAIS"), depois.get("PAIS")],
                          "PEDIDOS_POR_HOST": cort.get("PEDIDOS_POR_HOST"),
                          "PEDIDOS_NAO_CONTADOS": cort.get("PEDIDOS_NAO_CONTADOS"),
                          "RECUSAS_DO_FREIO": cort.get("RECUSAS") or [], "LIVRO_DA_ONDA": livro_agora})
            estado["FONTES"].append(linha)
            feitas.add(sid)
            grava()
            print("%02d %s %s %ss livro %s" % (n, sid, linha["STATUS"], seg, livro_agora), flush=True)
            if depois.get("PAIS") != "IT":
                return parar("EGRESSO_SAIU_DE_IT depois da fonte: %s" % depois.get("PAIS"), sid)
            if seg > LIMITE_S:
                return parar("CORRIDA_MAIS_DE_30_MIN", sid)
            acima = {d: v for d, v in livro_agora.items() if v > TETO}
            if acima:
                return parar("LIVRO_DA_ONDA_ACIMA_DO_TETO %s" % acima, sid)
            falhas_seguidas = falhas_seguidas + 1 if linha["STATUS"] == "FAILED" else 0
            if falhas_seguidas >= 3:
                return parar("TRES_FONTES_SEGUIDAS_FAILED", sid)
        run_ids = [f["RUN_ID"] for f in estado["FONTES"] if f.get("ONDA") == n and f.get("RUN_ID")]
        pt = prova(run_ids) if run_ids else {"ESTADO": "PASS", "NOTA": "nenhuma corrida nesta onda (nada saiu)"}
        estado["ONDAS"] = [o for o in estado["ONDAS"] if o["ONDA"] != n] + [
            {"ONDA": n, "LIVRO": str(livro), "LIVRO_NO_FIM": ler_livro_da_onda(livro), "RUN_IDS": run_ids,
             "PROVA_TETO": {k: pt.get(k) for k in ("ESTADO", "PEDIDOS_POR_DOMINIO", "DOMINIOS_ACIMA_DO_TETO",
                                                     "CORRIDAS_SEM_LINHA_NO_LIVRO", "CORRIDAS_SEM_PEDIDOS_POR_HOST",
                                                     "NOTA")}}]
        grava()
        print("ONDA %02d PROVA_TETO=%s" % (n, pt.get("ESTADO")), flush=True)
        if pt.get("ESTADO") != "PASS":
            return parar("PROVA_TETO_%s na onda %d" % (pt.get("ESTADO"), n))
    estado["FIM"] = agora()
    grava()
    return 0


# ── relatorio (sem rede, sem Sala: le o estado) ──────────────────────────────
def relatorio(estado: dict) -> dict:
    fontes = estado.get("FONTES", [])
    ondas = estado.get("ONDAS", [])
    return {"DATASET": "MAESTRO-SOCIAL-RELATORIO", "CANARIO": estado.get("CANARIO"),
            "ONDAS_PLANEADAS": (estado.get("PLANO") or {}).get("ONDAS"), "ONDAS_FECHADAS": len(ondas),
            "PROVA_TETO_POR_ONDA": {o["ONDA"]: (o.get("PROVA_TETO") or {}).get("ESTADO") for o in ondas},
            "FONTES_CORRIDAS": sum(1 for f in fontes if f.get("CORREU")),
            "FONTES_SEM_VIDEO_E_SEM_CHAVE": [f["SOURCE_ID"] for f in fontes
                                             if f.get("PORQUE_NAO_CORREU") == "SEM_VIDEO_E_SEM_CHAVE"],
            "POR_STATUS": _contar(f.get("STATUS") for f in fontes if f.get("CORREU")),
            "EGRESSO_SEMPRE_IT": all(f.get("EGRESSO") == ["IT", "IT"] for f in fontes if f.get("CORREU")),
            "RECUSAS_DO_FREIO": sum(len(f.get("RECUSAS_DO_FREIO") or []) for f in fontes),
            "RETOMADAS": len(estado.get("RETOMADAS", [])), "PAROU": estado.get("PAROU"),
            "TERMINOU": bool(estado.get("FIM"))}


def _contar(it):
    c = {}
    for x in it:
        c[x] = c.get(x, 0) + 1
    return c


def relatorio_md(r: dict) -> str:
    linhas = ["# MAESTRO SOCIAL — relatorio da rodada", ""]
    for k in ("CANARIO", "ONDAS_PLANEADAS", "ONDAS_FECHADAS", "PROVA_TETO_POR_ONDA", "FONTES_CORRIDAS",
              "POR_STATUS", "EGRESSO_SEMPRE_IT", "RECUSAS_DO_FREIO", "FONTES_SEM_VIDEO_E_SEM_CHAVE",
              "RETOMADAS", "PAROU", "TERMINOU"):
        linhas.append("- **%s**: %s" % (k, json.dumps(r.get(k), ensure_ascii=False)))
    return "\n".join(linhas) + "\n"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    so = [x.strip() for x in arg["fontes"].split(",") if x.strip()] if "fontes" in arg else None
    videos = dict(x.split(":", 1) for x in arg.get("videos", "").split(",") if ":" in x)
    saida = Path(arg["saida"]) if arg.get("saida") else None
    canario = "--canario" in argv
    if "--so-plano" in argv:
        p = plano(canario=canario, so=so)
        if saida:
            saida.mkdir(parents=True, exist_ok=True)
            (saida / "MAESTRO-SOCIAL-PLANO.json").write_text(json.dumps(p, ensure_ascii=False, indent=1),
                                                             encoding="utf-8")
        print(json.dumps({k: v for k, v in p.items() if k != "RODADAS"}, ensure_ascii=False, indent=1))
        for r in p["RODADAS"]:
            print("  ONDA %02d  LI %s  YT %s  previsto %s" % (r["ONDA"], r["LINKEDIN"], r["YOUTUBE"],
                                                            r["PREVISTO_POR_DOMINIO"]))
        return 0
    if "--correr" in argv:
        if "--autorizado-pelo-dono" not in argv or not saida:
            raise SystemExit("--correr exige --autorizado-pelo-dono e --saida=<pasta da rodada>")
        return correr(saida, canario=canario, so=so, videos=videos, retomar="--retomar" in argv)
    if "--relatorio" in argv:
        if not arg.get("estado"):
            raise SystemExit("--relatorio exige --estado=<MAESTRO-SOCIAL-ESTADO.json>")
        e = json.loads(Path(arg["estado"]).read_text(encoding="utf-8"))
        r = relatorio(e)
        destino = Path(arg["estado"]).with_name("MAESTRO-SOCIAL-RELATORIO.md")
        destino.write_text(relatorio_md(r), encoding="utf-8")
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0 if r["TERMINOU"] and not r["PAROU"] else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
