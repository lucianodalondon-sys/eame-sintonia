#!/usr/bin/env python3
"""
Contrato de leitura da lista de DENOMINACIONES COMUNES do MAPA (`dc_web.pdf`).

Por que existe: a MISSÃO 06 publicou "1.737 / 708 / 2,45" sem dizer **o que cada
número conta**. Sem contrato de coluna, 2,45 vira "o mercado infla 2,45x", que é
uma frase maior do que o dado. Este script declara o contrato e o mede.

O PDF não tem separadores de campo. As colunas são:

    Nº Registro | Producto de Referencia | Empresa Concesionaria |
    Denominación común | Fecha Aceptación | Notas

REGRA DE CORTE DECLARADA
  1. as Notas têm forma fixa (`P V/D: <data>`, `P U/A/E: <data>`) e são removidas
     ANTES de qualquer corte, senão a data da nota seria lida como fim de linha;
  2. cada linha termina na sua *Fecha Aceptación* (`dd/mm/aaaa`);
  3. cada linha começa no seu Nº Registro (`ES-01717` ou `25854`).

O QUE ESTE PARSER **NÃO** FAZ: separar `Producto de Referencia` de
`Empresa Concesionaria` de `Denominación común`. Não há separador; qualquer corte
aí seria invenção. Por isso as três colunas ficam num único campo `middle_raw` e
NÃO são publicadas como campos distintos.

Uso:
    python3 scripts/denominaciones.py <dc_web.pdf> [--json saida.json]
"""
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_text import text                                     # noqa: E402

HEADER = re.compile(
    r'Nº RegistroProducto de ReferenciaEmpresa ConcesionariaDenominación común'
    r'\((\d{2}/\d{2}/\d{4})\)Fecha AceptaciónNotas')
NOTE = re.compile(r'P\s*[VU]/[DA](?:/E)?:\s*\d{2}/\d{2}/\d{2,4}')
DATE = re.compile(r'\d{2}/\d{2}/\d{4}')
REGID = re.compile(r'^(ES-\d{4,5}|\d{4,6})')


def read(path):
    """Devolve (data_da_versão, linhas). Cada linha: dict com registro e resto bruto."""
    raw = ''.join(''.join(p) for p in text(path))
    raw = re.sub(r'[\x00-\x1f]', '', raw)

    version = None
    m = HEADER.search(raw)
    if m:
        version = m.group(1)
    raw = HEADER.sub('\n', raw)
    raw = NOTE.sub(' ', raw)

    rows, unparsed, pos = [], [], 0
    for d in DATE.finditer(raw):
        chunk = raw[pos:d.start()].strip()
        pos = d.end()
        rid = REGID.match(chunk)
        if not rid:
            unparsed.append(chunk[:60])
            continue
        rows.append({
            'registration': rid.group(1),
            'middle_raw': chunk[rid.end():],
            'accepted': d.group(0),
        })
    return version, rows, unparsed


def measure(rows):
    per = Counter(r['registration'] for r in rows)
    multi = {k: v for k, v in per.items() if v > 1}
    return {
        'DENOMINATION_ROWS': len(rows),
        'DISTINCT_REGISTRATIONS_IN_THIS_DOCUMENT': len(per),
        'REGISTRATIONS_WITH_MORE_THAN_ONE_ROW': len(multi),
        'SHARE_OF_LISTED_REGISTRATIONS_WITH_MORE_THAN_ONE_ROW':
            round(len(multi) / len(per), 4) if per else None,
        'MEAN_ROWS_PER_LISTED_REGISTRATION':
            round(len(rows) / len(per), 4) if per else None,
        'MAX_ROWS_ON_ONE_REGISTRATION': max(per.values()) if per else None,
        'REGISTRATION_WITH_MAX': per.most_common(1)[0][0] if per else None,
    }


if __name__ == '__main__':
    path = sys.argv[1]
    version, rows, unparsed = read(path)
    out = {
        'source_file': os.path.basename(path),
        'document_version_date': version,
        'contract': {
            'DENOMINATION_ROWS': 'uma linha da tabela = uma denominación común '
                                 'concedida a uma empresa concessionária sobre um '
                                 'registro de referência',
            'DISTINCT_REGISTRATIONS_IN_THIS_DOCUMENT':
                'registros de referência que aparecem NESTE documento — ou seja, '
                'que têm PELO MENOS UMA denominación común. NÃO é o total de '
                'registros do ROPF.',
            'not_measured': ['Producto de Referencia', 'Empresa Concesionaria',
                             'Denominación común'],
        },
        'unparsed_chunks': len(unparsed),
        'unparsed_sample': unparsed[:5],
    }
    out.update(measure(rows))
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if '--json' in sys.argv:
        dest = sys.argv[sys.argv.index('--json') + 1]
        with open(dest, 'w', encoding='utf-8') as f:
            json.dump({'measure': out, 'rows': rows}, f, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------------------
# SEPARAÇÃO DE COLUNAS — só com âncora externa, nunca por heurística de forma
# jurídica. Tentamos a heurística ("corta na primeira S.A./S.L./AG") e ela
# produziu "INDUSTRIAS A" + "FRASA, S.A." e "ECOLOGIA Y PROTECCION AG" +
# "RICOLA": erro silencioso, plausível na tela e falso. Foi descartada.
#
# A regra que ficou usa duas âncoras que vêm de FORA do PDF:
#   1. `Producto de Referencia` — o nome oficial do registro, lido no export
#      JSON do próprio ROPF (`Exportaciones/ExportJsonProductos`);
#   2. `Empresa Concesionaria` — casada contra o vocabulário de titulares do
#      ROPF, escolhendo a entrada MAIS LONGA que prefixa o resto.
# O que não casa fica `UNRESOLVED`. Não se adivinha.
# ---------------------------------------------------------------------------
import unicodedata                                            # noqa: E402


def fold(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^A-Z0-9]', '', s.upper())


def _eat(text, folded_len):
    """Consome de `text` os caracteres que correspondem a `folded_len` letras úteis."""
    k = c = 0
    while k < len(text) and c < folded_len:
        if fold(text[k]):
            c += 1
        k += 1
    while k < len(text) and text[k] in '.,;: ':          # pontuação final da razão social
        k += 1
    return text[:k], text[k:]


def split_rows(rows, register):
    """
    rows: saída de read(); register: {NumRegistro: registro do ROPF}.
    Devolve (resolvidas, não_resolvidas).
    """
    vocab = sorted({fold(r['Titular']) for r in register.values() if r.get('Titular')} - {''},
                   key=len, reverse=True)
    done, unresolved = [], []
    for r in rows:
        reg = register.get(r['registration'])
        mid = r['middle_raw']
        name = fold(reg['Nombre']) if reg and reg.get('Nombre') else ''
        if not name or not fold(mid).startswith(name):
            unresolved.append(dict(r, reason='REFERENCE_PRODUCT_NOT_MATCHED'))
            continue
        ref, rest = _eat(mid, len(name))
        frest = fold(rest)
        hit = next((v for v in vocab if frest.startswith(v)), None)
        if hit is None:
            unresolved.append(dict(r, reason='CONCESSIONAIRE_NOT_IN_REGISTER_VOCABULARY'))
            continue
        comp, brand = _eat(rest, len(hit))
        done.append({
            'REGISTRATION_ID': r['registration'],
            'REFERENCE_PRODUCT': ref.strip(' .,'),
            'CONCESSIONAIRE': comp.strip(' .,'),
            'COMMON_DENOMINATION': brand.strip(' .,'),
            'ACCEPTED': r['accepted'],
        })
    return done, unresolved
