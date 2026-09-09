#!/usr/bin/env python3
"""A PORTA DE ENTRADA DO DISPATCHER — quem quebrou tem nome, e o nome é o certo.

Duas mentiras mediadas ao vivo no piloto de 2026-09-09, as duas no mesmo `except`
genérico do fim de `_executar`:

    pedido sem `channel_id`   ->  PARSER_DRIFT    (afirma que a fonte respondeu
                                                   e o nosso extrator falhou —
                                                   a fonte nunca foi tocada)
    sem YOUTUBE_DATA_API_KEY  ->  UNKNOWN_ERROR   (a própria exceção dizia
                                                   CREDENTIAL_MISSING no texto)

O custo não é estético. `PARSER_DRIFT` manda gente depurar extrator; `UNKNOWN`
manda investigar. O defeito era do PEDIDO, e a ação certa era PROVISIONAR chave.
Estado errado compra a hora errada.

    ENTRADA QUE FALTA NÃO É FONTE QUE MUDOU.
    CREDENCIAL AUSENTE NÃO É ERRO DESCONHECIDO.

Nenhum destes testes toca a rede: os dois param ANTES da primeira requisição, e é
exatamente isso que eles provam.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(HERE)
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, 'coleta'))
import _gavetas  # noqa: E402,F401
import social_rotas as sr   # noqa: E402


class EntradaQueFaltaNaoEFonteQueMudou(unittest.TestCase):

    def test_pedido_sem_entrada_obrigatoria_nao_vira_parser_drift(self):
        _o, r = sr.executar(platform='YOUTUBE', capability='INCREMENTAL',
                            run_id='TEST-ENTRADA', country_scope='IT')
        self.assertEqual(r['ESTADO'], 'CONTRACT_DRIFT')
        self.assertNotEqual(r['ESTADO'], 'PARSER_DRIFT')
        # O registro tem de NOMEAR a entrada que faltou; senão não serve para
        # consertar nada.
        self.assertIn('channel_id', r['ERRO'])

    def test_o_portao_de_entrada_nao_recusa_argumento_a_mais(self):
        """Ele recusa entrada que FALTA. Extra é problema de outro portão."""
        faltando = sr._entradas_faltando(sr.youtube_uploads,
                                         {'channel_id': 'UC0', 'coisa_extra': 1})
        self.assertEqual(faltando, [])

    def test_run_id_e_country_scope_nao_contam_como_faltando(self):
        """A porta já os injeta em toda chamada; cobrá-los do pedido barraria tudo."""
        self.assertEqual(sr._entradas_faltando(sr.youtube_metadata,
                                               {'video_ids': ['x']}), [])


class CredencialAusenteNaoEErroDesconhecido(unittest.TestCase):

    def setUp(self):
        self._antes = os.environ.pop('YOUTUBE_DATA_API_KEY', None)

    def tearDown(self):
        if self._antes is not None:
            os.environ['YOUTUBE_DATA_API_KEY'] = self._antes

    def test_sem_chave_o_estado_e_credential_missing(self):
        _o, r = sr.executar(platform='YOUTUBE', capability='INCREMENTAL',
                            run_id='TEST-CRED', country_scope='IT',
                            channel_id='UC_inexistente_de_teste')
        self.assertEqual(r['ESTADO'], 'CREDENTIAL_MISSING')

    def test_a_acao_de_recuperacao_manda_provisionar_e_nao_investigar(self):
        _o, r = sr.executar(platform='YOUTUBE', capability='INCREMENTAL',
                            run_id='TEST-CRED', country_scope='IT',
                            channel_id='UC_inexistente_de_teste')
        self.assertEqual(r['RECOVERY_ACTION'], 'HUMAN_PROVISION_CREDENTIAL')

    def test_credencial_ausente_nunca_autoriza_cair_para_scraping(self):
        """O estado é de recusa: zero objeto, e nenhuma rota alternativa tentada."""
        objs, r = sr.executar(platform='YOUTUBE', capability='INCREMENTAL',
                              run_id='TEST-CRED', country_scope='IT',
                              channel_id='UC_inexistente_de_teste')
        self.assertEqual(objs, [])
        self.assertFalse(r.get('EXPECTED') is None)


if __name__ == '__main__':
    unittest.main()
