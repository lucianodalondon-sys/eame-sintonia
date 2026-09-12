#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O processo que morre DENTRO do boundary comum — C10.6C.

    py provas/_c106c_filho.py <CLASSE> <RUN_ID> [MORRER]

`CLASSE` ∈ MEDIA · API · JSON. Com `MORRER`, o processo faz `os._exit(97)` logo
depois de a etapa `CHECK` fechar — ou seja, com a RUN já aberta e o trabalho por
fazer. O que sobrevive é o que o boundary tinha escrito, e mais nada.

    A PROVA DE QUE A INFRAESTRUTURA É COMUM É ELA PARTIR-SE IGUAL EM TODAS.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

CLASSE, RUN = sys.argv[1], sys.argv[2]
MORRER = len(sys.argv) > 3 and sys.argv[3] == 'MORRER'

import coleta_checkpoint as ck   # noqa: E402
import scrap_http as http        # noqa: E402
import scrap_registo as reg      # noqa: E402

reg.carregar_adaptadores()
# ⚠️ O ACERVO REAL NÃO RECEBE PROVA. É lei da casa desde a C2, e esta prova
# atravessa rotas que GRAVAM bruto antes de normalizar. Sem isto, correr a
# prova deixava ficheiros em `data/samples/` — e os guardas da casa
# apanharam-nos, que é o que eles existem para fazer.
#
#     UMA PROVA QUE SUJA O ACERVO MEDE-SE A SI PRÓPRIA DEPOIS.
import tempfile
import social_envelope as env
env.RAW_DIR = tempfile.mkdtemp(prefix='c106c-raw-')
http.permitido = lambda url: (True, 'fixture: esta prova nao sai')
http.buscar = lambda url, *a, **k: json.dumps([{
    'id': '1', 'uri': 'https://mastodon.uno/users/x/statuses/1',
    'url': 'https://mastodon.uno/@x/1', 'content': '<p>fixture</p>',
    'created_at': '2026-09-01T10:00:00.000Z', 'language': 'it',
    'account': {'acct': 'x@mastodon.uno'}}])

BASE = ck.RelatorDeEtapas


def morrer(onde):
    print('MORRENDO_EM=%s PID=%d' % (onde, os.getpid()), flush=True)
    os._exit(97)


class MorreDepoisDoCheck(BASE):
    def fechar(self, linha, estado, **kw):
        etapa = next((e for (i, e, _t) in self.abertas if i == linha), None)
        fora = BASE.fechar(self, linha, estado, **kw)
        if etapa == 'CHECK' and MORRER:
            morrer('%s:CHECK_FECHADA' % CLASSE)
        return fora


if MORRER:
    ck.RelatorDeEtapas = MorreDepoisDoCheck

import scrap_executor as sx     # noqa: E402

banco = ck.Banco(os.environ['BANCO_DESCARTAVEL_URL'])
if CLASSE == 'MEDIA':
    midia = os.path.join(RAIZ, 'data', 'raw', 'REEL-MIDIA', 'C-FanW_CYMz.wav')
    kw = dict(platform='INSTAGRAM', capability='instagram.reel.capture',
              ident={'PLATFORM': 'INSTAGRAM', 'POST_ID': 'C106C-' + RUN},
              midia_ficheiro=midia, model_hint='tiny', guardar=False,
              oficina=os.path.join(RAIZ, 'data', 'raw', 'C10-6C-OFICINA'))
elif CLASSE == 'API':
    import youtube_oficial as yt

    class T:
        def __call__(self, url, *a, **k):
            return {'items': [{'id': {'kind': 'youtube#channel',
                                      'channelId': 'UCP'},
                               'snippet': {'title': 'C',
                                           'publishedAt': '2026-01-01T00:00:00Z',
                                           'description': 'f'}}],
                    'pageInfo': {'totalResults': 1}}
    kw = dict(platform='YOUTUBE', capability='youtube.search', termo='x',
              country_scope='IT', limit=1,
              sessao=yt.Sessao(api_key='FIXTURE', transporte=T()))
else:
    kw = dict(platform='MASTODON', capability='mastodon.hashtag.search',
              instancia='mastodon.uno', tag='agri', limit=1, country_scope='IT')

objetos, trace = sx.COLLECT(run_id=RUN, banco=banco, **kw)
print('TERMINOU objetos=%d RUN_STATUS=%s CHECKPOINT=%s'
      % (len(objetos or []), trace.get('RUN_STATUS'), trace.get('CHECKPOINT_ID')),
      flush=True)
raise SystemExit(0)
