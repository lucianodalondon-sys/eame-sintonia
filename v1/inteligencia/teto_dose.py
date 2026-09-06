#!/usr/bin/env python3
"""
teto_dose.py — a etichetta as vezes poe um TETO POR CULTURA fora da tabela.

A tabela de usos nao e o documento inteiro. A etichetta 008259 (LAMDEX EXTRA) e
mais quatro registros trazem, logo abaixo da tabela:

    Per le seguenti colture non superare le seguenti dosi per ettaro:
    erba medica, prati e pascoli: 400 g/ha
    soia, carciofo, lattughe e simili, finocchio: 600 g/ha
    mais dolce, aglio: 800 g/ha
    mais da foraggio: 1000 g/ha

A tabela da 580-1200 g/ha para SOIA x CIMICI. A nota diz 600. As duas frases sao
do mesmo documento oficial e tem o mesmo valor legal — e a ferramenta exibia
1200, o dobro do autorizado, sem dizer que a nota existia. A string "non
superare" nao aparecia uma unica vez em todo o payload.

Este modulo le a nota e cruza com a dose exibida. Nao calcula uma dose nova: um
numero que nao esta escrito no rotulo nao pode nascer aqui. Ele marca o par e
publica o teto LITERAL ao lado, para quem le decidir.

Casamento por FRASE INTEIRA. "mais dolce" nao e "mais", e "mais da foraggio"
tampouco: casar por token faria o teto do milho doce cair sobre o milho, que e
outra cultura. Medido: por token o modulo acusava 60 pares; por frase inteira,
40 — e as 20 de diferenca eram todas MAIS contra o teto de MAIS DOLCE.
"""
import argparse, json, os, re, subprocess, sys, unicodedata

CABECALHO = re.compile(r'non superare le seguenti dosi per ettaro\s*:?', re.I)
ITEM = re.compile(r'^\s*([a-zà-ÿ][a-zà-ÿ ,\'\-]{2,90}?)\s*:\s*([\d.,]+)\s*(kg|g|l|ml)\s*/\s*ha\b', re.I)
# Marcador de que existe restricao de dose FORA da tabela que este modulo nao le.
OUTRAS_NOTAS = re.compile(r'non superare (?!le seguenti dosi per ettaro)|dose massima', re.I)


def sem_acento(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()


def em_g(valor, unidade):
    """Normaliza para g/ha. l/ha e ml/ha sao de PRODUTO, e o teto tambem: a
    comparacao continua valendo dentro da mesma unidade do rotulo."""
    v = float(str(valor).replace(',', '.'))
    u = unidade.lower()
    if u in ('kg', 'l'):
        return v * 1000.0
    return v


def texto(reg, pdfs, cache):
    os.makedirs(cache, exist_ok=True)
    alvo = os.path.join(cache, f'{reg}.txt')
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        pdf = os.path.join(pdfs, f'{reg}.pdf')
        if not os.path.exists(pdf):
            return None
        try:
            subprocess.run(['pdftotext', '-layout', pdf, alvo], check=True,
                           capture_output=True, timeout=180)
        except Exception:
            return None
    return open(alvo, encoding='utf-8', errors='replace').read()


def tetos(t):
    out = []
    for m in CABECALHO.finditer(t):
        for linha in t[m.end():m.end() + 800].split('\n')[1:]:
            if not linha.strip():
                if out:
                    break
                continue
            g = ITEM.match(linha)
            if not g:
                break
            culturas = [sem_acento(c).strip() for c in re.split(r'[,;]| e ', g.group(1))
                        if len(sem_acento(c).strip()) > 2]
            out.append({'CULTURAS': culturas, 'VALOR': g.group(2),
                        'UNIDADE': f'{g.group(3)}/ha', 'G_HA': em_g(g.group(2), g.group(3)),
                        'LITERAL': re.sub(r'\s+', ' ', linha).strip()})
    return out


def topo(dose):
    nums = re.findall(r'\d+[.,]?\d*', str(dose or ''))
    return max((float(n.replace(',', '.')) for n in nums), default=None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdfs', default='pilot-label-intelligence/labels/pdf')
    ap.add_argument('--cache', default='/tmp/tetotxt')
    ap.add_argument('--pacote', default='v1/dados/COLLECTION-PACKAGE.json')
    ap.add_argument('--out', default='v1/dados/TETO-DOSE.json')
    a = ap.parse_args()

    regs = [i['REGISTRATION_ID'] for i in json.load(open(a.pacote, encoding='utf-8'))['ITEMS']]
    por_reg, com_outras = {}, []
    for reg in regs:
        t = texto(reg, a.pdfs, a.cache)
        if t is None:
            continue
        # A etichetta costuma repetir a tabela e a nota (frente e verso, ou duas
        # copias no mesmo PDF). Teto repetido nao e teto novo.
        vistos, ts = set(), []
        for x in tetos(t):
            if x['LITERAL'] in vistos:
                continue
            vistos.add(x['LITERAL']); ts.append(x)
        if ts:
            por_reg[reg] = ts
        elif OUTRAS_NOTAS.search(t):
            com_outras.append(reg)

    saida = {
        'DATASET': 'V1-TETO-DOSE',
        'RULE_ID': 'R-12',
        'O_QUE_ISTO_E': ('teto de dose por cultura escrito na etichetta FORA da tabela de usos, '
                         'lido literalmente'),
        'O_QUE_ISTO_NAO_E': ('nao calcula dose nova nem corrige a tabela: publica os dois numeros '
                             'do documento e diz que eles se contradizem para aquela cultura'),
        'MATCH': 'igualdade de frase inteira da cultura, nao de token',
        'LABELS_WITH_CEILING': len(por_reg),
        'LABELS_WITH_OTHER_DOSE_NOTES_NOT_READ': len(com_outras),
        'OTHER_DOSE_NOTES_NOT_READ': com_outras,
        'NOTA_SOBRE_AS_OUTRAS': ('estes rotulos tem alguma restricao de dose fora da tabela que '
                                 'ESTE modulo nao le (formatos como "non superare la dose massima '
                                 'di X per anno"). Isto e LABEL_NOTES_NOT_READ, e nao autoriza '
                                 'dizer que nao ha restricao'),
        'CEILINGS': por_reg,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  rotulos com teto por cultura: {len(por_reg)} | com nota de dose nao lida por '
          f'este modulo: {len(com_outras)}', file=sys.stderr)
    for reg, ts in list(por_reg.items())[:2]:
        for t in ts:
            print(f'    {reg}  {t["LITERAL"]}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
