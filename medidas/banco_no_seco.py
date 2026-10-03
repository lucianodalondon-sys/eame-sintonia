#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O BANCO A SECO — para um executor real emitir rastro sem tocar producao.

    INSTRUMENTAR NAO PODE EXIGIR ESCREVER EM PRODUCAO.

`medidas/rastro_da_coleta.py` e o dono canonico da escrita do rastro, e ele
escreve em Postgres. A migration `024` NAO esta aplicada. Se instrumentar um
executor exigisse banco vivo, a instrumentacao so poderia ser provada no dia em
que a migration entrasse — e ate la ninguem saberia se ela funciona.

Este ficheiro e um `banco` de mentira que responde ao mesmo `.executa(sql)`.
O executor emite pelo dono canonico, sem desvio; so o destino muda.

⚠️ ISTO E UMA TRADUCAO DECLARADA, E TRADUCAO PODE DIVERGIR
-----------------------------------------------------------
As duas colunas que o `registrar()` le de volta sao GERADAS pelo banco — de
proposito, para «ninguem poder escrever um numero que fecha sem fechar». Aqui
elas sao RECALCULADAS em Python, copiando a definicao da migration 024:

    accounted_input   = passed + rejected + error_count
                        + not_run_count + unknown_count + reused
    unaccounted_input = coalesce(input_count,0) - accounted_input

Enquanto for copia, pode envelhecer. Por isso a definicao fica aqui em cima,
com o sitio de onde veio, e ha um teste que compara esta traducao com o texto
da propria migration — se a 024 mudar e isto nao, o teste reprova.

    O QUE ISTO PROVA:  o executor emite, e a conta fecha.
    O QUE NAO PROVA:   que o Postgres real aceita. Isso e `DB_TESTED`,
                       e mede-se em `provas/rastro_no_postgres.py`.
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

MIGRATION = os.path.join(RAIZ, 'supabase', 'migrations',
                         '024_a_corrida_conta_o_que_passou.sql')

# As parcelas que somam ACCOUNTED. A ordem nao importa; a lista importa.
PARCELAS = ('passed', 'rejected', 'error_count', 'not_run_count',
            'unknown_count', 'reused')

_INSERT = re.compile(
    r"insert\s+into\s+public\.etapa_da_corrida\s*\((?P<cols>[^)]*)\)"
    r"\s*values\s*\((?P<vals>.*)\)\s*returning", re.I | re.S)


def _partir(vals):
    """Parte a lista de valores respeitando as aspas do SQL.

    Um `split(',')` cortaria dentro de uma mensagem de erro que tenha virgula —
    e mensagens de erro tem virgulas.
    """
    fora, atual, dentro = [], [], False
    i = 0
    while i < len(vals):
        ch = vals[i]
        if ch == "'":
            if dentro and i + 1 < len(vals) and vals[i + 1] == "'":
                atual.append("''")
                i += 2
                continue
            dentro = not dentro
            atual.append(ch)
        elif ch == ',' and not dentro:
            fora.append(''.join(atual).strip())
            atual = []
        else:
            atual.append(ch)
        i += 1
    if atual:
        fora.append(''.join(atual).strip())
    return fora


def _numero(bruto):
    """Só conta o que é número. `null` não é zero — é ausência."""
    if bruto is None:
        return None
    b = bruto.strip().split('::')[0].strip()
    if b.lower() == 'null':
        return None
    try:
        return int(b)
    except ValueError:
        return None


class BancoNoSeco:
    """Responde ao `.executa(sql)` e nao sai da memoria."""

    def __init__(self):
        self.linhas = []          # cada passagem, como dicionario
        self.sqls = []            # o SQL literal, para quem quiser conferir

    def executa(self, sql):
        self.sqls.append(sql)
        m = _INSERT.search(sql)
        if not m:
            # ⚠️ NAO INVENTAR RESPOSTA. Um SQL que este banco nao entende tem
            # de doer aqui, e nao devolver um zero que parece saudavel.
            raise ValueError('banco a seco nao entende este SQL: %s' % sql[:120])
        cols = [c.strip() for c in m.group('cols').split(',')]
        vals = _partir(m.group('vals'))
        if len(cols) != len(vals):
            raise ValueError('colunas (%d) e valores (%d) nao batem'
                             % (len(cols), len(vals)))
        linha = dict(zip(cols, vals))

        accounted = sum(_numero(linha.get(p)) or 0 for p in PARCELAS)
        entrada = _numero(linha.get('input_count'))
        unaccounted = (entrada or 0) - accounted

        estado = (linha.get('estado') or '').split('::')[0].strip().strip("'")
        codigo = (linha.get('diagnostic_code') or '').split('::')[0].strip().strip("'")
        registo = dict(linha)
        registo['_ACCOUNTED'] = accounted
        registo['_UNACCOUNTED'] = unaccounted
        self.linhas.append(registo)
        return [(accounted, unaccounted, estado, codigo or None)]

    # ── leitura, para quem instrumenta conferir o que emitiu ────────────────
    def por_etapa(self):
        return {(l.get('etapa') or '').split('::')[0].strip().strip("'"): l
                for l in self.linhas}

    def sem_explicacao(self):
        """As passagens em que algo entrou e nao saiu por porta nenhuma."""
        return [l for l in self.linhas if l['_UNACCOUNTED'] != 0]

    def ultimo_bom(self, ordem):
        """A ultima etapa que passou, na ordem canonica."""
        passou = {(l.get('etapa') or '').split('::')[0].strip().strip("'")
                  for l in self.linhas
                  if (l.get('estado') or '').strip().strip("'").startswith('PASS')}
        bom = None
        for e in ordem:
            if e in passou:
                bom = e
        return bom


def definicao_da_migration():
    """O texto das colunas geradas, lido da propria migration.

    Serve para o teste comparar a traducao com a origem. Uma copia que ninguem
    confere e uma copia que ja divergiu e ninguem sabe.
    """
    if not os.path.exists(MIGRATION):
        return ''
    with open(MIGRATION, encoding='utf-8') as f:
        texto = f.read()
    i = texto.find('accounted_input')
    return texto[i:i + 420] if i >= 0 else ''
