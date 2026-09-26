#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VOZES-EXECUTAR · monta o PLANO de pedidos das VOZES-AGRONOMOS a partir SÓ do que já está nos livros. Sem rede.

    PYTHONUTF8=1 py ferramentas/vozes/montar_plano.py [--saida=data/derivados/VOZES-AGRONOMOS/PLANO-EXECUCAO.json]

Para cada ficha de `VOZES.json`, o endereço a pedir é um de dois, e nunca um terceiro:
  BUSCA   — a busca do PRÓPRIO site, com a `action` e o nome do campo tirados do `<form>` de uma página desse site
            JÁ GUARDADA no armazém (Sala só leitura). O termo é o nome da pessoa (ou o tema da série).
  ENTRADA — o endereço desse domínio que já está nas candidatas/contratos do vivo (só leitura).
Se não há nenhum dos dois, a ficha fica DESCOBRIR (0 pedidos). Não se escreve endereço de cabeça.

Fora deste comando, e porquê (escrito no plano): CNR/Coldiretti/ANGA/Unaprol (coordenação 10:13) · reterurale.it
(robots: só 01–03 h UTC → ronda NOTURNA, comando à parte) · domínios da 4.ª onda (C2-ONDA4/rodadas.txt: colisão 0,
ficam para DEPOIS da rodada deles) · a pessoa já provada (V22, página oficial colhida pela P5: 0 pedidos).
"""
from __future__ import annotations

import html
import importlib.machinery
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse

RAIZ = Path(__file__).resolve().parents[2]
DERIV = RAIZ / "data" / "derivados" / "VOZES-AGRONOMOS"
VIVO = Path("C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1")
ARMAZEM = Path(os.path.expanduser("~/sintonia-sala-italia/armazem"))
RODADAS_ONDA4 = Path("C:/Users/London1/auditoria-madrugada/C2-ONDA4/rodadas.txt")

PROIBIDOS = ("cnr.it", "coldiretti.it", "anga.it", "unaprol.it")          # coordenação 10:13
NOTURNOS = ("reterurale.it",)                                              # robots Visit-time 01-03 UTC
# o termo de busca das séries sem nome (o tema, como está no título do vídeo guardado)
# o nome como a pessoa o escreve (VOZES.json guarda-o sem acento)
TERMO_DA_PESSOA = {"V18": "Mario Enrico Pè"}
TERMO_DA_SERIE = {"V23": "webinar", "V24": "difesa delle colture", "V25": "annata agronomica",
                  "V26": "mosca delle olive", "V27": "afide melone", "V28": "cimice asiatica",
                  "V29": "monitoraggio fenologico", "V30": "agronomia moderna"}


def dominio(u: str) -> str:
    return urlparse(u or "").netloc.lower().removeprefix("www.")


def mesmo_site(a: str, b: str) -> bool:
    """terraevita.edagricole.it e edagricole.it são o MESMO site (um é subdomínio do outro); amap.marche.it e
    arpa.marche.it NÃO são (só partilham o sufixo regional)."""
    return a == b or a.endswith("." + b) or b.endswith("." + a)


def organizacao(d: str) -> str:
    return d


def dominios_da_onda4() -> set[str]:
    if not RODADAS_ONDA4.exists():
        raise SystemExit("sem %s: a colisão com a 4.a onda não se mede — não se monta plano" % RODADAS_ONDA4)
    return set(re.findall(r"^\s+([a-z0-9.-]+\.[a-z]{2,})\s", RODADAS_ONDA4.read_text("utf-8"), re.M))


def entradas_dos_livros() -> dict[str, list[str]]:
    urls = [c.get("URL") for c in json.loads((VIVO / "candidatas/FONTES-CANDIDATAS.json").read_text("utf-8"))["CANDIDATAS"]]
    for f in ("curadoria/italy_contracts_curator.json", "regras/italy_contracts_onboarded.json"):
        for s in json.loads((VIVO / f).read_text("utf-8"))["FONTES"]:
            urls += [s.get("CANONICAL_ENTRY_URL"), (s.get("ACQUISITION") or {}).get("INDEX_URL")]
    por = {}
    for u in urls:
        if u and u.startswith("http"):
            por.setdefault(dominio(u), []).append(u)
    return por


def formularios_guardados(consultar, sep) -> dict[str, dict]:
    """{dominio: {ACTION, CAMPO, VISTO_EM}} — a busca do site, lida do <form> de uma página JÁ guardada."""
    fora = {}
    for linha in consultar("select source_url, storage_path from public.raw_asset where media_type like 'text/html%'"):
        u, sp = linha.split(sep)
        d = dominio(u)
        if d in fora:
            continue
        p = ARMAZEM / sp
        if not p.exists():
            continue
        b = p.read_bytes().decode("utf-8", "replace")
        for m in re.finditer(r"<form\b([^>]*)>(.*?)</form>", b, re.I | re.S):
            attrs, corpo = m.group(1), m.group(2)
            if not re.search(r"search|cerca|ricerca", attrs + corpo[:400], re.I):
                continue
            if re.search(r'method\s*=\s*["\']?post', attrs, re.I):
                continue                                     # POST não é um endereço: não se usa
            campo = next((c for c in re.findall(r'<input\b[^>]*\bname\s*=\s*["\']([^"\']+)', corpo, re.I)
                          if c.lower() in ("q", "s", "search_term", "query", "testoricerca", "keys", "searchword",
                                           "search_api_fulltext", "k", "text")), None)
            act = re.search(r'action\s*=\s*["\']([^"\']*)', attrs, re.I)
            if campo:
                fora[d] = {"ACTION": urljoin(u, html.unescape(act.group(1) if act else "")), "CAMPO": campo, "VISTO_EM": u}
                break
    return fora


def montar(vozes: dict, entradas: dict, formularios: dict, onda4: set[str]) -> dict:
    fichas = []
    for f in vozes["FICHAS"]:
        d = f["PROVAR_PAPEL_EM"]
        linha = {"ID": f["ID"], "PESSOA": f["PESSOA"], "PAPEL_NO_TITULO": f["PAPEL_NO_TITULO"], "DOMINIO": d}
        if "PROVADO" in f["PAPEL_NO_TITULO"]:
            linha.update(ESTADO="JA_PROVADO", PORQUE="pagina oficial ja colhida (P5); 0 pedidos")
        elif d.startswith("DESCOBRIR"):
            linha.update(ESTADO="DESCOBRIR", PORQUE=d)
        elif any(p in d for p in PROIBIDOS):
            linha.update(ESTADO="FORA", PORQUE="dominio fechado pela coordenacao (10:13)")
        elif any(mesmo_site(d, o) for o in onda4):
            linha.update(ESTADO="DEPOIS_DA_ONDA4", PORQUE="dominio na 4.a onda (%s): colisao 0 = so depois da rodada dele"
                         % next(o for o in onda4 if mesmo_site(d, o)))
        else:
            if f["PESSOA"].startswith("NAO SEI"):
                termo = TERMO_DA_SERIE.get(f["ID"], "")
            else:
                termo = TERMO_DA_PESSOA.get(f["ID"]) or f["PESSOA"]
            form = next((v for k, v in formularios.items() if k == d or k.endswith("." + d) or d.endswith("." + k)), None)
            if form and termo:
                alvo = form["ACTION"] + ("&" if "?" in form["ACTION"] else "?") + urlencode({form["CAMPO"]: termo})
                linha.update(MODO="BUSCA", ALVO=alvo, TERMO=termo, FORM_VISTO_EM=form["VISTO_EM"])
            else:
                ent = sorted(entradas.get(d, []) or [u for k, v in entradas.items() if k.endswith("." + d) for u in v],
                             key=len)
                if not ent:
                    linha.update(ESTADO="DESCOBRIR", PORQUE="sem busca guardada e sem entrada nos livros")
                    fichas.append(linha)
                    continue
                linha.update(MODO="ENTRADA", ALVO=ent[0], TERMO=termo)
            linha["ESTADO"] = "NOTURNO" if any(n in d for n in NOTURNOS) else "A_PEDIR"
            linha["ORGANIZACAO"] = organizacao(dominio(linha["ALVO"]))
        fichas.append(linha)
    # rondas: por organizacao, robots.txt + 1 pagina = 2 pedidos (teto 2); a 2.a pessoa do mesmo site vai a ronda seguinte
    ronda_de, n = {}, {}
    for f in fichas:
        if f["ESTADO"] not in ("A_PEDIR", "NOTURNO"):
            continue
        o = f["ORGANIZACAO"]
        n[o] = n.get(o, 0) + 1
        f["RONDA"] = ("NOTURNA-" if f["ESTADO"] == "NOTURNO" else "") + str(n[o])
        f["PEDIDOS"] = 2
    rondas = {}
    for f in fichas:
        if "RONDA" in f:
            rondas.setdefault(f["RONDA"], []).append(f["ID"])
    return {"DATASET": "VOZES-PLANO-EXECUCAO", "TETO_POR_DOMINIO_POR_RONDA": 2,
            "ONDA4_ORGANIZACOES": sorted(onda4), "RONDAS": rondas,
            "PEDIDOS_POR_RONDA": {r: 2 * len(v) for r, v in rondas.items()}, "FICHAS": fichas}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    a = dict(x[2:].split("=", 1) for x in argv if x.startswith("--") and "=" in x)
    LS = importlib.machinery.SourceFileLoader("ler_sala", str(DERIV / "ler_sala.py.txt")).load_module()
    plano = montar(json.loads((DERIV / "VOZES.json").read_text("utf-8")), entradas_dos_livros(),
                   formularios_guardados(LS.consultar, LS.SEP), dominios_da_onda4())
    saida = Path(a.get("saida", DERIV / "PLANO-EXECUCAO.json"))
    saida.write_text(json.dumps(plano, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for f in plano["FICHAS"]:
        print("%-4s %-16s %-7s %-10s %s" % (f["ID"], f["ESTADO"], f.get("MODO", ""), f.get("RONDA", ""),
                                             (f.get("ALVO") or f.get("PORQUE") or "")[:95]))
    print("RONDAS", plano["RONDAS"], "PEDIDOS", plano["PEDIDOS_POR_RONDA"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
