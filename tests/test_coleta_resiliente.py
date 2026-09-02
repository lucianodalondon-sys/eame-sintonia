"""Token acaba, processo morre, e a coleta nao recomeca do zero.

O teste atravessa o MESMO caminho da producao: scripts/coleta_checkpoint.py
chamando scripts/apify_pool.executar_com_pool. Nao ha ator falso dentro do
modulo — o falso e o `trabalho`, que e o ponto de extensao que o proprio
pool ja expunha.

Custo real: zero. Nenhuma chave e usada, nenhuma chamada sai da maquina.
"""
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
import apify_pool as ap          # noqa: E402
import coleta_checkpoint as C    # noqa: E402

DSN = os.environ.get('EAME_TEST_DSN')
N_ITENS = 10
UNIDADES = ['u1', 'u2', 'u3', 'u4', 'u5']
POR_UNIDADE = 2


def itens_da(unidade):
    i = UNIDADES.index(unidade)
    return [{'plataforma': 'web', 'content_id': 'X%02d' % (i * POR_UNIDADE + k)}
            for k in range(POR_UNIDADE)]


class TestIdentidadeNaoDependeDaRodada(unittest.TestCase):

    def test_token_run_dataset_e_captura_sao_recusados(self):
        for c in ('token', 'apify_token', 'run_id', 'dataset_id', 'captured_at',
                  'coletado_em', 'pool_position'):
            ok, ruins = C.identidade_valida(['plataforma', 'content_id', c])
            with self.subTest(campo=c):
                self.assertFalse(ok)
                self.assertIn(c, ruins)

    def test_plataforma_mais_external_id_e_aceita(self):
        ok, _ = C.identidade_valida(['plataforma', 'content_id'])
        self.assertTrue(ok)

    def test_a_entrada_igual_da_o_mesmo_hash(self):
        self.assertEqual(C.hash_da_entrada({'a': 1, 'b': [2, 3]}),
                         C.hash_da_entrada({'b': [2, 3], 'a': 1}))
        self.assertNotEqual(C.hash_da_entrada({'a': 1}), C.hash_da_entrada({'a': 2}))


class TestRotacaoSemBanco(unittest.TestCase):
    """O que o pool italiano ja garantia, usado como controle."""

    def test_falha_desconhecida_nao_queima_o_pool(self):
        env = {'APIFY_TOKEN_POOL': 'apify_api_' + 'a' * 36 + ',apify_api_' + 'b' * 36}
        chamadas = []

        def trabalho(u, t):
            chamadas.append(t)
            raise ValueError('bug meu')
        r = ap.executar_com_pool(['u1'], trabalho, identidade=lambda x: x, env=env)
        self.assertEqual(1, len(chamadas), 'um bug nosso nao pode gastar o pool inteiro')
        self.assertEqual(ap.UNKNOWN_FAILURE, r['BY_POSITION'][0]['FINAL_STATE'])

    def test_token_esgotado_rotaciona_e_retoma_a_mesma_unidade(self):
        env = {'APIFY_TOKEN_POOL': 'apify_api_' + 'a' * 36 + ',apify_api_' + 'b' * 36}
        vistos = []

        def trabalho(u, t):
            vistos.append((u, t[-4:]))
            if t.endswith('a' * 4):
                return [], ap.TOKEN_EXHAUSTED
            return itens_da(u), ap.TOKEN_OK
        r = ap.executar_com_pool(['u1'], trabalho,
                                 identidade=lambda x: x['content_id'], env=env)
        self.assertEqual('DONE', r['STATE'])
        self.assertEqual(['u1', 'u1'], [v[0] for v in vistos])
        self.assertEqual(2, r['TOKENS_USED'])


@unittest.skipUnless(DSN, 'sem EAME_TEST_DSN: o caminho produtivo precisa de banco')
class TestCaminhoProdutivo(unittest.TestCase):
    """A prova integrada: token acaba, processo reinicia, nada se perde."""

    def setUp(self):
        self.b = C.Banco(DSN)
        # A ordem importa: conteudo_visto_em referencia conteudo, conteudo
        # referencia collection_run. Limpar de fora para dentro. Apagar por
        # run_id (e nao por prefixo de content_id) para que qualquer linha
        # deixada por uma mutacao anterior tambem saia.
        self.b.executa("delete from public.conteudo_visto_em "
                       "where run_id = 'ENSAIO-RESILIENCIA'")
        self.b.executa("delete from public.conteudo "
                       "where run_id = 'ENSAIO-RESILIENCIA'")
        self.b.executa("delete from public.checkpoint_coleta "
                       "where collection_target like 'ENSAIO-%'")
        self.b.executa("delete from public.collection_run "
                       "where run_id = 'ENSAIO-RESILIENCIA'")
        self.b.executa(
            "insert into public.collection_run (run_id, platform, actor, started_at, "
            "status, rule_version) values ('ENSAIO-RESILIENCIA','web','ensaio', now(), "
            "'rodando','ensaio') on conflict do nothing")
        self.canal = self.b.executa(
            "select c.id from public.canal c where c.channel_id='ENSAIO-CANAL-01'")[0][0]

    def persistir(self, itens, unidade):
        n = 0
        for it in itens:
            self.b.executa(
                "insert into public.conteudo (canal_id, run_id, tipo, content_id, "
                "hash_conteudo, rule_version) values (%s,'ENSAIO-RESILIENCIA','post',%s,"
                "md5(%s)||md5(%s),'ensaio') on conflict (canal_id, content_id) do nothing"
                % (self.canal, C._lit(it['content_id']), C._lit(it['content_id']),
                   C._lit(it['content_id'])))
            self.b.executa(
                "insert into public.conteudo_visto_em (conteudo_id, run_id, visto_em) "
                "select id,'ENSAIO-RESILIENCIA', now() from public.conteudo "
                "where canal_id=%s and content_id=%s on conflict do nothing"
                % (self.canal, C._lit(it['content_id'])))
            n += 1
        return n

    def conteudos(self):
        return int(self.b.executa(
            "select count(*) from public.conteudo where content_id like 'X%'")[0][0])

    def test_A_a_H_o_ciclo_inteiro(self):
        env = {'APIFY_TOKEN_POOL': 'apify_api_' + 'a' * 36 + ',apify_api_' + 'b' * 36}
        alvo, entrada = 'ENSAIO-RESILIENCIA', {'q': 'ensaio', 'n': N_ITENS}

        # ── A · token 1 coleta parte, e esgota na terceira unidade ──
        estado = {'chamadas': 0}

        def trabalho1(u, t):
            estado['chamadas'] += 1
            if t.endswith('a' * 4) and UNIDADES.index(u) >= 2:
                return [], ap.TOKEN_EXHAUSTED
            if t.endswith('b' * 4):
                raise AssertionError('a segunda chave nao devia ser usada nesta fase')
            return itens_da(u), ap.TOKEN_OK

        r1 = C.coletar(self.b, target=alvo, entrada=entrada, actor='ensaio',
                       platform='web', unidades=UNIDADES, trabalho=trabalho1,
                       identidade=lambda x: x['content_id'],
                       persistir=self.persistir,
                       campos_da_identidade=['plataforma', 'content_id'],
                       env={'APIFY_TOKEN_POOL': 'apify_api_' + 'a' * 36})
        # ── B · o que chegou esta PERSISTIDO, nao so em memoria ──
        self.assertEqual(4, self.conteudos(), 'duas unidades salvas antes do esgotamento')
        self.assertEqual('PARCIAL', r1['CHECKPOINT_STATE'])

        # ── C/D · o processo MORRE aqui. Nada da memoria sobrevive. ──
        del r1, trabalho1, estado

        # ── E · outro processo comeca, com a segunda chave ──
        estado2 = {'unidades': []}

        def trabalho2(u, t):
            estado2['unidades'].append(u)
            return itens_da(u), ap.TOKEN_OK

        r2 = C.coletar(self.b, target=alvo, entrada=entrada, actor='ensaio',
                       platform='web', unidades=UNIDADES, trabalho=trabalho2,
                       identidade=lambda x: x['content_id'],
                       persistir=self.persistir,
                       campos_da_identidade=['plataforma', 'content_id'], env=env)

        # ── F · resultado final completo ──
        self.assertEqual(N_ITENS, self.conteudos(), 'EXPECTED_ITEMS = N, LOST = 0')
        self.assertEqual('CONCLUIDO', r2['CHECKPOINT_STATE'])
        # ── RESUME_FROM_CHECKPOINT · nao refez as unidades ja feitas ──
        self.assertNotIn('u1', estado2['unidades'], 'u1 ja estava feita e foi repaga')
        self.assertNotIn('u2', estado2['unidades'], 'u2 ja estava feita e foi repaga')
        self.assertEqual(['u3', 'u4', 'u5'], estado2['unidades'])

    def test_G_zero_duplicata_viva_mesmo_com_item_repetido(self):
        """TOKEN A traz X; TOKEN B, apos retomada, traz X de novo."""
        alvo, entrada = 'ENSAIO-DUPLICATA', {'q': 'dup'}
        env = {'APIFY_TOKEN_POOL': 'apify_api_' + 'a' * 36 + ',apify_api_' + 'b' * 36}

        def trabalho(u, t):
            if t.endswith('a' * 4):
                # entrega os itens E ESGOTA: o pool retoma a MESMA unidade
                self.persistir(itens_da(u), u)
                return [], ap.TOKEN_EXHAUSTED
            return itens_da(u), ap.TOKEN_OK

        C.coletar(self.b, target=alvo, entrada=entrada, actor='ensaio', platform='web',
                  unidades=['u1'], trabalho=trabalho,
                  identidade=lambda x: x['content_id'], persistir=self.persistir,
                  campos_da_identidade=['plataforma', 'content_id'], env=env)
        self.assertEqual(POR_UNIDADE, self.conteudos(),
                         'o mesmo item visto por duas chaves e UM conteudo')
        vistas = int(self.b.executa(
            "select count(*) from public.conteudo_visto_em")[0][0])
        self.assertEqual(POR_UNIDADE, vistas, 'a proveniencia da rodada continua guardada')

    def test_sem_checkpoint_nenhuma_chamada_paga_acontece(self):
        """A guarda. Sem linha aberta, o ator nao e chamado."""
        chamou = {'n': 0}

        def trabalho(u, t):
            chamou['n'] += 1
            return itens_da(u), ap.TOKEN_OK

        # checkpoint fechado como CONCLUIDO: a guarda tem de recusar
        self.b.executa(
            "insert into public.checkpoint_coleta (collection_target, input_hash, actor, "
            "platform, started_at, updated_at, estado, rule_version) values "
            "('ENSAIO-FECHADO', %s, 'ensaio','web', now(), now(), 'CONCLUIDO','ensaio') "
            "on conflict do nothing" % C._lit(C.hash_da_entrada({'q': 'x'})))
        r = C.coletar(self.b, target='ENSAIO-FECHADO', entrada={'q': 'x'},
                      actor='ensaio', platform='web', unidades=['u1'],
                      trabalho=trabalho, identidade=lambda x: x['content_id'],
                      persistir=self.persistir,
                      campos_da_identidade=['plataforma', 'content_id'],
                      env={'APIFY_TOKEN_POOL': 'apify_api_' + 'a' * 36})
        self.assertEqual(0, chamou['n'], 'houve chamada paga sem checkpoint valido')
        self.assertEqual(C.JA_CONCLUIDO, r['STATE'])
        self.assertEqual(0, r['PAID_CALLS'])

    def test_identidade_invalida_barra_antes_de_gastar(self):
        chamou = {'n': 0}

        def trabalho(u, t):
            chamou['n'] += 1
            return [], ap.TOKEN_OK
        r = C.coletar(self.b, target='ENSAIO-ID', entrada={'q': 'y'}, actor='ensaio',
                      platform='web', unidades=['u1'], trabalho=trabalho,
                      identidade=lambda x: x, persistir=self.persistir,
                      campos_da_identidade=['content_id', 'run_id'],
                      env={'APIFY_TOKEN_POOL': 'apify_api_' + 'a' * 36})
        self.assertEqual('IDENTIDADE_INVALIDA', r['STATE'])
        self.assertEqual(0, chamou['n'])


@unittest.skipUnless(DSN, 'sem EAME_TEST_DSN')
class TestMutacoes(unittest.TestCase):
    """Uma trava que passaria sem a trava nao e trava."""

    def setUp(self):
        self.b = C.Banco(DSN)
        self.canal = self.b.executa(
            "select id from public.canal where channel_id='ENSAIO-CANAL-01'")[0][0]

    def test_remover_a_guarda_deixa_a_chamada_paga_acontecer(self):
        """MUTACAO: sem pode_gastar, o ator seria chamado com checkpoint fechado."""
        self.b.executa(
            "insert into public.checkpoint_coleta (collection_target, input_hash, actor, "
            "platform, started_at, updated_at, estado, rule_version) values "
            "('MUT-FECHADO', %s,'x','web', now(), now(), 'CONCLUIDO','v') "
            "on conflict do nothing" % C._lit(C.hash_da_entrada({'q': 'm'})))
        chamou = {'com': 0, 'sem': 0}

        def trabalho(u, t):
            chamou['com'] += 1
            return [], ap.TOKEN_OK
        C.coletar(self.b, target='MUT-FECHADO', entrada={'q': 'm'}, actor='x',
                  platform='web', unidades=['u1'], trabalho=trabalho,
                  identidade=lambda x: x, persistir=lambda i, u: 0,
                  campos_da_identidade=['plataforma', 'content_id'],
                  env={'APIFY_TOKEN_POOL': 'apify_api_' + 'a' * 36})
        self.assertEqual(0, chamou['com'], 'a guarda deixou passar')

        original = C.pode_gastar
        try:
            C.pode_gastar = lambda b, t, h: (True, 'MUTACAO', 1, None)

            def trabalho2(u, t):
                chamou['sem'] += 1
                return [], ap.TOKEN_OK
            C.coletar(self.b, target='MUT-FECHADO', entrada={'q': 'm'}, actor='x',
                      platform='web', unidades=['u1'], trabalho=trabalho2,
                      identidade=lambda x: x, persistir=lambda i, u: 0,
                      campos_da_identidade=['plataforma', 'content_id'],
                      env={'APIFY_TOKEN_POOL': 'apify_api_' + 'a' * 36})
        finally:
            C.pode_gastar = original
        self.assertEqual(1, chamou['sem'],
                         'sem a guarda a chamada paga teria acontecido — '
                         'se isto der 0, o teste nao esta exercendo nada')

    def test_bypassar_a_identidade_natural_reprova(self):
        """MUTACAO: sem a chave natural, o item repetido viraria dois conteudos.

        A trava e `conteudo_canal_id_content_id_key`, que existe desde a 003.
        A rodada passada diagnosticou BR-14 como "falta a trava" e estava
        errado: a trava existia e o que faltava era provar que o caminho
        produtivo passa por ela. A 016 chegou a criar um indice novo com as
        mesmas colunas — segundo dono da mesma lei — e o banco recusou.
        """
        self.b.executa("delete from public.conteudo_visto_em using public.conteudo c "
                       "where c.id = conteudo_visto_em.conteudo_id "
                       "and c.content_id='MUTDUP'")
        self.b.executa("delete from public.conteudo where content_id='MUTDUP'")

        def insere():
            self.b.executa(
                "insert into public.conteudo (canal_id, run_id, tipo, content_id, "
                "hash_conteudo, rule_version) values (%s,'ENSAIO-RESILIENCIA','post',"
                "'MUTDUP', md5('a')||md5('b'),'ensaio') "
                "on conflict (canal_id, content_id) do nothing" % self.canal)
        insere()
        insere()
        n = int(self.b.executa(
            "select count(*) from public.conteudo where content_id='MUTDUP'")[0][0])
        self.assertEqual(1, n, 'o indice natural deixou o mesmo item entrar duas vezes')

        # E sem o indice entrariam dois. O `on conflict` do chamador nem
        # compila sem ele — entao a mutacao insere direto, que e exatamente o
        # que um chamador descuidado faria.
        self.b.executa("alter table public.conteudo drop constraint "
                       "conteudo_canal_id_content_id_key")
        try:
            self.b.executa(
                "insert into public.conteudo (canal_id, run_id, tipo, content_id, "
                "hash_conteudo, rule_version) values (%s,'ENSAIO-RESILIENCIA','post',"
                "'MUTDUP', md5('a')||md5('b'),'ensaio')" % self.canal)
            n2 = int(self.b.executa(
                "select count(*) from public.conteudo where content_id='MUTDUP'")[0][0])
        finally:
            # limpar ANTES de repor o indice: se sobrar a duplicata que a
            # mutacao criou, o indice nao pode nascer de volta.
            self.b.executa("delete from public.conteudo_visto_em using public.conteudo c "
                           "where c.id = conteudo_visto_em.conteudo_id "
                           "and c.content_id='MUTDUP'")
            self.b.executa("delete from public.conteudo where content_id='MUTDUP'")
            self.b.executa("alter table public.conteudo add constraint "
                           "conteudo_canal_id_content_id_key "
                           "UNIQUE (canal_id, content_id)")
        self.assertEqual(2, n2, 'sem o indice a duplicata nao aconteceu — '
                                'entao o indice nao era o que segurava')


if __name__ == '__main__':
    unittest.main()
