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
    # ⚠️ «suspensao DE OIDIO». O boletim de Firenze escreve a suspensao com o
    # nome do ALVO no lugar do nome da defesa, e o padrao acima — que exige a
    # palavra «defesa» ou «tratamento» — nao a via. Enquanto a oracao corrida
    # era lida inteira o buraco ficava escondido: a suspensao da peronospora,
    # escrita com «defesa», cobria os alvos vizinhos. Separada a enumeracao,
    # cada pedaco responde por si, e este pedaco precisa ser lido pelo que ele
    # mesmo diz.
    #
    #     SUSPENDER O OIDIO E SUSPENDER O TRATAMENTO DO OIDIO.
    r'\bsuspensao (?:de|da|do|das|dos)\b',
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


# ── A ORAÇÃO CORRIDA ─────────────────────────────────────────────────────────
# `oracoes()` corta em `.` e `;`. Dois boletins publicam O MESMO TEXTO com
# pontuação diferente: `IT-PHEN-040` (Siena) separa os assuntos com ponto e
# vírgula, e `IT-PHEN-041` (Firenze) — que o próprio registro declara ser
# «mesmo texto de secoes que Siena nesta semana» — separa com VÍRGULA. O corte
# não vê a vírgula, e a frase de Firenze chega inteira:
#
#   «suspensao da defesa antiperonosporica…, suspensao de oidio…, fim da defesa
#    de black rot, janela de maior suscetibilidade a botrite, fim da defesa de
#    Scaphoideus titanus.»
#
# Cinco assuntos, uma oração. O primeiro padrão que casa é `suspensao`, e a
# direção era aplicada aos TRÊS alvos com `ISSUE_ID` — inclusive à botrite,
# sobre a qual a mesma frase diz o contrário: «janela de maior suscetibilidade».
# Como a regra do par é «a que manda parar vence», a leitura falsa SUPRIMIA a
# verdadeira: videira × botrite · Toscana saía `ACTION_SUSPENDED`.
#
#     UMA ORAÇÃO QUE NOMEIA TRÊS ALVOS E UM VERBO NÃO DIZ A QUAL DELES O VERBO
#     SE APLICA. ATRIBUIR A TODOS É ADIVINHAR — E AQUI ADIVINHOU ERRADO.
#
# A correção não afrouxa nada e não inventa direção nenhuma:
#
#   1. a oração que nomeia UM alvo continua exatamente como estava;
#   2. a que nomeia MAIS DE UM é subdividida na vírgula — é a mesma enumeração
#      que Siena escreveu com ponto e vírgula — e cada pedaço que nomeia UM só
#      alvo responde por ele, com a direção que esse pedaço declara;
#   3. o alvo que nenhum pedaço isola fica `NEUTRAL_MENTION` e a ambiguidade é
#      ESCRITA no pino (`NEED_AMBIGUITY`), em vez de virar um palpite silencioso.
#
# `NEUTRAL_MENTION` não abre porta comercial nenhuma: em `v21_comercial` ele cai
# em `NECESSIDADE_MORNA` e o caso sai `TO_VALIDATE`, o mesmo destino de quem tem
# a porta fechada. Portanto o passo 3 nunca converte uma proibição em venda —
# ele apenas para de emprestar a proibição a quem a frase não nomeou.
_VIRGULA = re.compile(r',\s+')


def sub_oracoes(oracao):
    """→ os pedaços de uma enumeração separada por vírgula."""
    return [x.strip() for x in _VIRGULA.split(str(oracao or '')) if x.strip()]


def atribuir_direcao(oracao, issues, direcao_fn=None):
    """→ {alvo: (ESTADO, trecho, ambiguidade|None)} para UMA oração.

    Com um alvo só, é a direção da oração — o comportamento de sempre. Com mais
    de um, cada alvo só recebe direção do pedaço que o nomeia sozinho.
    """
    dirf = direcao_fn or direcao
    if len(issues) <= 1:
        est, _ = dirf(oracao)
        return {i: (est, oracao, None) for i in issues}
    est_todo, _ = dirf(oracao)
    vistos = defaultdict(list)
    trecho_de = {}
    for parte in sub_oracoes(oracao):
        aqui = N.issues_no_texto(parte)
        if len(aqui) != 1:
            continue
        est, _ = dirf(parte)
        i = aqui[0]
        vistos[i].append(est)
        trecho_de.setdefault(i, parte)
    saida = {}
    for i in issues:
        if i in vistos:
            # o mesmo alvo isolado em dois pedaços: vale a lei do arquivo.
            saida[i] = (_mais_restritiva(vistos[i]), trecho_de[i], None)
        else:
            saida[i] = (NEUTRAL_MENTION, oracao,
                        'ORACAO_CORRIDA · %d alvos numa oracao so; a direcao '
                        'lida no conjunto (%s) nao foi atribuida a nenhum deles '
                        'porque a frase nao diz a qual se aplica'
                        % (len(issues), est_todo))
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
        'AMBIGUITIES': [],
    })
    if estado not in p['DIRECTIONS_SEEN']:
        p['DIRECTIONS_SEEN'].append(estado)
    p['EXCERPT_BY_DIRECTION'].setdefault(estado, oracao[:320])
    if ambiguidade and ambiguidade not in p['AMBIGUITIES']:
        p['AMBIGUITIES'].append(ambiguidade)
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


def pares_observados(sinal):
    """→ lista de pares (cultura, alvo) que ESTE registro de fato observou.

    Cada par carrega a direção, o trecho que a sustenta, o campo de onde saiu e
    o método pelo qual a cultura foi atribuída.
    """
    crops_doc = list(sinal.get('CROP_IDS') or [])
    achados = {}
    if not crops_doc:
        # ⚠️ SEM CULTURA DECLARADA NÃO HÁ PAR. É a mesma lei de `crop_id`: ler a
        # prosa para adivinhar a cultura que o registro não declarou foi o que
        # pôs milho num boletim de oliveira no V2 — e aqui puxaria CROP_MAIZE de
        # «as estações agrometeorológicas MAIS próximas», onde `mais` é advérbio
        # português e não a cultura italiana.
        return []
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
                    est_t, _ = direcao(oracao)
                    if est_t != NEUTRAL_MENTION:
                        for c, i in do_titulo:
                            _pinar(achados, sinal, campo, 'PAIR_IN_DOCUMENT_TITLE',
                                   c, i, est_t, oracao)
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
            # ⚠️ A DIREÇÃO É POR ALVO, NÃO POR ORAÇÃO. Ver `atribuir_direcao`.
            for i, (est, trecho, amb) in atribuir_direcao(oracao, issues).items():
                for c in crops:
                    _pinar(achados, sinal, campo, metodo, c, i, est, trecho, amb)
    for p in achados.values():
        p['NEED_DIRECTION'] = _mais_restritiva(p['DIRECTIONS_SEEN'])
        p['NEED_EXCERPT'] = p['EXCERPT_BY_DIRECTION'].get(p['NEED_DIRECTION'], '')
        p.pop('EXCERPT_BY_DIRECTION')
        # A ambiguidade viaja com o pino: quem discorda lê a oração inteira.
        p['NEED_AMBIGUITY'] = p['AMBIGUITIES'][0] if p['AMBIGUITIES'] else None
        p.pop('AMBIGUITIES')
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
