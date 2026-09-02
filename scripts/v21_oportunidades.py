#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O MOTOR DE OPORTUNIDADES · descobre convergências defensáveis no V2.1.

    python3 scripts/v21_oportunidades.py

O QUE HAVIA ANTES
-----------------
Nada. `OPPORTUNITIES.json` trazia três fichas escritas à mão, importadas inteiras
do handoff anterior (`LEGACY_CASE_ID: IT-HERO-00x`), e a evidência delas era
prosa — «ver 01-DESIGN-READY/MARKET-PULSE/». Nenhum ID canônico, nenhuma regra,
nenhum portão. As três nasceram antes de existirem 2.030 pares de rótulo, 53
substâncias ativas e 47 fatos regulatórios europeus.

    FICHA ESCRITA À MÃO NÃO É MOTOR: É LEMBRANÇA DE UMA LEITURA.

A LEI QUE GOVERNA ESTE ARQUIVO
------------------------------
Uma oportunidade é LEITURA NOSSA sobre fatos de terceiros. Vale aqui a mesma
regra que já governa os cruzamentos, e ela vale porque vale para o que nós mesmos
produzimos:

    CLIENT_SAFE = false, SEMPRE. RENDERABLE_WITH_METHOD diz o que vai à tela.

Isso não é rebaixamento: é o portão. O que separa CONFIRMADA de DA VALIDAR é
`OPPORTUNITY_STATE` — e uma confirmada exige que TODA a evidência que a sustenta
seja ela própria client-safe, e que os oito portões passem.

    CRUZAMENTO NÃO É OPORTUNIDADE, E OPORTUNIDADE NÃO É PEDIDO.
"""
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V21 = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1')
ING = os.path.join(V21, 'DESIGN-INGEST')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_datas as DT  # noqa: E402

HOJE = date(2026, 9, 2)          # a data de referência do pacote, pinada
JANELA_FUTURA = 365              # dias à frente que ainda contam como "preparar"


def _le(arq):
    p = os.path.join(ING, arq)
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding='utf-8')).get('RECORDS') or []


def _ix(regs, campo):
    d = defaultdict(list)
    for r in regs:
        for v in (r.get(campo) or []):
            d[v].append(r)
    return d


# ── ARQUÉTIPOS ───────────────────────────────────────────────────────────────
# ⚠️ FRASE COM VARIAVEL DENTRO NUNCA FICA TRADUZIDA: e frase nova a cada build,
# e a memoria de traducao chaveia pelo texto. Ja aconteceu duas vezes nesta
# missao. Entao o texto de tela e FIXO por arquetipo, e os numeros vivem em
# campos estruturados ao lado.
#
#     O NUMERO E DADO. A FRASE E TEXTO. MISTURA-LOS PERDE OS DOIS.
TEXTO = {
 'O1_FIELD_PRESSURE': {
   'WHY_NOW': 'um boletim fitossanitario oficial registra este alvo nesta cultura, e '
              'existe rotulo ADAMA que nomeia a combinacao cultura x alvo.',
   'ADAMA': 'ha produtos ADAMA cuja combinacao cultura x alvo esta escrita no rotulo '
            'ministerial, e nao inferida.',
   'PROVA': 'que o alvo foi observado pelo servico fitossanitario e que existe '
            'autorizacao para trata-lo nesta cultura.',
   'NAO_PROVA': 'NAO prova incidencia, area afetada, nem que o produtor va tratar. '
                'Boletim e observacao do servico, nao censo do campo.'},
 'O2_MARKET_MOMENT': {
   'WHY_NOW': 'ha preco corrente ou peso economico medido para esta cultura, e a ADAMA '
              'tem rotulo nela.',
   'ADAMA': 'ha produtos ADAMA com rotulo ministerial nesta cultura.',
   'PROVA': 'que a cultura tem preco publicado ou area medida, e que ha portfolio nela.',
   'NAO_PROVA': 'NAO prova lucro do produtor, demanda nem intencao de compra. '
                'PRECO DE PIAZZA NAO E PRECO NACIONAL.'},
 'O3_RESISTANCE_MOA': {
   'WHY_NOW': 'ha resistencia documentada para este alvo e a ADAMA tem rotulo com modo '
              'de acao declarado na mesma combinacao.',
   'ADAMA': 'os produtos ADAMA desta combinacao tem modo de acao classificado por '
            'HRAC, IRAC ou FRAC.',
   'PROVA': 'que a resistencia foi registrada na literatura e que existem produtos com '
            'modo de acao declarado.',
   'NAO_PROVA': 'NAO prova que a resistencia esteja ocorrendo agora nesta regiao, nem '
                'que o produto ADAMA a resolva. RESISTENCIA DOCUMENTADA NAO E '
                'INCIDENCIA CORRENTE.'},
 'O4_COMPETITIVE_OPENING': {
   'WHY_NOW': 'ha pecas correntes de comunicacao de concorrente sobre esta cultura, e a '
              'ADAMA tem rotulo nela.',
   'ADAMA': 'a ADAMA tem produto autorizado na cultura de que o concorrente fala.',
   'PROVA': 'que houve comunicacao publica de concorrente sobre esta cultura.',
   'NAO_PROVA': 'ANUNCIO ALCANCOU NAO E ANUNCIO MIRAVA, e COMUNICACAO NAO E '
                'PARTICIPACAO DE MERCADO. NAO prova investimento, share nem resultado.'},
 'O5_REGULATORY_PREPARATION': {
   'WHY_NOW': 'a aprovacao europeia desta substancia tem data-limite publicada, e '
              'autorizacoes italianas da ADAMA a contem.',
   'ADAMA': 'produtos ADAMA registrados na Italia contem esta substancia ativa.',
   'PROVA': 'que existe uma data europeia publicada e quais produtos a contem.',
   'NAO_PROVA': 'EXPIRACAO DE APROVACAO NAO E NAO-RENOVACAO, NAO e risco e NAO e '
                'oportunidade. ESTADO EUROPEU NAO E COMERCIALIZABILIDADE ITALIANA.'},
 'O6_SCIENCE_TO_FIELD': {
   'WHY_NOW': 'ha ciencia registrada sobre esta cultura e sinal de campo corrente nela.',
   'ADAMA': 'a ADAMA tem rotulo ministerial nesta cultura.',
   'PROVA': 'que existe literatura sobre o tema e que houve observacao de campo.',
   'NAO_PROVA': 'ARTIGO CIENTIFICO NAO E PRESENCA NO CAMPO. NAO prova incidencia nem '
                'eficacia de produto.'},
}

ARQ = {
    'O1_FIELD_PRESSURE': 'pressao de campo corrente sobre cultura com janela e rotulo ADAMA',
    'O2_MARKET_MOMENT': 'sinal de mercado ou peso economico sobre cultura com portfolio ADAMA',
    'O3_RESISTANCE_MOA': 'resistencia documentada com relevancia de campo ou ciencia e MoA ADAMA',
    'O4_COMPETITIVE_OPENING': 'comunicacao corrente de concorrente sobre cultura onde a ADAMA tem rotulo',
    'O5_REGULATORY_PREPARATION': 'data regulatoria europeia sobre substancia que produtos ADAMA contem',
    'O6_SCIENCE_TO_FIELD': 'ciencia relevante com evidencia corrente de campo e relevancia ADAMA',
}

# Estados de relação com o produto, do mais forte ao mais fraco.
VERIFIED_LABEL_MATCH = 'VERIFIED_LABEL_MATCH'
RELATED_PORTFOLIO = 'RELATED_PORTFOLIO'
LABEL_CHECK_NEEDED = 'LABEL_CHECK_NEEDED'

CONFIRMADA = 'OPPORTUNITY_CONFIRMED'
CANDIDATA = 'OPPORTUNITY_CANDIDATE'
ROTULO = {CONFIRMADA: ('OPPORTUNITÀ CONFERMATA', 'CONFIRMED OPPORTUNITY'),
          CANDIDATA: ('OPPORTUNITÀ DA VALIDARE', 'OPPORTUNITY TO VALIDATE')}


def identidade(arquetipo, crop, alvo, geo, jan):
    """A identidade é determinística: mesma situação, mesma ficha.

        CINCO CARTOES DA MESMA SITUACAO NAO SAO CINCO OPORTUNIDADES.
    """
    chave = '|'.join([arquetipo, crop or 'NO_CROP', alvo or 'NO_TARGET',
                      geo or 'NO_GEO', jan or 'NO_WINDOW'])
    return 'OPP_' + hashlib.sha256(chave.encode()).hexdigest()[:12].upper(), chave


def data_do_sinal(regs):
    """A data do proprio documento e evidencia temporal.

    A janela de APLICACAO e prosa em quase todo o pacote, e nao se inventa uma.
    Mas um boletim fitossanitario publicado tem data, e essa data responde
    «isto e corrente?» — que e a pergunta do portao C. As duas coisas convivem:
    WINDOW_* diz quando se aplica; SIGNAL_DATE diz quando se observou.

        NAO SABER A JANELA DE APLICACAO NAO E NAO SABER SE O SINAL E DE HOJE.
    """
    melhor = None
    for r in regs:
        if r.get('ENTITY_TYPE') not in ('FIELD_SIGNAL', 'MARKET_OBSERVATION',
                                        'COMPETITOR_ACTIVITY', 'EVENT'):
            continue
        d = DT.analisar(('REFERENCE_DATE', r.get('REFERENCE_DATE')),
                        ('PUBLICATION_DATE', r.get('PUBLICATION_DATE')),
                        ('START_DATE', r.get('START_DATE')))
        if d['DATE_PARSE_STATE'] == DT.UNKNOWN:
            continue
        v = d['END_DATE'] or d['START_DATE']
        if v and (melhor is None or v > melhor):
            melhor = v
    if not melhor:
        return None, None
    return melhor, (HOJE - date.fromisoformat(melhor)).days


def janela(regs):
    """→ (inicio, fim, dias, estado). Prosa nunca vira janela."""
    for r in regs:
        for campo in ('APPLICATION_WINDOW_2026', 'NEXT_IMPORTANT_WINDOW',
                      'MONITORING_WINDOW', 'REGULATORY_WINDOW',
                      'PREPARATION_WINDOW'):
            d = DT.analisar((campo, r.get(campo)))
            if d['DATE_PARSE_STATE'] != DT.UNKNOWN:
                fim = date.fromisoformat(d['END_DATE'])
                return (d['START_DATE'], d['END_DATE'], (fim - HOJE).days,
                        d['DATE_PARSE_STATE'])
    return (None, None, None, 'UNKNOWN')


def score(dim):
    """0–2 por dimensão, máximo 12. Ordena; não prova."""
    return sum(min(2, max(0, v)) for v in dim.values())


def estado_temporal(dias, arquetipo, tem_janela):
    if arquetipo == 'O5_REGULATORY_PREPARATION':
        return 'FUTURE_PREPARATION'
    if not tem_janela or dias is None:
        return 'WATCH'
    if 0 <= dias <= 30:
        return 'ACT_NOW'
    if 30 < dias <= 120:
        return 'PREPARE_NOW'
    if dias > 120:
        return 'FUTURE_PREPARATION'
    return 'WATCH'


# ── OS OITO PORTÕES DA CONFIRMAÇÃO ───────────────────────────────────────────
def portoes(o, ev):
    """A–H. Devolve a lista dos que FALHARAM. Score alto não abre portão.

        UM 12 COM PORTAO FECHADO CONTINUA SENDO UM 12 COM PORTAO FECHADO.
    """
    f = []
    geos = {g for e in ev for g in (e.get('REGION_IDS') or [])}
    # A · geografia compatível: nenhum apoio pode falar por região que não é dele
    if any(e.get('REGION_REPRESENTS') is False and o['GEOGRAPHY_SCOPE'] == 'REGIONAL'
           for e in ev):
        f.append('A_GEOGRAFIA · apoio provincial sustentando alegacao regional')
    if len(geos) > 1 and o['GEOGRAPHY'] not in ('GEO_ITALY', 'GEO_EU') and \
            not geos <= {o['GEOGRAPHY']}:
        f.append('A_GEOGRAFIA · apoios em geografias que nao se contem')
    # B · identidade de cultura
    crops = {c for e in ev for c in (e.get('CROP_IDS') or [])}
    if o['CROP'] and crops and o['CROP'] not in crops:
        f.append('B_CULTURA · a cultura do caso nao aparece nos apoios')
    # C · tempo: janela de aplicacao OU sinal datado e recente
    if o['ARCHETYPE'] != 'O5_REGULATORY_PREPARATION' and \
            o['WINDOW_STATE'] == 'UNKNOWN' and \
            (o['SIGNAL_AGE_DAYS'] is None or o['SIGNAL_AGE_DAYS'] > 120):
        f.append('C_TEMPO · sem janela defensavel e sem sinal datado nos ultimos 120 dias')
    # D · problema agronômico evidenciado
    if o['ARCHETYPE'] in ('O1_FIELD_PRESSURE', 'O3_RESISTANCE_MOA', 'O6_SCIENCE_TO_FIELD') \
            and not o['TARGET']:
        f.append('D_PROBLEMA · sem alvo agronomico declarado')
    # E · relação ADAMA evidenciada
    if o['PRODUCT_LINK_STATE'] == LABEL_CHECK_NEEDED:
        f.append('E_ADAMA · rotulo por verificar (LABEL_CHECK_NEEDED)')
    if o['PRODUCT_LINK_STATE'] == RELATED_PORTFOLIO and o['ARCHETYPE'] != 'O5_REGULATORY_PREPARATION':
        f.append('E_ADAMA · so RELATED_PORTFOLIO nao confirma oportunidade comercial')
    # F · procedência resolvível
    sem = [e['ID'] for e in ev if not e.get('SOURCE_URLS')
           and e.get('PROVENANCE_STATE') == 'UNRECOVERABLE']
    if sem:
        f.append('F_PROCEDENCIA · apoio sem origem recuperavel: %s' % ', '.join(sem[:3]))
    # G · contradição
    if o['CROP'] and any(e.get('CROP_IDS') and o['CROP'] not in e['CROP_IDS']
                         and e.get('ENTITY_TYPE') == 'FIELD_SIGNAL' for e in ev):
        f.append('G_CONTRADICAO · sinal de campo de outra cultura no mesmo caso')
    # H · a leitura não pode exceder a evidência
    if any(not e.get('CLIENT_SAFE') for e in ev):
        f.append('H_EXCESSO · apoio que nao passou no portao de QA')
    return f


# ── O RED TEAM ───────────────────────────────────────────────────────────────
def red_team(o, ev):
    """Nove perguntas, cada uma um defeito que este projeto ja cometeu."""
    m = []
    t = {e['ID']: e for e in ev}
    if len(ev) == 1:
        m.append('artefato de fonte unica: um documento nao e convergencia')
    if len({e.get('SOURCE_DOCUMENT_ID') or (e.get('SOURCE_URLS') or [None])[0]
            for e in ev} - {None}) < 2 and len(ev) > 1:
        m.append('todos os apoios saem do MESMO documento')
    if any(e.get('REGION_REPRESENTS') is False for e in ev) and \
            o['GEOGRAPHY_SCOPE'] in ('REGIONAL', 'NACIONAL'):
        m.append('geografia promovida: apoio provincial em alegacao mais ampla')
    if any(e.get('COMMODITY_STAGE') == 'PROCESSED_PRODUCT' for e in ev):
        m.append('preco de produto processado sustentando mercado da cultura')
    if o['ARCHETYPE'] == 'O5_REGULATORY_PREPARATION' and o['STATUS'] == 'ACT_NOW':
        m.append('data regulatoria virou urgencia')
    if any(e.get('ENTITY_TYPE') == 'COMPETITOR_ACTIVITY' for e in ev) and \
            re.search(r'share|participac|quota', json.dumps(o, ensure_ascii=False), re.I):
        m.append('comunicacao de concorrente virou participacao de mercado')
    if o['ARCHETYPE'] == 'O3_RESISTANCE_MOA' and not any(
            e.get('ENTITY_TYPE') == 'FIELD_SIGNAL' for e in ev):
        m.append('resistencia documentada sem sinal de campo corrente: nao e incidencia')
    if o['PRODUCT_LINK_STATE'] != VERIFIED_LABEL_MATCH and \
            o['OPPORTUNITY_STATE'] == CONFIRMADA:
        m.append('relacao de portfolio tratada como verificacao de rotulo')
    if o['ARCHETYPE'] == 'O6_SCIENCE_TO_FIELD' and not any(
            e.get('ENTITY_TYPE') == 'FIELD_SIGNAL' for e in ev):
        m.append('artigo cientifico virou presenca no campo')
    if any(e.get('ENTITY_TYPE') == 'PUBLIC_VOICE' for e in ev) and len(ev) < 3:
        m.append('voz isolada tratada como incidencia')
    return m


def main():
    C = {n: _le(n + '.json') for n in (
        'CURRENT-FIELD-SIGNALS', 'CROP-WINDOWS', 'RESISTANCE', 'SCIENCE',
        'COMPETITOR-ACTIVITIES', 'MARKET-OBSERVATIONS', 'CROP-ECONOMIC-WEIGHT',
        'PRODUCT-RELATIONSHIPS', 'PRODUCTS-COMMERCIAL', 'PRODUCTS-REGULATORY',
        'ACTIVE-INGREDIENTS', 'PRODUCT-ACTIVE-INGREDIENTS',
        'REGULATORY-FUTURE-FACTS', 'PUBLIC-VOICES')}
    cs = {k: [x for x in v if x.get('CLIENT_SAFE')] for k, v in C.items()}

    lbl_crop = _ix(cs['PRODUCT-RELATIONSHIPS'], 'CROP_IDS')
    lbl_issue = _ix(cs['PRODUCT-RELATIONSHIPS'], 'ISSUE_IDS')
    field_crop = _ix(cs['CURRENT-FIELD-SIGNALS'], 'CROP_IDS')
    win_crop = _ix(cs['CROP-WINDOWS'], 'CROP_IDS')
    res_crop = _ix(cs['RESISTANCE'], 'CROP_IDS')
    sci_crop = _ix(cs['SCIENCE'], 'CROP_IDS')
    comp_crop = _ix(cs['COMPETITOR-ACTIVITIES'], 'CROP_IDS')
    mkt_crop = _ix(cs['MARKET-OBSERVATIONS'], 'CROP_IDS')
    econ_crop = _ix(cs['CROP-ECONOMIC-WEIGHT'], 'CROP_IDS')

    reg_por_num = {re.sub(r'\D', '', str(p.get('REGISTRATION_NUMBER') or '')).lstrip('0').zfill(6): p
                   for p in cs['PRODUCTS-REGULATORY']}
    ai_por_prod = defaultdict(list)
    for r in cs['PRODUCT-ACTIVE-INGREDIENTS']:
        k = re.sub(r'\D', '', str(r.get('REGISTRATION_NUMBER') or '')).lstrip('0').zfill(6)
        ai_por_prod[k].append(r)
    ai_por_id = {a['ID']: a for a in cs['ACTIVE-INGREDIENTS']}

    brutos, rejeitados = [], []

    def emitir(arquetipo, crop, alvo, geo, escopo, apoios, link, produtos,
               numeros, dim, acao):
        T = TEXTO[arquetipo]
        porque_agora, relevancia = T['WHY_NOW'], T['ADAMA']
        prova, nao_prova = T['PROVA'], T['NAO_PROVA']
        apoios = [a for a in apoios if a]
        if not apoios:
            return
        ini, fim, dias, jest = janela(win_crop.get(crop, []) + apoios)
        sdata, sidade = data_do_sinal(apoios)
        oid, chave = identidade(arquetipo, crop, alvo, geo,
                                ini or ('EU' if arquetipo == 'O5_REGULATORY_PREPARATION' else None))
        o = {'ID': oid, 'IDENTITY_KEY': chave, 'ARCHETYPE': arquetipo,
             'CROP': crop, 'TARGET': alvo, 'GEOGRAPHY': geo, 'GEOGRAPHY_SCOPE': escopo,
             'WINDOW_START': ini, 'WINDOW_END': fim, 'DAYS_REMAINING': dias,
             'WINDOW_STATE': jest, 'SIGNAL_DATE': sdata, 'SIGNAL_AGE_DAYS': sidade,
             'PRODUCT_LINK_STATE': link,
             'PRODUCT_RELATIONSHIPS': produtos[:12],
             'EVIDENCE_IDS': [a['ID'] for a in apoios],
             'EVIDENCE_FAMILIES': sorted({a.get('ENTITY_TYPE') for a in apoios}),
             'WHY_NOW': porque_agora, 'ADAMA_RELEVANCE': relevancia,
             'NUMBERS': numeros,
             'WHAT_IT_PROVES': prova, 'WHAT_IT_DOES_NOT_PROVE': nao_prova,
             'SCORE_DIMENSIONS': dim, 'OPPORTUNITY_SCORE': score(dim),
             'ACTION_MAP': acao}
        o['STATUS'] = estado_temporal(dias, arquetipo, jest != 'UNKNOWN')
        if o['STATUS'] == 'WATCH' and sidade is not None and sidade <= 30:
            o['STATUS'] = 'ACT_NOW'
        elif o['STATUS'] == 'WATCH' and sidade is not None and sidade <= 120:
            o['STATUS'] = 'PREPARE_NOW'
        falhas = portoes(o, apoios)
        o['OPPORTUNITY_STATE'] = CONFIRMADA if not falhas else CANDIDATA
        o['BLOCKING_GATES'] = falhas
        rt = red_team(o, apoios)
        o['RED_TEAM_FINDINGS'] = rt
        if rt:
            # o red team NAO confirma nada: so derruba
            o['OPPORTUNITY_STATE'] = CANDIDATA
            o['BLOCKING_GATES'] = falhas + ['RED_TEAM · ' + x for x in rt]
        if o['OPPORTUNITY_STATE'] == CANDIDATA:
            o['STATUS'] = 'TO_VALIDATE' if falhas else o['STATUS']
        o['CONFIDENCE'] = ('ALTA' if o['OPPORTUNITY_STATE'] == CONFIRMADA
                           else ('MEDIA' if o['OPPORTUNITY_SCORE'] >= 8 else 'BAIXA'))
        brutos.append((o, apoios))

    # ══ O1 · PRESSÃO DE CAMPO ════════════════════════════════════════════════
    for crop, sinais in sorted(field_crop.items()):
        alvos = {i for s in sinais for i in (s.get('ISSUE_IDS') or [])}
        for alvo in sorted(alvos) or [None]:
            sin = [s for s in sinais if not alvo or alvo in (s.get('ISSUE_IDS') or [])]
            rot = [r for r in lbl_crop.get(crop, [])
                   if not alvo or alvo in (r.get('ISSUE_IDS') or [])]
            if not sin or not rot:
                continue
            geos = {g for s in sin for g in (s.get('REGION_IDS') or [])}
            geo = sorted(geos)[0] if len(geos) == 1 else 'GEO_ITALY'
            esc = sin[0].get('GEOGRAPHIC_SCOPE') if len(geos) == 1 else 'NACIONAL'
            prods = sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')})
            emitir('O1_FIELD_PRESSURE', crop, alvo, geo, esc,
                   sin[:8] + win_crop.get(crop, [])[:3] + rot[:6],
                   VERIFIED_LABEL_MATCH if rot else LABEL_CHECK_NEEDED, prods,
                   {'PRODUTOS_COM_ROTULO': len(prods), 'SINAIS_DE_CAMPO': len(sin)},
                   {'CURRENTNESS': 2 if sin else 0, 'GEOGRAPHY': 2 if len(geos) == 1 else 1,
                    'AGRONOMIC': 2 if alvo else 1, 'ADAMA': 2 if rot else 0,
                    'MULTI_SOURCE': min(2, len({s.get('SOURCE_IDS', [None])[0] for s in sin})),
                    'ACTIONABILITY': 2 if win_crop.get(crop) else 1},
                   ['MARKET_DEVELOPMENT', 'COMMERCIAL', 'SCIENCE_TECHNICAL'])

    # ══ O2 · MOMENTO DE MERCADO ══════════════════════════════════════════════
    for crop in sorted(set(mkt_crop) | set(econ_crop)):
        mk = [m for m in mkt_crop.get(crop, [])
              if m.get('COMMODITY_STAGE') != 'PROCESSED_PRODUCT']
        ec = econ_crop.get(crop, [])
        rot = lbl_crop.get(crop, [])
        if not (mk or ec) or not rot:
            continue
        prods = sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')})
        emitir('O2_MARKET_MOMENT', crop, None, 'GEO_ITALY', 'NACIONAL',
               mk[:6] + ec[:3] + rot[:6],
               VERIFIED_LABEL_MATCH if rot else RELATED_PORTFOLIO, prods,
               {'PRODUTOS_COM_ROTULO': len(prods), 'OBSERVACOES_DE_MERCADO': len(mk),
                'LINHAS_DE_PESO_ECONOMICO': len(ec)},
               {'CURRENTNESS': 2 if mk else 1, 'GEOGRAPHY': 1, 'AGRONOMIC': 1,
                'ADAMA': 2 if rot else 0,
                'MULTI_SOURCE': min(2, (1 if mk else 0) + (1 if ec else 0)),
                'ACTIONABILITY': 1},
               ['MARKET_DEVELOPMENT', 'PORTFOLIO', 'COMMERCIAL'])

    # ══ O3 · RESISTÊNCIA / MoA ═══════════════════════════════════════════════
    for crop, rs in sorted(res_crop.items()):
        alvos = {i for r in rs for i in (r.get('ISSUE_IDS') or [])}
        for alvo in sorted(alvos) or [None]:
            r0 = [r for r in rs if not alvo or alvo in (r.get('ISSUE_IDS') or [])]
            camp = [s for s in field_crop.get(crop, [])
                    if not alvo or alvo in (s.get('ISSUE_IDS') or [])]
            rot = [r for r in lbl_crop.get(crop, [])
                   if not alvo or alvo in (r.get('ISSUE_IDS') or [])]
            regs = {re.sub(r'\D', '', str(r.get('REGISTRATION_NUMBER') or '')).lstrip('0').zfill(6)
                    for r in rot}
            ais = [ai_por_id.get(x['ACTIVE_INGREDIENT_ID']) for g in regs
                   for x in ai_por_prod.get(g, []) if x.get('ACTIVE_INGREDIENT_ID') in ai_por_id]
            ais = [a for a in ais if a]
            if not r0 or not rot:
                continue
            moas = sorted({m for a in ais for m in
                           (a.get('HRAC'), a.get('IRAC'), a.get('FRAC')) if m})
            emitir('O3_RESISTANCE_MOA', crop, alvo, 'GEO_ITALY', 'NACIONAL',
                   r0[:6] + camp[:4] + rot[:6] + ais[:6],
                   VERIFIED_LABEL_MATCH if rot else LABEL_CHECK_NEEDED,
                   sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')}),
                   {'MODOS_DE_ACAO': moas, 'REGISTOS_DE_RESISTENCIA': len(r0),
                    'SINAIS_DE_CAMPO': len(camp)},
                   {'CURRENTNESS': 2 if camp else 0, 'GEOGRAPHY': 1,
                    'AGRONOMIC': 2 if alvo else 1, 'ADAMA': 2 if moas else 1,
                    'MULTI_SOURCE': min(2, (1 if camp else 0) + (1 if ais else 0)),
                    'ACTIONABILITY': 1},
                   ['SCIENCE_TECHNICAL', 'MARKET_DEVELOPMENT', 'PORTFOLIO'])

    # ══ O4 · ABERTURA COMPETITIVA ════════════════════════════════════════════
    for crop, ats in sorted(comp_crop.items()):
        rot = lbl_crop.get(crop, [])
        if not rot or len(ats) < 3:
            continue
        emitir('O4_COMPETITIVE_OPENING', crop, None, 'GEO_ITALY', 'NACIONAL',
               ats[:8] + rot[:6],
               VERIFIED_LABEL_MATCH if rot else RELATED_PORTFOLIO,
               sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')}),
               {'PECAS_DE_CONCORRENTE': len(ats), 'PRODUTOS_COM_ROTULO': len(rot)},
               {'CURRENTNESS': 2, 'GEOGRAPHY': 1, 'AGRONOMIC': 1,
                'ADAMA': 2 if rot else 0, 'MULTI_SOURCE': 2 if len(ats) > 5 else 1,
                'ACTIONABILITY': 1},
               ['MARKETING', 'MARKET_DEVELOPMENT', 'COMMERCIAL'])

    # ══ O5 · PREPARAÇÃO REGULATÓRIA ══════════════════════════════════════════
    for f in sorted(cs['REGULATORY-FUTURE-FACTS'], key=lambda x: x['ID']):
        regs = [r for r in (f.get('ITALIAN_REGISTRATIONS') or [])]
        prods = [reg_por_num.get(re.sub(r'\D', '', str(r)).lstrip('0').zfill(6))
                 for r in regs]
        prods = [p for p in prods if p]
        if not prods:
            continue
        ai = ai_por_id.get(f.get('ACTIVE_INGREDIENT_ID'))
        rot = [r for r in cs['PRODUCT-RELATIONSHIPS']
               if re.sub(r'\D', '', str(r.get('REGISTRATION_NUMBER') or '')).lstrip('0').zfill(6)
               in {re.sub(r'\D', '', str(x)).lstrip('0').zfill(6) for x in regs}]
        crops = sorted({c for r in rot for c in (r.get('CROP_IDS') or [])})
        d = DT.analisar(('EU_EXPIRATION_OF_APPROVAL', f.get('EU_EXPIRATION_OF_APPROVAL')))
        dias = (date.fromisoformat(d['END_DATE']) - HOJE).days if d['END_DATE'] else None
        o_ap = [f] + prods[:6] + ([ai] if ai else []) + rot[:4]
        emitir('O5_REGULATORY_PREPARATION', crops[0] if len(crops) == 1 else None,
               None, 'GEO_EU', 'EUROPEU', o_ap,
               VERIFIED_LABEL_MATCH if rot else RELATED_PORTFOLIO,
               sorted({p.get('NAME') for p in prods if p.get('NAME')}),
               {'SUBSTANCIA': f.get('ACTIVE_INGREDIENT'),
                'DATA_LIMITE_UE': f.get('EU_EXPIRATION_OF_APPROVAL'),
                'PRODUTOS_ADAMA': len(prods), 'CULTURAS_DE_ROTULO': len(crops),
                'DIAS_ATE_A_DATA': dias},
               {'CURRENTNESS': 1, 'GEOGRAPHY': 1, 'AGRONOMIC': 1 if crops else 0,
                'ADAMA': 2 if rot else 1, 'MULTI_SOURCE': 2 if ai else 1,
                'ACTIONABILITY': 2 if dias and dias < 540 else 1},
               ['REGULATORY', 'PORTFOLIO', 'SUPPLY', 'MARKET_DEVELOPMENT'])

    # ══ O6 · CIÊNCIA → CAMPO ═════════════════════════════════════════════════
    for crop, sc in sorted(sci_crop.items()):
        camp = field_crop.get(crop, [])
        rot = lbl_crop.get(crop, [])
        if not camp or not rot or len(sc) < 2:
            continue
        emitir('O6_SCIENCE_TO_FIELD', crop, None, 'GEO_ITALY', 'NACIONAL',
               sc[:6] + camp[:4] + rot[:4],
               VERIFIED_LABEL_MATCH if rot else RELATED_PORTFOLIO,
               sorted({r.get('PRODUCT_NAME') for r in rot if r.get('PRODUCT_NAME')}),
               {'TRABALHOS_CIENTIFICOS': len(sc), 'SINAIS_DE_CAMPO': len(camp),
                'PRODUTOS_COM_ROTULO': len(rot)},
               {'CURRENTNESS': 2 if camp else 0, 'GEOGRAPHY': 1, 'AGRONOMIC': 1,
                'ADAMA': 2 if rot else 0, 'MULTI_SOURCE': 2, 'ACTIONABILITY': 1},
               ['SCIENCE_TECHNICAL', 'MARKET_DEVELOPMENT'])

    return brutos, rejeitados, C, cs


def gravar(brutos, C, cs):
    """Dedup determinístico, tradução dos campos de tela e os cinco artefatos."""
    porid = {}
    colapsados = 0
    for o, ev in brutos:
        if o['ID'] in porid:
            # A MESMA SITUACAO NAO VIRA DOIS CARTOES: o apoio reforca o caso.
            a, aev = porid[o['ID']]
            a['EVIDENCE_IDS'] = sorted(set(a['EVIDENCE_IDS']) | set(o['EVIDENCE_IDS']))
            a['EVIDENCE_FAMILIES'] = sorted(set(a['EVIDENCE_FAMILIES']) |
                                            set(o['EVIDENCE_FAMILIES']))
            a['MERGED_FROM'] = a.get('MERGED_FROM', 0) + 1
            colapsados += 1
            continue
        porid[o['ID']] = (o, ev)

    regs, rejeitados = [], []
    for oid in sorted(porid):
        o, ev = porid[oid]
        it, en = ROTULO[o['OPPORTUNITY_STATE']]
        r = {
            'ID': o['ID'], 'ENTITY_TYPE': 'OPPORTUNITY',
            'PROVENANCE': 'REAL_DERIVED', 'QA_STATUS': 'EVIDENCE_DERIVED',
            # ⚠️ SEMPRE false, e isto NAO e rebaixamento: e o portao.
            # A juncao e leitura nossa, como no cruzamento. O que vai a tela e
            # decidido por RENDERABLE_WITH_METHOD, e o metodo vai junto.
            'CLIENT_SAFE': False,
            'RENDERABLE_WITH_METHOD': o['OPPORTUNITY_STATE'] == CONFIRMADA,
            'WHY_NOT_CLIENT_SAFE':
                'oportunidade e LEITURA NOSSA sobre fatos de terceiros. A regra vale '
                'para o que nos mesmos produzimos, ou nao e regra. Cada apoio citado '
                'em EVIDENCE_IDS passou pelo portao; a juncao nao passa, e por isso '
                'vai a tela com o metodo declarado ao lado.',
            'SOURCE_IDS': sorted({s for e in ev for s in (e.get('SOURCE_IDS') or [])}) or ['SRC_NAO_DECLARADA'],
            'SOURCE_URLS': sorted({u for e in ev for u in (e.get('SOURCE_URLS') or [])})[:12],
            'REFERENCE_DATE': HOJE.isoformat(),
            'CROP_IDS': [o['CROP']] if o['CROP'] else [],
            'ISSUE_IDS': [o['TARGET']] if o['TARGET'] else [],
            'REGION_IDS': [o['GEOGRAPHY']], 'GEOGRAPHIC_SCOPE': o['GEOGRAPHY_SCOPE'],
            'OPPORTUNITY_STATE': o['OPPORTUNITY_STATE'],
            'OPPORTUNITY_LABEL_IT': it, 'OPPORTUNITY_LABEL_EN': en,
            'ARCHETYPE': o['ARCHETYPE'], 'ARCHETYPE_MEANS': ARQ[o['ARCHETYPE']],
            'STATUS': o['STATUS'],
            'STATUS_LAW': 'o estado e INTERPRETACAO SINTONIA derivada de data externa. '
                          'Nunca infere demanda de revenda, sell-in, estoque, pedido nem '
                          'pipeline interno.',
            'CROP': o['CROP'], 'TARGET': o['TARGET'], 'GEOGRAPHY': o['GEOGRAPHY'],
            'WINDOW_START': o['WINDOW_START'], 'WINDOW_END': o['WINDOW_END'],
            'DAYS_REMAINING': o['DAYS_REMAINING'], 'WINDOW_STATE': o['WINDOW_STATE'],
            'SIGNAL_DATE': o['SIGNAL_DATE'], 'SIGNAL_AGE_DAYS': o['SIGNAL_AGE_DAYS'],
            'WINDOW_LAW': 'WINDOW_* e a janela de APLICACAO, lida de campo declarado; '
                          'quando nao ha, fica UNKNOWN e nao se inventa. SIGNAL_DATE e '
                          'a data do documento que sustenta o caso — diz se o sinal e '
                          'corrente, nao quando aplicar.',
            'WHY_NOW': o['WHY_NOW'], 'ADAMA_RELEVANCE': o['ADAMA_RELEVANCE'],
            'NUMBERS': o['NUMBERS'],
            'NUMBERS_LAW': 'os numeros vivem aqui, fora da frase: frase com variavel '
                           'dentro e frase nova a cada build e nunca fica traduzida.',
            'PRODUCT_LINK_STATE': o['PRODUCT_LINK_STATE'],
            'PRODUCT_RELATIONSHIPS': o['PRODUCT_RELATIONSHIPS'],
            'EVIDENCE_IDS': o['EVIDENCE_IDS'],
            'EVIDENCE_FAMILIES': o['EVIDENCE_FAMILIES'],
            'EVIDENCE_COUNT': len(o['EVIDENCE_IDS']),
            'WHAT_IT_PROVES': o['WHAT_IT_PROVES'],
            'WHAT_IT_DOES_NOT_PROVE': o['WHAT_IT_DOES_NOT_PROVE'],
            'CONFIDENCE': o['CONFIDENCE'],
            'OPPORTUNITY_SCORE': o['OPPORTUNITY_SCORE'],
            'SCORE_DIMENSIONS': o['SCORE_DIMENSIONS'],
            'SCORE_LAW': 'o score ORDENA, nao prova. Um 12 com portao fechado continua '
                         'sendo um 12 com portao fechado.',
            'BLOCKING_GATES': o['BLOCKING_GATES'],
            'RED_TEAM_FINDINGS': o['RED_TEAM_FINDINGS'],
            'ACTION_MAP': o['ACTION_MAP'],
            'ACTION_MAP_LAW': 'quem deve olhar isto agora e leitura de inteligencia '
                              'externa, nao prova de que o departamento deva agir.',
            # O motor roda no passo 5e, DEPOIS do carimbo de origem do passo 4:
            # o registro tem de trazer a propria camada, ou nasce sem procedencia.
            # E a camada e DERIVED_V2_1 porque a oportunidade e leitura NOSSA — nao
            # veio de fonte nenhuma, nasceu aqui.
            'ORIGIN_LAYER': 'DERIVED_V2_1',
            'MERGED_FROM': o.get('MERGED_FROM', 0),
            'IDENTITY_KEY': o['IDENTITY_KEY'],
        }
        if o.get('MERGED_FROM'):
            r['DEDUP_NOTE'] = ('%d registros adicionais descreviam a MESMA situacao e '
                               'reforcam este caso em vez de criar cartoes novos.'
                               % o['MERGED_FROM'])
        regs.append(r)

    ev_out = {'LEI': 'toda evidencia citada por ID canonico. Nenhuma juncao por texto.',
              'POR_OPORTUNIDADE': {r['ID']: r['EVIDENCE_IDS'] for r in regs}}
    return regs, ev_out, colapsados


if __name__ == '__main__':
    brutos, _rej, C, cs = main()
    regs, ev_out, colapsados = gravar(brutos, C, cs)
    conf = [r for r in regs if r['OPPORTUNITY_STATE'] == CONFIRMADA]
    cand = [r for r in regs if r['OPPORTUNITY_STATE'] == CANDIDATA]
    rejeitados = [{'ID': r['ID'], 'ARCHETYPE': r['ARCHETYPE'],
                   'POR_QUE': r['RED_TEAM_FINDINGS'] + r['BLOCKING_GATES']}
                  for r in cand if r['RED_TEAM_FINDINGS']]

    hdr = {'COLLECTION': 'OPPORTUNITIES', 'FILE': 'OPPORTUNITIES.json',
           'SCHEMA_VERSION': 'V2.1', 'BUILT_AT': HOJE.isoformat(), 'PRIMARY_KEY': 'ID',
           'SOURCE_OF_TRUTH': 'motor de oportunidades sobre o proprio V2.1',
           'COUNT_TOTAL': len(regs), 'COUNT_CLIENT_SAFE': 0,
           'COUNT_CONFIRMED': len(conf), 'COUNT_CANDIDATE': len(cand),
           'COUNT_RENDERABLE_WITH_METHOD': len(conf),
           'BY_ARCHETYPE': dict(Counter(r['ARCHETYPE'] for r in regs)),
           'BY_STATUS': dict(Counter(r['STATUS'] for r in regs)),
           'DUPLICATES_COLLAPSED': colapsados,
           'BY_ORIGIN': {'DERIVED_V2_1': len(regs)},
           'BY_QA': {'EVIDENCE_DERIVED': len(regs)},
           'LAW': 'CLIENT_SAFE=false em TODAS, e isso nao e rebaixamento: e o portao. '
                  'A juncao e leitura nossa. RENDERABLE_WITH_METHOD separa a confirmada '
                  'da que ainda tem portao fechado. CRUZAMENTO NAO E OPORTUNIDADE, E '
                  'OPORTUNIDADE NAO E PEDIDO.',
           'LOCALIZED_FIELDS': ['WHY_NOW', 'ADAMA_RELEVANCE', 'WHAT_IT_PROVES',
                                'WHAT_IT_DOES_NOT_PROVE'],
           'RECORDS': regs}
    json.dump(hdr, open(os.path.join(ING, 'OPPORTUNITIES.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump(ev_out, open(os.path.join(ING, 'OPPORTUNITY-EVIDENCE.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'ARQUETIPOS': ARQ, 'PORTOES': list('ABCDEFGH'),
               'ESTADOS_DE_PRODUTO': [VERIFIED_LABEL_MATCH, RELATED_PORTFOLIO,
                                      LABEL_CHECK_NEEDED],
               'ESTADOS_TEMPORAIS': ['ACT_NOW', 'PREPARE_NOW', 'WATCH',
                                     'FUTURE_PREPARATION', 'TO_VALIDATE'],
               'SCORE': {'DIMENSOES': ['CURRENTNESS', 'GEOGRAPHY', 'AGRONOMIC',
                                       'ADAMA', 'MULTI_SOURCE', 'ACTIONABILITY'],
                         'MAXIMO': 12,
                         'LEI': 'ordena, nao prova'},
               'LEI_DO_CLIENT_SAFE':
                   'oportunidade e derivacao: CLIENT_SAFE=false sempre.'},
              open(os.path.join(ING, 'OPPORTUNITY-RULES.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    json.dump({'LEI': 'o red team so derruba; nunca confirma.',
               'TOTAL': len(rejeitados), 'REJEICOES': rejeitados},
              open(os.path.join(ING, 'OPPORTUNITY-REJECTIONS.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('== MOTOR DE OPORTUNIDADES ==')
    print('  confirmadas %d · candidatas %d · total %d · colapsadas %d'
          % (len(conf), len(cand), len(regs), colapsados))
    print('  por arquetipo: %s' % dict(Counter(r['ARCHETYPE'] for r in regs)))
    print('  por estado   : %s' % dict(Counter(r['STATUS'] for r in regs)))
    print('  derrubadas pelo red team: %d' % len(rejeitados))
