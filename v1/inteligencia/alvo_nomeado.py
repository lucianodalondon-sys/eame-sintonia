#!/usr/bin/env python3
"""
alvo_nomeado.py — R-17. O NOME do alvo que a ferramenta publica esta escrito no
rotulo, ou veio de uma taxonomia que este repositorio nao tem?

## O defeito, medido

A tela imprime uma coluna chamada "Alvo" com nomes como `CARPOCAPSA`,
`CECIDOMIA`, `LITOCOLLETE`, `BOTRITE`. Em **256 pares publicados** esse nome nao
aparece **uma unica vez** no documento oficial. O caso maior e `007555`, que
escreve:

    "Contro afidi (Dysaphis plantaginea, Aphis pomi), ditteri cecidomidi
     (Contarinia pyrivora, Dasineura pyri), lepidotteri (Adoxophyes orana,
     Phyllonorycter blancardella, Cydia pomonella, Yponomeuta malinellus)"

e do qual a ferramenta publica CARPOCAPSA, CECIDOMIA, LITOCOLLETE e COCCINIGLIE.

`Cydia pomonella` **e** a carpocapsa e `Phyllonorycter blancardella` **e** a
litocollete — isso e verdade entomologica, e provavelmente o par esta certo. Mas
quem sabe disso e uma TAXONOMIA que nao esta neste repositorio, nao pode ser
mostrada ao lado da afirmacao, e nao volta ao documento. Pela LEI ZERO isso e
INFERENCIA, e inferencia tem de viajar rotulada como inferencia.

## A regra

Uma linha, e ela e um `grep`: o nome normalizado do alvo, com as suas partes,
aparece no texto do rotulo? O texto e lido nas TRES formas que o `pdftotext`
oferece — coluna, fluxo e cru — porque uma palavra partida entre colunas numa
delas costuma estar inteira noutra, e o que se procura aqui e a PRESENCA da
palavra, nao a estrutura em volta dela.

    TARGET_NAME_LITERAL                    o nome esta no rotulo
    TARGET_NAME_INFLECTED_IN_LABEL         nao esta assim, mas o documento escreve
                                           a MESMA palavra flexionada
    TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL   nao esta em nenhuma das tres leituras
    TARGET_NAME_NOT_CHECKED                nao ha texto para conferir

## O ESTADO DO MEIO, QUE ESTA REGRA NAO TINHA E A IRMA TINHA

R-21 distingue `CROP_NAME_INFLECTED_IN_LABEL` ("cavoli" e CAVOLO, 31 pares) de
`CROP_NAME_NOT_IN_LABEL`, e o `payload.py` argumenta, com razao, que recusar por
causa de um plural "seria esconder fato verdadeiro para a regra parecer severa".
R-17 nao tinha esse estado — e por isso dizia, sobre 34 pares, uma frase falsa:

    "este nome nao esta escrito no rotulo. O documento nomeia a praga pelo
     binomio (Cydia pomonella) e a ferramenta publica o nome comum"

Em 015232 a celula desenhada de "Aglio, Cipolla (uso in serra)" escreve
literalmente **"Ruggini (Puccinia spp.)"**, e o par publicado diz RUGGINE. Nao e
taxonomia: e o plural italiano.

    RUGGINE / "Ruggini"        15      MOSCA / "mosche"     6
    COCCINIGLIE / "cocciniglia" 12      NOTTUE / "nottua"    1

Doze desses 34 viram FATO com o estado novo — todos com R-14 ja absolvendo o par
e a cultura literal. Esconder fato verdadeiro e tao caro quanto publicar fato
falso, e a assimetria entre as duas regras irmas nao tinha motivo escrito.

## O QUALIFICADOR QUE O NOME CURTO JOGA FORA

A rodada 4 achou uma terceira coisa, e ela nao e um quarto estado: e um CAMPO.
Em 008259, 013560, 013590, 015275 e 017687 a celula do alvo escreve **"mosca
bianca"** — a mosca-branca, Bemisia/Trialeurodes — e a ferramenta publica
**MOSCA**, que em italiano e a mosca da fruta ou a mosca das raizes. Sao 85
pares. A palavra "mosca" ESTA escrita no rotulo, entao R-17 dizia LITERAL e
tinha razao; o que ela nao dizia e que a palavra nunca aparece sozinha ali.

Medido no acervo: em 834 pares o nome publicado do alvo NUNCA ocorre sozinho na
celula — vem sempre com uma palavra atras. As mais frequentes:

    INFESTANTI sensibili   273     MOSCA bianca            85
    INFESTANTI controllate 128     DITTERI cecidomidi      56
    NOTTUE defogliatrici   100     ANARSIA lineatella      12

E aqui esta o limite desta ferramenta, dito sem rodeio: "sensibili" e adjetivo e
nao muda a praga; "lineatella" e o nome da especie e confirma; "bianca" muda o
inseto. Distinguir os tres precisa de ENTOMOLOGIA, que nao esta neste
repositorio. Entao o modulo NAO acusa e NAO retira: ele publica o qualificador
ao lado do nome, do mesmo jeito que `crop_scope` publica "da vino" ao lado de
VITE, e quem le decide. Chamar isso de erro seria inventar; esconder seria pior.

## O que esta regra NAO faz

Nao diz que o par esta errado, e nao remove nada. `Cydia pomonella` e mesmo a
carpocapsa. Ela diz uma coisa so, e verificavel: **o nome publicado nao e o nome
que o documento escreve**, e por isso a afirmacao nao pode receber o mesmo selo
de quem volta ao papel palavra por palavra.

Nao e o inverso de R-13 tambem: R-13 pergunta se o texto do ALVO DE UMA LINHA DE
DOSE existe no documento; esta pergunta e sobre o NOME NORMALIZADO do par de uso.
"""
import argparse, json, os, re, subprocess, sys, unicodedata
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from selo import selo, gravar
from collections import Counter


def sa(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()


def nz(s):
    return re.sub(r'\s+', ' ', sa(s)).strip()


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
    return nz(' || '.join(partes))


# Palavras que seguem o nome do alvo e NAO sao qualificador: ligacao, pontuacao
# e o comeco da proxima entrada da lista. Fechada e medida sobre o acervo.
NAO_QUALIFICA = {'', 'e', 'o', 'a', 'ed', 'di', 'del', 'della', 'dei', 'delle',
                 'in', 'su', 'contro', 'con', 'per', 'da', 'dal', 'alla', 'al',
                 # medidos no acervo: seguem o nome do alvo e nao qualificam praga
                 # nenhuma. 'quando' vem de 018101 MORAINE, "post-emergenza delle
                 # infestanti quando la coltura ha raggiunto la terza foglia".
                 'quando', 'nel', 'nei', 'nelle', 'sui', 'sulle', 'dopo', 'prima',
                 'oppure', 'anche', 'come', 'se', 'che', 'non'}

# Comprimentos em que o extrator CORTA a celula como escrita. Medidos sobre os
# 5.746 campos CROP_AS_WRITTEN/TARGET_AS_WRITTEN: 728 tem exatamente 80
# caracteres, 661 exatamente 180 e 509 exatamente 200. Nao e o documento que
# escreve assim; e regua do extrator.
CORTES_DO_EXTRATOR = {80, 180, 200}


def radical(w):
    """A mesma raiz de R-14 e R-21: corta a ultima vogal e o h de apoio."""
    w = re.sub(r'[^a-z]', '', sa(w))
    if len(w) >= 5:
        r = re.sub(r'h?[aeiou]$', '', w)
        if len(r) >= 4:
            return r
    return w


_RAIZES = {}


def raizes_do_texto(reg, t):
    if reg not in _RAIZES:
        _RAIZES[reg] = {radical(w) for w in re.findall(r"[a-z']+", t)}
    return _RAIZES[reg]


def qualificadores(nome, bruto):
    """Palavras que SEMPRE acompanham o nome do alvo na celula como escrita.

    So devolve alguma coisa quando o nome NUNCA aparece sozinho. Uma unica
    ocorrencia solta ja significa que a etichetta usa o nome curto, e ai nao ha
    qualificador a declarar.

    E NAO DEVOLVE NADA QUANDO O QUALIFICADOR E O RESTO DE UM CORTE.

    Medido, e e um defeito que esta regra criou na rodada 4: em 008601 FOLPAN 80
    WDG, 013012, 017111, 017311 e 011501 a tela chegou a escrever "a etichetta
    nunca escreve este alvo sozinho: sempre MUFFA g". O documento escreve "Muffa
    grigia (Botrytis cinerea)"; o `g` e o que sobrou de um TARGET_AS_WRITTEN
    cortado em exatamente 180 caracteres. Afirmar que a etichetta escreve "Muffa
    g" e uma afirmacao sobre o documento que o documento contradiz — a classe de
    erro que esta regra existe para nao cometer.
    O guarda: se a celula como escrita tem um dos comprimentos de corte do
    extrator E o qualificador e a ultima coisa dela, nao ha como saber se ele
    esta inteiro. Medido no acervo: mata 7 (4x 'g', 1x 'gr', 2x 'grigia' — este
    ultimo completo, mas indistinguivel de um corte) e deixa passar 749,
    incluindo os 85 'bianca', que sao o achado que importa.
    """
    b = nz(bruto)
    n = nz(nome)
    if not b or not n or ' ' in n or len(n) < 4:
        return []
    # casa o nome com flexao de vogal final (mosca/mosche, nottua/nottue)
    rx = re.compile(r'\b' + re.escape(n[:-1]) + r'[a-z]{0,2}\b([^a-z]*)([a-z]+)?')
    seg = []
    for m in rx.finditer(b):
        entre, prox = m.group(1) or '', m.group(2) or ''
        # so conta como qualificador o que vem depois de UM espaco simples
        if entre != ' ' or prox in NAO_QUALIFICA:
            return []          # apareceu sozinho, ou seguido de pontuacao
        seg.append(prox)
    if not seg:
        return []
    fim = sorted(set(seg))
    if len(str(bruto or '')) in CORTES_DO_EXTRATOR and b.endswith(' '.join(fim)):
        return []
    return fim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pares', default='v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json')
    ap.add_argument('--pdfs', default='pilot-label-intelligence/labels/pdf')
    ap.add_argument('--cache', default='/tmp/nomecache')
    ap.add_argument('--out', default='v1/dados/ALVO-NOMEADO.json')
    a = ap.parse_args()

    pares = json.load(open(a.pares, encoding='utf-8'))['PAIRS']
    ver, det, qual = {}, [], {}
    cont = Counter()
    memo, ordem = {}, {}
    for x in pares:
        reg = x['REGISTRATION_ID']
        i = ordem[reg] = ordem.get(reg, -1) + 1
        chave = f'{reg}#{i}'
        if reg not in memo:
            memo[reg] = leituras(reg, a.pdfs, a.cache)
        t = memo[reg]
        nome = nz(str(x['TARGET']).replace('_', ' '))
        partes = [p for p in nome.split() if len(p) >= 4]
        qual[chave] = qualificadores(nome, x.get('TARGET_AS_WRITTEN'))
        if not t:
            est = 'TARGET_NAME_NOT_CHECKED'
        elif nome and (nome in t or (partes and all(p in t for p in partes))):
            est = 'TARGET_NAME_LITERAL'
        elif partes and all(radical(q) in raizes_do_texto(reg, t) for q in partes):
            est = 'TARGET_NAME_INFLECTED_IN_LABEL'
        else:
            est = 'TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL'
            det.append({'KEY': chave, 'REGISTRATION_ID': reg, 'PRODUCT': x.get('PRODUCT'),
                        'CROP': x['CROP'], 'TARGET': x['TARGET'], 'ROUTE': x['ROUTE'],
                        'TARGET_AS_WRITTEN': str(x.get('TARGET_AS_WRITTEN'))[:240],
                        'PROOF': (f'a palavra "{nome}" nao aparece em nenhuma das tres leituras '
                                  f'do PDF oficial. O nome publicado vem de taxonomia, nao do '
                                  f'documento')})
        ver[chave] = est
        cont[est] += 1

    saida = {
        'DATASET': 'V1-ALVO-NOMEADO',
        'PRODUCED_BY': selo(__file__),
        'RULE_ID': 'R-17',
        'O_QUE_ISTO_E': ('o nome do alvo que a ferramenta publica esta escrito no rotulo?'),
        'O_QUE_ISTO_NAO_E': ('nao diz que o par esta errado e nao remove nada: Cydia pomonella '
                             'e mesmo a carpocapsa. Diz que o NOME nao volta ao documento'),
        'READINGS': 'pdftotext em tres modos (fluxo, -layout, -raw)',
        'PAIRS': len(pares),
        'COUNTS': dict(cont.most_common()),
        'QUALIFIER_NOTA': ('palavras que SEMPRE acompanham o nome do alvo na celula como '
                           'escrita. Nao e acusacao: "sensibili" nao muda a praga, '
                           '"lineatella" confirma a especie e "bianca" muda o inseto, e '
                           'distinguir os tres precisa de entomologia que nao esta aqui. '
                           'Vai para a tela ao lado do nome, como crop_scope'),
        'TARGETS_ALWAYS_QUALIFIED': sum(1 for v in qual.values() if v),
        'VERDICT': ver,
        'QUALIFIER': {k: v for k, v in qual.items() if v},
        'NOT_IN_LABEL': det,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    gravar(saida, a.out)
    for k, v in cont.most_common():
        print(f'  {v:5}  {k}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
