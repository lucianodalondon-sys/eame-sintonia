#!/usr/bin/env python3
"""Uma lei, tres lugares: o core, o leitor italiano e o banco.

O risco desta familia nao e errar uma regra. E ter DUAS regras para a mesma
pergunta, divergindo devagar ate que a mesma frase receba dois vereditos —
um do leitor que le o texto, outro da trava que grava a linha.

Por isso o core (scripts/lugar_do_fato.py) declara o vocabulario, o leitor
italiano (scripts/fato_local.py, portado da branch da Italia) usa as mesmas
palavras, e o banco aceita exatamente esse conjunto. Estes testes comparam
os tres. Qualquer um que ande sozinho reprova.
"""
import os
import re
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import lugar_do_fato as L                                          # noqa: E402
import fato_local as IT                                            # noqa: E402

DSN = os.environ.get('EAME_TEST_DSN')
MIG = os.path.join(RAIZ, 'supabase', 'migrations',
                   '018_o_lugar_do_fato_ganha_dono.sql')


def sql(caminho):
    with open(caminho, encoding='utf-8') as f:
        return f.read()


def vocab_do_banco(tabela, coluna):
    """O vocabulário que o BANCO aceita, lido do banco.

    A primeira versão destes testes lia a migration com expressão regular e
    casava o `check` errado — um parser de SQL improvisado dentro de um teste.
    A autoridade sobre o que o banco aceita é o banco, e perguntar a ele custa
    o mesmo. Sem psycopg na casa, a porta é o psql, como no resto do repo.
    """
    q = ("select pg_get_constraintdef(c.oid) from pg_constraint c "
         "join pg_attribute a on a.attrelid = c.conrelid "
         "and a.attnum = any(c.conkey) "
         "where c.conrelid = 'public.%s'::regclass and c.contype = 'c' "
         "and a.attname = '%s' and array_length(c.conkey,1) = 1" % (tabela, coluna))
    r = subprocess.run(['psql', DSN, '-tAc', q], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip()[:300])
    return set(re.findall(r"'([A-Z_]+)'::text", r.stdout))


@unittest.skipUnless(DSN, 'sem EAME_TEST_DSN: o vocabulario do banco vem do banco')
class TestOCoreEOBancoNaoDivergem(unittest.TestCase):
    """A migration e o core tem de aceitar exatamente o mesmo conjunto."""

    def test_os_papeis_do_conteudo_batem(self):
        self.assertEqual(set(L.PAPEIS_NO_CONTEUDO),
                         vocab_do_banco('conteudo_lugar', 'papel'))

    def test_as_origens_do_lugar_batem(self):
        self.assertEqual(set(L.ORIGENS_DO_LUGAR),
                         vocab_do_banco('conteudo_lugar', 'origem_do_dado'))

    def test_as_especies_de_evidencia_batem(self):
        self.assertEqual(set(L.TIPOS_DE_EVIDENCIA),
                         vocab_do_banco('conteudo_lugar', 'tipo_de_evidencia'))

    def test_os_estados_do_lugar_batem(self):
        self.assertEqual(set(L.ESTADOS_DO_LUGAR),
                         vocab_do_banco('conteudo_lugar', 'estado_do_lugar'))

    def test_fact_nao_esta_no_vocabulario_dos_lugares_do_sujeito(self):
        no_banco = vocab_do_banco('origem_lugar', 'papel')
        self.assertEqual(set(L.ESPECIES_DO_SUJEITO), no_banco)
        self.assertNotIn('FACT', no_banco,
                         'a sede de alguem passou a poder ser declarada lugar de fato')

    def test_publicacao_nao_esta_no_vocabulario_do_tempo(self):
        """A ausencia E a trava. Se ela aparecer, a lei morre em silencio."""
        no_banco = vocab_do_banco('conteudo', 'fact_tempo_origem')
        self.assertEqual(set(L.ORIGENS_DO_TEMPO), no_banco)
        self.assertNotIn('PUBLICACAO', no_banco)

    def test_a_lista_branca_do_fato_e_so_escrito_e_citado(self):
        q = ("select pg_get_constraintdef(oid) from pg_constraint "
             "where conname = 'so_o_escrito_e_o_citado_sustentam_o_lugar_do_fato'")
        r = subprocess.run(['psql', DSN, '-tAc', q], capture_output=True, text=True)
        valores = set(re.findall(r"'([A-Z_]+)'::text", r.stdout))
        self.assertEqual(set(L.ORIGENS_QUE_SUSTENTAM_FATO) | {'FACT'}, valores,
                         'a lista branca mudou: tres leis dependem do que esta nela')

    def test_o_dono_antigo_nao_voltou(self):
        q = ("select count(*) from information_schema.columns where table_schema='public' "
             "and table_name='conteudo' and column_name='fact_geografia_id'")
        r = subprocess.run(['psql', DSN, '-tAc', q], capture_output=True, text=True)
        self.assertEqual('0', r.stdout.strip(),
                         'DOIS DONOS DA MESMA LEI responderiam coisas diferentes um dia')


class TestAMigrationAposentaODonoAntigo(unittest.TestCase):
    """Isto se le no arquivo mesmo: e sobre o que a migration FAZ."""

    def test_a_migration_derruba_a_coluna(self):
        m = sql(MIG)
        self.assertIn('drop column if exists fact_geografia_id', m)
        self.assertIn('drop column if exists fact_geografia_origem', m)

    def test_a_migration_nao_cria_um_segundo_dono(self):
        m = sql(MIG)
        self.assertNotIn('add column if not exists fact_geografia_id', m)


class TestALeiPura(unittest.TestCase):

    def test_so_escrito_e_citado_sustentam_o_fato(self):
        for origem in L.ORIGENS_DO_LUGAR:
            ok, porque = L.sustenta_fato(origem, L.FACT)
            with self.subTest(origem=origem):
                self.assertEqual(origem in L.ORIGENS_QUE_SUSTENTAM_FATO, ok, porque)
                self.assertTrue(porque.strip())

    def test_papel_que_nao_e_fato_nunca_sustenta_fato(self):
        for papel in L.PAPEIS_NO_CONTEUDO:
            if papel == L.FACT:
                continue
            ok, _ = L.sustenta_fato('ESCRITO', papel)
            self.assertFalse(ok, 'papel %s virou lugar do fato' % papel)

    def test_a_zona_da_fonte_e_incomparavel_e_nao_menos_precisa(self):
        self.assertIsNone(L.mais_especifico_que('ZONA_DEFINIDA_PELA_FONTE', 'PROVINCIA'),
                          'a zona foi comparada na régua administrativa')
        self.assertIsNone(L.mais_especifico_que('PROVINCIA', 'ZONA_DEFINIDA_PELA_FONTE'))
        self.assertTrue(L.mais_especifico_que('MUNICIPIO', 'REGIAO'))
        self.assertFalse(L.mais_especifico_que('REGIAO', 'MUNICIPIO'))

    def test_ocorrencia_nunca_soma_com_incidencia(self):
        r = L.ocorrencia_nao_e_incidencia(
            ['DIAGNOSTIC_SAMPLE'] * 5 + ['REGIONAL_STATEMENT'])
        self.assertEqual(5, r['OBSERVED_OCCURRENCES'],
                         'o comunicado regional entrou na contagem de ocorrências')
        self.assertEqual('NOT_KNOWN', r['INCIDENCE'])
        self.assertEqual('NOT_KNOWN', r['REGIONAL_PRESSURE'])

    def test_nao_existe_score_no_contrato(self):
        c = L.contrato()
        for chave in c:
            self.assertNotIn('SCORE', chave.upper())


class TestOsBacktests(unittest.TestCase):
    """Contraexemplos ja medidos, exercidos contra o leitor de verdade.

    Nenhum destes foi inventado para passar: cada um e a forma de um falso
    positivo que ja custou caro no Brasil ou na Italia.
    """

    def le(self, texto):
        ok, nao = IT.localizacoes_do_fato(texto)
        return ({a['FACT_LOCATION'] for a in ok},
                {(r['PLACE'], r['STATE']) for r in nao})

    def test_italia_a_sede_nao_vira_foco(self):
        fatos, recusas = self.le(
            'Azienda con sede a Bergamo. Fusariosi constatata a Grosseto.')
        self.assertEqual({'Grosseto'}, fatos)
        self.assertIn(('Bergamo', IT.PLACE_MENTION_ONLY), recusas)

    def test_italia_o_local_do_convegno_nao_vira_foco(self):
        fatos, recusas = self.le(
            'Convegno a Torino con relatore di Piacenza. Sintomi osservati a Siena.')
        self.assertEqual({'Siena'}, fatos)
        self.assertIn(('Torino', IT.PLACE_MENTION_ONLY), recusas)

    def test_brasil_a_lista_territorial_economica_nao_vira_ocorrencia(self):
        fatos, recusas = self.le('Operiamo in Torino, Piacenza e Bergamo.')
        self.assertEqual(set(), fatos)
        self.assertTrue(all(e == IT.TERRITORIAL_LIST for _, e in recusas), recusas)

    def test_brasil_varios_lugares_num_documento_nao_viram_um(self):
        fatos, _ = self.le(
            'Campioni positivi provenienti da Grosseto, Siena e Arezzo.')
        self.assertEqual({'Grosseto', 'Siena', 'Arezzo'}, fatos,
                         'ficar com a primeira inventaria um recorte que a fonte não fez')

    def test_brasil_amostra_positiva_nao_e_incidencia(self):
        ok, _ = IT.localizacoes_do_fato(
            'Campioni positivi provenienti da Grosseto.')
        self.assertEqual('DIAGNOSTIC_SAMPLE', ok[0]['TYPE_OF_EVIDENCE'])
        r = L.ocorrencia_nao_e_incidencia([a['TYPE_OF_EVIDENCE'] for a in ok])
        self.assertEqual('NOT_KNOWN', r['INCIDENCE'])

    def test_italia_a_data_de_publicacao_nao_vira_tempo_do_fato(self):
        t = IT.tempo_do_fato(
            '13 febbraio 2026. Durante la stagione 2025 sono stati osservati sintomi.',
            '2026-02-13')
        self.assertEqual('stagione 2025', t['FACT_TIME'])
        self.assertEqual('SEASON', t['FACT_TIME_PRECISION'])
        self.assertIn(IT.PUBLICATION_STAMP,
                      [d['WHY'] for d in t['TIME_CANDIDATES_DISCARDED']])

    def test_italia_uma_serie_historica_nao_e_uma_safra(self):
        t = IT.tempo_do_fato('Serie storica 2011-2025 dei monitoraggi.', '2026-02-13')
        self.assertNotEqual('2011-2025', t.get('FACT_TIME'))

    def test_gazetteer_declara_a_propria_cobertura(self):
        """NOT_IN_GAZETTEER != NOT_A_PLACE: o silencio precisa ser legivel."""
        c = IT.cobertura()
        self.assertEqual(0, c['MUNICIPALITIES'])
        self.assertIn('NOT_IN_GAZETTEER', c['LIMIT'])
        fatos, recusas = self.le('Focolaio constatato a Roccalbegna.')
        self.assertEqual(set(), fatos)
        self.assertEqual(set(), recusas,
                         'um lugar fora do gazetteer é INVISÍVEL ao leitor, e não '
                         'recusado — quem o guarda é conteudo_lugar, com o estado')


if __name__ == '__main__':
    unittest.main()
