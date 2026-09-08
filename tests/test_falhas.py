#!/usr/bin/env python3
"""
As doze propriedades que a taxonomia canônica tem de sustentar.

Não testam implementação: testam LEIS. Se uma delas cair, o SINTONIA voltou a
confundir "não tinha conteúdo" com "meu coletor quebrou" — que é o defeito que
`falhas.py` existe para impedir.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import falhas                      # noqa: E402
import apify_pool as ap            # noqa: E402
import social_rotas as sr          # noqa: E402
import social_sessao as ss         # noqa: E402
import source_health as sh         # noqa: E402


class TestZeroNaoEErro(unittest.TestCase):
    """LEI 1 e 2 — ZERO não é ERRO, e ERRO não é ZERO."""

    def test_zero_resultado_nao_e_falha(self):
        self.assertFalse(falhas.e_falha('ZERO_RESULTS'))
        self.assertEqual(falhas.camada('ZERO_RESULTS'), falhas.NENHUMA)
        self.assertFalse(falhas.degrada_fonte('ZERO_RESULTS'))

    def test_nenhuma_falha_e_confundida_com_zero(self):
        for nome in falhas.NOMES:
            if nome in falhas.NAO_SAO_FALHA:
                continue
            self.assertTrue(falhas.e_falha(nome),
                            '%s escapou da contagem de falha' % nome)

    def test_zero_e_falha_nao_compartilham_estado(self):
        self.assertNotEqual(falhas.traduzir('SOURCE_EMPTY'),
                            falhas.traduzir('SOURCE_UNAVAILABLE'))


class TestSessaoNaoViraFonteVazia(unittest.TestCase):
    """LEI 3 — AUTH EXPIRED não é NO CONTENT."""

    def test_sessao_vencida_nao_degrada_a_fonte(self):
        for velho in ('SESSION_EXPIRED', 'MFA_REQUIRED', 'LOGIN_WALL', 'TOKEN_INVALID'):
            canon = falhas.traduzir(velho)
            self.assertEqual(falhas.camada(canon), falhas.ROUTE, velho)
            self.assertFalse(falhas.degrada_fonte(canon),
                             '%s degradou a fonte — sessao vencida nao mede fonte' % velho)

    def test_sessao_vencida_nao_e_zero(self):
        self.assertTrue(falhas.e_falha('SESSION_EXPIRED'))


class TestRateLimitNaoEFonteCaida(unittest.TestCase):
    """LEI 4 — RATE LIMITED não é SOURCE DOWN."""

    def test_rate_limit_e_da_rota(self):
        self.assertEqual(falhas.camada('RATE_LIMITED'), falhas.ROUTE)
        self.assertFalse(falhas.degrada_fonte('RATE_LIMITED'))

    def test_rate_limit_e_retentavel_e_5xx_tambem_mas_por_camadas_diferentes(self):
        self.assertTrue(falhas.retentavel('RATE_LIMITED'))
        self.assertTrue(falhas.retentavel('SOURCE_UNAVAILABLE'))
        self.assertNotEqual(falhas.camada('RATE_LIMITED'),
                            falhas.camada('SOURCE_UNAVAILABLE'))


class TestParserDriftNaoEHttp(unittest.TestCase):
    """LEI 5 — PARSER DRIFT é diferente de falha de HTTP."""

    def test_parser_e_nosso_e_pede_gente(self):
        self.assertEqual(falhas.camada('PARSER_DRIFT'), falhas.EXECUTOR)
        self.assertFalse(falhas.esperado('PARSER_DRIFT'),
                         'parser quebrado tem de pedir gente')

    def test_http_5xx_e_da_fonte_e_nao_pede_gente(self):
        self.assertEqual(falhas.classificar(http=503), 'SOURCE_UNAVAILABLE')
        self.assertTrue(falhas.esperado('SOURCE_UNAVAILABLE'))

    def test_parser_nao_degrada_a_fonte(self):
        self.assertFalse(falhas.degrada_fonte('PARSER_DRIFT'),
                         'parser quebrado NUNCA e prova sobre a fonte')

    def test_excecao_de_parse_no_executor_vira_parser_drift(self):
        """A prova viva: uma KeyError no adaptador não pode sair como FAILED."""
        def adaptador_quebrado(**_):
            return [{'a': 1}][0]['campo_que_a_plataforma_removeu']

        sr.ADAPTADORES[('PLATAFORMA_DE_TESTE', 'CAP')] = adaptador_quebrado
        import social_matriz as mz
        mz.MATRIZ.setdefault('PLATAFORMA_DE_TESTE', {})['CAP'] = [
            mz.r('rota-de-teste', 'PUBLIC_NATIVE', 'SIM', 'PROVED', 'zero', 'teste')]
        try:
            _, reg = sr.executar(platform='PLATAFORMA_DE_TESTE', capability='CAP',
                                 run_id='T-PARSER')
            self.assertEqual(reg['ESTADO'], 'PARSER_DRIFT')
            self.assertEqual(reg['EXECUTOR_HEALTH'], falhas.BROKEN)
            self.assertEqual(reg['SOURCE_HEALTH'], falhas.HEALTHY)
            self.assertFalse(reg['EXPECTED'])
        finally:
            del sr.ADAPTADORES[('PLATAFORMA_DE_TESTE', 'CAP')]
            mz.MATRIZ.pop('PLATAFORMA_DE_TESTE', None)


class TestRotaNaoDegradaFonte(unittest.TestCase):
    """LEI 6 — ROUTE UNAVAILABLE não degrada SOURCE HEALTH."""

    def test_so_a_camada_source_degrada_a_fonte(self):
        for nome in falhas.NOMES:
            esperado = falhas.camada(nome) == falhas.SOURCE
            self.assertEqual(falhas.degrada_fonte(nome), esperado, nome)

    def test_source_health_nao_e_chamado_com_falha_de_rota(self):
        """O adapter tem de RECUSAR julgar a fonte quando quem falhou foi a rota."""
        for nome in ('ROUTE_NOT_ALLOWED', 'QUOTA_EXHAUSTED', 'AUTH_EXPIRED',
                     'BUDGET_EXHAUSTED', 'PARSER_DRIFT', 'EXECUTOR_UNAVAILABLE'):
            avaliar, _ = falhas.fetch_ok_para_source_health(nome)
            self.assertFalse(avaliar, '%s deixaria source_health dizer SOURCE_FAILED' % nome)

    def test_source_health_e_chamado_quando_a_fonte_falou(self):
        for nome, fetch in (('OK', True), ('ZERO_RESULTS', True),
                            ('SOURCE_UNAVAILABLE', False), ('SOURCE_GONE', False)):
            avaliar, fo = falhas.fetch_ok_para_source_health(nome)
            self.assertTrue(avaliar, nome)
            self.assertEqual(fo, fetch, nome)
        self.assertEqual(sh.version_state(fetch_ok=False, current_hash=None,
                                          previous_hash='x'), sh.SOURCE_FAILED)

    def test_as_tres_saudes_sao_independentes(self):
        reg = sr.selar({'ESTADO': 'AUTH_EXPIRED'})
        self.assertEqual(reg['SOURCE_HEALTH'], falhas.HEALTHY)
        self.assertEqual(reg['ROUTE_HEALTH'], falhas.UNHEALTHY)
        self.assertEqual(reg['EXECUTOR_HEALTH'], falhas.HEALTHY)


class TestSessaoNaoAutorizaAutomacao(unittest.TestCase):
    """LEI 7 — LOCAL_SESSION disponível não torna a capability permitida."""

    def test_sessao_disponivel_nao_e_autorizacao(self):
        r = ss.usabilidade('INSTAGRAM', 'FETCH_COMMENTS', 'LOCAL_SESSION',
                           ss.THIRD_PARTY, auth_status=ss.SESSION_AVAILABLE)
        self.assertEqual(r['AUTH_STATUS'], ss.SESSION_AVAILABLE)
        self.assertEqual(r['AUTHORIZATION_STATUS'], ss.FORBIDDEN)
        self.assertEqual(r['ROUTE_STATUS'], ss.NOT_USABLE)

    def test_auth_e_authorization_sao_colunas_diferentes(self):
        r = ss.usabilidade('YOUTUBE', 'FETCH_COMMENTS', 'LOCAL_SESSION', ss.THIRD_PARTY,
                           auth_status=ss.SESSION_AVAILABLE)
        self.assertNotEqual(r['AUTH_STATUS'], r['AUTHORIZATION_STATUS'])


class TestOwnPropertyNaoBypassaPolicy(unittest.TestCase):
    """LEI 8 — OWN_PROPERTY não é autorização automática."""

    def test_conta_propria_nao_e_passe_livre(self):
        for plat in ss.POLITICA:
            r = ss.usabilidade(plat, 'FETCH_POST', 'LOCAL_SESSION', ss.OWN_PROPERTY)
            self.assertNotEqual(r['ROUTE_STATUS'], ss.USABLE,
                                '%s deu passe livre para conta propria' % plat)
            self.assertEqual(r['ROUTE_STATUS'], ss.NEEDS_REVIEW, plat)

    def test_a_trava_historica_nao_deixa_mais_passar_por_propriedade(self):
        ok, _ = ss.automacao_permitida('YOUTUBE', ss.OWN_PROPERTY)
        self.assertFalse(ok, 'OWN_PROPERTY voltou a ser um SIM automatico')

    def test_needs_review_nao_e_licenca(self):
        ok, _ = ss.automacao_permitida('LINKEDIN', ss.OWN_PROPERTY)
        self.assertFalse(ok, 'revisao pendente nao autoriza coletar')


class TestTerceiroPorApiOficialNaoERecusado(unittest.TestCase):
    """LEI 9 — THIRD_PARTY via API oficial não é recusado por regra genérica."""

    def test_o_exemplo_da_missao(self):
        """YOUTUBE · FETCH_COMMENTS · OFFICIAL_API · THIRD_PARTY -> USABLE."""
        r = ss.usabilidade('YOUTUBE', 'FETCH_COMMENTS', 'OFFICIAL_API', ss.THIRD_PARTY)
        self.assertEqual(r['ROUTE_STATUS'], ss.USABLE)
        self.assertEqual(r['TERMS_STATUS'], ss.ALLOWED)

    def test_a_mesma_capability_por_sessao_e_recusada(self):
        r = ss.usabilidade('YOUTUBE', 'FETCH_COMMENTS', 'LOCAL_SESSION', ss.THIRD_PARTY)
        self.assertEqual(r['ROUTE_STATUS'], ss.NOT_USABLE)

    def test_a_decisao_e_por_rota_em_todas_as_sete(self):
        for plat in ss.POLITICA:
            api = ss.usabilidade(plat, 'FETCH_PROFILE', 'OFFICIAL_API', ss.THIRD_PARTY)
            sessao = ss.usabilidade(plat, 'FETCH_PROFILE', 'LOCAL_SESSION', ss.THIRD_PARTY)
            self.assertEqual(api['ROUTE_STATUS'], ss.USABLE, plat)
            self.assertEqual(sessao['ROUTE_STATUS'], ss.NOT_USABLE, plat)


class TestRobotsNaoETerms(unittest.TestCase):
    """A separação que a missão exige explicitamente."""

    def test_robots_nao_governa_api_nem_sessao(self):
        for modo in ('OFFICIAL_API', 'OFFICIAL_PAID_API', 'LOCAL_SESSION', 'APIFY'):
            r = ss.usabilidade('YOUTUBE', 'FETCH_POST', modo, ss.THIRD_PARTY)
            self.assertEqual(r['ROBOTS_STATUS'], ss.NOT_APPLICABLE, modo)

    def test_robots_e_terms_sao_campos_separados(self):
        r = ss.usabilidade('YOUTUBE', 'FETCH_POST', 'PUBLIC', ss.THIRD_PARTY)
        self.assertIn('ROBOTS_STATUS', r)
        self.assertIn('TERMS_STATUS', r)
        self.assertNotEqual(r['ROBOTS_STATUS'], r['TERMS_STATUS'])

    def test_robots_publico_nao_e_afirmado_de_memoria(self):
        """Quem lê o robots e `social_rotas.permitido()`, na hora, com o UA real."""
        r = ss.usabilidade('YOUTUBE', 'FETCH_POST', 'PUBLIC', ss.THIRD_PARTY)
        self.assertEqual(r['ROBOTS_STATUS'], ss.UNKNOWN)


class TestUmaLinguaSo(unittest.TestCase):
    """A rota paga e a gratuita falam a mesma língua de erro."""

    def test_a_rota_paga_traduz_para_o_canonico(self):
        for n in ap.ROTACIONAM + ap.NAO_ROTACIONAM:
            self.assertIn(ap.canonico(n), falhas.NOMES, n)

    def test_a_regra_de_rotacao_da_rota_paga_sobrevive(self):
        for n in ap.ROTACIONAM:
            self.assertTrue(falhas.rotaciona(ap.canonico(n)),
                            '%s deixou de rotacionar ao virar canonico' % n)
        for n in ap.NAO_ROTACIONAM:
            self.assertFalse(falhas.rotaciona(ap.canonico(n)),
                             '%s passou a rotacionar sem motivo' % n)

    def test_platform_failure_nao_acusa_a_fonte_sem_prova(self):
        """O nome antigo culpava a plataforma. NAO SEI e mais honesto."""
        self.assertEqual(ap.canonico('PLATFORM_FAILURE'), 'UNKNOWN_ERROR')
        self.assertFalse(falhas.degrada_fonte('PLATFORM_FAILURE'))

    def test_todo_estado_emitido_pelas_rotas_e_traduzivel(self):
        emitidos = ['NOT_APPLICABLE', 'ROUTE_NOT_ALLOWED', 'AUTOMATION_NOT_ALLOWED',
                    'CREDENTIAL_MISSING', 'PAID_ROUTE_REFUSED', 'BLOCKED', 'FAILED',
                    'OK', 'ZERO_RESULTS', 'SESSION_MISSING', 'SESSION_EXPIRED',
                    'MFA_REQUIRED', 'LOGIN_REQUIRED', 'PLATFORM_BLOCKED']
        for e in emitidos:
            self.assertIn(falhas.traduzir(e), falhas.NOMES, e)

    def test_o_balde_failed_foi_desmontado(self):
        """`FAILED` cobria transporte, parser e 4xx. Agora cada um tem nome."""
        self.assertNotEqual(falhas.traduzir('TRANSIENT_NETWORK_ERROR'),
                            falhas.traduzir('PARSER_DRIFT'))
        self.assertNotEqual(falhas.classificar(http=429), falhas.classificar(http=503))
        self.assertNotEqual(falhas.classificar(http=404), falhas.classificar(http=403))


class TestVocabularioMinimo(unittest.TestCase):
    """O vocabulário tem de ser pequeno E completo."""

    def test_nenhum_estado_orfao_sem_nota(self):
        for nome in falhas.NOMES:
            self.assertTrue(len(falhas.ESTADOS[nome].nota) > 30,
                            '%s existe sem explicar por que existe' % nome)

    def test_todo_estado_pertence_a_uma_camada_valida(self):
        for nome in falhas.NOMES:
            self.assertIn(falhas.camada(nome), falhas.CAMADAS, nome)

    def test_so_o_executor_pede_gente(self):
        """`esperado=False` e caro: so vale para defeito NOSSO."""
        for nome in falhas.NOMES:
            if not falhas.esperado(nome):
                self.assertEqual(falhas.camada(nome), falhas.EXECUTOR, nome)

    def test_nao_retentar_o_que_nunca_passa(self):
        for nome in ('PERMANENT_HTTP_ERROR', 'PARSER_DRIFT', 'ROUTE_NOT_ALLOWED',
                     'AUTOMATION_NOT_ALLOWED', 'BUDGET_EXHAUSTED', 'SOURCE_GONE'):
            self.assertFalse(falhas.retentavel(nome),
                             '%s autorizaria repetir um pedido que nunca passa' % nome)


class TestSegredoContinuaProtegido(unittest.TestCase):
    """LEI 10 e 11 — segredo redigido, cookie fora do Git."""

    def test_redacao_continua_funcionando(self):
        sujo = 'Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789'
        limpo = ss.redigir(sujo)
        self.assertNotIn('abcdefghijklmnopqrstuvwxyz0123456789', limpo)

    def test_o_selo_nao_reintroduz_segredo(self):
        reg = sr.selar({'ESTADO': 'AUTH_EXPIRED',
                        'ERRO': ss.redigir('token=apify_api_' + 'z' * 40)})
        self.assertNotIn('z' * 40, str(reg))

    def test_perfil_do_navegador_fica_fora_do_repo(self):
        self.assertFalse(ss._dentro_do_repo(ss.perfil_dir()),
                         'o perfil do navegador nao pode viver dentro do repositorio')


if __name__ == '__main__':
    unittest.main(verbosity=1)
