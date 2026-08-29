#!/usr/bin/env python3
"""
NORMALIZADOR DA CAMADA DE VOZ — o contrato de campos da REGRA DE COLETA EXTERNA.

A regra fixa a lista de campos por vídeo. Este arquivo é o único lugar onde essa lista
vira código, para que o próximo país não a redigite e não a encolha em silêncio.

Três decisões que este arquivo carrega:

1. CAMPO AUSENTE VIRA `NÃO SEI`, NUNCA SOME.
   Um campo que desaparece do registro é indistinguível de um campo que nunca existiu.
   `NAO_SEI` é um valor; a ausência da chave não é.

2. ORIGIN ≠ CONTENT.
   157 canais publicaram 252 vídeos. São 157 ORIGENS e 252 CONTEÚDOS, e as duas contagens
   nunca podem ser somadas nem trocadas.

3. DEDUPE É ESTRUTURAL.
   A chave é `PLATFORM + EXTERNAL_ID`. Dois vídeos com o mesmo título são dois vídeos.
   Texto igual nunca colapsa registro.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

NAO_SEI = 'NÃO SEI'

# A lista da regra, em ordem. Todo registro normalizado tem exatamente estas chaves.
CAMPOS_VIDEO = [
    'SOURCE_ID', 'ORIGIN_ID', 'CHANNEL_ID', 'CONTENT_ID', 'PLATFORM', 'EXTERNAL_ID', 'URL',
    'TITLE', 'DESCRIPTION', 'PUBLICATION_DATE', 'CAPTURE_DATE', 'CHANNEL_NAME',
    'DECLARED_AUTHOR', 'DECLARED_ROLE', 'ORGANIZATION', 'COUNTRY', 'LANGUAGE', 'DURATION',
    'VIEWS', 'LIKES', 'COMMENTS_COUNT', 'TRANSCRIPT', 'TRANSCRIPT_LANGUAGE', 'CAPTION_SOURCE',
    'CROP', 'ISSUE', 'PRODUCT', 'MOLECULE', 'FACT_LOCATION', 'SOURCE_LOCATION',
    'RUN_ID', 'EVIDENCE_PATH',
]

# Tipos de conteúdo da regra. `OTHER` é um destino legítimo, não um fracasso de
# classificação — e `NAO_SEI` continua sendo diferente de `OTHER`.
TIPOS_VIDEO = [
    'RESEARCH_TALK', 'TECHNICAL_WEBINAR', 'FIELD_DAY', 'FIELD_OBSERVATION',
    'COOPERATIVE_CONTENT', 'TECHNICAL_ADVISER', 'PRODUCER_VOICE', 'COMPETITOR_TECHNICAL',
    'PRODUCT_DEMO', 'CONFERENCE', 'MEDIA', 'PROMOTIONAL', 'OTHER',
]

# Origem do conteúdo. Uma release republicada em quatro lugares não é quatro evidências.
ORIGINALIDADE = ['ORIGINAL', 'RESHARE', 'SYNDICATED', 'UNKNOWN']

ESTADOS_DE_FONTE = ['PROVED', 'PARTIAL', 'NOT_REACHED', 'NOT_TESTED', 'FAILED_WITH_REASON',
                    'NAO_SEI']


def registro_vazio():
    """Todo campo da regra presente, todo valor em NÃO SEI."""
    return {c: NAO_SEI for c in CAMPOS_VIDEO}


def duracao_em_segundos(hhmmss):
    """'01:12:30' -> 4350. Devolve None quando o formato não é reconhecido — nunca 0,
    porque 0 segundos é uma afirmação e o desconhecido não é."""
    if not isinstance(hhmmss, str):
        return None
    partes = hhmmss.strip().split(':')
    if not all(p.isdigit() for p in partes) or not 1 <= len(partes) <= 3:
        return None
    s = 0
    for p in partes:
        s = s * 60 + int(p)
    return s


def chave_de_dedupe(reg):
    """Identidade estrutural. Nunca o texto."""
    return (reg['PLATFORM'], reg['EXTERNAL_ID'])


def dedupe(registros):
    """Colapsa por PLATFORM+EXTERNAL_ID e devolve (únicos, n_colapsados)."""
    vistos, saida = set(), []
    for r in registros:
        k = chave_de_dedupe(r)
        if k in vistos:
            continue
        vistos.add(k)
        saida.append(r)
    return saida, len(registros) - len(saida)


def normalizar_video(bruto, *, source_id, run_id, capture_date, papel_por_canal=None,
                     transcricoes=None, evidence_path=None):
    """Um item cru do coletor de vídeo -> o registro declarado pela regra.

    `papel_por_canal` mapeia CHANNEL_ID -> papel DECLARADO pelo canal. O papel nunca é
    inferido do vídeo: a regra proíbe, e um vídeo técnico num canal promocional continua
    sendo um canal promocional.
    """
    r = registro_vazio()
    vid = bruto.get('id')
    canal = bruto.get('channelId')

    r['SOURCE_ID'] = source_id
    r['PLATFORM'] = 'YOUTUBE'
    r['EXTERNAL_ID'] = vid or NAO_SEI
    r['CONTENT_ID'] = f'YOUTUBE:{vid}' if vid else NAO_SEI
    # A ORIGEM é o canal. O vídeo é conteúdo dela. Nunca o contrário.
    r['CHANNEL_ID'] = canal or NAO_SEI
    r['ORIGIN_ID'] = f'YOUTUBE:{canal}' if canal else NAO_SEI
    r['URL'] = bruto.get('url') or NAO_SEI
    r['TITLE'] = bruto.get('title') or NAO_SEI
    r['DESCRIPTION'] = bruto.get('text') or NAO_SEI
    r['PUBLICATION_DATE'] = (bruto.get('date') or NAO_SEI)[:10] if bruto.get('date') else NAO_SEI
    r['CAPTURE_DATE'] = capture_date
    r['CHANNEL_NAME'] = bruto.get('channelName') or NAO_SEI
    # DECLARED_AUTHOR é o canal, que é quem publica. Uma pessoa que aparece no vídeo não é
    # o autor do registro — e descobrir quem aparece exigiria ler o conteúdo, o que a
    # regra proíbe como fonte de identidade.
    r['DECLARED_AUTHOR'] = bruto.get('channelName') or NAO_SEI
    if papel_por_canal and canal in papel_por_canal:
        r['DECLARED_ROLE'] = papel_por_canal[canal]
    # ORGANIZATION, COUNTRY e LANGUAGE não são declarados pelo item de vídeo desta rota.
    # Ficam em NÃO SEI até que uma segunda camada os resolva.
    r['DURATION'] = duracao_em_segundos(bruto.get('duration')) or NAO_SEI
    for campo, chave in (('VIEWS', 'viewCount'), ('LIKES', 'likes'),
                         ('COMMENTS_COUNT', 'commentsCount')):
        v = bruto.get(chave)
        r[campo] = v if isinstance(v, int) else NAO_SEI

    t = (transcricoes or {}).get(bruto.get('url')) if transcricoes else None
    if t and t.get('transcript'):
        r['TRANSCRIPT'] = t['transcript']
        r['TRANSCRIPT_LANGUAGE'] = t.get('language', NAO_SEI)
        r['CAPTION_SOURCE'] = t.get('caption_source', NAO_SEI)
    elif t is not None:
        # Transcrição pedida e vazia. Isso é FAILED, não "vídeo sem conteúdo técnico".
        r['TRANSCRIPT'] = NAO_SEI
        r['CAPTION_SOURCE'] = 'REQUESTED_EMPTY'

    r['SOURCE_LOCATION'] = 'plataforma global'
    r['RUN_ID'] = run_id
    if evidence_path:
        r['EVIDENCE_PATH'] = evidence_path
    return r


# CROP e ISSUE saem de vocabulário declarado, não de leitura livre do texto.
VOCAB_CROP = {'OLIVE': r'\boliv|olivar|aceituna|aceite de oliva|almazara|\bolea\b'}
VOCAB_ISSUE = {
    'REPILO': r'repilo|venturia|spilocaea',
    'XYLELLA': r'xylella',
    'VERTICILLIUM': r'verticil',
    'MOSCA_DEL_OLIVO': r'mosca del olivo|bactrocera',
    'PRAYS': r'\bprays\b|polilla del olivo',
    'TUBERCULOSIS': r'tuberculosis del olivo|pseudomonas savastanoi',
}


def marcar_assunto(reg):
    """CROP e ISSUE a partir de título e descrição, com vocabulário declarado.

    Isto é assunto, não identidade. Marcar o tema de um texto é leitura de conteúdo e é
    permitido; deduzir QUEM fala a partir do mesmo texto não é.
    """
    campo = ' '.join(str(reg.get(k) or '') for k in ('TITLE', 'DESCRIPTION'))
    for nome, rx in VOCAB_CROP.items():
        if re.search(rx, campo, re.I):
            reg['CROP'] = nome
            break
    achados = [n for n, rx in VOCAB_ISSUE.items() if re.search(rx, campo, re.I)]
    if len(achados) == 1:
        reg['ISSUE'] = achados[0]
    elif len(achados) > 1:
        reg['ISSUE'] = 'AMBIGUOUS:' + '+'.join(sorted(achados))
    return reg


# MOLECULE sai de vocabulário de substância ativa declarado, nunca de marca comercial.
VOCAB_MOLECULE = {
    'COBRE': r'\bcobre\b|oxicloruro de cobre|hidróxido de cobre|caldo bordel',
    'DODINA': r'\bdodina\b',
    'TREBUCONAZOL': r'tebuconazol',
    'DIFENOCONAZOL': r'difenoconazol',
    'MANCOZEB': r'mancozeb',
    'KRESOXIM': r'kresoxim',
    'AZOXISTROBINA': r'azoxistrobina',
    'PIRACLOSTROBINA': r'piraclostrobina',
    'DIMETOATO': r'dimetoato',
    'DELTAMETRINA': r'deltametrina',
    'ESPINOSAD': r'spinosad|espinosad',
    'CAOLIN': r'caol[ií]n',
}

# FACT_LOCATION só quando o próprio texto NOMEIA o lugar. Nunca por idioma, nunca pelo país
# da plataforma, nunca pelo país do canal — SOURCE_LOCATION e FACT_LOCATION são coisas
# diferentes e é justamente aqui que se confundem.
VOCAB_LUGAR = {
    'ES-Jaén': r'\bja[eé]n\b', 'ES-Córdoba': r'\bc[oó]rdoba\b', 'ES-Sevilla': r'\bsevilla\b',
    'ES-Granada': r'\bgranada\b', 'ES-Málaga': r'\bm[aá]laga\b', 'ES-Huelva': r'\bhuelva\b',
    'ES-Cádiz': r'\bc[aá]diz\b', 'ES-Almería': r'\balmer[ií]a\b',
    'ES-Andalucía': r'\bandaluc[ií]a\b', 'ES-Extremadura': r'\bextremadura\b',
    'ES-Castilla-La Mancha': r'castilla[- ]la mancha', 'ES-Cataluña': r'catalu[ñn]a',
    'ES': r'\bespa[ñn]a\b',
}


def marcar_molecula_e_lugar(reg):
    """MOLECULE e FACT_LOCATION a partir do texto declarado, com vocabulário fechado.

    Quando o texto nomeia mais de um lugar, o registro recebe todos — não se escolhe um.
    Um vídeo que fala de Jaén e Córdoba fala das duas.
    """
    campo = ' '.join(str(reg.get(k) or '') for k in ('TITLE', 'DESCRIPTION'))
    mols = sorted(n for n, rx in VOCAB_MOLECULE.items() if re.search(rx, campo, re.I))
    if mols:
        reg['MOLECULE'] = '+'.join(mols)
    lugares = sorted(n for n, rx in VOCAB_LUGAR.items() if re.search(rx, campo, re.I))
    # 'ES' sozinho é redundante quando há província: a província já implica o país.
    if len(lugares) > 1 and 'ES' in lugares:
        lugares.remove('ES')
    if lugares:
        reg['FACT_LOCATION'] = '+'.join(lugares)
        reg['FACT_LOCATION_RULE'] = 'NOMEADO_NO_TEXTO'
    return reg


def cobertura(registros):
    """Quantos registros declaram cada campo. É isto que impede a lista de encolher."""
    total = len(registros)
    out = {}
    for c in CAMPOS_VIDEO:
        n = sum(1 for r in registros if r.get(c) not in (NAO_SEI, None, ''))
        out[c] = {'DECLARED': n, 'TOTAL': total,
                  'PCT': round(100.0 * n / total, 1) if total else None}
    return out


if __name__ == '__main__':
    import sys
    print('CAMPOS_VIDEO  :', len(CAMPOS_VIDEO))
    print('TIPOS_VIDEO   :', len(TIPOS_VIDEO))
    print('ORIGINALIDADE :', ORIGINALIDADE)
    print('ESTADOS       :', ESTADOS_DE_FONTE)
    if '--campos' in sys.argv:
        for c in CAMPOS_VIDEO:
            print(' ', c)
