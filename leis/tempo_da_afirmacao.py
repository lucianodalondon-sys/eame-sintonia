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
# QUATRO origens, e cada uma diz ONDE esta a prova. A distincao e do dono da Intelligence
# (CONTRATO-CONSUMO-AFIRMACOES §5-B, condicao C1): a 1.a versao chamava LITERAL ao valor que
# vinha do CABECALHO quando uma relativa do trecho batia com ele — e LITERAL, para quem
# consome, promete que o BASIS esta DENTRO do trecho. Prometia o que nao cumpria.
LITERAL = "LITERAL"
#: escrito DENTRO do proprio trecho; o BASIS cai entre INICIO e FIM da afirmacao
CABECALHO_D147 = "CABECALHO_D147"
#: composto do cabecalho da seccao, com as cinco condicoes da D147 cumpridas
RELATIVA_ANCORADA_D149 = "RELATIVA_ANCORADA_D149"
#: o trecho escreve uma relativa («la settimana scorsa») e o cabecalho da seccao imprime o
#: periodo; os dois dao o MESMO valor, e o impresso e a prova. O BASIS e o do CABECALHO —
#: e por isso esta origem NAO se chama LITERAL.
RELATIVO_D63 = "RELATIVO_D63"
#: contado pelo leitor vivo a partir de publicacao PROVADA; o BASIS e o trecho da expressao
ORIGENS = (LITERAL, CABECALHO_D147, RELATIVA_ANCORADA_D149, RELATIVO_D63)
#: as origens cujo BASIS vive FORA do trecho da afirmacao. LITERAL nunca esta aqui.
ORIGENS_COM_BASIS_FORA_DO_TRECHO = (CABECALHO_D147, RELATIVA_ANCORADA_D149)

#: o motivo com que o tempo sai NAO SEI por haver mais de um tempo no trecho (BLK-1)
TEMPOS_CONCORRENTES = "TEMPOS_CONCORRENTES"

# ── o vocabulario que MARCA o papel, quando o papel esta escrito ─────────────
# Palavras administrativas e comerciais do italiano. Nao sao saber agronomico nem
# taxonomia: sao a palavra com que a propria fonte diz de que e a data. Uma data
# sem nenhuma destas marcas nao ganha papel por elas — cai na regra do tempo.
# ⚠️ As tres ultimas alternativas entraram pelo red team D160 §2.2: «impiego consentito a
# partire dal 1 aprile 2026 fino al 29 luglio 2026» e uma JANELA DE USO, e saia como
# ACONTECIMENTO em tres casos reais (`derived:busca-3ae87b2ee6c08d80`). Uma janela em que
# uma coisa E PERMITIDA nunca e a data em que ela aconteceu.
_MARCA_DE_VALIDADE = re.compile(
    r"(?<![a-zà-ÿ])(?:validit|valid[oa]\s+(?:dal|fino|da|al)|in\s+vigore|vigenza|scadenz|"
    r"fino\s+al\s+termine|proroga\s+(?:al|fino)|"
    r"(?:impiego|utilizzo|impieghi|uso)\s+(?:consentit|ammess|autorizzat)|"
    r"(?:consentit[oi]|ammess[oi]|autorizzat[oi])\s+(?:a\s+partire\s+)?dal|"
    r"vale\s+dal|decorre\s+dal|con\s+decorrenza|"
    # ⚠️ RT3 §2.C · A JANELA QUE UMA AGENCIA «TORNA ATIVA» NAO E O DIA EM QUE ALGO ACONTECEU.
    # «Dal 22 giugno al 14 settembre, l'Agenzia … rende attiva … la fase di attenzione per gli
    # incendi boschivi» saia ACONTECIMENTO «22 giugno» em 4 afirmacoes. Ninguem observou nada a
    # 22 de junho: aquilo e a janela em que uma regra vale — que e o que VALIDADE quer dizer.
    r"rende\s+attiv|fase\s+di\s+attenzione|fase\s+di\s+preallarme|stato\s+di\s+allerta|"
    # «di ogni anno» diz que a janela SE REPETE todos os anos. Uma janela que se repete nao e
    # um dia em que algo aconteceu. ⚠️ LIMITE DECLARADO: nao existe papel «RECORRENTE» neste
    # vocabulario, e inventar um seria decidir vocabulario de toda a casa. VALIDADE e o papel
    # mais proximo (a janela em que a regra se aplica) e, sobretudo, NAO e ACONTECIMENTO —
    # que era o defeito. Se o dono quiser um papel proprio, e decisao dele.
    r"di\s+ogni\s+anno)", re.I)
# ⚠️ PROD-4 · A FORMA DE CITACAO DE UM ATO NAO ESCREVE A PALAVRA «DECRETO».
# O dono mediu-o em «8810 del 24 aprile 2026, recante il Piano di azione … lotta obbligatoria
# … in Toscana»: um ATO que saia ALERTA_EVENTO. As palavras `decreto|determina|delibera` ja
# estavam aqui — e nenhuma esta NAQUELE trecho. O que esta ali e a forma como um ato se CITA:
# o numero, o «del <data>», e o «recante» que introduz o conteudo.
#
#     PROCURAR O NOME DO ATO E PERDER TODO O ATO QUE E CITADO PELO NUMERO.
#
# `recante` sozinho e marca forte (em italiano administrativo introduz o que o ato contem), e
# `n. <numero> del` e a citacao curta. Acrescentado por ordem escrita do dono da Intelligence.
_MARCA_DE_ATO = re.compile(
    r"(?<![a-zà-ÿ])(?:decreto|determina(?:zione)?|ordinanza|delibera(?:zione)?|d\.?\s?m\.?\s?n|"
    r"d\.?g\.?r\.?|circolare\s+n|legge\s+n|regolamento\s+\(?(?:ue|ce)\)?|recante|"
    r"n\.?\s*\d+\s+del(?![a-zà-ÿ])|lotta\s+obbligatoria|"
    # ⚠️ RT3 §2.D · os tres atos que o red team mediu a sair ACONTECIMENTO, e nenhum deles
    # escreve «decreto». Acrescentados por ordem escrita do coordenador (item 4).
    r"deroga|stabilito\s+dal|"
    # «è stato sostituito»: a substituicao de um orgao ou servico e um ato administrativo, e
    # era o caso que a revisao anterior registou como «menos grave» e eu deixei aberto por nao
    # ter autorizacao para mexer neste vocabulario. Agora tenho-a, por escrito.
    r"(?:e|è)\s+stat[oa]\s+sostituit)", re.I)
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


def dia_da_captura(valor) -> date | None:
    """O dia em que o documento foi colhido. NUNCA ancora uma data (D63): so recusa uma
    data que venha DEPOIS dele, que e o que o G0 ja faz ao item inteiro."""
    m = _RE_DIA_ISO.search(str(valor or ""))
    return _dia(m.group(1), m.group(2), m.group(3)) if m else None


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


# ── O FUTURO GRAMATICAL (red team D160 §2.1) ─────────────────────────────────
# O `_RE_FUTURO` do vivo e uma lista de PALAVRAS («previsto», «domani», «attesa»). Ele nao
# apanha o FUTURO DO VERBO, que em italiano se escreve na propria terminacao: «si terra»,
# «colpira», «sara organizzata», «si svolgeranno». Medido pelo red team: 10 datas
# posteriores a captura sairam como ACONTECIMENTO por causa disto.
# A regra e MORFOLOGICA, nao uma lista: o futuro simples da 3.a pessoa acaba em «-rà» ou
# «-ranno». O acento final e o que a torna segura em italiano — «città», «libertà» e «papà»
# acabam em «-tà» e «-pà», nunca em «-rà». Exige-se raiz de 2+ letras para nao apanhar
# «ranno» sozinho.
# ⚠️ RT3 §2.A · A REGRA DIZIA «FUTURO» PARA TUDO, E O COMENTARIO ACIMA EXPLICA PORQUE NAO.
# Ela aceitava `r[àa]`, com o `a` SEM acento, e o `marca_futuro` aplicava-a a `FL._baixo(span)`,
# que TIRA os acentos. Ou seja: o acento que o comentario diz tornar a regra segura era
# destruido antes de a regra correr. Medido: «peronospora», «temperatura», «ieri sera» e
# «duramente» davam futuro — e na Sala real 4 afirmacoes de chuva MEDIDA viraram PREVISAO.
#
#     UM COMENTARIO QUE DESCREVE A REGRA CERTA POR CIMA DO CODIGO QUE FAZ OUTRA
#     E PIOR DO QUE NENHUM: ELE FAZ A REVISAO PARAR DE PROCURAR.
#
# Agora o acento e OBRIGATORIO e a procura e feita no texto COM acentos. O `-ranno` fica sem
# acento porque em italiano nao ha outra forma: o unico substantivo comum que acaba assim e
# «tiranno», e esse sai por um olhar-atras de duas letras — um nome, nao uma lista.
_RE_FUTURO_DO_VERBO = re.compile(r"(?<![a-zà-ÿ])[a-zà-ÿ]{2,}(?:rà\b|(?<!ti)ranno\b)", re.I)
#: as construcoes que anunciam sem verbo no futuro, medidas pelo red team
_RE_ANUNCIO = re.compile(
    r"(?<![a-zà-ÿ])(?:in\s+programma|fissat[oaie]\s+per|in\s+calendario|avr[àa]\s+luogo|"
    r"si\s+terr|si\s+svolger|a\s+partire\s+da(?:l|lla)?\s+prossim|"
    # ⚠️ RT3 §2.B · «entro il prossimo 11 settembre, previa registrazione» saia ACONTECIMENTO.
    # E um PRAZO, e um prazo e futuro. O calendario nao o apanhava: sem ano escrito o
    # `primeiro_dia` devolve None e a comparacao com a publicacao nunca acontece. Quem o
    # apanha e a palavra — «entro il prossimo» nao se diz de nada que ja passou.
    r"entro\s+il\s+prossim|entro\s+la\s+prossim)", re.I)


#: onde uma frase acaba. Exige espaco depois do ponto, para «20.09.2026» nao ser duas frases.
_RE_FIM_DE_FRASE = re.compile(r"[.;!?]+\s|\n")


def frase_do_valor(span: str, valor: str) -> str:
    """A FRASE do trecho onde a data esta escrita.

    ⚠️ RT3 §2.A, 2.º defeito: a versao anterior cortava uma JANELA de N LETRAS em volta da
    data, e cortava A MEIO DE UMA PALAVRA. «…aveva colpito duramente…» virava «…colpito dura»,
    e o `\\b` do fim da expressao casava contra o CORTE — «dura» passava por futuro.
    Uma janela que corta palavras inventa palavras que o texto nao tem.

    A unidade certa nao e um numero de letras: e a FRASE. Ela nao parte palavras, e e o que o
    italiano usa para prender um verbo ao seu complemento. E continua BOUNDED — nao e o trecho
    inteiro: um verbo no futuro NOUTRA frase do mesmo trecho nao fala desta data (e o mutante
    RT12 do red team, que o teste `test_o_futuro_de_outra_frase_nao_conta` agora mata)."""
    texto = str(span or "")
    v = str(valor or "").lower()
    i = texto.lower().find(v)
    if i < 0 or not v:
        return texto
    a = 0
    for m in _RE_FIM_DE_FRASE.finditer(texto):
        if m.end() <= i:
            a = m.end()
        else:
            break
    b = len(texto)
    for m in _RE_FIM_DE_FRASE.finditer(texto, i + len(v)):
        b = m.start()
        break
    return texto[a:b]


def marca_futuro(span: str, valor: str) -> bool:
    """O trecho anuncia o que ainda nao aconteceu, na frase DA data?

    A pergunta e a do vivo (`fato_do_texto._futuro_perto`, com a janela dele); o que se
    acrescenta sao as duas formas que a lista de palavras do vivo nao tem — e procura-se no
    texto COM acentos, porque e o acento que distingue o futuro «-rà» de qualquer palavra
    acabada em «-ra»."""
    if FT._RE_FUTURO.search(span) and FT._futuro_perto(span, valor):
        return True
    frase = frase_do_valor(span, valor)
    return bool(_RE_FUTURO_DO_VERBO.search(frase) or _RE_ANUNCIO.search(frase))


def _papel_do_vivo(c: dict, span: str, pub, captura=None) -> tuple:
    """(PAPEL, PORQUE) para o tempo que o vivo devolveu sobre o trecho."""
    valor = c["fact_time"]
    marca = papel_do_periodo(span, None, None, None)[0]
    if marca in (VALIDADE, ATO, MARKET_PERIOD, PUBLICACAO):
        return marca, "o proprio trecho escreve a marca do papel"
    if marca_futuro(span, valor):
        return PREVISAO, "o trecho anuncia o que ainda nao aconteceu, junto da data"
    ini, sem_ano = primeiro_dia(valor)
    if ini is not None:
        if pub is not None and ini > pub:
            return PREVISAO, "a data e posterior a publicacao provada"
        # A DATA DEPOIS DA CAPTURA NAO PODE SER UM ACONTECIMENTO OBSERVADO. Isto nao e
        # ancorar nada na coleta (a D63 proibe ancorar): e recusar. E a mesma regra que o
        # G0 ja aplica ao item inteiro (`FACT_TIME:FUTURO_EM_RELACAO_A_CAPTURA`), feita
        # agora por afirmacao.
        if captura is not None and ini > captura:
            return PREVISAO, "a data e posterior ao dia em que o documento foi colhido"
    return ACONTECIMENTO, "o leitor vivo prendeu a data a um acontecimento (kind %s)" % c["fact_time_kind"]


# ── LER A DATA EM QUALQUER FORMA QUE O VIVO ESCREVA ──────────────────────────
# O vivo devolve o valor COMO O TEXTO O ESCREVE: um intervalo em ISO, mas tambem
# «12 novembre 2026», «6-8 ottobre 2026», «18 febbraio» (sem ano), «16/09/2026».
# (RT3 §4: este comentario citava uma data da corrida R9. O §5 do LAB manda ZERO mencoes
#  dela no codigo de producao — mesmo em prosa —, e uma data de exemplo nao precisa de ser
#  a dela para explicar a forma.)
# Ler so o ISO foi o defeito medido: `_primeiro_dia` devolvia None e a comparacao com a
# publicacao nunca acontecia. Isto NAO e um leitor de italiano novo — e a leitura do
# NUMERO de um valor que o vivo ja leu, com a tabela de meses do dono dela (`fato_local`).
_RE_DIA_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_RE_DIA_BARRA = re.compile(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})\b")
_RE_DIA_MES = re.compile(r"\b(\d{1,2})\s*(?:[-–]\s*\d{1,2}\s*)?(%s)(?:\s+(\d{4}))?\b"
                         % "|".join(FL.MESES), re.I)
_RE_SO_MES = re.compile(r"\b(%s)\s+(\d{4})\b" % "|".join(FL.MESES), re.I)
_RE_SO_ANO = re.compile(r"\b((?:19|20)\d{2})\b")


def primeiro_dia(valor) -> tuple:
    """(o primeiro dia do valor, sem_ano) — `(None, …)` quando nao ha dia nenhum.

    `sem_ano` e True quando o texto escreve o dia e o mes e NAO escreve o ano: nesse caso
    nao se inventa o ano (nem o da publicacao), e a precisao passa a dizer que ele falta."""
    s = str(valor or "")
    m = _RE_DIA_ISO.search(s)
    if m:
        return _dia(m.group(1), m.group(2), m.group(3)), False
    m = _RE_DIA_BARRA.search(s)
    if m:
        return _dia(m.group(3), m.group(2), m.group(1)), False
    m = _RE_DIA_MES.search(FL._baixo(s))
    if m:
        mes = FL.MES_NUM[m.group(2).lower()]
        if m.group(3):
            return _dia(m.group(3), mes, m.group(1)), False
        return None, True
    m = _RE_SO_MES.search(FL._baixo(s))
    if m:
        return _dia(m.group(2), FL.MES_NUM[m.group(1).lower()], 1), False
    m = _RE_SO_ANO.search(s)
    if m:
        return _dia(m.group(1), 1, 1), False
    # ⚠️ RT3 §2.D · O MES SOZINHO TAMBEM NAO ESCREVE O ANO.
    # `primeiro_dia('luglio')` devolvia `(None, False)`, e o `False` era lido por quem chama
    # como «tem ano» — logo a classe dizia «o ano esta escrito» sobre «luglio», «marzo»,
    # «maggio» e «ottobre» (5 casos reais medidos pelo red team). O `_RE_DIA_MES` quer o dia e
    # o `_RE_SO_MES` quer o ano; um mes sozinho nao casa nenhum dos dois e caia aqui, calado.
    # Nao se inventa o ano (nem o da publicacao, D63): diz-se que ele FALTA.
    if _RE_MES_ESCRITO.search(FL._baixo(s)):
        return None, True
    return None, False


# ── QUANTOS TEMPOS O TRECHO ESCREVE (BLK-1, Intelligence owner) ──────────────
# O BLOQUEADOR, na frase em que o dono o encontrou (CLAIM …330ce9da):
#
#     «rilevata in Europa per la prima volta nel 2004 e in Italia nel 2012, in Emilia Romagna»
#
# O produtor devolvia FACT_TIME = 2004 e FACT_LOCATION = Italia. O texto diz o contrario:
# 2004 e a Europa; a Italia e 2012. Duas metades de factos DIFERENTES, colhidas como se
# fossem um.
#
#     UM PAR TEMPO+LUGAR MONTADO DE DOIS FACTOS E UM FACTO FALSO,
#     E UM FACTO FALSO E PIOR DO QUE NENHUM.
#
# A condicao 3 da D147 («o trecho nao escreve outro tempo concorrente») ja existia — mas so
# era aplicada a composicao por CABECALHO. Ao valor LITERAL, lido no proprio trecho, nao era.
# Esta funcao conta, e o `extrair_tempo` recusa.
#
# NAO HA VOCABULARIO NOVO AQUI. Conta com as MESMAS cinco expressoes que o `primeiro_dia`
# usa para ler, e na mesma ordem de prioridade. Uma segunda lista de formas de data ao lado
# da primeira seria a segunda a ficar para tras.
_FORMAS_DE_DATA = ((_RE_DIA_ISO, False), (_RE_DIA_BARRA, False),
                   (_RE_DIA_MES, True), (_RE_SO_MES, True), (_RE_SO_ANO, False))
#: o que LIGA duas datas num SO periodo («dal 1 gennaio al 31 dicembre»). Deliberadamente
#: CURTA: «e» ficou de fora, porque «nel 2004 e nel 2012» sao dois factos e «tra il 2004 e o
#: 2012» e um periodo — e a mesma palavra. Ligar de MENOS conta tempos a MAIS, e contar a
#: mais so produz NAO SEI. Ligar de mais produziria um facto.
_RE_LIGA_UM_PERIODO = re.compile(
    r"^\W*(?:al|all'|alla|ao|fino\s+al?|sino\s+al?|entro\s+il|[-–—/])\W*$", re.I)


def expressoes_de_tempo(span: str) -> list:
    """As expressoes de data ESCRITAS neste trecho, sem se sobreporem, da esquerda para a
    direita. Um intervalo («dal X al Y») conta como UMA."""
    texto = str(span or "")
    baixo = FL._baixo(texto)
    # O `_baixo` tira acentos por decomposicao; em quase todo o italiano o comprimento
    # aguenta-se, mas uma ligadura tipografica encolhe-o. Nesse caso o offset deixaria de
    # bater, e entao le-se o trecho da MESMA string onde ele foi procurado.
    mesmo_tamanho = len(baixo) == len(texto)
    achados, ocupado = [], []
    for rx, em_baixo in _FORMAS_DE_DATA:
        sobre = baixo if em_baixo else texto
        for m in rx.finditer(sobre):
            if any(m.start() < f and i < m.end() for i, f in ocupado):
                continue                      # ja apanhado por uma forma mais longa
            ocupado.append((m.start(), m.end()))
            bruto = (texto if (mesmo_tamanho or not em_baixo) else sobre)[m.start():m.end()]
            achados.append({"INICIO": m.start(), "FIM": m.end(), "TRECHO": bruto})
    achados.sort(key=lambda x: x["INICIO"])
    # ── juntar o que e UM periodo, e tirar a data repetida ────────────────────
    juntos = []
    for a in achados:
        if juntos:
            entre = texto[juntos[-1]["FIM"]:a["INICIO"]]
            if _RE_LIGA_UM_PERIODO.match(entre):
                juntos[-1] = dict(juntos[-1], FIM=a["FIM"],
                                  TRECHO=texto[juntos[-1]["INICIO"]:a["FIM"]])
                continue
        juntos.append(a)
    vistos, fora = set(), []
    for a in juntos:
        chave = re.sub(r"\s+", " ", FL._baixo(a["TRECHO"])).strip()
        if chave in vistos:
            continue                          # a mesma data escrita duas vezes e uma data
        vistos.add(chave)
        fora.append(a)
    return fora


def tempos_no_trecho(span: str) -> int:
    """QUANTOS tempos distintos o trecho escreve. Viaja em cada afirmacao (contrato §5-C)."""
    return len(expressoes_de_tempo(span))


def _escreve_este_dia(escritos: list, valor) -> str | None:
    """A expressao do trecho que da ESTE mesmo dia, ou None (PROD-1).

    Compara-se pelo DIA a que cada forma se resolve, com o mesmo `primeiro_dia` que le o
    valor — nunca por texto igual: «12 novembre 2026» e «2026-11-12» sao a mesma data e
    nenhuma string das duas contem a outra."""
    dia, _sem_ano = primeiro_dia(valor)
    if dia is None:
        return None
    for x in escritos:
        se_dia, _ = primeiro_dia(x["TRECHO"])
        if se_dia == dia:
            return x["TRECHO"]
    return None


# ── O ANO, PERGUNTADO AO VALOR E NAO A PRECISAO (PROD-3) ─────────────────────
# «il suo ciclo iniziava con la semina nel mese di marzo» saia com a classe ALERTA_EVENTO
# SEM ANO — contra a regra do proprio produtor, que diz «sem ano, NAO SEI».
#
# A causa nao era a regra da classe: era o SINAL que ela lia. O `sem_ano` do `primeiro_dia`
# so acende no caso «dia + mes sem ano» (`_RE_DIA_MES` com o grupo do ano vazio). Um mes
# SOZINHO — «marzo» — nao casa o `_RE_DIA_MES` (falta-lhe o dia) nem o `_RE_SO_MES` (falta-lhe
# o ano), logo `primeiro_dia` devolvia `(None, False)` e o «False» era lido como «tem ano».
#
#     UM SINAL QUE SO SABE DIZER «FALTA O ANO» EM UM DOS CASOS EM QUE ELE FALTA
#     NAO E UM SINAL DE QUE FALTA O ANO.
#
# Agora pergunta-se ao VALOR se ele escreve um ano, com a mesma expressao que o le.
_RE_MES_ESCRITO = re.compile(r"(?<![a-z])(?:%s)(?![a-z])" % "|".join(FL.MESES), re.I)


def escreve_o_ano(valor) -> bool:
    """O valor escreve um ano de quatro algarismos? (a mesma `_RE_SO_ANO` que o le)"""
    return bool(_RE_SO_ANO.search(str(valor or "")))


def falta_o_ano(valor) -> bool:
    """O valor nomeia um mes (ou um dia) e NAO escreve o ano.

    Nao se inventa o ano — nem o da publicacao (D63). O que se faz e DIZER que ele falta."""
    s = str(valor or "")
    if escreve_o_ano(s):
        return False
    return bool(_RE_MES_ESCRITO.search(FL._baixo(s)) or re.search(r"\d", s))


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
        CAPTURA        o dia em que o documento foi colhido (opcional). NAO ancora nada
                       (a D63 proibe); serve so para RECUSAR uma data posterior a ele

    O valor sai em VALOR; NAO SEI quando ha tempo escrito mas nao se prova que e desta
    afirmacao; NAO_EXISTE quando nem o trecho nem a seccao escrevem tempo nenhum."""
    ini, fim = int(alvo["INICIO"]), int(alvo["FIM"])
    span = texto[ini:fim]
    secao = alvo.get("SECAO") or {"INICIO": 0, "FIM": len(texto)}
    publicacao = alvo.get("PUBLICACAO") or {}
    pub = FT.publicacao_provada(publicacao.get("VALOR"), publicacao.get("BASE"))
    captura = dia_da_captura(alvo.get("CAPTURA"))
    escritos = expressoes_de_tempo(span)
    base = {"LEITOR": LEITOR_VIVO, "PUBLICACAO_PROVADA": pub.isoformat() if pub else None,
            "CAPTURA": captura.isoformat() if captura else None,
            "TEMPOS_NO_TRECHO": len(escritos),
            "EXPRESSOES_DE_TEMPO": [x["TRECHO"] for x in escritos],
            "LEI": "D63 · D147 · D149 · D153 · §5-C (tempos concorrentes); "
                   "so ACONTECIMENTO e tempo do facto"}

    cab_doc = cabecalho_do_documento(texto)
    periodos = periodos_do_cabecalho(texto, secao["INICIO"], ini, pub, cabecalho_do_documento=cab_doc)

    # ── 1 · o que o LEITOR VIVO le no proprio trecho ───────────────────────
    c = _do_vivo(span, publicacao.get("VALOR"), publicacao.get("BASE"))
    if c["fact_time"] != NAO_SEI:
        papel, porque = _papel_do_vivo(c, span, pub, captura)
        calculada = c["fact_time_calculo"] == FT.RELATIVA
        # ── PROD-1 · a data ESCRITA no trecho e LITERAL, mesmo com «oggi» ao lado ──
        # O dono (contrato §5-C, «Origem»): «Uma data escrita por extenso dentro do trecho e
        # LITERAL, mesmo que venha acompanhada de "oggi" ou "ieri". O rotulo RELATIVO_D63 so
        # vale quando o valor foi mesmo CALCULADO a partir da publicacao.»
        #
        # O vivo marca a leitura como RELATIVA quando ve a palavra relativa, mesmo que o
        # valor que devolve venha da data escrita ao lado. RELATIVO_D63 promete a quem
        # consome que o BASIS e a expressao relativa e que a conta partiu da publicacao —
        # e prometia isso sobre uma data que estava ali, escrita, para ser lida.
        if calculada and _escreve_este_dia(escritos, c["fact_time"]):
            calculada = False
            porque = ("%s · §5-C: a data esta ESCRITA no trecho («%s»), logo a origem e "
                      "LITERAL e nao RELATIVO_D63 — o valor nao foi calculado da publicacao"
                      % (porque, _escreve_este_dia(escritos, c["fact_time"])))
        origem = RELATIVO_D63 if calculada else LITERAL
        # ── A CONTAGEM DE TEMPOS TEM DE INCLUIR O TEMPO EMITIDO, quando ele e LITERAL ──
        # Achado pela bancada L2 no artefato publicado (derived:21): `FACT_TIME = «marzo»` com
        # `ORIGEM = LITERAL` e `TEMPOS_NO_TRECHO = 0`. E o espelho exacto da PROD-3 do lado do
        # lugar, e pela mesma razao: um mes SOZINHO nao casa nenhuma das cinco formas de data
        # (`_RE_DIA_MES` quer o dia, `_RE_SO_MES` quer o ano), logo o contador nao o ve — mas o
        # leitor vivo emitiu-o.
        #
        #     ZERO AO LADO DE UM VALOR PRESENTE E O MESMO ESTADO INCOERENTE,
        #     SEJA DO LADO DO TEMPO OU DO LADO DO LUGAR.
        #
        # ⚠️ SO PARA `LITERAL`, e o limite e da L2: com `CABECALHO_D147`,
        # `RELATIVA_ANCORADA_D149` ou `RELATIVO_D63` o valor NAO esta escrito no trecho — vem
        # do cabecalho ou de uma conta — e ai a contagem de zero esta CERTA. Contar o valor
        # nesses casos era inventar uma data escrita onde nao ha nenhuma.
        # ⚠️ A CONDICAO E «NADA CONTADO», E NAO «o valor nao bate com nenhum».
        # A 1.a versao perguntava `not _escreve_este_dia(escritos, valor)`, e isso QUEBROU um
        # teste que ja existia: em «il 18 febbraio» (dia e mes sem ano) o `primeiro_dia` nao
        # resolve dia nenhum, logo `_escreve_este_dia` nao podia casar, logo eu somava uma
        # segunda expressao sobre a mesma data, a contagem ia a 2, e a guarda dos concorrentes
        # matava um FACT_TIME que estava certo. Com `origem == LITERAL` o valor FOI lido no
        # trecho: se ja se contou alguma coisa, ela e ele. So o ZERO e que e incoerente.
        if origem == LITERAL and not escritos:
            escritos = escritos + [{"INICIO": None, "FIM": None, "TRECHO": str(c["fact_time"]),
                                    "DE_ONDE": "emitido pelo leitor vivo como LITERAL; a forma "
                                               "escrita nao casa nenhuma das cinco formas de "
                                               "data (ex.: o mes sozinho, «marzo»)"}]
            base = dict(base, TEMPOS_NO_TRECHO=len(escritos),
                        EXPRESSOES_DE_TEMPO=[x["TRECHO"] for x in escritos])
        trecho = c["fact_time_evidencia"] if calculada else _trecho_do_basis(c["fact_time_basis"])
        basis = _basis(texto, trecho, (ini, fim)) or _basis(texto, span, (ini, fim))
        # ── D149 · a relativa ancora-se no periodo IMPRESSO, quando ele existe ──
        impressos = [p for p in periodos if p["PAPEL"] == ACONTECIMENTO]
        if calculada and len(impressos) == 1:
            p = impressos[0]
            if p["VALOR"] == c["fact_time"]:
                return dict(base, PAPEL=papel, VALOR=p["VALOR"], ORIGEM=RELATIVA_ANCORADA_D149,
                            BASIS=p["BASIS"], PRECISAO=_precisao_do_periodo(p),
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
        # ── BLK-1 · dois tempos de ACONTECIMENTO no trecho: qual deles e o do facto? ──
        # O produtor NAO TEM analisador de sintaxe: nao sabe dizer qual data prende qual
        # facto. Entao, havendo mais de uma, nao escolhe — e nao escolher escreve-se NAO SEI.
        # So morde o ACONTECIMENTO, que e o unico papel que vira FACT_TIME: uma janela de
        # VALIDADE («dal … fino al …») tem duas pontas de proposito, e o intervalo ja conta
        # como UMA em `expressoes_de_tempo`.
        if papel in PAPEL_QUE_E_FACTO and len(escritos) > 1:
            return dict(base, PAPEL=NAO_SEI, VALOR=NAO_SEI, ORIGEM=None, BASIS=basis,
                        PRECISAO="NOT_KNOWN", MOTIVO=TEMPOS_CONCORRENTES,
                        PORQUE="§5-C: o trecho escreve %d tempos (%s) e o produtor nao tem "
                               "como provar qual deles e o do facto — o vivo leu «%s». "
                               "Escolher seria inferir"
                               % (len(escritos), ", ".join("«%s»" % x["TRECHO"] for x in escritos),
                                  c["fact_time"]),
                        CONCORRENTES=[x["TRECHO"] for x in escritos],
                        LIDO_PELO_VIVO=c["fact_time"])
        _dia_lido, sem_ano = primeiro_dia(c["fact_time"])
        sem_ano = sem_ano or falta_o_ano(c["fact_time"])      # PROD-3: o mes sozinho tambem
        precisao = c["fact_time_precision"] + ("+SEM_ANO" if sem_ano else "")
        # ⚠️ RT3 §7 · «+CALCULADA» AO LADO DE «LITERAL» SAO DUAS AFIRMACOES OPOSTAS.
        # O selo do vivo diz que o valor foi CONTADO; a origem LITERAL diz que ele estava
        # ESCRITO. Depois da PROD-1 (a data escrita e LITERAL mesmo com «oggi» ao lado) as duas
        # coisas apareciam juntas no mesmo campo, e quem consome tinha de escolher em qual
        # acreditar. Quem manda e a ORIGEM, que e a decisao desta lei.
        if origem == LITERAL:
            precisao = precisao.replace("+CALCULADA", "")
        return dict(base, PAPEL=papel, VALOR=c["fact_time"], ORIGEM=origem, BASIS=basis,
                    PRECISAO=precisao, ANO=NAO_SEI if sem_ano else None, PORQUE=porque,
                    BASE_DO_VIVO=c["fact_time_basis"][:400])

    # ── 2 · o trecho nao escreve a data: o CABECALHO da seccao pode governa-la (D147) ──
    r = _compor_do_cabecalho(texto, alvo, secao, periodos, pub, span)
    if not r["CONDICOES"]:
        p = r["PERIODO"]
        return dict(base, PAPEL=ACONTECIMENTO, VALOR=p["VALOR"], ORIGEM=CABECALHO_D147, BASIS=p["BASIS"],
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
