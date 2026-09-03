#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTEMUNHA UNIVERSAL · TODA origem atravessa a trilha, ou só a que já sabíamos?

    python3 scripts/v21_testemunha_universal.py

A testemunha anterior (`v21_testemunha_de_ingestao.py`) provou UMA porta e UMA
família: um boletim fitossanitário entrando por `CURRENT_FIELD_SIGNALS`. Prova
boa, e insuficiente para a pergunta desta missão, que é outra:

    TODO material novo, INDEPENDENTEMENTE DA ORIGEM, passa pela inteligência
    antes de poder alterar uma oportunidade publicável?

    UMA PORTA PROVADA NÃO É UMA TRILHA UNIVERSAL.
    PROVAR UMA E CONCLUIR TODAS É EXATAMENTE O ERRO QUE ESTE REPOSITÓRIO CAÇA.

AS PORTAS, E POR QUE SÃO ESTAS
-------------------------------
Não são portas novas. São as que a cadeia real já lê, e cada uma está
versionada no git:

    D1  build/ITALY-REALITY-HANDOFF-V2/CANONICAL-INTELLIGENCE.json
        as DEZ famílias por onde entra toda coleta nova
    D2  research/italy-lastmile/NEW-REAL-SOURCES.json
        o cadastro de fonte nova

As dez famílias de D1 cobrem as origens que a missão lista:

    boletim / fitossanitário / PDF   CURRENT_FIELD_SIGNALS
    API / mercado                    MARKET_OBSERVATIONS
    estatística oficial              CROP_ECONOMIC_WEIGHT
    clima                            AGROMET_CONDITIONS
    regulatório                      REGULATORY_FUTURE
    comunicação de concorrente       COMPETITOR_PUBLIC_SIGNALS
    voz · produtor · vídeo · áudio   PUBLIC_VOICES
    evento                           FUTURE_EVENTS
    catálogo ADAMA                   COMMERCIAL_CATALOG
    contexto de herbicida            HERBICIDE_CURRENT_CONTEXT

O QUE SE MEDE POR FIXTURE
--------------------------
Para cada registro injetado, a travessia inteira, etapa a etapa:

    entrou no pacote? · normalizou? · classificou? · passou na régua? ·
    extraiu relação? · a catraca lhe deu estado? · a oportunidade mudou? ·
    o briefing existe?

⚠️ ENTRAR NO ACERVO E ALTERAR UMA OPORTUNIDADE SÃO DUAS COISAS. A missão
permite a primeira sem inteligência; proíbe a segunda. Uma fixture que entra e
NÃO muda oportunidade nenhuma não reprova nada — ela CONFIRMA a catraca.

E A LIMPEZA, QUE É PARTE DA PROVA
----------------------------------
As portas são restauradas com `git checkout --`, a cadeia roda de novo, e o
`BUILD_ID` tem de voltar exatamente ao de antes. Se não voltar, a passagem
deixou resíduo — e resíduo silencioso é a doença que a cadeia inteira existe
para evitar.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D1_REL = 'build/ITALY-REALITY-HANDOFF-V2/CANONICAL-INTELLIGENCE.json'
D2_REL = 'research/italy-lastmile/NEW-REAL-SOURCES.json'
D1 = os.path.join(ROOT, D1_REL)
D2 = os.path.join(ROOT, D2_REL)
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
CADEIA = os.path.join(ROOT, 'scripts', 'v21_cadeia.sh')
SAIDA = os.path.join(ROOT, 'data', 'samples', 'AUDITORIA-SOMBRA',
                     'TRILHA-UNIVERSAL-TESTEMUNHA.json')

MARCA = 'IT-FIXTURE-TRILHA'
URL = 'https://fixture.invalid/trilha-universal/%s'
AVISO = ('FIXTURE — nenhuma fonte disse isto. Registro de teste, injetado e '
         'removido pela testemunha da trilha universal.')


def _fix(familia, **kw):
    r = {'FAMILIA': familia,
         'CANONICAL_RECORD_ID': '%s-%s' % (MARCA, familia),
         'QA_STATUS': 'QA_PASS',
         'source_name': 'FIXTURE DE TESTE — NAO E FONTE REAL',
         'source_url': URL % familia.lower().replace('_', '-'),
         'publication_date': '2026-09-01',
         'observation_class': 'CURRENT',
         'citacao_literal': AVISO}
    r.update(kw)
    return r


# ── AS ONZE FIXTURES ────────────────────────────────────────────────────────
#
# A de CURRENT_FIELD_SIGNALS é deliberadamente VENDÁVEL: videira × botrite na
# Emilia-Romagna, com a oração que manda intervir. É a única desenhada para
# poder mexer numa oportunidade, e existe para que a travessia mostre o tamanho
# do que a ingestão automática faz. As outras dez são de origens que NÃO fundam
# par cultura × alvo, e servem para medir o outro lado da mesma pergunta:
# material entra no acervo sem virar oportunidade, e isso é o correto.
FIXTURES = [
    _fix('CURRENT_FIELD_SIGNALS',
         tipo='BOLETIM FITOSSANITARIO OFICIAL · VITE · FIXTURE DE TRILHA',
         crop='VITE', region='Emilia-Romagna', geographic_scope='REGIONALE',
         o_que='Vite/botrite: intervir em pre-colheita com Fenhexamid.'),
    _fix('MARKET_OBSERVATIONS', tipo='PRECO', crop='FRUMENTO TENERO',
         region='Italia', valor='999,99', unidade='EUR por tonelada',
         o_que='Cotacao de fixture para o trigo mole, sem praca real.'),
    _fix('CROP_ECONOMIC_WEIGHT', tipo='AREA_PRODUCAO_REGIONAL', crop='mais',
         region='Emilia-Romagna', valor='1,00 mil ha', unidade='mil hectares',
         o_que='Area de fixture para o milho, sem medicao real.'),
    _fix('AGROMET_CONDITIONS', tipo='SECA_INDICE_OFICIAL', region='Italia',
         o_que='Indice de seca de fixture, sem leitura real.'),
    _fix('REGULATORY_FUTURE', tipo='DATA_EUROPEIA', region='Europa',
         o_que='Data regulatoria de fixture, sem ato real.'),
    _fix('COMPETITOR_PUBLIC_SIGNALS', tipo='ANUNCIO_DE_PRODUTO',
         crop='VITE', region='Italia',
         o_que='Comunicacao de concorrente de fixture sobre videira.'),
    _fix('PUBLIC_VOICES', tipo='VOZ_DE_PRODUTOR', crop='OLIVE',
         region='Toscana',
         o_que='Voz de fixture de um produtor sobre a oliveira.'),
    _fix('FUTURE_EVENTS', tipo='EVENTO_FUTURO_CONFIRMADO', region='Italia',
         periodo='outubro de 2026',
         o_que='Evento de fixture, sem realizacao real.'),
    _fix('COMMERCIAL_CATALOG', tipo='CATALOG_CENSUS', region='Italia',
         valor='0', unidade='fichas de produto',
         o_que='Censo de catalogo de fixture, sem leitura real.'),
    _fix('HERBICIDE_CURRENT_CONTEXT', tipo='JANELA_CORRENTE',
         crop='Cereali autunno-vernini', region='Emilia-Romagna',
         o_que='Contexto de herbicida de fixture, sem janela real.'),
]

FONTE_FIXTURE = {
    'NOME': 'FIXTURE DE TESTE — NAO E FONTE REAL',
    'URL': URL % 'fonte-nova',
    'O_QUE_PUBLICA': 'nada: e uma fixture da testemunha da trilha universal.',
    'ESTADO_DE_ACESSO': 'NAO_SE_APLICA',
    'EVIDENCIA_DO_ESTADO': AVISO,
    'EXIGE_ROTA_ITALIANA': False,
}

# As etapas da trilha, na ordem em que a missão as escreveu.
TRILHA = ('ENTROU_NO_PACOTE', 'IDENTITY_PROVENANCE', 'NORMALIZATION',
          'CLASSIFICATION', 'MISSION_RULER', 'RELATION_EXTRACTION',
          'LOCALIZATION', 'CATRACA_DEU_ESTADO', 'CITADA_COMO_EVIDENCIA',
          'MUDOU_OPORTUNIDADE', 'TEM_BRIEFING')

# As famílias que a catraca declara como NÃO ingeridas, com o motivo escrito em
# `v21_catraca.FAMILIA_NAO_INGERIDA`. Uma fixture nelas NÃO entra no pacote, e
# isso é o comportamento declarado — não uma falha desta testemunha. Foi esta
# testemunha que as descobriu; agora elas têm nome, motivo e contador.
DECLARADAS_FORA = ('COMMERCIAL_CATALOG', 'HERBICIDE_CURRENT_CONTEXT')


def _git(*a):
    return subprocess.run(['git', '-C', ROOT] + list(a),
                          capture_output=True, text=True)


def _cadeia():
    r = subprocess.run(['bash', CADEIA], cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def _foto():
    """→ (BUILD_ID, {id da oportunidade: assinatura}, censo da catraca, briefings)."""
    o = json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'), encoding='utf-8'))
    g = json.load(open(os.path.join(ING, 'PUBLICATION-GATE.json'), encoding='utf-8'))
    b = json.load(open(os.path.join(ING, 'OPPORTUNITY-BRIEFINGS.json'), encoding='utf-8'))
    # ⚠️ A ASSINATURA JA FOI ESTREITA DEMAIS E MENTIU. A primeira versao
    # comparava so (prioridade, estado, direcao, EVIDENCE_IDS), e a fixture de
    # CURRENT_FIELD_SIGNALS apareceu como «nao mudou oportunidade nenhuma».
    # Tinha mudado: o motor grava `sin[:8]` em EVIDENCE_IDS — a lista de apoios
    # e CORTADA em oito — e o nono sinal entra na conta (`NUMBERS`) sem entrar
    # na citacao. A medicao dizia NAO porque olhava o campo cortado.
    #
    #     MEDIR PELO CAMPO TRUNCADO E MEDIR O TRUNCAMENTO, NAO O FATO.
    assin = {r['ID']: (r.get('COMMERCIAL_PRIORITY'), r.get('PUBLICATION_STATE'),
                       r.get('NEED_DIRECTION'), r.get('OPPORTUNITY_SCORE'),
                       json.dumps(r.get('NUMBERS') or {}, sort_keys=True),
                       r.get('EVIDENCE_COUNT'),
                       tuple(r.get('EVIDENCE_IDS') or []))
             for r in o['RECORDS']}
    return o['BUILD_ID'], assin, g, {r['OPPORTUNITY_ID']: r for r in b['RECORDS']}


def _indice_do_pacote():
    """{ID canônico: (arquivo, registro)} de tudo o que existe no ingest."""
    ix = {}
    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq.startswith('CANONICAL'):
            continue
        d = json.load(open(os.path.join(ING, arq), encoding='utf-8'))
        for r in (d.get('RECORDS') or []):
            if isinstance(r, dict) and r.get('ID') and r['ID'] not in ix:
                ix[r['ID']] = (arq, r)
    return ix


def _injetar():
    d = json.load(open(D1, encoding='utf-8'))
    d['RECORDS'] = list(d['RECORDS']) + FIXTURES
    d['COUNT'] = len(d['RECORDS'])
    json.dump(d, open(D1, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = json.load(open(D2, encoding='utf-8'))
    f['FONTES'] = list(f.get('FONTES') or []) + [FONTE_FIXTURE]
    json.dump(f, open(D2, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def main():
    sujo = _git('status', '--porcelain', '--', D1_REL, D2_REL).stdout.strip()
    if sujo:
        print('As portas tem alteracao nao commitada. Nao injeto sobre trabalho '
              'de outra pessoa:\n  %s' % sujo, file=sys.stderr)
        return 2

    falhas = []
    print('── 1 · a linha de base ─────────────────────────────────────────────')
    rc, _log = _cadeia()
    if rc != 0:
        print('a cadeia ja falha ANTES da injecao. Nada a medir.', file=sys.stderr)
        return 2
    base_id, base_assin, base_gate, base_brf = _foto()
    print('BUILD_ID %s · %d oportunidades · %d fichas'
          % (base_id, len(base_assin), len(base_brf)))

    print('\n── 2 · a injecao, pelas portas reais ───────────────────────────────')
    _injetar()
    print('%d fixtures em %s' % (len(FIXTURES), D1_REL))
    print('1 fonte em %s' % D2_REL)

    try:
        rc, log = _cadeia()
        if rc != 0:
            falhas.append('a cadeia FALHOU com as fixtures dentro (rc=%d)' % rc)
            print(log[-2500:])
        novo_id, nova_assin, novo_gate, novo_brf = _foto()
        ix = _indice_do_pacote()
        censo = {r['RECORD_ID']: r for r in novo_gate['RECORDS']}

        mudou = {k for k in set(base_assin) | set(nova_assin)
                 if base_assin.get(k) != nova_assin.get(k)}
        detalhe_mudanca = [
            {'OPPORTUNITY_ID': k,
             'ANTES': base_assin.get(k), 'DEPOIS': nova_assin.get(k)}
            for k in sorted(mudou)]
        print('BUILD_ID %s · %d oportunidades · %d mudaram/nasceram'
              % (novo_id, len(nova_assin), len(mudou)))
        if novo_id == base_id:
            falhas.append('o BUILD_ID nao mudou com 11 registros novos dentro: '
                          'a porta nao esta sendo lida')

        print('\n── 3 · a travessia, fixture a fixture ──────────────────────────────')
        linhas = []
        for f in FIXTURES:
            rid = f['CANONICAL_RECORD_ID']
            arq, rec = ix.get(rid, (None, None))
            etapas = {e: 'NAO' for e in TRILHA}
            etapas['ENTROU_NO_PACOTE'] = 'SIM' if rec else 'NAO'
            if rec:
                c = censo.get(rid)
                # Ausente do censo de incompletos = passou todas as etapas.
                for e in ('IDENTITY_PROVENANCE', 'NORMALIZATION', 'CLASSIFICATION',
                          'MISSION_RULER', 'RELATION_EXTRACTION', 'LOCALIZATION'):
                    etapas[e] = (c['STAGES'].get(e) if c else 'PASSED')
                etapas['CATRACA_DEU_ESTADO'] = 'SIM'
            citadas = sorted(k for k in nova_assin
                             if rid in (nova_assin[k] or ((),) * 7)[6])
            etapas['CITADA_COMO_EVIDENCIA'] = ','.join(citadas) if citadas else 'NAO'
            tocadas = sorted(mudou)
            etapas['MUDOU_OPORTUNIDADE'] = ','.join(tocadas) if tocadas else 'NAO'
            etapas['TEM_BRIEFING'] = ('SIM' if all(t in novo_brf for t in citadas)
                                      else 'NAO') if citadas else 'NAO_SE_APLICA'
            linhas.append({'FAMILIA': f['FAMILIA'], 'RECORD_ID': rid,
                           'COLECAO': arq, 'ETAPAS': etapas})
            print('  %-28s entrou=%-4s%s catraca=%-4s citada=%s'
                  % (f['FAMILIA'], etapas['ENTROU_NO_PACOTE'],
                     ' (declarada FORA)' if f['FAMILIA'] in DECLARADAS_FORA
                     else '                 ',
                     etapas['CATRACA_DEU_ESTADO'],
                     etapas['CITADA_COMO_EVIDENCIA'][:44]))
            if not rec and f['FAMILIA'] not in DECLARADAS_FORA:
                falhas.append('%s: a fixture NAO entrou no pacote' % f['FAMILIA'])
            elif rec and f['FAMILIA'] in DECLARADAS_FORA:
                falhas.append('%s: a familia esta declarada FORA e a fixture '
                              'entrou — a declaracao envelheceu' % f['FAMILIA'])
            elif rec and etapas['CLASSIFICATION'] != 'PASSED':
                falhas.append('%s: entrou sem classificacao (%s)'
                              % (f['FAMILIA'], etapas['CLASSIFICATION']))

        # A fonte nova, pela segunda porta.
        fontes = json.load(open(os.path.join(ING, 'SOURCES.json'), encoding='utf-8'))
        fonte_entrou = any(FONTE_FIXTURE['URL'] in (r.get('SOURCE_URLS') or [])
                           or r.get('URL') == FONTE_FIXTURE['URL']
                           for r in fontes['RECORDS'])
        print('  %-28s entrou=%s' % ('D2 · FONTE NOVA',
                                     'SIM' if fonte_entrou else 'NAO'))
        if not fonte_entrou:
            falhas.append('D2: a fonte nova NAO entrou no cadastro de fontes')

        # ── 4 · a catraca segurou o que tinha de segurar? ────────────────────
        print('\n── 4 · a catraca sobre as fixtures ─────────────────────────────────')
        publicaveis = [k for k, v in nova_assin.items() if v[1] == 'PUBLISHABLE']
        com_fixture = [k for k in publicaveis
                       if any(e.startswith(MARCA) for e in nova_assin[k][6])]
        quarentena = [rid for rid in censo
                      if censo[rid]['MATERIAL_STATE'] == 'QUARANTINED']
        print('  publicaveis: %d · publicaveis apoiados em fixture: %d'
              % (len(publicaveis), len(com_fixture)))
        print('  material em quarentena no pacote: %d' % len(quarentena))
        if novo_gate['VIOLATION_COUNT']:
            falhas.append('a catraca acusou %d violacao(oes) com as fixtures '
                          'dentro' % novo_gate['VIOLATION_COUNT'])

        # ── 5 · o backfill: a régua nova valeu para o acervo INTEIRO? ────────
        print('\n── 5 · o backfill, na mesma execucao ───────────────────────────────')
        antigos = [k for k in nova_assin if k in base_assin]
        sem_estado = [k for k in antigos if nova_assin[k][1] is None]
        sem_ficha = [k for k in antigos if k not in novo_brf]
        print('  oportunidades preexistentes: %d · sem PUBLICATION_STATE: %d · '
              'sem ficha: %d' % (len(antigos), len(sem_estado), len(sem_ficha)))
        if sem_estado or sem_ficha:
            falhas.append('a regua nova NAO alcancou todo o acervo antigo')

    finally:
        print('\n── 6 · a restauracao ───────────────────────────────────────────────')
        _git('checkout', '--', D1_REL, D2_REL)
        rc, _log = _cadeia()
        fim_id, fim_assin, _g, _b = _foto()
        print('BUILD_ID %s (base %s) · %s' % (fim_id, base_id,
                                              'IGUAL' if fim_id == base_id else 'DIFERENTE'))
        if fim_id != base_id:
            falhas.append('o BUILD_ID nao voltou: a passagem deixou residuo')
        if fim_assin != base_assin:
            falhas.append('as oportunidades nao voltaram ao estado de antes')

    # ⚠️ DOIS VEREDITOS, PORQUE SÃO DUAS PERGUNTAS.
    #
    #   UNIVERSAL_GATE            algo consegue alterar uma oportunidade
    #                             publicável SEM passar pela inteligência?
    #   UNIVERSAL_TRAIL_COVERAGE  toda origem que chega na porta chega até a
    #                             inteligência?
    #
    # A primeira é sobre VAZAMENTO e a resposta é medida. A segunda é sobre
    # COBERTURA, e ela não está inteira: duas das dez famílias da porta não
    # entram, e uma delas — HERBICIDE_CURRENT_CONTEXT, 16 registros reais — é
    # material de campo, não papel de trabalho.
    #
    #     UM PORTÃO QUE NÃO VAZA E UMA TRILHA QUE NÃO COBRE TUDO SÃO DOIS
    #     FATOS DIFERENTES, E RESPONDER UM PELO OUTRO É O ERRO DE SEMPRE.
    fora = [f for f in DECLARADAS_FORA]
    veredito = {
        'AUTOMATIC_NEW_INGEST': 'YES' if not falhas else 'NO',
        'UNIVERSAL_GATE': 'YES' if not falhas else 'NO',
        'UNIVERSAL_TRAIL_COVERAGE': 'PARTIAL' if fora else 'FULL',
        'FAMILIAS_DA_PORTA_QUE_NAO_ENTRAM': fora,
        'BACKFILL': 'YES' if not falhas else 'NO',
        'OPORTUNIDADES_QUE_MUDARAM': detalhe_mudanca,
        'BASELINE_BUILD_ID': base_id,
        'BUILD_ID_COM_FIXTURES': novo_id,
        'BUILD_ID_RESTAURADO': fim_id,
        'PORTAS': [D1_REL, D2_REL],
        'FIXTURES': len(FIXTURES) + 1,
        'TRAVESSIA': linhas,
        'FALHAS': falhas,
        'LEI': 'entrar no acervo e alterar uma oportunidade publicavel sao duas '
               'coisas. A missao permite a primeira sem inteligencia e proibe a '
               'segunda. Uma fixture que entra e nao muda oportunidade nenhuma '
               'CONFIRMA a catraca — nao a reprova.',
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(veredito, open(SAIDA, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('\n── VEREDITO ────────────────────────────────────────────────────────')
    for k in ('AUTOMATIC_NEW_INGEST', 'UNIVERSAL_GATE',
              'UNIVERSAL_TRAIL_COVERAGE', 'BACKFILL'):
        print('  %-22s %s' % (k, veredito[k]))
    print('  gravado: %s' % SAIDA)
    if falhas:
        print('\n  FALHAS:')
        for f in falhas:
            print('   · %s' % f)
        return 1
    print('\n  FALHAS: nenhuma')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
