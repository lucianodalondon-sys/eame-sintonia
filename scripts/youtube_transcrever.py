#!/usr/bin/env python3
"""
A ESCADA DO TEXTO DO YOUTUBE — título, depois legenda, e só então o whisper.

    py scripts/youtube_transcrever.py estado          # a máquina tem com que transcrever?
    py scripts/youtube_transcrever.py alvos           # GRÁTIS: o que a fila manda
    py scripts/youtube_transcrever.py escada          # a escada inteira, sobre a fila
    py scripts/youtube_transcrever.py escada 10       # sobre os 10 primeiros
    py scripts/youtube_transcrever.py escada ids:a,b  # sobre estes vídeos, e só eles
    py scripts/youtube_transcrever.py rodar small 20  # o nome antigo de `escada`

A ORDEM É LEI, E ELA NÃO É MINHA
==================================
`youtube_janela.py` a declara na primeira página dele:

    LOTE CONGELADO → CANAL → OBJETO → LEGENDA → (só então) WHISPER → (só então) PAGO

Este arquivo é o degrau `WHISPER`, e a única coisa que ele acrescenta à ordem é
OBEDECÊ-LA vídeo a vídeo, em vez de fase a fase:

    1. título e metadados             — já vieram de graça na grade do canal
    2. tentar a legenda nativa        — quem tenta é `youtube_janela.py`, o dono dela
    3. legenda utilizável?            — USA A LEGENDA e NÃO roda o whisper
    4. legenda não pôde ser usada?    — registra exatamente POR QUÊ, e tenta o whisper
    5. os dois falharam?              — permanece NÃO SEI, e diz de qual dos dois

    ESTE ARQUIVO NÃO É DONO DE COLETA. ELE NÃO ABRE CANAL, NÃO LÊ GRADE E NÃO
    BUSCA LEGENDA. Ele lê o que os donos gravaram e decide o que fazer com o buraco.

FALHA TÉCNICA DA LEGENDA NÃO É "VÍDEO SEM LEGENDA"
====================================================
Esta é a lei mais importante do arquivo, e ela existe porque o erro contrário é mudo.
Um 429 de um IP de datacenter e um vídeo sem faixa de legenda produzem, os dois, um
lugar vazio onde o texto deveria estar. Escrever "SEM_LEGENDA" nos dois casos custa
duas coisas: manda o whisper transcrever som que já existia escrito, e ensina ao
acervo que aquele vídeo não tem legenda — para sempre, porque ninguém reconfere.

    HTTP 429 DE UM IP ≠ PÁGINA FECHADA PARA TODOS.
    E NENHUM DOS DOIS É "O VÍDEO NÃO TEM LEGENDA".

Por isso o estado da legenda que este arquivo grava tem CINCO nomes, não um:

    NO_CAPTION_CONFIRMED ........ o player declarou que não há faixa. É o único
                                  caso limpo: o vídeo REALMENTE não tem legenda.
    CAPTION_ENVIRONMENT_FAILURE . a porta não abriu, ou abriu e veio CAPTCHA/429.
                                  Isto é sobre a REDE desta máquina, não sobre o vídeo.
    CAPTION_FETCH_FAILURE ....... a faixa existe, foi pedida, e o corpo não chegou
                                  (erro de rede no `timedtext`, ou 0 byte de resposta).
    CAPTION_PARSE_FAILURE ....... o corpo chegou e eu não soube ler. O defeito é meu.
    CAPTION_DELIVERED_EMPTY ..... o corpo chegou, era JSON legítimo, e não tinha texto.

O quinto nome não estava na lista da missão, e ele está aqui porque o repositório
produz esse caso e ele não cabia em nenhum dos quatro sem mentir: `_timedtext` volta
sem trechos tanto quando o servidor manda 0 byte quanto quando manda uma legenda
vazia, e essas duas coisas pedem condutas diferentes de quem for tentar de novo.

    ESTADO QUE NÃO EXISTE VIRA ESTADO ERRADO. NUNCA VIRA SILÊNCIO.

E o sexto, que é ausência de pergunta e não ausência de resposta:

    CAPTION_NOT_TESTED .......... ninguém rodou a fase de legenda sobre este vídeo.
                                  Aqui o whisper NÃO roda — porque pular a legenda para
                                  gastar hora de máquina é inverter a ordem, e a ordem
                                  é lei. Rode `youtube_janela.py legendas` antes.

O IDIOMA ESTAVA SENDO ADIVINHADO, E NINGUÉM SABIA
===================================================
A versão anterior deste arquivo lia `o.get('COUNTRY_SCOPE')` de um item de
`FILA-WHISPER.json` e passava o resultado para `IDIOMA_DO_PAIS`. Dois defeitos
empilhados, medidos em 2026-09-04:

  1. O item da fila **nunca teve** o campo `COUNTRY_SCOPE`. `get` devolvia `None`.
  2. Mesmo em `OBJETOS.json`, onde o campo existe, ele **não é um código de país**:
     vale `LOCAL_COUNTRY_PROVED`, que é um ESCOPO. `IDIOMA_DO_PAIS` não tem essa
     chave, e devolveria `None` do mesmo jeito.

Resultado: `language=None` em 240 de 240 vídeos, e autodetecção por vídeo em todos —
exatamente a coisa que `instagram_transcrever.py` proíbe em prosa, com a medição de
dois reels espanhóis que voltaram `en` com confiança 0,37.

    ESCOPO NÃO É PAÍS. E `get` QUE DEVOLVE `None` NÃO AVISA QUE ERROU.

O código do país existe, e num lugar só: o campo `COUNTRY` do LOTE CONGELADO. Este
arquivo faz o `join` por `ACCOUNT_HANDLE` contra o lote e grava
`ASR_LANGUAGE_ORIGEM` dizendo de onde o idioma veio — declarado, ou detectado.

O ÁUDIO, E POR QUE ELE NÃO PRECISA MAIS DO `ffmpeg`
=====================================================
A versão anterior pedia `-x --audio-format wav` ao `yt-dlp`, o que obriga o `ffmpeg`
a existir no PATH. Não precisa: o `faster-whisper` decodifica pelo PyAV, que traz as
bibliotecas dele próprias. Medido neste contêiner, que **não tem `ffmpeg`**: 218 s de
fala espanhola em `.mp3` foram transcritos em 39,5 s de máquina, 5,53x.

    A FAIXA NATIVA BASTA. CONVERTER PARA WAV ERA UMA DEPENDÊNCIA PAGA EM NADA.

E um segundo defeito medido no mesmo dia: a chamada era
`subprocess.run([sys.executable, '-m', 'yt_dlp', ...])`, e o processo filho **não
herda o `sys.path` que este arquivo monta** para achar `~/.sintonia-libs`. O filho
respondia `No module named yt_dlp` com o `yt_dlp` instalado. Agora o `PYTHONPATH`
viaja no ambiente do filho.

Nada de login, nada de cookie de conta, nada de CAPTCHA, nada de Apify, nada pago.
Se a rota pública não entregar o áudio, o estado é `WHISPER_AUDIO_FAILURE` — que é
uma confissão sobre a minha rede, e nunca um veredito sobre a fala do vídeo.

O CACHE, E O QUE ELE NÃO PODE CACHEAR
=======================================
A chave mínima é `VIDEO_ID | ASR_ENGINE | ASR_MODEL | ASR_LANGUAGE`, e ela mora em
`asr_local.chave()`. A versão anterior guardava por `VIDEO_ID` sozinho: trocar
`YT_MODELO` de `small` para `base` devolvia, em silêncio, o texto do `small`.

    CACHE COM CHAVE CURTA DEMAIS NÃO ERRA. ELE RESPONDE A OUTRA PERGUNTA.

E só entra no cache o que terminou em `WHISPER_OK`. Cachear um `WHISPER_AUDIO_FAILURE`
transformaria uma rede ruim de terça-feira numa condenação permanente daquele vídeo.
Quando a configuração muda, o resultado antigo **não é apagado**: ele fica no arquivo,
com a chave dele, e os dois convivem.

O QUE ESTE ARQUIVO NÃO FAZ
============================
Não classifica assunto, não decide relevância, não resume, não traduz e — a mais
importante — **não infere identidade, papel nem entidade a partir da fala**. Quem
falou, de que empresa e de que país são fatos do LOTE CONGELADO, provados de graça
antes de qualquer áudio tocar. A transcrição é conteúdo; ela nunca é prova de quem é
quem.

    O QUE A PESSOA DIZ NÃO DIZ QUEM ELA É.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import asr_local                 # noqa: E402  — a camada técnica, que não sabe de YouTube

LIBS = asr_local.LIBS

SAMPLES = os.path.join(ROOT, 'data', 'samples')
JANELA = os.path.join(SAMPLES, 'YOUTUBE-JANELA')
RELEVANCIA = os.path.join(SAMPLES, 'YOUTUBE-RELEVANCIA')
LOTE = os.path.join(SAMPLES, 'COMPETITOR-PUBLIC-COMM', 'PUBLIC-COMM-FIRST-BATCH-EAME.json')
SAIDA = os.path.join(SAMPLES, 'YOUTUBE-TRANSCRICOES')
# Descartável e reproduzível: o áudio é insumo, a transcrição é o resultado. Já está
# em `.gitignore` — e é por isso que este caminho, e não o de YOUTUBE-JANELA.
MEDIA = os.path.join(SAIDA, 'audio-cache')

MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'
NAO_SEI = 'NOT_KNOWN'

MODELO_PADRAO = os.environ.get('YT_MODELO') or asr_local.MODELO_PADRAO

# ── OS ESTADOS DA LEGENDA, VISTOS DAQUI ────────────────────────────────────────────
CAPTION_OK = 'YOUTUBE_CAPTION_USABLE'
NO_CAPTION_CONFIRMED = 'NO_CAPTION_CONFIRMED'
CAPTION_ENVIRONMENT_FAILURE = 'CAPTION_ENVIRONMENT_FAILURE'
CAPTION_FETCH_FAILURE = 'CAPTION_FETCH_FAILURE'
CAPTION_PARSE_FAILURE = 'CAPTION_PARSE_FAILURE'
CAPTION_DELIVERED_EMPTY = 'CAPTION_DELIVERED_EMPTY'
CAPTION_NOT_TESTED = 'CAPTION_NOT_TESTED'

# ── OS ESTADOS DO WHISPER ──────────────────────────────────────────────────────────
WHISPER_NOT_NEEDED = 'WHISPER_NOT_NEEDED'
WHISPER_NOT_TRIED = 'WHISPER_NOT_TRIED'
WHISPER_ENGINE_MISSING = asr_local.SEM_MOTOR
WHISPER_AUDIO_FAILURE = asr_local.AUDIO_ILEGIVEL
WHISPER_OK = asr_local.OK

# ── DE ONDE VEIO O TEXTO ───────────────────────────────────────────────────────────
YOUTUBE_CAPTION = 'YOUTUBE_CAPTION'
WHISPER_LOCAL = 'WHISPER_LOCAL'
TITLE_ONLY = 'TITLE_ONLY'

# Exceções de REDE contra exceções de LEITURA. A diferença decide se vale tentar de
# novo: rede se conserta sozinha, defeito de leitor não.
ERRO_DE_REDE = ('HTTPError', 'URLError', 'TimeoutError', 'timeout', 'socket.timeout',
                'ConnectionResetError', 'IncompleteRead', 'RemoteDisconnected',
                'ContentTooShortError', 'SSLError', 'ConnectionError')

# Clientes públicos do player, tentados nesta ordem. NENHUM deles usa login, cookie de
# conta ou CAPTCHA resolvido — são as superfícies públicas que o próprio `yt-dlp`
# oferece. Medido em 2026-09-04 neste contêiner: o cliente padrão respondeu
# "Sign in to confirm you're not a bot" e o `android` respondeu com metadado.
CLIENTES = [c for c in (os.environ.get('YT_PLAYER_CLIENTS') or 'default,android').split(',') if c]

# Teto de download por vídeo. Um áudio que não termina em 10 minutos não é um áudio
# lento: é uma rota que não vai entregar.
TETO_DOWNLOAD_S = int(os.environ.get('YT_TETO_DOWNLOAD_S') or 600)


def agora():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def hoje():
    import datetime
    return datetime.date.today().isoformat()


def _ler_json(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/YOUTUBE-TRANSCRICOES/' + nome


# ═════════════════════════════════════════ O PAÍS, QUE SÓ O LOTE CONGELADO CONHECE

def paises_do_lote():
    """ACCOUNT_HANDLE → {'COUNTRY', 'NO_LOTE'}. O código de país não existe em outro lugar.

    `NO_LOTE` diz se a conta está em `ACCOUNTS` (dentro do lote) ou em
    `EXCLUDED_ACCOUNTS` (fora dele, de propósito). Quem gasta hora de máquina precisa
    saber a diferença — ver a prosa de `escada()` sobre isso.
    """
    d = _ler_json(LOTE)
    if not d:
        return {}
    mapa = {}

    def anda(o, dentro):
        if isinstance(o, dict):
            if o.get('PLATFORM') == 'YOUTUBE' and o.get('ACCOUNT_HANDLE'):
                mapa[o['ACCOUNT_HANDLE']] = {'COUNTRY': o.get('COUNTRY', NAO_SEI),
                                             'NO_LOTE': dentro,
                                             'PAGE_ROLE': o.get('PAGE_ROLE', NAO_SEI)}
            for k, v in o.items():
                anda(v, False if k == 'EXCLUDED_ACCOUNTS' else dentro)
        elif isinstance(o, list):
            for v in o:
                anda(v, dentro)

    anda(d.get('ACCOUNTS') or [], True)
    anda(d.get('EXCLUDED_ACCOUNTS') or [], False)
    return mapa


# ══════════════════════════════════════════════════ DEGRAU 2 · O ESTADO DA LEGENDA

def estado_da_legenda(item):
    """Um item de LEGENDAS.json (ou None) → (ESTADO, POR_QUE, RETENTAR_LEGENDA).

    Função PURA: sem rede, sem disco, sem modelo. É assim de propósito — a escada
    inteira depende desta tradução, e uma decisão que só pode ser provada com rede
    não é provada nunca.
    """
    if item is None:
        return (CAPTION_NOT_TESTED,
                'a fase `legendas` ainda não rodou sobre este vídeo. Isto NÃO diz que '
                'ele não tem legenda — diz que ninguém perguntou.', True)

    estado = item.get('CAPTION_STATE')

    if estado == 'PRESENTE' and (item.get('TRANSCRICAO') or item.get('CAPTION_SEGMENTS')):
        return (CAPTION_OK,
                'legenda pública lida de graça, com tempos — o whisper não precisa rodar',
                False)

    if estado == 'AUSENTE':
        return (NO_CAPTION_CONFIRMED,
                'o player declarou a lista de faixas e ela veio vazia. Este é o único '
                'caso em que "não tem legenda" é uma afirmação, e não uma desculpa.',
                False)

    if estado in ('PORTA_NAO_ABRIU', 'PLAYER_RESPONSE_AUSENTE'):
        return (CAPTION_ENVIRONMENT_FAILURE,
                'a página do vídeo não chegou até aqui (%s). Isto é sobre a REDE desta '
                'máquina, não sobre o vídeo — e não autoriza ninguém a escrever que ele '
                'não tem legenda.' % (item.get('POR_QUE') or estado),
                True)

    if estado == 'DECLARADA_MAS_VAZIA':
        tipo = item.get('TIMEDTEXT_ERRO_TIPO')
        vazio = item.get('TIMEDTEXT_VAZIO_POR_QUE')
        if tipo:
            if tipo in ERRO_DE_REDE:
                return (CAPTION_FETCH_FAILURE,
                        'a faixa existe e o corpo não chegou: %s. Rede, não vídeo.'
                        % item.get('TIMEDTEXT_ERRO', tipo), True)
            return (CAPTION_PARSE_FAILURE,
                    'o corpo chegou e eu não soube ler: %s. O defeito é meu, não da '
                    'fonte.' % item.get('TIMEDTEXT_ERRO', tipo), False)
        if vazio == 'CORPO_VAZIO':
            return (CAPTION_FETCH_FAILURE,
                    'o servidor respondeu 0 byte para uma faixa que ele mesmo declarou. '
                    'Sem assinatura válida é o que acontece.', True)
        if vazio == 'SEM_TRECHOS':
            return (CAPTION_DELIVERED_EMPTY,
                    'o corpo chegou, era JSON legítimo, e nenhum evento tinha texto. A '
                    'legenda existe e está vazia — é diferente de não existir.', False)
        # Item gravado ANTES de `TIMEDTEXT_VAZIO_POR_QUE` existir. Não dá para saber
        # qual dos dois foi, e chutar seria pior do que confessar.
        return (CAPTION_PARSE_FAILURE,
                'faixa declarada e corpo não aproveitado, por um artefato antigo que não '
                'registrou a causa. Reler a legenda deste vídeo resolve a dúvida.', True)

    if estado in (None, 'NOT_TESTED'):
        return (CAPTION_NOT_TESTED,
                'o item não carrega estado de legenda utilizável (%s)' % estado, True)

    return (CAPTION_PARSE_FAILURE,
            'estado de legenda desconhecido para este leitor: %r. Um estado novo do dono '
            'da legenda chegou aqui sem tradução — e virar silêncio seria pior.' % estado,
            True)


def texto_da_legenda(item):
    """Os trechos da legenda no vocabulário ÚNICO da escada. → (texto, segmentos).

    O repositório tem quatro vocabulários para a mesma coisa: `T_MS/DUR_MS/TEXTO` na
    legenda, `start/end/text` no Instagram, `T_S/FIM_S/TEXTO` na versão anterior deste
    arquivo e `START_S/END_S/TEXT` na camada de ASR. A escada declara UM —
    `START_S/END_S/TEXT`, em SEGUNDOS — e traduz na entrada.

        MILISSEGUNDO E SEGUNDO NA MESMA CHAVE É ERRO DE MIL VEZES QUE PARECE CERTO.

    E `DUR_MS` é DURAÇÃO, não fim: quem somar errado encurta toda citação do acervo.
    """
    segs = []
    for t in (item.get('TRANSCRICAO') or []):
        ini = t.get('T_MS')
        dur = t.get('DUR_MS')
        comeco = round(ini / 1000.0, 2) if isinstance(ini, (int, float)) else NAO_SEI
        fim = (round((ini + dur) / 1000.0, 2)
               if isinstance(ini, (int, float)) and isinstance(dur, (int, float))
               else NAO_SEI)
        segs.append({'START_S': comeco, 'END_S': fim, 'TEXT': (t.get('TEXTO') or '').strip()})
    return ' '.join(s['TEXT'] for s in segs).strip(), segs


# ═══════════════════════════════════════════════════════ DEGRAU 4 · O ÁUDIO, E SÓ ELE

def _ambiente_filho():
    """O `PYTHONPATH` que faz o processo filho enxergar `~/.sintonia-libs`.

    Sem isto o filho responde `No module named yt_dlp` com o `yt_dlp` instalado — o
    `sys.path` que este arquivo monta morre no processo dele. Medido em 2026-09-04.
    """
    env = dict(os.environ)
    caminhos = [p for p in (LIBS, env.get('PYTHONPATH')) if p]
    env['PYTHONPATH'] = os.pathsep.join(caminhos)
    return env


# Sobras do `yt-dlp` quando um download morre no meio. Um `.part` de 4 MB é um arquivo
# grande e legítimo aos olhos de `getsize` — e é meio vídeo. Tratá-lo como áudio pronto
# transcreveria metade da fala e chamaria isso de transcrição completa.
#
#     ARQUIVO PELA METADE NÃO SE DENUNCIA. ELE SÓ TERMINA CEDO.
SOBRAS = ('.part', '.ytdl', '.temp', '.tmp', '.part-Frag')


def _audio_em_cache(video_id):
    """O áudio já baixado deste vídeo, em qualquer container. → caminho ou None."""
    if not os.path.isdir(MEDIA):
        return None
    for nome in sorted(os.listdir(MEDIA)):
        if not nome.startswith(video_id + '.'):
            continue
        if any(nome.endswith(s) or ('%s.' % s) in nome for s in SOBRAS):
            continue
        if os.path.getsize(os.path.join(MEDIA, nome)) > 1000:
            return os.path.join(MEDIA, nome)
    return None


def audio(video_id):
    """→ (caminho, ROTA, POR_QUE). SÓ áudio: vídeo completo seria pagar banda por imagem.

    A faixa vem no container nativo (`m4a`/`webm`) e NÃO é convertida: o PyAV que o
    `faster-whisper` já usa decodifica os dois. Converter para WAV exigiria `ffmpeg`,
    e esse `ffmpeg` seria uma dependência inteira paga em nada.
    """
    os.makedirs(MEDIA, exist_ok=True)
    ja = _audio_em_cache(video_id)
    if ja:
        return ja, 'AUDIO_CACHE_HIT', 'áudio já estava no cache: %s' % os.path.basename(ja)

    url = 'https://www.youtube.com/watch?v=' + video_id
    falhas = []
    for cliente in CLIENTES:
        cmd = [sys.executable, '-m', 'yt_dlp', '-q', '--no-warnings', '--no-progress',
               '-f', 'bestaudio/bestaudio*/best',
               '-o', os.path.join(MEDIA, '%(id)s.%(ext)s'), url]
        if cliente and cliente != 'default':
            cmd += ['--extractor-args', 'youtube:player_client=' + cliente]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=TETO_DOWNLOAD_S, env=_ambiente_filho())
        except subprocess.TimeoutExpired:
            falhas.append('%s: estourou %ds' % (cliente, TETO_DOWNLOAD_S))
            continue
        achado = _audio_em_cache(video_id)
        if achado:
            return achado, 'YT_DLP:' + cliente, 'faixa nativa, sem conversão'
        linhas = [x for x in (r.stderr or r.stdout or '').strip().splitlines() if x.strip()]
        falhas.append('%s: %s' % (cliente, (linhas[-1][:160] if linhas else 'sem mensagem')))
    return None, 'NENHUMA', ' | '.join(falhas) or 'nenhum cliente público tentado'


# ═══════════════════════════════════════════════════════════════ O CACHE DE ASR

def _ler_cache():
    d = _ler_json(os.path.join(SAIDA, 'ASR-CACHE.json')) or {}
    return {i['ASR_CACHE_KEY']: i for i in (d.get('ITEMS') or []) if i.get('ASR_CACHE_KEY')}


def _gravar_cache(cache):
    """O cache é ACUMULATIVO: resultado de outra configuração nunca é apagado.

    Trocar de modelo é uma decisão, e ela produz um texto NOVO — não uma correção do
    anterior. Quem quiser comparar `small` com `base` precisa dos dois no arquivo, com
    a chave de cada um. Apagar o antigo transformaria a comparação em fé.
    """
    itens = sorted(cache.values(), key=lambda i: i['ASR_CACHE_KEY'])
    return _gravar('ASR-CACHE.json', {
        'SOURCE_ID': 'YOUTUBE-TRANSCRICOES/ASR-CACHE',
        'source': ('resultados de reconhecimento local já pagos em tempo de máquina, '
                   'guardados para não serem pagos de novo'),
        'SOURCE_LOCATION': 'derivado — máquina local, nenhuma rota paga',
        'FACT_LOCATION': 'NOT_KNOWN — o lugar do fato sai do conteúdo, nunca da conta',
        'ORIGINAL_LANGUAGE': 'multi',
        'EVIDENCE_CLASS': 'LOCAL_ASR',
        'captured_at': hoje(), 'CAPTURED_AT': agora(),
        'APIFY_RUNS': 0, 'COST_USD': 0, 'PAID_API_COST_USD': 0,
        'A_CHAVE': 'VIDEO_ID | ASR_ENGINE | ASR_MODEL | ASR_LANGUAGE',
        'POR_QUE_ESSA_CHAVE': (
            'modelo e idioma mudam o TEXTO e por isso entram. Beam, lote e número de '
            'núcleos mudam só o TEMPO e por isso NÃO entram — uma chave que muda com o '
            'número de núcleos transforma "trocar de máquina" em "transcrever tudo de novo".'),
        'SO_ENTRA_O_QUE_DEU_CERTO': (
            'apenas WHISPER_OK é cacheado. Cachear uma falha de áudio transformaria uma '
            'rede ruim de hoje numa condenação permanente daquele vídeo.'),
        'NADA_E_APAGADO': (
            'trocar de configuração ACRESCENTA uma entrada. A antiga fica, com a chave '
            'dela — senão a comparação entre dois modelos vira fé.'),
        'ENTRADAS': len(itens),
        'ITEMS': itens})


# ═══════════════════════════════════════════════════════════════════════ A ESCADA

def universo(ids=None, teto=None, so_da_fila=False):
    """Quem vai passar pela escada, e a partir de quais artefatos. → (lista, avisos)."""
    objetos = _ler_json(os.path.join(JANELA, 'OBJETOS.json'))
    avisos = []
    if not objetos:
        return None, ['sem OBJETOS.json — rode `py scripts/youtube_janela.py objetos` antes']
    itens = objetos['ITEMS']
    if so_da_fila:
        fila = _ler_json(os.path.join(RELEVANCIA, 'FILA-WHISPER.json')) or {}
        ordem = [q['VIDEO_ID'] for q in (fila.get('QUEUE') or [])]
        if not ordem:
            avisos.append(
                'FILA_VAZIA=YES · o portão de relevância não aprovou nenhum vídeo (%s). '
                'A escada roda sobre o acervo, e a fila continua sendo quem ordena quando '
                'houver ordem.' % (fila.get('QUAL_CRITERIO_REALMENTE_FILTRA') or 'sem motivo'))
        else:
            por_id = {i['VIDEO_ID']: i for i in itens}
            itens = [por_id[v] for v in ordem if v in por_id]
    if ids:
        pedidos = [str(i).strip() for i in ids if str(i).strip()]
        por_id = {i['VIDEO_ID']: i for i in itens}
        faltando = [i for i in pedidos if i not in por_id]
        if faltando:
            avisos.append('%d VIDEO_ID pedidos não estão no acervo: %s'
                          % (len(faltando), ', '.join(faltando[:6])))
        itens = [por_id[i] for i in pedidos if i in por_id]
    elif teto:
        itens = itens[:int(teto)]
    return itens, avisos


def escada(ids=None, teto=None, modelo=None, so_da_fila=False):
    """A escada inteira, vídeo a vídeo. → 0/1.

    SOBRE OS 30 VÍDEOS DE UMA CONTA QUE O LOTE EXCLUIU
    ---------------------------------------------------
    `youtube_janela.contas()` percorre o lote congelado INTEIRO e casa qualquer registro
    com `PLATFORM=YOUTUBE`, sem olhar em que lista ele está. Por isso `OBJETOS.json`
    tem 30 vídeos de `CortevaBiologicals`, que o lote registrou em `EXCLUDED_ACCOUNTS`
    com `PAGE_ROLE=PRODUCT_BRAND` — 12,5% do acervo.

        ISTO NÃO É CONSERTADO AQUI, E A OMISSÃO É DELIBERADA.

    Consertar seria mudar quem entra na coleta, e quem entra na coleta é decisão do dono
    da coleta, não de quem transcreve. O que este arquivo faz é o que lhe cabe: marca
    cada item com `NO_LOTE_CONGELADO`, e o relatório mostra quanta hora de máquina foi
    gasta fora do lote. Quem manda decide depois, vendo o número.
    """
    modelo = modelo or MODELO_PADRAO
    alvos, avisos = universo(ids=ids, teto=teto, so_da_fila=so_da_fila)
    for a in avisos:
        print('  ⚠️  %s' % a)
    if alvos is None:
        return 1
    if not alvos:
        print('nenhum objeto selecionado — nada a fazer, e isso não é falha.')
        return 0

    legendas = _ler_json(os.path.join(JANELA, 'LEGENDAS.json')) or {}
    por_legenda = {i['VIDEO_ID']: i for i in (legendas.get('ITEMS') or [])}
    lote = paises_do_lote()
    cache = _ler_cache()

    # O motor só é carregado se ALGUÉM precisar dele. Carregar custa dezenas de segundos,
    # e um acervo inteiramente legendado não deve pagar por isso.
    motor, sem_motor_por_que = None, None

    itens = []
    contas = {'CAPTION_HITS': 0, 'WHISPER_FALLBACKS': 0, 'WHISPER_SUCCESS': 0,
              'WHISPER_FAILURES': 0, 'CACHE_HITS': 0, 'CAPTION_NOT_TESTED': 0,
              'AUDIO_CACHE_HITS': 0}
    audio_s, maquina_s = 0.0, 0.0

    for n, o in enumerate(alvos, 1):
        vid = o['VIDEO_ID']
        handle = o.get('ACCOUNT_HANDLE')
        do_lote = lote.get(handle) or {}
        pais = do_lote.get('COUNTRY', NAO_SEI)
        idioma = asr_local.idioma_do_pais(pais)

        d = {
            'VIDEO_ID': vid,
            'SOURCE_ID': 'YOUTUBE-TRANSCRICOES/TEXTO/%s' % vid,
            'SOURCE_URL': o.get('VIDEO_URL') or ('https://www.youtube.com/watch?v=' + vid),
            'ACCOUNT_HANDLE': handle,
            'COMPANY': o.get('COMPANY', NAO_SEI),
            'COUNTRY_SCOPE': o.get('COUNTRY_SCOPE', NAO_SEI),
            'COUNTRY': pais,
            'NO_LOTE_CONGELADO': do_lote.get('NO_LOTE', NAO_SEI),
            'PAGE_ROLE': do_lote.get('PAGE_ROLE', NAO_SEI),
            'TITLE': o.get('TITLE', NAO_SEI),
            'DURATION_S': o.get('DURATION_S', NAO_SEI),
            'PUBLISHED_RELATIVE': o.get('PUBLISHED_RELATIVE', NAO_SEI),
            'LANGUAGE': idioma or NAO_SEI,
            'LANGUAGE_ORIGEM': ('DECLARADO_PELO_LOTE:%s' % pais if idioma
                                else 'NAO_DECLARADO — o lote não dá país para este handle'),
            'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
            'CAPTURED_AT': agora(),
            'COST_USD': 0, 'PAID_API_COST_USD': 0, 'APIFY_RUNS': 0,
            'IDENTITY_FROM_CONTENT': 'NONE — identidade vem do lote congelado, nunca da fala',
        }

        estado_leg, por_que_leg, retentar = estado_da_legenda(por_legenda.get(vid))
        d['CAPTION_STATE'] = estado_leg
        d['CAPTION_POR_QUE'] = por_que_leg
        d['CAPTION_RETRY_RECOMENDADO'] = 'YES' if retentar else 'NO'

        # ── DEGRAU 3 · legenda utilizável ⇒ o whisper NÃO roda ───────────────────
        if estado_leg == CAPTION_OK:
            texto, segs = texto_da_legenda(por_legenda[vid])
            item_leg = por_legenda[vid]
            d.update({
                'TEXT_SOURCE': YOUTUBE_CAPTION,
                'WHISPER_STATE': WHISPER_NOT_NEEDED,
                'TRANSCRIPT': texto or None,
                'TRANSCRIPT_SEGMENTS': segs,
                'TRANSCRIPT_CHARS': len(texto),
                'CAPTION_LANG': item_leg.get('CAPTION_LANG', NAO_SEI),
                'CAPTION_KIND': item_leg.get('CAPTION_KIND', NAO_SEI),
                'MACHINE_SECONDS': 0,
                'POR_QUE_NAO_RODOU_WHISPER': (
                    'a legenda pública já trouxe o texto COM tempos, de graça. Rodar o '
                    'whisper aqui seria pagar hora de máquina por som que já veio escrito.'),
            })
            contas['CAPTION_HITS'] += 1
            itens.append(d)
            print('  %3d/%d %-13s LEGENDA      %5d chars  %s'
                  % (n, len(alvos), vid, len(texto), str(d['TITLE'])[:34]))
            continue

        # ── DEGRAU 5a · ninguém perguntou pela legenda ⇒ não inverter a ordem ─────
        if estado_leg == CAPTION_NOT_TESTED:
            d.update({'TEXT_SOURCE': TITLE_ONLY, 'WHISPER_STATE': WHISPER_NOT_TRIED,
                      'TRANSCRIPT': None, 'TRANSCRIPT_SEGMENTS': [],
                      'MACHINE_SECONDS': 0,
                      'POR_QUE_NAO_RODOU_WHISPER': (
                          'a ordem é LEGENDA antes de WHISPER. Gastar hora de máquina '
                          'antes de perguntar pela legenda seria inverter a ordem — e a '
                          'ordem é a economia inteira desta missão.')})
            contas['CAPTION_NOT_TESTED'] += 1
            itens.append(d)
            print('  %3d/%d %-13s SEM PERGUNTA (rode `youtube_janela.py legendas` antes)'
                  % (n, len(alvos), vid))
            continue

        # ── DEGRAU 4 · a legenda não pôde ser usada ⇒ o whisper é chamado ─────────
        contas['WHISPER_FALLBACKS'] += 1
        chave = asr_local.chave(vid, asr_local.config(modelo=modelo), idioma)
        d['ASR_CACHE_KEY'] = chave
        if chave in cache:
            guardado = cache[chave]
            d.update({k: v for k, v in guardado.items()
                      if k not in ('ASR_CACHE_KEY', 'VIDEO_ID')})
            d.update({'TEXT_SOURCE': WHISPER_LOCAL, 'WHISPER_STATE': WHISPER_OK,
                      'CACHE_HIT': 'YES',
                      'MACHINE_SECONDS': 0,
                      'MACHINE_SECONDS_ORIGINAL': guardado.get('MACHINE_SECONDS'),
                      'POR_QUE_CACHE': ('mesmo vídeo, mesmo motor, mesmo modelo, mesmo '
                                        'idioma — o áudio não é baixado e o whisper não '
                                        'roda de novo.')})
            contas['CACHE_HITS'] += 1
            contas['WHISPER_SUCCESS'] += 1
            itens.append(d)
            print('  %3d/%d %-13s CACHE        %5s chars  %s'
                  % (n, len(alvos), vid, d.get('TRANSCRIPT_CHARS', 0), str(d['TITLE'])[:34]))
            continue

        d['CACHE_HIT'] = 'NO'
        caminho, rota, por_que_audio = audio(vid)
        d['AUDIO_ROUTE'] = rota
        d['AUDIO_POR_QUE'] = por_que_audio
        if rota == 'AUDIO_CACHE_HIT':
            contas['AUDIO_CACHE_HITS'] += 1
        if not caminho:
            d.update({'TEXT_SOURCE': TITLE_ONLY, 'WHISPER_STATE': WHISPER_AUDIO_FAILURE,
                      'TRANSCRIPT': None, 'TRANSCRIPT_SEGMENTS': [], 'MACHINE_SECONDS': 0,
                      'NAO_SIGNIFICA': ('que o vídeo não tem fala. Significa que eu não '
                                        'consegui o áudio pela rota pública.')})
            contas['WHISPER_FAILURES'] += 1
            itens.append(d)
            print('  %3d/%d %-13s SEM ÁUDIO    %s' % (n, len(alvos), vid, por_que_audio[:44]))
            continue

        if motor is None and sem_motor_por_que is None:
            motor, sem_motor_por_que = asr_local.carregar(modelo=modelo)
            if motor:
                print('  motor %s carregado em %.1f s · %d núcleos'
                      % (motor.cfg['ASR_MODEL'], motor.segundos_de_carga,
                         motor.cfg['ASR_CPU_THREADS']))
        if not motor:
            d.update({'TEXT_SOURCE': TITLE_ONLY, 'WHISPER_STATE': WHISPER_ENGINE_MISSING,
                      'TRANSCRIPT': None, 'TRANSCRIPT_SEGMENTS': [], 'MACHINE_SECONDS': 0,
                      'WHY': sem_motor_por_que,
                      'NAO_SIGNIFICA': 'que o vídeo não tem fala. O motor é que não existe aqui.'})
            contas['WHISPER_FAILURES'] += 1
            itens.append(d)
            print('  %3d/%d %-13s SEM MOTOR' % (n, len(alvos), vid))
            continue

        dur = o.get('DURATION_S')
        r = motor.transcrever(caminho, language=idioma,
                              duracao_esperada_s=dur if isinstance(dur, (int, float)) else None)
        d.update({k: v for k, v in r.items() if k != 'ESTADO'})
        d['WHISPER_STATE'] = r['ESTADO']
        d['TRANSCRIBED_AT'] = agora()
        maquina_s += float(r.get('MACHINE_SECONDS') or 0)
        if isinstance(r.get('AUDIO_SECONDS'), (int, float)):
            audio_s += r['AUDIO_SECONDS']
        if r['ESTADO'] == WHISPER_OK:
            d['TEXT_SOURCE'] = WHISPER_LOCAL
            contas['WHISPER_SUCCESS'] += 1
            # Só o que deu certo entra no cache. Ver a prosa de `_gravar_cache`.
            cache[chave] = dict({k: v for k, v in d.items() if k in (
                'VIDEO_ID', 'TRANSCRIPT', 'TRANSCRIPT_SEGMENTS', 'TRANSCRIPT_CHARS',
                'ASR_ENGINE', 'ASR_MODEL', 'ASR_DEVICE', 'ASR_COMPUTE_TYPE', 'ASR_BEAM',
                'ASR_BATCH', 'ASR_CPU_THREADS', 'ASR_LANGUAGE', 'ASR_LANGUAGE_DECLARADO',
                'LANGUAGE_DETECTED', 'LANGUAGE_CONFIDENCE', 'AUDIO_SECONDS',
                'MACHINE_SECONDS', 'REALTIME_FACTOR', 'TRANSCRIBED_AT')},
                ASR_CACHE_KEY=chave)
            print('  %3d/%d %-13s WHISPER      %5d chars  %5.1f s máquina  %s'
                  % (n, len(alvos), vid, d.get('TRANSCRIPT_CHARS', 0),
                     r.get('MACHINE_SECONDS', 0), str(d['TITLE'])[:26]))
        else:
            d['TEXT_SOURCE'] = TITLE_ONLY if not r.get('TRANSCRIPT') else WHISPER_LOCAL
            contas['WHISPER_FAILURES'] += 1
            print('  %3d/%d %-13s %-12s %s'
                  % (n, len(alvos), vid, r['ESTADO'][:12], str(r.get('WHY', ''))[:38]))
        itens.append(d)

    _gravar_cache(cache)
    caminho = _gravar('TEXTO.json', _cabecalho(itens, contas, audio_s, maquina_s, modelo))
    _resumo(caminho, itens, contas, audio_s, maquina_s)
    return 0


# ══════════════════════════════════════════════════════════ O ARTEFATO E A AUDITORIA

def auditar_identidade(itens):
    """Os quatro contadores da missão, CALCULADOS — nunca afirmados.

    Um contador que é escrito à mão como zero não mede nada: ele repete a intenção de
    quem escreveu. Estes são contados sobre os itens que acabaram de ser gravados.
    """
    sem_source_id = sum(1 for i in itens if not i.get('SOURCE_ID'))
    # A identidade de cada item tem de vir de campo que existia ANTES do texto. Se um
    # item carrega COMPANY/COUNTRY que não bate com o lote congelado, alguém inferiu.
    lote = paises_do_lote()
    papel_do_conteudo = sum(
        1 for i in itens
        if i.get('PAGE_ROLE') not in (NAO_SEI, None)
        and i.get('PAGE_ROLE') != (lote.get(i.get('ACCOUNT_HANDLE')) or {}).get('PAGE_ROLE'))
    entidade_do_conteudo = sum(
        1 for i in itens
        if i.get('ACCOUNT_HANDLE') and i['ACCOUNT_HANDLE'] not in lote)
    pais_do_conteudo = sum(
        1 for i in itens
        if i.get('COUNTRY') not in (NAO_SEI, None)
        and i['COUNTRY'] != (lote.get(i.get('ACCOUNT_HANDLE')) or {}).get('COUNTRY'))
    return {
        'IDENTITY_ERRORS': papel_do_conteudo + entidade_do_conteudo + pais_do_conteudo,
        'NEW_ENTITIES_FROM_CONTENT': entidade_do_conteudo,
        'ROLE_FROM_CONTENT': papel_do_conteudo,
        'DOCUMENT_WITHOUT_SOURCE_ID': sem_source_id,
        'COMO_FORAM_CONTADOS': (
            'comparando ACCOUNT_HANDLE, COUNTRY e PAGE_ROLE de cada documento contra o '
            'LOTE CONGELADO. Nenhum deles é lido do texto — e é exatamente isso que os '
            'contadores verificam.'),
    }


def _cabecalho(itens, contas, audio_s, maquina_s, modelo):
    cfg = asr_local.config(modelo=modelo)
    corpo = {
        'SOURCE_ID': 'YOUTUBE-TRANSCRICOES/TEXTO',
        'source': ('o texto de cada vídeo pela escada título → legenda → whisper local, '
                   'sem rota paga'),
        'SOURCE_LOCATION': ('youtube.com (título e legenda pública) + máquina local '
                            '(reconhecimento de fala)'),
        'FACT_LOCATION': 'NOT_KNOWN — o lugar do fato sai do conteúdo, nunca da conta',
        'ORIGINAL_LANGUAGE': 'multi',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'captured_at': hoje(), 'CAPTURED_AT': agora(),
        'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        'APIFY_RUNS': 0, 'COST_USD': 0, 'PAID_API_COST_USD': 0,
        'CUSTO_NAO_E_ZERO_ABSOLUTO': (
            'a fatura é zero dólar porque o reconhecimento roda nesta máquina. O custo '
            'REAL é tempo de máquina, e ele está medido abaixo em MACHINE_SECONDS_TOTAL. '
            'Chamar isso de "custo zero" seria esconder a única conta que existe.'),
        'A_ORDEM_QUE_ESTE_ARQUIVO_OBEDECE': (
            'título/metadados → legenda nativa → (legenda utilizável ⇒ o whisper NÃO '
            'roda) → (legenda falhou ⇒ registrar POR QUÊ e tentar o whisper) → (os dois '
            'falharam ⇒ permanecer NÃO SEI)'),
        'FALHA_DE_LEGENDA_NAO_E_AUSENCIA_DE_LEGENDA': (
            'NO_CAPTION_CONFIRMED é o único estado que afirma que o vídeo não tem '
            'legenda. CAPTION_ENVIRONMENT_FAILURE, CAPTION_FETCH_FAILURE, '
            'CAPTION_PARSE_FAILURE e CAPTION_DELIVERED_EMPTY são confissões sobre a '
            'minha rede ou sobre o meu leitor — e CAPTION_NOT_TESTED é ausência de '
            'pergunta, não ausência de resposta.'),
        'VOCABULARIO_DE_TEMPO': (
            'TRANSCRIPT_SEGMENTS usa START_S/END_S/TEXT, em SEGUNDOS, venha o texto da '
            'legenda ou do whisper. A legenda do YouTube chega em T_MS/DUR_MS (milissegundos '
            'e DURAÇÃO) e é traduzida na entrada.'),
        'ASR_ENGINE': cfg['ASR_ENGINE'], 'ASR_MODEL': cfg['ASR_MODEL'],
        'ASR_DEVICE': cfg['ASR_DEVICE'], 'ASR_COMPUTE_TYPE': cfg['ASR_COMPUTE_TYPE'],
        'ASR_BEAM': cfg['ASR_BEAM'], 'ASR_BATCH': cfg['ASR_BATCH'],
        'ASR_CPU_THREADS': cfg['ASR_CPU_THREADS'], 'ASR_VAD_FILTER': cfg['ASR_VAD_FILTER'],
        'OBJETOS_NA_ESCADA': len(itens),
        'TOTAL_AUDIO_MINUTES': round(audio_s / 60.0, 2),
        'TOTAL_MACHINE_SECONDS': round(maquina_s, 1),
        'REALTIME_FACTOR': round(audio_s / maquina_s, 2) if maquina_s else NAO_SEI,
    }
    corpo.update(contas)
    corpo['POR_ESTADO_DE_LEGENDA'] = _contar(itens, 'CAPTION_STATE')
    corpo['POR_ESTADO_DE_WHISPER'] = _contar(itens, 'WHISPER_STATE')
    corpo['POR_FONTE_DE_TEXTO'] = _contar(itens, 'TEXT_SOURCE')
    corpo['FORA_DO_LOTE_CONGELADO'] = sum(1 for i in itens if i.get('NO_LOTE_CONGELADO') is False)
    corpo['FORA_DO_LOTE_POR_QUE'] = (
        '`youtube_janela.contas()` casa qualquer registro com PLATFORM=YOUTUBE no lote '
        'inteiro, inclusive os de EXCLUDED_ACCOUNTS. Este arquivo não conserta a coleta '
        '— ele MOSTRA quanto do esforço caiu fora do lote, para quem manda decidir.')
    corpo.update(auditar_identidade(itens))
    corpo['ITEMS'] = itens
    return corpo


def _contar(itens, campo):
    fora = {}
    for i in itens:
        k = str(i.get(campo, NAO_SEI))
        fora[k] = fora.get(k, 0) + 1
    return dict(sorted(fora.items(), key=lambda kv: -kv[1]))


def _resumo(caminho, itens, contas, audio_s, maquina_s):
    print()
    print('gravado: %s · %d objetos' % (caminho, len(itens)))
    print('  CAPTION_HITS ....... %d  (legenda de graça, whisper não rodou)' % contas['CAPTION_HITS'])
    print('  WHISPER_FALLBACKS .. %d' % contas['WHISPER_FALLBACKS'])
    print('  WHISPER_SUCCESS .... %d' % contas['WHISPER_SUCCESS'])
    print('  WHISPER_FAILURES ... %d' % contas['WHISPER_FAILURES'])
    print('  CACHE_HITS ......... %d' % contas['CACHE_HITS'])
    # TITLE_ONLY como FONTE DE TEXTO é outra coisa, e maior: um vídeo cuja legenda
    # falhou E cujo áudio não veio também termina só com título. Quem quiser esse
    # número lê POR_FONTE_DE_TEXTO, que conta os dois casos.
    print('  CAPTION_NOT_TESTED . %d  (a legenda nem foi perguntada — whisper não roda)'
          % contas['CAPTION_NOT_TESTED'])
    print('  TOTAL_AUDIO_MINUTES  %.2f' % (audio_s / 60.0))
    print('  TOTAL_MACHINE_SECONDS %.1f' % maquina_s)
    print('  PAID_API_COST_USD ... 0 — e tempo de máquina NÃO é zero')
    a = auditar_identidade(itens)
    for k in ('IDENTITY_ERRORS', 'NEW_ENTITIES_FROM_CONTENT', 'ROLE_FROM_CONTENT',
              'DOCUMENT_WITHOUT_SOURCE_ID'):
        print('  %-26s %d' % (k, a[k]))


# ═══════════════════════════════════════════════════════════════════ AS OUTRAS FASES

def fase_estado():
    ok, motivo = asr_local.disponivel()
    print('WHISPER_ENGINE_ALREADY_EXISTS . SIM — scripts/instagram_transcrever.py, medido')
    print('FASTER_WHISPER_IMPORTABLE ..... %s' % ('SIM' if ok else 'NÃO'))
    print('  %s' % motivo)
    print('SINTONIA_LIBS ................. %s' % LIBS)
    try:
        r = subprocess.run([sys.executable, '-m', 'yt_dlp', '--version'],
                           capture_output=True, text=True, timeout=60,
                           env=_ambiente_filho())
        print('YT_DLP ........................ %s'
              % (r.stdout.strip() if r.returncode == 0 else 'AUSENTE'))
    except Exception as e:                                     # noqa: BLE001
        print('YT_DLP ........................ AUSENTE (%s)' % type(e).__name__)
    print('FFMPEG_NECESSARIO ............. NÃO — o PyAV do faster-whisper decodifica')
    for nome, caminho in (('OBJETOS.json', os.path.join(JANELA, 'OBJETOS.json')),
                          ('LEGENDAS.json', os.path.join(JANELA, 'LEGENDAS.json')),
                          ('FILA-WHISPER.json', os.path.join(RELEVANCIA, 'FILA-WHISPER.json')),
                          ('TEXTO.json', os.path.join(SAIDA, 'TEXTO.json')),
                          ('ASR-CACHE.json', os.path.join(SAIDA, 'ASR-CACHE.json'))):
        d = _ler_json(caminho)
        print('%-30s %s' % (nome, ('%d itens' % len(d.get('ITEMS') or [])) if d else 'AUSENTE'))
    return 0 if ok else 1


def fase_alvos():
    """A fila do portão de relevância, de graça. Ela ORDENA; ela não é a escada."""
    fila = _ler_json(os.path.join(RELEVANCIA, 'FILA-WHISPER.json'))
    if not fila:
        print('sem FILA-WHISPER.json — rode `py scripts/youtube_relevancia.py tudo`')
        return 1
    itens = fila.get('QUEUE') or []
    print('universo lido pelo portão .......... %s' % fila.get('UNIVERSO'))
    print('recusados .......................... %s' % fila.get('RECUSADOS'))
    for m, c in (fila.get('MOTIVOS_DE_RECUSA') or {}).items():
        print('    %-32s %s' % (m, c))
    print('na fila ............................ %d' % len(itens))
    print('qual critério realmente filtra ..... %s' % fila.get('QUAL_CRITERIO_REALMENTE_FILTRA'))
    for i in itens[:25]:
        print('  %-13s %5s s  %-24s %s' % (i['VIDEO_ID'], i.get('DURATION_S'),
                                           str(i.get('ACCOUNT_HANDLE'))[:24],
                                           str(i.get('TITLE'))[:40]))
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'alvos'
    if cmd == 'estado':
        raise SystemExit(fase_estado())
    if cmd == 'alvos':
        raise SystemExit(fase_alvos())
    if cmd in ('escada', 'rodar'):
        # `rodar [modelo] [teto]` é o nome antigo, e o workflow desta casa o usa.
        resto = sys.argv[2:]
        ids = None
        modelo, teto = None, None
        for a in resto:
            if a.startswith('ids:'):
                ids = a[4:].split(',')
            elif a.isdigit():
                teto = a
            elif a:
                modelo = a
        raise SystemExit(escada(ids=ids, teto=teto, modelo=modelo,
                                so_da_fila=(cmd == 'rodar')))
    print('uso: youtube_transcrever.py {estado|alvos|escada [modelo] [teto|ids:V1,V2]|rodar}')
    raise SystemExit(2)
