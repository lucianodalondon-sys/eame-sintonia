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

NOME = 'adaptador_instagram'
PLATAFORMA = 'INSTAGRAM'


def capturar_reel(*, url=None, ident=None, run_id, model_hint=None,
                  midia_url=None, midia_ficheiro=None, guardar=True, **_):
    """Um Reel, ponta a ponta. → (objetos, trace).

    Delega a cadeia ja provada. NAO a reimplementa: a cadeia tem 47 testes e
    oito Reels reais no disco, e reescrever isso aqui seria criar a terceira
    cadeia numa missao que existe para acabar com a segunda.
    """
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
reg.registar(PLATAFORMA, 'instagram.reel.transcribe', adaptador=NOME,
             executa=capturar_reel,
             nota='o unico caminho onde o ASR proprio e indispensavel')

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
