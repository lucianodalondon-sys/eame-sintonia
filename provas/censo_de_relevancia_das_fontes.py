#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CENSO DA RELEVANCIA DAS FONTES — quantas estao cobertas, e quantas gastam sem cobertura.

    py provas/censo_de_relevancia_das_fontes.py
    py provas/censo_de_relevancia_das_fontes.py --escrever

    NAO BASTA PROTEGER AS FONTES FUTURAS. AS QUE JA CA ESTAO SAO DEZENAS.

Esta medicao responde, fonte a fonte, com evidencia e sem prosa:

    RELEVANCIA_PRESENTE      ha decisao no livro para algum proposito?
    PROPOSITOS_AVALIADOS     para quais, e com que resultado
    EVIDENCIA_PRESENTE       a decisao aponta para alguma coisa?
    PODE_DISPARAR_COLETA     existe hoje executor que a alcance?
    PODE_GASTAR              e essa rota abre alguma forma de gasto?
    BURACO                   o que falta, dito numa palavra

⚠️ POR QUE O ATLAS NAO FOI PORTADO
-----------------------------------
A missao autorizava portar decisoes ja explicitas do atlas, SE fosse barato,
deterministico e SE se provasse que `GREEN` quer dizer exactamente
«relevante». Foi medido, e nao quer. O proprio atlas define:

    GREEN   «verificada, ACESSIVEL, UTIL, com exemplo real capturado»
    YELLOW  «fonte real e RELEVANTE, mas com atrito: acesso dificil, licenca
             dubia, granularidade fraca, frequencia ruim ou automacao incerta»
    RED     «descartada por motivo concreto — nao serve, NAO E ACESSIVEL, ou
             o uso e PROIBIDO»
    NAO SEI «nao foi possivel verificar»

Tres dos quatro misturam eixos. E o caso que fecha o assunto e o YELLOW: ele
DIZ que a fonte e relevante, e mesmo assim nao e verde — porque o amarelo esta
a falar de ACESSO, LICENCA e AUTOMACAO, nao de relevancia. Se `GREEN` virasse
`SIM`, as fontes verdes nasciam relevantes por uma convencao de cor, e as
amarelas — que o atlas declara relevantes — ficavam de fora. Quantas sao de
cada, nesta corrida, e `porque_nao_portar()` que conta: um numero escrito a mao
dentro da explicacao de por que nao se confia num numero escrito a mao seria a
ironia a contar-se sozinha.

    VERDICT_DO_ATLAS = EIXO_MISTURADO.
    PORTADAS_DO_ATLAS = 0, E O MOTIVO ESTA MEDIDO.

    UMA COR NAO E UMA DECISAO. PINTAR NAO E AVALIAR.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import relevancia_da_fonte as rel   # noqa: E402
from receitas import EXECUTORES     # noqa: E402 — quem a casa sabe correr
from pedido import ALVOS            # noqa: E402

FONTES_MEDIDAS = os.path.join('system-map', 'data', 'sources.generated.json')
SAIDA = os.path.join('data', 'derivados', 'CENSO-RELEVANCIA-DE-FONTE-V1.json')

# Os quatro vereditos do atlas, e o eixo que cada um realmente mistura.
# Medido em `docs/fontes/ATLAS-DE-FONTES-EAME.md`, seccao VERDICT.
VERDICT_DO_ATLAS_MISTURA = {
    'GREEN': ('ACESSO', 'UTILIDADE', 'EVIDENCIA'),
    'YELLOW': ('RELEVANCIA', 'ACESSO', 'LICENCA', 'QUALIDADE', 'FREQUENCIA',
               'AUTOMACAO'),
    'RED': ('RELEVANCIA', 'ACESSO', 'LEGALIDADE'),
    'NAO SEI': ('MEDICAO_AUSENTE',),
}
PORTAR_DO_ATLAS = False


def porque_nao_portar(fontes: list) -> str:
    """O motivo, com os numeros MEDIDOS sobre o cadastro desta corrida.

    ⚠️ ESTA FRASE TINHA OS NUMEROS ESCRITOS A MAO — «16» e «2» — e eles eram
    a conta do atlas europeu sozinho, nao a do cadastro de 77. A COL-LAW-103
    ja o dizia: estado derivavel nao se escreve a mao. Um numero escrito a
    mao dentro da explicacao de por que nao se confia num numero escrito a
    mao e a ironia a contar-se sozinha.
    """
    verde = sum(1 for f in fontes if str(f.get('verdict') or '').upper() == 'GREEN')
    amarelo = sum(1 for f in fontes if str(f.get('verdict') or '').upper() == 'YELLOW')
    return ('o veredito do atlas mistura eixos, e o proprio atlas o diz: YELLOW '
            'e «fonte real e RELEVANTE, mas com atrito de acesso/licenca/'
            'automacao». GREEN -> SIM promoveria %d fontes por convencao de cor '
            'e deixaria de fora %d que o atlas declara relevantes. Uma cor nao '
            'e uma decisao.' % (verde, amarelo))


def _fontes(raiz=RAIZ) -> list:
    caminho = os.path.join(raiz, FONTES_MEDIDAS)
    if not os.path.isfile(caminho):
        return []
    with open(caminho, encoding='utf-8') as f:
        S = json.load(f)
    return list(S.get('SOURCES') or []) + list(S.get('MASTER_ITALIANO') or [])


def _executor_do_territorio(territorio: str):
    e = EXECUTORES.get(str(territorio or '').upper() or '')
    return e[0] if e else None


def medir(raiz=RAIZ) -> dict:
    """→ o censo. Tudo derivado; nada escrito a mao."""
    livro = rel.ler_livro(raiz)
    fontes = _fontes(raiz)

    # Todos os propositos para os quais existe QUALQUER decisao no livro.
    por_par = {}
    for l in livro:
        por_par.setdefault(l.get('SOURCE_ID'), []).append(l)

    linhas = []
    for f in fontes:
        sid = f.get('source_id')
        if not sid:
            continue
        territorio = str(f.get('territory') or '').upper()
        executor = _executor_do_territorio(territorio)

        decisoes = por_par.get(sid) or []
        propositos = {}
        for d in decisoes:
            propositos[d.get('PROPOSITO')] = d.get('RESULTADO')

        # PODE DISPARAR COLETA: existe hoje um executor que a alcance?
        pode_disparar = executor is not None
        # PODE GASTAR: e essa rota abre alguma forma de gasto?
        #   Manual + pontual e o pedido por omissao desta casa, logo a unica
        #   forma de gasto que o executor sozinho abre e o DINHEIRO.
        paga = pode_disparar and not rel.custo_e_gratuito(executor.get('custo'))

        # O portao, perguntado como o caminho real o pergunta.
        nomeia_fonte = bool(executor and 'fonte' in
                            (executor.get('argumentos_de_filtros') or []))
        alvo_do_portao = sid if nomeia_fonte else None
        v = rel.portao(alvo_do_portao, territorio, livro,
                       custo=(executor or {}).get('custo'),
                       acionamento='MANUAL', escopo='PONTUAL')

        presente = 'SIM' if decisoes else 'NAO'
        com_evidencia = any(d.get('EVIDENCIA') for d in decisoes)

        if decisoes:
            buraco = ''
        elif paga:
            buraco = 'PODE_GASTAR_SEM_AVALIACAO'
        elif pode_disparar:
            buraco = 'PODE_COLETAR_DE_GRACA_SEM_AVALIACAO'
        else:
            buraco = 'SEM_EXECUTOR_E_SEM_AVALIACAO'

        linhas.append({
            'SOURCE_ID': sid,
            'TERRITORIO_DECLARADO': territorio,
            'VERDICT_DO_ATLAS': f.get('verdict'),
            'RELEVANCIA_PRESENTE': presente,
            'PROPOSITOS_AVALIADOS': propositos,
            'EVIDENCIA_PRESENTE': com_evidencia,
            'PODE_DISPARAR_COLETA': pode_disparar,
            'EXECUTOR': (executor or {}).get('id'),
            'CUSTO_DA_ROTA': (executor or {}).get('custo'),
            'PODE_GASTAR_DINHEIRO': paga,
            'PLANO_NOMEIA_A_FONTE': nomeia_fonte,
            'VEREDITO_DO_PORTAO': v['VEREDITO'],
            'BURACO': buraco,
        })

    cobertas = [l for l in linhas if l['RELEVANCIA_PRESENTE'] == 'SIM']
    gastam_sem_cobertura = [l for l in linhas
                            if l['PODE_GASTAR_DINHEIRO']
                            and l['RELEVANCIA_PRESENTE'] == 'NAO']
    coletam_sem_cobertura = [l for l in linhas
                             if l['PODE_DISPARAR_COLETA']
                             and l['RELEVANCIA_PRESENTE'] == 'NAO']

    # O QUE O PORTAO PASSOU A BARRAR. Medido sobre o caminho real, nao suposto.
    barrados = [l for l in linhas if l['PODE_GASTAR_DINHEIRO']
                and l['VEREDITO_DO_PORTAO'] != rel.AUTORIZA]

    return {
        'SCHEMA': 'sintonia.censo-relevancia-de-fonte/1',
        'CONTRATO': rel.CONTRATO,
        'VERSAO_DO_PORTAO': rel.VERSAO_DO_PORTAO,
        'LIVRO': rel.LIVRO,
        'TOTAIS': {
            'FONTES_NO_CADASTRO': len(linhas),
            'COM_DECISAO_DE_RELEVANCIA': len(cobertas),
            'SEM_DECISAO_DE_RELEVANCIA': len(linhas) - len(cobertas),
            'PODEM_DISPARAR_COLETA': sum(1 for l in linhas
                                         if l['PODE_DISPARAR_COLETA']),
            'PODEM_GASTAR_DINHEIRO': sum(1 for l in linhas
                                         if l['PODE_GASTAR_DINHEIRO']),
            'COLETAM_SEM_AVALIACAO': len(coletam_sem_cobertura),
            'GASTAM_SEM_AVALIACAO': len(gastam_sem_cobertura),
            'BARRADAS_PELO_PORTAO_NO_DINHEIRO': len(barrados),
            'DECISOES_NO_LIVRO': len(livro),
        },
        'PORTADAS_DO_ATLAS': 0,
        'PORQUE_NAO_PORTAR': porque_nao_portar(fontes),
        'VERDICT_DO_ATLAS_MISTURA': VERDICT_DO_ATLAS_MISTURA,
        'POR_BURACO': dict(Counter(l['BURACO'] for l in linhas)),
        'POR_VEREDITO': dict(Counter(l['VEREDITO_DO_PORTAO'] for l in linhas)),
        'TERRITORIOS_COM_EXECUTOR': sorted(EXECUTORES),
        'TERRITORIOS_SEM_EXECUTOR': sorted(set(ALVOS) - set(EXECUTORES)),
        'FONTES': linhas,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--escrever', action='store_true')
    a = ap.parse_args()
    c = medir()
    t = c['TOTAIS']

    print('CENSO DA RELEVANCIA DAS FONTES · %s' % c['CONTRATO'])
    for k, v in t.items():
        print('  %-34s %s' % (k, v))
    print()
    print('  por buraco  : %s' % json.dumps(c['POR_BURACO'], ensure_ascii=False))
    print('  por veredito: %s' % json.dumps(c['POR_VEREDITO'], ensure_ascii=False))
    print()
    print('  PORTADAS_DO_ATLAS = %d' % c['PORTADAS_DO_ATLAS'])
    print('  %s' % c['PORQUE_NAO_PORTAR'])
    if a.escrever:
        caminho = os.path.join(RAIZ, SAIDA)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(json.dumps(c, ensure_ascii=False, indent=2) + '\n')
        print('\n  escrito: %s' % SAIDA)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
