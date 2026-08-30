#!/usr/bin/env python3
"""
Provas da PORTA DE COLETA — o navegador que se acha, e o que ele nunca faz.

A pergunta de cada teste é a de sempre: **isto falha fechado, ou devolve um
resultado errado com cara de certo?** Um descobridor de navegador erra de dois
jeitos, e os dois são silenciosos:

  1. diz "não achei" numa máquina que TEM Chrome — porque só olhou o PATH, e no
     Windows o Chrome não está no PATH;
  2. troca Chrome por Chromium sem avisar — e aí duas coletas da mesma página
     deixam de ser comparáveis sem que ninguém tenha mudado nada.

As máquinas destes testes são inventadas de propósito: nenhum deles pergunta ao
disco de quem está rodando, senão o resultado mudaria de máquina para máquina.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import navegador as nav                                        # noqa: E402


def maquina(*, path=(), arquivos=(), env=None):
    """Uma máquina de mentira: o que o `which` acha e o que existe em disco."""
    path, arquivos = set(path), set(arquivos)
    return {
        'env': env or {},
        'which': lambda n: ('/usr/bin/' + n) if n in path else None,
        'existe': lambda c: c in arquivos,
    }


class Descoberta(unittest.TestCase):

    def test_chrome_vence_chromium_quando_os_dois_existem(self):
        """A ordem não é estética: trocar o binário troca o User-Agent e o TLS."""
        r = nav.descobrir(**maquina(path=('google-chrome', 'chromium',
                                          'chromium-browser')))
        self.assertTrue(r['FOUND'])
        self.assertEqual(r['FAMILY'], nav.CHROME)
        self.assertTrue(r['EXECUTABLE'].endswith('google-chrome'))
        self.assertTrue(r['IS_PREFERRED'])

    def test_chromium_e_aceito_mas_sai_marcado(self):
        """Aceitar sem marcar é o que faz a substituição virar invisível."""
        r = nav.descobrir(**maquina(path=('chromium-browser',)))
        self.assertTrue(r['FOUND'])
        self.assertEqual(r['FAMILY'], nav.CHROMIUM)
        self.assertFalse(r['IS_PREFERRED'])

    def test_windows_sem_chrome_no_path_ainda_assim_acha(self):
        """O defeito 1: `which google-chrome` no Windows devolve nada, e há Chrome.

        Esta é a máquina real desta missão. Um descobridor que só olha o PATH
        conclui CHROME_INSTALLED=NO numa máquina com Chrome 151 instalado.
        """
        alvo = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        original = nav.platform.system
        nav.platform.system = lambda: 'Windows'
        try:
            r = nav.descobrir(**maquina(path=(), arquivos=(alvo,)))
        finally:
            nav.platform.system = original
        self.assertTrue(r['FOUND'])
        self.assertEqual(r['EXECUTABLE'], alvo)
        self.assertEqual(r['HOW'], 'INSTALL_PATH')

    def test_sem_nada_diz_que_nao_achou_e_por_que(self):
        r = nav.descobrir(**maquina())
        self.assertFalse(r['FOUND'])
        self.assertIsNone(r['EXECUTABLE'])
        self.assertIn('nenhum', r['WHY'])


class VariavelDeAmbiente(unittest.TestCase):

    def test_declarado_manda_mesmo_havendo_outro_no_path(self):
        alvo = '/opt/meu/chrome'
        r = nav.descobrir(**maquina(path=('google-chrome',), arquivos=(alvo,),
                                    env={'CHROME_EXECUTABLE': alvo}))
        self.assertEqual(r['EXECUTABLE'], alvo)
        self.assertEqual(r['HOW'], 'CHROME_EXECUTABLE')

    def test_declarado_e_ausente_falha_fechado(self):
        """NÃO cair no automático. Cair esconderia o erro de configuração.

        Se a variável aponta para o lugar errado e a descoberta segue em frente,
        a coleta roda com um binário que ninguém escolheu — e o relatório dirá
        que rodou com o que estava na variável.
        """
        r = nav.descobrir(**maquina(path=('google-chrome',),
                                    env={'CHROME_EXECUTABLE': '/nao/existe/chrome'}))
        self.assertFalse(r['FOUND'])
        self.assertIn('não existe', r['WHY'])


class Argumentos(unittest.TestCase):

    def test_no_sandbox_nunca_entra(self):
        """A regra 5 da missão, escrita como prova e não como intenção."""
        for kwargs in ({}, {'headless': True}, {'porta_devtools': 9222},
                       {'headless': True, 'porta_devtools': 9222}):
            with self.subTest(**kwargs):
                args = nav.argumentos('https://exemplo.invalid', **kwargs)
                self.assertNotIn('--no-sandbox', args)
                self.assertFalse(any('sandbox' in a for a in args))

    def test_perfil_fica_fora_do_repositorio(self):
        """Cookie e sessão não podem estar num caminho que o Git alcance."""
        args = nav.argumentos('https://exemplo.invalid')
        perfil = [a for a in args if a.startswith('--user-data-dir=')][0]
        caminho = os.path.abspath(perfil.split('=', 1)[1])
        self.assertFalse(caminho.startswith(os.path.abspath(ROOT) + os.sep))

    def test_headless_e_opcional_e_nao_e_o_padrao(self):
        """Nesta máquina headless levou 403 na ADAMA e janela não. O padrão é janela."""
        self.assertNotIn('--headless=new', nav.argumentos('https://exemplo.invalid'))
        self.assertIn('--headless=new',
                      nav.argumentos('https://exemplo.invalid', headless=True))

    def test_a_url_vai_por_ultimo(self):
        args = nav.argumentos('https://exemplo.invalid', porta_devtools=9222)
        self.assertEqual(args[-1], 'https://exemplo.invalid')


class Versao(unittest.TestCase):

    class _Resposta:
        def __init__(self, out='', err=''):
            self.stdout, self.stderr = out, err

    def test_le_da_saida_quando_o_binario_responde(self):
        r = nav.versao('/usr/bin/google-chrome',
                       rodar=lambda *a, **k: self._Resposta('Google Chrome 151.0.7922.174 \n'))
        self.assertEqual(r['VERSION'], '151.0.7922.174')

    def test_windows_nao_escreve_no_terminal_e_a_pasta_irma_salva(self):
        """O binário gráfico do Windows não devolve texto. A versão está no disco.

        Sem esta saída, a entrega diria CHROME_VERSION=None numa máquina onde a
        versão está escrita na pasta ao lado do executável.
        """
        r = nav.versao(os.path.join(ROOT, 'scripts', 'chrome.exe'),
                       rodar=lambda *a, **k: self._Resposta())
        self.assertIsNone(r['VERSION'])
        self.assertIn('não devolveu versão', r['WHY'])

    def test_binario_que_estoura_nao_derruba_a_descoberta(self):
        def explode(*a, **k):
            raise OSError('o sistema recusou')
        r = nav.versao('/nao/existe/chrome', rodar=explode)
        self.assertIsNone(r['VERSION'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
