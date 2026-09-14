"""A coleta de Instagram não pode repetir os erros que esta casa já pagou.

Custo real: ZERO. Nenhuma chave é usada, nenhuma chamada sai da máquina, nenhum
navegador é aberto. Tudo o que toca rede está injetado.

O QUE ESTES TESTES TRAVAM — cada um é uma cicatriz, não uma hipótese
---------------------------------------------------------------------
1. `waitForFinish=280` pedia 280 s e a plataforma corta em 60. Havia 21 manifestos no
   acervo com `status da plataforma: READY` e RAW marcado PRESERVED — retrato de meia
   coleta apresentado como coleta preservada.
2. `SUCCEEDED` com itens NÃO prova completude: uma execução medida teve 107 de 161
   requisições falhadas, devolveu 708 itens e saiu SUCCEEDED. No dia seguinte, 4.723.
3. Campo que o schema não declara é DESCARTADO em silêncio pela Apify. Custou 8
   execuções pagas que devolveram o mesmo consultor de cibersegurança.
4. A DESCRIÇÃO de um campo pode sugerir valor que o enum não aceita (`recent_activity`
   contra enum `["popular","recent"]`).
5. Entrada vazia contra `required: []` passa — e o ator roda com os exemplos da vitrine.
6. Comentário é dado pessoal: o handle não pode chegar ao artefato.
7. Parser sem dado se apresentando como fonte sem dado — medido em 3 de 10 objetos.
"""
import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import coletor                   # noqa: E402
import contrato_ator as ca       # noqa: E402
import instagram_janela as ij    # noqa: E402
import instagram_pessoal as ip   # noqa: E402


# ─────────────────────────────────────────────────── plataforma de mentira, sem rede
class ApifyFalsa:
    """Responde como a Apify responde — inclusive nas horas em que ela mente."""

    def __init__(self, *, status_no_post='RUNNING', status_depois='SUCCEEDED',
                 itens=None, requests_failed=0, requests_finished=10,
                 chave_stats='SDK_CRAWLER_STATISTICS_0'):
        self.status_no_post = status_no_post
        self.status_depois = status_depois
        self.itens = itens if itens is not None else [{'a': 1}]
        self.requests_failed = requests_failed
        self.requests_finished = requests_finished
        # O nome da chave de estatística MUDA entre versões do Crawlee. O padrão aqui é o
        # nome velho; os testes trocam para os novos e o coletor tem de continuar achando.
        self.chave_stats = chave_stats
        self.urls = []
        self.consultas = 0

    def __call__(self, url, *, token, metodo='GET', corpo=None, timeout=300, **kw):
        self.urls.append(url)
        if '/runs?' in url:
            return {'data': {'id': 'RUN1', 'status': self.status_no_post,
                             'defaultDatasetId': 'DS1', 'defaultKeyValueStoreId': 'KV1',
                             'startedAt': '2026-09-02T00:00:00.000Z', 'buildNumber': '0.0.1'}}
        if '/actor-runs/' in url:
            self.consultas += 1
            return {'data': {'id': 'RUN1', 'status': self.status_depois,
                             'defaultDatasetId': 'DS1', 'defaultKeyValueStoreId': 'KV1',
                             'startedAt': '2026-09-02T00:00:00.000Z',
                             'finishedAt': '2026-09-02T00:03:00.000Z',
                             'buildNumber': '0.0.1'}}
        if '/datasets/' in url:
            return self.itens
        if '/keys' in url:
            return {'data': {'items': [{'key': 'INPUT'},
                                       {'key': self.chave_stats},
                                       {'key': 'OUTPUT'}]}}
        if '/records/' in url:
            if url.rstrip('/').endswith(self.chave_stats):
                return {'requestsFailed': self.requests_failed,
                        'requestsFinished': self.requests_finished}
            raise AssertionError('pediu um registro que não existe: %s' % url)
        raise AssertionError('URL inesperada no teste: %s' % url)


class ColetorEsperaDeVerdade(unittest.TestCase):
    """A espera de 60 s da plataforma não pode passar por fim de execução."""

    def setUp(self):
        self._curl = coletor._curl
        self._sleep = coletor.time.sleep
        coletor.time.sleep = lambda s: None

    def tearDown(self):
        coletor._curl = self._curl
        coletor.time.sleep = self._sleep

    def _rodar(self, falsa, **kw):
        coletor._curl = falsa
        return coletor.executar(
            'ator~x', {'a': 1}, token='t', run_id='T1', platform='INSTAGRAM',
            country='ES', mission='M', query='q', source_version='v',
            evidence_path='e.json', salvar_raw=False, **kw)

    def test_nunca_pede_mais_de_60_segundos_a_plataforma(self):
        """O teto documentado é 60. Pedir 280 não compra 280 — compra ilusão."""
        f = ApifyFalsa()
        self._rodar(f, wait=280)
        post = [u for u in f.urls if '/runs?' in u][0]
        self.assertIn('waitForFinish=60', post,
                      'pediu espera acima do teto da plataforma: %s' % post)

    def test_status_transitorio_vira_consulta_ate_o_fim(self):
        """RUNNING no POST tem de virar consulta, não leitura do dataset."""
        f = ApifyFalsa(status_no_post='RUNNING', status_depois='SUCCEEDED')
        itens, man = self._rodar(f, wait=120)
        self.assertGreaterEqual(f.consultas, 1, 'não consultou o estado da execução')
        self.assertEqual(man['STATUS'], 'SUCCESS')
        self.assertEqual(man['RUN_REACHED_TERMINAL'], 'YES')
        self.assertEqual(man['RAW_COMPLETENESS'], 'RUN_REACHED_TERMINAL_STATUS')
        self.assertEqual(len(itens), 1)

    def test_execucao_que_nao_termina_e_PARTIAL_e_o_raw_diz_que_e_parcial(self):
        """O defeito dos 21 manifestos: READY lido como se fosse resultado."""
        f = ApifyFalsa(status_no_post='READY', status_depois='READY', itens=[{'a': 1}] * 77)
        itens, man = self._rodar(f, wait=65)
        self.assertEqual(man['STATUS'], 'PARTIAL',
                         'execução que não chegou ao fim não pode sair SUCCESS')
        self.assertEqual(man['RUN_REACHED_TERMINAL'], 'NO')
        self.assertEqual(man['RAW_COMPLETENESS'], 'PARTIAL_RUN_WAS_NOT_TERMINAL',
                         'retrato de meia coleta não pode passar por coleta completa')
        self.assertIn('NÃO chegou a status terminal', man['ERROR'])
        self.assertEqual(len(itens), 77, 'os itens parciais continuam preservados')

    def test_requisicoes_falhadas_derrubam_o_SUCCESS_mesmo_com_itens(self):
        """708 itens com 107 requisições falhadas saiu SUCCEEDED. Não sai mais."""
        f = ApifyFalsa(status_no_post='SUCCEEDED', itens=[{'a': 1}] * 708,
                       requests_failed=107, requests_finished=54)
        _itens, man = self._rodar(f)
        self.assertEqual(man['STATUS'], 'PARTIAL')
        self.assertIn('107', man['ERROR'])
        self.assertEqual(man['REQUESTS_FAILED'], 107)

    def test_a_trava_sobrevive_ao_crawlee_renomear_a_chave(self):
        """O Crawlee v4 renomeou a chave. Trava que se desliga sozinha não é trava.

        Pedir `SDK_CRAWLER_STATISTICS_0` pelo nome funcionava HOJE. No dia em que o ator
        atualizasse, a leitura voltaria vazia EM SILÊNCIO e o caso dos 107 requests
        falhados voltaria a passar como SUCCESS — sem erro nenhum para avisar.
        """
        for nome in ('SDK_CRAWLER_STATISTICS_0',            # SDK antigo
                     'CRAWLEE_CRAWLER_STATISTICS_0',        # Crawlee v4
                     '__CRAWLER_STATISTICS_1a2b3c'):        # Crawlee em Python
            f = ApifyFalsa(status_no_post='SUCCEEDED', itens=[{'a': 1}] * 700,
                           requests_failed=107, requests_finished=54, chave_stats=nome)
            _itens, man = self._rodar(f)
            self.assertEqual(107, man['REQUESTS_FAILED'],
                             'não achou a estatística com a chave %s' % nome)
            self.assertEqual('PARTIAL', man['STATUS'], 'com a chave %s' % nome)

    def test_o_bruto_ganha_impressao_digital_do_conteudo(self):
        """Caminho e rótulo não provam que o arquivo ainda é o que a execução produziu.

        E a soma sai do CONTEÚDO, não do .gz: o gzip carimba a hora dentro do arquivo,
        então duas gravações dos mesmos itens teriam somas diferentes — uma impressão
        digital que muda sozinha não identifica coisa nenhuma.
        """
        import hashlib
        import tempfile
        itens = [{'b': 2}, {'a': 1}]
        esperado = hashlib.sha256(
            json.dumps(itens, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
        antigo = coletor.RAW_DIR
        with tempfile.TemporaryDirectory() as tmp:
            coletor.RAW_DIR = tmp
            try:
                coletor._curl = ApifyFalsa(status_no_post='SUCCEEDED', itens=itens)
                _i, man = coletor.executar(
                    'ator~x', {'a': 1}, token='t', run_id='T-SHA', platform='INSTAGRAM',
                    country='ES', mission='M', query='q', source_version='v',
                    evidence_path='e.json')
            finally:
                coletor.RAW_DIR = antigo
        self.assertEqual(esperado, man['RAW_SHA256'])
        self.assertEqual('PRESERVED', man['RAW_EVIDENCE_STATE'])

    def test_o_POST_que_cria_execucao_paga_NUNCA_e_repetido(self):
        """Repetir um GET é barato. Repetir um POST é comprar de novo.

        O transporte deste ambiente derruba conexão no meio da troca — está documentado no
        próprio arquivo. Se o POST chegou e só a resposta se perdeu, repetir acende uma
        SEGUNDA execução paga, órfã: sem run_id, sem manifesto, sem custo rastreado. Com as
        4 tentativas antigas, até 4 execuções por chamada. E `maxTotalChargeUsd` não
        protege disso: ele limita cada execução, nunca a soma das que ninguém sabe que
        existem.
        """
        posts = {'n': 0}

        def transporte_que_cai(cmd, capture_output, text, timeout):
            class R:
                returncode, stdout, stderr = 52, '', 'ws_closed_mid_exchange'
            if '-X' in cmd and cmd[cmd.index('-X') + 1] == 'POST':
                posts['n'] += 1
            return R()

        antigo = coletor.subprocess.run
        coletor.subprocess.run = transporte_que_cai
        try:
            with self.assertRaises(coletor.PostTalvezCriado):
                coletor._curl('http://x/runs?a=1', token='t', metodo='POST', corpo={'a': 1})
        finally:
            coletor.subprocess.run = antigo
        self.assertEqual(1, posts['n'],
                         'o POST foi disparado %d vezes — cada uma é uma execução paga'
                         % posts['n'])

    def test_POST_perdido_ADOTA_a_execucao_em_vez_de_acender_outra(self):
        """A execução pode ter nascido do outro lado. Adotar é a única saída que não paga 2x."""
        criados = {'n': 0}

        class TransportePerdeORetorno(ApifyFalsa):
            def __call__(self, url, *, token, metodo='GET', corpo=None, timeout=300, **kw):
                if metodo == 'POST':
                    criados['n'] += 1
                    raise coletor.PostTalvezCriado('a resposta se perdeu na volta')
                if '/runs?desc' in url:          # a busca pela execução órfã
                    return {'data': {'items': [
                        {'id': 'RUN_ORFA', 'status': 'SUCCEEDED',
                         'defaultDatasetId': 'DS1', 'defaultKeyValueStoreId': 'KV1',
                         'startedAt': '2099-01-01T00:00:00.000Z',
                         'finishedAt': '2099-01-01T00:01:00.000Z'}]}}
                return super().__call__(url, token=token, metodo=metodo, corpo=corpo,
                                        timeout=timeout, **kw)

        _itens, man = self._rodar(TransportePerdeORetorno())
        self.assertEqual(1, criados['n'], 'disparou POST mais de uma vez')
        self.assertEqual('YES', man['RUN_ADOPTED_AFTER_TRANSPORT_LOSS'])
        self.assertEqual('SUCCESS', man['STATUS'])

    def test_estatistica_ausente_nao_vira_prova_de_que_nada_falhou(self):
        """Ausência de prova de falha não é prova de ausência de falha."""
        class SemEstatistica(ApifyFalsa):
            def __call__(self, url, **kw):
                if 'SDK_CRAWLER_STATISTICS_0' in url:
                    raise RuntimeError('404')
                return super().__call__(url, **kw)
        _itens, man = self._rodar(SemEstatistica(status_no_post='SUCCEEDED'))
        self.assertEqual(man['REQUESTS_FAILED'], 'NOT_PRESERVED')
        self.assertNotEqual(man['REQUESTS_FAILED'], 0,
                            'não lido nunca pode virar zero')

    def test_teto_de_gasto_e_build_vao_para_a_plataforma(self):
        """A trava tem de estar do lado da Apify, não só na minha aritmética."""
        f = ApifyFalsa()
        self._rodar(f, teto_usd=0.2, build='0.0.776')
        post = [u for u in f.urls if '/runs?' in u][0]
        self.assertIn('maxTotalChargeUsd=0.2', post)
        self.assertIn('build=0.0.776', post)

    def test_custo_lido_na_hora_nasce_rotulado_como_nao_liquidado(self):
        """US$0,90 anunciados, US$5,04 reais. O rótulo é o que impede repetir."""
        _itens, man = self._rodar(ApifyFalsa(status_no_post='SUCCEEDED'))
        self.assertEqual(man['COST_STATE'], 'NOT_SETTLED')

    def test_o_manifesto_nunca_carrega_credencial(self):
        _itens, man = self._rodar(ApifyFalsa(status_no_post='SUCCEEDED'))
        self.assertNotIn('apify_api_', json.dumps(man, ensure_ascii=False))


# ─────────────────────────────────────────────────────── o portão grátis do gasto
CONTRATO_FALSO = {
    'STATE': ca.CONTRATO_OK, 'BUILD_NUMBER': '0.0.164', 'BUILD_FINISHED_AT': 'hoje',
    'CAMPOS': ['postUrls', 'maxCommentsPerPost', 'sortOrder'],
    'OBRIGATORIOS': [],
    'PROPRIEDADES': {
        'postUrls': {'type': 'array'},
        'maxCommentsPerPost': {'type': 'integer', 'default': 10},
        'sortOrder': {'type': 'string', 'enum': ['popular', 'recent'],
                      'default': 'popular'},
    },
}


class PortaoDeContrato(unittest.TestCase):

    def _codigos(self, entrada, **kw):
        _ok, probs = ca.conferir(CONTRATO_FALSO, entrada, **kw)
        return [p['CODIGO'] for p in probs if p['GRAVIDADE'] == 'REPROVA']

    def test_campo_que_o_schema_nao_declara_reprova(self):
        """A Apify não recusa: ela descarta em silêncio e cobra o run."""
        self.assertIn('CAMPO_DESCONHECIDO',
                      self._codigos({'postUrls': ['x'], 'sortComentariosPor': 'top'}))

    def test_valor_fora_do_enum_reprova_mesmo_vindo_da_descricao_do_campo(self):
        """`recent_activity` está na prosa do campo e NÃO está no enum."""
        self.assertIn('VALOR_FORA_DO_ENUM',
                      self._codigos({'postUrls': ['x'], 'sortOrder': 'recent_activity'}))

    def test_valor_do_enum_passa(self):
        self.assertEqual([], self._codigos({'postUrls': ['x'], 'sortOrder': 'recent'}))

    def test_entrada_vazia_reprova_mesmo_com_required_vazio(self):
        """Passa no contrato e roda com os exemplos da vitrine. É o pior dos dois."""
        self.assertIn('NO_INPUT_DECLARED', self._codigos({}))

    def test_credencial_na_entrada_reprova(self):
        self.assertIn('CREDENCIAL_NA_ENTRADA',
                      self._codigos({'postUrls': ['x'], 'sessionid': 'abc'}))

    def test_build_que_mudou_reprova(self):
        """Os quatro atores oficiais foram reconstruídos no mesmo minuto de 31/08."""
        self.assertIn('BUILD_DRIFT',
                      self._codigos({'postUrls': ['x']}, build_esperado='0.0.100'))

    def test_obrigatorio_ausente_reprova(self):
        c = dict(CONTRATO_FALSO, OBRIGATORIOS=['postUrls'])
        _ok, probs = ca.conferir(c, {'sortOrder': 'recent'})
        self.assertIn('OBRIGATORIO_AUSENTE',
                      [p['CODIGO'] for p in probs if p['GRAVIDADE'] == 'REPROVA'])

    def test_schema_nao_publicado_avisa_mas_nao_reprova(self):
        """Ausência de régua não é reprovação — é ordem para andar só com entrada provada."""
        c = {'STATE': ca.SCHEMA_NAO_PUBLICADO, 'WHY': 'o build não publica inputSchema'}
        ok, probs = ca.conferir(c, {'videoUrl': 'x'})
        self.assertTrue(ok)
        self.assertEqual(['AVISO'], [p['GRAVIDADE'] for p in probs])

    def test_ator_nao_alcancado_e_diferente_de_ator_inexistente(self):
        """Queda de rede não pode virar veredito sobre a ferramenta."""
        ok, probs = ca.conferir({'STATE': ca.ATOR_NAO_ALCANCADO, 'WHY': 'HTTP 500'},
                                {'postUrls': ['x']})
        self.assertFalse(ok)
        self.assertEqual('ATOR_NAO_ALCANCADO', probs[0]['CODIGO'])


# ──────────────────────────────────────────────────────────────── dado pessoal
class DadoPessoal(unittest.TestCase):

    def test_o_portao_nasce_fechado(self):
        self.assertFalse(ip.pode_coletar(env={})[0])

    def test_so_abre_com_autorizacao_explicita(self):
        self.assertTrue(ip.pode_coletar(env={ip.AUTORIZADO: '1'})[0])
        self.assertFalse(ip.pode_coletar(env={ip.AUTORIZADO: 'talvez'})[0])

    def test_o_handle_do_autor_nunca_chega_ao_artefato(self):
        r = ip.normalizar_comentario(
            {'ownerUsername': 'mario.rossi.1980', 'text': 'ottimo prodotto'},
            objeto={'SHORTCODE': 'ABC', 'ACCOUNT_HANDLE': 'bayer_italia'}, run_id='R1')
        texto = json.dumps(r, ensure_ascii=False)
        self.assertNotIn('mario.rossi.1980', texto, 'o handle vazou para o artefato')
        self.assertEqual('REDACTED_BY_POLICY', r['AUTHOR_HANDLE'])
        self.assertTrue(r['AUTHOR_PSEUDONYM'].startswith('IGP-'))

    def test_a_frase_fica_inteira_porque_e_a_evidencia(self):
        frase = 'in Emilia il diserbo non ha tenuto, troppa pioggia a maggio'
        r = ip.normalizar_comentario({'text': frase, 'ownerUsername': 'x'},
                                     objeto={}, run_id='R1')
        self.assertEqual(frase, r['COMMENT_TEXT_RAW'])

    def test_pseudonimo_e_estavel_e_nao_colide(self):
        self.assertEqual(ip.pseudonimo('ana'), ip.pseudonimo('ana'))
        self.assertNotEqual(ip.pseudonimo('ana'), ip.pseudonimo('ano'))

    def test_o_comentario_nasce_com_a_revisao_juridica_pendente(self):
        r = ip.normalizar_comentario({'text': 'x'}, objeto={}, run_id='R1')
        self.assertEqual('PENDING', r['LEGAL_REVIEW'])
        self.assertEqual('UNDECLARED_PENDING_LEGAL_REVIEW', r['RETENTION_STATE'])
        self.assertEqual('PROHIBITED_FOR_CURRENT_PILOT', r['AUTHOR_SCORING'])

    def test_voz_nao_e_incidencia(self):
        r = ip.normalizar_comentario({'text': 'x'}, objeto={}, run_id='R1')
        self.assertEqual('FIELD_VOICE_OBSERVED', r['EVIDENCE_CLASS'])
        self.assertIn('FIELD_PROBLEM_CONFIRMED', r['NAO_E'])

    def test_expurgo_sem_confirmar_nao_apaga_nada(self):
        r = ip.expurgar(confirmar=False)
        self.assertTrue(r['DRY_RUN'])


# ──────────────────────────────────────────────────────────── a rota do navegador
class RotaDaJanela(unittest.TestCase):

    def test_numero_arredondado_pela_tela_e_declarado_como_tal(self):
        """"18,7 mil" não é 18.737. Tratar os dois como iguais inventa perda de seguidor."""
        v, como = ij._numero('18,7 mil')
        self.assertEqual(18700, v)
        self.assertIn('ARREDONDADO', como)

    def test_numero_exato_e_declarado_exato(self):
        v, como = ij._numero('2.751')
        self.assertEqual(2751, v)
        self.assertNotIn('ARREDONDADO', como)

    def test_o_que_a_fonte_nao_deu_nao_vira_zero(self):
        v, _como = ij._numero(None)
        self.assertEqual('NOT_KNOWN', v)
        self.assertNotEqual(0, v)

    def test_legenda_resgatada_da_og_nunca_se_disfarca_de_legenda_inteira(self):
        """Medido: 3 de 10 objetos vieram sem o bloco do embed. A og salva — rotulada."""
        r = {'OG_DESCRIPTION': '14 likes, 1 comments - syngentaitalia no August 3, '
                               '2026: "Breakthrough...".'}
        ij._resgatar_do_og(r)
        self.assertEqual('Breakthrough...', r['CAPTION'])
        self.assertEqual('NO', r['CAPTION_IS_COMPLETE'])
        self.assertIn('TRUNCADA', r['CAPTION_SOURCE'])

    def test_sem_og_a_legenda_e_NOT_KNOWN_e_nao_string_vazia(self):
        r = {'OG_DESCRIPTION': 'NOT_KNOWN'}
        ij._resgatar_do_og(r)
        self.assertEqual('NOT_KNOWN', r['CAPTION'])


if __name__ == '__main__':
    unittest.main(verbosity=2)


class CheiroDeCredencial(unittest.TestCase):
    """Um aviso que grita à toa treina a casa a ignorar aviso — e aí o certo passa."""

    def test_campo_de_busca_por_autor_nao_e_credencial(self):
        """Medido contra harvestapi~linkedin-post-search: 4 falsos positivos por `auth`."""
        for campo in ('authorKeywords', 'authorUrls', 'authorsCompanies',
                      'authorsIndustryId', 'autorNome'):
            self.assertFalse(ca.cheira_a_credencial(campo),
                             '%s foi acusado de credencial e não é' % campo)

    def test_credencial_de_verdade_continua_sendo_pega(self):
        for campo in ('sessionid', 'session_id', 'cookie', 'apiKey', 'api_key',
                      'password', 'accessToken', 'authorization', 'loginUser'):
            self.assertTrue(ca.cheira_a_credencial(campo),
                            '%s passou e é credencial' % campo)
