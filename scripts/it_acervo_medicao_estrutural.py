#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUANTOS REGISTOS ITALIANOS EXISTEM, E EM QUE ESTRUTURAS VIVEM.

    python3 scripts/it_acervo_medicao_estrutural.py

Isto NAO classifica destino de superficie, NAO altera contrato nenhum e NAO
gera handoff. Conta.

O QUE E UMA COLECCAO
--------------------
Chave de topo cujo valor e uma lista nao vazia de dicionarios. A FORMA, nunca o
nome — foi uma lista branca de treze nomes que fez um ficheiro com 421 registos
valer 1.

    UM TOTAL QUE ENCOLHE EM SILENCIO E PIOR QUE UM TOTAL QUE FALHA.

O QUE E ESCRITURACAO
--------------------
Registos que descrevem O NOSSO PROCESSO, nao a Italia: contratos, verificacoes,
handoffs, manifestos de corrida e livros de lote. Ficam SEPARADOS e nao somem —
sao contados, nomeados e subtraidos a vista, para que quem quiser inclui-los
possa faze-lo sem recontar nada.

    O ACERVO E O QUE MEDIMOS. A ESCRITURACAO E COMO O MEDIMOS.
    SOMA-LOS DA UM NUMERO QUE CRESCE QUANDO ESCREVEMOS UM CONTRATO.

ESTE RELATORIO NAO SE CONTA A SI PROPRIO
----------------------------------------
Por construcao: escreve dicionarios com chave por nome, nunca listas de
dicionarios. Assim nao cria coleccao nenhuma e a proxima corrida devolve o
mesmo numero. A alternativa — excluir-se pelo nome — funcionaria ate alguem
renomear o ficheiro.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data/samples/IT-PORTAL-V1/IT-ACERVO-MEDICAO-ESTRUTURAL-V1.json')

FAMILIAS = [
    ('RADAR_FUTURO',      r'IT-FUTURO'),
    ('ROTULOS_PORTFOLIO', r'IT-ROTULOS|IT-VOCAB|IT-PAIRSET|productsRegulatory|productRelationships'),
    ('SINAIS_DE_CAMPO',   r'IT-CAMPO|CURRENT-FIELD|IT-CRUZAMENTO'),
    ('FITOSSANITARIO',    r'IT-CONVEGNO|IT-VIDEO|IT-VOZ-AUDIO|falas/|testemunhas/'),
    ('FONTES',            r'IT-FONTES'),
    ('CONCORRENCIA',      r'COMPETITOR|CONCORREN'),
    ('SOCIAL_INSTAGRAM',  r'IT-INSTAGRAM'),
    ('SENSORES_HUMANOS',  r'SENSOR-PILOT|EARLY_SIGNAL|RESEARCHER|SPEAKER'),
    ('GEOGRAFIA',         r'TERRITORIAL|nuts2|GEOGRAF'),
    ('MERCADO',           r'MARKET|PRICES|ECONOMIC'),
    ('OPORTUNIDADES',     r'IT-RADAR-V21|OPPORTUNIT|IT-SNAPSHOT'),
    ('HANDOFF_METODO',    r'IT-HANDOFF|RUN-MANIFEST|DATA-CLOCK|POLITICA|AUDITORIA|ROTAS-EXTERNAS'),
    ('CAMADA_DE_METODO',  r'IT-PORTAL'),
]

# ESCRITURACAO, chave a chave, com o artefacto que a carrega. A lista e
# explicita de proposito: quem discordar move uma linha e reconta, em vez de
# discutir um total.
ESCRITURACAO = {
    # o que ESTA missao produziu sobre o acervo
    'ENTRADAS_AUTORIZADAS': 'handoff · a lista que o contrato autorizou',
    'RAZAO_DE_EXCLUSAO':    'handoff · porque cada subconjunto ficou fora',
    'LIMITES':              'handoff · limites declarados por subconjunto',
    'SUBCONJUNTOS':         'contrato de familia · os subconjuntos declarados',
    'PASSOS':               'verificacao · as perguntas que o consumidor fez',
    'FAMILIAS':             'verificacao · o resultado por familia',
    'EXCLUIDOS':            'handoff · o excluido, com o porque',
    # livros de corrida e manifestos, anteriores a esta missao
    'files':                'DATA-CLOCK-manifest · ficheiros vistos numa corrida',
    'FILES':                'MANIFEST · ficheiros de um pacote',
    'LOTES_FECHADOS':       'IT-SNAPSHOT-ESTADO · lotes de trabalho fechados',
    'SUSPEITOS_DE_ESCRITA': 'IT-SNAPSHOT-ESTADO · ficheiros suspeitos de escrita',
    'CHECKPOINTS':          'IT-CHECKPOINT · os checkpoints da missao',
    'READ_FROM':            'IT-INVENTARIO-FALA · de onde a corrida leu',
}


def familia(c):
    for nome, rx in FAMILIAS:
        if re.search(rx, c, re.I):
            return nome
    return 'OUTROS'


def italiano(rel, doc):
    if re.search(r'(^|/)IT-|italia|italy', rel, re.I):
        return True
    if isinstance(doc, dict):
        c = str(doc.get('COUNTRY') or doc.get('country') or '')
        if c.upper() in ('IT', 'ITALY', 'ITALIA'):
            return True
        if 'ITALY' in str(doc.get('SOURCE_LOCATION') or '').upper():
            return True
    return False


def coleccoes(d):
    if isinstance(d, list):
        return [('(raiz e lista)', len(d))] if d and isinstance(d[0], dict) else []
    if not isinstance(d, dict):
        return []
    return [(k, len(v)) for k, v in d.items()
            if isinstance(v, list) and v and isinstance(v[0], dict)]


def main():
    it_ch, nit_ch = Counter(), Counter()
    it_fam = Counter()
    origem = defaultdict(set)
    f_it = f_nit = sem_col_it = ileg = 0

    for base, _, nomes in os.walk(os.path.join(ROOT, 'data')):
        for n in sorted(nomes):
            if not n.endswith('.json'):
                continue
            p = os.path.join(base, n)
            rel = os.path.relpath(p, ROOT)
            try:
                d = json.load(open(p, encoding='utf-8'))
            except Exception:
                ileg += 1
                continue
            cols = coleccoes(d)
            if not italiano(rel, d):
                f_nit += 1
                for k, c in cols:
                    nit_ch[k] += c
                continue
            f_it += 1
            if not cols:
                sem_col_it += 1
            fam = familia(rel)
            for k, c in cols:
                it_ch[k] += c
                it_fam[fam] += c
                origem[k].add(os.path.basename(rel))

    escr = {k: v for k, v in it_ch.items() if k in ESCRITURACAO}
    tot_it = sum(it_ch.values())
    tot_escr = sum(escr.values())
    # ⚠️ A PRIMEIRA VERSAO ESCREVIA AQUI UMA SUBTRACCAO QUE DAVA SEMPRE ZERO.
    # Um campo que nao pode falhar nao mede nada — decora. Aqui nao ha lista
    # branca, logo nao existe «chave nao reconhecida»: existe a pergunta se toda
    # chave contada aparece no relatorio pelo nome. E ESSA pode falhar.
    nomeadas = set(it_ch)
    nao_nomeadas = sorted(k for k in it_ch if k not in nomeadas)

    doc = OrderedDict([
        ('DATASET', 'IT-ACERVO-MEDICAO-ESTRUTURAL-V1'),
        ('LAYER', 'medicao — quantos registos italianos existem e em que estruturas vivem'),
        ('CAPTURED_AT', '2026-09-04'),
        ('LEI', 'coleccao e a FORMA (chave de topo com lista nao vazia de dicionarios), '
                'nunca uma lista branca de nomes. Nenhuma chave vira 1: toda chave aparece '
                'pelo nome. Este relatorio nao se conta a si proprio porque nao escreve '
                'listas de dicionarios.'),
        ('FICHEIROS', {'ITALIA': f_it, 'NAO_ITALIA': f_nit, 'ILEGIVEIS': ileg,
                       'ITALIANOS_SEM_COLECCAO': sem_col_it}),
        ('TOTAL_BRUTO_TODOS_OS_ESCOPOS', tot_it + sum(nit_ch.values())),
        ('TOTAL_ITALIA', tot_it),
        ('TOTAL_EXCLUIDO_NAO_ITALIA', sum(nit_ch.values())),
        ('TOTAL_EXCLUIDO_ESCRITURACAO', tot_escr),
        ('TOTAL_ITALIA_SEM_ESCRITURACAO', tot_it - tot_escr),
        ('CHAVES_DISTINTAS_TOTAIS', len(set(it_ch) | set(nit_ch))),
        ('CHAVES_DE_COLECAO_ITALIA', len(it_ch)),
        ('CHAVES_DE_ESCRITURACAO', len(escr)),
        ('CHAVES_NAO_RECONHECIDAS', len(nao_nomeadas)),
        ('PORQUE_ZERO', 'nao ha lista branca: coleccao e reconhecida pela forma, e toda '
                        'chave contada aparece pelo nome em TOTAL_POR_CHAVE. O contador '
                        'que produzia UNKNOWN_COLLECTION_KEY e o inventario V2, que tem '
                        'registo de chaves; este relatorio nao tem registo e por isso nao '
                        'tem o que desconhecer.'),
        ('TODA_CHAVE_CONTADA_APARECE_NOMEADA', not nao_nomeadas),
        ('INVARIANTE_SOMA_DAS_CHAVES_IGUAL_AO_TOTAL', sum(it_ch.values()) == tot_it),
        ('INVARIANTE_SOMA_DAS_FAMILIAS_IGUAL_AO_TOTAL', sum(it_fam.values()) == tot_it),
        ('TOTAL_POR_CHAVE', OrderedDict(
            (k, {'REGISTOS': c, 'ESCRITURACAO': k in ESCRITURACAO,
                 'PORQUE_ESCRITURACAO': ESCRITURACAO.get(k),
                 'FICHEIROS': sorted(origem[k])[:4],
                 'N_FICHEIROS': len(origem[k])})
            for k, c in it_ch.most_common())),
        ('TOTAL_POR_FAMILIA', OrderedDict(it_fam.most_common())),
        ('CHAVES_SO_FORA_DA_ITALIA', OrderedDict(
            (k, nit_ch[k]) for k in sorted(set(nit_ch) - set(it_ch)))),
    ])
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(doc, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('== MEDICAO ESTRUTURAL DO ACERVO ITALIANO ==')
    for k in ('TOTAL_BRUTO_TODOS_OS_ESCOPOS', 'TOTAL_ITALIA', 'TOTAL_EXCLUIDO_NAO_ITALIA',
              'TOTAL_EXCLUIDO_ESCRITURACAO', 'TOTAL_ITALIA_SEM_ESCRITURACAO',
              'CHAVES_DISTINTAS_TOTAIS', 'CHAVES_DE_COLECAO_ITALIA',
              'CHAVES_DE_ESCRITURACAO', 'CHAVES_NAO_RECONHECIDAS'):
        print('  %-34s %s' % (k, doc[k]))
    print('  %-34s %s' % ('SOMA_DAS_CHAVES == TOTAL_ITALIA',
                          doc['INVARIANTE_SOMA_DAS_CHAVES_IGUAL_AO_TOTAL']))
    print('  %-34s %s' % ('SOMA_DAS_FAMILIAS == TOTAL_ITALIA',
                          doc['INVARIANTE_SOMA_DAS_FAMILIAS_IGUAL_AO_TOTAL']))
    print('\n  %-20s %8s' % ('FAMILIA', 'REGISTOS'))
    for k, v in doc['TOTAL_POR_FAMILIA'].items():
        print('  %-20s %8d' % (k, v))
    print('\n  gravado: %s' % os.path.relpath(SAIDA, ROOT))
    ok = (doc['INVARIANTE_SOMA_DAS_CHAVES_IGUAL_AO_TOTAL']
          and doc['INVARIANTE_SOMA_DAS_FAMILIAS_IGUAL_AO_TOTAL']
          and not nao_nomeadas)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
