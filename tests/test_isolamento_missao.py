# -*- coding: utf-8 -*-
"""O namespace por missão não pode ser comprado com estado global.

Este ficheiro existe por um defeito medido, não por simetria. `creator_coleta.py`
e `creator_corpus_coleta.py` redirecionavam `pv.MANIFESTO`, `coletor.RAW_DIR` e
`coletor._curl` no CORPO DO MÓDULO. Importar qualquer um deles mudava, para o
resto do processo, qual manifesto a casa inteira lia — e quem lesse a seguir não
tinha como saber. A medição que o apanhou: `pv.carregar()` devolvia 22 execuções
antes de `import creator_coleta` e 7 depois.

A lei que estes testes escrevem:

    MISSION_LOCAL_MANIFEST != GLOBAL_MANIFEST_MUTATION

O namespace por missão continua — o que passou a ser verdade é que ele tem
ALCANCE. Fora do `with`, a casa; dentro, a missão; e o `finally` devolve mesmo
quando a fase rebenta.
"""
import importlib.util
import os
import runpy
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import coletor          # noqa: E402
import proveniencia as pv   # noqa: E402

MISSOES = (
    ('creator_coleta', os.path.join(
        'data', 'samples', 'CREATOR-MAP-EAME', 'RUN-MANIFEST-CREATORS.json')),
    ('creator_corpus_coleta', os.path.join(
        'data', 'samples', 'CREATOR-CONTENT-CORPUS-EAME', 'RUN-MANIFEST-CORPUS.json')),
)


def _carrega(nome, apelido):
    """Carrega o módulo por caminho, como o runner faz — sem cache de import."""
    spec = importlib.util.spec_from_file_location(
        apelido, os.path.join(ROOT, 'scripts', nome + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestImportNaoSequestraOGlobal(unittest.TestCase):
    """1 — importar não pode mudar estado global. É o defeito original."""

    def setUp(self):
        self.antes = (pv.MANIFESTO, coletor.RAW_DIR, coletor._curl)

    def tearDown(self):
        pv.MANIFESTO, coletor.RAW_DIR, coletor._curl = self.antes

    def test_importar_os_dois_modulos_nao_move_pv_manifesto(self):
        for i, (nome, _) in enumerate(MISSOES):
            _carrega(nome, '_iso_imp_%d' % i)
            self.assertEqual(
                self.antes[0], pv.MANIFESTO,
                'importar %s moveu pv.MANIFESTO — era exatamente este o defeito' % nome)

    def test_importar_nao_move_raw_dir_nem_a_porta_do_coletor(self):
        for i, (nome, _) in enumerate(MISSOES):
            _carrega(nome, '_iso_imp2_%d' % i)
            self.assertEqual(self.antes[1], coletor.RAW_DIR,
                             'importar %s moveu coletor.RAW_DIR' % nome)
            self.assertIs(self.antes[2], coletor._curl,
                          'importar %s substituiu coletor._curl' % nome)

    def test_o_global_continua_a_ler_o_manifesto_da_casa(self):
        for i, (nome, _) in enumerate(MISSOES):
            _carrega(nome, '_iso_imp3_%d' % i)
        self.assertTrue(pv.MANIFESTO.endswith(os.path.join('samples', 'RUN-MANIFEST.json')),
                        'o manifesto global deixou de ser o da casa: %s' % pv.MANIFESTO)


class TestEscopoAplicaEDevolve(unittest.TestCase):
    """2, 3 e 4 — dentro do escopo é a missão; ao sair é a casa; em exceção também."""

    def setUp(self):
        self.antes = (pv.MANIFESTO, coletor.RAW_DIR, coletor._curl)

    def tearDown(self):
        pv.MANIFESTO, coletor.RAW_DIR, coletor._curl = self.antes

    def test_dentro_do_escopo_a_missao_ve_o_seu_manifesto(self):
        for i, (nome, esperado) in enumerate(MISSOES):
            mod = _carrega(nome, '_iso_esc_%d' % i)
            with mod.escopo_da_missao():
                self.assertTrue(
                    pv.MANIFESTO.endswith(esperado),
                    '%s não apontou para o seu manifesto: %s' % (nome, pv.MANIFESTO))
                self.assertEqual(mod.RAW_DIR_DA_MISSAO, coletor.RAW_DIR)
                # A porta de rede PAGA também é da missão. Sem esta linha, apagar
                # `coletor._curl = _http` de dentro do escopo passava despercebido:
                # a fase corria no namespace certo com o transporte da casa.
                self.assertIs(mod._http, coletor._curl,
                              '%s não trocou a porta de rede dentro do escopo' % nome)

    def test_ao_sair_do_escopo_o_valor_anterior_volta(self):
        for i, (nome, _) in enumerate(MISSOES):
            mod = _carrega(nome, '_iso_sai_%d' % i)
            with mod.escopo_da_missao():
                pass
            self.assertEqual(self.antes[0], pv.MANIFESTO)
            self.assertEqual(self.antes[1], coletor.RAW_DIR)
            self.assertIs(self.antes[2], coletor._curl)

    def test_em_excecao_o_valor_anterior_tambem_volta(self):
        for i, (nome, _) in enumerate(MISSOES):
            mod = _carrega(nome, '_iso_exc_%d' % i)
            with self.assertRaises(RuntimeError):
                with mod.escopo_da_missao():
                    raise RuntimeError('a fase rebentou a meio, que é o caso que interessa')
            self.assertEqual(self.antes[0], pv.MANIFESTO,
                             '%s não devolveu pv.MANIFESTO depois da exceção' % nome)
            self.assertEqual(self.antes[1], coletor.RAW_DIR)
            self.assertIs(self.antes[2], coletor._curl)


class TestAsDuasMissoesNaoSeContaminam(unittest.TestCase):
    """5 — Creator Map e Creator Content Corpus são donos diferentes."""

    def setUp(self):
        self.antes = (pv.MANIFESTO, coletor.RAW_DIR, coletor._curl)

    def tearDown(self):
        pv.MANIFESTO, coletor.RAW_DIR, coletor._curl = self.antes

    def test_escopos_aninhados_nao_se_misturam(self):
        mapa = _carrega('creator_coleta', '_iso_a')
        corpus = _carrega('creator_corpus_coleta', '_iso_b')
        with mapa.escopo_da_missao():
            dentro_mapa = pv.MANIFESTO
            with corpus.escopo_da_missao():
                dentro_corpus = pv.MANIFESTO
            self.assertEqual(dentro_mapa, pv.MANIFESTO,
                             'sair do corpus deixou o mapa a ler o manifesto errado')
        self.assertNotEqual(dentro_mapa, dentro_corpus,
                            'as duas missões partilham manifesto — o namespace não existe')
        self.assertEqual(self.antes[0], pv.MANIFESTO)

    def test_a_ordem_de_importacao_deixa_de_decidir_quem_ganha(self):
        """Antes, o último módulo importado ficava dono do manifesto da casa."""
        _carrega('creator_corpus_coleta', '_iso_ord1')
        _carrega('creator_coleta', '_iso_ord2')
        self.assertEqual(self.antes[0], pv.MANIFESTO)
        _carrega('creator_coleta', '_iso_ord3')
        _carrega('creator_corpus_coleta', '_iso_ord4')
        self.assertEqual(self.antes[0], pv.MANIFESTO)

    def test_cada_missao_declara_o_seu_dono_e_sao_diferentes(self):
        """O dono sai do mapa declarado, nunca do prefixo do RUN_ID."""
        mapa = _carrega('creator_coleta', '_iso_dono1')
        corpus = _carrega('creator_corpus_coleta', '_iso_dono2')
        donos = [pv.dono_da_missao(m.MISSION) for m in (mapa, corpus)]
        self.assertNotEqual(donos[0], donos[1],
                            'Creator Map e Creator Content Corpus são datasets diferentes')
        for dono in donos:
            self.assertNotEqual(pv.UNDECLARED_OWNER, dono,
                                'missão sem dono declarado em pv.DONOS')
        self.assertEqual(pv.UNDECLARED_OWNER, pv.dono_da_missao('MISSAO-QUE-NAO-EXISTE'),
                         'o fail-closed foi enfraquecido para conseguir verde')


class TestODispatchDeProducaoCorreDentroDoEscopo(unittest.TestCase):
    """Propriedade 2, provada onde ela importa: no `__main__` que o workflow chama.

    Sem esta classe, apagar `with escopo_da_missao():` do dispatch deixava os nove
    testes anteriores verdes — o context manager continuava correto e ninguém o
    usava. A fase real voltava a escrever no manifesto e no `raw-paid` DA CASA.
    Medido: 9/9 passed com as duas linhas removidas.

    O método é uma sonda no primeiro ponto que toda fase atravessa: `apify_pool.pool()`.
    Ela regista o que a fase VÊ e levanta `SystemExit` antes de gastar rede ou dinheiro.
    """

    SONDAS = (
        ('creator_coleta.py', 'contratos',
         os.path.join('CREATOR-MAP-EAME', 'RUN-MANIFEST-CREATORS.json')),
        ('creator_corpus_coleta.py', 'contratos',
         os.path.join('CREATOR-CONTENT-CORPUS-EAME', 'RUN-MANIFEST-CORPUS.json')),
    )

    def setUp(self):
        self.antes = (pv.MANIFESTO, coletor.RAW_DIR, coletor._curl)

    def tearDown(self):
        pv.MANIFESTO, coletor.RAW_DIR, coletor._curl = self.antes

    def _corre(self, script, fase):
        """Corre o `__main__` de verdade e devolve o que a fase viu."""
        import apify_pool as ap
        visto = {}
        original, argv = ap.pool, sys.argv

        def sonda():
            visto['MANIFESTO'] = pv.MANIFESTO
            visto['RAW_DIR'] = coletor.RAW_DIR
            visto['CURL'] = coletor._curl
            raise SystemExit(0)     # para antes de qualquer chamada paga

        ap.pool = sonda
        sys.argv = [script, fase]
        try:
            runpy.run_path(os.path.join(ROOT, 'scripts', script), run_name='__main__')
        except SystemExit:
            pass
        finally:
            ap.pool, sys.argv = original, argv
        return visto

    def test_a_fase_real_ve_o_manifesto_e_o_raw_dir_da_missao(self):
        for script, fase, esperado in self.SONDAS:
            visto = self._corre(script, fase)
            self.assertTrue(visto, '%s não chegou à sonda — a fase mudou de forma' % script)
            self.assertTrue(
                visto['MANIFESTO'].endswith(esperado),
                '%s: a fase correu contra %s, não contra o manifesto da missão'
                % (script, visto['MANIFESTO']))
            self.assertIn('raw-paid', visto['RAW_DIR'])
            self.assertNotEqual(
                self.antes[1], visto['RAW_DIR'],
                '%s: a fase escreveria o bruto no raw-paid DA CASA' % script)

    def test_a_fase_real_usa_a_porta_de_rede_da_missao(self):
        for script, fase, _ in self.SONDAS:
            visto = self._corre(script, fase)
            self.assertIsNot(
                self.antes[2], visto['CURL'],
                '%s: a fase correu com o transporte HTTP da casa' % script)

    def test_depois_do_dispatch_o_global_volta_ao_da_casa(self):
        for script, fase, _ in self.SONDAS:
            self._corre(script, fase)
            self.assertEqual(self.antes[0], pv.MANIFESTO,
                             '%s deixou pv.MANIFESTO redirecionado' % script)
            self.assertEqual(self.antes[1], coletor.RAW_DIR)
            self.assertIs(self.antes[2], coletor._curl)


class TestReconciliarNaoEntraNoEscopo(unittest.TestCase):
    """`pv.reconciliar()` derivaria o índice de TODOS os donos para dentro da missão."""

    def setUp(self):
        self.antes = (pv.MANIFESTO, coletor.RAW_DIR, coletor._curl, pv.reconciliar)

    def tearDown(self):
        pv.MANIFESTO, coletor.RAW_DIR, coletor._curl, pv.reconciliar = self.antes

    def test_dentro_do_escopo_reconciliar_falha_alto(self):
        for i, (nome, _) in enumerate(MISSOES):
            mod = _carrega(nome, '_iso_rec_%d' % i)
            with mod.escopo_da_missao():
                # A identidade PRIMEIRO, e de propósito: se a guarda faltar,
                # `pv.reconciliar` é a função verdadeira e chamá-la ESCREVE os
                # fragmentos de todos os donos dentro do manifesto desta missão.
                # Medido: numa corrida de mutação sem guarda, este ficheiro passou
                # de 7 execuções de um dono para 22 de três. O teste tem de falhar
                # antes de tocar no disco, nunca depois.
                self.assertIsNot(self.antes[3], pv.reconciliar,
                                 '%s não instalou a guarda do reconciliar' % nome)
                with self.assertRaises(RuntimeError, msg='%s deixou reconciliar passar' % nome):
                    pv.reconciliar('2026-09-05')

    def test_fora_do_escopo_reconciliar_continua_a_ser_a_funcao_da_casa(self):
        for i, (nome, _) in enumerate(MISSOES):
            mod = _carrega(nome, '_iso_rec2_%d' % i)
            with mod.escopo_da_missao():
                pass
            self.assertIs(self.antes[3], pv.reconciliar,
                          '%s não devolveu pv.reconciliar' % nome)


if __name__ == '__main__':
    unittest.main()
