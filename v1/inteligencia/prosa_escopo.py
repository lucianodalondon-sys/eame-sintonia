#!/usr/bin/env python3
"""
prosa_escopo.py — R-16. O par de uso lido de PROSA tambem tem de sobreviver ao
documento. O instrumento aqui nao e geometrico: e SINTATICO.

## O territorio, medido antes de qualquer regra

Dos 2.875 pares publicados, 1.562 vem de rota de PROSA e nao de tabela. R-14 e
geometrica e so alcanca quem tem grade desenhada: 1.052 desses pares
(HEADER_CONTINUATION e AUTHORISED_USE_LIST) saem
`PAIR_NOT_CHECKABLE_ROUTE_NOT_GEOMETRIC` — que e NOT_CHECKED, nunca aprovacao,
mas continuam publicados como uso autorizado.

E ja foi medido que o atalho obvio nao serve: perguntar "a cultura e o alvo
aparecem no mesmo documento?" responde SIM para 93,6% dos pares que a geometria
CONDENA e 98,5% dos que ela ABSOLVE. Coocorrencia nao discrimina nada.

## O que o documento realmente tem

A etichetta em prosa nao escreve frases soltas: ela escreve BLOCOS COM CABECALHO.

    MELO: contro Podosphaera leucotricha, intervenire in modo preventivo con
    60 mL/hL di prodotto, ogni 10 giorni, dallo stadio di prefioritura...
    VITE: contro Uncinula necator, intervenire...

O cabecalho e o escopo. Tudo o que vem depois dele pertence aquela cultura ate o
PROXIMO cabecalho. Essa e uma estrutura verificavel palavra a palavra, e e a
mesma coisa que os fios fazem na tabela: delimitar.

## A regra

Para cada par de prosa:

  1. o texto e remontado POR COLUNA (mesmo instrumento de SF-01: fios verticais
     + caixas de palavra). Sem isso, um cabecalho de uma coluna captura o texto
     da coluna vizinha, que e o vazamento que MF-02 mediu na tabela;
  2. acham-se os CABECALHOS DE BLOCO da coluna: nome(s) de cultura seguidos de
     dois-pontos. Sao medidos no documento, nao supostos;
  3. o escopo de um cabecalho vai dele ate o cabecalho seguinte;
  4. o par sobrevive se existir um cabecalho que NOMEIA esta cultura e cujo
     escopo contem a EVIDENCIA do alvo. E cai se existir cabecalho para esta
     cultura e a evidencia do alvo estiver, toda ela, no escopo de outro
     cabecalho DE CULTURA.

## NEM TODO DOIS-PONTOS E UM CABECALHO DE CULTURA

Isto foi medido, e custou dois falsos positivos que so apareceram no controle:

  * `015317` SESTO GOLD — a regra condenava VITE x PERONOSPORA, que a etichetta
    autoriza em letra de forma ("Coltura: VITE da vino | Patogeno: Peronospora
    della vite (Plasmopara Viticola) | 200 g/hl | 2 kg/ha"). O "cabecalho" que a
    condenou era **"folpet:"**, uma substancia ativa seguida de dois-pontos na
    secao de composicao;
  * `016312` TOMIGAN — MANDORLO e NOCE x INFESTANTI condenados por
    **"usi autorizzati:"**, que e um titulo de SECAO.

Entao: **so cabecalho DE CULTURA delimita bloco de cultura.** Um titulo que nao
nomeia cultura nem abre bloco nem fecha o anterior — ele esta DENTRO do bloco.
Isso tambem foi medido, no mesmo 016312: MANDORLO e NOCE continuavam condenados
depois do primeiro conserto porque o bloco

    "Fruttiferi a guscio (nocciolo, mandorlo, noce): Per il controllo delle
     malerbe: Applicare in post-emergenza delle infestanti alla dose di 1,5 l/ha"

era cortado ao meio por "Per il controllo delle malerbe:", que e um subtitulo do
proprio bloco. O escopo de uma cultura vai ate a PROXIMA CULTURA, e o que estiver
no meio pertence a ela.

Contradicao, portanto, so existe entre DUAS CULTURAS.

## E O TESTE SO SE APLICA A QUEM NASCEU DE BLOCO

Terceiro conserto vindo do controle, e o que mais mudou o resultado. A primeira
versao usava como evidencia o NOME do alvo. Para um herbicida isso e vazio: o
alvo e a categoria `INFESTANTI`, atribuida pelo tipo do produto, e nao uma
palavra que cada bloco tenha de repetir. Medido em `009005` AGIL: o rotulo tem 4
blocos de cultura e a palavra "infestanti" aparece em UM deles ("riso:"). A
regra concluia que LATTUGA — que esta no terceiro bloco, autorizada em letra de
forma — era contradita, porque o bloco dela fala em "malerbe" e nao em
"infestanti". Foram **169 condenacoes falsas**, todas da rota
`AUTHORISED_USE_LIST`.

A evidencia certa nao e o nome normalizado: e o `TARGET_AS_WRITTEN`, o trecho
que o extrator REALMENTE LEU para produzir o par. E dai sai o filtro que faltava:
**se esse trecho nao esta dentro de nenhum bloco de cultura, o par nao nasceu de
prosa de bloco e este teste nao se aplica a ele** — sai
`PROSE_SCOPE_NOT_FROM_BLOCK_PROSE`, que e NOT_MEASURABLE com nome proprio.

A evidencia do alvo e, em ordem: o nome do alvo como a lista o normaliza; e, se
ele nao for literal no documento, o trecho que o extrator gravou em
`TARGET_AS_WRITTEN` — que e o texto que ele leu.

## O QUE ESTA REGRA NAO RESOLVE, E E MUITO

Ela responde ESCOPO: "este texto de alvo pertence a esta cultura?". Ela **nao**
responde NOMEACAO: "o nome do alvo publicado e o que o documento diz?".

Medido: **154 pares de prosa publicam um nome de alvo que nao aparece uma unica
vez no rotulo**. O caso maior e 007555, que escreve

    "Contro afidi (Dysaphis plantaginea, Aphis pomi), ditteri cecidomidi
     (Contarinia pyrivora, Dasineura pyri), lepidotteri (Adoxophyes orana,
     Phyllonorycter blancardella, Cydia pomonella, Yponomeuta malinellus)"

e do qual a ferramenta publica CARPOCAPSA, CECIDOMIA, LITOCOLLETE, COCCINIGLIE.
`Cydia pomonella` E a carpocapsa e `Phyllonorycter blancardella` E a
litocollete — mas quem sabe disso e uma TAXONOMIA que este repositorio nao tem e
nao pode mostrar. A afirmacao e provavelmente verdadeira e nao e verificavel
contra o documento, e as duas coisas tem de ser ditas juntas.

Por isso o modulo emite DOIS eixos separados, e o casco nunca os colapsa:

    SCOPE  : PROSE_SCOPE_PROVEN / CONTRADICTED / AMBIGUOUS / NOT_MEASURABLE
    NAMING : TARGET_NAME_LITERAL / TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL

Um par so e FATO se as duas colunas fecharem. Escopo provado com nome inferido e
inferencia rotulada, nao fato.

## O VEREDITO DESTE INSTRUMENTO: **ELE NAO DISCRIMINA. NAO ENTRA EM PRODUCAO.**

Isto foi medido, nao concluido por prudencia. Havia uma verdade de terra
disponivel de graca: os 1.336 pares de rota de TABELA em que R-14 da um veredito
GEOMETRICO independente. Rodando R-16 sobre eles:

    PROSE_SCOPE_PROVEN        17,8% dos pares que a geometria ABSOLVE
                              27,7% dos pares que a geometria CONDENA

O sinal esta INVERTIDO: a regra "prova" com mais frequencia justamente onde o
documento desmente. Os 13 casos sao todos de `012573`, onde os blocos
(CARCIOFO / BARBABIETOLA / ORNAMENTALI) estao empilhados na MESMA coluna sem fio
vertical entre eles — o escopo do cabecalho vaza para o bloco de baixo, que e
exatamente o vazamento que MF-02 mediu na camada de tabela. **PROVEN nao pode
autorizar nada.**

    PROSE_SCOPE_CONTRADICTED  4 casos produzidos no acervo inteiro
                              4 auditados a mao contra o PDF
                              4 FALSOS POSITIVOS

  * `016152` SEEDRON — ORZO x FUSARIOSI, x CARBONE e x ELMINTOSPORIOSI. A
    etichetta escreve, em letra de forma: "Orzo: Fusariosi (Fusarium spp.,
    Microdochium nivale), Carbone (Ustilago nuda), Striatura bruna (Pyrenophora
    spp.)". Os tres usos existem. A regra condenou porque o trecho que o extrator
    gravou tem espacamento diferente do documento ("( Fusarium" contra
    "(Fusarium") e casou no bloco vizinho da reconstrucao por coluna;
  * `009005` AGIL — TABACCO x INFESTANTI. A etichetta escreve "..., Tabacco,
    Coriandolo da seme: Intervenire alla dose di 0,8-2,0 l/ha adattando il
    dosaggio in funzione delle malerbe presenti". O uso existe. A regra condenou
    porque a secao de espectro ("Infestanti sensibili: Avena spp....") nao e
    bloco de cultura e foi atribuida ao bloco anterior.

**Taxa de falso positivo medida: 4 em 4.** Uma regra que so produz falso positivo
nao remove nada.

## AS TRES TENTATIVAS, TODAS MEDIDAS

Este e o terceiro instrumento tentado sobre o territorio de prosa, e os tres
falharam por motivos diferentes — o que ja e conhecimento:

  1. COOCORRENCIA NO DOCUMENTO ("a cultura e o alvo aparecem no mesmo rotulo").
     Responde SIM para 93,6% dos pares que a geometria condena e 98,5% dos que
     ela absolve. Nao mede nada;
  2. COOCORRENCIA EM ESCOPO DE CABECALHO, sem exigir que o par tenha nascido de
     bloco. Produzia 169 condenacoes falsas so na rota AUTHORISED_USE_LIST,
     porque para um herbicida o alvo e a categoria `INFESTANTI` e nao uma palavra
     que cada bloco repita;
  3. ESTE — escopo de bloco de cultura, com o texto remontado por coluna, com a
     evidencia sendo o trecho que o extrator leu, e com tres filtros que sairam
     de contraexemplos reais (so cabecalho de cultura possui escopo; subtitulo
     nao corta bloco; par que nao nasceu de bloco nao e testado). Ainda assim:
     PROVEN invertido e CONTRADITO 4/4 falso.

O que os tres tem em comum: **a estrutura de bloco existe no PAPEL, nao no texto
extraido.** O `pdftotext` — de coluna ou de fluxo — nao devolve a fronteira de
bloco de forma confiavel em etichetta de tres colunas, e a reconstrucao por
fios verticais so acerta quando ha fio vertical entre os blocos, que e
justamente o caso em que a camada geometrica ja resolve.

## ENTAO PARA QUE ISTO SERVE

Para duas coisas, e as duas entram em producao:

  1. o eixo **NOMEACAO**, que nao depende de escopo nenhum: `154` pares de prosa
     publicam um nome de alvo que NAO aparece uma unica vez no rotulo. E um
     `grep`, e reproduz sempre;
  2. o **CENSO** (`prosa_censo.py`), que diz de que forma o documento apresenta
     cada par — e por que os instrumentos falham em cada familia.

O eixo ESCOPO fica gravado em `PROSA-ESCOPO.json` como DIAGNOSTICO e
**nao e lido pelo payload**. Publicar um selo a partir dele seria repetir, na
camada de prosa, o erro que a rodada 3 encontrou na camada de tabela: dar selo
verde a um teste que nao testa.
"""
import argparse, json, os, re, subprocess, sys, unicodedata
from collections import Counter

RXP = re.compile(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', re.S)
RXW = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>')
TOL_LINHA = 2.5

# Um CABECALHO DE BLOCO e um ou mais nomes seguidos de dois-pontos. A forma foi
# medida no acervo antes de virar regex: caixa alta ("MELO:", "ORNAMENTALI,
# FLOREALI, FORESTALI:"), capitalizada ("Pesco, Albicocco e Nettarino:") e com
# parentese de escopo ("POMODORO (pieno campo e serra):"). O limite de 90
# caracteres e o que separa cabecalho de frase com dois-pontos no meio.
RX_CABECA = re.compile(
    r'(?:^|(?<=[.;)\s]))'
    r'([A-ZÀ-Þ][A-Za-zÀ-ÿ][A-Za-zÀ-ÿ \'’,\-()/&]{1,88}?)\s*:\s',
)
# Palavras que denunciam frase, nao cabecalho de cultura. Medidas no acervo.
NAO_E_CABECA = re.compile(
    r'\b(avvertenz|attenzione|nota|note|informazioni|medico|sintomi|terapia|'
    r'pericolo|prescrizioni|indicazioni|consigli|smaltimento|composizione|'
    r'registrazione|autorizzazione|stabilimento|distribuito|contenuto|partita|'
    r'etichetta|fabbricante|titolare|telefono|antidoto|modalit|precauzion|'
    r'in caso|per proteggere|non rientrare|conservare|tenere|classificazione|'
    r'meccanismo|caratteristiche|dosi e|spettro|compatibilit|fitotossicit|'
    r'avvertenze|resistenz|gestione|epoca|volume|attrezzatur)', re.I)


# UMA SO STRING, E TODAS AS POSICOES SOBRE ELA.
#
# A primeira versao detectava cabecalho no texto CRU e fatiava o escopo no texto
# normalizado. As duas strings nao tem o mesmo comprimento — tirar acento muda
# tamanho — e o escopo saia deslocado, em silencio, com numeros plausiveis. Foi
# o mesmo erro de indexacao que ja custou uma medicao nesta casa (fios() e
# 1-indexado, palavras() e 0-indexada). Agora ha UMA base: acento dobrado,
# espaco colapsado, CAIXA PRESERVADA — porque cabecalho se reconhece pela caixa.
def dobra(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def base(s):
    return re.sub(r'\s+', ' ', dobra(s)).strip()


def sa(s):
    return dobra(s).lower()


def nz(s):
    return re.sub(r'\s+', ' ', sa(s)).strip()


def caixas(pdf, cache):
    os.makedirs(cache, exist_ok=True)
    alvo = os.path.join(cache, os.path.basename(pdf)[:-4] + '.xml')
    if not os.path.exists(alvo) or os.path.getsize(alvo) == 0:
        subprocess.run(['pdftotext', '-bbox-layout', pdf, alvo],
                       check=True, capture_output=True, timeout=300)
    body = open(alvo, encoding='utf-8', errors='replace').read()
    return [[(float(x0), float(y0), float(x1), float(y1), t)
             for x0, y0, x1, y1, t in RXW.findall(b)] for _, _, b in RXP.findall(body)]


def texto_por_coluna(pg, verticais, largura):
    """O texto da pagina remontado DENTRO de cada banda entre fios verticais."""
    cortes = sorted({0.0, largura} | {v for v in verticais if 0 < v < largura})
    saida = []
    for a, b in zip(cortes, cortes[1:]):
        if b - a < 20:
            continue
        dentro = [w for w in pg if a <= (w[0] + w[2]) / 2 <= b]
        if not dentro:
            continue
        linhas = {}
        for x0, y0, x1, y1, t in dentro:
            cy = (y0 + y1) / 2
            k = next((k for k in linhas if abs(k - cy) <= TOL_LINHA), round(cy, 1))
            linhas.setdefault(k, []).append((x0, t))
        saida.append(' '.join(' '.join(t for _, t in sorted(linhas[k]))
                              for k in sorted(linhas)))
    return saida


def cabecalhos(txt, vocab):
    """[(inicio_escopo, fim_escopo, cabecalho, posicao)] dos blocos DE CULTURA.

    So cabecalho que nomeia cultura entra, e o escopo de um vai ate o proximo:
    subtitulo dentro do bloco nao o corta.
    """
    achados = []
    for m in RX_CABECA.finditer(txt):
        cab = m.group(1).strip()
        if NAO_E_CABECA.search(cab):
            continue
        if len(cab) < 3 or not re.search(r'[A-Za-zÀ-ÿ]{3}', cab):
            continue
        if not cabeca_e_de_cultura(nz(cab), vocab):
            continue
        achados.append((m.start(1), m.end(0), nz(cab)))
    out = []
    for i, (a, fim_cab, cab) in enumerate(achados):
        prox = achados[i + 1][0] if i + 1 < len(achados) else len(txt)
        out.append((fim_cab, prox, cab, a))
    return out


def itens(cab):
    """Os nomes que um cabecalho enumera. Lista se le item a item."""
    bruto = re.sub(r'\((.*?)\)', r', \1', cab)
    return [p.strip() for p in re.split(r'[,;/]|\se\s|\sed\s', bruto) if p.strip()]


def cabeca_e_de_cultura(cab, vocab):
    """O cabecalho nomeia alguma cultura do vocabulario do acervo?

    Sem este filtro, "folpet:" e "usi autorizzati:" viravam donos de escopo e
    condenavam uso que a etichetta escreve em letra de forma.
    """
    for it in itens(cab):
        n = nz(it)
        for v in vocab:
            if n == v or n.startswith(v + ' ') or n.endswith(' ' + v):
                return True
    return False


def cabeca_nomeia(cab, crop):
    """O cabecalho nomeia ESTA cultura? Item inteiro, nao substring."""
    c = nz(crop)
    for it in itens(cab):
        it = nz(it)
        if it == c or it.startswith(c + ' ') or it.endswith(' ' + c):
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pares', default='v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json')
    ap.add_argument('--pdfs', default='pilot-label-intelligence/labels/pdf')
    ap.add_argument('--bbox', default='/tmp/bboxcache')
    ap.add_argument('--fios', default='/tmp/fioscache')
    ap.add_argument('--fluxo', default='/tmp/leiturafluxo')
    ap.add_argument('--bin', default='pilot-label-intelligence/bin')
    ap.add_argument('--out', default='v1/dados/PROSA-ESCOPO.json')
    # CONTROLE DE DISCRIMINACAO: rodar tambem sobre os pares de TABELA, onde
    # R-14 da um veredito geometrico INDEPENDENTE. Se R-16 responder a mesma
    # coisa para os que a geometria condena e para os que ela absolve, ela nao
    # mede nada — foi assim que o teste de coocorrencia foi descartado.
    ap.add_argument('--incluir-tabela', action='store_true')
    a = ap.parse_args()
    sys.path.insert(0, a.bin)
    import fios as F
    os.makedirs(a.fios, exist_ok=True)
    os.makedirs(a.fluxo, exist_ok=True)

    TAB = {'GEOMETRIC_TABLE', 'MERGED_COLUMN_TABLE'}
    pares = json.load(open(a.pares, encoding='utf-8'))['PAIRS']
    # vocabulario de cultura do acervo: os nomes que o proprio leitor de uso
    # emite. Fechado e medido, como o de exclusao.py.
    VOCAB = {nz(str(x['CROP']).replace('_', ' ')) for x in pares}
    VOCAB |= {p for v in VOCAB for p in v.split() if len(p) >= 4}
    memo = {}

    def textos(reg):
        """[(texto_normalizado, cabecalhos)] — uma entrada por coluna, mais o
        texto em ordem de leitura como ultima chance."""
        if reg in memo:
            return memo[reg]
        pdf = os.path.join(a.pdfs, f'{reg}.pdf')
        blocos = []
        if os.path.exists(pdf):
            try:
                pgs = caixas(pdf, a.bbox)
                for pi, pg in enumerate(pgs):
                    r = F.fios(pdf, pi + 1, cache=a.fios)
                    for col in texto_por_coluna(pg, r.get('V') or [],
                                                r.get('PAGE_WIDTH_PT') or 0):
                        blocos.append(re.sub(r'\s+', ' ', col).strip())
            except Exception:
                blocos = []
            f = os.path.join(a.fluxo, reg + '.txt')
            if not os.path.exists(f) or os.path.getsize(f) == 0:
                try:
                    subprocess.run(['pdftotext', pdf, f], check=True,
                                   capture_output=True, timeout=120)
                except Exception:
                    pass
            if os.path.exists(f):
                blocos.append(re.sub(r'\s+', ' ',
                                     open(f, encoding='utf-8', errors='replace').read()).strip())
        # base() preserva a caixa (o cabecalho se reconhece por ela) e o
        # .lower() dela tem EXATAMENTE o mesmo comprimento, entao as posicoes
        # do cabecalho valem nas duas.
        saida = []
        for b in blocos:
            if not b:
                continue
            bb = base(b)
            saida.append((bb.lower(), cabecalhos(bb, VOCAB)))
        memo[reg] = saida
        return memo[reg]

    ver, det = {}, []
    cont, cont_nome = Counter(), Counter()
    ordem = {}
    for x in pares:
        reg = x['REGISTRATION_ID']
        i = ordem[reg] = ordem.get(reg, -1) + 1
        chave = f'{reg}#{i}'
        if x['ROUTE'] in TAB and not a.incluir_tabela:
            continue
        crop, alvo = x['CROP'], x['TARGET']
        traw = nz(x.get('TARGET_AS_WRITTEN'))
        nome_alvo = nz(str(alvo).replace('_', ' '))

        # ---- eixo NOMEACAO, independente do escopo
        blocos = textos(reg)
        tudo = ' || '.join(b for b, _ in blocos)
        if nome_alvo and nome_alvo in tudo:
            nomeacao = 'TARGET_NAME_LITERAL'
        elif not blocos:
            nomeacao = 'TARGET_NAME_NOT_CHECKABLE_NO_TEXT'
        else:
            nomeacao = 'TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL'
        cont_nome[nomeacao] += 1

        # ---- eixo ESCOPO
        # A EVIDENCIA E O QUE O EXTRATOR LEU, nao o nome que ele atribuiu.
        ev = traw[:60] if traw else ''
        prova = ''
        estado = 'PROSE_SCOPE_NOT_MEASURABLE'
        achou_cab = achou_outro = ev_em_bloco = False
        for txt, cabs in blocos:
            if not cabs or not ev:
                continue
            if any(ev in txt[ini:fim] for ini, fim, _c, _a in cabs):
                ev_em_bloco = True
            meus = [c for c in cabs if cabeca_nomeia(c[2], crop)]
            if not meus:
                continue
            achou_cab = True
            for ini, fim, cab, _a in meus:
                if ev in txt[ini:fim]:
                    estado = 'PROSE_SCOPE_PROVEN'
                    prova = (f'o rotulo abre um bloco "{cab[:60]}:" e o trecho que o extrator '
                             f'leu para este alvo esta dentro dele, antes do proximo bloco de '
                             f'cultura')
                    break
            if estado == 'PROSE_SCOPE_PROVEN':
                break
            for ini, fim, cab, _a in cabs:
                if cabeca_nomeia(cab, crop):
                    continue
                if ev in txt[ini:fim]:
                    achou_outro = True
                    prova = (f'o rotulo abre um bloco para esta cultura, e o trecho que o '
                             f'extrator leu para este alvo esta INTEIRO no bloco de outra '
                             f'cultura ("{cab[:60]}:")')
                    break
        if estado != 'PROSE_SCOPE_PROVEN':
            if not ev:
                estado = 'PROSE_SCOPE_NO_TARGET_TEXT_RECORDED'
            elif not ev_em_bloco:
                estado = 'PROSE_SCOPE_NOT_FROM_BLOCK_PROSE'
            elif achou_cab and achou_outro:
                estado = 'PROSE_SCOPE_CONTRADICTED'
            elif achou_cab:
                estado = 'PROSE_SCOPE_TARGET_NOT_FOUND_IN_ANY_BLOCK'
            else:
                estado = 'PROSE_SCOPE_NO_HEADING_FOR_THIS_CROP'
        cont[estado] += 1
        ver[chave] = {'scope': estado, 'naming': nomeacao, 'route': x['ROUTE']}
        if estado in ('PROSE_SCOPE_CONTRADICTED',) or \
           nomeacao == 'TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL':
            det.append({'KEY': chave, 'REGISTRATION_ID': reg, 'PRODUCT': x.get('PRODUCT'),
                        'CROP': crop, 'TARGET': alvo, 'ROUTE': x['ROUTE'],
                        'SCOPE': estado, 'NAMING': nomeacao,
                        'TARGET_AS_WRITTEN': str(x.get('TARGET_AS_WRITTEN'))[:220],
                        'PROOF': prova})

    saida = {
        'DATASET': 'V1-PROSA-ESCOPO',
        'RULE_ID': 'R-16',
        'O_QUE_ISTO_E': ('conferencia do par de uso lido de PROSA contra o escopo do cabecalho '
                         'de bloco que o rotulo escreve, com o texto remontado por coluna'),
        'O_QUE_ISTO_NAO_E': ('nao responde NOMEACAO: se o nome do alvo publicado nao aparece no '
                             'rotulo, nenhum teste de escopo o torna literal'),
        'PAIRS_PROSE': sum(cont.values()),
        'SCOPE_COUNTS': dict(cont.most_common()),
        'NAMING_COUNTS': dict(cont_nome.most_common()),
        'VERDICT': ver,
        'DETAIL': det,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(saida, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('  ESCOPO:', file=sys.stderr)
    for k, v in cont.most_common():
        print(f'    {v:5}  {k}', file=sys.stderr)
    print('  NOMEACAO:', file=sys.stderr)
    for k, v in cont_nome.most_common():
        print(f'    {v:5}  {k}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
