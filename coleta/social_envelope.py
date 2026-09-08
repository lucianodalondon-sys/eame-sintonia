#!/usr/bin/env python3
"""
ENVELOPE SOCIAL — o pouco que TODA plataforma precisa ter, e nada além disso.

Este arquivo não é um normalizador universal. Ele é o CONTRÁRIO disso: a lista
curta de campos sem os quais um objeto social não pode ser auditado, mais um
saco `RAW` onde tudo o que é específico da plataforma continua vivo.

    A TENTAÇÃO É A FICHA ÚNICA. A FICHA ÚNICA É QUE MATA O DADO.

Se eu tentar espremer um Reel, um tweet, um post de LinkedIn e um vídeo de
YouTube na MESMA ficha rica, eu preciso escolher um vocabulário — e o
vocabulário escolhido apaga o que a plataforma tinha de próprio. `view_count`
do YouTube e `play_count` do TikTok não são a mesma medida; `retweets` não é
`shares`. Então o envelope guarda só o que é comparável de verdade, e o resto
fica em `RAW`, com o nome que a plataforma deu.

O QUE ENTRA NO ENVELOPE E POR QUÊ
-----------------------------------
    PLATFORM        de onde veio
    SOURCE_ACCOUNT  a conta/canal, quando existe
    NATIVE_ID       o id DA PLATAFORMA — é a chave da dedupe, não a URL
    URL             para um humano conferir
    CONTENT_TYPE    VIDEO | POST | PROFILE | CHANNEL | COMMENT | ARTICLE
    PUBLISHED_AT    quando a plataforma diz que publicou
    COLLECTED_AT    quando EU li
    LANGUAGE        idioma DECLARADO, nunca inferido do texto
    SOURCE_LOCATION país declarado pela fonte — UNKNOWN é resposta legítima
    COUNTRY_SCOPE   o recorte da MISSÃO que pediu isto
    ROUTE / EXECUTOR qual porta trouxe o objeto
    COST_USD        o que ESTE objeto custou
    RUN_ID          liga o objeto à execução que o produziu
    RAW_REFERENCE   onde está o bruto de onde isto foi derivado

IDIOMA NÃO É PAÍS, E O ENVELOPE SE RECUSA A CONFUNDIR OS DOIS
---------------------------------------------------------------
`LANGUAGE=it` e `SOURCE_LOCATION=IT` são campos DIFERENTES e nenhum dos dois é
derivado do outro. Um agrônomo suíço do Ticino publica em italiano e não é
Itália; a página italiana de uma multinacional é Itália e às vezes publica em
inglês. Quando a rota não disse o país, o campo vale `UNKNOWN` — que é um dado,
não um buraco.

    LÍNGUA ITALIANA NÃO PROVA ITÁLIA. `UNKNOWN` É MAIS BARATO QUE ERRADO.

A DEDUPE É POR `PLATFORM + NATIVE_ID`, NUNCA POR URL
------------------------------------------------------
A mesma publicação chega por URLs diferentes: com `?utm_source`, com `/reel/`
em vez de `/p/`, encurtada, com o handle novo depois de um rename. URL é
apresentação; `NATIVE_ID` é identidade. Quando duas rotas trazem o mesmo
objeto, ele continua sendo UM objeto e as duas rotas ficam preservadas em
`DISCOVERY_ROUTES` — rota de descoberta é proveniência, não evidência a mais.
"""
import datetime
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'samples', 'SOCIAL-IT')
RAW_DIR = os.path.join(SAIDA, 'raw-free')

# ── O QUE ESTA CORRIDA PRODUZIU, E SO ISSO ────────────────────────────────
# Varrer `RAW_DIR` responde "que arquivos existem no disco", que NAO e a mesma
# pergunta que "que arquivos esta corrida colheu". O checkout ja traz RAW de
# corridas antigas, entao a varredura fazia uma corrida que nem rodou parecer
# ter colhido.
#
#     CHECKOUT NAO E COLETA.
#
# O registro abaixo so cresce quando ESTE processo escreve um arquivo. Processo
# novo comeca vazio — de proposito: ele nao colheu nada.
_PRODUZIDOS = []


def produzidos():
    """Os RAW que ESTE processo escreveu, na ordem em que sairam."""
    return list(_PRODUZIDOS)


def esquecer_produzidos():
    """So para teste: devolve o processo ao estado de quem nao colheu nada."""
    del _PRODUZIDOS[:]


NOT_PRESERVED = 'NOT_PRESERVED'
PRESERVED = 'PRESERVED'

CONTENT_TYPES = ('VIDEO', 'POST', 'PROFILE', 'CHANNEL', 'COMMENT', 'ARTICLE', 'DISCOVERY')

# `UNKNOWN` é o valor de partida dos dois campos que a casa mais erra quando
# tem pressa. Nenhum deles é preenchido por inferência de texto.
DESCONHECIDO = 'UNKNOWN'


def agora():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')


def hoje():
    return datetime.datetime.now(datetime.timezone.utc).date().isoformat()


def guardar_raw(platform, chave, corpo):
    """Grava o bruto ANTES de qualquer normalização e devolve a referência.

    A ordem importa: se o normalizador quebrar, o bruto já está no disco e a
    coleta não precisa ser refeita. O nome do arquivo carrega o hash do corpo
    para que reler a mesma coisa duas vezes não gere dois arquivos.
    """
    if isinstance(corpo, (dict, list)):
        corpo = json.dumps(corpo, ensure_ascii=False, indent=1)
    corpo = corpo if isinstance(corpo, str) else str(corpo)
    h = hashlib.sha256(corpo.encode('utf-8')).hexdigest()[:16]
    pasta = os.path.join(RAW_DIR, platform.upper())
    os.makedirs(pasta, exist_ok=True)
    nome = '%s__%s.txt' % (_slug(chave)[:60], h)
    caminho = os.path.join(pasta, nome)
    if not os.path.exists(caminho):
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(corpo)
    if caminho not in _PRODUZIDOS:
        _PRODUZIDOS.append(caminho)
    return {
        'PATH': os.path.relpath(caminho, ROOT).replace('\\', '/'),
        'SHA256': hashlib.sha256(corpo.encode('utf-8')).hexdigest(),
        'SHA256_16': h,
        'BYTES': len(corpo.encode('utf-8')),
        # ── O ESTADO DE PRESERVAÇÃO VIAJA COM A REFERÊNCIA ──────────────────
        # Um `PATH` sozinho é uma promessa que o runner não pode cumprir: o disco
        # dele morre no fim do job, e a referência fica apontando para prova que
        # sumiu.
        #
        #     RAW_REFERENCE PARA ARQUIVO QUE SOME NÃO É PROVENIÊNCIA.
        #
        # Enquanto o dono forward do G-42 — o que escreve em Storage e em
        # `raw_asset` — não tiver recebido este byte, o estado é NOT_PRESERVED, e
        # ele vai ASSIM para o artefato. O hash inteiro vai junto: com ele, a
        # prova pode ser reconciliada depois; sem ele, some para sempre.
        #
        # O dono é nomeado pelo DESTINO, não pelo módulo, de propósito: a suíte
        # canônica trata uma menção ao módulo como CALLER REAL e exige que o
        # estado do G-42 suba para OPERATIONAL. Aqui não há chamada nenhuma — só
        # a declaração de para onde este byte ainda precisa ir. Citar o módulo
        # seria reivindicar uma integração que não existe.
        'PRESERVATION': NOT_PRESERVED,
        'PRESERVATION_OWNER': 'G-42 forward: Supabase Storage + raw_asset',
        'NOT_PRESERVED_REASON': (
            'gravado no disco do runner; ainda não entregue ao dono forward'),
    }


def _slug(s):
    return ''.join(c if (c.isalnum() or c in '-_.') else '-' for c in str(s)).strip('-')


def envelope(*, platform, native_id, url, content_type, route, executor,
             run_id, country_scope, source_account=None, published_at=None,
             language=None, source_location=None, cost_usd=0.0,
             raw_reference=None, raw=None, title=None, text=None):
    """Monta o envelope canônico. Campos ausentes viram UNKNOWN, nunca ''."""
    if content_type not in CONTENT_TYPES:
        raise ValueError('CONTENT_TYPE fora do vocabulário: %r' % content_type)
    return {
        'PLATFORM': platform.upper(),
        'SOURCE_ACCOUNT': source_account or DESCONHECIDO,
        'NATIVE_ID': str(native_id),
        'URL': url,
        'CONTENT_TYPE': content_type,
        'TITLE': title,
        'TEXT': text,
        'PUBLISHED_AT': published_at or DESCONHECIDO,
        'COLLECTED_AT': agora(),
        # Os dois campos que NUNCA se derivam um do outro.
        'LANGUAGE': language or DESCONHECIDO,
        'SOURCE_LOCATION': source_location or DESCONHECIDO,
        'COUNTRY_SCOPE': country_scope,
        'ROUTE': route,
        'EXECUTOR': executor,
        'COST_USD': round(float(cost_usd), 6),
        'RUN_ID': run_id,
        'RAW_REFERENCE': raw_reference,
        'DISCOVERY_ROUTES': [route],
        'RAW': raw if raw is not None else {},
    }


def dedupe(objetos):
    """UM objeto lógico por `PLATFORM + NATIVE_ID`. Rotas somam, objetos não.

    Devolve `(lista, relatorio)`. O relatório conta o que foi fundido, porque
    "achei 40" e "achei 40 distintos" são frases diferentes e a segunda é a
    única que pode virar número num relatório.
    """
    vistos = {}
    ordem = []
    fundidos = 0
    for o in objetos:
        chave = (o['PLATFORM'], o['NATIVE_ID'])
        if chave in vistos:
            alvo = vistos[chave]
            for r in o.get('DISCOVERY_ROUTES', []):
                if r not in alvo['DISCOVERY_ROUTES']:
                    alvo['DISCOVERY_ROUTES'].append(r)
            # O objeto que chegou depois só preenche buraco; nunca sobrescreve
            # um valor que já veio de outra rota. Duas rotas discordando é um
            # fato a preservar, não um empate a resolver no silêncio.
            for campo in ('TITLE', 'TEXT', 'PUBLISHED_AT', 'LANGUAGE', 'SOURCE_LOCATION'):
                if alvo.get(campo) in (None, DESCONHECIDO) and o.get(campo) not in (None, DESCONHECIDO):
                    alvo[campo] = o[campo]
            fundidos += 1
            continue
        vistos[chave] = o
        ordem.append(o)
    return ordem, {'ENTRARAM': len(objetos), 'DISTINTOS': len(ordem), 'FUNDIDOS': fundidos}


def gravar(nome, corpo):
    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, nome)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return os.path.relpath(caminho, ROOT).replace('\\', '/')


def ler(nome, padrao=None):
    caminho = os.path.join(SAIDA, nome)
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)
