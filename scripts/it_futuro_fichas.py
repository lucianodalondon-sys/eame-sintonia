#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOS CANDIDATOS APROVADOS PARA SINAIS COMPLETOS — a consolidacao das fichas.

    python3 scripts/it_futuro_fichas.py <run_id>

LE O JOURNAL, NAO O RESULTADO DA FERRAMENTA
--------------------------------------------
O resultado de um workflow chega truncado quando e grande. Foi assim que o
artefacto IT-FUTURO-NOVOS-CANDIDATOS-V1 declarou 14 aprovados quando eram 45: eu
li os primeiros 170 mil de 996 mil caracteres e transcrevi so o que vi.

    O QUE NAO FOI LIDO NAO PODE VIRAR O QUE NAO EXISTE.

Entao a consolidacao le o journal do proprio workflow, linha a linha, e conta o
que la esta — nao o que coube na janela.

O VEREDITO E DO REFUTADOR, NAO DO AUTOR
----------------------------------------
Cada ficha foi escrita por um agente e atacada por outro, instruido a derrubar.
Quando os dois discordam, manda o refutador: quem escreve tem interesse em que a
ficha sobreviva. A autoavaliacao do autor fica gravada ao lado, para se poder ver
quantas vezes ele se deu por completo e foi rebaixado.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.expanduser(
    '~/.claude/projects/-home-user-eame-sintonia/'
    'f0de5886-eea0-5643-b2e1-e51287bd65f1/subagents/workflows')
JULGADOS = 'data/samples/IT-FUTURO-V1/IT-FUTURO-JULGADOS-V1.json'
SAIDA = 'data/samples/IT-FUTURO-V1/IT-FUTURO-SINAIS-V1.json'

DEPTOS = ['DESENVOLVIMENTO_DE_MERCADO', 'MARKETING', 'COMERCIAL_RTV',
          'CIENCIA_TECNICO', 'SUPPLY', 'REGULATORIO_PORTFOLIO']


def do_journal(run):
    caminho = os.path.join(BASE, run, 'journal.jsonl')
    fichas, vereditos = {}, {}
    for linha in open(caminho):
        r = json.loads(linha)
        if r.get('type') != 'result':
            continue
        v = r['result']
        if not isinstance(v, dict) or 'CAND_ID' not in v:
            continue
        (vereditos if 'VEREDITO' in v else fichas)[v['CAND_ID']] = v
    return fichas, vereditos


def mapa_de_acao(f):
    """Os seis departamentos, na forma que se le — e so quem tem razao."""
    saida = []
    for d in DEPTOS:
        saida.append({'DEPARTAMENTO': d,
                      'ACIONAVEL': f.get('M_%s' % d, 'NAO'),
                      'RAZAO': f.get('M_%s_RAZAO' % d, '')})
    return saida


def main(run):
    fichas, vereditos = do_journal(run)
    jul = json.load(open(os.path.join(ROOT, JULGADOS)))
    origem = {r['CAND_ID']: r for r in jul['RULED'] if r.get('CAND_ID')}

    linhas = []
    for cid in sorted(origem):
        f, v = fichas.get(cid), vereditos.get(cid)
        o = origem[cid]
        if not f:
            linhas.append({'CAND_ID': cid, 'ESTADO': 'SEM_FICHA',
                           'PORQUE': 'o agente que escreveria a ficha nao devolveu resultado',
                           'SOURCE_ID': o['SOURCE_ID'],
                           'SINAL': o['FUTURE_SIGNAL'],
                           'NOMEADO_PELO_USUARIO': o['ALREADY_PUBLISHED_AS_APPROVED']})
            continue
        estado = (v or {}).get('VEREDITO') or 'SEM_REFUTACAO'
        mapa = mapa_de_acao(f)
        sem_razao = set((v or {}).get('DEPARTAMENTOS_SEM_RAZAO') or [])
        for m in mapa:
            if m['DEPARTAMENTO'] in sem_razao and m['ACIONAVEL'] == 'SIM':
                m['ACIONAVEL'] = 'NAO'
                m['RAZAO'] = ('REBAIXADO PELO REFUTADOR: a razao nao apontava para '
                              'facto verificavel desta ficha. Original: ' + m['RAZAO'])
        linhas.append({
            'CAND_ID': cid,
            'ESTADO': estado,
            'MOTIVO_DO_VEREDITO': (v or {}).get('MOTIVO'),
            'VALOR': (v or {}).get('VALOR'),
            'VALOR_PORQUE': (v or {}).get('VALOR_PORQUE'),
            'NOMEADO_PELO_USUARIO': o['ALREADY_PUBLISHED_AS_APPROVED'],
            'SOURCE_ID': o['SOURCE_ID'],
            'TITULO': f.get('TITULO_OPERACIONAL'),
            'A_FATO': {k[2:]: f[k] for k in f if k.startswith('F_')},
            'B_CONFIANCA': {k[2:]: f[k] for k in f if k.startswith('C_')},
            'C_TEMPO_AGRONOMICO': {k[2:]: f[k] for k in f if k.startswith('T_')},
            'D_RELEVANCIA_ADAMA': {k[2:]: f[k] for k in f if k.startswith('A_')},
            'E_MAPA_DE_ACAO': mapa,
            'F_ACAO_POSSIVEL': {'CLASSE': f.get('ACAO_CLASSE'),
                                'ACOES': f.get('ACAO_LISTA'),
                                'PORQUE': f.get('ACAO_PORQUE')},
            'G_HORIZONTE': f.get('HORIZONTE'),
            'AUTOAVALIACAO_DO_AUTOR': f.get('AUTOAVALIACAO'),
            'AUTOAVALIACAO_PORQUE': f.get('AUTOAVALIACAO_PORQUE'),
            'DEFEITOS_ENCONTRADOS': (v or {}).get('DEFEITOS'),
            'CORRECOES_OBRIGATORIAS': (v or {}).get('CORRECOES_OBRIGATORIAS'),
            'JANELA_INVENTADA': (v or {}).get('JANELA_INVENTADA'),
            'UNIAO_MAQUIADA': (v or {}).get('UNIAO_MAQUIADA'),
            'PORTFOLIO_ERRADO': (v or {}).get('PORTFOLIO_ERRADO'),
            'CITACAO_CONFERIDA_PELO_REFUTADOR': (v or {}).get('CITACAO_CONFERIDA_POR_MIM'),
        })

    por_estado = Counter(x['ESTADO'] for x in linhas)
    completos = [x for x in linhas if x['ESTADO'] == 'SINAL_COMPLETO']
    parciais = [x for x in linhas if x['ESTADO'] == 'PARCIAL']
    caidos = [x for x in linhas if x['ESTADO'] == 'DERRUBADO']

    # o autor deu-se por completo e foi rebaixado quantas vezes?
    rebaixados = [x['CAND_ID'] for x in linhas
                  if x.get('AUTOAVALIACAO_DO_AUTOR') == 'SINAL_COMPLETO'
                  and x['ESTADO'] in ('PARCIAL', 'DERRUBADO')]

    ordem_valor = {'ALTO': 0, 'MEDIO': 1, 'BAIXO': 2, None: 3}
    top = sorted(completos, key=lambda x: (
        ordem_valor.get(x['VALOR'], 3),
        {'AGIR_AGORA': 0, 'PREPARAR': 1, 'MONITORAR': 2,
         'SEM_ACAO_DEMONSTRAVEL': 3}.get(x['F_ACAO_POSSIVEL']['CLASSE'], 4),
        0 if x['D_RELEVANCIA_ADAMA'].get('TEM_PORTFOLIO') == 'SIM' else 1,
    ))[:3]

    saida = {
        'DATASET': 'IT-FUTURO-SINAIS-V1',
        'LAYER': 'FUTURE INTELLIGENCE — sinais completos, com ficha operacional',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-FUTURO-JULGADOS-V1',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'cada candidato aprovado pela regua virou ficha operacional escrita por um '
                  'agente e atacada por outro, instruido a derrubar. O journal do workflow %s '
                  'e a fonte, nao o resultado da ferramenta.' % run,
        'RUN_ID': run,
        'QUEM_MANDA_NO_VEREDITO': 'o refutador. Quem escreve a ficha tem interesse em que ela '
                                  'sobreviva; a autoavaliacao do autor fica gravada ao lado.',
        'CANDIDATOS': len(linhas),
        'POR_ESTADO': dict(por_estado),
        'SINAL_COMPLETO': len(completos),
        'PARCIAL': len(parciais),
        'DERRUBADO': len(caidos),
        'AUTOR_SE_DEU_POR_COMPLETO_E_FOI_REBAIXADO': rebaixados,
        'POR_VALOR': dict(Counter(x['VALOR'] for x in linhas if x.get('VALOR'))),
        'POR_ACAO': dict(Counter(x['F_ACAO_POSSIVEL']['CLASSE'] for x in linhas
                                 if x.get('F_ACAO_POSSIVEL'))),
        'POR_HORIZONTE': dict(Counter(x['G_HORIZONTE'] for x in linhas if x.get('G_HORIZONTE'))),
        'JANELAS_INVENTADAS_APANHADAS': [x['CAND_ID'] for x in linhas
                                         if x.get('JANELA_INVENTADA') == 'SIM'],
        'UNIOES_MAQUIADAS_APANHADAS': [x['CAND_ID'] for x in linhas
                                       if x.get('UNIAO_MAQUIADA') == 'SIM'],
        'PORTFOLIOS_ERRADOS_APANHADOS': [x['CAND_ID'] for x in linhas
                                         if x.get('PORTFOLIO_ERRADO') == 'SIM'],
        'OS_TRES_DE_MAIOR_VALOR': [x['CAND_ID'] for x in top],
        'MOTIVO_DE_CADA_QUEDA_OU_PARCIAL': [
            {'CAND_ID': x['CAND_ID'], 'ESTADO': x['ESTADO'],
             'MOTIVO': x.get('MOTIVO_DO_VEREDITO') or x.get('PORQUE'),
             'DEFEITOS': x.get('DEFEITOS_ENCONTRADOS')}
            for x in linhas if x['ESTADO'] != 'SINAL_COMPLETO'],
        'ROWS': linhas,
    }
    with open(os.path.join(ROOT, SAIDA), 'w') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)

    print('CANDIDATOS      ', len(linhas))
    print('POR ESTADO      ', dict(por_estado))
    print('POR VALOR       ', saida['POR_VALOR'])
    print('POR ACAO        ', saida['POR_ACAO'])
    print('POR HORIZONTE   ', saida['POR_HORIZONTE'])
    print('JANELA INVENTADA', saida['JANELAS_INVENTADAS_APANHADAS'])
    print('UNIAO MAQUIADA  ', saida['UNIOES_MAQUIADAS_APANHADAS'])
    print('PORTFOLIO ERRADO', saida['PORTFOLIOS_ERRADOS_APANHADOS'])
    print('REBAIXADOS      ', rebaixados)
    print('TOP 3           ', saida['OS_TRES_DE_MAIOR_VALOR'])
    for x in top:
        print('   %s %-6s %-22s %s' % (x['CAND_ID'], x['VALOR'],
                                       x['F_ACAO_POSSIVEL']['CLASSE'], x['TITULO']))
    print('->', SAIDA)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'wf_e5e03bcc-487')
