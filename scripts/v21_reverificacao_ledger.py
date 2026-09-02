#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""§12 · O LIVRO-RAZAO DA REVERIFICACAO dos 35 achados BLOQUEIA_ENTREGA.

    python3 scripts/v21_reverificacao_ledger.py

POR QUE ESTE ARQUIVO EXISTE
---------------------------
Os 99 achados da auditoria nunca passaram pela fase de refutacao: a missao foi
pausada antes. O handoff e explicito — um achado nao refutado nao e um defeito,
e uma suspeita. Este script le o resultado da reverificacao (medicao + dois
ceticos independentes + juiz onde houve queda) e monta a tabela que diz, achado
a achado, o que sobreviveu.

    TRATAR SUSPEITA COMO DEFEITO FAZ CONSERTAR O QUE NAO ESTA QUEBRADO.
    TRATAR COMO RUIDO DEIXA O DEFEITO PASSAR. OS DOIS ERROS CUSTAM CARO.

COBERTURA PARCIAL SE DECLARA, NAO SE ESCONDE
---------------------------------------------
Se nem todos os 35 tiverem sido reverificados, o relatorio diz QUAIS FALTAM e
recusa-se a apresentar percentagem sobre o total. Um resumo que arredonda
cobertura parcial para "pronto" e a mesma mentira que o relatorio escrito a mao.
"""
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRUTO = os.path.join(ROOT, 'handoff', 'paused-v2', 'reverificacao')
ACHADOS_ORIGEM = os.path.join(ROOT, 'handoff', 'paused-v2',
                              'ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json')

CLASSES = ('CONFIRMED_BLOCKER', 'NEEDS_CORRECTION', 'ALREADY_FIXED', 'FALSE_POSITIVE')
# So estas duas exigem trabalho no dado. As outras duas encerram o achado.
EXIGEM_ACAO = ('CONFIRMED_BLOCKER', 'NEEDS_CORRECTION')


def esperados():
    """Os 35 BLOQUEIA_ENTREGA, na ordem em que foram numerados B01..B35."""
    with open(ACHADOS_ORIGEM, encoding='utf-8') as fh:
        d = json.load(fh)
    blk = [a for a in d['ACHADOS'] if a['GRAVIDADE'] == 'BLOQUEIA_ENTREGA']
    return {f'B{i:02d}': a for i, a in enumerate(blk, 1)}


def coletar():
    if not os.path.isdir(BRUTO):
        sys.exit(f'nao achei a evidencia bruta em {BRUTO}')
    por_id, medicoes = {}, []
    for nome in sorted(os.listdir(BRUTO)):
        if not nome.endswith('.json'):
            continue
        with open(os.path.join(BRUTO, nome), encoding='utf-8') as fh:
            r = json.load(fh)
        medicoes.extend(r.get('MEDICAO_POR_GRUPO') or [])
        for a in r.get('ACHADOS') or []:
            aid = a.get('ID')
            if not aid:
                continue
            if aid in por_id:
                # dois arquivos falando do mesmo achado: nao escolher em silencio
                a['_CONFLITO_DE_ARQUIVO'] = True
            por_id[aid] = a
    return por_id, medicoes


def main():
    todos = esperados()
    feitos, medicoes = coletar()
    faltam = [i for i in sorted(todos) if i not in feitos]

    por_classe = Counter(a['CLASSIFICACAO_FINAL'] for a in feitos.values())
    por_grupo = defaultdict(Counter)
    for a in feitos.values():
        por_grupo[a['GRUPO']][a['CLASSIFICACAO_FINAL']] += 1

    acao = [a for a in feitos.values() if a['CLASSIFICACAO_FINAL'] in EXIGEM_ACAO]
    juiz = [a for a in feitos.values() if a.get('DECIDIDO_POR') == 'JUIZ']
    derrub = [a for a in feitos.values()
              if a.get('PRIMEIRA_LEITURA', {}).get('CLASSIFICACAO')
              and a['PRIMEIRA_LEITURA']['CLASSIFICACAO'] != a['CLASSIFICACAO_FINAL']]

    saida = {
        'ESTADO': ('COMPLETO' if not faltam else 'PARCIAL'),
        'ESPERADOS': len(todos),
        'REVERIFICADOS': len(feitos),
        'FALTAM': faltam,
        'AVISO_DE_COBERTURA': (
            None if not faltam else
            f'{len(faltam)} dos {len(todos)} achados BLOQUEIA_ENTREGA ainda NAO foram '
            f'reverificados: {", ".join(faltam)}. Nenhuma conclusao deste arquivo vale '
            f'para eles. Ausencia de veredito NAO e veredito de ausencia.'),
        'POR_CLASSIFICACAO': {c: por_classe.get(c, 0) for c in CLASSES},
        'EXIGEM_ACAO': len(acao),
        'DECIDIDOS_POR_JUIZ': len(juiz),
        'CLASSIFICACAO_MUDADA_PELA_REFUTACAO': [
            {'ID': a['ID'],
             'DE': a['PRIMEIRA_LEITURA']['CLASSIFICACAO'],
             'PARA': a['CLASSIFICACAO_FINAL']} for a in sorted(derrub, key=lambda x: x['ID'])],
        'POR_GRUPO': {g: dict(c) for g, c in sorted(por_grupo.items())},
        'ACHADOS': [],
    }

    for aid in sorted(feitos):
        a = feitos[aid]
        pl = a.get('PRIMEIRA_LEITURA') or {}
        saida['ACHADOS'].append({
            'ID': aid,
            'TITULO': todos[aid]['TITULO'],
            'GRUPO': a.get('GRUPO'),
            'CLASSIFICACAO_FINAL': a['CLASSIFICACAO_FINAL'],
            'DECIDIDO_POR': a.get('DECIDIDO_POR'),
            'VOTOS_DOS_CETICOS': a.get('VOTOS'),
            'CONFIANCA': pl.get('CONFIANCA'),
            'REPRODUZ': pl.get('REPRODUZ'),
            'EVIDENCIA_ATUAL': pl.get('EVIDENCIA_ATUAL'),
            'O_QUE_MEDI': pl.get('O_QUE_MEDI'),
            'ONDE_EXATO': pl.get('ONDE_EXATO'),
            'LEI_VIOLADA': pl.get('LEI_VIOLADA'),
            'CORRECAO_PROPOSTA': pl.get('CORRECAO_PROPOSTA'),
            'CONFLITO_DE_ARQUIVO': a.get('_CONFLITO_DE_ARQUIVO', False),
        })

    saida['MEDICAO_POR_GRUPO'] = medicoes
    destino = os.path.join(ROOT, 'handoff', 'paused-v2', 'REVERIFICACAO-LEDGER.json')
    with open(destino, 'w', encoding='utf-8') as fh:
        json.dump(saida, fh, ensure_ascii=False, indent=1)

    print(f"== §12 · REVERIFICACAO DOS BLOQUEADORES · {saida['ESTADO']} ==")
    print(f"  reverificados : {len(feitos)} de {len(todos)}")
    for c in CLASSES:
        print(f"    {c:18s}: {por_classe.get(c,0)}")
    print(f"  exigem acao no dado : {len(acao)}")
    print(f"  decididos por juiz  : {len(juiz)}")
    if derrub:
        print(f"  a refutacao MUDOU a classificacao em {len(derrub)}:")
        for a in sorted(derrub, key=lambda x: x['ID']):
            print(f"      {a['ID']}: {a['PRIMEIRA_LEITURA']['CLASSIFICACAO']} -> {a['CLASSIFICACAO_FINAL']}")
    if faltam:
        print(f"  !! FALTAM {len(faltam)}: {', '.join(faltam)}")
        print("     (cobertura parcial declarada de proposito — nao ha percentagem sobre o total)")
    print(f"  gravado: {destino}")


if __name__ == '__main__':
    main()
