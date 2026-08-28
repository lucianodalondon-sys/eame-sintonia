#!/usr/bin/env python3
"""
Normalizador de substância ativa — FASE 2 da MISSÃO EAME 03 (cruzamento X-006).

O problema, medido antes de escrever uma linha de código:

  · o registro francês usa **1.225 grafias distintas** nos produtos, e **736 delas
    não batem** com a própria tabela oficial francesa de substâncias;
  · a França escreve em francês ("mancozèbe", "zinèbe", "carbendazime", "folpel"),
    a Itália escreve em inglês maiúsculo ("MANCOZEB", "COPPER OXYCHLORIDE");
  · 560 usos citam "glyphosate sel d'isopropylamine" — um **sal**, não a molécula-mãe;
  · só **624 das 1.338** substâncias francesas trazem número CAS.

Sem uma chave normalizada, o cruzamento UE → produto nacional (X-006) fica preso ao
CAS, que cobre menos da metade do universo.

Métodos, em ordem de confiança — e cada um é registrado no resultado:

  CAS            número CAS idêntico                          confiança ALTA
  EXACT_NAME     nome normalizado idêntico                    confiança ALTA
  MORPHOLOGY     regra de sufixo FR↔EN (mancozèbe→mancozeb)   confiança MÉDIA
  SALT_STRIPPED  sal/éster removido (glyphosate sel d'...)    confiança BAIXA
  FUZZY          similaridade alta, sem regra                 confiança BAIXA
  NONE           não resolvido

    python3 scripts/normalize_substance.py evaluate
"""
import csv, json, os, re, sys, random, unicodedata
from difflib import SequenceMatcher
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FR = os.path.join(ROOT, 'data', 'raw', 'FR-T4-001')
IT = os.path.join(ROOT, 'data', 'raw', 'IT-T4-001', 'PROD_FTS_6_20260824.csv')
OUT = os.path.join(ROOT, 'data', 'samples', 'X-006-substance-normalisation.json')

# Marcadores de sal, éster e forma — removê-los é legítimo para chegar à molécula-mãe,
# mas NUNCA é a mesma coisa: fica registrado como SALT_STRIPPED, confiança baixa.
FUZZY_MIN = 0.92

SALT = re.compile(r"\b(sel|sels|ester|esters|de\s+sodium|de\s+potassium|d[eu]?\s*'?"
                  r"isopropylamine|d[eu]?\s*'?amine|dimethylamine|choline|"
                  r"trolamine|salt|sale|acide libre)\b.*$", re.I)

# Morfologia francesa → nome comum ISO/inglês. Cada regra existe porque foi observada
# no dado, não por generalização linguística.
MORPH = [
    # ATENÇÃO: as regras rodam DEPOIS de remover acentos, então o padrão é 'ebe',
    # não 'èbe'. Escrever o acento aqui faz a regra nunca disparar — foi o bug que
    # suprimiu as correspondências por morfologia na primeira medição.
    (r'ebe$', 'eb'),      # mancozèbe → mancozeb, manèbe → maneb, zinèbe → zineb
    (r'ime$', 'im'),      # carbendazime → carbendazim
    (r'ine$', 'in'),      # cyperméthrine → cypermethrin
    (r'ol$', 'ol'),
    (r'one$', 'one'),
    (r'azole$', 'azole'),
    (r'ate$', 'ate'),
    (r'el$', 'et'),       # folpel → folpet  (variante observada no próprio registro FR)
]


def strip_accents(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', strip_accents(s)).strip()


def morph(s):
    """Aplica as regras de sufixo ao último token, que é onde a molécula está."""
    t = norm(s)
    out = []
    for w in t.split():
        for pat, rep in MORPH:
            if re.search(pat, w):
                w = re.sub(pat, rep, w)
                break
        out.append(w)
    return ' '.join(out)


def load_fr_table():
    with open(os.path.join(FR, 'substance_active_utf8.csv'), encoding='utf-8') as f:
        rows = list(csv.DictReader(f, delimiter=';'))
    return [{'name': r['Nom substance active'], 'cas': (r['Numero CAS'] or '').strip(),
             'state': r['Etat d’autorisation']} for r in rows]


def load_fr_spellings():
    """Grafias como aparecem nos produtos, com o número de produtos que as usam."""
    c = Counter()
    with open(os.path.join(FR, 'produits_utf8.csv'), encoding='utf-8') as f:
        for p in csv.DictReader(f, delimiter=';'):
            for sa in (p['Substances actives'] or '').split('|'):
                n = sa.split('(')[0].strip()
                if n:
                    c[n] += 1
    return c


def load_it_spellings():
    c = Counter()
    with open(IT, encoding='utf-8') as f:
        for r in csv.DictReader(f, delimiter=';'):
            for sa in (r['sostanze_attive'] or '').split('|'):
                n = sa.strip()
                if n and n != '-':
                    c[n] += 1
    return c


class Normalizer:
    """Índice construído SOMENTE sobre o conjunto de construção."""

    def __init__(self, table):
        self.by_cas = {}
        self.by_name = {}
        self.by_morph = {}
        for r in table:
            key = norm(r['name'])
            self.by_name.setdefault(key, r)
            self.by_morph.setdefault(morph(r['name']), r)
            if r['cas']:
                self.by_cas.setdefault(r['cas'], r)

    def resolve(self, spelling, cas=None):
        if cas and cas in self.by_cas:
            return self.by_cas[cas], 'CAS', 'ALTA'
        n = norm(spelling)
        if n in self.by_name:
            return self.by_name[n], 'EXACT_NAME', 'ALTA'
        m = morph(spelling)
        if m in self.by_morph:
            return self.by_morph[m], 'MORPHOLOGY', 'MÉDIA'
        stripped = SALT.sub('', spelling).strip(" -,")
        if stripped and norm(stripped) != n:
            sn, sm = norm(stripped), morph(stripped)
            if sn in self.by_name:
                return self.by_name[sn], 'SALT_STRIPPED', 'BAIXA'
            if sm in self.by_morph:
                return self.by_morph[sm], 'SALT_STRIPPED', 'BAIXA'
        best, score = None, 0.0
        for k, r in self.by_name.items():
            s = SequenceMatcher(None, m, k).ratio()
            if s > score:
                best, score = r, s
        if score >= FUZZY_MIN:
            # Guarda contra falso positivo químico: duas moléculas diferentes podem ter
            # nomes quase idênticos ("methanol" × "ethanol", "alachlor" × "alaclor").
            # A diferença de UMA letra no radical muda a molécula, então o comprimento
            # e o primeiro caractere precisam bater.
            a, b = m.replace(' ', ''), norm(best['name']).replace(' ', '')
            if abs(len(a) - len(b)) > 2 or a[:1] != b[:1]:
                return None, 'REJECTED_FUZZY', None
            return best, 'FUZZY', 'BAIXA'
        return None, 'NONE', None


def evaluate():
    table = load_fr_table()
    fr_sp = load_fr_spellings()
    it_sp = load_it_spellings()

    # ---- amostra cega: 30% das grafias francesas ficam FORA da construção
    rng = random.Random(20260828)
    names = sorted(fr_sp)
    rng.shuffle(names)
    cut = int(len(names) * 0.7)
    train_names, blind_names = set(names[:cut]), set(names[cut:])
    # A tabela oficial de substâncias é DICIONÁRIO, não dado de treino: mutilá-la mediria
    # a mutilação, não a generalização. O que se mede na amostra cega é a cobertura sobre
    # grafias que não foram olhadas ao desenhar as regras.
    nz_full = Normalizer(table)
    nz_train = nz_full

    def run(nz, spellings, label):
        res = Counter()
        weighted = Counter()
        examples = []
        for sp in spellings:
            r, method, conf = nz.resolve(sp)
            res[method] += 1
            weighted[method] += fr_sp.get(sp, it_sp.get(sp, 1))
            if method in ('MORPHOLOGY', 'SALT_STRIPPED', 'FUZZY') and len(examples) < 8:
                examples.append((sp, r['name'] if r else None, method))
        n = sum(res.values())
        print(f'\n=== {label} ({n} grafias)')
        for k in ('CAS', 'EXACT_NAME', 'MORPHOLOGY', 'SALT_STRIPPED', 'FUZZY', 'REJECTED_FUZZY', 'NONE'):
            if res[k]:
                print(f'   {k:14s} {res[k]:5d}  {100*res[k]/n:5.1f}%   '
                      f'(por uso: {100*weighted[k]/sum(weighted.values()):5.1f}%)')
        resolved = n - res['NONE'] - res['REJECTED_FUZZY']
        print(f'   RESOLVIDO      {resolved:5d}  {100*resolved/n:5.1f}%')
        for e in examples:
            print(f'      ex. {e[2]:14s} "{e[0][:38]}" -> "{e[1]}"')
        return res, weighted, examples

    print('MEDIÇÃO DA NORMALIZAÇÃO DE SUBSTÂNCIA ATIVA')
    print(f'tabela oficial FR: {len(table)} substâncias, '
          f'{sum(1 for r in table if r["cas"])} com CAS')
    a = run(nz_full, sorted(fr_sp), 'FRANÇA — todas as grafias (conjunto completo)')
    b = run(nz_train, sorted(blind_names), 'FRANÇA — AMOSTRA CEGA (30% fora da construção)')
    c = run(nz_full, sorted(it_sp), 'ITÁLIA — grafias italianas contra a tabela francesa')

    def pack(t):
        res, wt, ex = t
        n = sum(res.values())
        return {'spellings': n, 'by_method': dict(res),
                'resolved': n - res['NONE'] - res['REJECTED_FUZZY'],
                'resolved_pct': round(100 * (n - res['NONE'] - res['REJECTED_FUZZY']) / n, 1),
                'rejected_fuzzy': res['REJECTED_FUZZY'],
                'weighted_by_use_pct': {k: round(100 * v / sum(wt.values()), 1)
                                        for k, v in wt.items()},
                'examples': [{'spelling': x[0], 'canonical': x[1], 'method': x[2]} for x in ex]}

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'source': 'derivado de FR-T4-001 (E-Phy) e IT-T4-001 (Min. Salute)',
                   'sources': ['FR-T4-001', 'IT-T4-001'], 'captured_at': '2026-08-28',
                   'SOURCE_LOCATION': 'FRANCE / ITALY', 'FACT_LOCATION': 'FRANCE / ITALY',
                   'ORIGINAL_LANGUAGE': 'FR/IT', 'layer': 'NATIONAL PRODUCT AUTHORIZATION',
                   'blind_split': '70% construção / 30% cega, semente 20260828',
                   'france_full': pack(a), 'france_blind': pack(b), 'italy_vs_france': pack(c)},
                  f, ensure_ascii=False, indent=2)
    print(f'\ngravado: {OUT}')


if __name__ == '__main__':
    evaluate()
