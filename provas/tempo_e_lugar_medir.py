#!/usr/bin/env python3
"""TEMPO-E-LUGAR · ponto 1 — a informacao de tempo e de lugar EXISTE para os
itens da Sala? So leitura: le a Sala (psql com default_transaction_read_only),
os bytes guardados (armazem) e os contratos. Nao escreve em banco nenhum.

    FACT_TIME != PUBLICATION_TIME != OBSERVATION_TIME != COLLECTION_TIME
    SOURCE_LOCATION != FACT_LOCATION

Para cada item diz, por campo, se ha PROVA disponivel e qual e a BASE.
Nao decide nada: conta o que existe.

    py provas/tempo_e_lugar_medir.py --sala-json <dump.json> --contratos <c.json>
        --raizes <raiz1;raiz2;...> --saida <out.json>

O dump da Sala e JSON de
    select json_agg(...) from sala_de_espera s join raw_asset r ...
com as chaves: ordem, run_id, obs, source_id, sha256, storage_path,
source_url, media_type, texto.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import fato_local as FL  # noqa: E402

NAO_SEI = "NAO SEI"

# ── PUBLICACAO NA PAGINA: cada padrao leva o nome da sua BASE ────────────
# A ordem e a de confianca: o que a pagina declara como data de publicacao
# do ARTIGO vem antes de um <time> solto, que pode ser de outra coisa.
PADROES_HTML = (
    ("JSONLD_datePublished", r'"datePublished"\s*:\s*"([^"]{8,40})"'),
    ("META_article:published_time",
     r'<meta[^>]+(?:property|name)=["\']article:published_time["\'][^>]*content=["\']([^"\']+)'),
    ("META_article:published_time",
     r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\']article:published_time'),
    ("META_og:published_time",
     r'<meta[^>]+property=["\']og:published_time["\'][^>]*content=["\']([^"\']+)'),
    ("ITEMPROP_datePublished",
     r'itemprop=["\']datePublished["\'][^>]*(?:content|datetime)=["\']([^"\']+)'),
    ("META_date",
     r'<meta[^>]+name=["\'](?:date|DC\.date(?:\.issued)?|pubdate|publish-date|parsely-pub-date)["\'][^>]*content=["\']([^"\']+)'),
    ("TIME_datetime", r'<time[^>]+datetime=["\']([^"\']+)'),
)
RE_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def data_iso(v):
    m = RE_ISO.search(v or "")
    return "%s-%s-%s" % m.groups() if m else None


def publicacao_html(b: bytes):
    """-> {BASE, VALOR, TODAS} ou None. Varias datas <time> diferentes = AMBIGUO."""
    s = b.decode("utf-8", errors="replace")
    achados = []
    for base, p in PADROES_HTML:
        for m in re.finditer(p, s, re.I):
            achados.append((base, m.group(1).strip()))
    if not achados:
        return None
    fortes = [a for a in achados if a[0] != "TIME_datetime"]
    if fortes:
        base, v = fortes[0]
        return {"BASE": base, "VALOR": v, "ISO": data_iso(v),
                "TODAS": sorted({a[1] for a in fortes})[:5]}
    datas = sorted({data_iso(v) for _, v in achados if data_iso(v)})
    return {"BASE": "TIME_datetime" + ("_AMBIGUO" if len(datas) > 1 else ""),
            "VALOR": achados[0][1], "ISO": datas[0] if len(datas) == 1 else None,
            "TODAS": datas[:5]}


RE_NOME_DATA = re.compile(r"(\d{2})[-_/](\d{2})[-_/](\d{4})")


def publicacao_pdf(nome: str, b: bytes):
    """Data da EDICAO no nome do ficheiro; a CreationDate do PDF e geracao, e
    fica ao lado com o seu nome — nao e publicacao."""
    fora = {}
    m = RE_NOME_DATA.search(nome)
    if m:
        fora["NOME_DO_FICHEIRO"] = "%s-%s-%s" % (m.group(3), m.group(2), m.group(1))
    c = re.search(rb"/CreationDate\s*\(D:(\d{4})(\d{2})(\d{2})", b)
    if c:
        fora["PDF_CreationDate_GERACAO"] = "-".join(x.decode() for x in c.groups())
    return fora


def achar_bytes(sp, sha, raizes):
    for r in raizes:
        for cand in glob.glob(os.path.join(r, sp)):
            try:
                b = open(cand, "rb").read()
            except OSError:
                continue
            if hashlib.sha256(b).hexdigest() == sha:
                return cand, b
    return None, None


def medir(item, contratos, raizes):
    sp, sha = item["storage_path"], item["sha256"].strip()
    caminho, b = achar_bytes(sp, sha, raizes)
    r = {"OBS": item["obs"], "RUN_ID": item["run_id"], "ORDEM": item["ordem"],
         "SOURCE_ID": item["source_id"], "MEDIA_TYPE": item["media_type"],
         "BYTES_ACHADOS": caminho or NAO_SEI}
    # PUBLICACAO
    pub = None
    if b is not None and "html" in item["media_type"]:
        pub = publicacao_html(b)
    elif b is not None and "pdf" in item["media_type"]:
        p = publicacao_pdf(os.path.basename(sp), b)
        if p.get("NOME_DO_FICHEIRO"):
            pub = {"BASE": "NOME_DO_FICHEIRO_EDICAO", "ISO": p["NOME_DO_FICHEIRO"],
                   "VALOR": os.path.basename(sp), "TODAS": p}
        elif p:
            pub = {"BASE": "SO_GERACAO_DO_PDF", "ISO": None, "TODAS": p}
    r["PUBLICACAO"] = pub or NAO_SEI
    # LUGAR DA FONTE — so do contrato; o REGION do Atlas e o que a AMOSTRA viu
    sl = (contratos.get(item["source_id"]) or {}).get("SL") or NAO_SEI
    r["SOURCE_LOCATION_CONTRATO"] = sl
    # FACTO — sobre o texto que a Sala guardou
    texto = item["texto"] or ""
    aceitas, recusadas = FL.localizacoes_do_fato(texto, origem="SALA_TEXTO")
    r["FACT_LOCATION_ACEITAS"] = aceitas[:5]
    r["MENCOES_DE_LUGAR"] = sorted({x["PLACE"] for x in recusadas})[:10]
    t = FL.tempo_do_fato(texto, (pub or {}).get("ISO") if isinstance(pub, dict) else None)
    r["FACT_TIME"] = {k: t.get(k) for k in ("FACT_TIME", "FACT_TIME_PRECISION",
                                            "FACT_TIME_EVIDENCE", "FACT_TIME_ORIGIN")}
    return r


def resumo(linhas):
    n = len(linhas)
    def conta(f):
        return sum(1 for x in linhas if f(x))
    return {
        "ITENS": n,
        "BYTES_ACHADOS_COM_SHA_CERTO": conta(lambda x: x["BYTES_ACHADOS"] != NAO_SEI),
        "PUBLICACAO_COM_PROVA": conta(lambda x: isinstance(x["PUBLICACAO"], dict)
                                      and x["PUBLICACAO"].get("ISO")),
        "PUBLICACAO_POR_BASE": _por(linhas, lambda x: x["PUBLICACAO"]["BASE"]
                                    if isinstance(x["PUBLICACAO"], dict) else NAO_SEI),
        "SOURCE_LOCATION_NO_CONTRATO": conta(
            lambda x: not x["SOURCE_LOCATION_CONTRATO"].upper().startswith(("NAO SEI", "NÃO SEI"))),
        "FACT_LOCATION_COM_ANCORA": conta(lambda x: x["FACT_LOCATION_ACEITAS"]),
        "SO_MENCAO_DE_LUGAR": conta(lambda x: not x["FACT_LOCATION_ACEITAS"]
                                    and x["MENCOES_DE_LUGAR"]),
        "FACT_TIME_AMARRADO_AO_FACTO": conta(
            lambda x: x["FACT_TIME"]["FACT_TIME"] not in (None, "NOT_KNOWN")),
    }


def _por(linhas, f):
    d = {}
    for x in linhas:
        k = f(x)
        d[k] = d.get(k, 0) + 1
    return dict(sorted(d.items(), key=lambda kv: -kv[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sala-json", required=True)
    ap.add_argument("--contratos", required=True)
    ap.add_argument("--raizes", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    itens = json.load(open(a.sala_json, encoding="utf-8"))
    contratos = json.load(open(a.contratos, encoding="utf-8"))
    raizes = [x for x in a.raizes.split(";") if x]
    linhas = [medir(i, contratos, raizes) for i in itens]
    out = {"RESUMO": resumo(linhas), "ITENS": linhas}
    with open(a.saida, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps(out["RESUMO"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
