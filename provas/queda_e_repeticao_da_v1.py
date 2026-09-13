#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIGHT-SHIFT-01 §15/§16 — QUEDA, REPETIÇÃO, IDEMPOTÊNCIA E CONCORRÊNCIA.

    python3 provas/queda_e_repeticao_da_v1.py

Quatro perguntas, e nenhuma delas é «a guarda devolve o que eu espero?».

    1  DUAS CORRIDAS AO MESMO TEMPO CONSEGUEM PAGAR DUAS VEZES
       COM UMA AUTORIZAÇÃO PARA UMA?
    2  UMA CORRIDA QUE MORRE DEPOIS DE CONSUMIR DEVOLVE O GASTO?
    3  UMA AUTORIZAÇÃO ATRAVESSA PARA OUTRO PROCESSO?
    4  REPETIR COM O MESMO `run_id` FABRICA IDENTIDADE?

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
`subprocess.run` DENTRO do `coletor` — a camada mais funda, por baixo da
guarda, dos dois tetos e do cap do provider. A lei, o coletor, o adaptador, o
roteador e o executor são os verdadeiros.

    UM FAKE ACIMA DO GATE MEDE O FAKE.

E a contagem é de POSTs que TERIAM saído: um POST que o falso viu é uma compra
que nasceu.

    APIFY_RUNS = 0 · PAID_USD = 0 · REDE REAL = 0

POR QUE SE FORÇA A TROCA DE FIO
--------------------------------
Uma corrida que só aparece uma vez em mil não deixa de existir por não ter
aparecido hoje. `sys.setswitchinterval` encurtado não INVENTA a corrida — ela
ou existe no código ou não existe. Só a torna visível numa medição de minutos
em vez de numa de meses.

    PLAUSIBLE != PROVEN — E «NÃO APARECEU» NÃO É «NÃO EXISTE».
"""
import os
import subprocess
import sys
import threading

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('provas', 'coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import autorizacao_de_gasto as az                                 # noqa: E402
import coletor as ct                                              # noqa: E402
import nenhuma_compra_sem_autorizacao as sr02                     # noqa: E402
import scrap_http as http                                         # noqa: E402

PROPOSITO = sr02.PROPOSITO
FONTE = sr02.FONTE


def _autorizacao(n, usd=0.10):
    """Uma autorização de ensaio para `n` execuções. Quem a concede é o dono."""
    return az.autorizar(
        motivo=az.TRIAL_DE_CAPACIDADE, proposito=PROPOSITO,
        max_execucoes=n, max_usd=usd, quem_autorizou='NIGHT-SHIFT-01',
        porque='medir se a porta paga deixa passar mais do que autorizou',
        condicao_de_paragem='as %d execucao(oes) autorizadas' % n)


# ══════════════════════════════════════════════════════════════════════════
# 1 · A PORTA PAGA, COM DUAS CORRIDAS AO MESMO TEMPO
# ══════════════════════════════════════════════════════════════════════════
def a_porta_paga(fios, teto, rodadas=1):
    """→ (POSTs que teriam saído, execuções autorizadas, teto)."""
    piores = (0, 0)
    for _ in range(rodadas):
        a = _autorizacao(teto)
        falsa = sr02.FalsaApify(sr02.itens_reais())
        # ⚠️ O TRANSPORTE E FIXADO ANTES DE MEDIR. `regras/sensor_coleta.py`
        # troca `coletor._curl` NO IMPORT: basta alguem te-lo importado antes
        # para o falso deixar de ser chamado e a medicao passar a ser de outra
        # coisa. A lei e da bateria da SR-02, e vale aqui igual.
        #
        #     UMA SONDA QUE NAO FIXA O TRANSPORTE MEDE QUEM IMPORTOU ANTES DELA.
        real, curl = subprocess.run, ct._curl
        subprocess.run = falsa
        ct._curl = ct._CURL_DA_CASA
        porta = threading.Barrier(fios)
        try:
            # UM orçamento para todos: dois orçamentos fariam a lei recusar por
            # `AUTORIZACAO_DE_OUTRO_LEDGER` e a corrida ficava escondida atrás
            # de uma recusa certa pelo motivo errado.
            with http.orcamento_de_rede(fios * 4), ct.orcamento_financeiro(0.10):
                def bate():
                    porta.wait()
                    try:
                        ct.executar(sr02.ATOR, {'videoUrl': 'https://youtu.be/X'},
                                    token='FALSO', run_id='NS-CORRIDA',
                                    platform='YOUTUBE', country='IT',
                                    mission='NIGHT-SHIFT-01', query='X',
                                    source_version='prova',
                                    evidence_path='/dev/null', wait=5,
                                    salvar_raw=False, teto_usd=0.10,
                                    modo=az.TRIAL, autorizacao=a,
                                    proposito=PROPOSITO,
                                    motivo_do_gasto=az.TRIAL_DE_CAPACIDADE)
                    except Exception:                             # noqa: BLE001
                        pass
                ts = [threading.Thread(target=bate) for _ in range(fios)]
                for t in ts:
                    t.start()
                for t in ts:
                    t.join()
        finally:
            subprocess.run, ct._curl = real, curl
        piores = max(piores, (len(falsa.posts), a.gastas))
    return piores[0], piores[1], teto


# ══════════════════════════════════════════════════════════════════════════
# 2 · A PRIMITIVA, MUITAS VEZES — a corrida é rara, e rara não é ausente
# ══════════════════════════════════════════════════════════════════════════
def a_primitiva(fios, teto, rodadas=200):
    """→ (rodadas com furo, pior número de autorizações concedidas)."""
    furos, pior = 0, teto
    for _ in range(rodadas):
        a = _autorizacao(teto)
        porta = threading.Barrier(fios)
        contados, trava = [], threading.Lock()

        def bate():
            porta.wait()
            try:
                az.conferir_e_consumir(a, motivo=az.TRIAL_DE_CAPACIDADE,
                                       proposito=PROPOSITO, teto_usd=0.10)
                ok = True
            except az.GastoRecusado:
                ok = False
            if ok:
                with trava:
                    contados.append(1)

        ts = [threading.Thread(target=bate) for _ in range(fios)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        if len(contados) != teto:
            furos += 1
            pior = max(pior, len(contados))
    return furos, pior


# ══════════════════════════════════════════════════════════════════════════
# 3 · QUEDA DEPOIS DE CONSUMIR, E REPETIÇÃO
# ══════════════════════════════════════════════════════════════════════════
def queda_e_repeticao():
    """Consome, a rota morre, e a mesma autorização é trazida outra vez."""
    a = _autorizacao(1)
    az.conferir_e_consumir(a, motivo=az.TRIAL_DE_CAPACIDADE,
                           proposito=PROPOSITO, teto_usd=0.10)
    # aqui a corrida morreria: o POST saiu, a resposta nunca chegou.
    try:
        az.conferir_e_consumir(a, motivo=az.TRIAL_DE_CAPACIDADE,
                               proposito=PROPOSITO, teto_usd=0.10)
        return 'PAGOU_OUTRA_VEZ', a.gastas
    except az.GastoRecusado as e:
        # ⚠️ `e.causa`, e nao `e.args[0]`: o primeiro argumento e a FRASE
        # inteira, com o prefixo e o detalhe. A primeira corrida desta sonda
        # comparou-a com o codigo, nao bateu, e imprimiu «PAGOU DUAS VEZES»
        # sobre uma recusa correcta.
        #
        #     UMA SONDA QUE LE O CAMPO ERRADO ACUSA O CODIGO CERTO.
        return e.causa, a.gastas


def copia_da_autorizacao():
    """Uma autorização reconstruída a partir dos campos dela."""
    a = _autorizacao(1)
    campos = a.para_o_manifesto()
    try:
        falsa = az.Autorizacao(
            motivo=a.motivo, proposito=a.proposito, source_id=a.source_id,
            max_execucoes=a.max_execucoes, max_usd=a.max_usd,
            quem_autorizou=a.quem_autorizou, porque=a.porque,
            condicao_de_paragem=a.condicao_de_paragem)
    except az.AutorizacaoInvalida as e:
        return 'RECUSADA_NA_CONSTRUCAO', str(e).split(':')[0], len(campos)
    try:
        az.conferir_e_consumir(falsa, motivo=a.motivo, proposito=a.proposito,
                               teto_usd=0.10)
        return 'COMPROU', '', len(campos)
    except az.GastoRecusado as e:
        return 'RECUSADA_NA_PORTA', e.causa, len(campos)


# ══════════════════════════════════════════════════════════════════════════
# 4 · REPETIR NÃO FABRICA IDENTIDADE
# ══════════════════════════════════════════════════════════════════════════
def repetir_o_canario():
    """Duas corridas do canário com o MESMO `run_id`. → o que mudou."""
    import tempfile
    import _rc01_mundo_falso as mundo
    import social_envelope as env
    import scrap_colheita as sc
    banco = tempfile.mkdtemp(prefix='ns-repete-')
    os.environ['RC01_MARCA'] = banco
    env.RAW_DIR = os.path.join(banco, 'raw')
    mundo.MARCA = banco
    mundo.IDAS = os.path.join(banco, 'IDAS.json')
    mundo.instalar()
    handle = mundo.FEED['feed'][0]['post']['author']['handle']
    saidas = []
    for _ in range(2):
        env_ = sc.colher('canario-bluesky', run_id='NS-REPETE',
                         fonte='IT-T9-001', handle=handle)
        saidas.append([{k: u.get(k) for k in
                        ('SOURCE_ID', 'DOCUMENT_ID', 'RUN_ID', 'URL')}
                       for u in env_['COLHEITA']])
    return saidas


def main():
    print(__doc__.strip().splitlines()[0])
    print('=' * 78)
    sys.setswitchinterval(1e-9)

    print('\n1 · A PORTA PAGA — %s' % 'POSTs que teriam saído')
    mal = 0
    for fios, teto in ((4, 1), (16, 1), (16, 3)):
        posts, gastas, t = a_porta_paga(fios, teto, rodadas=10)
        furou = posts > t
        mal += furou
        print('   fios=%-3d teto=%-2d  POSTS=%-3d GASTAS=%-3d  %s'
              % (fios, teto, posts, gastas,
                 '⚠️ NASCERAM %d COMPRAS ALÉM DO AUTORIZADO' % (posts - t)
                 if furou else 'dentro do autorizado'))

    print('\n2 · A PRIMITIVA — 200 rodadas por linha')
    for fios, teto in ((4, 1), (16, 1), (16, 3), (64, 3)):
        furos, pior = a_primitiva(fios, teto)
        mal += bool(furos)
        print('   fios=%-3d teto=%-2d  furos=%-4d pior=%-3d  %s'
              % (fios, teto, furos, pior,
                 '⚠️ A PORTA DEIXOU PASSAR %d' % pior if furos else 'nenhum furo'))

    print('\n3 · QUEDA E REPETIÇÃO')
    causa, gastas = queda_e_repeticao()
    ok = causa == 'AUTORIZACAO_ESGOTADA'
    mal += not ok
    print('   a mesma autorização, outra vez: %-24s GASTAS=%d  %s'
          % (causa, gastas, 'não devolve o gasto' if ok else '⚠️ PAGOU DUAS VEZES'))
    veredito, causa2, campos = copia_da_autorizacao()
    ok = veredito != 'COMPROU'
    mal += not ok
    print('   uma cópia reconstruída:         %-24s (%s)  %s'
          % (veredito, causa2 or '-',
             'COPIAR NÃO É RECEBER' if ok else '⚠️ UMA CÓPIA COMPROU'))

    print('\n4 · REPETIR COM O MESMO run_id')
    a, b = repetir_o_canario()
    igual = a == b
    # ⚠️ LIDO DO DONO, e nao escrito a mao: a primeira corrida desta sonda
    # comparou com `'NÃO SEI'` acentuado, o dono escreve `NAO SEI`, e ela
    # acusou o canario de fabricar identidade.
    #
    #     UMA SONDA QUE ADIVINHA O VOCABULARIO DE OUTRO DONO
    #     MEDE O QUE ELA IMAGINOU QUE ELE DIRIA.
    import retorno_da_coleta as rc
    sem_doc = all(u['DOCUMENT_ID'] == rc.NAO_SEI for u in a + b)
    mal += not (igual and sem_doc)
    print('   unidades: %d e %d · idênticas=%s · DOCUMENT_ID fabricado=%s'
          % (len(a), len(b), 'SIM' if igual else 'NÃO',
             'NÃO' if sem_doc else '⚠️ SIM'))
    for u in a[:1]:
        print('   %s' % u)

    print('=' * 78)
    print('FUROS = %d · REAL_NETWORK = 0 · APIFY_RUNS = 0 · PAID_USD = 0' % mal)
    return 1 if mal else 0


if __name__ == '__main__':
    sys.exit(main())
