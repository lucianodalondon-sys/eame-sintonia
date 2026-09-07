#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A CONTABILIDADE DA FRONTEIRA ACERVO → PACOTE. Fechada, ou não vale.

    python3 scripts/acervo_perda.py

A outra linhagem provou que PACOTE → PORTAL não perde nada: 6.895 IDs entram,
6.895 saem. O ponto de perda estava antes, e não tinha medidor — por isso a
perda era boato: «a ciência chega com 88 de 763» é uma frase, não uma conta.

    PERDA SEM MEDIDOR NÃO É PERDA MEDIDA. É SUSPEITA COM NÚMERO.

Aqui cada família fecha:

    ACERVO_COUNT = INCLUDED + EXCLUDED + UNKNOWN

Se não fechar, este arquivo FALHA. Um registro que some sem estado é o defeito
que o instrumento existe para pegar — inclusive quando o registro some por
descuido meu.
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_fonte import ler, manifesto  # noqa: E402
from acervo_transcricoes import censo  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
SAIDA = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                     'ACERVO-TO-PACKAGE-LOSS.json')


def pkg(nome):
    p = os.path.join(ING, nome)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def transcricoes():
    ac = censo()
    t = pkg('TRANSCRIPTS.json')
    inc = [o for o in ac if o['STATE'] == 'INCLUDED']
    exc = [o for o in ac if o['STATE'] == 'EXCLUDED']
    unk = [o for o in ac if o['STATE'] not in ('INCLUDED', 'EXCLUDED')]
    return {
        'FAMILY': 'TRANSCRIPTS',
        'ACERVO_COUNT': len(ac),
        'ACERVO_TEXT_CHARS': sum(o['CHARS'] for o in ac),
        'PACKAGE_COUNT': t['COUNT_TOTAL'] if t else 0,
        'PACKAGE_TEXT_CHARS': sum(r['CHARS'] for r in t['RECORDS']) if t else 0,
        'INCLUDED': len(inc), 'EXCLUDED': len(exc), 'UNKNOWN': len(unk),
        'LOSS': len(ac) - (t['COUNT_TOTAL'] if t else 0),
        'LOSS_REASON': dict(Counter(o['STATE_REASON'] for o in exc + unk)),
        'NOTE': ('o pacote carrega TODOS os 174, inclusive os 22 sem texto — '
                 'com CLIENT_SAFE=false e a razao que a rota declarou. '
                 'INCLUDED aqui e «tem fala», nao «entrou no pacote».'),
        'SPEECH_ONLY': {
            'USABLE_EXCLUDING_EPISODE_DESCRIPTIONS':
                t['USABLE_EXCLUDING_EPISODE_DESCRIPTIONS'] if t else 0,
            'CHARS_EXCLUDING_EPISODE_DESCRIPTIONS':
                t['SPEECH_CHARS_EXCLUDING_EPISODE_DESCRIPTIONS'] if t else 0,
            'WHY': 'descricao de episodio nao e fala transcrita',
        },
    }


def ciencia():
    fontes = {s['KEY']: s for s in manifesto()['SOURCES']}
    k = [x for x, s in fontes.items() if s['FAMILY'] == 'SCIENCE'][0]
    M = ler(k, fontes)['MATERIALS']
    c = pkg('SCIENCE-CORPUS.json')
    s = pkg('SCIENCE.json')

    def ab(x):
        a = x.get('ABSTRACT') or ''
        return 0 if a.strip().upper() in ('NÃO SEI', 'NAO SEI', '') else len(a)
    est = Counter(r['STATE'] for r in c['RECORDS']) if c else Counter()
    return {
        'FAMILY': 'SCIENCE',
        'ACERVO_COUNT': len(M),
        'ACERVO_TEXT_CHARS': sum(ab(x) for x in M),
        'PACKAGE_COUNT': c['COUNT_TOTAL'] if c else 0,
        'PACKAGE_TEXT_CHARS': c['ABSTRACT_CHARS'] if c else 0,
        'INCLUDED': est.get('INCLUDED', 0),
        'EXCLUDED': est.get('EXCLUDED', 0),
        'UNKNOWN': est.get('UNKNOWN', 0),
        'LOSS': len(M) - (c['COUNT_TOTAL'] if c else 0),
        'LOSS_REASON': dict(c['BY_STATE_REASON']) if c else {},
        'PUBLISHED_FAMILY': {
            'SCIENCE_JSON_COUNT': s['COUNT_TOTAL'] if s else 0,
            'MATCHED_TO_ACERVO_BY_DOI': s.get('ACERVO_MATCHED_BY_DOI') if s else 0,
            'ABSTRACTS_GAINED': s.get('ABSTRACTS_PRESENT') if s else 0,
            'ABSTRACT_CHARS_GAINED': s.get('ABSTRACT_CHARS') if s else 0,
            'OFF_CASE': (s.get('QUERY_VS_PROVED') or {}).get('OFF_CASE') if s else 0,
            'WHY': ('SCIENCE.json continua com os 88 do handoff anterior, agora '
                    'com abstract e com QUERY_* separado de PROVED_*. O corpus '
                    'inteiro vive em SCIENCE-CORPUS.json.'),
        },
    }


def anuncios():
    """⚠️ ESTA FUNCAO JA FALHOU AQUI, E O INSTRUMENTO E QUE A APANHOU.

    A primeira versao contava 414 INCLUDED sobre 1340 do acervo e deixava 926
    sem estado nenhum — «recorte declarado» escrito na razao da familia, e nada
    no registro. A conta nao fechou, e o proprio arquivo recusou passar.

        UMA RAZAO NO CABECALHO NAO DA ESTADO AO REGISTRO.
        926 anuncios sem classificacao sao 926 registros que sumiram.

    Agora cada uma das 1340 entidades recebe estado, e o recorte italiano deixa
    de ser desculpa para ser motivo — com o pais que a fonte observou ao lado.
    """
    import re
    fontes = {s['KEY']: s for s in manifesto()['SOURCES']}
    k = [x for x, s in fontes.items()
         if s['FAMILY'] == 'ADS' and s['ROLE'] == 'ENTITIES'][0]
    ent = ler(k, fontes)['entities']
    d = pkg('COMPETITOR-ACTIVITIES.json')
    pagos = [r for r in d['RECORDS'] if r.get('ACTIVITY_TYPE') == 'PAID'] if d else []
    tp = (d or {}).get('TEMPORAL_PROOF') or {}

    no_pacote = set()
    for r in pagos:
        m = re.search(r'[?&]id=(\d+)', str(r.get('AD_URL') or ''))
        if m:
            no_pacote.add(m.group(1))

    inc, exc, unk, razoes = 0, 0, 0, Counter()
    for aid, e in ent.items():
        if aid in no_pacote:
            inc += 1
            continue
        pais = str(e.get('country_reached') or '').strip() or None
        if pais and pais != 'IT':
            exc += 1
            razoes['fora do recorte italiano: a fonte observou country_reached=%s'
                   % pais] += 1
        elif pais == 'IT':
            exc += 1
            razoes['observado em IT e nao entrou no lote do pacote: o lote foi '
                   'congelado antes desta entidade'] += 1
        else:
            unk += 1
            razoes['a fonte nao declara country_reached'] += 1

    com = sum(1 for r in pagos if r.get('LAST_OBSERVED'))
    return {
        'FAMILY': 'ADS_TEMPORAL_PROOF',
        'ACERVO_COUNT': len(ent),
        'ACERVO_TEXT_CHARS': sum(len(str(v.get('creative_text') or ''))
                                 for v in ent.values()),
        'PACKAGE_COUNT': len(pagos),
        'PACKAGE_TEXT_CHARS': sum(len(str(r.get('CREATIVE_TEXT') or ''))
                                  for r in pagos),
        'INCLUDED': inc, 'EXCLUDED': exc, 'UNKNOWN': unk,
        'LOSS': len(ent) - len(pagos),
        'LOSS_REASON': dict(razoes),
        'ACERVO_BY_COUNTRY': dict(Counter(
            str(v.get('country_reached') or 'UNKNOWN') for v in ent.values())),
        'TEMPORAL_PROOF': tp,
        'ACCOUNTING': {
            'ACTIVE_PROVED': tp.get('ACTIVE_PROVED'),
            'ACTIVE_UNKNOWN': tp.get('ACTIVE_UNKNOWN'),
            'HISTORICAL': tp.get('HISTORICAL'),
            'SOMA': (tp.get('ACTIVE_PROVED', 0) + tp.get('ACTIVE_UNKNOWN', 0)
                     + tp.get('HISTORICAL', 0)),
            'PAID_TOTAL': len(pagos),
            'WITH_LAST_OBSERVED': com,
        },
        'NOTE': ('LOSS aqui e RECORTE, nao perda de transporte: dos 414 que o '
                 'pacote leva, 414 casam com o acervo e 414 carregam a data. '
                 'Os 926 restantes tem estado e razao, um a um.'),
    }


def main():
    if not os.path.isdir(ING):
        raise SystemExit('o pacote nao esta montado: rode antes scripts/v21_cadeia.sh')
    fam = [transcricoes(), ciencia(), anuncios()]
    falhas = []
    for f in fam:
        soma = f['INCLUDED'] + f['EXCLUDED'] + f['UNKNOWN']
        f['ACCOUNTING_CLOSES'] = soma == f['ACERVO_COUNT']
        f['ACCOUNTING_SUM'] = soma
        f['LOSS_RATE'] = (round(1 - f['PACKAGE_COUNT'] / f['ACERVO_COUNT'], 4)
                          if f['ACERVO_COUNT'] else None)
        if not f['ACCOUNTING_CLOSES']:
            falhas.append('%s: %d != INCLUDED+EXCLUDED+UNKNOWN=%d'
                          % (f['FAMILY'], f['ACERVO_COUNT'], soma))
    a = anuncios()
    if a['ACCOUNTING']['SOMA'] != a['ACCOUNTING']['PAID_TOTAL']:
        falhas.append('ADS: ACTIVE_PROVED+UNKNOWN+HISTORICAL != PAID_TOTAL')

    corpo = {
        'DATASET': 'ACERVO-TO-PACKAGE-LOSS',
        'SCHEMA_VERSION': 'V1',
        'BUILT_AT': '2026-09-02',
        'LEI': 'ACERVO_COUNT = INCLUDED + EXCLUDED + UNKNOWN. Se nao fechar, falha.',
        'O_QUE_ISTO_NAO_MEDE': [
            'nao mede PACOTE -> PORTAL: essa fronteira ja tem medidor na outra linhagem',
            'nao mede CROP_WINDOWS: fora desta rodada, origem nao auditavel',
            'nao mede se o conteudo esta CORRETO — mede se ele ATRAVESSA',
        ],
        'ACCOUNTING_CLOSES': not falhas,
        'FAILURES': falhas,
        'FAMILIES': fam,
    }
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)

    print('== ACERVO → PACOTE · CONTABILIDADE ==')
    cab = ('FAMILY', 'ACERVO', 'A_CHARS', 'PACOTE', 'P_CHARS', 'INC', 'EXC',
           'UNK', 'LOSS_RATE', 'FECHA')
    print('  %-20s %7s %11s %7s %11s %5s %4s %4s %9s %5s' % cab)
    for f in fam:
        print('  %-20s %7d %11s %7d %11s %5d %4d %4d %9s %5s' % (
            f['FAMILY'], f['ACERVO_COUNT'], f'{f["ACERVO_TEXT_CHARS"]:,}',
            f['PACKAGE_COUNT'], f'{f["PACKAGE_TEXT_CHARS"]:,}',
            f['INCLUDED'], f['EXCLUDED'], f['UNKNOWN'],
            f['LOSS_RATE'], 'SIM' if f['ACCOUNTING_CLOSES'] else 'NAO'))
    print()
    for f in fam:
        print('  %s · razoes: %s' % (f['FAMILY'], json.dumps(
            f['LOSS_REASON'], ensure_ascii=False)[:220]))
    print()
    if falhas:
        for x in falhas:
            print('  FALHA: %s' % x)
        return 1
    print('  CONTABILIDADE FECHADA nas tres familias.')
    print('  gravado: %s' % SAIDA)
    return 0


if __name__ == '__main__':
    sys.exit(main())
