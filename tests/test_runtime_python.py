#!/usr/bin/env python3
"""
Provas do RUNTIME — a cicatriz do falso "download concluído", virada teste.

Em 2026-08-30 um coletor terminou sem reclamar e a pasta ficou vazia. O que
falhou não foi a fonte francesa: foi o interpretador. E o relatório teria dito
"a França devolveu zero" se ninguém tivesse olhado a pasta.

Os três cenários que a missão exigiu, e um quarto que a máquina ensinou:

    python3 falso   -> sai sem executar          -> REPROVA
    Python real     -> executa e entrega         -> PASSA
    Python real     -> erra, entrega pela metade -> REPROVA (fail safe)
    Python real     -> executa e MENTE onde mora -> REPROVA até consertar a casa

Nenhum teste pergunta ao disco de quem roda. Os interpretadores aqui são de
mentira, e cada um falha de um jeito diferente de propósito — porque o modo de
falha que machuca não é o que grita, é o que sai com zero.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import runtime_python as rt                                     # noqa: E402


class _Resposta:
    def __init__(self, returncode=0, stdout='', stderr=''):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def _relato(**extra):
    base = {'MARCADOR': rt.MARCADOR, 'EXECUTABLE': '/falso/python',
            'VERSION': '3.12.10', 'PREFIX': '/casa', 'STDLIB_FILE': '/casa/Lib/os.py',
            'STDLIB_FILE_EXISTS': True, 'ARCH': '64bit', 'LIB_DIRS': ['/casa/Lib']}
    base.update(extra)
    return json.dumps(base)


# ── os interpretadores de mentira ────────────────────────────────────────────

def alias_da_loja(argv, **kw):
    """Existe no PATH, não executa nada, e sai com código de erro."""
    return _Resposta(9009, '', 'Python nao foi encontrado; abra a Loja...')


def sai_zero_sem_trabalhar(argv, **kw):
    """O PIOR: diz que deu tudo certo e não fez nada. A cicatriz em pessoa."""
    return _Resposta(0, '', '')


def python_de_verdade(argv, **kw):
    """Escreve o segredo sorteado e conta quem é. É o que se espera."""
    alvo, nonce = argv[3], argv[4]
    with open(alvo, 'w', encoding='utf-8') as fh:
        fh.write(nonce)
    return _Resposta(0, _relato() + '\n', '')


def entrega_pela_metade(argv, **kw):
    """Escreve, mas escreve outra coisa. Arquivo existe e não vale nada."""
    alvo = argv[3]
    with open(alvo, 'w', encoding='utf-8') as fh:
        fh.write('conteudo de outra execucao')
    return _Resposta(1, '', 'estourou no meio')


class casa_instavel:
    """Executa, e diz que sua biblioteca está num lugar que não existe.

    Na segunda chamada — a que leva PYTHONHOME — passa a dizer a verdade. É o
    comportamento medido do `py -3` desta máquina.
    """

    def __init__(self):
        self.chamadas = []

    def __call__(self, argv, **kw):
        ambiente = kw.get('env') or {}
        alvo, nonce = argv[3], argv[4]
        with open(alvo, 'w', encoding='utf-8') as fh:
            fh.write(nonce)
        self.chamadas.append(ambiente.get('PYTHONHOME'))
        if ambiente.get('PYTHONHOME') == '/casa':
            return _Resposta(0, _relato(PREFIX='/casa') + '\n', '')
        return _Resposta(0, _relato(STDLIB_FILE_EXISTS=False,
                                    PREFIX='/onde/eu/estava',
                                    STDLIB_FILE='/onde/eu/estava/Lib/os.py') + '\n', '')


class Sonda(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='sintonia-teste-')
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def sondar(self, runner, **kw):
        return rt.sondar('/falso/python', rodar=runner, pasta_tmp=self.tmp, **kw)

    def test_exit_zero_sem_trabalho_reprova(self):
        """O cenário exato do falso "download concluído".

        Este é o único teste que precisava existir em 30/08 e não existia.
        """
        r = self.sondar(sai_zero_sem_trabalhar)
        self.assertEqual(r['STATE'], rt.TRABALHO_NAO_FEITO)
        self.assertEqual(r['EXIT_CODE'], 0)
        self.assertFalse(r['WORK_DONE'])
        self.assertEqual(r['OUTPUT_BYTES'], 0)

    def test_python_real_passa(self):
        r = self.sondar(python_de_verdade)
        self.assertEqual(r['STATE'], rt.VALIDO)
        self.assertTrue(r['WORK_DONE'])
        self.assertGreater(r['OUTPUT_BYTES'], 0)
        self.assertEqual(r['VERSION'], '3.12.10')

    def test_erro_com_entrega_parcial_reprova(self):
        """Arquivo existe, bytes existem, conteúdo é de outra execução."""
        r = self.sondar(entrega_pela_metade)
        self.assertEqual(r['STATE'], rt.TRABALHO_NAO_FEITO)
        self.assertIn('vazio ou com conteúdo diferente', r['WHY'])

    def test_alias_da_loja_reprova_e_sai_marcado(self):
        r = self.sondar(alias_da_loja)
        self.assertEqual(r['STATE'], rt.ALIAS_QUEBRADO)
        self.assertFalse(r['WORK_DONE'])

    def test_casa_instavel_reprova_antes_do_conserto(self):
        r = self.sondar(casa_instavel())
        self.assertEqual(r['STATE'], rt.CASA_INSTAVEL)
        self.assertIn('não existe', r['WHY'])

    def test_o_arquivo_de_prova_some_no_fim(self):
        """Deixar lixo faria a próxima execução herdar a prova da anterior."""
        antes = set(os.listdir(self.tmp))
        self.sondar(python_de_verdade)
        self.assertEqual(set(os.listdir(self.tmp)), antes)

    def test_arquivo_deixado_por_execucao_anterior_nao_passa(self):
        """O segredo é sorteado agora. Prova velha prova o passado."""
        def escreve_valor_fixo(argv, **kw):
            with open(argv[3], 'w', encoding='utf-8') as fh:
                fh.write('valor-de-ontem')
            return _Resposta(0, _relato() + '\n', '')
        r = self.sondar(escreve_valor_fixo)
        self.assertEqual(r['STATE'], rt.TRABALHO_NAO_FEITO)

    def test_interpretador_que_nem_executa_nao_derruba_a_descoberta(self):
        def recusa(*a, **k):
            raise OSError('acesso negado')
        r = self.sondar(recusa)
        self.assertEqual(r['STATE'], rt.NAO_EXECUTOU)


class Descoberta(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='sintonia-teste-')
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_pula_o_que_existe_e_nao_executa(self):
        """COMMAND_EXISTS != VALID_INTERPRETER, escrito como prova.

        A máquina tem `python3` no PATH, e ele é o alias quebrado. Um descobridor
        que aceita o primeiro caminho ENCONTRADO escolhe justamente o que não
        funciona — e escolhe primeiro, porque o quebrado é quem está no PATH.
        """
        quebrados = {'/apps/python3', '/apps/python'}

        def rodar(argv, **kw):
            if argv[0] in quebrados:
                return sai_zero_sem_trabalhar(argv, **kw)
            return python_de_verdade(argv, **kw)

        r = rt.descobrir(env={}, which=lambda n: {'python3': '/apps/python3',
                                                  'python': '/apps/python'}.get(n),
                         existe=lambda c: True, rodar=rodar, pasta_tmp=self.tmp,
                         sistema='Linux')
        self.assertEqual(r['STATE'], rt.VALIDO)
        self.assertEqual(r['EXECUTABLE'], '/falso/python')
        self.assertEqual(r['HOW'], 'INSTALL_PATH')
        # os dois do PATH foram TENTADOS e recusados, não ignorados
        self.assertEqual([x['EXECUTABLE'] for x in r['REJECTED']],
                         ['/apps/python3', '/apps/python'])
        self.assertTrue(all(x['STATE'] == rt.TRABALHO_NAO_FEITO
                            for x in r['REJECTED']))

    def test_quando_nenhum_candidato_executa_falha_fechado(self):
        """Sem Python válido não há coleta. Escolher um "mais ou menos" é pior."""
        r = rt.descobrir(env={}, which=lambda n: '/apps/' + n,
                         existe=lambda c: True, rodar=sai_zero_sem_trabalhar,
                         pasta_tmp=self.tmp, sistema='Linux')
        self.assertEqual(r['STATE'], rt.AUSENTE)
        self.assertTrue(all(x['STATE'] != rt.VALIDO for x in r['REJECTED']))
        self.assertIn('COMMAND_EXISTS', r['WHY'])

    def test_variavel_declarada_e_ausente_falha_fechado(self):
        r = rt.descobrir(env={'SINTONIA_PYTHON': '/nao/existe'},
                         which=lambda n: '/apps/' + n, existe=lambda c: False,
                         rodar=python_de_verdade, pasta_tmp=self.tmp, sistema='Linux')
        self.assertEqual(r['STATE'], rt.AUSENTE)
        self.assertEqual(r['REJECTED'][0]['STATE'], rt.AUSENTE)

    def test_casa_instavel_e_consertada_com_o_que_o_proprio_python_contou(self):
        """O PYTHONHOME não é chutado: sai do `sys.path` que ele mesmo devolveu."""
        fake = casa_instavel()
        r = rt.descobrir(env={}, which=lambda n: '/apps/' + n,
                         existe=lambda c: True, rodar=fake, pasta_tmp=self.tmp,
                         sistema='Linux')
        self.assertEqual(r['STATE'], rt.VALIDO)
        self.assertEqual(r['ENV_EXTRA']['PYTHONHOME'], '/casa')
        self.assertEqual(r['HOME_DERIVED_FROM'], '/casa/Lib')
        self.assertIn(None, fake.chamadas)          # tentou sem, antes de tentar com


class Portao(unittest.TestCase):

    def test_fecha_so_com_trabalho_feito(self):
        p = rt.portao({'STATE': rt.VALIDO, 'WORK_DONE': True, 'OUTPUT_BYTES': 32,
                       'STDLIB_FILE_EXISTS': True, 'IS_WINDOWSAPPS_ALIAS': False,
                       'EXECUTABLE': '/real/python', 'VERSION': '3.12.10'})
        self.assertEqual(p['PYTHON_RUNTIME_GATE'], 'CLOSED')

    def test_nao_fecha_com_presenca_sem_trabalho(self):
        p = rt.portao({'STATE': rt.VALIDO, 'WORK_DONE': False, 'OUTPUT_BYTES': 0,
                       'STDLIB_FILE_EXISTS': True, 'IS_WINDOWSAPPS_ALIAS': False})
        self.assertEqual(p['PYTHON_RUNTIME_GATE'], 'OPEN')
        self.assertIn('WORK_EXECUTED', p['MISSING'])

    def test_nao_fecha_com_alias_da_loja(self):
        p = rt.portao({'STATE': rt.VALIDO, 'WORK_DONE': True, 'OUTPUT_BYTES': 32,
                       'STDLIB_FILE_EXISTS': True, 'IS_WINDOWSAPPS_ALIAS': True})
        self.assertIn('NOT_WINDOWSAPPS_ALIAS', p['MISSING'])


class PosCondicao(unittest.TestCase):
    """EMPTY_OUTPUT != ZERO_RESULTS — a lei que separa 'não veio' de 'veio zero'."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='sintonia-saida-')
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def arquivo(self, nome, conteudo='dado'):
        caminho = os.path.join(self.tmp, nome)
        with open(caminho, 'w', encoding='utf-8') as fh:
            fh.write(conteudo)
        return caminho

    def test_pasta_vazia_nunca_vira_zero_resultados(self):
        """Exatamente o que aconteceu com o E-Phy. Nunca mais em silêncio."""
        r = rt.conferir_saida(caminhos=[os.path.join(self.tmp, 'ephy.zip')],
                              exit_code=0)
        self.assertEqual(r['STATE'], rt.SAIDA_AUSENTE)
        self.assertIn('EMPTY_OUTPUT', r['WHY'])

    def test_exit_zero_nao_basta(self):
        r = rt.conferir_saida(caminhos=[os.path.join(self.tmp, 'nada.csv')],
                              exit_code=0, contagem=0)
        self.assertNotEqual(r['STATE'], rt.SAIDA_OK)

    def test_saida_presente_com_registros_passa(self):
        r = rt.conferir_saida(caminhos=[self.arquivo('ephy.csv')], exit_code=0,
                              contagem=15140)
        self.assertEqual(r['STATE'], rt.SAIDA_OK)
        self.assertGreater(r['OUTPUT_BYTES'], 0)

    def test_zero_medido_da_fonte_e_um_fato_e_passa(self):
        """Zero pode ser verdade — mas alguém tem de ter LIDO esse zero."""
        r = rt.conferir_saida(caminhos=[self.arquivo('busca.json', '[]')],
                              exit_code=0, contagem=0, fonte_respondeu_zero=True)
        self.assertEqual(r['STATE'], rt.ZERO_MEDIDO)

    def test_arquivo_de_zero_byte_reprova(self):
        r = rt.conferir_saida(caminhos=[self.arquivo('vazio.csv', '')], exit_code=0)
        self.assertEqual(r['STATE'], rt.SAIDA_VAZIA)

    def test_saida_parcial_reprova_e_diz_qual_faltou(self):
        presente = self.arquivo('a.csv')
        ausente = os.path.join(self.tmp, 'b.csv')
        r = rt.conferir_saida(caminhos=[presente, ausente], exit_code=0, contagem=5)
        self.assertEqual(r['STATE'], rt.SAIDA_PARCIAL)
        self.assertEqual(r['OUTPUTS_MISSING'], [ausente])

    def test_exit_diferente_de_zero_com_saida_boa_ainda_reprova(self):
        r = rt.conferir_saida(caminhos=[self.arquivo('a.csv')], exit_code=2,
                              contagem=10)
        self.assertEqual(r['STATE'], rt.EXECUCAO_INVALIDA)

    def test_sem_saida_declarada_nao_ha_o_que_conferir(self):
        r = rt.conferir_saida(caminhos=[], exit_code=0)
        self.assertEqual(r['STATE'], rt.SAIDA_AUSENTE)


class AmbienteSeguro(unittest.TestCase):

    def test_o_filho_recebe_utf8(self):
        """Imprimir "≠" no console cp1252 desta máquina levanta UnicodeEncodeError.

        Um coletor morreria justamente na hora de EXPLICAR por que recusou algo.
        """
        vistos = {}

        def rodar(argv, **kw):
            vistos.update(kw.get('env') or {})
            return python_de_verdade(argv, **kw)

        tmp = tempfile.mkdtemp(prefix='sintonia-env-')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        rt.sondar('/falso/python', rodar=rodar, pasta_tmp=tmp)
        self.assertEqual(vistos.get('PYTHONIOENCODING'), 'utf-8')

    def test_pythonhome_herdado_nao_contamina_a_medicao(self):
        """Medir com o PYTHONHOME de quem chamou mediria a casa errada."""
        vistos = {}

        def rodar(argv, **kw):
            vistos['home'] = (kw.get('env') or {}).get('PYTHONHOME', '<ausente>')
            return python_de_verdade(argv, **kw)

        tmp = tempfile.mkdtemp(prefix='sintonia-env-')
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        os.environ['PYTHONHOME'] = '/casa/de/quem/chamou'
        self.addCleanup(os.environ.pop, 'PYTHONHOME', None)
        rt.sondar('/falso/python', rodar=rodar, pasta_tmp=tmp)
        self.assertEqual(vistos['home'], '<ausente>')


if __name__ == '__main__':
    unittest.main(verbosity=2)
