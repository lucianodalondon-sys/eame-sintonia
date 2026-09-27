#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAP-SCI — A CAPACIDADE CIENTIFICA DA INTELLIGENCE, na sua forma minima.

    MISSAO   CAP-SCI (Biblia §34 · CAP-SCI; mapa do dono §35)
    ESPECIE  ANALYTIC_JUDGMENT de FORCA e APLICABILIDADE da evidencia cientifica.
    BASE     a corrida G0/v4 (`motor/corrida_da_inteligencia.py`): so le o que
             a corrida admitiu, e so no uso que o livro dela deixa disponivel.

    python3 -m unittest tests.test_capacidade_cientifica -v

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    O QUE A CIENCIA SUSTENTA, COM QUE FORCA, APLICAVEL A QUE,
    E REPLICADO POR QUEM?

O mapa do dono (§35) diz o que isto NAO e: «nao e biblioteca de papers». A
pergunta de negocio e «que conhecimento cientifico novo pode alterar uma decisao
agronomica ou estrategica?». Por isso cada estudo sai com FORCA decomposta,
APLICABILIDADE (o que esta provado e o que falta), a ESPECIE que ele proprio
declara, e — so quando cultura + alvo + molecula estao provados — a ligacao
TEMATICA a um rotulo ADAMA ativo.

O QUE ELE NUNCA FAZ
-------------------
    NAO le identidade de fora do READY. A unica materia e o item READY (os
        campos de `CAMPOS_DO_READY`) e, dentro dele, o envelope `FATO` que a
        Collection preservou tal e qual. Campo a mais e recusado, nao ignorado.
    NAO le o TEXTO. Titulo e resumo existem para o humano; extrair molecula,
        local ou n do texto seria a Intelligence a cunhar o facto (COL-LAW-202).
    NAO troca afiliacao por local do estudo (INT-LAW-102). A instituicao entra
        so na INDEPENDENCIA, nunca na geografia.
    NAO troca publicacao por periodo do estudo (INT-LAW-100).
    NAO conta tres papers do mesmo ensaio como tres evidencias (MUST_NOT_DO).
    NAO infere independencia: o numero de grupos e um TETO, e diz-se.
    NAO transforma estudo pequeno, nem estudo negativo, em «o produto nao
        funciona». Essa leitura nao existe no vocabulario desta capacidade.
    NAO produz FINDING nem OPPORTUNITY. NAO pontua com um numero so.
"""
from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "motor") not in sys.path:
    sys.path.insert(0, str(RAIZ / "motor"))

# A corrida e a dona do intake, do portao e da leitura de tempo — nada disso e
# copiado aqui. O vocabulario do READY chega PELA corrida (que o le da espinha,
# que o le do dono da Sala): importar a espinha daqui seria mais um modulo de
# runtime a importar `provas/` por nome nu (test_a_porta_cli_liga_o_banco).
import corrida_da_inteligencia as CORRIDA                          # noqa: E402

CAMPOS_DO_READY = CORRIDA.CAMPOS_DO_READY
NAO_SEI = CORRIDA.NAO_SEI

CONTRATO = "CAP-SCI/v1"
CAPACIDADE = "CAP-SCI"
PERGUNTA = ("que conhecimento cientifico novo pode alterar uma decisao "
            "agronomica ou estrategica — com que forca, aplicavel a que, "
            "replicado por quem?")
PRONTO = "PRONTO_PARA_INTELIGENCIA"
#: O uso que o livro da corrida G0/v4 tem de deixar disponivel ao item.
USO_EXIGIDO = "LEITURA_ATEMPORAL_DE_CAPACIDADE"
REFERENCIA_ADAMA = RAIZ / "referencia" / "adama"


class LeiViolada(Exception):
    """A capacidade recusou-se, e diz porque. Nao e defeito: e o portao."""


# ═════════════════════════════════════════════════════════════════════════
# 1 · O QUE SE LE DO ENVELOPE `FATO` — nomes que o produtor pode ter usado
# ═════════════════════════════════════════════════════════════════════════
#: A Collection preserva o FATO com os nomes do produtor (`envelope_do_fato`,
#: COL-LAW-202: sem esquema fechado). Esta tabela diz, para cada chave da
#: CAP-SCI (Biblia JOIN_KEYS + PRESERVA), que nomes do produtor valem para ela.
#: Dois nomes da mesma chave com valores DIFERENTES e conflito, e conflito fica
#: conflito (INT-LAW-084): a chave sai NAO SEI com o motivo.
CHAVES_DO_FATO = {
    "DOI": ("doi",),
    "TRIAL_ID": ("trial_id",),
    "DATASET_ID": ("dataset_id", "dataset_ids"),
    "TITULO": ("title", "titulo", "titolo"),
    "CULTURA": ("crop", "cultura", "coltura"),
    "PROBLEMA": ("problem", "problema", "issue", "target", "alvo"),
    "MOLECULA": ("molecule", "molecules", "molecula", "moleculas",
                 "active_ingredient", "active_ingredients"),
    "METODO": ("method", "metodo", "metodo_do_estudo"),
    "N": ("n", "sample_size", "n_unidades"),
    "AUTORES": ("researcher_ids", "orcid", "orcids", "authors", "autores"),
    "INSTITUICOES": ("institution_ids", "ror", "rors", "institutions",
                     "instituicoes"),
    "ESPECIE": ("evidence_species", "especie", "especie_declarada"),
    "RESULTADO": ("result", "resultado", "direction", "direcao"),
}

#: ⚠️ CHAVES QUE PARECEM LUGAR E NAO SAO. Estao aqui para serem RECUSADAS como
#: local do estudo, com nome — e um teste prova que nenhuma delas entra.
#: INT-LAW-102: afiliacao != local do estudo.
NAO_SAO_LOCAL_DO_ESTUDO = ("affiliation", "afiliacao", "institution",
                           "institution_country", "country_of_affiliation")

# ═════════════════════════════════════════════════════════════════════════
# 2 · ESPECIE — a que o ESTUDO declara, nunca a que o texto sugere
# ═════════════════════════════════════════════════════════════════════════
#: Tres especies, e nao uma. Uma regra de modelo (limiar de infecao, «regra dos
#: 3-10» da peronospora) e uma medicao de resistencia NAO sao resultado de
#: eficacia: contadas juntas, uma regra de modelo passava por ensaio, e uma
#: resistencia local passava por «a molecula falha».
ESPECIE_RESULTADO = "SCIENTIFIC_RESULT"
ESPECIE_MODELO = "MODEL_RULE"
ESPECIE_RESISTENCIA = "RESISTANCE"
ESPECIES = (ESPECIE_RESULTADO, ESPECIE_MODELO, ESPECIE_RESISTENCIA)
_ESPECIE_ALIAS = {
    "SCIENTIFIC_RESULT": ESPECIE_RESULTADO, "RESULTADO_CIENTIFICO": ESPECIE_RESULTADO,
    "MODEL_RULE": ESPECIE_MODELO, "REGRA_DE_MODELO": ESPECIE_MODELO,
    "RESISTANCE": ESPECIE_RESISTENCIA, "RESISTENCIA": ESPECIE_RESISTENCIA,
}

# ═════════════════════════════════════════════════════════════════════════
# 3 · FORCA — decomposta (INT-LAW-093), e nunca um numero so
# ═════════════════════════════════════════════════════════════════════════
#: O desenho do estudo, do vocabulario fechado. Metodo fora da lista e NAO SEI:
#: adivinhar «parece um ensaio de campo» e o erro que esta tabela existe para
#: impedir. O numero e o degrau do DESENHO, e nao da verdade do resultado.
METODOS = {
    "ENSAIO_DE_CAMPO_RANDOMIZADO": 3,
    "ENSAIO_DE_CAMPO": 2,
    "ENSAIO_EM_ESTUFA": 2,
    "LABORATORIO": 1,
    "OBSERVACIONAL": 1,
    "MONITORAMENTO": 1,
    "MODELO": 1,
}
_METODO_ALIAS = {
    "RANDOMIZED_FIELD_TRIAL": "ENSAIO_DE_CAMPO_RANDOMIZADO",
    "FIELD_TRIAL": "ENSAIO_DE_CAMPO", "GREENHOUSE": "ENSAIO_EM_ESTUFA",
    "IN_VITRO": "LABORATORIO", "LAB": "LABORATORIO", "LABORATORY": "LABORATORIO",
    "OBSERVATIONAL": "OBSERVACIONAL", "MONITORING": "MONITORAMENTO",
    "MODEL": "MODELO", "MODELLING": "MODELO",
}
#: ⚠️ REVISAO NAO E EVIDENCIA PRIMARIA. Uma revisao ou meta-analise junta
#: estudos que podem estar no mesmo corte: contar a revisao AO LADO deles e
#: contar os mesmos ensaios duas vezes (INT-LAW-072). Ela sai com FORCA
#: NAO_APLICAVEL e fora da contagem de replicacao.
METODOS_SECUNDARIOS = ("REVISAO", "META_ANALISE")
_METODO_ALIAS.update({"REVIEW": "REVISAO", "SYSTEMATIC_REVIEW": "REVISAO",
                      "META_ANALYSIS": "META_ANALISE", "METANALISI": "META_ANALISE"})

#: ⚠️ ESTUDO PEQUENO. Abaixo disto (unidades experimentais declaradas pelo
#: estudo — repeticoes, parcelas, locais) o estudo e INDICATIVO, qualquer que
#: seja o desenho. Nao e um limiar estatistico universal: e o piso desta
#: capacidade, declarado, e muda-se aqui e so aqui.
N_PEQUENO = 4

FORTE, MODERADA, FRACA, INDICATIVA = "FORTE", "MODERADA", "FRACA", "INDICATIVA"
NAO_APLICAVEL = "NAO_APLICAVEL"
_NIVEL = {3: FORTE, 2: MODERADA, 1: FRACA}

#: Os resultados que o estudo pode declarar. Direcao, e nao conclusao.
RESULTADOS = {
    "EFICAZ": "+", "EFFECTIVE": "+", "POSITIVE": "+",
    "SEM_EFEITO_DEMONSTRADO": "0", "NO_EFFECT": "0", "NO_DIFFERENCE": "0",
    "INEFICAZ": "-", "INEFFECTIVE": "-", "NEGATIVE": "-",
    "RESISTENCIA_DETECTADA": "R", "RESISTANCE_DETECTED": "R",
    "SENSIBILIDADE_MANTIDA": "S", "SENSITIVE": "S",
}

# ═════════════════════════════════════════════════════════════════════════
# 4 · A LEITURA — vocabulario fechado, e a que falta falta de proposito
# ═════════════════════════════════════════════════════════════════════════
#: O que um estudo PODE dizer, conforme a direcao do resultado e a forca. Nao
#: existe entrada que diga «o produto nao funciona» nem «a molecula falha»:
#: um estudo e sobre a MOLECULA nas condicoes DELE, nao sobre o produto, e
#: ausencia de efeito medido nao e prova de ineficacia.
LEITURAS = (
    "SUSTENTA_EFEITO_NESTAS_CONDICOES",
    "NAO_DEMONSTROU_EFEITO_NESTAS_CONDICOES",
    "INDICIO_A_CONFIRMAR",
    "RESISTENCIA_OBSERVADA_NESTE_LOCAL_E_PERIODO",
    "RESISTENCIA_OBSERVADA_LOCAL_OU_PERIODO_NAO_PROVADO",
    "SENSIBILIDADE_MANTIDA_NESTE_ESTUDO",
    "REGRA_DE_MODELO_DECLARADA",
    "SEM_LEITURA_RESULTADO_NAO_DECLARADO",
    "SEM_LEITURA_TEMA_NAO_PROVADO",
    "SEM_LEITURA_REVISAO_NAO_E_EVIDENCIA_PRIMARIA",
)
#: E o que NUNCA sai daqui. Um teste varre o livro inteiro atras delas.
LEITURAS_PROIBIDAS = ("O_PRODUTO_NAO_FUNCIONA", "PRODUTO_NAO_FUNCIONA",
                      "A_MOLECULA_NAO_FUNCIONA", "MOLECULA_INEFICAZ",
                      "RESISTENCIA_GENERALIZADA")


# ═════════════════════════════════════════════════════════════════════════
# LER O ITEM — so o READY, e dentro dele so o FATO
# ═════════════════════════════════════════════════════════════════════════
def _dobra(s) -> str:
    """Maiusculas e sem acento. Nao e semelhanca: e a MESMA grafia (INT-LAW-081)."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.upper().split())


def conferir_ready(item) -> None:
    """Recusa o item que nao e READY — ou que traz identidade de fora dele.

    ⚠️ UM CAMPO A MAIS NAO E IGNORADO. Se alguem pendurar `DOI` ou
    `ADAMA_PRODUCT_ID` no item, fora do contrato, e a CAP-SCI o ignorasse, o
    proximo a mexer aqui ia le-lo — e a identidade passava a vir de quem chamou,
    nao da Collection. Recusar e a unica forma de a fronteira ficar verificavel.
    """
    if not isinstance(item, dict):
        raise LeiViolada("um item que nao e um item nao se le")
    sobra = sorted(set(item) - set(CAMPOS_DO_READY))
    if sobra:
        raise LeiViolada("IDENTIDADE_DE_FORA_DO_READY: o item %r traz campo que o "
                         "contrato READY nao tem: %s"
                         % (item.get("ITEM_ID", NAO_SEI), ", ".join(sobra)))
    if item.get("ESTADO") != PRONTO:
        raise LeiViolada("o item %r nao esta READY (ESTADO=%r)"
                         % (item.get("ITEM_ID", NAO_SEI), item.get("ESTADO")))


def _fato(item: dict) -> dict:
    f = item.get("FATO")
    return f if isinstance(f, dict) else {}


def ler_chave(fato: dict, chave: str) -> tuple:
    """`(valor, motivo)`. O valor como o produtor o escreveu, ou NAO SEI.

    O motivo diz PORQUE e NAO SEI: nenhum nome da chave presente, o valor e
    ignorancia escrita, ou dois nomes da mesma chave discordam (conflito).
    """
    nomes = {str(k).lower(): k for k in fato}
    achados = []
    for nome in CHAVES_DO_FATO[chave]:
        if nome in nomes:
            v = fato[nomes[nome]]
            if not _ignorancia(v):
                achados.append((nome, v))
    if not achados:
        return NAO_SEI, "AUSENTE_NO_FATO"
    valores = {json.dumps(_normal(v), sort_keys=True, ensure_ascii=False)
               for _, v in achados}
    if len(valores) > 1:
        return NAO_SEI, "CONFLITO_NO_FATO: " + ", ".join(n for n, _ in achados)
    return achados[0][1], "FATO." + achados[0][0]


def _ignorancia(v) -> bool:
    if isinstance(v, (list, tuple)):
        return not [x for x in v if not CORRIDA.e_ignorancia(x)]
    return CORRIDA.e_ignorancia(v)


def _normal(v):
    if isinstance(v, (list, tuple)):
        return sorted({_dobra(x) for x in v if not CORRIDA.e_ignorancia(x)})
    return _dobra(v) if isinstance(v, str) else v


def _lista(v) -> list:
    if v == NAO_SEI:
        return []
    if isinstance(v, (list, tuple)):
        return sorted({_dobra(x) for x in v if not CORRIDA.e_ignorancia(x)})
    return [_dobra(v)]


def local_do_estudo(item: dict) -> dict:
    """O LOCAL DO ESTUDO — so `FACT_LOCATION` com base, como a Collection deu.

    Nunca `SOURCE_LOCATION`, nunca a afiliacao, nunca o pais da revista.
    """
    v, base = item.get("FACT_LOCATION"), item.get("FACT_LOCATION_BASIS")
    if CORRIDA.e_ignorancia(v):
        return {"VALOR": NAO_SEI, "ESTADO": "NAO_SEI", "PORQUE": "FACT_LOCATION ausente"}
    if CORRIDA.base_ignorante(base):
        return {"VALOR": NAO_SEI, "ESTADO": "NAO_SEI",
                "PORQUE": "FACT_LOCATION sem base: valor sem razao nao ancora",
                "VALOR_SEM_BASE": v}
    return {"VALOR": v, "ESTADO": "PROVADO", "BASE": base}


def periodo_do_estudo(item: dict) -> dict:
    """O PERIODO DO ESTUDO — so `FACT_TIME` com base e com ano.

    Nunca `PUBLISHED_AT`: um paper de 2024 pode relatar a campanha de 2019.
    """
    v, base = item.get("FACT_TIME"), item.get("FACT_TIME_BASIS")
    if CORRIDA.e_ignorancia(v):
        return {"VALOR": NAO_SEI, "ESTADO": "NAO_SEI", "PORQUE": "FACT_TIME ausente",
                "PUBLICATION_TIME_NAO_E_PERIODO": True}
    if CORRIDA.base_ignorante(base):
        return {"VALOR": NAO_SEI, "ESTADO": "NAO_SEI",
                "PORQUE": "FACT_TIME sem base", "VALOR_SEM_BASE": v}
    tempo = CORRIDA.intervalo_do_tempo(v)
    if tempo["ESTADO"] != "INTERVALO":
        return {"VALOR": NAO_SEI, "ESTADO": "NAO_SEI",
                "PORQUE": "FACT_TIME " + tempo["ESTADO"], "VALOR_SEM_ANO": v}
    return {"VALOR": v, "ESTADO": "PROVADO", "BASE": base, "INTERVALO": tempo}


# ═════════════════════════════════════════════════════════════════════════
# O JULGAMENTO DE UM ESTUDO
# ═════════════════════════════════════════════════════════════════════════
def _especie(fato: dict) -> tuple:
    v, porque = ler_chave(fato, "ESPECIE")
    if v == NAO_SEI:
        return NAO_SEI, "o estudo nao declara especie (" + porque + ")"
    e = _ESPECIE_ALIAS.get(_dobra(v).replace(" ", "_"))
    if e is None:
        return NAO_SEI, "especie fora do vocabulario: %r" % v
    return e, porque


def _metodo(fato: dict) -> tuple:
    v, porque = ler_chave(fato, "METODO")
    if v == NAO_SEI:
        return NAO_SEI, porque
    m = _dobra(v).replace(" ", "_").replace("-", "_")
    m = _METODO_ALIAS.get(m, m)
    if m in METODOS or m in METODOS_SECUNDARIOS:
        return m, porque
    return NAO_SEI, "metodo fora do vocabulario: %r" % v


def _n(fato: dict) -> tuple:
    v, porque = ler_chave(fato, "N")
    if v == NAO_SEI:
        return NAO_SEI, porque
    if isinstance(v, bool) or not isinstance(v, int) or v <= 0:
        return NAO_SEI, "n nao e inteiro positivo: %r" % (v,)
    return v, porque


def forca(metodo, n) -> dict:
    """A FORCA, decomposta: desenho, tamanho, e o nivel que os dois deixam.

    Sem metodo nao ha forca — NAO SEI, e nao «fraca»: fraca e um juizo, e nao
    ha base para ele. Estudo pequeno e INDICATIVO qualquer que seja o desenho.
    Sem n, o nivel nao passa de FRACA: um ensaio de campo com n desconhecido
    pode ser um vaso so.
    """
    if metodo == NAO_SEI:
        return {"NIVEL": NAO_SEI, "DESENHO": NAO_SEI, "N": n,
                "PORQUE": ["METODO nao provado: sem desenho nao ha forca"]}
    if metodo in METODOS_SECUNDARIOS:
        return {"NIVEL": NAO_APLICAVEL, "DESENHO": metodo, "N": n,
                "PORQUE": ["revisao agrega estudos que podem estar no mesmo corte "
                           "(INT-LAW-072): nao e evidencia primaria"]}
    degrau = METODOS[metodo]
    porque = ["DESENHO %s = degrau %d" % (metodo, degrau)]
    if n == NAO_SEI:
        nivel = _NIVEL[min(degrau, 1)]
        porque.append("N nao declarado: o nivel nao passa de FRACA")
    elif n < N_PEQUENO:
        nivel = INDICATIVA
        porque.append("ESTUDO_PEQUENO: n=%d < %d" % (n, N_PEQUENO))
    else:
        nivel = _NIVEL[degrau]
        porque.append("n=%d" % n)
    return {"NIVEL": nivel, "DESENHO": metodo, "N": n,
            "ESTUDO_PEQUENO": (n != NAO_SEI and n < N_PEQUENO), "PORQUE": porque}


def leitura(especie, resultado_dir, f: dict, local: dict, periodo: dict,
            tema_provado: bool = True) -> str:
    """O que o estudo PODE dizer — do vocabulario fechado `LEITURAS`.

    Sem cultura e problema provados nao ha leitura de efeito: um efeito sem
    «em que e contra que» nao se aplica a decisao nenhuma.
    """
    if not tema_provado:
        return "SEM_LEITURA_TEMA_NAO_PROVADO"
    if f["NIVEL"] == NAO_APLICAVEL:
        return "SEM_LEITURA_REVISAO_NAO_E_EVIDENCIA_PRIMARIA"
    if especie == ESPECIE_MODELO:
        return "REGRA_DE_MODELO_DECLARADA"
    if resultado_dir == NAO_SEI:
        return "SEM_LEITURA_RESULTADO_NAO_DECLARADO"
    if resultado_dir == "R":
        if local["ESTADO"] == "PROVADO" and periodo["ESTADO"] == "PROVADO":
            return "RESISTENCIA_OBSERVADA_NESTE_LOCAL_E_PERIODO"
        return "RESISTENCIA_OBSERVADA_LOCAL_OU_PERIODO_NAO_PROVADO"
    if resultado_dir == "S":
        return "SENSIBILIDADE_MANTIDA_NESTE_ESTUDO"
    if f["NIVEL"] in (NAO_SEI, INDICATIVA):
        return "INDICIO_A_CONFIRMAR"
    if resultado_dir == "+":
        return "SUSTENTA_EFEITO_NESTAS_CONDICOES"
    # «0» e «-»: um estudo, por mais forte, nao prova ineficacia. So diz que
    # NESTAS condicoes o efeito nao se demonstrou.
    return "NAO_DEMONSTROU_EFEITO_NESTAS_CONDICOES"


def julgar_estudo(item: dict) -> dict:
    """O ANALYTIC_JUDGMENT de um estudo: identidade, especie, forca, aplicabilidade."""
    conferir_ready(item)
    fato = _fato(item)
    doi, doi_pq = ler_chave(fato, "DOI")
    trial, _ = ler_chave(fato, "TRIAL_ID")
    dataset, _ = ler_chave(fato, "DATASET_ID")
    cultura, cult_pq = ler_chave(fato, "CULTURA")
    problema, prob_pq = ler_chave(fato, "PROBLEMA")
    molecula, mol_pq = ler_chave(fato, "MOLECULA")
    resultado, res_pq = ler_chave(fato, "RESULTADO")
    autores, _ = ler_chave(fato, "AUTORES")
    insts, _ = ler_chave(fato, "INSTITUICOES")
    especie, esp_pq = _especie(fato)
    metodo, met_pq = _metodo(fato)
    n, n_pq = _n(fato)
    local, periodo = local_do_estudo(item), periodo_do_estudo(item)
    f = forca(metodo, n)
    res_dir = NAO_SEI if resultado == NAO_SEI else RESULTADOS.get(
        _dobra(resultado).replace(" ", "_"), NAO_SEI)

    provado = {"CULTURA": cultura != NAO_SEI, "PROBLEMA": problema != NAO_SEI,
               "MOLECULA": molecula != NAO_SEI,
               "LOCAL": local["ESTADO"] == "PROVADO",
               "PERIODO": periodo["ESTADO"] == "PROVADO"}
    falta = [k for k, ok in provado.items() if not ok]
    if not (provado["CULTURA"] and provado["PROBLEMA"]):
        aplic = "TEMA_NAO_PROVADO"
    elif falta:
        aplic = "PARCIAL"
    else:
        aplic = "COMPLETA"

    return {
        "ITEM_ID": item.get("ITEM_ID", NAO_SEI),
        "SOURCE_ID": item.get("SOURCE_ID", NAO_SEI),
        "RAW_OBSERVATION_ID": item.get("RAW_OBSERVATION_ID", NAO_SEI),
        "DOI": doi,
        "TRIAL_ID": trial, "DATASET_ID": dataset,
        "LINEAGE": ("COMPLETE" if doi != NAO_SEI or trial != NAO_SEI else
                    "PARTIAL — sem DOI nem TRIAL_ID a atravessar a fronteira "
                    "(Biblia CAP-SCI LINEAGE)"),
        "ESPECIE": especie, "ESPECIE_PORQUE": esp_pq,
        "CULTURA": cultura, "PROBLEMA": problema,
        "MOLECULA": _lista(molecula) or NAO_SEI,
        "METODO": metodo, "N": n,
        "LOCAL_DO_ESTUDO": local, "PERIODO_DO_ESTUDO": periodo,
        "AFILIACAO_NAO_E_LOCAL": True,
        "RESULTADO": resultado, "RESULTADO_DIRECAO": res_dir,
        "FORCA": f,
        "APLICABILIDADE": {"ESTADO": aplic, "PROVADO": provado, "FALTA": falta},
        "LEITURA": leitura(especie, res_dir, f, local, periodo,
                           provado["CULTURA"] and provado["PROBLEMA"]),
        "NAO_E": ["INCIDENCIA_DE_CAMPO", "RESULTADO_DO_PRODUTO", "FINDING"],
        "CHAVES_DE_INDEPENDENCIA": {
            "TRIAL": [trial] if trial != NAO_SEI else [],
            "DATASET": _lista(dataset),
            "AUTOR": _lista(autores),
            "INSTITUICAO": _lista(insts),
        },
        "PORQUE_NAO_SEI": {k: v for k, v in (("DOI", doi_pq), ("CULTURA", cult_pq),
                                             ("PROBLEMA", prob_pq), ("MOLECULA", mol_pq),
                                             ("RESULTADO", res_pq), ("METODO", met_pq),
                                             ("N", n_pq))
                           if not v.startswith("FATO.")},
    }


# ═════════════════════════════════════════════════════════════════════════
# INDEPENDENCIA — grupos por equipe, instituicao, dataset e ensaio
# ═════════════════════════════════════════════════════════════════════════
def _tema(e: dict) -> str:
    return "%s x %s" % (_dobra(e["CULTURA"]), _dobra(e["PROBLEMA"]))


def independencia(estudos: list) -> dict:
    """Por tema (cultura x problema): obras, grupos, e o que falta para saber.

    Dois estudos caem no MESMO grupo se partilham um ensaio (TRIAL), um dataset
    (INT-LAW-073), um autor ou uma instituicao. O mesmo DOI e a MESMA obra
    (INT-LAW-072). O numero de grupos e um TETO: partilhar nada do que se sabe
    nao prova que sao independentes — so que nada provado os liga.

    ⚠️ Estudo sem nenhuma chave de independencia nao conta como grupo novo
    PROVADO: fica em `SEM_CHAVE`, e o piso de grupos fica NAO SEI. Contar cada
    um como independente seria inferir independencia (INT-LAW-280).
    """
    temas: dict = {}
    for e in estudos:
        if e["CULTURA"] == NAO_SEI or e["PROBLEMA"] == NAO_SEI:
            continue
        temas.setdefault(_tema(e), []).append(e)
    out = {}
    for tema, es in sorted(temas.items()):
        pai = list(range(len(es)))

        def raiz(i):
            while pai[i] != i:
                pai[i] = pai[pai[i]]
                i = pai[i]
            return i
        dono: dict = {}
        sem_chave = []
        for i, e in enumerate(es):
            chaves = [("DOI", e["DOI"])] if e["DOI"] != NAO_SEI else []
            for tipo, vs in e["CHAVES_DE_INDEPENDENCIA"].items():
                chaves += [(tipo, v) for v in vs]
            if not [c for c in chaves if c[0] != "DOI"]:
                sem_chave.append(e["ITEM_ID"])
            for c in chaves:
                if c in dono:
                    pai[raiz(i)] = raiz(dono[c])
                else:
                    dono[c] = i
        grupos: dict = {}
        for i, e in enumerate(es):
            grupos.setdefault(raiz(i), []).append(e["ITEM_ID"])
        obras = {e["DOI"] if e["DOI"] != NAO_SEI else "ITEM:" + str(e["ITEM_ID"])
                 for e in es}
        out[tema] = {
            "ESTUDOS": len(es),
            "OBRAS": len(obras),
            "GRUPOS_TETO": len(grupos),
            "GRUPOS": sorted(sorted(map(str, g)) for g in grupos.values()),
            "SEM_CHAVE_DE_INDEPENDENCIA": sorted(map(str, sem_chave)),
            "INDEPENDENCIA": ("TETO — nao e prova de independencia" if not sem_chave
                              else "TETO; %d estudo(s) sem chave: o piso e NAO SEI"
                              % len(sem_chave)),
        }
    return out


def replicacao(estudos: list, grupos: dict) -> list:
    """Por afirmacao (cultura x problema x molecula x direcao), em quantos grupos.

    So resultados primarios de eficacia e de resistencia contam; regra de modelo
    e revisao ficam fora. Direcoes opostas no mesmo tema+molecula sao
    CONTRADICAO, declarada — nunca «a maioria ganha».
    """
    grupo_de = {}
    for tema, g in grupos.items():
        for n, membros in enumerate(g["GRUPOS"]):
            for m in membros:
                grupo_de[(tema, m)] = n
    sem_chave = {m for g in grupos.values() for m in g["SEM_CHAVE_DE_INDEPENDENCIA"]}
    afirm: dict = {}
    for e in estudos:
        if (e["ESPECIE"] == ESPECIE_MODELO or e["FORCA"]["NIVEL"] == NAO_APLICAVEL
                or e["RESULTADO_DIRECAO"] == NAO_SEI or e["MOLECULA"] == NAO_SEI
                or e["CULTURA"] == NAO_SEI or e["PROBLEMA"] == NAO_SEI):
            continue
        tema = _tema(e)
        for mol in e["MOLECULA"]:
            chave = (tema, mol)
            afirm.setdefault(chave, {}).setdefault(e["RESULTADO_DIRECAO"], []).append(e)
    out = []
    for (tema, mol), por_dir in sorted(afirm.items()):
        for d, es in sorted(por_dir.items()):
            gs = {grupo_de[(tema, str(e["ITEM_ID"]))] for e in es
                  if str(e["ITEM_ID"]) not in sem_chave}
            n_sem = sum(1 for e in es if str(e["ITEM_ID"]) in sem_chave)
            estado = ("REPLICADO_EM_GRUPOS_DISTINTOS_TETO" if len(gs) >= 2 else
                      "NAO_REPLICADO" if len(gs) == 1 and not n_sem else
                      "NAO_SEI")
            opostos = sorted(x for x in por_dir if x != d and {x, d} in
                             ({"+", "-"}, {"+", "0"}, {"R", "S"}))
            out.append({"TEMA": tema, "MOLECULA": mol, "DIRECAO": d,
                        "ESTUDOS": sorted(str(e["ITEM_ID"]) for e in es),
                        "GRUPOS_COM_CHAVE": len(gs), "ESTUDOS_SEM_CHAVE": n_sem,
                        "REPLICACAO": estado,
                        "CONTRADICAO_COM": opostos,
                        "REPLICACAO_AUSENTE_DECLARADA": estado != "REPLICADO_EM_GRUPOS_DISTINTOS_TETO"})
    return out


# ═════════════════════════════════════════════════════════════════════════
# A LIGACAO ESTUDO -> PRODUTO ADAMA — so com cultura + alvo + molecula provados
# ═════════════════════════════════════════════════════════════════════════
#: ⚠️ ISTO NAO E SEMELHANCA. Cada linha e a MESMA substancia escrita de outra
#: maneira (abreviatura ISO, grafia portuguesa/italiana), declarada a mao e
#: com o nome da referencia a direita. METALAXYL e METALAXYL-M sao DUAS
#: moleculas e nao se juntam (um teste prova-o).
ALIAS_DE_MOLECULA = {
    "FOSETYL-AL": "FOSETYL-ALUMINIUM", "FOSETIL-AL": "FOSETYL-ALUMINIUM",
    "FOSETIL-ALLUMINIO": "FOSETYL-ALUMINIUM", "FOSETIL-ALUMINIO": "FOSETYL-ALUMINIUM",
    "METALAXIL-M": "METALAXYL-M", "METALAXIL": "METALAXYL",
    "CIMOXANIL": "CYMOXANIL", "CIMOXANILE": "CYMOXANIL",
    "FOLPETE": "FOLPET",
}


def _mol_ref(m: str) -> str:
    m = _dobra(m)
    return ALIAS_DE_MOLECULA.get(m, m)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def carregar_referencia(pasta: Path = REFERENCIA_ADAMA) -> dict:
    """A referencia ADAMA (ENTRADA B, so leitura). Quatro livros, com a impressao.

    Nao e identidade do estudo: e o outro lado do cruzamento. Se faltar um livro
    a referencia sai NAO SEI inteira — ligar com meia referencia daria «a ADAMA
    nao tem» onde a verdade e «nao li».
    """
    livros = ("ACTIVE-INGREDIENTS", "PRODUCT-ACTIVE-INGREDIENTS",
              "AUTHORIZED-USES", "REGISTRATIONS")
    try:
        dados = {n: json.loads((pasta / (n + ".json")).read_text(encoding="utf-8"))["RECORDS"]
                 for n in livros}
        impressao = {n: _sha(pasta / (n + ".json")) for n in livros}
    except (OSError, ValueError, KeyError) as erro:
        return {"ESTADO": NAO_SEI, "PORQUE": "referencia ilegivel: %r" % erro}
    return {"ESTADO": "LIDA", "PASTA": str(pasta.relative_to(RAIZ)) if pasta.is_relative_to(RAIZ) else str(pasta),
            "SHA256": impressao, **dados}


def ligar_ao_produto(e: dict, ref: dict) -> dict:
    """O cruzamento CAP-LABEL: molecula x cultura x alvo contra rotulo ADAMA ATIVO.

    Estados (INT-LAW-091: chave ausente bloqueia, nunca closest-match):
        NOT_POSSIBLE        o estudo nao prova cultura, alvo ou molecula
        UNKNOWN_REFERENCIA  a referencia nao foi lida, ou conhece a molecula
                            mas nao a liga a produto (referencia incompleta —
                            NUNCA «a ADAMA nao tem»)
        UNKNOWN_MOLECULA    a molecula nao esta entre os ativos da referencia
        RELACAO_SEM_ROTULO  a ADAMA tem a molecula, mas nenhum rotulo ATIVO
                            dela autoriza esta cultura x alvo
        PARTIAL             casa rotulo ativo; falta local e/ou periodo
        CANDIDATE           casa rotulo ativo, e local e periodo provados
    """
    base = {"ITEM_ID": e["ITEM_ID"], "DOI": e["DOI"], "CULTURA": e["CULTURA"],
            "PROBLEMA": e["PROBLEMA"], "MOLECULA": e["MOLECULA"]}
    falta = [k for k in ("CULTURA", "PROBLEMA", "MOLECULA") if e[k] == NAO_SEI]
    if falta:
        return dict(base, ESTADO="NOT_POSSIBLE", FALTA=falta, PRODUTOS=[])
    if ref.get("ESTADO") != "LIDA":
        return dict(base, ESTADO="UNKNOWN_REFERENCIA",
                    PORQUE=ref.get("PORQUE", NAO_SEI), PRODUTOS=[])
    cult, alvo = _dobra(e["CULTURA"]), _dobra(e["PROBLEMA"])
    ativos = {_dobra(a["NAME"]) for a in ref["ACTIVE-INGREDIENTS"]}
    ativos_reg = {r["REGISTRATION_NUMBER"] for r in ref["REGISTRATIONS"]
                  if r.get("ADMIN_ACTIVE") is True}
    por_mol = []
    for m in e["MOLECULA"]:
        mref = _mol_ref(m)
        regs = {p["REGISTRATION_NUMBER"] for p in ref["PRODUCT-ACTIVE-INGREDIENTS"]
                if _dobra(p["ACTIVE_INGREDIENT"]) == mref}
        if not regs:
            por_mol.append({"MOLECULA": m, "MOLECULA_NA_REFERENCIA": mref,
                            "ESTADO": ("UNKNOWN_REFERENCIA" if mref in ativos
                                       else "UNKNOWN_MOLECULA"),
                            "PORQUE": ("a referencia conhece o ativo mas nao o liga a "
                                       "produto: referencia incompleta, dono referencia/"
                                       if mref in ativos else
                                       "a molecula nao esta entre os ativos da referencia"),
                            "PRODUTOS": []})
            continue
        usos = [u for u in ref["AUTHORIZED-USES"]
                if u["REGISTRATION_NUMBER"] in regs and u["REGISTRATION_NUMBER"] in ativos_reg
                and _dobra(u["CROP_ON_LABEL"]) == cult and _dobra(u["TARGET_ON_LABEL"]) == alvo]
        produtos = sorted({(u["ADAMA_PRODUCT_ID"], u["OBSERVED_PRODUCT_NAME"],
                            u["REGISTRATION_NUMBER"]) for u in usos})
        if not produtos:
            por_mol.append({"MOLECULA": m, "MOLECULA_NA_REFERENCIA": mref,
                            "ESTADO": "RELACAO_SEM_ROTULO", "PRODUTOS": []})
            continue
        completo = (e["LOCAL_DO_ESTUDO"]["ESTADO"] == "PROVADO"
                    and e["PERIODO_DO_ESTUDO"]["ESTADO"] == "PROVADO")
        por_mol.append({
            "MOLECULA": m, "MOLECULA_NA_REFERENCIA": mref,
            "ESTADO": "CANDIDATE" if completo else "PARTIAL",
            "FALTA": [k for k in ("LOCAL", "PERIODO")
                      if not e["APLICABILIDADE"]["PROVADO"][k]],
            "PRODUTOS": [{"ADAMA_PRODUCT_ID": p, "NOME_NO_ROTULO": nome,
                          "REGISTRATION_NUMBER": r} for p, nome, r in produtos],
            "USE_IDS": sorted(u["USE_ID"] for u in usos),
        })
    ordem = ("CANDIDATE", "PARTIAL", "RELACAO_SEM_ROTULO", "UNKNOWN_REFERENCIA",
             "UNKNOWN_MOLECULA")
    estado = min((x["ESTADO"] for x in por_mol), key=ordem.index)
    return dict(base, ESTADO=estado, POR_MOLECULA=por_mol,
                NAO_PROVA=("a ligacao e TEMATICA: molecula, cultura e alvo casam um "
                           "rotulo ativo. NAO diz que o estudo testou o produto, a "
                           "formulacao ou a dose, e o resultado do estudo nao e o "
                           "resultado do produto."))


# ═════════════════════════════════════════════════════════════════════════
# A CAPACIDADE — sobre o livro da corrida
# ═════════════════════════════════════════════════════════════════════════
def julgar(livro: dict, itens: list, referencia: dict | None = None,
           triados_fora: dict | None = None) -> dict:
    """Le os itens que a corrida G0/v4 admitiu e devolve o livro da CAP-SCI.

    O livro da corrida manda: so e julgado o item que esta na LINEAGE dele com
    o uso `LEITURA_ATEMPORAL_DE_CAPACIDADE` disponivel. Item sem proveniencia
    fica FORA com o motivo — e nao sai da contagem.

    `triados_fora` (INT-R7-CAPS) = {ITEM_ID: motivo} dos itens que o motor
    das capacidades triou para outra capacidade (um boletim sem identidade de
    estudo no FATO nao e estudo). Ficam em FORA com o motivo, e nao sao
    julgados: um boletim julgado como estudo sairia «TEMA_NAO_PROVADO» e
    enchia a contagem de estudos com o que nao e estudo.
    """
    if not isinstance(livro, dict) or livro.get("RESULT_STATE") not in ("DONE", "REUSED"):
        raise LeiViolada("a CAP-SCI so le uma corrida fechada (DONE/REUSED)")
    linhas = {str(l["ITEM_ID"]): l for l in livro.get("LINEAGE", [])}
    refs = [str(r.get("ITEM_ID")) for r in livro.get("INPUT_REFERENCES", [])]
    for it in itens:
        conferir_ready(it)
    ids = [str(it.get("ITEM_ID")) for it in itens]
    if sorted(ids) != sorted(refs):
        raise LeiViolada("os itens nao sao os que a corrida %s consumiu"
                         % livro.get("INTELLIGENCE_RUN_ID"))
    ref = referencia if referencia is not None else carregar_referencia()

    estudos, fora = [], []
    for it in itens:
        l = linhas.get(str(it["ITEM_ID"]))
        if it["ITEM_ID"] in (triados_fora or {}):
            fora.append({"ITEM_ID": it["ITEM_ID"], "PORQUE": triados_fora[it["ITEM_ID"]]})
            continue
        if l is None or USO_EXIGIDO not in l.get("USOS_DISPONIVEIS", []):
            fora.append({"ITEM_ID": it["ITEM_ID"],
                         "PORQUE": (l or {}).get("USOS_BLOQUEADOS", {}).get(
                             USO_EXIGIDO, "fora da LINEAGE da corrida")})
            continue
        estudos.append(julgar_estudo(it))

    grupos = independencia(estudos)
    ligacoes = [ligar_ao_produto(e, ref) for e in estudos
                if e["ESPECIE"] != ESPECIE_MODELO]
    livro_sci = {
        "SCHEMA": CONTRATO,
        "CAPACIDADE": CAPACIDADE,
        "PERGUNTA": PERGUNTA,
        "INTELLIGENCE_RUN_ID": livro.get("INTELLIGENCE_RUN_ID"),
        "RULESET_DA_CORRIDA": livro.get("RULESET_VERSION"),
        "CODE_VERSION": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16],
        "REFERENCIA": {k: ref.get(k, NAO_SEI) for k in ("ESTADO", "PASTA", "SHA256", "PORQUE")
                       if k in ref},
        "UNIVERSO": {"ITENS": len(itens), "JULGADOS": len(estudos), "FORA": len(fora)},
        "ESTUDOS": estudos,
        "FORA": fora,
        "INDEPENDENCIA": grupos,
        "REPLICACAO": replicacao(estudos, grupos),
        "REGRAS_DE_MODELO": [e["ITEM_ID"] for e in estudos if e["ESPECIE"] == ESPECIE_MODELO],
        "RESISTENCIAS": [e["ITEM_ID"] for e in estudos if e["ESPECIE"] == ESPECIE_RESISTENCIA],
        "LIGACOES": [x for x in ligacoes if x["ESTADO"] in ("PARTIAL", "CANDIDATE")],
        "TENTATIVAS_DE_LIGACAO": _contar(x["ESTADO"] for x in ligacoes),
        "CONTAGENS": {
            "FORCA": _contar(e["FORCA"]["NIVEL"] for e in estudos),
            "APLICABILIDADE": _contar(e["APLICABILIDADE"]["ESTADO"] for e in estudos),
            "ESPECIE": _contar(e["ESPECIE"] for e in estudos),
            "LEITURA": _contar(e["LEITURA"] for e in estudos),
        },
        "NAO_PRODUZ": ["FINDING", "OPPORTUNITY", "INCIDENCIA_DE_CAMPO", "SCORE_UNICO"],
    }
    _vigiar_leituras_proibidas(livro_sci)
    return livro_sci


def _vigiar_leituras_proibidas(livro_sci: dict) -> None:
    """Ultima trava: nenhuma leitura proibida sai deste livro, escrita onde for."""
    texto = json.dumps({k: v for k, v in livro_sci.items() if k != "PERGUNTA"},
                       ensure_ascii=False).upper()
    sujo = [p for p in LEITURAS_PROIBIDAS if p in texto]
    if sujo:
        raise LeiViolada("a CAP-SCI ia escrever leitura proibida: " + ", ".join(sujo))


def _contar(xs) -> dict:
    out: dict = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return dict(sorted(out.items()))


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip().split("\n\n")[0])
        print("\n  uso: python3 motor/capacidade_cientifica.py <itens-ready.json>")
        return 2
    dado = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    itens = dado.get("ITENS", []) if isinstance(dado, dict) else dado
    livro = CORRIDA.correr("CAP-SCI: " + PERGUNTA, itens,
                           universo={"CORTE": Path(sys.argv[1]).name,
                                     "ITENS_NO_CORTE": len(itens)})
    print(json.dumps(julgar(livro, itens), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
