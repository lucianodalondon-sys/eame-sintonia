"""Diagnostico: por que o ingresso recusou as duas observacoes do canario.

Corre a cadeia offline (bytes do disco) e imprime o DETALHE de cada quebra de
contrato. Nao e prova: e bisturi.
"""
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in ('coleta', 'leis', 'regras', 'guarda', 'medidas', ''):
    sys.path.insert(0, os.path.join(RAIZ, g) if g else RAIZ)
import _gavetas  # noqa: F401

import scrap_http as http
import adaptador_linkedin as al
import ingresso as ing
import artefato as art
import proveniencia as pv

ORGANIZACAO = 'https://www.linkedin.com/company/gruppocaviro/'

raw = []
for nome in sorted(os.listdir(os.path.join(RAIZ, 'data', 'samples', 'SOCIAL-IT',
                                           'raw-free', 'LINKEDIN'))):
    if nome.startswith('post-') and nome.endswith('.txt'):
        raw.append(json.load(io.open(os.path.join(RAIZ, 'data', 'samples', 'SOCIAL-IT',
                                                  'raw-free', 'LINKEDIN', nome),
                                     encoding='utf-8')))
mapa = {}
for j in raw:
    if j.get('RENDITION_CHOSEN') and j.get('VIDEO_STORAGE_LOCATION'):
        mapa[j['RENDITION_CHOSEN']] = j['VIDEO_STORAGE_LOCATION']
    if j.get('CAPTION_URL') and j.get('CAPTION_STORAGE_LOCATION'):
        mapa[j['CAPTION_URL']] = j['CAPTION_STORAGE_LOCATION']


def duble(url, **kw):
    p = os.path.join(RAIZ, mapa[url])
    return open(p, 'rb').read(), {'CONTENT_TYPE': 'video/mp4', 'STATUS': None, 'URL': url}


http.buscar_bytes = duble
objetos = al.video_da_pagina_publica(pagina_url=ORGANIZACAO, run_id='DIAG-D23',
                                    country_scope='IT', teto=2)
print('objetos:', len(objetos))
import scrap_colheita as SC
corrida = {'RUN_ID': 'DIAG-D23', 'STARTED_AT': art.agora()}
for i, o in enumerate(objetos):
    u = SC.unidade(o, run_id='DIAG-D23', fonte=None)
    f = ing.ficha(u, corrida=corrida, raiz=RAIZ)
    quebras = art.conferir(f) + pv.conferir_unidades_de_texto(u.get(pv.CAMPO_DAS_UNIDADES))
    print('--- item %d · ACTIVITY %s' % (i, (u.get('OBSERVACAO') or {}).get('RAW', {}).get('ACTIVITY_ID')))
    print('    STORAGE_LOCATION:', f.STORAGE_LOCATION)
    print('    CONTENT_TYPE    :', f.CONTENT_TYPE)
    print('    SHA256          :', f.SHA256[:16])
    print('    quebras         :', quebras if quebras else 'NENHUMA')
    if quebras:
        print('    unidades de texto:', json.dumps(u.get(pv.CAMPO_DAS_UNIDADES),
                                                   ensure_ascii=False)[:600])
