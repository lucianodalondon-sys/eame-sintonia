#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BG-06 — O COLETOR ITALIANO NÃO TEM CONJUNTO POR OMISSÃO.

    py -m unittest tests.test_fontes_explicitas_no_coletor

O DEFEITO QUE ISTO FECHA
------------------------
`PILOT_SOURCES` tem SETE entradas, e a sétima — `IT-T3-005` — tem ZERO menções
no Atlas: é candidata (`status NEW`, `verdict NAO SEI`). Uma corrida sem
fontes nomeadas colhia as sete, e portanto colhia a candidata, por omissão.

    A LISTA DO QUE O COLETOR SABE PERCORRER
    NÃO É A LISTA DO QUE UMA CORRIDA DEVE COLHER.

O que muda: quem colhe NOMEIA as fontes. `executarRodada` sem `apenas` levanta
`FONTES_AUSENTES`; a CLI sem `--fonte=` sai com 2. `PILOT_SOURCES` continua a
existir com as sete — é CAPACIDADE (serve para recusar FONTE_DESCONHECIDA), e
capacidade não é aprovação:

    HISTORY EXISTS != SOURCE APPROVED.

O corredor recorrente (`italy_recurrent_collect.mjs`) não muda: ele já nomeia
as fontes por declaração explícita de perfil, que é outra decisão, de outra
missão. Este teste também prova que essa declaração continua explícita.

Nenhum caso aqui vai à rede: todos são recusados ANTES de qualquer aquisição.
"""
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLETOR = os.path.join(RAIZ, "coleta", "italy_pilot_collect.mjs")

AS_SEIS_DO_PILOTO = ("IT-T4-001", "IT-T3-002", "IT-T3-008",
                     "IT-T3-010", "IT-T2-002", "IT-T2-004")


def _node(driver, ops_root, timeout=120):
    env = dict(os.environ, ITALY_OPS_ROOT=ops_root)
    return subprocess.run(["node", "--input-type=module", "-e", driver],
                          cwd=RAIZ, capture_output=True, text=True,
                          timeout=timeout, env=env)


def _cli(args, ops_root, timeout=120):
    env = dict(os.environ, ITALY_OPS_ROOT=ops_root)
    return subprocess.run(["node", COLETOR] + args, cwd=RAIZ,
                          capture_output=True, text=True, timeout=timeout,
                          env=env)


def _driver_apenas(valor_js):
    return """
import { pathToFileURL } from "node:url";
const { executarRodada } = await import(pathToFileURL(%s).href);
try {
  await executarRodada({ runId: "BG06-PROVA-0001", apenas: %s });
  console.log("NAO_RECUSOU");
} catch (e) {
  console.log("RECUSOU: " + String(e.message).slice(0, 60));
}
""" % (json.dumps(COLETOR.replace("\\", "/")), valor_js)


class SemNomeNaoHaColheita(unittest.TestCase):

    def setUp(self):
        self.ops = tempfile.mkdtemp(prefix="bg06-")
        self.addCleanup(shutil.rmtree, self.ops, True)

    def _livro_vazio(self):
        p = os.path.join(self.ops, "data", "collection-ledger", "italy",
                         "observations.ndjson")
        return (not os.path.exists(p)) or not io.open(
            p, encoding="utf-8").read().strip()

    def test_1_executarRodada_sem_apenas_levanta_FONTES_AUSENTES(self):
        r = _node(_driver_apenas("null"), self.ops)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        self.assertIn("RECUSOU: FONTES_AUSENTES", r.stdout)
        self.assertTrue(self._livro_vazio(),
                        "a recusa nao pode deixar observacao no livro")

    def test_2_lista_vazia_tambem_recusa(self):
        r = _node(_driver_apenas("[]"), self.ops)
        self.assertIn("RECUSOU: FONTES_AUSENTES", r.stdout, r.stderr[-400:])

    def test_3_a_cli_sem_fonte_sai_com_2_e_nao_colhe(self):
        r = _cli(["--run-id=BG06-PROVA-0002"], self.ops)
        self.assertEqual(r.returncode, 2, r.stdout[-400:] + r.stderr[-400:])
        self.assertIn("FONTES_AUSENTES", r.stderr)
        self.assertTrue(self._livro_vazio())

    def test_4_fonte_desconhecida_continua_recusada_antes_da_rede(self):
        r = _cli(["--run-id=BG06-PROVA-0003", "--fonte=IT-T9-999"], self.ops)
        self.assertEqual(r.returncode, 2)
        self.assertIn("FONTE_DESCONHECIDA", r.stderr)
        self.assertTrue(self._livro_vazio())

    def test_5_as_seis_aprovadas_sao_elegiveis_na_capacidade(self):
        """Elegível = o coletor sabe percorrê-la. Não corre nada aqui."""
        fonte = io.open(COLETOR, encoding="utf-8").read()
        m = re.search(r"PILOT_SOURCES = (\[[^\]]*\])", fonte)
        capacidade = json.loads(m.group(1).replace("'", '"'))
        for sid in AS_SEIS_DO_PILOTO:
            self.assertIn(sid, capacidade, sid)

    def test_6_a_candidata_nao_foi_apagada_da_capacidade(self):
        """HISTORY EXISTS != SOURCE APPROVED — e apagar seria reescrever a
        historia: o corredor recorrente percorre-a por perfil explicito."""
        fonte = io.open(COLETOR, encoding="utf-8").read()
        self.assertIn('"IT-T3-005"', fonte)

    def test_7_o_corredor_recorrente_continua_a_nomear_por_perfil(self):
        corredor = io.open(os.path.join(RAIZ, "coleta",
                                        "italy_recurrent_collect.mjs"),
                           encoding="utf-8").read()
        self.assertIn("apenas: PROFILE.SOURCES", corredor,
                      "o corredor deixou de passar a lista explicita do perfil")

    def test_8_nao_ha_mais_queda_para_PILOT_SOURCES_no_runtime(self):
        """Mede o CÓDIGO, não os comentários — o comentário que explica o
        defeito antigo tem o direito de citá-lo."""
        fonte = io.open(COLETOR, encoding="utf-8").read()
        codigo = "\n".join(l for l in fonte.split("\n")
                           if not l.strip().startswith("//"))
        self.assertNotIn("?? PILOT_SOURCES", codigo,
                         "a queda por omissao voltou ao codigo executavel")
        self.assertIn("FONTES_AUSENTES", codigo,
                      "a recusa explicita sumiu")


if __name__ == "__main__":
    unittest.main()
