#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MICRO-VERIFICACAO · a PREVISAO medida: os leitores INSTALADOS (e5cd691f) sobre as materias JA guardadas.

    py ferramentas/micro_verif/prever_com_o_instalado.py <collection-store/italy do vivo> <saida.json> SID [SID...]

Sem rede, sem Sala, so leitura do armazem. Para cada materia HTML guardada (versao mais recente) das
fontes escolhidas, corre o que o encanamento corre:
  · publicacao da pagina  -> coleta/italy_executor.publicacao_da_pagina (JSON-LD > meta > <time>)
  · texto                 -> coleta/executor_texto_de_html.extrair
  · data/lugar do facto   -> leis/fato_do_texto.campos_do_fato (sem publicacao provada: relativas nao contam)
  · lugar da fonte        -> regras/contratos_de_fonte.lugar_da_fonte (pelo contrato)
Serve de base a previsao: itens NOVOS da mesma fonte tendem a sair como os guardados.
"""
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / "coleta"), str(RAIZ / "regras"), str(RAIZ / "leis"), str(RAIZ)]
import contratos_de_fonte as CF  # noqa: E402
import executor_texto_de_html as H  # noqa: E402
import fato_do_texto as FT  # noqa: E402
import italy_executor as IE  # noqa: E402


def main():
    loja, saida, sids = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
    out = []
    for sid in sids:
        c = Counter()
        exemplos = []
        lugar_fonte = CF.lugar_da_fonte(sid)
        for it in sorted(d for d in (loja / sid).iterdir() if d.is_dir()) if (loja / sid).is_dir() else []:
            vs = sorted(v for v in it.iterdir() if v.is_dir())
            fich = [p for p in vs[-1].iterdir() if p.is_file()] if vs else []
            if not fich:
                continue
            b = fich[0].read_bytes()
            if b.lstrip()[:1] != b"<":
                c["NAO_HTML"] += 1
                continue
            c["HTML"] += 1
            pub = IE.publicacao_da_pagina(b)
            tem_pub = bool(pub.get("PUBLISHED_AT")) and str(pub.get("PUBLISHED_AT")).upper() not in ("NAO SEI", "UNKNOWN")
            c["PUBLICACAO_SIM" if tem_pub else "PUBLICACAO_NAO"] += 1
            if tem_pub:
                c["PRECISAO:" + str(pub.get("PUBLISHED_AT_PRECISION"))] += 1
            r = H.extrair(b, "text/html")
            texto = r[0] if isinstance(r, tuple) else r
            f = FT.campos_do_fato(texto or "", pub.get("PUBLISHED_AT") if tem_pub else None,
                                  pub.get("PUBLISHED_AT_BASIS") if tem_pub else None)
            c["DATA_FATO_SIM" if f["fact_time"] != FT.NAO_SEI else "DATA_FATO_NAO"] += 1
            c["LUGAR_FATO_SIM" if f["fact_location"] != FT.NAO_SEI else "LUGAR_FATO_NAO"] += 1
            if f["fact_time"] != FT.NAO_SEI:
                c["DATA_FATO_KIND:" + f["fact_time_kind"]] += 1
            if f["fact_location"] != FT.NAO_SEI:
                c["LUGAR_FATO_KIND:" + f["fact_location_kind"]] += 1
            if len(exemplos) < 3:
                exemplos.append({"ITEM": it.name[:90], "PUBLISHED_AT": pub.get("PUBLISHED_AT"),
                                 "PUBLISHED_AT_BASIS": str(pub.get("PUBLISHED_AT_BASIS"))[:80],
                                 "PUBLISHED_AT_PRECISION": pub.get("PUBLISHED_AT_PRECISION"),
                                 "fact_time": f["fact_time"], "fact_time_kind": f["fact_time_kind"],
                                 "fact_location": f["fact_location"], "fact_location_kind": f["fact_location_kind"]})
        out.append({"SOURCE_ID": sid, "LUGAR_DA_FONTE_PELO_CONTRATO": lugar_fonte["VALOR"],
                    "CONTAGENS": dict(c), "EXEMPLOS": exemplos})
        print(sid, lugar_fonte["VALOR"], dict(c))
    saida.write_text(json.dumps({"DATASET": "PREVISAO-COM-O-INSTALADO-V1", "ARVORE": "e5cd691f",
                                 "LOJA": str(loja), "FONTES": out}, ensure_ascii=False, indent=1) + "\n",
                     encoding="utf-8")


if __name__ == "__main__":
    main()
