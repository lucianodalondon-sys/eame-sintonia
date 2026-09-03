#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A JANELA AGRONÔMICA · o que ela é, e o que ela não é.

    python3 scripts/v21_janelas.py      # inspeção: mede o acervo, não grava

O DEFEITO DE DEFINIÇÃO
----------------------
O motor tratava JANELA como INTERVALO DE CALENDÁRIO. Só um campo com duas datas
virava janela; tudo o mais virava `UNKNOWN`. Medido no acervo: das orações
atribuídas a um par cultura × alvo, **nenhuma** declara a janela por datas — e
14 declaram por FENOLOGIA, 3 por LIMIAR, 3 por ATO ADMINISTRATIVO, 2 por FASE
DA PRAGA e 1 por CONDIÇÃO CLIMÁTICA.

    O SERVIÇO FITOSSANITÁRIO NÃO ESCREVE «DE 3 A 18 DE JUNHO».
    ELE ESCREVE «EM PRÉ-COLHEITA», «AO ULTRAPASSAR 5%», «EM CONDIÇÕES
    PREDISPONENTES». ISSO É JANELA — SÓ NÃO É CALENDÁRIO.

Chamar de «sem janela» um boletim que diz QUANDO agir é perder a informação que
a fonte deu. E chamar de «janela aberta» o mesmo boletim sem saber se a condição
está satisfeita é inventar a que ela não deu.

AS DUAS PERGUNTAS, QUE NUNCA SÃO A MESMA
----------------------------------------
    WINDOW_DEFINED   → sabemos QUAL condição define o momento certo?
    WINDOW_OPEN_NOW  → há evidência de que a condição está satisfeita AGORA?

«Intervir em pré-colheita» define a janela. Se o MESMO documento declara que a
cultura está em maturação, a condição está satisfeita agora. Se não declara,
`WINDOW_OPEN_NOW = UNKNOWN` — e não há `ACT_NOW`.

    DEFINIDA NÃO É ABERTA. SABER O GATILHO NÃO É SABER QUE ELE DISPAROU.

⚠️ `ADMINISTRATIVE_WINDOW` NUNCA vira janela agronômica automaticamente. A
Determinazione 9818/2026 da Emilia-Romagna fixa datas de tratamento OBRIGATÓRIO
contra o vetor da flavescenza: é prazo de norma, e vale para o alvo que a norma
nomeia — não para a botrite da mesma videira.
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_normalizar as N  # noqa: E402
import v21_necessidade as NE  # noqa: E402

# ── OS TIPOS, TODOS MEDIDOS NO ACERVO ANTES DE EXISTIREM ────────────────────
CALENDAR_WINDOW = 'CALENDAR_WINDOW'
PHENOLOGY_WINDOW = 'PHENOLOGY_WINDOW'
PREHARVEST_WINDOW = 'PREHARVEST_WINDOW'
THRESHOLD_WINDOW = 'THRESHOLD_WINDOW'
WEATHER_TRIGGERED_WINDOW = 'WEATHER_TRIGGERED_WINDOW'
PEST_STAGE_WINDOW = 'PEST_STAGE_WINDOW'
ADMINISTRATIVE_WINDOW = 'ADMINISTRATIVE_WINDOW'

TIPOS = (CALENDAR_WINDOW, PREHARVEST_WINDOW, PHENOLOGY_WINDOW, THRESHOLD_WINDOW,
         PEST_STAGE_WINDOW, WEATHER_TRIGGERED_WINDOW, ADMINISTRATIVE_WINDOW)

# Os que dizem QUANDO A PLANTA/PRAGA está pronta — janela agronômica de verdade.
AGRONOMICOS = (CALENDAR_WINDOW, PREHARVEST_WINDOW, PHENOLOGY_WINDOW,
               THRESHOLD_WINDOW, PEST_STAGE_WINDOW, WEATHER_TRIGGERED_WINDOW)

# ── OS PADRÕES, EM ORDEM DE PRECEDÊNCIA ─────────────────────────────────────
# Precedência importa: «intervir em pré-colheita» é PREHARVEST, não FENOLOGIA
# genérica; e um trecho que cita determinação É administrativo mesmo que
# também nomeie uma fase.
_P = [
 (ADMINISTRATIVE_WINDOW, [
    r'\bdeterminazione\b', r'\bdetermina n', r'\bddr n', r'\bdecreto\b',
    r'\bderoga\b', r'\blotta obbligatoria\b', r'\bimpiego consentito\b',
    r'\bobrigatori\w+ por norma\b', r'\bconforme a determina\w*']),

 (PREHARVEST_WINDOW, [
    r'\bpre[- ]?colheita\b', r'\bpre[- ]?raccolta\b', r'\bpreraccolta\b',
    r'\bprossimita della raccolta\b', r'\bem prox\w+ (?:da|de) colheita\b',
    r'\bantes da colheita\b', r'\bpre[- ]?vindima\b',
    r'\bin prossimita della raccolta\b']),

 (THRESHOLD_WINDOW, [
    r'\bao ultrapassar\b', r'\bal superamento\b', r'\bsuperamento del\b',
    r'\bsoglia\b', r'\blimiar\b', r'\bacima d[eoa]\b.{0,30}\d',
    r'\bsuperiore[s]? a \d', r'\bsuperiores a \d', r'\b\d+\s?%\s*(?:de|di)\b']),

 (PEST_STAGE_WINDOW, [
    r'\bvolo\b', r'\bvoo\b', r'\bgenerazione\b', r'\bgeracao\b',
    r'\bovideposi\w*', r'\bsfarfallament\w*', r'\bstadi giovanili\b',
    r'\bneanidi\b', r'\bnascita\b', r'\bformas juvenis\b']),

 (WEATHER_TRIGGERED_WINDOW, [
    r'\bem caso de (?:chuva|temporal|granizo)\b',
    r'\bin caso di (?:pioggia|temporal|grandine)\b',
    r'\bjunto de chuva\b', r'\bdopo le piogge\b',
    r'\bmolhamento\b', r'\bbagnatura\b',
    r'\bcondicoes predisponentes\b', r'\bcondizioni predisponenti\b',
    r'\bcondicoes ideais para\b']),

 # ⚠️ O ESTÁDIO SOZINHO NÃO É JANELA. «espigas em maturacao avancada» descreve
 # a planta; não manda tratar em maturação. A janela é a LIGAÇÃO entre uma ação
 # e um estádio — «a partir da invaiatura», «na fase de maior suscetibilidade» —
 # e por isso os padrões exigem a preposição que amarra os dois.
 #
 #     O ESTÁDIO É O ESTADO DA PLANTA. A JANELA É O ESTADO AMARRADO A UMA AÇÃO.
 #     LER A PALAVRA SOLTA FOI O QUE PÔS «maturacao» DO MILHO COMO JANELA ABERTA
 #     NUMA ORAÇÃO QUE DIZIA EXATAMENTE O CONTRÁRIO.
 (PHENOLOGY_WINDOW, [
    r'\ba partir d[ao]\b[^.;]{0,40}\b(?:invaiatura|maturac\w+|maturaz\w+|'
    r'fioritura|floracao|sfioritura|allegagione|accrescimento|raccolta|colheita)\b',
    r'\b(?:dalla|nella|alla|dopo la|prima della) fase\b',
    r'\bna fase de\b', r'\bem fase de\b', r'\bin fase di\b',
    r'\bbbch \d', r'\ba partir da viragem de cor\b',
    r'\bao (?:atingir|chegar a)\b[^.;]{0,30}\bfase\b']),

 (CALENDAR_WINDOW, [
    r'\b\d{1,2}/\d{1,2}/\d{4}\b', r'\b\d{4}-\d{2}-\d{2}\b',
    r'\ba partir de \d{1,2} de \w+', r'\bdal \d{1,2}\b', r'\bentro il \d{1,2}\b',
    r'\bfino al \d{1,2}\b', r'\bate o fim de \w+\b']),
]


def tipos_da_oracao(oracao):
    """→ [(TIPO, padrão que casou)], em ordem de precedência. Pode ser vazio."""
    t = N._n(oracao)
    fora = []
    for tipo, padroes in _P:
        for p in padroes:
            if re.search(p, t):
                fora.append((tipo, p))
                break
    return fora


# ── A EQUIVALÊNCIA FENOLÓGICA, DECLARADA — NÃO INFERIDA ─────────────────────
#
# Esta tabela é LÉXICO, da mesma espécie de `CROP_ALIAS`: ela diz que palavras a
# fonte usa para o mesmo estádio. Não é dedução sobre o campo; é vocabulário, e
# está escrita aqui para poder ser contestada lendo-a.
#
#     A EQUIVALÊNCIA É NOSSA E ESTÁ ESCRITA. INFERÊNCIA É A QUE NÃO SE VÊ.
#
# `PREHARVEST` é satisfeito pelos estádios que a própria escala BBCH põe entre a
# maturação e a colheita — é o intervalo que «pré-colheita» nomeia.
FENOLOGIA_QUE_SATISFAZ = {
    PREHARVEST_WINDOW: ('maturazione', 'maturacao', 'invaiatura', 'raccolta',
                        'colheita', 'vindima', 'bbch 8', 'addolcimento'),
    PHENOLOGY_WINDOW: (),      # comparado contra a própria condição, abaixo
}

_ASPA = re.compile(r'«([^»]*)»')


def estagio_do_documento(sinal, crop):
    """→ o estádio que ESTE documento declara para ESTA cultura, ou None.

    `PHENOLOGICAL_STAGE_DECLARED` é prosa por cultura — «Vite: «maturazione».
    Pero: «maturazione».» — e a cultura tem de estar nomeada no mesmo pedaço.
    """
    txt = sinal.get('PHENOLOGICAL_STAGE_DECLARED')
    if not txt or sinal.get('CROP_STATE') != 'DECLARED_BY_SOURCE':
        return None
    if str(txt).strip().upper().startswith(('NAO SEI', 'NÃO SEI', 'NAO SE APLICA')):
        return None
    for pedaco in re.split(r'(?<=[.;])\s+', str(txt)):
        if crop in N.crops_no_texto(pedaco):
            return pedaco.strip()
    # documento de uma cultura só: a prosa inteira é dela
    if len(sinal.get('CROP_IDS') or []) == 1 and (sinal['CROP_IDS'][0] == crop):
        return str(txt).strip()
    return None


def aberta_agora(tipo, oracao, estagio, corrente):
    """→ ('YES'|'UNKNOWN'|'NO', método). A segunda pergunta, nunca a primeira.

    Só a fenologia se fecha com o que o acervo tem: o documento declara o
    estádio da cultura. Limiar, clima e fase da praga dependem de medição que
    ninguém nos deu — e por isso `UNKNOWN`, que é a resposta honesta.
    """
    if not corrente:
        return 'UNKNOWN', 'DOCUMENTO_NAO_CORRENTE'
    if tipo == ADMINISTRATIVE_WINDOW:
        return 'NO', 'ATO_ADMINISTRATIVO_NAO_E_JANELA_AGRONOMICA'
    if tipo in (THRESHOLD_WINDOW, WEATHER_TRIGGERED_WINDOW, PEST_STAGE_WINDOW):
        return 'UNKNOWN', 'CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS'
    if not estagio:
        return 'UNKNOWN', 'DOCUMENTO_NAO_DECLARA_ESTADIO_DA_CULTURA'
    e = N._n(estagio)
    if tipo == PREHARVEST_WINDOW:
        if any(v in e for v in FENOLOGIA_QUE_SATISFAZ[PREHARVEST_WINDOW]):
            return 'YES', 'ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO'
        return 'NO', 'ESTADIO_DECLARADO_NAO_SATISFAZ_A_CONDICAO'
    if tipo == PHENOLOGY_WINDOW:
        # a condição nomeia o próprio estádio: basta a fonte declarar o mesmo
        cond = N._n(oracao)
        for termo in ('invaiatura', 'maturazione', 'maturacao', 'fioritura',
                      'floracao', 'accrescimento', 'ingrossamento', 'raccolta',
                      'colheita', 'sfioritura', 'allegagione'):
            if termo in cond and termo in e:
                return 'YES', 'ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO'
        return 'UNKNOWN', 'ESTADIO_DECLARADO_NAO_NOMEIA_A_CONDICAO'
    return 'UNKNOWN', 'TIPO_SEM_REGRA_DE_ABERTURA'


def janelas_do_sinal(sinal):
    """→ candidatas de janela deste registro, por par cultura × alvo."""
    corrente = True
    fora = []
    for campo, metodo, crops, issues, oracao in NE.atribuicoes(sinal):
        tipos = tipos_da_oracao(oracao)
        if not tipos:
            continue
        direcao, _padrao = NE.direcao(oracao)
        for c in crops:
            estagio = estagio_do_documento(sinal, c)
            for i in issues:
                for tipo, padrao in tipos:
                    aberta, como = aberta_agora(tipo, oracao, estagio, corrente)
                    # ⚠️ INTELIGÊNCIA NEGATIVA SE PRESERVA. Uma oração que manda
                    # PARAR também declara um momento — o de não tratar. Ela
                    # entra no inventário como janela FECHADA, não desaparece.
                    if direcao in NE.RESTRITIVOS:
                        aberta, como = 'NO', 'A_ORACAO_MANDA_PARAR'
                    fora.append({
                        'CROP': c, 'TARGET': i,
                        'REGION_IDS': sinal.get('REGION_IDS') or [],
                        'SOURCE_ID': sinal['ID'],
                        'SOURCE_FIELD': campo, 'PAIR_METHOD': metodo,
                        'WINDOW_TYPE': tipo,
                        'WINDOW_CONDITION': oracao[:320],
                        'MATCHED_PATTERN': padrao,
                        'PHENOLOGY_DECLARED': estagio,
                        'WINDOW_DEFINED': 'YES',
                        'CLAUSE_DIRECTION': direcao,
                        'WINDOW_OPEN_NOW': aberta,
                        'OPEN_NOW_METHOD': como,
                        'SOURCE_EXCERPT': oracao[:320],
                    })
    return fora


def main():
    ing = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
    sinais = [r for r in json.load(
        open(os.path.join(ing, 'CURRENT-FIELD-SIGNALS.json'), encoding='utf-8')
    )['RECORDS'] if r.get('CLIENT_SAFE')]
    todas = [j for s in sinais for j in janelas_do_sinal(s)]
    print('sinais client-safe: %d · candidatas de janela: %d'
          % (len(sinais), len(todas)))
    print('\nPOR TIPO')
    for t, n in Counter(j['WINDOW_TYPE'] for j in todas).most_common():
        print('  %-26s %d' % (t, n))
    print('\nWINDOW_OPEN_NOW')
    for t, n in Counter(j['WINDOW_OPEN_NOW'] for j in todas).most_common():
        print('  %-26s %d' % (t, n))
    print('\nPARES COM JANELA DEFINIDA')
    pares = Counter((j['CROP'], j['TARGET']) for j in todas)
    for (c, i), n in pares.most_common():
        print('  %-22s x %-24s %d' % (c.replace('CROP_', ''),
                                      i.replace('ISSUE_', ''), n))
    fora = {
        'COLLECTION': 'V113-INVENTARIO-DE-JANELAS',
        'SOURCE': 'build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/'
                  'CURRENT-FIELD-SIGNALS.json · regra de scripts/v21_janelas.py',
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'inventario do que o acervo JA DIZ sobre o momento de intervir. '
               'Nenhuma coleta nova. Campos ausentes ficam UNKNOWN.',
        'SIGNALS_READ': len(sinais),
        'BY_TYPE': dict(Counter(j['WINDOW_TYPE'] for j in todas)),
        'BY_OPEN_NOW': dict(Counter(j['WINDOW_OPEN_NOW'] for j in todas)),
        'CANDIDATES': todas,
    }
    saida = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                         'V113-INVENTARIO-DE-JANELAS.json')
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    json.dump(fora, open(saida, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('\ngravado em %s' % os.path.relpath(saida, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
