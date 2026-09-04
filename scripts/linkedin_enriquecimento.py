#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LINKEDIN ENRICHMENT V1 — enriquecer quem JÁ EXISTE, sem inventar ninguém.

    py scripts/linkedin_enriquecimento.py mapa         # o que a casa consegue hoje
    py scripts/linkedin_enriquecimento.py enriquecer   # lê o RAW JÁ PAGO
    py scripts/linkedin_enriquecimento.py video        # a escada do vídeo

ESTE ARQUIVO NÃO ABRE NENHUMA ROTA PAGA. NENHUMA.
-------------------------------------------------
Ele não chama Apify, não inicia ator, não gasta chave. Tudo que ele lê já foi
comprado e já está no repositório, em `data/samples/raw-paid/`. O custo de rodar
este arquivo é zero, e há teste que prova que ele não importa `coletor`.

    O DADO MAIS BARATO DA CASA É O QUE JÁ FOI PAGO E NÃO FOI LIDO.

POR QUE ELE EXISTE — a medição que o justificou
------------------------------------------------
O ator de perfil devolveu, para 138 pessoas já pagas:

    experience      98%        about            63%
    education       86%        languages        41%
    skills          88%        certifications   27%

e a normalização preservou NENHUM deles. O artefato normalizado guarda nome,
headline, localização, seguidores e URL — e joga fora a experiência profissional,
a formação, as competências, o texto que a própria pessoa escreveu sobre si.

Nos posts o desperdício é o mesmo: 291 de 472 traziam imagem, 93 traziam artigo
com link externo, 56 traziam VÍDEO com URL de mídia, 20 traziam documento em PDF
— e o normalizado não tem um único campo de mídia.

Nada disso exige execução nova. Exige LER o que já está pago.

O QUE ESTE ARQUIVO SE RECUSA A FAZER
-------------------------------------
**Não cria pessoa.** LinkedIn é enriquecimento de `PERSON_ID` que já existe no
universo canônico (`SPEAKER-UNIVERSE-PILOT-V1.json`), e o único caminho de ligação
aceito é o que `sensor_canal_identidade.py` já provou em `CANAL-IDENTIDADE.json`.
Perfil sem ligação provada sai como `IDENTITY = NÃO SEI` e fica de fora do
enriquecimento — nunca vira pessoa nova.

    NAME_MATCH ≠ PERSON. SEARCH_HIT ≠ PERSON.

**Não infere papel.** `headline` e `currentPosition` provam uma coisa só: *a pessoa
se apresenta assim*. Isso vira `SELF_DECLARED_*`, nunca `ROLE = RESEARCHER`. Quem
decide papel é a âncora técnica do universo canônico, que veio de ORCID e OpenAlex.

**Não transforma métrica social em autoridade.** `FOLLOWERS ≠ AUTHORITY` continua
sendo lei da casa, e aqui ela é executada: as métricas entram no bloco de
`ENGAGEMENT`, separadas dos fatos, e nenhum estado deste arquivo as consulta.

AS TRÊS COISAS FICAM EM CAMPOS FISICAMENTE SEPARADOS
------------------------------------------------------
    FACT            o que a fonte diz, com proveniência que resolve
    INTERPRETATION  o que isso PODE significar para o Sintonia
    ACTION          o que alguém poderia fazer com isso

Misturar as três num campo só é como se perde a diferença entre o que foi
observado e o que foi concluído. Aqui elas nem cabem no mesmo dicionário.

A LEI NOVA QUE ESTA RODADA DESCOBRIU
--------------------------------------
    RAW PRESERVADO ≠ MÍDIA PRESERVADA

O RAW dos posts guarda a URL do vídeo, e essa URL é ASSINADA e EXPIRA. Medido em
2026-09-04: as 56 URLs de vídeo do corpus `ES-T8-002`, capturado em 2026-08-29,
carregavam `e=1788580800` — expiração em **2026-09-05**. Sete dias de vida.

O `.raw.json.gz` está preservado para sempre e continua dizendo que havia vídeo;
o vídeo em si desaparece em uma semana. Preservar o RAW **não** preserva a mídia,
e quem quiser a fala precisa buscar a mídia perto da coleta, não meses depois.

Por isso `MEDIA_URL_STATE` é calculado contra o relógio, e uma URL vencida sai
como `MEDIA_URL_EXPIRED` — que é um estado, não uma ausência de vídeo.

E A ARMADILHA QUE O WHISPER ARMOU SOZINHO
-------------------------------------------
Medido na mesma rodada, em três vídeos de origens que a casa já conhecia:

    Celestino Domínguez Infante   64 s de áudio → 1.100 caracteres de fala técnica
    demoFARM Andalucía            19 s de áudio → "¡Suscríbete!"
    Alberto Giner                 22 s de áudio → nada

Os dois últimos foram reconferidos SEM filtro de voz, para separar "o filtro comeu"
de "não havia fala": o áudio foi lido, a duração foi medida, e não havia fala.

    VÍDEO ≠ FALA

E "¡Suscríbete!" não é o que a demoFARM disse — é o que o modelo alucina sobre
música e silêncio. Se aquilo entrasse no corpus, o Sintonia teria registrado uma
autoridade fitossanitária andaluza pedindo inscrição num canal. Por isso existe
`SUSPECTED_HALLUCINATION`: transcrição curta demais para a duração do áudio não é
promovida a fala, é marcada.

    TRANSCRIÇÃO VAZIA ≠ SEM ÁUDIO
    FALHA DE ACESSO ≠ VÍDEO SEM LEGENDA
"""
import datetime
import gzip
import json
import os
import re
import sys
import unicodedata
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
RAW = os.path.join(SAMPLES, 'raw-paid')
DEST_DIR = os.path.join(SAMPLES, 'LINKEDIN-ENRICHMENT')

NAO_SEI = 'NÃO SEI'
MISSION = 'LINKEDIN_ENRICHMENT_V1'

# ── de onde vem a identidade canônica. NÃO se cria outra. ────────────────────────
UNIVERSO = os.path.join(SAMPLES, 'SPEAKER-UNIVERSE-PILOT-V1.json')
CANAL_IDENTIDADE = os.path.join(SAMPLES, 'SENSOR-PILOT', 'CANAL-IDENTIDADE.json')
VOZ_LINKEDIN = os.path.join(SAMPLES, 'ES-VOICE-LINKEDIN.json')

# ── enums de proveniência (missão §8) ───────────────────────────────────────────
CONTENT_SOURCE = ('PROFILE', 'POST_TEXT', 'NATIVE_CAPTION', 'WHISPER_TRANSCRIPT',
                  'DOCUMENT_PDF', 'OTHER')
TRANSCRIPT_METHOD = ('NATIVE_CAPTION', 'WHISPER', 'NOT_AVAILABLE')

# ── estados da escada do vídeo (missão §5) ──────────────────────────────────────
NO_VIDEO = 'NO_VIDEO'
NATIVE_CAPTION_AVAILABLE = 'NATIVE_CAPTION_AVAILABLE'
NATIVE_CAPTION_NOT_IN_ROUTE = 'NATIVE_CAPTION_NOT_IN_ROUTE'
MEDIA_URL_PRESENT = 'MEDIA_URL_PRESENT'
MEDIA_URL_EXPIRED = 'MEDIA_URL_EXPIRED'
MEDIA_URL_ABSENT = 'MEDIA_URL_ABSENT'
NO_SPEECH_DETECTED = 'NO_SPEECH_DETECTED'
SUSPECTED_HALLUCINATION = 'SUSPECTED_HALLUCINATION'
TRANSCRIPT_OK = 'TRANSCRIPT_OK'
NOT_ATTEMPTED = 'NOT_ATTEMPTED'

# Fala real ocupa espaço. Menos de um caractere por segundo de áudio, sobre um vídeo
# que tinha áudio legível, é forte demais para ser fala e fraco demais para ser prova.
# O número não é elegante: é o que separa "¡Suscríbete!" (12 caracteres em 19 s) do
# vídeo técnico (1.100 caracteres em 64 s), com folga dos dois lados.
DENSIDADE_MINIMA_CHAR_POR_S = 1.0


def agora():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def hoje():
    return datetime.date.today().isoformat()


def _norm(s):
    """Nome comparável. O travessão U+2010 do OpenAlex contra o hífen ASCII já
    fez a MESMA pessoa sair como duas — normalizar antes de comparar fecha isso."""
    s = unicodedata.normalize('NFKD', str(s or ''))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    for t in ('‐', '‑', '‒', '–', '—', '−'):
        s = s.replace(t, '-')
    return re.sub(r'[^a-z0-9 ]+', ' ', s.lower()).strip()


def identificador_publico(url):
    """→ o `public identifier` do perfil, que é a identidade do CONTEÚDO.

    Nunca o token de busca que trouxe o perfil: trocar de consulta não pode fazer
    a mesma pessoa entrar duas vezes.
    """
    if not url:
        return None
    u = urllib.parse.unquote(str(url).split('?')[0].rstrip('/'))
    m = re.search(r'/in/(.+)$', u)
    return m.group(1).lower() if m else None


def _ler(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _ler_gz(nome):
    p = os.path.join(RAW, nome)
    if not os.path.exists(p):
        return None
    with gzip.open(p, 'rt', encoding='utf-8') as f:
        return json.load(f)


# ═══════════════════════════════════════════════════════ 1 · IDENTIDADE CANÔNICA
def mapa_de_identidade():
    """perfil do LinkedIn → PERSON_ID canônico, e SÓ quando já foi provado.

    A ligação não é feita aqui: ela é LIDA de `CANAL-IDENTIDADE.json`, que é o dono
    do assunto. Este arquivo não tem opinião sobre identidade — ele obedece a de
    quem já decidiu, de graça, sobre material já pago.
    """
    d = _ler(CANAL_IDENTIDADE)
    if not d:
        return {}, {'STATE': 'CANAL_IDENTIDADE_AUSENTE'}
    por_perfil, por_pessoa = {}, {}
    for i in d.get('ITEMS', []):
        if i.get('PLATFORM') != 'LINKEDIN':
            continue
        if i.get('CHANNEL_IDENTITY_STATE') != 'PROVED':
            continue
        chave = identificador_publico(i.get('SOURCE_URL'))
        if not chave:
            continue
        por_perfil[chave] = {
            'PERSON_ID': i['PERSON_ID'], 'PERSON_NAME': i['NAME'],
            'CASE_ID': i.get('CASE_ID'), 'COUNTRY_OF_PERSON': i.get('COUNTRY_OF_PERSON'),
            'INSTITUTION': i.get('INSTITUTION'),
            'IDENTITY_BASIS': i.get('CHANNEL_IDENTITY_EVIDENCE'),
            'IDENTITY_OWNER': 'SENSOR-PILOT/CANAL-IDENTIDADE',
        }
        por_pessoa.setdefault(i['PERSON_ID'], []).append(chave)

    # Uma pessoa com VÁRIOS perfis provados não é um detalhe: ou ela tem várias
    # contas, ou a regra de identidade aprovou homônimo. Antonio Logrieco saiu com
    # TRÊS. Escolher um em silêncio esconderia a pergunta; declarar o estado a mantém
    # aberta, e o enriquecimento continua — só carimbado.
    for chave, v in por_perfil.items():
        n = len(por_pessoa.get(v['PERSON_ID'], []))
        v['PERSON_PROFILE_COUNT'] = n
        v['MULTIPLE_PROVED_PROFILES'] = 'YES' if n > 1 else 'NO'
    return por_perfil, {'STATE': 'OK', 'PROFILES_PROVED': len(por_perfil),
                        'PEOPLE_WITH_PROVED_PROFILE': len(por_pessoa)}


def resolver_identidade(url_perfil, mapa):
    """→ (bloco de identidade, ligado?). Sem prova, `NÃO SEI` — nunca pessoa nova."""
    chave = identificador_publico(url_perfil)
    achado = mapa.get(chave) if chave else None
    if achado:
        return dict(achado, IDENTITY='LINKED_TO_CANONICAL_PERSON',
                    LINKEDIN_PUBLIC_ID=chave), True
    return {
        'IDENTITY': NAO_SEI,
        'PERSON_ID': NAO_SEI,
        'LINKEDIN_PUBLIC_ID': chave,
        'WHY': ('nenhuma ligação PROVADA entre este perfil e uma pessoa do universo '
                'canônico. Isto NÃO significa que a pessoa não exista, e NÃO autoriza '
                'criar pessoa nova a partir do LinkedIn.'),
        'IDENTITY_OWNER': 'SENSOR-PILOT/CANAL-IDENTIDADE',
    }, False


# ═════════════════════════════════════════════════════════════════ 2 · PERFIL
# Campos DECLARADOS pela própria pessoa. O prefixo não é decoração: ele é o que
# impede o campo de ser lido depois como se o Sintonia tivesse verificado o cargo.
def campos_de_perfil(item):
    """→ o que o perfil declara, com cada campo carimbado como declaração."""
    loc = item.get('location') or {}
    exp = item.get('experience') or []
    edu = item.get('education') or []

    def _lista(v, campos):
        saida = []
        for e in (v or []):
            if isinstance(e, dict):
                saida.append({c: e.get(c) for c in campos if e.get(c) not in (None, '', [])})
        return saida

    return {
        'PROFILE_URL': item.get('linkedinUrl'),
        'LINKEDIN_PUBLIC_ID': (item.get('publicIdentifier') or '').lower() or None,
        'PROFILE_DISPLAY_NAME': ('%s %s' % (item.get('firstName') or '',
                                            item.get('lastName') or '')).strip() or None,
        # "a pessoa se apresenta como X" — prova a apresentação, não o cargo.
        'SELF_DECLARED_HEADLINE': item.get('headline'),
        'SELF_DECLARED_ABOUT': item.get('about'),
        'SELF_DECLARED_CURRENT_POSITION': _lista(
            item.get('currentPosition'), ('title', 'companyName', 'companyUrn')),
        'SELF_DECLARED_LOCATION': loc.get('linkedinText'),
        'SELF_DECLARED_COUNTRY_CODE': loc.get('countryCode'),
        'SELF_DECLARED_EXPERIENCE': _lista(
            exp, ('position', 'title', 'companyName', 'duration', 'location', 'description')),
        'SELF_DECLARED_EDUCATION': _lista(
            edu, ('title', 'schoolName', 'degree', 'fieldOfStudy', 'period')),
        'SELF_DECLARED_SKILLS': [s.get('name') for s in (item.get('skills') or [])
                                 if isinstance(s, dict) and s.get('name')],
        'SELF_DECLARED_LANGUAGES': [l.get('name') for l in (item.get('languages') or [])
                                    if isinstance(l, dict) and l.get('name')],
        'SELF_DECLARED_CERTIFICATIONS': _lista(
            item.get('certifications'), ('title', 'issuedAt', 'issuedBy')),
        'SELF_DECLARED_PUBLICATIONS': _lista(
            item.get('publications'), ('title', 'publishedAt', 'description', 'link')),
        'SELF_DECLARED_WEBSITES': item.get('websites') or [],
        # Métrica social. Fica aqui, longe dos fatos, e nenhum estado a consulta.
        'ENGAGEMENT': {'FOLLOWERS': item.get('followerCount'),
                       'CONNECTIONS': item.get('connectionsCount'),
                       'PLATFORM_VERIFIED': item.get('verified'),
                       'PLATFORM_CREATOR_FLAG': item.get('creator'),
                       'AVISO': 'FOLLOWERS ≠ AUTHORITY. Nada aqui prova competência.'},
        'PROFILE_REGISTERED_AT': item.get('registeredAt'),
        'ROLE_NOT_INFERRED': ('o papel técnico NÃO é derivado da headline. Ele é do '
                              'universo canônico, com âncora ORCID/OpenAlex.'),
    }


def ganho_de_perfil(campos):
    """Quais campos ESTE perfil realmente acrescenta. Vazio não conta como ganho."""
    interessa = ('SELF_DECLARED_ABOUT', 'SELF_DECLARED_EXPERIENCE',
                 'SELF_DECLARED_EDUCATION', 'SELF_DECLARED_SKILLS',
                 'SELF_DECLARED_LANGUAGES', 'SELF_DECLARED_CERTIFICATIONS',
                 'SELF_DECLARED_PUBLICATIONS', 'SELF_DECLARED_WEBSITES',
                 'SELF_DECLARED_CURRENT_POSITION', 'SELF_DECLARED_HEADLINE')
    return sorted(c for c in interessa if campos.get(c) not in (None, '', [], {}))


# ══════════════════════════════════════════════════════════════════ 3 · POSTS
def _expira_em(url):
    """A URL de mídia é assinada. `e=` é o instante em que ela morre."""
    m = re.search(r'[?&]e=(\d+)', str(url or ''))
    if not m:
        return None
    try:
        return datetime.datetime.fromtimestamp(int(m.group(1)), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return None


def estado_da_url_de_midia(url, referencia=None):
    """→ (estado, expira_em_iso). Vencida é ESTADO, nunca 'não havia vídeo'."""
    if not url:
        return MEDIA_URL_ABSENT, None
    exp = _expira_em(url)
    if exp is None:
        return MEDIA_URL_PRESENT, NAO_SEI
    ref = referencia or datetime.datetime.now(datetime.timezone.utc)
    estado = MEDIA_URL_PRESENT if exp > ref else MEDIA_URL_EXPIRED
    return estado, exp.strftime('%Y-%m-%dT%H:%M:%SZ')


# ═══════════════════════════════════ 3b · A DATA QUE VEM DE GRAÇA, DENTRO DO ID
# Padrão descrito por `Ollie-Boyd/Linkedin-post-timestamp-extractor` (GPL-3.0). O
# CÓDIGO não foi copiado — a licença não permitiria, e não precisa: o algoritmo é
# prior art pública (mesma técnica que Ryan Benson descreveu para o TikTok, usada
# pelo Bellingcat). O que segue é reimplementação a partir da descrição.
#
# Os 41 primeiros bits do id de 19 dígitos do post SÃO o instante de criação em
# milissegundos. Nenhuma chamada de rede, nenhum cookie, nenhum custo.
#
# CONFERIDO CONTRA OS NOSSOS PRÓPRIOS DADOS antes de entrar aqui: nos 472 posts
# de `ES-T8-002`, a data derivada do id bateu com o `postedAt.timestamp` que a
# plataforma devolveu em 472 de 472, com diferença menor que 1 segundo. Zero
# divergências. Um padrão de fora só entra nesta casa depois de ser medido dentro
# dela — há teste que refaz essa conferência sobre o RAW.
#
# Serve para duas coisas, e a segunda é a mais valiosa:
#   1. DATAR o post quando a rota só deu data relativa ("3mo"), que envelhece;
#   2. CONFERIR a data que a rota afirmou. Se as duas discordarem, uma está errada
#      — e o estado sai DISAGREE, nunca uma das duas escolhida em silêncio.
BITS_DO_TEMPO = 41


def data_do_urn(post_id):
    """→ datetime UTC da criação do post, tirado do próprio id. Sem rede."""
    try:
        bits = bin(int(str(post_id).strip()))[2:]
    except (TypeError, ValueError):
        return None
    if len(bits) < BITS_DO_TEMPO:
        return None
    ms = int(bits[:BITS_DO_TEMPO], 2)
    try:
        d = datetime.datetime.fromtimestamp(ms / 1000.0, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return None
    # Um id que decodifica para 1973 ou 2190 não é um id de post: é outra coisa
    # com cara de número. Faixa declarada, e fora dela o resultado é None.
    if not (2010 <= d.year <= datetime.date.today().year + 1):
        return None
    return d


def conferir_data(post_id, data_declarada):
    """→ (data_do_urn_iso, estado do acordo). Discordância é ESTADO, não escolha."""
    d = data_do_urn(post_id)
    if d is None:
        return None, 'URN_NOT_DECODABLE'
    iso = d.strftime('%Y-%m-%dT%H:%M:%SZ')
    if not data_declarada or data_declarada == NAO_SEI:
        # A rota não deu data. O id deu. Um NÃO SEI a menos, de graça.
        return iso, 'RESOLVED_BY_URN'
    try:
        decl = datetime.datetime.strptime(
            str(data_declarada)[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        return iso, 'DECLARED_DATE_UNPARSEABLE'
    return iso, ('AGREE' if abs((d - decl).total_seconds()) <= 1.0 else 'DISAGREE')

def campos_de_post(item):
    """→ texto, data, mídia, hashtags, menções e links. Tudo que a normalização perdeu."""
    texto = item.get('content') or ''
    postado = item.get('postedAt') or {}
    autor = item.get('author') or {}
    video = item.get('postVideo') or {}
    doc = item.get('document') or {}
    art = item.get('article') or {}

    mencoes, empresas = [], []
    for a in (item.get('contentAttributes') or []):
        if a.get('type') == 'PROFILE_MENTION' and a.get('profile'):
            mencoes.append(a['profile'].get('linkedinUrl') or a['profile'].get('name'))
        if a.get('type') == 'COMPANY_NAME' and a.get('company'):
            empresas.append(a['company'].get('name'))

    estado_midia, expira = estado_da_url_de_midia(video.get('videoUrl'))

    # Data: só é data quando a fonte deu data. `postedAgoShort` ("3mo") é a data
    # RELATIVA que a plataforma mostra, e ela envelhece — vira campo próprio, e nunca
    # é convertida em data absoluta por subtração da hora da leitura.
    data_iso = postado.get('date')
    urn_iso, acordo = conferir_data(item.get('id'), data_iso)
    return {
        'POST_ID': item.get('id'),
        'POST_URL': item.get('linkedinUrl'),
        'DECLARED_AUTHOR': autor.get('name'),
        'AUTHOR_URL': (autor.get('linkedinUrl') or '').split('?')[0] or None,
        'AUTHOR_PUBLIC_ID': (autor.get('publicIdentifier') or '').lower() or None,
        'TEXT': texto,
        'TEXT_LENGTH': len(texto),
        'PUBLICATION_DATE': data_iso or urn_iso or NAO_SEI,
        'PUBLICATION_DATE_RELATIVE': postado.get('postedAgoShort') or NAO_SEI,
        'PUBLICATION_DATE_FROM_URN': urn_iso or NAO_SEI,
        'PUBLICATION_DATE_AGREEMENT': acordo,
        'HASHTAGS': sorted(set(re.findall(r'#(\w+)', texto))),
        'PROFILE_MENTIONS': mencoes,
        'COMPANY_MENTIONS': sorted(set(empresas)),
        'EXTERNAL_LINKS': sorted(set(re.findall(r'https?://\S+', texto))),
        'CONTENT_KIND': ('VIDEO' if video else 'DOCUMENT' if doc else
                         'ARTICLE' if art else 'IMAGE' if item.get('postImages') else
                         'TEXT_ONLY' if texto else NAO_SEI),
        'IMAGE_COUNT': len(item.get('postImages') or []),
        'HAS_VIDEO': bool(video),
        'VIDEO_URL': video.get('videoUrl'),
        'VIDEO_THUMBNAIL': video.get('thumbnailUrl'),
        'MEDIA_URL_STATE': estado_midia,
        'MEDIA_URL_EXPIRES_AT': expira,
        # Documento de carrossel vem como PDF já higienizado. A casa tem `pdf_text.py`
        # e não precisa de OCR nem de rota nova para ler isto.
        'DOCUMENT_TITLE': doc.get('title'),
        'DOCUMENT_PDF_URL': doc.get('transcribedDocumentUrl'),
        'ARTICLE_TITLE': art.get('title'),
        'ARTICLE_LINK': art.get('link'),
        'ARTICLE_SOURCE': art.get('subtitle'),
        'IS_REPOST': bool(item.get('repost')),
        'ENGAGEMENT': dict(item.get('engagement') or {},
                           AVISO='métrica social. NÃO é autoridade científica.'),
        'DISCOVERY_QUERY': (item.get('query') or {}).get('query')
        if isinstance(item.get('query'), dict) else item.get('query'),
    }


# ═══════════════════════════════════════════════════════════ 4 · ESCADA DO VÍDEO
def escada_do_video(post, transcricao=None):
    """A escada da missão §5, com cada degrau declarado e nenhum atalho.

    `transcricao`, quando existe, é o resultado JÁ MEDIDO do whisper local:
    {'TEXT':…, 'AUDIO_SECONDS':…, 'SEGMENTS':…, 'MODEL':…}. Este arquivo NÃO chama
    o whisper: quem gasta hora de máquina é o operador, e o resultado entra aqui.
    """
    if not post.get('HAS_VIDEO'):
        return {'VIDEO_LADDER': NO_VIDEO, 'TRANSCRIPT': None,
                'TRANSCRIPT_METHOD': 'NOT_AVAILABLE', 'CONTENT_SOURCE': 'POST_TEXT'}

    passo = {
        'VIDEO_DETECTED': 'YES',
        # Medido: o ator de posts devolve `postVideo` com thumbnail e URL de mídia,
        # e NENHUM campo de legenda, transcrição, VTT ou SRT. Isso é uma afirmação
        # sobre A ROTA, não sobre o vídeo: dizer "vídeo sem legenda" seria inventar.
        'NATIVE_CAPTION': NATIVE_CAPTION_NOT_IN_ROUTE,
        'NATIVE_CAPTION_WHY': ('a rota paga de posts não devolve campo de legenda. '
                               'Se o vídeo tem ou não legenda no player é NÃO SEI.'),
        'MEDIA_URL_STATE': post.get('MEDIA_URL_STATE'),
        'MEDIA_URL_EXPIRES_AT': post.get('MEDIA_URL_EXPIRES_AT'),
    }

    if post.get('MEDIA_URL_STATE') == MEDIA_URL_EXPIRED:
        passo.update({
            'VIDEO_LADDER': MEDIA_URL_EXPIRED, 'TRANSCRIPT': None,
            'TRANSCRIPT_METHOD': 'NOT_AVAILABLE', 'CONTENT_SOURCE': 'POST_TEXT',
            'WHY': ('a URL assinada da mídia venceu. RAW PRESERVADO ≠ MÍDIA '
                    'PRESERVADA. Isto NÃO significa que o vídeo não tenha fala.'),
        })
        return passo

    if transcricao is None:
        passo.update({
            'VIDEO_LADDER': NOT_ATTEMPTED, 'TRANSCRIPT': None,
            'TRANSCRIPT_METHOD': 'NOT_AVAILABLE', 'CONTENT_SOURCE': 'POST_TEXT',
            'WHY': 'mídia alcançável, whisper ainda não rodado sobre este item.',
        })
        return passo

    txt = (transcricao.get('TEXT') or '').strip()
    dur = transcricao.get('AUDIO_SECONDS') or 0
    passo['ASR_MODEL'] = transcricao.get('MODEL')
    passo['AUDIO_SECONDS'] = dur
    passo['AUDIO_WAS_READ'] = 'YES'      # a duração foi medida: o áudio existe

    if not txt:
        passo.update({
            'VIDEO_LADDER': NO_SPEECH_DETECTED, 'TRANSCRIPT': None,
            'TRANSCRIPT_METHOD': 'WHISPER', 'CONTENT_SOURCE': 'POST_TEXT',
            'WHY': ('o áudio foi obtido e lido (%.0f s) e não havia fala. VÍDEO ≠ FALA. '
                    'Isto é diferente de "não consegui o áudio".' % dur),
        })
        return passo

    densidade = (len(txt) / dur) if dur else 0
    if dur and densidade < DENSIDADE_MINIMA_CHAR_POR_S:
        passo.update({
            'VIDEO_LADDER': SUSPECTED_HALLUCINATION, 'TRANSCRIPT': txt,
            'TRANSCRIPT_METHOD': 'WHISPER', 'CONTENT_SOURCE': 'POST_TEXT',
            'CHAR_PER_SECOND': round(densidade, 3),
            'WHY': ('%d caracteres para %.0f s de áudio. Densidade baixa demais para '
                    'ser fala. O modelo alucina frases prontas sobre música e silêncio '
                    '— este texto NÃO é promovido a voz da pessoa.' % (len(txt), dur)),
        })
        return passo

    passo.update({
        'VIDEO_LADDER': TRANSCRIPT_OK, 'TRANSCRIPT': txt,
        'TRANSCRIPT_METHOD': 'WHISPER', 'CONTENT_SOURCE': 'WHISPER_TRANSCRIPT',
        'CHAR_PER_SECOND': round(densidade, 3),
    })
    return passo


# ══════════════════════════════════════════════════════════════ 5 · PROVENIÊNCIA
def proveniencia(post_ou_perfil, identidade, *, content_source, transcript_method,
                 run_id, raw_path, idioma):
    """O bloco que a missão §8 exige em CADA fato extraído."""
    assert content_source in CONTENT_SOURCE, content_source
    assert transcript_method in TRANSCRIPT_METHOD, transcript_method
    return {
        'SOURCE_PLATFORM': 'LINKEDIN',
        'SOURCE_URL': post_ou_perfil.get('POST_URL') or post_ou_perfil.get('PROFILE_URL'),
        'PERSON_ID': identidade.get('PERSON_ID'),
        'POST_ID': post_ou_perfil.get('POST_ID'),
        'CAPTURED_AT': agora(),
        'PUBLICATION_DATE': post_ou_perfil.get('PUBLICATION_DATE', NAO_SEI),
        'ORIGINAL_LANGUAGE': idioma,
        'CONTENT_SOURCE': content_source,
        'TRANSCRIPT_METHOD': transcript_method,
        'COLLECTION_RUN_ID': run_id,
        'RAW_EVIDENCE_PATH': raw_path,
        'NEW_ACTOR_RUNS': 0,
        'COST_USD': 0,
        'SOURCE_LOCATION': 'LinkedIn',
        'FACT_LOCATION': ('NÃO DERIVADO — onde a pessoa mora não é onde o fenômeno '
                          'agrícola aconteceu'),
    }


def fato(texto, prov):
    """FACT: o que a fonte diz. Sem leitura, sem conclusão, sem recomendação."""
    return {'FACT': texto, 'PROVENANCE': prov}


def interpretacao(texto, base):
    """INTERPRETATION: o que PODE significar. Nunca no mesmo campo que o fato."""
    return {'INTERPRETATION': texto, 'BASED_ON_FACT': base,
            'STATUS': 'HYPOTHESIS_NOT_PROVED'}


def acao(texto, para_quem):
    """ACTION: o que alguém poderia fazer. Nem fato nem interpretação."""
    return {'ACTION': texto, 'FOR': para_quem, 'STATUS': 'SUGGESTED_NOT_DECIDED'}


# ═════════════════════════════════════════════════════════════════ 6 · COMANDOS
FONTES_RAW = [
    ('ES-T8-002-linkedin-profiles.raw.json.gz', 'PROFILE',
     'ES-T8-002-PROFILES-2026-08-29-a'),
    ('ES-T8-002-linkedin-posts-a.raw.json.gz', 'POST', 'ES-T8-002-2026-08-29-a'),
    ('ES-T8-002-linkedin-posts-b.raw.json.gz', 'POST', 'ES-T8-002-2026-08-29-a'),
]


def _pessoas(item):
    return 'headline' in item or 'firstName' in item


def enriquecer():
    mapa, meta = mapa_de_identidade()
    universo = _ler(UNIVERSO) or {}
    saida = {
        'SOURCE_ID': 'DERIVED/LINKEDIN-ENRICHMENT-V1',
        'source': ('releitura do RAW JÁ PAGO do LinkedIn. NENHUMA execução nova, '
                   'nenhuma chave usada, custo zero.'),
        'SOURCE_LOCATION': 'LinkedIn', 'FACT_LOCATION': 'n/a — metadado de coleta',
        'ORIGINAL_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'MISSION': MISSION, 'captured_at': hoje(), 'CAPTURED_AT': agora(),
        'NEW_ACTOR_RUNS': 0, 'COST_USD': 0,
        'IDENTITY_OWNER': 'SENSOR-PILOT/CANAL-IDENTIDADE — este arquivo NÃO cria pessoa',
        'CANONICAL_PERSON_OWNER': 'SPEAKER-UNIVERSE-PILOT-V1',
        'CANONICAL_PEOPLE': universo.get('PEOPLE_COUNT', NAO_SEI),
        'IDENTITY_MAP': meta,
        'LAWS': ['NAME_MATCH ≠ PERSON', 'FOLLOWERS ≠ AUTHORITY',
                 'RAW PRESERVADO ≠ MÍDIA PRESERVADA', 'VÍDEO ≠ FALA',
                 'TRANSCRIÇÃO VAZIA ≠ SEM ÁUDIO'],
    }

    perfis, posts, faltando = [], [], []
    for nome, tipo, run_id in FONTES_RAW:
        itens = _ler_gz(nome)
        if itens is None:
            faltando.append(nome)
            continue
        raw_path = 'data/samples/raw-paid/' + nome
        for it in itens:
            if tipo == 'PROFILE':
                if not _pessoas(it):
                    continue          # página de empresa não é pessoa
                c = campos_de_perfil(it)
                ident, ligado = resolver_identidade(c['PROFILE_URL'], mapa)
                perfis.append({
                    'IDENTITY': ident, 'LINKED_TO_CANONICAL': 'YES' if ligado else 'NO',
                    'PROFILE': c, 'FIELDS_GAINED': ganho_de_perfil(c),
                    'PROVENANCE': proveniencia(c, ident, content_source='PROFILE',
                                               transcript_method='NOT_AVAILABLE',
                                               run_id=run_id, raw_path=raw_path,
                                               idioma=NAO_SEI),
                })
            else:
                c = campos_de_post(it)
                ident, ligado = resolver_identidade(c['AUTHOR_URL'], mapa)
                posts.append({
                    'IDENTITY': ident, 'LINKED_TO_CANONICAL': 'YES' if ligado else 'NO',
                    'POST': c, 'VIDEO': escada_do_video(c),
                    'PROVENANCE': proveniencia(c, ident, content_source='POST_TEXT',
                                               transcript_method='NOT_AVAILABLE',
                                               run_id=run_id, raw_path=raw_path,
                                               idioma=NAO_SEI),
                })

    # dedupe por identidade do CONTEÚDO, nunca pela consulta que o trouxe
    vistos, unicos = set(), []
    for p in posts:
        k = p['POST']['POST_ID'] or p['POST']['POST_URL']
        if k in vistos:
            continue
        vistos.add(k)
        unicos.append(p)
    dups = len(posts) - len(unicos)
    posts = unicos

    vistos, unicos = set(), []
    for p in perfis:
        k = p['PROFILE']['LINKEDIN_PUBLIC_ID'] or p['PROFILE']['PROFILE_URL']
        if k in vistos:
            continue
        vistos.add(k)
        unicos.append(p)
    perfis = unicos

    com_video = [p for p in posts if p['POST']['HAS_VIDEO']]
    saida.update({
        'RAW_SOURCES_READ': [n for n, _t, _r in FONTES_RAW if n not in faltando],
        'RAW_SOURCES_MISSING': faltando,
        'PROFILES': perfis, 'POSTS': posts,
        'COUNTS': {
            'PROFILES_READ': len(perfis),
            'PROFILES_LINKED_TO_CANONICAL_PERSON': sum(
                1 for p in perfis if p['LINKED_TO_CANONICAL'] == 'YES'),
            'PROFILES_IDENTITY_NAO_SEI': sum(
                1 for p in perfis if p['LINKED_TO_CANONICAL'] == 'NO'),
            'POSTS_READ': len(posts), 'POSTS_DEDUPED': dups,
            'POSTS_WITH_TEXT': sum(1 for p in posts if p['POST']['TEXT_LENGTH'] > 0),
            'POSTS_WITH_DATE': sum(1 for p in posts
                                   if p['POST']['PUBLICATION_DATE'] != NAO_SEI),
            'POSTS_WITH_IMAGE': sum(1 for p in posts if p['POST']['IMAGE_COUNT']),
            'POSTS_WITH_VIDEO': len(com_video),
            'POSTS_WITH_DOCUMENT_PDF': sum(1 for p in posts
                                           if p['POST']['DOCUMENT_PDF_URL']),
            'POSTS_WITH_ARTICLE': sum(1 for p in posts if p['POST']['ARTICLE_LINK']),
            'MEDIA_URL_LIVE': sum(1 for p in com_video
                                  if p['POST']['MEDIA_URL_STATE'] == MEDIA_URL_PRESENT),
            'MEDIA_URL_EXPIRED': sum(1 for p in com_video
                                     if p['POST']['MEDIA_URL_STATE'] == MEDIA_URL_EXPIRED),
        },
        'FIELDS_GAINED_HISTOGRAM': _histograma(perfis),
        'O_QUE_ISTO_NAO_PROVA': [
            'não prova cargo: headline é como a pessoa se apresenta, não o que ela é',
            'não prova localização do fato: onde a pessoa mora não é onde o fenômeno ocorreu',
            'não prova autoridade: seguidor e curtida não são competência técnica',
            'não prova censo: o corpus veio de busca por termo, não de tudo que se publicou',
        ],
        'STATE': 'ENRICHED_FROM_ALREADY_PAID_RAW',
    })
    return saida


def _histograma(perfis):
    h = {}
    for p in perfis:
        for c in p['FIELDS_GAINED']:
            h[c] = h.get(c, 0) + 1
    return dict(sorted(h.items(), key=lambda kv: -kv[1]))


def _grava(nome, corpo):
    os.makedirs(DEST_DIR, exist_ok=True)
    p = os.path.join(DEST_DIR, nome)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return os.path.relpath(p, ROOT)


def cmd_mapa():
    mapa, meta = mapa_de_identidade()
    universo = _ler(UNIVERSO) or {}
    print('=== CAPACIDADE LINKEDIN DA CASA, HOJE (leitura, custo zero) ===')
    print('pessoas no universo canônico ........ %s' % universo.get('PEOPLE_COUNT', NAO_SEI))
    print('perfis LinkedIn PROVADOS ............ %s' % meta.get('PROFILES_PROVED', 0))
    print('pessoas com perfil provado .......... %s' % meta.get('PEOPLE_WITH_PROVED_PROFILE', 0))
    print()
    for nome, tipo, _r in FONTES_RAW:
        itens = _ler_gz(nome)
        n = len(itens) if itens is not None else None
        print('  %-6s %-46s %s' % (tipo, nome, ('%d itens' % n) if n is not None
                                   else 'AUSENTE'))
    return 0


def cmd_enriquecer():
    out = enriquecer()
    caminho = _grava('ENRIQUECIMENTO-V1.json', out)
    c = out['COUNTS']
    print('=== ENRIQUECIMENTO V1 — RAW JÁ PAGO, 0 execuções novas, US$ 0 ===')
    for k, v in c.items():
        print('  %-38s %s' % (k, v))
    print()
    print('campos de perfil recuperados (top):')
    for k, v in list(out['FIELDS_GAINED_HISTOGRAM'].items())[:10]:
        print('  %-34s %3d perfis' % (k, v))
    print('->', caminho)
    return 0


def cmd_video():
    out = enriquecer()
    com = [p for p in out['POSTS'] if p['POST']['HAS_VIDEO']]
    est = {}
    for p in com:
        e = p['VIDEO']['VIDEO_LADDER']
        est[e] = est.get(e, 0) + 1
    print('=== ESCADA DO VÍDEO — %d posts com vídeo ===' % len(com))
    for k, v in sorted(est.items()):
        print('  %-26s %d' % (k, v))
    venc = [p for p in com if p['POST']['MEDIA_URL_STATE'] == MEDIA_URL_EXPIRED]
    if venc:
        print()
        print('  %d URLs de mídia venceram. RAW PRESERVADO ≠ MÍDIA PRESERVADA.' % len(venc))
    return 0


COMANDOS = {'mapa': cmd_mapa, 'enriquecer': cmd_enriquecer, 'video': cmd_video}


def main(argv):
    if len(argv) < 2 or argv[1] not in COMANDOS:
        print(__doc__.strip().splitlines()[1])
        print('comandos: %s' % ', '.join(COMANDOS))
        return 2
    return COMANDOS[argv[1]]()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
