#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRUZA O QUE A ITÁLIA FALA COM O QUE A ADAMA PODE.

    python3 scripts/cruzar_regua_rotulo.py

Junta as duas réguas, que até aqui viviam separadas:

    IT-PARES-CULTURA-ALVO-V0.json   116 pares da conversa pública (vídeo e plateia)
    IT-ROTULOS-PARES.json         1.424 pares do rótulo autorizado (Ministero)

E devolve TRÊS GAVETAS, que nunca viram uma só:

    CONVERGENCIA          a conversa fala E o rótulo autoriza
    CONVERSA_SEM_LEITURA  a conversa fala e NÃO LEMOS linha de rótulo
    ROTULO_SEM_CONVERSA   o rótulo autoriza e o nosso corpus não fala

⚠️ AS TRÊS GAVETAS DIZEM COISAS DIFERENTES, E DUAS DELAS SÃO FÁCEIS DE LER ERRADO

`CONVERSA_SEM_LEITURA` **não** é «a ADAMA não tem produto». É «não lemos». A
cobertura de rótulo é 51,5% — quase metade dos produtos não teve linha de uso lida.
Chamar isso de lacuna de portfólio é o pior erro possível deste sistema.

`ROTULO_SEM_CONVERSA` **não** é «ninguém fala disso na Itália». É «o nosso corpus
não fala» — e o corpus é amostra dos 17 recortes que abrimos, não do país.

    AUSÊNCIA EM UMA GAVETA É AUSÊNCIA NA NOSSA LEITURA, NUNCA NO MUNDO.

A RECONCILIAÇÃO DE VOCABULÁRIO É UM ATO NOSSO
----------------------------------------------
As duas réguas nasceram para fontes diferentes e batizaram as mesmas coisas de
jeitos diferentes: o corpus diz `GIAVONE`, o rótulo diz `ECHINOCHLOA`; o corpus diz
`NOTTUA`, o rótulo diz `NOTTUE`. Ligar os dois é inferência, não observação — então
cada equivalência vem escrita aqui, com o motivo, e viaja no resultado.

Uma delas é deliberadamente mais fraca: `GRANO_GEN` existe no corpus porque «grano»
colide entre italiano e espanhol e ficou em quarentena. Fundi-lo em `FRUMENTO`
desfaria a quarentena, então ele entra como `EQUIVALENCIA_APROXIMADA` e a
convergência que nasce dele sai marcada.
"""
import json
import os
import time
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, 'data', 'samples', 'IT-REGUA',
                      'IT-PARES-CULTURA-ALVO-V0.json')
ROTULO = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS', 'IT-ROTULOS-PARES.json')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-CRUZAMENTO')

# ── EQUIVALÊNCIAS DECLARADAS ────────────────────────────────────────────────────
# corpus → rótulo. Cada linha é uma decisão nossa, e cada uma pode estar errada.
EQ_ALVO = {
    'NOTTUA':         ('NOTTUE', 'plural do mesmo genero de lagarta noturna'),
    'CICALINA_GEN':   ('CICALINE', 'plural do mesmo grupo de cigarrinhas'),
    'ACARO_GEN':      ('ACARI', 'plural do mesmo grupo'),
    'GIAVONE':        ('ECHINOCHLOA', 'giavone e o nome italiano de Echinochloa'),
    'LOIETTO':        ('LOLIUM', 'loietto e o nome italiano de Lolium'),
    'SORGHETTA':      ('SORGHUM_HAL', 'sorghetta e o nome italiano de Sorghum halepense'),
    'PAPAVERO':       ('PAPAVER', 'nome italiano do genero'),
    'CHENOPODIO':     ('CHENOPODIUM', 'nome italiano do genero'),
    'CIPERO':         ('CYPERUS', 'nome italiano do genero'),
    'RISO_CRODO':     ('ORYZA_CRODO', 'mesmo objeto, chave diferente nas duas reguas'),
    'SETARIA_PANICO': ('SETARIA', 'panico e um dos nomes italianos de Setaria'),
    'CERATITIS':      ('MOSCA_FRUTTA', 'Ceratitis capitata e a mosca da fruta'),
    'MARCIUME':       ('BOTRITE', 'APROXIMADA: marciume acido/nero nem sempre e Botrytis'),
}
EQ_CULTURA = {
    'GRANO_GEN': ('FRUMENTO', 'APROXIMADA: grano generico ficou em quarentena no corpus '
                              'porque colide com o espanhol. Fundir desfaz a quarentena.'),
    'ORTICOLE':  ('ORTAGGI', 'mesmo agrupamento, nome diferente nas duas reguas'),
}
APROXIMADAS = {'MARCIUME', 'GRANO_GEN'}


def traduz(chave, tabela):
    """→ (chave_no_rotulo, como). `como` viaja no resultado, sempre."""
    if chave in tabela:
        destino, motivo = tabela[chave]
        return destino, {'TRADUZIDO': True, 'DE': chave, 'PARA': destino,
                         'MOTIVO': motivo,
                         'FORCA': ('APROXIMADA' if chave in APROXIMADAS else 'DIRETA')}
    return chave, {'TRADUZIDO': False}


def main():
    corpus = json.load(open(CORPUS, encoding='utf-8'))
    rotulo = json.load(open(ROTULO, encoding='utf-8'))
    os.makedirs(SAIDA, exist_ok=True)

    # índice do rótulo: (cultura, alvo) → produtos
    idx = defaultdict(list)
    for p in rotulo['PARES']:
        idx[(p['CULTURA_CANONICA'], p['ALVO_CANONICO'])].append(p)

    convergencia, sem_leitura = [], []
    vistos_no_rotulo = set()

    for c in corpus['PARES']:
        cult, como_c = traduz(c['CULTURA'], EQ_CULTURA)
        alvo, como_a = traduz(c['ALVO'], EQ_ALVO)
        produtos = idx.get((cult, alvo), [])

        base = {
            'PAR_DA_CONVERSA': c['PAR'],
            'CULTURA': c['CULTURA'],
            'ALVO': c['ALVO'],
            'CATEGORIA_DE_PRODUTO': c.get('CATEGORIA_DE_PRODUTO'),
            'CONVERSA_NIVEL': c['NIVEL'],
            'CONVERSA_DOCUMENTOS': c['N_DOCUMENTOS'],
            'CONVERSA_FONTES': c['N_FONTES_DISTINTAS'],
            'CONVERSA_PLATEIA': c.get('PLATEIA_VEREDITO'),
            'CONVERSA_PLATEIA_DETALHE': c.get('PLATEIA_DA_EVIDENCIA'),
            'TRADUCAO_DE_CULTURA': como_c,
            'TRADUCAO_DE_ALVO': como_a,
        }
        if produtos:
            vistos_no_rotulo.add((cult, alvo))
            niveis = Counter(x.get('LIGACAO_NIVEL') for x in produtos)
            forte = como_c.get('FORCA') != 'APROXIMADA' and \
                como_a.get('FORCA') != 'APROXIMADA'
            convergencia.append(dict(base, **{
                'GAVETA': 'CONVERGENCIA',
                'PRODUTOS_ADAMA': sorted({x['PRODUCT'] for x in produtos if x['PRODUCT']}),
                'N_PRODUTOS': len({x['REGISTRATION_ID'] for x in produtos}),
                'ROTULO_NIVEIS_DE_LIGACAO': dict(niveis),
                'ROTULO_TEM_LINHA_DE_TABELA': niveis.get('LINHA_DA_TABELA', 0) > 0,
                'CITACAO_DO_ROTULO': produtos[0].get('CITACAO_DA_LINHA', '')[:300],
                'ALVO_LITERAL_NO_ROTULO': produtos[0].get('ALVO_LITERAL'),
                'CONVERGENCIA_FORCA': 'DIRETA' if forte else 'POR_EQUIVALENCIA_APROXIMADA',
                'O_QUE_ISTO_SUSTENTA':
                    'a conversa publica italiana liga esta cultura a este alvo, E o '
                    'registro italiano da ADAMA tem produto cujo rotulo nomeia os dois.',
                'O_QUE_ISTO_NAO_SUSTENTA':
                    'nao sustenta demanda, venda, prioridade nem eficacia. E encontro '
                    'de duas leituras, nao medida de mercado.',
            }))
        else:
            sem_leitura.append(dict(base, **{
                'GAVETA': 'CONVERSA_SEM_LEITURA',
                'LEIA_ASSIM':
                    'NAO LEMOS linha de rotulo que ligue esta cultura a este alvo. A '
                    'cobertura de rotulo e 51,5%% -- quase metade dos produtos nao teve '
                    'linha de uso lida.',
                'AFIRMACAO_PROIBIDA': 'a ADAMA nao tem produto para este alvo nesta cultura',
                'AFIRMACAO_PERMITIDA':
                    'nesta leitura dos rotulos publicados pelo Ministero, capturada em '
                    '02/09/2026, nao encontramos linha que ligue esta cultura a este '
                    'alvo. NAO SEI.',
            }))

    # a terceira gaveta: o rótulo autoriza e o corpus não fala
    sem_conversa = []
    for (cult, alvo), produtos in sorted(idx.items()):
        if (cult, alvo) in vistos_no_rotulo or alvo == 'NAO_MAPEADO':
            continue
        niveis = Counter(x.get('LIGACAO_NIVEL') for x in produtos)
        sem_conversa.append({
            'GAVETA': 'ROTULO_SEM_CONVERSA',
            'PAR_DO_ROTULO': '%s x %s' % (cult, alvo),
            'CULTURA': cult,
            'ALVO': alvo,
            'ALVO_E': produtos[0].get('ALVO_E'),
            'N_PRODUTOS': len({x['REGISTRATION_ID'] for x in produtos}),
            'PRODUTOS_ADAMA': sorted({x['PRODUCT'] for x in produtos if x['PRODUCT']})[:12],
            'ROTULO_NIVEIS_DE_LIGACAO': dict(niveis),
            'LEIA_ASSIM':
                'o rotulo autoriza, e o NOSSO CORPUS nao fala. O corpus e amostra dos '
                '17 recortes que abrimos, nao do pais.',
            'AFIRMACAO_PROIBIDA': 'ninguem fala disso na Italia',
        })

    convergencia.sort(key=lambda x: (-int(x['CONVERSA_NIVEL'] == 3),
                                     -x['CONVERSA_DOCUMENTOS']))
    sem_conversa.sort(key=lambda x: -x['N_PRODUTOS'])

    saida = {
        'DATASET': 'IT-CRUZAMENTO-CONVERSA-X-ROTULO',
        'O_QUE_E': 'encontro das duas reguas: o que a Italia fala x o que a ADAMA pode',
        'ENTRADAS': {
            'CONVERSA': {'ARQUIVO': 'IT-PARES-CULTURA-ALVO-V0.json',
                         'PARES': corpus['PARES_TOTAL'],
                         'DOCUMENTOS': corpus['DOCUMENTOS_LIDOS']},
            'ROTULO': {'ARQUIVO': 'IT-ROTULOS-PARES.json',
                       'PARES': rotulo['PARES_TOTAL'],
                       'COBERTURA': rotulo['COBERTURA']},
        },
        'AS_TRES_GAVETAS_NAO_SE_SOMAM': {
            'CONVERGENCIA': 'a conversa fala E o rotulo autoriza',
            'CONVERSA_SEM_LEITURA': 'NAO LEMOS linha de rotulo. Nunca «nao tem produto».',
            'ROTULO_SEM_CONVERSA': 'o NOSSO CORPUS nao fala. Nunca «ninguem fala disso».',
            'LEI': 'AUSENCIA EM UMA GAVETA E AUSENCIA NA NOSSA LEITURA, NUNCA NO MUNDO.',
        },
        'EQUIVALENCIAS_DECLARADAS': {
            'O_QUE_SAO': 'as duas reguas batizaram as mesmas coisas de jeitos diferentes. '
                         'Ligar os dois e inferencia nossa, nao observacao.',
            'ALVO': {k: {'PARA': v[0], 'MOTIVO': v[1],
                         'FORCA': 'APROXIMADA' if k in APROXIMADAS else 'DIRETA'}
                     for k, v in EQ_ALVO.items()},
            'CULTURA': {k: {'PARA': v[0], 'MOTIVO': v[1],
                            'FORCA': 'APROXIMADA' if k in APROXIMADAS else 'DIRETA'}
                        for k, v in EQ_CULTURA.items()},
        },
        'CAPTURADO_EM': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'CONVERGENCIA_TOTAL': len(convergencia),
        'CONVERGENCIA_COM_PLATEIA_PROFISSIONAL': sum(
            1 for x in convergencia
            if x['CONVERSA_PLATEIA'] in ('SUSTENTADO_POR_CANAL_PROFISSIONAL',
                                         'PREDOMINANTEMENTE_PROFISSIONAL')),
        'CONVERSA_SEM_LEITURA_TOTAL': len(sem_leitura),
        'ROTULO_SEM_CONVERSA_TOTAL': len(sem_conversa),
        'CONVERGENCIA': convergencia,
        'CONVERSA_SEM_LEITURA': sem_leitura,
        'ROTULO_SEM_CONVERSA': sem_conversa,
    }
    destino = os.path.join(SAIDA, 'IT-CONVERSA-X-ROTULO.json')
    json.dump(saida, open(destino, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('CONVERGENCIA .......... %3d  (com plateia profissional: %d)'
          % (len(convergencia), saida['CONVERGENCIA_COM_PLATEIA_PROFISSIONAL']))
    print('CONVERSA_SEM_LEITURA .. %3d  <- «nao lemos», nunca «nao tem»' % len(sem_leitura))
    print('ROTULO_SEM_CONVERSA ... %3d  <- «nosso corpus nao fala»' % len(sem_conversa))
    print()
    print('%-26s %-5s %-5s %-4s %s' % ('PAR', 'NIVEL', 'DOCS', 'PROD', 'PLATEIA'))
    for x in convergencia[:14]:
        print('%-26s %-5s %-5d %-4d %s' % (
            x['PAR_DA_CONVERSA'], x['CONVERSA_NIVEL'], x['CONVERSA_DOCUMENTOS'],
            x['N_PRODUTOS'], (x['CONVERSA_PLATEIA'] or '')[:34]))
    print()
    print('gravado:', os.path.relpath(destino, ROOT))


if __name__ == '__main__':
    main()
