#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O PROCESSO QUE MORRE DE VERDADE — o outro lado de `run_duravel_no_postgres.py`.

    py provas/_c106b_filho.py <PONTO> <UNIDADE> <RUN_ID>

`PONTO` ∈ F0 F1 F2 F3 F4 RETOMAR. A morte é `os._exit(97)`: sem `finally`, sem
`atexit`, sem flush, sem fechar a ligação ao banco.

    UMA EXCEÇÃO NÃO É UMA MORTE. UMA EXCEÇÃO TEM `finally`.

Este ficheiro não toca plataforma nenhuma: o trabalho é uma função local que
declara o que fez. O que se mede aqui é a DURABILIDADE, não a aquisição — e
misturar as duas faria a prova precisar de rede para provar que sobrevive a um
crash.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import coleta_checkpoint as ck   # noqa: E402

PONTO, UNIDADE, RUN = sys.argv[1], sys.argv[2], sys.argv[3]
TARGET = 'PROVA/unidade/%s' % UNIDADE
ENTRADA = {'PLATFORM': 'PROVA', 'EXTERNAL_ID': UNIDADE, 'CAPABILITY': 'FETCH'}
IDENT = ('PLATFORM', 'EXTERNAL_ID', 'CAPABILITY')
BASE = ck.RelatorDeEtapas


def morrer(onde):
    print('MORRENDO_EM=%s PID=%d' % (onde, os.getpid()), flush=True)
    os._exit(97)


class MorreAoAbrir(BASE):
    ALVO = None

    def abrir(self, etapa, **kw):
        linha = BASE.abrir(self, etapa, **kw)
        if etapa == self.ALVO:
            morrer('%s:%s_ABERTA' % (PONTO, etapa))
        return linha


class MorreAoFechar(BASE):
    ALVO = None

    def fechar(self, linha, estado, **kw):
        etapa = next((e for (i, e, _t) in self.abertas if i == linha), None)
        fora = BASE.fechar(self, linha, estado, **kw)
        if etapa == self.ALVO:
            morrer('%s:%s_FECHADA' % (PONTO, etapa))
        return fora


def trabalho(relator, contexto):
    if PONTO == 'F0':
        morrer('F0:RUN_E_CHECKPOINT_ABERTOS')
    # ── FERR · A ETAPA FALHA COM ESTADO CANONICO, E NINGUEM MORRE ──────────
    # Nao e crash: e uma falha normal, para provar que o checkpoint NAO anda e
    # que a linha de FAIL fica no banco com o codigo de diagnostico.
    if PONTO == 'FERR':
        x = relator.abrir('FETCH', input_grain='ITEM', input_count=1)
        relator.fechar(x, 'FAIL', error=1, canonical_state='RATE_LIMITED',
                       http_status=429, error_message='a fonte pediu para esperar')
        return {'PERSISTIU': 0, 'FALHOU': True, 'PORQUE': 'RATE_LIMITED'}
    # ── FEXC · UMA EXCECAO DENTRO DO TRABALHO, COM UMA ETAPA ABERTA ────────
    # Quem esta VIVO nao pode deixar uma etapa pendurada: so a morte tem esse
    # direito, porque so ela nao teve como fechar.
    if PONTO == 'FEXC':
        relator.abrir('FETCH', input_grain='ITEM', input_count=1)
        raise RuntimeError('o trabalho rebentou com uma etapa aberta')
    # ── FTENT · DUAS TENTATIVAS DA MESMA ETAPA NA MESMA CORRIDA ───────────
    if PONTO == 'FTENT':
        a = relator.abrir('FETCH', input_grain='ITEM', input_count=1)
        relator.fechar(a, 'FAIL', error=1, canonical_state='TRANSIENT_NETWORK_ERROR',
                       error_message='primeira tentativa')
        b = relator.abrir('FETCH', input_grain='ITEM', input_count=1)
        relator.fechar(b, 'PASS', passed=1, output_grain='MEDIA', output_count=1,
                       cardinalidade='1:1', last_good_artifact='RAW_BYTES:local')
        return {'PERSISTIU': 1, 'FALHOU': False}
    f = relator.abrir('FETCH', input_grain='ITEM', input_count=1)
    relator.fechar(f, 'SKIPPED', reused=1, output_grain='MEDIA', output_count=1,
                   cardinalidade='1:1', last_good_artifact='RAW_BYTES:local')
    r = relator.abrir('RAW', edge_from='FETCH', input_grain='MEDIA', input_count=1)
    relator.fechar(r, 'PASS', passed=1, output_grain='RAW_OBSERVATION',
                   output_count=1, cardinalidade='1:1',
                   last_good_artifact='RAW:PROVA-%s' % UNIDADE)
    d = relator.abrir('DERIVED', edge_from='RAW',
                      input_grain='RAW_OBSERVATION', input_count=1)
    relator.fechar(d, 'PASS', passed=1, output_grain='TRANSCRIPT', output_count=1,
                   cardinalidade='1:1',
                   last_good_artifact='DERIVED:PROVA-%s' % UNIDADE)
    if PONTO == 'F4':
        morrer('F4:DERIVED_PERSISTIDO_RUN_ABERTA')
    return {'PERSISTIU': 1, 'FALHOU': False}


if PONTO == 'F1':
    MorreAoAbrir.ALVO = 'FETCH'
    ck.RelatorDeEtapas = MorreAoAbrir
elif PONTO == 'F3':
    MorreAoAbrir.ALVO = 'DERIVED'
    ck.RelatorDeEtapas = MorreAoAbrir
elif PONTO == 'F2':
    MorreAoFechar.ALVO = 'RAW'
    ck.RelatorDeEtapas = MorreAoFechar

banco = ck.Banco(os.environ['BANCO_DESCARTAVEL_URL'])
r = ck.executar_unidade_duravel(
    banco, run_id=RUN, target=TARGET, entrada=ENTRADA, actor='prova_c106b',
    platform='PROVA', trabalho=trabalho, campos_da_identidade=IDENT,
    unidade=UNIDADE)
print('STATE=%s RUN=%s CHECKPOINT=%s AVANCO=%s'
      % (r.get('STATE'), r.get('RUN_ID'), r.get('CHECKPOINT_ID'),
         r.get('CHECKPOINT_ADVANCE')), flush=True)
raise SystemExit(0)
