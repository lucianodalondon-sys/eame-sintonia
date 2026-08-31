#!/usr/bin/env python3
"""
PROVAS EXECUTAVEIS DO ACERVO META — cada teste tenta QUEBRAR uma separacao.

A missao lista onze confusoes que nao podem acontecer. Um teste que so confirma
o caminho feliz nao serve para nenhuma delas: `DUPLICATE_COUNT = 0` e verdade e
por isso mesmo nao prova nada, porque um dedupe que nao faz nada passaria igual.
Entao aqui cada teste ATACA:

  · mando o mesmo anuncio duas vezes — ele vira dois?
  · mando anuncio em tagalo alcancando a Espanha — vira "atividade na Espanha"?
  · dou a uma pagina o nome "Syngenta Espana" — ela vira pagina local sozinha?
  · o resumo, em algum lugar, deixa vazar venda, share, gasto ou registro?
  · um anuncio ATIVO visto pela primeira vez vira anuncio NOVO?
  · um criador que aparece no criativo vira parceria paga?
  · o acervo proprio da ADAMA cai no arquivo do concorrente?

Fail closed: na duvida, o teste reprova.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import meta_navegador as navegador  # noqa: E402
import meta_identidade as identidade  # noqa: E402
import meta_relogio as relogio  # noqa: E402
import meta_leitura as leitura  # noqa: E402
import meta_anunciante as anunciante  # noqa: E402
import meta_coleta as coleta  # noqa: E402
import meta_convergencia as convergencia  # noqa: E402
import meta_piloto as piloto  # noqa: E402
import meta_temporal as temporal  # noqa: E402

PASTA = os.path.join(ROOT, 'data', 'samples', 'META-EAME')

PROIBIDAS = ('sales', 'venda', 'market_share', 'share_of_voice', 'spend_estimate',
             'competitor_pressure_score', 'media_intensity_score',
             'product_available', 'local_registration_proved')


def anuncio(lid, **extra):
    base = {
        'meta_ad_library_id': lid,
        'active_status': 'ACTIVE',
        'country_reached': 'ES',
        'creative_text': 'texto',
        'creative_text_hash': 'h1',
        'start_date': '2026-07-01',
        'as_of_date': '2026-08-30T10:00:00+00:00',
        'collection_completeness': 'COMPLETE_MATCHES_SOURCE_COUNT',
    }
    base.update(extra)
    return base


class AdIdNaoDuplica(unittest.TestCase):
    """MESMO AD_ID EM DUAS COLETAS = UMA ENTIDADE, DUAS OBSERVACOES."""

    def test_mesma_coleta_duas_vezes_nao_cria_duas_entidades(self):
        ent, _ = relogio.fundir({}, [anuncio('111'), anuncio('111')])
        self.assertEqual(len(ent), 1)

    def test_coletas_de_dias_diferentes_somam_observacao_nao_entidade(self):
        ent, _ = relogio.fundir({}, [anuncio('111')])
        ent2, _ = relogio.fundir(ent, [anuncio('111', as_of_date='2026-08-31T10:00:00+00:00')])
        self.assertEqual(len(ent2), 1)
        self.assertEqual(len(ent2['111']['observations']), 2)
        self.assertEqual(ent2['111']['first_observed'], '2026-08-30T10:00:00+00:00')
        self.assertEqual(ent2['111']['last_observed'], '2026-08-31T10:00:00+00:00')

    def test_anuncio_sem_library_id_e_recusado_e_nao_ganha_chave_inventada(self):
        ent, _ = relogio.fundir({}, [anuncio(None), anuncio('')])
        self.assertEqual(ent, {})


class AtivoNaoENovo(unittest.TestCase):
    """ACTIVE_AD != NEW_AD, e NEW_AD_OBSERVED != NEW_AD_BY_START_DATE."""

    def test_primeira_vez_no_acervo_nao_e_novidade_no_mundo(self):
        ent, ev = relogio.fundir({}, [anuncio('222')])
        self.assertTrue(any(e['event'] == relogio.NEW_AD_OBSERVED for e in ev))
        por_inicio = relogio.novos_por_data_de_inicio(ev, ent, None)
        self.assertEqual(por_inicio['estado'], relogio.BASELINE_ONLY)
        self.assertEqual(por_inicio['eventos'], [])

    def test_anuncio_antigo_visto_hoje_nao_vira_novo(self):
        ent, ev = relogio.fundir({}, [anuncio('333', start_date='2025-01-01')])
        por_inicio = relogio.novos_por_data_de_inicio(ev, ent, '2026-08-01')
        self.assertEqual(por_inicio['eventos'], [],
                         'anuncio iniciado em 2025 nao pode contar como novo em 2026')

    def test_so_e_novo_no_mundo_se_a_fonte_diz_que_comecou_depois(self):
        ent, ev = relogio.fundir({}, [anuncio('444', start_date='2026-08-20')])
        por_inicio = relogio.novos_por_data_de_inicio(ev, ent, '2026-08-01')
        self.assertEqual(len(por_inicio['eventos']), 1)
        self.assertEqual(por_inicio['eventos'][0]['event'], relogio.NEW_AD_BY_START_DATE)


class SumirNaoEParar(unittest.TestCase):
    """AD_STOPPED so com listagem completa nas duas pontas."""

    def test_lista_truncada_nao_vira_anuncio_parado(self):
        ent, _ = relogio.fundir({}, [anuncio('555', collection_completeness='SHORT_OF_SOURCE_COUNT')])
        _, ev = relogio.fundir(ent, [anuncio('999', collection_completeness='SHORT_OF_SOURCE_COUNT')])
        eventos = [e['event'] for e in ev if e['meta_ad_library_id'] == '555']
        self.assertIn(relogio.AD_ABSENT_UNEXPLAINED, eventos)
        self.assertNotIn(relogio.AD_STOPPED_OBSERVED, eventos)

    def test_com_as_duas_pontas_completas_o_evento_pode_ser_afirmado(self):
        ent, _ = relogio.fundir({}, [anuncio('666')])
        _, ev = relogio.fundir(ent, [anuncio('777')])
        eventos = [e['event'] for e in ev if e['meta_ad_library_id'] == '666']
        self.assertIn(relogio.AD_STOPPED_OBSERVED, eventos)


class CompletudeVemDaFonte(unittest.TestCase):
    """A regra antiga ("parou de crescer") leu 29 cartoes numa pagina que a
    fonte declarava com 230 e chamou aquilo de completa. Com os dois lados
    marcados assim, o relogio teria emitido 160 "parou de veicular" falsos."""

    def test_leitura_muito_abaixo_do_declarado_nao_e_completa(self):
        c = navegador.completude(29, '230')
        self.assertEqual(c['state'], navegador.AQUEM_DA_FONTE)
        self.assertEqual(c['source_count'], 230)
        self.assertLess(c['ratio'], 0.2)

    def test_leitura_que_bate_com_o_declarado_e_completa(self):
        self.assertEqual(navegador.completude(79, '79')['state'],
                         navegador.COMPLETA_BATE_COM_A_FONTE)

    def test_tolerancia_aceita_o_til_da_fonte_mas_nao_metade(self):
        self.assertEqual(navegador.completude(96, '100')['state'],
                         navegador.COMPLETA_BATE_COM_A_FONTE)
        self.assertEqual(navegador.completude(50, '100')['state'],
                         navegador.AQUEM_DA_FONTE)

    def test_zero_provado_pela_fonte_nao_se_confunde_com_zero_por_falta_de_leitura(self):
        provado = navegador.completude(0, None, sem_resultados=True)
        naolido = navegador.completude(0, None, sem_resultados=False)
        self.assertEqual(provado['state'], navegador.ZERO_DECLARADO)
        self.assertEqual(naolido['state'], navegador.FONTE_NAO_DECLARA)
        self.assertNotEqual(provado['state'], naolido['state'])

    def test_texto_de_zero_com_cartoes_lidos_nao_vira_zero_provado(self):
        # se a pagina diz "sem resultados" mas eu li cartoes, algo esta errado:
        # o estado forte nao pode sair so pelo texto.
        self.assertNotEqual(
            navegador.completude(5, '5', sem_resultados=True)['state'],
            navegador.ZERO_DECLARADO)

    def test_sem_denominador_da_fonte_nao_se_afirma_completude(self):
        c = navegador.completude(40, None)
        self.assertEqual(c['state'], navegador.FONTE_NAO_DECLARA)
        self.assertNotEqual(c['state'], navegador.COMPLETA_BATE_COM_A_FONTE)

    def test_o_separador_de_milhar_da_fonte_e_lido(self):
        self.assertEqual(navegador.completude(1, '1,100')['source_count'], 1100)

    def test_cartao_nao_e_anuncio_e_a_conta_fecha_com_a_fonte(self):
        # medido na pagina Syngenta global, ES: ~15 declarados, 13 cartoes,
        # dois deles com 2 anuncios cada -> 11 + 4 = 15
        cartoes = ([{'ads_neste_cartao': 1}] * 11) + ([{'ads_neste_cartao': 2}] * 2)
        self.assertEqual(len(cartoes), 13)
        self.assertEqual(navegador.anuncios_em(cartoes), 15)
        self.assertEqual(navegador.completude(navegador.anuncios_em(cartoes), '15')['state'],
                         navegador.COMPLETA_BATE_COM_A_FONTE)
        self.assertEqual(navegador.completude(len(cartoes), '15')['state'],
                         navegador.AQUEM_DA_FONTE,
                         'contar cartoes reprova uma leitura que pegou tudo')

    def test_cartao_sem_grupo_vale_um(self):
        self.assertEqual(navegador.anuncios_em([{}, {'ads_neste_cartao': None}]), 2)

    def test_grupo_declarado_pela_fonte_nao_inventa_os_irmaos(self):
        cartao = {'library_id': '1', 'ads_neste_cartao': 3,
                  'texto': 'Active\nLibrary ID: 1\nSponsored\nolá',
                  'links': [], 'rotulos': [], 'n_img': 1, 'n_video': 0}
        r = coleta.registro(cartao, {'company': 'X', 'page_id': '9'}, 'ES',
                            'COMPLETE_MATCHES_SOURCE_COUNT', '2026-08-30T00:00:00+00:00')
        self.assertEqual(r['ads_in_this_creative_group'], 3)
        self.assertEqual(r['creative_group_state'],
                         'SAME_CREATIVE_AND_TEXT_DECLARED_BY_SOURCE')
        self.assertIsNone(r['creative_group_sibling_ids'])

    def test_so_o_estado_forte_autoriza_dizer_que_um_anuncio_parou(self):
        self.assertEqual(relogio.COMPLETA_OBSERVADA,
                         navegador.COMPLETA_BATE_COM_A_FONTE)


class SemLinhaDeBaseNaoESemMudanca(unittest.TestCase):
    def test_primeira_rodada_declara_baseline_e_nao_ausencia_de_mudanca(self):
        ent, ev = relogio.fundir({}, [anuncio('888')])
        r = relogio.resumo(ent, ev, tem_linha_de_base=False)
        self.assertEqual(r['events'], {'estado': relogio.BASELINE_ONLY})


class ContagemNaoEInvestimento(unittest.TestCase):
    """AD_COUNT != SPEND — e o resumo nao pode ter campo de dinheiro nenhum."""

    def test_resumo_nao_tem_campo_de_gasto_nem_score(self):
        ent, ev = relogio.fundir({}, [anuncio('101')])
        r = relogio.resumo(ent, ev, True)
        chaves = ' '.join(r.keys()).lower()
        for proibida in PROIBIDAS:
            self.assertNotIn(proibida, chaves)

    def test_anuncio_comercial_sai_com_gasto_none(self):
        texto = ('Active\nLibrary ID: 1\nStarted running on Jul 15, 2026\n'
                 'Platforms\nEU transparency\nSee ad details\nX\nSponsored\nolá')
        b = coleta.bloco_declarado(texto)
        self.assertIsNone(b['spend'])
        self.assertIsNone(b['spend_source'])

    def test_gasto_so_aparece_quando_a_fonte_escreve_e_vem_rotulado(self):
        texto = ('Inactive\nLibrary ID: 2\nCategories\nEstimated audience size:\n>1M\n'
                 'Amount spent (USD):\n$1K - $1.5K\nImpressions:\n>1M\n'
                 'Sponsored\nolá')
        b = coleta.bloco_declarado(texto)
        self.assertEqual(b['spend'], {'currency': 'USD', 'range': '$1K - $1.5K'})
        self.assertEqual(b['spend_source'], coleta.BLOCO_POLITICO)


class IdiomaNaoEPais(unittest.TestCase):
    """LANGUAGE != COUNTRY, e PAIS_ALCANCADO != PAIS_ALVO."""

    def test_pais_do_parametro_sai_rotulado_como_alcancado(self):
        cartao = {'library_id': '1', 'texto': 'Active\nLibrary ID: 1\n'
                  'Started running on Jul 15, 2026\nSponsored\n'
                  'HYBRID GROWER KA BA? Machete herbicide',
                  'links': [], 'rotulos': [], 'n_img': 1, 'n_video': 0}
        r = coleta.registro(cartao, {'company': 'Syngenta', 'page_id': '9'},
                            'ES', 'COMPLETE_MATCHES_SOURCE_COUNT', '2026-08-30T00:00:00+00:00')
        self.assertEqual(r['country_reached'], 'ES')
        self.assertIn('AD_REACHED_COUNTRY', r['country_param_semantics'])
        self.assertIsNone(r['target_locations'])
        self.assertEqual(r['target_location_state'], 'NOT_PROVED')

    def test_texto_em_outra_lingua_nao_gera_afirmacao_de_pais(self):
        r = leitura.ler({'creative_text': 'Machete herbicide para sa palay'})
        self.assertNotIn('country', r)


class PaginaGlobalNaoEPaginaLocal(unittest.TestCase):
    """PAGE_COUNTRY != TARGET_COUNTRY — e nome nao promove pagina a local."""

    def test_nome_com_pais_nao_vira_pagina_local(self):
        self.assertEqual(anunciante.escopo(None),
                         anunciante.GLOBAL_OR_UNLABELED_PAGE)

    def test_rotulo_da_meta_e_o_que_promove(self):
        self.assertEqual(anunciante.escopo('Spain'), anunciante.LOCAL_COUNTRY_PAGE)
        self.assertEqual(anunciante.escopo('Argentina and other locations'),
                         anunciante.MULTI_COUNTRY_PAGE)

    def test_sinal_agro_no_nome_e_pista_e_diz_que_e_pista(self):
        self.assertEqual(anunciante.relevancia_agro('Bayer', 'Bayer'),
                         anunciante.AGRO_PARTIAL)
        self.assertEqual(anunciante.relevancia_agro('Bayer Crop Science', 'Bayer'),
                         anunciante.AGRO_PROVED)
        self.assertEqual(anunciante.relevancia_agro('Bayer Aspirin', 'Bayer'),
                         anunciante.AGRO_NAO)


class AnuncioNaoEVendaNemRegistro(unittest.TestCase):
    """AD != SALES / MARKET_SHARE / PRODUCT_AVAILABLE / LOCAL_REGISTRATION."""

    def test_leitura_nao_produz_nenhum_desses_campos(self):
        r = leitura.ler({'creative_text': 'Fungicida para viñedo contra mildiu'})
        texto = json.dumps(r).lower()
        for proibida in PROIBIDAS:
            self.assertNotIn(proibida, texto)

    def test_registro_de_anuncio_nao_afirma_registro_local(self):
        cartao = {'library_id': '1', 'texto': 'Active\nLibrary ID: 1\nSponsored\n'
                  'Fungicida para viñedo', 'links': [], 'rotulos': [],
                  'n_img': 1, 'n_video': 0}
        r = coleta.registro(cartao, {'company': 'X', 'page_id': '9'}, 'ES',
                            'COMPLETE_MATCHES_SOURCE_COUNT', '2026-08-30T00:00:00+00:00')
        self.assertNotIn('local_registration', json.dumps(r).lower())


class RespostaNaoEAtivacao(unittest.TestCase):
    """COMPETITOR_REGISTERED_RESPONSE != COMPETITOR_PAID_META_ACTIVITY."""

    def test_o_acervo_meta_nao_carrega_campo_de_resposta_registrada(self):
        cartao = {'library_id': '1', 'texto': 'Active\nLibrary ID: 1\nSponsored\nolá',
                  'links': [], 'rotulos': [], 'n_img': 1, 'n_video': 0}
        r = coleta.registro(cartao, {'company': 'X', 'page_id': '9'}, 'IT',
                            'COMPLETE_MATCHES_SOURCE_COUNT', '2026-08-30T00:00:00+00:00')
        self.assertNotIn('registered_response', json.dumps(r).lower())


class CriadorNaoEContrato(unittest.TestCase):
    """CREATOR_APPEARANCE != PAID_CREATOR_PARTNERSHIP."""

    def test_mencao_no_criativo_sai_como_nao_provado(self):
        r = leitura.ler({'creative_text': 'Con @agro.juan en el campo'})
        self.assertEqual(r['creators'][0]['paid_creator_relation'], 'NOT_PROVED')
        self.assertEqual(r['creators'][0]['collaboration_observed'],
                         'MENTION_IN_CREATIVE_TEXT')


class ImagemNaoEProva(unittest.TestCase):
    def test_sem_palavra_no_texto_a_cultura_fica_desconhecida(self):
        r = leitura.ler({'creative_text': 'Mira nuestro nuevo vídeo 🌾'})
        self.assertEqual(r['crop_state'], 'NOT_KNOWN')

    def test_grupo_nao_vira_especie(self):
        r = leitura.ler({'creative_text': 'Protección para cereales'})
        self.assertEqual(r['crop_state'], 'PARTIAL')

    def test_nome_comercial_nao_vira_ingrediente_ativo(self):
        r = leitura.ler({'creative_text': 'Nuevo Ampligo® para tu cultivo'})
        self.assertEqual(r['active_ingredient_state'], 'NOT_KNOWN')
        self.assertEqual(r['active_ingredient'], [])

    def test_ingrediente_sai_so_quando_o_anuncio_o_escreve(self):
        r = leitura.ler({'creative_text': 'Contiene azoxistrobina 250 g/L'})
        self.assertEqual(r['active_ingredient_state'], 'PROVED')


class FerramentaCaidaNaoEAusencia(unittest.TestCase):
    """Na primeira rodada real, o Chrome caiu e a ADAMA foi gravada como
    ADVERTISER_NOT_RESOLVED. Ler aquilo depois como "a ADAMA nao anuncia" seria
    transformar navegador fechado em fato de mercado. Estes testes proibem."""

    def test_porta_recusada_nao_vira_nao_resolvido(self):
        erro = ('<urlopen error [WinError 10061] Nenhuma conexao pode ser feita '
                'porque a maquina de destino as recusou ativamente>')
        self.assertEqual(anunciante.estado_de_falha(erro),
                         anunciante.COLLECTION_FAILED_BROWSER_DOWN)
        self.assertNotEqual(anunciante.estado_de_falha(erro),
                            anunciante.ADVERTISER_NOT_RESOLVED)

    def test_falha_desconhecida_tambem_nao_vira_nao_resolvido(self):
        self.assertEqual(anunciante.estado_de_falha(ValueError('json quebrado')),
                         anunciante.COLLECTION_FAILED_OTHER)

    def test_o_arquivo_gravado_conta_falha_de_ferramenta_a_parte(self):
        if not os.path.exists(anunciante.DEST_COMP):
            self.skipTest('resolucao ainda nao rodou')
        with open(anunciante.DEST_COMP, encoding='utf-8') as f:
            d = json.load(f)
        self.assertIn('advertisers_tool_failure', d)
        soma = (d['advertisers_resolved'] + d['advertisers_not_resolved']
                + d['advertisers_tool_failure'])
        self.assertEqual(soma, d['advertisers_attempted'],
                         'toda empresa tentada precisa cair em exatamente um estado')


class GuardaDeIdentidadeDoAnunciante(unittest.TestCase):
    """ADAMA_ADVERTISER_IDENTITY_GUARD.

    O `Instytut Adama Mickiewicza` — instituto cultural polones — entrou como
    ADAMA por casamento nominal e levou 33 dos 40 cartoes do acervo PROPRIO.
    Estes testes existem para que ele nunca mais seja agregado.
    """

    def test_o_instituto_polones_e_recusado(self):
        g = identidade.guarda_identidade('Instytut Adama Mickiewicza', 'ADAMA')
        self.assertEqual(g['state'], identidade.IDENTIDADE_RECUSADA)

    def test_a_pagina_real_da_adama_e_aceita(self):
        self.assertEqual(
            identidade.guarda_identidade('ADAMA Ltd.', 'ADAMA')['state'],
            identidade.IDENTIDADE_ACEITA)

    def test_paginas_legitimas_de_concorrentes_continuam_passando(self):
        for nome, empresa in [('Bayer Crop Science España', 'Bayer'),
                              ('UPL Iberia', 'UPL'),
                              ('Certis Belchim España', 'Certis Belchim'),
                              ('Corteva.Agriscience', 'Corteva'),
                              ('SEIPASA', 'Seipasa')]:
            self.assertEqual(
                identidade.guarda_identidade(nome, empresa)['state'],
                identidade.IDENTIDADE_ACEITA, nome)

    def test_token_no_meio_do_nome_nunca_agrega(self):
        for nome in ['Fundacao Adama Cultural', 'Amigos de Adama',
                     'Instytut Adama Mickiewicza']:
            self.assertEqual(
                identidade.guarda_identidade(nome, 'ADAMA')['state'],
                identidade.IDENTIDADE_RECUSADA, nome)

    def test_o_acervo_limpo_no_disco_nao_contem_o_falso(self):
        caminho = os.path.join(PASTA, 'META-OWN-ADS-ENTITIES-ADAMA-CLEAN-V1.json')
        if not os.path.exists(caminho):
            self.skipTest('limpeza ainda nao rodou')
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
        nomes = {e.get('page_name_resolved') for e in d['entities'].values()}
        self.assertNotIn('Instytut Adama Mickiewicza', nomes)
        self.assertEqual(d['identity_guard']['adama_false_cards_rejected'], 33)
        self.assertEqual(d['identity_guard']['adama_real_cards_remaining'],
                         len(d['entities']))

    def test_os_recusados_foram_preservados_e_nao_apagados(self):
        caminho = os.path.join(PASTA, 'META-OWN-ADS-REJECTED-IDENTITY-V1.json')
        if not os.path.exists(caminho):
            self.skipTest('limpeza ainda nao rodou')
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
        self.assertEqual(len(d['entities']), 33)


class EntregaNaoProvaNacionalidade(unittest.TestCase):
    """ADS_DELIVERED_IN_ES != PAGE_IS_SPANISH."""

    def test_pagina_sem_rotulo_da_meta_fica_not_proved(self):
        p = {'page_name': 'Bayer Crop Science España', 'country_label_by_meta': None}
        self.assertEqual(identidade.escopo_de_pais(p)['page_country_scope'],
                         identidade.SCOPE_NOT_PROVED)

    def test_so_o_rotulo_da_meta_promove(self):
        p = {'page_name': 'Corteva Agriscience', 'country_label_by_meta': 'Italy'}
        e = identidade.escopo_de_pais(p)
        self.assertEqual(e['page_country_scope'], identidade.LOCAL_PROVED)
        self.assertEqual(e['country_code'], 'IT')

    def test_papel_da_pagina_nao_e_inventado_a_partir_da_categoria(self):
        r = identidade.papel({'category': 'Agricultural Service'})
        self.assertEqual(r['page_role'], identidade.ROLE_NOT_PROVED)

    def test_o_inventario_no_disco_nao_conta_entrega_como_localidade(self):
        caminho = os.path.join(PASTA, 'META-PAGE-IDENTITY-EAME-V1.json')
        if not os.path.exists(caminho):
            self.skipTest('inventario ainda nao gerado')
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
        for p in d['pages']:
            if p['page_country_scope']['page_country_scope'] != 'NOT_PROVED':
                self.assertIsNotNone(p['page_country_scope']['proof'])
        s = d['summary']
        self.assertEqual(s['page_country_scope_local_proved']
                         + s['page_country_scope_global_proved']
                         + s['page_country_scope_not_proved'],
                         s['page_ids_proved'])


class DoisSnapshotsNaoProvamCicloDeVida(unittest.TestCase):
    """O que dois pontos no tempo podem e nao podem dizer."""

    def test_o_que_some_de_lista_incompleta_nao_pode_ser_afirmado(self):
        r = temporal.comparar_slice(['1', '2'], ['1'], ambas_pontas_completas=False)
        self.assertEqual(r['no_longer_observed'], [])
        self.assertEqual(r['absent_but_not_claimable'], ['2'])

    def test_com_as_duas_pontas_completas_a_ausencia_pode_ser_afirmada(self):
        r = temporal.comparar_slice(['1', '2'], ['1'], ambas_pontas_completas=True)
        self.assertEqual(r['no_longer_observed'], ['2'])
        self.assertEqual(r['absent_but_not_claimable'], [])

    def test_zero_para_ativo_e_visivel_porque_o_zero_foi_revisitado(self):
        r = temporal.comparar_slice([], ['9'], True)
        self.assertEqual(r['slice_transition'], temporal.ZERO_TO_ACTIVE)
        self.assertEqual(r['newly_observed'], ['9'])

    def test_ativo_para_zero(self):
        self.assertEqual(temporal.comparar_slice(['9'], [], True)['slice_transition'],
                         temporal.ACTIVE_TO_ZERO)

    def test_nada_muda_devolve_present_both_e_nenhuma_transicao(self):
        r = temporal.comparar_slice(['1'], ['1'], True)
        self.assertEqual(r['present_both'], ['1'])
        self.assertEqual(r['slice_transition'], temporal.ACTIVE_BOTH)
        self.assertEqual(r['newly_observed'], [])

    def test_active_again_nao_existe_com_dois_snapshots(self):
        # o estado nao pode nem ser produzido pela funcao de comparacao
        r = temporal.comparar_slice(['1'], ['1'], True)
        self.assertNotIn('ACTIVE_AGAIN', json.dumps(r))
        self.assertNotIn('active_again', json.dumps(r).lower())

    def test_o_manifesto_congelado_inclui_os_zeros(self):
        caminho = os.path.join(PASTA, 'META-TEMPORAL-SNAPSHOT-MANIFEST.json')
        if not os.path.exists(caminho):
            self.skipTest('manifesto ainda nao congelado')
        with open(caminho, encoding='utf-8') as f:
            m = json.load(f)
        self.assertEqual(m['slices_with_ads'] + m['slices_honest_zero'],
                         m['slices_total'])
        self.assertGreater(m['slices_honest_zero'], 0,
                           'sem revisitar zeros, ZERO_TO_ACTIVE seria invisivel')

    def test_o_manifesto_e_congelado_antes_da_coleta(self):
        mcaminho = os.path.join(PASTA, 'META-TEMPORAL-SNAPSHOT-MANIFEST.json')
        scaminho = os.path.join(PASTA, 'META-SNAPSHOT-2-OBSERVATIONS.json')
        if not (os.path.exists(mcaminho) and os.path.exists(scaminho)):
            self.skipTest('snapshot 2 ainda nao rodou')
        with open(mcaminho, encoding='utf-8') as f:
            m = json.load(f)
        with open(scaminho, encoding='utf-8') as f:
            s = json.load(f)
        self.assertEqual(s['manifest_frozen_at'], m['frozen_at'])
        self.assertLess(m['frozen_at'], s['collection_started_at'],
                        'o denominador tem de estar congelado ANTES da coleta')

    def test_profundidade_de_leitura_nao_pode_virar_mudanca_de_mercado(self):
        """Os 587 'novos' da primeira comparacao saiam TODOS de 7 recortes onde
        o snapshot 2 leu mais fundo que o 1. Medir a propria mudanca de metodo e
        chamar de mudanca do concorrente e o erro mais caro possivel aqui."""
        caminho = os.path.join(PASTA, 'META-TEMPORAL-COMPARISON-V1.json')
        if not os.path.exists(caminho):
            self.skipTest('comparacao ainda nao gerada')
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
        confundidos = [s for s in d['slices'] if not s['read_depth_comparable']]
        for s in confundidos:
            self.assertGreater(s['snapshot_2_cards'], s['snapshot_1_cards'])
        soma_confundida = sum(len(s['newly_observed']) for s in confundidos)
        self.assertEqual(
            d['totals_unit_ad_card_all_slices']['NEWLY_OBSERVED']
            - d['totals_unit_ad_card_read_depth_comparable']['NEWLY_OBSERVED'],
            soma_confundida)
        self.assertEqual(d['read_depth_confounded']['slices'], len(confundidos))

    def test_change_observed_usa_so_os_recortes_comparaveis(self):
        caminho = os.path.join(PASTA, 'META-TEMPORAL-COMPARISON-V1.json')
        if not os.path.exists(caminho):
            self.skipTest('comparacao ainda nao gerada')
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
        c = d['totals_unit_ad_card_read_depth_comparable']
        t = d['slice_transitions_unit_slice']
        esperado = 'YES' if (c['NEWLY_OBSERVED']
                             or c['NO_LONGER_OBSERVED_IN_SNAPSHOT_2']
                             or t['ZERO_TO_ACTIVE'] or t['ACTIVE_TO_ZERO']) else 'NO'
        self.assertEqual(d['change_observed'], esperado)

    def test_conservacao_dos_recortes_no_snapshot_2(self):
        caminho = os.path.join(PASTA, 'META-SNAPSHOT-2-OBSERVATIONS.json')
        if not os.path.exists(caminho):
            self.skipTest('snapshot 2 ainda nao rodou')
        with open(caminho, encoding='utf-8') as f:
            s = json.load(f)
        self.assertEqual(s['slices_successful'] + s['slices_failed'],
                         s['slices_total'])
        self.assertEqual(s['slices_content'] + s['slices_honest_zero'],
                         s['slices_successful'])
        self.assertEqual(s['slices_preexisting'] + s['slices_new_this_resume'],
                         s['slices_total'])

    def test_a_janela_de_coleta_nao_finge_um_instante(self):
        caminho = os.path.join(PASTA, 'META-SNAPSHOT-2-OBSERVATIONS.json')
        if not os.path.exists(caminho):
            self.skipTest('snapshot 2 ainda nao rodou')
        with open(caminho, encoding='utf-8') as f:
            s = json.load(f)
        self.assertLess(s['collection_started_at'], s['collection_completed_at'])
        momentos = {o['observed_at'] for o in s['observations']
                    if o.get('slice_state') == 'SLICE_OK'}
        self.assertGreater(len(momentos), 1,
                           'cada observacao mantem seu proprio observed_at')

    def test_a_comparacao_no_disco_nao_afirma_ciclo_de_vida_completo(self):
        caminho = os.path.join(PASTA, 'META-TEMPORAL-COMPARISON-V1.json')
        if not os.path.exists(caminho):
            self.skipTest('comparacao ainda nao gerada')
        with open(caminho, encoding='utf-8') as f:
            d = json.load(f)
        self.assertEqual(d['full_lifecycle_state_capability'], 'NOT_PROVED')
        self.assertIn(d['change_observed'], ('YES', 'NO'))


class CruzamentoNaoColapsa(unittest.TestCase):
    """As duas camadas se encontram numa CELULA, e nunca numa so coluna."""

    def test_registro_sem_anuncio_e_anuncio_sem_registro_sao_celulas_distintas(self):
        reg = {('ADAMA', 'IT'): [{'product_name': 'MAXENTIS', 'registration': '018067'}]}
        ati = {('SYNGENTA', 'IT'): {'ads': 3, 'active': 2, 'products': set(),
                                    'library_ids': ['1']}}
        celulas = {c['company_base']: c for c in
                   convergencia.cruzar(reg, {'IT'}, ati)}
        self.assertEqual(celulas['ADAMA']['competitor_registered_response'], 'YES')
        self.assertEqual(celulas['ADAMA']['competitor_paid_meta_activity'], 'NOT_PROVED')
        self.assertEqual(celulas['SYNGENTA']['competitor_paid_meta_activity'], 'YES')
        self.assertEqual(celulas['SYNGENTA']['competitor_registered_response'],
                         convergencia.CONSULTADO_SEM_ACHADO)

    def test_pais_sem_fonte_regulatoria_nao_vira_sem_registro(self):
        ati = {('BASF', 'FR'): {'ads': 1, 'active': 1, 'products': set(),
                                'library_ids': ['9']}}
        c = convergencia.cruzar({}, {'IT'}, ati)[0]
        self.assertEqual(c['competitor_registered_response'],
                         convergencia.NAO_CONSULTADO)
        self.assertNotEqual(c['competitor_registered_response'], 'NO')

    def test_anuncio_nao_promove_produto_a_autorizado(self):
        reg = {('ADAMA', 'IT'): [{'product_name': 'MAXENTIS', 'registration': '018067'}]}
        ati = {('ADAMA', 'IT'): {'ads': 1, 'active': 1,
                                 'products': {'KOJAMI'}, 'library_ids': ['1']}}
        c = convergencia.cruzar(reg, {'IT'}, ati)[0]
        self.assertEqual(c['product_crosscheck'][0]['state'],
                         convergencia.PRODUCT_MATCH_NOT_PROVED)

    def test_nome_igual_casa_e_traz_o_numero_do_registro(self):
        reg = {('ADAMA', 'IT'): [{'product_name': 'MAXENTIS', 'registration': '018067'}]}
        ati = {('ADAMA', 'IT'): {'ads': 1, 'active': 1,
                                 'products': {'MAXENTIS'}, 'library_ids': ['1']}}
        c = convergencia.cruzar(reg, {'IT'}, ati)[0]
        self.assertEqual(c['product_crosscheck'][0]['state'],
                         convergencia.PRODUCT_MATCH_PROVED)
        self.assertEqual(c['product_crosscheck'][0]['registration'], '018067')


class ArtefatoEDerivado(unittest.TestCase):
    def test_o_artefato_se_declara_derivado_e_nao_dono_da_verdade(self):
        art = piloto.artefato({'entities': {}, 'as_of_date': 'x'}, {'events': []})
        self.assertTrue(art['read_only'])
        self.assertFalse(art['is_source_of_truth'])
        self.assertTrue(art['not_wired_to_portal'])
        self.assertTrue(art['cannot_claim'])

    def test_o_artefato_nao_carrega_escore_de_pressao(self):
        art = piloto.artefato({'entities': {}}, {'events': []})
        texto = json.dumps(art).lower()
        for proibida in PROIBIDAS:
            self.assertNotIn(proibida, texto)

    def test_inativo_sem_data_de_fim_nao_conta_como_recente(self):
        ent = {'entities': {'1': {'active_status': 'INACTIVE', 'end_date': None,
                                  'company': 'X', 'reading': {}}}}
        m = piloto.metricas(ent, {}, {'events': []})
        self.assertEqual(m['inactive_last_365d'], 0)
        self.assertEqual(m['inactive_end_date_not_read'], 1)

    def test_toda_contagem_sai_com_denominador(self):
        m = piloto.metricas({'entities': {}}, {}, {'events': []})
        self.assertIn('crop_proved_denominator', m)
        self.assertIn('issue_proved_denominator', m)


class DonoDoDataset(unittest.TestCase):
    """ADAMA e concorrente nao podem cair no mesmo arquivo."""

    def test_destinos_sao_arquivos_diferentes(self):
        self.assertNotEqual(anunciante.DEST_COMP, anunciante.DEST_ADAMA)

    def test_arquivos_gravados_declaram_donos_distintos(self):
        pares = [(anunciante.DEST_COMP, 'COMPETITOR_PAID_META_ACTIVITY'),
                 (anunciante.DEST_ADAMA, 'OWN_PUBLIC_META_ACTIVITY')]
        for caminho, esperado in pares:
            if not os.path.exists(caminho):
                self.skipTest('coleta ainda nao rodou: %s' % caminho)
            with open(caminho, encoding='utf-8') as f:
                d = json.load(f)
            self.assertEqual(d.get('dataset'), esperado)
            self.assertEqual(d.get('dataset_owner'), 'META_COMPETITOR_EAME')

    def test_owner_nao_invade_as_outras_missoes(self):
        for caminho in (anunciante.DEST_COMP, anunciante.DEST_ADAMA):
            if not os.path.exists(caminho):
                continue
            with open(caminho, encoding='utf-8') as f:
                bruto = f.read()
            self.assertNotIn('EARLY_SIGNAL_EAME', bruto)
            self.assertNotIn('CREATOR_MAP_EAME', bruto)


if __name__ == '__main__':
    unittest.main(verbosity=2)
