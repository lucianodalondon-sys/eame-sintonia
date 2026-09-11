#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTADOR DO LINKEDIN — a melhor midia das cinco, e o teto mais baixo.

E a unica plataforma onde o video e MP4 progressivo com endereco de vida longa
observada, e onde a legenda vem servida ao lado, com marcacao temporal. A
cadeia fecha sem login, sem navegador e sem rota paga.

O teto nao e acesso — e PROFUNDIDADE. A pagina da empresa entrega as ultimas
publicacoes e nao expoe endereco de pagina seguinte.

    `LINKEDIN_DISCOVERY_RECENT = PROVEN`.  `DEPTH = SHALLOW`.

Sao dois factos, e o segundo nao revoga o primeiro. Escrever
`LINKEDIN_DISCOVERY = BLOCKED` foi erro medido e ja corrigido, e nao se repete.

A LEGENDA NATIVA E DE MAQUINA, NAO DE GENTE
---------------------------------------------
O endereco da legenda di-lo em claro: `video-auto-caption-srt-acs-singleton`. E
SRT, nao WebVTT — numeracao de sequencia e virgula decimal, verificado nos
bytes. E automatica, o que significa ASR de outra casa.

    ISSO NAO A DESQUALIFICA. TORNA-A BARATA, NAO CONFIAVEL.

Uma legenda de maquina erra onde a nossa erra: termo agronomico e nome de
marca. Usa-se, e guarda-se de onde veio. Quando `TEXT_KIND` ganhar o valor
`NATIVE_CAPTION`, o ASR deles deixa de se confundir com o nosso.

NESTA MISSAO NAO SE EXPANDE DESCOBERTA NEM HISTORIA
-----------------------------------------------------
`linkedin.history.discovery` fica `UNKNOWN`, que e o que foi medido. Quanta
historia o SINTONIA precisa e decisao de quem coordena, nao de quem implementa.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import scrap_registo as reg  # noqa: E402

NOME = 'adaptador_linkedin'
PLATAFORMA = 'LINKEDIN'

# Sete capacidades medidas, nenhuma com rota ligada nesta missao. Declarar sem
# executar e honesto; executar sem declarar e que nao e.
reg.registar(PLATAFORMA, 'linkedin.recent.discovery', adaptador=NOME,
             nota='11, 13 e 10 activity ids em tres company pages; sem pagina seguinte')
reg.registar(PLATAFORMA, 'linkedin.history.discovery', adaptador=NOME,
             nota='«Show more» nao expoe URL; cinco cenarios em aberto no benchmark')
reg.registar(PLATAFORMA, 'linkedin.direct_post', adaptador=NOME,
             nota='HTTP 200 a convidado, com <video data-sources>')
reg.registar(PLATAFORMA, 'linkedin.native_video', adaptador=NOME,
             nota='tres MP4 progressivos; URL LONG_LIVED_OBSERVED, nunca «permanente»')
reg.registar(PLATAFORMA, 'linkedin.native_caption', adaptador=NOME,
             nota='SRT AUTOMATICA: ASR de outra casa, mais barata e nao melhor')
reg.registar(PLATAFORMA, 'linkedin.comments', adaptador=NOME, nota='nunca tentado')
reg.registar(PLATAFORMA, 'linkedin.documents', adaptador=NOME,
             nota='carrossel em PDF; nunca tentado')
