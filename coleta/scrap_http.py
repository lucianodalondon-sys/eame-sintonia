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


class PortaoIndisponivel(RuntimeError):
    """Não deu para LER o robots.txt — o transporte caiu antes da resposta.

    ⚠️ ISTO NÃO É UMA RECUSA, E ATÉ A C10.8A ERA REPORTADO COMO UMA.

    O portão tinha três respostas: `LIDO`, `AUSENTE` e `ILEGIVEL`. Um
    `Connection reset by peer` a meio do túnel caía em `ILEGIVEL`, que
    `permitido()` traduz para `False` — e o roteador, para `ROUTE_NOT_ALLOWED`.

    Medido ao vivo: `public.api.bsky.app/robots.txt` responde `200` com
    `Allow: /` e um comentário que diz, por escrito, «Crawling the public parts
    of the API is allowed». O trilho canônico dizia `ROUTE_NOT_ALLOWED` sobre
    uma rota que a plataforma autoriza em voz alta.

        UM TRANSPORTE QUE CAIU NÃO É UMA POLÍTICA QUE RECUSOU.

    A recusa continua a acontecer — não se afirma permissão que não se leu. O
    que muda é o NOME dela: `TRANSIENT_NETWORK_ERROR` pede `WAIT`,
    `ROUTE_NOT_ALLOWED` pede `NO_RETRY`. Chamar a primeira pela segunda ensina
    a casa a desistir de uma porta que está aberta.
    """


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
    if estado == 'INDISPONIVEL':
        # Não esquecer o insucesso: uma tentativa seguinte pode ler o robots, e
        # guardar «indisponível» para sempre transformaria um soluço de rede
        # numa proibição permanente em memória.
        _ROBOTS.pop(base, None)
        raise PortaoIndisponivel(
            'não deu para LER o robots.txt de %s: o transporte caiu antes da '
            'resposta. Isto não é uma recusa do host.' % base)
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
        # O pedido diz o que e. Um `UNCLASSIFIED` no rasto seria o portao a nao
        # se reconhecer a si proprio.
        req.tipo_de_pedido = PEDIDO_ROBOTS
        with urllib.request.urlopen(req, timeout=TIMEOUT) as f:
            corpo = f.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        # O host RESPONDEU. 404/410 é «não publico regra»; o resto é uma
        # resposta que não sabemos ler. Nos dois casos houve conversa.
        if e.code in (404, 410):
            return rp, 'AUSENTE'
        return rp, 'ILEGIVEL'
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
        # O host NÃO respondeu. Não há robots para julgar, e não há recusa
        # nenhuma para registar.
        return rp, 'INDISPONIVEL'
    except Exception:
        return rp, 'ILEGIVEL'
    # Um host que devolve HTML no lugar do robots não está publicando regra:
    # está nos mandando para uma página. Isso não é "pode".
    if corpo.lstrip()[:9].lower().startswith('<!doctype') or corpo.lstrip()[:5].lower() == '<html':
        return rp, 'ILEGIVEL'
    rp.parse(corpo.splitlines())
    return rp, 'LIDO'


def buscar(url, *, aceitar_json=True):
    """GET com o portão na frente. Nenhuma rota escapa dele.

    `PortaoIndisponivel` sobe, não é apanhada: ela é o único caso em que o
    portão não conseguiu JULGAR. Transformá-la aqui numa recusa seria repetir
    o defeito que a C10.8A mediu ao vivo.
    """
    ok, motivo = permitido(url)
    if not ok:
        raise RotaNaoPermitida('%s · %s' % (motivo, url))
    req = urllib.request.Request(url, headers={
        'User-Agent': AGENTE,
        'Accept': 'application/json' if aceitar_json else 'text/html',
    })
    req.tipo_de_pedido = PEDIDO_ROTA
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as f:
            corpo = f.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        raise RotaBloqueada('HTTP %s em %s' % (e.code, url))
    except SemOrcamentoDeRede:
        # ⚠️ PELA SEGUNDA VEZ NESTA CADEIA: o `except Exception` ia traduzir uma
        # recusa NOSSA para `RotaBloqueada`, que quer dizer «a plataforma nos
        # impediu». Foi assim que a queda do tunel saiu como `ROUTE_NOT_ALLOWED`
        # na C10.8A, e seria assim que o teto sairia como `BLOCKED`.
        #
        #     ESGOTAR O ORCAMENTO NAO E A PLATAFORMA IMPEDIR.
        #
        # Um `except Exception` largo nao distingue quem disse nao. Por isso a
        # recusa do teto passa por cima dele, inteira.
        raise
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


# ══════════════════════════════════════════════════════════════════════════
# O ORÇAMENTO DE REDE — UM TETO QUE RECUSA, E NÃO UM CONTADOR QUE RELATA
# ══════════════════════════════════════════════════════════════════════════
# A C10.8A declarou `MAX_REAL_HTTP_REQUESTS = 2` e fez sete. O teto existia —
# num script de prova, do lado de fora do runtime. Quando a sonda rebentou e
# foi preciso repetir, o teto repetiu-se com ela, zerado, porque era uma
# variável de um processo que acabou.
#
#     UM TETO QUE VIVE NA PROVA MEDE A PROVA.
#     DECLARED BUDGET != ENFORCED BUDGET.
#
# ONDE ISTO TEM DE VIVER, E POR QUE NÃO É ÓBVIO
# -----------------------------------------------
# O censo da C10.8A-R mediu por onde as catorze capacidades ligadas saem para a
# rede, e são TRÊS portas diferentes:
#
#     scrap_http.buscar          5 capacidades (bluesky, mastodon, telegram)
#     reel_transcricao.baixar    3 capacidades (os Reels) — não passa aqui
#     cdp.abas / cdp._handshake  1 capacidade (a janela) — não passa aqui
#
# Ou seja: este ficheiro é o transporte NOMEADO da casa, e mesmo assim não vê
# tudo. Um contador em `buscar()` deixaria de fora metade das capacidades, e um
# teto que só cobre metade das portas não é um teto — é uma sugestão.
#
# O único ponto que TODAS atravessam é o transporte do próprio Python. Então o
# orçamento é declarado aqui, que é o dono do conceito «rede» nesta casa, e é
# cobrado lá, onde o socket nasce.
#
#     ONE CONCEPT → ONE OWNER. O dono é o transporte; o ponto de cobrança é
#     onde a ligação abre — e as duas coisas não precisam de ser a mesma linha.
#
# E ELE É DA EXECUÇÃO, NÃO DO PROCESSO
# --------------------------------------
# Duas execuções têm orçamentos distintos. Um contador global de módulo faria a
# segunda corrida herdar a dívida da primeira — e, pior, faria uma corrida
# inocente ser recusada por causa de outra.
import contextlib
import socket as _socket
import threading

_LOCAL = threading.local()

#: Os tipos de acesso, para o rasto dizer o que foi gasto em quê. Nenhum deles
#: é de graça: `ROBOTS` custa uma ida à rede como qualquer outra.
#:
#:     GRÁTIS EM DÓLAR != GRÁTIS EM REQUESTS.
PEDIDO_ROBOTS = 'ROBOTS'
PEDIDO_ROTA = 'ROUTE'
PEDIDO_RETENTATIVA = 'RETRY'
PEDIDO_ALTERNATIVA = 'FALLBACK'
PEDIDO_DIAGNOSTICO = 'DIAGNOSTIC'
PEDIDO_DESCONHECIDO = 'UNCLASSIFIED'


class SemOrcamentoDeRede(RuntimeError):
    """A tentativa N+1. Ela NÃO chega ao socket.

    Não é uma falha da fonte nem da rota: é esta casa a cumprir um limite que
    ela própria declarou. Quem a apanhar não deve traduzi-la para
    `ZERO_RESULTS` — não houve resultado nenhum, houve uma recusa nossa.
    """


class OrcamentoDeRede(object):
    """Quantos acessos externos esta execução ainda pode fazer."""

    def __init__(self, limite):
        if limite is None or int(limite) < 0:
            raise ValueError('limite de rede inválido: %r' % limite)
        self.limite = int(limite)
        self.usados = 0
        self.recusados = 0
        self.tentativas = []

    @property
    def restantes(self):
        return max(0, self.limite - self.usados)

    @property
    def esgotado(self):
        return self.usados >= self.limite

    def reservar(self, tipo, destino):
        """Pede UMA ida à rede. Levanta ANTES de qualquer socket existir.

            O GATE VEM ANTES DA REDE. Cobrar depois é contar o prejuízo.
        """
        registo = {'TYPE': tipo, 'TARGET': _so_o_host(destino),
                   'COUNTED': True, 'OUTCOME': None}
        if self.esgotado:
            self.recusados += 1
            registo.update({'COUNTED': False, 'OUTCOME': 'REFUSED_BY_BUDGET'})
            self.tentativas.append(registo)
            raise SemOrcamentoDeRede(
                'orçamento de rede esgotado: %d de %d já usados, e este pedido '
                '(%s → %s) seria o %d.'
                % (self.usados, self.limite, tipo, registo['TARGET'],
                   self.usados + 1))
        self.usados += 1
        self.tentativas.append(registo)
        return registo

    def para_o_rasto(self):
        return {
            'NETWORK_BUDGET_LIMIT': self.limite,
            'NETWORK_REQUESTS_USED': self.usados,
            'NETWORK_REQUESTS_REMAINING': self.restantes,
            'NETWORK_BUDGET_EXHAUSTED': self.esgotado,
            'NETWORK_REQUESTS_REFUSED': self.recusados,
            'NETWORK_ATTEMPTS': list(self.tentativas),
        }


def _so_o_host(destino):
    """O host, sem caminho e sem query. Uma query pode carregar segredo."""
    try:
        texto = destino if isinstance(destino, str) else getattr(
            destino, 'full_url', str(destino))
        partes = urllib.parse.urlsplit(texto)
        return partes.netloc or texto.split('/')[0]
    except Exception:                                             # noqa: BLE001
        return 'NAO_SEI'


def orcamento_actual():
    """O orçamento desta execução, ou None quando ninguém declarou um."""
    return getattr(_LOCAL, 'orcamento', None)


def _tipo_por_omissao(destino):
    """Um pedido que ninguém classificou ainda tem de ser classificado.

    O `robots.txt` reconhece-se pelo caminho, e é o único que se pode adivinhar
    sem mentir. O resto é `UNCLASSIFIED` — e `UNCLASSIFIED` conta na mesma.

        UM PEDIDO QUE NINGUÉM CLASSIFICOU NÃO É UM PEDIDO QUE NÃO ACONTECEU.
    """
    texto = destino if isinstance(destino, str) else getattr(
        destino, 'full_url', str(destino))
    return PEDIDO_ROBOTS if texto.endswith('/robots.txt') else PEDIDO_DESCONHECIDO


@contextlib.contextmanager
def orcamento_de_rede(limite, *, tipo_por_omissao=None):
    """Instala um teto de acessos externos para o bloco inteiro.

    O teto é cobrado no ponto onde a ligação abre — `urllib.request.urlopen` e
    `socket.create_connection` — porque as três portas de rede desta casa não
    passam todas por aqui. Cobrar em `buscar()` deixaria de fora os Reels e a
    janela.

    A re-entrância é contada: um `urlopen` abre um socket por dentro, e isso é
    UM pedido, não dois.
    """
    anterior = getattr(_LOCAL, 'orcamento', None)
    orcamento = limite if isinstance(limite, OrcamentoDeRede) else OrcamentoDeRede(limite)
    _LOCAL.orcamento = orcamento
    urlopen_real = urllib.request.urlopen
    conectar_real = _socket.create_connection

    def _dentro():
        return getattr(_LOCAL, 'profundidade', 0) > 0

    @contextlib.contextmanager
    def _um_nivel():
        _LOCAL.profundidade = getattr(_LOCAL, 'profundidade', 0) + 1
        try:
            yield
        finally:
            _LOCAL.profundidade -= 1

    def urlopen_com_teto(req, *a, **k):
        actual = orcamento_actual()
        if actual is None or _dentro():
            return urlopen_real(req, *a, **k)
        registo = actual.reservar(
            getattr(req, 'tipo_de_pedido', None)
            or tipo_por_omissao or _tipo_por_omissao(req), req)
        with _um_nivel():
            try:
                resposta = urlopen_real(req, *a, **k)
            except Exception as e:                                # noqa: BLE001
                registo['OUTCOME'] = type(e).__name__
                raise
        registo['OUTCOME'] = getattr(resposta, 'status', 'OK')
        return resposta

    def conectar_com_teto(endereco, *a, **k):
        actual = orcamento_actual()
        if actual is None or _dentro():
            return conectar_real(endereco, *a, **k)
        alvo = '%s:%s' % endereco if isinstance(endereco, tuple) else str(endereco)
        registo = actual.reservar(tipo_por_omissao or PEDIDO_DESCONHECIDO, alvo)
        with _um_nivel():
            try:
                ligacao = conectar_real(endereco, *a, **k)
            except Exception as e:                                # noqa: BLE001
                registo['OUTCOME'] = type(e).__name__
                raise
        registo['OUTCOME'] = 'OK'
        return ligacao

    urllib.request.urlopen = urlopen_com_teto
    _socket.create_connection = conectar_com_teto
    try:
        yield orcamento
    finally:
        urllib.request.urlopen = urlopen_real
        _socket.create_connection = conectar_real
        _LOCAL.orcamento = anterior


#: Nomes antigos, mantidos porque codigo vivo ja os chama assim.
_get = buscar
_EstadoDaApi = EstadoDaApi
