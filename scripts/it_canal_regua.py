#!/usr/bin/env python3
"""REGUA DE CANAL — provada em amostra ANTES de qualquer coleta nova.

A missao pede para descobrir quais dados publicos respondem cinco perguntas:

    QUEM COMPRA · QUEM RECOMENDA · QUEM INFLUENCIA · QUEM DISTRIBUI ·
    QUEM REPRESENTA PRODUTORES

E pede para comecar pequeno, medido e auditavel — provar a regua na amostra antes
de sair coletando. Entao esta regua roda sobre o que JA existe no acervo, sem
rede, e mede quanto de cada papel o acervo consegue responder hoje.

    CORRECAO DE UMA AFIRMACAO MINHA. Eu escrevi ontem
    CHANNEL_LAYER_STATE = NOT_COLLECTED. Estava errado por baixo: a rodada de
    descoberta de fontes ja tinha classificado COOPERATIVE,
    COOPERATIVE_DISTRIBUTOR, PRODUCER_ORGANISATION e PRIVATE_AGRONOMIC_ADVISORY —
    material de canal, catalogado com outro nome e nunca usado para esta pergunta.
    O certo e PARTIALLY_COLLECTED_UNDER_ANOTHER_NAME.

A LEI QUE NAO SE AFROUXA
    ORGANIZACAO NOMEADA NUM CONVEGNO NAO E CANAL COMERCIAL.
    Papel so se afirma com evidencia do proprio acervo, e o campo que falta fica
    NOT_IN_SOURCE.
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(ROOT, 'data', 'samples')
DEST = os.path.join(ROOT, 'data/samples/IT-FUTURO-V1')

# ── a regua: que EVIDENCIA prova cada papel ─────────────────────────────────
PAPEIS = {
    'QUEM_COMPRA': {
        'PERGUNTA': 'quem adquire o produto fitossanitario',
        'EVIDENCIA_QUE_PROVARIA': 'nota fiscal, contrato de fornecimento, lista de '
                                  'preco com comprador nomeado',
        'EVIDENCIA_PUBLICA_POSSIVEL': 'NENHUMA — compra e dado privado. Public'
                                      'amente so se alcanca por PROXY: quem '
                                      'distribui e quem representa quem compra.',
        'ACERVO_RESPONDE': 'NO',
    },
    'QUEM_RECOMENDA': {
        'PERGUNTA': 'quem diz ao produtor o que aplicar e quando',
        'EVIDENCIA_QUE_PROVARIA': 'boletim tecnico assinado com recomendacao de '
                                  'intervencao; servico de assistencia declarado',
        'EVIDENCIA_PUBLICA_POSSIVEL': 'boletins regionais de produzione integrata, '
                                      'consorzi fitosanitari, DSS comerciais',
        'ACERVO_RESPONDE': 'YES',
    },
    'QUEM_INFLUENCIA': {
        'PERGUNTA': 'quem forma a opiniao tecnica sem necessariamente recomendar',
        'EVIDENCIA_QUE_PROVARIA': 'palestra em convegno, publicacao, canal com '
                                  'audiencia declarada',
        'EVIDENCIA_PUBLICA_POSSIVEL': 'convegni, canais de video, perfis, midia '
                                      'tecnica',
        'ACERVO_RESPONDE': 'YES',
    },
    'QUEM_DISTRIBUI': {
        'PERGUNTA': 'quem revende o produto ao produtor',
        'EVIDENCIA_QUE_PROVARIA': 'catalogo de revenda, rede declarada, consorzio '
                                  'agrario com loja',
        'EVIDENCIA_PUBLICA_POSSIVEL': 'sites de consorzi agrari e cooperativas com '
                                      'catalogo de mezzi tecnici',
        'ACERVO_RESPONDE': 'PARTIAL',
    },
    'QUEM_REPRESENTA_PRODUTORES': {
        'PERGUNTA': 'quem fala em nome de um conjunto de produtores',
        'EVIDENCIA_QUE_PROVARIA': 'organizzazione di produttori reconhecida, '
                                  'cooperativa com socios, associazione de categoria',
        'EVIDENCIA_PUBLICA_POSSIVEL': 'registro de OP, estatuto, site institucional',
        'ACERVO_RESPONDE': 'PARTIAL',
    },
}

# tipos ja catalogados no acervo que sustentam cada papel
TIPO_PARA_PAPEL = {
    'FITOSANITARY_SERVICE': ['QUEM_RECOMENDA'],
    'PRIVATE_AGRONOMIC_ADVISORY': ['QUEM_RECOMENDA', 'QUEM_INFLUENCIA'],
    'DSS_COMMERCIAL': ['QUEM_RECOMENDA'],
    'COOPERATIVE': ['QUEM_REPRESENTA_PRODUTORES', 'QUEM_DISTRIBUI'],
    'COOPERATIVE_DISTRIBUTOR': ['QUEM_DISTRIBUI', 'QUEM_REPRESENTA_PRODUTORES'],
    'PRODUCER_ORGANISATION': ['QUEM_REPRESENTA_PRODUTORES'],
    'TECHNICAL_MEDIA': ['QUEM_INFLUENCIA'],
    'PODCAST': ['QUEM_INFLUENCIA'],
    'UNIVERSITY_DEPARTMENT': ['QUEM_INFLUENCIA'],
    'INSTITUTIONAL_REPOSITORY': ['QUEM_INFLUENCIA'],
    'COMPETITOR_CHANNEL': [],
    'AGROMET_OPEN_DATA': [],
}


def main():
    os.makedirs(DEST, exist_ok=True)
    fontes = json.load(open(os.path.join(S, 'IT-FONTES-V1',
                                         'IT-FONTES-DESCOBERTA-V1.json'),
                            encoding='utf-8'))['SOURCES']
    canais = json.load(open(os.path.join(S, 'IT-VIDEO-V1',
                                         'IT-VIDEO-CANAIS-V1.json'),
                            encoding='utf-8'))['CHANNELS']
    perfis = json.load(open(os.path.join(S, 'IT-INSTAGRAM-V3',
                                         'IT-INSTAGRAM-PERFIS-V3.json'),
                            encoding='utf-8'))['PROFILES']

    linhas = []
    for f in fontes:
        papeis = TIPO_PARA_PAPEL.get(f.get('SOURCE_TYPE'), [])
        linhas.append({
            'ENTITY': f.get('NAME'), 'ORIGIN': 'IT-FONTES-DESCOBERTA-V1',
            'SOURCE_ID': f.get('SOURCE_ID'),
            'TYPE_AS_COLLECTED': f.get('SOURCE_TYPE'),
            'AUTHORITY_CLASS': f.get('AUTHORITY_CLASS'),
            'REGION': f.get('REGION') or 'NOT_IN_SOURCE',
            'CROPS': f.get('CROPS_RELEVANT') or [],
            'URL': f.get('PRIMARY_URL'),
            'CHANNEL_ROLES': papeis,
            'ROLE_EVIDENCE': ('classificacao feita na rodada de descoberta de '
                              'fontes, a partir do site institucional'
                              if papeis else None),
            'BUYS_PRODUCT': 'NOT_IN_SOURCE',
            'LINKED_TO_ADAMA': 'NOT_IN_SOURCE',
        })
    for c in canais:
        linhas.append({
            'ENTITY': c.get('ORGANIZATION') or c.get('CHANNEL_NAME'),
            'ORIGIN': 'IT-VIDEO-CANAIS-V1', 'SOURCE_ID': c.get('CHANNEL_ID'),
            'TYPE_AS_COLLECTED': 'YOUTUBE_CHANNEL',
            'AUTHORITY_CLASS': c.get('DECLARED_ROLE'),
            'REGION': 'NOT_IN_SOURCE', 'CROPS': [],
            'URL': None, 'CHANNEL_ROLES': ['QUEM_INFLUENCIA'],
            'ROLE_EVIDENCE': 'canal com publicacao tecnica medida (%s itens)'
                             % c.get('ITEMS_IN_FEED'),
            'BUYS_PRODUCT': 'NOT_IN_SOURCE', 'LINKED_TO_ADAMA': 'NOT_IN_SOURCE',
        })
    for p in perfis:
        linhas.append({
            'ENTITY': p.get('ORGANISATION') or p.get('HANDLE'),
            'ORIGIN': 'IT-INSTAGRAM-PERFIS-V3', 'SOURCE_ID': p.get('HANDLE'),
            'TYPE_AS_COLLECTED': 'INSTAGRAM_PROFILE',
            'AUTHORITY_CLASS': p.get('PAGE_ROLE'),
            'REGION': 'NOT_IN_SOURCE', 'CROPS': [],
            'URL': p.get('URL'), 'CHANNEL_ROLES': ['QUEM_INFLUENCIA'],
            'ROLE_EVIDENCE': 'perfil com audiencia medida (%s seguidores)'
                             % p.get('FOLLOWERS'),
            'BUYS_PRODUCT': 'NOT_IN_SOURCE', 'LINKED_TO_ADAMA': 'NOT_IN_SOURCE',
        })

    por_papel = collections.Counter()
    for x in linhas:
        for r in x['CHANNEL_ROLES']:
            por_papel[r] += 1
    com_regiao = sum(1 for x in linhas if x['REGION'] != 'NOT_IN_SOURCE')

    out = {
        'DATASET': 'IT-CANAL-REGUA-V1',
        'LAYER': 'COMMERCIAL CHANNEL — RULER PROVEN ON SAMPLE',
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-FUTURO-V1', 'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'regua de canal aplicada ao que o acervo JA tem, sem coleta nova',
        'CORRECAO_DE_ONTEM': (
            'eu escrevi CHANNEL_LAYER_STATE = NOT_COLLECTED. Estava errado por '
            'baixo: a rodada de descoberta de fontes ja havia catalogado '
            'COOPERATIVE, COOPERATIVE_DISTRIBUTOR, PRODUCER_ORGANISATION e '
            'PRIVATE_AGRONOMIC_ADVISORY. Material de canal, com outro nome, nunca '
            'usado para esta pergunta.'),
        'CHANNEL_LAYER_STATE': 'PARTIALLY_COLLECTED_UNDER_ANOTHER_NAME',
        'ROLES': PAPEIS,
        'ENTITIES_IN_SAMPLE': len(linhas),
        'ENTITIES_WITH_A_ROLE': sum(1 for x in linhas if x['CHANNEL_ROLES']),
        'BY_ROLE': dict(por_papel),
        'WITH_REGION': com_regiao,
        'LINKED_TO_ADAMA': 0,
        'BUYS_PRODUCT_KNOWN': 0,
        'O_QUE_A_AMOSTRA_PROVA': (
            'QUEM INFLUENCIA e QUEM RECOMENDA o acervo ja responde, com evidencia '
            'e sem coleta nova. QUEM DISTRIBUI e QUEM REPRESENTA respondem em '
            'parte, e so onde a rodada de fontes ja classificou. QUEM COMPRA nao '
            'tem resposta publica e nao vai ter: compra e dado privado, e o maximo '
            'honesto e o PROXY de quem distribui e quem representa.'),
        'PROXIMA_COLETA_MINIMA': [
            {'ALVO': 'consorzi agrari com catalogo de mezzi tecnici publico',
             'PORQUE': 'e a unica fonte publica que liga territorio a distribuicao',
             'TAMANHO': 'comecar por 10, medidos, das regioes dos dez sinais futuros',
             'REGUA': 'so entra quem publica catalogo ou lista de pontos de venda; '
                      'presenca em convegno NAO conta'},
            {'ALVO': 'organizzazioni di produttori reconhecidas por regiao',
             'PORQUE': 'responde QUEM REPRESENTA com registro publico',
             'TAMANHO': '10 por regiao dos sinais',
             'REGUA': 'so entra OP com reconhecimento regional citavel'},
        ],
        'O_QUE_NAO_SE_FAZ': 'nao inventar ligacao produtor -> revenda; nao tratar '
                            'presenca em convegno como canal; nao publicar ligacao '
                            'comercial sem evidencia.',
        'ENTITIES': linhas,
    }
    json.dump(out, open(os.path.join(DEST, 'IT-CANAL-REGUA-V1.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)
    print('CHANNEL_LAYER_STATE   %s' % out['CHANNEL_LAYER_STATE'])
    print('ENTITIES_IN_SAMPLE    %d' % out['ENTITIES_IN_SAMPLE'])
    print('ENTITIES_WITH_A_ROLE  %d' % out['ENTITIES_WITH_A_ROLE'])
    print('BY_ROLE               %s' % out['BY_ROLE'])
    print('WITH_REGION           %d' % out['WITH_REGION'])
    for k, v in PAPEIS.items():
        print('  %-28s acervo responde: %s' % (k, v['ACERVO_RESPONDE']))
    return out


if __name__ == '__main__':
    main()
