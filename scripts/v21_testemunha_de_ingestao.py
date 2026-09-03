#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TESTEMUNHA DE INGESTÃO · a coleta nova passa pela V11.2 sozinha?

    python3 scripts/v21_testemunha_de_ingestao.py

A pergunta não se responde lendo código. Responde-se pondo um registro novo na
PORTA REAL da coleta, rodando a CADEIA REAL e olhando o que saiu do outro lado.

    UM REGISTRO QUE ENTRA POR UMA PORTA ESPECIAL PROVA A PORTA ESPECIAL.

A PORTA REAL
------------
`build/ITALY-REALITY-HANDOFF-V2/CANONICAL-INTELLIGENCE.json`, família
`CURRENT_FIELD_SIGNALS` — versionada, e lida por `v21_ingest_b.py` no passo 1 de
`v21_cadeia.sh`. É por ela que entrou cada um dos 49 sinais de last-mile que já
estão no acervo. Este arquivo NÃO inventa porta nova: usa essa.

O QUE A FIXTURE FOI DESENHADA PARA PEGAR
-----------------------------------------
Um único boletim fictício, no PIEMONTE, com duas orações:

1. «Vite/botrite: intervir em pre-colheita com Fenhexamid.»
   → par observado, direção POSITIVE_PRESSURE, um alvo só.
2. «Suspensao de oidio, fim da defesa de tignoletta e de peronospora ...»
   → uma direção e TRÊS alvos na mesma oração.

O Piemonte tem janela no acervo — `IT-WIN-003`, videira × *Scaphoideus*. Cultura
e região batem; o ALVO não. No comportamento antigo os quatro casos herdariam
`IT-WIN-001/002/003` e os três alvos da oração corrida receberiam
`WINDOW_CONCLUDED`. Se isso reaparecer, a coleta nova caiu no comportamento
antigo — e este arquivo falha.

    A FIXTURE NÃO PERGUNTA SE O MOTOR ESTÁ CERTO.
    PERGUNTA SE A COLETA NOVA CHEGA ATÉ ELE.

⚠️ A fixture é INJETADA e DEPOIS REMOVIDA. O arquivo de porta é restaurado com
`git checkout --` e a cadeia roda outra vez, para que o pacote volte ao
`BUILD_ID` de antes. Se o BUILD_ID não voltar, este arquivo grita: significa que
a passagem deixou residuo, e residuo silencioso e a doenca que a cadeia inteira
existe para evitar.
"""
import json
import os
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTA = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2',
                     'CANONICAL-INTELLIGENCE.json')
PORTA_REL = 'build/ITALY-REALITY-HANDOFF-V2/CANONICAL-INTELLIGENCE.json'
PACOTE = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1',
                      'DESIGN-INGEST', 'OPPORTUNITIES.json')
CADEIA = os.path.join(ROOT, 'scripts', 'v21_cadeia.sh')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V112-TESTEMUNHA-DE-INGESTAO.json')

FIXTURE = {
    'FAMILIA': 'CURRENT_FIELD_SIGNALS',
    'CANONICAL_RECORD_ID': 'IT-FIXTURE-INGESTAO-V112',
    'QA_STATUS': 'QA_PASS',
    'tipo': 'BOLETIM FITOSSANITARIO OFICIAL · VITE · FIXTURE DE INGESTAO V11.2',
    'crop': 'VITE',
    'region': 'Piemonte',
    'geographic_scope': 'REGIONALE',
    'source_name': 'FIXTURE DE TESTE — NAO E FONTE REAL',
    'source_url': 'https://fixture.invalid/v112/testemunha-de-ingestao',
    'publication_date': '2026-09-01',
    'observation_class': 'CURRENT',
    'o_que': 'Vite/botrite: intervir em pre-colheita com Fenhexamid. '
             'Suspensao de oidio, fim da defesa de tignoletta e de peronospora '
             'nas mesmas vinhas.',
    'citacao_literal': 'FIXTURE — nenhuma fonte disse isto. Registro de teste, '
                       'injetado e removido pela testemunha de ingestao.',
}

# ⚠️ A fixture NAO declara `RESSALVA_PERMANENTE`, e isso foi MEDIDO, nao
# escolhido por estilo. `promover_research` (passo 5d) e tudo-ou-nada: se o
# registro ja tem QUALQUER campo de tela — e `PERMANENT_CAVEAT` e um deles —
# nenhuma prosa sobe de `RESEARCH`. Com a ressalva dentro, o boletim entrava no
# acervo com `WHAT_IT_IS = None` e o extrator de pares nao tinha texto para ler:
# a coleta chegava ao motor MUDA. Esta e a primeira coisa que a testemunha
# achou, e esta contada em `V112-AUTOMACAO-DA-INGESTAO.md`.
#
#     UM REGISTRO QUE ENTRA SEM TEXTO NAO E RECUSADO. ELE E IGNORADO —
#     E IGNORADO EM SILENCIO E PIOR QUE RECUSADO EM VOZ ALTA.

# O que a coleta nova NÃO pode voltar a produzir.
JANELAS_DO_ACERVO = ('IT-WIN-001', 'IT-WIN-002', 'IT-WIN-003', 'IT-WIN-004',
                     'IT-WIN-005', 'IT-WIN-006', 'IT-WIN-007')


def _git(*args):
    return subprocess.run(['git', '-C', ROOT] + list(args),
                          capture_output=True, text=True)


def _cadeia():
    r = subprocess.run(['bash', CADEIA], cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout


def _pacote():
    d = json.load(open(PACOTE, encoding='utf-8'))
    return d['BUILD_ID'], {r['ID']: r for r in d['RECORDS']}


def _casos_da_fixture(recs):
    return {r['TARGET']: r for r in recs.values()
            if r.get('GEOGRAPHY') == 'REGION_PIEMONTE'
            and r.get('CROP') == 'CROP_GRAPEVINE' and r.get('TARGET')}


def main():
    sujo = _git('status', '--porcelain', '--', PORTA_REL).stdout.strip()
    if sujo:
        print('A porta tem alteracao nao commitada. Nao injeto sobre trabalho '
              'de outra pessoa:\n  %s' % sujo, file=sys.stderr)
        return 2

    print('=' * 78)
    print('PORTA REAL : %s' % PORTA_REL)
    print('CADEIA     : scripts/v21_cadeia.sh (passo 1 ingest · passo 5e motor)')
    print('=' * 78)

    # ⚠️ O baseline sai de uma CADEIA RODADA AGORA, com a porta limpa. Ler o
    # pacote que estava no disco compara contra o que a rodada anterior deixou
    # — e foi exatamente assim que a primeira execucao desta testemunha se
    # acusou de «residuo» que era dela mesma.
    #
    #     BASELINE QUE NAO FOI RECONSTRUIDO E LEMBRANCA DO ULTIMO ERRO.
    print('\nreconstruindo o baseline com a porta limpa...')
    codigo, _log = _cadeia()
    if codigo != 0:
        print('a cadeia falhou ANTES da fixture (EXIT=%d)' % codigo,
              file=sys.stderr)
        return 1
    build_antes, antes = _pacote()
    print('BASELINE   BUILD_ID %s · %d casos' % (build_antes, len(antes)))

    # ── injeta na porta e roda a cadeia REAL ────────────────────────────────
    d = json.load(open(PORTA, encoding='utf-8'))
    d['RECORDS'].append(dict(FIXTURE))
    json.dump(d, open(PORTA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('injetado 1 registro na porta · rodando a cadeia real...')
    try:
        codigo, _log = _cadeia()
        if codigo != 0:
            print('a cadeia falhou com a fixture dentro (EXIT=%d)' % codigo,
                  file=sys.stderr)
            return 1
        build_depois, depois = _pacote()
    finally:
        _git('checkout', '--', PORTA_REL)

    novos = sorted(set(depois) - set(antes))
    casos = _casos_da_fixture(depois)
    print('\nDEPOIS DA INGESTAO   BUILD_ID %s · %d casos · %d novos'
          % (build_depois, len(depois), len(novos)))

    falhas = []

    # 1 · o derivado apareceu sem ninguem chamar o motor a mao
    if not casos:
        falhas.append('a ingestao nao produziu caso nenhum no Piemonte: o '
                      'derivado nao recalculou')
    print('\n1 · DERIVADO RECALCULADO SOZINHO')
    for alvo, r in sorted(casos.items()):
        print('   %s  %-22s %-18s %s' % (r['ID'], alvo.replace('ISSUE_', ''),
                                         r['NEED_DIRECTION'],
                                         r['COMMERCIAL_PRIORITY']))

    # 2 · a chave de janela da V11.2 valeu para o registro novo
    print('\n2 · VINCULO DE JANELA (cultura + alvo + regiao)')
    for alvo, r in sorted(casos.items()):
        herdadas = [i for i in (r.get('EVIDENCE_IDS') or [])
                    if i in JANELAS_DO_ACERVO]
        print('   %-24s janelas herdadas: %s' % (alvo.replace('ISSUE_', ''),
                                                 herdadas or 'nenhuma'))
        if herdadas:
            falhas.append('%s herdou %s — a coleta nova caiu no indice por '
                          'cultura' % (r['ID'], ', '.join(herdadas)))

    # 3 · a direcao nao se repartiu entre os alvos da oracao corrida
    print('\n3 · DIRECAO NAO REPARTIDA')
    corrida = ('ISSUE_POWDERY_MILDEW', 'ISSUE_GRAPE_MOTH', 'ISSUE_DOWNY_MILDEW')
    for alvo in corrida:
        r = casos.get(alvo)
        if not r:
            falhas.append('%s nao virou caso: a oracao corrida destruiu o par'
                          % alvo)
            continue
        ok = r['NEED_DIRECTION'] == 'UNKNOWN'
        print('   %-24s %-10s ambiguidade=%s' % (alvo.replace('ISSUE_', ''),
                                                 r['NEED_DIRECTION'],
                                                 r.get('NEED_AMBIGUITY_CODES')))
        if not ok:
            falhas.append('%s recebeu %s de uma oracao com tres alvos'
                          % (alvo, r['NEED_DIRECTION']))
    b = casos.get('ISSUE_BOTRYTIS')
    if b:
        print('   %-24s %-10s (oracao de um alvo so, continua decidindo)'
              % ('BOTRYTIS', b['NEED_DIRECTION']))
        if b['NEED_DIRECTION'] != 'POSITIVE_PRESSURE':
            falhas.append('a oracao de um alvo so deixou de decidir')

    # 4 · a passagem nao deixou residuo
    print('\n4 · RESTAURACAO')
    codigo, _log = _cadeia()
    build_final, final = _pacote()
    print('   BUILD_ID final %s · %d casos' % (build_final, len(final)))
    if codigo != 0 or build_final != build_antes or len(final) != len(antes):
        falhas.append('a passagem deixou residuo: BUILD_ID %s != %s'
                      % (build_final, build_antes))

    print('\n' + '=' * 78)
    if falhas:
        print('FALHAS: %d' % len(falhas))
        for f in falhas:
            print('  · %s' % f)
    else:
        print('SEM FALHAS · a coleta nova atravessou a V11.2 sozinha')
    print('=' * 78)

    fora = {
        'COLLECTION': 'V112-TESTEMUNHA-DE-INGESTAO',
        'SOURCE': 'injecao de fixture em %s + execucao de scripts/v21_cadeia.sh'
                  % PORTA_REL,
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'a fixture entra pela porta versionada da coleta e sai pelo '
               'pacote reconstruido. Nenhum passo foi chamado a mao.',
        'DOOR': PORTA_REL,
        'ENGINE_CALLED_BY': 'scripts/v21_cadeia.sh · passo 5e',
        'BUILD_ID_BASELINE': build_antes,
        'BUILD_ID_COM_FIXTURE': build_depois,
        'BUILD_ID_RESTAURADO': build_final,
        'CASOS_BASELINE': len(antes), 'CASOS_COM_FIXTURE': len(depois),
        'CASOS_NOVOS': novos,
        'CASOS_DA_FIXTURE': {
            a: {'ID': r['ID'], 'NEED_DIRECTION': r['NEED_DIRECTION'],
                'NEED_AMBIGUITY_CODES': r.get('NEED_AMBIGUITY_CODES'),
                'WINDOW_FIELD': r.get('WINDOW_FIELD'),
                'JANELAS_HERDADAS': [i for i in (r.get('EVIDENCE_IDS') or [])
                                     if i in JANELAS_DO_ACERVO],
                'BLOCKING_GATES': r.get('BLOCKING_GATES'),
                'COMMERCIAL_PRIORITY': r['COMMERCIAL_PRIORITY']}
            for a, r in sorted(casos.items())},
        'FALHAS': falhas,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(fora, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('gravado em %s' % os.path.relpath(SAIDA, ROOT))
    return 1 if falhas else 0


if __name__ == '__main__':
    sys.exit(main())
