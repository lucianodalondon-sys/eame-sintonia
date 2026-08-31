#!/usr/bin/env python3
"""
QUATRO PERGUNTAS QUE VIRARAM UMA — e a correcao que as separa de novo.

A auditoria anterior escreveu que o papel/localidade da pagina podia ser provado
"empiricamente pelo perfil de entrega": a pagina `Bayer Crop Science Espana`
tinha 209 anuncios na Espanha e zero na Italia e na Franca, logo seria uma
pagina espanhola. O coordenador recusou, e a recusa esta certa.

    ANUNCIOS_ENTREGUES_NA_ES  !=  PAGINA_E_ESPANHOLA
    ANUNCIOS_ENTREGUES_NA_FR  !=  PAGINA_E_FRANCESA

Uma pagina global pode escolher anunciar so num pais. A distribuicao mede a
DECISAO DE MIDIA daquela janela, nao a nacionalidade da entidade. Confundir as
duas transformava uma observacao de campanha em fato cadastral — e um fato
cadastral errado contamina tudo o que se apoiar nele depois.

AS QUATRO PERGUNTAS, SEPARADAS PARA SEMPRE
-------------------------------------------
    PAGE_IDENTITY          quem e esta pagina? -> PAGE_ID, PAGE_NAME
    PAGE_COUNTRY_SCOPE     a pagina e de um pais? -> so com prova da fonte
    PAGE_ROLE              e pagina de empresa ou de marca/produto?
    AD_DELIVERY_COUNTRY    em que pais os anuncios foram entregues?

A quarta continua valendo mesmo quando a segunda e NOT_PROVED. Dizer

    "esta pagina teve anuncios observados na Espanha"

nao exige saber de onde a pagina e. E por isso a unidade da Meta pode seguir
sendo COMPETITOR x PAGE_ID x AD_DELIVERY_COUNTRY x SNAPSHOT.

O QUE CONTA COMO PROVA DE PAIS DA PAGINA
-----------------------------------------
Uma so coisa: o rotulo que a PROPRIA META escreve no painel de paginas irmas
("Syngenta / Agricultural Service / Italy"). Nao conta o nome da pagina, nao
conta o idioma do anuncio, e agora tambem nao conta a distribuicao de entrega.

Resultado medido em 31/08/2026: das 23 paginas com PAGE_ID provado, apenas
UMA carrega esse rotulo. As outras 22 ficam NOT_PROVED — e ficar NOT_PROVED e
a resposta correta, nao uma falha da coleta.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

LOCAL_PROVED = 'LOCAL_COUNTRY_PROVED'
GLOBAL_PROVED = 'GLOBAL_PROVED'
SCOPE_NOT_PROVED = 'NOT_PROVED'

ROLE_COMPANY = 'COMPANY'
ROLE_BRAND = 'BRAND_PRODUCT'
ROLE_OTHER = 'OTHER_PROVED_ROLE'
ROLE_NOT_PROVED = 'NOT_PROVED'

# A unica prova de pais aceita: o rotulo da Meta no painel de irmas.
PROVA_ROTULO_META = 'PAGE_ID_FROM_SIBLING_PANEL_CLICK'
ROTULO_PAIS = {'Spain': 'ES', 'Italy': 'IT', 'France': 'FR'}


# ── guarda de identidade do anunciante ───────────────────────────────────────
# O CASO QUE ORIGINOU ESTA GUARDA
# --------------------------------
# A resolucao da ADAMA aceitou como pagina da empresa o `Instytut Adama
# Mickiewicza` — um instituto cultural polones, batizado em homenagem ao poeta
# Adam Mickiewicz. "Adama" ali e o genitivo de "Adam", nao a marca. O casamento
# foi por token solto no meio do nome, e entraram 33 cartoes de 40 no acervo
# PROPRIO da ADAMA: 82% do dataset era outra entidade.
#
#     TOKEN_NO_MEIO_DO_NOME != MESMA_EMPRESA
#
# A regra abaixo nao e uma lista negra de um caso. E estrutural: o token da
# empresa precisa abrir o nome da pagina. Marca costuma vir na frente
# ("ADAMA Ltd.", "Bayer Crop Science Espana", "UPL Iberia", "Certis Belchim
# Espana"); homonimo pessoal costuma vir no meio ("Instytut ADAMA Mickiewicza").
#
# O que esta guarda NAO faz: nao decide relevancia agro. `FMC Moto Srl` passa,
# porque e outro tipo de erro — nome de empresa igual, negocio diferente. Esse
# fica visivel no acervo, com zero sinal agro nos anuncios, e nao e problema
# desta guarda resolver.
IDENTIDADE_ACEITA = 'ADVERTISER_IDENTITY_ACCEPTED'
IDENTIDADE_RECUSADA = 'ADVERTISER_IDENTITY_REJECTED_TOKEN_NOT_LEADING'


def _tokens(nome):
    return [t for t in ''.join(
        c if (c.isalnum() or c.isspace()) else ' ' for c in (nome or '')).split() if t]


def guarda_identidade(page_name, empresa):
    """O token da empresa precisa ABRIR o nome da pagina."""
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


def filtrar_por_identidade(entidades, empresa):
    """Separa o acervo em aceitos e recusados, preservando os recusados."""
    aceitos, recusados = {}, {}
    for k, e in (entidades or {}).items():
        g = guarda_identidade(e.get('page_name_resolved'), empresa)
        if g['state'] == IDENTIDADE_ACEITA:
            aceitos[k] = e
        else:
            e = dict(e)
            e['rejected_by'] = g
            recusados[k] = e
    return aceitos, recusados


def escopo_de_pais(pagina):
    """So promove a pagina com prova da FONTE. Nome nao promove. Entrega nao promove."""
    rotulo = pagina.get('country_label_by_meta')
    if rotulo and rotulo in ROTULO_PAIS:
        return {'page_country_scope': LOCAL_PROVED,
                'country_code': ROTULO_PAIS[rotulo],
                'proof': 'META_SIBLING_PANEL_COUNTRY_LABEL',
                'evidence': rotulo}
    if rotulo and 'other locations' in rotulo:
        # "Argentina and other locations" prova que NAO e de um pais so.
        return {'page_country_scope': GLOBAL_PROVED, 'country_code': None,
                'proof': 'META_SIBLING_PANEL_MULTI_COUNTRY_LABEL',
                'evidence': rotulo}
    return {'page_country_scope': SCOPE_NOT_PROVED, 'country_code': None,
            'proof': None,
            'evidence': None,
            'nota': 'a fonte nao rotulou o pais desta pagina. Nome da pagina e '
                    'distribuicao de entrega NAO promovem a NOT_PROVED.'}


def papel(pagina):
    """PAGE_ROLE precisa de prova, e a Biblioteca nao publica esse campo.

    A categoria que aparece no painel ("Agricultural Service") descreve o
    NEGOCIO, nao diz se a pagina representa a empresa ou uma marca de produto.
    Sem fonte que declare isso, o estado honesto e NOT_PROVED.
    """
    return {'page_role': ROLE_NOT_PROVED,
            'category_declared_by_source': pagina.get('category'),
            'nota': 'a Biblioteca nao publica papel de pagina. Categoria de '
                    'negocio nao e papel.'}


def paises_de_entrega(page_id, diagnosticos):
    """AD_DELIVERY_COUNTRY: pergunta separada, e continua valendo sozinha."""
    saida = {}
    for d in diagnosticos or []:
        if d.get('page_id') != page_id:
            continue
        saida[d.get('country')] = {
            'ads_observed_cards': d.get('cards_read'),
            'ads_represented': d.get('ads_represented'),
            'slice_state': d.get('completeness'),
        }
    return saida


def inventario(arquivo_anunciantes, acervo):
    """Uma linha por pagina, com as quatro perguntas em colunas diferentes."""
    with open(arquivo_anunciantes, encoding='utf-8') as f:
        adv = json.load(f)
    diag = (acervo or {}).get('collection_diagnostics', [])
    linhas = []
    for c in adv.get('companies', []):
        for p in c.get('pages', []):
            if not p.get('page_id'):
                continue
            esc = escopo_de_pais(p)
            linhas.append({
                'competitor': c['company'],
                'page_identity': {
                    'page_id': p['page_id'],
                    'page_name': p.get('page_name'),
                    'state': 'PROVED',
                    'proof': p.get('identity_proof'),
                    'evidence_url': p.get('evidence_url'),
                },
                'page_country_scope': esc,
                'page_role': papel(p),
                'ad_delivery_country': paises_de_entrega(p['page_id'], diag),
                'nota': ('page_country_scope e ad_delivery_country sao perguntas '
                         'diferentes. A segunda vale mesmo com a primeira '
                         'NOT_PROVED.'),
            })
    return linhas


def resumo(linhas):
    def conta(estado):
        return sum(1 for l in linhas
                   if l['page_country_scope']['page_country_scope'] == estado)
    return {
        'page_ids_proved': len(linhas),
        'page_country_scope_local_proved': conta(LOCAL_PROVED),
        'page_country_scope_global_proved': conta(GLOBAL_PROVED),
        'page_country_scope_not_proved': conta(SCOPE_NOT_PROVED),
        'page_roles_proved': sum(1 for l in linhas
                                 if l['page_role']['page_role'] != ROLE_NOT_PROVED),
        'ad_delivery_countries': ['ES', 'IT', 'FR'],
        'aviso': ('PROVED_LOCAL_META_PAGES conta SOMENTE paginas rotuladas por '
                  'pais pela propria Meta. Distribuicao de entrega nao entra '
                  'nesta conta — e a pergunta ao lado, nao esta.'),
    }
