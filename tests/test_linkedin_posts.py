"""
Provas da leitura de posts. Nenhuma toca a rede.

A regressão central: um post lido por este arquivo NÃO pode produzir uma
localização do fato que o texto não sustente — nem herdá-la da base do autor,
nem da geotag, nem de uma menção solta.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import fato_local as fl        # noqa: E402
import linkedin_posts as lp    # noqa: E402
import linkedin_prova_busca as pb  # noqa: E402

AUTOR = {'NAME': 'Pasquale De Vita',
         'IDENTITY_STATE': pb.IDENTITY_CONFIRMED,
         'PROFILE_URL': 'https://www.linkedin.com/in/exemplo',
         'PROFILE_DECLARED_LOCATION': 'Foggia, Puglia, Italia',
         'INSTITUTION_ASKED': 'CREA Cerealicoltura e Colture Industriali'}


def ler(texto, **extra):
    p = {'content': texto, 'postedAt': '2026-04-20T10:00:00', 'linkedinUrl': 'x'}
    p.update(extra)
    return lp.ler_post(p, AUTOR)


class ALocalizacaoNaoVazaDeUmaEspecieParaOutra(unittest.TestCase):

    def test_a_base_do_autor_nunca_vira_local_do_fato(self):
        """O autor declara Foggia. O post fala de Grosseto. Foggia nao entra."""
        r = ler('Fusariosi constatata a Grosseto su grano duro.')
        self.assertEqual([f['FACT_LOCATION'] for f in r['FACT_LOCATIONS']],
                         ['Grosseto'])
        self.assertIn('Foggia', r['AUTHOR_BASE']['PROFILE_DECLARED_LOCATION'])
        self.assertEqual(r['AUTHOR_BASE']['FACT_LOCATION'], 'NOT_KNOWN')
        self.assertEqual(r['AUTHOR_BASE']['PLACE_KIND'], fl.BASE)

    def test_um_post_sem_ancora_nao_produz_local_do_fato_nenhum(self):
        r = ler('Bella giornata a Bologna con i colleghi.')
        self.assertEqual(r['FACT_LOCATIONS'], [])
        self.assertEqual(r['FACT_LOCATIONS_COUNT'], 0)
        self.assertTrue(r['PLACE_MENTIONS_REJECTED'])

    def test_a_geotag_e_preservada_e_nao_promovida(self):
        r = ler('Fusariosi.', geo='Grosseto, Toscana')
        self.assertEqual(r['CONTENT_GEO_EVIDENCE']['PLACE_KIND'],
                         fl.CONTENT_GEO_EVIDENCE)
        self.assertEqual(r['CONTENT_GEO_EVIDENCE']['FACT_LOCATION'], 'NOT_KNOWN')
        self.assertEqual(r['FACT_LOCATIONS'], [])

    def test_post_sem_geotag_nao_inventa_uma(self):
        self.assertIsNone(ler('Fusariosi.')['CONTENT_GEO_EVIDENCE'])

    def test_varios_locais_do_fato_num_unico_post(self):
        r = ler('Campioni positivi provenienti da Grosseto, Siena e Arezzo.')
        self.assertEqual({f['FACT_LOCATION'] for f in r['FACT_LOCATIONS']},
                         {'Grosseto', 'Siena', 'Arezzo'})
        for f in r['FACT_LOCATIONS']:
            self.assertEqual(f['TYPE_OF_EVIDENCE'], fl.DIAGNOSTIC_SAMPLE)

    def test_cada_local_aceito_carrega_o_trecho_e_a_origem(self):
        r = ler('Sintomi osservati in Toscana su frumento duro.')
        f = r['FACT_LOCATIONS'][0]
        self.assertEqual(f['FACT_LOCATION_ORIGIN'], 'POST_TEXT')
        self.assertIn('Toscana', f['FACT_LOCATION_EVIDENCE'])
        self.assertIn(f['FACT_LOCATION_PRECISION'], fl.PRECISOES)


class OTempoDoFatoNaoHerdaAPublicacao(unittest.TestCase):

    def test_sem_evidencia_temporal_o_fato_fica_sem_data(self):
        r = ler('Fusariosi constatata a Grosseto.')
        self.assertEqual(r['PUBLISHED_AT'], '2026-04-20')
        self.assertEqual(r['FACT_TIME'], 'NOT_KNOWN')

    def test_com_evidencia_temporal_os_dois_campos_convivem(self):
        r = ler('Constatata a Grosseto la settimana scorsa.')
        self.assertEqual(r['PUBLISHED_AT'], '2026-04-20')
        self.assertEqual(r['FACT_TIME_PRECISION'], fl.WEEK)
        self.assertNotEqual(r['FACT_TIME'], r['PUBLISHED_AT'])


class OEstadoDaIdentidadeViajaComOPost(unittest.TestCase):

    def test_todo_post_carrega_o_estado_de_identidade_do_autor(self):
        r = ler('Fusariosi a Grosseto constatata.')
        self.assertEqual(r['AUTHOR_IDENTITY_STATE'], pb.IDENTITY_CONFIRMED)

    def test_so_entra_autor_com_identidade_resolvida(self):
        ident = {
            'A': {'STATE': pb.IDENTITY_CONFIRMED, 'INSTITUTION_ASKED': 'CREA',
                  'BY_CANDIDATE': [{'IDENTITY_STATE': pb.IDENTITY_CONFIRMED,
                                    'PROFILE_URL': 'https://x/1'}]},
            'B': {'STATE': pb.IDENTITY_NOT_ENOUGH, 'INSTITUTION_ASKED': 'X',
                  'BY_CANDIDATE': [{'IDENTITY_STATE': pb.IDENTITY_NOT_ENOUGH,
                                    'PROFILE_URL': 'https://x/2'}]},
            'C': {'STATE': pb.IDENTITY_MISMATCH, 'INSTITUTION_ASKED': 'Y',
                  'BY_CANDIDATE': [{'IDENTITY_STATE': pb.IDENTITY_MISMATCH,
                                    'PROFILE_URL': 'https://x/3'}]},
        }
        nomes = [a['NAME'] for a in lp.autores_elegiveis(ident)]
        self.assertEqual(nomes, ['A'])

    def test_escolhe_o_candidato_do_estado_que_resolveu_e_nao_o_primeiro(self):
        """Ordenar por posicao na lista foi o defeito original desta missao."""
        ident = {'A': {'STATE': pb.IDENTITY_CONFIRMED, 'INSTITUTION_ASKED': 'CREA',
                       'BY_CANDIDATE': [
                           {'IDENTITY_STATE': pb.IDENTITY_MISMATCH,
                            'PROFILE_URL': 'https://x/errado'},
                           {'IDENTITY_STATE': pb.IDENTITY_CONFIRMED,
                            'PROFILE_URL': 'https://x/certo'}]}}
        self.assertEqual(lp.autores_elegiveis(ident)[0]['PROFILE_URL'],
                         'https://x/certo')

    def test_candidato_sem_url_utilizavel_nao_entra(self):
        ident = {'A': {'STATE': pb.IDENTITY_CONFIRMED, 'INSTITUTION_ASKED': 'CREA',
                       'BY_CANDIDATE': [{'IDENTITY_STATE': pb.IDENTITY_CONFIRMED,
                                         'PROFILE_URL': 'NÃO SEI'}]}}
        self.assertEqual(lp.autores_elegiveis(ident), [])


class AJanelaEDoCasoENaoDaFonte(unittest.TestCase):

    def test_o_limite_pedido_ao_ator_cobre_a_janela_inteira(self):
        """"6months" hoje cortaria janeiro e fevereiro em silencio."""
        self.assertEqual(lp.POSTED_LIMIT, 'year')

    def test_a_entrada_conferida_e_a_executada_sao_a_mesma_funcao(self):
        with open(lp.__file__, encoding='utf-8') as fh:
            fonte = fh.read()
        self.assertIn('modelo = entrada_de([autores[0]', fonte)
        self.assertIn('entrada = entrada_de([autor[', fonte)

    def test_o_teto_de_posts_esta_no_codigo(self):
        self.assertLessEqual(lp.TETO_POSTS, 80)
        self.assertLessEqual(lp.TETO_AUTORES, 8)


class OVereditoNaoUltrapassaOMedido(unittest.TestCase):

    def _medir(self, posts, nao_perguntados=()):
        return lp.medir(posts, [AUTOR], {'Pasquale De Vita': {'STATE': 'X'}},
                        nao_perguntados=nao_perguntados)

    def test_com_autor_por_perguntar_o_painel_nao_conclui(self):
        """O silencio de quem nao foi perguntado e meu, nao dele.

        Foi exatamente isto que aconteceu na primeira coleta: um autor sem posts
        parou a fila, tres nunca foram perguntados, e o veredito saiu dizendo
        que as vozes humanas nao acrescentam nada.
        """
        r = self._medir([], nao_perguntados=['B', 'C', 'D'])
        self.assertEqual(r['HUMAN_SENSOR_VERDICT'], 'PANEL_INCOMPLETE_CANNOT_CONCLUDE')
        self.assertEqual(r['AUTHORS_NOT_ASKED'], ['B', 'C', 'D'])

    def test_sem_ninguem_por_perguntar_o_zero_pode_ser_afirmado(self):
        r = self._medir([], nao_perguntados=[])
        self.assertEqual(r['HUMAN_SENSOR_VERDICT'],
                         'HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL')

    def test_zero_sinal_nao_vira_as_vozes_nao_servem(self):
        r = self._medir([])
        self.assertEqual(r['HUMAN_SENSOR_VERDICT'],
                         'HUMAN_SENSOR_ADDS_NOTHING_IN_THIS_PANEL')
        self.assertIn('não é', r['VERDICT_MUST_CARRY']['ZERO_IS_NOT_ABSENCE'])

    def test_achado_depois_do_caso_e_contexto_e_nunca_antecedencia(self):
        r = self._medir([ler('Fusariosi sul grano duro constatata a Grosseto.',
                             postedAt='2026-05-20T10:00:00')])
        self.assertEqual(r['HUMAN_SENSOR_VERDICT'],
                         'HUMAN_SENSOR_ADDS_CONTEXT_NOT_ANTICIPATION')
        self.assertEqual(r['EXACT_BEFORE_CASE'], 0)

    def test_achado_antes_do_caso_e_antecedencia(self):
        r = self._medir([ler('Fusariosi sul grano duro constatata a Grosseto.',
                             postedAt='2026-03-20T10:00:00')])
        self.assertEqual(r['HUMAN_SENSOR_VERDICT'], 'HUMAN_SENSOR_ADDS_ANTICIPATION')
        self.assertEqual(r['EXACT_BEFORE_CASE'], 1)

    def test_ocorrencia_medida_nunca_vira_incidencia(self):
        r = self._medir([ler('Campioni positivi provenienti da Grosseto e Siena.',
                             postedAt='2026-03-20T10:00:00')])
        o = r['OCCURRENCE_NOT_INCIDENCE']
        self.assertEqual(o['INCIDENCE'], 'NOT_KNOWN')
        self.assertEqual(o['REGIONAL_PRESSURE'], 'NOT_KNOWN')
        self.assertEqual(o['BY_TYPE_OF_EVIDENCE'][fl.DIAGNOSTIC_SAMPLE], 2)

    def test_o_veredito_carrega_o_que_nao_foi_medido(self):
        r = self._medir([])
        deve = r['VERDICT_MUST_CARRY']
        self.assertIn('Instagram', deve['NOT_MEASURED'])
        self.assertIn('FACT_LOCATION', deve['LOCATION_RULE'])
        for proibido in ('ITALY OPPORTUNITY', 'ADAMA SHOULD ACT'):
            self.assertIn(proibido, deve['STILL_FORBIDDEN'])
