"""O Casco le o ESTADO VIVO ACUMULADO (INTELLIGENCE-CURRENT.json), nao a ultima rodada.

Usa as 4 rodadas REAIS de 04/10 (copiadas para uma pasta temporaria) e o acumulador da Intelligence
(motor/fast_auto/estado_vivo.py do commit 722bf312e). O casco nao acumula: so confere e reembala.

    python -m unittest tests.test_casco_le_estado_vivo
"""
import importlib.util, json, os, shutil, subprocess, sys, tempfile, unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
CASCO = os.path.join(AQUI, '..', 'italia-portale', 'audit', 'casco')
sys.path.insert(0, CASCO)
import gerar_cruzamento_publicado as G  # noqa: E402
import publicar_cruzamento_preview as P  # noqa: E402

REAL = r'C:/Users/London1/sintonia-sala-italia/intelligence-experimental/FAST-AUTO'
EV = r'C:/g/fast-auto-722bf312/motor/fast_auto/estado_vivo.py'
RUNS = ['FAST-20261004T004228', 'FAST-20261004T024230', 'FAST-20261004T044228', 'FAST-20261004T064230']
TRES = ('melinda', 'invitalia', 'agrisicilia')


def aplicar(raiz, *runs):
    r = subprocess.run([sys.executable, EV, 'aplicar', raiz] + list(runs), capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def envelope(raiz):
    env, motivo = G.envelope_do_vivo(os.path.join(raiz, 'INTELLIGENCE-CURRENT.json'))
    assert env, motivo
    return env


def market(env):
    return [o for o in env['CRUZAMENTO']['OBJETOS'] if 'MARKET_PULSE' in (o.get('DESTINO_FERRAMENTA') or [])]


def tem(objs, nome):
    return any(nome in (json.dumps(o.get('TITULO', ''), ensure_ascii=False) + json.dumps(o.get('TITULO_IT', ''),
               ensure_ascii=False)).lower() for o in objs)


@unittest.skipUnless(os.path.isfile(EV) and all(os.path.isdir(os.path.join(REAL, r)) for r in RUNS),
                     'rodadas reais / acumulador ausentes')
class CascoLeEstadoVivo(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp()
        for r in RUNS:
            shutil.copytree(os.path.join(REAL, r), os.path.join(self.t, r))
        open(os.path.join(self.t, 'ULTIMA.txt'), 'w').write('RUN_ID=' + RUNS[-1] + '\n')

    def tearDown(self):
        shutil.rmtree(self.t, ignore_errors=True)

    def test_rodada_vazia_nao_zera_market(self):
        aplicar(self.t, RUNS[0])
        m1 = market(envelope(self.t))
        self.assertEqual(len(m1), 3)
        for n in TRES:
            self.assertTrue(tem(m1, n), n)
        aplicar(self.t, *RUNS[1:])
        env = envelope(self.t)
        m4 = market(env)
        for n in TRES:
            self.assertTrue(tem(m4, n), n)
        self.assertGreaterEqual(len(m4), 3)
        # o que a ultima rodada sozinha daria ao casco: 0 no Market Pulse
        ult = json.load(open(os.path.join(self.t, RUNS[-1], 'CRUZAMENTO-COMERCIAL.json'), encoding='utf-8'))
        self.assertEqual(sum('MARKET_PULSE' in (o.get('DESTINO_FERRAMENTA') or []) for o in ult['OBJETOS']), 0)

    def test_nao_publicar_nunca_no_envelope(self):
        aplicar(self.t, *RUNS)
        env = envelope(self.t)
        self.assertNotIn('NAO_PUBLICAR', env['CRUZAMENTO']['DESTINOS'])
        for o in env['CRUZAMENTO']['OBJETOS']:
            self.assertNotIn('NAO_PUBLICAR', o.get('DESTINO_FERRAMENTA') or [])

    def test_repetir_rodada_nao_duplica(self):
        aplicar(self.t, *RUNS)
        a = [o['ID'] for o in envelope(self.t)['CRUZAMENTO']['OBJETOS']]
        aplicar(self.t, RUNS[0])
        b = [o['ID'] for o in envelope(self.t)['CRUZAMENTO']['OBJETOS']]
        self.assertEqual(sorted(a), sorted(b))
        self.assertEqual(len(b), len(set(b)))

    def test_publicador_escolhe_o_vivo_e_nao_a_ultima(self):
        aplicar(self.t, *RUNS)
        e = P.escolher_vivo(self.t)
        self.assertIsNotNone(e)
        self.assertTrue(e['PASTA'].endswith('INTELLIGENCE-CURRENT.json'))
        self.assertEqual(e['RUN_ID'], 'VIVO@' + RUNS[-1])

    def test_vivo_adulterado_recusa(self):
        aplicar(self.t, *RUNS)
        open(os.path.join(self.t, 'INTELLIGENCE-CURRENT.json'), 'a').write(' ')
        self.assertIsNone(P.escolher_vivo(self.t))
        env, motivo = G.envelope_do_vivo(os.path.join(self.t, 'INTELLIGENCE-CURRENT.json'))
        self.assertIsNone(env)

    def test_sem_vivo_nao_recua_para_ultima(self):
        self.assertIsNone(P.escolher_vivo(self.t))  # so ha ULTIMA.txt: o publicador nao faz nada

    def test_leitor_js_aceita_o_envelope(self):
        aplicar(self.t, *RUNS)
        env = envelope(self.t)
        js = os.path.join(AQUI, '..', 'italia-portale', 'client', 'sintonia-cruzamento-casco.js')
        f = os.path.join(self.t, 'env.json')
        json.dump(env, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
        prog = ("const fs=require('fs');global.window={};eval(fs.readFileSync(process.argv[1],'utf8'));"
                "const C=window.SINTONIA_CRUZAMENTO_CASCO,e=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));"
                "console.log(JSON.stringify({f:C.conferir(e),m:C.objetosDaVista(e,'market').length}))")
        r = subprocess.run(['node', '-e', prog, js, f], capture_output=True, text=True, encoding='utf-8')
        out = json.loads(r.stdout)
        self.assertEqual(out['f'], [])
        self.assertEqual(out['m'], len(market(env)))


if __name__ == '__main__':
    unittest.main()
