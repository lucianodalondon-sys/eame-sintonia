#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AS TRANSCRIÇÕES DO ACERVO — lidas, normalizadas e CONTADAS, uma a uma.

    python3 scripts/acervo_transcricoes.py          # censo na tela

    from acervo_transcricoes import censo
    objs = censo()

A ESCADA QUE NÃO SE PODE SUBIR SOZINHA
--------------------------------------
Cinco condições, e nenhuma implica a seguinte:

    VIDEO_EXISTS                 existe o objeto de vídeo
    TRANSCRIPT_EXISTS            alguém pediu a fala e a rota respondeu
    TRANSCRIPT_USABLE            veio texto, e não string vazia
    TRANSCRIPT_INCLUDED_IN_PACKAGE   o pacote carrega os bytes
    TRANSCRIPT_USED_AS_EVIDENCE      um cartão apoia afirmação nesses bytes

URL DE VÍDEO NÃO É TRANSCRIÇÃO. Um pacote que cita 245 URLs de vídeo e zero
falas tem 245 endereços, não 245 depoimentos.

O QUE ESTE ARQUIVO NÃO FAZ
--------------------------
Não resume, não traduz, não interpreta. O texto que entra é o texto que a rota
devolveu, e o SHA256 do texto é gravado para que a pergunta «quais bytes
sustentam esta evidência?» tenha resposta exata, e não aproximada.

    RESUMO DE LLM NÃO SUBSTITUI FALA. O RESUMO É LEITURA; A FALA É PROVA.

E o país NÃO se deduz da tela que vai consumir. `CROP_DECLARED_BY_THE_ROUTE` é
termo de BUSCA, não conteúdo provado — entra com esse nome, e nunca como CROP.
"""
import json
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acervo_fonte import carimbo, ler, manifesto, sha256_texto  # noqa: E402

# ⚠️ DUAS FALHAS LATENTES, FECHADAS ANTES DE FICAREM VIVAS.
#
# A versão anterior era `youtube.com/watch\?v=…`, e com isso:
#   · perdia `watch?list=PL…&v=ID` — o `v` fora da primeira posição, que é
#     exactamente como o YouTube escreve o link de um vídeo dentro de playlist;
#   · casava `https://exemplo.com/youtube.com/watch?v=ID`, porque não exigia o
#     host — um endereço de outro sítio que só CONTÉM a string.
#
# Medido no acervo e no pacote de hoje: zero perdidas, zero falsos. Ou seja, as
# duas falhas eram LATENTES. Fechadas assim mesmo:
#
#     A JUNÇÃO QUE ERRA SÓ ÀS VEZES É A PIOR DE AUDITAR.
#     Quando ela erra, o objeto some — e sumir não acende nada.
VID = re.compile(
    r'https?://(?:[\w-]+\.)*(?:youtube\.com|youtube-nocookie\.com|youtu\.be)'
    r'(?:/watch\?(?:[^"\s]*&)?v=|/shorts/|/embed/|/live/|/v/|/)'
    r'([A-Za-z0-9_-]{11})(?![A-Za-z0-9_-])')

# Estados de exclusão que o PRÓPRIO acervo declara. Nenhum é inventado aqui:
# quando a rota disse por que não trouxe fala, essa razão é transportada.
RAZAO_ACERVO = {
    'NAO_OBTIDA': 'a rota nao devolveu legenda para este objeto',
    'REQUESTED_EMPTY': 'a rota respondeu, e o texto veio vazio',
    'EMPTY': 'a rota respondeu, e o texto veio vazio',
}


# O acervo escreve `NÃO SEI` quando NÃO SABE. Sete caracteres de honestidade —
# e sete caracteres que um contador ingênuo soma como se fossem fala. Em
# IT-VIDEO-V1.json isso são 84 objetos e 588 «caracteres de fala» que ninguém
# falou.
#
#     UNKNOWN NÃO É TEXTO CURTO. É AUSÊNCIA DECLARADA.
SENTINELA = re.compile(r'^(n[aã]o\s*sei|unknown|none|null|n/?a|not[_\s]known|'
                       r'sem\s+texto|vazio)[\s.·-]*$', re.I)
# E a sentinela COM RAZÃO: «NÃO SEI — a rota nao declara o idioma da legenda».
# Continua sendo desconhecimento; a razão é preservada ao lado, não descartada.
SENTINELA_COM_RAZAO = re.compile(r'^(n[aã]o\s*sei|unknown|not[_\s]known)\b\s*[—\-:·]',
                                 re.I)


def _e_sentinela(v):
    v = (v or '').strip()
    return bool(v) and bool(SENTINELA.match(v) or SENTINELA_COM_RAZAO.match(v))

# Rótulos de país que o acervo usa, e o que cada um realmente diz.
PAIS = {'ITALY': 'IT', 'ITALIA': 'IT', 'IT': 'IT', 'ES': 'ES', 'SPAIN': 'ES',
        'FR': 'FR', 'FRANCE': 'FR'}


def _pais(v):
    """País do FATO. Ponteiro («ver outro arquivo») não é país: é UNKNOWN."""
    v = (v or '').strip()
    if not v or len(v) > 24 or _e_sentinela(v) or v.upper() == 'NOT_KNOWN':
        return 'UNKNOWN'
    return PAIS.get(v.upper(), 'UNKNOWN')


def _texto(v):
    """O texto, ou vazio. Sentinela de desconhecimento NÃO é texto."""
    v = (v or '')
    return '' if _e_sentinela(v) else v


def _vid(u):
    m = VID.search(str(u or ''))
    return m.group(1) if m else None


def _lang(v):
    """Língua declarada. `NÃO SEI` do acervo vira UNKNOWN, e continua UNKNOWN."""
    v = (v or '').strip()
    return 'UNKNOWN' if (not v or _e_sentinela(v)) else v.lower()[:8]


def _obj(**kw):
    """O envelope de UMA transcrição. Campo ausente é UNKNOWN, nunca vazio mudo."""
    o = OrderedDict()
    o['TRANSCRIPT_ID'] = kw['tid']
    o['VIDEO_ID'] = kw.get('vid') or 'UNKNOWN'
    o['PLATFORM'] = kw.get('platform') or 'UNKNOWN'
    o['SOURCE_URL'] = kw.get('url') or None
    o['TITLE'] = kw.get('title') or 'UNKNOWN'
    o['CHANNEL_NAME'] = kw.get('channel') or 'UNKNOWN'
    o['CHANNEL_ID'] = kw.get('channel_id') or 'UNKNOWN'
    o['PUBLICATION_DATE'] = kw.get('pub') or None
    o['DURATION_S'] = kw.get('dur')
    # ⚠️ LOCAL_DA_FONTE != LOCAL_DO_FATO — a lei que veio do Brasil, em
    # scripts/lugar_do_fato.py. O que a ROTA declara sobre si mesma («este é um
    # corpus italiano») é o escopo dela, não o lugar onde o fato aconteceu.
    #
    #     UM VÍDEO PUBLICADO POR UMA ORGANIZAÇÃO DE MILÃO NÃO PROVA
    #     QUE O FATO ACONTECEU EM MILÃO.
    #
    # `SOURCE_COUNTRY` guarda o escopo da rota, com origem DA_FONTE — que a lei
    # recusa como sustentação de fato. `FACT_COUNTRY` só nasce de ESCRITO/CITADO,
    # com a frase de evidência ao lado, e é UNKNOWN quando não há.
    o['SOURCE_COUNTRY'] = _pais(kw.get('country'))
    o['SOURCE_COUNTRY_DECLARED'] = kw.get('country') or None
    o['SOURCE_COUNTRY_ORIGIN'] = 'DA_FONTE' if o['SOURCE_COUNTRY'] != 'UNKNOWN' else 'NAO_SEI'
    o['COLLECTION_COUNTRY'] = kw.get('coleta') or 'UNKNOWN'
    o['FACT_COUNTRY'] = 'UNKNOWN'
    o['FACT_COUNTRY_ORIGIN'] = 'NAO_SEI'
    o['FACT_COUNTRY_EVIDENCE'] = None
    o['FACT_LOCATION_LAW'] = (
        'LOCAL_DA_FONTE != LOCAL_DO_FATO. SOURCE_COUNTRY e o escopo declarado '
        'pela rota (origem DA_FONTE, que a lei recusa como prova de fato). '
        'FACT_COUNTRY so nasce de ESCRITO/CITADO no proprio conteudo.')
    o['SOURCE_LANGUAGE'] = _lang(kw.get('lang'))
    o['SOURCE_LANGUAGE_DECLARED'] = kw.get('lang') or None
    o['CASE_ID'] = kw.get('case_id') or 'UNKNOWN'
    o['CASE_COUNTRY'] = kw.get('case_country') or 'UNKNOWN'
    o['CASE_LANGUAGE'] = kw.get('case_language') or 'UNKNOWN'
    o['CROP_DECLARED_BY_THE_ROUTE'] = kw.get('crop_q') or None
    o['ISSUE_DECLARED_BY_THE_ROUTE'] = kw.get('issue_q') or None
    o['REGION_NAMED'] = kw.get('region') or None
    o['CAPTION_SOURCE'] = kw.get('cap') or 'UNKNOWN'
    o['COLLECTION_ID'] = kw.get('run') or 'UNKNOWN'
    o['OBSERVED_AT'] = kw.get('at') or None
    txt = _texto(kw.get('text'))
    o['CHARS'] = len(txt)
    o['TEXT_SHA256'] = sha256_texto(txt) if txt else None
    o['VIDEO_EXISTS'] = True
    o['TRANSCRIPT_EXISTS'] = kw.get('exists', bool(kw.get('requested', True)))
    o['TRANSCRIPT_USABLE'] = len(txt) > 0
    o['TRANSCRIPT_QUALITY'] = (
        'NO_TEXT' if not txt else 'SHORT' if len(txt) < 200 else 'FULL')
    o['STATE'] = 'INCLUDED' if txt else 'EXCLUDED'
    o['STATE_REASON'] = (
        'texto de fala presente e nao vazio' if txt else
        RAZAO_ACERVO.get(str(kw.get('why') or '').upper(),
                         kw.get('why') or
                         ('o campo de fala traz sentinela de desconhecimento, '
                          'nao texto' if (kw.get('text') or '') else
                          'o acervo nao declara razao')))
    o['ACERVO'] = kw['carimbo']
    o['TEXT'] = txt
    return o


# ── as rotas, uma função por forma de arquivo ────────────────────────────────
def _fala_convegno(d, c, tid):
    return _obj(tid=tid, vid=d.get('EXTERNAL_ID') or _vid(d.get('URL')),
                platform=d.get('PLATFORM'), url=d.get('URL'), title=d.get('TITLE'),
                channel=d.get('CHANNEL_NAME'), channel_id=d.get('CHANNEL_ID'),
                pub=d.get('PUBLICATION_DATE'), dur=d.get('DURATION_S'),
                country='IT', coleta='IT', lang=d.get('TRANSCRIPT_LANGUAGE'),
                crop_q=d.get('CROP_DECLARED_BY_THE_ROUTE') or d.get('CROP'),
                issue_q=d.get('ISSUE_DECLARED_BY_THE_ROUTE') or d.get('TARGET'),
                region=d.get('REGION_NAMED'), cap=d.get('CAPTION_SOURCE'),
                run=d.get('SOURCE_ID'), at=d.get('CAPTURED_AT'),
                text=d.get('TRANSCRIPT') or '', carimbo=c)


def _item_inline(x, c, tid, pais, plataforma=None):
    txt = x.get('TRANSCRIPT') or ''
    est = str(x.get('TRANSCRIPT_STATE') or '').upper()
    return _obj(tid=tid, vid=x.get('EXTERNAL_ID') or x.get('SHORTCODE')
                or x.get('EPISODE_ID') or _vid(x.get('URL')),
                platform=plataforma or x.get('PLATFORM'),
                url=x.get('URL') or x.get('AUDIO_URL') or x.get('PAGE_URL'),
                title=x.get('TITLE'),
                channel=x.get('CHANNEL_NAME') or x.get('HANDLE')
                or x.get('AUTHOR') or x.get('ORGANISATION'),
                channel_id=x.get('CHANNEL_ID') or x.get('SHOW_ID'),
                pub=x.get('PUBLICATION_DATE') or x.get('PUBLISHED_AT'),
                dur=x.get('DURATION_S') or x.get('VIDEO_DURATION_S'),
                country=x.get('COUNTRY') or pais, coleta=pais,
                lang=x.get('TRANSCRIPT_LANGUAGE') or x.get('ORIGINAL_LANGUAGE'),
                crop_q=x.get('CROP_FROM_DESCRIPTION') or x.get('CROP'),
                issue_q=x.get('ISSUE_FROM_DESCRIPTION') or x.get('TARGET'),
                region=x.get('REGION_DECLARED'),
                cap=x.get('CAPTION_SOURCE') or x.get('TRANSCRIPT_ENGINE'),
                run=x.get('RUN_ID'), at=x.get('COLLECTION_DATE'),
                text=txt, why=est or None, carimbo=c)


def _item_sensor(x, c, tid, cab):
    txt = x.get('TRANSCRIPT') or ''
    return _obj(tid=tid, vid=_vid(x.get('SOURCE_URL')),
                platform='YOUTUBE', url=x.get('SOURCE_URL'),
                country=cab.get('FACT_LOCATION'),
                coleta=_pais(cab.get('SOURCE_LOCATION')),
                lang=x.get('TRANSCRIPT_LANGUAGE'),
                cap=x.get('CAPTION_SOURCE'),
                run=x.get('COLLECTION_RUN_ID') or x.get('BATCH_ID'),
                at=x.get('CAPTURED_AT'), text=txt,
                why=x.get('WHY_EMPTY') or x.get('TRANSCRIPT_AVAILABLE'),
                carimbo=c)


def _item_es(x, c, tid, cab):
    txt = x.get('TRANSCRIPT_ORIGINAL') or ''
    return _obj(tid=tid, vid=x.get('EXTERNAL_ID') or _vid(x.get('URL')),
                platform=x.get('PLATFORM'), url=x.get('URL'), title=x.get('TITLE'),
                channel=x.get('CHANNEL_NAME'), channel_id=x.get('ORIGIN_ID'),
                pub=x.get('PUBLICATION_DATE'), country=cab.get('FACT_LOCATION'),
                coleta='ES',
                lang=x.get('TRANSCRIPT_LANGUAGE'), cap=x.get('CAPTION_SOURCE'),
                run=x.get('RUN_ID'), at=cab.get('captured_at'),
                text=txt, carimbo=c)


def _tid(plataforma, vid, n):
    """ID determinístico: mesma entrada, mesmo ID. Sem contador global."""
    base = re.sub(r'[^A-Za-z0-9_-]+', '_', str(vid or ('SEQ%04d' % n)))
    return 'IT-TRX-%s-%s' % ((plataforma or 'UNK')[:3].upper(), base[:32])


def enriquecimento():
    """{video_id: metadados} — título, canal, país do fato e CASE_ID.

    ⚠️ SÓ METADADO. `MEDICAO.json` e `ES-T8-001-videos.json` também têm campo
    `TRANSCRIPT`, e lê-lo aqui contaria a mesma fala duas vezes — uma pelo lote
    de transcrição, outra pelo arquivo de enriquecimento.

        O ARQUIVO QUE SABE MAIS SOBRE O MESMO OBJETO NÃO É OUTRO OBJETO.

    `CROP` e `ISSUE` daqui vêm da busca, e viajam com esse nome: o próprio
    acervo declara a base em `CROP_ISSUE_BASIS`.
    """
    fontes = {s['KEY']: s for s in manifesto()['SOURCES']}
    idx = {}
    for s in sorted((s for s in fontes.values() if s['ROLE'] == 'ENRICHMENT'),
                    key=lambda s: s['PATH']):
        d = ler(s['KEY'], fontes)
        itens = []
        for k, v in d.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                itens.extend(v)
        for x in itens:
            vid = x.get('EXTERNAL_ID') or x.get('CONTENT_ID') or _vid(
                x.get('SOURCE_URL') or x.get('URL'))
            if not vid or _e_sentinela(vid) or vid in idx:
                continue
            idx[vid] = {
                'TITLE': x.get('TITLE'),
                'CHANNEL': x.get('CHANNEL') or x.get('CHANNEL_NAME'),
                'CHANNEL_ID': x.get('CHANNEL_URL') or x.get('CHANNEL_ID')
                or x.get('ORIGIN_ID'),
                'COUNTRY': x.get('COUNTRY_OF_FACT') or x.get('FACT_LOCATION')
                or x.get('COUNTRY'),
                'COUNTRY_EVIDENCE': x.get('COUNTRY_OF_FACT_EVIDENCE')
                or x.get('FACT_LOCATION_RULE'),
                'CASE_ID': x.get('CASE_ID'),
                'PUB': x.get('PUBLISHED_AT') or x.get('PUBLICATION_DATE'),
                'DUR': x.get('DURATION'),
                'CROP_Q': x.get('CROP'),
                'ISSUE_Q': x.get('ISSUE'),
                'CROP_ISSUE_BASIS': x.get('CROP_ISSUE_BASIS'),
                'LANG': x.get('LANGUAGE') or x.get('TRANSCRIPT_LANGUAGE'),
                'REGION': x.get('REGION_OF_FACT'),
                'FROM': s['PATH'],
            }
    return idx


def _aplica(o, e):
    """O enriquecimento PREENCHE o que está UNKNOWN. Nunca sobrescreve o que a
    própria rota da transcrição declarou — a rota que trouxe a fala está mais
    perto dela."""
    if not e:
        return o
    o['ENRICHED_FROM'] = e['FROM']
    if o['TITLE'] == 'UNKNOWN' and e.get('TITLE') and not _e_sentinela(e['TITLE']):
        o['TITLE'] = e['TITLE']
    if o['CHANNEL_NAME'] == 'UNKNOWN' and e.get('CHANNEL') \
            and not _e_sentinela(e['CHANNEL']):
        o['CHANNEL_NAME'] = e['CHANNEL']
    if o['CHANNEL_ID'] == 'UNKNOWN' and e.get('CHANNEL_ID'):
        o['CHANNEL_ID'] = e['CHANNEL_ID']
    if not o['PUBLICATION_DATE'] and e.get('PUB') and not _e_sentinela(e['PUB']):
        o['PUBLICATION_DATE'] = e['PUB']
    # ⚠️ O FATO NAO E PREENCHIDO «SO SE ESTIVER VAZIO».
    # A versao anterior so olhava o enriquecimento quando SOURCE_COUNTRY estava
    # UNKNOWN — e como a rota ja tinha carimbado «IT» em 126 registros, a
    # evidencia real (a frase «o texto nomeia "veneto"») era SOMBREADA pelo
    # carimbo da rota, que e justamente o que a lei recusa.
    #
    #     O PALPITE QUE CHEGA PRIMEIRO NAO PODE TRANCAR A PROVA QUE CHEGA DEPOIS.
    ev = e.get('COUNTRY_EVIDENCE')
    pais_fato = _pais(e.get('COUNTRY'))
    escrito = bool(ev) and (
        'nomeia' in str(ev).lower() or str(ev).upper() == 'NOMEADO_NO_TEXTO')
    if pais_fato != 'UNKNOWN' and escrito:
        o['FACT_COUNTRY'] = pais_fato
        o['FACT_COUNTRY_ORIGIN'] = 'ESCRITO'
        o['FACT_COUNTRY_EVIDENCE'] = ev
    elif ev:
        o['FACT_COUNTRY_EVIDENCE'] = ev      # a razao da ausencia tambem e prova
    if o['SOURCE_COUNTRY'] == 'UNKNOWN' and pais_fato != 'UNKNOWN':
        o['SOURCE_COUNTRY'] = pais_fato
        o['SOURCE_COUNTRY_ORIGIN'] = 'ESCRITO' if escrito else 'DA_FONTE'
        o['SOURCE_COUNTRY_DECLARED'] = o['SOURCE_COUNTRY_DECLARED'] or e.get('COUNTRY')
    if o['SOURCE_LANGUAGE'] == 'UNKNOWN' and e.get('LANG'):
        o['SOURCE_LANGUAGE'] = _lang(e['LANG'])
    if o['CASE_ID'] == 'UNKNOWN' and e.get('CASE_ID') and not _e_sentinela(e['CASE_ID']):
        o['CASE_ID'] = e['CASE_ID']
        # O CASE_ID nomeia o pais do caso na propria chave: ES-OLIVE-REPILO.
        pref = str(e['CASE_ID']).split('-')[0].upper()
        o['CASE_COUNTRY'] = pref if pref in ('IT', 'ES', 'FR') else 'UNKNOWN'
    if not o['CROP_DECLARED_BY_THE_ROUTE'] and e.get('CROP_Q'):
        o['CROP_DECLARED_BY_THE_ROUTE'] = e['CROP_Q']
    if not o['ISSUE_DECLARED_BY_THE_ROUTE'] and e.get('ISSUE_Q'):
        o['ISSUE_DECLARED_BY_THE_ROUTE'] = e['ISSUE_Q']
    if e.get('CROP_ISSUE_BASIS'):
        o['CROP_ISSUE_BASIS'] = e['CROP_ISSUE_BASIS']
    if not o['REGION_NAMED'] and e.get('REGION') and not _e_sentinela(e['REGION']):
        o['REGION_NAMED'] = e['REGION']
    return o


def censo():
    """Todas as transcrições do acervo, normalizadas. Ordem determinística."""
    fontes = {s['KEY']: s for s in manifesto()['SOURCES']}
    enr = enriquecimento()
    out, n = [], 0

    for s in sorted((s for s in fontes.values() if s['FAMILY'] == 'TRANSCRIPTS'),
                    key=lambda s: s['PATH']):
        c = carimbo(s['KEY'], fontes)
        d = ler(s['KEY'], fontes)
        p = s['PATH']
        n += 1

        if s['ROLE'] == 'ENRICHMENT':
            continue          # só metadado, e já foi lido em enriquecimento()
        if s['ROLE'] == 'FALA':
            o = _fala_convegno(d, c, _tid(d.get('PLATFORM'),
                                          d.get('EXTERNAL_ID') or _vid(d.get('URL')), n))
            out.append(o)
        elif 'IT-INSTAGRAM' in p:
            for i, x in enumerate(d.get('ITEMS') or []):
                out.append(_item_inline(x, c, _tid('INSTAGRAM',
                                                   x.get('SHORTCODE'), n * 100 + i),
                                        'IT', 'INSTAGRAM'))
        elif 'IT-VOZ-AUDIO' in p:
            for i, x in enumerate(d.get('RECORDS') or []):
                out.append(_item_inline(x, c, _tid('AUDIO',
                                                   x.get('EXTERNAL_ID') or
                                                   x.get('EPISODE_ID'), n * 100 + i),
                                        'IT', x.get('PLATFORM') or 'AUDIO'))
        elif 'SENSOR-PILOT' in p:
            for i, x in enumerate(d.get('ITEMS') or []):
                out.append(_item_sensor(x, c, _tid('YOUTUBE',
                                                   _vid(x.get('SOURCE_URL')),
                                                   n * 100 + i), d))
        elif 'ES-T8-001' in p:
            for i, x in enumerate(d.get('TRANSCRIPTS') or []):
                out.append(_item_es(x, c, _tid('YOUTUBE', x.get('EXTERNAL_ID'),
                                               n * 100 + i), d))
        # ROLE == MANIFEST: é CENSO da rota, não conteúdo. Entra em `pedidos()`.

    out = [_aplica(o, enr.get(o['VIDEO_ID'])) for o in out]
    # a mesma fala pode ter sido colhida duas vezes; o objeto é o VÍDEO.
    return _dedup(out)


def _dedup(objs):
    """Um vídeo, um objeto. Duas colheitas do mesmo vídeo NÃO são dois depoimentos.

    Vence a colheita com mais texto — e a perdedora fica registrada em
    `ALSO_COLLECTED_BY`, para que nenhuma coleta desapareça sem estado.
    """
    por = OrderedDict()
    for o in sorted(objs, key=lambda o: (o['VIDEO_ID'], -o['CHARS'],
                                         o['ACERVO']['ACERVO_PATH'])):
        k = o['VIDEO_ID']
        if k == 'UNKNOWN':
            por['%s::%s' % (k, o['TRANSCRIPT_ID'])] = o
            continue
        if k in por:
            por[k].setdefault('ALSO_COLLECTED_BY', []).append({
                'ACERVO_PATH': o['ACERVO']['ACERVO_PATH'],
                'CHARS': o['CHARS'], 'TEXT_SHA256': o['TEXT_SHA256'],
                'WHY_NOT_CHOSEN': 'colheita com menos texto do mesmo video',
            })
            continue
        por[k] = o
    return sorted(por.values(), key=lambda o: o['TRANSCRIPT_ID'])


def pedidos():
    """O que a rota PEDIU — inclusive o que não voltou. Fecha a contabilidade."""
    fontes = {s['KEY']: s for s in manifesto()['SOURCES']}
    out = []
    for s in sorted((s for s in fontes.values()
                     if s['FAMILY'] == 'TRANSCRIPTS' and s['ROLE'] == 'MANIFEST'),
                    key=lambda s: s['PATH']):
        d = ler(s['KEY'], fontes)
        for x in (d.get('ITEMS') or []):
            x = {k.upper(): v for k, v in x.items()}
            out.append({
                'VIDEO_ID': x.get('EXTERNAL_ID') or _vid(x.get('URL')) or 'UNKNOWN',
                'URL': x.get('URL'), 'TITLE': x.get('TITLE'),
                'STATE': x.get('STATE') or (
                    'OK' if (x.get('SPOKEN_TEXT_AVAILABLE') or
                             x.get('TRANSCRIPT_LENGTH')) else 'UNKNOWN'),
                'WHY': x.get('WHY'),
                'CHARS_DECLARED': x.get('CHARS') or x.get('SPOKEN_TEXT_CHARS')
                or x.get('TRANSCRIPT_LENGTH') or 0,
                'ACERVO_PATH': s['PATH'],
            })
    return out


def main():
    objs = censo()
    ped = pedidos()
    inc = [o for o in objs if o['STATE'] == 'INCLUDED']
    exc = [o for o in objs if o['STATE'] != 'INCLUDED']
    print('== CENSO DAS TRANSCRIÇÕES DO ACERVO ==')
    print('  objetos distintos (por video)   : %d' % len(objs))
    print('  TRANSCRIPT_USABLE (chars > 0)   : %d' % len(inc))
    print('  sem texto, com razao declarada  : %d' % len(exc))
    print('  caracteres de fala              : %s' % f'{sum(o["CHARS"] for o in inc):,}')
    print('  pedidos registrados no manifesto: %d' % len(ped))
    print()
    for rot, ch in (('BY_LANGUAGE', 'SOURCE_LANGUAGE'), ('BY_COUNTRY', 'SOURCE_COUNTRY'),
                    ('BY_PLATFORM', 'PLATFORM'), ('BY_CAPTION_SOURCE', 'CAPTION_SOURCE')):
        print('  %-18s %s' % (rot, dict(Counter(o[ch] for o in objs).most_common())))
    print('  %-18s %s' % ('BY_STATE_REASON',
                          dict(Counter(o['STATE_REASON'] for o in exc).most_common())))
    dup = sum(len(o.get('ALSO_COLLECTED_BY') or []) for o in objs)
    print('  colheitas repetidas do mesmo video, registradas: %d' % dup)


if __name__ == '__main__':
    sys.exit(main())
