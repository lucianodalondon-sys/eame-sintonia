#!/usr/bin/env python3
"""
A PORTA DE COLETA — onde está o navegador desta máquina, e o que ele prova.

Existe porque há rota pública que o navegador normal abre e o `curl` não. Isso
NÃO é proteção burlada: é a mesma página, pedida pelo mesmo programa que qualquer
pessoa usa para lê-la. O que este módulo faz é ACHAR esse programa e dizer a
versão dele — nada mais. Não desliga sandbox, não resolve CAPTCHA, não mexe em
sessão, não lê cookie.

    python3 scripts/navegador.py            # onde está, qual versão, o que suporta

A DISTINÇÃO QUE ESTA MÁQUINA MEDIU EM 2026-08-30
--------------------------------------------------
Contra `https://www.adama.com/france/fr`, três pedidos diferentes:

    curl com User-Agent de Chrome ........ HTTP 403, corpo de 143 bytes
    chrome --headless=new --dump-dom ..... HTTP 403, corpo de 186 bytes
    chrome com janela, via DevTools ...... a página francesa inteira

Então headless NÃO é substituto de navegador com janela nesta rota:

    HTTP_ROUTE ≠ HEADLESS_ROUTE ≠ HEADED_ROUTE

E a lei que já vinha da Itália continua valendo, agora com um degrau a mais:

    ROUTE_BLOCKED_FOR_AUTOMATION ≠ CATALOG_EMPTY

Um 403 mede o que o servidor respondeu ao MEU pedido. Não mede o que existe do
outro lado. Quem trata os dois como a mesma coisa publica "catálogo vazio" quando
o catálogo está cheio.

A ORDEM DE PREFERÊNCIA, E POR QUE ELA É ESSA
----------------------------------------------
Chrome antes de Chromium, de propósito. Não porque Chromium seja pior, mas porque
a coleta tem de ser reproduzível: trocar silenciosamente o binário troca o
User-Agent, o conjunto de codecs e o comportamento de TLS, e aí duas execuções da
mesma coleta deixam de ser comparáveis sem que ninguém tenha mudado nada.

    CHROME_EXECUTABLE  (variável de ambiente)  — manda em tudo, se existir
    google-chrome · google-chrome-stable       — no PATH
    caminhos de instalação padrão do Windows e do macOS
    chromium · chromium-browser                — último recurso, e ANOTADO como tal

SANDBOX
--------
`--no-sandbox` não é padrão aqui e não vira padrão "para funcionar". Se um
ambiente impedir o Chrome de subir por causa de sandbox, o certo é dizer isso —
não desligar a proteção e seguir.

PERFIL — E POR QUE ELE TEM PAÍS
---------------------------------
O perfil de coleta mora FORA do repositório, em
`~/.sintonia-browser/<país>/chrome-profile`. Cookie, histórico, Local Storage e
Login Data são dados de sessão: nunca entram em Git, nem em fixture, nem em
relatório.

O país no caminho não é organização: é isolamento. Um perfil só, compartilhado,
faz duas coletas dividirem cookie, cache, consentimento e — pior — a MESMA porta
de DevTools. Em 30/08 uma janela aberta para a França apareceu com uma aba
italiana dentro, e não havia como saber de quem era o quê. Duas missões no mesmo
navegador é o mesmo defeito que duas missões no mesmo checkout.

    ONE ACTIVE MISSION = ONE WORKTREE = ONE BROWSER PROFILE = ONE PORT

A porta é reservada por país e escrita aqui, para que reservar deixe de depender
de alguém lembrar.
"""
import os
import platform
import re
import shutil
import subprocess
import sys

# A raiz dos perfis. Fora do repositório, sempre.
BASE_PERFIS = os.path.join(os.path.expanduser('~'), '.sintonia-browser')

# Porta de DevTools por país. Compartilhar porta é compartilhar processo: quem
# se conectar na 9222 fala com o Chrome de quem chegou primeiro, e as abas de uma
# missão aparecem na outra.
PORTAS_POR_PAIS = {'FR': 9222, 'IT': 9223, 'ES': 9224}


def perfil(pais):
    """→ o perfil daquele país. Sem país não há perfil: falha fechado.

    Aceitar um padrão silencioso aqui recriaria o perfil único que causou a
    colisão — e ele voltaria com cara de conveniência.
    """
    p = str(pais or '').strip().upper()
    if not p:
        raise ValueError('perfil de coleta exige país; sem ele o perfil é compartilhado')
    return os.path.join(BASE_PERFIS, p.lower(), 'chrome-profile')


def porta(pais):
    """→ a porta reservada daquele país, ou erro se ninguém a reservou."""
    p = str(pais or '').strip().upper()
    if p not in PORTAS_POR_PAIS:
        raise ValueError('nenhuma porta de DevTools reservada para %r. '
                         'Reservar em PORTAS_POR_PAIS antes de coletar' % pais)
    return PORTAS_POR_PAIS[p]

# Famílias. `CHROME` é preferido; `CHROMIUM` é aceito e sinalizado.
CHROME = 'CHROME'
CHROMIUM = 'CHROMIUM'

# Nomes no PATH, em ordem. Chrome primeiro.
_NO_PATH = (
    ('google-chrome', CHROME),
    ('google-chrome-stable', CHROME),
    ('chrome', CHROME),
    ('chromium', CHROMIUM),
    ('chromium-browser', CHROMIUM),
)

# Caminhos de instalação que o PATH normalmente não cobre. No Windows o Chrome
# não entra no PATH, e é por isso que procurar só com `which` conclui "ausente"
# numa máquina que tem Chrome instalado.
_FIXOS_WINDOWS = (
    (r'C:\Program Files\Google\Chrome\Application\chrome.exe', CHROME),
    (r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe', CHROME),
    (os.path.join(os.environ.get('LOCALAPPDATA', ''),
                  r'Google\Chrome\Application\chrome.exe'), CHROME),
    (r'C:\Program Files\Chromium\Application\chrome.exe', CHROMIUM),
)
_FIXOS_MAC = (
    ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', CHROME),
    ('/Applications/Chromium.app/Contents/MacOS/Chromium', CHROMIUM),
)
_FIXOS_LINUX = (
    ('/usr/bin/google-chrome', CHROME),
    ('/usr/bin/google-chrome-stable', CHROME),
    ('/opt/google/chrome/chrome', CHROME),
    ('/usr/bin/chromium', CHROMIUM),
    ('/usr/bin/chromium-browser', CHROMIUM),
    ('/snap/bin/chromium', CHROMIUM),
)


def _fixos():
    s = platform.system()
    if s == 'Windows':
        return _FIXOS_WINDOWS
    if s == 'Darwin':
        return _FIXOS_MAC
    return _FIXOS_LINUX


def descobrir(env=None, which=None, existe=None):
    """→ dict com executável, família e COMO foi achado. Nunca chuta.

    `env`, `which` e `existe` são injetáveis para que o teste possa montar
    máquinas que não existem aqui — uma sem Chrome e com Chromium, uma com a
    variável de ambiente apontando para o lugar errado — sem depender do disco
    de quem roda o teste.
    """
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    existe = os.path.isfile if existe is None else existe

    declarado = (env.get('CHROME_EXECUTABLE') or '').strip()
    if declarado:
        if existe(declarado):
            return {'FOUND': True, 'EXECUTABLE': declarado,
                    'FAMILY': CHROME if 'chromium' not in declarado.lower() else CHROMIUM,
                    'HOW': 'CHROME_EXECUTABLE',
                    'IS_PREFERRED': 'chromium' not in declarado.lower()}
        # Declarado e ausente é erro de configuração, e cair no automático
        # silenciosamente esconderia exatamente esse erro.
        return {'FOUND': False, 'EXECUTABLE': None, 'FAMILY': None,
                'HOW': 'CHROME_EXECUTABLE',
                'WHY': ('CHROME_EXECUTABLE aponta para um arquivo que não existe: '
                        + declarado)}

    for nome, familia in _NO_PATH:
        caminho = which(nome)
        if caminho:
            return {'FOUND': True, 'EXECUTABLE': caminho, 'FAMILY': familia,
                    'HOW': 'PATH', 'IS_PREFERRED': familia == CHROME}

    for caminho, familia in _fixos():
        if caminho and existe(caminho):
            return {'FOUND': True, 'EXECUTABLE': caminho, 'FAMILY': familia,
                    'HOW': 'INSTALL_PATH', 'IS_PREFERRED': familia == CHROME}

    return {'FOUND': False, 'EXECUTABLE': None, 'FAMILY': None, 'HOW': None,
            'WHY': 'nenhum Chrome ou Chromium encontrado no PATH nem nos caminhos padrão'}


_VERSAO = re.compile(r'(\d+\.\d+\.\d+\.\d+)')


def versao(executavel, rodar=None):
    """→ a versão, ou None com o motivo. No Windows `--version` não escreve na saída.

    O binário do Chrome no Windows é uma aplicação gráfica: ele não devolve texto
    para o terminal. A versão está nos metadados do arquivo e na pasta irmã com
    nome de versão — e ler dali é medir, não adivinhar.
    """
    rodar = subprocess.run if rodar is None else rodar
    try:
        r = rodar([executavel, '--version'], capture_output=True, text=True, timeout=30)
        m = _VERSAO.search((getattr(r, 'stdout', '') or '') + (getattr(r, 'stderr', '') or ''))
        if m:
            return {'VERSION': m.group(1), 'HOW': '--version'}
    except Exception:                                   # noqa: BLE001
        pass

    pasta = os.path.dirname(executavel or '')
    if pasta and os.path.isdir(pasta):
        achadas = sorted(d for d in os.listdir(pasta) if _VERSAO.fullmatch(d))
        if achadas:
            return {'VERSION': achadas[-1], 'HOW': 'pasta de versão ao lado do binário'}

    return {'VERSION': None, 'HOW': None,
            'WHY': 'o binário não devolveu versão e não há pasta de versão ao lado'}


def argumentos(url, pais, headless=False, com_devtools=True):
    """A linha de comando da coleta. Sem `--no-sandbox`, e isso é uma decisão.

    `pais` é obrigatório e vem antes de tudo: é ele que decide perfil e porta, e
    é a única coisa que impede duas missões de dividirem o mesmo navegador.

    `headless=True` continua disponível porque serve para rota que não é
    bloqueada — mas quem chamar precisa saber que nesta máquina, contra a ADAMA,
    headless levou 403 e janela não.
    """
    args = [
        '--user-data-dir=' + perfil(pais),
        '--no-first-run',
        '--no-default-browser-check',
    ]
    if headless:
        args += ['--headless=new', '--disable-gpu']
    if com_devtools:
        args += ['--remote-debugging-port=%d' % porta(pais)]
    args.append(url)
    return args


def diagnostico(pais='FR'):
    """O retrato desta máquina, para o relatório de entrega."""
    achado = descobrir()
    fora = {
        'OS': platform.system(),
        'OS_RELEASE': platform.release(),
        'ARCH': platform.machine(),
        'CHROME_FOUND': achado['FOUND'],
        'CHROME_EXECUTABLE': achado.get('EXECUTABLE'),
        'CHROME_FAMILY': achado.get('FAMILY'),
        'HOW_FOUND': achado.get('HOW'),
        'COUNTRY': pais,
        'PROFILE_DIR': perfil(pais),
        'PROFILE_EXISTS': os.path.isdir(perfil(pais)),
        'DEVTOOLS_PORT': porta(pais),
        'SANDBOX': 'ON — `--no-sandbox` não é padrão',
    }
    if achado['FOUND']:
        fora.update(versao(achado['EXECUTABLE']))
    else:
        fora['WHY'] = achado.get('WHY')
    return fora


def main():
    pais = (sys.argv[1] if len(sys.argv) > 1 else 'FR').upper()
    d = diagnostico(pais)
    largura = max(len(k) for k in d)
    for k, v in d.items():
        print('%-*s : %s' % (largura, k, v))
    if not d['CHROME_FOUND']:
        return 1
    print()
    print('exemplo de chamada (janela, sem sandbox desligada):')
    print('  ', d['CHROME_EXECUTABLE'], ' '.join(
        argumentos('https://exemplo.invalid', pais)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
