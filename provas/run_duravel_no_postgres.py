#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""C10.6B — A PROVA QUE PRECISA DE UM POSTGRES DE VERDADE E DE UMA MORTE DE VERDADE.

    BANCO_DESCARTAVEL_URL=postgresql://... py provas/run_duravel_no_postgres.py

O que esta prova mede, e que nenhum teste de contrato consegue medir:

    F0  RUN e checkpoint abertos, morte antes da primeira etapa
    F1  uma etapa RUNNING, morte antes de produzir artefato
    F2  RAW persistido, morte antes de DERIVED
    F3  morte DENTRO da derivação
    F4  DERIVED persistido, morte antes de fechar RUN e checkpoint
    OK  o fluxo termina normalmente

Depois de cada morte, um PROCESSO NOVO com uma LIGAÇÃO NOVA pergunta ao banco o
que aconteceu. Ele não recebe variável, não lê ficheiro temporário do morto, não
herda objeto.

    PROCESS DEATH != EXCEPTION.
    A MORTE É `os._exit(97)`: sem `finally`, sem `atexit`, sem flush.

RECUSA-SE A CORRER CONTRA QUALQUER COISA QUE NÃO SEJA LOCAL. Um endereço que não
seja visivelmente descartável para esta prova — e uma prova que possa tocar
produção não é uma prova, é um risco.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

DSN = (os.environ.get('BANCO_DESCARTAVEL_URL') or '').strip()
LOCAL = ('localhost', '127.0.0.1', '::1', '@postgres', '/var/run/postgresql')

FILHO = os.path.join(RAIZ, 'provas', '_c106b_filho.py')


def _local(dsn):
    return bool(dsn) and any(m in dsn for m in LOCAL)


def main():
    if not DSN:
        print('BANCO_DESCARTAVEL_URL ausente — esta prova nao inventa banco.')
        print('RUN_DURAVEL=NOT_RUN')
        return 0
    if not _local(DSN):
        print('BANCO_DESCARTAVEL_URL nao parece local. Esta prova MATA processos '
              'e escreve linhas: ela nao corre contra o que nao consegue provar '
              'que e descartavel.')
        print('RUN_DURAVEL=RECUSADA_ENDERECO_NAO_LOCAL')
        return 1

    import coleta_checkpoint as ck
    import falhas as fx
    banco = ck.Banco(DSN)
    try:
        banco.executa("select 1 from public.checkpoint_coleta limit 1")
        banco.executa("select 1 from public.etapa_da_corrida limit 1")
    except Exception as e:                                        # noqa: BLE001
        print('schema ausente (%s). A cadeia de migrations tem de correr antes.'
              % type(e).__name__)
        print('RUN_DURAVEL=NOT_RUN')
        return 0

    falhas_ = []
    print('═══ F0–F4 · MORTE REAL, PROCESSO NOVO, SO O BANCO ═══')
    for ponto in ('F0', 'F1', 'F2', 'F3', 'F4'):
        alvo = 'PROVA-%s' % ponto
        r = subprocess.run([sys.executable, FILHO, ponto, alvo, 'RUN-%s' % ponto],
                           cwd=RAIZ, capture_output=True, text=True, timeout=600,
                           env=dict(os.environ))
        morreu = r.returncode == 97
        print('%-3s exit=%-4s %s' % (ponto, r.returncode,
                                     'morreu de verdade' if morreu
                                     else 'NAO MORREU: ' + (r.stderr or '')[:120]))
        if not morreu:
            falhas_.append('%s nao morreu' % ponto)
            continue

        # ── O PROCESSO NOVO ─────────────────────────────────────────────────
        b2 = ck.Banco(DSN)
        target = 'PROVA/unidade/%s' % alvo
        entrada = {'PLATFORM': 'PROVA', 'EXTERNAL_ID': alvo, 'CAPABILITY': 'FETCH'}
        est = ck.estado_duravel(b2, target=target, entrada=entrada)
        cp, corridas = est['CHECKPOINT'], est['CORRIDAS']
        todas = [p for ps in est['PASSAGENS'].values() for p in ps]
        if cp is None:
            falhas_.append('%s: o processo novo nao viu checkpoint nenhum' % ponto)
            continue
        if not corridas:
            falhas_.append('%s: o processo novo nao viu a corrida morta' % ponto)
            continue
        if corridas[0]['STATUS'] != 'rodando':
            falhas_.append('%s: alguem fechou a corrida morta (%s)'
                           % (ponto, corridas[0]['STATUS']))
        esperadas = {'F0': 0, 'F1': 1, 'F2': 2, 'F3': 3, 'F4': 3}[ponto]
        if len(todas) != esperadas:
            falhas_.append('%s: esperava %d passagem(ns), ha %d'
                           % (ponto, esperadas, len(todas)))
        penduradas = est['ETAPAS_PENDURADAS']
        deve_pendurar = ponto in ('F1', 'F3')
        if bool(penduradas) != deve_pendurar:
            falhas_.append('%s: etapa pendurada=%s, esperado=%s'
                           % (ponto, bool(penduradas), deve_pendurar))
        print('    checkpoint=%s/%s corrida=%s passagens=%d penduradas=%d'
              % (cp['ID'], cp['ESTADO'], corridas[0]['STATUS'], len(todas),
                 len(penduradas)))

    # ── F4 · DERIVED EXISTE E A RUN NAO ESTA CONCLUIDA ────────────────────
    print()
    print('═══ F4 · `DERIVED EXISTS != RUN COMPLETED` ═══')
    b3 = ck.Banco(DSN)
    l = b3.executa(
        "select r.status::text, coalesce(c.estado,'-'), c.unidades_feitas::text,"
        " coalesce((select estado::text from public.etapa_da_corrida"
        "   where run_id='RUN-F4' and etapa='DERIVED' order by tentativa desc"
        "   limit 1),'-')"
        " from public.collection_run r join public.checkpoint_coleta c"
        " on c.id = r.checkpoint_id where r.run_id = 'RUN-F4'")
    if not l or not l[0] or len(l[0]) < 4:
        falhas_.append('F4: nao consegui ler o estado final')
    else:
        status, cpe, feitas, der = l[0][:4]
        print('    DERIVED (etapa)              = %s' % der)
        print('    OLD_RUN_COMPLETED            = %s' % ('NO' if status == 'rodando' else status))
        print('    CHECKPOINT_COMPLETED         = %s' % ('NO' if cpe != 'CONCLUIDO' else 'YES'))
        if der != 'PASS':
            falhas_.append('F4: a derivacao nao chegou a passar; F4 nao mediu o que devia')
        if status != 'rodando' or cpe == 'CONCLUIDO' or feitas != '0':
            falhas_.append('F4: um DERIVED no disco promoveu a corrida a concluida')

    # ── A RETOMADA ────────────────────────────────────────────────────────
    print()
    print('═══ FASE 16 · RETOMADA: NOVA RUN, MESMO CHECKPOINT ═══')
    r = subprocess.run([sys.executable, FILHO, 'RETOMAR', 'PROVA-F4', 'RUN-F4-B'],
                       cwd=RAIZ, capture_output=True, text=True, timeout=600,
                       env=dict(os.environ))
    print((r.stdout or r.stderr).strip()[-600:])
    if r.returncode != 0:
        falhas_.append('a retomada nao correu: %s' % (r.stderr or '')[:200])
    else:
        b4 = ck.Banco(DSN)
        runs = b4.executa(
            "select r.run_id, r.status::text from public.collection_run r"
            " join public.checkpoint_coleta c on c.id = r.checkpoint_id"
            " where c.collection_target = 'PROVA/unidade/PROVA-F4' order by r.run_id")
        nomes = {x[0]: x[1] for x in runs if x and x[0]}
        print('    corridas no mesmo checkpoint = %s' % nomes)
        if 'RUN-F4' not in nomes:
            falhas_.append('a corrida morta desapareceu na retomada')
        if 'RUN-F4-B' not in nomes:
            falhas_.append('a retomada nao criou corrida nova')
        if nomes.get('RUN-F4') != 'rodando':
            falhas_.append('a retomada reescreveu a corrida morta')

    # ══════════════════════════════════════════════════════════════════════
    # AS INVARIANTES, AFIRMADAS — NAO IMPRESSAS
    # ══════════════════════════════════════════════════════════════════════
    # Ate aqui a prova IMPRIMIA o estado e passava. Doze mutacoes mostraram o
    # preco disso: nove sobreviveram, porque nada exigia que o estado fosse
    # aquele. Imprimir nao e afirmar.
    #
    #     UMA PROVA QUE MOSTRA O NUMERO E NAO O EXIGE MEDE O ECRA.
    print()
    print('═══ AS INVARIANTES ═══')
    b5 = ck.Banco(DSN)

    def correr(ponto, unidade, run, espera=0):
        r_ = subprocess.run([sys.executable, FILHO, ponto, unidade, run],
                            cwd=RAIZ, capture_output=True, text=True, timeout=600,
                            env=dict(os.environ))
        if r_.returncode != espera:
            falhas_.append('%s: exit %s (esperado %s) %s'
                           % (ponto, r_.returncode, espera, (r_.stderr or '')[:160]))
        return r_

    def uma(sql):
        l_ = b5.executa(sql)
        return l_[0][0] if l_ and l_[0] else None

    # ── I1 · FALHA NAO ANDA COM O CHECKPOINT ────────────────────────────────
    # `PERSIST FIRST, THEN ADVANCE` tem uma metade que ninguem olha: quando NAO
    # se persistiu, o checkpoint nao pode andar. Um `unidades_feitas = 1` aqui
    # faria a proxima execucao pular uma unidade que ninguem guardou.
    correr('FERR', 'PROVA-ERR', 'RUN-ERR')
    cp_err = uma("select estado from public.checkpoint_coleta"
                 " where collection_target = 'PROVA/unidade/PROVA-ERR'")
    feitas_err = uma("select unidades_feitas::text from public.checkpoint_coleta"
                     " where collection_target = 'PROVA/unidade/PROVA-ERR'")
    itens_err = uma("select itens_persistidos::text from public.checkpoint_coleta"
                    " where collection_target = 'PROVA/unidade/PROVA-ERR'")
    st_err = uma("select status::text from public.collection_run where run_id='RUN-ERR'")
    print('I1 falha: checkpoint=%s feitas=%s itens=%s run=%s'
          % (cp_err, feitas_err, itens_err, st_err))
    if cp_err == 'CONCLUIDO' or feitas_err != '0' or itens_err != '0':
        falhas_.append('I1: o checkpoint andou numa unidade que falhou')
    if st_err not in ('falhou', 'parcial'):
        falhas_.append('I1: a corrida que falhou fechou como %s' % st_err)

    # ── I2 · A ETAPA `FAIL` FICA, COM CODIGO ────────────────────────────────
    diag = uma("select coalesce(diagnostic_code,'-') from public.etapa_da_corrida"
               " where run_id = 'RUN-ERR' and estado = 'FAIL'")
    canon = uma("select coalesce(canonical_state,'-') from public.etapa_da_corrida"
                " where run_id = 'RUN-ERR' and estado = 'FAIL'")
    http = uma("select coalesce(http_status::text,'-') from public.etapa_da_corrida"
               " where run_id = 'RUN-ERR' and estado = 'FAIL'")
    print('I2 FAIL: diagnostic=%s canonical=%s http=%s' % (diag, canon, http))
    if diag in (None, '-'):
        falhas_.append('I2: a etapa FAIL ficou sem diagnostic_code')
    if canon != 'RATE_LIMITED':
        falhas_.append('I2: o estado canonico da falha nao chegou ao banco (%s)' % canon)
    if canon not in (None, '-') and not fx.retentavel(canon):
        falhas_.append('I2: `leis/falhas.py` deixou de dizer que 429 se retenta')
    if http != '429':
        falhas_.append('I2: o `http_status` nao ficou durável (%s)' % http)

    # ── I3 · QUEM ESTA VIVO NAO DEIXA ETAPA PENDURADA ───────────────────────
    correr('FEXC', 'PROVA-EXC', 'RUN-EXC', espera=1)
    pend = uma("select count(*)::text from public.etapa_da_corrida"
               " where run_id = 'RUN-EXC' and estado = 'RUNNING'")
    est_exc = uma("select estado::text from public.etapa_da_corrida"
                  " where run_id = 'RUN-EXC' order by id desc limit 1")
    st_exc = uma("select status::text from public.collection_run where run_id='RUN-EXC'")
    print('I3 excecao: penduradas=%s ultima=%s run=%s' % (pend, est_exc, st_exc))
    if pend != '0':
        falhas_.append('I3: um processo VIVO deixou etapa pendurada')
    if est_exc != 'FAIL':
        falhas_.append('I3: a etapa aberta na excecao nao fechou em FAIL (%s)' % est_exc)
    if st_exc != 'falhou':
        falhas_.append('I3: a corrida que rebentou nao fechou como `falhou` (%s)' % st_exc)

    # ── I4 · A TENTATIVA 0 NAO E SOBRESCRITA ────────────────────────────────
    correr('FTENT', 'PROVA-TENT', 'RUN-TENT')
    tent = b5.executa("select tentativa::text, estado::text from public.etapa_da_corrida"
                      " where run_id = 'RUN-TENT' and etapa = 'FETCH' order by tentativa")
    print('I4 tentativas: %s' % [(t[0], t[1]) for t in tent])
    if len(tent) != 2 or tent[0][0] != '0' or tent[1][0] != '1':
        falhas_.append('I4: a tentativa 0 foi sobrescrita pela 1')
    if tent and tent[0][1] != 'FAIL':
        falhas_.append('I4: a tentativa 0 perdeu o seu estado')

    # ── I5 · TODA CORRIDA APONTA PARA A SUA UNIDADE DE TRABALHO ─────────────
    orfas = b5.executa("select run_id from public.collection_run"
                       " where checkpoint_id is null and run_id like 'RUN-%'")
    print('I5 corridas sem checkpoint: %d' % len(orfas))
    if orfas:
        falhas_.append('I5: %d corrida(s) sem ligacao ao checkpoint: %s'
                       % (len(orfas), [o[0] for o in orfas][:4]))

    # ── I6 · AS ETAPAS EXISTEM, E SAO AS QUE CORRERAM ───────────────────────
    n_etapas = uma("select count(*)::text from public.etapa_da_corrida"
                   " where run_id like 'RUN-%'")
    print('I6 passagens gravadas: %s' % n_etapas)
    if int(n_etapas or 0) < 10:
        falhas_.append('I6: o rastro quase nao tem linhas; a sonda mediria zero')

    # ── I7 · O AVANCO E DE UM SO, CONTRA DOIS PROCESSOS DE VERDADE ──────────
    ps = [subprocess.Popen([sys.executable, FILHO, 'OK', 'PROVA-CONC',
                            'RUN-CONC-%s' % lado],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, cwd=RAIZ, env=dict(os.environ))
          for lado in ('A', 'B')]
    saidas = [p_.communicate(timeout=600)[0].strip() for p_ in ps]
    avancos = [o.split('AVANCO=')[-1] for o in saidas if 'AVANCO=' in o]
    feitas_c = uma("select unidades_feitas::text from public.checkpoint_coleta"
                   " where collection_target = 'PROVA/unidade/PROVA-CONC'")
    print('I7 concorrencia: avancos=%s unidades_feitas=%s' % (avancos, feitas_c))
    if avancos.count('AVANCOU') != 1:
        falhas_.append('I7: %d processos disseram que avancaram' % avancos.count('AVANCOU'))
    if feitas_c != '1':
        falhas_.append('I7: o checkpoint andou %s vezes para UMA unidade' % feitas_c)

    print()
    for f in falhas_:
        print('  ✗ %s' % f)
    print('RUN_DURAVEL=%s' % ('PASS' if not falhas_ else 'FAIL'))
    return 0 if not falhas_ else 1


if __name__ == '__main__':
    raise SystemExit(main())
