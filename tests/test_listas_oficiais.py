# -*- coding: utf-8 -*-
"""PESQ-FORA-DO-MUR · listas oficiais da FEM/CREA/CNR por rodadas, sem rede: teto, robots, so alvos, CNR fechado."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "seguir_pesquisadores"))
import listas_oficiais as L   # noqa: E402
import fora_do_mur as FM      # noqa: E402

FX = RAIZ / "ferramentas" / "seguir_pesquisadores" / "fixtures"
ALVOS = FX / "ALVOS-LISTAS.json"


def rodar(saida, casa, *extra):
    return L.main(["x", "--seco", "--fixtures=%s" % FX, "--casa=%s" % casa, "--alvos=%s" % ALVOS,
                   "--saida=%s" % saida] + list(extra))


def estado(saida, casa):
    return json.loads((Path(saida) / ("ESTADO-%s.json" % casa)).read_text(encoding="utf-8"))


class Casa(unittest.TestCase):
    def test_casa_pela_instituicao_da_obra(self):
        self.assertEqual(("FEM", "FEM", "CERTA"), FM.casa_de("Fondazione Edmund Mach"))
        self.assertEqual(("CNR", "IPSP", "CERTA"), FM.casa_de("Institute for Sustainable Plant Protection"))
        self.assertEqual("PROVAVEL", FM.casa_de("Cereal Research Centre")[2])
        self.assertIsNone(FM.casa_de("University of Padua"))

    def test_so_o_alvo_unico_pelo_texto_da_ligacao(self):
        al = json.loads(ALVOS.read_text(encoding="utf-8"))["PESSOAS"]
        self.assertEqual("Gianfranco Anfora", L.casa_o_alvo("Anfora Gianfranco", al)["NOME"])
        self.assertIsNone(L.casa_o_alvo("M. Bianchi", al))          # Marco e Marta: ambiguo
        self.assertIsNone(L.casa_o_alvo("Luca Verdi", al))          # nao e alvo
        self.assertIsNone(L.casa_o_alvo("Paolo Anfora", al))        # inicial diferente


class Rodadas(unittest.TestCase):
    def test_fem_descobre_a_lista_e_respeita_teto_e_robots(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(0, rodar(d, "FEM"))
            e = estado(d, "FEM")
            reg = json.loads(json.dumps(e))
            self.assertEqual(["https://www.fmach.it/persone/tonina"], [x["URL"] for x in reg["FILA"]])   # ficou pelo teto
            feitos = {f["URL"]: f for f in e["FEITOS"]}
            self.assertEqual("ROBOTS_OU_NAO_LIDO", feitos["https://www.fmach.it/riservato/staff"]["MOTIVO"])
            self.assertNotIn("https://www.fmach.it/persone/verdi", feitos)     # nao e alvo: nao se abre
            self.assertEqual(0, rodar(d, "FEM"))                                # 2.a rodada: tira o pendente
            e = estado(d, "FEM")
            self.assertEqual([], e["FILA"])
            por = {p["PESSOA"]: p for p in e["PERFIS"]}
            self.assertEqual({"Gianfranco Anfora", "Claudio Ioriatti", "Lorenzo Tonina"}, set(por))
            self.assertEqual(["LINKEDIN_PERFIL"], [x["PLATAFORMA"] for x in por["Gianfranco Anfora"]["NAO_ENTRAM"]])
            self.assertFalse(any("mailto" in x["URL"] or "tel:" in x["URL"]
                                 for p in e["PERFIS"] for x in p["CANAIS"] + p["NAO_ENTRAM"]))

    def test_teto_contado_em_cada_rodada(self):
        with tempfile.TemporaryDirectory() as d:
            rodar(d, "FEM")
            doc = json.loads((Path(d) / "RODADA-FEM-01" / "PEDIDOS.json").read_text(encoding="utf-8"))
            feitos = [x for x in doc["PEDIDOS"] if x["RESULTADO"] in ("OK", "FALHA")]
            self.assertEqual(5, len(feitos))                             # robots + 4 paginas
            self.assertEqual({"fmach.it": 5}, doc["POR_DOMINIO"])
            self.assertEqual("https://www.fmach.it/robots.txt", feitos[0]["URL"])

    def test_crea_ambiguo_nao_se_abre_e_falha_fica_escrita(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(0, rodar(d, "CREA"))
            e = estado(d, "CREA")
            urls = {f["URL"]: f["RESULTADO"] for f in e["FEITOS"]}
            self.assertNotIn("https://www.crea.gov.it/web/difesa-e-certificazione/-/marco-bianchi", urls)
            self.assertEqual("NAO_ABERTA", urls["https://www.crea.gov.it/web/olivicoltura-frutticoltura-e-agrumicoltura"])
            self.assertEqual(["Mario Rossi"], [p["PESSOA"] for p in e["PERFIS"]])

    def test_cnr_fechado_sem_liberacao_e_rede_so_autorizada(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(2, L.main(["x", "--rodada", "--autorizado", "--casa=CNR", "--alvos=%s" % ALVOS, "--saida=%s" % d]))
            self.assertEqual(2, L.main(["x", "--rodada", "--casa=FEM", "--alvos=%s" % ALVOS, "--saida=%s" % d]))
            self.assertEqual([], list(Path(d).iterdir()))

    def test_candidatas_pela_porta_numa_copia(self):
        with tempfile.TemporaryDirectory() as d:
            rodar(d, "FEM"), rodar(d, "FEM"), rodar(d, "CREA")
            fila = Path(d) / "FILA.json"
            fila.write_text(json.dumps({"CANDIDATAS": []}), encoding="utf-8")
            r = L.candidatar(sorted(Path(d).glob("ESTADO-*.json")), fila)
            linhas = json.loads(fila.read_text(encoding="utf-8"))["CANDIDATAS"]
            self.assertEqual(5, len(linhas))
            self.assertFalse(any("/in/" in x["URL"] for x in linhas))
            self.assertTrue(all(x["PAIS"] == "IT" and x["PARA_QUE_SERVE"].startswith("D85") for x in linhas))
            self.assertEqual(2, len(r["NAO_ENTRAM"]))


if __name__ == "__main__":
    unittest.main()
