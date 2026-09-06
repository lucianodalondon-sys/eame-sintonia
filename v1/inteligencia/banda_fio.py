#!/usr/bin/env python3
"""
banda_fio.py — R-22. A BANDA que o extrator chamou de UMA LINHA contem um fio
desenhado de separacao de linha?

## O defeito, e por que ele nao tinha detector

Toda a camada de dose repete, desde a rodada 2, que nao sabe detectar FUSAO DE
LINHA: `alvo_literal.py` publica `FUSION_DETECTOR: NOT_IMPLEMENTED` e explica os
tres instrumentos que falharam. A fusao provada de 008259 — "Nottue
defogliatrici (allo scoperto) tentredine" com a dose da linha de cima — continua
sendo detectada por ninguem.

Este modulo nao resolve o caso geral. Ele resolve o caso em que o DOCUMENTO
DESENHOU A SEPARACAO e o extrator passou por cima dela:

    o extrator guarda, para cada linha de dose, a banda SOURCE_Y de onde leu.
    Se dentro dessa banda existe um fio horizontal desenhado que atravessa a
    largura da propria linha, com texto acima E abaixo dele, entao a banda nao
    e uma linha: sao duas, e a etichetta desenhou o risco entre elas.

Nao ha vocabulario, nao ha heuristica de conteudo e nao ha numero novo: usa a
mesma cobertura de 60% que `fios.mesma_celula` e `par_validar` ja usam para
dizer que um fio atravessa uma coluna.

## O que foi medido

Das 839 linhas de dose com banda e pagina preservadas, **29** tem um fio
desenhado por dentro:

    017687  6    013560  4    013590  4    008259  3    015275  3
    007876  2    014091  2    004701  1    017340  1    017409  1
    018270  1    018279  1

A primeira medicao, sem exigir texto dos dois lados do fio, acusava 188 — e as
159 de diferenca eram a PROPRIA BORDA da banda, que cai meio ponto para dentro
do SOURCE_Y. Borda de linha nao e separador de linha, e acusar as duas coisas
com o mesmo nome seria inventar defeito.

018270 e o caso que o red team achou por fora, lendo a pagina: a dose da linha
do MAIS e o unico "1" da regiao e ele esta na linha DEBAIXO, do outro lado do
risco. A ferramenta publicava esse 1 como dose do MAIS.

## O que este modulo NAO faz

Nao diz qual das duas linhas e a certa e nao escolhe um numero. Nao remove o par
de uso: a cultura e o alvo continuam podendo estar certos, e e so a atribuicao
do NUMERO aquela linha que fica sem prova. E nao detecta a fusao quando o
documento NAO desenhou o risco — nesse caso continua valendo o
`FUSION_DETECTOR: NOT_IMPLEMENTED` de R-13, e isto aqui nao o substitui.

    DOSE_ROW_BAND_IS_ONE_DRAWN_ROW        a banda nao tem risco por dentro
    DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE    tem: sao duas linhas coladas
    DOSE_ROW_BAND_NOT_PRESERVED           o extrator nao guardou banda ou pagina
    DOSE_ROW_BAND_NOT_CHECKED             sem PDF, sem fios ou sem palavra na banda
"""
import argparse, json, os, sys
from collections import Counter

COBRE = 0.6      # a mesma fracao de fios.mesma_celula e de par_validar
FOLGA = 0.5      # pontos: o fio tem de estar por DENTRO da banda, nao na borda


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--doses', default='pilot-label-intelligence/demo/IT-DOSES.json')
    ap.add_argument('--pdfs', default='pilot-label-intelligence/labels/pdf')
    ap.add_argument('--bbox', default='/tmp/bboxcache')
    ap.add_argument('--fios', default='/tmp/fioscache')
    ap.add_argument('--bin', default='pilot-label-intelligence/bin')
    ap.add_argument('--out', default='v1/dados/BANDA-FIO-CHECK.json')
    a = ap.parse_args()
    sys.path.insert(0, a.bin)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fios as F
    from par_validar import palavras

    memo = {}

    def segmentos(pdf, p1):
        k = (pdf, p1)
        if k not in memo:
            try:
                memo[k] = F.fios(pdf, p1, cache=a.fios)['SEG']
            except Exception:
                memo[k] = None
        return memo[k]

    ver, det = {}, []
    cont = Counter()
    for lab in json.load(open(a.doses, encoding='utf-8'))['LABELS']:
        reg = lab['REGISTRATION_ID']
        pdf = os.path.join(a.pdfs, f'{reg}.pdf')
        linhas = lab.get('ROWS') or []
        if not linhas:
            continue
        try:
            pgs = palavras(pdf, a.bbox) if os.path.exists(pdf) else []
        except Exception:
            pgs = []
        for i, r in enumerate(linhas):
            chave = f'{reg}#{i}'
            sy, sp = r.get('SOURCE_Y'), r.get('SOURCE_PAGE')
            if not sy or not sp or not pgs or sp > len(pgs):
                ver[chave] = ('DOSE_ROW_BAND_NOT_PRESERVED' if not sy or not sp
                              else 'DOSE_ROW_BAND_NOT_CHECKED')
                cont[ver[chave]] += 1
                continue
            y0, y1 = min(sy), max(sy)
            pg = pgs[sp - 1]
            dentro = [(x0, (yy0 + yy1) / 2, x1) for x0, yy0, x1, yy1, _t in pg
                      if y0 <= (yy0 + yy1) / 2 <= y1]
            seg = segmentos(pdf, sp)
            if y1 <= y0 or not dentro or seg is None:
                ver[chave] = 'DOSE_ROW_BAND_NOT_CHECKED'
                cont[ver[chave]] += 1
                continue
            bx0 = min(w[0] for w in dentro)
            bx1 = max(w[2] for w in dentro)
            larg = max(bx1 - bx0, 1e-6)
            cys = [w[1] for w in dentro]
            cruzam = [round(y, 2) for y, xa, xb in seg
                      if y0 + FOLGA < y < y1 - FOLGA
                      and (min(bx1, xb) - max(bx0, xa)) / larg >= COBRE
                      and any(v < y for v in cys) and any(v > y for v in cys)]
            if cruzam:
                ver[chave] = 'DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE'
                det.append({
                    'KEY': chave, 'REGISTRATION_ID': reg, 'PRODUCT': lab.get('PRODUCT'),
                    'CROP': r.get('CROP'), 'TARGET': r.get('TARGET'),
                    'DOSE_PER_HECTARE': r.get('DOSE_PER_HECTARE'),
                    'SOURCE_PAGE': sp, 'SOURCE_Y': [round(y0, 2), round(y1, 2)],
                    'RULE_Y': cruzam[:4],
                    'PROOF': (f'na pagina {sp} a banda y {y0:.1f}-{y1:.1f}, que o extrator leu '
                              f'como UMA linha, tem {len(cruzam)} fio(s) horizontal(is) '
                              f'desenhado(s) por dentro (y={cruzam[:3]}), atravessando ao menos '
                              f'{int(COBRE * 100)}% da largura da propria linha, com texto acima '
                              f'e abaixo. A etichetta desenhou a separacao e o extrator leu as '
                              f'duas linhas como uma'),
                })
            else:
                ver[chave] = 'DOSE_ROW_BAND_IS_ONE_DRAWN_ROW'
            cont[ver[chave]] += 1

    saida = {
        'DATASET': 'V1-BANDA-FIO-CHECK',
        'RULE_ID': 'R-22',
        'O_QUE_ISTO_E': ('a banda que o extrator leu como UMA linha de dose contem um fio '
                         'horizontal desenhado por dentro?'),
        'O_QUE_ISTO_NAO_E': ('nao diz qual das duas linhas e a certa, nao escolhe numero e nao '
                             'remove o par de uso: so tira a prova da atribuicao do numero'),
        'NAO_SUBSTITUI': ('FUSION_DETECTOR de R-13 continua NOT_IMPLEMENTED: este modulo so ve '
                          'a fusao quando o documento DESENHOU o risco entre as duas linhas'),
        'COBERTURA_MINIMA_DO_FIO': COBRE,
        'ROWS': sum(cont.values()),
        'COUNTS': dict(cont.most_common()),
        'VERDICT': ver,
        'CROSSED': det,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in saida['COUNTS'].items():
        print(f'  {v:5}  {k}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
