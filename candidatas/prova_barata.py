#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PROVA BARATA — como se olha para uma fonte SEM lhe fazer uma coleta.

    py candidatas/prova_barata.py IT-T3-002 T3
    py candidatas/prova_barata.py IT-T3-002 T3 --escrever

    UMA FONTE DESCONHECIDA NAO PODE SER CONDENADA SEM SER OBSERVADA.
    E TAMBEM NAO DEVE RECEBER COLETA MASSIVA PARA DESCOBRIR SE PRESTA.

E a saida do impasse que `leis/relevancia_da_fonte.py` cria de proposito: o
portao recusa gasto sobre fonte nao avaliada, e avaliar exige olhar. Se a
unica maneira de olhar fosse coletar, o portao seria uma porta trancada com a
chave do lado de dentro.

    CANDIDATA -> PROVA BARATA -> AMOSTRA PEQUENA REAL
              -> DECISAO DE RELEVANCIA -> PROMOVE / RECUSA / FICA NAO_SEI

⚠️ E A PROVA NAO DECIDE. ELA OBSERVA.
--------------------------------------
Esta ferramenta escreve uma OBSERVACAO, nunca uma decisao. A separacao nao e
cerimonia: uma sonda que decidisse sozinha transformaria «a amostra que eu
consegui apanhar» em «o que a fonte e», e a primeira amostra magra condenava
a fonte para sempre com ar de medicao.

    CAN DO != DID DO.  OBSERVAR != JULGAR.  AMOSTRA != POPULACAO.

Quem decide e uma pessoa, escrevendo `leis/relevancia_da_fonte.Decisao` com
esta observacao como `EVIDENCIA`.

OS DOIS DEGRAUS, E O PRIMEIRO E DE GRACA
-----------------------------------------
    DEGRAU 0 · O ACERVO     o que esta casa JA guardou desta fonte.
                            Zero rede, zero dinheiro, zero risco.
    DEGRAU 1 · A SONDA      uma ida ao mundo, limitada por teto, por rota
                            gratuita e por uma so passagem.

O degrau 0 vem primeiro porque a COL-LAW-053 ja o manda:

    O ACERVO E CAPITAL PARADO. CONSULTA-SE ANTES DE COLETAR.
    NAO SE COLETA PARA DESCOBRIR O QUE JA SE SABE.

Medido nesta arvore: 15 fontes italianas tem amostra real em
`data/samples/IT-SOURCE-SAMPLES/`, e 22 fichas do atlas carregam
`real_example`. Para essas, a prova barata custa zero e nao sai da maquina.

O TETO NAO E UM CONSELHO
-------------------------
`TETO_DE_UNIDADES` e duro. Uma sonda sem teto e uma coleta com outro nome, e
seria exactamente o gasto que o portao existe para impedir. O teto entra na
observacao escrita, para que ninguem leia «3 unidades» como «e isto que a
fonte tem».

    AMOSTRA PEQUENA NAO E POPULACAO. O DENOMINADOR VAI JUNTO.

E NAO HA ROTA PAGA AQUI, EM CIRCUNSTANCIA NENHUMA
--------------------------------------------------
    PROVA_BARATA_NUNCA_PAGA = True

Uma avaliacao paga pode existir — mas nao por esta porta, e nao por omissao.
Exige orcamento, teto, motivo, autorizacao humana, numero maximo de corridas e
condicao de paragem, e nada disso cabe num argumento de linha de comando.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import relevancia_da_fonte as rel  # noqa: E402

FONTES_MEDIDAS = os.path.join('system-map', 'data', 'sources.generated.json')
ACERVO_IT = os.path.join('data', 'samples', 'IT-SOURCE-SAMPLES')
SAIDA = os.path.join('data', 'derivados', 'PROVAS-BARATAS-DE-FONTE-V1.json')

VERSAO_DA_PROVA = '1'

# ── O TETO ──────────────────────────────────────────────────────────────────
# Tres unidades. Nao e um numero bonito: e o menor numero que ainda mostra
# VARIACAO — com uma so nao se distingue «a fonte publica isto» de «a fonte
# publicou isto uma vez».
TETO_DE_UNIDADES = 3
UMA_PASSAGEM_SO = True
PROVA_BARATA_NUNCA_PAGA = True

# Os degraus, e o que cada um custa.
DEGRAU_ACERVO = 'ACERVO'
DEGRAU_SONDA = 'SONDA_LIMITADA'


class ProvaRecusada(Exception):
    """A prova nao corre. Para-se, e o motivo fica escrito."""


def agora() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _fontes(raiz=RAIZ) -> list:
    caminho = os.path.join(raiz, FONTES_MEDIDAS)
    if not os.path.isfile(caminho):
        return []
    with open(caminho, encoding='utf-8') as f:
        S = json.load(f)
    return list(S.get('SOURCES') or []) + list(S.get('MASTER_ITALIANO') or [])


def ficha(source_id: str, raiz=RAIZ):
    """→ a ficha da fonte no cadastro unico, ou None.

    ⚠️ NAO SE FABRICA FONTE AQUI. Se o identificador nao esta no cadastro, a
    prova recusa — porque sondar um id que ninguem levantou criaria uma fonte
    pela porta das traseiras, sem ficha, sem exemplo real e sem territorio.
    """
    sid = rel.conferir_source_id(source_id)
    for f in _fontes(raiz):
        if f.get('source_id') == sid:
            return f
    return None


def _unidades_no_acervo(source_id: str, raiz=RAIZ) -> list:
    """O que esta casa JA tem desta fonte, em disco. Zero rede."""
    pasta = os.path.join(raiz, ACERVO_IT, source_id)
    if not os.path.isdir(pasta):
        return []
    return sorted(n for n in os.listdir(pasta)
                  if not n.startswith('.')
                  and not n.endswith('.headers.txt')
                  and n != 'MANIFEST.json')


def observar(source_id: str, proposito: str, raiz=RAIZ,
             teto: int = TETO_DE_UNIDADES) -> dict:
    """DEGRAU 0 — o que ja temos desta fonte. → uma OBSERVACAO, nunca decisao.

    Ela responde «o que da para olhar sem gastar nada», e nada mais. O campo
    `DECISAO` sai sempre `NAO_TOMADA`, com o motivo por extenso — para que
    ninguem, daqui a seis meses, leia este ficheiro como um veredito.
    """
    sid = rel.conferir_source_id(source_id)
    alvo = str(proposito or '').strip()
    if not alvo:
        raise ProvaRecusada(
            'PROPOSITO ausente. Uma prova sem proposito produz uma observacao '
            'que serve para todos os universos — que e o defeito que a lei da '
            'relevancia existe para impedir.')

    f = ficha(sid, raiz)
    if f is None:
        raise ProvaRecusada(
            'FONTE «%s» NAO ESTA NO CADASTRO UNICO (%s). Sondar um '
            'identificador que ninguem levantou seria criar uma fonte pela '
            'porta das traseiras. Entre pela fila: candidatas/fonte_nova.py'
            % (sid, FONTES_MEDIDAS))

    unidades = _unidades_no_acervo(sid, raiz)
    vistas = unidades[:teto]
    exemplo = str(f.get('real_example') or f.get('prova') or '').strip()

    if vistas:
        o_que_deu = 'ACERVO_LOCAL'
        quanto = ('%d unidade(s) olhada(s), de %d que esta casa guarda desta '
                  'fonte. TETO = %d.' % (len(vistas), len(unidades), teto))
    elif exemplo:
        o_que_deu = 'EXEMPLO_REAL_NA_FICHA'
        quanto = ('nenhuma unidade em disco; a ficha guarda um exemplo real '
                  'escrito. AMOSTRA = 1 relato, nao 1 unidade.')
    else:
        # ⚠️ E ISTO NAO E «A FONTE NAO PRESTA». E «esta casa ainda nao olhou».
        o_que_deu = 'NADA_NO_ACERVO'
        quanto = ('esta casa nao guardou nada desta fonte. Isto e ausencia de '
                  'observacao, NAO observacao de ausencia (COL-LAW-035).')

    return {
        'SCHEMA': 'sintonia.prova-barata-de-fonte/1',
        'SOURCE_ID': sid,
        'PROPOSITO': alvo,
        'DEGRAU': DEGRAU_ACERVO,
        'CUSTO_USD': 0,                  # MEDIDO: nao saiu da maquina
        'REDE_USADA': False,
        'TETO_DE_UNIDADES': teto,
        'UMA_PASSAGEM_SO': UMA_PASSAGEM_SO,
        'O_QUE_DEU': o_que_deu,
        'QUANTO': quanto,
        'UNIDADES_OLHADAS': vistas,
        'UNIDADES_NO_ACERVO': len(unidades),
        'EXEMPLO_REAL_NA_FICHA': exemplo[:400],
        # O territorio DECLARADO vai junto como CONTEXTO, e esta marcado como
        # tal. Ele nao e a resposta: ver `provas/candidatos_tematicos.py`.
        'TERRITORIO_DECLARADO_NA_FICHA': f.get('territory'),
        'AVISO_DECLARED': ('DECLARED != OBSERVED: o territorio da ficha e uma '
                           'afirmacao de quem a escreveu, nunca uma avaliacao.'),
        # ⚠️ O CAMPO MAIS IMPORTANTE DESTE FICHEIRO.
        'DECISAO': 'NAO_TOMADA',
        'PORQUE_NAO_TOMADA': (
            'uma prova barata OBSERVA; nao julga. Transformar a amostra que '
            'se conseguiu apanhar em «o que a fonte e» faria a primeira '
            'amostra magra condenar a fonte com ar de medicao. A decisao '
            'escreve-se em %s, com esta observacao como EVIDENCIA.' % rel.LIVRO),
        'VERSAO_DA_PROVA': VERSAO_DA_PROVA,
        'OBSERVADO_EM': agora(),
    }


def sondar(source_id: str, proposito: str, custo_da_rota=None, **_k) -> dict:
    """DEGRAU 1 — a ida ao mundo. RECUSA rota paga, sempre, sem excepcao.

    ⚠️ E RECUSA TAMBEM O QUE NAO SABE QUANTO CUSTA. «NAO SEI» nao e gratuito:
    o custo de errar aqui e uma corrida paga que ninguem autorizou.

    O TRANSPORTE CANONICO NAO VIVE NESTA ARVORE. As rotas sociais passam pelo
    executor canonico do SINTONIA SCRAP, e chamar um adapter directamente para
    contornar isso seria criar um segundo caminho de coleta — exactamente o que
    a COL-LAW-011 proibe. Enquanto o executor nao estiver aqui, esta funcao diz
    que nao consegue, em vez de improvisar.

        NAO CONSEGUIR OLHAR != OLHAR E NAO VER NADA.
    """
    rel.conferir_source_id(source_id)
    if not rel.custo_e_gratuito(custo_da_rota):
        raise ProvaRecusada(
            'ROTA PAGA (ou de custo nao declarado: «%s») NUNCA entra pela '
            'prova barata. Uma avaliacao paga exige orcamento, teto, motivo, '
            'autorizacao humana, numero maximo de corridas e condicao de '
            'paragem — e nada disso cabe num argumento de linha de comando.'
            % custo_da_rota)
    raise ProvaRecusada(
        'SONDA NAO DISPONIVEL NESTA ARVORE: o executor canonico do SINTONIA '
        'SCRAP nao vive aqui, e chamar um adapter directamente criaria um '
        'segundo caminho de coleta (COL-LAW-011). Use o DEGRAU 0 (o acervo), '
        'que ja da amostra real sem sair da maquina. Isto e ERRO de '
        'avaliacao — NAO e uma fonte que nao serve.')


def escrever(observacoes: list, raiz=RAIZ) -> int:
    """Junta ao ficheiro das provas. Append-only, como todo livro desta casa."""
    caminho = os.path.join(raiz, SAIDA)
    d = {'SCHEMA': 'sintonia.provas-baratas-de-fonte/1',
         'LEI': ('uma prova barata OBSERVA e nao decide. A decisao de '
                 'relevancia vive em %s.' % rel.LIVRO),
         'PROVAS': []}
    if os.path.isfile(caminho):
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
    d.setdefault('PROVAS', []).extend(observacoes)
    d['TOTAL'] = len(d['PROVAS'])
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
    return len(d['PROVAS'])


def main() -> int:
    ap = argparse.ArgumentParser(
        description='Olha para uma fonte sem lhe fazer uma coleta.',
        epilog='Isto NAO decide relevancia. Produz a observacao com que '
               'alguem decide.')
    ap.add_argument('source_id')
    ap.add_argument('proposito', help='o territorio: T1..T13')
    ap.add_argument('--teto', type=int, default=TETO_DE_UNIDADES)
    ap.add_argument('--escrever', action='store_true',
                    help='junta a observacao a %s' % SAIDA)
    a = ap.parse_args()

    try:
        o = observar(a.source_id, a.proposito, teto=a.teto)
    except (ProvaRecusada, rel.SourceIdInvalido) as e:
        print('RECUSADA: %s' % e, file=sys.stderr)
        return 1

    print('PROVA BARATA · %s para «%s»' % (o['SOURCE_ID'], o['PROPOSITO']))
    print('  degrau  : %s · rede=%s · custo=US$ %s'
          % (o['DEGRAU'], o['REDE_USADA'], o['CUSTO_USD']))
    print('  o que deu: %s' % o['O_QUE_DEU'])
    print('  quanto   : %s' % o['QUANTO'])
    for u in o['UNIDADES_OLHADAS']:
        print('      · %s' % u)
    print('  DECISAO : %s — %s' % (o['DECISAO'], o['PORQUE_NAO_TOMADA']))
    if a.escrever:
        print('  escrito : %s (%d provas)' % (SAIDA, escrever([o])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
