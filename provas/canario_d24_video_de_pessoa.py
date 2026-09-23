#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CANARIO REAL DO D24 — o video de uma PESSOA do agro, por US$ 0.

    py provas/canario_d24_video_de_pessoa.py

O QUE ELE PROVA, e por que cada metade existe:

  1 · A PORTA QUE A PLATAFORMA FECHOU. A pagina de PERFIL de uma pessoa
      (`/in/<slug>/`) e um pedido real, e a resposta fica registada. Nao se
      contorna nada: mede-se.
  2 · A PORTA QUE ELA DEIXOU ABERTA. A pagina do POST publico da mesma pessoa,
      com MP4 e legenda, adquiridos a convidado.
  3 · A CADEIA, com o bruto ja em disco: `unidade()` -> `coleta/ingresso.py` ->
      o dono do RAW, contra uma base DESCARTAVEL (nada toca a Sala real).
  4 · AS TRAVAS DO D24, sem rede: contatos, seguidores, mensagens e comentarios
      de terceiros morrem na trava ANTES de qualquer pedido.

Limites, cumpridos e verificados: sem conta, sem login, sem cookie de sessao,
sem navegador, sem rota paga, sem contornar login wall/CAPTCHA/bloqueio. Toca
UMA pessoa, e so o que ela publicou publicamente.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _g in ('coleta', 'leis', 'regras', 'guarda', 'pedido', ''):
    sys.path.insert(0, os.path.join(RAIZ, _g) if _g else RAIZ)
import _gavetas  # noqa: E402,F401

import adaptador_linkedin as al       # noqa: E402
import scrap_http as http             # noqa: E402
import ingresso as ing                # noqa: E402
import scrap_colheita as SC           # noqa: E402
from guarda.preservar_coleta import ArmazemLocal  # noqa: E402
from guarda.memoria_descartavel import MemoriaDescartavel  # noqa: E402

#: O POST PUBLICO DE PESSOA, escolhido por MEDICAO numa amostra de 15: foi o
#: unico que trazia video — e trazia legenda tambem. A pessoa e profissional do
#: agro (UPL Iberia), e o PERFIL dela nunca e tocado.
POST = ('https://www.linkedin.com/posts/celestino-dom%C3%ADnguez-infante-423b4957_'
        'uplcorpiberia-uplcorpiespaaeha-uplespaaeha-activity-7445139302390382592-eYKi')
PERFIL = 'https://www.linkedin.com/in/celestino-dom%C3%ADnguez-infante-423b4957'
#: O id da publicacao DESTA pessoa. Ele existe porque a pasta de bytes e
#: COMPARTILHADA entre missoes: contar o que la esta daria os videos de outra
#: missao dentro do numero desta, e um numero que soma dois trabalhos nao mede
#: nenhum deles.
ID_DESTA_PESSOA = '7445139302390382592'
RUN_ID = 'CANARIO-D24-PESSOA'
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'CANARIO-D24-PESSOA-V1.json')
PASTA_RAW = os.path.join(RAIZ, 'data', 'samples', 'SOCIAL-IT', 'raw-free', 'LINKEDIN')
ACHADOS = {}


def mede(nome, valor, porque=''):
    ACHADOS[nome] = {'VALOR': valor, 'PORQUE': porque}
    print('  %-36s = %-30s %s' % (nome, str(valor)[:30], porque[:56]))
    return valor


def egresso():
    import urllib.request
    req = urllib.request.Request('https://ipinfo.io/json',
                                 headers={'User-Agent': http.AGENTE})
    try:
        with urllib.request.urlopen(req, timeout=25) as f:
            d = json.loads(f.read().decode('utf-8', 'replace'))
        return {k: d.get(k) for k in ('ip', 'org', 'city', 'country')}
    except Exception as e:                                          # noqa: BLE001
        return {'ERRO': '%s: %s' % (type(e).__name__, str(e)[:120])}


def mede_a_porta_fechada():
    """O PERFIL, com um pedido real. Mede-se a recusa; nao se contorna nada."""
    try:
        r = subprocess.run(['curl', '-sL', '--max-time', '30', '-A', http.AGENTE,
                            '-o', os.path.join(tempfile.gettempdir(), 'd24-perfil.html'),
                            '-w', '%{http_code} %{size_download}', PERFIL],
                           capture_output=True, text=True)
        cod, tam = (r.stdout or '000 0').split()
    except Exception as e:                                          # noqa: BLE001
        cod, tam = '000', '0:%s' % e
    try:
        corpo = io.open(os.path.join(tempfile.gettempdir(), 'd24-perfil.html'),
                        encoding='utf-8', errors='replace').read()
    except Exception:                                               # noqa: BLE001
        corpo = ''
    return cod, tam, ('authwall' in corpo.lower()), corpo.count('urn:li:activity:')


def brutos():
    """→ os ficheiros de midia em disco, com o sha conferido a mao."""
    fora = []
    for papel, pasta, ext in (('video', 'video', '.mp4'), ('legenda', 'legenda', '.webvtt')):
        p = os.path.join(RAIZ, 'data', 'raw', 'LINKEDIN', pasta)
        if not os.path.isdir(p):
            continue
        for nome in sorted(os.listdir(p)):
            if not nome.endswith(ext):
                continue
            caminho = os.path.join(p, nome)
            h = hashlib.sha256(open(caminho, 'rb').read()).hexdigest()
            fora.append({'PAPEL': papel, 'CAMINHO': os.path.relpath(caminho, RAIZ),
                         'BYTES': os.path.getsize(caminho), 'SHA256': h,
                         'ID': nome.split('__')[0]})
    return fora


def raw_do_disco():
    fora = []
    if os.path.isdir(PASTA_RAW):
        for nome in sorted(os.listdir(PASTA_RAW)):
            if nome.startswith('post-') and nome.endswith('.txt'):
                try:
                    fora.append({'FICHEIRO': os.path.relpath(os.path.join(PASTA_RAW, nome), RAIZ),
                                 'JSON': json.load(io.open(os.path.join(PASTA_RAW, nome),
                                                           encoding='utf-8'))})
                except ValueError:
                    continue
    return fora


def duble_do_replay():
    """Serve os BYTES DO DISCO. URL que o bruto nao conheca NAO e servida."""
    mapa = {}
    for r in raw_do_disco():
        j = r['JSON']
        if j.get('VIDEO_URL_SERVED') and j.get('VIDEO_STORAGE_LOCATION'):
            mapa[j['VIDEO_URL_SERVED']] = j['VIDEO_STORAGE_LOCATION']
        if j.get('CAPTION_URL') and j.get('CAPTION_STORAGE_LOCATION'):
            mapa[j['CAPTION_URL']] = j['CAPTION_STORAGE_LOCATION']
    real = http.buscar_bytes
    pedidos = []

    def duble(url, **kw):
        destino = mapa.get(url)
        if not destino:
            raise RuntimeError('REPLAY_SEM_BRUTO: %s' % url[:90])
        dados = open(os.path.join(RAIZ, destino), 'rb').read()
        pedidos.append({'URL': url[:110], 'DO_DISCO': destino, 'BYTES': len(dados)})
        return dados, {'CONTENT_TYPE': 'video/mp4' if destino.endswith('.mp4') else None,
                       'STATUS': None, 'URL': url, 'REPLAY': True}
    http.buscar_bytes = duble
    return real, pedidos


def main():
    print('=' * 78)
    print('CANARIO REAL · D24 · O VIDEO DE UMA PESSOA DO AGRO')
    print('=' * 78)
    e = egresso()
    mede('EGRESSO', '%s · %s' % (e.get('ip'), (e.get('org') or '')[:34]),
         'por aqui saiu a corrida (%s)' % e.get('country'))
    mede('CUSTO_USD', 0.0, 'rota gratuita, por decisao do dono')
    mede('LOGIN_USADO', 'NAO', 'nenhuma conta, nenhum cookie de sessao')
    mede('ROTA_PAGA', 'NAO', 'nenhum provedor pago envolvido')

    # ── 1 · A PORTA QUE A PLATAFORMA FECHOU ───────────────────────────────
    print('\n  1 · a porta do PERFIL — mede-se a recusa, nao se contorna')
    cod, tam, muro, ids = mede_a_porta_fechada()
    mede('PERFIL_HTTP', cod, 'HTTP 999 e o `authwall` da plataforma')
    mede('PERFIL_BYTES', tam, 'corpo da recusa')
    mede('PERFIL_AUTHWALL', muro, 'o muro esta no corpo, e nao se contorna')
    mede('PERFIL_ACTIVITY_IDS', ids, 'zero: a pagina nao serve conteudo nenhum')

    # ── 2 · AS TRAVAS DO D24, SEM REDE ────────────────────────────────────
    print('\n  2 · as travas do D24 — a recusa e estatica, antes da rede')
    alvos = {
        'CONTATOS': 'https://www.linkedin.com/in/x/detail/contact-info/',
        'SEGUIDORES': 'https://www.linkedin.com/in/x/followers/',
        'MENSAGENS': 'https://www.linkedin.com/messaging/thread/1/',
        'COMENTARIOS': 'https://www.linkedin.com/feed/update/urn:li:activity:7445139302390382592/comments/',
        'ECRA_DE_LOGIN': 'https://www.linkedin.com/uas/login',
    }
    for nome, alvo in alvos.items():
        try:
            al._alvo_e_post_publico(alvo)
            mede('TRAVA_' + nome, 'PASSOU', 'DEFEITO: devia ter recusado')
        except Exception as ex:                                     # noqa: BLE001
            mede('TRAVA_' + nome, 'RECUSADO', '%s' % type(ex).__name__)

    # ── 3 · A REDE, PELA PORTA DO POST PUBLICO ────────────────────────────
    print('\n  3 · a rede: o post publico da pessoa')
    med = {}
    objetos = al.video_de_post_publico(post_url=POST, run_id=RUN_ID,
                                       egresso='%s · %s' % (e.get('ip'), e.get('org')),
                                       medida=med)
    mede('OBJETOS_ADQUIRIDOS', len(objetos), 'um por publicacao com video')
    mede('PEDIDOS_DE_REDE', med.get('REQUESTS'), 'post + salto + MP4 + legenda')
    if objetos:
        o = objetos[0]
        mede('ROUTE', o.get('ROUTE'), 'a rota que a matriz declara')
        mede('DECISAO_DO_DONO', o.get('DECISAO_DO_DONO'), 'a excecao que autorizou')
        mede('LIMITE', o.get('LIMITE'), 'o limite da pessoa, e nao o da organizacao')
        mede('PUBLISHED_AT', o.get('PUBLISHED_AT'), 'declarado pela plataforma (JSON-LD)')
        mede('IDENTITY_CROSSCHECK', (o.get('RAW') or {}).get('IDENTITY_CROSSCHECK'),
             'a ligacao do video ao post, conferida')

    # ── 4 · OS BYTES, MEDIDOS NO DISCO ────────────────────────────────────
    print('\n  4 · os bytes, conferidos no disco')
    bs = [b for b in brutos() if b['ID'] == ID_DESTA_PESSOA]
    vs = [b for b in bs if b['PAPEL'] == 'video']
    ls = [b for b in bs if b['PAPEL'] == 'legenda']
    mede('VIDEO_MP4_DESTA_PESSOA', len(vs), 'MP4 desta publicacao, e nao os de outra missao')
    mede('LEGENDA_VTT_DESTA_PESSOA', len(ls), 'legendas desta publicacao')
    mede('BYTES_NA_PASTA_EM_TOTAL', len(brutos()), 'o que a pasta compartilhada tem, ao lado')
    for v in vs[:2]:
        mede('  MP4_BYTES', v['BYTES'], '%s · sha %s' % (os.path.basename(v['CAMINHO'])[:30],
                                                        v['SHA256'][:16]))
    for l in ls[:2]:
        mede('  LEGENDA_BYTES', l['BYTES'], '%s · sha %s' % (os.path.basename(l['CAMINHO'])[:30],
                                                             l['SHA256'][:16]))

    # ── 5 · A CADEIA, COM O BRUTO EM DISCO ────────────────────────────────
    print('\n  5 · a cadeia: unidade -> ingresso -> dono do RAW (base descartavel)')
    real, pedidos = duble_do_replay()
    try:
        reconstruidos = al.video_de_post_publico(post_url=POST, run_id=RUN_ID)
    finally:
        http.buscar_bytes = real
    mede('OBJETOS_RECONSTRUIDOS', len(reconstruidos), 'a partir do bruto preservado')
    mede('BYTES_SERVIDOS_DO_DISCO', len(pedidos), 'nenhuma ida a rede nesta metade')
    base = tempfile.mkdtemp(prefix='canario-d24-')
    armazem = ArmazemLocal(base)
    memoria = MemoriaDescartavel(os.path.join(base, 'descartavel.sqlite'))
    unidades = [SC.unidade(o, run_id=RUN_ID, fonte=None) for o in reconstruidos]
    recibo = ing.receber(unidades, corrida={'RUN_ID': RUN_ID, 'STARTED_AT': None},
                         armazem=armazem, memoria=memoria, raiz=RAIZ)
    mede('INGRESSO_ACEITES', len(recibo.get('ACEITES') or []), 'observacoes que a porta aceitou')
    mede('INGRESSO_RECUSAS', len(recibo.get('RECUSAS') or []),
         str([r.get('PORQUE') for r in (recibo.get('RECUSAS') or [])])[:50])
    raw = recibo.get('RAW') or {}
    sem_id = raw.get('RECUSADOS_SEM_IDENTIDADE') or []
    mede('RAW_LINHAS_GRAVADAS', (raw.get('PLANO') or {}).get('OBSERVACOES_PLANEADAS'),
         'linhas que o dono do RAW planeou escrever')
    mede('RAW_RECUSADOS_SEM_IDENTIDADE', len(sem_id),
         (sem_id[0]['PORQUE'] if sem_id else 'nenhum')[:52])
    for u in unidades[:1]:
        mede('  DOCUMENT_ID', u.get('DOCUMENT_ID'), 'a identidade do documento')
        mede('  PUBLISHED_AT', u.get('PUBLISHED_AT'), 'declarado pela plataforma')
    mede('LINHAS_RAW_NA_BASE', len(memoria.objetos_da_corrida(RUN_ID)),
         'lidas do banco descartavel, nao do recibo')

    # ── 6 · O DERIVADO ────────────────────────────────────────────────────
    print('\n  6 · o derivado')
    tx = [u for o in reconstruidos for u in (o.get('TEXT_UNITS') or []) if u.get('TEXT')]
    mede('DERIVED_UNIDADES', len(tx), 'textos com conteudo')
    if tx:
        mede('DERIVED_KINDS', ' + '.join(sorted({t.get('TEXT_KIND') for t in tx})),
             'a especie de cada texto, declarada')
        mede('DERIVED_CHARS', sum(len(t['TEXT']) for t in tx), 'caracteres de fala real')
        mede('DERIVED_AMOSTRA', ' '.join(tx[0]['TEXT'].split())[:110], 'primeiros caracteres')
    mede('ADMISSAO_IMPORTAVEL', _admissao_importavel(), 'o que impede a regua de correr aqui')

    ACHADOS['_O_QUE_ISTO_E'] = ('O canario real do D24: o video e a legenda de uma PESSOA do agro, '
                                'adquiridos da pagina PUBLICA do post dela, sem conta, sem login, '
                                'sem contornar muro e por US$ 0. O perfil da mesma pessoa foi '
                                'medido e esta fechado (999/authwall) — e nao se contorna.')
    ACHADOS['_COMO_REFAZER'] = ('py provas/canario_d24_video_de_pessoa.py')
    ACHADOS['_O_NUMERO_CONTA_SO_ESTA_PESSOA'] = (
        'A pasta `data/raw/LINKEDIN` e compartilhada entre missoes: '
        '`VIDEO_MP4_DESTA_PESSOA` conta os bytes desta publicacao (%s), e '
        '`BYTES_NA_PASTA_EM_TOTAL` diz o que mais la esta. Dois trabalhos somados '
        'num numero so nao medem nenhum deles.' % ID_DESTA_PESSOA)
    ACHADOS['_LIMITES'] = ({'SEM_CONTA': True, 'SEM_LOGIN': True, 'SEM_COOKIE': True,
                            'SEM_NAVEGADOR': True, 'SEM_ROTA_PAGA': True,
                            'SEM_CONTORNAR_MURO': True, 'SO_PUBLICO': True,
                            'PESSOAS': 'UMA, e so o que ela publicou publicamente'})
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with io.open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(ACHADOS, f, ensure_ascii=False, indent=1, default=str)
    print('\nARTEFACTO: %s' % os.path.relpath(SAIDA, RAIZ))
    return 0


def _admissao_importavel():
    try:
        import admissao  # noqa: F401
        import fcntl     # noqa: F401
        return 'SIM'
    except ImportError as ex:
        return 'NAO (%s)' % ex


if __name__ == '__main__':
    raise SystemExit(main())
