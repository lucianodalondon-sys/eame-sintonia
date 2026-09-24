#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D24 · O VIDEO PUBLICO DE UM AGRONOMO ITALIANO NO YOUTUBE — o canario real.

    python provas/canario_d24_video_youtube_de_pessoa.py

⚠️ CORRER COM `python` (que tem `yt-dlp` instalado), e nao com `py`.
   O `_audio()` do dono do YouTube chama `sys.executable -m yt_dlp`: correr com
   um interpretador sem a biblioteca devolve `YT_DLP_NAO_ENTREGOU` e parece uma
   falha da rota quando e' so' do ambiente.

O QUE ESTE CANARIO ACRESCENTA

A D24 autorizou o VIDEO de PESSOAS do agro em qualquer plataforma ja' coberta
pela matriz. O que faltava era a metade ITALIANA: a doc do D24 ficou com
`ITALIANO = NAO ENCONTRADO NA AMOSTRA` (4 posts de pessoa italiana medidos, 0
com video). Este canario mede um agronomo italiano numa SEGUNDA plataforma.

    A PESSOA E' A MESMA do canario do Reel (`dr.agricultura`), e isso e'
    deliberado: a mesma pessoa provada em duas plataformas mede a MATRIZ, e nao
    so' mais um video.

O QUE ELE NAO FAZ, E DIZ-SE EM VOZ ALTA

A rota do YouTube declarada na matriz e' `yt-dlp:public_audio` com
`LIMITE = PUBLIC_AUDIO_ONLY` (D17.4/C13). O que este canario adquire sao os
BYTES DE SOM da publicacao publica — com o VIDEO preservado como PAI
(`PARENT.VIDEO_ID`). `VIDEO_BYTES = NOT_RUN`: nao existe rota declarada na
matriz para os bytes de imagem do YouTube, e inventar uma seria abrir capability
nova dentro de uma missao de fecho.

Nao usa conta, login, cookie de sessao, navegador logado, CAPTCHA, token de
sessao nem rota paga. Nao toca no perfil: o alvo e' a PUBLICACAO.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _g in ('coleta', 'leis', 'regras', 'guarda', 'pedido', 'superficie', 'ferramentas', ''):
    sys.path.insert(0, os.path.join(RAIZ, _g) if _g else RAIZ)
import _gavetas  # noqa: E402,F401

import rede as superficie              # noqa: E402 — o DONO do portao de egresso
import social_matriz as mz             # noqa: E402 — o dono da politica
import adaptador_youtube as ay         # noqa: E402 — a rota provada do audio publico

RUN_ID = 'CANARIO-D24-YOUTUBE-PESSOA'
EGRESSO_EXIGIDO = 'IT'

#: O VIDEO PUBLICO. Canal `xFarm` (empresa italiana de agricultura digital);
#: o alvo e' a PUBLICACAO, e nao o perfil de ninguem.
ALVO = 'https://www.youtube.com/watch?v=WOrq-i7JXJc'
VIDEO_ID = 'WOrq-i7JXJc'

#: O QUE A PROPRIA PLATAFORMA DECLARA, medido no `oembed` e no acervo da casa.
#: A identificacao da pessoa pelo handle NAO e' inferencia nossa: e' a mesma
#: base do canario do Reel (imprensa italiana nomeia o agronomo pelo handle).
PESSOA = {
    'NOME_PUBLICO': 'Alessandro Giglietti',
    'HANDLE': 'dr.agricultura',
    'PAPEL': 'dottore agronomo (laureado em Agraria, Univ. Firenze) — divulgador',
    'PAPEL_EVIDENCIA': ('a propria plataforma o nomeia na descricao da '
                        'publicacao (canal xFarm); imprensa italiana '
                        '(Gazzetta di Siena, Corriere.it) liga o handle a pessoa'),
    'MESMA_PESSOA_DO_CANARIO': 'provas/canario_d24_reel_de_pessoa.py',
}

SAIDA = os.path.join(RAIZ, 'data', 'samples', 'CANARIO-D24-YOUTUBE-PESSOA-V1.json')
ACHADOS = {}


def mede(nome, valor, porque=''):
    ACHADOS[nome] = {'VALOR': valor, 'PORQUE': porque}
    print('  %-34s = %-28s %s' % (nome, str(valor)[:28], porque[:64]))
    return valor


def oembed(url):
    """A declaracao da PLATAFORMA sobre a publicacao. Gratis, sem chave."""
    u = 'https://www.youtube.com/oembed?' + urllib.parse.urlencode(
        {'url': url, 'format': 'json'})
    try:
        with urllib.request.urlopen(urllib.request.Request(
                u, headers={'User-Agent': 'Mozilla/5.0 (compatible; sintonia-scrap)'}),
                timeout=30) as f:
            return f.status, json.loads(f.read().decode('utf-8', 'replace'))
    except Exception as ex:                                          # noqa: BLE001
        return None, {'ERRO': '%s: %s' % (type(ex).__name__, str(ex)[:120])}


def main():
    print('=' * 78)
    print('CANARIO REAL · D24 · O VIDEO DE UM AGRONOMO ITALIANO NO YOUTUBE')
    print('=' * 78)

    # ── 0 · O AMBIENTE DE REDE, ANTES — pelo portao do dono ───────────────
    antes = superficie.portao_de_egresso(EGRESSO_EXIGIDO)
    mede('EGRESS_GATE_BEFORE', antes['EGRESS_GATE'],
         'o portao do dono (superficie/rede.py), ANTES de qualquer pedido')
    mede('EGRESS_COUNTRY_BEFORE', antes['EGRESS_COUNTRY_CODE'],
         'medido na hora, e nao o que a missao dizia')
    if antes['EGRESS_GATE'] != 'PASS':
        mede('RESULTADO', 'PARADO_NO_PORTAO_DE_EGRESSO',
             'a corrida nao comeca fora de %s' % EGRESSO_EXIGIDO)
        print('\nARTEFACTO NAO ESCRITO: a corrida nao aconteceu.')
        return 1

    # ── 1 · A LEI, SEM ESTAGIO: o que a matriz ja' manda para o YouTube ───
    d = mz.decisao('YOUTUBE', 'FETCH_AUDIO_BYTES')
    mede('MATRIZ_DECISAO', d.get('DECISAO'), 'a acao que ESTA corrida usa, sem estagio')
    mede('MATRIZ_ROTA', d.get('ROTA'), 'a rota provada para os BYTES DE SOM')
    mede('MATRIZ_LIMITE', d.get('LIMITE'), 'o limite que viaja no objeto')
    mede('MATRIZ_OWNER_AUTHORIZED', d.get('OWNER_AUTHORIZED'), 'o eixo do dono do risco')
    mede('MATRIZ_PLATFORM_POLICY', d.get('PLATFORM_POLICY_STATUS'), 'o eixo da plataforma')
    # ⚠️ A rota da TRANSCRICAO e' outra, e e' PAGA. Regista-se para que ninguem
    # leia o `yt-dlp` ao lado do `apify` e conclua que este canario pagou algo.
    dt = mz.decisao('YOUTUBE', 'FETCH_TRANSCRIPT')
    mede('MATRIZ_TRANSCRICAO_ROTA', dt.get('ROTA'),
         'a transcricao e rota PAGA (apify) — NAO foi tocada nesta corrida')

    # ── 2 · A DECLARACAO DA PLATAFORMA, leram-na — e nao se inventa ───────
    print('\n  2 · o que a propria PLATAFORMA declara da publicacao (oembed, gratis)')
    cod, oe = oembed(ALVO)
    mede('OEMBED_HTTP', cod, 'a plataforma respondeu a convidado, sem chave')
    mede('PLATAFORMA_DECLARA_TITULO', (oe.get('title') or '')[:80], 'titulo como a plataforma o serve')
    mede('PLATAFORMA_DECLARA_CANAL', oe.get('author_name'), 'quem publica, segundo a plataforma')
    mede('PESSOA_ALVO', '%s · %s' % (PESSOA['NOME_PUBLICO'], PESSOA['HANDLE']),
         'identificada fora da plataforma, e nao por inferencia do handle')

    # ── 3 · A AQUISICAO, pela rota provada (audio publico, D17.4/C13) ─────
    print('\n  3 · a aquisicao: yt-dlp:public_audio')
    try:
        objetos = ay.youtube_audio_publico(run_id=RUN_ID, country_scope='IT',
                                           video_url=ALVO)
    except Exception as ex:                                          # noqa: BLE001
        mede('AQUISICAO', 'FALHOU', '%s: %s' % (type(ex).__name__, str(ex)[:110]))
        objetos = []

    if objetos:
        o = objetos[0]
        mede('ROUTE', o.get('ROUTE'), 'a rota que a matriz declara')
        mede('EXECUTOR', o.get('EXECUTOR'), 'quem executou')
        mede('LIMITE', o.get('LIMITE'), 'o limite da rota')
        mede('MEDIA_KIND', o.get('MEDIA_KIND'), 'a especie do que veio')
        mede('CONTENT_TYPE', o.get('CONTENT_TYPE'), 'declarado por quem mediu os bytes')
        mede('AUDIO_BYTES', o.get('AUDIO_BYTES'), 'bytes de som medidos no ficheiro')
        mede('AUDIO_SHA256', o.get('AUDIO_SHA256'), 'o hash que nao se finge')
        mede('AUDIO_DURATION_S', o.get('AUDIO_DURATION_S'), 'duracao medida pelo dono do ffprobe')
        mede('STREAMS_VIDEO', (o.get('STREAMS') or {}).get('VIDEO'),
             'zero: o ficheiro e som, e chama-lo de video seria a 1a mentira')
        mede('STREAMS_AUDIO', (o.get('STREAMS') or {}).get('AUDIO'), 'faixas de som')
        mede('VIDEO_ID_DE_ORIGEM', (o.get('PARENT') or {}).get('VIDEO_ID'),
             'o VIDEO fica preservado como PAI do som')
        mede('COUNTRY_SCOPE', o.get('COUNTRY_SCOPE'), 'o escopo declarado no objeto')
        caminho = o.get('AUDIO_REFERENCE')
        if caminho and os.path.exists(caminho):
            h = hashlib.sha256()
            with open(caminho, 'rb') as f:
                for b in iter(lambda: f.read(1 << 20), b''):
                    h.update(b)
            mede('SHA_CONFERIDO_NO_DISCO', h.hexdigest() == o.get('AUDIO_SHA256'),
                 'recalculado agora, fora do objeto')
            mede('BYTES_NO_DISCO', os.path.getsize(caminho), 'o ficheiro existe e mede-se')

    # ── 4 · O QUE ESTA ROTA **NAO** ENTREGA, e fica escrito ───────────────
    mede('VIDEO_BYTES', 'NOT_RUN',
         'a matriz so declara audio para o YouTube; bytes de imagem = capability nova')
    mede('TRANSCRIPT_STATE', 'NOT_RUN',
         'transcrever e outra capacidade (ferramentas/youtube_transcrever.py), e a fila nao foi tocada')
    mede('CUSTO_USD', 0.0, 'rota gratuita por decisao do dono')

    # ── 5 · O AMBIENTE DE REDE, DEPOIS ────────────────────────────────────
    print('\n  5 · o portao de egresso, depois da corrida')
    depois = superficie.portao_de_egresso(EGRESSO_EXIGIDO)
    mede('EGRESS_GATE_AFTER', depois['EGRESS_GATE'], 'o mesmo portao do dono, DEPOIS')
    mede('EGRESS_COUNTRY_AFTER', depois['EGRESS_COUNTRY_CODE'],
         'a corrida INTEIRA saiu por %s?' % EGRESSO_EXIGIDO)
    mede('EGRESSO_UNICO_NA_CORRIDA',
         antes['EGRESS_COUNTRY_CODE'] == depois['EGRESS_COUNTRY_CODE'] == EGRESSO_EXIGIDO,
         'antes e depois dao o mesmo pais exigido')
    mede('RESULTADO', 'ADQUIRIDO' if objetos else 'NAO_ADQUIRIDO',
         'o veredito desta corrida')

    ACHADOS['_O_QUE_ISTO_E'] = (
        'O video publico de um agronomo ITALIANO (a mesma pessoa do canario do '
        'Reel), adquirido pela rota PUBLIC_AUDIO_ONLY do YouTube, sem conta, sem '
        'login, sem cookie e por US$ 0. O que se mede sao os BYTES DE SOM: a '
        'matriz nao declara rota para os bytes de imagem do YouTube.')
    ACHADOS['_COMO_REFAZER'] = ('python provas/canario_d24_video_youtube_de_pessoa.py '
                               '(com `python`, que tem yt-dlp — nao com `py`)')
    ACHADOS['_PESSOA'] = PESSOA
    ACHADOS['_ALVO'] = ALVO
    ACHADOS['_LIMITES'] = {'SEM_CONTA': True, 'SEM_LOGIN': True, 'SEM_COOKIE': True,
                           'SEM_NAVEGADOR_LOGADO': True, 'SEM_ROTA_PAGA': True,
                           'SEM_CONTORNAR_MURO': True, 'SO_PUBLICO': True}
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with io.open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(ACHADOS, f, ensure_ascii=False, indent=1, default=str)
    print('\nARTEFACTO: %s' % os.path.relpath(SAIDA, RAIZ))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())