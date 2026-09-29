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

#: Porque SUBJECT/PREDICATE/OBJECT saem NAO SEI: partir uma frase italiana em sujeito,
#: predicado e objeto e um analisador sintatico, e a D158 autorizou a versao MINIMA e
#: DETERMINISTICA. O campo esta presente, como o contrato de consumo exige, e a afirmacao
#: inteira e o TRECHO LITERAL — que a Intelligence tem e pode citar.
_SEM_SVO = ("o produtor minimo nao parte a frase em sujeito/predicado/objeto: isso seria um "
            "analisador sintatico. A afirmacao e o EVIDENCE_SPAN literal, que viaja inteiro.")


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


# ════════════════════════════════════════════════════════════════════════════
# 2b · O CONTRATO DE CONSUMO DA INTELLIGENCE (D158)
# ════════════════════════════════════════════════════════════════════════════
# O dono da Intelligence escreveu o que aceita consumir
# (`CONTRATO-CONSUMO-AFIRMACOES.md`, fora do Git). Duas coisas dele vivem aqui, porque sao
# a FORMA da afirmacao e nao o juizo sobre ela:
#
#   · a CLASSE do claim (`CLAIM_KIND`), que decide QUE TEMPO a Intelligence vai exigir;
#   · os campos que o produtor NUNCA escreve. Escrever um deles seria a Collection a
#     decidir liberacao, e a afirmacao inteira e recusada com esse motivo.
CLAIM_KINDS = ("ALERTA_EVENTO", "CIENCIA_FICHA", "PRECO", "REGULATORIO", "RECOMENDACAO")
#: Escrever qualquer um destes = PRODUTOR_DECIDIU_LIBERACAO, e a afirmacao nao viaja.
CAMPOS_PROIBIDOS = ("LIBERADO", "LIBERACAO", "LIBERADO_POR", "LIBERADO_NA_CORRIDA",
                    "CONFERENCIA_DE_LIBERACAO", "NAO_PARA_CLIENTE", "ESPECIE", "USO",
                    "RELEVANCIA", "OPORTUNIDADE", "LIGACAO_ADAMA", "RECOMENDACAO",
                    "PRIORIDADE", "PRODUTO", "SCORE")

# A superficie de cada classe. Nao e saber agronomico nem comercial: e a palavra com que a
# propria fonte diz de que tipo e a frase. As marcas administrativas sao as da interface do
# tempo (`tempo_da_afirmacao`), lidas de la — nao ha segunda lista.
_RE_PRECO = re.compile(
    r"(?<![a-zà-ÿ])(?:prezz|quotazion|listin|mercuriale|€|\d+[,.]\d+\s*(?:€|euro)|"
    r"(?:€|euro)\s*\d|al\s+kg|/\s*kg|al\s+quintale|al\s+litro)", re.I)
_RE_ESTUDO = re.compile(r"(?:\b10\.\d{4,9}/\S+|\bdoi\b|\bnct\d{6,}\b|\btrial\s+(?:id|n)|"
                        r"\bsperimentazion|\bprova\s+sperimentale)", re.I)


def classe_do_claim(span: str, tempo: dict) -> dict:
    """A CLASSE do claim, no vocabulario fechado do contrato de consumo.

    A regra e a mesma da D112 para duas pragas: quando o trecho traz a marca de DUAS
    classes, escolher uma seria inferir — sai NAO SEI, com as duas marcas escritas.
    ALERTA_EVENTO nao tem marca propria: e o que sobra quando a fonte prende uma data de
    ACONTECIMENTO ao que ela conta, e por isso nao entra no conflito."""
    marcas = []
    if TA._MARCA_DE_ATO.search(span) or TA._MARCA_DE_VALIDADE.search(span):
        marcas.append("REGULATORIO")
    if _RE_PRECO.search(span) or TA._MARCA_DE_MERCADO.search(span):
        marcas.append("PRECO")
    if FT._RE_RECOMENDACAO.search(span):
        marcas.append("RECOMENDACAO")
    if _RE_ESTUDO.search(span):
        marcas.append("CIENCIA_FICHA")
    if len(marcas) > 1:
        return {"VALOR": NAO_SEI, "MARCAS": marcas,
                "PORQUE": "o trecho traz a marca de %d classes (%s); escolher uma seria inferir"
                          % (len(marcas), ", ".join(marcas))}
    if marcas:
        return {"VALOR": marcas[0], "MARCAS": marcas, "PORQUE": "a marca da classe esta escrita no trecho"}
    if tempo["PAPEL"] == TA.ACONTECIMENTO:
        return {"VALOR": "ALERTA_EVENTO", "MARCAS": [],
                "PORQUE": "a fonte prende uma data de ACONTECIMENTO ao que conta, e nao ha marca de outra classe"}
    return {"VALOR": NAO_SEI, "MARCAS": [],
            "PORQUE": "o trecho nao escreve marca de classe nenhuma e nao tem data de acontecimento"}


def _nome_original(nome, span: str):
    """A forma como o nome esta ESCRITO no trecho, quando esta LITERALMENTE la.

    O nome que sai de `ler_afirmacao` ja vem NORMALIZADO pela tabela `MESMO_PROBLEMA`: o
    texto pode escrever «mosca delle olive» e o valor ser «mosca dell'olivo». Quando as
    duas formas nao coincidem, NOME_ORIGINAL fica NAO SEI — a forma escrita nao se
    adivinha, e a que a Intelligence tem e o EVIDENCE_SPAN inteiro."""
    m = re.search(re.escape(str(nome)), span, re.I)
    return m.group(0) if m else NAO_SEI


def _entidades(leitura: dict, span: str) -> list:
    """As entidades da afirmacao, na forma do contrato de consumo: uma por nome, cada uma
    com NOME_ORIGINAL, VALOR_NORMALIZADO e o ENTITY_SOURCE da COL-LAW-221."""
    fora = []
    for tipo, r in (("CULTURA", leitura["CULTURA"]), ("PRAGA_OU_DOENCA", leitura["PRAGAS"])):
        valores = r["VALOR"] if isinstance(r["VALOR"], list) else []
        if not valores:
            fora.append({"TIPO": tipo, "NOME_ORIGINAL": NAO_SEI, "VALOR_NORMALIZADO": NAO_SEI,
                         "ENTITY_SOURCE": r["ENTITY_SOURCE"], "PROVA": r.get("PROVA"),
                         "PORQUE": r.get("MOTIVO") or "o trecho nao nomeia nenhuma"})
            continue
        for v in valores:
            fora.append({"TIPO": tipo, "NOME_ORIGINAL": _nome_original(v, span),
                         "VALOR_NORMALIZADO": v, "ENTITY_SOURCE": r["ENTITY_SOURCE"],
                         "PROVA": r.get("PROVA"), "PORQUE": r.get("MOTIVO")})
    return fora


def _periodo_por_papel(tempo: dict, papel: str) -> dict:
    """O periodo que a fonte marcou com ESTE papel, ou NAO SEI com o porque.

    A Intelligence exige VALIDITY / MARKET_PERIOD / STUDY_PERIOD conforme a classe. O
    produtor so os preenche quando a propria fonte lhes deu esse papel — nunca por classe."""
    if tempo["PAPEL"] == papel:
        return {"VALOR": tempo["VALOR"], "BASIS": tempo["BASIS"], "ORIGEM": tempo["ORIGEM"]}
    return {"VALOR": NAO_SEI, "BASIS": None,
            "PORQUE": "nenhum tempo deste trecho tem o papel %s (o que ha tem o papel %s)"
                      % (papel, tempo["PAPEL"])}


def produtor_versao() -> dict:
    """QUEM extraiu, e com que regra (INT-LAW-052). O selo e o sha256 dos dois ficheiros
    de lei que decidem — muda a regra, muda o selo."""
    selo = {}
    for nome in ("afirmacao_do_documento.py", "tempo_da_afirmacao.py"):
        caminho = os.path.join(_AQUI, nome)
        selo["leis/" + nome] = hashlib.sha256(open(caminho, "rb").read()).hexdigest()[:16]
    return {"CONTRATO": CONTRATO, "DECISAO": "D158", "CODIGO": selo,
            "LEITOR_TEMPORAL": TA.LEITOR_VIVO, "SEM_LLM": True}


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

    versao = produtor_versao()
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
            oid = assertion_id(prov.get("SOURCE_ID"), prov.get("RAW_SHA256"), a, b, span)
            e_facto = tempo["PAPEL"] in TA.PAPEL_QUE_E_FACTO
            fact_time = (tempo["VALOR"] if e_facto
                         else (TA.NAO_EXISTE if tempo["VALOR"] == TA.NAO_EXISTE else NAO_SEI))
            af = {
                "CONTRATO": CONTRATO,
                # ── identidade e lineage (§1 do contrato de consumo) ───────────────
                "CLAIM_ID": oid,
                "ASSERTION_ID": oid,          # o MESMO valor, com o nome que a D158 usou
                "ITEM_ID": prov.get("ITEM_ID", NAO_SEI),
                "RAW_OBSERVATION_ID": prov.get("RAW_OBSERVATION_ID", NAO_SEI),
                "RAW_SHA256": prov.get("RAW_SHA256", NAO_SEI),
                "SOURCE_ID": prov.get("SOURCE_ID", NAO_SEI),
                "PRODUTOR_VERSAO": versao,
                "EVIDENCE_SPAN": {"INICIO": a, "FIM": b, "TRECHO": span, "SHA256": sha_do_trecho(span)},
                # os mesmos tres valores, com os nomes que a D158 usou
                "TRECHO_LITERAL": span,
                "TRECHO_SHA256": sha_do_trecho(span),
                "POSICAO": {"INICIO": a, "FIM": b,
                            "SECAO": {"INICIO": s["INICIO"], "FIM": s["FIM"],
                                      "CABECALHO": s["CABECALHO"],
                                      "CABECALHO_INICIO": s["CABECALHO_INICIO"],
                                      "CABECALHO_FIM": s["CABECALHO_FIM"]},
                            "SECAO_TERRITORIAL": leitura["SECAO"]},
                "CONTEXTO_MINIMO": _contexto_minimo(original, s, a, precisa),
                # ── conteudo (§1): o campo esta sempre; o valor pode ser NAO SEI ───
                "CLAIM_KIND": classe_do_claim(span, tempo),
                "SUBJECT": {"VALOR": NAO_SEI, "BASE": _SEM_SVO},
                "PREDICATE": {"VALOR": NAO_SEI, "BASE": _SEM_SVO},
                "OBJECT": {"VALOR": NAO_SEI, "BASE": _SEM_SVO},
                "ENTIDADES": _entidades(leitura, span),
                "FACT_TIME": {"VALOR": fact_time,
                              "FACT_TIME_BASIS": tempo["BASIS"] if e_facto else None,
                              "FACT_TIME_PRECISION": tempo["PRECISAO"] if e_facto else "NOT_KNOWN",
                              "PORQUE_NAO": None if e_facto else tempo["PORQUE"]},
                "FACT_TIME_ROLE": {"PAPEL": tempo["PAPEL"], "VALOR_LIDO": tempo["VALOR"],
                                   "ORIGEM": tempo["ORIGEM"], "BASIS": tempo["BASIS"],
                                   "PRECISAO": tempo["PRECISAO"], "PORQUE": tempo["PORQUE"],
                                   "COMPOSICAO": tempo.get("COMPOSICAO"),
                                   "LEITOR": tempo["LEITOR"],
                                   "PUBLICACAO_PROVADA": tempo["PUBLICACAO_PROVADA"]},
                "VALIDITY": _periodo_por_papel(tempo, TA.VALIDADE),
                "MARKET_PERIOD": _periodo_por_papel(tempo, TA.MARKET_PERIOD),
                "STUDY_PERIOD": {"VALOR": NAO_SEI, "BASIS": None,
                                 "PORQUE": "o produtor minimo nao le identidade de estudo no trecho; "
                                           "quem a le e leis/estudo_chaves.py, ao nivel do item"},
                "ACT_TIME": _periodo_por_papel(tempo, TA.ATO),
                "FACT_LOCATION": _lugar(leitura),
                # ── AO LADO, nunca no lugar do FACT_TIME (§1) ──────────────────────
                "PUBLISHED_AT": {"VALOR": prov.get("PUBLISHED_AT", NAO_SEI),
                                 "BASE": prov.get("PUBLISHED_AT_BASIS", NAO_SEI),
                                 "DE_ONDE": "copiado do item da Sala; nunca preenche FACT_TIME"},
                "OBSERVED_AT": {"VALOR": prov.get("OBSERVED_AT", NAO_SEI),
                                "DE_ONDE": "copiado do item da Sala; nunca preenche FACT_TIME"},
                "COLLECTED_AT": {"VALOR": prov.get("COLHIDO_EM", NAO_SEI),
                                 "DE_ONDE": "copiado do item da Sala; nunca preenche FACT_TIME"},
                "PROVENIENCIA": prov,
                "LEI": ("COL-LAW-202 · o trecho e a prova; a data so e do facto com o papel "
                        "ACONTECIMENTO; publicacao nunca e FACT_TIME; NAO SEI e saida valida. "
                        "O produtor nao decide liberacao (CONTRATO-CONSUMO-AFIRMACOES §0)."),
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
                          "DOCUMENT_ID", "URL", "PUBLISHED_AT", "PUBLISHED_AT_BASIS",
                          "OBSERVED_AT", "COLHIDO_EM")
#: como cada um se chama na linha da Sala (`admissao/sala_de_espera.py`)
_DA_SALA = {"ITEM_ID": "item_id", "RUN_ID": "run_id", "ORDEM": "ordem", "SOURCE_ID": "source_id",
            "UNIVERSO": "universo", "RAW_OBSERVATION_ID": "raw_observation_id",
            "RAW_SHA256": "raw_sha256", "RAW_STORAGE_PATH": "raw_storage_path",
            "DOCUMENT_ID": "raw_document_key", "URL": "raw_source_url",
            "PUBLISHED_AT": "published_at", "PUBLISHED_AT_BASIS": "published_at_basis",
            "OBSERVED_AT": "observed_at", "COLHIDO_EM": "raw_captured_at"}


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
    # ── §0 do contrato de consumo: o produtor NUNCA decide liberacao ──────────
    intrusos = sorted(set(CAMPOS_PROIBIDOS) & set(af))
    if intrusos:
        v.append("PRODUTOR_DECIDIU_LIBERACAO: %s nao e campo de uma afirmacao" % ", ".join(intrusos))
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
    ctx = af.get("CONTEXTO_MINIMO")
    if ctx and ctx.get("TRECHO") != t[ctx.get("INICIO", -1):ctx.get("FIM", -1)]:
        v.append("o CONTEXTO_MINIMO nao esta no texto onde diz estar")

    # ── §1 do contrato de consumo: identidade, EVIDENCE_SPAN e classe ─────────
    if af.get("CLAIM_ID") != af.get("ASSERTION_ID"):
        v.append("CLAIM_ID e ASSERTION_ID sao nomes do MESMO valor, e nao batem")
    span = af.get("EVIDENCE_SPAN")
    if not isinstance(span, dict):
        v.append("sem EVIDENCE_SPAN")
    elif (span.get("INICIO"), span.get("FIM"), span.get("TRECHO")) != (a, b, trecho):
        v.append("o EVIDENCE_SPAN nao e o mesmo trecho que TRECHO_LITERAL/POSICAO")
    if not isinstance(af.get("PRODUTOR_VERSAO"), dict):
        v.append("sem PRODUTOR_VERSAO: nao se sabe que codigo e que regra extrairam (INT-LAW-052)")
    for c in ("ITEM_ID", "RAW_OBSERVATION_ID", "RAW_SHA256", "SOURCE_ID"):
        if af.get(c) in (None, ""):
            v.append("sem %s: sem prova ate ao RAW nao e evidencia" % c)
    classe = (af.get("CLAIM_KIND") or {}).get("VALOR")
    if classe not in CLAIM_KINDS and classe != NAO_SEI:
        v.append("CLAIM_KIND %r fora do vocabulario fechado" % (classe,))
    for c in ("SUBJECT", "PREDICATE", "OBJECT", "VALIDITY", "MARKET_PERIOD", "STUDY_PERIOD",
              "PUBLISHED_AT", "OBSERVED_AT", "COLLECTED_AT"):
        if not isinstance(af.get(c), dict) or "VALOR" not in af[c]:
            v.append("sem o campo %s (a presenca e obrigatoria; o valor pode ser NAO SEI)" % c)

    # ── a publicacao NUNCA e o tempo do facto, nem por coincidencia de valor ──
    publicado = (af.get("PUBLISHED_AT") or {}).get("VALOR")
    if ft not in (NAO_SEI, TA.NAO_EXISTE) and str(ft) == str(publicado):
        origem = (af.get("FACT_TIME_ROLE") or {}).get("ORIGEM")
        if origem not in TA.ORIGENS or not isinstance(basis, dict):
            v.append("FACT_TIME igual a PUBLISHED_AT sem base textual propria")

    # ── COL-LAW-221: SPAN exige o nome DENTRO do trecho ───────────────────────
    # «Esta no trecho?» pergunta-se ao DONO da leitura (`boletim_do_campo`), com o mesmo
    # vocabulario e a mesma dobra que ele usou para a ler. Refazer a pergunta com um
    # casamento proprio criaria uma segunda leitura — e ela discordaria da lei: medido em
    # 883 afirmacoes de 15 577, onde a forma escrita («mosca delle olive») nao e a forma
    # normalizada («mosca dell'olivo») e um `find` ingenuo dizia que o nome nao estava la.
    for e in af.get("ENTIDADES") or []:
        if not isinstance(e, dict):
            v.append("entidade que nao e objeto")
            continue
        if e.get("ENTITY_SOURCE") not in AF.ENTITY_SOURCES:
            v.append("entidade com ENTITY_SOURCE %r fora da COL-LAW-221" % (e.get("ENTITY_SOURCE"),))
            continue
        nome = e.get("VALOR_NORMALIZADO")
        ler = BC._culturas_em if e.get("TIPO") == "CULTURA" else BC._pragas_em
        no_trecho = nome not in (None, NAO_SEI) and nome in ler(str(trecho or ""))
        ok, porque = AF.procedencia_da_entidade(e["ENTITY_SOURCE"], nome_no_trecho=no_trecho)
        if not ok:
            v.append("entidade %r: COL-LAW-221 reprovou %s (%s)" % (nome, e["ENTITY_SOURCE"], porque))
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
