"""As regras da fronteira de importação, e as mutações que as provam.

Cada regra aqui existe porque um defeito medido a exigiu. Um teste que
passaria com o parser defeituoso reinstalado não vale nada — por isso cada
lei central tem a mutação ao lado.
"""
import json
import os
import re
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import adama_es_import_rules as R  # noqa: E402

# Os dois textos são LITERAIS do handoff. Não são exemplos escritos por mim.
TEXTO_DESDE_HASTA = (
    'En cebada de invierno se podrá realizar una aplicación en post-emergencia '
    'temprada del cultivo, o bien, realizar dicha aplicación en pre-emergencia del '
    'cultivo, desde BBCH 00 (semilla seca) hasta BBCH 07 (coleòptilo, emergido de '
    'la semilla).')
TEXTO_COM_TRACO = (
    'Aplicar únicamente en variedades Full Page. Pueden realizarse 2 aplicaciones a '
    '0,4375 l/ha, espaciadas 20 días. Aplicar sin agua e inundar 3-4 días más tarde. '
    'Aplicar durante BBCH 12-29.')


class TestBBCHPreservaOIntervaloReal(unittest.TestCase):
    """RT-6. A fonte diz BBCH 00 até BBCH 07; o sistema não pode guardar 00-00."""

    def test_desde_hasta_vira_faixa_inteira(self):
        r = R.normalizar_bbch(TEXTO_DESDE_HASTA)
        self.assertEqual('PHENOLOGY_STAGE', r['RESOLUCAO'])
        self.assertEqual((0, 7), (r['BBCH_INICIO'], r['BBCH_FIM']))
        self.assertIn('desde…hasta', r['REGRA'])

    def test_o_traco_continua_funcionando(self):
        r = R.normalizar_bbch(TEXTO_COM_TRACO)
        self.assertEqual((12, 29), (r['BBCH_INICIO'], r['BBCH_FIM']))

    def test_estadio_unico_legitimo_continua_possivel(self):
        """BBCH 65-65 é uma janela válida. A correção não pode matá-la."""
        r = R.normalizar_bbch('Aplicar en BBCH 65')
        self.assertEqual('PHENOLOGY_STAGE', r['RESOLUCAO'])
        self.assertEqual((65, 65), (r['BBCH_INICIO'], r['BBCH_FIM']))

    def test_ponta_aberta_nunca_vira_faixa_fechada(self):
        """'a partir de BBCH 30' não tem fim. Fechar em 30 seria o RT-6 de novo."""
        for t in ('Aplicar a partir de BBCH 30', 'Aplicar hasta BBCH 39',
                  'Aplicar después de BBCH 21'):
            r = R.normalizar_bbch(t)
            with self.subTest(texto=t):
                self.assertEqual('APPROXIMATE', r['RESOLUCAO'])
                self.assertIsNone(r['BBCH_FIM'])

    def test_duas_mencoes_sem_linguagem_nao_viram_faixa(self):
        r = R.normalizar_bbch('Tratar em BBCH 13 e novamente BBCH 39')
        self.assertEqual('APPROXIMATE', r['RESOLUCAO'])

    def test_faixa_invertida_nao_e_aceita(self):
        r = R.normalizar_bbch('BBCH 29-12')
        self.assertEqual('APPROXIMATE', r['RESOLUCAO'])

    def test_sem_mencao_e_not_known(self):
        r = R.normalizar_bbch('Centeno | Malas Hierbas | 2 l/ha |')
        self.assertEqual('NOT_KNOWN', r['RESOLUCAO'])
        self.assertIsNone(r['BBCH_INICIO'])

    def test_o_texto_literal_viaja_sempre(self):
        for t in (TEXTO_DESDE_HASTA, TEXTO_COM_TRACO, 'nada aqui'):
            self.assertEqual(t, R.normalizar_bbch(t)['TEXTO_LITERAL'])

    def test_o_fim_nunca_e_derivado_do_inicio(self):
        """A lei em uma linha, varrida sobre todos os casos conhecidos."""
        casos = [TEXTO_DESDE_HASTA, TEXTO_COM_TRACO, 'Aplicar a partir de BBCH 30',
                 'Tratar em BBCH 13 e novamente BBCH 39', 'BBCH 29-12',
                 'Aplicar hasta BBCH 39']
        for t in casos:
            r = R.normalizar_bbch(t)
            if r['BBCH_INICIO'] is not None and r['BBCH_INICIO'] == r['BBCH_FIM']:
                with self.subTest(texto=t[:40]):
                    self.assertIn('ESTADIO_UNICO', r['REGRA'],
                                  'início == fim só pode vir de linguagem pontual')


class TestMutacaoDoParserDefeituoso(unittest.TestCase):
    """Reinstalar o parser antigo tem de REPROVAR. Sem isto, o teste é enfeite."""

    @staticmethod
    def parser_antigo(t):
        """Cópia fiel do _bbch() do coletor: search() + `group(2) or group(1)`."""
        rx = re.compile(r'bbch\s*:?\s*(\d{1,2})\s*(?:[-–a]\s*(\d{1,2}))?', re.I)
        m = rx.search(t or '')
        if not m:
            return (None, None)
        return (int(m.group(1)), int(m.group(2) or m.group(1)))

    def test_o_parser_antigo_produz_o_defeito(self):
        self.assertEqual((0, 0), self.parser_antigo(TEXTO_DESDE_HASTA),
                         'se isto mudou, o defeito de origem não é mais o que medimos')

    def test_a_regra_nova_discorda_do_parser_antigo_onde_importa(self):
        antigo = self.parser_antigo(TEXTO_DESDE_HASTA)
        novo = R.normalizar_bbch(TEXTO_DESDE_HASTA)
        self.assertNotEqual(antigo, (novo['BBCH_INICIO'], novo['BBCH_FIM']))
        self.assertEqual((0, 7), (novo['BBCH_INICIO'], novo['BBCH_FIM']))

    def test_e_concorda_onde_o_antigo_estava_certo(self):
        antigo = self.parser_antigo(TEXTO_COM_TRACO)
        novo = R.normalizar_bbch(TEXTO_COM_TRACO)
        self.assertEqual(antigo, (novo['BBCH_INICIO'], novo['BBCH_FIM']),
                         'a correção não pode quebrar o caso que já funcionava')


class TestOrigemDoAlvo(unittest.TestCase):
    """RT-11. Um menu do site não vira alvo autorizado por conter a palavra."""

    def test_linha_de_tabela_ancorada_pode_virar_alvo(self):
        r = {'CROP': 'ARROZ', 'ISSUE': 'Dicotiledóneas',
             'ANCHOR': {'ROW_TEXT': 'Arroz | Dicotiledóneas | 0,5', 'ROW_INDEX': 1}}
        self.assertEqual('PAIR_TABLE_ROW', R.classificar_origem_do_issue(r))
        self.assertTrue(R.pode_virar_alvo_autorizado('PAIR_TABLE_ROW'))

    def test_varredura_de_texto_nunca_vira_alvo(self):
        r = {'ISSUE': 'MALAS HIERBAS', 'PRODUCT_ID': 'x'}
        self.assertEqual('PAGE_BODY_TEXT', R.classificar_origem_do_issue(r))
        self.assertFalse(R.pode_virar_alvo_autorizado('PAGE_BODY_TEXT'))

    def test_nenhuma_origem_desconhecida_vira_alvo(self):
        for o in R.ORIGENS:
            if o != 'PAIR_TABLE_ROW':
                self.assertFalse(R.pode_virar_alvo_autorizado(o), o)

    def test_a_regra_nao_e_lista_de_palavras(self):
        """A decisão é por ORIGEM. O mesmo termo entra ou não conforme a âncora."""
        ancorado = {'CROP': 'CEBADA', 'ISSUE': 'MALAS HIERBAS',
                    'ANCHOR': {'ROW_TEXT': 'Cebada | Malas Hierbas | 2 l/ha', 'ROW_INDEX': 1}}
        solto = {'ISSUE': 'MALAS HIERBAS'}
        self.assertTrue(R.pode_virar_alvo_autorizado(R.classificar_origem_do_issue(ancorado)))
        self.assertFalse(R.pode_virar_alvo_autorizado(R.classificar_origem_do_issue(solto)))

    def test_termo_ubiquo_e_medida_nao_filtro(self):
        rel = [{'ISSUE': 'X', 'PRODUCT_ID': p} for p in ('a', 'b', 'c')] + \
              [{'ISSUE': 'Y', 'PRODUCT_ID': 'a'}]
        u = R.termos_ubiquos(rel, 3)
        self.assertEqual({'X': 3}, u)
        # e o ubíquo continua podendo entrar se vier ancorado: a medida informa,
        # não decide.
        self.assertTrue(R.pode_virar_alvo_autorizado('PAIR_TABLE_ROW'))


class TestMutacaoDaRegraDeOrigem(unittest.TestCase):

    def test_admitir_varredura_reprovaria(self):
        """Se pode_virar_alvo_autorizado aceitasse PAGE_BODY_TEXT, o alvo
        MALAS HIERBAS entraria para um fungicida. A mutação prova que a
        regressão pega."""
        def mutada(origem):
            return origem in ('PAIR_TABLE_ROW', 'PAGE_BODY_TEXT')
        fungicida = {'ISSUE': 'MALAS HIERBAS', 'PRODUCT_ID': 'NEPTUNE'}
        origem = R.classificar_origem_do_issue(fungicida)
        self.assertFalse(R.pode_virar_alvo_autorizado(origem))
        self.assertTrue(mutada(origem), 'a mutação precisa realmente mudar o resultado')


class TestContraOArtefatoReal(unittest.TestCase):
    """As regras contra o handoff inteiro, não contra exemplos escolhidos."""

    @classmethod
    def setUpClass(cls):
        import subprocess
        cls.h = json.loads(subprocess.check_output(
            ['git', '-C', RAIZ, 'show',
             'origin/claude/adama-es-local-browser:data/samples/'
             'ADAMA-ES-PRODUCT-INTELLIGENCE.json'], text=True))

    def test_as_tres_janelas_do_handoff_passam_pela_regra(self):
        for w in self.h['APPLICATION_WINDOWS']:
            par = [r for r in self.h['CROP_ISSUE_RELATIONS']
                   if r['PRODUCT_ID'] == w['PRODUCT_ID'] and r['CROP'] == w['CROP']]
            raw = par[0]['ANCHOR']['ROW_TEXT'] if par else ''
            r = R.normalizar_bbch(raw)
            with self.subTest(crop=w['CROP']):
                self.assertNotEqual((0, 0), (r['BBCH_INICIO'], r['BBCH_FIM']),
                                    'nenhuma janela pode sair 00-00')

    def test_as_duas_janelas_defeituosas_ficam_00_07(self):
        corrigidas = 0
        for w in self.h['APPLICATION_WINDOWS']:
            if (w['BBCH_FROM'], w['BBCH_TO']) != ('00', '00'):
                continue
            par = [r for r in self.h['CROP_ISSUE_RELATIONS']
                   if r['PRODUCT_ID'] == w['PRODUCT_ID'] and r['CROP'] == w['CROP']]
            r = R.normalizar_bbch(par[0]['ANCHOR']['ROW_TEXT'])
            self.assertEqual((0, 7), (r['BBCH_INICIO'], r['BBCH_FIM']))
            corrigidas += 1
        self.assertEqual(2, corrigidas, 'são duas janelas afetadas, não mais nem menos')

    def test_nenhuma_relacao_de_alvo_solta_pode_virar_alvo(self):
        for r in self.h['ISSUE_RELATIONS']:
            self.assertFalse(
                R.pode_virar_alvo_autorizado(R.classificar_origem_do_issue(r)))

    def test_as_cinco_relacoes_de_par_podem(self):
        n = sum(1 for r in self.h['CROP_ISSUE_RELATIONS']
                if R.pode_virar_alvo_autorizado(R.classificar_origem_do_issue(r)))
        self.assertEqual(5, n)

    def test_a_familia_de_erva_daninha_esta_em_todos_os_produtos(self):
        """A medida que sustenta a regra: um termo em 56/56 não discrimina."""
        def familia(i):
            u = i.upper()
            return 'ERVA' if any(t in u for t in (
                'MALAS HIERBAS', 'DICOTILED', 'MONOCOTILED', 'GRAMINEA', 'GRAMÍNEA',
                'VALLICO', 'CAÑOTA', 'AVENA LOCA')) else i
        rel = [{'ISSUE': familia(r['ISSUE']), 'PRODUCT_ID': r['PRODUCT_ID']}
               for r in self.h['ISSUE_RELATIONS']]
        self.assertEqual({'ERVA': 56}, R.termos_ubiquos(rel, len(self.h['PRODUCTS'])))


if __name__ == '__main__':
    unittest.main()
