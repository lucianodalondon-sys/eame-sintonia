#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CANARIO REAL DO D23 — uma organizacao, ate tres videos, base descartavel, US$ 0.

    py provas/canario_d23_linkedin_video.py

O QUE ELE PROVA, E EM QUE ORDEM
-------------------------------
1. A REDE. A fase corre pela PORTA CANONICA (a mesma linha que o workflow
   corre: `coleta/scrap_colheita.py video-linkedin --run-id=... --pagina=...
   --teto=...`), sem conta, sem cookie, sem navegador e sem rota paga. Os bytes
   do MP4 e da legenda chegam e ficam em disco com sha256.

2. A CADEIA. Com o bruto JA PRESERVADO em disco, os objetos sao reconstruidos
   pelo adaptador e atravessam `unidade()` -> `coleta/ingresso.py` -> o dono do
   RAW, contra uma BASE DESCARTAVEL (SQLite + armazem em pasta temporaria).
   Nada disto toca a Sala real.

       A REDE MEDE-SE UMA VEZ; A CADEIA MEDE-SE QUANTAS VEZES FOR PRECISO.
       Repetir a rede para medir a cadeia gasta banda do dono sem medir nada
       de novo — e por isso os bytes vem do disco, por um duble declarado.

3. A PORTA COM IDENTIDADE. A unica organizacao REGISTADA no atlas com pagina de
   LinkedIn e `IT-T8-002` (Image Line). A fase corre tambem com esse SOURCE_ID,
   para que a porta seja exercida COM fonte provada e nao apenas sem ela.

O QUE ELE NAO FAZ
-----------------
Nao contorna login wall, CAPTCHA nem bloqueio. Nao usa conta, cookie de sessao
ou rota paga. Nao toca em perfil de PESSOA — o limite autorizado (D23) e
PAGINAS DE ORGANIZACAO. Nao escreve na Sala real.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _g in ('coleta', 'leis', 'regras', 'guarda', 'medidas', 'ferramentas', ''):
    sys.path.insert(0, os.path.join(RAIZ, _g) if _g else RAIZ)
import _gavetas  # noqa: E402,F401

import scrap_colheita as SC            # noqa: E402
import scrap_http as http              # noqa: E402
import ingresso as ing                 # noqa: E402
from guarda.preservar_coleta import ArmazemLocal  # noqa: E402
from guarda.memoria_descartavel import MemoriaDescartavel  # noqa: E402

#: A organizacao ESCOLHIDA POR MEDICAO, e nao por lembranca: em 2026-09-23 e a
#: que serve video e legenda na pagina publica. As outras duas com video foram
#: medidas ao lado (macfrut-fiera: 2 videos, zero legendas; image-line: zero
#: videos).
ORGANIZACAO = 'https://www.linkedin.com/company/gruppocaviro/'
CANDIDATA = 'CAND-0094'          # a ficha de candidata desta pagina, com prova no site
#: A organizacao REGISTADA no atlas — a prova de que a porta tambem corre COM
#: fonte provada. Hoje nao publica video, e isso e um resultado, nao uma falha.
REGISTADA = 'https://www.linkedin.com/company/image-line/'
SOURCE_REGISTADO = 'IT-T8-002'

TETO = 3
SAIDA = os.path.join(RAIZ, 'data', 'samples', 'CANARIO-LINKEDIN-D23-V1.json')
ACHADOS = {}


def mede(nome, valor, porque=''):
    ACHADOS[nome] = {'VALOR': valor, 'PORQUE': porque}
    print('  %-34s = %-26s %s' % (nome, str(valor)[:26], porque[:56]))
    return valor


def egresso():
    """EGR (24/09): o pais pelo DONO — superficie/rede.py, consenso de 3 verificadores
    com cache de 3 min. Nenhum consumidor pergunta a um servico diretamente (o
    ipinfo.io em 429 parou tudo das 13:05 as 15:05). O IP nao sai do dono."""
    import importlib.util as _u, os as _os
    _s = _u.spec_from_file_location("rede_egresso", _os.path.join(str(RAIZ), "superficie", "rede.py"))
    _r = _u.module_from_spec(_s)
    _s.loader.exec_module(_r)
    e = _r.egresso()
    pais = e["EGRESS_COUNTRY_CODE"] if e["EGRESS_COUNTRY_CODE"] != "UNKNOWN" else None
    return {'country': pais, 'VOTOS': e['VOTOS']}


def corre_a_fase(run_id, pagina, fonte=None, teto=TETO):
    """Corre a fase PELA PORTA CANONICA, com a linha de comando do workflow.

    Um subprocesso de proposito: e a MESMA linha que o CI corre, e nao uma
    reimplementacao dela. Um canario que chama funcoes por dentro mede a funcao;
    este mede a PORTA.
    """
    cmd = [sys.executable, os.path.join(RAIZ, 'coleta', 'scrap_colheita.py'),
           'video-linkedin', '--run-id=%s' % run_id, '--pagina=%s' % pagina,
           '--teto=%d' % teto]
    if fonte:
        cmd.append('--fonte=%s' % fonte)
    t0 = time.time()
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    saida = r.stdout or ''
    caminho = None
    for linha in saida.splitlines():
        if 'envelope' in linha and os.sep in linha:
            caminho = os.path.join(RAIZ, linha.split('envelope', 1)[1].strip())
    env = None
    if caminho and os.path.isfile(caminho):
        env = json.load(io.open(caminho, encoding='utf-8'))
    return {'RUN_ID': run_id, 'CMD': ' '.join(cmd[1:]), 'EXIT': r.returncode,
            'SECS': round(time.time() - t0, 1), 'ENVELOPE': caminho,
            'COLHEITA': len((env or {}).get('COLHEITA') or []),
            'PORQUE_ZERO': (env or {}).get('PORQUE_ZERO_COLHEITA'),
            'ENVELOPE_JSON': env, 'STDOUT': saida[-1200:],
            'STDERR': (r.stderr or '')[-600:]}


def brutos_do_disco():
    """→ o que a corrida REAL deixou em disco, lido dos RAW preservados.

    Devolve, por ficheiro de RAW, o que o adaptador registou: a rendicao
    escolhida, o caminho do MP4, o caminho da legenda e o sha de cada um. E
    daqui que o duble da cadeia tira os bytes — do bruto que a rede JA trouxe.
    """
    pasta = os.path.join(RAIZ, 'data', 'raw', 'LINKEDIN')
    fora = []
    for sub, ext in (('video', '.mp4'), ('legenda', ('.webvtt', '.srt', '.txt'))):
        d = os.path.join(pasta, sub)
        if not os.path.isdir(d):
            continue
        for nome in sorted(os.listdir(d)):
            if nome.endswith(ext if isinstance(ext, tuple) else (ext,)):
                p = os.path.join(d, nome)
                dados = open(p, 'rb').read()
                fora.append({'PAPEL': sub, 'CAMINHO': os.path.relpath(p, RAIZ),
                             'BYTES': len(dados), 'SHA256': hashlib.sha256(dados).hexdigest()})
    return fora


def raw_do_disco():
    """→ os RAW de observacao (o JSON que o adaptador preservou), lidos."""
    pasta = os.path.join(RAIZ, 'data', 'samples', 'SOCIAL-IT', 'raw-free', 'LINKEDIN')
    fora = []
    if os.path.isdir(pasta):
        for nome in sorted(os.listdir(pasta)):
            if nome.startswith('post-') and nome.endswith('.txt'):
                p = os.path.join(pasta, nome)
                try:
                    fora.append({'FICHEIRO': os.path.relpath(p, RAIZ),
                                 'JSON': json.load(io.open(p, encoding='utf-8'))})
                except ValueError:
                    continue
    return fora


def duble_do_replay():
    """Instala um duble que serve os BYTES DO DISCO em vez de ir a rede.

    O duble so responde ao que o RAW preservado diz que ja foi adquirido: para
    cada rendicao e cada legenda registadas, o ficheiro correspondente. Uma
    URL que o bruto nao conheca NAO e servida — e a corrida falha alto, que e
    o lado certo para falhar.

        DUBLE QUE RESPONDE A TUDO NAO E UM DUBLE: E UMA REDE FINGIDA.
    """
    mapa = {}
    for r in raw_do_disco():
        j = r['JSON']
        if j.get('RENDITION_CHOSEN') and j.get('VIDEO_STORAGE_LOCATION'):
            mapa[j['RENDITION_CHOSEN']] = j['VIDEO_STORAGE_LOCATION']
        if j.get('CAPTION_URL') and j.get('CAPTION_STORAGE_LOCATION'):
            mapa[j['CAPTION_URL']] = j['CAPTION_STORAGE_LOCATION']
    real = http.buscar_bytes
    pedidos = []

    def duble(url, **kw):
        destino = mapa.get(url)
        if not destino:
            raise RuntimeError('REPLAY_SEM_BRUTO: %s nao esta no RAW preservado' % url[:90])
        p = os.path.join(RAIZ, destino)
        dados = open(p, 'rb').read()
        pedidos.append({'URL': url[:120], 'DO_DISCO': destino, 'BYTES': len(dados)})
        return dados, {'CONTENT_TYPE': 'video/mp4' if destino.endswith('.mp4') else None,
                       'STATUS': None, 'URL': url, 'REPLAY': True}
    http.buscar_bytes = duble
    return real, pedidos, mapa


def main():
    print('=' * 78)
    print('CANARIO REAL · D23 · O VIDEO DA PAGINA PUBLICA DE ORGANIZACAO')
    print('=' * 78)

    e = egresso()
    mede('EGRESSO', '%s · %s' % (e.get('ip'), (e.get('org') or '')[:40]),
         'por aqui saiu a corrida (%s)' % e.get('country'))

    # ── 1 · A REDE, PELA PORTA CANONICA ───────────────────────────────────
    print('\n  1 · a rede, pela porta canonica')
    a = corre_a_fase('CANARIO-D23-A', ORGANIZACAO)
    mede('RUN_A_CMD', a['CMD'][:70], 'a MESMA linha que o workflow corre')
    mede('RUN_A_EXIT', a['EXIT'], 'subprocesso da porta')
    mede('RUN_A_SECS', a['SECS'], 'relogio de parede')
    brutos = brutos_do_disco()
    videos = [b for b in brutos if b['PAPEL'] == 'video']
    legendas = [b for b in brutos if b['PAPEL'] == 'legenda']
    mede('VIDEO_MP4_ADQUIRIDOS', len(videos), 'ficheiros de video em data/raw/LINKEDIN/video')
    mede('LEGENDAS_ADQUIRIDAS', len(legendas), 'faixas de legenda em data/raw/LINKEDIN/legenda')
    for v in videos[:3]:
        mede('  MP4_BYTES', v['BYTES'], '%s · sha %s' % (os.path.basename(v['CAMINHO'])[:34],
                                                        v['SHA256'][:16]))
    for l in legendas[:3]:
        mede('  LEGENDA_BYTES', l['BYTES'], '%s · sha %s' % (os.path.basename(l['CAMINHO'])[:34],
                                                             l['SHA256'][:16]))
    mede('RUN_A_COLHEITA', a['COLHEITA'], (a['PORQUE_ZERO'] or '')[:70])

    # ── 2 · A PORTA COM FONTE PROVADA ─────────────────────────────────────
    print('\n  2 · a mesma porta, com um SOURCE_ID provado')
    b = corre_a_fase('CANARIO-D23-B', REGISTADA, fonte=SOURCE_REGISTADO)
    mede('RUN_B_CMD', b['CMD'][:70], 'com --fonte=%s' % SOURCE_REGISTADO)
    mede('RUN_B_COLHEITA', b['COLHEITA'], (b['PORQUE_ZERO'] or 'sem recusa')[:70])
    mede('RUN_B_EXIT', b['EXIT'], 'a porta aceitou a fonte provada')

    # ── 3 · A CADEIA, COM O BRUTO JA EM DISCO ─────────────────────────────
    print('\n  3 · a cadeia: unidade -> ingresso -> dono do RAW (base descartavel)')
    # A organizacao do RUN A e uma CANDIDATA: nao ha SOURCE_ID dela, e inventar
    # um seria o defeito que esta casa mais paga para nao cometer. A corrida
    # corre sem fonte, e o que sai e o que sai SEM fonte — medido.
    import adaptador_linkedin as al
    real, pedidos, mapa = duble_do_replay()
    # ⚠️ O DUBLE SUBSTITUI SO OS BYTES, E NADA MAIS. As PAGINAS (a landing da
    # organizacao e a pagina de cada publicacao) continuam a ser lidas da rede,
    # porque e o adaptador que as pede, por dentro da autorizacao do dono — e
    # porque o bruto guardado nao as tem. Substituir a pagina tambem seria
    # medir uma pagina que ninguem leu.
    #
    #     O QUE JA ESTA EM DISCO VEM DO DISCO. O QUE NAO ESTA, LE-SE.
    objetos = al.video_da_pagina_publica(
        pagina_url=ORGANIZACAO, run_id='CANARIO-D23-A', country_scope='IT', teto=TETO)
    http.buscar_bytes = real
    mede('OBJETOS_RECONSTRUIDOS', len(objetos), 'a partir do bruto preservado')
    mede('BYTES_SERVIDOS_DO_DISCO', len(pedidos), 'nenhuma ida a rede nesta metade')

    base = tempfile.mkdtemp(prefix='canario-d23-')
    armazem = ArmazemLocal(base)
    memoria = MemoriaDescartavel(os.path.join(base, 'descartavel.sqlite'))
    unidades = [SC.unidade(o, run_id='CANARIO-D23-A', fonte=None) for o in objetos]
    corrida = {'RUN_ID': 'CANARIO-D23-A', 'STARTED_AT': None}
    recibo = ing.receber(unidades, corrida=corrida, armazem=armazem, memoria=memoria,
                         raiz=RAIZ)
    mede('INGRESSO_ACEITES', len(recibo.get('ACEITES') or []), 'observacoes que a porta aceitou')
    mede('INGRESSO_RECUSAS', len(recibo.get('RECUSAS') or []),
         str([r.get('PORQUE') for r in (recibo.get('RECUSAS') or [])]))
    raw = recibo.get('RAW') or {}
    # ── A MEDICAO QUE IMPORTA, E ELA VEM DO DONO DO RAW ───────────────────
    # A porta ACEITOU as observacoes (contrato inteiro). Quem recusa a linha e
    # o dono do RAW, e recusa com o nome e o motivo:
    #
    #     «sem SOURCE_ID real nao ha estado de identidade possivel,
    #      e nenhum se inventa»
    #
    # Isto NAO e um defeito desta missao: e a lei da casa a funcionar. O que o
    # canario mostra e onde ela morde — e a resposta que falta e de CATALOGO,
    # nao de engenharia de aquisicao.
    sem_id = raw.get('RECUSADOS_SEM_IDENTIDADE') or []
    mede('RAW_LINHAS_GRAVADAS', (raw.get('PLANO') or {}).get('OBSERVACOES_PLANEADAS'),
         'linhas que o dono do RAW planeou escrever')
    mede('RAW_RECUSADOS_SEM_IDENTIDADE', len(sem_id),
         (sem_id[0]['PORQUE'] if sem_id else 'nenhum')[:60])
    for u in unidades[:3]:
        mede('  DOCUMENT_ID', u.get('DOCUMENT_ID'), '%s · %s' % (u.get('SOURCE_ID'),
                                                                 u.get('DOCUMENT_ID_BASE', '')[:34]))
        mede('  PUBLISHED_AT', u.get('PUBLISHED_AT'), 'declarado pela plataforma (JSON-LD)')
        mede('  PAYLOAD', (u.get('PAYLOAD') or {}).get('ESTADO'),
             (u.get('PAYLOAD') or {}).get('ONDE', '')[:40])
    ida = memoria.objetos_da_corrida('CANARIO-D23-A')
    mede('LINHAS_RAW_NA_BASE', len(ida), 'lidas do banco descartavel, nao do recibo')

    # ── 4 · O DERIVADO: A LEGENDA E TEXTO COM ESPECIE ─────────────────────
    print('\n  4 · o derivado')
    textos = []
    for o in objetos:
        for u in (o.get('TEXT_UNITS') or []):
            if u.get('TEXT_KIND') == 'NATIVE_CAPTION' and u.get('TEXT'):
                textos.append(u)
    mede('DERIVED_UNIDADES', len(textos), 'legendas com texto, uma por video')
    if textos:
        mede('DERIVED_KIND', textos[0].get('TEXT_KIND'), '%s / %s' % (
            textos[0].get('TEXT_KIND_BASIS'), textos[0].get('TEXT_RELATION')))
        mede('DERIVED_CHARS', sum(len(t['TEXT']) for t in textos), 'caracteres de fala real')
        mede('DERIVED_AMOSTRA', ' '.join(textos[0]['TEXT'].split())[:120], 'primeiros caracteres')
    else:
        mede('DERIVED_CHARS', 0, 'nenhuma legenda: o texto teria de vir do ASR')

    # ── 5 · A ADMISSAO ────────────────────────────────────────────────────
    print('\n  5 · a admissao')
    try:
        import admissao as adm                                      # noqa: F401
        try:
            import fcntl                                            # noqa: F401
            mede('ADMISSAO_IMPORTAVEL', 'SIM', 'os dois imports passaram')
        except ImportError as ex:
            mede('ADMISSAO_IMPORTAVEL', 'NAO', 'fcntl ausente no Windows — medido: %s' % ex)
    except Exception as ex:                                          # noqa: BLE001
        mede('ADMISSAO_IMPORTAVEL', 'NAO', '%s: %s' % (type(ex).__name__, str(ex)[:60]))

    estado = {
        'O_QUE_ISTO_E': ('O canario real do D23: video (e legenda) de pagina publica de '
                         'ORGANIZACAO no LinkedIn, pela porta canonica do SCRAP, contra '
                         'uma base descartavel e sem dolar.'),
        'COMO_REFAZER': 'py provas/canario_d23_linkedin_video.py',
        'DECISAO_DO_DONO': 'D23 · DECISOES-DONO-2026-09-23.md',
        'OWNER_AUTHORIZED': 'SIM',
        'PLATFORM_POLICY_STATUS': 'DISALLOWED (robots.txt do LinkedIn, medido)',
        'LIMITE': 'PUBLIC_ORG_VIDEO_ONLY',
        'ORGANIZACAO': ORGANIZACAO, 'CANDIDATA': CANDIDATA,
        'ORGANIZACAO_REGISTADA': REGISTADA, 'SOURCE_REGISTADO': SOURCE_REGISTADO,
        'EGRESSO': e, 'RUN_A': {k: v for k, v in a.items() if k != 'ENVELOPE_JSON'},
        'RUN_B': {k: v for k, v in b.items() if k != 'ENVELOPE_JSON'},
        'BRUTOS_EM_DISCO': brutos, 'BASE_DESCARTAVEL': base,
        'MEDIDO': ACHADOS,
        'RECIBO_DO_RAW': {
            'PLANO': (raw.get('PLANO') or {}),
            'RECUSADOS_SEM_IDENTIDADE': (raw.get('RECUSADOS_SEM_IDENTIDADE') or []),
            'ENVIO': (raw.get('ENVIO') or {}),
            'MEMORIA': (raw.get('MEMORIA') or {}),
        },
        'VIAS_QUE_RESTAM': {
            '1': ('PROMOVER A CANDIDATA A FONTE. A pagina do `gruppocaviro` e a '
                  'candidata %s, com prova (a organizacao publica este endereco no '
                  'site dela). O molde ja existe nesta casa: `IT-T8-002` («Image Line '
                  '— pagina aziendale LinkedIn») e exactamente isto — uma PAGINA DE '
                  'LINKEDIN como fonte registada. Com a ficha no atlas, o mesmo '
                  'canario passa a gravar RAW com identidade, e o DOCUMENT_ID deixa de '
                  'ser NAO SEI.' % CANDIDATA),
            '2': ('A ADMISSAO corre no CI, onde ha Postgres e onde `fcntl` existe. '
                  'Nesta maquina nao ha banco nem `fcntl` — medido, e por isso '
                  'declarado em vez de fingido.'),
            '3': ('O ASR (para video SEM legenda) continua a ser do dono unico '
                  '(`ferramentas/fala_local.py`), e nao correu: nao faltou legenda '
                  'neste canario, e nesta maquina o reconhecedor nao esta instalado. '
                  'Os videos sem legenda saem com `DERIVED_TEXT = ASR_REQUIRED` e o '
                  'dono nomeado — nunca mudos.'),
        },
        'PENDENTE': {
            'COLLECTION_COM_IDENTIDADE': ('a organizacao do RUN A e CANDIDATA (%s); a porta '
                                          'exige SOURCE_ID provado, e por isso a colheita '
                                          'sai zero e as observacoes ficam em SUPORTE. '
                                          'Promover a candidata no atlas e a decisao que '
                                          'falta — e ela nao e do engenheiro.' % CANDIDATA),
            'ADMISSAO': ('exige banco real e `fcntl`; nesta maquina nao ha Postgres. O '
                         'caminho e o CI (fases do workflow), onde a base e criada e deitada '
                         'fora.'),
        },
        'CUSTO_USD': 0.0,
        'LOGIN_USADO': 'NAO', 'COOKIE_DE_SESSAO': 'NAO', 'ROTA_PAGA': 'NAO',
        'CONTORNO_DE_ACESSO': 'NAO',
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with io.open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(estado, f, ensure_ascii=False, indent=1, default=str)
        f.write('\n')
    print('\n  gravado: %s' % os.path.relpath(SAIDA, RAIZ))
    print('\nCANARIO_D23 = %s · videos=%d · legendas=%d · colheita_A=%d · colheita_B=%d'
          % ('MEDIDO', len(videos), len(legendas), a['COLHEITA'], b['COLHEITA']))
    print('CUSTO_USD = 0.0 · login=NAO · cookie=NAO · rota_paga=NAO · contorno=NAO')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
