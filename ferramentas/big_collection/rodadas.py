# -*- coding: utf-8 -*-
"""O DISPARADOR DE RODADAS — a onda que nao cabe no teto, corrida em rodadas, UMA A UMA.

    py ferramentas/big_collection/rodadas.py --so-plano --base=<pasta> [--historico=a.json,b.json] [--teto-dia=N]
    py ferramentas/big_collection/rodadas.py --correr --sha256=<da coorte congelada> --base=<pasta>
          [--historico=...] [--rodada=N] [--teto-dia=N] [--livros-do-dia=<pasta das ondas>] [--sem-janela-24h]

Porque existe (C2-ONDA4, 26/09/2026): na 3.a onda 26 de 64 fontes ficaram de fora por
TETO_DOMINIO — edagricole.it sozinho tem 15 fontes, e o teto (D38) e 5 pedidos por dominio POR
ONDA. Para visitar todas, cada rodada tem de ser uma onda PROPRIA: pasta nova, livro do teto novo.
Isto fazia-se a mao, 15 comandos `onda_web.py --correr --fontes=...`. Este ficheiro e esse laco,
com as guardas que a mao esquecia:

  1. O PLANO: a coorte oficial pela ordem justa do `onda_web` (quem nunca foi atendido primeiro),
     partida em rodadas em que nenhum dominio passa de 5 pedidos PREVISTOS. Previsto = o maximo
     medido nas ondas do --historico; sem medida, o teto inteiro. Gravado uma vez em
     `<base>/RODADAS-PLANO.json`, com o sha256 da coorte: uma retoma com outra coorte recusa.
  2. POR RODADA, sempre nesta ordem:
       portao de egresso IT (consenso) ANTES  -> falha: PARA sem pedir nada
       teto DIARIO (so com --teto-dia)        -> fontes cujo dominio passaria o teto do dia ficam ADIADAS
       a onda: `onda_web.py --correr --fontes=<as da rodada> --saida=<base>/RODADA-NN`
       portao de egresso IT DEPOIS            -> falha: PARA
       PROVA-TETO (`provas/prova_teto_dominio.py`, o mesmo codigo, importado) -> so PASS fecha a
                                                 rodada; FAIL (>5) ou NAO_SEI: PARA TUDO
       relatorio do runbook: `micro_coleta.py relatorio --estado=<RODADA-NN>/ONDA-WEB-ESTADO.json`
  3. RETOMA: `<base>/RODADAS-ESTADO.json` diz que rodadas FECHARAM. Correr de novo comeca na
     primeira que nao fechou; uma rodada PARADA a meio retoma a MESMA onda (`--retomar`, o mesmo
     livro do teto: os pedidos ja feitos continuam a contar).
  4. JANELA MOVEL DE 24 H POR DOMINIO (D79, ligada por omissao; --sem-janela-24h desliga): uma rodada
     so corre quando TODOS os seus dominios estao ha mais de 24 h sem pedido, lido dos livros (a
     hora de cada corrida vem do RUN_ID). Senao PARA com ABRE_EM.
  5. --teto-dia=N (opcional): soma os `TETO-ONDA.json` de HOJE em --livros-do-dia (por omissao, a
     pasta-mae de --base). Sem ele, nada muda em relacao ao `onda_web` de hoje.

    UMA RODADA SO FECHA COM A PROVA INDEPENDENTE. O CONTADOR QUE CORTA NAO E O QUE CONFERE.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, date, timedelta, timezone
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "provas"))
import prova_teto_dominio as PT                                    # noqa: E402 — um so dono da prova

TETO = PT.TETO_D38
ONDA_WEB = RAIZ / "ferramentas" / "big_collection" / "onda_web.py"
PLANO_F = "RODADAS-PLANO.json"
ESTADO_F = "RODADAS-ESTADO.json"


def agora() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


# ── 1. o plano (puro) ────────────────────────────────────────────────────────
def pedidos_medidos(estados: list[dict]) -> dict:
    """SOURCE_ID -> o maximo de pedidos que a fonte fez numa corrida das ondas dadas."""
    out = {}
    for e in estados:
        for f in e.get("FONTES", []):
            if f.get("CORREU"):
                n = sum((f.get("PEDIDOS_POR_DOMINIO") or f.get("PEDIDOS_POR_SITE") or {}).values())
                out[f["SOURCE_ID"]] = max(out.get(f["SOURCE_ID"], 0), n)
    return out


def planear(linhas: list[dict], medidos: dict, teto: int = TETO) -> list[dict]:
    """Parte as fontes (ja na ordem justa) em rodadas: nenhum dominio passa de `teto` previstos
    numa rodada. Dentro de um dominio a ordem mantem-se; dominios diferentes nao se atrasam uns aos outros."""
    rodadas: list[list[dict]] = []
    onde = {}                                   # dominio -> (rodada actual, gasto nela)
    for l in linhas:
        d, s = l["DOMINIO"], l["SOURCE_ID"]
        p = max(1, min(teto, medidos.get(s) or l.get("PEDIDOS_PREVISTOS") or teto))
        r, gasto = onde.get(d, (0, 0))
        if gasto + p > teto:
            r, gasto = r + 1, 0
        while len(rodadas) <= r:
            rodadas.append([])
        rodadas[r].append({"SOURCE_ID": s, "DOMINIO": d, "PREVISTOS": p,
                           "PREVISAO_VEM_DE": "medido" if medidos.get(s) else "teto/1.a onda"})
        onde[d] = (r, gasto + p)
    out = []
    for i, fs in enumerate(rodadas, 1):
        por_dom = {}
        for f in fs:
            por_dom[f["DOMINIO"]] = por_dom.get(f["DOMINIO"], 0) + f["PREVISTOS"]
        out.append({"RODADA": i, "FONTES": fs, "PEDIDOS_PREVISTOS_POR_DOMINIO": por_dom,
                    "PEDIDOS_PREVISTOS": sum(por_dom.values()), "MAXIMO_POR_DOMINIO": max(por_dom.values())})
    return out


# ── 2. o teto do dia (so leitura dos livros) ─────────────────────────────────
def gasto_do_dia(raiz: Path, hoje: date | None = None) -> dict:
    """Soma os PEDIDOS_POR_DOMINIO de todos os TETO-ONDA.json escritos HOJE debaixo de `raiz`."""
    hoje = hoje or date.today()
    out = {}
    for f in sorted(Path(raiz).glob("**/TETO-ONDA.json")):
        if date.fromtimestamp(f.stat().st_mtime) != hoje:
            continue
        for d, n in json.loads(f.read_text(encoding="utf-8"))["PEDIDOS_POR_DOMINIO"].items():  # ilegivel rebenta
            out[d] = out.get(d, 0) + int(n)
    return out


def filtrar_pelo_dia(fontes: list[dict], gasto: dict, teto_dia: int | None) -> tuple:
    """(correm, adiadas). Sem teto diario, correm todas."""
    if teto_dia is None:
        return list(fontes), []
    ja, correm, adiadas = dict(gasto), [], []
    for f in fontes:
        d = f["DOMINIO"]
        if ja.get(d, 0) + f["PREVISTOS"] > teto_dia:
            adiadas.append(dict(f, PORQUE="TETO_DIA", GASTO_HOJE=ja.get(d, 0)))
        else:
            correm.append(f)
            ja[d] = ja.get(d, 0) + f["PREVISTOS"]
    return correm, adiadas


# ── 2b. a janela movel de 24 h por dominio (D79, 26/09/2026) ─────────────────
# «1 rodada por janela movel de 24 h»: um dominio visitado ha menos de 24 h nao volta a ser pedido.
# A hora vem de cada corrida: o RUN_ID traz o instante em UTC (IT-Tn-AAAA-MM-DD-HHMMSS-...), lido do
# ONDA-WEB-ESTADO.json ao lado de cada TETO-ONDA.json. Sem estado, vale a hora do livro (a ultima
# escrita) para todos os dominios dele. O RUN_ID marca o INICIO da corrida; soma-se SEGUNDOS (a duracao
# que o onda_web regista) para a janela contar do fim. Sem SEGUNDOS, conta do inicio: ate ~1 min cedo.
RE_RUN_QUANDO = re.compile(r"-(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(\d{2})-[0-9a-f]{16}$")


def ultima_visita_por_dominio(raiz: Path) -> dict:
    """dominio -> instante (UTC) da ultima corrida que lhe fez >= 1 pedido, em qualquer onda debaixo de `raiz`."""
    out = {}

    def marca(d, t):
        if d and (d not in out or t > out[d]):
            out[d] = t
    for livro in sorted(Path(raiz).glob("**/TETO-ONDA.json")):
        gastos = json.loads(livro.read_text(encoding="utf-8"))["PEDIDOS_POR_DOMINIO"]     # ilegivel rebenta
        visto = set()
        est = livro.parent / "ONDA-WEB-ESTADO.json"
        if est.exists():
            for f in json.loads(est.read_text(encoding="utf-8")).get("FONTES", []):
                m = RE_RUN_QUANDO.search(f.get("RUN_ID") or "")
                if not m or not f.get("CORREU"):
                    continue
                # o RUN_ID e o INICIO da corrida; soma-se a duracao medida (SEGUNDOS) quando existe
                t = datetime(*map(int, m.groups()), tzinfo=timezone.utc) + timedelta(seconds=int(f.get("SEGUNDOS") or 0))
                for d in (f.get("PEDIDOS_POR_DOMINIO") or {f.get("DOMINIO"): 1}):
                    marca(PT.dominio_registavel(d), t)
                    visto.add(PT.dominio_registavel(d))
        t_livro = datetime.fromtimestamp(livro.stat().st_mtime, tz=timezone.utc)
        for d, n in gastos.items():
            if int(n) > 0 and PT.dominio_registavel(d) not in visto:
                marca(PT.dominio_registavel(d), t_livro)
    return out


def janela_fechada(fontes: list, ultima: dict, agora_utc: datetime, horas: int = 24) -> dict:
    """{dominio: instante em que volta a abrir} para os dominios da rodada visitados ha menos de `horas`."""
    out = {}
    for f in fontes:
        d = f["DOMINIO"]
        t = ultima.get(d)
        if t and agora_utc < t + timedelta(hours=horas):
            out[d] = (t + timedelta(hours=horas)).isoformat(timespec="seconds")
    return out


# ── 3. as pecas de fora (injectaveis: os testes trocam-nas, o CLI usa estas) ─
def portao_real() -> dict:
    r = subprocess.run([sys.executable, str(RAIZ / "superficie" / "rede.py"), "--portao-de-egresso", "IT",
                        "--sem-cache"], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", timeout=300)
    try:
        v = json.loads(r.stdout)
    except ValueError:
        v = {"SAIDA": r.stdout[-400:]}
    return {"PASSA": r.returncode == 0, "CODIGO": r.returncode, "PAIS": v.get("EGRESS_COUNTRY_CODE") or v.get("PAIS"),
            "EGRESS_GATE": v.get("EGRESS_GATE")}


def onda_real(sha: str, fontes: list[str], pasta: Path, historico: list[str], retomar: bool) -> int:
    cmd = [sys.executable, str(ONDA_WEB), "--correr", "--sha256=" + sha, "--fontes=" + ",".join(fontes),
           "--saida=" + str(pasta)]
    if historico:
        cmd.append("--historico=" + ",".join(historico))
    if retomar:
        cmd.append("--retomar")
    return subprocess.run(cmd, cwd=RAIZ).returncode


def relatorio_real(estado: Path, saida: Path) -> int:
    return subprocess.run([sys.executable, str(RAIZ / "scripts" / "micro_coleta" / "micro_coleta.py"), "relatorio",
                           "--estado=" + str(estado), "--saida=" + str(saida)], cwd=RAIZ,
                          capture_output=True, text=True, encoding="utf-8").returncode


def ledger_real() -> Path:
    import os
    return Path(os.environ.get("ITALY_OPS_ROOT") or RAIZ) / "data" / "collection-ledger" / "italy" / "runs.ndjson"


# ── 4. a prova de uma rodada (o codigo da PROVA-TETO, nao uma copia) ─────────
def provar_rodada(pasta: Path, ledger: Path, teto: int = TETO) -> dict:
    ids = PT.run_ids_da_onda((pasta / "ONDA-WEB-ESTADO.json").read_text(encoding="utf-8")
                             if (pasta / "ONDA-WEB-ESTADO.json").exists() else "")
    linhas = ledger.read_text(encoding="utf-8").splitlines() if ledger.exists() else []
    return PT.verificar(ids, PT.ler_livro(linhas), teto)


# ── 5. o laco ────────────────────────────────────────────────────────────────
def ler_estado(base: Path) -> dict:
    f = base / ESTADO_F
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"RODADAS": {}}


def gravar(base: Path, nome: str, doc: dict) -> None:
    (base / nome).write_text(json.dumps(doc, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def correr_rodadas(base: Path, sha: str, plano: dict, *, onda, portao, relatorio, ledger: Path,
                   historico: list[str] | None = None, rodada: int | None = None, teto_dia: int | None = None,
                   livros_do_dia: Path | None = None, hoje: date | None = None,
                   janela_h: int | None = None, agora_utc: datetime | None = None) -> dict:
    """Corre as rodadas por fechar (ou so `rodada`). Devolve o estado. Para na primeira que nao fecha."""
    if plano.get("COORTE_SHA256") != sha:
        raise SystemExit("PLANO_DE_OUTRA_COORTE: o plano em %s e da coorte %s, pedida %s"
                         % (base / PLANO_F, plano.get("COORTE_SHA256"), sha))
    estado = ler_estado(base)
    estado.update(BASE=str(base), COORTE_SHA256=sha, TETO_DIA=teto_dia, JANELA_H=janela_h)
    alvo = [r for r in plano["RODADAS"] if (rodada is None or r["RODADA"] == rodada)]
    if rodada is not None and not alvo:
        raise SystemExit("RODADA_INEXISTENTE: %s (o plano tem %d)" % (rodada, len(plano["RODADAS"])))
    for r in alvo:
        n = r["RODADA"]
        reg = estado["RODADAS"].get(str(n)) or {}
        if reg.get("ESTADO") == "FECHADA":
            continue                                             # retoma: o que fechou nao se repete
        pasta = base / ("RODADA-%02d" % n)
        # O que ja correu numa tentativa anterior desta rodada (INCOMPLETA) nao corre outra vez.
        feitas = list(reg.get("FEITAS") or [])
        reg = {"RODADA": n, "PASTA": str(pasta), "INICIO": agora(), "ESTADO": "A_CORRER", "FEITAS": feitas}
        estado["RODADAS"][str(n)] = reg

        def parar(porque, **extra):
            reg.update(ESTADO="PARADA", PORQUE=porque, FIM=agora(), **extra)
            estado["PAROU_NA_RODADA"] = n
            gravar(base, ESTADO_F, estado)
            return estado

        pendentes = [f for f in r["FONTES"] if f["SOURCE_ID"] not in feitas]
        if janela_h is not None:
            fecha = janela_fechada(pendentes, ultima_visita_por_dominio(livros_do_dia or base.parent),
                                   agora_utc or datetime.now(timezone.utc), janela_h)
            if fecha:
                return parar("JANELA_24H", DOMINIOS_NA_JANELA=fecha, ABRE_EM=max(fecha.values()),
                             NOTA="dominio visitado ha menos de %d h; a rodada corre inteira depois de ABRE_EM" % janela_h)
        antes = portao()
        reg["EGRESSO_ANTES"] = antes
        if not antes.get("PASSA"):
            return parar("EGRESSO_ANTES")
        correm, adiadas = filtrar_pelo_dia(pendentes, gasto_do_dia(livros_do_dia or base.parent, hoje)
                                           if teto_dia is not None else {}, teto_dia)
        reg["ADIADAS_TETO_DIA"] = adiadas
        if not correm:
            return parar("TETO_DIA", NOTA="todas as fontes da rodada passariam o teto do dia; retomar amanha")
        reg["FONTES"] = [f["SOURCE_ID"] for f in correm]
        retomar = (pasta / "TETO-ONDA.json").exists()
        reg["RETOMOU_A_MESMA_ONDA"] = retomar
        gravar(base, ESTADO_F, estado)
        reg["CODIGO_DA_ONDA"] = onda(sha, reg["FONTES"], pasta, list(historico or []), retomar)
        depois = portao()
        reg["EGRESSO_DEPOIS"] = depois
        if not depois.get("PASSA"):
            return parar("EGRESSO_DEPOIS")
        prova = provar_rodada(pasta, ledger)
        reg["PROVA_TETO"] = {k: prova[k] for k in ("ESTADO", "CORRIDAS_DA_ONDA", "PEDIDOS_NA_ONDA",
                                                   "DOMINIOS_ACIMA_DO_TETO", "CORRIDAS_SEM_LINHA_NO_LIVRO",
                                                   "CORRIDAS_SEM_PEDIDOS_POR_HOST")}
        if prova["ESTADO"] != "PASS":
            return parar("PROVA_TETO_" + prova["ESTADO"])
        if teto_dia is not None:
            dia = gasto_do_dia(livros_do_dia or base.parent, hoje)
            acima = {d: v for d, v in dia.items() if v > teto_dia}
            reg["GASTO_DO_DIA"] = dia
            if acima:
                return parar("TETO_DIA_ULTRAPASSADO", ACIMA=acima)
        if (pasta / "ONDA-WEB-ESTADO.json").exists():
            reg["CODIGO_DO_RELATORIO"] = relatorio(pasta / "ONDA-WEB-ESTADO.json", pasta / "relatorio")
        e = json.loads((pasta / "ONDA-WEB-ESTADO.json").read_text(encoding="utf-8")) \
            if (pasta / "ONDA-WEB-ESTADO.json").exists() else {}
        if reg["CODIGO_DA_ONDA"] != 0 or e.get("PAROU"):
            return parar("ONDA_PAROU", DISJUNTOR=e.get("PAROU"))
        reg["FEITAS"] = feitas + reg["FONTES"]
        if adiadas:                                              # nao se perde ninguem: a rodada fica por acabar
            reg.update(ESTADO="INCOMPLETA", PORQUE="TETO_DIA", FIM=agora(),
                       FALTAM=[a["SOURCE_ID"] for a in adiadas])
            estado["PAROU_NA_RODADA"] = n
            gravar(base, ESTADO_F, estado)
            return estado
        reg.update(ESTADO="FECHADA", FIM=agora())
        gravar(base, ESTADO_F, estado)
    estado["PAROU_NA_RODADA"] = None
    gravar(base, ESTADO_F, estado)
    return estado


# ── 6. o CLI ─────────────────────────────────────────────────────────────────
def plano_da_coorte(historico: list[str]) -> dict:
    sys.path.insert(0, str(ONDA_WEB.parent))
    import onda_web as OW                                          # noqa: E402
    sp = OW.so_plano(OW.COORTE_OFICIAL, None, historico)
    rodadas = planear(sp["LINHAS"], pedidos_medidos(OW.historicos(historico)))
    return {"DATASET": "RODADAS-PLANO", "GERADO_EM": agora(), "ARVORE": sp["ARVORE"],
            "COORTE_SHA256": sp["COORTE_SHA256_DO_COMMIT"], "COORTE_ESTADO": sp["COORTE_ESTADO"],
            "PODE_CORRER": sp["PODE_CORRER"], "TETO_POR_DOMINIO_POR_RODADA": TETO, "HISTORICO": historico,
            "FONTES": sum(len(r["FONTES"]) for r in rodadas), "N_RODADAS": len(rodadas),
            "PEDIDOS_PREVISTOS": sum(r["PEDIDOS_PREVISTOS"] for r in rodadas), "RODADAS": rodadas}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    if "base" not in arg:
        print(__doc__)
        return 2
    base = Path(arg["base"])
    historico = [x for x in arg.get("historico", "").split(",") if x]
    teto_dia = int(arg["teto-dia"]) if arg.get("teto-dia") else None
    # D79: a janela de 24 h por dominio e a regra; so se desliga dizendo-o.
    janela_h = None if "--sem-janela-24h" in argv else 24
    if "--so-plano" in argv:
        p = plano_da_coorte(historico)
        base.mkdir(parents=True, exist_ok=True)
        gravar(base, "RODADAS-SO-PLANO.json", p)
        if teto_dia is not None:
            p["GASTO_DO_DIA"] = gasto_do_dia(Path(arg.get("livros-do-dia") or base.parent))
        if janela_h is not None:
            ult = ultima_visita_por_dominio(Path(arg.get("livros-do-dia") or base.parent))
            agora_u = datetime.now(timezone.utc)
            for r in p["RODADAS"]:
                fecha = janela_fechada(r["FONTES"], ult, agora_u, janela_h)
                r["JANELA_24H"] = {"ABRE_EM": max(fecha.values()) if fecha else "ABERTA", "DOMINIOS": len(fecha)}
        print(json.dumps({k: v for k, v in p.items() if k != "RODADAS"}, ensure_ascii=False, indent=1))
        for r in p["RODADAS"]:
            print("RODADA %02d  %2d fontes  %3d pedidos  max/dominio %d  janela: %s" % (
                r["RODADA"], len(r["FONTES"]), r["PEDIDOS_PREVISTOS"], r["MAXIMO_POR_DOMINIO"],
                (r.get("JANELA_24H") or {}).get("ABRE_EM", "-")))
        return 0
    if "--correr" in argv:
        if not arg.get("sha256"):
            raise SystemExit("--correr exige --sha256=<da coorte congelada>")
        base.mkdir(parents=True, exist_ok=True)
        f = base / PLANO_F
        if f.exists():
            plano = json.loads(f.read_text(encoding="utf-8"))  # retoma: o plano gravado manda
        else:
            plano = plano_da_coorte(historico)
            if not plano["PODE_CORRER"]:
                raise SystemExit("COORTE_NAO_CONGELADA: ESTADO=%s" % plano["COORTE_ESTADO"])
            gravar(base, PLANO_F, plano)
        e = correr_rodadas(base, arg["sha256"], plano, onda=onda_real, portao=portao_real,
                           relatorio=relatorio_real, ledger=ledger_real(), historico=historico,
                           rodada=int(arg["rodada"]) if arg.get("rodada") else None, teto_dia=teto_dia,
                           livros_do_dia=Path(arg["livros-do-dia"]) if arg.get("livros-do-dia") else None,
                           janela_h=janela_h)
        print(json.dumps({"PAROU_NA_RODADA": e.get("PAROU_NA_RODADA"),
                          "RODADAS": {k: v.get("ESTADO") for k, v in e["RODADAS"].items()}}, indent=1))
        return 0 if e.get("PAROU_NA_RODADA") is None else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
