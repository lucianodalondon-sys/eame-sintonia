#!/usr/bin/env python3
"""
TRANSCRIÇÃO DOS VÍDEOS — a fala vira texto, aqui na máquina, sem pagar por minuto.

    py ferramentas/instagram_transcrever.py alvos          # GRÁTIS: o que seria transcrito
    py ferramentas/instagram_transcrever.py rodar          # transcreve o que falta
    py ferramentas/instagram_transcrever.py rodar base 20  # modelo e teto de objetos

POR QUE LOCAL, E NÃO PAGO
---------------------------
Medido nesta máquina em 2026-09-02, num reel real de 110 s da @basf_agroes, com os 16
núcleos e o modo em lote:

    modelo    velocidade      qualidade do texto
    tiny      18,7x           "Pirar Pascal", "agro-imfluencia" — inutilizável
    base       9,4x           "Pilar Pasqual", "ingeniero-agricula" — média
    small      3,2x           "Pilar Pascual", "ingeniero agrícola" — boa

`small` em lote leva ~6 horas para 1.000 vídeos (~19 h de áudio) e custa **zero dólar**.
A rota paga cobra por MINUTO — e há ator que cobra por minuto INICIADO, onde um reel de
61 s paga 2 minutos.

    O CUSTO DE TRANSCREVER AQUI É TEMPO DE MÁQUINA, NÃO FATURA.

DUAS COISAS QUE CUSTARAM MEDIÇÃO PARA DESCOBRIR
-------------------------------------------------
1. **Os núcleos não vêm de graça.** O padrão da biblioteca usa 4 threads. Nesta máquina de
   16, declarar `cpu_threads` deu ~4x. A primeira medição, sem isso, deu 0,3x — e 0,3x
   levaria 63 horas para os mesmos mil vídeos.
2. **`beam_size=5` custa o dobro e entrega o mesmo texto.** Medido: 1,16x contra 2,31x,
   com 2.079 e 2.054 caracteres praticamente idênticos. O padrão aqui é 1, de propósito.

A URL DO MP4 EXPIRA, E ISSO NÃO É "O VÍDEO SUMIU"
---------------------------------------------------
`VIDEO_URL_TEMPORARY` é assinada pela CDN da Meta e morre em horas. Quando ela morre, este
arquivo **relê o embed** (grátis) para pegar uma URL nova. O que ele NUNCA faz é registrar
o vídeo como ausente:

    URL EXPIRADA ≠ VÍDEO INEXISTENTE.

O QUE ESTE ARQUIVO NÃO FAZ
----------------------------
Não classifica assunto, não resume, não traduz, não decide se a fala é relevante. Ele
transcreve e preserva — inclusive os tempos de cada trecho, para que qualquer citação
futura possa ser conferida contra o segundo exato do vídeo.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
# O DONO DO RECONHECEDOR. Importado AQUI, ao nivel do modulo, porque a
# politica de modelo se le antes de qualquer funcao correr. `fala_local`
# so importa `os`, `re` e `time` no topo — a biblioteca pesada continua a
# entrar tarde, dentro das funcoes dele.
import fala_local as fl  # noqa: E402
import social_matriz as mz  # noqa: E402 — a política de rota, dono único

#: O ACTO QUE ESTE FICHEIRO EXECUTA, NA LÍNGUA DA MATRIZ.
#: O mesmo que a cadeia nova pergunta. Uma decisão, todas as portas.
CAPACIDADE_NA_MATRIZ = 'FETCH_TRANSCRIPT'
PLATAFORMA = 'INSTAGRAM'


def politica_da_aquisicao():
    """A lei responde ANTES de o socket abrir. Zero rede, zero custo.

    POR QUE ISTO ESTÁ AQUI, NUM FICHEIRO QUE NINGUÉM IMPORTA
    ----------------------------------------------------------
    A C10.4B mediu quem alcança esta implementação. Pelo pedido canônico —
    executor, roteador, portão, adaptador — NINGUÉM: a armadilha ficou muda nas
    seis entradas. Mas há uma porta que nenhum `import` mostra:

        .github/workflows/sintonia-scrap.yml
            fase=transcrever  ->  instagram_transcrever.py rodar

    É `workflow_dispatch`. Não é teste, não é histórico, não é comentário: é
    despacho de produção, e o ficheiro que ele corre baixa o MP4 INTEIRO da CDN
    da Meta e só depois deita a imagem fora.

        UMA PORTA QUE NENHUM IMPORT MOSTRA CONTINUA A SER UMA PORTA.

    E, até aqui, essa porta não perguntava nada a ninguém. A decisão humana da
    C10.5D — `INSTAGRAM_REMOTE_ACQUISITION = NOT_ALLOWED` — não a alcançava.

        UMA DECISÃO QUE UMA PORTA NÃO CONHECE NÃO É UMA DECISÃO. É UM DESEJO.

    Isto NÃO altera política nenhuma: lê a que já está escrita, no mesmo dono
    que a cadeia nova lê.
    """
    return mz.decisao(PLATAFORMA, CAPACIDADE_NA_MATRIZ)

# As bibliotecas pesadas vivem FORA do repositório. A memória desta casa registra o
# acidente: `pip` sem `--target` criou `C:\eame-sintonia\Scripts`, e apagar `Scripts`
# apagou `scripts` — no Windows os dois nomes são a MESMA pasta.
LIBS = os.environ.get('SINTONIA_LIBS') or os.path.join(
    os.path.expanduser('~'), '.sintonia-libs')
if os.path.isdir(LIBS):
    sys.path.insert(0, LIBS)

SAMPLES = os.path.join(ROOT, 'data', 'samples')
JANELA = os.path.join(SAMPLES, 'INSTAGRAM-JANELA')
SAIDA = os.path.join(SAMPLES, 'INSTAGRAM-TRANSCRICOES')
MEDIA = os.path.join(SAIDA, 'audio-cache')

MISSION = '14-COMUNICACAO-PUBLICA-DO-CONCORRENTE'
RUNNER = os.environ.get('RUNNER_NAME') or 'NOT_KNOWN'
NAO_SEI = 'NOT_KNOWN'

# A politica vive no dono; `IG_MODELO` continua a valer. Ver
# `fala_local.MODELOS_POR_CHAMADOR`.
MODELO_PADRAO = fl.modelo_de('instagram')
# Medido: 5 custa o dobro do tempo e devolve o mesmo texto.
BEAM = int(os.environ.get('IG_BEAM') or 1)
# Medido com aquecimento e 3 repetições: sequencial 2,49x · lote 8 → 4,13x · lote 16 → 4,03x.
# O lote dá 1,66x de graça, e 16 não é melhor que 8.
LOTE = int(os.environ.get('IG_LOTE') or 8)

# ── O IDIOMA É DECLARADO, NUNCA DETECTADO POR VÍDEO ─────────────────────────────
# Três segundos de abertura com música fazem o detector escolher errado, e o resto do
# vídeo sai lixo — em silêncio, com o texto parecendo normal. Medido nesta casa: dois
# reels voltaram `en` com confiança 0,37, sendo espanhóis.
#
#     IDIOMA ADIVINHADO POR VÍDEO É UM ERRO QUE NÃO AVISA.
#
# O país da CONTA é conhecido desde o lote congelado. Usar isso não é suposição — é
# usar o que já foi provado de graça na fase de identidade.
IDIOMA_DO_PAIS = {'ES': 'es', 'IT': 'it', 'FR': 'fr', 'PT': 'pt', 'BR': 'pt'}

# Teto de tempo por vídeo. Áudio repetitivo faz o decodificador entrar em laço e um lote
# noturno morre sem ninguém saber. 6x a duração é folga larga sobre os ~4x medidos.
TETO_FATOR = 6
TETO_MINIMO_S = 120


def agora():
    import datetime
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _ler(pasta, nome):
    p = os.path.join(pasta, nome)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def _gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    with open(os.path.join(SAIDA, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return 'data/samples/INSTAGRAM-TRANSCRICOES/' + nome


# ─────────────────────────────────────────────────────────────── quem entra na fila
def alvos():
    """Os vídeos que valem transcrever, e o motivo de cada exclusão. Custo zero.

    Excluir em silêncio é o defeito clássico: quem lê o artefato depois não sabe se o
    objeto não tinha fala ou se ninguém tentou.
    """
    objs = _ler(JANELA, 'OBJETOS.json')
    if not objs:
        print('sem OBJETOS.json — rode `py coleta/instagram_janela.py tudo` antes')
        return None, []
    dentro, fora = [], []
    for o in objs['ITEMS']:
        if o.get('IS_VIDEO') != 'YES':
            fora.append((o, 'NAO_E_VIDEO'))
            continue
        # Reel com música de catálogo costuma não ter fala: transcrever devolveria a letra
        # da música ou silêncio. Não é regra de ouro, é sinal — e por isso o objeto sai
        # marcado, não descartado.
        audio = str(o.get('AUDIO_NAME') or '')
        if audio and audio != NAO_SEI and 'riginal' not in audio:
            fora.append((o, 'AUDIO_DE_CATALOGO:%s' % audio[:30]))
            continue
        if o.get('VIDEO_URL_TEMPORARY') in (None, NAO_SEI):
            fora.append((o, 'SEM_URL_DE_VIDEO'))
            continue
        dentro.append(o)
    return objs, (dentro, fora)


def fase_alvos():
    objs, par = alvos()
    if not objs:
        return 1
    dentro, fora = par
    dur = sum(o['VIDEO_DURATION_S'] for o in dentro
              if isinstance(o.get('VIDEO_DURATION_S'), (int, float)))
    print('objetos no acervo : %d' % len(objs['ITEMS']))
    print('entram na fila    : %d  (%.1f min de áudio)' % (len(dentro), dur / 60))
    print('ficam de fora     : %d' % len(fora))
    from collections import Counter
    for motivo, n in Counter(m.split(':')[0] for _o, m in fora).most_common():
        print('    %-22s %d' % (motivo, n))
    print()
    for v in ('small', 'base', 'tiny'):
        x = {'small': 3.21, 'base': 9.36, 'tiny': 18.68}[v]
        print('  com `%-5s` em lote (%.2fx medido aqui): %.1f min de máquina'
              % (v, x, dur / x / 60))
    print()
    print('custo em dólar: 0,00 — o custo é tempo de máquina ligada.')
    return 0


# ─────────────────────────────────────────────────────────────────────── o trabalho
def _baixar(url, destino):
    # O PORTÃO, ANTES DO SOCKET. Mesma pergunta, mesmo dono, mesma resposta.
    decisao = politica_da_aquisicao()
    if decisao['DECISAO'] != mz.PERMITIDA_SIM:
        raise PermissionError('%s: %s' % (decisao['DECISAO'], decisao['PORQUE']))
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(destino, 'wb') as f:
        f.write(r.read())
    return os.path.getsize(destino)


def _url_nova(shortcode):
    """Relê o embed para pegar uma URL de MP4 viva. Grátis, e é o conserto do vencimento.

    GRÁTIS NÃO É PERMITIDO. Abrir o embed é tocar a plataforma — sobe navegador,
    gasta pedido e aparece no log do host. O portão vem antes.
    """
    decisao = politica_da_aquisicao()
    if decisao['DECISAO'] != mz.PERMITIDA_SIM:
        raise PermissionError('%s: %s' % (decisao['DECISAO'], decisao['PORQUE']))
    import cdp
    import instagram_janela as ij
    try:
        cdp.subir(ij.PORTA, perfil=ij.PERFIL)
        aba, _h = cdp.abrir('https://www.instagram.com/p/%s/embed/captioned/' % shortcode,
                            porta=ij.PORTA, espera=4)
        try:
            e = aba.js(ij.JS_EMBED) or {}
            return e.get('VIDEO_URL')
        finally:
            aba.fechar()
    except Exception:                                        # noqa: BLE001
        return None


def _audio(shortcode, url):
    """MP4 → WAV 16 kHz mono. → (caminho, motivo_da_falha)."""
    os.makedirs(MEDIA, exist_ok=True)
    wav = os.path.join(MEDIA, '%s.wav' % shortcode)
    if os.path.exists(wav) and os.path.getsize(wav) > 1000:
        return wav, None
    mp4 = os.path.join(MEDIA, '%s.mp4' % shortcode)
    if not (os.path.exists(mp4) and os.path.getsize(mp4) > 10000):
        try:
            _baixar(url, mp4)
        except Exception as e:                               # noqa: BLE001
            # A URL assinada morreu. Reler o embed é grátis e resolve.
            nova = _url_nova(shortcode)
            if not nova:
                return None, ('URL_EXPIRADA_E_NAO_RENOVOU: %s. Isto NÃO é vídeo '
                              'inexistente — é endereço vencido.' % type(e).__name__)
            try:
                _baixar(nova, mp4)
            except Exception as e2:                          # noqa: BLE001
                return None, 'DOWNLOAD_FALHOU: %s' % type(e2).__name__
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp4, '-vn', '-ac', '1',
                        '-ar', '16000', '-c:a', 'pcm_s16le', wav],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(wav):
        return None, 'FFMPEG_FALHOU: %s' % (r.stderr or '')[:120]
    return wav, None


def fase_rodar(modelo=None, teto=None):
    modelo = modelo or MODELO_PADRAO
    objs, par = alvos()
    if not objs:
        return 1
    dentro, fora = par
    if teto:
        dentro = dentro[:int(teto)]

    # O RECONHECEDOR NÃO VIVE MAIS AQUI. Ele foi para `ferramentas/fala_local.py`,
    # que é agora o dono único — este ficheiro e o do YouTube tinham a MESMA lógica
    # copiada, e duas cópias da mesma lei são duas leis. Os parâmetros medidos aqui
    # em 2026-09-02 foram para lá inteiros, com a medição junto.
    ha, porque = fl.disponivel()
    if not ha:
        print(porque)
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

    # Retomar de onde parou: transcrição é cara em TEMPO, e refazer o que já está pronto
    # é o mesmo desperdício que pagar duas vezes por um item.
    feito = {}
    antigo = _ler(SAIDA, 'TRANSCRICOES.json')
    if antigo:
        feito = {i['OBJECT_ID']: i for i in antigo.get('ITEMS', [])
                 if i.get('TRANSCRIPT_STATE') == 'OK'}
        print('já transcritos antes: %d (serão preservados)' % len(feito))

    itens, seg_audio, seg_maquina = [], 0.0, 0.0
    for n, o in enumerate(dentro, 1):
        sc = o['SHORTCODE']
        if sc in feito:
            itens.append(feito[sc])
            continue
        wav, motivo = _audio(sc, o['VIDEO_URL_TEMPORARY'])
        base = {
            'OBJECT_ID': sc, 'SHORTCODE': sc,
            'ACCOUNT_HANDLE': o.get('ACCOUNT_HANDLE'),
            'COMPANY': o.get('COMPANY'), 'COUNTRY_SCOPE': o.get('COUNTRY_SCOPE'),
            'SOURCE_URL': o.get('SOURCE_URL'),
            'PUBLISHED_AT': o.get('PUBLISHED_AT', NAO_SEI),
            'VIDEO_DURATION_S': o.get('VIDEO_DURATION_S', NAO_SEI),
            'AUDIO_NAME': o.get('AUDIO_NAME', NAO_SEI),
            'ASR_ENGINE': 'faster-whisper',
            'ASR_MODEL': modelo, 'ASR_BEAM': BEAM, 'ASR_BATCH': LOTE,
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
        if not wav:
            itens.append(dict(base, **{
                'TRANSCRIPT': None, 'TRANSCRIPT_STATE': 'AUDIO_NAO_OBTIDO',
                'WHY': motivo,
                'NAO_SIGNIFICA': 'que o vídeo não tem fala. Significa que eu não ouvi.'}))
            print('  %3d/%d %-13s SEM ÁUDIO — %s' % (n, len(dentro), sc, str(motivo)[:60]))
            continue

        # O idioma vem do PAÍS DA CONTA, provado de graça na fase de identidade.
        idioma = IDIOMA_DO_PAIS.get(str(o.get('COUNTRY_SCOPE') or '').upper())
        # O TETO DE TEMPO tambem mudou de dono: `fala_local` calcula-o a partir da
        # duracao, com os mesmos 6x e os mesmos 120 s de piso medidos aqui.
        dur = o.get('VIDEO_DURATION_S')
        r = fl.transcrever(wav, idioma=idioma, modelo_nome=modelo,
                           duracao_s=dur if isinstance(dur, (int, float)) else None)
        if r['TRANSCRIPT_STATE'] in (fl.ASR_FALHOU, fl.ASR_INDISPONIVEL):
            # A QUEDA TAMBEM TEM FICHA, e ela vem do reconhecedor — nao da base.
            # Antes este ramo guardava `base` intacta e deitava fora o trace de
            # `r`: perdia-se qual ferro tinha sido escolhido justamente no caso
            # em que essa e a pergunta.
            #
            #     QUEM FALHA E QUEM MAIS PRECISA DE DIZER ONDE ESTAVA.
            itens.append(dict(base, **{
                'TRANSCRIPT': None, 'TRANSCRIPT_STATE': r['TRANSCRIPT_STATE'],
                'ASR_DEVICE': r.get('ASR_DEVICE', fl.NAO_SEI),
                'ASR_DEVICE_SELECTED': r.get('ASR_DEVICE_SELECTED', fl.NAO_SEI),
                'ASR_DEVICE_EXECUTION': r.get('ASR_DEVICE_EXECUTION',
                                              fl.EXECUCAO_NAO_CORREU),
                'ASR_WHY_FALLBACK': r.get('ASR_WHY_FALLBACK'),
                'WHY': r.get('ERROR', ''),
                'NAO_SIGNIFICA': r.get('NAO_SIGNIFICA', '')}))
            print('  %3d/%d %-13s ASR FALHOU' % (n, len(dentro), sc))
            continue
        if r['TRANSCRIPT_STATE'] == fl.TRANSCRIPTION_TIMEOUT:
            itens.append(dict(base, **{k: r[k] for k in r if k != 'SEGMENTS'}))
            print('  %3d/%d %-13s ESTOUROU O TETO (%ss > %ss)'
                  % (n, len(dentro), sc, r.get('MACHINE_SECONDS'),
                     r.get('TIMEOUT_LIMIT_S')))
            continue
        if isinstance(r.get('AUDIO_SECONDS'), (int, float)):
            seg_audio += r['AUDIO_SECONDS']
        if isinstance(r.get('MACHINE_SECONDS'), (int, float)):
            seg_maquina += r['MACHINE_SECONDS']
        itens.append(dict(base, **r))
        texto = r.get('TRANSCRIPT')
        print('  %3d/%d %-13s %-3s %-5s  %5ss áudio em %5ss  %s'
              % (n, len(dentro), sc, r.get('LANGUAGE_DETECTED'),
                 r.get('LANGUAGE_CONFIDENCE'), r.get('AUDIO_SECONDS'),
                 r.get('MACHINE_SECONDS'),
                 (texto[:42] + '…') if texto else '(nao saiu texto)'))

    com = sum(1 for i in itens if i.get('TRANSCRIPT_STATE') == 'OK')
    caminho = _gravar('TRANSCRICOES.json', {
        'SOURCE_ID': 'INSTAGRAM-TRANSCRICOES/TRANSCRICOES',
        'source': 'reconhecimento de fala LOCAL sobre o áudio dos vídeos públicos',
        'SOURCE_LOCATION': 'Instagram (vídeo) + máquina local (reconhecimento)',
        'FACT_LOCATION': 'NOT_KNOWN — o lugar do fato sai do conteúdo, nunca da conta',
        'EVIDENCE_CLASS': 'COMPETITOR_PUBLIC_COMMUNICATION_OBSERVED',
        'CAPTURED_AT': agora(), 'MISSION': MISSION, 'RUNNER_NAME': RUNNER,
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'COST_NOTE': ('custo em dólar é zero: o reconhecimento roda nesta máquina. '
                      'O custo real é TEMPO DE MÁQUINA, e está medido abaixo.'),
        **fl.carimbo(modelo, ferro),
        'OBJECTS_IN_QUEUE': len(dentro),
        'OBJECTS_EXCLUDED': len(fora),
        'EXCLUSION_REASONS': sorted({m.split(':')[0] for _o, m in fora}),
        'TRANSCRIBED_OK': com,
        'AUDIO_SECONDS_TOTAL': round(seg_audio, 1),
        'MACHINE_SECONDS_TOTAL': round(seg_maquina, 1),
        'REALTIME_FACTOR': round(seg_audio / seg_maquina, 2) if seg_maquina else NAO_SEI,
        'LEI': ('transcrição vazia é REQUESTED_EMPTY, um estado — nunca "o vídeo não tem '
                'conteúdo". E áudio não obtido é AUDIO_NAO_OBTIDO, nunca ausência de fala.'),
        'ITEMS': itens})
    print()
    print('gravado: %s' % caminho)
    print('  transcritos=%d/%d · %.1f min de áudio em %.1f min de máquina (%.2fx)'
          % (com, len(dentro), seg_audio / 60, seg_maquina / 60,
             seg_audio / seg_maquina if seg_maquina else 0))
    print('  custo=0,00 USD')
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'alvos'
    if cmd == 'alvos':
        raise SystemExit(fase_alvos())
    if cmd == 'rodar':
        raise SystemExit(fase_rodar(sys.argv[2] if len(sys.argv) > 2 else None,
                                    sys.argv[3] if len(sys.argv) > 3 else None))
    print('uso: instagram_transcrever.py {alvos|rodar [modelo] [teto]}')
    raise SystemExit(2)
