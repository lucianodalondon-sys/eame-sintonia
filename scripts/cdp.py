#!/usr/bin/env python3
"""
CDP — falar com o Chrome QUE JÁ ESTÁ ABERTO, pela porta de depuração dele.

    py scripts/cdp.py https://exemplo.invalid          # abre, lê e imprime o tamanho

POR QUE ISTO EXISTE, E POR QUE EM BIBLIOTECA PADRÃO
-----------------------------------------------------
Esta casa tem uma rota medida que nenhuma outra substitui: **Chrome com janela**.
`scripts/navegador.py` documenta a medição contra a ADAMA em 2026-08-30 —

    curl com User-Agent de Chrome ....... HTTP 403, 143 bytes
    chrome --headless=new --dump-dom .... HTTP 403, 186 bytes
    chrome com janela, via DevTools ..... a página francesa inteira

e a Biblioteca de Anúncios da Meta repetiu a mesma fronteira em 30-31/08.
`navegador.py` sabe ACHAR o Chrome e montar a linha de comando com
`--remote-debugging-port`. Faltava a outra metade: **conversar** com ele depois de
aberto. Até hoje cada missão resolvia isso à mão, e o código não era compartilhado.

Em biblioteca padrão porque o repositório **não tem `requirements.txt`**. Ganhar uma
dependência para abrir um socket é caro: quebra em runner novo, atrasa coleta paga e
introduz uma versão a mais para divergir entre as duas máquinas.

O QUE ESTE MÓDULO NÃO FAZ, E É DECISÃO
----------------------------------------
Não faz login. Não lê nem escreve cookie. Não resolve CAPTCHA. Não desliga sandbox.
Não passa credencial. Ele abre uma página pública no navegador da própria pessoa e
lê o que a tela mostra — é o mesmo programa que qualquer um usa para ler a página.

    LER PÁGINA PÚBLICA COM O NAVEGADOR ≠ BURLAR PROTEÇÃO.

E a lei que vem junto, herdada da rota da ADAMA:

    ROUTE_BLOCKED_FOR_AUTOMATION ≠ CATALOG_EMPTY

Um 403 mede o que o servidor respondeu ao MEU pedido. Não mede o que existe do outro
lado. `abrir()` devolve o ESTADO da porta, e nunca converte porta fechada em vazio.

O PROTOCOLO, EM DUAS FRASES
-----------------------------
O Chrome publica um catálogo em `http://127.0.0.1:<porta>/json` dizendo que abas
existem e qual o endereço de WebSocket de cada uma. Pelo WebSocket se mandam comandos
em JSON (`Page.navigate`, `Runtime.evaluate`) e se recebem as respostas — cada uma com
o `id` que a pergunta levou, porque as respostas voltam fora de ordem.
"""
import base64
import json
import os
import socket
import struct
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import navegador  # noqa: E402

# Estados da porta. São ESTADOS, não graus de fracasso — cada um pede uma conduta
# diferente de quem chama, e nenhum deles significa "não existe do outro lado".
PAGE_RENDERED = 'PAGE_RENDERED'
LOGIN_WALL = 'LOGIN_WALL'
NOT_FOUND = 'NOT_FOUND'
BROWSER_NOT_REACHED = 'BROWSER_NOT_REACHED'
NAVIGATION_FAILED = 'NAVIGATION_FAILED'


# ─────────────────────────────────────────────────────── WebSocket em socket puro
class Erro(Exception):
    """Falha de transporte com o navegador. Nunca é conclusão sobre a página."""


def _handshake(host, porta, caminho, timeout):
    s = socket.create_connection((host, porta), timeout=timeout)
    chave = base64.b64encode(os.urandom(16)).decode()
    pedido = (
        'GET %s HTTP/1.1\r\n'
        'Host: %s:%d\r\n'
        'Upgrade: websocket\r\n'
        'Connection: Upgrade\r\n'
        'Sec-WebSocket-Key: %s\r\n'
        'Sec-WebSocket-Version: 13\r\n\r\n' % (caminho, host, porta, chave))
    s.sendall(pedido.encode())
    # Ler só até o fim do cabeçalho: o que vier depois já é quadro e não pode ser comido.
    cab = b''
    while b'\r\n\r\n' not in cab:
        p = s.recv(1)
        if not p:
            raise Erro('o navegador fechou a conexão durante o aperto de mão')
        cab += p
    if b'101' not in cab.split(b'\r\n')[0]:
        raise Erro('o navegador recusou o WebSocket: %s'
                   % cab.split(b'\r\n')[0].decode('utf-8', 'replace'))
    return s


def _enviar(s, texto):
    """Um quadro de texto, mascarado. Cliente SEMPRE mascara — o servidor recusa se não."""
    dados = texto.encode('utf-8')
    n = len(dados)
    cab = bytearray([0x81])                       # FIN=1, opcode=1 (texto)
    if n < 126:
        cab.append(0x80 | n)
    elif n < (1 << 16):
        cab.append(0x80 | 126)
        cab += struct.pack('>H', n)
    else:
        cab.append(0x80 | 127)
        cab += struct.pack('>Q', n)
    mascara = os.urandom(4)
    cab += mascara
    s.sendall(bytes(cab) + bytes(b ^ mascara[i % 4] for i, b in enumerate(dados)))


def _ler_exato(s, n):
    buf = b''
    while len(buf) < n:
        p = s.recv(min(65536, n - len(buf)))
        if not p:
            raise Erro('o navegador fechou a conexão no meio de um quadro')
        buf += p
    return buf


def _receber(s):
    """Um quadro completo. Junta continuação e responde ping — senão a conexão morre.

    O HTML de uma página real passa de 800 mil bytes e chega picado em vários quadros.
    Ler só o primeiro devolveria um pedaço de JSON que nem `json.loads` aceita — e isso
    se leria como "o navegador não respondeu".
    """
    partes, opcode = [], None
    while True:
        b1, b2 = _ler_exato(s, 2)
        fin, op, n = b1 & 0x80, b1 & 0x0F, b2 & 0x7F
        if n == 126:
            n = struct.unpack('>H', _ler_exato(s, 2))[0]
        elif n == 127:
            n = struct.unpack('>Q', _ler_exato(s, 8))[0]
        corpo = _ler_exato(s, n) if n else b''
        if op == 0x9:                                        # ping → pong, e segue
            s.sendall(bytes([0x8A, 0x80]) + os.urandom(4))
            continue
        if op == 0x8:
            raise Erro('o navegador encerrou a conexão')
        if op in (0x1, 0x2):
            opcode = op
        partes.append(corpo)
        if fin:
            break
    bruto = b''.join(partes)
    return bruto.decode('utf-8', 'replace') if opcode != 0x2 else bruto


class Aba:
    """Uma aba do Chrome. Cada comando leva um `id` e a resposta é casada por ele."""

    def __init__(self, ws_url, timeout=60):
        if not ws_url.startswith('ws://'):
            raise Erro('endereço de WebSocket inesperado: %s' % ws_url[:60])
        resto = ws_url[len('ws://'):]
        hostporta, _, caminho = resto.partition('/')
        host, _, porta = hostporta.partition(':')
        self._s = _handshake(host, int(porta or 80), '/' + caminho, timeout)
        self._n = 0

    def comando(self, metodo, **params):
        self._n += 1
        meu = self._n
        _enviar(self._s, json.dumps({'id': meu, 'method': metodo, 'params': params}))
        # As respostas voltam fora de ordem, e no meio delas vêm EVENTOS (sem `id`).
        # Casar pelo `id` é o que impede ler a resposta de outra pergunta.
        while True:
            m = json.loads(_receber(self._s))
            if m.get('id') != meu:
                continue
            if 'error' in m:
                raise Erro('%s recusado: %s' % (metodo, str(m['error'])[:200]))
            return m.get('result') or {}

    def js(self, expressao, timeout_ms=30000):
        """Avalia e devolve o valor. `await` no topo funciona.

        O erro carrega a mensagem REAL da página. A primeira versão relatava só
        `exceptionDetails.text`, que no Chrome é a palavra `"Uncaught"` — literalmente
        isso, sem o motivo. Um relatório dizendo "o JavaScript lançou: Uncaught" é
        indistinguível de um navegador mudo, e mandaria quem depura procurar defeito de
        conexão onde havia erro de sintaxe. O motivo está em
        `exceptionDetails.exception.description`, e a linha em `lineNumber`.
        """
        r = self.comando('Runtime.evaluate', expression=expressao,
                         returnByValue=True, awaitPromise=True,
                         timeout=timeout_ms)
        det = r.get('exceptionDetails')
        if det:
            excecao = det.get('exception') or {}
            motivo = (excecao.get('description') or excecao.get('value')
                      or det.get('text') or 'sem descrição')
            raise Erro('o JavaScript da página lançou (linha %s, coluna %s): %s'
                       % (det.get('lineNumber'), det.get('columnNumber'),
                          str(motivo)[:400]))
        return (r.get('result') or {}).get('value')

    def fechar(self):
        try:
            self._s.close()
        except OSError:
            pass


# ────────────────────────────────────────────────────────────── catálogo de abas
def abas(porta, timeout=10):
    """→ lista de abas publicadas pelo Chrome, ou levanta `Erro` com o motivo."""
    try:
        with urllib.request.urlopen('http://127.0.0.1:%d/json' % porta,
                                    timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise Erro('não achei Chrome escutando na porta %d (%s: %s). '
                   'Ele foi aberto com --remote-debugging-port=%d?'
                   % (porta, type(e).__name__, str(e)[:80], porta))


def _ultima_linha(arquivo):
    """A última coisa que o navegador imprimiu antes de morrer, ou por que não deu para ler."""
    try:
        arquivo.flush()
        arquivo.seek(0)
        linhas = [l.strip() for l in arquivo.read().splitlines() if l.strip()]
    except (OSError, ValueError) as e:
        return '(não consegui ler o que ele imprimiu: %s)' % type(e).__name__
    return linhas[-1][:300] if linhas else '(nada em stderr)'


def _descartar(arquivo):
    """Some com o registro de stderr quando o navegador subiu — ninguém vai lê-lo."""
    try:
        arquivo.close()
        os.unlink(arquivo.name)
    except OSError:
        pass


def subir(porta, *, perfil=None, url='about:blank', segundos=25):
    """Abre o Chrome com janela nesta porta, se ainda não houver um. Devolve o processo.

    Reusa o que já está aberto: subir um segundo Chrome no MESMO perfil não abre uma
    segunda instância — ele conversa com a primeira e a porta nova nunca escuta. É o que
    a memória desta casa registra sobre duas sessões dividindo perfil e porta 9222.
    """
    import subprocess
    aviso = tomar_porta(porta, quem=os.path.basename(sys.argv[0] or 'cdp'))
    if aviso:
        print('  ⚠️  %s' % aviso)
    try:
        abas(porta, timeout=3)
        return None                                   # já tem um; não abrir outro
    except Erro:
        pass
    achado = navegador.descobrir()
    if not achado['FOUND']:
        raise Erro('sem Chrome nesta máquina: %s' % achado.get('WHY'))
    args = navegador.argumentos(url, perfil=perfil, porta_devtools=porta)
    # O QUE O CHROME DISSE ANTES DE MORRER — 2026-09-04
    # ------------------------------------------------
    # Isto aqui mandava stdout E stderr para DEVNULL, e o laço abaixo nunca perguntava
    # se o processo ainda estava vivo. Num contêiner rodando como root, o Chromium morre
    # em 0,4 s dizendo, textualmente:
    #
    #     Running as root without --no-sandbox is not supported.
    #
    # Essa frase ia para o lixo. O laço dormia os 25 s inteiros esperando uma porta que
    # nunca ia abrir e depois AFIRMAVA algo falso — "o Chrome subiu mas a porta não
    # passou a escutar" —, mandando o operador caçar defeito de rede onde havia binário
    # que se recusou a iniciar. Numa passada de 240 vídeos isso são ~100 minutos de
    # silêncio enganoso: foi exatamente assim que a camada de legendas "não completou".
    #
    #     PROCESSO MORTO ≠ PORTA LENTA.
    #
    # stderr vai para arquivo, não para PIPE: um pipe de 64 KB não drenado travaria o
    # navegador VIVO — o mesmo bug, pior. E o arquivo sobrevive (delete=False) porque
    # quem lê o erro é gente, depois.
    import tempfile
    registro = tempfile.NamedTemporaryFile('w+', prefix='chrome-%d-' % porta,
                                           suffix='.err', delete=False)
    p = subprocess.Popen([achado['EXECUTABLE']] + args,
                         stdout=subprocess.DEVNULL, stderr=registro)
    inicio = time.time()
    fim = inicio + segundos
    while time.time() < fim:
        try:
            abas(porta, timeout=2)
            _descartar(registro)              # subiu: o registro de erro não serve a ninguém
            return p
        except Erro:
            if p.poll() is not None:          # morreu: esperar mais não muda nada
                raise Erro(
                    'o Chrome NÃO subiu: morreu em %.1fs com código %s, sem abrir a '
                    'porta %d. Ele disse: %s (saída completa em %s)'
                    % (time.time() - inicio, p.returncode, porta,
                       _ultima_linha(registro), registro.name))
            time.sleep(1)
    raise Erro('o Chrome está vivo mas a porta %d não passou a escutar em %ds '
               '(o que ele imprimiu está em %s)' % (porta, segundos, registro.name))


def _aba_de_pagina(porta):
    for a in abas(porta):
        if a.get('type') == 'page' and a.get('webSocketDebuggerUrl'):
            return a
    raise Erro('o Chrome da porta %d não tem nenhuma aba de página aberta' % porta)


# ── UM DONO POR PORTA ───────────────────────────────────────────────────────────
# Escrito depois de eu mesmo cometer o erro, em 2026-09-02: a passada diária estava
# rodando na porta 9226 e eu disparei uma sonda de destaques na MESMA porta, com o
# MESMO perfil. As duas mandaram `Page.navigate` na mesma janela, e a sonda leu a
# página que a outra tinha acabado de abrir — e concluiu "esta conta não tem destaque".
#
#     DOIS PROCESSOS NA MESMA JANELA NÃO DÃO ERRO. DÃO MEDIÇÃO ERRADA.
#
# É a mesma família do que a memória desta casa já registra sobre duas SESSÕES
# escolhendo sozinhas a porta 9222. Ali eram duas pessoas; aqui fui eu duas vezes.
#
# A trava é um arquivo com o PID de quem pegou a porta. Ela não impede nada à força:
# ela AVISA, com o número do processo e o que fazer — porque travar coleta noturna por
# causa de um arquivo esquecido seria pior que o problema que ela resolve.
def _arquivo_de_trava(porta):
    return os.path.join(os.path.expanduser('~'), '.sintonia-browser',
                        'porta-%d.dono' % porta)


def dono_da_porta(porta):
    """→ (pid, quando) de quem declarou a porta, ou (None, None)."""
    caminho = _arquivo_de_trava(porta)
    if not os.path.exists(caminho):
        return None, None
    try:
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
        return d.get('PID'), d.get('DESDE')
    except (OSError, ValueError):
        return None, None


def _vivo(pid):
    if not pid or pid == os.getpid():
        return pid == os.getpid()
    try:
        import subprocess
        r = subprocess.run(['tasklist', '/FI', 'PID eq %d' % int(pid)],
                           capture_output=True, text=True, timeout=20)
        return str(pid) in (r.stdout or '')
    except Exception:                                        # noqa: BLE001
        return False


def tomar_porta(porta, *, quem='?'):
    """Declara esta porta como minha. → aviso em texto, ou '' se estava livre."""
    import datetime
    pid, desde = dono_da_porta(porta)
    aviso = ''
    if pid and pid != os.getpid() and _vivo(pid):
        aviso = ('A PORTA %d JÁ TEM DONO: processo %s, desde %s. Duas leituras na mesma '
                 'janela não dão erro — dão medição errada. Use outra porta '
                 '(IG_PORTA=%d) ou espere o outro terminar.'
                 % (porta, pid, desde, porta + 1))
    os.makedirs(os.path.dirname(_arquivo_de_trava(porta)), exist_ok=True)
    with open(_arquivo_de_trava(porta), 'w', encoding='utf-8') as f:
        json.dump({'PID': os.getpid(), 'QUEM': quem,
                   'DESDE': datetime.datetime.now().isoformat(timespec='seconds')}, f)
    return aviso


def abrir(url, *, porta, espera=3.0, timeout=60):
    """Navega e devolve `(aba, html)`. Quem fecha a aba é quem chamou.

    `espera` existe porque `Page.navigate` volta quando o pedido saiu, não quando a
    página montou. Página que monta por JavaScript devolveria um esqueleto vazio — e
    esqueleto vazio se lê como "a fonte não tem nada", que é a leitura errada de sempre.
    """
    a = Aba(_aba_de_pagina(porta)['webSocketDebuggerUrl'], timeout=timeout)
    a.comando('Page.enable')
    a.comando('Page.navigate', url=url)
    time.sleep(espera)
    html = a.js('document.documentElement.outerHTML') or ''
    return a, html


def png(aba, caminho):
    """A prova visual. → bytes gravados, ou `(0, motivo)` — nunca derruba a coleta.

    DUAS COISAS MEDIDAS AQUI, as duas em 2026-09-02 contra o Instagram:

    1. `Page.captureScreenshot` **trava para sempre** quando a aba não está em primeiro
       plano. O Chrome só entrega o quadro da SUPERFÍCIE quando existe superfície sendo
       desenhada; numa aba oculta ele simplesmente não responde, e o socket estoura o
       tempo. `Page.bringToFront` resolve, e `fromSurface=False` (desenhar a partir do
       renderizador, não da tela) é a saída para quando a janela está minimizada.

    2. Foto é PROVA, não é o dado. Uma coleta inteira não pode morrer porque a captura
       falhou — mas o relatório também não pode dizer que tem prova quando não tem. Por
       isso o retorno é um par: bytes e motivo.
    """
    try:
        aba.comando('Page.bringToFront')
    except Erro:
        pass                              # sem primeiro plano ainda dá para tentar
    motivo = 'nenhuma tentativa chegou a rodar'
    for params in ({'format': 'png'},
                   {'format': 'png', 'fromSurface': False},
                   {'format': 'jpeg', 'quality': 60, 'fromSurface': False}):
        try:
            r = aba.comando('Page.captureScreenshot', **params)
        except (Erro, socket.timeout, OSError) as e:
            motivo = '%s: %s' % (type(e).__name__, str(e)[:120])
            continue
        dados = base64.b64decode(r.get('data') or '')
        if not dados:
            motivo = 'a captura voltou vazia'
            continue
        os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
        with open(caminho, 'wb') as f:
            f.write(dados)
        return len(dados), 'OK'
    return 0, 'SCREENSHOT_FAILED — %s' % motivo


if __name__ == '__main__':
    alvo = sys.argv[1] if len(sys.argv) > 1 else 'https://example.com'
    p = int(os.environ.get('CDP_PORTA') or 9222)
    subir(p)
    aba, h = abrir(alvo, porta=p)
    print('porta      :', p)
    print('url        :', alvo)
    print('html bytes :', len(h))
    print('título     :', aba.js('document.title'))
    aba.fechar()
