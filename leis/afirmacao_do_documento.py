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

# ── COMO A CASA ESCREVE «NAO SEI» ────────────────────────────────────────────
# O dono desta lista e `motor/corrida_da_inteligencia.PALAVRAS_DE_IGNORANCIA`. Esta copiada
# por NOME para esta funcao continuar PURA (o mesmo que `boletim_do_campo` faz com o
# vocabulario da regua T1), e `tests/test_o_produtor_de_afirmacoes.py` confere que as duas
# sao iguais — se o dono acrescentar uma palavra e aqui nao, o teste reprova.
PALAVRAS_DE_IGNORANCIA = (NAO_SEI, "NAO_SEI", "UNKNOWN", "NOT_KNOWN")


def e_ignorancia(valor) -> bool:
    """«NAO SEI» continua «NAO SEI», escreva-se como se escrever."""
    if valor is None or valor == "":
        return True
    if not isinstance(valor, str):
        return False
    s = valor.strip().upper()
    return s.startswith(PALAVRAS_DE_IGNORANCIA) or s in ("?", "-", "NONE", "NULL")


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
# Num texto tirado de PDF aparece o ponto que o compositor perdeu: «… nella zona, Gli
# accumuli osservati …» (exemplo sintetico; o teste tem o dele). Sem isto, DUAS afirmacoes
# diferentes viajam num trecho so — e um trecho que mistura duas afirmacoes e uma prova
# pior, com ou sem R9.
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


# ── O BLOCO DE MENU QUE PASSA POR FRASE ──────────────────────────────────────
# Medido pelo red team D160 (§1.9): 700 trechos com 3 ou mais quebras de linha. Numa pagina
# web guardada, o menu e a lista de manchetes nao acabam em ponto nenhum — e a frase, que so
# acaba em pontuacao, linha em branco, pagina ou cabecalho, engolia o bloco inteiro e
# chamava-lhe corpo. Somadas, oito palavras curtas passam no teste das oito palavras.
# A regra: com LINHAS_DO_BLOCO linhas ou mais, a MAIORIA tem de ser frase. Linha curta
# (< PALAVRAS_MINIMAS palavras, a regra do vivo) e item de lista, nao oracao.
LINHAS_DO_BLOCO = 3


def e_bloco_de_linhas_curtas(frase: str) -> bool:
    linhas = [l for l in str(frase or "").splitlines() if l.strip()]
    if len(linhas) < LINHAS_DO_BLOCO:
        return False
    curtas = sum(1 for l in linhas if FT._palavras(l) < FT.PALAVRAS_MINIMAS)
    return curtas > len(linhas) / 2


def e_corpo(frase: str) -> bool:
    """A mesma pergunta que o vivo faz a cada linha (`fato_do_texto.corpo`): tem frase, e
    nao e rodape nem institucional. Nao se reescreve a regra: leem-se as constantes do dono.
    Mais a do bloco de linhas curtas, que o vivo nao precisava de fazer porque lia LINHA a
    LINHA e este le FRASES, que atravessam linhas."""
    s = str(frase or "").strip()
    return (FT._palavras(s) >= FT.PALAVRAS_MINIMAS and not FT.RODAPE.search(s)
            and not e_bloco_de_linhas_curtas(s))


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


#: O que o gazetteer do vivo cobre HOJE. Lido do dono dele (`leis/fato_local.cobertura`),
#: nunca copiado: o lugar viaja com a precisao E com o limite de quem o leu. Medido:
#: MUNICIPALITIES = 0 — sem a lista oficial do ISTAT, um comune que nao seja capoluogo de
#: provincia e INVISIVEL. Inventar o municipio a partir do texto seria fabricar identidade.
_COBERTURA = {}


def cobertura_do_gazetteer() -> dict:
    if not _COBERTURA:
        _COBERTURA.update(BC._ft().FL.cobertura())
    return dict(_COBERTURA)


# ── QUANTOS LUGARES O TRECHO ESCREVE (BLK-1, Intelligence owner) ─────────────
# O outro lado do bloqueador. Na frase «…in Europa … nel 2004 e in Italia nel 2012, in
# Emilia Romagna», o lugar saia «Italia» — e a Italia e do facto de 2012, nao do de 2004.
#
# Conta-se com o GAZETTEER do leitor italiano (`fato_local.GAZETTEER`), que e o vocabulario
# de lugares desta casa; nao nasce aqui uma segunda lista de toponimos. Duas diferencas
# deliberadas em relacao ao `FL.mencoes`, e as duas so sabem contar MAIS:
#
#   1. HIFEN E ESPACO SAO A MESMA COISA. O gazetteer escreve «Emilia-Romagna» e o jornal
#      escreve «Emilia Romagna». O `FL.mencoes` nao casa a segunda — medido. Para RESOLVER
#      um lugar isso falha de menos e fica invisivel; para CONTAR concorrentes falha no
#      sentido perigoso, porque um concorrente que nao se conta e uma guarda que nao dispara.
#   2. AS AREAS SUPRANACIONAIS. O gazetteer cobre a Italia de proposito (20 regioes, 85
#      provincias, 2 formas do pais) e por isso «Europa» nao esta la. Mas «rilevata in
#      Europa» E um lugar concorrente da «Italia» na mesma frase.
#
# ⚠️ A ASSIMETRIA E O QUE TORNA ISTO SEGURO: esta lista so pode fazer o lugar sair NAO SEI.
# Nunca RESOLVE um lugar, nunca escreve um FACT_LOCATION, nunca entra na PRECISAO. Um nome
# a mais aqui custa uma afirmacao mais pobre; um nome a menos custaria um lugar falso.
_AREAS_SUPRANACIONAIS = ("Europa", "Unione Europea", "Mediterraneo", "Africa", "Asia",
                         "America", "Sud America", "Nord America", "Oceania",
                         "Spagna", "Francia", "Grecia", "Germania", "Portogallo", "Turchia",
                         "Paesi Bassi", "Olanda", "Belgio", "Svizzera", "Austria",
                         "Slovenia", "Croazia", "Albania", "Romania", "Ungheria", "Cina",
                         "Giappone", "Stati Uniti", "Israele", "Egitto", "Marocco", "Tunisia")
#: ⚠️ LIMITE DECLARADO: o contador de lugares nao ve o que o gazetteer nao tem. Com
#: `MUNICIPALITIES = 0`, duas comunas concorrentes na mesma frase contam ZERO, e a guarda
#: nao dispara. Ele CONTA DE MENOS, e contar de menos e o lado em que ele falha.
LIMITE_DO_CONTADOR_DE_LUGARES = (
    "conta com o gazetteer (regioes, provincias, pais) mais as areas supranacionais "
    "declaradas; comuna que nao seja capoluogo nao e contada — MUNICIPALITIES = 0")
#: o motivo com que o lugar sai NAO SEI por haver mais de um lugar no trecho (BLK-1)
LUGARES_CONCORRENTES = "LUGARES_CONCORRENTES"
_LUGARES_RX = {}


def _rx_do_lugar(nome: str):
    """A expressao que casa ESTE nome com hifen OU espaco entre as palavras."""
    if nome not in _LUGARES_RX:
        partes = [re.escape(p) for p in re.split(r"[-\s']+", TA.FL._baixo(nome)) if p]
        _LUGARES_RX[nome] = re.compile(r"(?<![0-9a-z])%s(?![0-9a-z])"
                                       % r"[-\s']+".join(partes))
    return _LUGARES_RX[nome]


def expressoes_de_lugar(span: str) -> list:
    """Os lugares ESCRITOS neste trecho, sem se sobreporem, da esquerda para a direita.

    O nome mais longo ganha no mesmo ponto — «Emilia-Romagna» antes de «Romagna» —, que e a
    mesma regra que o `FL.mencoes` usa, e pela mesma razao: substring acidental."""
    texto = str(span or "")
    baixo = TA.FL._baixo(texto)
    if len(baixo) != len(texto):
        baixo = texto.lower()                 # ligadura tipografica: os offsets mandam
    nomes = sorted({n for n, _p in TA.FL.GAZETTEER} | set(_AREAS_SUPRANACIONAIS),
                   key=lambda n: (-len(n), n))
    achados, ocupado = [], []
    for nome in nomes:
        for m in _rx_do_lugar(nome).finditer(baixo):
            if any(m.start() < f and i < m.end() for i, f in ocupado):
                continue
            ocupado.append((m.start(), m.end()))
            achados.append({"INICIO": m.start(), "FIM": m.end(),
                            "TRECHO": texto[m.start():m.end()], "PLACE": nome})
    achados.sort(key=lambda x: x["INICIO"])
    vistos, fora = set(), []
    for a in achados:
        if a["PLACE"] in vistos:
            continue                          # o mesmo lugar nomeado duas vezes e um lugar
        vistos.add(a["PLACE"])
        fora.append(a)
    return fora


def lugares_no_trecho(span: str) -> int:
    """QUANTOS lugares distintos o trecho escreve. Viaja em cada afirmacao (contrato §5-C)."""
    return len(expressoes_de_lugar(span))


def _onde_esta_o_lugar(expressao, texto, inicio, fim, secao) -> dict | None:
    """O OFFSET do lugar no documento (red team D160 §2.6): dentro do trecho quando o lugar
    esta escrito la; no cabecalho territorial quando veio de la. Sem o achar, None — e o
    `PORQUE` diz que a forma escrita nao e a forma normalizada.

    A procura tolera espaco a mais e quebra de linha entre as palavras, porque e assim que
    o texto de um PDF as escreve — e e essa tolerancia que permite VER que a expressao
    atravessou uma linha (ver `_lugar`)."""
    alvo = str(expressao or "").strip()
    if not alvo:
        return None
    rx = re.compile(r"\s+".join(re.escape(p) for p in alvo.split()), re.I)
    for a, b in ((inicio, fim), (secao.get("INICIO", 0), inicio)):
        m = rx.search(texto[a:b])
        if m:
            achado = texto[a + m.start():a + m.end()]
            return {"INICIO": a + m.start(), "FIM": a + m.end(), "TRECHO": achado,
                    "DENTRO_DO_ALVO": (a, b) == (inicio, fim),
                    "ATRAVESSA_LINHA": bool(re.search(r"[\r\n]", achado))}
    return None


def _lugar(leitura: dict, texto: str, inicio: int, fim: int, secao: dict) -> dict:
    """O FACT_LOCATION da afirmacao, tal como a lei o devolveu — sem reescrever nada.

    C2 do contrato de consumo: o lugar viaja SEMPRE com a PRECISAO (COUNTRY · REGION ·
    PROVINCE · MUNICIPALITY · ZONA_DEFINIDA_PELA_FONTE · NOT_KNOWN) e com a cobertura de
    quem o leu, para que quem consome saiba o que a ausencia significa. E com o OFFSET,
    quando a forma escrita e a forma normalizada coincidem."""
    l_ = leitura["FACT_LOCATION"]
    valor = l_["VALOR"]
    bruto = l_.get("LOCATION_EXPRESSION_RAW")
    onde = _onde_esta_o_lugar(bruto, texto, inicio, fim, secao) if valor != UNRESOLVED else None
    porque = l_.get("PORQUE")
    # ── A EXPRESSAO QUE ATRAVESSA UMA LINHA NAO E UMA EXPRESSAO ──────────────
    # Medido pelo red team D160 (§1.5): «zone cuscinetto Il monitoraggio» — a regra de zona
    # do leitor vivo apanha ate 8 palavras a seguir a «zone», e ali elas saltaram de uma
    # linha de TITULO para a frase seguinte. Duas metades de coisas diferentes nao sao o
    # nome de um lugar. Isto NAO reescreve o leitor: recusa a leitura dele quando a prova
    # que ele aponta nao e uma frase contigua no documento.
    if onde and onde["ATRAVESSA_LINHA"]:
        valor = UNRESOLVED
        porque = ("a expressao do lugar atravessa uma quebra de linha («%s»): sao duas "
                  "metades de linhas diferentes, nao o nome de um lugar"
                  % re.sub(r"\s+", " ", onde["TRECHO"])[:80])
        onde = None
    # ── BLK-1 · dois lugares no trecho: de qual deles e o facto? ──────────────
    # A mesma razao do tempo: o produtor nao tem analisador de sintaxe e nao sabe qual lugar
    # prende qual facto. Havendo mais de um, nao escolhe. Foi exactamente aqui que a «Italia»
    # do facto de 2012 foi colada ao tempo do facto de 2004.
    escritos = expressoes_de_lugar(texto[inicio:fim])
    # ── PROD-3 · A CONTAGEM TEM DE INCLUIR O LUGAR QUE FOI EMITIDO ────────────
    # Medido pelo dono: `LUGARES_NO_TRECHO = 0` com `FACT_LOCATION = Ferrara`. O lugar veio de
    # «ferrarese» — um ADJETIVO —, e o contador procura o nome do gazetteer («Ferrara»), que
    # nao esta escrito ali. Nao houve vazamento (o G0 recusou por outra razao), mas:
    #
    #     UMA CONTAGEM DE ZERO AO LADO DE UM VALOR PRESENTE E UM ESTADO INCOERENTE,
    #     E QUEM CONSOME NAO TEM COMO SABER QUAL DOS DOIS ACREDITAR.
    #
    # O lugar EMITIDO concorre sempre — e por definicao, porque e ele que vai viajar. Some-se
    # a ele, se for o caso: isto so pode SUBIR a contagem, nunca descer, logo nao afrouxa a
    # guarda dos concorrentes. A forma escrita dele fica em EXPRESSOES_DE_LUGAR como o leitor
    # a leu, para que a diferenca «Ferrara» x «ferrarese» seja visivel em vez de escondida.
    if valor != UNRESOLVED and not any(x["PLACE"] == valor for x in escritos):
        escritos = escritos + [{"INICIO": None, "FIM": None, "PLACE": valor,
                                "TRECHO": bruto if bruto else valor,
                                "DE_ONDE": "emitido pelo leitor do lugar; a forma escrita nao "
                                           "e o nome do gazetteer (ex.: «ferrarese» -> Ferrara)"}]
    motivo = None
    if valor != UNRESOLVED and len(escritos) > 1:
        motivo = LUGARES_CONCORRENTES
        porque = ("§5-C: o trecho escreve %d lugares (%s) e o produtor nao tem como provar "
                  "de qual deles e o facto — a leitura dava «%s». Escolher seria inferir"
                  % (len(escritos), ", ".join("«%s»" % x["TRECHO"] for x in escritos), valor))
        valor = UNRESOLVED
        onde = None
    return {"VALOR": NAO_SEI if valor == UNRESOLVED else valor,
            "MOTIVO": motivo,
            "LUGARES_NO_TRECHO": len(escritos),
            "EXPRESSOES_DE_LUGAR": [x["TRECHO"] for x in escritos],
            "LIMITE_DA_CONTAGEM": LIMITE_DO_CONTADOR_DE_LUGARES,
            "LOCATION_SOURCE": l_["LOCATION_SOURCE"],
            "PRECISAO": l_.get("PRECISAO") or "NOT_KNOWN",
            "TRECHO": bruto,
            "ONDE": onde,
            "PORQUE_SEM_OFFSET": None if onde or valor == UNRESOLVED else
                                 ("a forma ESCRITA nao e a forma normalizada (ex.: «barese» -> Bari); "
                                  "o trecho que a prova esta em PROVA"),
            "PROVA": l_.get("PROVA"),
            "PORQUE": porque,
            "PONTO_NO_MAPA": bool(l_.get("PONTO_NO_MAPA")) and valor != UNRESOLVED,
            "COBERTURA_DO_GAZETTEER": cobertura_do_gazetteer()}


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

    Duas regras, e so estas:

    1. Quando o trecho traz a marca de DUAS classes, escolher uma seria inferir — sai
       NAO SEI, com as duas marcas escritas. E a mesma regra da D112 para duas pragas.
    2. ⚠️ ALERTA_EVENTO NAO E O QUE SOBRA. Foi assim na 1.a versao, e o red team D160 (§2.3)
       mediu o estrago: 122 ALERTA_EVENTO, dos quais 9 eram eventos futuros, 3 eram janelas
       de licenca e outros eram texto historico («nel 2003»). A classe manda a Intelligence
       exigir FACT_TIME com ano e inicio <= captura, e uma classe dada por omissao empurra
       a decisao dela por dentro. Agora ALERTA_EVENTO exige TRES coisas ao mesmo tempo:
       o papel ACONTECIMENTO, o texto a prender a data a um acontecimento (a pergunta e do
       leitor vivo, `_relativa_presa_ao_campo`), e o ano escrito. Faltando uma, NAO SEI."""
    marcas = []
    if TA._MARCA_DE_ATO.search(span) or TA._MARCA_DE_VALIDADE.search(span):
        marcas.append("REGULATORIO")
    # ── PROD-2 · a LOJA e mercado, e a casa ja o lia assim ────────────────────
    # O dono (contrato §5-C, «Classe»): «Uma leitura ja estabelecida na casa (por exemplo,
    # fato_do_texto.py "punti vendita" = MERCADO) prevalece sobre a omissao.»
    # Medido por ele num item de um portal de fruta: uma visita a pontos de venda saia
    # ALERTA_EVENTO. O `_RE_LOJA` do leitor vivo — «punti (di) vendita», «grande
    # distribuzione», «supermercati», «ipermercati» — ja decide MERCADO no lugar do fato
    # desde o ensaio IT-T10-018. Duas partes da casa a ler a mesma frase e a discordar e o
    # defeito; a marca da classe passa a ser a MESMA que o lugar usa, lida de la.
    if _RE_PRECO.search(span) or TA._MARCA_DE_MERCADO.search(span) or FT._RE_LOJA.search(span):
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
    faltas = []
    if tempo.get("PAPEL") != TA.ACONTECIMENTO:
        faltas.append("o papel da data e %s, nao ACONTECIMENTO" % tempo.get("PAPEL"))
    if not FT._relativa_presa_ao_campo(span):
        faltas.append("o texto nao prende a data a um acontecimento (nenhuma ancora do leitor vivo)")
    # PROD-3: pergunta-se tambem ao VALOR, e nao so a PRECISAO. Um mes sozinho («marzo») nao
    # acendia o sinal `SEM_ANO`, e a classe saia ALERTA_EVENTO contra a regra escrita acima.
    if (str(tempo.get("PRECISAO") or "").endswith("SEM_ANO") or tempo.get("ANO") == NAO_SEI
            or TA.falta_o_ano(tempo.get("VALOR"))):
        faltas.append("a data nao escreve o ano")
    if faltas:
        return {"VALOR": NAO_SEI, "MARCAS": [],
                "PORQUE": "sem marca de classe, e ALERTA_EVENTO nao e o que sobra: " + "; ".join(faltas)}
    return {"VALOR": "ALERTA_EVENTO", "MARCAS": [],
            "PORQUE": "papel ACONTECIMENTO, o texto prende a data a um acontecimento, e o ano esta escrito"}


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
            tempo = TA.extrair_tempo(t, {"INICIO": a, "FIM": b, "SECAO": s,
                                         "PUBLICACAO": publicacao, "CAPTURA": prov.get("COLHIDO_EM")})
            precisa = []
            for nome, r in (("cultura", leitura["CULTURA"]), ("praga", leitura["PRAGAS"])):
                if r["ENTITY_SOURCE"] not in (BC.SPAN, BC.UNKNOWN):
                    precisa.append("a %s veio de %s, fora do trecho" % (nome, r["ENTITY_SOURCE"]))
            if tempo["ORIGEM"] in TA.ORIGENS_COM_BASIS_FORA_DO_TRECHO:
                precisa.append("a data veio de %s: o BASIS esta fora do trecho" % tempo["ORIGEM"])
            # Tudo o que a afirmacao guarda e LITERAL do documento. O leitor temporal
            # trabalha sobre o texto limpo pela D19 (mesmo comprimento, logo mesmos
            # offsets); o TRECHO que viaja e o do ORIGINAL, que e o que a conferencia confere.
            _literal(tempo.get("BASIS"), original)
            lugar = _lugar(leitura, original, a, b, s)
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
                # ── §5-C · a CONTAGEM viaja, para a Intelligence poder defender-se sem
                # ler texto: ela recusa se a contagem for > 1 e o valor nao for NAO SEI, e
                # recusa tambem se o campo faltar. Por isso ele esta SEMPRE presente.
                "TEMPOS_NO_TRECHO": tempo.get("TEMPOS_NO_TRECHO", 0),
                "LUGARES_NO_TRECHO": lugar["LUGARES_NO_TRECHO"],
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
                                   "PRECISAO": tempo["PRECISAO"],
                                   "ANO": tempo.get("ANO") or (NAO_SEI if str(tempo["PRECISAO"]).endswith("SEM_ANO") else None),
                                   "PORQUE": tempo["PORQUE"],
                                   "COMPOSICAO": tempo.get("COMPOSICAO"),
                                   "LEITOR": tempo["LEITOR"],
                                   "PUBLICACAO_PROVADA": tempo["PUBLICACAO_PROVADA"]},
                "VALIDITY": _periodo_por_papel(tempo, TA.VALIDADE),
                "MARKET_PERIOD": _periodo_por_papel(tempo, TA.MARKET_PERIOD),
                "STUDY_PERIOD": {"VALOR": NAO_SEI, "BASIS": None,
                                 "PORQUE": "o produtor minimo nao le identidade de estudo no trecho; "
                                           "quem a le e leis/estudo_chaves.py, ao nivel do item"},
                "ACT_TIME": _periodo_por_papel(tempo, TA.ATO),
                "FACT_LOCATION": lugar,
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
    origem = (af.get("FACT_TIME_ROLE") or {}).get("ORIGEM")
    if ft not in (NAO_SEI, TA.NAO_EXISTE):
        if not isinstance(basis, dict):
            v.append("FACT_TIME com valor e sem BASIS")
        elif basis.get("TRECHO") != t[basis.get("INICIO", -1):basis.get("FIM", -1)]:
            v.append("o BASIS do FACT_TIME nao esta no texto onde diz estar")
        elif origem not in TA.ORIGENS:
            v.append("FACT_TIME com valor e ORIGEM %r fora do vocabulario" % (origem,))
        # C1 do contrato de consumo: LITERAL promete que a prova esta DENTRO do trecho.
        # Uma origem que va buscar o valor ao cabecalho tem de se chamar pelo nome dela.
        elif origem == TA.LITERAL and not (a <= basis["INICIO"] and basis["FIM"] <= b):
            v.append("ORIGEM = LITERAL com o BASIS em [%d:%d], fora do trecho [%d:%d]: "
                     "LITERAL promete a prova dentro do trecho"
                     % (basis["INICIO"], basis["FIM"], a, b))
    loc = af.get("FACT_LOCATION") or {}
    if loc.get("VALOR") != NAO_SEI and loc.get("LOCATION_SOURCE") not in BC.LOCATION_SOURCES:
        v.append("FACT_LOCATION com valor e LOCATION_SOURCE %r fora da COL-LAW-032"
                 % (loc.get("LOCATION_SOURCE"),))
    # C2 do contrato de consumo: o lugar nunca viaja sem a precisao e sem a cobertura de
    # quem o leu — quem consome tem de saber o que a ausencia de um municipio significa.
    if not loc.get("PRECISAO"):
        v.append("FACT_LOCATION sem PRECISAO")
    if not isinstance(loc.get("COBERTURA_DO_GAZETTEER"), dict):
        v.append("FACT_LOCATION sem a COBERTURA_DO_GAZETTEER de quem o leu")
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
    # §3 do contrato de consumo: «NAO SEI em identidade/lineage → RECUSA. Nao ha
    # rebaixamento: sem prova ate ao RAW, nao e evidencia.» A 1.a versao so recusava o vazio,
    # e uma linha da Sala sem `raw_sha256` passava com os quatro campos a dizer «NAO SEI»
    # (medido pelo red team D160 §1.6-H: 0 casos na Sala da R9, mas a porta estava aberta).
    for c in ("ITEM_ID", "RAW_OBSERVATION_ID", "RAW_SHA256", "SOURCE_ID"):
        if e_ignorancia(af.get(c)):
            v.append("%s = %r: NAO SEI na identidade RECUSA, nao rebaixa — sem prova ate ao "
                     "RAW nao e evidencia" % (c, af.get(c)))
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
