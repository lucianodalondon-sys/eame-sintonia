#!/usr/bin/env python3
"""
cobertura_cultura.py — R-20. A cobertura de uso era contada por ROTULO. Ela
passa a ser contada tambem por CELULA DE CULTURA DESENHADA.

## O defeito, medido

A tela de COBERTURA diz `AUTHORIZED_USE_ROW_COVERAGE = 128 de 163 (78,5%)`. O
denominador e ROTULO: um rotulo conta como coberto se dele saiu pelo menos um
par. `008259` LAMDEX EXTRA conta como coberto com 184 pares — e na pagina 3 dele
ha celulas de cultura com fio desenhado, cheias, cujo nome NUNCA virou par:
PORRO, LATTUGHE, SCAROLE, RUCOLA, FINOCCHIO. O vocabulario do leitor de uso e
uma lista fechada de 46 nomes e nenhum desses esta nela.

Cobertura por rotulo esconde exatamente isso: **o bloco que o leitor nao leu
desaparece no denominador do bloco que ele leu.**

## A regra

Para cada pagina de cada etichetta:

  1. acham-se as palavras que sao NOME DE CULTURA — nao pelo vocabulario fechado
     de 46 (que e justamente o que esta sob suspeita), e sim por um vocabulario
     ABERTO, tirado das celulas de cultura que o proprio leitor de dose gravou
     em `IT-DOSES.json` mais os 46 nomes de uso. Um nome que so aparece na
     tabela de dose e um nome que o leitor de USO nao tem;
  2. para cada ocorrencia, calcula-se a CELULA DESENHADA dela com o mesmo
     instrumento de R-14 (>= 3 fios atravessando a coluna, celula coerente com o
     texto que contem);
  3. celulas distintas — mesma pagina, mesma banda y, mesma coluna — sao uma so;
  4. cada celula e classificada:

    CROP_BLOCK_READ                 alguma cultura nomeada nela virou par de uso
    CROP_BLOCK_NOT_COLLECTED        nenhuma virou, e o nome esta fora do
                                    vocabulario de uso: o leitor nao tem palavra
                                    para este bloco
    CROP_BLOCK_IN_VOCABULARY_NOT_READ
                                    o nome ESTA no vocabulario e mesmo assim o
                                    bloco nao produziu par — e o caso mais grave,
                                    porque nao e diferenca de vocabulario

## O que este numero e, e o que ele nao e

Ele **nao** e "a cobertura verdadeira". Uma celula desenhada que contem um nome
de cultura nao e necessariamente um bloco de uso autorizado — pode ser cabecalho,
nota, tabela de carencia. O que ele mede e uma coisa so e verificavel: **quantas
celulas desenhadas com nome de cultura existem, e quantas delas o leitor de uso
alcancou.** A diferenca e um piso do que falta, nao o total do que falta.

E ele nao substitui `AUTHORIZED_USE_ROW_COVERAGE`: as duas contam coisas
diferentes e as duas ficam na tela, com o denominador de cada uma escrito ao
lado. Cobertura como numero unico foi o defeito da rodada 1.
"""
import argparse, json, os, re, sys, unicodedata
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def nz(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'\s+', ' ', s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pares', default='v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json')
    ap.add_argument('--doses', default='pilot-label-intelligence/demo/IT-DOSES.json')
    ap.add_argument('--pdfs', default='pilot-label-intelligence/labels/pdf')
    ap.add_argument('--bbox', default='/tmp/bboxcache')
    ap.add_argument('--fios', default='/tmp/fioscache')
    ap.add_argument('--bin', default='pilot-label-intelligence/bin')
    ap.add_argument('--out', default='v1/dados/COBERTURA-CULTURA.json')
    a = ap.parse_args()
    sys.path.insert(0, a.bin)
    import fios as F
    from par_validar import palavras, celula, celula_coerente, radical
    os.makedirs(a.fios, exist_ok=True)

    pares = json.load(open(a.pares, encoding='utf-8'))['PAIRS']
    # vocabulario de USO: os 46 nomes que o leitor de uso emite
    VOC_USO = {radical(str(x['CROP']).split('_')[0]) for x in pares}
    VOC_USO = {v for v in VOC_USO if len(v) >= 4}
    # vocabulario ABERTO: + os nomes que so a tabela de dose conhece
    VOC = set(VOC_USO)
    d = json.load(open(a.doses, encoding='utf-8'))
    for lab in d['LABELS']:
        for r in (lab.get('ROWS') or []):
            for pedaco in re.split(r'[,;()/]|\se\s', str(r.get('CROP') or '')):
                w = radical(pedaco.strip().split()[0]) if pedaco.strip().split() else ''
                if len(w) >= 4:
                    VOC.add(w)

    # que culturas cada rotulo publicou como PAR DE USO
    usadas = defaultdict(set)
    for x in pares:
        usadas[x['REGISTRATION_ID']].add(radical(str(x['CROP']).split('_')[0]))

    cont = Counter()
    porreg = {}
    naolidas = []
    regs = sorted({x['REGISTRATION_ID'] for x in pares} |
                  {l['REGISTRATION_ID'] for l in d['LABELS']})
    for reg in regs:
        pdf = os.path.join(a.pdfs, f'{reg}.pdf')
        if not os.path.exists(pdf):
            continue
        try:
            pgs = palavras(pdf, a.bbox)
        except Exception:
            continue
        celulas = {}
        for pi, pg in enumerate(pgs):
            try:
                r = F.fios(pdf, pi + 1, cache=a.fios)
            except Exception:
                continue
            seg, alt = r['SEG'], (r.get('PAGE_HEIGHT_PT') or 1e6)
            if not seg:
                continue
            for x0, y0, x1, y1, t in pg:
                w = radical(t)
                if len(w) < 4 or w not in VOC:
                    continue
                cel = celula(pg, x0, x1, (y0 + y1) / 2, seg, alt)
                if (cel is None or cel == 'RULES_ARE_TEXT_UNDERLINES'
                        or not celula_coerente(pg, *cel)):
                    continue
                k = (pi + 1, round(cel[0], 1), round(cel[1], 1), round(cel[2], 1))
                celulas.setdefault(k, set()).add(w)
        est = Counter()
        for k, nomes in celulas.items():
            if nomes & usadas[reg]:
                e = 'CROP_BLOCK_READ'
            elif nomes & VOC_USO:
                e = 'CROP_BLOCK_IN_VOCABULARY_NOT_READ'
            else:
                e = 'CROP_BLOCK_NOT_COLLECTED'
            est[e] += 1
            cont[e] += 1
            if e != 'CROP_BLOCK_READ':
                naolidas.append({'REGISTRATION_ID': reg, 'PAGE': k[0],
                                 'CELL_Y': [k[1], k[2]], 'CELL_X0': k[3],
                                 'CROP_WORDS': sorted(nomes), 'STATE': e})
        porreg[reg] = dict(est)

    tot = sum(cont.values())
    lidas = cont['CROP_BLOCK_READ']
    saida = {
        'DATASET': 'V1-COBERTURA-CULTURA',
        'RULE_ID': 'R-20',
        'O_QUE_ISTO_E': ('cobertura de uso contada por CELULA DE CULTURA DESENHADA, e nao por '
                         'rotulo'),
        'O_QUE_ISTO_NAO_E': ('nao e "a cobertura verdadeira": uma celula desenhada com nome de '
                             'cultura pode ser cabecalho, nota ou tabela de carencia. A '
                             'diferenca e um PISO do que falta, nao o total'),
        'CROP_CELLS_DETECTED': tot,
        'CROP_CELLS_READ': lidas,
        'PCT': round(100 * lidas / tot, 1) if tot else 'NOT_MEASURABLE',
        'COUNTS': dict(cont.most_common()),
        'USE_VOCABULARY_SIZE': len(VOC_USO),
        'OPEN_VOCABULARY_SIZE': len(VOC),
        'BY_LABEL': porreg,
        'NOT_READ': naolidas,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in cont.most_common():
        print(f'  {v:5}  {k}', file=sys.stderr)
    print(f'  cobertura por celula desenhada: {lidas}/{tot}'
          f'{f" ({100*lidas/tot:.1f}%)" if tot else ""}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
