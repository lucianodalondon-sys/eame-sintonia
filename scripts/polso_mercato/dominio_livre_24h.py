#!/usr/bin/env python3
"""POLSO-FONTES · o dominio esta livre ha 24 h? Le os livros do robo vivo (SO LEITURA, sem rede).

    py scripts/polso_mercato/dominio_livre_24h.py <raiz dos livros vivos> [--desde 2026-09-26T01:05:00Z] [saida.json]

Para cada um dos 5 dominios do POLSO-FONTES procura, nos ficheiros de texto/JSON da arvore viva:
  - o DOMINIO escrito (url, host);
  - os IDs que o representam nos livros (SOURCE_ID / CANDIDATA_ID), porque o coletor escreve o ID e nao o URL.
Um registo so conta se trouxer um carimbo ISO >= --desde (por omissao: agora - 24 h). Registo com o dominio e
SEM carimbo nenhum nao prova visita e nao prova ausencia: vai para SEM_CARIMBO (NAO SEI), nunca para LIVRE.

Veredito por dominio: OCUPADO (ha registo datado nas ultimas 24 h) · LIVRE_NOS_LIVROS (nenhum) — e LIVRE so
quer dizer «os livros lidos nao registam»: pedido feito fora destes livros (outra sessao, curl a mao) nao
aparece aqui.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DOMINIOS = {
    "ismeamercati.it": {"hosts": ["ismeamercati.it"], "ids": ["IT-T10-001"]},
    "bmti.it": {"hosts": ["bmti.it", "listinicun.it"], "ids": ["IT-T10-002"]},
    "granariamilano.it": {"hosts": ["granariamilano.it", "granariamilano.org"],
                          # os SOURCE_ID que a alocacao viva deu as paginas da Granaria (SOURCE-ID-ALLOCATION-V1, 26/09)
                          "ids": ["CAND-0157"] + ["CAND-%04d" % n for n in range(492, 503)] +
                                 ["IT-T10-%03d" % n for n in (23, 25, 26, 27, 28, 29, 30, 34, 35, 36, 44)] + ["IT-T7-079"]},
    "italmercati.it": {"hosts": ["italmercati.it"], "ids": []},
    "clal.it": {"hosts": ["clal.it"], "ids": []},
}
RX_ISO = re.compile(r"20\d\d-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:?\d\d)?")
EXT = {".json", ".ndjson", ".jsonl", ".log", ".txt", ".csv"}


def _quando(s):
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _padroes(cfg):
    hosts = [re.compile(r"(?<![\w.-])(?:[\w-]+\.)*%s(?![\w-])" % re.escape(h), re.I) for h in cfg["hosts"]]
    ids = [re.compile(r"(?<![\w-])%s(?![\w-])" % re.escape(i)) for i in cfg["ids"]]
    return hosts + ids


def _registos(p: Path):
    """Unidade de leitura: um objeto JSON folha-de-lista (o registo) ou uma linha."""
    txt = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix == ".json":
        try:
            d = json.loads(txt)
        except ValueError:
            yield from txt.splitlines()
            return
        pilha = [d]
        while pilha:
            x = pilha.pop()
            if isinstance(x, dict):
                filhos = [v for v in x.values() if isinstance(v, (dict, list))]
                simples = {k: v for k, v in x.items() if not isinstance(v, (dict, list))}
                if simples:
                    yield json.dumps(simples, ensure_ascii=False)
                pilha.extend(filhos)
            elif isinstance(x, list):
                pilha.extend(x)
    else:
        yield from txt.splitlines()


def main():
    raiz = Path(sys.argv[1])
    desde = (_quando(sys.argv[sys.argv.index("--desde") + 1]) if "--desde" in sys.argv
             else datetime.now(timezone.utc) - timedelta(hours=24))
    saida = next((a for a in sys.argv[2:] if a.endswith(".json") and not a.startswith("--")), None)
    pads = {d: _padroes(c) for d, c in DOMINIOS.items()}
    res = {d: {"OCUPADO_POR": [], "SEM_CARIMBO": 0, "REGISTOS_ANTIGOS": 0} for d in DOMINIOS}
    lidos = 0
    for p in raiz.rglob("*"):
        if ".git" in p.parts or p.suffix.lower() not in EXT or not p.is_file():
            continue
        lidos += 1
        for reg in _registos(p):
            for d, rxs in pads.items():
                if not any(rx.search(reg) for rx in rxs):
                    continue
                datas = [q for q in (_quando(s) for s in RX_ISO.findall(reg)) if q]
                if not datas:
                    res[d]["SEM_CARIMBO"] += 1
                elif max(datas) >= desde:
                    res[d]["OCUPADO_POR"].append({"FICHEIRO": str(p.relative_to(raiz)).replace(os.sep, "/"),
                                                  "QUANDO": max(datas).isoformat(), "TRECHO": reg[:300]})
                else:
                    res[d]["REGISTOS_ANTIGOS"] += 1
    for d, r in res.items():
        r["VEREDITO"] = "OCUPADO" if r["OCUPADO_POR"] else "LIVRE_NOS_LIVROS"
        if r["OCUPADO_POR"]:
            ultimo = max(_quando(o["QUANDO"]) for o in r["OCUPADO_POR"])
            r["ULTIMO_REGISTO"] = ultimo.isoformat()
            r["LIVRE_A_PARTIR_DE"] = (ultimo + timedelta(hours=24)).isoformat()
        r["DATADOS_24H"] = len(r["OCUPADO_POR"])
        r["OCUPADO_POR"] = sorted(r["OCUPADO_POR"], key=lambda o: o["QUANDO"], reverse=True)[:20]
    out = {"DATASET": "POLSO-DOMINIO-LIVRE-24H-V1", "RAIZ": str(raiz), "DESDE": desde.isoformat(),
           "MEDIDO_EM": datetime.now(timezone.utc).isoformat(), "FICHEIROS_LIDOS": lidos, "DOMINIOS": res}
    if saida:
        Path(saida).write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    for d, r in res.items():
        print("%-18s %-17s datados_24h=%d antigos=%d sem_carimbo=%d%s" % (
            d, r["VEREDITO"], r.get("DATADOS_24H", 0), r["REGISTOS_ANTIGOS"], r["SEM_CARIMBO"],
            "  livre_a_partir_de=" + r["LIVRE_A_PARTIR_DE"] if r["OCUPADO_POR"] else ""))
        for o in r["OCUPADO_POR"][:3]:
            print("    %s  %s" % (o["QUANDO"], o["FICHEIRO"]))


if __name__ == "__main__":
    main()
