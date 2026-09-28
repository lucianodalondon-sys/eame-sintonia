#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PASSAGEM ARMAZEM -> SALA — toda coleta reconciliada atravessa a porta canonica, sozinha.

    MISSAO   ESTEIRA-SOZINHA (28/09/2026)
    QUEM CHAMA  o supervisor (`curadoria/supervisor.py::_hook_esteira`), a cada volta.

    python3 admissao/passagem_para_a_sala.py --plano     # so le: o que passaria, e o que fica, e porque

PORQUE A RODADA R03 DEU `raw +5 · derived +5 · sala +0` — MEDIDO NO CODIGO
--------------------------------------------------------------------------
A passagem NAO e um passo manual esquecido. Na rodada, a porta corre DENTRO da mesma corrida:
`orquestrador.correr()` -> RAW (`pela_entrada`) -> DERIVED -> STRUCTURED -> `pela_porta()`
(orquestrador.py:1169-1211), e `pela_porta` so pousa o que a Admissao disse `SIM`
(orquestrador.py:777-785). O +0 tem quatro causas possiveis, todas no codigo:

    A  universo SEM REGUA -> `NAO_SE_APLICA` sempre (admissao.py:859; a regua conhece
       T1 T2 T3 T4 T5 T7 T9 T10). A coorte congelada tem 13 fontes T8 e 6 T12, e o plano da
       4.a onda poe uma T8 (edagricole) em CADA rodada da 3 em diante — a Rodada 3 do plano e
       IT-T8-021 + IT-T7-135 (ORDEM-RENDIMENTO-ONDA4.md, «Rodada 3»): duas corridas, como o
       `collection_run +2` medido. `micro_coleta.plano` nao pergunta se o universo tem regua.
    B  veredito `NAO` / `NAO_SEI` (capa, uma palavra so, lingua sem regua).
    C  dedup da Sala: SIM, mas o documento ja la estava por outra corrida -> REUSED, 0 linhas.
    D  a corrida caiu no `pousar` (ConflitoDeCorrida, SalaIndisponivel): RAW ja gravado.
    Qual delas foi a R03: NAO SEI daqui — o livro de decisoes e o RELATORIO-PASSAGEM da rodada
    vivem na maquina do coordenador. `--plano` e o vigia dizem-no a partir de hoje.

O QUE ESTE PASSO FAZ, ENTAO
---------------------------
Garante que NENHUMA corrida reconciliada fica sem passar pela porta — as que cairam (D), as que
vieram por outro caminho (a tarefa ForwardOnly, o servico fonte-a-fonte da outra equipe, que
escrevem no mesmo livro de corridas) — e diz, corrida a corrida, porque uma nao passa.

    RECONCILIADA = fechada no livro das corridas (FINISHED_AT) E com observacoes no livro das
                   observacoes (o envelope refaz-se: `italy_executor.colher`, o dono).
    JA PASSOU    = o livro de decisoes da Admissao tem decisoes com `corrida` = RUN_ID (a porta
                   em linha da rodada), ou este passo ja a levou (PAS_PASSAGENS).

    A PORTA E A CANONICA: `orquestrador.py <apelido> --so-a-porta --colheita-da-corrida=<RUN_ID>`
    com o pedido montado por `micro_coleta.comando()` — o mesmo da rodada. Nenhum INSERT aqui.

AS TRAVAS
---------
    UM ESCRITOR   `sala_de_espera._Trava` sobre curadoria/ESTEIRA-PASSAGEM(.lock).
    BACKUP        `provar_backup_da_sala.provar` ANTES de gravar; sem PROVA_VALE nao se grava nada.
    PARAR         `curadoria/PARAR.flag` antes de tudo e entre corridas.
    PRECONDICOES  `micro_coleta.precondicoes()`: Sala POSTGRES, DSN, psql, armazem.
    PASSADO       na primeira volta grava-se PAS_DESDE = agora: o historico nao atravessa sozinho
                  (59 corridas no livro do repo). Levar o passado e decisao do coordenador:
                  `--desde=AAAA-MM-DDTHH:MM:SSZ`.
    NAO SE PASSA  universo sem regua (A: seria NAO_SE_APLICA garantido) e corrida com varias
                  fontes (a porta pergunta UM universo por corrida; julgar um T3 como T7 escreveria
                  um NAO falso no livro). Ficam a vista, com o porque.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

import admissao as adm                           # noqa: E402 — a regua (PERGUNTAS_DO_UNIVERSO)
import sala_de_espera as espera                  # noqa: E402 — dono da trava

CURADORIA = RAIZ / "curadoria"
PARAR = CURADORIA / "PARAR.flag"
TRINCO = CURADORIA / "ESTEIRA-PASSAGEM"
PASTA = CURADORIA / "esteira" / "passagem"
LIVRO_DAS_CORRIDAS = Path("data") / "collection-ledger" / "italy" / "runs.ndjson"
ASSENTAR = timedelta(minutes=2)          # corrida fechada ha menos disto pode ainda estar a escrever
INTERVALO = timedelta(minutes=5)
RECUO = timedelta(minutes=30)
GUARDAR_PASSAGENS = 500

(PASSAR, JA_PASSOU, SEM_OBSERVACOES, VARIAS_FONTES, SEM_REGUA, ABERTA, ANTES_DO_DESDE) = (
    "PASSAR", "JA_PASSOU_PELA_PORTA", "SEM_OBSERVACOES", "VARIAS_FONTES",
    "SEM_REGUA_NO_UNIVERSO", "AINDA_ABERTA", "ANTES_DO_DESDE")


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _quando(v) -> datetime | None:
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _mc():
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    import micro_coleta as MC                                   # noqa: PLC0415
    return MC


def raizes_dos_livros() -> list[Path]:
    """A arvore, e a raiz de operacao se for outra (a tarefa ForwardOnly escreve la)."""
    out = [RAIZ]
    ops = os.environ.get("ITALY_OPS_ROOT")
    if ops and Path(ops).resolve() != RAIZ.resolve():
        out.append(Path(ops))
    return out


def corridas_do_livro(raizes: list[Path]) -> list[dict]:
    vistas, out = set(), []
    for r in raizes:
        p = r / LIVRO_DAS_CORRIDAS
        if not p.exists():
            continue
        for linha in p.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                x = json.loads(linha)
            except ValueError:
                continue                       # linha partida no fim de um livro append-only
            run = x.get("RUN_ID") if isinstance(x, dict) else None
            if run and run not in vistas:
                vistas.add(run)
                out.append({"RUN_ID": run, "FINISHED_AT": x.get("FINISHED_AT"), "RAIZ": str(r)})
    return out


def ja_julgadas(livro: Path = adm.LIVRO) -> set:
    if not livro.exists():
        return set()
    return {d.get("corrida") for d in json.loads(livro.read_text(encoding="utf-8")).get("DECISOES", [])}


def _observacoes(run_id: str, raiz: str) -> list:
    from coleta import italy_executor as ix                      # noqa: PLC0415
    return ix.observacoes_da_corrida(run_id, raiz)


def planear(estado: dict, agora: datetime, raizes: list[Path] | None = None,
            livro: Path = adm.LIVRO, observacoes=None) -> dict:
    """So le. -> {"PASSAR": [...], "FICA": [...]} com o porque de cada uma."""
    MC = _mc()
    observacoes = observacoes or _observacoes
    desde = _quando(estado.get("PAS_DESDE"))
    feitas = estado.get("PAS_PASSAGENS") or {}
    julgadas = ja_julgadas(livro)
    passar, fica = [], []
    for c in corridas_do_livro(raizes or raizes_dos_livros()):
        run, fim = c["RUN_ID"], _quando(c["FINISHED_AT"])
        if run in feitas:
            continue
        if fim is None or agora - fim < ASSENTAR:
            fica.append({**c, "PORQUE": ABERTA})
            continue
        if desde and fim < desde:
            continue                                   # o passado nao se conta a cada volta
        if run in julgadas:
            fica.append({**c, "PORQUE": JA_PASSOU})
            continue
        fontes = sorted({o.get("SOURCE_ID") for o in observacoes(run, c["RAIZ"]) if o.get("SOURCE_ID")})
        if not fontes:
            fica.append({**c, "PORQUE": SEM_OBSERVACOES})
        elif len(fontes) > 1:
            fica.append({**c, "PORQUE": VARIAS_FONTES, "FONTES": fontes})
        else:
            u = MC.universo_de(fontes[0])
            if u not in adm.PERGUNTAS_DO_UNIVERSO:
                fica.append({**c, "PORQUE": SEM_REGUA, "FONTE": fontes[0], "UNIVERSO": u})
            else:
                passar.append({**c, "PORQUE": PASSAR, "FONTE": fontes[0], "UNIVERSO": u})
    return {"PASSAR": passar, "FICA": fica}


def backup_padrao(pasta: Path) -> dict:
    sys.path.insert(0, str(RAIZ / "scripts" / "micro_coleta"))
    import provar_backup_da_sala as PB                          # noqa: PLC0415
    return PB.provar(os.environ["SINTONIA_SALA_DSN"], pasta, ler_real_do_ficheiro=False)


def lancar_padrao(cmd: list) -> dict:
    x = subprocess.run(cmd, cwd=str(RAIZ), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=1800)
    return {"CODIGO": x.returncode, "SAIDA": x.stdout[-4000:], "ERRO": x.stderr[-1500:]}


def passar_uma(linha: dict, lancar=None, livro: Path = adm.LIVRO) -> dict:
    """O envelope refeito pelo dono, e a porta canonica sobre ele. -> o recibo desta passagem."""
    from coleta import italy_executor as ix                      # noqa: PLC0415
    MC = _mc()
    run = linha["RUN_ID"]
    balcao = ix.colher(run, ops_root=linha["RAIZ"], raiz=str(RAIZ))
    cmd = MC.comando(linha["FONTE"]) + ["--so-a-porta", "--colheita-da-corrida=%s" % run]
    r = (lancar or lancar_padrao)(cmd)
    m = re.search(r"CORRIDA (\S+) · (\S+)", r.get("SAIDA", ""))
    nova = m.group(2) if m else None
    conta = {}
    if nova and livro.exists():
        for d in json.loads(livro.read_text(encoding="utf-8")).get("DECISOES", []):
            if d.get("corrida") == nova:
                conta[d["resultado"]] = conta.get(d["resultado"], 0) + 1
    return {"COLHEITA_DA_CORRIDA": run, "FONTE": linha["FONTE"], "UNIVERSO": linha["UNIVERSO"],
            "OBSERVACOES": balcao.get("OBSERVACOES_DESTA_CORRIDA"), "CODIGO": r.get("CODIGO"),
            "STATUS": m.group(1) if m else "NAO SEI", "CORRIDA_DA_PORTA": nova or "NAO SEI",
            "POR_RESULTADO": conta, "ERRO": (r.get("ERRO") or "")[-300:]}


def passar_se_devido(estado: dict, *, agora: datetime | None = None, raizes=None, livro: Path = adm.LIVRO,
                     observacoes=None, backup=None, lancar=None, precondicoes=None,
                     parar: Path = PARAR, trinco: Path = TRINCO, pasta: Path = PASTA,
                     forcar: bool = False) -> dict:
    """Uma volta da passagem. Devolve o que fez; guarda em `estado` as marcas (PAS_*)."""
    agora = agora or _agora()
    if parar.exists():
        return {"ACCAO": "PARAR_FLAG"}
    estado.setdefault("PAS_DESDE", agora.isoformat())
    visto = _quando(estado.get("PAS_VERIFICADO_EM"))
    if not forcar and visto and agora - visto < INTERVALO:
        return {"ACCAO": "NADA"}
    estado["PAS_VERIFICADO_EM"] = agora.isoformat()
    falhou = _quando(estado.get("PAS_ULTIMA_FALHA_EM"))
    if not forcar and falhou and agora - falhou < RECUO:
        return {"ACCAO": "RECUO_DEPOIS_DE_FALHA", "ABRE_EM": (falhou + RECUO).isoformat()}
    try:
        plano = planear(estado, agora, raizes, livro, observacoes)
    except Exception as e:  # noqa: BLE001
        return {"ACCAO": "NAO_SEI", "PORQUE": "plano nao lido: %s" % repr(e)[:200]}
    porques = {}
    for f in plano["FICA"]:
        porques[f["PORQUE"]] = porques.get(f["PORQUE"], 0) + 1
    estado["PAS_ULTIMO_PLANO"] = {"EM": agora.isoformat(), "PASSAR": len(plano["PASSAR"]),
                                  "FICA_POR_PORQUE": porques,
                                  "SEM_REGUA": [(f["RUN_ID"], f["FONTE"], f["UNIVERSO"])
                                                for f in plano["FICA"] if f["PORQUE"] == SEM_REGUA][-20:]}
    if not plano["PASSAR"]:
        return {"ACCAO": "NADA_A_PASSAR", "FICA_POR_PORQUE": porques}
    falta = (precondicoes or _mc().precondicoes)()
    if falta:
        return {"ACCAO": "PRECONDICOES", "FALTA": falta}
    try:
        with espera._Trava(str(trinco)):
            b = (backup or backup_padrao)(pasta / agora.strftime("%Y%m%dT%H%M%SZ") / "backup")
            if not b.get("PROVA_VALE"):
                estado["PAS_ULTIMA_FALHA_EM"] = agora.isoformat()
                return {"ACCAO": "BACKUP_NAO_VALE", "PORQUE": "sem PROVA_VALE nao se grava na Sala",
                        "PENDENTES": len(plano["PASSAR"])}
            feitas = estado.setdefault("PAS_PASSAGENS", {})
            recibos = []
            for linha in plano["PASSAR"]:
                if parar.exists():
                    break
                r = passar_uma(linha, lancar, livro)
                r["EM"] = agora.isoformat()
                feitas[linha["RUN_ID"]] = r
                recibos.append(r)
            for velho in list(feitas)[:-GUARDAR_PASSAGENS]:
                del feitas[velho]
            estado["PAS_ULTIMA_PASSAGEM_EM"] = agora.isoformat()
            return {"ACCAO": "PASSOU", "BACKUP": b.get("DUMP"), "CORRIDAS": recibos,
                    "PARADO_POR_FLAG": parar.exists()}
    except espera.EsperaOcupada:
        return {"ACCAO": "OCUPADO", "PORQUE": "outra passagem esta a escrever"}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--plano" not in argv:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 admissao/passagem_para_a_sala.py --plano [--desde=ISO]   (so le)")
        return 2
    desde = next((a.split("=", 1)[1] for a in argv if a.startswith("--desde=")), None)
    p = planear({"PAS_DESDE": desde} if desde else {}, _agora())
    for x in p["PASSAR"]:
        print("PASSA  %s  %s %s" % (x["RUN_ID"], x["FONTE"], x["UNIVERSO"]))
    for x in p["FICA"]:
        print("FICA   %s  %s %s" % (x["RUN_ID"], x["PORQUE"], x.get("FONTE") or x.get("FONTES") or ""))
    print("PASSA=%d FICA=%d" % (len(p["PASSAR"]), len(p["FICA"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
