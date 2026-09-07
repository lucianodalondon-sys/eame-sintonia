#!/usr/bin/env python3
"""
SAÚDE DE FONTE e ESTADO DE VERSÃO — os estados que não podem virar o mesmo resultado.

Duas máquinas de estado pequenas, e nenhuma tela.

## 1 · SAÚDE DA FONTE

    HEALTHY    a fonte respondeu, o tipo bate, o schema mínimo está presente,
               a chave de identidade existe e é única, e há conteúdo.
    DEGRADED   respondeu e é usável, mas algo do contrato mudou: campo novo,
               campo ausente que não é chave, volume fora da faixa esperada.
    FAILED     não respondeu, respondeu outra coisa, ou respondeu vazio.
    UNKNOWN    não foi verificada nesta execução. NÃO é sinônimo de saudável.

**HTTP 200 não basta para HEALTHY.** O caso que motiva a regra é o `200` com página
de erro: o servidor responde, o status é bom, o conteúdo é lixo. Por isso a checagem
é de schema e de identidade, não de status.

## 2 · ESTADO DE VERSÃO

    BASELINE_ESTABLISHED    é a primeira versão. **Nunca `NO_CHANGE`** — sem duas
                            versões não existe ausência de mudança, existe ausência
                            de comparação.
    NO_NEW_VERSION          a fonte não publicou versão nova desde a última coleta.
    NEW_VERSION_IDENTICAL   publicou, e o conteúdo é byte a byte igual.
    NEW_VERSION_CHANGED     publicou e mudou — só aqui roda o detector de eventos.
    SOURCE_FAILED           não deu para saber. **Não é `NO_NEW_VERSION`.**

O erro que estes cinco estados existem para impedir: uma fonte que caiu produzir a
mesma saída de uma fonte que não mudou, e o radar dizer "nada mudou" quando o que
houve foi "não consegui olhar".
"""
import hashlib
import json
import os

HEALTHY, DEGRADED, FAILED, UNKNOWN = 'HEALTHY', 'DEGRADED', 'FAILED', 'UNKNOWN'
BASELINE_ESTABLISHED = 'BASELINE_ESTABLISHED'
NO_NEW_VERSION = 'NO_NEW_VERSION'
NEW_VERSION_IDENTICAL = 'NEW_VERSION_IDENTICAL'
NEW_VERSION_CHANGED = 'NEW_VERSION_CHANGED'
SOURCE_FAILED = 'SOURCE_FAILED'


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def check(payload, *, required_fields, identity_key,
          content_type=None, expected_type=None, min_rows=1, expect_rows=None,
          tolerance=0.10):
    """
    Avalia uma coleta contra o contrato declarado da fonte.

    payload          lista de dicts (linhas) já decodificada, ou None se a coleta falhou
    required_fields  campos sem os quais a fonte não serve para o que dependemos dela
    identity_key     campo que identifica a linha — tem de existir e ser único
    expect_rows      volume esperado; fora de ±tolerance vira DEGRADED (nunca HEALTHY)

    Devolve (estado, dict com os motivos). Nunca levanta: quem decide o que fazer com
    FAILED é o chamador, e a decisão tem de ser explícita.
    """
    notes = {'checks': [], 'missing_fields': [], 'extra_fields': [],
             'duplicate_identity': 0, 'rows': None}

    if payload is None:
        notes['checks'].append('sem payload — coleta falhou ou não foi tentada')
        return FAILED, notes
    if expected_type and content_type and expected_type not in (content_type or ''):
        notes['checks'].append(f'content-type {content_type!r} não é {expected_type!r} '
                               '— 200 com corpo errado é FAILED, não DEGRADED')
        return FAILED, notes
    if not isinstance(payload, list):
        notes['checks'].append(f'payload é {type(payload).__name__}, não lista de linhas')
        return FAILED, notes

    notes['rows'] = len(payload)
    if len(payload) < min_rows:
        notes['checks'].append(f'{len(payload)} linhas < mínimo {min_rows} — '
                               'lista vazia é FAILED, nunca "zero resultados"')
        return FAILED, notes

    first = payload[0] if isinstance(payload[0], dict) else {}
    present = set(first)
    notes['missing_fields'] = sorted(set(required_fields) - present)
    if identity_key not in present:
        notes['checks'].append(f'chave de identidade {identity_key!r} ausente')
        return FAILED, notes
    if notes['missing_fields']:
        notes['checks'].append('campos obrigatórios ausentes')
        return FAILED, notes

    ids = [r.get(identity_key) for r in payload if isinstance(r, dict)]
    if any(i in (None, '') for i in ids):
        notes['checks'].append('identidade vazia em alguma linha')
        return FAILED, notes
    notes['duplicate_identity'] = len(ids) - len(set(ids))

    state = HEALTHY
    if notes['duplicate_identity']:
        notes['checks'].append(f'{notes["duplicate_identity"]} identidades duplicadas')
        state = DEGRADED
    extra = sorted(present - set(required_fields))
    if extra:
        notes['extra_fields'] = extra
        notes['checks'].append('campos novos em relação ao contrato — usável, mas o '
                               'contrato mudou')
        state = DEGRADED
    if expect_rows:
        low, high = expect_rows * (1 - tolerance), expect_rows * (1 + tolerance)
        if not low <= len(payload) <= high:
            notes['checks'].append(f'{len(payload)} linhas fora de {expect_rows}±'
                                   f'{tolerance:.0%}')
            state = DEGRADED
    return state, notes


def version_state(*, fetch_ok, current_hash, previous_hash,
                  current_version=None, previous_version=None):
    """
    Os cinco estados. A ordem das perguntas é a regra:
      1. consegui olhar?            não → SOURCE_FAILED
      2. tenho versão anterior?     não → BASELINE_ESTABLISHED
      3. a fonte publicou de novo?  não → NO_NEW_VERSION
      4. mudou?                     não → NEW_VERSION_IDENTICAL  senão → NEW_VERSION_CHANGED
    """
    if not fetch_ok or current_hash is None:
        return SOURCE_FAILED
    if previous_hash is None:
        return BASELINE_ESTABLISHED
    if current_version is not None and previous_version is not None \
            and current_version == previous_version:
        return NO_NEW_VERSION
    if current_hash == previous_hash:
        return NEW_VERSION_IDENTICAL
    return NEW_VERSION_CHANGED


def can_diff(state):
    """Só um estado autoriza emitir CHANGE EVENT."""
    return state == NEW_VERSION_CHANGED


if __name__ == '__main__':
    import sys
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    man = os.path.join(root, 'data', 'samples', 'DATA-CLOCK-manifest.json')
    with open(man, encoding='utf-8') as f:
        rows = json.load(f)
    rows = rows.get('files', rows) if isinstance(rows, dict) else rows
    print(json.dumps(rows, ensure_ascii=False)[:200] if '--dump' in sys.argv else
          f'{len(rows)} arquivos no manifesto do data clock')
