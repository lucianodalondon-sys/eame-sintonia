#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A FILA DE CAUDA LONGA — OS 46 PARES QUE O ROTULO AUTORIZA E O PARSER NAO LE.

    python3 scripts/it_divida_fila.py

POR QUE UMA FILA, E NAO UMA CAMPANHA
-------------------------------------
Os 46 nao sao um bloco. Zera-los seria perseguir um numero; e a razao por que
existem e sempre a mesma familia de defeitos estruturais, ja diagnosticada e ja
nomeada. O que muda entre eles e o VALOR DO QUE SE DESTRAVA — e isso nunca foi
medido, so contado.

    UM NUMERO SEM EXEMPLO NAO VALE. UMA FILA SEM PRIORIDADE E UMA LISTA.

Entao aqui cada par leva quatro coisas: a causa da ilegibilidade, o valor se
resolvido, o custo provavel da leitura, e o que ele bloqueia a jusante.

AS QUATRO PRIORIDADES, E O QUE AS SEPARA
-----------------------------------------
P0  destrava um sinal ou uma ferramenta de alto valor: o par (cultura, alvo)
    cai exactamente numa das 43 oportunidades canonicas e o produto AINDA NAO
    esta la. Ler o rotulo muda a carteira de uma oportunidade viva.
P1  resolve oportunidade relevante: o par tem ISSUE_ID e CROP_ID canonicos —
    o motor sabe nomear os dois — mas a oportunidade correspondente ou nao
    existe ou ja tem o produto. E divida de recall real, com endereco.
P2  melhora cobertura: o par e legivel e verdadeiro, mas um dos dois lados nao
    tem nome no motor. Entra no conjunto de rotulos; nao move oportunidade
    enquanto o vocabulario nao entrar (ver IT-VOCAB-HANDOFF-V1).
P3  fechamento estatistico: o produto JA alcanca essa cultura por outro par
    lido. Recuperar este par nao acrescenta autorizacao nova a ninguem —
    acrescenta uma linha.

    P3 NAO E LIXO. E VERDADE QUE NAO MUDA DECISAO NENHUMA.

O CUSTO
-------
Vem da classe de defeito, e a mais cara e conhecida: MATRIZ_MULTICOLUNA exige
cindir colunas dentro de um bloco fundido, que foi implementado, medido e
DESLIGADO — produzia pares deslocados de linha (GIRASOLE x DIABROTICA) com
precisao ~0,75 nessa familia, abaixo do portao de 0,95, e invisivel ao gabarito.
Reabrir essa rota custa gabarito novo antes de custar codigo.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

DIVIDA = 'data/samples/IT-ROTULOS-V1/IT-ROTULOS-DIVIDA-DE-LEITURA-V1.json'
PARES = 'data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json'
PROPAG = 'data/samples/IT-ROTULOS-V1/IT-PAIRSET-PROPAGACAO-V1.json'
FUTURO = 'data/samples/IT-FUTURO-V1/IT-FUTURO-JULGADOS-V1.json'
SAIDA = 'data/samples/IT-ROTULOS-V1/IT-ROTULOS-FILA-DE-CAUDA-V1.json'

# A classe curta e o primeiro token da classe de defeito escrita pelo auditor.
CUSTO = [
    (r'MATRIZ_MULTICOLUNA|COLUNA_FUNDIDA|CALHA_DE_COLUNA', 'ALTO',
     'exige cindir colunas dentro de um bloco fundido — a rota que foi medida a '
     '0,75 de precisao e desligada. Custa gabarito novo antes de custar codigo.'),
    (r'SECAO_PROIBIDA|GUARDA_DE_SECAO', 'MEDIO',
     'mover a guarda de secao de BLOCO para FRASE. Mudanca pequena e testavel, '
     'mas toca todas as rotas ao mesmo tempo: exige a suite inteira.'),
    (r'CABECALHO_DE_SECAO|MULTI_CABECALHO|CABECALHO_MULTIPLO|CABECALHO_ORFAO|'
     r'CABECA_INLINE|CABECALHO_COM_QUALIFICADOR|CABECALHO_DE_USO', 'MEDIO',
     'costurar cabecalho de cultura ao bloco de uso que o segue, atravessando '
     'quebra de coluna ou de pagina.'),
    (r'LISTA_DE_USOS|CELULA_DE_LISTA|CELULA_DE_CULTURA_LONGA|EXCLUSAO_POR_BLOCO', 'BAIXO',
     'a rota certa ja existe; a guarda e que e aplicada ao bloco em vez da frase.'),
    (r'VOCABULARIO_DE_ALVO|LEXICO_DE_ALVOS|GLOSSARIO', 'BAIXO',
     'e vocabulario, nao geometria — mas passa pelo processo de proposta, nao '
     'por remendo (ver IT-VOCAB-HANDOFF-V1).'),
]


def classe_curta(fix):
    m = re.match(r'[A-Z_]{4,}', fix or '')
    return m.group(0) if m else 'NAO_CLASSIFICADA'


def custo(fix):
    for rx, nivel, porque in CUSTO:
        if re.search(rx, fix or ''):
            return nivel, porque
    return 'NAO SEI', 'a classe de defeito nao cai em nenhuma das familias medidas'


def main():
    from it_vocab_handoff import motor
    M, ref, sha = motor()

    d = json.load(open(os.path.join(ROOT, DIVIDA)))
    blk = [r for r in d['ROWS']
           if r.get('VERDICT') == 'AUTORIZADO_MAS_NAO_LIDO'
           and not r.get('RESOLVED_BY_PARSER_TONIGHT')]

    P = json.load(open(os.path.join(ROOT, PARES)))['PAIRS']
    # o que cada registo JA alcanca hoje
    ja = defaultdict(set)
    for p in P:
        ja[p['REGISTRATION_ID']].add(p['CROP'])

    prop = json.load(open(os.path.join(ROOT, PROPAG)))
    # chave da oportunidade -> produtos que ela ja tem depois da uniao
    opp = {}
    for o in prop['ROWS']:
        opp[(o.get('CROP_ID'), o.get('ISSUE_ID'))] = o

    fut = json.load(open(os.path.join(ROOT, FUTURO)))
    fut_pares = {(str(r.get('CROP') or '').upper(), str(r.get('TARGET') or '').upper())
                 for r in fut['RULED'] if r['PASSES']}

    linhas = []
    for r in blk:
        cid = M.crop_id(r['CROP'].replace('_', ' '))
        alvos = r.get('TARGETS_ON_LABEL') or []
        iids = []
        for a in alvos:
            i = M.issue_id(a, permitir_prosa=True)
            if i and i not in iids:
                iids.append(i)

        # P0 — cai numa oportunidade viva cuja carteira ainda nao tem o produto
        bloqueia = []
        for i in (iids or [None]):
            o = opp.get((cid, i))
            if o and r['PRODUCT'].split(' (')[0] not in (o.get('NEW_PRODUCTS') or []):
                bloqueia.append({'OPPORTUNITY_ID': o['OPPORTUNITY_ID'],
                                 'STATUS': o.get('STATUS'),
                                 'PRIORIDADE_COMERCIAL': o.get('COMMERCIAL_PRIORITY'),
                                 'CHAVE': [cid, i]})
        # sinal futuro que fala desta cultura
        sinais = sorted({f'{c} x {t}' for (c, t) in fut_pares
                         if cid and c and M.crop_id(c[:58]) == cid})

        ja_alcanca = r['CROP'] in ja.get(r['LABEL_ID'], set())
        nivel, porque_custo = custo(r.get('FIX_CLASS'))

        if bloqueia:
            p, porque = 'P0', ('cai na oportunidade %s, que hoje nao tem este produto na carteira'
                               % bloqueia[0]['OPPORTUNITY_ID'])
        elif ja_alcanca:
            p, porque = 'P3', ('o registo %s ja alcanca %s por outro par lido: recuperar este '
                               'nao acrescenta autorizacao a ninguem'
                               % (r['LABEL_ID'], r['CROP']))
        elif cid and iids:
            p, porque = 'P1', ('o motor sabe nomear os dois lados (%s x %s): e divida de recall '
                               'com endereco' % (cid, '/'.join(iids)))
        else:
            falta = 'a cultura' if not cid else 'o alvo'
            p, porque = 'P2', ('%s nao tem nome no motor: entra no conjunto de rotulos, mas nao '
                               'move oportunidade enquanto o vocabulario nao entrar' % falta)

        linhas.append({
            'PRIORIDADE': p,
            'PORQUE_ESTA_PRIORIDADE': porque,
            'LABEL_ID': r['LABEL_ID'],
            'PRODUTO': r['PRODUCT'],
            'CULTURA': r['CROP'],
            'ALVOS_NO_ROTULO': alvos,
            'CROP_ID_CANONICO': cid,
            'ISSUE_IDS_CANONICOS': iids,
            'CAUSA_DA_ILEGIBILIDADE': classe_curta(r.get('FIX_CLASS')),
            'CAUSA_COMPLETA': r.get('FIX_CLASS'),
            'PORQUE_O_PARSER_PERDE': r.get('WHY_PARSER_MISSES'),
            'CITACAO_DO_ROTULO': (r.get('EVIDENCE_QUOTE') or '')[:400],
            'COORDENADAS': r.get('EVIDENCE_COORDS'),
            'CUSTO_PROVAVEL': nivel,
            'PORQUE_ESSE_CUSTO': porque_custo,
            'BLOQUEIA_OPORTUNIDADE': bloqueia,
            'SINAIS_FUTUROS_NA_MESMA_CULTURA': sinais,
            'PRODUTO_JA_ALCANCA_A_CULTURA': ja_alcanca,
        })

    ordem = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    custo_ordem = {'BAIXO': 0, 'MEDIO': 1, 'ALTO': 2, 'NAO SEI': 3}
    linhas.sort(key=lambda x: (ordem[x['PRIORIDADE']], custo_ordem[x['CUSTO_PROVAVEL']],
                               x['LABEL_ID'], x['CULTURA']))

    por_p = Counter(x['PRIORIDADE'] for x in linhas)
    saida = {
        'DATASET': 'IT-ROTULOS-FILA-DE-CAUDA-V1',
        'LAYER': 'NATIONAL PRODUCT AUTHORIZATION — divida de leitura priorizada por valor',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-ROTULOS-DIVIDA-DE-LEITURA-V1',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'os 46 pares AUTORIZADO_MAS_NAO_LIDO que sobraram, cruzados com as 43 '
                  'oportunidades canonicas, com o conjunto publicado e com os sinais futuros',
        'MOTOR_LIDO': '%s %s' % (ref, sha[:12]),
        'LEI': 'AUSENCIA NA NOSSA LEITURA NUNCA E AUSENCIA NO REGISTRO',
        'A_FILA_NAO_E_META': 'nao ha objectivo de zerar os 46. Ha objectivo de nao deixar por '
                             'ler o que muda uma decisao.',
        'TOTAL': len(linhas),
        'POR_PRIORIDADE': dict(por_p),
        'POR_CAUSA': dict(Counter(x['CAUSA_DA_ILEGIBILIDADE'] for x in linhas)),
        'POR_CUSTO': dict(Counter(x['CUSTO_PROVAVEL'] for x in linhas)),
        'P0_EXISTE': por_p.get('P0', 0) > 0,
        'ROWS': linhas,
    }
    with open(os.path.join(ROOT, SAIDA), 'w') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)

    print('MOTOR       ', ref, sha[:12])
    print('PARES NA FILA', len(linhas))
    print('POR PRIORIDADE', dict(por_p))
    print('POR CUSTO    ', dict(Counter(x['CUSTO_PROVAVEL'] for x in linhas)))
    print('P0 EXISTE?   ', saida['P0_EXISTE'])
    for x in linhas:
        if x['PRIORIDADE'] in ('P0', 'P1'):
            print('  %s %-7s %-6s %-14s %-14s %s' % (
                x['PRIORIDADE'], x['LABEL_ID'], x['CUSTO_PROVAVEL'], x['CULTURA'],
                x['CROP_ID_CANONICO'] or '-', '/'.join(x['ISSUE_IDS_CANONICOS']) or '-'))
    print('->', SAIDA)


if __name__ == '__main__':
    main()
