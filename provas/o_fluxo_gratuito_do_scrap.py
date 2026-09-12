#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UMA ROTA GRATUITA ATRAVESSA O FLUXO CANÓNICO? — prova offline, ponta a ponta.

    python3 provas/o_fluxo_gratuito_do_scrap.py

A SCRAP-FLOW-01 provou o caminho canónico com uma COMPRA, e deixou a pergunta
seguinte por responder:

    FREE != CANONICAL.  ROUTE WORKS != FLOW WORKS.

    «O fluxo canónico funciona também para uma aquisição gratuita, sem depender
     dos contratos específicos de uma compra?»

A rota medida é a janela pública do Instagram — `INSTAGRAM /
instagram.profile.discovery`, classe `PUBLIC_BROWSER`. Até aqui:

    sintonia-scrap.yml  ->  coleta/social_scrap.py coletar janela
                        ->  scrap_executor.COLLECT

Agora:

    sintonia-scrap.yml  ->  orquestrador  ->  PEDIDO  ->  plano + portão
                        ->  subprocesso  ->  COLLECT  ->  adaptador  ->  CDP
                        ->  envelope declarado  ->  ingresso  ->  recibo

O QUE É FALSO AQUI, E O QUE NÃO PODE SER
-----------------------------------------
Falso: **só o mundo lá fora**, e ele é UM: o **navegador**.

    Um servidor que fala DevTools numa porta de `127.0.0.1`. Ele responde
    `GET /json` e o WebSocket do CDP com sockets REAIS — `ferramentas/cdp.py`
    fala com ele exactamente como falaria com o Chrome, e não sabe a diferença.

    Enquanto ele estiver à escuta, `cdp.subir()` encontra a porta ocupada e
    NÃO abre navegador nenhum. Nenhum pacote sai desta máquina, e nenhuma
    página do instagram.com é pedida.

        META_REQUESTS = 0 · REAL_NETWORK = 0.

E ele é o mais fundo que existe: abaixo do socket só há o Chrome, e o Chrome é
que não queremos acordar.

    UM FAKE ACIMA DO GATE MEDE O FAKE.

Não é falso — e falsificá-lo invalidaria a prova inteira: `pedido`, `receitas`,
`orquestrador`, `scrap_executor`, `social_rotas`, `adaptador_instagram`,
`instagram_janela`, `orcamento_de_rede`, `relevancia_da_fonte`,
`retorno_da_coleta`, `ingresso`.

AS PROVAS
---------
    P0  a cadeia está ligada, e a escolha não depende da ordem da lista
    P1  POSITIVA · MUNDO FALSO — a cadeia inteira atravessa, e custa zero
    P2  NEGATIVA · RELEVÂNCIA — fonte barrada no livro não executa a rota
    P3  NEGATIVA · EXECUTOR — o pedido de outra fase não abre este executor
    P4  NEGATIVA · POLÍTICA — rota recusada não toca no navegador
    P5  NEGATIVA · EXECUÇÃO — porta fechada é ERRO, e nunca REJEITADO
    P6  NEGATIVA · OUTPUT — sem ficheiro não se declara payload preservado

A CASA FICA COMO ESTAVA
-----------------------
Tudo o que a cadeia escreve é fotografado antes e reposto depois, byte a byte.

    UMA PROVA QUE DEIXA OBSERVAÇÃO FALSA NO LIVRO DA CASA
    NÃO PROVOU A CASA: CONTAMINOU-A.

EXECUÇÃO REAL
-------------
    REAL_NETWORK = 0 · APIFY_REAL_RUNS = 0 · META_REAL_REQUESTS = 0
    PAID_REAL_RUNS = 0 · REAL_COST_USD = 0 · FONTES_AVALIADAS = 0
"""

import base64
import hashlib
import json
import os
import shutil
import socket
import struct
import sys
import threading

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

import pedido as ped                    # noqa: E402
import receitas as rec                  # noqa: E402
import orquestrador as orq              # noqa: E402
import relevancia_da_fonte as rel       # noqa: E402
import retorno_da_coleta as rdc         # noqa: E402

FALHAS = []
PROVAS = 0

CLI = os.path.join('coleta', 'social_scrap.py')
RETORNO = os.path.join('data', 'colheita', 'scrap', 'RETORNO.json')
GAVETA = os.path.join('data', 'samples', 'INSTAGRAM-JANELA')
FASE = 'janela-perfis'


def diz(ok, titulo, detalhe=''):
    global PROVAS
    PROVAS += 1
    print('  %s  %-52s %s' % ('OK   ' if ok else 'FALHA', titulo[:52], detalhe))
    if not ok:
        FALHAS.append('%s · %s' % (titulo, detalhe))
    return ok


# ══════════════════════════════════════════════════════════════════════════
# O MUNDO FALSO — um navegador que não existe, numa porta que existe
# ══════════════════════════════════════════════════════════════════════════
_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

#: A página que o navegador falso devolve. Ela NÃO é do instagram.com: é um
#: esqueleto escrito aqui, com o texto de que `JS_PERFIL` precisa.
HTML_FALSO = ('<html><head><title>Perfil falso da prova</title></head>'
              '<body>1.234 seguidores · 56 seguindo</body></html>')

#: O que o `Runtime.evaluate` do perfil devolve. Os nomes são os que
#: `instagram_janela.JS_PERFIL` declara — não se inventa campo nenhum.
PERFIL_FALSO = {
    'TITULO': 'Perfil falso da prova',
    'OG_DESCRIPTION': None,
    'SEGUIDORES_TEXTO': '1.234',
    'SEGUINDO_TEXTO': '56',
    'LINK_EXTERNO': None,
    'TEXTO_VISIVEL': 'nenhuma destas letras veio do instagram.com',
    'CODIGOS_NA_GRADE': ['p:FAKE0000001', 'p:FAKE0000002'],
    'ITENS_NA_GRADE': 2,
    'DESTAQUES': [],
    'MURO_DE_LOGIN': False,
    'PAGINA_NAO_ENCONTRADA': False,
}

#: 1x1 PNG. É prova de que a captura respondeu — nunca um retrato de nada.
PNG_FALSO = base64.b64decode(
    b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQ'
    b'AAAABJRU5ErkJggg==')


class NavegadorFalso(object):
    """Fala DevTools numa porta real. Não abre página nenhuma para o mundo.

    ⚠️ ELE REGISTA TUDO O QUE LHE PEDIRAM. É desse registo que as provas
    negativas leem «o navegador foi tocado?» — a medição está na camada mais
    funda, e não no que o runtime disse que fez.
    """

    def __init__(self):
        self.porta = None
        self.pedidos = []                 # (tipo, detalhe)
        self._srv = None
        self._fio = None
        self._parar = threading.Event()

    # ── ciclo de vida ────────────────────────────────────────────────────
    def __enter__(self):
        self._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind(('127.0.0.1', 0))
        self.porta = self._srv.getsockname()[1]
        self._srv.listen(16)
        self._srv.settimeout(0.4)
        self._fio = threading.Thread(target=self._servir, daemon=True)
        self._fio.start()
        return self

    def __exit__(self, *a):
        self._parar.set()
        self._fio.join(timeout=5)
        try:
            self._srv.close()
        except OSError:
            pass
        trava = os.path.join(os.path.expanduser('~'), '.sintonia-browser',
                             'porta-%d.dono' % self.porta)
        if os.path.isfile(trava):
            os.remove(trava)
        return False

    def tocado(self):
        return len(self.pedidos)

    def navegacoes(self):
        return [d for t, d in self.pedidos if t == 'Page.navigate']

    # ── o servidor ───────────────────────────────────────────────────────
    def _servir(self):
        while not self._parar.is_set():
            try:
                c, _ = self._srv.accept()
            except (socket.timeout, OSError):
                continue
            threading.Thread(target=self._atender, args=(c,), daemon=True).start()

    def _atender(self, c):
        try:
            c.settimeout(10)
            cab = b''
            while b'\r\n\r\n' not in cab:
                p = c.recv(4096)
                if not p:
                    return
                cab += p
            texto = cab.decode('latin-1')
            linha = texto.split('\r\n', 1)[0]
            if 'Upgrade: websocket' in texto or 'upgrade: websocket' in texto:
                return self._websocket(c, texto)
            self.pedidos.append(('HTTP', linha))
            if '/json' in linha:
                corpo = json.dumps([{
                    'id': 'FAKE-PAGE', 'type': 'page', 'url': 'about:blank',
                    'title': 'aba falsa da prova',
                    'webSocketDebuggerUrl':
                        'ws://127.0.0.1:%d/devtools/page/FAKE-PAGE' % self.porta,
                }]).encode('utf-8')
            else:
                corpo = b'{}'
            c.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n'
                      b'Content-Length: %d\r\n\r\n' % len(corpo) + corpo)
        except OSError:
            pass
        finally:
            try:
                c.close()
            except OSError:
                pass

    def _websocket(self, c, cabecalho):
        chave = ''
        for l in cabecalho.split('\r\n'):
            if l.lower().startswith('sec-websocket-key:'):
                chave = l.split(':', 1)[1].strip()
        aceite = base64.b64encode(
            hashlib.sha1((chave + _GUID).encode('ascii')).digest()).decode('ascii')
        c.sendall(('HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n'
                   'Connection: Upgrade\r\nSec-WebSocket-Accept: %s\r\n\r\n'
                   % aceite).encode('ascii'))
        while not self._parar.is_set():
            try:
                msg = self._receber(c)
            except (OSError, ValueError):
                return
            if msg is None:
                return
            try:
                m = json.loads(msg)
            except ValueError:
                continue
            self._enviar(c, json.dumps(self._responder(m)))

    def _responder(self, m):
        metodo, params = m.get('method'), (m.get('params') or {})
        self.pedidos.append((metodo, params.get('url') or params.get('expression', '')[:40]))
        if metodo == 'Runtime.evaluate':
            e = params.get('expression') or ''
            if 'outerHTML' in e:
                valor = HTML_FALSO
            elif 'CODIGOS_NA_GRADE' in e or 'ITENS_NA_GRADE' in e:
                valor = PERFIL_FALSO
            else:
                valor = None
            return {'id': m.get('id'), 'result': {'result': {'value': valor}}}
        if metodo == 'Page.captureScreenshot':
            return {'id': m.get('id'),
                    'result': {'data': base64.b64encode(PNG_FALSO).decode('ascii')}}
        return {'id': m.get('id'), 'result': {}}

    # ── enquadramento ────────────────────────────────────────────────────
    @staticmethod
    def _enviar(c, texto):
        d = texto.encode('utf-8')
        n = len(d)
        if n < 126:
            cab = struct.pack('!BB', 0x81, n)
        elif n < (1 << 16):
            cab = struct.pack('!BBH', 0x81, 126, n)
        else:
            cab = struct.pack('!BBQ', 0x81, 127, n)
        c.sendall(cab + d)

    @staticmethod
    def _exato(c, n):
        b = b''
        while len(b) < n:
            p = c.recv(n - len(b))
            if not p:
                raise OSError('ligacao fechada a meio do quadro')
            b += p
        return b

    def _receber(self, c):
        try:
            cab = self._exato(c, 2)
        except OSError:
            return None
        op = cab[0] & 0x0F
        if op == 0x8:
            return None
        mascarado = cab[1] & 0x80
        n = cab[1] & 0x7F
        if n == 126:
            n = struct.unpack('!H', self._exato(c, 2))[0]
        elif n == 127:
            n = struct.unpack('!Q', self._exato(c, 8))[0]
        chave = self._exato(c, 4) if mascarado else b'\0\0\0\0'
        dados = bytearray(self._exato(c, n))
        if mascarado:
            for i in range(n):
                dados[i] ^= chave[i % 4]
        return bytes(dados).decode('utf-8', 'replace')


# ══════════════════════════════════════════════════════════════════════════
# A CASA FICA COMO ESTAVA — medido, não prometido
# ══════════════════════════════════════════════════════════════════════════
#: Tudo o que a cadeia inteira escreve. Fotografado antes, reposto depois, e o
#: conteúdo conferido byte a byte no fim.
#:
#:     UMA PROVA QUE DEIXA OBSERVAÇÃO FALSA NO LIVRO DA CASA
#:     NÃO PROVOU A CASA: CONTAMINOU-A.
ESCRITOS_PELA_CADEIA = (
    os.path.join('data', 'samples', 'LIVRO-DE-DECISOES.json'),
    os.path.join(GAVETA, 'PERFIS.json'),
    RETORNO,
)
#: Pastas inteiras que a rota cria. O que não existia antes não fica depois.
PASTAS_DA_ROTA = (os.path.join(GAVETA, 'provas'),
                  os.path.join(GAVETA, 'html-bruto'))


class CasaIntacta(object):
    def __init__(self):
        self.antes = {}
        self.pastas = {}

    def __enter__(self):
        for rel_ in ESCRITOS_PELA_CADEIA:
            c = os.path.join(RAIZ, rel_)
            self.antes[rel_] = open(c, 'rb').read() if os.path.isfile(c) else None
        for rel_ in PASTAS_DA_ROTA:
            c = os.path.join(RAIZ, rel_)
            self.pastas[rel_] = (sorted(os.listdir(c)) if os.path.isdir(c)
                                 else None)
        return self

    def __exit__(self, *a):
        self.repor()
        return False

    def repor(self):
        for rel_, corpo in self.antes.items():
            c = os.path.join(RAIZ, rel_)
            if corpo is None:
                if os.path.isfile(c):
                    os.remove(c)
            else:
                os.makedirs(os.path.dirname(c), exist_ok=True)
                with open(c, 'wb') as f:
                    f.write(corpo)
        for rel_, tinha in self.pastas.items():
            c = os.path.join(RAIZ, rel_)
            if tinha is None:
                shutil.rmtree(c, ignore_errors=True)
            elif os.path.isdir(c):
                for n in os.listdir(c):
                    if n not in tinha:
                        os.remove(os.path.join(c, n))

    def confere(self):
        mal = []
        for rel_, corpo in self.antes.items():
            c = os.path.join(RAIZ, rel_)
            agora = open(c, 'rb').read() if os.path.isfile(c) else None
            if agora != corpo:
                mal.append(rel_)
        for rel_, tinha in self.pastas.items():
            c = os.path.join(RAIZ, rel_)
            agora = sorted(os.listdir(c)) if os.path.isdir(c) else None
            if agora != tinha:
                mal.append(rel_ + '/')
        return mal


CASA = CasaIntacta()


def pedido_com(**filtros):
    p = ped.de_uma_frase('colete concorrentes')
    p.filtros.update(filtros)
    return p


def ambiente_do_navegador(porta):
    """As variáveis que apontam a rota ao navegador FALSO. → o que restaurar."""
    antes = {}
    for k, v in (('IG_PORTA', str(porta)),
                 # A pausa entre contas é de cortesia com a plataforma. Contra um
                 # servidor local ela só faz a prova demorar — e uma prova lenta
                 # é uma prova que ninguém corre.
                 ('IG_PAUSA', '0'),
                 ('SUPABASE_DB_URL', '')):
        antes[k] = os.environ.get(k)
        os.environ[k] = v
    return antes


def repor_ambiente(antes):
    for k, v in antes.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def envelope_escrito():
    c = os.path.join(RAIZ, RETORNO)
    return json.load(open(c, encoding='utf-8')) if os.path.isfile(c) else {}


# ══════════════════════════════════════════════════════════════════════════
# P0 · A CADEIA ESTÁ LIGADA, E A ORDEM NÃO DECIDE
# ══════════════════════════════════════════════════════════════════════════
def p0_a_cadeia_esta_ligada():
    print('\nP0 · A CADEIA ESTÁ LIGADA, E A ORDEM NÃO DECIDE\n' + '-' * 72)
    T9 = rec.EXECUTORES['T9']
    e = rec.resolver(pedido_com(fase=FASE)).escolhido or {}
    diz(e.get('id') == 'scrap-janela',
        'o PEDIDO escolhe o executor da janela', e.get('id'))
    diz(e.get('custo') == 'gratuito' and rel.custo_e_gratuito(e.get('custo')),
        'e ele declara-se GRATUITO na língua do dono da lei', e.get('custo'))
    diz(e.get('aceita_fonte') is False,
        'e declara que NÃO aceita fonte — as contas não têm ficha')

    # ── A ORDEM DA LISTA NÃO PODE DECIDIR ────────────────────────────────
    # Dois candidatos falsos, um antes e outro depois, com selectores que NÃO
    # casam. Se a escolha dependesse do índice, qualquer um deles ganhava.
    falso_a = {'id': 'falso-antes', 'roda': ['x'], 'rotas': [], 'custo': 'gratuito',
               'o_que_traz': '', 'pedido_pede': {'fase': 'nunca-pedida-a'}}
    falso_b = {'id': 'falso-depois', 'roda': ['y'], 'rotas': [], 'custo': 'gratuito',
               'o_que_traz': '', 'pedido_pede': {'fase': 'nunca-pedida-b'}}
    p = pedido_com(fase=FASE)
    escolhas = {
        'antes':  rec.escolher([falso_a] + list(T9), p),
        'depois': rec.escolher(list(T9) + [falso_b], p),
        'ambos':  rec.escolher([falso_a] + list(T9) + [falso_b], p),
        'invertida': rec.escolher(list(reversed(T9)), p),
    }
    diz(all(x and x['id'] == 'scrap-janela' for x in escolhas.values()),
        'com quatro ordens diferentes, a escolha é a mesma',
        ' · '.join('%s=%s' % (k, (v or {}).get('id')) for k, v in escolhas.items()))
    diz(rec.escolher([falso_a, falso_b], pedido_com(fase=FASE)) is None,
        'e nenhum candidato com selector é escolhido por omissão')

    # ── O PORTÃO É CONSULTADO, E DEIXA PASSAR — SEM GASTO ────────────────
    plano = rec.resolver(pedido_com(fase=FASE))
    r = plano.relevancia
    diz(r.get('VEREDITO') == rel.EXIGE_AVALIACAO,
        'o portão foi consultado e respondeu', r.get('VEREDITO'))
    diz(plano.bloqueia_a_corrida is False,
        'e NÃO barra: rota gratuita não abre forma de gasto nenhuma',
        str(r.get('FORMAS_DE_GASTO_ABERTAS')))
    diz(r.get('SOURCE_ID') is None,
        'e o plano não nomeia fonte nenhuma — nem inventa uma')


# ══════════════════════════════════════════════════════════════════════════
# P1 · POSITIVA · MUNDO FALSO — a cadeia inteira atravessa, e custa zero
# ══════════════════════════════════════════════════════════════════════════
def p1_positiva():
    print('\nP1 · POSITIVA · MUNDO FALSO\n' + '-' * 72)
    with NavegadorFalso() as nav:
        antes = ambiente_do_navegador(nav.porta)
        try:
            recibo = orq.correr(pedido_com(fase=FASE))
            recibo.pop('_plano', None)
        finally:
            repor_ambiente(antes)

        # ── O CAMINHO ────────────────────────────────────────────────────
        diz(recibo['STATUS'] == 'SUCCESS', 'a corrida terminou em SUCCESS',
            '%s · %s' % (recibo['STATUS'], (recibo['ERROR'] or '')[:60]))
        diz(recibo['ACTOR'] == CLI, 'quem correu foi a CLI do SCRAP', recibo['ACTOR'])
        diz('coletar %s' % FASE in recibo['COMANDO'],
            'e a fase veio do PEDIDO, não de quem chamou', recibo['COMANDO'])
        diz(recibo['CAPTURE_METHOD'] == 'gratuito',
            'o recibo diz que a captura foi GRATUITA', recibo['CAPTURE_METHOD'])
        diz(recibo['COST_USD'] == 0,
            'e o custo é ZERO MEDIDO, não «NAO SEI»', repr(recibo['COST_USD']))

        # ── O RUN É UM SÓ ────────────────────────────────────────────────
        env = envelope_escrito()
        corridas = {recibo['RUN_ID'], str(env.get('RUN_ID') or '')}
        corridas |= {str(u.get('RUN_ID')) for u in (env.get('COLHEITA') or [])}
        diz('--run-id=%s' % recibo['RUN_ID'] in recibo['COMANDO'],
            'a corrida cunhada pelo orquestrador desceu ao executor',
            recibo['RUN_ID'])
        diz(len(corridas) == 1,
            'UM só RUN_ID do princípio ao fim — nem dois, nem nenhum',
            ' · '.join(sorted(corridas)))

        # ── O QUE A CORRIDA DECLAROU ─────────────────────────────────────
        diz(bool(env), 'a corrida DECLAROU o que produziu (COL-LAW-505)', RETORNO)
        diz(env.get('ESTADO') == 'SUCCESS', 'e o envelope diz SUCCESS',
            str(env.get('ESTADO')))
        n = len(env.get('COLHEITA') or [])
        diz(n >= 1, 'com colheita declarada, unidade a unidade', '%d unidade(s)' % n)
        diz(rdc.conferir(env, RAIZ) == [],
            'e o envelope respeita o contrato do retorno',
            ' · '.join(rdc.conferir(env, RAIZ))[:80])
        origens = {u.get('SOURCE_ID') for u in (env.get('COLHEITA') or [])}
        diz(origens == {'INSTAGRAM-JANELA/PERFIS'},
            'cada unidade traz a origem que o ARTEFATO declara', str(origens))
        docs = [u.get('DOCUMENT_ID') for u in (env.get('COLHEITA') or [])]
        diz(all(d and d != rdc.NAO_SEI for d in docs),
            'e a identidade é a da plataforma, nunca derivada', str(docs[:3]))
        diz(recibo.get('COLHEITA_ENCONTRADA') == n,
            'o orquestrador encontrou o que a corrida declarou',
            str(recibo.get('COLHEITA_ENCONTRADA')))
        diz('INGRESSO' in recibo,
            'e a colheita foi à PORTA DE ENTRADA antes de alguém a julgar')

        # ── O OUTPUT, E OS BYTES ─────────────────────────────────────────
        perfis = os.path.join(RAIZ, GAVETA, 'PERFIS.json')
        diz(os.path.isfile(perfis), 'o artefato da rota existe em disco',
            os.path.join(GAVETA, 'PERFIS.json'))
        d = json.load(open(perfis, encoding='utf-8')) if os.path.isfile(perfis) else {}
        diz(d.get('SOURCE_ID') == 'INSTAGRAM-JANELA/PERFIS',
            'e é ele que declara a origem — não este ficheiro',
            str(d.get('SOURCE_ID')))
        diz(d.get('APIFY_RUNS') == 0 and d.get('COST_USD') == 0,
            'o artefato declara zero provider e zero dólares')
        lidos = [i for i in (d.get('ITEMS') or [])
                 if i.get('DOOR_STATE') == 'PAGE_RENDERED']
        diz(bool(lidos), 'e a porta do navegador ABRIU nesta corrida',
            '%d de %d contas' % (len(lidos), len(d.get('ITEMS') or [])))
        brutos = [i.get('RAW_HTML_PATH') for i in lidos if i.get('RAW_HTML_PATH')]
        existe = [b for b in brutos
                  if os.path.isfile(os.path.join(RAIZ, b))]
        diz(len(existe) == len(brutos) and brutos,
            'o RAW da página foi escrito, e está onde ele diz que está',
            '%d ficheiro(s)' % len(existe))
        if existe:
            # ── RAW RELIDO, E NÃO APENAS ESCRITO ──────────────────────────
            # O bruto vai comprimido — `instagram_janela._guardar_html` fecha-o
            # em gzip, e é assim que ele existe. Reler significa abri-lo como
            # ele É, e não como seria cómodo para esta prova.
            #
            #     DECLARAR UM CAMINHO NÃO É CONFIRMAR OS BYTES.
            import gzip
            caminho = os.path.join(RAIZ, existe[0])
            sha = hashlib.sha256(open(caminho, 'rb').read()).hexdigest()
            with gzip.open(caminho, 'rt', encoding='utf-8') as f:
                corpo = f.read()
            diz(corpo == HTML_FALSO,
                'e relido é exactamente o que o navegador falso devolveu',
                'sha256 %s' % sha[:12])
            diz(len(sha) == 64, 'o RAW tem SHA-256 calculado sobre os bytes')

        # ── E O MUNDO? ───────────────────────────────────────────────────
        diz(nav.tocado() > 0, 'o navegador falso foi mesmo usado',
            '%d pedido(s) CDP' % nav.tocado())
        alvos = nav.navegacoes()
        diz(bool(alvos) and all('instagram.com' in u for u in alvos),
            'e as navegações foram para as contas do lote — contra o FALSO',
            '%d navegação(ões)' % len(alvos))
        CASA.repor()


# ══════════════════════════════════════════════════════════════════════════
# AS NEGATIVAS — e a medida que não se discute é o navegador falso
# ══════════════════════════════════════════════════════════════════════════
#     FREE_ROUTE != NO_GATES.
#
# Uma rota que não gasta dinheiro continua a obedecer à política, ao portão da
# fonte e ao teto de acessos. Cada negativa abaixo exige as duas coisas: a
# recusa TEM nome próprio, e o navegador NÃO é tocado.
RECEITAS = os.path.join('pedido', 'receitas.py')
MATRIZ = os.path.join('leis', 'social_matriz.py')


def _sha(caminho):
    with open(caminho, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


class Mutante(object):
    """Altera UM ficheiro real, e repõe-no sempre — inclusive a rebentar."""

    def __init__(self, rel_, onde, para):
        self.caminho = os.path.join(RAIZ, rel_)
        self.onde, self.para = onde, para
        self.original = None
        self.aplicou = False

    def __enter__(self):
        self.original = open(self.caminho, encoding='utf-8').read()
        self.sha = _sha(self.caminho)
        if self.original.count(self.onde) != 1:
            # ÂNCORA QUE NÃO É ÚNICA NÃO É MUTANTE MORTO: a mutação nem chegou
            # a aplicar-se, e contá-la como defesa seria fabricar contagem.
            return self
        with open(self.caminho, 'w', encoding='utf-8') as f:
            f.write(self.original.replace(self.onde, self.para, 1))
        self.aplicou = True
        return self

    def __exit__(self, *a):
        with open(self.caminho, 'w', encoding='utf-8') as f:
            f.write(self.original)
        if _sha(self.caminho) != self.sha:
            raise SystemExit('3 · o ficheiro NÃO ficou como estava: %s'
                             % self.caminho)
        return False


def _correr_contra_o_falso(p, **kw):
    """Corre a cadeia canónica contra o navegador falso. → (recibo, navegador)."""
    with NavegadorFalso() as nav:
        antes = ambiente_do_navegador(nav.porta)
        try:
            recibo = orq.correr(p, **kw)
            recibo.pop('_plano', None)
        finally:
            repor_ambiente(antes)
        CASA.repor()
        return recibo, nav


def livro_que_barra(sid):
    """Um livro de FIXTURE com UM «NÃO» sobre UMA fonte obviamente falsa.

    ⚠️ NÃO É O LIVRO DESTA CASA, e a fonte não é nenhuma das 77. Esta missão
    não avalia fonte nenhuma: ela só exercita o dono da lei com uma entrada.
    """
    return [rel.Decisao(
        source_id=sid, proposito='T9', resultado=rel.NAO,
        motivo='fonte INVENTADA por provas/o_fluxo_gratuito_do_scrap.py para '
               'exercitar o portao. NAO e uma fonte desta casa.',
        metodo='FIXTURE_DE_PROVA_OFFLINE',
        evidencia={'ONDE': 'provas/o_fluxo_gratuito_do_scrap.py'},
        corrida='NAO SEI').para_livro()]


def p2_relevancia():
    print('\nP2 · NEGATIVA · RELEVÂNCIA — grátis não é sem portão\n' + '-' * 72)
    # Para o portão ter par que julgar, esta rota teria de aceitar fonte. Ela
    # NÃO aceita — e é isso que o mutante troca, para perguntar: se aceitasse,
    # um «NÃO» no livro parava a corrida antes do navegador?
    with Mutante(RECEITAS, '"aceita_fonte": False,', '"aceita_fonte": True,') as m:
        if not m.aplicou:
            return diz(False, 'P2 · âncora do mutante não é única')
        import importlib
        importlib.reload(rec)
        importlib.reload(orq)
        try:
            p = pedido_com(fase=FASE, fonte='fake~fonte-barrada-da-prova')
            recibo, nav = _correr_contra_o_falso(p, livro=livro_que_barra(
                'fake~fonte-barrada-da-prova'))
            diz(recibo['STATUS'] == 'BARRADO_NA_RELEVANCIA',
                'um NÃO no livro barra a corrida GRATUITA', recibo['STATUS'])
            diz(recibo['RELEVANCIA_DA_FONTE']['VEREDITO'] == rel.BARRA,
                'e a recusa tem o nome do dono da lei',
                recibo['RELEVANCIA_DA_FONTE']['VEREDITO'])
            diz(nav.tocado() == 0,
                'e o navegador NÃO foi tocado', '%d pedido(s) CDP' % nav.tocado())
            diz(recibo.get('COST_USD') == 0,
                'nada correu, nada custou', repr(recibo.get('COST_USD')))
        finally:
            pass
    import importlib
    importlib.reload(rec)
    importlib.reload(orq)


def p3_executor():
    print('\nP3 · NEGATIVA · EXECUTOR — o pedido de outra fase não abre este\n'
          + '-' * 72)
    with NavegadorFalso() as nav:
        antes = ambiente_do_navegador(nav.porta)
        try:
            plano = rec.resolver(pedido_com(fase='yt-legenda-paga'))
        finally:
            repor_ambiente(antes)
        diz(plano.escolhido['id'] == 'scrap-yt-legenda-paga',
            'a fase paga continua a abrir o executor dela',
            plano.escolhido['id'])
        diz(rec.resolver(pedido_com()).escolhido['id'] == 'comunicacao-publica',
            'e quem não nomeia fase leva o executor de sempre')
        diz(rec.escolher(rec.EXECUTORES['T9'],
                         pedido_com(fase='janela-que-nao-existe'))['id']
            == 'comunicacao-publica',
            'uma fase parecida mas diferente NÃO abre a janela')
        diz(nav.tocado() == 0,
            'e escolher executor não toca no navegador',
            '%d pedido(s) CDP' % nav.tocado())


def p4_politica():
    print('\nP4 · NEGATIVA · POLÍTICA — recusa não toca no mundo\n' + '-' * 72)
    with Mutante(MATRIZ,
                 "r('instagram_janela.py:grade', 'PUBLIC_BROWSER', 'CONDICIONAL', 'PROVED', 'zero',",
                 "r('instagram_janela.py:grade', 'PUBLIC_BROWSER', 'NAO', 'PROVED', 'zero',") as m:
        if not m.aplicou:
            return diz(False, 'P4 · âncora do mutante não é única')
        recibo, nav = _correr_contra_o_falso(pedido_com(fase=FASE))
        saida = (recibo.get('SAIDA') or '')
        diz('ROUTE_NOT_ALLOWED' in saida or 'AUTOMATION_NOT_ALLOWED' in saida,
            'a política recusou, e a recusa tem nome próprio',
            'ROUTE_NOT_ALLOWED' if 'ROUTE_NOT_ALLOWED' in saida else saida[-60:])
        diz(nav.tocado() == 0,
            'e o navegador NÃO foi tocado', '%d pedido(s) CDP' % nav.tocado())


def p5_execucao():
    print('\nP5 · NEGATIVA · EXECUÇÃO — porta fechada é ERRO, nunca REJEITADO\n'
          + '-' * 72)
    # Nenhum navegador falso: a porta aponta para o vazio. É a diferença entre
    # «a conta não publica» e «a minha ponta não abriu».
    livre = socket.socket()
    livre.bind(('127.0.0.1', 0))
    porta = livre.getsockname()[1]
    livre.close()
    antes = ambiente_do_navegador(porta)
    try:
        recibo = orq.correr(pedido_com(fase=FASE))
        recibo.pop('_plano', None)
    finally:
        repor_ambiente(antes)
    env = envelope_escrito()
    # ⚠️ O QUE ACONTECE AQUI FOI MEDIDO, E NÃO É O QUE EU ESPERAVA.
    # `instagram_janela.perfis()` sabe escrever `BROWSER_NOT_REACHED` por conta
    # — mas só chega lá quando a porta RESPONDE e a aba é que não abre. Sem
    # navegador nenhum nesta máquina, quem levanta primeiro é `cdp.subir`, e a
    # rota falha ANTES de escrever registo de conta nenhuma.
    #
    # O que esta prova exige é a parte que importa, e ela vale nos dois casos:
    #
    #     FALHA DE AMBIENTE NÃO VIRA COLHEITA VAZIA, E NÃO VIRA REJEIÇÃO.
    diz(str(env.get('ESTADO')) == 'FAILED',
        'a corrida declara FAILED — e não SUCCESS com zero', str(env.get('ESTADO')))
    diz(bool(env.get('ERROS')),
        'com o motivo escrito: uma falha sem motivo é um rótulo',
        str((env.get('ERROS') or [''])[0])[:70])
    diz('EXECUTOR_UNAVAILABLE' in str(env.get('ERROS')),
        'e a falha diz QUE ferramenta faltou — não «UNKNOWN_ERROR»',
        str((env.get('ERROS') or [''])[0])[:46])
    diz((env.get('COLHEITA') or []) == [],
        'e zero colheita — nada foi inventado para o número fechar')
    diz(recibo.get('ESTADO_DOS_ITENS') != 'REJEITADO',
        'o recibo NÃO chama a isto rejeição', str(recibo.get('ESTADO_DOS_ITENS')))
    diz(recibo.get('ESTADO_DOS_ITENS') == 'ERRO',
        'chama-lhe ERRO: ninguém chegou a olhar para a fonte',
        str(recibo.get('ESTADO_DOS_ITENS')))
    CASA.repor()


def p6_output():
    print('\nP6 · NEGATIVA · OUTPUT — sem ficheiro não há payload preservado\n'
          + '-' * 72)
    # O estado do payload é MEDIDO contra a árvore, nunca afirmado. Estas três
    # perguntas são feitas ao dono da lei, com o caminho que a corrida daria.
    diz(rdc.estado_do_payload(None, RAIZ) == rdc.PAYLOAD_NAO_SE_APLICA,
        'sem caminho declarado, o payload NÃO SE APLICA',
        rdc.estado_do_payload(None, RAIZ))
    diz(rdc.estado_do_payload('data/nao-existe/ficheiro.gz', RAIZ) == rdc.AUSENTE,
        'com caminho declarado e ficheiro ausente, AUSENTE — nunca PRESENTE',
        rdc.estado_do_payload('data/nao-existe/ficheiro.gz', RAIZ))
    mentiroso = {'RUN_ID': 'R1', 'EXECUTOR_ID': 'x', 'EXECUTOR_VERSION': 'v',
                 'ESTADO': 'SUCCESS', 'SUPORTE': [], 'ERROS': [],
                 'COLHEITA': [{'ESPECIE': rdc.COLHEITA, 'SOURCE_ID': 'X/Y',
                               'DOCUMENT_ID': 'abc', 'RUN_ID': 'R1',
                               'PAYLOAD': {'ESTADO': rdc.PRESENTE,
                                           'ONDE': 'data/nao-existe/ficheiro.gz'}}]}
    diz(rdc.conferir(mentiroso, RAIZ) != [],
        'e um envelope que AFIRMA preservado sem bytes é recusado',
        (rdc.conferir(mentiroso, RAIZ) or [''])[0][:60])
    # E o caso REAL desta rota: ela não declara RAW forward, e por isso as
    # unidades dizem NAO_SE_APLICA — que é a verdade, e não um silêncio.
    with NavegadorFalso() as nav:
        antes = ambiente_do_navegador(nav.porta)
        try:
            orq.correr(pedido_com(fase=FASE)).pop('_plano', None)
        finally:
            repor_ambiente(antes)
        env = envelope_escrito()
        estados = {(u.get('PAYLOAD') or {}).get('ESTADO')
                   for u in (env.get('COLHEITA') or [])}
        diz(estados and estados <= set(rdc.ESTADOS_DO_PAYLOAD),
            'as unidades desta rota declaram o payload que MEDIRAM', str(estados))
        CASA.repor()


if __name__ == '__main__':
    print('=' * 72)
    print('UMA ROTA GRATUITA ATRAVESSA O FLUXO CANÓNICO? — prova offline')
    print('=' * 72)
    with CASA:
        try:
            p0_a_cadeia_esta_ligada()
            p1_positiva()
            p2_relevancia()
            p3_executor()
            p4_politica()
            p5_execucao()
            p6_output()
        finally:
            CASA.repor()

    print('\nA CASA FICOU COMO ESTAVA\n' + '-' * 72)
    sujos = CASA.confere()
    diz(not sujos, 'os livros e as gavetas voltaram ao que eram',
        ', '.join(sujos) if sujos else '%d caminho(s) conferido(s)'
        % (len(ESCRITOS_PELA_CADEIA) + len(PASTAS_DA_ROTA)))

    print('\nEXECUÇÃO REAL\n' + '-' * 72)
    print('  REAL_NETWORK         = 0  (o navegador desta prova é um socket local)')
    print('  META_REAL_REQUESTS   = 0  (nenhuma página do instagram.com foi pedida)')
    print('  APIFY_REAL_RUNS      = 0')
    print('  PAID_REAL_RUNS       = 0')
    print('  REAL_COST_USD        = 0')
    print('  FONTES_AVALIADAS     = 0  (o livro desta casa não foi tocado)')

    print('\n' + '=' * 72)
    print('PROVAS = %d · FALHAS = %d' % (PROVAS, len(FALHAS)))
    if FALHAS:
        for f in FALHAS:
            print('  !!', f)
        raise SystemExit(1)
    print('FLUXO_GRATUITO = PASS')
