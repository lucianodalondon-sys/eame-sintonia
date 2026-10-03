"""Diagnostico 2: o que o dono do RAW respondeu, e por que nao gravou linha.

Nao e prova: e bisturi. Corre a cadeia com bytes do disco e imprime o recibo
inteiro do RAW, sem resumir.
"""
import io
import json
import os
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for g in ('coleta', 'leis', 'regras', 'guarda', 'medidas', ''):
    sys.path.insert(0, os.path.join(RAIZ, g) if g else RAIZ)
import _gavetas  # noqa: F401

import scrap_http as http
import adaptador_linkedin as al
import ingresso as ing
import scrap_colheita as SC
import artefato as art
from guarda.preservar_coleta import ArmazemLocal
from guarda.memoria_descartavel import MemoriaDescartavel

ORGANIZACAO = 'https://www.linkedin.com/company/gruppocaviro/'
pasta = os.path.join(RAIZ, 'data', 'samples', 'SOCIAL-IT', 'raw-free', 'LINKEDIN')
raw = [json.load(io.open(os.path.join(pasta, n), encoding='utf-8'))
       for n in sorted(os.listdir(pasta))
       if n.startswith('post-') and n.endswith('.txt')]
mapa = {}
for j in raw:
    if j.get('RENDITION_CHOSEN'):
        mapa[j['RENDITION_CHOSEN']] = j['VIDEO_STORAGE_LOCATION']
    if j.get('CAPTION_URL'):
        mapa[j['CAPTION_URL']] = j['CAPTION_STORAGE_LOCATION']
http.buscar_bytes = lambda u, **k: (open(os.path.join(RAIZ, mapa[u]), 'rb').read(),
                                    {'CONTENT_TYPE': 'video/mp4', 'STATUS': None, 'URL': u})

objetos = al.video_da_pagina_publica(pagina_url=ORGANIZACAO, run_id='DIAG2-D23',
                                    country_scope='IT', teto=2)
base = tempfile.mkdtemp(prefix='diag2-d23-')
memoria = MemoriaDescartavel(os.path.join(base, 'd.sqlite'))
unidades = [SC.unidade(o, run_id='DIAG2-D23', fonte=None) for o in objetos]
recibo = ing.receber(unidades, corrida={'RUN_ID': 'DIAG2-D23', 'STARTED_AT': art.agora()},
                     armazem=ArmazemLocal(base), memoria=memoria, raiz=RAIZ)
print('ACEITES:', len(recibo.get('ACEITES') or []))
print('RECUSAS:', json.dumps(recibo.get('RECUSAS'), ensure_ascii=False)[:300])
print('\n--- RAW ---')
print(json.dumps(recibo.get('RAW'), ensure_ascii=False, indent=1, default=str)[:2500])
print('\n--- linhas na base ---')
print('raw_asset:', len(memoria.objetos_da_corrida('DIAG2-D23')))
print('\n--- chaves do recibo ---')
print(sorted(recibo.keys()))
