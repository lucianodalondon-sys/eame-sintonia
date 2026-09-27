#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CAP-WIN — A JANELA DE CULTURA, a capacidade minima, e so ela.

    MISSAO   CAP-WIN (D100 · D100-b/L6: a CAP-WIN vem primeiro na espinha G0-G6)
    DESENHO  docs/intelligence/CAP-WIN-DESENHO-R5.md (W0-W8)
    LEIS     Biblia CAP-WIN · INT-LAW-030/091/100/104 · INT-LAW-070..077 (via grafo)
    ESTADO   EXPERIMENTAL / NAO_PARA_CLIENTE

    python3 motor/cap_win.py <itens.json> --hoje AAAA-MM-DD
    python3 -m unittest tests.test_cap_win -v

A PERGUNTA QUE ESTE FICHEIRO RESPONDE, E MAIS NENHUMA
-----------------------------------------------------
    NESTA CULTURA, PARA ESTE PROBLEMA, NESTA REGIAO, QUAL E A JANELA EM QUE
    AGIR FAZ DIFERENCA — E HA PROVA DE QUE ELA ESTA ABERTA AGORA?

    CULTURA x FASE/BBCH x REGIAO x PERIODO x PROBLEMA

Duas perguntas, que nunca sao a mesma (regra do V21, portada):

    WINDOW_DEFINED   sabemos QUAL condicao define o momento certo?
    WINDOW_OPEN_NOW  ha evidencia de que a condicao esta satisfeita AGORA?

    DEFINIDA NAO E ABERTA. SABER O GATILHO NAO E SABER QUE ELE DISPAROU.

A ENTRADA E O LIVRO DA CORRIDA G0/v4, E NAO O TEXTO SOLTO
--------------------------------------------------------
Todo READY atravessou o intake (a5db06c4) e esta no livro com o seu ESTADO
TEMPORAL. Esta capacidade le o livro e respeita o que ele diz:

  - a REGRA (WINDOW_DEFINED) e leitura atemporal: entra pelo uso
    `LEITURA_ATEMPORAL_DE_CAPACIDADE`, disponivel mesmo com FACT_TIME = NAO SEI;
  - a OBSERVACAO (WINDOW_OPEN_NOW) exige tempo: entra pelo uso `CAP-WIN`, que a
    corrida bloqueia quando o tempo do facto nao ancorou. O que a fonte DISSE
    continua visivel (`DECLARADO_PELA_FONTE`); so nao responde «agora».

    O TEMPO SO BLOQUEIA OS USOS QUE EXIGEM TEMPO.

O QUE ELE NUNCA FAZ
-------------------
    NAO tira CROP_ID / ISSUE_ID / REGION_ID do texto (INT-LAW-084). Sem par em
        campo: NOT_POSSIBLE (INT-LAW-091) + o requisito que o desbloqueia. O texto
        so serve de SONDA do requisito (prova de que o valor esta no bruto).
    NAO usa PUBLICATION_TIME como tempo do facto (INT-LAW-100).
    NAO trata data de calendario como janela agronomica; ADMINISTRATIVE nunca e
        janela agronomica. NAO trata janela de outro ano como deste (STALE).
    NAO responde a condicao quantitativa com frase qualitativa.
    NAO produz OPPORTUNITY. `NO_DEFENSIBLE_ACTION_YET` e resultado de primeira
        classe (INT-LAW-012), e e o esperado no corte ARIF x APOL.

PORTAR A REGRA, NAO O FICHEIRO
------------------------------
`scripts/v21_janelas.py` @ 85df96f7 (legado V21) le `DESIGN-INGEST`, nao a Sala,
e atribui par por texto. Daqui veio a REGRA: os 8 tipos, os padroes, a
precedencia e os silencios de `aberta_agora`. Nao veio: `v21_normalizar`,
`v21_necessidade.atribuicoes`, nem o leitor do acervo. Os lexicos que a regra
usa (qualitativo, fase da praga, delegada, restritivos) vieram copiados com
ela, porque importa-los arrastava o motor V21 para dentro da janela.

Um acrescimo, e so um, declarado (desenho §3): a APOL escreve a medicao por
extenso — «non si sono rilevate raggiungimenti o superamenti della soglia» — e
o V21 respondia `FONTE_NAO_DECLARA_A_MEDICAO...`. A resposta UNKNOWN ficava
certa e a RAZAO errada. Aqui: `WINDOW_OPEN_NOW = NO`, metodo
`FONTE_DECLARA_SOGLIA_NAO_ATINGIDA`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ / "motor") not in sys.path:
    sys.path.insert(0, str(RAIZ / "motor"))

import corrida_da_inteligencia as CI            # noqa: E402
import grafo_de_dependencia as GD               # noqa: E402
# PORTA-UNICA-REFERENCIA (D116): «que produto ADAMA a bula autoriza para esta
# cultura x problema?» e perguntado a porta, na MESMA edicao das outras capacidades.
import porta_da_referencia as PORTA             # noqa: E402

# ⚠️ O vocabulario vem da CORRIDA, que ja o le da espinha. Importar a espinha
# daqui era runtime a importar `provas/` por nome nu — e
# `test_a_porta_cli_liga_o_banco.test_1` reprova isso (apanhou-me na bateria).
NAO_SEI = CI.NAO_SEI
PALAVRAS_QUE_O_REQUISITO_RECUSA = CI.PALAVRAS_QUE_O_REQUISITO_RECUSA

VERSAO = "CAP-WIN/v1"
CAPACIDADE = "CAP-WIN"
REGRA_PORTADA_DE = "scripts/v21_janelas.py @ 85df96f7c83083aabbc7bdf84ab6f575503f7134"

#: ⚠️ W4 · o limiar de CURRENT, fixado ANTES de olhar para os dados. E o mesmo
#: numero do V21 (`DIAS_PARA_DOCUMENTO_CORRENTE = 30`), portado com a regra.
#: O desenho (§7) diz que o N e decisao de regra do dono: fica declarado aqui
#: como HERDADO, e muda-se num sitio so.
N_DIAS_CURRENT = 30
N_DIAS_CURRENT_ESTADO = "HERDADO_DO_V21 — decisao do dono pendente (desenho §7)"


def _n(t) -> str:
    """Sem acento, minusculo, so letras e numeros — o achatamento do V21."""
    t = "".join(c for c in unicodedata.normalize("NFD", str(t or ""))
                if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


# ══════════════════════════════════════════════════════════════════════════
# W2 · OS OITO TIPOS DE JANELA (regra do V21, portada sem mudar um padrao)
# ══════════════════════════════════════════════════════════════════════════
CALENDAR_WINDOW = "CALENDAR_WINDOW"
PHENOLOGY_WINDOW = "PHENOLOGY_WINDOW"
PREHARVEST_WINDOW = "PREHARVEST_WINDOW"
THRESHOLD_WINDOW = "THRESHOLD_WINDOW"
WEATHER_TRIGGERED_WINDOW = "WEATHER_TRIGGERED_WINDOW"
PEST_STAGE_WINDOW = "PEST_STAGE_WINDOW"
ADMINISTRATIVE_WINDOW = "ADMINISTRATIVE_WINDOW"
RULE_DELEGATED_TO_FARM = "RULE_DELEGATED_TO_FARM"

TIPOS = (CALENDAR_WINDOW, PREHARVEST_WINDOW, PHENOLOGY_WINDOW, THRESHOLD_WINDOW,
         PEST_STAGE_WINDOW, WEATHER_TRIGGERED_WINDOW, ADMINISTRATIVE_WINDOW,
         RULE_DELEGATED_TO_FARM)
#: ADMINISTRATIVE fica FORA: prazo de norma nao e janela agronomica.
AGRONOMICOS = (CALENDAR_WINDOW, PREHARVEST_WINDOW, PHENOLOGY_WINDOW,
               THRESHOLD_WINDOW, PEST_STAGE_WINDOW, WEATHER_TRIGGERED_WINDOW,
               RULE_DELEGATED_TO_FARM)

_ACAO = (r"\b(?:intervenire|intervir|intervenite|trattare|tratar|posizionare|"
         r"effettuare|applicare|aplicar|trattament\w+|tratament\w+|"
         r"intervenc\w+|intervent[oi]\b)")
_ESTAGIO = (r"\b(?:vol[oi]|voos?|generazion\w+|gerac\w+|ovideposi\w*|"
            r"sfarfallament\w*|stadi giovanili|neanid\w*|schiusur\w*|"
            r"nascita d\w+ \w+|formas juvenis)\b")

# lexico da regra delegada (dono no V21: `v21_necessidade._DELEGADA`)
_DELEGADA = re.compile(
    r"\b(?:decisoes|decisao|decisioni|decisione)\b[^.;]{0,80}"
    r"\b(?:observacoes|observacao|osservazion\w+|situacao|situazione)\b"
    r"[^.;]{0,40}\b(?:empresa|aziendal\w+|azienda|pomar|frutteto)\b|"
    r"\bosservazioni aziendali\b|\bobservacoes da propria empresa\b|"
    r"\bvalutazione aziendale\b|\bin base alla situazione aziendale\b")

_P = [
 (ADMINISTRATIVE_WINDOW, [
    r"\bdeterminazione\b", r"\bdetermina n", r"\bddr n", r"\bdecreto\b",
    r"\bderoga\b", r"\blotta obbligatoria\b", r"\bimpiego consentito\b",
    r"\bobrigatori\w+ por norma\b", r"\bconforme a determina\w*",
    r"\bluta obrigatoria\b", r"\bintervent[oi]s? obrigatori\w+\b",
    r"\bintervent[oi] obbligatori\b", r"\bmisure obbligatorie\b",
    r"\bmedidas obrigatorias\b", r"\bpiano di azione regionale\b",
    r"\bplano de acao regional\b",
    r"\bareas? delimitad\w+\b", r"\baree delimitate\b"]),
 (PREHARVEST_WINDOW, [
    r"\bpre[- ]?colheita\b", r"\bpre[- ]?raccolta\b", r"\bpreraccolta\b",
    r"\bprossimita della raccolta\b", r"\bem prox\w+ (?:da|de) colheita\b",
    r"\bantes da colheita\b", r"\bpre[- ]?vindima\b",
    r"\bin prossimita della raccolta\b"]),
 (THRESHOLD_WINDOW, [
    r"\bao ultrapassar\b", r"\bal superamento\b", r"\bsuperamento del\b",
    # ⚠️ ACRESCIMO DECLARADO (CAP-WIN): o V21 so conhecia «soglia». O ARIF
    # escreve «al disotto delle SOGLIE di intervento» (desenho §3), e o plural
    # ficava sem janela nenhuma — a lacuna era nossa, nao da fonte.
    r"\bsogli[ae]\b", r"\blimiar\b", r"\bacima d[eoa]\b.{0,30}\d",
    r"\bsuperiore[s]? a \d", r"\bsuperiores a \d", r"\b\d+\s?%\s*(?:de|di)\b"]),
 (PEST_STAGE_WINDOW, [
    _ACAO + r"[^.;]{0,70}" + _ESTAGIO,
    _ESTAGIO + r"[^.;]{0,70}" + _ACAO]),
 (WEATHER_TRIGGERED_WINDOW, [
    r"\bem caso de (?:chuva|temporal|granizo)\b",
    r"\bin caso di (?:pioggia|temporal|grandine)\b",
    r"\bjunto de chuva\b", r"\bdopo le piogge\b",
    r"\bmolhamento\b", r"\bbagnatura\b",
    r"\bcondicoes predisponentes\b", r"\bcondizioni predisponenti\b",
    r"\bcondicoes ideais para\b",
    r"\bprevisao d[ae]s? (?:chuvas|precipitacoes)\b",
    r"\bprevisione delle piogge\b",
    r"\bcondi[cz]\w+ favorav\w+ (?:ao|a|para) \w*\s?(?:desenvolvimento|doenca)\b",
    r"\bcondizioni favorevoli alla malattia\b",
    r"\bandamento climatico\b", r"\bandamento do clima\b"]),
 (PHENOLOGY_WINDOW, [
    r"\ba partir d[ao]\b[^.;]{0,40}\b(?:invaiatura|maturac\w+|maturaz\w+|"
    r"fioritura|floracao|sfioritura|allegagione|accrescimento|raccolta|colheita)\b",
    r"\b(?:dalla|nella|alla|dopo la|prima della) fase\b",
    r"\bna fase de\b", r"\bem fase de\b", r"\bin fase di\b",
    r"\bbbch \d", r"\ba partir da viragem de cor\b",
    r"\bao (?:atingir|chegar a)\b[^.;]{0,30}\bfase\b",
    r"\b(?:ate|fino) [aà]s? (?:pre[- ]?)?(?:fioritura|floracao|allegagione|"
    r"invaiatura|prefioritura)\b",
    r"\bd[oa] germogliamento (?:a|ate)\b", r"\bdal germogliamento all\b",
    r"\bd[ae] pre[- ]?(?:fioritura|floracao)\b",
    r"\bdalla pre fioritura\b", r"\bdall\W?allegagione\b",
    r"\b(?:imediatamente )?antes d[ae] (?:fioritura|floracao)\b",
    r"\bsubito prima della fioritura\b",
    r"\b(?:no |a )?fim d[ae] (?:fioritura|floracao)\b",
    r"\ba fine fioritura\b", r"\bem pre[- ]?(?:fioritura|floracao)\b",
    r"\bnas fases compreendidas entre\b"]),
 (CALENDAR_WINDOW, [
    r"\b\d{1,2}/\d{1,2}/\d{4}\b", r"\b\d{4}-\d{2}-\d{2}\b",
    r"\ba partir de \d{1,2} de \w+", r"\bdal \d{1,2}\b", r"\bentro il \d{1,2}\b",
    r"\bfino al \d{1,2}\b", r"\bate o fim de \w+\b"]),
 (RULE_DELEGATED_TO_FARM, [_DELEGADA.pattern]),
]


def tipos_da_oracao(oracao) -> list:
    """-> [(TIPO, padrao que casou)], em ordem de precedencia. Pode ser vazio."""
    t = _n(oracao)
    fora = []
    for tipo, padroes in _P:
        for p in padroes:
            if re.search(p, t):
                fora.append((tipo, p))
                break
    return fora


def oracoes(texto) -> list:
    """Parte o texto em oracoes sem quebrar dentro de «citacao» (V21)."""
    t = str(texto or "")
    if not t.strip():
        return []
    guardas = {}

    def _guardar(m):
        k = "\x00%d\x00" % len(guardas)
        guardas[k] = m.group(0)
        return k
    t = re.sub(r"«[^»]*»", _guardar, t)
    t = re.sub(r"(\x00\d+\x00)\s+(?=[A-ZÀ-Ý])", r"\1\n", t)
    saida = []
    for p in re.split(r"(?<=[.;])\s+|\s+\|\s+|\n", t):
        for k, v in guardas.items():
            p = p.replace(k, v)
        p = p.strip()
        if p:
            saida.append(p)
    return saida


# ══════════════════════════════════════════════════════════════════════════
# W3 · «A CONDICAO ESTA SATISFEITA?» — os silencios do V21 + SOGLIA_NAO_ATINGIDA
# ══════════════════════════════════════════════════════════════════════════
YES, NO, UNKNOWN = "YES", "NO", "UNKNOWN"

FENOLOGIA_QUE_SATISFAZ_PREHARVEST = ("maturazione", "maturacao", "invaiatura",
                                     "raccolta", "colheita", "vindima", "bbch 8",
                                     "addolcimento")
CONDICAO_MEDIDA = (THRESHOLD_WINDOW, WEATHER_TRIGGERED_WINDOW, PEST_STAGE_WINDOW)

_PRESENTE = re.compile(
    r"\bsiamo (?:nella|in) fase\b|\bse esta na fase\b|\bestamos na fase\b|"
    r"\bci troviamo (?:nella|in) fase\b|\bsiamo nel periodo\b|"
    r"\be o momento (?:de|da|do)\b|\be il momento (?:di|della|del)\b")
_ENCERRADA = re.compile(
    r"\bconclus\w*\b|\bconclu[ií]d\w*\b|\btermina\w*\b|\bfinal\w*\b|"
    r"\bcalant\w*\b|\bin esaurimento\b|\bultim\w*\b|\bencerrad\w*\b")
_QUALITATIVO = re.compile(
    r"\bsituazione buona\b|\bsituacao boa\b|"
    r"\bquadro\b[^.;]{0,30}\bbuono\b|\bquadro\b[^.;]{0,30}\bbom\b|"
    r"\btendenzialmente buono\b|\btendencialmente bom\b|"
    r"\bpressione contenuta\b|\bpressao contida\b|"
    r"\binfestazioni contenute\b|\binfestacoes contidas\b|"
    r"\bsotto controllo\b|\bsob controlo\b|\bsob controle\b|"
    r"\bfase conclusa\b|\bfase concluida\b|"
    r"\bdanni presenti\b|\bdanos presentes\b|\bpresenza di danni\b|"
    r"\bsituazione sotto\b|\bnella norma\b|\bnormal para a epoca\b")

# fase da praga (dono no V21: `v21_necessidade.fase_da_praga`)
_ESTADIO_DA_PRAGA = re.compile(
    r"\bvol[oi]\b|\bvoos?\b|\bgenerazion\w+\b|\bgerac\w+\b|"
    r"\bovideposi\w*|\bsfarfallament\w*|\bneanid\w*|\bpostura\w*|"
    r"\bformas juvenis\b|\bstadi giovanili\b|\bnascita d\w+ \w+\b")
_FASE_ENCERRADA = re.compile(r"\btermina\w*\b|\bconclus\w*\b|\bconclu[ií]d\w*\b|"
                             r"\bencerrad\w*\b|\bfinit\w*\b|\bterminou\b")
_FASE_DECLINIO = re.compile(r"\bcalant\w*\b|\bin esaurimento\b|\bem declinio\b|"
                            r"\bdecrescent\w*\b|\bem esgotamento\b")
_FASE_PRESENTE = re.compile(r"\bpicco\b|\bpico\b|\bmassimo\b|\bauge\b|"
                            r"\biniziat\w*\b|\binizio\b|\bcomecou\b|\bcomecad\w*\b|"
                            r"\bin corso\b|\bem curso\b|\bavviat\w*\b")

# ⚠️ O ACRESCIMO DA CAP-WIN (desenho §3). A fonte declarando, POR EXTENSO, que a
# soglia NAO foi atingida. Exige a negacao amarrada a soglia, ou «sotto soglia».
# «poche catture» sozinho NAO casa: numero baixo nao e soglia nao atingida.
_SOGLIA_NAO_ATINGIDA = re.compile(
    r"\bnon\b[^.;]{0,60}\b(?:raggiungiment\w*|superament\w*|superat\w*|"
    r"raggiunt\w*)\b[^.;]{0,40}\bsogli\w*|"
    r"\bsogli\w*\b[^.;]{0,30}\bnon\b[^.;]{0,20}\b(?:raggiunt\w*|superat\w*)\b|"
    r"\b(?:al ?di ?sotto|sotto) (?:della |delle |alla |alle |la |le )?sogli\w*|"
    r"\babaixo d[oa]s? limia\w*|"
    r"\bnao\b[^.;]{0,40}\b(?:atingid\w*|ultrapassad\w*)\b[^.;]{0,30}\blimia\w*|"
    r"\blimiar\w*\b[^.;]{0,20}\bnao\b[^.;]{0,20}\b(?:atingid\w*|ultrapassad\w*)\b")
# A fonte declarando que a soglia FOI atingida — sem negacao.
_SOGLIA_ATINGIDA = re.compile(
    r"\b(?:superat\w*|raggiunt\w*) (?:la |le )?sogli\w*|"
    r"\bsogli\w* (?:di intervento )?(?:e |sono )?(?:stat\w )?(?:superat\w*|raggiunt\w*)|"
    r"\bsopra (?:la )?sogli\w*|\blimiar\w* (?:foi )?(?:atingid\w*|ultrapassad\w*)|"
    r"\bacima d[oa] limiar\b")
_NEGACAO_ANTES = re.compile(r"\bnon\b|\bnao\b|\bnessun\w*\b|\bnenhum\w*\b")
# «pochissime aree sopra soglia» diz as duas coisas: parte da area SIM, o resto NAO.
_SO_EM_PARTE = re.compile(r"\b(?:poch\w*|alcun\w*|singol\w*|isolat\w*|algum\w*|"
                          r"poucas?|pouco)\b[^.;]{0,30}\b(?:aree|area|zone|areas|zonas)\b")

# restritivos (dono no V21: `v21_necessidade._P`, estados que FECHAM a porta) +
# a redacao da APOL medida no desenho: «non si ritiene giustificata ... trattamento».
_RESTRITIVO = re.compile(
    r"\bvigora a proibicao\b|\bproibicao de intervencao\b|\be proibido\b|"
    r"\bvietat[oa]\b|\bdivieto\b|"
    r"\bpode(?:m)? ser suspens[oa]s?\b|\bsospend\w*\b|\bsospes[oai]\w*\b|"
    r"\b(?:defesa|difesa|tratamentos?|trattament\w+)[^.;]{0,60}"
    r"(?:conclu[ií]d[oa]|conclus[oa]|encerrad[oa]|terminad[oa])\b|"
    r"\bnao (?:sao|e|ha) necessari\w*\b|\bnon (?:sono )?necessari\w*\b|"
    r"\bnon si prevedono\b|\bnao (?:se )?preve\w* tratament\w*\b|"
    r"\bnon si ritiene giustificat\w*\b|\bnon (?:e|sono) giustificat\w*\b|"
    r"\bnao (?:se )?justifica\w*\b[^.;]{0,40}\btratament\w*")


def restritiva(oracao) -> str | None:
    """-> o padrao que manda NAO tratar, ou None. Quem manda parar manda parar."""
    m = _RESTRITIVO.search(_n(oracao))
    return m.group(0) if m else None


def aberta_agora(tipo, oracao, estagio) -> tuple:
    """-> (YES|NO|UNKNOWN, metodo): o que A FONTE declara sobre a condicao.

    A regra do V21 sem o ramo `DOCUMENTO_NAO_CORRENTE`: aqui o tempo e do FACTO
    e quem o decide e `julgar()` (W4), que sabe o estado temporal do item. Esta
    funcao responde so «o que o documento diz», e o metodo tem de ser verdadeiro.
    """
    if tipo == ADMINISTRATIVE_WINDOW:
        return NO, "ATO_ADMINISTRATIVO_NAO_E_JANELA_AGRONOMICA"
    if tipo == RULE_DELEGATED_TO_FARM:
        return UNKNOWN, "REGRA_EXIGE_MEDICAO_DO_POMAR_QUE_NENHUMA_FONTE_REGIONAL_TEM"
    t = _n(oracao)
    if tipo in CONDICAO_MEDIDA:
        if tipo == THRESHOLD_WINDOW:
            neg = _SOGLIA_NAO_ATINGIDA.search(t)
            # «non e stata superata la soglia»: a negacao desarma o positivo
            pos = next((m for m in _SOGLIA_ATINGIDA.finditer(t)
                        if not _NEGACAO_ANTES.search(t[max(0, m.start() - 25):m.start()])),
                       None)
            if pos and (neg or _SO_EM_PARTE.search(t)):
                return UNKNOWN, "FONTE_DECLARA_SOGLIA_ATINGIDA_SO_EM_PARTE_DA_AREA"
            if neg:
                return NO, "FONTE_DECLARA_SOGLIA_NAO_ATINGIDA"
            if pos:
                return YES, "FONTE_DECLARA_SOGLIA_ATINGIDA"
        if _QUALITATIVO.search(t):
            return UNKNOWN, "FRASE_QUALITATIVA_NAO_RESPONDE_CONDICAO_QUANTITATIVA"
        if tipo == PEST_STAGE_WINDOW:
            if _ESTADIO_DA_PRAGA.search(t):
                if _FASE_ENCERRADA.search(t):
                    return NO, "FONTE_DECLARA_A_FASE_DA_PRAGA_COMO_ENCERRADA"
                if not _FASE_DECLINIO.search(t) and _FASE_PRESENTE.search(t):
                    return YES, "FONTE_DECLARA_A_FASE_DA_PRAGA_COMO_PRESENTE"
            return UNKNOWN, "FONTE_NAO_DECLARA_A_FASE_QUE_A_CONDICAO_EXIGE"
        return UNKNOWN, "FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE"
    if _PRESENTE.search(t):
        if _ENCERRADA.search(t):
            return NO, "FONTE_DECLARA_A_FASE_COMO_ENCERRADA"
        return YES, "FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE"
    if not estagio:
        return UNKNOWN, "DOCUMENTO_NAO_DECLARA_ESTADIO_DA_CULTURA"
    e = _n(estagio)
    if tipo == PREHARVEST_WINDOW:
        if any(v in e for v in FENOLOGIA_QUE_SATISFAZ_PREHARVEST):
            return YES, "ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO"
        return NO, "ESTADIO_DECLARADO_NAO_SATISFAZ_A_CONDICAO"
    if tipo == PHENOLOGY_WINDOW:
        for termo in ("invaiatura", "maturazione", "maturacao", "fioritura",
                      "floracao", "accrescimento", "ingrossamento", "raccolta",
                      "colheita", "sfioritura", "allegagione"):
            if termo in t and termo in e:
                return YES, "ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO"
        return UNKNOWN, "ESTADIO_DECLARADO_NAO_NOMEIA_A_CONDICAO"
    return UNKNOWN, "TIPO_SEM_REGRA_DE_ABERTURA"


# ══════════════════════════════════════════════════════════════════════════
# W0 · O PAR EM CAMPO — nunca do texto
# ══════════════════════════════════════════════════════════════════════════
#: As chaves vem de `JANELA_DECLARADA` (migration 033: CULTURA, REGIAO_DO_FATO,
#: FASE, JANELA — cada uma com VALOR, VEIO_DE e BASE).
#: ⚠️ `PROBLEMA` NAO EXISTE no contrato 033. E o requisito `CROP_ISSUE_EM_CAMPO`
#: do desenho (R5): o nome esta aqui PROPOSTO, e ate a Collection o declarar
#: todo item real sai NOT_POSSIBLE — que e a verdade de hoje.
CHAVES_DO_PAR = {"CROP_ID": "CULTURA", "ISSUE_ID": "PROBLEMA",
                 "REGION_ID": "REGIAO_DO_FATO"}
CHAVE_DA_FASE = "FASE"
CHAVE_DA_SUBAREA = "SUBAREA"                     # opcional: subarea DENTRO da regiao
CHAVE_DA_REDE = "REDE_DE_MONITORIZACAO"          # opcional: quem observou
CHAVE_DA_ORIGEM_DA_REGRA = "ORIGEM_DA_REGRA"     # opcional: de onde vem a regra
REQUISITO_DO_PAR = "CROP_ISSUE_EM_CAMPO"
REQUISITO_DA_REGIAO = "REGION_EM_CAMPO"


def _declarado(jd: dict, chave: str):
    """-> (valor, base) se a Collection declarou COM base; senao (None, porque)."""
    bloco = jd.get(chave) if isinstance(jd, dict) else None
    if not isinstance(bloco, dict):
        return None, "campo ausente"
    v, base = bloco.get("VALOR"), bloco.get("BASE")
    if isinstance(v, (list, tuple)):
        v = ",".join(str(x) for x in v if not CI.e_ignorancia(x)) or None
    if CI.e_ignorancia(v):
        return None, "VALOR = NAO SEI"
    if CI.base_ignorante(base):
        return None, "VALOR sem BASE"
    return str(v).strip(), base


def par_em_campo(item: dict) -> tuple:
    """-> (par, falta). `par` = {CROP_ID, ISSUE_ID, REGION_ID, ...} ou None."""
    jd = item.get("JANELA_DECLARADA") or {}
    par, falta = {}, []
    for chave, campo in CHAVES_DO_PAR.items():
        v, base = _declarado(jd, campo)
        if v is None:
            falta.append(f"JANELA_DECLARADA.{campo}: {base}")
        else:
            par[chave] = v
    fase, _b = _declarado(jd, CHAVE_DA_FASE)
    par["PHENOLOGY_STAGE"] = fase or NAO_SEI
    sub, _b = _declarado(jd, CHAVE_DA_SUBAREA)
    par["SUBAREA"] = sub or NAO_SEI
    rede, _b = _declarado(jd, CHAVE_DA_REDE)
    par["REDE"] = rede
    origem, _b = _declarado(jd, CHAVE_DA_ORIGEM_DA_REGRA)
    par["ORIGEM_DA_REGRA"] = origem
    return (None if falta else par), falta


# ══════════════════════════════════════════════════════════════════════════
# W4 · O ESTADO TEMPORAL DA OBSERVACAO
# ══════════════════════════════════════════════════════════════════════════
CURRENT, STALE = "CURRENT", "STALE"


def estado_temporal(linha: dict, hoje: date, n_dias: int = N_DIAS_CURRENT) -> tuple:
    """-> (CURRENT|STALE|UNKNOWN, intervalo, porque). Le o LIVRO, nao o item.

    O tempo vem de FACT_TIME, e so quando a corrida o ancorou. PUBLICATION_TIME
    nunca entra aqui (INT-LAW-100).
    """
    if linha.get("TEMPORAL_STATE") != "ANCORADO":
        return UNKNOWN, None, "FACT_TIME:" + str(linha.get("TEMPORAL_STATE"))
    tempo = CI.intervalo_do_tempo(linha.get("FACT_TIME"))
    if tempo.get("ESTADO") != "INTERVALO":
        return UNKNOWN, None, "FACT_TIME nao cobre intervalo"
    fim = date.fromisoformat(tempo["FIM"])
    if fim >= hoje - timedelta(days=n_dias):
        return CURRENT, tempo, f"fim do facto {fim} >= hoje {hoje} - {n_dias} dias"
    return STALE, tempo, (f"fim do facto {fim} < hoje {hoje} - {n_dias} dias: "
                          "TRUE-BUT-STALE, janela de outro momento nao e a de agora")


def _sobrepoe(a: dict | None, b: dict | None) -> bool:
    if not a or not b:
        return False
    return a["INICIO"] <= b["FIM"] and b["INICIO"] <= a["FIM"]


# ══════════════════════════════════════════════════════════════════════════
# W5 · A REGRA PARTILHADA — sequencias de 10 palavras
# ══════════════════════════════════════════════════════════════════════════
#: O desenho mediu 82 sequencias de 10 palavras partilhadas entre APOL e ARIF (o
#: disciplinare). Semelhanca NAO prova equivalencia (INT-LAW-081), e por isso
#: ela so e usada no sentido CONSERVADOR: nunca soma apoio, so impede que a regra
#: seja contada duas vezes quando a Collection nao declarou a origem.
TAMANHO_DA_SEQUENCIA = 10


def sequencias(texto: str, k: int = TAMANHO_DA_SEQUENCIA) -> set:
    p = _n(texto).split()
    return {" ".join(p[i:i + k]) for i in range(len(p) - k + 1)}


# ══════════════════════════════════════════════════════════════════════════
# O JUIZO
# ══════════════════════════════════════════════════════════════════════════
ACT_NOW = "ACT_NOW"
NO_DEFENSIBLE_ACTION_YET = "NO_DEFENSIBLE_ACTION_YET"
NOT_POSSIBLE = "NOT_POSSIBLE"
CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
SUPPORT, CONTRADICTS = "SUPPORT", "CONTRADICTS"


class LeiViolada(Exception):
    """A capacidade recusou-se, e diz porque."""


def _requisito(item: dict, falta: list, sonda: list, run_id: str) -> dict:
    nomes = sorted({REQUISITO_DA_REGIAO if "REGIAO_DO_FATO" in m else REQUISITO_DO_PAR
                    for m in falta})
    req = {
        "REQUIREMENT_ID": "REQ-" + hashlib.sha256(
            (run_id + "|" + CAPACIDADE + "|" + str(item.get("ITEM_ID", ""))
             + "|" + ",".join(sorted(falta))).encode("utf-8")).hexdigest()[:16],
        "REQUIREMENT": nomes,
        "QUESTION_BLOCKED": ("CAP-WIN: sem CROP_ID x ISSUE_ID x REGION_ID em campo "
                             "nao ha janela de ninguem (INT-LAW-091)"),
        "MISSING_FACT_OR_KEY": sorted(falta),
        # a SONDA prova que o valor existe no bruto; nao vira par (INT-LAW-084)
        "SONDA_DO_TEXTO": sonda,
        "WHY_EXISTING_MATERIAL_IS_INSUFFICIENT": (
            "o texto pode nomear cultura e praga, mas atribuir par por texto e "
            "fabricar CROP_ID/ISSUE_ID; a chave tem de vir em campo, com base"),
        "REQUIRED_SCOPE": {"ITEM_ID": item.get("ITEM_ID", NAO_SEI),
                           "SOURCE_ID": item.get("SOURCE_ID", NAO_SEI),
                           "UNIVERSO": item.get("UNIVERSO", NAO_SEI)},
        "URGENCY": NAO_SEI,
    }
    sujo = [p for p in PALAVRAS_QUE_O_REQUISITO_RECUSA
            if p in json.dumps(req, ensure_ascii=False).upper()]
    if sujo:
        raise LeiViolada("o requisito nomeou palavra da Collection: " + ", ".join(sujo))
    return req


def _evidencias_do_item(item: dict, linha: dict, par: dict, hoje: date,
                        n_dias: int) -> list:
    """Uma evidencia por (oracao, tipo). Cada uma diz o que a FONTE declarou e o
    que disso pode responder «agora»."""
    usos = linha.get("USOS_DISPONIVEIS") or []
    pode_regra = "LEITURA_ATEMPORAL_DE_CAPACIDADE" in usos
    pode_agora = CAPACIDADE in usos
    est, tempo, porque_tempo = estado_temporal(linha, hoje, n_dias)
    fase = None if par["PHENOLOGY_STAGE"] == NAO_SEI else par["PHENOLOGY_STAGE"]
    fora = []
    todas = oracoes(item.get("TEXTO"))
    # O que o DOCUMENTO manda (nao tratar), mesmo numa oracao sem janela: «Pertanto
    # non si ritiene giustificata l'esecuzione di un trattamento». Nao muda o
    # «aberta agora» de ninguem (isso so a oracao da propria condicao decide, como
    # no V21); vai para a LEITURA. O item fala de UM par em campo, por isso a
    # recomendacao nao escorre para outro alvo.
    do_documento = sorted({r for r in (restritiva(o) for o in todas) if r})
    for oracao in todas:
        tipos = tipos_da_oracao(oracao)
        if not tipos:
            continue
        parar = restritiva(oracao)
        for tipo, padrao in tipos:
            dec, metodo = aberta_agora(tipo, oracao, fase)
            if parar and dec != NO:
                dec, metodo = NO, "A_ORACAO_MANDA_PARAR"
            # a resposta ao «agora»: so com o uso CAP-WIN (tempo ancorado) e CURRENT.
            # ADMINISTRATIVE e DELEGADA nao dependem da idade (regra do V21).
            if tipo in (ADMINISTRATIVE_WINDOW, RULE_DELEGATED_TO_FARM):
                agora, metodo_agora = dec, metodo
            elif not pode_agora:
                agora, metodo_agora = UNKNOWN, "OBSERVACAO_SEM_TEMPO: " + porque_tempo
            elif est == STALE:
                agora, metodo_agora = UNKNOWN, "OBSERVACAO_STALE: " + porque_tempo
            elif est != CURRENT:
                agora, metodo_agora = UNKNOWN, "OBSERVACAO_SEM_TEMPO: " + porque_tempo
            else:
                agora, metodo_agora = dec, metodo
            fora.append({
                "ITEM_ID": linha.get("ITEM_ID"), "SOURCE_ID": linha.get("SOURCE_ID"),
                "RAW_OBSERVATION_ID": linha.get("RAW_OBSERVATION_ID"),
                "URL": item.get("URL") or item.get("DOCUMENT_URL"),
                "SUBAREA": par["SUBAREA"], "REDE": par["REDE"],
                "ORIGEM_DA_REGRA": par["ORIGEM_DA_REGRA"],
                "PHENOLOGY_STAGE": par["PHENOLOGY_STAGE"],
                "WINDOW_TYPE": tipo, "MATCHED_PATTERN": padrao,
                "WINDOW_CONDITION": oracao[:320],
                "REGRA_UTILIZAVEL": pode_regra,
                "DECLARADO_PELA_FONTE": dec, "METODO_DECLARADO": metodo,
                "RESTRITIVA": parar, "DOCUMENTO_MANDA_NAO_TRATAR": do_documento,
                "TIME_WINDOW": tempo, "ESTADO_TEMPORAL": est,
                "PORQUE_TEMPO": porque_tempo,
                "WINDOW_OPEN_NOW": agora, "OPEN_NOW_METHOD": metodo_agora,
            })
    return fora


def _arestas(evs: list) -> list:
    """W6 · SUPPORT / CONTRADICTS entre observacoes com tempo, do mesmo par, com
    TIME_WINDOW sobreposto e subarea compativel. UNKNOWN nao apoia nem contradiz.
    Subareas declaradas e DIFERENTES nao se contradizem: sao lugares diferentes."""
    obs = [e for e in evs if e["TIME_WINDOW"] and e["DECLARADO_PELA_FONTE"] in (YES, NO)
           and e["WINDOW_TYPE"] in AGRONOMICOS]
    fora = []
    for i, a in enumerate(obs):
        for b in obs[i + 1:]:
            if a["ITEM_ID"] == b["ITEM_ID"] or not _sobrepoe(a["TIME_WINDOW"], b["TIME_WINDOW"]):
                continue
            if NAO_SEI not in (a["SUBAREA"], b["SUBAREA"]) and a["SUBAREA"] != b["SUBAREA"]:
                continue
            fora.append({
                "TIPO": SUPPORT if a["DECLARADO_PELA_FONTE"] == b["DECLARADO_PELA_FONTE"]
                else CONTRADICTS,
                "DE": a["ITEM_ID"], "PARA": b["ITEM_ID"],
                "VALORES": [a["DECLARADO_PELA_FONTE"], b["DECLARADO_PELA_FONTE"]],
                "TIME_WINDOWS": [a["TIME_WINDOW"], b["TIME_WINDOW"]],
            })
    return fora


def _apoios(evs: list, valor: str, textos: dict) -> dict:
    """W5 · apoios da OBSERVACAO (pelo grafo, e pelas redes declaradas) e da
    REGRA (uma origem conta uma vez)."""
    a_favor = [e for e in evs if e["WINDOW_OPEN_NOW"] == valor and valor in (YES, NO)]
    por_item = {}
    for e in a_favor:
        por_item.setdefault(e["ITEM_ID"], e)
    g = GD.grafo([{"ID": e["ITEM_ID"], "URL": e["URL"], "SOURCE_ID": e["SOURCE_ID"]}
                  for e in por_item.values()])
    redes = [e["REDE"] for e in por_item.values()]
    if por_item and all(redes):
        provadas = len(set(redes))
        base_rede = "REDES_DECLARADAS_PELA_COLLECTION"
    else:
        provadas = NAO_SEI if por_item else 0
        base_rede = ("a Collection nao declarou a rede de monitorizacao de todas as "
                     "observacoes: originador distinto NAO prova rede independente")
    observacao = {
        "SINAIS": len(a_favor), "EVIDENCIAS": g["EVIDENCE_BASE_COUNT"],
        "ORIGINADORES_DISTINTOS": g["INDEPENDENT_SOURCE_COUNT"],
        "ORIGINADORES": [f["ORIGINADOR"] for f in g["SOURCE_FAMILIES"]],
        "INDEPENDENTES_PROVADOS": provadas,
        "INDEPENDENTES_PROVAVEIS": g["INDEPENDENT_SOURCE_COUNT_MAX"],
        "BASE": base_rede,
        # a CONVERGENCE do grafo e por ORIGINADOR distinto (dominio); quem decide
        # o W8 e INDEPENDENTES_PROVADOS (redes), e nao ela
        "GRAFO": {k: g[k] for k in ("VERSAO", "CONVERGENCE", "CONVERGENCE_WHY",
                                    "INDEPENDENCE_BASIS", "DOMINANT_SOURCE",
                                    "DOMINANT_SOURCE_SHARE_PCT")},
    }
    # ── a regra ──
    com_regra = {}
    for e in evs:
        if e["REGRA_UTILIZAVEL"] and e["WINDOW_TYPE"] in AGRONOMICOS:
            com_regra.setdefault(e["ITEM_ID"], e)
    declaradas = {e["ORIGEM_DA_REGRA"] for e in com_regra.values() if e["ORIGEM_DA_REGRA"]}
    orig_regra = GD.grafo([{"ID": e["ITEM_ID"], "URL": e["URL"], "SOURCE_ID": e["SOURCE_ID"]}
                           for e in com_regra.values()])
    ids = sorted(com_regra)
    partilhadas = 0
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            partilhadas = max(partilhadas, len(sequencias(textos.get(a, ""))
                                               & sequencias(textos.get(b, ""))))
    if com_regra and all(e["ORIGEM_DA_REGRA"] for e in com_regra.values()):
        conta, base = len(declaradas), "ORIGEM_DA_REGRA declarada pela Collection"
    elif not com_regra:
        conta, base = 0, "nenhuma regra utilizavel"
    else:
        conta = 1
        base = ((f"{partilhadas} sequencias de {TAMANHO_DA_SEQUENCIA} palavras partilhadas: "
                 "texto normativo comum provavel; a regra conta UMA vez")
                if partilhadas else
                "origem da regra nao declarada: a regra conta UMA vez ate a Collection "
                "declarar origens distintas (unir a mais so esconde independencia)")
    regra = {"CONTA": conta, "BASE": base, "SEQUENCIAS_PARTILHADAS": partilhadas,
             "ORIGINADORES_QUE_A_CITAM": orig_regra["INDEPENDENT_SOURCE_COUNT"],
             "ORIGENS_DECLARADAS": sorted(declaradas)}
    return {"OBSERVACAO": observacao, "REGRA": regra}


def _julgar_par(chave: tuple, evs: list, textos: dict, run_id: str) -> dict:
    crop, issue, regiao = chave
    agron = [e for e in evs if e["WINDOW_TYPE"] in AGRONOMICOS and e["REGRA_UTILIZAVEL"]]
    definida = sorted({e["WINDOW_TYPE"] for e in agron})
    admin = [e for e in evs if e["WINDOW_TYPE"] == ADMINISTRATIVE_WINDOW]
    arestas = _arestas(evs)
    contra = [a for a in arestas if a["TIPO"] == CONTRADICTS]

    # W3/W4 · o «agora», so das observacoes utilizaveis
    usaveis = [e for e in agron if e["WINDOW_OPEN_NOW"] in (YES, NO)]
    valores = {e["WINDOW_OPEN_NOW"] for e in usaveis}
    limitacoes = []
    if contra:
        aberta, metodo = UNKNOWN, CONFLICTING_EVIDENCE
    elif len(valores) == 1:
        aberta = valores.pop()
        metodo = sorted({e["OPEN_NOW_METHOD"] for e in usaveis if e["WINDOW_OPEN_NOW"] == aberta})
    elif len(valores) > 1:
        # YES e NO em subareas diferentes ou tempos que nao se tocam: nao ha um
        # «agora» unico do par inteiro, e nao se escolhe um.
        aberta, metodo = UNKNOWN, "SUBAREAS_OU_PERIODOS_DIVERGEM"
    else:
        aberta = UNKNOWN
        metodo = sorted({e["OPEN_NOW_METHOD"] for e in agron}) or ["SEM_JANELA_DEFINIDA"]
    for e in agron:
        if e["WINDOW_OPEN_NOW"] == UNKNOWN and (e["SUBAREA"] != NAO_SEI or aberta != UNKNOWN):
            limitacoes.append(f"subarea {e['SUBAREA']} ({e['ITEM_ID']}): UNKNOWN — "
                              f"{e['OPEN_NOW_METHOD']}")
    for e in agron:
        if e["DECLARADO_PELA_FONTE"] != e["WINDOW_OPEN_NOW"]:
            limitacoes.append(f"{e['ITEM_ID']}: a fonte declara {e['DECLARADO_PELA_FONTE']} "
                              f"({e['METODO_DECLARADO']}), mas nao responde agora — "
                              f"{e['OPEN_NOW_METHOD']}")
    estados = {e["ESTADO_TEMPORAL"] for e in usaveis if e["WINDOW_OPEN_NOW"] == aberta}
    estado_temporal_ = (CURRENT if estados == {CURRENT}
                        else STALE if {e["ESTADO_TEMPORAL"] for e in agron} == {STALE}
                        else UNKNOWN)
    apoios = _apoios(agron, aberta, textos)
    obs = apoios["OBSERVACAO"]

    # W8 · ACT_NOW, e so com as quatro coisas
    porque = []
    if aberta != YES:
        porque.append(f"WINDOW_OPEN_NOW = {aberta} ({metodo if isinstance(metodo, str) else ', '.join(metodo)})")
    if estado_temporal_ != CURRENT:
        porque.append(f"ESTADO_TEMPORAL = {estado_temporal_}")
    if not (isinstance(obs["INDEPENDENTES_PROVADOS"], int) and obs["INDEPENDENTES_PROVADOS"] >= 2):
        porque.append(f"apoios independentes provados na observacao = "
                      f"{obs['INDEPENDENTES_PROVADOS']} (exige >= 2; provaveis "
                      f"{obs['INDEPENDENTES_PROVAVEIS']})")
    if contra:
        porque.append(f"{len(contra)} contradicao(oes) aberta(s): as duas visiveis")
    if not definida:
        porque.append("nenhuma janela agronomica definida para o par")
    restr = sorted({r for e in agron for r in e["DOCUMENTO_MANDA_NAO_TRATAR"]})
    resultado = ACT_NOW if not porque else NO_DEFENSIBLE_ACTION_YET
    leitura = None
    if resultado == NO_DEFENSIBLE_ACTION_YET and aberta == NO:
        leitura = "monitorizar; a condicao de intervencao nao esta satisfeita" + (
            " e a fonte declara que o tratamento nao se justifica" if restr else "")
    sid = "CW-" + hashlib.sha256(("|".join([run_id, crop, issue, regiao])).encode()).hexdigest()[:16]
    return {
        "OBJECT": "ANALYTIC_JUDGMENT", "SPECIES": "CROP_WINDOW", "CROP_WINDOW_ID": sid,
        "CAPABILITY": CAPACIDADE, "VERSION": VERSAO,
        "CROP_ID": crop, "ISSUE_ID": issue, "REGION_ID": regiao,
        "SUBAREAS": sorted({e["SUBAREA"] for e in evs}),
        "PHENOLOGY_STAGE": sorted({e["PHENOLOGY_STAGE"] for e in evs}),
        "TIME_WINDOW": sorted([e["TIME_WINDOW"] for e in evs if e["TIME_WINDOW"]],
                              key=lambda t: t["INICIO"]) or NAO_SEI,
        "WINDOW_DEFINED": "YES" if definida else "NO",
        "WINDOW_TYPES": definida,
        "WINDOW_CONDITIONS": sorted({e["WINDOW_CONDITION"] for e in agron}),
        "ADMINISTRATIVE_CONSTRAINTS": sorted({e["WINDOW_CONDITION"] for e in admin}),
        "WINDOW_OPEN_NOW": aberta, "METHOD": metodo,
        "TEMPORAL_STATE": estado_temporal_,
        "SUPPORTS": apoios,
        "EDGES": arestas, "CONTRADICTIONS": contra,
        "SOURCE_SAYS_DO_NOT_TREAT": restr,
        "LIMITATIONS": limitacoes,
        "RESULT": resultado, "WHY": porque or ["as quatro condicoes do W8 estao satisfeitas"],
        "READING": leitura,
        "EVIDENCE": evs,
        "LINEAGE": sorted({(e["ITEM_ID"], e["SOURCE_ID"], e["RAW_OBSERVATION_ID"]) for e in evs}),
    }


def produtos_adama(ref: dict, crop: str, issue: str) -> dict:
    """A janela -> os produtos ADAMA que a bula lida autoriza para a cultura x problema.

    PELA PORTA, e so do REGISTRO: catalogo nao e autorizacao. Nao mexe no RESULT da janela
    (produto autorizado nao abre janela nenhuma), e bula nao lida fica A_CONFIRMAR.
    """
    r = PORTA.autorizados(ref, crop, issue)
    r.pop("CARIMBO", None)
    r["EDICAO_REGISTRO"] = (ref.get("REGISTRO") or {}).get("EDICAO", NAO_SEI) \
        if isinstance(ref, dict) else NAO_SEI
    return r


def julgar(livro: dict, itens: list, hoje: date, n_dias: int = N_DIAS_CURRENT,
           fora: dict | None = None, referencia: dict | None = None) -> dict:
    """A CAP-WIN sobre UMA corrida G0/v4. `hoje` e obrigatorio: quem pergunta
    «agora» diz que dia e agora — nunca o relogio escondido.

    `fora` (INT-R7-CAPS) = {ITEM_ID: motivo} dos itens que o motor das
    capacidades triou para OUTRA capacidade (ex.: um estudo declarado no FATO
    vai para a CAP-SCI: estudo nunca vira observacao de janela). Esses itens
    continuam no livro e na contagem, saem em `FORA` com o motivo, e nao geram
    requisito de par em campo — pedir CROP_ISSUE_EM_CAMPO a um estudo seria a
    Intelligence a fabricar necessidade (INT-LAW-014)."""
    if not isinstance(hoje, date):
        raise LeiViolada("sem HOJE declarado nao ha «agora»: a janela nao se julga")
    if livro.get("RULESET_VERSION") != CI.RULESET_VERSION or livro.get("RESULT_STATE") not in ("DONE", "REUSED"):
        raise LeiViolada("a CAP-WIN so le um livro G0/v4 fechado (DONE/REUSED)")
    linhas = livro.get("LINEAGE") or []
    if len(linhas) != len(itens):
        raise LeiViolada("PRE_FILTRO: o livro tem %d linhas e chegaram %d itens"
                         % (len(linhas), len(itens)))
    run_id = livro["INTELLIGENCE_RUN_ID"]
    pares, nao_possivel, requisitos, textos, fora_daqui = {}, [], [], {}, []
    fora = fora or {}
    for item, linha in zip(itens, linhas):
        if item.get("ITEM_ID", NAO_SEI) != linha.get("ITEM_ID"):
            raise LeiViolada("o livro e os itens nao estao na mesma ordem")
        if linha.get("ITEM_ID") in fora:
            fora_daqui.append({"ITEM_ID": linha.get("ITEM_ID"),
                               "PORQUE": fora[linha.get("ITEM_ID")]})
            continue
        if linha.get("PROVENIENCIA") != "COMPLETA":
            nao_possivel.append({"ITEM_ID": linha.get("ITEM_ID"), "ESTADO": NOT_POSSIBLE,
                                 "PORQUE": "SEM_PROVENIENCIA: " + str(linha.get("PROVENIENCIA"))})
            continue
        par, falta = par_em_campo(item)
        if par is None:
            sonda = sorted({t for o in oracoes(item.get("TEXTO")) for t, _p in tipos_da_oracao(o)})
            req = _requisito(item, falta, sonda, run_id)
            requisitos.append(req)
            nao_possivel.append({"ITEM_ID": linha.get("ITEM_ID"), "ESTADO": NOT_POSSIBLE,
                                 "PORQUE": "INT-LAW-091: " + "; ".join(falta),
                                 "REQUIREMENT_ID": req["REQUIREMENT_ID"]})
            continue
        textos[linha.get("ITEM_ID")] = str(item.get("TEXTO") or "")
        chave = (par["CROP_ID"], par["ISSUE_ID"], par["REGION_ID"])
        pares.setdefault(chave, []).extend(
            _evidencias_do_item(item, linha, par, hoje, n_dias))
    janelas = [_julgar_par(k, v, textos, run_id) for k, v in sorted(pares.items())]
    ref = referencia if referencia is not None else PORTA.abrir(hoje=hoje)
    for j in janelas:
        j["PRODUTOS_ADAMA"] = produtos_adama(ref, j["CROP_ID"], j["ISSUE_ID"])
    return {
        "SCHEMA": VERSAO, "CAPABILITY": CAPACIDADE,
        "INTELLIGENCE_RUN_ID": run_id, "RULESET_VERSION": livro.get("RULESET_VERSION"),
        "HOJE": hoje.isoformat(),
        "REFERENCIA_ADAMA": PORTA.carimbo(ref),
        "N_DIAS_CURRENT": n_dias, "N_DIAS_CURRENT_ESTADO": N_DIAS_CURRENT_ESTADO,
        "REGRA_PORTADA_DE": REGRA_PORTADA_DE,
        "CAPACIDADES_EXECUTADAS": {CAPACIDADE: {"VERSION": VERSAO, "RUN": run_id}},
        "ANALYTIC_OUTPUT": (ACT_NOW if any(j["RESULT"] == ACT_NOW for j in janelas)
                            else NO_DEFENSIBLE_ACTION_YET if janelas else NOT_POSSIBLE),
        "CROP_WINDOWS": janelas,
        "NOT_POSSIBLE": nao_possivel,
        "FORA": fora_daqui,
        "REQUIREMENTS": requisitos,
        "OPPORTUNITIES": [],
        "ESTADO": "EXPERIMENTAL / NAO_PARA_CLIENTE",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="CAP-WIN sobre uma corrida G0/v4")
    ap.add_argument("itens")
    ap.add_argument("--hoje", required=True, help="AAAA-MM-DD: o «agora» declarado")
    a = ap.parse_args()
    itens = json.loads(Path(a.itens).read_text(encoding="utf-8"))
    if isinstance(itens, dict):
        itens = itens.get("ITENS", [itens])
    livro = CI.correr("CAP-WIN: qual e a janela, e esta aberta agora?", itens,
                      universo={"ITENS_NO_CORTE": len(itens)})
    print(json.dumps(julgar(livro, itens, date.fromisoformat(a.hoje)),
                     ensure_ascii=False, indent=1, default=list))
    return 0


if __name__ == "__main__":
    sys.exit(main())
