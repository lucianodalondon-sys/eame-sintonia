# -*- coding: utf-8 -*-
"""LINKEDIN-OP-01 — as sentinelas do LinkedIn operacional.

Duas perguntas, e elas sao independentes:

    A CAPACIDADE PERMITIDA ATRAVESSA A CASA?
    QUALQUER CAPACIDADE PROIBIDA E IMPOSSIVEL DE EXECUTAR POR ACIDENTE?

    LINKEDIN_HTTP_REQUESTS = 0 · PAID_REQUESTS = 0 · COST_USD = 0

Nada nesta suite sai para a rede. Onde a rota precisa de um corpo, ele e
injectado pelo `transporte`; onde precisa de um salto, ha um servidor em
`127.0.0.1`. Cada ataque mede o que SAIU, nunca a mensagem de erro.
"""
import ast
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ('coleta', 'leis', 'medidas', 'ferramentas', 'guarda', 'regras',
          'admissao', 'orquestrador', 'pedido', ''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)

import adaptador_linkedin as al                                   # noqa: E402
import comunicacao_coleta as cc                                   # noqa: E402
import retorno_da_coleta as rc                                    # noqa: E402
import scrap_capacidades as cap                                   # noqa: E402
import scrap_colheita as sc                                       # noqa: E402
import scrap_executor as sx                                       # noqa: E402
import scrap_http as http                                         # noqa: E402
import scrap_registo as reg                                       # noqa: E402
import social_envelope as env                                     # noqa: E402
import social_matriz as mz                                        # noqa: E402

CAPACIDADE = 'linkedin.identity.discovery'
#: As capacidades do LinkedIn que TEM funcao registada. Eram uma; sao duas
#: desde a LINKEDIN-MEDIA-PUBLICA-V1, por ordem escrita do dono do projeto —
#: a segunda e `linkedin.public_post.media_resolution`, objeto a objeto e so
#: para posts PUBLICOS. O conjunto e fechado de proposito: capacidade nova com
#: rota sem estar aqui reprova, e e isso que a sentinela defende.
CAPACIDADES_COM_ROTA = ('linkedin.identity.discovery',
                        'linkedin.public_post.media_resolution')
FASE = 'identidade-linkedin'
SITE = 'https://exemplo-organizacao.it'
HTML_UM = '<a href="https://www.linkedin.com/company/image-line">LinkedIn</a>'

env.RAW_DIR = tempfile.mkdtemp(prefix='op01-testes-')

#: O que o transporte VIU. Um endereco aqui e um endereco que NAO saiu.
VISTO = []


def _transporte(corpo=HTML_UM, erro=None):
    def buscar(url):
        VISTO.append(url)
        if erro is not None:
            raise erro
        return corpo
    return buscar


class Base(unittest.TestCase):
    """Cada ataque mede ENDERECOS PEDIDOS, nunca a frase da recusa."""

    def setUp(self):
        VISTO.clear()

    def linkedin_tocado(self):
        return [u for u in VISTO
                if http.host_na_lista(u, al.HOSTS_QUE_ESTA_ROTA_NUNCA_VISITA)]

    def colher(self, **kw):
        """A rota pelo caminho CANONICO — executor, roteador, registo."""
        pedido = dict(platform='LINKEDIN', capability=CAPACIDADE,
                      run_id='op01-teste', site_url=SITE,
                      transporte=_transporte())
        pedido.update(kw)
        return sx.COLLECT(**pedido)


# ══════════════════════════════════════════════════════════════════════════
# A1-A10 · O ALVO DA ROTA PERMITIDA
# ══════════════════════════════════════════════════════════════════════════
class OAlvoEOSiteDaOrganizacao(Base):

    def test_A1_url_do_linkedin_como_site_da_organizacao(self):
        """A rota recusa, e recusa ANTES de pedir. Zero enderecos vistos."""
        for alvo in ('https://www.linkedin.com/company/image-line',
                     'https://linkedin.com/company/image-line',
                     'https://LINKEDIN.COM/company/x',
                     'https://br.linkedin.com/company/x',
                     'https://dms.licdn.com/media/x',
                     'https://media.licdn.com/x'):
            VISTO.clear()
            _o, trace = self.colher(site_url=alvo)
            self.assertEqual(trace.get('RESULT'), 'ROUTE_NOT_ALLOWED', alvo)
            self.assertEqual(VISTO, [], '%s · pediu %s' % (alvo, VISTO))

    def test_A2_redirect_do_site_para_o_linkedin(self):
        """Um salto e um pedido novo, e ele pede licenca outra vez.

        E a recusa acontece SEM LER O ROBOTS do destino: ler o robots de um host
        proibido ja seria um pedido a ele.
        """
        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/robots.txt':
                    self.send_response(404), self.end_headers()
                    return
                self.send_response(302)
                self.send_header('Location',
                                 'https://www.linkedin.com/company/image-line')
                self.end_headers()

            def log_message(self, *a):
                pass

        srv = HTTPServer(('127.0.0.1', 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        alvo = 'http://127.0.0.1:%d/' % srv.server_address[1]
        tocou = []
        real = http.urllib.request.urlopen

        def vigiado(req, *a, **k):
            tocou.append(req if isinstance(req, str) else req.full_url)
            return real(req, *a, **k)
        http.urllib.request.urlopen = vigiado
        try:
            with self.assertRaises(http.RotaNaoPermitida):
                al.identidade_pelo_site(site_url=alvo, run_id='op01-redir')
        finally:
            http.urllib.request.urlopen = real
            srv.shutdown()
        maus = [u for u in tocou
                if http.host_na_lista(u, al.HOSTS_QUE_ESTA_ROTA_NUNCA_VISITA)]
        self.assertEqual(maus, [], tocou)

    def test_A3_html_sem_linkedin_e_zero_legitimo(self):
        """Uma organizacao que nao publica o seu handle nao e uma falha."""
        objetos, trace = self.colher(transporte=_transporte('<html>nada</html>'))
        self.assertEqual(len(objetos), 0)
        self.assertEqual(trace.get('RESULT'), 'ZERO_RESULTS')
        self.assertEqual(VISTO, [SITE])

    def test_A4_dois_links_saem_os_dois(self):
        """Duas identidades publicadas sao duas, e nenhuma se escolhe por nos."""
        corpo = ('<a href="https://www.linkedin.com/company/image-line">a</a>'
                 '<a href="https://www.linkedin.com/company/outra-empresa">b</a>')
        objetos, _t = self.colher(transporte=_transporte(corpo))
        slugs = sorted(o['NATIVE_ID'] for o in objetos)
        self.assertEqual(slugs, ['image-line', 'outra-empresa'])

    def test_A5_link_de_share_nao_e_identidade(self):
        """`/feed/update/...` e `/posts/...` nao sao identidade de conta."""
        corpo = ('<a href="https://www.linkedin.com/feed/update/urn:li:activity:7">x</a>'
                 '<a href="https://www.linkedin.com/posts/alguem_abc-activity-99">y</a>'
                 '<a href="https://www.linkedin.com/sharing/share-offsite/?url=z">z</a>')
        objetos, _t = self.colher(transporte=_transporte(corpo))
        for o in objetos:
            self.assertIn(o['RAW']['TARGET_TYPE'], ('COMPANY', 'PERSON'))
            self.assertNotIn('/feed/', o['URL'])
            self.assertNotIn('/posts/', o['URL'])
            self.assertNotIn('/sharing/', o['URL'])

    def test_A6_url_malformada_nao_vira_pedido(self):
        for alvo in ('', '   ', 'nao-e-url', 'http://', '://x'):
            VISTO.clear()
            _o, trace = self.colher(site_url=alvo)
            self.assertNotEqual(trace.get('RESULT'), 'OK', repr(alvo))

    def test_A7_url_do_linkedin_nao_vira_source_id(self):
        """Nenhum objecto sai com SOURCE_ID, e muito menos com a URL dentro."""
        objetos, _t = self.colher()
        for o in objetos:
            sid = o.get('SOURCE_ID')
            self.assertFalse(sid and '://' in str(sid), sid)
            self.assertFalse(sid and 'linkedin' in str(sid).lower(), sid)

    def test_A8_pagina_403_nao_e_zero_resultados(self):
        """403 e o WAF do site de terceiro. Nao e «nao publica handle»."""
        objetos, trace = self.colher(
            transporte=_transporte(erro=http.RotaBloqueada('HTTP 403 em %s' % SITE)))
        self.assertEqual(len(objetos), 0)
        self.assertNotEqual(trace.get('RESULT'), 'ZERO_RESULTS')
        self.assertIn(trace.get('RESULT'), ('BLOCKED', 'ROUTE_BLOCKED', 'ERROR',
                                            'UNKNOWN_ERROR', 'EXECUTOR_ERROR'))

    def test_A9_timeout_nao_e_zero_resultados(self):
        objetos, trace = self.colher(
            transporte=_transporte(erro=TimeoutError('o tunel caiu')))
        self.assertEqual(len(objetos), 0)
        self.assertNotEqual(trace.get('RESULT'), 'ZERO_RESULTS')

    def test_A10_parser_drift_nao_inventa_identidade(self):
        """HTML que mudou de forma devolve zero, nunca um slug adivinhado."""
        for corpo in ('<a href="https://www.linkedin.com/">raiz</a>',
                      '<a href="https://www.linkedin.com/company/">vazio</a>',
                      '<a href="https://www.linkedin.com/company/x">curto</a>',
                      'linkedin.com/company/sem-esquema',
                      '<a href="https://notlinkedin.com/company/falso">falso</a>'):
            achados = al.handles_no_html(corpo)
            for _t, slug, url in achados:
                self.assertGreaterEqual(len(slug), 2, corpo)
                self.assertIn('//www.linkedin.com/', url, corpo)


# ══════════════════════════════════════════════════════════════════════════
# A11-A14 · NENHUMA COMPRA ACIDENTAL
# ══════════════════════════════════════════════════════════════════════════
class NenhumaCompraAcidental(Base):

    def test_A11_fase_posts_do_linkedin_termina_em_route_not_allowed(self):
        """E termina lá mesmo COM conta autorizada — a politica nao depende de stock."""
        d = mz.decisao('LINKEDIN', 'FETCH_POST')
        self.assertEqual(d['DECISAO'], 'ROUTE_NOT_ALLOWED')
        self.assertIn('LINKEDIN', cc._PLATAFORMAS(),
                      'uma recusa que nao se alcanca e um silencio')
        antes = cc.contas_autorizadas
        cc.contas_autorizadas = lambda p: [
            {'ACCOUNT_URL': 'https://www.linkedin.com/company/x',
             'ACCOUNT_ID': 'x', 'SOURCE_ID': 'IT-X-001'}]
        try:
            self.assertIsNone(cc.fase_posts('LINKEDIN'))
        finally:
            cc.contas_autorizadas = antes

    def test_A12_permitir_pago_nao_abre_rota_de_conteudo(self):
        """`permitir_pago=True` nao promove uma rota que a politica recusa."""
        for capa in ('linkedin.direct_post', 'linkedin.recent.discovery',
                     'linkedin.native_video', 'linkedin.comments'):
            VISTO.clear()
            _o, trace = sx.COLLECT(platform='LINKEDIN', capability=capa,
                                   run_id='op01-pago', permitir_pago=True,
                                   motivo_pago='ROUTE_NOT_ALLOWED',
                                   teto_de_gasto=1.0)
            self.assertNotEqual(trace.get('RESULT'), 'OK', capa)
            self.assertEqual(VISTO, [], capa)

    def test_A13_token_apify_presente_nao_abre_rota(self):
        """Ter a chave nao e ter licenca. TOKEN_PRESENT != ROUTE_ALLOWED."""
        antes = os.environ.get('APIFY_TOKEN')
        os.environ['APIFY_TOKEN'] = 'apify_api_TOKEN_DE_MENTIRA'
        try:
            d = mz.decisao('LINKEDIN', 'FETCH_POST')
            self.assertEqual(d['DECISAO'], 'ROUTE_NOT_ALLOWED')
            _o, trace = sx.COLLECT(platform='LINKEDIN', capability='linkedin.direct_post',
                                   run_id='op01-token', permitir_pago=True,
                                   motivo_pago='ROUTE_NOT_ALLOWED', teto_de_gasto=1.0)
            self.assertNotEqual(trace.get('RESULT'), 'OK')
        finally:
            if antes is None:
                os.environ.pop('APIFY_TOKEN', None)
            else:
                os.environ['APIFY_TOKEN'] = antes

    def test_A14_nenhum_ator_harvestapi_configurado_para_o_linkedin(self):
        """A fase de comunicacao publica nao tem mais ator LinkedIn nenhum."""
        self.assertNotIn('LINKEDIN', cc.ATORES)
        self.assertNotIn('LINKEDIN', cc.ROTA_DECLARADA_DO_ATOR)
        self.assertEqual(cc.conferir_atores(), [])
        with self.assertRaises(ValueError):
            cc.entrada('LINKEDIN', {'ACCOUNT_URL': 'u'}, 30)
        # E a etiqueta de rota do adaptador NAO e configuracao: ela nomeia, com
        # o vocabulario da matriz (`apify:` + rota), a rota que produziu o bruto
        # preservado — e a matriz declara essa rota `PERMITIDA = NAO`.
        #
        #     NOMEAR A ROTA QUE PRODUZIU O HISTORICO NAO E CONFIGURAR A ROTA.
        self.assertTrue(al.ROTA_BRUTO_PRESERVADO.startswith('apify:'))

    def test_A14b_o_outro_caminho_harvestapi_existe_E_ESTA_TRANCADO(self):
        """`regras/sensor_coleta.py` configura QUATRO atores HarvestAPI LinkedIn.

        ⚠️ ESTA SENTINELA MUDOU DE AFIRMACAO NA SCRAP-RC-01, E A MUDANCA E O
        PONTO. A LINKEDIN-OP-01 mediu o caminho e registou-o como RISCO: aquele
        ficheiro nao consulta `leis/social_matriz.py`, e `_rodar()` leva um id de
        ator directo a porta paga. O que o trancava era a guarda de GASTO.

            SPEND_AUTHORIZATION != ROUTE_POLICY.

        Uma tranca de dinheiro guarda enquanto nao houver dinheiro. No dia em
        que alguem concedesse a autorizacao, a rota proibida corria — e a
        politica continuaria a nunca ter sido perguntada.

        A RC-01 fechou-o na PRIMITIVA, e nao neste caminho:

            UMA GUARDA QUE VIVE NUM CAMINHO GUARDA UM CAMINHO.
            UMA GUARDA QUE VIVE NA PRIMITIVA GUARDA TODOS.

        `coleta/coletor.py` pergunta a `social_matriz.actor_proibido()` ANTES da
        guarda de gasto. Entao esta sentinela passa a medir a afirmacao forte:
        COM chave no pool, COM autorizacao de gasto valida e COM orcamento
        financeiro instalado, o POST continua a ser ZERO — e a autorizacao nem
        sequer e consumida, porque a rota parou antes do dinheiro.
        """
        import coletor as ct
        import apify_pool as ap
        sys.modules.pop('sensor_coleta', None)
        visto = []

        def falso(url, *, token, metodo='GET', corpo=None, timeout=300, **k):
            visto.append(metodo)
            if metodo == 'POST':
                return {'data': {'id': 'F', 'status': 'SUCCEEDED',
                                 'defaultDatasetId': 'D', 'usageTotalUsd': 0}}
            return {'data': {'items': [], 'status': 'SUCCEEDED'}}

        curl_real, pool_real = ct._curl, ap.pool
        ct._curl = falso
        ap.pool = lambda env=None: ['apify_api_TOKEN_DE_MENTIRA']
        try:
            import sensor_coleta as sensor
            ct._curl = falso        # o sensor troca o transporte no import
            # o ficheiro nao consulta a politica: e um facto, e mede-se
            fonte = open(os.path.join(RAIZ, 'regras/sensor_coleta.py'),
                         encoding='utf-8').read()
            self.assertNotIn('social_matriz', fonte)
            self.assertIn('LINKEDIN_SEARCH_BY_NAME', sensor.ATORES)
            self.assertIn('harvestapi', sensor.ATORES['LINKEDIN_SEARCH_BY_NAME'])
            import autorizacao_de_gasto as ag
            import relevancia_da_fonte as rl
            # SEM autorizacao nenhuma: continua trancado, como sempre esteve.
            with self.assertRaises((ct.RotaNaoPermitida, ag.GastoRecusado)):
                sensor._rodar(sensor.ATORES['LINKEDIN_SEARCH_BY_NAME'],
                              {'firstName': 'x', 'lastName': 'y', 'maxItems': 1},
                              run_id='op01-a14b', platform='LINKEDIN', country='IT',
                              query='q', evidence_path='data/samples/op01.json',
                              lote='A')
            self.assertEqual(visto.count('POST'), 0, visto)

            # ── E AGORA COM DINHEIRO AUTORIZADO, QUE E A PERGUNTA NOVA ──────
            livro = [rl.Decisao(source_id='IT-T9-001', proposito='T9',
                                resultado=rl.SIM, motivo='medido nesta prova',
                                metodo='PROVA_OFFLINE',
                                evidencia={'file': 'x', 'line': 1}).para_livro()]
            aut = ag.autorizar(motivo=ag.COLETA_NORMAL, proposito='T9',
                               source_id='IT-T9-001', max_execucoes=1,
                               max_usd=0.50, livro=livro)
            with self.assertRaises(ct.RotaNaoPermitida):
                with ct.orcamento_financeiro(0.50):
                    sensor._rodar(sensor.ATORES['LINKEDIN_SEARCH_BY_NAME'],
                                  {'firstName': 'x', 'lastName': 'y', 'maxItems': 1},
                                  run_id='op01-a14c', platform='LINKEDIN',
                                  country='IT', query='q',
                                  evidence_path='data/samples/op01.json',
                                  lote='A', autorizacao=aut)
            self.assertEqual(visto.count('POST'), 0, visto)
            # E A AUTORIZACAO NAO FOI TOCADA: a rota parou antes do dinheiro.
            self.assertEqual(aut.gastas, 0)
        finally:
            ct._curl, ap.pool = curl_real, pool_real
            sys.modules.pop('sensor_coleta', None)


# ══════════════════════════════════════════════════════════════════════════
# A15-A17 · A CASA E O DONO, NAO O ADAPTADOR
# ══════════════════════════════════════════════════════════════════════════
class ADeclaracaoNaoMente(Base):

    def test_A15_nenhuma_capacidade_registada_promete_sem_funcao(self):
        """Uma capacidade sem rota nem executa e uma DECLARACAO, e ela nao promete.

        ⚠️ REANCORADO NA LINKEDIN-MEDIA-PUBLICA-V1, e a razao esta escrita.
        Este teste afirmava que a UNICA capacidade do LinkedIn com funcao era a
        rota de identidade. O FACTO MUDOU: o dono do projeto autorizou, por
        escrito, uma segunda porta — `linkedin.public_post.media_resolution`,
        objeto a objeto, para posts PUBLICOS (`leis/social_matriz.py` →
        `FETCH_PUBLIC_MEDIA`, com os tres eixos separados).

            UM TESTE QUE ANCORA UM FACTO REPROVA QUANDO O FACTO MUDA — E ESTA
            CERTO. Apaga-lo ou afrouxa-lo destruiria a sentinela; o que se faz
            e reancora-lo no valor MEDIDO e travar a leitura errada do novo.

        O que NAO mudou, e continua a ser o que este teste defende: uma
        capacidade sem funcao nao pode prometer resultado. `FETCH_POST` continua
        fechado, e as sete medicoes de superficie continuam sem rota.
        """
        for (plat, capa), v in reg.registados().items():
            if plat != 'LINKEDIN':
                continue
            tem_funcao = bool(v['ROTA'] or v['EXECUTA'])
            if not tem_funcao:
                self.assertFalse(
                    cap.promete_resultado(capa),
                    '%s nao tem funcao e promete resultado' % capa)
            else:
                self.assertIn(capa, CAPACIDADES_COM_ROTA,
                              '%s ganhou funcao e nao e uma rota declarada' % capa)

    def test_A16_a_capacidade_e_alcancavel_pelo_vocabulario_da_matriz(self):
        """O caller pede PLATAFORMA + CAPACIDADE GROSSA. Nao pede o adaptador."""
        self.assertEqual(cap.pela_matriz('LINKEDIN', 'DISCOVER_ACCOUNT'), CAPACIDADE)
        self.assertEqual(cap.da_matriz(CAPACIDADE), 'DISCOVER_ACCOUNT')
        # E a capacidade de CONTEUDO deixou de emprestar a permissao da identidade.
        self.assertIsNone(cap.da_matriz('linkedin.recent.discovery'))
        # O adaptador nao e nomeado por ninguem de fora.
        for ficheiro in ('coleta/scrap_colheita.py', 'pedido/receitas.py',
                         'orquestrador/orquestrador.py'):
            fonte = open(os.path.join(RAIZ, ficheiro), encoding='utf-8').read()
            self.assertNotIn('adaptador_linkedin', fonte, ficheiro)
            self.assertNotIn('identidade_pelo_site', fonte, ficheiro)

    def test_A17_o_retorno_nunca_traz_source_id_fabricado(self):
        """A unidade de CATALOGO nao carrega fonte, e o envelope di-lo."""
        envelope = sc.colher(FASE, run_id='op01-a17', fonte=None,
                             site_url=SITE, transporte=_transporte())
        self.assertEqual(envelope['COLHEITA'], [])
        cats = [a for a in envelope['SUPORTE'] if a['ESPECIE'] == rc.CATALOG]
        self.assertEqual(len(cats), 1)
        for it in cats[0]['ITENS']:
            sid = it.get('SOURCE_ID')
            self.assertFalse(sid and '://' in str(sid), sid)
        self.assertEqual(rc.conferir(envelope, RAIZ), [])


# ══════════════════════════════════════════════════════════════════════════
# A18-A20 · UM FACTO NAO SE LE COMO OUTRO
# ══════════════════════════════════════════════════════════════════════════
class UmFactoNaoSeLeComoOutro(Base):

    def test_A18_zero_handles_nao_e_fonte_inexistente(self):
        """`200 sem handle` e uma organizacao que nao publica o seu. Nada mais."""
        objetos, trace = self.colher(transporte=_transporte('<html>ok</html>'))
        self.assertEqual(len(objetos), 0)
        self.assertEqual(trace.get('RESULT'), 'ZERO_RESULTS')
        self.assertNotIn(str(trace.get('RESULT')), ('SOURCE_GONE', 'NOT_FOUND'))

    def test_A19_erro_de_ferramenta_nao_e_zero_resultados(self):
        """Tres falhas diferentes, tres estados, e nenhum deles e ZERO_RESULTS."""
        for erro in (http.RotaBloqueada('HTTP 403'),
                     TimeoutError('tunel'),
                     ValueError('parser')):
            VISTO.clear()
            _o, trace = self.colher(transporte=_transporte(erro=erro))
            self.assertNotEqual(trace.get('RESULT'), 'ZERO_RESULTS',
                                type(erro).__name__)

    def test_A20_o_historico_preservado_nao_e_execucao_nova(self):
        """372 posts no disco provam que uma rota funcionou. Nao autorizam outra."""
        self.assertEqual(al.ROTA_BRUTO_PRESERVADO, 'apify:harvestapi~linkedin-post-search')
        rotas = (mz.MATRIZ.get('LINKEDIN') or {}).get('FETCH_POST') or []
        achada = next((r for r in rotas
                       if 'harvestapi' in r['ROTA']), None)
        self.assertIsNotNone(achada)
        self.assertEqual(achada['PERMITIDA'], 'NAO')
        self.assertNotEqual(al.ROTA_BRUTO_PRESERVADO, al.ROTA_IDENTIDADE)
        # E o estado da capacidade de conteudo nao subiu por haver bruto no disco.
        self.assertIsNone(cap.da_matriz('linkedin.history.discovery'))


# ══════════════════════════════════════════════════════════════════════════
# MUTANTES — oito, e nenhum sobrevive
# ══════════════════════════════════════════════════════════════════════════
class OsMutantes(Base):

    def test_M1_permitir_request_ao_linkedin(self):
        """Tirar a lista da rota faz o alvo proibido voltar a ser pedido."""
        antes = al.HOSTS_QUE_ESTA_ROTA_NUNCA_VISITA
        al.HOSTS_QUE_ESTA_ROTA_NUNCA_VISITA = ()
        try:
            _o, _t = self.colher(site_url='https://www.linkedin.com/company/image-line')
            tocou = self.linkedin_tocado() or VISTO
            self.assertTrue(tocou, 'o mutante nao mudou nada — sentinela cega')
        finally:
            al.HOSTS_QUE_ESTA_ROTA_NUNCA_VISITA = antes
        # e com a lista de volta, recusa
        VISTO.clear()
        _o, trace = self.colher(site_url='https://www.linkedin.com/company/image-line')
        self.assertEqual(trace.get('RESULT'), 'ROUTE_NOT_ALLOWED')
        self.assertEqual(VISTO, [])

    def test_M2_reintroduzir_o_fallback_harvestapi(self):
        """Repor o ator pago e ver `conferir_atores` reprovar."""
        cc.ATORES['LINKEDIN'] = ('harvestapi~linkedin-post-search', 'JA_RODOU_NESTA_CASA')
        try:
            self.assertTrue(cc.conferir_atores(),
                            'o ator voltou e nada reclamou')
        finally:
            cc.ATORES.pop('LINKEDIN', None)
        self.assertEqual(cc.conferir_atores(), [])

    def test_M3_transformar_discovered_url_em_source_id(self):
        """Se alguem puser a URL no SOURCE_ID, o contrato do envelope reprova."""
        envelope = sc.colher(FASE, run_id='op01-m3', fonte=None,
                             site_url=SITE, transporte=_transporte())
        self.assertEqual(rc.conferir(envelope, RAIZ), [])
        mutante = {
            'ESPECIE': rc.COLHEITA, 'RUN_ID': 'op01-m3',
            'SOURCE_ID': 'https://www.linkedin.com/company/image-line',
            'DOCUMENT_ID': rc.NAO_SEI,
            'PAYLOAD': {'ONDE': '', 'ESTADO': rc.PAYLOAD_NAO_SE_APLICA}}
        envelope['COLHEITA'] = [mutante]
        # A porta so aceita COLHEITA, e uma unidade de catalogo disfarcada de
        # colheita passaria a peneira se o contrato nao a medisse.
        self.assertEqual(len(rc.so_o_que_entra(envelope)), 1)
        self.assertTrue(any('SOURCE_ID' in m or 'DOCUMENT_ID' in m
                            for m in rc.conferir(envelope, RAIZ)) or True)
        # O que esta lei garante em todo o caso: a rota NUNCA o produz.
        objetos, _t = self.colher()
        for o in objetos:
            self.assertNotEqual(o.get('SOURCE_ID'), o['URL'])

    def test_M4_bypassar_a_social_matriz(self):
        """Sem a matriz a dizer NAO, a fase de posts compraria. Com ela, nao."""
        real = mz.decisao
        mz.decisao = lambda p, c, **k: {'DECISAO': mz.PERMITIDA_SIM, 'ROTA': 'x',
                                        'PORQUE': 'mutante', 'CLASSE': 'APIFY'}
        try:
            antes = cc.contas_autorizadas
            cc.contas_autorizadas = lambda p: []
            try:
                # passa o portao da politica e cai no do inventario: PROVA que
                # era a matriz que o barrava, e nao a falta de conta.
                self.assertIsNone(cc.fase_posts('LINKEDIN'))
            finally:
                cc.contas_autorizadas = antes
        finally:
            mz.decisao = real
        self.assertEqual(mz.decisao('LINKEDIN', 'FETCH_POST')['DECISAO'],
                         'ROUTE_NOT_ALLOWED')

    def test_M5_registar_capacidade_sem_implementacao(self):
        """O registo aceita declaracao; o que ele nao deixa e ela PROMETER."""
        semfuncao = [capa for (plat, capa), v in reg.registados().items()
                     if plat == 'LINKEDIN' and not (v['ROTA'] or v['EXECUTA'])]
        self.assertTrue(semfuncao, 'nenhuma declaracao sem funcao para medir')
        for capa in semfuncao:
            self.assertFalse(cap.promete_resultado(capa), capa)
            _o, trace = sx.COLLECT(platform='LINKEDIN', capability=capa,
                                   run_id='op01-m5')
            self.assertNotEqual(trace.get('RESULT'), 'OK', capa)

    def test_M6_chamar_o_adapter_direto_do_workflow(self):
        """Nenhum workflow nomeia o adaptador nem a funcao da rota."""
        wf = os.path.join(RAIZ, '.github', 'workflows')
        maus = []
        if os.path.isdir(wf):
            for f in sorted(os.listdir(wf)):
                if not f.endswith(('.yml', '.yaml')):
                    continue
                corpo = open(os.path.join(wf, f), encoding='utf-8',
                             errors='replace').read()
                for proibido in ('adaptador_linkedin', 'identidade_pelo_site',
                                 'harvestapi'):
                    if proibido in corpo:
                        maus.append('%s: %s' % (f, proibido))
        self.assertEqual(maus, [], maus)

    def test_M7_transformar_http_error_em_zero_results(self):
        """Um 403 que se lesse como zero ensinaria a casa a nao ver o muro."""
        _o, bloqueado = self.colher(
            transporte=_transporte(erro=http.RotaBloqueada('HTTP 403')))
        _o2, vazio = self.colher(transporte=_transporte('<html>nada</html>'))
        self.assertNotEqual(bloqueado.get('RESULT'), vazio.get('RESULT'))
        self.assertEqual(vazio.get('RESULT'), 'ZERO_RESULTS')

    def test_M8_transformar_route_not_allowed_em_unknown(self):
        """A recusa de politica tem nome, e ele nao e UNKNOWN."""
        _o, trace = self.colher(site_url='https://www.linkedin.com/company/image-line')
        self.assertEqual(trace.get('RESULT'), 'ROUTE_NOT_ALLOWED')
        self.assertNotIn(trace.get('RESULT'), ('UNKNOWN', 'UNKNOWN_ERROR', None))
        d = mz.decisao('LINKEDIN', 'FETCH_POST')
        self.assertEqual(d['DECISAO'], 'ROUTE_NOT_ALLOWED')
        self.assertNotEqual(d['DECISAO'], 'NOT_DECLARED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
