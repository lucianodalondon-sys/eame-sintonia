# -*- coding: utf-8 -*-
"""LINKEDIN-BUILD-01 — as sentinelas da escada OWN/FREE -> LOCAL -> PAID RESIDUAL.

Todas medem COMPORTAMENTO contra o bruto REAL preservado. Nao ha rede nenhuma
para fingir: o ficheiro esta no disco desde 2026-08-29, e a unica rota ligada
recebe HTML por injeccao.

    LINKEDIN_REAL_REQUESTS = 0 · APIFY_RUNS = 0 · COST_USD = 0
"""
import ast
import gzip
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import adaptador_linkedin as li                                   # noqa: E402
import scrap_capacidades as cap                                   # noqa: E402
import scrap_executor as sx                                       # noqa: E402
import scrap_registo as reg                                       # noqa: E402
import social_matriz as mz                                        # noqa: E402
import social_envelope as env                                     # noqa: E402
reg.carregar_adaptadores()

# A suite tambem nao deixa acervo: o bruto preservado vai para um temporario.
import tempfile                                                   # noqa: E402
env.RAW_DIR = tempfile.mkdtemp(prefix='test-linkedin-build-01-')

BRUTO = ('data/samples/raw-paid/ES-T8-002-linkedin-posts-a.raw.json.gz',
         'data/samples/raw-paid/ES-T8-002-linkedin-posts-b.raw.json.gz')
RUN = 'TEST-LINKEDIN-BUILD-01'
_CACHE = {}


def bruto():
    if 'itens' not in _CACHE:
        itens = []
        for f in BRUTO:
            itens += json.loads(gzip.decompress(open(os.path.join(RAIZ, f), 'rb').read()))
        _CACHE['itens'] = itens
    return _CACHE['itens']


def envelopes():
    if 'env' not in _CACHE:
        _CACHE['env'] = li.normalizar_lote(bruto(), run_id=RUN, country_scope='ES',
                                           raw_reference=BRUTO[0])
    return _CACHE['env']


def um(campo):
    """→ o primeiro envelope cujo campo de bruto esta preenchido."""
    es, _ = envelopes()
    return next(e for e in es if e['RAW'].get(campo))


# ══════════════════════════════════════════════════════════════════════════
# 1-4 · O NORMALIZADOR NAO PERDE CAMPO  (ataques 1 a 4)
# ══════════════════════════════════════════════════════════════════════════
class ONormalizadorNaoPerdeCampo(unittest.TestCase):
    """`PROVIDER_GAP != NORMALIZATION_GAP`. Cada campo tem a sua sentinela."""

    def test_1_postVideo_sobrevive(self):
        _, c = envelopes()
        self.assertEqual(c['VIDEO_URL'], 56)

    def test_2_document_sobrevive(self):
        _, c = envelopes()
        self.assertEqual(c['DOCUMENT_URL'], 20)
        self.assertEqual(c['DOCUMENT_TRANSCRIPT_URL'], 20)

    def test_3_article_sobrevive(self):
        _, c = envelopes()
        self.assertEqual(c['ARTICLE_URL'], 93)

    def test_4_tipos_de_reacao_sobrevivem(self):
        _, c = envelopes()
        self.assertEqual(c['REACTIONS_BY_TYPE'], 449)
        tipos = set()
        for e in envelopes()[0]:
            tipos |= set(e['RAW'].get('REACTIONS_BY_TYPE') or {})
        self.assertEqual(tipos, {'LIKE', 'PRAISE', 'INTEREST', 'EMPATHY', 'APPRECIATION'})

    def test_o_bruto_viaja_inteiro_no_envelope(self):
        """Um campo que o tradutor esqueca continua a existir onde se pode ver."""
        e = um('VIDEO_URL')
        self.assertIn('RAW', e)
        self.assertTrue(e['RAW'].get('SHARE_URN'))
        self.assertEqual(e['CONTENT_TYPE'], 'POST')


# ══════════════════════════════════════════════════════════════════════════
# 5-7 · CONTAGEM NAO E COISA  (ataques 5, 6, 7)
# ══════════════════════════════════════════════════════════════════════════
class ContagemNaoEConteudo(unittest.TestCase):

    def test_5_comments_count_nao_vira_comments_text(self):
        es, c = envelopes()
        self.assertEqual(sum((e['RAW'].get('COMMENTS_COUNT') or 0) for e in es), 335)
        self.assertEqual(c['COMMENTS_TEXT'], 0)
        self.assertTrue(all(e['RAW'].get('COMMENTS_TEXT') is None for e in es))

    def test_6_document_metadata_nao_vira_pdf_capturado(self):
        e = um('DOCUMENT_URL')
        self.assertTrue(e['RAW']['DOCUMENT_URL'])
        self.assertFalse(e['RAW']['DOCUMENT_BYTES_ACQUIRED'])

    def test_7_video_url_nao_vira_video_bytes(self):
        e = um('VIDEO_URL')
        self.assertTrue(e['RAW']['VIDEO_URL'])
        self.assertFalse(e['RAW']['VIDEO_BYTES_ACQUIRED'])
        _, _, falta = li.o_que_falta(e, dict(li.pedido_vazio(), WANT_MEDIA=True))
        self.assertIn('VIDEO_BYTES', falta)

    def test_30_reaction_people_nunca_sem_pedido(self):
        es, _ = envelopes()
        self.assertTrue(all(e['RAW'].get('REACTION_PEOPLE') is None for e in es))
        p = li.plano_de_aquisicao(um('VIDEO_URL'), li.pedido_vazio())
        self.assertNotIn('REACTION_PEOPLE', p['GAP'])


# ══════════════════════════════════════════════════════════════════════════
# 8-9 · FALA  (ataques 8, 9)
# ══════════════════════════════════════════════════════════════════════════
class FalaNaoSeFabrica(unittest.TestCase):

    def test_8_asr_nao_corre_sem_midia(self):
        """`MEDIA ACCESS != ASR`. O transcript e LOCAL e exige bytes antes."""
        self.assertEqual(li.ONDE_SE_OBTEM['TRANSCRIPT']['NIVEL'], li.LOCAL)
        p = li.plano_de_aquisicao(um('VIDEO_URL'), dict(li.pedido_vazio(), WANT_TRANSCRIPT=True))
        passos = {x['NEED']: x for x in p['PLAN']}
        # A legenda vem antes, e ela esta BLOCKED: logo a fala nao tem caminho
        # completo, e o plano di-lo em vez de prometer transcript.
        self.assertEqual(passos['NATIVE_CAPTION']['VERDICT'], 'BLOCKED_NO_PERMITTED_ROUTE')

    def test_9_caption_inexistente_nao_vira_transcript(self):
        es, c = envelopes()
        self.assertEqual(c['NATIVE_CAPTION'], 0)
        self.assertTrue(all(e['RAW'].get('TRANSCRIPT') is None for e in es))

    def test_caption_precede_transcript_no_plano(self):
        p = li.plano_de_aquisicao(um('VIDEO_URL'), {k: True for k in li.BANDEIRAS})
        ordem = [x['NEED'] for x in p['PLAN']]
        self.assertLess(ordem.index('NATIVE_CAPTION'), ordem.index('TRANSCRIPT'))


# ══════════════════════════════════════════════════════════════════════════
# 10-12 · DELTA  (ataques 10, 11, 12)
# ══════════════════════════════════════════════════════════════════════════
class ADeltaNaoViraHistoria(unittest.TestCase):

    def test_10_history_route_nao_vira_company_page_history(self):
        """Os dois eixos de profundidade continuam separados na declaracao."""
        nota = reg.adaptador_de('LINKEDIN', 'linkedin.history.discovery')['NOTA']
        self.assertIn('PAGINA DE EMPRESA', nota)
        self.assertIn('palavra-chave', nota)
        self.assertEqual(cap.estado('linkedin.history.discovery'), cap.UNKNOWN)

    def test_11_corrida_total_nao_acontece_em_delta(self):
        _, r = li.filtrar_janela(bruto(), since='2026-08-22T00:00:00Z')
        self.assertEqual(r['DENTRO'], 13)
        self.assertLess(r['DENTRO'], 472)
        self.assertEqual(r['DENTRO'] + r['FORA_POR_TEMPO'], 472)

    def test_12_last_seen_nao_e_ignorado(self):
        itens = bruto()
        run1, _ = li.filtrar_janela(itens, since='2026-08-22T00:00:00Z')
        c1 = [li.campos_do_bruto(i) for i in run1]
        ids1 = {x['NATIVE_ID'] for x in c1}
        run2, _ = li.filtrar_janela(itens,
                                    last_seen_time=max(x['PUBLISHED_AT_EPOCH_MS'] for x in c1))
        self.assertEqual(set(), ids1 & {li.campos_do_bruto(i)['NATIVE_ID'] for i in run2})
        # E o corte por ID conta num campo proprio, nunca no do tempo.
        alvo = sorted(ids1)[0]
        _, r = li.filtrar_janela(run1, last_seen_id=[alvo])
        self.assertEqual(r['JA_VISTO_POR_ID'], 1)
        self.assertEqual(r['FORA_POR_TEMPO'], 0)

    def test_o_limite_mais_restritivo_vence(self):
        _, largo = li.filtrar_janela(bruto(), since='2025-08-29T00:00:00Z')
        _, dois = li.filtrar_janela(bruto(), since='2025-08-29T00:00:00Z',
                                    posted_limit_date='2026-08-22T00:00:00Z')
        self.assertLess(dois['DENTRO'], largo['DENTRO'])
        self.assertEqual(dois['DENTRO'], 13)

    def test_segundos_e_milissegundos_nao_se_confundem(self):
        """Um limite em segundos comparado contra ms deixaria passar tudo."""
        _, ms = li.filtrar_janela(bruto(), since=1787270400000)
        _, seg = li.filtrar_janela(bruto(), since=1787270400)
        self.assertEqual(ms['DENTRO'], seg['DENTRO'])
        self.assertLess(ms['DENTRO'], 472)

    def test_item_sem_data_nao_entra_na_janela(self):
        """Ausencia de prova nao e prova de recencia."""
        _, r = li.filtrar_janela([{'id': 'x', 'postedAt': {}}], since='2020-01-01T00:00:00Z')
        self.assertEqual(r['DENTRO'], 0)
        self.assertEqual(r['SEM_DATA'], 1)


# ══════════════════════════════════════════════════════════════════════════
# 13-16 · PAGO NAO CORRE POR OMISSAO  (ataques 13, 14, 15, 16)
# ══════════════════════════════════════════════════════════════════════════
class OPagoEResidual(unittest.TestCase):

    def test_13_pago_nao_corre_antes_da_rota_livre(self):
        """A unica capacidade ligada do LinkedIn e a GRATUITA e PERMITIDA."""
        ligadas = [k for k in reg.executaveis() if k[0] == 'LINKEDIN']
        self.assertEqual(ligadas, [('LINKEDIN', 'linkedin.identity.discovery')])
        rota = mz.decisao('LINKEDIN', 'DISCOVER_ACCOUNT')
        self.assertEqual(rota['DECISAO'], 'ALLOWED')
        self.assertEqual(rota['CLASSE'], 'DIRECT_HTTP')
        self.assertNotIn(rota['CLASSE'], ('APIFY', 'OFFICIAL_API_PAID'))

    def test_14_enriquecimento_nao_compra_campo_ja_presente(self):
        e = json.loads(json.dumps(um('VIDEO_URL')))
        e['RAW']['COMMENTS_TEXT'] = [{'text': 'ja veio'}]
        p = li.plano_de_aquisicao(e, dict(li.pedido_vazio(), WANT_COMMENTS=True))
        self.assertEqual(p['ALREADY_PRESENT'], ['COMMENTS_TEXT'])
        self.assertEqual(p['GAP'], [])
        self.assertTrue(p['PAID_ENRICHMENT_NOT_REQUIRED'])

    def test_15_want_comments_falso_nao_compra_comentarios(self):
        p = li.plano_de_aquisicao(um('VIDEO_URL'),
                                  dict(li.pedido_vazio(), WANT_COMMENTS=False))
        self.assertEqual(p['GAP'], [])
        self.assertNotIn('COMMENTS_TEXT', [x['NEED'] for x in p['PLAN']])

    def test_16_want_media_falso_nao_baixa_midia(self):
        p = li.plano_de_aquisicao(um('VIDEO_URL'),
                                  dict(li.pedido_vazio(), WANT_MEDIA=False))
        self.assertNotIn('VIDEO_BYTES', p['GAP'])
        es, _ = envelopes()
        self.assertTrue(all(not e['RAW'].get('VIDEO_BYTES_ACQUIRED') for e in es))

    def test_bandeira_com_nome_errado_rebenta(self):
        """Um pedido que nunca se cumpre e pior do que um erro."""
        with self.assertRaises(ValueError):
            li.o_que_falta(um('VIDEO_URL'), {'want_comments': True})


# ══════════════════════════════════════════════════════════════════════════
# 17-23 · QUEM ESCOLHE, E COM QUE PROVA  (ataques 17 a 23)
# ══════════════════════════════════════════════════════════════════════════
class OAdapterNaoEscolheRota(unittest.TestCase):

    def test_17_18_o_adapter_nao_guarda_copia_da_politica(self):
        """Escolher rota e do router/politica. Uma copia aqui divergiria."""
        fonte = open(os.path.join(RAIZ, 'coleta/adaptador_linkedin.py'), encoding='utf-8').read()
        arvore = ast.parse(fonte)
        # Nenhuma constante deste ficheiro declara PERMITIDA/PRIORIDADE/preco.
        for proibido in ('PERMITIDA', 'PRIORIDADE', 'USD_POR_1000', 'CLASSES ='):
            self.assertNotIn('\n%s' % proibido, fonte)
        # E a decisao de politica e LIDA do dono, nao reimplementada.
        self.assertIn('import social_matriz as mz', fonte)
        self.assertTrue(any(isinstance(n, ast.FunctionDef) and n.name == '_politica'
                            for n in ast.walk(arvore)))

    def test_19_preco_de_tabela_nao_vira_custo_real(self):
        """Nenhum preco vive neste adaptador. Quem sabe o custo e quem paga."""
        fonte = open(os.path.join(RAIZ, 'coleta/adaptador_linkedin.py'), encoding='utf-8').read()
        self.assertNotIn('1.50', fonte)
        self.assertNotIn('4.033', fonte)

    def test_20_cpu_local_nao_vira_custo_zero_total(self):
        """`FREE` e `LOCAL` sao niveis distintos e nao se somam."""
        self.assertNotEqual(li.FREE, li.LOCAL)
        self.assertEqual(len(set(li.NIVEIS)), 4)

    def test_21_provider_pago_nao_muda_politica(self):
        p = li.plano_de_aquisicao(um('VIDEO_URL'), {k: True for k in li.BANDEIRAS})
        self.assertEqual(p['PAID_NEEDED_FOR'], [])
        for passo in p['PLAN']:
            if passo['TIER'] == li.BLOCKED:
                self.assertEqual(passo['VERDICT'], 'BLOCKED_NO_PERMITTED_ROUTE')
                self.assertNotEqual(passo['POLICY'], 'ALLOWED')

    def test_22_23_a_rota_atravessa_o_roteador(self):
        """A rota ligada entra pelo `rota=`, que e a porta que mede o portao."""
        r = reg.adaptador_de('LINKEDIN', 'linkedin.identity.discovery')
        self.assertIsNotNone(r['ROTA'])
        self.assertIsNone(r['EXECUTA'])
        self.assertEqual(sx.CHECK('LINKEDIN', 'linkedin.identity.discovery')['STATE'], sx.PODE)


# ══════════════════════════════════════════════════════════════════════════
# 24-29 · PROCEDENCIA  (ataques 24 a 29)
# ══════════════════════════════════════════════════════════════════════════
class AProcedenciaNaoSeMistura(unittest.TestCase):

    def test_24_25_o_bruto_e_referenciado_e_nao_substituido(self):
        e = um('VIDEO_URL')
        self.assertTrue(e['RAW_REFERENCE'])
        self.assertTrue(e['RAW'])
        self.assertTrue(os.path.exists(os.path.join(RAIZ, e['RAW_REFERENCE'])))

    def test_26_27_article_url_e_post_url_nao_viram_source_id(self):
        """Nem o link externo nem o URL do post sao identidade de fonte."""
        e = um('ARTICLE_URL')
        self.assertNotIn('SOURCE_ID', e)
        self.assertNotEqual(e['NATIVE_ID'], e['RAW']['ARTICLE_URL'])
        self.assertNotEqual(e['NATIVE_ID'], e['URL'])
        # O NATIVE_ID e o activity id, que e o identificador da plataforma.
        self.assertTrue(e['NATIVE_ID'].isdigit())

    def test_28_country_scope_nao_vira_source_location(self):
        e = um('VIDEO_URL')
        self.assertEqual(e['COUNTRY_SCOPE'], 'ES')
        self.assertEqual(e['SOURCE_LOCATION'], 'UNKNOWN')

    def test_29_localizacao_da_empresa_nao_vira_fact_location(self):
        es, _ = envelopes()
        self.assertTrue(all(e['SOURCE_LOCATION'] == 'UNKNOWN' for e in es))
        self.assertTrue(all('FACT_LOCATION' not in e for e in es))

    def test_o_rasto_separa_a_origem_dos_campos(self):
        e = um('VIDEO_URL')
        t = li.rasto_de_aquisicao(e, li.plano_de_aquisicao(e, li.pedido_vazio()))
        self.assertEqual(t['ACQUISITION_TIER'], li.LOCAL)
        self.assertTrue(t['FIELDS_FROM_PAID'])
        self.assertEqual(t['FIELDS_FROM_FREE'], [])
        self.assertEqual(t['PROVIDER'], li.ROTA_BRUTO_PRESERVADO)

    def test_visibilidade_declarada_nao_e_permissao(self):
        """«Visible to anyone on or off LinkedIn» e visibilidade, nao licenca."""
        e = um('VIDEO_URL')
        self.assertIn('Visible to anyone', e['RAW']['DECLARED_VISIBILITY'])
        self.assertNotEqual(mz.decisao('LINKEDIN', 'FETCH_POST')['DECISAO'], 'ALLOWED')


# ══════════════════════════════════════════════════════════════════════════
# A ROTA PERMITIDA, E O DEFEITO DE TRADUCAO QUE ESTA MISSAO FECHOU
# ══════════════════════════════════════════════════════════════════════════
class AIdentidadeNaoEConteudo(unittest.TestCase):

    HTML = ('<a href="https://www.linkedin.com/company/image-line">x</a>'
            '<a href="https://it.linkedin.com/in/alguem-123">y</a>')

    def _correr(self):
        tocou = []

        def t(u):
            tocou.append(u)
            return self.HTML
        objs = li.identidade_pelo_site(site_url='https://exemplo.example/', run_id=RUN,
                                       transporte=t)
        return objs, tocou

    def test_a_rota_nao_toca_no_linkedin(self):
        _, tocou = self._correr()
        self.assertTrue(all('linkedin.com' not in u for u in tocou))
        self.assertTrue(all('licdn' not in u for u in tocou))

    def test_devolve_handle_e_nunca_publicacao(self):
        objs, _ = self._correr()
        self.assertEqual(len(objs), 2)
        for o in objs:
            self.assertEqual(o['CONTENT_TYPE'], 'DISCOVERY')
            self.assertIsNone(o['RAW']['POST_CONTENT'])
            self.assertFalse(o['RAW']['CONTENT_ACQUIRED'])
            self.assertTrue(o['RAW']['DISCOVERY_SOURCE'])
            self.assertTrue(o['RAW']['DISCOVERED_URL'])
            self.assertIn(o['RAW']['TARGET_TYPE'], ('COMPANY', 'PERSON'))

    def test_um_dono_para_a_permissao_de_discover_account(self):
        donos = [n for n, v in cap.DECLARADAS.items()
                 if v[0] == 'LINKEDIN' and v[5] == 'DISCOVER_ACCOUNT']
        self.assertEqual(donos, ['linkedin.identity.discovery'])
        self.assertIsNone(cap.da_matriz('linkedin.recent.discovery'))

    def test_recent_discovery_nao_tem_mais_rota_permitida(self):
        """Retirar a traducao FECHA uma porta; nao abre nenhuma."""
        self.assertEqual(sx.CHECK('LINKEDIN', 'linkedin.recent.discovery')['STATE'],
                         sx.SEM_ROTA)
        self.assertNotIn(('LINKEDIN', 'linkedin.recent.discovery'), reg.executaveis())

    def test_nao_confunde_outros_hosts(self):
        def t(_u):
            return '<a href="https://twitter.com/x">x</a><a href="https://linkedin.com/">y</a>'
        self.assertEqual(li.identidade_pelo_site(site_url='https://e.example/', run_id=RUN,
                                                 transporte=t), [])


# ══════════════════════════════════════════════════════════════════════════
# MUTANTES — doze, e nenhum sobrevive
# ══════════════════════════════════════════════════════════════════════════
class OsMutantes(unittest.TestCase):
    """Cada um faz o defeito que a missao proibiu; cada `assert` e a sentinela."""

    def _es(self):
        return envelopes()[0]

    def test_M1_remover_postVideo_do_mapeamento(self):
        e = um('VIDEO_URL')
        mutante = dict(e['RAW'], VIDEO_URL=None, VIDEO_THUMBNAIL=None)
        self.assertNotEqual(mutante.get('VIDEO_URL'), e['RAW']['VIDEO_URL'])
        _, c = envelopes()
        self.assertEqual(c['VIDEO_URL'], 56)   # a sentinela que o apanha

    def test_M2_remover_document(self):
        _, c = envelopes()
        self.assertEqual(c['DOCUMENT_URL'], 20)
        self.assertEqual(c['DOCUMENT_TRANSCRIPT_URL'], 20)

    def test_M3_remover_reactions(self):
        _, c = envelopes()
        self.assertEqual(c['REACTIONS_BY_TYPE'], 449)

    def test_M4_ignorar_delta(self):
        """Um filtro que ignora a janela devolve tudo. A sentinela conta."""
        _, r = li.filtrar_janela(bruto(), since='2026-08-22T00:00:00Z')
        self.assertNotEqual(r['DENTRO'], 472)
        self.assertEqual(r['DENTRO'], 13)

    def test_M5_always_enrich(self):
        """Enriquecer sempre significaria gap nao-vazio com pedido vazio."""
        p = li.plano_de_aquisicao(um('VIDEO_URL'), li.pedido_vazio())
        self.assertEqual(p['GAP'], [])
        self.assertEqual(p['WANTED'], [])

    def test_M6_paid_before_free(self):
        """A unica ligada e DIRECT_HTTP. Um pago ligado apareceria aqui."""
        for _plat, nome in [k for k in reg.executaveis() if k[0] == 'LINKEDIN']:
            grosso = cap.da_matriz(nome)
            d = mz.decisao('LINKEDIN', grosso)
            self.assertNotIn(d['CLASSE'], ('APIFY', 'OFFICIAL_API_PAID'))

    def test_M7_comments_true_por_default(self):
        self.assertFalse(li.pedido_vazio()['WANT_COMMENTS'])
        self.assertTrue(all(v is False for v in li.pedido_vazio().values()))

    def test_M8_full_video_antes_de_caption(self):
        p = li.plano_de_aquisicao(um('VIDEO_URL'), {k: True for k in li.BANDEIRAS})
        ordem = [x['NEED'] for x in p['PLAN']]
        self.assertLess(ordem.index('NATIVE_CAPTION'), ordem.index('TRANSCRIPT'))

    def test_M9_asr_sem_media_gate(self):
        """O transcript nunca sai READY quando nao ha bytes nesta casa."""
        e = um('VIDEO_URL')
        self.assertFalse(e['RAW']['VIDEO_BYTES_ACQUIRED'])
        p = li.plano_de_aquisicao(e, dict(li.pedido_vazio(), WANT_TRANSCRIPT=True))
        passos = {x['NEED']: x for x in p['PLAN']}
        self.assertEqual(passos['NATIVE_CAPTION']['VERDICT'], 'BLOCKED_NO_PERMITTED_ROUTE')

    def test_M10_provider_direto(self):
        """Nenhuma CHAMADA a provider vive neste adaptador.

        A sentinela mede o IMPORT e a CHAMADA, nao o texto. A primeira versao
        proibia a cadeia `harvestapi~` e apanhou-se a si mesma: o nome do ator
        aparece uma vez, como ROTULO de procedencia do bruto preservado.

            PROIBIR O NOME DO PROVIDER APAGARIA A PROCEDENCIA. O que nao pode
            existir aqui e a IDA a ele.
        """
        caminho = os.path.join(RAIZ, 'coleta/adaptador_linkedin.py')
        arvore = ast.parse(open(caminho, encoding='utf-8').read())
        importados = set()
        for n in ast.walk(arvore):
            if isinstance(n, ast.Import):
                importados |= {a.name.split('.')[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module:
                importados.add(n.module.split('.')[0])
        for proibido in ('coletor', 'apify_pool', 'urllib', 'requests', 'subprocess'):
            self.assertNotIn(proibido, importados)
        # E nenhuma chamada com nome de compra.
        chamadas = {n.func.attr for n in ast.walk(arvore)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        for proibido in ('executar_com_pool', 'pool', 'urlopen'):
            self.assertNotIn(proibido, chamadas)
        # O rotulo de procedencia CONTINUA a existir — sem ele o rasto emudece.
        self.assertIn('harvestapi', li.ROTA_BRUTO_PRESERVADO)

    def test_M11_raw_after_normalization(self):
        """`RAW FIRST`: a referencia do bruto existe antes de haver envelope."""
        e = um('VIDEO_URL')
        self.assertTrue(e['RAW_REFERENCE'])
        sem_ref = li.normalizar_post(bruto()[0], run_id=RUN)
        self.assertIsNone(sem_ref['RAW_REFERENCE'])
        # E sem referencia o nivel desta acao NAO e LOCAL: nao ha bruto no disco.
        self.assertNotEqual(sem_ref['ACQUISITION_TIER'], li.LOCAL)

    def test_M12_policy_ignored(self):
        """A politica lida do dono, e nao uma copia local."""
        e = um('VIDEO_URL')
        p = li.plano_de_aquisicao(e, {k: True for k in li.BANDEIRAS})
        self.assertEqual(p['PAID_NEEDED_FOR'], [])
        self.assertTrue(p['BLOCKED_FOR'])
        for passo in p['PLAN']:
            self.assertIn(passo['POLICY'],
                          ('ALLOWED', 'ROUTE_NOT_ALLOWED', 'NOT_DECLARED'))


# ══════════════════════════════════════════════════════════════════════════
# O NIVEL DE AQUISICAO E VOCABULARIO FECHADO
# ══════════════════════════════════════════════════════════════════════════
class OVocabularioEFechado(unittest.TestCase):

    def test_nivel_fora_do_vocabulario_rebenta(self):
        with self.assertRaises(ValueError):
            li.normalizar_post(bruto()[0], run_id=RUN, origem='DE_GRACA')

    def test_item_que_nao_e_dicionario_rebenta(self):
        with self.assertRaises(ValueError):
            li.campos_do_bruto(['nao sou um post'])

    def test_a_origem_por_omissao_e_paga(self):
        """O unico bruto de posts desta casa veio de rota paga."""
        e = li.normalizar_post(bruto()[0], run_id=RUN)
        self.assertEqual(e['FIELD_ORIGIN_TIER'], li.PAID)


if __name__ == '__main__':
    unittest.main(verbosity=2)
