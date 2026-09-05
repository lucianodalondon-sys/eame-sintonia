#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A LEI DE RELEVANCIA ADAMA — o unico dono da decisao «isto e uma oportunidade?»

    from adama_relevance import classificar, CONTRATO

POR QUE ESTE FICHEIRO EXISTE
----------------------------
O motor encontra CASOS. Um caso vira OPORTUNIDADE ADAMA quando — e so quando —
se consegue ligar o facto a um produto ADAMA de forma defensavel. Sem essa
ligacao a pergunta fica sem resposta:

    POR QUE ISTO E UM CASO PARA A ADAMA?

Medido nos 43 antes desta lei: 30 cartoes eram apresentados como oportunidade
sem conseguir responder. Vinte e um tinham produto ligado mas nenhum alvo
agronomico — provavam «este produto pode ser usado nesta cultura», nunca
«serve para este problema». Oito nao tinham produto nenhum. E um ligava AGIL
a arroz, uma cultura que a pagina de catalogo do proprio produto nao declara.

    UM PRODUTO QUE PODE SER USADO NA CULTURA NAO E UM PRODUTO QUE RESOLVE O
    PROBLEMA. A PRIMEIRA E UMA AUTORIZACAO; A SEGUNDA E UMA OPORTUNIDADE.

O QUE ESTA LEI NAO FAZ
----------------------
Nao apaga nada. Um caso que nao passa continua inteiro na materia-prima e
continua alcancavel — muda o NOME por que e chamado, e o sitio onde aparece.

    ESCONDER NAO E APAGAR. DEIXAR DE CHAMAR OPORTUNIDADE NAO E PERDER O SINAL.

Nao promove por preenchimento. Preencher `ISSUE_IDS` no catalogo faria os 21 B
subirem a A sem que ninguem tivesse provado que o facto agronomico e o produto
fecham. Esta lei exige a prova que o motor JA escreveu, nunca uma que se possa
inventar num campo vazio.

UM SO DONO
----------
Esta funcao e o unico sitio onde a classe se decide. `it_casa_dados.py`
importa-a e imprime o veredito no pacote; `meeting-surface.js` LE o veredito
impresso e nunca o recalcula. Duas implementacoes da mesma lei divergem na
terceira vez que alguem mexe numa.

    O AVALIADOR E UM. O RESTO TRANSPORTA.

FAIL-CLOSED: o que nao se prova nao sobe. Um caso que a lei nao sabe
classificar cai em E — nunca em A.
"""

# ── O CONTRATO, DITO ANTES DE SER APLICADO ──────────────────────────────────
CONTRATO = {
    'DATASET': 'ADAMA-RELEVANCE-LAW-V1',
    'LEI': ('todo caso promovido como inteligencia relevante tem de ter ligacao '
            'factual e defensavel com pelo menos um produto ADAMA. Sem ela, o caso '
            'continua a existir — como radar, sinal ou erro — mas nao como '
            'oportunidade.'),
    'CADEIA_EXIGIDA': [
        'PAIS', 'CULTURA', 'ALVO/PROBLEMA', 'PRODUTO ADAMA',
        'RELACAO produto x cultura (pagina de catalogo)',
        'RELACAO produto x alvo (rotulo ministerial)',
        'PROBLEMA OBSERVADO (evidencia que sustenta o sinal ou declara a direccao)',
        'AUTORIZACAO VIVA (registo + estado)',
    ],
    'PREENCHER_NAO_PROMOVE': (
        'TARGET_FIT vale ON_MINISTERIAL_LABEL em 65 de 65 correspondencias: e uma '
        'constante, e nao distingue nada. Se a lei se apoiasse nela, escrever um alvo '
        'no caso promovia-o — medido, 10 dos 21 B subiriam sem nada observado. Por isso '
        'o problema agronomico exige evidencia que DECIDA um elo (SUPPORTS_SIGNAL ou '
        'SUPPORTS_DIRECTION). Com a regra, preencher o alvo nos 21 B promove UM: '
        'OPP_00C5B6E15185, que ja traz 4 sinais de campo e 4 evidencias de sinal — '
        'esse subiria por ter facto, nao por ter campo cheio.'),
    'NAO_ACEITE': [
        'correspondencia lexical', 'mesmo ingrediente activo',
        'produto parecido', 'catalogo generico', 'template',
        'inferencia nao provada',
        'proximidade de data de expiracao europeia',
        'alvo escrito no caso sem fonte que o tenha observado',
    ],
    'BASTA_UM_PRODUTO': ('um caso e oportunidade se PELO MENOS UM produto fechar a '
                         'cadeia inteira. Os outros produtos ligados nao sao a prova '
                         'e nao a estragam — o cartao nomeia qual deles a carrega. '
                         'Exigir que TODOS fechassem derrubaria OPP_75C37DED9160, '
                         'onde Lamdex Extra fecha e MAVRIK SMART nao.'),
    'APPROVAL_EXPIRY_NAO_E_RISCO': (
        'uma data de expiracao europeia NAO e risco de nao-renovacao. Medido nos 47 '
        'factos regulatorios do pacote: EU_STATE=APPROVED e IS_RISK=false em 47/47, '
        'e o proprio artefacto declara «APPROVAL EXPIRY IS NOT NON-RENEWAL». '
        'Um facto regulatorio NUNCA contribui para a classe A por si so; precisa de '
        'facto adicional de risco, que hoje nao existe em registo nenhum.'),
    'CLASSES': {
        'A': 'PRODUTO ADAMA PROVADO — publica-se como OPORTUNIDADE',
        'B': 'PLAUSIVEL, NAO PROVADO — fica em RADAR / A VALIDAR',
        'C': 'SEM PRODUTO ADAMA LIGAVEL — fica como SINAL BRUTO',
        'D': 'LIGACAO ERRADA — NAO PUBLICAVEL, e um erro a corrigir',
        'E': 'NAO SEI — dados insuficientes; nunca sobe',
    },
    'SO_A_PUBLICA': True,
}

# Os valores canonicos que o motor escreve. Nao sao adivinhados: sao lidos do
# snapshot e qualquer outro valor faz a cadeia falhar fechada.
CATALOGO_DECLARA_A_CULTURA = 'DECLARED_ON_CATALOG_PAGE'
ROTULO_DECLARA_O_ALVO = 'ON_MINISTERIAL_LABEL'
AUTORIZACAO_VIVA = 'AUTHORIZATION_LIVE'

# ── O ALVO TEM DE SER OBSERVADO, NAO SO ESCRITO ─────────────────────────────
# `TARGET_FIT` vale ON_MINISTERIAL_LABEL em 65 de 65 correspondencias — e uma
# CONSTANTE, e uma constante nao distingue nada. Se a lei se apoiasse nela,
# bastaria escrever um alvo no caso para o promover: medido, 10 dos 21 B
# subiriam a A sem que nada tivesse sido observado no campo.
#
#     PREENCHER UM CAMPO NAO E DESCOBRIR UM FACTO.
#
# Por isso o problema agronomico exige EVIDENCIA que DECIDA um elo: uma fonte
# que sustenta o sinal, ou que declara a direccao. Medido: 13/13 dos A tem-na,
# e 9 dos 10 promoviveis por preenchimento nao tem nenhuma.
PAPEIS_QUE_DECIDEM_O_PROBLEMA = ('SUPPORTS_SIGNAL', 'SUPPORTS_DIRECTION')


def problema_evidenciado(caso):
    """→ True se uma fonte sustenta o sinal ou declara a direccao."""
    return any(e.get('ROLE') in PAPEIS_QUE_DECIDEM_O_PROBLEMA
               for e in (caso.get('EVIDENCE_ROLES') or []))


def produto_que_prova(caso):
    """→ o primeiro produto ADAMA que fecha a cadeia inteira, ou None.

    A ordem e a do motor; nao se escolhe o «melhor», escolhe-se o primeiro que
    PROVA. Escolher entre produtos que provam seria decidir no lugar do motor,
    e o motor ja declarou que nao tem regra para isso (PRIMARY_MATCH_REASON =
    SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER em 26 dos 43).
    """
    if not caso.get('CROP') or not caso.get('TARGET'):
        return None
    if not problema_evidenciado(caso):
        return None                        # alvo escrito sem nada observado
    catalogo = set(caso.get('MATCHED_COMMERCIAL_PRODUCT_IDS') or [])
    if not catalogo:
        return None
    for m in (caso.get('PORTFOLIO_MATCHES') or []):
        if m.get('PRODUCT_ID') not in catalogo:
            continue                       # nao esta no catalogo comercial ADAMA
        if m.get('CROP_FIT') != CATALOGO_DECLARA_A_CULTURA:
            continue                       # a pagina do produto nao declara a cultura
        if m.get('TARGET_FIT') != ROTULO_DECLARA_O_ALVO:
            continue                       # o rotulo ministerial nao declara o alvo
        if m.get('REGULATORY_FIT') != AUTORIZACAO_VIVA:
            continue                       # autorizacao nao viva
        if not m.get('REGISTRATION_NUMBER'):
            continue                       # sem numero de registo nao ha prova
        return m
    return None


def ativo_adama_nomeado(caso):
    """→ True se o caso nomeia um PRODUTO ADAMA registado afectado.

    E a excepcao estrategica: pode nao haver produto comercializavel hoje e
    ainda assim existir um activo ADAMA em jogo. Mas nomear nao e provar — ver
    APPROVAL_EXPIRY_NAO_E_RISCO. Por isso isto leva a B, nunca a A.
    """
    tipos = {e.get('ENTITY_TYPE') for e in (caso.get('EVIDENCE_ROLES') or [])}
    return 'REGULATORY_PRODUCT' in tipos and 'REGULATORY_FUTURE_FACT' in tipos


def classificar(caso):
    """→ (classe, porque). O unico sitio onde a classe se decide."""
    tem_produto = bool(caso.get('MATCHED_COMMERCIAL_PRODUCT_IDS'))
    tem_alvo = bool(caso.get('TARGET'))
    prova = produto_que_prova(caso)

    if prova is not None:
        return 'A', 'RELEVANCE_A_PROVEN'

    if tem_produto and tem_alvo:
        # ha produto e ha alvo, e mesmo assim nenhum produto fecha a cadeia:
        # a ligacao que o cartao mostra nao sobrevive a auditoria.
        return 'D', 'RELEVANCE_D_LINK_FAILS'

    if tem_produto and not tem_alvo:
        return 'B', 'RELEVANCE_B_NO_TARGET'

    if not tem_produto and ativo_adama_nomeado(caso):
        return 'B', 'RELEVANCE_B_NAMED_ASSET_NO_RISK'

    if not tem_produto:
        return 'C', 'RELEVANCE_C_NO_LINK'

    return 'E', 'RELEVANCE_E_UNKNOWN'       # fail-closed: nunca sobe


# A superficie onde cada classe pode aparecer. Nada desaparece: muda de nome.
SUPERFICIE = {'A': 'OPPORTUNITA', 'B': 'RADAR', 'C': 'SEGNALI', 'D': 'ERRORE', 'E': 'ERRORE'}
PUBLICAVEL_COMO_OPORTUNIDADE = ('A',)


def restricoes_separadas(caso):
    """As restricoes do produto ADAMA ligado, e as dos OUTROS activos.

    Medido: 40 das 114 restricoes citam um activo que nao esta em nenhum
    produto ADAMA ligado ao caso — vem do superset ACTIVE_INGREDIENT_NAMES,
    que inclui activos nomeados pelas fontes e pela concorrencia.

        MOSTRAR A EXPIRACAO DO ACTIVO DO CONCORRENTE COMO SE FOSSE A NOSSA
        NAO E UM ERRO DE ETIQUETA: E UMA DECISAO COMERCIAL TOMADA AO CONTRARIO.

    Uma nunca pode aparecer como a outra. Separam-se aqui, na origem.
    """
    nossos = {a for m in (caso.get('PORTFOLIO_MATCHES') or [])
              for a in (m.get('ACTIVE_INGREDIENTS') or [])}
    minhas, outras = [], []
    for r in (caso.get('PRODUCT_RESTRICTIONS') or []):
        (minhas if r.get('ACTIVE_INGREDIENT') in nossos else outras).append(r)
    return minhas, outras


def contar(casos):
    """→ contagem por classe, para quem precisa provar a populacao."""
    c = {k: 0 for k in 'ABCDE'}
    for caso in casos:
        c[classificar(caso)[0]] += 1
    return c
