#!/usr/bin/env python3
"""STORIES — o red team da capacidade, todo offline e sem credencial nenhuma.

Cada teste aqui é um ataque que já aconteceu com alguém, e o mais caro deles
aconteceu no ator mais usado do mercado: `apify/instagram-scraper` publicava
`resultsType=stories`, cobrava o run, ficava verde — e devolvia REELS. O valor
foi depreciado pelo próprio publisher por isso.

    ENUM EXISTE != CAPACIDADE FUNCIONA.
    RUN VERDE != CLASSE CERTA.

O segundo ataque mais caro não tem culpado: é o zero. Um ator que falhou e uma
conta que não postou devolvem exatamente a mesma coisa — nenhuma linha. Chamar
as duas de `NO_ACTIVE_STORIES` produz um acervo que afirma ausência que ninguém
mediu, e ausência inventada é pior que buraco declarado, porque não dá para
procurar depois.

    ZERO LINHA DE ATOR QUE FALHOU NÃO É «NÃO POSTOU».
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
sys.path.insert(0, os.path.join(RAIZ, 'leis'))
sys.path.insert(0, os.path.join(RAIZ, 'guarda'))
import _gavetas  # noqa: E402,F401
import instagram_stories as ist   # noqa: E402
import social_envelope as env     # noqa: E402
import social_rotas as sr         # noqa: E402
import social_sessao as ss        # noqa: E402

AGORA = 1789000000          # instante fixo: teste não pode depender do relógio
DEPOIS = AGORA + 86400

# A FORMA REAL, lida da página do ator em 2026-09-09 antes do piloto vivo. Ela
# importa mais que qualquer outra linha deste arquivo: a fixture inventada da R2
# não tinha `product_type` nem `caption_is_edited`, e por isso a porta de tipo
# passou nos testes enquanto teria recusado 100% dos Stories verdadeiros.
#
#     UMA TRAVA CALIBRADA EM CIMA DE FIXTURE INVENTADA MEDE A FIXTURE.
STORY_IMAGEM = {
    'pk': '3210000000000000001', 'id': '3210000000000000001_999',
    'media_type': 1, 'taken_at': AGORA, 'expiring_at': DEPOIS,
    'product_type': 'story',        # o valor que PROVA a classe
    'is_reel_media': True,          # e que NÃO prova Reel — ver abaixo
    'caption_is_edited': False, 'code': 'CxYzStory', 'caption': None,
    'like_and_view_counts_disabled': True, 'fb_aggregated_like_count': 0,
    'has_liked': False, 'story_hashtags': [], 'story_link_stickers': [],
    'user': {'username': 'conta_publica_exemplo', 'id': '999'},
    'image_versions2': {'candidates': [{'url': 'https://cdn.example/i.jpg?sig=abc'}]},
    'original_width': 1080, 'original_height': 1920,
}
STORY_VIDEO = dict(STORY_IMAGEM, pk='3210000000000000002', media_type=2,
                   video_versions=[{'url': 'https://cdn.example/v.mp4?sig=abc'}],
                   has_audio=True)

# O item que quebrou o mercado: um Reel vestido de Story.
REEL_DISFARCADO = dict(STORY_IMAGEM, pk='3210000000000000009',
                       product_type='clips', play_count=12345, shortcode='CxYzAbC')


def _norm(item, u='conta_publica_exemplo'):
    return ist.normalizar(item, username=u, run_id='TEST-STORY',
                          country_scope='IT', route='apify:teste')


class RunVerdeNaoEClasseCerta(unittest.TestCase):
    """§67 — o ataque mais perigoso, e o único com precedente de mercado."""

    def test_reel_disfarcado_de_story_e_recusado(self):
        with self.assertRaises(ist.NaoEStory):
            _norm(REEL_DISFARCADO)

    def test_a_recusa_nomeia_o_campo_que_denunciou(self):
        with self.assertRaises(ist.NaoEStory) as c:
            _norm(REEL_DISFARCADO)
        self.assertIn('clips', str(c.exception))

    def test_reel_sem_product_type_ainda_morre_pelas_metricas_de_feed(self):
        """Renomear um campo não deve abrir a porta."""
        item = dict(REEL_DISFARCADO); item.pop('product_type')
        with self.assertRaises(ist.NaoEStory):
            _norm(item)

    def test_o_story_REAL_passa_pela_porta(self):
        """A prova que faltava na R2: a porta calibrada contra a forma medida."""
        self.assertEqual(_norm(STORY_IMAGEM)['CONTENT_TYPE'], 'STORY')

    def test_is_reel_media_TRUE_nao_e_prova_de_reel(self):
        """Armadilha de nome: no vocabulário do Instagram, `reel media` é a
        BANDEJA DE STORIES. Um Story tem `is_reel_media=true`. Ler esse campo
        como prova de Reel inverteria a porta e recusaria tudo o que é certo."""
        self.assertTrue(STORY_IMAGEM['is_reel_media'])
        self.assertEqual(_norm(STORY_IMAGEM)['CONTENT_TYPE'], 'STORY')

    def test_product_type_desconhecido_nao_entra_por_omissao(self):
        with self.assertRaises(ist.NaoEStory):
            _norm(dict(STORY_IMAGEM, product_type='alguma_coisa_nova'))

    def test_highlight_nao_e_story(self):
        """Highlight é permanente. Story expira. Não são a mesma evidência."""
        item = dict(STORY_IMAGEM, is_highlight=True, highlight_id='h1')
        with self.assertRaises(ist.NaoEStory):
            _norm(item)

    def test_item_sem_prazo_de_expiracao_nao_prova_ser_efemero(self):
        item = dict(STORY_IMAGEM); item.pop('expiring_at')
        with self.assertRaises(ist.NaoEStory):
            _norm(item)

    def test_item_sem_NENHUM_id_nativo_e_recusado(self):
        """Sem ID estável não há dedupe, e sem dedupe a mesma Story vira duas."""
        item = {k: v for k, v in STORY_IMAGEM.items() if k not in ('pk', 'id')}
        with self.assertRaises(ist.NaoEStory):
            _norm(item)

    def test_sem_pk_o_id_composto_serve_de_identidade(self):
        """Recusar aqui perderia Story bom: `id` é tão estável quanto `pk`."""
        item = dict(STORY_IMAGEM); item.pop('pk')
        self.assertEqual(_norm(item)['NATIVE_ID'], STORY_IMAGEM['id'])

    def test_na_porta_do_dispatcher_a_recusa_vira_contract_drift(self):
        """E nunca um `continue` silencioso que deixaria o Reel entrar."""
        self.assertIs(sr._NaoEStory(), ist.NaoEStory)


class ZeroNaoEAusenciaAteAlguemProvarQueOlhou(unittest.TestCase):
    """§68 — zero linha só vira «não postou» com prova de que o perfil foi lido."""

    def test_zero_para_todos_os_perfis_e_unknown_e_nao_no_active_stories(self):
        e = ist.classificar({'STATUS': 'SUCCESS'}, [], ['a', 'b', 'c'])
        for u in ('a', 'b', 'c'):
            self.assertEqual(e[u]['ESTADO'], 'UNKNOWN_ERROR')

    def test_zero_para_um_perfil_quando_outro_respondeu_e_no_active_stories(self):
        e = ist.classificar({'STATUS': 'SUCCESS'}, [STORY_IMAGEM],
                            ['conta_publica_exemplo', 'sem_story'])
        self.assertEqual(e['conta_publica_exemplo']['ESTADO'], 'OK')
        self.assertEqual(e['sem_story']['ESTADO'], 'NO_ACTIVE_STORIES')

    def test_succeeded_com_zero_itens_chega_como_partial_e_nao_vira_ausencia(self):
        """A porta paga já classifica esse caso como PARTIAL. Aqui ele não pode
        ser reinterpretado como «a conta não postou»."""
        e = ist.classificar({'STATUS': 'PARTIAL', 'ERRO': 'SUCCEEDED com ZERO itens'},
                            [], ['a'])
        self.assertEqual(e['a']['ESTADO'], 'UNKNOWN_ERROR')

    def test_perfil_privado_e_bloqueio_e_nao_vazio(self):
        item = dict(STORY_IMAGEM, is_private=True)
        e = ist.classificar({'STATUS': 'SUCCESS'}, [item], ['conta_publica_exemplo'])
        self.assertEqual(e['conta_publica_exemplo']['ESTADO'], 'PRIVATE_PROFILE')

    def test_ator_falhado_nao_inventa_ausencia_para_a_lista_inteira(self):
        e = ist.classificar({'STATUS': 'FAILED', 'ERRO': 'ator caiu'},
                            [], ['a', 'b'])
        self.assertEqual({v['ESTADO'] for v in e.values()}, {'ACTOR_FAILED'})

    def test_cada_falha_tem_nome_proprio_e_nenhuma_e_unknown_por_preguica(self):
        casos = {
            'HTTP 429 rate limit': 'RATE_LIMITED',
            'login required: session expired': 'LOGIN_REQUIRED',
            'maxTotalChargeUsd atingido': 'BUDGET_EXHAUSTED',
        }
        for msg, esperado in casos.items():
            with self.subTest(msg=msg):
                e = ist.classificar({'STATUS': 'FAILED', 'ERRO': msg}, [], ['a'])
                self.assertEqual(e['a']['ESTADO'], esperado)

    def test_os_quatro_estados_continuam_distinguiveis_no_vocabulario_canonico(self):
        """Se dois deles colapsarem no mesmo canônico, a medição perde sentido."""
        import falhas
        canon = {n: falhas.traduzir(n) for n in
                 ('NO_ACTIVE_STORIES', 'PRIVATE_PROFILE', 'LOGIN_REQUIRED', 'ACTOR_FAILED')}
        self.assertEqual(len(set(canon.values())), 4, canon)


class OQueOScrapNaoTemODireitoDePreencher(unittest.TestCase):

    def test_story_e_classe_propria_e_nao_post(self):
        self.assertEqual(_norm(STORY_IMAGEM)['CONTENT_TYPE'], 'STORY')
        self.assertIn('STORY', env.CONTENT_TYPES)

    def test_publicacao_nao_vira_fato(self):
        o = _norm(STORY_IMAGEM)
        self.assertNotEqual(o['PUBLISHED_AT'], o['FACT_TIME'])
        self.assertEqual(o['FACT_TIME'], 'UNKNOWN')

    def test_conta_nao_vira_lugar_do_fato(self):
        o = _norm(STORY_IMAGEM)
        self.assertEqual(o['FACT_LOCATION'], 'UNKNOWN')
        self.assertEqual(o['ACCOUNT_LOCATION'], 'UNKNOWN')
        self.assertEqual(o['SOURCE_LOCATION'], 'UNKNOWN')

    def test_expiracao_vem_da_plataforma_e_nunca_de_publicado_mais_24h(self):
        o = _norm(STORY_IMAGEM)
        self.assertEqual(o['EXPIRES_AT_SOURCE'], 'PLATFORM')
        self.assertTrue(o['EXPIRES_AT'].startswith('20'))

    def test_observado_e_coletado_sao_campos_separados(self):
        o = _norm(STORY_IMAGEM)
        self.assertIn('OBSERVED_AT', o)
        self.assertIn('COLLECTED_AT', o)

    def test_a_url_do_cdn_e_declarada_temporaria(self):
        """URL assinada morre em horas. Tratá-la como prova durável é perder a prova."""
        self.assertEqual(_norm(STORY_IMAGEM)['MEDIA_URL_DURABILITY'],
                         'TEMPORARY_CDN_SIGNED_URL')

    def test_o_objeto_confessa_que_pode_ser_dado_pessoal(self):
        o = _norm(STORY_IMAGEM)
        self.assertEqual(o['DATA_CLASS'], 'PERSONAL_DATA_POSSIBLE')
        self.assertTrue(o['LEGAL_INTERPRETATION_REQUIRED'])

    def test_video_e_imagem_sao_distinguidos_pelo_ator_e_nao_pela_extensao(self):
        self.assertEqual(_norm(STORY_IMAGEM)['MEDIA_TYPE'], 'IMAGE')
        self.assertEqual(_norm(STORY_VIDEO)['MEDIA_TYPE'], 'VIDEO')


class DuasVarredurasNaoFazemDoisObjetos(unittest.TestCase):
    """§36 — a mesma Story ativa, lida duas vezes, continua sendo uma."""

    def test_a_mesma_story_em_duas_varreduras_funde(self):
        scan1 = [_norm(STORY_IMAGEM), _norm(STORY_VIDEO)]
        scan2 = [_norm(STORY_IMAGEM), _norm(STORY_VIDEO)]
        objs, rel = env.dedupe(scan1 + scan2)
        self.assertEqual(len(objs), 2)
        self.assertEqual(rel['FUNDIDOS'], 2)

    def test_story_nova_na_segunda_varredura_e_objeto_novo(self):
        nova = dict(STORY_IMAGEM, pk='3210000000000000003')
        objs, _r = env.dedupe([_norm(STORY_IMAGEM)] + [_norm(STORY_IMAGEM), _norm(nova)])
        self.assertEqual(len(objs), 2)

    def test_a_identidade_e_o_id_nativo_e_nao_a_imagem(self):
        """Duas Stories com a MESMA arte e IDs diferentes são duas Stories."""
        gemea = dict(STORY_IMAGEM, pk='3210000000000000004')
        objs, _r = env.dedupe([_norm(STORY_IMAGEM), _norm(gemea)])
        self.assertEqual(len(objs), 2)


class ONaoAcendeRunPagoAToa(unittest.TestCase):

    def test_lista_vazia_e_recusada_antes_de_pagar_a_taxa_de_partida(self):
        with self.assertRaises(ist.EntradaInvalida):
            ist.entrada([])

    def test_url_no_lugar_de_handle_e_recusada(self):
        with self.assertRaises(ist.EntradaInvalida):
            ist.entrada(['https://www.instagram.com/fao/'])

    def test_o_teto_de_perfis_por_run_e_desta_casa_e_nao_do_ator(self):
        with self.assertRaises(ist.EntradaInvalida):
            ist.entrada(['c%d' % i for i in range(ist.MAX_PERFIS_POR_RUN + 1)])

    def test_o_arroba_e_tolerado_porque_gente_cola_com_arroba(self):
        self.assertEqual(ist.entrada(['@fao'])['usernames'], ['fao'])

    def test_o_custo_estimado_sai_do_preco_publicado_e_nao_de_palpite(self):
        self.assertAlmostEqual(ist.custo_estimado(10), 0.099 + 10 * 0.003, places=6)


class NenhumAtorRecebeSessaoHumana(unittest.TestCase):
    """§12 — a linha que decidiu a escolha do ator, e não foi o preço."""

    def test_o_ator_que_pede_cookie_de_sessao_esta_recusado_por_escrito(self):
        self.assertIn('automation-lab/instagram-stories-scraper', ist.RECUSADOS)
        self.assertIn('sessionCookie', ist.RECUSADOS['automation-lab/instagram-stories-scraper'])

    def test_o_ator_do_enum_que_devolvia_reel_esta_recusado_por_escrito(self):
        self.assertIn('apify/instagram-scraper', ist.RECUSADOS)

    def test_a_entrada_do_ator_escolhido_nao_carrega_credencial_nenhuma(self):
        self.assertEqual(set(ist.entrada(['fao'])), {'usernames'})


class OTokenNaoVazaPeloCaminhoDoErro(unittest.TestCase):
    """§55/§57 — sem credencial real: as formas são montadas em execução."""

    def test_token_da_apify_e_redigido(self):
        falso = 'apify_' + 'api_' + ('Z' * 36)
        self.assertNotIn(falso, ss.redigir('RuntimeError ao chamar com %s' % falso))

    def test_url_de_dataset_com_token_no_parametro_e_redigida(self):
        falso = 'apify_' + 'api_' + ('Q' * 36)
        url = 'https://api.apify.com/v2/datasets/abc/items?token=%s&clean=true' % falso
        self.assertNotIn(falso, ss.redigir(url))

    def test_cabecalho_de_autorizacao_e_redigido(self):
        cab = 'Authoriz' + 'ation: Bearer ' + ('K' * 30)
        self.assertNotIn('K' * 30, ss.redigir(cab))


class OByteVemAntesDaFila(unittest.TestCase):
    """§37-§39 — a lei do conteúdo efêmero, executável e não documental."""

    def test_sem_url_de_midia_o_objeto_confessa_que_nao_e_duravel(self):
        o = _norm(STORY_IMAGEM)
        o['MEDIA_URL'] = 'UNKNOWN'
        r = ist.baixar_midia(o, '/tmp/claude-0/nao-usado')
        self.assertEqual(r['MEDIA_DURABILITY'], ist.MEDIA_NOT_DURABLE)

    def test_url_morta_nao_derruba_a_coleta_e_vira_estado(self):
        """A URL assinada pode morrer entre descobrir e baixar. Isso é ESTADO."""
        o = _norm(STORY_IMAGEM)
        o['MEDIA_URL'] = 'https://cdn.invalido.invalido/nada.jpg'
        r = ist.baixar_midia(o, '/tmp/claude-0/story-teste')
        self.assertEqual(r['MEDIA_DURABILITY'], ist.MEDIA_NOT_DURABLE)
        self.assertIn('no mesmo run', r['MEDIA_NOT_DURABLE_REASON'])

    def test_story_descoberto_sem_byte_nao_pode_parecer_preservado(self):
        o = ist.baixar_midia(dict(_norm(STORY_IMAGEM), MEDIA_URL='UNKNOWN'), '/tmp/claude-0/x')
        self.assertNotEqual(o.get('MEDIA_DURABILITY'), ist.MEDIA_PRESERVED)
        self.assertIsNone(o.get('MEDIA_SHA256'))


class OTetoMorde(unittest.TestCase):
    """§99-§100, §127-§128 — duas travas independentes, e as duas precisam abrir."""

    def test_a_previsao_que_nao_cabe_e_recusada_antes_de_executar(self):
        with self.assertRaises(ist.ForaDoOrcamento):
            ist.cabe_no_teto(3, ja_gasto_usd=0.45)

    def test_o_que_cabe_passa_e_devolve_a_sobra(self):
        previsto, sobra = ist.cabe_no_teto(3, ja_gasto_usd=0.10)
        self.assertAlmostEqual(previsto, 0.108, places=3)
        self.assertAlmostEqual(sobra, 0.40, places=3)

    def test_intencao_de_pagar_sem_orcamento_nao_roda(self):
        """`--pagar` é INTENÇÃO. O teto é CAPACIDADE. Uma não substitui a outra."""
        with self.assertRaises(ist.ForaDoOrcamento):
            ist.cabe_no_teto(25, ja_gasto_usd=0.40)

    def test_orcamento_sem_intencao_de_pagar_nao_roda(self):
        _o, r = sr.executar(platform='INSTAGRAM', capability='FETCH_STORIES',
                            run_id='TEST-TETO', country_scope='IT', perfis=['fao'])
        self.assertEqual(r['ESTADO'], 'BUDGET_EXHAUSTED')


class OTranscritorRecebeOByteENaoVaiBuscaLo(unittest.TestCase):
    """§59-§60 — separar AQUISIÇÃO de TRANSCRIÇÃO, sem Story fingir ser Reel."""

    def setUp(self):
        sys.path.insert(0, os.path.join(RAIZ, 'ferramentas'))
        import story_transcrever
        self.st = story_transcrever

    def test_arquivo_ausente_e_estado_da_nossa_cadeia_e_nao_silencio_do_story(self):
        r = self.st.transcrever('/tmp/claude-0/nao-existe-nenhum.mp4')
        self.assertEqual(r['TRANSCRIPT_STATE'], self.st.MEDIA_MISSING)
        self.assertIsNone(r['TRANSCRIPT'])

    def test_story_de_imagem_nao_entra_na_cadeia_de_video(self):
        o = self.st.anexar(_norm(STORY_IMAGEM))
        self.assertNotIn('DERIVED_TRANSCRIPT', o)

    def test_video_sem_byte_preservado_nao_e_enfileirado_para_depois(self):
        o = dict(_norm(STORY_VIDEO), MEDIA_DURABILITY=ist.MEDIA_NOT_DURABLE)
        r = self.st.anexar(o)
        self.assertEqual(r['DERIVED_TRANSCRIPT']['TRANSCRIPT_STATE'],
                         self.st.MEDIA_MISSING)

    def test_o_transcritor_nao_conhece_shortcode_nem_instagram(self):
        """Se ele soubesse buscar, teria o caminho de renovação que para Story
        SEMPRE falha — e falharia em silêncio, devolvendo «sem fala»."""
        fonte = open(os.path.join(RAIZ, 'ferramentas', 'story_transcrever.py'),
                     encoding='utf-8').read()
        corpo = fonte.split('"""', 2)[2]      # fora da docstring, que explica o porquê
        self.assertNotIn('shortcode', corpo)
        self.assertNotIn('urlopen', corpo)

    def test_o_custo_em_dolar_e_zero_e_o_tempo_de_maquina_e_outro_campo(self):
        r = self.st.transcrever('/tmp/claude-0/nao-existe.mp4')
        self.assertEqual(r['USD_COST'], 0.0)
        self.assertIn('LOCAL_COMPUTE_S', r)


if __name__ == '__main__':
    unittest.main()
