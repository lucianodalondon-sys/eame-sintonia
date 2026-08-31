# -*- coding: utf-8 -*-
"""Provas da resolucao do alvo DEV.

A correcao desta rodada e de SEMANTICA: existir projeto e eu conseguir ve-lo sao
coisas diferentes, e eu tinha misturado as duas. Estas provas travam a separacao e
o classificador — inclusive a regra que importa mais: nunca devolver YES por
ausencia de informacao.

Zero rede. Nenhuma conexao com o projeto: nao ha credencial, e credencial nao e
coisa que eu deva manusear.
"""
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from supabase_dev_target import (  # noqa: E402
    INVENTARIO, PROJETO, SCHEMAS_DE_SISTEMA, acesso_local, classificar,
    gerar_inventario_sql, medir, preparar_aplicacao,
)

SUP = os.path.join(ROOT, 'data', 'supabase')
with open(os.path.join(SUP, 'SUPABASE-DEV-TARGET.json'), encoding='utf-8') as f:
    ALVO = json.load(f)
INV_SQL_PATH = os.path.join(ROOT, 'supabase', 'inventory', '0000_readonly_inventory.sql')
with open(INV_SQL_PATH, encoding='utf-8') as f:
    INV_SQL = f.read()

VAZIO = {'EXISTING_SCHEMAS': ['public', 'auth', 'storage', 'extensions'],
         'EXISTING_TABLES': [], 'EXISTING_VIEWS': [], 'EXISTING_FUNCTIONS': [],
         'EXISTING_RLS_POLICIES': [], 'EXISTING_USER_DATA': [],
         'EXISTING_MIGRATION_HISTORY': None, 'AUTH_USERS': 0, 'STORAGE_OBJECTS': 0}


def com(**mudanca):
    d = json.loads(json.dumps(VAZIO))
    d.update(mudanca)
    return d


class TestSemantica(unittest.TestCase):

    def test_as_tres_coisas_sao_separadas(self):
        c = ALVO['CORRECAO_DE_SEMANTICA']
        self.assertIn('EXISTENCIA', c['POR_QUE_ESTAVA_ERRADO'])
        self.assertIn('MEU ACESSO', c['POR_QUE_ESTAVA_ERRADO'])
        self.assertIn('existe banco DEV UTILIZAVEL', c['NOVA_DEFINICAO'])
        self.assertIn('CLAUDE_LOCAL_SUPABASE_ACCESS = NO', c['O_QUE_CONTINUA_VALENDO'])

    def test_a_medicao_anterior_continua_certa(self):
        """O que estava errado era o rotulo, nao o que eu medi."""
        a = acesso_local()
        self.assertEqual(a['CLAUDE_LOCAL_SUPABASE_ACCESS'], 'NO')
        self.assertFalse(any(a['ENV'].values()))
        self.assertFalse(any(a['BIN'].values()))

    def test_a_existencia_do_projeto_nao_foi_verificada_por_mim(self):
        self.assertFalse(PROJETO['VERIFICADO_POR_MIM'])
        self.assertEqual(PROJETO['MEDIDO_POR'], 'Luciano, na conta Supabase')
        self.assertEqual(PROJETO['PROJECT_REF'], 'odhdwvugikjdvkapbowe')
        self.assertEqual(PROJETO['REGION'], 'eu-west-1')
        self.assertEqual(PROJETO['STATUS'], 'ACTIVE_HEALTHY')

    def test_nome_igual_nao_e_prova_de_ambiente(self):
        r = ALVO['REGRA_DO_CLASSIFICADOR']
        self.assertIn('nao prova que e o ambiente certo', r['NOME_IGUAL_NAO_E_PROVA'])


class TestClassificador(unittest.TestCase):

    def test_sem_inventario_e_NEEDS_DECISION(self):
        c = classificar(None)
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NEEDS_DECISION')
        self.assertEqual(c['DEV_INSTANCE_AVAILABLE'], 'NOT_MEASURED')

    def test_nunca_devolve_YES_por_ausencia_de_informacao(self):
        """'Nao sei o que tem dentro' e o contrario de 'esta vazio'."""
        for inv in (None, {}):
            self.assertNotEqual(classificar(inv)['SAFE_TO_USE_AS_DEV'], 'YES')

    def test_projeto_vazio_e_YES(self):
        c = classificar(VAZIO)
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'YES')
        self.assertEqual(c['DEV_INSTANCE_AVAILABLE'], 'YES')
        self.assertEqual(c['MOTIVOS_DE_BLOQUEIO'], [])

    def test_usuario_cadastrado_bloqueia(self):
        c = classificar(com(AUTH_USERS=3))
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NO')
        self.assertIn('gente dentro', c['MOTIVOS_DE_BLOQUEIO'][0])

    def test_arquivo_em_storage_bloqueia(self):
        c = classificar(com(STORAGE_OBJECTS=1))
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NO')

    def test_tabela_com_linha_bloqueia(self):
        c = classificar(com(EXISTING_USER_DATA=[
            {'schemaname': 'public', 'relname': 'clientes', 'n_live_tup': 12}]))
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NO')
        self.assertIn('public.clientes(12)', c['MOTIVOS_DE_BLOQUEIO'][0])

    def test_tabela_vazia_nao_bloqueia(self):
        c = classificar(com(EXISTING_USER_DATA=[
            {'schemaname': 'public', 'relname': 'vazia', 'n_live_tup': 0}]))
        self.assertEqual(c['MOTIVOS_DE_BLOQUEIO'], [])

    def test_schema_alheio_pede_decisao(self):
        c = classificar(com(EXISTING_SCHEMAS=['public', 'auth', 'outro_produto']))
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NEEDS_DECISION')
        self.assertIn('outro_produto', str(c['MOTIVOS_DE_ATENCAO']))

    def test_schema_sintonia_ja_existente_pede_decisao(self):
        c = classificar(com(
            EXISTING_SCHEMAS=['public', 'auth', 'sintonia'],
            EXISTING_TABLES=[{'table_schema': 'sintonia', 'table_name': 'attention_object'}]))
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NEEDS_DECISION')
        self.assertIn('nao pode assumir banco limpo', str(c['MOTIVOS_DE_ATENCAO']))

    def test_migration_ja_aplicada_pede_decisao(self):
        c = classificar(com(EXISTING_MIGRATION_HISTORY=[
            {'version': '20260101', 'name': 'algo'}]))
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NEEDS_DECISION')

    def test_bloqueio_vence_atencao(self):
        c = classificar(com(AUTH_USERS=1, EXISTING_SCHEMAS=['public', 'outro']))
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NO')

    def test_schemas_de_sistema_nao_contam_como_alheios(self):
        c = classificar(com(EXISTING_SCHEMAS=list(SCHEMAS_DE_SISTEMA)))
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'YES')


class TestInventario(unittest.TestCase):

    def test_o_contrato_cobre_o_que_foi_pedido(self):
        chaves = {i['CHAVE'] for i in INVENTARIO}
        for exigida in ('DATABASE_VERSION', 'EXISTING_SCHEMAS', 'EXISTING_TABLES',
                        'EXISTING_VIEWS', 'EXISTING_FUNCTIONS', 'EXISTING_RLS_POLICIES',
                        'EXISTING_USER_DATA', 'EXISTING_MIGRATION_HISTORY'):
            self.assertIn(exigida, chaves)
        # e duas que ninguem pediu e decidem o veredito
        self.assertIn('AUTH_USERS', chaves)
        self.assertIn('STORAGE_OBJECTS', chaves)

    def test_o_sql_do_inventario_e_somente_leitura(self):
        corpo = re.sub(r'--[^\n]*', '', INV_SQL)
        for proibido in ('insert', 'update', 'delete', 'drop', 'truncate', 'alter',
                         'grant', 'revoke'):
            self.assertNotRegex(corpo.lower(), r'\b%s\b' % proibido,
                                'o inventario contem %s' % proibido)
        self.assertNotRegex(corpo.lower(), r'\bcreate\b')
        self.assertEqual(corpo.lower().count('select'), corpo.lower().count('select'))
        self.assertIn('select jsonb_pretty', corpo)

    def test_o_sql_e_gerado_e_nao_editado(self):
        self.assertEqual(INV_SQL, gerar_inventario_sql())
        self.assertIn('Nao editar a mao', INV_SQL)

    def test_o_sql_sobrevive_a_tabela_que_nao_existe(self):
        """auth.users e schema_migrations podem nao existir: ausencia e resposta."""
        for marca in ("to_regclass('auth.users')",
                      "to_regclass('storage.objects')",
                      "to_regclass('supabase_migrations.schema_migrations')"):
            self.assertIn(marca, INV_SQL)

    def test_o_projeto_esta_nomeado_no_sql(self):
        self.assertIn(PROJETO['PROJECT_REF'], INV_SQL)


class TestPortaoDeAplicacao(unittest.TestCase):

    def test_o_portao_recusa_hoje(self):
        p = preparar_aplicacao()
        self.assertFalse(p['PODE_APLICAR'])
        self.assertIn('inventario nao executado', p['RECUSAS'])
        self.assertIn('SAFE_TO_USE_AS_DEV = NEEDS_DECISION', p['RECUSAS'])

    def test_o_portao_recusa_mesmo_com_projeto_vazio_sem_acesso(self):
        """Inventario limpo nao basta: quem aplica e quem tem credencial."""
        p = preparar_aplicacao(VAZIO)
        self.assertFalse(p['PODE_APLICAR'])
        self.assertIn('sem acesso local: quem aplica e quem tem credencial', p['RECUSAS'])

    def test_o_alvo_e_o_projeto_informado(self):
        self.assertEqual(preparar_aplicacao()['ALVO'], 'odhdwvugikjdvkapbowe')

    def test_nada_foi_aplicado(self):
        self.assertEqual(ALVO['MIGRATION_APPLIED_DEV'], 'NO')
        self.assertEqual(ALVO['READY_TO_APPLY_MIGRATION_DEV'], 'NO')
        self.assertFalse(ALVO['INVENTARIO_EXECUTADO'])
        self.assertIsNone(ALVO['INVENTARIO'])


class TestNaoRegressao(unittest.TestCase):
    """O que a rodada anterior conquistou continua de pe."""

    def test_o_estado_anterior_foi_preservado(self):
        with open(os.path.join(SUP, 'H2-COMMIT-RESOLUTION.json'), encoding='utf-8') as f:
            h2 = json.load(f)
        self.assertEqual(h2['RESOLVED_COMMIT_SHA'],
                         'd7b289425c5e436f3ce68e367b8706e11910f43b')
        self.assertEqual(h2['H2_PROVENANCE_MUTABLE_REF'], 'NO')

        with open(os.path.join(SUP, 'SUPABASE-MIGRATION-REVIEW.json'), encoding='utf-8') as f:
            self.assertEqual(json.load(f)['MIGRATION_REVIEW'], 'PASS')

        with open(os.path.join(SUP, 'SUPABASE-PUBLISHER-DRYRUN.json'), encoding='utf-8') as f:
            dry = json.load(f)
        self.assertTrue(dry['IDEMPOTENCIA']['DUAS_PASSAGENS_IDENTICAS'])
        self.assertEqual(dry['IDEMPOTENCIA']['NOVAS_ENTIDADES_NA_SEGUNDA'], 0)
        self.assertEqual(dry['MODE']['REAL_DATA_PUBLISHED'], 'NO')

        with open(os.path.join(SUP, 'SUPABASE-CANONICAL-SCHEMA.json'), encoding='utf-8') as f:
            esquema = json.load(f)
        self.assertEqual(len(esquema['VIEWS']), 13)
        self.assertEqual(len(esquema['RPCS']), 4)
        self.assertEqual(esquema['MODE']['MIGRATION_APPLIED'], 'NO')
        self.assertEqual(esquema['MODE']['V8_WIRED'], 'NO')

    def test_nenhuma_credencial_entrou_no_repositorio(self):
        for var in ('SUPABASE_SERVICE_ROLE_KEY', 'SUPABASE_ANON_KEY',
                    'SUPABASE_ACCESS_TOKEN'):
            self.assertIsNone(os.environ.get(var))
        alvo = json.dumps(ALVO)
        self.assertEqual(re.findall(r'eyJ[A-Za-z0-9_-]{20,}', alvo), [])
        self.assertEqual(re.findall(r'sbp_[A-Za-z0-9]{20,}', alvo + INV_SQL), [])


if __name__ == '__main__':
    unittest.main()
