#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O PORTAO E A BUSCA — as primitivas de HTTP que todo adaptador atravessa.

    import scrap_http as http
    ok, motivo = http.permitido('https://exemplo.tld/caminho')
    corpo = http.buscar(url)          # levanta se o portao recusar

POR QUE ISTO SAIU DO ROTEADOR
------------------------------
Enquanto o portao vivia dentro de `social_rotas.py`, um adaptador so conseguia
usa-lo importando o roteador — e o roteador precisa de conhecer os adaptadores
para os despachar. Isso e um ciclo, e ciclos resolvem-se por ordem de import,
que e exatamente o que esta casa ja mediu como perigoso.

Com as primitivas aqui, ninguem importa o roteador para bater a uma porta.

    O PORTAO NAO MUDOU DE REGRA AO MUDAR DE FICHEIRO. E o mesmo codigo, com o
    mesmo `User-Agent`, a ler o mesmo robots.txt vivo.

O QUE O PORTAO FAZ, E POR QUE ELE EXISTE
-----------------------------------------
`social_matriz.py` DECLARA que uma rota e permitida. Declaracao nao impede
ninguem de nada. Entao toda rota de HTTP direto passa, antes da primeira
requisicao, por `permitido()` — que busca o `robots.txt` REAL do host, com o
`User-Agent` REAL desta coleta, e recusa o caminho barrado.

    O ROBOTS E LIDO NA HORA, NAO DECORADO NO CODIGO.

E o portao ja REPROVOU rota que funcionava: o `feeds/videos.xml` do YouTube
devolveu 15 videos italianos com descricao inteira nesta maquina, e esta em
`Disallow`. Ele nao entrou. E para isso que o portao serve — se ele so
aprovasse, nao seria portao.

O QUE ESTE FICHEIRO NAO FAZ
----------------------------
Nao faz login, nao manda cookie, nao resolve CAPTCHA, nao troca de IP para
escapar de bloqueio, nao finge ser navegador de gente. Quando a plataforma diz
nao, a resposta e `ROUTE_NOT_ALLOWED` ou `BLOCKED` no artefato — nunca uma
tentativa mais esperta.
"""
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser

# O agente se identifica. Nao ha ganho em mentir e ha perda: um host que quer
# nos barrar tem direito de nos reconhecer, e um host que nos permite precisa
# conseguir nos medir.
AGENTE = 'SintoniaScrap/1.0 (+EAME; social capability census; contato via repositorio)'

TIMEOUT = 25
PAUSA_ENTRE_CHAMADAS = 1.0   # cortesia; nenhum host desta missao pede menos

_ROBOTS = {}


class RotaNaoPermitida(RuntimeError):
    """A rota existe, responderia, e nós não vamos usá-la."""


class RotaBloqueada(RuntimeError):
    """A plataforma nos impediu. Diferente de não permitida."""


# ══════════════════════════════════════════════════════════════════════════
# O PORTÃO
# ══════════════════════════════════════════════════════════════════════════
def permitido(url):
    """Lê o robots.txt vivo do host e responde (bool, motivo).

    Host que não publica robots.txt é permissivo por omissão — é o caso
    medido do t.me. Host que responde HTML em vez de robots (Instagram e
    Threads, deste IP) é `UNKNOWN`: não afirmamos permissão que não lemos.
    """
    partes = urllib.parse.urlsplit(url)
    base = '%s://%s' % (partes.scheme, partes.netloc)
    if base not in _ROBOTS:
        _ROBOTS[base] = _carregar_robots(base)
    rp, estado = _ROBOTS[base]
    if estado == 'AUSENTE':
        return True, 'host não publica robots.txt (permissivo por omissão)'
    if estado == 'ILEGIVEL':
        return False, 'robots.txt ilegível deste host — não afirmamos permissão que não lemos'
    ok = rp.can_fetch(AGENTE, url)
    if not ok:
        return False, 'robots.txt do host barra este caminho para %s' % AGENTE.split('/')[0]
    return True, 'robots.txt do host permite este caminho'


def _carregar_robots(base):
    rp = urllib.robotparser.RobotFileParser()
    try:
        req = urllib.request.Request(base + '/robots.txt', headers={'User-Agent': AGENTE})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as f:
            corpo = f.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return rp, 'AUSENTE'
        return rp, 'ILEGIVEL'
    except Exception:
        return rp, 'ILEGIVEL'
    # Um host que devolve HTML no lugar do robots não está publicando regra:
    # está nos mandando para uma página. Isso não é "pode".
    if corpo.lstrip()[:9].lower().startswith('<!doctype') or corpo.lstrip()[:5].lower() == '<html':
        return rp, 'ILEGIVEL'
    rp.parse(corpo.splitlines())
    return rp, 'LIDO'


def buscar(url, *, aceitar_json=True):
    """GET com o portão na frente. Nenhuma rota escapa dele."""
    ok, motivo = permitido(url)
    if not ok:
        raise RotaNaoPermitida('%s · %s' % (motivo, url))
    req = urllib.request.Request(url, headers={
        'User-Agent': AGENTE,
        'Accept': 'application/json' if aceitar_json else 'text/html',
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as f:
            corpo = f.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        raise RotaBloqueada('HTTP %s em %s' % (e.code, url))
    except Exception as e:
        raise RotaBloqueada('%s em %s' % (type(e).__name__, url))
    finally:
        time.sleep(PAUSA_ENTRE_CHAMADAS)
    return corpo


# ══════════════════════════════════════════════════════════════════════════
# ADAPTADORES — um por rota permitida. Pequenos de propósito.
# ══════════════════════════════════════════════════════════════════════════


class EstadoDaApi(RuntimeError):
    """Carrega o estado canonico que a propria API declarou, sem reinterpretar.

    Vive aqui, e nao no adaptador, porque quem o levanta e um adaptador e quem
    o apanha e o roteador. Se morasse num dos dois, o outro teria de o importar
    — e um deles importar o outro e o ciclo que este ficheiro existe para
    desfazer.
    """

    def __init__(self, rel):
        self.rel = rel
        super().__init__('%s (razao nativa: %s)' % (rel.get('STATE'),
                                                    rel.get('NATIVE_REASON')))


#: Nomes antigos, mantidos porque codigo vivo ja os chama assim.
_get = buscar
_EstadoDaApi = EstadoDaApi
