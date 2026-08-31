# -*- coding: utf-8 -*-
"""Regressoes da PASSAGEM DE CORRECAO PRE-ARBITRAGEM.

Cada classe trava um erro real — a maioria deles meu, encontrado pelo red team externo
ou por esta propria passagem. Nenhum teste aqui existe por volume.

Zero rede: tudo le commit congelado ou arquivo ja em disco.
"""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import refresh_correction as rc  # noqa: E402

OUT = os.path.join(ROOT, 'data', 'refresh-corrected')


def carregar(nome):
    with open(os.path.join(OUT, nome), encoding='utf-8') as f:
        return json.load(f)


class TestGrafoDerivadoNaoDigitado(unittest.TestCase):
    """`8_DEPENDENT_4_INDEPENDENT_DERIVED_NOT_HARDCODED`.

    O red team estimou 12 relacoes / 8 dependentes / 4 independentes. O numero derivado
    e outro, e o artefato ganha. O que este teste garante e que os totais saem da
    ESTRUTURA, nunca de constante escrita a mao.
    """

    def test_totais_batem_com_a_contagem_da_estrutura(self):
        g = rc.grafo_v2()
        dep = [r for r in g['RELATIONS'] if r['DEPENDENCY_TYPE'] != 'INDEPENDENT_SOURCE']
        ind = [r for r in g['RELATIONS'] if r['DEPENDENCY_TYPE'] == 'INDEPENDENT_SOURCE']
        self.assertEqual(g['RELATIONS_TOTAL'], len(g['RELATIONS']))
        self.assertEqual(g['RELATIONS_DEPENDENT'], len(dep))
        self.assertEqual(g['RELATIONS_INDEPENDENT'], len(ind))
        self.assertEqual(g['RELATIONS_TOTAL'],
                         g['RELATIONS_DEPENDENT'] + g['RELATIONS_INDEPENDENT'])

    def test_soma_por_tipo_fecha(self):
        g = rc.grafo_v2()
        self.assertEqual(sum(g['RELATIONS_BY_TYPE'].values()), g['RELATIONS_TOTAL'])

    def test_todo_tipo_esta_no_vocabulario(self):
        for r in rc.grafo_v2()['RELATIONS']:
            self.assertIn(r['DEPENDENCY_TYPE'], rc.TIPOS_DEP)


class TestFieldHistoricalScopeIn(unittest.TestCase):
    """`FIELD_HISTORICAL_SCOPE_IN` — decisao do coordenador, sem comprar segunda perna."""

    def test_escopo_entrou(self):
        fh = rc.field_historical()
        self.assertEqual(fh['FIELD_HISTORICAL_SCOPE'], 'IN')
        self.assertIn('FIELD_HISTORICAL', rc.grafo_v2()['FAMILIES_THAT_CAN_COUNT_TODAY'])

    def test_independencia_do_territorial_nao_e_comprada(self):
        fh = rc.field_historical()
        self.assertEqual(fh['INDEPENDENCE_FROM_TERRITORIAL_RAIF']['STATE'], 'NOT_PROVED')

    def test_adama_link_do_artefato_nao_vira_autorizacao(self):
        fh = rc.field_historical()
        self.assertTrue(fh['ADAMA_CONTEXT_DECLARED_IN_ARTIFACT'])
        self.assertEqual(fh['LOCAL_PRODUCT_AUTHORIZATION_PROVED'], 'NOT_MEASURED')

    def test_divergencia_de_serie_e_declarada_e_nao_escolhida(self):
        fh = rc.field_historical()
        self.assertIn('DIVERGENCIA_DECLARADA', fh['HISTORICAL_BASELINE'])
        self.assertIn('23', fh['HISTORICAL_BASELINE']['DIVERGENCIA_DECLARADA'])


class TestParserDeRecorte(unittest.TestCase):
    """`MULTI_TOKEN_SLICE_PARSER`.

    BUG REAL do refresh V1: `FR_VINE_DOWNY_MILDEW` quebrado por '_' devolvia
    CROP='VINE_DOWNY' e ISSUE='MILDEW'. Cinco dos seis recortes funcionavam por sorte.
    """

    def test_o_schema_devolve_o_par_certo(self):
        e = rc.slice_schema()
        s = e['FR_VINE_DOWNY_MILDEW']
        self.assertEqual(s['CROP'], 'VINE')
        self.assertEqual(s['ISSUE'], 'DOWNY_MILDEW')

    def test_o_parser_ingenuo_erra_e_o_teste_prova(self):
        n = rc.parser_ingenuo('FR_VINE_DOWNY_MILDEW')
        self.assertEqual(n['CROP'], 'VINE_DOWNY')
        self.assertEqual(n['ISSUE'], 'MILDEW')

    def test_os_seis_recortes_auditados_pelo_schema(self):
        e = rc.slice_schema()
        self.assertEqual(len(e), 6)
        for slug, s in e.items():
            self.assertTrue(slug.startswith(s['COUNTRY'] + '_'))
            self.assertTrue(slug.endswith('_' + s['ISSUE']))
            self.assertIn(s['CROP'], slug)

    def test_apenas_um_recorte_tem_issue_multi_token(self):
        e = rc.slice_schema()
        multi = [s for s, v in e.items() if '_' in v['ISSUE']]
        self.assertEqual(multi, ['FR_VINE_DOWNY_MILDEW'])


class TestCase001(unittest.TestCase):
    """`FUSARIUM_QUOTE_MATCHES_ISSUE` — o card do V1 exibia a citacao de SEPTORIA."""

    def _lamma(self):
        _, itens = rc.reprocessar()
        return [i for i in itens if 'LAMMA' in str(i['SOURCE_ENTITY_ID'])][0]

    def test_o_par_trigo_duro_fusarium_esta_provado(self):
        pares = self._lamma()['CROP_ISSUE_PAIRING']['PAIRS_PROVEN']
        alvo = [p for p in pares if p['CROP'] == 'DURUM_WHEAT' and p['ISSUE'] == 'FUSARIUM']
        self.assertTrue(alvo, 'DURUM_WHEAT x FUSARIUM precisa fechar dentro da passagem')

    def test_a_passagem_do_par_menciona_fusarium_e_trigo_duro(self):
        pares = self._lamma()['CROP_ISSUE_PAIRING']['PAIRS_PROVEN']
        alvo = [p for p in pares if p['CROP'] == 'DURUM_WHEAT'][0]
        t = rc.norm(alvo['PASSAGE'])
        self.assertIn('fusario', t, 'a citacao precisa sustentar o problema do caso')
        self.assertIn('frumento duro', t)

    def test_a_citacao_de_septoria_nao_serve_ao_caso_de_fusarium(self):
        pares = self._lamma()['CROP_ISSUE_PAIRING']['PAIRS_PROVEN']
        for p in pares:
            if p['ISSUE'] == 'FUSARIUM':
                self.assertNotIn('septoria rimane la patologia', rc.norm(p['PASSAGE']))


class TestPareamentoCulturaProblema(unittest.TestCase):
    """`CROP_ISSUE_PAIRING_NOT_PROVEN` + `MULTI_BULLETIN_DOCUMENT_GUARD`."""

    def test_produto_cartesiano_e_evitado(self):
        _, itens = rc.reprocessar()
        lamma = [i for i in itens if 'LAMMA' in str(i['SOURCE_ENTITY_ID'])][0]
        p = lamma['CROP_ISSUE_PAIRING']
        self.assertGreater(p['PAIRS_CARTESIAN_AVOIDED'], 0)
        self.assertLess(len([x for x in p['PAIRS_PROVEN'] if x['CROP'] != 'DURUM_WHEAT']),
                        p['PAIRS_TESTED'])

    def test_vinha_nao_herda_fusarium_nem_cereal_herda_mildio(self):
        _, itens = rc.reprocessar()
        lamma = [i for i in itens if 'LAMMA' in str(i['SOURCE_ENTITY_ID'])][0]
        pares = set((p['CROP'], p['ISSUE']) for p in lamma['CROP_ISSUE_PAIRING']['PAIRS_PROVEN'])
        self.assertNotIn(('VINE', 'FUSARIUM'), pares)
        self.assertNotIn(('CEREAL', 'DOWNY_MILDEW'), pares)

    def test_documentos_multi_boletim_sao_marcados(self):
        _, itens = rc.reprocessar()
        self.assertGreater(sum(1 for i in itens if i['MULTI_BULLETIN_DOCUMENT']), 0)

    def test_item_sem_par_sai_como_nao_provado(self):
        _, itens = rc.reprocessar()
        sem = [i for i in itens if not i['CROP_ISSUE_PAIRING']['PAIRS_PROVEN']]
        for i in sem:
            self.assertEqual(i['CROP_ISSUE_PAIRING']['STATE'], 'CROP_ISSUE_PAIRING_NOT_PROVEN')


class TestSemanticMismatch(unittest.TestCase):
    """`SEMANTIC_MISMATCH_NOT_CORROBORATION` e `SAME_INDEX_NOT_SAME_EVIDENCE`."""

    def test_registro_e_campo_nao_corroboram_a_mesma_proposicao(self):
        g = rc.grafo_v2()
        r = [x for x in g['RELATIONS']
             if x['FROM'] == 'NATIONAL_REGISTRATION_FOR_PAIR'][0]
        self.assertEqual(r['DEPENDENCY_TYPE'], 'SEMANTIC_DEPENDENCY')
        self.assertIn('SEMANTIC_MISMATCH_NOT_CORROBORATION', r['WHY'])

    def test_mesmo_indice_nao_e_mesma_evidencia(self):
        g = rc.grafo_v2()
        self.assertIn('SAME_INDEX != SAME_EVIDENCE', g['LAWS'])
        r = [x for x in g['RELATIONS'] if x['TO'] == 'OPENALEX_INDEX'][0]
        self.assertEqual(r['DEPENDENCY_TYPE'], 'SOURCE_DEPENDENCY')

    def test_tres_tipos_de_convergencia_nunca_somam(self):
        k = rc.grafo_v2()['CONVERGENCE_KINDS']
        for t in ('PHENOMENON_CONVERGENCE', 'IDENTITY_CONVERGENCE', 'CONTEXTUAL_ALIGNMENT'):
            self.assertIn(t, k)
        self.assertIn('NUNCA_SOMAR', k)

    def test_convergencia_exige_mesma_proposicao(self):
        self.assertIn('CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE',
                      rc.grafo_v2()['LAWS'])


class TestIdentityChain(unittest.TestCase):
    """A cadeia de identidade nao e convergencia de caso."""

    def test_nao_se_chama_convergencia_de_caso(self):
        ic = rc.identity_chain()
        self.assertEqual(ic['IS_NOT'], 'CASE_MULTI_SIGNAL_CONVERGENCE')
        self.assertEqual(ic['DOES_NOT_REQUIRE'], ['CROP', 'ISSUE'])

    def test_nao_prova_campo_nem_venda(self):
        for x in ('FIELD_PROBLEM', 'DEMAND', 'SALES', 'MARKET_MOVEMENT'):
            self.assertIn(x, rc.identity_chain()['DOES_NOT_PROVE'])

    def test_conservacao_de_tuplas(self):
        ic = rc.identity_chain()
        self.assertEqual(ic['PROVED_TUPLES'] + ic['REJECTED_TUPLES'] + ic['NOT_KNOWN_TUPLES'],
                         ic['CANDIDATE_TUPLES'])


class TestRegulatoryDeadline(unittest.TestCase):
    """`EXPIRY_NOT_WITHDRAWAL`."""

    def test_as_duas_leis_viajam(self):
        rd = rc.regulatory_deadlines()
        self.assertIn('EXPIRY != WITHDRAWAL', rd['LAWS'])
        self.assertIn('EXPIRY_DATE_REACHED != PRODUCT_DISCONTINUED', rd['LAWS'])

    def test_acao_permitida_e_revisao_nao_alerta(self):
        rd = rc.regulatory_deadlines()
        self.assertIn('REVIEW', rd['PERMITTED_ACTION'])
        self.assertIn('WILL DISAPPEAR', rd['FORBIDDEN_ACTION'])

    def test_nao_e_dashboard(self):
        self.assertIn('nunca como', rc.regulatory_deadlines()['NOT_A_DASHBOARD'])


class TestTempoEObservacao(unittest.TestCase):
    """`OBSERVATION_STAGE_NOT_CURRENT_STAGE` e `PIPELINE_LATENCY_NOT_OBSERVATION_AGE`."""

    def test_estagio_na_observacao_nao_promove_estagio_de_hoje(self):
        _, itens = rc.reprocessar()
        provados = [i for i in itens
                    if i['PHENOLOGY']['CROP_STAGE_AT_OBSERVATION'] == 'PROVED']
        self.assertTrue(provados, 'a fixture precisa ter ao menos um item com fenologia')
        for i in provados:
            self.assertEqual(i['PHENOLOGY']['CURRENT_CROP_STAGE_TODAY'], 'NOT_PROVED')
            self.assertEqual(i['PHENOLOGY']['CURRENT_APPLICATION_WINDOW'], 'NOT_PROVED')

    def test_o_escopo_do_texto_e_declarado(self):
        _, itens = rc.reprocessar()
        for i in itens:
            self.assertEqual(i['PHENOLOGY']['TEXT_SCOPE'],
                             'DOCUMENT_EXCERPT + EVIDENCE_PASSAGES')
            self.assertFalse(i['PHENOLOGY']['FULL_BODY_PRESERVED'],
                             'o corpo completo NAO esta preservado; medir sobre inteiro '
                             'devolveria zero em tudo')

    def test_latencia_declara_o_limite_da_captura_unica(self):
        s = carregar('SOURCE-LATENCY-EAME.json')
        self.assertIn('LIMITE_DESTA_MEDICAO', s)
        self.assertIn('captura unica', s['LIMITE_DESTA_MEDICAO'])

    def test_latencia_so_existe_com_as_duas_datas(self):
        _, itens = rc.reprocessar()
        for i in itens:
            if i['LATENCY']['STATE'] == 'MEASURED':
                self.assertIsNotNone(i['LATENCY']['SOURCE_LATENCY_DAYS'])
            else:
                self.assertIsNone(i['LATENCY']['SOURCE_LATENCY_DAYS'])


class TestCentralUserAbsorption(unittest.TestCase):
    """`CENTRAL_USER_ABSORPTION_GUARD`.

    Market Development e usuario central por decisao arquitetonica — NAO porque recebeu
    todas as linhas da tabela de acao. Ocupar 100% das linhas nao prova centralidade.
    """

    def test_o_guard_esta_escrito_no_artefato(self):
        a = carregar('ACTION-CANDIDATES.json')
        self.assertIn('CENTRAL_USER_ABSORPTION_GUARD', a)
        self.assertIn('NAO porque', a['CENTRAL_USER_ABSORPTION_GUARD'])

    def test_existe_acao_cujo_dono_nao_e_market_development(self):
        a = carregar('ACTION-CANDIDATES.json')
        donos = set()
        for c in a['CANDIDATES']:
            donos.update(c['INFERENCES']['OWNERS'])
        self.assertTrue(donos - {'MARKET_DEVELOPMENT'},
                        'se MD e o unico dono de tudo, a tabela nao esta medindo nada')

    def test_tipo_de_acao_separa_negocio_de_sistema(self):
        a = carregar('ACTION-CANDIDATES.json')
        for t in ('BUSINESS_DECISION', 'SYSTEM_DECISION', 'INVESTIGATION'):
            self.assertIn(t, a['ACTION_TYPES'])


class TestMedidoNaoEscrito(unittest.TestCase):
    """`MEASURED_NOT_WRITTEN` — julgamento de produto nao pode passar por medicao."""

    def test_cada_candidato_separa_fato_de_inferencia_e_julgamento(self):
        a = carregar('ATTENTION-CANDIDATES.json')
        self.assertTrue(a['CANDIDATES'])
        for c in a['CANDIDATES']:
            for k in ('EVIDENCE_INPUTS', 'DERIVATION_RULE', 'FACTS', 'INFERENCES',
                      'JUDGMENT_REQUIRED'):
                self.assertIn(k, c, '%s sem %s' % (c['CANDIDATE_ID'], k))

    def test_estado_de_atencao_e_do_vocabulario(self):
        a = carregar('ATTENTION-CANDIDATES.json')
        ok = {'ATTENTION_READY', 'ATTENTION_CANDIDATE_TEST',
              'VALID_EVIDENCE_NOT_ATTENTION_READY'}
        for c in a['CANDIDATES']:
            self.assertIn(c['ATTENTION_STATE'], ok)

    def test_nenhum_score_agregado(self):
        r = carregar('FINAL-INTELLIGENCE-REFRESH-EAME-V2.json')
        texto = json.dumps(r, ensure_ascii=False).upper()
        for proibido in ('OPPORTUNITY_SCORE', 'SALES_SCORE', 'RELEVANCE_SCORE'):
            self.assertNotIn(proibido, texto)


class TestSemRede(unittest.TestCase):
    """`NO_NETWORK_IN_CORRECTION_PASS`.

    A primeira versao deste teste procurava a palavra 'apify' no texto do arquivo e
    reprovava por causa de um COMENTARIO que dizia "nenhum Apify". Procurar substring
    em codigo-fonte confunde mencao com uso. Agora a checagem e por AST: importa? chama?
    """

    MODULOS_DE_REDE = {'requests', 'urllib', 'http', 'httpx', 'socket', 'ftplib',
                       'telnetlib', 'aiohttp', 'selenium', 'websocket', 'smtplib'}
    BINARIOS_DE_REDE = {'curl', 'wget', 'apify', 'chrome', 'chromium'}

    def _arvore(self, nome):
        import ast
        p = os.path.join(ROOT, 'scripts', nome)
        with open(p, encoding='utf-8') as f:
            return ast.parse(f.read(), filename=p)

    def test_nenhum_modulo_de_rede_e_importado(self):
        import ast
        for nome in ('refresh_correction.py', 'refresh_correction_run.py'):
            for no in ast.walk(self._arvore(nome)):
                if isinstance(no, ast.Import):
                    for a in no.names:
                        self.assertNotIn(a.name.split('.')[0], self.MODULOS_DE_REDE,
                                         '%s importa %s' % (nome, a.name))
                elif isinstance(no, ast.ImportFrom) and no.module:
                    self.assertNotIn(no.module.split('.')[0], self.MODULOS_DE_REDE,
                                     '%s importa de %s' % (nome, no.module))

    def test_o_unico_subprocesso_e_git_de_leitura(self):
        import ast
        permitidos = {('git', 'show'), ('git', 'rev-parse'), ('git', 'cat-file')}
        achados = []
        for nome in ('refresh_correction.py', 'refresh_correction_run.py'):
            for no in ast.walk(self._arvore(nome)):
                if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) \
                        and no.func.attr == 'run' and no.args:
                    arg = no.args[0]
                    if isinstance(arg, ast.List) and len(arg.elts) >= 2:
                        vals = [e.value for e in arg.elts[:2]
                                if isinstance(e, ast.Constant)]
                        if len(vals) == 2:
                            achados.append(tuple(vals))
        self.assertTrue(achados, 'a passagem precisa mesmo chamar git para ler os freezes')
        for a in achados:
            self.assertIn(a, permitidos, 'subprocesso nao permitido: %s' % (a,))
            self.assertNotIn(a[0], self.BINARIOS_DE_REDE)

    def test_os_artefatos_declaram_zero_rede(self):
        r = carregar('FINAL-INTELLIGENCE-REFRESH-EAME-V2.json')
        self.assertEqual(r['NEW_COLLECTION'], 'NO')
        self.assertEqual(r['NETWORK_REQUESTS'], 0)

    def test_toda_entrada_vem_de_commit_fixo_ou_disco(self):
        for commit, path in rc.PIN.values():
            self.assertTrue(commit and path)
            o = subprocess.run(['git', 'cat-file', '-e', '%s:%s' % (commit, path)],
                               cwd=ROOT, capture_output=True)
            self.assertEqual(o.returncode, 0, '%s:%s nao existe' % (commit, path))


class TestRotulosItalianos(unittest.TestCase):
    """Manifesto completo com PDF ausente nao e reprocessamento possivel."""

    def test_disponibilidade_local_e_medida_e_nao_assumida(self):
        r = carregar('FINAL-INTELLIGENCE-REFRESH-EAME-V2.json')
        lab = r['ITALIAN_LABELS']
        self.assertIsInstance(lab['LOCAL_LABEL_PDFS_AVAILABLE_NOW'], int)
        self.assertEqual(lab['RECONSTRUCTION_EXECUTED'], 'NO')

    def test_sha_preservado_nao_substitui_o_arquivo(self):
        lab = carregar('FINAL-INTELLIGENCE-REFRESH-EAME-V2.json')['ITALIAN_LABELS']
        self.assertIn('NAO substitui o arquivo', lab['NOTE'])


if __name__ == '__main__':
    unittest.main()
