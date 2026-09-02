#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2 · RELIGAR A PROCEDÊNCIA que já está dentro do pacote.

    python3 scripts/v21_procedencia_religar.py

O DEFEITO
---------
2.217 registros client-safe citavam `SRC_NAO_DECLARADA` como única fonte, com
`SOURCE_URLS` vazio — e exibiam ao lado, em campo de tela, o texto
«record acquisito da fonte pubblica identificata, con URL e data».

    O CARIMBO PROMETIA O QUE O REGISTRO NÃO TINHA.

O QUE A AUDITORIA NÃO MEDIU
---------------------------
Que a procedência **já estava lá**, noutro campo do mesmo registro. Recolher de
novo seria refazer trabalho feito; o que faltava era ligar.

    ANTES DE SAIR PARA A RUA, OLHE DENTRO DE CASA.

A ESCADA DE FORÇA — e ela importa
----------------------------------
1. `EMBEDDED_URL`      — o endereço do PRÓPRIO item. O mais forte: aponta para a
                         coisa, não para quem a publicou.
2. `REGISTRATION_NUMBER` — aponta para o documento (o rótulo do Ministero) de
                         onde a relação foi lida. Direto, mas herdado.
3. `LEGACY_SOURCE_ID`  — aponta só para o EDITOR, não para o item. O mais fraco,
                         e o registro tem de dizer isso: saber que a frase veio
                         do YouTube não é saber de que vídeo.

    APONTAR PARA O EDITOR NÃO É APONTAR PARA O DOCUMENTO.

O QUE ESTE ARQUIVO NÃO FAZ
--------------------------
Não inventa SOURCE_ID. Não coleta nada. Não promove QA. Quando não há caminho, o
registro fica `UNRECOVERABLE` — visível, contado, e com o carimbo corrigido para
dizer a verdade em vez da promessa.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
SENTINELAS = ('SRC_NAO_DECLARADA', 'SRC_DESCONHECIDA')

# Campos que carregam o endereço do próprio item, em ordem de preferência.
# ⚠️ ORCID NAO ENTRA. Um ORCID identifica uma PESSOA, nao um documento — usa-lo
# como endereco de fonte criava a fonte inexistente SRC_ORCID_ORG em 54
# registros de pesquisador, e dizia que a procedencia era o proprio pesquisador.
#
#     O IDENTIFICADOR DE QUEM ESCREVEU NAO E O ENDERECO DO QUE FOI ESCRITO.
CAMPOS_URL = ('AD_URL', 'URL', 'LABEL_URL', 'PUBLIC_CATALOG_URL', 'OPENALEX_ID')

# O texto que o registro mostra na tela quando a procedência é herdada ou fraca.
# Ele substitui a promessa antiga, que dizia «com URL e data» sem ter nem uma nem
# outra.
# Campos que carregam a data do proprio item, em ordem de preferencia. A data,
# como a URL, ja estava dentro do registro: 414 anuncios traziam START_DATE e
# REFERENCE_DATE nulo ao lado de um carimbo que prometia data.
CAMPOS_DATA = ('PUBLICATION_DATE', 'DATE', 'START_DATE', 'PUBLISHED_AT',
               'AD_DELIVERY_START_TIME')

CARIMBO = {
    'EMBEDDED_URL': 'registro capturado de fonte publica identificada, com URL e data.',
    # Sem data declarada o carimbo NAO pode dizer "com data". Muda-se a
    # afirmacao, nunca a evidencia.
    'EMBEDDED_URL_SEM_DATA': (
        'registro capturado de fonte publica identificada, com URL. A fonte nao '
        'declara data de publicacao para este item.'),
    'REGISTRATION_NUMBER': (
        'fato lido no rotulo oficial do produto. A URL e a data vem do registro '
        'regulatorio citado por este mesmo registro, nao de leitura propria.'),
    'LEGACY_SOURCE_ID': (
        'a fonte publicadora esta identificada, mas o endereco do item nao. '
        'Sabe-se onde foi publicado; nao se sabe qual item exatamente.'),
    'UNRECOVERABLE': (
        'este registro NAO declarou a sua origem, e a origem nao foi encontrada '
        'em nenhum outro campo. Nao ha link para mostrar. A tela mostra este '
        'aviso, nunca um endereco.'),
}
FORCA = {'EMBEDDED_URL': 'DIRETA', 'EMBEDDED_URL_SEM_DATA': 'DIRETA_SEM_DATA',
         'REGISTRATION_NUMBER': 'HERDADA',
         'LEGACY_SOURCE_ID': 'SO_O_EDITOR', 'UNRECOVERABLE': 'NENHUMA'}


def _primeira_url(v):
    """A URL dentro de um campo que virou prosa.

    Cinco registros do ISTAT trazem SOURCE_URLS com texto do tipo
    «dados: https://... | rotulos de cultura: https://...». O campo esta
    preenchido, entao o religamento os pulava; mas o SOURCE_ID continuava a
    sentinela. Campo preenchido nao e campo declarado.
    """
    m = re.search(r'https?://\S+', str(v or ''))
    return m.group(0).rstrip('|,; ') if m else None


# As frases que prometem data. Cada uma tem a sua versao sem-data ao lado: a
# correcao nunca inventa texto novo para um caso que ja tinha frase.
PROMESSA_DE_DATA = ('com URL e data', 'com fonte e data')
SEM_DATA = {
    'registro capturado de fonte publica identificada, com URL e data.':
        ('registro capturado de fonte publica identificada, com URL. A fonte nao '
         'declara data de publicacao para este item.'),
    'fato lido em documento oficial, com fonte e data. A proveniencia foi '
    'estabelecida no handoff anterior e e traduzida, nao rebaixada.':
        ('fato lido em documento oficial, com fonte identificada. O documento nao '
         'declara data, e a proveniencia vem do handoff anterior — traduzida, nao '
         'rebaixada.'),
}


def _host_id(u):
    m = re.match(r'https?://([^/]+)', str(u or ''))
    if not m:
        return None
    h = m.group(1).lower().replace('www.', '')
    return 'SRC_' + re.sub(r'[^A-Z0-9]+', '_', h.upper()).strip('_')[:40]


def colecoes():
    for a in sorted(os.listdir(ING)):
        if not a.endswith('.json') or a in ('APP-MANIFEST.json',
                                            'CANONICAL-INTELLIGENCE-MASTER.json'):
            continue
        p = os.path.join(ING, a)
        d = json.load(open(p, encoding='utf-8'))
        if isinstance(d, dict) and isinstance(d.get('RECORDS'), list):
            yield a, p, d


def main():
    fontes = json.load(open(os.path.join(ING, 'SOURCES.json'), encoding='utf-8'))
    idx = {}
    for r in fontes['RECORDS']:
        for k in [r.get('ID'), r.get('ID_ANTERIOR')] + list(r.get('ID_ALIASES') or []):
            if k:
                idx.setdefault(k, r)

    reg = {}
    pr = os.path.join(ING, 'PRODUCTS-REGULATORY.json')
    if os.path.exists(pr):
        for r in json.load(open(pr, encoding='utf-8'))['RECORDS']:
            k = re.sub(r'\D', '', str(r.get('REGISTRATION_NUMBER') or ''))
            if k:
                reg[k.lstrip('0').zfill(6)] = r

    cont = {k: 0 for k in CARIMBO}
    antes = depois = 0
    irrecuperaveis = []

    for arq, caminho, d in colecoes():
        mudou = False
        for r in d['RECORDS']:
            sent = (r.get('SOURCE_IDS') or []) and all(
                s in SENTINELAS for s in r['SOURCE_IDS'])
            if not sent:
                continue
            antes += 1
            via = url = alvo = None

            # 1 · o endereço do próprio item
            for c in CAMPOS_URL:
                v = r.get(c)
                if isinstance(v, str) and v.startswith('http'):
                    via, url = 'EMBEDDED_URL', v
                    break
            # 1b · a URL que existe, mas dentro de prosa
            if not via:
                for v in (r.get('SOURCE_URLS') or []):
                    u = _primeira_url(v)
                    if u:
                        via, url = 'EMBEDDED_URL', u
                        break
            # 2 · o rótulo de onde a relação foi lida
            if not via and r.get('REGISTRATION_NUMBER'):
                k = re.sub(r'\D', '', str(r['REGISTRATION_NUMBER']))
                alvo = reg.get(k.lstrip('0').zfill(6)) if k else None
                if alvo and alvo.get('SOURCE_URLS'):
                    via, url = 'REGISTRATION_NUMBER', alvo['SOURCE_URLS'][0]
            # 3 · só o editor
            if not via and r.get('SOURCE_ID') and idx.get(r['SOURCE_ID']):
                f = idx[r['SOURCE_ID']]
                if f.get('URL') or f.get('SOURCE_URLS'):
                    via = 'LEGACY_SOURCE_ID'
                    url = f.get('URL') or f['SOURCE_URLS'][0]

            if via:
                sid = (alvo.get('SOURCE_IDS') or [None])[0] if via == 'REGISTRATION_NUMBER' else None
                sid = sid or (idx[r['SOURCE_ID']]['ID'] if via == 'LEGACY_SOURCE_ID' else None)
                sid = sid or _host_id(url)
                if sid and sid not in idx and via != 'EMBEDDED_URL':
                    # nunca cadastrar fonte que nao existe por caminho fraco
                    via = None
            if via:
                r['SOURCE_IDS'] = [sid]
                # A URL do EDITOR nao e a URL do item: nao entra em SOURCE_URLS.
                if via != 'LEGACY_SOURCE_ID':
                    r['SOURCE_URLS'] = [url]
                    if not r.get('REFERENCE_DATE'):
                        # a data tambem ja estava dentro do registro
                        for c in CAMPOS_DATA:
                            if r.get(c):
                                r['REFERENCE_DATE'] = r[c]
                                r['REFERENCE_DATE_RECOVERED_FROM'] = c
                                break
                    if not r.get('REFERENCE_DATE') and alvo:
                        r['REFERENCE_DATE'] = alvo.get('REFERENCE_DATE')
                    if via == 'EMBEDDED_URL' and not r.get('REFERENCE_DATE'):
                        via = 'EMBEDDED_URL_SEM_DATA'
                else:
                    r['PROVENANCE_PUBLISHER_URL'] = url
                r['PROVENANCE_STATE'] = 'RECOVERED'
                r['PROVENANCE_RECOVERED_VIA'] = via
                r['PROVENANCE_STRENGTH'] = FORCA[via]
                if alvo:
                    r['PROVENANCE_RECOVERED_FROM'] = alvo.get('ID')
                r['EVIDENCE_STATUS_WHY'] = CARIMBO[via]
                depois += 1
            else:
                via = 'UNRECOVERABLE'
                r['PROVENANCE_STATE'] = 'UNRECOVERABLE'
                r['PROVENANCE_STRENGTH'] = FORCA[via]
                r['EVIDENCE_STATUS_WHY'] = CARIMBO[via]
                irrecuperaveis.append(f"{arq}:{r.get('ID')}")
            # o texto mudou: as traducoes antigas nao valem mais
            for suf in ('_IT', '_EN', '_ORIGINAL_RESEARCH_TEXT'):
                r.pop('EVIDENCE_STATUS_WHY' + suf, None)
            cont[via] += 1
            mudou = True

        # ── 2a passada · o carimbo que promete data sem ter data ────────────
        # Nem todo registro que promete demais e sentinela. Um registro pode ter
        # fonte e URL de verdade, nao ter data nenhuma, e ainda assim mostrar na
        # tela «com URL e data». A evidencia esta certa; a frase e que passou do
        # ponto.
        #
        #     QUANDO A EVIDENCIA NAO ALCANCA A FRASE, MUDA-SE A FRASE.
        for r in d['RECORDS']:
            if r.get('PROVENANCE_STATE'):
                continue
            texto = str(r.get('EVIDENCE_STATUS_WHY') or '')
            if not any(p in texto for p in PROMESSA_DE_DATA):
                continue
            if r.get('REFERENCE_DATE') not in (None, ''):
                continue
            for c in CAMPOS_DATA:
                if r.get(c):
                    r['REFERENCE_DATE'] = r[c]
                    r['REFERENCE_DATE_RECOVERED_FROM'] = c
                    break
            if r.get('REFERENCE_DATE') not in (None, ''):
                cont['DATA_RECUPERADA'] = cont.get('DATA_RECUPERADA', 0) + 1
            else:
                r['EVIDENCE_STATUS_WHY'] = SEM_DATA.get(
                    texto, CARIMBO['EMBEDDED_URL_SEM_DATA'])
                r['PROVENANCE_STATE'] = 'SOURCE_OK_NO_DATE'
                for suf in ('_IT', '_EN', '_ORIGINAL_RESEARCH_TEXT'):
                    r.pop('EVIDENCE_STATUS_WHY' + suf, None)
                cont['CARIMBO_SEM_DATA'] = cont.get('CARIMBO_SEM_DATA', 0) + 1
            mudou = True
        if mudou:
            json.dump(d, open(caminho, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)

    print('== R2 · RELIGAR PROCEDENCIA ==')
    print(f'  sentinelas antes  : {antes}')
    print(f'  religados         : {depois}')
    for k in ('EMBEDDED_URL', 'REGISTRATION_NUMBER', 'LEGACY_SOURCE_ID', 'UNRECOVERABLE'):
        print(f'    {k:22s}: {cont[k]}  ({FORCA[k]})')
    print(f'  irrecuperaveis    : {len(irrecuperaveis)}  {irrecuperaveis[:8]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
