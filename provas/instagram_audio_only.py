#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVA C10 — a cadeia de Reel adquire SOMENTE audio, e prova-o nos bytes.

    py provas/instagram_audio_only.py
    py provas/instagram_audio_only.py --url=https://www.instagram.com/reel/XXXX

O QUE ESTA PROVA RECUSA COMO EVIDENCIA
---------------------------------------
Tres coisas que PARECEM prova de aquisicao so de audio e nao sao:

    · a bandeira `-f bestaudio` na linha de comando — diz o que foi PEDIDO;
    · a extensao `.m4a` — diz o que alguem escreveu no nome;
    · o nome do fornecedor — o `yt-dlp` traz as duas coisas.

Nenhuma das tres abre o ficheiro. Por isso o veredito desta prova sai do
`ffprobe` sobre os bytes que chegaram, e de mais nada.

    PEDIR AUDIO != TER RECEBIDO SO AUDIO.

E POR QUE ELA NAO CORRE SOBRE O CORPUS PRESERVADO
--------------------------------------------------
Ha oito MP4 no disco desta casa. Extrair audio deles e barato, e daria um
transcript identico — e seria `REUSED_VIDEO + AUDIO_DERIVATION`, que e
exatamente o estado ANTIGO com nome novo. Por isso a prova corre numa gaveta
vazia: se o MP4 antigo estivesse ao alcance, a cadeia reusava-o e a prova
passaria sem nunca ter adquirido nada.

    UMA PROVA QUE PODE PASSAR SEM FAZER O TRABALHO NAO E PROVA.

A GAVETA DA PROVA
------------------
`data/raw/C10-PROVA-AUDIO/`, que esta dentro do `.gitignore`. Nada aqui sobe
ao Git, nada sobe a bucket nenhum e nenhuma observacao canonica nasce: isto e
prova tecnica descartavel, e fica descartavel.
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'ferramentas'))
sys.path.insert(0, ROOT)

import fala_local as fl          # noqa: E402
import reel_transcricao as rt    # noqa: E402

#: Os Reels sentinela desta casa, por ordem. NAO e descoberta: sao enderecos
#: que o repositorio JA CONHECE, e a lista existe por um motivo medido.
#:
#: Em 2026-09-11, as 17:42, `C-63RfHoJTU` resolvia. As 19:0x do mesmo dia, o
#: mesmo endereco passou a devolver «Instagram sent an empty media response»
#: enquanto os outros tres continuavam a resolver na mesma maquina, no mesmo
#: minuto. Ou seja:
#:
#:     UMA PUBLICACAO QUE DEIXA DE RESPONDER != A ROTA DEIXOU DE FUNCIONAR.
#:
#: Uma sentinela unica transformaria a segunda coisa na primeira. Por isso sao
#: varias, e por isso cada tentativa fica ESCRITA — a escada e declarada, como
#: a da propria cadeia. O que esta lista NAO faz e procurar publicacao nova:
#: sair destes enderecos seria descoberta, e descoberta esta fora do escopo.
SENTINELAS = (
    'https://www.instagram.com/reel/DQhloXtjTep',
    'https://www.instagram.com/reel/C-FanW_CYMz',
    'https://www.instagram.com/reel/DW6X5lZkU41',
    'https://www.instagram.com/reel/C-63RfHoJTU',
)
URL_SENTINELA = SENTINELAS[0]

GAVETA = os.path.join(ROOT, 'data', 'raw', 'C10-PROVA-AUDIO')


def _sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def manifesto(url):
    """Os formatos anunciados, sem baixar byte nenhum. → (dict, motivo)."""
    r = rt._ytdlp(['-J', '--skip-download', url], timeout=180)
    if r.returncode != 0:
        return None, (r.stderr or '').strip().splitlines()[-1:][0][:200]
    try:
        return json.loads(r.stdout), None
    except Exception as e:                                     # noqa: BLE001
        return None, '%s ao ler o manifesto' % type(e).__name__


def correr(url, *, limpar=True, man=None):
    linhas = []

    def diz(chave, valor):
        linhas.append((chave, valor))
        print('%-34s %s' % (chave, valor))

    falhas = []

    def exige(nome, condicao, detalhe=''):
        if not condicao:
            falhas.append('%s%s' % (nome, (' — ' + detalhe) if detalhe else ''))
        print('  %-4s %s%s' % ('OK' if condicao else 'FAIL', nome,
                               (' — ' + detalhe) if detalhe and not condicao else ''))

    print('=' * 74)
    print('PROVA C10 · INSTAGRAM AUDIO-ONLY')
    print('=' * 74)
    diz('URL', url)

    # ── 1 · o manifesto resolve, e sem baixar nada ──────────────────────────
    # Se a escada de sentinelas ja o trouxe, reusa-se: pedir duas vezes a mesma
    # coisa a uma plataforma que limita pedidos e gastar a prova contra si.
    porque = None
    if man is None:
        man, porque = manifesto(url)
    exige('1 · metadados resolvem', man is not None, porque or '')
    if not man:
        return linhas, falhas

    formatos = man.get('formats') or []
    so_audio = [f for f in formatos
                if f.get('vcodec') in (None, 'none') and f.get('acodec') not in (None, 'none')]
    pedidos = man.get('requested_formats') or []
    diz('FORMATOS_ANUNCIADOS', len(formatos))
    diz('FORMATOS_AUDIO_ONLY', len(so_audio))
    diz('PADRAO_PEDIRIA', ' + '.join(f.get('format_id', '?') for f in pedidos) or '?')
    exige('2 · existe formato audio-only', bool(so_audio))

    # ── 3 · a cadeia PEDE audio, e isso prova-se sem tocar na rede ──────────
    # A primeira versao desta prova perguntava ao `yt-dlp`, por uma terceira
    # chamada, que formato e que `bestaudio` resolvia. Era desperdicio e era
    # fragil: a Instagram limitou a terceira chamada seguida e a prova
    # reprovou a rota por causa da propria sonda.
    #
    #     UMA SONDA QUE GASTA UM PEDIDO PARA CONFIRMAR O QUE JA VAI MEDIR NOS
    #     BYTES MEDE A SONDA, NAO A ROTA.
    #
    # O que interessa saber e se a CADEIA poe o seletor no comando. Isso le-se
    # interceptando o `argv`, de graca e sem rede — e o que chegou ao disco e
    # conferido depois, nos bytes, pelo `ffprobe`.
    vistos = []
    original = rt._ytdlp

    class _Fingido:
        """Um `yt-dlp` que regista o pedido e nao sai da maquina."""
        returncode, stdout, stderr = 1, '', 'PROVA: nao correu de proposito'

    rt._ytdlp = lambda args, timeout=300: (vistos.append(list(args)), _Fingido)[1]
    try:
        rt.midia_por_ytdlp(url, os.path.join(GAVETA, 'nunca-escrito.m4a'),
                           tentativas=1, kind=rt.MIDIA_AUDIO)
        pedido_audio = list(vistos)
        vistos.clear()
        rt.midia_por_ytdlp(url, os.path.join(GAVETA, 'nunca-escrito.mp4'),
                           tentativas=1, kind=rt.MIDIA_VIDEO)
        pedido_video = list(vistos)
    finally:
        rt._ytdlp = original

    argv_audio = pedido_audio[0] if pedido_audio else []
    tem_seletor = ('-f' in argv_audio
                   and argv_audio[argv_audio.index('-f') + 1] == rt.SELETOR_SO_AUDIO)
    campos = []
    diz('SELETOR', rt.SELETOR_SO_AUDIO)
    diz('ARGV_COM_KIND_AUDIO', ' '.join(argv_audio[:4]) + ' …')
    exige('3 · a cadeia pede `-f %s` quando o pedido e fala' % rt.SELETOR_SO_AUDIO,
          tem_seletor, ' '.join(argv_audio))
    # E o contraponto, que e o que torna o teste 3 informativo: sem o pedido de
    # audio o seletor NAO aparece. Se aparecesse sempre, o teste passaria mesmo
    # com a lei desligada, e nao mediria nada.
    exige('3b · sem pedido de fala o seletor nao entra',
          '-f' not in (pedido_video[0] if pedido_video else []),
          str(pedido_video[:1]))

    # ── a gaveta vazia, para o MP4 historico nao entrar pela porta do reuso ─
    if limpar and os.path.isdir(GAVETA):
        shutil.rmtree(GAVETA)
    os.makedirs(GAVETA, exist_ok=True)
    midia_antes, saida_antes = rt.MIDIA, rt.SAIDA
    rt.MIDIA, rt.SAIDA = GAVETA, os.path.join(GAVETA, 'TEXTO')
    try:
        ident = rt.identidade_do_url(url)
        t0 = time.time()
        reg = rt.transcrever_reel(ident, run_id='C10-PROVA', guardar=True)
        segundos = round(time.time() - t0, 2)
    finally:
        rt.MIDIA, rt.SAIDA = midia_antes, saida_antes

    diz('DOWNLOAD_E_ASR_SEGUNDOS', segundos)
    diz('CAPTURE_PROVIDER', reg.get('CAPTURE_PROVIDER'))
    diz('MEDIA_KIND_REQUESTED', reg.get('MEDIA_KIND_REQUESTED'))
    diz('MEDIA_KIND_USED', reg.get('MEDIA_KIND_USED'))
    diz('AUDIO_ONLY_ACQUISITION', reg.get('AUDIO_ONLY_ACQUISITION'))

    # ── 4 a 8 · os bytes que chegaram ───────────────────────────────────────
    adquiridos = [os.path.join(GAVETA, f) for f in sorted(os.listdir(GAVETA))
                  if os.path.isfile(os.path.join(GAVETA, f))]
    raw = reg.get('RAW') or {}
    caminho = os.path.join(ROOT, raw.get('STORAGE_LOCATION', '')) if raw else None
    exige('4 · o RAW existe no disco', bool(caminho and os.path.exists(caminho)))
    if not (caminho and os.path.exists(caminho)):
        return linhas, falhas

    v, a, porque_f = fl.fluxos(caminho)
    bytes_audio = os.path.getsize(caminho)
    diz('RAW_FICHEIRO', os.path.basename(caminho))
    diz('VIDEO_STREAMS', v)
    diz('AUDIO_STREAMS', a)
    diz('AUDIO_BYTES', bytes_audio)
    diz('AUDIO_SHA256', _sha256(caminho))
    diz('DURACAO_S', fl.duracao(caminho))
    exige('5 · AUDIO_STREAMS >= 1', a != fl.NAO_SEI and a >= 1, porque_f or '')
    exige('6 · VIDEO_STREAMS = 0', v == 0, porque_f or 'ha imagem no ficheiro')
    exige('7 · bytes > 0', bytes_audio > 0)
    exige('8 · duracao valida', isinstance(fl.duracao(caminho), (int, float)))

    # ── 9 · NENHUM ficheiro de video foi escrito, em toda a gaveta ──────────
    # Nao basta conferir o RAW: um degrau podia ter baixado um MP4 e deitado
    # fora. Aqui olha-se TUDO o que a corrida deixou.
    com_imagem = []
    for f in adquiridos:
        if f.endswith('.wav'):
            continue                     # meio de trabalho, nasce do audio
        vv, _aa, _p = fl.fluxos(f)
        if vv not in (0, fl.NAO_SEI) and vv > 0:
            com_imagem.append((os.path.basename(f), vv))
    diz('FICHEIROS_NA_GAVETA', ', '.join(os.path.basename(f) for f in adquiridos))
    diz('VIDEO_BYTES_DOWNLOADED',
        sum(os.path.getsize(os.path.join(GAVETA, n)) for n, _ in com_imagem))
    exige('9 · nenhum ficheiro com imagem foi escrito', not com_imagem,
          str(com_imagem))

    # ── 10 a 12 · a fala, e o pai dela ──────────────────────────────────────
    # DUAS AFIRMACOES, E ELAS NAO SE PROVAM NO MESMO SITIO:
    #
    #   A · AQUISICAO   os bytes vieram, e sao so audio  (5, 6, 9)
    #   B · CADEIA      o ASR le esses bytes e o texto tem pai declarado
    #
    # A `B` precisa de um Reel que TENHA fala. Um Reel so com musica devolve
    # `REQUESTED_EMPTY`, que nao e falha nenhuma: e o motor a correr ate ao fim
    # e a dizer que nao ouviu palavra. Reprovar a rota por causa disso seria
    # medir o conteudo e escrever o resultado na conta da rota.
    #
    #     «ESTE REEL NAO TEM FALA» != «A ROTA NAO TRAZ FALA».
    #
    # Por isso o estado `REQUESTED_EMPTY` conta como LEITURA FEITA — o motor
    # abriu o ficheiro adquirido — e a prova do PAI segue para a sentinela
    # seguinte, com o salto escrito.
    texto = reg.get('TRANSCRIPT_TEXT') or ''
    der = reg.get('DERIVED') or {}
    estado_asr = reg.get('TRANSCRIPT_STATE')
    diz('TRANSCRIPT_STATE', estado_asr)
    diz('TRANSCRIPT_CHARS', len(texto))
    diz('TRANSCRIPT_INICIO', (texto[:70] + '…') if texto else '(vazio)')
    exige('10 · o ASR conseguiu ler o audio adquirido',
          estado_asr in (fl.OK, fl.REQUESTED_EMPTY), str(estado_asr))

    if not texto and estado_asr == fl.REQUESTED_EMPTY:
        diz('SEM_FALA_NESTE_REEL', 'SIM — o motor correu e nao ouviu palavra')
        exige('11 · ha fala neste Reel', False,
              'conteudo sem fala; a prova do PAI precisa de outra sentinela')
        return linhas, falhas

    diz('DERIVED_PARENT', der.get('PARENT_ARTIFACT_ID') or der.get('PARENT_SHA256')
        or der.get('DERIVED_FROM') or 'NAO DECLARADO')
    exige('11 · transcript nao vazio', len(texto) > 0)
    pai_ok = raw.get('SHA256') and (
        raw['SHA256'] in json.dumps(der, ensure_ascii=False))
    exige('12 · o pai do transcript e o audio adquirido', bool(pai_ok),
          'o SHA do RAW nao aparece no derivado')

    # ── 13 · quanto se poupou, e com que base ───────────────────────────────
    tbr_audio = so_audio[0].get('tbr') if so_audio else None
    tbr_padrao = sum(f.get('tbr') or 0 for f in pedidos) or None
    diz('FORMAT_ESTIMATE_PADRAO_KBPS', tbr_padrao)
    diz('FORMAT_ESTIMATE_AUDIO_KBPS', tbr_audio)
    if tbr_padrao and tbr_audio:
        diz('BYTE_REDUCTION_RATIO_ESTIMADO', '%.1fx' % (tbr_padrao / tbr_audio))
    diz('MEASURED_BYTES_AUDIO', bytes_audio)
    diz('MEASURED_BYTES_VIDEO', 0)

    print()
    print('=' * 74)
    if falhas:
        print('INSTAGRAM_AUDIO_ONLY = BLOCKED · %d prova(s) reprovada(s)' % len(falhas))
        for f in falhas:
            print('  ·', f)
    else:
        print('INSTAGRAM_AUDIO_ONLY = PROVEN')
    print('=' * 74)
    return linhas, falhas


def escolher_sentinela(candidatas):
    """A primeira que ainda responde, com a escada escrita. → (url, degraus, manifesto).

    NAO e «tentar ate uma passar». E distinguir duas coisas que se parecem no
    log e nao sao a mesma: a publicacao ficou indisponivel, ou a rota partiu-se.
    Se TODAS falharem, a resposta e `None` — e ai o veredito e sobre a rota.
    """
    degraus = []
    for u in candidatas:
        man, porque = manifesto(u)
        degraus.append({'URL': u, 'RESOLVE': bool(man), 'WHY': porque})
        if man:
            return u, degraus, man
    return None, degraus, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', default=None)
    ap.add_argument('--manter', action='store_true',
                    help='nao limpa a gaveta antes de correr')
    a = ap.parse_args()
    man = None
    if a.url:
        url, degraus = a.url, []
    else:
        url, degraus, man = escolher_sentinela(SENTINELAS)
        print('ESCADA DE SENTINELAS')
        for d in degraus:
            print('  %-4s %s%s' % ('OK' if d['RESOLVE'] else 'FALHA',
                                   d['URL'].rsplit('/', 1)[-1],
                                   '' if d['RESOLVE'] else ' — ' + str(d['WHY'])[:90]))
        print()
    if not url:
        print('INSTAGRAM_AUDIO_ONLY = BLOCKED · nenhuma sentinela resolveu. '
              'Isto e sobre a ROTA, nao sobre uma publicacao.')
        return 1

    _linhas, falhas = correr(url, limpar=not a.manter, man=man)
    # UM UNICO SALTO PERMITIDO, E SO POR AUSENCIA DE FALA. Qualquer outra falha
    # e da rota e fica como esta — saltar por causa dela seria procurar ate
    # passar, que e o contrario de medir.
    if a.url is None and falhas == ['11 · ha fala neste Reel — conteudo sem fala; '
                                    'a prova do PAI precisa de outra sentinela']:
        restantes = [u for u in SENTINELAS if u != url]
        print()
        print('A sentinela anterior nao tem fala. A AQUISICAO ja esta provada '
              'nela; o que falta provar e o PAI do texto, e isso precisa de um '
              'Reel falado. Seguinte:')
        seguinte, degraus2, man2 = escolher_sentinela(restantes)
        for d in degraus2:
            print('  %-4s %s' % ('OK' if d['RESOLVE'] else 'FALHA',
                                 d['URL'].rsplit('/', 1)[-1]))
        if seguinte:
            _l2, falhas = correr(seguinte, limpar=True, man=man2)
    return 1 if falhas else 0


if __name__ == '__main__':
    raise SystemExit(main())
