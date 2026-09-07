#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O TEXTO CIENTÍFICO ATRAVESSA — e o termo de busca para de passar por fato.

    python3 scripts/v21_ciencia_texto.py

DOIS DEFEITOS, UM INSUMO
-------------------------
1. `SCIENCE.json` não tem campo de texto. Os 88 registros trazem título, DOI e
   autor — e nenhum abstract. O acervo tem 618 abstracts e 612.291 caracteres.
   Dos 88 que já atravessam, **81 ganham abstract aqui: 93.889 caracteres**.

2. `CROP` e `ISSUE` dos 88 são o TERMO DA BUSCA, não o que o texto prova. O
   registro `IT-SCI-001` diz `ISSUE: REPILO` sobre um paper de *Xylella
   fastidiosa* — porque a busca que o achou usava «repilo». Medido nos 86 que
   casam por DOI: **39 são OFF_CASE**.

        QUERY_TERM NÃO É PROVED_CONTENT.
        Um é a pergunta que fiz; o outro é a resposta que o texto deu.

POR QUE NÃO TROCO `CROP` PELO PROVADO
--------------------------------------
Porque isso mudaria, em silêncio, o que 88 cartões já publicados afirmam. O
campo antigo fica onde está, com o nome que sempre teve; ao lado entram
`QUERY_CROP`, `PROVED_CROP` e a EVIDÊNCIA de cada um — a frase do próprio texto
que sustenta a leitura. Quem consome decide. E `CROP_IS_QUERY_TERM` diz, em
cada registro, que o campo antigo é a pergunta.

POR QUE OS 675 NÃO ENTRAM EM `SCIENCE.json`
--------------------------------------------
Porque não é filtro: **nenhum passo da cadeia lê o corpus de 763**. Os 88 são
transporte 1:1 de `PREVIOUS-HANDOFF/.../SCIENCE/scientific-records.json`, e os
86 com DOI são subconjunto estrito do corpus — 0 existem só do lado velho.

Despejar 675 registros dentro da família que a tela já mostra seria mudar a
população de um cartão publicado sem ninguém pedir. Então o corpus inteiro entra
em `SCIENCE-CORPUS.json`, com estado por registro, e a adoção é decisão de quem
consome — não efeito colateral desta linhagem.

    PACOTE MELHOR NÃO É PACOTE MAIS CHEIO. É PACOTE QUE DIZ O QUE TEM.
"""
import json
import os
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v21_normalizar as N  # noqa: E402
from acervo_fonte import carimbo, ler, manifesto, sha256_texto  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')

SENT = ('NÃO SEI', 'NAO SEI', 'UNKNOWN', 'NOT_KNOWN', 'NONE', '')


def val(v):
    """`NÃO SEI` do acervo continua UNKNOWN aqui. Não vira vazio nem some."""
    s = str(v).strip() if v is not None else ''
    return 'UNKNOWN' if s.upper() in SENT else s


def boo(v):
    """O acervo grava `True`/`False` como STRING. Aqui volta a ser booleano."""
    s = str(v).strip().lower()
    return True if s == 'true' else False if s == 'false' else None


def doi(v):
    return (str(v or '').strip().lower()
            .replace('https://doi.org/', '').replace('http://doi.org/', ''))


def texto_cientifico(m):
    """O bloco de texto científico canônico: original, língua, hash, fonte."""
    a = m.get('ABSTRACT') or ''
    a = '' if a.strip().upper() in SENT else a
    return OrderedDict([
        ('ABSTRACT_ORIGINAL', a or None),
        ('ABSTRACT_LANGUAGE', val(m.get('LANGUAGE')) or 'UNKNOWN'),
        ('ABSTRACT_CHARS', len(a)),
        ('ABSTRACT_SHA256', sha256_texto(a) if a else None),
        ('ABSTRACT_SOURCE', val(m.get('SOURCE_ROUTE'))),
        ('ABSTRACT_TRANSLATED_TEXT', None),
        ('ABSTRACT_TRANSLATION_METHOD', 'NAO_TRADUZIDO'),
        ('ABSTRACT_LAW',
         'ABSTRACT_ORIGINAL e a palavra da fonte e NUNCA e substituido. Se um '
         'dia houver traducao, ela entra em ABSTRACT_TRANSLATED_TEXT, ao lado, '
         'com o metodo declarado — nunca por cima.'),
    ])


def prova(m):
    """A separação que o acervo já faz, e que o pacote não transportava."""
    return OrderedDict([
        ('QUERY_CROP', val(m.get('QUERY_CROP'))),
        ('QUERY_ISSUE', val(m.get('QUERY_ISSUE'))),
        ('PROVED_CROP', val(m.get('PROVED_CROP'))),
        ('PROVED_CROP_EVIDENCE', val(m.get('PROVED_CROP_EVIDENCE'))),
        ('PROVED_ISSUE', val(m.get('PROVED_ISSUE'))),
        ('PROVED_ISSUE_EVIDENCE', val(m.get('PROVED_ISSUE_EVIDENCE'))),
        ('CASE_ADHERENCE', val(m.get('CASE_ADHERENCE'))),
        ('CASE_ID_DECLARED', val(m.get('CASE_ID'))),
        ('COUNTRY_OF_FACT', val(m.get('COUNTRY_OF_FACT'))),
        ('COUNTRY_OF_FACT_EVIDENCE', val(m.get('COUNTRY_OF_FACT_EVIDENCE'))),
        ('REGION_OF_FACT', val(m.get('REGION_OF_FACT'))),
        ('PERSON_PROOF', val(m.get('PERSON_PROOF'))),
        ('PERSON_PROOF_EVIDENCE', val(m.get('PERSON_PROOF_EVIDENCE'))),
        ('DOMAIN_STATE', val(m.get('DOMAIN_STATE'))),
        ('DOMAIN_FIELD', val(m.get('DOMAIN_FIELD'))),
        ('QUERY_VS_PROVED_LAW',
         'QUERY_* e o termo que a busca usou. PROVED_* e o que o texto sustenta, '
         'com a frase de evidencia ao lado. Nao se promove um ao outro.'),
    ])


# ⚠️ ESTE BLOCO CORRIGE UM DEFEITO QUE ESTA MISSAO INTRODUZIU.
#
# `ISSUE_IDS` estava VAZIO em 88/88 porque o laco de ingest pedia um campo que a
# ciencia nao tem. Corrigido o campo, ele passou a ser preenchido 88/88 a partir
# de `ISSUE` — que e o TERMO DA BUSCA, nao o que o texto prova.
#
# `ISSUE_IDS` nao e rotulo: e CHAVE DE JUNCAO, lida por v21_oportunidades.py,
# v21_catraca.py e v21_necessidade.py. Enche-la com o termo da busca faz o motor
# juntar por uma pergunta e apresentar o resultado como resposta.
#
#     CONSERTAR O CAMPO ERRADO E DEPOIS ENCHE-LO COM O VALOR ERRADO
#     TROCA UM VAZIO HONESTO POR UM CHEIO FALSO. O SEGUNDO E PIOR.
#
# Medido nos 88: PROVED_ISSUE e conhecido em 39. Em 6 deles o texto prova
# XYLELLA onde a busca dizia REPILO ou FLAVESCENCE. Se o motor juntasse pelo
# termo da busca, esses 6 entrariam num caso que o proprio texto contradiz.
#
# Entao: ISSUE_IDS passa a sair do PROVADO, e so dele. O termo da busca continua
# a viajar, com nome que diz o que ele e.
#
# CROP_IDS NAO e mexido aqui. Ele ja vinha do termo da busca ANTES desta missao
# (87/88), e mudar a populacao de uma familia publicada nao e decisao desta
# linhagem — fica declarado em CROP_IDS_ARE_QUERY_DERIVED e no relatorio de
# perdas, para quem consome decidir.
def chaves_de_juncao(r):
    """ISSUE_IDS sai do PROVADO. O termo da busca vai para o campo que o nomeia."""
    r['ISSUE_IDS_QUERY'] = list(r.get('ISSUE_IDS') or [])
    prov = r.get('PROVED_ISSUE')
    pid = N.issue_id(prov) if prov and prov != 'UNKNOWN' else None
    r['ISSUE_IDS'] = [pid] if pid else []
    r['PROVED_ISSUE_ID'] = pid
    r['ISSUE_IDS_LAW'] = (
        'ISSUE_IDS sai de PROVED_ISSUE — o que o TEXTO sustenta, com a frase de '
        'evidencia em PROVED_ISSUE_EVIDENCE. ISSUE_IDS_QUERY guarda o termo que '
        'a busca usou. Vazio aqui significa «o texto nao prova alvo», e nao «a '
        'fonte nao declarou».')
    pc = r.get('PROVED_CROP')
    cid = N.crop_id(pc) if pc and pc != 'UNKNOWN' else None
    r['PROVED_CROP_ID'] = cid
    r['CROP_IDS_ARE_QUERY_DERIVED'] = True
    r['CROP_IDS_LAW'] = (
        'CROP_IDS deste registro vem do TERMO DA BUSCA, e vinha assim antes '
        'desta missao. PROVED_CROP_ID e a chave que o texto sustenta. Trocar a '
        'primeira pela segunda muda a populacao de uma familia publicada, e '
        'essa decisao e de quem consome.')
    return r


def estado(m):
    """INCLUDED · EXCLUDED · UNKNOWN — e a razão, sempre."""
    dom = val(m.get('DOMAIN_STATE'))
    pes = val(m.get('PERSON_PROOF'))
    if dom == 'OFF_DOMAIN':
        return 'EXCLUDED', 'DOMAIN_STATE=OFF_DOMAIN: o campo do trabalho nao e agro'
    if dom == 'NO_TOPIC':
        return 'UNKNOWN', 'a fonte nao declara campo do trabalho'
    if pes == 'NAME_MATCH_ONLY':
        return 'EXCLUDED', ('PERSON_PROOF=NAME_MATCH_ONLY: so o nome bate, e '
                            'homonimo nao e prova de autoria')
    return 'INCLUDED', 'em dominio agro e com autoria provada alem do nome'


def main():
    if not os.path.isdir(ING):
        raise SystemExit('o pacote nao esta montado: rode antes scripts/v21_ingest.py')
    fontes = {s['KEY']: s for s in manifesto()['SOURCES']}
    chave = [k for k, s in fontes.items() if s['FAMILY'] == 'SCIENCE'][0]
    corp = ler(chave, fontes)
    car = carimbo(chave, fontes)
    M = corp['MATERIALS']
    por_doi = {}
    for m in M:
        d = doi(m.get('DOI'))
        if d:
            por_doi.setdefault(d, m)

    # ── 1 · os 88 que já atravessam ganham texto e a separação query/proved ──
    p = os.path.join(ING, 'SCIENCE.json')
    sci = json.load(open(p, encoding='utf-8'))
    # o mesmo paper existe com DOIS IDs: IT-SCI-001 na familia publicada e
    # IT-SCIC-W… no corpus. Nao e duplicata de dado — e a mesma entidade vista
    # de dois angulos. O registro central proibe ambiguidade, e a saida nao e
    # esconder o segundo: e DECLARAR o par.
    ID_NO_SCIENCE = {doi(x.get('DOI')): x.get('ID')
                     for x in sci['RECORDS'] if doi(x.get('DOI'))}
    DOIS_NO_SCIENCE = set(ID_NO_SCIENCE)
    casou = ganhou = ch = 0
    for r in sci['RECORDS']:
        m = por_doi.get(doi(r.get('DOI')))
        r['CROP_IS_QUERY_TERM'] = True
        r['ISSUE_IS_QUERY_TERM'] = True
        r['QUERY_TERM_LAW'] = (
            'CROP e ISSUE deste registro sao o TERMO DA BUSCA que achou o paper, '
            'nao o que o texto prova. Os campos PROVED_* ao lado dizem o que o '
            'texto sustenta, com a frase de evidencia.')
        if not m:
            r['ACERVO_MATCH'] = 'NAO_CASOU_POR_DOI'
            r['ACERVO_MATCH_WHY'] = (
                'este registro nao tem DOI, ou o DOI nao existe no corpus de 763')
            continue
        casou += 1
        r['ACERVO_MATCH'] = 'CASOU_POR_DOI'
        r['ACERVO_MATCH_WHY'] = 'mesmo DOI no corpus RESEARCHER-CORPUS-EAME-V1'
        r.update(prova(m))
        chaves_de_juncao(r)
        t = texto_cientifico(m)
        r.update(t)
        r['MATERIAL_ID'] = val(m.get('MATERIAL_ID'))
        r['CITED_BY'] = m.get('CITED_BY')
        r['IS_RETRACTED'] = boo(m.get('IS_RETRACTED'))
        r['ACERVO'] = car
        if t['ABSTRACT_CHARS']:
            ganhou += 1
            ch += t['ABSTRACT_CHARS']

    sci['ABSTRACTS_PRESENT'] = ganhou
    sci['ABSTRACT_CHARS'] = ch
    sci['ACERVO_MATCHED_BY_DOI'] = casou
    sci['BY_CASE_ADHERENCE'] = dict(Counter(
        r.get('CASE_ADHERENCE', 'SEM_CORRESPONDENCIA') for r in sci['RECORDS']))
    sci['JOIN_KEYS'] = {
        'ISSUE_IDS_FROM_PROVED': sum(1 for r in sci['RECORDS'] if r.get('ISSUE_IDS')),
        'ISSUE_IDS_QUERY_POPULATED': sum(
            1 for r in sci['RECORDS'] if r.get('ISSUE_IDS_QUERY')),
        'PROVED_CROP_ID_KNOWN': sum(
            1 for r in sci['RECORDS'] if r.get('PROVED_CROP_ID')),
        'CROP_IDS_STILL_QUERY_DERIVED': sum(
            1 for r in sci['RECORDS'] if r.get('CROP_IDS')),
        'LAW': ('ISSUE_IDS e chave de juncao e sai do PROVADO. CROP_IDS continua '
                'como estava antes desta missao — termo de busca — e diz isso.'),
    }
    sci['QUERY_VS_PROVED'] = {
        'CROP_QUERY_EQUALS_PROVED': sum(
            1 for r in sci['RECORDS']
            if r.get('PROVED_CROP') and r.get('PROVED_CROP') == r.get('QUERY_CROP')),
        'ISSUE_QUERY_EQUALS_PROVED': sum(
            1 for r in sci['RECORDS']
            if r.get('PROVED_ISSUE') and r.get('PROVED_ISSUE') == r.get('QUERY_ISSUE')),
        'OFF_CASE': sum(1 for r in sci['RECORDS']
                        if r.get('CASE_ADHERENCE') == 'OFF_CASE'),
    }
    sci['LOCALIZED_FIELDS'] = sorted(set(sci.get('LOCALIZED_FIELDS') or []))
    fr = dict(sci.get('FIELD_ROLES') or {})
    fr.update({'ABSTRACT_ORIGINAL': 'RAW_ORIGINAL', 'TITLE': 'RAW_ORIGINAL',
               'PROVED_CROP_EVIDENCE': 'RAW_ORIGINAL',
               'PROVED_ISSUE_EVIDENCE': 'RAW_ORIGINAL'})
    sci['FIELD_ROLES'] = fr
    sci['POPULATION_LAW'] = (
        'esta familia continua com os 88 do handoff anterior. O corpus completo '
        'de 763 vive em SCIENCE-CORPUS.json, com estado por registro — adota-lo '
        'e decisao de quem consome, nao efeito colateral desta cadeia.')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(sci, f, ensure_ascii=False, indent=1)

    # ── 2 · o corpus inteiro, com estado por registro ────────────────────────
    recs = []
    for m in M:
        st, why = estado(m)
        r = OrderedDict()
        r['ID'] = 'IT-SCIC-' + val(m.get('MATERIAL_ID')).rsplit('/', 1)[-1]
        r['ENTITY_TYPE'] = 'SCIENTIFIC_MATERIAL'
        r['PROVENANCE'] = 'REAL_SOURCE'
        r['QA_STATUS'] = 'EVIDENCE_SOURCED' if st == 'INCLUDED' else 'EVIDENCE_UNSPECIFIED'
        r['CLIENT_SAFE'] = st == 'INCLUDED'
        r['SOURCE_IDS'] = ['SRC_DOI_ORG'] if m.get('DOI') else ['SRC_OPENALEX_ORG']
        r['SOURCE_URLS'] = [m['SOURCE_URL']] if m.get('SOURCE_URL') else []
        r['REFERENCE_DATE'] = val(m.get('PUBLISHED_AT')) or None
        r['CROP_IDS'] = []
        r['ISSUE_IDS'] = []
        r['REGION_IDS'] = []
        r['GEOGRAPHIC_SCOPE'] = 'NAO_SEI'
        r['STATE'] = st
        r['STATE_REASON'] = why
        r['MATERIAL_ID'] = val(m.get('MATERIAL_ID'))
        r['DOI'] = val(m.get('DOI'))
        r['TITLE'] = m.get('TITLE')
        r['AUTHOR'] = m.get('NAME')
        r['ORCID'] = val(m.get('ORCID'))
        r['INSTITUTION'] = val(m.get('INSTITUTION'))
        r['INSTITUTION_COUNTRY'] = val(m.get('INSTITUTION_COUNTRY'))
        r['PUBLISHED_AT'] = val(m.get('PUBLISHED_AT'))
        r['VENUE'] = val(m.get('VENUE'))
        r['VENUE_KIND'] = val(m.get('VENUE_KIND'))
        r['MATERIAL_TYPE'] = val(m.get('MATERIAL_TYPE'))
        r['MATERIAL_ROLE'] = val(m.get('MATERIAL_ROLE'))
        r['LANGUAGE'] = val(m.get('LANGUAGE'))
        r['CITED_BY'] = m.get('CITED_BY')
        r['IS_RETRACTED'] = boo(m.get('IS_RETRACTED'))
        r.update(prova(m))
        r.update(texto_cientifico(m))
        # ⚠️ ESTA LINHA JA ESTEVE ERRADA, e o erro era mudo: `doi(None)` devolve
        # string vazia, e 85 materiais sem DOI casavam com 2 registros sem DOI —
        # 171 «ja em SCIENCE.json» onde ha 86.
        #
        #     CHAVE QUE CASA POR AUSENCIA NAO E CHAVE: E COINCIDENCIA DE VAZIO.
        r['IN_SCIENCE_JSON'] = bool(doi(m.get('DOI'))) and doi(m.get('DOI')) in DOIS_NO_SCIENCE
        r['SAME_ENTITY_AS'] = ID_NO_SCIENCE.get(doi(m.get('DOI')))
        r['SAME_ENTITY_LAW'] = (
            'quando preenchido, este registro e O MESMO PAPER que aquele ID em '
            'SCIENCE.json, por DOI. Dois IDs, uma entidade — declarado, nao '
            'escondido.') if r['SAME_ENTITY_AS'] else None
        r['ACERVO'] = car
        r['EVIDENCE_STATUS'] = r['QA_STATUS']
        r['EVIDENCE_STATUS_WHY'] = (
            'registro capturado de fonte publica identificada, com URL e data.')
        r['ORIGIN_LAYER'] = 'ACERVO_PINNED'
        r['CLAIM_DOMAIN'] = 'DOMAIN_INTELLIGENCE'
        recs.append(r)
    recs.sort(key=lambda r: r['ID'])

    abst = [r for r in recs if r['ABSTRACT_CHARS']]
    corpo = OrderedDict()
    corpo['COLLECTION'] = 'SCIENCE_CORPUS'
    corpo['FILE'] = 'SCIENCE-CORPUS.json'
    corpo['SCHEMA_VERSION'] = 'V2.1'
    corpo['BUILT_AT'] = '2026-09-02'
    corpo['PRIMARY_KEY'] = 'ID'
    corpo['SOURCE_OF_TRUTH'] = 'OpenAlex · ORCID · DOI'
    corpo['COUNT_TOTAL'] = len(recs)
    corpo['COUNT_CLIENT_SAFE'] = sum(1 for r in recs if r['CLIENT_SAFE'])
    corpo['BY_ORIGIN'] = dict(Counter(r['ORIGIN_LAYER'] for r in recs))
    corpo['BY_QA'] = dict(Counter(r['QA_STATUS'] for r in recs))
    corpo['BY_STATE'] = dict(Counter(r['STATE'] for r in recs))
    corpo['BY_STATE_REASON'] = dict(Counter(r['STATE_REASON'] for r in recs))
    corpo['BY_CASE_ADHERENCE'] = dict(Counter(r['CASE_ADHERENCE'] for r in recs))
    corpo['BY_LANGUAGE'] = dict(Counter(r['LANGUAGE'] for r in recs))
    corpo['BY_COUNTRY_OF_FACT'] = dict(Counter(r['COUNTRY_OF_FACT'] for r in recs))
    corpo['ABSTRACTS_PRESENT'] = len(abst)
    corpo['ABSTRACT_CHARS'] = sum(r['ABSTRACT_CHARS'] for r in recs)
    corpo['ALREADY_IN_SCIENCE_JSON'] = sum(1 for r in recs if r['IN_SCIENCE_JSON'])
    corpo['SAME_ENTITY_PAIRS'] = sum(1 for r in recs if r.get('SAME_ENTITY_AS'))
    corpo['DISTINCT_DOI'] = len({r['DOI'] for r in recs if r['DOI'] != 'UNKNOWN'})
    corpo['WITHOUT_DOI'] = sum(1 for r in recs if r['DOI'] == 'UNKNOWN')
    corpo['LAW'] = (
        'os 88 de SCIENCE.json sao SUBCONJUNTO deste corpus: 86 casam por DOI e '
        'nenhum existe so do lado velho. A diferenca nao e filtro — e que '
        'nenhum passo da cadeia lia este arquivo.')
    corpo['LOCALIZED_FIELDS'] = ['EVIDENCE_STATUS_WHY']
    corpo['LOCALIZATION_LAW'] = (
        'ABSTRACT_ORIGINAL e a palavra da fonte e nao se traduz. Se houver '
        'traducao, ela entra ao lado, com metodo declarado.')
    corpo['FIELD_ROLES'] = {
        'ABSTRACT_ORIGINAL': 'RAW_ORIGINAL', 'TITLE': 'RAW_ORIGINAL',
        'PROVED_CROP_EVIDENCE': 'RAW_ORIGINAL',
        'PROVED_ISSUE_EVIDENCE': 'RAW_ORIGINAL',
        'PERSON_PROOF_EVIDENCE': 'RAW_ORIGINAL',
        'EVIDENCE_STATUS_WHY': 'CLIENT_NARRATIVE'}
    corpo['LOCALIZATION_CONTRACT'] = (
        'so CLIENT_NARRATIVE e CLIENT_LABEL pedem irmao _IT/_EN. RAW_ORIGINAL e '
        'citacao e fica na lingua publicada.')
    corpo['ACERVO_SOURCES'] = [chave]
    corpo['RECORDS'] = recs
    q = os.path.join(ING, 'SCIENCE-CORPUS.json')
    with open(q, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)

    print('== SCIENCE.json enriquecido ==')
    print('  casaram por DOI          : %d/%d' % (casou, len(sci['RECORDS'])))
    print('  ganharam abstract        : %d   (%s caracteres)' % (ganhou, f'{ch:,}'))
    print('  aderencia ao caso        : %s' % sci['BY_CASE_ADHERENCE'])
    print('  query vs proved          : %s' % sci['QUERY_VS_PROVED'])
    print('  chaves de juncao         : %s' % {
        k: v for k, v in sci['JOIN_KEYS'].items() if k != 'LAW'})
    print('== SCIENCE-CORPUS.json ==')
    print('  registros                : %d  (client-safe %d)' % (
        len(recs), corpo['COUNT_CLIENT_SAFE']))
    print('  estados                  : %s' % corpo['BY_STATE'])
    print('  abstracts                : %d   (%s caracteres)' % (
        len(abst), f'{corpo["ABSTRACT_CHARS"]:,}'))
    print('  ja em SCIENCE.json       : %d' % corpo['ALREADY_IN_SCIENCE_JSON'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
