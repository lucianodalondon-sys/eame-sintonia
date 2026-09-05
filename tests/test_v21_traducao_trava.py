# -*- coding: utf-8 -*-
"""
PROVA QUE A TRAVA AINDA MORDE.

    python3 -m pytest tests/test_v21_traducao_trava.py -q

POR QUE ESTE ARQUIVO EXISTE
----------------------------
A trava da tradução foi corrigida SEIS VEZES até parar de reprovar tradução
correta. Cada correção afrouxou alguma coisa: aceitou mês por extenso, aceitou
número virado palavra, trocou contagem por presença, alargou a lista de
negações.

    UMA TRAVA CORRIGIDA ATÉ PASSAR PODE TER VIRADO UM CARIMBO.

Então aqui se planta mentira de propósito — uma para cada proibição da missão —
e se exige que ela seja pega. Se algum destes testes passar a falhar, a trava
deixou de proteger e o pacote não pode ser gerado até que ela volte a morder.

O que NÃO se testa aqui: se «autorizza» quer dizer «autoriza». Nenhuma trava
mecânica sabe, e fingir que sabe é pior do que dizer que não sabe.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'scripts'))
from v21_traducao_trava import conferir  # noqa: E402


def erros(pt, alvo, lingua='EN'):
    return ' '.join(conferir(pt, alvo, lingua))


# ── 1 · ACRESCENTAR FATO ────────────────────────────────────────────────────
def test_numero_inventado_e_pego():
    pt = 'A area plantada foi de 120 mil hectares.'
    mentira = 'The planted area was 120 thousand hectares, up 15% on the year.'
    assert 'NUMERO_NASCEU' in erros(pt, mentira)


def test_numero_apagado_e_pego():
    pt = 'A amostra foi de 200 azeitonas em quatro zonas.'
    mentira = 'The sample covered several olives across four zones.'
    assert 'NUMERO_SUMIU:200' in erros(pt, mentira)


# ── 2 · FORTALECER ALEGAÇÃO ─────────────────────────────────────────────────
def test_negacao_apagada_e_pega():
    pt = 'NAO prova eficacia, recomendacao nem prioridade.'
    mentira = 'Proves efficacy, recommendation and priority.'
    assert 'NEGACAO_SUMIU' in erros(pt, mentira)


def test_negacao_preservada_passa():
    pt = 'nao prova eficacia, recomendacao nem prioridade.'
    bom = 'does not prove efficacy, recommendation or priority.'
    assert erros(pt, bom) == ''


def test_enfase_do_nao_tem_de_atravessar():
    """«NAO prova» em caixa alta é o aviso; «does not prove» apaga o aviso.

    Esta fixture já esteve errada aqui dentro: eu escrevi o português enfático e
    o inglês neutro, e culpei a trava por reprovar. Ela estava certa.
    """
    pt = 'NAO prova eficacia, recomendacao nem prioridade.'
    fraco = 'Does not prove efficacy, recommendation or priority.'
    forte = 'Does NOT prove efficacy, recommendation or priority.'
    assert 'CAIXA_ALTA_CAIU' in erros(pt, fraco)
    assert erros(pt, forte) == ''


def test_sigla_nao_conta_como_enfase():
    """CDI e EDO aparecem iguais nas duas línguas: não são grito, são sigla."""
    pt = 'O CDI do EDO poe o norte em alerta nesta decada.'
    bom = 'The EDO CDI places the north in alert in this ten-day period.'
    assert 'CAIXA_ALTA_CAIU' not in erros(pt, bom)


# ── 3 · MUDAR ALCANCE GEOGRÁFICO ────────────────────────────────────────────
def test_regiao_que_some_e_pega():
    pt = 'O dado vale para o Veneto, nao para a Italia inteira.'
    mentira = 'The figure holds for the whole country.'
    assert 'LUGAR_SUMIU:Veneto' in erros(pt, mentira)


def test_cidade_traduzida_nao_e_falso_alarme():
    pt = 'Evento em Bruxelas, nao na Italia.'
    bom = 'Event in Brussels, not in Italy.'
    assert 'LUGAR_SUMIU' not in erros(pt, bom)


# ── 4 · REMOVER INCERTEZA ───────────────────────────────────────────────────
def test_ressalva_apagada_e_pega():
    pt = 'O modelo indica risco elevado; a leitura pode estar defasada.'
    mentira = 'The model shows high risk.'
    assert 'INCERTEZA_SUMIU' in erros(pt, mentira)


# ── 5 · MUDAR CONFIANÇA (a ênfase é o aviso) ────────────────────────────────
def test_caixa_alta_que_some_e_pega():
    pt = ('CONDICAO CLIMATICA NAO ESTABELECE PRESENCA DE DOENCA nesta leitura '
          'do boletim regional.')
    mentira = ('Climate condition does not establish disease presence in this '
               'regional bulletin reading.')
    assert 'CAIXA_ALTA_CAIU' in erros(pt, mentira)


# ── 6 · O QUE A TRAVA APRENDEU A NÃO REPROVAR ───────────────────────────────
# Cada um destes já foi um falso alarme que quase me fez afrouxar a trava por
# engano. Ficam aqui para que o afrouxamento não volte disfarçado de correção.
def test_data_por_extenso_passa():
    pt = 'A BASF publicou em 30/01/2026 o comunicado.'
    bom = 'BASF published the statement on 30 January 2026.'
    assert erros(pt, bom) == ''


def test_dia_sem_ano_passa():
    pt = 'Episodios em 10/03, 19/03 e 09/04/2026.'
    bom = 'Episodes on 10 March, 19 March and 9 April 2026.'
    assert erros(pt, bom) == ''


def test_numero_virado_palavra_passa():
    pt = 'E uma decada de 10 dias, nao o estado de hoje.'
    bom = 'It is a ten-day period, not today’s state.'
    assert erros(pt, bom) == ''


def test_repeticao_a_menos_passa():
    pt = 'Essas 10 pracas nao sao comparaveis; somar essas 10 mistura estagios.'
    bom = ('These 10 market places are not comparable; adding them up mixes '
           'stages.')
    assert erros(pt, bom) == ''


def test_nao_renovacao_passa():
    pt = 'PROJETO de regulamento de NAO-RENOVACAO da aprovacao.'
    bom = 'DRAFT regulation for NON-RENEWAL of the approval.'
    assert 'NEGACAO_SUMIU' not in erros(pt, bom)


def test_proibicao_nao_exige_hedge():
    """«não pode ser citado» é proibição; exigir «may» ali seria afrouxar."""
    pt = 'Este preco nao pode ser citado como preco nacional.'
    bom = 'This price cannot be cited as a national price.'
    assert 'INCERTEZA_SUMIU' not in erros(pt, bom)


def test_vazia_e_pega():
    assert conferir('qualquer coisa com 5 numeros', '', 'EN') == ['VAZIA']


# ── 7 · os buracos de vocabulário que 726 traduções revelaram ───────────────
# Nove traduções corretas foram reprovadas porque faltava palavra na lista. Cada
# uma virou um teste, para que a lista não volte a encolher sem alguém notar.
def test_potrebbe_conta_como_incerteza_em_italiano():
    pt = 'pode haver texto dentro do JPG que nao extraimos.'
    bom = 'potrebbe esserci del testo dentro il JPG che non abbiamo estratto.'
    assert 'INCERTEZA_SUMIU' not in erros(pt, bom, 'IT')


def test_unable_conta_como_negacao_em_ingles():
    pt = 'o PDF fica atras de um botao que eu nao consegui resolver.'
    bom = 'the PDF sits behind a button that I was unable to resolve.'
    assert 'NEGACAO_SUMIU' not in erros(pt, bom)


def test_mancanza_conta_como_negacao_em_italiano():
    pt = 'impacto severo por calor e falta de agua no Norte da Italia'
    bom = 'impatto severo da caldo e mancanza d’acqua nel Nord Italia'
    assert 'NEGACAO_SUMIU' not in erros(pt, bom, 'IT')


def test_sole_conta_como_so_em_italiano():
    pt = 'a media vem de apenas tres pracas.'
    bom = 'la media proviene da sole tre piazze.'
    assert 'INCERTEZA_SUMIU' not in erros(pt, bom, 'IT')


def test_at_least_conta_como_incerteza():
    pt = 'esta desatualizado em pelo menos dois pontos que eu verifiquei.'
    bom = 'it is out of date in at least two places that I checked.'
    assert 'INCERTEZA_SUMIU' not in erros(pt, bom)


def test_algarismo_romano_nao_e_enfase():
    pt = 'Mais recente lido: IV trimestre de 2025.'
    bom = 'Most recent one read: fourth quarter of 2025.'
    assert 'CAIXA_ALTA_CAIU' not in erros(pt, bom)
