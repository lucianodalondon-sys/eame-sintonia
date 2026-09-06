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
        # A origem agora diz TAMBEM por que a data foi aceita: ela estava
        # amarrada ao acontecimento. "veio do texto" nao bastava — o carimbo da
        # publicacao tambem vem do texto.
        self.assertEqual(r['FACT_TIME_ORIGIN'], 'TEXT/TIED_TO_EVENT')


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



class OCarimboDaPublicacaoNaoPodeVirarTempoDoFato(unittest.TestCase):
    """Defeito medido em 2026-08-30 sobre um artigo REAL do AgroNotizie.

    A implementação pegava a PRIMEIRA expressão temporal do texto. Num artigo de
    imprensa, a primeira é o carimbo da publicação — e ela devolvia, para uma
    reportagem de 13/02/2026 sobre a safra de 2025, `FACT_TIME = 13 febbraio`.
    A lei estava escrita no arquivo e a implementação a contornava por dentro.
    """

    ARTIGO = ('13 febbraio 2026 Mais e micotossine, un 2025 da dimenticare. '
              'Al classico appuntamento con la Giornata del Mais, organizzata lo '
              'scorso 30 gennaio dal Crea, sede di Bergamo, i dati diffusi sul '
              'monitoraggio delle micotossine durante la stagione 2025 confermano '
              "tendenze allarmanti, uno dei picchi dell'intera serie storica "
              '2011-2025.')

    def test_o_carimbo_da_publicacao_e_descartado_e_dito(self):
        r = fl.tempo_do_fato(self.ARTIGO, '2026-02-13')
        self.assertNotEqual(r['FACT_TIME'], '13 febbraio')
        descartados = {d['VALUE']: d['WHY'] for d in r['TIME_CANDIDATES_DISCARDED']}
        self.assertEqual(descartados.get('13 febbraio 2026'), fl.PUBLICATION_STAMP)

    def test_o_tempo_do_fato_e_a_safra_e_nao_a_data_do_jornal(self):
        r = fl.tempo_do_fato(self.ARTIGO, '2026-02-13')
        self.assertEqual(r['FACT_TIME'], 'stagione 2025')
        self.assertEqual(r['FACT_TIME_PRECISION'], fl.SEASON)
        self.assertEqual(r['PUBLISHED_AT'], '2026-02-13')

    def test_intervalo_de_serie_historica_nao_e_data_de_acontecimento(self):
        """"2011-2025" e o alcance da MEDICAO, nao a data do que foi medido."""
        self.assertFalse(fl._e_campanha('2011-2025'))
        self.assertTrue(fl._e_campanha('2025/26'))
        self.assertTrue(fl._e_campanha('2025-26'))
        r = fl.tempo_do_fato(self.ARTIGO, '2026-02-13')
        self.assertNotEqual(r['FACT_TIME'], '2011-2025')

    def test_data_solta_sem_ancora_de_acontecimento_nao_vira_tempo_do_fato(self):
        r = fl.tempo_do_fato('Il regolamento del 2019 resta in vigore.', '2026-02-13')
        self.assertEqual(r['FACT_TIME'], 'NOT_KNOWN')
        self.assertIn('FACT_TIME_CANDIDATES', r)

    def test_uma_data_igual_a_publicacao_mas_ancorada_ainda_e_descartada(self):
        """Se o texto diz "campioni raccolti il 13 febbraio" e publica no mesmo
        dia, o campo continua sendo o da publicacao ate prova em contrario."""
        r = fl.tempo_do_fato('Campioni osservati il 13 febbraio 2026.', '2026-02-13')
        descartados = {d['VALUE'] for d in r['TIME_CANDIDATES_DISCARDED']}
        self.assertIn('13 febbraio 2026', descartados)


class OGazetteerDizOQueNaoCobre(unittest.TestCase):
    """Bergamo aparecia TRES vezes num artigo real e nao era recusada por lei
    nenhuma: era invisivel, porque faltava no gazetteer. O resultado certo veio
    pelo motivo errado — e isso nao conta como protecao."""

    def test_bergamo_existe_e_e_julgada_pela_lei(self):
        nomes = {n for n, _ in fl.GAZETTEER}
        self.assertIn('Bergamo', nomes)
        _, nao = fl.localizacoes_do_fato('Giornata del Mais, sede di Bergamo.')
        self.assertEqual(nao[0]['WHY'], 'endereço da entidade')

    def test_e_quando_ha_ancora_de_verdade_bergamo_e_fato(self):
        ok, _ = fl.localizacoes_do_fato('Fumonisine rilevate a Bergamo nel 2025.')
        self.assertEqual([a['FACT_LOCATION'] for a in ok], ['Bergamo'])

    def test_a_cobertura_e_declarada_e_nao_presumida(self):
        c = fl.cobertura()
        self.assertEqual(c['MUNICIPALITIES'], 0)
        self.assertIn('NOT_IN_GAZETTEER', c['LIMIT'])
        self.assertIn('Ovest', c['ALSO_NOT_COVERED'])


class OBoletimFitossanitarioRealAchouTresFuros(unittest.TestCase):
    """Um boletim de serviço fitossanitário regional — o conteúdo de campo mais
    rico que esta missão encontrou — devolvia ZERO localizações. Três defeitos,
    todos só visíveis contra texto real."""

    BOLETIM = ('In base ai dati pervenuti dalla rete di monitoraggio regionale sugli '
               'areali CONCA TERNANA, LAGO TRASIMENO, si rappresenta la seguente '
               'situazione: FRUMENTO Non riscontrata presenza di avversità ad '
               'eccezione di lieve attacco di Septoriosi nei Comuni di Branca di '
               'Gubbio. ORZO Fitopatie assenti ad eccezione di presenza media di '
               'Septoriosi nel Comune di Parrano (TR). Le s.a. utilizzabili sono '
               "riportate nel relativo disciplinare valido per l'annata 2021-2022.")

    def _fatos(self):
        ok, _ = fl.localizacoes_do_fato(self.BOLETIM)
        return {a['FACT_LOCATION']: a for a in ok}

    def test_1_a_ancora_do_ataque_no_singular_existe(self):
        """`attacch[io]` não pegava "attacco". A frase ficava sem âncora nenhuma."""
        self.assertIn('Branca di Gubbio', self._fatos())
        self.assertEqual(self._fatos()['Branca di Gubbio']['FACT_LOCATION_ANCHOR'],
                         'attacco')

    def test_2_o_comune_declarado_pelo_texto_vale_sem_gazetteer(self):
        """Comune não é província e o gazetteer só tem províncias. Mas o texto
        DIZ "nel Comune di Parrano" — é a fonte nomeando a unidade, não eu."""
        nomes = {n for n, _ in fl.GAZETTEER}
        self.assertNotIn('Parrano', nomes)
        f = self._fatos()['Parrano']
        self.assertEqual(f['FACT_LOCATION_PRECISION'], fl.MUNICIPALITY)
        self.assertEqual(f['PRECISION_SOURCE'], 'DECLARED_BY_TEXT')

    def test_o_marcador_da_o_nivel_e_nao_a_permissao(self):
        """"nel Comune di X" sozinho não é fato: continua precisando de âncora."""
        ok, nao = fl.localizacoes_do_fato('La sede è nel Comune di Parrano.')
        self.assertEqual(ok, [])
        self.assertIn('Parrano', {r['PLACE'] for r in nao})

    def test_o_marcador_nao_transforma_palavra_comum_em_lugar(self):
        ok, nao = fl.localizacoes_do_fato('Rilevato nel comune di produzione.')
        self.assertEqual([a['FACT_LOCATION'] for a in ok], [])

    def test_3_observacao_negada_nao_e_observacao(self):
        """"Non riscontrata presenza di avversità" com um lugar depois produziria
        a afirmação OPOSTA à do boletim."""
        ok, nao = fl.localizacoes_do_fato(
            'Non riscontrata presenza di avversità nei Comuni di Gubbio.')
        self.assertEqual(ok, [])
        estados = {r['PLACE']: r['STATE'] for r in nao}
        self.assertEqual(estados['Gubbio'], fl.NEGATED_OBSERVATION)

    def test_a_negacao_termina_em_ad_eccezione_di(self):
        """"Fitopatie assenti AD ECCEZIONE DI presenza media a X" volta a ser
        observação positiva — e o boletim real depende disso."""
        self.assertIn('Parrano', self._fatos())
        self.assertEqual(self._fatos()['Parrano']['TYPE_OF_EVIDENCE'],
                         fl.FIELD_OBSERVATION)

    def test_a_zona_da_rede_de_monitoramento_nao_vira_fato(self):
        """"areali CONCA TERNANA" é geografia da FONTE, não unidade administrativa."""
        _, nao = fl.localizacoes_do_fato(self.BOLETIM)
        self.assertIn('CONCA TERNANA', {r['PLACE'] for r in nao})
        self.assertNotIn('CONCA TERNANA', self._fatos())

    def test_a_validade_de_uma_norma_nao_e_a_data_do_acontecimento(self):
        """"disciplinare valido per l'annata 2021-2022" devolvia FACT_TIME=annata 2021."""
        r = fl.tempo_do_fato(self.BOLETIM)
        self.assertEqual(r['FACT_TIME'], 'NOT_KNOWN')
        motivos = {d['WHY'] for d in r['TIME_CANDIDATES_DISCARDED']}
        self.assertIn('REGULATORY_VALIDITY_NOT_FACT_TIME', motivos)

    def test_safra_deixou_de_ser_ancora_de_si_mesma(self):
        """`annata`/`stagione` estavam nos DOIS lados: na expressão e na âncora,
        então toda expressão de safra se autoqualificava."""
        self.assertNotIn(r'annata', fl.ANCORAS_DE_TEMPO_DO_FATO)
        self.assertNotIn(r'stagione', fl.ANCORAS_DE_TEMPO_DO_FATO)

    # As duas proteções se sobrepõem de propósito, então uma mutação precisa de
    # uma frase onde SÓ a proteção mutada esteja em jogo. Uma frase que ambas
    # cobrem faria a mutação "passar" e a prova mentiria por excesso de defesa.
    FRASE_NORMA = ("Sintomi rilevati secondo il disciplinare valido per "
                   "l'annata 2021-2022.")

    def test_com_as_duas_leis_de_pe_a_norma_nao_data_o_fato(self):
        self.assertEqual(fl.tempo_do_fato(self.FRASE_NORMA)['FACT_TIME'], 'NOT_KNOWN')

    def test_mutacao_sem_contexto_administrativo_a_validade_da_norma_vira_fato(self):
        """A frase tem âncora de verdade ("rilevati"): só o contexto
        administrativo a separa de uma data de acontecimento."""
        salvo = fl.CONTEXTO_ADMINISTRATIVO
        try:
            fl.CONTEXTO_ADMINISTRATIVO = ()
            r = fl.tempo_do_fato(self.FRASE_NORMA)
            self.assertEqual(r['FACT_TIME'], "annata 2021-2022",
                             'a mutação não mudou nada — a prova não mordia')
        finally:
            fl.CONTEXTO_ADMINISTRATIVO = salvo

    def test_mutacao_se_safra_voltar_a_ser_ancora_ela_se_autoqualifica(self):
        """Sem contexto administrativo E com `annata` de volta nas âncoras, uma
        expressão de safra passa a se ancorar em si mesma."""
        salvo_c, salvo_a = fl.CONTEXTO_ADMINISTRATIVO, fl.ANCORAS_DE_TEMPO_DO_FATO
        try:
            fl.CONTEXTO_ADMINISTRATIVO = ()
            fl.ANCORAS_DE_TEMPO_DO_FATO = salvo_a + (r'annata',)
            r = fl.tempo_do_fato("Il disciplinare vale per l'annata 2021-2022.")
            self.assertNotEqual(r['FACT_TIME'], 'NOT_KNOWN',
                                'a mutação não mudou nada — a prova não mordia')
        finally:
            fl.CONTEXTO_ADMINISTRATIVO, fl.ANCORAS_DE_TEMPO_DO_FATO = salvo_c, salvo_a


class OBoletimEmJanelaAchouMaisDoisFuros(unittest.TestCase):
    """Boletim ERSA FVG frumento-orzo n.7 de 20/04/2026 — três dias antes da data
    do caso. O conteúdo em janela mais próximo que esta missão encontrou, e ele
    devolveu uma província a 100 km de distância como local de um fato."""

    RISCO = 'Rischio attacchi septoriosi in Friuli Venezia Giulia (10 marker).'
    CAMPO = ('Dai rilievi in campo è emerso che si osservano sintomi evidenti '
             'della patologia in Friuli Venezia Giulia.')

    def test_a_regiao_sem_hifen_nao_vira_a_provincia_de_dentro(self):
        """"Friuli Venezia Giulia" sem hífen não casava com a região do
        gazetteer, e sobrava "Venezia" — província a 100 km dali. A substring
        acidental voltou pela porta da grafia."""
        lugares = [m['PLACE'] for m in fl.mencoes(self.RISCO)]
        self.assertEqual(lugares, ['Friuli-Venezia Giulia'])
        self.assertNotIn('Venezia', lugares)

    def test_o_mesmo_vale_para_as_outras_regioes_compostas(self):
        for escrito, esperado in (('Emilia Romagna', 'Emilia-Romagna'),
                                  ('Emilia-Romagna', 'Emilia-Romagna'),
                                  ('Trentino Alto Adige', 'Trentino-Alto Adige')):
            self.assertEqual([m['PLACE'] for m in fl.mencoes('Rilevato in ' + escrito)],
                             [esperado], escrito)

    def test_risco_modelado_nao_e_sintoma_observado(self):
        """O próprio boletim distingue as duas coisas em frases seguidas."""
        ok, _ = fl.localizacoes_do_fato(self.RISCO)
        self.assertEqual(ok[0]['TYPE_OF_EVIDENCE'], fl.MODELLED_RISK)
        ok2, _ = fl.localizacoes_do_fato(self.CAMPO)
        self.assertEqual(ok2[0]['TYPE_OF_EVIDENCE'], fl.FIELD_OBSERVATION)

    def test_a_ancora_de_fora_governa_a_de_dentro(self):
        """"Rischio attacchi" CONTÉM "attacchi". Pela proximidade venceria a de
        dentro, e o mapa de previsão viraria sintoma visto."""
        ok, _ = fl.localizacoes_do_fato(self.RISCO)
        self.assertEqual(ok[0]['FACT_LOCATION_ANCHOR'], 'rischio attacchi')

    def test_risco_modelado_fica_fora_da_contagem_de_ocorrencias(self):
        r = fl.ocorrencia_nao_e_incidencia([fl.MODELLED_RISK, fl.MODELLED_RISK,
                                            fl.FIELD_OBSERVATION])
        self.assertEqual(r['OBSERVED_OCCURRENCES'], 1)
        self.assertEqual(r['MODELLED_RISK_STATEMENTS'], 2)
        self.assertEqual(r['INCIDENCE'], 'NOT_KNOWN')

    def test_mutacao_sem_a_ancora_externa_o_risco_vira_observacao(self):
        salvo = fl.ANCORAS_POSITIVAS
        try:
            fl.ANCORAS_POSITIVAS = tuple((p, r) for p, r in salvo
                                         if r != fl.MODELLED_RISK)
            ok, _ = fl.localizacoes_do_fato(self.RISCO)
            self.assertEqual(ok[0]['TYPE_OF_EVIDENCE'], fl.FIELD_OBSERVATION,
                             'a mutação não mudou nada — a prova não mordia')
        finally:
            fl.ANCORAS_POSITIVAS = salvo


class OBoletimDeConsorzioAchouMaisTres(unittest.TestCase):
    """Bollettino do Consorzio Collio n.06 de 15/05/2026, assinado por um
    agrônomo nomeado. O documento mais LOCAL que esta missão leu — vinte
    localidades com chuva em mm — e o que menos localização produzia."""

    SENTINELA_POSITIVA = 'Nel testimone non trattato di Plessiva si segnalano infezioni.'
    SENTINELA_NEGATIVA = ('Al momento nel testimone non trattato di Plessiva non si '
                          'segnalano infezioni.')

    def test_1_a_parcela_sentinela_declara_o_lugar(self):
        """"testimone non trattato di Plessiva" — o agrônomo está dizendo que
        Plessiva é um lugar com parcela de monitoramento. Sem o marcador, o nome
        ficava invisível: nem aceito nem recusado."""
        ok, _ = fl.localizacoes_do_fato(self.SENTINELA_POSITIVA)
        self.assertEqual([a['FACT_LOCATION'] for a in ok], ['Plessiva'])
        self.assertEqual(ok[0]['PRECISION_SOURCE'], 'DECLARED_BY_TEXT')
        self.assertEqual(ok[0]['FACT_LOCATION_PRECISION'], fl.LOCALITY)

    def test_2_a_ancora_pode_vir_DEPOIS_do_lugar(self):
        """O italiano põe o verbo depois do lugar o tempo todo. Olhar só para
        trás recusava a frase por "falta de relação semântica" — pelo motivo
        errado."""
        ok, _ = fl.localizacoes_do_fato('A Grosseto si segnalano infezioni.')
        self.assertEqual([a['FACT_LOCATION'] for a in ok], ['Grosseto'])

    def test_olhar_para_os_dois_lados_nao_reabre_o_falso_positivo(self):
        """A âncora negativa concorre pela mesma distância."""
        ok, nao = fl.localizacoes_do_fato(
            'Convegno a Bologna e fusariosi constatata a Grosseto.')
        self.assertEqual([a['FACT_LOCATION'] for a in ok], ['Grosseto'])
        self.assertIn('Bologna', {r['PLACE'] for r in nao})

    def test_3_negacao_estrutural_nao_e_negacao_de_observacao(self):
        """"testimone NON TRATTATO" descreve a parcela — que é justamente onde a
        doença aparece primeiro. Tratar esse "non" como negação do achado
        descartaria a evidência mais precoce que existe."""
        ok, _ = fl.localizacoes_do_fato(self.SENTINELA_POSITIVA)
        self.assertTrue(ok)

    def test_mas_a_negacao_de_observacao_continua_valendo(self):
        ok, nao = fl.localizacoes_do_fato(self.SENTINELA_NEGATIVA)
        self.assertEqual(ok, [])
        self.assertEqual({r['STATE'] for r in nao}, {fl.NEGATED_OBSERVATION})

    def test_a_negacao_e_proximidade_e_nao_morfologia(self):
        """Enumerar formas verbais negadas do italiano foi um erro: "non si
        segnalano" não caía em nenhum dos padrões da primeira versão."""
        self.assertLessEqual(fl.JANELA_NEGACAO, 60)
        distante = ('Non abbiamo ancora un quadro completo della situazione '
                    'regionale in questa fase della stagione, ma a Grosseto si '
                    'segnalano infezioni.')
        ok, _ = fl.localizacoes_do_fato(distante)
        self.assertEqual([a['FACT_LOCATION'] for a in ok], ['Grosseto'],
                         'um "non" distante não pode alcançar a observação')

    def test_mutacao_sem_a_negacao_estrutural_a_sentinela_se_perde(self):
        salvo = fl.NEGACAO_ESTRUTURAL
        try:
            fl.NEGACAO_ESTRUTURAL = ()
            ok, _ = fl.localizacoes_do_fato(self.SENTINELA_POSITIVA)
            self.assertEqual(ok, [], 'a mutação não mudou nada — a prova não mordia')
        finally:
            fl.NEGACAO_ESTRUTURAL = salvo

    def test_todos_os_casos_anteriores_continuam_valendo(self):
        """As correções deste boletim não podem desfazer as dos anteriores."""
        casos = {
            'Non riscontrata presenza di avversità nei Comuni di Gubbio.': [],
            ('Fitopatie assenti ad eccezione di presenza media di Septoriosi '
             'nel Comune di Parrano.'): ['Parrano'],
            'Campioni positivi provenienti da Grosseto, Siena e Arezzo.':
                ['Grosseto', 'Siena', 'Arezzo'],
            'Operiamo in Toscana con i nostri tecnici.': [],
            'Rischio attacchi septoriosi in Friuli Venezia Giulia.':
                ['Friuli-Venezia Giulia'],
        }
        for frase, esperado in casos.items():
            ok, _ = fl.localizacoes_do_fato(frase)
            self.assertEqual([a['FACT_LOCATION'] for a in ok], esperado, frase[:50])


class OEscopoDoDocumentoEACaseFieldLeg(unittest.TestCase):
    """O boletim que é a perna de campo do CASO devolvia ZERO localizações.

    A frase que relata o sintoma — "Si segnala la comparsa di sintomi lievi nel
    frumento duro" — não nomeia lugar nenhum, porque o lugar é o documento
    inteiro: "Provincia di Grosseto - Bollettino Frumento del 2026-04-23".
    """

    DOC = ('Provincia di Grosseto - Bollettino Frumento del 2026-04-23. '
           'Fusariosi. Si segnala la comparsa di sintomi lievi nel frumento duro '
           'in alcune situazioni, mentre il tenero resta esente.')

    def test_o_escopo_do_cabecalho_e_lido(self):
        e = fl.escopo_do_documento(self.DOC)
        self.assertEqual(e['PLACE'], 'Grosseto')
        self.assertEqual(e['PRECISION'], fl.PROVINCE)

    def test_a_frase_sem_lugar_recebe_o_escopo_do_documento(self):
        ok, _ = fl.localizacoes_do_fato(self.DOC)
        self.assertEqual(len(ok), 1)
        self.assertEqual(ok[0]['FACT_LOCATION'], 'Grosseto')
        self.assertEqual(ok[0]['PRECISION_SOURCE'], fl.DOCUMENT_SCOPE)
        self.assertIn('frumento duro', ok[0]['FACT_LOCATION_EVIDENCE'])

    def test_a_precisao_e_a_do_cabecalho_e_nunca_mais_fina(self):
        """§14: não inventar município para melhorar o mapa."""
        ok, _ = fl.localizacoes_do_fato(self.DOC)
        self.assertEqual(ok[0]['FACT_LOCATION_PRECISION'], fl.PROVINCE)

    def test_o_escopo_NAO_resgata_frase_cujo_lugar_foi_recusado(self):
        """Senão o "convegno a Bologna" voltaria pela porta do cabeçalho."""
        ok, nao = fl.localizacoes_do_fato(
            'Provincia di Grosseto - Bollettino. Convegno a Bologna sulla fusariosi.')
        self.assertEqual(ok, [])
        self.assertIn('Bologna', {r['PLACE'] for r in nao})

    def test_o_escopo_nao_resgata_observacao_negada(self):
        ok, _ = fl.localizacoes_do_fato(
            'Provincia di Grosseto - Bollettino. Non si segnalano sintomi.')
        self.assertEqual(ok, [])

    def test_o_lugar_da_propria_frase_vence_o_escopo(self):
        ok, _ = fl.localizacoes_do_fato(
            'Provincia di Grosseto - Bollettino. Constatata fusariosi a Siena.')
        self.assertEqual([a['FACT_LOCATION'] for a in ok], ['Siena'])

    def test_sem_cabecalho_nao_ha_escopo(self):
        ok, _ = fl.localizacoes_do_fato(
            'Bollettino senza intestazione. Si segnala la comparsa di sintomi.')
        self.assertEqual(ok, [])

    def test_o_titulo_do_boletim_nao_e_uma_observacao(self):
        """`bollettino` era âncora, e o cabeçalho "Provincia di Grosseto -
        Bollettino Frumento" virava uma observação em Grosseto."""
        ok, _ = fl.localizacoes_do_fato(
            'Provincia di Grosseto - Bollettino Frumento. Il tempo è variabile.')
        self.assertEqual(ok, [])

    def test_uma_frase_solta_nao_e_um_documento(self):
        """Sem esta trava, a própria frase virava cabeçalho e era pulada."""
        ok, nao = fl.localizacoes_do_fato('La sede è nel Comune di Parrano.')
        self.assertEqual(ok, [])
        self.assertIn('Parrano', {r['PLACE'] for r in nao})

    def test_mutacao_sem_escopo_de_documento_o_caso_volta_a_zero(self):
        ok, _ = fl.localizacoes_do_fato(self.DOC, usar_escopo=False)
        self.assertEqual(ok, [], 'a mutação não mudou nada — a prova não mordia')


class ODataDeAcaoNaoEDataDeFato(unittest.TestCase):
    """Boletim provincial de Ancona n.615, publicado em 22/04/2026, dizia
    "si consiglia di intervenire entro lunedì 27 aprile" — e o sistema datava um
    fato observado numa data que ainda não tinha chegado."""

    def test_data_de_acao_recomendada_nao_e_tempo_do_fato(self):
        r = fl.tempo_do_fato('Si consiglia di intervenire entro lunedì 27 aprile.',
                             '2026-04-22')
        self.assertEqual(r['FACT_TIME'], 'NOT_KNOWN')
        motivos = {d['WHY'] for d in r['TIME_CANDIDATES_DISCARDED']}
        self.assertIn('PLANNED_ACTION_DATE_NOT_FACT_TIME', motivos)

    def test_nenhum_fato_observado_acontece_depois_da_publicacao(self):
        """A trava mais simples e a mais difícil de furar."""
        r = fl.tempo_do_fato('Campioni raccolti il 30 aprile 2026.', '2026-04-22')
        self.assertEqual(r['FACT_TIME'], 'NOT_KNOWN')
        motivos = {d['WHY'] for d in r['TIME_CANDIDATES_DISCARDED']}
        self.assertIn('FUTURE_DATE_NOT_FACT_TIME', motivos)

    def test_data_passada_e_ancorada_continua_valendo(self):
        r = fl.tempo_do_fato('Sintomi osservati il 20 aprile 2026.', '2026-04-22')
        self.assertEqual(r['FACT_TIME'], '20 aprile 2026')

    def test_sem_data_de_publicacao_a_trava_de_futuro_nao_inventa_recusa(self):
        r = fl.tempo_do_fato('Sintomi osservati il 30 aprile 2026.')
        self.assertEqual(r['FACT_TIME'], '30 aprile 2026')

    # A âncora e o prazo têm de estar na MESMA oração, senão a mutação "passa"
    # por outra proteção — a de que data solta não se ancora — e a prova mente
    # por excesso de defesa.
    FRASE_ACAO = ('Rilevato attacco, si consiglia di intervenire entro il '
                  '10 aprile 2026.')

    def test_com_a_lei_de_pe_o_prazo_nao_data_o_fato(self):
        self.assertEqual(fl.tempo_do_fato(self.FRASE_ACAO, '2026-04-22')['FACT_TIME'],
                         'NOT_KNOWN')

    def test_mutacao_sem_contexto_de_acao_o_prazo_vira_data_do_fato(self):
        salvo = fl.CONTEXTO_ACAO
        try:
            fl.CONTEXTO_ACAO = ()
            r = fl.tempo_do_fato(self.FRASE_ACAO, '2026-04-22')
            self.assertEqual(r['FACT_TIME'], '10 aprile 2026',
                             'a mutação não mudou nada — a prova não mordia')
        finally:
            fl.CONTEXTO_ACAO = salvo

# O `unittest.main()` estava a MEIO do ficheiro e as classes abaixo nunca eram
# recolhidas: correr `python3 tests/test_fato_local.py` dizia OK tendo corrido metade.
# Movido para o fim no PASSO 03; a contagem por pytest nao muda.

if __name__ == '__main__':
    unittest.main()
