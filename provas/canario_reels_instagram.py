#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CANÁRIO REAL — REELS DO INSTAGRAM PELA CADEIA CANÓNICA.

    py provas/canario_reels_instagram.py [--perfil bayer_italia] [--reels 3]

O QUE ESTE CANÁRIO MEDE, E O QUE ELE **NÃO** MEDE
-------------------------------------------------
Mede, com rede a sério e a dinheiro ZERO:

    PERFIL → LISTA (embed, sem login) → REEL (URL directa)
        → cadeia do Reel (yt-dlp + ffprobe) → RAW (bytes + sha256)
        → DERIVED (TEXTO, pelo dono único do ASR, `fala_local`)
        → ingresso → Admissão (régua multilingue)

E mede o EGRESSO de cada passo: um canário que não diz de que país saiu não é
comparável com o próximo (mudar a rota de rede entre duas medições é mudar o
método).

NÃO mede: nada que fique na Sala real. O banco é DESCARTÁVEL e a RUN é cunhada
aqui — `DURAÇÃO DA PROVA != ESTADO DA CASA`.

Autorização: D22 (dono REAL, 2026-09-23) — Reels públicos por URL directa, sem
login, sem conta, sem rota paga, risco assumido por ele. A matriz declara os
três eixos e a plataforma continua `DISALLOWED` (robots.txt medido).
"""
import argparse
import io
import json
import os
import re
import sys
import time
import urllib.request
import uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
for _g in ('coleta', 'leis', 'ferramentas', 'regras', 'guarda', 'admissao',
           'medidas', 'pedido', 'orquestrador'):
    sys.path.insert(0, os.path.join(RAIZ, _g))
sys.path.insert(0, RAIZ)

import _gavetas  # noqa: E402,F401

import admissao as adm          # noqa: E402
import adaptador_instagram as ai  # noqa: E402
import derivacao_forward as dvf  # noqa: E402
import fala_local as fl         # noqa: E402
import ingresso as ing          # noqa: E402
import memoria_descartavel as md  # noqa: E402
import preservar_coleta as pc   # noqa: E402
import rota_forward_documento as rf  # noqa: E402
import scrap_colheita as SC     # noqa: E402

#: A fonte das contas de concorrência. Ela é DECLARADA no próprio conjunto de
#: contas (`CONTAS-V1.json` → `SOURCE_ID`), não inventada aqui — e o canário
#: usa-a tal como está. Se o ingresso a recusar, o canário PARA em vez de
#: trocar de nome até um passar.
FONTE = 'COMPETITOR-PUBLIC-COMM/CONTAS-V1'
PAIS = 'IT'
UNIVERSO = 'T10'
RUN = 'CANARIO-REEL-%s' % uuid.uuid4().hex[:8]
#: ⚠️ O UA DECIDE O QUE A PLATAFORMA SERVE, E ISSO FOI MEDIDO NESTA MISSÃO.
#:
#:     UA curto  («Mozilla/5.0 (Windows NT 10.0; Win64; x64)»)
#:         -> 200 · 322 KB · COM `graphql_media` (a lista dos itens)
#:     UA completo (Chrome/124 ...)
#:         -> 200 · 631 KB · SEM `graphql_media` (uma casca)
#:
#:     O MESMO ENDEREÇO, DOIS CONTEÚDOS DIFERENTES — E A DIFERENÇA NÃO ESTÁ
#:     NO PEDIDO: ESTÁ EM QUEM O PEDIDO DIZ SER.
#:
#: Por isso a descoberta TENTA os dois e DIZ qual serviu. Tentar um só e
#: concluir «não dá» seria medir a minha escolha, não a plataforma.
UAS = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
       '(KHTML, like Gecko) Chrome/124 Safari/537.36')


def egresso():
    """De que país e de que operadora esta prova saiu. Sem credencial."""
    try:
        with urllib.request.urlopen('https://ipinfo.io/json', timeout=20) as r:
            d = json.loads(r.read().decode('utf-8', 'replace'))
        return {'NETWORK_EXIT_COUNTRY': d.get('country'),
                'NETWORK_EXIT_REGION': d.get('region'),
                'NETWORK_EXIT_ORG': (d.get('org') or '')[:60],
                'NETWORK_EXIT_HOW': 'ipinfo.io — serviço público, sem credencial'}
    except Exception as e:                                     # noqa: BLE001
        return {'NETWORK_EXIT_COUNTRY': 'NAO SEI', 'NETWORK_EXIT_WHY':
                type(e).__name__}


def lista_de_reels(perfil, teto, relato):
    """Os Reels recentes do perfil, pelo EMBED público — sem login, sem conta.

    ⚠️ ESTA É A ROTA DE DESCOBERTA MEDIDA NESTA MISSÃO, e o que se mede é o
    que a plataforma responde a um pedido anónimo vindo DESTE egresso:

        GET /<perfil>/            -> 200, HTML com a bio e a grade
        GET /<perfil>/embed/      -> 200, HTML com `graphql_media` (os itens)
        GET /<perfil>/?__a=1&__d=dis -> 201 e ZERO bytes (não serve)

    O que sai daqui é ENDEREÇO, não conteúdo: o canário não lê legenda nem
    mídia desta resposta — só os `shortcode` dos itens que são vídeo, para
    depois pedir CADA UM pela porta autorizada (D22: por URL directa).
    """
    url = 'https://www.instagram.com/%s/embed/' % perfil
    relato['LIST_URL'] = url
    relato['LIST_TENTATIVAS'] = []
    corpo, estado = '', None
    for ua in UAS:
        pedido = urllib.request.Request(url, headers={'User-Agent': ua})
        t0 = time.time()
        with urllib.request.urlopen(pedido, timeout=45) as r:
            corpo = r.read().decode('utf-8', 'replace')
            estado = r.status
        tem = 'graphql_media' in corpo
        relato['LIST_TENTATIVAS'].append(
            {'UA': ua[:48], 'HTTP': estado, 'BYTES': len(corpo),
             'SEGUNDOS': round(time.time() - t0, 1),
             'TEM_GRAPHQL_MEDIA': tem})
        relato['LIST_UA_QUE_SERVIU'] = ua[:48] if tem else relato.get(
            'LIST_UA_QUE_SERVIU')
        if tem:
            break
    relato['LIST_HTTP_STATUS'] = estado
    relato['LIST_BYTES'] = len(corpo)
    relato['LIST_HAS_GRAPHQL_MEDIA'] = 'graphql_media' in corpo
    achados = []
    for m in re.finditer('GraphVideo', corpo):
        # O shortcode vem depois do `__typename` do MESMO item: procura-se à
        # frente, e não atrás, porque atrás estaria o item anterior.
        trecho = corpo[m.start():m.start() + 400]
        sc = re.search(r'shortcode\\*"?\s*:\s*\\*"([A-Za-z0-9_-]{5,20})', trecho)
        if sc:
            achados.append(sc.group(1))
    vistos, reels = set(), []
    for sc in achados:
        if sc not in vistos:
            vistos.add(sc)
            reels.append('https://www.instagram.com/reel/%s/' % sc)
    relato['LIST_ITENS_VIDEO'] = len(reels)
    return reels[:teto]


def um_reel(url, banco, armazem, relato):
    """Um reel, ponta a ponta, pela cadeia canónica. → o dicionário da prova."""
    linha = {'URL': url}
    t0 = time.time()
    objetos, trace = ai.capturar_reel(url=url, run_id=RUN)
    linha['CAPTURA_SEGUNDOS'] = round(time.time() - t0, 1)
    linha['CAPTURA_ESTADO'] = trace.get('CANONICAL_STATE')
    linha['CAPTURA_RESULTADO'] = trace.get('RESULT')
    if not objetos:
        linha['VEREDITO'] = 'SEM_OBJETO'
        return linha
    o = objetos[0]
    linha['POST_ID'] = o.get('POST_ID')
    linha['TRANSCRIPT_STATE'] = o.get('TRANSCRIPT_STATE')
    linha['TEXTO_CARACTERES'] = len(str(o.get('TRANSCRIPT_TEXT') or ''))
    linha['TEXTO_INICIO'] = str(o.get('TRANSCRIPT_TEXT') or '')[:90]
    linha['IDIOMA'] = (o.get('REEL') or {}).get('LANGUAGE') or o.get('LANGUAGE')
    linha['PUBLISHED_AT'] = (o.get('REEL') or {}).get('PUBLISHED_AT')
    linha['CAPTION_IS_NOT_TRANSCRIPT'] = bool(o.get('CAPTION_IS_NOT_TRANSCRIPT'))
    raw = o.get('RAW') or {}
    linha['RAW_SHA256'] = raw.get('SHA256')
    linha['RAW_BYTES'] = raw.get('BYTES')
    linha['RAW_CONTENT_TYPE'] = raw.get('CONTENT_TYPE')
    linha['RAW_STORAGE_LOCATION'] = raw.get('STORAGE_LOCATION')

    # ── a unidade do SCRAP (a língua da porta) ────────────────────────────
    u = SC.unidade(o, run_id=RUN, fonte=FONTE)
    linha['DOCUMENT_ID'] = u.get('DOCUMENT_ID')
    linha['DOCUMENT_ID_BASE'] = u.get('DOCUMENT_ID_BASE')
    linha['STORAGE_LOCATION'] = u.get('STORAGE_LOCATION')
    linha['CONTENT_TYPE'] = u.get('CONTENT_TYPE')
    linha['SOURCE_ID'] = u.get('SOURCE_ID')

    ficha = ing.ficha(u, corrida={'RUN_ID': RUN, 'STARTED_AT': _agora()})
    linha['FICHA_MEDIA_TYPE'] = getattr(ficha, 'CONTENT_TYPE', None)
    linha['FICHA_BYTES'] = ficha.BYTES
    linha['FICHA_SHA256'] = ficha.SHA256

    # ── RAW preservado no armazém descartável ─────────────────────────────
    caminho = raw.get('STORAGE_LOCATION')
    if not (caminho and os.path.isfile(caminho)):
        linha['VEREDITO'] = 'SEM_BYTES_EM_DISCO'
        return linha
    with io.open(caminho, 'rb') as f:
        dados = f.read()
    alvo = 'IT/reel/%s%s' % (ficha.SHA256[:16], os.path.splitext(caminho)[1])
    armazem.enviar(alvo, dados, getattr(ficha, 'CONTENT_TYPE', None))
    pai = _pai_no_banco(banco, ficha, alvo, u.get('DOCUMENT_ID'))

    # ── DERIVED: o TEXTO, pelo dono único do ASR ──────────────────────────
    unidade = {'RAW_ASSET_ID': pai, 'PDF': caminho,      # `PDF` é histórico
               'MEDIA_TYPE': ficha.MEDIA_TYPE, 'SOURCE_ID': FONTE,
               'CAPTURED_AT': _agora()}
    t0 = time.time()
    recibo = dvf.correr([unidade], banco_do_rastro=None, run_id=RUN,
                        armazem=armazem, memoria=banco, source_id=FONTE,
                        route_class_id=None, relogio=_agora)
    resultado = (recibo.get('RESULTADOS') or [{}])[0]
    linha['DERIVED_SEGUNDOS'] = round(time.time() - t0, 1)
    linha['DERIVED_PORTA'] = resultado.get('PORTA')
    linha['DERIVED_EXECUTOR'] = resultado.get('EXECUTOR_ID')
    linha['DERIVED_MOTIVO'] = resultado.get('MOTIVO')
    texto = ''
    derivado = (resultado.get('LINHA') or {}).get('storage_path')
    if derivado:
        try:
            texto = armazem.ler(derivado).decode('utf-8')
        except Exception as e:                                  # noqa: BLE001
            linha['DERIVED_LEITURA_FALHOU'] = type(e).__name__
    linha['DERIVED_CARACTERES'] = len(texto)
    linha['DERIVED_TEXTO_INICIO'] = texto[:90]

    # ── ingresso → Admissão (a régua multilingue) ─────────────────────────
    item = rf.item_para_a_porta({
        'CONTENT_ID': ficha.SHA256, 'TEXTO': texto, 'SOURCE_ID': FONTE,
        'ARTIFACT_TYPE': 'DERIVED', 'RAW_ASSET_ID': pai,
        'PARENT_SHA256': ficha.SHA256, 'CAPTURED_AT': _agora(), 'URL': url})
    decisao = adm.decidir(item, UNIVERSO, corrida=RUN)
    linha['ADMISSAO'] = decisao.resultado
    linha['ADMISSAO_ESTAGIO'] = (decisao.evidencia or {}).get('estagio')
    linha['VEREDITO'] = ('PONTA_A_PONTA' if (linha['DERIVED_PORTA'] == 'PASSED'
                                             and texto) else 'PARCIAL')
    return linha


def _agora():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).replace(
        microsecond=0).isoformat()


def _pai_no_banco(banco, ficha, caminho, document_key):
    tem_chave = bool(document_key and str(document_key).strip()
                     and str(document_key).strip().upper()
                     not in ('NAO SEI', 'NAO_SEI', 'UNKNOWN'))
    ident = ("'FORWARD_IDENTIFIED', '%s', '%s', 'SOURCE_DOCUMENT_ID'"
             % (FONTE, document_key) if tem_chave else
             "'FORWARD_IDENTITY_UNPROVEN', '%s', NULL, NULL" % FONTE)
    banco.aplicar(
        "insert into public.storage_object (storage_path, media_type, bytes, "
        "sha256, created_at) values ('%s','%s',%d,'%s','%s');"
        % (caminho, getattr(ficha, 'CONTENT_TYPE', None), ficha.BYTES, ficha.SHA256, _agora()))
    banco.aplicar(
        "insert into public.raw_asset (run_id, storage_path, media_type, bytes, "
        "sha256, captured_at, storage_object_id, identity_state, source_id, "
        "document_key, document_key_basis) "
        "select '%s','%s','%s',%d,'%s','%s', o.id, %s "
        "from public.storage_object o where o.storage_path = '%s';"
        % (RUN, caminho, getattr(ficha, 'CONTENT_TYPE', None), ficha.BYTES, ficha.SHA256,
           _agora(), ident, caminho))
    linhas = banco.con.execute(
        'select id from public.raw_asset order by id desc limit 1').fetchall()
    return int(linhas[0][0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--perfil', default='bayer_italia')
    ap.add_argument('--reels', type=int, default=3)
    ap.add_argument('--saida', default=os.path.join(
        RAIZ, 'data', 'samples', 'CANARIO-REELS-INSTAGRAM-V1.json'))
    args = ap.parse_args()

    relato = {'MISSION': 'REELS-FUNCIONANDO', 'RUN_ID': RUN, 'FONTE': FONTE,
              'PERFIL': args.perfil, 'TETO_DE_REELS': args.reels,
              'ASR_OWNER': 'ferramentas/fala_local.py',
              'ASR_DISPONIVEL': bool(fl.disponivel()),
              'AUTORIZACAO': 'D22 (2026-09-23) — Reels por URL directa, sem '
                             'login, sem conta, sem rota paga',
              'CUSTO_USD': 0}
    relato.update(egresso())
    import tempfile
    tmp = tempfile.mkdtemp(prefix='canario-reel-')
    relato['ARMAZEM_DESCARTAVEL'] = tmp
    armazem = pc.ArmazemLocal(tmp)
    banco = md.MemoriaDescartavel()

    t0 = time.time()
    reels = lista_de_reels(args.perfil, args.reels, relato)
    relato['REELS_ENCONTRADOS'] = reels
    relato['PROVA'] = [um_reel(u, banco, armazem, relato) for u in reels]
    relato['SEGUNDOS_TOTAIS'] = round(time.time() - t0, 1)
    relato['PONTA_A_PONTA'] = sum(1 for p in relato['PROVA']
                                  if p.get('VEREDITO') == 'PONTA_A_PONTA')
    relato['DE'] = len(relato['PROVA'])
    relato['RAWS'] = sum(1 for p in relato['PROVA'] if p.get('RAW_SHA256'))
    relato['DERIVED_COM_TEXTO'] = sum(1 for p in relato['PROVA']
                                      if p.get('DERIVED_CARACTERES'))
    relato['ADMISSOES'] = [p.get('ADMISSAO') for p in relato['PROVA']]

    os.makedirs(os.path.dirname(args.saida), exist_ok=True)
    with io.open(args.saida, 'w', encoding='utf-8') as f:
        json.dump(relato, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in relato.items() if k != 'PROVA'},
                     ensure_ascii=False, indent=1))
    for p in relato['PROVA']:
        print('--- %s · %s · RAW %s · DERIVED %s car · ADMISSAO %s' % (
            p.get('POST_ID'), p.get('VEREDITO'), str(p.get('RAW_SHA256'))[:12],
            p.get('DERIVED_CARACTERES'), p.get('ADMISSAO')))
    print('CANARIO: %d/%d ponta a ponta · gravado em %s'
          % (relato['PONTA_A_PONTA'], relato['DE'], args.saida))
    return 0 if relato['PONTA_A_PONTA'] else 1


if __name__ == '__main__':
    sys.exit(main())
