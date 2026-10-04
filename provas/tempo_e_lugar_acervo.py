#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TEMPO-E-LUGAR · previsao do REPROCESSAMENTO DO ACERVO, sem rede e sem banco.

So LEITURA. Para cada original (RAW) do acervo com bytes guardados (sha256
conferido) aplica o codigo novo de tempo/lugar e CONTA — nao escreve em lado
nenhum alem do ficheiro de saida:

    livro do coletor  -> coleta/italy_executor.tempo_e_lugar   (publicacao T3, sede, porques)
    bytes da pagina   -> provas/tempo_e_lugar_medir.publicacao_html
                         (PREVISAO do extractor de publicacao, que e da nuvem
                          nuvem-tempo-publicacao-v1 e ainda nao chegou)
    texto derivado    -> leis/fato_do_texto.campos_do_fato     (LUGAR-FATO)

    py provas/tempo_e_lugar_acervo.py --raw <raw-todos.json> --derivados <derivados.json>
        --armazem <raiz> --raizes "<r1;r2>" --livros "<glob;glob>" --sala78 <sala78.json>
        --saida <out.json>

LEI DE PRESERVACAO: isto nao altera RAW, derivado, nem Sala. E so a conta.
"""
import argparse
import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
for p in ("", "coleta", "orquestrador", "admissao", "regras", "leis", "provas"):
    sys.path.insert(0, os.path.join(RAIZ, p))
import _gavetas  # noqa: E402,F401
import fato_do_texto as FT  # noqa: E402
import italy_executor as ex  # noqa: E402
import tempo_e_lugar_medir as M  # noqa: E402

NS = "NAO SEI"
QUATRO = ("PUBLICACAO", "LOCAL_DA_FONTE", "DATA_DO_FATO", "LOCAL_DO_FATO")


def _livros(padroes):
    por_sha = {}
    for padrao in padroes:
        for f in __import__("glob").glob(padrao):
            for linha in open(f, encoding="utf-8", errors="replace"):
                try:
                    o = json.loads(linha)
                except json.JSONDecodeError:
                    continue
                if o.get("RAW_SHA256"):
                    por_sha.setdefault(o["RAW_SHA256"], o)
    return por_sha


def _ler(caminho, sha):
    try:
        b = open(caminho, "rb").read()
    except OSError:
        return None
    return b if hashlib.sha256(b).hexdigest() == sha else None


def prever(raw, obs, bytes_, texto):
    """-> {campo: (valor, base)} para os quatro, com o codigo novo."""
    tl = ex.tempo_e_lugar(obs) if obs else {}
    pub, pub_base = tl.get("PUBLISHED_AT"), tl.get("PUBLISHED_AT_BASIS")
    if not pub and bytes_ is not None and "html" in raw["media_type"]:
        p = M.publicacao_html(bytes_)
        if p and p.get("ISO"):
            pub, pub_base = p["ISO"], "PAGINA:%s (previsao; extractor da nuvem)" % p["BASE"]
    fora = {"PUBLICACAO": (pub or NS, pub_base or NS),
            "LOCAL_DA_FONTE": (tl.get("SOURCE_LOCATION") or NS,
                               tl.get("SOURCE_LOCATION_BASIS") or NS)}
    if texto:
        f = FT.campos_do_fato(texto, pub, pub_base)
        fora["DATA_DO_FATO"] = (f["fact_time"], f["fact_time_basis"])
        fora["LOCAL_DO_FATO"] = (f["fact_location"], f["fact_location_basis"])
    else:
        fora["DATA_DO_FATO"] = (NS, "sem texto derivado guardado")
        fora["LOCAL_DO_FATO"] = (NS, "sem texto derivado guardado")
    return fora


def main():
    ap = argparse.ArgumentParser()
    for a in ("--raw", "--derivados", "--armazem", "--raizes", "--livros", "--sala78", "--saida"):
        ap.add_argument(a, required=True)
    a = ap.parse_args()
    raws = json.load(open(a.raw, encoding="utf-8"))
    derivados = json.load(open(a.derivados, encoding="utf-8"))
    sala78 = {x["sha256"].strip() for x in json.load(open(a.sala78, encoding="utf-8"))}
    texto_da_sala = {x["sha256"].strip(): x["texto"]
                     for x in json.load(open(a.sala78, encoding="utf-8"))}
    livros = _livros([x for x in a.livros.split(";") if x])
    raizes = [a.armazem] + [x for x in a.raizes.split(";") if x]
    der_por_raw = collections.defaultdict(list)
    for d in derivados:
        if d["kind"] == "TEXT_EXTRACTION":
            der_por_raw[d["raw"]].append(d)

    por_sha = {}
    for r in raws:
        if r["media_type"] not in ("text/html", "application/pdf"):
            continue
        sha = r["sha256"].strip()
        por_sha.setdefault(sha, []).append(r)

    itens = []
    for sha, lista in sorted(por_sha.items()):
        r = lista[0]
        bytes_ = None
        for raiz in raizes:
            for cand in __import__("glob").glob(os.path.join(raiz, r["storage_path"])):
                bytes_ = _ler(cand, sha)
                if bytes_ is not None:
                    break
            if bytes_ is not None:
                break
        texto = texto_da_sala.get(sha)
        if not texto:
            for rr in lista:
                for d in der_por_raw.get(rr["id"], []):
                    b = _ler(os.path.join(a.armazem, d["path"]), d["sha"].strip())
                    if b is not None:
                        texto = b.decode("utf-8", errors="replace")
                        break
                if texto:
                    break
        obs = livros.get(sha)
        p = prever(r, obs, bytes_, texto)
        itens.append({"SHA256": sha, "RAW_IDS": [x["id"] for x in lista],
                      "SOURCE_ID": r["source_id"], "MEDIA_TYPE": r["media_type"],
                      "NA_SALA": sha in sala78, "BYTES": bytes_ is not None,
                      "TEXTO": bool(texto), "LIVRO": obs is not None,
                      "PREVISTO": {k: {"VALOR": v, "BASE": b[:300]} for k, (v, b) in p.items()}})

    def conta(sub):
        c = {"ORIGINAIS": len(sub), "COM_BYTES": sum(x["BYTES"] for x in sub),
             "COM_TEXTO": sum(x["TEXTO"] for x in sub), "COM_LIVRO": sum(x["LIVRO"] for x in sub)}
        for q in QUATRO:
            c["GANHA_" + q] = sum(1 for x in sub if x["PREVISTO"][q]["VALOR"] != NS)
        c["DATA_DO_FATO_CALCULADA"] = sum(
            1 for x in sub if FT.RELATIVA in x["PREVISTO"]["DATA_DO_FATO"]["BASE"])
        c["PUBLICACAO_SO_PELA_PAGINA"] = sum(
            1 for x in sub if x["PREVISTO"]["PUBLICACAO"]["BASE"].startswith("PAGINA:"))
        return c

    fontes = collections.defaultdict(list)
    for x in itens:
        fontes[x["SOURCE_ID"]].append(x)
    out = {"SALA_78": conta([x for x in itens if x["NA_SALA"]]),
           "ACERVO_FORA_DA_SALA": conta([x for x in itens if not x["NA_SALA"]]),
           "ACERVO_TODO": conta(itens),
           "POR_FONTE": {k: conta(v) for k, v in sorted(fontes.items())},
           "ITENS": itens}
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("SALA_78", "ACERVO_FORA_DA_SALA", "ACERVO_TODO")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
