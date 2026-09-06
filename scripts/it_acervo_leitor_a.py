#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LEITOR A do `UNIVERSE_ACERVO_IT`.

    py -3 scripts/it_acervo_leitor_a.py [--raiz .] [--json saida.json]

Implementa `docs/UNIVERSO-ACERVO-IT-REGRA-CANONICA.md`. SOMENTE LEITURA: nunca
escreve dentro de `data/`, e ha um teste que cai se ganhar uma escrita.

E o par do LEITOR B. Os dois nao partilham uma linha de classificacao — nem por
import, nem por copia de funcao. Este e escrito em estilo procedural: `os.walk`,
predicados nomeados, o caminho partido em segmentos a mao. O B e escrito por
`pathlib` e tabela de decisao. Se dois estilos diferentes chegam ao mesmo numero,
o numero e da REGRA; se chegassem por partilharem codigo, seria do CODIGO.

Saida com os nomes da seccao 9 da especificacao.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, OrderedDict

# ── constantes da especificacao (dados, nao logica) ──────────────────────────

PASTA_RAIZ = 'data'
CAMINHOS_EXCLUIDOS = ('data/samples/IT-PORTAL-V1/', 'data/runs/')
REGISTO_DE_CHAVES = 'data/samples/IT-PORTAL-V1/IT-ACERVO-CHAVES-V1.json'

CHAVE_RAIZ = '__RAIZ__'
CHAVE_VAZIO = '__VAZIO__'
CHAVE_DOC_UNICO = '__DOCUMENTO_UNICO__'
CHAVES_DA_REGRA = (CHAVE_RAIZ, CHAVE_VAZIO, CHAVE_DOC_UNICO)

# Tabela do dono, preservada. So ETIQUETA o registo; ja nao decide pertenca —
# quem decide pertenca e o teste de Italia da seccao 1.3.
FAMILIAS = [
    ('RADAR_FUTURO',      r'IT-FUTURO'),
    ('ROTULOS_PORTFOLIO', r'IT-ROTULOS|IT-VOCAB|IT-PAIRSET|productsRegulatory|productRelationships'),
    ('SINAIS_DE_CAMPO',   r'IT-CAMPO|CURRENT-FIELD|IT-CRUZAMENTO'),
    ('FITOSSANITARIO',    r'IT-CONVEGNO|IT-VIDEO|IT-VOZ-AUDIO|falas/|testemunhas/'),
    ('FONTES',            r'IT-FONTES'),
    ('CONCORRENCIA',      r'COMPETITOR|CONCORREN'),
    ('SOCIAL_INSTAGRAM',  r'IT-INSTAGRAM'),
    ('SENSORES_HUMANOS',  r'SENSOR-PILOT|EARLY_SIGNAL|RESEARCHER|SPEAKER'),
    ('GEOGRAFIA',         r'TERRITORIAL|nuts2|GEOGRAF'),
    ('MERCADO',           r'MARKET|PRICES|ECONOMIC'),
    ('OPORTUNIDADES',     r'IT-RADAR-V21|OPPORTUNIT|IT-SNAPSHOT'),
    ('HANDOFF_METODO',    r'IT-HANDOFF|RUN-MANIFEST|DATA-CLOCK|POLITICA|AUDITORIA|ROTAS-EXTERNAS'),
    ('IT-PORTAL',         r'IT-PORTAL'),
]

PAISES_ITALIA = ('IT', 'ITALY', 'ITALIA')


# ── predicados, um por linha da especificacao ────────────────────────────────

def normaliza(caminho_absoluto, raiz):
    """Seccao 8: toda comparacao acontece sobre o caminho com `/`."""
    return os.path.relpath(caminho_absoluto, raiz).replace(os.sep, '/')


def esta_sob_data(rel):
    return rel == PASTA_RAIZ or rel.startswith(PASTA_RAIZ + '/')


def e_json(nome):
    return nome.endswith('.json')


def esta_excluido(rel):
    for prefixo in CAMINHOS_EXCLUIDOS:
        if rel.startswith(prefixo):
            return True
    return False


def italia_pelo_caminho(rel):
    """Seccao 1.3, teste PATH: um segmento depois de `data/` declara a Italia."""
    segmentos = rel.split('/')[1:]
    for s in segmentos:
        alto = s.upper()
        if alto == 'IT' or alto.startswith('IT-'):
            return True
        if 'ITALIA' in alto or 'ITALY' in alto:
            return True
    return False


def italia_pelo_documento(doc):
    """Seccao 1.3, testes COUNTRY e FACT_LOCATION. SOURCE_LOCATION nao entra."""
    if not isinstance(doc, dict):
        return False
    pais = doc.get('COUNTRY')
    if pais is None:
        pais = doc.get('country')
    if str(pais or '').strip().upper() in PAISES_ITALIA:
        return True
    if re.search(r'ITAL', str(doc.get('FACT_LOCATION') or ''), re.IGNORECASE):
        return True
    return False


def familia_de(rel):
    for nome, padrao in FAMILIAS:
        if re.search(padrao, rel, re.IGNORECASE):
            return nome
    return 'OUTROS'


def coleccoes_de(doc):
    """Seccao 2. Devolve [(chave, registos)]."""
    if isinstance(doc, list):
        if doc and isinstance(doc[0], dict):
            return [(CHAVE_RAIZ, len(doc))]
        return [(CHAVE_VAZIO, 0)]
    if not isinstance(doc, dict):
        return [(CHAVE_VAZIO, 0)]
    achadas = []
    for chave in doc:
        valor = doc[chave]
        if isinstance(valor, list) and len(valor) > 0 and isinstance(valor[0], dict):
            achadas.append((chave, len(valor)))
    if achadas:
        return achadas
    return [(CHAVE_DOC_UNICO, 1)]


# ── a corrida ────────────────────────────────────────────────────────────────

def ler(raiz):
    raiz = os.path.abspath(raiz)
    registo_p = os.path.join(raiz, REGISTO_DE_CHAVES.replace('/', os.sep))
    with open(registo_p, encoding='utf-8') as f:
        conhecidas = set(json.load(f)['CHAVES'])

    incluidos = []           # (rel, [(chave, n)], familia)
    ilegiveis = []
    for pasta, _, nomes in os.walk(os.path.join(raiz, PASTA_RAIZ)):
        for nome in sorted(nomes):
            if not e_json(nome):
                continue
            absoluto = os.path.join(pasta, nome)
            rel = normaliza(absoluto, raiz)
            if not esta_sob_data(rel):
                continue
            if esta_excluido(rel):
                continue
            try:
                with open(absoluto, encoding='utf-8') as f:
                    doc = json.load(f)
            except Exception as erro:                          # noqa: BLE001
                # Seccao 1.2: um .json que nao abre REPROVA a corrida.
                if italia_pelo_caminho(rel):
                    ilegiveis.append({'FICHEIRO': rel, 'ERRO': type(erro).__name__})
                continue
            if not (italia_pelo_caminho(rel) or italia_pelo_documento(doc)):
                continue
            incluidos.append((rel, coleccoes_de(doc), familia_de(rel)))

    incluidos.sort(key=lambda t: t[0])

    por_chave, por_familia = Counter(), Counter()
    desconhecidas = []
    for rel, cols, fam in incluidos:
        for chave, n in cols:
            por_chave[chave] += n
            por_familia[fam] += n
            if chave not in CHAVES_DA_REGRA and chave not in conhecidas:
                desconhecidas.append({'CHAVE': chave, 'FICHEIRO': rel, 'REGISTOS': n})

    lista = [rel for rel, _, _ in incluidos]

    # Seccao 7: digital sobre o conjunto E sobre o conteudo.
    h = hashlib.sha256()
    for rel in lista:
        h.update(rel.encode('utf-8'))
        h.update(b'\n')
        with open(os.path.join(raiz, rel.replace('/', os.sep)), 'rb') as f:
            h.update(hashlib.sha256(f.read()).hexdigest().encode('utf-8'))
        h.update(b'\n')

    return OrderedDict([
        ('LEITOR', 'A'),
        ('UNIVERSE', 'UNIVERSE_ACERVO_IT'),
        ('FILES', len(lista)),
        ('RECORDS', sum(por_chave.values())),
        ('COLLECTIONS', len(por_chave)),
        ('UNKNOWN_KEYS', len(desconhecidas)),
        ('FINGERPRINT', h.hexdigest()),
        ('INVARIANT_FAMILY_SUM_OK', sum(por_familia.values()) == sum(por_chave.values())),
        ('FILE_LIST', lista),
        ('PER_KEY', OrderedDict(sorted(por_chave.items()))),
        ('PER_FAMILY', OrderedDict(sorted(por_familia.items()))),
        ('UNKNOWN_COLLECTION_KEY', desconhecidas),
        ('ILEGIVEL', ilegiveis),
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raiz', default='.')
    ap.add_argument('--json', default=None)
    a = ap.parse_args()

    r = ler(a.raiz)
    print('== LEITOR A · UNIVERSE_ACERVO_IT ==')
    for k in ('FILES', 'RECORDS', 'COLLECTIONS', 'UNKNOWN_KEYS', 'FINGERPRINT'):
        print('   %-14s %s' % (k, r[k]))
    print('   %-14s %s' % ('INVARIANTE', r['INVARIANT_FAMILY_SUM_OK']))
    if r['UNKNOWN_COLLECTION_KEY']:
        print('\n   UNKNOWN_COLLECTION_KEY (%d):' % len(r['UNKNOWN_COLLECTION_KEY']))
        for u in r['UNKNOWN_COLLECTION_KEY'][:8]:
            print('    · %s em %s (%d)' % (u['CHAVE'], u['FICHEIRO'], u['REGISTOS']))
    if r['ILEGIVEL']:
        print('\n   ILEGIVEL (%d):' % len(r['ILEGIVEL']))
        for i in r['ILEGIVEL'][:8]:
            print('    · %s (%s)' % (i['FICHEIRO'], i['ERRO']))

    if a.json:
        assert '/data/' not in a.json.replace(os.sep, '/'), 'leitor nao escreve em data/'
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
        print('\n   gravado: %s' % a.json)

    reprova = bool(r['UNKNOWN_COLLECTION_KEY']) or bool(r['ILEGIVEL']) \
        or not r['INVARIANT_FAMILY_SUM_OK'] or r['FILES'] == 0
    return 1 if reprova else 0


if __name__ == '__main__':
    raise SystemExit(main())
