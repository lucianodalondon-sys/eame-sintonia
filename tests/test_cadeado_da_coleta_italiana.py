#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CADEADO DA COLETA ITALIANA — dono morto e ASSUMIDO, dono vivo e RESPEITADO.

    py -m unittest tests.test_cadeado_da_coleta_italiana

O DEFEITO QUE ISTO FECHA
------------------------
`pegarLock()` (coleta/italy_recurrent_collect.mjs) fazia:

    try { const fd = openSync(LOCK, "wx"); ... return true; }
    catch { return false; }

O `catch` apanhava QUALQUER erro e chamava-lhe o mesmo nome: «outra coleta esta
a correr». O cadeado nunca era LIDO — nao dizia de quem era, nao dizia quando
nasceu, e nao era conferido contra o processo que o deixou. Um processo morto no
meio da corrida deixava o cadeado preso, e a coleta horaria parava para sempre,
sem que nada a pudesse destravar a nao ser alguem a renomear o ficheiro a mao.

Medido no registo de producao (`data/collection-ledger/italy/logs/runs.log`), em
2026-09-28: 518 execucoes, 430 delas paradas em `SKIPPED_LOCK_HELD`.

    «NAO CONSEGUI PEGAR O CADEADO» NAO E «OUTRA COLETA ESTA A CORRER».
    SO UMA DESSAS DUAS E MOTIVO PARA NAO COLHER.

O QUE SE PROVA AQUI — POR RUNTIME, COM PROCESSOS A SERIO
--------------------------------------------------------
Os casos correm o entrypoint AGENDADO (`node coleta/italy_recurrent_collect.mjs`)
com `ITALY_OPS_ROOT` a apontar para uma pasta descartavel: o cadeado e o log
nascem e morrem la. `--simulate-vpn DE` poe o egress fora da Italia e faz a
corrida PARAR ANTES do portao e da rede — nenhum caso aqui toca uma fonte.

Nenhum caso le o ficheiro do runner a procura de frases. O que se compara e o
RESUMO que a corrida escreve, e o ESTADO DO CADEADO no disco depois dela:

  1. sem cadeado                     -> a corrida segue, e o cadeado e solto
  2. cadeado com processo VIVO       -> RESPEITADO (nada e assumido, nada e tocado)
  3. cadeado com processo MORTO      -> ASSUMIDO, e o antigo fica PRESERVADO
  4. cadeado VAZIO e recente         -> RESPEITADO (nao se assume o que e recente)
  5. cadeado ILEGIVEL e velho        -> ASSUMIDO, e o antigo fica PRESERVADO
  6. cadeado de OUTRO host, recente  -> RESPEITADO (um pid de outra maquina NAO SE MEDE daqui)

O caso 2 e o controlo POSITIVO do 3, e o 4 e o controlo NEGATIVO do 5: um dono
vivo TEM de travar, um ficheiro ilegivel recente NAO pode ser assumido por
descargo de consciencia. Sem o par, uma regra que assumisse sempre passaria.
"""
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join("coleta", "italy_recurrent_collect.mjs")
CADEADO = ".italy-forward-only.lock"
PRESERVADO = CADEADO + ".ASSUMIDO-"
MAX_IDADE_DE_CORRIDA_MIN = 15     # o mesmo teto que o runner declara
VELHO_MIN = 6 * 60                # 6 h: muito acima de qualquer corrida medida


def _hostname_como_o_node_o_ve():
    """O host tem de ser lido PELO MESMO instrumento que o runner usa.

    `socket.gethostname()` pode diferir de `os.hostname()` por caixa; se
    diferisse, o caso 2 passaria a ser «NAO SEI» e estaria a passar pela razao
    errada — um verde falso, que e o unico erro que esta lei nao pode cometer.
    """
    r = subprocess.run(["node", "-e", "process.stdout.write(require('node:os').hostname())"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip()


def _node_existe():
    return shutil.which("node") is not None


class Cadeado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not _node_existe():
            raise unittest.SkipTest("node nao esta nesta maquina — a prova de runtime do cadeado nao corre aqui")
        cls.host = _hostname_como_o_node_o_ve()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ops = self.tmp.name
        self.filhos = []

    def tearDown(self):
        for p in self.filhos:
            try:
                p.kill()
                p.wait(timeout=10)
            except Exception:
                pass
        self.tmp.cleanup()

    # ---------- instrumentos ----------
    def caminho(self):
        return os.path.join(self.ops, CADEADO)

    def escrever_cadeado(self, conteudo, idade_min=0):
        p = self.caminho()
        with open(p, "w", encoding="utf-8") as f:
            f.write(conteudo)
        if idade_min:
            t = time.time() - idade_min * 60
            os.utime(p, (t, t))
        return p

    def ler(self, caminho):
        with open(caminho, encoding="utf-8") as f:
            return f.read()

    def preservados(self):
        return sorted(n for n in os.listdir(self.ops) if n.startswith(PRESERVADO))

    def filho_vivo(self):
        """Um processo A SERIO, vivo, com um pid que se pode medir daqui."""
        p = subprocess.Popen(["node", "-e", "setInterval(() => {}, 1000)"])
        self.filhos.append(p)
        # espera que o pid exista de facto antes de o declarar vivo
        for _ in range(50):
            if p.poll() is None:
                time.sleep(0.05)
                return p.pid
        self.fail("o processo de controle negativo nao chegou a ficar vivo")

    def filho_morto(self):
        """Um pid que EXISTIU e morreu — o caso real que travava a coleta."""
        pid = self.filho_vivo()
        p = self.filhos[-1]
        p.kill()
        p.wait(timeout=10)
        self.filhos.remove(p)
        self.assertIsNotNone(p.returncode, "o pid de controle positivo nao chegou a morrer")
        return pid

    def correr_o_agendado(self):
        r = subprocess.run(
            ["node", RUNNER, "--profile", "forward-only-live",
             "--simulate-vpn", "DE", "--no-git"],
            cwd=RAIZ, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300,
            env={**os.environ, "ITALY_OPS_ROOT": self.ops})
        self.assertIn("{", r.stdout, "o runner nao devolveu resumo: %s" % r.stderr[-600:])
        return json.loads(r.stdout[r.stdout.index("{"):])

    def sem_trava(self, resumo):
        """A corrida foi ADIANTE — parou na VPN, e nao no cadeado.

        `VPN_NOT_ITALY` e a prova de que o cadeado foi atravessado: e o passo
        imediatamente a seguir a ele, e acontece com `--simulate-vpn DE` sem
        tocar em fonte nenhuma.
        """
        self.assertNotEqual("SKIPPED_LOCK_HELD", resumo["RUN_STATE"],
                            "a corrida parou no cadeado: %s" % resumo.get("reason"))
        self.assertEqual("VPN_NOT_ITALY", resumo.get("reason"))
        self.assertEqual(0, resumo["SOURCE_ATTEMPTED"])

    # ---------- 1 ----------
    def test_sem_cadeado_a_corrida_segue_e_o_cadeado_e_solto(self):
        resumo = self.correr_o_agendado()
        self.sem_trava(resumo)
        self.assertEqual("NOVO", resumo["CADEADO"]["ESTADO"],
                         "o registo nao diz como o cadeado foi obtido")
        self.assertFalse(os.path.exists(self.caminho()),
                         "o cadeado proprio nao foi solto no fim da corrida")
        self.assertEqual([], self.preservados())

    # ---------- 2 ----------
    def test_cadeado_de_processo_vivo_e_respeitado(self):
        pid = self.filho_vivo()
        corpo = json.dumps({"pid": pid, "at": "2026-09-28T11:00:00.000Z", "host": self.host})
        self.escrever_cadeado(corpo)

        resumo = self.correr_o_agendado()

        self.assertEqual("SKIPPED_LOCK_HELD", resumo["RUN_STATE"],
                         "uma segunda instancia arrancou com a primeira viva: %s" % resumo.get("reason"))
        self.assertEqual("RESPEITADO_PID_VIVO", resumo["CADEADO"]["ESTADO"])
        self.assertIs(True, resumo["CADEADO"]["DONO_VIVO"])
        self.assertEqual(pid, resumo["CADEADO"]["DONO_PID"])
        self.assertEqual(0, resumo["SOURCE_ATTEMPTED"])
        self.assertNotEqual("FAILED", resumo["RUNNER_HEALTH"],
                            "corredor marcado como quebrado por causa de uma trava ocupada")
        # o cadeado da outra instancia fica INTACTO: nao se assume, nao se renomeia
        self.assertEqual(corpo, self.ler(self.caminho()))
        self.assertEqual([], self.preservados(), "assumiu-se um cadeado de processo VIVO")

    # ---------- 3 ----------
    def test_cadeado_de_processo_morto_e_assumido_com_prova_preservada(self):
        pid = self.filho_morto()
        corpo = json.dumps({"pid": pid, "at": "2026-09-24T19:00:00.000Z", "host": self.host})
        self.escrever_cadeado(corpo)

        resumo = self.correr_o_agendado()

        self.sem_trava(resumo)
        self.assertEqual("ASSUMIDO", resumo["CADEADO"]["ESTADO"])
        self.assertIs(False, resumo["CADEADO"]["DONO_VIVO"])
        self.assertEqual(pid, resumo["CADEADO"]["DONO_PID"])
        # a prova do que estava preso sobrevive, com o pid dentro do nome
        preservado = resumo["CADEADO"]["PRESERVADO_EM"]
        self.assertTrue(preservado, "assumiu sem guardar o cadeado antigo")
        nome = os.path.basename(preservado)
        self.assertTrue(nome.startswith(PRESERVADO))
        self.assertIn("PID%d-MORTO" % pid, nome)
        self.assertIn(nome, self.preservados())
        self.assertEqual(corpo, open(preservado, encoding="utf-8").read(),
                         "o cadeado antigo foi alterado: deixou de ser prova")
        # o cadeado antigo NAO foi apagado, e o proprio foi solto no fim
        self.assertFalse(os.path.exists(self.caminho()))

    # ---------- 4 ----------
    def test_cadeado_vazio_e_recente_e_respeitado(self):
        self.escrever_cadeado("")          # o instante em que o processo morreu entre criar e escrever

        resumo = self.correr_o_agendado()

        self.assertEqual("SKIPPED_LOCK_HELD", resumo["RUN_STATE"])
        self.assertEqual("RESPEITADO_ILEGIVEL_RECENTE", resumo["CADEADO"]["ESTADO"])
        self.assertEqual([], self.preservados(),
                         "um cadeado ilegivel RECENTE foi assumido — a idade nao foi respeitada")

    # ---------- 5 ----------
    def test_cadeado_ilegivel_e_velho_e_assumido(self):
        self.escrever_cadeado("isto nao e um cadeado", idade_min=VELHO_MIN)

        resumo = self.correr_o_agendado()

        self.sem_trava(resumo)
        self.assertEqual("ASSUMIDO", resumo["CADEADO"]["ESTADO"])
        self.assertGreaterEqual(resumo["CADEADO"]["IDADE_MIN"], MAX_IDADE_DE_CORRIDA_MIN)
        nome = os.path.basename(resumo["CADEADO"]["PRESERVADO_EM"])
        self.assertIn("ILEGIVEL", nome)
        self.assertEqual("isto nao e um cadeado",
                         self.ler(os.path.join(self.ops, nome)))

    # ---------- 6 ----------
    def test_cadeado_de_outro_host_nao_se_mede_daqui(self):
        pid = self.filho_vivo()
        corpo = json.dumps({"pid": pid, "at": "2026-09-28T11:00:00.000Z",
                            "host": "UMA-MAQUINA-QUE-NAO-E-ESTA"})
        self.escrever_cadeado(corpo)

        resumo = self.correr_o_agendado()

        self.assertEqual("SKIPPED_LOCK_HELD", resumo["RUN_STATE"],
                         "um pid de outra maquina foi dado como morto — NAO SEI nao e MORTO")
        self.assertEqual("RESPEITADO_DONO_NAO_SEI_RECENTE", resumo["CADEADO"]["ESTADO"])
        self.assertIsNone(resumo["CADEADO"]["DONO_VIVO"])
        self.assertEqual(corpo, self.ler(self.caminho()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
