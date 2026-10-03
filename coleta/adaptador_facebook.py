#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADAPTADOR DO FACEBOOK — o muro mais alto, e a granularidade que o impede de mentir.

De todas as plataformas medidas, e a unica onde a IDENTIDADE sai e o CONTEUDO
nao sai nenhum. `gallery-dl` deslogado devolveu id da Page, fbid, albuns e URL
canonica. Texto, imagem, video, Reels, comentarios e metricas: 302 e 400 em
tudo, deste IP. NENHUM OBJETO FOI CAPTURADO.

    ESCREVER «FACEBOOK = BLOCKED» SERIA MAIS CURTO E MENOS VERDADEIRO.

Por isso as quatro capacidades estao separadas: identidade PARTIAL, e conteudo,
midia e metricas BLOCKED. Colapsa-las numa linha so apagaria o unico sitio por
onde esta plataforma ainda responde.

E existir um adaptador nao muda nada disto. Um adaptador declara; quem decide
se ha resultado e o estado medido.

    `BLOCKED` NAO VIRA SUCESSO PORQUE ALGUEM ESCREVEU CODIGO PARA ELE.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import scrap_registo as reg  # noqa: E402

NOME = 'adaptador_facebook'
PLATAFORMA = 'FACEBOOK'

reg.registar(PLATAFORMA, 'facebook.identity.discovery', adaptador=NOME,
             nota='id da Page, fbid, albuns e URL canonica, deslogado')
reg.registar(PLATAFORMA, 'facebook.content', adaptador=NOME, nota='302 login')
reg.registar(PLATAFORMA, 'facebook.media', adaptador=NOME, nota='302/400 deste IP')
reg.registar(PLATAFORMA, 'facebook.metrics', adaptador=NOME, nota='sem conteudo nao ha metrica')
