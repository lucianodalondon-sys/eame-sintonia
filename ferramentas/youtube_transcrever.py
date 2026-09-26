#!/usr/bin/env python3
"""
WHISPER DO YOUTUBE — a fala que a legenda não deu, e SÓ ela.

    py ferramentas/youtube_transcrever.py alvos           # GRÁTIS: o que a fila manda
    py ferramentas/youtube_transcrever.py rodar           # transcreve o que a fila manda
    py ferramentas/youtube_transcrever.py rodar small 20  # modelo e teto de itens

ESTE ARQUIVO NÃO ESCOLHE NADA
-------------------------------
Ele obedece `YOUTUBE-RELEVANCIA/FILA-WHISPER.json`, e a fila obedece o portão de
relevância. Se a fila estiver vazia, este arquivo não roda — e isso é o desenho,
não uma falha.

    QUEM DECIDE GASTAR HORA DE MÁQUINA É O PORTÃO, DE GRAÇA, ANTES.

POR QUE A ORDEM É LEGENDA PRIMEIRO
------------------------------------
`youtube_janela.py legendas` já leu a legenda pública de graça, com tempos. Um vídeo
legendado NUNCA chega aqui: a fila o marcou `JA_TEM_LEGENDA` e o tirou do caminho.

    TRANSCREVER O QUE JÁ VEIO ESCRITO É PAGAR HORA DE MÁQUINA POR NADA.

Foi por isso que a camada de legenda existe: no Instagram não havia essa saída, e
lá o whisper era o único caminho. Aqui ele é o último.

OS PARÂMETROS SÃO OS MEDIDOS, E NÃO SÃO MEUS
----------------------------------------------
Vêm de `instagram_transcrever.py`, cronometrados nesta máquina em 2026-09-02:

    small     3,2x    "Pilar Pascual", "ingeniero agrícola"    — o padrão
    base      9,4x    "Pilar Pasqual"                          — média
    tiny     18,7x    "Pirar Pascal", "agro-imfluencia"        — inutilizável

E as duas descobertas que custaram medição: declarar `cpu_threads` nos 16 núcleos
deu ~4x (sem isso, 0,3x — 63 horas para mil vídeos), e `beam_size=5` custa o dobro
para entregar o mesmo texto.

O ÁUDIO VEM DO `yt-dlp`, E ISSO É UMA DEPENDÊNCIA NOVA
--------------------------------------------------------
O Instagram entregava um MP4 assinado que morria em horas. O YouTube não entrega URL
de mídia direta: a faixa de áudio é negociada pelo player. `yt-dlp` faz essa
negociação, e mora FORA do repositório, junto do `faster-whisper`.

    py -m pip install --target ~/.sintonia-libs yt-dlp faster-whisper

NUNCA instalar sem `--target`: no Windows o `pip` cria `Scripts/`, que é a MESMA
pasta que `scripts/` — a memória desta casa registra o acidente.
"""
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
# O DONO DO RECONHECEDOR. Importado AQUI, ao nivel do modulo, porque a
# politica de modelo se le antes de qualquer funcao correr. `fala_local`
# so importa `os`, `re` e `time` no topo — a biblioteca pesada continua a
# entrar tarde, dentro das funcoes dele.
import fala_local as fl  # noqa: E402

LIBS = os.environ.get('SINTONIA_LIBS') or os.path.join(
    os.path.expanduser('~'), '.sintonia-libs')
if os.path.isdir(LIBS):
    sys.path.insert(0, LIBS)

SAMPLES = os.path.join(ROOT, 'data', 'samples')
FILA = os.path.join(SAMPLES, 'YOUTUBE-RELEVANCIA', 'FILA-WHISPER.json')
SAIDA = os.path.join(SAMPLES, 'YOUTUBE-TRANSCRICOES')
MEDIA = os.path.join(SAIDA, 'audio-cache')

MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'
NAO_SEI = 'NOT_KNOWN'

# A politica vive no dono; `YT_MODELO` continua a valer. Ver
# `fala_local.MODELOS_POR_CHAMADOR`.
MODELO_PADRAO = fl.modelo_de('youtube')
BEAM = int(os.environ.get('YT_BEAM') or 1)
LOTE = int(os.environ.get('YT_LOTE') or 8)

# País da conta → idioma. Declarar o idioma evita o detector errar em áudio curto,
# e `IDIOMA != LUGAR` continua valendo: isto escolhe o decodificador, não o fato.
IDIOMA_DO_PAIS = {'ES': 'es', 'IT': 'it', 'FR': 'fr', 'PT': 'pt', 'BR': 'pt'}

# Teto de tempo por item. Áudio repetitivo pode fazer o decodificador entrar em laço:
# ele não erra, ele NÃO TERMINA. Seis vezes a duração é folga larga e corta o laço.
TETO_FATOR = 6
TETO_MINIMO_S = 120


def agora():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def hoje():
    import datetime
    return datetime.date.today().isoformat()


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/YOUTUBE-TRANSCRICOES/' + nome


def _ler_saida(nome):
    p = os.path.join(SAIDA, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def fila():
    """→ (itens_da_fila, cabecalho). A fila manda; este arquivo obedece."""
    if not os.path.exists(FILA):
        print('sem FILA-WHISPER.json — rode `py coleta/youtube_relevancia.py tudo`')
        return [], None
    with open(FILA, encoding='utf-8') as f:
        d = json.load(f)
    return d.get('QUEUE') or [], d


def fase_alvos():
    itens, cab = fila()
    if cab is None:
        return 1
    print('universo lido pelo portão .......... %s' % cab.get('UNIVERSO'))
    print('recusados .......................... %s' % cab.get('RECUSADOS'))
    for m, c in (cab.get('MOTIVOS_DE_RECUSA') or {}).items():
        print('    %-32s %s' % (m, c))
    print('na fila ............................ %d' % len(itens))
    print('fora do orçamento .................. %s' % cab.get('FORA_DO_ORCAMENTO'))
    print('custo de máquina da fila ........... %s h (orçamento %s h)'
          % (cab.get('CUSTO_DE_MAQUINA_DA_FILA_H'), cab.get('ORCAMENTO_H')))
    print('qual critério realmente filtra ..... %s' % cab.get('QUAL_CRITERIO_REALMENTE_FILTRA'))
    print()
    for i in itens[:25]:
        print('  %-13s %5s s  %-24s %s' % (i['VIDEO_ID'], i.get('DURATION_S'),
                                           str(i.get('ACCOUNT_HANDLE'))[:24],
                                           str(i.get('TITLE'))[:40]))
    return 0


def _audio(video_id):
    """→ (caminho_wav, motivo). O `yt-dlp` negocia a faixa; o `ffmpeg` corta o resto.

    ⚠️ `--write-info-json` ENTROU EM 2026-09-24, E NAO E DECORACAO.

    Os METADADOS publicos do video (data de publicacao, canal, id do canal) sao
    devolvidos pelo MESMO `yt-dlp` que ja corre aqui — sem chave, sem conta e sem
    uma segunda ida a rede. Eles ficam ao lado do `.wav`, em `<id>.info.json`, e
    quem os le e `metadados()`, neste ficheiro.

        UMA CORRIDA, DOIS PRODUTOS: O SOM E O QUE A PLATAFORMA DECLARA DELE.

    A SOC-ONDA2 mediu o preco de nao os guardar: 11/11 videos com audio e
    transcricao, e ZERO a chegar a READY — porque o item entrava sem
    `PUBLISHED_AT`, sem canal e sem o carimbo do dono.
    """
    os.makedirs(MEDIA, exist_ok=True)
    wav = os.path.join(MEDIA, video_id + '.wav')
    if os.path.exists(wav) and os.path.getsize(wav) > 1000:
        return wav, 'CACHE'
    url = 'https://www.youtube.com/watch?v=' + video_id
    global ULTIMO_TRAFEGO
    # Ate prova em contrario, os pedidos desta ida nao estao contados.
    ULTIMO_TRAFEGO = None
    # FREIO-SOCIAL (26/09): o yt-dlp corre pelo `yt_dlp_com_freio.py`, que faz
    # cada pedido dele reservar o lugar no livro da onda ANTES de sair (D38/D41).
    # As recusas do filho voltam por um ficheiro e entram nas deste processo.
    import tempfile                                                # noqa: PLC0415
    fd, recusas_do_filho = tempfile.mkstemp(prefix='teto-recusas-', suffix='.ndjson')
    os.close(fd)
    env = dict(os.environ, SINTONIA_TETO_RECUSAS=recusas_do_filho)
    try:
        # `--print-traffic` (PROVA-TETO-SOCIAL): o `yt-dlp` e outro processo e
        # os pedidos dele (pagina, player, stream em `googlevideo.com`) nao
        # passam pelo portao do Scrap. Ele proprio escreve uma linha `send:`
        # por pedido, com o Host — e e dai que a contagem sai, medida.
        r = subprocess.run(
            [sys.executable, FREIO_DO_YT_DLP, '-q', '--no-warnings',
             '--print-traffic',
             '-f', 'bestaudio/best', '-x', '--audio-format', 'wav',
             '--postprocessor-args', '-ac 1 -ar 16000',
             '--write-info-json',
             '-o', os.path.join(MEDIA, '%(id)s.%(ext)s'), url],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=600, env=env)
    except subprocess.TimeoutExpired:
        # Saida a meio nao e contagem: fica NAO contado, e diz-se.
        _recolher_recusas(recusas_do_filho)
        return None, 'YT_DLP_ESTOUROU_O_TEMPO'
    recusadas = _recolher_recusas(recusas_do_filho)
    ULTIMO_TRAFEGO = trafego_do_yt_dlp(r.stdout)
    if recusadas:
        # O freio parou o yt-dlp: o que saiu esta contado; o que nao saiu esta escrito.
        return None, ('TETO_DOMINIO: %d pedido(s) recusado(s) antes de sair (%s)'
                      % (len(recusadas), recusadas[0].get('ORCAMENTO')))
    if os.path.exists(wav) and os.path.getsize(wav) > 1000:
        return wav, 'BAIXADO'
    erro = [l for l in (r.stderr or '').strip().splitlines() if l.strip()]
    erro = erro or [l for l in (r.stdout or '').strip().splitlines()
                    if l.strip() and not _LINHA_DE_TRAFEGO.match(l)]
    return None, ('YT_DLP_NAO_ENTREGOU: %s' % (erro[-1][:150] if erro else 'sem mensagem'))


FREIO_DO_YT_DLP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yt_dlp_com_freio.py')


def _recolher_recusas(f):
    """As recusas que o yt-dlp com freio escreveu → entram no `teto_da_onda` deste processo."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'coleta'))
    import teto_da_onda as teto                                    # noqa: PLC0415
    lidas = teto.ler_recusas_do_filho(f)
    teto.acrescentar_recusas(lidas)
    try:
        os.remove(f)
    except OSError:
        pass
    return lidas


#: Os pedidos da ultima ida do `yt-dlp`: {host: pedidos}, ou None quando nao
#: foi possivel conta-los (tempo estourado, linha de pedido sem Host).
ULTIMO_TRAFEGO = None

# Uma linha `send:` do `--print-traffic` e o `repr()` dos bytes enviados. So as
# que comecam por uma linha de pedido HTTP contam: um corpo de POST sai numa
# segunda linha `send:`, e o CONNECT e o aperto de mao com um proxy, nao um
# pedido ao site.
_LINHA_DE_TRAFEGO = re.compile(r"^(send|reply|header|director):")
_PEDIDO = re.compile(r"^send: b['\"](GET|POST|HEAD|PUT|DELETE|PATCH|OPTIONS) \S+ HTTP/")
_HOST = re.compile(r"\\r\\nHost: ([^\\\s]+)\\r\\n", re.I)


def trafego_do_yt_dlp(saida):
    """→ {host: pedidos} lido da saida do `--print-traffic`, ou None se algum
    pedido nao disser o Host. Zero pedidos com saida legivel e zero de verdade
    (ex.: o `yt-dlp` recusou antes de ir a rede)."""
    por_host = {}
    for linha in (saida or '').splitlines():
        if not _PEDIDO.match(linha):
            continue
        m = _HOST.search(linha)
        if not m:
            return None
        h = m.group(1).split(':')[0].lower()
        por_host[h] = por_host.get(h, 0) + 1
    return por_host


#: O que a plataforma DECLARA, e nada mais. A lista e fechada de proposito: um
#: dicionario inteiro do yt-dlp dentro do objeto poria no acervo campos que
#: ninguem leu, e o acervo guarda o que se pode citar.
CAMPOS_PUBLICOS = ('id', 'title', 'upload_date', 'release_date', 'timestamp',
                   'uploader', 'uploader_id', 'uploader_url',
                   'channel', 'channel_id', 'channel_url',
                   'duration', 'view_count', 'availability', 'live_status',
                   'webpage_url', 'channel_follower_count')


def metadados(video_id):
    """→ (dict, motivo). O QUE A PLATAFORMA DECLARA do video, sem chave nenhuma.

    Ordem: o `.info.json` que a aquisicao deixou ao lado do som; e, se ele nao
    existir (som veio da cache), UMA chamada so de metadados — `--skip-download`,
    que nao baixa bytes de midia.

        METADADO DECLARADO != METADADO INFERIDO. A data que sai daqui e a que a
        plataforma serve; nao se corrige, nao se completa e nao se deduz.

    Sem rede que responda, ou sem `yt-dlp`, a resposta honesta e `{}` com o
    motivo escrito — nunca um dicionario inventado.
    """
    os.makedirs(MEDIA, exist_ok=True)
    cache = os.path.join(MEDIA, video_id + '.info.json')
    if os.path.exists(cache) and os.path.getsize(cache) > 2:
        try:
            with io.open(cache, encoding='utf-8') as f:
                return {k: v for k, v in json.load(f).items() if k in CAMPOS_PUBLICOS}, 'CACHE'
        except (OSError, ValueError):
            pass
    url = 'https://www.youtube.com/watch?v=' + video_id
    try:
        r = subprocess.run(
            [sys.executable, '-m', 'yt_dlp', '-q', '--no-warnings',
             '--skip-download', '--dump-json', url],
            capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {}, 'YT_DLP_ESTOUROU_O_TEMPO'
    if r.returncode != 0 or not (r.stdout or '').strip():
        erro = (r.stderr or r.stdout or '').strip().splitlines()
        return {}, ('YT_DLP_NAO_ENTREGOU: %s' % (erro[-1][:150] if erro else 'sem mensagem'))
    try:
        bruto = json.loads(r.stdout.splitlines()[0])
    except ValueError as e:
        return {}, 'YT_DLP_DEVOLVEU_JSON_ILEGIVEL: %s' % str(e)[:120]
    limpo = {k: bruto.get(k) for k in CAMPOS_PUBLICOS}
    try:
        with io.open(cache, 'w', encoding='utf-8') as f:
            json.dump(limpo, f, ensure_ascii=False)
    except OSError:
        pass
    return limpo, 'DECLARADO'


def declarado_em(md):
    """→ (ISO-8601 em UTC, precisao) a partir do que a plataforma declara.

    `timestamp` da o segundo; `upload_date` da so o DIA. Quando so ha o dia, a
    precisao vai escrita ao lado — uma data a meio-dia inventada pareceria
    exata, e a casa nao arredonda para cima uma certeza que nao tem.
    """
    import datetime
    ts = md.get('timestamp')
    if isinstance(ts, (int, float)) and ts > 0:
        return (datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
                .strftime('%Y-%m-%dT%H:%M:%SZ'), 'SECOND')
    d = str(md.get('upload_date') or '')
    if len(d) == 8 and d.isdigit():
        return ('%s-%s-%sT00:00:00Z' % (d[:4], d[4:6], d[6:8]), 'DAY')
    return ('NAO SEI', 'NAO DECLARADA')


def fase_rodar(modelo=None, teto=None):
    modelo = modelo or MODELO_PADRAO
    itens, cab = fila()
    if cab is None:
        return 1
    if not itens:
        print('FILA_VAZIA=YES · o portão não aprovou nenhum vídeo. Isto é o desenho:')
        print('  %s' % cab.get('QUAL_CRITERIO_REALMENTE_FILTRA'))
        return 0
    if teto:
        itens = itens[:int(teto)]

    # O RECONHECEDOR NÃO VIVE MAIS AQUI. O cabeçalho deste ficheiro sempre disse
    # que os parâmetros «vêm de instagram_transcrever.py» — o que é outra forma de
    # dizer que a lógica estava copiada. Agora os dois chamam o mesmo dono,
    # `ferramentas/fala_local.py`, e a medição vive num sítio só.
    ha, porque = fl.disponivel()
    if not ha:
        print(porque + '\n(e `yt-dlp` para o áudio)')
        return 1

    nucleos = fl.nucleos()
    print('modelo %s · %d núcleos · lote %d · beam %d'
          % (modelo, nucleos, fl.LOTE, fl.BEAM))
    t0 = time.time()
    # O DONO DECIDE O FERRO; ESTE PROGRAMA SO REPORTA O QUE ELE DECIDIU.
    # O `trace` volta do dono e vai INTEIRO para o carimbo do artefato. Sem
    # ele o carimbo diria `NOT_KNOWN` onde a resposta existe — e um campo que
    # confessa nao saber o que o processo ao lado sabe e um campo partido.
    _pipe, ferro = fl.modelo(modelo)
    print('carregado em %.1f s' % (time.time() - t0))

    # Retomar: transcrição é cara em TEMPO, e refazer o pronto é o mesmo desperdício
    # que pagar duas vezes por um item.
    feito = {}
    antigo = _ler_saida('TRANSCRICOES.json')
    if antigo:
        feito = {i['VIDEO_ID']: i for i in antigo.get('ITEMS', [])
                 if i.get('TRANSCRIPT_STATE') == 'OK'}
        print('já transcritos antes: %d (serão preservados)' % len(feito))

    saida, seg_audio, seg_maquina = [], 0.0, 0.0
    for n, o in enumerate(itens, 1):
        vid = o['VIDEO_ID']
        if vid in feito:
            saida.append(feito[vid])
            continue
        base = {
            'VIDEO_ID': vid,
            'VIDEO_URL': 'https://www.youtube.com/watch?v=' + vid,
            'ACCOUNT_HANDLE': o.get('ACCOUNT_HANDLE'),
            'TITLE': o.get('TITLE'),
            'DURATION_S': o.get('DURATION_S', NAO_SEI),
            'POR_QUE_ESTE_VIDEO': ('a legenda pública não existia (%s) e o portão de '
                                   'relevância o aprovou' % o.get('CAPTION_STATE')),
            'ASR_ENGINE': 'faster-whisper', 'ASR_MODEL': modelo,
            'ASR_BEAM': BEAM, 'ASR_BATCH': LOTE,
            # ⚠️ AQUI ESTAVA O MESMO DEFEITO DA C4B, NOUTRO CAMPO.
            # Esta ficha e a BASE de todos os registos deste lote, e os
            # que nunca chegam ao reconhecedor — `AUDIO_NAO_OBTIDO`,
            # `ASR_FALHOU` — levavam-na inteira. Um registo onde NADA
            # correu saia a jurar `cpu/int8/16 threads`.
            #
            #     NOT_RUN NAO PODE TER FICHA DE EXECUCAO.
            #
            # A ficha do ferro passa a nascer so quando ha resultado, e
            # vem do dono — `fala_local.carimbo`, que a preenche com o
            # estado ao lado.
            'ASR_DEVICE': fl.NAO_SEI,
            'ASR_DEVICE_EXECUTION': fl.EXECUCAO_NAO_CORREU,
            'CAPTURED_AT': agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
            'COST_USD': 0,
        }
        wav, motivo = _audio(vid)
        if not wav:
            saida.append(dict(base, **{
                'TRANSCRIPT': None, 'TRANSCRIPT_STATE': 'AUDIO_NAO_OBTIDO',
                'WHY': motivo,
                'NAO_SIGNIFICA': 'que o vídeo não tem fala. Significa que eu não ouvi.'}))
            print('  %3d/%d %-13s SEM ÁUDIO — %s' % (n, len(itens), vid, str(motivo)[:56]))
            continue
        base['AUDIO_STATE'] = motivo
        idioma = IDIOMA_DO_PAIS.get(str(o.get('COUNTRY_SCOPE') or '').upper())
        dur = o.get('DURATION_S')
        limite = max(TETO_MINIMO_S,
                     int(dur * TETO_FATOR) if isinstance(dur, (int, float)) else TETO_MINIMO_S)
        r = fl.transcrever(wav, idioma=idioma, modelo_nome=modelo,
                           duracao_s=dur if isinstance(dur, (int, float)) else None)
        if r['TRANSCRIPT_STATE'] in (fl.ASR_FALHOU, fl.ASR_INDISPONIVEL):
            # A QUEDA TAMBEM TEM FICHA, e ela vem do reconhecedor — nao da base.
            # Antes este ramo guardava `base` intacta e deitava fora o trace de
            # `r`: perdia-se qual ferro tinha sido escolhido justamente no caso
            # em que essa e a pergunta.
            #
            #     QUEM FALHA E QUEM MAIS PRECISA DE DIZER ONDE ESTAVA.
            saida.append(dict(base, **{
                'TRANSCRIPT': None, 'TRANSCRIPT_STATE': r['TRANSCRIPT_STATE'],
                'ASR_DEVICE': r.get('ASR_DEVICE', fl.NAO_SEI),
                'ASR_DEVICE_SELECTED': r.get('ASR_DEVICE_SELECTED', fl.NAO_SEI),
                'ASR_DEVICE_EXECUTION': r.get('ASR_DEVICE_EXECUTION',
                                              fl.EXECUCAO_NAO_CORREU),
                'ASR_WHY_FALLBACK': r.get('ASR_WHY_FALLBACK'),
                'WHY': r.get('ERROR', '')}))
            print('  %3d/%d %-13s ASR FALHOU' % (n, len(itens), vid))
            continue
        if r.get('TRUNCATED_BY_TIME') == 'YES':
            base['TRUNCADO_POR_TEMPO_S'] = r.get('TIMEOUT_LIMIT_S', NAO_SEI)
        gasto = r.get('MACHINE_SECONDS')
        gasto = gasto if isinstance(gasto, (int, float)) else 0.0
        seg_maquina += gasto
        if isinstance(dur, (int, float)):
            seg_audio += dur
        texto = r.get('TRANSCRIPT') or ''
        saida.append(dict(base, **{
            'TRANSCRIPT': r.get('TRANSCRIPT'),
            # Os tempos de cada trecho ficam com o nome que este ficheiro sempre
            # usou; o dono unico devolve-os em `SEGMENTS`, e a traducao e aqui.
            'TRANSCRIPT_SEGMENTS': [{'T_S': x['start'], 'FIM_S': x['end'],
                                     'TEXTO': x['text']} for x in r.get('SEGMENTS', [])],
            'TRANSCRIPT_CHARS': r.get('TRANSCRIPT_CHARS', 0),
            # ⚠️ ISTO DIZIA `'OK'` SEMPRE, mesmo com texto vazio. Um video sem
            # fala saia daqui a afirmar transcricao bem-sucedida, e a diferenca
            # entre «ouvi e nao havia» e «ouvi e transcrevi» desaparecia.
            'TRANSCRIPT_STATE': r['TRANSCRIPT_STATE'],
            'WHY': r.get('WHY', ''),
            'NAO_SIGNIFICA': r.get('NAO_SIGNIFICA', ''),
            'DISCARDED_OUTPUT': r.get('DISCARDED_OUTPUT'),
            'ASR_LANGUAGE': r.get('LANGUAGE', NAO_SEI),
            'ASR_LANGUAGE_DECLARADO': r.get('LANGUAGE_SOURCE') == 'DECLARED',
            'ASR_LANGUAGE_CONFIDENCE': r.get('LANGUAGE_CONFIDENCE', NAO_SEI),
            'SEGUNDOS_DE_MAQUINA': round(gasto, 1)}))
        print('  %3d/%d %-13s %6.1f s de máquina · %5d chars · %-18s %s'
              % (n, len(itens), vid, gasto, len(texto), r['TRANSCRIPT_STATE'],
                 str(o.get('TITLE'))[:32]))

    vel = (seg_audio / seg_maquina) if seg_maquina else 0
    p = _gravar('TRANSCRICOES.json', {
        'SOURCE_ID': 'YOUTUBE-TRANSCRICOES',
        'source': 'faster-whisper local sobre o áudio público, nesta máquina',
        'SOURCE_LOCATION': 'local — nenhuma rota paga',
        'FACT_LOCATION': 'EAME', 'ORIGINAL_LANGUAGE': 'multi',
        'EVIDENCE_CLASS': 'LOCAL_ASR',
        'captured_at': hoje(), 'CAPTURED_AT': agora(),
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'CUSTO_E_TEMPO_NAO_FATURA': ('zero dólar. O custo é %.0f s de máquina para '
                                     '%.0f s de áudio.' % (seg_maquina, seg_audio)),
        'VELOCIDADE_MEDIDA_AGORA': round(vel, 2),
        **fl.carimbo(modelo, ferro),
        'A_FILA_QUE_MANDOU': 'data/samples/YOUTUBE-RELEVANCIA/FILA-WHISPER.json',
        'O_QUE_NAO_ESTA_AQUI': ('todo vídeo que já tinha legenda pública. Ele não foi '
                                'esquecido: está em YOUTUBE-JANELA/LEGENDAS.json, de '
                                'graça e com tempos.'),
        'ITEMS': saida})
    print()
    print('gravado: %s' % p)
    print('velocidade medida agora: %.2fx · %d itens' % (vel, len(saida)))
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'alvos'
    if cmd == 'alvos':
        raise SystemExit(fase_alvos())
    if cmd == 'rodar':
        raise SystemExit(fase_rodar(sys.argv[2] if len(sys.argv) > 2 else None,
                                    sys.argv[3] if len(sys.argv) > 3 else None))
    print('uso: youtube_transcrever.py {alvos|rodar [modelo] [teto]}')
    raise SystemExit(2)
