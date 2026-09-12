#!/usr/bin/env python3
"""
COLETOR — a porta única por onde toda rota paga passa a entrar.

Existe para que os defeitos apontados pela auditoria não possam se repetir por esquecimento.
Quem chama `executar()` não consegue, mesmo querendo:

  · perder a hora da execução — `STARTED_AT`/`FINISHED_AT` vêm da própria plataforma;
  · perder o ator, a versão de build, o dataset e o custo;
  · normalizar antes de gravar o bruto — o RAW é escrito primeiro, sempre;
  · gravar o token — ele vive só no cabeçalho da chamada e nunca entra no manifesto.

A cadeia que isto garante:

    RAW → NORMALIZED → ANALYTICAL

e, no sentido inverso, `CONTENT → RUN_ID → RUN_MANIFEST → INPUT / ACTOR / DATASET / RAW`.

Por que `runs?waitForFinish` e não `run-sync-get-dataset-items`: o segundo devolve só os
itens. Os metadados da execução — `startedAt`, `finishedAt`, `defaultDatasetId`, `buildId`,
`usageTotalUsd` — vêm no objeto da execução, e são exatamente os campos que faltavam.

A ESPERA DE 60 SEGUNDOS — O DEFEITO QUE JÁ PRODUZIU 21 RETRATOS PARCIAIS
------------------------------------------------------------------------
Até 2026-09-02 este arquivo pedia `waitForFinish=280`. A documentação da Apify diz, do
parâmetro: *"By default it is 0, the maximum value is 60"*. Pedir 280 não compra 280 —
a plataforma responde aos 60 e devolve a execução com status TRANSITÓRIO (`READY` ou
`RUNNING`), que é "ainda não acabou", não "acabou assim".

O que acontecia depois é o defeito inteiro: o coletor lia o dataset de uma execução que
AINDA ESTAVA SENDO ESCRITA, contava os itens que já tinham caído lá, e gravava esse
pedaço como `RAW_EVIDENCE_STATE: PRESERVED`.

    STATUS TRANSITÓRIO NÃO É FIM DE EXECUÇÃO.
    RETRATO DE MEIA COLETA NÃO É COLETA PRESERVADA.

Medido no próprio acervo desta casa, em `data/samples/SENSOR-PILOT/RUNS-A.json`: 21
manifestos carregam `"ERROR": "status da plataforma: READY."`, e três deles têm
`FINISHED_AT` exatamente ~61 s depois do `STARTED_AT` — e SEM milissegundos, porque a
hora não veio da plataforma, veio do relógio local em `agora()`. As execuções que deram
`SUCCESS` terminaram entre 2 e 12 segundos: por isso o defeito nunca apareceu.

O conserto tem duas partes, e as duas importam:

  1. pedir à plataforma o máximo que ela concede (60 s) — a maioria das execuções desta
     casa termina antes disso e nem chega a consultar de novo;
  2. quando 60 s não bastarem, **consultar `GET /v2/actor-runs/{id}` até o status ser
     TERMINAL**, dentro de um tempo próprio. Só então ler o dataset.

TRÊS TRAVAS QUE A PLATAFORMA OFERECE E ESTA CASA NÃO USAVA
------------------------------------------------------------
`teto_usd`   → `&maxTotalChargeUsd=`. Trava do lado da Apify: funciona mesmo se o meu
               código ler o custo errado. É a única proteção que sobrevive a um bug meu.
`build`      → `&build=`. Os quatro atores oficiais de Instagram foram reconstruídos no
               mesmo minuto de 2026-08-31; "entrada provada ontem" tem prazo de dias.
               Fixar o build faz a coleta ser reproduzível.
`requestsFailed` → lido de graça do registro `SDK_CRAWLER_STATISTICS_0`. Existe porque
               contagem de itens NÃO detecta perda: há execução medida com 107 de 161
               requisições falhadas que devolveu 708 itens e saiu `SUCCEEDED` — no dia
               seguinte, mesma entrada, 4.723 itens. A lei antiga ("SUCCEEDED com zero
               itens = PARTIAL") não pega isso: vieram itens, faltavam 85%.
"""
import datetime
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import proveniencia as pv  # noqa: E402
# A guarda do gasto. Ela NAO decide relevancia — valida a autorizacao que
# recebe. O dono da relevancia vive noutra linhagem, e e assim que fica.
#
#     SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER.
import autorizacao_de_gasto as az  # noqa: E402
#: A recusa da guarda, re-exportada: quem apanha excecoes do coletor nao
#: tem de saber em que ficheiro ela nasceu.
SemAutorizacaoDeGasto = az.SemAutorizacaoDeGasto

RAW_DIR = os.path.join(ROOT, 'data', 'samples', 'raw-paid')
API = 'https://api.apify.com/v2'

# Teto documentado do `waitForFinish`. Pedir mais não compra mais — só faz a resposta
# parecer conclusiva quando não é.
ESPERA_MAXIMA_DA_PLATAFORMA = 60

# Status em que a execução ACABOU. Todo o resto é "ainda está acontecendo".
STATUS_TERMINAIS = ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT')
STATUS_TRANSITORIOS = ('READY', 'RUNNING', 'ABORTING')


# ══════════════════════════════════════════════════════════════════════════════
# O ORÇAMENTO FINANCEIRO DESTA EXECUÇÃO
# ══════════════════════════════════════════════════════════════════════════════
# A C10.8A-R provou o primeiro teto: quantos ACESSOS uma execução pode fazer. Este
# é o segundo, e ele é de outra natureza.
#
#     REQUEST COUNT != MONEY.
#
# Dez chamadas à API oficial do YouTube gastam dez idas à rede e zero dólares. Um
# único POST que acende um ator da Apify gasta uma ida e compromete dinheiro antes
# de alguém saber quanto. Os dois eixos medem coisas diferentes e nenhum responde
# pelo outro:
#
#     NETWORK BUDGET decide SE CABE MAIS UMA IDA.
#     FINANCIAL BUDGET decide SE PODEMOS ASSUMIR MAIS EXPOSIÇÃO FINANCEIRA.
#
# POR QUE ELE VIVE AQUI, E NÃO NUM FICHEIRO NOVO
# ------------------------------------------------
# O censo da C10.8A-F mediu, e não presumiu: `POST /v2/acts/{ator}/runs` — a linha
# abaixo, dentro de `executar()` — é o ÚNICO sítio desta casa que compromete
# dinheiro. As trinta e cinco capacidades declaradas têm três com rota paga por
# omissão e ZERO com adaptador; `ferramentas/contrato_ator.py` toca a Apify mas só
# com `GET` sem credencial. Uma porta, e é esta.
#
# Por isso, e ao contrário do teto de rede — que tem 25 portas e por isso é
# declarado em `scrap_http` e cobrado nas primitivas do Python —, aqui o dono do
# conceito e o ponto de cobrança são o MESMO ficheiro. Não por comodidade: porque
# a medição disse que só há um.
#
#     ONE CONCEPT → ONE OWNER. Quando há uma só porta, o dono está nela.
#
# E ele é da EXECUÇÃO, não do processo: duas corridas têm orçamentos distintos, e a
# segunda não herda a dívida da primeira.
import contextlib
import threading

_LOCAL = threading.local()

#: O dinheiro vive em MICRO-DÓLARES INTEIROS por dentro. Somar `float` de dólar
#: acumula erro, e um teto que erra na sexta casa decimal é um teto que às vezes
#: deixa passar. A Apify reporta `usageTotalUsd` com essa mesma granularidade.
MICRO = 1000000

#: O que se SABE do custo de uma chamada. Quatro valores, e nenhum colapsa no
#: outro:
#:
#:     NOT_RUN          != 0 — o provider nunca foi chamado.
#:     UNKNOWN          != 0 — foi chamado e não conseguimos ler quanto custou.
#:     READ_NOT_SETTLED      — lemos `usageTotalUsd`, e a Apify ainda não fechou a
#:                             conta. Esta casa já anunciou US$0,90 e pagou
#:                             US$5,04 exactamente por publicar este valor como
#:                             se fosse o final.
#:     SETTLED               — reconciliado depois. Não acontece aqui; acontece em
#:                             `provas/corrigir_custo.py`, e é o único definitivo.
#:
#: Por isso o eixo `ACTUAL` deste orçamento quer dizer «o que se conseguiu LER»,
#: nunca «o que se pagou».
#:
#:     READ COST != SETTLED COST.
CUSTO_NAO_CORRIDO = 'NOT_RUN'
CUSTO_DESCONHECIDO = 'UNKNOWN'
CUSTO_LIDO = 'READ_NOT_SETTLED'
CUSTO_LIQUIDADO = 'SETTLED'


def _micros(valor):
    """Dólar → micro-dólar inteiro. `None` continua `None`: ausência não é zero."""
    if valor is None:
        return None
    return int(round(float(valor) * MICRO))


def _dolares(micros):
    return round(micros / float(MICRO), 6)


class SemOrcamentoFinanceiro(RuntimeError):
    """A chamada paga que NÃO acontece. Ela morre antes do provider.

    Não é a fonte a recusar, não é a plataforma a bloquear e não é o teto de rede:
    é esta casa a cumprir um limite de DINHEIRO que ela própria declarou. Quem a
    apanhar não pode traduzi-la para `SOURCE_UNAVAILABLE`, `BLOCKED` nem
    `NETWORK_BUDGET_EXHAUSTED` — são quatro coisas diferentes e só uma aconteceu.
    """


class Reserva(object):
    """Dinheiro comprometido por UMA chamada, à espera de saber o que custou.

    Ela existe porque `AUTHORIZED`, `COMMITTED` e `ACTUAL` são três eixos, e o
    intervalo entre o segundo e o terceiro é exactamente onde o dinheiro fica sem
    dono se ninguém o guardar.
    """

    def __init__(self, orcamento, cap_micros, registo):
        self.orcamento = orcamento
        self.cap_micros = cap_micros
        self.registo = registo
        self.fechada = False

    @property
    def cap(self):
        """O teto que vai como `maxTotalChargeUsd` — nunca acima do que resta."""
        return _dolares(self.cap_micros)

    def liquidar(self, custo):
        """Fecha a reserva com o custo REAL, lido do provider.

        `custo=None` não é zero: é `UNKNOWN`, e `UNKNOWN` não devolve o dinheiro.
        """
        return self.orcamento._fechar(self, _micros(custo))

    def desconhecer(self):
        """O provider pode ter cobrado e não temos como saber. O dinheiro fica fora.

            UM GASTO QUE NÃO SE CONSEGUE LER NÃO É UM GASTO QUE NÃO ACONTECEU.
        """
        return self.orcamento._fechar(self, None)

    def anular(self, porque):
        """A chamada PROVADAMENTE não correu — o provider respondeu «não».

        Só para o caso em que a própria plataforma devolveu recusa SEM criar
        execução. Usar isto num caso duvidoso seria devolver ao bolso dinheiro
        que talvez já tenha saído.
        """
        return self.orcamento._fechar(self, 0, anulada=porque)


class OrcamentoFinanceiro(object):
    """Quanto dinheiro esta execução ainda pode comprometer.

    Sete conceitos, e eles não se misturam:

        AUTHORIZED  o que a execução foi autorizada a comprometer
        COMMITTED   reservado por chamadas em curso, ainda sem custo lido
        ACTUAL      o que chamadas terminadas custaram de verdade
        UNKNOWN     reservado por chamadas cujo custo nunca se soube
        REMAINING   AUTHORIZED − (ACTUAL + COMMITTED + UNKNOWN)
        EXHAUSTED   não resta nada para comprometer
        REFUSED     quantas chamadas o teto recusou antes do provider
    """

    def __init__(self, limite):
        if limite is None or float(limite) < 0:
            raise ValueError('limite financeiro inválido: %r' % limite)
        self.limite_micros = _micros(limite)
        self.gasto_micros = 0
        self.comprometido_micros = 0
        self.desconhecido_micros = 0
        self.recusadas = 0
        self.tentativas = []
        # A trava existe para que duas chamadas nunca leiam o mesmo saldo e
        # comprometam as duas. O runtime de hoje é SERIAL — medido: não há
        # `threading`, `concurrent.futures` nem `asyncio` em nenhuma das três
        # portas pagas — mas segurança presumida não é segurança medida.
        self._trava = threading.Lock()

    # ── os sete conceitos, em dólar ──────────────────────────────────────────
    @property
    def autorizado(self):
        return _dolares(self.limite_micros)

    @property
    def gasto(self):
        return _dolares(self.gasto_micros)

    @property
    def comprometido(self):
        return _dolares(self.comprometido_micros)

    @property
    def desconhecido(self):
        return _dolares(self.desconhecido_micros)

    @property
    def exposto_micros(self):
        return self.gasto_micros + self.comprometido_micros + self.desconhecido_micros

    @property
    def restante(self):
        return _dolares(max(0, self.limite_micros - self.exposto_micros))

    @property
    def esgotado(self):
        return self.exposto_micros >= self.limite_micros

    def reservar(self, *, pedido=None, ator=None, rota=None, missao=None):
        """Compromete dinheiro ANTES de o provider ser chamado. → `Reserva`.

        `pedido` é o teto que o chamador queria mandar ao provider. Ele é
        REBAIXADO ao que resta — nunca o contrário:

            PROVIDER CAP <= EXECUTION REMAINING.

        Sem `pedido`, o teto enviado é o saldo inteiro: uma chamada paga sem
        trava do lado do provider é exposição sem fim, e um orçamento declarado
        não pode permitir isso.
        """
        # `MISSAO` e nao `MOTIVO_PAGO`: o que chega aqui e a missao que chamou.
        # O motivo canonico do gasto e do ROTEADOR, que e quem o valida contra
        # `MOTIVOS_PAGOS`, e ele viaja no registo dele.
        #
        #     UM CAMPO COM O NOME DE OUTRA COISA MENTE SEM NINGUEM MENTIR.
        registo = {'PROVIDER': 'APIFY', 'ACTOR': ator, 'ROUTE': rota,
                   'MISSAO': missao, 'PROVIDER_SIDE_CAP': None,
                   'OUTCOME': None, 'COST_STATE': CUSTO_NAO_CORRIDO,
                   'ACTUAL_COST_USD': None}
        with self._trava:
            resto = max(0, self.limite_micros - self.exposto_micros)
            pedido_micros = _micros(pedido)
            cap = resto if pedido_micros is None else min(pedido_micros, resto)
            if cap <= 0:
                self.recusadas += 1
                registo.update({'OUTCOME': 'REFUSED_BY_FINANCIAL_BUDGET'})
                self.tentativas.append(registo)
                raise SemOrcamentoFinanceiro(
                    'orçamento financeiro esgotado: autorizado US$%s, exposto '
                    'US$%s (gasto US$%s + comprometido US$%s + desconhecido '
                    'US$%s), e esta chamada (%s) precisaria de mais.'
                    % (self.autorizado, _dolares(self.exposto_micros), self.gasto,
                       self.comprometido, self.desconhecido, ator or rota or '?'))
            self.comprometido_micros += cap
            registo['PROVIDER_SIDE_CAP'] = _dolares(cap)
            registo['OUTCOME'] = 'COMMITTED'
            self.tentativas.append(registo)
            return Reserva(self, cap, registo)

    def _fechar(self, reserva, custo_micros, anulada=None):
        with self._trava:
            if reserva.fechada:
                return reserva.registo
            reserva.fechada = True
            self.comprometido_micros -= reserva.cap_micros
            if custo_micros is None:
                # O dinheiro NÃO volta. Devolvê-lo deixaria a execução seguinte
                # gastar de novo aquilo que talvez já tenha saído.
                self.desconhecido_micros += reserva.cap_micros
                reserva.registo.update({'OUTCOME': 'UNKNOWN_COMMITMENT',
                                        'COST_STATE': CUSTO_DESCONHECIDO,
                                        'ACTUAL_COST_USD': None})
            else:
                self.gasto_micros += custo_micros
                reserva.registo.update(
                    {'OUTCOME': anulada or 'CLOSED_WITH_READ_COST',
                     'COST_STATE': (CUSTO_NAO_CORRIDO if anulada
                                    else CUSTO_LIDO),
                     'ACTUAL_COST_USD': _dolares(custo_micros)})
                if custo_micros > reserva.cap_micros:
                    # O provider cobrou acima do teto que lhe foi dado. Isso não
                    # é sucesso financeiro: é uma trava que não travou, e tem de
                    # aparecer como tal.
                    reserva.registo['OUTCOME'] = 'PROVIDER_EXCEEDED_CAP'
                    reserva.registo['PROVIDER_CAP_BREACH_USD'] = _dolares(
                        custo_micros - reserva.cap_micros)
            return reserva.registo

    def para_o_rasto(self):
        return {
            'FINANCIAL_BUDGET_AUTHORIZED_USD': self.autorizado,
            'FINANCIAL_BUDGET_COMMITTED_USD': self.comprometido,
            'FINANCIAL_BUDGET_ACTUAL_USD': self.gasto,
            'FINANCIAL_BUDGET_UNKNOWN_USD': self.desconhecido,
            'FINANCIAL_BUDGET_REMAINING_USD': self.restante,
            'FINANCIAL_BUDGET_EXHAUSTED': self.esgotado,
            'FINANCIAL_CALLS_REFUSED': self.recusadas,
            'FINANCIAL_ATTEMPTS': list(self.tentativas),
        }


def _orcamento_de_rede():
    """O teto de ACESSOS desta execucao, perguntado ao dono dele.

    Perguntado, e nao guardado: um saldo de rede copiado para ca seria um
    segundo contador, e dois contadores da mesma coisa divergem sempre.
    """
    try:
        import scrap_http as _http
    except ImportError:                                           # pragma: no cover
        return None
    return _http.orcamento_actual()


def orcamento_financeiro_actual():
    """O orçamento desta execução, ou None quando ninguém declarou um."""
    return getattr(_LOCAL, 'orcamento', None)


@contextlib.contextmanager
def orcamento_financeiro(limite):
    """Instala um teto de GASTO para o bloco inteiro.

    Ao contrário do teto de rede, aqui não há primitiva do Python a embrulhar: o
    ponto onde o dinheiro é comprometido é uma linha desta casa, e é chamada por
    nome. Um teto que se cobra onde o gasto nasce não precisa de armadilha.

    O objecto pode ser passado em vez do número — é assim que duas linhas de
    execução partilham o MESMO saldo em vez de cada uma ganhar o seu.
    """
    anterior = getattr(_LOCAL, 'orcamento', None)
    orc = (limite if isinstance(limite, OrcamentoFinanceiro)
           else OrcamentoFinanceiro(limite))
    _LOCAL.orcamento = orc
    try:
        yield orc
    finally:
        _LOCAL.orcamento = anterior


def _recusas_nossas():
    """As excecoes que sao RECUSA DESTA CASA, e nunca resposta da fonte."""
    try:
        import scrap_http as _http
        return (SemAutorizacaoDeGasto, SemOrcamentoFinanceiro,
                _http.SemOrcamentoDeRede)
    except ImportError:                                           # pragma: no cover
        return (SemAutorizacaoDeGasto, SemOrcamentoFinanceiro)


class PostTalvezCriado(RuntimeError):
    """O POST caiu no transporte e NÃO foi repetido — a execução pode existir mesmo assim.

    Existe para que a diferença entre "não pedi" e "pedi e não sei o que houve" tenha um
    tipo próprio. Tratar as duas como a mesma falha é o que faz alguém repetir o pedido e
    pagar duas vezes.
    """


def agora():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _curl(url, *, token, metodo='GET', corpo=None, timeout=300, tentativas=4):
    """Chama a API e devolve o JSON. Reexecuta quando o TUNEL cai, nunca quando a API recusa.

    Medido em 2026-08-29 neste ambiente: o proxy derruba conexoes no meio da troca
    (`ws_closed_mid_exchange`) e o curl volta 35/52/56 com stdout vazio. Sem retentativa,
    um POST perdido assim vira `status: None` no manifesto — indistinguivel de um ator que
    respondeu errado. A retentativa existe para que falha de TRANSPORTE nao seja lida como
    falha de ROTA. Um 4xx da propria Apify NAO e retentado: aquilo e resposta, nao queda.

    POST NAO E RETENTADO, E ISSO E UM CONSERTO DE 2026-09-02
    ---------------------------------------------------------
    A versao anterior repetia QUALQUER metodo ate 4 vezes — inclusive o POST que **cria a
    execucao paga**. E a propria docstring acima documenta que o proxy derruba conexoes no
    meio da troca.

    Junte as duas coisas: se o POST CHEGOU na Apify e so a RESPOSTA se perdeu na volta, a
    retentativa nao esta repetindo um pedido perdido — esta **acendendo uma segunda
    execucao paga**. A primeira fica orfa: sem run_id, sem manifesto, sem custo rastreado,
    e gastando. Com 4 tentativas, ate 4 execucoes por chamada.

        REPETIR UM GET E BARATO. REPETIR UM POST E COMPRAR DE NOVO.

    E o `maxTotalChargeUsd` nao protege disto: ele limita CADA execucao, nunca a soma das
    execucoes que ninguem sabe que existem.

    Entao: GET continua com retentativa; POST vai UMA vez. Se o transporte cair num POST,
    quem chama recebe `PostTalvezCriado` e decide — e `executar()` decide ADOTAR a execucao
    que possa ter nascido, em vez de acender outra.
    """
    cmd = ['curl', '-sS', '-X', metodo, '-H', 'Authorization: Bearer %s' % token]
    if corpo is not None:
        cmd += ['-H', 'Content-Type: application/json', '-d', json.dumps(corpo)]
    cmd.append(url)
    ultimo = ''
    vezes = 1 if metodo.upper() in ('POST', 'PUT', 'PATCH', 'DELETE') else tentativas
    for n in range(vezes):
        # ── ESTA PORTA TAMBEM CONTA PARA O TETO DE ACESSOS ────────────────────
        # A C10.8A-R cobrou o teto de rede em `urlopen` e `socket.create_connection`
        # porque as portas de Python desta casa passam todas por uma das duas.
        # ESTA nao passa: ela abre um PROCESSO `curl`. Medido na C10.8A-F, e por
        # isso escrito aqui em vez de presumido la.
        #
        #     UM TETO COBRADO NA PRIMITIVA NAO VE QUEM SAI POR UM SUBPROCESSO.
        #
        # O dono do conceito «rede» continua a ser `scrap_http`. Este ficheiro
        # nao conta nada: ele PEDE autorizacao a quem conta.
        _rede = _orcamento_de_rede()
        _registo_de_rede = None
        if _rede is not None:
            import scrap_http as _http
            _registo_de_rede = _rede.reservar(
                _http.PEDIDO_ROTA if n == 0 else _http.PEDIDO_RETENTATIVA, url)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if _registo_de_rede is not None:
            _registo_de_rede['OUTCOME'] = ('OK' if r.returncode == 0
                                           else 'CURL_%d' % r.returncode)
        if r.returncode == 0 and (r.stdout or '').strip():
            try:
                return json.loads(r.stdout)
            except ValueError:
                ultimo = 'resposta nao-JSON: %s' % (r.stdout or '')[:160]
        else:
            ultimo = 'curl rc=%s %s' % (r.returncode, (r.stderr or '')[:160])
        if n < vezes - 1:
            time.sleep(2 ** n)                    # 1s, 2s, 4s
    if vezes == 1:
        raise PostTalvezCriado(
            'o %s caiu no transporte e NAO foi repetido: %s. A execucao pode ter nascido '
            'do outro lado — repetir seria pagar duas vezes.' % (metodo, ultimo))
    raise RuntimeError('curl falhou apos %d tentativas: %s' % (vezes, ultimo))


#: O TRANSPORTE DESTA CASA, GUARDADO COM NOME.
#:
#: `regras/sensor_coleta.py` substitui `_curl` no import, e a troca e legitima:
#: o proxy deste ambiente derruba conexoes, e urllib sobrevive onde o
#: subprocesso nao sobrevive. O que NAO e legitimo e a troca ser invisivel.
#:
#:     UMA TROCA DE TRANSPORTE LEVA COM ELA AS LEIS QUE MORAVAM NO TRANSPORTE.
#:
#: Medido na SCRAP-SR-02: a substituicao tinha levado embora o teto de rede e a
#: regra de que o POST vai uma vez so. Com este nome, quem audita consegue
#: perguntar «este e o transporte da casa?» e quem testa consegue repo-lo.
_CURL_DA_CASA = _curl


def _ultima_execucao(actor, *, token, desde):
    """A execucao mais recente DESTE ator. Serve para ADOTAR um POST que talvez tenha nascido.

    Leitura, nao execucao: nao gasta e funciona com chave esgotada. `desde` e o carimbo de
    antes do POST — sem ele, adotar a "ultima" pegaria uma execucao antiga de outra coleta
    e o manifesto mentiria sobre o que produziu os itens.
    """
    try:
        d = _curl('%s/acts/%s/runs?desc=1&limit=3' % (API, actor), token=token, timeout=90)
    except Exception:                                        # noqa: BLE001
        return None
    for r in ((d or {}).get('data') or {}).get('items') or []:
        if (r.get('startedAt') or '') >= desde:
            return r
    return None


def _esperar_terminal(id_na_plataforma, *, token, segundos, intervalo=5):
    """Consulta a execução até ela ACABAR de verdade, ou até o tempo desta casa esgotar.

    Devolve `(objeto_da_execucao, alcancou_terminal, consultas)`.

    Consultar é leitura: não roda ator, não gasta, e funciona com chave esgotada. O que
    ela compra é a diferença entre "a execução terminou assim" e "a execução ainda estava
    correndo quando eu olhei" — que é a diferença entre um retrato e um retrato parcial.
    """
    fim = time.time() + max(0, segundos)
    d, consultas = {}, 0
    while True:
        r = _curl('%s/actor-runs/%s' % (API, id_na_plataforma), token=token, timeout=90)
        consultas += 1
        d = (r or {}).get('data') or d
        if d.get('status') in STATUS_TERMINAIS:
            return d, True, consultas
        if time.time() >= fim:
            return d, False, consultas
        time.sleep(min(intervalo, max(1, fim - time.time())))


def _requisicoes_falhadas(loja_kv, *, token):
    """→ (falhadas, terminadas) do rastreador, ou (NOT_PRESERVED, NOT_PRESERVED).

    Leitura grátis. Ausência do registro é `NOT_PRESERVED` — e ausência de prova de falha
    NUNCA vira prova de ausência de falha: quem chama trata os dois estados diferente.

    O NOME DA CHAVE NÃO É CHUTADO, E ISSO É UM CONSERTO
    ----------------------------------------------------
    A primeira versão pedia `SDK_CRAWLER_STATISTICS_0` direto. Esse nome é herança do SDK
    antigo: o Crawlee v4 renomeou para `CRAWLEE_CRAWLER_STATISTICS_{n}`, e o Crawlee em
    Python usa um terceiro nome, `__CRAWLER_STATISTICS_{id}`.

    No dia em que um ator atualizasse, a leitura devolveria `NOT_PRESERVED` **em silêncio**
    e a trava de `requestsFailed > 0` nunca mais dispararia. O caso medido — 107 de 161
    requisições falhadas com 708 itens devolvidos — voltaria a passar como SUCCESS.

        CHAVE CHUTADA QUE MUDA DE NOME É UMA TRAVA QUE SE DESLIGA SOZINHA.

    Então: listar as chaves da loja e pegar a que TERMINA em `CRAWLER_STATISTICS` ou tem
    esse trecho no meio, seja qual for o prefixo ou o sufixo numérico.
    """
    if not loja_kv:
        return pv.NOT_PRESERVED, pv.NOT_PRESERVED
    try:
        lista = _curl('%s/key-value-stores/%s/keys?limit=1000' % (API, loja_kv),
                      token=token, timeout=60, tentativas=2)
        chaves = [k.get('key') for k in
                  (((lista or {}).get('data') or {}).get('items') or [])]
        alvo = next((k for k in chaves if k and 'CRAWLER_STATISTICS' in k.upper()), None)
        if not alvo:
            return pv.NOT_PRESERVED, pv.NOT_PRESERVED
        d = _curl('%s/key-value-stores/%s/records/%s' % (API, loja_kv, alvo),
                  token=token, timeout=60, tentativas=2)
    except Exception:                                        # noqa: BLE001
        return pv.NOT_PRESERVED, pv.NOT_PRESERVED
    if not isinstance(d, dict):
        return pv.NOT_PRESERVED, pv.NOT_PRESERVED
    f, t = d.get('requestsFailed'), d.get('requestsFinished')
    return (f if isinstance(f, int) else pv.NOT_PRESERVED,
            t if isinstance(t, int) else pv.NOT_PRESERVED)


def executar(actor, entrada, *, token, run_id, platform, country, mission, query,
             source_version, evidence_path, wait=280, salvar_raw=True,
             teto_usd=None, build=None, rota=None,
             modo=az.NORMAL, autorizacao=None, source_id=None,
             proposito=None):
    """Roda um ator e devolve (itens_crus, manifesto). Grava o RAW antes de devolver.

    `token` nunca entra no manifesto: ele só existe no cabeçalho da chamada.

    `wait` é o tempo TOTAL que esta casa aceita esperar a execução acabar — não o que se
    pede à plataforma. À plataforma se pede 60 s, que é o máximo que ela concede; o resto
    é consulta ao estado da execução. Chamadores antigos passam `wait=280` e continuam
    esperando 280 s: o que muda é que agora eles esperam de verdade.

    `teto_usd` vira `&maxTotalChargeUsd=` e `build` vira `&build=`. Os dois são travas do
    lado da plataforma — valem mesmo que este arquivo tenha um defeito.

    QUANDO HÁ ORÇAMENTO FINANCEIRO DECLARADO
    ------------------------------------------
    `teto_usd` deixa de ser o que o chamador pediu e passa a ser o que CABE: ele é
    rebaixado ao saldo que resta, e a chamada que não couber morre aqui, antes do
    POST. Sem orçamento declarado nada muda — nem o `teto_usd`, nem o manifesto.

        PROVIDER CAP != EXECUTION BUDGET.
    """
    started = agora()
    # ── E ANTES DE TUDO: ALGUÉM AUTORIZOU ESTA COMPRA? ────────────────────────
    # Esta é a linha onde uma corrida paga nasce nesta árvore — a única. Quatro
    # sítios chamam esta função, e três deles saltam o roteador. Pôr a guarda
    # num caminho guardaria um caminho; pô-la aqui guarda todos.
    #
    #     UMA GUARDA QUE VIVE NA PRIMITIVA GUARDA TODOS OS CAMINHOS.
    #
    # `autorizacao=None` RECUSA, e é deliberado: um chamador novo que não saiba
    # desta lei não compra, em vez de comprar por omissão.
    #
    #     FAIL CLOSED. O SILÊNCIO NÃO AUTORIZA.
    #
    # E ela vem ANTES da reserva financeira de propósito. Reservar primeiro
    # comprometeria dinheiro por uma compra que nunca devia ter sido pensada —
    # e uma reserva que ninguém liquidou não volta ao bolso.
    recibo = az.pode_comprar(modo=modo, autorizacao=autorizacao,
                             source_id=source_id, proposito=proposito,
                             ator=actor)
    # ── O GATE FINANCEIRO VEM ANTES DO POST ───────────────────────────────────
    # Cobrar depois do provider é contar o prejuízo. A reserva acontece aqui, e é
    # ela que decide o `maxTotalChargeUsd` que vai na query.
    orcamento = orcamento_financeiro_actual()
    reserva = None
    if orcamento is not None:
        reserva = orcamento.reservar(pedido=teto_usd, ator=actor,
                                     rota=rota or evidence_path, missao=mission)
        teto_usd = reserva.cap
    try:
        params = ['waitForFinish=%d' % min(int(wait), ESPERA_MAXIMA_DA_PLATAFORMA)]
        if teto_usd is not None:
            params.append('maxTotalChargeUsd=%s' % teto_usd)
        if build:
            params.append('build=%s' % build)
        adotada = 'NO'
        try:
            run = _curl('%s/acts/%s/runs?%s' % (API, actor, '&'.join(params)),
                        token=token, metodo='POST', corpo=entrada,
                        timeout=ESPERA_MAXIMA_DA_PLATAFORMA + 40)
        except PostTalvezCriado as e:
            # O pedido pode ter chegado. ADOTAR a execução que nasceu é a única saída que
            # não paga duas vezes — e se não nasceu nenhuma, a falha continua sendo falha.
            achada = _ultima_execucao(actor, token=token, desde=started)
            if not achada:
                # NÃO se conclui «não gastou». Não ter ACHADO execução é uma
                # leitura, não uma prova — e o dinheiro que ficou comprometido
                # continua comprometido.
                #
                #     POTENTIAL COMMITMENT != NOTHING HAPPENED.
                if reserva is not None:
                    reserva.desconhecer()
                raise RuntimeError('%s — e nenhuma execução deste ator nasceu depois de %s, '
                                   'então o pedido não chegou.' % (e, started))
            run, adotada = {'data': achada}, 'YES'
            print('      POST caiu no transporte; ADOTEI a execução %s que já existia '
                  '(em vez de acender outra e pagar duas vezes)' % achada.get('id'))
        # A API recusa entrada invalida com {"error": {...}} e SEM `data`. Sem este ramo o
        # manifesto registrava `status: None` — que se le como ator mudo, quando na verdade
        # a plataforma respondeu e disse exatamente o que estava errado. Recusa da API e
        # RESPOSTA, e precisa aparecer como tal.
        if run.get('error'):
            e = run['error']
            # A plataforma RESPONDEU e não criou execução nenhuma. Este é o único
            # caso em que o dinheiro volta inteiro ao saldo — porque houve prova
            # de que não houve corrida, e não apenas ausência de notícia.
            if reserva is not None:
                reserva.anular('API_REFUSED_NO_RUN_CREATED')
            raise RuntimeError('API recusou: %s — %s' % (e.get('type'), str(e.get('message'))[:300]))
        d = run.get('data') or {}

        # A plataforma respondeu aos 60 s. Se a execução ainda não acabou, ESPERAR — ler o
        # dataset agora seria fotografar uma coleta pela metade. Só depois disto o dataset
        # pode ser lido.
        terminal, consultas = d.get('status') in STATUS_TERMINAIS, 0
        if not terminal and d.get('id'):
            restante = int(wait) - ESPERA_MAXIMA_DA_PLATAFORMA
            d2, terminal, consultas = _esperar_terminal(
                d['id'], token=token, segundos=restante)
            d = d2 or d

        dataset = d.get('defaultDatasetId')
        itens = []
        if dataset:
            itens = _curl('%s/datasets/%s/items?clean=true' % (API, dataset),
                          token=token, timeout=180)

        # Contagem de item NÃO detecta perda. Esta leitura é grátis e é a única que pega o
        # caso medido de 107 requisições falhadas em 161 com 708 itens devolvidos.
        falhadas, terminadas = _requisicoes_falhadas(
            d.get('defaultKeyValueStoreId'), token=token)

        # `SUCCEEDED` da plataforma NAO basta. Medido em 2026-08-29: o ator devolveu
        # SUCCEEDED, exitCode limpo e ZERO itens, com statusMessage "free user run limit
        # reached". Uma cota esgotada que se apresenta como sucesso e exatamente o caso de
        # "nenhum resultado do Actor != nenhum resultado na plataforma". Registrar isso como
        # SUCCESS faria uma coleta vazia parecer uma coleta bem-sucedida.
        msg = d.get('statusMessage') or ''
        if not terminal:
            # O caso novo, e o mais perigoso dos três: a execução NÃO acabou. Os itens que
            # vieram são um pedaço legítimo, e é exatamente por isso que não podem passar
            # por coleta inteira.
            status = 'PARTIAL'
            erro = ('execução NÃO chegou a status terminal em %ds (status: %s, %d '
                    'consultas). Os %d itens são um retrato parcial de uma coleta que '
                    'ainda estava correndo. %s'
                    % (int(wait), d.get('status'), consultas, len(itens), msg))
        elif d.get('status') != 'SUCCEEDED':
            status = 'FAILED' if d.get('status') in ('FAILED', 'ABORTED', 'TIMED-OUT') else 'PARTIAL'
            erro = 'status da plataforma: %s. %s' % (d.get('status'), msg)
        elif not itens:
            status = 'PARTIAL'
            erro = ('SUCCEEDED com ZERO itens — degradacao que se apresenta como sucesso. '
                    'statusMessage: %s' % (msg or 'nenhuma'))
        elif isinstance(falhadas, int) and falhadas > 0:
            status = 'PARTIAL'
            erro = ('SUCCEEDED com %d de %s requisições FALHADAS — vieram %d itens e o '
                    'buraco não aparece na contagem. statusMessage: %s'
                    % (falhadas, terminadas, len(itens), msg or 'nenhuma'))
        else:
            status = 'SUCCESS'
            erro = ('statusMessage: %s' % msg) if msg else pv.NOT_PRESERVED
    except _recusas_nossas():
        # TERCEIRA vez nesta cadeia que um `except` largo veste uma recusa NOSSA
        # com a roupa da fonte. Um teto que devolve `STATUS: FAILED` faz o
        # manifesto dizer que a Apify falhou quando fomos nos que nao deixamos
        # sair.
        #
        #     UM `except Exception` LARGO NAO DISTINGUE QUEM DISSE NAO.
        #
        # E se o teto de REDE recusou, o POST provadamente nao saiu: o dinheiro
        # reservado volta inteiro. Este e o outro caso — com prova — em que ele
        # volta.
        if reserva is not None and not reserva.fechada:
            reserva.anular('REFUSED_BY_NETWORK_BUDGET_NO_POST_SENT')
        raise
    except Exception as e:                                   # falha é estado, não zero
        d, dataset, itens = {}, None, []
        terminal, consultas, adotada = False, 0, 'NO'
        falhadas, terminadas = pv.NOT_PRESERVED, pv.NOT_PRESERVED
        status, erro = 'FAILED', '%s: %s' % (type(e).__name__, str(e)[:180])

    # Zero item NAO e "nada para preservar": e a prova de que a rota devolveu vazio.
    # Confundir os dois faria uma execucao bem-sucedida e vazia parecer uma execucao cujo
    # bruto se perdeu — que e justamente a distincao que este arquivo existe para manter.
    raw_path, raw_state = pv.NOT_PRESERVED, 'NOT_PRESERVED'
    raw_sha = pv.NOT_PRESERVED
    if salvar_raw and status != 'FAILED':
        os.makedirs(RAW_DIR, exist_ok=True)
        nome = '%s.raw.json.gz' % run_id
        # O SHA-256 sai do CONTEÚDO canônico, não do arquivo .gz: gzip carimba a hora
        # dentro do arquivo, então dois arquivos com os mesmos itens teriam somas
        # diferentes — uma impressão digital que muda sozinha não identifica nada.
        canonico = json.dumps(itens, ensure_ascii=False, sort_keys=True).encode('utf-8')
        raw_sha = hashlib.sha256(canonico).hexdigest()
        with gzip.open(os.path.join(RAW_DIR, nome), 'wt', encoding='utf-8', compresslevel=9) as f:
            json.dump(itens, f, ensure_ascii=False)          # RAW gravado ANTES de normalizar
        raw_path = 'data/samples/raw-paid/' + nome
        raw_state = 'PRESERVED'
        # ── O BRUTO PAGO ENTRA NO INVENTARIO DA CORRIDA ───────────────────
        # Ele e gravado aqui, com gzip e SHA proprios — este ficheiro e o dono
        # desse formato. Mas quem empacota a evidencia para atravessar a
        # fronteira do job le `social_envelope.produzidos()`, e ate a C10.8B-R
        # o bruto pago nao estava la. Resultado medido na C10.8B-LIVE: 59.743
        # bytes escritos, relidos, assinados — e apagados pelo checkout
        # seguinte, sem ninguem os ter visto.
        #
        #     O QUE O INVENTARIO NAO VE NAO ATRAVESSA A FRONTEIRA DO JOB.
        try:
            import social_envelope as _env
            _env.registar_produzido(os.path.join(RAW_DIR, nome))
        except ImportError:                                       # pragma: no cover
            pass

    manifesto = pv.novo_run(
        run_id, PLATFORM=platform, ACTOR=actor,
        ACTOR_VERSION=d.get('buildNumber') or d.get('buildId') or pv.NOT_PRESERVED,
        STARTED_AT=d.get('startedAt') or started,
        FINISHED_AT=d.get('finishedAt') or agora(),
        INPUT=entrada, COUNTRY=country, MISSION=mission, QUERY=query,
        DATASET_ID=dataset or pv.NOT_PRESERVED,
        ITEM_COUNT_RAW=len(itens), ITEM_COUNT_NORMALIZED=pv.NOT_PRESERVED,
        COST_USD=(d.get('usageTotalUsd') if d.get('usageTotalUsd') is not None
                  else pv.NOT_PRESERVED),
        SOURCE_VERSION=source_version, STATUS=status, ERROR=erro,
        CAPTURE_METHOD=('POST /acts/{actor}/runs?waitForFinish=60 + GET /actor-runs/{id} '
                        'até status terminal + GET /datasets/{id}/items'),
        EVIDENCE_PATH=evidence_path, RAW_EVIDENCE_PATH=raw_path,
        RAW_EVIDENCE_STATE=raw_state, OUTPUT_WRITTEN_AT=agora())

    # Campos FORA do contrato de `CAMPOS_RUN`, de propósito: acrescentá-los ao contrato
    # obrigaria todo manifesto antigo já gravado a tê-los, e `pv.gravar()` reprovaria a
    # regravação do arquivo inteiro. Chave a mais é aceita; chave a menos, não.
    manifesto['PLATFORM_STATUS'] = d.get('status') or pv.NOT_PRESERVED
    manifesto['RUN_REACHED_TERMINAL'] = 'YES' if terminal else 'NO'
    manifesto['STATUS_POLLS'] = consultas
    # A cadeia de proveniência ganha impressão digital. Até 2026-09-02 ela era feita só de
    # CAMINHO e RÓTULO: nada provava que o arquivo em `RAW_EVIDENCE_PATH` ainda é o que a
    # execução produziu. `apify_recuperar.py` (a porta de recuperação, removida em 2026-09-09) já gravava
    # `RAW_SHA256`; a porta PRINCIPAL não gravava — duas portas, dois contratos.
    manifesto['RAW_SHA256'] = raw_sha
    manifesto['RAW_SHA256_OF'] = ('json.dumps(itens, sort_keys=True) em UTF-8 — o CONTEÚDO, '
                                  'não o .gz (gzip carimba a hora e mudaria a soma sozinho)')
    manifesto['RUN_ADOPTED_AFTER_TRANSPORT_LOSS'] = adotada
    manifesto['REQUESTS_STATS_KEY_HOW'] = ('chave que contém CRAWLER_STATISTICS, achada por '
                                           'listagem — o nome muda entre versões do Crawlee')
    manifesto['REQUESTS_FAILED'] = falhadas
    manifesto['REQUESTS_FINISHED'] = terminadas
    manifesto['MAX_TOTAL_CHARGE_USD'] = teto_usd if teto_usd is not None else pv.NOT_PRESERVED
    manifesto['BUILD_PINNED'] = build or pv.NOT_PRESERVED
    # O custo lido AGORA vem 0 enquanto a Apify não fecha a conta da execução. Já custou
    # 5,6x uma vez (US$0,90 anunciados, US$5,04 reais). Ele fica gravado, mas ROTULADO:
    # quem publicar número sem liquidar está publicando o número errado.
    manifesto['COST_STATE'] = 'NOT_SETTLED'
    manifesto['COST_SETTLE_HOW'] = ('GET /v2/actor-runs casado por DATASET_ID. '
                                    'Ver provas/corrigir_custo.py')
    # O bruto EXISTE em disco (por isso PRESERVED), mas pode ser o retrato de uma execução
    # que não acabou. São duas perguntas diferentes e cada uma tem seu campo.
    manifesto['RAW_COMPLETENESS'] = ('RUN_REACHED_TERMINAL_STATUS' if terminal
                                     else 'PARTIAL_RUN_WAS_NOT_TERMINAL')

    # ── A RESERVA FECHA-SE COM O QUE SE CONSEGUIU LER, E SÓ COM ISSO ──────────
    # `usageTotalUsd` ausente NÃO é gasto zero: é gasto que não se leu. Fechar a
    # reserva como zero devolveria ao saldo dinheiro que pode ter saído — e a
    # execução seguinte gastá-lo-ia outra vez.
    #
    #     UNKNOWN COST != ZERO COST.
    #
    # Uma reserva que chegasse aqui por fechar seria dinheiro sem dono, então o
    # caminho por omissão é o conservador: sem número lido, fica `UNKNOWN`.
    if reserva is not None:
        if not reserva.fechada:
            lido = d.get('usageTotalUsd') if isinstance(d, dict) else None
            reserva.liquidar(lido if isinstance(lido, (int, float)) else None)
        # E ela sobe para o manifesto ESTEJA ELA FECHADA OU NAO. A versao
        # anterior so a anexava quando fechava AQUI — e o caso em que ela fecha
        # antes e justamente o pior de todos: o POST caiu no transporte, o
        # dinheiro ficou em UNKNOWN, e o manifesto nao dizia nada. Quem lesse
        # via `NOT_RUN`, que e a unica coisa que aquele momento nao foi.
        #
        #     UMA RESERVA QUE NAO SOBE AO MANIFESTO DEIXA O RASTO DIZER
        #     «NAO CORREU» SOBRE UMA COMPRA QUE TALVEZ TENHA ACONTECIDO.
        manifesto['FINANCIAL_RESERVATION'] = dict(reserva.registo)
    # O RECIBO DA AUTORIZACAO viaja com o manifesto. Sem ele, ler o artefato
    # diria quanto se gastou e nunca quem tinha deixado.
    #
    #     CAN DO != DID DO — e um artefato que nao diz quem autorizou
    #     obriga quem audita a acreditar.
    manifesto['SPEND_AUTHORIZATION'] = dict(recibo)

    pv.checar_token(manifesto)
    return itens, manifesto


def registrar(manifesto, *, item_count_normalized=None):
    """Acrescenta a execução ao manifesto persistido, sem apagar as anteriores."""
    if item_count_normalized is not None:
        manifesto['ITEM_COUNT_NORMALIZED'] = item_count_normalized
    runs = pv.carregar()
    runs[manifesto['RUN_ID']] = manifesto
    pv.gravar([runs[k] for k in sorted(runs)], captured_at=agora()[:10])
    return manifesto


if __name__ == '__main__':
    print('coletor — porta única das rotas pagas')
    print('campos capturados por execução:', len(pv.CAMPOS_RUN))
    print('RAW gravado ANTES da normalização, em', os.path.relpath(RAW_DIR, ROOT))
