"""
As regressões obrigatórias da localização do fato.

Cada classe aqui corresponde a um falso positivo MEDIDO no Sintonia Brasil e
traduzido para o italiano. Nenhuma é hipotética: se alguma destas passar a
reprovar, o sistema voltou a dizer que a doença está onde ela não está.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'scripts'))
import fato_local as fl  # noqa: E402


def lugares(texto):
    ok, _ = fl.localizacoes_do_fato(texto)
    return {a['FACT_LOCATION'] for a in ok}


def recusas(texto):
    _, nao = fl.localizacoes_do_fato(texto)
    return {r['PLACE']: r for r in nao}


class AsQuatroEspeciesNaoSePromovem(unittest.TestCase):

    def test_local_declarado_no_perfil_nunca_vira_fato(self):
        """PROFILE_LOCATION -> FACT_LOCATION = REPROVA."""
        r = fl.local_declarado_do_perfil('Foggia, Puglia, Italia')
        self.assertEqual(r['PLACE_KIND'], fl.BASE)
        self.assertEqual(r['FACT_LOCATION'], 'NOT_KNOWN')
        self.assertIn('Foggia', r['PROFILE_DECLARED_LOCATION'])

    def test_a_proveniencia_do_perfil_e_independente_da_do_fato(self):
        """ROW_PROVENANCE != VALUE_PROVENANCE: cada valor diz de onde veio."""
        perfil = fl.local_declarado_do_perfil('Foggia', origem='PROFILE.location')
        ok, _ = fl.localizacoes_do_fato('Sintomi osservati in Toscana',
                                        origem='POST_TEXT')
        self.assertEqual(perfil['PROFILE_LOCATION_ORIGIN'], 'PROFILE.location')
        self.assertEqual(ok[0]['FACT_LOCATION_ORIGIN'], 'POST_TEXT')
        self.assertNotEqual(perfil['PROFILE_LOCATION_ORIGIN'],
                            ok[0]['FACT_LOCATION_ORIGIN'])

    def test_as_quatro_especies_existem_e_sao_distintas(self):
        self.assertEqual(len(set(fl.ESPECIES)), 4)
        self.assertIn('BASE ≠ OPERATING ≠ INFLUENCE ≠ FACT', fl.__doc__)

    def test_o_caso_italiano_tem_os_quatro_lugares_ao_mesmo_tempo(self):
        """Pesquisador em Foggia, instituição CREA, post sobre Toscana, fato em
        Grosseto. Nenhum sobrescreve outro."""
        perfil = fl.local_declarado_do_perfil('Foggia, Puglia, Italia')
        texto = ('Operiamo in Toscana. Fusariosi della spiga constatata a '
                 'Grosseto su grano duro.')
        ok, nao = fl.localizacoes_do_fato(texto)
        self.assertEqual({a['FACT_LOCATION'] for a in ok}, {'Grosseto'})
        self.assertIn('Toscana', recusas(texto))
        self.assertIn('Foggia', perfil['PROFILE_DECLARED_LOCATION'])
        self.assertEqual(perfil['FACT_LOCATION'], 'NOT_KNOWN')


class MencaoNaoEFato(unittest.TestCase):

    def test_evento_em_bologna_nao_e_doenca_em_bologna(self):
        """"evento em Bologna" -> disease fact in Bologna = REPROVA."""
        t = 'Convegno a Bologna sulla fusariosi del grano duro.'
        self.assertNotIn('Bologna', lugares(t))
        self.assertEqual(recusas(t)['Bologna']['WHY'], 'local de evento')

    def test_atuamos_na_toscana_nao_e_fato_na_toscana(self):
        """"atuamos em Toscana" -> fact in Toscana = REPROVA."""
        t = 'Operiamo in Toscana con i nostri tecnici.'
        self.assertNotIn('Toscana', lugares(t))
        self.assertEqual(recusas(t)['Toscana']['WHY'], 'área de atuação')

    def test_sede_da_entidade_nao_e_fato(self):
        t = 'Azienda con sede a Foggia, specializzata in cereali.'
        self.assertNotIn('Foggia', lugares(t))

    def test_moro_em_nao_e_fato(self):
        t = 'Abito a Siena da dieci anni.'
        self.assertNotIn('Siena', lugares(t))

    def test_afiliacao_institucional_nao_e_fato(self):
        t = 'Ricercatore presso il centro di Roma.'
        self.assertNotIn('Roma', lugares(t))

    def test_area_comercial_nao_e_fato(self):
        t = 'Serviamo clienti in Puglia e Basilicata.'
        self.assertEqual(lugares(t), set())

    def test_substring_acidental_nao_conta_como_lugar(self):
        """"Romagna" contem "Roma"; "Barletta" contem "Bari"."""
        ms = {m['PLACE'] for m in fl.mencoes('Emilia-Romagna')}
        self.assertNotIn('Roma', ms)
        self.assertIn('Emilia-Romagna', ms)

    def test_preposicao_e_proximidade_sozinhas_nao_bastam(self):
        """Nao usar somente preposicao ou proximidade de palavras."""
        t = 'Fusariosi. A Bologna una bella giornata.'
        self.assertNotIn('Bologna', lugares(t))


class OQueSimSustentaOFato(unittest.TestCase):

    def test_constatata_fusariosi_a_grosseto_aprova(self):
        """"constatata fusariosi a Grosseto" -> FACT Grosseto = APROVA."""
        ok, _ = fl.localizacoes_do_fato('Constatata fusariosi a Grosseto.')
        self.assertEqual(len(ok), 1)
        a = ok[0]
        self.assertEqual(a['FACT_LOCATION'], 'Grosseto')
        self.assertEqual(a['FACT_LOCATION_PRECISION'], fl.PROVINCE)
        self.assertEqual(a['TYPE_OF_EVIDENCE'], fl.CONFIRMED_FOCUS)

    def test_sintomas_observados_sustentam_observacao_de_campo(self):
        ok, _ = fl.localizacoes_do_fato('Sintomi osservati in Toscana su grano duro.')
        self.assertEqual(ok[0]['TYPE_OF_EVIDENCE'], fl.FIELD_OBSERVATION)
        self.assertEqual(ok[0]['FACT_LOCATION_PRECISION'], fl.REGION)

    def test_todo_fato_aceito_carrega_o_trecho_que_o_prova(self):
        """FACT sem trecho reproduzivel nao pode ser promovido a PROVED."""
        ok, _ = fl.localizacoes_do_fato('Constatata fusariosi a Grosseto su duro.')
        for campo in ('FACT_LOCATION_EVIDENCE', 'FACT_LOCATION_ANCHOR',
                      'FACT_LOCATION_ORIGIN', 'FACT_LOCATION_PRECISION',
                      'TYPE_OF_EVIDENCE'):
            self.assertTrue(ok[0][campo], campo)
        self.assertIn('Grosseto', ok[0]['FACT_LOCATION_EVIDENCE'])

    def test_a_ancora_mais_proxima_governa_e_nao_a_existencia_de_uma_ancora(self):
        """Uma frase com as duas ancoras: cada lugar e governado pela sua."""
        t = 'Convegno a Bologna e fusariosi constatata a Grosseto.'
        self.assertEqual(lugares(t), {'Grosseto'})
        self.assertNotIn('Grosseto', recusas(t))
        self.assertIn('Bologna', recusas(t))


class APrecisaoViajaComOFato(unittest.TestCase):

    def test_se_a_fonte_prova_toscana_nao_se_inventa_grosseto(self):
        ok, _ = fl.localizacoes_do_fato('Sintomi rilevati in Toscana.')
        self.assertEqual(ok[0]['FACT_LOCATION'], 'Toscana')
        self.assertEqual(ok[0]['FACT_LOCATION_PRECISION'], fl.REGION)
        self.assertNotIn('Grosseto', lugares('Sintomi rilevati in Toscana.'))

    def test_se_a_fonte_prova_grosseto_nao_se_reduz_para_italia(self):
        ok, _ = fl.localizacoes_do_fato('Focolaio accertato a Grosseto.')
        self.assertEqual(ok[0]['FACT_LOCATION_PRECISION'], fl.PROVINCE)
        self.assertNotIn('Italia', lugares('Focolaio accertato a Grosseto.'))

    def test_toda_precisao_declarada_esta_na_taxonomia(self):
        ok, _ = fl.localizacoes_do_fato(
            'Constatata a Grosseto e sintomi osservati in Toscana e in Italia.')
        for a in ok:
            self.assertIn(a['FACT_LOCATION_PRECISION'], fl.PRECISOES)


class UmConteudoPodeTerVariosLugares(unittest.TestCase):

    def test_tres_procedencias_dao_tres_localizacoes_e_nao_uma(self):
        """"amostre positive provenienti da A, B, C" -> tres candidatas."""
        t = 'Campioni positivi provenienti da Grosseto, Siena e Arezzo.'
        self.assertEqual(lugares(t), {'Grosseto', 'Siena', 'Arezzo'})

    def test_cada_uma_traz_a_propria_evidencia_e_o_proprio_tipo(self):
        ok, _ = fl.localizacoes_do_fato(
            'Campioni positivi provenienti da Grosseto, Siena e Arezzo.')
        self.assertEqual(len(ok), 3)
        for a in ok:
            self.assertEqual(a['TYPE_OF_EVIDENCE'], fl.DIAGNOSTIC_SAMPLE)
            self.assertTrue(a['FACT_LOCATION_EVIDENCE'])

    def test_nao_se_fica_com_a_primeira_cidade_encontrada(self):
        ok, _ = fl.localizacoes_do_fato(
            'Focolai confermati a Foggia. Sintomi osservati anche a Bari.')
        self.assertEqual({a['FACT_LOCATION'] for a in ok}, {'Foggia', 'Bari'})

    def test_um_conteudo_sem_lugar_nenhum_devolve_zero_e_nao_um_chute(self):
        ok, _ = fl.localizacoes_do_fato('Fusariosi della spiga sul grano duro.')
        self.assertEqual(ok, [])


class ListaTerritorialNaoEFato(unittest.TestCase):

    def test_lista_comercial_de_cidades_nao_vira_fato(self):
        """lista comercial de cidades -> FACT_LIST = REPROVA."""
        t = 'Filiali: Milano, Torino, Genova, Bologna, Verona'
        self.assertEqual(lugares(t), set())

    def test_lista_sem_ancora_nenhuma_e_marcada_como_lista_territorial(self):
        t = 'Milano, Torino, Genova, Bologna'
        estados = {r['STATE'] for r in recusas(t).values()}
        self.assertEqual(estados, {fl.TERRITORIAL_LIST})

    def test_mas_uma_lista_COM_ancora_de_ocorrencia_vale(self):
        """A lista vira fato quando a relacao com o acontecimento esta sustentada."""
        t = 'Focolai confermati a Grosseto, Siena, Arezzo, Firenze'
        self.assertEqual(lugares(t), {'Grosseto', 'Siena', 'Arezzo', 'Firenze'})


class OcorrenciaNaoEIncidencia(unittest.TestCase):

    def test_amostra_diagnostica_nao_vira_incidencia_regional(self):
        """diagnostic sample -> regional incidence = REPROVA."""
        r = fl.ocorrencia_nao_e_incidencia([fl.DIAGNOSTIC_SAMPLE] * 5)
        self.assertEqual(r['INCIDENCE'], 'NOT_KNOWN')
        self.assertEqual(r['PREVALENCE'], 'NOT_KNOWN')
        self.assertEqual(r['REGIONAL_PRESSURE'], 'NOT_KNOWN')

    def test_as_especies_de_evidencia_nao_se_somam_entre_si(self):
        r = fl.ocorrencia_nao_e_incidencia(
            [fl.DIAGNOSTIC_SAMPLE, fl.REGIONAL_STATEMENT, fl.FIELD_OBSERVATION])
        self.assertEqual(r['BY_TYPE_OF_EVIDENCE'][fl.DIAGNOSTIC_SAMPLE], 1)
        self.assertEqual(r['BY_TYPE_OF_EVIDENCE'][fl.REGIONAL_STATEMENT], 1)
        # o comunicado regional NAO entra na contagem de ocorrencias observadas
        self.assertEqual(r['OBSERVED_OCCURRENCES'], 2)

    def test_tipo_desconhecido_cai_em_OTHER_e_nao_some(self):
        r = fl.ocorrencia_nao_e_incidencia(['ALGO_QUE_NAO_EXISTE'])
        self.assertEqual(r['BY_TYPE_OF_EVIDENCE'][fl.OTHER_EVIDENCE], 1)


class TempoDoFatoNaoEDataDePublicacao(unittest.TestCase):

    def test_sem_evidencia_temporal_o_fato_fica_sem_data(self):
        """published_at -> fact_time sem evidencia = REPROVA."""
        r = fl.tempo_do_fato('Fusariosi constatata a Grosseto.', '2026-04-20')
        self.assertEqual(r['FACT_TIME'], 'NOT_KNOWN')
        self.assertEqual(r['PUBLISHED_AT'], '2026-04-20')
        self.assertNotEqual(r['FACT_TIME'], r['PUBLISHED_AT'])

    def test_semana_passada_e_semana_e_nao_dia(self):
        r = fl.tempo_do_fato('Constatata la settimana scorsa.', '2026-04-20')
        self.assertEqual(r['FACT_TIME_PRECISION'], fl.WEEK)

    def test_safra_e_temporada_e_nao_dia(self):
        r = fl.tempo_do_fato('Nella campagna 2025/26 abbiamo osservato.', '2026-04-20')
        self.assertEqual(r['FACT_TIME_PRECISION'], fl.SEASON)

    def test_durante_marco_e_mes(self):
        r = fl.tempo_do_fato('Durante marzo i sintomi sono comparsi.', '2026-04-20')
        self.assertEqual(r['FACT_TIME_PRECISION'], fl.MONTH)
        self.assertEqual(r['FACT_TIME'], 'marzo')

    def test_toda_data_do_fato_carrega_o_trecho_que_a_prova(self):
        r = fl.tempo_do_fato('Durante marzo i sintomi.', '2026-04-20')
        self.assertIn('marzo', r['FACT_TIME_EVIDENCE'])
        self.assertEqual(r['FACT_TIME_ORIGIN'], 'POST_TEXT')


class GeotagNaoFechaFato(unittest.TestCase):

    def test_geotag_e_preservada_mas_nao_promovida(self):
        """geotag -> fact location automaticamente = REPROVA."""
        r = fl.geo_do_conteudo('Grosseto, Toscana')
        self.assertEqual(r['PLACE_KIND'], fl.CONTENT_GEO_EVIDENCE)
        self.assertEqual(r['FACT_LOCATION'], 'NOT_KNOWN')
        self.assertIn('Grosseto', r['VALUE'])


class MutacaoDasLeisCentrais(unittest.TestCase):
    """As provas acima só valem se morderem. Aqui eu quebro a lei de propósito e
    exijo que alguma prova caia — uma regressão que passa com o código quebrado
    não é regressão, é decoração."""

    # A frase onde a ancora negativa e a UNICA coisa que separa um foco de doenca
    # de um local de evento: a positiva vem antes das duas cidades, e so o
    # "convegno" impede que Bologna herde o "constatata" de Grosseto.
    FRASE_LIMITE = 'Fusariosi constatata a Grosseto durante il convegno a Bologna.'

    def test_com_a_lei_de_pe_so_grosseto_e_fato(self):
        self.assertEqual(lugares(self.FRASE_LIMITE), {'Grosseto'})

    def test_se_a_ancora_negativa_sumir_bologna_vira_foco_de_doenca(self):
        """A prova de que as ancoras negativas trabalham, e nao so existem.

        Sem elas, Bologna herda o "constatata" que era de Grosseto e o sistema
        passa a afirmar fusariose num lugar onde houve um congresso.
        """
        salvo = fl.ANCORAS_NEGATIVAS
        try:
            fl.ANCORAS_NEGATIVAS = ()
            self.assertIn('Bologna', lugares(self.FRASE_LIMITE),
                          'a mutacao nao mudou nada — a prova nao estava mordendo')
        finally:
            fl.ANCORAS_NEGATIVAS = salvo
        self.assertNotIn('Bologna', lugares(self.FRASE_LIMITE))

    def test_se_a_ancora_positiva_sumir_nenhum_fato_sobrevive(self):
        salvo = fl.ANCORAS_POSITIVAS
        try:
            fl.ANCORAS_POSITIVAS = ()
            self.assertEqual(lugares('Constatata fusariosi a Grosseto.'), set())
        finally:
            fl.ANCORAS_POSITIVAS = salvo
        self.assertEqual(lugares('Constatata fusariosi a Grosseto.'), {'Grosseto'})

    def test_se_a_fronteira_de_palavra_sumir_a_substring_volta_a_casar(self):
        ms = {m['PLACE'] for m in fl.mencoes('Emilia-Romagna e Barletta')}
        self.assertNotIn('Roma', ms)
        self.assertNotIn('Bari', ms)
        # e a prova de que o gazetteer REALMENTE contem os dois nomes curtos,
        # senao este teste passaria por ausencia e nao por protecao
        nomes = {n for n, _ in fl.GAZETTEER}
        self.assertIn('Roma', nomes)
        self.assertIn('Bari', nomes)

    def test_se_o_governo_virasse_existe_ancora_na_frase_bologna_seria_fato(self):
        """A prova de que `_governa` olha a MAIS PROXIMA, e nao 'existe alguma'."""
        t = 'Convegno a Bologna e fusariosi constatata a Grosseto.'
        positivas = fl._ancoras(t, fl.ANCORAS_POSITIVAS)
        pos_bologna = fl.mencoes(t)[0]['POS']
        # existe ancora positiva na frase...
        self.assertTrue(positivas)
        # ...mas nenhuma ANTES de Bologna
        self.assertFalse([a for a in positivas if a['POS'] < pos_bologna])
        self.assertNotIn('Bologna', lugares(t))


if __name__ == '__main__':
    unittest.main()
