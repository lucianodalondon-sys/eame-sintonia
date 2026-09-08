#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O VALIDADOR DA BÍBLIA — prova que a constituição da coleta não anda sozinha.

    py provas/valida_biblia.py            mede e reprova (código 1) se algo divergir
    py provas/valida_biblia.py --build    regera docs/biblia/leis.json a partir do texto

POR QUE ELE EXISTE
-------------------
`docs/biblia/leis.json` NÃO é uma segunda verdade: é a leitura por máquina do MESMO texto.
Ele é DERIVADO de `BIBLIA-CANONICA-DA-COLETA.md`, nunca escrito à mão — pela mesma razão
que `state.generated.json` é derivado do repositório. Duas listas de leis divergiriam, e a
partir daí nenhuma das duas valeria.

    LEI QUE NINGUÉM MEDE É COMENTÁRIO.

O QUE ELE PROVA
----------------
    B1_BIBLIA_EXISTE           a Bíblia e os quatro apêndices estão no sítio declarado
    B2_IDS_UNICOS              nenhum COL-LAW repetido
    B3_LEI_COMPLETA            toda lei declara ORIGEM, LAW_STATUS e estado na Itália
    B4_STATUS_VALIDO           só os valores conhecidos entram nos dois eixos
    B5_VERSAO_DECLARADA        BIBLE_ID, VERSION, STATUS, EFFECTIVE_FROM, CURRENT_PROFILE
    B6_PERFIL_IT_DECLARADO     o perfil corrente diz que país é
    B7_REFERENCIA_EXISTE       toda lei citada pelos apêndices existe na Bíblia
    B8_CONFORMIDADE_COBRE      a matriz de conformidade fala de todas as leis, e só delas
    B9_FICHEIROS_CITADOS       todo ficheiro que a Bíblia cita como contrato existe
    B10_JSON_BATE_COM_O_TEXTO  leis.json é exatamente o que o texto diz

FALHA FECHADO, como o resto da casa: erro inesperado também é FAIL.
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho

BIBLIA = os.path.join(ROOT, 'BIBLIA-CANONICA-DA-COLETA.md')
PASTA = os.path.join(ROOT, 'docs', 'biblia')
CENSO = os.path.join(PASTA, 'CENSO-DAS-LEIS-DA-COLETA.md')
CONFLITOS = os.path.join(PASTA, 'MATRIZ-DE-CONFLITOS.md')
CONFORMIDADE = os.path.join(PASTA, 'CONFORMIDADE-ITALIA.md')
LEIS_JSON = os.path.join(PASTA, 'leis.json')

LAW_STATUS_VALIDOS = ('CANONICAL',)
IMPL_VALIDOS = ('IMPLEMENTED', 'PARTIAL', 'ABSENT', 'UNKNOWN')
ORIGENS_VALIDAS = ('EXISTING_SINTONIA_LAW', 'CONSOLIDATED_FROM_MULTIPLE',
                   'ARCHITECTURAL_DECISION', 'ENGINEERING_PRINCIPLE')

CABECALHO = re.compile(r'^## (COL-LAW-\d{3}) · (.+?)\s*$', re.M)
RE_ORIGEM = re.compile(r'\*\*ORIGEM\.\*\*\s*(.+)')
RE_LAW = re.compile(r'\*\*LAW_STATUS\*\*\s*`([A-Z_]+)`')
RE_IT = re.compile(r'\*\*IT\*\*\s*`([A-Z_]+)`')
# um ficheiro do repositorio citado em crase: `pedido/pedido.py`, `docs/x/Y.md`
RE_FICHEIRO = re.compile(r'`([A-Za-z0-9_\-./]+\.(?:py|mjs|md|json|sql|yml|ndjson))`')


def _ler(p: str) -> str:
    with open(p, encoding='utf-8') as f:
        return f.read()


def leis_do_texto(texto: str) -> list:
    """Cada lei, lida do proprio texto da Biblia. Nada declarado a mao."""
    marcas = list(CABECALHO.finditer(texto))
    saida = []
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        corpo = texto[m.end():fim]
        origem = RE_ORIGEM.search(corpo)
        law = RE_LAW.search(corpo)
        it = RE_IT.search(corpo)
        saida.append({
            'id': m.group(1),
            'nome': m.group(2).strip(),
            # a origem pode vir com ponteiro entre parenteses; guarda-se so a etiqueta
            'origem': sorted({o for o in ORIGENS_VALIDAS
                              if origem and o in origem.group(1)}),
            'law_status': law.group(1) if law else '',
            'italia': it.group(1) if it else '',
        })
    return saida


def cabecalho_da_biblia(texto: str) -> dict:
    """O bloco de versionamento no topo — BIBLE_ID, VERSION, e o resto."""
    bloco = texto.split('```', 2)
    if len(bloco) < 2:
        return {}
    d = {}
    for linha in bloco[1].splitlines():
        partes = linha.split(None, 1)
        if len(partes) == 2:
            d[partes[0].strip()] = partes[1].strip()
    return d


def main() -> int:
    falhas = []

    def prova(nome, frase, ok, detalhe=''):
        print('  %-4s %-26s %s' % ('PASS' if ok else 'FAIL', nome, frase))
        if not ok:
            falhas.append(nome)
            if detalhe:
                print('        %s' % detalhe)

    # ── B1 ───────────────────────────────────────────────────────────────────
    faltam = [os.path.relpath(p, ROOT) for p in
              (BIBLIA, CENSO, CONFLITOS, CONFORMIDADE) if not os.path.isfile(p)]
    prova('B1_BIBLIA_EXISTE', 'a Biblia e os apendices estao no sitio declarado',
          not faltam, ', '.join(faltam))
    if faltam:
        print('\nBIBLIA_CHECK=FAIL · sem os ficheiros nao ha o que medir.')
        return 1

    texto = _ler(BIBLIA)
    leis = leis_do_texto(texto)
    ids = [x['id'] for x in leis]

    # ── B2 ───────────────────────────────────────────────────────────────────
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    prova('B2_IDS_UNICOS', 'nenhum COL-LAW repetido', not repetidos,
          ', '.join(repetidos))

    # ── B3 ───────────────────────────────────────────────────────────────────
    incompletas = [x['id'] for x in leis
                   if not x['origem'] or not x['law_status'] or not x['italia']]
    prova('B3_LEI_COMPLETA', 'toda lei declara origem, estado de lei e estado na Italia',
          not incompletas, ', '.join(incompletas))

    # ── B4 ───────────────────────────────────────────────────────────────────
    maus = [f"{x['id']} law={x['law_status']} it={x['italia']}" for x in leis
            if x['law_status'] not in LAW_STATUS_VALIDOS or x['italia'] not in IMPL_VALIDOS]
    prova('B4_STATUS_VALIDO', 'os dois eixos so usam valores conhecidos',
          not maus, ' | '.join(maus))

    # ── B5 e B6 ──────────────────────────────────────────────────────────────
    cab = cabecalho_da_biblia(texto)
    exigidos = ('BIBLE_ID', 'VERSION', 'STATUS', 'EFFECTIVE_FROM', 'CURRENT_PROFILE')
    sem = [k for k in exigidos if not cab.get(k)]
    prova('B5_VERSAO_DECLARADA', 'a Biblia diz quem e, que versao e desde quando',
          not sem, ', '.join(sem))
    perfil = cab.get('CURRENT_PROFILE', '')
    prova('B6_PERFIL_IT_DECLARADO', 'o perfil corrente esta declarado e nomeia o pais',
          bool(perfil) and 'ITALY' in perfil.upper(), perfil)

    # ── B7 · os apendices nao podem citar lei que nao existe ────────────────
    conhecidas = set(ids)
    orfas = set()
    for p in (CENSO, CONFLITOS, CONFORMIDADE):
        for citada in re.findall(r'COL-LAW-\d{3}', _ler(p)):
            if citada not in conhecidas:
                orfas.add(f'{os.path.basename(p)}:{citada}')
    prova('B7_REFERENCIA_EXISTE', 'toda lei citada pelos apendices existe na Biblia',
          not orfas, ', '.join(sorted(orfas)))

    # ── B8 · a matriz de conformidade fala de TODAS, e so delas ─────────────
    na_matriz = set(re.findall(r'COL-LAW-\d{3}', _ler(CONFORMIDADE)))
    sem_medida = sorted(conhecidas - na_matriz)
    prova('B8_CONFORMIDADE_COBRE', 'a matriz mede todas as leis da Biblia',
          not sem_medida, ', '.join(sem_medida))

    # ── B9 · ficheiro citado como contrato tem de existir ───────────────────
    # So se conferem caminhos com pasta: `pedido/pedido.py` e uma promessa;
    # `leis.json` sozinho e o nome de um ficheiro, nao um caminho.
    fantasmas = sorted({f for f in RE_FICHEIRO.findall(texto)
                        if '/' in f and not f.endswith('*')
                        and not os.path.exists(os.path.join(ROOT, f))})
    prova('B9_FICHEIROS_CITADOS', 'todo ficheiro que a Biblia cita existe no repositorio',
          not fantasmas, ', '.join(fantasmas[:8]))

    # ── B10 · o JSON e o texto dizem a mesma coisa ──────────────────────────
    pacote = {
        'SCHEMA': 'sintonia.collection-bible/1',
        'NOTA': 'DERIVADO de BIBLIA-CANONICA-DA-COLETA.md. Nao editar a mao: '
                'corra `py provas/valida_biblia.py --build`.',
        'BIBLE_ID': cab.get('BIBLE_ID', ''),
        'VERSION': cab.get('VERSION', ''),
        'STATUS': cab.get('STATUS', ''),
        'EFFECTIVE_FROM': cab.get('EFFECTIVE_FROM', ''),
        'CURRENT_PROFILE': cab.get('CURRENT_PROFILE', ''),
        'LAWS': leis,
    }
    if '--build' in sys.argv:
        os.makedirs(PASTA, exist_ok=True)
        with open(LEIS_JSON, 'w', encoding='utf-8') as f:
            json.dump(pacote, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('\nLEIS_JSON_GERADO=OK · %s · %d leis'
              % (os.path.relpath(LEIS_JSON, ROOT), len(leis)))
        return 0

    igual = False
    if os.path.isfile(LEIS_JSON):
        try:
            igual = json.loads(_ler(LEIS_JSON)) == pacote
        except ValueError:
            igual = False
    prova('B10_JSON_BATE_COM_O_TEXTO', 'leis.json e exatamente o que o texto diz',
          igual, 'corra `py provas/valida_biblia.py --build` e comite o resultado')

    print('\n  %d leis canonicas · %s' % (len(leis), ' · '.join(
        '%s %d' % (e, sum(1 for x in leis if x['italia'] == e)) for e in IMPL_VALIDOS)))

    if falhas:
        print('\nBIBLIA_CHECK=FAIL · %s' % ', '.join(falhas))
        return 1
    print('\nBIBLIA_CHECK=PASS · a Biblia, os apendices e o registo dizem a mesma coisa')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:                                   # noqa: BLE001
        print('BIBLIA_CHECK=FAIL · erro inesperado: %s' % e, file=sys.stderr)
        raise SystemExit(1)
