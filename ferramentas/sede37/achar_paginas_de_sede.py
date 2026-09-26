#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SEDE-37-PREP · 1) a pagina que PROVAVELMENTE prova a sede, tirada dos links das paginas JA guardadas.

SO LEITURA, sem rede. Para cada fonte do alvo (coorte congelada + as 61 PRONTAS do ensaio consolidado):
  · o estado da sede na SEDE-DAS-FONTES (sede-fontes-v1 @ dba56dd0): PAGINA_PROPRIA / MESMO_SITE / NAO_SEI,
    ou FORA_DA_LISTA (a fonte nao estava nas 60 dela);
  · TODAS as paginas HTML ja guardadas dessa fonte, de quatro sitios, e SO com o sha256 certo quando o banco o da:
      A  o armazem da Sala + arvores de trabalho (raw.json da ACERVO, 31 raizes) — inclui a 3.a onda;
      B  a loja do vivo (data/collection-store/italy/<SID>/**.html);
      C  os indices D40 guardados (alvos-novos-20260925/indices/<SID>.html);
      D  a pagina de evidencia do Curator (curadoria/evidencia/..., pelo campo EVIDENCE do contrato);
  · os links ESCRITOS nessas paginas cujo caminho diz contatti / dove-siamo / chi-siamo / about / note-legali,
    do MESMO dominio registavel da fonte. Nada e inventado: um link so entra se estiver escrito numa pagina.

Escolha: a classe mais forte (contatti > dove-siamo > chi-siamo > about > note-legali), depois a que aparece em
mais paginas, depois a mais curta. Cada candidato leva as paginas onde foi visto (caminho + sha256).

    py ferramentas/sede37/achar_paginas_de_sede.py --saida ferramentas/sede37/PAGINAS-DE-SEDE.json
"""
from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import html as H
import json
import os
import re
import subprocess
import sys
from urllib.parse import urljoin, urlparse

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "provas"))
import prova_teto_dominio as T  # noqa: E402  (dominio_registavel: o mesmo do teto D38)
sys.path.insert(0, os.path.join(RAIZ, "curadoria"))
import sede_da_fonte as S  # noqa: E402  (a regra da sede, dona unica)

VIVO = "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1"
ACERVO = "C:/Users/London1/reproc-acervo"
INDICES = "C:/Users/London1/alvos-novos-20260925/indices"
SEDE_FONTES = "dba56dd0:ferramentas/sede_fontes/PROPOSTA-SOURCE-LOCATION-RULE-V1.json"  # o campo VIA: PAGINA_GUARDADA_DA_PROPRIA_FONTE / MESMO_SITE de X / nada
BC = "onda3-pacote-v1:ferramentas/onda3_pacote/medida-bc/BC-LISTAS.json"
COORTE = os.path.join(RAIZ, "ferramentas", "big_collection", "COORTE-BIG-COLLECTION-V1.json")

#: (classe, regex no CAMINHO do link) — da mais forte para a mais fraca
CLASSES = (
    ("CONTATTI", re.compile(r"contatt|contact|recapiti", re.I)),
    ("DOVE_SIAMO", re.compile(r"dove[-_]?siamo|come[-_]?raggiungerci|sede[-_]|/sede/?$|/sedi/?", re.I)),
    ("CHI_SIAMO", re.compile(r"chi[-_]?siamo|/azienda/?$|/la[-_]societa/?$|about", re.I)),
    ("NOTE_LEGALI", re.compile(r"note[-_]?legali|impressum|colophon|informazioni[-_]legali", re.I)),
)
RE_HREF = re.compile(r"""href\s*=\s*["']([^"'#]+)""", re.I)
#: ficheiros tecnicos nao sao paginas (medido: IT-T7-017 dava contact-form-7/.../styles.css)
RE_TECNICO = re.compile(r"\.(?:css|js|png|jpe?g|gif|svg|ico|woff2?|ttf|pdf|xml|json)(?:$|\?)|/wp-(?:content|includes|json)/", re.I)


def git_json(ref):
    r = subprocess.run(["git", "show", ref], cwd=RAIZ, capture_output=True)
    return json.loads(r.stdout.decode("utf-8"))


def ler(caminho, sha=None):
    try:
        b = open(caminho, "rb").read()
    except OSError:
        return None
    if sha and hashlib.sha256(b).hexdigest() != sha:
        return None
    return b


def paginas_da_fonte(sid, raws_por_fonte, raizes, contrato):
    """[(origem, caminho, sha256, url_da_pagina, bytes)]"""
    fora, vistos = [], set()
    for r in raws_por_fonte.get(sid, []):                       # A
        if "html" not in (r.get("media_type") or ""):
            continue
        sha = r["sha256"].strip()
        if sha in vistos:
            continue
        for rz in raizes:
            b = ler(os.path.join(rz, r["storage_path"]), sha)
            if b is not None:
                vistos.add(sha)
                fora.append(("A_ARMAZEM", os.path.join(rz, r["storage_path"]), sha, r.get("source_url"), b))
                break
    for f in sorted(glob.glob(os.path.join(VIVO, "data", "collection-store", "italy", sid, "**", "*.htm*"), recursive=True)):  # B
        b = ler(f)
        sha = hashlib.sha256(b).hexdigest() if b else None
        if b and sha not in vistos:
            vistos.add(sha)
            fora.append(("B_LOJA_DO_VIVO", f, sha, None, b))
    f = os.path.join(INDICES, sid + ".html")                        # C
    b = ler(f)
    if b and hashlib.sha256(b).hexdigest() not in vistos:
        vistos.add(hashlib.sha256(b).hexdigest())
        fora.append(("C_INDICE_D40", f, hashlib.sha256(b).hexdigest(), None, b))
    ev = (contrato or {}).get("EVIDENCE")                            # D
    if ev:
        for f in sorted(glob.glob(os.path.join(VIVO, ev, "**", "*"), recursive=True)) + [os.path.join(VIVO, ev)]:
            if os.path.isfile(f):
                b = ler(f)
                if b and b.lstrip()[:1] == b"<" and hashlib.sha256(b).hexdigest() not in vistos:
                    vistos.add(hashlib.sha256(b).hexdigest())
                    fora.append(("D_EVIDENCIA_CURATOR", f, hashlib.sha256(b).hexdigest(), None, b))
    return fora


def links_de_sede(b, base_url, dominio):
    t = b.decode("utf-8", "replace")
    achados = {}
    for h in RE_HREF.findall(t):
        u = urljoin(base_url, H.unescape(h.strip()))
        p = urlparse(u)
        if p.scheme not in ("http", "https") or T.dominio_registavel(p.hostname or "") != dominio:
            continue
        caminho = p.path + (("?" + p.query) if p.query else "")
        if RE_TECNICO.search(caminho):
            continue
        for classe, rx in CLASSES:
            if rx.search(caminho):
                achados.setdefault(u.split("#")[0], classe)
                break
    return achados


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", required=True)
    ap.add_argument("--micro", default="", help="relatorios MICRO-SEDE-RONDA-*.json (;): as paginas pedidas entram como origem E")
    a = ap.parse_args()
    coorte = {l["SOURCE_ID"] for l in json.load(open(COORTE, encoding="utf-8"))["COORTE"]}
    p61 = set(git_json(BC)["PRONTAS_DEPOIS"])
    alvo = sorted(coorte | p61)
    sede60 = {f["SOURCE_ID"]: f for f in git_json(SEDE_FONTES)["FONTES"]}
    contratos = {c["SOURCE_ID"]: c for c in json.load(open(os.path.join(VIVO, "curadoria", "italy_contracts_curator.json"),
                                                            encoding="utf-8"))["FONTES"]}
    tabela = {c["SOURCE_ID"]: c for c in json.load(open(os.path.join(VIVO, "regras", "italy_contracts_onboarded.json"),
                                                         encoding="utf-8"))["FONTES"]}
    raws = json.load(open(os.path.join(ACERVO, "raw.json"), encoding="utf-8"))
    raws_por_fonte = collections.defaultdict(list)
    for r in raws:
        raws_por_fonte[r["source_id"]].append(r)
    raizes = open(os.path.join(ACERVO, "raizes.txt"), encoding="utf-8").read().strip().split(";")
    ordem = {c: i for i, (c, _) in enumerate(CLASSES)}
    # E · as paginas que a MICRO-SEDE pediu (so as guardadas com sha256 certo), para cada fonte que ela serve
    micro = collections.defaultdict(list)
    for rel in [x for x in a.micro.split(";") if x]:
        pasta = os.path.dirname(rel)
        for pg in json.load(open(rel, encoding="utf-8"))["PAGINAS"]:
            if pg.get("RESULTADO") == "OK":
                b = ler(os.path.join(pasta, pg["SHA256"] + ".html"), pg["SHA256"])
                if b:
                    for sid_m in pg["FONTES"]:
                        micro[sid_m].append(("E_MICRO_SEDE", os.path.join(pasta, pg["SHA256"] + ".html"), pg["SHA256"], pg["URL"], b))
    linhas = []
    for sid in alvo:
        s = sede60.get(sid)
        via = (s or {}).get("VIA") or ""
        if s is None:
            estado = "FORA_DA_LISTA_DA_SEDE_FONTES"
        elif via.startswith("PAGINA_GUARDADA"):
            estado = "PAGINA_PROPRIA"
        elif via.startswith("MESMO_SITE"):
            estado = "MESMO_SITE"
        else:
            estado = "NAO_SEI"
        c = contratos.get(sid) or {}
        idx = ((tabela.get(sid) or {}).get("ACQUISITION") or {}).get("INDEX_URL") or (c.get("ACQUISITION") or {}).get("INDEX_URL") \
            or c.get("CANONICAL_ENTRY_URL") or ""
        dominio = T.dominio_registavel(urlparse(idx).hostname or "")
        pags = paginas_da_fonte(sid, raws_por_fonte, raizes, c) + micro.get(sid, [])
        vistos = collections.defaultdict(list)
        classe_de = {}
        for origem, caminho, sha, url, b in pags:
            for u, classe in links_de_sede(b, url or idx, dominio).items():
                vistos[u].append({"ORIGEM": origem, "PAGINA": caminho.replace("\\", "/"), "SHA256": sha})
                classe_de[u] = classe
        cands = sorted(vistos, key=lambda u: (ordem[classe_de[u]], -len(vistos[u]), len(u)))
        sede_off = S.sede_das_paginas([(p[3] or p[1], p[2], p[4]) for p in pags])
        linhas.append({
            "SOURCE_ID": sid, "NA_COORTE": sid in coorte, "NAS_61_PRONTAS": sid in p61,
            "NOME": c.get("NAME"), "INDEX_URL": idx, "DOMINIO": dominio,
            "SEDE_HOJE": estado, "SEDE_SEDE_FONTES": (s or {}).get("SEDE_PROVAVEL"), "VIA_SEDE_FONTES": (s or {}).get("VIA") or "NAO SEI",
            "SEDE_NO_CONTRATO": c.get("SOURCE_LOCATION") or "AUSENTE",
            "PAGINAS_GUARDADAS_LIDAS": len(pags),
            "PAGINAS_POR_ORIGEM": dict(collections.Counter(p[0] for p in pags)),
            "PAGINA_DE_SEDE_PROVAVEL": cands[0] if cands else "NAO SEI — nenhuma pagina guardada tem link de contactos/sede",
            "CLASSE": classe_de[cands[0]] if cands else None,
            "VISTO_EM": vistos[cands[0]][:3] if cands else [],
            "VISTO_EM_N_PAGINAS": len(vistos[cands[0]]) if cands else 0,
            "ALTERNATIVAS": [{"URL": u, "CLASSE": classe_de[u], "PAGINAS": len(vistos[u])} for u in cands[1:4]],
            "SEDE_SEM_REDE": {k: sede_off[k] for k in ("SOURCE_LOCATION", "SOURCE_LOCATION_PRECISION", "SOURCE_LOCATION_BASIS", "SOURCE_LOCATION_RULE")},
            "SEDE_SEM_REDE_CANDIDATA": sede_off.get("CANDIDATA_NAO_PROVADA"),
        })
        print("%-11s %-16s pags=%-3d %-11s %s" % (sid, estado, len(pags), classe_de[cands[0]] if cands else "-",
                                                 cands[0] if cands else "NAO SEI"), flush=True)
    # sem link proprio: o link visto numa pagina de OUTRA fonte do mesmo dominio (dito como tal; nao inventado)
    por_dominio = {}
    for l in linhas:
        if l["CLASSE"] and l["DOMINIO"] not in por_dominio:
            por_dominio[l["DOMINIO"]] = l
    for l in linhas:
        if not l["CLASSE"] and l["DOMINIO"] in por_dominio:
            d = por_dominio[l["DOMINIO"]]
            l.update(PAGINA_DE_SEDE_PROVAVEL=d["PAGINA_DE_SEDE_PROVAVEL"], CLASSE=d["CLASSE"],
                     VISTO_EM=d["VISTO_EM"], VISTO_EM_N_PAGINAS=d["VISTO_EM_N_PAGINAS"],
                     VIA_DO_LINK="MESMO_DOMINIO de %s" % d["SOURCE_ID"])
        elif l["CLASSE"]:
            l["VIA_DO_LINK"] = "PAGINA_DA_PROPRIA_FONTE"
        else:
            l["VIA_DO_LINK"] = "NAO SEI"
    sem = [l for l in linhas if l["SEDE_HOJE"] != "PAGINA_PROPRIA"]
    resumo = {
        "ALVO": len(alvo), "COORTE_CONGELADA": len(coorte), "PRONTAS_61": len(p61),
        "SEDE_HOJE": dict(collections.Counter(l["SEDE_HOJE"] for l in linhas)),
        "SEM_SEDE_PROVADA_NA_PROPRIA_PAGINA": len(sem),
        "DESTAS_COM_PAGINA_DE_SEDE_ACHADA": sum(1 for l in sem if l["CLASSE"]),
        "POR_CLASSE": dict(collections.Counter(l["CLASSE"] or "NAO_SEI" for l in sem)),
        "DOMINIOS_DISTINTOS_DAS_SEM_SEDE": len({l["DOMINIO"] for l in sem}),
        "VIA_DO_LINK_DAS_SEM_SEDE": dict(collections.Counter(l["VIA_DO_LINK"] for l in sem)),
        "SEDE_PROVADA_SEM_REDE_NAS_SEM_SEDE": sum(1 for l in sem if l["SEDE_SEM_REDE"]["SOURCE_LOCATION"] != S.NAO_SEI),
    }
    json.dump({"DATASET": "SEDE-37-PAGINAS-DE-SEDE-V1", "REDE": 0, "RESUMO": resumo, "FONTES": linhas},
              open(a.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
