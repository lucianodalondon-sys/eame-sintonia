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



# Artefatos publicados que carregam RUN_ID. Derivado por varredura, não escolhido a dedo:
# ver `_run_ids_publicados`.
_ARTEFATOS_COM_RUN_ID = []


def _run_ids_publicados():
    """Todo RUN_ID citado por qualquer artefato de data/samples, em qualquer profundidade.

    O portão antigo lia três arquivos. A varredura achou seis. Afirmar "0 órfãos" sobre
    uma amostra escolhida a dedo é afirmar sobre o que não foi lido.
    """
    import glob
    ids, arquivos = set(), []
    for caminho in sorted(glob.glob(os.path.join(SAMPLES, '**', '*.json'), recursive=True)):
        if os.path.basename(caminho) == 'RUN-MANIFEST.json':
            continue          # é o índice, não um artefato que cita
        try:
            with open(caminho, encoding='utf-8') as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        achados = set()

        def anda(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == 'RUN_ID' and isinstance(v, str):
                        achados.add(v)
                    else:
                        anda(v)
            elif isinstance(o, list):
                for x in o:
                    anda(x)
        anda(d)
        if achados:
            arquivos.append(os.path.relpath(caminho, SAMPLES))
            ids |= achados
    _ARTEFATOS_COM_RUN_ID[:] = arquivos
    return ids


def _distribuicao(registros, campo):
    """Contagem DERIVADA dos registros. Nunca o bloco declarado no arquivo."""
    d = {}
    for r in registros:
        d[r.get(campo)] = d.get(r.get(campo), 0) + 1
    return dict(sorted(d.items(), key=lambda kv: (-kv[1], str(kv[0]))))


def _evidencia_valida(v):
    """`NÃO SEI` não é evidência. É a declaração de que não há.

    Medido na MISSÃO 10C: o portão aceitava `ORIGINALITY_EVIDENCE = 'NÃO SEI'` como se
    fosse prova, porque só testava se o campo era vazio.
    """
    if not v:
        return False
    if isinstance(v, str) and v.strip() in (voz.NAO_SEI, 'NAO SEI', 'NOT_PRESERVED'):
        return False
    return True


def _bruto_corrompido():
    """Bruto de PRODUÇÃO cujo SHA-256 diverge do que o relógio de dados registrou."""
    import hashlib
    try:
        with open(os.path.join(SAMPLES, 'DATA-CLOCK-manifest.json'), encoding='utf-8') as f:
            clock = json.load(f)
    except (OSError, ValueError):
        return ['DATA-CLOCK-manifest.json ilegível']
    declarado = {f['FILE']: f.get('SHA256') for f in clock.get('files', []) if f.get('SHA256')}
    ruins = []
    for item in pv.inventario_raw_pago():
        if item['CLASS'] != pv.PRODUCTION_RAW:
            continue
        esperado = declarado.get(item['FILE'])
        caminho = os.path.join(ROOT, item['FILE'])
        if not esperado:
            ruins.append('%s sem SHA-256 no relógio' % item['FILE'])
            continue
        with open(caminho, 'rb') as f:
            real = hashlib.sha256(f.read()).hexdigest()
        if real != esperado:
            ruins.append(item['FILE'])
    return ruins

def avaliar():
    p = {}
    runs = pv.carregar()
    vids = _ler('ES-T8-001-videos.json')

    # ---- RUN_MANIFEST: todo RUN_ID citado por QUALQUER artefato publicado precisa resolver.
    # Antes o portão olhava três arquivos escolhidos a dedo. A MISSÃO 10C mediu: SEIS
    # artefatos publicados carregam RUN_ID. Verificar três e afirmar "0 órfãos" é afirmar
    # sobre uma população que não foi lida.
    citados = _run_ids_publicados()
    orfaos = sorted(r for r in citados if r not in runs)
    completos = all(not (set(pv.CAMPOS_RUN) - set(r)) for r in runs.values())
    # RUN_ID repetido no manifesto faz uma execução sobrescrever a outra em silêncio.
    duplicados = pv.runs_duplicados()
    # E a direção inversa: arquivo bruto de produção que nenhuma execução reivindica.
    orfaos_raw = pv.brutos_orfaos()
    p['RUN_MANIFEST'] = {
        'PROVED': bool(not orfaos and completos and len(runs) > 0
                       and not duplicados and not orfaos_raw),
        'MEDIDA': ('%d execuções no manifesto, %d RUN_ID citados em %d artefatos, %d órfãos; '
                   '%d RUN_ID duplicados; %d bruto de produção órfão') % (
            len(runs), len(citados), len(_ARTEFATOS_COM_RUN_ID), len(orfaos),
            len(duplicados), len(orfaos_raw)),
        'BLOQUEIO': ('RUN_ID sem manifesto: %s' % orfaos) if orfaos
                    else (('RUN_ID duplicado no manifesto: %s' % duplicados) if duplicados
                          else (('bruto de produção sem execução: %s' % orfaos_raw)
                                if orfaos_raw else None)),
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
    # LIMITE DECLARADO: este portão garante FORMA, não VERDADE. Ele prova que todo vídeo
    # tem um tipo do contrato e que o primário é coerente com CONTENT_TYPE_ALL. Ele NÃO
    # prova que a classificação está certa — o classificador é lexical e a polissemia
    # produz falso positivo ("curso natural del agua" casa `curso`). Por isso todo
    # registro carrega CONTENT_TYPE_EVIDENCE: a checagem de verdade é humana e auditável.
    validos = set(voz.TIPOS_VIDEO) | {voz.NAO_SEI}
    fora = [v['EXTERNAL_ID'] for v in vids['VIDEOS'] if v.get('CONTENT_TYPE') not in validos]
    sem = [v['EXTERNAL_ID'] for v in vids['VIDEOS'] if 'CONTENT_TYPE' not in v]
    # primário tem de estar em CONTENT_TYPE_ALL quando ALL existe: senão a precedência
    # declarada é decorativa e ninguém percebe.
    incoerentes = [v['EXTERNAL_ID'] for v in vids['VIDEOS']
                   if v.get('CONTENT_TYPE_ALL')
                   and v.get('CONTENT_TYPE') not in v['CONTENT_TYPE_ALL']]
    sem_ev = [v['EXTERNAL_ID'] for v in vids['VIDEOS']
              if not _evidencia_valida(v.get('CONTENT_TYPE_EVIDENCE'))]
    dist = _distribuicao(vids['VIDEOS'], 'CONTENT_TYPE')
    ok3 = not fora and not sem and not incoerentes and not sem_ev
    p['VIDEO_TAXONOMY_APPLIED'] = {
        'PROVED': bool(ok3),
        'MEDIDA': '%d/%d classificados dentro do contrato de %d tipos; distribuição derivada %s' % (
            len(vids['VIDEOS']) - len(fora) - len(sem), len(vids['VIDEOS']),
            len(voz.TIPOS_VIDEO), dist),
        'BLOQUEIO': None if ok3 else (
            'sem tipo: %d; fora do contrato: %d; primário fora de CONTENT_TYPE_ALL: %d; '
            'sem evidência de tipo: %d' % (len(sem), len(fora), len(incoerentes), len(sem_ev))),
    }

    # ---- VIDEO_ORIGINALITY: todos com estado, UNKNOWN é aceitável mas explícito
    semo = [v['EXTERNAL_ID'] for v in vids['VIDEOS']
            if v.get('ORIGINALITY') not in voz.ORIGINALIDADE]
    semev = [v['EXTERNAL_ID'] for v in vids['VIDEOS']
             if not _evidencia_valida(v.get('ORIGINALITY_EVIDENCE'))]
    # `ORIGINAL` não tem caminho de código: nenhuma rota prova autoria. Se ele aparece num
    # artefato publicado, foi ESCRITO À MÃO — e "está no canal da própria empresa" é
    # exatamente a inferência que a lei proíbe. O portão barra, em vez de abençoar.
    afirmam_original = [v['EXTERNAL_ID'] for v in vids['VIDEOS']
                        if v.get('ORIGINALITY') == 'ORIGINAL']
    # A distribuição é DERIVADA dos registros. Antes vinha do bloco declarado no próprio
    # arquivo: os 252 podiam virar ORIGINAL e o portão seguia imprimindo {UNKNOWN: 241}.
    dist4 = _distribuicao(vids['VIDEOS'], 'ORIGINALITY')
    declarada = (vids.get('ORIGINALITY') or {}).get('DISTRIBUICAO')
    bate_declarada = declarada is None or dict(declarada) == dist4
    ok4 = not semo and not semev and not afirmam_original and bate_declarada
    p['VIDEO_ORIGINALITY'] = {
        'PROVED': bool(ok4),
        'MEDIDA': '%s (derivada dos registros)' % dist4,
        'BLOQUEIO': None if ok4 else (
            'sem estado: %d; sem evidência: %d; afirmam ORIGINAL sem prova de autoria: %d; '
            'distribuição declarada %s != derivada %s' % (
                len(semo), len(semev), len(afirmam_original), declarada, dist4)),
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
    # "o pipeline lê o bruto" era `'raw-paid' in ENTRADA`: uma verificação de MENÇÃO.
    # Bastava a string. Agora a entrada declarada tem de ser um arquivo que EXISTE dentro
    # de raw-paid — menção não é leitura.
    entrada = (vids.get('PIPELINE') or {}).get('ENTRADA') or ''
    leu_bruto = bool(entrada) and entrada.startswith(pv.RAW_PAID_REL + '/') \
        and os.path.exists(os.path.join(ROOT, entrada))
    # INTEGRIDADE: o bruto de rota paga é a ÚNICA cópia da evidência — a chave morreu e a
    # rota não se repete. O DATA CLOCK guarda o SHA-256 de cada um e nada o conferia: um
    # bruto podia ser trocado ou corrompido e o portão seguia dizendo PROVED porque o
    # ARQUIVO existia. Existência não é integridade.
    corrompidos = _bruto_corrompido()
    ok5 = not faltando and leu_bruto and not corrompidos
    p['PAID_RAW_POLICY'] = {
        'PROVED': bool(ok5),
        'MEDIDA': ('%d rotas pagas; %d com bruto declarado ausente; %d com SHA-256 divergente; '
                   'pipeline lê o bruto de verdade: %s') % (
            pagas, len(faltando), len(corrompidos), leu_bruto),
        'BLOQUEIO': ('bruto declarado e inexistente: %s' % faltando) if faltando
                    else (('bruto com SHA-256 diferente do relógio de dados: %s' % corrompidos)
                          if corrompidos
                          else (None if leu_bruto else
                                'PIPELINE.ENTRADA não aponta para um bruto existente')),
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



def verificacao_adversarial():
    """O estado da verificacao adversarial, DERIVADO — nunca digitado.

    A MISSAO 10C refutou seis dos sete portoes, corrigiu e reverificou. O veredito ficou
    so no relatorio, e veredito fora do Git nao existe para a proxima conta.

    A verificacao vale para o SHA em que rodou. Se qualquer arquivo que IMPLEMENTA os
    portoes mudou depois dele, o estado cai para VERIFICATION_STALE: um portao reverificado
    e depois reescrito nao esta mais verificado. Nao ha estado "com ressalva".
    """
    import subprocess
    caminho = os.path.join(SAMPLES, 'VERIFICACAO-ADVERSARIAL-PORTOES.json')
    if not os.path.exists(caminho):
        return {'ESTADO': 'NOT_VERIFIED',
                'MOTIVO': 'nenhuma verificacao adversarial registrada'}
    with open(caminho, encoding='utf-8') as f:
        v = json.load(f)
    sha = v.get('AUDIT_TARGET_SHA')
    arquivos = v.get('ARQUIVOS_QUE_IMPLEMENTAM_OS_PORTOES', [])
    refutados = [k for k, x in v.get('RESULTADO_POR_PORTAO', {}).items()
                 if x.get('RESULT') != 'SURVIVED_ADVERSARIAL_CHECK']
    if refutados:
        return {'ESTADO': 'REFUTED', 'AUDIT_TARGET_SHA': sha,
                'MOTIVO': 'portoes refutados: %s' % refutados}
    r = subprocess.run(['git', 'diff', '--name-only', sha, '--'] + arquivos,
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return {'ESTADO': 'UNKNOWN', 'AUDIT_TARGET_SHA': sha,
                'MOTIVO': 'nao foi possivel comparar com o SHA verificado: %s'
                          % r.stderr.strip()[:120]}
    mudaram = [x for x in r.stdout.split('\n') if x.strip()]
    if mudaram:
        return {'ESTADO': 'VERIFICATION_STALE', 'AUDIT_TARGET_SHA': sha,
                'MOTIVO': 'implementacao dos portoes mudou desde a verificacao: %s' % mudaram}
    return {'ESTADO': 'ADVERSARIALLY_VERIFIED', 'AUDIT_TARGET_SHA': sha,
            'ATAQUES': v.get('ATAQUES_TOTAIS'),
            'LIMITE_ABERTO': (v.get('RESULTADO_POR_PORTAO', {})
                              .get('P3_VIDEO_TAXONOMY', {})
                              .get('LIMITE_DECLARADO_E_ABERTO'))}

def veredito():
    p = avaliar()
    tudo = all(v['PROVED'] for v in p.values())
    bloqueios = [k for k, v in p.items() if not v['PROVED']]
    adv = verificacao_adversarial()
    # `YES` e auto-avaliacao: o portao dizendo que ele mesmo passa. `ADVERSARIALLY_VERIFIED`
    # exige, ALEM disso, que alguem tenha tentado REFUTAR cada portao e falhado — e que a
    # implementacao nao tenha mudado desde entao.
    if not tudo:
        estado = 'NO'
    elif adv['ESTADO'] == 'ADVERSARIALLY_VERIFIED':
        estado = 'ADVERSARIALLY_VERIFIED'
    else:
        estado = 'YES'
    return {'PORTOES': p,
            'READY_FOR_NEXT_ES_COLLECTION': estado,
            'VERIFICACAO_ADVERSARIAL': adv,
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
        a = v['VERIFICACAO_ADVERSARIAL']
        print('VERIFICACAO_ADVERSARIAL      %s  (%s)' % (
            a['ESTADO'], a.get('AUDIT_TARGET_SHA', '—')[:12] or '—'))
        if a.get('MOTIVO'):
            print('                             -> %s' % a['MOTIVO'])
        print()
        print('READY_FOR_NEXT_ES_COLLECTION =', v['READY_FOR_NEXT_ES_COLLECTION'])
        if v['BLOQUEADO_POR']:
            print('bloqueado por:', ', '.join(v['BLOQUEADO_POR']))
