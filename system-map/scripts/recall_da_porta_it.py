# -*- coding: utf-8 -*-
"""QUANTO A PENEIRA APANHA, NOS ITENS ITALIANOS QUE TÊM TEXTO.

POR QUE ISTO EXISTE
-------------------
Corrigiu-se o vocabulário da porta de admissão: passou de zero palavras
italianas para vinte e nove. É uma melhoria real e é fácil de contar.

Mas contar palavras não é medir nada. Um dicionário grande não prova que a
porta acerta, do mesmo modo que ter muitas ferramentas não prova que a casa
está construída. A pergunta que interessa é outra:

    DOS ITENS ITALIANOS QUE TÊM TEXTO PARA LER, QUANTOS A PORTA DEIXA PASSAR?

E há uma condição antes dessa: só se pode medir acerto em itens que TÊM texto.
Julgar um item vazio é julgar o vazio — a resposta certa aí é NÃO SEI, e foi
por isso que a lei da ausência foi consertada primeiro.

COMO SE LÊ O RESULTADO
----------------------
SIM       a porta reconheceu o assunto
NAO       a porta viu prova de que o item é de outro mundo
NAO_SEI   não achou palavra nenhuma — o léxico não chegou lá

Um NAO_SEI alto não é a porta a falhar: é a porta a dizer onde faltam
palavras. É informação, e a única razão de ela ser visível é a lei da ausência.

CORRER
------
    py system-map/scripts/recall_da_porta_it.py

Não lê a rede, não gasta nada, não altera nenhum dado.
"""
import collections
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import admissao as adm  # noqa: E402

CENSO = os.path.join(RAIZ, 'system-map', 'data', 'corpus-it.generated.json')
SAIDA = os.path.join(RAIZ, 'system-map', 'data', 'recall-porta-it.generated.json')

CAMPOS = ('texto', 'TEXTO', 'TITLE', 'TITULO', 'title', 'titulo',
          'DESCRIPTION', 'DESCRICAO', 'description', 'descricao',
          'TRANSCRIPT', 'TRANSCRICAO', 'COMMENT', 'COMMENT_TEXT',
          'CONTENT', 'BODY', 'SNIPPET', 'ABSTRACT', 'OBSERVATION')
MINIMO = 20


def colher_itens(no, saco, ficheiro):
    """Junta os pedaços de prosa de cada linha que tenha alguma."""
    if isinstance(no, dict):
        prosa = []
        for c in CAMPOS:
            v = no.get(c)
            if isinstance(v, str) and len(v.strip()) >= MINIMO:
                prosa.append(v.strip())
        if prosa:
            saco.append({'FICHEIRO': ficheiro,
                         'id': no.get('id') or no.get('ID') or 'sem-id',
                         'texto': ' '.join(prosa)})
        for v in no.values():
            colher_itens(v, saco, ficheiro)
    elif isinstance(no, list):
        for x in no:
            colher_itens(x, saco, ficheiro)


def main():
    if not os.path.exists(CENSO):
        raise SystemExit('corre primeiro: py system-map/scripts/censo_do_corpus_it.py')
    censo = json.load(io.open(CENSO, encoding='utf-8'))

    itens = []
    for f in censo['ONDE_ESTA_O_TEXTO_ITALIANO']:
        caminho = os.path.join(RAIZ, f['FICHEIRO'])
        try:
            colher_itens(json.load(io.open(caminho, encoding='utf-8')),
                         itens, f['FICHEIRO'])
        except Exception:
            continue

    contas = collections.Counter()
    por_ficheiro = {}
    exemplos = {'SIM': [], 'NAO': [], 'NAO_SEI': []}
    for it in itens:
        d = adm.decidir({'id': it['id'], 'texto': it['texto'],
                         'source_id': 'IT-RECALL', 'fact_time': '2026-09-07'},
                        'T7')
        r = d.resultado
        contas[r] += 1
        por_ficheiro.setdefault(it['FICHEIRO'], collections.Counter())[r] += 1
        if len(exemplos.get(r, [])) < 4:
            exemplos.setdefault(r, []).append({
                'FICHEIRO': it['FICHEIRO'],
                'TEXTO': it['texto'][:160],
                'PORQUE': d.motivo,
                'PROVA': d.evidencia,
            })

    total = sum(contas.values())
    if total == 0:
        raise SystemExit('nenhum item italiano com texto — nada para medir')

    estado = {
        'O_QUE_ISTO_E': ('Quanto a porta de admissao apanha nos itens italianos '
                         'que TEM texto. Nao mede tamanho de vocabulario: mede '
                         'decisoes sobre itens reais.'),
        'COMO_REFAZER': 'py system-map/scripts/recall_da_porta_it.py',
        'VERSAO_DA_REGRA': adm.VERSAO_DA_REGRA,
        'ITENS_COM_TEXTO': total,
        'DECISOES': dict(contas),
        'EM_PERCENTAGEM': {k: round(100.0 * v / total, 1) for k, v in contas.items()},
        'POR_FICHEIRO': {k: dict(v) for k, v in sorted(por_ficheiro.items())},
        'EXEMPLOS': exemplos,
        'O_QUE_ISTO_NAO_DIZ': (
            'Nao diz se as decisoes estao CERTAS. Para isso era preciso alguem '
            'que leia italiano marcar a mao o que devia passar, e essa lista '
            'nao existe. Sem ela, o acerto e NAO SEI — e dizer que e alto seria '
            'inventar.'),
    }
    with io.open(SAIDA, 'w', encoding='utf-8') as fh:
        json.dump(estado, fh, ensure_ascii=False, indent=1)
        fh.write('\n')

    print('A PENEIRA, NOS ITENS ITALIANOS COM TEXTO')
    print('  itens medidos ......... %d' % total)
    print('  versao da regra ....... %s' % adm.VERSAO_DA_REGRA)
    for r in ('SIM', 'NAO', 'NAO_SEI', 'NAO_SE_APLICA', 'ERRO'):
        if contas.get(r):
            print('  %-12s ......... %4d  (%.1f%%)'
                  % (r, contas[r], 100.0 * contas[r] / total))
    print()
    print('  gravado: %s' % os.path.relpath(SAIDA, RAIZ).replace('\\', '/'))


if __name__ == '__main__':
    main()
