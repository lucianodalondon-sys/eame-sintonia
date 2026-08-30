#!/usr/bin/env python3
"""
Provas do pool de chaves — TODAS com token falso, nenhuma chamada real.

O contrato de leitura vem do `credenciais.py` do portal-sintonia (Brasil), onde
cada regra custou uma execucao real. Estes testes existem para que a portagem
nao perca nenhuma delas, e para que a rotacao — que e nova — nao queime o pool.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import apify_pool as ap  # noqa: E402

# Tokens FALSOS, com o tamanho real (46) para exercitar o aviso de formato.
def _falso(n):
    return 'apify_api_' + (str(n) * 36)

T1, T2, T3, T4 = _falso(1), _falso(2), _falso(3), _falso(4)


class TestLeituraDoPool(unittest.TestCase):
    """A · B · C · J — a forma do segredo nao pode derrubar a coleta."""

    def test_A_um_token(self):
        self.assertEqual([T1], ap.pool({'APIFY_TOKEN_POOL': T1}))

    def test_B_quatro_tokens_uma_por_linha(self):
        v = '\n'.join([T1, T2, T3, T4])
        self.assertEqual([T1, T2, T3, T4], ap.pool({'APIFY_TOKEN_POOL': v}))

    def test_C_linhas_vazias_e_espacos_sao_ignorados(self):
        v = '\n\n  %s  \n\n\n\t%s\n   \n' % (T1, T2)
        self.assertEqual([T1, T2], ap.pool({'APIFY_TOKEN_POOL': v}))

    def test_J_quantidade_nao_e_fixa(self):
        for n in (1, 2, 3, 5, 9):
            ks = [_falso(i) for i in range(n)]
            with self.subTest(n=n):
                self.assertEqual(n, len(ap.pool(
                    {'APIFY_TOKEN_POOL': '\n'.join(ks)})))

    def test_qualquer_separador(self):
        """O separador e do CODIGO, nao da pessoa — licao paga no Brasil."""
        for sep in ('\n', ',', ';', ' ', '\t', ',\n', ' ; '):
            with self.subTest(sep=repr(sep)):
                self.assertEqual([T1, T2],
                                 ap.pool({'APIFY_TOKEN_POOL': sep.join([T1, T2])}))

    def test_chaves_grudadas_sem_separador_sao_descoladas(self):
        """O colar pode tirar as quebras e grudar tudo numa tira so."""
        self.assertEqual([T1, T2, T3],
                         ap.pool({'APIFY_TOKEN_POOL': T1 + T2 + T3}))

    def test_chave_sozinha_nunca_e_cortada(self):
        """Cortar chave boa no meio a estragaria em silencio."""
        self.assertEqual([T1], ap.pool({'APIFY_TOKEN_POOL': T1}))

    def test_rotulo_dentro_do_valor_e_removido(self):
        for rot in ('APIFY_TOKEN_POOL=', 'apify_token=', 'APIFY_KEYS='):
            with self.subTest(rotulo=rot):
                self.assertEqual([T1], ap.pool({'APIFY_TOKEN_POOL': rot + T1}))

    def test_repetida_sai_uma_vez_mantendo_a_ordem(self):
        """Repetida faria a mesma conta ser consultada duas vezes de graca."""
        self.assertEqual([T1, T2],
                         ap.pool({'APIFY_TOKEN_POOL': '\n'.join([T1, T2, T1])}))

    def test_G_nenhum_token_e_pool_empty(self):
        r = ap.executar_com_pool(['u1'], lambda u, t: ([], ap.TOKEN_OK),
                                 identidade=lambda x: x, env={})
        self.assertEqual(ap.POOL_EMPTY, r['STATE'])
        self.assertEqual(0, r['TOKENS_AVAILABLE'])
        self.assertEqual(['u1'], r['UNITS_PENDING'])


class TestFormatoEAviso(unittest.TestCase):
    """Contar as letras antes de mandar procurar chave revogada."""

    def test_tamanho_certo_nao_avisa(self):
        self.assertEqual('', ap.formato_suspeito(T1))

    def test_letra_faltando_e_diagnosticada_como_colar(self):
        aviso = ap.formato_suspeito(T1[:-1])
        self.assertIn('faltou 1 no colar', aviso)
        self.assertNotIn(T1[:-1], aviso, 'o aviso NUNCA pode conter a chave')

    def test_o_aviso_nunca_recusa_so_avisa(self):
        """Trava nossa nao pode derrubar coleta se a Apify mudar o tamanho."""
        v = T1[:-1]
        self.assertEqual([v], ap.pool({'APIFY_TOKEN_POOL': v}),
                         'formato suspeito continua entrando no pool')

    def test_censo_nao_traz_valor(self):
        c = ap.censo({'APIFY_TOKEN_POOL': '\n'.join([T1, T2])})
        self.assertEqual('YES', c['TOKEN_POOL_PRESENT'])
        self.assertEqual(2, c['TOKEN_POOL_SIZE'])
        texto = repr(c)
        for t in (T1, T2):
            self.assertNotIn(t, texto)


class TestRedacao(unittest.TestCase):
    """H · o segredo nunca aparece na saida, nem dentro de URL ou traceback."""

    def test_redige_token_solto(self):
        self.assertNotIn(T1, ap.redigir('falhou com %s' % T1))

    def test_redige_token_dentro_de_url(self):
        u = 'https://api.apify.com/v2/acts/x/runs?token=%s&clean=true' % T1
        s = ap.redigir('URLError ao chamar %s' % u)
        self.assertNotIn(T1, s)
        self.assertIn('REDACTED', s)

    def test_redige_varios_de_uma_vez(self):
        s = ap.redigir('%s e %s' % (T1, T2))
        for t in (T1, T2):
            self.assertNotIn(t, s)

    def test_excecao_com_token_sai_redigida_do_runner(self):
        def explode(u, t):
            raise RuntimeError('falha chamando https://api.apify.com/?token=%s' % t)
        r = ap.executar_com_pool(['u1'], explode, identidade=lambda x: x,
                                 env={'APIFY_TOKEN_POOL': T1})
        texto = repr(r)
        self.assertNotIn(T1, texto)
        self.assertIn('REDACTED', texto)


class TestRotacao(unittest.TestCase):
    """D · E · F — trocar de chave so quando a CHAVE e o problema."""

    def _runner(self, roteiro, unidades=('u1',), env=None):
        """`roteiro` mapeia posicao-do-pool -> estado devolvido."""
        chamadas = []

        def trabalho(u, token):
            pos = ap.pool(env).index(token) + 1
            chamadas.append((u, pos))
            est = roteiro.get(pos, ap.TOKEN_OK)
            itens = [{'id': '%s-%d' % (u, pos)}] if est == ap.TOKEN_OK else []
            return itens, est

        r = ap.executar_com_pool(list(unidades), trabalho,
                                 identidade=lambda x: x['id'], env=env)
        return r, chamadas

    def test_D_primeiro_expirado_usa_o_segundo(self):
        env = {'APIFY_TOKEN_POOL': '\n'.join([T1, T2])}
        r, ch = self._runner({1: ap.TOKEN_INVALID}, env=env)
        self.assertEqual([1, 2], [c[1] for c in ch])
        self.assertEqual(2, r['TOKENS_USED'])
        self.assertEqual(ap.TOKEN_INVALID, r['BY_POSITION'][0]['FINAL_STATE'])
        self.assertEqual(ap.TOKEN_OK, r['BY_POSITION'][1]['FINAL_STATE'])

    def test_E_primeiro_sem_saldo_usa_o_segundo(self):
        env = {'APIFY_TOKEN_POOL': '\n'.join([T1, T2])}
        r, ch = self._runner({1: ap.TOKEN_EXHAUSTED}, env=env)
        self.assertEqual([1, 2], [c[1] for c in ch])
        self.assertEqual('DONE', r['STATE'])
        self.assertEqual(1, len(r['ITEMS']))

    def test_F_erro_de_parser_NAO_rotaciona(self):
        """Bug meu nao pode queimar o pool inteiro em segundos."""
        env = {'APIFY_TOKEN_POOL': '\n'.join([T1, T2, T3])}
        r, ch = self._runner({1: ap.PARSER_FAILURE}, env=env)
        self.assertEqual([1], [c[1] for c in ch], 'so a primeira chave foi tocada')
        self.assertEqual(1, r['TOKENS_USED'])
        self.assertEqual('STOPPED', r['STATE'])

    def test_unknown_nao_consome_o_pool(self):
        env = {'APIFY_TOKEN_POOL': '\n'.join([T1, T2, T3, T4])}
        r, ch = self._runner({1: ap.UNKNOWN_FAILURE}, env=env)
        self.assertEqual(1, r['TOKENS_USED'])
        self.assertEqual(4, r['TOKENS_AVAILABLE'])

    def test_falha_de_plataforma_nao_rotaciona(self):
        env = {'APIFY_TOKEN_POOL': '\n'.join([T1, T2])}
        r, _ = self._runner({1: ap.PLATFORM_FAILURE}, env=env)
        self.assertEqual(1, r['TOKENS_USED'])

    def test_I_dedupe_sobre_troca_de_token(self):
        """Trocar de chave nao pode fazer o mesmo item entrar duas vezes."""
        env = {'APIFY_TOKEN_POOL': '\n'.join([T1, T2])}
        chamadas = []

        def trabalho(u, token):
            pos = ap.pool(env).index(token) + 1
            chamadas.append(pos)
            if pos == 1 and u == 'u2':
                return [], ap.TOKEN_EXHAUSTED
            return [{'id': u}, {'id': 'comum'}], ap.TOKEN_OK

        r = ap.executar_com_pool(['u1', 'u2'], trabalho,
                                 identidade=lambda x: x['id'], env=env)
        ids = [x['id'] for x in r['ITEMS']]
        self.assertEqual(len(ids), len(set(ids)), 'nenhum item repetido')
        self.assertIn('comum', ids)
        self.assertEqual(1, ids.count('comum'))
        self.assertGreaterEqual(r['DUPLICATES_REMOVED'], 1)

    def test_rotacao_retoma_a_unidade_nao_reinicia_a_coleta(self):
        """A chave B continua de onde a A parou — nao refaz o que ja foi feito."""
        env = {'APIFY_TOKEN_POOL': '\n'.join([T1, T2])}
        feitas = []

        def trabalho(u, token):
            pos = ap.pool(env).index(token) + 1
            if u == 'u3' and pos == 1:
                return [], ap.TOKEN_EXHAUSTED
            feitas.append((u, pos))
            return [{'id': u}], ap.TOKEN_OK

        r = ap.executar_com_pool(['u1', 'u2', 'u3', 'u4'], trabalho,
                                 identidade=lambda x: x['id'], env=env)
        self.assertEqual(['u1', 'u2', 'u3', 'u4'], r['UNITS_DONE'])
        self.assertEqual([('u1', 1), ('u2', 1), ('u3', 2), ('u4', 2)], feitas,
                         'u1 e u2 NAO foram refeitas com a segunda chave')

    def test_posicao_e_numero_nunca_valor(self):
        env = {'APIFY_TOKEN_POOL': '\n'.join([T1, T2])}
        r, _ = self._runner({1: ap.TOKEN_EXHAUSTED}, env=env)
        self.assertEqual([1, 2], r['POOL_POSITION_USED'])
        for p in r['BY_POSITION']:
            self.assertIsInstance(p['POOL_POSITION'], int)
        self.assertNotIn(T1, repr(r))


class TestClassificador(unittest.TestCase):
    """A cota esgotada CHEGA COMO SUCESSO — e por isso a ordem importa."""

    def test_cota_esgotada_se_apresenta_como_sucesso(self):
        self.assertEqual(ap.TOKEN_EXHAUSTED, ap.classificar(
            status='SUCCEEDED', status_message='free user run limit reached',
            itens=[]))

    def test_http_de_credencial(self):
        self.assertEqual(ap.TOKEN_INVALID, ap.classificar(http=401))
        self.assertEqual(ap.TOKEN_OTHER_AUTH_FAILURE, ap.classificar(http=403))
        self.assertEqual(ap.TOKEN_RATE_LIMITED_ACCOUNT, ap.classificar(http=429))

    def test_5xx_e_plataforma_nao_credencial(self):
        self.assertEqual(ap.PLATFORM_FAILURE, ap.classificar(http=503))
        self.assertNotIn(ap.classificar(http=503), ap.ROTACIONAM)

    def test_ator_falhou_nao_e_a_chave(self):
        for s in ('FAILED', 'ABORTED', 'TIMED-OUT'):
            with self.subTest(status=s):
                self.assertEqual(ap.ACTOR_FAILURE, ap.classificar(status=s))
                self.assertNotIn(ap.classificar(status=s), ap.ROTACIONAM)

    def test_excecao_de_parsing_e_parser_failure(self):
        self.assertEqual(ap.PARSER_FAILURE,
                         ap.classificar(excecao=ValueError('json decode error')))

    def test_excecao_generica_e_unknown_e_nao_rotaciona(self):
        e = ap.classificar(excecao=RuntimeError('algo estranho'))
        self.assertEqual(ap.UNKNOWN_FAILURE, e)
        self.assertNotIn(e, ap.ROTACIONAM)

    def test_sucesso_com_itens_e_token_ok(self):
        self.assertEqual(ap.TOKEN_OK,
                         ap.classificar(status='SUCCEEDED', itens=[{'a': 1}]))


class TestTetoNaoCresceComOPool(unittest.TestCase):
    """§15 — o pool existe para RESILIENCIA, nao para volume."""

    def test_teto_de_itens_e_respeitado_com_muitas_chaves(self):
        env = {'APIFY_TOKEN_POOL': '\n'.join(_falso(i) for i in range(12))}
        self.assertEqual(12, len(ap.pool(env)))
        r = ap.executar_com_pool(
            ['u%d' % i for i in range(50)],
            lambda u, t: ([{'id': '%s-%d' % (u, j)} for j in range(10)], ap.TOKEN_OK),
            identidade=lambda x: x['id'], env=env, teto_itens=80)
        self.assertLessEqual(len(r['ITEMS']), 80,
                             'doze chaves nao autorizam mais que o teto')


if __name__ == '__main__':
    unittest.main(verbosity=2)


class TestNadaVazaParaORepositorio(unittest.TestCase):
    """O teste que impede o vazamento chegar ao Git — nao so ao log."""

    def test_nenhum_token_literal_em_arquivo_versionado(self):
        import re
        import subprocess
        pad = re.compile(r'apify_api_[A-Za-z0-9]{20,}')
        saida = subprocess.run(['git', 'ls-files'], cwd=ROOT,
                               capture_output=True, text=True).stdout.split('\n')
        achados = []
        for f in saida:
            if not f or not os.path.exists(os.path.join(ROOT, f)):
                continue
            try:
                with open(os.path.join(ROOT, f), encoding='utf-8') as fh:
                    txt = fh.read()
            except (UnicodeDecodeError, IsADirectoryError):
                continue
            for m in pad.finditer(txt):
                # tokens sinteticos dos proprios testes sao digito repetido
                corpo = m.group(0)[len('apify_api_'):]
                if len(set(corpo)) > 2:
                    achados.append(f)
                    break
        self.assertEqual([], achados, 'token literal em arquivo versionado: %s' % achados)

    def test_o_workflow_nao_tem_agendamento_nem_token(self):
        import re
        p = os.path.join(ROOT, '.github', 'workflows', 'sensores-linkedin.yml')
        self.assertTrue(os.path.exists(p), 'o workflow precisa existir')
        s = open(p, encoding='utf-8').read()
        corpo = '\n'.join(l for l in s.splitlines() if not l.strip().startswith('#'))
        self.assertIn('workflow_dispatch', corpo)
        self.assertIsNone(re.search(r'^\s*(schedule|cron):', corpo, re.M),
                          'coleta paga nao pode rodar por relogio')
        self.assertIn('add-mask', corpo, 'cada chave tem de ser mascarada')
        self.assertIsNone(re.search(r'apify_api_[A-Za-z0-9]{10,}', s))

    def test_o_coletor_de_linkedin_respeita_os_tetos(self):
        import linkedin_sensores as ls
        self.assertEqual(8, ls.TETO_PERFIS)
        self.assertEqual(80, ls.TETO_POSTS)
        self.assertEqual(8, len(ls.ALVOS), 'nenhum nome novo entra')
        nomes = {a['NAME'] for a in ls.ALVOS}
        self.assertIn('Sabrina Locatelli', nomes)
        self.assertIn('Federico Cavina', nomes)
