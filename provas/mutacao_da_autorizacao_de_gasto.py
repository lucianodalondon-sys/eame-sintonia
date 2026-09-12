#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SUITE DA AUTORIZACAO DE GASTO MORDE? — prova por mutacao.

    python3 provas/mutacao_da_autorizacao_de_gasto.py

    UMA SUITE VERDE NAO PROVA QUE ELA MORDE.
    PROVA QUE, COM O CODIGO COMO ESTA, NADA REBENTOU.

O risco desta guarda nao e um bug: e o afrouxamento. Uma corrida barrada, uma
pressa, uma linha comentada «so para testar» — e a porta do dinheiro fica
aberta sem que nenhum teste mude de cor.

Cada mutacao altera o FICHEIRO REAL do dono, corre a suite REAL, e exige que
ela REPROVE. Depois restaura, e confere pelo sha256.

    mutante que sobrevive = regra sem guarda
    SURVIVORS = 0   e a unica saida aceitavel.

⚠️ ANCORA QUE NAO E UNICA CONTA COMO SOBREVIVENTE, nunca como mutante morto:
a mutacao nem chegou a aplicar-se, e contar isso como defesa seria fabricar
contagem.
"""

import hashlib
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

SUITE = 'tests.test_autorizacao_de_gasto'

GUARDA = os.path.join('leis', 'autorizacao_de_gasto.py')
PORTA = os.path.join('coleta', 'coletor.py')
SENSOR = os.path.join('regras', 'sensor_coleta.py')
INSTA = os.path.join('coleta', 'instagram_coleta.py')


MUTACOES = (
    # ── M1 · remover a guarda ───────────────────────────────────────────
    # ⚠️ A PRIMEIRA VERSAO DESTE MUTANTE ERA UM NO-OP: `{} or X` avalia X,
    # porque `{}` e falso. Ele «sobreviveu» sem nunca ter mudado nada — e um
    # mutante que nao muda o codigo nao mede a suite, mede a minha distraccao.
    #
    #     UM MUTANTE QUE NAO MUTA E UM TESTE QUE SE ENGANA A SI PROPRIO.
    {
        'NOME': 'M1 remover a guarda da porta paga',
        'FICHEIRO': PORTA,
        'O_QUE_AFROUXA': 'o POST passa a sair sem ninguem conferir nada',
        'ONDE': '''    recibo_da_autorizacao = ag.conferir_e_consumir(
        autorizacao,
        motivo=motivo_do_gasto or ag.COLETA_NORMAL,
        proposito=proposito,
        source_id=source_id,
        teto_usd=teto_usd)''',
        'PARA': "    recibo_da_autorizacao = {'VEREDITO': 'AUTORIZADO'}  # mutante",
    },
    # ── M2..M4 · as ausencias passam a autorizar ────────────────────────
    {
        'NOME': 'M2 NAO_AVALIADA passa a autorizar',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'fonte que ninguem abriu compra',
        'ONDE': "        if v['VEREDITO'] != rel.AUTORIZA:",
        'PARA': "        if v['ESTADO_DA_RELEVANCIA'] == rel.NAO:  # mutante",
    },
    {
        'NOME': 'M3 NAO_SEI passa a autorizar',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': '«nao se concluiu» vira «pode gastar»',
        'ONDE': "        v = rel.portao(sid, alvo, livro, custo='rota paga (autorizacao_de_gasto)')",
        'PARA': "        v = rel.portao(sid, alvo, livro, custo='rota paga (autorizacao_de_gasto)')\n"
                "        if v['ESTADO_DA_RELEVANCIA'] == rel.NAO_SEI:\n"
                "            v = dict(v, VEREDITO=rel.AUTORIZA)  # mutante",
    },
    {
        'NOME': 'M4 proposito errado passa a autorizar',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'um SIM em T3 compra em T9',
        'ONDE': "    if str(autorizacao.proposito) != str(proposito or '').strip():",
        'PARA': '    if False:  # mutante',
    },
    # ── M5 · credencial vira autorizacao ────────────────────────────────
    # ⚠️ TAMBEM ERA NO-OP: `a if not token else a` devolve `a` nos dois ramos.
    {
        'NOME': 'M5 autorizacao ausente passa a ser aceite',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'chamar sem autorizacao volta a comprar — ter a chave basta',
        'ONDE': "    if autorizacao is None:\n        raise GastoRecusado('AUTORIZACAO_AUSENTE'",
        'PARA': "    if autorizacao is None and False:\n        raise GastoRecusado('AUTORIZACAO_AUSENTE'",
    },
    # ── M6 · orcamento sozinho basta ────────────────────────────────────
    {
        'NOME': 'M6 ter orcamento dispensa a relevancia',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'dinheiro na conta compra decisao de fonte',
        'ONDE': '    if motivo == COLETA_NORMAL:',
        'PARA': '    if motivo == COLETA_NORMAL and max_usd is None:  # mutante',
    },
    # ── M7 · probe sem limite ───────────────────────────────────────────
    {
        'NOME': 'M7 probe sem teto de execucoes',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'o probe vira coleta com outro nome',
        'ONDE': '    if not max_execucoes or int(max_execucoes) < 1:',
        'PARA': '    if False:  # mutante',
    },
    {
        'NOME': 'M7b probe sem teto de dolares',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'cheque em branco para avaliar uma fonte',
        'ONDE': '    if max_usd is None or float(max_usd) <= 0:',
        'PARA': '    if False:  # mutante',
    },
    # ── M8 · trial disfarcado de coleta ─────────────────────────────────
    {
        'NOME': 'M8 trial passa por coleta normal',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'o motivo deixa de ter de bater com o autorizado',
        'ONDE': '    if autorizacao.motivo != motivo:',
        'PARA': '    if False:  # mutante',
    },
    # ── M9 · o transporte contorna ──────────────────────────────────────
    {
        'NOME': 'M9 a guarda desce para o transporte (e o sensor troca-o)',
        'FICHEIRO': SENSOR,
        'O_QUE_AFROUXA': 'a autorizacao deixa de atravessar o caminho do sensor',
        'ONDE': '            autorizacao=autorizacao,',
        'PARA': '            autorizacao=None,  # mutante',
    },
    # ── M10/M11 · os dois donos voltam a decidir ────────────────────────
    {
        'NOME': 'M10 probe e trial deixam de exigir quem assina',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'gasto por excecao sem ninguem que responda por ele',
        'ONDE': "    if not str(quem_autorizou or '').strip():",
        'PARA': '    if False:  # mutante',
    },
    {
        'NOME': 'M11 o coletor aceita autorizacao fabricada',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'qualquer objecto com os campos certos compra',
        'ONDE': '    if not isinstance(autorizacao, Autorizacao) or autorizacao._selo is not _SELO:',
        'PARA': '    if False:  # mutante',
    },
    # ── M12 · o segundo POST ────────────────────────────────────────────
    {
        'NOME': 'M12 a autorizacao deixa de se gastar',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'uma autorizacao paga tantas execucoes quantas chaves houver',
        'ONDE': '    autorizacao._gastas += 1',
        'PARA': '    autorizacao._gastas += 0  # mutante',
    },
    {
        'NOME': 'M12b o teto de execucoes deixa de ser conferido',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'o retry pago passa por cima do limite',
        'ONDE': '    if autorizacao.restantes <= 0:',
        'PARA': '    if False:  # mutante',
    },
    # ── M13 · URL como identidade ───────────────────────────────────────
    {
        'NOME': 'M13 URL aceite como SOURCE_ID',
        'FICHEIRO': os.path.join('leis', 'relevancia_da_fonte.py'),
        'O_QUE_AFROUXA': 'a mesma fonte nasce outra vez quando muda de dominio',
        'ONDE': "    if any(baixo.startswith(p) for p in _PREFIXOS_DE_URL) or '/' in s:",
        'PARA': '    if False:  # mutante',
    },
    # ── M14 · a trava do fornecedor ─────────────────────────────────────
    {
        'NOME': 'M14 o teto do fornecedor deixa de ser exigido',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'some a unica trava que sobrevive a um defeito nosso',
        'ONDE': '        if teto_usd is None:\n            raise GastoRecusado(',
        'PARA': '        if teto_usd is None and False:\n            raise GastoRecusado(',
    },
    {
        'NOME': 'M14b o teto pedido pode passar do autorizado',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'autoriza-se um centimo e gasta-se cinco dolares',
        'ONDE': '        if float(teto_usd) > float(autorizacao.max_usd) + 1e-9:',
        'PARA': '        if False:  # mutante',
    },
    # ── M15/M16 · a autorizacao viaja ───────────────────────────────────
    {
        'NOME': 'M15 autorizacao reutilizada noutra fonte',
        'FICHEIRO': GUARDA,
        'O_QUE_AFROUXA': 'autoriza-se uma fonte e compra-se outra',
        'ONDE': "        if str(source_id or '').strip() != autorizacao.source_id:",
        'PARA': '        if False:  # mutante',
    },
    {
        'NOME': 'M16 autorizacao reutilizada noutro proposito',
        'FICHEIRO': INSTA,
        'O_QUE_AFROUXA': 'o adapter deixa de declarar o proposito que esta a comprar',
        'ONDE': "            proposito=getattr(autorizacao, 'proposito', None),",
        'PARA': "            proposito='QUALQUER',  # mutante",
    },
)


def _hash(caminho):
    with open(caminho, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def _suite_passa():
    r = subprocess.run([sys.executable, '-m', 'unittest', SUITE],
                       cwd=RAIZ, capture_output=True, text=True)
    return r.returncode == 0


def correr():
    print('MUTACAO DA AUTORIZACAO DE GASTO — a suite percebe quando ela afrouxa?')
    print('=' * 78)
    print('  suite  %s' % SUITE)

    ficheiros = sorted({m['FICHEIRO'] for m in MUTACOES})
    originais, fontes, backups = {}, {}, {}
    for rel_path in ficheiros:
        caminho = os.path.join(RAIZ, rel_path)
        originais[rel_path] = _hash(caminho)
        with open(caminho, encoding='utf-8') as f:
            fontes[rel_path] = f.read()
        backups[rel_path] = caminho + '.mutacao.bak'
        shutil.copy2(caminho, backups[rel_path])
        print('  dono   %-36s sha256 %s…' % (rel_path, originais[rel_path][:16]))
    print()

    if not _suite_passa():
        for rel_path in ficheiros:
            shutil.copy2(backups[rel_path], os.path.join(RAIZ, rel_path))
            os.remove(backups[rel_path])
        print('  A SUITE JA ESTAVA VERMELHA ANTES DE QUALQUER MUTACAO.')
        return 2

    sobreviventes = []
    try:
        for m in MUTACOES:
            rel_path = m['FICHEIRO']
            caminho = os.path.join(RAIZ, rel_path)
            fonte = fontes[rel_path]
            if fonte.count(m['ONDE']) != 1:
                sobreviventes.append(
                    (m['NOME'], 'ANCORA NAO E UNICA (%d) — nao se aplicou'
                     % fonte.count(m['ONDE'])))
                print('  ?????  %-48s ancora ausente ou repetida' % m['NOME'][:48])
                continue
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(fonte.replace(m['ONDE'], m['PARA'], 1))
            passou = _suite_passa()
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(fonte)
            if passou:
                sobreviventes.append((m['NOME'], m['O_QUE_AFROUXA']))
                print('  VIVE   %-48s %s' % (m['NOME'][:48], m['O_QUE_AFROUXA']))
            else:
                print('  morre  %-48s %s' % (m['NOME'][:48], m['O_QUE_AFROUXA']))
    finally:
        for rel_path in ficheiros:
            shutil.copy2(backups[rel_path], os.path.join(RAIZ, rel_path))
            os.remove(backups[rel_path])

    mal = [r for r in ficheiros if _hash(os.path.join(RAIZ, r)) != originais[r]]
    print('\n  ficheiros restaurados: %s'
          % ('todos' if not mal else 'NAO — VERIFICAR A MAO: %s' % ', '.join(mal)))
    if mal:
        return 3

    print('\n  MUTANTES  %d' % len(MUTACOES))
    print('  SURVIVORS %d' % len(sobreviventes))
    if sobreviventes:
        print('\n  Um mutante vivo e uma regra sem guarda:')
        for nome, porque in sobreviventes:
            print('    · %s — %s' % (nome, porque))
        return 1
    print('\n  Nenhum afrouxamento plausivel desta guarda passa despercebido.')
    return 0


if __name__ == '__main__':
    raise SystemExit(correr())
