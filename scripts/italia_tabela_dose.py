#!/usr/bin/env python3
"""
ITÁLIA — a tabela de doses, que é onde a autorização por cultura realmente mora.

Nas rodadas anteriores este repositório publicou `CROP_TERM_PRESENT` com uma ressalva
honesta e limitante: *"a associação cultura↔alvo mora numa coluna de tabela que a extração
de PDF perde"*. Isso era verdade sobre o documento inteiro. **Não é verdade sobre a região
da tabela**, e a diferença é o que este arquivo explora.

O texto extraído perde a GRADE, mas preserva a ORDEM de leitura. Dentro da tabela de doses
as linhas saem sequenciais:

    Coltura Patogeno Dose ...
    Barbabietola da zucchero  Cercosporiosi (Cercospora beticola)  150  0,75  2 trattamenti…
    Mais, Mais Dolce, Sorgo   Agriotes sp., Diabrotica sp.         12-15

Então a linha é recuperável **se e somente se** o recorte for a tabela e não o documento.
Fora dela, "mais" pode ser cláusula de rotação; dentro dela, é a cultura autorizada.

O QUE ISTO MUDA DE CLASSE

    CROP_TERM_PRESENT      o termo aparece no rótulo              (fraco)
    AUTHORIZED_USE_ROW     cultura, alvo e dose na MESMA linha    (forte)

A segunda é `REGULATORY_FACT` com granularidade de uso. É o que permite responder
"a ADAMA tem resposta registrada para ESTE alvo NESTA cultura" sem inferir.

O QUE CONTINUA NÃO SENDO PROVADO
Nenhuma linha aqui prova venda, disponibilidade comercial ou recomendação. E a extração
**falha em parte dos rótulos** — a taxa é medida e publicada por documento, nunca
arredondada para cima. Rótulo sem tabela detectada sai como `NO_TABLE_DETECTED`, que é
`NÃO SEI`, não "não tem usos".
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import italia_rotulo_parse as rp  # noqa: E402

# Assinatura da tabela: uma coluna de CULTURA e, perto, uma de DOSE ou de ALVO.
# Exigir as duas colunas é o que separa tabela de dose de qualquer frase com "coltura".
HDR = re.compile(
    r'\bcoltur[ae]\b[^.\n]{0,90}?\b(?:dos[ei]|parassit\w*|patogen\w*|avversit\w*|'
    r'infestant\w*|malatti\w*)\b', re.I)

# Onde a tabela acaba. São seções que sempre vêm DEPOIS dela.
FIM = re.compile(
    r'\b(AVVERTENZ|FITOTOSSICIT|INTERVALLO DI SICUREZZA|ATTENZIONE\b|'
    r'Registrazione\s+(?:del\s+)?Ministero|Composizione\s*:|INDICAZIONI DI PERICOLO|'
    r'CONSIGLI DI PRUDENZA|Partita n|SMALTIRE|NON APPLICARE CON I MEZZI AEREI)', re.I)

# Binômio na tabela: aqui NÃO há parênteses para validar. Dentro da tabela o alvo aparece
# nu — "Agriotes sp., Atomaria linearis, Chaetocnema tibialis" —, e a forma
# `Maiúscula + minúscula` sozinha casa qualquer frase italiana que comece com maiúscula.
#
# Medido: sem verificação, a tabela devolvia `Portare quindi` (verbo), `Adattare
# quantitativi` (verbo) e `Trisulfuron metile` (que é SUBSTÂNCIA ATIVA numa linha de
# compatibilidade de mistura, não praga) como se fossem alvos.
#
# A saída é o padrão que esta casa já usa em `normalize_agro.py`: **uma fonte propõe,
# outra verifica.** Quem propõe aqui é a rota PRECISA de `italia_rotulo_parse.alvos()`,
# que só aceita binômio entre parênteses e tem teste próprio; ela varre os 163 rótulos e
# produz o léxico de gêneros. Quem consome é a tabela. A circularidade se quebra porque
# os dois lados usam critérios diferentes: um exige parêntese, o outro exige pertencer ao
# que o parêntese já provou.
BINOMIO = re.compile(r'\b([A-Z][a-z]{3,20})\s+(spp?\.?|[a-z]{3,20})\b')

# Vocabulário de busca de cultura — o MESMO índice declarado em italia_rotulo_parse,
# reusado de propósito: duas listas divergentes seriam duas verdades.
CROPS = rp.CROP_TERMS

# Dose: número com unidade agronômica, ou faixa. É o que fecha a linha.
DOSE = re.compile(
    r'(\d+(?:[.,]\d+)?(?:\s*[-–]\s*\d+(?:[.,]\d+)?)?)\s*'
    r'(kg/ha|l/ha|ml/ha|g/ha|ml/hl|g/hl|l/hl|kg/hl|cc/hl)', re.I)

# Um epíteto específico nunca é artigo nem preposição italiana. `Peronospora` está no
# EPPO e passava no filtro de gênero, mas "Peronospora della vite" produzia o alvo
# `Peronospora della`. O gênero certo com o epíteto errado continua sendo alvo errado.
EPITETO_PROIBIDO = {
    'della', 'delle', 'dello', 'degli', 'dei', 'del', 'di', 'da', 'dal', 'dalla',
    'nel', 'nella', 'nelle', 'sul', 'sulla', 'con', 'per', 'alla', 'alle', 'allo',
    'agli', 'and', 'the', 'che', 'come', 'quindi', 'oppure', 'anche', 'sono', 'una',
    'delle', 'spp', 'sp',
}

N_APPL = re.compile(r'(?:n[°º.]?\s*max\w*\s*applicazioni|max\s*(\d+)\s*applicazion)', re.I)
INTERVALLO = re.compile(r'intervall\w*[^.]{0,40}?(\d+\s*(?:[-–]\s*\d+)?)\s*(?:giorni|gg)', re.I)

_LEXICO = None

EPPO_DICT = os.path.join(ROOT, 'data', 'samples', 'ES-T4-001', 'eppo-dictionary.json')


def lexico_de_generos(caminho=None):
    """Gêneros aceitos: os do dicionário EPPO. Verificação EXTERNA, não auto-derivada.

    A primeira tentativa construiu o léxico a partir dos próprios rótulos, pela rota de
    parênteses. Não funcionou, e a razão é medida: as DUAS ordens de captura vazam
    vernáculo italiano. A rota direta entregou `Amaranto`, `Carota`, `Loglio`; a
    invertida entregou `Erba`, `Contro`, `Muffa`. Nome comum italiano tem a mesma FORMA
    de um binômio, então nenhuma regra de forma os separa — só um verificador externo
    separa.

    O verificador é o `eppo-dictionary.json` que a rodada espanhola já preservou
    (`ES-T4-001`, extraído das tabelas oficiais do MAPA): 982 gêneros binomiais. É
    reuso, não redescoberta, e é cache-first: nenhuma requisição de rede.

    O QUE ESTA ESCOLHA CUSTA, e o custo é declarado em vez de escondido: o dicionário é
    espanhol e não cobre gêneros que só importam na Itália. `Scaphoideus` — o vetor da
    flavescência, central no `IT-HERO-001` — **não está nele**. Portanto a tabela de
    doses SUBESTIMA os alvos italianos, e o número que ela publica é piso, não teto.
    Alvos fora do EPPO continuam existindo pela rota de parênteses, em
    `italia_rotulo_parse.alvos()`; o que a tabela acrescenta é a LIGAÇÃO com a cultura.
    """
    global _LEXICO
    if _LEXICO is not None:
        return _LEXICO
    c = caminho or EPPO_DICT
    gen = set()
    if os.path.exists(c):
        import json
        d = json.load(open(c, encoding='utf-8'))
        for sec in ('crops', 'pests'):
            for v in (d.get(sec) or {}).values():
                sci = (v.get('scientific') or '').strip()
                if re.match(r'^[A-Z][a-z]{2,}\s+[a-z]', sci):
                    gen.add(sci.split()[0])
    _LEXICO = gen
    return gen


def regiao_tabela(t):
    """Devolve os trechos de tabela de dose. Vazio é 'não detectei', não 'não existe'."""
    out = []
    for m in HDR.finditer(t):
        ini = m.start()
        f = FIM.search(t, m.end())
        fim = f.start() if f else min(len(t), m.end() + 2600)
        if fim - ini > 60:
            out.append((ini, fim, t[ini:fim]))
    # funde regiões sobrepostas
    fundido = []
    for ini, fim, s in sorted(out):
        if fundido and ini <= fundido[-1][1]:
            a, b, _ = fundido[-1]
            b2 = max(b, fim)
            fundido[-1] = (a, b2, t[a:b2])
        else:
            fundido.append((ini, fim, s))
    return fundido


def _culturas_na_regiao(bloco):
    """Posições onde uma cultura do índice aparece. São as âncoras de linha."""
    achados = []
    for nome, pats in CROPS.items():
        for p in pats:
            for m in re.finditer(p, bloco, re.I):
                achados.append((m.start(), m.end(), nome, m.group(0)))
    achados.sort()
    # colapsa âncoras coladas (ex.: "Mais, Mais Dolce" é UMA linha)
    limpo = []
    for a in achados:
        if limpo and a[0] - limpo[-1][1] <= 24 and a[2] == limpo[-1][2]:
            continue
        limpo.append(a)
    return limpo


def linhas_de_uso(t, lex=None):
    """PRODUTO × CULTURA × ALVO × DOSE, extraído da região da tabela."""
    lex = lex if lex is not None else lexico_de_generos()
    saida = []
    for ini, fim, bloco in regiao_tabela(t):
        ancoras = _culturas_na_regiao(bloco)
        for i, (a0, a1, cultura, termo) in enumerate(ancoras):
            prox = ancoras[i + 1][0] if i + 1 < len(ancoras) else len(bloco)
            trecho = bloco[a0:prox]
            if len(trecho) > 900:            # linha longa demais: provavelmente não é linha
                trecho = trecho[:900]
            alvos = []
            for m in BINOMIO.finditer(trecho):
                if m.group(1) not in lex:        # gênero fora da verificação externa
                    continue
                ep = m.group(2).rstrip('.').lower()
                if ep in EPITETO_PROIBIDO and not m.group(2).lower().startswith('sp'):
                    continue
                sci = '%s %s' % (m.group(1), m.group(2))
                if sci not in alvos:
                    alvos.append(sci)
            doses = ['%s %s' % (m.group(1).replace(' ', ''), m.group(2).lower())
                     for m in DOSE.finditer(trecho)]
            napp = N_APPL.search(trecho)
            inter = INTERVALLO.search(trecho)
            # Linha sem ALVO VERIFICADO não é linha de uso autorizado: pode ser texto de
            # aplicação, de mistura ou de rotação. Dose sozinha não basta — foi
            # exatamente assim que `NICOGAN` entrou com "Portare quindi".
            if not alvos:
                continue
            saida.append({
                'CROP': cultura,
                'CROP_TERM_MATCHED': termo,
                'TARGETS': alvos[:14],
                'DOSES': doses[:6],
                'MAX_APPLICATIONS': (napp.group(1) if napp and napp.group(1) else
                                     ('DECLARADO_SEM_NUMERO' if napp else None)),
                'INTERVAL_DAYS': inter.group(1).replace(' ', '') if inter else None,
                # A força da linha é declarada: com alvo E dose é o caso completo.
                'ROW_STATE': ('CROP_TARGET_DOSE' if (alvos and doses)
                              else ('CROP_TARGET' if alvos else 'CROP_DOSE')),
                'EVIDENCE': re.sub(r'\s+', ' ', trecho[:240]),
            })
    # Âncoras sobrepostas produzem a MESMA linha duas vezes (medido em DURAVIS, que
    # devolvia MAIZE→Diabrotica virgifera duplicado). A chave é estrutural —
    # cultura + conjunto de alvos —, nunca texto.
    vistos, unicas = set(), []
    for r in saida:
        k = (r['CROP'], tuple(sorted(r['TARGETS'])))
        if k in vistos:
            continue
        vistos.add(k)
        unicas.append(r)
    return unicas


def analisar(caminho, lex=None):
    t, _ = rp.texto(caminho)
    regs = regiao_tabela(t)
    linhas = linhas_de_uso(t, lex)
    return {
        'TABLE_REGIONS': len(regs),
        'TABLE_STATE': 'DETECTED' if regs else 'NO_TABLE_DETECTED',
        'USE_ROWS': linhas,
        'ROWS_WITH_TARGET_AND_DOSE': sum(1 for r in linhas if r['ROW_STATE'] == 'CROP_TARGET_DOSE'),
    }


def main():
    d = os.path.join(ROOT, 'data', 'raw', 'IT', 'etichette')
    fs = sorted(f for f in os.listdir(d) if f.endswith('.pdf'))
    lex = lexico_de_generos()
    print('léxico de gêneros EPPO (verificação externa): %d' % len(lex))
    comtab = linhas = completas = 0
    for f in fs:
        r = analisar(os.path.join(d, f), lex)
        if r['TABLE_STATE'] == 'DETECTED':
            comtab += 1
        linhas += len(r['USE_ROWS'])
        completas += r['ROWS_WITH_TARGET_AND_DOSE']
    print('rotulos: %d · com tabela detectada: %d (%.0f%%)' % (len(fs), comtab, 100 * comtab / len(fs)))
    print('linhas de uso: %d · com alvo E dose: %d' % (linhas, completas))


if __name__ == '__main__':
    main()
