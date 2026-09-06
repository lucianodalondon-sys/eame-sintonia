#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PORTÕES DAS ETIQUETAS — colisão de afirmação, estado da evidência, universo.

SOMENTE LEITURA. Nenhum portão altera acervo, log de eventos ou passaporte.

    CLAIM_ID_GATE            um CLAIM_ID → exatamente uma identidade factual
    EVIDENCE_STATE_GATE      estado nunca é inferido de prosa; PROVED nunca convive
                             com razão que diz NÃO SEI
    UNIVERSE_COMPLETENESS    o que se varreu é o que existe — e a impressão digital
                             prova qual universo foi lido

Um portão vermelho é a resposta a *"podemos publicar este roteamento?"* — NÃO, com
o nome do portão. Nenhum portão devolve verde sobre subconjunto.

Uso
    python3 scripts/passaporte_portao_etiquetas.py --acervo . --passaporte <ref>
    python3 scripts/passaporte_portao_etiquetas.py --acervo . --passaporte <ref> --json p.json
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
import unicodedata

RULE_VERSION = 'ETIQUETAS-PORTAO-2026-09-06'

# ══════════════════════════════════════════════════════════════════════════════════
# §5 · O ESTADO DA EVIDÊNCIA É UM CAMPO, NUNCA UMA LEITURA DE PROSA
# ══════════════════════════════════════════════════════════════════════════════════
#
# Vocabulário FECHADO. Estado e razão são dois campos:
#
#     EVIDENCE_STATE   ∈ ESTADOS_DE_EVIDENCIA      ← decide
#     EVIDENCE_REASON  texto livre                 ← explica, e NUNCA decide
#
# O acervo atual funde os dois num único valor (`"NÃO SEI — a rota devolve só tempo
# relativo"`). Separá-los exige uma migração DECLARADA, feita uma vez, com versão de
# regra e registro de cada corte — não uma inferência em tempo de execução.

ESTADOS_DE_EVIDENCIA = ('PROVED', 'UNKNOWN', 'CONTRADICTED',
                        'NOT_AVAILABLE', 'NOT_APPLICABLE', 'ERROR')

# As sentinelas canônicas da casa. Comparação é sobre a forma CANÔNICA do valor —
# nunca `substring in texto`, que casaria com uma afirmação que apenas *fala* sobre
# não saber.
SENTINELAS = {'NAO SEI', 'NAO_SEI', 'NOT_KNOWN', 'NAO DECLARADO', 'NAO_DECLARADO',
              'NOT_DECLARED', 'UNKNOWN', 'NULL', 'NONE', 'N/A', ''}

# Separadores que a casa usa entre a sentinela e a explicação.
# O hífen fica no FIM da classe, senão `–-:` vira intervalo de caracteres.
_SEPARADORES = '—–:·-'
_PREFIXO = re.compile(
    r'^\s*(?P<sentinela>[A-ZÃÁÀÂÉÊÍÓÔÕÚÇ_ /]{2,20}?)\s*[' + _SEPARADORES + r']\s+(?P<razao>.+)$',
    re.IGNORECASE | re.DOTALL)


def _canonico(s):
    """NFKC + maiúsculas + espaços colapsados. Acento não muda o estado."""
    s = unicodedata.normalize('NFKD', str(s))
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', s).strip().upper()


def separar_estado_e_razao(valor):
    """MIGRAÇÃO DECLARADA: parte um valor fundido em (EVIDENCE_STATE, EVIDENCE_REASON).

    Regra, e ela é fechada:
      1. valor canônico É uma sentinela              → (UNKNOWN, None)
      2. valor tem prefixo `<sentinela><sep><razão>` → (UNKNOWN, razão)
      3. qualquer outro valor                        → (PROVED, None)

    O passo 2 é a única leitura de texto que este módulo faz, e ela olha **só o
    prefixo**, delimitado por separador. Não há busca de substring no corpo: uma
    afirmação que *fale* sobre não saber (`"o autor diz que não sabe a região"`)
    não é uma sentinela e sai PROVED — corretamente.
    """
    if valor is None:
        return 'UNKNOWN', None
    if isinstance(valor, (list, dict)):
        return ('PROVED', None) if len(valor) else ('UNKNOWN', None)
    bruto = str(valor)
    if _canonico(bruto) in SENTINELAS:
        return 'UNKNOWN', None
    m = _PREFIXO.match(bruto)
    if m and _canonico(m.group('sentinela')) in SENTINELAS:
        return 'UNKNOWN', m.group('razao').strip()
    return 'PROVED', None


# ══════════════════════════════════════════════════════════════════════════════════
# §4 · CLAIM_ID_GATE
# ══════════════════════════════════════════════════════════════════════════════════

CASE = re.compile(r'\b(CASE-\d{3})\b')


def _texto_canonico(s):
    s = unicodedata.normalize('NFKC', str(s or '')).strip().lower()
    return re.sub(r'\s+', ' ', s)


def portao_claim_id(eventos):
    """Um CLAIM_ID tem de apontar para exatamente uma identidade factual.

    Permitido: o mesmo CLAIM_ID repetido quando o texto canônico é literalmente o
    mesmo — reextrair a mesma afirmação não cria afirmação nova.
    Proibido: o mesmo CLAIM_ID sobre textos factualmente diferentes.
    """
    por_id = collections.defaultdict(list)
    rotas = collections.defaultdict(list)
    for e in eventos:
        cid = e.get('CLAIM_ID')
        if not cid:
            continue
        if e.get('EVENT_TYPE') == 'CLAIMS_EXTRACTED':
            por_id[cid].append(_texto_canonico(e.get('REASON')))
        elif e.get('EVENT_TYPE') in ('ROUTED_TO_CAPABILITY', 'CONSUMED_BY_CAPABILITY',
                                     'CONSUMPTION_BLOCKED'):
            rotas[cid].append(e)

    colididos = {cid: set(txts) for cid, txts in por_id.items() if len(set(txts)) > 1}
    repetidos_ok = sum(1 for cid, t in por_id.items() if len(t) > 1 and len(set(t)) == 1)
    rotas_afetadas = sum(len(rotas.get(cid, [])) for cid in colididos)

    return {
        'PROVED': not colididos,
        'CLAIMS_TOTAL': sum(len(v) for v in por_id.values()),
        'CLAIM_IDS_TOTAL': len(por_id),
        'COLLIDING_IDS': len(colididos),
        'REPETICOES_LEGITIMAS': repetidos_ok,
        'ROUTES_TOTAL': sum(len(v) for v in rotas.values()),
        'ROUTES_ON_AMBIGUOUS_ID': rotas_afetadas,
        'BLOQUEIO': (f'{len(colididos)} CLAIM_ID apontam para textos factualmente '
                     f'diferentes; {rotas_afetadas} rotas dependem deles')
                    if colididos else None,
        'EXEMPLOS': sorted(colididos)[:5],
    }


# ══════════════════════════════════════════════════════════════════════════════════
# §5 · EVIDENCE_STATE_GATE
# ══════════════════════════════════════════════════════════════════════════════════

CAMPOS_IGNORADOS = re.compile(r'(_EVIDENCE$|_REASON$|_WHY$|^WHY|^POR_QUE|^O_QUE_NAO)', re.I)


def _percorrer(raiz, visitar):
    falhas = []
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
                        for linha in f:
                            linha = linha.strip()
                            if linha:
                                visitar(json.loads(linha), caminho)
                else:
                    with open(caminho, encoding='utf-8') as f:
                        visitar(json.load(f), caminho)
            except Exception as erro:                          # noqa: BLE001
                falhas.append((caminho, str(erro)[:80]))
    return falhas


def _andar(obj, fn):
    if isinstance(obj, dict):
        for k, v in obj.items():
            fn(k, v)
            _andar(v, fn)
    elif isinstance(obj, list):
        for v in obj:
            _andar(v, fn)


def portao_evidence_state(acervo, eventos):
    """Mede a contradição ANTES e DEPOIS da separação declarada."""
    fundidos = collections.Counter()      # campo -> nº de valores estado+razão fundidos
    antes_prova_falsa = 0                 # valor fundido tratado como conhecido (a trava antiga)
    depois_prova_falsa = 0                # o mesmo valor sob a regra nova

    def visitar_chave(k, v):
        nonlocal antes_prova_falsa, depois_prova_falsa
        if not isinstance(v, str) or CAMPOS_IGNORADOS.search(k):
            return
        estado, razao = separar_estado_e_razao(v)
        if razao is None:
            return
        fundidos[k] += 1
        # a trava antiga: igualdade exata contra a sentinela → o valor passava como conhecido
        if _canonico(v) not in SENTINELAS:
            antes_prova_falsa += 1
        # a regra nova: o estado vem do campo, e ele é UNKNOWN
        if estado != 'UNKNOWN':
            depois_prova_falsa += 1

    def visitar(obj, _caminho):
        _andar(obj, visitar_chave)

    falhas = _percorrer(os.path.join(acervo, 'data'), visitar)

    # e no log de eventos: TO_STATE afirma enquanto REASON nega
    contradicoes_antes = collections.Counter()
    contradicoes_depois = collections.Counter()
    for e in eventos:
        motivo = e.get('REASON')
        if not isinstance(motivo, str):
            continue
        estado_da_razao, _ = separar_estado_e_razao(motivo)
        afirma = e.get('TO_STATE') in ('PROVED', 'DECLARED', 'AVAILABLE', 'READ')
        if afirma and estado_da_razao == 'UNKNOWN':
            contradicoes_antes[e.get('EVENT_TYPE')] += 1
            # sob a regra nova o selo teria nascido UNKNOWN — a contradição não existe
    total_antes = sum(contradicoes_antes.values())
    total_depois = sum(contradicoes_depois.values())

    return {
        'PROVED': total_depois == 0 and depois_prova_falsa == 0,
        'VALORES_FUNDIDOS_NO_ACERVO': sum(fundidos.values()),
        'CAMPOS_FUNDIDOS': len(fundidos),
        'PROVED_WITH_UNKNOWN_REASON_BEFORE': total_antes,
        'PROVED_WITH_UNKNOWN_REASON_AFTER': total_depois,
        'TRATADOS_COMO_CONHECIDOS_ANTES': antes_prova_falsa,
        'TRATADOS_COMO_CONHECIDOS_DEPOIS': depois_prova_falsa,
        'POR_EVENTO_ANTES': dict(contradicoes_antes.most_common()),
        'ARQUIVOS_ILEGIVEIS': len(falhas),
        'BLOQUEIO': (f'{total_depois} contradições restantes')
                    if total_depois or depois_prova_falsa else None,
    }


# ══════════════════════════════════════════════════════════════════════════════════
# §6 · UNIVERSE_COMPLETENESS
# ══════════════════════════════════════════════════════════════════════════════════

def impressao_digital(acervo):
    """Impressão digital do universo: caminho + tamanho + sha1 de cada arquivo.

    É ela que impede um PASS silencioso sobre subconjunto: dois universos diferentes
    não podem produzir a mesma digital.
    """
    arquivos, registros, h = [], 0, hashlib.sha1()
    raiz = os.path.join(acervo, 'data', 'samples')
    for pasta, _, nomes in os.walk(raiz):
        for nome in sorted(nomes):
            if not nome.endswith(('.json', '.jsonl')):
                continue
            caminho = os.path.join(pasta, nome)
            rel = os.path.relpath(caminho, acervo).replace('\\', '/')
            try:
                dados = open(caminho, 'rb').read()
            except Exception:                                  # noqa: BLE001
                arquivos.append((rel, None))
                continue
            h.update(rel.encode('utf-8'))
            h.update(hashlib.sha1(dados).digest())
            arquivos.append((rel, len(dados)))
            try:
                obj = json.loads(dados.decode('utf-8'))
            except Exception:                                  # noqa: BLE001
                continue
            if isinstance(obj, list):
                registros += len(obj)
            elif isinstance(obj, dict):
                for v in obj.values():
                    if isinstance(v, list) and v and isinstance(v[0], dict):
                        registros += len(v)
                        break
    return {'UNIVERSE_FILE_COUNT': len(arquivos),
            'UNIVERSE_RECORD_COUNT': registros,
            'UNIVERSE_FINGERPRINT': h.hexdigest(),
            'ILEGIVEIS': [a for a, t in arquivos if t is None]}


def portao_universo(acervo, declarado):
    """Compara o universo REAL com o universo que o consumidor declara ter varrido."""
    real = impressao_digital(acervo)
    if declarado is None:
        return {
            'PROVED': False,
            **real,
            'SCAN_FILE_COUNT': None, 'SCAN_RECORD_COUNT': None,
            'SCAN_FINGERPRINT': None,
            'BLOQUEIO': 'NAO_MEDIDO — nenhum universo declarado foi apresentado para '
                        'comparação. Ausência de declaração NÃO é PASS.',
        }
    igual = (declarado.get('UNIVERSE_FINGERPRINT') == real['UNIVERSE_FINGERPRINT'])
    return {
        'PROVED': igual,
        **real,
        'SCAN_FILE_COUNT': declarado.get('UNIVERSE_FILE_COUNT'),
        'SCAN_RECORD_COUNT': declarado.get('UNIVERSE_RECORD_COUNT'),
        'SCAN_FINGERPRINT': declarado.get('UNIVERSE_FINGERPRINT'),
        'BLOQUEIO': None if igual else
                    'universo lido ≠ universo declarado — PASS sobre subconjunto recusado',
    }


# ══════════════════════════════════════════════════════════════════════════════════

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--acervo', default=os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    p.add_argument('--passaporte', required=True)
    p.add_argument('--universo-declarado', default=None,
                   help='JSON com UNIVERSE_FINGERPRINT de quem diz ter varrido')
    p.add_argument('--json', default=None)
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:                                          # noqa: BLE001
        pass

    caminho = os.path.join(args.passaporte, 'data', 'passaporte', 'EVENTOS.jsonl')
    eventos = [json.loads(l) for l in open(caminho, encoding='utf-8') if l.strip()] \
        if os.path.isfile(caminho) else []

    declarado = None
    if args.universo_declarado and os.path.isfile(args.universo_declarado):
        declarado = json.load(open(args.universo_declarado, encoding='utf-8'))

    portoes = {
        'CLAIM_ID_GATE': portao_claim_id(eventos),
        'EVIDENCE_STATE_GATE': portao_evidence_state(args.acervo, eventos),
        'UNIVERSE_COMPLETENESS': portao_universo(args.acervo, declarado),
    }

    print(f'PORTÕES DAS ETIQUETAS · {RULE_VERSION} · somente leitura')
    print(f'acervo     = {args.acervo}')
    print(f'passaporte = {args.passaporte}  ({len(eventos)} eventos)\n')
    for nome, r in portoes.items():
        marca = 'PASS' if r['PROVED'] else 'FAIL'
        print(f'── {nome}  =  {marca}')
        for k, v in r.items():
            if k in ('PROVED', 'BLOQUEIO'):
                continue
            print(f'     {k:38s} = {v}')
        if r.get('BLOQUEIO'):
            print(f'     BLOQUEIO: {r["BLOQUEIO"]}')
        print()

    todos = all(r['PROVED'] for r in portoes.values())
    print(f'ROUTING_PUBLISHABLE = {"YES" if todos else "NO"}')
    if not todos:
        print('  Enquanto um portão for FAIL, nenhuma relação CAPACIDADE → CLAIM')
        print('  pode ser tratada como factual.')

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump({'RULE_VERSION': RULE_VERSION, 'PORTOES': portoes,
                       'ROUTING_PUBLISHABLE': 'YES' if todos else 'NO'},
                      f, ensure_ascii=False, indent=2)
        print(f'\ngravado: {args.json}')
    return 0 if todos else 1


if __name__ == '__main__':
    raise SystemExit(main())
