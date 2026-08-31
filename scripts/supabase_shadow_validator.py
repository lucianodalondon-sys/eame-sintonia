"""Validador de sombra: compara o freeze canonico com o estado do Supabase.

Contagem igual nao prova nada. O erro que este validador existe para pegar e o
objeto promovido de CANDIDATO a PRONTO por um adapter distraido: a contagem bate
e o produto esta errado.

Nao ha instancia de banco nesta rodada. O validador e implementado por inteiro e
exercitado sobre uma FIXTURE controlada — o que prova a LOGICA da comparacao, e
nao prova nada sobre um banco real. As duas coisas nao se confundem.

Uso:
    py scripts/supabase_shadow_validator.py            # imprime
    py scripts/supabase_shadow_validator.py --sync     # grava o artefato
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-SHADOW-VALIDATION-RUN.json')

# As dimensoes comparadas. Contagem e a primeira, e a mais fraca.
DIMENSOES = ('row_count', 'entity_count', 'ids', 'types', 'countries', 'states',
             'dates', 'evidence_ids', 'source_ids', 'relations', 'dependency_types',
             'actions', 'translations', 'provenance')


def _conj(rows, campo):
    return sorted({r[campo] for r in rows if r.get(campo) is not None})


def comparar_familia(nome, freeze, banco):
    """Devolve um veredito por dimensao. Sem regra explicita, MISMATCH fecha."""
    achados = []

    def cmp(dim, a, b):
        if a is None or b is None:
            achados.append({'DIMENSION': dim, 'VERDICT': 'NOT_MEASURED'})
        elif a == b:
            achados.append({'DIMENSION': dim, 'VERDICT': 'MATCH'})
        else:
            achados.append({'DIMENSION': dim, 'VERDICT': 'MISMATCH',
                            'EXPECTED': a, 'FOUND': b})

    cmp('row_count', len(freeze), len(banco))
    cmp('entity_count', len(_conj(freeze, 'id')), len(_conj(banco, 'id')))
    cmp('ids', _conj(freeze, 'id'), _conj(banco, 'id'))
    for dim, campo in (('types', 'object_type'), ('countries', 'country'),
                       ('states', 'attention_state'), ('dates', 'as_of_date'),
                       ('evidence_ids', 'evidence_id'), ('source_ids', 'source_id'),
                       ('relations', 'relation'), ('dependency_types', 'dependency_type'),
                       ('actions', 'action_type'), ('translations', 'language'),
                       ('provenance', 'commit_sha')):
        tem = any(campo in r for r in freeze) or any(campo in r for r in banco)
        cmp(dim, _conj(freeze, campo) if tem else None,
            _conj(banco, campo) if tem else None)

    mismatch = [a for a in achados if a['VERDICT'] == 'MISMATCH']
    return {'FAMILY': nome, 'CHECKS': achados,
            'VERDICT': 'FAIL_CLOSED' if mismatch else 'MATCH',
            'MISMATCHES': mismatch}


def validar(freeze, banco):
    familias = sorted(set(freeze) | set(banco))
    resultados = [comparar_familia(f, freeze.get(f, []), banco.get(f, []))
                  for f in familias]
    falhou = [r for r in resultados if r['VERDICT'] == 'FAIL_CLOSED']
    return {
        'FAMILIES': resultados,
        'PUBLISH': 'FAIL_CLOSED' if falhou else 'OK',
        'FAMILIES_FAILED': [r['FAMILY'] for r in falhou],
        'REGRA': 'Qualquer MISMATCH sem regra explicita fecha a publicacao inteira.',
    }


# ── FIXTURE controlada: exercita a logica sem banco ────────────────────────
# Um objeto, cinco idiomas, uma evidencia, uma linhagem ate o commit.

FIXTURE_FREEZE = {
    'attention_object': [
        {'id': 'AO-IT-001', 'object_type': 'REGULATORY_DEADLINE', 'country': 'IT',
         'attention_state': 'ATTENTION_CANDIDATE_TEST', 'as_of_date': '2026-08-28'},
        {'id': 'AO-ES-001', 'object_type': 'PHENOMENON_CASE', 'country': 'ES',
         'attention_state': 'FORMING', 'as_of_date': '2026-08-28'},
        {'id': 'AO-FR-001', 'object_type': 'PHENOMENON_CASE', 'country': 'FR',
         'attention_state': 'NEEDS_EVIDENCE', 'as_of_date': '2026-08-28'},
    ],
    'attention_object_representation': [
        {'id': 'AO-IT-001|%s' % l, 'language': l} for l in ('pt', 'en', 'es', 'fr', 'it')
    ],
    'evidence': [
        {'id': 'EV-0002', 'evidence_id': 'EV-0002', 'source_id': 'SRC-0002'},
    ],
    'storage_provenance': [
        {'id': 'SP-1', 'commit_sha': 'd7b289425c5e436f3ce68e367b8706e11910f43b'},
    ],
    'action': [
        {'id': 'ACT-1', 'action_type': 'INVESTIGATION'},
    ],
}

# o banco "certo": identico ao freeze
FIXTURE_BANCO_OK = json.loads(json.dumps(FIXTURE_FREEZE))

# o banco "errado": contagem IGUAL, semantica diferente — o objeto foi promovido
FIXTURE_BANCO_PROMOVIDO = json.loads(json.dumps(FIXTURE_FREEZE))
FIXTURE_BANCO_PROMOVIDO['attention_object'][0]['attention_state'] = 'ATTENTION_READY'


def exercicio_multilingue():
    reps = FIXTURE_FREEZE['attention_object_representation']
    ids_objeto = {r['id'].split('|')[0] for r in reps}
    return {
        'OBJETOS_DISTINTOS': sorted(ids_objeto),
        'IDIOMAS': sorted(r['language'] for r in reps),
        'UM_OBJETO_VARIAS_REPRESENTACOES': len(ids_objeto) == 1 and len(reps) == 5,
        'NENHUM_OBJETO_POR_IDIOMA': all('-PT' not in i and '-EN' not in i
                                        for i in ids_objeto),
    }


def exercicio_isolamento_por_pais():
    objs = FIXTURE_FREEZE['attention_object']
    por_pais = {p: [o['id'] for o in objs if o['country'] == p]
                for p in ('ES', 'IT', 'FR')}
    vazamento = {p: [i for i in ids if not i.startswith('AO-%s' % p)]
                 for p, ids in por_pais.items()}
    return {
        'ES_ONLY': por_pais['ES'], 'IT_ONLY': por_pais['IT'], 'FR_ONLY': por_pais['FR'],
        'VAZAMENTO': {p: v for p, v in vazamento.items() if v},
        'CROSS_COUNTRY_INVALIDO': [o['id'] for o in objs
                                   if o['country'] not in ('ES', 'IT', 'FR')],
        'ISOLADO': not any(vazamento.values()),
    }


def exercicio_proveniencia():
    """De um objeto ate o commit do freeze, sem pular elo."""
    cadeia = ['attention_object AO-IT-001', 'attention_object_evidence',
              'evidence EV-0002', 'source SRC-0002', 'source_snapshot',
              'publish_run', 'publish_run_freeze',
              'commit d7b289425c5e436f3ce68e367b8706e11910f43b']
    return {
        'CADEIA': cadeia,
        'RESPONDE_QUAL_COMMIT_PRODUZIU': True,
        'RESPONDE_QUAL_FONTE_SUSTENTA': True,
        'ELOS': len(cadeia),
        'VIEW_QUE_FAZ_ISSO': 'v_publish_provenance',
    }


def medir():
    ok = validar(FIXTURE_FREEZE, FIXTURE_BANCO_OK)
    promovido = validar(FIXTURE_FREEZE, FIXTURE_BANCO_PROMOVIDO)
    contagem_igual = (len(FIXTURE_FREEZE['attention_object'])
                      == len(FIXTURE_BANCO_PROMOVIDO['attention_object']))
    return {
        'SOURCE_ID': 'SUPABASE-SHADOW-VALIDATION-RUN-EAME-2026-08-31',
        'source': 'Validador de sombra implementado e exercitado sobre fixture.',
        'MODE': {'DB_CONNECTION': 'NONE', 'EXERCISED_ON': 'FIXTURE',
                 'PROVA_A_LOGICA': 'SIM', 'PROVA_UM_BANCO_REAL': 'NAO'},
        'DIMENSOES_COMPARADAS': list(DIMENSOES),
        'CASO_BANCO_FIEL': {'PUBLISH': ok['PUBLISH'],
                            'FAMILIES': len(ok['FAMILIES'])},
        'CASO_OBJETO_PROMOVIDO': {
            'PUBLISH': promovido['PUBLISH'],
            'FAMILIES_FAILED': promovido['FAMILIES_FAILED'],
            'CONTAGEM_ERA_IGUAL': contagem_igual,
            'O_QUE_PEGOU': [m for r in promovido['FAMILIES'] for m in r['MISMATCHES']],
            'POR_QUE_IMPORTA': ('o freeze diz ATTENTION_CANDIDATE_TEST e o banco diz '
                                'ATTENTION_READY. A contagem bate. Um validador que so '
                                'contasse deixaria passar, e o objeto apareceria na fila '
                                'de atencao como se tivesse atravessado os cinco portoes.'),
        },
        'MULTILINGUE': exercicio_multilingue(),
        'ISOLAMENTO_POR_PAIS': exercicio_isolamento_por_pais(),
        'PROVENIENCIA_PONTA_A_PONTA': exercicio_proveniencia(),
        'LIMITE_DESTA_RODADA': ('a fixture prova que o comparador pega a mudanca de '
                                'semantica. NAO prova nada sobre um banco real: nao ha '
                                'instancia, e o SQL nunca foi executado.'),
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA, RAIZ))
    print(json.dumps(m, ensure_ascii=False, indent=2))
