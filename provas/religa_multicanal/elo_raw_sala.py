# -*- coding: utf-8 -*-
"""O ELO RAW -> SALA, MEDIDO ITEM A ITEM (correccao C4 do revisor, D156).

    py provas/religa_multicanal/elo_raw_sala.py --ciclo=<pasta do CICLO> [--dsn=<DSN da Sala>]

O revisor escreveu, e a frase e o metodo desta peca:

    «um FAIL com zero itens, numa entrega onde o resto do orquestrador passou, e a assinatura de um
     ELO DE ESCRITA PARTIDO — nao de uma coleta que nao trouxe nada. Se os RAW existem e a Sala tem 0,
     o defeito esta ENTRE os dois, e e la que a proxima medicao deve comecar.»

Ele tem razao em exigir a medicao, e a hipotese dele TEM DE PODER SER FALSIFICADA. Por isso isto nao
conta itens: segue CADA captura do canario e diz ONDE ela parou, com o motivo LITERAL de quem a parou.

    A PERGUNTA NAO E «QUANTOS CHEGARAM». E «ONDE PARARAM, E QUEM OS PAROU».

Tres respostas possiveis, e elas NAO se confundem:

    ADMISSION_RECUSOU     a porta julgou e disse NAO / NAO_SEI / NAO_SE_APLICA. O elo esta INTEIRO:
                          a unidade chegou a quem julga, e quem julga respondeu. Sai o motivo literal.
    ELO_PARTIDO           a unidade tinha READY e NAO esta na Sala, ou nao recebeu RAW_OBSERVATION_ID,
                          ou a escrita levantou. Aqui sim o defeito esta ENTRE os dois.
    CHEGOU                esta na `sala_de_espera`, com a linhagem.

Saida: `provas/religa_multicanal/ELO-RAW-SALA.json` e uma tabela no ecra.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def _psql(dsn: str, sql: str) -> list:
    exe = os.environ.get("SINTONIA_PSQL_EXE") or "psql"
    r = subprocess.run([exe, dsn, "-t", "-A", "-F", "\x1f", "-c", sql],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError("psql: %s" % (r.stderr or "")[-300:])
    # \x1f e o separador, e o psql traz \r no Windows
    return [l.rstrip("\r").split("\x1f") for l in r.stdout.splitlines() if l.strip()]


def medir(ciclo: Path, dsn: str | None) -> dict:
    """Cada captura do ciclo -> onde parou. Sem banco, mede-se o que os ficheiros do ciclo dizem."""
    na_sala, com_raw = set(), set()
    if dsn:
        na_sala = {l[0] for l in _psql(dsn, "select item_id from sala_de_espera")}
        com_raw = {l[0] for l in _psql(dsn, "select id::text from raw_asset")}

    linhas, conta = [], {}
    for estado_f in sorted(Path(ciclo).glob("*/ONDA-WEB-ESTADO.json")):
        e = json.loads(estado_f.read_text(encoding="utf-8"))
        linha = e.get("LINHA")
        for fonte in e.get("FONTES", []):
            # a fonte que nem chegou a colher nao tem captura: isso e da COLETA, nao do elo
            if not (fonte.get("RELATO") or []):
                if fonte.get("STATUS") in ("FAILED", "ZERO"):
                    r = {"LINHA": linha, "SOURCE_ID": fonte.get("SOURCE_ID"), "ONDE_PAROU": "ANTES_DO_RAW",
                         "QUEM_PAROU": "COLETA", "MOTIVO": fonte.get("PORQUE_NAO_CORREU")}
                    linhas.append(r)
                    conta["ANTES_DO_RAW"] = conta.get("ANTES_DO_RAW", 0) + 1
                continue
            for rel in fonte["RELATO"]:
                rid = rel.get("RAW_OBSERVATION_ID")
                decisoes = rel.get("ADMISSION")
                if isinstance(decisoes, dict):                     # forma antiga: uma decisao so
                    decisoes = [decisoes]
                decisoes = decisoes or []
                aceites = [d for d in decisoes if d.get("RESULTADO") == "SIM"]
                r = {"LINHA": linha, "SOURCE_ID": rel.get("SOURCE_ID"), "URL": rel.get("URL"),
                     "SHA256": (rel.get("SHA256") or "")[:16], "RAW_OBSERVATION_ID": rid,
                     "PASSAGEM": (rel.get("PASSAGEM") or "")[:8],
                     "PERGUNTAS": [{"UNIVERSO": d.get("UNIVERSO"), "RESULTADO": d.get("RESULTADO"),
                                    "MOTIVO": (d.get("MOTIVO") or "")[:220],
                                    "CARIMBO": d.get("CARIMBO_DA_REGUA")} for d in decisoes]}
                if rid is None:
                    # ⚠️ AQUI SIM: a captura foi colhida e NAO recebeu observacao no banco.
                    r.update(ONDE_PAROU="ELO_PARTIDO", QUEM_PAROU="ESCRITA_DO_RAW",
                             MOTIVO="a captura nao recebeu RAW_OBSERVATION_ID do banco")
                elif rel.get("ESTADO") == "PRESERVADA_SEM_JULGAMENTO":
                    # ⚠️ NAO E ELO PARTIDO: e uma captura que foi preservada DE PROPOSITO sem ser
                    # julgada — os bytes de origem de um Reel, cuja unidade julgada e o registo.
                    # Chamar-lhe defeito faria uma decisao de desenho parecer um cano roto, e era
                    # exactamente isso que este medidor existe para distinguir.
                    r.update(ONDE_PAROU="PRESERVADA_SEM_JULGAMENTO", QUEM_PAROU=None,
                             MOTIVO=rel.get("PORQUE"))
                elif not decisoes:
                    r.update(ONDE_PAROU="ELO_PARTIDO", QUEM_PAROU="ADMISSION_NAO_CORREU",
                             MOTIVO="tem RAW no banco e nenhuma decisao foi registada")
                elif aceites:
                    # tinha READY: entao TEM de estar na Sala. Se nao esta, o elo partiu-se na escrita.
                    ids = [d.get("ITEM_ID") or (d.get("READY") or {}).get("ITEM_ID") for d in aceites]
                    if dsn and not any(i in na_sala for i in ids if i):
                        r.update(ONDE_PAROU="ELO_PARTIDO", QUEM_PAROU="ESCRITA_NA_SALA",
                                 MOTIVO="a Admission disse SIM e o item nao esta na sala_de_espera")
                    else:
                        r.update(ONDE_PAROU="CHEGOU", QUEM_PAROU=None, MOTIVO=None)
                else:
                    # A PORTA JULGOU E DISSE NAO. O elo esta INTEIRO — a unidade chegou a quem julga.
                    r.update(ONDE_PAROU="ADMISSION_RECUSOU", QUEM_PAROU="ADMISSION",
                             MOTIVO="; ".join("%s=%s: %s" % (d.get("UNIVERSO"), d.get("RESULTADO"),
                                                             (d.get("MOTIVO") or "")[:150])
                                              for d in decisoes))
                linhas.append(r)
                conta[r["ONDE_PAROU"]] = conta.get(r["ONDE_PAROU"], 0) + 1

    # O VEREDITO SOBRE A HIPOTESE DO REVISOR, dito de forma falsificavel.
    partidos = conta.get("ELO_PARTIDO", 0)
    veredito = ("ELO_INTEIRO: nenhuma captura se perdeu entre o RAW e a Sala. Onde a Sala ficou vazia, "
                "foi a Admission a julgar e a dizer que nao — com motivo escrito, item a item."
                if partidos == 0 else
                "ELO_PARTIDO em %d captura(s): ver QUEM_PAROU em cada uma." % partidos)
    return {"DATASET": "ELO-RAW-SALA", "CICLO": str(ciclo), "DSN_MEDIDO": bool(dsn),
            "CAPTURAS": len([x for x in linhas if x["ONDE_PAROU"] != "ANTES_DO_RAW"]),
            "JULGADAS": len([x for x in linhas
                             if x["ONDE_PAROU"] in ("ADMISSION_RECUSOU", "CHEGOU")]),
            "CONTA": conta, "VEREDITO": veredito, "ITENS": linhas}


def main(argv) -> int:
    arg = dict(a[2:].split("=", 1) for a in argv if a.startswith("--") and "=" in a)
    if "ciclo" not in arg:
        print(__doc__)
        return 2
    doc = medir(Path(arg["ciclo"]), arg.get("dsn") or os.environ.get("SINTONIA_SALA_DSN"))
    saida = Path(__file__).resolve().parent / "ELO-RAW-SALA.json"
    saida.write_text(json.dumps(doc, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("%-10s %-22s %-18s %-20s %s" % ("LINHA", "SOURCE_ID", "ONDE_PAROU", "QUEM_PAROU", "MOTIVO"))
    for x in doc["ITENS"]:
        print("%-10s %-22s %-18s %-20s %s" % (x.get("LINHA"), str(x.get("SOURCE_ID"))[:22],
                                              x["ONDE_PAROU"], str(x.get("QUEM_PAROU"))[:20],
                                              str(x.get("MOTIVO") or "")[:90]))
    print()
    print(json.dumps({"CAPTURAS": doc["CAPTURAS"], "CONTA": doc["CONTA"]}, ensure_ascii=False))
    print(doc["VEREDITO"])
    print("->", saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
