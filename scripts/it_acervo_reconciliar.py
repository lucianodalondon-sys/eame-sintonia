#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POR QUE TRES LEITORES DO MESMO UNIVERSO DAO TRES NUMEROS.

    py -3 scripts/it_acervo_reconciliar.py --raiz . [--raiz2 ../outro-checkout]

SOMENTE LEITURA. Este ficheiro nao escreve dentro de `data/`. Ele reimplementa
as tres definicoes lado a lado sobre a MESMA arvore e devolve o diff de
pertenca, ficheiro a ficheiro.

    A  inventario publicado   IT-ACERVO-INVENTARIO-V2.json
    B  script do dono         it_acervo_inventario_v2.py   (replay, sem gravar)
    C  leitor independente    passaporte_universos.py      (replay)

A NAO tem lista de ficheiros: o artefacto publicado guarda totais e chaves, e
nunca guardou QUAIS ficheiros contou. Por isso A entra no diff pelas CHAVES e
pelos totais, nunca por ficheiro — dizer o contrario seria inventar a lista.

B e replicado DUAS vezes de proposito:
    B_NATIVO  com o separador de caminho da plataforma, como o script corre hoje
    B_POSIX   com o caminho normalizado para `/`, como corria em Linux
A diferenca entre os dois nao e cosmetica: as regras de B sao expressas em
regex com `/` literal, e um separador `\\` faz a regra deixar de casar.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter

# ── as regras de B, copiadas do dono sem alterar uma letra ───────────────────

FAMILIAS_B = [
    ('RADAR_FUTURO',        r'IT-FUTURO'),
    ('ROTULOS_PORTFOLIO',   r'IT-ROTULOS|IT-VOCAB|IT-PAIRSET|productsRegulatory|productRelationships'),
    ('SINAIS_DE_CAMPO',     r'IT-CAMPO|CURRENT-FIELD|IT-CRUZAMENTO'),
    ('FITOSSANITARIO',      r'IT-CONVEGNO|IT-VIDEO|IT-VOZ-AUDIO|falas/|testemunhas/'),
    ('FONTES',              r'IT-FONTES'),
    ('CONCORRENCIA',        r'COMPETITOR|CONCORREN'),
    ('SOCIAL_INSTAGRAM',    r'IT-INSTAGRAM'),
    ('SENSORES_HUMANOS',    r'SENSOR-PILOT|EARLY_SIGNAL|RESEARCHER|SPEAKER'),
    ('GEOGRAFIA',           r'TERRITORIAL|nuts2|GEOGRAF'),
    ('MERCADO',             r'MARKET|PRICES|ECONOMIC'),
    ('OPORTUNIDADES',       r'IT-RADAR-V21|OPPORTUNIT|IT-SNAPSHOT'),
    ('HANDOFF_METODO',      r'IT-HANDOFF|RUN-MANIFEST|DATA-CLOCK|POLITICA|AUDITORIA|ROTAS-EXTERNAS'),
    ('IT-PORTAL',           r'IT-PORTAL'),
]

AS_MINHAS_PROPRIAS_SAIDAS = (
    'IT-ACERVO-INVENTARIO-V2.json',
    'IT-ACERVO-CHAVES-V1.json',
    'IT-FAMILIA-SUPERFICIE-VERIFICACAO-V1.json',
)
CAMADA_DE_METODO = ('IT-PORTAL-V1',)


def familia_b(c):
    for nome, rx in FAMILIAS_B:
        if re.search(rx, c, re.I):
            return nome
    return 'OUTROS'


def e_italiano_b(caminho, doc):
    """Devolve (bool, motivo) — o motivo e o que torna o diff legivel."""
    if re.search(r'(^|/)IT-|italia|italy', caminho, re.I):
        return True, 'PATH'
    if isinstance(doc, dict):
        c = str(doc.get('COUNTRY') or doc.get('country') or '')
        if c.upper() in ('IT', 'ITALY', 'ITALIA'):
            return True, 'DOC_COUNTRY'
        if 'ITALY' in str(doc.get('SOURCE_LOCATION') or '').upper():
            return True, 'DOC_SOURCE_LOCATION'
    return False, 'NAO_ITALIANO'


def coleccoes_b(doc):
    if isinstance(doc, list):
        return [('(raiz e lista)', len(doc))] if doc else []
    if not isinstance(doc, dict):
        return []
    cols = [(k, len(v)) for k, v in doc.items()
            if isinstance(v, list) and v and isinstance(v[0], dict)]
    return cols or [('(documento unico)', 1)]


def varre_b(root, posix):
    """Replay de B. `posix=True` normaliza o separador; False usa o da plataforma."""
    out = {}
    for base, _, nomes in os.walk(os.path.join(root, 'data')):
        for n in sorted(nomes):
            if not n.endswith('.json') or n in AS_MINHAS_PROPRIAS_SAIDAS:
                continue
            base_cmp = (base.replace('\\', '/') if posix else base) + '/'
            if any(('/%s/' % d) in base_cmp for d in CAMADA_DE_METODO):
                continue
            p = os.path.join(base, n)
            try:
                d = json.load(open(p, encoding='utf-8'))
            except Exception:
                continue
            rel_raw = os.path.relpath(p, root)
            rel_cmp = rel_raw.replace('\\', '/') if posix else rel_raw
            ok, motivo = e_italiano_b(rel_cmp, d)
            if not ok:
                continue
            chave = rel_raw.replace('\\', '/')
            out[chave] = {
                'cols': coleccoes_b(d),
                'familia': familia_b(rel_cmp),
                'motivo': motivo,
            }
    return out


# ── as regras de C, copiadas do leitor independente sem alterar uma letra ────

FAMILIAS_C = FAMILIAS_B  # a mesma tabela, menos a familia OUTROS


def familia_c(rel):
    for nome, rx in FAMILIAS_C:
        if re.search(rx, rel, re.IGNORECASE):
            return nome
    return None                      # <- C EXIGE familia; B cai em OUTROS


def registros_c(caminho):
    try:
        d = json.load(open(caminho, encoding='utf-8'))
    except Exception:
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
    return n, chaves                 # <- sem fallback `(documento unico)`


def varre_c(root):
    base = os.path.join(root, 'data', 'samples')
    out = {}
    for pasta, _, nomes in os.walk(base):
        for nome in sorted(nomes):
            if not nome.endswith('.json'):
                continue
            c = os.path.join(pasta, nome)
            rel = os.path.relpath(c, base).replace('\\', '/')
            fam = familia_c(rel)
            if not fam:
                continue
            n, chaves = registros_c(c)
            if not n:
                continue             # <- ficheiro sem lista some do universo
            out['data/samples/' + rel] = {
                'n': n, 'chaves': chaves, 'familia': fam,
            }
    return out


# ── medicao ──────────────────────────────────────────────────────────────────

def medir_b(vb, conhecidas):
    reg = Counter()
    desconhecidas = []
    for rel, info in vb.items():
        for k, n in info['cols']:
            reg[k] += n
            if k not in conhecidas:
                desconhecidas.append({'CHAVE': k, 'FICHEIRO': rel, 'REGISTOS': n})
    return {
        'FILES': len(vb),
        'RECORDS': sum(reg.values()),
        'COLLECTIONS': len(reg),
        'UNKNOWN': len(desconhecidas),
        'unknown_list': desconhecidas,
        'por_chave': reg,
    }


def medir_c(vc, conhecidas):
    reg = Counter()
    desconhecidas = []
    for rel, info in vc.items():
        for k in info['chaves']:
            reg[k] += 1
            if k not in conhecidas:
                desconhecidas.append({'CHAVE': k, 'FICHEIRO': rel})
    return {
        'FILES': len(vc),
        'RECORDS': sum(i['n'] for i in vc.values()),
        'COLLECTIONS': len(reg),
        'UNKNOWN': len(desconhecidas),
        'unknown_list': desconhecidas,
        'por_chave': reg,
    }


MOTIVO_C_FORA = {}


def porque_c_recusa(root, rel):
    """C recusa por um de tres motivos, e o diff precisa de saber qual."""
    if not rel.startswith('data/samples/'):
        return 'FORA_DE_data_samples'
    sub = rel[len('data/samples/'):]
    if familia_c(sub) is None:
        return 'SEM_FAMILIA'
    n, _ = registros_c(os.path.join(root, rel))
    if not n:
        return 'ZERO_REGISTOS_DESCARTA_FICHEIRO'
    return '?'


def diff_de_pertenca(root, b_nat, b_pos, c):
    todos = sorted(set(b_nat) | set(b_pos) | set(c))
    linhas = []
    for rel in todos:
        em_a = rel in b_pos          # A = a regra de B com o caminho POSIX
        em_b = rel in b_nat
        em_c = rel in c
        if em_a:
            ra = 'INCLUI · %s · familia=%s' % (b_pos[rel]['motivo'], b_pos[rel]['familia'])
        else:
            ra = 'FORA · nao italiano pela regra de caminho POSIX'
        if em_b:
            rb = 'INCLUI · %s · familia=%s' % (b_nat[rel]['motivo'], b_nat[rel]['familia'])
        else:
            rb = 'FORA · separador \\ quebra (^|/)IT-  ou camada nao excluida'
        rc = ('INCLUI · familia=%s · %d registos' % (c[rel]['familia'], c[rel]['n'])
              if em_c else 'FORA · ' + porque_c_recusa(root, rel))
        linhas.append({'FILE': rel, 'A': em_a, 'B': em_b, 'C': em_c,
                       'REASON_A': ra, 'REASON_B': rb, 'REASON_C': rc})

    baldes = {k: [] for k in ('ALL_AGREE', 'A_ONLY', 'B_ONLY', 'C_ONLY',
                              'A_B_ONLY', 'A_C_ONLY', 'B_C_ONLY')}
    for l in linhas:
        t = (l['A'], l['B'], l['C'])
        baldes[{(1, 1, 1): 'ALL_AGREE', (1, 0, 0): 'A_ONLY', (0, 1, 0): 'B_ONLY',
                (0, 0, 1): 'C_ONLY', (1, 1, 0): 'A_B_ONLY', (1, 0, 1): 'A_C_ONLY',
                (0, 1, 1): 'B_C_ONLY'}[tuple(int(x) for x in t)]].append(l['FILE'])
    return linhas, baldes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raiz', default='.')
    ap.add_argument('--raiz2', default=None, help='segundo checkout, para provar deriva de arvore')
    ap.add_argument('--json', default=None, help='onde gravar o relatorio (nunca dentro de data/)')
    ap.add_argument('--diff', action='store_true', help='diff de pertenca ficheiro a ficheiro')
    a = ap.parse_args()

    raizes = [('RAIZ1', os.path.abspath(a.raiz))]
    if a.raiz2:
        raizes.append(('RAIZ2', os.path.abspath(a.raiz2)))

    relatorio = {}
    for etiqueta, root in raizes:
        decl_p = os.path.join(root, 'data/samples/IT-PORTAL-V1/IT-ACERVO-INVENTARIO-V2.json')
        reg_p = os.path.join(root, 'data/samples/IT-PORTAL-V1/IT-ACERVO-CHAVES-V1.json')
        decl = json.load(open(decl_p, encoding='utf-8'))
        conhecidas = set(json.load(open(reg_p, encoding='utf-8'))['CHAVES'])

        b_nat = varre_b(root, posix=False)
        b_pos = varre_b(root, posix=True)
        c = varre_c(root)

        r = {
            'ROOT': root,
            'A_PUBLICADO': {
                'FILES': decl['FICHEIROS'],
                'RECORDS': decl['TOTAL_REAL_ACERVO'],
                'COLLECTIONS': decl['CHAVES_DE_COLECAO_ENCONTRADAS'],
                'UNKNOWN': decl['CHAVES_NAO_RECONHECIDAS'],
                'CAPTURED_AT': decl['CAPTURED_AT'],
            },
            'B_NATIVO': medir_b(b_nat, conhecidas),
            'B_POSIX': medir_b(b_pos, conhecidas),
            'C': medir_c(c, conhecidas),
            '_files': {'B_NATIVO': b_nat, 'B_POSIX': b_pos, 'C': c},
            '_decl_por_chave': decl['POR_CHAVE'],
        }
        relatorio[etiqueta] = r

        print('== %s  %s' % (etiqueta, root))
        for nome in ('A_PUBLICADO', 'B_NATIVO', 'B_POSIX', 'C'):
            m = r[nome]
            print('   %-12s files=%-5s records=%-7s colecoes=%-4s desconhecidas=%s'
                  % (nome, m['FILES'], m['RECORDS'], m['COLLECTIONS'], m['UNKNOWN']))
        print()

        if a.diff:
            linhas, baldes = diff_de_pertenca(root, b_nat, b_pos, c)
            r['_diff'] = linhas
            r['_baldes'] = baldes
            print('   -- DIFF DE PERTENCA (%d ficheiros vistos por alguem) --' % len(linhas))
            for k in ('ALL_AGREE', 'A_B_ONLY', 'A_C_ONLY', 'B_C_ONLY',
                      'A_ONLY', 'B_ONLY', 'C_ONLY'):
                print('      %-10s %4d' % (k, len(baldes[k])))
            for k in ('A_ONLY', 'C_ONLY', 'A_C_ONLY', 'B_ONLY', 'B_C_ONLY'):
                if baldes[k]:
                    print('      %s (ate 4):' % k)
                    for f in baldes[k][:4]:
                        print('        · %s' % f)
            print()

    if a.json:
        assert '/data/' not in a.json.replace('\\', '/'), 'nao gravar dentro de data/'
        limpo = {}
        for k, v in relatorio.items():
            limpo[k] = {kk: vv for kk, vv in v.items() if not kk.startswith('_')}
            limpo[k]['_files'] = {n: sorted(v['_files'][n]) for n in v['_files']}
            for n in ('B_NATIVO', 'B_POSIX', 'C'):
                limpo[k][n] = {kk: vv for kk, vv in v[n].items() if kk != 'por_chave'}
        json.dump(limpo, open(a.json, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('relatorio: %s' % a.json)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
