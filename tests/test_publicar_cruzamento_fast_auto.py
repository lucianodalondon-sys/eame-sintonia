"""O publicador do cruzamento segue a rodada AUTOMATICA da Intelligence (FAST-AUTO/ULTIMA.txt), falha fechada.

    python -m unittest tests.test_publicar_cruzamento_fast_auto
"""
import os, shutil, sys, tempfile, unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', 'italia-portale', 'audit', 'casco'))
import publicar_cruzamento_preview as P  # noqa: E402

REAL = r'C:/Users/London1/sintonia-sala-italia/intelligence-experimental/FAST-AUTO'
RUN = 'FAST-20261002T044229'
SHA = 'e392db76ec44a44b7b399b60900b8299fcd21254e17339f739b159f2ba908218'


def montar(raiz, run, ponteiro=None, adulterar=False, sem_sums=False):
    d = os.path.join(raiz, run)
    os.makedirs(d)
    for f in ('CRUZAMENTO-COMERCIAL.json', 'SHA256SUMS.txt'):
        if f == 'SHA256SUMS.txt' and sem_sums:
            continue
        shutil.copy(os.path.join(REAL, RUN, f), d)
    if adulterar:
        open(os.path.join(d, 'CRUZAMENTO-COMERCIAL.json'), 'a').write(' ')
    with open(os.path.join(raiz, 'ULTIMA.txt'), 'w') as fh:
        fh.write((ponteiro if ponteiro is not None else 'RUN_ID=' + run) + '\n')


@unittest.skipUnless(os.path.isdir(os.path.join(REAL, RUN)), 'rodada real ausente nesta maquina')
class SegueFastAuto(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.t, ignore_errors=True)

    def test_rodada_automatica_e_escolhida(self):
        montar(self.t, RUN)
        e = P.escolher(self.t)
        self.assertIsNotNone(e)
        self.assertEqual(e['RUN_ID'], RUN)
        self.assertEqual(e['SHA'], SHA)
        self.assertEqual(os.path.normpath(e['PASTA']), os.path.normpath(os.path.join(self.t, RUN)))

    def test_ponteiro_lixo_recusa(self):
        for lixo in ('RUN_ID=../remessa-001', 'RUN_ID=a/b', 'qualquer coisa', 'RUN_ID='):
            shutil.rmtree(self.t); os.makedirs(self.t)
            montar(self.t, RUN, ponteiro=lixo)
            self.assertIsNone(P.escolher(self.t), lixo)

    def test_sha_adulterado_recusa(self):
        montar(self.t, RUN, adulterar=True)
        self.assertIsNone(P.escolher(self.t))

    def test_sem_sha256sums_recusa(self):
        montar(self.t, RUN, sem_sums=True)
        self.assertIsNone(P.escolher(self.t))

    def test_sem_ultima_recusa(self):
        montar(self.t, RUN)
        os.remove(os.path.join(self.t, 'ULTIMA.txt'))
        self.assertIsNone(P.escolher(self.t))

    def test_remessa_001_deixa_de_ser_fonte(self):
        self.assertNotIn('sintonia-fluxo-unico', P.FAST_AUTO_PADRAO)
        e = P.escolher(REAL)
        self.assertIsNotNone(e)
        self.assertTrue(e['RUN_ID'].startswith('FAST-'))


if __name__ == '__main__':
    unittest.main()
