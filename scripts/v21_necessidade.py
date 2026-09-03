#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A NECESSIDADE DECLARADA · o par observado e a direção do texto.

    python3 scripts/v21_necessidade.py          # inspeção: mede, não grava

O QUE ESTE ARQUIVO CONSERTA
---------------------------
Dois defeitos medidos na auditoria da régua comercial.

**1 · O par cultura × alvo era cartesiano.** O boletim traz uma lista plana de
culturas e uma lista plana de alvos, e o motor cruzava as duas. Um boletim que
cobre dez culturas e normaliza um alvo produzia dez pares. Daí saíram
*beterraba × ticchiolatura* e *soja × ticchiolatura*, 13 vezes cada — pares que
a agronomia não admite e que nenhuma frase do documento sustenta.

    LISTA DE CULTURAS × LISTA DE ALVOS NÃO É OBSERVAÇÃO: É PRODUTO CARTESIANO.
    O PAR EXISTE ONDE A FONTE O ESCREVEU JUNTO.

**2 · A direção do texto não era lida.** O motor detectava que a praga aparece;
não distinguia «intervir» de «non necessari interventi», de «pode ser suspensa»,
de «pode considerar-se concluída» ou de «vigora a proibição». Os quatro casos de
score máximo do motor apoiavam-se em documentos que mandam PARAR.

    O MOTOR LIA QUE A PRAGA APARECE. ELE NÃO LIA SE O TEXTO MANDA AGIR.

**3 · A direção era repartida entre os alvos da mesma oração.** Medido depois,
em `IT-PHEN-041`: uma oração corrida nomeia três alvos e traz uma palavra de
direção, e os três recebiam a mesma. Ver a lei em `MULTIPLE_TARGETS_IN_CLAUSE`,
mais abaixo.

    UMA DIREÇÃO NÃO SE REPARTE. SE NÃO SE SABE DE QUEM ELA É, NÃO SE SABE.

COMO O PAR É FORMADO — e o que é recusado
------------------------------------------
O texto do boletim é partido em orações. Numa oração:

    cultura nomeada + alvo nomeado           → PAIR_IN_SAME_CLAUSE
    o TÍTULO nomeia os dois                  → PAIR_IN_DOCUMENT_TITLE
    só o alvo, cultura na oração anterior    → CROP_FROM_PRECEDING_CLAUSE
    só o alvo, e o documento tem UMA cultura → CROP_FROM_SINGLE_CROP_DOCUMENT
    só o alvo, e o documento tem VÁRIAS      → NADA. Era aqui que nascia o cartesiano.
    sem cultura DECLARADA no registro        → NADA, em nenhum caso.

Duas leis atravessam os quatro métodos:

1. **O alvo tem de estar escrito no texto.** Nunca vem do cabeçalho do registro
   — era de `ISSUE_IDS` que `ISSUE_SCAB` se espalhava por nove culturas.
2. **A cultura tem de estar DECLARADA em `CROP_IDS`.** Ler a prosa para
   adivinhá-la é o erro que pôs milho num boletim de oliveira no V2.

Nenhum par é inventado por proximidade de documento. Um alvo não migra para uma
cultura porque as duas aparecem no mesmo PDF.

A DIREÇÃO É INTERPRETAÇÃO SINTONIA — a frase continua sendo a evidência
-----------------------------------------------------------------------
`NEED_DIRECTION` é leitura nossa. Por isso cada pino carrega
`NEED_EVIDENCE_ID`, `NEED_EXCERPT` e `NEED_METHOD`: a frase original vai junto,
e quem discordar da classificação lê a frase e decide sozinho.

    CLASSIFICAR NÃO É SUBSTITUIR. O TRECHO ORIGINAL VIAJA COM O RÓTULO.

E a classificação NÃO é por palavra solta. «Terzo volo di Cydia pomonella
**terminato**, con danni in aumento» não é janela concluída: o que terminou foi
o voo, não a defesa. Por isso os padrões de conclusão exigem a defesa, o
tratamento ou a armadilha na mesma expressão.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_normalizar as N  # noqa: E402

# ── OS OITO ESTADOS ──────────────────────────────────────────────────────────
POSITIVE_PRESSURE = 'POSITIVE_PRESSURE'
MONITOR = 'MONITOR'
NEUTRAL_MENTION = 'NEUTRAL_MENTION'
NO_ACTION_RECOMMENDED = 'NO_ACTION_RECOMMENDED'
ACTION_SUSPENDED = 'ACTION_SUSPENDED'
WINDOW_CONCLUDED = 'WINDOW_CONCLUDED'
TREATMENT_PROHIBITED = 'TREATMENT_PROHIBITED'
UNKNOWN = 'UNKNOWN'

ESTADOS = [POSITIVE_PRESSURE, MONITOR, NEUTRAL_MENTION, NO_ACTION_RECOMMENDED,
           ACTION_SUSPENDED, WINDOW_CONCLUDED, TREATMENT_PROHIBITED, UNKNOWN]

# Os que FECHAM a porta comercial. Um deles na mesma oração vence qualquer
# «intervir» que apareça ao lado: quem manda parar manda parar.
RESTRITIVOS = (TREATMENT_PROHIBITED, ACTION_SUSPENDED, WINDOW_CONCLUDED,
               NO_ACTION_RECOMMENDED)

# ── OS PADRÕES, EM ORDEM DE PRECEDÊNCIA ──────────────────────────────────────
# Português da prosa de pesquisa e italiano das citações convivem: o registro
# guarda as duas línguas no mesmo campo, e traduzir a citação seria adulterar a
# prova. Então o padrão lê as duas.
_P = [
 (TREATMENT_PROHIBITED, [
    r'\bvigora a proibicao\b', r'\bproibicao de intervencao\b',
    r'\be proibido\b', r'\bproibid[ao]s? (?:a|o|de|durante)\b',
    r'\bvietat[oa]\b', r'\bdivieto\b', r'\be vietato\b']),

 (ACTION_SUSPENDED, [
    r'\bpode(?:m)? ser suspens[oa]s?\b', r'\bpodem ser suspensos\b',
    r'\bsuspensao (?:da|do|dos|das) (?:defesa|tratamento)\b',
    r'\bsospend\w*\b', r'\bsospes[oai]\w*\b']),

 (WINDOW_CONCLUDED, [
    # A conclusão tem de nomear a DEFESA, o TRATAMENTO ou a ARMADILHA.
    # «voo terminado» não é janela fechada — é fenologia.
    r'\b(?:defesa|difesa|tratamentos?|trattament\w+)[^.;]{0,60}'
    r'(?:conclu[ií]d[oa]|conclus[oa]|encerrad[oa]|terminad[oa])\b',
    r'\bpode considerar-se conclu[ií]da\b',
    r'\b(?:fim|final) (?:da|do) (?:defesa|tratamento)\b',
    r'\bretirar as armadilhas\b', r'\bretirada das armadilhas\b',
    r'\besgotad[ao] (?:a|o) (?:receptividade|suscetibilidade)\b',
    r'\bja nao (?:e|esta) (?:suscetivel|sensivel|receptivo)\b',
    r'\bjanela\w* (?:obrigatori\w+ )?(?:fechad|terminar|encerr)\w*\b']),

 (NO_ACTION_RECOMMENDED, [
    r'\bnao (?:sao|e|ha) necessari\w*\b', r'\bnon (?:sono )?necessari\w*\b',
    r'\bnao ha recomendacao\b', r'\bnenhuma recomendacao\b',
    r'\bnao se preveem intervencoes\b', r'\bnao (?:se )?preve\w* tratament\w*\b',
    r'\bnon si prevedono\b', r'\bnao necessit\w*\b',
    r'\bnao (?:e|sao) necessario\w*\b']),

 (POSITIVE_PRESSURE, [
    r'\bdann?[oi]s? (?:in|em) aumento\b', r'\bdanni in aumento\b',
    r'\bem aumento\b', r'\baggressivita particolarmente elevata\b',
    r'\brisco (?:de )?\w* ?(?:infectivo )?(?:em nivel )?elevado\b',
    r'\brischio\w* elevat\w*\b',
    r'\bintervir\b', r'\bintervenire\b', r'\bintervenite\b',
    r'\bindica tratar\b', r'\bdeve(?:-se)? tratar\b',
    r'\brecomenda\w* (?:o )?(?:tratamento|intervencao|intervir)\b',
    r'\braccomand\w+ (?:il |un )?trattament\w*\b',
    r'\bcondicoes ideais para (?:novas )?infec\w+\b',
    r'\bcondizioni ideali per\b.{0,30}\binfezion\w*\b',
    r'\btratamento\w* (?:insecticida |fitossanitario )?justificad\w*\b',
    r'\bstrategia di difesa dovra essere puntuale\b',
    r'\bestrategia de defesa (?:devera|deve) ser pontual\b',
    r'\bacima da qual\b.{0,40}\btratar\b',
    r'\bao ultrapassar\b.{0,60}\bintervir\b']),

 (MONITOR, [
    r'\bmonitor\w+\b', r'\bamostrag\w+\b', r'\bcampionament\w+\b',
    r'\binspecionar\b', r'\bverificar\b', r'\bavaliar\b', r'\bvalutare\b',
    r'\bcontroll\w+\b', r'\barmadilhas? para captura\b',
    r'\blimiar\b', r'\bsoglia\b', r'\bcaptur\w+\b',
    r'\bainda (?:baixa|ausente)\b', r'\bancora bassa\b', r'\baddirittura assente\b',
    r'\bpochissime aree sopra soglia\b', r'\babaixo (?:do|da) limiar\b']),
]

# Textos que declaram, eles mesmos, que não há leitura possível.
_SEM_LEITURA = re.compile(
    r'^\s*(?:nao sei|nao abri|nenhuma\b|n/?a)\b', re.I)

# Campos de texto do sinal que valem como evidência de NECESSIDADE.
# `INTERVENTION_GUIDANCE` é o que o serviço RECOMENDA; `WHAT_IT_IS` é o que o
# registro OBSERVOU. Os dois respondem «há o que fazer?».
#
# ⚠️ `CITATION` está FORA de propósito, e a medição mostrou por quê: a citação
# do boletim empacota vários assuntos dentro de umas mesmas aspas — «non sono
# necessari interventi. Fase calante dei voli della Tignoletta…» — e a
# advertência de um alvo escorria para os outros três da mesma aspa. A citação
# continua sendo a prova do fato; ela não é a recomendação sobre ele.
#
#     CITAÇÃO SEM RECOMENDAÇÃO NÃO É DIREÇÃO.
CAMPOS_DE_TEXTO = ('INTERVENTION_GUIDANCE', 'WHAT_IT_IS')


def _n(t):
    """Sem acento, minúsculo — o mesmo achatamento do léxico canônico."""
    return N._n(t)


def oracoes(texto):
    """Parte o texto em orações, sem quebrar dentro de «citação»."""
    t = str(texto or '')
    if not t.strip():
        return []
    # protege o conteúdo entre aspas angulares, que é citação da fonte
    guardas = {}
    def _guardar(m):
        k = '\x00%d\x00' % len(guardas)
        guardas[k] = m.group(0)
        return k
    t = re.sub(r'«[^»]*»', _guardar, t)
    # Depois de uma citação fechada, o boletim muda de assunto: «Peronospora:
    # "non necessari interventi." Oidio: ...» são dois tópicos, não um. Sem este
    # corte, a advertência de um alvo contaminava os alvos seguintes.
    t = re.sub(r'(\x00\d+\x00)\s+(?=[A-ZÀ-Ý])', r'\1\n', t)
    partes = re.split(r'(?<=[.;])\s+|\s+\|\s+|\n', t)
    saida = []
    for p in partes:
        for k, v in guardas.items():
            p = p.replace(k, v)
        p = p.strip()
        if p:
            saida.append(p)
    return saida


def direcao(oracao):
    """→ (ESTADO, padrão que decidiu). Precedência, nunca palavra solta."""
    t = _n(oracao)
    if not t.strip():
        return UNKNOWN, None
    if _SEM_LEITURA.match(t):
        return UNKNOWN, 'o proprio texto declara que nao ha leitura'
    for estado, padroes in _P:
        for p in padroes:
            if re.search(p, t):
                return estado, p
    return NEUTRAL_MENTION, None


def _mais_restritiva(estados):
    """Entre as vistas para o mesmo par, a que fecha a porta ganha.

        QUEM MANDA PARAR MANDA PARAR, MESMO QUE OUTRA ORACAO MANDE AGIR.

    Fora dos restritivos, uma pressão declarada não é apagada por uma menção de
    monitoramento ao lado: as duas coisas convivem num boletim, e a pressão é a
    que responde «por que agora».
    """
    for e in RESTRITIVOS:                      # já em ordem de severidade
        if e in estados:
            return e
    for e in (POSITIVE_PRESSURE, MONITOR, NEUTRAL_MENTION):
        if e in estados:
            return e
    return UNKNOWN


# ── A DIREÇÃO NÃO SE REPARTE ENTRE ALVOS ────────────────────────────────────
#
# Medido em `IT-PHEN-041`: Firenze publica o mesmo texto de Siena com VÍRGULAS
# onde Siena usou ponto e vírgula. A oração vira uma só, nomeia botrite, oídio e
# Scaphoideus, e o primeiro padrão que casa é `suspensao`. Os três recebiam
# `ACTION_SUSPENDED` — inclusive a botrite, para a qual o MESMO texto diz
# «janela de maior suscetibilidade». A oportunidade verdadeira de Toscana era
# apagada por pontuação alheia.
#
#     UMA PALAVRA DE DIREÇÃO NUMA ORAÇÃO COM VÁRIOS ALVOS NÃO DIZ A QUAL DELES
#     SE REFERE. ENTÃO NÃO SE SABE — E «NÃO SEI» É A RESPOSTA HONESTA.
#
# O par NÃO é destruído: a fonte escreveu cultura e alvo juntos, e isso continua
# sendo observação. O que não existe é a direção individual. E a assimetria é de
# propósito: `UNKNOWN` não fecha a porta comercial nem a abre — nunca vende.
#
# ⚠️ Isto NÃO vale para a oração que não nomeia alvo nenhum. «Durante a floração
# vigora a proibição de intervenção fitoiátrica com inseticidas» proíbe a
# PRÁTICA sobre a cultura inteira: não é uma direção de um alvo repartida entre
# vários, é uma direção que nunca foi de um alvo só.
MULTIPLE_TARGETS_IN_CLAUSE = 'MULTIPLE_TARGETS_IN_CLAUSE'
MULTIPLE_CROPS_IN_CLAUSE = 'MULTIPLE_CROPS_IN_CLAUSE'

AMBIGUIDADE = {
    MULTIPLE_TARGETS_IN_CLAUSE:
        'a mesma oracao nomeia mais de um alvo e uma direcao so: nao se sabe a '
        'qual deles a direcao se refere, e por isso nenhum a recebeu.',
    MULTIPLE_CROPS_IN_CLAUSE:
        'a mesma oracao nomeia mais de uma cultura e uma direcao so: nao se sabe '
        'a qual delas a direcao se refere, e por isso nenhuma a recebeu.',
}

# Força dos métodos de atribuição, do mais forte ao mais fraco. Um par visto
# pelo método forte não é rebaixado por reaparecer pelo fraco.
FORCA_DO_METODO = ('PAIR_IN_SAME_CLAUSE', 'PAIR_IN_DOCUMENT_TITLE',
                   'CROP_FROM_PRECEDING_CLAUSE', 'CROP_FROM_SINGLE_CROP_DOCUMENT')


def _pinar(achados, sinal, campo, metodo, crop, issue, estado, oracao,
           ambiguidade=None):
    """Registra um pino de necessidade, guardando o trecho que o sustenta."""
    p = achados.setdefault((crop, issue), {
        'CROP_ID': crop, 'ISSUE_ID': issue,
        'NEED_EVIDENCE_ID': sinal['ID'],
        'NEED_FIELD': campo,
        'NEED_METHOD': metodo,
        'DIRECTIONS_SEEN': [],
        'EXCERPT_BY_DIRECTION': {},
        'NEED_AMBIGUITY_CODES': [],
    })
    if estado not in p['DIRECTIONS_SEEN']:
        p['DIRECTIONS_SEEN'].append(estado)
    p['EXCERPT_BY_DIRECTION'].setdefault(estado, oracao[:320])
    if ambiguidade and ambiguidade not in p['NEED_AMBIGUITY_CODES']:
        p['NEED_AMBIGUITY_CODES'].append(ambiguidade)
    if FORCA_DO_METODO.index(metodo) < FORCA_DO_METODO.index(p['NEED_METHOD']):
        p['NEED_METHOD'], p['NEED_FIELD'] = metodo, campo


def par_do_titulo(sinal):
    """→ pares que o PRÓPRIO TÍTULO do boletim declara.

    «Bollettino di difesa integrata COLTURE ERBACEE — Piralide del mais» nomeia
    a cultura e o alvo lado a lado: é o assunto declarado do documento, escrito
    pelo serviço. Não é inferência de proximidade — é o cabeçalho.

    Isto não reabre o cartesiano: o cartesiano vinha de cruzar listas, e aqui só
    entram os nomes que estão dentro do próprio título. Um título que não nomeia
    alvo não produz par nenhum.

        O CABEÇALHO DO DOCUMENTO É DECLARAÇÃO, NÃO VIZINHANÇA.
    """
    t = sinal.get('BULLETIN_TITLE')
    if not t:
        return []
    crops_doc = set(sinal.get('CROP_IDS') or [])
    crops = [c for c in N.crops_no_texto(t) if c in crops_doc]
    issues = N.issues_no_texto(t)
    return [(c, i) for c in crops for i in issues]


def atribuicoes(sinal):
    """→ gera (campo, metodo, crops, issues, oracao) — a ATRIBUIÇÃO, sem leitura.

    Este é o único lugar do repositório que decide de que par uma oração fala.
    `pares_observados` lê a DIREÇÃO em cima disto; o inventário de janelas lê o
    TIPO DE JANELA em cima disto. Dois leitores, uma atribuição.

        DUAS CÓPIAS DA MESMA REGRA DIVERGEM NO DIA EM QUE UMA DELAS É
        CONSERTADA.
    """
    crops_doc = list(sinal.get('CROP_IDS') or [])
    if not crops_doc:
        # ⚠️ SEM CULTURA DECLARADA NÃO HÁ PAR. É a mesma lei de `crop_id`: ler a
        # prosa para adivinhar a cultura que o registro não declarou foi o que
        # pôs milho num boletim de oliveira no V2 — e aqui puxaria CROP_MAIZE de
        # «as estações agrometeorológicas MAIS próximas», onde `mais` é advérbio
        # português e não a cultura italiana.
        return
    do_titulo = par_do_titulo(sinal)
    for campo in CAMPOS_DE_TEXTO:
        texto = sinal.get(campo)
        if not texto:
            continue
        ultimas_crops, desde = [], 99
        for oracao in oracoes(texto):
            aqui = [c for c in N.crops_no_texto(oracao) if c in crops_doc]
            if aqui:
                ultimas_crops, desde = aqui, 0
            else:
                desde += 1
            issues = N.issues_no_texto(oracao)
            if not issues:
                # A oração não nomeia alvo — mas o TÍTULO já declarou de que par
                # este documento trata, e esta oração é a recomendação sobre ele.
                if do_titulo:
                    yield (campo, 'PAIR_IN_DOCUMENT_TITLE',
                           sorted({c for c, _i in do_titulo}),
                           sorted({i for _c, i in do_titulo}), oracao)
                continue
            # ⚠️ O ALVO TEM DE ESTAR ESCRITO NA ORAÇÃO. Nunca vem do cabeçalho
            # do documento: era daí que `ISSUE_SCAB` do inventário se espalhava
            # por nove culturas.
            if aqui:
                crops, metodo = aqui, 'PAIR_IN_SAME_CLAUSE'
            elif ultimas_crops and desde <= 2:
                # O boletim escreve por tópico: «Pero/maculatura bruna: ... .
                # Vite/botrite: ...». A cultura vale até a próxima ser nomeada.
                crops, metodo = ultimas_crops, 'CROP_FROM_PRECEDING_CLAUSE'
            elif len(crops_doc) == 1:
                crops, metodo = list(crops_doc), 'CROP_FROM_SINGLE_CROP_DOCUMENT'
            else:
                # ⚠️ AQUI NASCIA O CARTESIANO. O par não é emitido.
                continue
            yield campo, metodo, crops, issues, oracao


def pares_observados(sinal):
    """→ lista de pares (cultura, alvo) que ESTE registro de fato observou.

    Cada par carrega a direção, o trecho que a sustenta, o campo de onde saiu e
    o método pelo qual a cultura foi atribuída.
    """
    achados = {}
    for campo, metodo, crops, issues, oracao in atribuicoes(sinal):
        est, _padrao = direcao(oracao)
        if metodo == 'PAIR_IN_DOCUMENT_TITLE':
            # a oração não nomeia alvo: só o título disse de que par se trata
            if est == NEUTRAL_MENTION:
                continue
            for c in crops:
                for i in issues:
                    _pinar(achados, sinal, campo, metodo, c, i, est, oracao)
            continue
        # ⚠️ UMA DIREÇÃO NÃO SE REPARTE. Se a oração nomeia mais de um alvo
        # — ou mais de uma cultura — e traz uma palavra de direção, não se
        # sabe a qual deles ela se refere. Então não se sabe: `UNKNOWN`.
        amb = None
        if est not in (NEUTRAL_MENTION, UNKNOWN):
            if len(issues) > 1:
                amb, est = MULTIPLE_TARGETS_IN_CLAUSE, UNKNOWN
            elif len(crops) > 1:
                amb, est = MULTIPLE_CROPS_IN_CLAUSE, UNKNOWN
        for c in crops:
            for i in issues:
                _pinar(achados, sinal, campo, metodo, c, i, est, oracao, amb)
    for p in achados.values():
        p['NEED_DIRECTION'] = _mais_restritiva(p['DIRECTIONS_SEEN'])
        p['NEED_EXCERPT'] = p['EXCERPT_BY_DIRECTION'].get(p['NEED_DIRECTION'], '')
        p.pop('EXCERPT_BY_DIRECTION')
    return sorted(achados.values(), key=lambda p: (p['CROP_ID'], p['ISSUE_ID']))


def indice_de_pares(sinais):
    """→ {(cultura, alvo): [pino, ...]} sobre uma lista de sinais de campo."""
    ix = defaultdict(list)
    for s in sinais:
        for p in pares_observados(s):
            ix[(p['CROP_ID'], p['ISSUE_ID'])].append(p)
    return ix


def direcao_do_par(pinos):
    """→ (direção, pino que a decidiu) para o conjunto de pinos de um par."""
    est = _mais_restritiva([p['NEED_DIRECTION'] for p in pinos])
    for p in pinos:
        if p['NEED_DIRECTION'] == est:
            return est, p
    return UNKNOWN, None


# ── INSPEÇÃO ─────────────────────────────────────────────────────────────────
def _cartesiano(sinais):
    """O par como o motor V1 o formava: lista de culturas × lista de alvos."""
    pares = set()
    for s in sinais:
        for c in (s.get('CROP_IDS') or []):
            for i in (s.get('ISSUE_IDS') or []):
                pares.add((c, i))
    return pares


def main():
    ing = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
    sinais = [r for r in json.load(
        open(os.path.join(ing, 'CURRENT-FIELD-SIGNALS.json'), encoding='utf-8')
    )['RECORDS'] if r.get('CLIENT_SAFE')]

    antes = _cartesiano(sinais)
    ix = indice_de_pares(sinais)
    depois = set(ix)

    print('sinais de campo client-safe: %d' % len(sinais))
    print()
    print('PARES CULTURA x ALVO')
    print('  ANTES  (cartesiano, V1) : %d' % len(antes))
    print('  DEPOIS (observados, V11): %d' % len(depois))
    print('  removidos : %d' % len(antes - depois))
    print('  adicionados: %d' % len(depois - antes))
    print()
    print('REMOVIDOS — o documento nao os escreveu juntos')
    for c, i in sorted(antes - depois):
        print('   - %-22s x %s' % (c, i))
    print()
    print('ADICIONADOS — com o trecho que os sustenta')
    for c, i in sorted(depois - antes):
        p = ix[(c, i)][0]
        print('   + %-22s x %-24s %s' % (c, i, p['NEED_METHOD']))
        print('       %s · %s' % (p['NEED_EVIDENCE_ID'], p['NEED_DIRECTION']))
        print('       «%s»' % p['NEED_EXCERPT'][:150])
    print()
    print('DIRECAO DA NECESSIDADE, por par observado')
    d = Counter(direcao_do_par(v)[0] for v in ix.values())
    for e in ESTADOS:
        if d.get(e):
            print('  %-24s %d' % (e, d[e]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
