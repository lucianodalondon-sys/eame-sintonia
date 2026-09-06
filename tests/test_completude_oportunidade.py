"""Regressoes da varredura de portfolio e do cruzamento de inteligencia.

Cada teste impede um silencio que esta missao mediu no pacote servido.

    UM CORTE SEM CONTADOR NAO E UM RESUMO: E UMA AFIRMACAO DE TOTAL.

O motor le de build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/, que NAO e
versionado — reconstroi-se do ZIP, que e. Sem o ZIP os testes do motor sao
SKIP declarado, nunca falso verde.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'scripts')
ZIP = os.path.join(ROOT, 'build', 'SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip')
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
MEDIDA = os.path.join(ROOT, 'data', 'samples', 'IT-COMPLETUDE',
                      'IT-COMPLETUDE-OPORTUNIDADE.json')
sys.path.insert(0, SCRIPTS)


def _prepara_ingest():
    """Extrai o DESIGN-INGEST do ZIP se ele nao estiver no disco.

    Devolve (ok, criado_por_nos) — o segundo diz se ha que limpar no fim.
    """
    if os.path.isdir(ING) and os.listdir(ING):
        return True, False
    if not os.path.exists(ZIP):
        return False, False
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(ZIP) as z:
            z.extractall(tmp)
        origem = os.path.join(tmp, 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
        if not os.path.isdir(origem):
            return False, False
        os.makedirs(os.path.dirname(ING), exist_ok=True)
        shutil.copytree(origem, ING)
    return True, True


class TestVarreduraDoMotor(unittest.TestCase):
    """O motor tem de DECLARAR a varredura, e a conta tem de fechar."""

    @classmethod
    def setUpClass(cls):
        ok, cls._limpar = _prepara_ingest()
        if not ok:
            raise unittest.SkipTest('DESIGN-INGEST indisponivel (sem ZIP no disco)')
        import v21_oportunidades as M
        cls.brutos = M.main()[0]

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, '_limpar', False):
            shutil.rmtree(os.path.dirname(ING), ignore_errors=True)

    def test_a_conta_do_portfolio_fecha_em_todos(self):
        """ENCONTRADOS = LIGADOS + NAO_LIGADOS + NAO_SEI, sem excecao."""
        fora = [o['ID'] for o, _ in self.brutos
                if o['PORTFOLIO_SCAN_FOUND'] != (o['PORTFOLIO_SCAN_LINKED']
                                                 + o['PORTFOLIO_SCAN_NOT_LINKED']
                                                 + o['PORTFOLIO_SCAN_UNKNOWN'])]
        self.assertEqual([], fora, 'a varredura nao fecha em: %s' % fora)

    def test_o_corte_declara_o_que_removeu(self):
        """O teto pode cortar. O que ele nao pode e cortar em silencio."""
        for o, _ in self.brutos:
            self.assertIn('PORTFOLIO_LIST_TOTAL_BEFORE_CAP', o, o['ID'])
            self.assertIn('PORTFOLIO_LIST_OMITTED', o, o['ID'])
            self.assertEqual(
                o['PORTFOLIO_LIST_OMITTED'], len(o['PORTFOLIO_LIST_OMITTED_NAMES']),
                'contagem de omitidos nao bate com a lista em %s' % o['ID'])
            self.assertEqual(
                max(0, o['PORTFOLIO_LIST_TOTAL_BEFORE_CAP'] - o['PORTFOLIO_LIST_CAP']),
                o['PORTFOLIO_LIST_OMITTED'], o['ID'])

    def test_nenhum_produto_ligado_esta_fora_do_universo(self):
        """LIGADO sai do rotulo da cultura. Nao pode aparecer de outro lado."""
        for o, _ in self.brutos:
            self.assertLessEqual(o['PORTFOLIO_SCAN_LINKED'], o['PORTFOLIO_SCAN_FOUND'],
                                 o['ID'])

    def test_sem_alvo_nada_e_ligado_nem_rejeitado(self):
        """Sem alvo declarado, aceitar ou rejeitar seria inventar o criterio."""
        for o, _ in self.brutos:
            if o.get('TARGET'):
                continue
            self.assertEqual(0, o['PORTFOLIO_SCAN_LINKED'], o['ID'])
            self.assertEqual(0, o['PORTFOLIO_SCAN_NOT_LINKED'], o['ID'])
            self.assertEqual(o['PORTFOLIO_SCAN_FOUND'], o['PORTFOLIO_SCAN_UNKNOWN'],
                             o['ID'])


class TestCruzamentoDeInteligencia(unittest.TestCase):
    """Todas as familias sao PERGUNTADAS. Nenhuma delas LIGA seja o que for."""

    @classmethod
    def setUpClass(cls):
        ok, cls._limpar = _prepara_ingest()
        if not ok:
            raise unittest.SkipTest('DESIGN-INGEST indisponivel (sem ZIP no disco)')
        import v21_oportunidades as M
        cls.brutos = M.main()[0]

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, '_limpar', False):
            shutil.rmtree(os.path.dirname(ING), ignore_errors=True)

    def test_toda_familia_e_consultada_em_todo_cartao(self):
        n = {len(o['CROSS_INTELLIGENCE_SCAN']) for o, _ in self.brutos}
        self.assertEqual(1, len(n), 'cartoes consultam numeros diferentes de familias')
        for o, _ in self.brutos:
            for fam, v in o['CROSS_INTELLIGENCE_SCAN'].items():
                self.assertTrue(v['CONSULTED'], '%s nao consultou %s' % (o['ID'], fam))
                self.assertIn(v['RESULT'],
                              ('MATCH', 'CROP_ONLY', 'NOT_FOUND', 'NO_CROP_KEY'), fam)

    def test_as_quatro_listas_esgotam_as_familias(self):
        """Cada familia cai em exatamente uma classe. Sem sobra, sem repeticao."""
        for o, _ in self.brutos:
            somadas = (o['CROSS_INTELLIGENCE_FAMILIES_WITH_MATCH']
                       + o['CROSS_INTELLIGENCE_FAMILIES_CROP_ONLY']
                       + o['CROSS_INTELLIGENCE_FAMILIES_NOT_FOUND']
                       + o['CROSS_INTELLIGENCE_FAMILIES_NO_CROP_KEY'])
            self.assertEqual(sorted(o['CROSS_INTELLIGENCE_SCAN']), sorted(somadas),
                             o['ID'])

    def test_o_cruzamento_nao_entra_na_evidencia(self):
        """Se entrasse, uma familia nova mudava julgamento ja emitido.

        Este e o teste que impede a correcao de virar promocao silenciosa. A
        prova e de IGUALDADE, nao de ausencia: EVIDENCE_IDS tem de ser
        EXATAMENTE o que os apoios do arquetipo trouxeram — nem um id a mais.

        Note-se que familias como FIELD_SIGNAL aparecem legitimamente em
        EVIDENCE_FAMILIES: elas SAO a evidencia do arquetipo O1, e ja eram
        antes deste scan existir. O que se proibe e o scan ACRESCENTAR.
        """
        for o, apoios in self.brutos:
            self.assertEqual([a['ID'] for a in apoios], o['EVIDENCE_IDS'],
                             'o scan acrescentou evidencia em %s' % o['ID'])
            # O scan PODE achar o que a evidencia nao cita — e isso que o torna
            # uma leitura do acervo, e nao uma segunda porta para a evidencia.
            # Por isso nao se exige nada dos ids que ele encontrou; exige-se que
            # nenhum deles tenha atravessado para EVIDENCE_IDS, que e o que a
            # igualdade acima ja prova.

    def test_score_nao_conhece_o_scan(self):
        """O scan nao pode ter mexido em nenhuma dimensao de pontuacao."""
        for o, _ in self.brutos:
            self.assertEqual(
                sorted(o['SCORE_DIMENSIONS']),
                ['ACTIONABILITY', 'ADAMA', 'AGRONOMIC', 'CURRENTNESS',
                 'GEOGRAPHY', 'MULTI_SOURCE'], o['ID'])


class TestMedidaPublicada(unittest.TestCase):
    """O relatorio publicado tem de bater com o proprio ficheiro medido."""

    def setUp(self):
        if not os.path.exists(MEDIDA):
            self.skipTest('medida ainda nao gerada')
        with open(MEDIDA, encoding='utf-8') as f:
            self.r = json.load(f)

    def test_a_conta_fecha_nos_quarenta_e_tres(self):
        self.assertEqual(43, self.r['OPORTUNIDADES'])
        self.assertTrue(self.r['TOTAIS']['CONTA_DO_PORTFOLIO_FECHA_EM_TODAS'])

    def test_todo_cartao_tem_entrada_de_arquetipo_reconstruida(self):
        """Sem a entrada, o corte nao tem denominador e o numero nao vale."""
        self.assertEqual(0, self.r['TOTAIS']['CARTOES_SEM_ENTRADA_RECONSTRUIDA'])

    def test_o_corte_de_doze_nao_e_medido_por_subtracao_cega(self):
        """O campo antigo somava tres mecanismos num nome so — e mentia.

        MEDIDO: 10 cartoes e 81 produtos saem do teto. O resto do antigo 184
        era o portao CLIENT_SAFE e o recorte do arquetipo.
        """
        t = self.r['TOTAIS']
        self.assertNotIn('PRODUTOS_PERDIDOS_PELO_CORTE_12', t,
                         'o nome que misturava mecanismos voltou')
        self.assertGreaterEqual(t['PRODUTOS_REMOVIDOS_PELO_TETO_12'], 0)
        self.assertLessEqual(t['CARTOES_CORTADOS_PELO_TETO_12'],
                             self.r['OPORTUNIDADES'])

    def test_o_material_nao_utilizavel_nao_conta_como_zero(self):
        """Video existe e nao serve. Contar como zero mentiria sobre o acervo."""
        for f in self.r['FICHAS']:
            self.assertIn(f['CRUZAMENTO']['TRANSCRICOES']['RESULTADO'],
                          ('MATERIAL_EXISTENTE_NAO_UTILIZAVEL',))


if __name__ == '__main__':
    unittest.main()
