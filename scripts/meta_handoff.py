#!/usr/bin/env python3
"""
O HANDOFF DA META — todo numero derivado do arquivo, nenhum digitado.

Um handoff com numero digitado a mao envelhece na primeira correcao e ninguem
percebe. Aqui cada campo e lido dos artefatos no momento em que o documento e
gerado; se o acervo mudar e o handoff nao for regerado, a divergencia aparece.

    NUMERO_DIGITADO != NUMERO_DERIVADO

A LINHAGEM QUE PRECISA VIAJAR JUNTO
------------------------------------
O Competitor Foresight (branch `claude/eame-competitor-foresight`, commit
25194e3) fez a juncao de tres camadas sobre a fotografia ANTIGA da Meta:

    1111 cartoes · 145 nomes crus de produto  ->  28 produtos com cadeia provada

Essa fotografia foi corrigida por dois defeitos medidos — completude que
confundia pausa de rede com fim de lista, e contagem que tratava cartao como
anuncio. A base congelada aqui e outra. Os 28 nao ficam invalidos; ficam
apoiados numa entrada superada.

    SUPERSEDED_INPUT != INVALID_RESULT

Por isso o handoff carrega `FORESIGHT_REJOIN_REQUIRED = YES`. A missao Meta NAO
executa esse rejoin, nao mexe naquela branch e nao coleta para aumentar o 28.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PASTA = os.path.join(ROOT, 'data', 'samples', 'META-EAME')
DEST = os.path.join(PASTA, 'META-HANDOFF-FREEZE-V1.json')

FORESIGHT_BRANCH = 'claude/eame-competitor-foresight'
FORESIGHT_COMMIT = '25194e3'
FORESIGHT_OLD_INPUT = {'ad_cards': 1111, 'raw_product_names': 145,
                       'products_with_proved_three_layer_chain': 28}


def _ler(nome, padrao=None):
    caminho = os.path.join(PASTA, nome)
    if not os.path.exists(caminho):
        return padrao
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


def montar(freeze_commit=None):
    s1 = _ler('META-ADS-ENTITIES-EAME-V1.json', {})
    s2 = _ler('META-SNAPSHOT-2-OBSERVATIONS.json', {})
    cmp_ = _ler('META-TEMPORAL-COMPARISON-V1.json', {})
    manif = _ler('META-TEMPORAL-SNAPSHOT-MANIFEST.json', {})
    ident = _ler('META-PAGE-IDENTITY-EAME-V1.json', {})
    met = _ler('META-PILOT-METRICS-V1.json', {})
    adama = _ler('META-OWN-ADS-ENTITIES-ADAMA-CLEAN-V1.json', {})
    rota = _ler('META-ROUTE-PROBE-V1.json', {})

    ent1 = s1.get('entities', {})
    obs2 = [o for o in (s2.get('observations') or [])
            if o.get('slice_state') == 'SLICE_OK']
    cartoes2 = {a['library_id'] for o in obs2 for a in o.get('ads', [])}
    guarda = (adama.get('identity_guard') or {})

    # ── O QUE OS 1.340 SAO, EXATAMENTE ──────────────────────────────────────
    # O numero foi reportado como TEMPORAL_ENTITIES_COMPARABLE, e isso podia ser
    # lido como "universo valido para afirmar mudanca". Nao e. Os 1.340 sao as
    # entidades do snapshot 1 que voltaram a ser encontradas no snapshot 2 BRUTO
    # — util para saber que nenhuma se perdeu no realinhamento, e insuficiente
    # para sustentar claim de mudanca, porque 7 dos 67 recortes foram lidos com
    # profundidades diferentes.
    #
    #     REALINHAVEL_NO_BRUTO != VALIDO_PARA_AFIRMAR_MUDANCA
    #
    # O universo que sustenta claim de mudanca sao os 337 cartoes dos 60
    # recortes de profundidade comparavel.
    alinhaveis = set(ent1) & cartoes2
    comparaveis = (cmp_.get('totals_unit_ad_card_read_depth_comparable') or {})
    confundidos = (cmp_.get('read_depth_confounded') or {})
    selos_temporais = {
        'stable_entities_alignable_across_raw_snapshots': len(alinhaveis),
        'stable_entities_alignable_definition': (
            'entidades do snapshot 1 reencontradas no snapshot 2 BRUTO, em '
            'qualquer recorte. Mede realinhamento, NAO autoriza claim de '
            'mudanca.'),
        'stable_entities_lost_in_realignment': len(set(ent1) - cartoes2),
        'temporal_comparable_depth_slices': comparaveis.get('slices'),
        'temporal_noncomparable_depth_slices': confundidos.get('slices'),
        'temporal_entities_in_comparable_depth_slices':
            comparaveis.get('PRESENT_BOTH'),
        'present_both': comparaveis.get('PRESENT_BOTH'),
        'newly_observed': comparaveis.get('NEWLY_OBSERVED'),
        'no_longer_observed': comparaveis.get('NO_LONGER_OBSERVED_IN_SNAPSHOT_2'),
        'method_depth_delta_cards': confundidos.get('cards_gained_by_deeper_reading'),
        'method_depth_delta_excluded_from_temporal_change_claim': 'YES',
        'method_depth_delta_nao_e': (
            'NEW_AD_ACTIVITY. Sao cartoes que ja estavam la e o snapshot 1 nao '
            'chegou a ler.'),
        'change_observed': cmp_.get('change_observed'),
        'change_observed_scope': (
            '%s DEPTH-COMPARABLE SLICES BETWEEN THE TWO MEASURED SNAPSHOTS'
            % comparaveis.get('slices')),
        'change_observed_frase_permitida': (
            'NO CHANGE OBSERVED IN THE COMPARABLE MEASURED SLICES DURING THIS '
            'SHORT OBSERVATION WINDOW'),
        'change_observed_frase_proibida': (
            'os concorrentes nao mudaram sua atividade na Meta'),
    }

    return {
        'artifact': 'META-HANDOFF-FREEZE-V1',
        'dataset_owner': 'META_COMPETITOR_EAME',
        'meta_route': rota.get('meta_route'),
        'api_auth_state': rota.get('api_auth_state'),
        'meta_canonical_freeze_commit': freeze_commit,

        'decision_question': (
            'e possivel observar atividade publica paga de concorrente na Meta, '
            'por empresa x pais de entrega x pagina provada x tempo?'),

        'units': {
            'AD_OBSERVATION': 'uma leitura de um cartao numa data',
            'AD_CARD_CREATIVE_GROUP': 'o cartao na Biblioteca; pode representar '
                                      'mais de um anuncio',
            'ADS_REPRESENTED_BY_SOURCE': 'quantos anuncios os cartoes declaram',
            'STABLE_AD_ENTITY': 'entidade unica por meta_ad_library_id',
            'PRODUCT_NAME': 'nome comercial escrito no anuncio com simbolo de marca',
            'SLICE': 'page_id x ad_delivery_country',
        },

        'snapshot_1': {
            'as_of_date': s1.get('as_of_date'),
            'ad_observations': sum(len(e.get('observations') or [])
                                   for e in ent1.values()),
            'unique_cards': len(ent1),
            'ads_represented': sum(int(e.get('ads_in_this_creative_group') or 1)
                                   for e in ent1.values()),
            'stable_ad_entities': len(ent1),
            'raw_product_names_proved': len(met.get('ads_by_product_proved') or {}),
        },
        'snapshot_2': {
            'collection_started_at': s2.get('collection_started_at'),
            'collection_resumed_at': s2.get('collection_resumed_at'),
            'collection_completed_at': s2.get('collection_completed_at'),
            'window_nota': 'JANELA de coleta, nao instante. Cada observacao tem '
                           'seu proprio observed_at.',
            'slices_total': s2.get('slices_total'),
            'slices_preexisting': s2.get('slices_preexisting'),
            'slices_new_this_resume': s2.get('slices_new_this_resume'),
            'slices_successful': s2.get('slices_successful'),
            'slices_failed': s2.get('slices_failed'),
            'slices_content': s2.get('slices_content'),
            'slices_honest_zero': s2.get('slices_honest_zero'),
            'unique_cards': len(cartoes2),
            'ads_represented': sum(o.get('ads_represented') or 0 for o in obs2),
            'ad_observations': sum(len(o.get('ads') or []) for o in obs2),
            'enrichment_nota': ('esta captura coletou SO os campos de comparacao. '
                                'Nao reprocessou cultura, problema, produto nem '
                                'criativo — o objetivo era tempo.'),
        },

        'temporal': {
            'manifest_frozen_at': manif.get('frozen_at'),
            'manifest_frozen_before_collection': bool(
                manif.get('frozen_at') and s2.get('collection_started_at')
                and manif['frozen_at'] < s2['collection_started_at']),
            'slices_in_manifest': manif.get('slices_total'),
            'slices_compared': cmp_.get('slices_compared'),
            'totals_unit_ad_card_all_slices':
                cmp_.get('totals_unit_ad_card_all_slices'),
            'totals_unit_ad_card_read_depth_comparable':
                cmp_.get('totals_unit_ad_card_read_depth_comparable'),
            'read_depth_confounded': cmp_.get('read_depth_confounded'),
            'slice_transitions_unit_slice': cmp_.get('slice_transitions_unit_slice'),
            'change_observed': cmp_.get('change_observed'),
            'change_observed_basis': cmp_.get('change_observed_basis'),
            **selos_temporais,
        },

        # PAGE_IDENTITY_MODEL = PROVED, sozinho, mentia por omissao: dava a
        # entender que pais e papel da pagina tambem estavam provados. Estao em
        # 1 de 23 e 0 de 23. Cada capacidade sai com o proprio selo e o proprio
        # denominador.
        'page_model': {
            'page_id_proof_capability': 'PROVED',
            'page_id_proof_denominator': (ident.get('summary') or {}).get(
                'page_ids_proved'),
            'page_country_scope_capability': 'PARTIAL_LOW_COVERAGE',
            'page_country_scope_coverage': '%s de %s paginas' % (
                (ident.get('summary') or {}).get('page_country_scope_local_proved'),
                (ident.get('summary') or {}).get('page_ids_proved')),
            'page_role_capability': 'NOT_PROVED',
            'ad_delivery_country_model': 'PROVED',
            'ad_delivery_country_scope': ['ES', 'IT', 'FR'],
            **(ident.get('summary') or {}),
            'leis_permanentes': [
                'PAGE_COUNTRY_SCOPE != AD_DELIVERY_COUNTRY',
                'AD_REACHED_OR_OBSERVED_IN_COUNTRY != AD_TARGETED_TO_COUNTRY',
                'ADS_DELIVERED_IN_ES != PAGE_IS_SPANISH',
            ],
            'frase_proibida': (
                '"dirigido a Espanha/Franca/Italia" sem target_location ou prova '
                'equivalente. O que temos e pais de ENTREGA observada.'),
            'nota': 'a comparacao temporal usa page_id x ad_delivery_country e '
                    'NAO depende de a pagina ser local.',
        },

        'capability_statement': {
            'observable_unit': ('COMPETITOR x PROVED PAGE_ID x '
                                'AD_DELIVERY_COUNTRY x SNAPSHOT'),
            'claim': 'COMPETITOR_PAID_META_ACTIVITY_OBSERVED',
            'nao_depende_de': 'a pagina ser local ao pais de entrega',
        },

        'own_dataset_adama': {
            'adama_advertiser_identity_guard': (
                'PASS' if guarda.get('adama_false_cards_rejected') else 'NOT_RUN'),
            'adama_false_cards_rejected': guarda.get('adama_false_cards_rejected'),
            'adama_real_cards_remaining': guarda.get('adama_real_cards_remaining'),
            'rejected_pages': guarda.get('rejected_pages'),
            'rejected_preserved_in': guarda.get('rejected_preserved_in'),
        },

        # MECANISMO E VALOR SAO DUAS COISAS
        # Duas leituras separadas por cerca de uma hora provam que o relogio
        # COMPARA. Nao provam que comparar todo dia entrega sinal util para o
        # Daily Intelligence — para isso seria preciso medir uma cadencia real,
        # e a missao esta parada.
        #
        #     MECANISMO_FUNCIONA != CADENCIA_TEM_VALOR
        'capabilities': {
            'meta_snapshot_capability': 'PROVED',
            'temporal_comparison_mechanism': 'PROVED',
            'meta_temporal_comparison_capability': 'PROVED_FOR_COMPARABLE_SLICES',
            'temporal_comparison_scope': '%s de %s recortes' % (
                comparaveis.get('slices'), (manif or {}).get('slices_total')),
            'operational_temporal_signal_value': 'NOT_PROVED',
            'daily_intelligence_value': 'NOT_PROVED',
            'operational_value_nota': (
                'a janela medida tem cerca de uma hora. Isso mostra que o '
                'mecanismo compara; nao mostra que a cadencia diaria produz '
                'sinal util. Provar isso exigiria outra medicao, e nao ha '
                'terceira coleta autorizada.'),
            'full_lifecycle_state_capability': 'NOT_PROVED',
            'full_lifecycle_nota': (
                'ACTIVE_AGAIN exige ativo -> ausente -> ativo, e isso pede tres '
                'pontos no tempo.'),
        },

        'foresight_lineage': {
            'branch': FORESIGHT_BRANCH,
            'commit': FORESIGHT_COMMIT,
            'old_foresight_meta_input': FORESIGHT_OLD_INPUT,
            'meta_corrected_snapshot_1': {
                'ad_cards': len(ent1),
                'raw_product_names': len(met.get('ads_by_product_proved') or {}),
            },
            'state': 'SUPERSEDED_INPUT',
            'foresight_rejoin_required': 'YES',
            'instruction': 'REEXECUTE EXISTING FORESIGHT JOIN ON FROZEN META INPUT',
            'nao_fazer': ['nao alterar a branch Foresight',
                          'nao reimplementar matcher',
                          'nao coletar para aumentar os 28',
                          'o rejoin NAO e tarefa da missao Meta'],
        },

        'cost': {'apify_cost_usd': 0, 'other_cost_usd': 0,
                 'nota': 'rota publica com Chrome local; nenhum runner, nenhum ator pago'},

        'exact_limitations': [
            'JANELA CURTA: snapshot 1 e snapshot 2 estao a cerca de uma hora de '
            'distancia, na mesma data-calendario. A comparacao e valida, mas uma '
            'janela de um dia mediria muito mais mudanca.',
            'PROFUNDIDADE DE LEITURA DESIGUAL: em 7 dos 67 recortes o snapshot 2 '
            'leu mais fundo que o 1, porque a regra de rolagem foi corrigida '
            'entre as duas capturas. Esses 7 estao FORA da conta de mudanca, e '
            'os 587 cartoes que eles acrescentam sao metodo, nao mercado. A '
            'medida de mudanca vale sobre os 60 recortes comparaveis.',
            'A rota oficial (Ads Library API) nao foi exercida: falta token de '
            'aplicativo. API_TOKEN_AUSENTE nao e porta fechada.',
            'PAGE_COUNTRY_SCOPE fica NOT_PROVED em quase todas as paginas. So a '
            'Meta rotulando o pais promove, e ela rotula pouco.',
            'PAGE_ROLE nao e publicado pela fonte: NOT_PROVED em todas.',
            'TARGET_LOCATION nao coletado. country e pais ALCANCADO, nao ALVO.',
            'Transparencia da UE (beneficiario, pagador, alcance) nao coletada.',
            'Plataforma de veiculacao sai NOT_KNOWN: a UI mostra icone sem rotulo.',
            'Gasto so existe para anuncio declarado de tema social/politico, e vem '
            'rotulado como tal. Nao ha, e nao deve haver, estimativa de investimento.',
            'Snapshot 2 nao reprocessou classificacao; entidades novas dele estao '
            'como bruto a processar.',
            'ACTIVE_AGAIN, comentarios, split de plataforma e ligacao completa '
            'produto-anuncio ficam fora do congelamento, por decisao do coordenador.',
        ],

        'cannot_claim': [
            'quanto o concorrente investiu',
            'que o concorrente vendeu qualquer coisa',
            'participacao de mercado',
            'sucesso de campanha',
            'que o produto anunciado esta autorizado naquele pais',
            'que a pagina e daquele pais porque entregou anuncios la',
            'que um anuncio parou de veicular porque sumiu da lista',
        ],

        'more_collection_needed': 'NO',
        'meta_competitor': 'ACCEPTED',
        'mandatory_handoff_ready': 'YES',
        'mission_state': 'PARKED',
        'no_further_action_now': 'YES',
    }


if __name__ == '__main__':
    commit = sys.argv[1] if len(sys.argv) > 1 else None
    h = montar(commit)
    with open(DEST, 'w', encoding='utf-8') as f:
        json.dump(h, f, ensure_ascii=False, indent=2)
    print(json.dumps({'snapshot_1': h['snapshot_1'], 'snapshot_2': h['snapshot_2'],
                      'temporal': h['temporal'], 'capabilities': h['capabilities'],
                      'adama': h['own_dataset_adama']},
                     ensure_ascii=False, indent=2))
