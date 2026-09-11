#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTADOR DO INSTAGRAM — a semantica da plataforma, e mais nada.

O adaptador sabe o que e um Reel, o que e um Story e o que e uma legenda de
autor. Nao sabe o que e `yt-dlp`, nao sabe o que e Whisper, e nao sabe se corre
aqui ou no computador da casa. Essas tres coisas tem donos proprios.

    ADAPTADOR    a semantica       Reel, Story, perfil, legenda
    FORNECEDOR   a ferramenta      yt-dlp, Instaloader, embed, Apify
    AMBIENTE     onde corre        ONLINE, LOCAL

A UNICA PLATAFORMA ONDE O RECONHECIMENTO DE FALA E INDISPENSAVEL
-----------------------------------------------------------------
O Instagram nao serve legenda nativa. O que ele serve e o `caption`, que e o
texto que o autor escreveu — e texto de autor nao e fala reconhecida.

    CAPTION != TRANSCRIPT. Somar os dois apaga qual deles sustentou uma
    classificacao, e essa pergunta e a que a inteligencia faz primeiro.

Por isso `instagram.native_caption` nao esta declarado em
`scrap_capacidades.py`: nao existe. A ausencia e o achado.

O ADAPTADOR NAO ESCOLHE MODELO
-------------------------------
`reel_transcricao.py` tem hoje `MODELO_PADRAO = 'medium'` e `fala_local.py` tem
`'small'`. Sao duas camadas a decidir, e a de cima ganha — de proposito, porque
Reel curto com termo agronomico e marca e onde o `small` escreveu «MICE» onde
se disse «mais».

Esta missao NAO fecha essa politica. O que ela faz e tirar a decisao das maos
do adaptador: aqui passa-se `model_hint`, e quem decide e o dono do ASR.

    `model_hint=None` E O CAMINHO NORMAL. Um valor so entra quando quem chama
    tem motivo declarado, e o motivo fica no trace.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import scrap_registo as reg          # noqa: E402
import scrap_fornecedores as forn    # noqa: E402
import scrap_capacidades as cap      # noqa: E402
import social_matriz as mz           # noqa: E402 — DONO da decisao de rota

NOME = 'adaptador_instagram'
PLATAFORMA = 'INSTAGRAM'


#: A PERGUNTA QUE AS TRES CAPACIDADES DE REEL FAZEM, E E UMA SO.
#
# `instagram.reel.capture`, `instagram.reel.audio` e `instagram.reel.transcribe`
# nao sao tres actos: sao tres nomes do mesmo acto — ir buscar a media do Reel e
# reconhecer a fala aqui na maquina. Na lingua da matriz esse acto chama-se
# FETCH_TRANSCRIPT, e e essa a unica pergunta que este adaptador faz a politica.
#
#     TRES NOMES PARA UM ACTO NAO SAO TRES AUTORIZACOES.
#
# NAO e FETCH_VIDEO_BYTES. A C10 mediu `VIDEO_BYTES_DOWNLOADED = 0` nesta cadeia,
# e pedir autorizacao para o que nao se faz seria alargar a superficie no papel.
#
# E O NOME NAO SE ESCREVE AQUI. Quem traduz `instagram.reel.transcribe` para a
# lingua da matriz e `scrap_capacidades`, e escrever a traducao uma segunda vez
# faria duas verdades que so um teste manteria iguais.
CAPACIDADE_NA_MATRIZ = cap.da_matriz('instagram.reel.transcribe')


def politica():
    """A decisao do dono da politica para esta plataforma. Zero rede, zero custo.

    Le `social_matriz` — nao mantem tabela propria e nao reinterpreta. Um
    segundo lugar a responder «pode?» seria um segundo portao, e o segundo
    portao e sempre o que ninguem mede.
    """
    return mz.decisao(PLATAFORMA, CAPACIDADE_NA_MATRIZ)


def _recusa(decisao):
    """O trace de quem NAO saiu. Recusa e resultado medido, nao ausencia dele."""
    trace = forn.Percurso('instagram.reel.transcribe').selar(
        resultado=decisao['DECISAO'])
    trace['POLICY_OWNER'] = 'leis/social_matriz.py'
    trace['POLICY_CAPABILITY'] = '%s/%s' % (PLATAFORMA, CAPACIDADE_NA_MATRIZ)
    trace['POLICY_WHY'] = decisao['PORQUE']
    trace['NETWORK_TOUCHED'] = False
    trace['ASR_RUN'] = False
    return trace


def capturar_reel(*, url=None, ident=None, run_id, model_hint=None,
                  midia_url=None, midia_ficheiro=None, guardar=True, **_):
    """Um Reel, ponta a ponta. → (objetos, trace).

    Delega a cadeia ja provada. NAO a reimplementa: a cadeia tem 47 testes e
    oito Reels reais no disco, e reescrever isso aqui seria criar a terceira
    cadeia numa missao que existe para acabar com a segunda.
    """
    # O PORTAO VEM PRIMEIRO — ANTES DO IMPORT DA CADEIA.
    #
    # Nao e zelo: `reel_transcricao` traz `yt_dlp` e o reconhecedor atras dele, e
    # perguntar «posso?» depois de carregar a ferramenta ja e ter decidido que
    # sim. Aqui a recusa custa uma leitura de dicionario e nao abre socket
    # nenhum.
    #
    #     O PORTAO QUE CORRE DEPOIS DA REDE NAO E UM PORTAO. E UM RELATORIO.
    decisao = politica()
    if decisao['DECISAO'] != mz.PERMITIDA_SIM:
        return [], _recusa(decisao)
    import reel_transcricao as rt
    if ident is None:
        if not url:
            return [], forn.Percurso('instagram.reel.transcribe').selar(
                resultado='NOT_ATTEMPTED')
        ident = rt.identidade_do_url(url)
    # `guardar=False` existe para a prova de fiacao: atravessar a cadeia
    # inteira sem escrever no disco da casa. Nao e um modo de producao.
    registo = rt.transcrever_reel(ident, run_id=run_id, midia_url=midia_url,
                                  midia_ficheiro=midia_ficheiro,
                                  modelo=model_hint, guardar=guardar)
    trace = forn.de_degraus('instagram.reel.transcribe',
                            registo.get('CAPTURE_ATTEMPTS'),
                            resultado=registo.get('MEDIA_STATE'))
    trace['ASR_MODEL_HINT'] = model_hint
    trace['ASR_OWNER'] = 'ferramentas/fala_local.py'
    return [registo], trace


def reel_transcrever(*, run_id, country_scope=None, medida=None, **kw):
    """A rota CRUA, que `social_rotas` despacha depois de medir o portao.

    Devolve a lista de objetos — o trace nasce do registo que o roteador sela.
    O que sobe daqui e MEDIDA, nao narrativa: quem executou de facto, quem fez o
    reconhecimento, e se a aquisicao foi mesmo so de som.

    POR QUE A IMPLEMENTACAO VAI NA MEDIDA E NAO NA MATRIZ
    ------------------------------------------------------
    A matriz chama esta rota `instagram_transcrever.py:faster-whisper`. Quem
    corre aqui e `ferramentas/reel_transcricao.py`. Sao dois ficheiros vivos da
    MESMA classe permitida (LOCAL_EXECUTOR, faster-whisper pelo mesmo dono de
    ASR), e escolher qual deles a matriz deve nomear e decisao de politica —
    logo, de gente. Ate la o registo diz as duas coisas: que rota a politica
    escolheu, e que ficheiro de facto correu.

        O TRACE QUE NOMEIA O FICHEIRO ERRADO MENTE COM PRECISAO DE RELOJOEIRO.
    """
    objetos, trace = capturar_reel(run_id=run_id, **kw)
    if medida is not None:
        medida['IMPLEMENTACAO'] = 'ferramentas/reel_transcricao.py'
        medida['ASR_OWNER'] = 'ferramentas/fala_local.py'
        medida['POLICY_OWNER'] = 'leis/social_matriz.py'
        medida['PROVIDER_STEPS'] = trace.get('PROVIDER_STEPS')
        primeiro = (objetos or [None])[0] or {}
        for k in ('MEDIA_KIND_REQUESTED', 'MEDIA_KIND_USED',
                  'AUDIO_ONLY_ACQUISITION', 'MEDIA_STATE'):
            medida[k] = primeiro.get(k, 'NAO SEI')
    return objetos


# ══════════════════════════════════════════════════════════════════════════
# O QUE ESTE ADAPTADOR DECLARA
# ══════════════════════════════════════════════════════════════════════════
# Tres capacidades com rota, quatro sem. As quatro sem rota NAO devolvem
# sucesso vazio: o executor le o estado medido e responde com ele.
reg.registar(PLATAFORMA, 'instagram.reel.capture', adaptador=NOME,
             executa=capturar_reel,
             nota='mesma cadeia da transcricao; a captura e o primeiro degrau')
reg.registar(PLATAFORMA, 'instagram.reel.audio', adaptador=NOME,
             executa=capturar_reel,
             nota='FFmpeg extrai do video ja preservado; faixa m4a poupa 7,58x de banda')
# A UNICA DAS TRES COM `rota`, E E DE PROPOSITO.
#
# `rota` significa: quem colhe isto entra pelo caminho canonico — executor,
# roteador, portao — e o trace nasce do registo que o roteador sela. `executa`
# significa o contrario: nao ha porta a atravessar, por isso monta-se o proprio
# trace. Ate a C10.4 as tres tinham `executa`, e a nota que justificava isso era
# verdadeira — a matriz nao conhecia nenhuma delas.
#
# Agora conhece esta. Deixar `executa` aqui seria manter aberta, ao lado do
# portao, a porta que existia por nao haver portao.
reg.registar(PLATAFORMA, 'instagram.reel.transcribe', adaptador=NOME,
             rota=reel_transcrever,
             nota='o unico caminho onde o ASR proprio e indispensavel; '
                  'atravessa INSTAGRAM/FETCH_TRANSCRIPT no dono da politica')

reg.registar(PLATAFORMA, 'instagram.profile.discovery', adaptador=NOME,
             nota='302/429 deste IP; a janela esgota em ~8-10 respostas')
reg.registar(PLATAFORMA, 'instagram.post.comments', adaptador=NOME,
             nota='nenhuma rota anonima provada')
reg.registar(PLATAFORMA, 'instagram.story.capture', adaptador=NOME,
             nota='capacidade real numa linhagem que o HEAD nao contem; sem rota de captura')
reg.registar(PLATAFORMA, 'instagram.story.transcribe', adaptador=NOME,
             nota='quando houver captura, pede ao dono do ASR; nao traz motor proprio')

assert not cap.existe('instagram.native_caption'), (
    'o Instagram nao serve legenda nativa; declarar isso seria prometer o que '
    'a plataforma nao tem')
