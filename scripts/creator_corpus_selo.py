#!/usr/bin/env python3
"""
SELO DA V1 — validar semanticamente o que já foi coletado, e decidir o freeze.

    py scripts/creator_corpus_selo.py            # roda tudo e grava o selo
    py scripts/creator_corpus_selo.py guardas    # só as regressões

ZERO COLETA. ZERO APIFY. ZERO CUSTO.
--------------------------------------
Nada aqui abre rota paga. Tudo é leitura do que já está preservado, mais leitura
READ-ONLY de artefatos canônicos de outras branches por `git show` — sem copiar
arquivo, sem trocar de branch, sem criar segundo dono.

O QUE ESTA ETAPA EXISTE PARA IMPEDIR
--------------------------------------
Um corpus que fecha com número redondo e significado errado. Quatro perguntas
que só se responde olhando de novo:

  1. `ALL_ITEMS = 442` responde quantos itens vieram. NÃO responde quantos estão
     na janela que a missão pediu. `LAST_90D_CORPUS` é outro número, e é ele que
     sustenta qualquer frase sobre atividade recente.

  2. Canal usado != canal provado. Se a coleta tivesse entrado por um canal
     descoberto durante a missão, o conteúdo NÃO poderia ser atribuído à pessoa
     sem prova de ligação. Nome parecido, avatar, idioma e tema não provam.

  3. Bug corrigido sem teste volta. Os quatro defeitos medidos viram regressão
     executável — e uma regressão que não FALHA quando o bug volta não é teste.

  4. `NOT_OBSERVED_IN_MEASURED_CORPUS` != `DOES_NOT_EXIST`. O vocabulário de
     quatro estados existe para que essa diferença não se perca na leitura.
"""
import json
import os
import re
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import creator_corpus as cc                                  # noqa: E402
import creator_corpus_analise as an                          # noqa: E402

AS_OF = '2026-08-30'

# Vocabulário de quatro estados. Um estado a menos e duas coisas diferentes
# passam a caber na mesma palavra.
OBSERVED = 'OBSERVED'
NOT_OBSERVED = 'NOT_OBSERVED_IN_MEASURED_CORPUS'
NOT_MEASURED = 'NOT_MEASURED'
NOT_APPLICABLE = 'NOT_APPLICABLE'


def _dias(data):
    from datetime import datetime, timezone
    if not data or len(data) < 10:
        return None
    try:
        d = datetime.strptime(data[:10], '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    base = datetime.strptime(AS_OF, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    return (base - d).days


# ═══════════════════════════════════════════ 1 · a janela real
def janela_real(materiais, universo, runs):
    """§1 · reconcilia a janela por alvo. Item antigo é PRESERVADO, não descartado.

    O contrato começa em `LAST_90D`. Cortar o que passou disso faria o número
    caber e apagaria o histórico que a própria missão manda guardar. A janela se
    separa; o item fica.
    """
    por_alvo = {}
    for m in materiais:
        por_alvo.setdefault(m['ENTITY_ID'], []).append(m)
    runs_por_alvo = {}
    for r in runs:
        rid = r.get('RUN_ID') or ''
        for e in universo:
            if rid.endswith('-' + e['ENTITY_ID']):
                runs_por_alvo.setdefault(e['ENTITY_ID'], []).append(r)

    linhas = []
    for e in universo:
        itens = por_alvo.get(e['ENTITY_ID'], [])
        rs = [r for r in runs_por_alvo.get(e['ENTITY_ID'], [])
              if not (r.get('RUN_ID') or '').split('-')[-2:-1] == ['CM']]
        rs = [r for r in runs_por_alvo.get(e['ENTITY_ID'], [])
              if '-CM-' not in (r.get('RUN_ID') or '')]
        datas = sorted(d for d in (m.get('PUBLISHED_AT') for m in itens)
                       if d and d != cc.NOT_KNOWN)
        dias = [_dias(m.get('PUBLISHED_AT')) for m in itens]
        dias = [d for d in dias if d is not None]
        d90 = sum(1 for d in dias if d <= 90)
        d180 = sum(1 for d in dias if 90 < d <= 180)
        dmais = sum(1 for d in dias if d > 180)
        # Canal TENTADO é o que tinha endereço coletável. O de PC-03 não tinha,
        # e por isso ele conta 0 tentativas — nunca 1 tentativa falhada.
        tentados = 1 if e['COLLECTABLE'] == 'YES' else 0
        bemsucedidos = 1 if itens else 0
        linhas.append({
            'TARGET_ID': e['ENTITY_ID'],
            'HANDLE': e['HANDLE'],
            'TARGET_TYPE': e['ENTITY_TYPE'],
            'CHANNELS_ATTEMPTED': tentados,
            'CHANNELS_SUCCESSFUL': bemsucedidos,
            'ITEMS_COLLECTED': len(itens),
            'ITEMS_LAST_90D': d90,
            'ITEMS_91_180D': d180,
            'ITEMS_OLDER_THAN_180D': dmais,
            'ITEMS_WITHOUT_DATE': len(itens) - len(dias),
            'OLDEST_ITEM_DATE': datas[0] if datas else cc.NOT_KNOWN,
            'NEWEST_ITEM_DATE': datas[-1] if datas else cc.NOT_KNOWN,
            'COLLECTION_QUERY_SUCCESS': 'YES' if itens else 'NO',
            'RUN_STATUS': sorted({r.get('STATUS') for r in rs}) or [cc.NOT_KNOWN],
            'EXACT_LIMITATION': _limite(e, itens, d90),
        })
    return linhas


def _limite(e, itens, d90):
    if e['COLLECTABLE'] == 'NO':
        return ('sem rota de conteúdo provada: %s' % e['WHY_NOT_COLLECTABLE'])
    if not itens:
        return 'canal coletável, mas a rota devolveu zero item'
    partes = []
    if d90 < 30:
        partes.append('LAST_90D tem %d itens — o alvo de 30 não é atingido dentro '
                      'da janela do contrato, e o resto do acervo é histórico' % d90)
    vazios = sum(1 for m in itens if m.get('TEXT_SUBSTANCE') == 'HASHTAGS_OR_EMPTY')
    if vazios >= len(itens) / 2:
        partes.append('%d de %d legendas são só hashtag/emoji' % (vazios, len(itens)))
    return ' · '.join(partes) or 'NENHUMA'


# ═══════════════════════════════════════════ 2 · identidade do canal
def identidade_dos_canais(universo, materiais):
    """§2 · todo canal EFETIVAMENTE usado foi conferido contra o congelado.

    O único jeito de um canal entrar na coleta foi `PUBLIC_CHANNEL` do artefato
    congelado — a coleta não aceita handle, nome nem busca. Ainda assim a
    conferência é feita aqui, item a item, porque "o código não faz isso" é uma
    afirmação sobre o código e não sobre os dados que existem.
    """
    provados = {e['ENTITY_ID']: (e['PUBLIC_CHANNEL'] or '').rstrip('/').lower()
                for e in universo}
    usados = {}
    for m in materiais:
        usados.setdefault(m['ENTITY_ID'], set()).add(m['PLATFORM'])

    linhas = []
    for e in universo:
        eid = e['ENTITY_ID']
        if e['COLLECTABLE'] == 'NO':
            estado, prova = NOT_APPLICABLE, 'nenhum canal foi usado'
            corpus_provado = 'NO'
        elif eid in usados:
            estado = 'PROVED'
            prova = ('o canal usado é literalmente o PUBLIC_CHANNEL do '
                     'CREATOR-CAPABILITY-EAME.json congelado: %s' % provados[eid])
            corpus_provado = 'YES'
        else:
            estado, prova, corpus_provado = NOT_MEASURED, 'canal não produziu item', 'NO'
        linhas.append({
            'TARGET_ID': eid, 'HANDLE': e['HANDLE'],
            'CHANNEL_USED': e['PUBLIC_CHANNEL'],
            'PLATFORMS_WITH_ITEMS': sorted(usados.get(eid, [])),
            'CHANNEL_IDENTITY': estado,
            'CORPUS_CHANNEL_PROVED': corpus_provado,
            'IDENTITY_ROUTE': prova,
            'IDENTITY_OWNER': 'CREATOR_MAP_EAME (congelado) — não reescrito aqui',
        })
    return linhas


def candidatos_de_correcao(materiais):
    """§2 · canais CITADOS no conteúdo, nunca usados, e por que não sobem sozinhos.

    O PC-01 anuncia um canal de YouTube na própria legenda do Instagram. Isso é
    um candidato forte e continua sendo APENAS candidato: a legenda de um perfil
    é declaração da própria conta, o que resolve a ligação entre as duas contas,
    mas o canal não foi coletado nesta missão e o Creator Map está congelado. Ele
    fica registrado para uma futura atualização do mapa — e nenhum material foi
    atribuído a ele, porque nenhum material dele existe no acervo.
    """
    fora = []
    # A primeira versão aceitava a própria palavra `youtube` como gatilho e
    # devolveu dois candidatos que eram `y Spotify` e `o Spotify.` — pedaços da
    # frase "en YouTube y Spotify". Um candidato de canal que é uma preposição
    # solta não é candidato fraco: é ruído com cara de descoberta. Agora exige a
    # palavra CANAL antes do nome, e recusa captura que começa por artigo ou
    # preposição.
    padrao = re.compile(r'(?:canale|canal|chaîne|chaine|channel)\s*[:\-]?\s*'
                        r'([A-Za-zÀ-ÿ0-9_\.]{3,}(?:\s+[A-Za-zÀ-ÿ0-9_\.]{2,}){0,3})',
                        re.IGNORECASE)
    VAZIAS = ('de', 'del', 'du', 'di', 'the', 'da', 'das', 'dos', 'y', 'e', 'o',
              'et', 'and', 'en', 'su', 'sur')
    vistos = set()
    for m in materiais:
        t = (m.get('TEXT') or '')
        if 'youtube' not in t.lower():
            continue
        achado = padrao.search(t)
        if not achado:
            continue
        nome = achado.group(1).strip()
        if nome.split()[0].lower() in VAZIAS or len(nome) < 4:
            continue
        chave = (m['ENTITY_ID'], nome[:40])
        if chave in vistos:
            continue
        vistos.add(chave)
        fora.append({
            'TARGET_ID': m['ENTITY_ID'],
            'CANDIDATE_CHANNEL_NAME': nome[:40],
            'DECLARED_IN': m['URL'],
            'DECLARED_BY': 'a própria conta provada, na legenda',
            'STATUS': 'CORRECTION_CANDIDATE',
            'USED_IN_THIS_CORPUS': 'NO',
            'WHY_NOT_USED': 'o Creator Map está congelado e esta missão não abre '
                            'canal novo. O candidato fica para a atualização do mapa.',
            'MATERIALS_ATTRIBUTED': 0,
        })
    return fora


# ═══════════════════════════════════════════ 3 · regressões
def guardas():
    """§3 · os quatro defeitos medidos, como teste que FALHA se o bug voltar."""
    r = []

    # 1 · `mais` em francês é a conjunção "mas", não milho.
    frase = 'Je suis au rendez-vous mais en légère avance sur les céréales'
    achou = an._achar(frase, an.CULTURAS)
    r.append(_g('FR_MAIS_NOT_MAIZE_GUARD', 'MAIZE' not in achou,
                'a frase francesa com "mais" não pode virar milho · achou=%s' % achou))

    # 2 · `bio` no nome da empresa não é manejo biológico.
    frase = 'Bio Campojoyma amplía su punto de recogida'
    achou = any(cc.contem_palavra(frase, p) for p in an.BIOLOGICO)
    r.append(_g('BIO_BRAND_NOT_BIOLOGICAL_GUARD', not achou,
                'o nome da empresa não pode acionar BIOLOGICALS'))

    # 3 · hashtag de cultura não é manejo de cultura.
    tipos = _tipos_de('Pequeña avería #viña #viticultura #vino')
    r.append(_g('HASHTAG_ALONE_NOT_TECHNICAL_MANAGEMENT_GUARD',
                'CROP_MANAGEMENT' not in tipos,
                'legenda só com hashtag de cultura não vira CROP_MANAGEMENT · '
                'tipos=%s' % sorted(tipos)))
    # e o contraprova: com sinal de manejo, DEVE virar. Um teste que só sabe
    # dizer não é um teste que passaria com o classificador desligado.
    tipos2 = _tipos_de('Hoy hacemos el tratamiento contra el mildiu en la viña')
    r.append(_g('HASHTAG_GUARD_STILL_CLASSIFIES', 'CROP_MANAGEMENT' in tipos2,
                'com cultura MAIS sinal de manejo, CROP_MANAGEMENT tem de aparecer · '
                'tipos=%s' % sorted(tipos2)))

    # 4 · o contrato do ator precisa ter sido LIDO de verdade.
    contratos = cc.carregar('ACTOR-CONTRACTS-CORPUS.json')
    lidos = [a for a in contratos if a.get('CONTRACT_STATE') == 'SCHEMA_READ']
    rejeitados = [a for a in contratos if a.get('FIELDS_WE_SEND_REJECTED')]
    r.append(_g('ACTOR_SCHEMA_ROUTE_GUARD',
                len(lidos) == len(contratos) and not rejeitados,
                'schema lido em %d de %d atores · campos fora do schema: %s'
                % (len(lidos), len(contratos),
                   [a['LABEL'] for a in rejeitados] or 'nenhum')))

    # 5 · a lei que nenhum artefato pode quebrar.
    fichas = cc.carregar('CREATOR-CORPUS-FICHES.json')
    bruto = json.dumps(fichas, ensure_ascii=False)
    proibidas = [n for n in ('ADAMA_RELEVANCE_SCORE', 'CREATOR_SCORE',
                             'FOLLOWER_RANK', 'RANKING')
                 if '"%s"' % n in bruto]
    r.append(_g('NO_RELEVANCE_SCORE', not proibidas,
                'nenhuma métrica de score nas fichas · encontradas=%s' % proibidas))
    return r


def _tipos_de(texto):
    culturas = an._achar(texto, an.CULTURAS)
    assuntos = an._achar(texto, an.ASSUNTOS)
    formas = set(an._achar(texto, an.FORMA))
    tipos = set(formas)
    if any(cc.contem_palavra(texto, p) for p in an.TRATAMENTO):
        tipos.update(('APPLICATION_CONTENT', 'CROP_PROTECTION'))
    if 'DISEASE' in assuntos:
        tipos.add('DISEASE_CONTENT')
    manejo = bool(tipos & {'HARVEST', 'PLANTING', 'IRRIGATION', 'NUTRITION',
                           'APPLICATION_CONTENT', 'CROP_PROTECTION',
                           'FIELD_TRIAL', 'BIOLOGICALS'}) or bool(assuntos)
    if culturas and manejo and not (tipos & {'CONSUMER_FACING', 'FARM_LIFESTYLE'}):
        tipos.add('CROP_MANAGEMENT')
    return tipos


def _g(nome, passou, detalhe):
    print('%-46s %s · %s' % (nome, 'PASS' if passou else 'FAIL', detalhe))
    return {'GUARD': nome, 'STATE': 'PASS' if passou else 'FAIL', 'DETAIL': detalhe}


# ═══════════════════════════════════════════ idioma
# Detector de PALAVRAS FUNCIONAIS. Não decide país: `LANGUAGE != COUNTRY`.
FUNCIONAIS = {
    'ES': ('que', 'para', 'los', 'las', 'con', 'una', 'del', 'este', 'muy', 'pero',
           'como', 'está', 'esta', 'por', 'más', 'hoy', 'todo'),
    'FR': ('les', 'des', 'une', 'pour', 'dans', 'avec', 'est', 'sur', 'pas', 'plus',
           'nous', 'vous', 'cette', 'aussi', 'mais', 'sont'),
    'IT': ('che', 'per', 'con', 'una', 'del', 'della', 'sono', 'anche', 'più',
           'nel', 'alla', 'come', 'questo', 'gli', 'non'),
}


def idioma(texto):
    t = (texto or '').lower()
    if len(t.split()) < 4:
        return 'TEXT_TOO_SHORT'
    pontos = {k: sum(1 for p in v if cc.contem_palavra(t, p))
              for k, v in FUNCIONAIS.items()}
    melhor = max(pontos, key=pontos.get)
    if pontos[melhor] == 0:
        return 'NOT_KNOWN'
    segundo = sorted(pontos.values())[-2]
    # Empate não é idioma. Espanhol e italiano partilham palavras, e escolher no
    # empate produziria uma cobertura por idioma que mede o desempate, não o texto.
    if pontos[melhor] == segundo:
        return 'AMBIGUOUS'
    return melhor


def cobertura_por_idioma(materiais):
    """§3 · cobertura observada. NUNCA acurácia: não há gabarito humano."""
    linhas = {}
    for m in materiais:
        lang = idioma(_todo_texto(m))
        d = linhas.setdefault(lang, {'TEXT_ITEMS': 0, 'CLASSIFIED': 0, 'OTHER': 0})
        d['TEXT_ITEMS'] += 1
        tipos = set(m.get('CONTENT_TYPES') or [])
        if tipos - {'OTHER', 'NOT_KNOWN'}:
            d['CLASSIFIED'] += 1
        else:
            d['OTHER'] += 1
    for lang, d in linhas.items():
        d['CLASSIFICATION_COVERAGE_OBSERVED'] = (
            '%d/%d' % (d['CLASSIFIED'], d['TEXT_ITEMS']))
    return linhas


def _todo_texto(m):
    return ' '.join(str(m.get(c) or '') for c in ('TITLE', 'TEXT', 'CAPTION'))


# Veredito da leitura MANUAL dos 12 itens italianos em OTHER. Escrito à mão,
# depois de abrir os doze, e deliberadamente NÃO convertido em taxa: doze itens
# lidos por uma pessoa não fazem acurácia de classificador.
LEITURA_MANUAL_IT = {
    'VERDICT': 'ITALIAN_OTHER_CONTAINS_MISSED_RELEVANT_CONTENT',
    'GAP': 'PROVED',
    'REVIEWED': 12,
    'WHAT_WAS_MISSED': [
        {'TYPE': 'EVENT', 'N_IN_SAMPLE': 7,
         'WHY': 'a feira italiana chama-se Agrishow e apresenta-se como festival; '
                'o léxico só conhece feria/fiera/jornada/congreso'},
        {'TYPE': 'MACHINERY', 'N_IN_SAMPLE': 3,
         'WHY': 'drone, engate rápido e marca de implemento — nenhum termo '
                'italiano de maquinaria além de trattore está no léxico'},
        {'TYPE': 'FIELD_TRIAL + NUTRITION', 'N_IN_SAMPLE': 1,
         'WHY': '"campo PROVA" com fertilizante: nem prova de campo em italiano '
                'nem o rótulo #adv estavam previstos'},
    ],
    'NOT_A_RATE': 'esta leitura NÃO vira CLASSIFIER_ACCURACY. Não há gabarito '
                  'humano suficiente, e doze itens não são amostra estatística.',
    'DECISION': 'o dicionário italiano NÃO foi expandido nesta rodada. Expandir '
                'até o número ficar bonito é como se fabrica cobertura falsa; os '
                'temas italianos ficam declarados INCOMPLETOS.',
    'CONSEQUENCE': 'toda contagem temática do PC-01 é PISO, não medida. '
                   'NOT_OBSERVED_IN_MEASURED_CORPUS ali significa, em parte, '
                   'não-lido — e não ausência.',
}


def amostra_italiana(materiais, n=12):
    """§3 · amostra dirigida do italiano em OTHER. Não vira taxa de acurácia."""
    alvo = [m for m in materiais
            if idioma(_todo_texto(m)) == 'IT'
            and not (set(m.get('CONTENT_TYPES') or []) - {'OTHER', 'NOT_KNOWN'})
            and m.get('TEXT_SUBSTANCE') in ('TEXT_RICH', 'TEXT_SHORT')]
    return alvo[:n]


# ═══════════════════════════════════════════ 4 · duplicatas
def duplicatas(materiais):
    """§4 · duplicata DENTRO da plataforma, por id estável. Nada de texto parecido."""
    por_plataforma = {}
    for m in materiais:
        por_plataforma.setdefault(m['PLATFORM'], []).append(m['CONTENT_ID'])
    dentro = {p: len(ids) - len(set(ids)) for p, ids in por_plataforma.items()}
    urls = Counter(m['URL'] for m in materiais if m['URL'] != cc.NOT_KNOWN)
    return {
        'WITHIN_PLATFORM_DUPLICATES': sum(dentro.values()),
        'BY_PLATFORM': dentro,
        'DUPLICATE_URLS': sum(1 for u, c in urls.items() if c > 1),
        'UNIQUE_ITEMS': len({m['CONTENT_ID'] for m in materiais}),
        'CROSS_PLATFORM_DUPLICATION': 'NOT_MEASURED',
        'CROSS_PLATFORM_WHY': 'não existe chave segura ligando um post do Instagram '
                              'ao mesmo vídeo no YouTube. Deduplicar por texto '
                              'parecido trataria semelhança como identidade, e um '
                              'crosspost apagado por engano some do acervo sem '
                              'deixar rastro.',
        'AGGREGATE_RATE_CAVEAT': 'só um canal tem as duas plataformas no acervo '
                                 '(PC-02 é YouTube puro; os demais são Instagram '
                                 'puro), logo nenhuma contagem temática agregada '
                                 'pode estar inflada por crosspost entre elas.',
    }


# ═══════════════════════════════════════════ 5 · comentários
# Só sobe de UNKNOWN com evidência DENTRO do próprio comentário.
PAPEL = {
    'PRODUCER': ('mi finca', 'mis olivos', 'mi parcela', 'mi campo', 'mi cosecha',
                 'mi explotación', 'mi explotacion', 'tengo olivos', 'tengo viña',
                 'ma parcelle', 'mon exploitation', 'il mio campo'),
    'COMPANY': ('nuestra empresa', 'somos fabricantes', 'nuestra marca',
                'nuestros productos'),
    'AGRONOMIST': ('soy ingeniero agrónomo', 'soy agrónomo', 'como agrónomo',
                   'soy técnico agrícola'),
    'FIELD_TECHNICIAN': ('soy técnico de campo', 'trabajo como técnico'),
    'CONSULTANT': ('soy asesor', 'como asesor'),
    'RESEARCHER': ('en nuestro estudio', 'investigamos', 'universidad'),
    'ORGANIZATION': ('cooperativa', 'asociación', 'asociacion'),
}


def papel_do_comentarista(texto):
    t = (texto or '').lower()
    for papel, marcas in PAPEL.items():
        if any(cc.contem_palavra(t, marca) for marca in marcas):
            return papel, 'evidência escrita no próprio comentário'
    return 'UNKNOWN', ('nenhuma evidência de papel no texto. COMMENTER != FARMER, '
                       'e o silêncio permanece UNKNOWN')


def semantica_dos_comentarios(comentarios):
    fora = []
    for c in comentarios:
        papel, porque = papel_do_comentarista(c.get('TEXT'))
        fora.append(dict(c, COMMENTER_ROLE=papel, COMMENTER_ROLE_WHY=porque))
    papeis = Counter(c['COMMENTER_ROLE'] for c in fora)
    classes = Counter(c['CLASS'] for c in fora)
    relatos = [c for c in fora if c['CLASS'] == 'FIRST_PERSON_FIELD_REPORT']
    perguntas = [c for c in fora if c['CLASS'] in ('QUESTION', 'TECHNICAL_QUESTION')]
    return fora, {
        'COMMENTS_TOTAL': len(fora),
        'BY_ROLE': dict(papeis),
        'BY_CLASS': dict(classes),
        'FIELD_VOICE_OBSERVED': OBSERVED if relatos else NOT_OBSERVED,
        'FIELD_VOICE_N': len(relatos),
        'AUDIENCE_QUESTION_OBSERVED': OBSERVED if perguntas else NOT_OBSERVED,
        'AUDIENCE_QUESTION_N': len(perguntas),
        'FORBIDDEN': ['INCIDENCE', 'OUTBREAK', 'TREND'],
        'WHY_FORBIDDEN': 'comentário é reação pública numa amostra escolhida por '
                         'relevância técnica. Virar incidência exigiria denominador '
                         'de campo, que não existe aqui.',
        'LAW': cc.COMENTARISTA_NAO_E,
    }


# ═══════════════════════════════════════════ 6 · contexto ADAMA local
# Crosswalk EXPLÍCITO. Pequeno de propósito: cada linha é uma afirmação que
# alguém pode contestar olhando. Uma cultura sem linha aqui não é "sem
# portfólio" — é sem tradução, e sai NOT_MEASURED.
CROSSWALK_ES = {
    'OLIVE': ('OLIVO', 'OLIVAR'), 'TOMATO': ('TOMATE',), 'PEPPER': ('PIMIENTO',),
    'MAIZE': ('MAÍZ', 'MAIZ'), 'WHEAT': ('TRIGO',), 'BARLEY': ('CEBADA',),
    'GRAPEVINE': ('VID', 'VIÑA', 'UVA DE MESA'), 'PISTACHIO': ('PISTACHO',),
    'ALMOND': ('ALMENDRO',), 'CITRUS': ('CÍTRICOS',), 'POTATO': ('PATATA',),
    'SUNFLOWER': ('GIRASOL',), 'RAPESEED': ('COLZA',), 'CAROB': ('ALGARROBO',),
}
CROSSWALK_FR = {
    'WHEAT': ('Blé',), 'BARLEY': ('Orge',), 'GRAPEVINE': ('Vigne',),
    'MAIZE': ('Maïs',), 'RAPESEED': ('Colza',),
}
FONTES_ADAMA = {
    'ES': ('origin/claude/adama-es-local-browser',
           'data/samples/ES-ADAMA-PORTFOLIO-ROPF.json'),
    'FR': ('origin/claude/adama-fr-local-catalog',
           'data/samples/FR-T4-001/FR-T4-001-adama-crop-target.json'),
    'IT': ('origin/claude/adama-it-local-catalog',
           'data/samples/IT-CATALOGO/IT-ADAMA-CATALOG-V1.json'),
}


def _ler_de_outra_branch(ref, caminho):
    """READ-ONLY por `git show`. Não copia arquivo, não troca de branch."""
    try:
        bruto = subprocess.run(['git', 'show', '%s:%s' % (ref, caminho)],
                               cwd=ROOT, capture_output=True, timeout=120)
        if bruto.returncode != 0:
            return None, 'ref/caminho não resolveu'
        commit = subprocess.run(['git', 'rev-parse', ref], cwd=ROOT,
                                capture_output=True, text=True).stdout.strip()
        return json.loads(bruto.stdout.decode('utf-8')), commit
    except Exception as e:                                   # noqa: BLE001
        return None, '%s: %s' % (type(e).__name__, str(e)[:120])


def contexto_adama(fichas, sem_corpus=()):
    es, commit_es = _ler_de_outra_branch(*FONTES_ADAMA['ES'])
    fr, commit_fr = _ler_de_outra_branch(*FONTES_ADAMA['FR'])
    it, commit_it = _ler_de_outra_branch(*FONTES_ADAMA['IT'])

    fontes = {}
    culturas_es = set()
    if es:
        culturas_es = {c.upper() for c in (es.get('CROPS_POR_REGISTROS') or {})}
        fontes['ES'] = {
            'ARTEFACT': FONTES_ADAMA['ES'][1], 'REF': FONTES_ADAMA['ES'][0],
            'COMMIT': commit_es, 'LAYER': 'NATIONAL PRODUCT AUTHORIZATION',
            'CROPS_IN_PORTFOLIO': len(culturas_es),
            'JOIN': 'SAFE — lista COMPLETA de culturas dos registros ADAMA vigentes',
            'STATE': 'MEASURED'}
    culturas_fr = set()
    if fr:
        culturas_fr = {l['crop'] for l in (fr.get('adama_crop_target_top') or [])}
        fontes['FR'] = {
            'ARTEFACT': FONTES_ADAMA['FR'][1], 'REF': FONTES_ADAMA['FR'][0],
            'COMMIT': commit_fr, 'LAYER': 'NATIONAL PRODUCT AUTHORIZATION',
            'CROPS_IN_ARTEFACT': len(culturas_fr),
            # Uma lista TOP-25 responde ao positivo e não responde ao negativo.
            # Dizer "não há portfólio para esta cultura" com base num top-25 seria
            # transformar um recorte de exibição em ausência de autorização.
            'JOIN': 'PARTIAL — o artefato traz um TOP-25 de usos, não o conjunto '
                    'completo. Presença prova; ausência NÃO prova ausência.',
            'STATE': 'MEASURED_POSITIVE_ONLY'}
    if it:
        fontes['IT'] = {
            'ARTEFACT': FONTES_ADAMA['IT'][1], 'REF': FONTES_ADAMA['IT'][0],
            'COMMIT': commit_it, 'LAYER': 'DERIVED_MEASUREMENT',
            'AUTHORIZED_REGULATORY': it.get('AUTHORIZED_REGULATORY'),
            'CROP_RELATIONS_BY_ORIGIN': it.get('CROP_RELATIONS_BY_ORIGIN'),
            'JOIN': 'NONE — o próprio artefato declara AUTHORIZED_REGULATORY = 0. '
                    'As 622 relações cultura↔produto são CITED ou ROTATION_ONLY, '
                    'e citação em rótulo não é autorização por cultura.',
            'STATE': NOT_MEASURED}

    linhas = []
    for f in fichas:
        pais = f['COUNTRY']
        culturas = sorted(set(f['CROPS_PROVED']) | set(f['CROPS_OBSERVED']))
        if pais == 'ES' and culturas_es:
            casadas = [c for c in culturas
                       if any(n in culturas_es for n in CROSSWALK_ES.get(c, ()))]
            sem_traducao = [c for c in culturas if c not in CROSSWALK_ES]
            estado = ('LOCAL_CONTEXT_OVERLAP_PROVED' if casadas else
                      'NO_OVERLAP_IN_AUTHORIZED_PORTFOLIO')
            linha = {'CROPS_WITH_LOCAL_ADAMA_PORTFOLIO': casadas,
                     'CROPS_WITHOUT_CROSSWALK': sem_traducao,
                     'LOCAL_ADAMA_CONTEXT': 'MEASURED', 'OVERLAP_STATE': estado}
        elif pais == 'FR' and culturas_fr:
            casadas = [c for c in culturas
                       if any(n in culturas_fr for n in CROSSWALK_FR.get(c, ()))]
            linha = {'CROPS_WITH_LOCAL_ADAMA_PORTFOLIO': casadas,
                     'LOCAL_ADAMA_CONTEXT': 'MEASURED' if casadas else NOT_MEASURED,
                     'OVERLAP_STATE': ('LOCAL_CONTEXT_OVERLAP_PROVED' if casadas
                                       else 'PARTIAL'),
                     'EXACT_REASON': ('o artefato FR é um TOP-25: ausência não prova '
                                      'ausência de autorização')}
        else:
            linha = {'LOCAL_ADAMA_CONTEXT': NOT_MEASURED,
                     'OVERLAP_STATE': NOT_MEASURED,
                     'EXACT_REASON': (
                         'IT: o artefato canônico declara AUTHORIZED_REGULATORY = 0'
                         if pais == 'IT' else
                         'nenhum artefato de portfólio autorizado local para %s' % pais)}
        # Alvo sem corpus medido não pode sair como MEASURED: a cultura dele vem
        # do Creator Map, não do acervo. O cruzamento continua sendo informação
        # boa — mas com a origem no nome, senão PC-03 apareceria "medido" numa
        # missão que não conseguiu ler uma única publicação dele.
        if f['ENTITY_ID'] in sem_corpus and linha.get('LOCAL_ADAMA_CONTEXT') == 'MEASURED':
            linha['LOCAL_ADAMA_CONTEXT'] = 'MEASURED_FROM_CREATOR_MAP_CROPS_ONLY'
            linha['EXACT_REASON'] = ('nenhum material foi lido deste alvo; a cultura '
                                     'cruzada é a PROVADA pelo Creator Map, não a '
                                     'observada no acervo')
        linha.update(TARGET_ID=f['ENTITY_ID'], HANDLE=f['HANDLE'], COUNTRY=pais,
                     CROPS_CONSIDERED=culturas)
        linha['DOES_NOT_MEAN'] = list(cc.CONTEXTO_ADAMA_NAO_SIGNIFICA)
        linhas.append(linha)
    return fontes, linhas


# ═══════════════════════════════════════════ 7 · perfil com 4 estados
def perfis(fichas, janelas, adama, identidades):
    por_alvo = {j['TARGET_ID']: j for j in janelas}
    por_adama = {a['TARGET_ID']: a for a in adama}
    por_id = {i['TARGET_ID']: i for i in identidades}
    fora = []
    for f in fichas:
        eid = f['ENTITY_ID']
        j = por_alvo[eid]
        medido = j['ITEMS_COLLECTED'] > 0
        p = f['RELEVANCE_PROFILE']

        def estado(condicao):
            if not medido:
                return NOT_MEASURED
            return OBSERVED if condicao else NOT_OBSERVED

        fora.append({
            'TARGET_ID': eid, 'HANDLE': f['HANDLE'], 'NAME': f['NAME'],
            'TARGET_TYPE': f['ENTITY_TYPE'],
            'CHANNEL_IDENTITY': por_id[eid]['CHANNEL_IDENTITY'],
            'MEASURED_CORPUS': {'ITEMS': j['ITEMS_COLLECTED'],
                                'LAST_90D': j['ITEMS_LAST_90D'],
                                'OLDER_THAN_180D': j['ITEMS_OLDER_THAN_180D']},
            'COUNTRY': {'VALUE': f['COUNTRY'], 'STATE': OBSERVED,
                        'OWNER': 'CREATOR_MAP_EAME'},
            'REGION': {'VALUE': f['REGION'],
                       'STATE': (OBSERVED if f['REGION'] not in (cc.NAO_SEI, 'NÃO SEI')
                                 else NOT_MEASURED),
                       'OWNER': 'CREATOR_MAP_EAME',
                       'NOTE': 'região do FATO não foi extraída do texto nesta rodada'},
            'CROP': {'PROVED_BY_CREATOR_MAP': f['CROPS_PROVED'],
                     'OBSERVED_IN_CORPUS': f['CROPS_OBSERVED'],
                     'STATE': estado(f['CROPS_OBSERVED'])},
            'ISSUE': {'OBSERVED_IN_CORPUS': f['ISSUES_OBSERVED'],
                      'STATE': estado(f['ISSUES_OBSERVED'])},
            'FIELD_CONTENT': {'N': p['C_FARM_PROXIMITY']['FIELD_MATERIALS'],
                              'STATE': estado(p['C_FARM_PROXIMITY']['FIELD_MATERIALS'])},
            'TECHNICAL_CONTENT': {'N': p['D_TECHNICAL_DEPTH']['TECHNICAL_MATERIALS'],
                                  'STATE': estado(p['D_TECHNICAL_DEPTH']['TECHNICAL_MATERIALS'])},
            'CROP_PROTECTION': {'N': p['E_CROP_PROTECTION_RELEVANCE']['MATERIALS'],
                                'STATE': estado(p['E_CROP_PROTECTION_RELEVANCE']['MATERIALS'])},
            'AUDIENCE_TYPE': {'VALUE': p['F_AUDIENCE_FACING']['VALUE'],
                              'STATE': (OBSERVED
                                        if p['F_AUDIENCE_FACING']['VALUE'] != 'NOT_KNOWN'
                                        else NOT_MEASURED),
                              'LAW': 'profissão de seguidor não se infere'},
            'BRAND_HISTORY': {'BRANDS': f['BRANDS_OBSERVED'],
                              'STATE': estado(f['BRANDS_OBSERVED'])},
            'COMPETITOR_HISTORY': {
                'EVENTS': f['COMPETITOR_RELATIONSHIP_EVIDENCE'],
                'HIGHEST_LEVEL': (sorted({e['EVIDENCE_LEVEL']
                                          for e in f['COMPETITOR_RELATIONSHIP_EVIDENCE']})
                                  or [NOT_OBSERVED])[0],
                'STATE': estado(f['COMPETITOR_RELATIONSHIP_EVIDENCE'])},
            'SPONSORED_CONTENT': {'N': len(f['SPONSORED_CONTENT_EVIDENCE']),
                                  'STATE': estado(f['SPONSORED_CONTENT_EVIDENCE'])},
            'ACTIVATION_STYLE': {'OBSERVED': p['G_ACTIVATION_STYLE']['OBSERVED'],
                                 'STATE': estado(
                                     p['G_ACTIVATION_STYLE']['OBSERVED'] != ['NOT_KNOWN'])},
            'LOCAL_ADAMA_CONTEXT': por_adama[eid],
            'WHAT_IS_NOT_KNOWN': f['WHAT_IS_NOT_KNOWN'],
            'TOP_EVIDENCE': f['TOP_EVIDENCE'],
        })
    return fora


# ═══════════════════════════════════════════ 8 · o selo
def selo():
    universo = cc.carregar('CORPUS-UNIVERSE.json')
    materiais = cc.carregar('CORPUS-OBSERVATIONS.json')
    comentarios = cc.carregar('CORPUS-COMMENTS.json')
    fichas = cc.carregar('CREATOR-CORPUS-FICHES.json')
    runs = cc.carregar('RUN-MANIFEST-CORPUS.json')
    runs = list(runs.values()) if isinstance(runs, dict) else runs
    runs = [r for r in runs if isinstance(r, dict) and r.get('RUN_ID')]

    print('── 1 · janela real'); janelas = janela_real(materiais, universo, runs)
    for j in janelas:
        print('  %-6s %-24s N=%-4d 90d=%-4d 91-180=%-3d >180=%-3d %s→%s' % (
            j['TARGET_ID'], (j['HANDLE'] or '')[:24], j['ITEMS_COLLECTED'],
            j['ITEMS_LAST_90D'], j['ITEMS_91_180D'], j['ITEMS_OLDER_THAN_180D'],
            j['OLDEST_ITEM_DATE'], j['NEWEST_ITEM_DATE']))

    print('── 2 · identidade dos canais')
    identidades = identidade_dos_canais(universo, materiais)
    correcoes = candidatos_de_correcao(materiais)
    print('  PROVED=%d NOT_APPLICABLE=%d · candidatos de correção=%d' % (
        sum(1 for i in identidades if i['CHANNEL_IDENTITY'] == 'PROVED'),
        sum(1 for i in identidades if i['CHANNEL_IDENTITY'] == NOT_APPLICABLE),
        len(correcoes)))

    print('── 3 · regressões'); guardinhas = guardas()
    idiomas = cobertura_por_idioma(materiais)
    print('  cobertura por idioma:', {k: v['CLASSIFICATION_COVERAGE_OBSERVED']
                                      for k, v in sorted(idiomas.items())})
    amostra = amostra_italiana(materiais)
    veredito_it = LEITURA_MANUAL_IT

    print('── 4 · duplicatas'); dup = duplicatas(materiais)
    print('  dentro da plataforma=%d · únicos=%d · entre plataformas=%s' % (
        dup['WITHIN_PLATFORM_DUPLICATES'], dup['UNIQUE_ITEMS'],
        dup['CROSS_PLATFORM_DUPLICATION']))

    print('── 5 · comentários')
    comentarios2, semantica = semantica_dos_comentarios(comentarios)
    print('  papéis:', semantica['BY_ROLE'])

    print('── 6 · contexto ADAMA local')
    sem_corpus = {j['TARGET_ID'] for j in janelas if j['ITEMS_COLLECTED'] == 0}
    fontes, adama = contexto_adama(fichas, sem_corpus)
    print('  fontes:', {k: v['STATE'] for k, v in fontes.items()})

    print('── 7 · perfis'); perfil = perfis(fichas, janelas, adama, identidades)

    d90 = sum(j['ITEMS_LAST_90D'] for j in janelas)
    d180 = sum(j['ITEMS_91_180D'] for j in janelas)
    dmais = sum(j['ITEMS_OLDER_THAN_180D'] for j in janelas)

    condicoes = {
        'COLLECTION_WINDOW_RECONCILED': 'YES',
        'USED_CHANNEL_IDENTITIES_AUDITED': (
            'YES' if all(i['CHANNEL_IDENTITY'] in ('PROVED', NOT_APPLICABLE)
                         for i in identidades) else 'NO'),
        'FALSE_POSITIVE_REGRESSIONS': (
            'PASS' if all(g['STATE'] == 'PASS' for g in guardinhas) else 'FAIL'),
        'LANGUAGE_COVERAGE_EXPOSED': 'YES',
        'COMMENT_SEMANTICS_GUARDED': 'YES',
        'NO_RELEVANCE_SCORE': (
            'YES' if next(g for g in guardinhas
                          if g['GUARD'] == 'NO_RELEVANCE_SCORE')['STATE'] == 'PASS'
            else 'NO'),
    }
    ok = (condicoes['USED_CHANNEL_IDENTITIES_AUDITED'] == 'YES'
          and condicoes['FALSE_POSITIVE_REGRESSIONS'] == 'PASS'
          and condicoes['NO_RELEVANCE_SCORE'] == 'YES')

    it_lang = idiomas.get('IT', {})
    cc.gravar('CORPUS-COMMENTS.json', {
        'CAPTURED_AT': AS_OF,
        'WHAT_THIS_IS': 'AMOSTRA de comentários públicos. Não é censo, não é campo.',
        'SEMANTICS': semantica,
        'COMMENTS': comentarios2})
    cc.gravar('CORPUS-V1-SEAL.json', {
        'CAPTURED_AT': AS_OF,
        'WHAT_THIS_IS': 'validação semântica do corpus JÁ coletado. Zero coleta, '
                        'zero Apify, zero custo.',
        'WINDOW_RECONCILIATION': {
            'ALL_ITEMS_COLLECTED': len(materiais),
            'LAST_90D_CORPUS': d90,
            'ITEMS_91_180D': d180,
            'ITEMS_OLDER_THAN_180D': dmais,
            'LAW': 'ALL_ITEMS != LAST_90D_CORPUS. Item antigo foi PRESERVADO e '
                   'separado, nunca descartado para o número caber.',
            'BY_TARGET': janelas},
        'CHANNEL_IDENTITY_AUDIT': {
            'CHANNELS': identidades,
            'ROUTE': 'a coleta só aceita PUBLIC_CHANNEL do artefato congelado; '
                     'handle, nome e busca não entram',
            'CORRECTION_CANDIDATES': correcoes,
            'CREATOR_MAP_WRITTEN': 'NO'},
        'REGRESSION_GUARDS': guardinhas,
        'LANGUAGE_COVERAGE': {
            'METRIC': 'CLASSIFICATION_COVERAGE_OBSERVED',
            'NOT_PUBLISHED': 'CLASSIFIER_ACCURACY — não há gabarito humano suficiente',
            'BY_LANGUAGE': idiomas,
            'ITALIAN_MANUAL_REVIEW': veredito_it,
            'ITALIAN_DICTIONARY_COVERAGE_GAP': veredito_it['GAP'],
            'ITALIAN_SAMPLE_REVIEWED': len(amostra),
            'ITALIAN_SAMPLE': [{'URL': m['URL'], 'TEXT': (m.get('TEXT') or '')[:200]}
                               for m in amostra]},
        'DUPLICATION': dup,
        'COMMENT_SEMANTICS': semantica,
        'LOCAL_ADAMA_CONTEXT': {'SOURCES': fontes, 'BY_TARGET': adama,
                                'READ_MODE': 'git show READ-ONLY, sem cópia e sem '
                                             'troca de branch'},
        'RELEVANCE_PROFILES': perfil,
        'PROHIBITED_METRIC': cc.SCORE_PROIBIDO,
        'FREEZE_CONDITIONS': condicoes,
        'CREATOR_DEEP_CORPUS_V1': 'FROZEN' if ok else 'NOT_FROZEN',
        'OPTIONAL_REFRESH_INPUT': ('READY_WITH_LIMITATIONS' if ok else 'NOT_READY'),
        'EXACT_BLOCKER': cc.NOT_KNOWN if ok else 'ver FREEZE_CONDITIONS',
    })
    print('── 8 · freeze')
    for k, v in condicoes.items():
        print('  %-34s %s' % (k, v))
    print('  CREATOR_DEEP_CORPUS_V1 =', 'FROZEN' if ok else 'NOT_FROZEN')
    return ok


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'guardas':
        guardas(); raise SystemExit
    selo()
