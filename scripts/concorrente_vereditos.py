#!/usr/bin/env python3
"""
OS VEREDICTOS DO COMPETITOR FORESIGHT — um por capacidade, nunca um só.

    python3 scripts/concorrente_vereditos.py

Este script não coleta e não deriva número novo: ele LÊ o que as rodadas
mediram e escreve o veredicto de cada capacidade, com o par semântico que
impede a leitura errada.

POR QUE UM VEREDICTO POR CAPACIDADE
  "COMPETITOR FORESIGHT funciona" é uma frase sem denominador. Quatro coisas
  diferentes foram testadas, e elas terminaram em quatro estados diferentes.
  Um veredicto único apagaria três.

OS QUATRO PARES SEMÂNTICOS QUE ESTA RODADA CORRIGIU
  Cada um é uma frase verdadeira que estava a um passo de virar uma falsa.

  1 · PRECEDÊNCIA HISTÓRICA  ≠  ANTECEDÊNCIA OPERACIONAL
      A marca precedeu o registro em 1.087 de 1.652 pares ligados. Com
      mediana de ~4 anos, isso NÃO é aviso prévio útil para decisão: pode
      ser cedo DEMAIS. `OPERATIONAL_EARLY_WARNING_VALUE = NOT_PROVED`.

  2 · ATIVIDADE RECENTE  ≠  VALOR DIÁRIO
      346 depósitos desde 2025 e um a três dias da coleta provam que a
      fonte SE MEXE. Não provam que olhá-la todo dia devolva decisão.
      Uma fotografia não mede cadência. `DAILY_VALUE = NOT_PROVED`.

  3 · ZERO MUDANÇA NO INTERVALO  ≠  REGISTRO ESTÁTICO
      40.092 comparações entre 29/08 e 31/08 deram zero. Dois dias são dois
      dias. `REGULATORY_CHANGE_CADENCE = NOT_PROVED`.

  4 · ROTA REFUTADA  ≠  CAMADA REFUTADA
      O que morreu foi `PATENT_LOOKUP_BY_COMMERCIAL_BRAND_NAME`, em 5 de 5
      casos. `PATENT_WATCH` inteiro NÃO foi testado — busca por titular, por
      substância ativa, por formulação e por família de patente continuam
      sem veredicto. Refutar a camada com o teste de uma rota seria o mesmo
      erro que este piloto passou a rodada inteira evitando.

E UM ERRO DE ESTADO QUE ESTA RODADA CORRIGIU
  A primeira entrega escreveu que META e CREATOR "não existem no
  repositório". **Errado.** O Creator Map está CONGELADO em branch própria
  com handoff canônico; o Meta Competitor corre em missão paralela e já tem
  1.111 anúncios dos mesmos seis concorrentes. O que esta branch pode dizer
  é `NOT_JOINED_IN_THIS_MISSION` — nunca ausência global.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(RAIZ, 'data', 'samples')
SAIDA = os.path.join(S, 'COMPETITOR-EAME-VEREDITOS.json')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def ler(nome):
    with open(os.path.join(S, nome), encoding='utf-8') as f:
        return json.load(f)


def tabela_por_pais(par):
    """A tabela comparável do §11 — com denominador em cada linha."""
    linhas = {}
    for pais, b in par['POR_PAIS'].items():
        if b.get('ESTADO_DA_MEDICAO') != 'MEASURED':
            linhas[pais] = {'ESTADO': 'NOT_MEASURED',
                            'EXACT_REASON': b.get('EXACT_REASON'),
                            'NAO_SIGNIFICA': b.get('NAO_SIGNIFICA')}
            continue
        a = b['ANTECEDENCIA']
        linhas[pais] = {
            'ESTADO': 'MEASURED',
            'FONTE': b['FONTE_DO_REGISTRO'],
            'VERSAO_DA_FONTE': b['VERSAO_DA_FONTE'],
            'TRADEMARKS': b['TRADEMARKS_TESTADAS'],
            'LOCAL_REGISTRATIONS': b['LOCAL_REGISTRATIONS'],
            'LOCAL_REGISTRATIONS_EM_VIGOR': b['LOCAL_REGISTRATIONS_EM_VIGOR'],
            'LINKED_CHAINS': b['LINKED_CHAINS'],
            'TM_BEFORE_REG': a['TM_BEFORE_REG'],
            'REG_BEFORE_TM': a['REG_BEFORE_TM'],
            'UNLINKED': b['UNLINKED'],
            'FALSE_LINKS_REJECTED': b['FALSE_LINKS_REJECTED'],
            'PARTIAL': b['PARTIAL'],
            'RUIDO_CASADOR_FROUXO': b['RUIDO_DO_CASADOR_FROUXO']['COM_TITULAR_ERRADO'],
            'SUBCONTAGEM_POR_ANTECESSOR': b['SUBCONTAGEM_POR_ANTECESSOR'],
            'TAXA_DE_LIGACAO': b['TAXA_DE_LIGACAO'],
        }
    return linhas


def main():
    par = ler('COMPETITOR-EAME-PARIDADE.json')
    ev = ler('COMPETITOR-EVENTS.json')
    ip = ler('COMPETITOR-IP-TMVIEW.json')
    reg = ler('COMPETITOR-REGULATORY-EVENTS.json')
    pat = ler('COMPETITOR-PATENT-DEMOTE.json')
    aud = ler('COMPETITOR-THREE-LAYER-AUDIT.json')

    paises = tabela_por_pais(par)
    medidos = [p for p, v in paises.items() if v['ESTADO'] == 'MEASURED']
    soma = {k: sum(paises[p][k] for p in medidos) for k in
            ('LINKED_CHAINS', 'TM_BEFORE_REG', 'REG_BEFORE_TM',
             'FALSE_LINKS_REJECTED', 'UNLINKED')}
    ligados = soma['TM_BEFORE_REG'] + soma['REG_BEFORE_TM']
    lead = ev['LEAD_DAYS']

    # depósitos recentes — o que sustenta PROMISING, e só isso
    recentes = 0
    for offs in ip['POR_CONCORRENTE'].values():
        for v in offs.values():
            if v.get('ESTADO') != 'OK':
                continue
            for m in v['MARCAS']:
                if m['APPLICATION_DATE'] != 'NOT_KNOWN' \
                        and m['APPLICATION_DATE'] >= '2025-01-01':
                    recentes += 1

    art = {
        'SOURCE_ID': 'COMPETITOR-EAME-VEREDITOS',
        'source': 'derivação sobre os artefatos medidos desta missão',
        'SOURCE_LOCATION': 'interno — derivado',
        'FACT_LOCATION': 'ES · IT · FR',
        'CAMADA_DO_PILOTO': 'VEREDICTO POR CAPACIDADE',
        'captured_at': ev['captured_at'],

        # ── §11 · a tabela comparável ────────────────────────────────────
        'COUNTRY_COVERAGE': {
            'REGRA': ('todo número vem com denominador. Os totais de registro '
                      'NÃO são comparáveis entre países: ES publica o conjunto '
                      'corrente, IT guarda o revogado desde 1970, FR publica '
                      'autorizado + retirado.'),
            'POR_PAIS': paises,
            'SOMA_DOS_MEDIDOS': soma,
            'NOT_MEASURED': [p for p, v in paises.items()
                             if v['ESTADO'] != 'MEASURED'],
        },

        # ── §12 · um veredicto por capacidade ────────────────────────────
        'CAPABILITIES': {
            'A_TRADEMARK_CHANGE_WATCH': {
                'VEREDICTO': 'PROMISING',
                'O_QUE_ESTA_PROVADO': (
                    f'a rota TMview responde e devolve depósito recente: '
                    f'{recentes} depósitos desde 2025-01-01 nos quatro '
                    'escritórios, um deles a três dias da coleta.'),
                'O_QUE_NAO_ESTA_PROVADO': {
                    'DAILY_VALUE': 'NOT_PROVED',
                    'POR_QUE': ('existe UMA captura. Uma fotografia não mede '
                                'cadência. Provar valor diário exige duas '
                                'capturas separadas por dias e a contagem do '
                                'que apareceu entre elas.'),
                },
                'RECENT_TRADEMARK_ACTIVITY_EXISTS': 'YES',
                'TRADEMARK_WATCH_AS_CHANGE_SOURCE': 'PROMISING',
                'COMO_PROMOVER': ('segunda captura do TMview em D+7 e D+30, '
                                  'com o mesmo portão de filtro, e a contagem '
                                  'de depósitos novos por janela.'),
            },

            'B_TRADEMARK_TO_LOCAL_REGISTRATION_LINK': {
                'VEREDICTO': 'PROVED',
                'ONDE': 'ES · IT · FR — os três medidos com a MESMA régua',
                'EVIDENCIA': (
                    f"{soma['LINKED_CHAINS']} cadeias ligadas "
                    f"({paises['ES']['LINKED_CHAINS']} ES · "
                    f"{paises['IT']['LINKED_CHAINS']} IT · "
                    f"{paises['FR']['LINKED_CHAINS']} FR), com "
                    f"{soma['FALSE_LINKS_REJECTED']} recusas publicadas por "
                    'titular divergente.'),
                'A_REGRA': ('duas concordâncias obrigatórias: nome normalizado E '
                            'grupo do titular. Nome sozinho nunca promove.'),
                'REGRESSAO_DE_OURO': ('URBOLE — marca da SYNGENTA, registro '
                                      'espanhol 24157 da ADAMA. '
                                      'SAME_NAME != SAME_COMPETITOR_PRODUCT.'),
                'LIMITE': (f"{soma['UNLINKED']} marcas ficaram NO_LINK nos três "
                           'países somados. A maioria esmagadora das marcas de um '
                           'concorrente NÃO tem registro local de mesmo nome.'),
            },

            'C_COMPETITOR_TIMELINE': {
                'VEREDICTO': 'PARTIAL',
                'O_QUE_EXISTE': (
                    f"{ev['TIMELINES']['TOTAL']} cadeias com DUAS camadas "
                    '(IP + REGULATORY), datadas e rastreáveis à fonte.'),
                'O_QUE_FALTA': ('as outras três camadas da cadeia de cinco. '
                                'NOT_JOINED_IN_THIS_MISSION — ver JOIN_READINESS.'),
                'CADEIAS_COM_5_DE_5': 0,
                'HISTORICAL_PRECEDENCE_OBSERVED': {
                    'TM_BEFORE_REG': soma['TM_BEFORE_REG'],
                    'REG_BEFORE_TM': soma['REG_BEFORE_TM'],
                    'DE': ligados,
                    'LEITURA': (f"a marca precedeu o registro em "
                                f"{soma['TM_BEFORE_REG']} de {ligados} pares "
                                'ligados, nos três países independentes. É '
                                'PRECEDÊNCIA HISTÓRICA OBSERVADA.'),
                },
                'OPERATIONAL_EARLY_WARNING_VALUE': {
                    'ESTADO': 'NOT_PROVED',
                    'POR_QUE': (
                        f"a mediana defensável é {lead['MEDIANA_DIAS_DEFENSAVEIS']} "
                        f"dias (~{round(lead['MEDIANA_DIAS_DEFENSAVEIS'] / 365, 1)} "
                        'anos), com amplitude bruta de '
                        f"{lead['AMPLITUDE_BRUTA_DIAS']}. Um sinal que chega anos "
                        'antes pode estar cedo DEMAIS para decisão operacional. '
                        'Precedência não é aviso prévio útil enquanto ninguém '
                        'medir a janela em que a decisão é tomada.'),
                    'PROIBIDO_DIZER': ['a marca prevê o registro',
                                       'a marca dá 6 anos de antecedência útil',
                                       'temos aviso prévio de lançamento'],
                },
            },

            'D_PATENT_WATCH': {
                'PATENT_LAYER': 'DEMOTED / NOT_USED',
                'PATENT_BRAND_LINKAGE_ROUTE': 'REFUTED_FOR_PILOT',
                'O_QUE_FOI_REFUTADO': (
                    'apenas PATENT_LOOKUP_BY_COMMERCIAL_BRAND_NAME: buscar o nome '
                    'comercial da marca no texto completo do Espacenet. 0 de 5 '
                    'casos recuperaram o titular correto.'),
                'PATENT_WATCH_COMO_UM_TODO': 'NOT_TESTED',
                'ROTAS_QUE_NAO_FORAM_TESTADAS': [
                    'APPLICANT_BASED_PATENT_WATCH — busca por titular normalizado',
                    'TECHNOLOGY_WATCH — por classificação técnica',
                    'ACTIVE_INGREDIENT_WATCH — por substância ativa',
                    'FORMULATION_WATCH — por formulação',
                    'ASSIGNEE_FAMILY_WATCH — por família de patente do titular',
                ],
                'PROIBIDO_ESCREVER': 'PATENT_WATCH = REFUTED',
                'MOTIVO': ('refutar a camada com o teste de UMA rota é o mesmo '
                           'erro que este piloto passou a rodada evitando.'),
                'EVIDENCIA': pat['SOURCE_ID'],
                'DECISAO': 'parar aqui. Patente não entra e não volta nesta missão.',
            },
        },

        # ── §4 · o par semântico do regulatório ──────────────────────────
        'REGULATORY_WATCH': {
            'REGULATORY_CHANGE_IN_THIS_INTERVAL': '0 OBSERVED',
            'INTERVALO': ('29/08/2026 → 31/08/2026 · '
                          f"{reg['PORTAO_DE_VERSAO']['COMPARACOES_CAMPO_A_CAMPO']} "
                          'comparações campo a campo'),
            'REGULATORY_CHANGE_CADENCE': 'NOT_PROVED',
            'POR_QUE': ('dois dias são dois dias. Uma janela curta sem mudança '
                        'não mede a frequência com que o registro se mexe.'),
            'PROIBIDO_DIZER': ['o registro não se mexe no dia a dia',
                               'o registro é estático',
                               'o ROPF não tem sinal'],
            'PARIDADE': reg['PARIDADE_EAME']['CHANGE_EVENTS_POR_PAIS'],
        },

        # ── §5 · o estado real das outras camadas ────────────────────────
        'JOIN_READINESS': {
            'REGRA': ('esta branch declara o que ELA juntou. O estado das outras '
                      'missões é lido dos handoffs delas, não afirmado por aqui.'),
            'CREATOR': {
                'CREATOR_DATA_AVAILABLE_IN_THIS_SNAPSHOT': 'NO',
                'ESTADO_REAL_DA_CAPACIDADE': 'FROZEN_WAITING_FOR_INTELLIGENCE',
                'ONDE': 'branch claude/eame-agro-creators-map-77c4ld · '
                        'docs/creators/HANDOFF-INTELLIGENCE-CREATOR-MAP-EAME.md',
                'CHAVE_DE_JUNCAO_QUE_ELE_DECLARA': 'BRAND × RELATION_TYPE',
                'CHAVE_QUE_ESTA_CAMADA_OFERECE': 'BRAND (evento_concorrente.brand)',
                'PRONTO_PARA_O_REFRESH': 'SIM — as duas pontas declaram BRAND',
                'PROIBIDO_DIZER': 'não existe creator no repositório',
            },
            'META': {
                'META_DATA_AVAILABLE_IN_THIS_SNAPSHOT': 'NO',
                'ESTADO_REAL_DA_CAPACIDADE': 'EM CONSTRUÇÃO, missão paralela',
                'ONDE': 'branch claude/eame-meta-competitor · '
                        'data/samples/META-EAME/',
                'O_QUE_ELA_JA_TEM': ('1.111 anúncios observados dos MESMOS seis '
                                     'concorrentes, em ES/IT/FR, com 145 produtos '
                                     'de marca provados'),
                'MEDIDO_NESTA_RODADA': {
                    'ATENCAO': ('a primeira medição desta junção casava APENAS o '
                                'nome do produto anunciado com o nome da marca, e '
                                'anunciou 36 cadeias. Era a falha que URBOLE '
                                'existe para impedir. O número foi AUDITADO com '
                                'concordância de titular nas três pontas.'),
                    'REGRA_AUDITADA': ('company da Meta == grupo do titular da '
                                       'marca == grupo do titular do registro '
                                       'local, e o mesmo país nas três'),
                    # ── unidade TUPLA ──────────────────────────────────
                    'THREE_LAYER_CANDIDATE_UNIT': aud['UNIVERSO'][
                        'THREE_LAYER_CANDIDATE_UNIT'],
                    'THREE_LAYER_CANDIDATES_TOTAL': aud['UNIVERSO'][
                        'THREE_LAYER_CANDIDATES_TOTAL'],
                    'THREE_LAYER_CHAIN_PROVED_TUPLES': aud['RESULTADO'][
                        'THREE_LAYER_CHAIN_PROVED_TUPLES'],
                    'THREE_LAYER_CHAIN_REJECTED_TUPLES': aud['RESULTADO'][
                        'THREE_LAYER_CHAIN_REJECTED_TUPLES'],
                    'THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES': aud['RESULTADO'][
                        'THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES'],
                    'CONSERVACAO_TUPLAS': aud['RESULTADO']['CONSERVACAO_TUPLAS'],
                    # ── unidade PRODUTO, conta separada ────────────────
                    'META_CANONICAL_SOURCE_COMMIT': aud['FONTE_EXTERNA'][
                        'META_CANONICAL_SOURCE_COMMIT'],
                    'META_RAW_PRODUCT_NAMES': aud['RESULTADO'][
                        'POR_UNIDADE_PRODUTO']['NOMES_CRUS_NA_META'],
                    'META_PRODUCTS_TOTAL': aud['RESULTADO'][
                        'POR_UNIDADE_PRODUTO']['META_PRODUCTS_TOTAL'],
                    'META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN': aud['RESULTADO'][
                        'POR_UNIDADE_PRODUTO'][
                        'META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN'],
                    'META_PRODUCTS_WITHOUT_PROVED_THREE_LAYER_CHAIN': aud[
                        'RESULTADO']['POR_UNIDADE_PRODUTO'][
                        'META_PRODUCTS_WITHOUT_PROVED_THREE_LAYER_CHAIN'],
                    'CONSERVACAO_PRODUTOS': aud['RESULTADO'][
                        'POR_UNIDADE_PRODUTO']['CONSERVACAO_PRODUTOS'],
                    'THREE_LAYER_UNIT_RECONCILED': 'YES',
                    'NAO_SUBTRAIR_ENTRE_UNIDADES': aud['RESULTADO'][
                        'POR_UNIDADE_PRODUTO']['NAO_SUBTRAIR_ENTRE_UNIDADES'],
                    'DEFEITO_ENCONTRADO_NA_CONFERENCIA_DE_UNIDADE': aud[
                        'UNIVERSO']['DESCARTADAS_ANTES_DE_CANDIDATAR'][
                        'EFEITO_DO_DEFEITO'],
                    'LINHAGEM': aud['LINHAGEM'],
                    'OLD_RESULT': 'SUPERSEDED_BY_CORRECTED_META_INPUT',
                    'O_QUE_MUDOU_DO_RESULTADO_ANTERIOR': (
                        'a Meta congelou uma base corrigida — 1.340 cartões e 151 '
                        'nomes crus, contra 1.111 e 145. Só o PONTEIRO da fonte '
                        'mudou (4cee050 → acfd987); o casador é o mesmo do commit '
                        'congelado do Foresight. O resultado anterior não é '
                        'inválido: foi medido corretamente sobre o input daquele '
                        'momento.'),
                    'URBOLE_GUARD': aud['URBOLE_GUARD']['URBOLE_GUARD'],
                    'URBOLE_GUARD_EXERCIDO': aud['URBOLE_GUARD'][
                        'EXERCIDO_POR_MUTACAO']['PEGOU'],
                    'COLISOES_DE_NOME': aud['COLISOES_DE_NOME_ENTRE_AS_PROVADAS'],
                    'PRELIMINARY_CROSS_BRANCH_JOIN': 'PROVED',
                    'FINAL_REFRESH_INPUT': 'NO',
                    'POR_QUE_NAO_E_FINAL': ('a Meta é fonte externa a esta missão e '
                                            'seu handoff ainda NÃO foi congelado '
                                            'pelo coordenador. Entrada final de '
                                            'refresh só depois do handoff canônico '
                                            'da Meta.'),
                    'COMO_FOI_MEDIDO': (
                        'git show somente-leitura sobre '
                        f"{aud['FONTE_EXTERNA']['BRANCH']} @ "
                        f"{aud['FONTE_EXTERNA']['META_CANONICAL_SOURCE_COMMIT'][:9]}. Nenhum merge, "
                        'nenhum checkout, nenhuma alteração de índice.'),
                },
                'PROIBIDO_DIZER': 'não existe Meta no repositório',
            },
            'PRODUCT_CATALOG': {
                'CATALOG_DATA_AVAILABLE_IN_THIS_SNAPSHOT': 'NO',
                'O_QUE_EXISTE_NAS_FOUNDATIONS': (
                    'catálogos ADAMA de ES, IT e FR, em branches próprias '
                    '(claude/adama-es-local-browser, adama-it-local-catalog, '
                    'adama-fr-local-catalog). São catálogos DA ADAMA, não dos '
                    'concorrentes.'),
                'CATALOGO_DE_CONCORRENTE': 'NOT_COLLECTED em nenhuma branch conhecida',
                'PROIBIDO_DIZER': 'os concorrentes não publicam catálogo',
            },
        },

        # ── as duas métricas de falso link, reconciliadas ────────────────
        'FALSE_LINK_METRICS': {
            'REGRA': ('duas métricas com nome próprio. Nenhuma substitui a outra: '
                      'elas medem estágios diferentes do matcher, sobre universos '
                      'que não se tocam.'),
            'POR_PAIS': {
                pais: b['FALSE_LINK_METRICS']
                for pais, b in par['POR_PAIS'].items()
                if b.get('ESTADO_DA_MEDICAO') == 'MEASURED'
            },
            'RECONCILIACAO_ES': {
                'OLD_151_METRIC_NAME': 'LOOSE_CANDIDATE_LINKS_REJECTED',
                'OLD_151_DENOMINATOR': 441,
                'OLD_151_UNIVERSO': '5.266 marcas SEM nome exato no registro',
                'OLD_151_ESTAGIO': 'CONTRAFACTUAL — nunca gerou link',
                'NEW_9_METRIC_NAME': 'STRICT_MATCH_FALSE_LINKS_REJECTED',
                'NEW_9_DENOMINATOR': 242,
                'NEW_9_UNIVERSO': '242 marcas COM nome exato no registro',
                'NEW_9_ESTAGIO': 'PRODUÇÃO — é o casador que gera os links',
                'INTERSECAO_DOS_UNIVERSOS': 0,
                'UMA_SUBSTITUIU_A_OUTRA': False,
                'HOUVE_MUDANCA_METODOLOGICA': False,
                'VEREDICTO': ('são métricas DIFERENTES, medidas sobre conjuntos '
                              'disjuntos, e ambas permanecem. O 151 mede o dano '
                              'que a frouxidão causaria; o 9 mede o que a régua '
                              'recusou tendo formado o candidato.'),
                'ES_REGRESSION_PRESERVED': 'YES',
            },
        },

        # ── §13 · o que já pode entrar na convergência ───────────────────
        'CONVERGENCE_READINESS': {
            'REGRA': ('as duas camadas entram como FATOS SEPARADOS. Não é preciso '
                      'ter o link marca→registro para usar qualquer uma delas.'),
            'COMPETITOR_BRAND_EVENT_OBSERVED': {
                'ESTADO': 'PRONTO',
                'EVENTOS': ev['EVENTOS']['POR_TIPO'].get('TRADEMARK_APPLICATION', 0)
                + ev['EVENTOS']['POR_TIPO'].get('TRADEMARK_REGISTRATION', 0),
                'CHAVES': ['COMPETITOR', 'COUNTRY', 'BRAND', 'EFFECTIVE_DATE'],
            },
            'COMPETITOR_LOCAL_REGISTRATION_OBSERVED': {
                'ESTADO': 'PRONTO',
                'EVENTOS': sum(ev['EVENTOS']['POR_TIPO'].get(t, 0) for t in
                               ('LOCAL_REGISTRATION', 'EXPIRY',
                                'SELLING_OFF_DEADLINE', 'REGISTRATION_MODIFIED')),
                'CHAVES': ['COMPETITOR', 'COUNTRY', 'REGULATORY_ID',
                           'EFFECTIVE_DATE'],
            },
            'TIMELINE_QUANDO_HA_LINK': {
                'ESTADO': 'PRONTO onde o link é PROVED',
                'CADEIAS': ev['TIMELINES']['TOTAL'],
            },
            'O_QUE_AINDA_NAO_LIGA': {
                'CROP_E_ISSUE': ('nenhum dos três registros nacionais traz cultura '
                                 'e alvo neste dataset. Sem eles, a camada de '
                                 'concorrente NÃO entra no eixo cultura×praga que '
                                 'é o coração da convergência.'),
            },
            'NAO_CRIAR_SCORE': 'nenhum número desta camada é ranking ou ameaça.',
        },
    }

    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(art, f, ensure_ascii=False, indent=2)

    print('COUNTRY COVERAGE')
    for p, v in art['COUNTRY_COVERAGE']['POR_PAIS'].items():
        if v['ESTADO'] != 'MEASURED':
            print(f'  {p}: NOT_MEASURED — {v["EXACT_REASON"]}')
            continue
        print(f"  {p}: {v['TRADEMARKS']:>5} marcas · {v['LOCAL_REGISTRATIONS']:>6} "
              f"registros · {v['LINKED_CHAINS']:>5} ligadas · "
              f"TM_antes {v['TM_BEFORE_REG']:>4} / REG_antes {v['REG_BEFORE_TM']:>4} · "
              f"{v['FALSE_LINKS_REJECTED']:>3} recusadas")
    a = art['CAPABILITIES']['C_COMPETITOR_TIMELINE']
    del a
    j = art['JOIN_READINESS']['META']['MEDIDO_NESTA_RODADA']
    print(f"\nRED TEAM DA JUNCAO META")
    print(f"  TUPLAS  : {j['THREE_LAYER_CANDIDATES_TOTAL']} candidatas = "
          f"{j['THREE_LAYER_CHAIN_PROVED_TUPLES']} PROVED + "
          f"{j['THREE_LAYER_CHAIN_REJECTED_TUPLES']} REJECTED + "
          f"{j['THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES']} NOT_KNOWN")
    print(f"  PRODUTOS: {j['META_PRODUCTS_TOTAL']} = "
          f"{j['META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN']} com cadeia + "
          f"{j['META_PRODUCTS_WITHOUT_PROVED_THREE_LAYER_CHAIN']} sem")
    print(f"  URBOLE_GUARD={j['URBOLE_GUARD']} · "
          f"UNIT_RECONCILED={j['THREE_LAYER_UNIT_RECONCILED']}")
    print('\nCAPABILITIES')
    for k, v in art['CAPABILITIES'].items():
        ver = v.get('VEREDICTO') or v.get('PATENT_LAYER')
        print(f'  {k}: {ver}')
    print('\ngravado:', SAIDA)


if __name__ == '__main__':
    main()
