#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O TEMPO DE UMA AFIRMACAO — a INTERFACE do leitor temporal, com o PAPEL da data (D158).

    extrair_tempo(texto, alvo) -> {"PAPEL", "VALOR", "ORIGEM", "BASIS", ...}

O QUE ISTO E, E O QUE NAO E
---------------------------
NAO e um segundo leitor temporal. Quem le expressao de tempo em italiano continua a ser o
leitor do vivo: `leis/fato_do_texto.py` (que por sua vez le `leis/fato_local.py`). Este
ficheiro e a JANELA por onde o produtor de afirmacoes lhe pergunta, para que o componente
tipado da L5 (`leis_proposta/tempo_tipado.py`, congelado) possa entrar no lugar dele sem
mexer em quem pergunta. Por isso ha UMA funcao publica, `extrair_tempo`, e o leitor vivo
esta atras dela numa constante, `LEITOR_VIVO`.

O QUE ESTA INTERFACE ACRESCENTA (e e a unica parte nova, por REGRA)
-------------------------------------------------------------------
1. O PAPEL da data. O vivo tem UM campo (`fact_time`) e um `kind` (CAMPO/EVENTO). O dono
   (D147) exige dizer DE QUE e a data. Os papeis estao em `PAPEIS`, e a regra que escolhe
   cada um esta escrita ao lado dele.
2. O PERIODO IMPRESSO NUM CABECALHO em duas formas que o vivo nao le:
   · a numerica — «Dal 01-02-2020 al 07-02-2020» (o vivo so le o mes por extenso,
     `fato_do_texto._RE_PERIODO_DO_CABECALHO`);
   · a de LETRAS DOBRADAS, que o extrator de PDF produz quando o texto esta a negrito
     («SSEEZZIIOONNEE» = «SEZIONE»). Ver `desdobrar`.
   Nenhuma destas duas e um leitor de italiano: sao a mesma data, escrita de outra maneira.
3. A COMPOSICAO do D147/D149/D153: quando a afirmacao nao escreve a data mas o CABECALHO da
   seccao dela escreve, a data pode ser composta — sob as CINCO CONDICOES do dono, todas
   verificadas por programa em `_compor_do_cabecalho`, e sempre com OS DOIS TRECHOS e a
   ORIGEM registados. Na duvida, NAO SEI.

AS LEIS QUE GOVERNAM ISTO
-------------------------
D63   relativa («la settimana scorsa») so com publicacao PROVADA, e a conta e a do vivo.
D147  o ano/periodo do cabecalho so governa a afirmacao com as cinco condicoes cumpridas;
      o periodo que a EDICAO cobre nao e validade nem facto: e PERIODO_DA_EDICAO.
D149  uma relativa de semana ancora-se no periodo IMPRESSO do proprio boletim, quando ele
      existe: o impresso e mais forte do que a conta a partir da publicacao.
D153  compor so com evidencia de que o cabecalho governa a afirmacao, sem concorrente, com
      os dois trechos e a origem registados. Na duvida, NAO SEI.
COL-LAW-031/032/201  a publicacao NUNCA e o tempo do facto. Aqui isso e mecanico: PUBLICACAO
      e um PAPEL, e um papel que nao seja ACONTECIMENTO nunca sai como tempo do facto.

Funcao PURA: sem rede, sem banco, sem ficheiros.

    python3 leis/tempo_da_afirmacao.py    # imprime o contrato
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date

_AQUI = os.path.dirname(os.path.abspath(__file__))
if _AQUI not in sys.path:
    sys.path.insert(0, _AQUI)

import fato_do_texto as FT      # noqa: E402  o leitor do VIVO — nao se reescreve aqui
import fato_local as FL         # noqa: E402  quem le o italiano

#: O leitor vivo, atras da interface. Trocar a L5 por aqui, num sitio so.
LEITOR_VIVO = "leis/fato_do_texto.py::campos_do_fato (+ leis/fato_local.py)"

NAO_SEI = FT.NAO_SEI                  # "NAO SEI" — ha data no texto, mas nao se sabe se e desta afirmacao
NAO_EXISTE = "NAO_EXISTE"             # o texto da afirmacao e da seccao dela nao escreve tempo nenhum

# ── OS PAPEIS DA DATA (D147) ─────────────────────────────────────────────────
# De QUE e a data. O vivo nao responde a esta pergunta; o dono exige-a. So
# ACONTECIMENTO e tempo do FACTO — os outros seis existem para poderem ser
# DITOS e, ao serem ditos, ficarem de fora do FACT_TIME.
ACONTECIMENTO = "ACONTECIMENTO"          # aconteceu no campo / no mundo, e o texto prende a data a isso
VALIDADE = "VALIDADE"                    # ate quando uma regra, derroga ou autorizacao vale
PUBLICACAO = "PUBLICACAO"                # o carimbo de quem publicou. NUNCA e o tempo do facto
PREVISAO = "PREVISAO"                    # o que ainda nao aconteceu
PERIODO_DA_EDICAO = "PERIODO_DA_EDICAO"  # de que dias esta EDICAO fala (D147: nao e validade)
ATO = "ATO"                              # a data do decreto / determina / ordinanza
MARKET_PERIOD = "MARKET_PERIOD"          # safra, campanha, semana de rilevacao de preco
PAPEIS = (ACONTECIMENTO, VALIDADE, PUBLICACAO, PREVISAO, PERIODO_DA_EDICAO, ATO, MARKET_PERIOD)
#: O unico papel que pode virar FACT_TIME. Esta lista e a lei, e nao tem excecao.
PAPEL_QUE_E_FACTO = (ACONTECIMENTO,)

# ── DE ONDE VEIO O VALOR ─────────────────────────────────────────────────────
LITERAL = "LITERAL"              # escrito dentro do proprio trecho da afirmacao
CABECALHO = "CABECALHO"          # composto do cabecalho da seccao (D147: cinco condicoes)
RELATIVO_D63 = "RELATIVO_D63"    # contado pelo vivo a partir de publicacao PROVADA
ORIGENS = (LITERAL, CABECALHO, RELATIVO_D63)

# ── o vocabulario que MARCA o papel, quando o papel esta escrito ─────────────
# Palavras administrativas e comerciais do italiano. Nao sao saber agronomico nem
# taxonomia: sao a palavra com que a propria fonte diz de que e a data. Uma data
# sem nenhuma destas marcas nao ganha papel por elas — cai na regra do tempo.
_MARCA_DE_VALIDADE = re.compile(
    r"(?<![a-zà-ÿ])(?:validit|valid[oa]\s+(?:dal|fino|da|al)|in\s+vigore|vigenza|scadenz|"
    r"fino\s+al\s+termine|proroga\s+(?:al|fino))", re.I)
_MARCA_DE_ATO = re.compile(
    r"(?<![a-zà-ÿ])(?:decreto|determina(?:zione)?|ordinanza|delibera(?:zione)?|d\.?\s?m\.?\s?n|"
    r"d\.?g\.?r\.?|circolare\s+n|legge\s+n|regolamento\s+\(?(?:ue|ce)\)?)", re.I)
_MARCA_DE_MERCADO = re.compile(
    r"(?<![a-zà-ÿ])(?:rilevazion|listin|quotazion|campagna\s+(?:commerciale|\d)|annata\s+agraria|"
    r"settimana\s+di\s+rilevazione|borsa\s+merci|mercuriale)", re.I)
_MARCA_DE_PUBLICACAO = re.compile(
    r"(?<![a-zà-ÿ])(?:pubblicat|aggiornat[oa]\s+al|data\s+di\s+pubblicazione|edizione\s+del|"
    r"del\s+giorno\s+di\s+pubblicazione)", re.I)

# ── o cabecalho: linha curta, sem ponto final, que ABRE um bloco ─────────────
#: quantas palavras uma linha pode ter e ainda ser cabecalho (a mesma ordem de grandeza
#: que `boletim_do_campo.PALAVRAS_DO_CABECALHO_TERRITORIAL`, que conta so as palavras)
PALAVRAS_DO_CABECALHO = 12


# ════════════════════════════════════════════════════════════════════════════
# AS LETRAS DOBRADAS DO PDF
# ════════════════════════════════════════════════════════════════════════════
# Um extrator de PDF que le texto a negrito desenhado duas vezes devolve cada letra
# duplicada: «SSEEZZIIOONNEE DDaall 0011--0022--22002200» = «SEZIONE Dal 01-02-2020».
# Nao e uma palavra italiana nem uma abreviatura: e a MESMA linha, escrita com cada
# caractere repetido. Desfaz-se por REGRA, e a regra e exigente de proposito — uma
# palavra normal quase nunca passa nela:
#   · a linha parte-se por espacos;
#   · CADA pedaco tem de ter comprimento PAR e ser pares de caracteres iguais;
#   · tem de haver pelo menos DOIS pedacos, e pelo menos um com 4 caracteres ou mais;
#   · a linha desdobrada tem de ficar com pelo menos MINIMO_DESDOBRADO caracteres.
# Sem isto, «aa bb» viraria «a b». Com isto, uma linha dobrada desdobra e «La settimana
# scorsa e iniziata» nao (o primeiro pedaco, «La», tem L != a).
MINIMO_DESDOBRADO = 6


def desdobrar(linha: str) -> str | None:
    """A linha com as letras dobradas desfeitas, ou None se ela nao esta dobrada."""
    pedacos = str(linha or "").split()
    if len(pedacos) < 2:
        return None
    fora, longos = [], 0
    for p in pedacos:
        if len(p) % 2 or not p:
            return None
        if any(p[i] != p[i + 1] for i in range(0, len(p), 2)):
            return None
        if len(p) >= 4:
            longos += 1
        fora.append(p[::2])
    if not longos:
        return None
    saida = " ".join(fora)
    return saida if len(saida) >= MINIMO_DESDOBRADO else None


def como_se_le(linha: str) -> str:
    """A linha como um humano a le: desdobrada quando estava dobrada, igual quando nao."""
    return desdobrar(linha) or str(linha or "")


# ════════════════════════════════════════════════════════════════════════════
# O PERIODO IMPRESSO NUM CABECALHO
# ════════════════════════════════════════════════════════════════════════════
# Duas formas. A do vivo (mes por extenso) le-se com a regra do vivo, importada —
# nao copiada. A numerica e a parte nova.
_D, _A = r"\d{1,2}", r"\d{4}"
_RE_PERIODO_NUMERICO = re.compile(
    r"(?:dal(?:l['’])?\s+)?(%s)[-./](%s)[-./](%s)\s*(?:al(?:l['’])?|[-–—])\s*(%s)[-./](%s)[-./](%s)"
    % (_D, _D, _A, _D, _D, _A), re.I)
#: a forma do vivo, lida do dono dela
_RE_PERIODO_DO_VIVO = FT._RE_PERIODO_DO_CABECALHO


def _dia(a, m, d) -> date | None:
    try:
        return date(int(a), int(m), int(d))
    except ValueError:
        return None


def periodos_escritos(linha: str) -> list:
    """TODOS os periodos escritos NESTA linha. Sao todos porque DOIS periodos no mesmo
    cabecalho sao a condicao (1) da D147 a falhar: um cabecalho com duas datas nao governa
    afirmacao nenhuma, e para isso e preciso ve-las as duas.

    Cada um: {"INICIO_DIA", "FIM_DIA", "VALOR", "LIDO_COMO", "FORMA"} — as duas datas, o
    valor normalizado «AAAA-MM-DD/AAAA-MM-DD» e a linha como um humano a le."""
    lido = como_se_le(linha).strip()
    fora = []
    for m in _RE_PERIODO_NUMERICO.finditer(lido):
        a, b = _dia(m.group(3), m.group(2), m.group(1)), _dia(m.group(6), m.group(5), m.group(4))
        if a and b and a <= b:
            fora.append({"INICIO_DIA": a, "FIM_DIA": b, "VALOR": "%s/%s" % (a.isoformat(), b.isoformat()),
                         "LIDO_COMO": lido, "FORMA": "NUMERICA"})
    if fora:
        return fora
    m = _RE_PERIODO_DO_VIVO.match(FL._baixo(lido))
    if m:
        d1, d2, mes, ano = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4))
        a, b = _dia(ano, FL.MES_NUM[mes], d1), _dia(ano, FL.MES_NUM[mes], d2)
        if a and b and a <= b:
            fora.append({"INICIO_DIA": a, "FIM_DIA": b, "VALOR": "%s/%s" % (a.isoformat(), b.isoformat()),
                         "LIDO_COMO": lido, "FORMA": "MES_POR_EXTENSO"})
    return fora


def periodo_escrito(linha: str) -> dict | None:
    """O PRIMEIRO periodo escrito nesta linha, ou None."""
    ps = periodos_escritos(linha)
    return ps[0] if ps else None


#: que parte das letras de um cabecalho vem em maiuscula
MAIUSCULAS_DO_CABECALHO = 0.6


def _linha_que_e_so_o_periodo(lido: str) -> bool:
    """A linha INTEIRA e o periodo — a regra do VIVO, lida do dono dela
    (`fato_do_texto._RE_PERIODO_DO_CABECALHO` e ancorada: «a linha inteira tem de ser o
    periodo»). «16 - 22 settembre 2026» nao tem uma maiuscula, e mesmo assim e cabecalho."""
    return bool(_RE_PERIODO_DO_VIVO.match(FL._baixo(lido)))


def e_cabecalho(linha: str) -> bool:
    """A linha ABRE um bloco? Curta, sem terminar em ponto, e nao e uma frase corrida."""
    lido = como_se_le(linha).strip()
    if not lido or lido.endswith("."):
        return False
    palavras = re.findall(r"[A-Za-zÀ-ÿ']+", lido)
    if len(palavras) > PALAVRAS_DO_CABECALHO:
        return False
    letras = [c for c in lido if c.isalpha()]
    maiusculas = bool(letras) and sum(c.isupper() for c in letras) >= MAIUSCULAS_DO_CABECALHO * len(letras)
    return bool(desdobrar(linha)) or maiusculas or _linha_que_e_so_o_periodo(lido)


# ════════════════════════════════════════════════════════════════════════════
# O PAPEL
# ════════════════════════════════════════════════════════════════════════════
def papel_do_periodo(trecho: str, inicio_dia, fim_dia, pub, *, no_cabecalho_do_documento=False) -> tuple:
    """(PAPEL, PORQUE) de um periodo escrito em `trecho`.

    A ordem e a lei: a MARCA escrita ganha ao calendario (a fonte diz de que e a data);
    sem marca, o calendario decide contra a publicacao PROVADA (D63)."""
    if _MARCA_DE_VALIDADE.search(trecho):
        return VALIDADE, "o texto escreve a marca de validade"
    if _MARCA_DE_ATO.search(trecho):
        return ATO, "o texto escreve a marca de ato administrativo"
    if _MARCA_DE_MERCADO.search(trecho):
        return MARKET_PERIOD, "o texto escreve a marca de periodo de mercado"
    if _MARCA_DE_PUBLICACAO.search(trecho):
        return PUBLICACAO, "o texto escreve a marca de publicacao"
    if no_cabecalho_do_documento:
        return PERIODO_DA_EDICAO, "periodo no cabecalho do proprio boletim: diz de que dias a EDICAO fala"
    if pub is None:
        return NAO_SEI, "sem publicacao provada nao se sabe se o periodo ja passou (D63)"
    if inicio_dia > pub:
        return PREVISAO, "o periodo comeca depois da publicacao provada: ainda nao aconteceu"
    if fim_dia >= pub:
        return NAO_SEI, ("o periodo atravessa o dia da publicacao: parte dele ainda nao aconteceu "
                         "e o texto nao diz de que e a data")
    return ACONTECIMENTO, "o periodo inteiro e anterior a publicacao provada"


# ════════════════════════════════════════════════════════════════════════════
# A INTERFACE
# ════════════════════════════════════════════════════════════════════════════
def _precisao_do_periodo(p: dict) -> str:
    """A precisao de um periodo IMPRESSO: uma semana ou menos e WEEK; mais do que isso,
    APPROXIMATE. Nunca «+CALCULADA» — o valor foi lido, nao contado."""
    return "WEEK" if (p["FIM_DIA"] - p["INICIO_DIA"]).days <= 6 else "APPROXIMATE"


def _basis(texto, trecho, dentro_de=None):
    """{'TRECHO', 'INICIO', 'FIM'} — onde o trecho esta no documento. Sem o achar, NAO SEI."""
    if not trecho:
        return None
    alvo = re.sub(r"\s+", " ", str(trecho)).strip()
    if not alvo:
        return None
    rx = re.compile(r"\s+".join(re.escape(p) for p in alvo.split()))
    inicio, fim = (dentro_de or (0, len(texto)))
    m = rx.search(texto, inicio, fim) or rx.search(texto)
    if not m:
        return None
    return {"TRECHO": texto[m.start():m.end()], "INICIO": m.start(), "FIM": m.end()}


def _do_vivo(span: str, published_at, published_at_basis) -> dict:
    """O que o LEITOR VIVO diz sobre ESTE trecho, sozinho. Nada e reescrito aqui."""
    return FT.campos_do_fato(span, published_at, published_at_basis)


def _papel_do_vivo(c: dict, span: str, pub) -> tuple:
    """(PAPEL, PORQUE) para o tempo que o vivo devolveu sobre o trecho."""
    valor = c["fact_time"]
    marca = papel_do_periodo(span, None, None, None)[0]
    if marca in (VALIDADE, ATO, MARKET_PERIOD, PUBLICACAO):
        return marca, "o proprio trecho escreve a marca do papel"
    if FT._RE_FUTURO.search(span) and FT._futuro_perto(span, valor):
        return PREVISAO, "o trecho marca futuro junto da data"
    ini = _primeiro_dia(valor)
    if pub is not None and ini is not None and ini > pub:
        return PREVISAO, "a data e posterior a publicacao provada"
    return ACONTECIMENTO, "o leitor vivo prendeu a data a um acontecimento (kind %s)" % c["fact_time_kind"]


_RE_DIA_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def _primeiro_dia(valor) -> date | None:
    m = _RE_DIA_ISO.search(str(valor or ""))
    return _dia(m.group(1), m.group(2), m.group(3)) if m else None


def _ha_tempo_escrito(texto: str) -> bool:
    """Existe ALGUMA expressao de tempo no texto? Pergunta-se ao vivo, com o vocabulario dele."""
    baixo = FL._baixo(texto)
    if re.search(r"\b(?:19|20)\d{2}\b", baixo) or re.search(r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b", baixo):
        return True
    if re.search(r"(?<![a-z])(?:%s)(?![a-z])" % "|".join(FL.MESES), baixo):
        return True
    return bool(FT._RE_RELATIVOS.search(baixo))


def fala_de_acontecimento(span: str) -> str | None:
    """None quando o trecho fala de alguma coisa que aconteceu; o PORQUE quando nao fala.

    As tres recusas sao as do LEITOR VIVO, lidas do dono delas — nao ha lista nova aqui:
    conselho (`_RE_RECOMENDACAO`), frase institucional (`_RE_INSTITUCIONAL`) e futuro
    (`_RE_FUTURO`). Uma seccao com o periodo da semana passada nao empresta essa semana a
    uma recomendacao nem a uma previsao."""
    if FT._RE_RECOMENDACAO.search(span):
        return "o trecho e conselho / recomendacao: nao e o que aconteceu"
    if FT._RE_INSTITUCIONAL.search(span):
        return "o trecho e frase institucional: nao e facto do campo"
    if FT._RE_FUTURO.search(span):
        return "o trecho marca futuro: o que ainda nao aconteceu nao herda a data da seccao"
    return None


def _compor_do_cabecalho(texto, alvo, secao, periodos, pub, span) -> dict:
    """D147/D153 · as CINCO CONDICOES para o cabecalho governar a afirmacao.

    (1) ha UM periodo no cabecalho da seccao — nao dois;
    (2) o periodo esta na MESMA seccao que a afirmacao, e ANTES dela;
    (3) nao ha periodo concorrente para a mesma afirmacao (o trecho nao escreve outro);
    (4) o papel do periodo e ACONTECIMENTO (um periodo de edicao, de validade, de ato ou de
        previsao nunca vira data de facto) E o trecho fala de alguma coisa que aconteceu —
        conselho, frase institucional e futuro nao herdam a data de uma seccao passada;
    (5) OS DOIS TRECHOS e a ORIGEM ficam registados.
    Faltando uma, NAO SEI — com o porque."""
    faltas = []
    if len(periodos) != 1:
        faltas.append("o cabecalho da seccao escreve %d periodos: ha ano/periodo concorrente" % len(periodos))
        return {"CONDICOES": faltas}
    p = periodos[0]
    if not (secao["INICIO"] <= p["BASIS"]["INICIO"] and p["BASIS"]["FIM"] <= alvo["INICIO"]):
        faltas.append("o cabecalho nao esta na mesma seccao, antes da afirmacao")
    if _ha_tempo_escrito(span):
        faltas.append("o proprio trecho escreve tempo: ha concorrente para a mesma afirmacao")
    papel, porque = p["PAPEL"], p["PORQUE"]
    if papel != ACONTECIMENTO:
        faltas.append("o periodo do cabecalho tem papel %s (%s): nao e data de facto" % (papel, porque))
    conselho = fala_de_acontecimento(span)
    if conselho:
        faltas.append(conselho)
    if faltas:
        return {"CONDICOES": faltas}
    return {"CONDICOES": [], "PERIODO": p}


def periodos_do_cabecalho(texto: str, inicio: int, fim: int, pub, *, cabecalho_do_documento=(0, 0)) -> list:
    """Os periodos escritos em LINHA DE CABECALHO dentro de texto[inicio:fim], com papel e basis."""
    fora, pos = [], 0
    for linha in str(texto or "").splitlines(keepends=True):
        a, b = pos, pos + len(linha)
        pos = b
        if b <= inicio or a >= fim:
            continue
        crua = linha.rstrip("\r\n")
        if not e_cabecalho(crua):
            continue
        no_doc = cabecalho_do_documento[0] <= a < cabecalho_do_documento[1]
        for p in periodos_escritos(crua):
            papel, porque = papel_do_periodo(p["LIDO_COMO"], p["INICIO_DIA"], p["FIM_DIA"], pub,
                                             no_cabecalho_do_documento=no_doc)
            fora.append(dict(p, PAPEL=papel, PORQUE=porque, ORIGEM=LITERAL,
                             BASIS={"TRECHO": crua.strip(),
                                    "INICIO": a + (len(crua) - len(crua.lstrip())),
                                    "FIM": a + len(crua.rstrip())}))
    return fora


def cabecalho_do_documento(texto: str) -> tuple:
    """(inicio, fim) das primeiras linhas onde um boletim se APRESENTA — a regra do vivo,
    lida do dono dela (`fato_do_texto.LINHAS_DO_CABECALHO` e `_RE_E_BOLETIM`).

    A janela FECHA no primeiro dos tres: a quebra de pagina, a primeira linha de corpo
    (a regra do vivo: `PALAVRAS_MINIMAS` palavras) ou as `LINHAS_DO_CABECALHO` linhas.
    Sem o fecho, um documento curto punha o cabecalho de uma SECCAO dentro do cabecalho do
    DOCUMENTO, e o periodo da seccao passava por periodo da edicao — medido.

    Fora de um boletim devolve (0, 0): ai nenhum periodo e «da edicao»."""
    pos, fim, vistas, e_boletim = 0, 0, 0, False
    for linha in str(texto or "").splitlines(keepends=True):
        crua = linha.rstrip("\r\n")
        if "\f" in crua:
            break
        pos += len(linha)
        if not crua.strip():
            continue
        if FT._palavras(crua) >= FT.PALAVRAS_MINIMAS:
            break
        vistas += 1
        if FT._RE_E_BOLETIM.search(como_se_le(crua)):
            e_boletim = True
        fim = pos
        if vistas >= FT.LINHAS_DO_CABECALHO:
            break
    return (0, fim) if e_boletim else (0, 0)


def extrair_tempo(texto: str, alvo: dict) -> dict:
    """O tempo DESTA afirmacao: papel, valor, origem e a prova (trecho + offset).

    `alvo`:
        INICIO, FIM    o trecho da afirmacao, em `texto`
        SECAO          {"INICIO", "FIM"} — o bloco que governa o trecho (opcional)
        PUBLICACAO     {"VALOR", "BASE"} — o published_at e a base dele (opcional)

    O valor sai em VALOR; NAO SEI quando ha tempo escrito mas nao se prova que e desta
    afirmacao; NAO_EXISTE quando nem o trecho nem a seccao escrevem tempo nenhum."""
    ini, fim = int(alvo["INICIO"]), int(alvo["FIM"])
    span = texto[ini:fim]
    secao = alvo.get("SECAO") or {"INICIO": 0, "FIM": len(texto)}
    publicacao = alvo.get("PUBLICACAO") or {}
    pub = FT.publicacao_provada(publicacao.get("VALOR"), publicacao.get("BASE"))
    base = {"LEITOR": LEITOR_VIVO, "PUBLICACAO_PROVADA": pub.isoformat() if pub else None,
            "LEI": "D63 · D147 · D149 · D153; so ACONTECIMENTO e tempo do facto"}

    cab_doc = cabecalho_do_documento(texto)
    periodos = periodos_do_cabecalho(texto, secao["INICIO"], ini, pub, cabecalho_do_documento=cab_doc)

    # ── 1 · o que o LEITOR VIVO le no proprio trecho ───────────────────────
    c = _do_vivo(span, publicacao.get("VALOR"), publicacao.get("BASE"))
    if c["fact_time"] != NAO_SEI:
        papel, porque = _papel_do_vivo(c, span, pub)
        calculada = c["fact_time_calculo"] == FT.RELATIVA
        origem = RELATIVO_D63 if calculada else LITERAL
        trecho = c["fact_time_evidencia"] if calculada else _trecho_do_basis(c["fact_time_basis"])
        basis = _basis(texto, trecho, (ini, fim)) or _basis(texto, span, (ini, fim))
        # ── D149 · a relativa ancora-se no periodo IMPRESSO, quando ele existe ──
        impressos = [p for p in periodos if p["PAPEL"] == ACONTECIMENTO]
        if calculada and len(impressos) == 1:
            p = impressos[0]
            if p["VALOR"] == c["fact_time"]:
                return dict(base, PAPEL=papel, VALOR=p["VALOR"], ORIGEM=LITERAL, BASIS=p["BASIS"],
                            PRECISAO=_precisao_do_periodo(p),
                            PORQUE="D149: a relativa «%s» bate com o periodo impresso do cabecalho, e o "
                                   "impresso e a prova" % c["fact_time_expressao"],
                            COMPOSICAO={"RELATIVA": c["fact_time_expressao"], "CONTA_DO_VIVO": c["fact_time"],
                                        "IMPRESSO": p["VALOR"], "TRECHO_DO_CABECALHO": p["BASIS"]["TRECHO"],
                                        "TRECHO_DO_ALVO": span})
            return dict(base, PAPEL=NAO_SEI, VALOR=NAO_SEI, ORIGEM=None, BASIS=basis,
                        PRECISAO="NOT_KNOWN",
                        PORQUE="D149/D153: a conta a partir da publicacao da %s e o periodo impresso do "
                               "cabecalho da %s — ha concorrente para a mesma afirmacao"
                               % (c["fact_time"], p["VALOR"]),
                        COMPOSICAO={"RELATIVA": c["fact_time_expressao"], "CONTA_DO_VIVO": c["fact_time"],
                                    "IMPRESSO": p["VALOR"], "TRECHO_DO_CABECALHO": p["BASIS"]["TRECHO"]})
        return dict(base, PAPEL=papel, VALOR=c["fact_time"], ORIGEM=origem, BASIS=basis,
                    PRECISAO=c["fact_time_precision"], PORQUE=porque,
                    BASE_DO_VIVO=c["fact_time_basis"][:400])

    # ── 2 · o trecho nao escreve a data: o CABECALHO da seccao pode governa-la (D147) ──
    r = _compor_do_cabecalho(texto, alvo, secao, periodos, pub, span)
    if not r["CONDICOES"]:
        p = r["PERIODO"]
        return dict(base, PAPEL=ACONTECIMENTO, VALOR=p["VALOR"], ORIGEM=CABECALHO, BASIS=p["BASIS"],
                    PRECISAO=_precisao_do_periodo(p),
                    PORQUE="D147: as cinco condicoes cumpridas — o cabecalho da seccao governa a afirmacao",
                    COMPOSICAO={"TRECHO_DO_CABECALHO": p["BASIS"]["TRECHO"], "TRECHO_DO_ALVO": span,
                                "PAPEL_DO_CABECALHO": p["PAPEL"], "PORQUE_DO_CABECALHO": p["PORQUE"]})

    # ── 3 · nem uma coisa nem outra ────────────────────────────────────────
    ha = _ha_tempo_escrito(span) or bool(periodos)
    porque = c["fact_time_basis"][:400]
    if r["CONDICOES"]:
        porque += " · cabecalho: " + "; ".join(r["CONDICOES"])
    return dict(base, PAPEL=NAO_SEI, VALOR=NAO_SEI if ha else NAO_EXISTE, ORIGEM=None, BASIS=None,
                PRECISAO="NOT_KNOWN", PORQUE=porque,
                PERIODOS_NO_CABECALHO=[{"VALOR": p["VALOR"], "PAPEL": p["PAPEL"],
                                        "TRECHO": p["BASIS"]["TRECHO"]} for p in periodos])


def _trecho_do_basis(basis: str) -> str | None:
    """O trecho literal que o vivo poe no fim da `fact_time_basis`, entre aspas baixas."""
    m = re.findall(r"«(.*?)»", str(basis or ""), re.S)
    return m[-1] if m else None


def contrato() -> dict:
    return {
        "SOURCE_ID": "TEMPO-DA-AFIRMACAO-CONTRATO",
        "VERSION": "V1",
        "DECISAO": "D158",
        "LEIS": ["D63", "D147", "D149", "D153", "COL-LAW-031", "COL-LAW-032", "COL-LAW-201"],
        "LEITOR_VIVO": LEITOR_VIVO,
        "PAPEIS": list(PAPEIS),
        "PAPEL_QUE_E_FACTO": list(PAPEL_QUE_E_FACTO),
        "ORIGENS": list(ORIGENS),
        "AUSENCIAS": [NAO_SEI, NAO_EXISTE],
        "O_QUE_ISTO_NAO_E": ("nao e um segundo leitor temporal: quem le a expressao continua a ser "
                             "leis/fato_do_texto.py. Isto e a janela por onde se lhe pergunta, para a "
                             "L5 poder entrar no lugar dele."),
    }


if __name__ == "__main__":
    json.dump(contrato(), sys.stdout, ensure_ascii=False, indent=1)
    print()
