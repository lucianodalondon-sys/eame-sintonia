#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-OWNER-01 — A MUTAÇÃO DIZ SE O DONO ÚNICO ESTÁ MESMO A GUARDAR.

    py provas/mutacao_da_autorizacao.py

Duas linhagens escreveram a mesma lei. A que venceu trouxe duas propriedades
que a outra não tinha — autorização SELADA e autorização CONSUMÍVEL — e essas
duas não se provam lendo a árvore: provam-se partindo-as.

    SE EU ABRIR UM BURACO NA GUARDA, ALGUMA SENTINELA FICA VERMELHA?

Muta-se uma CÓPIA. A árvore real não é tocada.

    APIFY_RUNS = 0 · REAL_NETWORK = 0 · COST_USD = 0
"""
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATERIAS = ('tests.test_autorizacao_de_gasto',
            'tests.test_scrap_sr02_autorizacao_de_gasto',
            'tests.test_c10_8b_rota_paga_canonica')

LEI = 'leis/autorizacao_de_gasto.py'
DONO = 'coleta/coletor.py'
REL = 'leis/relevancia_da_fonte.py'
SENSOR = 'regras/sensor_coleta.py'

MUTACOES = [
    ('M1 · o selo desaparece', LEI,
     "        if self._selo is not _SELO:",
     "        if False:",
     'uma autorizacao que o chamador escreve nao e uma autorizacao'),

    ('M1b · a guarda deixa de conferir o selo', LEI,
     "    if not isinstance(autorizacao, Autorizacao) or autorizacao._selo is not _SELO:",
     "    if autorizacao is None:",
     'o objecto tem de ter saido de autorizar()'),

    ('M2 · reuso ilimitado', LEI,
     "    if autorizacao.restantes <= 0:",
     "    if False:",
     'uma autorizacao de uma execucao nao paga duas'),

    ('M2b · o consumo deixa de acontecer', LEI,
     "    autorizacao._gastas += 1",
     "    pass",
     'a autorizacao gasta-se'),

    ('M3 · fonte errada passa', LEI,
     "        if str(source_id or '').strip() != autorizacao.source_id:",
     "        if False:",
     'autorizada para outra fonte'),

    ('M4 · proposito errado passa', LEI,
     "    if str(autorizacao.proposito) != str(proposito or '').strip():",
     "    if False:",
     'um SIM para T3 nao e um SIM para T9'),

    ('M5 · motivo errado passa', LEI,
     "    if autorizacao.motivo != motivo:",
     "    if False:",
     'coleta normal != probe != trial'),

    ('M6 · o orcamento substitui a autorizacao', DONO,
     "    recibo = az.conferir_e_consumir(",
     "    if orcamento_financeiro_actual() is not None:\n"
     "        recibo = {'VEREDITO': 'AUTORIZADO', 'MOTIVO_DO_GASTO': motivo}\n"
     "    else:\n"
     "        recibo = az.conferir_e_consumir(",
     'BUDGET_PRESENT != SPEND_AUTHORIZED'),

    ('M7 · a chave substitui a autorizacao', DONO,
     "    motivo = az.motivo_do_modo(motivo_do_gasto or modo)",
     "    motivo = az.motivo_do_modo(motivo_do_gasto or modo)\n"
     "    if token and autorizacao is None:\n"
     "        autorizacao = az.autorizar(\n"
     "            motivo=motivo, proposito=proposito or 'T9', max_execucoes=99,\n"
     "            max_usd=99.0, quem_autorizou='a chave', porque='a chave',\n"
     "            condicao_de_paragem='nenhuma')",
     'TOKEN_PRESENT != SPEND_ALLOWED'),

    ('M8 · a politica substitui a autorizacao', LEI,
     "    if autorizacao is None:\n        raise GastoRecusado('AUTORIZACAO_AUSENTE'",
     "    if False:\n        raise GastoRecusado('AUTORIZACAO_AUSENTE'",
     'ALLOWED_ROUTE != AUTHORIZED_SPEND'),

    ('M9 · o probe fica ilimitado', LEI,
     "    if not max_execucoes or int(max_execucoes) < 1:",
     "    if False:",
     'gasto por excecao sem teto e coleta com outro nome'),

    ('M10 · o trial dispensa teto de dolares', LEI,
     "    if max_usd is None or float(max_usd) <= 0:",
     "    if False:",
     'gasto por excecao sem teto de dolares e um cheque em branco'),

    ('M10b · o gasto por excecao dispensa quem responde', LEI,
     "    if not str(quem_autorizou or '').strip():",
     "    if False:",
     'excecao precisa de alguem que responda por ela'),

    ('M11 · NORMAL veste-se de TRIAL', LEI,
     "    NORMAL: COLETA_NORMAL,",
     "    NORMAL: TRIAL_DE_CAPACIDADE,",
     'o modo nao escolhe o motivo que lhe convem'),

    ('M12 · NORMAL veste-se de PROBE', LEI,
     "    PROBE: PROVA_DE_RELEVANCIA,",
     "    PROBE: COLETA_NORMAL,",
     'os tres modos continuam distintos'),

    ('M13 · URL passa a valer como SOURCE_ID', REL,
     "    if any(baixo.startswith(p) for p in _PREFIXOS_DE_URL) or '/' in s:",
     "    if False:",
     'URL nao e SOURCE_ID'),

    ('M14 · o teto do fornecedor deixa de ser exigido', LEI,
     "        if teto_usd is None:\n"
     "            raise GastoRecusado('SEM_TETO_NO_FORNECEDOR'",
     "        if False:\n"
     "            raise GastoRecusado('SEM_TETO_NO_FORNECEDOR'",
     'a nossa trava nao sobrevive a um bug nosso'),

    ('M14b · o teto pedido pode passar do autorizado', LEI,
     "        if float(teto_usd) > float(autorizacao.max_usd) + 1e-9:",
     "        if False:",
     'PROVIDER CAP <= AUTORIZADO'),

    # Um mutante que chama uma funcao inexistente morre de NameError, e isso
    # nao mede sentinela nenhuma. Este cunha MESMO uma autorizacao por volta.
    ('M15 · a rotacao cunha autorizacao nova', SENSOR,
     "        itens, man = coletor.executar(\n"
     "            actor, entrada, token=chaves[idx], run_id='%s-p%d' % (run_id, pos),",
     "        autorizacao = coletor.az.autorizar(\n"
     "            motivo=getattr(autorizacao, 'motivo', 'TRIAL_DE_CAPACIDADE'),\n"
     "            proposito=getattr(autorizacao, 'proposito', 'T9'),\n"
     "            max_execucoes=1, max_usd=getattr(autorizacao, 'max_usd', 1.0),\n"
     "            quem_autorizou='a rotacao', porque='a rotacao',\n"
     "            condicao_de_paragem='nenhuma') if autorizacao is not None else None\n"
     "        itens, man = coletor.executar(\n"
     "            actor, entrada, token=chaves[idx], run_id='%s-p%d' % (run_id, pos),",
     'rotacao de chave nao e nova autorizacao'),

    ('M16 · a rota gratuita passa a exigir autorizacao de gasto', 'coleta/scrap_executor.py',
     "    kwargs = dict(kwargs, modo=modo)",
     "    kwargs = dict(kwargs, modo=modo)\n"
     "    if kwargs.get('autorizacao') is None:\n"
     "        raise RuntimeError('sem autorizacao de gasto')",
     'uma rota que nao gasta nao precisa de autorizacao para gastar'),

    ('M17 · nasce um segundo dono', LEI,
     "CONTRATO = 'AUTORIZACAO_DE_GASTO/v2'",
     "CONTRATO = 'AUTORIZACAO_DE_GASTO/v2'\n"
     "import spend_guard_v2  # noqa",
     'ONE CONCEPT -> ONE OWNER'),

    ('M18 · a API antiga volta e salta o modelo novo', DONO,
     "    recibo = az.conferir_e_consumir(",
     "    if isinstance(autorizacao, dict):\n"
     "        recibo = dict(autorizacao, VEREDITO='AUTORIZADO')\n"
     "    else:\n"
     "        recibo = az.conferir_e_consumir(",
     'um dicionario nao e uma autorizacao'),

    ('M19 · o contrato volta a chamar-se v1', LEI,
     "CONTRATO = 'AUTORIZACAO_DE_GASTO/v2'",
     "CONTRATO = 'AUTORIZACAO_DE_GASTO/v1'",
     'v1 ja nomeava dois comportamentos'),

    ('M20 · a relevancia passa a ser decidida aqui', LEI,
     "        v = rel.portao(sid, alvo, livro, custo='rota paga (autorizacao_de_gasto)')",
     "        v = {'VEREDITO': rel.AUTORIZA, 'ESTADO_DA_RELEVANCIA': rel.SIM,\n"
     "             'DECISAO': None, 'VERSAO_DO_PORTAO': '1', 'PORQUE': 'eu decidi'}",
     'SOURCE RELEVANCE OWNER != SPEND ENFORCER'),
]


def _copia(destino):
    pesadas = {'.git', 'data', 'node_modules', 'italia-portale', '__pycache__',
               '.tmp', 'build'}
    for nome in os.listdir(RAIZ):
        if nome in pesadas:
            continue
        o, a = os.path.join(RAIZ, nome), os.path.join(destino, nome)
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
    print('SCRAP-OWNER-01 · MUTAÇÃO DO DONO ÚNICO DA AUTORIZAÇÃO')
    print('=' * 74)
    base = tempfile.mkdtemp(prefix='owner01-mut-')
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
        for nome, rel_, velho, novo, garantia in MUTACOES:
            alvo = os.path.join(arvore, rel_)
            with open(alvo, encoding='utf-8') as f:
                original = f.read()
            if velho not in original:
                print('%-52s ALVO_AUSENTE' % nome[:52])
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
            print('%-52s %s (%d sentinelas)'
                  % (nome[:52], 'MORTA  ' if morta else 'SOBREVIVE', quantas))
            print('%-52s   guarda: %s' % ('', garantia))
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
