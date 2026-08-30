#!/usr/bin/env python3
"""
LINKEDIN — a única porta que esta missão abre, e só para oito nomes.

Roda no GitHub Actions, onde vive a secret `APIFY_TOKEN_POOL`. Não roda no
contêiner de sessão, que nunca teve as chaves.

O TETO É DO ESCOPO, NÃO DO POOL
--------------------------------
Oito perfis, oitenta posts. Se a secret trouxer doze chaves, continua sendo
oito e oitenta. O pool existe para **resiliência** — sobreviver a uma chave
que esgota no meio —, nunca para volume. Há teste que prova que doze chaves
não elevam o teto.

DUAS ETAPAS, E A PRIMEIRA PODE MATAR A SEGUNDA
-----------------------------------------------
1. resolver o perfil de cada nome;
2. ler os posts do perfil na janela.

A etapa 2 só existe para nome que a etapa 1 resolveu. **`PROFILE ≠ CONTENT`**,
e o inverso também vale: sem perfil não há conteúdo a pedir. Se poucos nomes
resolverem, o resultado honesto é "não medido para os demais", não "eles não
publicaram".

O QUE ESTE ARQUIVO NÃO FAZ
---------------------------
Não descobre nomes novos. Não abre Instagram, YouTube, Meta nem OpenAlex. Não
paraleliza por haver várias chaves. E não grava token em lugar nenhum: tudo que
sai daqui passa por `apify_pool.redigir()`.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apify_pool as ap          # noqa: E402
import coletor                   # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS',
                    'IT-LINKEDIN-SENSOR-RUN.json')

CASE_DATE = datetime.date(2026, 4, 23)
JANELA = (datetime.date(2026, 1, 1), datetime.date(2026, 5, 31))
TETO_PERFIS = 8
TETO_POSTS = 80

# Os oito de sempre. NENHUM nome novo entra aqui.
ALVOS = [
    {'NAME': 'Pasquale De Vita', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali'},
    {'NAME': 'Nicola Pecchioni', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali'},
    {'NAME': 'Sabrina Locatelli', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA — Bergamo'},
    {'NAME': 'Francesca Nocente', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA'},
    {'NAME': 'Daniela Pacifico', 'VOICE_CLASS': 'RESEARCHER',
     'INSTITUTION': 'CREA'},
    {'NAME': 'Stefano Biagetti', 'VOICE_CLASS': 'TECHNICAL_FIELD_VOICE',
     'INSTITUTION': 'Consorzio Agrario di Ancona'},
    {'NAME': 'Giovanni Drei', 'VOICE_CLASS': 'TECHNICAL_FIELD_VOICE',
     'INSTITUTION': 'Bayer Crop Science Italia'},
    {'NAME': 'Federico Cavina', 'VOICE_CLASS': 'TECHNICAL_FIELD_VOICE',
     'INSTITUTION': 'Terremerse Soc. Coop.'},
]

# Significado, não palavra solta: estes termos apenas ORDENAM a leitura.
TERMOS = ('grano duro', 'frumento duro', 'fusarios', 'fusarium', 'fioritura',
          'spigatura', 'pioggia', 'umidit', 'sintom', 'rischio', 'malatti',
          'monitoraggio', 'difesa', 'micotossin')

ACTOR_PERFIL = os.environ.get('ACTOR_LINKEDIN_PROFILE', 'apimaestro~linkedin-profile-detail')
ACTOR_POSTS = os.environ.get('ACTOR_LINKEDIN_POSTS', 'apimaestro~linkedin-profile-posts')


def _data(v):
    for f in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ',
              '%Y-%m-%dT%H:%M:%SZ'):
        try:
            return datetime.datetime.strptime(str(v)[:len(f) + 4], f).date()
        except (ValueError, TypeError):
            continue
    return None


def relativo(d):
    if d is None:
        return 'NOT_DATED_PRECISELY'
    if d < CASE_DATE - datetime.timedelta(days=7):
        return 'BEFORE_CASE'
    if d <= CASE_DATE + datetime.timedelta(days=7):
        return 'AROUND_CASE'
    return 'AFTER_CASE'


def relevancia(texto, crop_ok, issue_ok):
    """CASE_RELEVANCE — cultura E problema, com data compatível, fecham EXACT."""
    if crop_ok and issue_ok:
        return 'EXACT_CASE_SIGNAL'
    if crop_ok or issue_ok:
        return 'NEIGHBOURING_SIGNAL'
    if any(t in texto for t in ('ricerca', 'studio', 'progetto', 'pubblicazione')):
        return 'GENERAL_RESEARCH'
    return 'UNRELATED'


def ler_post(p, alvo):
    txt = (p.get('text') or p.get('content') or p.get('postText') or '')
    low = txt.lower()
    d = _data(p.get('postedAtISO') or p.get('publishedAt') or p.get('date')
              or p.get('postedAt'))
    crop_ok = any(t in low for t in ('grano duro', 'frumento duro', 'grano', 'frumento'))
    issue_ok = any(t in low for t in ('fusarios', 'fusarium'))
    return {
        'AUTHOR': alvo['NAME'], 'ROLE': alvo['VOICE_CLASS'],
        'INSTITUTION': alvo['INSTITUTION'],
        'VOICE_CLASS': alvo['VOICE_CLASS'],
        'PROFILE_URL': alvo.get('PROFILE_URL'),
        'POST_URL': p.get('url') or p.get('postUrl'),
        'PUBLISHED_AT': d.isoformat() if d else 'NOT_DATED_PRECISELY',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'TEXT': txt[:1500],
        'CROP': 'grano duro' if 'duro' in low else ('frumento' if crop_ok else 'NÃO SEI'),
        'ISSUE': 'fusariosi' if issue_ok else 'NÃO SEI',
        'REGION': 'NÃO SEI',
        'MATCHED_TERMS': sorted({t for t in TERMOS if t in low}),
        'RELATIVE_TO_CASE': relativo(d),
        'CASE_RELEVANCE': relevancia(low, crop_ok, issue_ok),
        'IN_WINDOW': bool(d and JANELA[0] <= d <= JANELA[1]),
    }


def coletar():
    censo = ap.censo()
    saida = {
        'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
        'SOURCE_ID': 'DERIVED/IT-LINKEDIN-SENSOR-RUN',
        'source': 'LinkedIn via Apify, pool de chave única APIFY_TOKEN_POOL',
        'SOURCE_LOCATION': 'LinkedIn', 'FACT_LOCATION': 'ITALY',
        'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'CASE_DATE': CASE_DATE.isoformat(),
        'WINDOW': [JANELA[0].isoformat(), JANELA[1].isoformat()],
        'CAPS': {'PROFILES': TETO_PERFIS, 'POSTS': TETO_POSTS,
                 'NOTE': 'o teto é do escopo, não do pool'},
        'POOL': censo,
        'TOKEN_VALUE_LOGGED': 'NO', 'TOKEN_VALUE_COMMITTED': 'NO',
        'BRAZIL_PATTERN_REUSED': 'YES',
        'BRAZIL_PATTERN_SOURCE': ('portal-sintonia/credenciais.py — _separa, _descola, '
                                  '_sem_rotulo, formato_suspeito'),
    }
    if censo['TOKEN_POOL_PRESENT'] != 'YES':
        saida['STATE'] = 'APIFY_ENV_MISSING'
        saida['VERDICT'] = 'NOT_MEASURED'
        return saida

    # ---------------------------------------------------------- 1 · perfis
    def trabalho_perfil(alvo, token):
        entrada = {'searchQuery': '%s %s' % (alvo['NAME'], alvo['INSTITUTION']),
                   'maxItems': 3}
        itens, man = coletor.executar(
            ACTOR_PERFIL, entrada, token=token,
            run_id='IT-LI-PROF-%s' % alvo['NAME'].replace(' ', '-'),
            platform='LINKEDIN', country='IT', mission='HUMAN-SENSOR-LINKEDIN',
            query=ap.redigir(entrada['searchQuery']),
            source_version=datetime.date.today().isoformat(),
            evidence_path='data/samples/IT-CASOS/IT-LINKEDIN-SENSOR-RUN.json')
        est = ap.classificar(status=None if man['STATUS'] == 'SUCCESS' else 'FAILED',
                             status_message=str(man.get('ERROR') or ''), itens=itens)
        return ([dict(i, _ALVO=alvo['NAME']) for i in (itens or [])], est)

    r1 = ap.executar_com_pool(ALVOS[:TETO_PERFIS], trabalho_perfil,
                              identidade=lambda i: (i.get('_ALVO'),
                                                    i.get('publicIdentifier') or
                                                    i.get('profileUrl') or i.get('url')))
    saida['PROFILE_STAGE'] = {
        'TOKENS_AVAILABLE': r1['TOKENS_AVAILABLE'], 'TOKENS_USED': r1['TOKENS_USED'],
        'POOL_POSITION_USED': r1.get('POOL_POSITION_USED', []),
        'BY_POSITION': r1['BY_POSITION'], 'STATE': r1['STATE'],
        'UNITS_DONE': [u['NAME'] for u in r1['UNITS_DONE']],
        'UNITS_PENDING': [u['NAME'] for u in r1['UNITS_PENDING']],
        'DUPLICATES_REMOVED': r1['DUPLICATES_REMOVED'],
    }

    achados = {}
    for it in r1['ITEMS']:
        u = it.get('profileUrl') or it.get('url') or it.get('publicIdentifier')
        if u and it.get('_ALVO') not in achados:
            achados[it['_ALVO']] = u
    for a in ALVOS:
        a['PROFILE_URL'] = achados.get(a['NAME'])
        a['PROFILE_STATE'] = 'FOUND' if achados.get(a['NAME']) else 'NOT_FOUND'
    saida['PROFILES'] = [{'NAME': a['NAME'], 'VOICE_CLASS': a['VOICE_CLASS'],
                          'INSTITUTION': a['INSTITUTION'],
                          'PROFILE_STATE': a['PROFILE_STATE'],
                          'PROFILE_URL': a.get('PROFILE_URL')} for a in ALVOS]

    com_perfil = [a for a in ALVOS if a.get('PROFILE_URL')]
    if not com_perfil:
        saida['STATE'] = 'NO_PROFILE_RESOLVED'
        saida['POSTS'] = []
        return saida

    # ----------------------------------------------------------- 2 · posts
    def trabalho_posts(alvo, token):
        entrada = {'profileUrl': alvo['PROFILE_URL'], 'maxPosts': 20}
        itens, man = coletor.executar(
            ACTOR_POSTS, entrada, token=token,
            run_id='IT-LI-POST-%s' % alvo['NAME'].replace(' ', '-'),
            platform='LINKEDIN', country='IT', mission='HUMAN-SENSOR-LINKEDIN',
            query=ap.redigir(str(entrada)),
            source_version=datetime.date.today().isoformat(),
            evidence_path='data/samples/IT-CASOS/IT-LINKEDIN-SENSOR-RUN.json')
        est = ap.classificar(status=None if man['STATUS'] == 'SUCCESS' else 'FAILED',
                             status_message=str(man.get('ERROR') or ''), itens=itens)
        return ([dict(i, _ALVO=alvo['NAME']) for i in (itens or [])], est)

    r2 = ap.executar_com_pool(com_perfil, trabalho_posts,
                              identidade=lambda i: i.get('url') or i.get('postUrl')
                              or (i.get('_ALVO'), (i.get('text') or '')[:120]),
                              teto_itens=TETO_POSTS)
    por_nome = {a['NAME']: a for a in ALVOS}
    posts = [ler_post(p, por_nome[p['_ALVO']]) for p in r2['ITEMS']]
    saida['POST_STAGE'] = {
        'TOKENS_AVAILABLE': r2['TOKENS_AVAILABLE'], 'TOKENS_USED': r2['TOKENS_USED'],
        'POOL_POSITION_USED': r2.get('POOL_POSITION_USED', []),
        'BY_POSITION': r2['BY_POSITION'], 'STATE': r2['STATE'],
        'DUPLICATES_REMOVED': r2['DUPLICATES_REMOVED'],
    }
    saida['POSTS_READ'] = len(posts)
    saida['POSTS'] = posts
    saida['STATE'] = 'MEASURED'
    return saida


def main():
    out = coletar()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    texto = ap.redigir(json.dumps(out, ensure_ascii=False, indent=2))
    with open(DEST, 'w', encoding='utf-8') as fh:
        fh.write(texto)
    print('TOKEN_POOL_PRESENT =', out['POOL']['TOKEN_POOL_PRESENT'])
    print('TOKEN_POOL_SIZE    =', out['POOL']['TOKEN_POOL_SIZE'])
    print('STATE              =', out.get('STATE'))
    print('POSTS_READ         =', out.get('POSTS_READ', 0))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
