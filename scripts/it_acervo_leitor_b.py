#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LEITOR B do `UNIVERSE_ACERVO_IT`.

    py -3 scripts/it_acervo_leitor_b.py [--raiz .] [--json saida.json]

Implementa `docs/UNIVERSO-ACERVO-IT-REGRA-CANONICA.md`. SOMENTE LEITURA.

E o par do LEITOR A e **nao partilha nada com ele**: nao o importa, nao copia
funcao nenhuma, e nao passa pelas mesmas primitivas. Onde o A usa `os.walk` e
predicados soltos, este constroi o conjunto de caminhos com `pathlib.Path.rglob`,
decide por uma TABELA de regras avaliadas em ordem, e conta a forma varrendo os
pares do documento com uma compreensao em vez de um laco.

Concordar aqui significa que a REGRA e reproduzivel. Concordar por partilhar
codigo nao significaria nada.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path, PurePosixPath

# ── constantes da especificacao ──────────────────────────────────────────────

SOB = 'data'
FORA = ('data/samples/IT-PORTAL-V1', 'data/runs')
REGISTO = 'data/samples/IT-PORTAL-V1/IT-ACERVO-CHAVES-V1.json'

K_RAIZ, K_VAZIO, K_UNICO = '__RAIZ__', '__VAZIO__', '__DOCUMENTO_UNICO__'
K_DA_REGRA = frozenset({K_RAIZ, K_VAZIO, K_UNICO})

# Mesma tabela do dono, aqui como pares ja compilados e percorridos por `next`.
TABELA_DE_FAMILIAS = tuple(
    (etiqueta, re.compile(padrao, re.IGNORECASE)) for etiqueta, padrao in (
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
    )
)

SEGMENTO_ITALIANO = re.compile(r'^IT$|^IT-|ITALIA|ITALY', re.IGNORECASE)
FATO_ITALIANO = re.compile(r'ITAL', re.IGNORECASE)
ROTULOS_DE_PAIS = frozenset({'IT', 'ITALY', 'ITALIA'})


# ── a tabela de decisao: cada regra devolve o motivo de recusa, ou None ──────

def _fora_de_data(rel: PurePosixPath, _doc) -> str | None:
    return None if rel.parts and rel.parts[0] == SOB else 'FORA_DE_DATA'


def _camada_excluida(rel: PurePosixPath, _doc) -> str | None:
    texto = rel.as_posix()
    return next((f'EXCLUIDO:{p}' for p in FORA if texto.startswith(p + '/')), None)


def _nao_italiano(rel: PurePosixPath, doc) -> str | None:
    if any(SEGMENTO_ITALIANO.search(s) for s in rel.parts[1:]):
        return None
    if isinstance(doc, dict):
        pais = str(doc.get('COUNTRY', doc.get('country', '')) or '').strip().upper()
        if pais in ROTULOS_DE_PAIS:
            return None
        if FATO_ITALIANO.search(str(doc.get('FACT_LOCATION') or '')):
            return None
    return 'NAO_ITALIANO'


REGRAS_DE_RECUSA = (_fora_de_data, _camada_excluida, _nao_italiano)


def motivo_de_recusa(rel: PurePosixPath, doc):
    """None = pertence. Caso contrario, a etiqueta da primeira regra que recusa."""
    return next((m for m in (regra(rel, doc) for regra in REGRAS_DE_RECUSA) if m), None)


def forma_do_documento(doc):
    """Seccao 2, escrita como mapa em vez de laco acumulador."""
    if isinstance(doc, list):
        return {K_RAIZ: len(doc)} if (doc and isinstance(doc[0], dict)) else {K_VAZIO: 0}
    if not isinstance(doc, dict):
        return {K_VAZIO: 0}
    achadas = {
        chave: len(valor) for chave, valor in doc.items()
        if isinstance(valor, list) and valor and isinstance(valor[0], dict)
    }
    return achadas or {K_UNICO: 1}


def etiqueta_de_familia(texto: str) -> str:
    return next((e for e, rx in TABELA_DE_FAMILIAS if rx.search(texto)), 'OUTROS')


def digital(raiz: Path, relativos):
    acumulador = hashlib.sha256()
    for rel in relativos:
        acumulador.update(rel.encode('utf-8'))
        acumulador.update(b'\n')
        bruto = (raiz / rel).read_bytes()
        acumulador.update(hashlib.sha256(bruto).hexdigest().encode('utf-8'))
        acumulador.update(b'\n')
    return acumulador.hexdigest()


def ler(raiz_txt: str):
    raiz = Path(raiz_txt).resolve()
    conhecidas = frozenset(json.loads((raiz / REGISTO).read_text(encoding='utf-8'))['CHAVES'])

    candidatos = sorted(
        (c for c in (raiz / SOB).rglob('*.json') if c.is_file()),
        key=lambda c: c.relative_to(raiz).as_posix(),
    )

    aceites, ilegiveis = OrderedDict(), []
    for caminho in candidatos:
        rel = PurePosixPath(caminho.relative_to(raiz).as_posix())
        try:
            doc = json.loads(caminho.read_text(encoding='utf-8'))
        except Exception as erro:                                # noqa: BLE001
            if _nao_italiano(rel, None) is None:
                ilegiveis.append({'FICHEIRO': rel.as_posix(), 'ERRO': type(erro).__name__})
            continue
        if motivo_de_recusa(rel, doc) is not None:
            continue
        aceites[rel.as_posix()] = forma_do_documento(doc)

    por_chave, por_familia = Counter(), Counter()
    desconhecidas = []
    for rel, forma in aceites.items():
        familia = etiqueta_de_familia(rel)
        for chave, quantos in forma.items():
            por_chave[chave] += quantos
            por_familia[familia] += quantos
            if chave not in K_DA_REGRA and chave not in conhecidas:
                desconhecidas.append({'CHAVE': chave, 'FICHEIRO': rel, 'REGISTOS': quantos})

    lista = list(aceites)
    return OrderedDict([
        ('LEITOR', 'B'),
        ('UNIVERSE', 'UNIVERSE_ACERVO_IT'),
        ('FILES', len(lista)),
        ('RECORDS', sum(por_chave.values())),
        ('COLLECTIONS', len(por_chave)),
        ('UNKNOWN_KEYS', len(desconhecidas)),
        ('FINGERPRINT', digital(raiz, lista)),
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
    print('== LEITOR B · UNIVERSE_ACERVO_IT ==')
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
        assert '/data/' not in a.json.replace('\\', '/'), 'leitor nao escreve em data/'
        Path(a.json).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
        print('\n   gravado: %s' % a.json)

    reprova = bool(r['UNKNOWN_COLLECTION_KEY']) or bool(r['ILEGIVEL']) \
        or not r['INVARIANT_FAMILY_SUM_OK'] or r['FILES'] == 0
    return 1 if reprova else 0


if __name__ == '__main__':
    raise SystemExit(main())
