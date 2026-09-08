"""A sessao local e uma rota, e uma rota precisa saber dizer NAO.

Estes testes nao exigem conta real, nao abrem navegador e nao tocam a rede.
Eles guardam as duas coisas que, se quebrarem, quebram em silencio:

  1. que estar logado nunca vira permissao para automatizar;
  2. que sessao ruim nunca vira ausencia de conteudo.

O segundo e o mais perigoso dos dois. Um muro de login convertido em "a conta
nao tem posts" envenena o corpus e ninguem descobre, porque o numero fica
plausivel.
"""
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))

import social_sessao as ss          # noqa: E402
import social_guarda as sg          # noqa: E402
import social_matriz as mz          # noqa: E402


class TestAutomacaoNaoDecorreDeSessao(unittest.TestCase):
    """CASO H — LOCAL_SESSION proibida para a capability."""

    def test_terceiro_e_proibido_em_todas_as_sete_plataformas(self):
        for plat in ss.POLITICA:
            ok, porque = ss.automacao_permitida(plat, ss.THIRD_PARTY)
            self.assertFalse(ok, '%s deixou passar automacao contra terceiro' % plat)
            self.assertTrue(len(porque) > 40,
                            '%s recusou sem citar a clausula que sustenta o NAO' % plat)

    def test_cada_negativa_aponta_uma_fonte(self):
        for plat, p in ss.POLITICA.items():
            self.assertTrue(str(p.get('FONTE', '')).strip(),
                            '%s nega sem fonte verificavel' % plat)

    def test_plataforma_desconhecida_e_negada_por_omissao(self):
        ok, _ = ss.automacao_permitida('REDE_QUE_NAO_EXISTE', ss.THIRD_PARTY)
        self.assertFalse(ok, 'o padrao de uma plataforma nao declarada tem de ser NAO')

    def test_conta_propria_NAO_e_passe_livre(self):
        """CORRIGIDO em 2026-09-08 — este teste afirmava o contrario, e estava errado.

        A versao anterior canonizava `OWN_PROPERTY -> PERMITIDO` nas sete
        plataformas. Nenhuma das sete clausulas lidas abre excecao escrita ao dono:
        os Termos §3 do YouTube proibem "any automated means" sem falar em
        propriedade. E a nota de cada plataforma nesta mesma tabela ja mandava usar
        a API oficial para conta propria — ou seja, o valor dizia SIM enquanto a
        nota ao lado dizia "nao por aqui".

            SER DONO MUDA O QUE SE PODE LER. NAO MUDA O QUE SE PODE AUTOMATIZAR.

        O veredito honesto e `NEEDS_REVIEW`, e revisao pendente nao e licenca.
        """
        ok, _ = ss.automacao_permitida('YOUTUBE', ss.OWN_PROPERTY)
        self.assertFalse(ok, 'OWN_PROPERTY voltou a ser um SIM automatico')
        r = ss.usabilidade('YOUTUBE', 'FETCH_POST', 'LOCAL_SESSION', ss.OWN_PROPERTY)
        self.assertEqual(r['ROUTE_STATUS'], ss.NEEDS_REVIEW)

    def test_terceiro_por_api_oficial_NAO_e_recusado(self):
        """O outro lado do mesmo erro: a recusa valia para a SESSAO, e generalizou."""
        r = ss.usabilidade('YOUTUBE', 'FETCH_COMMENTS', 'OFFICIAL_API', ss.THIRD_PARTY)
        self.assertEqual(r['ROUTE_STATUS'], ss.USABLE)


class TestEstadosDaSessao(unittest.TestCase):
    """CASOS B, C, D, J — o que a pagina mostra vira que estado."""

    def test_muro_de_login_vira_login_required(self):
        estado, _ = ss.classificar_pagina('<div>Please log in to continue</div>')
        self.assertEqual(estado, ss.LOGIN_REQUIRED)

    def test_mfa_nao_vira_login_generico(self):
        """CASO D — MFA e acao HUMANA, e precisa ser distinguivel."""
        estado, _ = ss.classificar_pagina('<p>Enter the verification code we sent</p>')
        self.assertEqual(estado, ss.MFA_REQUIRED)
        self.assertNotEqual(estado, ss.LOGIN_REQUIRED)

    def test_sessao_expirada_tem_estado_proprio(self):
        estado, _ = ss.classificar_pagina('<p>Your session expired</p>')
        self.assertEqual(estado, ss.SESSION_EXPIRED)

    def test_bloqueio_da_plataforma_nao_e_pagina_vazia(self):
        estado, _ = ss.classificar_pagina('<p>We detected unusual activity</p>')
        self.assertEqual(estado, ss.PLATFORM_BLOCKED)

    def test_pagina_vazia_e_unknown_e_nunca_conteudo_ausente(self):
        """CASO J — erro de sessao nao classifica conteudo como ausente."""
        estado, _ = ss.classificar_pagina('')
        self.assertEqual(estado, ss.UNKNOWN)

    def test_nenhum_estado_ruim_significa_zero_conteudo(self):
        ruins = (ss.LOGIN_REQUIRED, ss.MFA_REQUIRED, ss.SESSION_EXPIRED,
                 ss.PLATFORM_BLOCKED, ss.UNKNOWN, ss.SESSION_MISSING)
        for e in ruins:
            self.assertNotIn(e, ('ZERO_RESULTS', 'NOT_FOUND', 'EMPTY'),
                             'estado de sessao virou ausencia de conteudo: %s' % e)


class TestPerfil(unittest.TestCase):
    """CASO A — perfil nao existe."""

    def test_perfil_vem_de_env_var_quando_definida(self):
        antes = os.environ.get(ss.ENV_PERFIL)
        os.environ[ss.ENV_PERFIL] = os.path.join('tmp', 'perfil-de-teste')
        try:
            self.assertTrue(ss.perfil_dir().endswith('perfil-de-teste'))
        finally:
            if antes is None:
                del os.environ[ss.ENV_PERFIL]
            else:
                os.environ[ss.ENV_PERFIL] = antes

    def test_nenhum_caminho_pessoal_no_padrao(self):
        """O padrao nao pode carregar o nome de ninguem."""
        import navegador
        self.assertNotIn('Luciano', navegador.PERFIL_COLETA)
        self.assertNotIn('London1', navegador.PERFIL_COLETA)

    def test_perfil_dentro_do_repo_e_recusado(self):
        antes = os.environ.get(ss.ENV_PERFIL)
        os.environ[ss.ENV_PERFIL] = os.path.join(RAIZ, 'perfil-perigoso')
        try:
            r = ss.preflight()
            self.assertTrue(r['PERFIL_DENTRO_DO_REPO'])
            self.assertEqual(r['ESTADO'], ss.UNHEALTHY)
        finally:
            if antes is None:
                del os.environ[ss.ENV_PERFIL]
            else:
                os.environ[ss.ENV_PERFIL] = antes

    def test_preflight_nunca_devolve_o_caminho_do_perfil(self):
        """O relatorio diz que HA perfil, nunca ONDE ele esta."""
        r = ss.preflight()
        for v in r.values():
            self.assertNotIn(os.path.expanduser('~'), str(v))


class TestRedacao(unittest.TestCase):
    """FASE 7 — nada de segredo em log, excecao ou manifesto."""

    def test_cookie_e_apagado(self):
        self.assertNotIn('IGSNa9Xk', ss.redigir('Cookie: sessionid=IGSNa9Xk2m0Q'))

    def test_bearer_e_apagado(self):
        self.assertNotIn('FALSOtok', ss.redigir('Authorization: Bearer FALSOtok123'))

    def test_caminho_pessoal_e_apagado(self):
        for t in (r'C:\Users\Luciano\perfil', '/home/luciano/x', '/Users/luciano/y'):
            self.assertNotIn('uciano', ss.redigir(t), 'vazou em %r' % t)

    def test_redigir_aceita_none(self):
        self.assertIsNone(ss.redigir(None))


class TestGuardaDeCredencial(unittest.TestCase):
    """RED TEAM 1-4 — cookie em log, perfil no git, token em excecao."""

    def _pega(self, texto):
        for tipo, padrao in sg.CONTEUDO_PROIBIDO:
            m = padrao.search(texto)
            if m and sg._valor_e_segredo(m.group(0)):
                return tipo
        return None

    def test_pega_segredo_de_verdade(self):
        reais = ('Cookie: sessionid=IGSNa9Xk2m0QpZ7v',
                 'Set-Cookie: li_at=AQEDATh8ZmQFxYzA',
                 'Authorization: Bearer FALSOtok123',
                 'password = "MinhaSenh4Real"',
                 'access_token: "ya29.a0AfH6SMBxxxxxxxxxx"')
        for t in reais:
            self.assertIsNotNone(self._pega(t), 'deixou passar: %r' % t)

    def test_nao_reclama_de_referencia_a_variavel(self):
        """Guarda que grita demais vira guarda desligada."""
        falsos = ('Authorization: Bearer $SUPABASE_SECRET_KEY',
                  'Authorization: Bearer ${{ secrets.TOKEN }}',
                  'Authorization: Bearer <TOKEN>',
                  'password = "your-password-here"')
        for t in falsos:
            self.assertIsNone(self._pega(t), 'falso positivo em: %r' % t)

    def test_nomes_de_perfil_de_navegador_sao_bloqueados(self):
        for f in ('data/Cookies', 'p/Default/Login Data', 'a/chrome-profile/x',
                  '.sintonia-browser/y', 'tests/cookies.txt'):
            self.assertTrue(sg.ARQUIVOS_PROIBIDOS.search(f) or sg.PASTAS_PROIBIDAS.search(f),
                            'nao bloqueou %s' % f)

    def test_o_repositorio_esta_limpo_agora(self):
        """RED TEAM 2 — o perfil nao pode estar rastreado."""
        achados = sg.varrer(sg.rastreados(), 'RASTREADO')
        novos = [a for a in achados if a[1].split(':')[0] not in sg.DIVIDA_CONHECIDA]
        self.assertEqual(novos, [], 'segredo ou perfil rastreado: %s' % novos)

    def test_gitignore_cobre_perfil_de_navegador(self):
        with open(os.path.join(RAIZ, '.gitignore'), encoding='utf-8') as f:
            g = f.read()
        for regra in ('.sintonia-browser/', 'chrome-profile/', 'cookies.sqlite'):
            self.assertIn(regra, g, 'gitignore nao cobre %s' % regra)


class TestPoliticaDeRota(unittest.TestCase):
    """CASOS E, F, G, I — a rota mais barata capaz, saudavel e permitida."""

    def setUp(self):
        import social_rotas
        self.sr = social_rotas

    def test_rota_publica_resolve_e_sessao_nao_e_usada(self):
        """CASO E — MASTODON tem rota publica; o auth mode tem de ser PUBLIC."""
        d = mz._rota_padrao(mz.MATRIZ['MASTODON']['SEARCH_HASHTAG'])
        self.assertEqual(mz.auth_mode(d), 'PUBLIC')

    def test_api_oficial_resolve_e_sessao_nao_e_usada(self):
        """CASO F — YOUTUBE prefere a Data API, nunca a sessao."""
        d = mz._rota_padrao(mz.MATRIZ['YOUTUBE']['SEARCH_KEYWORD'])
        self.assertEqual(mz.auth_mode(d), 'OFFICIAL_API')

    def test_apify_nao_roda_quando_rota_livre_resolve(self):
        """CASO I — Apify existe para INSTAGRAM/FETCH_POST e nao e a padrao."""
        d = mz._rota_padrao(mz.MATRIZ['INSTAGRAM']['FETCH_POST'])
        self.assertNotEqual(d['CLASSE'], 'APIFY')

    def test_rota_paga_recusa_motivo_fora_do_vocabulario(self):
        _, r = self.sr.executar(platform='X', capability='SEARCH_KEYWORD', run_id='T',
                                permitir_pago=True,
                                motivo_pago='porque a Apify ja estava configurada')
        # O estado passou a ser selado pela taxonomia canonica. O nome antigo
        # sobrevive em ESTADO_ORIGINAL — a traducao e conferivel, nao e fe.
        self.assertEqual(r['ESTADO'], 'BUDGET_EXHAUSTED')
        self.assertEqual(r['ESTADO_ORIGINAL'], 'PAID_ROUTE_REFUSED')
        self.assertFalse(r['DEGRADES_SOURCE'],
                         'recusa de gasto NOSSA nao diz nada sobre a fonte')

    def test_local_session_contra_terceiro_para_antes_de_navegar(self):
        """RED TEAM 9 — sessao usada em capability nao autorizada."""
        antes = mz.MATRIZ['LINKEDIN'].get('FETCH_PROFILE')
        mz.MATRIZ['LINKEDIN']['FETCH_PROFILE'] = [
            mz.r('linkedin:sessao', 'LOCAL_SESSION', 'CONDICIONAL',
                 'POSSIBLE_NOT_PROVED', 'zero', 'fixture de teste', None)]
        try:
            _, r = self.sr.executar(platform='LINKEDIN', capability='FETCH_PROFILE',
                                    run_id='T', ownership=ss.THIRD_PARTY)
            self.assertEqual(r['ESTADO'], ss.AUTOMATION_NOT_ALLOWED)
            self.assertEqual(r['AUTH_MODE'], 'LOCAL_SESSION')
        finally:
            if antes is None:
                del mz.MATRIZ['LINKEDIN']['FETCH_PROFILE']
            else:
                mz.MATRIZ['LINKEDIN']['FETCH_PROFILE'] = antes

    def test_o_padrao_de_ownership_e_terceiro(self):
        """O caso perigoso tem de ser o padrao; conta propria se declara."""
        antes = mz.MATRIZ['YOUTUBE'].get('FETCH_PROFILE')
        mz.MATRIZ['YOUTUBE']['FETCH_PROFILE'] = [
            mz.r('yt:sessao', 'LOCAL_SESSION', 'CONDICIONAL',
                 'POSSIBLE_NOT_PROVED', 'zero', 'fixture', None)]
        try:
            _, r = self.sr.executar(platform='YOUTUBE', capability='FETCH_PROFILE',
                                    run_id='T')
            self.assertEqual(r['ESTADO'], ss.AUTOMATION_NOT_ALLOWED)
        finally:
            if antes is None:
                del mz.MATRIZ['YOUTUBE']['FETCH_PROFILE']
            else:
                mz.MATRIZ['YOUTUBE']['FETCH_PROFILE'] = antes


class TestNaoAutentica(unittest.TestCase):
    """FASE 4 — o executor nunca faz login."""

    def test_nenhum_modulo_da_missao_digita_credencial(self):
        proibido = ('type_password', 'fill(\'password', 'send_keys', 'submit_login',
                    'Input.insertText', 'autenticar(', 'fazer_login')
        for nome in ('social_sessao.py', 'social_rotas.py', 'social_scrap.py',
                     'social_guarda.py'):
            with open(os.path.join(RAIZ, 'scripts', nome), encoding='utf-8') as f:
                corpo = f.read()
            for p in proibido:
                self.assertNotIn(p, corpo, '%s parece tentar autenticar (%s)' % (nome, p))


if __name__ == '__main__':
    unittest.main(verbosity=2)
