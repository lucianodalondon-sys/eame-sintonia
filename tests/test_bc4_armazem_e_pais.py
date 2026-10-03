# -*- coding: utf-8 -*-
"""BC4 — A CORRIDA DA SALA REAL GUARDA OS BYTES NO ARMAZEM DA SALA, E SABE DE QUE PAIS E A FONTE.

Medido na micro real da BC4 (24/09/2026, linha instalada 8eec2e2a, Sala real
127.0.0.1:54330): IT-T10-018, IT-T7-033 e IT-T2-034 entraram na Sala (+3), mas

  1. os bytes das 4 materias cairam em `<arvore do bot>/XX/` — residuo de
     medicao, ignorado pelo Git, e que a suite ja apagou uma vez (BC2, 20/09).
     O conserto de 20/09 (GARGALOS-BC2, 356b1b3c) nunca chegou a esta linha;
  2. as corridas nasceram `XX-T..` com `source_country = NAO_SEI`, porque o
     instrumento da micro nao punha o pais no pedido.

O pais vem da IDENTIDADE da fonte — o SOURCE_ID do Atlas, `IT-T<n>-<seq>` —
e nunca do egresso. O egresso medido continua a ser registado AO LADO (o
coletor escreve VPN_COUNTRY/EGRESS_IP no livro de corridas):

    VPN_LOCATION != SOURCE_LOCATION != FACT_LOCATION.
"""
import inspect
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
from guarda import preservar_coleta as pc  # noqa: E402
from orquestrador import persistencia  # noqa: E402

import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location(
    "micro_coleta_bc4", os.path.join(RAIZ, "scripts", "micro_coleta", "micro_coleta.py"))
MC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MC)

VARIAVEL_DA_RAIZ = "SINTONIA_ARMAZEM_RAIZ"
MARCADOR = "ARMAZEM_OPERACIONAL.json"
OPERACIONAL_OK = "postgresql://postgres:x@127.0.0.1:54330/sala_italia"


def _operacional_conhecido():
    return not persistencia.porque_nao_e_operacional(OPERACIONAL_OK)


class APersistenciaOperacionalExigeORaizDosBytes(unittest.TestCase):

    def setUp(self):
        if not _operacional_conhecido():
            self.skipTest("a allowlist operacional desta arvore nao conhece 54330/sala_italia")

    def test_operacional_sem_raiz_nao_nasce(self):
        env = {persistencia.VARIAVEL_OPERACIONAL: OPERACIONAL_OK}
        recusa = getattr(pc, "ArmazemOperacionalSemRaiz", None)
        self.assertIsNotNone(recusa, "o dono dos bytes nao tem a recusa ArmazemOperacionalSemRaiz")
        with self.assertRaises(recusa):
            persistencia.dependencias_do_runtime(env)

    def test_operacional_com_raiz_entrega_a_raiz_ao_runtime(self):
        raiz = tempfile.mkdtemp(prefix="armazem-bc4-")
        self.addCleanup(shutil.rmtree, raiz, True)
        env = {persistencia.VARIAVEL_OPERACIONAL: OPERACIONAL_OK, VARIAVEL_DA_RAIZ: raiz}
        rt = persistencia.dependencias_do_runtime(env)
        self.assertEqual(rt.ESTADO, persistencia.OPERACIONAL)
        self.assertEqual(os.path.normpath(getattr(rt, "raiz_do_armazem", "") or ""),
                         os.path.normpath(raiz))
        self.assertEqual(rt.para_json().get("ARMAZEM_RAIZ"), rt.raiz_do_armazem)
        self.assertTrue(os.path.isfile(os.path.join(raiz, MARCADOR)))


class APortaDaLinhaDeComando(unittest.TestCase):

    def test_main_recusa_sem_raiz_e_passa_a_raiz_a_corrida(self):
        """main() apanha a recusa e sai 2 — nunca corre sem armazem."""
        fonte = Path(RAIZ, "orquestrador", "orquestrador.py").read_text(encoding="utf-8")
        corpo = fonte.split("def main()", 1)[1]
        recusas = corpo.split("persistencia.dependencias_do_runtime()", 1)[1].split("return 2", 1)[0]
        self.assertIn("ArmazemOperacionalSemRaiz", recusas)
        self.assertIn("raiz_do_armazem=runtime.raiz_do_armazem", corpo)


def _payload():
    loja = os.path.join(RAIZ, "data", "collection-store", "italy")
    for base, _, fs in os.walk(loja):
        for f in sorted(fs):
            if not f.endswith(".json"):
                return os.path.relpath(os.path.join(base, f), RAIZ).replace(os.sep, "/")
    return None


def _ficheiros(raiz):
    if not os.path.isdir(raiz):
        return set()
    return {os.path.relpath(os.path.join(b, f), raiz)
            for b, _, fs in os.walk(raiz) for f in fs}


class ACorridaGuardaOsBytesNaRaizQueLheDao(unittest.TestCase):
    """A rota inteira, sem rede: a colheita de uma corrida vai a porta e o
    bruto aterra na raiz entregue — e NAO em `<arvore>/XX/`."""

    def setUp(self):
        import admissao
        import italy_executor as adapter
        import orquestrador as orq
        from pedido import de_uma_frase
        self.orq, self.frase = orq, de_uma_frase
        pay = _payload()
        if not pay:
            self.skipTest("sem byte real no armazem")
        self.ops = tempfile.mkdtemp(prefix=".corrida-bc4-", dir=os.path.join(RAIZ, "data"))
        self.addCleanup(shutil.rmtree, self.ops, True)
        antes = os.environ.get("ITALY_OPS_ROOT")
        os.environ["ITALY_OPS_ROOT"] = self.ops
        self.addCleanup(lambda: os.environ.__setitem__("ITALY_OPS_ROOT", antes)
                        if antes else os.environ.pop("ITALY_OPS_ROOT", None))
        self.addCleanup(shutil.rmtree, os.path.join(RAIZ, adapter.BALCAO), True)
        self.residuo = os.path.join(RAIZ, "XX")
        self.residuo_antes = _ficheiros(self.residuo)
        self.armazem = tempfile.mkdtemp(prefix="armazem-oper-bc4-")
        self.addCleanup(shutil.rmtree, self.armazem, True)
        self.livro = admissao.LIVRO
        try:
            conteudo = Path(self.livro).read_text(encoding="utf-8")
        except OSError:
            conteudo = None
        self.addCleanup(self._repor, conteudo)
        self.run_id = "CORRIDA-BC4-0001"
        caminho = os.path.join(self.ops, adapter.LIVRO)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "RUN_ID": self.run_id, "SOURCE_ID": "IT-T2-002",
                "DOCUMENT_ID": "ARPAV_BC4", "RAW_PATH": pay,
                "CAPTURED_AT": "2026-09-24T00:00:00Z",
                "texto": "Bollettino agrometeorologico con dati di campo."}) + "\n")
        adapter.colher(self.run_id, ops_root=self.ops)

    def _repor(self, conteudo):
        # o residuo que ESTE teste deixou (se o conserto faltar) sai; o que ja
        # la estava fica — nunca rmtree a seco em <arvore>/XX
        for rel in _ficheiros(self.residuo) - self.residuo_antes:
            os.remove(os.path.join(self.residuo, rel))
        if conteudo is None:
            if os.path.exists(self.livro):
                os.remove(self.livro)
        else:
            Path(self.livro).write_text(conteudo, encoding="utf-8")

    def test_o_bruto_aterra_no_armazem_entregue_e_nao_no_residuo(self):
        self.assertIn("raiz_do_armazem", inspect.signature(self.orq.correr).parameters,
                      "correr() nao recebe a raiz dos bytes")
        pedido = self.frase("colete clima e tempo")
        pedido.filtros["universo"] = "T2"          # a rota exige o universo do PEDIDO
        recibo = self.orq.correr(pedido, so_a_porta=True,
                                 colheita_da_corrida=self.run_id,
                                 raiz_do_armazem=self.armazem)
        self.assertEqual(recibo["INGRESSO"]["PRESERVADOS"], 1, recibo["INGRESSO"])
        no_armazem = [f for f in _ficheiros(self.armazem) if f != MARCADOR]
        self.assertTrue(no_armazem, "o bruto nao aterrou no armazem entregue")
        self.assertEqual(self.residuo_antes, _ficheiros(self.residuo),
                         "a corrida escreveu no residuo <arvore>/XX/")


class OPaisVemDaIdentidadeDaFonte(unittest.TestCase):

    def setUp(self):
        if not hasattr(MC, "pais_de"):
            self.fail("micro_coleta nao sabe o pais da fonte (pais_de)")

    def test_o_pais_e_o_prefixo_do_source_id_do_atlas(self):
        self.assertEqual(MC.pais_de("IT-T10-018"), "IT")
        self.assertEqual(MC.pais_de("IT-T2-034"), "IT")
        self.assertEqual(MC.pais_de("FR-T3-001"), "FR")

    def test_sem_identidade_valida_nao_se_inventa(self):
        for s in ("CAND-0250", "XX-T3-001", "IT-X3-001", "", None, "it-t3-001"):
            with self.subTest(s=s):
                self.assertIsNone(MC.pais_de(s))

    def test_o_comando_da_micro_declara_o_pais_da_fonte(self):
        cmd = MC.comando("IT-T10-018")
        i = cmd.index("pais=IT")
        self.assertEqual(cmd[i - 1], "--filtro")

    def test_o_pais_nao_vem_do_egresso(self):
        """Uma fonte francesa medida por uma saida italiana continua francesa."""
        self.assertIn("pais=FR", MC.comando("FR-T3-001"))
        self.assertNotIn("egresso", inspect.signature(MC.comando).parameters)

    def test_o_run_id_nasce_com_o_pais_do_pedido(self):
        import orquestrador as orq
        from pedido import de_uma_frase
        cmd = MC.comando("IT-T10-018")
        p = de_uma_frase(" ".join(a for a in cmd[2:] if not a.startswith("--")))
        for i, a in enumerate(cmd):
            if a == "--filtro":
                k, v = cmd[i + 1].split("=", 1)
                p.filtros[k] = v
        self.assertTrue(orq.novo_run_id(p).startswith("IT-T10-"), orq.novo_run_id(p))


class AMicroRecusaSemArmazem(unittest.TestCase):

    def test_precondicoes_pedem_a_raiz_dos_bytes(self):
        env = {"SINTONIA_COLLECTION_DSN": "x", "SINTONIA_SALA_DSN": "x",
               "SINTONIA_SALA_BACKEND": "POSTGRES", "SINTONIA_PSQL_EXE": "x"}
        self.assertIn(VARIAVEL_DA_RAIZ, " ".join(MC.precondicoes(env)))
        env[VARIAVEL_DA_RAIZ] = tempfile.gettempdir()
        self.assertEqual([], MC.precondicoes(env))


if __name__ == "__main__":
    unittest.main()
