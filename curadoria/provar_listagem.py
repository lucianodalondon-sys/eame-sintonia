#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PROVAR A LISTAGEM — a capacidade que trava as 7 e as 33: descer do indice ao item.

    A ENTRADA NAO LISTA OS ITENS. ENTAO ONDE E QUE ELES ESTAO?

Medido no PASSO 1 do candidate feeder: 7 fontes com SOURCE_ID e 33 HTML nunca
caracterizadas esbarram na MESMA coisa — a pagina de entrada tem «0 links com
cara de item». O molde generico (entrada = homepage, padrao = qualquer seccao)
nunca as encontraria. A outra linha (aquisicao-detalhe-v1) resolveu isto para
21 fontes do motor com um GET por listagem e juizo por fonte. Aqui faz-se o
mesmo, deterministico, para as candidatas do Curator:

    1. robots.txt pela porta da casa (gate_de_rota) — proibido nao se bate
    2. GET a entrada, pela MESMA identidade do canario do Curator
    3. procurar, nos links internos, ate 2 seccoes com vocabulario de noticia
    4. GET a seccao; contar ITENS (slug com 2+ hifens, ou ano no caminho)
       debaixo do caminho dela; 2 ou mais = listagem
    5. abrir o PRIMEIRO item e retrata-lo: uma capa nao prova nada

    PROVADA           listagem com 2+ itens e item aberto com texto, sem capa
    NAO_SEI           respondeu 200 e nao se achou listagem — resultado valido
    HTTP_403 / 4xx    a fonte respondeu que nao; regista-se, nao se contorna
    ROBOTS_BLOCK      o anfitriao proibiu o caminho
    ROBOTS_UNREADABLE nao se leu o robots; prudencia: nao se bate
    UNREACHABLE       DNS/transporte deste egresso — UNKNOWN, nao morta

Cadencia: 1 s entre pedidos, no maximo 4 pedidos por fonte, 1 fonte de cada
vez. CONTROLO POSITIVO primeiro (uma listagem que a outra linha ja provou):
se ele falhar, o leitor esta avariado e NENHUMA fonte e julgada.

    NAO SEI E RESULTADO. 403 E RESPOSTA. UMA FALHA UNIFORME ACUSA O LEITOR.

Com `--contratar`, as PROVADAS que ja tem SOURCE_ID ganham contrato pelo
molde da casa com a rota provada (ROUTE_PROVENANCE = este ficheiro), entram
no livro como CANARY_PENDING e na fila como VALIDATE_ROUTE. Quem promove a
READY continua a ser o worker, com o gate de detalhe. Nunca aqui.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "curadoria"))
import canario as CAN            # noqa: E402  (buscar: UA, timeout, 4 MB)
import gate_de_rota as GATE      # noqa: E402
import retrato_html as RH        # noqa: E402

CUR = RAIZ / "curadoria"
BALDES = CUR / "CANDIDATE-BUCKETS-V1.json"
CANDIDATAS = RAIZ / "candidatas" / "FONTES-CANDIDATAS.json"
ALLOC = CUR / "SOURCE-ID-ALLOCATION-V1.json"
CARACT = CUR / "SOURCE-CHARACTERIZATION-V1.json"
CONTRATOS = CUR / "italy_contracts_curator.json"
SAIDA = CUR / "LISTAGENS-PROVADAS-V1.json"

PAUSA_S = 1.0
MAX_PEDIDOS_POR_FONTE = 4
TETO_MAX_TARGETS = 30
MIN_ITENS = 2

# ⚠️ CONTROLO POSITIVO: listagem provada pela outra linha (83385fe7) e
# re-provada pelo canario desta arvore no PASSO 2 revisto (15 itens).
CONTROLO = {"NOME": "Consorzio Vino Chianti Classico (IT-T7-033)",
            "URL": "https://www.chianticlassico.com/news/"}

_SECCAO = re.compile(
    r"^/(?:[a-z]{2}/)?(?:news|notizie|notizia|novita|ultime-notizie|comunicati(?:-stampa)?|"
    r"ufficio-stampa|sala-stampa|press|attualita|eventi|blog|bollettin[oi]|rassegna(?:-stampa)?|"
    r"primo-piano|in-evidenza|approfondiment[oi]|avvisi|pubblicazioni|magazine|articoli|"
    r"news-e-eventi|news-ed-eventi|news-blog|notizie-ed-eventi)/?$", re.I)
_ITEM_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){2,}/?$")
_ITEM_ANO = re.compile(r"(?:^|/)(?:19|20)\d{2}(?:/|$)")
_EXCLUI = re.compile(r"(?:^|/)(?:category|categoria|tag|author|page|pagina|feed|rss|search|cerca|"
                     r"wp-json|wp-content|wp-admin|login|privacy|cookie)(?:/|$)", re.I)


def _dominio(u: str) -> str:
    return urlparse(u).netloc.lower().replace("www.", "")


def _links_internos(html: str, base: str) -> list[str]:
    dom = _dominio(base)
    out, vistos = [], set()
    for h in re.findall(r'href=["\']([^"\'#]+)["\']', html, re.I):
        u = urljoin(base, h.strip())
        if not u.startswith("http") or _dominio(u) != dom:
            continue
        u = u.split("?")[0]
        if u not in vistos:
            vistos.add(u)
            out.append(u)
    return out


_SECCAO_LARGA = re.compile(r"(?:news|notiz|novita|comunicat|stampa|press|attualit|eventi|blog|"
                           r"bollettin|rassegna|approfondiment|avvisi|pubblicazion|magazine|articol)",
                           re.I)


def _seccoes(links: list[str]) -> list[str]:
    """Links cujo caminho e uma seccao de noticias. Mais curtos primeiro.

    Primeiro a lista fechada (caminho EXACTO de seccao). Se nao houver, a
    larga: um caminho com 1-2 segmentos que CONTENHA vocabulario de noticia
    e nao pareca item (sem slug de 2+ hifens no ultimo segmento). Medido na
    1a corrida: 23 de 26 NAO_SEI gastaram UM pedido — a entrada — porque a
    seccao chamava-se `/archivio-news/`, `/news-eventi/`, `/comunicati/`…
    e a lista fechada nao a via.
    """
    exacta, larga = [], []
    for u in links:
        p = urlparse(u).path or "/"
        if _SECCAO.match(p.rstrip("/") + "/"):
            exacta.append(u)
            continue
        segs = [s for s in p.strip("/").split("/") if s]
        if 1 <= len(segs) <= 2 and _SECCAO_LARGA.search(p) and not _EXCLUI.search(p) \
                and not _ITEM_SLUG.match(segs[-1]) and not _ITEM_ANO.search(p) \
                and not re.search(r"\.(?:pdf|jpg|png|xml|rss)$", p, re.I):
            larga.append(u)
    exacta = sorted(set(exacta), key=lambda u: (len(urlparse(u).path), u))
    larga = sorted(set(larga), key=lambda u: (len(urlparse(u).path), u))
    return (exacta + [u for u in larga if u not in exacta])[:2]


def _itens_sob(listagem: str, links: list[str]) -> list[str]:
    """Itens debaixo do caminho da listagem: slug com 2+ hifens ou ano."""
    base = urlparse(listagem).path.rstrip("/") + "/"
    out = []
    for u in links:
        p = urlparse(u).path
        if not p.startswith(base) or p.rstrip("/") == base.rstrip("/"):
            continue
        resto = p[len(base):]
        if _EXCLUI.search(resto):
            continue
        ult = resto.rstrip("/").split("/")[-1]
        if _ITEM_SLUG.match(ult) or _ITEM_ANO.search(resto):
            out.append(u)
    return out


def _padrao(listagem: str) -> str:
    host = re.escape(_dominio(listagem))
    path = re.escape(urlparse(listagem).path.rstrip("/") + "/")
    return (r"^https?://(www\.)?%s%s(?:[a-z0-9-]+/)?(?:[a-z0-9]+(?:-[a-z0-9]+){2,}|(?:19|20)\d{2}[^?#]*)/?$"
            % (host, path))


def provar(url: str, *, pedidos: dict, pausa: float = PAUSA_S) -> dict:
    """Uma fonte. Devolve o veredito e a evidencia; nunca levanta."""
    r = {"URL": url, "ESTADO": "NAO_SEI", "PEDIDOS": 0, "ROBOTS": None, "ENTRADA_HTTP": None,
         "SECCOES_TENTADAS": [], "LISTAGEM": None, "ITENS": 0, "LINK_PATTERN": None,
         "MAX_TARGETS": None, "ITEM_ABERTO": None, "PORQUE": ""}
    host = urlparse(url).netloc
    try:
        rp, origem = GATE.robots_de(host)
    except Exception as e:
        r.update(ESTADO="ROBOTS_UNREADABLE", PORQUE="robots.txt ilegivel: %s" % type(e).__name__)
        return r
    r["ROBOTS"] = origem[:100]
    if "inacessivel" in origem:
        r.update(ESTADO="ROBOTS_UNREADABLE", PORQUE="robots nao pode ser lido — nao se bate por prudencia")
        return r
    if not GATE.permitido(url, rp):
        r.update(ESTADO="ROBOTS_BLOCK", PORQUE="a entrada casa com Disallow no robots vivo")
        return r

    def _get(u: str):
        if r["PEDIDOS"] >= MAX_PEDIDOS_POR_FONTE:
            return None, b"", "teto de pedidos"
        r["PEDIDOS"] += 1
        pedidos["TOTAL"] += 1
        st, b, err = CAN.buscar(u)
        time.sleep(pausa)
        return st, b, err

    st, b, err = _get(url)
    r["ENTRADA_HTTP"] = st
    if st == 403 or st == 401:
        r.update(ESTADO="HTTP_%d" % st, PORQUE="a fonte respondeu que nao a esta identidade; registado, nao contornado")
        return r
    if st == 0:
        r.update(ESTADO="UNREACHABLE", PORQUE="transporte/DNS deste egresso: %s — UNKNOWN, nao morta" % err)
        return r
    if st != 200 or not b:
        r.update(ESTADO="HTTP_%s" % st, PORQUE="entrada devolveu HTTP %s" % st)
        return r
    if b.lstrip().removeprefix(b"\xef\xbb\xbf")[:1] != b"<":   # BOM a frente nao e «nao e HTML»
        r.update(ESTADO="NAO_SEI", PORQUE="a entrada nao e HTML (%s)" % b[:8])
        return r

    html = b.decode("utf-8", "replace")
    links = _links_internos(html, url)
    candidatas = [url] + [s for s in _seccoes(links) if s.rstrip("/") != url.rstrip("/")]
    melhor = None
    for lst in candidatas:
        if lst == url:
            l_links = links
            r["SECCOES_TENTADAS"].append({"URL": lst, "HTTP": 200, "COMO": "a propria entrada"})
        else:
            st2, b2, err2 = _get(lst)
            r["SECCOES_TENTADAS"].append({"URL": lst, "HTTP": st2, "COMO": "seccao com vocabulario de noticia"})
            if st2 != 200 or not b2:
                continue
            l_links = _links_internos(b2.decode("utf-8", "replace"), lst)
        itens = _itens_sob(lst, l_links)
        rx = re.compile(_padrao(lst))
        itens = [u for u in itens if rx.match(u)]
        if len(itens) >= MIN_ITENS and (melhor is None or len(itens) > melhor[1]):
            melhor = (lst, len(itens), itens)
        if melhor and melhor[1] >= 5:
            break
    if not melhor:
        r.update(ESTADO="NAO_SEI", PORQUE="entrada e seccoes respondem mas nenhuma lista %d+ itens com cara de item"
                 % MIN_ITENS)
        return r

    lst, n, itens = melhor
    r.update(LISTAGEM=lst, ITENS=n, LINK_PATTERN=_padrao(lst), MAX_TARGETS=min(n, TETO_MAX_TARGETS))
    # ⚠️ ABRIR O MESMO ITEM QUE O CANARIO VAI ABRIR. canario_html ordena os
    # alvos alfabeticamente e abre o primeiro. Medido no controlo positivo:
    # pela ordem do HTML o primeiro «item» da Chianti era uma pagina-hub
    # (CAPA_PROVAVEL) e o controlo reprovava; pela ordem do canario e uma
    # noticia. Julgar outro item que nao o do canario e provar outra coisa.
    primeiro = sorted(itens)[0]
    st3, b3, err3 = _get(primeiro)
    item = {"URL": primeiro, "HTTP": st3}
    if st3 != 200 or not b3:
        item["PORQUE"] = "item inacessivel: %s" % (err3 or st3)
        r.update(ITEM_ABERTO=item, ESTADO="NAO_SEI", PORQUE="a listagem lista, mas o primeiro item nao abriu")
        return r
    ret = RH.retrato_do_html(b3)
    item.update(HTML_KIND=ret["HTML_KIND"], CAPA_OU_MATERIA=ret["CAPA_OU_MATERIA"],
                LINKS=ret["LINKS"], NON_WHITESPACE_CHARACTERS=ret["NON_WHITESPACE_CHARACTERS"])
    r["ITEM_ABERTO"] = item
    if ret["HTML_KIND"] == "EMPTY":
        r.update(ESTADO="NAO_SEI", PORQUE="o item abriu sem texto visivel")
        return r
    if ret["CAPA_OU_MATERIA"] == "CAPA_PROVAVEL":
        r.update(ESTADO="NAO_SEI", PORQUE="o primeiro item parece capa/navegacao (gate CAPA != MATERIA)")
        return r
    r.update(ESTADO="PROVADA", PORQUE="listagem com %d itens; primeiro item aberto e %s" % (n, ret["CAPA_OU_MATERIA"]))
    return r


def alvos() -> list[dict]:
    """As 7 (SOURCE_ID sem contrato) + as HTML nunca caracterizadas que nao sao endpoint."""
    b = json.loads(BALDES.read_text(encoding="utf-8"))
    cands = {c["CANDIDATA_ID"]: c for c in json.loads(CANDIDATAS.read_text(encoding="utf-8"))["CANDIDATAS"]}
    sid = {n["CANDIDATE_ID"]: n["SOURCE_ID"] for n in json.loads(ALLOC.read_text(encoding="utf-8"))["NOVAS"]}
    endpoints = {e["CANDIDATE_ID"] for e in b["NUNCA_CARACTERIZADAS"]["HTML_ENDPOINTS_DE_FONTE_EXISTENTE"]}
    out = []
    for cid in b["POR_BALDE"]["COM_SOURCE_ID_SEM_CONTRATO"]:
        out.append({"CANDIDATE_ID": cid, "SOURCE_ID": sid.get(cid), "URL": cands[cid]["URL"],
                    "NOME": cands[cid]["NOME"], "BALDE": "COM_SOURCE_ID_SEM_CONTRATO"})
    for cid in b["POR_BALDE"]["NUNCA_CARACTERIZADAS"]:
        c = cands[cid]
        if c["TIPO"] in ("LINKEDIN", "INSTAGRAM", "FACEBOOK") or cid in endpoints:
            continue
        out.append({"CANDIDATE_ID": cid, "SOURCE_ID": None, "URL": c["URL"], "NOME": c["NOME"],
                    "BALDE": "NUNCA_CARACTERIZADAS_HTML"})
    return out


def contratar(provadas: list[dict]) -> list[dict]:
    """As PROVADAS com SOURCE_ID ganham contrato pelo molde da casa, com a rota provada."""
    import escrever_contratos as EC
    import fila as F
    import lifecycle as LC
    import validar_contratos as VC

    alloc = {n["SOURCE_ID"]: n for n in json.loads(ALLOC.read_text(encoding="utf-8"))["NOVAS"]}
    car = {f["CANDIDATE_ID"]: f for f in json.loads(CARACT.read_text(encoding="utf-8"))["FONTES"]}
    tabela = json.loads(CONTRATOS.read_text(encoding="utf-8"))
    ja = {c["SOURCE_ID"] for c in tabela["FONTES"]}
    feitos = []
    for p in provadas:
        sid = p.get("SOURCE_ID")
        if not sid or sid in ja:
            continue
        n = alloc[sid]
        f = car.get(n["CANDIDATE_ID"], {})
        novo = EC.contrato_html(n, f)
        novo["ACQUISITION"].update({"INDEX_URL": p["LISTAGEM"], "LINK_PATTERN": p["LINK_PATTERN"],
                                    "MAX_TARGETS": p["MAX_TARGETS"]})
        novo["ROUTE_PROVENANCE"] = {
            "MISSAO": "CANDIDATE-FEEDER-V1", "PASSO": 3, "FERRAMENTA": "curadoria/provar_listagem.py",
            "LISTAGEM": p["LISTAGEM"], "ITENS_VISTOS": p["ITENS"], "ITEM_ABERTO": p["ITEM_ABERTO"],
            "MAX_TARGETS_DERIVACAO": "min(N=%d, TETO=%d)" % (p["ITENS"], TETO_MAX_TARGETS),
            "PROVADO_EM": p["PROVADO_EM"], "EGRESSO": p.get("EGRESSO"),
            "NOTA": ("a caracterizacao dizia SMALL_ADAPTATION_REQUIRED = «SIM — ramo de indice»; "
                     "a listagem foi provada contra a rede e o item aberto nao e capa"),
        }
        novo["SOURCE_CONTRACT_VERSION"] = EC.VERSAO
        novo["SOURCE_CONTRACT_HASH"] = EC.hash_do_contrato(novo)
        novo["ONBOARDED_BY"] = "SOURCE-CURATOR · provar_listagem.py (CANDIDATE-FEEDER-V1, PASSO 3)"
        _, falhas = VC.validar([novo])
        if falhas:
            feitos.append({"SOURCE_ID": sid, "FEITO": False, "PORQUE": str(falhas[0])[:160]})
            continue
        tabela["FONTES"].append(novo)
        ja.add(sid)
        LC.registar(sid, LC.CANARY_PENDING,
                    "contrato escrito com listagem provada (%d itens); sai de CAPABILITY_BLOCK; "
                    "falta provar a rota" % p["ITENS"], evidence_ref="LISTAGENS-PROVADAS-V1.json")
        t = F.enfileirar(sid, F.VALIDATE_ROUTE, priority=55, motivo="listagem provada — validar rota e canariar")
        feitos.append({"SOURCE_ID": sid, "FEITO": True, "TASK_ID": t["TASK_ID"]})
    if any(x["FEITO"] for x in feitos):
        tabela["TOTAL"] = len(tabela["FONTES"])
        tabela["GERADO_EM"] = datetime.now(timezone.utc).isoformat()
        CONTRATOS.write_text(json.dumps(tabela, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return feitos


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--so", help="so estas CANDIDATE_ID (virgulas)")
    ap.add_argument("--max-fontes", type=int, default=0)
    ap.add_argument("--pausa", type=float, default=PAUSA_S)
    ap.add_argument("--contratar", action="store_true")
    ap.add_argument("--egresso", default="NAO SEI")
    a = ap.parse_args(argv)

    pedidos = {"TOTAL": 0}
    print("controlo positivo: %s" % CONTROLO["URL"])
    ctl = provar(CONTROLO["URL"], pedidos=pedidos, pausa=a.pausa)
    print("  -> %s · %s" % (ctl["ESTADO"], ctl["PORQUE"][:90]))
    if ctl["ESTADO"] != "PROVADA":
        print("  CONTROLO FALHOU: o leitor esta avariado; NENHUMA fonte e julgada (CLIENT_FAILURE)")
        SAIDA.write_text(json.dumps({"DATASET": "LISTAGENS-PROVADAS-V1", "CLIENT_FAILURE": True,
                                     "CONTROLO_POSITIVO": ctl}, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
        return 2

    lista = alvos()
    if a.so:
        quer = set(a.so.split(","))
        lista = [x for x in lista if x["CANDIDATE_ID"] in quer]
    if a.max_fontes:
        lista = lista[:a.max_fontes]

    resultados = []
    for i, x in enumerate(lista, 1):
        r = provar(x["URL"], pedidos=pedidos, pausa=a.pausa)
        r.update({k: x[k] for k in ("CANDIDATE_ID", "SOURCE_ID", "NOME", "BALDE")})
        r["PROVADO_EM"] = datetime.now(timezone.utc).isoformat()
        r["EGRESSO"] = a.egresso
        resultados.append(r)
        print("  %2d/%d %-10s %-9s %-17s %s" % (i, len(lista), x["CANDIDATE_ID"], x["SOURCE_ID"] or "-",
                                                r["ESTADO"], (r["LISTAGEM"] or r["PORQUE"])[:70]))

    # Com --so, os resultados novos SUBSTITUEM os das mesmas candidatas e os
    # outros ficam: uma segunda passada nao apaga a primeira.
    contratadas_antes = []
    if a.so and SAIDA.exists():
        antes = json.loads(SAIDA.read_text(encoding="utf-8"))
        novos = {r["CANDIDATE_ID"] for r in resultados}
        resultados = [r for r in antes.get("RESULTADOS", []) if r["CANDIDATE_ID"] not in novos] + resultados
        resultados.sort(key=lambda r: (r["BALDE"], r["CANDIDATE_ID"]))
        contratadas_antes = antes.get("CONTRATADAS", []) or []
        pedidos["TOTAL"] += antes.get("CADENCIA", {}).get("PEDIDOS_TOTAL", 0)

    por_estado = Counter(r["ESTADO"] for r in resultados)
    saida = {
        "DATASET": "LISTAGENS-PROVADAS-V1",
        "LEI": ("descer do indice ao item, por fonte, contra a rede: 2+ itens debaixo de uma "
                "seccao e o primeiro item aberto sem capa. NAO SEI e resultado; 403 e resposta; "
                "o controlo positivo corre antes e, se falhar, ninguem e julgado."),
        "CORRIDO_EM": datetime.now(timezone.utc).isoformat(),
        "EGRESSO": a.egresso,
        "CADENCIA": {"PAUSA_S": a.pausa, "MAX_PEDIDOS_POR_FONTE": MAX_PEDIDOS_POR_FONTE,
                     "PEDIDOS_TOTAL": pedidos["TOTAL"]},
        "CONTROLO_POSITIVO": ctl,
        "FONTES_JULGADAS": len(resultados),
        "POR_ESTADO": dict(por_estado),
        "POR_BALDE_E_ESTADO": dict(Counter("%s | %s" % (r["BALDE"], r["ESTADO"]) for r in resultados)),
        "RESULTADOS": resultados,
    }
    if a.contratar:
        feitos = contratar([r for r in resultados if r["ESTADO"] == "PROVADA" and r.get("SOURCE_ID")])
        saida["CONTRATADAS"] = contratadas_antes + feitos
        print("contratadas: %s" % json.dumps(feitos, ensure_ascii=False))
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("POR_ESTADO %s · pedidos %d · escrito %s" % (dict(por_estado), pedidos["TOTAL"], SAIDA.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
