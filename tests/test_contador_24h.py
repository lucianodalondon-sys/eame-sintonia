# -*- coding: utf-8 -*-
"""O contador multicanal (D90): RESERVAR antes do pedido, atomico, partilhado — AGORA ADAPTATIVO (D124).

    py tests/test_contador_24h.py

Sem rede: o livro vive numa pasta temporaria. A corrida concorrente e entre PROCESSOS reais
(multiprocessing e node), nao threads. A prova do transporte contra o servidor local e a de
`provas/contador_24h_local.mjs` (A1..A4, B1..B4, C1), chamada aqui.

REESCRITO DE FORMA DECLARADA (D124, dono 27/09 ~21:30): este ficheiro prendia o teto FIXO de 5 por dominio
em 24 h («cinco passam, o sexto fica adiado», «16 processos: so 5 passam»). A D124 revogou o 5: o teto e o
orcamento VIGENTE da politica adaptativa (`coleta/cortesia_adaptativa.py`; SITE comeca em 40) e ha 1 pedido
de cada vez por dominio. As mesmas perguntas continuam aqui, com a regra nova: a reserva e atomica entre
processos e linguagens (D90-2: o 2.o executor recebe ADIADO_ATE sem pedir), a janela e movel, o dominio e o
registavel, googlevideo paga de youtube, sem livro e FAIL, livro ilegivel e UNKNOWN e nada se escreve.
As provas do sobe/recua/pausa/alerta vivem em `tests/test_cortesia_adaptativa.py`.
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
from coleta import cortesia_adaptativa as CA  # noqa: E402

T0 = 1_800_000_000.0


def _corredor(args):
    livro, i, n = args
    os.environ["SINTONIA_CORTESIA_LIVRO"] = livro
    sys.path.insert(0, str(RAIZ))
    from coleta import reserva_24h as RR                           # noqa: E402
    return [RR.reservar("www.cia.it", 1, run_id="P%d-%d" % (i, k), linha="L%d" % (i % 3))["ESTADO"]
            for k in range(n)]


def _reservas(livro):
    return [e for e in CA.ler_eventos(Path(livro)) if e["TIPO"] == "RESERVA"]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="c24-"))
        self.livro = self.tmp / "LIVRO-CORTESIA.ndjson"
        for k in ("SINTONIA_TETO_24H", "SINTONIA_CORTESIA_ALERTAS", "SINTONIA_TETO_POR_HOST"):
            os.environ.pop(k, None)
        os.environ["SINTONIA_CORTESIA_LIVRO"] = str(self.livro)

    def tearDown(self):
        os.environ.pop("SINTONIA_CORTESIA_LIVRO", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def res(self, host="cia.it", q=1, t=T0, run="r", linha="L"):
        return R.reservar(host, q, run_id=run, linha=linha, agora=t)

    def pedido(self, host="cia.it", t=T0, run="r"):
        r = self.res(host, t=t, run=run)
        if r["ESTADO"] == "RESERVADO":
            CA.registrar_resposta(host, 200, run_id=run, linha="L", agora=t + 1)
        return r


class ARegra(Base):
    def test_o_orcamento_vigente_passa_e_o_seguinte_fica_adiado_com_a_hora(self):
        """Era «cinco passam, o sexto fica adiado» (D38). D124: 40 passam (SITE), o 41.o fica adiado."""
        for k in range(40):
            self.assertEqual(self.pedido(t=T0 + 10 * k)["ESTADO"], "RESERVADO", k)
        r = self.res(t=T0 + 1000)
        self.assertEqual((r["ESTADO"], r["MOTIVO"]), ("ADIADO_ATE", "ORCAMENTO_ESGOTADO"))
        self.assertEqual(r["ATE"], T0 + 24 * 3600)                  # sai a mais antiga

    def test_janela_movel(self):
        for k in range(40):
            self.pedido(t=T0 + 10 * k)
        self.assertEqual(self.res(t=T0 + 24 * 3600 + 0.5)["ESTADO"], "RESERVADO")   # a 1.a ja saiu

    def test_dominio_registavel_junta_www_e_sub(self):
        self.assertEqual(self.res(host="www.cia.it")["ESTADO"], "RESERVADO")
        for h in ("cia.it", "sub.cia.it", "WWW.CIA.IT"):
            r = self.res(host=h, t=T0 + 1)
            self.assertEqual((r["ESTADO"], r["DOMINIO"]), ("ADIADO_ATE", "cia.it"), h)

    def test_googlevideo_gasta_de_youtube(self):
        self.assertEqual(self.res(host="r1---sn-x.googlevideo.com")["ESTADO"], "RESERVADO")
        r = self.res(host="www.youtube.com", t=T0 + 1)
        self.assertEqual((r["ESTADO"], r["DOMINIO"], r["MOTIVO"]), ("ADIADO_ATE", "youtube.com", "UM_DE_CADA_VEZ"))

    def test_um_de_cada_vez(self):
        """Era «quantidade maior que o que sobra». D124: nunca mais de um pedido em curso por dominio."""
        self.assertEqual(self.res(q=3)["ESTADO"], "FAIL")
        self.assertEqual(self.res()["ESTADO"], "RESERVADO")
        self.assertEqual(self.res(t=T0 + 2)["MOTIVO"], "UM_DE_CADA_VEZ")

    def test_regista_quem_gastou(self):
        self.res(run="IT-T7-1", linha="SITES")
        r = _reservas(self.livro)[0]
        self.assertEqual((r["DOMINIO"], r["RUN_ID"], r["LINHA"], r["EM"]), ("cia.it", "IT-T7-1", "SITES", T0))

    def test_sem_livro_e_fail(self):
        os.environ.pop("SINTONIA_CORTESIA_LIVRO")
        self.assertEqual(self.res()["ESTADO"], "FAIL")

    def test_pedido_invalido_e_fail(self):
        self.assertEqual(R.reservar("cia.it", 0, run_id="r", linha="L")["ESTADO"], "FAIL")
        self.assertEqual(R.reservar("cia.it", 6, run_id="r", linha="L")["ESTADO"], "FAIL")
        self.assertEqual(R.reservar("cia.it", 1, run_id="", linha="L")["ESTADO"], "FAIL")

    def test_livro_ilegivel_e_unknown_e_nao_escreve(self):
        self.livro.write_text("{nao e json", encoding="utf-8")
        self.assertEqual(self.res()["ESTADO"], "UNKNOWN")
        self.assertEqual(self.livro.read_text(encoding="utf-8"), "{nao e json")

    def test_json_valido_de_outro_formato_e_unknown(self):
        """Um livro que e JSON mas nao e o livro da cortesia (outro ficheiro, ou o D90 malformado) NAO e vazio.

        D124-REBASE — AJUSTE DECLARADO (verificador independente, 28/09): '{"RESERVAS": []}' saiu desta lista.
        E o formato do livro VIVO da D90 (TETO-24H.json da coleta continua): bem formado, le-se e migra-se
        (tests/test_teto_adaptativo_rebase.py::OLivroAntigo). O D90 MALFORMADO continua UNKNOWN e fica no lugar."""
        for conteudo in ('{"PEDIDOS_POR_DOMINIO": {"cia.it": 5}}', '{"RESERVAS": 3}'):
            self.livro.write_text(conteudo, encoding="utf-8")
            self.assertEqual(self.res()["ESTADO"], "UNKNOWN", conteudo)
            self.assertIsNone(R.gasto_24h("cia.it"))

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
    def test_16_processos_python_no_mesmo_dominio_so_1_passa(self):
        """D90-2: era «so 5 passam». D124: 1 de cada vez — os outros 47 recebem ADIADO_ATE sem pedir."""
        with mp.get_context("spawn").Pool(8) as p:
            estados = [e for lote in p.map(_corredor, [(str(self.livro), i, 3) for i in range(16)]) for e in lote]
        self.assertEqual(estados.count("RESERVADO"), 1, estados)
        self.assertEqual(estados.count("ADIADO_ATE"), 48 - 1)
        self.assertEqual(len(_reservas(self.livro)), 1)

    def test_python_e_node_excluem_se_pelo_mesmo_trinco(self):
        js = ("import('./coleta/italy_pilot_collect.mjs').then(m=>{const o=[];for(let i=0;i<6;i++)"
              "o.push(m.reservar24h('cia.it',1,{runId:'N'+i}).ESTADO);console.log(JSON.stringify(o))})")
        p = subprocess.Popen(["node", "-e", js], cwd=RAIZ, env=dict(os.environ), stdout=subprocess.PIPE, text=True)
        py = [R.reservar("cia.it", 1, run_id="P%d" % k, linha="PY")["ESTADO"] for k in range(6)]
        node = json.loads(p.communicate(timeout=120)[0].strip().splitlines()[-1])
        self.assertEqual((py + node).count("RESERVADO"), 1, (py, node))
        self.assertEqual(len(_reservas(self.livro)), 1)


class OGemeoNode(Base):
    def _node(self, js):
        p = subprocess.run(["node", "-e", js], cwd=RAIZ, env=dict(os.environ), capture_output=True, text=True, timeout=120)
        return p.stdout.strip().splitlines()[-1]

    def test_node_livro_ilegivel_e_unknown(self):
        for conteudo in ("{nao e json", '{"PEDIDOS_POR_DOMINIO": {"cia.it": 5}}'):
            self.livro.write_text(conteudo, encoding="utf-8")
            e = self._node("import('./coleta/italy_pilot_collect.mjs').then(m=>console.log(m.reservar24h('cia.it',1,{runId:'N'}).ESTADO))")
            self.assertEqual(e, "UNKNOWN", conteudo)
            self.assertEqual(self.livro.read_text(encoding="utf-8"), conteudo)

    def test_node_regra_igual_a_do_python(self):
        t = time.time()
        e = self._node("import('./coleta/italy_pilot_collect.mjs').then(m=>{const o=[];"
                       "o.push(m.reservar24h('www.cia.it',1,{runId:'N0'}).ESTADO, m.reservar24h('cia.it',1,{runId:'N1'}).MOTIVO,"
                       "m.reservar24h('cia.it',2,{runId:'N2'}).ESTADO, m.reservar24h('r1.googlevideo.com',1,{runId:'Y'}).ESTADO,"
                       "m.reservar24h('youtube.com',1,{runId:'Y2'}).MOTIVO);console.log(o.join(','))})")
        self.assertEqual(e, "RESERVADO,UM_DE_CADA_VEZ,FAIL,RESERVADO,UM_DE_CADA_VEZ")
        self.assertEqual(R.reservar("cia.it", 1, run_id="P", linha="PY", agora=t + 1)["MOTIVO"], "UM_DE_CADA_VEZ")


class OTransporteContraOServidor(unittest.TestCase):
    def test_prova_adversarial_contra_o_servidor_local(self):
        """A1..A4 (atomico, 1 de cada vez, Python + Node), B1..B4 (429/Retry-After, desafio, 503, sobe), C1 (robots)."""
        r = subprocess.run(["node", "provas/contador_24h_local.mjs"], cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-2500:] + r.stderr[-800:])
        self.assertIn("passou=21 FALHAS=0", r.stdout)


if __name__ == "__main__":
    unittest.main()
