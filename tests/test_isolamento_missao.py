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


if __name__ == '__main__':
    unittest.main()
