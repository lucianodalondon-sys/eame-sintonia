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
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

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

MODELO_PADRAO = os.environ.get('YT_MODELO') or 'small'
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
    """→ (caminho_wav, motivo). O `yt-dlp` negocia a faixa; o `ffmpeg` corta o resto."""
    os.makedirs(MEDIA, exist_ok=True)
    wav = os.path.join(MEDIA, video_id + '.wav')
    if os.path.exists(wav) and os.path.getsize(wav) > 1000:
        return wav, 'CACHE'
    url = 'https://www.youtube.com/watch?v=' + video_id
    try:
        r = subprocess.run(
            [sys.executable, '-m', 'yt_dlp', '-q', '--no-warnings',
             '-f', 'bestaudio/best', '-x', '--audio-format', 'wav',
             '--postprocessor-args', '-ac 1 -ar 16000',
             '-o', os.path.join(MEDIA, '%(id)s.%(ext)s'), url],
            capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return None, 'YT_DLP_ESTOUROU_O_TEMPO'
    if os.path.exists(wav) and os.path.getsize(wav) > 1000:
        return wav, 'BAIXADO'
    erro = (r.stderr or r.stdout or '').strip().splitlines()
    return None, ('YT_DLP_NAO_ENTREGOU: %s' % (erro[-1][:150] if erro else 'sem mensagem'))


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
    import fala_local as fl
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
            'ASR_DEVICE': 'cpu/int8/%d threads' % nucleos,
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
            saida.append(dict(base, **{
                'TRANSCRIPT': None, 'TRANSCRIPT_STATE': r['TRANSCRIPT_STATE'],
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
