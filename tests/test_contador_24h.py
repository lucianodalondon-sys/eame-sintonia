# -*- coding: utf-8 -*-
"""O contador multicanal de 24 h (D90): RESERVAR antes do pedido, atomico, partilhado.

    py tests/test_contador_24h.py

Sem rede: o livro vive numa pasta temporaria. A corrida concorrente e entre PROCESSOS reais
(multiprocessing e node), nao threads. A prova do transporte contra o servidor local e a de
`provas/contador_24h_local.mjs` (A1..A4), chamada aqui.
"""
import json
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from coleta import reserva_24h as R  # noqa: E402

T0 = 1_800_000_000.0


def _corredor(args):
    livro, i, n = args
    os.environ["SINTONIA_TETO_24H"] = livro
    sys.path.insert(0, str(RAIZ))
    from coleta import reserva_24h as RR                           # noqa: E402
    return [RR.reservar("www.cia.it", 1, run_id="P%d-%d" % (i, k), linha="L%d" % (i % 3))["ESTADO"]
            for k in range(n)]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="c24-"))
        self.livro = self.tmp / "TETO-24H.json"
        os.environ["SINTONIA_TETO_24H"] = str(self.livro)

    def tearDown(self):
        os.environ.pop("SINTONIA_TETO_24H", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def res(self, host="cia.it", q=1, t=T0, run="r", linha="L"):
        return R.reservar(host, q, run_id=run, linha=linha, agora=t)


class ARegra(Base):
    def test_cinco_passam_o_sexto_fica_adiado_com_a_hora(self):
        for k in range(5):
            self.assertEqual(self.res(t=T0 + k)["ESTADO"], "RESERVADO")
        r = self.res(t=T0 + 10)
        self.assertEqual(r["ESTADO"], "ADIADO_ATE")
        self.assertEqual(r["ATE"], T0 + 24 * 3600)                  # sai a mais antiga

    def test_janela_movel(self):
        for k in range(5):
            self.res(t=T0 + k)
        self.assertEqual(self.res(t=T0 + 24 * 3600 + 0.5)["ESTADO"], "RESERVADO")   # a 1.a ja saiu

    def test_dominio_registavel_junta_www_e_sub(self):
        for h in ("cia.it", "www.cia.it", "sub.cia.it", "WWW.CIA.IT", "cia.it"):
            self.assertEqual(self.res(host=h)["ESTADO"], "RESERVADO")
        self.assertEqual(self.res(host="x.cia.it")["ESTADO"], "ADIADO_ATE")

    def test_googlevideo_gasta_de_youtube(self):
        self.assertEqual(self.res(host="r1---sn-x.googlevideo.com", q=5)["ESTADO"], "RESERVADO")
        self.assertEqual(self.res(host="www.youtube.com")["ESTADO"], "ADIADO_ATE")

    def test_quantidade_maior_que_o_que_sobra(self):
        self.res(q=3)
        self.assertEqual(self.res(q=3)["ESTADO"], "ADIADO_ATE")
        self.assertEqual(self.res(q=2)["ESTADO"], "RESERVADO")

    def test_regista_quem_gastou(self):
        self.res(run="IT-T7-1", linha="SITES")
        r = json.loads(self.livro.read_text(encoding="utf-8"))["RESERVAS"][0]
        self.assertEqual((r["DOMINIO"], r["QTD"], r["RUN_ID"], r["LINHA"], r["EM"]), ("cia.it", 1, "IT-T7-1", "SITES", T0))

    def test_sem_livro_e_fail(self):
        os.environ.pop("SINTONIA_TETO_24H")
        self.assertEqual(self.res()["ESTADO"], "FAIL")

    def test_pedido_invalido_e_fail(self):
        self.assertEqual(R.reservar("cia.it", 0, run_id="r", linha="L")["ESTADO"], "FAIL")
        self.assertEqual(R.reservar("cia.it", 6, run_id="r", linha="L")["ESTADO"], "FAIL")
        self.assertEqual(R.reservar("cia.it", 1, run_id="", linha="L")["ESTADO"], "FAIL")

    def test_livro_ilegivel_e_unknown_e_nao_escreve(self):
        self.livro.write_text("{nao e json", encoding="utf-8")
        self.assertEqual(self.res()["ESTADO"], "UNKNOWN")
        self.assertEqual(self.livro.read_text(encoding="utf-8"), "{nao e json")

    def test_trinco_preso_e_unknown(self):
        os.mkdir(str(self.livro) + ".trinco")
        velho = R.TRINCO_ESPERA_S
        R.TRINCO_ESPERA_S = 0.2
        try:
            self.assertEqual(self.res()["ESTADO"], "UNKNOWN")
        finally:
            R.TRINCO_ESPERA_S = velho
            os.rmdir(str(self.livro) + ".trinco")

    def test_o_trinco_e_libertado(self):
        self.res()
        self.assertFalse(Path(str(self.livro) + ".trinco").exists())


class ACorridaEntreProcessos(Base):
    def test_16_processos_python_no_mesmo_dominio_so_5_passam(self):
        with mp.get_context("spawn").Pool(8) as p:
            estados = [e for lote in p.map(_corredor, [(str(self.livro), i, 3) for i in range(16)]) for e in lote]
        self.assertEqual(estados.count("RESERVADO"), 5, estados)
        self.assertEqual(estados.count("ADIADO_ATE"), 48 - 5)
        self.assertEqual(len(json.loads(self.livro.read_text(encoding="utf-8"))["RESERVAS"]), 5)

    def test_python_e_node_excluem_se_pelo_mesmo_trinco(self):
        js = ("import('./coleta/italy_pilot_collect.mjs').then(m=>{const o=[];for(let i=0;i<6;i++)"
              "o.push(m.reservar24h('cia.it',1,{runId:'N'+i}).ESTADO);console.log(JSON.stringify(o))})")
        env = dict(os.environ)
        p = subprocess.Popen(["node", "-e", js], cwd=RAIZ, env=env, stdout=subprocess.PIPE, text=True)
        py = [R.reservar("cia.it", 1, run_id="P%d" % k, linha="PY")["ESTADO"] for k in range(6)]
        node = json.loads(p.communicate(timeout=120)[0].strip().splitlines()[-1])
        self.assertEqual((py + node).count("RESERVADO"), 5, (py, node))
        self.assertEqual(len(json.loads(self.livro.read_text(encoding="utf-8"))["RESERVAS"]), 5)


class OTransporteContraOServidor(unittest.TestCase):
    def test_prova_adversarial_A1_a_A4(self):
        r = subprocess.run(["node", "provas/contador_24h_local.mjs"], cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-500:])
        self.assertIn("passou=8 FALHAS=0", r.stdout)


if __name__ == "__main__":
    unittest.main()
