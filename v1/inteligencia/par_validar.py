#!/usr/bin/env python3
"""
par_validar.py — o PAR DE USO tambem tem de sobreviver aos fios desenhados.

## O defeito que este modulo fecha

A rodada 2 do red team achou os erros na camada de DOSE e os consertos foram
aplicados na camada de dose: `cultura_validar.py` (R-11) confere a cultura da
LINHA DE DOSE, `teto_dose.py` (R-12) o teto DA DOSE, `alvo_literal.py` (R-13) o
alvo DA LINHA DE DOSE. Nenhum dos tres foi aplicado a camada de PARES DE USO —
que e a afirmacao regulatoria mais fundamental das duas, porque diz o que o
produto **pode ser usado para**, e nao quanto se aplica.

O resultado, medido pelo arbitro da rodada 3 com um porte independente de R-11:
dos pares publicados, dezenas eram **uso que a etichetta nao autoriza**, todos
com o selo verde `TABELA` — a classe de evidencia mais forte da tela. Pior, a
legenda da mesma tela anunciava quantas linhas de DOSE tinham sido descartadas
por R-11, e o leitor concluia que o que sobrou tinha sobrevivido aos fios. As
linhas de PAR nunca tinham sido submetidas a fio nenhum.

    R-11 tirou o NUMERO de TABACCO x CIMICI e deixou de pe a AFIRMACAO DE USO.

## A regra: a CELULA DESENHADA da cultura, e o que cabe dentro dela

R-11 pergunta se um fio separa a linha de dose da cultura dela. Aqui a pergunta
e a mesma, feita do outro lado: **a celula desenhada que contem o nome da
cultura contem tambem um glifo do alvo?**

Para cada ocorrencia do nome da cultura na pagina:

  1. juntam-se os fios desenhados que ATRAVESSAM a coluna daquela palavra
     (>= 60% da largura dela, o mesmo criterio de `fios.mesma_celula`), fundindo
     os riscos que o raster detecta duas vezes. Sao precisos **tres** deles:
     duas bordas fecham uma celula, a terceira prova que a coluna tem mais de
     uma — que e o que separa uma grade de um titulo riscado;
  2. o fio imediatamente acima e o imediatamente abaixo dao a **banda y da
     celula** (o topo e o fim da pagina fecham a primeira e a ultima), e a
     extensao x deles diz **ate onde vai a tabela** naquela altura;
  3. a celula so vale se ela **descreve o texto que esta dentro dela**: se
     alguma linha que comeca dentro da tabela termina fora dela, o que foi lido
     como grade e sublinhado de titulo, e o teste nao se aplica;
  4. o par sobrevive se algum glifo do alvo cai dentro da banda y **e** dentro
     da faixa x da tabela.

O teste em x nao e detalhe: numa etichetta em paisagem ha duas tabelas lado a
lado, e sem ele o alvo da tabela da esquerda "salva" um par da tabela da
direita so por estar na mesma altura da folha. Medido em 012573.

Como em R-11, o criterio e **conservador**: basta UMA ocorrencia da cultura com
UM glifo do alvo dentro da sua celula para o par sobreviver, e qualquer sinal de
que o desenho nao e o que a regra supoe faz o modulo se abster em vez de
condenar. Sao CINCO abstencoes com nome proprio, escritas no codigo ao lado da
linha que as aplica — e cada uma vem com quantas vezes ela DISPARA no censo:

    ROUTE_NOT_GEOMETRIC          1.056   a rota nao afirma ter lido tabela
    ANCHOR_NOT_FOUND               258   cultura e alvo nunca na mesma pagina
    NO_DRAWN_CELL                  112   convivem, mas a coluna nao e riscada
    CROP_ALSO_OUTSIDE_TABLE        106   parte das ocorrencias fora de celula,
                                         e o alvo NAO tem outro dono
    TABLE_NOT_DESCRIBING_ITS_TEXT   58   a grade existe e nao descreve o texto
    CROP_NAME_NOT_THE_ANCHOR        13   a celula fechou pelo TITULO do grupo
    TARGET_UNDER_CROP_HEADER         0   <- CODIGO MORTO NO ACERVO DE HOJE

A ultima linha e uma correcao de uma afirmacao anterior deste proprio docstring,
que dizia "quatro abstencoes, todas medidas contra um caso real do acervo". O
ramo de TARGET_UNDER_CROP_HEADER existe e foi escrito contra 010587 FOLPAN SC,
mas nesse rotulo o par cai antes, em CROP_ALSO_OUTSIDE_TABLE: nas 47
condenacoes o ramo nunca chega a ser exercido (em 38 nao ha glifo do alvo abaixo
da celula na mesma faixa x; nos 9 de 012573 o `titulo_entre` bloqueia com
titulos reais em caixa alta). Ele fica no codigo porque a situacao que ele trata
e real e pode voltar com outro acervo — mas "medido contra um caso real" era
verdade sobre o CODIGO e nao sobre o CENSO, e as duas coisas nao sao a mesma.

E o modulo **nao depende de `PAGE`**: 1.427 dos 2.928 pares nao preservaram a
pagina, e amarrar o teste a ela deixaria de fora justamente 012573 (MF-02), onde
o vazamento e maior. Procurar em todas as paginas so aumenta as chances de
ABSOLVER.

## O que foi medido com esta regra

49 pares contraditos. Os 47 primeiros estao na lista que o arbitro da rodada 3
mediu por conta propria, com outro instrumento e a partir de coordenadas que este
repositorio nao tem; os outros 2 sao de mecanismo diferente e vieram da rodada 4
(TARGET_BELONGS_TO_ANOTHER_CROP_CELL, ver `alvo_tem_outro_dono`):

    018067 MAXENTIS · 019095 KOJAMI   SEGALE x OIDIO. A tabela empilha ORZO
                               (que tem OIDIO), SEGALE (que tem Rincosporiosi
                               e Ruggine) e TRITICALE. O par sobrevivia pela
                               palavra "segale" na LINHA DE TITULO do produto,
                               fora de celula nenhuma.

E os 47 da rodada 3, por CROP_CELL_DOES_NOT_CONTAIN_TARGET:

    012573 EKO OIL SPRAY  18   BARBABIETOLA fica com os 4 alvos que a etichetta
                               lhe da e CARCIOFO com os 6 — os 18 restantes sao
                               os "18 alvos falsos num unico rotulo" de MF-02
    015232 · 017358 · 017824   4 cada: CETRIOLO/ZUCCHINO x ELMINTOSPORIOSI,
                               AGLIO/CIPOLLA x OIDIO
    015275 DURAVIS · 017687 ELTIRA  4 cada: + TABACCO x DORIFORA
    008259 · 013560 · 013590   3 cada: TABACCO x CIMICI,
                               BARBABIETOLA/ERBA_MEDICA x DIABROTICA

E zero contradicao nos rotulos de controle: 014386 OLIONET (que le a MESMA frase
de 012573 e acerta), 008102 MERPAN e 010587 FOLPAN SC (prosa com cabecalho
sublinhado, onde a regra se abstem em vez de apagar uso verdadeiro).

## O que este modulo NAO faz

Nao le rotulo novo, nao corrige a cultura, nao adivinha o par certo e nao
descobre qual seria o alvo verdadeiro. Ele diz uma coisa so: que o par
publicado **nao sobrevive ao documento**. Quem tira o par da tela e o payload.

    PARSER_FAILURE != REGULATORY_ABSENCE — um par que este teste nao consegue
    conferir sai como NOT_CHECKABLE com o nome proprio, nunca como aprovado.

Saida: PARES-FIOS-CHECK.json, com um veredito por chave `reg#i` e a coordenada
que o sustenta.
"""
import argparse, json, os, re, sys
from collections import Counter

RXP = re.compile(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', re.S)
RXW = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>')

# Fracao da largura da palavra que um fio precisa cruzar para contar como
# borda da celula dela. Mesmo valor de fios.mesma_celula, pelo mesmo motivo:
# fio que so encosta na borda nao separa nada.
COBRE = 0.6

# ROTAS que este teste pode condenar. Sao as que afirmam ter lido uma TABELA
# ou um cabecalho de bloco dentro dela — as unicas em que "a celula desenhada
# nao contem este alvo" e uma afirmacao sobre o documento.
#
# HEADER_CONTINUATION e AUTHORISED_USE_LIST ficam de fora, e a medicao diz por
# que: os pares de AUTHORISED_USE_LIST sao herbicida com alvo generico
# ("INFESTANTI") e cultura vinda da linha de dose, e submete-los a geometria
# condenava 195 pares — quase todos os herbicidas do acervo — porque a palavra
# "infestanti" nao mora na celula da cultura. Isso nao e a etichetta
# contradizendo o par; e o teste sendo usado onde nao se aplica.
# ROUTE_NOT_GEOMETRIC e NOT_CHECKABLE, nunca aprovacao.
ROTAS_TESTAVEIS = {'GEOMETRIC_TABLE', 'MERGED_COLUMN_TABLE',
                   'INLINE_COLON_HEAD', 'INLINE_STATEMENT'}

PARADAS = {'de', 'da', 'del', 'della', 'dei', 'delle', 'degli', 'in', 'con', 'per',
           'su', 'al', 'alla', 'allo', 'ed', 'contro', 'sp', 'spp', 'periodo',
           'vegetativo', 'primavera', 'estate', 'autunno', 'inverno', 'uova'}


def so_letras(s):
    return re.sub(r'[^a-z]', '', str(s or '').lower())


# A ETICHETTA FLEXIONA E O VOCABULARIO NAO. Medido, nao suposto: em 014386 a
# celula de POMACEE escreve "Tignola" e o par publicado diz TIGNOLE; a de
# DRUPACEE escreve "uova di Lepidottero" e o par diz LEPIDOTTERI. Com casamento
# por token inteiro, os dois eram CONDENADOS por uma letra — e condenar uso
# verdadeiro e o erro caro nesta direcao, porque apaga fato regulatorio real.
#
# O italiano flexiona quase sempre na ULTIMA VOGAL (acaro/acari,
# afide/afidi, tignola/tignole, lepidottero/lepidotteri), as vezes com um h de
# apoio (mosca/mosche). O radical corta exatamente isso e nada mais. Palavra
# curta nao e cortada: "melo" viraria "mel" e passaria a casar coisa demais.
def radical(w):
    w = so_letras(w)
    if len(w) >= 5:
        r = re.sub(r'h?[aeiou]$', '', w)
        if len(r) >= 4:
            return r
    return w


def palavras(pdf, cache):
    """Caixas de palavra por pagina, via pdftotext -bbox-layout, com cache."""
    import subprocess
    os.makedirs(cache, exist_ok=True)
    alvo = os.path.join(cache, os.path.basename(pdf)[:-4] + '.xml')
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        subprocess.run(['pdftotext', '-bbox-layout', pdf, alvo],
                       check=True, capture_output=True, timeout=300)
    body = open(alvo, encoding='utf-8', errors='replace').read()
    return [[(float(x0), float(y0), float(x1), float(y1), t)
             for x0, y0, x1, y1, t in RXW.findall(b)] for _, _, b in RXP.findall(body)]


def raizes_cultura(crop, crop_raw):
    """Glifos que identificam a CULTURA na pagina.

    O par guarda a cultura normalizada ("BARBABIETOLA", "ERBA_MEDICA"); a
    etichetta escreve "Barbabietola da zucchero" ou "BARBABIETOLA". O primeiro
    segmento do nome normalizado casa os dois. A celula como escrita entra
    junto, quando ela existe e nao e uma descricao do proprio extrator
    ("linha de dose por cultura", "faixa y 102-111 da coluna de cultura").
    """
    out = []
    for parte in str(crop or '').split('_'):
        p = radical(parte)
        if len(p) >= 4:
            out.append(p)
            break
    bruto = str(crop_raw or '')
    if bruto and not re.search(r'linha de dose|faixa y|coluna de cultura', bruto, re.I):
        p = radical(bruto.split(',')[0].split('(')[0].strip().split()[0]
                    if bruto.split() else '')
        if len(p) >= 4 and p not in out:
            out.append(p)
    return out


def raizes_alvo(target):
    """Glifos que ancoram ESTE alvo na pagina — e so ele.

    A primeira versao juntava as palavras da celula como escrita
    (`TARGET_AS_WRITTEN`) as do nome normalizado. Foi medido e estava errado:
    em 012573 a celula de CARCIOFO escreve "Acari, Afidi, Aleurodidi, Ditteri,
    Tripidi", e essa mesma frase viaja no `TARGET_AS_WRITTEN` dos catorze pares
    de BARBABIETOLA. Com ela como ancora, o par BARBABIETOLA x ALEURODIDI era
    ABSOLVIDO por encontrar a palavra "Afidi" dentro da celula da barbabietola.
    A pergunta e se ESTE alvo esta na celula, entao a ancora tem de ser o nome
    DELE. Alvo que nao ocorre literalmente na pagina nao e condenado: sai como
    ancora nao encontrada, que e ignorancia com nome proprio.
    """
    out = []
    for parte in str(target or '').split('_'):
        p = radical(parte)
        if len(p) >= 4 and p not in PARADAS and p not in out:
            out.append(p)
    return out


# Quantos fios distintos precisam atravessar a coluna de uma palavra para ela
# estar dentro de uma TABELA, e nao debaixo de um sublinhado. Tres, porque duas
# bordas fecham UMA celula e a terceira prova que a coluna tem MAIS DE UMA — que
# e o que distingue uma grade de um titulo riscado. Medido nos dois sentidos:
#
#   * com um fio so, o cabecalho sublinhado "Melo, Cotogno, Pero, Nashi:" de
#     008102 MERPAN separava o titulo do seu proprio texto e a regra condenava
#     MELO x TICCHIOLATURA, que a etichetta autoriza na linha seguinte;
#   * exigindo fio ACIMA e ABAIXO, a primeira linha da tabela de 012573 — cuja
#     borda de cima e o proprio topo da pagina — ficava sem celula, e CARCIOFO
#     perdia os 6 alvos que a etichetta lhe da.
#
# Com a coluna riscada, o topo da pagina e o fim dela fecham a primeira e a
# ultima celula, e o sublinhado solto continua nao sendo celula nenhuma.
MIN_FIOS_NA_COLUNA = 3
JUNTA_FIO = 1.5      # pontos: dois riscos a menos que isto sao o MESMO fio


def fios_da_coluna(x0, x1, seg):
    """Fios que atravessam a coluna [x0,x1], agrupados por altura.

    Devolve [(y, x_ini, x_fim)] ja fundido: o raster detecta o mesmo risco em
    duas ou tres alturas vizinhas (0,48 pt de diferenca), e conta-las como fios
    distintos faria um sublinhado parecer uma grade.
    """
    larg = max(x1 - x0, 1e-6)
    cruz = sorted((y, xa, xb) for y, xa, xb in seg
                  if (min(x1, xb) - max(x0, xa)) / larg >= COBRE)
    out = []
    for y, xa, xb in cruz:
        if out and y - out[-1][0] <= JUNTA_FIO:
            out[-1] = (out[-1][0], min(out[-1][1], xa), max(out[-1][2], xb))
        else:
            out.append((y, xa, xb))
    return out


RX_CAIXA_ALTA = re.compile(r'^[A-ZÀ-Þ][A-ZÀ-Þ\'’-]{3,}$')


def titulo_entre(pg, y_de, y_ate, tx0, tx1, vocab):
    """Ha outro titulo de bloco entre a celula da cultura e o alvo?

    Titulo = palavra em CAIXA ALTA com 4+ letras, ou um nome do vocabulario de
    cultura do acervo. As duas formas foram medidas em 012573: "BARBABIETOLA"
    (que esta no vocabulario) e "ORNAMENTALI," (que nao esta, porque nunca virou
    par publicado — e nem por isso deixa de ser o titulo do bloco seguinte).
    """
    for x0, y0, x1, y1, t in pg:
        cy = (y0 + y1) / 2
        if not (y_de < cy < y_ate) or not (tx0 - 1 <= x0 <= tx1 + 1):
            continue
        limpo = t.strip().strip('.,;:()')
        if RX_CAIXA_ALTA.match(limpo) or radical(limpo) in vocab:
            return True
    return False


def celula_coerente(pg, topo, base, tx0, tx1, folga=2.0):
    """A celula desenhada realmente descreve o texto que esta dentro dela?

    UMA BORDA DE LINHA E, NO MINIMO, TAO LARGA QUANTO A LINHA QUE ELA FECHA.
    Um SUBLINHADO de titulo nao e: ele tem a largura das palavras sublinhadas e
    o texto embaixo passa muito dele.

    Medido em 010587 FOLPAN SC: a coluna da direita e prosa com cabecalhos
    sublinhados, e a "celula" de POMODORO tinha largura 556,8..696,96 enquanto
    as linhas dentro dela vao ate x=799,7. Pela geometria a ferramenta condenava
    POMODORO x ALTERNARIA, que a etichetta autoriza na linha seguinte
    ("...contro Peronospora (...), Alternaria (Alternaria solani)").

    Quando alguma linha transborda a largura da tabela, o que foi lido como
    grade nao e grade: e risco de titulo, e o teste nao se aplica.
    """
    linhas = {}
    for wx0, wy0, wx1, wy1, _t in pg:
        cy = (wy0 + wy1) / 2
        if not (topo < cy < base):
            continue
        k = round(cy, 1)
        a, b = linhas.get(k, (wx0, wx1))
        linhas[k] = (min(a, wx0), max(b, wx1))
    for a, b in linhas.values():
        # so conta a linha que COMECA dentro da tabela: texto de uma coluna
        # vizinha, a direita da grade, nao transborda coisa nenhuma — ele
        # simplesmente nao e desta tabela.
        if tx0 - folga <= a <= tx1 and b > tx1 + folga:
            return False
    return True


def alvo_tem_outro_dono(pgs, rc, rp, ra, voc_reg, segmentos, pdf):
    """TODO glifo deste alvo mora na celula desenhada de OUTRA cultura?

    A abstencao CROP_ALSO_OUTSIDE_TABLE existe por um motivo bom: parte das
    ocorrencias do nome da cultura esta fora de celula desenhada, e a
    autorizacao pode estar justamente numa delas — condenar com base so nas
    celulas seria afirmar sobre o que nao foi medido. Medido em 008102 MERPAN.

    Mas a frase "pode estar la" e uma afirmacao, e ela pode ser FALSA. Se todo
    glifo deste alvo na pagina ja mora dentro de uma celula desenhada que
    contem OUTRA cultura do rotulo e NAO contem esta, entao o alvo ja tem dono
    geometrico e a autorizacao nao pode estar na ocorrencia solta.

    Medido em 018067 MAXENTIS e 019095 KOJAMI: a tabela empilha ORZO (com
    Rincosporiosi, Maculatura, Elimintosporiosi, Ramularia, Ruggini e OIDIO),
    depois SEGALE (com Rincosporiosi e Ruggine) e depois TRITICALE. A palavra
    "segale" tambem aparece na linha de titulo do produto ("Fungicida per
    frumento, orzo, segale e triticale"), que nao esta em celula nenhuma — e
    era essa ocorrencia de TITULO que salvava o par. Os dois glifos de "Oidio"
    da pagina estao um na celula do ORZO e outro na tabela do FRUMENTO. SEGALE
    x OIDIO e um uso que a etichetta nao autoriza, e saia publicado.

    CONTROLES, medidos sobre os 1.872 pares de rota testavel antes de o teste
    entrar:
      absolvidos por R-14 (1.276)   0 acusados  <- nunca contradiz a geometria
      ja condenados por R-14 (47)  13 acusados  <- concorda por outro caminho
      CROP_ALSO_OUTSIDE_TABLE(108)  2 acusados  <- so os dois de 018067/019095
      NO_DRAWN_CELL (170)           0 acusados
    Nao ha numero novo aqui: o teste reusa `celula` e `celula_coerente` como
    estao, e o vocabulario e o das culturas que o proprio rotulo publica.
    """
    total = donos = 0
    for pi, pg in enumerate(pgs):
        als = [(x0, y0, x1, y1) for x0, y0, x1, y1, t in pg if radical(t) in ra]
        if not als or not any(radical(t) in rc for *_, t in pg):
            continue
        sg = segmentos(pdf, pi + 1)
        if sg is None:
            continue
        seg, altura = sg
        for ax0, ay0, ax1, ay1 in als:
            total += 1
            cel = celula(ax0, ax1, (ay0 + ay1) / 2, seg, altura)
            if cel is None or not celula_coerente(pg, *cel):
                continue
            topo, base, tx0, tx1 = cel
            dentro = {radical(t) for wx0, wy0, wx1, wy1, t in pg
                      if topo < (wy0 + wy1) / 2 < base and tx0 - 1 <= wx0 <= tx1 + 1}
            if (dentro & voc_reg) - {rp} and not (dentro & set(rc)):
                donos += 1
    return total > 0 and total == donos


def celula(x0, x1, cy, seg, altura):
    """Banda y da celula desenhada que contem a palavra, e a largura da tabela.

    Devolve (y_topo, y_base, x_tabela_ini, x_tabela_fim), ou None quando a
    coluna desta palavra nao e riscada — e ai a palavra nao prova nada, em
    direcao nenhuma.
    """
    cruz = fios_da_coluna(x0, x1, seg)
    if len(cruz) < MIN_FIOS_NA_COLUNA:
        return None
    acima = max((f for f in cruz if f[0] <= cy), default=None, key=lambda f: f[0])
    abaixo = min((f for f in cruz if f[0] > cy), default=None, key=lambda f: f[0])
    lados = [f for f in (acima, abaixo) if f]
    return (acima[0] if acima else 0.0,
            abaixo[0] if abaixo else altura,
            min(f[1] for f in lados), max(f[2] for f in lados))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pares', default='v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json')
    ap.add_argument('--pdfs', default='pilot-label-intelligence/labels/pdf')
    ap.add_argument('--bbox', default='/tmp/bboxcache')
    ap.add_argument('--fios', default='/tmp/fioscache')
    ap.add_argument('--out', default='v1/dados/PARES-FIOS-CHECK.json')
    ap.add_argument('--bin', default='pilot-label-intelligence/bin')
    a = ap.parse_args()
    sys.path.insert(0, a.bin)
    import fios as F
    os.makedirs(a.fios, exist_ok=True)

    memo = {}

    def segmentos(pdf, pagina1):
        """(segmentos, altura da pagina em pontos) — None quando o raster falha."""
        k = (pdf, pagina1)
        if k not in memo:
            try:
                r = F.fios(pdf, pagina1, cache=a.fios)
                memo[k] = (r['SEG'], r.get('PAGE_HEIGHT_PT') or 1e6)
            except Exception:
                memo[k] = None
        return memo[k]

    pares = json.load(open(a.pares, encoding='utf-8'))['PAIRS']
    # vocabulario de cultura do acervo, ja em radical — o mesmo conjunto fechado
    # de 46 nomes que o leitor de uso emite
    vocab = {r for x in pares for r in [radical(str(x.get('CROP') or '').split('_')[0])] if len(r) >= 4}
    por_reg = {}
    for i_global, x in enumerate(pares):
        por_reg.setdefault(x['REGISTRATION_ID'], []).append(x)

    ver, contra = {}, []
    cont = Counter()
    for reg in sorted(por_reg):
        pdf = os.path.join(a.pdfs, f'{reg}.pdf')
        if not os.path.exists(pdf):
            for i, _ in enumerate(por_reg[reg]):
                ver[f'{reg}#{i}'] = 'PAIR_NOT_CHECKABLE_NO_LABEL_PDF'
                cont['PAIR_NOT_CHECKABLE_NO_LABEL_PDF'] += 1
            continue
        try:
            pgs = palavras(pdf, a.bbox)
        except Exception:
            pgs = []
        # as culturas que ESTE rotulo publica, em radical. Vocabulario do
        # documento, nao do acervo: quem pode ser dono de um alvo aqui e uma
        # cultura deste rotulo.
        voc_reg = {r for y in por_reg[reg]
                   for r in [radical(str(y.get('CROP') or '').split('_')[0])] if len(r) >= 4}
        for i, x in enumerate(por_reg[reg]):
            chave = f'{reg}#{i}'
            rc = raizes_cultura(x.get('CROP'), x.get('CROP_AS_WRITTEN'))
            ra = raizes_alvo(x.get('TARGET'))
            # A RAIZ DO NOME PUBLICADO, separada das outras. rc pode conter uma
            # segunda raiz vinda de CROP_AS_WRITTEN, que e o TITULO DO GRUPO
            # ("ORTICOLE (...)", "Grano tenero e duro"). Ela serve para ACHAR a
            # celula; nao serve para provar o par. Ver PROVA_PELO_TITULO abaixo.
            rp = next((q for q in (radical(pt) for pt in str(x.get('CROP') or '').split('_'))
                       if len(q) >= 4), None)
            if x.get('ROUTE') not in ROTAS_TESTAVEIS:
                ver[chave] = 'PAIR_NOT_CHECKABLE_ROUTE_NOT_GEOMETRIC'
                cont[ver[chave]] += 1
                continue
            if not rc or not ra or not pgs:
                ver[chave] = 'PAIR_NOT_CHECKABLE_ANCHOR_NOT_BUILDABLE'
                cont[ver[chave]] += 1
                continue
            achou = None            # (pagina1, y_cultura, y_alvo)
            pelo_titulo = None      # a celula fechou, mas pela raiz do TITULO do grupo
            houve_celula = False    # alguma ocorrencia da cultura tem celula desenhada
            fora_de_celula = False  # e alguma NAO tem
            celula_incoerente = False  # havia grade, e ela nao descreve o texto
            sob_cabecalho = False   # o alvo esta abaixo da cultura, na mesma coluna
            houve_convivio = False  # cultura e alvo na mesma pagina
            perto = None
            for pi, pg in enumerate(pgs):
                cs = [(x0, y0, x1, y1, radical(t) == rp)
                      for x0, y0, x1, y1, t in pg if radical(t) in rc]
                if not cs:
                    continue
                als = [(x0, x1, (y0 + y1) / 2) for x0, y0, x1, y1, t in pg if radical(t) in ra]
                if not als:
                    continue
                houve_convivio = True
                sg = segmentos(pdf, pi + 1)
                if sg is None:
                    continue
                seg, altura = sg
                for x0, cy0, x1, cy1, e_o_nome in cs:
                    c = (cy0 + cy1) / 2
                    cel = celula(x0, x1, c, seg, altura)
                    if cel is not None and not celula_coerente(pg, *cel):
                        # NAO E "SEM GRADE". A grade existe: o que ela nao faz e
                        # descrever o texto que esta dentro dela. Sao duas
                        # ignorancias diferentes e ate a rodada 4 as duas saiam
                        # com o mesmo nome, NO_DRAWN_CELL, que a tela lia como
                        # "a coluna da cultura nesta pagina nao tem grade
                        # desenhada". Medido: em 58 dos 170 casos havia >=3 fios
                        # atravessando a coluna — a frase da tela era falsa
                        # sobre o documento. Em 008259 a coluna de "Pesco" e
                        # atravessada por 15 e 17 fios.
                        cel = None
                        celula_incoerente = True
                    if cel is None:
                        fora_de_celula = True
                        continue
                    houve_celula = True
                    topo, base, tx0, tx1 = cel
                    dentro = [ay for ax, axf, ay in als
                              if topo < ay < base and tx0 - 1 <= ax <= tx1 + 1]
                    if dentro:
                        if e_o_nome:
                            achou = (pi + 1, round(c, 2), round(dentro[0], 2))
                            break
                        # PROVA PELO TITULO DO GRUPO NAO E PROVA DO PAR.
                        #
                        # Medido em 018270 GLIPHOGAN TOP CL (e nos identicos
                        # 018271/018277/018279): a celula desenhada escreve
                        # "ORTICOLE (CARCIOFO, CAROTA, FAGIOLINO, FAVA,
                        # PISELLO, ...)" e o par publicado diz FAGIOLO. A
                        # palavra FAGIOLO nao existe em nenhuma pagina do PDF.
                        # O que casou a celula foi a raiz de CROP_AS_WRITTEN,
                        # 'orticol' — o TITULO. A geometria provou que o titulo
                        # do grupo e o alvo dividem uma celula; nao provou que
                        # FAGIOLO esta nesse grupo, porque para isso e preciso
                        # decidir se FAGIOLO e FAGIOLINO sao a mesma cultura, e
                        # essa e uma equivalencia taxonomica que este
                        # repositorio nao tem. Mesmo mecanismo em 015232,
                        # 017358 e 017824, onde 'gran' ("Grano tenero e duro")
                        # absolve FRUMENTO por sinonimia nao declarada.
                        #
                        # 13 dos 1.289 absolvidos vinham daqui. Os outros 1.276
                        # tem o nome proprio da cultura DENTRO da celula usada.
                        # O selo verde nao pode cobrir os dois casos, entao o
                        # segundo sai com nome proprio de ignorancia. NAO e
                        # condenacao: a etichetta pode muito bem autorizar o
                        # uso, e o modulo nao sabe.
                        if pelo_titulo is None:
                            pelo_titulo = (pi + 1, round(c, 2), round(dentro[0], 2))
                        continue
                    # CABECALHO DE BLOCO NAO E COLUNA DE CULTURA. Quando um
                    # glifo do alvo esta na MESMA faixa x da cultura e ABAIXO
                    # da celula dela, o desenho e "titulo em cima, linhas
                    # embaixo" — e o fio entre os dois separa linhas de um
                    # bloco que o titulo governa, nao a cultura do alvo.
                    # Medido em 010587 FOLPAN SC: "POMODORO" e um cabecalho e
                    # "Peronospora" e a linha logo abaixo, na mesma coluna;
                    # pela regra de coluna a ferramenta condenava um uso que a
                    # etichetta autoriza. Nesse desenho o teste nao se aplica.
                    #
                    # A ressalva da ressalva: so e cabecalho se NAO houver
                    # outro TITULO DE BLOCO entre a celula da cultura e o alvo.
                    # Em 012573 as culturas sao empilhadas na mesma coluna
                    # ("CARCIOFO:", "BARBABIETOLA", "ORNAMENTALI,") e as linhas
                    # de alvo continuam na largura toda: o alvo da BARBABIETOLA
                    # cai abaixo da celula do CARCIOFO e na mesma faixa x. Se
                    # entre os dois ha outro titulo, o alvo e DELE, e a
                    # contradicao continua de pe.
                    for ax, axf, ay in als:
                        if not (ax <= x1 and axf >= x0 and ay > base):
                            continue
                        if not titulo_entre(pg, base, ay, tx0, tx1, vocab):
                            sob_cabecalho = True
                            break
                    if perto is None:
                        perto = (pi + 1, round(c, 2),
                                 round(min(als, key=lambda p: abs(p[2] - c))[2], 2))
                if achou:
                    break
            if achou:
                ver[chave] = 'PAIR_CONSISTENT_WITH_RULES'
            elif pelo_titulo:
                ver[chave] = 'PAIR_NOT_CHECKABLE_CROP_NAME_NOT_THE_ANCHOR'
            elif houve_celula and sob_cabecalho:
                ver[chave] = 'PAIR_NOT_CHECKABLE_TARGET_UNDER_CROP_HEADER'
            elif houve_celula and fora_de_celula:
                # EVIDENCIA MISTA, QUE NAO E CONDENACAO. Parte das ocorrencias
                # do nome da cultura esta dentro de celula desenhada e parte
                # nao. As celulas que existem nao contem este alvo — mas a
                # autorizacao pode estar justamente numa das ocorrencias que o
                # teste nao alcanca, e condenar com base nas outras seria
                # afirmar sobre o que nao foi medido. Medido em 008102 MERPAN:
                # "melo" aparece na descricao do produto (coluna riscada) e no
                # bloco de uso (prosa sublinhada, sem grade); pela ocorrencia da
                # descricao a regra condenava MELO x TICCHIOLATURA, que o bloco
                # de uso autoriza duas linhas abaixo.
                #
                # A RESSALVA DA RESSALVA: "a autorizacao pode estar la" e uma
                # afirmacao, e da para testa-la. Ver alvo_tem_outro_dono.
                if alvo_tem_outro_dono(pgs, rc, rp, ra, voc_reg, segmentos, pdf):
                    ver[chave] = 'PAIR_CONTRADICTED_BY_RULE'
                    pg1, cy, ay = perto or ('NOT_KNOWN', 'NOT_KNOWN', 'NOT_KNOWN')
                    contra.append({
                        'KEY': chave, 'REGISTRATION_ID': reg, 'PRODUCT': x.get('PRODUCT'),
                        'CROP': x.get('CROP'), 'TARGET': x.get('TARGET'),
                        'CROP_AS_WRITTEN': x.get('CROP_AS_WRITTEN'),
                        'TARGET_AS_WRITTEN': x.get('TARGET_AS_WRITTEN'),
                        'ROUTE': x.get('ROUTE'), 'PAGE_TESTED': pg1,
                        'CROP_TOKEN_Y': cy, 'TARGET_ANCHOR_Y': ay,
                        'MECHANISM': 'TARGET_BELONGS_TO_ANOTHER_CROP_CELL',
                        'PROOF': (f'o nome "{rc[0]}" tambem ocorre fora de celula desenhada '
                                  f'(pagina {pg1}), e por isso este par era abstencao. Mas '
                                  f'TODO glifo do alvo "{x.get("TARGET")}" nesta etichetta '
                                  f'mora dentro da celula desenhada de OUTRA cultura do mesmo '
                                  f'rotulo — o alvo ja tem dono, e a autorizacao nao pode '
                                  f'estar na ocorrencia solta'),
                    })
                else:
                    ver[chave] = 'PAIR_NOT_CHECKABLE_CROP_ALSO_OUTSIDE_TABLE'
            elif houve_celula:
                ver[chave] = 'PAIR_CONTRADICTED_BY_RULE'
                pg1, cy, ay = perto or ('NOT_KNOWN', 'NOT_KNOWN', 'NOT_KNOWN')
                contra.append({
                    'MECHANISM': 'CROP_CELL_DOES_NOT_CONTAIN_TARGET',
                    'KEY': chave, 'REGISTRATION_ID': reg, 'PRODUCT': x.get('PRODUCT'),
                    'CROP': x.get('CROP'), 'TARGET': x.get('TARGET'),
                    'CROP_AS_WRITTEN': x.get('CROP_AS_WRITTEN'),
                    'TARGET_AS_WRITTEN': x.get('TARGET_AS_WRITTEN'),
                    'ROUTE': x.get('ROUTE'), 'PAGE_TESTED': pg1,
                    'CROP_TOKEN_Y': cy, 'TARGET_ANCHOR_Y': ay,
                    'PROOF': (f'na pagina {pg1} nenhuma celula desenhada que contem "{rc[0]}" '
                              f'(a ocorrencia mais proxima em y={cy}) contem qualquer glifo do '
                              f'alvo "{x.get("TARGET")}" (o mais proximo em y={ay}, fora da banda '
                              f'ou fora da largura da tabela). A etichetta nao autoriza este uso '
                              f'nesta celula'),
                })
            elif houve_convivio and celula_incoerente:
                ver[chave] = 'PAIR_NOT_CHECKABLE_TABLE_NOT_DESCRIBING_ITS_TEXT'
            elif houve_convivio:
                ver[chave] = 'PAIR_NOT_CHECKABLE_NO_DRAWN_CELL'
            else:
                ver[chave] = 'PAIR_NOT_CHECKABLE_ANCHOR_NOT_FOUND'
            cont[ver[chave]] += 1

    saida = {
        'DATASET': 'V1-PARES-FIOS-CHECK',
        'RULE_ID': 'R-14',
        'O_QUE_ISTO_E': ('conferencia do PAR DE USO (cultura x alvo) contra os fios desenhados '
                         'da tabela, do mesmo jeito que R-11 confere a linha de dose'),
        'O_QUE_ISTO_NAO_E': ('nao le rotulo novo, nao corrige a cultura e nao descobre o alvo '
                             'certo: so diz que o par publicado nao sobrevive ao documento'),
        'ANCHOR': ('a celula desenhada de cada ocorrencia do nome da cultura (fio acima, fio '
                   'abaixo, largura da tabela); basta um glifo do alvo dentro de uma delas '
                   'para o par sobreviver'),
        'COBERTURA_MINIMA_DO_FIO': COBRE,
        'PAIRS': len(pares),
        'COUNTS': dict(sorted(cont.items(), key=lambda kv: -kv[1])),
        'VERDICT': ver,
        'CONTRADICTED': contra,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in saida['COUNTS'].items():
        print(f'  {v:>5}  {k}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
