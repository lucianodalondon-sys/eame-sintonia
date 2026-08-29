#!/usr/bin/env python3
"""
PROVENIÊNCIA — o RUN_ID deixa de ser um rótulo e passa a resolver.

O defeito que este arquivo fecha: até 2026-08-29 o `RUN_ID` agrupava registros entre si e
não resolvia para nada fora do repositório. Dado um vídeo, não havia como responder
"que execução produziu isto, com que ator, que entrada e que custo".

A cadeia que passa a existir:

    CONTENT → RUN_ID → RUN_MANIFEST → INPUT / ACTOR / DATASET / RAW

Três decisões carregadas aqui:

1. **CAMPO DESCONHECIDO É `NOT_PRESERVED`, NUNCA AUSENTE.**
   Execução antiga que não capturou `ACTOR_VERSION` declara `NOT_PRESERVED`. Isso é
   diferente de `NAO_SEI` (a fonte não informa) e muito diferente da chave sumir.

2. **NUNCA GRAVAR TOKEN.** `INPUT` guarda a consulta e os parâmetros; credencial jamais.
   Há teste que varre o manifesto atrás de padrão de token.

3. **TEMPO É MEDIDO, NÃO INFERIDO.** `STARTED_AT`/`FINISHED_AT` vêm da execução. Sem eles,
   nenhuma afirmação de ordem entre camadas é permitida — ver `pode_afirmar_ordem()`.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFESTO = os.path.join(ROOT, 'data', 'samples', 'RUN-MANIFEST.json')

NAO_SEI = 'NÃO SEI'
NOT_PRESERVED = 'NOT_PRESERVED'

# Campos obrigatórios de todo manifesto de execução.
CAMPOS_RUN = [
    'RUN_ID', 'PLATFORM', 'ACTOR', 'ACTOR_VERSION', 'STARTED_AT', 'FINISHED_AT',
    'INPUT', 'COUNTRY', 'MISSION', 'QUERY', 'DATASET_ID',
    'ITEM_COUNT_RAW', 'ITEM_COUNT_NORMALIZED', 'COST_USD', 'SOURCE_VERSION',
    'STATUS', 'ERROR', 'CAPTURE_METHOD', 'EVIDENCE_PATH', 'RAW_EVIDENCE_PATH',
    'RAW_EVIDENCE_STATE',
    # Hora em que o coletor GRAVOU a saída. É medida de verdade, mas NÃO é a hora da
    # execução na plataforma — por isso vive em campo próprio e nunca é usada como
    # STARTED_AT/FINISHED_AT. Passar hora de escrita por hora de execução seria
    # exatamente o erro que a auditoria derrubou.
    'OUTPUT_WRITTEN_AT',
]

STATUS_RUN = ['SUCCESS', 'PARTIAL', 'FAILED', 'NOT_PRESERVED']
# Estado da evidência bruta. `NOT_PRESERVED` é uma confissão, não um sinônimo de ausência
# de dado: quer dizer que a resposta crua existiu e não foi guardada.
ESTADOS_RAW = ['PRESERVED', 'NOT_PRESERVED', 'NOT_APPLICABLE']

TOKEN = re.compile(r'apify_api_[A-Za-z0-9]{10,}|Bearer\s+[A-Za-z0-9._\-]{20,}')


def run_vazio():
    """Todo campo presente, todo valor em NOT_PRESERVED."""
    return {c: NOT_PRESERVED for c in CAMPOS_RUN}


def novo_run(run_id, **campos):
    """Monta um manifesto completo. Campo não informado fica NOT_PRESERVED, nunca some."""
    r = run_vazio()
    r['RUN_ID'] = run_id
    for k, v in campos.items():
        if k not in CAMPOS_RUN:
            raise KeyError('campo fora do contrato de RUN: %s' % k)
        r[k] = v
    checar_token(r)
    return r


def checar_token(run):
    """Um manifesto nunca pode carregar credencial."""
    achado = TOKEN.search(json.dumps(run, ensure_ascii=False))
    if achado:
        raise ValueError('credencial no manifesto de execução — nunca gravar token')
    return True


def carregar():
    if not os.path.exists(MANIFESTO):
        return {}
    with open(MANIFESTO, encoding='utf-8') as f:
        d = json.load(f)
    return {r['RUN_ID']: r for r in d.get('RUNS', [])}


def resolver(run_id):
    """RUN_ID -> manifesto. É isto que faltava: o rótulo agora resolve."""
    return carregar().get(run_id)


def gravar(runs, *, captured_at):
    """Persiste o manifesto. `runs` é lista de dicionários já no contrato."""
    for r in runs:
        faltando = set(CAMPOS_RUN) - set(r)
        if faltando:
            raise KeyError('manifesto incompleto, faltam: %s' % sorted(faltando))
        checar_token(r)
        if r['STATUS'] not in STATUS_RUN:
            raise ValueError('STATUS fora do contrato: %s' % r['STATUS'])
        if r['RAW_EVIDENCE_STATE'] not in ESTADOS_RAW:
            raise ValueError('RAW_EVIDENCE_STATE fora do contrato: %s' % r['RAW_EVIDENCE_STATE'])
    corpo = {
        'SOURCE_ID': 'RUN-MANIFEST',
        'source': 'manifesto de execuções de coleta do SINTONIA EAME',
        'SOURCE_LOCATION': 'interno — metadado de coleta',
        'FACT_LOCATION': 'n/a — descreve execução, não fato do mundo',
        'ORIGINAL_LANGUAGE': 'pt',
        'captured_at': captured_at,
        'PARA_QUE_SERVE': (
            'dado um registro qualquer, o RUN_ID leva a esta tabela e a tabela diz que ator '
            'rodou, com que entrada, quando, quanto custou e onde está a evidência bruta. '
            'Sem isto o RUN_ID só agrupa registros entre si.'),
        'CAMPO_DESCONHECIDO': (
            'NOT_PRESERVED significa que o campo existiu na execução e não foi capturado. '
            'É confissão, não ausência de dado — e é diferente de NÃO SEI, que é a fonte '
            'não informar.'),
        'NUNCA_GRAVAR_TOKEN': 'INPUT guarda consulta e parâmetros. Credencial, jamais.',
        'RUNS': runs,
    }
    with open(MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)
    return corpo


# ---------------------------------------------------------------- ordem entre camadas
def pode_afirmar_ordem(run_a, run_b):
    """`X BEFORE Y` só é dizível quando as duas execuções têm hora medida.

    A auditoria de 2026-08-29 derrubou a afirmação "o YouTube veio antes do LinkedIn":
    as duas rotas saíram do mesmo orçamento sem carimbo que as separasse, e o horário de
    commit do git NÃO mede hora de coleta — mede hora de escrita.
    """
    for r in (run_a, run_b):
        if not r:
            return False, 'execução sem manifesto'
        for c in ('STARTED_AT', 'FINISHED_AT'):
            if r.get(c) in (NOT_PRESERVED, NAO_SEI, None, ''):
                return False, '%s sem %s medido' % (r.get('RUN_ID'), c)
    return True, ''


def ordem(run_a, run_b):
    """Devolve BEFORE / AFTER / OVERLAPS, ou NAO_DIZIVEL com o motivo."""
    ok, motivo = pode_afirmar_ordem(run_a, run_b)
    if not ok:
        return 'NAO_DIZIVEL', motivo
    if run_a['FINISHED_AT'] <= run_b['STARTED_AT']:
        return 'BEFORE', ''
    if run_b['FINISHED_AT'] <= run_a['STARTED_AT']:
        return 'AFTER', ''
    return 'OVERLAPS', ''


if __name__ == '__main__':
    import sys
    runs = carregar()
    print('execuções no manifesto:', len(runs))
    for rid, r in sorted(runs.items()):
        print('  %-34s %-9s %-8s raw=%s' % (rid, r['PLATFORM'], r['STATUS'],
                                            r['RAW_EVIDENCE_STATE']))
    if '--campos' in sys.argv:
        for c in CAMPOS_RUN:
            print(' ', c)
