#!/usr/bin/env python3
"""
QUEM É O ANUNCIANTE — a régua que CARIMBA a página no momento em que ela entra
na linha da Meta.

Trazido do ramo `claude/eame-meta-competitor` (a2fad2d0, 31/08/2026):
`scripts/meta_identidade.py` (a guarda e o escopo) e `scripts/meta_adama.py` (a
aplicação da guarda ao acervo próprio, que vive aqui como `filtrar_por_identidade`).
Régua que carimba (AGENTS.md: `regras/`) porque `coleta/concorrencia_meta.py` a
usa ANTES de visitar a página — página recusada não é visitada.

AS QUATRO PERGUNTAS, SEPARADAS PARA SEMPRE
-------------------------------------------
    PAGE_IDENTITY          quem é esta página? -> PAGE_ID, provado pela Meta
    PAGE_COUNTRY_SCOPE     a página é de um país? -> só com rótulo da Meta
    PAGE_ROLE              empresa ou marca? -> a Biblioteca não publica: NOT_PROVED
    AD_DELIVERY_COUNTRY    onde os anúncios foram entregues? -> o `country=`

    ANUNCIOS_ENTREGUES_NA_IT  !=  PAGINA_E_ITALIANA

A quarta vale sozinha: «esta página teve anúncios que alcançaram a Itália» não
exige saber de onde a página é.

A PROVA DE PAGE_ID — duas, e só estas
--------------------------------------
    PAGE_ID_FROM_AD_DETAIL_URL        abrir `?id=<library_id>` faz a própria
                                      Meta reescrever o endereço com
                                      `view_all_page_id=<número>`
    PAGE_ID_FROM_SIBLING_PANEL_CLICK  «Similar regional ads»: a Meta lista a
                                      irmã COM rótulo de país e o clique revela
                                      o id

Nome da página NÃO é prova de PAGE_ID. Página sem uma destas provas não entra
na lista da linha — fica na fila de descoberta.

A GUARDA DE IDENTIDADE (o caso que a fez nascer)
-------------------------------------------------
`Instytut Adama Mickiewicza` — instituto cultural polaco — entrou como ADAMA por
token solto no meio do nome: 33 de 40 cartões do acervo próprio eram ele.

    TOKEN_NO_MEIO_DO_NOME != MESMA_EMPRESA

O token da empresa tem de ABRIR o nome da página. A guarda NÃO decide relevância
agro: `FMC Moto Srl` passa (mesmo nome, outro negócio). Por isso a lista da
linha carrega `agro_relevance` à parte, e a página conhecida como não-agro é
recusada POR DECLARAÇÃO na lista, com o motivo escrito — nunca em silêncio.
"""
PROVA_DETALHE = 'PAGE_ID_FROM_AD_DETAIL_URL'
PROVA_IRMA = 'PAGE_ID_FROM_SIBLING_PANEL_CLICK'
PROVAS_DE_PAGE_ID = (PROVA_DETALHE, PROVA_IRMA)

LOCAL_PROVED = 'LOCAL_COUNTRY_PROVED'
GLOBAL_PROVED = 'GLOBAL_PROVED'
SCOPE_NOT_PROVED = 'NOT_PROVED'
ROLE_NOT_PROVED = 'NOT_PROVED'

ROTULO_PAIS = {'Spain': 'ES', 'Italy': 'IT', 'France': 'FR'}

IDENTIDADE_ACEITA = 'ADVERTISER_IDENTITY_ACCEPTED'
IDENTIDADE_RECUSADA = 'ADVERTISER_IDENTITY_REJECTED_TOKEN_NOT_LEADING'
PAGE_ID_NAO_PROVADO = 'PAGE_ID_NOT_PROVED_BY_META'


def _tokens(nome):
    return [t for t in ''.join(
        c if (c.isalnum() or c.isspace()) else ' ' for c in (nome or '')).split() if t]


def guarda_identidade(page_name, empresa):
    """O token da empresa precisa ABRIR o nome da página."""
    alvo = _tokens(empresa)[0].lower() if _tokens(empresa) else ''
    toks = _tokens(page_name)
    primeiro = toks[0].lower() if toks else ''
    if alvo and primeiro.startswith(alvo):
        return {'state': IDENTIDADE_ACEITA, 'leading_token': toks[0]}
    return {'state': IDENTIDADE_RECUSADA, 'leading_token': toks[0] if toks else None,
            'expected_leading_token': alvo,
            'nota': ('o nome da empresa aparece fora da posicao inicial. '
                     'Casamento nominal no meio do nome nao prova mesma '
                     'entidade — foi assim que o Instytut Adama Mickiewicza '
                     'entrou como ADAMA.')}


def page_id_provado(pagina):
    """O PAGE_ID tem prova da PRÓPRIA META? Número sem prova não conta."""
    pid = str((pagina or {}).get('page_id') or '').strip()
    return bool(pid.isdigit() and len(pid) >= 6
                and pagina.get('identity_proof') in PROVAS_DE_PAGE_ID)


def carimbar(pagina):
    """O carimbo de entrada de UMA página da lista. → (entra, motivo)."""
    if not page_id_provado(pagina):
        return False, PAGE_ID_NAO_PROVADO
    g = guarda_identidade(pagina.get('page_name'), pagina.get('company'))
    if g['state'] != IDENTIDADE_ACEITA:
        return False, g['state']
    return True, IDENTIDADE_ACEITA


def filtrar_por_identidade(entidades, empresa):
    """Separa o acervo em aceitos e recusados, PRESERVANDO os recusados.

        RECUSADO != APAGADO
    """
    aceitos, recusados = {}, {}
    for k, e in (entidades or {}).items():
        g = guarda_identidade(e.get('page_name_resolved') or e.get('page_name'), empresa)
        if g['state'] == IDENTIDADE_ACEITA:
            aceitos[k] = e
        else:
            e = dict(e)
            e['rejected_by'] = g
            recusados[k] = e
    return aceitos, recusados


def escopo_de_pais(pagina):
    """Só promove a página com prova da FONTE. Nome não promove. Entrega não promove."""
    rotulo = (pagina or {}).get('country_label_by_meta')
    if rotulo and rotulo in ROTULO_PAIS:
        return {'page_country_scope': LOCAL_PROVED,
                'country_code': ROTULO_PAIS[rotulo],
                'proof': 'META_SIBLING_PANEL_COUNTRY_LABEL', 'evidence': rotulo}
    if rotulo and 'other locations' in rotulo:
        return {'page_country_scope': GLOBAL_PROVED, 'country_code': None,
                'proof': 'META_SIBLING_PANEL_MULTI_COUNTRY_LABEL', 'evidence': rotulo}
    return {'page_country_scope': SCOPE_NOT_PROVED, 'country_code': None,
            'proof': None, 'evidence': None,
            'nota': 'a fonte nao rotulou o pais desta pagina. Nome da pagina e '
                    'distribuicao de entrega NAO promovem a NOT_PROVED.'}
