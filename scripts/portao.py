#!/usr/bin/env python3
"""
PORTÃO DE SAÍDA — os seis estados que autorizam (ou barram) a próxima coleta espanhola.

Cada portão é DERIVADO do artefato, nunca digitado. Se um deles não fechar, a resposta a
"podemos coletar mais?" é NÃO, e o motivo é o portão que barrou.

    python3 scripts/portao.py
    python3 scripts/portao.py --json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
sys.path.insert(0, HERE)
import proveniencia as pv  # noqa: E402
import voz                 # noqa: E402


def _ler(nome):
    with open(os.path.join(SAMPLES, nome), encoding='utf-8') as f:
        return json.load(f)


def avaliar():
    p = {}
    runs = pv.carregar()
    vids = _ler('ES-T8-001-videos.json')

    # ---- RUN_MANIFEST: todo RUN_ID citado por um registro publicado precisa resolver
    citados = {v['RUN_ID'] for v in vids['VIDEOS']}
    citados |= {_ler('ES-T8-001-comentarios.json')['RUN_ID'],
                _ler('ES-T8-002-posts.json')['RUN_ID']}
    orfaos = sorted(r for r in citados if r not in runs)
    completos = all(not (set(pv.CAMPOS_RUN) - set(r)) for r in runs.values())
    p['RUN_MANIFEST'] = {
        'PROVED': not orfaos and completos and len(runs) > 0,
        'MEDIDA': '%d execuções no manifesto, %d RUN_ID citados, %d órfãos' % (
            len(runs), len(citados), len(orfaos)),
        'BLOQUEIO': ('RUN_ID sem manifesto: %s' % orfaos) if orfaos else None,
    }

    # ---- PIPELINE_DEDUPE: as três contagens existem, fecham, e vêm do pipeline
    pi = vids.get('PIPELINE') or {}
    tem = all(c in pi for c in ('RAW_COUNT', 'DUPLICATE_COUNT', 'UNIQUE_CONTENT_COUNT'))
    fecha = tem and pi['RAW_COUNT'] == pi['UNIQUE_CONTENT_COUNT'] + pi['DUPLICATE_COUNT']
    bate = tem and pi['UNIQUE_CONTENT_COUNT'] == len(vids['VIDEOS'])
    invoca = 'pipeline_video' in (pi.get('FUNCAO') or '')
    # DUPLICATE_COUNT=0 nesta camada é verdade, e por isso mesmo não prova nada: o portão
    # passaria com um dedupe que não faz nada. Então o portão EXERCE o dedupe num caso
    # conhecido, em vez de confiar num zero.
    prova = [{'PLATFORM': 'X', 'EXTERNAL_ID': 'a', 'TITLE': 'mesmo'},
             {'PLATFORM': 'X', 'EXTERNAL_ID': 'a', 'TITLE': 'outro'},
             {'PLATFORM': 'X', 'EXTERNAL_ID': 'b', 'TITLE': 'mesmo'}]
    unicos_p, colaps_p = voz.dedupe(prova)
    colapsa = (colaps_p == 1 and len(unicos_p) == 2)   # id igual colapsa, título igual não
    p['PIPELINE_DEDUPE'] = {
        'PROVED': bool(tem and fecha and bate and invoca and colapsa),
        'MEDIDA': ('RAW %s = ÚNICOS %s + DUPLICATAS %s; saída publicada com %d registros; '
                   'dedupe exercido: id igual colapsa, título igual não') % (
            pi.get('RAW_COUNT'), pi.get('UNIQUE_CONTENT_COUNT'), pi.get('DUPLICATE_COUNT'),
            len(vids['VIDEOS'])),
        'BLOQUEIO': None if (tem and fecha and bate and invoca and colapsa)
                    else ('contagens ausentes ou incoerentes, saída fora do pipeline, '
                          'ou dedupe que não colapsa'),
    }

    # ---- VIDEO_TAXONOMY_APPLIED: todo vídeo com tipo dentro do contrato
    validos = set(voz.TIPOS_VIDEO) | {voz.NAO_SEI}
    fora = [v['EXTERNAL_ID'] for v in vids['VIDEOS'] if v.get('CONTENT_TYPE') not in validos]
    sem = [v['EXTERNAL_ID'] for v in vids['VIDEOS'] if 'CONTENT_TYPE' not in v]
    p['VIDEO_TAXONOMY_APPLIED'] = {
        'PROVED': not fora and not sem,
        'MEDIDA': '%d/%d classificados dentro do contrato de %d tipos' % (
            len(vids['VIDEOS']) - len(fora) - len(sem), len(vids['VIDEOS']), len(voz.TIPOS_VIDEO)),
        'BLOQUEIO': ('vídeos sem tipo: %d; fora do contrato: %d' % (len(sem), len(fora)))
                    if (fora or sem) else None,
    }

    # ---- VIDEO_ORIGINALITY: todos com estado, UNKNOWN é aceitável mas explícito
    semo = [v['EXTERNAL_ID'] for v in vids['VIDEOS']
            if v.get('ORIGINALITY') not in voz.ORIGINALIDADE]
    semev = [v['EXTERNAL_ID'] for v in vids['VIDEOS'] if not v.get('ORIGINALITY_EVIDENCE')]
    p['VIDEO_ORIGINALITY'] = {
        'PROVED': not semo and not semev,
        'MEDIDA': '%s' % (vids.get('ORIGINALITY', {}).get('DISTRIBUICAO')),
        'BLOQUEIO': ('sem estado: %d; sem evidência: %d' % (len(semo), len(semev)))
                    if (semo or semev) else None,
    }

    # ---- PAID_RAW_POLICY: quem diz PRESERVED tem o arquivo; quem não tem, confessa
    faltando, pagas = [], 0
    for rid, r in runs.items():
        if r['RAW_EVIDENCE_STATE'] == 'NOT_APPLICABLE':
            continue
        pagas += 1
        if r['RAW_EVIDENCE_STATE'] != 'PRESERVED':
            continue
        caminhos = r['RAW_EVIDENCE_PATH']
        for c in (caminhos if isinstance(caminhos, list) else [caminhos]):
            c = str(c).split(' (')[0].strip()
            if c and c != pv.NOT_PRESERVED and not os.path.exists(os.path.join(ROOT, c)):
                faltando.append((rid, c))
    leu_bruto = 'raw-paid' in ((vids.get('PIPELINE') or {}).get('ENTRADA') or '')
    p['PAID_RAW_POLICY'] = {
        'PROVED': not faltando and leu_bruto,
        'MEDIDA': '%d rotas pagas; %d com bruto declarado ausente; pipeline lê o bruto: %s' % (
            pagas, len(faltando), leu_bruto),
        'BLOQUEIO': ('bruto declarado e inexistente: %s' % faltando) if faltando
                    else (None if leu_bruto else 'o pipeline não lê o bruto preservado'),
    }

    # ---- COLLECTION_TIMESTAMPS: existe execução com hora medida, e a antiga não finge
    # O invariante não é "existem N execuções com hora": é "toda execução que passou pela
    # porta nova tem hora MEDIDA PELA PLATAFORMA". As antigas legitimamente não têm, e
    # nunca terão — o que elas não podem é fingir que têm.
    PORTA_NOVA = 'POST /acts/{actor}/runs?waitForFinish'
    pela_porta = [r for r in runs.values() if PORTA_NOVA in str(r['CAPTURE_METHOD'])]
    sem_hora = [r['RUN_ID'] for r in pela_porta
                if pv.NOT_PRESERVED in (r['STARTED_AT'], r['FINISHED_AT'])]
    fingindo = [r['RUN_ID'] for r in runs.values()
                if r['STARTED_AT'] != pv.NOT_PRESERVED
                and r['OUTPUT_WRITTEN_AT'] == r['STARTED_AT']]
    ordem_ok = False
    if len(pela_porta) >= 2:
        d = sorted(pela_porta, key=lambda r: r['STARTED_AT'])
        ordem_ok = pv.ordem(d[0], d[-1])[0] != 'NAO_DIZIVEL'
    p['COLLECTION_TIMESTAMPS'] = {
        'PROVED': bool(pela_porta) and not sem_hora and not fingindo and ordem_ok,
        'MEDIDA': ('%d execuções pela porta nova, %d sem hora medida; ordem entre elas é '
                   'afirmável: %s. As %d antigas seguem sem hora e sem fingir que têm.') % (
            len(pela_porta), len(sem_hora), ordem_ok, len(runs) - len(pela_porta)),
        'BLOQUEIO': ('hora de escrita promovida a hora de execução: %s' % fingindo) if fingindo
                    else (('execução pela porta nova sem hora: %s' % sem_hora) if sem_hora
                          else (None if ordem_ok else
                                'nenhuma ordem afirmável — o portão estaria só afirmado')),
    }
    return p


def veredito():
    p = avaliar()
    tudo = all(v['PROVED'] for v in p.values())
    bloqueios = [k for k, v in p.items() if not v['PROVED']]
    return {'PORTOES': p,
            'READY_FOR_NEXT_ES_COLLECTION': 'YES' if tudo else 'NO',
            'BLOQUEADO_POR': bloqueios}


if __name__ == '__main__':
    v = veredito()
    if '--json' in sys.argv:
        print(json.dumps(v, ensure_ascii=False, indent=1))
    else:
        for k, d in v['PORTOES'].items():
            print('%-26s %-6s %s' % (k, 'PROVED' if d['PROVED'] else 'BLOCKED', d['MEDIDA']))
            if d['BLOQUEIO']:
                print('%-26s        -> %s' % ('', d['BLOQUEIO']))
        print()
        print('READY_FOR_NEXT_ES_COLLECTION =', v['READY_FOR_NEXT_ES_COLLECTION'])
        if v['BLOQUEADO_POR']:
            print('bloqueado por:', ', '.join(v['BLOQUEADO_POR']))
