#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAMADA DE CONVERGÊNCIA — o encontro das duas réguas, embalado para a tela.

Dois arquivos entram no pacote:

    LABEL-USE/label-use-pairs.json    o que o rótulo autoriza  (2.030 pares)
    CONVERGENCE/convergence.json      o encontro com a conversa (38 + 78 + 282)

⚠️ O NÚMERO DE CAPA MUDOU, E COM ELE UMA LIMITAÇÃO INTEIRA
-----------------------------------------------------------
Até 01/09 o pacote declarava cobertura de uso lido de **19 em 163 (11,7%)** e a
chamava de sua limitação mais cara. Depois de ler os 163 rótulos por dentro, a
cobertura é **102 em 163 (62,6%)**.

A limitação não desapareceu — encolheu. Continuam **61 produtos** sem par lido, e
para cada um deles a frase permitida é a mesma de antes:

    «não encontramos linha que ligue cultura e alvo NESTA LEITURA» — não
    «a ADAMA não tem produto».

TRÊS FORÇAS DE LIGAÇÃO, E ELAS NÃO SE SOMAM
--------------------------------------------
    LINHA_DA_TABELA        o documento une cultura e alvo na mesma linha
    BLOCO_DA_CULTURA       a cultura encabeça o bloco, o alvo está dentro dele
    DECLARACAO_DE_PRODUTO  o rótulo declara as duas listas SEPARADAS e nós as
                           aproximamos — é o mais fraco, e o único que é nosso

A tela que somar os três produz um número que nenhuma das três sustenta.
"""
import os

from pacote_normalizar import DR, env, grava, local_json, novo_id  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def camada_convergencia():
    rot = local_json(os.path.join('IT-ROTULOS', 'IT-ROTULOS-PARES.json'))
    cru = local_json(os.path.join('IT-CRUZAMENTO', 'IT-CONVERSA-X-ROTULO.json'))
    if not rot or not cru:
        print('  (sem artefato de rotulo ou de cruzamento — camada nao gerada)')
        return

    # ── 1 · o que o rótulo autoriza ────────────────────────────────────────────
    pares = []
    for p in rot['PARES']:
        pares.append({
            'ID': novo_id('IT-LBL'),
            'CROP': p['CULTURA_CANONICA'],
            'TARGET': p['ALVO_CANONICO'],
            'TARGET_AS_WRITTEN_ON_LABEL': p['ALVO_LITERAL'],
            'TARGET_KIND': p.get('ALVO_E'),
            'WEED_GROUP': p.get('ALVO_GRUPO'),
            'PRODUCT': p['PRODUCT'],
            'REGISTRATION_ID': p['REGISTRATION_ID'],
            'LINK_STRENGTH': p.get('LIGACAO_NIVEL'),
            'LINK_MEANS': p.get('LIGACAO_O_QUE_SIGNIFICA'),
            'QUOTE_FROM_LABEL': (p.get('CITACAO_DA_LINHA') or '')[:300],
            'SOURCE': 'Ministero della Salute · rotulo autorizado (PDF)',
            'EVIDENCE_CLASS': 'OFFICIAL_DOCUMENT',
            # A proveniencia segue a forca da ligacao, e nao poderia ser outra:
            # quando o DOCUMENTO une cultura e alvo, o par e fato lido. Quando
            # somos NOS que aproximamos duas listas separadas, e derivacao nossa.
            'PROVENANCE': ('REAL_FACT'
                           if p.get('LIGACAO_NIVEL') in ('LINHA_DA_TABELA',
                                                         'BLOCO_DA_CULTURA')
                           else 'REAL_DERIVED'),
            'WHAT_IT_DOES_NOT_PROVE': p.get('O_QUE_NAO_PROVA'),
        })

    lidos = [x for x in rot['POR_PRODUTO']
             if x['ESTADO_DA_LEITURA'].startswith('LIDO')]
    grava('LABEL-USE', 'label-use-pairs.json', dict(
        env('LABEL_USE_PAIRS',
            ['data/samples/IT-ROTULOS/IT-ROTULOS-PARES.json',
             'data/raw/IT-ROTULOS/_MANIFESTO.json'],
            'MINISTERO_LABEL_PDF',
            'par cultura x alvo lido DENTRO do rotulo autorizado'),
        **{
            'COUNT': len(pares),
            'PRODUCTS_IN_REGISTRY': len(rot['POR_PRODUTO']),
            'PRODUCTS_WITH_A_PAIR_READ': len(lidos),
            'USE_COVERAGE': rot['COBERTURA'],
            'COVERAGE_WAS_BEFORE_THIS_READING': '19/163 (11.7%)',
            'COVERAGE_IS_A_FLOOR':
                'ausencia aqui e ausencia NA NOSSA LEITURA, nunca no registro. '
                '61 produtos seguem sem par lido.',
            'FORBIDDEN_CLAIM': 'ADAMA has no product for X',
            'PAIRS_BY_LINK_STRENGTH': rot['PARES_POR_NIVEL_DE_LIGACAO'],
            'LINK_STRENGTHS_DO_NOT_ADD_UP': rot['LEI_DO_NIVEL_DE_LIGACAO'],
            'UNMAPPED_TARGETS': rot['ALVOS_NAO_MAPEADOS'],
            'UNMAPPED_MEANS':
                'o literal do rotulo esta preservado; falta o nome canonico NOSSO. '
                'O fato nao se perde.',
            'PAIRS': pares,
        }))

    # ── 2 · o encontro ─────────────────────────────────────────────────────────
    conv = []
    for c in cru['CONVERGENCIA']:
        conv.append({
            'ID': novo_id('IT-CONV'),
            'PAIR': c['PAR_DA_CONVERSA'],
            'CROP': c['CULTURA'],
            'TARGET': c['ALVO'],
            'PRODUCT_CATEGORY': c.get('CATEGORIA_DE_PRODUTO'),
            'PUBLIC_CONVERSATION_LEVEL': c['CONVERSA_NIVEL'],
            'PUBLIC_CONVERSATION_DOCS': c['CONVERSA_DOCUMENTOS'],
            'PUBLIC_CONVERSATION_SOURCES': c['CONVERSA_FONTES'],
            'AUDIENCE_VERDICT': c.get('CONVERSA_PLATEIA'),
            'AUDIENCE_DETAIL': c.get('CONVERSA_PLATEIA_DETALHE'),
            'ADAMA_PRODUCTS': c.get('PRODUTOS_ADAMA'),
            'ADAMA_PRODUCT_COUNT': c.get('N_PRODUTOS'),
            'LABEL_LINK_STRENGTHS': c.get('ROTULO_NIVEIS_DE_LIGACAO'),
            'LABEL_HAS_TABLE_ROW': c.get('ROTULO_TEM_LINHA_DE_TABELA'),
            'QUOTE_FROM_LABEL': c.get('CITACAO_DO_ROTULO'),
            'CONVERGENCE_STRENGTH': c.get('CONVERGENCIA_FORCA'),
            'VOCABULARY_TRANSLATION_CROP': c.get('TRADUCAO_DE_CULTURA'),
            'VOCABULARY_TRANSLATION_TARGET': c.get('TRADUCAO_DE_ALVO'),
            'PROVENANCE': 'REAL_DERIVED',
            'PROVENANCE_WHY': 'o encontro das duas leituras e ato nosso; cada leitura '
                              'isolada e que e fato',
            'WHAT_IT_SUPPORTS': c.get('O_QUE_ISTO_SUSTENTA'),
            'WHAT_IT_DOES_NOT_SUPPORT': c.get('O_QUE_ISTO_NAO_SUSTENTA'),
        })

    sem_leitura = [{
        'ID': novo_id('IT-NOREAD'),
        'PAIR': x['PAR_DA_CONVERSA'],
        'CROP': x['CULTURA'],
        'TARGET': x['ALVO'],
        'PUBLIC_CONVERSATION_LEVEL': x['CONVERSA_NIVEL'],
        'PUBLIC_CONVERSATION_DOCS': x['CONVERSA_DOCUMENTOS'],
        'AUDIENCE_VERDICT': x.get('CONVERSA_PLATEIA'),
        'PROVENANCE': 'REAL_DERIVED',
        'READ_IT_LIKE_THIS': x['LEIA_ASSIM'],
        'FORBIDDEN_CLAIM': x['AFIRMACAO_PROIBIDA'],
        'ALLOWED_CLAIM': x['AFIRMACAO_PERMITIDA'],
    } for x in cru['CONVERSA_SEM_LEITURA']]

    sem_conversa = [{
        'ID': novo_id('IT-NOTALK'),
        'PAIR': x['PAR_DO_ROTULO'],
        'CROP': x['CULTURA'],
        'TARGET': x['ALVO'],
        'TARGET_KIND': x.get('ALVO_E'),
        'ADAMA_PRODUCT_COUNT': x['N_PRODUTOS'],
        'ADAMA_PRODUCTS': x['PRODUTOS_ADAMA'],
        'LABEL_LINK_STRENGTHS': x['ROTULO_NIVEIS_DE_LIGACAO'],
        'PROVENANCE': 'REAL_DERIVED',
        'READ_IT_LIKE_THIS': x['LEIA_ASSIM'],
        'FORBIDDEN_CLAIM': x['AFIRMACAO_PROIBIDA'],
    } for x in cru['ROTULO_SEM_CONVERSA']]

    grava('CONVERGENCE', 'convergence.json', dict(
        env('CONVERGENCE',
            ['data/samples/IT-CRUZAMENTO/IT-CONVERSA-X-ROTULO.json',
             'data/samples/IT-REGUA/IT-PARES-CULTURA-ALVO-V0.json',
             'data/samples/IT-ROTULOS/IT-ROTULOS-PARES.json'],
            'SINTONIA_CROSSING',
            'encontro entre a conversa publica italiana e o rotulo autorizado'),
        **{
            'COUNT': len(conv),
            'THE_THREE_DRAWERS_DO_NOT_ADD_UP': cru['AS_TRES_GAVETAS_NAO_SE_SOMAM'],
            'VOCABULARY_RECONCILIATION': cru['EQUIVALENCIAS_DECLARADAS'],
            'CONVERGENCE_COUNT': len(conv),
            'CONVERGENCE_WITH_PROFESSIONAL_AUDIENCE':
                cru['CONVERGENCIA_COM_PLATEIA_PROFISSIONAL'],
            'AUDIENCE_WARNING':
                'convergencia sustentada so por canal de horta domestica descreve '
                'conversa de jardim. Na tela ela NAO pode ter o mesmo peso que uma '
                'sustentada por canal profissional.',
            'TALKED_ABOUT_BUT_NOT_READ_COUNT': len(sem_leitura),
            'AUTHORIZED_BUT_NOT_IN_OUR_CORPUS_COUNT': len(sem_conversa),
            'CONVERGENCE': conv,
            'TALKED_ABOUT_BUT_NOT_READ': sem_leitura,
            'AUTHORIZED_BUT_NOT_IN_OUR_CORPUS': sem_conversa,
        }))
