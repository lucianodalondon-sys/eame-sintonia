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
# ⚠️ O OITAVO TIPO NÃO SAIU DE UMA IDEIA: SAIU DE UM DOCUMENTO.
# «Per cui le decisioni devono essere necessariamente basate sulle osservazioni
# aziendali» — Manuale difesa integrata del melo, Regione del Veneto. A regra
# existe, é publicada, e o que ela publica é que o gatilho é do pomar.
#
#     SABER QUE A REGRA MANDA MEDIR NO POMAR É SABER A REGRA.
#     E CONTINUAR SEM A MEDIÇÃO É CONTINUAR SEM SABER SE A JANELA ESTÁ ABERTA.
RULE_DELEGATED_TO_FARM = 'RULE_DELEGATED_TO_FARM'

TIPOS = (CALENDAR_WINDOW, PREHARVEST_WINDOW, PHENOLOGY_WINDOW, THRESHOLD_WINDOW,
         PEST_STAGE_WINDOW, WEATHER_TRIGGERED_WINDOW, ADMINISTRATIVE_WINDOW,
         RULE_DELEGATED_TO_FARM)

# Os que dizem QUANDO A PLANTA/PRAGA está pronta — janela agronômica de verdade.
# A regra delegada entra por último: se houver uma condição regional declarada
# para o mesmo par, é ela que responde, e a delegação fica de reserva.
AGRONOMICOS = (CALENDAR_WINDOW, PREHARVEST_WINDOW, PHENOLOGY_WINDOW,
               THRESHOLD_WINDOW, PEST_STAGE_WINDOW, WEATHER_TRIGGERED_WINDOW,
               RULE_DELEGATED_TO_FARM)

# ── OS PADRÕES, EM ORDEM DE PRECEDÊNCIA ─────────────────────────────────────
# Precedência importa: «intervir em pré-colheita» é PREHARVEST, não FENOLOGIA
# genérica; e um trecho que cita determinação É administrativo mesmo que
# também nomeie uma fase.
# O verbo que manda AGIR e o substantivo que nomeia o ESTÁDIO DA PRAGA. A janela
# de fase de praga exige os dois na mesma oração — a ação amarrada ao estádio.
_ACAO = (r'\b(?:intervenire|intervir|intervenite|trattare|tratar|posizionare|'
         r'effettuare|applicare|aplicar|trattament\w+|tratament\w+|'
         r'intervenc\w+|intervent[oi]\b)')
_ESTAGIO = (r'\b(?:vol[oi]|voos?|generazion\w+|gerac\w+|ovideposi\w*|'
            r'sfarfallament\w*|stadi giovanili|neanid\w*|schiusur\w*|'
            r'nascita d\w+ \w+|formas juvenis)\b')

_P = [
 # Medido nos disciplinari de 2026: a Toscana não escreve «determinazione» na
 # linha do escafoide — escreve «nelle aree delimitate dal Servizio Fitosanitario
 # … eseguire gli interventi obbligatori». É ato administrativo com outro nome.
 (ADMINISTRATIVE_WINDOW, [
    r'\bdeterminazione\b', r'\bdetermina n', r'\bddr n', r'\bdecreto\b',
    r'\bderoga\b', r'\blotta obbligatoria\b', r'\bimpiego consentito\b',
    r'\bobrigatori\w+ por norma\b', r'\bconforme a determina\w*',
    r'\bluta obrigatoria\b', r'\bintervent[oi]s? obrigatori\w+\b',
    r'\bintervent[oi] obbligatori\b', r'\bmisure obbligatorie\b',
    r'\bmedidas obrigatorias\b', r'\bpiano di azione regionale\b',
    r'\bplano de acao regional\b',
    r'\bareas? delimitad\w+\b', r'\baree delimitate\b']),

 (PREHARVEST_WINDOW, [
    r'\bpre[- ]?colheita\b', r'\bpre[- ]?raccolta\b', r'\bpreraccolta\b',
    r'\bprossimita della raccolta\b', r'\bem prox\w+ (?:da|de) colheita\b',
    r'\bantes da colheita\b', r'\bpre[- ]?vindima\b',
    r'\bin prossimita della raccolta\b']),

 (THRESHOLD_WINDOW, [
    r'\bao ultrapassar\b', r'\bal superamento\b', r'\bsuperamento del\b',
    r'\bsoglia\b', r'\blimiar\b', r'\bacima d[eoa]\b.{0,30}\d',
    r'\bsuperiore[s]? a \d', r'\bsuperiores a \d', r'\b\d+\s?%\s*(?:de|di)\b']),

 # ⚠️ MESMA LEI DA FENOLOGIA, MEDIDA OUTRA VEZ NO RED TEAM SEMÂNTICO.
 # «terzo volo terminato, danni in aumento» NÃO diz quando tratar: relata o
 # inseto. Lido como janela, produzia `CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS`
 # sobre um boletim que tinha declarado a medição — uma frase falsa no cartão.
 #
 #     O VOO É O ESTADO DA PRAGA. A JANELA É O ESTADO AMARRADO A UMA AÇÃO.
 #
 # A fase declarada não se perde: vai para `PEST_STAGE_STATE`, com dono próprio.
 (PEST_STAGE_WINDOW, [
    _ACAO + r'[^.;]{0,70}' + _ESTAGIO,
    _ESTAGIO + r'[^.;]{0,70}' + _ACAO]),

 # ⚠️ Os quatro disciplinari lidos (FVG, Emilia-Romagna, Umbria, Toscana)
 # escrevem o mesmo gatilho com quatro redações. Nenhuma delas casava.
 #
 #     «intervenire preventivamente sulla base della previsione delle piogge»
 #     «in previsione del verificarsi … di condizioni favorevoli alla malattia»
 #
 # Um léxico que só conhece a redação de um boletim chama de «sem janela» o
 # disciplinare que declara a janela — e a lacuna é nossa, não da fonte.
 (WEATHER_TRIGGERED_WINDOW, [
    r'\bem caso de (?:chuva|temporal|granizo)\b',
    r'\bin caso di (?:pioggia|temporal|grandine)\b',
    r'\bjunto de chuva\b', r'\bdopo le piogge\b',
    r'\bmolhamento\b', r'\bbagnatura\b',
    r'\bcondicoes predisponentes\b', r'\bcondizioni predisponenti\b',
    r'\bcondicoes ideais para\b',
    r'\bprevisao d[ae]s? (?:chuvas|precipitacoes)\b',
    r'\bprevisione delle piogge\b',
    r'\bcondi[cz]\w+ favorav\w+ (?:ao|a|para) \w*\s?(?:desenvolvimento|doenca)\b',
    r'\bcondizioni favorevoli alla malattia\b',
    r'\bandamento climatico\b', r'\bandamento do clima\b']),

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
    r'\bao (?:atingir|chegar a)\b[^.;]{0,30}\bfase\b',
    # os disciplinari delimitam o período POR DUAS FASES — «da X até Y» — e é
    # essa moldura que diz quando agir. Medido em FVG, ER, Umbria e Toscana.
    r'\b(?:ate|fino) [aà]s? (?:pre[- ]?)?(?:fioritura|floracao|allegagione|'
    r'invaiatura|prefioritura)\b',
    r'\bd[oa] germogliamento (?:a|ate)\b', r'\bdal germogliamento all\b',
    r'\bd[ae] pre[- ]?(?:fioritura|floracao)\b',
    r'\bdalla pre fioritura\b', r'\bdall\W?allegagione\b',
    r'\b(?:imediatamente )?antes d[ae] (?:fioritura|floracao)\b',
    r'\bsubito prima della fioritura\b',
    r'\b(?:no |a )?fim d[ae] (?:fioritura|floracao)\b',
    r'\ba fine fioritura\b', r'\bem pre[- ]?(?:fioritura|floracao)\b',
    r'\bnas fases compreendidas entre\b']),

 (CALENDAR_WINDOW, [
    r'\b\d{1,2}/\d{1,2}/\d{4}\b', r'\b\d{4}-\d{2}-\d{2}\b',
    r'\ba partir de \d{1,2} de \w+', r'\bdal \d{1,2}\b', r'\bentro il \d{1,2}\b',
    r'\bfino al \d{1,2}\b', r'\bate o fim de \w+\b']),

 # o dono do padrão é `v21_necessidade.decisao_delegada`: um léxico só, lido
 # aqui e lá, para as duas leituras nunca discordarem.
 (RULE_DELEGATED_TO_FARM, [NE._DELEGADA.pattern]),
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

# ── O DOCUMENTO DE REGRA NÃO É O DOCUMENTO DE HOJE ──────────────────────────
#
# `aberta_agora` sempre teve o ramo `DOCUMENTO_NAO_CORRENTE` — e ele nunca era
# alcançado, porque `janelas_do_sinal` passava `corrente = True` a todos. No
# acervo de hoje isso não fez diferença nenhuma: as 16 candidatas saem todas de
# documentos com 22 dias ou menos. Mas a coleta de REGRA traz manuais — o
# «Manuale difesa integrata del melo» do Veneto é de março de 2020 — e um manual
# de 2020 diria «a condição está satisfeita agora» com a mesma cara de um
# boletim de ontem.
#
#     UM MANUAL DIZ QUAL É A REGRA. SÓ UM BOLETIM DIZ COMO ESTÁ O CAMPO HOJE.
#     A REGRA NÃO ENVELHECE; O ESTADO ENVELHECE EM DIAS.
#
# `WINDOW_DEFINED` continua YES para o manual — a regra é a regra. O que a data
# governa é só a segunda pergunta.
#
# São os mesmos 30 dias de `SINAL_CORRENTE_DIAS`, e `T54` quebra se as duas
# constantes se separarem sem que alguém decida separá-las.
DIAS_PARA_DOCUMENTO_CORRENTE = 30


def documento_corrente(sinal, hoje=None):
    """→ o documento é recente o bastante para falar do AGORA?

    Sem data declarada a resposta é NÃO: um documento que não diz quando foi
    escrito não pode dizer que a condição está satisfeita agora.
    """
    bruto = str(sinal.get('REFERENCE_DATE') or '')[:10]
    try:
        ano, mes, dia = (int(x) for x in bruto.split('-'))
        quando = date(ano, mes, dia)
    except (ValueError, TypeError):
        return False
    return 0 <= ((hoje or date.today()) - quando).days <= DIAS_PARA_DOCUMENTO_CORRENTE

# A fonte declarando, no presente, que a condição está satisfeita. NUNCA um
# tempo verbal qualquer: só as formas em que o serviço afirma o momento.
_PRESENTE = re.compile(
    r'\bsiamo (?:nella|in) fase\b|\bse esta na fase\b|\bestamos na fase\b|'
    r'\bci troviamo (?:nella|in) fase\b|\bsiamo nel periodo\b|'
    r'\be o momento (?:de|da|do)\b|\be il momento (?:di|della|del)\b')


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


# Palavras que declaram uma fase COMO ENCERRADA. Se a fonte diz «siamo nella
# fase conclusiva», ela está a declarar o presente — e o presente que ela
# declara é o fim. Sem esta guarda, `_PRESENTE` abria a janela numa frase que a
# fechava.
_ENCERRADA = re.compile(
    r'\bconclus\w*\b|\bconclu[ií]d\w*\b|\btermina\w*\b|\bfinal\w*\b|'
    r'\bcalant\w*\b|\bin esaurimento\b|\bultim\w*\b|\bencerrad\w*\b')

# Os tipos cuja condição é QUANTITATIVA ou EVENTUAL: só uma medição, uma
# contagem ou um evento datado a satisfazem. Prosa qualitativa não os responde.
CONDICAO_MEDIDA = (THRESHOLD_WINDOW, WEATHER_TRIGGERED_WINDOW, PEST_STAGE_WINDOW)


def aberta_agora(tipo, oracao, estagio, corrente):
    """→ ('YES'|'UNKNOWN'|'NO', método). A segunda pergunta, nunca a primeira.

    O MÉTODO É UMA AFIRMAÇÃO SOBRE A FONTE, E TEM DE SER VERDADEIRO
    ---------------------------------------------------------------
    O red team pegou o motor a dizer `CONDICAO_EXIGE_MEDICAO_QUE_NAO_TEMOS`
    sobre o boletim frutticolo do Veneto de 03/09/2026 — que declarava a
    medição em letras: «terzo volo terminato». A resposta `UNKNOWN` estava
    certa; a razão estava errada, e uma razão errada no cartão é uma mentira
    pequena que ninguém audita.

        «NÃO TEMOS A MEDIÇÃO» E «A MEDIÇÃO NÃO RESPONDE À PERGUNTA» SÃO COISAS
        DIFERENTES. O CARTÃO TEM DE DIZER QUAL DAS DUAS É.

    Por isso o método distingue agora quatro silêncios diferentes: a fonte não
    mediu; a fonte descreveu em prosa qualitativa; a fonte declarou a fase e ela
    não é a da condição; e a fonte declarou a fase como encerrada.
    """
    # ⚠️ ESTES DOIS NÃO DEPENDEM DA IDADE DO DOCUMENTO. Um ato administrativo é
    # prazo de norma num manual de 2020 e num boletim de ontem; e uma regra que
    # manda medir no pomar manda medir no pomar em qualquer ano. Responder
    # `DOCUMENTO_NAO_CORRENTE` a eles seria dar a razão errada de novo.
    if tipo == ADMINISTRATIVE_WINDOW:
        return 'NO', 'ATO_ADMINISTRATIVO_NAO_E_JANELA_AGRONOMICA'
    if tipo == RULE_DELEGATED_TO_FARM:
        # a regra é conhecida — «medir no pomar» — e a medição não é regional.
        # Nenhuma coleta de fonte oficial muda esta resposta: ela já foi dada.
        return 'UNKNOWN', 'REGRA_EXIGE_MEDICAO_DO_POMAR_QUE_NENHUMA_FONTE_REGIONAL_TEM'
    if not corrente:
        return 'UNKNOWN', 'DOCUMENTO_NAO_CORRENTE'
    t = N._n(oracao)
    if tipo in CONDICAO_MEDIDA:
        # ⚠️ TESTEMUNHA NEGATIVA. «il quadro rimane tendenzialmente buono» não
        # diz que 5% de cachos infestados não foi ultrapassado: diz que quem
        # escreveu achou o quadro bom. Entre as duas coisas há uma medição que
        # ninguém fez, e transformá-la em resposta seria inventar o número.
        #
        #     FRASE QUALITATIVA SÓ RESPONDE A UMA CONDIÇÃO QUANTITATIVA QUANDO
        #     A PRÓPRIA FONTE DECLARA A EQUIVALÊNCIA. NUNCA POR LEITURA NOSSA.
        if NE.qualitativo(oracao):
            return 'UNKNOWN', 'FRASE_QUALITATIVA_NAO_RESPONDE_CONDICAO_QUANTITATIVA'
        if tipo == PEST_STAGE_WINDOW:
            # aqui a AÇÃO está amarrada ao ESTÁDIO — é a própria oração que
            # prescreve. Então a fase que ela declara responde por ela mesma.
            fase, _p = NE.fase_da_praga(oracao)
            if fase in (NE.STAGE_STARTED, NE.STAGE_PEAK):
                return 'YES', 'FONTE_DECLARA_A_FASE_DA_PRAGA_COMO_PRESENTE'
            if fase == NE.STAGE_ENDED:
                return 'NO', 'FONTE_DECLARA_A_FASE_DA_PRAGA_COMO_ENCERRADA'
            return 'UNKNOWN', 'FONTE_NAO_DECLARA_A_FASE_QUE_A_CONDICAO_EXIGE'
        return 'UNKNOWN', 'FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE'
    # ⚠️ A FONTE PODE DIZER «AGORA» ELA MESMA, e aí não há o que deduzir.
    # Medido no Bollettino Vite Integrato de Siena de 03/09/2026:
    # «Siamo nella fase di maggior suscettibilità a questa malattia.» A condição
    # é «fase de maior suscetibilidade» e quem declara que ela está satisfeita é
    # o serviço fitossanitário, no presente, no mesmo documento.
    #
    #     QUANDO A FONTE ESCREVE «ESTAMOS NA FASE», NÃO É INFERÊNCIA LER ISSO.
    #     É LEITURA. INFERÊNCIA SERIA CONCLUIR SEM ELA TER ESCRITO.
    if _PRESENTE.search(t):
        # ...mas a fase que ela declara pode ser a fase FINAL. «Siamo nella fase
        # conclusiva» é presente e é fim: ler só o presente abriria a janela
        # exatamente na frase que a fecha.
        if _ENCERRADA.search(t):
            return 'NO', 'FONTE_DECLARA_A_FASE_COMO_ENCERRADA'
        return 'YES', 'FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE'
    if not estagio:
        return 'UNKNOWN', 'DOCUMENTO_NAO_DECLARA_ESTADIO_DA_CULTURA'
    e = N._n(estagio)
    if tipo == PREHARVEST_WINDOW:
        if any(v in e for v in FENOLOGIA_QUE_SATISFAZ[PREHARVEST_WINDOW]):
            return 'YES', 'ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO'
        return 'NO', 'ESTADIO_DECLARADO_NAO_SATISFAZ_A_CONDICAO'
    if tipo == PHENOLOGY_WINDOW:
        # a condição nomeia o próprio estádio: basta a fonte declarar o mesmo
        for termo in ('invaiatura', 'maturazione', 'maturacao', 'fioritura',
                      'floracao', 'accrescimento', 'ingrossamento', 'raccolta',
                      'colheita', 'sfioritura', 'allegagione'):
            if termo in t and termo in e:
                return 'YES', 'ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO'
        return 'UNKNOWN', 'ESTADIO_DECLARADO_NAO_NOMEIA_A_CONDICAO'
    return 'UNKNOWN', 'TIPO_SEM_REGRA_DE_ABERTURA'


def janelas_do_sinal(sinal):
    """→ candidatas de janela deste registro, por par cultura × alvo."""
    corrente = documento_corrente(sinal)
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
