#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CENSO DA TOPOLOGIA DA COLETA — cartao a cartao, aresta a aresta.

    python3 system-map/scripts/censo_da_topologia.py
    python3 system-map/scripts/censo_da_topologia.py --json
    python3 system-map/scripts/censo_da_topologia.py --json --nao-escrever

POR QUE ISTO EXISTE
-------------------
O mapa responde «o que existe». Este censo responde as perguntas que se fazem
DIANTE de um cartao, e que ninguem conseguia responder sem abrir o repositorio:

    QUEM TE CHAMA?          um workflow, uma cadeia .sh, um humano, ou ninguem
    ESTAS NA ESTEIRA?       ou es apoio, regra, prova ou armazem
    O QUE ATRAVESSA A TUA ARESTA?   dado, controlo, leitura, regra, prova, codigo
    PORQUE ESTAS SOZINHO?   entrada, terminal, apoio, so-prova, ou buraco

    UM CARTAO SEM RAZAO DE EXISTIR NAO E UM CARTAO: E UM DESENHO.

O QUE ELE NAO FAZ
-----------------
Nao decide arquitetura e nao inventa ligacao. Ele MEDE o que ja esta no disco e
no grafo, e diz UNKNOWN quando nao consegue medir — nunca zero. O veredito de
cada cartao continua a ser trabalho de quem le, com isto na mao.

    GREP NAO E RUNTIME. Um ficheiro citado so por `tests/` ou `provas/` nao tem
    chamador de runtime, e este censo conta-o assim.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ESTADO = os.path.join(RAIZ, 'system-map', 'data', 'state.generated.json')

# As familias que sao a coleta e a sua sala de espera.
LADO_DA_COLETA = ('F-COLETA', 'F-ESPERA')
# Quem chama de VERDADE: um workflow ou uma cadeia. O resto e mencao.
ONDE_SE_CHAMA = ('.github/workflows', 'motor/')
# Onde vivem provas e testes — citar aqui nao e ter chamador de runtime.
SO_MEDEM = ('tests/', 'provas/', 'system-map/')


def _sh(cmd):
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, shell=True)
    # 0 achou · 1 nao achou · 2+ NAO CONSEGUIU PROCURAR — e isso nao e zero.
    if r.returncode > 1:
        raise SystemExit('RECUSADO: a busca falhou (%d): %s' % (r.returncode, cmd))
    return [l for l in r.stdout.splitlines() if l.strip()]


ARQ = os.path.join(RAIZ, 'system-map', 'data', 'architecture.generated.json')


def alcancaveis_do_runtime():
    """Os ficheiros que uma corrida real ALCANCA — entrypoints e o que eles importam.

    ⚠️ A PRIMEIRA VERSAO DISTO CONTAVA SO OS ENTRYPOINTS, e deu 86 de 103
    cartoes «sem chamador». Isso nao era o sistema morto: era a medicao errada.
    Um modulo que ninguem invoca pela linha de comando mas que o executor
    importa CORRE — e chamar-lhe orfao seria transformar uma pergunta mal feita
    num facto.

        UM ENTRYPOINT NAO E O UNICO CODIGO QUE CORRE.
        E `grep` CONTINUA A NAO SER RUNTIME: o alcance calcula-se sobre as
        arestas de IMPORT que o scanner ja mediu, a partir de quem um WORKFLOW
        ou uma CADEIA invoca de verdade.
    """
    G = json.load(open(ARQ, encoding='utf-8'))
    importa = {}
    for e in G.get('FILE_EDGES') or []:
        if e.get('type') == 'IMPORTS':
            importa.setdefault(e['from_file'], set()).add(e['to_file'])
    # quem um workflow ou uma cadeia invoca, pelo nome do ficheiro
    raizes = set()
    for w in (glob.glob(os.path.join(RAIZ, '.github/workflows/*.yml'))
              + glob.glob(os.path.join(RAIZ, 'motor/*.sh'))
              + glob.glob(os.path.join(RAIZ, 'provas/*.sh'))):
        try:
            txt = open(w, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        for m in re.finditer(r'([A-Za-z0-9_./-]+\.(?:py|mjs|js|sh))', txt):
            c = m.group(1).lstrip('./')
            if os.path.isfile(os.path.join(RAIZ, c)):
                raizes.add(c)
    vistos, pilha = set(raizes), list(raizes)
    while pilha:
        a = pilha.pop()
        for b in importa.get(a, ()):
            if b not in vistos:
                vistos.add(b)
                pilha.append(b)
    return raizes, vistos


def chamadores(ficheiros):
    """Quem executa estes ficheiros. Separa RUNTIME de QUEM SO MEDE."""
    runtime, medem = set(), set()
    for f in ficheiros:
        base = os.path.basename(f)
        if not base or '.' not in base:
            continue
        for l in _sh("grep -rn --include=*.yml --include=*.sh --include=*.py "
                     "--include=*.mjs -F %s . 2>/dev/null | head -60"
                     % json.dumps(base)):
            onde = l.split(':', 1)[0].lstrip('./')
            if onde == f:
                continue
            if onde.startswith(ONDE_SE_CHAMA):
                runtime.add(onde)
            elif onde.startswith(SO_MEDEM):
                medem.add(onde)
    return sorted(runtime), sorted(medem)


# ─────────────────────────────────────────────────────────────────────────
# OS DOCUMENTOS DESTA ARVORE — PEDIDOS AO GIT, E NAO AO SISTEMA DE FICHEIROS
#
#     A ORDEM EM QUE UM DISCO DEVOLVE NOMES NAO E UMA REGRA SEMANTICA.
#
# ⚠️ A VERSAO ANTERIOR PERGUNTAVA AO `grep -r` E FICAVA COM O PRIMEIRO QUE
# APARECESSE. Medido em duas arvores do MESMO commit (a mesma `tree` do git,
# dafbd4e1), uma em ext4 e outra em tmpfs: DEZ cartoes com resposta diferente, e
# dois deles a dizer que NAO estavam documentados quando estavam. A causa e que
# `grep -r` percorre por `readdir`, cuja ordem e do sistema de ficheiros, e o
# `head -20` cortava as 31 linhas do `orquestrador` antes da unica que casava.
#
#     MESMA ARVORE GIT, OUTRA ORDEM DE DISCO, OUTRA RESPOSTA
#     NAO E UMA MEDICAO: E UMA SORTE.
#
# Agora a lista de documentos vem de `git ls-files` — que ordena — e e ordenada
# outra vez aqui, de proposito: depender da ordem de saida de outra ferramenta
# seria trocar um dono de ordem por outro.
#
# SO O QUE ESTA RASTREADO CONTA. Um `.md` por commitar nao faz parte da arvore a
# que a pergunta se refere, e deixa-la depender dele quebrava a propria garantia
# desta correcao: a mesma arvore GIT tem de dar a mesma resposta. Medido nesta
# arvore: 287 `.md` rastreados, ZERO por rastrear e ZERO ignorados — logo o
# conjunto e exactamente o que o `grep` via, e a mudanca de fonte nao muda quem
# entra na conta.
# ─────────────────────────────────────────────────────────────────────────
DOCUMENTOS_AUSENTES_DO_DISCO: list = []
_DOCUMENTOS = None


def documentos_da_arvore(recarregar=False):
    """OS `.md` RASTREADOS, POR ORDEM LEXICAL, LIDOS UMA VEZ SO.

    Ler 287 ficheiros custa 14 milissegundos — medido, nao estimado. A versao
    anterior lancava um `grep -r` sobre o repositorio inteiro POR CADA ficheiro
    de cartao: 358 varreduras para responder a uma pergunta que cabe numa
    leitura.

        ENGENHARIA ANTES DE MICRO-OTIMIZACAO — e a leitura inteira e mais
        barata do que a busca repetida que ela substitui.

    Um ficheiro rastreado que falta ao disco NAO e saltado em silencio: fica em
    `DOCUMENTOS_AUSENTES_DO_DISCO`, e o artefacto declara-o.
    """
    global _DOCUMENTOS
    if _DOCUMENTOS is not None and not recarregar:
        return _DOCUMENTOS
    del DOCUMENTOS_AUSENTES_DO_DISCO[:]
    docs = []
    for nome in sorted(n for n in git('ls-files').splitlines() if n.endswith('.md')):
        caminho = os.path.join(RAIZ, nome)
        if not os.path.isfile(caminho):
            DOCUMENTOS_AUSENTES_DO_DISCO.append(nome)
            continue
        with open(caminho, encoding='utf-8', errors='ignore') as fh:
            docs.append((nome, fh.read().splitlines()))
    _DOCUMENTOS = docs
    return _DOCUMENTOS


# A REGRA DO QUE CONTA COMO «ENSINA UM HUMANO A CORRER ISTO».
# Ela NAO mudou nesta missao: continua a exigir um lancador (`python`, `py`,
# `node`, `bash`, `./`) seguido do nome do ficheiro. Uma mencao narrativa ao
# nome — «o `orquestrador.py` decide a rota» — nao e uma instrucao, e continua
# a nao contar.
LANCADORES = r'(python3?|py|node|bash|\./)'


def documenta_como_cli(ficheiro, documentos):
    """QUE DOCUMENTOS ENSINAM A CORRER ESTE FICHEIRO. Funcao pura, sem disco.

    Recebe a lista de documentos ja lida e devolve TODOS os que casam, ordenados.
    Nao para no primeiro: parar no primeiro obriga alguem a decidir qual e «o
    primeiro», e a unica resposta que o codigo tinha para isso era «aquele que o
    disco devolveu primeiro».

        SE A PERGUNTA E «HA DOCUMENTACAO?», A RESPOSTA HONESTA E A LISTA TODA.

    A ordem de entrada NAO pode mudar a saida — e e por isso que a saida e
    ordenada aqui e nao herdada de quem chamou.
    """
    padrao = re.compile(LANCADORES + r'\s+\S*' + re.escape(os.path.basename(ficheiro)))
    achados = set()
    for caminho, linhas in documentos:
        for linha in linhas:
            # A linha tem de citar o CAMINHO INTEIRO (era o `-F` do grep) e
            # mostrar o lancador ao lado do nome. As duas condicoes, na MESMA
            # linha, como antes.
            if ficheiro in linha and padrao.search(linha):
                achados.add(caminho)
                break
    return sorted(achados)


def documentado_como_cli(ficheiros):
    """Um humano corre isto, e esta escrito num documento.

    ⚠️ ISTO NAO E O MESMO QUE «TEM CHAMADOR». Um CLI documentado corre quando
    alguem se lembra — nao numa corrida. Mas tambem NAO e codigo morto, e
    achatar os dois faz uma ferramenta viva parecer sobra.

        NENHUM CHAMADOR != NINGUEM CORRE.
        MAS CLI DOCUMENTADO != PORTAO QUE CORRE SOZINHO.
    """
    docs = documentos_da_arvore()
    fora = set()
    for f in ficheiros:
        if not f.endswith(('.py', '.mjs', '.sh')):
            continue
        fora.update(documenta_como_cli(f, docs))
    return sorted(fora)


def escreve_le(ficheiros):
    escreve, le = set(), set()
    for f in ficheiros:
        p = os.path.join(RAIZ, f)
        if not os.path.isfile(p) or not f.endswith(('.py', '.mjs', '.js')):
            continue
        try:
            txt = open(p, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        for m in re.finditer(r'insert into\s+(?:public\.)?([a-z_]+)', txt, re.I):
            escreve.add(m.group(1))
        for m in re.finditer(r'update\s+(?:public\.)?([a-z_]+)\s+set', txt, re.I):
            escreve.add(m.group(1))
        for m in re.finditer(r'from\s+(?:public\.)?([a-z_]+)', txt, re.I):
            le.add(m.group(1))
    return sorted(escreve), sorted(le - set(escreve))


def orfaos_por_vista(N, E):
    """Os cartoes que parecem sozinhos SO porque os vizinhos vivem noutra vista.

    ⚠️ ESTA E A RESPOSTA A «HA CARTOES SEM LIGACAO».
    No grafo inteiro a coleta nao tem um unico orfao. Na tela, tem — porque a
    tela mostra UMA vista de cada vez, e um cartao pode ter todas as suas
    ligacoes para vizinhos que nao estao naquela vista.

        ORFAO NO GRAFO   e um buraco de arquitetura.
        ORFAO NA VISTA   e um efeito da lente, e nao quer dizer nada sobre o
                         sistema — mas parece exactamente igual a quem olha.

    Distinguir os dois e o que impede alguem de ir procurar um dono que nunca
    faltou. Um cartao que aparece aqui NAO precisa de ligacao nova: precisa de
    estar na mesma vista de quem ja fala com ele, ou de nao estar naquela vista
    de todo.
    """
    fora = {}
    vistas = sorted({v for n in N.values() for v in (n.get('views') or [])})
    for vista in vistas:
        dentro = {i for i, n in N.items() if vista in (n.get('views') or [])}
        grau = {}
        for e in E:
            if e['from'] in dentro and e['to'] in dentro:
                grau[e['from']] = grau.get(e['from'], 0) + 1
                grau[e['to']] = grau.get(e['to'], 0) + 1
        for i in dentro:
            if grau.get(i):
                continue
            vizinhos = [e['to'] if e['from'] == i else e['from']
                        for e in E if i in (e['from'], e['to'])]
            if vizinhos:      # tem ligacoes — so nao NESTA vista
                fora.setdefault(i, []).append(vista)
    return fora


def porque_sozinho(n, grau):
    """A razao de um cartao nao ter ligacao. UNKNOWN e uma resposta."""
    if grau:
        return None
    t, k = n.get('territory'), n.get('kind')
    if t == 'Z-PROVA' or k == 'test':
        return 'SO_PROVA'
    if t in ('Z-REGUAS', 'Z-REGRAS') or k == 'contract':
        return 'SO_REGRA'
    if t == 'Z-ENTRADA' or k == 'workflow':
        return 'ENTRADA'
    if k == 'acervo':
        return 'ARMAZEM'
    if not n.get('files'):
        return 'CONCEITO_MEDIDO'
    return 'UNKNOWN'


def medir():
    """A MEDICAO, SEM UMA LINHA DE FORMATO. E so isto que le a arvore."""
    S = json.load(open(ESTADO, encoding='utf-8'))
    N = {n['id']: n for n in S['NODES']}
    E = S['EDGES']
    # ── AS TRES POPULACOES, SEPARADAS NA ORIGEM ──────────────────────────
    # Elas ja eram tres; o codigo antigo somava-as numa variavel so chamada
    # `universo` e a distincao morria ali, dentro da funcao. Persistir a soma
    # sem persistir as parcelas seria publicar 111 sem poder responder «111
    # do que?» — que e exactamente a pergunta que o G2 veio fechar.
    #
    #     UM VIZINHO DA COLETA NAO VIRA MEMBRO DA COLETA.
    colecao = sorted(i for i, n in N.items() if n.get('family') in LADO_DA_COLETA)
    dentro = set(colecao)
    tocam = set()
    for e in E:
        if e['from'] in dentro:
            tocam.add(e['to'])
        if e['to'] in dentro:
            tocam.add(e['from'])
    vizinhos = sorted(tocam - dentro)
    universo = sorted(dentro | tocam)

    grau = {}
    for e in E:
        grau[e['from']] = grau.get(e['from'], 0) + 1
        grau[e['to']] = grau.get(e['to'], 0) + 1

    RAIZES, ALCANCADOS = alcancaveis_do_runtime()
    FALSOS = orfaos_por_vista(N, E)

    fichas = []
    for i in universo:
        n = N[i]
        fs = n.get('files') or []
        rt, md = chamadores(fs)
        cli = documentado_como_cli(fs)
        esc, le = escreve_le(fs)
        ent = [e for e in E if e['to'] == i]
        sai = [e for e in E if e['from'] == i]
        fichas.append({
            'CARD_ID': i, 'NOME': n['name'],
            'FAMILIA': n.get('family'), 'TERRITORIO': n.get('territory'),
            'KIND': n.get('kind'), 'STATUS': n.get('status'),
            'FICHEIROS': fs,
            'CHAMADORES_DE_RUNTIME': rt,
            'SO_MEDEM_ESTE': md,
            'DOCUMENTADO_COMO_CLI': cli,
            # ⚠️ UM WORKFLOW E O PROPRIO BOTAO. A regra de alcance procura os
            # ficheiros CITADOS DENTRO de um workflow — e um `.yml` nunca se
            # cita a si mesmo, entao os cartoes de despacho apareciam «sem
            # chamador». O chamador deles e uma pessoa a carregar no botao.
            #
            #     SER O ENTRYPOINT NAO E NAO TER CHAMADOR.
            'E_ENTRYPOINT': bool(set(fs) & RAIZES) or any(
                f.startswith(('.github/workflows/', 'motor/'))
                and f.endswith(('.yml', '.sh')) for f in fs),
            'ALCANCADO_POR_CORRIDA': bool(set(fs) & ALCANCADOS),
            'RUNTIME_OBSERVADO': (bool(rt) or bool(set(fs) & ALCANCADOS)
                                  or any(f.startswith(('.github/workflows/', 'motor/'))
                                         and f.endswith(('.yml', '.sh')) for f in fs)),
            'ESCREVE_EM': esc, 'LE_DE': le,
            'ENTRAM': len(ent), 'SAEM': len(sai),
            'CATEGORIAS_QUE_ENTRAM': sorted({e.get('categoria') for e in ent}),
            'CATEGORIAS_QUE_SAEM': sorted({e.get('categoria') for e in sai}),
            'PORQUE_SOZINHO': porque_sozinho(n, grau.get(i, 0)),
            'ORFAO_FALSO_NAS_VISTAS': FALSOS.get(i, []),
            'GAP': n.get('gap'),
        })

    rel = [e for e in E if e['from'] in set(universo) or e['to'] in set(universo)]
    # Travessias de familia: da coleta para a inteligencia, uma a uma.
    atravessa = [e for e in E
                 if N.get(e['from'], {}).get('family') == 'F-COLETA'
                 and N.get(e['to'], {}).get('family') == 'F-INTELIGENCIA']

    resumo = {
        'CARTOES_NO_UNIVERSO': len(universo),
        'CARTOES_AUDITADOS': len(fichas),
        'ARESTAS_RELACIONADAS': len(rel),
        'ENTRYPOINTS': sorted(f['CARD_ID'] for f in fichas if f['E_ENTRYPOINT']),
        'ALCANCADOS_POR_UMA_CORRIDA': sorted(
            f['CARD_ID'] for f in fichas if f['ALCANCADO_POR_CORRIDA']),
        'SEM_CHAMADOR_DE_RUNTIME': sorted(
            f['CARD_ID'] for f in fichas if f['FICHEIROS'] and not f['RUNTIME_OBSERVADO']),
        'SO_CLI_DOCUMENTADO': sorted(
            f['CARD_ID'] for f in fichas
            if f['FICHEIROS'] and not f['RUNTIME_OBSERVADO'] and f['DOCUMENTADO_COMO_CLI']),
        'NINGUEM_CORRE': sorted(
            f['CARD_ID'] for f in fichas
            if f['FICHEIROS'] and not f['RUNTIME_OBSERVADO']
            and not f['DOCUMENTADO_COMO_CLI'] and not f['SO_MEDEM_ESTE']),
        'SEM_LIGACAO': {f['CARD_ID']: f['PORQUE_SOZINHO']
                        for f in fichas if f['PORQUE_SOZINHO']},
        'ORFAOS_FALSOS_POR_VISTA': {k: v for k, v in sorted(FALSOS.items())},
        'SEM_LIGACAO_INEXPLICADOS': sorted(
            f['CARD_ID'] for f in fichas if f['PORQUE_SOZINHO'] == 'UNKNOWN'),
        'CATEGORIAS_DAS_ARESTAS': {
            c: len([e for e in rel if e.get('categoria') == c])
            for c in sorted({e.get('categoria') for e in rel} - {None})},
        'GAPS_NOMEADOS': sorted({f['GAP'] for f in fichas if f['GAP']}),
        # ── A FRONTEIRA, CONTADA ─────────────────────────────────────────
        # A queixa que abriu esta missao foi «cartoes da coleta ligados
        # direto a inteligencia». Sao 149 travessias, e o numero sozinho da
        # razao a queixa. Repartido, diz outra coisa: 138 delas vao parar a
        # Z-PROVA — a zona das PROVAS, que esta arrumada debaixo de
        # F-INTELIGENCIA por nao haver familia para ela. Uma prova a ler o
        # que a coleta produziu e o trabalho dela, e nao uma fuga de dado.
        #
        #     UMA PROVA NAO E A INTELIGENCIA.
        #
        # Ao motor propriamente dito (Z-MOTOR) chegam SEIS, e nenhuma leva
        # dado. Nao mudo familia nenhuma aqui: a familia e do desenho, e o
        # desenho e de gente. Deixo o numero a vista para a pergunta poder
        # ser feita com ele em cima da mesa.
        'TRAVESSIAS_COLETA_PARA_INTELIGENCIA': len(atravessa),
        'TRAVESSIAS_POR_ZONA_DE_DESTINO': {
            z: len([e for e in atravessa if N[e['to']]['territory'] == z])
            for z in sorted({N[e['to']]['territory'] for e in atravessa})},
        'TRAVESSIAS_POR_CATEGORIA': {
            c: len([e for e in atravessa if e.get('categoria') == c])
            for c in sorted({e.get('categoria') or 'UNKNOWN' for e in atravessa})},
        'TRAVESSIAS_QUE_LEVAM_DADO': len(
            [e for e in atravessa if e.get('categoria') == 'DATA']),
    }

    return {'COLECAO': colecao, 'VIZINHOS': vizinhos, 'UNIVERSO': universo,
            'FICHAS': fichas, 'ARESTAS': rel, 'RESUMO': resumo}


# ─────────────────────────────────────────────────────────────────────────
# SERIALIZAR — O CENSO PASSA A DEIXAR RASTO
#
#     STDOUT NAO E MEMORIA DURAVEL.
#
# Este censo publicava 111, 65, 590 e mais catorze numeros, e nao escrevia
# ficheiro nenhum. Um numero que so existe enquanto alguem olha para o
# terminal nao pode ser comparado amanha — e por isso nao pode envelhecer a
# vista de ninguem. Quem quisesse o numero copiava-o para um `.md` a mao, e
# a partir dai o `.md` era o segundo dono de uma medicao que ninguem refazia.
#
# MEDIR -> SERIALIZAR -> VALIDAR, e os tres no MESMO dono. Nao ha segundo
# censo: `medir()` acima continua a ser a unica implementacao da medicao, e
# tudo o que esta daqui para baixo apenas lhe da forma, carimbo e conferencia.
#
# ⚠️ CONFERIR NAO E PROVAR. O contrato proibe auto-prova (§13.1): um artefacto
# nao fica verdadeiro por o gerador o ter escrito e aprovado contra os proprios
# dados. `conferir()` e um PORTAO DE SAIDA — recusa escrever um ficheiro que
# ja nasce incoerente. Quem VALIDA e outro processo: `test_topologia_persistida.py`
# regenera numa copia e compara com o que esta commitado, sem partilhar estado
# com quem escreveu.
# ─────────────────────────────────────────────────────────────────────────
SAIDA = os.path.join(RAIZ, 'system-map', 'data', 'topologia.generated.json')
SCHEMA = 'sintonia.system-map.topologia/1'
NAO_SEI = 'NAO SEI'
PLANOS = ('DECLARED', 'CODE', 'OBSERVED', 'PROVEN')
VALORES_DE_PLANO = ('YES', 'NO', 'UNKNOWN')

# A ESPECIE DO QUE ESTE CENSO CONTA — declarada por quem conta, uma vez so.
# `reconciliacao_do_universo.py` importa-a daqui, como ja importa a regra de
# entrada. Escrever a palavra nos dois ficheiros criava dois donos do mesmo
# facto, e bastava um deles mudar para a contagem voltar a nao dizer o que conta.
ESPECIE_DO_UNIVERSO = 'SYSTEM_MAP_VISUAL_CARD'

# O que muda a cada corrida sem que nada de substantivo tenha mudado. Sai do
# hash semantico, e por isso duas corridas na mesma arvore dao o mesmo numero.
# `HEAD` esta aqui pela lei ja aprendida: um ficheiro commitado nunca nomeia o
# commit que o contem, logo um SHA de commit nunca prova frescura de nada.
CAMPOS_VOLATEIS = ('GENERATED_AT', 'HEAD', 'BRANCH', 'SEMANTIC_HASH')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import impressao_da_arvore as IMPRESSAO          # noqa: E402


def git(*args):
    r = subprocess.run(['git', '-C', RAIZ, *args], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    return r.stdout.rstrip('\n')


def entradas(fichas):
    """OS FICHEIROS QUE ESTE CENSO ABRE, COM A VERSAO DE CADA UM.

    Nao e a lista de dependencias que seria bonito ter: e a lista dos caminhos
    que o codigo acima ABRE de facto. Declarar uma dependencia que ninguem le
    seria inventar proveniencia, e proveniencia inventada e pior do que nenhuma.

    A VERSAO DE CADA UM NAO E O SHA DO FICHEIRO — E DE PROPOSITO.

    Os dois `.generated.json` que este censo le sao reescritos a cada corrida da
    cadeia, e o carimbo deles carrega `HEAD` e `GENERATED_AT`. Se a versao fosse
    o SHA do conteudo, regerar o mapa SEM MUDAR NADA movia a versao, e este
    artefacto nascia STALE em toda a corrida de CI — um alarme que toca sempre
    nao e um alarme. A versao de um artefacto gerado e a IMPRESSAO DA ARVORE QUE
    ELE CARIMBA: ela responde «que fontes mediste?», que e a pergunta certa.

        A PERGUNTA NAO E «QUE BYTES?». E «QUE ARVORE MEDISTE?».

    Para os ficheiros de FONTE a versao e o SHA do blob que o git guardaria —
    o mesmo numero que a impressao da arvore usa, pedido ao mesmo git.
    """
    gerados = [
        ('system-map/data/state.generated.json', 'main() · json.load'),
        ('system-map/data/architecture.generated.json',
         'alcancaveis_do_runtime() · json.load'),
    ]
    fontes = set()
    for padrao in ('.github/workflows/*.yml', 'motor/*.sh', 'provas/*.sh'):
        for p in glob.glob(os.path.join(RAIZ, padrao)):
            fontes.add(os.path.relpath(p, RAIZ).replace(os.sep, '/'))
    for f in fichas:
        for c in f['FICHEIROS']:
            if c.endswith(('.py', '.mjs', '.js')) and os.path.isfile(os.path.join(RAIZ, c)):
                fontes.add(c)

    itens, ausentes = [], []
    for caminho, lido_por in gerados:
        p = os.path.join(RAIZ, caminho)
        if not os.path.isfile(p):
            ausentes.append(caminho)
            continue
        try:
            prov = (json.load(open(p, encoding='utf-8')).get('PROVENANCE') or {})
        except (OSError, ValueError):
            prov = {}
        itens.append({
            'PATH': caminho, 'PAPEL': 'GERADO',
            'VERSAO': prov.get('SOURCE_TREE_FINGERPRINT') or NAO_SEI,
            'COMO_SE_MEDE': 'SOURCE_TREE_FINGERPRINT que o proprio artefacto carimba',
            'LIDO_POR': lido_por,
        })
    presentes = sorted(f for f in fontes if os.path.isfile(os.path.join(RAIZ, f)))
    ausentes += sorted(f for f in fontes if not os.path.isfile(os.path.join(RAIZ, f)))
    for caminho, sha in zip(presentes, IMPRESSAO.sha_do_disco(presentes)):
        itens.append({
            'PATH': caminho, 'PAPEL': 'FONTE', 'VERSAO': sha,
            'COMO_SE_MEDE': 'SHA do blob que o git guardaria deste caminho',
            'LIDO_POR': ('alcancaveis_do_runtime() · open'
                         if caminho.startswith(('.github/workflows/', 'motor/', 'provas/'))
                         else 'escreve_le() · open'),
        })
    itens.sort(key=lambda x: x['PATH'])
    return itens, sorted(set(ausentes))


def selo_das_entradas(itens):
    """UMA FORMULA DE SELAGEM SO. A de `impressao_da_arvore`, sem copia."""
    return IMPRESSAO._selar(['%s %s' % (i['VERSAO'], i['PATH']) for i in itens])


# O QUE FOI MEDIDO, SEM UMA PALAVRA SOBRE QUEM MEDIU OU QUANDO.
#
#     «AS CONTAGENS REPRODUZEM-SE?»  !=  «O FICHEIRO E O MESMO?»
#
# Sao duas perguntas, e usar um numero so para as duas responde mal as duas. O
# `SEMANTIC_HASH` inclui a proveniencia — tem de incluir, senao adulterar um
# carimbo passava despercebido — e por isso MUDA quando se toca em qualquer
# fonte da arvore, mesmo num comentario que nao move numero nenhum. Usa-lo para
# dizer «as contagens deixaram de reproduzir» era gritar a cada commit.
#
# O `MEASUREMENT_HASH` cobre so o que o censo MEDIU. Ele muda quando o grafo
# muda, e fica quieto quando so a arvore a volta mudou.
BLOCOS_MEDIDOS = ('UNIVERSE', 'BOUNDARY_NEIGHBORS', 'EXPANDED', 'ARITMETICA',
                  'EDGES', 'RESUMO', 'FICHAS')

# ─────────────────────────────────────────────────────────────────────────
# NADA FICA DE FORA DESTA CONTA — E ISSO NEM SEMPRE FOI VERDADE
#
# O G2 tirou `DOCUMENTADO_COMO_CLI` (e os dois campos do RESUMO que dele
# derivam) desta conta, porque o campo nao se reproduzia entre maquinas. Era a
# saida honesta para uma medicao que nao cumpria o que prometia — e era uma
# divida, nao uma solucao:
#
#     UM CAMPO PUBLICADO QUE NAO ENTRA NA PROVA SEMANTICA
#     E UM CAMPO QUE NINGUEM ESTA A GUARDAR.
#
# O G2B fechou a divida na origem: a lista de documentos passou a vir de
# `git ls-files`, ordenada, lida inteira, e o campo passou a trazer TODOS os
# documentos que casam. Medido em duas arvores do mesmo commit, uma em ext4 e
# outra em tmpfs: DEZ cartoes divergiam antes, ZERO divergem depois.
#
# A excepcao foi REMOVIDA, e nao alargada. Fica declarada aqui vazia de
# proposito: uma lista de exclusao que desaparece do codigo volta a nascer no
# dia em que alguem tiver pressa.
CAMPOS_NAO_REPRODUZIVEIS: dict = {}


def hash_da_medicao(doc):
    return hashlib.sha256(json.dumps(
        {k: doc.get(k) for k in BLOCOS_MEDIDOS},
        sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def hash_semantico(doc):
    """O QUE ESTE ARTEFACTO DIZ, SEM O QUE MUDA SO POR TER CORRIDO OUTRA VEZ.

    ⚠️ UM RESUMO QUE SE INCLUI A SI PROPRIO NUNCA ESTABILIZA — a mesma lei da
    impressao da arvore, um nivel acima. Por isso `SEMANTIC_HASH` sai da conta
    antes de ser calculado.
    """
    d = json.loads(json.dumps(doc, ensure_ascii=False))
    for k in CAMPOS_VOLATEIS:
        (d.get('PROVENANCE') or {}).pop(k, None)
    return hashlib.sha256(
        json.dumps(d, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def _aresta(e):
    """A ARESTA COMO O G1 A DEIXOU. Nao ha aqui um `status` a decidir nada.

        ANALISE ESTATICA PROVA CAN DO. SO TELEMETRIA PROVA DID DO.

    Os quatro planos viajam separados, e a evidencia viaja a dizer QUE
    AFIRMACAO sustenta. Achatar isto outra vez num `status=PROVEN` era desfazer
    o G1 dentro do G2, em silencio.
    """
    d = {
        'EDGE_ID': '%s--%s-->%s' % (e['from'], e['type'], e['to']),
        'FROM': e['from'], 'TO': e['to'],
        'RELATION_TYPE': e.get('type'),
        'CATEGORIA': e.get('categoria'),
        'PROVEN_PLANE': e.get('PROVEN_PLANE'),
    }
    for p in PLANOS:
        d[p] = e.get(p)
    d['EVIDENCE_BINDING'] = [{
        'FICHEIRO': v.get('file'), 'LINHA': v.get('line'),
        'SUPPORTS': v.get('SUPPORTS'),
        'EVIDENCE_TYPE': v.get('EVIDENCE_TYPE'),
        'ASSERTION_EDGE_ID': (v.get('ASSERTION_SUPPORTED') or {}).get('EDGE_ID'),
        'ASSERTION_PLANE': (v.get('ASSERTION_SUPPORTED') or {}).get('PLANE'),
    } for v in (e.get('evidence') or [])]
    return d


def serializar(med):
    """A FORMA. Nao mede nada, nao decide nada: da nome ao que `medir()` viu."""
    impressao, n_ficheiros, fora_do_disco = IMPRESSAO.do_disco()
    itens, ausentes = entradas(med['FICHAS'])
    doc = {
        'SCHEMA': SCHEMA,
        'NOTA': [
            'O CENSO DA TOPOLOGIA DA COLETA, PERSISTIDO.',
            '',
            'Ate aqui este censo so imprimia. Um numero publicado que nao deixa',
            'artefacto nao pode ser comparado amanha, e por isso nao consegue',
            'envelhecer a vista de ninguem.',
            '',
            '    STDOUT NAO E MEMORIA DURAVEL.',
            '',
            'TRES POPULACOES, E ELAS NAO SE SOMAM NUMA SO:',
            '',
            '    UNIVERSE            a coleta e a espera, por FAMILIA',
            '    BOUNDARY_NEIGHBORS  quem lhes toca por aresta e nao e delas',
            '    EXPANDED            a uniao — e a uniao NAO E A COLETA MAIOR',
            '',
            'O numero grande do RESUMO (`CARTOES_NO_UNIVERSO`) e o EXPANDIDO, e',
            'esse nome e anterior a esta missao. Ele fica como estava, porque',
            'mudar a semantica do censo nao era trabalho desta missao; o que',
            'mudou e que agora ha onde ver, membro a membro, de que populacao',
            'cada numero saiu.',
            '',
            '    UM VIZINHO DA COLETA NAO VIRA MEMBRO DA COLETA.',
            '',
            'Este ficheiro e GERADO. Editar a mao e detectado: `SEMANTIC_HASH`',
            'deixa de bater e `test_topologia_persistida.py` reprova.',
        ],
        'PROVENANCE': {
            'OWNER': 'system-map/scripts/censo_da_topologia.py',
            'GENERATED_BY': 'system-map/scripts/censo_da_topologia.py',
            'GENERATED_AT': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'HEAD': git('rev-parse', 'HEAD'),
            'BRANCH': git('rev-parse', '--abbrev-ref', 'HEAD'),
            'HEAD_VERIFICAVEL': False,
            'HEAD_PORQUE_NAO': ('um ficheiro commitado nunca nomeia o commit que o '
                                'contem. A prova de frescura e SOURCE_TREE_FINGERPRINT.'),
            'SOURCE_TREE_FINGERPRINT': impressao,
            'FICHEIROS_NA_IMPRESSAO': n_ficheiros,
            'FICHEIROS_RASTREADOS_AUSENTES_DO_DISCO': fora_do_disco,
            'INPUTS': itens,
            'INPUTS_COUNT': len(itens),
            'INPUTS_DIGEST': selo_das_entradas(itens),
            'INPUTS_AUSENTES': ausentes,
            'INPUTS_NAO_ENUMERAVEIS': [{
                'O_QUE': 'a varredura `grep -rn` de `chamadores()` e `documentado_como_cli()`',
                'PORQUE': ('o conjunto de ficheiros que o grep toca depende da arvore, '
                           'e nao esta escrito em lado nenhum do codigo: nao ha lista '
                           'para carimbar.'),
                'FICA_COBERTO_POR': ('SOURCE_TREE_FINGERPRINT — a varredura so ve ficheiros '
                                     'de fonte, e todos eles entram na impressao da arvore.'),
            }],
            'CAMPOS_VOLATEIS': list(CAMPOS_VOLATEIS),
            'BLOCOS_DA_MEDICAO': list(BLOCOS_MEDIDOS),
            'CAMPOS_FORA_DO_MEASUREMENT_HASH': {
                bloco: list(campos)
                for bloco, campos in CAMPOS_NAO_REPRODUZIVEIS.items()},
            'CAMPOS_FORA_DO_MEASUREMENT_HASH_PORQUE': (
                'nenhum. O G2 tinha excluido DOCUMENTADO_COMO_CLI e os dois campos '
                'do RESUMO que dele derivam, por a medicao depender da ordem do '
                'sistema de ficheiros; o G2B fechou essa dependencia na origem e a '
                'excepcao foi removida. Todo campo medido entra nesta conta.'),
            'DOCUMENTOS_LIDOS': len(documentos_da_arvore()),
            'DOCUMENTOS_AUSENTES_DO_DISCO': list(DOCUMENTOS_AUSENTES_DO_DISCO),
            'FONTE_DOS_DOCUMENTOS': ('git ls-files · so o que esta rastreado · '
                                     'ordem lexical'),
            'DEPENDENCIES': [i['PATH'] for i in itens if i['PAPEL'] == 'GERADO'],
        },
        'UNIVERSE': {
            'UNIVERSE_ID': 'TOPOLOGY_COLLECTION_UNIVERSE',
            'ENTITY_SPECIES': ESPECIE_DO_UNIVERSO,
            'DEFINITION': ('os cartoes da coleta e da sua sala de espera. E uma '
                           'populacao de FAMILIA, e nada aqui entra por vizinhanca.'),
            'INCLUSION_RULE': 'family in %s' % (list(LADO_DA_COLETA),),
            'EXCLUSION_RULE': 'qualquer outra familia, mesmo que ligada por aresta.',
            'OWNER': 'system-map/scripts/censo_da_topologia.py · LADO_DA_COLETA',
            'PARENT_UNIVERSE_ID': 'SYSTEM_MAP_NODE_UNIVERSE',
            'MEMBERS': med['COLECAO'],
            'COUNT': len(med['COLECAO']),
        },
        'BOUNDARY_NEIGHBORS': {
            'UNIVERSE_ID': 'TOPOLOGY_BOUNDARY_NEIGHBORS',
            'ENTITY_SPECIES': ESPECIE_DO_UNIVERSO,
            'DEFINITION': ('quem esta ligado por aresta a alguem da coleta e NAO e '
                           'da coleta. A vista tem de os mostrar, senao o cartao de '
                           'dentro parece orfao; o universo continua a ser outro.'),
            'INCLUSION_RULE': 'tem aresta de ou para um membro de UNIVERSE',
            'EXCLUSION_RULE': 'ja ser membro de UNIVERSE',
            'NAO_E': 'membro da coleta. Somar isto a coleta e o ataque 15 do contrato.',
            'MEMBERS': med['VIZINHOS'],
            'COUNT': len(med['VIZINHOS']),
        },
        'EXPANDED': {
            'UNIVERSE_ID': 'TOPOLOGY_EXPANDED_UNIVERSE',
            'ENTITY_SPECIES': ESPECIE_DO_UNIVERSO,
            'DEFINITION': 'UNIVERSE mais BOUNDARY_NEIGHBORS. E o que o censo audita.',
            'MEMBERS': med['UNIVERSO'],
            'COUNT': len(med['UNIVERSO']),
        },
        'ARITMETICA': {
            'COLLECTION': len(med['COLECAO']),
            'BOUNDARY': len(med['VIZINHOS']),
            'SOMA': len(med['COLECAO']) + len(med['VIZINHOS']),
            'EXPANDED': len(med['UNIVERSO']),
            'FECHA': len(med['COLECAO']) + len(med['VIZINHOS']) == len(med['UNIVERSO']),
            'INTERSECAO': sorted(set(med['COLECAO']) & set(med['VIZINHOS'])),
            'RESUMO_CARTOES_NO_UNIVERSO': med['RESUMO']['CARTOES_NO_UNIVERSO'],
            'NOTA': ('`RESUMO.CARTOES_NO_UNIVERSO` conta o EXPANDIDO, e sempre contou. '
                     'O nome e anterior a esta missao e nao foi mudado aqui.'),
        },
        'EDGES': {
            'DEFINITION': ('as arestas com pelo menos uma ponta no universo expandido. '
                           'Modelo G1: quatro planos que nao se promovem, e a evidencia '
                           'a dizer que afirmacao sustenta.'),
            'MODELO': 'DECLARED · CODE · OBSERVED · PROVEN (+ PROVEN_PLANE)',
            'ORDEM': 'EDGE_ID crescente',
            'MEMBERS': sorted((_aresta(e) for e in med['ARESTAS']),
                              key=lambda d: d['EDGE_ID']),
            'COUNT': len(med['ARESTAS']),
        },
        'RESUMO': med['RESUMO'],
        'FICHAS': med['FICHAS'],
        'LIMITATIONS': [
            'MEDE, NAO DECIDE. Nao cria aresta, nao move cartao, nao muda familia '
            'nem territorio, nao atribui ROLE. Um numero daqui nunca e um veredito '
            'de arquitetura.',
            'GREP NAO E RUNTIME. `CHAMADORES_DE_RUNTIME` sai de uma varredura de '
            'texto: ela prova CITACAO, nao execucao. Nenhum campo deste ficheiro '
            'prova que alguma coisa CORREU.',
            'RUNTIME_OBSERVADO E UM NOME HERDADO E NAO E OBSERVACAO: ele soma '
            'citacao em workflow, alcance por import estatico e ser entrypoint. '
            'Isso e o plano CODE. Telemetria nao entra aqui.',
            'A FRESCURA DESTE FICHEIRO NAO SE LE NELE. Um artefacto nao se declara '
            'actual a si proprio (§13.1). Quem responde CURRENT/STALE e '
            '`frescura()`, corrida por outro processo contra a arvore de agora.',
            'INPUTS SO CONHECE O QUE O CODIGO ABRE POR CAMINHO. A varredura `grep` '
            'nao e enumeravel e fica coberta pela impressao da arvore, nao por '
            'INPUTS_DIGEST.',
            'UMA ENTRADA GERADA EDITADA A MAO SEM REGERAR NAO MOVE A VERSAO DELA: '
            'a versao e a impressao que ela carimba. Quem apanha esse caso e a P1 '
            'do validador, que regenera e compara — nao este ficheiro.',
            # ⚠️ ACHADO DA MISSAO G2, DECLARADO E NAO CORRIGIDO.
            # Persistir uma medicao obriga a perguntar se ela e reproduzivel, e a
            # pergunta encontrou isto. Corrigi-lo seria mudar a semantica do censo,
            # e isso nao era trabalho desta missao — declara-lo e.
            'DOCUMENTADO_COMO_CLI SO VE DOCUMENTOS RASTREADOS. Um `.md` por '
            'commitar nao conta, de proposito: a garantia desta medicao e «a mesma '
            'arvore GIT da a mesma resposta», e deixa-la depender de trabalho solto '
            'quebrava-a. Medido nesta arvore: 287 `.md` rastreados, zero por '
            'rastrear e zero ignorados — o conjunto e o mesmo que a versao anterior '
            'via, logo a mudanca de fonte nao mudou quem entra na conta.',
            'ELE LISTA TODOS OS DOCUMENTOS QUE CASAM, E NAO UM. A versao anterior '
            'parava no primeiro e o «primeiro» era o que o disco devolvesse '
            'primeiro. A pergunta nao mudou — «ha documentacao que ensine a correr '
            'isto?» — mudou a testemunha: era uma a esmo, passou a ser a lista.',
            'A VARREDURA `head -60` DE `chamadores()` CONTINUA A SER UM `grep -r`, '
            'e e a ultima parte desta medicao que depende do disco. Ela nao foi '
            'vista a divergir: os resultados dela sao CONJUNTOS ordenados, e zero '
            'ficheiros de cartao desta arvore chegam as 60 linhas. Medido em duas '
            'arvores do mesmo commit, uma em ext4 e outra em tmpfs: identica. O '
            'risco e latente e esta declarado; a prova volta a compara-lo a cada '
            'corrida, e em duas arvores.',
            'STALE_BY_CYCLE E NOMEADO, NAO REPARADO. Se uma entrada gerada mediu '
            'outra arvore, `frescura()` recusa dizer CURRENT e diz qual — mas nao '
            'reordena a cadeia nem regenera nada. Ordenar a cadeia pelos INPUTS '
            'declarados e o G5, e nao foi feito aqui.',
        ],
    }
    doc['PROVENANCE']['MEASUREMENT_HASH'] = hash_da_medicao(doc)
    doc['PROVENANCE']['SEMANTIC_HASH'] = hash_semantico(doc)
    return doc


def conferir(doc):
    """O PORTAO DE SAIDA. Devolve as queixas; lista vazia e que e passar.

    Serve dois momentos com o mesmo codigo: antes de escrever (o gerador recusa
    escrever incoerencia) e depois de ler (outro processo confere o que esta no
    disco). O segundo e que e validacao; o primeiro e higiene.
    """
    q = []
    if doc.get('SCHEMA') != SCHEMA:
        q.append('SCHEMA=%r esperado %r' % (doc.get('SCHEMA'), SCHEMA))
    for bloco in ('PROVENANCE', 'UNIVERSE', 'BOUNDARY_NEIGHBORS', 'EXPANDED',
                  'ARITMETICA', 'EDGES', 'RESUMO', 'FICHAS', 'LIMITATIONS'):
        if bloco not in doc:
            q.append('BLOCO_EM_FALTA=%s' % bloco)
    if q:
        return q

    # ── CONTAGEM TEM MEMBROS, E SAO ESTES ────────────────────────────────
    for nome in ('UNIVERSE', 'BOUNDARY_NEIGHBORS', 'EXPANDED'):
        b = doc[nome]
        m = b.get('MEMBERS')
        if not isinstance(m, list):
            q.append('%s.MEMBERS nao e lista' % nome)
            continue
        if b.get('COUNT') != len(m):
            q.append('%s.COUNT=%s mas MEMBERS=%d' % (nome, b.get('COUNT'), len(m)))
        if len(set(m)) != len(m):
            q.append('%s tem membro duplicado' % nome)
        if m != sorted(m):
            q.append('%s.MEMBERS fora de ordem' % nome)
        if not b.get('ENTITY_SPECIES'):
            q.append('%s sem ENTITY_SPECIES' % nome)
        if not b.get('UNIVERSE_ID'):
            q.append('%s sem UNIVERSE_ID' % nome)
        if not b.get('DEFINITION'):
            q.append('%s sem DEFINITION' % nome)

    col = set(doc['UNIVERSE'].get('MEMBERS') or [])
    viz = set(doc['BOUNDARY_NEIGHBORS'].get('MEMBERS') or [])
    exp = set(doc['EXPANDED'].get('MEMBERS') or [])
    # ── O VIZINHO NAO VIRA MEMBRO ────────────────────────────────────────
    if col & viz:
        q.append('VIZINHO_CONTADO_COMO_COLETA=%s' % sorted(col & viz)[:5])
    if col | viz != exp:
        q.append('EXPANDED nao e a uniao das duas populacoes')
    a = doc['ARITMETICA']
    if a.get('COLLECTION') != len(col) or a.get('BOUNDARY') != len(viz):
        q.append('ARITMETICA nao bate com os membros')
    if a.get('SOMA') != a.get('COLLECTION', 0) + a.get('BOUNDARY', 0):
        q.append('ARITMETICA.SOMA errada')
    if a.get('EXPANDED') != len(exp) or not a.get('FECHA'):
        q.append('ARITMETICA nao fecha: %s + %s != %s'
                 % (a.get('COLLECTION'), a.get('BOUNDARY'), a.get('EXPANDED')))

    # ── AS ARESTAS, NO MODELO G1 ─────────────────────────────────────────
    E = doc['EDGES']
    ms = E.get('MEMBERS')
    if not isinstance(ms, list):
        q.append('EDGES.MEMBERS nao e lista')
    else:
        if E.get('COUNT') != len(ms):
            q.append('EDGES.COUNT=%s mas MEMBERS=%d' % (E.get('COUNT'), len(ms)))
        ids = [x.get('EDGE_ID') for x in ms]
        if len(set(ids)) != len(ids):
            q.append('EDGE_ID duplicado')
        if ids != sorted(ids):
            q.append('EDGES.MEMBERS fora de ordem')
        for x in ms:
            falta = [k for k in ('EDGE_ID', 'FROM', 'TO', 'RELATION_TYPE') if not x.get(k)]
            if falta:
                q.append('aresta %s sem %s' % (x.get('EDGE_ID'), falta))
                break
            mau = [p for p in PLANOS if x.get(p) not in VALORES_DE_PLANO]
            if mau:
                q.append('aresta %s com plano fora do vocabulario: %s'
                         % (x['EDGE_ID'], [(p, x.get(p)) for p in mau]))
                break
            if x['EDGE_ID'] != '%s--%s-->%s' % (x['FROM'], x['RELATION_TYPE'], x['TO']):
                q.append('EDGE_ID nao descreve a propria aresta: %s' % x['EDGE_ID'])
                break

    # ── AS FICHAS SAO AS DO UNIVERSO EXPANDIDO ───────────────────────────
    fichas = doc.get('FICHAS') or []
    ids_f = [f.get('CARD_ID') for f in fichas]
    if sorted(ids_f) != sorted(exp):
        q.append('FICHAS nao cobrem o universo expandido (%d fichas, %d membros)'
                 % (len(ids_f), len(exp)))
    if doc['RESUMO'].get('CARTOES_AUDITADOS') != len(fichas):
        q.append('RESUMO.CARTOES_AUDITADOS nao bate com as fichas')
    if doc['RESUMO'].get('ARESTAS_RELACIONADAS') != E.get('COUNT'):
        q.append('RESUMO.ARESTAS_RELACIONADAS nao bate com EDGES.COUNT')

    # ── PROVENIENCIA ─────────────────────────────────────────────────────
    p = doc['PROVENANCE']
    for k in ('GENERATED_BY', 'GENERATED_AT', 'SOURCE_TREE_FINGERPRINT',
              'INPUTS', 'INPUTS_DIGEST', 'MEASUREMENT_HASH', 'SEMANTIC_HASH'):
        if not p.get(k):
            q.append('PROVENANCE sem %s' % k)
    if p.get('INPUTS') and selo_das_entradas(p['INPUTS']) != p.get('INPUTS_DIGEST'):
        q.append('INPUTS_DIGEST nao e o selo dos INPUTS declarados')
    if not doc.get('LIMITATIONS'):
        q.append('LIMITATIONS vazio')
    if p.get('MEASUREMENT_HASH') and hash_da_medicao(doc) != p['MEASUREMENT_HASH']:
        q.append('MEASUREMENT_HASH nao bate: a medicao no ficheiro foi mexida')
    if p.get('SEMANTIC_HASH') and hash_semantico(doc) != p['SEMANTIC_HASH']:
        q.append('SEMANTIC_HASH nao bate: o ficheiro foi mexido depois de escrito')
    return q


def frescura(doc=None):
    """CURRENT · STALE · UNVERIFIABLE · UNKNOWN — e quem pergunta nao e quem escreveu.

    Tres relogios, nunca um:

        A ARVORE     a impressao das FONTES mudou desde que isto foi medido?
        AS ENTRADAS  algum input declarado esta noutra versao?
        O CICLO      alguma entrada gerada mediu uma arvore que nao e esta?

    Os tres sao precisos porque nenhum ve o do outro: os `.generated.json` que
    este censo le estao FORA da impressao da arvore (senao ela perseguia o
    proprio rabo), a varredura `grep` esta fora dos INPUTS, e os dois primeiros
    comparam o artefacto consigo mesmo — nunca com quem o alimentou.
    """
    if doc is None:
        if not os.path.isfile(SAIDA):
            return {'VEREDITO': 'UNKNOWN',
                    'PORQUE': 'nao existe artefacto em %s' % _rel(SAIDA)}
        try:
            doc = json.load(open(SAIDA, encoding='utf-8'))
        except (OSError, ValueError) as x:
            return {'VEREDITO': 'UNVERIFIABLE',
                    'PORQUE': 'artefacto ilegivel: %s' % x}
    p = doc.get('PROVENANCE') or {}
    declarados = p.get('INPUTS') or []
    if not declarados:
        return {'VEREDITO': 'UNVERIFIABLE', 'PORQUE': 'o artefacto nao declara INPUTS'}

    agora, _, _ = IMPRESSAO.do_disco()
    caminhos = [i['PATH'] for i in declarados]
    sumidos = [c for c in caminhos if not os.path.isfile(os.path.join(RAIZ, c))]
    if sumidos:
        return {'VEREDITO': 'UNVERIFIABLE',
                'PORQUE': 'entradas declaradas que ja nao existem: %s' % sumidos[:5],
                'IMPRESSAO_AGORA': agora}

    fontes = [i['PATH'] for i in declarados if i.get('PAPEL') == 'FONTE']
    shas = dict(zip(fontes, IMPRESSAO.sha_do_disco(fontes))) if fontes else {}
    hoje, nao_sei = [], []
    for i in declarados:
        if i.get('PAPEL') == 'FONTE':
            v = shas.get(i['PATH'], NAO_SEI)
        else:
            try:
                prov = (json.load(open(os.path.join(RAIZ, i['PATH']), encoding='utf-8'))
                        .get('PROVENANCE') or {})
            except (OSError, ValueError):
                prov = {}
            v = prov.get('SOURCE_TREE_FINGERPRINT') or NAO_SEI
        if v == NAO_SEI:
            nao_sei.append(i['PATH'])
        hoje.append({'PATH': i['PATH'], 'VERSAO': v})
    if nao_sei:
        return {'VEREDITO': 'UNVERIFIABLE',
                'PORQUE': 'entradas sem versao aferivel: %s' % nao_sei[:5],
                'IMPRESSAO_AGORA': agora}

    selo_agora = selo_das_entradas(hoje)
    mexidas = [i['PATH'] for i, j in zip(declarados, hoje)
               if i.get('VERSAO') != j['VERSAO']]
    arvore_bate = agora == p.get('SOURCE_TREE_FINGERPRINT')
    entradas_batem = selo_agora == p.get('INPUTS_DIGEST')

    # ── O TERCEIRO RELOGIO: A LEI DO CICLO ATRASADO (contrato §9.2) ──────
    #
    #     NENHUM ARTEFACTO E `CURRENT` SE MEDIU O OUTPUT DA GERACAO ANTERIOR
    #     ENQUANTO A SUA SEMANTICA DIZ QUE REPRESENTA A ACTUAL.
    #
    # Os dois relogios de cima comparam este artefacto CONSIGO MESMO no tempo:
    # se ninguem mexeu em nada desde que ele correu, os dois dizem CURRENT — e
    # dizem-no mesmo que ele tenha medido um `state.generated.json` de ha tres
    # arvores atras. Regerar este censo sobre uma entrada velha nao torna a
    # entrada nova; torna a mentira mais recente.
    #
    # A pergunta que falta e outra: CADA ENTRADA GERADA MEDIU ESTA ARVORE?
    # O produtor dela carimba a impressao que mediu; se essa impressao nao e a
    # de agora, este censo leu o output da corrida anterior.
    #
    # E DE PROPOSITO QUE ISTO NAO REPARA NADA. O censo nao regenera a cadeia,
    # nao reordena passos e nao esconde o caso: nomeia-o. Ordenar a cadeia pelos
    # INPUTS declarados e o G5, e nao e trabalho desta missao.
    ciclo = [j['PATH'] for i, j in zip(declarados, hoje)
             if i.get('PAPEL') == 'GERADO' and j['VERSAO'] != agora]

    atual = arvore_bate and entradas_batem and not ciclo
    if atual:
        motivo, porque = 'CURRENT', 'a arvore e as entradas sao as que foram medidas'
    elif ciclo:
        motivo = 'STALE_BY_CYCLE'
        porque = ('entrada gerada que nao mediu esta arvore: %s' % ciclo[:5])
    else:
        motivo = 'ARVORE_MUDOU' if not arvore_bate else 'ENTRADA_MUDOU'
        porque = ('mudou %s%s%s desde a medicao'
                  % ('a arvore' if not arvore_bate else '',
                     ' e ' if not arvore_bate and not entradas_batem else '',
                     'alguma entrada' if not entradas_batem else ''))
    return {
        'VEREDITO': 'CURRENT' if atual else 'STALE',
        'MOTIVO': motivo,
        'ARVORE_BATE': arvore_bate,
        'ENTRADAS_BATEM': entradas_batem,
        'ENTRADAS_GERADAS_DE_OUTRA_ARVORE': ciclo,
        'IMPRESSAO_CARIMBADA': p.get('SOURCE_TREE_FINGERPRINT'),
        'IMPRESSAO_AGORA': agora,
        'INPUTS_DIGEST_CARIMBADO': p.get('INPUTS_DIGEST'),
        'INPUTS_DIGEST_AGORA': selo_agora,
        'ENTRADAS_QUE_MUDARAM': mexidas[:10],
        'PORQUE': porque,
    }


def _rel(caminho):
    return os.path.relpath(caminho, RAIZ).replace(os.sep, '/')


def escrever(doc):
    """ESCREVE INTEIRO OU NAO ESCREVE.

    ⚠️ UM FICHEIRO MEIO ESCRITO NAO E UMA MEDICAO PARCIAL: E LIXO COM AR DE
    ARTEFACTO. O censo demora segundos e le meio repositorio; se a corrida
    morrer a meio de um `write`, o que fica no disco nao e a medicao anterior
    nem a nova — e um JSON truncado que ninguem consegue ler.

    Por isso a escrita vai para um ficheiro ao lado e so depois toma o lugar do
    outro, num `os.replace` que o sistema de ficheiros faz de uma vez. Se a
    corrida morrer, o artefacto ANTERIOR fica intacto — e a frescura dele
    continua a saber dizer se ainda vale.
    """
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    ao_lado = SAIDA + '.a-escrever'
    with open(ao_lado, 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + '\n')
    os.replace(ao_lado, SAIDA)
    return SAIDA


def main():
    doc = serializar(medir())
    queixas = conferir(doc)
    if queixas:
        raise SystemExit('RECUSADO: o artefacto nasceria incoerente:\n  - '
                         + '\n  - '.join(queixas))
    # ── `--nao-escrever`: PARA QUEM SO QUER OS NUMEROS ───────────────────
    # `reconciliacao_do_universo.py` corre este censo para perguntar «as
    # contagens de hoje batem com as commitadas?». Se essa pergunta reescrevesse
    # o ficheiro, ela deixava de ter resposta — ninguem compara um ficheiro com
    # a versao dele que acabou de gravar por cima.
    #
    #     UMA PROVA QUE SUJA A ARVORE MUDA AQUILO QUE MEDE.
    #
    # ⚠️ ISTO NAO E UMA PORTA PARA DESLIGAR A PERSISTENCIA. O caminho canonico —
    # o passo 1b do workflow — corre sem bandeira nenhuma, e
    # `test_topologia_persistida.py` reprova se alguem lhe acrescentar uma.
    if '--nao-escrever' not in sys.argv:
        escrever(doc)

    if '--json' in sys.argv:
        # O MESMO DICIONARIO QUE FOI PARA O DISCO. Serializar duas vezes a
        # partir de duas fontes seria convidar o stdout a divergir do ficheiro.
        print(json.dumps(doc, ensure_ascii=False, indent=1))
        return 0

    resumo = doc['RESUMO']
    print('CENSO DA TOPOLOGIA DA COLETA')
    print('=' * 70)
    print('  %-28s %s' % ('COLETA (universo)', doc['UNIVERSE']['COUNT']))
    print('  %-28s %s' % ('VIZINHOS DE FRONTEIRA', doc['BOUNDARY_NEIGHBORS']['COUNT']))
    print('  %-28s %s' % ('EXPANDIDO (a soma)', doc['EXPANDED']['COUNT']))
    for k, v in resumo.items():
        if isinstance(v, (list, dict)) and len(v) > 6:
            print('  %-28s %s' % (k, len(v)))
        else:
            print('  %-28s %s' % (k, v))
    print()
    print('  %-26s %-9s %-7s %-6s %s' % ('CARD', 'RUNTIME', 'ENTRAM', 'SAEM', 'SOZINHO'))
    print('  ' + '-' * 66)
    for f in doc['FICHAS']:
        print('  %-26s %-9s %-7s %-6s %s'
              % (f['CARD_ID'][:26], 'SIM' if f['RUNTIME_OBSERVADO'] else
                 ('-' if not f['FICHEIROS'] else 'NAO'),
                 f['ENTRAM'], f['SAEM'], f['PORQUE_SOZINHO'] or ''))
    print()
    print('  escrito em %s' % (_rel(SAIDA) if '--nao-escrever' not in sys.argv
                               else '(nada — corrido com --nao-escrever)'))
    f = frescura(doc)
    print('  frescura   %s · %s' % (f['VEREDITO'], f['PORQUE']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
