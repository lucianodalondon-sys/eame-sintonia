#!/usr/bin/env python3
"""
CICLO 9 e CICLO 10 — CHECKPOINT INCREMENTAL E RECONCILIACAO.

    py scripts/it_checkpoint.py            # abre ou atualiza o checkpoint
    py scripts/it_checkpoint.py --reconciliar   # a prova final, quando a coleta acabar

POR QUE ISTO EXISTE
---------------------
Duas trilhas correm ao mesmo tempo. A coleta fecha lotes de vez em quando; a inteligencia
processa o que ja fechou. Sem um livro-caixa, tres coisas acontecem em silencio:

    1. um lote fecha e ninguem processa
    2. o mesmo objeto e processado duas vezes e vira dois
    3. alguem conclui a partir de um arquivo que ainda estava sendo escrito

Este arquivo e o livro-caixa. Ele nao coleta e nao analisa: ele CONTA, e prova.

A UNIDADE E O OBJETO, E A CHAVE E (PLATFORM, EXTERNAL_ID)
----------------------------------------------------------
A mesma do dedupe do `voz.py`. Um episodio que chegue por duas rotas continua sendo um.

O CARIMBO DE CADA LOTE E O SHA256 DO ARQUIVO
----------------------------------------------
Se o sha muda, o lote mudou, e os objetos dele voltam para a fila — porque uma conclusao
tirada de um snapshot que nao existe mais e uma conclusao sem prova.

    SNAPSHOT_SHA DIFERENTE = REPROCESSAR AQUELE LOTE, E SO AQUELE.
    Nunca reprocessar tudo do zero: e caro, e apaga a ordem em que as coisas foram sabidas.
"""
import json
import os
import sys
import glob
import hashlib
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
SAIDA = os.path.join(SAMPLES, 'IT-SNAPSHOT-V1')
LIVRO = os.path.join(SAIDA, 'IT-CHECKPOINT-V1.json')
INVENTARIO = os.path.join(SAIDA, 'IT-INVENTARIO-FALA-V1.json')
CAPTURA = '2026-09-03'
IDADE_MINIMA_S = 120


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()[:16]


def fechado(p):
    return os.path.exists(p) and (time.time() - os.stat(p).st_mtime) > IDADE_MINIMA_S


LOTES = [
    'IT-VIDEO-V1/IT-VIDEO-FALAS-V1.json',
    'IT-VOZ-AUDIO-V1/IT-VOZ-AUDIO-TRANSCRICOES-V1.json',
    'IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-TRANSCRICOES-V2.json',
    'IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-LOCAIS-V2.json',
    'IT-INSTAGRAM-V1/IT-INSTAGRAM-TRANSCRICOES-V1.json',
    'IT-INSTAGRAM-V2/IT-INSTAGRAM-TRANSCRICOES-V2.json',
    'IT-INSTAGRAM-V3/IT-INSTAGRAM-TRANSCRICOES-V3.json',
]


def estado_dos_lotes():
    fila, abertos = [], []
    for rel in LOTES:
        p = os.path.join(SAMPLES, rel)
        if not os.path.exists(p):
            abertos.append({'FILE': rel, 'STATE': 'AUSENTE'})
            continue
        idade = int(time.time() - os.stat(p).st_mtime)
        if idade <= IDADE_MINIMA_S:
            abertos.append({'FILE': rel, 'STATE': 'EM_ESCRITA', 'AGE_S': idade})
            continue
        fila.append({'FILE': rel, 'SHA256_16': sha(p), 'AGE_S': idade, 'STATE': 'FECHADO'})
    return fila, abertos


def carregar():
    if os.path.exists(LIVRO):
        with open(LIVRO, encoding='utf-8') as f:
            return json.load(f)
    return {'DATASET': 'IT-CHECKPOINT-V1', 'CHECKPOINTS': [], 'PROCESSED': {}}


def abrir_checkpoint(rotulo, processados=None):
    """Registra um ponto no tempo: o que estava fechado, o que foi processado ate aqui."""
    livro = carregar()
    fila, abertos = estado_dos_lotes()
    inv = None
    if fechado(INVENTARIO):
        with open(INVENTARIO, encoding='utf-8') as f:
            inv = json.load(f)
    chaves = ['%s|%s' % (r['PLATFORM'], r['EXTERNAL_ID']) for r in (inv or {}).get('ITEMS', [])]
    ja = set(livro['PROCESSED'])
    novos = [k for k in chaves if k not in ja]
    for k in (processados or []):
        livro['PROCESSED'][k] = {'AT': rotulo, 'SNAPSHOT_SHA': (sha(INVENTARIO)
                                                               if fechado(INVENTARIO) else None)}
    livro['CHECKPOINTS'].append({
        'LABEL': rotulo,
        'AT_UTC': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'CLOSED_BATCHES': fila,
        'OPEN_OR_MISSING': abertos,
        'INVENTORY_SHA': sha(INVENTARIO) if fechado(INVENTARIO) else 'INVENTARIO_EM_ESCRITA',
        'OBJECTS_IN_SNAPSHOT': len(chaves),
        'OBJECTS_NEW_SINCE_LAST': len(novos),
        'OBJECTS_MARKED_PROCESSED': len(livro['PROCESSED']),
    })
    livro.update({
        'SOURCE': ('livro-caixa da trilha de inteligencia. Le apenas mtime, sha256 e o '
                   'inventario congelado; nao toca em nada da trilha de coleta.'),
        'SOURCE_ID': 'IT-CHECKPOINT-V1', 'CAPTURED_AT': CAPTURA,
        'CLOSED_RULE': 'arquivo sem escrita ha mais de %d s' % IDADE_MINIMA_S,
        'DEDUPE_KEY': '(PLATFORM, EXTERNAL_ID)',
        'REPROCESS_RULE': ('sha do lote mudou -> os objetos DAQUELE lote voltam para a fila. '
                           'Nunca reprocessar o universo inteiro.'),
    })
    os.makedirs(SAIDA, exist_ok=True)
    with open(LIVRO, 'w', encoding='utf-8') as f:
        json.dump(livro, f, ensure_ascii=False, indent=1)
    return livro


def reconciliar():
    """CICLO 10 — a prova final. Devolve (relatorio, ok)."""
    livro = carregar()
    fila, abertos = estado_dos_lotes()
    with open(INVENTARIO, encoding='utf-8') as f:
        inv = json.load(f)
    chaves = ['%s|%s' % (r['PLATFORM'], r['EXTERNAL_ID']) for r in inv['ITEMS']]
    from collections import Counter
    repetidas = [k for k, n in Counter(chaves).items() if n > 1]
    processadas = set(livro['PROCESSED'])
    sem_processar = [k for k in chaves if k not in processadas]
    fantasmas = [k for k in processadas if k not in set(chaves)]
    shas_agora = {x['FILE']: x['SHA256_16'] for x in fila}
    ultimo = livro['CHECKPOINTS'][-1] if livro['CHECKPOINTS'] else {}
    shas_antes = {x['FILE']: x['SHA256_16'] for x in ultimo.get('CLOSED_BATCHES', [])}
    mudaram = [f for f, s in shas_agora.items() if shas_antes.get(f) not in (None, s)]

    rel = {
        'DATASET': 'IT-RECONCILIACAO-V1',
        'SOURCE': 'contagem propria sobre o inventario congelado e o livro-caixa',
        'SOURCE_ID': 'IT-RECONCILIACAO-V1',
        'CAPTURED_AT': CAPTURA,
        'AT_UTC': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'PROVA_1_NENHUM_FECHADO_SEM_PROCESSAR': {
            'OK': not sem_processar, 'MISSING': sem_processar,
            'MEANS': 'todo objeto de lote fechado passou pela trilha de inteligencia'},
        'PROVA_2_NENHUM_OBJETO_CONTADO_DUAS_VEZES': {
            'OK': not repetidas, 'DUPLICATES': repetidas,
            'MEANS': 'a chave (PLATFORM, EXTERNAL_ID) e unica no universo'},
        'PROVA_3_NENHUMA_CONCLUSAO_DE_ARQUIVO_PARCIAL': {
            'OK': not abertos, 'STILL_OPEN': abertos,
            'MEANS': 'nenhum lote estava em escrita quando o universo foi fechado'},
        'PROVA_4_NENHUM_ACHADO_PERDIDO_POR_TROCA_DE_SNAPSHOT': {
            'OK': not mudaram, 'CHANGED_SINCE_LAST_CHECKPOINT': mudaram,
            'MEANS': 'nenhum lote mudou de sha por baixo de uma conclusao ja tirada'},
        'PROVA_5_SEM_FANTASMA': {
            'OK': not fantasmas, 'PROCESSED_BUT_ABSENT': fantasmas,
            'MEANS': 'nada foi marcado processado sem existir no universo'},
        'DENOMINADORES': {
            'OBJETOS_NO_UNIVERSO': len(chaves),
            'OBJETOS_UNICOS': len(set(chaves)),
            'OBJETOS_PROCESSADOS': len(processadas & set(chaves)),
            'TAXA_DE_PROCESSAMENTO': ('%.1f%%' % (100.0 * len(processadas & set(chaves)) / len(chaves))
                                      if chaves else 'NAO_SEI'),
            'LOTES_FECHADOS': len(fila), 'LOTES_ABERTOS_OU_AUSENTES': len(abertos),
        },
    }
    ok = all(rel[k]['OK'] for k in rel if k.startswith('PROVA_'))
    rel['RECONCILIACAO'] = 'PASS' if ok else 'FAIL'
    p = os.path.join(SAIDA, 'IT-RECONCILIACAO-V1.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(rel, f, ensure_ascii=False, indent=1)
    return rel, ok


if __name__ == '__main__':
    if '--reconciliar' in sys.argv:
        rel, ok = reconciliar()
        for k, v in rel.items():
            if k.startswith('PROVA_'):
                print('%-52s %s' % (k, 'OK' if v['OK'] else 'FALHOU'))
        print()
        for k, v in rel['DENOMINADORES'].items():
            print('%-32s %s' % (k, v))
        print('%-32s %s' % ('RECONCILIACAO', rel['RECONCILIACAO']))
        sys.exit(0 if ok else 1)
    rotulo = sys.argv[1] if len(sys.argv) > 1 else 'checkpoint'
    livro = abrir_checkpoint(rotulo)
    c = livro['CHECKPOINTS'][-1]
    print('checkpoint %r registrado' % rotulo)
    for k in ('OBJECTS_IN_SNAPSHOT', 'OBJECTS_NEW_SINCE_LAST', 'OBJECTS_MARKED_PROCESSED'):
        print('%-28s %s' % (k, c[k]))
    print('%-28s %d fechados · %d em escrita ou ausentes'
          % ('LOTES', len(c['CLOSED_BATCHES']), len(c['OPEN_OR_MISSING'])))
