#!/usr/bin/env python3
"""POLSO-FONTES · o leitor de preco (leis/preco_de_mercado.py) sobre o que JA esta no repo. Sem rede.

    py scripts/polso_mercato/medir_fixtures.py [saida.json]

Duas entradas, e nao se misturam:
  A · ACERVO    data/collection-store/italy/IT-T10-*/**.html — o que a Collection guardou (bytes reais).
  B · HANDOFF   build/ITALY-REALITY-HANDOFF-V2/MARKET-OBSERVATIONS.json — 80 observacoes de mercado lidas
                em 2026-09-02, cada uma com `citacao_literal`. NAO e acervo da Collection: e a leitura de um
                agente, guardada no repo. Serve de amostra do que cada fonte ESCREVE, nao de prova de coleta.
Por fonte: documentos, documentos com >=1 observacao, observacoes, e quantas tem as QUATRO chaves pedidas
(PRECO + PRACA + PERIODO + UNIDADE) e as seis do casco (+ CULTURA + ESTAGIO).
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "leis"))
import preco_de_mercado as PM   # noqa: E402

NS = PM.NAO_SEI


def _conta(obs):
    q = [o for o in obs if o["PAPEL"] == PM.OBSERVACAO]
    tem = lambda o, ks: all(o[k] != NS for k in ks)
    return {"OBS": len(q),
            "COM_4_CHAVES": sum(tem(o, ("PRACA", "PERIODO", "UNIDADE")) for o in q),
            "COM_6_CHAVES": sum(tem(o, ("PRACA", "PERIODO", "UNIDADE", "CULTURA", "ESTAGIO")) for o in q)}


def acervo():
    res = defaultdict(lambda: {"DOCS": 0, "DOCS_COM_PRECO": 0, "OBS": 0, "COM_4_CHAVES": 0, "COM_6_CHAVES": 0,
                               "EXEMPLOS": []})
    base = RAIZ / "data" / "collection-store" / "italy"
    for f in sorted(base.glob("IT-T10-*/**/*.htm*")):
        sid = f.relative_to(base).parts[0]
        # uma versao por documento: a ultima (vN) — as versoes sao a mesma pagina revisitada
        irmaos = sorted(f.parent.parent.glob("v*/" + f.name))
        if irmaos and f != irmaos[-1]:
            continue
        r = PM.precos_do_texto(PM.texto_de_html(f.read_text(encoding="utf-8", errors="replace")))
        c = _conta(r["OBSERVACOES"])
        d = res[sid]
        d["DOCS"] += 1
        d["DOCS_COM_PRECO"] += bool(c["OBS"])
        for k in ("OBS", "COM_4_CHAVES", "COM_6_CHAVES"):
            d[k] += c[k]
        for o in r["OBSERVACOES"][:1]:
            if len(d["EXEMPLOS"]) < 3:
                d["EXEMPLOS"].append({"FICHEIRO": str(f.relative_to(RAIZ)).replace("\\", "/"),
                                      **{k: o[k] for k in ("COMMODITY", "PRACA", "PERIODO", "PRECO_TEXTO",
                                                           "UNIDADE", "ESTAGIO", "PAPEL")}})
    return dict(res)


def handoff():
    d = json.loads((RAIZ / "build" / "ITALY-REALITY-HANDOFF-V2" / "MARKET-OBSERVATIONS.json").read_text(encoding="utf-8"))
    itens = d if isinstance(d, list) else next(v for v in d.values() if isinstance(v, list))
    res = defaultdict(lambda: {"CITACOES": 0, "CITACOES_COM_PRECO": 0, "OBS": 0, "COM_4_CHAVES": 0,
                               "COM_6_CHAVES": 0, "EXEMPLOS": []})
    for it in itens:
        nome = re.split(r"\s+[—(]", it.get("source_name") or "?")[0].strip()
        cit = it.get("citacao_literal") or ""
        r = PM.precos_do_texto(cit)
        c = _conta(r["OBSERVACOES"])
        x = res[nome]
        x["CITACOES"] += 1
        x["CITACOES_COM_PRECO"] += bool(c["OBS"])
        for k in ("OBS", "COM_4_CHAVES", "COM_6_CHAVES"):
            x[k] += c[k]
        if c["OBS"] and len(x["EXEMPLOS"]) < 3:
            o = r["OBSERVACOES"][0]
            x["EXEMPLOS"].append({"CITACAO": cit[:220], "URL": it.get("source_url"),
                                  **{k: o[k] for k in ("COMMODITY", "CULTURA", "PRACA", "PERIODO", "PRECO_TEXTO",
                                                       "UNIDADE", "ESTAGIO")}})
    return dict(res)


def main():
    out = {"DATASET": "POLSO-FONTES-FIXTURES-V1", "LEITOR": "leis/preco_de_mercado.py",
           "A_ACERVO": acervo(), "B_HANDOFF_V2": handoff()}
    s = json.dumps(out, ensure_ascii=False, indent=1) + "\n"
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(s, encoding="utf-8", newline="\n")
    for bloco in ("A_ACERVO", "B_HANDOFF_V2"):
        print(bloco)
        for k, v in sorted(out[bloco].items()):
            print("  %-45s %s" % (k, {a: b for a, b in v.items() if a != "EXEMPLOS"}))


if __name__ == "__main__":
    main()
