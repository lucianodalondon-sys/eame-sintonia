#!/usr/bin/env python3
"""
OS POSTS DE QUEM A IDENTIDADE PERMITE — e a pergunta que a missão de fato faz.

A pergunta não é "quantos posts achamos?". É:

    AS VOZES HUMANAS ACRESCENTAM SINAL DE CAMPO, OU ANTECEDÊNCIA, AO SINTONIA?

Por isso este arquivo não conta posts. Ele os situa contra um caso datado —
`IT-CASE-DURUM-FUSARIUM-001`, Toscana/Grosseto, grano duro, fusariose, fioritura,
2026-04-23 — e pergunta de cada um: veio antes? fala da cultura? fala do problema?

QUEM ENTRA, E COM QUE PESO
---------------------------
Só alvo cuja identidade a busca resolveu. E o estado da identidade **viaja junto
com cada post**: nada que venha de um autor `PLAUSIBLE` pode ser lido depois como
se viesse de um `CONFIRMED`. Quatro dos oito ficaram em `NOT_ENOUGH_EVIDENCE` e
não são coletados — o que é resultado, não obstáculo.

    AUTHOR_IDENTITY_STATE viaja com o post, sempre.

A ARMADILHA DA JANELA
----------------------
`postedLimit` do ator é RELATIVO A HOJE: "6months" hoje (2026-08-30) começa em
março e cortaria janeiro e fevereiro da janela do caso em silêncio. Peço `year` e
filtro a janela eu mesmo, com a data de cada post. Deixar a fonte decidir a janela
seria o mesmo erro de sempre, com outra roupa.

    MONITORING WINDOW ≠ APPLICATION WINDOW

E O QUE ISTO NÃO PODE CONCLUIR
-------------------------------
Zero post relevante NÃO é "as vozes humanas não servem". Quatro autores, uma
plataforma, uma janela: é o que foi medido, e é pequeno. Um achado retrospectivo
— alguém falando de fusariose em julho sobre o que houve em abril — é contexto,
nunca antecedência.

    RETROSPECTIVE_FINDING ≠ EARLY_WARNING
    PAINEL MEDIDO ≠ PAÍS MEDIDO
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_contrato as ac        # noqa: E402
import apify_pool as ap            # noqa: E402
import coletor                     # noqa: E402
import fato_local as fl            # noqa: E402
import linkedin_prova_busca as pb  # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-LINKEDIN-POSTS.json')
ACTOR = 'harvestapi~linkedin-post-search'

CASE_DATE = datetime.date(2026, 4, 23)
JANELA = (datetime.date(2026, 1, 1), datetime.date(2026, 5, 31))
TETO_AUTORES = 8
TETO_POSTS_POR_AUTOR = 20
TETO_POSTS = 80

# Estados de identidade que autorizam coleta. NOT_ENOUGH e MISMATCH não entram:
# coletar posts de alguém que eu não sei quem é produziria "sinal" sem sujeito.
ELEGIVEIS = (pb.IDENTITY_CONFIRMED, pb.IDENTITY_PLAUSIBLE)

# `postedLimit` é relativo a hoje. Peço o máximo e filtro a janela do caso eu mesmo.
POSTED_LIMIT = 'year'

CULTURA = ('grano duro', 'frumento duro', 'grano', 'frumento', 'durum', 'cereal')
PROBLEMA = ('fusarios', 'fusarium', 'micotossin', 'don ', 'deossinivalen',
            'deoxynivalenol', 'spiga')
CAMPO = ('fioritura', 'spigatura', 'pioggia', 'umidit', 'sintom', 'infezion',
         'trattament', 'monitoraggio', 'campo', 'parcell', 'azienda agricola')


def entrada_de(urls, teto=TETO_POSTS_POR_AUTOR):
    """A entrada pretendida. Uma função só — a conferida e a executada."""
    return {'authorUrls': list(urls), 'maxPosts': teto, 'postedLimit': POSTED_LIMIT}


def _data(v):
    """Data de um post, tolerando os formatos que a fonte usa. Sem chute.

    A primeira versão cortava a string pelo COMPRIMENTO DA MÁSCARA — `t[:len(f)]`
    — e "%Y-%m-%dT%H:%M:%S" tem 17 caracteres para uma data de 19. Toda data
    virava `NOT_DATED_PRECISELY`, e todo post caía fora da janela do caso: um
    silêncio que se pareceria exatamente com "ninguém publicou nada".
    """
    if isinstance(v, dict):                     # a fonte às vezes aninha a data
        v = v.get('date') or v.get('iso') or v.get('timestamp')
    t = str(v or '').strip().replace('Z', '')
    if not t:
        return None
    for f in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S',
              '%Y-%m-%dT%H:%M', '%Y-%m-%d'):
        try:
            return datetime.datetime.strptime(t[:26], f).date()
        except ValueError:
            continue
    try:                                        # último recurso: só a data
        return datetime.datetime.strptime(t[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


def relativo(d):
    """Onde o post cai em relação ao caso. Sem data, não se inventa posição."""
    if d is None:
        return 'NOT_DATED_PRECISELY'
    if d < CASE_DATE - datetime.timedelta(days=7):
        return 'BEFORE_CASE'
    if d <= CASE_DATE + datetime.timedelta(days=7):
        return 'AROUND_CASE'
    return 'AFTER_CASE'


def relevancia(low, cultura_ok, problema_ok):
    """Cultura E problema fecham EXACT. Um só é vizinhança, não é o caso."""
    if cultura_ok and problema_ok:
        return 'EXACT_CASE_SIGNAL'
    if cultura_ok or problema_ok:
        return 'NEIGHBOURING_SIGNAL'
    if any(t in low for t in ('ricerca', 'studio', 'progetto', 'pubblicazione',
                              'convegno', 'sperimentazione')):
        return 'GENERAL_RESEARCH'
    return 'UNRELATED'


def ler_post(p, autor):
    texto = ''
    for chave in ('content', 'text', 'postContent', 'description'):
        v = p.get(chave)
        if isinstance(v, str) and v:
            texto = v
            break
    low = texto.lower()
    # Primeiro campo de data que a fonte realmente preencher. A versão anterior
    # misturava `or` e um `if` ternário numa expressão só, e a precedência fazia
    # o ternário engolir a cadeia inteira — outra forma de perder toda data.
    d = None
    for chave in ('postedAt', 'postedAtISO', 'publishedAt', 'date', 'postedDate'):
        d = _data(p.get(chave))
        if d:
            break
    cultura_ok = any(t in low for t in CULTURA)
    problema_ok = any(t in low for t in PROBLEMA)
    publicado = d.isoformat() if d else 'NOT_DATED_PRECISELY'

    # ---- LOCALIZAÇÃO, sob as leis importadas do Brasil ----------------------
    # Quatro espécies de lugar, e nenhuma promove a outra. O local declarado no
    # perfil do autor é BASE; a geotag do conteúdo é evidência do conteúdo; e o
    # FACT só existe onde o texto liga o acontecimento ao lugar.
    fatos, recusados = fl.localizacoes_do_fato(texto, origem='POST_TEXT')
    geo = p.get('geo') or p.get('location') or p.get('place')

    return {
        'AUTHOR': autor['NAME'],
        'AUTHOR_IDENTITY_STATE': autor['IDENTITY_STATE'],
        'AUTHOR_INSTITUTION_ASKED': autor.get('INSTITUTION_ASKED', 'NÃO SEI'),
        'VOICE_CLASS': autor.get('VOICE_CLASS', 'NÃO SEI'),
        'PROFILE_URL': autor.get('PROFILE_URL'),
        'POST_URL': p.get('linkedinUrl') or p.get('url') or p.get('postUrl'),

        # BASE — do perfil do autor. Nunca lida como local do fato.
        'AUTHOR_BASE': fl.local_declarado_do_perfil(
            autor.get('PROFILE_DECLARED_LOCATION'), origem='PROFILE.location'),
        # CONTENT_GEO_EVIDENCE — preservada, jamais promovida.
        'CONTENT_GEO_EVIDENCE': (fl.geo_do_conteudo(geo, origem='ACTOR.geo')
                                 if geo else None),
        # FACT — 0..N, cada uma com o trecho que a sustenta.
        'FACT_LOCATIONS': fatos,
        'FACT_LOCATIONS_COUNT': len(fatos),
        'PLACE_MENTIONS_REJECTED': recusados,

        # Tempo: dois campos, e o segundo só existe com evidência própria.
        'PUBLISHED_AT': publicado,
        **fl.tempo_do_fato(texto, publicado),

        'IN_CASE_WINDOW': bool(d and JANELA[0] <= d <= JANELA[1]),
        'RELATIVE_TO_CASE': relativo(d),
        'TEXT': texto[:1200],
        'CROP': 'grano duro' if 'duro' in low else ('frumento' if cultura_ok else 'NÃO SEI'),
        'ISSUE': 'fusariosi' if problema_ok else 'NÃO SEI',
        'FIELD_TERMS': sorted({t.strip() for t in CAMPO if t in low}),
        'CASE_RELEVANCE': relevancia(low, cultura_ok, problema_ok),
    }


def autores_elegiveis(identidades):
    """Do resultado de identidade para a lista de autores, com o estado colado.

    Escolhe, por alvo, o candidato do estado que resolveu o alvo — nunca o
    primeiro da lista. Ordenar por posição foi o defeito original desta missão.
    """
    fora = []
    for nome, v in sorted((identidades or {}).items()):
        estado = v.get('STATE')
        if estado not in ELEGIVEIS:
            continue
        escolhido = next((c for c in v.get('BY_CANDIDATE', [])
                          if c.get('IDENTITY_STATE') == estado), None)
        url = (escolhido or {}).get('PROFILE_URL')
        if not escolhido or not url or not str(url).startswith('http'):
            continue
        fora.append({'NAME': nome, 'IDENTITY_STATE': estado, 'PROFILE_URL': url,
                     'HEADLINE': escolhido.get('HEADLINE'),
                     'PROFILE_DECLARED_LOCATION': escolhido.get(
                         'PROFILE_DECLARED_LOCATION'),
                     'INSTITUTION_ASKED': v.get('INSTITUTION_ASKED', 'NÃO SEI')})
    return fora[:TETO_AUTORES]


def medir(posts, autores, identidades):
    """A resposta à pergunta da missão, com o que ela NÃO responde ao lado."""
    janela = [p for p in posts if p['IN_CASE_WINDOW']]
    exatos = [p for p in janela if p['CASE_RELEVANCE'] == 'EXACT_CASE_SIGNAL']
    vizinhos = [p for p in janela if p['CASE_RELEVANCE'] == 'NEIGHBOURING_SIGNAL']
    antes = [p for p in exatos if p['RELATIVE_TO_CASE'] == 'BEFORE_CASE']
    campo = [p for p in janela if p['FIELD_TERMS']]

    if antes:
        veredito = 'HUMAN_SENSOR_ADDS_ANTICIPATION'
    elif exatos:
        veredito = 'HUMAN_SENSOR_ADDS_CONTEXT_NOT_ANTICIPATION'
    elif vizinhos or campo:
        veredito = 'HUMAN_SENSOR_ADJACENT_ONLY'
    else:
        veredito = 'HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL'
    # As localizações do fato, agregadas SEM somar espécies diferentes.
    todos_fatos = [f for p in janela for f in p['FACT_LOCATIONS']]
    lugares = {}
    for f in todos_fatos:
        chave = (f['FACT_LOCATION'], f['FACT_LOCATION_PRECISION'])
        lugares.setdefault(chave, []).append(f)
    return {
        'FACT_LOCATIONS_FOUND': [
            {'FACT_LOCATION': k[0], 'FACT_LOCATION_PRECISION': k[1],
             'MENTIONS': len(v),
             'EVIDENCE': [f['FACT_LOCATION_EVIDENCE'] for f in v][:3],
             'TYPES_OF_EVIDENCE': sorted({f['TYPE_OF_EVIDENCE'] for f in v})}
            for k, v in sorted(lugares.items())],
        'OCCURRENCE_NOT_INCIDENCE': fl.ocorrencia_nao_e_incidencia(
            [f['TYPE_OF_EVIDENCE'] for f in todos_fatos]),
        'PLACE_MENTIONS_REJECTED_TOTAL': sum(
            len(p['PLACE_MENTIONS_REJECTED']) for p in posts),
        'AUTHORS_COLLECTED': len(autores),
        'AUTHORS_BY_IDENTITY_STATE': {
            e: sum(1 for a in autores if a['IDENTITY_STATE'] == e) for e in ELEGIVEIS},
        'AUTHORS_NOT_COLLECTED': sorted(
            n for n, v in (identidades or {}).items() if v.get('STATE') not in ELEGIVEIS),
        'POSTS_READ': len(posts),
        'POSTS_IN_CASE_WINDOW': len(janela),
        'POSTS_NOT_DATED': sum(1 for p in posts
                               if p['PUBLISHED_AT'] == 'NOT_DATED_PRECISELY'),
        'EXACT_CASE_SIGNALS': len(exatos),
        'NEIGHBOURING_SIGNALS': len(vizinhos),
        'WITH_FIELD_TERMS': len(campo),
        'EXACT_BEFORE_CASE': len(antes),
        'HUMAN_SENSOR_VERDICT': veredito,
        'VERDICT_MUST_CARRY': {
            'SCOPE': '%d autores, LinkedIn, janela %s a %s' % (
                len(autores), JANELA[0], JANELA[1]),
            'NOT_MEASURED': ('Instagram, YouTube, Meta; os 4 alvos sem identidade '
                             'resolvida; qualquer voz fora dos 8 nomes'),
            'ZERO_IS_NOT_ABSENCE': ('zero sinal neste painel não é "as vozes humanas '
                                    'não servem" — é este painel, pequeno, medido'),
            'ANTICIPATION_RULE': 'achado depois do caso é contexto, nunca antecedência',
            'LOCATION_RULE': ('FACT_LOCATION só existe com trecho que ligue o '
                              'acontecimento ao lugar; BASE, OPERATING, INFLUENCE '
                              'e geotag nunca são promovidos a FACT'),
            'INCIDENCE_RULE': ('ocorrência observada não é incidência, prevalência '
                               'nem pressão regional'),
            'STILL_FORBIDDEN': ['ITALY OPPORTUNITY', 'SALES OPPORTUNITY',
                                'ADAMA SHOULD ACT', 'MARKET GAP'],
        },
    }


def executar():
    hoje = datetime.date.today().isoformat()
    out = {'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
           'SOURCE_ID': 'DERIVED/IT-LINKEDIN-POSTS',
           'source': 'Apify %s — posts de autores com identidade resolvida' % ACTOR,
           'SOURCE_LOCATION': 'LinkedIn', 'FACT_LOCATION': 'ITALY',
           'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
           'captured_at': hoje, 'CAPTURED_AT': hoje,
           'CASE_DATE': CASE_DATE.isoformat(),
           'WINDOW': [JANELA[0].isoformat(), JANELA[1].isoformat()],
           'ACTOR': ACTOR,
           'CAPS': {'AUTHORS': TETO_AUTORES, 'POSTS_PER_AUTHOR': TETO_POSTS_POR_AUTOR,
                    'POSTS': TETO_POSTS, 'NOTE': 'o teto é do escopo, não do pool'},
           'POSTED_LIMIT_ASKED': POSTED_LIMIT,
           'WHY_NOT_A_TIGHTER_LIMIT': ('postedLimit é relativo a hoje; "6months" '
                                       'cortaria janeiro e fevereiro da janela do '
                                       'caso em silêncio'),
           'TOKEN_VALUE_LOGGED': 'NO', 'TOKEN_VALUE_COMMITTED': 'NO',
           'LAWS': ['AUTHOR_IDENTITY_STATE viaja com o post',
                    'BASE ≠ OPERATING ≠ INFLUENCE ≠ FACT',
                    'PLACE_MENTION ≠ FACT_LOCATION',
                    'TERRITORIAL_LIST ≠ FACT_LIST',
                    'GEOTAG ≠ FACT_LOCATION',
                    'PUBLISHED_AT ≠ FACT_TIME',
                    'ROW_PROVENANCE ≠ VALUE_PROVENANCE',
                    'OCCURRENCE ≠ INCIDENCE',
                    'MONITORING WINDOW ≠ APPLICATION WINDOW',
                    'RETROSPECTIVE_FINDING ≠ EARLY_WARNING',
                    'MEDIA_SIGNAL ≠ FIELD_SIGNAL',
                    'PAINEL MEDIDO ≠ PAÍS MEDIDO']}

    ks = ap.pool()
    if not ks:
        out['STATE'], out['HUMAN_SENSOR_VERDICT'] = 'APIFY_ENV_MISSING', 'NOT_MEASURED'
        return out

    # ------------------------------------------- identidade, do RAW já pago
    ident_out = {}
    itens = pb.reler_raw()
    if not itens:
        out['STATE'] = 'IDENTITY_RAW_NOT_PRESENT'
        out['HUMAN_SENSOR_VERDICT'] = 'NOT_MEASURED'
        out['WHY'] = ('sem o RAW da busca não há identidade resolvida, e sem ela '
                      'coletar posts produziria sinal sem sujeito')
        return out
    pb.ler_itens(itens, ident_out)
    identidades = ident_out.get('IDENTITY_BY_TARGET') or {}
    out['IDENTITY_SOURCE'] = 'RAW já pago da busca por nome — 0 execuções novas'
    out['IDENTITY_BY_TARGET'] = {n: v['STATE'] for n, v in identidades.items()}

    autores = autores_elegiveis(identidades)
    out['AUTHORS'] = [{k: a[k] for k in ('NAME', 'IDENTITY_STATE', 'HEADLINE',
                                         'PROFILE_URL', 'INSTITUTION_ASKED')}
                      for a in autores]
    if not autores:
        out['STATE'] = 'NO_ELIGIBLE_AUTHOR'
        out['HUMAN_SENSOR_VERDICT'] = 'NOT_MEASURED'
        out['WHY'] = 'nenhum alvo chegou a CONFIRMED ou PLAUSIBLE'
        return out

    # ------------------------------------------------------ portão contrato
    modelo = entrada_de([autores[0]['PROFILE_URL']])
    try:
        meta, schema = ac.contrato(ACTOR, ks[0])
        props, req = ac.campos_do_schema(schema)
        conf = ac.conferir(props, req, modelo)
        conf['CONTRACT_FIELDS'] = sorted(props)
        conf['ACTOR_TITLE'] = meta.get('title')
    except Exception as e:
        conf = {'STATE': ac.CONTRACT_NOT_READABLE, 'ERROR': ap.redigir(str(e))[:180]}
    out['CONTRACT'] = conf
    if conf['STATE'] not in (ac.CONTRACT_MATCH, ac.CONTRACT_NOT_READABLE):
        out['STATE'] = 'CONTRACT_REFUSED_SPEND'
        out['HUMAN_SENSOR_VERDICT'] = 'NOT_MEASURED'
        out['NEW_ACTOR_RUNS'] = 0
        return out

    # --------------------------------------------------------------- coleta
    def trabalho(autor, token):
        entrada = entrada_de([autor['PROFILE_URL']])
        itens, man = coletor.executar(
            ACTOR, entrada, token=token,
            run_id='IT-LI-POSTS-%s' % autor['NAME'].replace(' ', '-'),
            platform='LINKEDIN', country='IT', mission='HUMAN-SENSOR-LINKEDIN-POSTS',
            query=ap.redigir(json.dumps(entrada, ensure_ascii=False)),
            source_version=hoje,
            evidence_path='data/samples/IT-CASOS/IT-LINKEDIN-POSTS.json')
        est = ap.classificar(status=None if man['STATUS'] == 'SUCCESS' else 'FAILED',
                             status_message=str(man.get('ERROR') or ''), itens=itens)
        coletor.registrar(man, item_count_normalized=len(itens or []))
        return ([dict(i, _AUTOR=autor['NAME']) for i in (itens or [])
                 if isinstance(i, dict)], est)

    r = ap.executar_com_pool(
        autores, trabalho, teto_itens=TETO_POSTS,
        identidade=lambda i: (i.get('_AUTOR'),
                              i.get('linkedinUrl') or i.get('url')
                              or str(i.get('content'))[:120]))
    out['NEW_ACTOR_RUNS'] = len(r['UNITS_DONE'])
    out['POOL'] = {'TOKENS_AVAILABLE': r['TOKENS_AVAILABLE'],
                   'TOKENS_USED': r['TOKENS_USED'], 'STATE': r['STATE'],
                   'BY_POSITION': r['BY_POSITION'],
                   'UNITS_DONE': [u['NAME'] for u in r['UNITS_DONE']],
                   'UNITS_PENDING': [u['NAME'] for u in r['UNITS_PENDING']]}

    por_nome = {a['NAME']: a for a in autores}
    posts = [ler_post({k: v for k, v in p.items() if k != '_AUTOR'},
                      por_nome[p['_AUTOR']]) for p in r['ITEMS'] if p.get('_AUTOR')]
    out['RAW_FIELD_MAP'] = {}
    for p in r['ITEMS'][:40]:
        out['RAW_FIELD_MAP'].update(
            pb.esqueleto({k: v for k, v in p.items() if k != '_AUTOR'}))
    out['POSTS'] = posts
    out['STATE'] = 'MEASURED'
    out.update(medir(posts, autores, identidades))
    return out


def main():
    out = executar()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        fh.write(ap.redigir(json.dumps(out, ensure_ascii=False, indent=2)))
    print('STATE   =', out.get('STATE'))
    print('autores =', out.get('AUTHORS_COLLECTED', 0),
          '| runs =', out.get('NEW_ACTOR_RUNS', 0),
          '| posts =', out.get('POSTS_READ', 0),
          '| na janela =', out.get('POSTS_IN_CASE_WINDOW', 0))
    for a in out.get('AUTHORS', []):
        print('   %-20s %-30s %s' % (a['NAME'][:20], a['IDENTITY_STATE'],
                                     (a['HEADLINE'] or '')[:50]))
    for campo, tipo in sorted((out.get('RAW_FIELD_MAP') or {}).items())[:50]:
        print('   RAW %-42s %s' % (campo[:42], tipo))
    for p in out.get('POSTS', [])[:40]:
        if p['CASE_RELEVANCE'] != 'UNRELATED' or p['IN_CASE_WINDOW']:
            print('   %-18s %-11s %-22s %s' % (
                p['AUTHOR'][:18], p['PUBLISHED_AT'], p['CASE_RELEVANCE'],
                p['TEXT'][:60].replace('\n', ' ')))
    for f in out.get('FACT_LOCATIONS_FOUND', []):
        print('   FACT %-18s %-13s x%d  %s' % (
            f['FACT_LOCATION'][:18], f['FACT_LOCATION_PRECISION'], f['MENTIONS'],
            ', '.join(f['TYPES_OF_EVIDENCE'])))
    print('mencoes de lugar recusadas =', out.get('PLACE_MENTIONS_REJECTED_TOTAL', 0))
    print('EXACT =', out.get('EXACT_CASE_SIGNALS', 0),
          '| vizinhos =', out.get('NEIGHBOURING_SIGNALS', 0),
          '| com termo de campo =', out.get('WITH_FIELD_TERMS', 0),
          '| EXACT antes do caso =', out.get('EXACT_BEFORE_CASE', 0))
    print('VEREDITO =', out.get('HUMAN_SENSOR_VERDICT'))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
