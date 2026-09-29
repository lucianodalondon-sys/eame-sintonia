#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PRODUTOR DE AFIRMACOES — de um DOCUMENTO da Sala para AFIRMACOES COM PROVA (D158).

    afirmacoes_do_item(item) -> {"AFIRMACOES": [...], "FUNIL": {...}}
    conferir_afirmacao(af, texto) -> [violacoes]

POR QUE ISTO EXISTE
-------------------
A COL-LAW-202 (`ARTIFACT → CLAIM`, BIBLIA-CANONICA-DA-COLETA.md:1803-1823) estava `ABSENT`:
o SINTONIA guardava DOCUMENTOS e nunca AFIRMACOES. Sem afirmacao, tudo o que a Intelligence
recebia era o documento inteiro com a data e o lugar do documento inteiro — e foi por isso
que os dois objetos da corrida R9 tiveram de ser ESCRITOS A MAO. Esta e a versao MINIMA que
o dono autorizou (D158): o caminho DOCUMENTO → AFIRMACOES COM PROVA → INTELLIGENCE,
repetivel, deterministico, sem LLM.

O QUE UMA AFIRMACAO E
---------------------
UM trecho do texto, com tudo o que prova que ele e daquele documento e o que a fonte diz
sobre QUANDO e ONDE:

    ASSERTION_ID      deterministico: SOURCE_ID + RAW_SHA256 + offset inicio/fim + trecho
    TRECHO_LITERAL    exactamente texto[INICIO:FIM] — nunca reescrito, nunca normalizado
    POSICAO           offset inicio/fim + a seccao que governa o trecho
    CONTEXTO_MINIMO   so quando o sentido do trecho depende dele (entidade ou data herdada)
    FACT_TIME         valor / NAO SEI / NAO_EXISTE, com PAPEL, ORIGEM e BASIS (trecho+offset)
    FACT_LOCATION     valor / NAO SEI, com LOCATION_SOURCE e o trecho que o prova
    PROVENIENCIA      o caminho ate ao documento e ate ao RAW original

O QUE ELE NAO DECIDE
--------------------
Relevancia comercial, oportunidade, ligacao ADAMA, recomendacao, prioridade, LIBERACAO,
produto ou significado estrategico. Isso e da Intelligence e dos portoes depois dela. A
Collection nao vira Intelligence (INT-LAW-030/031 · COL-LAW-201/202).

O QUE ELE REUSA (e por isso nao ha extractor paralelo nenhum)
-------------------------------------------------------------
    leis/fato_do_texto.py         o corpo (`sem_vizinhos`, `corpo`), e o leitor temporal vivo
    leis/tempo_da_afirmacao.py    a INTERFACE do leitor temporal: papel, origem e basis (D158)
    leis/boletim_do_campo.py      `ler_afirmacao`: cultura, praga e LUGAR do trecho, com a
                                  procedencia de cada um e as travas COL-LAW-221/032
    leis/afirmacao_da_fonte.py    o vocabulario e as travas da afirmacao (D112)

A PARTE NOVA, e so ela: quem da o `inicio/fim` a `ler_afirmacao` (ate hoje era o gabarito,
a mao) e quem parte o documento em SECCOES estruturais. Tudo por regra declarada.

Funcao PURA: sem rede, sem banco, sem ficheiros.

    python3 leis/afirmacao_do_documento.py     # imprime o contrato
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
if _AQUI not in sys.path:
    sys.path.insert(0, _AQUI)

import afirmacao_da_fonte as AF        # noqa: E402
import boletim_do_campo as BC          # noqa: E402
import fato_do_texto as FT             # noqa: E402
import tempo_da_afirmacao as TA        # noqa: E402

CONTRATO = "AFIRMACAO/v1"
NAO_SEI = FT.NAO_SEI
UNRESOLVED = BC.UNRESOLVED

#: o prefixo do ASSERTION_ID e quantas letras do sha entram nele
PREFIXO_DO_ID = "AF-"
LETRAS_DO_ID = 24


# ════════════════════════════════════════════════════════════════════════════
# 1 · AS SECCOES ESTRUTURAIS DO DOCUMENTO
# ════════════════════════════════════════════════════════════════════════════
# Uma seccao e o bloco que governa um trecho. Ela abre em DOIS sitios, e so nestes:
#   · a QUEBRA DE PAGINA («\f») que o extractor de PDF escreve;
#   · a LINHA DE CABECALHO — curta, sem ponto final, em maiusculas ou com as letras
#     dobradas do PDF (`tempo_da_afirmacao.e_cabecalho`).
# ⚠️ LIMITE DECLARADO: um cabecalho escrito em Maiusculas De Titulo («Situazione Attuale»)
# NAO abre seccao aqui. Preferiu-se falhar de menos a cortar o corpo ao meio: uma seccao a
# mais partiria uma afirmacao do periodo que a governa, e isso seria dado errado, nao dado
# a menos. A seccao TERRITORIAL continua a ser a de `boletim_do_campo.secoes_territoriais`
# — sao perguntas diferentes (esta diz ONDE o trecho esta; aquela diz de que LUGAR ele fala).
def secoes_do_documento(texto: str) -> list:
    """[{"INICIO", "FIM", "CABECALHO", "CABECALHO_INICIO", "CABECALHO_FIM"}] — em ordem."""
    t = str(texto or "")
    cortes, cabecalhos, pos = {0}, {}, 0
    for linha in t.splitlines(keepends=True):
        a, b = pos, pos + len(linha)
        pos = b
        crua = linha.rstrip("\r\n")
        for m in re.finditer("\f", crua):
            cortes.add(a + m.start())
        limpa = crua.replace("\f", " ")
        if TA.e_cabecalho(limpa):
            inicio = a + (len(limpa) - len(limpa.lstrip()))
            cortes.add(inicio)
            cabecalhos[inicio] = (limpa.strip(), inicio, a + len(limpa.rstrip()))
    ordenados = sorted(cortes) + [len(t)]
    fora = []
    for i in range(len(ordenados) - 1):
        a, b = ordenados[i], ordenados[i + 1]
        if a >= b:
            continue
        cab = cabecalhos.get(a)
        fora.append({"INICIO": a, "FIM": b,
                     "CABECALHO": TA.como_se_le(cab[0]) if cab else None,
                     "CABECALHO_LITERAL": cab[0] if cab else None,
                     "CABECALHO_INICIO": cab[1] if cab else None,
                     "CABECALHO_FIM": cab[2] if cab else None})
    return fora


def secao_de(secoes: list, pos: int) -> dict:
    for s in secoes:
        if s["INICIO"] <= pos < s["FIM"]:
            return s
    return {"INICIO": 0, "FIM": pos, "CABECALHO": None, "CABECALHO_LITERAL": None,
            "CABECALHO_INICIO": None, "CABECALHO_FIM": None}


# ════════════════════════════════════════════════════════════════════════════
# 2 · AS FRASES — quem da o inicio/fim que `ler_afirmacao` sempre pediu
# ════════════════════════════════════════════════════════════════════════════
# Uma frase acaba em «.», «!», «?» ou «;» SEGUIDO de espaco ou do fim do texto. A condicao
# do espaco e o que separa «46.8 mm» (numero) de «… 32,8 mm.» (fim de frase) — medido: sem
# ela, `fato_local._frases` partia a frase dos acumulados ao meio, no decimal.
# Tambem cortam: a linha em branco (paragrafo), a quebra de pagina e a linha de cabecalho —
# um cabecalho nunca faz parte da frase que vem a seguir.
_RE_FIM_DE_FRASE = re.compile(r"[.!?;](?=\s|$)")

# ── A VIRGULA QUE EMENDA DUAS FRASES ─────────────────────────────────────────
# Num texto tirado de PDF aparece o ponto que o compositor perdeu: «… sul Salento, Gli
# accumuli settimanali …». Sem isto, DUAS afirmacoes diferentes viajam num trecho so — e um
# trecho que mistura duas afirmacoes e uma prova pior, com ou sem R9.
# A regra e estreita de proposito, e so ela: virgula + PALAVRA DE CLASSE FECHADA em
# maiuscula + palavra em minuscula. A classe fechada (artigo, determinante, preposicao
# articulada) nunca e nome proprio; a minuscula a seguir e a guarda que salva «La Spezia»,
# «Le Marche» e «Il Cairo», onde a segunda palavra vem em maiuscula e nao se corta nada.
_CLASSE_FECHADA = ("il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "questo", "questa",
                   "questi", "queste", "nel", "nella", "nei", "negli", "nelle", "dal", "dalla",
                   "dai", "dagli", "dalle", "del", "della", "dei", "degli", "delle", "sul",
                   "sulla", "sui", "sugli", "sulle", "al", "alla", "ai", "agli", "alle",
                   "non", "si", "che", "per", "con", "tra", "fra", "durante", "inoltre")
_RE_VIRGULA_QUE_EMENDA = re.compile(
    r",\s+(?:%s)\s+[a-zà-ÿ]" % "|".join(w.capitalize() for w in _CLASSE_FECHADA))


def _cortes_duros(texto: str, ini: int, fim: int) -> list:
    """Onde uma frase nao pode atravessar: paragrafo, pagina e linha de cabecalho."""
    fora, pos = [], 0
    for linha in str(texto or "").splitlines(keepends=True):
        a, b = pos, pos + len(linha)
        pos = b
        if b <= ini or a >= fim:
            continue
        crua = linha.rstrip("\r\n")
        if not crua.strip() or "\f" in crua or TA.e_cabecalho(crua.replace("\f", " ")):
            fora += [a, b]
    return sorted({x for x in fora if ini <= x <= fim})


def frases(texto: str, ini: int, fim: int):
    """Os (inicio, fim) de cada frase de texto[ini:fim], em `texto`."""
    t = str(texto or "")
    limites = sorted({ini, fim} | set(_cortes_duros(t, ini, fim))
                     | {m.end() for m in _RE_FIM_DE_FRASE.finditer(t, ini, fim)}
                     | {m.start() + 1 for m in _RE_VIRGULA_QUE_EMENDA.finditer(t, ini, fim)})
    for a, b in zip(limites, limites[1:]):
        pedaco = t[a:b]
        if not pedaco.strip():
            continue
        esquerda = a + (len(pedaco) - len(pedaco.lstrip()))
        direita = b - (len(pedaco) - len(pedaco.rstrip()))
        if direita > esquerda:
            yield esquerda, direita


def e_corpo(frase: str) -> bool:
    """A mesma pergunta que o vivo faz a cada linha (`fato_do_texto.corpo`): tem frase, e
    nao e rodape nem institucional. Nao se reescreve a regra: leem-se as constantes do dono."""
    s = str(frase or "").strip()
    return FT._palavras(s) >= FT.PALAVRAS_MINIMAS and not FT.RODAPE.search(s)


# ════════════════════════════════════════════════════════════════════════════
# 3 · A AFIRMACAO
# ════════════════════════════════════════════════════════════════════════════
def assertion_id(source_id, raw_sha256, inicio, fim, trecho) -> str:
    """Deterministico e sem estado: a mesma afirmacao do mesmo byte da sempre o mesmo ID."""
    semente = "|".join([str(source_id or NAO_SEI), str(raw_sha256 or NAO_SEI),
                        str(int(inicio)), str(int(fim)), str(trecho)])
    return PREFIXO_DO_ID + hashlib.sha256(semente.encode("utf-8")).hexdigest()[:LETRAS_DO_ID]


def sha_do_trecho(trecho: str) -> str:
    return hashlib.sha256(str(trecho).encode("utf-8")).hexdigest()


def _literal(basis, original):
    """O TRECHO de um `basis` passa a ser o do documento ORIGINAL, no mesmo offset."""
    if isinstance(basis, dict) and isinstance(basis.get("INICIO"), int):
        basis["TRECHO"] = original[basis["INICIO"]:basis["FIM"]]
    return basis


def _contexto_minimo(texto, secao, inicio, precisa: list) -> dict | None:
    """O MINIMO que falta para o trecho fazer sentido: do inicio do bloco ate ao trecho.

    So sai quando alguma coisa do sentido veio de FORA do trecho (entidade herdada, data
    composta do cabecalho). Sem isso, None — contexto que ninguem precisa e ruido.

    ⚠️ `texto` tem de ser o texto ORIGINAL do documento, nao o texto ja limpo pela D19:
    tudo o que a afirmacao guarda e literal, e a conferencia confere-o contra o original."""
    if not precisa:
        return None
    a = max(secao["INICIO"], inicio - JANELA_DO_CONTEXTO)
    if secao.get("CABECALHO_INICIO") is not None:
        a = min(a, secao["CABECALHO_INICIO"])
    a = max(a, secao["INICIO"])
    if a >= inicio:
        return None
    return {"TRECHO": texto[a:inicio], "INICIO": a, "FIM": inicio,
            "PORQUE": "; ".join(precisa)}


#: quanto contexto antes do trecho se guarda quando ele e preciso (letras)
JANELA_DO_CONTEXTO = 600


def _lugar(leitura: dict) -> dict:
    """O FACT_LOCATION da afirmacao, tal como a lei o devolveu — sem reescrever nada."""
    l_ = leitura["FACT_LOCATION"]
    valor = l_["VALOR"]
    return {"VALOR": NAO_SEI if valor == UNRESOLVED else valor,
            "LOCATION_SOURCE": l_["LOCATION_SOURCE"],
            "PRECISAO": l_.get("PRECISAO") or "NOT_KNOWN",
            "TRECHO": l_.get("LOCATION_EXPRESSION_RAW"),
            "PROVA": l_.get("PROVA"),
            "PORQUE": l_.get("PORQUE"),
            "PONTO_NO_MAPA": bool(l_.get("PONTO_NO_MAPA"))}


def _entidade(r: dict) -> dict:
    return {"VALOR": r["VALOR"], "ENTITY_SOURCE": r["ENTITY_SOURCE"],
            "PROVA": r.get("PROVA"), "MOTIVO": r.get("MOTIVO")}


def afirmacoes(texto: str, *, titulo=None, published_at=None, published_at_basis=None,
               proveniencia: dict | None = None) -> dict:
    """As AFIRMACOES de UM documento. `proveniencia` viaja inteira dentro de cada uma."""
    original = str(texto or "")
    t = FT.sem_vizinhos(original)
    if len(t) != len(original):                      # a lei do D19 promete o comprimento
        raise AssertionError("sem_vizinhos mudou o comprimento do texto: os offsets deixariam de bater")
    secoes = secoes_do_documento(t)
    prov = dict(proveniencia or {})
    publicacao = {"VALOR": published_at, "BASE": published_at_basis}

    lidas, fora_do_corpo, sem_prova = [], 0, 0
    for s in secoes:
        for a, b in frases(t, s["INICIO"], s["FIM"]):
            span = t[a:b]
            if not e_corpo(span):
                fora_do_corpo += 1
                continue
            if span != original[a:b]:
                # o D19 tapou parte deste trecho (menu / manchete vizinha): nao e corpo
                fora_do_corpo += 1
                continue
            leitura = BC.ler_afirmacao(original, a, b, titulo=titulo)
            tempo = TA.extrair_tempo(t, {"INICIO": a, "FIM": b, "SECAO": s, "PUBLICACAO": publicacao})
            precisa = []
            for nome, r in (("cultura", leitura["CULTURA"]), ("praga", leitura["PRAGAS"])):
                if r["ENTITY_SOURCE"] not in (BC.SPAN, BC.UNKNOWN):
                    precisa.append("a %s veio de %s, fora do trecho" % (nome, r["ENTITY_SOURCE"]))
            if tempo["ORIGEM"] == TA.CABECALHO:
                precisa.append("a data veio do cabecalho da seccao, fora do trecho")
            # Tudo o que a afirmacao guarda e LITERAL do documento. O leitor temporal
            # trabalha sobre o texto limpo pela D19 (mesmo comprimento, logo mesmos
            # offsets); o TRECHO que viaja e o do ORIGINAL, que e o que a conferencia confere.
            _literal(tempo.get("BASIS"), original)
            af = {
                "CONTRATO": CONTRATO,
                "ASSERTION_ID": assertion_id(prov.get("SOURCE_ID"), prov.get("RAW_SHA256"), a, b, span),
                "TRECHO_LITERAL": span,
                "TRECHO_SHA256": sha_do_trecho(span),
                "POSICAO": {"INICIO": a, "FIM": b,
                            "SECAO": {"INICIO": s["INICIO"], "FIM": s["FIM"],
                                      "CABECALHO": s["CABECALHO"],
                                      "CABECALHO_INICIO": s["CABECALHO_INICIO"],
                                      "CABECALHO_FIM": s["CABECALHO_FIM"]},
                            "SECAO_TERRITORIAL": leitura["SECAO"]},
                "CONTEXTO_MINIMO": _contexto_minimo(original, s, a, precisa),
                "FACT_TIME": {"VALOR": tempo["VALOR"] if tempo["PAPEL"] in TA.PAPEL_QUE_E_FACTO
                              else (TA.NAO_EXISTE if tempo["VALOR"] == TA.NAO_EXISTE else NAO_SEI),
                              "PORQUE_NAO": None if tempo["PAPEL"] in TA.PAPEL_QUE_E_FACTO else tempo["PORQUE"]},
                "FACT_TIME_ROLE": {"PAPEL": tempo["PAPEL"], "VALOR_LIDO": tempo["VALOR"],
                                   "ORIGEM": tempo["ORIGEM"], "BASIS": tempo["BASIS"],
                                   "PRECISAO": tempo["PRECISAO"], "PORQUE": tempo["PORQUE"],
                                   "COMPOSICAO": tempo.get("COMPOSICAO"),
                                   "LEITOR": tempo["LEITOR"],
                                   "PUBLICACAO_PROVADA": tempo["PUBLICACAO_PROVADA"]},
                "FACT_LOCATION": _lugar(leitura),
                "ENTIDADES": {"CULTURA": _entidade(leitura["CULTURA"]),
                              "PRAGAS": _entidade(leitura["PRAGAS"])},
                "PROVENIENCIA": prov,
                "LEI": ("COL-LAW-202 · o trecho e a prova; a data so e do facto com o papel "
                        "ACONTECIMENTO; publicacao nunca e FACT_TIME; NAO SEI e saida valida"),
            }
            if af["FACT_TIME"]["VALOR"] in (NAO_SEI, TA.NAO_EXISTE) and af["FACT_LOCATION"]["VALOR"] == NAO_SEI:
                sem_prova += 1
            lidas.append(af)
    return {"AFIRMACOES": lidas,
            "FUNIL": {"SECOES": len(secoes), "FRASES_FORA_DO_CORPO": fora_do_corpo,
                      "AFIRMACOES": len(lidas),
                      "COM_TEMPO_DO_FACTO": sum(1 for x in lidas
                                                if x["FACT_TIME"]["VALOR"] not in (NAO_SEI, TA.NAO_EXISTE)),
                      "COM_LUGAR_DO_FACTO": sum(1 for x in lidas if x["FACT_LOCATION"]["VALOR"] != NAO_SEI),
                      "COM_TEMPO_E_LUGAR": sum(1 for x in lidas
                                               if x["FACT_TIME"]["VALOR"] not in (NAO_SEI, TA.NAO_EXISTE)
                                               and x["FACT_LOCATION"]["VALOR"] != NAO_SEI),
                      "SEM_TEMPO_NEM_LUGAR": sem_prova}}


#: os campos da Sala que viajam dentro da PROVENIENCIA de cada afirmacao
CAMPOS_DA_PROVENIENCIA = ("ITEM_ID", "RUN_ID", "ORDEM", "SOURCE_ID", "UNIVERSO",
                          "RAW_OBSERVATION_ID", "RAW_SHA256", "RAW_STORAGE_PATH",
                          "DOCUMENT_ID", "URL", "PUBLISHED_AT", "PUBLISHED_AT_BASIS", "COLHIDO_EM")
#: como cada um se chama na linha da Sala (`admissao/sala_de_espera.py`)
_DA_SALA = {"ITEM_ID": "item_id", "RUN_ID": "run_id", "ORDEM": "ordem", "SOURCE_ID": "source_id",
            "UNIVERSO": "universo", "RAW_OBSERVATION_ID": "raw_observation_id",
            "RAW_SHA256": "raw_sha256", "RAW_STORAGE_PATH": "raw_storage_path",
            "DOCUMENT_ID": "raw_document_key", "URL": "raw_source_url",
            "PUBLISHED_AT": "published_at", "PUBLISHED_AT_BASIS": "published_at_basis",
            "COLHIDO_EM": "raw_captured_at"}


def proveniencia_da_sala(linha: dict) -> dict:
    """A PROCEDENCIA de uma linha da Sala. Valor que a Sala nao tem sai NAO SEI — nunca
    calculado, nunca adivinhado (o RAW_SHA256 e o do banco ou e NAO SEI)."""
    prov = {}
    for k in CAMPOS_DA_PROVENIENCIA:
        v = (linha or {}).get(_DA_SALA[k])
        prov[k] = NAO_SEI if v in (None, "") else v
    prov["CAMINHO"] = ("SALA(%s#%s) → RAW_OBSERVATION(%s) → RAW_ASSET(sha256 %s) → %s"
                       % (prov["RUN_ID"], prov["ORDEM"], prov["RAW_OBSERVATION_ID"],
                          prov["RAW_SHA256"], prov["RAW_STORAGE_PATH"]))
    return prov


def afirmacoes_do_item(linha: dict) -> dict:
    """As afirmacoes de UMA linha da Sala de Espera (o contrato READY)."""
    prov = proveniencia_da_sala(linha)
    r = afirmacoes(linha.get("texto") or "",
                   titulo=linha.get("titulo"),
                   published_at=linha.get("published_at"),
                   published_at_basis=linha.get("published_at_basis"),
                   proveniencia=prov)
    r["PROVENIENCIA"] = prov
    return r


# ════════════════════════════════════════════════════════════════════════════
# 4 · A CONFERENCIA — o programa prova o trecho de origem
# ════════════════════════════════════════════════════════════════════════════
def conferir_afirmacao(af: dict, texto: str, *, raw_sha256=None) -> list:
    """As violacoes desta afirmacao contra o texto (e contra o byte, se ele for dado).

    Lista vazia = a afirmacao sustenta-se. Isto e o que faz de NAO SEI uma saida valida:
    o que nao se sustenta nao passa a ser opiniao, e reprovado."""
    v = []
    if not isinstance(af, dict) or af.get("CONTRATO") != CONTRATO:
        return ["fora do contrato %s" % CONTRATO]
    t = str(texto or "")
    pos = af.get("POSICAO") or {}
    a, b = pos.get("INICIO"), pos.get("FIM")
    if not isinstance(a, int) or not isinstance(b, int) or not (0 <= a < b <= len(t)):
        return ["offset invalido: INICIO=%r FIM=%r num texto de %d letras" % (a, b, len(t))]
    trecho = af.get("TRECHO_LITERAL")
    if trecho != t[a:b]:
        v.append("o TRECHO_LITERAL nao e texto[%d:%d]: o documento mudou ou a ancora esta errada" % (a, b))
    if af.get("TRECHO_SHA256") != sha_do_trecho(trecho or ""):
        v.append("TRECHO_SHA256 nao bate com o trecho")
    prov = af.get("PROVENIENCIA") or {}
    if raw_sha256 is not None and prov.get("RAW_SHA256") not in (NAO_SEI, raw_sha256):
        v.append("RAW_SHA256 da afirmacao (%s) != o do documento (%s): documento alterado"
                 % (prov.get("RAW_SHA256"), raw_sha256))
    esperado = assertion_id(prov.get("SOURCE_ID"), prov.get("RAW_SHA256"), a, b, trecho)
    if af.get("ASSERTION_ID") != esperado:
        v.append("ASSERTION_ID nao e o hash desta afirmacao")
    secao = (pos.get("SECAO") or {})
    if not (secao.get("INICIO", 0) <= a and b <= secao.get("FIM", len(t))):
        v.append("o trecho esta fora da seccao declarada")
    papel = (af.get("FACT_TIME_ROLE") or {}).get("PAPEL")
    if papel not in TA.PAPEIS and papel != NAO_SEI:
        v.append("FACT_TIME_ROLE.PAPEL %r fora do vocabulario" % (papel,))
    ft = (af.get("FACT_TIME") or {}).get("VALOR")
    if ft not in (NAO_SEI, TA.NAO_EXISTE) and papel not in TA.PAPEL_QUE_E_FACTO:
        v.append("FACT_TIME com valor e papel %r: so ACONTECIMENTO e tempo do facto" % (papel,))
    basis = (af.get("FACT_TIME_ROLE") or {}).get("BASIS")
    if ft not in (NAO_SEI, TA.NAO_EXISTE):
        if not isinstance(basis, dict):
            v.append("FACT_TIME com valor e sem BASIS")
        elif basis.get("TRECHO") != t[basis.get("INICIO", -1):basis.get("FIM", -1)]:
            v.append("o BASIS do FACT_TIME nao esta no texto onde diz estar")
    loc = af.get("FACT_LOCATION") or {}
    if loc.get("VALOR") != NAO_SEI and loc.get("LOCATION_SOURCE") not in BC.LOCATION_SOURCES:
        v.append("FACT_LOCATION com valor e LOCATION_SOURCE %r fora da COL-LAW-032"
                 % (loc.get("LOCATION_SOURCE"),))
    for nome in ("CULTURA", "PRAGAS"):
        e = (af.get("ENTIDADES") or {}).get(nome) or {}
        if e.get("ENTITY_SOURCE") not in AF.ENTITY_SOURCES:
            v.append("%s com ENTITY_SOURCE %r fora da COL-LAW-221" % (nome, e.get("ENTITY_SOURCE")))
    ctx = af.get("CONTEXTO_MINIMO")
    if ctx and ctx.get("TRECHO") != t[ctx.get("INICIO", -1):ctx.get("FIM", -1)]:
        v.append("o CONTEXTO_MINIMO nao esta no texto onde diz estar")
    return v


def contrato() -> dict:
    return {
        "SOURCE_ID": "AFIRMACAO-DO-DOCUMENTO-CONTRATO",
        "VERSION": "V1",
        "DECISAO": "D158",
        "CONTRATO": CONTRATO,
        "LEIS": ["COL-LAW-201", "COL-LAW-202", "COL-LAW-221", "COL-LAW-222", "COL-LAW-032",
                 "INT-LAW-030", "INT-LAW-031", "D63", "D112", "D147", "D149", "D153"],
        "CAMPOS": ["ASSERTION_ID", "TRECHO_LITERAL", "TRECHO_SHA256", "POSICAO", "CONTEXTO_MINIMO",
                   "FACT_TIME", "FACT_TIME_ROLE", "FACT_LOCATION", "ENTIDADES", "PROVENIENCIA"],
        "PAPEIS_DO_TEMPO": list(TA.PAPEIS),
        "PAPEL_QUE_E_FACTO": list(TA.PAPEL_QUE_E_FACTO),
        "REUSA": [TA.LEITOR_VIVO, "leis/tempo_da_afirmacao.py::extrair_tempo",
                  "leis/boletim_do_campo.py::ler_afirmacao", "leis/afirmacao_da_fonte.py"],
        "NAO_DECIDE": ["relevancia comercial", "oportunidade", "ligacao ADAMA", "recomendacao",
                       "prioridade", "liberacao", "produto", "significado estrategico"],
        "SEM_LLM": True,
    }


if __name__ == "__main__":
    json.dump(contrato(), sys.stdout, ensure_ascii=False, indent=1)
    print()
