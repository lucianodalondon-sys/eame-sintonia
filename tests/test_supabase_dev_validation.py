"""Provas da correcao de alvo DEV e da bateria de validacao.

O que esta rodada aprendeu, e que estas provas guardam: vazio de dado NAO e limpo
de schema. Uma branch com 0 linha e 51 tabelas herdadas passou pelo meu
classificador. Nao passa mais.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))

import supabase_dev_target as alvo          # noqa: E402
import supabase_dev_validation as val       # noqa: E402

BRANCH_INV = {'EXISTING_SCHEMAS': ['public'], 'EXISTING_TABLES': [],
              'EXISTING_USER_DATA': [], 'AUTH_USERS': 0, 'STORAGE_OBJECTS': 0}
BRANCH_INV.update(alvo.BRANCH['MEDIDO'])   # a medicao real manda sobre o esqueleto
LIMPO = {'EXISTING_SCHEMAS': ['public'], 'EXISTING_TABLES': [], 'EXISTING_USER_DATA': [],
         'AUTH_USERS': 0, 'STORAGE_OBJECTS': 0, 'PUBLIC_TABLES': 0,
         'PUBLIC_VIEWS': 0, 'PUBLIC_FUNCTIONS': 0}


class TestBranchMedida(unittest.TestCase):
    def test_branch_registrada_com_o_ref(self):
        self.assertEqual(alvo.BRANCH['DEV_BRANCH_REF'], 'hvtycqsrdtmxxodwcwph')
        self.assertEqual(alvo.BRANCH['PARENT_PROJECT_REF'], 'odhdwvugikjdvkapbowe')

    def test_nao_verifiquei_eu(self):
        self.assertFalse(alvo.BRANCH['VERIFICADO_POR_MIM'])

    def test_os_tres_vereditos_da_branch(self):
        self.assertEqual(alvo.BRANCH['DEV_BRANCH_DATA_EMPTY'], 'YES')
        self.assertEqual(alvo.BRANCH['DEV_BRANCH_SCHEMA_CLEAN'], 'NO')
        self.assertEqual(alvo.BRANCH['DEV_BRANCH_SAFE_FOR_CANONICAL_MIGRATION'], 'NO')

    def test_dado_vazio_nao_virou_schema_limpo(self):
        # o erro exato desta rodada, em uma linha
        self.assertNotEqual(alvo.BRANCH['DEV_BRANCH_DATA_EMPTY'],
                            alvo.BRANCH['DEV_BRANCH_SCHEMA_CLEAN'])

    def test_o_que_nao_fazer_esta_escrito(self):
        texto = ' '.join(alvo.BRANCH['O_QUE_NAO_FAZER']).lower()
        for proibido in ('migration', 'limpar', 'drop', 'parent'):
            self.assertIn(proibido, texto)


class TestClassificadorCorrigido(unittest.TestCase):
    def test_branch_nao_e_mais_YES(self):
        # antes desta rodada, isto devolvia YES. Era o bug.
        c = alvo.classificar(BRANCH_INV)
        self.assertNotEqual(c['SAFE_TO_USE_AS_DEV'], 'YES')

    def test_duas_perguntas_separadas(self):
        c = alvo.classificar(BRANCH_INV)
        self.assertEqual(c['DATA_EMPTY'], 'YES')
        self.assertEqual(c['SCHEMA_CLEAN'], 'NO')

    def test_migration_exige_as_duas(self):
        c = alvo.classificar(BRANCH_INV)
        self.assertEqual(c['SAFE_FOR_CANONICAL_MIGRATION'], 'NO')

    def test_banco_limpo_continua_passando(self):
        c = alvo.classificar(LIMPO)
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'YES')
        self.assertEqual(c['SAFE_FOR_CANONICAL_MIGRATION'], 'YES')

    def test_tabela_em_public_e_motivo_de_schema_nao_de_dado(self):
        c = alvo.classificar(BRANCH_INV)
        self.assertEqual(c['MOTIVOS_DE_BLOQUEIO'], [])
        self.assertTrue(any('public' in m for m in c['MOTIVOS_DE_SCHEMA']))

    def test_schema_migracao_e_motivo(self):
        c = alvo.classificar(BRANCH_INV)
        self.assertTrue(any('schema_migracao' in m for m in c['MOTIVOS_DE_SCHEMA']))

    def test_parent_continua_reprovado_por_dado(self):
        c = alvo.classificar(alvo.INVENTARIO_MEDIDO)
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NO')
        self.assertEqual(c['DATA_EMPTY'], 'NO')

    def test_sem_inventario_continua_needs_decision(self):
        self.assertEqual(alvo.classificar(None)['SAFE_TO_USE_AS_DEV'], 'NEEDS_DECISION')


class TestPortao(unittest.TestCase):
    def test_os_dois_refs_estao_recusados(self):
        self.assertIn('odhdwvugikjdvkapbowe', alvo.REFS_RECUSADOS)
        self.assertIn('hvtycqsrdtmxxodwcwph', alvo.REFS_RECUSADOS)

    def test_portao_recusa_a_branch_pelo_ref(self):
        r = alvo.preparar_aplicacao(LIMPO, 'hvtycqsrdtmxxodwcwph')
        self.assertFalse(r['PODE_APLICAR'])
        self.assertTrue(any('recusados' in x for x in r['RECUSAS']))

    def test_portao_recusa_o_parent_pelo_ref(self):
        r = alvo.preparar_aplicacao(LIMPO, 'odhdwvugikjdvkapbowe')
        self.assertFalse(r['PODE_APLICAR'])

    def test_portao_recusa_sem_ref(self):
        r = alvo.preparar_aplicacao(LIMPO, None)
        self.assertFalse(r['PODE_APLICAR'])

    def test_ref_limpo_so_esbarra_na_credencial(self):
        r = alvo.preparar_aplicacao(LIMPO, 'ref-novo-limpo')
        self.assertFalse(r['PODE_APLICAR'])
        self.assertEqual(len(r['RECUSAS']), 1)
        self.assertIn('credencial', r['RECUSAS'][0])


class TestEstrategia(unittest.TestCase):
    def test_estrategia_virou_projeto_novo(self):
        self.assertEqual(alvo.DEV_TARGET['DEV_TARGET_STRATEGY'], 'NEW_PROJECT')

    def test_nada_foi_criado(self):
        self.assertEqual(alvo.DEV_TARGET['DEV_TARGET_CREATED'], 'NO')
        self.assertIsNone(alvo.DEV_TARGET['DEV_PROJECT_REF'])


class TestBateriaDeValidacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = val.gerar_sql()
        cls.m = val.medir()

    def test_nao_ha_alvo_fixo_no_codigo(self):
        self.assertIsNone(val.DEV_REF)

    def test_o_ref_da_branch_so_aparece_como_recusa(self):
        self.assertIn('hvtycqsrdtmxxodwcwph', val.REFS_RECUSADOS)
        # e no SQL, so dentro do bloco de recusados
        for linha in self.sql.split('\n'):
            if 'hvtycqsrdtmxxodwcwph' in linha:
                self.assertTrue(linha.strip().startswith('--'), linha)

    def test_abre_e_fecha_desfazendo(self):
        self.assertIn('BEGIN;', self.sql)
        self.assertTrue(self.sql.rstrip().endswith('ROLLBACK;'))
        self.assertNotIn('COMMIT;', self.sql)

    def test_toda_negativa_espera_recusa(self):
        for nome, _, _ in val.NEGATIVAS:
            self.assertIn("'%s', 'NEGATIVA', 'RECUSADO', 'ACEITO', 'FAIL'" % nome,
                          self.sql)
            self.assertIn("'%s', 'NEGATIVA', 'RECUSADO', SQLERRM, 'PASS'" % nome,
                          self.sql)

    def test_as_leis_que_o_briefing_nomeou_estao_na_bateria(self):
        nomes = {n for n, _, _ in val.NEGATIVAS}
        for lei in ('EXPIRY_NE_WITHDRAWAL', 'PRAZO_NAO_AUTORIZA_BUSINESS_DECISION',
                    'MEDIA_EXIGE_N', 'LOCALITY_TEXT_NAO_E_POINT',
                    'DEPENDENTE_DECLARA_ALVO', 'INDEPENDENTE_NAO_TEM_ALVO',
                    'PUBLICADO_EXIGE_SOMBRA', 'BACKENDS_NAO_SE_MISTURAM',
                    'GDPR_ANTES_DA_IDENTIDADE', 'PORTFOLIO_E_SEMPRE_CONTEXTO'):
            self.assertIn(lei, nomes)

    def test_traco_nunca_e_lingua(self):
        self.assertIn('SOURCE_LANGUAGE_NAO_ACEITA_TRACO',
                      {n for n, _, _ in val.NEGATIVAS})

    def test_contagens_batem_com_o_schema(self):
        with open(os.path.join(RAIZ, 'data', 'supabase',
                               'SUPABASE-CANONICAL-SCHEMA.json'), encoding='utf-8') as fh:
            d = json.load(fh)
        e = self.m['ESPERADO_DO_SCHEMA']
        self.assertEqual(e['TABLES'], len(d['TABLES']))
        self.assertEqual(e['VIEWS'], len(d['VIEWS']))
        self.assertEqual(e['RPCS'], len(d['RPCS']) + 1)   # +1: allowed_countries()

    def test_positiva_de_tabela_espera_o_numero_do_schema(self):
        esperados = {n: e for n, e, _ in val.POSITIVAS}
        self.assertEqual(esperados['TABLES_ACTUAL'], 57)
        self.assertEqual(esperados['VIEWS_ACTUAL'], 13)
        self.assertEqual(esperados['RLS_ENABLED_ALL'], 57)

    def test_pais_isolado_nos_tres(self):
        nomes = {n for n, _, _ in val.POSITIVAS}
        for pais in ('ES', 'IT', 'FR'):
            self.assertIn('COUNTRY_ISOLATION_%s' % pais, nomes)

    def test_multilingue_um_objeto_cinco_linguas(self):
        esperados = {n: e for n, e, _ in val.POSITIVAS}
        self.assertEqual(esperados['MULTILINGUAL_ONE_OBJECT'], 1)
        self.assertEqual(esperados['MULTILINGUAL_FIVE_LANGUAGES'], 5)

    def test_original_nao_entra_na_cadeia_de_fallback(self):
        esperados = {n: e for n, e, _ in val.POSITIVAS}
        self.assertEqual(esperados['ORIGINAL_PRESERVED'], 'texto original em espanhol')

    def test_proveniencia_chega_no_commit_do_H2(self):
        esperados = {n: e for n, e, _ in val.POSITIVAS}
        self.assertEqual(esperados['PROVENANCE_REACHES_COMMIT'],
                         'd7b289425c5e436f3ce68e367b8706e11910f43b')

    def test_porta_fechada_por_padrao(self):
        esperados = {n: e for n, e, _ in val.POSITIVAS}
        self.assertEqual(esperados['ALLOWED_COUNTRIES_DENIES_BY_DEFAULT'], 0)

    def test_uma_perna_nao_e_convergencia(self):
        esperados = {n: e for n, e, _ in val.POSITIVAS}
        self.assertEqual(esperados['CONVERGENCE_SINGLE_SIGNAL'], 'SINGLE_SIGNAL')

    def test_nao_foi_executada(self):
        self.assertFalse(self.m['EXECUTADA'])

    def test_inventario_vem_antes_da_migration(self):
        self.assertIn('inventory', self.m['ORDEM'][0])
        self.assertIn('migrations', self.m['ORDEM'][1])
        self.assertIn('validation', self.m['ORDEM'][2])

    def test_arquivo_gravado_bate_com_o_gerador(self):
        with open(os.path.join(RAIZ, 'supabase', 'validation',
                               '0002_dev_validation.sql'), encoding='utf-8') as fh:
            self.assertEqual(fh.read(), self.sql)

    def test_sem_segredo_no_sql(self):
        import re
        achados = re.findall(r'eyJ[A-Za-z0-9_-]{20,}', self.sql)
        self.assertEqual(achados, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
