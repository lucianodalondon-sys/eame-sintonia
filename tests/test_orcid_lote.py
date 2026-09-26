# -*- coding: utf-8 -*-
"""D90 §3.4 · ORCID em lote, <= 5 pedidos a orcid.org por 24 h; canario antes; pendentes ficam; sem rede."""
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "ferramentas" / "seguir_pesquisadores"))
import contador as CT        # noqa: E402
import listas_oficiais as L  # noqa: E402
import orcid_lote as O       # noqa: E402
import seguir as S           # noqa: E402

FX = RAIZ / "ferramentas" / "seguir_pesquisadores" / "fixtures"
T0 = datetime.fromisoformat("2026-09-27T08:00:00+00:00")


def correr(d, *passos, fx=FX):
    O.main(["x", "--plano", "--pessoas=%s" % (FX / "PESSOAS.json"), "--fora=%s" % (FX / "ALVOS-LISTAS.json"),
            "--saida=%s" % d])
    rcs = []
    for acao, horas in passos:
        rcs.append(O.main(["x", acao, "--seco", "--fixtures=%s" % fx, "--agora=%s" % (T0 + timedelta(hours=horas)).isoformat(),
                           "--saida=%s" % d]))
    return rcs, json.loads((Path(d) / "ESTADO-ORCID.json").read_text(encoding="utf-8"))


def orcid_em_24h(d):
    em = sorted(datetime.fromisoformat(p["EM"]) for p in
                json.loads((Path(d) / "CONTADOR-24H.json").read_text(encoding="utf-8"))["PEDIDOS"] if p["DOMINIO"] == "orcid.org")
    return max(sum(1 for y in em if x <= y < x + timedelta(hours=24)) for x in em)


class Contador(unittest.TestCase):
    def test_cinco_por_24h_e_depois_volta(self):
        with tempfile.TemporaryDirectory() as d:
            agora = [T0]
            c = CT.Contador24h(Path(d) / "C.json", agora=lambda: agora[0])
            self.assertTrue(all(c.reservar("orcid.org", "u%d" % i)[0] for i in range(5)))
            ok, ate = c.reservar("orcid.org", "u6")
            self.assertFalse(ok)
            self.assertEqual("2026-09-28T08:00:00+00:00", ate)
            agora[0] = T0 + timedelta(hours=23, minutes=59)
            self.assertEqual(0, CT.Contador24h(Path(d) / "C.json", agora=lambda: agora[0]).livres("orcid.org"))  # persiste
            agora[0] = T0 + timedelta(hours=24, seconds=1)
            self.assertEqual(5, CT.Contador24h(Path(d) / "C.json", agora=lambda: agora[0]).livres("orcid.org"))

    def test_robots_guardado_nao_gasta_pedido(self):
        with tempfile.TemporaryDirectory() as d:
            pedidos = []

            def falso(url):
                pedidos.append(url)
                return 200, b"User-agent: *\nAllow: /\n" if url.endswith("robots.txt") else b"{}"
            c = CT.Contador24h(Path(d) / "C.json", agora=lambda: T0)
            S.Transporte(Path(d), buscar=falso, pausa=0, contador=c).get("https://pub.orcid.org/a", "t")
            S.Transporte(Path(d), buscar=falso, pausa=0, contador=c).get("https://pub.orcid.org/b", "t")
            self.assertEqual(["https://pub.orcid.org/robots.txt", "https://pub.orcid.org/a", "https://pub.orcid.org/b"], pedidos)

    def test_robots_que_nao_cabe_deixa_a_pagina_pendente(self):
        with tempfile.TemporaryDirectory() as d:
            c = CT.Contador24h(Path(d) / "C.json", agora=lambda: T0)
            for i in range(5):
                c.reservar("uni.it", "x%d" % i)
            t = S.Transporte(Path(d), buscar=lambda u: (200, b""), pausa=0, contador=c)
            self.assertEqual((None, None), t.get("https://www.uni.it/p", "t"))
            self.assertEqual(("https://www.uni.it/p", "TETO_24H"), (t.registo[-1]["URL"], t.registo[-1]["RESULTADO"]))


class Canario(unittest.TestCase):
    def test_sem_canario_nao_ha_dia_e_canario_so_uma_vez(self):
        with tempfile.TemporaryDirectory() as d:
            rcs, e = correr(d, ("--dia", 0), ("--canario", 0), ("--canario", 1))
            self.assertEqual([2, 0, 2], rcs)
            self.assertEqual("POR_PESSOA", e["CANARIO"]["MODO"])          # o csv respondeu 400
            self.assertTrue(e["CANARIO"]["B_LOTE_BUSCA"]["FORMATO_OK"])
            self.assertEqual(4, e["CANARIO"]["PEDIDOS_ORCID"])             # robots + a + b + c

    def test_csv_com_links_da_o_modo_em_lote(self):
        with tempfile.TemporaryDirectory() as d:
            fx = Path(d) / "fx"
            shutil.copytree(FX, fx)
            r = json.loads((fx / "RESPOSTAS-ORCID.json").read_text(encoding="utf-8"))
            e = O.estado_novo(O.juntar(json.loads((FX / "PESSOAS.json").read_text(encoding="utf-8")),
                                       json.loads((FX / "ALVOS-LISTAS.json").read_text(encoding="utf-8"))["PESSOAS"]))
            lote = [p for p in e["PESSOAS"] if p["FASE"] == "LINKS"]
            r[O.url_csv(O.q_por_orcid(lote))] = {"TEXTO": "orcid,given-names,family-name,researcher-urls\n"
                                                           "0000-0000-0000-0002,Anna,Bianchi,https://bsky.app/profile/b\n"}
            (fx / "RESPOSTAS-ORCID.json").write_text(json.dumps(r), encoding="utf-8")
            _, e = correr(Path(d) / "s", ("--canario", 0), fx=fx)
            self.assertEqual("LOTE_COM_LINKS", e["CANARIO"]["MODO"])


class Dias(unittest.TestCase):
    def test_tres_dias_teto_pendentes_e_identidade(self):
        with tempfile.TemporaryDirectory() as d:
            rcs, e = correr(d, ("--canario", 0), ("--dia", 1), ("--dia", 25), ("--dia", 49))
            self.assertEqual([0, 0, 0, 0], rcs)
            self.assertLessEqual(orcid_em_24h(d), 5)
            self.assertEqual([1, 5, 3], [x["PEDIDOS_POR_DOMINIO"].get("orcid.org", 0) for x in e["DIAS"]])
            self.assertEqual("2026-09-28T08:00:00+00:00", e["DIAS"][0]["PROXIMO_DIA_A_PARTIR_DE"])
            por = {p["NOME"]: p for p in e["PESSOAS"]}
            self.assertEqual(["0000-0000-0000-0201"], por["Lorenzo Tonina"]["ORCID"])     # achado em lote, nome + casa
            self.assertEqual("SEM_ORCID", por["Mario Rossi"]["FASE"])   # o Mario Rossi de Padova NAO e o do CREA
            self.assertEqual("AMBIGUO", por["NERI Paolo"]["FASE"])      # dois ORCID possiveis: nao se funde
            self.assertEqual("AMBIGUO", por["GIALLI Sara"]["FASE"])
            self.assertIn("LINKEDIN_PERFIL", [c["PLATAFORMA"] for c in por["ROSSI Mario"]["NAO_ENTRAM"]])
            self.assertFalse(any("mailto" in c["URL"] for p in e["PESSOAS"] for c in p["CANAIS"]))
            self.assertEqual(0, e["DIAS"][-1]["PENDENTES"])

    def test_no_mesmo_dia_so_o_que_sobra(self):
        with tempfile.TemporaryDirectory() as d:
            _, e = correr(d, ("--canario", 0), ("--dia", 1), ("--dia", 2))
            self.assertEqual(0, e["DIAS"][-1]["PEDIDOS_POR_DOMINIO"].get("orcid.org", 0))
            self.assertLessEqual(orcid_em_24h(d), 5)

    def test_candidatas_numa_copia(self):
        with tempfile.TemporaryDirectory() as d:
            _, e = correr(d, ("--canario", 0), ("--dia", 1), ("--dia", 25), ("--dia", 49))
            fila = Path(d) / "FILA.json"
            fila.write_text(json.dumps({"CANDIDATAS": []}), encoding="utf-8")
            O.candidatar(e, fila)
            linhas = json.loads(fila.read_text(encoding="utf-8"))["CANDIDATAS"]
            self.assertTrue(linhas)
            self.assertFalse(any("/in/" in x["URL"] for x in linhas))
            self.assertTrue(all(x["PAIS"] == "IT" and x["PARA_QUE_SERVE"].startswith("D85") for x in linhas))


class Antigo(unittest.TestCase):
    def test_rodadas_antigas_recusadas(self):
        self.assertEqual(2, S.main(["x", "--rodada=1", "--autorizado", "--pessoas=%s" % (FX / "PESSOAS.json"), "--saida=x"]))

    def test_listas_oficiais_respeitam_o_contador_partilhado(self):
        with tempfile.TemporaryDirectory() as d:
            ctd = Path(d) / "CONTADOR-24H.json"
            base = ["x", "--seco", "--fixtures=%s" % FX, "--casa=FEM", "--alvos=%s" % (FX / "ALVOS-LISTAS.json"),
                    "--saida=%s" % d, "--contador=%s" % ctd]
            L.main(base + ["--agora=%s" % T0.isoformat()])
            L.main(base + ["--agora=%s" % (T0 + timedelta(hours=1)).isoformat()])     # mesmo dia: fmach.it esgotado
            pedidos = json.loads((Path(d) / "RODADA-FEM-02" / "PEDIDOS.json").read_text(encoding="utf-8"))
            self.assertEqual({}, pedidos["POR_DOMINIO"])
            self.assertEqual(1, len(json.loads((Path(d) / "ESTADO-FEM.json").read_text(encoding="utf-8"))["FILA"]))


if __name__ == "__main__":
    unittest.main()
