#!/usr/bin/env python3
"""
O RELOGIO DA CONCORRENCIA — um anuncio visto duas vezes e UM anuncio, duas vezes.

Esta e a diferenca entre um acervo que serve para "o que mudou hoje?" e uma
planilha que incha sozinha. A regra e curta:

    MESMO META_AD_LIBRARY_ID  ->  UMA entidade, N observacoes
    NUNCA                     ->  N entidades

O QUE ESTE ARQUIVO DECIDE
--------------------------
Funde snapshots de coletas diferentes em entidades com relogio:

    FIRST_OBSERVED   a primeira vez que NOS vimos
    LAST_OBSERVED    a ultima vez que NOS vimos
    START_DATE       a data que a FONTE declara de inicio de veiculacao
    END_DATE         idem, de fim

FIRST_OBSERVED nao e START_DATE, e a confusao entre os dois e cara: um anuncio
que comecou em julho e foi visto por nos pela primeira vez hoje NAO e um anuncio
novo. Por isso existem dois eventos distintos, e nunca um so:

    NEW_AD_OBSERVED       apareceu num snapshot nosso pela primeira vez
    NEW_AD_BY_START_DATE  a fonte diz que a veiculacao comecou depois da
                          coleta anterior — so entao ha novidade no mundo

E O QUE ELE SE RECUSA A DECIDIR
--------------------------------
Com UM snapshot so, nao existe mudanca. Um acervo de uma foto so devolve
`BASELINE_ONLY` em todos os eventos comparativos — nao `NENHUMA_MUDANCA`, que
seria afirmar que nada mudou quando na verdade nao houve com o que comparar.

    SEM_LINHA_DE_BASE != SEM_MUDANCA

Tambem nao produz intensidade. Contar anuncios nao mede investimento, e a
missao proibe ate o rascunho disso:

    AD_COUNT != SPEND        AD_COUNT != SHARE_OF_VOICE

`AD_STOPPED_OBSERVED` merece cuidado extra: um anuncio some da listagem tanto
quando para quanto quando a rolagem nao chegou nele. Por isso o evento so e
emitido se o snapshot anterior E o novo forem COMPLETE_MATCHES_SOURCE_COUNT
recorte; se nao forem, sai `AD_ABSENT_UNEXPLAINED`.
"""
import copy

NEW_AD_OBSERVED = 'NEW_AD_OBSERVED'
NEW_AD_BY_START_DATE = 'NEW_AD_BY_START_DATE'
AD_STILL_ACTIVE = 'AD_STILL_ACTIVE'
AD_STOPPED_OBSERVED = 'AD_STOPPED_OBSERVED'
AD_ABSENT_UNEXPLAINED = 'AD_ABSENT_UNEXPLAINED'
AD_ACTIVE_AGAIN = 'AD_ACTIVE_AGAIN'
CREATIVE_TEXT_CHANGED = 'CREATIVE_TEXT_CHANGED'
STATUS_CHANGED = 'STATUS_CHANGED'
NEW_COUNTRY_ACTIVITY = 'NEW_COUNTRY_ACTIVITY'
BASELINE_ONLY = 'BASELINE_ONLY'

# so este estado autoriza afirmar que um anuncio PAROU. Ver meta_navegador.py:
# a regra antiga ('parou de crescer') marcou como completa uma leitura de 29
# cartoes numa pagina de 230, e teria produzido 160 'parou de veicular' falsos.
COMPLETA_OBSERVADA = 'COMPLETE_MATCHES_SOURCE_COUNT'


def chave(anuncio):
    """A identidade. Sem library_id nao ha entidade — e melhor recusar do que
    inventar uma chave por texto, que colaria dois anuncios diferentes."""
    lid = (anuncio or {}).get('meta_ad_library_id')
    return str(lid) if lid else None


def _observacao(anuncio):
    return {
        'as_of_date': anuncio.get('as_of_date'),
        'active_status': anuncio.get('active_status'),
        'country_reached': anuncio.get('country_reached'),
        'creative_text_hash': anuncio.get('creative_text_hash'),
        'collection_completeness': anuncio.get('collection_completeness'),
    }


def fundir(entidades, snapshot):
    """Funde um snapshot (lista de anuncios) no acervo de entidades.

    Devolve (entidades_novas, eventos). Nao altera a entrada.
    """
    ent = copy.deepcopy(entidades or {})
    eventos = []
    primeira_rodada = not ent
    vistos_agora = set()

    for a in snapshot or []:
        k = chave(a)
        if not k:
            continue
        vistos_agora.add(k)
        obs = _observacao(a)
        if k not in ent:
            novo = {kk: vv for kk, vv in a.items() if kk != 'as_of_date'}
            novo['meta_ad_library_id'] = k
            novo['first_observed'] = a.get('as_of_date')
            novo['last_observed'] = a.get('as_of_date')
            novo['countries_reached_observed'] = (
                [a['country_reached']] if a.get('country_reached') else [])
            novo['observations'] = [obs]
            ent[k] = novo
            eventos.append({'event': NEW_AD_OBSERVED, 'meta_ad_library_id': k,
                            'as_of_date': a.get('as_of_date'),
                            'nota': ('primeira vez no NOSSO acervo; ver '
                                     'NEW_AD_BY_START_DATE para novidade na fonte'),
                            'baseline': BASELINE_ONLY if primeira_rodada else None})
            continue

        e = ent[k]
        anterior_status = e.get('active_status')
        anterior_hash = e.get('creative_text_hash')
        e['observations'].append(obs)
        e['last_observed'] = a.get('as_of_date')

        pais = a.get('country_reached')
        if pais and pais not in e.get('countries_reached_observed', []):
            e.setdefault('countries_reached_observed', []).append(pais)
            eventos.append({'event': NEW_COUNTRY_ACTIVITY, 'meta_ad_library_id': k,
                            'country_reached': pais, 'as_of_date': a.get('as_of_date'),
                            'nota': 'pais ALCANCADO, nao pais alvo comprovado'})

        if a.get('creative_text_hash') and anterior_hash and \
                a['creative_text_hash'] != anterior_hash:
            eventos.append({'event': CREATIVE_TEXT_CHANGED, 'meta_ad_library_id': k,
                            'as_of_date': a.get('as_of_date')})
        if a.get('active_status') and anterior_status and \
                a['active_status'] != anterior_status:
            eventos.append({'event': STATUS_CHANGED, 'meta_ad_library_id': k,
                            'de': anterior_status, 'para': a.get('active_status'),
                            'as_of_date': a.get('as_of_date')})
            if a['active_status'] == 'ACTIVE':
                eventos.append({'event': AD_ACTIVE_AGAIN, 'meta_ad_library_id': k,
                                'as_of_date': a.get('as_of_date')})
        elif a.get('active_status') == 'ACTIVE':
            eventos.append({'event': AD_STILL_ACTIVE, 'meta_ad_library_id': k,
                            'as_of_date': a.get('as_of_date')})

        for campo in ('active_status', 'creative_text_hash', 'end_date',
                      'creative_text', 'start_date'):
            if a.get(campo) is not None:
                e[campo] = a[campo]

    # ausentes: so viram "parou" se as duas pontas forem completas
    if not primeira_rodada:
        completude_agora = {a.get('country_reached'): a.get('collection_completeness')
                            for a in (snapshot or [])}
        agora = (snapshot or [{}])[0].get('as_of_date') if snapshot else None
        for k, e in ent.items():
            if k in vistos_agora:
                continue
            pais = (e.get('countries_reached_observed') or [None])[0]
            antes_ok = (e.get('observations') or [{}])[-1].get(
                'collection_completeness') == COMPLETA_OBSERVADA
            agora_ok = completude_agora.get(pais) == COMPLETA_OBSERVADA
            eventos.append({
                'event': AD_STOPPED_OBSERVED if (antes_ok and agora_ok)
                else AD_ABSENT_UNEXPLAINED,
                'meta_ad_library_id': k, 'as_of_date': agora,
                'nota': ('sumiu de uma listagem completa segundo a fonte nas duas pontas'
                         if (antes_ok and agora_ok) else
                         'sumiu, mas a listagem nao estava completa nas duas pontas; '
                         'pode ser limite da coleta, nao fim da veiculacao'),
            })

    return ent, eventos


def novos_por_data_de_inicio(eventos, entidades, data_coleta_anterior):
    """Separa a novidade DO MUNDO da novidade do nosso acervo.

    Sem coleta anterior, devolve BASELINE_ONLY: nao da para dizer que um anuncio
    e novo quando nao havia ontem com que comparar.
    """
    if not data_coleta_anterior:
        return {'estado': BASELINE_ONLY, 'eventos': []}
    saida = []
    for ev in eventos:
        if ev.get('event') != NEW_AD_OBSERVED:
            continue
        e = entidades.get(ev['meta_ad_library_id']) or {}
        inicio = e.get('start_date')
        if inicio and inicio > data_coleta_anterior:
            saida.append({'event': NEW_AD_BY_START_DATE,
                          'meta_ad_library_id': ev['meta_ad_library_id'],
                          'start_date': inicio,
                          'coleta_anterior': data_coleta_anterior})
    return {'estado': 'OK', 'eventos': saida}


def resumo(entidades, eventos, tem_linha_de_base):
    """Contagens. Sao contagens de ANUNCIO, e a palavra investimento nao aparece."""
    ativos = sum(1 for e in entidades.values() if e.get('active_status') == 'ACTIVE')
    por_evento = {}
    for ev in eventos:
        por_evento[ev['event']] = por_evento.get(ev['event'], 0) + 1
    return {
        'ads_total_entities': len(entidades),
        'ads_active_observed': ativos,
        'ads_inactive_observed': len(entidades) - ativos,
        'events': por_evento if tem_linha_de_base else {'estado': BASELINE_ONLY},
        'aviso': 'contagem de anuncios NAO e investimento, share of voice nem '
                 'intensidade de midia',
    }
