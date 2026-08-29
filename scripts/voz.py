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


# Marcador de registro SEM identidade estrutural. Não é uma identidade: é a declaração de
# que não há nenhuma. Ver `chave_de_dedupe`.
SEM_ID_ESTRUTURAL = '__SEM_ID_ESTRUTURAL__'


def tem_id_estrutural(reg):
    """O registro traz um EXTERNAL_ID de verdade?

    `NÃO SEI`, vazio e None NÃO são identificadores — são a ausência de um.
    """
    v = reg.get('EXTERNAL_ID')
    if v is None:
        return False
    v = str(v).strip()
    return bool(v) and v != NAO_SEI


def chave_de_dedupe(reg, posicao=None):
    """Identidade estrutural. Nunca o texto — e nunca a ausência de identidade.

    O defeito medido na MISSÃO 10C: quando a rota não devolve `id`, `normalizar_video`
    grava `EXTERNAL_ID = NÃO SEI`. Com a chave antiga `(PLATFORM, EXTERNAL_ID)`, TODOS os
    registros sem id compartilhavam a chave `('YOUTUBE', 'NÃO SEI')` e colapsavam num só.
    Três vídeos distintos viravam um, com `DUPLICATE_COUNT = 2`, a aritmética fechava e o
    portão dizia PROVED enquanto dois vídeos reais desapareciam.

    `NÃO SEI` é ausência de identidade, e **ausência de identidade não é identidade
    compartilhada**. Dois registros que não sabemos identificar não são o mesmo registro:
    são dois registros que não sabemos identificar. Sem id, cada um é único por posição e
    nunca colapsa — a incerteza preserva conteúdo em vez de destruí-lo.
    """
    if tem_id_estrutural(reg):
        return (reg['PLATFORM'], str(reg['EXTERNAL_ID']).strip())
    return (reg.get('PLATFORM'), SEM_ID_ESTRUTURAL, posicao)


def dedupe(registros):
    """Colapsa por PLATFORM+EXTERNAL_ID e devolve (únicos, n_colapsados).

    Registro sem identidade estrutural NUNCA colapsa — ver `chave_de_dedupe`.
    """
    vistos, saida = set(), []
    for i, r in enumerate(registros):
        k = chave_de_dedupe(r, i)
        if k in vistos:
            continue
        vistos.add(k)
        saida.append(r)
    return saida, len(registros) - len(saida)


def sem_id_estrutural(registros):
    """Quantos registros entraram sem identificador. Nunca pode ficar implícito."""
    return [r for r in registros if not tem_id_estrutural(r)]


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


# ---------------------------------------------------------------- tipo de conteúdo
# A classificação lê o TEXTO do vídeo, e isso é legítimo: dizer o que a peça É não é o
# mesmo que dizer QUEM fala. O papel da origem continua vindo do canal, nunca daqui.
#
# `NÃO SEI` e `OTHER` são estados diferentes e a diferença importa:
#   NÃO SEI = não há texto suficiente para classificar
#   OTHER   = há texto, e ele não corresponde a nenhum dos 12 tipos nomeados
VOCAB_TIPO = [
    ('FIELD_DAY',           r'd[ií]a de campo|jornada de campo|demostraci[oó]n en campo|visita t[eé]cnica a|ensayo de campo'),
    ('CONFERENCE',          r'\bcongreso\b|\bsimposi\w*|\bsymposium\b|\bjornada t[eé]cnica|\bjornadas t[eé]cnicas|\bponencia\b|mesa redonda|\bclausura\b|\binauguraci[oó]n\b.{0,30}(congreso|simposi|symposium|jornada)'),
    ('TECHNICAL_WEBINAR',   r'\bwebinar\b|\bseminario\b|\bmasterclass\b|\bcurso\b|\bformaci[oó]n\b.{0,20}(t[eé]cnica|online)|\bcharla t[eé]cnica'),
    ('RESEARCH_TALK',       r'\binvestigador[ao]?\b|grupo de investigaci|\bsecuencian\b|\bestudio cient[ií]fico|resultados? del ensayo|\btesis\b|proyecto de investigaci'),
    ('PRODUCT_DEMO',        r'demostraci[oó]n de (la |el )?(m[aá]quina|equipo|producto)|\ben acci[oó]n\b|prueba de (m[aá]quina|equipo)|\bunboxing\b'),
    ('COOPERATIVE_CONTENT', r'\bcooperativa\b|\bs\.?\s?coop\b|\balmazara\b|denominaci[oó]n de origen'),
    ('FIELD_OBSERVATION',   r'\ben mi (finca|olivar|parcela)\b|\bos ense[ñn]o\b|estado del (olivar|cultivo)|\bvisita(mos)? la parcela|\d+[ºª] visita'),
    ('PRODUCER_VOICE',      r'\bagricultor\b|\bolivarero\b|mi experiencia|llevo \d+ a[ñn]os'),
    ('MEDIA',               r'\bnoticias?\b|\binformativo\b|\breportaje\b|\bentrevista\b|\btelediario\b|\bcanal sur\b|gabinete de comunicaci'),
    ('PROMOTIONAL',         r'\bpublicidad\b|\banuncio\b|\bspot\b|\boferta\b|\bs[ií]guenos\b|\bsuscr[ií]bete\b|\bpromoci[oó]n\b'),
]

# PRECEDÊNCIA DECLARADA, do mais específico para o mais genérico.
# Um vídeo pode ser legitimamente duas coisas — a apresentação de um investigador DENTRO
# de um congresso é as duas. Empate não vira `OTHER` nem se resolve por ordem acidental de
# regex: o primário sai desta lista publicada e os demais ficam visíveis em
# `CONTENT_TYPE_ALL`, para que a escolha seja auditável.
PRECEDENCIA_TIPO = [
    'FIELD_DAY', 'CONFERENCE', 'TECHNICAL_WEBINAR', 'RESEARCH_TALK', 'PRODUCT_DEMO',
    'COOPERATIVE_CONTENT', 'FIELD_OBSERVATION', 'PRODUCER_VOICE', 'COMPETITOR_TECHNICAL',
    'TECHNICAL_ADVISER', 'MEDIA', 'PROMOTIONAL',
]

# Papel do canal que tipifica a peça quando o texto não decide. Isto NÃO é inferir papel a
# partir do conteúdo: é o contrário — usar o papel JÁ DECLARADO pelo canal.
TIPO_POR_PAPEL = {
    'TECHNICAL_MEDIA': 'MEDIA',
    'COOPERATIVE_OR_ASSOCIATION': 'COOPERATIVE_CONTENT',
}


def classificar_tipo(reg):
    """Devolve (CONTENT_TYPE, todos_os_tipos, evidência).

    `NÃO SEI` e `OTHER` continuam sendo coisas diferentes:
      NÃO SEI = não há texto declarado suficiente para classificar
      OTHER   = há texto, e ele não corresponde a nenhum dos tipos nomeados
    """
    campo = ' '.join(str(reg.get(k) or '') for k in ('TITLE', 'DESCRIPTION'))
    campo = campo.replace(NAO_SEI, ' ').strip()
    # Menos de tres palavras nao estabelece TIPO. "Verticillium" e um topico, nao um tipo
    # de peca — e contar caracteres seria numero magico onde o criterio real e outro.
    palavras = [w for w in re.split(r'\W+', campo) if len(w) > 1]
    if len(palavras) < 3:
        return NAO_SEI, [], 'texto declarado com %d palavra(s) — insuficiente para tipificar' % len(palavras)
    achados = {}
    for n, rx in VOCAB_TIPO:
        m = re.search(rx, campo, re.I)
        if m:
            achados[n] = m.group(0)
    if achados:
        primario = next(t for t in PRECEDENCIA_TIPO if t in achados)
        ev = 'texto: "%s"' % achados[primario]
        if len(achados) > 1:
            ev += ' — também casou %s; primário por precedência declarada' % (
                '+'.join(sorted(set(achados) - {primario})))
        return primario, sorted(achados), ev
    papel = reg.get('DECLARED_ROLE')
    if papel in TIPO_POR_PAPEL:
        return TIPO_POR_PAPEL[papel], [TIPO_POR_PAPEL[papel]], 'papel declarado do canal: %s' % papel
    return 'OTHER', [], 'texto presente e nenhum dos tipos nomeados casou'


# ---------------------------------------------------------------- originalidade
# O YouTube não declara republicação como a plataforma do LinkedIn declara repost. Então:
#   · `RESHARE`    exige marca textual de republicação;
#   · `SYNDICATED` exige o mesmo título em canais DIFERENTES — a mesma peça distribuída;
#   · `ORIGINAL`   exigiria prova de autoria que a rota não dá.
# Estar no canal da própria empresa NÃO prova originalidade. O resto é `UNKNOWN`.
MARCA_RESHARE = re.compile(
    r'\bv[ií]a\b|\bfuente:|\bcr[eé]ditos?:|reproducci[oó]n de|\brepost\b|'
    r'publicado originalmente|extra[ií]do de|con permiso de', re.I)


def marcar_originalidade(registros):
    """Marca ORIGINALITY em todos, e devolve a contagem por estado.

    Ausência de evidência de republicação **não** é evidência de originalidade.
    """
    por_titulo = {}
    for r in registros:
        t = (r.get('TITLE') or '').strip().lower()
        if t and t != NAO_SEI.lower():
            por_titulo.setdefault(t, set()).add(r.get('CHANNEL_ID'))
    contagem = {}
    for r in registros:
        campo = ' '.join(str(r.get(k) or '') for k in ('TITLE', 'DESCRIPTION'))
        t = (r.get('TITLE') or '').strip().lower()
        if MARCA_RESHARE.search(campo):
            estado, ev = 'RESHARE', 'marca textual de republicação'
        elif t and len(por_titulo.get(t, ())) > 1:
            estado, ev = 'SYNDICATED', 'mesmo título em %d canais distintos' % len(por_titulo[t])
        else:
            estado, ev = 'UNKNOWN', ('a rota não declara autoria nem republicação; '
                                     'estar no canal não prova originalidade')
        r['ORIGINALITY'] = estado
        r['ORIGINALITY_EVIDENCE'] = ev
        contagem[estado] = contagem.get(estado, 0) + 1
    return contagem


# ---------------------------------------------------------------- pipeline
def pipeline_video(brutos, *, source_id, run_id, capture_date, papel_por_canal=None,
                   transcricoes=None, evidence_path=None):
    """RAW -> normaliza -> classifica -> originalidade -> DEDUPE -> saída.

    É este caminho, e não a função solta, que a coleta precisa chamar. A auditoria de
    2026-08-29 apontou que o dedupe existia como função testada e nenhum pipeline o
    invocava; a partir daqui, invocar o pipeline é a única forma de produzir registro.

    Devolve (registros_únicos, relatório) com RAW_COUNT / DUPLICATE_COUNT /
    UNIQUE_CONTENT_COUNT sempre explícitos.
    """
    normalizados = []
    for b in brutos:
        r = normalizar_video(b, source_id=source_id, run_id=run_id,
                             capture_date=capture_date, papel_por_canal=papel_por_canal,
                             transcricoes=transcricoes, evidence_path=evidence_path)
        r = marcar_molecula_e_lugar(marcar_assunto(r))
        r['CONTENT_TYPE'], r['CONTENT_TYPE_ALL'], r['CONTENT_TYPE_EVIDENCE'] = classificar_tipo(r)
        normalizados.append(r)

    unicos, colapsados = dedupe(normalizados)
    # quem colapsou, e contra qual registro canônico
    canonico, duplicatas = {}, []
    for i, r in enumerate(normalizados):
        k = chave_de_dedupe(r, i)
        if k in canonico:
            duplicatas.append({'DUPLICATE_OF': canonico[k], 'PLATFORM': k[0], 'EXTERNAL_ID': k[1]})
        else:
            canonico[k] = r.get('CONTENT_ID')

    originalidade = marcar_originalidade(unicos)
    tipos = {}
    for r in unicos:
        tipos[r['CONTENT_TYPE']] = tipos.get(r['CONTENT_TYPE'], 0) + 1

    relatorio = {
        'RUN_ID': run_id,
        'RAW_COUNT': len(brutos),
        'DUPLICATE_COUNT': colapsados,
        'UNIQUE_CONTENT_COUNT': len(unicos),
        'UNIQUE_ORIGIN_COUNT': len({r['ORIGIN_ID'] for r in unicos}),
        'DEDUPE_KEY': 'PLATFORM + EXTERNAL_ID',
        # Sem isto, um lote inteiro sem id vira "tudo duplicata" e ninguem ve.
        'WITHOUT_STRUCTURAL_ID_COUNT': len(sem_id_estrutural(normalizados)),
        'REGRA_SEM_ID': ('registro sem EXTERNAL_ID nao colapsa: ausencia de identidade nao '
                         'e identidade compartilhada'),
        'DUPLICATES': duplicatas,
        'CONTENT_TYPE_COUNTS': tipos,
        'CLASSIFIED_COUNT': sum(n for t, n in tipos.items() if t != NAO_SEI),
        'UNKNOWN_TYPE_COUNT': tipos.get(NAO_SEI, 0),
        'ORIGINALITY_COUNTS': originalidade,
        'FIELD_COVERAGE': cobertura(unicos),
    }
    return unicos, relatorio


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
