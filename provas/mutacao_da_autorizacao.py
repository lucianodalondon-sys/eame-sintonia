#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-SR-02 — A MUTAÇÃO DIZ SE A GUARDA ESTÁ MESMO A GUARDAR.

    py provas/mutacao_da_autorizacao.py

Quarenta e cinco sentinelas verdes só provam que elas passaram. A pergunta é:

    SE EU ABRIR UM BURACO NA GUARDA, ALGUMA FICA VERMELHA?

Cada mutação estraga UMA garantia. Uma que sobreviva é um buraco que ninguém
está a vigiar.

    SURVIVORS > 0 SIGNIFICA QUE A BATERIA MEDE A SI PRÓPRIA.

A árvore real não é tocada: muta-se uma CÓPIA numa pasta temporária.

    APIFY_RUNS = 0 · PAID_USD = 0 · REDE = 0
"""
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATERIAS = ('tests.test_scrap_sr02_autorizacao_de_gasto',
            'tests.test_c10_8b_rota_paga_canonica',
            'tests.test_c10_8af_orcamento_financeiro')

LEI = 'leis/autorizacao_de_gasto.py'
DONO = 'coleta/coletor.py'
EXEC = 'coleta/scrap_executor.py'

#: (nome, ficheiro, velho, novo, a garantia que isto parte)
MUTACOES = [
    ('M1 · a guarda desaparece da primitiva', DONO,
     "    recibo = az.pode_comprar(modo=modo, autorizacao=autorizacao,\n"
     "                             source_id=source_id, proposito=proposito,\n"
     "                             ator=actor)",
     "    recibo = {'CAN_START_PAID_EXECUTION': True, 'MODE': modo,\n"
     "              'BASIS': 'NENHUMA', 'PROMOTES_RELEVANCE': False}",
     'nenhuma compra sem autorizacao'),

    ('M2 · NAO_AVALIADA passa a comprar', LEI,
     "    if veredito != AUTORIZA or estado_rel != SIM:",
     "    if veredito != AUTORIZA and estado_rel == NAO:",
     'as ausencias nao viram sim'),

    ('M3 · NAO_SEI passa a comprar', LEI,
     "        nome = _NOME_DA_AUSENCIA.get(estado_rel, SEM_AUTORIZACAO)",
     "        if estado_rel == NAO_SEI:\n"
     "            return {'CAN_START_PAID_EXECUTION': True, 'MODE': modo,\n"
     "                    'BASIS': 'SOURCE_RELEVANCE', 'PROMOTES_RELEVANCE': False,\n"
     "                    'SOURCE_ID': pedido_sid, 'PROPOSITO': pedido_prop}\n"
     "        nome = _NOME_DA_AUSENCIA.get(estado_rel, SEM_AUTORIZACAO)",
     'NAO_SEI nao e um sim'),

    ('M4 · ERRO passa a ser uma rejeicao com nome de barrada', LEI,
     "    ERRO: RELEVANCIA_COM_ERRO,",
     "    ERRO: RELEVANCIA_BARRADA,",
     'as quatro ausencias nao colapsam num nome so'),

    ('M5 · o proposito errado passa', LEI,
     "    if pedido_prop != autorizado_prop:",
     "    if False and pedido_prop != autorizado_prop:",
     'um SIM para T3 nao e um SIM para T9'),

    ('M6 · a fonte errada passa', LEI,
     "    if pedido_sid != autorizado_sid:",
     "    if False and pedido_sid != autorizado_sid:",
     'autorizacao da fonte A nao compra a fonte B'),

    ('M7 · URL passa a valer como SOURCE_ID', LEI,
     "    if any(s.lower().startswith(p) for p in _PREFIXOS_DE_URL) or '/' in s:",
     "    if False:",
     'URL nao e SOURCE_ID'),

    ('M8 · a chave substitui a autorizacao', DONO,
     "    recibo = az.pode_comprar(modo=modo, autorizacao=autorizacao,\n"
     "                             source_id=source_id, proposito=proposito,\n"
     "                             ator=actor)",
     "    if token:\n"
     "        recibo = {'CAN_START_PAID_EXECUTION': True, 'MODE': modo,\n"
     "                  'BASIS': 'TOKEN', 'PROMOTES_RELEVANCE': False}\n"
     "    else:\n"
     "        recibo = az.pode_comprar(modo=modo, autorizacao=autorizacao,\n"
     "                                 source_id=source_id, proposito=proposito,\n"
     "                                 ator=actor)",
     'TOKEN_OWNER != SPEND_OWNER'),

    ('M9 · o orcamento substitui a autorizacao', LEI,
     "    if not isinstance(autorizacao, dict) or not autorizacao:",
     "    if False:",
     'BUDGET_PRESENT != SPEND_AUTHORIZED'),

    ('M10 · qualquer veredito serve desde que exista', LEI,
     "    for campo in CAMPOS_DA_AUTORIZACAO:\n"
     "        if campo not in autorizacao:",
     "    for campo in ():\n"
     "        if campo not in autorizacao:",
     'o contrato do veredito e conferido'),

    ('M11 · NORMAL escapa por TRIAL sem limites', LEI,
     "        limites = _conferir_limites(autorizacao, modo)",
     "        limites = {}",
     'NORMAL nao se veste de TRIAL'),

    ('M12 · NORMAL escapa por PROBE sem limites', LEI,
     "    campos = list(CAMPOS_DO_LIMITE)\n"
     "    if modo == PROBE:\n"
     "        campos.append(CAMPO_SO_DO_PROBE)",
     "    campos = []",
     'NORMAL nao se veste de PROBE'),

    ('M13 · o probe fica ilimitado', LEI,
     "            if numero <= 0:",
     "            if False:",
     'zero nao e sem teto'),

    ('M14 · o trial dispensa autorizacao humana', LEI,
     "CAMPOS_DO_LIMITE = ('AUTORIZACAO_HUMANA', 'MAX_PROVIDER_RUNS',\n"
     "                    'MAX_START_POSTS', 'MAX_USD')",
     "CAMPOS_DO_LIMITE = ('MAX_PROVIDER_RUNS', 'MAX_START_POSTS')",
     'PROBE e TRIAL exigem gente e teto de dolares'),

    # Este APAGA a chamada (o M1 substitui-a por um recibo falso). Dois sitios
    # de edicao diferentes para a mesma garantia — e o M15b, abaixo, e o unico
    # que mede a ORDEM sem mexer na existencia.
    ('M15 · a chamada da guarda e apagada da primitiva', DONO,
     "    recibo = az.pode_comprar(modo=modo, autorizacao=autorizacao,\n"
     "                             source_id=source_id, proposito=proposito,\n"
     "                             ator=actor)\n"
     "    # ── O GATE FINANCEIRO VEM ANTES DO POST ",
     "    # ── O GATE FINANCEIRO VEM ANTES DO POST ",
     'a guarda vem antes da reserva'),

    # A guarda continua LA — so troca de lugar com a reserva. Um mutante que a
    # apagasse seria o M1 outra vez com outro nome, e um que a duplicasse nao
    # mudava comportamento nenhum (foi o primeiro erro desta prova).
    # A guarda continua LA — so troca de lugar com a reserva. Um mutante que a
    # apagasse seria o M1 outra vez com outro nome, e um que a DUPLICASSE nao
    # mudava comportamento nenhum: foram os dois primeiros erros desta prova.
    #
    #     UM MUTANTE QUE NAO MUDA O COMPORTAMENTO NAO MEDE SENTINELA NENHUMA.
    ('M15b · a guarda corre, mas depois de o dinheiro estar reservado', DONO,
     '    recibo = az.pode_comprar(modo=modo, autorizacao=autorizacao,\n                             source_id=source_id, proposito=proposito,\n                             ator=actor)\n    # ── O GATE FINANCEIRO VEM ANTES DO POST ───────────────────────────────────\n    # Cobrar depois do provider é contar o prejuízo. A reserva acontece aqui, e é\n    # ela que decide o `maxTotalChargeUsd` que vai na query.\n    orcamento = orcamento_financeiro_actual()\n    reserva = None\n    if orcamento is not None:\n        reserva = orcamento.reservar(pedido=teto_usd, ator=actor,\n                                     rota=rota or evidence_path, missao=mission)\n        teto_usd = reserva.cap',
     '    # ── O GATE FINANCEIRO VEM ANTES DO POST ───────────────────────────────────\n    # Cobrar depois do provider é contar o prejuízo. A reserva acontece aqui, e é\n    # ela que decide o `maxTotalChargeUsd` que vai na query.\n    orcamento = orcamento_financeiro_actual()\n    reserva = None\n    if orcamento is not None:\n        reserva = orcamento.reservar(pedido=teto_usd, ator=actor,\n                                     rota=rota or evidence_path, missao=mission)\n        teto_usd = reserva.cap\n    recibo = az.pode_comprar(modo=modo, autorizacao=autorizacao,\n                             source_id=source_id, proposito=proposito,\n                             ator=actor)',
     'uma reserva que ninguem liquidou nao volta ao bolso'),

    ('M16 · o pool de chaves passa a decidir gasto', 'ferramentas/apify_pool.py',
     "def pool(",
     "def pode_comprar(*a, **k):\n"
     "    return {'VEREDITO': 'AUTORIZA'}\n\n\ndef pool(",
     'TOKEN_OWNER != SPEND_OWNER'),

    ('M17 · o coletor passa a julgar relevancia', DONO,
     "import autorizacao_de_gasto as az  # noqa: E402",
     "import autorizacao_de_gasto as az  # noqa: E402\nimport admissao  # noqa: E402",
     'SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER'),

    ('M18 · o modo deixa de descer ate ao dono da compra', EXEC,
     "    kwargs = dict(kwargs, modo=modo)",
     "    kwargs = dict(kwargs)",
     'o eixo do modo viaja com o pedido'),

    ('M19 · o recibo deixa de viajar no manifesto', DONO,
     "    manifesto['SPEND_AUTHORIZATION'] = dict(recibo)",
     "    manifesto['SPEND_AUTHORIZATION'] = None",
     'CAN DO != DID DO'),

    ('M20 · a recusa deixa de ser da casa', DONO,
     "        return (SemAutorizacaoDeGasto, SemOrcamentoFinanceiro,\n"
     "                _http.SemOrcamentoDeRede)",
     "        return (SemOrcamentoFinanceiro, _http.SemOrcamentoDeRede)",
     'uma recusa nossa nao veste a roupa da fonte'),

    ('M21 · os modos voltam a ter dois donos', EXEC,
     "from autorizacao_de_gasto import (  # noqa: E402\n"
     "    NORMAL, TRIAL, PROBE, MODOS, MODOS_DE_MEDIDA,\n"
     ")",
     "NORMAL = 'NORMAL'\nTRIAL = 'TRIAL'\nPROBE = 'PROBE'\n"
     "MODOS = (NORMAL, TRIAL, PROBE)\nMODOS_DE_MEDIDA = (TRIAL, PROBE)",
     'ONE CONCEPT -> ONE OWNER'),

    ('M22 · a guarda passa a ler o livro da relevancia', LEI,
     "    if modo in MODOS_DE_MEDIDA:",
     "    if os.path.exists('LIVRO'):\n"
     "        open('LIVRO').read()\n"
     "    if modo in MODOS_DE_MEDIDA:",
     'o spend boundary nao abre o livro'),
]


def _copia(destino):
    pesadas = {'.git', 'data', 'node_modules', 'italia-portale', '__pycache__',
               '.tmp', 'build'}
    for nome in os.listdir(RAIZ):
        if nome in pesadas:
            continue
        o = os.path.join(RAIZ, nome)
        a = os.path.join(destino, nome)
        if os.path.isdir(o):
            shutil.copytree(o, a, symlinks=True,
                            ignore=shutil.ignore_patterns('__pycache__',
                                                          'node_modules'))
        else:
            shutil.copy2(o, a)
    for nome in ('.git', 'data'):
        os.symlink(os.path.join(RAIZ, nome), os.path.join(destino, nome))


def _correr(arvore):
    p = subprocess.run([sys.executable, '-m', 'unittest'] + list(BATERIAS),
                       cwd=arvore, capture_output=True, text=True)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def main():
    print('SCRAP-SR-02 · MUTAÇÃO DA GUARDA DE GASTO')
    print('=' * 74)
    base = tempfile.mkdtemp(prefix='sr02-mut-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        _copia(arvore)
        codigo, saida = _correr(arvore)
        if codigo != 0:
            print('A CÓPIA JÁ NASCE VERMELHA — a mutação não mediria nada.')
            print(saida[-2500:])
            return 3
        print('cópia limpa: baterias VERDES\n')

        sobreviventes = []
        for nome, rel, velho, novo, garantia in MUTACOES:
            alvo = os.path.join(arvore, rel)
            with open(alvo, encoding='utf-8') as f:
                original = f.read()
            if velho not in original:
                print('%-56s ALVO_AUSENTE' % nome[:56])
                sobreviventes.append((nome, 'ALVO_AUSENTE'))
                continue
            with open(alvo, 'w', encoding='utf-8') as f:
                f.write(original.replace(velho, novo, 1))
            try:
                codigo, saida = _correr(arvore)
            finally:
                with open(alvo, 'w', encoding='utf-8') as f:
                    f.write(original)
            morta = codigo != 0
            quantas = saida.count('FAIL: ') + saida.count('ERROR: ')
            print('%-56s %s (%d sentinelas)'
                  % (nome[:56], 'MORTA  ' if morta else 'SOBREVIVE', quantas))
            print('%-56s   guarda: %s' % ('', garantia))
            if not morta:
                sobreviventes.append((nome, garantia))

        print('=' * 74)
        print('MUTANTS   = %d' % len(MUTACOES))
        print('SURVIVORS = %d' % len(sobreviventes))
        for nome, porque in sobreviventes:
            print('  SOBREVIVEU · %s — ninguém guarda: %s' % (nome, porque))
        return 0 if not sobreviventes else 1
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
