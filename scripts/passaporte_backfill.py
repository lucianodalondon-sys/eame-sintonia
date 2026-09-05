#!/usr/bin/env python3
"""
BACKFILL DO ACERVO — onde cada coisa ESTÁ, não o que ela deveria ter virado.

Esta migração é **somente leitura sobre o acervo**: ela não reinterpreta conteúdo, não
reclassifica, não abre uma execução, não gasta um centavo. Ela lê o que os artefatos já
declaram e converte isso em identidade, estado e histórico.

AS TRÊS PROIBIÇÕES DESTE ARQUIVO
----------------------------------
1. **NÃO inventar que um item foi lido porque existe classificador.** O classificador
   lexical do SENSOR tocou o texto de 431 vídeos e 991 comentários. Isso é
   `LEXICALLY_SCANNED`, um selo mais fraco, e ele NUNCA vira `READ`. Foi essa confusão
   que deixou 1.005.157 caracteres de transcrição parecerem processados.

2. **NÃO inventar que algo foi consumido porque aparece numa pasta de inteligência.**
   `ES-X-VOICE-FIELD.json` cruzou as datas dos 252 vídeos espanhóis com o RAIF. É
   tentador selar 252 consumos. Não é consumo de inteligência do item: é um agregado
   sobre metadados, e o resultado foi `NO_RELIABLE_SIGNAL`. Nenhum consumo é selado por
   este backfill — o acervo inteiro sai `READY_NOT_CONSUMED` ou antes disso, e a dívida
   aparece no painel em vez de sumir.

3. **NÃO promover UNKNOWN a estado.** O que o artefato não prova sai `UNKNOWN` ou
   `PENDING`. Estado reconstruído sem prova seria pior do que estado ausente: teria a
   mesma cara do estado medido.

O QUE ESTE BACKFILL PROVA DE PROPÓSITO
----------------------------------------
Que selo novo não apaga selo antigo. Os 102 candidatos a canal do SENSOR entram com o
selo da coleta (`NOT_PROVED`, 2026-08-30 21h) e recebem depois o selo da prova de
identidade derivada (`PROVED`/`PLAUSIBLE`/`NOT_PROVED`, mesma data, processo diferente).
Os dois selos ficam no histórico; só a projeção mostra o último.

    python3 scripts/passaporte_backfill.py            # reconstrói data/passaporte/EVENTOS.jsonl
    python3 scripts/passaporte_backfill.py --dry-run  # só conta, não grava
"""
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
sys.path.insert(0, HERE)
import passaporte as pp  # noqa: E402

# Data de referência da migração. Explícita, como ES_REFERENCE_DATE em
# metricas_canonicas.py: usar "hoje" faria o mesmo comando produzir um log diferente
# amanhã sem que nada tivesse mudado no acervo.
BACKFILL_AT = '2026-09-05'
ATOR = 'BACKFILL/passaporte_backfill.py'

NAO_SEI = ('NÃO SEI', 'NAO SEI', 'NOT_KNOWN', 'NAO_DECLARADO', 'NOT_DECLARED',
           'UNKNOWN', '', None)


def _ler(*p):
    caminho = os.path.join(SAMPLES, *p)
    if caminho.endswith('.gz'):
        with gzip.open(caminho, 'rt', encoding='utf-8') as f:
            return json.load(f)
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _sabido(v):
    return v not in NAO_SEI and str(v).strip() != ''


def _vid(url):
    """Extrai o id do vídeo da URL. A URL é REFERÊNCIA — o id é que costura a linhagem."""
    if not url:
        return None
    m = re.search(r'[?&]v=([A-Za-z0-9_-]{6,})', str(url))
    return m.group(1) if m else None


def _raw_state(caminho_relativo):
    """PRESERVED só quando o byte está aqui. Caminho declarado e arquivo ausente é
    NOT_PRESERVED — nunca PRESERVED por confiança no manifesto."""
    return ('PRESERVED' if os.path.exists(os.path.join(SAMPLES, caminho_relativo))
            else 'NOT_PRESERVED')


def _tempo(item, campo, relativo=None):
    if _sabido(item.get(campo)):
        return 'PROVED', item[campo]
    if relativo and _sabido(item.get(relativo)):
        return 'RELATIVE_ONLY', item[relativo]
    return 'NOT_KNOWN', None


def _selos_comuns(reg, iid, item, *, ts, geo, geo_ev, crop, issue, tempo, tempo_ev):
    if geo:
        reg.selar(iid, 'GEOGRAPHY_PROVED', to_state='PROVED', actor=ATOR, timestamp=ts,
                  reason=geo_ev, evidence_reference=geo)
    else:
        reg.selar(iid, 'GEOGRAPHY_NOT_PROVED', to_state='NOT_KNOWN', actor=ATOR,
                  timestamp=ts, reason=geo_ev or 'nenhum lugar nomeado no conteúdo')
    reg.selar(iid, 'TIME_RESOLVED', to_state=tempo, actor=ATOR, timestamp=ts,
              reason=tempo_ev, evidence_reference=None)
    reg.selar(iid, 'CROP_DECLARED', to_state='DECLARED' if crop else 'NOT_KNOWN',
              actor=ATOR, timestamp=ts, reason=str(crop) if crop else None)
    reg.selar(iid, 'ISSUE_DECLARED', to_state='DECLARED' if issue else 'NOT_KNOWN',
              actor=ATOR, timestamp=ts, reason=str(issue) if issue else None)


# ══════════════════════════════════════════════════════════════════════════════════
# COLEÇÃO · VOICE_ES  —  a rodada espanhola paga (missões 10A/10B)
# ══════════════════════════════════════════════════════════════════════════════════

def voice_es(reg):
    d = _ler('ES-T8-001-videos.json')
    ts = d['captured_at']
    raw = _raw_state('raw-paid/ES-T8-001-youtube-search.raw.json.gz')

    # As 20 transcrições PEDIDAS estão no bruto pago, com `chars`. É de lá — e não do
    # agregado TRANSCRIPT_STATE — que sai QUAIS 5 voltaram vazias. Contagem agregada não
    # diz quem; o bruto diz.
    pedidas, com_texto = {}, {}
    for t in _ler('raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz'):
        v = _vid(t.get('url'))
        if v:
            pedidas[v] = t.get('chars') or 0
            if t.get('transcript'):
                com_texto[v] = t

    por_video = {}
    for v in d['VIDEOS']:
        base = 'YOUTUBE:VIDEO:%s' % v['EXTERNAL_ID']
        iid = reg.admitir(
            identity_basis=base, collection_id='VOICE_ES', source_id=v['SOURCE_ID'],
            source_family='PLATFORM_PUBLIC_PAID_ROUTE', source_reference=v['URL'],
            captured_at=v['CAPTURE_DATE'], content_type='VIDEO', actor=ATOR,
            raw_state=raw, evidence_reference=d['PIPELINE']['ENTRADA'],
            timestamp=v['CAPTURE_DATE'])
        por_video[v['EXTERNAL_ID']] = iid
        reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED', actor='scripts/voz.py',
                  timestamp=ts, reason=d['PIPELINE']['FUNCAO'],
                  evidence_reference='ES-T8-001-videos.json :: PIPELINE')
        reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor='scripts/voz.py',
                  timestamp=ts, reason='chave %s' % d['DEDUPE']['KEY'],
                  evidence_reference='PIPELINE.DUPLICATE_COUNT=%d' % d['PIPELINE']['DUPLICATE_COUNT'])
        reg.selar(iid, 'LINEAGE_RESOLVED', to_state='ROOT', actor=ATOR, timestamp=ts,
                  reason='vídeo é raiz; transcrição e comentário derivam dele')

        # CONTENT do vídeo é a transcrição dele. Três estados, e o terceiro é o caro:
        # ninguém PERGUNTOU. NOT_TESTED nunca é reprovação.
        eid = v['EXTERNAL_ID']
        if eid in com_texto:
            reg.selar(iid, 'TRANSCRIPT_AVAILABLE', to_state='AVAILABLE', actor=ATOR,
                      timestamp=ts, reason='legenda pública devolvida pela rota paga',
                      evidence_reference='ES-T8-001-transcricoes.json')
        elif eid in pedidas:
            reg.selar(iid, 'CONTENT_UNAVAILABLE', to_state='REQUESTED_EMPTY', actor=ATOR,
                      timestamp=ts, reason='pedida e vazia — estado, não ausência',
                      evidence_reference='raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz')
        else:
            reg.selar(iid, 'CONTENT_UNAVAILABLE', to_state='NOT_TESTED', actor=ATOR,
                      timestamp=ts, reason='transcrição nunca pedida para este vídeo',
                      evidence_reference='TRANSCRIPT_STATE.REQUESTED=%d de %d'
                      % (d['TRANSCRIPT_STATE']['REQUESTED'], len(d['VIDEOS'])))

        # O classificador de CONTENT_TYPE leu TÍTULO e DESCRIÇÃO. Isso é varredura, não
        # leitura — e o selo diz exatamente isso.
        reg.selar(iid, 'CONTENT_SCANNED', to_state='LEXICALLY_SCANNED',
                  actor='scripts/voz.py :: classificação de CONTENT_TYPE', timestamp=ts,
                  reason='classificador lexical sobre título e descrição; %s'
                  % str(v.get('CONTENT_TYPE_EVIDENCE'))[:120],
                  evidence_reference='CONTENT_TYPE=%s' % v.get('CONTENT_TYPE'))

        papel = v.get('DECLARED_ROLE')
        if _sabido(papel):
            reg.selar(iid, 'IDENTITY_PROVED', to_state='PROVED', actor='scripts/voz.py',
                      timestamp=ts, reason='papel declarado pelo canal: %s' % papel,
                      evidence_reference=v.get('ORIGIN_ID'))
        else:
            reg.selar(iid, 'IDENTITY_NOT_PROVED', to_state='NOT_PROVED',
                      actor='scripts/voz.py', timestamp=ts,
                      reason='canal sem papel declarado; nome de conta não decide papel',
                      evidence_reference=v.get('ORIGIN_ID'))
        t_state, t_ev = _tempo(v, 'PUBLICATION_DATE')
        _selos_comuns(reg, iid, v, ts=ts,
                      geo=v.get('FACT_LOCATION') if _sabido(v.get('FACT_LOCATION')) else None,
                      geo_ev=v.get('FACT_LOCATION_RULE'),
                      crop=v.get('CROP') if _sabido(v.get('CROP')) else None,
                      issue=v.get('ISSUE') if _sabido(v.get('ISSUE')) else None,
                      tempo=t_state, tempo_ev=t_ev)

    # ---- transcrições: itens DERIVADOS, com pai resolvido -------------------------
    tr = _ler('ES-T8-001-transcricoes.json')
    for t in tr['TRANSCRIPTS']:
        pai = por_video.get(t['EXTERNAL_ID'])
        base = 'YOUTUBE:TRANSCRIPT:%s:PLATFORM_CAPTIONS_APIFY' % t['EXTERNAL_ID']
        iid = reg.admitir(
            identity_basis=base, collection_id='VOICE_ES', source_id=tr['SOURCE_ID'],
            source_family='PLATFORM_PUBLIC_PAID_ROUTE', source_reference=t['URL'],
            captured_at=tr['captured_at'], content_type='TRANSCRIPT', actor=ATOR,
            parent_item_id=pai, derived_from='TRANSCRIPT_OF',
            raw_state=_raw_state('raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz'),
            evidence_reference='ES-T8-001-transcricoes.json',
            timestamp=tr['captured_at'])
        reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED', actor='scripts/voz.py',
                  timestamp=tr['captured_at'], reason='normalizada na rota de voz')
        reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor=ATOR,
                  timestamp=tr['captured_at'],
                  reason='chave vídeo + origem da legenda')
        reg.selar(iid, 'LINEAGE_RESOLVED',
                  to_state='RESOLVED' if pai else 'BROKEN', actor=ATOR,
                  timestamp=tr['captured_at'],
                  reason='pai = vídeo %s' % t['EXTERNAL_ID'], evidence_reference=pai)
        reg.selar(iid, 'TRANSCRIPT_AVAILABLE', to_state='AVAILABLE', actor=ATOR,
                  timestamp=tr['captured_at'],
                  reason='%s caracteres de legenda pública' % t['CHARS'],
                  evidence_reference='CHARS=%s' % t['CHARS'],
                  extra={'CONTENT_CHARS': len(t['TRANSCRIPT_ORIGINAL'])})
        # O SELO QUE NÃO EXISTE: nenhum processo leu estes caracteres. A ausência do selo
        # é a informação, e é ela que a fila de dívida vai cobrar.
        reg.selar(iid, 'STOPPED_WITH_REASON', to_state=None, actor=ATOR,
                  timestamp=BACKFILL_AT, reason='CONTENT_NOT_PROCESSED',
                  evidence_reference='nenhum evento CONTENT_READ neste item')
        # A transcrição não prova identidade por si: ela herda a referência do pai e nada
        # mais. NOT_APPLICABLE é o estado honesto — não NOT_PROVED, que sugeriria tentativa.
        reg.selar(iid, 'IDENTITY_NOT_PROVED', to_state='NOT_APPLICABLE', actor=ATOR,
                  timestamp=tr['captured_at'],
                  reason='identidade é do vídeo pai; a transcrição herda referência, não prova')
        _selos_comuns(reg, iid, t, ts=tr['captured_at'], geo=None,
                      geo_ev='a transcrição não declara lugar por si',
                      crop=None, issue=None, tempo='PROVED' if _sabido(
                          t.get('PUBLICATION_DATE')) else 'NOT_KNOWN',
                      tempo_ev=t.get('PUBLICATION_DATE'))

    # ---- comentários --------------------------------------------------------------
    cm = _ler('ES-T8-001-comentarios.json')
    for c in cm['COMMENTS']:
        pai = por_video.get(c['VIDEO_ID'])
        iid = reg.admitir(
            identity_basis='YOUTUBE:COMMENT:%s' % c['COMMENT_ID'], collection_id='VOICE_ES',
            source_id=c['SOURCE_ID'], source_family='PLATFORM_PUBLIC_PAID_ROUTE',
            source_reference='youtube:%s#%s' % (c['VIDEO_ID'], c['COMMENT_ID']),
            captured_at=cm['captured_at'], content_type='COMMENT', actor=ATOR,
            parent_item_id=pai, derived_from='COMMENT_ON',
            raw_state=_raw_state('raw-paid/ES-T8-001-youtube-comments.raw.json.gz'),
            timestamp=cm['captured_at'])
        reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED', actor='scripts/voz.py',
                  timestamp=cm['captured_at'], reason='normalizado na rota de voz')
        reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor='scripts/voz.py',
                  timestamp=cm['captured_at'],
                  reason='chave %s' % cm['DEDUPE']['KEY'])
        reg.selar(iid, 'LINEAGE_RESOLVED', to_state='RESOLVED' if pai else 'BROKEN',
                  actor=ATOR, timestamp=cm['captured_at'],
                  reason='comentário do vídeo %s' % c['VIDEO_ID'], evidence_reference=pai)
        reg.selar(iid, 'CONTENT_AVAILABLE', to_state='AVAILABLE', actor=ATOR,
                  timestamp=cm['captured_at'], reason='texto do comentário preservado')
        reg.selar(iid, 'CONTENT_SCANNED', to_state='LEXICALLY_SCANNED',
                  actor='scripts/voz.py :: classificação de comentário',
                  timestamp=cm['captured_at'],
                  reason='classificador lexical; CLASS=%s' % c.get('CLASS'),
                  evidence_reference=str(c.get('CLASS_NOTE'))[:160])
        # AUTHOR_REFERENCE é handle público. Handle não é pessoa — a lei da casa.
        reg.selar(iid, 'IDENTITY_NOT_PROVED', to_state='NOT_PROVED', actor=ATOR,
                  timestamp=cm['captured_at'],
                  reason='AUTHOR_REFERENCE é handle público; HANDLE != PESSOA',
                  evidence_reference=c.get('AUTHOR_REFERENCE'))
        t_state, t_ev = _tempo(c, 'DATE', 'DATE_RELATIVE')
        _selos_comuns(reg, iid, c, ts=cm['captured_at'], geo=None,
                      geo_ev='comentário raramente declara lugar',
                      crop=None,
                      issue=c.get('VIDEO_ISSUE') if _sabido(c.get('VIDEO_ISSUE')) else None,
                      tempo=t_state, tempo_ev=t_ev)

    # ---- posts do LinkedIn ---------------------------------------------------------
    po = _ler('ES-T8-002-posts.json')
    origens = {o['ORIGIN_ID']: o for o in _ler('ES-VOICE-LINKEDIN.json')['ORIGINS']}
    for p in po['POSTS']:
        iid = reg.admitir(
            identity_basis='LINKEDIN:POST:%s' % p['EXTERNAL_ID'], collection_id='VOICE_ES',
            source_id=p['SOURCE_ID'], source_family='PLATFORM_PUBLIC_PAID_ROUTE',
            source_reference=p['URL'], captured_at=p['CAPTURE_DATE'],
            content_type='POST', actor=ATOR,
            raw_state=_raw_state('raw-paid/ES-T8-002-linkedin-posts-a.raw.json.gz'),
            timestamp=p['CAPTURE_DATE'])
        reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED', actor='scripts/voz.py',
                  timestamp=po['captured_at'], reason='normalizado na rota de voz')
        reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor='scripts/voz.py',
                  timestamp=po['captured_at'],
                  reason='chave %s; %s colapsados de %s no lote'
                  % (po['DEDUPE']['KEY'], po['DEDUPE']['COLLAPSED'], po['DEDUPE']['RAW']))
        reg.selar(iid, 'LINEAGE_RESOLVED', to_state='ROOT', actor=ATOR,
                  timestamp=po['captured_at'], reason='post é raiz')
        reg.selar(iid, 'CONTENT_AVAILABLE',
                  to_state='AVAILABLE' if _sabido(p.get('TEXT')) else 'ABSENT',
                  actor=ATOR, timestamp=po['captured_at'],
                  reason='texto do post preservado' if _sabido(p.get('TEXT'))
                  else 'post sem texto')
        o = origens.get(p.get('ORIGIN_ID'))
        if o and _sabido(o.get('DECLARED_ORG_TYPE')) and _sabido(o.get('COUNTRY')):
            reg.selar(iid, 'IDENTITY_PROVED', to_state='PROVED', actor=ATOR,
                      timestamp=po['captured_at'],
                      reason='origem com tipo e país declarados em campo estruturado',
                      evidence_reference='ES-VOICE-LINKEDIN.json :: %s' % p['ORIGIN_ID'])
        else:
            reg.selar(iid, 'IDENTITY_NOT_PROVED', to_state='NOT_PROVED', actor=ATOR,
                      timestamp=po['captured_at'],
                      reason='origem sem tipo ou país declarado em campo estruturado',
                      evidence_reference=p.get('ORIGIN_ID'))
        t_state, t_ev = _tempo(p, 'PUBLICATION_DATE')
        geo = o.get('COUNTRY') if o and _sabido(o.get('COUNTRY')) else None
        _selos_comuns(reg, iid, p, ts=po['captured_at'], geo=geo,
                      geo_ev='país declarado pela ORIGEM, não pelo texto do post'
                      if geo else 'nem origem nem texto declaram país',
                      crop=None, issue=None, tempo=t_state, tempo_ev=t_ev)



# ══════════════════════════════════════════════════════════════════════════════════
# COLEÇÃO · EARLY_SIGNAL_EAME  —  o piloto de sensores técnicos (missão 13)
# ══════════════════════════════════════════════════════════════════════════════════

def early_signal(reg):
    # A medição já dobrou os dois lotes e classificou. Ela é a EVIDÊNCIA dos selos de
    # varredura; não é, e nunca será, evidência de leitura.
    med = _ler('SENSOR-PILOT', 'MEDICAO.json')
    med_por_id = {v.get('EXTERNAL_ID'): v for v in med['VIDEOS_ITEMS']}
    med_com = {c.get('COMMENT_ID'): c for c in med['COMMENTS_ITEMS']}

    por_video = {}
    for lote in ('A', 'B'):
        d = _ler('SENSOR-PILOT', 'VIDEOS-%s.json' % lote)
        for v in d['ITEMS']:
            # O bruto é o da execução DAQUELE item. Usar um caminho fixo por lote marcaria
            # 219 vídeos como NOT_PRESERVED tendo o byte no disco — e NOT_PRESERVED é uma
            # afirmação, não um chute.
            raw = _raw_state('raw-paid/%s.raw.json.gz' % v.get('COLLECTION_RUN_ID'))
            eid = v['EXTERNAL_ID']
            ts = v.get('CAPTURED_AT') or d['CAPTURED_AT']
            novo = eid not in por_video
            iid = reg.admitir(
                identity_basis='YOUTUBE:VIDEO:%s' % eid,
                collection_id='EARLY_SIGNAL_EAME', source_id=d['SOURCE_ID'],
                source_family='PLATFORM_PUBLIC_PAID_ROUTE',
                source_reference=v['SOURCE_URL'], captured_at=ts, content_type='VIDEO',
                actor=ATOR, raw_state=raw, timestamp=ts,
                evidence_reference=v.get('COLLECTION_RUN_ID'))
            por_video[eid] = iid
            if not novo:
                # Reencontro do MESMO vídeo. Não nasce item novo: o log ganha um selo de
                # captura e RECOLLECTED sobe. Foram 9 no lote B, e agora eles são visíveis
                # como reencontro em vez de somarem 9 itens fantasma à contagem.
                continue
            reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED',
                      actor='scripts/sensor_coleta.py', timestamp=ts,
                      reason='normalizado na coleta de sensores')
            reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE',
                      actor='scripts/sensor_medir.py', timestamp=med['captured_at'],
                      reason='dedupe global entre lotes por PLATFORM+EXTERNAL_ID',
                      evidence_reference='MEDICAO.VIDEOS_DUPLICADOS_INTERCEPTADOS=%d'
                      % med['VIDEOS_DUPLICADOS_INTERCEPTADOS'])
            reg.selar(iid, 'LINEAGE_RESOLVED', to_state='ROOT', actor=ATOR, timestamp=ts,
                      reason='vídeo é raiz')
            m = med_por_id.get(eid, {})
            reg.selar(iid, 'CONTENT_UNAVAILABLE',
                      to_state='AVAILABLE' if m.get('TRANSCRIPT_AVAILABLE') == 'YES'
                      else 'NOT_TESTED',
                      actor=ATOR, timestamp=med['captured_at'],
                      reason='TRANSCRIPT_AVAILABLE=%s na coleta'
                      % v.get('TRANSCRIPT_AVAILABLE'),
                      evidence_reference='MEDICAO.TRANSCRIPT_CHARS=%s'
                      % m.get('TRANSCRIPT_CHARS'))
            reg.selar(iid, 'CONTENT_SCANNED', to_state='LEXICALLY_SCANNED',
                      actor='scripts/sensor_medir.py :: classificar_conteudo',
                      timestamp=med['captured_at'],
                      reason='classificador LEXICAL sobre título, descrição e (quando '
                             'houve) transcrição — %s' % med['LIMITE_DO_CLASSIFICADOR'][:90],
                      evidence_reference='CONTENT_TYPE=%s' % m.get('CONTENT_TYPE'))
            est = v.get('CHANNEL_IDENTITY_STATE')
            reg.selar(iid, 'IDENTITY_PROVED' if est == 'PROVED' else 'IDENTITY_NOT_PROVED',
                      to_state=est if est in ('PROVED', 'PLAUSIBLE', 'NOT_PROVED')
                      else 'UNKNOWN',
                      actor='scripts/sensor_canal_identidade.py', timestamp=ts,
                      reason=str(v.get('CHANNEL_IDENTITY_EVIDENCE'))[:180],
                      evidence_reference=v.get('CHANNEL_URL'))
            pais = m.get('COUNTRY_OF_FACT')
            _selos_comuns(reg, iid, v, ts=med['captured_at'],
                          geo=pais if _sabido(pais) else None,
                          geo_ev=m.get('COUNTRY_OF_FACT_EVIDENCE'),
                          crop=v.get('CROP') if _sabido(v.get('CROP')) else None,
                          issue=v.get('ISSUE') if _sabido(v.get('ISSUE')) else None,
                          tempo='PROVED' if _sabido(v.get('PUBLISHED_AT')) else 'NOT_KNOWN',
                          tempo_ev=v.get('PUBLISHED_AT'))

    # ---- transcrições do piloto: o pai só existe pela URL, e ele resolve -----------
    for lote in ('A', 'B'):
        d = _ler('SENSOR-PILOT', 'TRANSCRICOES-%s.json' % lote)
        for t in d['ITEMS']:
            eid = _vid(t.get('SOURCE_URL'))
            pai = por_video.get(eid)
            ts = t.get('CAPTURED_AT') or d['CAPTURED_AT']
            iid = reg.admitir(
                identity_basis='YOUTUBE:TRANSCRIPT:%s:%s' % (eid, t.get('CAPTION_SOURCE')),
                collection_id='EARLY_SIGNAL_EAME', source_id=d['SOURCE_ID'],
                source_family='PLATFORM_PUBLIC_PAID_ROUTE',
                source_reference=t['SOURCE_URL'], captured_at=ts,
                content_type='TRANSCRIPT', actor=ATOR, parent_item_id=pai,
                derived_from='TRANSCRIPT_OF', timestamp=ts,
                raw_state=_raw_state('raw-paid/%s.raw.json.gz' % t['COLLECTION_RUN_ID']),
                evidence_reference=t.get('COLLECTION_RUN_ID'))
            reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED',
                      actor='scripts/sensor_coleta.py', timestamp=ts,
                      reason='normalizada na coleta de sensores')
            reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor=ATOR, timestamp=ts,
                      reason='chave vídeo + ator de legenda')
            reg.selar(iid, 'LINEAGE_RESOLVED',
                      to_state='RESOLVED' if pai else 'BROKEN', actor=ATOR, timestamp=ts,
                      reason='EXTERNAL_ID saiu NÃO SEI na coleta; o pai foi recosturado '
                             'pela URL, sem reinterpretar conteúdo',
                      evidence_reference=pai)
            reg.selar(iid, 'TRANSCRIPT_AVAILABLE', to_state='AVAILABLE', actor=ATOR,
                      timestamp=ts, reason='%d caracteres de legenda pública'
                      % len(t.get('TRANSCRIPT') or ''),
                      evidence_reference='CHARS=%d' % len(t.get('TRANSCRIPT') or ''),
                      extra={'CONTENT_CHARS': len(t.get('TRANSCRIPT') or '')})
            reg.selar(iid, 'STOPPED_WITH_REASON', to_state=None, actor=ATOR,
                      timestamp=BACKFILL_AT, reason='CONTENT_NOT_PROCESSED',
                      evidence_reference='nenhum evento CONTENT_READ neste item')
            reg.selar(iid, 'IDENTITY_NOT_PROVED', to_state='NOT_APPLICABLE', actor=ATOR,
                      timestamp=ts, reason='identidade é do vídeo pai')
            _selos_comuns(reg, iid, t, ts=ts, geo=None,
                          geo_ev='a transcrição não declara lugar por si',
                          crop=None, issue=None, tempo='NOT_KNOWN', tempo_ev=None)

    # ---- comentários ----------------------------------------------------------------
    for lote in ('A', 'B'):
        d = _ler('SENSOR-PILOT', 'COMENTARIOS-%s.json' % lote)
        for c in d['ITEMS']:
            pai = por_video.get(c.get('VIDEO_ID'))
            ts = c.get('CAPTURED_AT') or d['CAPTURED_AT']
            m = med_com.get(c.get('COMMENT_ID'), {})
            iid = reg.admitir(
                identity_basis='YOUTUBE:COMMENT:%s' % c['COMMENT_ID'],
                collection_id='EARLY_SIGNAL_EAME', source_id=d['SOURCE_ID'],
                source_family='PLATFORM_PUBLIC_PAID_ROUTE',
                source_reference='youtube:%s#%s' % (c.get('VIDEO_ID'), c['COMMENT_ID']),
                captured_at=ts, content_type='COMMENT', actor=ATOR, parent_item_id=pai,
                derived_from='COMMENT_ON', timestamp=ts,
                raw_state=_raw_state('raw-paid/%s.raw.json.gz'
                                     % c.get('COLLECTION_RUN_ID')),
                evidence_reference=c.get('COLLECTION_RUN_ID'))
            reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED',
                      actor='scripts/sensor_coleta.py', timestamp=ts,
                      reason='normalizado na coleta de sensores')
            reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE',
                      actor='scripts/sensor_medir.py', timestamp=med['captured_at'],
                      reason='chave COMMENT_ID; %d duplicados interceptados no acervo'
                      % med['COMMENTS_DUPLICADOS_INTERCEPTADOS'])
            reg.selar(iid, 'LINEAGE_RESOLVED', to_state='RESOLVED' if pai else 'BROKEN',
                      actor='scripts/sensor_medir.py', timestamp=med['captured_at'],
                      reason='recostura por VIDEO_ID — o join da coleta procurou por URL '
                             'e falhou; o dado nunca se perdeu',
                      evidence_reference=pai)
            reg.selar(iid, 'CONTENT_AVAILABLE',
                      to_state='AVAILABLE' if _sabido(c.get('COMMENT_TEXT_RAW'))
                      else 'ABSENT', actor=ATOR, timestamp=ts,
                      reason='texto do comentário preservado')
            reg.selar(iid, 'CONTENT_SCANNED', to_state='LEXICALLY_SCANNED',
                      actor='scripts/sensor_medir.py :: classificar_comentario',
                      timestamp=med['captured_at'],
                      reason='classificador lexical; SPEECH_TYPE=%s'
                      % m.get('SPEECH_TYPE', c.get('SPEECH_TYPE')),
                      evidence_reference=str(m.get('SPEECH_TYPE_EVIDENCE'))[:160])
            reg.selar(iid, 'IDENTITY_NOT_PROVED', to_state='NOT_PROVED', actor=ATOR,
                      timestamp=ts,
                      reason='handle público do comentador; HANDLE != PESSOA',
                      evidence_reference=c.get('COMMENTER_PROFILE_URL'))
            pais = m.get('COUNTRY_OF_FACT', c.get('COUNTRY_OF_FACT'))
            t_state, t_ev = _tempo(c, 'DATE', 'DATE_RELATIVE')
            _selos_comuns(reg, iid, c, ts=med['captured_at'],
                          geo=pais if _sabido(pais) else None,
                          geo_ev=m.get('COUNTRY_OF_FACT_EVIDENCE'),
                          crop=c.get('CROP') if _sabido(c.get('CROP')) else None,
                          issue=c.get('ISSUE') if _sabido(c.get('ISSUE')) else None,
                          tempo=t_state, tempo_ev=t_ev)

    # ---- candidatos a canal: dois selos, o da coleta e o da prova -------------------
    por_perfil = {}
    for lote in ('A', 'B'):
        d = _ler('SENSOR-PILOT', 'CANAIS-%s.json' % lote)
        for c in d['ITEMS']:
            ts = c.get('CAPTURED_AT') or d['CAPTURED_AT']
            chave = '%s:PROFILE:%s' % (c['SOURCE_PLATFORM'], c['EXTERNAL_ID'])
            iid = reg.admitir(
                identity_basis=chave, collection_id='EARLY_SIGNAL_EAME',
                source_id=d['SOURCE_ID'], source_family='PLATFORM_PUBLIC_PAID_ROUTE',
                source_reference=c['SOURCE_URL'], captured_at=ts,
                content_type='PROFILE_CANDIDATE', item_class='ORIGIN_CANDIDATE',
                actor=ATOR, timestamp=ts,
                raw_state=_raw_state('raw-paid/%s.raw.json.gz' % c['COLLECTION_RUN_ID']),
                evidence_reference=c.get('COLLECTION_RUN_ID'))
            if chave in por_perfil:
                continue
            por_perfil[chave] = iid
            reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED',
                      actor='scripts/sensor_coleta.py', timestamp=ts,
                      reason='candidato normalizado; SEARCH_HIT != PERSON')
            reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor=ATOR, timestamp=ts,
                      reason='chave plataforma + EXTERNAL_ID')
            reg.selar(iid, 'LINEAGE_RESOLVED', to_state='ROOT', actor=ATOR, timestamp=ts,
                      reason='candidato é raiz')
            reg.selar(iid, 'CONTENT_AVAILABLE',
                      to_state='AVAILABLE' if _sabido(c.get('PROFILE_NAME')) else 'ABSENT',
                      actor=ATOR, timestamp=ts,
                      reason='campos estruturados do perfil preservados')
            reg.selar(iid, 'IDENTITY_NOT_PROVED', to_state='NOT_PROVED',
                      actor='scripts/sensor_coleta.py', timestamp=ts,
                      reason='selo da COLETA: nenhum candidato nasce provado',
                      evidence_reference=str(c.get('CHANNEL_IDENTITY_EVIDENCE'))[:160])
            _selos_comuns(reg, iid, c, ts=ts,
                          geo=c.get('COUNTRY_OF_PERSON')
                          if _sabido(c.get('COUNTRY_OF_PERSON')) else None,
                          geo_ev='país da PESSOA procurada, não do fato',
                          crop=None, issue=None, tempo='NOT_KNOWN', tempo_ev=None)

    # O segundo selo. Mesma data, processo diferente, e ele NÃO apaga o primeiro.
    ci = _ler('SENSOR-PILOT', 'CANAL-IDENTIDADE.json')
    for c in ci['ITEMS']:
        chave = '%s:PROFILE:%s' % (c['PLATFORM'], c['EXTERNAL_ID'])
        iid = por_perfil.get(chave)
        if not iid:
            continue
        est = c['CHANNEL_IDENTITY_STATE']
        ev = str(c.get('CHANNEL_IDENTITY_EVIDENCE') or '')
        reg.selar(iid, 'IDENTITY_PROVED' if est == 'PROVED' else 'IDENTITY_NOT_PROVED',
                  to_state=est, actor='scripts/sensor_canal_identidade.py',
                  timestamp=ci['captured_at'], reason=ev[:200],
                  evidence_reference='CANAL-IDENTIDADE.json')
        if est == 'NOT_PROVED' and ('omônim' in ev or 'omonim' in ev):
            # Parada DECLARADA, com evidência: o perfil é outra pessoa. Isto é
            # FALSE_POSITIVE — e é a única forma de um item sair do fluxo por julgamento.
            reg.selar(iid, 'STOPPED_WITH_REASON', to_state=None,
                      actor='scripts/sensor_canal_identidade.py',
                      timestamp=ci['captured_at'], reason='FALSE_POSITIVE',
                      evidence_reference=ev[:200])


# ══════════════════════════════════════════════════════════════════════════════════
# COLEÇÃO · TERRITORIAL  —  a rota territorial gratuita (missão 16)
# ══════════════════════════════════════════════════════════════════════════════════

def territorial(reg):
    for nome, tipo in (('ITENS-A.json', 'LISTING_ENTRY'), ('ITENS-B.json', 'LISTING_ENTRY'),
                       ('DOCUMENTOS.json', 'BULLETIN_DOCUMENT')):
        d = _ler('TERRITORIAL', nome)
        ts = d['CAPTURED_AT']
        for i in d['ITEMS']:
            # O ITEM_ID que a missão 16 já cunhou é a BASE de identidade — não o ITEM_ID
            # do passaporte. Ele é estável e local à fonte, que é exatamente o que se pede
            # de uma base; o ID canônico continua sendo derivado dela.
            iid = reg.admitir(
                identity_basis='TERRITORIAL:%s' % i['ITEM_ID'],
                collection_id='TERRITORIAL', source_id=i['SOURCE_ENTITY_ID'],
                source_family='TERRITORIAL_BULLETIN', source_reference=i['SOURCE_URL'],
                captured_at=i.get('CAPTURED_AT') or ts, content_type=tipo, actor=ATOR,
                raw_state='NOT_PRESERVED', timestamp=i.get('CAPTURED_AT') or ts,
                evidence_reference=json.dumps(i.get('PROVENANCE'), ensure_ascii=False))
            reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED',
                      actor='scripts/territorial_documentos.py', timestamp=ts,
                      reason='normalizado na rota territorial (HTTP direto, zero Apify)')
            reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor=ATOR, timestamp=ts,
                      reason='chave SOURCE_ENTITY_ID + url do item')
            reg.selar(iid, 'LINEAGE_RESOLVED', to_state='ROOT', actor=ATOR, timestamp=ts,
                      reason='item territorial é raiz')
            corpo = i.get('DOCUMENT_CHARS')
            if corpo:
                reg.selar(iid, 'CONTENT_AVAILABLE', to_state='AVAILABLE', actor=ATOR,
                          timestamp=ts, reason='%s caracteres de corpo do boletim' % corpo,
                          evidence_reference='DOCUMENT_CHARS=%s' % corpo,
                          extra={'CONTENT_CHARS': int(corpo)})
            elif _sabido(i.get('OBSERVATION_TEXT')):
                # A primeira passagem leu a LISTAGEM, não o corpo. Texto de listagem é
                # conteúdo — mas é o conteúdo da listagem, e o selo diz isso.
                reg.selar(iid, 'CONTENT_AVAILABLE', to_state='AVAILABLE', actor=ATOR,
                          timestamp=ts, reason='texto de LISTAGEM, não corpo do boletim',
                          evidence_reference=str(i.get('OBSERVATION_TYPE_EVIDENCE'))[:140])
            else:
                reg.selar(iid, 'CONTENT_UNAVAILABLE', to_state='NOT_TESTED', actor=ATOR,
                          timestamp=ts, reason='corpo do boletim não baixado nesta passagem')
            reg.selar(iid, 'CONTENT_SCANNED', to_state='LEXICALLY_SCANNED',
                      actor='scripts/territorial_medir.py', timestamp=ts,
                      reason='classificação lexical de OBSERVATION_TYPE=%s'
                      % i.get('OBSERVATION_TYPE'),
                      evidence_reference=str(i.get('OBSERVATION_TYPE_EVIDENCE'))[:140])
            # A fonte territorial é uma AUTORIDADE nomeada com mandato declarado: a
            # identidade da origem está provada por construção da rota, não por inferência.
            reg.selar(iid, 'IDENTITY_PROVED', to_state='PROVED', actor=ATOR, timestamp=ts,
                      reason='fonte institucional com mandato declarado: %s (%s)'
                      % (i.get('SOURCE_NAME'), i.get('SOURCE_TYPE')),
                      evidence_reference=i.get('MANDATE_GEOGRAPHY'))
            pais = i.get('COUNTRY_OF_FACT')
            t_state, t_ev = _tempo(i, 'PUBLISHED_AT')
            _selos_comuns(reg, iid, i, ts=ts, geo=pais if _sabido(pais) else None,
                          geo_ev=i.get('LOCALITY_EVIDENCE'),
                          crop=i.get('CROP') if _sabido(i.get('CROP')) else None,
                          issue=i.get('ISSUE') if _sabido(i.get('ISSUE')) else None,
                          tempo=t_state, tempo_ev=t_ev)


# ══════════════════════════════════════════════════════════════════════════════════
# COLEÇÃO · YOUTUBE_JANELA  —  a grade pública, rota gratuita (missão 17)
# ══════════════════════════════════════════════════════════════════════════════════

def youtube_janela(reg):
    d = _ler('YOUTUBE-JANELA', 'OBJETOS.json')
    ts = d['CAPTURED_AT']
    fila = _ler('YOUTUBE-RELEVANCIA', 'FILA-WHISPER.json')
    recusa = {r['VIDEO_ID']: r for r in fila['RECUSADOS_ITENS']}
    por_video = {}
    for v in d['ITEMS']:
        iid = reg.admitir(
            identity_basis='YOUTUBE:VIDEO:%s' % v['VIDEO_ID'],
            collection_id='YOUTUBE_JANELA', source_id='YOUTUBE-JANELA/OBJETOS',
            source_family='PLATFORM_PUBLIC_FREE_ROUTE', source_reference=v['VIDEO_URL'],
            captured_at=v.get('CAPTURED_AT') or ts, content_type='VIDEO', actor=ATOR,
            # O HTML bruto fica FORA do Git por política (.gitignore). NOT_PRESERVED aqui
            # é um estado declarado, nunca uma ausência de campo.
            raw_state='NOT_PRESERVED', timestamp=v.get('CAPTURED_AT') or ts,
            evidence_reference=v.get('DOOR'))
        if v['VIDEO_ID'] in por_video:
            continue
        por_video[v['VIDEO_ID']] = iid
        reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED',
                  actor='scripts/youtube_janela.py', timestamp=ts,
                  reason='normalizado da grade pública do canal')
        reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor=ATOR, timestamp=ts,
                  reason='chave PLATFORM + VIDEO_ID')
        reg.selar(iid, 'LINEAGE_RESOLVED', to_state='ROOT', actor=ATOR, timestamp=ts,
                  reason='vídeo é raiz')
        # O caso mais limpo do acervo inteiro: 240 de 240 com legenda NÃO TESTADA.
        # Ninguém perguntou. Isso é DEFER com motivo — nunca reprovação.
        reg.selar(iid, 'CONTENT_UNAVAILABLE', to_state='NOT_TESTED', actor=ATOR,
                  timestamp=ts, reason='CAPTION_STATE=%s' % v.get('CAPTION_STATE'),
                  evidence_reference='FILA-WHISPER: %s de %s recusados por %s'
                  % (fila['RECUSADOS'], fila['UNIVERSO'],
                     list(fila['MOTIVOS_DE_RECUSA'])[0]))
        r = recusa.get(v['VIDEO_ID'])
        if r:
            reg.selar(iid, 'STOPPED_WITH_REASON', to_state=None,
                      actor='scripts/youtube_relevancia.py', timestamp=fila['CAPTURED_AT'],
                      reason='TRANSCRIPT_PENDING',
                      evidence_reference='FILA-WHISPER: DECISAO=%s · %s'
                      % (r.get('DECISAO'), str(r.get('POR_QUE'))[:120]))
        reg.selar(iid, 'IDENTITY_PROVED', to_state='PROVED', actor=ATOR, timestamp=ts,
                  reason='conta oficial de empresa com identidade provada na lista '
                         'congelada: %s' % v.get('COMPANY'),
                  evidence_reference=v.get('ACCOUNT_HANDLE'))
        t_state, t_ev = _tempo(v, 'PUBLISHED_AT', 'PUBLISHED_RELATIVE')
        _selos_comuns(reg, iid, v, ts=ts, geo=None,
                      geo_ev='COUNTRY_SCOPE é escopo da CONTA, não lugar do fato',
                      crop=None, issue=None, tempo=t_state, tempo_ev=t_ev)


# ══════════════════════════════════════════════════════════════════════════════════
# ORIGENS — candidatos coletados cuja decisão do pipeline é POR ITEM
# ══════════════════════════════════════════════════════════════════════════════════

def origens(reg):
    b = _ler('COMPETITOR-PUBLIC-COMM', 'PUBLIC-COMM-FIRST-BATCH-EAME.json')
    for a in b['ACCOUNTS']:
        iid = reg.admitir(
            identity_basis='%s:ACCOUNT:%s' % (a['PLATFORM'], a['ACCOUNT_HANDLE']),
            collection_id='COMPETITOR_PUBLIC_COMM', source_id=b['SOURCE_ID'],
            source_family='PLATFORM_PUBLIC_FREE_ROUTE', source_reference=a['ACCOUNT_URL'],
            captured_at=b['CAPTURED_AT'], content_type='ACCOUNT',
            item_class='ORIGIN_CANDIDATE', actor=ATOR, raw_state='NOT_PRESERVED',
            timestamp=b['CAPTURED_AT'], evidence_reference=a.get('IDENTITY_EVIDENCE'))
        reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED', actor=ATOR,
                  timestamp=b['CAPTURED_AT'], reason='conta normalizada na lista congelada')
        reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor=ATOR,
                  timestamp=b['CAPTURED_AT'], reason='chave plataforma + handle')
        reg.selar(iid, 'LINEAGE_RESOLVED', to_state='ROOT', actor=ATOR,
                  timestamp=b['CAPTURED_AT'], reason='conta é raiz')
        reg.selar(iid, 'IDENTITY_PROVED', to_state='PROVED', actor=ATOR,
                  timestamp=b['CAPTURED_AT'], reason=str(a.get('IDENTITY_EVIDENCE'))[:180],
                  evidence_reference='ENTRY_RULE: %s' % b['ENTRY_RULE'][:90])
        # Identidade congelada NÃO é missão terminada — o próprio artefato declara isso.
        reg.selar(iid, 'CONTENT_UNAVAILABLE', to_state='NOT_TESTED', actor=ATOR,
                  timestamp=b['CAPTURED_AT'],
                  reason='CONTENT_COLLECTION_STAGE=%s' % b['CONTENT_COLLECTION_STAGE'],
                  evidence_reference=b['ZERO_MEANS_NOW'][:140])
        _selos_comuns(reg, iid, a, ts=b['CAPTURED_AT'], geo=a.get('COUNTRY'),
                      geo_ev='escopo de país da CONTA, declarado e com evidência',
                      crop=None, issue=None, tempo='NOT_KNOWN', tempo_ev=None)

    d = _ler('ES-VOICE-LINKEDIN.json')
    ts = d['captured_at']
    for o in d['ORIGINS']:
        iid = reg.admitir(
            identity_basis='LINKEDIN:PROFILE:%s' % o['ORIGIN_ID'],
            collection_id='VOICE_ES', source_id='ES-T8-002',
            source_family='PLATFORM_PUBLIC_PAID_ROUTE', source_reference=o['URL'],
            captured_at=ts, content_type='PROFILE', item_class='ORIGIN_CANDIDATE',
            actor=ATOR, raw_state=_raw_state('raw-paid/ES-T8-002-linkedin-profiles.raw.json.gz'),
            timestamp=ts)
        reg.selar(iid, 'NORMALIZED', to_state='NORMALIZED', actor='scripts/voz.py',
                  timestamp=ts, reason='origem normalizada da camada de voz')
        reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor=ATOR, timestamp=ts,
                  reason='chave ORIGIN_ID')
        reg.selar(iid, 'LINEAGE_RESOLVED', to_state='ROOT', actor=ATOR, timestamp=ts,
                  reason='origem é raiz')
        reg.selar(iid, 'CONTENT_AVAILABLE', to_state='AVAILABLE', actor=ATOR, timestamp=ts,
                  reason='campos estruturados da origem preservados')
        # Papel sai de CAMPO ESTRUTURADO. Prosa livre é proibida — medido em 40 perfis:
        # o classificador que lia prosa reportava 100% de cobertura e a cobertura era falsa.
        if _sabido(o.get('DECLARED_ORG_TYPE')) and _sabido(o.get('COUNTRY')):
            reg.selar(iid, 'IDENTITY_PROVED', to_state='PROVED', actor='scripts/voz.py',
                      timestamp=ts, reason='tipo e país declarados em campo estruturado: %s / %s'
                      % (o['DECLARED_ORG_TYPE'], o['COUNTRY']))
        else:
            reg.selar(iid, 'IDENTITY_NOT_PROVED', to_state='NOT_PROVED',
                      actor='scripts/voz.py', timestamp=ts,
                      reason='campo estruturado ausente; nome de conta não decide papel')
        _selos_comuns(reg, iid, o, ts=ts,
                      geo=o.get('COUNTRY') if _sabido(o.get('COUNTRY')) else None,
                      geo_ev='país declarado pela própria origem; idioma não é país',
                      crop=None, issue=None, tempo='NOT_KNOWN', tempo_ev=None)


# ══════════════════════════════════════════════════════════════════════════════════
# SNAPSHOTS — a terceira granularidade, declarada e com contagem visível
# ══════════════════════════════════════════════════════════════════════════════════
#
# REGRA DE GRANULARIDADE (declarada, não implícita). Um passaporte por unidade sobre a
# qual o pipeline toma decisão INDIVIDUAL. Isso acontece quando (a) o item resolve para
# uma execução própria (RUN_ID / COLLECTION_RUN_ID) ou (b) o repositório já registra uma
# decisão por item sobre ele (classificação, fila, veto, estado de identidade).
#
# Registro oficial e corpus científico não satisfazem nem (a) nem (b): eles entram como
# SNAPSHOT e são consumidos como conjunto. Cada snapshot declara `UNIT_COUNT` — as 3.084
# linhas do ROPF e os 1.771 documentos do corpus espanhol NÃO ficam escondidos atrás de
# um passaporte só; ficam contados dentro dele.
#
# O CAMINHO DE SUBIDA ESTÁ DECLARADO: no dia em que o pipeline passar a decidir por linha
# — ler cada paper, por exemplo — o snapshot é expandido em passaportes por linha, e essa
# expansão é uma migração declarada, com evento próprio. Nunca um silêncio.

SNAPSHOTS = (
    # (caminho, SOURCE_ID, família, tipo, captured_at, normalizado, chave de contagem)
    ('EU-T4-001/evidence-32026R1696.json', 'EU-T4-001', 'OFFICIAL_REGISTRY',
     'REGULATORY_ACT', '2026-08-28', True, None),
    ('EU-T4-001/sparql-active-substance-2026.json', 'EU-T4-001', 'OFFICIAL_REGISTRY',
     'REGISTRY_PROJECTION', '2026-08-28', True, None),
    ('EU-T4-001/CELEX-32026R1696-eng.xhtml', 'EU-T4-001', 'OFFICIAL_REGISTRY',
     'REGULATORY_ACT_FULLTEXT', '2026-08-28', False, None),
    ('FR-T4-001/FR-T4-001-adama-produtos.json', 'FR-T4-001', 'OFFICIAL_REGISTRY',
     'REGISTRY_PROJECTION', '2026-08-28', True, 'sample'),
    ('FR-T4-001/FR-T4-001-adama-crop-target.json', 'FR-T4-001', 'OFFICIAL_REGISTRY',
     'REGISTRY_PROJECTION', '2026-08-28', True, 'adama_crop_target_top'),
    ('FR-T4-001/substance_active_utf8.csv', 'FR-T4-001', 'OFFICIAL_REGISTRY',
     'REGISTRY_DUMP', '2026-08-28', False, None),
    ('IT-T4-001/IT-T4-001-adama-expiries.json', 'IT-T4-001', 'OFFICIAL_REGISTRY',
     'REGISTRY_PROJECTION', '2026-08-28', True, 'adama_next_expiries'),
    ('ES-T4-001/ES-T4-002-autorizaciones-excepcionales.json', 'ES-T4-002',
     'OFFICIAL_REGISTRY', 'REGISTRY_PROJECTION', '2026-08-28', True, 'rows'),
    ('ES-T4-001/eppo-dictionary.json', 'ES-T4-001', 'OFFICIAL_REGISTRY',
     'CONTROLLED_VOCABULARY', '2026-08-28', True, None),
    ('ES-T4-001/plagas.xlsx', 'ES-T4-001', 'OFFICIAL_REGISTRY', 'REGISTRY_DUMP',
     '2026-08-28', False, None),
    ('ES-T4-001/jerarquia.xlsx', 'ES-T4-001', 'OFFICIAL_REGISTRY', 'REGISTRY_DUMP',
     '2026-08-28', False, None),
    ('ES-T4-004-denominaciones-comunes.json', 'ES-T4-004', 'OFFICIAL_REGISTRY',
     'REGISTRY_PROJECTION', '2026-08-29', True, None),
    ('ES-T4-004-versoes/dc_web_20260826.pdf', 'ES-T4-004', 'OFFICIAL_REGISTRY',
     'REGISTRY_DUMP', '2026-08-26', False, None),
    ('ES-T4-004-versoes/dc_web_20250528.pdf', 'ES-T4-004', 'OFFICIAL_REGISTRY',
     'REGISTRY_DUMP', '2025-05-28', False, None),
    ('ES-T4-005/ropf_20260829.json.gz', 'ES-T4-005', 'OFFICIAL_REGISTRY',
     'REGISTRY_PROJECTION', '2026-08-29', True, 'rows'),
    ('ES-T4-005-ficha-primaria-es01717.json', 'ES-T4-005', 'OFFICIAL_REGISTRY',
     'REGISTRY_RECORD', '2026-08-29', True, None),
    ('ES-T3-001-raif-olivar-repilo-2026.json', 'ES-T3-001', 'FIELD_MONITORING_NETWORK',
     'MONITORING_SERIES', '2026-08-28', True, None),
    ('ES-T3-001-raif-vid-mildiu-2026.json', 'ES-T3-001', 'FIELD_MONITORING_NETWORK',
     'MONITORING_SERIES', '2026-08-28', True, 'series_pct_cepas_afectadas'),
    ('ES-T3-001-repilo-serie-historica.json', 'ES-T3-001', 'FIELD_MONITORING_NETWORK',
     'MONITORING_SERIES', '2026-08-28', True, None),
    ('EU-T1-001-nuts2-crop-area.json', 'EU-T1-001', 'STATISTICAL_OFFICE',
     'STATISTICAL_SERIES', '2026-08-28', True, 'rows'),
    ('EU-T1-002-wheat-yield-country.json', 'EU-T1-002', 'STATISTICAL_OFFICE',
     'STATISTICAL_SERIES', '2026-08-28', True, None),
    ('EU-T10-001-cereal-prices.json', 'EU-T10-001', 'STATISTICAL_OFFICE',
     'STATISTICAL_SERIES', '2026-08-28', True, 'sample_rows'),
    ('EU-T5-001-openalex-people.json', 'EU-T5-001', 'SCIENCE_CORPUS',
     'PEOPLE_CORPUS', '2026-08-28', True, None),
    ('ES-T5-002-corpus-documentos.json', 'ES-T5-002', 'SCIENCE_CORPUS',
     'DOCUMENT_CORPUS', '2026-08-29', True, 'DOCUMENTS'),
    ('ES-RESEARCHERS-OLIVE.json', 'ES-T5-002', 'SCIENCE_CORPUS', 'PEOPLE_CORPUS',
     '2026-08-29', True, 'RESEARCHERS'),
    ('FR-T13-001-distribution.json', 'FR-T13-001', 'OFFICIAL_REGISTRY',
     'REGISTRY_PROJECTION', '2026-08-28', True, None),
    ('ES-VOICE-YOUTUBE.json', 'ES-T8-001', 'PLATFORM_PUBLIC_PAID_ROUTE',
     'SEARCH_PROBE', '2026-08-29', True, 'SEARCH_TERMS'),
    ('ES-VOICE-INSTAGRAM.json', 'ES-T8-003', 'PLATFORM_PUBLIC_PAID_ROUTE',
     'SEARCH_PROBE', '2026-08-29', True, 'HASHTAGS'),
    ('ES-VOICE-MEDIA-ROUTES.json', 'ES-T7-001', 'MEDIA_FEED', 'ROUTE_PROBE',
     '2026-08-29', True, 'ROUTES'),
)


def snapshots(reg):
    por_source = {}
    for caminho, sid, familia, tipo, ca, norm, chave in SNAPSHOTS:
        completo = os.path.join(SAMPLES, caminho)
        iid = reg.admitir(
            identity_basis='SNAPSHOT:%s:%s' % (sid, caminho), collection_id='ACERVO_BASE',
            source_id=sid, source_family=familia, source_reference='data/samples/' + caminho,
            captured_at=ca, content_type=tipo, item_class='DATASET_SNAPSHOT', actor=ATOR,
            raw_state='PRESERVED' if os.path.exists(completo) else 'NOT_PRESERVED',
            timestamp=ca, evidence_reference='data/samples/' + caminho)
        por_source.setdefault(sid, []).append(iid)
        unidades = None
        if chave and caminho.endswith(('.json', '.json.gz')):
            d = _ler(caminho)
            unidades = len(d.get(chave) or [])
        reg.selar(iid, 'NORMALIZED',
                  to_state='NORMALIZED' if norm else 'PENDING', actor=ATOR, timestamp=ca,
                  reason='projeção normalizada preservada' if norm
                  else 'bruto da fonte; nenhuma projeção normalizada declarada neste arquivo')
        reg.selar(iid, 'DEDUP_RESOLVED', to_state='UNIQUE', actor=ATOR, timestamp=ca,
                  reason='snapshot é único pela versão da fonte')
        reg.selar(iid, 'LINEAGE_RESOLVED', to_state='ROOT', actor=ATOR, timestamp=ca,
                  reason='snapshot é raiz')
        reg.selar(iid, 'CONTENT_AVAILABLE', to_state='AVAILABLE', actor=ATOR, timestamp=ca,
                  reason='snapshot preservado%s'
                  % ('' if unidades is None else ' · UNIT_COUNT=%d' % unidades),
                  evidence_reference='UNIT_COUNT=%s' % unidades)
        reg.selar(iid, 'IDENTITY_PROVED', to_state='PROVED', actor=ATOR, timestamp=ca,
                  reason='fonte oficial/institucional nomeada: %s' % sid,
                  evidence_reference='docs/fontes/ATLAS-DE-FONTES-EAME.md')
        _selos_comuns(reg, iid, {}, ts=ca, geo=None,
                      geo_ev='o snapshot cobre várias geografias; o lugar é por linha',
                      crop=None, issue=None, tempo='PROVED', tempo_ev=ca)
    return por_source


# ══════════════════════════════════════════════════════════════════════════════════
# LEITURA, CLAIM, ROTA E CONSUMO — derivados dos casos já publicados, nunca digitados
# ══════════════════════════════════════════════════════════════════════════════════
#
# Este é o único lugar do backfill onde um item sai de INTELLIGENCE_READING. A prova de
# que ele foi lido não é "existe um classificador": é um CASO PUBLICADO que nomeia a fonte,
# publica um número derivado dela e aponta a evidência preservada.
#
# A capacidade que consumiu sai da ÁREA que lista aquele caso em REAL_EXAMPLES. Nenhum
# consumo é inventado: quando nenhuma área lista o caso, o claim fica sem rota e aparece
# em ORPHAN_INTELLIGENCE — que é exatamente o que ele é.

AREA_PARA_CAPACIDADE = {
    'REGULATORY': 'REGULATORY',
    'MOLECULE': 'PORTFOLIO',
    'PEST & DISEASE': 'PHYTOSANITARY',
    'SCIENCE & EXPERTS': 'SCIENCE',
    'CROPS & CLIMATE': 'COUNTRY_CROP_PULSE',
    'COMPETITIVE': 'COMPETITOR',
    'MARKET': 'MARKET_DEVELOPMENT',
    'DISTRIBUTION': 'COMMERCIAL',
    'FIELD VOICES': 'HUMAN_SENSORS',
    'EVIDENCE & SOURCES': 'ASK_SINTONIA',
}

# OPPORTUNITY não recebe rota automática de nenhuma área — de propósito. O produto declara
# `PRIORITY TO INVESTIGATE ← nunca SALES OPPORTUNITY`. Toda rota para OPPORTUNITY nasce
# BLOCKED, com o motivo escrito, até que alguém prove o contrário com dado interno da ADAMA.
OPPORTUNITY_BLOQUEIO = ('a saída provada é PRIORITY TO INVESTIGATE, nunca SALES '
                        'OPPORTUNITY: volume, preço, canal e prioridade interna não '
                        'existem em fonte pública (ARQUITETURA-DE-PRODUTO-ATUAL.md)')


def _casos():
    """Lê os casos publicados: CASE_ID -> {SOURCES, RAW_EVIDENCE, TITULO}."""
    caminho = os.path.join(ROOT, 'docs', 'apresentacao', 'CASOS-PARA-APRESENTACAO.md')
    with open(caminho, encoding='utf-8') as f:
        texto = f.read()
    casos, atual = {}, None
    for linha in texto.splitlines():
        m = re.match(r'^### (CASE-\d+)\s*·\s*(.+)$', linha)
        if m:
            atual = m.group(1)
            casos[atual] = {'TITULO': m.group(2).strip(), 'SOURCES': [], 'EVIDENCE': []}
            continue
        if not atual:
            continue
        if linha.startswith('SOURCES:'):
            casos[atual]['SOURCES'] = sorted(set(re.findall(r'\b([A-Z]{2}-T\d+-\d{3})\b',
                                                            linha)))
        if 'RAW_EVIDENCE' in linha:
            casos[atual]['EVIDENCE'] = re.findall(r'`([^`]+)`', linha)
    return casos


def _areas():
    """Lê as áreas de informação: ÁREA -> [CASE_ID] declarados em REAL_EXAMPLES."""
    caminho = os.path.join(ROOT, 'docs', 'ferramentas', 'ARQUITETURA-DE-INFORMACAO-EAME.md')
    with open(caminho, encoding='utf-8') as f:
        texto = f.read()
    areas, atual = {}, None
    for linha in texto.splitlines():
        m = re.match(r'^## ÁREA · ([A-Z &]+?)\s+—', linha)
        if m:
            atual = m.group(1).strip()
            areas[atual] = []
            continue
        if atual and linha.startswith('REAL_EXAMPLES:'):
            areas[atual] = sorted(set(re.findall(r'\b(CASE-\d+)\b', linha)))
    return areas


def leituras(reg, por_source):
    casos, areas = _casos(), _areas()
    por_caso = {}
    for area, lista in areas.items():
        cap = AREA_PARA_CAPACIDADE.get(area)
        if not cap:
            continue
        for cid in lista:
            por_caso.setdefault(cid, []).append(cap)

    lidos, sem_snapshot = set(), set()
    for cid, caso in sorted(casos.items()):
        for sid in caso['SOURCES']:
            alvos = por_source.get(sid)
            if not alvos:
                sem_snapshot.add(sid)
                continue
            for iid in alvos:
                if iid not in lidos:
                    reg.selar(iid, 'CONTENT_READ', to_state='READ',
                              actor='docs/apresentacao/CASOS-PARA-APRESENTACAO.md',
                              timestamp='2026-08-28',
                              reason='caso publicado nomeia esta fonte e publica número '
                                     'derivado dela',
                              evidence_reference=' · '.join(caso['EVIDENCE']) or cid)
                    lidos.add(iid)
                ids = reg.extrair_claims(
                    iid, ['%s — %s' % (cid, caso['TITULO'])],
                    actor='docs/apresentacao/CASOS-PARA-APRESENTACAO.md',
                    timestamp='2026-08-28',
                    evidence_reference=' · '.join(caso['EVIDENCE']) or cid)
                reg.selar(iid, 'INTELLIGENCE_PRODUCED', to_state='PRODUCED',
                          actor='docs/apresentacao/CASOS-PARA-APRESENTACAO.md',
                          timestamp='2026-08-28', reason=cid)
                caps = por_caso.get(cid, [])
                for cap in caps:
                    reg.rotear(iid, ids[0], cap, 'DIRECT',
                               actor='docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md',
                               timestamp='2026-08-28',
                               why='a área que sustenta %s lista %s em REAL_EXAMPLES'
                                   % (cap, cid))
                    reg.consumir(iid, ids[0], cap,
                                 actor='docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md',
                                 timestamp='2026-08-28',
                                 evidence_reference='%s · REAL_EXAMPLES=%s' % (cid, cid))
                if caps:
                    # A mesma inteligência, na capacidade OPPORTUNITY, nasce BLOQUEADA —
                    # e continua existindo. É a prova de que o Passaporte não é um funil
                    # de oportunidades: destino único não existe.
                    reg.rotear(iid, ids[0], 'OPPORTUNITY', 'BLOCKED',
                               actor=ATOR, timestamp='2026-08-28',
                               why=OPPORTUNITY_BLOQUEIO,
                               blocker='NO_INTERNAL_ADAMA_DATA')
    return sorted(sem_snapshot)


# ══════════════════════════════════════════════════════════════════════════════════
# PORTÃO DE ENTRADA DO ACERVO — nenhum arquivo entra sem classificação declarada
# ══════════════════════════════════════════════════════════════════════════════════
#
# Esta tabela é o que torna a regra TECNICAMENTE IMPOSSÍVEL de burlar em vez de apenas
# recomendada. Arquivo novo em `data/samples/` que ninguém declarou aqui derruba o portão.
# Não há classificação por padrão, não há heurística de nome, não há "provavelmente é
# derivado". A porta é fechada e a chave é uma linha nesta tabela.
#
#   ITENS       — adaptador cunha passaportes a partir dele
#   SELOS       — adaptador acrescenta selos a passaportes que já existem
#   SNAPSHOT    — um passaporte para o arquivo inteiro (ver SNAPSHOTS)
#   DERIVADO    — produzido DENTRO do Sintonia a partir de material já passaportado
#   OPERACIONAL — metadado de execução, política ou portão; não é unidade de informação
#   RAW         — evidência bruta de execução paga (política em POLITICA-RAW-ROTA-PAGA)
#   DOC         — texto explicativo ao lado do dado

INVENTARIO = {
    'ES-T8-001-videos.json': ('ITENS', 'vídeos da rodada espanhola paga'),
    'ES-T8-001-transcricoes.json': ('ITENS', 'transcrições derivadas dos vídeos'),
    'ES-T8-001-comentarios.json': ('ITENS', 'comentários derivados dos vídeos'),
    'ES-T8-002-posts.json': ('ITENS', 'posts do LinkedIn'),
    'ES-VOICE-LINKEDIN.json': ('ITENS', 'origens do LinkedIn, decisão de papel por item'),
    'SENSOR-PILOT/VIDEOS-A.json': ('ITENS', 'vídeos do piloto, lote A'),
    'SENSOR-PILOT/VIDEOS-B.json': ('ITENS', 'vídeos do piloto, lote B'),
    'SENSOR-PILOT/TRANSCRICOES-A.json': ('ITENS', 'transcrições do piloto, lote A'),
    'SENSOR-PILOT/TRANSCRICOES-B.json': ('ITENS', 'transcrições do piloto, lote B'),
    'SENSOR-PILOT/COMENTARIOS-A.json': ('ITENS', 'comentários do piloto, lote A'),
    'SENSOR-PILOT/COMENTARIOS-B.json': ('ITENS', 'comentários do piloto, lote B'),
    'SENSOR-PILOT/CANAIS-A.json': ('ITENS', 'candidatos a canal, lote A'),
    'SENSOR-PILOT/CANAIS-B.json': ('ITENS', 'candidatos a canal, lote B'),
    'SENSOR-PILOT/CANAL-IDENTIDADE.json': ('SELOS', 'segundo selo de identidade'),
    'SENSOR-PILOT/MEDICAO.json': ('SELOS', 'evidência dos selos de varredura lexical'),
    'TERRITORIAL/ITENS-A.json': ('ITENS', 'itens de listagem territorial, lote A'),
    'TERRITORIAL/ITENS-B.json': ('ITENS', 'itens de listagem territorial, lote B'),
    'TERRITORIAL/DOCUMENTOS.json': ('ITENS', 'corpos de boletim baixados'),
    'YOUTUBE-JANELA/OBJETOS.json': ('ITENS', 'grade pública de vídeos, rota gratuita'),
    'YOUTUBE-RELEVANCIA/FILA-WHISPER.json': ('SELOS', 'decisão de fila por vídeo'),
    'COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json': (
        'ITENS', 'contas de concorrente com identidade congelada'),

    'ASK-SINTONIA-benchmark.json': ('DERIVADO', 'benchmark da camada de evidência'),
    'ASK-SINTONIA-teste.json': ('DERIVADO', 'teste determinístico da camada'),
    'AUDITORIA-REGRA-COLETA-EXTERNA.json': ('DERIVADO', 'auditoria do próprio repositório'),
    'BACKTEST-REPILO-LEAD-TIME.json': ('DERIVADO', 'backtest sobre ES-T3-001'),
    'BENCHMARK-ORDENACAO-B2.json': ('DERIVADO', 'benchmark de ordenação'),
    'BENCHMARK-RESEARCH-SAVING-B1.json': ('DERIVADO', 'benchmark de economia de pesquisa'),
    'CASE-006-es41-rain-window-vs-yield.json': ('DERIVADO', 'cruzamento do caso 006'),
    'CHANGE-EVENTS-es-2025-2026.json': ('DERIVADO', 'diferença entre duas versões da fonte'),
    'COMPETITOR-azoxy-prothio-italy.json': ('DERIVADO', 'recorte sobre IT-T4-001'),
    'CROSS-MARKET-prothioconazole-cereal.json': ('DERIVADO', 'cruzamento entre registros'),
    'ES-COMPETITOR-VOICE.json': ('DERIVADO', 'agregado por origem sobre ES-T8-002'),
    'ES-PRESSAO-x-AREA-OLIVAR.json': ('DERIVADO', 'cruzamento RAIF × área de olivar'),
    'ES-T4-004-denominaciones-medida.json': ('DERIVADO', 'medida de cobertura do parser'),
    'ES-T4-004-denominaciones-padrao.json': ('DERIVADO', 'padrão observado nas denominações'),
    'ES-T4-005-denominadores-ropf.json': ('DERIVADO', 'denominadores derivados do ROPF'),
    'ES-T4-005-divergencia-resolvida.json': ('DERIVADO', 'resolução de divergência'),
    'ES-T8-001-baseline-canais.json': ('DERIVADO', 'baseline por canal sobre ES-T8-001'),
    'ES-VOICE-x-REGUA.json': ('DERIVADO', 'reconciliação geográfica da camada de voz'),
    'ES-X-VOICE-FIELD.json': ('DERIVADO', 'cruzamento temporal voz × campo'),
    'ES-X-VOICE-SCIENCE.json': ('DERIVADO', 'cruzamento voz × ciência'),
    'PILOT-SCOPE-MATRIX-V1.json': ('DERIVADO', 'varredura do próprio repositório'),
    'PORTAO-10B-ES.json': ('DERIVADO', 'estado derivado dos portões'),
    'PUBLIC-TECHNICAL-VOICE-QUEUE-ES.json': ('DERIVADO', 'fila derivada de ES-VOICE-LINKEDIN'),
    'RADAR-ADAMA-prothioconazole.json': ('DERIVADO', 'radar público cruzado com registro'),
    'RAIF-COORTE-REPILO.json': ('DERIVADO', 'coorte derivada de ES-T3-001'),
    'REDTEAM-CASE-014-datas.json': ('DERIVADO', 'red team sobre datas do caso 014'),
    'RESEARCHER-PUBLIC-VOICE-QUEUE-ES.json': ('DERIVADO', 'fila derivada do corpus'),
    'SLICE-PLASVI-vertical.json': ('DERIVADO', 'fatia vertical sobre FR-T4-001'),
    'SPEAKER-UNIVERSE-PILOT-V1.json': ('DERIVADO', 'universo derivado da fila espanhola'),
    'X-001-completo-mildiu-vs-clima.json': ('DERIVADO', 'cruzamento X-001'),
    'X-001-nuts2-heat-vs-wheat.json': ('DERIVADO', 'cruzamento X-001'),
    'X-006-eu-cas-to-ephy.json': ('DERIVADO', 'normalização por CAS'),
    'X-006-substance-normalisation.json': ('DERIVADO', 'normalização de substância'),
    'X-007-canonical-agro-dictionary.json': ('DERIVADO', 'dicionário agronômico canônico'),
    'TERRITORIAL/MEDICAO.json': ('DERIVADO', 'medição da rota territorial'),
    'YOUTUBE-JANELA/CANAIS.json': ('DERIVADO', 'recorte da lista congelada de contas'),
    'YOUTUBE-RELEVANCIA/FONTES.json': ('DERIVADO', 'fontes lidas na janela'),
    'YOUTUBE-RELEVANCIA/LEXICO-APROVADO.json': ('DERIVADO', 'léxico aprovado'),
    'YOUTUBE-RELEVANCIA/LEXICO-CANDIDATOS.json': ('DERIVADO', 'léxico candidato'),
    'YOUTUBE-RELEVANCIA/LEXICO-COBERTURA.json': ('DERIVADO', 'cobertura do léxico'),

    'DATA-CLOCK-manifest.json': ('OPERACIONAL', 'relógio de versões das fontes'),
    'ES-T8-002-entradas-enriquecimento.json': ('OPERACIONAL', 'entradas reais das execuções'),
    'INVENTARIO-SCRATCHPAD-HANDOFF.json': ('OPERACIONAL', 'decisão PRESERVE/DISCARD'),
    'POLITICA-RAW-ROTA-PAGA.json': ('OPERACIONAL', 'política de bruto de rota paga'),
    'ROTAS-EXTERNAS-TESTADAS-M09.json': ('OPERACIONAL', 'rotas testadas'),
    'RUN-MANIFEST.json': ('OPERACIONAL', 'manifesto de execuções'),
    'SENSOR-PILOT/CONTRATOS-DE-ENTRADA.json': ('OPERACIONAL', 'contratos de ator'),
    'SENSOR-PILOT/RUNS-A.json': ('OPERACIONAL', 'fragmento de manifesto, lote A'),
    'SENSOR-PILOT/RUNS-B.json': ('OPERACIONAL', 'fragmento de manifesto, lote B'),
    'TERRITORIAL/INVENTARIO-DE-FONTES.json': ('OPERACIONAL', 'inventário de fontes'),

    'ES-T4-004-versoes/LEIA-ME.md': ('DOC', 'nota ao lado das versões do dc_web'),
    'ES-T4-005/LEIA-ME.md': ('DOC', 'nota ao lado do export do ROPF'),
    '.gitkeep': ('DOC', 'marcador de pasta versionada'),
}
for _c, _s, _f, _t, _ca, _n, _k in SNAPSHOTS:
    INVENTARIO[_c] = ('SNAPSHOT', 'snapshot de %s' % _s)

# Duas pastas com regra de DIRETÓRIO, e o motivo está declarado:
#   raw-paid/  — todo arquivo ali é bruto de rota paga por definição da pasta, e a política
#                que o governa é POLITICA-RAW-ROTA-PAGA.json.
#   data/runs/ — todo arquivo ali é fragmento de manifesto de execução, governado por
#                scripts/proveniencia.py, que já tem portão próprio.
DIRETORIOS = {'raw-paid/': ('RAW', 'bruto de rota paga'),
              '__runs__': ('OPERACIONAL', 'fragmento de manifesto de execução')}


def inventario_do_acervo():
    """Varre o acervo e devolve (classificados, NÃO DECLARADOS). O segundo tem de ser []."""
    classificados, orfaos = {}, []
    for base, _, arquivos in os.walk(SAMPLES):
        for nome in sorted(arquivos):
            rel = os.path.relpath(os.path.join(base, nome), SAMPLES).replace(os.sep, '/')
            if rel.startswith('raw-paid/'):
                classificados[rel] = DIRETORIOS['raw-paid/']
                continue
            if rel in INVENTARIO:
                classificados[rel] = INVENTARIO[rel]
            else:
                orfaos.append('data/samples/' + rel)
    runs = os.path.join(ROOT, 'data', 'runs')
    for base, _, arquivos in os.walk(runs):
        for nome in sorted(arquivos):
            rel = os.path.relpath(os.path.join(base, nome), runs).replace(os.sep, '/')
            classificados['data/runs/' + rel] = DIRETORIOS['__runs__']
    return classificados, orfaos


def backfill(reg=None):
    reg = reg or pp.Registro([], pp.EVENTOS)
    voice_es(reg)
    early_signal(reg)
    territorial(reg)
    youtube_janela(reg)
    origens(reg)
    por_source = snapshots(reg)
    sem_snapshot = leituras(reg, por_source)
    return reg, sem_snapshot


def main():
    reg, sem_snapshot = backfill()
    ps = reg.passaportes()
    _, orfaos = inventario_do_acervo()
    if '--dry-run' not in sys.argv:
        reg.gravar()
    from collections import Counter
    print('EVENTOS              %6d' % len(reg.eventos))
    print('PASSAPORTES          %6d' % len(ps))
    print('recoletas            %6d' % sum(p['RECOLLECTED'] for p in ps.values()))
    print('por coleção          %s' % dict(Counter(p['COLLECTION_ID'] for p in ps.values())))
    print('por classe           %s' % dict(Counter(p['ITEM_CLASS'] for p in ps.values())))
    print('ciclo de vida        %s' % dict(Counter(p['LIFECYCLE'] for p in ps.values())))
    print('estágio atual        %s' % dict(Counter(p['CURRENT_STAGE'] for p in ps.values())))
    print('SOURCE_ID de caso sem snapshot: %s' % (sem_snapshot or 'nenhum'))
    print('ARQUIVOS NÃO DECLARADOS: %s' % (orfaos or 'nenhum'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
