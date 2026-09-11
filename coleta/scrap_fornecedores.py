#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FORNECEDORES — o degrau que caiu tem de dizer o nome, e por que caiu.

    import scrap_fornecedores as forn
    p = forn.Percurso('instagram.reel.capture', pedido=forn.YTDLP)
    p.degrau(forn.YTDLP, 'MEDIA_DOWNLOAD_FAILED', 'HTTP 403 do CDN')
    p.degrau(forn.EMBED, 'MEDIA_OK', 'baixou 3.257.414 bytes')
    trace = p.selar()

ADAPTER != PROVIDER != EXECUTION ENVIRONMENT
---------------------------------------------
    ADAPTER     a semantica da plataforma        «como se fala com o Instagram»
    PROVIDER    a ferramenta que cumpre          «com yt-dlp, ou com Instaloader»
    AMBIENTE    onde aquilo corre                «aqui, ou no computador da casa»

Sao tres eixos. Fundir dois deles num conceito so parece simplificacao e custa
a verdade: `yt-dlp` traz metadados do YouTube e leva 403 nos bytes do mesmo
YouTube, do mesmo IP, no mesmo minuto. Quem so guardasse o fornecedor escreveria
«yt-dlp nao serve para YouTube», que e falso.

O QUE ESTE FICHEIRO EXISTE PARA IMPEDIR
----------------------------------------
    FALLBACK SILENCIOSO E MENTIRA COM OUTRO NOME.

Uma cadeia que pede `yt-dlp`, recebe do `embed`, e devolve so o objeto, produz
um resultado verdadeiro e uma historia falsa: quem le acredita que a primeira
rota funcionou. No dia em que a primeira rota morrer de vez, ninguem repara,
porque nunca reparou que ela ja tinha morrido.

Por isso quatro campos, e o validador recusa a falta do quarto:

    PROVIDER_REQUESTED   qual foi pedido
    PROVIDER_USED        qual entregou
    WHY_FALLBACK         por que o pedido nao serviu
    RESULT               o que saiu

    TROCAR DE FORNECEDOR SEM `WHY_FALLBACK` REPROVA. Nao e aviso: e recusa.
"""

# ── OS FORNECEDORES CONHECIDOS ────────────────────────────────────────────
# Os cinco primeiros sao os degraus que a cadeia de Reels ja usa hoje, com os
# nomes que ela ja grava. Nao foram renomeados: renomear e reescrever historia
# de artefatos que ja estao no disco.
FORNECIDO = 'MEDIA_FORNECIDA'
JA_PRESERVADO = 'MEDIA_JA_PRESERVADA'
YTDLP = 'LOCAL_YTDLP'
EMBED = 'LOCAL_EMBED'
APIFY = 'APIFY'

# Medidos no benchmark, ainda sem rota ligada.
INSTALOADER = 'LOCAL_INSTALOADER'
GALLERY_DL = 'LOCAL_GALLERY_DL'
HTTP_PROPRIO = 'LOCAL_HTTP'
API_OFICIAL = 'OFFICIAL_API'
BROWSER = 'LOCAL_BROWSER'

CONHECIDOS = (FORNECIDO, JA_PRESERVADO, YTDLP, EMBED, APIFY,
              INSTALOADER, GALLERY_DL, HTTP_PROPRIO, API_OFICIAL, BROWSER)

#: Os que custam dinheiro. `COL-LAW-019`: rota paga e escalada, nao padrao.
PAGOS = (APIFY,)

#: A CLASSE da rota, como `social_matriz` a declara, traduzida para o
#: fornecedor. Existe porque a matriz fala de CLASSE DE PORTA e o trace fala
#: de FERRAMENTA, e sao perguntas diferentes: `OFFICIAL_API_FREE` e
#: `OFFICIAL_API_PAID` sao a mesma ferramenta com contas diferentes.
#:
#:     QUEM PAGA NAO SE LE NO NOME DO FORNECEDOR. Le-se em `PAID_PROVIDER_USED`
#:     e no `COST_USD` da corrida.
POR_CLASSE = {
    'OFFICIAL_API_FREE': API_OFICIAL,
    'OFFICIAL_API_PAID': API_OFICIAL,
    'APIFY': APIFY,
    'PUBLIC_NATIVE': HTTP_PROPRIO,
    'DIRECT_HTTP': HTTP_PROPRIO,
    'LOCAL_SESSION': BROWSER,
    'LOCAL_EXECUTOR': YTDLP,
}


def da_classe(classe):
    """→ o fornecedor daquela classe de rota, ou None se ninguem a declarou."""
    return POR_CLASSE.get(classe)


def do_registo(capacidade, registo):
    """Traduz o registo selado por `social_rotas` para o trace canonico.

    O roteador ja media tudo o que este trace precisa: a rota escolhida, a
    classe dela, o estado final e o custo. O que faltava era a leitura de
    cima — qual fornecedor foi pedido, qual entregou, e se houve troca.

    Nao ha troca aqui, e isso e o ponto: `social_rotas` escolhe UMA rota e
    executa. Se ela recusar, o resultado e o estado da recusa — nunca uma
    segunda tentativa por outra porta que ninguem pediu.
    """
    classe = (registo or {}).get('CLASSE_DA_ROTA')
    fornecedor = da_classe(classe)
    estado = (registo or {}).get('ESTADO')
    p = Percurso(capacidade, pedido=fornecedor)
    if fornecedor:
        p.degrau(fornecedor, estado, registo.get('ROTA_ESCOLHIDA'))
    trace = p.selar(resultado=estado)
    trace['ROUTE'] = (registo or {}).get('ROTA_ESCOLHIDA')
    trace['ROUTE_CLASS'] = classe
    trace['AUTH_MODE'] = (registo or {}).get('AUTH_MODE')
    trace['COST_USD'] = (registo or {}).get('COST_USD')
    # ── A MEDIDA SOBE, E SO SOBE SE EXISTIR ──────────────────────────────────
    # Balde vazio nao vira `0`: «a rota nao declarou» e «a rota gastou zero» sao
    # coisas diferentes, e colapsa-las e a forma mais barata de publicar um
    # palpite com cara de medida.
    medida = (registo or {}).get('MEDIDA') or {}
    for campo in ('QUOTA_UNITS', 'QUOTA_SEARCH_CALLS'):
        if campo in medida:
            trace[campo] = medida[campo]
    trace['NATIVE_REASON'] = (registo or {}).get('NATIVE_REASON')
    trace['RECOVERY_ACTION'] = (registo or {}).get('RECOVERY_ACTION')
    trace['FAILURE_LAYER'] = (registo or {}).get('FAILURE_LAYER')
    trace['ROUTER_RECORD'] = registo
    return trace


class TraceIncompleto(RuntimeError):
    """Houve troca de fornecedor e ninguem escreveu por que."""


class FornecedorDesconhecido(ValueError):
    """Nome de fornecedor fora da lista. Inventar nome e perder o rasto."""


class Percurso:
    """Os degraus de uma capacidade, na ordem em que foram tentados."""

    def __init__(self, capacidade, *, pedido=None):
        if pedido is not None and pedido not in CONHECIDOS:
            raise FornecedorDesconhecido(pedido)
        self.capacidade = capacidade
        self.pedido = pedido
        self.degraus = []

    def degrau(self, fornecedor, resultado, porque=None):
        """Regista uma tentativa. `porque` vale tanto para o que falhou como
        para o que serviu — e o campo que conta a historia."""
        if fornecedor not in CONHECIDOS:
            raise FornecedorDesconhecido(fornecedor)
        self.degraus.append({'PROVIDER': fornecedor, 'RESULT': resultado,
                             'WHY': porque})
        return self

    def selar(self, *, resultado=None):
        """→ o trace, sempre. Mesmo sem nenhum degrau."""
        usado = None
        for d in self.degraus:
            if str(d.get('RESULT', '')).endswith('_OK') or d.get('RESULT') == 'OK':
                usado = d['PROVIDER']
        pedido = self.pedido
        if pedido is None and self.degraus:
            pedido = self.degraus[0]['PROVIDER']
        porque = None
        if usado and pedido and usado != pedido:
            # o motivo e o do PRIMEIRO degrau que nao serviu
            for d in self.degraus:
                if d['PROVIDER'] == pedido:
                    porque = d.get('WHY') or d.get('RESULT')
                    break
            porque = porque or 'o fornecedor pedido nao entregou'
        trace = {
            'CAPABILITY': self.capacidade,
            'PROVIDER_REQUESTED': pedido,
            'PROVIDER_USED': usado,
            'WHY_FALLBACK': porque,
            'RESULT': resultado if resultado is not None else (
                self.degraus[-1]['RESULT'] if self.degraus else 'NOT_ATTEMPTED'),
            'PROVIDER_STEPS': list(self.degraus),
            'PAID_PROVIDER_USED': usado in PAGOS if usado else False,
        }
        conferir(trace)
        return trace


def de_degraus(capacidade, degraus, *, pedido=None, resultado=None):
    """Traduz os `degraus` que a cadeia de Reels ja produz para o trace canonico.

    A cadeia de Reels ja escrevia PROVIDER, RESULT e WHY por degrau desde que
    nasceu. O que faltava nao era medicao — era a leitura de cima: qual foi
    pedido, qual serviu, e por que houve troca.
    """
    p = Percurso(capacidade, pedido=pedido)
    for d in (degraus or ()):
        p.degrau(d.get('PROVIDER'), d.get('RESULT'), d.get('WHY'))
    return p.selar(resultado=resultado)


def conferir(trace):
    """Levanta `TraceIncompleto` se houve troca de fornecedor sem motivo escrito."""
    pedido = trace.get('PROVIDER_REQUESTED')
    usado = trace.get('PROVIDER_USED')
    if usado and pedido and usado != pedido and not trace.get('WHY_FALLBACK'):
        raise TraceIncompleto(
            '%s: pediu %s, usou %s, e nao disse por que. Fallback silencioso '
            'nao passa.' % (trace.get('CAPABILITY'), pedido, usado))
    for d in trace.get('PROVIDER_STEPS') or ():
        if d.get('PROVIDER') not in CONHECIDOS:
            raise FornecedorDesconhecido(d.get('PROVIDER'))
    return True


def houve_fallback(trace):
    pedido, usado = trace.get('PROVIDER_REQUESTED'), trace.get('PROVIDER_USED')
    return bool(usado and pedido and usado != pedido)
