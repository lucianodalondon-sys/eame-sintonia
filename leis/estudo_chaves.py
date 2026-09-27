#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESTUDOS-CHAVES — CULTURA, PROBLEMA e o LUGAR DO ESTUDO lidos no titulo+resumo de um estudo (T5).

    chaves_do_estudo(texto) -> {"CULTURA": {...}, "PROBLEMA": {...}, "REGIAO_DO_FATO": {...}, "CAP_SCI": {...}}

POR QUE EXISTE. Medido na Sala real (27/09): os 100 estudos do universo T5 (OpenAlex, `EU-T5-001`)
entraram com `janela_declarada` toda NAO SEI — CULTURA, PROBLEMA, FASE e REGIAO_DO_FATO em 100/100. So
PUBLISHED_AT vinha declarado. A porta so lia a cultura fora de T1 no TITULO e com o vocabulario ITALIANO
da regua (`admissao._cultura_fora_da_regua`), e um resumo cientifico escreve «grapevine», «Plasmopara
viticola», «olive». Sem cultura e praga a Intelligence nao cruza estudo -> cultura -> praga -> produto.

NAO HA SEGUNDO VOCABULARIO. Este ficheiro nao escreve nome de cultura, de praga nem de lugar: COMPOE os
que ja existem, cada um com o seu dono, pela ordem em que se leem:

    CULTURA   coleta/pesquisadores_t6.py::CULTURAS    ingles + italiano + nome cientifico (o lexico T6)
              leis/boletim_do_campo.py::CULTURAS/FORMAS   o italiano dos boletins
              admissao.CULTURA_OBRIGATORIA[_EN]["T1"]     a regua T1 (a forma fica como a regua a escreve)
    PROBLEMA  coleta/pesquisadores_t6.py::PROBLEMAS   ingles + italiano + nome cientifico
              leis/boletim_do_campo.py::PROBLEMAS    o vocabulario de pragas (nome por MESMO_PROBLEMA)
    LUGAR     leis/fato_local.py::REGIOES/PROVINCIAS  o gazetteer (cobertura declarada, nao presumida)
              coleta/pesquisadores_t6.py::REGIOES_EN/EXONIMOS/ZONAS_IT/PAIS_IT   o nome ingles

AS LEIS
  · D112 · ENTITY_SOURCE = SPAN. Cada valor sai com o TRECHO LITERAL do texto (as letras como a fonte as
    escreveu, com o inicio e o fim), e `BASE` e esse trecho. Nada e inferido: sem trecho, nao ha valor.
  · AMBIGUO = NAO SEI. Uma forma que os donos ja declararam ambigua («vite» = plural de «vita», «mais»,
    «pero» = «pero/mas», «mora» = «in mora», «vine» = qualquer trepadeira) sozinha NAO da valor: fica em
    `AMBIGUAS`, com o trecho. So conta se a mesma cultura tiver outra forma sem ambiguidade no texto.
    Um lugar homonimo de palavra comum («Prato», «Potenza», «Latina», «Lodi», «Fermo», «Cuneo») so conta
    depois de «provincia di / province of».
  · UM TRECHO, UMA ENTIDADE. Dois vocabularios que casam no mesmo pedaco do texto dao um valor so — o do
    primeiro dono da ordem acima («Lobesia botrana» e `tignoletta` do lexico T6, e nao duas pragas).
  · O LUGAR DO ESTUDO SO QUANDO O TEXTO DIZ ONDE O ESTUDO FOI FEITO: um verbo ou nome de experimento
    («trials», «experiments», «samples were collected», «conducted», «prove», «condotte», «campionamento»)
    na MESMA frase, e o lugar logo a seguir a uma preposicao («in Tuscany», «field trials in Apulia», «nella
    provincia di Lecce»). Nomear um lugar nao prova que o ensaio foi la (PLACE_MENTION != FACT_LOCATION).
  · AFILIACAO NUNCA VIRA LUGAR DO ESTUDO (INT-LAW-102). Um nome logo depois de «University of / Istituto di
    / Department of» nao conta, mesmo com um verbo de experimento na frase.
  · CAP-SCI · ESTUDO NUNCA VIRA INCIDENCIA DE CAMPO (AGENTS.md: «ciencia nao vira incidencia de campo»).
    O PROBLEMA de um estudo e NOMEADO pelo estudo — `ESTADO = NOMEADO_NO_ESTUDO`, nunca PRESENTE — e o
    lugar e `LOCAL_DO_ESTUDO`, nunca ocorrencia. FACT_TIME e FACT_LOCATION do item nao se tocam aqui.
  · PUBLICACAO != PERIODO. Este ficheiro nao le datas.

Funcao PURA: sem rede, sem banco, sem ficheiros escritos.
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata

EXTRATOR = "estudo-chaves-v1"
ENTITY_SOURCE = "SPAN"                   # D112
AUSENCIA = "NAO SEI"
NATUREZA = "ESTUDO_CIENTIFICO"
ESTADO_DO_PROBLEMA = "NOMEADO_NO_ESTUDO"
KIND_DO_LUGAR = "LOCAL_DO_ESTUDO"
LEI_CAP_SCI = ("CAP-SCI: estudo nunca vira incidencia de campo (AGENTS.md; BIBLIA-DE-ENGENHARIA-DA-"
               "INTELLIGENCE.md §CAP-SCI). O texto NOMEIA; nao prova que foi observado no campo.")
LEI_LUGAR = ("so o lugar onde o TEXTO diz que o estudo foi feito (verbo/nome de experimento na mesma frase + "
             "preposicao); afiliacao do autor nunca (INT-LAW-102); nunca source_location")

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── as formas que os DONOS ja declararam ambiguas (citadas, nao inventadas) ─────────────────────────
AMBIGUAS_CULTURA = {
    "vite": "plural de «vita» (coleta/pesquisadores_t6.py, comentario de CULTURAS)",
    "mais": "«mais» em portugues/frances (coleta/pesquisadores_t6.py; admissao.py, regua T1)",
    "pero": "«pero» = «mas» sem acento (admissao.py, regua T1)",
    "mora": "«in mora», «interessi di mora» (admissao._MORA_QUE_NAO_E_FRUTA)",
    "vine": "qualquer planta trepadeira; o gabarito T1 em ingles NAO foi medido (admissao.py)",
    "vines": "idem «vine»",
}
# provincias do gazetteer que sao tambem palavra comum em italiano/ingles
AMBIGUOS_LUGAR = {
    "prato": "«prato» = relvado", "potenza": "«potenza» = potencia", "latina": "«latina» (adjectivo)",
    "lodi": "«lodi» = louvores", "fermo": "«fermo» = parado", "cuneo": "«cuneo» = cunha",
}

# ── o experimento: a frase tem de dizer que ALGO FOI FEITO ali ─────────────────────────────────────
# ⚠️ FORA, e medido nas fixtures: «established» e «located» («Xylella has become ESTABLISHED in Apulia» e
# linguagem de INCIDENCIA, nao de ensaio — CAP-SCI), «situato/ubicato» (idem) e «raccolta» sozinha (e a
# colheita: «la raccolta in Puglia»). «study area is located in…» continua a contar, por «study area».
_PISTA_DE_ESTUDO = re.compile(
    r"(?<![a-z])(?:"
    # en
    r"trials?|experiments?|experimental|field\s+(?:study|studies|surveys?|plots?|conditions|work)|"
    r"surveys?|surveyed|sampl(?:ed|ing|es)|collected|monitor(?:ed|ing)|conducted|carried\s+out|"
    r"performed|set\s+up|study\s+(?:area|sites?)|"
    # it
    r"prov[ae]\s+(?:sperimentali|di\s+campo|in\s+campo)|sperimentazion[ei]|sperimental[ei]|esperiment[oi]|"
    r"campionament[oi]|campion[ei]\s+(?:raccolt|prelevat)\w*|prelevat[oiae]|monitoraggi?o|"
    r"condott[oaie]|effettuat[oaie]|realizzat[oaie]|svolt[oaie]|allestit[oaie]|indagin[ei]"
    r")(?![a-z])")
# a preposicao logo antes do lugar (cauda do texto dobrado ate ao lugar)
_PREPOSICAO = re.compile(
    r"(?<![a-z])(?:in|at|near|across|throughout|from|within|of|nel|nella|nelle|nei|negli|nell'"
    r"|della|delle|dei|di|a|ad)\s*(?:the\s+)?"
    r"(?:(?:province|region|area|district|island|provincia|regione|zona|territorio)\s+"
    r"(?:of|di|del|della|dell')\s*)?$")
_PROVINCIA_DE = re.compile(r"(?:province|provincia)\s+(?:of|di)\s*$")
# «University of Pisa»: o nome logo depois disto e da AFILIACAO (o mesmo criterio do lexico T6)
_INSTITUCIONAL = re.compile(
    r"(?<![a-z])(?:universit\w*(?:\s+degli\s+studi)?|institut\w*|istituto|department|dipartimento|faculty|"
    r"facolta|cnr|crea|research\s+cent(?:re|er)|centro\s+di\s+ricerca)\W+(?:of|di|degli|della|del)?\W*$")
_COORDENADO = re.compile(r"^\s*(?:,\s*(?:and\s+|e\s+|ed\s+)?|\s+(?:and|e|ed|or|o)\s+)(?:the\s+)?"
                         r"(?:(?:province|region|provincia|regione)\s+(?:of|di|del|della)\s+)?$")


# ═════════════════════════════════════════════ o texto dobrado, com o mapa para o original
def _dobrar_com_mapa(texto: str):
    """Minusculas, sem acento, travessao e apostrofo unificados — e, para cada letra dobrada, a posicao
    dela no ORIGINAL. E o mapa que permite devolver o trecho LITERAL (D112), com as letras da fonte."""
    out, mapa = [], []
    for i, c in enumerate(str(texto or "")):
        if c in "‐‑‒–—−":
            c = "-"
        elif c in "’‘`´":
            c = "'"
        for d in unicodedata.normalize("NFKD", c):
            if unicodedata.combining(d):
                continue
            for e in d.lower():
                out.append(e)
                mapa.append(i)
    return "".join(out), mapa


def _dobrar(s: str) -> str:
    return _dobrar_com_mapa(s)[0]


def _rx(forma: str):
    f = re.escape(_dobrar(forma).strip()).replace(r"\ ", r"\s+")
    return re.compile(r"(?<![a-z0-9])%s(?![a-z0-9])" % f)


def _literal(texto, mapa, ini, fim):
    return texto[mapa[ini]:mapa[fim - 1] + 1]


# ═════════════════════════════════════════════ os vocabularios, compostos dos donos
_VOC = {}


def _t6():
    sys.path.insert(0, os.path.join(_RAIZ, "coleta"))
    import pesquisadores_t6 as T6                    # noqa: PLC0415 — o lexico T6 (ingles/cientifico)
    return T6


def _bc():
    sys.path.insert(0, os.path.join(_RAIZ, "leis"))
    import boletim_do_campo as BC                    # noqa: PLC0415 — o vocabulario de pragas
    return BC


def _regua_t1():
    """As formas da regua T1 (italiano, ingles e as que so servem a chave). Lidas do dono, nunca copiadas."""
    sys.path.insert(0, os.path.join(_RAIZ, "admissao"))
    import admissao as ADM                           # noqa: PLC0415
    formas = []
    for v in (ADM.CULTURA_OBRIGATORIA["T1"], ADM.CULTURA_OBRIGATORIA_EN["T1"], ADM.CULTURA_SO_DA_CHAVE):
        formas += [f for f in v.split("|") if f]
    return formas


def vocabulario_de_cultura():
    """[(forma, nome, dono)] — pela ordem dos donos; dentro de cada dono, a forma mais longa primeiro."""
    if "CULTURA" not in _VOC:
        T6, BC = _t6(), _bc()
        voc, vistas = [], set()

        def por(dono, pares):
            for forma, nome in sorted(pares, key=lambda p: -len(p[0])):
                f = _dobrar(forma).strip()
                if f and f not in vistas:
                    vistas.add(f)
                    voc.append((f, nome, dono))
        por("coleta/pesquisadores_t6.py::CULTURAS",
            [(t, nome) for nome, termos in T6.CULTURAS.items() for t in termos])
        por("leis/boletim_do_campo.py::CULTURAS",
            [(c, BC._forma(c)) for c in list(BC.CULTURAS) + list(BC.FORMAS)])
        # a regua T1 nao tem ponte entre linguas: a forma e o nome, como `janela_declarada` ja faz
        por("admissao.CULTURA_OBRIGATORIA[T1] (regua T1)", [(f, _dobrar(f)) for f in _regua_t1()])
        _VOC["CULTURA"] = voc
    return _VOC["CULTURA"]


def vocabulario_de_problema():
    """[(forma ou regex, nome, dono, e_regex)] — o lexico T6 primeiro, depois o vocabulario de pragas."""
    if "PROBLEMA" not in _VOC:
        T6, BC = _t6(), _bc()
        voc = [(t, nome, "coleta/pesquisadores_t6.py::PROBLEMAS", False)
               for nome, termos in T6.PROBLEMAS.items() for t in termos]
        voc.sort(key=lambda x: -len(x[0]))
        voc.append((BC._RE_PROBLEMA, None, "leis/boletim_do_campo.py::PROBLEMAS (nome por MESMO_PROBLEMA)",
                    True))
        _VOC["PROBLEMA"] = voc
    return _VOC["PROBLEMA"]


def vocabulario_de_lugar():
    """[(forma, nome, precisao, dono)]: regioes e provincias do gazetteer, com o nome ingles do lexico T6."""
    if "LUGAR" not in _VOC:
        T6 = _t6()
        sys.path.insert(0, os.path.join(_RAIZ, "leis"))
        import fato_local as FL                      # noqa: PLC0415 — o gazetteer (so se LE)
        voc, vistas = [], set()

        def por(forma, nome, precisao, dono):
            f = _dobrar(forma).strip()
            if f and f not in vistas:
                vistas.add(f)
                voc.append((f, nome, precisao, dono))
        for reg in FL.REGIOES:
            for f in (reg,) + tuple(T6.REGIOES_EN.get(reg, ())):
                por(f, reg, "REGIAO", "leis/fato_local.py::REGIOES + pesquisadores_t6.REGIOES_EN")
        for prov in FL.PROVINCIAS:
            for f in (prov,) + tuple(T6.EXONIMOS.get(prov, ())):
                por(f, prov, "PROVINCIA", "leis/fato_local.py::PROVINCIAS + pesquisadores_t6.EXONIMOS")
        for zona, termos in T6.ZONAS_IT.items():
            for f in termos:
                por(f, zona, "ZONA", "coleta/pesquisadores_t6.py::ZONAS_IT")
        for f in T6.PAIS_IT:
            por(f, "Italia", "PAIS", "coleta/pesquisadores_t6.py::PAIS_IT")
        voc.sort(key=lambda x: -len(x[0]))
        _VOC["LUGAR"] = voc
    return _VOC["LUGAR"]


# ═════════════════════════════════════════════ ler
def _sobrepoe(a, b):
    return a[0] < b[1] and b[0] < a[1]


def _achados_de_cultura(texto, dob, mapa):
    aceites, ambiguas = [], []
    for forma, nome, dono in vocabulario_de_cultura():
        for m in _rx(forma).finditer(dob):
            sp = (m.start(), m.end())
            if any(_sobrepoe(sp, (a["INICIO_D"], a["FIM_D"])) for a in aceites + ambiguas):
                continue
            h = {"VALOR": nome, "TRECHO": _literal(texto, mapa, *sp), "INICIO": mapa[sp[0]],
                 "FIM": mapa[sp[1] - 1] + 1, "VOCABULARIO": dono, "INICIO_D": sp[0], "FIM_D": sp[1]}
            if forma in AMBIGUAS_CULTURA:
                h["PORQUE"] = AMBIGUAS_CULTURA[forma]
                ambiguas.append(h)
            else:
                aceites.append(h)
    # a forma ambigua so conta se a MESMA cultura tiver outra forma sem ambiguidade no texto
    nomes = {a["VALOR"] for a in aceites}
    sustentadas = [a for a in ambiguas if a["VALOR"] in nomes]
    return aceites + sustentadas, [a for a in ambiguas if a["VALOR"] not in nomes]


def _achados_de_problema(texto, dob, mapa):
    BC = _bc()
    aceites = []
    for forma, nome, dono, e_regex in vocabulario_de_problema():
        rx = forma if e_regex else _rx(forma)
        for m in rx.finditer(dob):
            sp = (m.start(), m.end())
            if sp[0] == sp[1] or any(_sobrepoe(sp, (a["INICIO_D"], a["FIM_D"])) for a in aceites):
                continue
            aceites.append({"VALOR": nome if nome else BC.nome_do_problema(m.group(0)),
                            "TRECHO": _literal(texto, mapa, *sp), "INICIO": mapa[sp[0]],
                            "FIM": mapa[sp[1] - 1] + 1, "VOCABULARIO": dono,
                            "INICIO_D": sp[0], "FIM_D": sp[1]})
    return aceites


def _frases(texto):
    """[(ini, fim)] no ORIGINAL. Fim de frase = «.;!?» seguido de espaco e MAIUSCULA ou digito:
    «L. botrana», «B. cinerea» nao partem a frase."""
    cortes, ini = [], 0
    for m in re.finditer(r"[.;!?](?=\s+[A-Z0-9À-Ý(«\"])|\n\s*\n", texto):
        cortes.append((ini, m.end()))
        ini = m.end()
    cortes.append((ini, len(texto)))
    return cortes


def _achados_de_lugar(texto, dob, mapa):
    frases = _frases(texto)
    pistas = [(mapa[m.start()], m.group(0)) for m in _PISTA_DE_ESTUDO.finditer(dob)]
    todos, ocupados = [], []
    for forma, nome, precisao, dono in vocabulario_de_lugar():
        for m in _rx(forma).finditer(dob):
            sp = (m.start(), m.end())
            if any(_sobrepoe(sp, o) for o in ocupados):
                continue
            ocupados.append(sp)
            todos.append({"VALOR": nome, "PRECISAO": precisao, "FORMA": forma, "VOCABULARIO": dono,
                          "TRECHO": _literal(texto, mapa, *sp), "INICIO": mapa[sp[0]],
                          "FIM": mapa[sp[1] - 1] + 1, "INICIO_D": sp[0], "FIM_D": sp[1]})
    todos.sort(key=lambda h: h["INICIO_D"])
    ancorados, recusados = [], []
    for h in todos:
        antes = dob[max(0, h["INICIO_D"] - 80):h["INICIO_D"]]
        frase = next(f for f in frases if f[0] <= h["INICIO"] < max(f[1], f[0] + 1))
        if _INSTITUCIONAL.search(antes):
            recusados.append(dict(h, PORQUE="AFILIACAO: o nome vem logo depois de universidade/instituto "
                                            "(INT-LAW-102)"))
            continue
        if h["FORMA"] in AMBIGUOS_LUGAR and not _PROVINCIA_DE.search(antes):
            recusados.append(dict(h, PORQUE="AMBIGUO: %s; so conta depois de «provincia di / province of»"
                                            % AMBIGUOS_LUGAR[h["FORMA"]]))
            continue
        anterior = ancorados[-1] if ancorados else None
        coordenado = (anterior is not None and anterior["FRASE"] == frase
                      and _COORDENADO.match(dob[anterior["FIM_D"]:h["INICIO_D"]]))
        if not (_PREPOSICAO.search(antes) or coordenado):
            recusados.append(dict(h, PORQUE="sem preposicao de lugar logo antes: nomear nao e dizer onde o "
                                            "estudo foi feito"))
            continue
        pista = [p for p in pistas if frase[0] <= p[0] < frase[1]]
        if not pista:
            recusados.append(dict(h, PORQUE="a frase nao diz que um estudo/ensaio foi feito ali (sem verbo ou "
                                            "nome de experimento): PLACE_MENTION != FACT_LOCATION"))
            continue
        ancorados.append(dict(h, FRASE=frase, PISTA=pista[0][1],
                              TRECHO_DA_FRASE=re.sub(r"\s+", " ", texto[frase[0]:frase[1]]).strip()[:240]))
    # o pais so quando nada mais fino foi dito
    finos = [a for a in ancorados if a["PRECISAO"] != "PAIS"]
    return (finos or ancorados), recusados


def _limpo(h):
    return {k: v for k, v in h.items() if k not in ("INICIO_D", "FIM_D", "FRASE", "FORMA")}


def _unicos(hs):
    return list(dict.fromkeys(h["VALOR"] for h in hs))


def chaves_do_estudo(texto: str) -> dict:
    """As tres chaves que o TEXTO de um estudo sustenta, cada uma com o trecho literal (D112).

    `texto` e o que a Sala guarda: o titulo e o resumo que a fonte publicou. Nada vem da consulta que
    trouxe o trabalho, nem da afiliacao dos autores, nem da data de publicacao."""
    texto = str(texto or "")
    dob, mapa = _dobrar_com_mapa(texto)
    nada = {"VALOR": AUSENCIA, "VEIO_DE": AUSENCIA, "BASE": AUSENCIA}
    veio = "item.texto (titulo + resumo do estudo), %s" % EXTRATOR

    culturas, ambiguas = _achados_de_cultura(texto, dob, mapa)
    culturas.sort(key=lambda h: h["INICIO"])
    if culturas:
        cultura = {"VALOR": _unicos(culturas), "VEIO_DE": veio,
                   "BASE": " ; ".join("«%s»" % h["TRECHO"] for h in culturas)[:600]}
    else:
        cultura = dict(nada, PORQUE=("so formas ambiguas no texto: AMBIGUO = NAO SEI" if ambiguas
                                     else "o texto nao nomeia cultura de nenhum dos vocabularios"))
    cultura.update({"ENTITY_SOURCE": ENTITY_SOURCE if culturas else AUSENCIA,
                    "SPANS": [_limpo(h) for h in culturas], "AMBIGUAS": [_limpo(h) for h in ambiguas],
                    "NATUREZA": NATUREZA,
                    "FORMA": "o nome do vocabulario que casou primeiro; nao e EPPO"})

    problemas = sorted(_achados_de_problema(texto, dob, mapa), key=lambda h: h["INICIO"])
    if problemas:
        problema = {"VALOR": _unicos(problemas), "VEIO_DE": veio,
                    "BASE": " ; ".join("«%s»" % h["TRECHO"] for h in problemas)[:600]}
    else:
        problema = dict(nada, PORQUE="o texto nao nomeia praga/doenca de nenhum dos vocabularios")
    problema.update({"ENTITY_SOURCE": ENTITY_SOURCE if problemas else AUSENCIA,
                     "SPANS": [_limpo(h) for h in problemas],
                     "ESTADO": ESTADO_DO_PROBLEMA if problemas else AUSENCIA,
                     "NATUREZA": NATUREZA, "LEI": LEI_CAP_SCI,
                     "FORMA": "o nome do vocabulario que casou primeiro; nao e EPPO"})

    lugares, recusados = _achados_de_lugar(texto, dob, mapa)
    if lugares:
        regiao = {"VALOR": _unicos(lugares), "VEIO_DE": veio,
                  "BASE": " ; ".join("«%s»" % h["TRECHO_DA_FRASE"] for h in lugares)[:600],
                  "PRECISAO": list(dict.fromkeys(h["PRECISAO"] for h in lugares))}
    else:
        regiao = dict(nada, PORQUE="o texto nao diz onde o estudo foi feito (lugar ancorado a um experimento)")
    regiao.update({"ENTITY_SOURCE": ENTITY_SOURCE if lugares else AUSENCIA,
                   "SPANS": [_limpo(h) for h in lugares], "RECUSADOS": [_limpo(h) for h in recusados],
                   "KIND": KIND_DO_LUGAR, "NATUREZA": NATUREZA, "LEI": LEI_LUGAR + " · " + LEI_CAP_SCI})
    return {"CULTURA": cultura, "PROBLEMA": problema, "REGIAO_DO_FATO": regiao,
            "CAP_SCI": {"NATUREZA": NATUREZA, "E_INCIDENCIA_DE_CAMPO": "NAO", "LEI": LEI_CAP_SCI},
            "EXTRATOR": EXTRATOR}
