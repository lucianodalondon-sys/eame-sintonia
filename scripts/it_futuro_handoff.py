#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O HANDOFF DO RADAR FUTURO — o que a Linha B recebe, e nada mais.

    python3 scripts/it_futuro_handoff.py [--source-head <sha>]

POR QUE ESTE ARQUIVO EXISTE
----------------------------
O congelamento diz o que os 45 sao. O contrato de superficie diz o que a tela
pode fazer com eles. Falta a terceira coisa: um pacote que a Linha B possa
consumir sem abrir nenhum dos dois e sem decidir nada.

    UM HANDOFF QUE OBRIGA O RECEPTOR A RECALCULAR NAO E HANDOFF:
    E O TRABALHO OUTRA VEZ, COM OUTRO DONO.

Este script NAO julga, NAO promove estado, NAO recalcula o TOP_3 e NAO consulta
a rota viva «temos algo para X?», que esta com defeito conhecido. Ele so
EMPACOTA o que ja esta congelado, e carimba os hashes do que leu para que o
receptor possa provar que recebeu o mesmo que foi congelado.

A identidade aqui nao e um BUILD_ID inventado: e o SHA do commit mais os hashes
dos artefactos consumidos. Fabricar um build so para ter um campo bonito seria
dar identidade a uma coisa que nao a tem.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, 'data', 'samples', 'IT-FUTURO-V1')
SAIDA = os.path.join(DIR, 'IT-FUTURO-HANDOFF-LINHA-B-V1.json')

CONSUMIDOS = ('IT-FUTURO-SINAIS-V1.json', 'IT-FUTURO-FICHAS-V1.json',
              'IT-FUTURO-JULGADOS-V1.json', 'IT-FUTURO-CONTRATO-SUPERFICIE-V1.json')


def _sha(nome):
    with open(os.path.join(DIR, nome), 'rb') as f:
        return 'sha256:' + hashlib.sha256(f.read()).hexdigest()[:32]


def _abre(nome):
    return json.load(open(os.path.join(DIR, nome), encoding='utf-8'))


def cabeca(argv):
    if '--source-head' in argv:
        return argv[argv.index('--source-head') + 1]
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None


def main():
    C = _abre('IT-FUTURO-CONTRATO-SUPERFICIE-V1.json')
    S = {r['CAND_ID']: r for r in _abre('IT-FUTURO-SINAIS-V1.json')['ROWS']}
    F = {r['CAND_ID']: r for r in _abre('IT-FUTURO-FICHAS-V1.json')['ROWS']}
    J = {r['CAND_ID']: r for r in _abre('IT-FUTURO-JULGADOS-V1.json')['RULED']
         if r.get('CAND_ID')}

    ev = C['ESTADOS_DE_VEREDITO']
    dep = C['DEPENDENCIA_DE_PORTFOLIO']
    rx = re.compile(dep['ROTA_QUEBRADA']['REGEX_SOBRE_TARGET_E_CROP'], re.I)

    render, fora, lim = [], [], {}
    por_acao = {}
    for cid in sorted(S):
        s, f, j = S[cid], F[cid], J[cid]
        if not ev[s['ESTADO']]['RENDERIZAVEL']:
            fora.append({'ID': cid, 'ESTADO': s['ESTADO'],
                         'PORQUE': ev[s['ESTADO']]['PORQUE'],
                         'ONDE_FICA': ev[s['ESTADO']]['CONTEXTO']})
            continue
        pair = str(j.get('ADAMA_PAIR_EXISTS'))
        quebrada = bool(rx.search(str(j.get('TARGET', '')) + str(j.get('CROP', ''))))
        classe = ('DECLARADO_UNKNOWN' if pair == 'UNKNOWN' else
                  ('EVIDENCIA_CONGELADA' if (pair == 'YES' and quebrada) else
                   ('CEGO_SEM_CLASSE' if (pair == 'NO' and quebrada) else
                    ('MEDIDO_EXISTE' if pair == 'YES' else 'MEDIDO_ZERO'))))
        acao = f.get('ACAO_CLASSE')
        por_acao[acao] = por_acao.get(acao, 0) + 1
        render.append(cid)

        lac = {}
        if s['ESTADO'] == 'PARCIAL':
            for campo in ev['PARCIAL']['LACUNAS_QUE_TEM_DE_APARECER']:
                v = s.get(campo, f.get(campo))
                lac[campo] = v
        entrada = {
            'ESTADO': s['ESTADO'],
            'ACAO': acao,
            'AVISO_OBRIGATORIO': ev[s['ESTADO']].get('AVISO_OBRIGATORIO'),
            'PORTFOLIO': {
                'CLASSE': classe,
                'ADAMA_PAIR_EXISTS': pair,
                'ROTA_VIVA_PERMITIDA': classe in ('MEDIDO_EXISTE', 'MEDIDO_ZERO'),
                'O_CARTAO_PODE': dep['CLASSES'][classe]['cartao'],
            },
        }
        if lac:
            entrada['LACUNAS'] = lac
        lim[cid] = entrada

    limitados = [c for c, v in lim.items()
                 if not v['PORTFOLIO']['ROTA_VIVA_PERMITIDA']]

    doc = {
        'DATASET': 'IT-FUTURO-HANDOFF-LINHA-B-V1',
        'LAYER': 'RADAR FUTURO — o pacote que a Linha B consome',
        'LEI': 'este handoff NAO recalcula julgamento nenhum. Empacota o que ja '
               'esta congelado. O receptor nao precisa de abrir o congelamento '
               'nem o contrato para montar a tela, e nao pode decidir nada que '
               'nao esteja aqui.',
        'UPSTREAM_CHECKPOINT': cabeca(sys.argv),
        'SOURCE_HEAD': cabeca(sys.argv),
        # O contrato mestre chama-lhe CONTRACT_VERSION, e os handoffs das outras
        # tres familias tambem. Dois nomes para o mesmo campo obrigam o receptor
        # a conhecer os dois — e um receptor que tem de conhecer as duas versoes
        # do nome ja esta a adivinhar.
        'CONTRACT_VERSION': C['DATASET'],
        'CONGELAMENTO': C['CONGELAMENTO'],
        'COLLECTION': C['COLECAO_CANONICA']['PREFIXO'],
        'TOTAL': len(S),
        'RENDERABLE': len(render),
        'DROPPED': len(fora),
        'ACT_NOW': por_acao.get('AGIR_AGORA', 0),
        'PREPARE': por_acao.get('PREPARAR', 0),
        'WATCH': por_acao.get('MONITORAR', 0),
        'PORTFOLIO_LIMITED': len(limitados),
        'TOP_3': C['TOP_3']['VALOR'],
        'HASHES_DOS_ARTEFACTOS_CONSUMIDOS': {n: _sha(n) for n in CONSUMIDOS},
        'POPULACAO_QUE_NAO_ENTRA': C['COLECAO_CANONICA']['NAO_E_ESTA_COLECAO'],
        'REGRAS_DE_TOM': {
            'PREPARAR': C['ESTADOS_TEMPORAIS']['PREPARAR']['LEI'],
            'MONITORAR': C['ESTADOS_TEMPORAIS']['MONITORAR']['LEI'],
            'AGIR_AGORA': C['ESTADOS_TEMPORAIS']['AGIR_AGORA']['LEI'],
        },
        'CAMPOS_OBRIGATORIOS_DO_CARTAO': C['CAMPOS_OBRIGATORIOS_DO_CARTAO'],
        'RENDERIZAVEIS': render,
        'EXCLUIDOS': fora,
        'PORTFOLIO_LIMITED_IDS': sorted(limitados),
        'LIMITACOES_POR_SINAL': lim,
    }
    json.dump(doc, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('== HANDOFF · RADAR FUTURO -> LINHA B ==')
    for k in ('UPSTREAM_CHECKPOINT', 'CONTRACT_VERSION', 'COLLECTION',
              'TOTAL', 'RENDERABLE', 'DROPPED', 'ACT_NOW', 'PREPARE', 'WATCH',
              'PORTFOLIO_LIMITED'):
        print('  %-26s %s' % (k, doc[k]))
    print('  %-26s %s' % ('TOP_3', doc['TOP_3']))
    print('  %-26s %s' % ('EXCLUIDO', [x['ID'] for x in fora]))
    print('  hashes:')
    for n, h in doc['HASHES_DOS_ARTEFACTOS_CONSUMIDOS'].items():
        print('    %-42s %s' % (n, h))
    print('  gravado: %s' % os.path.relpath(SAIDA, ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
