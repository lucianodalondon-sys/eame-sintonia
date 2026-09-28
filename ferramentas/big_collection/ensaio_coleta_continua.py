# -*- coding: utf-8 -*-
"""ENSAIO A SECO DA COLETA CONTINUA sobre a 4.a onda — 0 rede, 0 Sala, 0 robo.

    py ferramentas/big_collection/ensaio_coleta_continua.py                      (o ensaio gravado no repo)
    py ferramentas/big_collection/ensaio_coleta_continua.py --plano=%O%\\ONDA4-RODADAS\\RODADAS-PLANO.json
          --estado-rodadas=%O%\\ONDA4-RODADAS\\RODADAS-ESTADO.json --livros-do-dia=%O% --recibos=<pastas>
          [--agora=<ISO>] [--saida=<ficheiro>]                                     (o mesmo, com os livros REAIS)

A mesma pergunta, feita aos dois agendadores com o MESMO plano e os MESMOS livros:
  1. o disparador por rodada (`rodadas.correr_rodadas`, cada rodada por fechar, `--rodada=N`): corre? se nao,
     porque, e quando abre. A onda e um contador (nunca e chamada de verdade).
  2. o agendador por fonte (`coleta_continua.ciclo(..., a_seco=True)`): que fontes correm AGORA, e quando abre
     cada dominio das que esperam.

SEM ARGUMENTOS (o ensaio do repositorio) os livros vivos NAO estao aqui (vivem em ~/sintonia-sala-italia/ondas):
  · o PLANO e o do documento commitado `onda4/ORDEM-RENDIMENTO-ONDA4.md` (as 15 rodadas, fonte a fonte, com os
    pedidos previstos e os dominios) — lido da tabela, nao inventado;
  · o ESTADO e os LIVROS DE HOJE sao RECONSTRUIDOS do relato medido NOITE-20260927-2023 (27/09 20:25):
    R1, R2 e R3 FECHADAS; a R3 (IT-T8-021 edagricole.it, IT-T7-135 cia.it, 10 pedidos) acabou as 20:24 (-03);
    R4..R15 ADIADAS ate 28/09 20:24. As horas de R1 e R2 e os recibos das outras missoes: NAO SEI (nao estao no
    repo). Nenhum dominio de R4..R15 alem de edagricole.it e cia.it aparece em R1..R3; um recibo de outra missao
    que tenha tocado crea.gov.it / enea.it / cnr.it / santannapisa.it nas ultimas 24 h fecharia essa fonte —
    e o comando com os livros reais (acima) que o diz.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import coleta_continua as C                                        # noqa: E402
import rodadas as R                                                # noqa: E402

DOC = AQUI / "onda4" / "ORDEM-RENDIMENTO-ONDA4.md"
SAIDA = AQUI / "onda4" / "ENSAIO-COLETA-CONTINUA.json"
AGORA_RELATO = "2026-09-27T20:25:00-03:00"
SHA_ONDA4 = "eb7b6ab75056cff37b892cb7e9e59a553f6b9048ff8a5db961c532e643f0b9e4"
RE_RODADA = re.compile(r"^\*\*Rodada (\d+)\*\*\s*$")
RE_LINHA = re.compile(r"^\|\s*\d+\s*\|\s*(IT-T\d+-\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*([^|]*?)\s*\|\s*$")


def plano_do_documento(doc: Path = DOC) -> dict:
    rodadas, atual = [], None
    for l in doc.read_text(encoding="utf-8").splitlines():
        m = RE_RODADA.match(l)
        if m:
            atual = {"RODADA": int(m.group(1)), "FONTES": []}
            rodadas.append(atual)
            continue
        m = RE_LINHA.match(l)
        if m and atual is not None:
            doms = [d.strip() for d in m.group(2).split(",")]
            atual["FONTES"].append({"SOURCE_ID": m.group(1), "DOMINIO": doms[0], "DOMINIOS": doms,
                                    "PREVISTOS": int(m.group(3)), "CLASSE": m.group(4)})
    return {"COORTE_SHA256": SHA_ONDA4, "PLANO_VEM_DE": str(DOC.relative_to(AQUI.parents[1])), "RODADAS": rodadas}


def livros_do_relato(pasta: Path) -> dict:
    """RECONSTRUIDO do relato NOITE-20260927-2023: R1..R3 fechadas, a R3 acabou 27/09 23:24:00Z."""
    r3 = pasta / "ONDA4-RODADAS" / "RODADA-03"
    r3.mkdir(parents=True)
    (r3 / "TETO-ONDA.json").write_text(json.dumps({"PEDIDOS_POR_DOMINIO": {"edagricole.it": 5, "cia.it": 5}}), encoding="utf-8")
    (r3 / "ONDA-WEB-ESTADO.json").write_text(json.dumps({"FONTES": [
        {"SOURCE_ID": "IT-T8-021", "CORREU": True, "RUN_ID": "IT-T8-2026-09-27-232000-" + "0" * 16, "SEGUNDOS": 240,
         "PEDIDOS_POR_DOMINIO": {"edagricole.it": 5}},
        {"SOURCE_ID": "IT-T7-135", "CORREU": True, "RUN_ID": "IT-T7-2026-09-27-232300-" + "1" * 16, "SEGUNDOS": 60,
         "PEDIDOS_POR_DOMINIO": {"cia.it": 5}}]}), encoding="utf-8")
    return {"RODADAS": {"1": {"ESTADO": "FECHADA", "FONTES": [], "FEITAS": []},
                        "2": {"ESTADO": "FECHADA", "FONTES": [], "FEITAS": []},
                        "3": {"ESTADO": "FECHADA", "FONTES": ["IT-T8-021", "IT-T7-135"], "FEITAS": ["IT-T8-021", "IT-T7-135"]}}}


def ensaiar(plano: dict, estado_rodadas: dict, livros: Path, recibos: tuple, agora_utc: datetime) -> dict:
    # R1/R2 do relato: as fontes delas estao FEITAS (a lista vem do plano)
    for n, reg in estado_rodadas.get("RODADAS", {}).items():
        if reg.get("ESTADO") == "FECHADA" and not reg.get("FONTES"):
            reg["FONTES"] = [f["SOURCE_ID"] for r in plano["RODADAS"] if str(r["RODADA"]) == n for f in r["FONTES"]]
    tmp = Path(tempfile.mkdtemp(prefix="ensaio-coleta-continua-"))
    try:
        presas, chamadas = [], []
        for r in plano["RODADAS"]:
            if (estado_rodadas.get("RODADAS", {}).get(str(r["RODADA"])) or {}).get("ESTADO") == "FECHADA":
                continue
            b = tmp / ("R%02d" % r["RODADA"])
            b.mkdir()
            (b / R.ESTADO_F).write_text(json.dumps(estado_rodadas), encoding="utf-8")
            e = R.correr_rodadas(b, plano["COORTE_SHA256"], plano, onda=lambda *a: chamadas.append(a) or 0,
                                 portao=lambda: {"PASSA": False, "ENSAIO": "portao nunca perguntado"},
                                 relatorio=lambda *a: 0, ledger=b / "runs.ndjson", rodada=r["RODADA"], janela_h=24,
                                 livros_do_dia=livros, agora_utc=agora_utc, recibos=recibos)
            reg = e["RODADAS"][str(r["RODADA"])]
            presas.append({"RODADA": r["RODADA"], "PORQUE": reg.get("PORQUE"), "ABRE_EM": reg.get("ABRE_EM"),
                           "DOMINIOS_NA_JANELA": reg.get("DOMINIOS_NA_JANELA"),
                           "FONTES": [f["SOURCE_ID"] for f in r["FONTES"]]})
        cands = {l["LINHA"]: [] for l in C.LINHAS}
        cands["SITES"] = C.candidatas_do_plano(plano)
        eb = tmp / "cc"
        eb.mkdir()
        (eb / C.ESTADO_F).write_text(json.dumps({"LINHAS": {"SITES": {"FEITAS_NA_PASSAGEM": C.feitas_das_rodadas(estado_rodadas)}}}),
                                     encoding="utf-8")
        cc = C.ciclo(eb, plano["COORTE_SHA256"], cands, pecas={"ram": lambda: C.RAM_MINIMA_GB}, livros=livros,
                     recibos=recibos, livro_24h=tmp / "TETO-24H-VAZIO.json", agora_utc=agora_utc, a_seco=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    por_fonte = {f["SOURCE_ID"]: f for r in plano["RODADAS"] for f in r["FONTES"]}
    abre = {}
    for e in cc["ESPERAM"]:
        for d, x in (e.get("DOMINIOS_FECHADOS") or {}).items():
            a = abre.setdefault(d, {"ABRE_EM": x["ABRE_EM"], "PORQUE": set(), "FONTES_A_ESPERA": []})
            a["PORQUE"].add(x["PORQUE"])
            a["FONTES_A_ESPERA"].append(e["SOURCE_ID"])
            a["ABRE_EM"] = max(a["ABRE_EM"], x["ABRE_EM"])
    return {
        "DISPARADOR_POR_RODADA": {"PAROU": presas[0]["PORQUE"] if presas else None, "CHAMADAS_A_ONDA": len(chamadas),
                                  "RODADAS_POR_FECHAR": len(presas),
                                  "RODADAS_A_CORRER_AGORA": [p["RODADA"] for p in presas if not p["PORQUE"]]},
        "RODADAS_PRESAS": presas,
        "AGENDADOR_POR_FONTE": {k: cc[k] for k in ("AGORA_UTC", "LINHAS", "ESPERAM", "ORCAMENTO_DO_CICLO", "PROXIMO_A_ABRIR")},
        "ELEGIVEIS_AGORA_PRESAS_PELA_RODADA": [
            {"SOURCE_ID": s, "DOMINIO": por_fonte[s]["DOMINIO"], "PREVISTOS": por_fonte[s]["PREVISTOS"],
             "CLASSE": por_fonte[s].get("CLASSE"),
             "RODADA_DO_PLANO": next(p["RODADA"] for p in presas if s in p["FONTES"])}
            for s in cc["LINHAS"]["SITES"]["FONTES"]],
        "QUANDO_ABRE_CADA_DOMINIO": {d: dict(v, PORQUE=sorted(v["PORQUE"])) for d, v in sorted(abre.items())},
    }


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    agora = datetime.fromisoformat(arg.get("agora") or AGORA_RELATO).astimezone(timezone.utc)
    recibos = tuple(Path(x) for x in arg.get("recibos", "").split(",") if x)
    if arg.get("plano"):
        plano = json.loads(Path(arg["plano"]).read_text(encoding="utf-8"))
        er = json.loads(Path(arg["estado-rodadas"]).read_text(encoding="utf-8")) if arg.get("estado-rodadas") else {}
        out = ensaiar(plano, er, Path(arg["livros-do-dia"]), recibos, agora)
        out["ORIGEM"] = {"PLANO": arg["plano"], "ESTADO_RODADAS": arg.get("estado-rodadas"),
                         "LIVROS": arg["livros-do-dia"], "RECIBOS": [str(x) for x in recibos], "RECONSTRUIDO": False}
        saida = Path(arg["saida"]) if arg.get("saida") else Path(arg["livros-do-dia"]) / "ENSAIO-COLETA-CONTINUA.json"
    else:
        plano = plano_do_documento()
        tmp = Path(tempfile.mkdtemp(prefix="ensaio-livros-"))
        try:
            er = livros_do_relato(tmp)
            out = ensaiar(plano, er, tmp, (), agora)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        out["ORIGEM"] = {"PLANO": plano["PLANO_VEM_DE"], "RECONSTRUIDO": True,
                         "LIVROS": "RECONSTRUIDOS do relato NOITE-20260927-2023 (R1..R3 FECHADAS; R3 edagricole.it 5 + "
                                   "cia.it 5, fim 27/09 23:24:00Z). Livros reais fora do repo.",
                         "NAO_SEI": ["horas de R1 e R2 (nao mudam R4..R15: os dominios delas em R4..R15 sao so "
                                     "edagricole.it e cia.it, que a R3 fecha mais tarde)",
                                     "recibos das outras missoes (VOZES, MICRO-PROVA, T6) das ultimas 24 h",
                                     "o RODADAS-PLANO.json vivo (o plano aqui e a tabela do documento)"]}
        saida = Path(arg["saida"]) if arg.get("saida") else SAIDA
    out["AGORA"] = agora.isoformat(timespec="seconds")
    saida.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("DISPARADOR_POR_RODADA", "ELEGIVEIS_AGORA_PRESAS_PELA_RODADA",
                                          "QUANDO_ABRE_CADA_DOMINIO")}, ensure_ascii=False, indent=1, default=str))
    print("escrito:", saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
