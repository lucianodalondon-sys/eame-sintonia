"""As cicatrizes do Brasil continuam transferidas, e PROVED continua sendo PROVED.

O risco desta matriz nao e errar um status: e narrar. Uma linha dizendo
PROVED sem testemunha executavel vale menos que uma linha honesta dizendo
ABSENT, porque a primeira desliga a vigilancia.
"""
import json
import os
import subprocess
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))
MATRIZ = os.path.join(RAIZ, 'data', 'samples', 'BRAZIL-LESSONS-TRANSFER-EAME.json')
VALIDO = ('PROVED', 'PARTIAL', 'ABSENT', 'NOT_MEASURED')


def carrega():
    with open(MATRIZ, encoding='utf-8') as f:
        return json.load(f)


class TestAMatriz(unittest.TestCase):

    def setUp(self):
        self.d = carrega()

    def test_toda_cicatriz_aponta_o_arquivo_brasileiro(self):
        for c in self.d['CICATRIZES']:
            self.assertTrue(c['ONDE_NO_BRASIL'], c['ID'])
            self.assertTrue(c['WHY_IT_EXISTS'], c['ID'])

    def test_todo_status_e_um_dos_quatro(self):
        for c in self.d['CICATRIZES']:
            self.assertIn(c['EAME_STATUS'], VALIDO, c['ID'])

    def test_o_placar_bate_com_as_linhas(self):
        from collections import Counter
        c = Counter(x['EAME_STATUS'] for x in self.d['CICATRIZES'])
        for k in VALIDO:
            self.assertEqual(c.get(k, 0), self.d['PLACAR'][k], k)
        self.assertEqual(len(self.d['CICATRIZES']), self.d['CICATRIZES_IDENTIFICADAS'])

    def test_todo_proved_tem_testemunha_encontrada(self):
        for c in self.d['CICATRIZES']:
            if c['EAME_STATUS'] == 'PROVED':
                self.assertTrue(c['PROVA_ENCONTRADA'], c['ID'])
                self.assertFalse(c['PROVA_NAO_ENCONTRADA'], c['ID'])

    def test_todo_partial_nomeia_a_lacuna_e_a_acao(self):
        for c in self.d['CICATRIZES']:
            if c['EAME_STATUS'] in ('PARTIAL', 'ABSENT', 'NOT_MEASURED'):
                self.assertTrue(c['GAP'], c['ID'])
                self.assertTrue(c['MINIMAL_ACTION'], c['ID'])

    def test_nenhum_numero_brasileiro_foi_copiado_como_dado_do_eame(self):
        """Citar o achado brasileiro e legitimo. Importar o numero nao e."""
        for c in self.d['CICATRIZES']:
            for campo in ('OWNER', 'MINIMAL_ACTION'):
                v = c.get(campo) or ''
                self.assertNotIn('7.868', v, c['ID'])
                self.assertNotIn('4.548', v, c['ID'])
                self.assertNotIn('299', v, c['ID'])

    def test_as_cinco_familias_estao_cobertas(self):
        for f in ('LOCALIZACAO', 'RELEVANCIA', 'PROVENIENCIA', 'IDENTIDADE',
                  'UNIDADE_ANALITICA', 'RESILIENCIA', 'TEMPO', 'AUSENCIA'):
            self.assertIn(f, self.d['POR_FAMILIA'], f)


class TestAVerificacaoTemDentes(unittest.TestCase):
    """Um verificador que aprova qualquer testemunha nao verifica nada."""

    def test_uma_testemunha_inexistente_rebaixa_a_linha(self):
        import cicatrizes_brasil as C
        original = list(C.CICATRIZES)
        try:
            C.CICATRIZES = original + [{
                'ID': 'MUT-01', 'FAMILIA': 'MUTACAO',
                'BRAZIL_LESSON': 'mutação', 'ONDE_NO_BRASIL': 'nenhum',
                'WHY_IT_EXISTS': 'provar que o verificador reprova',
                'EAME_APPLICABLE': 'YES', 'EAME_STATUS': 'PROVED',
                'OWNER': 'ninguém',
                # A testemunha e MONTADA em tempo de execucao. Escreve-la
                # literal aqui a faria existir — dentro do proprio corpus que
                # o verificador varre, e o teste passaria por engano. Mesma
                # armadilha da linha de cima, em outra forma.
                'EXECUTABLE_PROOF': ['_'.join(['TESTEMUNHA', 'QUE', 'NAO',
                                               'EXISTE', 'EM', 'PARTE', 'NENHUMA'])],
                'GAP': None, 'MINIMAL_ACTION': None}]
            d = C.monta()
        finally:
            C.CICATRIZES = original
        self.assertIn('MUT-01', d['REBAIXADAS_PELA_VERIFICACAO'])
        m = [x for x in d['CICATRIZES'] if x['ID'] == 'MUT-01'][0]
        self.assertEqual('NOT_MEASURED', m['EAME_STATUS'])
        self.assertIn('REBAIXADA_POR_ESTE_SCRIPT', m)

    def test_o_artefato_versionado_bate_com_a_medicao_de_agora(self):
        import cicatrizes_brasil as C
        agora = C.monta()
        gravado = carrega()
        self.assertEqual(gravado['PLACAR'], agora['PLACAR'])
        self.assertEqual([x['ID'] for x in gravado['CICATRIZES']],
                         [x['ID'] for x in agora['CICATRIZES']])
        for a, b in zip(gravado['CICATRIZES'], agora['CICATRIZES']):
            self.assertEqual(a['EAME_STATUS'], b['EAME_STATUS'], a['ID'])


class TestAsTravasNoSchema(unittest.TestCase):
    """A cicatriz brasileira: a regra existia na prosa e nao no campo."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(RAIZ, 'supabase', 'migrations',
                               '015_cicatrizes_do_brasil.sql'), encoding='utf-8') as f:
            cls.sql = f.read()

    def test_o_lugar_da_fonte_nao_sustenta_o_lugar_do_fato(self):
        self.assertIn('local_da_fonte_nao_sustenta_local_do_fato', self.sql)
        self.assertIn("fact_geografia_origem in ('ESCRITO','CITADO')", self.sql)

    def test_o_lugar_do_fato_exige_origem_e_evidencia(self):
        self.assertIn('local_do_fato_diz_como_se_soube', self.sql)

    def test_os_estados_de_tentativa_separam_mundo_instalacao_e_nos(self):
        for e in ('RESPONDEU_SEM_O_CAMPO', 'LOGIN_WALL', 'THROTTLED', 'NOT_FOUND',
                  'PARSER_FAILURE', 'SEM_CHECKPOINT_NAO_GASTEI', 'NAO_TESTADO'):
            self.assertIn(e, self.sql, e)

    def test_relevancia_nao_tem_score(self):
        """Procura COLUNA chamada score, nao a palavra.

        A primeira versao lia o arquivo inteiro em minusculas e reprovava na
        frase "-- sem score. a relevancia ao caso e derivada na pergunta" —
        o comentario que ENUNCIA a proibicao. Sexta vez neste projeto.
        """
        import re as _re
        colunas = _re.findall(r'^\s+([a-z_]+)\s+(?:text|integer|numeric|boolean|bigint)',
                              self.sql, _re.M)
        for c in colunas:
            for p in ('score', 'peso', 'nota', 'rank', 'pontua'):
                self.assertNotIn(p, c, 'coluna %s parece um score' % c)

    def test_o_014_reservado_foi_OCUPADO_pelo_catalogo(self):
        """A reserva cumpriu a funcao dela.

        Este teste afirmava que o 014 estava VAGO. Ficou vago tres rodadas,
        de proposito, esperando a migration do catalogo da branch paralela —
        e a missao de importacao controlada a trouxe, renumerada de 010 para
        014. Um buraco declarado que e ocupado por quem estava declarado nao
        e um buraco preenchido por acaso: e a reserva funcionando.

        O que continua valendo: o 014 e do catalogo e de mais nada.
        """
        mig = sorted(f for f in os.listdir(os.path.join(RAIZ, 'supabase', 'migrations'))
                     if f.endswith('.sql'))
        m014 = [f for f in mig if f.startswith('014')]
        self.assertEqual(['014_catalogo_publico_fabricante.sql'], m014)
        self.assertIn('015_cicatrizes_do_brasil.sql', mig)
        # A 015 continua contando a historia da reserva, e a 014 diz que a ocupou.
        self.assertIn('O NÚMERO 014 ESTÁ RESERVADO', self.sql)
        with open(os.path.join(RAIZ, 'supabase', 'migrations', m014[0]),
                  encoding='utf-8') as f:
            self.assertIn('RENUMERADA', f.read())


class TestOBrasilFoiLidoENaoLembrado(unittest.TestCase):

    def test_o_repositorio_brasileiro_esta_acessivel(self):
        """Se ele sumir, a matriz vira memoria — e memoria nao e fonte."""
        r = subprocess.run(['git', '-C', '/home/user/portal-sintonia', 'rev-parse', 'HEAD'],
                           capture_output=True, text=True)
        if r.returncode != 0:
            self.skipTest('portal-sintonia nao esta anexado nesta sessao')
        self.assertRegex(r.stdout.strip(), r'^[0-9a-f]{40}$')

    def test_as_licoes_citam_arquivos_que_existem_la(self):
        if not os.path.isdir('/home/user/portal-sintonia'):
            self.skipTest('portal-sintonia nao esta anexado nesta sessao')
        for c in carrega()['CICATRIZES']:
            onde = c['ONDE_NO_BRASIL']
            if onde.endswith('.md'):
                with self.subTest(cicatriz=c['ID']):
                    self.assertTrue(
                        os.path.exists(os.path.join('/home/user/portal-sintonia', onde)),
                        '%s aponta %s e o arquivo nao existe la' % (c['ID'], onde))


if __name__ == '__main__':
    unittest.main()
