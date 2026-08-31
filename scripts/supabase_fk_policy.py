"""Declara ON DELETE e indices para cada chave estrangeira, no schema canonico.

Duas coisas que o Postgres NAO faz sozinho e que custam caro depois:

1. Ele indexa PK e UNIQUE, mas NAO a coluna que aponta para fora. Sem indice, todo
   join do produto varre a tabela inteira — e o produto e feito de joins.

2. Sem ON DELETE declarado, o padrao e NO ACTION. Nao esta errado; esta calado. E
   um comportamento calado vira surpresa no primeiro DELETE.

A politica abaixo e JULGAMENTO, nao derivacao — por isso fica escrita e justificada.

Uso:
    py scripts/supabase_fk_policy.py --sync
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-CANONICAL-SCHEMA.json')

# tabelas cuja linha e HISTORIA: nunca podem ser apagadas por baixo de quem as cita
IMUTAVEIS = ('evidence', 'source', 'source_snapshot', 'publish_run', 'ontology_term',
             'observation', 'content_entity')

POLITICA = {
    'REGRA_1_IMUTAVEIS': (
        'FK que aponta para %s e sempre RESTRICT. Evidencia e fonte sao historia: '
        'apagar uma delas por baixo de um objeto que a cita destruiria a linhagem '
        'que este produto inteiro existe para preservar.' % ', '.join(IMUTAVEIS)),
    'REGRA_2_FILHA_CAI_COM_A_RAIZ': (
        'FK que faz parte da CHAVE PRIMARIA da tabela e CASCADE. A tabela filha nao '
        'existe sem a raiz: phenomenon_case sem attention_object nao e nada.'),
    'REGRA_3_OBRIGATORIA': (
        'FK NOT NULL fora da PK e RESTRICT. A linha depende dela; apagar o alvo '
        'deixaria a linha invalida.'),
    'REGRA_4_OPCIONAL': (
        'FK que aceita nulo e SET NULL. O vinculo some, a linha continua — e a '
        'ausencia fica declarada como ausencia.'),
    'ORDEM': 'a regra 1 vence as outras tres.',
}


def _pk(t):
    if t.get('pk'):
        return list(t['pk'])
    return [c['name'] for c in t['columns'] if c.get('pk')]


def decidir(tabela, coluna):
    alvo = coluna['fk'].split('.')[0]
    if alvo in IMUTAVEIS:
        return 'RESTRICT', 'REGRA_1_IMUTAVEIS'
    if coluna['name'] in _pk(tabela):
        return 'CASCADE', 'REGRA_2_FILHA_CAI_COM_A_RAIZ'
    if coluna.get('null') is False:
        return 'RESTRICT', 'REGRA_3_OBRIGATORIA'
    return 'SET NULL', 'REGRA_4_OPCIONAL'


def sincronizar():
    with open(SCHEMA, encoding='utf-8') as fh:
        d = json.load(fh)

    contagem, indices = {}, []
    for t in d['TABLES']:
        pk = _pk(t)
        uq = [u[0] for u in t.get('unique', [])]
        for c in t['columns']:
            if not c.get('fk'):
                continue
            acao, regra = decidir(t, c)
            c['on_delete'] = acao
            c['on_delete_rule'] = regra
            contagem[acao] = contagem.get(acao, 0) + 1
            # indice so onde o Postgres nao cria sozinho
            if pk[:1] != [c['name']] and c['name'] not in uq:
                indices.append({'table': t['name'], 'column': c['name'],
                                'name': '%s_%s_idx' % (t['name'], c['name'])})

    d['FOREIGN_KEY_POLICY'] = POLITICA
    d['INDEXES'] = {
        'POR_QUE': ('O Postgres indexa PK e UNIQUE, e NAO a coluna que aponta para fora. '
                    'Sem estes indices todo join do produto varre a tabela inteira, e o '
                    'produto e feito de joins. Nao ha indice em coluna que ja e a primeira '
                    'da PK ou de um UNIQUE: seria duplicado.'),
        'LISTA': indices,
    }
    with open(SCHEMA, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    return contagem, len(indices)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if '--sync' not in sys.argv:
        print('use --sync'); raise SystemExit(1)
    c, n = sincronizar()
    print('ON DELETE por acao:', json.dumps(c, ensure_ascii=False))
    print('indices declarados:', n)
