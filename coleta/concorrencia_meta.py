#!/usr/bin/env python3
"""
A LINHA RECORRENTE DA META — o que o concorrente paga para mostrar na Itália.

    python3 coleta/concorrencia_meta.py --run-id=<RUN_ID> [--pais=IT] [--teto=N]
    python3 coleta/concorrencia_meta.py --comparar ANTERIOR.json ATUAL.json
    python3 coleta/concorrencia_meta.py --adama ENVELOPE.json   # substancia/alvo x referencia ADAMA

AÇÃO (AGENTS.md: quem VAI BUSCAR e GUARDA). A ferramenta é
`ferramentas/meta_biblioteca.py`; a régua que carimba a página é
`regras/meta_identidade.py`; a lista de páginas é
`data/samples/CONCORRENCIA-META/PAGINAS-META-IT-V1.json`.

A captura de 31/08/2026 (ramo `claude/eame-meta-competitor`, a2fad2d0) foi UMA
fotografia feita à mão. Esta linha é a mesma medida, repetível:

    por concorrente ... a lista de páginas com PAGE_ID provado pela Meta
    por rodada ........ UMA visita por página (sem repetir até o número agradar)
    por visita ........ snapshot datado (OBSERVED_AT), RAW preservado
    entre rodadas ..... comparação com o snapshot ANTERIOR, pela regra de 31/08
    saída ............. envelope COL-LAW-505 -> ingresso (RAW) -> Admissão T9

O QUE UMA RODADA AFIRMA, E O QUE NÃO
-------------------------------------
    NOVO NO ACERVO      o library_id nunca tinha sido visto por esta linha.
                        NÃO é «anúncio novo no mundo».
    NOVO COMPARÁVEL     visto agora, ausente antes, num recorte cuja leitura
                        anterior foi PELO MENOS TÃO FUNDA quanto a de agora.
    TERMINADO           ausente agora, presente antes, com as DUAS leituras
                        fechadas pela fonte. Nome longo de propósito:
                        NO_LONGER_OBSERVED != AD_STOPPED — a fonte deixou de o
                        listar; não declarou fim de veiculação.

A regra da profundidade não é desta linha — é a de 31/08, quando 587 «novos»
eram só a leitura nova a ir mais fundo que a antiga:

    LI_MAIS_FUNDO != APARECERAM_MAIS_ANUNCIOS

PROVENIÊNCIA, NA OBSERVAÇÃO E NÃO NO RELATÓRIO
-----------------------------------------------
Cada unidade leva a rota, o navegador, a porta, o estado de login lido na
página (tem de ser NAO_LOGADO — D88: sem login, sem conta paga), o país
ALCANÇADO e `TARGET_LOCATION_STATE = NOT_PROVED`, e o endereço + sha256 do RAW
da página de onde saiu.

    PAIS_ALCANCADO != PAIS_ALVO        CARTAO != ANUNCIO
    AD_COUNT != SPEND                  PAGINA_ENTREGA_NA_IT != PAGINA_ITALIANA

A NUVEM NÃO COLHE
-----------------
A rota exige Chrome com janela e saída pela Itália (VPN). Sem Chrome na porta,
a visita sai `SLICE_FAILED` com o estado nativo do `ferramentas/cdp.py`
(`BROWSER_NOT_REACHED`) — falha NOSSA, nunca «a página não anuncia».

    FERRAMENTA_CAIU != NAO_ENCONTRADO != NAO_EXISTE
"""
import datetime
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import meta_biblioteca as bib  # noqa: E402
import meta_identidade as ident  # noqa: E402
import proveniencia as pv  # noqa: E402
import porta_da_referencia as porta  # noqa: E402 — D116: a referencia ADAMA so pela porta
from leis import retorno_da_coleta as rc  # noqa: E402

EXECUTOR_ID = 'concorrencia-meta'
EXECUTOR_VERSION = '1'
# A regra de leitura de hoje: rolar até a lista parar de crescer 8 vezes.
# Viaja em cada recorte — a próxima mudança de método tem de ficar à vista.
METODO_DE_LEITURA = 'ROLAR-ATE-PARAR-P8-V1'
SOURCE_ID = 'EU-T9-002'
UNIVERSO = 'T9'
FASE = 'meta-anuncios'

LISTA = os.path.join(RAIZ, 'data', 'samples', 'CONCORRENCIA-META',
                     'PAGINAS-META-IT-V1.json')
# Estado da linha na máquina que colhe (data/colheita não entra no Git).
ESTADO = os.path.join(RAIZ, 'data', 'colheita', 'meta')
ENVELOPE = 'data/colheita/meta/ENVELOPE.json'

SLICE_OK = 'SLICE_OK'
SLICE_FAILED = 'SLICE_FAILED'
LOGIN_DETECTADO = 'LOGIN_DETECTED_STOP'

# comparação (estados de recorte e de cartão) — os nomes de 31/08
PRESENT_BOTH = 'PRESENT_BOTH'
NEWLY_OBSERVED = 'NEWLY_OBSERVED'
NO_LONGER_OBSERVED = 'NO_LONGER_OBSERVED_IN_SNAPSHOT_2'
ZERO_TO_ACTIVE = 'ZERO_TO_ACTIVE'
ACTIVE_TO_ZERO = 'ACTIVE_TO_ZERO'
ACTIVE_BOTH = 'ACTIVE_BOTH'
ZERO_BOTH = 'ZERO_BOTH'
BASELINE_ONLY = 'BASELINE_ONLY'
SLICE_NOT_COMPARABLE = 'SLICE_NOT_OBSERVED_ON_BOTH_ENDS'

# o rótulo que cada unidade leva para a Sala
NOVO_COMPARAVEL = 'NEW_IN_COMPARABLE_SLICE'
NOVO_NAO_AFIRMAVEL = 'NEW_NOT_CLAIMABLE_READ_DEPTH'
NOVO_SEM_ANTERIOR = 'FIRST_SEEN_NO_PREVIOUS_SLICE'
LINHA_DE_BASE = 'BASELINE_FIRST_SNAPSHOT'


def agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def _ler(caminho, padrao=None):
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _gravar(caminho, obj):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    corpo = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + '\n'
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(corpo)
    return hashlib.sha256(corpo.encode('utf-8')).hexdigest()


# ── 1. a lista ───────────────────────────────────────────────────────────────
def paginas_da_linha(lista):
    """→ (a visitar, fora). Quem não passa no carimbo fica FORA, com motivo.

    A lista é lida inteira e cada página sai numa das duas colunas — nada some
    em silêncio. Página repetida (mesmo PAGE_ID) é visitada UMA vez: a regra é
    uma visita por página por rodada.
    """
    visitar, fora, vistos = [], [], set()
    for p in (lista or {}).get('PAGINAS', []):
        if not p.get('EM_LINHA', True):
            fora.append(dict(p, MOTIVO=p.get('MOTIVO_FORA_DA_LINHA') or 'FORA_DA_LINHA'))
            continue
        entra, motivo = ident.carimbar(p)
        if not entra:
            fora.append(dict(p, MOTIVO=motivo))
            continue
        if str(p['page_id']) in vistos:
            fora.append(dict(p, MOTIVO='PAGE_ID_REPETIDO_NA_LISTA'))
            continue
        vistos.add(str(p['page_id']))
        visitar.append(p)
    return visitar, fora


# ── 2. uma visita ────────────────────────────────────────────────────────────
def _creative_text(texto):
    """O corpo do criativo: o que vem depois de «Sponsored». None se não há."""
    partes = (texto or '').split('\nSponsored\n', 1)
    if len(partes) < 2:
        return None
    corpo = re.sub(r'\n(Business|Product/service|Agricultural Service|Company|Brand)\n.*$'
                   r'|\n[\d.,]+ people like this\n.*$|\nLike Page\s*$', '',
                   partes[1], flags=re.S)
    return corpo.replace('​', '').strip() or None


def visitar(pagina, pais, *, snapshot_id, estado=ESTADO, ler=None):
    """UMA visita a UMA página num país. → o recorte observado (nunca levanta).

    `ler` é injetável para teste (por omissão, `meta_biblioteca.ler_pagina`).
    O RAW da página — cabeçalho e cartões inteiros, como a página os mostrou —
    é gravado ANTES de qualquer leitura, com o sha256 ao lado.
    """
    ler = ler or bib.ler_pagina
    url = bib.url_da_pagina(pagina['page_id'], pais)
    momento = agora()
    base = {'company': pagina.get('company'), 'page_id': str(pagina['page_id']),
            'page_name': pagina.get('page_name'), 'dataset': pagina.get('dataset'),
            'country_reached': pais, 'observed_at': momento, 'source_url': url,
            'metodo_de_leitura': METODO_DE_LEITURA}
    try:
        lido = ler(url)
    except Exception as e:                                      # noqa: BLE001
        return dict(base, slice_state=SLICE_FAILED, ads=[],
                    error='%s: %s' % (type(e).__name__, str(e)[:200]),
                    failure_state=getattr(e, 'estado', None) or 'NAO SEI',
                    nota='falha da NOSSA ferramenta; nada foi medido sobre a pagina')
    cab = lido.get('cabecalho') or {}
    cartoes = lido.get('cartoes') or []
    raw_rel = os.path.join('RAW', snapshot_id, '%s-%s.json' % (base['page_id'], pais))
    raw_sha = _gravar(os.path.join(estado, raw_rel),
                      {'url_pedida': url, 'observed_at': momento, 'lido': lido})
    base['raw'] = {'path': os.path.relpath(os.path.join(estado, raw_rel), RAIZ)
                   .replace('\\', '/'), 'sha256': raw_sha}
    login = cab.get('logado')
    if login != bib.NAO_LOGADO:
        # D88: sem login. Página que não mostra «Log in» pode estar a ser lida
        # com sessão — e aí a leitura deixou de ser a do público.
        return dict(base, slice_state=LOGIN_DETECTADO, ads=[], login_state=login,
                    nota='a pagina nao mostrou "Log in": leitura possivelmente '
                         'com sessao. Nada desta visita entra na linha (D88).')
    anuncios = bib.anuncios_em(cartoes)
    comp = bib.completude(anuncios, cab.get('resultados_declarados'),
                          sem_resultados=bool(cab.get('sem_resultados')))
    ads = []
    for c in cartoes:
        texto = c.get('texto') or ''
        inicio, fim = bib.datas_do_texto(texto)
        criativo = _creative_text(texto)
        ads.append({'library_id': c['library_id'],
                    'ads_neste_cartao': c.get('ads_neste_cartao') or 1,
                    'observed_state': bib.status_do_texto(texto),
                    'start_date': inicio, 'end_date': fim,
                    'creative_text': criativo,
                    'creative_text_hash': (hashlib.sha256(criativo.encode('utf-8'))
                                           .hexdigest()[:16] if criativo else None),
                    'eu_transparency_block_present': 'EU transparency' in texto})
    return dict(base, slice_state=SLICE_OK, login_state=login,
                url_final=lido.get('url_final'),
                source_declared_result_count=cab.get('resultados_declarados'),
                cards=len(cartoes), ads_represented=anuncios,
                completeness=comp['state'], completeness_detail=comp,
                scrolls=lido.get('rolagens'),
                stopped_without_growth=lido.get('parou_sem_crescer'), ads=ads)


def rodada(lista, pais='IT', *, teto=None, estado=ESTADO, ler=None):
    """Uma rodada: cada página da linha, UMA vez. → o snapshot."""
    visitar_, fora = paginas_da_linha(lista)
    if teto:
        visitar_ = visitar_[:int(teto)]
    inicio = agora()
    # Microssegundos, e não segundos: duas rodadas no mesmo segundo davam o
    # MESMO id e a segunda apagava a primeira (medido no teste
    # `test_rodada_que_caiu_nao_vira_linha_de_base`). O nome ordena no tempo.
    snapshot_id = 'META-%s-%s' % (pais, datetime.datetime.now(
        datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
    recortes = []
    for p in visitar_:
        r = visitar(p, pais, snapshot_id=snapshot_id, estado=estado, ler=ler)
        recortes.append(r)
        print('  %-42s %s  %3s cartoes  %s' % (
            (p.get('page_name') or '')[:42], pais, r.get('cards', '-'),
            r.get('completeness') or r.get('slice_state')), flush=True)
        if r['slice_state'] == LOGIN_DETECTADO:
            break                                  # D88: para a rodada inteira
    return {'DATASET': 'CONCORRENCIA-META-SNAPSHOT', 'SNAPSHOT_ID': snapshot_id,
            'PAIS': pais, 'SOURCE_ID': SOURCE_ID, 'ROTA': bib.ROTA,
            'PORTA': bib.PORTA, 'EXECUTOR_ID': EXECUTOR_ID,
            'EXECUTOR_VERSION': EXECUTOR_VERSION,
            'METODO_DE_LEITURA': METODO_DE_LEITURA,
            'OBSERVED_AT_INICIO': inicio, 'OBSERVED_AT_FIM': agora(),
            'OBSERVED_AT_NOTA': ('a rodada e uma JANELA; cada recorte guarda o seu '
                                 'observed_at. JANELA_DE_COLETA != INSTANTE.'),
            'PAGINAS_FORA_DA_LINHA': [{'page_id': f.get('page_id'),
                                       'page_name': f.get('page_name'),
                                       'MOTIVO': f['MOTIVO']} for f in fora],
            'RECORTES': recortes}


# ── 3. comparar com o snapshot anterior ──────────────────────────────────────
def comparar_recorte(ids_antes, ids_depois, ambas_fechadas):
    """A regra de UM recorte (a de 31/08). Ausência só se afirma com as duas
    leituras fechadas pela fonte; senão vai para `absent_but_not_claimable`."""
    antes, depois = set(ids_antes or []), set(ids_depois or [])
    sumidos = sorted(antes - depois)
    if antes and depois:
        transicao = ACTIVE_BOTH
    elif depois:
        transicao = ZERO_TO_ACTIVE
    elif antes:
        transicao = ACTIVE_TO_ZERO
    else:
        transicao = ZERO_BOTH
    return {'present_both': sorted(antes & depois),
            'newly_observed': sorted(depois - antes),
            'no_longer_observed': sumidos if ambas_fechadas else [],
            'absent_but_not_claimable': [] if ambas_fechadas else sumidos,
            'slice_transition': transicao}


def _chave(r):
    return (str(r.get('page_id')), r.get('country_reached'))


def comparar(anterior, atual):
    """→ a comparação por recorte, e os totais SÓ onde a regra deixa afirmar.

    Sem snapshot anterior: `BASELINE_ONLY` — nunca «nada mudou».
        SEM_LINHA_DE_BASE != SEM_MUDANCA
    """
    base = {'DATASET': 'CONCORRENCIA-META-COMPARACAO',
            'SNAPSHOT_ANTERIOR': (anterior or {}).get('SNAPSHOT_ID'),
            'SNAPSHOT_ATUAL': (atual or {}).get('SNAPSHOT_ID'),
            'unidades': {'present_both / newly_observed / no_longer_observed':
                         'CARTAO (grupo de criativo), por library_id',
                         'slice_transition': 'RECORTE (page_id x pais alcancado)'},
            'no_longer_observed_nota': 'NO_LONGER_OBSERVED_IN_SNAPSHOT_2 != AD_STOPPED'}
    if not anterior:
        return dict(base, change_observed=BASELINE_ONLY, RECORTES=[],
                    nota='primeiro snapshot: nao ha com que comparar. Isto NAO '
                         'significa que nada mudou.')
    antes = {_chave(r): r for r in anterior.get('RECORTES', [])}
    linhas, nao_comparaveis = [], []
    comparaveis = {PRESENT_BOTH: 0, NEWLY_OBSERVED: 0, NO_LONGER_OBSERVED: 0,
                   'slices': 0}
    confundidos = {'slices': 0, 'cards_gained_by_deeper_reading': 0}
    transicoes = {ZERO_TO_ACTIVE: 0, ACTIVE_TO_ZERO: 0, ACTIVE_BOTH: 0, ZERO_BOTH: 0}
    for r in atual.get('RECORTES', []):
        a = antes.get(_chave(r))
        if not a or a.get('slice_state') != SLICE_OK or r.get('slice_state') != SLICE_OK:
            nao_comparaveis.append({'page_id': r.get('page_id'),
                                    'page_name': r.get('page_name'),
                                    'country_reached': r.get('country_reached'),
                                    'motivo': SLICE_NOT_COMPARABLE})
            continue
        fechadas = (a.get('completeness') in bib.ESTADOS_FECHADOS_PELA_FONTE
                    and r.get('completeness') in bib.ESTADOS_FECHADOS_PELA_FONTE)
        c = comparar_recorte([x['library_id'] for x in a.get('ads', [])],
                             [x['library_id'] for x in r.get('ads', [])], fechadas)
        # A REGRA DE 31/08: o recorte só entra na conta de mudança se a leitura
        # ANTERIOR foi pelo menos tão funda quanto a de agora.
        funda = (a.get('cards') or 0) >= (r.get('cards') or 0)
        transicoes[c['slice_transition']] += 1
        if funda:
            comparaveis[PRESENT_BOTH] += len(c['present_both'])
            comparaveis[NEWLY_OBSERVED] += len(c['newly_observed'])
            comparaveis[NO_LONGER_OBSERVED] += len(c['no_longer_observed'])
            comparaveis['slices'] += 1
        else:
            confundidos['slices'] += 1
            confundidos['cards_gained_by_deeper_reading'] += (
                (r.get('cards') or 0) - (a.get('cards') or 0))
        linhas.append(dict(c, page_id=r.get('page_id'), page_name=r.get('page_name'),
                           company=r.get('company'),
                           country_reached=r.get('country_reached'),
                           both_ends_complete=fechadas, read_depth_comparable=funda,
                           cards_antes=a.get('cards'), cards_agora=r.get('cards'),
                           metodo_antes=a.get('metodo_de_leitura'),
                           metodo_agora=r.get('metodo_de_leitura')))
    mudou = (comparaveis[NEWLY_OBSERVED] or comparaveis[NO_LONGER_OBSERVED]
             or transicoes[ZERO_TO_ACTIVE] or transicoes[ACTIVE_TO_ZERO])
    return dict(base, RECORTES=linhas, slices_not_comparable=nao_comparaveis,
                totals_unit_card_read_depth_comparable=comparaveis,
                read_depth_confounded=dict(
                    confundidos, motivo='onde a leitura de agora foi mais funda, '
                                        '"novo" mede metodo, nao mercado'),
                slice_transitions_unit_slice=transicoes,
                change_observed='YES' if mudou else 'NO',
                change_observed_nota=('NO = a comparacao foi VALIDA e nada mudou. '
                                      'Nao e "nao conseguimos medir".'),
                full_lifecycle_state_capability='NOT_PROVED')


# ── 4. a saída para a Sala: envelope COL-LAW-505 ─────────────────────────────
def _vistos_antes(estado=ESTADO, excluir=None):
    """Todos os library_id que esta linha já viu, em QUALQUER snapshot anterior."""
    vistos = set()
    for f in sorted(glob.glob(os.path.join(estado, 'SNAPSHOTS', '*.json'))):
        s = _ler(f, {})
        if s.get('SNAPSHOT_ID') == excluir:
            continue
        for r in s.get('RECORTES', []):
            vistos.update(str(x['library_id']) for x in r.get('ads', []))
    return vistos


def rotulo_de_novidade(comparacao, recorte, library_id):
    if comparacao.get('change_observed') == BASELINE_ONLY:
        return LINHA_DE_BASE
    for l in comparacao.get('RECORTES', []):
        if (str(l['page_id']), l['country_reached']) == _chave(recorte):
            if library_id in l['newly_observed']:
                return (NOVO_COMPARAVEL if l['read_depth_comparable']
                        else NOVO_NAO_AFIRMAVEL)
    return NOVO_SEM_ANTERIOR


def unidade(recorte, ad, *, run_id, snapshot, comparacao, navegador=None):
    """UM cartão visto pela primeira vez por esta linha -> unidade de COLHEITA."""
    url_ad = bib.url_biblioteca(id=ad['library_id'])
    obs = {
        'META_AD_LIBRARY_ID': ad['library_id'],
        'ADS_IN_THIS_CREATIVE_GROUP': ad.get('ads_neste_cartao') or 1,
        'COMPANY': recorte.get('company'), 'DATASET': recorte.get('dataset'),
        'PAGE_ID': recorte.get('page_id'), 'PAGE_NAME': recorte.get('page_name'),
        'COUNTRY_REACHED': recorte.get('country_reached'),
        'COUNTRY_PARAM_SEMANTICS': 'AD_REACHED_COUNTRY (is_targeted_country=false)',
        'TARGET_LOCATION_STATE': 'NOT_PROVED',
        'PAGE_COUNTRY_SCOPE': 'NOT_PROVED_BY_THIS_LINE',
        'ACTIVE_STATUS': ad.get('observed_state'),
        'START_DATE': ad.get('start_date'), 'END_DATE': ad.get('end_date'),
        'CREATIVE_TEXT': ad.get('creative_text'),
        'CREATIVE_TEXT_HASH': ad.get('creative_text_hash'),
        'SPEND': None, 'SPEND_NOTA': 'AD_COUNT != SPEND; a fonte nao publica gasto '
                                     'de anuncio comercial',
        'NOVIDADE': rotulo_de_novidade(comparacao, recorte, ad['library_id']),
        'SNAPSHOT_ID': snapshot.get('SNAPSHOT_ID'),
        'SLICE_COMPLETENESS': recorte.get('completeness'),
        'META_ROUTE': bib.ROTA, 'BROWSER_PORT': bib.PORTA, 'BROWSER': navegador,
        'LOGIN_STATE': recorte.get('login_state'),
        'READ_METHOD': recorte.get('metodo_de_leitura'),
        'RAW_PAGINA': recorte.get('raw'),
        'SOURCE_PAGE_URL': recorte.get('source_url'),
    }
    u = {'ESPECIE': rc.COLHEITA, 'RUN_ID': run_id, 'SOURCE_ID': SOURCE_ID,
         # EU-T9-002 não tem contrato de fonte com regra de DOCUMENT_ID. O id
         # nativo viaja inteiro em META_AD_LIBRARY_ID; aqui NAO SEI declarado.
         'DOCUMENT_ID': rc.NAO_SEI,
         'DOCUMENT_ID_BASE': 'SEM_CONTRATO_DE_FONTE: o id nativo viaja em '
                             'OBSERVACAO.META_AD_LIBRARY_ID',
         'id': 'META_AD_LIBRARY:%s' % ad['library_id'],
         'SOURCE_URL': url_ad, 'COUNTRY_SCOPE': recorte.get('country_reached'),
         # OBSERVED_AT = o instante em que ESTA linha viu o cartão (e COLLECTED_AT
         # o mesmo): a Biblioteca não carimba observação própria.
         'OBSERVED_AT': recorte.get('observed_at'),
         'COLLECTED_AT': recorte.get('observed_at'),
         'EXECUTOR_ID': EXECUTOR_ID, 'EXECUTOR_VERSION': EXECUTOR_VERSION,
         # Sem CONTENT_TYPE: a observação É o item (JSON), e é o ingresso que o
         # escreve. Declará-lo aqui sem ficheiro colide com o dele (medido:
         # `Artefato() got multiple values for keyword argument 'CONTENT_TYPE'`).
         'OBSERVACAO': obs,
         'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA}}
    if ad.get('start_date'):
        # início de veiculação declarado pela fonte. PUBLICACAO != FACT_TIME.
        u['PUBLISHED_AT'] = ad['start_date']
        u['PUBLISHED_AT_BASIS'] = ('META_AD_LIBRARY "Started running on" no cartao: '
                                   'inicio de veiculacao declarado pela fonte, dia')
    if ad.get('creative_text'):
        u[pv.CAMPO_DAS_UNIDADES] = [pv.unidade_de_texto(
            texto=ad['creative_text'], kind=pv.AUTHOR_TEXT,
            kind_basis=pv.DECLARED_BY_ROUTE, relation=pv.TEXTO_DESCONHECIDO,
            unit_id='TU-1', source_artifact=url_ad,
            derivation_method=pv.RASPADO_DA_PAGINA,
            tool='ferramentas/meta_biblioteca.py')]
    return u


def envelope(snapshot, comparacao, *, run_id, vistos_antes, navegador=None):
    colheita, erros = [], []
    vistos = set(str(x) for x in (vistos_antes or ()))
    for r in snapshot.get('RECORTES', []):
        if r.get('slice_state') != SLICE_OK:
            erros.append({'page_id': r.get('page_id'), 'page_name': r.get('page_name'),
                          'estado': r.get('slice_state'),
                          'failure_state': r.get('failure_state'),
                          'erro': r.get('error') or r.get('nota')})
            continue
        for ad in r.get('ads', []):
            if str(ad['library_id']) in vistos:
                continue      # já foi à Sala (rodada anterior ou outro recorte)
            vistos.add(str(ad['library_id']))
            colheita.append(unidade(r, ad, run_id=run_id, snapshot=snapshot,
                                    comparacao=comparacao, navegador=navegador))
    ok = [r for r in snapshot.get('RECORTES', []) if r.get('slice_state') == SLICE_OK]
    estado = (rc.SUCCESS if ok and not erros else rc.PARTIAL if ok else rc.FAILED)
    env = {'RUN_ID': run_id, 'EXECUTOR_ID': EXECUTOR_ID,
           'EXECUTOR_VERSION': EXECUTOR_VERSION, 'ESTADO': estado,
           'COLHEITA': colheita, 'ERROS': erros,
           'SUPORTE': [{'ESPECIE': rc.RUN_RECEIPT,
                        'ONDE': snapshot.get('_CAMINHO', ''),
                        'O_QUE_E': 'o snapshot da rodada e a comparacao com o '
                                   'anterior: prova da execucao e da mudanca, '
                                   'nao material observado',
                        'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA}}],
           'FASE': FASE, 'UNIVERSO_SUGERIDO': UNIVERSO,
           'SNAPSHOT_ID': snapshot.get('SNAPSHOT_ID'),
           'CHANGE_OBSERVED': comparacao.get('change_observed')}
    if not colheita:
        env['PORQUE_ZERO_COLHEITA'] = ('nenhum cartao novo para esta linha nesta '
                                       'rodada. ZERO LEGITIMO NAO E FALHA.'
                                       if ok else 'nenhuma visita correu bem')
    return env


def anterior_por_recorte(estado=ESTADO, pais='IT'):
    """→ o «snapshot anterior»: para cada recorte, a última leitura SLICE_OK.

    Uma rodada que caiu inteira (Chrome fechado, VPN em baixo) não pode virar a
    linha de base da seguinte — senão a rodada boa depois dela sairia toda
    «não comparável», e uma queda da NOSSA ferramenta apagaria a memória da
    linha. Cada recorte leva o `snapshot_id` de onde veio.
    """
    fs = sorted(glob.glob(os.path.join(estado, 'SNAPSHOTS', 'META-%s-*.json' % pais)))
    ultimo = {}
    for f in fs:
        s = _ler(f, {})
        for r in s.get('RECORTES', []):
            if r.get('slice_state') == SLICE_OK:
                ultimo[_chave(r)] = dict(r, snapshot_id=s.get('SNAPSHOT_ID'))
    if not ultimo:
        return None
    origens = sorted({r['snapshot_id'] for r in ultimo.values()})
    return {'SNAPSHOT_ID': ' + '.join(origens), 'RECORTES': list(ultimo.values())}


def correr(run_id, *, pais='IT', teto=None, lista=None, estado=ESTADO, ler=None,
           raiz=RAIZ):
    """A rodada inteira: lista -> visitas -> snapshot -> comparação -> envelope."""
    anterior = anterior_por_recorte(estado, pais)
    vistos = _vistos_antes(estado)
    snap = rodada(lista if lista is not None else _ler(LISTA, {}), pais, teto=teto,
                  estado=estado, ler=ler)
    caminho = os.path.join(estado, 'SNAPSHOTS', snap['SNAPSHOT_ID'] + '.json')
    snap['_CAMINHO'] = os.path.relpath(caminho, raiz).replace('\\', '/')
    snap['SNAPSHOT_ANTERIOR'] = (anterior or {}).get('SNAPSHOT_ID')
    comp = comparar(anterior, snap)
    _gravar(caminho, snap)
    _gravar(os.path.join(estado, 'COMPARACOES', snap['SNAPSHOT_ID'] + '.json'), comp)
    env = envelope(snap, comp, run_id=run_id, vistos_antes=vistos)
    destino = os.path.join(raiz, rc.endereco_do_envelope(ENVELOPE, run_id))
    _gravar(destino, env)
    return env, comp, destino


# ── 6. o anúncio do concorrente contra a referência ADAMA (PORTA-UNICA-REFERENCIA) ──
def _formas(nome):
    return porta.dobrar(nome).replace('_', ' ').lower()


def _no_texto(forma, texto):
    return re.search(r'(?<![a-z0-9])%s(?![a-z0-9])' % re.escape(forma), texto) is not None


def adama_no_anuncio(colheita, referencia=None, hoje=None):
    """Cada cartão colhido -> substância/alvo que o criativo NOMEIA -> há registo ADAMA com o mesmo?

    SÓ a partir da referência, pela porta (a mesma edição das outras capacidades), e SÓ pelo
    vocabulário dela: substância = nome de `ACTIVE-INGREDIENTS`; alvo = `TARGET_ON_LABEL` das
    bulas lidas. O concorrente compara-se por SUBSTÂNCIA — o cadastro não dá cultura, e a
    cultura do anúncio não se afirma. Nome que a referência não escreve não é detetado (NÃO SEI,
    não «não tem»). Isto LÊ o que já foi colhido: não colhe, não escreve no envelope.
    """
    ref = referencia if referencia is not None else porta.abrir(hoje=hoje)
    if not porta.lida(ref):
        return {'REFERENCIA_ADAMA': porta.carimbo(ref), 'ESTADO': porta.NAO_SEI, 'ANUNCIOS': []}
    subs = {_formas(n): n for n in porta.ativos_conhecidos(ref)}
    alvos = {_formas(n): n for n in porta.alvos_conhecidos(ref)}
    out = []
    for u in colheita or []:
        obs = u.get('OBSERVACAO') or {}
        texto = _formas(obs.get('CREATIVE_TEXT') or '')
        achou_s = sorted({n for f, n in subs.items() if len(f) >= 4 and _no_texto(f, texto)})
        achou_a = sorted({n for f, n in alvos.items() if len(f) >= 4 and _no_texto(f, texto)})
        linha = {'META_AD_LIBRARY_ID': obs.get('META_AD_LIBRARY_ID'), 'COMPANY': obs.get('COMPANY'),
                 'SUBSTANCIAS_NO_CRIATIVO': [], 'ALVOS_NO_CRIATIVO': [],
                 'CULTURA_DO_ANUNCIO': porta.NAO_SEI}
        for n in achou_s:
            r = porta.por_substancia(ref, n)
            r.pop('CARIMBO', None)
            linha['SUBSTANCIAS_NO_CRIATIVO'].append({'SUBSTANCIA': n, 'ADAMA': r})
        for n in achou_a:
            r = porta.por_alvo(ref, n)
            r.pop('CARIMBO', None)
            linha['ALVOS_NO_CRIATIVO'].append({'ALVO': n, 'ADAMA': r})
        # LIGACAO-ADAMA (D123): pela porta, por substancia (o cadastro nao da cultura do anuncio).
        # A substancia vem do CRIATIVO lido por este ficheiro (vocabulario da referencia): divida
        # declarada — nao e chave da Collection.
        linha['LIGACAO_ADAMA'] = porta.ligacao_adama(ref, {
            'SUBSTANCIA': achou_s,
            'VEM_DE': {'SUBSTANCIA': 'CRIATIVO.CREATIVE_TEXT (adama_no_anuncio, vocabulario da referencia)'}})
        if not (achou_s or achou_a):
            linha['PORQUE'] = ('o criativo nao nomeia substancia nem alvo no vocabulario da referencia: '
                               'NAO SEI, nunca «a ADAMA nao tem»')
        out.append(linha)
    return {'REFERENCIA_ADAMA': porta.carimbo(ref), 'ESTADO': 'LIDA', 'ANUNCIOS': out,
            'GRAO': 'SUBSTANCIA (e alvo, em qualquer cultura) — a cultura do anuncio NAO SEI'}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ['--adama']:
        env = _ler(argv[1], {})
        print(json.dumps(adama_no_anuncio(env.get('COLHEITA', [])), ensure_ascii=False, indent=1))
        return 0
    if argv[:1] == ['--comparar']:
        print(json.dumps(comparar(_ler(argv[1]), _ler(argv[2])),
                         ensure_ascii=False, indent=1))
        return 0
    nomeados = dict(a[2:].split('=', 1) for a in argv if a.startswith('--') and '=' in a)
    run_id = nomeados.get('run-id')
    if not run_id:
        print('uso: concorrencia_meta.py --run-id=<RUN_ID> [--pais=IT] [--teto=N]')
        return 2
    env, comp, destino = correr(run_id, pais=(nomeados.get('pais') or 'IT').upper(),
                                teto=nomeados.get('teto'))
    print(json.dumps({'ENVELOPE': os.path.relpath(destino, RAIZ), 'ESTADO': env['ESTADO'],
                      'COLHEITA': len(env['COLHEITA']), 'ERROS': len(env['ERROS']),
                      'CHANGE_OBSERVED': comp.get('change_observed')},
                     ensure_ascii=False, indent=1))
    return 0 if env['ESTADO'] != rc.FAILED else 1


if __name__ == '__main__':
    sys.exit(main())
