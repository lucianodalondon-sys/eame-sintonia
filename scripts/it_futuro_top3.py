#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OS SINAIS DE MAIOR VALOR, ESCRITOS PARA QUEM DECIDE — nao para quem programa.

    python3 scripts/it_futuro_top3.py [n]

Le IT-FUTURO-SINAIS-V1.json e escreve os n sinais de maior valor em linguagem de
utilizador ADAMA. Nao ha campo novo aqui: tudo o que sai foi escrito na ficha e
sobreviveu ao refutador.

    NENHUM CAMPO E FABRICADO PARA COMPLETAR A FICHA.

Onde a ficha diz NAO SEI, este texto diz NAO SEI. Onde nao ha portfolio, diz que
nao ha, e diz de qual das tres coisas se trata — ausencia de autorizacao,
ausencia de leitura, ou alvo fora do catalogo. Um departamento so aparece se
tiver razao verificavel; os que ficaram de fora aparecem na linha final, para
que a ausencia seja visivel em vez de silenciosa.

    O QUE NAO SABEMOS E PARTE DO SINAL, NAO O RODAPE DELE.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = 'data/samples/IT-FUTURO-V1/IT-FUTURO-SINAIS-V1.json'

NOME = {
    'DESENVOLVIMENTO_DE_MERCADO': 'Desenvolvimento de Mercado',
    'MARKETING': 'Marketing',
    'COMERCIAL_RTV': 'Comercial / RTV',
    'CIENCIA_TECNICO': 'Técnico / Ciência',
    'SUPPLY': 'Supply',
    'REGULATORIO_PORTFOLIO': 'Regulatório / Portfólio',
}
ACAO = {
    'AGIR_AGORA': 'AGIR AGORA',
    'PREPARAR': 'PREPARAR',
    'MONITORAR': 'MONITORAR',
    'SEM_ACAO_DEMONSTRAVEL': 'SEM AÇÃO DEMONSTRÁVEL',
}
HORIZ = {
    'IMEDIATO': 'imediato',
    'PROXIMA_JANELA': 'próxima janela',
    'PROXIMA_SAFRA': 'próxima safra',
    'ESTRUTURAL_FUTURO': 'estrutural / futuro',
}


def sn(v, vazio='NÃO SEI'):
    t = str(v or '').strip()
    return t if t else vazio


def cartao(x, n):
    F, C, T, A = (x['A_FATO'], x['B_CONFIANCA'],
                  x['C_TEMPO_AGRONOMICO'], x['D_RELEVANCIA_ADAMA'])
    L = []
    L.append('### %d · %s' % (n, sn(x.get('TITULO'), 'sem título')))
    L.append('')
    L.append('`%s` · valor **%s** · **%s** · horizonte %s · estado do tempo `%s`'
             % (x['CAND_ID'], sn(x.get('VALOR'), '?'),
                ACAO.get(x['F_ACAO_POSSIVEL']['CLASSE'], '?'),
                HORIZ.get(x.get('G_HORIZONTE'), '?'),
                sn(C.get('ESTADO_DO_TEMPO'), '?')))
    L.append('')
    L.append('**Cultura** %s · **Problema** %s · **Região** %s'
             % (sn(F.get('CULTURA')), sn(F.get('ALVO')), sn(F.get('REGIAO'))))
    L.append('')
    L.append('**O que aconteceu.** %s' % sn(F.get('O_QUE_ACONTECEU')))
    L.append('')
    L.append('**Evidência.** %s' % sn(F.get('FONTE')))
    L.append('')
    L.append('> «%s»' % sn(F.get('CITACAO_VERBATIM')))
    L.append('')
    L.append('Facto de %s, publicado em %s. Citação conferida pelo refutador: **%s**.'
             % (sn(F.get('DATA_DO_FATO')), sn(F.get('DATA_DA_PUBLICACAO')),
                sn(x.get('CITACAO_CONFERIDA_PELO_REFUTADOR'), 'não declarado')))
    L.append('')
    L.append('**Janela de aplicação.** %s' % sn(T.get('JANELA_DE_APLICACAO')))
    L.append('')
    L.append('Base: %s' % sn(T.get('BASE_DA_JANELA'), 'NÃO HÁ BASE'))
    L.append('')
    L.append('É hora de agir agora? **%s.** Ainda há tempo? **%s.** '
             'É para a próxima janela ou safra? **%s.** %s'
             % (sn(T.get('AGIR_AGORA'), '?'), sn(T.get('AINDA_HA_TEMPO'), '?'),
                sn(T.get('PROXIMA_JANELA_OU_SAFRA'), '?'), sn(T.get('PORQUE'), '')))
    L.append('')
    if A.get('TEM_PORTFOLIO') == 'SIM':
        L.append('**Portfólio ADAMA relacionado** (%s):'
                 % ('união das autorizações, não recomendação de produto único'
                    if A.get('UNIAO_DE_AUTORIZACOES') == 'SIM' else 'registo único'))
        for p in A.get('PRODUTOS') or []:
            L.append('- %s' % p)
        if A.get('UNIAO_DE_AUTORIZACOES') == 'SIM':
            L.append('')
            L.append(sn(A.get('UNIAO_EXPLICADA'), ''))
    else:
        L.append('**Portfólio ADAMA relacionado:** %s. %s'
                 % (sn(A.get('TEM_PORTFOLIO'), 'NÃO SEI'),
                    sn(A.get('SEM_PORTFOLIO_PORQUE'), '')))
    L.append('')
    L.append('Oportunidade: **%s**.' % sn(A.get('OPORTUNIDADE'), '?'))
    L.append('')
    L.append('**Quem age, e porquê**')
    L.append('')
    fora = []
    for m in x['E_MAPA_DE_ACAO']:
        if m['ACIONAVEL'] == 'SIM':
            L.append('- **%s** — %s' % (NOME[m['DEPARTAMENTO']], m['RAZAO']))
        else:
            fora.append(NOME[m['DEPARTAMENTO']])
    if fora:
        L.append('')
        L.append('Sem acção demonstrável para: %s.' % ', '.join(fora))
    L.append('')
    L.append('**O que fazer**')
    for a in x['F_ACAO_POSSIVEL'].get('ACOES') or []:
        L.append('- %s' % a)
    L.append('')
    L.append('**O que ainda NÃO sabemos**')
    for u in C.get('NAO_SABEMOS') or ['não declarado']:
        L.append('- %s' % u)
    inf = C.get('INFERIDO') or []
    if inf:
        L.append('')
        L.append('Inferido, e não observado: %s' % '; '.join(inf))
    return '\n'.join(L)


def main(n=3):
    d = json.load(open(os.path.join(ROOT, FONTE)))
    por_id = {r['CAND_ID']: r for r in d['ROWS']}
    ids = d.get('OS_TRES_DE_MAIOR_VALOR') or []
    if not ids:
        print('ainda nao ha sinal COMPLETO: %s' % d.get('ESTADO'))
        return
    print('## Os %d sinais de maior valor' % min(n, len(ids)))
    print()
    for i, cid in enumerate(ids[:n], 1):
        print(cartao(por_id[cid], i))
        print()


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
