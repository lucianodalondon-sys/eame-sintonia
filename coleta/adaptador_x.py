#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTADOR DO X / TWITTER — onde `ZERO_APIFY` deixa de significar `ZERO CUSTO`.

O X e a unica das cinco plataformas onde a Apify ja era zero antes de alguem
tentar: nunca houve actor de X citado neste repositorio. E e tambem a unica
onde existe uma rota paga OFICIAL com preco de tabela por recurso lido.

    ZERO_APIFY  !=  ZERO_PAID_PROVIDER

Sao duas contas diferentes, e confundi-las faria o X parecer resolvido quando
a decisao dele nem sequer comecou.

O QUE FOI MEDIDO, E EM QUE CONDICOES
-------------------------------------
`gallery-dl` deslogado devolveu o tweet inteiro: texto, idioma, metricas
— incluindo visualizacoes — perfil do autor, imagem e video. Nada foi
autenticado e nada foi pago.

E, no mesmo dia, o `robots.txt` do X no grupo que nos serve diz:

    User-agent: *
    Disallow: /

O `Allow: /i/api/` que ele tem existe apenas no grupo `Googlebot`/`Bingbot`,
que nao somos. Para nos o estado e `ROBOTS_STATUS = DISALLOW_ALL`.

    CAPACIDADE TECNICA PROVADA  !=  AUTORIZACAO PARA PRODUCAO.

Sao eixos diferentes, e so um deles esta fechado. Os outros quatro documentos
de politica — Termos, API oficial, politica da casa, autorizacao do cliente —
continuam por levantar. Por isso este adaptador DECLARA e nao executa: ligar a
rota agora seria transformar um teste em producao, que e exatamente o que esta
missao proibe.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import scrap_registo as reg  # noqa: E402

NOME = 'adaptador_x'
PLATAFORMA = 'X'

reg.registar(PLATAFORMA, 'x.direct_post', adaptador=NOME,
             nota='gallery-dl deslogado; medido e nao ligado — politica por levantar')
reg.registar(PLATAFORMA, 'x.media', adaptador=NOME,
             nota='imagem 208.216 bytes e video 1.338.520 bytes, HTTP 200')
reg.registar(PLATAFORMA, 'x.metrics', adaptador=NOME,
             nota='favorite, retweet, reply, quote, bookmark e view_count vem no mesmo objeto')
reg.registar(PLATAFORMA, 'x.native_caption', adaptador=NOME,
             nota='existe e veio VAZIA: «could not transcribe the audio»')
reg.registar(PLATAFORMA, 'x.discovery', adaptador=NOME,
             nota='nenhuma listagem de cronologia foi tentada')
