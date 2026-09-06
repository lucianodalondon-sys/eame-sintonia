#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS UNIVERSOS DECLARADOS — quem diz o que deveria existir, e se ainda bate.

SOMENTE LEITURA. Este script não escreve em lugar nenhum, nem regenera artefato de
dono. Ele **lê a declaração de cada dono**, varre o disco por conta própria, e compara.

    UNIVERSE_PASSAPORTE   itens que o passaporte passaporta
    UNIVERSE_ACERVO_IT    o acervo italiano contado pela FORMA das coleções
    UNIVERSE_EXECUCOES    as execuções de coleta que produziram o bruto

**Os três não são o mesmo universo, e somá-los produziria um total sem significado.**
Um vídeo do SENSOR-PILOT pertence aos três ao mesmo tempo, respondendo a três perguntas
diferentes: *tem passaporte?* · *que forma de coleção ele tem?* · *que execução o trouxe?*

Nenhum valor esperado é digitado aqui. Cada um é **derivado da declaração do dono** —
a mesma disciplina de `scripts/inventario_esperado.py`, que deriva as tabelas esperadas
das migrations em vez de manter uma lista que envelhece.

Uso
    python3 scripts/passaporte_universos.py --acervo . --passaporte <ref> [--json p.json]
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys

RULE_VERSION = 'UNIVERSOS-2026-09-06'

# ── quem é dono de quê, declarado ─────────────────────────────────────────────────

DONOS = {
    'UNIVERSE_PASSAPORTE': {
        'OWNER_FILE': 'scripts/passaporte_backfill.py',
        'OWNER_FIELD': 'INVENTARIO + DIRETORIOS',
        'OWNER_BRANCH': 'claude/sintonia-information-passport-bbtps0',
        'WHAT_IT_DECLARES': 'a lista de arquivos do acervo que o passaporte reconhece, '
                            'arquivo por arquivo, sem heurística de nome',
        'SCOPE': 'itens passaportáveis (ES + piloto + territorial + snapshots)',
        'FAIL_CLOSED': 'arquivo em data/samples não declarado → órfão → ACERVO_DECLARADO cai',
        'CANONICAL': 'SIM, para este universo',
    },
    'UNIVERSE_ACERVO_IT': {
        'OWNER_FILE': 'data/samples/IT-PORTAL-V1/IT-ACERVO-INVENTARIO-V2.json',
        'OWNER_FIELD': 'FICHEIROS · TOTAL_REAL_ACERVO · CHAVES_DE_COLECAO_ENCONTRADAS',
        'OWNER_REGISTRY': 'data/samples/IT-PORTAL-V1/IT-ACERVO-CHAVES-V1.json',
        'OWNER_BRANCH': 'sintonia/canonical',
        'WHAT_IT_DECLARES': 'o acervo italiano contado pela FORMA das coleções, com um '
                            'registo de 80 chaves semeado do próprio acervo',
        'SCOPE': 'COUNTRY=IT · LAYER=PORTAL',
        'FAIL_CLOSED': 'chave de coleção fora do registo → UNKNOWN_COLLECTION_KEY → reprova',
        'CANONICAL': 'SIM, para este universo',
    },
    'UNIVERSE_EXECUCOES': {
        'OWNER_FILE': 'scripts/proveniencia.py',
        'OWNER_FIELD': 'RUN_ID → RUN_MANIFEST (data/runs/)',
        'OWNER_BRANCH': 'sintonia/canonical',
        'WHAT_IT_DECLARES': 'toda execução de coleta, com ator, entrada, dataset e bruto',
        'SCOPE': 'execuções, não arquivos nem registros',
        'FAIL_CLOSED': 'campo desconhecido → NOT_PRESERVED, nunca ausente',
        'CANONICAL': 'SIM, para este universo',
    },
}

# O que NENHUM dono declara — e por isso não pode receber PASS.
SEM_DONO = {
    'UNIVERSE_DATA_SAMPLES_INTEIRO': {
        'O_QUE_SERIA': 'todo arquivo sob data/samples, de qualquer país e camada',
        'POR_QUE_NAO_TEM_DONO': 'os três donos acima cobrem recortes, e a união deles '
                                'não é um universo declarado por ninguém. Foi essa união '
                                'que a primeira versão deste portão impressionou digitalmente '
                                '— e uma digital de um universo que ninguém declarou não '
                                'prova completude de nada.',
    },
}


def _sha_de_arquivos(caminhos, raiz):
    h = hashlib.sha256()
    for c in sorted(caminhos):
        rel = os.path.relpath(c, raiz).replace('\\', '/')
        h.update(rel.encode('utf-8'))
        try:
            with open(c, 'rb') as f:
                h.update(hashlib.sha256(f.read()).digest())
        except Exception:                                      # noqa: BLE001
            h.update(b'ILEGIVEL')
    return h.hexdigest()


def _registros(caminho):
    """Conta registros como o dono do acervo IT conta: chave de topo cujo valor é
    lista não vazia de dicionários. A forma, não o nome."""
    try:
        d = json.load(open(caminho, encoding='utf-8'))
    except Exception:                                          # noqa: BLE001
        return 0, []
    if isinstance(d, list):
        return (len(d), ['__RAIZ__']) if d and isinstance(d[0], dict) else (0, [])
    if not isinstance(d, dict):
        return 0, []
    n, chaves = 0, []
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            n += len(v)
            chaves.append(k)
    return n, chaves


# ── UNIVERSE_PASSAPORTE ───────────────────────────────────────────────────────────

def universo_passaporte(acervo, passaporte):
    fonte = os.path.join(passaporte, 'scripts', 'passaporte_backfill.py')
    if not os.path.isfile(fonte):
        return {'DECLARED': False, 'MOTIVO': 'OWNER_FILE_NOT_REACHABLE',
                'OWNER_FILE': fonte}
    texto = open(fonte, encoding='utf-8').read()
    m = re.search(r'^INVENTARIO\s*=\s*\{(.*?)^\}', texto, re.S | re.M)
    if not m:
        return {'DECLARED': False, 'MOTIVO': 'INVENTARIO_NOT_FOUND'}
    esperados = {x for x in re.findall(r"^\s*'([^']+)':", m.group(1), re.M)}

    base = os.path.join(acervo, 'data', 'samples')
    disco, caminhos = set(), []
    for pasta, _, nomes in os.walk(base):
        for nome in sorted(nomes):
            c = os.path.join(pasta, nome)
            rel = os.path.relpath(c, base).replace('\\', '/')
            if rel.startswith('raw-paid/'):     # diretório com regra própria, declarada
                continue
            disco.add(rel)
            caminhos.append(c)

    faltando = sorted(esperados - disco)
    extra = sorted(disco - esperados)
    presentes = sorted(esperados & disco)
    registros = sum(_registros(os.path.join(base, r))[0] for r in presentes)
    return {
        'DECLARED': True,
        'EXPECTED_FILE_COUNT': len(esperados),
        'EXPECTED_RECORD_COUNT': None,     # o dono NÃO declara contagem de registros
        'EXPECTED_FAMILIES': None,         # nem famílias
        'EXPECTED_COLLECTIONS': None,
        'EXPECTED_FINGERPRINT': None,      # nem impressão digital
        'SCANNED_FILE_COUNT': len(disco),
        'SCANNED_RECORD_COUNT': registros,
        'SCANNED_FINGERPRINT': _sha_de_arquivos(
            [os.path.join(base, r) for r in presentes], base),
        'MISSING': faltando,
        'EXTRA': extra,
        'DIMENSOES_AUSENTES': ['EXPECTED_RECORD_COUNT', 'EXPECTED_FAMILIES',
                               'EXPECTED_COLLECTIONS', 'EXPECTED_FINGERPRINT'],
    }


# ── UNIVERSE_ACERVO_IT ────────────────────────────────────────────────────────────

FAMILIAS_IT = [
    ('RADAR_FUTURO', r'IT-FUTURO'),
    ('ROTULOS_PORTFOLIO', r'IT-ROTULOS|IT-VOCAB|IT-PAIRSET|productsRegulatory|productRelationships'),
    ('SINAIS_DE_CAMPO', r'IT-CAMPO|CURRENT-FIELD|IT-CRUZAMENTO'),
    ('FITOSSANITARIO', r'IT-CONVEGNO|IT-VIDEO|IT-VOZ-AUDIO|falas/|testemunhas/'),
    ('FONTES', r'IT-FONTES'),
    ('CONCORRENCIA', r'COMPETITOR|CONCORREN'),
    ('SOCIAL_INSTAGRAM', r'IT-INSTAGRAM'),
    ('SENSORES_HUMANOS', r'SENSOR-PILOT|EARLY_SIGNAL|RESEARCHER|SPEAKER'),
    ('GEOGRAFIA', r'TERRITORIAL|nuts2|GEOGRAF'),
    ('MERCADO', r'MARKET|PRICES|ECONOMIC'),
    ('OPORTUNIDADES', r'IT-RADAR-V21|OPPORTUNIT|IT-SNAPSHOT'),
    ('HANDOFF_METODO', r'IT-HANDOFF|RUN-MANIFEST|DATA-CLOCK|POLITICA|AUDITORIA|ROTAS-EXTERNAS'),
    ('IT-PORTAL', r'IT-PORTAL'),
]


def _familia_it(rel):
    for nome, rx in FAMILIAS_IT:
        if re.search(rx, rel, re.IGNORECASE):
            return nome
    return None


def universo_acervo_it(acervo):
    decl_p = os.path.join(acervo, 'data', 'samples', 'IT-PORTAL-V1',
                          'IT-ACERVO-INVENTARIO-V2.json')
    reg_p = os.path.join(acervo, 'data', 'samples', 'IT-PORTAL-V1',
                         'IT-ACERVO-CHAVES-V1.json')
    if not (os.path.isfile(decl_p) and os.path.isfile(reg_p)):
        return {'DECLARED': False, 'MOTIVO': 'OWNER_FILE_NOT_FOUND'}
    decl = json.load(open(decl_p, encoding='utf-8'))
    reg = json.load(open(reg_p, encoding='utf-8'))
    chaves_esperadas = set(reg.get('CHAVES') or [])

    base = os.path.join(acervo, 'data', 'samples')
    arquivos, registros = [], 0
    chaves_vistas = collections.Counter()
    por_familia = collections.Counter()
    desconhecidas = []
    for pasta, _, nomes in os.walk(base):
        for nome in sorted(nomes):
            if not nome.endswith('.json'):
                continue
            c = os.path.join(pasta, nome)
            rel = os.path.relpath(c, base).replace('\\', '/')
            fam = _familia_it(rel)
            if not fam:
                continue
            n, chaves = _registros(c)
            if not n:
                continue
            arquivos.append(c)
            registros += n
            por_familia[fam] += n
            for k in chaves:
                chaves_vistas[k] += 1
                if k not in chaves_esperadas:
                    desconhecidas.append({'CHAVE': k, 'ARQUIVO': rel})
    return {
        'DECLARED': True,
        'EXPECTED_FILE_COUNT': decl.get('FICHEIROS'),
        'EXPECTED_RECORD_COUNT': decl.get('TOTAL_REAL_ACERVO'),
        'EXPECTED_FAMILIES': sorted(decl.get('TOTAL_POR_FAMILIA', {})),
        'EXPECTED_COLLECTIONS': sorted(chaves_esperadas),
        'EXPECTED_FINGERPRINT': None,      # o dono NÃO declara impressão digital
        'DECLARED_AT': decl.get('CAPTURED_AT'),
        'SCANNED_FILE_COUNT': len(arquivos),
        'SCANNED_RECORD_COUNT': registros,
        'SCANNED_FAMILIES': sorted(por_familia),
        'SCANNED_COLLECTIONS': sorted(chaves_vistas),
        'SCANNED_FINGERPRINT': _sha_de_arquivos(arquivos, base),
        'UNKNOWN_COLLECTION_KEY': desconhecidas,
        'DIMENSOES_AUSENTES': ['EXPECTED_FINGERPRINT'],
    }


# ── UNIVERSE_EXECUCOES ────────────────────────────────────────────────────────────

def universo_execucoes(acervo):
    base = os.path.join(acervo, 'data', 'runs')
    if not os.path.isdir(base):
        return {'DECLARED': False, 'MOTIVO': 'RUNS_DIR_NOT_FOUND'}
    arquivos, runs = [], set()
    for pasta, _, nomes in os.walk(base):
        for nome in sorted(nomes):
            if not nome.endswith('.json'):
                continue
            c = os.path.join(pasta, nome)
            arquivos.append(c)
            try:
                d = json.load(open(c, encoding='utf-8'))
                rid = d.get('RUN_ID') or d.get('COLLECTION_RUN_ID')
                if rid:
                    runs.add(rid)
            except Exception:                                  # noqa: BLE001
                pass
    return {
        'DECLARED': False,
        'MOTIVO': 'OWNER_DECLARES_SHAPE_NOT_EXTENT',
        'EXPLICACAO': 'proveniencia.py declara COMO uma execução tem de ser descrita, '
                      'e não QUANTAS execuções deveriam existir. Forma declarada não é '
                      'extensão declarada.',
        'SCANNED_FILE_COUNT': len(arquivos),
        'SCANNED_RUN_COUNT': len(runs),
        'SCANNED_FINGERPRINT': _sha_de_arquivos(arquivos, base),
        'DIMENSOES_AUSENTES': ['EXPECTED_FILE_COUNT', 'EXPECTED_RECORD_COUNT',
                               'EXPECTED_FAMILIES', 'EXPECTED_COLLECTIONS',
                               'EXPECTED_FINGERPRINT'],
    }


# ── o portão ──────────────────────────────────────────────────────────────────────

DIMENSOES = ('EXPECTED_FILE_COUNT', 'EXPECTED_RECORD_COUNT', 'EXPECTED_FAMILIES',
             'EXPECTED_COLLECTIONS', 'EXPECTED_FINGERPRINT')


def avaliar(nome, u):
    """PASS exige as CINCO dimensões declaradas E batendo. Falta uma → FAIL."""
    if not u.get('DECLARED'):
        return {'PASS': False, 'MOTIVO': u.get('MOTIVO', 'EXPECTED_UNIVERSE_NOT_DECLARED')}
    faltando_dim = [d for d in DIMENSOES if u.get(d) in (None, [], {})]
    if faltando_dim:
        return {'PASS': False, 'MOTIVO': 'EXPECTED_DIMENSIONS_MISSING',
                'DIMENSOES_AUSENTES': faltando_dim}
    problemas = {}
    if u.get('MISSING'):
        problemas['MISSING'] = len(u['MISSING'])
    if u.get('EXTRA'):
        problemas['EXTRA'] = len(u['EXTRA'])
    if u.get('UNKNOWN_COLLECTION_KEY'):
        problemas['UNKNOWN_COLLECTION_KEY'] = len(u['UNKNOWN_COLLECTION_KEY'])
    # contagens
    for a, b in (('EXPECTED_FILE_COUNT', 'SCANNED_FILE_COUNT'),
                 ('EXPECTED_RECORD_COUNT', 'SCANNED_RECORD_COUNT')):
        if u.get(a) is not None and u.get(a) != u.get(b):
            problemas[a] = {'ESPERADO': u[a], 'VARRIDO': u.get(b)}
    # conjuntos — família ou coleção que aparece ou some é deriva, não detalhe
    for a, b in (('EXPECTED_FAMILIES', 'SCANNED_FAMILIES'),
                 ('EXPECTED_COLLECTIONS', 'SCANNED_COLLECTIONS')):
        if u.get(a) is None:
            continue
        esp, var = set(u[a]), set(u.get(b) or [])
        if esp != var:
            problemas[a] = {'AUSENTES': sorted(esp - var)[:5],
                            'NAO_DECLARADOS': sorted(var - esp)[:5]}
    # a impressão digital é a checagem mais forte, e era a que faltava comparar
    if u.get('EXPECTED_FINGERPRINT') is not None and \
            u['EXPECTED_FINGERPRINT'] != u.get('SCANNED_FINGERPRINT'):
        problemas['EXPECTED_FINGERPRINT'] = {
            'ESPERADO': str(u['EXPECTED_FINGERPRINT'])[:16] + '…',
            'VARRIDO': str(u.get('SCANNED_FINGERPRINT'))[:16] + '…'}
    return {'PASS': not problemas, 'MOTIVO': None if not problemas else 'UNIVERSE_DRIFT',
            'PROBLEMAS': problemas}


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

    universos = {
        'UNIVERSE_PASSAPORTE': universo_passaporte(args.acervo, args.passaporte),
        'UNIVERSE_ACERVO_IT': universo_acervo_it(args.acervo),
        'UNIVERSE_EXECUCOES': universo_execucoes(args.acervo),
    }
    print(f'UNIVERSOS DECLARADOS · {RULE_VERSION} · somente leitura\n')
    veredictos = {}
    for nome, u in universos.items():
        dono = DONOS[nome]
        v = avaliar(nome, u)
        veredictos[nome] = v
        print(f'── {nome}  =  {"PASS" if v["PASS"] else "FAIL"}')
        print(f'     dono      : {dono["OWNER_FILE"]}  ({dono["OWNER_FIELD"]})')
        print(f'     escopo    : {dono["SCOPE"]}')
        print(f'     declara   : {dono["WHAT_IT_DECLARES"]}')
        for k in ('EXPECTED_FILE_COUNT', 'SCANNED_FILE_COUNT',
                  'EXPECTED_RECORD_COUNT', 'SCANNED_RECORD_COUNT',
                  'SCANNED_RUN_COUNT', 'DECLARED_AT'):
            if k in u:
                print(f'     {k:24s}= {u[k]}')
        for k in ('MISSING', 'EXTRA', 'UNKNOWN_COLLECTION_KEY'):
            if u.get(k):
                print(f'     {k:24s}= {len(u[k])}   ex.: '
                      f'{[str(x)[:60] for x in u[k][:2]]}')
        if u.get('DIMENSOES_AUSENTES'):
            print(f'     DIMENSOES NAO DECLARADAS = {u["DIMENSOES_AUSENTES"]}')
        print(f'     MOTIVO    : {v["MOTIVO"] or "—"}')
        if v.get('PROBLEMAS'):
            print(f'     PROBLEMAS : {v["PROBLEMAS"]}')
        print()

    print('── O QUE NINGUÉM DECLARA ──')
    for nome, d in SEM_DONO.items():
        print(f'  {nome}')
        print(f'     seria: {d["O_QUE_SERIA"]}')
        print(f'     {d["POR_QUE_NAO_TEM_DONO"]}')

    todos = all(v['PASS'] for v in veredictos.values())
    print(f'\nUNIVERSE_COMPLETENESS = {"PASS" if todos else "FAIL"}')
    if not todos:
        print('  Nenhum universo pode receber PASS hoje. Os motivos estão acima, e')
        print('  nenhum deles se resolve inventando um número.')

    if args.json:
        json.dump({'RULE_VERSION': RULE_VERSION, 'DONOS': DONOS, 'SEM_DONO': SEM_DONO,
                   'UNIVERSOS': {k: {kk: vv for kk, vv in v.items()
                                     if kk not in ('MISSING', 'EXTRA')}
                                 for k, v in universos.items()},
                   'MISSING': {k: v.get('MISSING', []) for k, v in universos.items()},
                   'EXTRA_COUNT': {k: len(v.get('EXTRA', [])) for k, v in universos.items()},
                   'VEREDICTOS': veredictos,
                   'UNIVERSE_COMPLETENESS': 'PASS' if todos else 'FAIL'},
                  open(args.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'\ngravado: {args.json}')
    return 0 if todos else 1


if __name__ == '__main__':
    raise SystemExit(main())
