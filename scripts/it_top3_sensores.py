#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOP_3-SENSORS — o handoff determinista dos tres gatilhos instrumentados.

    python3 scripts/it_top3_sensores.py

    le    : o journal do workflow wf_27de46ef-8d2 (tres sensores + tres ataques)
    grava : data/samples/IT-FUTURO-V1/IT-TOP3-SENSORES-V1.json

O QUE ESTE FICHEIRO E, E O QUE NAO E
-------------------------------------
E o handoff que ENRIQUECE os tres cartoes prioritarios do Radar Futuro. Nunca os
substitui: nao traz veredito, nao traz estado, nao traz portfolio. Traz uma so
coisa nova — COMO SE OBSERVA NO MUNDO SE O GATILHO ACONTECEU.

    A REGUA CONTINUA DONA DA PERGUNTA. ISTO RESPONDE OUTRA.

O VEREDITO E DO ATACANTE, NAO DO AUTOR
---------------------------------------
Cada especificacao foi escrita por um agente e atacada por outro, instruido a
mostrar que ela nao e executavel. Onde discordam, manda o atacante, e a
executabilidade publicada e a CORRIGIDA. Quem escreve um sensor tem interesse em
que ele pareca executavel.

O QUE ESTE HANDOFF ADMITE CONTRA SI PROPRIO
--------------------------------------------
Dois dos tres sensores foram DERRUBADOS pelo atacante, e os tres respondem que a
transicao de estado NAO e autorizada pela regua. Publicar isso e o ponto: um
handoff que so trouxesse o que funcionou mentiria sobre o estado do radar.

    UM SENSOR QUE NAO EXISTE E INFORMACAO. UM SENSOR INVENTADO E DIVIDA.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = 'wf_27de46ef-8d2'
BASE = os.path.expanduser(
    '~/.claude/projects/-home-user-eame-sintonia/'
    'f0de5886-eea0-5643-b2e1-e51287bd65f1/subagents/workflows')
SAIDA = 'data/samples/IT-FUTURO-V1/IT-TOP3-SENSORES-V1.json'
TOP3 = ['ITFC-009', 'ITFC-016', 'ITFC-018']

CAMPOS = [
    'SIGNAL_ID', 'CURRENT_STATE', 'TRIGGER_LITERAL_ATUAL',
    'INVALIDATION_TRIGGER_LITERAL_ATUAL', 'VARIABLE_TO_WATCH', 'SOURCE_TO_WATCH',
    'SOURCE_ID_REUSADO', 'SOURCE_AUTHORITY', 'SOURCE_ACCESS', 'WATCH_CADENCE',
    'CADENCE_DERIVED_FROM', 'CURRENT_VALUE_IF_KNOWN', 'TRIGGER_CONDITION',
    'INVALIDATION_VARIABLE', 'INVALIDATION_SOURCE', 'INVALIDATION_CONDITION',
    'STATE_TRANSITION', 'INVALIDATION_TRANSITION', 'SENSORES_ADICIONAIS',
    'EXECUTABILITY', 'EXECUTABILITY_PORQUE', 'ADAPTADOR_NECESSARIO', 'EVIDENCE',
    'SEGUNDO_DONO_DETECTADO', 'NAO_SOBREVIVEU_A_OPERACIONALIZACAO',
    'WHAT_WE_STILL_DONT_KNOW',
]


def do_journal():
    sens, atq = {}, {}
    p = os.path.join(BASE, RUN, 'journal.jsonl')
    for linha in open(p):
        r = json.loads(linha)
        if r.get('type') != 'result':
            continue
        x = r['result']
        if not isinstance(x, dict) or 'SIGNAL_ID' not in x:
            continue
        (atq if 'SENSOR_AGUENTA' in x else sens)[x['SIGNAL_ID']] = x
    return sens, atq


def main():
    sens, atq = do_journal()
    linhas = []
    for cid in TOP3:
        s, a = sens.get(cid), atq.get(cid)
        if not s:
            linhas.append({'SIGNAL_ID': cid, 'ESTADO': 'SEM_SENSOR'})
            continue
        row = {k: s.get(k) for k in CAMPOS}
        # O veredito publicado e o do atacante. Onde ele corrige, a correccao manda.
        row['EXECUTABILITY_DECLARADA_PELO_AUTOR'] = s.get('EXECUTABILITY')
        row['EXECUTABILITY'] = (a or {}).get('EXECUTABILITY_CORRIGIDA') or s.get('EXECUTABILITY')
        row['ATAQUE'] = {
            'SENSOR_AGUENTA': (a or {}).get('SENSOR_AGUENTA'),
            'MOTIVO': (a or {}).get('MOTIVO'),
            'CONDICAO_E_TESTAVEL': (a or {}).get('CONDICAO_E_TESTAVEL'),
            'FONTE_E_DONA_DA_VARIAVEL': (a or {}).get('FONTE_E_DONA_DA_VARIAVEL'),
            'FONTE_EXISTE_NO_CATALOGO': (a or {}).get('FONTE_EXISTE_NO_CATALOGO'),
            'CADENCIA_E_DERIVADA_OU_CONVENIENTE': (a or {}).get('CADENCIA_E_DERIVADA_OU_CONVENIENTE'),
            'TRANSICAO_E_AUTORIZADA_PELA_REGUA': (a or {}).get('TRANSICAO_E_AUTORIZADA_PELA_REGUA'),
            'DEFEITOS': (a or {}).get('DEFEITOS'),
            'NAO_ACHEI_NAO_E_NAO_EXISTE': (a or {}).get('NAO_ACHEI_NAO_E_NAO_EXISTE'),
            'SEGUNDO_DONO': (a or {}).get('SEGUNDO_DONO'),
        }
        linhas.append(row)

    por_exec = {}
    for r in linhas:
        k = r.get('EXECUTABILITY') or 'SEM_SENSOR'
        por_exec[k] = por_exec.get(k, 0) + 1

    doc = {
        'DATASET': 'IT-TOP3-SENSORES-V1',
        'LAYER': 'RADAR FUTURO — observabilidade dos tres cartoes prioritarios',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-FUTURO-SINAIS-V1',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'tres especificacoes de observacao escritas por um agente e atacadas por '
                  'outro, sobre os gatilhos congelados; journal do workflow %s' % RUN,
        'ENRIQUECE_NAO_SUBSTITUI': (
            'este handoff nao traz veredito, estado, evidencia nem portfolio. Traz uma coisa '
            'nova por cartao: como se observa no mundo se o gatilho aconteceu. A regua continua '
            'dona da pergunta "qual e o gatilho?"'),
        'O_VEREDITO_E_DO_ATACANTE': (
            'onde autor e atacante discordam, publica-se a executabilidade CORRIGIDA. Quem '
            'escreve um sensor tem interesse em que ele pareca executavel.'),
        'NADA_FOI_REJULGADO': (
            'SINAL_COMPLETO/PARCIAL/DERRUBADO, PREPARAR/MONITORAR/AGIR_AGORA, evidencia, '
            'portfolio, vocabulario e julgamento adversarial ficam exactamente como estavam '
            'em 9560823. Este ficheiro nao altera nenhum deles.'),
        'TOP_3': TOP3,
        'POR_EXECUTABILIDADE': por_exec,
        'TRANSICAO_AUTORIZADA_PELA_REGUA': {
            r['SIGNAL_ID']: r['ATAQUE']['TRANSICAO_E_AUTORIZADA_PELA_REGUA'] for r in linhas
            if 'ATAQUE' in r},
        'O_QUE_ISTO_DIZ_SOBRE_O_RADAR': (
            'dois dos tres sensores foram derrubados pelo atacante e os tres respondem que a '
            'transicao de estado NAO e autorizada pela regua. Um handoff que so trouxesse o que '
            'funcionou mentiria sobre o estado do radar: hoje o radar sabe o que esperar, e '
            'ainda nao sabe, para estes tres, o que o autoriza a mudar de estado.'),
        'ROWS': linhas,
    }
    caminho = os.path.join(ROOT, SAIDA)
    corpo = json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True)
    with open(caminho, 'w') as f:
        f.write(corpo)
    print('SENSORES        ', len([r for r in linhas if 'ATAQUE' in r]), 'de', len(TOP3))
    print('POR EXECUTABILIDADE', por_exec)
    print('TRANSICAO AUTORIZADA', doc['TRANSICAO_AUTORIZADA_PELA_REGUA'])
    print('SHA256          ', hashlib.sha256(corpo.encode()).hexdigest())
    print('->', SAIDA)


if __name__ == '__main__':
    main()
