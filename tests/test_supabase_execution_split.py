"""Cortar a migration nao pode mudar o que ela diz. Estes testes cobram isso.

A prova central e simples de enunciar e dificil de fingir: concatenar os corpos
dos cinco blocos, na ordem, tem de devolver o arquivo canonico inteiro, byte a
byte, menos as duas linhas de transacao. Ela roda de duas maneiras — da memoria
do gerador e dos arquivos gravados — porque so a segunda pega o erro de gravacao.

O que NAO esta provado aqui: que os blocos rodam. Nao ha Postgres nesta maquina.
SQL_EXECUTADO = NO.
"""
import hashlib
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import supabase_execution_split as sp  # noqa: E402

MANIFESTO = os.path.join(ROOT, 'data', 'supabase', 'SUPABASE-EXECUTION-MANIFEST.json')
with open(MANIFESTO, encoding='utf-8') as f:
    M = json.load(f)


def ler(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8', newline='') as fh:
        return fh.read()


class TestAOrigemNaoFoiTocada(unittest.TestCase):
    def test_o_sha_da_migration_e_o_declarado(self):
        # Se a migration mudasse, tudo aqui embaixo estaria dividindo outra coisa.
        atual = hashlib.sha256(sp.ler_canonica().encode('utf-8')).hexdigest()
        self.assertEqual(atual, sp.CANONICAL_0001_SHA256)
        self.assertEqual(M['CANONICAL_0001_SHA256'], sp.CANONICAL_0001_SHA256)
        self.assertTrue(M['SHA_BATE_COM_O_DECLARADO'])

    def test_o_json_da_autoridade_nao_entra_nesta_conversa(self):
        # A divisao e de ferramenta. Se ela precisasse mexer no contrato, seria
        # outra coisa com o mesmo nome.
        fonte = ler('scripts/supabase_execution_split.py')
        # 'CANONICAL-SCHEMA' aparece uma vez, na lista do que NAO foi tocado —
        # isso e declaracao, nao leitura. O que importa e o que ele abre.
        aberturas = [l for l in fonte.splitlines() if 'open(' in l]
        for linha in aberturas:
            self.assertTrue(
                any(alvo in linha for alvo in ('CANONICA', 'caminho', 'MANIFESTO')),
                'abre um arquivo que nao e a migration nem a saida: %s' % linha)
        self.assertNotIn('json.load', fonte)     # nao le contrato nenhum
        # e o unico arquivo de entrada e a propria migration
        self.assertIn("'0001_initial_canonical_schema.sql')", fonte)


class TestProvaDeReconstrucao(unittest.TestCase):
    def test_da_memoria_do_gerador(self):
        v = sp.verificar()
        self.assertEqual(v['RECONSTRUCTION_MATCH'], 'YES')
        self.assertEqual(v['SEMANTIC_DIFF'], 0)

    def test_dos_arquivos_gravados(self):
        # Esta e a que vale: pega erro de escrita que a de memoria nao ve.
        v = sp.verificar_no_disco()
        self.assertEqual(v['RECONSTRUCTION_MATCH'], 'YES')
        self.assertEqual(v['SEMANTIC_DIFF'], 0)
        self.assertEqual(v['CORPO_SHA256'], v['CORPO_SHA256_ESPERADO'])

    def test_so_saiu_o_begin_e_o_commit(self):
        d = sp.diferenca_para_o_original()
        self.assertEqual(d['LINHAS_REMOVIDAS'], ['BEGIN;', 'COMMIT;'])
        self.assertTrue(d['SO_SAIU_A_TRANSACAO'])
        self.assertEqual(d['ORIGINAL_SHA256'], sp.CANONICAL_0001_SHA256)

    def test_o_begin_dos_corpos_de_funcao_continua_la(self):
        # `DO $$ BEGIN` e o BEGIN de dentro das funcoes nao sao transacao. Um
        # replace de texto teria apagado todos.
        juntos = ''.join(sp.corpo_do_arquivo(ler(a['FILE'])) for a in M['ARQUIVOS'])
        self.assertIn('DO $$ BEGIN', juntos)
        # 2 corpos DO $$ e 4 funcoes que abrem BEGIN dentro. Um replace cego de
        # 'BEGIN;' nao pegaria estes, mas um replace de 'BEGIN' pegaria todos.
        self.assertGreaterEqual(juntos.count('BEGIN'), 6)
        # e a transacao de fora nao sobrou em lugar nenhum do corpo
        for linha in juntos.splitlines():
            self.assertNotEqual(linha.strip(), 'BEGIN;')
            self.assertNotEqual(linha.strip(), 'COMMIT;')

    def test_o_manifesto_no_disco_e_o_que_o_gerador_produz(self):
        gerado = sp.medir()
        gerado['PROVA_NO_DISCO'] = sp.verificar_no_disco()
        self.assertEqual(M, gerado)


class TestOsCortesSaoSeguros(unittest.TestCase):
    def setUp(self):
        self.corpos = [sp.corpo_do_arquivo(ler(a['FILE'])) for a in M['ARQUIVOS']]

    def test_nenhum_bloco_abre_um_comando_que_nao_fecha(self):
        # Se um corte tivesse caido no meio de um CREATE TABLE, o pedaco de cima
        # terminaria sem ';' e o de baixo comecaria sem comando.
        for corpo, a in zip(self.corpos, M['ARQUIVOS']):
            fatias = sp.statements(corpo)
            self.assertTrue(fatias, a['FILE'])
            resto = corpo[fatias[-1][1]:].strip()
            for linha in resto.splitlines():
                self.assertTrue(linha.strip().startswith('--'),
                                '%s termina com SQL fora de comando: %r'
                                % (a['FILE'], linha))

    def test_nenhum_corpo_de_dollar_quote_foi_partido(self):
        # Contagem par de cada etiqueta: abre e fecha dentro do mesmo bloco.
        for corpo, a in zip(self.corpos, M['ARQUIVOS']):
            for etiqueta in ('$$', '$fx$', '$fn$', '$neg$'):
                self.assertEqual(corpo.count(etiqueta) % 2, 0,
                                 '%s parte um corpo %s ao meio' % (a['FILE'], etiqueta))

    def test_cada_bloco_tem_pelo_menos_um_comando(self):
        for a in M['ARQUIVOS']:
            self.assertGreater(a['STATEMENTS_COUNT'], 0, a['FILE'])


class TestAFronteiraPedida(unittest.TestCase):
    def test_o_bloco_a_termina_na_tabela_source(self):
        # A regra veio de fora: os blocos restantes comecam logo depois de
        # CREATE TABLE source (...);
        corpo_a = sp.corpo_do_arquivo(ler(M['ARQUIVOS'][0]['FILE']))
        self.assertIn('CREATE TABLE source (', corpo_a)
        self.assertNotIn('CREATE TABLE source_snapshot (', corpo_a)
        corpo_b = sp.corpo_do_arquivo(ler(M['ARQUIVOS'][1]['FILE']))
        self.assertTrue(corpo_b.lstrip().startswith('--')
                        or corpo_b.lstrip().startswith('CREATE TABLE'))
        self.assertIn('CREATE TABLE source_snapshot (', corpo_b)

    def test_o_bloco_ja_aplicado_esta_marcado_e_isolado(self):
        a = M['ARQUIVOS'][0]
        self.assertTrue(a['JA_APLICADO'])
        self.assertEqual(M['ALREADY_APPLIED_BLOCK'], a['FILE'])
        self.assertNotIn(a['FILE'], M['REMAINING_BLOCKS'])
        # o cabecalho quebra em varias linhas: comparar sem as quebras
        corrido = ' '.join(ler(a['FILE']).split()).lower()
        self.assertIn('ja foi aplicado', corrido)
        self.assertIn('nao rode', corrido)

    def test_os_quatro_restantes_estao_na_ordem_de_dependencia(self):
        # tabelas -> FKs e indices -> papeis e RLS -> views e RPCs. Trocar a
        # ordem faz o Postgres recusar: FK sem tabela, view sem tabela.
        self.assertEqual([f.split('/')[-1] for f in M['REMAINING_BLOCKS']], [
            '0001b_tables_remaining.sql', '0001c_foreign_keys_indexes.sql',
            '0001d_roles_rls_policies.sql', '0001e_views_rpcs.sql'])


class TestNadaSePerdeuNoCaminho(unittest.TestCase):
    """As contagens somadas tem de ser as da migration inteira."""

    def _soma(self, tipo):
        return sum(a['STATEMENTS_POR_TIPO'].get(tipo, 0) for a in M['ARQUIVOS'])

    def test_as_57_tabelas_estao_todas(self):
        self.assertEqual(self._soma('CREATE TABLE'), 57)

    def test_os_27_vocabularios_fechados_estao_todos(self):
        self.assertEqual(self._soma('CREATE TYPE'), 27)

    def test_as_112_chaves_estrangeiras_e_os_57_rls_somam_os_alter(self):
        self.assertEqual(self._soma('ALTER TABLE'), 112 + 57)

    def test_os_86_indices_estao_todos(self):
        self.assertEqual(self._soma('CREATE INDEX'), 86)

    def test_as_82_politicas_estao_todas(self):
        self.assertEqual(self._soma('CREATE POLICY'), 82)

    def test_as_13_views_e_as_5_funcoes_estao_todas(self):
        self.assertEqual(self._soma('CREATE VIEW'), 13)
        self.assertEqual(self._soma('CREATE FUNCTION'), 5)   # 4 RPCs + o helper

    def test_o_total_de_comandos_bate_com_a_soma_dos_blocos(self):
        self.assertEqual(M['STATEMENTS_TOTAL'],
                         sum(a['STATEMENTS_COUNT'] for a in M['ARQUIVOS']))
        do_original = [f for f in sp.mapear()[1]
                       if f['TIPO'] not in ('BEGIN', 'COMMIT', 'COMENTARIO')]
        self.assertEqual(M['STATEMENTS_TOTAL'], len(do_original))


class TestOAndaimeEDeclarado(unittest.TestCase):
    def test_cada_arquivo_abre_e_fecha_a_propria_transacao(self):
        for a in M['ARQUIVOS']:
            txt = ler(a['FILE'])
            self.assertIn('BEGIN;', txt)
            self.assertTrue(txt.rstrip().endswith('COMMIT;'), a['FILE'])
            self.assertIn(sp.SET_PATH, txt)

    def test_o_andaime_vive_fora_das_marcas(self):
        for a in M['ARQUIVOS']:
            corpo = sp.corpo_do_arquivo(ler(a['FILE']))
            self.assertNotIn(sp.SET_PATH, corpo.split('\n')[0])
            # O corpo do bloco a carrega o cabecalho do PROPRIO 0001, que tambem
            # diz 'GERADO por scripts/'. O que nao pode vazar para dentro das
            # marcas e o cabecalho DESTE gerador.
            self.assertNotIn('supabase_execution_split.py', corpo)
            self.assertNotIn('EXECUCAO EM PARTES', corpo)

    def test_o_arquivo_diz_de_onde_veio_e_com_que_sha(self):
        for a in M['ARQUIVOS']:
            txt = ler(a['FILE'])
            self.assertIn('0001_initial_canonical_schema.sql', txt)
            self.assertIn(sp.CANONICAL_0001_SHA256, txt)
            self.assertIn(sp.DEV_PROJECT_REF, txt)

    def test_a_quebra_de_linha_nao_fica_misturada(self):
        # Corpo em CRLF com andaime em LF roda igual e suja todo diff.
        for a in M['ARQUIVOS']:
            txt = ler(a['FILE'])
            soltos = txt.replace('\r\n', '').count('\n')
            self.assertEqual(soltos, 0, '%s mistura CRLF com LF' % a['FILE'])


class TestOQueContinuaNaoProvado(unittest.TestCase):
    def test_nada_foi_executado(self):
        self.assertFalse(M['EXECUTADO_POR_MIM'])
        self.assertIn('credencial', M['POR_QUE_NAO'])

    def test_a_migration_ainda_nao_esta_aplicada_por_inteiro(self):
        # Um bloco de cinco nao e a migration. Enquanto e nao correr, PARTIAL.
        self.assertEqual(M['MIGRATION_APPLIED_DEV'], 'PARTIAL')

    def test_o_alvo_e_o_dev_novo(self):
        self.assertEqual(M['DEV_PROJECT_REF'], 'xhqebdweltytnghiavew')


if __name__ == '__main__':
    unittest.main()
