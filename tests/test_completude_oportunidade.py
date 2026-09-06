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
        # Compara-se por CONJUNTO, nao por lista: a ORDEM de EVIDENCE_IDS nao e
        # invariante entre linhagens — o gerador canonico ordena, esta nao — e um
        # teste que reprova por ordem reprova pela razao errada, exactamente onde
        # o handoff precisa de ser lido.
        #
        #     UM TESTE QUE FALHA POR ORDEM NAO ESTA A GUARDAR O CONTEUDO.
        # As DUAS unicas adicoes que o motor declara: a fonte que decidiu a
        # janela e a que declarou a regra do momento. Elas nao observam par
        # nenhum, por isso nunca entram em `apoios` — e o motor lista-as de
        # proposito, para que quem audita a evidencia encontre o documento que
        # decidiu o «quando». Nomea-las aqui e MAIS estreito que exigir
        # igualdade crua: prova que o scan nao acrescenta E que nada alem
        # destas duas acrescenta.
        for o, apoios in self.brutos:
            permitido = {a['ID'] for a in apoios}
            for campo in ('WINDOW_EVIDENCE_ID', 'WINDOW_RULE_EVIDENCE_ID'):
                if o.get(campo):
                    permitido.add(o[campo])
            self.assertEqual(sorted(permitido), sorted(set(o['EVIDENCE_IDS'])),
                             'o scan acrescentou evidencia em %s' % o['ID'])
            for extra in set(o['EVIDENCE_IDS']) - {a['ID'] for a in apoios}:
                papeis = [r for r in o['EVIDENCE_ROLES']
                          if r['EVIDENCE_ID'] == extra]
                self.assertTrue(papeis, 'id acrescentado sem papel declarado '
                                        'em %s: %s' % (o['ID'], extra))
                self.assertEqual('SUPPORTS_WINDOW', papeis[0]['ROLE'], o['ID'])
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




class TestIntegridadeDeCultura(unittest.TestCase):
    """O cartao so afirma o par produto x cultura que alguma casa prova.

        SUBSTANCIA EM COMUM NAO PROVA PRODUTO PARA A CULTURA.

    Os tres casos nomeados abaixo foram MEDIDOS no arquetipo O5 desta arvore
    antes da correcao: o cartao recebia cultura porque a substancia tocava uma
    so, e listava todos os produtos que a continham, viessem da cultura que
    viessem.
    """

    @classmethod
    def setUpClass(cls):
        ok, cls._limpar = _prepara_ingest()
        if not ok:
            raise unittest.SkipTest('DESIGN-INGEST indisponivel (sem ZIP no disco)')
        import v21_oportunidades as M
        cls.brutos = M.main()[0]
        cls.por_id = {o['ID']: o for o, _ in cls.brutos}

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, '_limpar', False):
            shutil.rmtree(os.path.dirname(ING), ignore_errors=True)

    def _autoridade(self):
        """As mesmas casas que o motor usa, remontadas por fora.

        Remontar por fora e de proposito: um teste que perguntasse ao proprio
        indice do motor provaria apenas que ele concorda consigo mesmo.
        """
        import re as _re
        base = os.path.join(ING, '%s.json')

        def le(n):
            return json.load(open(base % n, encoding='utf-8'))['RECORDS']

        def num(x):
            return _re.sub(r'\D', '', str(x or '')).lstrip('0').zfill(6)

        def chave(n):
            return _re.sub(r'[^a-z0-9]', '', str(n or '').lower())

        rel = [r for r in le('PRODUCT-RELATIONSHIPS') if r.get('CLIENT_SAFE')]
        reg = [r for r in le('PRODUCTS-REGULATORY') if r.get('CLIENT_SAFE')]
        com = [r for r in le('PRODUCTS-COMMERCIAL') if r.get('CLIENT_SAFE')]
        por_reg = {}
        for r in rel:
            por_reg.setdefault(num(r.get('REGISTRATION_NUMBER')), set()).update(
                r.get('CROP_IDS') or [])
        aut = {}

        def add(k, c):
            if c:
                aut.setdefault(k, set()).update(c)
        for p in reg:
            add(chave(p.get('NAME')), por_reg.get(num(p.get('REGISTRATION_NUMBER'))))
            add(chave(p.get('NAME')), set(p.get('CROP_IDS') or []))
        for p in com:
            add(chave(p.get('NAME')), set(p.get('CROP_IDS') or []))
        return aut, chave

    def test_nenhum_produto_servido_tem_a_cultura_errada(self):
        """A regressao geral: vale para TODO arquetipo, nao so o O5."""
        aut, chave = self._autoridade()
        erradas = []
        for o, _ in self.brutos:
            crop = o.get('CROP')
            if not crop:
                continue
            for nome in o['PRODUCT_RELATIONSHIPS']:
                provadas = aut.get(chave(nome)) or set()
                if provadas and crop not in provadas:
                    erradas.append((o['ID'], crop, nome, sorted(provadas)))
        self.assertEqual([], erradas,
                         'produto de outra cultura servido no cartao: %s' % erradas)

    def test_produto_sem_cultura_provada_nao_e_servido(self):
        """UNKNOWN nao e ligacao. Servi-lo seria afirmar o que nao se mediu."""
        aut, chave = self._autoridade()
        sem = [(o['ID'], n) for o, _ in self.brutos if o.get('CROP')
               for n in o['PRODUCT_RELATIONSHIPS'] if not (aut.get(chave(n)) or set())]
        self.assertEqual([], sem, 'produto sem cultura provada servido: %s' % sem)

    def test_vite_nao_recebe_produto_so_de_frumento(self):
        """STAVENTO declara frumento e estava num cartao de videira."""
        for o, _ in self.brutos:
            if o.get('CROP') != 'CROP_GRAPEVINE':
                continue
            self.assertNotIn('STAVENTO', o['PRODUCT_RELATIONSHIPS'], o['ID'])

    def test_pomodoro_nao_recebe_produto_so_de_vite(self):
        """VINETO declara videira e estava num cartao de tomate."""
        for o, _ in self.brutos:
            if o.get('CROP') != 'CROP_TOMATO':
                continue
            self.assertNotIn('VINETO', o['PRODUCT_RELATIONSHIPS'], o['ID'])

    def test_soia_nao_recebe_produto_de_mais_riso_girassol(self):
        """POSTSCRIPT 80 e 80 XL declaram milho/arroz/girassol, nao soja."""
        for o, _ in self.brutos:
            if o.get('CROP') != 'CROP_SOYBEAN':
                continue
            for n in ('POSTSCRIPT 80', 'POSTSCRIPT 80 XL'):
                self.assertNotIn(n, o['PRODUCT_RELATIONSHIPS'], o['ID'])

    def test_a_conta_do_filtro_fecha(self):
        """OFERECIDOS = SERVIDOS + EXCLUIDOS, sem excecao."""
        for o, _ in self.brutos:
            self.assertEqual(
                o['PORTFOLIO_OFFERED_TO_CARD'],
                len(o['PRODUCT_RELATIONSHIPS']) + o['PORTFOLIO_EXCLUDED_COUNT'],
                o['ID'])

    def test_todo_produto_excluido_tem_razao_especifica(self):
        """Razao generica onde a especifica e conhecida e recusa a responder."""
        VOCAB = {'CROP_MISMATCH', 'TARGET_MISMATCH', 'NOT_IN_COMMERCIAL_CATALOG',
                 'REGULATORY_NOT_PROVED', 'UNKNOWN_CROP', 'UNKNOWN_TARGET',
                 'PRESENTATION_LIMIT', 'OUT_OF_SCOPE'}
        for o, _ in self.brutos:
            for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']:
                self.assertIn(x.get('REASON'), VOCAB, o['ID'])
                self.assertTrue(x.get('PRODUCT_NAME'), o['ID'])
                self.assertTrue(x.get('REASON_MEANS'), o['ID'])

    def test_crop_mismatch_nomeia_a_cultura_que_provou(self):
        """Dizer «cultura errada» sem dizer QUAL seria a mesma opacidade."""
        for o, _ in self.brutos:
            for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']:
                if x['REASON'] == 'CROP_MISMATCH':
                    self.assertTrue(x['PROVEN_CROPS'], o['ID'])
                    self.assertTrue(x['PROVEN_BY'], o['ID'])
                    self.assertNotIn(o['CROP'], x['PROVEN_CROPS'], o['ID'])
                if x['REASON'] == 'UNKNOWN_CROP':
                    self.assertEqual([], x['PROVEN_CROPS'], o['ID'])

    def test_sem_cultura_no_cartao_nao_se_filtra(self):
        """Filtrar por uma cultura que nao existe seria inventar o criterio."""
        for o, _ in self.brutos:
            if o.get('CROP'):
                continue
            self.assertFalse(o['PORTFOLIO_CROP_FILTER_APPLIED'], o['ID'])
            razoes = {x['REASON'] for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']}
            self.assertFalse(razoes - {'PRESENTATION_LIMIT'}, o['ID'])

    def test_o_filtro_nao_mexeu_no_portfolio_matches(self):
        """PORTFOLIO_MATCHES tem outro dono — portfolio() — e continua com ele.

        Se o filtro de cultura tivesse mexido aqui, esta correcao teria criado
        um SEGUNDO dono para a mesma decisao.
        """
        for o, _ in self.brutos:
            for m in (o.get('PORTFOLIO_MATCHES') or []):
                self.assertIn('MATCH_REASON', m, o['ID'])
                self.assertEqual('REGISTRATION_NUMBER_JOIN', m['MATCH_REASON'], o['ID'])


if __name__ == '__main__':
    unittest.main()
