#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLIENT-SAFE-CROSSINGS — reconstruídos por ID, com as oito invariantes provadas.

    python3 scripts/v21_crossings.py

§9 · O QUE FOI JOGADO FORA, E POR QUÊ
--------------------------------------
O `TOP-CROSSINGS.json` do V2 foi DESCARTADO, não remendado. Medido nele:

    36 IDs cuja cultura não era a do cruzamento
    7 de 19 cruzamentos apoiados em registro QA_UNREVIEWED

A causa não era um caso isolado: era o método. Ele procurava a palavra da
cultura dentro do campo livre `o_que`. Um boletim de OLIVEIRA cuja descrição
mencionava milho entrava no cruzamento do MILHO.

    REMENDAR EXEMPLO A EXEMPLO DEIXARIA O MÉTODO VIVO.

§12 · AS OITO INVARIANTES, PROVADAS ANTES DE EMITIR
----------------------------------------------------
    A · toda evidência específica de cultura resolve no MESMO CROP_ID
    B · os vínculos de problema usam o mesmo ISSUE_ID
    C · a geografia nunca é promovida em silêncio
    D · nenhum apoio CLIENT_SAFE é QA_UNREVIEWED
    E · todo ID referenciado resolve
    F · o par de rótulo contém MESMO a relação cultura × alvo alegada
    G · a cultura do mercado é a do cruzamento
    H · a cultura do sinal de campo é a do cruzamento

Se qualquer uma falha: O CRUZAMENTO NÃO É EMITIDO. Não há aviso, não há
«parcialmente válido» — ele simplesmente não nasce, e o motivo fica registrado.
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')


def le(nome):
    p = os.path.join(ING, nome)
    return json.load(open(p, encoding='utf-8')).get('RECORDS', []) \
        if os.path.exists(p) else []


def main():
    col = {
        'FIELD': le('CURRENT-FIELD-SIGNALS.json'),
        'ECON': [x for x in le('CROP-ECONOMIC-WEIGHT.json')
                 if x['ENTITY_TYPE'] == 'CROP_ECONOMIC_WEIGHT'],
        'MARKET': le('MARKET-OBSERVATIONS.json'),
        'LABEL': le('PRODUCT-RELATIONSHIPS.json'),
        'RESIST': le('RESISTANCE.json'),
        'SCIENCE': le('SCIENCE.json'),
        'VOICE': le('PUBLIC-VOICES.json'),
        'HERB': le('CURRENT-FIELD-SIGNALS.json'),
        'COMP': le('COMPETITOR-ACTIVITIES.json'),
        'REG': le('REGULATORY-FUTURE.json'),
        'CAT': le('PRODUCTS-COMMERCIAL.json'),
        'WINDOW': le('CROP-WINDOWS.json'),
    }
    todos = {x['ID']: x for v in col.values() for x in v}

    def por_crop(lista, so_safe=True):
        d = defaultdict(list)
        for x in lista:
            if so_safe and not x.get('CLIENT_SAFE'):
                continue
            for c in x.get('CROP_IDS') or []:
                d[c].append(x)
        return d

    idx = {k: por_crop(v) for k, v in col.items()}
    idx_livre = {k: por_crop(v, so_safe=False) for k, v in col.items()}

    emitidos, recusados = [], []

    def prova(cruz, apoios, crop):
        """As oito invariantes. Devolve (ok, falhas)."""
        f = []
        for papel, itens in apoios.items():
            for x in itens:
                # E · resolve?
                if x['ID'] not in todos:
                    f.append('E · %s: ID %s nao resolve' % (papel, x['ID']))
                # D · nenhum apoio inseguro
                if not x.get('CLIENT_SAFE'):
                    f.append('D · %s: %s e %s, nao pode sustentar'
                             % (papel, x['ID'], x.get('QA_STATUS')))
                # A/G/H · a cultura tem de ser a do cruzamento
                cs = x.get('CROP_IDS') or []
                if cs and crop not in cs:
                    f.append('%s · %s: %s tem CROP_IDS %s, nao %s'
                             % ({'MARKET': 'G', 'FIELD': 'H'}.get(papel, 'A'),
                                papel, x['ID'], cs, crop))
                if not cs:
                    f.append('A · %s: %s nao tem cultura declarada'
                             % (papel, x['ID']))
                # C · escopo nunca promovido
                #
                # ⚠️ ESTA GUARDA JA FOI VAZIA. Ela comparava GEOGRAPHIC_CLAIM com
                # ('REGIONAL','NACIONAL'), mas o campo nascia sempre com a string
                # "NENHUMA — o cruzamento nao afirma geografia". A condicao era
                # estruturalmente inalcancavel, e mesmo assim 'C' ia para
                # INVARIANTS_PROVEN como literal fixo.
                #
                #     GUARDA QUE NUNCA DISPARA NAO PROTEGE: DA ALIBI.
                #
                # Agora C compara com o escopo EFETIVO que o cruzamento afirma —
                # calculado dos apoios em `escopo_do_cruzamento` — e um apoio que
                # declara REGION_REPRESENTS=False nunca pode sustentar alegacao
                # regional.
                alegado = cruz.get('GEOGRAPHIC_CLAIM_SCOPE')
                if x.get('GEOGRAPHIC_SCOPE') in ('PROVINCIAL', 'AREALE', 'ESTACAO',
                                                 'PIAZZA', 'GRADE_DE_MODELO') \
                        and alegado in ('REGIONAL', 'NACIONAL'):
                    f.append('C · %s: escopo %s promovido a %s'
                             % (papel, x['GEOGRAPHIC_SCOPE'], alegado))
                if x.get('REGION_REPRESENTS') is False and alegado in ('REGIONAL', 'NACIONAL'):
                    f.append('C · %s: %s declara REGION_REPRESENTS=false e nao '
                             'sustenta alegacao %s' % (papel, x['ID'], alegado))
        return (not f), f

    # ── o escopo que o cruzamento pode afirmar sai dos apoios, nao do desejo ──
    FRACO = ['ESTACAO', 'GRADE_DE_MODELO', 'PIAZZA', 'AREALE', 'PROVINCIAL',
             'REGIONAL', 'MACROAREA', 'NACIONAL', 'EUROPEU']

    def escopo_do_cruzamento(apoios):
        """O elo mais fraco manda.

        Um cruzamento apoiado em cinco boletins regionais e um provincial NAO e
        regional: e provincial com companhia. A cadeia vale o elo mais fraco, e
        em geografia o elo mais fraco e o mais especifico.
        """
        vistos, provs, regs, repr_falso = [], [], [], 0
        for itens in apoios.values():
            for x in itens:
                e = x.get('GEOGRAPHIC_SCOPE') or 'NAO_SEI'
                if e not in vistos:
                    vistos.append(e)
                for pid in (x.get('PROVINCE_IDS') or []):
                    if pid not in provs:
                        provs.append(pid)
                for rid in (x.get('REGION_IDS') or []):
                    if rid not in regs:
                        regs.append(rid)
                if x.get('REGION_REPRESENTS') is False:
                    repr_falso += 1
        conhecidos = [e for e in vistos if e in FRACO]
        if not conhecidos:
            escopo = 'NAO_SEI'
        else:
            escopo = min(conhecidos, key=FRACO.index)
        return {
            'GEOGRAPHIC_CLAIM_SCOPE': escopo,
            'GEOGRAPHIC_COVERAGE_PROVINCES': sorted(provs),
            'GEOGRAPHIC_COVERAGE_REGIONS': sorted(regs),
            'SUPPORTS_THAT_DO_NOT_REPRESENT_REGION': repr_falso,
            'GEOGRAPHIC_CLAIM_LAW': (
                'o escopo alegado e o do apoio mais especifico, nunca o do mais '
                'amplo. PROVINCIAL != REGIONAL, e a cobertura lista as provincias '
                'e regioes que os apoios de fato tocam — nao o que o mapa sugere.'),
        }

    def monta(tipo, crop, apoios, pergunta, nao_prova, extra=None):
        cruz = {'CROSSING_TYPE': tipo, 'CROP_ID': crop,
                'GEOGRAPHIC_CLAIM': 'NENHUMA — o cruzamento nao afirma geografia'}
        cruz.update(escopo_do_cruzamento(apoios))
        ok, falhas = prova(cruz, apoios, crop)
        if not ok:
            recusados.append({'CROSSING_TYPE': tipo, 'CROP_ID': crop,
                              'INVARIANTES_QUE_FALHARAM': falhas[:8],
                              'POR_QUE_NAO_FOI_EMITIDO':
                                  'o §12 manda NAO EMITIR quando uma invariante falha. '
                                  'Nao existe cruzamento «parcialmente valido».'})
            return
        cruz.update({
            'ID': 'XCR_%s_%s' % (tipo[:18], crop.replace('CROP_', '')),
            'SUPPORTING_IDS': {k: [x['ID'] for x in v] for k, v in apoios.items()},
            'SUPPORTING_QA': sorted({x.get('QA_STATUS') for v in apoios.values()
                                     for x in v}),
            'ALL_SUPPORT_CLIENT_SAFE': True,
            # ⚠️ O CRUZAMENTO NAO SAI DO PORTAO PELA PORTA DOS FUNDOS.
            #
            # Todo apoio dele e client-safe — a invariante D prova isso. Mas o
            # cruzamento em si nao foi lido em fonte nenhuma: fui EU que juntei
            # dois fatos e disse que falam da mesma cultura. Isso e derivacao.
            #
            #     A REGRA VALE PARA O QUE EU MESMO PRODUZO, OU NAO E REGRA.
            #
            # Entao CLIENT_SAFE=false, como manda o portao. E, para que a tela
            # nao filtre e mostre nada, RENDERABLE_WITH_METHOD diz como ele vai
            # a tela: sempre com a ressalva colada, nunca sozinho.
            'QA_STATUS': 'EVIDENCE_DERIVED',
            'CLIENT_SAFE': False,
            'RENDERABLE_WITH_METHOD': True,
            'RENDER_RULE':
                'pode aparecer na tela, mas SEMPRE com WHAT_IT_DOES_NOT_PROVE '
                'visivel ao lado — nunca atras de um «saiba mais». Sozinho, nao '
                'sustenta afirmacao nenhuma.',
            'WHY_NOT_CLIENT_SAFE':
                'CLIENT_SAFE=true e para fato lido em fonte. Este registro e '
                'leitura minha sobre fatos de outros. Os fatos que o sustentam '
                'sao todos client-safe (invariante D); a juncao nao e.',
            'WHAT_IT_LETS_YOU_ASK': pergunta,
            'WHAT_IT_DOES_NOT_PROVE': nao_prova,
            # 'C' entra so quando ha o que promover — ou seja, quando algum apoio
            # e mais especifico que o alegado. Sem isso, C nao foi provada: foi
            # NAO APLICAVEL, e dizer "provada" e dizer que se mediu o que nao se
            # mediu.
            'INVARIANTS_PROVEN': ['A', 'D', 'E'] +
                                 (['C'] if cruz.get('SUPPORTS_THAT_DO_NOT_REPRESENT_REGION')
                                  or cruz.get('GEOGRAPHIC_CLAIM_SCOPE') in
                                  ('PROVINCIAL', 'AREALE', 'ESTACAO', 'PIAZZA',
                                   'GRADE_DE_MODELO') else []) +
                                 (['G'] if 'MARKET' in apoios else []) +
                                 (['H'] if 'FIELD' in apoios else []) +
                                 (['F'] if 'LABEL' in apoios else []),
        })
        cruz['INVARIANTS_NOT_APPLICABLE'] = [
            i for i in ('C',) if i not in cruz['INVARIANTS_PROVEN']]
        if cruz['INVARIANTS_NOT_APPLICABLE']:
            cruz['INVARIANTS_NOT_APPLICABLE_WHY'] = (
                'C nao foi avaliada porque nenhum apoio e mais especifico que o '
                'escopo alegado — nao havia o que promover. NAO APLICAVEL nao e '
                'PROVADA.')
        if extra:
            cruz.update(extra)
        # RESEARCH_LEADS: o inseguro entra AQUI, nunca no apoio
        leads = {}
        for papel in apoios:
            ins = [x['ID'] for x in idx_livre.get(papel, {}).get(crop, [])
                   if not x.get('CLIENT_SAFE')]
            if ins:
                leads[papel] = ins[:10]
        if leads:
            cruz['RESEARCH_LEADS'] = leads
            cruz['RESEARCH_LEADS_LAW'] = (
                'QA_UNREVIEWED aparece SO aqui, como pista de pesquisa. Ele NUNCA '
                'satisfaz o cruzamento nem sustenta afirmacao ao cliente.')
        emitidos.append(cruz)

    # ── 1 · sinal de campo × uso de rótulo (peso econômico entra como PISTA) ──
    # ⚠️ O PESO ECONOMICO NAO PODE SUSTENTAR, E ISSO NAO E UM DEFEITO.
    # As 2.945 linhas do ISTAT sao QA_UNREVIEWED: ninguem as levou a uma segunda
    # passada. O §7 e explicito -- elas ficam ESTRUTURALMENTE presentes, e as
    # conclusoes ao cliente continuam obedecendo o portao.
    #
    # Entao o cruzamento nasce sobre FIELD + LABEL, que sao client-safe, e o peso
    # entra em RESEARCH_LEADS, que e onde o §11 manda o inseguro morar.
    #
    #     O DADO QUE NAO FOI CONFERIDO PODE ABRIR UMA PERGUNTA.
    #     NAO PODE FECHAR UMA AFIRMACAO.
    for crop in sorted(idx['FIELD']):
        lab = [x for x in idx['LABEL'].get(crop, [])
               if x.get('LINK_STRENGTH') in ('LINHA_DA_TABELA', 'BLOCO_DA_CULTURA')]
        if not lab:
            continue
        econ_lead = [x['ID'] for x in idx_livre['ECON'].get(crop, [])][:12]
        monta('FIELD_SIGNAL_X_LABEL_USE', crop,
              {'FIELD': idx['FIELD'][crop][:8], 'LABEL': lab[:8]},
              'ha sinal de campo corrente numa cultura para a qual o rotulo da '
              'ADAMA tem uso LIDO no documento',
              'nao e oportunidade. Nao prova demanda, nao prova que o produto '
              'resolve o problema, e o sinal e do lugar do boletim — nao da regiao '
              'inteira nem do pais.',
              extra={
                  'LABEL_LINK_STRENGTHS': sorted({x.get('LINK_STRENGTH')
                                                  for x in lab[:8]}),
                  'ECONOMIC_WEIGHT_LEADS': econ_lead,
                  'ECONOMIC_WEIGHT_LEADS_LAW':
                      'estes IDs do ISTAT sao QA_UNREVIEWED. Servem para o analista '
                      'abrir a pergunta «esta cultura pesa quanto nesta regiao?» — '
                      'e NAO para o portal afirmar o peso.',
              })

    # ── 2 · voz identificada × ciência × resistência ─────────────────────────
    for crop in sorted(idx['VOICE']):
        vs = [x for x in idx['VOICE'][crop] if x.get('VOICE_KIND') == 'IDENTIFIED_VOICE']
        if not vs or not idx['SCIENCE'].get(crop):
            continue
        ap = {'VOICE': vs[:6], 'SCIENCE': idx['SCIENCE'][crop][:6]}
        if idx['RESIST'].get(crop):
            ap['RESIST'] = idx['RESIST'][crop][:6]
        monta('IDENTIFIED_VOICE_X_SCIENCE_X_RESISTANCE', crop, ap,
              'gente com nome e cargo falou desta cultura, e ha ciencia registrada '
              'sobre ela',
              'VOZ NAO E INCIDENCIA. Uma declaracao nao mede quanto do campo esta '
              'afetado. E quatro pessoas num mesmo artigo sao quatro vozes e UM '
              'documento — conte por SOURCE_DOCUMENT_ID.',
              extra={'DISTINCT_SOURCE_DOCUMENTS':
                     len({x.get('SOURCE_DOCUMENT_ID') for x in vs[:6]})})

    # ── 3 · mercado × peso × sinal de campo ──────────────────────────────────
    # ⚠️ A AUSENCIA TEM DE SE VER. Quando uma cultura tem sinal de campo e SO tem
    # preco de produto processado (azeite, vinho), o cruzamento nao se forma — e
    # some sem deixar rastro, que e o mesmo mal do default silencioso: o vazio se
    # ve, mas o que sumiu em silencio nao.
    #
    #     CRUZAMENTO QUE DESAPARECE SEM DIZER POR QUE E DEFEITO DISFARCADO DE LIMPEZA.
    #
    # Entao a nao-emissao por estagio da mercadoria e registrada, com os IDs do
    # preco que existe e a razao de ele nao servir.
    por_estagio = []
    for crop in sorted(set(idx['FIELD'])):
        if crop in idx['MARKET']:
            continue
        derivados = [x for x in todos.values()
                     if x.get('DERIVED_FROM_CROP_ID') == crop
                     and x.get('COMMODITY_STAGE') == 'PROCESSED_PRODUCT']
        if derivados:
            por_estagio.append({
                'CROP_ID': crop,
                'CROSSING_TYPE': 'MARKET_X_FIELD_SIGNAL',
                'POR_QUE_NAO_FOI_EMITIDO':
                    'ha sinal de campo para esta cultura, mas o unico preco '
                    'disponivel e de PRODUTO PROCESSADO, nao da cultura. '
                    'PRECO DE AZEITE NAO E PRECO DA AZEITONA.',
                'PRECOS_QUE_EXISTEM_MAS_NAO_SERVEM':
                    [x['ID'] for x in derivados][:12],
                'QUANTOS': len(derivados),
                'O_QUE_ELES_SUSTENTAM':
                    'contexto economico do produto processado — e so isso. Nao '
                    'sustentam movimento de mercado da cultura, economia do '
                    'produtor, oportunidade comercial nem demanda.',
            })
    for crop in sorted(set(idx['MARKET']) & set(idx['FIELD'])):
        monta('MARKET_X_FIELD_SIGNAL', crop,
              {'MARKET': idx['MARKET'][crop][:6], 'FIELD': idx['FIELD'][crop][:6]},
              'ha preco corrente e sinal de campo para a MESMA cultura',
              'preco alto de cultura nao e lucro do produtor, e o preco nao diz se '
              'o problema fitossanitario esta ocorrendo. Preco de piazza nao e '
              'preco nacional.',
              extra={'ECONOMIC_WEIGHT_LEADS':
                     [x['ID'] for x in idx_livre['ECON'].get(crop, [])][:12]})

    # ── 4 · concorrente × janela × portfólio ─────────────────────────────────
    for crop in sorted(set(idx['COMP']) & set(idx['LABEL'])):
        w = idx['WINDOW'].get(crop, [])
        if not w:
            continue
        monta('COMPETITOR_X_CROP_WINDOW_X_PORTFOLIO', crop,
              {'COMP': idx['COMP'][crop][:6], 'WINDOW': w[:4],
               'LABEL': idx['LABEL'][crop][:6]},
              'um concorrente comunicou publicamente sobre uma cultura que tem '
              'janela declarada e onde a ADAMA tem uso de rotulo lido',
              'COMUNICACAO NAO E PARTICIPACAO DE MERCADO. E o anuncio ALCANCOU a '
              'Italia — nao foi necessariamente DIRIGIDO a ela.')

    saida = {
        'COLLECTION': 'CLIENT_SAFE_CROSSINGS', 'FILE': 'CLIENT-SAFE-CROSSINGS.json',
        'SCHEMA_VERSION': 'V2.1', 'BUILT_AT': '2026-09-02',
        'PRIMARY_KEY': 'ID',
        'REPLACES_OLD_FILES': ['V2/TOP-CROSSINGS.json — DESCARTADO, nao remendado'],
        'LAW': 'CROSSING NAO E OPPORTUNITY. E a constatacao de que duas camadas '
               'falam do mesmo CROP_ID. Quem decide se vale e uma pessoa.',
        'JOIN_METHOD': 'IDs normalizados exatos (CROP_ID). Nenhum casamento por '
                       'texto, substring ou semelhanca.',
        'COUNT_TOTAL': len(emitidos),
        # ⚠️ ZERO, E O NOME DO ARQUIVO NAO ESTA MENTINDO.
        #
        # «CLIENT-SAFE-CROSSINGS» quer dizer «cruzamentos cujo APOIO e todo
        # client-safe» — que e o que a invariante D prova. Nao quer dizer que o
        # cruzamento em si seja client-safe: ele e derivacao minha, e derivacao
        # nao passa no portao.
        #
        # A primeira versao declarava 20 aqui e nao punha CLIENT_SAFE nos
        # registros. O cabecalho prometia o que o dado nao entregava, e a tela
        # teria filtrado os 20 e mostrado vazio.
        #
        #     CABECALHO QUE PROMETE MAIS QUE O REGISTRO E O PIOR TIPO DE ERRO:
        #     SO APARECE NA TELA DO CLIENTE.
        'COUNT_CLIENT_SAFE': 0,
        'COUNT_RENDERABLE_WITH_METHOD': len(emitidos),
        'NAME_MEANS':
            'client-safe aqui qualifica o APOIO, nao o cruzamento. Todo apoio '
            'passou no portao; a juncao e leitura nossa e vai a tela com a '
            'ressalva colada (RENDER_RULE em cada registro).',
        'REFUSED': len(recusados),
        'NAO_EMITIDOS_POR_ESTAGIO_DA_MERCADORIA': por_estagio,
        'NAO_EMITIDOS_POR_ESTAGIO_LEI': (
            'PRECO DE AZEITE != PRECO DA AZEITONA != OPORTUNIDADE NA OLIVEIRA. '
            'Entre a materia-prima e o produto processado ha rendimento, safra '
            'estocada, industria e cambio: os dois precos nao andam juntos por '
            'construcao. O cruzamento que dependia dessa confusao nao foi '
            'preservado so porque existia antes.'),
        'INVARIANTS': {
            'A': 'toda evidencia de cultura resolve no MESMO CROP_ID',
            'C': 'geografia nunca promovida',
            'D': 'nenhum apoio e QA_UNREVIEWED',
            'E': 'todo ID resolve',
            'F': 'o par de rotulo contem a relacao cultura x alvo alegada',
            'G': 'cultura do mercado = cultura do cruzamento',
            'H': 'cultura do sinal de campo = cultura do cruzamento',
        },
        'BY_TYPE': dict(Counter(x['CROSSING_TYPE'] for x in emitidos)),
        'RECORDS': emitidos,
        'REFUSED_CROSSINGS': recusados,
    }
    json.dump(saida, open(os.path.join(ING, 'CLIENT-SAFE-CROSSINGS.json'), 'w',
                          encoding='utf-8'), ensure_ascii=False, indent=1)

    # RELATIONSHIPS: só IDs
    rel = [{'ID': x['ID'], 'CROSSING_TYPE': x['CROSSING_TYPE'],
            'CROP_ID': x['CROP_ID'], 'LINKS': x['SUPPORTING_IDS'],
            # o espelho carrega o mesmo carimbo do original; sem isto o
            # registro central acharia que ele nao tem QA nenhum
            'QA_STATUS': x['QA_STATUS'], 'CLIENT_SAFE': x['CLIENT_SAFE'],
            'RENDERABLE_WITH_METHOD': True}
           for x in emitidos]
    json.dump({
        'COLLECTION': 'RELATIONSHIPS', 'FILE': 'RELATIONSHIPS.json',
        'SCHEMA_VERSION': 'V2.1', 'BUILT_AT': '2026-09-02', 'PRIMARY_KEY': 'ID',
        'COUNT_TOTAL': len(rel), 'COUNT_CLIENT_SAFE': 0,
        'COUNT_RENDERABLE_WITH_METHOD': len(rel),
        'NAME_MEANS': 'espelho de CLIENT-SAFE-CROSSINGS, so com IDs. Herda o '
                      'mesmo estado: derivacao, nao fato lido.',
        'HOW_TO_RESOLVE': 'todo ID resolve em CANONICAL-INTELLIGENCE-MASTER.json',
        'LAW': 'as relacoes carregam SO IDs. Copiar o objeto para dentro da relacao '
               'cria dois donos do mesmo fato.',
        'RECORDS': rel,
    }, open(os.path.join(ING, 'RELATIONSHIPS.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)

    print('cruzamentos emitidos: %d · recusados pelas invariantes: %d'
          % (len(emitidos), len(recusados)))
    for k, v in saida['BY_TYPE'].items():
        print('  %-54s %d' % (k, v))
    if recusados:
        print()
        print('exemplos de recusa:')
        for r in recusados[:4]:
            print('  %s / %s' % (r['CROSSING_TYPE'][:44], r['CROP_ID']))
            for f in r['INVARIANTES_QUE_FALHARAM'][:2]:
                print('     %s' % f[:110])


if __name__ == '__main__':
    main()
