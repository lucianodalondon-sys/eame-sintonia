#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A FALA ATRAVESSA — TRANSCRIPTS.json, a família que o pacote não tinha.

    python3 scripts/v21_transcricoes.py

O acervo tem 174 objetos de fala pedidos, 152 com texto e 143 utilizáveis —
4.906.742 caracteres de gente falando sobre cultura, doença e produto. O pacote
carregava, disso, **zero**. Não por filtro: por ausência de campo. Nenhum passo
da cadeia lia transcrição.

    O QUE NENHUM PASSO LÊ NÃO É PERDA MEDIDA: É PERDA SEM MEDIDOR.

Três decisões que este passo toma, e por quê.

1 · O TEXTO INTEIRO ENTRA, E ISSO NÃO CUSTA GIT
   `build/ITALY-REALITY-HANDOFF-V2.1/` é .gitignore desde 2026-09-02: a cadeia
   o reconstrói. Então os 4,9 milhões de caracteres entram no pacote e pesam
   zero no repositório. O acervo continua vivendo no seu ref, pinado por SHA256.
   Manifesto de 55 linhas no Git; conteúdo no pacote reconstruível.

2 · O TERMO DE BUSCA NÃO VIRA CULTURA
   `CROP_DECLARED_BY_THE_ROUTE` é o que a rota PROCUROU, não o que a fala PROVA.
   Por isso `CROP_IDS` sai **vazio** nestes registros, e o termo viaja com o
   nome que diz o que ele é. Promover busca a fato é exatamente o defeito que a
   ciência deste pacote já tem (39 de 88 papers são OFF_CASE).

        QUERY_TERM NÃO É PROVED_CONTENT. Nem aqui, nem lá.

3 · OS 22 SEM TEXTO ENTRAM TAMBÉM
   Com `CLIENT_SAFE=false` e a razão que a própria rota declarou — 19 delas
   «HTTP 403 actor-disabled, monthly usage hard limit exceeded». Um registro que
   some do arquivo some da contabilidade, e aí a perda vira boato.

        NENHUM REGISTRO DESAPARECE SEM ESTADO.

A LÍNGUA E O PAÍS
------------------
102 falas declaram italiano, 72 não declaram nada. 111 têm país do fato IT, 63
UNKNOWN. Nada disso é deduzido da tela que vai consumir: se a rota não disse,
fica UNKNOWN, e a decisão sobre mostrar espanhol numa tela italiana é de quem
consome — não da ingestão.
"""
import json
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_transcricoes import censo, pedidos  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')

# O texto de EVIDENCE_STATUS_WHY vem do vocabulário QUE JÁ EXISTE traduzido no
# pacote. Frase nova em campo de LEITURA obriga tradução nova — e a trava recusa
# gravar sem ela, de propósito. Reusar é o caminho certo, não atalho.
POR_QUE = ('registro capturado de fonte publica identificada, com URL e data.')
POR_QUE_VAZIO = ('a rota respondeu e nao trouxe texto. O motivo declarado pela '
                 'rota fica no registro.')


def registro(o):
    """Um objeto de fala, no envelope §8 do pacote."""
    usavel = o['STATE'] == 'INCLUDED'
    r = OrderedDict()
    r['ID'] = o['TRANSCRIPT_ID']
    r['ENTITY_TYPE'] = 'SPEECH_TRANSCRIPT'
    r['PROVENANCE'] = 'REAL_SOURCE'
    r['QA_STATUS'] = 'EVIDENCE_SOURCED' if usavel else 'EVIDENCE_UNSPECIFIED'
    r['CLIENT_SAFE'] = usavel
    r['SOURCE_IDS'] = ['SRC_' + (o['PLATFORM'] or 'UNKNOWN').upper()[:32]]
    r['SOURCE_URLS'] = [o['SOURCE_URL']] if o['SOURCE_URL'] else []
    r['REFERENCE_DATE'] = o['PUBLICATION_DATE']
    # ⚠️ VAZIO DE PROPÓSITO. A rota declarou um termo de BUSCA, e termo de busca
    # nao prova que a fala trata daquela cultura. O termo viaja abaixo, com nome.
    r['CROP_IDS'] = []
    r['ISSUE_IDS'] = []
    r['REGION_IDS'] = []
    r['GEOGRAPHIC_SCOPE'] = 'NAO_SEI'

    r['VIDEO_ID'] = o['VIDEO_ID']
    r['PLATFORM'] = o['PLATFORM']
    r['TITLE'] = o['TITLE']
    r['CHANNEL_NAME'] = o['CHANNEL_NAME']
    r['CHANNEL_ID'] = o['CHANNEL_ID']
    r['PUBLICATION_DATE'] = o['PUBLICATION_DATE']
    r['DURATION_S'] = o['DURATION_S']

    r['SOURCE_COUNTRY'] = o['SOURCE_COUNTRY']
    r['SOURCE_COUNTRY_DECLARED'] = o['SOURCE_COUNTRY_DECLARED']
    r['SOURCE_COUNTRY_ORIGIN'] = o['SOURCE_COUNTRY_ORIGIN']
    r['COLLECTION_COUNTRY'] = o['COLLECTION_COUNTRY']
    # ⚠️ O LUGAR DO FATO E OUTRO CAMPO, E QUASE SEMPRE UNKNOWN.
    r['FACT_COUNTRY'] = o['FACT_COUNTRY']
    r['FACT_COUNTRY_ORIGIN'] = o['FACT_COUNTRY_ORIGIN']
    r['FACT_COUNTRY_EVIDENCE'] = o['FACT_COUNTRY_EVIDENCE']
    r['FACT_LOCATION_LAW'] = o['FACT_LOCATION_LAW']
    r['SOURCE_LANGUAGE'] = o['SOURCE_LANGUAGE']
    r['SOURCE_LANGUAGE_DECLARED'] = o['SOURCE_LANGUAGE_DECLARED']
    r['CASE_ID'] = o['CASE_ID']
    r['CASE_COUNTRY'] = o['CASE_COUNTRY']
    r['CASE_LANGUAGE'] = o['CASE_LANGUAGE']
    # ⚠️ ESTA LEI ESTAVA ERRADA, E ERA UM DEFEITO MEU.
    # Dizia «SOURCE_COUNTRY e o pais do FATO». Nao e: e o escopo que a ROTA
    # declara sobre si mesma, e 121 dos 184 registros o traziam como «IT» sem
    # evidencia nenhuma — o carimbo do lote, lido como se fosse o lugar do fato.
    #
    #     UM VIDEO PUBLICADO POR UMA ORGANIZACAO DE MILAO
    #     NAO PROVA QUE O FATO ACONTECEU EM MILAO.
    r['COUNTRY_LAW'] = ('SOURCE_COUNTRY e o ESCOPO DA ROTA (origem DA_FONTE, que '
                        'a lei recusa como prova de fato). FACT_COUNTRY e o lugar '
                        'do fato e so nasce de ESCRITO/CITADO no conteudo. '
                        'COLLECTION_COUNTRY e onde a coleta rodou. Os tres sao '
                        'coisas diferentes, e nenhum se deduz da tela que consome.')

    r['CROP_DECLARED_BY_THE_ROUTE'] = o['CROP_DECLARED_BY_THE_ROUTE']
    r['ISSUE_DECLARED_BY_THE_ROUTE'] = o['ISSUE_DECLARED_BY_THE_ROUTE']
    r['REGION_NAMED_BY_THE_ROUTE'] = o['REGION_NAMED']
    r['ROUTE_TERM_LAW'] = ('estes tres sao TERMO DE BUSCA da rota. Nao provam '
                           'que a fala trata do assunto: por isso CROP_IDS, '
                           'ISSUE_IDS e REGION_IDS ficam vazios.')

    r['CAPTION_SOURCE'] = o['CAPTION_SOURCE']
    r['COLLECTION_ID'] = o['COLLECTION_ID']
    r['OBSERVED_AT'] = o['OBSERVED_AT']

    r['VIDEO_EXISTS'] = o['VIDEO_EXISTS']
    r['TRANSCRIPT_EXISTS'] = o['TRANSCRIPT_EXISTS']
    r['TRANSCRIPT_USABLE'] = o['TRANSCRIPT_USABLE']
    r['TRANSCRIPT_INCLUDED_IN_PACKAGE'] = usavel
    r['TRANSCRIPT_USED_AS_EVIDENCE'] = False
    r['LADDER_LAW'] = ('cinco degraus, e nenhum implica o seguinte. '
                       'TRANSCRIPT_USED_AS_EVIDENCE so vira true quando um '
                       'cartao apoiar afirmacao nestes bytes — o motor ainda '
                       'nao o faz, e por isso o campo diz false, nao omite.')

    r['TRANSCRIPT_QUALITY'] = o['TRANSCRIPT_QUALITY']
    r['STATE'] = o['STATE']
    r['STATE_REASON'] = o['STATE_REASON']
    r['CHARS'] = o['CHARS']
    r['TEXT_SHA256'] = o['TEXT_SHA256']
    r['ACERVO'] = o['ACERVO']
    if o.get('ALSO_COLLECTED_BY'):
        r['ALSO_COLLECTED_BY'] = o['ALSO_COLLECTED_BY']

    r['EVIDENCE_STATUS'] = r['QA_STATUS']
    r['EVIDENCE_STATUS_WHY'] = POR_QUE if usavel else POR_QUE_VAZIO
    r['ORIGIN_LAYER'] = 'ACERVO_PINNED'
    r['CLAIM_DOMAIN'] = 'DOMAIN_INTELLIGENCE'
    # ⚠️ RAW_ORIGINAL: a fala da fonte. Nao se traduz, nao se resume, nao se
    # substitui. O SHA256 acima e a chave de «quais bytes sustentam isto».
    r['TEXT'] = o['TEXT']
    return r


# ⚠️ CITACAO CIRCULAR — O DEFEITO QUE ESTA MEDIDA JA TEVE.
# `SOURCES.json` e o REGISTRO DE URLs do pacote, e o passo 5 da cadeia cadastra
# nele toda fonte citada — inclusive as que ESTE passo acabou de acrescentar.
# Medindo com ele dentro, «videos que o pacote ja citava» saltou de 5 para 23:
# dezoito deles eram enderecos que eu proprio tinha acabado de por la.
#
#     MEDIR A PROPRIA ESCRITA COMO SE FOSSE ACHADO ANTERIOR NAO E MEDICAO:
#     E ECO.
#
# Medido contra o pacote intocado: 5 videos, 117.304 caracteres.
NAO_CONTA_COMO_CITACAO = {'TRANSCRIPTS.json', 'SOURCES.json',
                          'SCIENCE-CORPUS.json'}


def videos_do_pacote():
    """O que o pacote JA cita: {video_id: (id_da_atividade, [arquivos])}.

    ⚠️ A VARREDURA E DO ARQUIVO INTEIRO, NAO DE TRES CAMPOS.
    A primeira versao olhava so `URL`, `AD_URL` e `SOURCE_URL` dos registros, e
    achou 7 videos citados. A medicao por texto integral acha 245 — porque o
    endereco de video tambem aparece dentro de `PUBLIC-CHANNELS.json`, em campos
    de outro nome. Um dos que a versao estreita perdia carrega 97.710 caracteres
    de fala: mais que todos os outros somados.

        VARREDURA QUE SO OLHA ONDE ESPERA ACHAR MEDE A EXPECTATIVA, NAO O ARQUIVO.

    A LIGACAO com a atividade continua sendo por campo — ali o que importa e de
    qual registro o endereco veio, e isso o texto cru nao diz.
    """
    import glob
    from acervo_transcricoes import VID
    ativ, arqs = {}, {}
    for p in sorted(glob.glob(os.path.join(ING, '*.json'))):
        nome = os.path.basename(p)
        if nome in NAO_CONTA_COMO_CITACAO:
            continue
        try:
            with open(p, encoding='utf-8') as f:
                bruto = f.read()
        except OSError:
            continue
        for m in VID.finditer(bruto):
            arqs.setdefault(m.group(1), set()).add(nome)
        try:
            d = json.loads(bruto)
        except ValueError:
            continue
        for r in (d.get('RECORDS') or []):
            if not isinstance(r, dict) or r.get('ENTITY_TYPE') != 'COMPETITOR_ACTIVITY':
                continue
            for u in (r.get('URL'), r.get('AD_URL'), r.get('SOURCE_URL')):
                m = VID.search(str(u or ''))
                if m:
                    ativ.setdefault(m.group(1), r.get('ID'))
    return ativ, arqs


def main():
    if not os.path.isdir(ING):
        raise SystemExit('o pacote nao esta montado: rode antes scripts/v21_ingest.py')
    objs = censo()
    recs = [registro(o) for o in objs]
    ativ, arqs = videos_do_pacote()
    for r in recs:
        v = r['VIDEO_ID']
        r['CITED_IN_PACKAGE'] = v in arqs
        r['CITED_IN_PACKAGE_FILES'] = sorted(arqs.get(v) or [])
        r['SAME_VIDEO_AS_ACTIVITY_ID'] = ativ.get(v)
        r['SAME_ENTITY_LAW'] = (
            'quando preenchido, este registro e A FALA do mesmo video que aquela '
            'atividade de concorrente. Dois IDs, um video — declarado.'
        ) if r['SAME_VIDEO_AS_ACTIVITY_ID'] else None
    ped = pedidos()
    inc = [r for r in recs if r['STATE'] == 'INCLUDED']

    corpo = OrderedDict()
    corpo['COLLECTION'] = 'TRANSCRIPTS'
    corpo['FILE'] = 'TRANSCRIPTS.json'
    corpo['SCHEMA_VERSION'] = 'V2.1'
    corpo['BUILT_AT'] = '2026-09-02'
    corpo['PRIMARY_KEY'] = 'ID'
    corpo['SOURCE_OF_TRUTH'] = ('YouTube · Instagram · Spreaker — legenda de '
                                'plataforma e ASR local, por rota declarada')
    corpo['COUNT_TOTAL'] = len(recs)
    corpo['COUNT_CLIENT_SAFE'] = len(inc)
    corpo['BY_ORIGIN'] = dict(Counter(r['ORIGIN_LAYER'] for r in recs))
    corpo['BY_QA'] = dict(Counter(r['QA_STATUS'] for r in recs))
    corpo['LAW'] = ('URL DE VIDEO NAO E TRANSCRICAO. O pacote citava 245 '
                    'enderecos de video e zero falas.')
    corpo['LADDER'] = {
        'VIDEO_EXISTS': sum(1 for r in recs if r['VIDEO_EXISTS']),
        'TRANSCRIPT_EXISTS': sum(1 for r in recs if r['TRANSCRIPT_EXISTS']),
        'TRANSCRIPT_USABLE': sum(1 for r in recs if r['TRANSCRIPT_USABLE']),
        'TRANSCRIPT_INCLUDED_IN_PACKAGE': len(inc),
        'TRANSCRIPT_USED_AS_EVIDENCE': sum(
            1 for r in recs if r['TRANSCRIPT_USED_AS_EVIDENCE']),
    }
    corpo['SPEECH_CHARS'] = sum(r['CHARS'] for r in inc)
    corpo['SPEECH_CHARS_EXCLUDING_EPISODE_DESCRIPTIONS'] = sum(
        r['CHARS'] for r in inc
        if r['CAPTION_SOURCE'] != 'SPREAKER_EPISODE_DESCRIPTION')
    corpo['USABLE_EXCLUDING_EPISODE_DESCRIPTIONS'] = sum(
        1 for r in inc if r['CAPTION_SOURCE'] != 'SPREAKER_EPISODE_DESCRIPTION')
    corpo['EPISODE_DESCRIPTION_LAW'] = (
        'descricao de episodio NAO e fala transcrita. Nove registros do '
        'Spreaker trazem a descricao publicada pelo programa, e entram como '
        'texto de fonte — mas nao contam como voz falada.')
    corpo['BY_LANGUAGE'] = dict(Counter(r['SOURCE_LANGUAGE'] for r in recs))
    corpo['BY_SOURCE_COUNTRY'] = dict(Counter(r['SOURCE_COUNTRY'] for r in recs))
    corpo['BY_SOURCE_COUNTRY_ORIGIN'] = dict(
        Counter(r['SOURCE_COUNTRY_ORIGIN'] for r in recs))
    corpo['BY_FACT_COUNTRY'] = dict(Counter(r['FACT_COUNTRY'] for r in recs))
    corpo['BY_FACT_COUNTRY_ORIGIN'] = dict(
        Counter(r['FACT_COUNTRY_ORIGIN'] for r in recs))
    corpo['COUNTRY_LAW'] = (
        'LOCAL_DA_FONTE != LOCAL_DO_FATO. BY_SOURCE_COUNTRY conta o escopo da '
        'rota; BY_FACT_COUNTRY conta o que o conteudo prova. Sao numeros '
        'diferentes de proposito, e o segundo e muito menor.')
    corpo['BY_PLATFORM'] = dict(Counter(r['PLATFORM'] for r in recs))
    corpo['BY_CAPTION_SOURCE'] = dict(Counter(r['CAPTION_SOURCE'] for r in recs))
    corpo['BY_STATE'] = dict(Counter(r['STATE'] for r in recs))
    corpo['EXCLUDED_REASONS'] = dict(Counter(
        r['STATE_REASON'] for r in recs if r['STATE'] != 'INCLUDED'))
    citados = [r for r in recs if r['CITED_IN_PACKAGE']]
    corpo['CITED_IN_PACKAGE'] = len(citados)
    corpo['CITED_IN_PACKAGE_LAW'] = (
        'conta citacao em familia de conteudo. SOURCES.json fica de fora: e o '
        'registro de URLs, e o passo 5 cadastra nele as fontes que ESTE passo '
        'acrescenta — conta-lo faria a medida ecoar a propria escrita.')
    corpo['CITED_IN_PACKAGE_AND_USABLE'] = sum(
        1 for r in citados if r['STATE'] == 'INCLUDED')
    corpo['CITED_IN_PACKAGE_AND_USABLE_CHARS'] = sum(
        r['CHARS'] for r in citados if r['STATE'] == 'INCLUDED')
    corpo['SAME_VIDEO_PAIRS'] = sum(1 for r in recs if r['SAME_VIDEO_AS_ACTIVITY_ID'])
    corpo['ROUTE_REQUESTS_DECLARED'] = len(ped)
    corpo['ACERVO_SOURCES'] = sorted({r['ACERVO']['ACERVO_KEY'] for r in recs})
    corpo['LOCALIZED_FIELDS'] = ['EVIDENCE_STATUS_WHY']
    corpo['LOCALIZATION_LAW'] = (
        'a traducao fica AO LADO do original, nunca no lugar dele. TEXT e a '
        'fala da fonte e NAO se traduz: traduzir prova e adultera-la.')
    corpo['FIELD_ROLES'] = {
        'TEXT': 'RAW_ORIGINAL', 'TITLE': 'RAW_ORIGINAL',
        'CHANNEL_NAME': 'RAW_ORIGINAL', 'EVIDENCE_STATUS_WHY': 'CLIENT_NARRATIVE',
        'CROP_DECLARED_BY_THE_ROUTE': 'RAW_ORIGINAL',
        'ISSUE_DECLARED_BY_THE_ROUTE': 'RAW_ORIGINAL',
    }
    corpo['LOCALIZATION_CONTRACT'] = (
        'so CLIENT_NARRATIVE e CLIENT_LABEL pedem irmao _IT/_EN. RAW_ORIGINAL e '
        'citacao e fica na lingua publicada; CANONICAL e valor controlado e nao '
        'tem lingua.')
    corpo['RECORDS'] = recs

    p = os.path.join(ING, 'TRANSCRIPTS.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    print('== TRANSCRIPTS.json ==')
    print('  registros              : %d  (client-safe %d)' % (len(recs), len(inc)))
    print('  escada                 : %s' % corpo['LADDER'])
    print('  caracteres de fala     : %s' % f'{corpo["SPEECH_CHARS"]:,}')
    print('  sem descricao de episodio: %d objetos / %s ch' % (
        corpo['USABLE_EXCLUDING_EPISODE_DESCRIPTIONS'],
        f'{corpo["SPEECH_CHARS_EXCLUDING_EPISODE_DESCRIPTIONS"]:,}'))
    print('  ja citados pelo pacote : %d  (com fala %d, %s ch)' % (
        corpo['CITED_IN_PACKAGE'], corpo['CITED_IN_PACKAGE_AND_USABLE'],
        f'{corpo["CITED_IN_PACKAGE_AND_USABLE_CHARS"]:,}'))
    print('  gravado                : %s (%s bytes)' % (p, f'{os.path.getsize(p):,}'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
