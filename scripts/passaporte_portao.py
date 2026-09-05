#!/usr/bin/env python3
"""
PORTÃO DO PASSAPORTE — dez provas, e nenhuma delas é digitada.

Este arquivo não descreve o contrato: ele o EXERCE. Cada portão é derivado do acervo e do
log de eventos no momento em que roda, e um portão vermelho é a resposta a "podemos
considerar esta informação entregue?" — NÃO, com o nome do portão que barrou.

    PASSPORT_REQUIRED = YES  →  informação nova sem passaporte é REJECT_PIPELINE.
                                Não é WARN_AND_CONTINUE. Não há modo permissivo.

Os dois canários vivem aqui porque um contrato que não é testado contra o incidente que o
gerou é uma promessa, não um contrato.

    python3 scripts/passaporte_portao.py
    python3 scripts/passaporte_portao.py --json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
sys.path.insert(0, HERE)
import passaporte as pp                # noqa: E402
import passaporte_backfill as bf       # noqa: E402

# Os 1.005.157 caracteres do incidente, medidos: 705.149 em ES-T8-001 (15 transcrições) e
# 300.008 no SENSOR-PILOT (15 transcrições). O número é constante de propósito — se o
# acervo mudar, o portão precisa DIZER que mudou, não se ajustar em silêncio.
INCIDENTE_CHARS = 1005157
INCIDENTE_ITENS = 30

# Chaves naturais, relidas do acervo por um caminho INDEPENDENTE do que emitiu os eventos.
# Duas implementações que discordam é exatamente o que este portão existe para pegar.
ESPERADOS = (
    ('ES-T8-001-videos.json', 'VIDEOS', lambda i: 'YOUTUBE:VIDEO:%s' % i['EXTERNAL_ID']),
    ('ES-T8-001-transcricoes.json', 'TRANSCRIPTS',
     lambda i: 'YOUTUBE:TRANSCRIPT:%s:PLATFORM_CAPTIONS_APIFY' % i['EXTERNAL_ID']),
    ('ES-T8-001-comentarios.json', 'COMMENTS',
     lambda i: 'YOUTUBE:COMMENT:%s' % i['COMMENT_ID']),
    ('ES-T8-002-posts.json', 'POSTS', lambda i: 'LINKEDIN:POST:%s' % i['EXTERNAL_ID']),
    ('ES-VOICE-LINKEDIN.json', 'ORIGINS', lambda i: 'LINKEDIN:PROFILE:%s' % i['ORIGIN_ID']),
    ('SENSOR-PILOT/VIDEOS-A.json', 'ITEMS', lambda i: 'YOUTUBE:VIDEO:%s' % i['EXTERNAL_ID']),
    ('SENSOR-PILOT/VIDEOS-B.json', 'ITEMS', lambda i: 'YOUTUBE:VIDEO:%s' % i['EXTERNAL_ID']),
    ('SENSOR-PILOT/COMENTARIOS-A.json', 'ITEMS',
     lambda i: 'YOUTUBE:COMMENT:%s' % i['COMMENT_ID']),
    ('SENSOR-PILOT/COMENTARIOS-B.json', 'ITEMS',
     lambda i: 'YOUTUBE:COMMENT:%s' % i['COMMENT_ID']),
    ('SENSOR-PILOT/TRANSCRICOES-A.json', 'ITEMS',
     lambda i: 'YOUTUBE:TRANSCRIPT:%s:%s' % (bf._vid(i['SOURCE_URL']), i['CAPTION_SOURCE'])),
    ('SENSOR-PILOT/TRANSCRICOES-B.json', 'ITEMS',
     lambda i: 'YOUTUBE:TRANSCRIPT:%s:%s' % (bf._vid(i['SOURCE_URL']), i['CAPTION_SOURCE'])),
    ('SENSOR-PILOT/CANAIS-A.json', 'ITEMS',
     lambda i: '%s:PROFILE:%s' % (i['SOURCE_PLATFORM'], i['EXTERNAL_ID'])),
    ('SENSOR-PILOT/CANAIS-B.json', 'ITEMS',
     lambda i: '%s:PROFILE:%s' % (i['SOURCE_PLATFORM'], i['EXTERNAL_ID'])),
    ('TERRITORIAL/ITENS-A.json', 'ITEMS', lambda i: 'TERRITORIAL:%s' % i['ITEM_ID']),
    ('TERRITORIAL/ITENS-B.json', 'ITEMS', lambda i: 'TERRITORIAL:%s' % i['ITEM_ID']),
    ('TERRITORIAL/DOCUMENTOS.json', 'ITEMS', lambda i: 'TERRITORIAL:%s' % i['ITEM_ID']),
    ('YOUTUBE-JANELA/OBJETOS.json', 'ITEMS', lambda i: 'YOUTUBE:VIDEO:%s' % i['VIDEO_ID']),
    ('COMPETITOR-PUBLIC-COMM/PUBLIC-COMM-FIRST-BATCH-EAME.json', 'ACCOUNTS',
     lambda i: '%s:ACCOUNT:%s' % (i['PLATFORM'], i['ACCOUNT_HANDLE'])),
)


def _chars_do_acervo():
    """Recontagem independente dos caracteres de transcrição que existem no acervo."""
    total, itens = 0, 0
    d = bf._ler('ES-T8-001-transcricoes.json')
    for t in d['TRANSCRIPTS']:
        total += len(t['TRANSCRIPT_ORIGINAL'])
        itens += 1
    for lote in ('A', 'B'):
        for t in bf._ler('SENSOR-PILOT', 'TRANSCRICOES-%s.json' % lote)['ITEMS']:
            total += len(t.get('TRANSCRIPT') or '')
            itens += 1
    return total, itens


def _fail_closed():
    """Exerce a porta fechada. Cada linha aqui DEVE ser recusada; se uma passar, o
    sistema voltou a ser observacional e o portão precisa dizer isso."""
    reg = pp.Registro([], caminho=os.devnull)
    base = dict(identity_basis='X:1', collection_id='C', source_id='S',
                source_family='F', source_reference='r', captured_at='2026-09-05',
                content_type='T', actor='teste')
    tentativas = []

    def recusa(nome, fn):
        try:
            fn()
            tentativas.append((nome, 'PASSOU — PORTA ABERTA'))
        except pp.PassaporteRecusado:
            tentativas.append((nome, 'RECUSADO'))

    recusa('item sem identidade', lambda: reg.admitir(**dict(base, identity_basis='')))
    recusa('item sem coleção', lambda: reg.admitir(**dict(base, collection_id=None)))
    recusa('item sem data de captura', lambda: reg.admitir(**dict(base, captured_at=None)))
    recusa('derivado sem pai',
           lambda: reg.admitir(**dict(base, derived_from='TRANSCRIPT_OF')))
    iid = reg.admitir(**base)
    recusa('claim sem item rastreável',
           lambda: reg.extrair_claims('ITEM-INEXISTENTE', ['x'], actor='t',
                                      timestamp='2026-09-05', evidence_reference='e'))
    cid = reg.extrair_claims(iid, ['afirmação'], actor='t', timestamp='2026-09-05',
                             evidence_reference='e')[0]
    recusa('rota sem claim existente',
           lambda: reg.rotear(iid, 'CLAIM-NAO-EXISTE', 'SCIENCE', 'DIRECT', actor='t',
                              timestamp='2026-09-05', why='porque sim'))
    recusa('consumo sem rota declarada',
           lambda: reg.consumir(iid, cid, 'SCIENCE', actor='t', timestamp='2026-09-05',
                                evidence_reference='e'))
    reg.rotear(iid, cid, 'SCIENCE', 'DIRECT', actor='t', timestamp='2026-09-05',
               why='relevante')
    recusa('consumo sem evidência',
           lambda: reg.consumir(iid, cid, 'SCIENCE', actor='t', timestamp='2026-09-05',
                                evidence_reference=None))
    recusa('estado fora do vocabulário',
           lambda: reg.selar(iid, 'CONTENT_READ', to_state='MEIO_LIDO', actor='t',
                             timestamp='2026-09-05'))
    recusa('parada sem motivo declarado',
           lambda: reg.selar(iid, 'STOPPED_WITH_REASON', actor='t',
                             timestamp='2026-09-05', reason='porque eu quis'))
    recusa('evento sem tempo',
           lambda: reg.selar(iid, 'CONTENT_READ', to_state='READ', actor='t',
                             timestamp=None))
    return tentativas


def canario_multicapacidade():
    """SEGUNDO CANÁRIO · um conteúdo de Massimo Blandino sobre milho que NÃO é oportunidade.

    SONDA DE CONTRATO, e declarada como tal: nenhuma coleta nova foi feita para esta
    missão, e o acervo não contém conteúdo de milho do Blandino — o que ele contém são
    quatro candidatos de LinkedIn homônimos, todos `NOT_PROVED` por cidade divergente.
    Inventar o item seria exatamente o que este contrato proíbe.

    Então o canário prova o que pode ser provado sem coletar: que a MÁQUINA permite o
    estado. Ele roda num registro isolado, em memória, que nunca toca
    `data/passaporte/EVENTOS.jsonl` — e por isso não contamina um único número do acervo.
    """
    reg = pp.Registro([], caminho=os.devnull)
    iid = reg.admitir(
        identity_basis='SONDA:YOUTUBE:VIDEO:BLANDINO-MAIS-CONTRACT-PROBE',
        collection_id='SONDA_DE_CONTRATO', source_id='SONDA', source_family='SYNTHETIC',
        source_reference='sonda de contrato — não é dado do acervo',
        captured_at='2026-09-05', content_type='VIDEO', actor='portão do passaporte')
    for tipo, estado in (('NORMALIZED', 'NORMALIZED'), ('DEDUP_RESOLVED', 'UNIQUE'),
                         ('LINEAGE_RESOLVED', 'ROOT'), ('CONTENT_AVAILABLE', 'AVAILABLE'),
                         ('CONTENT_READ', 'READ'), ('IDENTITY_PROVED', 'PROVED'),
                         ('GEOGRAPHY_PROVED', 'PROVED'), ('CROP_DECLARED', 'DECLARED'),
                         ('ISSUE_DECLARED', 'DECLARED'), ('TIME_RESOLVED', 'PROVED')):
        reg.selar(iid, tipo, to_state=estado, actor='portão do passaporte',
                  timestamp='2026-09-05', reason='sonda de contrato')
    cid = reg.extrair_claims(
        iid, ['milho: manejo de fusariose com base em ensaio multi-ano no Piemonte'],
        actor='portão do passaporte', timestamp='2026-09-05',
        evidence_reference='sonda de contrato')[0]
    rotas = (('SCIENCE', 'DIRECT'), ('COMPETITOR', 'SUPPORTING'),
             ('MARKET_DEVELOPMENT', 'SUPPORTING'), ('OPPORTUNITY', 'BLOCKED'))
    for cap, rel in rotas:
        reg.rotear(iid, cid, cap, rel, actor='portão do passaporte',
                   timestamp='2026-09-05',
                   why='relevância declarada por capacidade — destino único não existe',
                   blocker=('sem produto ADAMA registrado para este par cultura×alvo'
                            if rel == 'BLOCKED' else None))
    reg.consumir(iid, cid, 'SCIENCE', actor='portão do passaporte', timestamp='2026-09-05',
                 evidence_reference='sonda de contrato — consumo com prova')
    p = reg.passaporte(iid)
    por_cap = {r['CAPABILITY_ID']: r for r in p['ROUTES']}
    consumidas = [c for c, r in por_cap.items() if r['STATE'] == 'CONSUMED']
    orfa = iid in pp.filas_de_divida({iid: p})['ORPHAN_INTELLIGENCE']
    return {
        'CONTENT_READ': p['CONTENT_READ_STATE'],
        'CLAIM_STATE': p['CLAIM_STATE'],
        'SCIENCE': por_cap['SCIENCE']['RELEVANCE'],
        'COMPETITOR': por_cap['COMPETITOR']['RELEVANCE'],
        'MARKET_DEVELOPMENT': por_cap['MARKET_DEVELOPMENT']['RELEVANCE'],
        'OPPORTUNITY': por_cap['OPPORTUNITY']['RELEVANCE'],
        'CONSUMED_BY': consumidas,
        'ORPHAN_INTELLIGENCE': 'YES' if orfa else 'NO',
        'LIFECYCLE': p['LIFECYCLE'],
        'OK': (p['CONTENT_READ_STATE'] == 'READ' and p['CLAIM_STATE'] == 'EXTRACTED'
               and por_cap['SCIENCE']['RELEVANCE'] in pp.RELEVANTES
               and por_cap['COMPETITOR']['RELEVANCE'] in pp.RELEVANTES
               and por_cap['MARKET_DEVELOPMENT']['RELEVANCE'] in pp.RELEVANTES
               and por_cap['OPPORTUNITY']['RELEVANCE'] in ('BLOCKED', 'NOT_APPLICABLE')
               and len(consumidas) >= 1 and not orfa),
    }


def avaliar(reg=None):
    reconstruido, sem_snapshot = bf.backfill()
    reg = reg if reg is not None else pp.Registro.carregar()
    ps = reg.passaportes()
    bases = {p['IDENTITY_BASIS'] for p in ps.values()}
    p = {}

    # ---- 1 · o acervo inteiro está declarado --------------------------------------
    classificados, orfaos = bf.inventario_do_acervo()
    p['ACERVO_DECLARADO'] = {
        'PROVED': not orfaos,
        'MEDIDA': '%d arquivos do acervo classificados, %d não declarados'
                  % (len(classificados), len(orfaos)),
        'BLOQUEIO': ('arquivo sem classificação declarada: %s' % orfaos) if orfaos else None,
    }

    # ---- 2 · ITEMS_WITHOUT_PASSPORT = 0 --------------------------------------------
    esperados = set()
    for nome, chave, kf in ESPERADOS:
        d = bf._ler(*nome.split('/'))
        for i in d[chave]:
            esperados.add(kf(i))
    faltando = sorted(esperados - bases)
    p['ITEMS_WITHOUT_PASSPORT'] = {
        'PROVED': not faltando,
        'MEDIDA': '%d unidades relidas do acervo por caminho independente, %d sem passaporte'
                  % (len(esperados), len(faltando)),
        'VALOR': len(faltando),
        'BLOQUEIO': ('unidade sem passaporte: %s' % faltando[:5]) if faltando else None,
    }

    # ---- 3 · contabilidade fechada, global e por coleção ---------------------------
    c = pp.contabilidade(ps)
    porcol = {k: pp.contabilidade(ps, k)
              for k in sorted({q['COLLECTION_ID'] for q in ps.values()})}
    quebradas = [k for k, v in porcol.items() if v['GATE'] != 'PASS']
    p['CONTABILIDADE_FECHADA'] = {
        'PROVED': c['GATE'] == 'PASS' and not quebradas,
        'MEDIDA': 'TOTAL_ENTERED=%d = ACTIVE %d + COMPLETED %d + DEFERRED %d + '
                  'REJECTED %d + ERROR %d · %d coleções fecham'
                  % (c['TOTAL_ENTERED'], c['LIFECYCLE']['ACTIVE'],
                     c['LIFECYCLE']['COMPLETED'], c['LIFECYCLE']['DEFERRED'],
                     c['LIFECYCLE']['REJECTED'], c['LIFECYCLE']['ERROR'],
                     len(porcol) - len(quebradas)),
        'BLOQUEIO': ('coleção que não fecha: %s' % quebradas) if quebradas else None,
    }

    # ---- 4 · UNEXPLAINED_STAGE_DROPS = 0 -------------------------------------------
    p['UNEXPLAINED_STAGE_DROPS'] = {
        'PROVED': not c['UNEXPLAINED_STAGE_DROPS'],
        'MEDIDA': '%d quedas sem motivo em %d estágios'
                  % (len(c['UNEXPLAINED_STAGE_DROPS']), len(pp.ESTAGIOS)),
        'VALOR': len(c['UNEXPLAINED_STAGE_DROPS']),
        'BLOQUEIO': (str(c['UNEXPLAINED_STAGE_DROPS'][:3])
                     if c['UNEXPLAINED_STAGE_DROPS'] else None),
    }

    # ---- 5 · TRANSCRIPT_AVAILABLE_BUT_UNTRACKED = 0 --------------------------------
    chars_acervo, itens_acervo = _chars_do_acervo()
    rastreados = [q for q in ps.values() if q['CONTENT_TYPE'] == 'TRANSCRIPT'
                  and q['CONTENT_STATE'] == 'AVAILABLE']
    chars_rastreados = sum(q['CONTENT_CHARS'] or 0 for q in rastreados)
    fora = itens_acervo - len(rastreados)
    p['TRANSCRIPT_AVAILABLE_BUT_UNTRACKED'] = {
        'PROVED': fora == 0 and chars_rastreados == chars_acervo == INCIDENTE_CHARS,
        'MEDIDA': '%d de %d transcrições com passaporte · %d de %d caracteres rastreados'
                  % (len(rastreados), itens_acervo, chars_rastreados, chars_acervo),
        'VALOR': fora,
        'BLOQUEIO': (None if fora == 0 and chars_rastreados == chars_acervo
                     else 'transcrição fora do passaporte, ou contagem divergente'),
    }

    # ---- 6 · VALID_INTELLIGENCE_WITH_UNKNOWN_CONSUMPTION_STATE = 0 -----------------
    validos = [q for q in ps.values() if q['CLAIM_STATE'] == 'EXTRACTED']
    desconhecidos = [q['ITEM_ID'] for q in validos
                     if q['CONSUMPTION_STATE'] in (pp.UNKNOWN, pp.PENDING)]
    p['VALID_INTELLIGENCE_WITH_UNKNOWN_CONSUMPTION_STATE'] = {
        'PROVED': not desconhecidos,
        'MEDIDA': '%d itens com claim extraído, %d com estado de consumo desconhecido'
                  % (len(validos), len(desconhecidos)),
        'VALOR': len(desconhecidos),
        'BLOQUEIO': ('inteligência sem estado de consumo: %s' % desconhecidos[:3])
                    if desconhecidos else None,
    }

    # ---- 7 · o log é append-only e íntegro ------------------------------------------
    base = reconstruido.eventos
    prefixo = reg.eventos[:len(base)] == base
    p['LOG_APPEND_ONLY'] = {
        'PROVED': prefixo and len(reg.eventos) >= len(base),
        'MEDIDA': '%d eventos gravados · %d reconstruídos do acervo · prefixo íntegro: %s'
                  % (len(reg.eventos), len(base), prefixo),
        'BLOQUEIO': None if prefixo else 'o log gravado não contém o histórico do backfill '
                                         'como prefixo — selo antigo foi alterado',
    }

    # ---- 8 · falha fechada, exercida ------------------------------------------------
    tentativas = _fail_closed()
    abertas = [t for t in tentativas if t[1] != 'RECUSADO']
    p['FAIL_CLOSED'] = {
        'PROVED': not abertas,
        'MEDIDA': '%d tentativas de entrada inválida, %d recusadas'
                  % (len(tentativas), len(tentativas) - len(abertas)),
        'BLOQUEIO': ('porta aberta: %s' % abertas) if abertas else None,
    }

    # ---- 9 · primeiro canário · os 1.005.157 caracteres -----------------------------
    canario = [q for q in ps.values() if q['CONTENT_TYPE'] == 'TRANSCRIPT']
    certos = [q for q in canario
              if q['CONTENT_STATE'] == 'AVAILABLE'
              and q['CONTENT_READ_STATE'] != 'READ'
              and q['CURRENT_STAGE'] == 'INTELLIGENCE_READING'
              and q['STAGE_VERDICT'] == 'PENDING'
              and 'CONTENT_NOT_PROCESSED' in q['BLOCKER_CODES']]
    p['CANARIO_TRANSCRICAO'] = {
        'PROVED': len(certos) == len(canario) == INCIDENTE_ITENS,
        'MEDIDA': '%d de %d transcrições em TRANSCRIPT_AVAILABLE=YES · TRANSCRIPT_READ=NO '
                  '· CURRENT_STAGE=INTELLIGENCE_READING · BLOCKER=CONTENT_NOT_PROCESSED'
                  % (len(certos), len(canario)),
        'BLOQUEIO': None if len(certos) == len(canario) == INCIDENTE_ITENS
                    else 'o sistema conseguiu deixar transcrição invisível',
    }

    # ---- 10 · segundo canário · multicapacidade sem funil de oportunidade -----------
    m = canario_multicapacidade()
    p['CANARIO_MULTICAPACIDADE'] = {
        'PROVED': m['OK'],
        'MEDIDA': 'SCIENCE=%s · COMPETITOR=%s · MARKET_DEVELOPMENT=%s · OPPORTUNITY=%s '
                  '· CONSUMED_BY=%d · ORPHAN_INTELLIGENCE=%s'
                  % (m['SCIENCE'], m['COMPETITOR'], m['MARKET_DEVELOPMENT'],
                     m['OPPORTUNITY'], len(m['CONSUMED_BY']), m['ORPHAN_INTELLIGENCE']),
        'BLOQUEIO': None if m['OK'] else 'a máquina não permite inteligência válida fora '
                                         'do funil de oportunidade',
        'SONDA': m,
    }

    p['_SEM_SNAPSHOT'] = sem_snapshot
    return p


def veredito(p=None):
    p = p if p is not None else avaliar()
    return 'PASS' if all(v['PROVED'] for k, v in p.items()
                         if not k.startswith('_')) else 'FAIL'


def main():
    p = avaliar()
    v = veredito(p)
    if '--json' in sys.argv:
        print(json.dumps({'PORTOES': p, 'PASSPORT_ENFORCEMENT':
                          'ACTIVE' if v == 'PASS' else 'BLOCKED'},
                         ensure_ascii=False, indent=1))
        return 0 if v == 'PASS' else 1
    for nome, r in p.items():
        if nome.startswith('_'):
            continue
        print('%-48s %s' % (nome, 'PASS' if r['PROVED'] else 'FAIL'))
        print('    %s' % r['MEDIDA'])
        if r.get('BLOQUEIO'):
            print('    BLOQUEIO: %s' % r['BLOQUEIO'])
    print()
    print('SOURCE_ID de caso sem snapshot preservado: %s' % (p['_SEM_SNAPSHOT'] or 'nenhum'))
    print('PASSPORT_ENFORCEMENT = %s' % ('ACTIVE' if v == 'PASS' else 'BLOCKED'))
    return 0 if v == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
