#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O VÃO · quais janelas faltam para os casos que já existem.

    python3 scripts/v21_vao_de_janelas.py

A V11.2 consertou o vínculo de janela e, ao consertá-lo, mediu um vazio: nenhum
caso comercial tem hoje janela que intersecte cultura × alvo × região. Este
arquivo NÃO conserta nada e NÃO coleta nada. Ele diz, caso a caso, POR QUE não
há janela — e junta os «não há» em combinações comerciais, não em documentos.

    NÃO SE CONTA DOCUMENTO. CONTA-SE A COMBINAÇÃO QUE PRECISA DE RESPOSTA.

O motivo da ausência sai de `OP.janela_vale`, a mesma função que o motor usa.
Nada aqui é uma segunda implementação da regra: se a regra mudar, este relatório
muda junto — e é assim que ele continua verdadeiro.

⚠️ A PRIORIDADE É `PRIORIDADE_NAO_CANONICA`. Cada CHAVE de ordenação tem dono no
acervo — `COMMERCIAL_PRIORITY`, `EXTERNAL_MATERIAL_READY`, `SOURCE_IDS` dos
sinais, a contagem de regiões do par. O que não tem dono é a COMPOSIÇÃO delas
num ranking: isso é escolha desta missão, e por isso vai marcada.
"""
import json
import os
import sys
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import v21_normalizar as N  # noqa: E402
import v21_oportunidades as OP  # noqa: E402

ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'V112-VAO-DE-JANELAS.json')

# Um caso só PRECISA de janela de aplicação se ele tem os três eixos. Sem alvo
# declarado não há «janela para o quê»; sem região declarada não há «janela de
# quem». Isso não é defeito do caso: é a natureza do arquétipo.
SEM_ALVO = 'CASO_SEM_ALVO_DECLARADO'
SEM_REGIAO = 'CASO_DE_ESCOPO_SUPRA_REGIONAL'


def _le(nome):
    return json.load(open(os.path.join(ING, nome), encoding='utf-8'))['RECORDS']


def _nome(tabela, ident):
    """O primeiro apelido do léxico é o nome italiano da fonte."""
    if not ident:
        return None
    v = tabela.get(ident)
    return v[0] if v else ident


def _regiao_nome(rid):
    if not rid or not str(rid).startswith('REGION_'):
        return None
    for r in N.REGIOES:
        if 'REGION_' + __import__('re').sub(r'[^A-Z]+', '_', r.upper()).strip('_') == rid:
            return r
    return rid


def motivo(caso, janelas):
    """Por que este caso não tem janela — em termos do que o acervo declara."""
    crop, alvo, geo = caso['CROP'], caso['TARGET'], caso['GEOGRAPHY']
    da_cultura = [w for w in janelas if crop in (w.get('CROP_IDS') or [])]
    if not da_cultura:
        return 'NENHUMA_JANELA_PARA_A_CULTURA'
    sem_id = [w for w in da_cultura
              if not (w.get('ISSUE_IDS') or []) and OP._declarado(w.get('ISSUE'))]
    do_par = [w for w in da_cultura if alvo in (w.get('ISSUE_IDS') or [])]
    if do_par:
        return 'JANELA_DO_PAR_MAS_DE_OUTRA_REGIAO'
    if sem_id and len(sem_id) == len(da_cultura):
        return 'JANELA_DA_CULTURA_COM_ALVO_SEM_IDENTIFICADOR'
    return 'JANELA_DA_CULTURA_MAS_DE_OUTRO_ALVO'


def linhas():
    janelas = _le('CROP-WINDOWS.json')
    sinais = {s['ID']: s for s in _le('CURRENT-FIELD-SIGNALS.json')}
    fora = []
    for c in _le('OPPORTUNITIES.json'):
        casa = [w['ID'] for w in janelas
                if OP.janela_vale(w, c['CROP'], c['TARGET'], c['GEOGRAPHY'])]
        apoios = [sinais[i] for i in (c.get('EVIDENCE_IDS') or []) if i in sinais]
        if not c.get('TARGET'):
            m = SEM_ALVO
        elif not str(c.get('GEOGRAPHY') or '').startswith('REGION_'):
            m = SEM_REGIAO
        elif casa:
            m = None
        else:
            m = motivo(c, janelas)
        fora.append({
            'ID': c['ID'],
            'COUNTRY': 'IT',
            'REGION_ID': c['GEOGRAPHY'],
            'REGION_NAME': _regiao_nome(c['GEOGRAPHY']),
            'CROP_ID': c['CROP'],
            'CROP_NAME': _nome(N.CROP_ALIAS, c['CROP']),
            'ISSUE_ID': c['TARGET'],
            'ISSUE_NAME': _nome(N.ISSUE_ALIAS, c['TARGET']),
            'ARCHETYPE': c['ARCHETYPE'],
            'COMMERCIAL_PRIORITY': c['COMMERCIAL_PRIORITY'],
            'EXTERNAL_MATERIAL_READY': c['EXTERNAL_MATERIAL_READY'],
            'NEED_DIRECTION': c['NEED_DIRECTION'],
            'SIGNAL_EVIDENCE_IDS': [s['ID'] for s in apoios],
            'SIGNAL_SOURCE_IDS': sorted({(s.get('SOURCE_IDS') or [None])[0]
                                         for s in apoios} - {None}),
            'NEED_EVIDENCE_ID': c.get('NEED_EVIDENCE_ID'),
            'NEED_EXCERPT': c.get('NEED_EXCERPT'),
            'HAS_COMPATIBLE_WINDOW': 'SIM' if casa else 'NAO',
            'MATCHING_WINDOW_IDS': casa,
            'ABSENCE_REASON': m,
        })
    return fora


def combinacoes(rows):
    """Agrupa por PAÍS × REGIÃO × CULTURA × ALVO — a combinação comercial."""
    ix = defaultdict(list)
    for r in rows:
        if r['ABSENCE_REASON'] in (SEM_ALVO, SEM_REGIAO):
            continue
        ix[(r['COUNTRY'], r['REGION_ID'], r['CROP_ID'], r['ISSUE_ID'])].append(r)
    fora = []
    for (pais, reg, crop, alvo), rs in ix.items():
        fora.append({
            'COUNTRY': pais, 'REGION_ID': reg, 'REGION_NAME': rs[0]['REGION_NAME'],
            'CROP_ID': crop, 'CROP_NAME': rs[0]['CROP_NAME'],
            'ISSUE_ID': alvo, 'ISSUE_NAME': rs[0]['ISSUE_NAME'],
            'CASES': [r['ID'] for r in rs],
            'HAS_WINDOW': 'SIM' if any(r['HAS_COMPATIBLE_WINDOW'] == 'SIM'
                                       for r in rs) else 'NAO',
            'ABSENCE_REASON': rs[0]['ABSENCE_REASON'],
            'COMMERCIAL_PRIORITY': rs[0]['COMMERCIAL_PRIORITY'],
            'EXTERNAL_MATERIAL_READY': rs[0]['EXTERNAL_MATERIAL_READY'],
            'NEED_DIRECTION': rs[0]['NEED_DIRECTION'],
            'INDEPENDENT_SOURCES': len(rs[0]['SIGNAL_SOURCE_IDS']),
            'SIGNAL_SOURCE_IDS': rs[0]['SIGNAL_SOURCE_IDS'],
            'SIGNALS': len(rs[0]['SIGNAL_EVIDENCE_IDS']),
        })
    # ── a ordenação, com o dono de cada chave declarado ─────────────────────
    regioes_do_par = defaultdict(set)
    for c in fora:
        regioes_do_par[(c['CROP_ID'], c['ISSUE_ID'])].add(c['REGION_ID'])
    for c in fora:
        c['REGIONS_OF_PAIR'] = len(regioes_do_par[(c['CROP_ID'], c['ISSUE_ID'])])
        c['RANK_KEYS'] = {
            'A_SALES_READY': c['COMMERCIAL_PRIORITY'] == 'SALES_READY',
            'B_EXTERNAL_YES': c['EXTERNAL_MATERIAL_READY'] == 'YES',
            'C_INDEPENDENT_SOURCES': c['INDEPENDENT_SOURCES'],
            'D_REGIONS_OF_PAIR': c['REGIONS_OF_PAIR'],
            'E_DURUM_WHEAT': c['CROP_ID'] == 'CROP_DURUM_WHEAT',
        }
    fora.sort(key=lambda c: (
        0 if c['RANK_KEYS']['A_SALES_READY'] else 1,
        0 if c['RANK_KEYS']['B_EXTERNAL_YES'] else 1,
        -c['RANK_KEYS']['C_INDEPENDENT_SOURCES'],
        -c['RANK_KEYS']['D_REGIONS_OF_PAIR'],
        0 if c['RANK_KEYS']['E_DURUM_WHEAT'] else 1,
        c['REGION_ID'], c['CROP_ID'], c['ISSUE_ID']))
    for i, c in enumerate(fora, 1):
        c['RANK'] = i
    return fora


def main():
    rows = linhas()
    combos = combinacoes(rows)
    sem = [c for c in combos if c['HAS_WINDOW'] == 'NAO']
    com = [c for c in combos if c['HAS_WINDOW'] == 'SIM']

    print('=' * 78)
    print('CASOS: %d' % len(rows))
    for m in (None, SEM_ALVO, SEM_REGIAO):
        n = len([r for r in rows if r['ABSENCE_REASON'] == m])
        print('  %-38s %d' % (m or 'COM JANELA COMPATIVEL', n))
    for m in sorted({r['ABSENCE_REASON'] for r in rows} - {None, SEM_ALVO, SEM_REGIAO}):
        print('  %-38s %d' % (m, len([r for r in rows if r['ABSENCE_REASON'] == m])))

    print()
    print('=' * 78)
    print('COMBINACOES COMERCIAIS (PAIS x REGIAO x CULTURA x ALVO)')
    print('  TOTAL_DE_COMBINACOES_NECESSARIAS : %d' % len(combos))
    print('  COM_JANELA                       : %d' % len(com))
    print('  SEM_JANELA                       : %d' % len(sem))
    print('=' * 78)
    print('\nRANKING FACTUAL DAS AUSENTES  ·  PRIORIDADE_NAO_CANONICA')
    print('  %-3s %-24s %-14s %-20s %-14s %s'
          % ('#', 'REGIAO', 'CULTURA', 'ALVO', 'PRIORIDADE', 'FONTES/REGIOES'))
    for c in sem:
        print('  %-3d %-24s %-14s %-20s %-14s %d/%d'
              % (c['RANK'], c['REGION_NAME'], c['CROP_NAME'], c['ISSUE_NAME'],
                 c['COMMERCIAL_PRIORITY'], c['INDEPENDENT_SOURCES'],
                 c['REGIONS_OF_PAIR']))
        print('      motivo: %s · casos: %s' % (c['ABSENCE_REASON'],
                                                ', '.join(c['CASES'])))

    fora = {
        'COLLECTION': 'V112-VAO-DE-JANELAS',
        'SOURCE': 'build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST '
                  '(OPPORTUNITIES, CROP-WINDOWS, CURRENT-FIELD-SIGNALS)',
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'o motivo da ausencia sai de OP.janela_vale, a mesma funcao do '
               'motor. Nao ha segunda implementacao da regra aqui.',
        'PRIORITY_STATE': 'PRIORIDADE_NAO_CANONICA',
        'PRIORITY_NOTE': 'cada chave de ordenacao tem dono no acervo; a '
                         'composicao delas num ranking nao tem, e por isso vai '
                         'marcada.',
        'TOTAL_DE_COMBINACOES_NECESSARIAS': len(combos),
        'COM_JANELA': len(com),
        'SEM_JANELA': len(sem),
        'CASES': rows,
        'COMBINATIONS': combos,
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(fora, open(SAIDA, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\ngravado em %s' % os.path.relpath(SAIDA, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
