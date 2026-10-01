#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ENXERTO DO L3 NA CANDIDATA (coordenador 01/10, red team do bot Luciano) — as guardas, provadas NA ARVORE FINAL.

    python3 -m unittest tests.test_enxerto_l3_guardas

O enxerto junta claude/l3-radar-original-v1 @ 8bc3451df (a PONTA, nao b005b8606) a candidata
coord/servico-com-release @ a9d86ad69. Este teste nao reimplementa nenhuma guarda: chama as que vieram e prova que
continuam a morder, cada uma pelo seu dono:

  G1  leitor do Casco (italia-portale/client/sintonia-pote-casco.js, 84df3497c): recusa a forma do e97ce8b0,
      recusa PRODUCAO = true, aceita o K2 (os dois eixos);
  G2  ha UM leitor do pote no client (nada de leitor v2 duplicado) e o portale.html carrega esse;
  G3  gatilho do preview (portoes/publicar_preview_da_pasta.py, 2eecbf09d): worktree suja = RECUSADO_ARVORE_SUJA e
      nada publicado; a pasta lida e a DECLARADA no contrato, nunca um caminho escrito a mao no .cmd;
  G4  envelope (portoes/publicar_portal_sozinho.py, 0d726d501): pote DEMO / nao-cliente nunca se diz aprovado pelo
      dono; e o pote com os eixos (marca EXPERIMENTAL · PREVIEW_NAO_PRODUCAO) continua EXPERIMENTAL na promocao;
  G5  badge DEMO na barra (sintonia-pote-casco.js + portale.html) — o node do test_pote_no_casco (P12) corre aqui.

Pote do e97ce8b0 = POTE-SINTETICO-V2-UNICO com um objeto LIBERADO e sem eixos (a forma exata que o LAB reprovou).
Pote K2 = tests/fixtures/pote/POTE-SINTETICO-K2-EIXOS.json (gerado por pote_intelligence_casco.aplicar_eixos).
Tudo SINTETICO. Os potes reais medem-se fora do Git (ENTREGA-CASCO-ENXERTO-L3.md).
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "portoes"))
sys.path.insert(0, str(RAIZ))
import _gavetas  # noqa: E402,F401

import publicar_portal_sozinho as PUB          # noqa: E402
import publicar_preview_da_pasta as G           # noqa: E402

FIX = RAIZ / "tests" / "fixtures" / "pote"
CLIENT = RAIZ / "italia-portale" / "client"
NODE = shutil.which("node")

CONFERIR_JS = r"""
const fs = require('fs'), vm = require('vm');
const sb = vm.createContext({ document: { write: () => {} } });
sb.window = sb; sb.window.location = { search: '' };
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), sb);
const potes = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(potes.map((p) => sb.SINTONIA_POTE_CASCO.conferir(p))));
"""


def _ler(n):
    return json.loads((FIX / n).read_text(encoding="utf-8"))


def conferir_no_leitor(potes):
    r = subprocess.run([NODE, "-e", CONFERIR_JS, str(CLIENT / "sintonia-pote-casco.js")],
                       input=json.dumps(potes), capture_output=True, text=True, encoding="utf-8", timeout=60)
    if r.returncode:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


@unittest.skipUnless(NODE, "node nao encontrado")
class G1_OLeitorSegueOsEixos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        k2 = _ler("POTE-SINTETICO-K2-EIXOS.json")
        e97 = _ler("POTE-SINTETICO-V2-UNICO.json")
        e97["COMPARTIMENTOS"]["meeting"]["OBJETOS"][0]["LIBERACAO"] = "LIBERADO_PARA_CLIENTE"
        prod = copy.deepcopy(k2)
        prod["PRODUCAO"] = True
        cls.k2, cls.e97, cls.prod = conferir_no_leitor([k2, e97, prod])

    def test_aceita_o_k2(self):
        self.assertEqual(self.k2, [])

    def test_recusa_a_forma_do_e97ce8b0(self):
        self.assertTrue(any("K2" in v and "ao mesmo tempo" in v for v in self.e97), self.e97)

    def test_recusa_producao_true(self):
        self.assertTrue(any("PRODUCAO = false" in v for v in self.prod), self.prod)


class G2_UmLeitorSo(unittest.TestCase):
    def test_um_so_leitor_do_pote_no_client(self):
        quem = sorted(p.name for p in CLIENT.glob("*.js")
                      if re.search(r"window\.SINTONIA_POTE_CASCO\s*=", p.read_text(encoding="utf-8", errors="replace")))
        self.assertEqual(quem, ["sintonia-pote-casco.js"])

    def test_o_portal_carrega_esse_leitor_uma_vez(self):
        html = (CLIENT / "portale.html").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r'<script[^>]+src="sintonia-pote-casco\.js"', html)), 1)


class G3_AGuardaDaArvoreEDaPasta(unittest.TestCase):
    def test_os_testes_do_dono_que_provam_a_guarda_existem_e_correm_aqui(self):
        import tests.test_publicar_preview_da_pasta as T  # noqa: E402
        nomes = {n for c in vars(T).values() if isinstance(c, type) for n in dir(c) if n.startswith("test_")}
        for n in ("test_worktree_suja_nao_publica_e_fica_escrito", "test_a_pasta_da_tarefa_e_a_declarada_no_contrato",
                  "test_a_rodada_sem_pasta_le_a_declarada"):
            self.assertIn(n, nomes)
        with open(os.devnull, "w") as nul:
            r = unittest.TextTestRunner(stream=nul).run(unittest.defaultTestLoader.loadTestsFromModule(T))
        self.assertTrue(r.wasSuccessful(), [str(x[0]) for x in r.failures + r.errors])

    def test_o_cmd_da_tarefa_nao_traz_pasta_escrita_a_mao(self):
        cmd = (RAIZ / "portoes" / "casco_preview.cmd").read_text(encoding="utf-8", errors="replace")
        linhas = [l for l in cmd.splitlines() if "publicar_preview_da_pasta.py" in l and not l.lower().startswith("rem")]
        self.assertTrue(linhas)
        self.assertFalse(any("--pasta" in l or "--raiz" in l for l in linhas), linhas)

    def test_a_pasta_da_tarefa_esta_declarada_no_contrato(self):
        c = json.loads((RAIZ / "portoes" / "PUBLICACAO-AUTOMATICA.json").read_text(encoding="utf-8"))
        self.assertTrue(c["ENTREGA_DA_TAREFA"]["PASTA"])
        self.assertIn("RECUSADO_ARVORE_SUJA", c["ENTREGA_DA_TAREFA"]["ARVORE_LIMPA"])


class G4_DemoENaoClienteNuncaAprovados(unittest.TestCase):
    def setUp(self):
        self.c = PUB.carregar_contrato()

    def test_demo_nao_se_diz_aprovado(self):
        env = PUB.envelope(_ler("POTE-SINTETICO-PUBLICA-SOZINHO.json"), "0" * 64, self.c, "preview", "x")
        self.assertEqual(env["PROMOCAO"]["ESTADO"], "DEMO_SEM_APROVACAO_DO_DONO")
        self.assertIsNone(env["PROMOCAO"]["APROVADA_POR"])

    def test_pote_com_eixos_nao_se_diz_aprovado(self):
        env = PUB.envelope(_ler("POTE-SINTETICO-K2-EIXOS.json"), "0" * 64, self.c, "preview", "x")
        self.assertIn(env["PROMOCAO"]["ESTADO"], ("DEMO_SEM_APROVACAO_DO_DONO", "NAO_PARA_CLIENTE_SEM_APROVACAO_DO_DONO"))

    def test_pote_com_eixos_continua_experimental_na_promocao(self):
        k2 = json.loads(json.dumps(_ler("POTE-SINTETICO-K2-EIXOS.json")).replace("SINT-", "RUN-"))
        k2["CORRIDA_SINTETICA"] = False
        c = copy.deepcopy(self.c)
        c["REGRA_DE_PROMOCAO"]["ESTADO"] = "AGUARDA_DONO"
        L = PUB.conferir_pote(k2, c, "producao")
        prom = [l for l in L if l["ID"] == "C0_PROMOCAO"]
        self.assertTrue(prom and not prom[0]["PASS"], prom)


@unittest.skipUnless(NODE, "node nao encontrado")
class G5_BadgeDemo(unittest.TestCase):
    def test_a_barra_diz_demo_e_o_real_so_o_numero(self):
        r = subprocess.run([NODE, str(RAIZ / "tests" / "test_pote_no_casco.mjs")], capture_output=True, text=True,
                           encoding="utf-8", timeout=300, cwd=str(RAIZ))
        for nome in ("P12 pote de teste: Radar e Radar Futuro na barra dizem DEMO ao lado do numero",
                     "P12 pote real: a barra so o numero, sem DEMO"):
            self.assertIn("ok   " + nome, r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])


if __name__ == "__main__":
    unittest.main()
