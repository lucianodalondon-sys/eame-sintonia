"""
Provas do mapa de portas e dos três vereditos.

O risco desta rodada não é errar um número: é fundir os vereditos. "O LinkedIn
rendeu pouco" e "pesquisadores não servem como sensores" são afirmações
diferentes, e a segunda é falsa. Estas provas existem para que a distinção não
se perca numa edição distraída.
"""
import datetime
import hashlib
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import fato_local as fl              # noqa: E402
import italia_portas_sensores as ps  # noqa: E402


class OsTresVereditosSaoIndependentes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.M = ps.medir()

    def test_o_linkedin_ruim_nao_condena_a_camada(self):
        self.assertEqual(self.M['LINKEDIN_SENSOR_CAPABILITY'], 'LOW_IN_MEASURED_PANEL')
        self.assertNotEqual(self.M['RESEARCHER_SENSOR_CAPABILITY'], 'NOT_PROVED')
        self.assertNotEqual(self.M['HUMAN_SENSOR_LAYER'], 'NOT_PROVED')

    def test_os_tres_vereditos_existem_separados(self):
        for chave in ('LINKEDIN_SENSOR_CAPABILITY', 'RESEARCHER_SENSOR_CAPABILITY',
                      'HUMAN_SENSOR_LAYER'):
            self.assertIn(chave, self.M)
        self.assertEqual(len({self.M['LINKEDIN_SENSOR_CAPABILITY'],
                              self.M['RESEARCHER_SENSOR_CAPABILITY'],
                              self.M['HUMAN_SENSOR_LAYER']}), 3)

    def test_a_lei_que_separa_os_dois_esta_declarada(self):
        self.assertIn('LINKEDIN_NOT_PRODUCTIVE_IN_MEASURED_PANEL '
                      '≠ HUMAN_SENSOR_LAYER_NOT_PRODUCTIVE', self.M['LAWS'])

    def test_a_camada_so_chega_a_ADDS_DECISION_VALUE_com_sinal_exato(self):
        """Controle positivo em OUTRO par cultura×problema nao promove a camada."""
        self.assertEqual(self.M['EXACT_CASE_SIGNAL'], ps.NOT_OBSERVED)
        self.assertEqual(self.M['HUMAN_SENSOR_LAYER'], 'PROMISING_BUT_NOT_PROVED')
        self.assertTrue(self.M['CONTROL_POSITIVE'])


class PublicarAntesNaoEAvisarAntes(unittest.TestCase):
    """A reportagem saiu dez semanas antes do caso — e fala da safra passada."""

    def test_o_controle_positivo_e_retrospectivo_e_nao_antecipacao(self):
        m = ps.medir()
        art = next(L for L in m['CONTENTS_READ'] if L['ID'] == 'AGRONOTIZIE/88873')
        self.assertEqual(art['PUBLICATION_RELATIVE_TO_CASE'], 'BEFORE_CASE')
        self.assertEqual(art['EARLY_WARNING_STATE'], 'RETROSPECTIVE_FINDING')
        self.assertEqual(art['TIME']['FACT_TIME'], 'stagione 2025')

    def test_publicado_depois_do_caso_nunca_e_antecipacao(self):
        pos, aviso, _ = ps.antecipa('2026-05-13', {'FACT_TIME': 'stagione 2026',
                                                   'FACT_TIME_PRECISION': fl.SEASON})
        self.assertEqual(pos, 'AFTER_CASE')
        self.assertEqual(aviso, 'NOT_EARLY_WARNING')

    def test_sem_tempo_do_fato_nao_se_afirma_antecipacao(self):
        _, aviso, _ = ps.antecipa('2026-02-13', {'FACT_TIME': 'NOT_KNOWN'})
        self.assertEqual(aviso, 'NOT_EARLY_WARNING')

    def test_fato_datado_na_estacao_corrente_pode_ser_candidato(self):
        _, aviso, _ = ps.antecipa('2026-04-10', {'FACT_TIME': 'la settimana scorsa',
                                                 'FACT_TIME_PRECISION': fl.WEEK})
        self.assertEqual(aviso, 'CANDIDATE_EARLY_WARNING')

    def test_mutacao_se_a_precisao_do_tempo_for_ignorada_o_retrospectivo_vira_aviso(self):
        """A prova de que é a PRECISÃO do tempo do fato que segura a distinção.

        Sem ela, um relatório sobre a safra encerrada contaria como aviso
        precoce — que é exatamente o erro que a lei proíbe.
        """
        _, aviso, _ = ps.antecipa('2026-02-13', {'FACT_TIME': 'stagione 2025',
                                                 'FACT_TIME_PRECISION': fl.SEASON})
        self.assertEqual(aviso, 'RETROSPECTIVE_FINDING')
        _, mutado, _ = ps.antecipa('2026-02-13', {'FACT_TIME': 'stagione 2025',
                                                  'FACT_TIME_PRECISION': fl.DAY})
        self.assertEqual(mutado, 'CANDIDATE_EARLY_WARNING',
                         'a mutação não mudou nada — a prova não estava mordendo')


class AEvidenciaLidaEstaPreservada(unittest.TestCase):

    def test_o_controle_positivo_tem_arquivo_e_hash_que_conferem(self):
        m = ps.medir()
        art = next(L for L in m['CONTENTS_READ'] if L['ID'] == 'AGRONOTIZIE/88873')
        self.assertEqual(art['EVIDENCE_STATE'], 'PRESERVED')
        caminho = os.path.join(RAIZ, art['EVIDENCE_PATH'])
        with open(caminho, 'rb') as fh:
            self.assertEqual(hashlib.sha256(fh.read()).hexdigest(),
                             art['SHA256_TEXTO'])

    def test_o_texto_preservado_sustenta_o_que_o_artefato_afirma(self):
        m = ps.medir()
        art = next(L for L in m['CONTENTS_READ'] if L['ID'] == 'AGRONOTIZIE/88873')
        with open(os.path.join(RAIZ, art['EVIDENCE_PATH']), encoding='utf-8') as fh:
            texto = fh.read()
        self.assertIn('Sabrina Locatelli', texto)
        self.assertIn('Giornata del Mais', texto)
        self.assertIn('72%', texto)
        self.assertIn('stagione 2025', texto)

    def test_conteudo_lido_mas_nao_preservado_e_dito_e_nao_escondido(self):
        m = ps.medir()
        estados = {L['ID']: L['EVIDENCE_STATE'] for L in m['CONTENTS_READ']}
        self.assertEqual(estados['CREA/DURUM-DAYS-2026'], 'READ_NOT_PRESERVED')


class ONaoEncontradoNaoViraInexistente(unittest.TestCase):

    def test_pesquisador_sem_canal_achado_fica_NOT_FOUND_IN_THIS_SEARCH(self):
        sem = [p for p in ps.PORTAS
               if p['PRIMARY_PUBLIC_CHANNEL'] == 'NOT_FOUND_IN_THIS_SEARCH']
        self.assertEqual(len(sem), 2)
        for p in sem:
            self.assertEqual(p['DATED_CONTENT_AVAILABLE'], 'NOT_KNOWN')
            self.assertNotIn('NOT_EXIST', json.dumps(p, ensure_ascii=False))

    def test_a_lei_esta_declarada_e_o_que_falta_medir_esta_nomeado(self):
        m = ps.medir()
        self.assertIn('NOT_FOUND_IN_THIS_SEARCH ≠ DOES_NOT_EXIST', m['LAWS'])
        falta = m['RECOMMENDATION']['STILL_UNMEASURED']
        self.assertIn('Nocente', falta)
        self.assertIn('Pacifico', falta)

    def test_todo_pesquisador_do_painel_tem_uma_linha(self):
        nomes = {p['RESEARCHER'] for p in ps.PORTAS}
        for esperado in ('Sabrina Locatelli', 'Pasquale De Vita', 'Nicola Pecchioni',
                         'Francesca Nocente', 'Daniela Pacifico'):
            self.assertIn(esperado, nomes)


class ALocalizacaoDoFatoNaoFoiForcada(unittest.TestCase):

    def test_zero_localizacao_de_fato_e_o_resultado_e_esta_explicado(self):
        m = ps.medir()
        self.assertEqual(m['FACT_LOCATIONS_COUNT'], 0)
        self.assertTrue(m['FACT_LOCATION'].startswith('NOT_KNOWN'))
        porque = m['WHY_NO_FACT_LOCATION']
        for esperado in ('Bergamo', 'Torino', 'Piacenza', 'Ovest'):
            self.assertIn(esperado, porque)

    def test_as_mencoes_recusadas_ficam_registradas_com_o_motivo(self):
        m = ps.medir()
        art = next(L for L in m['CONTENTS_READ'] if L['ID'] == 'AGRONOTIZIE/88873')
        recusadas = {r['PLACE'] for r in art['PLACE_MENTIONS_REJECTED']}
        self.assertIn('Torino', recusadas)
        self.assertIn('Bergamo', recusadas)

    def test_a_sede_do_crea_nao_virou_local_do_fato(self):
        """Bergamo aparece TRES vezes no artigo, com tres papeis diferentes:
        "sede di Bergamo", "presentati proprio a Bergamo" e "Giornata del Mais di
        Bergamo". Cada mencao e julgada por si — guardar so uma esconderia que a
        mesma cidade pode ser recusada por motivos distintos na mesma pagina.
        """
        m = ps.medir()
        art = next(L for L in m['CONTENTS_READ'] if L['ID'] == 'AGRONOTIZIE/88873')
        motivos = [r['WHY'] for r in art['PLACE_MENTIONS_REJECTED']
                   if r['PLACE'] == 'Bergamo']
        self.assertGreaterEqual(len(motivos), 3)
        self.assertIn('endereço da entidade', motivos)
        # e, acima de tudo: nunca aceita
        self.assertNotIn('Bergamo', [a['FACT_LOCATION'] for a in art['FACT_LOCATIONS']])

    def test_amostra_de_diagnostico_nao_virou_incidencia(self):
        m = ps.medir()
        art = next(L for L in m['CONTENTS_READ'] if L['ID'] == 'AGRONOTIZIE/88873')
        o = art['OCCURRENCE_NOT_INCIDENCE']
        self.assertEqual(o['INCIDENCE'], 'NOT_KNOWN')
        self.assertEqual(o['REGIONAL_PRESSURE'], 'NOT_KNOWN')


class OAchadoEstruturalEstaRegistrado(unittest.TestCase):

    def test_o_calendario_do_pesquisador_e_retrospectivo_por_construcao(self):
        m = ps.medir()['STRUCTURAL_FINDING']
        self.assertEqual(m['STATE'], 'RESEARCHER_CHANNEL_IS_RETROSPECTIVE_BY_CALENDAR')
        self.assertIn('30/01', m['EVIDENCE'])
        self.assertIn('19/05', m['EVIDENCE'])
        self.assertIn('abril', m['EVIDENCE'])

    def test_o_que_o_canal_serve_e_o_que_nao_serve_estao_ambos_ditos(self):
        m = ps.medir()['STRUCTURAL_FINDING']
        self.assertTrue(m['WHAT_IT_IS_GOOD_FOR'])
        self.assertIn('safra que está correndo', m['WHAT_IT_CANNOT_DO'])

    def test_a_recomendacao_nao_manda_reabrir_o_linkedin(self):
        r = ps.medir()['RECOMMENDATION']
        self.assertIn('LinkedIn', r['DO_NOT_COLLECT'])
        self.assertNotIn('LinkedIn', r['COLLECT'])

    def test_nenhuma_palavra_proibida_aparece_fora_da_lista(self):
        m = ps.medir()
        corpo = json.dumps({k: v for k, v in m.items()
                            if k != 'STILL_FORBIDDEN_TO_WRITE'}, ensure_ascii=False)
        for p in m['STILL_FORBIDDEN_TO_WRITE']:
            self.assertNotIn(p, corpo, p)

    def test_nenhuma_execucao_paga_nesta_rodada(self):
        m = ps.medir()
        self.assertEqual(m['APIFY_RUNS'], 0)
        self.assertEqual(m['APIFY_COST_USD'], 0)
