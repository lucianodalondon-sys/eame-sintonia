#!/usr/bin/env python3
"""LEITOR CANÔNICO DE RÓTULOS — o mais novo e portado vence o mais velho e menor.

O defeito que este arquivo torna impossível de repetir: um enxerto trouxe um artefato de
**30/08/2026** com **90 pares** cultura × alvo e ele foi apresentado como estado da arte,
ao lado de um leitor de **04/09/2026** com **2.928 pares** que já tinha passado portão com
gabarito lido à mão. O artefato antigo até declarava como limitação intransponível
*«o dicionário é espanhol, Scaphoideus não está nele»* — que é exatamente o que o leitor
novo resolveu.

    OLDER_SMALLER_READER != CANONICAL_READER
    NEW_MERGE_CANNOT_DOWNGRADE_GATED_READING

Nada aqui é lido de uma declaração e aceito: as datas são comparadas, os tamanhos contados
e os campos exclusivos conferidos nos dois conjuntos.
"""
import datetime
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGADO = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                      'ITALY-ADAMA-REGULATORY-INTELLIGENCE.json')
CANONICO = os.path.join(ROOT, 'data', 'samples', 'IT-ROTULOS-V1', 'IT-ROTULOS-PARES-V3.json')
PILOTO = os.path.join(ROOT, 'docs', 'piloto', 'SINTONIA-ITALIA-PILOTO.md')


def _j(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


@unittest.skipUnless(os.path.exists(LEGADO) and os.path.exists(CANONICO),
                     'os dois leitores precisam estar versionados')
class TestOLegadoNaoTemAutoridade(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.legado = _j(LEGADO)
        cls.canon = _j(CANONICO)
        cls.dec = cls.legado['LEITOR_CANONICO_DA_CASA']

    def test_o_legado_se_declara_legado(self):
        self.assertEqual('LEGACY_READER / HISTORICAL_INPUT', self.dec['ESTE_ARTEFACTO'])
        self.assertEqual('NO', self.dec['CANONICAL_AUTHORITY'])

    def test_as_duas_leis_estao_escritas(self):
        self.assertIn('OLDER_SMALLER_READER != CANONICAL_READER', self.dec['LEI'])
        self.assertIn('NEW_MERGE_CANNOT_DOWNGRADE_GATED_READING', self.dec['LEI'])

    def test_o_canonico_e_mesmo_o_mais_novo(self):
        """A declaração não basta: as datas são comparadas."""
        d = lambda s: datetime.date.fromisoformat(s)
        self.assertLess(d(self.legado['CAPTURED_AT']), d(self.canon['CAPTURED_AT']),
                        'o "canônico" não é mais novo que o legado — reabrir a decisão')
        self.assertEqual(d(self.dec['LEITOR_CANONICO']['CAPTURED_AT']),
                         d(self.canon['CAPTURED_AT']),
                         'a data declarada não é a do arquivo')

    def test_o_canonico_e_mesmo_o_maior_e_passou_portao(self):
        self.assertEqual(2928, len(self.canon['PAIRS']))
        self.assertEqual(2928, self.canon['SUPPORTED_PAIRS'])
        self.assertEqual(2928, self.dec['LEITOR_CANONICO']['PARES'])
        self.assertEqual(90, self.legado['DISTINCT_CROP_TARGET_PAIRS'])
        self.assertGreater(len(self.canon['PAIRS']),
                           self.legado['DISTINCT_CROP_TARGET_PAIRS'])
        self.assertEqual('it_rotulo_parser/3.4.0', self.canon['PARSER_VERSION'])
        self.assertIn('IT-ROTULOS-PORTAO-V1', self.dec['LEITOR_CANONICO']['PORTAO'])
        self.assertRegex(self.canon['ESTADO'], r'PUBLICADO')

    def test_a_limitacao_intransponivel_do_legado_ja_foi_resolvida(self):
        """O legado diz que Scaphoideus não está no dicionário. No canônico, está."""
        self.assertIn('Scaphoideus', self.legado['COVERAGE_IS_A_FLOOR'])
        achados = sum(1 for p in self.canon['PAIRS']
                      if 'scaphoideus' in json.dumps(p, ensure_ascii=False).lower())
        self.assertGreater(achados, 0,
                           'se o canônico também não lê Scaphoideus, a decisão muda')

    def test_o_caminho_declarado_e_o_arquivo_que_existe(self):
        self.assertTrue(os.path.exists(
            os.path.join(ROOT, self.dec['LEITOR_CANONICO']['CAMINHO'])))


@unittest.skipUnless(os.path.exists(LEGADO) and os.path.exists(CANONICO),
                     'os dois leitores precisam estar versionados')
class TestOQueOLegadoAINDATem(unittest.TestCase):
    """Sem autoridade não quer dizer sem valor. Mas o que ele tem entra como CANDIDATO."""

    @classmethod
    def setUpClass(cls):
        cls.legado = _j(LEGADO)
        cls.canon = _j(CANONICO)
        cls.so = cls.legado['LEITOR_CANONICO_DA_CASA']['O_QUE_ESTE_ARTEFACTO_TEM_E_O_CANONICO_NAO']

    def test_as_linhas_nao_cobertas_entram_como_candidato_nunca_como_par(self):
        self.assertEqual('CANDIDATE_INPUT_TO_CANONICAL_READER', self.so['CLASSE'])
        self.assertIn('AUTORIDADE', self.so['NAO_E'])
        self.assertEqual(12, len(self.so['LINHAS_NAO_COBERTAS']))

    def test_a_subsuncao_e_parcial_e_o_numero_bate(self):
        c = self.legado['LEITOR_CANONICO_DA_CASA']['COMPARACAO_CAMPO_A_CAMPO']
        self.assertEqual(len(self.legado['AUTHORIZED_USE_ROWS']), c['LINHAS_DE_USO_DO_LEGADO'])
        self.assertEqual(37, c['COBERTAS_PELO_CANONICO'])
        self.assertEqual(c['LINHAS_DE_USO_DO_LEGADO'] - c['COBERTAS_PELO_CANONICO'],
                         len(self.so['LINHAS_NAO_COBERTAS']))
        self.assertIn('PARCIAL', c['SUBSUMED_BY_IT_ROTULOS_PARES_V3'])

    def test_os_campos_exclusivos_sao_exclusivos_de_verdade(self):
        """Declarar exclusividade é fácil; aqui ela é conferida nos dois conjuntos."""
        do_legado = set()
        for r in self.legado['AUTHORIZED_USE_ROWS']:
            do_legado |= set(r)
        do_canon = set()
        for p in self.canon['PAIRS'][:200]:
            do_canon |= set(p)
        for campo in self.so['CAMPOS_EXCLUSIVOS']:
            with self.subTest(campo=campo):
                self.assertIn(campo, do_legado, 'declarado exclusivo e ausente no legado')
                self.assertNotIn(campo, do_canon, 'declarado exclusivo e presente no canônico')


@unittest.skipUnless(os.path.exists(PILOTO), 'documento do piloto ausente')
class TestNenhumDocumentoVendeOLeitorVelhoComoEstadoDaArte(unittest.TestCase):

    def test_o_documento_do_piloto_carrega_a_correcao(self):
        with open(PILOTO, encoding='utf-8') as f:
            doc = f.read()
        self.assertIn('IT-ROTULOS-PARES-V3', doc,
                      'o documento cita 90 pares sem dizer qual é o leitor canônico')
        self.assertRegex(doc, r'(?i)legacy_reader|LEGACY READER|não é o leitor can',
                         'falta a marca de que o leitor de 90 pares não é o canônico')
        self.assertRegex(doc, r'2\.?928',
                         'o documento não publica o tamanho do leitor canônico')


if __name__ == '__main__':
    unittest.main(verbosity=2)
