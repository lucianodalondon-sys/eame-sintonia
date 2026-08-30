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
"""
import datetime
import gzip
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import proveniencia as pv  # noqa: E402

RAW_DIR = os.path.join(ROOT, 'data', 'samples', 'raw-paid')
API = 'https://api.apify.com/v2'


def agora():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _curl(url, *, token, metodo='GET', corpo=None, timeout=300):
    cmd = ['curl', '-sS', '-X', metodo, '-H', 'Authorization: Bearer %s' % token]
    if corpo is not None:
        cmd += ['-H', 'Content-Type: application/json', '-d', json.dumps(corpo)]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError('curl falhou: %s' % r.stderr[:200])
    return json.loads(r.stdout)


def executar(actor, entrada, *, token, run_id, platform, country, mission, query,
             source_version, evidence_path, wait=280, salvar_raw=True):
    """Roda um ator e devolve (itens_crus, manifesto). Grava o RAW antes de devolver.

    `token` nunca entra no manifesto: ele só existe no cabeçalho da chamada.
    """
    started = agora()
    try:
        run = _curl('%s/acts/%s/runs?waitForFinish=%d' % (API, actor, wait),
                    token=token, metodo='POST', corpo=entrada, timeout=wait + 40)
        d = run.get('data') or {}
        dataset = d.get('defaultDatasetId')
        itens = []
        if dataset:
            itens = _curl('%s/datasets/%s/items?clean=true' % (API, dataset),
                          token=token, timeout=180)
        # `SUCCEEDED` da plataforma NAO basta. Medido em 2026-08-29: o ator devolveu
        # SUCCEEDED, exitCode limpo e ZERO itens, com statusMessage "free user run limit
        # reached". Uma cota esgotada que se apresenta como sucesso e exatamente o caso de
        # "nenhum resultado do Actor != nenhum resultado na plataforma". Registrar isso como
        # SUCCESS faria uma coleta vazia parecer uma coleta bem-sucedida.
        msg = d.get('statusMessage') or ''
        if d.get('status') != 'SUCCEEDED':
            status = 'FAILED' if d.get('status') in ('FAILED', 'ABORTED', 'TIMED-OUT') else 'PARTIAL'
            erro = 'status da plataforma: %s. %s' % (d.get('status'), msg)
        elif not itens:
            status = 'PARTIAL'
            erro = ('SUCCEEDED com ZERO itens — degradacao que se apresenta como sucesso. '
                    'statusMessage: %s' % (msg or 'nenhuma'))
        else:
            status = 'SUCCESS'
            erro = ('statusMessage: %s' % msg) if msg else pv.NOT_PRESERVED
    except Exception as e:                                   # falha é estado, não zero
        d, dataset, itens = {}, None, []
        status, erro = 'FAILED', '%s: %s' % (type(e).__name__, str(e)[:180])

    # Zero item NAO e "nada para preservar": e a prova de que a rota devolveu vazio.
    # Confundir os dois faria uma execucao bem-sucedida e vazia parecer uma execucao cujo
    # bruto se perdeu — que e justamente a distincao que este arquivo existe para manter.
    raw_path, raw_state = pv.NOT_PRESERVED, 'NOT_PRESERVED'
    if salvar_raw and status != 'FAILED':
        os.makedirs(RAW_DIR, exist_ok=True)
        nome = '%s.raw.json.gz' % run_id
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
        CAPTURE_METHOD='POST /acts/{actor}/runs?waitForFinish + GET /datasets/{id}/items',
        EVIDENCE_PATH=evidence_path, RAW_EVIDENCE_PATH=raw_path,
        RAW_EVIDENCE_STATE=raw_state, OUTPUT_WRITTEN_AT=agora())
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
