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
import collections
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.expanduser(
    '~/.claude/projects/-home-user-eame-sintonia/'
    'f0de5886-eea0-5643-b2e1-e51287bd65f1/subagents/workflows')
JULGADOS = 'data/samples/IT-FUTURO-V1/IT-FUTURO-JULGADOS-V1.json'
SAIDA = 'data/samples/IT-FUTURO-V1/IT-FUTURO-SINAIS-V1.json'

DEPTOS = ['DESENVOLVIMENTO_DE_MERCADO', 'MARKETING', 'COMERCIAL_RTV',
          'CIENCIA_TECNICO', 'SUPPLY', 'REGULATORIO_PORTFOLIO']


def do_journal(runs):
    """Le UM OU MAIS journals. Dois workflows correram sobre o mesmo universo, um
    pela cabeca e outro pela cauda, porque a maquina so da dois agentes de cada
    vez e 90 agentes em fila sao horas. Onde se cruzaram ha DUAS fichas e DOIS
    vereditos independentes do mesmo candidato — e isso nao e desperdicio, e a
    unica medida de acordo que esta operacao tem:

        SE DOIS AUTORES INDEPENDENTES E DOIS REFUTADORES INDEPENDENTES CHEGAM AO
        MESMO VEREDITO, O VEREDITO NAO E DO AGENTE. E DO DOCUMENTO.

    Na sobreposicao fica o veredito MAIS SEVERO. Discordar para baixo e barato;
    discordar para cima exige provar, e nenhum dos dois provou nada ao outro.
    """
    severidade = {'SINAL_COMPLETO': 0, 'PARCIAL': 1, 'DERRUBADO': 2}
    fichas, vereditos = {}, {}
    duplicados = collections.defaultdict(list)
    for run in runs:
        caminho = os.path.join(BASE, run, 'journal.jsonl')
        if not os.path.exists(caminho):
            continue
        for linha in open(caminho):
            r = json.loads(linha)
            if r.get('type') != 'result':
                continue
            v = r['result']
            if not isinstance(v, dict) or 'CAND_ID' not in v:
                continue
            cid = v['CAND_ID']
            if 'VEREDITO' in v:
                if v.get('LI_A_FICHA_INTEIRA') is None:
                    continue   # veredito da montagem truncada: nao conta
                antigo = vereditos.get(cid)
                if antigo:
                    duplicados[cid].append((antigo['VEREDITO'], v['VEREDITO']))
                    if severidade.get(v['VEREDITO'], 3) <= severidade.get(antigo['VEREDITO'], 3):
                        continue
                vereditos[cid] = v
            else:
                fichas.setdefault(cid, v)
    # as fichas vem do artefacto, nao dos journals: e la que elas estao inteiras
    art = os.path.join(ROOT, 'data/samples/IT-FUTURO-V1/IT-FUTURO-FICHAS-V1.json')
    if os.path.exists(art):
        for f in json.load(open(art))['ROWS']:
            fichas[f['CAND_ID']] = f
    return fichas, vereditos, dict(duplicados)


def mapa_de_acao(f):
    """Os seis departamentos, na forma que se le — e so quem tem razao."""
    saida = []
    for d in DEPTOS:
        saida.append({'DEPARTAMENTO': d,
                      'ACIONAVEL': f.get('M_%s' % d, 'NAO'),
                      'RAZAO': f.get('M_%s_RAZAO' % d, '')})
    return saida


def main(runs):
    fichas, vereditos, duplicados = do_journal(runs)
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
            'REFUTADOR_LEU_A_FICHA_INTEIRA': (v or {}).get('LI_A_FICHA_INTEIRA'),
            'CAMPOS_QUE_O_REFUTADOR_NAO_VIU': (v or {}).get('CAMPOS_QUE_NAO_CONSEGUI_VER'),
            'ESTADO_DO_TEMPO_ERRADO': (v or {}).get('ESTADO_DO_TEMPO_ERRADO'),
            'HORIZONTE_ERRADO': (v or {}).get('HORIZONTE_ERRADO'),
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
                  'agente e atacada por outro, instruido a derrubar. Os journals dos workflows '
                  '%s sao a fonte, nao o resultado da ferramenta.' % ', '.join(runs),
        'RUN_IDS': list(runs),
        'JULGADOS_DUAS_VEZES': {k: v for k, v in duplicados.items()},
        'ACORDO_NA_SOBREPOSICAO': (
            '%d de %d candidatos foram julgados por dois pares independentes de autor e '
            'refutador; %d receberam o mesmo veredito das duas vezes. Na discordancia fica o '
            'veredito mais severo.' % (
                len(duplicados), len(vereditos),
                sum(1 for v in duplicados.values() for a, b in v if a == b))
            if duplicados else 'nenhum candidato foi julgado duas vezes'),
        'QUEM_MANDA_NO_VEREDITO': 'o refutador. Quem escreve a ficha tem interesse em que ela '
                                  'sobreviva; a autoavaliacao do autor fica gravada ao lado.',
        'ESTADO': ('COMPLETO' if len(completos) + len(parciais) + len(caidos) == len(linhas)
                   else 'PARCIAL — os dois workflows ainda corriam quando este ficheiro foi '
                        'escrito. %d de %d candidatos ja tem veredito; os restantes aparecem '
                        'como SEM_FICHA ou SEM_REFUTACAO, que sao estados de PROCESSAMENTO e '
                        'nao julgamentos. Nao ler as contagens abaixo como resultado final.'
                        % (len(completos) + len(parciais) + len(caidos), len(linhas))),
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
        'REFUTACAO_SOBRE_FICHA_INTEIRA': sum(
            1 for x in linhas if x.get('REFUTADOR_LEU_A_FICHA_INTEIRA') == 'SIM'),
        'VEREDITOS_TRUNCADOS_DESCARTADOS': (
            'os quatro vereditos produzidos enquanto a ficha ia cortada em 12.000 caracteres no '
            'prompt nao entram nesta contagem: foram refeitos sobre a ficha inteira'),
        'ESTADO_DO_TEMPO_ERRADO_APANHADO': [x['CAND_ID'] for x in linhas
                                            if x.get('ESTADO_DO_TEMPO_ERRADO') == 'SIM'],
        'HORIZONTE_ERRADO_APANHADO': [x['CAND_ID'] for x in linhas
                                      if x.get('HORIZONTE_ERRADO') == 'SIM'],
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
    print('FICHA INTEIRA   ', saida['REFUTACAO_SOBRE_FICHA_INTEIRA'], 'de', len(linhas))
    print('TEMPO ERRADO    ', saida['ESTADO_DO_TEMPO_ERRADO_APANHADO'])
    print('HORIZONTE ERRADO', saida['HORIZONTE_ERRADO_APANHADO'])
    print('TOP 3           ', saida['OS_TRES_DE_MAIOR_VALOR'])
    for x in top:
        print('   %s %-6s %-22s %s' % (x['CAND_ID'], x['VALOR'],
                                       x['F_ACAO_POSSIVEL']['CLASSE'], x['TITULO']))
    print('->', SAIDA)


# Tres corridas sobre o mesmo universo, e nao uma. A maquina da poucos agentes
# de cada vez e a fila e FIFO: uma corrida so poe os 45 refutadores atras das 45
# fichas, e o primeiro veredito fica a horas de distancia. Entao a cabeca, a
# cauda e o miolo foram atacados em paralelo, cada um com a sua fila propria, e
# o veredito de cada candidato sai logo a seguir a ficha dele.
#
#     PARALELIZAR PELO MEIO NAO E OTIMIZACAO. E O QUE FAZ O REFUTADOR FALAR
#     ANTES DO FIM.
#
# Onde as corridas se cruzam ha julgamento em duplicado, e isso fica medido em
# JULGADOS_DUAS_VEZES em vez de ser silenciosamente descartado.
# As corridas de FICHA e as de REFUTACAO sao agora coisas separadas, e por uma
# razao que custou caro descobrir: enquanto a ficha ia dentro do prompt do
# refutador, cortada em 12.000 caracteres, ele julgava campos que nunca recebia.
# As corridas 'wf_e5e03bcc-487', 'wf_3d483e10-13c' e 'wf_e4c83732-977' produziram
# fichas boas e quatro vereditos TRUNCADOS. As fichas ficam — via
# IT-FUTURO-FICHAS-V1 — e aqueles quatro vereditos NAO entram: foram refeitos.
RUNS_FICHA = ['wf_e5e03bcc-487', 'wf_3d483e10-13c', 'wf_e4c83732-977', 'wf_4a1ab40f-f02']
RUNS_PADRAO = ['wf_c2aac729-96e', 'wf_cc35dd81-6c5']

if __name__ == '__main__':
    main(sys.argv[1:] or RUNS_PADRAO)
