#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OS DADOS DA CASA — a unica cadeia que chega ao browser.

    python3 scripts/it_casa_dados.py

POR QUE ESTE FICHEIRO EXISTE
----------------------------
A HOME tem de responder em trinta segundos o que esta em cima da mesa hoje. A
tentacao e responder com os numeros grandes que ja temos a mao: 9.574, 624,
607, 560. Todos verdadeiros. Nenhum e uma decisao.

    UM NUMERO DE ACERVO NA PRIMEIRA DOBRA MEDE O NOSSO ESFORCO,
    NAO O QUE O CLIENTE TEM DE FAZER NA SEGUNDA-FEIRA.

Por isso este gerador so deixa passar numeros de DECISAO — quantas oportunidades
estao na mesa agora, quantas preparar, quantas monitorar, onde temos olhos — e
le-os dos donos que ja os decidiram, sem os recontar. Recontar aqui criaria um
segundo dono de cada contagem.

UMA CADEIA, E UM SO PACOTE
--------------------------
O browser NAO le handoff cru. Este ficheiro e o adaptador de APRESENTACAO: le os
artefactos ja julgados a montante e escreve UM pacote — italy-casa.js — que
casa.html e portale.html consomem. Ele pode escolher registos autorizados,
normalizar, agrupar, ordenar, ligar evidencia e serializar.

    O QUE ELE NAO PODE FAZER: reclassificar, mudar prioridade, promover
    evidence-only, recuperar derrubado, criar oportunidade, reinterpretar
    NAO SEI.

OS DONOS QUE ELE CONSOME — E NAO SUBSTITUI
------------------------------------------
  · as 43 oportunidades atuais  -> meeting-intelligence-snapshot.json
    (motor V21, BUILD_ID carimbado). O 43 sai de la; escreve-lo aqui a mao
    faria dele uma segunda verdade, e duas verdades divergem.
  · o Radar Futuro 45/44/1      -> IT-FUTURO-HANDOFF-LINHA-B-V1.json
  · campo, fontes, evidencia    -> os handoffs Linha B ja ingeridos
  · prioridade -> estado do cliente -> meeting-surface.js
  · CADA frase IT/EN de codigo  -> meeting-labels.js

Os dois ultimos sao lidos do proprio ficheiro que os possui, e nao copiados:
uma copia e um segundo dono a espera de discordar.

    UM CODIGO SEM PAR IT+EN NAO SAI DAQUI. A GERACAO FALHA.

A LINGUA DA TELA E O ITALIANO, E ISSO NAO E COSMETICA. A inteligencia foi
investigada em portugues, e o portal ja tem um portao inteiro (audit/lang.mjs)
nascido de prosa de investigacao portuguesa a chegar ao cliente italiano. Aqui
cada frase que vai a tela viaja em par: IT e a que se le, PT e a que foi escrita.

    TRADUZIR A NOSSA PROSA E LOCALIZACAO. TRADUZIR O FACTO SERIA REESCREVE-LO.

Por isso so a NOSSA moldura — limites, leis, perguntas — e vertida. Numeros,
nomes de produto, numeros de registo, datas e estados administrativos ficam
exactamente como o registo os publica, em italiano de origem. E a prosa de
investigacao portuguesa do motor nunca atravessa como texto: atravessa o
DOCUMENTO que a contem, que e verdade, e nao a frase.

E DETERMINISTICO: sem relogio, sem aleatorio, chaves ordenadas. A data de
referencia sai dos artefactos, nunca da maquina que corre isto — um carimbo de
relogio faria duas corridas identicas produzirem ficheiros diferentes, e o
"rodei duas vezes e deu igual" deixaria de provar o que quer que seja.
"""
import hashlib
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# A LEI DE RELEVANCIA TEM UM DONO SO, E NAO E ESTE FICHEIRO. Aqui importa-se e
# imprime-se o veredito; recalcula-lo aqui daria duas leis com o mesmo nome.
from adama_relevance import (CONTRATO as LEI_ADAMA, classificar, contar,
                             restricoes_separadas, SUPERFICIE)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, 'italia-portale', 'client')
UP = os.path.join(CLI, 'upstream')
OUT = os.path.join(CLI, 'italy-casa.js')
OUT_REL = os.path.join(CLI, 'adama-relevance.js')
SNAPSHOT = os.path.join(CLI, 'meeting-intelligence-snapshot.json')
LABELS_JS = os.path.join(CLI, 'meeting-labels.js')
SURFACE_JS = os.path.join(CLI, 'meeting-surface.js')


def _bytes(p):
    with io.open(p, 'rb') as f:
        return f.read()


def ler(nome):
    cru = _bytes(os.path.join(UP, nome))
    return json.loads(cru.decode('utf-8')), 'sha256:' + hashlib.sha256(cru).hexdigest()


def ler_json(p):
    cru = _bytes(p)
    return json.loads(cru.decode('utf-8')), 'sha256:' + hashlib.sha256(cru).hexdigest()


# ── O DICIONARIO, LIDO DO SEU DONO ──────────────────────────────────────────
# meeting-labels.js e o unico sitio onde um codigo canonico vira frase. Copiar
# as frases para aqui faria deste ficheiro um SEGUNDO dono de labels — e duas
# tabelas da mesma lei divergem na terceira vez que alguem mexe numa.
#
#     O PACOTE TRANSPORTA AS FRASES. NAO AS ESCREVE.
_ESC = re.compile(r'\\(u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)', re.S)
_ROW = re.compile(
    r"""(?:^|\n)\s*(?:([A-Za-z_$][\w$]*)|'((?:[^'\\]|\\.)*)')\s*:\s*"""
    r"""\[\s*((?:'(?:[^'\\]|\\.)*'|\s|,|\n)*?)\]""")
_STR = re.compile(r"'(?:[^'\\]|\\.)*'")


def _un(m):
    t = m.group(1)
    if t[0] in 'ux':
        return chr(int(t[1:], 16))
    return {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', '0': '\0'}.get(t, t)


def _desescapar(s):
    return _ESC.sub(_un, s)


def carregar_labels():
    src = _bytes(LABELS_JS).decode('utf-8')
    h = 'sha256:' + hashlib.sha256(_bytes(LABELS_JS)).hexdigest()
    i = src.index('const L = {')
    j = src.index('\n  };', i)
    corpo = src[i:j]
    tab = {}
    for m in _ROW.finditer(corpo):
        chave = m.group(1) if m.group(1) is not None else _desescapar(m.group(2))
        partes = [_desescapar(p[1:-1]) for p in _STR.findall(m.group(3))]
        if len(partes) != 2 or not partes[0] or not partes[1]:
            raise SystemExit('meeting-labels.js: %r nao traz par IT+EN' % chave)
        tab[chave] = {'it': partes[0], 'en': partes[1]}
    # Um parser que devolve pouco nao e um dicionario pequeno: e um parser
    # partido a fingir que o dicionario encolheu.
    if len(tab) < 300:
        raise SystemExit('o parser leu %d linhas de meeting-labels.js — parece partido' % len(tab))
    return tab, h


def carregar_estado_cliente():
    """A regra COMMERCIAL_PRIORITY -> estado do cliente, lida do seu dono.

    Ela vive em meeting-surface.js e ja governa o portal. Reescreve-la aqui
    daria duas regras com o mesmo nome, e a segunda passaria a decidir quem e
    oportunidade comercial sem ninguem ter aprovado isso.
    """
    src = _bytes(SURFACE_JS).decode('utf-8')
    m = re.search(r'const CLIENT_STATE = \{(.*?)\n  \};', src, re.S)
    if not m:
        raise SystemExit('meeting-surface.js: CLIENT_STATE nao encontrado')
    mapa = dict(re.findall(r"([A-Z_]+):\s*'([A-Z_]+)'", m.group(1)))
    if len(mapa) != 3:
        raise SystemExit('CLIENT_STATE tem %d entradas, esperadas 3' % len(mapa))
    return mapa


# ── O PONTEIRO NAO E O FATO ─────────────────────────────────────────────────
# O motor escreve a propria prosa IT/EN e em alguns casos fecha-a com um
# rimando aos proprios campos («...— vedi NEED_DIRECTION e NEED_EXCERPT.»).
# Essa cauda foi escrita para quem le o JSON, e poe duas chaves internas num
# ecra italiano. Tira-se o PONTEIRO, nunca a afirmacao.
#
# A regra e a mesma de meeting-surface.js, letra por letra, e o portao
# casa-gate prova que as duas produzem exactamente o mesmo texto nas 86
# frases — se divergirem, o portao reprova em vez de a divergencia viajar.
_PONTEIRO = re.compile(
    r'\s*[—–-]\s*(?:vedi|see|cfr\.?|si veda)\b[^.;]*'
    r'\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b[^.;]*\.?\s*$')


def sem_ponteiro(texto):
    if not isinstance(texto, str) or not texto:
        return {'text': texto or '', 'pointerRemoved': False}
    corte = _PONTEIRO.sub('', texto).strip()
    if corte == texto.strip():
        return {'text': texto.strip(), 'pointerRemoved': False}
    if len(corte) < 12:
        return {'text': texto.strip(), 'pointerRemoved': False}
    return {'text': corte if corte[-1] in '.!?' else corte + '.', 'pointerRemoved': True}


# ── A NOSSA MOLDURA, EM ITALIANO E EM INGLES ────────────────────────────────
# Chave = o texto portugues tal como o handoff a montante o escreveu; valor = o
# PAR que se le na tela. Deixar isto explicito faz da traducao uma coisa
# auditavel: quem quiser conferir compara as colunas, em vez de procurar a frase
# num ficheiro e confiar. Se o texto a montante mudar, a chave deixa de casar e
# o gerador PARA — nao renderiza portugues em silencio.
#
# PORQUE UM PAR E NAO SO O ITALIANO: a casa desenha-se tambem em ingles. Enquanto
# esta tabela tinha uma coluna so, a superficie inglesa dizia «It never answers
# "qui c'e un problema"» — italiano dentro de uma frase inglesa. Foi o detector
# de DO_NOT_SHOW a apanha-lo, e nao a revisao: a negacao inglesa nao era
# reconhecida, e por isso a frase proibida contou como afirmada.
#
#     UMA SUPERFICIE BILINGUE COM UMA TABELA MONOLINGUE
#     NAO TRADUZ METADE: MOSTRA A OUTRA LINGUA COMO SE FOSSE A SUA.
MOLDURA = {
 'temos olhos aqui': {
   'it': 'qui abbiamo occhi',
   'en': 'we have eyes here'},
 'há problema aqui': {
   'it': 'qui c\'è un problema',
   'en': 'there is a problem here'},
 'o concorrente tem ~10 meses a mais de janela autorizada na mesma dupla de substâncias': {
   'it': 'il concorrente ha circa 10 mesi in più di finestra autorizzata sulla stessa coppia di sostanze',
   'en': 'the competitor has about 10 more months of authorised window on the same pair of substances'},
 'quatro registros, todos vigentes: dois da ADAMA ITALIA S.R.L. vencendo em 31/05/2027 e dois da CAC CHEMICAL GMBH vencendo em 31/03/2028': {
   'it': 'quattro registri, tutti vigenti: due di ADAMA ITALIA S.R.L. in scadenza il 31/05/2027 e due di CAC CHEMICAL GMBH in scadenza il 31/03/2028',
   'en': 'four registrations, all live: two held by ADAMA ITALIA S.R.L. expiring on 31/05/2027 and two held by CAC CHEMICAL GMBH expiring on 31/03/2028'},
 'produtos cujo campo `sostanze_attive` nomeia AZOXYSTROBIN E PROTHIOCONAZOLE ao mesmo tempo': {
   'it': 'prodotti il cui campo `sostanze_attive` nomina AZOXYSTROBIN e PROTHIOCONAZOLE insieme',
   'en': 'products whose `sostanze_attive` field names AZOXYSTROBIN and PROTHIOCONAZOLE together'},
 'ato europeu e registro nacional NÃO são duas fontes independentes: o nacional deriva do europeu. Contá-los como duas confirmações infla a confiança de um fato que tem uma origem só.': {
   'it': 'atto europeo e registro nazionale NON sono due fonti indipendenti: il nazionale deriva dall\'europeo. Contarli come due conferme gonfia la fiducia in un fatto che ha una sola origine.',
   'en': 'the European act and the national register are NOT two independent sources: the national one derives from the European one. Counting them as two confirmations inflates confidence in a fact that has a single origin.'},
 'se a renovação de 31/05/2027 já está em curso, e se a diferença de janela importa comercialmente': {
   'it': 'se il rinnovo del 31/05/2027 sia già in corso, e se lo scarto di finestra conti commercialmente',
   'en': 'whether the 31/05/2027 renewal is already under way, and whether the window gap counts commercially'},
 'REGRA METODOLÓGICA, não fato bruto: organização territorial Tier A/B sem especialidade declarada cobre todas as especialidades da sua cultura naquela região': {
   'it': 'REGOLA METODOLOGICA, non dato grezzo: un\'organizzazione territoriale Tier A/B senza specialità dichiarata copre tutte le specialità della sua coltura in quella regione',
   'en': 'a METHODOLOGICAL RULE, not raw data: a Tier A/B territorial organisation with no declared speciality covers every speciality of its crop in that area'},
 'STRICT mais "Ri-registrato*" e "Rinnovato*"': {
   'it': 'STRICT piu «Ri-registrato*» e «Rinnovato*»',
   'en': 'STRICT plus «Ri-registrato*» and «Rinnovato*»'},
 'apenas estados administrativos que contêm "Autorizzato"': {
   'it': 'solo gli stati amministrativi che contengono «Autorizzato»',
   'en': 'only administrative states containing «Autorizzato»'},
 'JULGAMENTO HUMANO, não fato do registro — é a lacuna DECK-015 (titular ≠ grupo empresarial)': {
   'it': 'GIUDIZIO UMANO, non fatto del registro — è la lacuna DECK-015 (titolare non equivale a gruppo societario)',
   'en': 'a HUMAN JUDGEMENT, not a fact of the register — it is the DECK-015 gap (holder is not the same as corporate group)'},
 'NÃO SEI declarado. Uma autorização suspensa não está vigente nem revogada, e nenhum dos critérios acima diz o que fazer com ela. Não forçar para nenhum dos lados até existir regra dona.': {
   'it': 'NON SO, dichiarato. Un\'autorizzazione sospesa non è né vigente né revocata, e nessuno dei criteri sopra dice cosa farne. Non si forza da nessuna parte finché non esiste una regola che ne risponda.',
   'en': 'UNKNOWN, declared. A suspended authorisation is neither live nor revoked, and none of the criteria above says what to do with it. It is not forced either way until a rule owns the question.'},
 'data de validade sozinha não responde se um registro está utilizável: 223 autorizações estão REVOCATO com vencimento ainda no futuro': {
   'it': 'la sola data di scadenza non dice se un registro sia utilizzabile: 223 autorizzazioni sono REVOCATO con scadenza ancora nel futuro',
   'en': 'the expiry date alone does not say whether a registration is usable: 223 authorisations are REVOCATO with an expiry still in the future'},
 'motivo declarado em 1119 de 13216. Nos outros, por que foi revogado é NÃO SEI — e não se infere.': {
   'it': 'motivo dichiarato in 1.119 su 13.216. Per gli altri, il perché della revoca è NON SO — e non si deduce.',
   'en': 'a reason is declared in 1,119 of 13,216. For the rest, why it was revoked is UNKNOWN — and it is not inferred.'},

}


# Os tokens do vocabulario interno. Um enum na tela e JSON cru na cara do
# cliente: "NAO" nao e uma palavra italiana, e "NAO_SEI" lido por quem nao
# conhece a regua parece um erro de sistema em vez de uma resposta valida.
# O token fica no artefacto; o que se le e a frase.
ENUM_IT = {
 'NAO': 'no',
 'SIM': 'sì',
 'NAO_SEI': 'NON SO',
 'EXECUTAVEL_COM_ADAPTADOR': 'eseguibile con adattatore',
 'NAO_EXECUTAVEL': 'non eseguibile',
 'SEM_TRANSICAO_SUSTENTADA': 'nessuna transizione sostenuta',
 'PREPARAR->AGIR_AGORA': 'PREPARARE -> AGIRE ORA',
 'OFFICIAL': 'UFFICIALE',
 'SCIENTIFIC': 'SCIENTIFICA',
}


def enum(tok):
    v = ENUM_IT.get(tok)
    if v is None:
        raise SystemExit('token de vocabulario sem leitura italiana: %r' % tok)
    return v


def it(frase):
    """O PAR IT+EN da tela, ou PARA.

    Traduzir por aproximacao seria pior do que nao traduzir: uma frase que
    ninguem escreveu a proposito acaba a explicar um facto ao cliente. E meia
    traducao — italiano onde se pediu ingles — nao e meia falha: e a outra
    lingua a passar por lingua da casa.
    """
    v = MOLDURA.get(frase)
    if v is None:
        raise SystemExit(
            'sem traducao para uma frase que vai a tela:\n  %r\n'
            'acrescente o par IT+EN ao dicionario MOLDURA em scripts/it_casa_dados.py.'
            % frase[:200])
    if not v.get('it') or not v.get('en'):
        raise SystemExit('a moldura tem meia traducao para %r' % frase[:120])
    return dict(v)


def par(it_txt, en_txt):
    """Uma frase nossa, escrita aqui, nas duas linguas — ou PARA."""
    if not it_txt or not en_txt:
        raise SystemExit('frase da moldura sem par IT+EN: %r / %r' % (it_txt, en_txt))
    return {'it': it_txt, 'en': en_txt}


# ── A CLASSE PORTUGUESA DO REGISTO ITFC, DITA POR CODIGO ────────────────────
# `O_CARTAO_PODE` chega como frase portuguesa. Ela nao atravessa: atravessa o
# CODIGO equivalente, e a frase italiana vem do dicionario como qualquer outra.
CARTAO_PODE = {
 'pode citar o portfolio medido': 'CARD_MAY_CITE_MEASURED',
 'pode citar o zero, COM numerador e denominador': 'CARD_MAY_CITE_ZERO',
 'usa SOMENTE a evidencia congelada e rastreavel; consulta viva PROIBIDA': 'CARD_MAY_FROZEN_ONLY',
 'o NAO e CEGO, nao e ausencia real de portfolio — tem de o dizer': 'CARD_MAY_BLIND_NO',
 'mostra UNKNOWN e o bloqueador nomeado; NAO usa o par': 'CARD_MAY_UNKNOWN_ONLY',
}

# ── O INNESCO, TRANSPORTADO POR CODIGO E NAO POR FRASE ──────────────────────
# `NEXT_TRIGGER` chega como frase PORTUGUESA de vocabulario fechado, e e por
# essa frase que meeting-labels.js a indexa — o dicionario e dela dono e assim
# fica. Mas embarcar a chave portuguesa no pacote poria prosa de investigacao
# dentro do ficheiro que o browser carrega, mesmo que a tela mostre italiano.
#
#     NAO RENDERIZADO NAO E O MESMO QUE NAO ENTREGUE.
#
# Por isso o pacote transporta um CODIGO, e a frase que ele carrega continua a
# ser exactamente a que o dono escreveu — copiada, nunca reescrita.
INNESCO_CODIGO = {
 'um boletim novo que declare necessidade positiva': 'TRIGGER_NEW_BULLETIN_POSITIVE_NEED',
 'evidencia de que a condicao declarada esta satisfeita agora — estadio, limiar medido, captura ou evento climatico':
   'TRIGGER_DECLARED_CONDITION_MET',
}

# A ordem dos reparos. Desenvolvimento de Mercado vem primeiro porque e o
# destinatario central quando ha base — e nao porque seja mais importante em
# abstracto: e o unico que recebe accao em todos os 43.
DEPT_ORDER = ['MARKET_DEVELOPMENT', 'COMMERCIAL', 'MARKETING', 'TECHNICAL_SCIENTIFIC', 'SUPPLY']
# A CADEIA, na ordem em que se parte.
CHAIN = ['SINAL_ATUAL', 'JANELA_DEFINIDA', 'JANELA_ABERTA_AGORA',
         'VINCULO_COM_PORTFOLIO', 'TEMPO_PARA_ACAO']
# A JANELA DE ACCAO, SO ONDE O MOTOR A DECLARA.
# ACT, PREPARE e WATCH tem janela. VALIDATE e NO_ACTION nao tem, e forca-los
# para dentro de uma das tres seria decidir no lugar do motor.
JANELA_DA_ACAO = {'ACT': 'WINDOW_ACT_NOW', 'PREPARE': 'WINDOW_PREPARE', 'WATCH': 'WINDOW_MONITOR'}
# Estados de arrefecimento: a evidencia que ESFRIA o caso. Vem do motor, em
# NEED_DIRECTION ou em ACTION_RECOMMENDATION_STATE, e le-se como inteligencia.
ARREFECEM_DIRECAO = ('NO_ACTION_RECOMMENDED', 'ACTION_SUSPENDED',
                     'TREATMENT_PROHIBITED', 'WINDOW_CONCLUDED')
ARREFECEM_RECOMENDACAO = ('NOT_NEEDED_DECLARED', 'PROHIBITED_DECLARED',
                          'SUSPEND_RECOMMENDED', 'CONCLUDED_DECLARED')


def main():
    RF, h_rf = ler('IT-FUTURO-HANDOFF-LINHA-B-V1.json')
    SC, h_sc = ler('IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json')
    FO, h_fo = ler('IT-HANDOFF-LINHA-B-FONTES-V1.json')
    FI, h_fi = ler('IT-HANDOFF-LINHA-B-FITOSSANITARIO-V1.json')
    HS, h_hs = ler('IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json')
    T3, h_t3 = ler('IT-TOP3-SENSORES-V1.json')
    MI, h_mi = ler_json(SNAPSHOT)

    LABELS, h_lab = carregar_labels()
    CLIENT_STATE = carregar_estado_cliente()

    # O alias de transporte: mesma frase, chave que nao e prosa portuguesa.
    for frase, cod in INNESCO_CODIGO.items():
        if frase not in LABELS:
            raise SystemExit('meeting-labels.js nao conhece o innesco %r' % frase[:60])
        if cod in LABELS:
            raise SystemExit('o codigo de transporte %s ja existe no dicionario' % cod)
        LABELS[cod] = LABELS[frase]

    # ── FAIL-CLOSED: um codigo sem par IT+EN nao sai daqui ───────────────────
    # `return ''` e a fuga que este projecto ja conhece: um codigo sem frase
    # devolve vazio, a linha desaparece, e o ecra fica coerente a mentir por
    # omissao. Aqui um codigo desconhecido nao devolve nada — regista-se, e a
    # GERACAO FALHA antes de existir pacote.
    #
    #     UMA LINHA QUE SOME EM SILENCIO E PIOR DO QUE UM TOKEN A VISTA:
    #     O TOKEN VE-SE.
    usados = set()
    faltam = set()

    def C(cod):
        """Marca um codigo como usado e exige-lhe o par IT+EN."""
        if cod is None or cod == '':
            return None
        cod = str(cod)
        if cod not in LABELS:
            faltam.add(cod)
            return None
        usados.add(cod)
        return cod

    def Cs(lista):
        return [c for c in (C(x) for x in (lista or [])) if c]

    # ── TOP_3: so entra quem sobreviveu ao atacante ──────────────────────────
    # O veredito e do atacante, nao do autor. Um sensor que o autor declarou
    # executavel e o atacante derrubou entra como DERRUBADO, com o porque — e
    # nunca como sensor. Fabricar o terceiro para manter o nome "TOP_3" seria
    # inventar observabilidade que ninguem provou.
    # A especificacao completa de cada sensor tem milhares de caracteres de prosa
    # tecnica portuguesa. Ela e o artefacto operacional da equipa e continua
    # inteira a montante; o que atravessa para a tela italiana e a leitura curta,
    # escrita a proposito. Despejar a especificacao aqui poria prosa de
    # investigacao portuguesa diante do cliente — o defeito que audit/lang.mjs
    # existe para apanhar — e nao a tornaria mais legivel.
    SENSOR_IT = {
        'ITFC-016': {
            'TITULO': par(
                'Melo · antracnosi post-raccolta in Emilia-Romagna',
                'Apple · post-harvest anthracnose in Emilia-Romagna'),
            'VARIAVEL': par(
                'presenza o assenza di un\'indicazione di trattamento DOPO la raccolta '
                'delle varietà precoci contro glomerella / complesso Colletotrichum, '
                'nella sezione MELO dei bollettini interprovinciali.',
                'presence or absence of an indication to treat AFTER the harvest of early '
                'varieties against glomerella / the Colletotrichum complex, in the MELO '
                'section of the inter-provincial bulletins.'),
            'FONTE': par(
                'Servizio Fitosanitario Emilia-Romagna — bollettini interprovinciali di '
                'produzione integrata e biologica (API Plone, JSON, senza chiave).',
                'Servizio Fitosanitario Emilia-Romagna — inter-provincial bulletins for '
                'integrated and organic production (Plone API, JSON, no key).'),
            'CADENZA': par(
                'settimanale in stagione, da giugno alla fine della raccolta delle '
                'varietà tardive; mensile fuori stagione. Mai giornaliera.',
                'weekly in season, from June to the end of the late-variety harvest; '
                'monthly out of season. Never daily.'),
            'SCATTA': par(
                'quando un bollettino datato porta, nello stesso item di difesa della '
                'sezione MELO, un termine di posteriorità alla raccolta, il bersaglio '
                'e la sostanza — i tre insieme.',
                'when a dated bulletin carries, within the same defence item of the MELO '
                'section, a term of posteriority to the harvest, the target and the '
                'substance — the three together.'),
            'INVALIDA': par(
                'quando nel CRIS UNIBO compare un record datato che conclude che '
                'l\'inoculo rilevante sverna in gemme e borse fiorali.',
                'when a dated record appears in CRIS UNIBO concluding that the relevant '
                'inoculum overwinters in buds and flower bourses.'),
            'ADATTATORE': par(
                'tre pezzi: risolvere per anno il percorso della collezione Plone '
                '(la rotta provata finisce in «-2026»), filtrare la sezione MELO e '
                'leggere i PDF. La collezione 2027 non è ancora stata sondata.',
                'three pieces: resolve the Plone collection path per year (the proven route '
                'ends in «-2026»), filter the MELO section and read the PDFs. The 2027 '
                'collection has not been probed yet.'),
        },
        'ITFC-009': {
            'TITULO': par(
                'Vite · black rot ed escoriosi su varietà resistenti',
                'Grapevine · black rot and phomopsis on resistant varieties'),
            'CAIU_PORQUE': par(
                'la clausola che sembrava piu solida — i bollettini di tre regioni — '
                'non ha retto: il segnale isola il danno sul grappolo, e la fonte che '
                'lo dichiara una volta l\'anno non e un bollettino ma la sessione '
                'annuale di un convegno, con trascrizione da produrre.',
                'the clause that looked most solid — bulletins from three regions — did not '
                'hold: the signal isolates damage on the bunch, and the source that states it '
                'once a year is not a bulletin but the annual session of a conference, whose '
                'transcript still has to be produced.'),
        },
        'ITFC-018': {
            'TITULO': par(
                'Agrumi · dodina nelle linee tecniche siciliane',
                'Citrus · dodine in the Sicilian technical guidelines'),
            'CAIU_PORQUE': par(
                'quello che sembrava un innesco di cambiamento è, una volta reso '
                'osservabile, un innesco di conferma; e la fonte primaria — il '
                'Servizio Fitosanitario della Regione Siciliana — non ha scheda nel '
                'catalogo, quindi il suo accesso non è mai stato misurato. '
                'NON SO, non «non esiste».',
                'what looked like a trigger of change is, once made observable, a trigger of '
                'confirmation; and the primary source — the Servizio Fitosanitario of the '
                'Sicilian Region — has no record in the catalogue, so its access was never '
                'measured. UNKNOWN, not «it does not exist».'),
        },
    }

    sensores, derrubados = [], []
    for r in T3['ROWS']:
        sid = r['SIGNAL_ID']
        t = SENSOR_IT[sid]
        vivo = r['EXECUTABILITY'] == 'EXECUTAVEL_COM_ADAPTADOR'
        linha = {
            'ID': sid,
            'TITULO': t['TITULO'],
            'EXECUTABILITY': enum(r['EXECUTABILITY']),
            'EXECUTABILITY_TOKEN': r['EXECUTABILITY'],
            'DECLARADA_PELO_AUTOR': enum(r['EXECUTABILITY_DECLARADA_PELO_AUTOR']),
            'AUTORIDADE': enum(r['SOURCE_AUTHORITY']),
            'TRANSICAO': enum(r['STATE_TRANSITION']),
            'TRANSICAO_TOKEN': r['STATE_TRANSITION'],
            'TRANSICAO_AUTORIZADA': enum(T3['TRANSICAO_AUTORIZADA_PELA_REGUA'][sid]),
        }
        if vivo:
            linha.update({'VARIAVEL': t['VARIAVEL'], 'FONTE': t['FONTE'],
                          'CADENZA': t['CADENZA'], 'SCATTA': t['SCATTA'],
                          'INVALIDA': t['INVALIDA'], 'ADATTATORE': t['ADATTATORE']})
        else:
            linha['CAIU_PORQUE'] = t['CAIU_PORQUE']
        # O derrubado nao carrega campos de sensor: nao os tem, e inventar-lhe
        # um vazio faria dele um sensor por preencher em vez de um derrubado.
        (sensores if vivo else derrubados).append(linha)

    # ══ O REGISTO COMPLETO DOS 44 ITFC ══════════════════════════════════════
    # O TOP_3 e ENRIQUECIMENTO, nao universo. Levar so tres para o browser fazia
    # do destaque a coleccao inteira: quem abrisse o Radar Futuro via 3 de 44 e
    # nao tinha como saber que faltavam 41.
    #
    #     UM DESTAQUE QUE SUBSTITUI A COLECCAO NAO DESTACA: ESCONDE.
    #
    # O que atravessa e o vocabulario FECHADO do handoff — estado, accao, aviso,
    # classe de portfolio, e as CONTAGENS das lacunas. Os defeitos e os "ainda
    # nao sabemos" sao paragrafos de investigacao em portugues: contam-se, nunca
    # se citam. A especificacao inteira fica a montante, e a tela di-lo.
    # A EXECUTABILIDADE E DO SENSOR, NAO DO SINAL. Dois dos tres foram
    # derrubados como sensor e continuam entre os 44 mostraveis do radar. As
    # duas coisas viajam juntas onde o id aparece: separa-las deixaria ler
    # "derrubado" como se o SINAL tivesse caido — e nao caiu.
    SENSOR_ESTADO = {r['SIGNAL_ID']:
                     ('SENSOR_EXECUTABLE' if r['EXECUTABILITY'] == 'EXECUTAVEL_COM_ADAPTADOR'
                      else 'SENSOR_NOT_EXECUTABLE') for r in T3['ROWS']}
    excluidos = {(e['ID'] if isinstance(e, dict) else e) for e in (RF.get('EXCLUIDOS') or [])}
    limitado = set(RF.get('PORTFOLIO_LIMITED_IDS') or [])
    ledger = []
    for sid in RF['RENDERIZAVEIS']:
        if sid in excluidos:
            raise SystemExit('%s esta em RENDERIZAVEIS e em EXCLUIDOS' % sid)
        L = RF['LIMITACOES_POR_SINAL'][sid]
        pf = L.get('PORTFOLIO') or {}
        lac = L.get('LACUNAS') or {}
        pode = pf.get('O_CARTAO_PODE')
        if pode is not None and pode not in CARTAO_PODE:
            raise SystemExit('O_CARTAO_PODE sem codigo declarado: %r' % pode)
        ledger.append({
            'ID': sid,
            'ESTADO': C(L['ESTADO']),
            'ACAO': C(L['ACAO']),
            'AVISO': C(L.get('AVISO_OBRIGATORIO')),
            'PORTFOLIO_CLASSE': C(pf.get('CLASSE')),
            'PORTFOLIO_PAR_ADAMA': C(pf.get('ADAMA_PAIR_EXISTS')),
            'PORTFOLIO_ROTA': C('ITFC_ROUTE_ALLOWED' if pf.get('ROTA_VIVA_PERMITIDA')
                                else 'ITFC_ROUTE_FORBIDDEN'),
            'O_CARTAO_PODE': C(CARTAO_PODE[pode]) if pode else None,
            'PORTFOLIO_LIMITADO': sid in limitado,
            # CONTAGENS, nao citacoes: a prosa e portuguesa e fica a montante.
            'DEFEITOS': len(lac.get('DEFEITOS_ENCONTRADOS') or []),
            'NAO_SABEMOS': len(lac.get('C_NAO_SABEMOS') or []),
            'SENSOR': C(SENSOR_ESTADO.get(sid)),
        })
    ledger.sort(key=lambda r: r['ID'])
    if len(ledger) != RF['RENDERABLE']:
        raise SystemExit('o registo tem %d linhas, o handoff diz %d renderizaveis'
                         % (len(ledger), RF['RENDERABLE']))
    prep = sum(1 for r in ledger if r['ACAO'] == 'PREPARAR')
    moni = sum(1 for r in ledger if r['ACAO'] == 'MONITORAR')
    if prep != RF['PREPARE'] or moni != RF['WATCH']:
        raise SystemExit('o registo da %d preparar / %d monitorar; o handoff diz %d / %d'
                         % (prep, moni, RF['PREPARE'], RF['WATCH']))

    # ══ AS 43 OPORTUNIDADES ATUAIS ══════════════════════════════════════════
    # O 43 vem do dono e de mais lado nenhum. Escreve-lo aqui a mao faria dele
    # uma verdade independente — e uma verdade independente e a que nao muda
    # quando o motor mudar.
    #
    #     HARDCODE 43 NAO PASSA. O NUMERO E DERIVADO OU NAO E.
    casos_crus = MI['CASES']
    total = MI['TOTAL_CASES']
    if total != len(casos_crus):
        raise SystemExit('o snapshot diz TOTAL_CASES=%s e traz %d casos' % (total, len(casos_crus)))

    def caso(c):
        estado_cliente = CLIENT_STATE.get(c['COMMERCIAL_PRIORITY'])
        # Os que o motor NAO sustenta como oportunidade comercial nao ficam sem
        # nome: chamam-se pelo que sao. Escondê-los seria perde-los.
        estado = C(estado_cliente or 'CLIENT_TO_VALIDATE')
        cooling = []
        if c.get('NEED_DIRECTION') in ARREFECEM_DIRECAO:
            cooling.append(c['NEED_DIRECTION'])
        if c.get('ACTION_RECOMMENDATION_STATE') in ARREFECEM_RECOMENDACAO:
            cooling.append(c['ACTION_RECOMMENDATION_STATE'])

        accoes = []
        por_reparto = c.get('ACTION_BY_DEPARTMENT') or {}
        for d in DEPT_ORDER:
            a = por_reparto.get(d)
            if not a:
                continue
            accoes.append({
                'REPARTO': C(d),
                'STATO': C(a.get('ACTION_STATE')),
                'AZIONE': C(a.get('ACTION')),
                'PERCHE': C(a.get('WHY_CODE')),
                'DIPENDE_DA': C(a.get('DEPENDENCY')),
                # NEXT_TRIGGER chega como frase portuguesa. Viaja por codigo:
                # a frase italiana e a inglesa sao as do dicionario, intactas.
                'INNESCO': C(INNESCO_CODIGO[a['NEXT_TRIGGER']]) if a.get('NEXT_TRIGGER') else None,
                # A JANELA so onde o motor a declara. Onde nao ha, diz-se.
                'FINESTRA': C(JANELA_DA_ACAO.get(a.get('ACTION_STATE'))),
                'EVIDENZA': list(a.get('EVIDENCE') or []),
            })

        cadeia = c.get('WHY_NOW_CHAIN') or {}
        elos = []
        for k in CHAIN:
            e = cadeia.get(k)
            if not e:
                continue
            facto = e.get('FACT')
            e_data = isinstance(facto, str) and bool(re.match(r'^\d{4}-\d{2}-\d{2}', facto))
            e_cod = isinstance(facto, str) and bool(re.match(r'^[A-Z0-9_]+$', facto))
            elos.append({
                'ELO': C(k), 'OK': bool(e.get('OK')),
                'FATTO_DATA': facto if e_data else None,
                'FATTO_CODICE': C(facto) if (e_cod and not e_data) else None,
                'EVIDENZA': list(e.get('EVIDENCE') or []),
            })

        prodotti = []
        for m in (c.get('PORTFOLIO_MATCHES') or []):
            prodotti.append({
                'ID': m.get('PRODUCT_ID'),
                'NOME': m.get('PRODUCT_NAME'),
                'REGISTRO': m.get('REGISTRATION_NUMBER'),
                'ATTIVI': list(m.get('ACTIVE_INGREDIENTS') or []),
                'MOA': list(m.get('MODE_OF_ACTION') or []),
                'VALIDAZIONE': C(m.get('VALIDATION_STATE')),
                'FINESTRA_FIT': C(m.get('WINDOW_FIT')),
                'RESTRIZIONI': [{'CODICE': C(r.get('CODE')), 'ATTIVO': r.get('ACTIVE_INGREDIENT'),
                                 'DATA': r.get('DATE')} for r in (m.get('RESTRICTIONS') or [])],
            })
        nomeado = c.get('PRIMARY_MATCH')
        principale = nomeado if any(p['ID'] == nomeado for p in prodotti) else None

        evidenze = [{'ID': e.get('EVIDENCE_ID'), 'FAMIGLIA': C(e.get('ENTITY_TYPE')),
                     'RUOLO': C(e.get('ROLE')), 'PERCHE': C(e.get('WHY_CODE'))}
                    for e in (c.get('EVIDENCE_ROLES') or [])]

        # ── A LEI DE RELEVANCIA, LIDA DO SEU DONO ────────────────────────
        classe, porque = classificar(c)
        minhas, outras = restricoes_separadas(c)
        prova = None
        if classe == 'A':
            from adama_relevance import produto_que_prova
            m = produto_que_prova(c)
            prova = {'PRODOTTO': m.get('PRODUCT_NAME'), 'ID': m.get('PRODUCT_ID'),
                     'REGISTRO': m.get('REGISTRATION_NUMBER'),
                     'ATTIVI': list(m.get('ACTIVE_INGREDIENTS') or []),
                     'CULTURA': C(m.get('CROP_FIT')), 'BERSAGLIO': C(m.get('TARGET_FIT')),
                     'AUTORIZZAZIONE': C(m.get('REGULATORY_FIT'))}

        why = {lg: sem_ponteiro(c.get('WHY_COMMERCIAL_' + lg.upper()) or '') for lg in ('it', 'en')}
        colt, alvo = C(c.get('CROP')), C(c.get('TARGET'))
        return {
            # ── L1 · o que se ve sem clicar ──────────────────────────────
            'ID': c['ID'],
            'COLTURA': colt, 'BERSAGLIO': alvo, 'GEOGRAFIA': C(c.get('GEOGRAPHY')),
            # Um caso em 43 nao tem coltura nem bersaglio: e uma data
            # regolatoria europeia, e a ausencia do alvo e um FACTO que o motor
            # declara. O titulo cai entao no ARQUETIPO — a unica coisa
            # verdadeira que se lhe pode intestar.
            'TITOLO_DA_ARCHETIPO': not (colt or alvo),
            'ARCHETIPO': C(c.get('ARCHETYPE')),
            'AMBITO': C(c.get('GEOGRAPHIC_SCOPE')),
            'STATO_CLIENTE': estado,
            # ── A LEI DE RELEVANCIA ADAMA ────────────────────────────────
            # A classe decide em que superficie o caso pode aparecer. Nada
            # desaparece: muda o nome por que e chamado.
            'RILEVANZA': classe,
            'RILEVANZA_PERCHE': C(porque),
            'RILEVANZA_SUPERFICIE': SUPERFICIE[classe],
            'PROVA_ADAMA': prova,
            'PRIORITA': C(c.get('COMMERCIAL_PRIORITY')),
            'PUBBLICAZIONE': C(c.get('PUBLICATION_STATE')),
            'E_OPPORTUNITA_COMMERCIALE': bool(estado_cliente),
            # ── L2 · gestione ────────────────────────────────────────────
            'PERCHE': {'it': why['it']['text'], 'en': why['en']['text']},
            'PERCHE_SOLO_CODICI': not (why['it']['text'] and why['en']['text']),
            'PERCHE_CODICI': Cs(c.get('WHY_COMMERCIAL_CODES')),
            'FINESTRA': {
                'DEFINITA': C('YES' if c.get('WINDOW_DEFINED') == 'YES' else 'NO'),
                'DEFINITA_TOKEN': c.get('WINDOW_DEFINED'),
                'APERTA_ORA': c.get('WINDOW_OPEN_NOW') or 'UNKNOWN',
                'TIPO': C(c.get('WINDOW_TYPE')),
                'REGOLA': C(c.get('WINDOW_RULE_STATE')),
                'METODO': C(c.get('WINDOW_OPEN_NOW_METHOD')),
                # A condicao e prosa de investigacao portuguesa. Atravessa o
                # DOCUMENTO que a contem — que e verdade — nunca o texto.
                'DOCUMENTO_CONDIZIONE': c.get('WINDOW_EVIDENCE_ID'),
                'DOCUMENTO_REGOLA': c.get('WINDOW_RULE_EVIDENCE_ID'),
                'CONDIZIONE_TRATTENUTA': bool(c.get('WINDOW_CONDITION__PT_ONLY')),
                'INIZIO': c.get('WINDOW_START'), 'FINE': c.get('WINDOW_END'),
                'GIORNI_RIMASTI': c.get('DAYS_REMAINING'),
            },
            'CATENA': elos,
            'CATENA_COMPLETA': 'CADEIA_COMPLETA' in (c.get('WHY_NOW_CODES') or []),
            'CATENA_CODICI': Cs(c.get('WHY_NOW_CODES')),
            'AZIONI': accoes,
            'INVALIDA': Cs(cooling),
            'DIREZIONE': C(c.get('NEED_DIRECTION')),
            'DIREZIONE_DOCUMENTO': c.get('NEED_EVIDENCE_ID'),
            'ESTRATTO_TRATTENUTO': bool(c.get('NEED_EXCERPT__PT_ONLY')),
            'STADIO': C(c.get('PEST_STAGE_STATE')),
            'RACCOMANDAZIONE': C(c.get('ACTION_RECOMMENDATION_STATE')),
            'SOGLIA': C(c.get('THRESHOLD_STATE')),
            'PRODOTTI': prodotti,
            'PRODOTTO_PRINCIPALE': principale,
            'PERCHE_NESSUN_PRINCIPALE': C(c.get('PRIMARY_MATCH_REASON')) if not principale else None,
            # ── L3 · evidenza ────────────────────────────────────────────
            # ── DUAS LISTAS, E NUNCA UMA ─────────────────────────────────
            # 40 das 114 restricoes citam um activo que NAO esta em nenhum
            # produto ADAMA ligado ao caso: vem do superset que inclui os
            # activos nomeados pelas fontes e pela concorrencia. Mostrar a
            # expiracao do activo do concorrente como se fosse a nossa nao e
            # um erro de etiqueta — e uma decisao comercial ao contrario.
            'RESTRIZIONI_ADAMA': [{'CODICE': C(r.get('CODE')), 'ATTIVO': r.get('ACTIVE_INGREDIENT'),
                                   'DATA': r.get('DATE')} for r in minhas],
            'RESTRIZIONI_ALTRO_ATTIVO': [{'CODICE': C(r.get('CODE')), 'ATTIVO': r.get('ACTIVE_INGREDIENT'),
                                          'DATA': r.get('DATE')} for r in outras],
            'FONTI_URL': list(c.get('SOURCE_URLS') or []),
            'FONTI_CHIAVI': len(c.get('SOURCE_IDS') or []),
            'METODO_NECESSITA': C(c.get('NEED_METHOD')),
            'LIMITI': Cs(c.get('WHAT_IS_MISSING')),
            'EVIDENZE': evidenze,
            'EVIDENZE_TOTALE': c.get('EVIDENCE_COUNT') or 0,
            'FAMIGLIE': Cs(c.get('EVIDENCE_FAMILIES')),
            'CONFIDENZA': C(c.get('CONFIDENCE')),
            'ATTUALITA': C(c.get('SIGNAL_CURRENCY')),
            'DATA_SEGNALE': c.get('SIGNAL_DATE'),
            'DATA_RIFERIMENTO': c.get('REFERENCE_DATE'),
            'PROVA': {'it': c.get('WHAT_IT_PROVES_IT') or '', 'en': c.get('WHAT_IT_PROVES_EN') or ''},
            'NON_PROVA': {'it': c.get('WHAT_IT_DOES_NOT_PROVE_IT') or '',
                          'en': c.get('WHAT_IT_DOES_NOT_PROVE_EN') or ''},
            'NON_PROVA_COMMERCIALE': {'it': c.get('COMMERCIAL_DOES_NOT_PROVE_IT') or '',
                                      'en': c.get('COMMERCIAL_DOES_NOT_PROVE_EN') or ''},
        }

    ordem = {'CLIENT_ACT_NOW': 0, 'CLIENT_PREPARE_NOW': 1, 'CLIENT_MONITOR': 2,
             'CLIENT_TO_VALIDATE': 3}
    casos = [caso(c) for c in casos_crus]
    casos.sort(key=lambda x: (ordem[x['STATO_CLIENTE']], x['ID']))

    commerciali = sum(1 for x in casos if x['E_OPPORTUNITA_COMMERCIALE'])
    da_validare = sum(1 for x in casos if not x['E_OPPORTUNITA_COMMERCIALE'])
    # ── A POPULACAO SEGUNDO A LEI DE RELEVANCIA ──────────────────────────────
    # 43 continuam a existir. O que muda e onde cada um pode aparecer.
    por_classe = contar(casos_crus)
    per_superficie = {}
    for x in casos:
        per_superficie[x['RILEVANZA_SUPERFICIE']] = per_superficie.get(x['RILEVANZA_SUPERFICIE'], 0) + 1
    if sum(por_classe.values()) != total:
        raise SystemExit('a lei de relevancia perdeu casos: %s de %d' % (por_classe, total))
    if commerciali + da_validare != total:
        raise SystemExit('%d + %d nao fecha em %d' % (commerciali, da_validare, total))
    por_stato = {}
    for x in casos:
        por_stato[x['STATO_CLIENTE']] = por_stato.get(x['STATO_CLIENTE'], 0) + 1

    a01 = HS['ACHADOS']['01_AZOXISTROBINA_PROTIOCONAZOL']
    a02 = HS['ACHADOS']['02_AUTORIZACOES_ADAMA']
    a03 = HS['ACHADOS']['03_REVOGADO_X_SCADUTO']
    a06 = HS['ACHADOS']['06_COBERTURA_TERRITORIAL']

    casa = {
        'GERADO_POR': 'scripts/it_casa_dados.py',
        'DETERMINISTICO': 'SIM — sem relogio, sem aleatorio, chaves ordenadas',
        'DATA_DE_REFERENCIA': a03['DATA_DE_REFERENCIA_DO_FUTURO'],
        'HASHES_CONSUMIDOS': {
            'IT-FUTURO-HANDOFF-LINHA-B-V1.json': h_rf,
            'IT-HANDOFF-LINHA-B-FITOSSANITARIO-V1.json': h_fi,
            'IT-HANDOFF-LINHA-B-FONTES-V1.json': h_fo,
            'IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json': h_sc,
            'IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json': h_hs,
            'IT-TOP3-SENSORES-V1.json': h_t3,
        },
        # Os donos que nao sao handoff de upstream carimbam-se a parte: sao
        # outra camada, com outro dono, e obriga-los ao carimbo dos seis
        # esconderia de onde vem cada coisa.
        'DONOS_DA_APRESENTACAO': {
            'meeting-intelligence-snapshot.json': h_mi,
            'meeting-labels.js': h_lab,
        },

        # ── AS TRES SUPERFICIES DE NUMERO, E POR QUE NAO SE SOMAM ────────────
        'OPPORTUNITA_ATTUALI': {
            'TOTALE': total,
            'PRIORITA_COMMERCIALE': commerciali,
            'DA_VALIDARE': da_validare,
            'PER_STATO': por_stato,
            # A lei nao apaga: os 43 continuam todos, distribuidos por superficie.
            'RILEVANZA_PER_CLASSE': por_classe,
            'RILEVANZA_PER_SUPERFICIE': per_superficie,
            'OPPORTUNITA': per_superficie.get('OPPORTUNITA', 0),
            'RADAR': per_superficie.get('RADAR', 0),
            'SEGNALI': per_superficie.get('SEGNALI', 0),
            'ERRORE': per_superficie.get('ERRORE', 0),
            'LEGGE_ADAMA': LEI_ADAMA,
            'SOURCE_HEAD': MI['SOURCE_HEAD'],
            'BUILD_ID': MI['BUILD_ID'],
            'MEETING_CUTOFF': MI['MEETING_CUTOFF'],
            'RULE_VERSION': MI['RULE_VERSION'],
            'ORIZZONTE': 'ADESSO',
            'CASI': casos,
        },
        'RADAR_FUTURO': {
            'PREPARAR': RF['PREPARE'],
            'MONITORAR': RF['WATCH'],
            'AGIR_AGORA': RF['ACT_NOW'],
            'RENDERIZAVEIS': RF['RENDERABLE'],
            'TOTAL': RF['TOTAL'],
            'DERRUBADOS': RF['DROPPED'],
            'PORTFOLIO_LIMITED': RF['PORTFOLIO_LIMITED'],
            'ORIZZONTE': 'PROSSIMA_CAMPAGNA',
            'LIMITE': par(
                'nessuno di questi è un\'opportunità di oggi: AGIRE ORA è zero '
                'per decisione della riga, non per mancanza di lettura',
                'none of these is an opportunity for today: ACT NOW is zero by decision of '
                'the rule, not for want of reading'),
            'REGISTRO': ledger,
        },
        'SINAIS_DE_CAMPO': {
            'VISIVEIS': SC['RENDERABLE_CARD'] + SC['RENDERABLE_WITH_METHOD'],
            'CARTAO': SC['RENDERABLE_CARD'],
            'COM_METODO': SC['RENDERABLE_WITH_METHOD'],
            'LIMITE': par(
                'le letture CON METODO viaggiano sempre con il modo in cui sono state lette',
                'readings WITH METHOD always travel with the way they were read'),
        },
        'FONTES': {
            'COM_METODO': FO['RENDERABLE_WITH_METHOD'],
            'LIMITE': it(a06['O_QUE_O_MAPA_NUNCA_RESPONDE']),
            'LIMITE_PT': a06['O_QUE_O_MAPA_NUNCA_RESPONDE'],
            'RESPONDE': it(a06['O_QUE_O_MAPA_RESPONDE']),
            'RESPONDE_PT': a06['O_QUE_O_MAPA_RESPONDE'],
        },
        'COBERTURA': {
            'CELULAS': a06['CELULAS'],
            'COM_EXPANSAO_GOOD': a06['COM_EXPANSAO_TERRITORIAL']['GOOD'],
            'SEM_EXPANSAO_GOOD': a06['SEM_EXPANSAO_TERRITORIAL']['GOOD'],
            'A_EXPANSAO_E': it(a06['A_EXPANSAO_E']),
            'A_EXPANSAO_E_PT': a06['A_EXPANSAO_E'],
        },
        'EVIDENCIA': {
            'FITOSSANITARIO': FI['EVIDENCE_ONLY'],
            'LEI': FI['LEI_DA_FAMILIA'],
            'NUNCA_E_GRELHA': par(
                'raggiungibile dalla scheda che lo cita, mai come scheda propria',
                'reachable from the card that cites it, never as a card of its own'),
        },

        # ── o destaque ───────────────────────────────────────────────────────
        'DESTAQUE': {
            'TITULO': 'AZOXYSTROBIN + PROTHIOCONAZOLE',
            'FATO': it(a01['FATO']),
            'FATO_PT': a01['FATO'],
            'UNIVERSO': a01['UNIVERSO'],
            # PASSAVA CRU E CHEGAVA 'SIM' A UMA TELA ITALIANA. A traducao ja
            # existia em ENUM_IT ('SIM' -> 'si'); faltava a chamada. Um valor
            # de uma palavra e o que mais facilmente escapa a revisao: ninguem o
            # le como prosa. `enum()` e fail-closed e recusa o token que nao conhece.
            'E_UNIVERSO_FECHADO': enum(a01['E_UNIVERSO_FECHADO_NAO_AMOSTRA']),
            'CRITERIO': it(a01['CRITERIO_DO_FILTRO']),
            'CRITERIO_PT': a01['CRITERIO_DO_FILTRO'],
            'INTERPRETACAO': it(a01['INTERPRETACAO']),
            'INTERPRETACAO_PT': a01['INTERPRETACAO'],
            'DELTA_MESES': a01['DELTA_JANELA_MESES_APROX'],
            'ADAMA_ATE': '31/05/2027',
            'CONCORRENTE_ATE': '31/03/2028',
            'ITENS': a01['ITENS'],
            'FONTE': a01['FONTE_OFICIAL'],
            'TRAVA_DE_INDEPENDENCIA': it(a01['TRAVA_DE_INDEPENDENCIA']),
            'TRAVA_DE_INDEPENDENCIA_PT': a01['TRAVA_DE_INDEPENDENCIA'],
            'ACTIVATION_QUESTION': par(
                'Portafoglio e Sviluppo Mercato: il rinnovo del 31/05/2027 è già in corso, '
                'e lo scarto di finestra conta commercialmente?',
                'Portfolio and Market Development: is the 31/05/2027 renewal already under '
                'way, and does the window gap count commercially?'),
            'QUEM_DECIDE': it(a01['ACAO_QUE_SO_A_ADAMA_DECIDE']),
            'QUEM_DECIDE_PT': a01['ACAO_QUE_SO_A_ADAMA_DECIDE'],
            'DATA_DO_SNAPSHOT': a02['DATA_DO_SNAPSHOT'],
        },

        # ── com metodo: numero nenhum viaja sozinho ──────────────────────────
        'AUTORIZACOES': {
            'AMPLIADO_CINCO_RAZOES': a02['MATRIZ_CRITERIO_X_RECORTE']['AMPLIADO|ADAMA_CINCO_RAZOES_SOCIAIS']['VIGENTES_COM_VENCIMENTO_FUTURO'],
            'STRICT_CINCO_RAZOES': a02['MATRIZ_CRITERIO_X_RECORTE']['STRICT|ADAMA_CINCO_RAZOES_SOCIAIS']['VIGENTES_COM_VENCIMENTO_FUTURO'],
            'CRITERIO_AMPLIADO': it(a02['CRITERIOS']['AMPLIADO']),
            'CRITERIO_STRICT': it(a02['CRITERIOS']['STRICT']),
            'DATA_DO_SNAPSHOT': a02['DATA_DO_SNAPSHOT'],
            'AGRUPAR_AS_CINCO_E': it(a02['AGRUPAR_AS_CINCO_E']),
            'LIMITE': par(
                'conteggio di registri, e nient\'altro. Non è quota di mercato.',
                'a count of registrations, and nothing else. It is not market share.'),
            'SEM_DONO': it(a02['ESTADOS_SEM_DONO']['REGRA']),
        },
        'REVOGADO_X_SCADUTO': {
            'REVOCATO': a03['REVOCATO'],
            'SCADUTO': a03['SCADUTO'],
            'REVOCATO_COM_VENCIMENTO_FUTURO': a03['REVOCATO_COM_VENCIMENTO_AINDA_FUTURO'],
            'DEMONSTRACAO': it(a03['DEMONSTRACAO']),
            'DEMONSTRACAO_PT': a03['DEMONSTRACAO'],
            'LIMITE': it(a03['LIMITE']),
            'LIMITE_PT': a03['LIMITE'],
        },

        'SENSORES': {
            'SOBREVIVERAM': sensores,
            'DERRUBADOS': derrubados,
            'REGRA': par(
                'si mostra solo ciò che ha retto all\'attacco. Gli abbattuti compaiono '
                'come abbattuti, con il perché — mai come sensore.',
                'only what held under attack is shown. The ones knocked down appear as '
                'knocked down, with the reason — never as a sensor.'),
            'NADA_FOI_REJULGADO': T3['NADA_FOI_REJULGADO'],
        },

        'DO_NOT_SHOW': HS['DO_NOT_SHOW'],
        'LIMITACOES_DA_CAMADA_HUMANA': HS['LIMITATIONS'],
        'NAO_ENTRA_NA_CASA': {
            '05_PESSOAS_E_PAPEIS': ('P-012 (GDPR) esta aberta: a camada nomeia pessoas com '
                                    'afiliacao e ORCID. Nao entra em tela nenhuma antes de revisao.'),
            '04_SOCIAL_YOUTUBE': 'METHOD_ONLY no proprio handoff. Nao e destaque de HOME.',
            'RECENCIA_TERRITORIAL': ('a camada territorial foi produzida com a leitura de data '
                                     'defeituosa do achado 07. Mostra-se cobertura, nunca recencia.'),
        },
    }

    # ── A CORNICE DA TELA, TAMBEM EM PAR ────────────────────────────────────
    # Os titulos de seccao e as perguntas sao MOLDURA nossa. Vem do mesmo dono
    # das outras frases, e passam pelo mesmo fail-closed.
    for k in ('casaTitle', 'casaLede', 'casaL1', 'casaL2', 'casaL3', 'casaL1Sub',
              'casaL2Sub', 'casaL3Sub', 'casaCurrentOpps', 'casaCommercialPriority',
              'casaToValidate', 'casaSplitExplained', 'casaRadarName', 'casaRadarPrepare',
              'casaRadarMonitor', 'casaRadarActNow', 'casaDoNotSum', 'casaRadarLedger',
              'casaRadarTotals', 'casaFieldName', 'casaSourcesName', 'casaEvidenceLayer',
              'casaSecWhy', 'casaSecWindow', 'casaSecChain', 'casaSecWhoActs',
              'casaSecTrigger', 'casaSecInvalidates', 'casaSecState', 'casaSecSource',
              'casaSecMethod', 'casaSecLimits', 'casaSecProvenance', 'casaSecEvidence',
              'casaSecRefutation', 'casaSecCannotSay', 'casaOpenL2', 'casaOpenL3',
              'casaNoneDeclared', 'casaNoWindowStated', 'casaEngineDecides',
              'casaSpecUpstream', 'casaGapsDeclared', 'casaUnknownsDeclared',
              'casaDropped', 'casaEvidenceOnlyRule', 'casaOf', 'casaShowAll',
              'casaFilterAll', 'casaSensorLegend', 'navMeeting', 'navSignals', 'lblCases',
              'RELEVANCE_A_PROVEN', 'RELEVANCE_B_NO_TARGET', 'RELEVANCE_B_NAMED_ASSET_NO_RISK',
              'RELEVANCE_C_NO_LINK', 'RELEVANCE_D_LINK_FAILS', 'RELEVANCE_E_UNKNOWN',
              'surfOPPORTUNITA', 'surfRADAR', 'surfSEGNALI', 'surfERRORE',
              'casaProvaAdama', 'casaRestrAdama', 'casaRestrAltro', 'casaLeggeAdama',
              'DECLARED_ON_CATALOG_PAGE', 'ON_MINISTERIAL_LABEL', 'AUTHORIZATION_LIVE',
              'casaKeyType', 'casaKeyRule', 'casaKeyDocument', 'casaKeyStart', 'casaKeyEnd',
              'casaKeyWindow', 'casaKeyNeed', 'casaKeyPortfolio', 'casaKeyDate',
              'casaKeyCurrency', 'casaKeyConfidence', 'casaKeyDirection', 'casaKeyStage',
              'casaKeyRecommend', 'casaKeyThreshold', 'casaKeyPublication', 'casaDependsOn',
              'casaColState', 'casaColAction', 'casaColPortfolio', 'casaColGaps',
              'secProducts', 'secEvidence', 'secActionMap',
              'CLIENT_ACT_NOW_WHY', 'CLIENT_PREPARE_NOW_WHY', 'CLIENT_MONITOR_WHY',
              'CLIENT_TO_VALIDATE_WHY', 'lblRule', 'lblStateNow',
              'windowDefinedYes', 'windowDefinedNo', 'windowOpenYes', 'windowOpenNo',
              'windowOpenUnknown', 'windowOpenNoRule', 'lblChainOk', 'lblChainBroken',
              'lblNoPrimary', 'lblAllProducts', 'lblNoProducts'):
        C(k)
    # WINDOW_OPEN_NOW viaja como token qualificado para que uma palavra inglesa
    # solta (UNKNOWN) nunca chegue ao ecra como palavra.
    for t in ('YES', 'NO', 'UNKNOWN'):
        C(t)

    # ── FAIL-CLOSED, SEGUNDA METADE: A MOLDURA TAMBEM VIAJA EM PAR ──────────
    # O fail-closed dos CODIGOS ja fecha o vocabulario. Mas as frases que
    # escrevemos nos — limites, criterios, perguntas — nao sao codigos, e foi
    # exactamente por ai que o ingles apanhou italiano. Estes caminhos sao os
    # que a tela desenha como prosa nossa, e todos tem de trazer o par.
    PARES_OBRIGATORIOS = [
        ('RADAR_FUTURO', 'LIMITE'), ('SINAIS_DE_CAMPO', 'LIMITE'),
        ('FONTES', 'LIMITE'), ('FONTES', 'RESPONDE'),
        ('COBERTURA', 'A_EXPANSAO_E'), ('EVIDENCIA', 'NUNCA_E_GRELHA'),
        ('DESTAQUE', 'FATO'), ('DESTAQUE', 'CRITERIO'), ('DESTAQUE', 'INTERPRETACAO'),
        ('DESTAQUE', 'TRAVA_DE_INDEPENDENCIA'), ('DESTAQUE', 'QUEM_DECIDE'),
        ('DESTAQUE', 'ACTIVATION_QUESTION'),
        ('AUTORIZACOES', 'CRITERIO_AMPLIADO'), ('AUTORIZACOES', 'CRITERIO_STRICT'),
        ('AUTORIZACOES', 'AGRUPAR_AS_CINCO_E'), ('AUTORIZACOES', 'LIMITE'),
        ('AUTORIZACOES', 'SEM_DONO'),
        ('REVOGADO_X_SCADUTO', 'DEMONSTRACAO'), ('REVOGADO_X_SCADUTO', 'LIMITE'),
        ('SENSORES', 'REGRA'),
    ]
    meias = []
    for a, bkey in PARES_OBRIGATORIOS:
        v = casa[a][bkey]
        if not isinstance(v, dict) or not v.get('it') or not v.get('en'):
            meias.append('%s.%s' % (a, bkey))
    for grupo in ('SOBREVIVERAM', 'DERRUBADOS'):
        for linha in casa['SENSORES'][grupo]:
            for k in ('TITULO', 'VARIAVEL', 'FONTE', 'CADENZA', 'SCATTA', 'INVALIDA',
                      'ADATTATORE', 'CAIU_PORQUE'):
                if k not in linha:
                    continue
                v = linha[k]
                if not isinstance(v, dict) or not v.get('it') or not v.get('en'):
                    meias.append('SENSORES.%s[%s].%s' % (grupo, linha['ID'], k))
    if meias:
        raise SystemExit(
            'GERACAO FALHOU — %d frase(s) da moldura chegam ao browser sem par IT+EN:\n  %s'
            % (len(meias), '\n  '.join(meias)))

    if faltam:
        raise SystemExit(
            'GERACAO FALHOU — %d codigo(s) chegam ao browser sem par IT+EN em '
            'meeting-labels.js:\n  %s\n'
            'Um codigo sem frase faz a linha desaparecer em silencio. '
            'Acrescente o par e volte a correr.'
            % (len(faltam), '\n  '.join(sorted(faltam))))

    casa['LABELS'] = {k: LABELS[k] for k in sorted(usados)}
    casa['LABELS_FAIL_CLOSED'] = {
        'DONO': 'italia-portale/client/meeting-labels.js',
        'CODIGOS_NO_PACOTE': len(usados),
        'REGRA': ('nenhum codigo sai daqui sem par IT+EN. Nao ha fallback para o '
                  'codigo cru, nao ha string vazia, e nenhuma linha desaparece em '
                  'silencio: sem par, a GERACAO falha.'),
    }

    # ── O VEREDITO IMPRESSO, PARA QUEM NAO PODE RECALCULAR ──────────────────
    # `meeting-surface.js` particiona a populacao por este ficheiro e NUNCA
    # reavalia a lei. O avaliador e um; o resto transporta.
    vereditos = {x['ID']: {'CLASSE': x['RILEVANZA'], 'SUPERFICIE': x['RILEVANZA_SUPERFICIE'],
                           'PERCHE': x['RILEVANZA_PERCHE'],
                           'PROVA': (x['PROVA_ADAMA'] or {}).get('PRODOTTO')}
                 for x in casos}
    rel = {'GERADO_POR': 'scripts/it_casa_dados.py + scripts/adama_relevance.py',
           'DONO_DA_LEI': 'scripts/adama_relevance.py',
           'LEGGE': LEI_ADAMA, 'TOTALE': total,
           'PER_CLASSE': por_classe, 'PER_SUPERFICIE': per_superficie,
           'SOURCE_HEAD': MI['SOURCE_HEAD'], 'BUILD_ID': MI['BUILD_ID'],
           'VERDETTI': vereditos}
    js_rel = ('/* GERADO por scripts/it_casa_dados.py — nao editar a mao.\n'
              '   A LEI vive em scripts/adama_relevance.py e decide-se LA. Este ficheiro\n'
              '   transporta o veredito para o browser, que nunca o recalcula. */\n'
              'window.ADAMA_RELEVANCE = '
              + json.dumps(rel, ensure_ascii=False, indent=1, sort_keys=True) + ';\n')
    with io.open(OUT_REL, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js_rel)

    corpo = json.dumps(casa, ensure_ascii=False, indent=1, sort_keys=True)
    js = ('/* GERADO por scripts/it_casa_dados.py — nao editar a mao.\n'
          '   Os numeros vem dos donos ja julgados; aqui nao se reconta nada.\n'
          '   As frases IT/EN vem de meeting-labels.js, que continua a ser o unico\n'
          '   dono de labels: este pacote transporta-as, nao as escreve. */\n'
          'window.ITALY_CASA = ' + corpo + ';\n')
    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('  escrito : %s' % os.path.relpath(OUT, ROOT))
    print('  sha256  : %s' % hashlib.sha256(js.encode('utf-8')).hexdigest())
    print('  escrito : %s' % os.path.relpath(OUT_REL, ROOT))
    print('  OPPORTUNITA ATTUALI %d = %d priorita commerciali + %d da validare'
          % (total, commerciali, da_validare))
    print('  LEI ADAMA · A=%d B=%d C=%d D=%d E=%d  ->  OPPORTUNITA %d · RADAR %d · SEGNALI %d · ERRORE %d'
          % (por_classe['A'], por_classe['B'], por_classe['C'], por_classe['D'], por_classe['E'],
             per_superficie.get('OPPORTUNITA', 0), per_superficie.get('RADAR', 0),
             per_superficie.get('SEGNALI', 0), per_superficie.get('ERRORE', 0)))
    print('  RADAR FUTURO %d totali · %d mostrabili · %d abbattuto · %d preparare · %d monitorare · %d agire ora'
          % (RF['TOTAL'], RF['RENDERABLE'], RF['DROPPED'], prep, moni, RF['ACT_NOW']))
    print('  CAMPO %d · FONTI %d · FITO %d evidence-only'
          % (casa['SINAIS_DE_CAMPO']['VISIVEIS'], casa['FONTES']['COM_METODO'],
             casa['EVIDENCIA']['FITOSSANITARIO']))
    print('  sensores sobreviventes %d · derrubados %d' % (len(sensores), len(derrubados)))
    print('  labels IT+EN no pacote: %d (fail-closed, 0 em falta)' % len(usados))


if __name__ == '__main__':
    main()
