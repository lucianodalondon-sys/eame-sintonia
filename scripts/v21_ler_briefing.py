#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LER UMA FICHA DO CONTRATO COMERCIAL, em prosa, a partir dos códigos.

    python3 scripts/v21_ler_briefing.py OPP_5F31A63F844D
    python3 scripts/v21_ler_briefing.py --lista
    python3 scripts/v21_ler_briefing.py --caso videira botrite emilia

Este arquivo é um LEITOR, não uma camada: ele não decide nada, não grava nada e
não entra na cadeia. Existe porque um contrato feito de códigos precisa de uma
maneira de ser conferido por gente — e conferir lendo JSON de 400 KB não é
conferir, é fingir que conferiu.

    UM CONTRATO QUE SÓ A MÁQUINA CONSEGUE LER NÃO FOI REVISADO POR NINGUÉM.

A prosa sai do dicionário `PHRASES` do próprio pacote, em PT por padrão. Nenhuma
frase é escrita aqui.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')


def _pkg():
    p = os.path.join(ING, 'OPPORTUNITY-BRIEFINGS.json')
    if not os.path.exists(p):
        print('pacote nao construido: rode bash scripts/v21_cadeia.sh',
              file=sys.stderr)
        raise SystemExit(2)
    return json.load(open(p, encoding='utf-8'))


def _frase(ph, grupo, cod):
    v = (ph.get(grupo) or {}).get(cod)
    if isinstance(v, dict):
        return v.get('PT') or cod
    return v or cod


def _template(ph, bloco, lang='PT'):
    t = (ph.get('BRIEFING_TEMPLATE') or {}).get(bloco.get('TEMPLATE_CODE'))
    if not t:
        return bloco.get('TEMPLATE_CODE') or 'UNKNOWN'
    txt = t[lang]
    vals = dict(bloco.get('SLOTS') or {})
    vals.update({k: v for k, v in (bloco.get('SLOT_LABELS') or {}).items() if v})
    for k, v in vals.items():
        txt = txt.replace('{%s}' % k, str(v))
    return txt


def imprimir(b, ph):
    W = 74
    print('=' * W)
    print('%s   ·   %s' % (b['OPPORTUNITY_ID'], b['PUBLICATION_STATE']))
    print('=' * W)
    h = b['WHAT_IS_HAPPENING']
    print('\nA · O QUE ESTA ACONTECENDO')
    print('  cultura/alvo/regiao : %s · %s · %s'
          % (h['CROP_ID'], h['ISSUE_ID'] or 'SEM ALVO', h['REGION_ID']))
    print('  data / idade        : %s · %s dias'
          % (h['SIGNAL_DATE'], h['SIGNAL_AGE_DAYS']))
    print('  direcao             : %s  (%s · %s)'
          % (h['DIRECTION'], h['DIRECTION_EVIDENCE_ID'], h['DIRECTION_METHOD']))
    print('  forca da evidencia  : %d apoios · familias %s · %d publicadores'
          % (h['EVIDENCE_COUNT'], ', '.join(h['EVIDENCE_FAMILIES']),
             h['PUBLISHER_COUNT']))
    if h['SOURCE_EXCERPT']:
        print('  a frase da fonte    : «%s»' % h['SOURCE_EXCERPT'])
    print('  resumo              : %s' % _template(ph, h['SUMMARY']))

    w = b['WHY_THIS_IS_A_COMMERCIAL_OPPORTUNITY']
    print('\nB · POR QUE ISTO E OPORTUNIDADE COMERCIAL')
    print('  COMMERCIAL_REASON   : %s' % w['COMMERCIAL_REASON_STATE'])
    for elo, v in w['CHAIN'].items():
        print('    %-16s %-24s %s'
              % (elo, v['STATE'], (', '.join(v['EVIDENCE_IDS'][:3])
                                   if v.get('EVIDENCE_IDS') else '')))
    if w['MISSING_LINKS']:
        print('  elos que faltam     : %s' % ', '.join(w['MISSING_LINKS']))
    for c in w['REASON_CODES']:
        print('  regua comercial     : %s' % c)

    print('\nC · POR QUE AGORA')
    print('  WHY_NOW             : %s' % b['WHY_NOW'])
    for c in b['WHY_NOW_CODES']:
        print('    · %s' % _frase(ph, 'WHY_NOW_CODE', c))
    win = b['WINDOW']
    print('  janela              : STATE=%s KIND=%s  ·  COMMERCIAL_WINDOW=%s (de %s)'
          % (win['STATE'], win['KIND'], win['COMMERCIAL_WINDOW'],
             win['COMMERCIAL_WINDOW_FROM']))

    print('\nD · PORTFOLIO  (%d no par · %d so na cultura)'
          % (b['PORTFOLIO_MATCH_COUNT'], b['CROP_LEVEL_ONLY_COUNT']))
    for m in b['PORTFOLIO_MATCHES']:
        subs = ', '.join('%s%s' % (s['NAME'],
                                   ' [FRAC %s]' % s['FRAC'] if s['FRAC'] else
                                   ' [HRAC %s]' % s['HRAC'] if s['HRAC'] else
                                   ' [IRAC %s]' % s['IRAC'] if s['IRAC'] else '')
                         for s in m['ACTIVE_SUBSTANCES']) or 'NAO SEI'
        print('  · %-16s %-8s %s' % (m['PRODUCT_NAME'], m['REGISTRATION_NUMBER'],
                                     m['MATCH_STATE']))
        print('      substancia   : %s' % subs)
        print('      alvo/rotulo  : «%s» (%s)'
              % (m['TARGET_FIT'].get('TARGET_AS_WRITTEN') or 'NAO SEI',
                 m['TARGET_FIT'].get('LINK_STRENGTH') or 'NAO SEI'))
        print('      regulatorio  : %s · %s · vence %s'
              % (m['REGULATORY_FIT']['STATE'],
                 m['REGULATORY_FIT']['AUTHORIZATION_HOLDER'],
                 m['REGULATORY_FIT']['EXPIRY']))
        print('      regiao/janela: %s · %s'
              % (m['REGIONAL_FIT']['STATE'], m['WINDOW_FIT']['STATE']))
        print('      catalogo     : %s · declara a cultura: %s'
              % (m['COMMERCIAL_CATALOG']['STATE'],
                 'SIM' if m['COMMERCIAL_CATALOG']['CATALOG_DECLARES_CROP'] else 'NAO'))
        print('      validacao    : %s · restricoes: %s'
              % (m['VALIDATION_STATE'], ', '.join(m['RESTRICTION_CODES']) or '-'))
        print('      evidencia    : %s' % ', '.join(m['EVIDENCE_IDS']))
    print('  PRIMARY_MATCH       : %s  (%s)'
          % (b['PRIMARY_MATCH'] or 'UNKNOWN', b['PRIMARY_MATCH_RULE']))

    print('\nE · RAZAO DE VENDA')
    sr = b['SALES_REASON']
    print('  %s' % sr['STATE'])
    if sr['STATE'] != 'UNKNOWN':
        print('  «%s»' % _template(ph, sr))
        for k, v in sr['SLOT_EVIDENCE_IDS'].items():
            print('    %-10s <- %s' % (k, ', '.join(v) or 'sem evidencia'))

    print('\nF · O QUE FALTA')
    for c in b['WHAT_IS_MISSING']:
        print('  · %-24s %s' % (c, _frase(ph, 'WHAT_IS_MISSING', c)))

    print('\nG · MAPA DE ACAO')
    for a in b['ACTION_MAP']:
        print('  %-20s %-10s %s' % (a['DEPARTMENT'], a['ACTION_STATE'],
                                    _frase(ph, 'ACTION_CODE', a['ACTION_CODE'])))
        print('      dependencia : %s' % (a['DEPENDENCY'] or '-'))
        print('      gatilho     : %s' % _frase(ph, 'NEXT_TRIGGER',
                                                a['NEXT_TRIGGER']))
        if a['EVIDENCE_IDS']:
            print('      evidencia   : %s' % ', '.join(a['EVIDENCE_IDS']))

    print('\nH · EVIDENCIAS (%d)' % len(b['EVIDENCES']))
    for e in b['EVIDENCES']:
        print('  %-16s %-26s %s' % (e['EVIDENCE_ID'], e['EVIDENCE_ROLE'],
                                    e['REFERENCE_DATE'] or ''))
        print('      %s' % _frase(ph, 'INTELLIGENCE_SUMMARY_CODE',
                                  e['INTELLIGENCE_SUMMARY_CODE']))
        print('      implicacao  : %s'
              % _frase(ph, 'COMMERCIAL_IMPLICATION_CODE',
                       e['COMMERCIAL_IMPLICATION_CODE']))
        print('      departamento: %s' % (e['DEPARTMENT_ACTION'] or '-'))
        if e['SOURCE_URLS']:
            print('      fonte       : %s' % e['SOURCE_URLS'][0][:100])
    print('\n  %s' % b['BRIEFING_DOES_NOT_PROVE'])


def main():
    d = _pkg()
    ph = d['PHRASES']
    args = sys.argv[1:]
    if not args or args[0] == '--lista':
        print('%-20s %-14s %-24s %-14s %s'
              % ('OPPORTUNITY', 'WHY_NOW', 'CULTURA x ALVO', 'REGIAO', 'PUBLICACAO'))
        for b in d['RECORDS']:
            h = b['WHAT_IS_HAPPENING']
            print('%-20s %-14s %-24s %-14s %s'
                  % (b['OPPORTUNITY_ID'], b['WHY_NOW'],
                     '%s x %s' % ((h['CROP_ID'] or 'SEM_CULTURA')
                                  .replace('CROP_', ''),
                                  (h['ISSUE_ID'] or 'SEM_ALVO')
                                  .replace('ISSUE_', '')),
                     (h['REGION_ID'] or '')[:14], b['PUBLICATION_STATE']))
        return 0
    if args[0] == '--caso':
        termos = [t.lower() for t in args[1:]]
        alvo = [b for b in d['RECORDS']
                if all(t in json.dumps(b['WHAT_IS_HAPPENING']).lower()
                       for t in termos)]
    else:
        alvo = [b for b in d['RECORDS'] if b['OPPORTUNITY_ID'] in args
                or b['ID'] in args]
    if not alvo:
        print('nenhuma ficha para %s' % ' '.join(args), file=sys.stderr)
        return 1
    for b in alvo:
        imprimir(b, ph)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
