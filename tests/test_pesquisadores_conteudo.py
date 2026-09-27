# -*- coding: utf-8 -*-
"""D92 PESQUISADORES-CONTEUDO · OpenAlex por ORCID (lote 50, cursor, teto) e grupos/labs com feed. Sem rede."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "seguir_pesquisadores"))
import contador as CT          # noqa: E402
import grupos_feeds as G       # noqa: E402
import openalex_conteudo as OA  # noqa: E402
import seguir as S             # noqa: E402


# NENHUM teste sai a rede (a guarda de 26/09)
def _sem_rede(*a, **k):
    raise RuntimeError("rede pedida dentro de um teste")


S.Transporte._urllib = staticmethod(_sem_rede)
S.portao = lambda *a, **k: False

FX = RAIZ / "ferramentas" / "seguir_pesquisadores" / "fixtures"


def _obra(i, doi, resumo=True, pdf=False):
    return {"id": "https://openalex.org/W%d" % i, "doi": doi, "title": "t%d" % i, "publication_date": "2025-01-01",
            "abstract_inverted_index": {"vite": [0]} if resumo else None,
            "best_oa_location": {"pdf_url": "https://x/p.pdf"} if pdf else None, "open_access": {"is_oa": pdf}}


class OpenAlex(unittest.TestCase):
    def montar(self, d, por_pedido=2):
        d = Path(d)
        (d / "lm").mkdir()
        (d / "lm" / "ESTADO-LISTA-MESTRA.json").write_text(json.dumps({"ORCID_ACHADOS": {
            "A|X": ["0000-0000-0000-0901"], "B|Y": ["0000-0000-0000-0902"], "C|Z": ["0000-0000-0000-0903", "0000-0000-0000-0904"]}}),
            encoding="utf-8")
        OA.POR_PEDIDO = por_pedido
        saida = d / "s"
        OA.main(["x", "--plano", "--lista-mestra=%s" % (d / "lm"), "--pessoas=%s" % (d / "p.json"), "--saida=%s" % saida])
        return saida

    def setUp(self):
        self.velho = OA.POR_PEDIDO

    def tearDown(self):
        OA.POR_PEDIDO = self.velho

    def test_lote_ambiguo_fora_teto_cursor_e_formato_do_executor(self):
        with tempfile.TemporaryDirectory() as d:
            pessoas = json.loads((FX / "PESSOAS.json").read_text(encoding="utf-8"))
            (Path(d) / "p.json").write_text(json.dumps({"PESSOAS": pessoas}), encoding="utf-8")
            saida = self.montar(d)
            e = json.loads((saida / "ESTADO-OPENALEX.json").read_text(encoding="utf-8"))
            self.assertNotIn("0000-0000-0000-0903", e["ORIGEM"])          # busca com 2 ORCID: ambiguo, fora
            self.assertNotIn("0000-0000-0000-0004", e["ORIGEM"])          # prioritario com 2 ORCID: fora
            self.assertEqual(7, len(e["ORIGEM"]))                         # 2 da lista-mestra + 5 prioritarios
            resp = {}
            for lote in e["AUTORES"]["LOTES"]:
                resp[OA.url_autores(lote)] = {"meta": {"count": len(lote)}, "results": [
                    {"id": "https://openalex.org/A%s" % o[-3:], "orcid": "https://orcid.org/" + o, "display_name": o,
                     "last_known_institutions": [{"display_name": "Uni"}], "topics": []} for o in lote]}
            g1 = e["OBRAS"]["GRUPOS"][0]["ORCIDS"]
            resp[OA.url_obras(g1, "*")] = {"meta": {"count": 3, "next_cursor": "C2"}, "results": [_obra(1, "https://doi.org/10.1/a"), _obra(2, "https://doi.org/10.1/b", False, True)]}
            resp[OA.url_obras(g1, "C2")] = {"meta": {"count": 3, "next_cursor": None}, "results": [_obra(3, "https://doi.org/10.1/c", False)]}
            for g in e["OBRAS"]["GRUPOS"][1:]:
                resp[OA.url_obras(g["ORCIDS"], "*")] = {"meta": {"count": 0, "next_cursor": None}, "results": []}
            fx = Path(d) / "fx"
            fx.mkdir()
            (fx / "RESPOSTAS-OPENALEX.json").write_text(json.dumps(resp), encoding="utf-8")
            base = ["x", "--rodada", "--seco", "--fixtures=%s" % fx, "--saida=%s" % saida]
            self.assertEqual(0, OA.main(base))
            e = json.loads((saida / "ESTADO-OPENALEX.json").read_text(encoding="utf-8"))
            r1 = e["RODADAS"][0]
            self.assertEqual(5, r1["PEDIDOS_OPENALEX"])                   # 4 lotes de autores + 1 pagina de obras
            self.assertEqual((4, 1), (r1["AUTORES_LOTES"], r1["OBRAS_PAGINAS"]))
            self.assertEqual("C2", e["OBRAS"]["GRUPOS"][0]["CURSOR"])     # o cursor fica para a rodada seguinte
            self.assertEqual(0, OA.main(base))
            e = json.loads((saida / "ESTADO-OPENALEX.json").read_text(encoding="utf-8"))
            self.assertTrue(all(g["FIM"] for g in e["OBRAS"]["GRUPOS"]))
            ped = json.loads((saida / "RODADA-02" / "PEDIDOS.json").read_text(encoding="utf-8"))["PEDIDOS"]
            self.assertFalse([x for x in ped if "orcid.org" in x["URL"] and "openalex" not in x["URL"]])   # nunca o ORCID
            self.assertFalse([x for x in ped if x["URL"].endswith("robots.txt")])                         # D91
            self.assertTrue(sorted(p.name for p in saida.glob("openalex-PESQUISADORES-g1-p*.json")))       # o nome do executor T6
            m = OA.medir(saida)
            self.assertEqual((3, 1, 1, 2), (m["OBRAS_DISTINTAS"], m["COM_RESUMO"], m["COM_PDF_ABERTO"], m["SO_TITULO"]))
            self.assertEqual(7, m["AUTORES_ACHADOS"])

    def test_rede_so_autorizada(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "p.json").write_text(json.dumps({"PESSOAS": []}), encoding="utf-8")
            saida = self.montar(d)
            self.assertEqual(2, OA.main(["x", "--rodada", "--saida=%s" % saida]))

    def test_openalex_sem_teto_de_24h_mas_escrito(self):
        with tempfile.TemporaryDirectory() as d:
            c = CT.Contador24h(Path(d) / "C.json")
            self.assertTrue(all(c.reservar("openalex.org", "u%d" % i)[0] for i in range(12)))
            self.assertEqual(12, len(c.na_janela("openalex.org")))
            self.assertFalse(all(c.reservar("orcid.org", "u%d" % i)[0] for i in range(6)))   # o ORCID continua 5/24 h
            self.assertEqual(0, c.marcar_gasto("openalex.org", c._agora(), "x"))


class Grupos(unittest.TestCase):
    def rodar(self, d, *extra):
        saida = Path(d) / "g"
        G.main(["x", "--plano", "--fila=%s" % (FX / "FILA-GRUPOS.json"), "--pessoas=%s" % (FX / "PESSOAS.json"),
                "--fora=%s" % (FX / "ALVOS-LISTAS.json"), "--saida=%s" % saida])
        rc = G.main(["x", "--rodada", "--seco", "--fixtures=%s" % FX, "--saida=%s" % saida] + list(extra))
        return rc, saida, json.loads((saida / "ESTADO-GRUPOS.json").read_text(encoding="utf-8"))

    def test_feed_declarado_grupos_robots_e_cnr(self):
        with tempfile.TemporaryDirectory() as d:
            rc, saida, e = self.rodar(d)
            self.assertEqual(0, rc)
            por = {g["URL"]: g for g in e["GRUPOS"]}
            lab = por["https://www.fmach.it/ricerca/lab-entomologia"]
            self.assertEqual(["https://www.fmach.it/ricerca/lab-entomologia/feed/"], lab["FEEDS"])
            self.assertEqual(["anfora"], lab["PESQUISADORES_CITADOS"])    # Ioriatti nao e alvo (sem obra recente)
            self.assertEqual(["YOUTUBE"], [c["PLATAFORMA"] for c in lab["CANAIS"]])
            self.assertEqual(["LINKEDIN_PERFIL"], [c["PLATAFORMA"] for c in lab["NAO_ENTRAM"]])
            self.assertEqual([], por["https://www.fmach.it/ricerca/unita-patologia"]["FEEDS"])   # nada se adivinha
            self.assertEqual(["https://www.fmach.it/rss.xml"], e["FEEDS_DAS_SEMENTES"]["https://www.fmach.it/"])
            feitos = {f["URL"]: f for f in e["FEITOS"]}
            self.assertNotIn("https://www.altro.it/research-group", feitos)          # outra casa: nao se segue
            self.assertNotIn("https://www.altro.it/research-group", [x["URL"] for x in e["FILA"]])
            self.assertEqual("ROBOTS_OU_NAO_LIDO", feitos["https://www.fmach.it/riservato/lab"]["MOTIVO"])
            self.assertEqual("ROBOTS_OU_NAO_LIDO", feitos["https://www.agr.unipi.it/"]["MOTIVO"])
            ped = json.loads((saida / "RODADA-01" / "PEDIDOS.json").read_text(encoding="utf-8"))
            self.assertLessEqual(max(ped["POR_DOMINIO"].values()), 5)
            self.assertNotIn("cnr.it", ped["POR_DOMINIO"])                           # CNR fechado
            self.assertIn("https://www.ibbr.cnr.it/", [x["URL"] for x in e["FILA"]])  # fica na fila

    def test_candidatas_numa_copia(self):
        with tempfile.TemporaryDirectory() as d:
            _, saida, e = self.rodar(d)
            fila = Path(d) / "FILA.json"
            fila.write_text(json.dumps({"CANDIDATAS": []}), encoding="utf-8")
            G.candidatar(e, fila)
            linhas = json.loads(fila.read_text(encoding="utf-8"))["CANDIDATAS"]
            self.assertEqual({"CIENCIA", "YOUTUBE", "OUTRO"}, {x["TIPO"] for x in linhas})
            self.assertFalse(any("/in/" in x["URL"] or "mailto" in x["URL"] for x in linhas))
            self.assertTrue(any("FEED_DECLARADO=https://www.fmach.it/ricerca/lab-entomologia/feed/" in x["NOTA"] for x in linhas))


if __name__ == "__main__":
    unittest.main()
