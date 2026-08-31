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

import supabase_dev_target as alvo  # noqa: E402
from supabase_dev_target import (  # noqa: E402
    INVENTARIO_MEDIDO,
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
        # mudou de lista: isto e sujeira de SCHEMA, nao de dado
        self.assertIn('nao pode assumir banco limpo', str(c['MOTIVOS_DE_SCHEMA']))
        self.assertEqual(c['SCHEMA_CLEAN'], 'NO')

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
        # O inventario aponta para o DEV NOVO. O ref antigo nao pode aparecer:
        # um SQL de leitura colado no projeto errado le o projeto errado.
        self.assertIn(alvo.DEV_TARGET['DEV_PROJECT_REF'], INV_SQL)
        self.assertNotIn(PROJETO['PROJECT_REF'], INV_SQL)

    def test_o_veredito_sai_separado_do_sql(self):
        # As duas perguntas, cada uma com nome proprio no resultado.
        for chave in ('DATA_EMPTY', 'SCHEMA_CLEAN', 'SAFE_FOR_CANONICAL_MIGRATION'):
            self.assertIn("'%s'" % chave, INV_SQL)

    def test_o_veredito_nao_conta_o_supabase_como_sujeira(self):
        # O bug do avesso: reprovar todo projeto novo porque ele nasce com auth,
        # storage e realtime dentro.
        for sistema in ('auth', 'storage', 'extensions', 'realtime', 'vault',
                        'supabase_migrations'):
            self.assertIn("('%s')" % sistema, INV_SQL)

    def test_a_linha_e_contada_de_verdade_e_nao_estimada(self):
        # n_live_tup e estimativa do coletor: pode dizer 0 numa tabela cheia.
        # Um zero falso aqui autorizaria a migration em cima do dado de alguem.
        self.assertIn('query_to_xml', INV_SQL)
        self.assertIn('count(*) real', INV_SQL)

    def test_objeto_de_extensao_nao_conta_como_schema_sujo(self):
        self.assertIn("d.deptype = 'e'", INV_SQL)

    def test_o_veredito_tambem_nao_escreve_nada(self):
        proibido = re.compile(r'\b(insert|update|delete|drop|alter|create|truncate|grant)\b',
                              re.I)
        depois = INV_SQL.split('VEREDITO')[-1]
        for linha in depois.splitlines():
            corpo = linha.split('--')[0]
            self.assertIsNone(proibido.search(corpo), linha)


class TestInventarioMedido(unittest.TestCase):
    """O inventario voltou, por acesso autorizado fora desta maquina."""

    def test_o_projeto_existente_reprova_como_DEV(self):
        c = classificar(INVENTARIO_MEDIDO)
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NO')
        self.assertEqual(c['DEV_INSTANCE_AVAILABLE'], 'NO')
        self.assertEqual(ALVO['EXISTING_PROJECT_SAFE_AS_DEV'], 'NO')
        self.assertEqual(ALVO['EXISTING_PROJECT_AVAILABLE'], 'YES')

    def test_os_dois_motivos_de_bloqueio_estao_medidos(self):
        c = classificar(INVENTARIO_MEDIDO)
        texto = ' '.join(c['MOTIVOS_DE_BLOQUEIO'])
        self.assertIn('732 objeto(s) em storage', texto)
        self.assertIn('19 tabela(s) com linhas', texto)
        self.assertEqual(INVENTARIO_MEDIDO['LINHAS_TOTAIS'], 1932)

    def test_bloqueio_vence_inventario_incompleto(self):
        """A ordem que um inventario real corrigiu.

        Vieram contagens, nao as listas de schema e tabela. Antes, a guarda de
        completude respondia primeiro e devolvia NEEDS_DECISION — com 732 arquivos
        medidos la dentro. 'Nao sei tudo, mas sei que ha 732 arquivos' e NAO.
        """
        parcial = {k: INVENTARIO_MEDIDO[k] for k in
                   ('EXISTING_USER_DATA', 'AUTH_USERS', 'STORAGE_OBJECTS')}
        self.assertNotIn('EXISTING_SCHEMAS', parcial)
        c = classificar(parcial)
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NO')
        self.assertIn('inventario parcial', ' '.join(c['MOTIVOS_DE_ATENCAO']))

    def test_sem_bloqueio_a_incompletude_ainda_pede_decisao(self):
        """A guarda antiga continua valendo onde ela importa."""
        c = classificar({'AUTH_USERS': 0, 'STORAGE_OBJECTS': 0})
        self.assertEqual(c['SAFE_TO_USE_AS_DEV'], 'NEEDS_DECISION')
        self.assertIn('inventario incompleto', c['WHY'][0])

    def test_zero_usuarios_nao_libera_nada(self):
        """AUTH_USERS = 0 e verdade, e nao muda o veredito."""
        self.assertEqual(INVENTARIO_MEDIDO['AUTH_USERS'], 0)
        self.assertEqual(classificar(INVENTARIO_MEDIDO)['SAFE_TO_USE_AS_DEV'], 'NO')

    def test_o_que_nao_foi_recebido_esta_declarado(self):
        self.assertIn('EXISTING_SCHEMAS', INVENTARIO_MEDIDO['NAO_RECEBIDO'])
        self.assertIn('EXISTING_MIGRATION_HISTORY', INVENTARIO_MEDIDO['NAO_RECEBIDO'])
        self.assertFalse(INVENTARIO_MEDIDO['EXECUTADO_POR_MIM'])

    def test_os_achados_do_inventario_estao_registrados(self):
        achados = {a['ACHADO'] for a in ALVO['ACHADOS_DO_INVENTARIO']}
        self.assertTrue(any('PUBLIC_POLICIES = 0' in a for a in achados))
        self.assertTrue(any('dominio SINTONIA' in a for a in achados))
        self.assertTrue(any('schema_migracao = 17' in a for a in achados))
        for a in ALVO['ACHADOS_DO_INVENTARIO']:
            self.assertTrue(a['ACAO'])
            self.assertNotIn('apagar', a['ACAO'])


class TestAlvoDev(unittest.TestCase):

    def test_a_estrategia_foi_decidida_pela_medicao_nao_por_mim(self):
        # Deixou de ser NEEDS_DECISION porque a opcao A foi TENTADA e medida: a
        # branch herdou schema e migrations do pai, exatamente como o contra da
        # opcao A previa. Nao e escolha em silencio — e a opcao que sobrou.
        d = ALVO['DEV_TARGET']
        self.assertEqual(d['DEV_TARGET_STRATEGY'], 'NEW_PROJECT')
        self.assertEqual(len(d['OPCOES']), 2)

    def test_o_projeto_novo_existe_e_isso_nao_o_aprova(self):
        # A opcao B saiu do papel: o projeto foi criado. Este teste guarda a
        # distancia entre as duas coisas — ter REF proprio e UM requisito, nao a
        # aprovacao. A branch reprovada tambem tinha REF proprio.
        d = ALVO['DEV_TARGET']
        self.assertEqual(d['DEV_TARGET_CREATED'], 'YES')
        self.assertEqual(d['DEV_PROJECT_REF'], 'xhqebdweltytnghiavew')
        self.assertNotIn(d['DEV_PROJECT_REF'], alvo.REFS_RECUSADOS)
        # existir nao mede nada do que decide
        self.assertEqual(d['DEV_INVENTARIO_EXECUTADO'], 'NO')
        self.assertEqual(d['DEV_DATA_EMPTY'], 'NOT_MEASURED')
        self.assertEqual(d['DEV_SCHEMA_CLEAN'], 'NOT_MEASURED')
        self.assertFalse(d['DEV_VERIFICADO_POR_MIM'])

    def test_o_portao_continua_recusando_o_alvo_novo_por_falta_de_inventario(self):
        # O portao nao pode abrir so porque o REF saiu da lista de recusados.
        p = alvo.preparar_aplicacao(None, 'xhqebdweltytnghiavew')
        self.assertFalse(p['PODE_APLICAR'])
        self.assertTrue(any('inventario' in r for r in p['RECUSAS']))

    def test_a_recomendacao_vem_do_inventario_e_nao_de_gosto(self):
        r = ALVO['DEV_TARGET']['RECOMENDACAO']
        self.assertEqual(r['ESCOLHA'], 'B')
        self.assertIn('nao e preferencia: e o inventario', r['POR_QUE'])
        self.assertIn('17 migrations', r['POR_QUE'])

    def test_os_requisitos_do_ambiente_dev(self):
        req = ' '.join(ALVO['DEV_TARGET']['REQUISITOS_DO_AMBIENTE_DEV'])
        for marca in ('nao carregar dado de producao', 'SOMENTE migrations',
                      'descartavel', 'PROJECT_REF proprio',
                      'service role NUNCA no frontend'):
            self.assertIn(marca, req)
        self.assertIn('odhdwvugikjdvkapbowe', req)

    def test_o_projeto_existente_fica_intocado(self):
        nao = ' '.join(ALVO['DEV_TARGET']['O_QUE_NAO_FAZER_COM_O_PROJETO_EXISTENTE'])
        for marca in ('nao aplicar a migration', 'nao limpar', 'nao apagar',
                      'nao reutilizar como sandbox'):
            self.assertIn(marca, nao)


class TestPortaoDeAplicacao(unittest.TestCase):

    def test_o_portao_recusa_hoje(self):
        p = preparar_aplicacao(INVENTARIO_MEDIDO)
        self.assertFalse(p['PODE_APLICAR'])
        self.assertIn('SAFE_TO_USE_AS_DEV = NO', p['RECUSAS'])

    def test_o_portao_recusa_mesmo_com_projeto_vazio_sem_acesso(self):
        """Inventario limpo nao basta: quem aplica e quem tem credencial."""
        p = preparar_aplicacao(VAZIO)
        self.assertFalse(p['PODE_APLICAR'])
        self.assertIn('sem acesso local: quem aplica e quem tem credencial', p['RECUSAS'])

    def test_o_alvo_deixou_de_ser_fixo(self):
        # Antes, ALVO era o parent, escrito no codigo. Isso era um alvo errado
        # esperando a hora de ser usado. Agora quem aplica informa o REF, e o
        # portao recusa os que ja foram medidos e reprovados.
        self.assertIsNone(preparar_aplicacao()['ALVO'])
        self.assertEqual(preparar_aplicacao(ref='ref-x')['ALVO'], 'ref-x')

    def test_nada_foi_aplicado(self):
        self.assertEqual(ALVO['MIGRATION_APPLIED_DEV'], 'NO')
        self.assertEqual(ALVO['READY_TO_APPLY_MIGRATION_DEV'], 'NO')
        # o inventario agora existe — e o veredito piorou, nao melhorou
        self.assertTrue(ALVO['INVENTARIO_EXECUTADO'])
        self.assertEqual(ALVO['INVENTARIO']['STORAGE_OBJECTS'], 732)


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
