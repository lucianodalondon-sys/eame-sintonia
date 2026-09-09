#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CENSO DA TOPOLOGIA DA COLETA — cartao a cartao, aresta a aresta.

    python3 system-map/scripts/censo_da_topologia.py
    python3 system-map/scripts/censo_da_topologia.py --json

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
import json
import os
import re
import subprocess
import sys

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


def documentado_como_cli(ficheiros):
    """Um humano corre isto, e esta escrito num documento.

    ⚠️ ISTO NAO E O MESMO QUE «TEM CHAMADOR». Um CLI documentado corre quando
    alguem se lembra — nao numa corrida. Mas tambem NAO e codigo morto, e
    achatar os dois faz uma ferramenta viva parecer sobra.

        NENHUM CHAMADOR != NINGUEM CORRE.
        MAS CLI DOCUMENTADO != PORTAO QUE CORRE SOZINHO.
    """
    fora = []
    for f in ficheiros:
        if not f.endswith(('.py', '.mjs', '.sh')):
            continue
        for l in _sh("grep -rn --include=*.md -F %s . 2>/dev/null | head -20"
                     % json.dumps(f)):
            if re.search(r'(python3?|py|node|bash|\./)\s+\S*' + re.escape(os.path.basename(f)), l):
                fora.append(l.split(':', 1)[0].lstrip('./'))
                break
    return sorted(set(fora))


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


def main():
    S = json.load(open(ESTADO, encoding='utf-8'))
    N = {n['id']: n for n in S['NODES']}
    E = S['EDGES']
    universo = [i for i, n in N.items() if n.get('family') in LADO_DA_COLETA]
    tocam = set()
    for e in E:
        if e['from'] in universo:
            tocam.add(e['to'])
        if e['to'] in universo:
            tocam.add(e['from'])
    universo = sorted(set(universo) | tocam)

    grau = {}
    for e in E:
        grau[e['from']] = grau.get(e['from'], 0) + 1
        grau[e['to']] = grau.get(e['to'], 0) + 1

    RAIZES, ALCANCADOS = alcancaveis_do_runtime()

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
            'GAP': n.get('gap'),
        })

    rel = [e for e in E if e['from'] in set(universo) or e['to'] in set(universo)]
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
        'SEM_LIGACAO_INEXPLICADOS': sorted(
            f['CARD_ID'] for f in fichas if f['PORQUE_SOZINHO'] == 'UNKNOWN'),
        'CATEGORIAS_DAS_ARESTAS': {
            c: len([e for e in rel if e.get('categoria') == c])
            for c in sorted({e.get('categoria') for e in rel} - {None})},
        'GAPS_NOMEADOS': sorted({f['GAP'] for f in fichas if f['GAP']}),
    }

    if '--json' in sys.argv:
        print(json.dumps({'RESUMO': resumo, 'FICHAS': fichas},
                         ensure_ascii=False, indent=1))
        return 0

    print('CENSO DA TOPOLOGIA DA COLETA')
    print('=' * 70)
    for k, v in resumo.items():
        if isinstance(v, (list, dict)) and len(v) > 6:
            print('  %-28s %s' % (k, len(v)))
        else:
            print('  %-28s %s' % (k, v))
    print()
    print('  %-26s %-9s %-7s %-6s %s' % ('CARD', 'RUNTIME', 'ENTRAM', 'SAEM', 'SOZINHO'))
    print('  ' + '-' * 66)
    for f in fichas:
        print('  %-26s %-9s %-7s %-6s %s'
              % (f['CARD_ID'][:26], 'SIM' if f['RUNTIME_OBSERVADO'] else
                 ('-' if not f['FICHEIROS'] else 'NAO'),
                 f['ENTRAM'], f['SAEM'], f['PORQUE_SOZINHO'] or ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
