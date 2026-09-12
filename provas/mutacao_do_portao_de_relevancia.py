#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A SUITE DO PORTAO DE RELEVANCIA MORDE? — prova por mutacao.

    python3 provas/mutacao_do_portao_de_relevancia.py

    UMA SUITE VERDE NAO PROVA QUE ELA MORDE.
    PROVA QUE, COM O CODIGO COMO ESTA, NADA REBENTOU.

O risco concreto deste portao nao e um bug. E o afrouxamento: alguem com
pressa, daqui a tres meses, a tirar uma linha para uma corrida passar. Se a
suite nao reparar, o portao deixa de ser uma porta e passa a ser um comentario.

Cada mutacao abaixo e um afrouxamento PLAUSIVEL — o tipo de alteracao que
alguem faria a olhar para uma corrida barrada, e nao um disparate que qualquer
leitura apanhava. Altera-se o FICHEIRO REAL, corre-se a suite REAL, e exige-se
que ela REPROVE. Depois restaura-se, e confirma-se pelo sha256.

    mutante que sobrevive = regra sem guarda
    SURVIVORS = 0   e a unica saida aceitavel.

⚠️ ESTE FICHEIRO ALTERA CODIGO EM DISCO. Restaura sempre, inclusive por
`finally`, e confere o hash no fim. Se o hash nao bater, devolve 3 e diz para
verificar a mao — nunca finge que restaurou.
"""

import hashlib
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

SUITE = 'tests.test_relevancia_da_fonte'

LEI = os.path.join('leis', 'relevancia_da_fonte.py')
PLANO = os.path.join('pedido', 'receitas.py')
CONTROLO = os.path.join('orquestrador', 'orquestrador.py')
SONDA = os.path.join('candidatas', 'prova_barata.py')


# ══════════════════════════════════════════════════════════════════════════
# AS MUTACOES — uma por cada coisa que a missao mandou mutar, e mais quatro
# ══════════════════════════════════════════════════════════════════════════
MUTACOES = (
    # ── remover o portao do caminho ─────────────────────────────────────
    {
        'NOME': 'remover o portao do orquestrador',
        'FICHEIRO': CONTROLO,
        'O_QUE_AFROUXA': 'a corrida passa a nunca ser barrada antes do gasto',
        'ONDE': '    if plano.bloqueia_a_corrida:',
        'PARA': '    if False:  # mutante',
    },
    {
        'NOME': 'o plano deixa de consultar o portao',
        'FICHEIRO': PLANO,
        'O_QUE_AFROUXA': 'o veredito nunca chega a quem gasta',
        # A ancora seguiu o codigo: a SCRAP-FLOW-01 deu dono a escolha do
        # executor, e o plano passou a consultar o portao sobre o executor
        # ESCOLHIDO em vez de sobre `execs[0]`. Uma ancora que fica na morada
        # antiga nao mata mutante nenhum — deixa de se aplicar, e esta suite
        # conta isso como SOBREVIVENTE, que e o que ela deve fazer.
        'ONDE': '    relevancia = {}\n    if escolhido is not None:',
        'PARA': '    relevancia = {}\n    if False:  # mutante',
    },
    # ── inverter UNKNOWN ────────────────────────────────────────────────
    {
        'NOME': 'UNKNOWN vira NAO',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': '«nao se concluiu» passa a fechar o assunto',
        'ONDE': '    NAO_SEI: EXIGE_AVALIACAO,',
        'PARA': '    NAO_SEI: BARRA,  # mutante',
    },
    {
        'NOME': 'UNKNOWN vira SIM',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': '«nao se concluiu» passa a autorizar gasto',
        'ONDE': '    NAO_SEI: EXIGE_AVALIACAO,',
        'PARA': '    NAO_SEI: AUTORIZA,  # mutante',
    },
    # ── tratar ERROR como NO ────────────────────────────────────────────
    {
        'NOME': 'ERRO vira NAO',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'uma falha de rede passa a ser um julgamento da fonte',
        'ONDE': '    ERRO: EXIGE_AVALIACAO,',
        'PARA': '    ERRO: BARRA,  # mutante',
    },
    # ── aceitar paid route sem decisao ──────────────────────────────────
    {
        'NOME': 'fonte nunca avaliada autoriza gasto',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'a rota paga corre sobre fonte que ninguem abriu',
        'ONDE': '    NAO_AVALIADA: EXIGE_AVALIACAO,',
        'PARA': '    NAO_AVALIADA: AUTORIZA,  # mutante',
    },
    {
        'NOME': 'custo desconhecido passa por gratuito',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'a trava do dinheiro abre para tudo o que nao se mediu',
        'ONDE': "    return isinstance(custo, str) and custo.strip().lower() == CUSTO_DECLARADO_GRATUITO",
        'PARA': '    return True  # mutante',
    },
    {
        'NOME': 'a coleta recorrente deixa de contar como gasto',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'o relogio passa a colher para sempre sem avaliacao',
        'ONDE': "    if str(acionamento or '').upper() == 'AGENDADO':\n        g.append(GASTO_RECORRENTE)",
        'PARA': '    if False:  # mutante\n        g.append(GASTO_RECORRENTE)',
    },
    {
        'NOME': 'a coleta total deixa de contar como gasto',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'o escopo TOTAL passa sem avaliacao',
        'ONDE': "    if str(escopo or '').upper() == 'TOTAL':\n        g.append(GASTO_VOLUME)",
        'PARA': '    if False:  # mutante\n        g.append(GASTO_VOLUME)',
    },
    # ── decisao de um universo vaza para outro ──────────────────────────
    {
        'NOME': 'a decisao vaza de um proposito para outro',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'um SIM em T3 abre a porta a T9',
        'ONDE': "    linhas = [l for l in (livro or [])\n"
                "              if l.get('SOURCE_ID') == sid and l.get('PROPOSITO') == alvo]",
        'PARA': "    linhas = [l for l in (livro or [])\n"
                "              if l.get('SOURCE_ID') == sid]  # mutante",
    },
    {
        'NOME': 'a fonte deixa de ser parte da chave',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'a decisao de uma fonte fala pelas outras do territorio',
        'ONDE': "    linhas = [l for l in (livro or [])\n"
                "              if l.get('SOURCE_ID') == sid and l.get('PROPOSITO') == alvo]",
        'PARA': "    linhas = [l for l in (livro or [])\n"
                "              if l.get('PROPOSITO') == alvo]  # mutante",
    },
    # ── remover evidencia obrigatoria ───────────────────────────────────
    {
        'NOME': 'SIM e NAO deixam de exigir evidencia',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'uma opiniao entra no livro com ar de medicao',
        'ONDE': '        if self.resultado in RESULTADOS_QUE_AFIRMAM and not self.evidencia:',
        'PARA': '        if False:  # mutante',
    },
    # ── remover versionamento ───────────────────────────────────────────
    {
        'NOME': 'a decisao deixa de exigir versao',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'deixa de haver como reabrir so o que a regra 1 recusou',
        'ONDE': "        if not str(self.versao or '').strip():",
        'PARA': '        if False:  # mutante',
    },
    {
        'NOME': 'a decisao deixa de exigir metodo',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'ninguem consegue repetir a avaliacao',
        'ONDE': "        if not str(self.metodo or '').strip():",
        'PARA': '        if False:  # mutante',
    },
    # ── promover candidate automaticamente ──────────────────────────────
    {
        'NOME': 'a prova barata passa a decidir',
        'FICHEIRO': SONDA,
        'O_QUE_AFROUXA': 'a amostra que se apanhou vira «o que a fonte e»',
        'ONDE': "        'DECISAO': 'NAO_TOMADA',",
        'PARA': "        'DECISAO': 'SIM',  # mutante",
    },
    {
        'NOME': 'a sonda aceita fonte fora do cadastro',
        'FICHEIRO': SONDA,
        'O_QUE_AFROUXA': 'uma fonte nasce pela porta das traseiras, sem ficha',
        'ONDE': '    if f is None:\n        raise ProvaRecusada(',
        'PARA': '    if False:\n        raise ProvaRecusada(',
    },
    {
        'NOME': 'a sonda aceita rota paga',
        'FICHEIRO': SONDA,
        'O_QUE_AFROUXA': 'avaliar passa a poder gastar sem autorizacao humana',
        'ONDE': '    if not rel.custo_e_gratuito(custo_da_rota):',
        'PARA': '    if False:  # mutante',
    },
    # ── a identidade da fonte ───────────────────────────────────────────
    {
        'NOME': 'URL passa a poder ser SOURCE_ID',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'a mesma fonte nasce outra vez quando muda de dominio',
        'ONDE': "    if any(baixo.startswith(p) for p in _PREFIXOS_DE_URL) or '/' in s:",
        'PARA': '    if False:  # mutante',
    },
    # ── o livro ─────────────────────────────────────────────────────────
    {
        'NOME': 'registar passa a reescrever o livro',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'o NAO de ontem desaparece quando se escreve o SIM de hoje',
        'ONDE': "        d['DECISOES'] = d_existente['DECISOES']",
        'PARA': "        d['DECISOES'] = []  # mutante",
    },
    {
        'NOME': 'livro ilegivel passa por livro vazio',
        'FICHEIRO': LEI,
        'O_QUE_AFROUXA': 'um ficheiro truncado faz toda a fonte voltar a NAO_AVALIADA',
        'ONDE': '        raise LivroIlegivel(\n'
                "            '%s existe e nao e JSON valido (%s). Um livro ilegivel nao e um '",
        'PARA': '        return []  # mutante\n'
                "        raise LivroIlegivel(\n"
                "            '%s existe e nao e JSON valido (%s). Um livro ilegivel nao e um '",
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
    print('MUTACAO DO PORTAO DE RELEVANCIA — a suite percebe quando ele afrouxa?')
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
        print('  dono   %-34s sha256 %s…' % (rel_path, originais[rel_path][:16]))
    print()

    if not _suite_passa():
        for rel_path in ficheiros:
            shutil.copy2(backups[rel_path], os.path.join(RAIZ, rel_path))
            os.remove(backups[rel_path])
        print('  A SUITE JA ESTAVA VERMELHA ANTES DE QUALQUER MUTACAO.')
        print('  Nao se mede mordida numa suite que ja esta a falhar.')
        return 2

    sobreviventes = []
    try:
        for m in MUTACOES:
            rel_path = m['FICHEIRO']
            caminho = os.path.join(RAIZ, rel_path)
            fonte = fontes[rel_path]
            if fonte.count(m['ONDE']) != 1:
                # ⚠️ ANCORA QUE NAO E UNICA NAO E UM MUTANTE MORTO.
                # Contar isto como defesa seria fabricar contagem: a mutacao
                # nem chegou a aplicar-se.
                sobreviventes.append(
                    (m['NOME'], 'ANCORA NAO E UNICA (%d) — a mutacao nao se aplicou'
                     % fonte.count(m['ONDE'])))
                print('  ?????  %-44s ancora ausente ou repetida' % m['NOME'][:44])
                continue
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(fonte.replace(m['ONDE'], m['PARA'], 1))
            passou = _suite_passa()
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(fonte)
            if passou:
                sobreviventes.append((m['NOME'], m['O_QUE_AFROUXA']))
                print('  VIVE   %-44s %s' % (m['NOME'][:44], m['O_QUE_AFROUXA']))
            else:
                print('  morre  %-44s %s' % (m['NOME'][:44], m['O_QUE_AFROUXA']))
    finally:
        for rel_path in ficheiros:
            shutil.copy2(backups[rel_path], os.path.join(RAIZ, rel_path))
            os.remove(backups[rel_path])

    mal_restaurado = [r for r in ficheiros
                      if _hash(os.path.join(RAIZ, r)) != originais[r]]
    print('\n  ficheiros restaurados: %s'
          % ('todos' if not mal_restaurado
             else 'NAO — VERIFICAR A MAO: %s' % ', '.join(mal_restaurado)))
    if mal_restaurado:
        return 3

    print('\n  MUTANTES  %d' % len(MUTACOES))
    print('  SURVIVORS %d' % len(sobreviventes))
    if sobreviventes:
        print('\n  Um mutante vivo e uma regra sem guarda:')
        for nome, porque in sobreviventes:
            print('    · %s — %s' % (nome, porque))
        return 1
    print('\n  Nenhum afrouxamento plausivel deste portao passa despercebido.')
    return 0


if __name__ == '__main__':
    raise SystemExit(correr())
