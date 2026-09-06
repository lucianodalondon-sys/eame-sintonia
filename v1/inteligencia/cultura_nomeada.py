#!/usr/bin/env python3
"""
cultura_nomeada.py — R-21. O NOME DA CULTURA que a ferramenta publica esta
escrito no rotulo, ou nasceu de uma equivalencia que este repositorio nao tem?

## Por que esta regra existe, e por que ela e a irma que faltava

R-17 (`alvo_nomeado.py`) ja faz esta pergunta do lado do ALVO: "CARPOCAPSA" nao
esta escrito em 007555, esta escrito "Cydia pomonella", e o nome publicado vem
de taxonomia. A pergunta simetrica — do lado da CULTURA — nunca tinha sido
feita, e a camada de cultura e a mais cara das duas: e ela que diz em que
lavoura o produto pode entrar.

Medido, e o resultado nao e cosmetico:

    CROP_NAME_LITERAL              2.874   o nome esta escrito assim
    CROP_NAME_INFLECTED_IN_LABEL      31   a etichetta flexiona (cavolo/cavoli)
    CROP_NAME_NOT_IN_LABEL            23   nenhuma palavra do documento tem
                                           esta raiz

Os 23 nao sao um so fenomeno, e o modulo NAO decide qual deles e:

    FRUMENTO   12  015232 · 017358 · 017824
                   a etichetta escreve "Grano tenero e duro, Triticale".
                   grano E frumento em italiano — a afirmacao e provavelmente
                   verdadeira, mas quem sabe disso e um dicionario que nao esta
                   aqui, e ate a rodada passada R-14 carimbava estes pares com
                   TABLE_GEOMETRY sem dizer que tinha absolvido por sinonimo.

    ZUCCHINO    5  009005 · 011660 · 015253 · 017115 · 017206
                   a etichetta escreve "zucca". Zucca e zucchino sao duas
                   culturas no registro italiano, e nao uma flexao da outra.

    FAGIOLO     4  018270 · 018271 · 018277 · 018279
                   a etichetta escreve "ORTICOLE (CARCIOFO, CAROTA, FAGIOLINO,
                   FAVA, PISELLO, ...)". FAGIOLINO nao e FAGIOLO: o diminutivo
                   e outra entrada.

    CILIEGIO    2  002983 · 013405
                   a etichetta escreve "Pomodoro (ad esclusione di Pomodoro
                   ciliegino), Melanzana e Peperone". "ciliegino" ali e o
                   TOMATE CEREJA, e esta dentro de uma EXCLUSAO. A lista de
                   pares traz CILIEGIO — a arvore.

O ultimo caso e o mais grave e e o unico que NAO chega a tela: R-10
(`coleta/exclusao.py`) ja o retira antes, como CROP_ONLY_INSIDE_EXCLUSION. Ou
seja, na tela sao 21 e nao 23. Isso nao diminui o caso; e o contrario. Duas
regras construidas para perguntas diferentes — "este nome esta so dentro de uma
exclusao?" e "este nome existe no documento?" — acusaram o mesmo defeito por
caminhos independentes, e concordar por acaso e o mais perto de prova que este
repositorio consegue chegar sem a Banca Dati.

## A regra

Tres estados, e a diferenca entre os dois primeiros importa:

    CROP_NAME_LITERAL             alguma leitura do PDF contem o nome, com
                                  fronteira de palavra
    CROP_NAME_INFLECTED_IN_LABEL  nao contem o nome, mas contem uma palavra com
                                  a MESMA RAIZ (`radical` de R-14: corta a
                                  ultima vogal e o h de apoio). cavolo/cavoli,
                                  pisello/piselli, fagiolo/fagioli. A etichetta
                                  escreveu a palavra; escreveu no plural.
    CROP_NAME_NOT_IN_LABEL        nenhuma palavra do documento tem essa raiz

Sem o estado do meio a regra teria 54 acusacoes em vez de 23, e as 31 de
diferenca seriam todas plural italiano — isto e, a regra estaria escondendo fato
verdadeiro para parecer rigorosa. `radical` separa flexao (fagiolo/fagioli, a
mesma raiz 'fagiol') de palavra diferente (fagiolino, raiz 'fagiolin';
ciliegino, raiz 'ciliegin'; zucca, raiz 'zucc'; grano, raiz 'gran').

O texto e lido nas TRES formas do `pdftotext` (fluxo, -layout, -raw), pelo mesmo
motivo de R-17: palavra partida entre colunas numa delas costuma estar inteira
noutra, e o que se procura e a PRESENCA da palavra.

## O que esta regra NAO faz

Nao diz que o par esta errado e nao remove nada. Nao sabe se ZUCCHINO saiu de
"zucca" por engano do extrator ou por uma equivalencia correta do registro
italiano — para saber isso e preciso a Banca Dati dei Prodotti Fitosanitari, que
nao esta neste repositorio. NAO SEI, e o modulo escreve NAO SEI.

O que ela faz e impedir que essas 23 afirmacoes viajem com o mesmo selo das
2.874 que voltam ao documento palavra por palavra. Uma equivalencia de cultura
so pode nascer de prova documental ou taxonomica; semelhanca de escrita nao e
prova, e "fagiolino parece fagiolo" e semelhanca de escrita.
"""
import argparse, json, os, re, subprocess, sys, unicodedata
from collections import Counter

# Descricoes que o proprio extrator escreve no lugar da celula, quando nao ha
# celula. Nao sao texto do documento e nao podem ser citadas como "o que a
# etichetta escreve".
DESCRICAO_DO_EXTRATOR = re.compile(r'linha de dose|faixa y|coluna de cultura', re.I)


def sa(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()


def radical(w):
    """A mesma funcao de R-14, repetida aqui de proposito.

    Copiar oito linhas e pior que importar — mas R-21 e R-14 respondem perguntas
    diferentes, e se um dia a raiz de R-14 mudar para acomodar geometria, a
    pergunta "o nome esta escrito?" nao deve mudar junto sem alguem decidir.
    O portao MEASURED_CONSTANTS_ARE_MEASURED confere que as duas continuam
    dando a mesma resposta enquanto ninguem decidir o contrario.
    """
    w = re.sub(r'[^a-z]', '', sa(w))
    if len(w) >= 5:
        r = re.sub(r'h?[aeiou]$', '', w)
        if len(r) >= 4:
            return r
    return w


def leituras(reg, pdfs, cache):
    """As tres leituras do mesmo PDF, concatenadas e normalizadas."""
    os.makedirs(cache, exist_ok=True)
    pdf = os.path.join(pdfs, f'{reg}.pdf')
    if not os.path.exists(pdf):
        return ''
    partes = []
    for modo, suf in (([], 'fluxo'), (['-layout'], 'layout'), (['-raw'], 'raw')):
        alvo = os.path.join(cache, f'{reg}.{suf}.txt')
        if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
            try:
                subprocess.run(['pdftotext'] + modo + [pdf, alvo], check=True,
                               capture_output=True, timeout=180)
            except Exception:
                continue
        try:
            partes.append(open(alvo, encoding='utf-8', errors='replace').read())
        except OSError:
            pass
    return re.sub(r'\s+', ' ', sa(' || '.join(partes))).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pares', default='v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json')
    ap.add_argument('--pdfs', default='pilot-label-intelligence/labels/pdf')
    ap.add_argument('--cache', default='/tmp/nomecache')
    ap.add_argument('--out', default='v1/dados/CULTURA-NOMEADA.json')
    a = ap.parse_args()

    pares = json.load(open(a.pares, encoding='utf-8'))['PAIRS']
    ver, det = {}, []
    cont = Counter()
    memo, ordem = {}, {}
    for x in pares:
        reg = x['REGISTRATION_ID']
        i = ordem[reg] = ordem.get(reg, -1) + 1
        chave = f'{reg}#{i}'
        if reg not in memo:
            t = leituras(reg, a.pdfs, a.cache)
            memo[reg] = (t, {radical(w) for w in re.findall(r"[a-z']+", t)})
        t, raizes = memo[reg]
        partes = [p for p in (sa(q) for q in str(x['CROP']).split('_')) if len(p) >= 4]
        if not t or not partes:
            est = 'CROP_NAME_NOT_CHECKED'
        elif all(re.search(r'\b' + re.escape(p), t) for p in partes):
            est = 'CROP_NAME_LITERAL'
        elif all(radical(p) in raizes for p in partes):
            est = 'CROP_NAME_INFLECTED_IN_LABEL'
        else:
            est = 'CROP_NAME_NOT_IN_LABEL'
            bruto = str(x.get('CROP_AS_WRITTEN') or '')
            escrito = ('CROP_AS_WRITTEN_IS_A_PARSER_DESCRIPTION'
                       if not bruto or DESCRICAO_DO_EXTRATOR.search(bruto) else bruto[:240])
            faltou = [p for p in partes if radical(p) not in raizes]
            det.append({
                'KEY': chave, 'REGISTRATION_ID': reg, 'PRODUCT': x.get('PRODUCT'),
                'CROP': x['CROP'], 'TARGET': x['TARGET'], 'ROUTE': x['ROUTE'],
                'CROP_AS_WRITTEN': escrito,
                'ROOT_NOT_IN_DOCUMENT': [radical(p) for p in faltou],
                'PROOF': (f'nenhuma palavra das tres leituras do PDF oficial tem a raiz '
                          f'{[radical(p) for p in faltou]}. O nome "{x["CROP"]}" nao e uma '
                          f'flexao de nada que o documento escreve: ele vem de uma '
                          f'equivalencia de cultura que este repositorio nao tem'),
            })
        ver[chave] = est
        cont[est] += 1

    saida = {
        'DATASET': 'V1-CULTURA-NOMEADA',
        'RULE_ID': 'R-21',
        'O_QUE_ISTO_E': 'o nome da CULTURA que a ferramenta publica esta escrito no rotulo?',
        'O_QUE_ISTO_NAO_E': ('nao diz que o par esta errado e nao remove nada; nao sabe se '
                             'ZUCCHINO saiu de "zucca" por engano ou por equivalencia correta '
                             'do registro italiano. NAO SEI, e diz NAO SEI'),
        'IRMA_DE': 'R-17, que faz a mesma pergunta do lado do ALVO',
        'READINGS': 'pdftotext em tres modos (fluxo, -layout, -raw)',
        'INFLECTION': ('CROP_NAME_INFLECTED_IN_LABEL usa a raiz de R-14 (corta a ultima vogal '
                       'e o h de apoio): separa plural italiano de palavra diferente. Sem esse '
                       'estado a regra acusaria 54 em vez de 23, e as 31 de diferenca seriam '
                       'todas plural'),
        'PAIRS': len(pares),
        'COUNTS': dict(cont.most_common()),
        'VERDICT': ver,
        'NOT_IN_LABEL': det,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in cont.most_common():
        print(f'  {v:5}  {k}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
