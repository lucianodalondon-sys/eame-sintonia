#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GRAFO DE DEPENDENCIA MINIMO — `INT-LAW-070..077`, e so ele.

    MISSAO   INDEPENDENCIA-V1 (defeitos D12 e D16 da Intelligence)
    python3 -m unittest tests.test_independencia_de_fontes -v

OS DOIS DEFEITOS QUE ESTE FICHEIRO FECHA
---------------------------------------
    D12  o MESMO documento lido duas vezes contava como DUAS evidencias.
    D16  o motor nao contava fontes independentes: na 1.a rodada real (26/09)
         6 de 9 sinais vinham de myfruit.it, e o numero publicado era 9.

    NOVE LEITURAS DE UM SO JORNAL NAO SAO NOVE TESTEMUNHAS.

A PERGUNTA QUE ELE RESPONDE, E MAIS NENHUMA
-------------------------------------------
    QUANTAS EVIDENCIAS DISTINTAS HA AQUI, DE QUANTOS ORIGINADORES
    INDEPENDENTES, QUANTO PESA O MAIOR DELES, E ISTO E CONVERGENCIA?

Tres camadas, e nenhuma se comprime na outra (`INT-LAW-075`):

    SINAL      cada entrada que chegou              EXTERNAL_SIGNAL_COUNT
    EVIDENCIA  o mesmo documento conta UMA vez      EVIDENCE_BASE_COUNT
    FONTE      o mesmo originador conta UMA vez     INDEPENDENT_SOURCE_COUNT

AS REGRAS, E PORQUE CADA UMA E CONSERVADORA
-------------------------------------------
    1. MESMO DOCUMENTO = UMA EVIDENCIA (`INT-LAW-072`). Duas entradas sao o mesmo
       documento se partilham QUALQUER uma destas chaves: DOCUMENT_ID declarado,
       SHA-256 dos bytes, ou o endereco do documento. Vistas diferentes (capa,
       metadado, corpo; duas capturas da mesma pagina) continuam uma evidencia.
       Duas capturas do mesmo endereco com bytes diferentes ficam marcadas
       `VERSOES_DIFERENTES` — `INT-LAW-074` manda classificar, nao somar.

    2. MESMO ORIGINADOR = UMA FONTE (`INT-LAW-071`). O originador sai, por esta
       ordem: do que a Collection DECLAROU (ORIGINATOR, REPUBLISHED_FROM, ...);
       da pagina/conta que publicou numa plataforma (PAGE_ID); do dominio do
       endereco (numa plataforma, do canal no endereco); do SOURCE_ID. As chaves
       unem-se: duas entradas com o mesmo dominio, OU o mesmo SOURCE_ID, OU o
       mesmo documento, sao a mesma fonte. Unir a mais so ESCONDE independencia.
       A EXCECAO, medida no pacote V2.1: quando quem fala ja esta dito (declarado,
       pagina, canal), o SOURCE_ID NAO une — ali ele e a plataforma inteira, e
       unir por ele fundia a Bayer com a BASF na Biblioteca de Anuncios.

    3. SEM ORIGINADOR = NAO SEI. Uma entrada sem endereco, sem SOURCE_ID e sem
       originador declarado nao e contada como fonte nova: nao se sabe se e.
       O numero exacto passa a `NAO SEI`, e ficam o MINIMO provado e o MAXIMO
       possivel ao lado.

    4. CONVERGENCIA SO COM INDEPENDENCIA (`INT-LAW-077`). `CONVERGE` exige duas
       fontes independentes PROVADAS (o minimo, nao o maximo). Com uma so fonte
       possivel e `NAO_CONVERGE`; com duas possiveis e uma provada e `NAO SEI`.

    5. VALIDACAO ESTRUTURAL NAO E FONTE (`INT-LAW-076`). Rotulo, registo e
       catalogo contam em STRUCTURAL_VALIDATION_COUNT, e nunca em fontes.

O QUE ELE NAO FAZ, E DIZ QUE NAO FAZ
------------------------------------
    NAO deteta sindicacao por semelhanca de texto (`INT-LAW-081`: semelhanca nao
    prova equivalencia). Cópia com bytes diferentes em dominio diferente so e
    apanhada se a Collection DECLARAR o originador. Por isso a independencia
    por dominio chama-se `ORIGINADOR_DISTINTO`, e nao «independencia provada».

    NAO cunha SOURCE_ID nem DOCUMENT_ID (`INT-LAW-083`). As chaves do grafo sao
    internas, prefixadas, e nao saem daqui como identidade de ninguem.
"""
from __future__ import annotations

from collections import OrderedDict
from urllib.parse import urlsplit

NAO_SEI = "NAO SEI"
VERSAO = "GRAFO-DE-DEPENDENCIA/v1"

CONVERGE = "CONVERGE"
NAO_CONVERGE = "NAO_CONVERGE"

#: Onde a Collection pode declarar a origem verdadeira de uma copia. Declarado
#: vence dominio: uma republicacao no site B de uma nota do site A e do A.
CAMPOS_DE_ORIGINADOR = ("ORIGINATOR", "ORIGINADOR", "REPUBLISHED_FROM",
                        "SYNDICATED_FROM", "ORIGINAL_SOURCE")
#: Em plataforma, quem fala e a PAGINA/CONTA que publicou, e nao a plataforma.
#: `PAGE_ID` e o numero da pagina do anunciante que a Biblioteca de Anuncios da
#: Meta devolve, gravado pela coleta — nao e cunhado aqui.
CAMPOS_DE_PAGINA = ("PAGE_ID", "ADVERTISER_ID", "CHANNEL_ID")
CAMPOS_DE_DOCUMENTO = ("DOCUMENT_ID", "SOURCE_DOCUMENT_ID")
CAMPOS_DE_SHA = ("SHA256", "TEXTO_SHA256", "CONTENT_SHA256", "RAW_SHA256",
                 "sha256")
CAMPOS_DE_ENDERECO = ("DOCUMENT_URL", "URL", "SOURCE_URL")

#: Plataformas onde o dominio NAO e o originador: dois canais do YouTube nao
#: sao a mesma fonte. Aqui o originador e o canal/perfil, se o endereco o disser;
#: se nao disser (`/watch?v=`), o dominio nao serve e cai-se no SOURCE_ID.
PLATAFORMAS = {"youtube.com", "youtu.be", "facebook.com", "instagram.com",
               "linkedin.com", "x.com", "twitter.com", "tiktok.com",
               "medium.com", "t.me", "wordpress.com", "blogspot.com"}
#: Resolvedores: o endereco diz ONDE o documento se acha, e nao QUEM o escreveu.
#: 86 de 88 registos cientificos do pacote V2.1 estao em doi.org, com SOURCE_ID
#: `SRC_DOI_ORG`: tomar o dominio (ou esse SOURCE_ID) fundia a Universidade de
#: Milao com o Instituto de Agricultura Sostenible numa «fonte» so. Aqui quem
#: fala e a instituicao declarada no registo; sem ela, NAO SEI.
RESOLVEDORES = {"doi.org", "handle.net", "hdl.handle.net"}
CAMPOS_DE_INSTITUICAO = ("INSTITUTION", "INSTITUICAO")
#: Sufixos de dois niveis em que o «dominio registavel» tem tres rotulos.
SUFIXOS_DUPLOS = {"gov.it", "edu.it", "co.uk", "ac.uk", "gov.uk", "com.br",
                  "gov.br", "org.br", "com.au", "co.jp"}


def _vazio(v) -> bool:
    return (v is None or v == "" or v == []
            or (isinstance(v, str) and v.strip().upper().startswith(NAO_SEI)))


def _primeiro(ev: dict, campos) -> str | None:
    for c in campos:
        v = ev.get(c)
        if isinstance(v, (list, tuple)):
            v = next((x for x in v if not _vazio(x)), None)
        if not _vazio(v):
            return str(v).strip()
    return None


def _e_endereco(v) -> bool:
    return isinstance(v, str) and v.strip().lower().startswith(("http://", "https://"))


def endereco_do_documento(ev: dict) -> str | None:
    """O endereco do DOCUMENTO, normalizado: sem esquema, sem `www.`, sem
    fragmento, sem barra final. A query fica — `?id=7` e `?id=8` sao dois
    documentos."""
    url = _primeiro(ev, CAMPOS_DE_ENDERECO)
    if url is None and _e_endereco(ev.get("ITEM_ID")):
        url = ev["ITEM_ID"]
    if url is None:
        urls = ev.get("SOURCE_URLS") or []
        url = next((u for u in urls if _e_endereco(u)), None)
    if url is None or not _e_endereco(url):
        return None
    p = urlsplit(url.strip())
    host = (p.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if not host:
        return None
    caminho = p.path.rstrip("/")
    return host + caminho + (("?" + p.query) if p.query else "")


def dominio_registavel(host: str) -> str:
    rot = host.lower().split(".")
    if rot and rot[0] == "www":
        rot = rot[1:]
    n = 3 if ".".join(rot[-2:]) in SUFIXOS_DUPLOS else 2
    return ".".join(rot[-n:])


def originador_por_endereco(ev: dict) -> str | None:
    """Dominio registavel; nas plataformas, dominio + canal. `None` se o
    endereco nao chega para saber quem fala."""
    end = endereco_do_documento(ev)
    if end is None:
        return None
    host, _, caminho = end.partition("/")
    host = host.split("?")[0]
    dom = dominio_registavel(host)
    if dom not in PLATAFORMAS:
        return dom
    if dom in ("wordpress.com", "blogspot.com") and host != dom:
        return host                      # fulano.blogspot.com e o blog do fulano
    partes = [p for p in caminho.split("?")[0].split("/") if p]
    if not partes:
        return None
    if partes[0].startswith("@"):
        return dom + "/" + partes[0].lower()
    if partes[0] in ("channel", "c", "user", "in", "company", "pages") and len(partes) > 1:
        return dom + "/" + partes[0] + "/" + partes[1].lower()
    if dom in ("x.com", "twitter.com", "instagram.com", "tiktok.com",
               "facebook.com", "medium.com", "t.me") and partes[0] not in (
                   "watch", "p", "reel", "status", "share", "video", "events",
                   "ads"):                       # a Biblioteca de Anuncios nao e anunciante
        return dom + "/" + partes[0].lower()
    return None


def chaves_de_documento(ev: dict) -> set:
    k = set()
    d = _primeiro(ev, CAMPOS_DE_DOCUMENTO)
    if d:
        k.add("DOC:" + d)
    s = _primeiro(ev, CAMPOS_DE_SHA)
    if s:
        k.add("SHA:" + s.lower())
    e = endereco_do_documento(ev)
    if e:
        k.add("URL:" + e)
    return k


def chaves_de_originador(ev: dict) -> tuple:
    """`(chaves, base)`. A base diz de onde o originador saiu, para quem ler."""
    dec = _primeiro(ev, CAMPOS_DE_ORIGINADOR)
    pag = _primeiro(ev, CAMPOS_DE_PAGINA)
    k, base = set(), None
    if dec:
        o = originador_por_endereco({"URL": dec}) if _e_endereco(dec) else dec.lower()
        k.add("ORIG:" + (o or dec.lower()))
        base = "DECLARADO"
    elif pag:
        k.add("ORIG:pagina/" + pag.lower())
        base = "PAGINA"
    end = endereco_do_documento(ev) if base is None else None
    if end and dominio_registavel(end.partition("/")[0].split("?")[0]) in RESOLVEDORES:
        inst = _primeiro(ev, CAMPOS_DE_INSTITUICAO)
        if inst:
            k.add("ORIG:instituicao/" + inst.lower())
            return k, "INSTITUICAO"
        return k, None                  # o resolvedor nao diz quem: NAO SEI
    if base is None:
        o = originador_por_endereco(ev)
        if o:
            k.add("ORIG:" + o)
            base = "PLATAFORMA" if "/" in o else "DOMINIO"
    # ⚠️ O SOURCE_ID UNE — mas nao quando quem fala ja esta dito. Numa plataforma
    # o SOURCE_ID costuma ser a PLATAFORMA inteira (`SRC_FACEBOOK_COM` cobre 351
    # anuncios de 4 anunciantes no pacote V2.1): unir por ele fundia a Bayer com
    # a BASF. Medido na primeira passagem desta missao, e corrigido aqui.
    if base in ("DECLARADO", "PAGINA", "PLATAFORMA"):
        return k, base
    sids = ev.get("SOURCE_IDS")
    sids = [s for s in (sids if isinstance(sids, (list, tuple)) else []) if not _vazio(s)]
    if not _vazio(ev.get("SOURCE_ID")):
        sids = [ev["SOURCE_ID"]] + sids
    for s in sids:
        k.add("SID:" + str(s).strip())
    if base is None and sids:
        base = "SOURCE_ID"
    return k, base


def referencia(ev: dict, i: int) -> str:
    for c in ("ID", "SIGNAL_ID", "ITEM_ID", "RAW_OBSERVATION_ID"):
        if not _vazio(ev.get(c)):
            return str(ev[c])
    return f"#{i}"


class _Uniao:
    def __init__(self, n):
        self.p = list(range(n))

    def raiz(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def unir(self, a, b):
        ra, rb = self.raiz(a), self.raiz(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def _grupos(chaves: list, u: _Uniao) -> list:
    dono = {}
    for i, ks in enumerate(chaves):
        for k in sorted(ks):
            if k in dono:
                u.unir(i, dono[k])
            else:
                dono[k] = i
    g = OrderedDict()
    for i in range(len(chaves)):
        g.setdefault(u.raiz(i), []).append(i)
    return list(g.values())


def grafo(evidencias: list, estrutural=None) -> dict:
    """O grafo de UM conjunto de apoios. Nao junta perguntas: quem chama e que
    decide o que e «o mesmo fato» (ver `por_fato`).

    `estrutural(ev) -> bool` separa rotulo/registo/catalogo (`INT-LAW-076`):
    esses contam em STRUCTURAL_VALIDATION_COUNT e ficam fora das fontes.
    """
    evidencias = [e for e in (evidencias or []) if isinstance(e, dict)]
    estr = [e for e in evidencias if estrutural and estrutural(e)]
    sinais = [e for e in evidencias if not (estrutural and estrutural(e))]
    n = len(sinais)
    refs = [referencia(e, i) for i, e in enumerate(sinais)]

    # 1 · EVIDENCIA: o mesmo documento conta uma vez
    kdoc = [chaves_de_documento(e) for e in sinais]
    ud = _Uniao(n)
    docs = _grupos(kdoc, ud)
    duplicatas = []
    for g in docs:
        if len(g) < 2:
            continue
        comuns = set.intersection(*(kdoc[i] for i in g)) if g else set()
        shas = {k for i in g for k in kdoc[i] if k.startswith("SHA:")}
        duplicatas.append({
            "MANTIDA": refs[g[0]],
            "COLAPSADAS": [refs[i] for i in g[1:]],
            "PORQUE": sorted({k.split(":", 1)[0] for k in comuns}) or ["CADEIA_DE_CHAVES"],
            "VERSOES_DIFERENTES": len(shas) > 1,
        })

    # 2 · FONTE: o mesmo originador conta uma vez — e o mesmo documento tambem
    korig, bases = [], []
    for i, e in enumerate(sinais):
        k, b = chaves_de_originador(e)
        korig.append(k)
        bases.append(b)
    uf = _Uniao(n)
    # quem partilha documento partilha fonte (copia identica em dois sitios)
    for g in docs:
        for i in g[1:]:
            uf.unir(g[0], i)
    grupos_f = _grupos([k if k else {f"__SEM__{i}"} for i, k in enumerate(korig)], uf)

    familias, sem_originador, grupos_sem = [], [], 0
    for g in grupos_f:
        if all(not korig[i] for i in g):
            # um grupo sem originador e UMA fonte possivel (o mesmo documento
            # lido duas vezes continua um so), nunca tantas quantas as leituras
            sem_originador.extend(refs[i] for i in g)
            grupos_sem += 1
            continue
        origs = sorted({k[5:] for i in g for k in korig[i] if k.startswith("ORIG:")})
        sids = sorted({k[4:] for i in g for k in korig[i] if k.startswith("SID:")})
        nome = origs[0] if origs else ("SOURCE_ID:" + sids[0])
        familias.append({
            "ORIGINADOR": nome,
            "ORIGINADORES_UNIDOS": origs,
            "SOURCE_IDS": sids,
            "BASE": sorted({bases[i] for i in g if bases[i]}),
            "SINAIS": len(g),
            "EVIDENCIAS": len({ud.raiz(i) for i in g}),
            "REFERENCIAS": [refs[i] for i in g],
        })
    familias.sort(key=lambda f: (-f["SINAIS"], f["ORIGINADOR"]))

    minimo = len(familias) + (1 if (sem_originador and not familias) else 0)
    maximo = len(familias) + grupos_sem
    exacto = len(familias) if not sem_originador else NAO_SEI
    dom = familias[0] if familias else None

    porque = []
    if n == 0:
        conv = NAO_CONVERGE
        porque.append("nenhum sinal externo: validacao estrutural nao e sinal (INT-LAW-076)")
    elif minimo >= 2:
        conv = CONVERGE
        porque.append(f"{minimo} originadores distintos provados")
    elif maximo < 2:
        conv = NAO_CONVERGE
        if n > 1:
            porque.append(f"{n} sinais, 1 originador: repeticao nao e convergencia (INT-LAW-071)")
        else:
            porque.append("um sinal so: um documento nao e convergencia")
    else:
        conv = NAO_SEI
        porque.append(f"{len(sem_originador)} sinal(is) sem originador: a independencia nao esta provada (INT-LAW-070)")

    return {
        "VERSAO": VERSAO,
        "LEI": "INT-LAW-070..077 · INT-LAW-092",
        "EXTERNAL_SIGNAL_COUNT": n,
        "EVIDENCE_BASE_COUNT": len(docs),
        "INDEPENDENT_SOURCE_COUNT": exacto,
        "INDEPENDENT_SOURCE_COUNT_MIN": minimo,
        "INDEPENDENT_SOURCE_COUNT_MAX": maximo,
        "STRUCTURAL_VALIDATION_COUNT": len(estr),
        "DOMINANT_SOURCE": dom["ORIGINADOR"] if dom else None,
        "DOMINANT_SOURCE_SIGNALS": dom["SINAIS"] if dom else 0,
        # a fracao do MAIOR originador sobre os SINAIS que chegaram: e o numero
        # que teria mostrado «6 de 9 = 66,7 % myfruit.it» na 1.a rodada
        "DOMINANT_SOURCE_SHARE_PCT": round(100.0 * dom["SINAIS"] / n, 1) if dom and n else None,
        "CONVERGENCE": conv,
        "CONVERGENCE_WHY": porque,
        "INDEPENDENCE_BASIS": ("ORIGINADOR_DISTINTO — dominio, SOURCE_ID ou declaracao "
                               "da Collection; sindicacao com bytes diferentes so e "
                               "apanhada se for declarada"),
        "DOCUMENT_DUPLICATES": duplicatas,
        "SOURCE_FAMILIES": familias,
        "SEM_ORIGINADOR": sem_originador,
    }


def por_fato(evidencias: list, chave_do_fato, estrutural=None) -> dict:
    """Um grafo POR FATO (`INT-LAW-077`: convergencia exige compatibilidade).

    `chave_do_fato(ev)` devolve a chave, ou `None`/`NAO SEI` quando o fato nao
    foi declarado. Esses nao convergem com ninguem: juntar apoios cujo fato se
    desconhece seria contar concordancia sobre coisas que podem ser diferentes.
    """
    grupos = OrderedDict()
    for e in evidencias or []:
        if not isinstance(e, dict):
            continue
        k = chave_do_fato(e)
        k = NAO_SEI if _vazio(k) else str(k)
        grupos.setdefault(k, []).append(e)
    out = OrderedDict()
    for k in sorted(grupos, key=lambda x: (x == NAO_SEI, x)):
        g = grafo(grupos[k], estrutural)
        if k == NAO_SEI and g["CONVERGENCE"] == CONVERGE:
            g["CONVERGENCE"] = NAO_SEI
            g["CONVERGENCE_WHY"] = g["CONVERGENCE_WHY"] + [
                "o fato destes sinais nao foi declarado: fontes distintas sobre "
                "fatos desconhecidos nao sao concordancia (INT-LAW-077)"]
        out[k] = g
    return out
