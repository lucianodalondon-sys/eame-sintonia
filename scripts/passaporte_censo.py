#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CENSO DO PASSAPORTE — reprodução dos números de PASSPORT-DEFEITOS-HERDADOS.md.

SOMENTE LEITURA. Este script não escreve nada: nem no acervo, nem em
`data/passaporte/EVENTOS.jsonl`, nem em disco. Ele mede e imprime.

Uso:
    python3 scripts/passaporte_censo.py [--acervo CAMINHO] [--passaporte CAMINHO]

`--acervo`      raiz do repositório canônico a medir       (default: o repo deste script)
`--passaporte`  raiz do worktree que contém o PASSPORT-1.0 (default: nenhum; as medidas
                que dependem do log de eventos são puladas e declaradas como puladas)

Nenhuma medida é estimada. Quando uma fonte não está disponível, o censo imprime
NAO_MEDIDO com o motivo — nunca zero.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

# ── sentinelas ─────────────────────────────────────────────────────────────────────
# A tupla exata usada por passaporte_backfill.py:55. É reproduzida aqui de propósito:
# o censo precisa medir o comportamento REAL da trava, não uma versão melhorada dela.
NAO_SEI_EXATO = ('NÃO SEI', 'NAO SEI', 'NOT_KNOWN', 'NAO_DECLARADO', 'NOT_DECLARED',
                 'UNKNOWN', '', None)

# O que a trava exata NÃO pega: sentinela seguida de explicação.
SENTINELA_COM_SUFIXO = re.compile(r'^\s*(NÃO SEI|NAO SEI|NOT_KNOWN|UNKNOWN)\s*[—\-–:·]',
                                  re.IGNORECASE)

CAMPOS_DE_IDENTIDADE = re.compile(
    r'^(EXTERNAL_ID|ENTITY_ID|PERSON_ID|ACCOUNT_HANDLE|CHANNEL_ID|CONTENT_ID'
    r'|SOURCE_ID|ITEM_ID|HANDLE)$', re.IGNORECASE)

CONCEITOS_DO_PASSAPORTE_UNIVERSAL = [
    'CROP', 'ISSUE', 'ISSUE_TYPE', 'COUNTRY', 'REGION', 'SUBREGION',
    'TIME_START', 'TIME_END', 'PROOF_STATE', 'OBSERVATION_STATE',
    'INDEPENDENCE_STATE', 'FAMILY_ID', 'LINEAGE_ID', 'RELATIONSHIP_ID',
    'CROSSING_ID', 'ADAMA_RELATION', 'PRODUCT_RELATION', 'UNIT_COUNT',
]


def _sabido_como_o_backfill_faz(v):
    """Cópia fiel de passaporte_backfill.py::_sabido. Não corrigir — é o objeto medido."""
    return v not in NAO_SEI_EXATO and str(v).strip() != ''


# ── leitura ────────────────────────────────────────────────────────────────────────

def _percorrer_json(raiz, limite_jsonl=3000):
    """Gera (caminho, objeto) para cada .json/.jsonl legível sob `raiz`.

    Arquivo ilegível não vira zero: vira uma entrada em `_percorrer_json.falhas`.
    """
    _percorrer_json.falhas = []
    for pasta, _, arquivos in os.walk(raiz):
        if '.git' in pasta.split(os.sep):
            continue
        for nome in sorted(arquivos):
            if not nome.endswith(('.json', '.jsonl')):
                continue
            caminho = os.path.join(pasta, nome)
            try:
                if nome.endswith('.jsonl'):
                    with open(caminho, encoding='utf-8') as f:
                        for i, linha in enumerate(f):
                            if i >= limite_jsonl:
                                break
                            linha = linha.strip()
                            if linha:
                                yield caminho, json.loads(linha)
                else:
                    with open(caminho, encoding='utf-8') as f:
                        yield caminho, json.load(f)
            except Exception as erro:                     # noqa: BLE001
                _percorrer_json.falhas.append((caminho, str(erro)[:90]))


def _andar(objeto, visitar, caminho_arquivo, teto_lista=None):
    """Percorre a estrutura inteira. Sem teto por padrão.

    Truncar lista é perder informação, e perda silenciosa é o defeito que este censo
    existe para medir. Se um teto for imposto, cada corte é contado em
    `_andar.truncadas` e impresso — nunca some.
    """
    if isinstance(objeto, dict):
        for chave, valor in objeto.items():
            visitar(chave, valor, caminho_arquivo)
            _andar(valor, visitar, caminho_arquivo, teto_lista)
    elif isinstance(objeto, list):
        if teto_lista is not None and len(objeto) > teto_lista:
            _andar.truncadas.append((caminho_arquivo, len(objeto), teto_lista))
            objeto = objeto[:teto_lista]
        for valor in objeto:
            _andar(valor, visitar, caminho_arquivo, teto_lista)


_andar.truncadas = []


# ── medidas sobre o ACERVO ─────────────────────────────────────────────────────────

def censo_sentinela_com_sufixo(acervo):
    """D8 — valores que a trava exata deixa passar como se fossem conhecidos."""
    por_campo = collections.Counter()
    exemplos = collections.defaultdict(list)
    arquivos = set()

    def visitar(chave, valor, arquivo):
        if isinstance(valor, str) and SENTINELA_COM_SUFIXO.match(valor):
            # a prova do defeito: a trava do backfill considera este valor CONHECIDO
            if _sabido_como_o_backfill_faz(valor):
                por_campo[chave] += 1
                arquivos.add(arquivo)
                if len(exemplos[chave]) < 2:
                    exemplos[chave].append(valor[:80])

    for arquivo, objeto in _percorrer_json(os.path.join(acervo, 'data')):
        _andar(objeto, visitar, arquivo)
    return por_campo, exemplos, arquivos


def censo_identidade_invalida(acervo):
    """D2 — campos de identidade cujo valor não é identidade."""
    por_arquivo = collections.defaultdict(collections.Counter)

    def visitar(chave, valor, arquivo):
        if not CAMPOS_DE_IDENTIDADE.match(chave):
            return
        if valor is None or (isinstance(valor, str)
                             and valor.strip().upper() in
                             {s.upper() for s in NAO_SEI_EXATO if isinstance(s, str)}):
            por_arquivo[os.path.relpath(arquivo, acervo)][chave] += 1

    for arquivo, objeto in _percorrer_json(os.path.join(acervo, 'data')):
        _andar(objeto, visitar, arquivo)
    return por_arquivo


def censo_transcricoes(acervo, ids_no_passaporte):
    """D3 — transcrições do acervo, dentro e fora do passaporte.

    `ids_no_passaporte` é None quando o log não foi informado: nesse caso o censo
    devolve a contagem do acervo e declara a comparação como NAO_MEDIDA.
    """
    pasta = os.path.join(acervo, 'data', 'samples', 'SENSOR-PILOT')
    dentro, fora, sem_id_recuperavel = [], [], 0
    if not os.path.isdir(pasta):
        return None
    for nome in sorted(os.listdir(pasta)):
        if not nome.startswith('TRANSCRICOES-'):
            continue
        with open(os.path.join(pasta, nome), encoding='utf-8') as f:
            dados = json.load(f)
        for item in dados.get('ITEMS', []):
            achado = re.search(r'watch\?v=([A-Za-z0-9_-]{6,})',
                               str(item.get('SOURCE_URL', '')))
            if not achado:
                sem_id_recuperavel += 1
                continue
            registro = (achado.group(1), len(item.get('TRANSCRIPT') or ''), nome)
            if ids_no_passaporte is None:
                fora.append(registro)          # sem log, nada pode ser dado como dentro
            elif achado.group(1) in ids_no_passaporte:
                dentro.append(registro)
            else:
                fora.append(registro)
    return dentro, fora, sem_id_recuperavel


# ── medidas sobre o LOG DE EVENTOS ─────────────────────────────────────────────────

def ler_eventos(passaporte):
    caminho = os.path.join(passaporte, 'data', 'passaporte', 'EVENTOS.jsonl')
    if not os.path.isfile(caminho):
        return None
    with open(caminho, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def censo_estado_contra_motivo(eventos, tipo):
    """D1 — eventos cujo TO_STATE afirma e cujo REASON nega."""
    pares = collections.Counter()
    amostra = []
    for e in eventos:
        if e.get('EVENT_TYPE') != tipo:
            continue
        motivo = str(e.get('REASON'))
        contradiz = bool(SENTINELA_COM_SUFIXO.match(motivo)) or \
            motivo.strip().upper() in {'NÃO SEI', 'NAO SEI', 'UNKNOWN', 'NOT_KNOWN'}
        pares[(e.get('TO_STATE'), 'MOTIVO_DIZ_NAO_SEI' if contradiz else 'motivo_normal')] += 1
        if contradiz and e.get('TO_STATE') not in (None, 'NOT_KNOWN', 'UNKNOWN') \
                and len(amostra) < 3:
            amostra.append({k: e.get(k) for k in ('ITEM_ID', 'TO_STATE', 'REASON')})
    return pares, amostra


def censo_colapso_de_identidade(eventos):
    """D2 — bases de identidade que são sentinela, e quantas capturas caíram em cada uma."""
    capturas = collections.Counter()
    itens = collections.defaultdict(set)
    for e in eventos:
        base = e.get('IDENTITY_BASIS')
        if not base:
            continue
        itens[base].add(e.get('ITEM_ID'))
        if e.get('EVENT_TYPE') == 'ITEM_CAPTURED':
            capturas[base] += 1
    suspeitas = {b: (len(itens[b]), capturas[b]) for b in itens
                 if any(s in str(b).upper() for s in ('NÃO SEI', 'NAO SEI', 'UNKNOWN',
                                                      'NOT_KNOWN'))}
    varios = {b: len(v) for b, v in itens.items() if len(v) > 1}
    return suspeitas, varios


def censo_chaves_ausentes(eventos):
    """D4 — quais conceitos do passaporte universal não existem como chave no log."""
    presentes = set()
    for e in eventos:
        presentes.update(e.keys())
    return {c: (c in presentes) for c in CONCEITOS_DO_PASSAPORTE_UNIVERSAL}


def censo_valor_em_prosa(eventos, tipo):
    """D4 — o valor da dimensão, que mora em REASON, e suas grafias concorrentes."""
    valores = collections.Counter()
    for e in eventos:
        if e.get('EVENT_TYPE') == tipo and e.get('TO_STATE') == 'DECLARED':
            valores[str(e.get('REASON'))] += 1
    grafias = collections.defaultdict(list)
    for valor, n in valores.items():
        chave = re.sub(r"[\[\]'\" ]", '', valor).upper()
        grafias[chave].append((valor, n))
    concorrentes = {k: v for k, v in grafias.items() if len(v) > 1}
    return valores, concorrentes


def censo_append_only(eventos):
    """D5 — o log preserva história? a projeção arbitra por recência?"""
    ids = collections.Counter(e.get('EVENT_ID') for e in eventos)
    escrita = {'IDENTITY_PROVED': 'IDENTITY_STATE', 'IDENTITY_NOT_PROVED': 'IDENTITY_STATE',
               'CONTENT_SCANNED': 'CONTENT_READ_STATE', 'CONTENT_READ': 'CONTENT_READ_STATE',
               'TRANSCRIPT_READ': 'CONTENT_READ_STATE'}
    historico = collections.defaultdict(list)
    for e in eventos:
        campo = escrita.get(e.get('EVENT_TYPE'))
        if campo:
            historico[(e['ITEM_ID'], campo)].append(e.get('TO_STATE'))
    multiplos = collections.Counter(campo for (_, campo), v in historico.items() if len(v) > 1)
    return {
        'EVENT_ID_REPETIDOS': sum(1 for n in ids.values() if n > 1),
        'ITENS_COM_2_OU_MAIS_SELOS': dict(multiplos),
    }


# ── impressão ──────────────────────────────────────────────────────────────────────

def _secao(titulo):
    print('\n' + '─' * 78)
    print(titulo)
    print('─' * 78)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--acervo', default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    p.add_argument('--passaporte', default=None)
    args = p.parse_args(argv)

    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:                                  # noqa: BLE001
            pass

    print('CENSO DO PASSAPORTE — somente leitura')
    print(f'ACERVO      = {args.acervo}')
    print(f'PASSAPORTE  = {args.passaporte or "NAO_INFORMADO"}')

    # ---- D8 ----
    _secao('D8 · sentinela com sufixo que a trava exata deixa passar')
    por_campo, exemplos, arquivos = censo_sentinela_com_sufixo(args.acervo)
    print(f'total = {sum(por_campo.values())} ocorrências · '
          f'{len(arquivos)} arquivos · {len(por_campo)} campos')
    for campo, n in por_campo.most_common():
        print(f'   {n:6d}  {campo}')
        for exemplo in exemplos[campo]:
            print(f'          {exemplo}')
    if _percorrer_json.falhas:
        print(f'   NAO_MEDIDO: {len(_percorrer_json.falhas)} arquivos ilegíveis '
              f'(ilegível NÃO é zero)')

    # ---- D2 (acervo) ----
    _secao('D2 · campos de identidade com valor que não é identidade')
    por_arquivo = censo_identidade_invalida(args.acervo)
    # O total soma TODOS os arquivos. A impressão mostra os 15 maiores — e diz
    # quantos ficaram de fora da tela, para que a tela não pareça o total.
    total = collections.Counter()
    for contagem in por_arquivo.values():
        total.update(contagem)
    ordenados = sorted(por_arquivo.items(), key=lambda x: -sum(x[1].values()))
    for arquivo, contagem in ordenados[:15]:
        print(f'   {sum(contagem.values()):6d}  {arquivo}')
    if len(ordenados) > 15:
        resto = sum(sum(c.values()) for _, c in ordenados[15:])
        print(f'   … mais {len(ordenados) - 15} arquivos, {resto} ocorrências '
              f'(somadas no total abaixo, não mostradas acima)')
    print(f'   ── total por campo · {len(por_arquivo)} arquivos ──')
    for campo, n in total.most_common():
        print(f'   {n:6d}  {campo}')

    if not args.passaporte:
        _secao('MEDIDAS QUE DEPENDEM DO LOG DE EVENTOS')
        print('   NAO_MEDIDO — --passaporte não foi informado.')
        print('   Ausência de medição NÃO é ausência de defeito.')
        return 0

    eventos = ler_eventos(args.passaporte)
    if eventos is None:
        _secao('MEDIDAS QUE DEPENDEM DO LOG DE EVENTOS')
        print(f'   NAO_MEDIDO — EVENTOS.jsonl não encontrado em {args.passaporte}')
        return 0
    print(f'\neventos lidos = {len(eventos)}')

    # ---- D1 ----
    _secao('D1 · estado que afirma contra motivo que nega')
    for tipo in ('TIME_RESOLVED', 'GEOGRAPHY_PROVED', 'GEOGRAPHY_NOT_PROVED'):
        pares, amostra = censo_estado_contra_motivo(eventos, tipo)
        if not pares:
            continue
        print(f'  {tipo}:')
        for chave, n in sorted(pares.items(), key=lambda x: -x[1]):
            marca = '   ← DEFEITO' if chave[1] == 'MOTIVO_DIZ_NAO_SEI' and \
                chave[0] not in (None, 'NOT_KNOWN', 'UNKNOWN') else ''
            print(f'     {n:6d}  {chave}{marca}')
        for a in amostra:
            print(f'        {a}')

    # ---- D2 (log) ----
    _secao('D2 · colapso de identidade no log')
    suspeitas, varios = censo_colapso_de_identidade(eventos)
    if not suspeitas:
        print('   nenhuma base de identidade é sentinela')
    for base, (n_itens, n_capturas) in suspeitas.items():
        print(f'   base={base!r}')
        print(f'      ITEM_ID distintos = {n_itens} · capturas = {n_capturas}'
              f'   → {n_capturas - n_itens} linha(s) de origem absorvida(s)')
    print(f'   bases servindo mais de um ITEM_ID: {len(varios)}')

    # ---- D3 ----
    _secao('D3 · transcrições do acervo, dentro e fora do passaporte')
    ids = {str(e['IDENTITY_BASIS']).split(':TRANSCRIPT:')[1].split(':')[0]
           for e in eventos
           if e.get('IDENTITY_BASIS') and ':TRANSCRIPT:' in str(e['IDENTITY_BASIS'])}
    resultado = censo_transcricoes(args.acervo, ids)
    if resultado is None:
        print('   NAO_MEDIDO — pasta SENSOR-PILOT ausente')
    else:
        dentro, fora, sem_id = resultado
        com_texto = [r for r in fora if r[1] > 0]
        print(f'   DENTRO  {len(dentro):3d} registros · {sum(r[1] for r in dentro):>9,} chars')
        print(f'   FORA    {len(fora):3d} registros · {sum(r[1] for r in fora):>9,} chars')
        print(f'      dos que estão fora, com texto real: {len(com_texto)} · '
              f'{sum(r[1] for r in com_texto):,} chars')
        print(f'      sem id recuperável da URL: {sem_id}')

    # ---- D4 ----
    _secao('D4 · o valor da dimensão não tem campo')
    for conceito, presente in censo_chaves_ausentes(eventos).items():
        print(f'   {conceito:20s} {"PRESENTE" if presente else "AUSENTE"}')
    for tipo in ('CROP_DECLARED', 'ISSUE_DECLARED'):
        valores, concorrentes = censo_valor_em_prosa(eventos, tipo)
        print(f'\n  {tipo}: {len(valores)} grafias distintas em REASON')
        for chave, lista in sorted(concorrentes.items())[:6]:
            grafias = ' vs '.join(f'{v!r}({n})' for v, n in lista)
            print(f'     MESMO VALOR, GRAFIAS DIFERENTES · {chave}: {grafias}')

    # ---- D5 ----
    _secao('D5 · append-only e arbitragem por recência')
    for chave, valor in censo_append_only(eventos).items():
        print(f'   {chave} = {valor}')
    print('   (história preservada no log; a projeção em passaporte.py:509 fica com o')
    print('    ÚLTIMO selo, sem comparar força de prova e sem estado de conflito)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
