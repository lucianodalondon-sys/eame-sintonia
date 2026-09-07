#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A DATA QUE PROVA O «ATTIVO» — e os 36 anúncios que não são italianos.

    python3 scripts/v21_anuncios_prova.py

O DEFEITO
----------
27 registros de `COMPETITOR-ACTIVITIES.json` declaram `ACTIVE_STATUS: ACTIVE`, e
o portal imprime o selo ATTIVO. Nenhum deles carrega a data em que alguém
verificou isso. `START_DATE` é quando o anúncio COMEÇOU — não diz nada sobre
hoje. `END_DATE` vem como a string `"None"` em 28 registros.

    UM SELO DE PRESENTE SEM DATA DE OBSERVAÇÃO AFIRMA O AGORA
    COM A PROVA DE UM DIA QUALQUER.

O acervo tem a prova: `META-ADS-ENTITIES-EAME-V1.json` traz `first_observed` e
`last_observed` em 1340 entidades, mais o histórico `observations[]` com
`as_of_date` por leitura. Medido: **414 de 414** registros PAID do pacote casam
com esse acervo pela chave `meta_ad_library_id`, extraída de `AD_URL`. Perda de
junção: **zero**.

O QUE ESTE PASSO NÃO FAZ
-------------------------
Não muda a regra para aumentar `ACTIVE_PROVED`. A regra continua a mesma —
histórico nunca vira ativo. O que muda é que a evidência atravessa, e aí o
número que já era verdadeiro passa a ser **demonstrável**.

E TEM UM ACHADO QUE NÃO ESTAVA NA CONTA
----------------------------------------
36 dos 414 anúncios que o pacote italiano carrega têm `country_reached: ES` no
acervo. Não são italianos. O campo `COUNTRY_REACHED` do pacote diz `IT` nos 414
— porque foi escrito pelo lote, não lido do anúncio. Aqui entra
`COUNTRY_REACHED_OBSERVED`, que é o que a fonte observou, ao lado do antigo.

    O PAÍS DO ANÚNCIO NÃO SE DEDUZ DA PASTA ONDE ELE FOI GUARDADO.
"""
import ast
import json
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_fonte import carimbo, ler, manifesto  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
ADID = re.compile(r'[?&]id=(\d+)')


def py(v):
    """O acervo grava listas e dicts com `str()`. Aqui voltam a ser objetos.

    Se não voltar, devolve o texto cru — nunca `None` mudo, que apagaria o dado.
    """
    if not isinstance(v, str):
        return v
    s = v.strip()
    if not s or s == 'None':
        return None
    if s[0] in '[{':
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError):
            return v
    return v


def val(v):
    s = str(v).strip() if v is not None else ''
    return None if s in ('', 'None', 'NÃO SEI', 'NAO SEI', 'UNKNOWN') else s


def main():
    if not os.path.isdir(ING):
        raise SystemExit('o pacote nao esta montado: rode antes scripts/v21_ingest.py')
    fontes = {s['KEY']: s for s in manifesto()['SOURCES']}
    chave = [k for k, s in fontes.items()
             if s['FAMILY'] == 'ADS' and s['ROLE'] == 'ENTITIES'][0]
    acv = ler(chave, fontes)
    car = carimbo(chave, fontes)
    ent = acv['entities']
    as_of = acv.get('as_of_date')

    # ── A SEGUNDA LEITURA ────────────────────────────────────────────────────
    # ⚠️ Sem ela, FIRST_OBSERVED == LAST_OBSERVED em 414/414: um ponto, e a
    # pergunta «mudou?» sem resposta. Ela existia no MESMO commit ja pinado.
    #
    #     UMA LEITURA E UM PONTO. DUAS SAO UMA LINHA — CURTA, MAS UMA LINHA.
    k2 = [k for k, f in fontes.items()
          if f['FAMILY'] == 'ADS' and f['ROLE'] == 'OBSERVATIONS_S2']
    s2, car2 = ({}, None)
    if k2:
        d2 = ler(k2[0], fontes)
        car2 = carimbo(k2[0], fontes)
        for o in d2.get('observations') or []:
            for a in (o.get('ads') or []):
                s2.setdefault(str(a.get('library_id')), []).append({
                    'as_of_date': o.get('observed_at'),
                    'active_status': a.get('observed_state'),
                    'country_reached': o.get('ad_delivery_country'),
                    'collection_completeness': o.get('completeness'),
                    'snapshot': 'S2',
                })
    kc = [k for k, f in fontes.items()
          if f['FAMILY'] == 'ADS' and f['ROLE'] == 'TEMPORAL_COMPARISON']
    cmp_ = ler(kc[0], fontes) if kc else {}

    p = os.path.join(ING, 'COMPETITOR-ACTIVITIES.json')
    d = json.load(open(p, encoding='utf-8'))

    casou = falhou = 0
    provado = desconhecido = historico = 0
    pais_divergente = 0
    for r in d['RECORDS']:
        if r.get('ACTIVITY_TYPE') != 'PAID':
            continue
        m = ADID.search(str(r.get('AD_URL') or ''))
        e = ent.get(m.group(1)) if m else None
        if not e:
            falhou += 1
            r['TEMPORAL_PROOF_STATE'] = 'NAO_CASOU_COM_ACERVO'
            r['TEMPORAL_PROOF_WHY'] = (
                'AD_URL nao traz id da Ad Library, ou o id nao esta no acervo pinado')
            r['ACTIVE_PROOF'] = 'ACTIVE_UNKNOWN'
            desconhecido += 1
            continue
        casou += 1
        r['META_AD_LIBRARY_ID'] = m.group(1)
        r['FIRST_OBSERVED'] = val(e.get('first_observed'))
        r['LAST_OBSERVED'] = val(e.get('last_observed'))
        r['COLLECTED_AT'] = as_of
        r['AS_OF_DATE'] = as_of
        r['OBSERVATION_SOURCE'] = 'META_ADS_LIBRARY'
        r['OBSERVATION_SOURCE_ID'] = m.group(1)
        obs = py(e.get('observations')) or []
        obs = obs if isinstance(obs, list) else []
        for o in obs:
            if isinstance(o, dict):
                o.setdefault('snapshot', 'S1')
        obs = obs + s2.get(m.group(1), [])
        # ordem determinística: pela data da observação, depois pelo snapshot
        obs.sort(key=lambda o: (str(o.get('as_of_date') or ''),
                                str(o.get('snapshot') or '')))
        r['OBSERVATIONS'] = obs
        r['OBSERVATION_COUNT'] = len(obs)
        r['OBSERVATION_SNAPSHOTS'] = sorted({str(o.get('snapshot')) for o in obs})
        datas = sorted({str(o.get('as_of_date')) for o in obs if o.get('as_of_date')})
        if datas:
            r['OBSERVATION_WINDOW_FROM'] = datas[0]
            r['OBSERVATION_WINDOW_TO'] = datas[-1]
        # o estado observado passa a ser o da leitura MAIS RECENTE, nao o da
        # primeira. Se as duas discordam, isso e CHANGE_OBSERVED, nao ruido.
        ult = [o for o in obs if o.get('active_status')]
        r['ACTIVE_STATUS_OBSERVED'] = val(
            (ult[-1].get('active_status') if ult else None) or e.get('active_status'))
        r['ACTIVE_STATUS_FIRST_OBSERVED'] = val(
            (ult[0].get('active_status') if ult else None) or e.get('active_status'))
        # ⚠️ `NOT_KNOWN` NAO E UM ESTADO: E A AUSENCIA DE UM.
        # A primeira versao desta conta marcou CHANGE_OBSERVED=YES num anuncio
        # que foi de INACTIVE para NOT_KNOWN. Isso nao e o mercado a mudar — e
        # a nossa leitura a piorar. Contar as duas coisas juntas faria «mudou»
        # significar «mudou OU deixamos de saber», e as duas pedem acoes opostas.
        #
        #     DEIXAR DE SABER NAO E UMA MUDANCA. E UMA PERDA DE LEITURA.
        CONHECIDOS = ('ACTIVE', 'INACTIVE')
        estados = [o.get('active_status') for o in obs if o.get('active_status')]
        conhecidos = [x for x in estados if x in CONHECIDOS]
        r['CHANGE_OBSERVED'] = (
            'NOT_COMPARABLE' if len(conhecidos) < 2
            else 'NO' if len(set(conhecidos)) == 1 else 'YES')
        r['OBSERVATION_DEGRADED_TO_UNKNOWN'] = bool(
            conhecidos) and any(x not in CONHECIDOS for x in estados)
        r['CHANGE_OBSERVED_LAW'] = (
            'compara apenas leituras com estado CONHECIDO (ACTIVE/INACTIVE). '
            'NOT_KNOWN nao e estado: e ausencia dele, e ir de INACTIVE para '
            'NOT_KNOWN e a nossa leitura a piorar, nao o mercado a mudar — isso '
            'vai em OBSERVATION_DEGRADED_TO_UNKNOWN, nunca em CHANGE_OBSERVED. '
            'NOT_COMPARABLE significa menos de duas leituras conhecidas: a '
            'pergunta nao tem resposta, e isso NAO e o mesmo que «nao mudou». '
            'NO_LONGER_OBSERVED != AD_STOPPED: a fonte deixou de listar, ela '
            'nao declarou fim de veiculacao.')
        r['COUNTRY_REACHED_OBSERVED'] = val(e.get('country_reached'))
        r['COLLECTION_COMPLETENESS'] = val(e.get('collection_completeness'))
        r['CREATIVE_TEXT_HASH'] = val(e.get('creative_text_hash'))
        if r.get('OBSERVATION_WINDOW_TO'):
            r['LAST_OBSERVED'] = r['OBSERVATION_WINDOW_TO']
        if r.get('OBSERVATION_WINDOW_FROM'):
            r['FIRST_OBSERVED'] = min(
                x for x in (r['FIRST_OBSERVED'], r['OBSERVATION_WINDOW_FROM']) if x)
        r['ACERVO'] = car
        r['ACERVO_SNAPSHOT_2'] = car2
        r['TEMPORAL_PROOF_STATE'] = 'CASOU_POR_META_AD_LIBRARY_ID'

        # ⚠️ A REGRA NÃO MUDA PARA O NÚMERO SUBIR.
        # ACTIVE_PROVED exige DUAS coisas: a fonte observou ACTIVE, E existe a
        # data dessa observação. Sem a data, o presente não está provado — está
        # afirmado.
        est = r['ACTIVE_STATUS_OBSERVED']
        if est == 'ACTIVE' and r['LAST_OBSERVED']:
            r['ACTIVE_PROOF'] = 'ACTIVE_PROVED'
            r['ACTIVE_PROOF_WHY'] = (
                'a fonte observou ACTIVE em %s, e a data da observacao atravessa'
                % r['LAST_OBSERVED'])
            provado += 1
        elif est == 'INACTIVE':
            r['ACTIVE_PROOF'] = 'HISTORICAL'
            r['ACTIVE_PROOF_WHY'] = (
                'a fonte observou INACTIVE em %s. Historico NUNCA vira ativo.'
                % (r['LAST_OBSERVED'] or 'data ausente'))
            historico += 1
        else:
            r['ACTIVE_PROOF'] = 'ACTIVE_UNKNOWN'
            r['ACTIVE_PROOF_WHY'] = (
                'a fonte nao declara estado, ou declara sem data de observacao')
            desconhecido += 1
        r['ACTIVE_PROOF_LAW'] = (
            'ACTIVE_PROVED exige estado observado ACTIVE **e** a data da '
            'observacao. START_DATE e quando o anuncio comecou; nao prova hoje.')
        # ⚠️ O QUE A OBSERVACAO PROVA, E O QUE NAO PROVA.
        # Medido: 372 anuncios tem UMA leitura, 20 tem duas, 22 tem tres. Uma
        # leitura prova que NAQUELE INSTANTE a fonte listava o anuncio assim.
        # NAO prova que ele esteja ativo hoje, nem o que houve entre as datas.
        #
        #     UMA LEITURA E UM PONTO, NAO UMA LINHA.
        #     E o selo que diz «ATTIVO» no presente fala de um ponto no passado.
        r['OBSERVATION_LAW'] = (
            'FIRST_OBSERVED e LAST_OBSERVED sao quando NOS observamos, nunca '
            'quando o concorrente comecou: OBSERVATION_START != ACTIVITY_START. '
            'Com OBSERVATION_COUNT=%d, isto prova o estado em AS_OF_DATE e mais '
            'nada. Quem mostra o selo tem de mostrar a data ao lado, e calcular '
            'a idade dela contra o dia da leitura.' % r['OBSERVATION_COUNT'])

        if r.get('COUNTRY_REACHED') and r['COUNTRY_REACHED_OBSERVED'] and \
                r['COUNTRY_REACHED'] != r['COUNTRY_REACHED_OBSERVED']:
            pais_divergente += 1
            r['COUNTRY_REACHED_DISAGREES'] = True
            r['COUNTRY_REACHED_WHY'] = (
                'o pacote carimbou %s pelo lote; a fonte observou %s. '
                'COUNTRY_REACHED_OBSERVED e o que a fonte viu.'
                % (r['COUNTRY_REACHED'], r['COUNTRY_REACHED_OBSERVED']))

    pagos = [r for r in d['RECORDS'] if r.get('ACTIVITY_TYPE') == 'PAID']
    d['TEMPORAL_PROOF'] = {
        'PAID_TOTAL': len(pagos),
        'MATCHED_TO_ACERVO': casou,
        'UNMATCHED': falhou,
        'WITH_LAST_OBSERVED': sum(1 for r in pagos if r.get('LAST_OBSERVED')),
        'WITH_FIRST_OBSERVED': sum(1 for r in pagos if r.get('FIRST_OBSERVED')),
        'AS_OF_DATE': as_of,
        'ACTIVE_PROVED': provado,
        'ACTIVE_UNKNOWN': desconhecido,
        'HISTORICAL': historico,
        'COUNTRY_REACHED_DISAGREEMENTS': pais_divergente,
        'CHANGE_OBSERVED': dict(Counter(r.get('CHANGE_OBSERVED') for r in pagos)),
        'OBSERVATION_DEGRADED_TO_UNKNOWN': sum(
            1 for r in pagos if r.get('OBSERVATION_DEGRADED_TO_UNKNOWN')),
    }
    obs = Counter(r.get('OBSERVATION_COUNT') for r in pagos)
    d['SNAPSHOT_COMPARISON'] = {
        'SNAPSHOT_1_AS_OF': cmp_.get('snapshot_1_as_of_date'),
        'SNAPSHOT_2_FROM': cmp_.get('snapshot_2_collection_started_at'),
        'SNAPSHOT_2_TO': cmp_.get('snapshot_2_collection_completed_at'),
        'CHANGE_OBSERVED_DECLARED_BY_SOURCE': cmp_.get('change_observed'),
        'CHANGE_OBSERVED_BASIS': cmp_.get('change_observed_basis'),
        'READ_DEPTH_CONFOUNDED': cmp_.get('read_depth_confounded'),
        'NO_LONGER_OBSERVED_NOTA': cmp_.get('no_longer_observed_nota'),
        'TEMPORAL_COMPARISON_CAPABILITY': cmp_.get('temporal_comparison_capability'),
        'FULL_LIFECYCLE_STATE_CAPABILITY': cmp_.get('full_lifecycle_state_capability'),
        'LAW': ('as duas leituras distam menos de duas horas. Isso confirma o '
                'estado duas vezes na mesma madrugada — NAO cobre um dia, uma '
                'semana nem uma campanha. E onde o snapshot 2 leu mais fundo, '
                '«novo» mede METODO, nao mercado: a propria fonte declara isso '
                'em READ_DEPTH_CONFOUNDED.'),
    }
    d['OBSERVATION_DEPTH'] = {
        'BY_OBSERVATION_COUNT': {str(k): v for k, v in sorted(
            obs.items(), key=lambda x: (x[0] is None, x[0]))},
        'AS_OF_DATE': as_of,
        'LAW': ('a leitura prova o estado em AS_OF_DATE e mais nada: nao prova '
                'continuidade, nao prova hoje. Quem mostra o selo tem de mostrar '
                'a data ao lado e calcular a idade dela contra o dia em que le.'),
        'DEPTH_IS_NOT_UNIFORM': (
            'a maioria tem UMA leitura; uma parte tem duas ou tres. Onde ha uma '
            'so, CHANGE_OBSERVED nao tem resposta — nao se sabe se o anuncio '
            'saiu do ar entre uma data e outra, porque nao ha outra data.'),
        'WHAT_A_SECOND_READING_ADDS': (
            'com duas leituras a pergunta «saiu do ar entre elas?» passa a ter '
            'resposta. Com uma, ela nao tem.'),
    }
    d['TEMPORAL_PROOF_LAW'] = (
        'o selo ATTIVO passa a vir acompanhado da data em que a fonte foi vista. '
        'A regra de negocio NAO mudou para o numero subir: mudou o que atravessa.')
    d['COUNTRY_LAW'] = (
        'COUNTRY_REACHED nos 414 foi carimbado pelo lote. '
        'COUNTRY_REACHED_OBSERVED e o que a fonte observou, e discorda em %d.'
        % pais_divergente)
    fr = dict(d.get('FIELD_ROLES') or {})
    fr.update({'ACTIVE_PROOF': 'CANONICAL', 'LAST_OBSERVED': 'CANONICAL',
               'FIRST_OBSERVED': 'CANONICAL'})
    d['FIELD_ROLES'] = fr
    d['ACERVO_SOURCES'] = [chave]
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)

    print('== PROVA TEMPORAL DOS ANUNCIOS ==')
    for k, v in d['TEMPORAL_PROOF'].items():
        print('  %-32s %s' % (k, v))
    print('  %-32s %s' % ('ACTIVE declarado no pacote',
                          Counter(r.get('ACTIVE_STATUS') for r in pagos)['ACTIVE']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
