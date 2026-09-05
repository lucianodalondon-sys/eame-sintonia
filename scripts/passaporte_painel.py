#!/usr/bin/env python3
"""
PAINEL OPERACIONAL DO PASSAPORTE — a pergunta que ele existe para responder é uma só:

    "Onde estão as informações que entraram ontem?"

E a resposta tem de sair sem auditoria manual, sem abrir arquivo, sem perguntar a ninguém.

O painel é DERIVADO do log de eventos a cada execução. Ele não guarda estado próprio: o
que ele grava em `data/passaporte/PAINEL.json` são contagens, e contagem gravada envelhece
— por isso o portão de métricas a recalcula em vez de confiar nela.

    python3 scripts/passaporte_painel.py                    # o acervo inteiro
    python3 scripts/passaporte_painel.py --em 2026-08-30    # o que entrou naquele dia
    python3 scripts/passaporte_painel.py --colecao VOICE_ES
    python3 scripts/passaporte_painel.py --json
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import passaporte as pp  # noqa: E402

PAINEL = os.path.join(ROOT, 'data', 'passaporte', 'PAINEL.json')


def painel(ps, *, em=None, colecao=None):
    itens = [p for p in ps.values()
             if (em is None or str(p['CAPTURED_AT']).startswith(em))
             and (colecao is None or p['COLLECTION_ID'] == colecao)]
    divida = pp.filas_de_divida({p['ITEM_ID']: p for p in itens})
    validos = [p for p in itens if p['CLAIM_STATE'] == 'EXTRACTED']

    def n(f):
        return sum(1 for p in itens if f(p))

    coleta = {
        'TOTAL': len(itens),
        'PASS': n(lambda p: p['TRIAGE'] == 'PASS'),
        'DEFER': n(lambda p: p['TRIAGE'] == 'DEFER'),
        'REJECT': n(lambda p: p['TRIAGE'] == 'REJECT'),
        'ERROR': n(lambda p: p['TRIAGE'] == 'ERROR'),
    }
    inteligencia = {
        'CONTENT_AVAILABLE': n(lambda p: p['CONTENT_STATE'] == 'AVAILABLE'),
        'CONTENT_READ': n(lambda p: p['CONTENT_READ_STATE'] == 'READ'),
        # Varredura lexical fica numa linha PRÓPRIA. Somá-la a CONTENT_READ seria repetir,
        # em forma de painel, o erro que criou o incidente.
        'CONTENT_LEXICALLY_SCANNED_ONLY': n(
            lambda p: p['CONTENT_READ_STATE'] == 'LEXICALLY_SCANNED'),
        'CLAIMS_PENDING': n(lambda p: p['CLAIM_STATE'] == pp.PENDING),
        'IDENTITY_PENDING': n(lambda p: p['IDENTITY_STATE'] in ('NOT_PROVED', pp.UNKNOWN)),
        'GEOGRAPHY_PENDING': n(lambda p: p['GEOGRAPHY_STATE'] in ('NOT_KNOWN', pp.UNKNOWN)),
        'ROUTING_PENDING': n(lambda p: p['ROUTING_STATE'] == pp.PENDING),
    }
    consumo = {
        'VALID_INTELLIGENCE': len(validos),
        'CONSUMED_BY_1_PLUS_CAPABILITY': sum(
            1 for p in validos
            if [r for r in p['ROUTES'] if r['STATE'] == 'CONSUMED']),
        'READY_NOT_CONSUMED': sum(
            1 for p in validos if p['CONSUMPTION_STATE'] == 'READY_NOT_CONSUMED'),
        'ORPHAN_INTELLIGENCE': len(divida['ORPHAN_INTELLIGENCE']),
    }
    capacidades = Counter()
    for p in itens:
        for r in p['ROUTES']:
            if r['STATE'] == 'CONSUMED':
                capacidades[r['CAPABILITY_ID']] += 1
    return {
        'FILTRO': {'CAPTURED_AT': em or 'todas', 'COLLECTION_ID': colecao or 'todas'},
        'COLETA': coleta,
        'INTELIGENCIA': inteligencia,
        'CONSUMO': consumo,
        'CONSUMO_POR_CAPACIDADE': dict(sorted(capacidades.items())),
        'DIVIDA': {k: len(v) for k, v in divida.items()},
        'ONDE_ESTAO': dict(Counter('%s · %s' % (p['CURRENT_STAGE'], p['REASON_CODE'] or '—')
                                   for p in itens).most_common()),
        'POR_COLECAO': dict(Counter(p['COLLECTION_ID'] for p in itens).most_common()),
        'CICLO_DE_VIDA': dict(Counter(p['LIFECYCLE'] for p in itens).most_common()),
    }


def _linha(titulo, d):
    print(titulo)
    for k, v in d.items():
        print('    %-34s %s' % (k, v))


def main():
    em = colecao = None
    if '--em' in sys.argv:
        em = sys.argv[sys.argv.index('--em') + 1]
    if '--colecao' in sys.argv:
        colecao = sys.argv[sys.argv.index('--colecao') + 1]
    ps = pp.Registro.carregar().passaportes()
    r = painel(ps, em=em, colecao=colecao)
    if '--json' in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    if em is None and colecao is None:
        os.makedirs(os.path.dirname(PAINEL), exist_ok=True)
        with open(PAINEL, 'w', encoding='utf-8') as f:
            json.dump(r, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write('\n')
    print('FILTRO  captured_at=%s · coleção=%s'
          % (r['FILTRO']['CAPTURED_AT'], r['FILTRO']['COLLECTION_ID']))
    print()
    _linha('COLETA', r['COLETA'])
    _linha('INTELIGENCIA', r['INTELIGENCIA'])
    _linha('CONSUMO', r['CONSUMO'])
    _linha('DIVIDA', r['DIVIDA'])
    print()
    print('ONDE ESTÃO — estágio atual · motivo')
    for k, v in r['ONDE_ESTAO'].items():
        print('    %-58s %5d' % (k, v))
    return 0


if __name__ == '__main__':
    sys.exit(main())
