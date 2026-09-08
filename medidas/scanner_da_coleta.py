#!/usr/bin/env python3
"""O SCANNER — o relatorio de uma corrida, GERADO e nunca escrito a mao.

    python3 medidas/scanner_da_coleta.py <RUN_ID>
    python3 medidas/scanner_da_coleta.py --janela 2026-09-08T14 --ate 2026-09-08T15

Ele responde as perguntas que fizeram esta missao existir: por onde passou,
quanto entrou, quanto saiu, o que sumiu, onde parou, onde retomar, quanto
custou, quanto demorou.

    SE NAO HA TELEMETRIA, DIZ `NOT_INSTRUMENTED`.
    NUNCA VERDE POR AUSENCIA.

Uma corrida sem passagem nenhuma nao e uma corrida saudavel: e uma corrida que
nao foi medida, e as duas coisas parecem iguais em qualquer painel que pinte o
vazio de verde.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import _gavetas  # noqa: E402,F401
import coleta_checkpoint as cc      # noqa: E402
import rastro_da_coleta as r        # noqa: E402
import diagnostico as dg            # noqa: E402

SAUDE_OK = 'PASS'
SAUDE_AVISO = 'WARN'
SAUDE_ERRO = 'ERROR'
NAO_MEDIDA = 'NOT_INSTRUMENTED'


def saude(passagens):
    """PASS / WARN / ERROR / NOT_INSTRUMENTED. Vazio nunca e PASS."""
    if not passagens:
        return NAO_MEDIDA
    if any(p['ESTADO'] == r.ERROR for p in passagens):
        return SAUDE_ERRO
    if any(p['UNACCOUNTED'] for p in passagens):
        return SAUDE_ERRO           # buraco na contabilidade e erro, nao aviso
    if any(p['ESTADO'] in (r.NOT_RUN, r.UNKNOWN) for p in passagens):
        return SAUDE_AVISO
    return SAUDE_OK


def relatorio(banco, run_id):
    ps = r.passagens(banco, run_id=run_id)
    integ = r.integridade(ps)
    return {
        'RUN_ID': run_id,
        'HEALTH': saude(ps),
        'PASSAGENS': ps,
        'ULTIMO_BOM': r.ultimo_bom(ps),
        'RETRY_FROM': r.onde_retomar(ps),
        'INTEGRIDADE': integ,
        'DIAGNOSTICOS': sorted({p['DIAGNOSTIC_CODE'] for p in ps
                                if p['DIAGNOSTIC_CODE']}),
        'CUSTO_USD': sum(float(p['CUSTO_USD'] or 0) for p in ps),
        'DURACAO_MS': sum(p['DURACAO_MS'] for p in ps),
        'INSTRUMENTADA': bool(ps),
        'NOTA': None if ps else r.SEM_INSTRUMENTO,
    }


def imprimir(rel):
    print('RUN %s' % rel['RUN_ID'])
    print('HEALTH %s' % rel['HEALTH'])
    if not rel['INSTRUMENTADA']:
        print()
        print('  %s — esta corrida e anterior ao instrumento.' % rel['NOTA'])
        print('  Nao ha rastro, e nao se inventa um. Isto NAO e uma corrida sa:')
        print('  e uma corrida que ninguem mediu.')
        return
    print()
    print('  %-11s %-9s %-11s %6s %-11s %6s  %5s %5s %5s %5s  %4s'
          % ('ETAPA', 'ESTADO', 'GRAO-IN', 'IN', 'GRAO-OUT', 'OUT',
             'PASS', 'REJ', 'UNK', 'ERR', 'S/EX'))
    print('  ' + '-' * 96)
    for p in rel['PASSAGENS']:
        print('  %-11s %-9s %-11s %6s %-11s %6s  %5d %5d %5d %5d  %4d'
              % (p['ETAPA'], p['ESTADO'], p['INPUT_GRAIN'] or '—',
                 p['INPUT_COUNT'] if p['INPUT_COUNT'] is not None else '—',
                 p['OUTPUT_GRAIN'] or '—',
                 p['OUTPUT_COUNT'] if p['OUTPUT_COUNT'] is not None else '—',
                 p['PASSED'], p['REJECTED'], p['UNKNOWN'], p['ERROR'],
                 p['UNACCOUNTED']))
        y = r.rendimento(p)
        if y.get('GRAIN_CHANGED'):
            print('              ↳ %s → %s · SEM RENDIMENTO: %s'
                  % (y['INPUT'], y['OUTPUT'], y['PORQUE'][:58]))
    print()
    print('  LAST_GOOD_STAGE  %s' % (rel['ULTIMO_BOM'] or '—'))
    print('  RETRY_FROM       %s' % (rel['RETRY_FROM'] or '—'))
    print('  ACCOUNTED        %s' % ('tudo explicado'
                                     if rel['INTEGRIDADE']['INTEGRO']
                                     else '%d SEM EXPLICACAO em %s'
                                     % (rel['INTEGRIDADE']['UNACCOUNTED_INPUT'],
                                        ', '.join(rel['INTEGRIDADE']['ETAPAS_COM_BURACO']))))
    for c in rel['DIAGNOSTICOS']:
        print('  DIAGNOSTIC       %-26s %s' % (c, dg.dono(c)))
        print('                   %s' % dg.explicar(c))
    print('  CUSTO USD        %.6f' % rel['CUSTO_USD'])
    print('  DURACAO ms       %d' % rel['DURACAO_MS'])


def janela(banco, de, ate):
    """Por hora, fonte, rota e etapa. Sai da view, nao de agregacao guardada."""
    linhas = banco.executa(
        "select to_char(hora,'YYYY-MM-DD HH24:MI'), coalesce(source_id,'-'),"
        " coalesce(route_class_id,'-'), etapa::text,"
        " coalesce(input_grain,'-'), coalesce(output_grain,'-'),"
        " entraram, sairam, passaram, recusados, unknown, com_erro,"
        " sem_explicacao, custo_usd::text, duracao_ms"
        " from public.v_coleta_por_hora"
        " where hora >= '%s' and hora < '%s' order by 1,2,4" % (de, ate))
    campos = ('HORA', 'SOURCE_ID', 'ROUTE', 'ETAPA', 'GRAO_IN', 'GRAO_OUT',
              'ENTRARAM', 'SAIRAM', 'PASSARAM', 'RECUSADOS', 'UNKNOWN',
              'COM_ERRO', 'SEM_EXPLICACAO', 'CUSTO_USD', 'DURACAO_MS')
    return [dict(zip(campos, l[:len(campos)])) for l in linhas]


def main():
    dsn = os.environ.get('BANCO_DESCARTAVEL_URL') or os.environ.get('SUPABASE_DB_URL')
    if not dsn:
        raise SystemExit('sem DSN: o scanner le o rastro, e o rastro vive no banco')
    banco = cc.Banco(dsn)
    args = sys.argv[1:]
    if not args:
        raise SystemExit('uso: scanner_da_coleta.py <RUN_ID> | --janela <de> --ate <ate>')
    if args[0] == '--janela':
        for l in janela(banco, args[1], args[3]):
            print(' '.join('%s=%s' % (k, v) for k, v in l.items()))
        return
    imprimir(relatorio(banco, args[0]))


if __name__ == '__main__':
    main()
