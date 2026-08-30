#!/usr/bin/env python3
"""
O DONO DO RUNTIME — qual Python desta máquina é real, provado por trabalho feito.

Existe por causa de um falso "download concluído" com pasta vazia, em 2026-08-30.
A pasta `data/raw/FR/anses-ephy` foi criada, o comando terminou, ninguém reclamou,
e nenhum byte francês entrou. Duas coisas diferentes tinham sido confundidas:

    PROCESS_EXIT_ZERO ≠ WORK_EXECUTED
    COMMAND_EXISTS    ≠ VALID_INTERPRETER

Uso:
    python3 scripts/runtime_python.py            # o retrato desta máquina

O QUE ESTA MÁQUINA MEDIU
--------------------------
1. `python3` resolve para `...\\WindowsApps\\python3.exe` — o atalho da Loja da
   Microsoft. Ele NÃO executa código: imprime um recado e sai com 49. Um cartaz
   escrito "Python" pregado numa porta que não leva a lugar nenhum.

2. `py -3` resolve para um executável REAL — e roda com a casa errada:

       prefix rodando de C:\\eame-sintonia  ->  C:\\eame-sintonia
       prefix rodando de C:\\Users          ->  C:\\Users
       prefix rodando de C:\\Windows        ->  C:\\Windows

   O `sys.prefix` segue a pasta onde você está parado. O interpretador não tem
   casa: ele acha que mora onde você o chamou. E `os.__file__` apontava para
   `C:\\eame-sintonia\\Lib\\os.py`, um arquivo que NÃO EXISTE — o interpretador
   mentindo sobre onde está a própria biblioteca dele.

   O preço disso não é cosmético: `site-packages` vira `<pasta atual>\\Lib\\
   site-packages`. Um `pip install` rodado de dentro do repositório instalaria
   pacotes DENTRO DO REPOSITÓRIO.

3. O conserto não é reinstalar: é dizer onde fica a casa. Com
   `PYTHONHOME` apontando para a instalação que tem o `Lib`, o prefix fica
   estável em qualquer pasta e `os.__file__` passa a existir.

A REGRA QUE SAI DISSO
-----------------------
Achar um comando não é achar um Python. Um candidato só é aceito depois de
FAZER UM TRABALHO e o trabalho ser conferido:

    escrever um arquivo com um segredo sorteado agora
    → o arquivo existe
    → tem mais de zero bytes
    → o conteúdo é exatamente o segredo
    → e some no fim

O segredo é sorteado a cada execução de propósito. Um arquivo deixado por uma
execução anterior passaria numa prova de conteúdo fixo — e provaria o passado,
não o presente.

E A PÓS-CONDIÇÃO DOS COLETORES
--------------------------------
    EMPTY_OUTPUT ≠ ZERO_RESULTS

Arquivo de saída ausente não é "a fonte devolveu zero". Zero é uma resposta que
a fonte dá; ausência é uma resposta que ninguém deu. Confundir os dois publica
"a França não tem registros" quando o que houve foi um interpretador quebrado.
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import uuid

MARCADOR = 'SINTONIA_RUNTIME_OK'

# Variáveis onde um humano pode declarar o interpretador. A primeira que existir
# manda — e se ela apontar para o vazio, isso é erro de configuração e falha
# fechado, em vez de cair no automático e esconder o engano.
VARS_EXPLICITAS = ('SINTONIA_PYTHON', 'PYTHON_EXECUTABLE')

# Terceiro defeito medido nesta máquina, e ele mata coleta pelo meio: o console
# do Windows aqui é cp1252, e imprimir "≠" levanta UnicodeEncodeError. As leis
# deste repositório são escritas com "≠" e os textos são em português com acento
# — então um coletor que tentasse EXPLICAR por que recusou um dado morreria na
# hora de explicar. O processo cairia com traceback no lugar do diagnóstico.
#
# Vai junto com o interpretador porque é condição para ele ser usável aqui, não
# preferência de quem chama.
AMBIENTE_SEGURO = {'PYTHONIOENCODING': 'utf-8'}

# O que o filho roda. Ele faz DUAS coisas: escreve o segredo em disco e conta
# quem é. A primeira é a prova de trabalho; a segunda é o diagnóstico.
_PROBE = (
    'import json,os,platform,sys\n'
    'alvo,nonce=sys.argv[1],sys.argv[2]\n'
    'open(alvo,"w",encoding="utf-8").write(nonce)\n'
    'libs=[p for p in sys.path if os.path.isfile(os.path.join(p,"os.py"))]\n'
    'print(json.dumps({"MARCADOR":"%s","EXECUTABLE":sys.executable,'
    '"VERSION":"%%d.%%d.%%d"%%sys.version_info[:3],"PREFIX":sys.prefix,'
    '"STDLIB_FILE":os.__file__,"STDLIB_FILE_EXISTS":os.path.exists(os.__file__),'
    '"ARCH":platform.architecture()[0],"LIB_DIRS":libs}))\n' % MARCADOR
)

# Estados de um candidato.
VALIDO = 'VALID_INTERPRETER'
ALIAS_QUEBRADO = 'BROKEN_EXECUTION_ALIAS'      # existe, não executa
CASA_INSTAVEL = 'UNSTABLE_PREFIX'              # executa, mente sobre onde mora
NAO_EXECUTOU = 'DID_NOT_EXECUTE'
TRABALHO_NAO_FEITO = 'EXIT_ZERO_WITHOUT_WORK'  # a cicatriz que deu nome a tudo
AUSENTE = 'NOT_FOUND'


def _windowsapps(caminho):
    """O atalho da Loja fica sempre nesta pasta. Marcar não substitui a prova."""
    return 'windowsapps' in str(caminho or '').replace('/', '\\').lower().split('\\')


# ══════════════════════════════════════════════════════════════════════════════
# 1 · A PROVA POSITIVA — o candidato tem de FAZER alguma coisa
# ══════════════════════════════════════════════════════════════════════════════

def sondar(executavel, env_extra=None, rodar=None, pasta_tmp=None):
    """→ dict com STATE. Só devolve VALID_INTERPRETER depois do trabalho conferido.

    A ordem das perguntas importa. Perguntar "o exit code foi 0?" primeiro faria
    o alias da Loja — que sai com 49 — parecer o único modo de falha possível, e
    o modo que realmente machuca é o outro: sair com 0 sem ter feito nada.
    """
    rodar = subprocess.run if rodar is None else rodar
    pasta_tmp = pasta_tmp or tempfile.gettempdir()

    nonce = uuid.uuid4().hex
    alvo = os.path.join(pasta_tmp, 'sintonia-runtime-%s.txt' % nonce)
    ambiente = dict(os.environ)
    ambiente.pop('PYTHONHOME', None)
    ambiente.update(AMBIENTE_SEGURO)
    ambiente.update(env_extra or {})

    try:
        r = rodar([executavel, '-c', _PROBE, alvo, nonce],
                  capture_output=True, text=True, timeout=60, env=ambiente)
    except Exception as e:                                        # noqa: BLE001
        return {'STATE': NAO_EXECUTOU, 'EXECUTABLE': executavel,
                'WHY': 'o sistema recusou executar: %s' % e}

    saida = (getattr(r, 'stdout', '') or '')
    erro = (getattr(r, 'stderr', '') or '')
    codigo = getattr(r, 'returncode', 1)

    # A pergunta que vale: o TRABALHO aconteceu? Não: o processo terminou bem?
    fez = os.path.isfile(alvo)
    bytes_ = os.path.getsize(alvo) if fez else 0
    conteudo = None
    if fez:
        try:
            with open(alvo, encoding='utf-8') as fh:
                conteudo = fh.read()
        finally:
            os.remove(alvo)

    if not fez:
        estado = TRABALHO_NAO_FEITO if codigo == 0 else ALIAS_QUEBRADO
        return {'STATE': estado, 'EXECUTABLE': executavel, 'EXIT_CODE': codigo,
                'WORK_DONE': False, 'OUTPUT_BYTES': 0,
                'IS_WINDOWSAPPS_ALIAS': _windowsapps(executavel),
                'WHY': ('terminou com %d e não escreveu o arquivo de prova. '
                        'PROCESS_EXIT_ZERO ≠ WORK_EXECUTED' % codigo),
                'STDERR': erro.strip()[:200]}

    if bytes_ <= 0 or conteudo != nonce:
        return {'STATE': TRABALHO_NAO_FEITO, 'EXECUTABLE': executavel,
                'EXIT_CODE': codigo, 'WORK_DONE': False, 'OUTPUT_BYTES': bytes_,
                'WHY': 'o arquivo de prova saiu vazio ou com conteúdo diferente do sorteado'}

    relato = None
    for linha in saida.splitlines():
        linha = linha.strip()
        if linha.startswith('{') and MARCADOR in linha:
            try:
                relato = json.loads(linha)
                break
            except ValueError:
                pass
    if not relato:
        return {'STATE': TRABALHO_NAO_FEITO, 'EXECUTABLE': executavel,
                'EXIT_CODE': codigo, 'WORK_DONE': True, 'OUTPUT_BYTES': bytes_,
                'WHY': 'escreveu o arquivo mas não devolveu o relato com o marcador'}

    fora = {'STATE': VALIDO, 'EXIT_CODE': codigo, 'WORK_DONE': True,
            'OUTPUT_BYTES': bytes_, 'ENV_EXTRA': dict(env_extra or {}),
            'IS_WINDOWSAPPS_ALIAS': _windowsapps(executavel)}
    fora.update({k: relato.get(k) for k in
                 ('EXECUTABLE', 'VERSION', 'PREFIX', 'STDLIB_FILE',
                  'STDLIB_FILE_EXISTS', 'ARCH', 'LIB_DIRS')})

    # Executa, mas mente sobre onde mora. Aceitar aqui é aceitar que
    # `site-packages` caia dentro do repositório.
    if not relato.get('STDLIB_FILE_EXISTS'):
        fora['STATE'] = CASA_INSTAVEL
        fora['WHY'] = ('o interpretador diz que sua biblioteca está em %s, e esse '
                       'arquivo não existe. O prefix está seguindo a pasta atual'
                       % relato.get('STDLIB_FILE'))
    return fora


def _consertar_casa(relato, executavel, rodar=None, pasta_tmp=None):
    """Deriva PYTHONHOME do que o PRÓPRIO interpretador contou. Não chuta caminho.

    Ele já disse, em `LIB_DIRS`, quais pastas do `sys.path` têm um `os.py` de
    verdade. A casa é a pasta acima dessa. Se com isso o prefix ficar honesto,
    o candidato é aceito COM esse ambiente anotado — e quem for usá-lo depois
    precisa levar o ambiente junto.
    """
    for lib in relato.get('LIB_DIRS') or []:
        casa = os.path.dirname(lib)
        if not casa:
            continue
        tentativa = sondar(executavel, env_extra={'PYTHONHOME': casa},
                           rodar=rodar, pasta_tmp=pasta_tmp)
        if tentativa.get('STATE') == VALIDO:
            tentativa['HOME_DERIVED_FROM'] = lib
            return tentativa
    return None


# ══════════════════════════════════════════════════════════════════════════════
# 2 · A DESCOBERTA — candidatos em ordem, e cada um passa pela prova
# ══════════════════════════════════════════════════════════════════════════════

def _candidatos_windows(env, which, existe, rodar):
    vistos = []

    for var in VARS_EXPLICITAS:
        declarado = (env.get(var) or '').strip()
        if declarado:
            # Declarado e ausente não cai no automático: esconderia o engano.
            vistos.append((declarado, 'ENV:' + var, existe(declarado)))
            return vistos

    # `py -3` é o jeito oficial do Windows de achar Python, e ele devolve o
    # caminho real — que pode não estar em lugar nenhum do PATH.
    try:
        lanc = which('py')
        if lanc:
            r = rodar([lanc, '-3', '-c', 'import sys;print(sys.executable)'],
                      capture_output=True, text=True, timeout=60)
            caminho = (getattr(r, 'stdout', '') or '').strip().splitlines()
            caminho = caminho[-1].strip() if caminho else ''
            if caminho:
                vistos.append((caminho, 'PY_LAUNCHER', existe(caminho)))
    except Exception:                                             # noqa: BLE001
        pass

    for nome in ('python', 'python3'):
        caminho = which(nome)
        if caminho:
            vistos.append((caminho, 'PATH', existe(caminho)))

    base = env.get('LOCALAPPDATA', '')
    for caminho in (os.path.join(base, r'Programs\Python\Python312\python.exe'),
                    r'C:\Python312\python.exe',
                    r'C:\Program Files\Python312\python.exe'):
        if caminho and existe(caminho):
            vistos.append((caminho, 'INSTALL_PATH', True))
    return vistos


def _candidatos_posix(env, which, existe, rodar):
    vistos = []
    for var in VARS_EXPLICITAS:
        declarado = (env.get(var) or '').strip()
        if declarado:
            vistos.append((declarado, 'ENV:' + var, existe(declarado)))
            return vistos
    for nome in ('python3', 'python'):
        caminho = which(nome)
        if caminho:
            vistos.append((caminho, 'PATH', existe(caminho)))
    for caminho in ('/usr/bin/python3', '/usr/local/bin/python3'):
        if existe(caminho):
            vistos.append((caminho, 'INSTALL_PATH', True))
    return vistos


def descobrir(env=None, which=None, existe=None, rodar=None, pasta_tmp=None,
              sistema=None):
    """→ o primeiro candidato que PROVA que executa. Nunca o primeiro que existe.

    A lista de recusados sai junto, com o motivo de cada um, porque "não achei
    Python" numa máquina que tem três é um diagnóstico inútil.
    """
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    existe = os.path.isfile if existe is None else existe
    rodar = subprocess.run if rodar is None else rodar
    sistema = platform.system() if sistema is None else sistema

    monta = _candidatos_windows if sistema == 'Windows' else _candidatos_posix
    candidatos = monta(env, which, existe, rodar)

    recusados = []
    for caminho, como, presente in candidatos:
        if not presente:
            recusados.append({'EXECUTABLE': caminho, 'HOW': como, 'STATE': AUSENTE,
                              'WHY': 'o caminho não existe'})
            continue
        r = sondar(caminho, rodar=rodar, pasta_tmp=pasta_tmp)
        if r['STATE'] == CASA_INSTAVEL:
            consertado = _consertar_casa(r, caminho, rodar=rodar, pasta_tmp=pasta_tmp)
            if consertado:
                consertado['HOW'] = como
                consertado['REJECTED'] = recusados
                return consertado
        if r['STATE'] == VALIDO:
            r['HOW'] = como
            r['REJECTED'] = recusados
            return r
        r['HOW'] = como
        recusados.append(r)

    return {'STATE': AUSENTE, 'EXECUTABLE': None, 'REJECTED': recusados,
            'WHY': ('nenhum candidato passou na prova de execução. '
                    'COMMAND_EXISTS ≠ VALID_INTERPRETER')}


def portao(achado=None):
    """PYTHON_RUNTIME_GATE. Fecha só com trabalho feito e casa honesta."""
    a = descobrir() if achado is None else achado
    condicoes = {
        'INTERPRETER_FOUND': a.get('STATE') == VALIDO,
        'WORK_EXECUTED': bool(a.get('WORK_DONE')),
        'OUTPUT_BYTES_POSITIVE': (a.get('OUTPUT_BYTES') or 0) > 0,
        'STDLIB_FILE_EXISTS': bool(a.get('STDLIB_FILE_EXISTS')),
        'NOT_WINDOWSAPPS_ALIAS': not a.get('IS_WINDOWSAPPS_ALIAS'),
    }
    faltam = sorted(k for k, v in condicoes.items() if not v)
    return {'PYTHON_RUNTIME_GATE': 'CLOSED' if not faltam else 'OPEN',
            'CONDITIONS': condicoes, 'MISSING': faltam,
            'PYTHON_REAL_EXECUTABLE': a.get('EXECUTABLE'),
            'PYTHON_VERSION': a.get('VERSION'),
            'PYTHON_ARCH': a.get('ARCH'),
            'PYTHON_PREFIX': a.get('PREFIX'),
            'ENV_EXTRA': a.get('ENV_EXTRA') or {}}


def comando(achado=None):
    """→ (argv_prefixo, env) para chamar o Python válido. O ambiente vai junto.

    Devolver só o caminho seria um convite ao defeito: este executável só está
    inteiro COM o `PYTHONHOME` do lado. Quem esquecer o ambiente roda de novo
    com a casa errada.
    """
    a = descobrir() if achado is None else achado
    if a.get('STATE') != VALIDO:
        raise RuntimeError('sem interpretador válido: ' + str(a.get('WHY')))
    ambiente = dict(os.environ)
    ambiente.pop('PYTHONHOME', None)
    ambiente.update(AMBIENTE_SEGURO)
    ambiente.update(a.get('ENV_EXTRA') or {})
    return [a['EXECUTABLE']], ambiente


# ══════════════════════════════════════════════════════════════════════════════
# 3 · A PÓS-CONDIÇÃO DOS COLETORES — exit 0 não basta
# ══════════════════════════════════════════════════════════════════════════════

SAIDA_OK = 'OUTPUT_OK'
SAIDA_AUSENTE = 'MISSING_OUTPUT'
SAIDA_VAZIA = 'EMPTY_OUTPUT'
SAIDA_PARCIAL = 'PARTIAL_OUTPUT'
EXECUCAO_INVALIDA = 'EXECUTION_INVALID_RUNTIME'
ZERO_MEDIDO = 'ZERO_RESULTS_MEASURED'


def conferir_saida(*, caminhos, exit_code=None, contagem=None, contagem_minima=1,
                   fonte_respondeu_zero=False, tamanho=None, existe=None):
    """A pós-condição de um coletor. Sem ela, exit 0 vira "coletado".

    `fonte_respondeu_zero` é o único jeito de um zero legítimo entrar — e ele
    tem de vir de uma resposta LIDA da fonte, nunca de arquivo que não apareceu.

        EMPTY_OUTPUT ≠ ZERO_RESULTS
    """
    existe = os.path.isfile if existe is None else existe
    tamanho = os.path.getsize if tamanho is None else tamanho

    caminhos = list(caminhos or [])
    presentes = [c for c in caminhos if existe(c)]
    ausentes = [c for c in caminhos if not existe(c)]
    bytes_totais = sum(tamanho(c) for c in presentes)

    base = {'EXPECTED_OUTPUTS': len(caminhos), 'OUTPUTS_PRESENT': len(presentes),
            'OUTPUTS_MISSING': ausentes, 'OUTPUT_BYTES': bytes_totais,
            'RECORD_COUNT': contagem, 'EXIT_CODE': exit_code}

    if not caminhos:
        return dict(base, STATE=SAIDA_AUSENTE,
                    WHY='nenhuma saída esperada foi declarada, e sem isso não há o que conferir')
    if not presentes:
        return dict(base, STATE=SAIDA_AUSENTE,
                    WHY=('nenhum arquivo de saída existe. Isso NÃO é a fonte '
                         'devolvendo zero: EMPTY_OUTPUT ≠ ZERO_RESULTS'))
    if ausentes:
        return dict(base, STATE=SAIDA_PARCIAL,
                    WHY='parte das saídas esperadas não apareceu: ' + ', '.join(ausentes))
    if bytes_totais <= 0:
        return dict(base, STATE=SAIDA_VAZIA,
                    WHY='os arquivos existem e somam zero byte')
    if contagem is not None and contagem < contagem_minima:
        if fonte_respondeu_zero:
            return dict(base, STATE=ZERO_MEDIDO,
                        WHY='a fonte respondeu e a resposta foi zero — isso é um fato medido')
        return dict(base, STATE=SAIDA_VAZIA,
                    WHY=('saiu com %s registros e ninguém provou que a fonte '
                         'respondeu zero' % contagem))
    if exit_code not in (None, 0):
        return dict(base, STATE=EXECUCAO_INVALIDA,
                    WHY='o processo terminou com %s' % exit_code)
    return dict(base, STATE=SAIDA_OK, WHY='saídas presentes, com bytes e com registros')


def main():
    a = descobrir()
    p = portao(a)
    print('PYTHON_RUNTIME_GATE     :', p['PYTHON_RUNTIME_GATE'])
    print('PYTHON_REAL_EXECUTABLE  :', p['PYTHON_REAL_EXECUTABLE'])
    print('PYTHON_VERSION          :', p['PYTHON_VERSION'])
    print('PYTHON_ARCH             :', p['PYTHON_ARCH'])
    print('PYTHON_PREFIX           :', p['PYTHON_PREFIX'])
    print('ENV_EXTRA               :', p['ENV_EXTRA'] or '(nenhum)')
    print('HOW_FOUND               :', a.get('HOW'))
    if p['MISSING']:
        print('FALTAM                  :', ', '.join(p['MISSING']))
    for r in a.get('REJECTED') or []:
        print('  recusado: %-58s %s' % (str(r.get('EXECUTABLE'))[:58], r.get('STATE')))
        print('            %s' % str(r.get('WHY'))[:100])
    return 0 if p['PYTHON_RUNTIME_GATE'] == 'CLOSED' else 1


if __name__ == '__main__':
    sys.exit(main())
