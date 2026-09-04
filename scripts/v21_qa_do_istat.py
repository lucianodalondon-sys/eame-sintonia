#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA DO ISTAT · a revisão que falta, feita como teste e não como opinião.

    python3 scripts/v21_qa_do_istat.py

As 2 945 linhas do ISTAT estão no acervo, com URL, dataset e ano, e estão todas
`QA_UNREVIEWED` — logo `CLIENT_SAFE = false`. Por causa disso, os 43 cartões
carregam `OFFICIAL_AREA_NOT_CLIENT_SAFE` em `WHAT_IS_MISSING`, e o tamanho
comercial de cada caso fica sem a única dimensão oficial que existe.

    O QUE IMPEDE O DADO DE APARECER NÃO É O DADO. É O CARIMBO QUE FALTA.

Este arquivo NÃO carimba nada. Ele executa a revisão que o carimbo exigiria e
diz se o dado sobreviveria a ela — por ano, porque 2024 e 2026 não são a mesma
coisa: o ISTAT publica 2026 como estimativa provisória, e provisório revisto
não é erro nosso, é o método deles.

    CARIMBAR SEM TESTEMUNHA É OPINIÃO COM CARA DE PROCESSO.
    E CARIMBAR PROVISÓRIO COMO DEFINITIVO É ERRAR EM SILÊNCIO SEIS MESES DEPOIS.
"""
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
TOLERANCIA = 0.02      # 2% — arredondamento do quintal publicado, não margem


def _le(nome):
    with open(os.path.join(ING, nome), encoding='utf-8') as f:
        return json.load(f)['RECORDS']


def provas(linhas):
    """→ {nome da prova: [linhas que falharam]}. Vazio é aprovado."""
    f = defaultdict(list)
    for r in linhas:
        if not r.get('SOURCE_URLS'):
            f['SEM_URL_DE_FONTE'].append(r['ID'])
        if not r.get('DATASET'):
            f['SEM_DATASET_DECLARADO'].append(r['ID'])
        if not r.get('UNIT'):
            f['SEM_UNIDADE'].append(r['ID'])
        try:
            if float(r.get('VALUE')) <= 0:
                f['VALOR_NAO_POSITIVO'].append(r['ID'])
        except (TypeError, ValueError):
            f['VALOR_NAO_NUMERICO'].append(r['ID'])
        if r.get('IS_DERIVED_BY_SINTONIA') and not r.get('DERIVATION_FORMULA'):
            f['DERIVADO_SEM_FORMULA'].append(r['ID'])
        if not r.get('IS_DERIVED_BY_SINTONIA') and r.get('DERIVATION_FORMULA'):
            f['NAO_DERIVADO_COM_FORMULA'].append(r['ID'])
        if not r.get('GEOGRAPHY_CODE'):
            f['SEM_CODIGO_DE_GEOGRAFIA'].append(r['ID'])

    chave = Counter((r.get('CROP_CODE'), r.get('GEOGRAPHY_CODE'), r.get('YEAR'),
                     r.get('INDICATOR')) for r in linhas)
    for k, n in chave.items():
        if n > 1:
            f['CHAVE_DUPLICADA'].append(str(k))

    unidade = defaultdict(set)
    for r in linhas:
        unidade[r['INDICATOR']].add(r.get('UNIT'))
    for ind, us in unidade.items():
        if len(us) > 1:
            f['UNIDADE_INSTAVEL_NO_INDICADOR'].append('%s: %s' % (ind, sorted(us)))

    ix = defaultdict(dict)
    for r in linhas:
        ix[(r.get('CROP_CODE'), r.get('GEOGRAPHY_CODE'), r.get('YEAR'))][
            r['INDICATOR']] = r
    for k, v in ix.items():
        a, p, y = v.get('AREA'), v.get('PRODUCTION'), v.get('YIELD')
        if not (a and p and y):
            continue
        try:
            area, prod, rend = (float(a['VALUE']), float(p['VALUE']),
                                float(y['VALUE']))
        except (TypeError, ValueError):
            continue
        if not area or not rend:
            continue
        if abs((prod / 10.0) / area - rend) / rend > TOLERANCIA:
            f['RENDIMENTO_NAO_FECHA_COM_AREA_E_PRODUCAO'].append(str(k))
    return dict(f)


def impacto_por_ano(linhas, ops):
    """Carimbar POR ANO — quanto isso libera, e o que muda de verdade.

    A pergunta não é «quantas linhas ficam client-safe». É «quantos dos 43 casos
    passam a ter área oficial, e algum resultado comercial muda por isso?».

        LIBERAR DADO NÃO É MUDAR DECISÃO. SÃO DUAS MEDIÇÕES, E A SEGUNDA É A
        QUE INTERESSA.
    """
    por_ano = defaultdict(list)
    for r in linhas:
        por_ano[r.get('YEAR')].append(r)
    # o motor liga a área por CULTURA × GEOGRAFIA, e só para o indicador AREA
    fora = {}
    for ano in sorted(por_ano):
        area = {(r.get('CROP_CODE'), reg)
                for r in por_ano[ano] if r.get('INDICATOR') == 'AREA'
                for reg in (r.get('REGION_IDS') or [])}
        # o cartão não guarda CROP_CODE; a ligação real do motor é por CROP_ID
        ids = {(r.get('CROP_IDS') or [None])[0]: None for r in por_ano[ano]}
        alcanca = [o['ID'] for o in ops
                   if any(o.get('CROP') == c and o.get('GEOGRAPHY') in (r.get('REGION_IDS') or [])
                          for r in por_ano[ano] if r.get('INDICATOR') == 'AREA'
                          for c in (r.get('CROP_IDS') or []))]
        fora[ano] = {
            'LINHAS': len(por_ano[ano]),
            'LINHAS_AREA': sum(1 for r in por_ano[ano] if r.get('INDICATOR') == 'AREA'),
            'PARES_CULTURA_X_GEOGRAFIA': len(area),
            'CASOS_DOS_43_QUE_CONSOMEM': len(set(alcanca)),
            'CASOS': sorted(set(alcanca)),
        }
        del ids
    return fora


def qual_ano_alimenta(linhas, ops):
    """QUAL ANO DEVE ALIMENTAR `COMMERCIAL_MAGNITUDE`? — os candidatos, medidos.

    Antes desta rodada a resposta era «o primeiro do arquivo», que não é
    critério nenhum. O motor passou a escolher com um critério explícito; qual
    critério DEVE ser é decisão, e esta função mede o que cada candidato daria.

        UM NÚMERO QUE MUDA DE SIGNIFICADO PELA ORDEM DO ARQUIVO
        É UM NÚMERO SEM DONO.
    """
    porta = {}          # (crop, regiao) -> {ano: linha AREA}
    for r in linhas:
        if r.get('INDICATOR') != 'AREA':
            continue
        for c in (r.get('CROP_IDS') or []):
            for g in (r.get('REGION_IDS') or []):
                porta.setdefault((c, g), {})[r.get('YEAR')] = r
    qa = {2024: 'YES', 2025: 'YES', 2026: 'UNKNOWN'}

    def escolher(anos, criterio, ano_do_sinal):
        if not anos:
            return None
        if criterio == 'ULTIMO_QA_PASS':
            ok = [a for a in anos if qa.get(a) == 'YES']
            return max(ok) if ok else None
        if criterio == 'ANO_MAIS_RECENTE':
            return max(anos)
        if criterio == 'ANO_DO_SINAL':
            return ano_do_sinal if ano_do_sinal in anos else None
        return None

    CRITERIOS = ('ULTIMO_QA_PASS', 'ANO_MAIS_RECENTE', 'ANO_DO_SINAL')
    linhas_fora, discordam = [], 0
    for o in ops:
        anos = sorted(porta.get((o.get('CROP'), o.get('GEOGRAPHY')), {}))
        if not anos:
            continue
        try:
            ano_sinal = int(str(o.get('SIGNAL_DATE') or '')[:4])
        except ValueError:
            ano_sinal = None
        esc = {c: escolher(anos, c, ano_sinal) for c in CRITERIOS}
        if len({v for v in esc.values() if v is not None}) > 1:
            discordam += 1
        linhas_fora.append({'OPPORTUNITY_ID': o['ID'], 'CROP': o.get('CROP'),
                            'GEOGRAPHY': o.get('GEOGRAPHY'),
                            'ANOS_DISPONIVEIS': anos,
                            'ANO_DO_SINAL': ano_sinal, 'ESCOLHA': esc})
    return {
        'PERGUNTA': 'qual ano deve alimentar COMMERCIAL_MAGNITUDE?',
        'CONTRATO_EXISTENTE': (
            'o repositorio tem dois contratos que se compoem: «o documento mais '
            'recente que afirma alguma coisa responde por ela, e empate '
            'desfaz-se pelo ID» (v21_oportunidades.declarados) e «so material '
            'client-safe entra no cartao». Juntos dao ULTIMO_QA_PASS. Nao ha '
            'contrato escrito que mande usar o ano do SINAL.'),
        'CRITERIO_APLICADO_HOJE': 'MAIS_RECENTE_ENTRE_AS_CLIENT_SAFE',
        'POLITICA': 'DECISION_REQUIRED',
        'CASOS_MEDIDOS': len(linhas_fora),
        'CASOS_EM_QUE_OS_CRITERIOS_DISCORDAM': discordam,
        'CASOS': linhas_fora[:60],
    }


def main():
    linhas = [r for r in _le('CROP-ECONOMIC-WEIGHT.json')
              if 'ISTAT' in str(r.get('SOURCE_IDS')) and r.get('INDICATOR')]
    por_ano = defaultdict(list)
    for r in linhas:
        por_ano[r.get('YEAR')].append(r)

    veredito, detalhe = {}, {}
    for ano in sorted(por_ano):
        falhas = provas(por_ano[ano])
        # ⚠️ 2026 é ESTIMATIVA PROVISÓRIA do próprio ISTAT — `OBSERVATION_CLASS
        # = OUTLOOK`. Passar nas provas de coerência não o torna definitivo: o
        # que o teste pode dizer é que a linha é internamente sã, não que o
        # número não vai ser revisto.
        provisorio = all(r.get('OBSERVATION_CLASS') == 'OUTLOOK'
                         for r in por_ano[ano])
        veredito[ano] = ('NO' if falhas else
                         'UNKNOWN' if provisorio else 'YES')
        detalhe[ano] = {'LINHAS': len(por_ano[ano]),
                        'PROVISORIO': provisorio,
                        'FALHAS': {k: len(v) for k, v in falhas.items()},
                        'EXEMPLOS': {k: v[:3] for k, v in falhas.items()}}

    geral = ('NO' if 'NO' in veredito.values() else
             'YES' if set(veredito.values()) == {'YES'} else 'PARTIAL')

    # O que o carimbo custaria — para a decisão ser tomada com o número na mão.
    ops = _le('OPPORTUNITIES.json')
    afetados = sum(1 for o in ops
                   if 'OFFICIAL_AREA_NOT_CLIENT_SAFE' in (o.get('WHAT_IS_MISSING') or []))

    print('linhas ISTAT: %d\n' % len(linhas))
    for ano in sorted(veredito):
        d = detalhe[ano]
        print('%s · %4d linhas · %s%s' % (
            ano, d['LINHAS'], veredito[ano],
            '  (estimativa provisoria do ISTAT)' if d['PROVISORIO'] else ''))
        for k, n in d['FALHAS'].items():
            print('      %-42s %d  %s' % (k, n, d['EXEMPLOS'][k]))
    print('\nQA_PASS = %s' % geral)
    print('CARIMBO NAO APLICADO. Aplicá-lo tornaria %d linhas client-safe e '
          'tiraria OFFICIAL_AREA_NOT_CLIENT_SAFE de %d cartoes.'
          % (sum(len(por_ano[a]) for a in veredito if veredito[a] == 'YES'),
             afetados))

    impacto = impacto_por_ano(linhas, ops)
    print('\nIMPACTO DO CARIMBO, ANO A ANO')
    for ano in sorted(impacto):
        i = impacto[ano]
        print('  %s · %4d linhas (%d de AREA) · %3d pares cultura x geografia '
              '· %2d dos 43 casos' % (ano, i['LINHAS'], i['LINHAS_AREA'],
                                      i['PARES_CULTURA_X_GEOGRAFIA'],
                                      i['CASOS_DOS_43_QUE_CONSOMEM']))
    # ⚠️ E A PERGUNTA QUE IMPORTA: o carimbo move alguma decisão comercial?
    # `AREA_OFICIAL_HA` alimenta COMMERCIAL_MAGNITUDE e a lista do que falta.
    # `v21_comercial.prioridade` não o lê — os portões são semânticos, e área
    # não é portão. Então a resposta é NÃO, e é verificável lendo os dois.
    print('\nMUDA ALGUM RESULTADO COMERCIAL? NAO — AREA_OFICIAL_HA alimenta '
          'COMMERCIAL_MAGNITUDE e WHAT_IS_MISSING, e nenhum portao de '
          'v21_comercial.prioridade a le.')

    ano = qual_ano_alimenta(linhas, ops)
    print('\nQUAL ANO ALIMENTA COMMERCIAL_MAGNITUDE?')
    print('  criterio aplicado hoje : %s' % ano['CRITERIO_APLICADO_HOJE'])
    print('  politica               : %s' % ano['POLITICA'])
    print('  casos medidos          : %d · criterios discordam em %d'
          % (ano['CASOS_MEDIDOS'], ano['CASOS_EM_QUE_OS_CRITERIOS_DISCORDAM']))

    fora = {
        'COLLECTION': 'V115-QA-DO-ISTAT',
        'SOURCE': 'build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/'
                  'CROP-ECONOMIC-WEIGHT.json · linhas com SOURCE_IDS do ISTAT',
        'CAPTURED_AT': date.today().isoformat(),
        'LAW': 'mede se o dado sobreviveria a uma revisao. NAO carimba, NAO '
               'coleta e NAO muda CLIENT_SAFE de linha nenhuma.',
        'QA_PASS': geral,
        'QA_PASS_BY_YEAR': veredito,
        'DETAIL_BY_YEAR': detalhe,
        'LINES': len(linhas),
        'CARDS_WITH_OFFICIAL_AREA_NOT_CLIENT_SAFE': afetados,
        'IMPACT_BY_YEAR': impacto,
        'CHANGES_ANY_COMMERCIAL_RESULT': 'NO',
        'CHANGES_ANY_COMMERCIAL_RESULT_WHY':
            'AREA_OFICIAL_HA alimenta COMMERCIAL_MAGNITUDE e a lista '
            'WHAT_IS_MISSING. Nenhum portao de v21_comercial.prioridade a le: '
            'os portoes sao semanticos e area nao e portao.',
        'AREA_YEAR_QUESTION': ano,
        'STAMP_APPLIED': False,
    }
    saida = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                         'V115-QA-DO-ISTAT.json')
    json.dump(fora, open(saida, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    print('gravado em %s' % os.path.relpath(saida, ROOT))
    return 0 if geral != 'NO' else 1


if __name__ == '__main__':
    sys.exit(main())
