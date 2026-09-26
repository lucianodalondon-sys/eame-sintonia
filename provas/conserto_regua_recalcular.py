#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CONSERTO-REGUA — o que o codigo DESTA arvore daria as linhas da Sala. Sem banco.

Le uma fotografia so-leitura da Sala (JSON, com texto, bruto e universo), e para
cada linha corre a MESMA estrada do reprocessamento
(`admissao/reprocessar_tempo_lugar.ready_de`): livro do coletor + bytes guardados
(sha256 conferido) + texto guardado. Escreve os valores na forma da vista
`sala_de_espera_atual`, para `provas/sala_verifica.py --vista-json` os conferir.

Corre-se DUAS vezes — na arvore de base (antes) e na do conserto (depois) — e a
diferenca e o conserto. Nao escreve em banco nenhum; o RAW nao e tocado.

    py provas/conserto_regua_recalcular.py --sala <foto.json> --livros "<glob;glob>"
        --raizes "<r1;r2>" --saida <valores.json>
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import reprocessar_tempo_lugar as R  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    for a in ("--sala", "--livros", "--raizes", "--saida"):
        ap.add_argument(a, required=True)
    a = ap.parse_args()
    linhas = json.load(open(a.sala, encoding="utf-8"))
    livros = R.livros_por_sha([x for x in a.livros.split(";") if x])
    raizes = [x for x in a.raizes.split(";") if x]
    fora = []
    for l in linhas:
        l = dict(l, SHA256=(l.get("SHA256") or "").strip())
        dados = R.bytes_guardados(l, raizes)
        ready = R.ready_de(l, livros.get(l["SHA256"]), dados)
        fora.append({
            "obs": l["RAW_OBSERVATION_ID"], "run_id": l["RUN_ID"], "ordem": l["ORDEM"],
            "source_id": l["SOURCE_ID"], "sha256": l["SHA256"],
            "storage_path": l["STORAGE_PATH"], "media_type": l["MEDIA_TYPE"],
            "published_at": ready["PUBLISHED_AT"], "published_at_basis": ready["PUBLISHED_AT_BASIS"],
            "source_location": ready["SOURCE_LOCATION"],
            "source_location_basis": ready["SOURCE_LOCATION_BASIS"],
            "fact_time": ready["FACT_TIME"], "fact_time_basis": ready["FACT_TIME_BASIS"],
            "fact_location": ready["FACT_LOCATION"],
            "fact_location_basis": ready["FACT_LOCATION_BASIS"],
            "evidencia": ready["TEMPO_LUGAR_EVIDENCIA"], "revisoes": 0,
            "versao_do_codigo": R.versao_do_codigo()})
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print("LINHAS=%d VERSAO=%s" % (len(fora), R.versao_do_codigo()))


if __name__ == "__main__":
    main()
