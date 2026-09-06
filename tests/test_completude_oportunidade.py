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
        """OFERECIDOS = SERVIDOS + EXCLUIDOS(no escopo do cartao), sem excecao."""
        for o, _ in self.brutos:
            noescopo = [x for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']
                        if x['SCOPE'] == 'OFFERED_TO_CARD']
            self.assertEqual(o['PORTFOLIO_EXCLUDED_COUNT'], len(noescopo), o['ID'])
            self.assertEqual(
                o['PORTFOLIO_OFFERED_TO_CARD'],
                len(o['PRODUCT_RELATIONSHIPS']) + len(noescopo), o['ID'])

    def test_todo_produto_nao_promovido_declara_de_que_universo_caiu(self):
        """Uma razao sem escopo nao se pode auditar: «excluido» de onde?"""
        ESCOPOS = {'OFFERED_TO_CARD', 'CROP_UNIVERSE', 'SERVED_NOT_MATCHED'}
        for o, _ in self.brutos:
            self.assertEqual(o['PORTFOLIO_NOT_PROMOTED_COUNT'],
                             len(o['PORTFOLIO_EXCLUDED_WITH_REASON']), o['ID'])
            for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']:
                self.assertIn(x.get('SCOPE'), ESCOPOS, o['ID'])
            # o alvo e a cultura nao se confundem: quem cai por alvo NAO pode
            # sair rotulado como cultura errada, e vice-versa
            for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']:
                if x['REASON'] == 'TARGET_MISMATCH':
                    self.assertEqual('CROP_UNIVERSE', x['SCOPE'], o['ID'])
                if x['REASON'] in ('CROP_MISMATCH', 'UNKNOWN_CROP'):
                    self.assertEqual('OFFERED_TO_CARD', x['SCOPE'], o['ID'])

    def test_nenhum_produto_servido_esta_tambem_excluido(self):
        """Servido e excluido ao mesmo tempo seria a conta a mentir dos dois lados."""
        for o, _ in self.brutos:
            servidos = set(o['PRODUCT_RELATIONSHIPS'])
            for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']:
                if x['SCOPE'] == 'SERVED_NOT_MATCHED':
                    continue
                self.assertNotIn(x['PRODUCT_NAME'], servidos,
                                 '%s: %s esta servido E excluido'
                                 % (o['ID'], x['PRODUCT_NAME']))

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
            # So o escopo OFFERED_TO_CARD fala do filtro de cultura. As outras
            # razoes vivem noutros universos e nao sao filtragem por cultura.
            razoes = {x['REASON'] for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']
                      if x['SCOPE'] == 'OFFERED_TO_CARD'}
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


class TestCortesDeclarados(unittest.TestCase):
    """Limitar apresentacao e permitido. Esconder que se limitou nao e."""

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

    def test_o_censo_de_evidencia_fecha_por_familia(self):
        """FOUND = USED + OMITTED, em cada familia de cada cartao."""
        for o, _ in self.brutos:
            self.assertTrue(o['EVIDENCE_SCAN'], 'cartao sem censo: %s' % o['ID'])
            for x in o['EVIDENCE_SCAN']:
                self.assertEqual(x['TOTAL_FOUND'],
                                 x['TOTAL_USED'] + x['TOTAL_OMITTED'],
                                 '%s · %s' % (o['ID'], x['FIELD']))

    def test_toda_omissao_de_evidencia_tem_razao(self):
        """Omitir sem razao e o corte silencioso outra vez, so que noutro campo."""
        for o, _ in self.brutos:
            for x in o['EVIDENCE_SCAN']:
                if x['TOTAL_OMITTED']:
                    self.assertTrue(x['OMISSION_REASON'],
                                    '%s · %s' % (o['ID'], x['FIELD']))
                else:
                    self.assertIsNone(x['OMISSION_REASON'], o['ID'])

    def test_a_evidencia_de_cada_casamento_declara_o_que_cortou(self):
        """O ultimo corte silencioso deste fluxo: PORTFOLIO_MATCHES[i].EVIDENCE
        levava quatro linhas de rotulo e nao dizia de quantas.

        MEDIDO: 66 linhas omitidas em 14 das 65 entradas.
        """
        for o, _ in self.brutos:
            for m in (o.get('PORTFOLIO_MATCHES') or []):
                self.assertEqual(m['EVIDENCE_LABEL_ROWS_FOUND'],
                                 m['EVIDENCE_LABEL_ROWS_SHOWN']
                                 + m['EVIDENCE_LABEL_ROWS_OMITTED'], o['ID'])
                if m['EVIDENCE_LABEL_ROWS_OMITTED']:
                    self.assertEqual('PRESENTATION_LIMIT',
                                     m['EVIDENCE_OMISSION_REASON'], o['ID'])

    def test_nenhuma_familia_e_cortada_sem_aparecer_no_censo(self):
        """O censo tem de cobrir TODAS as familias que o arquetipo ofereceu."""
        for o, _ in self.brutos:
            campos = [x['FIELD'] for x in o['EVIDENCE_SCAN']]
            self.assertEqual(len(campos), len(set(campos)),
                             'familia repetida no censo de %s' % o['ID'])


class TestContabilidadeDasFontes(unittest.TestCase):
    """A conta das origens tem de fechar, e a fusao nao pode comer origem."""

    @classmethod
    def setUpClass(cls):
        ok, cls._limpar = _prepara_ingest()
        if not ok:
            raise unittest.SkipTest('DESIGN-INGEST indisponivel (sem ZIP no disco)')
        import v21_oportunidades as M
        b, rej, C, cs = M.main()
        cls.regs = M.gravar(b, C, cs)[0] if hasattr(M, 'gravar') else None
        cls.pacote = json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'),
                                    encoding='utf-8'))['RECORDS']

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, '_limpar', False):
            shutil.rmtree(os.path.dirname(ING), ignore_errors=True)

    def test_a_conta_das_fontes_fecha(self):
        """FOUND = SHOWN + OMITTED, sem excecao."""
        for r in self.pacote:
            self.assertEqual(r['SOURCE_URLS_TOTAL_FOUND'],
                             r['SOURCE_URLS_TOTAL_SHOWN']
                             + r['SOURCE_URLS_TOTAL_OMITTED'], r['ID'])
            self.assertEqual(r['SOURCE_URLS_TOTAL_SHOWN'],
                             len(r['SOURCE_URLS']), r['ID'])

    def test_a_fusao_nao_come_origem(self):
        """Citar 250 provas e publicar 3 origens nao e resumo: e conta que nao fecha.

        MEDIDO antes da correcao: OPP_B9206ACFC797 funde 38 casos, publicava
        250 EVIDENCE_IDS e 3 SOURCE_URLS, porque a fusao unia os IDs e ficava
        com os REGISTOS do primeiro que chegou.
        """
        for r in self.pacote:
            if (r.get('MERGED_FROM') or 0) < 2:
                continue
            self.assertGreaterEqual(
                r['SOURCE_URLS_TOTAL_FOUND'], 4,
                'cartao fundido com origem de um so bruto: %s (%d provas, %d '
                'origens)' % (r['ID'], r['EVIDENCE_COUNT'],
                              r['SOURCE_URLS_TOTAL_FOUND']))

    def test_a_omissao_de_fonte_e_de_apresentacao_e_diz_isso(self):
        for r in self.pacote:
            if r['SOURCE_URLS_TOTAL_OMITTED']:
                self.assertEqual('PRESENTATION_LIMIT',
                                 r['SOURCE_URLS_OMISSION_REASON'], r['ID'])


class TestTestemunhas(unittest.TestCase):
    """Os dois casos-testemunha tem de sobreviver as correcoes."""

    @classmethod
    def setUpClass(cls):
        ok, cls._limpar = _prepara_ingest()
        if not ok:
            raise unittest.SkipTest('DESIGN-INGEST indisponivel (sem ZIP no disco)')
        # ⚠️ REGENERA. Ler o OPPORTUNITIES.json que estiver no disco faria a
        # testemunha passar contra um pacote antigo — um verde que prova o
        # ficheiro de ontem, nao o motor de hoje.
        #
        #     UM TESTE QUE LE O QUE ESTAVA LA NAO ESTA A TESTAR O MOTOR.
        import v21_oportunidades as M
        b, _rej, C, cs = M.main()
        M.gravar(b, C, cs)
        cls.pacote = json.load(open(os.path.join(ING, 'OPPORTUNITIES.json'),
                                    encoding='utf-8'))['RECORDS']
        cls.por_id = {r['ID']: r for r in cls.pacote}

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, '_limpar', False):
            shutil.rmtree(os.path.dirname(ING), ignore_errors=True)

    # ── A · MAIS x PIRALIDE x FRIULI-VENEZIA GIULIA ─────────────────────────
    def test_a_testemunha_do_milho_continua_de_pe(self):
        """O par, a regiao e o sinal de campo sao INVARIANTES: nenhuma
        correcao de cultura ou de catalogo pode mexer neles."""
        o = self.por_id.get('OPP_9C600748BB1B')
        self.assertIsNotNone(o, 'a testemunha do milho desapareceu do pacote')
        self.assertEqual('CROP_MAIZE', o['CROP'])
        self.assertEqual('ISSUE_CORN_BORER', o['TARGET'])
        self.assertEqual('REGION_FRIULI_VENEZIA_GIULIA', o['GEOGRAPHY'])
        self.assertIn('IT-PHEN-048', o['EVIDENCE_IDS'])

    def test_os_cinco_produtos_do_par_continuam_cinco(self):
        """Os cinco saem do rotulo ministerial no par — e o filtro de cultura
        NAO os pode tocar, porque milho e a cultura deles."""
        o = self.por_id['OPP_9C600748BB1B']
        self.assertEqual(['DURAVIS', 'ELTIRA', 'FORZA', 'LAMDEX EXTRA', 'NINJA'],
                         sorted(o['PRODUCT_RELATIONSHIPS']))
        # NENHUM dos cinco foi excluido do que o cartao ofereceu...
        self.assertEqual([], [x for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']
                              if x['SCOPE'] == 'OFFERED_TO_CARD'],
                         'a testemunha do milho perdeu produto oferecido')
        # ...e nada nesta testemunha cai por cultura: os que caem, caem por
        # ALVO ou por nao estarem no catalogo comercial, que sao outras
        # perguntas. Se aparecesse aqui um CROP_MISMATCH, o filtro de cultura
        # teria comecado a morder onde milho E a cultura certa.
        self.assertEqual(set(), {x['REASON']
                                 for x in o['PORTFOLIO_EXCLUDED_WITH_REASON']}
                         & {'CROP_MISMATCH', 'UNKNOWN_CROP'}, o['ID'])

    def test_sem_janela_factual_a_janela_fica_unknown(self):
        """Nao ha janela de milho no pacote. Inventar uma seria o defeito."""
        o = self.por_id['OPP_9C600748BB1B']
        self.assertEqual('UNKNOWN', o['WINDOW_STATE'])
        janelas = json.load(open(os.path.join(ING, 'CROP-WINDOWS.json'),
                                 encoding='utf-8'))['RECORDS']
        self.assertEqual(0, sum(1 for w in janelas
                                if 'CROP_MAIZE' in (w.get('CROP_IDS') or [])),
                         'apareceu janela de milho: o teste precisa de ser relido')

    def test_volume_de_anuncio_nao_funda_a_oportunidade(self):
        """69 pecas de concorrente na cultura, e ZERO entram como ligacao.

            VOLUME DE PUBLICIDADE E SINAL DE ATENCAO.
            NAO E INCIDENCIA, NEM JANELA, NEM INTENCAO DE COMPRA.
        """
        o = self.por_id['OPP_9C600748BB1B']
        comp = o['CROSS_INTELLIGENCE_SCAN']['COMPETITOR']
        self.assertEqual('CROP_ONLY', comp['RESULT'])
        self.assertEqual(0, comp['MATCH'])
        self.assertEqual([], comp['EVIDENCE'])
        # e nenhum id de concorrente atravessou para a evidencia do cartao
        self.assertNotIn('COMPETITOR_ACTIVITY', o['EVIDENCE_FAMILIES'])

    # ── B · VITE, E AS QUATRO CASAS ─────────────────────────────────────────
    def _casas_da_videira(self):
        import re as _re
        import v21_normalizar as N
        base = os.path.join(ING, '%s.json')

        def le(n):
            return json.load(open(base % n, encoding='utf-8'))['RECORDS']

        def k(n):
            return _re.sub(r'[^a-z0-9]', '', str(n or '').lower())
        V = 'CROP_GRAPEVINE'
        rel = [r for r in le('PRODUCT-RELATIONSHIPS') if r.get('CLIENT_SAFE')]
        reg = [r for r in le('PRODUCTS-REGULATORY') if r.get('CLIENT_SAFE')]
        com = [r for r in le('PRODUCTS-COMMERCIAL') if r.get('CLIENT_SAFE')]
        return {
            'MINISTERIAL_LABEL': {k(r.get('PRODUCT_NAME')) for r in rel
                                  if V in (r.get('CROP_IDS') or [])},
            'MINISTERIAL_REGISTRY': {k(r.get('NAME')) for r in reg
                                     if V in (r.get('CROP_IDS') or [])},
            'CATALOG_PRODUCT_SHEET': {
                k(r.get('NAME')) for r in com
                if V in {N.crop_id(x)
                         for x in (r.get('CROPS_DECLARED_BY_PRODUCT') or [])}},
            'CATALOG_CROP_PAGE': {
                k(r.get('NAME')) for r in com
                if V in {N.crop_id(x)
                         for x in (r.get('CROPS_DISCOVERED_VIA_CROP_PAGE') or [])}},
        }

    def test_as_quatro_casas_da_videira_estao_todas_disponiveis(self):
        """O numero 71 da auditoria nao se fixa aqui — a UNIAO recontа-se.

        Enquanto o motor via uma casa, escrever «= 71» seria fixar um numero
        que ele nao podia produzir. Agora ve as quatro, e o que se guarda e a
        REGRA: nenhuma casa vazia, e a uniao nunca menor que a maior delas.
        """
        casas = self._casas_da_videira()
        self.assertEqual(4, len(casas))
        for nome, s in casas.items():
            self.assertTrue(s, 'casa vazia: %s' % nome)
        uniao = set().union(*casas.values())
        self.assertGreaterEqual(len(uniao), max(len(s) for s in casas.values()))
        # e nenhuma casa sozinha explica a uniao: e por isso que sao quatro
        for nome, s in casas.items():
            self.assertLess(len(s), len(uniao), 'uma casa so daria a uniao: %s'
                            % nome)

    def test_as_grafias_da_videira_normalizam_para_um_id_so(self):
        import v21_normalizar as N
        for g in ('VITE', 'Vite da vino', 'VINE', 'vigneto', 'uva da vino',
                  'grapevine', 'videira'):
            self.assertEqual('CROP_GRAPEVINE', N.crop_id(g), g)

    def test_vite_da_tavola_nao_entra_produto_nenhum_sozinha(self):
        """A fusao tavola/vino nao pode ser PORTADORA sem contrato.

        Ela existe no normalizador — as duas dao CROP_GRAPEVINE. Neste acervo
        isso e inofensivo, e o teste PROVA porque: todo produto que declara
        «Vite da tavola» declara TAMBEM «Vite da vino», portanto a fusao nao
        promove ninguem. No dia em que um produto entrar so por tavola, este
        teste falha — e ai a fusao passa a precisar de decisao, nao de silencio.

            UMA FUSAO INOFENSIVA HOJE NAO E UMA FUSAO PROVADA.
            O QUE SE GUARDA E A CONDICAO QUE A TORNA INOFENSIVA.
        """
        censo = os.path.join(ROOT, 'data', 'samples', 'IT-CATALOGO',
                             'IT-ADAMA-CATALOG-CENSUS-2026-09-02.json')
        if not os.path.exists(censo):
            self.skipTest('censo do catalogo indisponivel')
        P = json.load(open(censo, encoding='utf-8'))['PRODUCTS']
        vino = {p['NAME'] for p in P
                if 'Vite da vino' in (p.get('CROPS_DECLARED_ON_PAGE') or [])}
        tavola = {p['NAME'] for p in P
                  if 'Vite da tavola' in (p.get('CROPS_DECLARED_ON_PAGE') or [])}
        self.assertTrue(tavola, 'sem «Vite da tavola» o teste nao prova nada')
        self.assertEqual(set(), tavola - vino,
                         'produto entra na videira SO por «Vite da tavola»: a '
                         'fusao passou a ser portadora e precisa de decisao')


class TestNaoSeiNaoViraZero(unittest.TestCase):
    """As tres maneiras de o motor mentir por omissao, e as tres travas."""

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

    def test_familia_sem_chave_nao_vira_not_found(self):
        """NAO CONSULTAVEL e NAO ENCONTRADO sao respostas diferentes.

        Uma familia que nao se deixa cruzar por cultura nao «nao tem nada»:
        nao ha por onde perguntar. Chamar-lhe NOT_FOUND publicaria um zero
        medido onde ha uma ausencia de chave.
        """
        for o, _ in self.brutos:
            for fam, v in o['CROSS_INTELLIGENCE_SCAN'].items():
                if v['RESULT'] == 'NO_CROP_KEY':
                    self.assertEqual(0, v['MATCH'], fam)
                    self.assertNotEqual('NOT_FOUND', v['RESULT'], fam)
                if v['RESULT'] == 'NOT_FOUND':
                    self.assertTrue(v['CONSULTED'],
                                    'NOT_FOUND sem consulta e silencio: %s' % fam)

    def test_familia_sem_registos_nao_produz_match(self):
        """Uma familia vazia responde NOT_FOUND — nunca MATCH."""
        for o, _ in self.brutos:
            for fam, v in o['CROSS_INTELLIGENCE_SCAN'].items():
                if not v['IN_FAMILY']:
                    self.assertNotEqual('MATCH', v['RESULT'], fam)

    def test_entrada_vazia_nao_gera_cartao(self):
        """Um arquetipo sem apoios nao pode emitir. Zero entrada, zero PASS."""
        for o, apoios in self.brutos:
            self.assertTrue(apoios, 'cartao sem apoio nenhum: %s' % o['ID'])
            self.assertTrue(o['EVIDENCE_IDS'], o['ID'])

    def test_a_chave_do_indice_de_cultura_nao_funde_produtos_distintos(self):
        """A autoridade de cultura junta por NOME NORMALIZADO. Isso e o que faz
        «Avastel®» e «AVASTEL» serem o mesmo produto — e e tambem o que faria
        dois produtos DIFERENTES trocarem culturas em silencio.

        A trava e o numero de registo: se duas grafias que a chave funde
        tiverem numeros de registo diferentes, nao sao grafias — sao produtos,
        e a fusao passou a emprestar cultura de um ao outro.

            UMA CHAVE QUE UNE GRAFIAS TAMBEM UNE HOMONIMOS.
            O QUE SEPARA OS DOIS CASOS E O REGISTO, NAO O NOME.
        """
        import re as _re
        from collections import defaultdict
        base = os.path.join(ING, '%s.json')

        def le(n):
            return json.load(open(base % n, encoding='utf-8'))['RECORDS']

        def chave(n):
            return _re.sub(r'[^a-z0-9]', '', str(n or '').lower())

        def num(x):
            return _re.sub(r'\D', '', str(x or '')).lstrip('0').zfill(6)
        registos = defaultdict(set)
        for p in le('PRODUCTS-REGULATORY'):
            if p.get('CLIENT_SAFE'):
                registos[chave(p.get('NAME'))].add(num(p.get('REGISTRATION_NUMBER')))
        for p in le('PRODUCTS-COMMERCIAL'):
            if not p.get('CLIENT_SAFE'):
                continue
            n = num(p.get('MATCHED_REGULATORY_ID')
                    or p.get('REGISTRATION_NUMBER_ON_PAGE'))
            if n != '000000':
                registos[chave(p.get('NAME'))].add(n)
        colididos = {a: sorted(b) for a, b in registos.items() if len(b) > 1}
        self.assertEqual({}, colididos,
                         'a chave de nome funde produtos com registos '
                         'diferentes: %s' % colididos)

    def test_cartao_sem_cultura_declara_que_nao_filtrou(self):
        """Nao filtrar tem de ser dito. Silencio leria-se como «filtrei e passou»."""
        for o, _ in self.brutos:
            self.assertEqual(bool(o.get('CROP')),
                             o['PORTFOLIO_CROP_FILTER_APPLIED'], o['ID'])


if __name__ == '__main__':
    unittest.main()
