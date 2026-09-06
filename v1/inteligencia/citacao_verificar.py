#!/usr/bin/env python3
"""
citacao_verificar.py — R-18. Toda frase que a ferramenta imprime ENTRE ASPAS tem
de existir no documento.

## Por que isto e uma regra e nao uma revisao de texto

A ferramenta usa aspas com um verbo: "o rotulo escreve", "a linha de dose fala
de", "a etichetta poe teto". Aspas com esse verbo sao uma afirmacao sobre o
documento — a mais forte que ela faz, porque convida quem le a ir conferir. Uma
citacao remontada e pior do que um numero errado: o numero errado se descobre
comparando, a citacao inventada manda a pessoa procurar no PDF uma frase que nao
esta la, e o que ela conclui e que o PDF e que esta errado.

A rodada 3 achou dois casos e os dois eram desta familia:

  * **SF-12** — a gaveta de dose cita "...ravanello, zucchino sedano" em 318
    doses publicadas. Nas coordenadas da fonte a celula "Orticole" termina em
    "zucchino" e "sedano" e celula PROPRIA, com linha e dose proprias. A string
    "zucchino sedano" nao existe no documento;
  * **SF-07** — a ficha de 004701 imprime, sob "O que o rotulo escreve:", quatro
    aspas, e duas delas sao "tranne spinacio". A etichetta exclui espinafre
    **baby leaf** e acelga **baby leaf**. O recorte inverte a relacao de escopo,
    de estreito para largo, e passa num teste de literalidade porque E substring
    verbatim — so que truncada no ponto errado.

## A regra, e por que ela e DIFERENTE por familia

Cada citacao e conferida contra o documento lido de quatro formas (coluna
reconstruida por fios verticais, `-layout`, fluxo e `-raw`), porque uma frase
partida entre colunas numa leitura costuma estar inteira noutra.

Mas nem toda citacao e uma FRASE, e tratar as tres como uma so foi a primeira
versao desta regra — que acusou 846 "truncamentos" e estava errada:

  * **FRASE** (janela de exclusao, teto de dose, nota de restricao, frase de
    sucessao, frase de retirada, vigencia declarada). E prosa do rotulo. Aqui
    nao basta existir — mas tambem NAO se cobra que termine em ponto: a segunda
    versao desta regra cobrava, e acusou 175 "truncamentos" que eram so linhas
    de lista terminando onde a linha termina. Inventar defeito e o mesmo pecado
    que esconder um.

    O que SF-07 descreve e mais estreito e e medivel: a citacao e um PREFIXO
    ESTRITO de outra citacao mais longa, da mesma familia e do mesmo rotulo.
    Em `004701` a ficha imprime quatro aspas sob "O que o rotulo escreve:" e
    duas sao "tranne spinacio", enquanto a quarta e "tranne spinacio baby leaf e
    bietola da foglia baby leaf". A curta e substring verbatim e mesmo assim
    mente: a etichetta exclui espinafre BABY LEAF, nao espinafre. O prefixo
    inverte a relacao de escopo, de estreito para largo.

    E o corte NO MEIO DE UMA PALAVRA continua sendo defeito, porque ai a
    "citacao" nem palavra e;
  * **CELULA** (a celula de cultura e a de alvo da tabela de dose). Uma celula
    termina onde a celula termina, e quase nunca em pontuacao — cobrar pontuacao
    dela seria inventar defeito. Aqui vale so a existencia: a celula tem de
    aparecer CONTIGUA em alguma leitura. Se nao aparece, ela foi montada com
    pedaco de mais de uma celula, que e o defeito de `SF-12`;
  * **LINHA DE TABELA** (`SOURCE_QUOTE`). Uma linha lida da esquerda para a
    direita atravessa colunas e **nunca** e contigua no texto linearizado. Exigir
    contiguidade dela seria acusar a tabela de nao ser uma frase. Aqui a
    pergunta e outra: todas as palavras da linha existem na PAGINA dela? Se
    existem, a linha e uma remontagem honesta de celulas reais; e a tela tem de
    dizer que e remontagem, e nao "citacao do documento".

    QUOTE_VERBATIM                     existe, literal e contigua
    QUOTE_NOT_CONTIGUOUS_IN_DOCUMENT   nao existe contigua em leitura nenhuma
    QUOTE_IS_PREFIX_OF_LONGER_QUOTE    e prefixo estrito de outra do mesmo
                                       rotulo — pode inverter escopo (so FRASE)
    QUOTE_CUT_MID_WORD                 o corte caiu dentro de uma palavra
    QUOTE_HAS_UNBALANCED_PARENTHESIS   abre parentese e nao fecha (ou o inverso):
                                       a celula continua na linha seguinte
    QUOTE_CUT_MID_LINE                 acaba no meio de uma linha do documento,
                                       com mais palavras da mesma linha depois
    ROW_RECONSTRUCTED_FROM_CELLS       linha de tabela, palavras todas na pagina
    ROW_HAS_WORDS_NOT_ON_THE_PAGE      linha de tabela com palavra que nao esta

O casco nao pode imprimir com o verbo "o rotulo escreve" nada que nao seja
`QUOTE_VERBATIM`. Para o resto ha nome proprio, e o nome diz o que aconteceu.

## O que a rodada 4 achou aqui, e era o buraco maior

Duas coisas, as duas na ligacao entre este modulo e o casco:

1. **AS DUAS MAIORES FAMILIAS NAO ESTAVAM NA LISTA.** A tela imprime, ao lado
   de cada par de uso, `o rotulo escreve: "..."` com o `CROP_AS_WRITTEN` e o
   `TARGET_AS_WRITTEN` — 2.873 frases de cada, com verbo de citacao, e nenhuma
   tinha passado por aqui. Medido agora:

       PAIR_CROP_AS_WRITTEN     1.465 verbatim · 670 cortada no meio de palavra
                                461 nao contigua · 277 curta demais
       PAIR_TARGET_AS_WRITTEN   1.934 verbatim · 621 cortada no meio de palavra
                                235 nao contigua ·  83 curta demais

   1.408 celulas de cultura e 939 de alvo saiam entre aspas sem ser literais.

2. **AUSENCIA DE REGISTRO VIRAVA APROVACAO.** Este modulo publicava so `DETAIL`,
   a lista das REPROVADAS, e o casco lia com `.get(chave, "QUOTE_VERBATIM")`.
   As 349 `ROW_RECONSTRUCTED_FROM_CELLS` e as 163 `QUOTE_TOO_SHORT_TO_CHECK`
   nunca estiveram na lista de falhas e por isso saiam como "Citacao do
   documento" — 512 selos por valor default. E a chave era a frase cortada em
   200 caracteres, cortada AQUI sobre o texto cru e LA sobre o texto
   normalizado: as citacoes longas nunca casavam e caiam no default em silencio.

   Agora sai `VERDICT` com TODAS as citacoes, a chave e o sha1 da frase
   normalizada, e o default do casco e `QUOTE_NOT_CHECKED`.

## DEPENDENCIA CIRCULAR, declarada

Este modulo LE `CASCO-PAYLOAD.json` para saber quais frases o casco imprime, e o
casco LE a saida deste modulo para saber quais pode citar. Na esteira, este roda
ANTES do casco — entao ele confere as frases do payload ANTERIOR. Se o conjunto
de pares mudar entre uma execucao e outra, as frases novas nao terao veredito e
o casco as marcara `QUOTE_NOT_CHECKED`, que e o lado seguro: a frase nova nao
recebe aspas ate alguem conferi-la. Duas execucoes seguidas da esteira fecham o
ciclo. Isto esta escrito porque um leitor que veja `QUOTE_NOT_CHECKED` numa
frase obviamente literal merece saber que a causa pode ser a ordem da esteira, e
nao o documento.
"""
import argparse, hashlib, json, os, re, subprocess, sys, unicodedata
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def nz(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'\s+', ' ', s).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--payload', default='v1/dados/CASCO-PAYLOAD.json')
    ap.add_argument('--pdfs', default='pilot-label-intelligence/labels/pdf')
    ap.add_argument('--bbox', default='/tmp/bboxcache')
    ap.add_argument('--fios', default='/tmp/fioscache')
    ap.add_argument('--cache', default='/tmp/nomecache')
    ap.add_argument('--bin', default='pilot-label-intelligence/bin')
    ap.add_argument('--out', default='v1/dados/CITACAO-CHECK.json')
    a = ap.parse_args()
    sys.path.insert(0, a.bin)
    import fios as F
    from prosa_escopo import texto_por_coluna, caixas
    os.makedirs(a.fios, exist_ok=True)
    os.makedirs(a.cache, exist_ok=True)

    memo = {}

    def leituras(reg):
        """As quatro leituras do documento, normalizadas."""
        if reg in memo:
            return memo[reg]
        pdf = os.path.join(a.pdfs, f'{reg}.pdf')
        out = []
        if os.path.exists(pdf):
            try:
                for pi, pg in enumerate(caixas(pdf, a.bbox)):
                    r = F.fios(pdf, pi + 1, cache=a.fios)
                    out += [nz(c) for c in texto_por_coluna(
                        pg, r.get('V') or [], r.get('PAGE_WIDTH_PT') or 0)]
            except Exception:
                pass
            for modo, suf in (([], 'fluxo'), (['-layout'], 'layout'), (['-raw'], 'raw')):
                f = os.path.join(a.cache, f'{reg}.{suf}.txt')
                if not os.path.exists(f) or os.path.getsize(f) == 0:
                    try:
                        subprocess.run(['pdftotext'] + modo + [pdf, f], check=True,
                                       capture_output=True, timeout=180)
                    except Exception:
                        continue
                try:
                    out.append(nz(open(f, encoding='utf-8', errors='replace').read()))
                except OSError:
                    pass
        memo[reg] = out
        return out

    # A LEITURA COM A ESTRUTURA DE LINHA PRESERVADA, so para uma pergunta: o
    # corte caiu no MEIO DE UMA LINHA do documento?
    memo_l = {}

    def layout(reg):
        if reg in memo_l:
            return memo_l[reg]
        f = os.path.join(a.cache, f'{reg}.layout.txt')
        t = ''
        if os.path.exists(f):
            t = unicodedata.normalize('NFD', open(f, encoding='utf-8', errors='replace').read())
            t = ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()
            # espaco simples vira espaco; quebra de linha e salto de coluna viram
            # o mesmo marcador de FRONTEIRA, que e o que interessa aqui
            t = re.sub(r'\n|   +', '\x00', t)
            t = re.sub(r'[ \t]+', ' ', t)
        memo_l[reg] = t
        return t

    def confere(reg, frase, tipo, minimo=8):
        f = nz(frase)
        if not f or len(f) < minimo:
            return 'QUOTE_TOO_SHORT_TO_CHECK'
        # PARENTESE ABERTO E NUNCA FECHADO E UM CORTE, NAO UMA CELULA.
        #
        # Medido em 012878 e 015317: a coluna tem tres linhas visuais —
        # "della vite", "(Plasmopara" e "Viticola)" — e o alvo publicado e
        # "Peronospora della vite (Plasmopara". A frase EXISTE contigua no
        # documento (as duas primeiras linhas), entao todos os testes de
        # existencia a aprovam; o que denuncia o corte e o parentese. A celula
        # verdadeira acaba em "Viticola)", e o que sobrou nao e a celula.
        #
        # Nao e heuristica de conteudo: um parentese aberto sem fechar e uma
        # afirmacao sintatica sobre o proprio texto citado, verificavel sem
        # conhecer o assunto. E o inverso tambem conta — fechar sem abrir e o
        # mesmo corte, do outro lado.
        if f.count('(') != f.count(')'):
            return 'QUOTE_HAS_UNBALANCED_PARENTHESIS'
        ls = leituras(reg)
        if not ls:
            return 'QUOTE_NOT_CHECKED_NO_TEXT'
        if tipo == 'LINHA':
            # uma linha de tabela nao e contigua por construcao: a pergunta e se
            # as palavras dela existem no documento
            faltam = [w for w in re.findall(r'[a-z]{4,}', f)
                      if not any(w in t for t in ls)]
            return ('ROW_RECONSTRUCTED_FROM_CELLS' if not faltam
                    else 'ROW_HAS_WORDS_NOT_ON_THE_PAGE')
        if not any(f in t for t in ls):
            return 'QUOTE_NOT_CONTIGUOUS_IN_DOCUMENT'
        # CORTE NO MEIO DA LINHA. O documento tem estrutura: uma celula acaba
        # onde acaba a coluna (salto de 3+ espacos no -layout) ou onde a linha
        # quebra. Se a citacao acaba no MEIO de uma linha, com mais palavras da
        # mesma linha logo depois, o que a cortou foi o extrator e nao o
        # documento.
        #
        # Medido, e e o defeito de maior volume desta camada: os campos
        # CROP_AS_WRITTEN e TARGET_AS_WRITTEN vem cortados por COMPRIMENTO FIXO
        # — 728 deles tem exatamente 80 caracteres, 661 exatamente 180 e 509
        # exatamente 200. Isso e regua do extrator, nao do papel, e a tela
        # imprimia tudo isso com "o rotulo escreve".
        tl = layout(reg)
        if tl:
            i, cortou = tl.find(f), None
            while i >= 0:
                d = tl[i + len(f): i + len(f) + 2]
                # fronteira de verdade: fim do texto, quebra/coluna, ou pontuacao
                # que termina frase logo em seguida
                fim = (not d) or d[0] == '\x00' or d[0] in '.;:' or (
                    d[0] == ' ' and len(d) > 1 and d[1] == '\x00')
                cortou = (cortou is not False) and not fim
                i = tl.find(f, i + 1)
            if cortou:
                return 'QUOTE_CUT_MID_LINE'
        if f[-1].isalpha():
            # o corte caiu dentro de uma palavra? (a letra seguinte, em TODAS as
            # ocorrencias, continua a palavra)
            cortes = []
            for t in ls:
                i = 0
                while True:
                    i = t.find(f, i)
                    if i < 0:
                        break
                    seg = t[i + len(f): i + len(f) + 1]
                    cortes.append(bool(seg) and seg.isalpha())
                    i += 1
            if cortes and all(cortes):
                return 'QUOTE_CUT_MID_WORD'
        return 'QUOTE_VERBATIM'

    pay = json.load(open(a.payload, encoding='utf-8'))
    fam = {}
    det = []
    # VEREDITO DE TODAS AS CITACOES, E NAO SO DAS REPROVADAS.
    #
    # Ate a rodada 4 este modulo publicava so a lista das que falharam, e o
    # casco lia essa lista com `.get(chave, 'QUOTE_VERBATIM')`. Ausencia de
    # registro virava afirmacao positiva — e as 163 QUOTE_TOO_SHORT_TO_CHECK e
    # as 349 ROW_RECONSTRUCTED_FROM_CELLS, que NUNCA estiveram na lista de
    # falhas, saiam na tela como "Citacao do documento". 512 citacoes com o selo
    # errado por causa de um valor default.
    #
    # A chave e o sha1 da frase JA NORMALIZADA, e nao a frase cortada em 200
    # caracteres: o corte era feito aqui sobre o texto cru e no casco sobre o
    # texto normalizado, entao as 35 citacoes de 200+ caracteres nunca casavam
    # e caiam no default silenciosamente.
    ver = {}

    def chave_cit(nome, reg, frase):
        return f'{nome}|{reg}|' + hashlib.sha1(nz(frase).encode()).hexdigest()[:16]

    def reg_fam(nome, tipo, itens):
        c = Counter()
        # SF-07 · uma citacao que e PREFIXO ESTRITO de outra do mesmo rotulo e da
        # mesma familia inverte escopo. Medido por familia, nao suposto.
        porreg = {}
        for reg, frase, _o in itens:
            porreg.setdefault(reg, set()).add(nz(frase))
        for reg, frase, onde in itens:
            e = confere(reg, frase, tipo)
            if e == 'QUOTE_VERBATIM' and tipo == 'FRASE':
                f = nz(frase)
                if any(o != f and o.startswith(f) for o in porreg.get(reg, ())):
                    e = 'QUOTE_IS_PREFIX_OF_LONGER_QUOTE'
            c[e] += 1
            ver[chave_cit(nome, reg, frase)] = e
            if e in ('QUOTE_NOT_CONTIGUOUS_IN_DOCUMENT', 'QUOTE_IS_PREFIX_OF_LONGER_QUOTE',
                     'QUOTE_CUT_MID_WORD', 'ROW_HAS_WORDS_NOT_ON_THE_PAGE',
                     'QUOTE_HAS_UNBALANCED_PARENTHESIS', 'QUOTE_CUT_MID_LINE'):
                det.append({'FAMILY': nome, 'TYPE': tipo, 'REGISTRATION_ID': reg, 'STATE': e,
                            'WHERE': onde, 'QUOTE': str(frase)[:200]})
        fam[nome] = dict(c.most_common())

    reg_fam('DOSE_CROP_CELL', 'CELULA', [(p['reg'], d.get('crop'), 'gaveta de dose · celula de cultura')
                               for p in pay['products'] for d in (p.get('doses') or [])])
    reg_fam('DOSE_TARGET_CELL', 'CELULA', [(p['reg'], d.get('target'), 'gaveta de dose · celula de alvo')
                                 for p in pay['products'] for d in (p.get('doses') or [])])
    reg_fam('DOSE_SOURCE_QUOTE', 'LINHA', [(p['reg'], d.get('quote'), 'gaveta de dose · citacao')
                                  for p in pay['products'] for d in (p.get('doses') or [])
                                  if d.get('quote') and d['quote'] != 'NOT_PRESERVED'])
    # AS DUAS FAMILIAS QUE FALTAVAM, E ERAM AS MAIORES.
    #
    # A tela imprime, ao lado de cada par de uso, `o rotulo escreve: "..."` com
    # o CROP_AS_WRITTEN e o TARGET_AS_WRITTEN — 2.873 frases com verbo de
    # citacao que R-18 nunca tinha olhado. Elas vem da remontagem de celula do
    # extrator e sao cortadas por comprimento, entao a suspeita de que muitas
    # nao existem contiguas no documento nao e teorica.
    reg_fam('PAIR_CROP_AS_WRITTEN', 'CELULA',
            [(p['reg'], u.get('crop_raw'), 'par de uso · celula de cultura como escrita')
             for p in pay['products'] for u in (p.get('uses') or [])
             if u.get('crop_raw') and u['crop_raw'] != 'NOT_PRESERVED'])
    reg_fam('PAIR_TARGET_AS_WRITTEN', 'CELULA',
            [(p['reg'], u.get('target_raw'), 'par de uso · celula de alvo como escrita')
             for p in pay['products'] for u in (p.get('uses') or [])
             if u.get('target_raw') and u['target_raw'] != 'NOT_PRESERVED'])
    reg_fam('EXCLUSION_WINDOW', 'FRASE', [(p['reg'], w.get('TEXT'), 'ficha · janela de exclusao')
                                 for p in pay['products'] for w in (p.get('exclusion_windows') or [])
                                 if w.get('QUOTABLE')])
    reg_fam('CEILING_LITERAL', 'FRASE', [(p['reg'], t.get('LITERAL'), 'ficha · teto de dose')
                                for p in pay['products'] for t in (p.get('ceilings') or [])])
    reg_fam('APP_LIMIT_NOTE', 'FRASE', [(p['reg'], n.get('TEXT'), 'ficha · restricao fora da tabela')
                               for p in pay['products'] for n in (p.get('label_app_limit_notes') or [])])
    reg_fam('ROTATION_TEXT', 'FRASE', [(p['reg'], w.get('ROTATION_TEXT'), 'ficha · frase de sucessao')
                              for p in pay['products'] for w in (p.get('uses_rotacao') or [])])
    reg_fam('WITHDRAWAL_TEXT', 'FRASE', [(p['reg'], w.get('EXCLUSION_TEXT'), 'ficha · frase que retirou o uso')
                                for p in pay['products'] for w in (p.get('uses_retirados') or [])])
    reg_fam('LABEL_VALIDITY_QUOTE', 'FRASE', [(p['reg'], p.get('label_validity_quote'), 'ficha · vigencia')
                                     for p in pay['products']
                                     if p.get('label_validity_quote') not in
                                     (None, 'NOT_PRESENT', 'NOT_CHECKED')])

    tot = Counter()
    for c in fam.values():
        tot.update(c)
    saida = {
        'DATASET': 'V1-CITACAO-CHECK',
        'RULE_ID': 'R-18',
        'O_QUE_ISTO_E': 'toda frase que a ferramenta imprime entre aspas existe no documento?',
        'O_QUE_ISTO_NAO_E': ('nao julga se a frase e relevante nem se o fato esta certo: julga '
                             'se ela esta escrita no PDF oficial'),
        'READINGS': 'coluna reconstruida por fios + pdftotext -layout, fluxo e -raw',
        'TOTAL': dict(tot.most_common()),
        'BY_FAMILY': fam,
        'KEY': ('FAMILIA|REGISTRO|sha1(frase normalizada)[:16]. A frase normalizada e a '
                'mesma nz() deste modulo: sem acento, minuscula, espacos colapsados'),
        'VERDICT': ver,
        'DETAIL': det,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in fam.items():
        print(f'  {k:22} {v}', file=sys.stderr)
    print(f'\n  TOTAL {dict(tot.most_common())}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
