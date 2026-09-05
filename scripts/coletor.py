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
sys.path.insert(0, HERE)
import proveniencia as pv  # noqa: E402

RAW_DIR = os.path.join(ROOT, 'data', 'samples', 'raw-paid')
API = 'https://api.apify.com/v2'

# Teto documentado do `waitForFinish`. Pedir mais não compra mais — só faz a resposta
# parecer conclusiva quando não é.
ESPERA_MAXIMA_DA_PLATAFORMA = 60

# Status em que a execução ACABOU. Todo o resto é "ainda está acontecendo".
STATUS_TERMINAIS = ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT')
STATUS_TRANSITORIOS = ('READY', 'RUNNING', 'ABORTING')


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
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
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
             teto_usd=None, build=None):
    """Roda um ator e devolve (itens_crus, manifesto). Grava o RAW antes de devolver.

    `token` nunca entra no manifesto: ele só existe no cabeçalho da chamada.

    `wait` é o tempo TOTAL que esta casa aceita esperar a execução acabar — não o que se
    pede à plataforma. À plataforma se pede 60 s, que é o máximo que ela concede; o resto
    é consulta ao estado da execução. Chamadores antigos passam `wait=280` e continuam
    esperando 280 s: o que muda é que agora eles esperam de verdade.

    `teto_usd` vira `&maxTotalChargeUsd=` e `build` vira `&build=`. Os dois são travas do
    lado da plataforma — valem mesmo que este arquivo tenha um defeito.
    """
    started = agora()
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

    manifesto = pv.novo_run(
        run_id, PLATFORM=platform, ACTOR=actor,
        ACTOR_VERSION=d.get('buildNumber') or d.get('buildId') or pv.NOT_PRESERVED,
        # HORA SÓ DA PLATAFORMA. O fallback anterior era `or started` / `or agora()`, e
        # `started` é a hora LOCAL de quando o coletor começou a chamar. Numa execução que
        # falha, a plataforma não devolve `data` — e o manifesto passava a registrar a
        # hora local como se fosse a hora de execução. É exatamente a promoção que a lei
        # desta casa proíbe, e foi um teste do próprio repositório que a flagrou nas
        # execuções falhas do piloto de sensores.
        #
        #     HORA DE ESCRITA != HORA DE EXECUÇÃO, inclusive quando a execução falhou.
        #
        # Sem hora medida, `NOT_PRESERVED` — e `pv.ordem()` devolve NAO_DIZIVEL, que é a
        # resposta certa. A hora local continua guardada, no campo dela: OUTPUT_WRITTEN_AT.
        STARTED_AT=d.get('startedAt') or pv.NOT_PRESERVED,
        FINISHED_AT=d.get('finishedAt') or pv.NOT_PRESERVED,
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
    # execução produziu. `apify_recuperar.py` (a porta de recuperação) já gravava
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
                                    'Ver scripts/corrigir_custo.py')
    # O bruto EXISTE em disco (por isso PRESERVED), mas pode ser o retrato de uma execução
    # que não acabou. São duas perguntas diferentes e cada uma tem seu campo.
    manifesto['RAW_COMPLETENESS'] = ('RUN_REACHED_TERMINAL_STATUS' if terminal
                                     else 'PARTIAL_RUN_WAS_NOT_TERMINAL')
    pv.checar_token(manifesto)
    return itens, manifesto


def registrar(manifesto, *, item_count_normalized=None, reconciliar=False):
    """Grava a execução como FRAGMENTO PRÓPRIO, sob a pasta do dono dela.

    A versão anterior lia o manifesto global inteiro, acrescentava uma linha e reescrevia
    o arquivo todo. Com uma missão só, funcionava. Com duas rodando nos mesmos runners,
    virou o defeito: dois processos reescrevendo o mesmo arquivo global deram
    `CONFLICT (content)` num rebase, o rebase parou no meio, e 29 candidatos JÁ PAGOS
    ficaram na máquina sem chegar ao repositório.

        DINHEIRO GASTO != DADO PRESERVADO.

    Agora cada execução escreve `data/runs/<DONO>/<RUN_ID>.json`, de forma atômica. Dois
    donos não compartilham caminho, então não há concorrência a gerenciar — ela deixa de
    existir. O índice global vira uma VISTA, reconstruível por `pv.reconciliar()`.

    `reconciliar=True` refaz o índice global na hora, e fica DESLIGADO por padrão de
    propósito: reconciliar dentro de uma coleta paralela reintroduziria exatamente a
    escrita concorrente que este arquivo passou a evitar. Reconciliação é passo
    serializado, feito depois, por quem consolida.
    """
    if item_count_normalized is not None:
        manifesto['ITEM_COUNT_NORMALIZED'] = item_count_normalized
    if manifesto.get('DATASET_OWNER') in (None, '', pv.NOT_PRESERVED):
        manifesto['DATASET_OWNER'] = pv.dono_da_missao(manifesto.get('MISSION'))
    pv.gravar_fragmento(manifesto)
    if reconciliar:
        pv.reconciliar(agora()[:10])
    return manifesto


if __name__ == '__main__':
    print('coletor — porta única das rotas pagas')
    print('campos capturados por execução:', len(pv.CAMPOS_RUN))
    print('RAW gravado ANTES da normalização, em', os.path.relpath(RAW_DIR, ROOT))
