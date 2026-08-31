"""O 0003 e medicao, nao promessa: estes testes olham o SQL que sera colado.

Nao ha Postgres nesta maquina, entao nada aqui prova que o SQL RODA. O que eles
provam e o que da para provar sem banco: que ele nao escreve fora da transacao,
que as contagens vem da autoridade e nao de memoria, que o isolamento por pais
troca de papel de verdade, e que o achado do GRANT esta escrito onde da para ler
em vez de estar escondido num comentario.

O limite fica dito: SQL_EXECUTADO = NO.
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import supabase_post_migration as pos  # noqa: E402

SQL_PATH = os.path.join(ROOT, 'supabase', 'validation', '0003_post_migration_checks.sql')
PLAN_PATH = os.path.join(ROOT, 'data', 'supabase', 'SUPABASE-POST-MIGRATION-PLAN.json')
with open(SQL_PATH, encoding='utf-8') as f:
    SQL = f.read()
with open(PLAN_PATH, encoding='utf-8') as f:
    PLANO = json.load(f)


class TestOArquivoEstaSincronizado(unittest.TestCase):
    def test_o_sql_no_disco_e_o_que_o_gerador_produz(self):
        # Editar o .sql a mao e o jeito mais facil de a medicao deixar de medir.
        self.assertEqual(SQL, pos.gerar_sql())

    def test_o_plano_no_disco_e_o_que_o_gerador_produz(self):
        self.assertEqual(PLANO, pos.medir())


class TestNaoDeixaRastro(unittest.TestCase):
    def test_comeca_em_begin_e_termina_em_rollback(self):
        self.assertTrue(SQL.lstrip().startswith('-- MEDICAO POS-MIGRATION'))
        self.assertIn('\nBEGIN;\n', SQL)
        self.assertTrue(SQL.rstrip().endswith('ROLLBACK;'))

    def test_nao_ha_commit_em_lugar_nenhum(self):
        for linha in SQL.splitlines():
            self.assertNotIn('COMMIT;', linha.split('--')[0])

    def test_o_grant_esta_dentro_da_transacao(self):
        # GRANT fora do BEGIN sobreviveria ao ROLLBACK e mudaria o DEV de verdade.
        # So conta linha executavel: o cabecalho fala de GRANT em comentario, e
        # comentario nao concede permissao nenhuma.
        antes, depois = SQL.split('\nBEGIN;\n', 1)
        for linha in antes.splitlines():
            self.assertNotIn('GRANT', linha.split('--')[0])
        self.assertIn('GRANT USAGE ON SCHEMA sintonia TO portal_reader;', depois)

    def test_o_papel_sempre_volta(self):
        # Uma medicao que deixa a sessao como portal_reader estraga as seguintes.
        self.assertEqual(SQL.count('SET LOCAL ROLE portal_reader;'),
                         SQL.count('RESET ROLE;') - 1)  # o RESET extra fecha o bloco


class TestAsContagensVemDaAutoridade(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, 'data', 'supabase',
                               'SUPABASE-CANONICAL-SCHEMA.json'), encoding='utf-8') as f:
            self.aut = json.load(f)

    def test_tabelas_views_e_rpcs_sao_os_do_json(self):
        esp = pos.esperado_da_autoridade()
        self.assertEqual(esp['TABLES'], len(self.aut['TABLES']))
        self.assertEqual(esp['VIEWS'], len(self.aut['VIEWS']))
        self.assertEqual(esp['RPCS'], len(self.aut['RPCS']))
        self.assertEqual(esp['DB_SCHEMA'], self.aut['DB_SCHEMA'])

    def test_a_contagem_sai_do_catalogo_e_nao_do_texto_do_sql(self):
        # pg_class prova que a tabela existe; contar CREATE num arquivo prova que
        # alguem digitou a palavra.
        self.assertIn('from pg_class', SQL)
        self.assertIn('from pg_policies', SQL)
        self.assertIn('relrowsecurity', SQL)

    def test_o_helper_de_rls_nao_e_contado_como_rpc(self):
        # 4 RPCs prometidos + allowed_countries() = 5 funcoes no catalogo. As duas
        # linhas existem separadas para que a diferenca nao vire suspeita de bug.
        self.assertIn("proretset = true", SQL)
        self.assertIn("proretset = false", SQL)
        self.assertIn('RLS_HELPER_FUNCTIONS', SQL)


class TestIsolamentoPorPais(unittest.TestCase):
    def test_os_tres_paises_sao_medidos(self):
        for pais in ('ES', 'IT', 'FR'):
            self.assertIn('COUNTRY_ISOLATION_%s' % pais, SQL)
            self.assertIn("SET LOCAL sintonia.countries = '%s';" % pais, SQL)

    def test_a_fixture_tem_um_objeto_por_pais(self):
        # Ver ES nao prova nada se ES for a unica linha que existe.
        for oid in ('AO-P-ES', 'AO-P-IT', 'AO-P-FR'):
            self.assertIn("'%s'" % oid, SQL)

    def test_o_teste_que_vale_e_o_que_olha_o_vizinho(self):
        self.assertIn('COUNTRY_ISOLATION_ES_NAO_VE_IT_NEM_FR', SQL)
        self.assertIn("where country in ('IT','FR')", SQL)

    def test_sem_configuracao_nao_le_nada(self):
        self.assertIn('COUNTRY_ISOLATION_DENY_BY_DEFAULT', SQL)

    def test_a_filha_herda_o_pais_da_raiz(self):
        self.assertIn('COUNTRY_ISOLATION_FILHA_HERDA_O_PAIS', SQL)
        self.assertIn('COUNTRY_ISOLATION_FILHA_NEGA_PAIS_ALHEIO', SQL)

    def test_o_papel_e_trocado_de_verdade(self):
        # Ler a policy no catalogo nao prova que ela filtra. So SET ROLE prova.
        self.assertIn('SET LOCAL ROLE portal_reader;', SQL)


class TestOAchadoDoGrantNaoEstaEscondido(unittest.TestCase):
    """A migration cria papel e politica e nao da GRANT. Isso esta medido."""

    def test_o_achado_e_uma_linha_do_resultado_e_nao_um_comentario(self):
        self.assertIn("'GRANT_PRESENTE_NA_MIGRATION', 'ACHADO', 'NO'", SQL)
        self.assertIn("has_table_privilege('portal_reader'", SQL)

    def test_o_achado_sai_no_json_do_resultado(self):
        self.assertIn("'ACHADOS'", SQL)

    def test_o_plano_diz_que_nao_foi_corrigido(self):
        a = PLANO['ACHADO_REGISTRADO']
        self.assertEqual(a['CORRIGIDO_NESTA_RODADA'], 'NO')
        self.assertEqual(a['HOJE_ESTA_COMPLETO'], 'nao')
        self.assertIn('SUPABASE-CANONICAL-SCHEMA.json', a['ONDE_SE_CORRIGE'])

    def test_o_grant_nao_entrou_na_migration(self):
        # O conserto vai para o JSON e a migration e regerada. Nao a mao, e nao
        # nesta rodada: o teste guarda o estado que foi medido e reportado.
        with open(os.path.join(ROOT, 'supabase', 'migrations',
                               '0001_initial_canonical_schema.sql'),
                  encoding='utf-8') as f:
            mig = f.read()
        self.assertNotIn('GRANT SELECT', mig)


class TestMultilingue(unittest.TestCase):
    def test_um_objeto_com_varias_representacoes(self):
        self.assertIn('MULTILINGUAL_ONE_OBJECT_MULTI_REPRESENTATION', SQL)
        self.assertIn("'1|3'", SQL)

    def test_o_texto_original_e_procurado_byte_a_byte(self):
        original = 'se ha detectado mildiu en vinedo en Andalucia'
        self.assertIn('ORIGINAL_TEXT_PRESERVED_EVIDENCE', SQL)
        # aparece na fixture (evidence e content_entity) e no esperado de cada
        # verificacao que o procura. O que importa e ser o MESMO texto sempre:
        # se o esperado fosse reescrito, o teste passaria medindo outra coisa.
        self.assertGreaterEqual(SQL.count(original), 4)
        self.assertNotIn('mildew', SQL.split('-- ── FIXTURE')[1].split('END $fx$')[0]
                         .split('original_text')[0])

    def test_a_traducao_mora_em_outra_tabela(self):
        self.assertIn('TRANSLATION_SEPARATE_TABLE', SQL)
        self.assertIn('content_translation', SQL)
        self.assertIn('content_entity', SQL)

    def test_a_lingua_da_fonte_nao_e_trocada(self):
        self.assertIn('ORIGINAL_TEXT_KEEPS_SOURCE_LANGUAGE', SQL)

    def test_o_fallback_diz_quando_caiu(self):
        self.assertIn('RPC_FALLBACK_USA_A_LINGUA_PEDIDA', SQL)
        self.assertIn('RPC_FALLBACK_CAI_PARA_EN', SQL)
        self.assertIn('RPC_NAO_INVENTA_TRADUCAO', SQL)
        self.assertIn('NO_REPRESENTATION_AVAILABLE', SQL)


class TestProveniencia(unittest.TestCase):
    def test_a_cadeia_inteira_esta_numa_consulta_so(self):
        # Se qualquer elo do meio faltar, o join morre e a contagem cai. E o ponto.
        self.assertIn('PROVENANCE_END_TO_END', SQL)
        for elo in ('attention_object', 'attention_object_evidence', 'evidence',
                    'source', 'source_snapshot', 'publish_run', 'publish_run_freeze'):
            self.assertIn(' %s ' % elo, SQL)

    def test_a_cadeia_termina_no_commit_do_h2(self):
        self.assertEqual(pos.H2_COMMIT, 'd7b289425c5e436f3ce68e367b8706e11910f43b')
        self.assertIn(pos.H2_COMMIT, SQL)
        self.assertIn('PROVENANCE_COMMIT_TEM_40_CARACTERES', SQL)
        self.assertEqual(len(pos.H2_COMMIT), 40)

    def test_o_pais_da_publicacao_nao_e_o_pais_do_fato(self):
        self.assertIn('PROVENANCE_SOURCE_LOCATION_NAO_E_FACT_LOCATION', SQL)

    def test_github_e_supabase_nao_se_misturam(self):
        self.assertIn('PROVENANCE_GITHUB_E_SUPABASE_SEPARADOS', SQL)
        self.assertIn('NEG_BACKENDS_MISTURADOS', SQL)


class TestNegativas(unittest.TestCase):
    def test_toda_negativa_espera_recusa(self):
        self.assertEqual(len(pos.NEGATIVAS), PLANO['VERIFICACOES_NEGATIVAS'])
        self.assertEqual(SQL.count("'NEGATIVA', 'RECUSADO'"), len(pos.NEGATIVAS))

    def test_cada_negativa_diz_por_que_e_proibida(self):
        for n in pos.NEGATIVAS:
            self.assertTrue(n['POR_QUE'])
            self.assertIn('-- %s' % n['POR_QUE'], SQL)

    def test_nao_ha_comando_de_transacao_dentro_de_plpgsql(self):
        # PL/pgSQL nao aceita SAVEPOINT nem ROLLBACK TO escritos a mao: levanta
        # erro de comando invalido e derruba o arquivo inteiro.
        for bloco in re.findall(r'DO \$neg\$.*?END \$neg\$;', SQL, re.S):
            self.assertNotIn('SAVEPOINT', bloco)
            self.assertNotIn('ROLLBACK', bloco)

    def test_a_linha_aceita_por_engano_e_desfeita(self):
        # Quando a insercao proibida passa, o RAISE proposital apaga a linha.
        self.assertIn("RAISE EXCEPTION 'DESFAZER_A_LINHA_QUE_NAO_DEVIA_TER_ENTRADO'", SQL)


class TestOAlvo(unittest.TestCase):
    def test_o_alvo_e_o_dev_novo(self):
        self.assertEqual(pos.DEV_PROJECT_REF, 'xhqebdweltytnghiavew')
        self.assertIn(pos.DEV_PROJECT_REF, SQL)

    def test_os_refs_recusados_estao_escritos_no_arquivo(self):
        # Quem cola o SQL le o cabecalho antes de escolher a aba do navegador.
        for ref in ('odhdwvugikjdvkapbowe', 'hvtycqsrdtmxxodwcwph'):
            self.assertIn(ref, SQL)
            self.assertIn(ref, pos.REFS_RECUSADOS)
        self.assertNotIn(pos.DEV_PROJECT_REF, pos.REFS_RECUSADOS)

    def test_o_sql_avisa_que_nao_sabe_onde_esta_rodando(self):
        self.assertIn('este SQL nao sabe onde esta rodando', SQL)


class TestOQueNaoFoiProvado(unittest.TestCase):
    def test_o_sql_nao_foi_executado_e_isso_esta_dito(self):
        self.assertFalse(PLANO['EXECUTADA'])
        self.assertIn('credencial', PLANO['POR_QUE_NAO'])

    def test_nenhum_teste_depende_do_frontend(self):
        self.assertFalse(PLANO['DEPENDE_DO_FRONTEND'])
        for palavra in ('fetch(', 'localStorage', 'window.', 'document.'):
            self.assertNotIn(palavra, SQL)

    def test_a_ordem_de_execucao_poe_o_inventario_antes_de_tudo(self):
        self.assertIn('0000', PLANO['ORDEM'][0])
        self.assertIn('0001', PLANO['ORDEM'][1])
        self.assertIn('0002', PLANO['ORDEM'][2])
        self.assertIn('0003', PLANO['ORDEM'][3])


if __name__ == '__main__':
    unittest.main()
