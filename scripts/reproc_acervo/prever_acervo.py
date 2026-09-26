#!/usr/bin/env python3
"""REPROC-ACERVO · previsao do reprocessamento de tempo/lugar do ACERVO que NAO esta na Sala.

SO LEITURA, sem rede e sem banco. O banco foi lido antes, por SELECT so-leitura, para tres ficheiros
JSON fora do Git (raw_asset, derived_artifact, sala_de_espera_atual). Este script:

  1. acha os BYTES de cada RAW e de cada TEXTO derivado em varias raizes, e SO aceita um ficheiro
     cujo sha256 bate com o do banco (os bytes estao espalhados por arvores de trabalho);
  2. acha a OBSERVACAO do livro do coletor de cada RAW (pela RAW_SHA256);
  3. corre o CODIGO INSTALADO (vivo e5cd691f), pela mesma estrada da producao:
        coleta/italy_executor.tempo_e_lugar(obs, bytes_da_pagina)   publicacao + lugar da fonte
        orquestrador._fato_do_texto(texto, bruto, publicacao)       data e lugar do facto (LUGAR-FATO)
     — a montagem de `bruto`/`publicacao` e a de `orquestrador.item_documental_para_a_porta`;
  4. conta, por campo e por fonte, quantos saem de NAO SEI.

NAO escreve em RAW, derivado, Sala nem armazem. So o ficheiro de saida.

    py scripts/reproc_acervo/prever_acervo.py --dados <pasta com raw.json derivados.json sala.json>
        --raizes "<r1;r2;...>" --livros "<glob;glob>" --saida <out.json>
"""
import argparse
import collections
import glob
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — as gavetas do processo no caminho

import ingresso as ing  # noqa: E402
import italy_executor as ex  # noqa: E402
import orquestrador as ORQ  # noqa: E402

NS = "NAO SEI"
QUATRO = (("PUBLICACAO", "PUBLISHED_AT"), ("LOCAL_DA_FONTE", "SOURCE_LOCATION"),
          ("DATA_DO_FATO", "FACT_TIME"), ("LOCAL_DO_FATO", "FACT_LOCATION"))
TEXTUAIS = ("TEXT_EXTRACTION", "TRANSCRIPTION")


def _ler(caminho, sha):
    try:
        with open(caminho, "rb") as f:
            b = f.read()
    except OSError:
        return None
    return b if hashlib.sha256(b).hexdigest() == sha else None


def achar(raizes, caminho_relativo, sha):
    """(bytes, raiz) do primeiro ficheiro com o sha certo; (None, None) se nenhum."""
    if not caminho_relativo or not sha:
        return None, None
    for r in raizes:
        b = _ler(os.path.join(r, caminho_relativo), sha)
        if b is not None:
            return b, r
    return None, None


def livros(padroes):
    """RAW_SHA256 -> a observacao MAIS RECENTE do livro (pela ordem dos ficheiros e das linhas)."""
    por_sha, n = {}, 0
    for padrao in padroes:
        for f in sorted(glob.glob(padrao)):
            n += 1
            with open(f, encoding="utf-8", errors="replace") as fh:
                for linha in fh:
                    try:
                        o = json.loads(linha)
                    except ValueError:
                        continue
                    if isinstance(o, dict) and o.get("RAW_SHA256"):
                        por_sha[str(o["RAW_SHA256"]).strip()] = o
    return por_sha, n


def prever(source_id, obs, pagina, texto):
    """-> {campo: (valor, base)} + a evidencia, pela estrada da producao."""
    obs = dict(obs or {})
    obs.setdefault("SOURCE_ID", source_id)
    tl = ex.tempo_e_lugar(obs, pagina)
    # o mesmo que orquestrador.item_documental_para_a_porta
    bruto = {k: tl[k] for k in ing.TEMPO_E_LUGAR if tl.get(k) not in ing.NAO_E_AFIRMACAO}
    publicacao = {k: bruto.pop(k) for k in ing.TEMPO_E_LUGAR_PARA_A_EVIDENCIA if k in bruto}
    ev = {}
    if texto:
        bruto.update(ORQ._fato_do_texto(texto, bruto, publicacao))
        ev = bruto.pop("TEMPO_LUGAR_EVIDENCIA", {})
    fora = {}
    for nome, campo in QUATRO:
        fora[nome] = (bruto.get(campo) or NS, bruto.get(campo + "_BASIS") or
                      ("sem texto derivado guardado" if campo in ("FACT_TIME", "FACT_LOCATION") and not texto else NS))
    return fora, ev, publicacao


def main():
    ap = argparse.ArgumentParser()
    for a in ("--dados", "--raizes", "--livros", "--saida"):
        ap.add_argument(a, required=True)
    a = ap.parse_args()
    ler = lambda n: json.load(open(os.path.join(a.dados, n), encoding="utf-8"))
    raws, derivados, sala = ler("raw.json"), ler("derivados.json"), ler("sala.json")
    raizes = [x for x in a.raizes.split(";") if x]
    por_sha_livro, n_livros = livros([x for x in a.livros.split(";") if x])

    der_na_sala = {int(x["item_id"].split(":")[1]) for x in sala if str(x["item_id"]).startswith("derived:")}
    der_por_raw = collections.defaultdict(list)
    for d in derivados:
        der_por_raw[d["raw_asset_id"]].append(d)

    por_sha = collections.OrderedDict()
    for r in raws:
        por_sha.setdefault(r["sha256"].strip(), []).append(r)

    itens, raiz_usada = [], collections.Counter()
    for sha, linhas in por_sha.items():
        r = linhas[0]
        ders = [d for rr in linhas for d in der_por_raw.get(rr["id"], [])]
        na_sala = any(d["id"] in der_na_sala for d in ders)
        bytes_, rz = None, None
        for rr in linhas:
            bytes_, rz = achar(raizes, rr["storage_path"], sha)
            if bytes_ is not None:
                raiz_usada[rz] += 1
                break
        texto, der_usado = None, None
        for d in sorted(ders, key=lambda d: d["id"]):
            if d["kind"] not in TEXTUAIS:
                continue
            b, _ = achar(raizes, d["storage_path"], (d["sha256"] or "").strip())
            if b is not None:
                texto, der_usado = b.decode("utf-8", errors="replace"), d["id"]
                break
        obs = por_sha_livro.get(sha)
        pagina = bytes_ if (bytes_ is not None and "html" in (r["media_type"] or "")) else None
        p, ev, pub = prever(r["source_id"], obs, pagina, texto)
        itens.append({
            "SHA256": sha, "RAW_IDS": [x["id"] for x in linhas], "SOURCE_ID": r["source_id"],
            "MEDIA_TYPE": r["media_type"], "NA_SALA": na_sala, "BYTES": bytes_ is not None,
            "DERIVADOS": [d["id"] for d in ders], "TEXTO": bool(texto), "DERIVADO_LIDO": der_usado,
            "LIVRO": obs is not None,
            "PREVISTO": {k: {"VALOR": v, "BASE": str(b)[:300]} for k, (v, b) in p.items()},
            "FACT_TIME_CALCULO": ev.get("FACT_TIME_CALCULO"), "FACT_TIME_KIND": ev.get("FACT_TIME_KIND"),
            "FACT_LOCATION_KIND": ev.get("FACT_LOCATION_KIND"),
            "PUBLICACAO_CONFLITO": bool(pub.get("PUBLISHED_AT_CONFLITO"))})

    def conta(sub):
        c = collections.OrderedDict()
        c["CONTEUDOS"] = len(sub)
        c["LINHAS_RAW"] = sum(len(x["RAW_IDS"]) for x in sub)
        c["COM_BYTES"] = sum(x["BYTES"] for x in sub)
        c["COM_TEXTO"] = sum(x["TEXTO"] for x in sub)
        c["COM_LIVRO"] = sum(x["LIVRO"] for x in sub)
        for nome, _ in QUATRO:
            c["GANHA_" + nome] = sum(1 for x in sub if x["PREVISTO"][nome]["VALOR"] not in ing.NAO_E_AFIRMACAO)
        c["DATA_DO_FATO_CALCULADA"] = sum(1 for x in sub if x["FACT_TIME_CALCULO"] == "RELATIVA_A_PUBLICACAO")
        c["PUBLICACAO_EM_CONFLITO"] = sum(x["PUBLICACAO_CONFLITO"] for x in sub)
        c["POR_TIPO_DE_MEDIA"] = dict(collections.Counter(x["MEDIA_TYPE"] for x in sub).most_common())
        return c

    fora = [x for x in itens if not x["NA_SALA"]]
    fontes = collections.defaultdict(list)
    for x in fora:
        fontes[x["SOURCE_ID"]].append(x)
    out = collections.OrderedDict()
    out["DATASET"] = "PREVISAO-REPROC-ACERVO-V1"
    out["CODIGO"] = "vivo origin/servico-20260923-0923 @ e5cd691f (italy_executor.tempo_e_lugar + orquestrador._fato_do_texto)"
    out["ENTRADAS"] = {"RAW_LINHAS": len(raws), "CONTEUDOS_DISTINTOS": len(por_sha), "DERIVADOS": len(derivados),
                       "SALA_LINHAS": len(sala), "LIVROS_LIDOS": n_livros, "OBSERVACOES_COM_SHA": len(por_sha_livro),
                       "RAIZES": raizes, "BYTES_ACHADOS_POR_RAIZ": dict(raiz_usada.most_common())}
    out["SALA"] = conta([x for x in itens if x["NA_SALA"]])
    out["ACERVO_FORA_DA_SALA"] = conta(fora)
    out["ACERVO_TODO"] = conta(itens)
    out["POR_FONTE_FORA_DA_SALA"] = {k: conta(v) for k, v in sorted(fontes.items(), key=lambda kv: -len(kv[1]))}
    out["ITENS"] = itens
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("ENTRADAS", "SALA", "ACERVO_FORA_DA_SALA")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
