#!/usr/bin/env python3
"""
prosa_censo.py — o CENSO da camada de prosa, por estrutura documental real.

A pergunta que este censo responde: **de que forma o documento apresenta cada
par de uso que a ferramenta publica sem tabela?** As familias abaixo nao foram
escolhidas de antemao: elas sao o que sobrou depois de medir, par a par, como o
`CROP_AS_WRITTEN` e o `TARGET_AS_WRITTEN` se relacionam com o texto do PDF.

## Os dois eixos, que nunca se colapsam

**ANCORA DA CULTURA** — por que a ferramenta acha que este par e desta cultura:

  `CABECALHO_DE_CULTURA`      o rotulo escreve "<CULTURA>: ..." e o par nasce dali
  `GRUPO_COM_PARENTESE`       "Pomacee (melo, pero, cotogno)" — a cultura e um
                              MEMBRO de um grupo, e quem diz que ela e membro e
                              o proprio rotulo, entre parenteses
  `LISTA_DE_CULTURAS`         "Pesco, Albicocco e Nettarino" — lista literal
  `CABECALHO_EMENDADO`        o `CROP_AS_WRITTEN` NAO existe no documento: e a
                              emenda de dois ou mais cabecalhos vizinhos que o
                              extrator colou ("CILIEGIO MELANZANA PEPERONE
                              POMODORO"). Ancora que nao existe no papel
  `SEM_ANCORA_TEXTUAL`        o `CROP_AS_WRITTEN` e uma DESCRICAO do proprio
                              extrator ("linha de dose por cultura"): a cultura
                              nao veio de uma frase de uso, veio da tabela de
                              dose

**NOMEACAO DO ALVO** — se o nome publicado esta no documento:

  `TARGET_NAME_LITERAL`                 o nome aparece no rotulo
  `TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL` nao aparece nenhuma vez. O rotulo
                              escreve o binomio ("Cydia pomonella") e a
                              ferramenta publica o nome comum ("CARPOCAPSA").
                              Provavelmente correto — e nao verificavel aqui

## Por que os dois eixos importam separadamente

Um par so e FATO quando as duas colunas fecham. Escopo provado com nome inferido
continua sendo inferencia; nome literal em escopo nao medido continua sendo
escopo nao medido. Colapsar os dois num selo so foi exatamente o defeito que a
rodada 3 encontrou na camada de tabela.
"""
import argparse, json, os, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prosa_escopo import nz, base, cabecalhos, cabeca_e_de_cultura, itens

RX_DESCRICAO = re.compile(r'linha de dose|faixa y|coluna de cultura', re.I)


def ancora_da_cultura(x, texto_doc):
    """Como o documento sustenta a cultura deste par."""
    craw = str(x.get('CROP_AS_WRITTEN') or '')
    n = nz(craw)
    if not n:
        return 'SEM_ANCORA_TEXTUAL'
    if RX_DESCRICAO.search(craw):
        return 'SEM_ANCORA_TEXTUAL'
    if n not in texto_doc:
        return 'CABECALHO_EMENDADO'
    if '(' in craw and nz(x['CROP']) in nz(re.sub(r'.*?\((.*?)\).*', r'\1', craw)):
        return 'GRUPO_COM_PARENTESE'
    if re.search(r'[,;]|\se\s', craw):
        return 'LISTA_DE_CULTURAS'
    return 'CABECALHO_DE_CULTURA'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pares', default='v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json')
    ap.add_argument('--escopo', default='v1/dados/PROSA-ESCOPO.json')
    ap.add_argument('--fluxo', default='/tmp/leiturafluxo')
    ap.add_argument('--out', default='v1/dados/PROSA-CENSO.json')
    a = ap.parse_args()

    TAB = {'GEOMETRIC_TABLE', 'MERGED_COLUMN_TABLE'}
    pares = json.load(open(a.pares, encoding='utf-8'))['PAIRS']
    esc = json.load(open(a.escopo, encoding='utf-8'))['VERDICT']

    cache = {}
    def doc(reg):
        if reg not in cache:
            f = os.path.join(a.fluxo, reg + '.txt')
            cache[reg] = nz(open(f, encoding='utf-8', errors='replace').read()) \
                if os.path.exists(f) else ''
        return cache[reg]

    # PROVADO / CONTRADITO / AMBIGUO / NAO SEI, sobre os dois eixos
    def veredito(sc, nm, anc):
        if sc == 'PROSE_SCOPE_CONTRADICTED':
            return 'CONTRADITO'
        if anc in ('CABECALHO_EMENDADO', 'SEM_ANCORA_TEXTUAL'):
            return 'NAO_SEI'
        if nm == 'TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL':
            return 'NAO_SEI'
        if sc == 'PROSE_SCOPE_PROVEN':
            # medido: PROSE_SCOPE_PROVEN nao discrimina (ver o controle no
            # cabecalho de prosa_escopo.py). Escopo "provado" nao autoriza.
            return 'AMBIGUO'
        return 'NAO_SEI'

    fam = defaultdict(Counter)
    porrota = defaultdict(Counter)
    linhas = []
    ordem = {}
    for x in pares:
        reg = x['REGISTRATION_ID']
        i = ordem[reg] = ordem.get(reg, -1) + 1
        if x['ROUTE'] in TAB:
            continue
        k = f'{reg}#{i}'
        e = esc.get(k, {})
        anc = ancora_da_cultura(x, doc(reg))
        sc, nm = e.get('scope', 'NOT_RUN'), e.get('naming', 'NOT_RUN')
        v = veredito(sc, nm, anc)
        fam[anc][v] += 1
        porrota[x['ROUTE']][v] += 1
        linhas.append({'KEY': k, 'REGISTRATION_ID': reg, 'PRODUCT': x.get('PRODUCT'),
                       'CROP': x['CROP'], 'TARGET': x['TARGET'], 'ROUTE': x['ROUTE'],
                       'ANCHOR': anc, 'SCOPE': sc, 'NAMING': nm, 'VERDICT': v})

    tot = Counter(l['VERDICT'] for l in linhas)
    saida = {
        'DATASET': 'V1-PROSA-CENSO',
        'O_QUE_ISTO_E': ('censo dos pares de uso lidos de PROSA, por estrutura documental real, '
                         'com os dois eixos separados: ancora da cultura e nomeacao do alvo'),
        'O_QUE_ISTO_NAO_E': ('nao e um veredito de uso autorizado: PROVADO aqui significa que o '
                             'documento sustenta o par, e AMBIGUO/NAO_SEI significam que ele nao '
                             'sustenta nem desmente'),
        'PROSE_PAIRS_TOTAL': len(linhas),
        'POR_VEREDITO': dict(tot.most_common()),
        'POR_ANCORA': {k: dict(v.most_common()) for k, v in sorted(fam.items())},
        'POR_ROTA': {k: dict(v.most_common()) for k, v in sorted(porrota.items())},
        'LINHAS': linhas,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  PROSE_PAIRS_TOTAL = {len(linhas)}', file=sys.stderr)
    for k, v in tot.most_common():
        print(f'    {v:5}  {k}', file=sys.stderr)
    print('\n  por ANCORA DA CULTURA:', file=sys.stderr)
    for k, v in sorted(fam.items(), key=lambda kv: -sum(kv[1].values())):
        print(f'    {sum(v.values()):5}  {k:24} {dict(v.most_common())}', file=sys.stderr)
    print('\n  por ROTA:', file=sys.stderr)
    for k, v in sorted(porrota.items(), key=lambda kv: -sum(kv[1].values())):
        print(f'    {sum(v.values()):5}  {k:24} {dict(v.most_common())}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
