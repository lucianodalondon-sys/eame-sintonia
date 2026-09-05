#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A TRAVA DA TRADUÇÃO — prova, por máquina, que a versão traduzida não mentiu.

    python3 scripts/v21_traducao_trava.py            # confere a memória
    python3 scripts/v21_traducao_trava.py --aplicar  # confere E grava nos arquivos

O QUE ESTÁ EM JOGO
-------------------
A missão põe cinco proibições sobre a tradução:

    não acrescentar fato · não fortalecer alegação · não mudar alcance
    geográfico · não mudar confiança · não remover incerteza

Ler as 714 traduções à mão para verificar isso é o tipo de conferência que
passa no primeiro dia e não passa no décimo. Então a máquina confere o que a
máquina consegue conferir, e o que ela não alcança fica dito, não escondido.

    UMA TRAVA QUE NÃO DIZ O QUE NÃO ALCANÇA É PIOR QUE NENHUMA.

O QUE A MÁQUINA CONSEGUE PROVAR
--------------------------------
1. NÚMERO — todo número do português aparece na tradução, e nenhum número novo
   nasce. É aqui que mora «não acrescentar fato»: número inventado é fato
   inventado.
2. NEGAÇÃO — a contagem de negações não pode cair. «não prova» que vira
   «prova» é exatamente «fortalecer alegação».
3. PALAVRA DE INCERTEZA — «pode», «talvez», «apenas», «só», «nem» têm de
   sobreviver em alguma forma. Sumiço de ressalva é «remover incerteza».
4. NOME DE LUGAR — Veneto continua Veneto. Se o português diz «norte da
   Itália» e o inglês diz «Italy», o alcance mudou.
5. MAIÚSCULA DE ÊNFASE — as palavras que escrevi em CAIXA ALTA são a lei do
   registro. Se somem, some o aviso.

O QUE ELA NÃO CONSEGUE
-----------------------
Ela não sabe se «autorizza» quer dizer «autoriza». Nenhuma trava mecânica sabe.
Essa parte é leitura humana, e o relatório diz quantas frases dependem dela.
"""
import json
import os
import re
import sys
import unicodedata
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
TM = os.path.join(ROOT, 'data', 'i18n', 'v21-traducoes.json')

sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from v21_campos_de_lingua import (LEITURA, MISTO, PROMOVE, campos_do_registro,  # noqa
                                  parte_minha, e_portugues)

# ⚠️ ESTAS LISTAS JÁ ESTIVERAM ERRADAS, e o erro tinha uma cara só: faltava
# palavra. «NÃO-RENOVAÇÃO» virou «NON-RENEWAL» e a trava disse que a negação
# tinha sumido — porque `non` não estava na lista. «não prova nada» virou
# «proves nothing», e faltava `nothing`.
#
#     TRAVA COM VOCABULÁRIO CURTO NÃO PEGA MENTIRA: PEGA SINÔNIMO.
#
# E o pior é o efeito: reprova o certo, ensina a ignorar, e no dia em que
# reprovar o errado ninguém olha.
NEG_PT = re.compile(r'\b(nao|não|nem|nunca|jamais|sem|nada|nenhum\w*|'
                    r'ausencia|ausência|falta)\b|\bnão-|\bnao-', re.I)
NEG_IT = re.compile(r'\b(non|né|ne|mai|senza|nessun\w*|nulla|niente|'
                    r'mancan\w+|mancat\w+|assenza|carenza|impossibil\w+)\b'
                    r'|\bnon-', re.I)
NEG_EN = re.compile(r"\b(not|no|never|without|nor|neither|n't|cannot|non\w*|"
                    r"nothing|none|nobody|absence|lack\w*|fails?|failure|"
                    r"unable|impossible)\b|\bnon-", re.I)

# ⚠️ «NÃO PODE» É PROIBIÇÃO, NÃO HESITAÇÃO. A trava contava o «pode» de «não
# pode ser citado» como incerteza e cobrava um «may» do inglês — que ali seria
# ERRADO, porque o inglês certo é «cannot». Cobrar hedge onde a frase proíbe é
# pedir que a tradução afrouxe justamente o que a missão manda manter firme.
PROIBICAO = re.compile(r'\b(n[aã]o|nunca|jamais)\s+(pode|podem|poderia|'
                       r'poderiam|deve|devem)\b', re.I)

INC_PT = re.compile(r'\b(pode|podem|talvez|apenas|so|só|somente|parece|'
                    r'indica|sugere|possivel|possível|estimad\w+)\b', re.I)
INC_IT = re.compile(r'\b(pu[oò]|possono|potrebb\w+|forse|sol[oaei]|soltanto|'
                    r'unic\w+|sembra|indica|suggerisce|possibil\w+|stimat\w+|'
                    r'appena|semplicemente|almeno|perlomeno|circa|una volta)\b',
                    re.I)
INC_EN = re.compile(r'\b(may|might|can|could|only|just|alone|single|solely|'
                    r'merely|seems|appears|indicates|suggests|possible|'
                    r'estimated|about|roughly|approximately|at once|in one|'
                    r'in a single|one pass|at least|unable|looks?\s+like|'
                    r'apparently|presumably)\b', re.I)

# ⚠️ Nome de lugar é alcance. Trocar um por outro é mudar de quem se fala.
#
# MAS O LUGAR TEM NOME DIFERENTE EM CADA LÍNGUA, e essa é a armadilha: a
# primeira versão desta trava reprovou «Bruxelas → Bruxelles → Brussels» como se
# a cidade tivesse sumido. A tradução estava certa; a trava é que era burra.
#
#     UMA TRAVA QUE REPROVA O CERTO ENSINA A IGNORAR TRAVA.
#
# Então cada lugar é um GRUPO de nomes. Some quando nenhum nome do grupo
# aparece — não quando some a grafia portuguesa dele.
LUGARES = [
    ('Bruxelas', 'Bruxelles', 'Brussels', 'Bruxelas'),
    ('Sicilia', 'Sicilia', 'Sicily', 'Sicília'),
    ('Sardegna', 'Sardegna', 'Sardinia', 'Sardenha'),
    ('Lombardia', 'Lombardia', 'Lombardy'),
    ('Piemonte', 'Piemonte', 'Piedmont'),
    ('Toscana', 'Toscana', 'Tuscany'),
    ('Puglia', 'Puglia', 'Apulia'),
    ('Russia', 'Russia', 'Russian'),
    ('Italia', 'Italia', 'Italy', 'Itália', 'Italian', 'italiana'),
    ('Emilia-Romagna', 'Emilia Romagna', 'Emilia'),
    ('Alto Adige', 'South Tyrol', 'Sudtirol'),
    ('Veneto',), ('Campania',), ('Lazio',), ('Marche',), ('Umbria',),
    ('Abruzzo',), ('Molise',), ('Calabria',), ('Basilicata',), ('Liguria',),
    ('Trentino',), ('Bolzano',), ('Trento',), ('Friuli',), ('Valle',),
    ('Modena',), ('Bologna',), ('Ravenna',), ('Forli',), ('Cesena',),
    ('Rovigo',), ('Vercelli',), ('Novara',), ('Pavia',),
]


# ⚠️ A DATA MUDA DE ROUPA AO MUDAR DE LÍNGUA e a primeira versão desta trava não
# sabia disso: «30/01/2026» virou «30 January 2026» e ela reclamou que o número
# 01 tinha sumido. Não sumiu — virou palavra.
#
#     UM MÊS ESCRITO POR EXTENSO CONTINUA SENDO O MESMO MÊS.
# ⚠️ A tabela nasceu SEM OS MESES EM PORTUGUÊS, e o efeito foi silencioso: em
# «setembro de 2026» o ano ficava solto, na tradução «September 2026» ele era
# reconhecido como data e saía — e a trava acusava número desaparecido. O
# português é a LÍNGUA DE ORIGEM: esquecê-lo aqui foi esquecer o lado que manda.
MESES = {
    1: ('gennaio', 'january', 'jan', 'janeiro'),
    2: ('febbraio', 'february', 'feb', 'fevereiro'),
    3: ('marzo', 'march', 'mar', 'marco', 'março'),
    4: ('aprile', 'april', 'apr', 'abril'),
    5: ('maggio', 'may', 'maio'),
    6: ('giugno', 'june', 'jun', 'junho'),
    7: ('luglio', 'july', 'jul', 'julho'),
    8: ('agosto', 'august', 'aug'),
    9: ('settembre', 'september', 'sep', 'setembro'),
    10: ('ottobre', 'october', 'oct', 'outubro'),
    11: ('novembre', 'november', 'nov', 'novembro'),
    12: ('dicembre', 'december', 'dec', 'dezembro'),
}
DATA = re.compile(r'\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b')

# ⚠️ «(10/03, 19/03 e 09/04/2026)» — as duas primeiras NÃO TÊM ANO, e o ano de
# quem vem depois vale para elas. Sem isto o dia e o mês ficam soltos como
# números avulsos, e a tradução «10 March» parece ter perdido o 03.
#
# ⚠️ E SÓ COM BARRA. A primeira versão aceitava ponto e hífen, e passou a ler
# «94,3%» como «dia 94, mês 3» e «0-1%» como data — apagando números REAIS antes
# da conferência. Uma trava que apaga o que deveria conferir não protege nada.
DATA_CURTA = re.compile(r'\b(\d{1,2})/(0?[1-9]|1[0-2])\b(?!\s*/\s*\d)')


def datas(t):
    """As datas como (dia, mês, ano) — não como três números soltos."""
    return {(int(a), int(b), int(c)) for a, b, c in DATA.findall(t)}


def data_presente(d, alvo):
    """A data chegou? Em número ou com o mês por extenso, tanto faz."""
    dia, mes, ano = d
    a = sem_acento(alvo)
    if str(ano) not in a:
        return False
    if DATA.search(alvo) and d in datas(alvo):
        return True
    tem_dia = re.search(r'\b0?%d\b' % dia, a)
    tem_mes = (re.search(r'\b0?%d\b' % mes, a)
               or any(n in a for n in MESES.get(mes, ())))
    return bool(tem_dia and tem_mes)


_NOMES_MES = '|'.join(sorted({n for v in MESES.values() for n in v}, key=len,
                             reverse=True))
# «30 January 2026», «January 30, 2026», «30 gennaio 2026», «de agosto de 2026»
DATA_EXTENSO = re.compile(
    r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:de\s+|di\s+)?(?:%s)\w*\s*,?\s*(?:de\s+)?\d{4}\b'
    r'|\b(?:%s)\w*\s+\d{1,2}(?:st|nd|rd|th)?\s*,?\s*\d{4}\b'
    r'|\b(?:%s)\w*\s+(?:de\s+|di\s+|del\s+)?\d{4}\b'
    # ⚠️ E O DIA SEM ANO. «10/03, 19/03 e 09/04/2026» vira «10 March, 19 March
    # and 9 April 2026»: só a última carrega o ano, e as duas primeiras ficavam
    # com o dia solto — a trava as lia como NÚMERO NOVO, isto é, fato inventado.
    r'|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:de\s+|di\s+)?(?:%s)\w*\b'
    % (_NOMES_MES, _NOMES_MES, _NOMES_MES, _NOMES_MES), re.I)

# ⚠️ «uma decada de 10 dias» virou «a ten-day period» — e o tradutor estava
# CERTO: em inglês «decade» significaria dez anos. O 10 não sumiu; virou
# palavra. Sem esta tabela, a trava reprova exatamente a tradução mais cuidadosa.
POR_EXTENSO = {
    '1': ('one', 'uno', 'una'), '2': ('two', 'due'), '3': ('three', 'tre'),
    '4': ('four', 'quattro'), '5': ('five', 'cinque'), '6': ('six', 'sei'),
    '7': ('seven', 'sette'), '8': ('eight', 'otto'), '9': ('nine', 'nove'),
    '10': ('ten', 'dieci'), '11': ('eleven', 'undici'), '12': ('twelve', 'dodici'),
    '15': ('fifteen', 'quindici'), '20': ('twenty', 'venti'),
    '30': ('thirty', 'trenta'), '100': ('hundred', 'cento'),
}


def numeros(t):
    """Todo número que NÃO é parte de data. 1.063.378 e 1063378 são o mesmo.

    ⚠️ A data por extenso também sai. «30/01/2026» em inglês vira «30 January
    2026», e os dígitos 30 e 2026 ficariam soltos — a trava os leria como
    NÚMERO NOVO, isto é, como fato inventado. Não são: são a mesma data com
    outra roupa.
    """
    t = DATA_CURTA.sub(' ', DATA_EXTENSO.sub(' ', DATA.sub(' ', t)))
    fora = []
    for m in re.finditer(r'\d[\d.,]*', t):
        v = m.group(0).rstrip('.,')
        fora.append(re.sub(r'[.,]', '', v))
    return Counter(fora)


# ⚠️ ALGARISMO ROMANO NÃO É ÊNFASE. «IV trimestre de 2025» virou «fourth quarter
# of 2025», e a trava acusou perda de CAIXA ALTA — mas «IV» é um NÚMERO escrito
# com letras, e o inglês o escreveu com uma palavra. Nada se perdeu.
ROMANO = re.compile(r'^(?=[IVXLCDM]+$)M*(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})'
                    r'(IX|IV|V?I{0,3})$')


def caixa_alta(t):
    """Toda palavra em CAIXA ALTA, de duas letras para cima — sem os romanos."""
    return {w for w in re.findall(r'\b[A-ZÀ-Ý]{2,}\b', t)
            if not ROMANO.match(w)}


def enfase(pt, alvo):
    """A CAIXA ALTA que é ênfase de cada lado — sem as siglas.

    ⚠️ Contar caixa alta por TAMANHO da palavra não funciona, e as duas tentativas
    anteriores mostram por quê: em quatro letras, «derivacao NOSSA → OUR
    derivation» reprovava; em três, «NAO falta → NO unit is missing» reprovava.
    A ênfase muda de tamanho ao mudar de língua, porque a palavra muda.

    O que NÃO muda é a sigla: CDI, BBCH, ADAMA, ISTAT aparecem iguais nos dois
    textos. Então elas se cancelam, e o que sobra de cada lado é a ênfase de
    verdade — que aí sim tem de existir dos dois lados.

        SIGLA NÃO É GRITO. O QUE APARECE IGUAL NAS DUAS LÍNGUAS NÃO É ÊNFASE.
    """
    a, b = caixa_alta(pt), caixa_alta(alvo)
    comum = a & b
    return a - comum, b - comum


def sem_acento(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t)
                   if unicodedata.category(c) != 'Mn').lower()


def conferir(pt, alvo, lingua):
    """Lista de problemas. Lista vazia = passou no que a máquina alcança."""
    p = []
    if not alvo or not str(alvo).strip():
        return ['VAZIA']

    # 1 · data — conferida como data, não como três números soltos
    for d in datas(pt):
        if not data_presente(d, alvo):
            p.append('DATA_SUMIU:%02d/%02d/%d' % d)

    # 2 · número — PRESENÇA, e sempre contra o texto CRU do outro lado
    #
    # ⚠️ Duas armadilhas derrubaram as versões anteriores desta conferência:
    #
    # CONTAGEM. «essas 10 praças» aparece duas vezes no português e uma no
    # inglês, que reusa «these 10» só uma vez. Nenhum fato se perdeu — repetir
    # não informa, e deixar de repetir não desinforma.
    #
    # DATA AMBÍGUA. «os outros 3 de agosto» é «os outros três, de agosto» — mas
    # a regra de data leu «3 de agosto» e comeu o número, que então reapareceu
    # no inglês como se tivesse nascido do nada.
    #
    #     A PERGUNTA CERTA NÃO É «QUANTAS VEZES», É «ESTÁ LÁ?».
    #     E a resposta se procura no texto inteiro do outro lado, não no que
    #     sobrou depois de eu recortar as datas dele.
    cru_pt, cru_al = sem_acento(pt), sem_acento(alvo)

    def _esta(n, cru, texto_limpo):
        if n in texto_limpo:
            return True
        if re.search(r'\b0*%s\b' % re.escape(n), cru):
            return True          # está lá, só que dentro de uma data
        return any(w in cru for w in POR_EXTENSO.get(n, ()))   # virou palavra

    a, b = set(numeros(pt)), set(numeros(alvo))
    sumiu = {n for n in a if not _esta(n, cru_al, b)}
    nasceu = {n for n in b if not _esta(n, cru_pt, a)}
    if sumiu:
        p.append('NUMERO_SUMIU:%s' % ','.join(sorted(sumiu)))
    if nasceu:
        p.append('NUMERO_NASCEU:%s' % ','.join(sorted(nasceu)))

    # 3 · negação — PRESENÇA, não proporção
    #
    # ⚠️ O português empilha o que o inglês diz uma vez só: «não prova A nem B»
    # vira «does not prove A or B». Contar negação por proporção reprovava
    # tradução correta — e o que interessa nunca foi a contagem:
    #
    #     O QUE NÃO PODE ACONTECER É A FRASE NEGATIVA VIRAR AFIRMATIVA.
    n_pt = len(NEG_PT.findall(pt))
    n_al = len((NEG_IT if lingua == 'IT' else NEG_EN).findall(alvo))
    if n_pt and not n_al:
        p.append('NEGACAO_SUMIU:%d->0' % n_pt)

    # 4 · incerteza — presença, e sem confundir proibição com hesitação
    i_pt = len(INC_PT.findall(PROIBICAO.sub(' ', pt)))
    i_al = len((INC_IT if lingua == 'IT' else INC_EN).findall(alvo))
    if i_pt and not i_al:
        p.append('INCERTEZA_SUMIU:%d->0' % i_pt)

    # 5 · lugar — o grupo inteiro conta como o mesmo lugar
    spt, salvo = sem_acento(pt), sem_acento(alvo)
    for grupo in LUGARES:
        na_origem = any(re.search(r'\b%s\b' % re.escape(sem_acento(n)), spt)
                        for n in grupo)
        if not na_origem:
            continue
        # no destino basta QUALQUER nome do grupo, e por prefixo: «Bruxelles»
        # e «Brussels» nao compartilham as 5 primeiras letras, mas sao a cidade.
        if not any(re.search(r'\b%s' % re.escape(sem_acento(n)[:4]), salvo)
                   for n in grupo):
            p.append('LUGAR_SUMIU:%s' % grupo[0])

    # 6 · ênfase
    c_pt, c_al = enfase(pt, alvo)
    if c_pt and not c_al:
        p.append('CAIXA_ALTA_CAIU:%s->nada' % ','.join(sorted(c_pt)[:4]))

    return p


def carregar_tm():
    if not os.path.exists(TM):
        return {}
    d = json.load(open(TM, encoding='utf-8'))
    return {x['PT']: x for x in d.get('TRADUCOES', d if isinstance(d, list) else [])}


def main():
    aplicar = '--aplicar' in sys.argv
    tm = carregar_tm()
    if not tm:
        print('memoria de traducao vazia: %s' % TM)
        return 1

    # ── confere ──────────────────────────────────────────────────────────────
    ruins, ok = [], 0
    for pt, e in tm.items():
        for lg in ('IT', 'EN'):
            pb = conferir(pt, e.get(lg), lg)
            if pb:
                ruins.append((lg, pt[:70], pb))
            else:
                ok += 1
    print('memoria: %d frases · %d versoes limpas · %d com problema'
          % (len(tm), ok, len(ruins)))
    if ruins:
        print()
        for lg, t, pb in ruins[:40]:
            print('  [%s] %s\n        %s' % (lg, t, ' · '.join(pb)))
        if len(ruins) > 40:
            print('  ... e mais %d' % (len(ruins) - 40))
        print('\nPARADO: traducao com problema nao entra no pacote.')
        return 1

    if not aplicar:
        print('\n(nada gravado — rode com --aplicar)')
        return 0

    # ── aplica ───────────────────────────────────────────────────────────────
    tocados, faltando, subiram = Counter(), Counter(), Counter()
    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq.startswith('CANONICAL'):
            continue
        p = os.path.join(ING, arq)
        d = json.load(open(p, encoding='utf-8'))
        n = 0
        for r in d.get('RECORDS') or []:
            if not isinstance(r, dict) or not r.get('ID'):
                continue
            for campo, v, de_research in campos_do_registro(r):
                meu, cauda = parte_minha(campo, v)
                if not e_portugues(meu):
                    continue
                e = tm.get(meu.strip())
                if not e:
                    faltando[campo] += 1
                    continue
                # ⚠️ O ORIGINAL NUNCA SOME. A traducao fica AO LADO, nao no lugar.
                r[campo + '_ORIGINAL_RESEARCH_TEXT'] = v
                r[campo + '_IT'] = e['IT'] + cauda
                r[campo + '_EN'] = e['EN'] + cauda
                if de_research:
                    # ⚠️ Este registro NAO TINHA campo client-facing: a leitura
                    # so existia dentro de RESEARCH, em portugues. Ela sobe agora
                    # — porque uma ressalva que a tela nao mostra e uma ressalva
                    # que nao existe. O bloco RESEARCH fica intacto embaixo.
                    r[campo + '_PROMOVIDO_DE'] = 'RESEARCH.%s' % next(
                        k for k, dst in PROMOVE.items() if dst == campo)
                    subiram[campo] += 1
                n += 1
        if n:
            d['LOCALIZED_FIELDS'] = sorted({k[:-3] for x in d['RECORDS']
                                            if isinstance(x, dict)
                                            for k in x if k.endswith('_IT')})
            d['LOCALIZATION_LAW'] = (
                'a traducao fica AO LADO do original, nunca no lugar dele. '
                'ORIGINAL_RESEARCH_TEXT guarda a prosa de pesquisa; _IT e _EN sao '
                'a mesma leitura noutra lingua. Citacao publica NAO foi traduzida: '
                'a palavra da fonte e a prova, e traduzir prova e adultera-la.')
            json.dump(d, open(p, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            tocados[arq] = n

    print('\ncampos localizados:')
    for k, v in tocados.most_common():
        print('  %-34s %6d' % (k, v))
    print('total: %d' % sum(tocados.values()))
    if subiram:
        print('\nsubiram de RESEARCH para o topo (nao tinham campo na tela): %d'
              % sum(subiram.values()))
        for k, v in subiram.most_common():
            print('  %-34s %6d' % (k, v))
    if faltando:
        print('\nAINDA EM PORTUGUES (sem traducao na memoria): %d'
              % sum(faltando.values()))
        for k, v in faltando.most_common(12):
            print('  %-34s %6d' % (k, v))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
