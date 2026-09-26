#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ACERVO-PARA-SALA-2 — a CULTURA das linhas que o ensaio poria na Sala, lida pelo extrator D84. So medida.

A estrada do vivo (69b0e23f) NAO escreve as quatro chaves (CULTURA, REGIAO_DO_FATO, FASE, JANELA): medido
na Sala real a 26/09, 94 de 94 linhas com `janela_declarada` = NAO SEI («pousado antes da 033»). Quem as le e
`admissao.janela_para_o_ready` do EXTRATOR-EVENTO-V2 / extratores-v2-juntos (D84), NAO instalado.

Este script responde a pergunta «e se o D84 estivesse instalado, quantas das linhas novas teriam cultura?»,
sem instalar nada: importa o D84 de uma COPIA (`--d84 <arvore em efb78e60>`) e aplica-o ao MESMO texto que o
ensaio gravou na copia da Sala (`NOVAS[].TEXTO`), com os bytes guardados do RAW (sha256 conferido) para o
titulo e a descricao do video. Nao escreve em banco nenhum; nao vai a rede.

    py provas/acervo_para_sala_cultura.py --ensaio <ensaio.json> --d84 <arvore> --dados <pasta com raw.json>
        --raizes "<r;r>" --saida <out.json>
"""
import argparse
import collections
import hashlib
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    for x in ("--ensaio", "--d84", "--dados", "--raizes", "--saida"):
        ap.add_argument(x, required=True)
    # as linhas novas do ensaio tem raw_observation_id do banco DESCARTAVEL (fora do raw.json): o pai vem
    # entao da decisao da porta (`evidencia.portoes.linhagem.pai`, os primeiros 60 caracteres do sha256)
    ap.add_argument("--decisoes", default="")
    a = ap.parse_args()
    os.environ["HTTP_PROXY"] = os.environ["HTTPS_PROXY"] = "http://127.0.0.1:9"
    sys.path[:0] = [os.path.join(a.d84, "admissao"), a.d84]
    os.chdir(a.d84)
    import _gavetas  # noqa: F401,PLC0415
    import admissao as adm  # noqa: PLC0415
    import reprocessar_tempo_lugar as RP  # noqa: PLC0415

    e = json.load(open(a.ensaio, encoding="utf-8"))
    lista = json.load(open(os.path.join(a.dados, "raw.json"), encoding="utf-8"))
    raws = {str(r["id"]): r for r in lista}
    pai_do_item = {}
    for d in (json.load(open(a.decisoes, encoding="utf-8")) if a.decisoes else []):
        pai = (((d.get("evidencia") or {}).get("portoes") or {}).get("linhagem") or {}).get("pai")
        if pai and d.get("resultado") == "SIM":
            pai_do_item[d["item"]] = pai

    def raw_de(n):
        r = raws.get(str(n.get("RAW_OBSERVATION_ID")))
        if r:
            return r
        pai = pai_do_item.get(n["ITEM_ID"])
        achados = [x for x in lista if pai and x["sha256"].strip().startswith(pai)] if pai else []
        return achados[0] if achados else None
    raizes = [x for x in a.raizes.split(";") if x]

    def dados_de(r):
        if not r:
            return None
        for R in raizes:
            p = os.path.join(R, r["storage_path"])
            if os.path.isfile(p):
                b = open(p, "rb").read()
                if hashlib.sha256(b).hexdigest() == r["sha256"].strip():
                    return b
        return None

    aus = adm.AUSENCIA
    linhas = []
    for n in e.get("NOVAS", []):
        sid, uni = n["SOURCE_ID"], n["UNIVERSO"]
        r = raw_de(n) or {}
        dados = dados_de(r) if r else None
        # o texto chega da copia da Sala com TAB/LF/CR trocados por espaco (ver o ensaio)
        est = {"SOURCE_ID": sid, "TEXTO": n.get("TEXTO") or "",
               "DERIVED_ARTIFACT_ID": str(n["ITEM_ID"]).split(":", 1)[-1],
               "RAW_ASSET_ID": n.get("RAW_OBSERVATION_ID"), "PARENT_SHA256": (r.get("sha256") or "").strip() or None,
               "CAPTURED_AT": r.get("captured_at"),
               "TEMPO_E_LUGAR": RP.ex.tempo_e_lugar({"SOURCE_ID": sid}, dados)}
        est.update(RP.titulo_e_descricao(dados))
        item = RP.ORQ.item_documental_para_a_porta(est, source_id=sid)
        d = adm.decidir(item, uni, corrida="ACERVO-PARA-SALA-2")
        j = adm.janela_para_o_ready(item, d)
        c = j["CULTURA"]
        linhas.append({"ITEM_ID": n["ITEM_ID"], "SOURCE_ID": sid, "UNIVERSO": uni, "BYTES_DO_RAW": dados is not None,
                       "DECISAO_D84": d.resultado,
                       "CULTURA": c["VALOR"], "CULTURA_BASE": c["BASE"] if c["VALOR"] != aus else aus,
                       "CULTURA_PROVADA": c["VALOR"] != aus and c["BASE"] != aus,
                       "FACT_TIME_DO_ENSAIO": n.get("FACT_TIME")})
    ns = ("NAO SEI", "", None)
    fora = {"D84_HEAD": os.popen('git -C "%s" log --format="%%H %%s" -1' % a.d84).read().strip(),
            "ENSAIO": a.ensaio, "LINHAS_NOVAS": len(linhas),
            "COM_CULTURA_PROVADA": sum(x["CULTURA_PROVADA"] for x in linhas),
            "COM_DATA_DO_FATO": sum(x["FACT_TIME_DO_ENSAIO"] not in ns for x in linhas),
            "COM_AS_DUAS": sum(x["CULTURA_PROVADA"] and x["FACT_TIME_DO_ENSAIO"] not in ns for x in linhas),
            "DECISAO_D84": dict(collections.Counter(x["DECISAO_D84"] for x in linhas)),
            "CULTURA_POR_UNIVERSO": dict(collections.Counter(x["UNIVERSO"] for x in linhas if x["CULTURA_PROVADA"])),
            "LINHAS": linhas}
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(fora, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in fora.items() if k != "LINHAS"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
