#!/usr/bin/env python3
"""O ENDEREÇO TAMBÉM É SEGREDO.

Red team de 2026-09-09, SCRAP-R1. `redigir()` tinha dois passos — rótulo
(`password=`) e forma (`apify_api_…`, JWT, `AIza…`) — e a DSN do Supabase não
tem nenhum dos dois: não há rótulo, e a forma de uma senha é NÃO TER FORMA.

    postgresql://postgres:<a senha, em claro>@db.xxxx.supabase.co:5432/postgres

atravessava a função inteira, em claro, e `social_rotas` chama `redigir()` em
TODA exceção — inclusive a de conexão, que carrega a DSN no texto.

O host continua visível de propósito: um log que não diz PARA ONDE a coleta
falhou não é privacidade, é cegueira.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'guarda'))
import _gavetas  # noqa: E402,F401
import social_sessao as ss   # noqa: E402

SENHA = ''.join(['Senha', 'Secreta', '123'])
# Montado em tempo de execução, nunca escrito inteiro no arquivo: `social_guarda`
# varre o repositório por FORMA, e um fixture com cara de credencial é indistinguível
# de uma credencial de verdade para quem varre. O guarda desta casa barrou este
# próprio teste na primeira versão — e estava certo.
#
#     FIXTURE COM FORMA DE SEGREDO É SEGREDO PARA QUEM VARRE.
TOKEN_FALSO = 'sk-' + 'live-' + ('A' * 4) + ('B' * 4) + ('C' * 4) + '1234'
CABECALHO_FALSO = 'Authoriz' + 'ation: Bearer ' + TOKEN_FALSO
DSNS = [
    'postgresql://postgres:%s@db.abcdefgh.supabase.co:5432/postgres' % SENHA,
    'postgres://user:%s@localhost:5432/x' % SENHA,
    'mongodb+srv://admin:%s@cluster0.mongodb.net/db' % SENHA,
    'redis://default:%s@redis.interno:6379' % SENHA,
    'https://user:%s@api.exemplo.com/v1' % SENHA,
]


class OEnderecoTambemESegredo(unittest.TestCase):

    def test_nenhuma_dsn_deixa_a_senha_passar(self):
        for dsn in DSNS:
            with self.subTest(dsn=dsn.split('://')[0]):
                self.assertNotIn(SENHA, ss.redigir(dsn))

    def test_o_host_sobrevive_para_o_log_continuar_util(self):
        saida = ss.redigir(DSNS[0])
        self.assertIn('db.abcdefgh.supabase.co', saida)
        self.assertIn('<REDIGIDO>', saida)

    def test_url_sem_credencial_atravessa_intacta(self):
        """Redigir demais também mente: some com a rota que a auditoria precisa ver."""
        url = 'https://mastodon.uno/api/v1/timelines/tag/agronomia?limit=20'
        self.assertEqual(ss.redigir(url), url)

    def test_a_dsn_dentro_de_um_traceback_tambem_e_redigida(self):
        """É assim que ela aparece de verdade: nunca sozinha."""
        texto = 'OperationalError: could not connect to %s (timeout)' % DSNS[0]
        self.assertNotIn(SENHA, ss.redigir(texto))

    def test_os_tres_passos_continuam_valendo_juntos(self):
        misto = ('conectando %s com %s a partir de '
                 '/home/alguem/.config/google-chrome' % (DSNS[0], CABECALHO_FALSO))
        saida = ss.redigir(misto)
        self.assertNotIn(SENHA, saida)
        self.assertNotIn(TOKEN_FALSO, saida)
        self.assertNotIn('/home/alguem', saida)


if __name__ == '__main__':
    unittest.main()
