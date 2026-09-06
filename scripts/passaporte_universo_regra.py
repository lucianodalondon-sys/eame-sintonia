#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A REGRA DE PERTENÇA DO `UNIVERSE_PASSAPORTE` — derivada do contrato, medida contra a lista.

SOMENTE LEITURA.

A pergunta: **o que faz um arquivo pertencer ao universo do passaporte?**

A resposta não é "estar em `data/samples`" (isso é diretório físico) nem "estar na lista
de 74" (isso é história). A resposta está escrita no contrato, em `§1.5 Granularidade`:

    "Um passaporte por unidade sobre a qual o pipeline toma decisão INDIVIDUAL. Isso vale
     quando (a) o item resolve para uma execução própria (RUN_ID/COLLECTION_RUN_ID), ou
     (b) o repositório já registra uma decisão por item sobre ele (classificação, fila,
     veto, estado de identidade).
     Registro oficial e corpus científico não satisfazem nem (a) nem (b): entram como
     DATASET_SNAPSHOT, com UNIT_COUNT declarado."

Este módulo transcreve essa frase em teste, aplica ao acervo inteiro, e **mede o
desacordo com a lista histórica** — sem ajustar a regra até o desacordo virar zero.
Ajustar até fechar seria decorar a lista, não derivar a regra.

Uso
    python3 scripts/passaporte_universo_regra.py --acervo . --passaporte <ref> [--json p.json]
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys

RULE_VERSION = 'UNIVERSO-PASSAPORTE-REGRA-2026-09-06'
RULE_SOURCE = 'docs/passaporte/CONTRATO-DO-PASSAPORTE.md §1.5'

# ── a frase do contrato, em campos ────────────────────────────────────────────────
#
# (a) "o item resolve para uma execução própria (RUN_ID/COLLECTION_RUN_ID)"
EXECUCAO_PROPRIA = re.compile(r'^(RUN_ID|COLLECTION_RUN_ID|BATCH_ID)$', re.I)

# (b) "o repositório já registra uma decisão por item sobre ele
#      (classificação, fila, veto, estado de identidade)"
#
# Um campo que carrega decisão por item termina em _STATE, _BASIS, _EVIDENCE, _DECISION
# ou nomeia fila/veto/classificação. `_BASIS`/`_EVIDENCE` entram porque a casa exige que
# toda decisão declare a base e a prova — é a assinatura de "alguém decidiu isto aqui".
DECISAO_POR_ITEM = re.compile(
    r'(_STATE$|_BASIS$|_EVIDENCE$|_DECISION$|^DECISAO|^VEREDITO|^TRIAGE$|'
    r'FILA|QUEUE|VETO|CLASSIFICA|RELEVANCIA|_POR_QUE$)', re.I)

# EXCLUSÃO · o registro NÃO é uma unidade de informação: ele É uma execução.
# Pertence a UNIVERSE_EXECUCOES, cujo dono é scripts/proveniencia.py.
E_UMA_EXECUCAO = ('ACTOR', 'INPUT', 'DATASET_ID', 'COST_USD', 'ACTOR_VERSION',
                  'ITEM_COUNT_RAW', 'FINISHED_AT')

# "Registro oficial e corpus científico ... entram como DATASET_SNAPSHOT, com UNIT_COUNT"
SNAPSHOT = re.compile(r'(UNIT_COUNT|TOTAL_ROWS|TOTAL_DOCS|N_DOCUMENTOS|N_LINHAS)$', re.I)


def listas_de_registros(obj, prefixo=''):
    """TODAS as listas de dicionários, em qualquer profundidade razoável.

    A primeira versão deste módulo pegava só a PRIMEIRA lista de topo — e por isso
    classificou errado `PUBLIC-COMM-FIRST-BATCH-EAME.json`, cuja primeira lista é
    `EXECUTION_ORDER` (passos) e cujos itens estão em `ACCOUNTS`. Era bug do leitor,
    não falha da regra.
    """
    saida = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                saida.append((f'{prefixo}{k}', v))
            if isinstance(v, (dict, list)) and len(prefixo) < 40:
                saida += listas_de_registros(v, f'{prefixo}{k}.')
    elif isinstance(obj, list):
        for v in obj[:50]:
            if isinstance(v, (dict, list)):
                saida += listas_de_registros(v, prefixo)
    return saida


def classificar(caminho):
    """Aplica a regra do contrato a um arquivo. Devolve (estado, motivo, detalhe)."""
    if not caminho.endswith(('.json', '.jsonl')):
        return 'OUT_OF_SCOPE', 'NAO_E_JSON', {}
    try:
        with open(caminho, encoding='utf-8') as f:
            dados = json.loads(f.read()) if caminho.endswith('.json') else \
                [json.loads(l) for l in f if l.strip()]
    except Exception as erro:                                  # noqa: BLE001
        return 'UNKNOWN_SCOPE', 'ILEGIVEL: %s' % str(erro)[:60], {}

    listas = listas_de_registros(dados)
    if not listas:
        # sem lista de registros: pode ainda ser um snapshot declarado
        texto = json.dumps(dados, ensure_ascii=False)[:20000]
        if SNAPSHOT.search(texto):
            return 'IN_UNIVERSE_PASSAPORTE', 'DATASET_SNAPSHOT_COM_UNIT_COUNT', {}
        return 'OUT_OF_SCOPE', 'SEM_REGISTROS', {}

    melhor = None
    for nome, arr in listas:
        campos = set()
        for r in arr[:80]:
            if isinstance(r, dict):
                campos |= set(r)
        exec_propria = any(EXECUCAO_PROPRIA.match(c) for c in campos)
        decisao = sorted({c for c in campos if DECISAO_POR_ITEM.search(c)})
        e_execucao = sum(1 for c in E_UMA_EXECUCAO if c in campos) >= 3
        info = {'LISTA': nome, 'N': len(arr), 'EXECUCAO_PROPRIA': exec_propria,
                'DECISAO_POR_ITEM': decisao[:6], 'E_UMA_EXECUCAO': e_execucao}
        if e_execucao:
            info['ESTADO'] = ('OUT_OF_SCOPE', 'E_UMA_EXECUCAO_PERTENCE_A_UNIVERSE_EXECUCOES')
        elif exec_propria or decisao:
            regra = 'REGRA_A_EXECUCAO_PROPRIA' if exec_propria else 'REGRA_B_DECISAO_POR_ITEM'
            info['ESTADO'] = ('IN_UNIVERSE_PASSAPORTE', regra)
        else:
            info['ESTADO'] = ('OUT_OF_SCOPE', 'NEM_A_NEM_B')
        # a lista mais forte manda: dentro vence fora, e a maior vence a menor
        chave = (info['ESTADO'][0] == 'IN_UNIVERSE_PASSAPORTE', len(arr))
        if melhor is None or chave > melhor[0]:
            melhor = (chave, info)
    info = melhor[1]
    return info['ESTADO'][0], info['ESTADO'][1], info


def varrer(acervo):
    base = os.path.join(acervo, 'data', 'samples')
    resultado = {}
    for pasta, _, nomes in os.walk(base):
        for nome in sorted(nomes):
            c = os.path.join(pasta, nome)
            rel = os.path.relpath(c, base).replace('\\', '/')
            if rel.startswith('raw-paid/'):
                resultado[rel] = ('OUT_OF_SCOPE', 'RAW_PAID_TEM_REGRA_DE_DIRETORIO_PROPRIA', {})
                continue
            resultado[rel] = classificar(c)
    return resultado


def lista_historica(passaporte):
    fonte = os.path.join(passaporte, 'scripts', 'passaporte_backfill.py')
    if not os.path.isfile(fonte):
        return None, None
    texto = open(fonte, encoding='utf-8').read()
    m = re.search(r'^INVENTARIO\s*=\s*\{(.*?)^\}', texto, re.S | re.M)
    if not m:
        return None, None
    ent = re.findall(r"^\s*'([^']+)':\s*\(([^,]+),\s*'([^']*)'\)", m.group(1), re.M)
    carrega = {a for a, r, _ in ent if r.strip() in ("'ITENS'", "'SELOS'")}
    todos = {a for a, _, _ in ent}
    return carrega, todos


def universo(acervo, resultado):
    base = os.path.join(acervo, 'data', 'samples')
    dentro = sorted(k for k, v in resultado.items() if v[0] == 'IN_UNIVERSE_PASSAPORTE')
    registros = 0
    colecoes = collections.Counter()
    familias = collections.Counter()
    h = hashlib.sha256()
    for rel in dentro:
        info = resultado[rel][2]
        registros += info.get('N', 0)
        if info.get('LISTA'):
            colecoes[info['LISTA']] += 1
        familias[rel.split('/')[0] if '/' in rel else '__RAIZ__'] += 1
        h.update(rel.encode('utf-8'))
        try:
            with open(os.path.join(base, rel), 'rb') as f:
                h.update(hashlib.sha256(f.read()).digest())
        except Exception:                                      # noqa: BLE001
            h.update(b'ILEGIVEL')
    return {'FILES': dentro, 'FILE_COUNT': len(dentro), 'RECORD_COUNT': registros,
            'FAMILIES': sorted(familias), 'COLLECTIONS': sorted(colecoes),
            'FINGERPRINT': h.hexdigest()}


def portao(acervo, passaporte):
    """EXPECTED = o que a REGRA diz que pertence. SCANNED = o que o passaporte cobre.

    Os dois lados medem coisas diferentes de propósito. Se `EXPECTED` fosse a regra e
    `SCANNED` também, o portão compararia uma conta consigo mesma e daria PASS sempre.
    Aqui:

        EXPECTED  ← a regra aplicada ao acervo de HOJE (auto-atualiza)
        SCANNED   ← os arquivos que o passaporte declara cobrir

    Arquivo novo que satisfaça a regra entra em `EXPECTED` sozinho, sem ninguém editar
    lista — e aparece em `MISSING` até ganhar passaporte. É esse o ponto.
    """
    r = varrer(acervo)
    u = universo(acervo, r)
    carrega, _ = lista_historica(passaporte)
    if carrega is None:
        return {'PASS': False, 'MOTIVO': 'PASSAPORTE_NAO_ALCANCAVEL'}, r, u

    esperado = set(u['FILES'])
    coberto = set(carrega)
    faltando = sorted(esperado - coberto)
    fora = sorted(coberto - esperado)

    # O UNKNOWN crítico: a regra não declara PERTENÇA, só granularidade.
    contraexemplos = [rel for rel in u['FILES']
                      if re.search(r'(^|[._])(ACTORS?|CONTRACTS?|GATES?|MANIFESTOS?|'
                                   r'MANIFEST|RUNNERS?|SCRIPTS?|FERRAMENTAS?)([._]|$)',
                                   str(r[rel][2].get('LISTA', '')).upper())]

    problemas = {}
    if faltando:
        problemas['MISSING'] = len(faltando)
    if fora:
        problemas['COBERTO_MAS_FORA_DA_REGRA'] = len(fora)
    if contraexemplos:
        problemas['MEMBERSHIP_CONDITION_NOT_DECLARED'] = len(contraexemplos)

    return {
        'PASS': not problemas,
        'MOTIVO': None if not problemas else (
            'MEMBERSHIP_CONDITION_NOT_DECLARED' if contraexemplos else 'UNIVERSE_DRIFT'),
        'EXPECTED_FILES': len(esperado),
        'EXPECTED_RECORDS': u['RECORD_COUNT'],
        'EXPECTED_FAMILIES': len(u['FAMILIES']),
        'EXPECTED_COLLECTIONS': len(u['COLLECTIONS']),
        'EXPECTED_FINGERPRINT': u['FINGERPRINT'],
        'SCANNED_FILES': len(coberto),
        'SCANNED_RECORDS': sum(r[x][2].get('N', 0) for x in coberto if x in r),
        'SCANNED_FAMILIES': len({x.split('/')[0] if '/' in x else '__RAIZ__'
                                 for x in coberto}),
        'SCANNED_COLLECTIONS': len({r[x][2].get('LISTA') for x in coberto
                                    if x in r and r[x][2].get('LISTA')}),
        'SCANNED_FINGERPRINT': _fingerprint(acervo, sorted(coberto)),
        'MISSING': faltando,
        'COBERTO_MAS_FORA_DA_REGRA': fora,
        'UNKNOWN_CRITICO': contraexemplos,
        'PROBLEMAS': problemas,
    }, r, u


def _fingerprint(acervo, relativos):
    base = os.path.join(acervo, 'data', 'samples')
    h = hashlib.sha256()
    for rel in sorted(relativos):
        h.update(rel.encode('utf-8'))
        try:
            with open(os.path.join(base, rel), 'rb') as f:
                h.update(hashlib.sha256(f.read()).digest())
        except Exception:                                      # noqa: BLE001
            h.update(b'ILEGIVEL')
    return h.hexdigest()


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--acervo', default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    p.add_argument('--passaporte', required=True)
    p.add_argument('--json', default=None)
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass

    print(f'REGRA DE PERTENÇA · {RULE_VERSION}')
    print(f'  fonte da regra: {RULE_SOURCE}')
    print(f'  (a) execução própria   → {EXECUCAO_PROPRIA.pattern}')
    print(f'  (b) decisão por item   → {DECISAO_POR_ITEM.pattern}')
    print(f'  exclusão: o registro É uma execução → {E_UMA_EXECUCAO}\n')

    r = varrer(args.acervo)
    estados = collections.Counter(v[0] for v in r.values())
    total = len(r)
    print('── 3 · CLASSIFICAÇÃO DE TODO ARQUIVO OBSERVADO ──')
    for e in ('IN_UNIVERSE_PASSAPORTE', 'OUT_OF_SCOPE', 'UNKNOWN_SCOPE'):
        print(f'  {e:26s} = {estados.get(e, 0)}')
    soma = sum(estados.values())
    print(f'  {"TOTAL":26s} = {total}   ·   soma fecha = {soma == total}')
    print('\n  motivos de OUT_OF_SCOPE:')
    for m, n in collections.Counter(v[1] for v in r.values()
                                    if v[0] == 'OUT_OF_SCOPE').most_common():
        print(f'     {n:5d}  {m}')
    if estados.get('UNKNOWN_SCOPE'):
        print('\n  UNKNOWN_SCOPE (não inventado — declarado):')
        for k, v in list(r.items()):
            if v[0] == 'UNKNOWN_SCOPE':
                print(f'     {k}  ·  {v[1]}')

    u = universo(args.acervo, r)
    print('\n── 2 · O UNIVERSO, DERIVADO DA REGRA ──')
    print(f'  RULE_DERIVED_FILES       = {u["FILE_COUNT"]}')
    print(f'  RULE_DERIVED_RECORDS     = {u["RECORD_COUNT"]}')
    print(f'  RULE_DERIVED_FAMILIES    = {len(u["FAMILIES"])}')
    print(f'  RULE_DERIVED_COLLECTIONS = {len(u["COLLECTIONS"])}')
    print(f'  FINGERPRINT              = {u["FINGERPRINT"]}')

    carrega, todos = lista_historica(args.passaporte)
    desacordo = {}
    if carrega is not None:
        dentro = set(u['FILES'])
        so_regra = sorted(dentro - carrega)
        so_lista = sorted(carrega - dentro)
        desacordo = {'SO_NA_REGRA': so_regra, 'SO_NA_LISTA': so_lista,
                     'CONCORDAM': len(dentro & carrega)}
        print('\n── 1 · A REGRA CONTRA A LISTA HISTÓRICA ──')
        print(f'  lista histórica diz que carregam item : {len(carrega)}')
        print(f'  a regra diz                           : {len(dentro)}')
        print(f'  concordam                             : {len(dentro & carrega)}')
        print(f'  só na regra (a lista não previa)      : {len(so_regra)}')
        print(f'  só na lista (a regra não pega)        : {len(so_lista)}')
        for x in so_lista:
            print(f'     LISTA-SÓ  {x}  ·  {r.get(x, ("?", "?"))[1]}')
        for x in so_regra[:10]:
            print(f'     REGRA-SÓ  {x}  ·  {r[x][1]}')
        if len(so_regra) > 10:
            print(f'     … mais {len(so_regra) - 10}')

    # ── o teste que derruba o meu próprio veredito ────────────────────────────────
    #
    # Reproduzir a lista e discriminar não bastam. §1.5 responde **com que
    # granularidade** um item entra — *"um passaporte por unidade sobre a qual o
    # pipeline toma decisão INDIVIDUAL"*. Ela NÃO responde **se aquilo é uma unidade
    # de informação**. Um contrato de ator do Apify tem `CONTRACT_STATE` por ator:
    # satisfaz a regra (b) ao pé da letra, e não é evidência sobre o mundo.
    contraexemplos = []
    for rel in u['FILES']:
        info = r[rel][2]
        lista = str(info.get('LISTA', '')).upper()
        # Fronteira de palavra, não substring: `TRANSCRIPTS` contém `SCRIPT`, e
        # transcrição É unidade de informação — está entre os 21 declarados. A primeira
        # versão deste teste a acusou por casamento de pedaço de palavra.
        if re.search(r'(^|[._])(ACTORS?|CONTRACTS?|GATES?|MANIFESTOS?|MANIFEST|'
                     r'RUNNERS?|SCRIPTS?|FERRAMENTAS?)([._]|$)', lista):
            contraexemplos.append({'ARQUIVO': rel, 'LISTA': info.get('LISTA'),
                                   'POR_QUE': 'a lista descreve ferramenta/processo, '
                                              'não unidade de informação sobre o mundo'})

    sem_falso_negativo = bool(carrega) and not desacordo.get('SO_NA_LISTA')
    discrimina = 0 < u['FILE_COUNT'] < total * 0.6
    provada = sem_falso_negativo and discrimina and not contraexemplos

    print('\n── O VEREDITO, com os três testes ──')
    print(f'  reproduz a lista sem falso negativo : {sem_falso_negativo}')
    print(f'  discrimina (não inclui quase tudo)  : {discrimina}  '
          f'({u["FILE_COUNT"]} de {total})')
    print(f'  toda inclusão é unidade de informação: {not contraexemplos}  '
          f'({len(contraexemplos)} contraexemplos)')
    for c in contraexemplos[:5]:
        print(f'     CONTRAEXEMPLO  {c["ARQUIVO"]}  ·  lista={c["LISTA"]}')
        print(f'                    {c["POR_QUE"]}')

    print(f'\nRULE_PROVED = {"SIM" if provada else "NAO"}')
    if not provada and sem_falso_negativo and discrimina:
        print('  MOTIVO = MEMBERSHIP_CONDITION_NOT_DECLARED')
        print('  §1.5 declara GRANULARIDADE — "um passaporte por unidade sobre a qual o')
        print('  pipeline decide individualmente". Ela não declara PERTENÇA: se aquilo é')
        print('  uma unidade de informação. Um contrato de ator satisfaz a letra da regra')
        print('  (b) e não é evidência sobre o mundo. A condição que falta não está')
        print('  escrita em lugar nenhum do contrato — e eu não vou inventá-la.')

    g, _, _ = portao(args.acervo, args.passaporte)
    print('')
    print('── 5 · O PORTÃO DE COMPLETUDE DO UNIVERSO DO PASSAPORTE ──')
    print(f'  {"":26s} {"ESPERADO":>12s} {"COBERTO":>12s}')
    for dim in ('FILES', 'RECORDS', 'FAMILIES', 'COLLECTIONS'):
        print(f'  {dim:26s} {str(g.get("EXPECTED_" + dim)):>12s} '
              f'{str(g.get("SCANNED_" + dim)):>12s}')
    print(f'  {"FINGERPRINT":26s} {str(g.get("EXPECTED_FINGERPRINT"))[:12]:>12s} '
          f'{str(g.get("SCANNED_FINGERPRINT"))[:12]:>12s}')
    print('')
    print(f'  MISSING (satisfaz a regra e nao tem passaporte) = {len(g.get("MISSING", []))}')
    print(f'  COBERTO MAS FORA DA REGRA                      = {len(g.get("COBERTO_MAS_FORA_DA_REGRA", []))}')
    print(f'  UNKNOWN CRÍTICO                                = {len(g.get("UNKNOWN_CRITICO", []))}')
    print('')
    print(f'UNIVERSE_COMPLETENESS = {"PASS" if g["PASS"] else "FAIL"}'
          f'{"  · " + str(g["MOTIVO"]) if g["MOTIVO"] else ""}')

    if args.json:
        json.dump({'RULE_VERSION': RULE_VERSION, 'RULE_SOURCE': RULE_SOURCE,
                   'PORTAO': {k: (v if not isinstance(v, list) else len(v))
                              for k, v in g.items()},
                   'PORTAO_MISSING': g.get('MISSING', []),
                   'CLASSIFICACAO': {k: {'ESTADO': v[0], 'MOTIVO': v[1]}
                                     for k, v in sorted(r.items())},
                   'CONTAGEM': dict(estados), 'TOTAL': total,
                   'UNIVERSO': {k: v for k, v in u.items() if k != 'FILES'},
                   'UNIVERSO_FILES': u['FILES'],
                   'DESACORDO_COM_A_LISTA': desacordo,
                   'CONTRAEXEMPLOS': contraexemplos,
                   'TESTES_DO_VEREDITO': {
                       'SEM_FALSO_NEGATIVO': sem_falso_negativo,
                       'DISCRIMINA': discrimina,
                       'TODA_INCLUSAO_E_UNIDADE_DE_INFORMACAO': not contraexemplos},
                   'RULE_PROVED': 'SIM' if provada else 'NAO',
                   'MOTIVO': None if provada else 'MEMBERSHIP_CONDITION_NOT_DECLARED'},
                  open(args.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'\ngravado: {args.json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
