#!/usr/bin/env python3
"""
CICLO 1 — INVENTARIO DE TUDO QUE JA FOI COLETADO E ESTA FECHADO.

    py scripts/it_inventario.py

POR QUE ESTE ARQUIVO EXISTE
-----------------------------
A coleta continua rodando em outra trilha. Esta aqui NAO toca nela: le apenas arquivos
FECHADOS — versionados no HEAD e sem escrita recente — e monta um SNAPSHOT IMUTAVEL com
uma linha por objeto de fala.

    LOTE FECHADO -> SNAPSHOT CONGELADO -> INTELIGENCIA
    Um arquivo que ainda esta sendo escrito nao entra. Nunca.

O que este arquivo NAO faz: nao classifica semanticamente, nao cruza, nao promove nada.
Ele so responde "o que existe, de onde veio e o que da para provar sobre cada peca".

O QUE E UMA LINHA AQUI
------------------------
Um objeto de fala: um video do YouTube, um reel do Instagram, um episodio de podcast ou um
arquivo de midia auto-hospedada. A chave e (PLATFORM, EXTERNAL_ID), a mesma do dedupe do
`voz.py` — para que o mesmo objeto vindo por duas rotas nao vire dois.

CAMPOS QUE SO SAO PREENCHIDOS QUANDO DEMONSTRADOS
--------------------------------------------------
REGION, CROP, ISSUE e MOLECULE saem do vocabulario italiano declarado, aplicado ao texto
lido, e cada um vem com o TRECHO EXATO que o sustenta. Campo sem leitura fica NAO_SEI.

    PRESENCA LEXICAL NAO PROVA CONTEXTO AGRONOMICO.
    "pomodoro" numa nota de degustacao de azeite ja passou por aqui. Por isso cada marca
    carrega EVIDENCE_SPAN: 140 caracteres em volta da ocorrencia, para que quem le julgue.
"""
import json
import os
import re
import sys
import glob
import hashlib
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
SAIDA = os.path.join(SAMPLES, 'IT-SNAPSHOT-V1')
CAPTURA = '2026-09-03'
NAO_SEI = 'NAO_SEI'
# O snapshot e IMUTAVEL: a trilha de inteligencia le um arquivo com nome fixo e ele nao pode
# mudar por baixo dela. Lote novo produz VERSAO NOVA, e nunca sobrescreve a anterior.
VERSAO = os.environ.get('IT_INV_VERSAO') or 'V1'

import voz


def _sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()[:16]


def _fechado(p, minimo=120):
    """Um arquivo so e FECHADO se ninguem escreveu nele nos ultimos `minimo` segundos."""
    return os.path.exists(p) and (time.time() - os.stat(p).st_mtime) > minimo


def _trecho(texto, m, raio=140):
    i, j = max(0, m.start() - raio), min(len(texto), m.end() + raio)
    return re.sub(r'\s+', ' ', texto[i:j]).strip()


def marcas(texto, vocab, prefixo):
    """→ [{TERM, MATCHED, EVIDENCE_SPAN, COUNT}] com a prova de cada marca.

    Devolve TODAS as ocorrencias distintas, e nao a primeira, porque para inventariar
    o primeiro casamento e cegueira.

    NOTA 2026-09-05 (D1): esta funcao existia para compensar um desenho do `voz.py` que
    parava no primeiro casamento. Esse desenho acabou — `voz.resolver_crop` agora devolve
    CROP_ALL com evidencia por cultura, que e exatamente o que `marcas` ja fazia aqui.
    Ver docs/regras/POLITICA-CANONICA-DE-CROP.md. As duas continuam a existir porque
    respondem a perguntas diferentes: `marcas` inventaria termos em qualquer vocabulario;
    `resolver_crop` decide o CROP canonico do registro.
    """
    achados = []
    for nome, rx in vocab.items():
        ms = list(re.finditer(rx, texto or '', re.I))
        if not ms:
            continue
        achados.append({'TERM': prefixo + ':' + nome,
                        'MATCHED': texto[ms[0].start():ms[0].end()],
                        'COUNT': len(ms),
                        'EVIDENCE_SPAN': _trecho(texto, ms[0])})
    return achados


# ── NUMEROS DITOS EM VOZ ALTA ─────────────────────────────────────────────────
# O CICLO 1 pede "numeros/medidas citados", e essa e a unica parte da leitura semantica que
# se faz sem julgamento: ou o numero esta na fala, ou nao esta.
#
#     UM NUMERO DITO E O QUE SEPARA "houve pressao" de "10 colonie vitali su 100 organi".
#
# O que NAO se faz aqui e interpretar o numero. `30%` pode ser incidencia, perda, dose ou
# umidade — e decidir qual e leitura de contexto, que e trabalho da camada de cima. Por isso
# cada numero sai com 120 caracteres de contexto em volta, e com o TIPO APARENTE declarado
# como aparente, nunca como fato.
NUMERO = [
    ('PERCENTUAL', r'\b\d{1,3}(?:[.,]\d+)?\s?%'),
    ('DOSE_POR_HECTARE', r'\b\d+(?:[.,]\d+)?\s?(?:l|kg|g|ml|cc)\s?(?:/|per\s+|a\s+)?ha\b'),
    ('CONCENTRACAO', r'\b\d+(?:[.,]\d+)?\s?(?:g|mg|kg|l|ml)\s?/\s?(?:l|hl|kg|ha)\b'),
    ('TEMPERATURA', r'\b\d{1,2}(?:[.,]\d+)?\s?(?:gradi|°\s?c)\b'),
    ('SOGLIA_LIMIAR', r'soglia[^.]{0,80}?\d+|\d+[^.]{0,40}?\bsoglia\b'),
    ('CONTAGEM_POR_UNIDADE', r'\b\d+\s+(?:individui|adulti|larve|uova|colonie|catture|trappole|piante|organi)\b'),
    ('ANO', r'\b(?:19|20)\d{2}\b'),
    ('NUMERO_DE_INTERVENCOES', r'\b(?:massimo|max\.?|fino a)\s+\d+\s+(?:interventi|trattamenti|applicazioni)'),
    ('SUPERFICIE', r'\b\d+(?:[.,]\d+)?\s?(?:ettari|ha)\b'),
]


def numeros(texto, teto=40):
    """→ [{KIND_APPARENT, MATCHED, EVIDENCE_SPAN}] com o contexto de cada numero dito."""
    achados, vistos = [], set()
    for tipo, rx in NUMERO:
        for m in re.finditer(rx, texto or '', re.I):
            chave = (tipo, m.group(0).lower())
            if chave in vistos:
                continue
            vistos.add(chave)
            achados.append({'KIND_APPARENT': tipo, 'MATCHED': m.group(0),
                            'EVIDENCE_SPAN': _trecho(texto, m, 120)})
            if len(achados) >= teto:
                return achados
    return achados


# ── OS LOTES FECHADOS, E COMO LER CADA UM ─────────────────────────────────────
def _le(caminho):
    if not _fechado(caminho):
        return None, 'NAO_FECHADO_OU_AUSENTE'
    with open(caminho, encoding='utf-8') as f:
        return json.load(f), None


def objetos():
    """Uma linha por objeto de fala, de todos os lotes fechados."""
    linhas, fontes_lidas, recusados = [], [], []

    def add(caminho, gerador):
        d, why = _le(os.path.join(SAMPLES, caminho))
        if d is None:
            recusados.append({'FILE': caminho, 'WHY': why})
            return
        n = 0
        for reg in gerador(d):
            linhas.append(reg); n += 1
        fontes_lidas.append({'FILE': caminho, 'SHA256_16': _sha(os.path.join(SAMPLES, caminho)),
                             'OBJECTS': n})

    def base(**kw):
        r = {'PLATFORM': NAO_SEI, 'EXTERNAL_ID': NAO_SEI, 'URL': NAO_SEI, 'TITLE': NAO_SEI,
             'ORGANISATION': NAO_SEI, 'DECLARED_ROLE': NAO_SEI, 'PUBLICATION_DATE': NAO_SEI,
             'DURATION_S': NAO_SEI, 'LANGUAGE': 'it', 'LANGUAGE_LAW': 'declarado, nunca detectado',
             'CAPTION_SOURCE': NAO_SEI, 'TRANSCRIPT_CHARS': 0, 'DESCRIPTION_CHARS': 0,
             'TEXT': '', 'DESCRIPTION': '', 'BATCH': NAO_SEI}
        r.update(kw)
        return r

    # YouTube — falas por arquivo individual (o indice traz o caminho)
    def _yt(d):
        for it in d.get('ITEMS', []):
            if it.get('STATE') != 'OK':
                continue
            fp = os.path.join(ROOT, it.get('FALA_PATH', ''))
            texto = ''
            if it.get('FALA_PATH') and _fechado(fp):
                with open(fp, encoding='utf-8') as f:
                    texto = (json.load(f) or {}).get('TRANSCRIPT') or ''
            yield base(PLATFORM='YOUTUBE', EXTERNAL_ID=it['EXTERNAL_ID'], URL=it.get('URL'),
                       TITLE=it.get('TITLE'), ORGANISATION=it.get('CHANNEL_NAME'),
                       PUBLICATION_DATE=it.get('PUBLICATION_DATE'),
                       CAPTION_SOURCE=it.get('CAPTION_SOURCE'), TEXT=texto,
                       TRANSCRIPT_CHARS=len(texto), BATCH='IT-VIDEO-V1')
    add('IT-VIDEO-V1/IT-VIDEO-FALAS-V1.json', _yt)

    # Audio V1 — Agricast e Vita in Campagna
    def _a1(d):
        for r in d.get('RECORDS', []):
            t = r.get('TRANSCRIPT') or ''
            yield base(PLATFORM='SPREAKER', EXTERNAL_ID=str(r.get('EXTERNAL_ID') or r.get('ID')
                                                            or r.get('TITLE'))[:64],
                       URL=r.get('URL', NAO_SEI), TITLE=r.get('TITLE'),
                       ORGANISATION=r.get('ORIGIN') or r.get('SHOW') or NAO_SEI,
                       PUBLICATION_DATE=r.get('PUBLICATION_DATE', NAO_SEI),
                       DURATION_S=r.get('DURATION_S', NAO_SEI),
                       CAPTION_SOURCE='SINTONIA_WHISPER_LOCAL', TEXT=t, TRANSCRIPT_CHARS=len(t),
                       DESCRIPTION=r.get('DESCRIPTION') or '',
                       DESCRIPTION_CHARS=len(r.get('DESCRIPTION') or ''),
                       BATCH='IT-VOZ-AUDIO-V1')
    add('IT-VOZ-AUDIO-V1/IT-VOZ-AUDIO-TRANSCRICOES-V1.json', _a1)

    # Audio V2 — rota Spreaker por janela, e rota de midia local
    def _a2(d):
        for r in d.get('RECORDS', []):
            if r.get('TRANSCRIPT_STATE') not in ('OK', 'REQUESTED_EMPTY'):
                continue
            t = r.get('TRANSCRIPT') or ''
            yield base(PLATFORM=r.get('PLATFORM', 'SPREAKER'), EXTERNAL_ID=str(r['EXTERNAL_ID']),
                       URL=r.get('PAGE_URL') or r.get('MEDIA_URL') or NAO_SEI,
                       TITLE=r.get('TITLE'), ORGANISATION=r.get('ORIGIN'),
                       DECLARED_ROLE=r.get('DECLARED_ROLE', NAO_SEI),
                       PUBLICATION_DATE=r.get('PUBLICATION_DATE'),
                       DURATION_S=r.get('DURATION_S'), CAPTION_SOURCE=r.get('CAPTION_SOURCE'),
                       TEXT=t, TRANSCRIPT_CHARS=len(t),
                       DESCRIPTION=r.get('DESCRIPTION') or '',
                       DESCRIPTION_CHARS=len(r.get('DESCRIPTION') or ''),
                       BATCH=d['DATASET'])
    add('IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-TRANSCRICOES-V2.json', _a2)
    add('IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-LOCAIS-V2.json', _a2)

    # Convegno — bilanci fitosanitari e Giornate Fitopatologiche, uma fala por arquivo
    def _cv(d):
        for it in d.get('ITEMS', []):
            vid = it.get('external_id')
            fp = os.path.join(SAMPLES, 'IT-CONVEGNO-V1', 'falas', '%s.json' % vid)
            if not _fechado(fp):
                continue
            with open(fp, encoding='utf-8') as f:
                fala = json.load(f)
            t = fala.get('TRANSCRIPT') or ''
            yield base(PLATFORM='YOUTUBE', EXTERNAL_ID=vid, URL=fala.get('URL'),
                       TITLE=fala.get('TITLE'), ORGANISATION=fala.get('CHANNEL_NAME'),
                       DECLARED_ROLE=fala.get('DECLARED_ROLE') or NAO_SEI,
                       PUBLICATION_DATE=fala.get('PUBLICATION_DATE'),
                       DURATION_S=fala.get('DURATION_S') or NAO_SEI,
                       CAPTION_SOURCE=fala.get('CAPTION_SOURCE'), TEXT=t,
                       TRANSCRIPT_CHARS=len(t), BATCH='IT-CONVEGNO-V1')
    if VERSAO != 'V1':
        add('IT-CONVEGNO-V1/IT-CONVEGNO-V1.json', _cv)

    # Instagram — tres lotes
    def _ig(d):
        for r in d.get('ITEMS', []):
            t = r.get('TRANSCRIPT') or ''
            yield base(PLATFORM='INSTAGRAM', EXTERNAL_ID=r['SHORTCODE'], URL=r.get('URL'),
                       TITLE=(r.get('CAPTION') or '')[:120],
                       ORGANISATION=r.get('ORGANISATION') or r.get('HANDLE'),
                       DECLARED_ROLE=r.get('PAGE_ROLE', NAO_SEI),
                       PUBLICATION_DATE=r.get('PUBLICATION_DATE'),
                       DURATION_S=r.get('VIDEO_DURATION_S', NAO_SEI),
                       CAPTION_SOURCE=r.get('CAPTION_SOURCE'), TEXT=t, TRANSCRIPT_CHARS=len(t),
                       DESCRIPTION=r.get('CAPTION') or '',
                       DESCRIPTION_CHARS=len(r.get('CAPTION') or ''),
                       BATCH=d['DATASET'])
    for v in ('V1', 'V2', 'V3'):
        add('IT-INSTAGRAM-%s/IT-INSTAGRAM-TRANSCRICOES-%s.json' % (v, v), _ig)

    # ── dedupe por (PLATFORM, EXTERNAL_ID), a mesma chave do voz.py ──
    visto, unicos, duplicados = {}, [], []
    for r in linhas:
        k = (r['PLATFORM'], r['EXTERNAL_ID'])
        if k in visto:
            duplicados.append({'KEY': '%s|%s' % k, 'KEPT_FROM': visto[k], 'ALSO_IN': r['BATCH']})
            continue
        visto[k] = r['BATCH']
        unicos.append(r)

    # ── marcas com prova ──
    for r in unicos:
        campo_fala = r['TEXT']
        campo_desc = r['DESCRIPTION'] + ' ' + (r['TITLE'] or '')
        r['CROP_MARKS_IN_SPEECH'] = marcas(campo_fala, voz.VOCAB_CROP_IT, 'CROP')
        r['ISSUE_MARKS_IN_SPEECH'] = marcas(campo_fala, voz.VOCAB_ISSUE_IT, 'ISSUE')
        r['MOLECULE_MARKS_IN_SPEECH'] = marcas(campo_fala, voz.VOCAB_MOLECULE_IT, 'MOLECULE')
        r['REGION_MARKS_IN_SPEECH'] = marcas(campo_fala, voz.VOCAB_LUGAR_IT, 'REGION')
        r['CROP_MARKS_IN_DESCRIPTION'] = marcas(campo_desc, voz.VOCAB_CROP_IT, 'CROP')
        r['ISSUE_MARKS_IN_DESCRIPTION'] = marcas(campo_desc, voz.VOCAB_ISSUE_IT, 'ISSUE')
        mols = [m['TERM'].split(':', 1)[1] for m in r['MOLECULE_MARKS_IN_SPEECH']]
        r['MOLECULE_ADAMA'] = sorted(m for m in mols if m in voz.MOLECULAS_ADAMA_IT) or None
        r['MOLECULE_NOT_ADAMA'] = sorted(m for m in mols if m not in voz.MOLECULAS_ADAMA_IT) or None
        so_fala = {m['TERM'] for m in r['ISSUE_MARKS_IN_SPEECH']} - {
            m['TERM'] for m in r['ISSUE_MARKS_IN_DESCRIPTION']}
        r['ISSUE_ONLY_IN_SPEECH'] = sorted(so_fala) or None
        r['NUMBERS_IN_SPEECH'] = numeros(campo_fala)
        r['NUMBERS_LAW'] = ('KIND_APPARENT e APARENTE. "30%" pode ser incidencia, perda, dose '
                            'ou umidade, e decidir qual e leitura de contexto — por isso cada '
                            'numero vem com o trecho em volta.')
        # a qualidade da evidencia sai do que existe, e nunca de quanto parece bom
        tem_alvo = bool(r['ISSUE_MARKS_IN_SPEECH'])
        tem_cult = bool(r['CROP_MARKS_IN_SPEECH'])
        tem_reg = bool(r['REGION_MARKS_IN_SPEECH'])
        tem_data = bool(r['PUBLICATION_DATE']) and r['PUBLICATION_DATE'] != NAO_SEI
        r['EVIDENCE_COMPLETENESS'] = {
            'HAS_SPEECH': r['TRANSCRIPT_CHARS'] > 200, 'HAS_CROP': tem_cult, 'HAS_ISSUE': tem_alvo,
            'HAS_REGION': tem_reg, 'HAS_DATE': tem_data,
            'SCORE_OF_5': sum([r['TRANSCRIPT_CHARS'] > 200, tem_cult, tem_alvo, tem_reg, tem_data])}
        r['CAPTION_TO_SPEECH_RATIO'] = (
            '1:%d' % round(r['TRANSCRIPT_CHARS'] / r['DESCRIPTION_CHARS'])
            if r['DESCRIPTION_CHARS'] else ('0:%d' % r['TRANSCRIPT_CHARS']))
        r.pop('TEXT', None)  # o texto fica no lote de origem; aqui vive o INVENTARIO
    return unicos, fontes_lidas, recusados, duplicados


def escrever():
    os.makedirs(SAIDA, exist_ok=True)
    linhas, fontes, recusados, dups = objetos()
    from collections import Counter
    com_fala = [r for r in linhas if r['EVIDENCE_COMPLETENESS']['HAS_SPEECH']]
    corpo = {
        'DATASET': 'IT-INVENTARIO-FALA-%s' % VERSAO,
        'LAYER': 'SPEECH_INVENTORY_ITALY',
        'COUNTRY': 'IT',
        'SOURCE': ('derivado: uma linha por objeto de fala, montada a partir dos lotes FECHADOS '
                   'listados em READ_FROM. Nenhuma coleta foi feita aqui e nenhum arquivo da '
                   'trilha de coleta foi tocado.'),
        'SOURCE_ID': 'IT-INVENTARIO-FALA-%s' % VERSAO,
        'CAPTURED_AT': CAPTURA,
        'CLOSED_FILE_RULE': ('so entra arquivo versionado e sem escrita nos ultimos 120 s. '
                             'Arquivo em escrita fica em REFUSED_NOT_CLOSED e NAO e lido.'),
        'DEDUPE_KEY': '(PLATFORM, EXTERNAL_ID) — a mesma chave do dedupe do voz.py',
        'MARK_LAW': ('PRESENCA LEXICAL NAO PROVA CONTEXTO AGRONOMICO. Cada marca traz '
                     'EVIDENCE_SPAN com 140 caracteres em volta da ocorrencia, para que quem le '
                     'julgue o contexto em vez de confiar na contagem.'),
        'MOLECULE_LAW': 'MOLECULA MARCADA != MOLECULA ADAMA (ver FIX-05)',
        'READ_FROM': fontes,
        'REFUSED_NOT_CLOSED': recusados,
        'DUPLICATES_COLLAPSED': dups,
        'OBJECTS': len(linhas),
        'OBJECTS_WITH_SPEECH': len(com_fala),
        'SPEECH_CHARS_TOTAL': sum(r['TRANSCRIPT_CHARS'] for r in linhas),
        'BY_PLATFORM': dict(Counter(r['PLATFORM'] for r in linhas)),
        'BY_BATCH': dict(Counter(r['BATCH'] for r in linhas)),
        'BY_EVIDENCE_SCORE': dict(Counter(r['EVIDENCE_COMPLETENESS']['SCORE_OF_5'] for r in linhas)),
        'WITH_ISSUE_IN_SPEECH': sum(1 for r in linhas if r['ISSUE_MARKS_IN_SPEECH']),
        'WITH_ISSUE_ONLY_IN_SPEECH': sum(1 for r in linhas if r['ISSUE_ONLY_IN_SPEECH']),
        'WITH_ADAMA_MOLECULE': sum(1 for r in linhas if r['MOLECULE_ADAMA']),
        'WITH_NON_ADAMA_MOLECULE': sum(1 for r in linhas if r['MOLECULE_NOT_ADAMA']),
        'ITEMS': linhas,
    }
    p = os.path.join(SAIDA, 'IT-INVENTARIO-FALA-%s.json' % VERSAO)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return p, corpo


if __name__ == '__main__':
    p, c = escrever()
    print('escrito: %s' % os.path.relpath(p, ROOT))
    print()
    for k in ('OBJECTS', 'OBJECTS_WITH_SPEECH', 'SPEECH_CHARS_TOTAL', 'BY_PLATFORM', 'BY_BATCH',
              'BY_EVIDENCE_SCORE', 'WITH_ISSUE_IN_SPEECH', 'WITH_ISSUE_ONLY_IN_SPEECH',
              'WITH_ADAMA_MOLECULE', 'WITH_NON_ADAMA_MOLECULE'):
        print('%-28s %s' % (k, c[k]))
    if c['REFUSED_NOT_CLOSED']:
        print('%-28s %s' % ('RECUSADOS (em escrita)', c['REFUSED_NOT_CLOSED']))
    if c['DUPLICATES_COLLAPSED']:
        print('%-28s %d' % ('DUPLICATAS COLAPSADAS', len(c['DUPLICATES_COLLAPSED'])))
