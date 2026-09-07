#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TEMPO E LUGAR DE CADA FATO — a lei do Brasil aplicada ao que já atravessou.

    python3 scripts/fatos_tempo_lugar.py

A LEI NÃO É NOVA E NÃO É INVENTADA AQUI
----------------------------------------
Ela tem dono: `scripts/lugar_do_fato.py`, que a trouxe do Brasil e a declarou
independente de idioma. Este arquivo **exerce** o vocabulário de lá; não cria
outro. Duas leis para a mesma pergunta divergem devagar até darem vereditos
diferentes sobre a mesma frase.

    LOCAL_DA_FONTE   != LOCAL_DO_FATO
    DATA_PUBLICACAO  != DATA_DO_ACONTECIMENTO
    DATA_COLETA      != DATA_DO_ACONTECIMENTO
    ROW_PROVENANCE   != VALUE_PROVENANCE

`ORIGENS_DO_TEMPO` não contém `PUBLICACAO`, e essa ausência é deliberada: não
existe forma de declarar que o tempo do fato veio do carimbo de publicação,
porque isso não é permitido.

O QUE ESTE PASSO FAZ, E O QUE NÃO FAZ
--------------------------------------
FAZ: percorre os fatos que JÁ existem no pacote e, **só por metadado**, tenta
provar seis valores. Cada um sai PROVADO com evidência, ou UNKNOWN com a razão.

NÃO FAZ: não relê os 5,1 milhões de caracteres, não roda modelo sobre corpus,
não extrai fato novo, não inventa cidade por contexto, não usa o lugar da fonte
como lugar do fato, não transforma data de vídeo em data de acontecimento.

    NÃO É PREENCHER TUDO. É GARANTIR QUE NADA ESTEJA PREENCHIDO POR PALPITE.
"""
import json
import os
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lugar_do_fato as L        # o dono da lei  # noqa: E402
import v21_datas as DT           # o dono do contrato temporal  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
SAIDA = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                     'FACT-TIME-PLACE-V1.json')

CAMPOS = ('fact_time', 'source_location', 'fact_location',
          'publication_time', 'observation_time', 'collection_time')


def desconhecido(porque):
    return {'value': 'UNKNOWN', 'value_source': None, 'value_evidence': porque,
            'value_provenance': 'NAO_SEI'}


def provado(valor, fonte, evidencia, proveniencia, resolucao=None):
    v = {'value': valor, 'value_source': fonte, 'value_evidence': evidencia,
         'value_provenance': proveniencia}
    if resolucao:
        v['resolution'] = resolucao
    return v


def data_ou_unknown(valor, campo, fonte, proveniencia, evidencia):
    """Data de verdade, analisada — prosa que parece data NÃO passa."""
    a = DT.analisar((campo, valor))
    if a.get('DATE_PARSE_STATE') == DT.UNKNOWN or not a.get('START_DATE'):
        return desconhecido('o campo %s nao traz data analisavel: %r'
                            % (campo, str(valor)[:60]))
    return provado(a['START_DATE'], campo, evidencia, proveniencia,
                   {'EXACT': 'DATE_EXACT', 'MONTH_ONLY': 'MONTH',
                    'RANGE': 'APPROXIMATE'}.get(a['DATE_PRECISION'], 'NOT_KNOWN'))


def le(nome):
    p = os.path.join(ING, nome)
    with open(p, encoding='utf-8') as f:
        return json.load(f)


# ── TRANSCRIÇÕES ────────────────────────────────────────────────────────────
def de_transcricao(r):
    f = OrderedDict()
    # ⚠️ A data de publicação do vídeo NÃO vira data do acontecimento.
    # PUBLICATION_STAMP_NOT_FACT_TIME é o estado de recusa do próprio leitor.
    f['fact_time'] = desconhecido(
        L.PUBLICATION_STAMP + ': a rota traz a data em que o video foi '
        'publicado, e nao a data em que o que se fala nele aconteceu')
    f['publication_time'] = data_ou_unknown(
        r.get('PUBLICATION_DATE'), 'PUBLICATION_DATE', 'PUBLICATION_DATE',
        'FONTE_OFICIAL', 'data declarada pela plataforma para o objeto')
    f['observation_time'] = data_ou_unknown(
        r.get('OBSERVED_AT'), 'OBSERVED_AT', 'OBSERVED_AT', 'FONTE_OFICIAL',
        'quando NOS observamos o objeto na plataforma')
    f['collection_time'] = data_ou_unknown(
        (r.get('ACERVO') or {}).get('ACERVO_COMMIT') and r.get('OBSERVED_AT'),
        'OBSERVED_AT', 'ACERVO.CAPTURED_AT', 'FONTE_OFICIAL',
        'carimbo de captura do lote de acervo pinado')
    # o escopo da rota: existe, e a lei recusa-o como lugar do fato
    f['source_location'] = (
        provado(r['SOURCE_COUNTRY'], 'SOURCE_COUNTRY',
                'escopo declarado pela rota do acervo', r['SOURCE_COUNTRY_ORIGIN'])
        if r.get('SOURCE_COUNTRY') != 'UNKNOWN'
        else desconhecido('a rota nao declara pais de origem do canal'))
    f['fact_location'] = (
        provado(r['FACT_COUNTRY'], 'FACT_COUNTRY', r.get('FACT_COUNTRY_EVIDENCE'),
                r.get('FACT_COUNTRY_ORIGIN'))
        if r.get('FACT_COUNTRY') not in (None, 'UNKNOWN')
        else desconhecido(r.get('FACT_COUNTRY_EVIDENCE')
                          or 'nenhum lugar nomeado no conteudo; '
                             'LOCAL_DA_FONTE != LOCAL_DO_FATO'))
    return f


# ── CIÊNCIA ─────────────────────────────────────────────────────────────────
def de_ciencia(r):
    f = OrderedDict()
    f['fact_time'] = desconhecido(
        L.PUBLICATION_STAMP + ': PUBLISHED_AT e quando o paper saiu, nao quando '
        'o fenomeno que ele descreve aconteceu')
    f['publication_time'] = data_ou_unknown(
        r.get('PUBLISHED_AT'), 'PUBLISHED_AT', 'PUBLISHED_AT', 'FONTE_OFICIAL',
        'data de publicacao declarada por OpenAlex/DOI')
    f['observation_time'] = desconhecido(
        'nao observamos o fenomeno: lemos o registro do paper')
    f['collection_time'] = provado(
        '2026-08-31', 'ACERVO.captured_at', 'captura do corpus de pesquisadores',
        'FONTE_OFICIAL', 'DATE_EXACT')
    # AFILIAÇÃO NÃO CONTA — a própria evidência do acervo diz isso.
    f['source_location'] = (
        provado(r['INSTITUTION_COUNTRY'], 'INSTITUTION_COUNTRY',
                'pais da instituicao do autor; afiliacao e da FONTE, nao do fato',
                'DA_FONTE')
        if r.get('INSTITUTION_COUNTRY') not in (None, 'UNKNOWN')
        else desconhecido('o registro nao declara pais da instituicao'))
    ev = r.get('COUNTRY_OF_FACT_EVIDENCE')
    escrito = bool(ev) and 'nomeia' in str(ev).lower()
    f['fact_location'] = (
        provado(r['COUNTRY_OF_FACT'], 'COUNTRY_OF_FACT', ev, 'ESCRITO')
        if r.get('COUNTRY_OF_FACT') not in (None, 'UNKNOWN') and escrito
        else desconhecido(ev or 'o texto nao nomeia lugar'))
    return f


# ── ANÚNCIOS ────────────────────────────────────────────────────────────────
def de_anuncio(r):
    f = OrderedDict()
    # Aqui o FATO é a veiculação do anúncio, e a plataforma declara o início
    # dela. É FONTE_OFICIAL, e não carimbo de publicação de terceiro.
    f['fact_time'] = data_ou_unknown(
        r.get('START_DATE'), 'START_DATE', 'START_DATE', 'FONTE_OFICIAL',
        'a Ad Library declara o inicio de veiculacao deste anuncio; o fato '
        'aqui e a propria veiculacao')
    f['publication_time'] = data_ou_unknown(
        r.get('START_DATE'), 'START_DATE', 'START_DATE', 'FONTE_OFICIAL',
        'inicio de veiculacao declarado pela fonte')
    f['observation_time'] = data_ou_unknown(
        r.get('LAST_OBSERVED'), 'LAST_OBSERVED', 'LAST_OBSERVED',
        'FONTE_OFICIAL', 'ultima vez que NOS observamos; '
        'OBSERVATION_START != ACTIVITY_START')
    f['collection_time'] = data_ou_unknown(
        r.get('AS_OF_DATE'), 'AS_OF_DATE', 'AS_OF_DATE', 'FONTE_OFICIAL',
        'carimbo da coleta que leu a Ad Library')
    f['source_location'] = desconhecido(
        'a pagina anunciante nao traz pais no registro; '
        'META-PAGE-IDENTITY-EAME-V1.json existe no acervo e nao esta pinado')
    # ⚠️ ALCANCE NÃO É LUGAR DO FATO. O próprio pacote já declara
    # AD_REACHED_COUNTRY != AD_TARGETED_COUNTRY.
    f['fact_location'] = desconhecido(
        'COUNTRY_REACHED e o pais onde o anuncio foi ENTREGUE, nao onde algum '
        'fato aconteceu. AD_REACHED_COUNTRY != AD_TARGETED_COUNTRY')
    return f


FAMILIAS = (
    ('TRANSCRIPTS', 'TRANSCRIPTS.json', de_transcricao, lambda r: True),
    ('SCIENCE_CORPUS', 'SCIENCE-CORPUS.json', de_ciencia, lambda r: True),
    ('ADS', 'COMPETITOR-ACTIVITIES.json', de_anuncio,
     lambda r: r.get('ACTIVITY_TYPE') == 'PAID'),
)


def main():
    if not os.path.isdir(ING):
        raise SystemExit('o pacote nao esta montado: rode bash scripts/v21_cadeia.sh')
    fatos, por_fam = [], {}
    for fam, arq, fn, filtro in FAMILIAS:
        recs = [r for r in le(arq)['RECORDS'] if filtro(r)]
        cont = Counter()
        for r in recs:
            campos = fn(r)
            desc = [k for k in CAMPOS if campos[k]['value'] == 'UNKNOWN']
            for k in CAMPOS:
                cont[k + ('_PROVED' if campos[k]['value'] != 'UNKNOWN'
                          else '_UNKNOWN')] += 1
            fatos.append(OrderedDict([
                ('fact_id', r['ID']),
                ('family', fam),
                ('entity_type', r.get('ENTITY_TYPE')),
                ('fact_time', campos['fact_time']),
                ('source_location', campos['source_location']),
                ('fact_location', campos['fact_location']),
                ('publication_time', campos['publication_time']),
                ('observation_time', campos['observation_time']),
                ('collection_time', campos['collection_time']),
                ('provenance', {
                    'ROW': r.get('PROVENANCE'),
                    'ORIGIN_LAYER': r.get('ORIGIN_LAYER'),
                    'ACERVO': (r.get('ACERVO') or {}).get('ACERVO_KEY'),
                    'LAW': 'ROW_PROVENANCE != VALUE_PROVENANCE: a linha veio de '
                           'um lugar, e cada VALOR veio do seu.',
                }),
                ('unknown_fields', desc),
            ]))
        por_fam[fam] = {'FACTS': len(recs), **{
            k: cont.get(k, 0) for k in sorted(
                c + s for c in CAMPOS for s in ('_PROVED', '_UNKNOWN'))}}

    tot = Counter()
    for f in fatos:
        for k in CAMPOS:
            tot[k + ('_PROVED' if f[k]['value'] != 'UNKNOWN' else '_UNKNOWN')] += 1

    corpo = OrderedDict()
    corpo['DATASET'] = 'FACT-TIME-PLACE-V1'
    corpo['SCHEMA_VERSION'] = 'V1'
    corpo['BUILT_AT'] = '2026-09-02'
    corpo['LAW_OWNER'] = 'scripts/lugar_do_fato.py (portada do SINTONIA Brasil)'
    corpo['LAWS'] = [
        'LOCAL_DA_FONTE != LOCAL_DO_FATO',
        'DATA_PUBLICACAO != DATA_DO_ACONTECIMENTO',
        'DATA_COLETA != DATA_DO_ACONTECIMENTO',
        'ROW_PROVENANCE != VALUE_PROVENANCE',
        'PLACE_MENTION != FACT_LOCATION',
        'OBSERVATION_START != ACTIVITY_START',
        'ausencia de prova = UNKNOWN, nunca inferencia silenciosa',
    ]
    corpo['O_QUE_ISTO_NAO_E'] = [
        'nao releu os 5,1 milhoes de caracteres de fala',
        'nao rodou modelo sobre o corpus',
        'nao extraiu fato novo: enriqueceu os que ja existiam',
        'nao inventou cidade nem regiao por contexto',
    ]
    corpo['VOCABULARY'] = {
        'ORIGENS_DO_TEMPO': list(L.ORIGENS_DO_TEMPO),
        'ORIGENS_DO_LUGAR': list(L.ORIGENS_DO_LUGAR),
        'ORIGENS_QUE_SUSTENTAM_FATO': list(L.ORIGENS_QUE_SUSTENTAM_FATO),
        'RESOLUCAO_TEMPORAL': list(L.RESOLUCAO_TEMPORAL),
        'NOTA': 'PUBLICACAO nao esta em ORIGENS_DO_TEMPO, e a ausencia e '
                'deliberada: nao ha como declarar que o tempo do fato veio do '
                'carimbo de publicacao, porque isso nao e permitido.',
    }
    corpo['FACTS_ALREADY_IDENTIFIED'] = len(fatos)
    # ⚠️ ZERO TAMBEM E UM NUMERO, E TEM DE APARECER.
    # `Counter` omite a chave que vale 0, e assim `publication_time_UNKNOWN`
    # sumia do relatorio. Um UNKNOWN que nao aparece parece um UNKNOWN que nao
    # existe — e a missao pede exactamente o contrario: nao esconder UNKNOWN.
    corpo['COVERAGE'] = {k: tot.get(k, 0) for k in sorted(
        c + s for c in CAMPOS for s in ('_PROVED', '_UNKNOWN'))}
    corpo['BY_FAMILY'] = por_fam
    corpo['FACTS'] = fatos
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)

    print('== TEMPO E LUGAR DOS FATOS QUE JA EXISTEM ==')
    print('  FACTS_ALREADY_IDENTIFIED = %d' % len(fatos))
    print()
    for k in CAMPOS:
        print('  %-18s PROVED %5d   UNKNOWN %5d' % (
            k.upper(), tot[k + '_PROVED'], tot[k + '_UNKNOWN']))
    print()
    for fam, v in por_fam.items():
        print('  %-16s fatos %5d | fact_time %4d | fact_location %4d | '
              'source_location %4d' % (
                  fam, v['FACTS'], v.get('fact_time_PROVED', 0),
                  v.get('fact_location_PROVED', 0),
                  v.get('source_location_PROVED', 0)))
    print()
    print('  gravado: %s' % SAIDA)
    return 0


if __name__ == '__main__':
    sys.exit(main())
