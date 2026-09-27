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

# NENHUM teste sai a rede: um mutante que desligue uma guarda chega aqui e para (26/09: um mutante da
# rodada antiga chegou a pedir o robots.txt real de pub.orcid.org antes desta guarda existir)
def _sem_rede(*a, **k):
    raise RuntimeError("rede pedida dentro de um teste")


S.Transporte._urllib = staticmethod(_sem_rede)
S.portao = lambda *a, **k: False

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
            t.get("https://www.uni.it/q", "t")          # o host nao fica marcado como proibido
            self.assertEqual("TETO_24H", t.registo[-1]["RESULTADO"])


class D91(unittest.TestCase):
    def test_lista_fechada_das_apis_oficiais(self):
        sim = ["https://pub.orcid.org/v3.0/0000-0000-0000-0001/researcher-urls", "https://pub.orcid.org/v3.0/expanded-search/?q=x",
               "https://api.openalex.org/authors?filter=orcid:x", "https://api.crossref.org/works?query=x"]
        nao = ["https://pub.orcid.org/v2.0/x", "http://pub.orcid.org/v3.0/x", "https://pub.orcid.org.evil.it/v3.0/x",
               "https://orcid.org/0000-0000-0000-0001", "https://pub.orcid.org:8443/v3.0/x", "https://www.fmach.it/persone",
               "https://www.crea.gov.it/web/difesa-e-certificazione", "https://openalex.org/works", "https://x.api.crossref.org/"]
        self.assertEqual([True] * len(sim), [S.api_oficial(u) for u in sim])
        self.assertEqual([False] * len(nao), [S.api_oficial(u) for u in nao])

    def test_pagina_comum_continua_a_respeitar_o_robots(self):
        with tempfile.TemporaryDirectory() as d:
            pedidos = []
            proibe = b"User-agent: *\nDisallow: /\n"

            def falso(url):
                pedidos.append(url)
                return 200, proibe if url.endswith("robots.txt") else b"{}"
            t = S.Transporte(Path(d), buscar=falso, pausa=0)
            self.assertEqual((None, None), t.get("https://www.unipd.it/persone/rossi", "t"))
            self.assertEqual(200, t.get("https://pub.orcid.org/v3.0/0000-0000-0000-0001/researcher-urls", "t")[0])
            self.assertEqual((None, None), t.get("https://pub.orcid.org/outra-coisa", "t"))   # fora da /v3.0/: robots
            self.assertEqual(["https://www.unipd.it/robots.txt", "https://pub.orcid.org/v3.0/0000-0000-0000-0001/researcher-urls",
                              "https://pub.orcid.org/robots.txt"], pedidos)

    def test_marcar_gasto_externo(self):
        with tempfile.TemporaryDirectory() as d:
            c = CT.Contador24h(Path(d) / "C.json", agora=lambda: T0)
            c.reservar("orcid.org", "u")
            self.assertEqual(4, c.marcar_gasto("orcid.org", T0 + timedelta(hours=12), "coordenacao"))
            self.assertEqual(0, c.livres("orcid.org"))
            antes = CT.Contador24h(Path(d) / "C.json", agora=lambda: T0 + timedelta(hours=11))
            self.assertEqual((False, (T0 + timedelta(hours=12)).isoformat()), antes.reservar("orcid.org", "v"))
            depois = CT.Contador24h(Path(d) / "C.json", agora=lambda: T0 + timedelta(hours=12, seconds=1))
            self.assertEqual(4, depois.livres("orcid.org"))          # o «u» das T0 ainda conta ate T0+24 h

    def test_marcar_gasto_nao_abre_vaga_antes_da_hora(self):
        # um pedido antigo que sai da janela ANTES de `ate` nao pode abrir vaga mais cedo (26/09: o robots das
        # 22:58Z abriria uma vaga as 19:58 de 27/09, antes das 20:20 da coordenacao)
        with tempfile.TemporaryDirectory() as d:
            CT.Contador24h(Path(d) / "C.json", agora=lambda: T0).reservar("orcid.org", "cedo")      # sai as T0+24h
            ate = T0 + timedelta(hours=24, minutes=22)
            c = CT.Contador24h(Path(d) / "C.json", agora=lambda: T0 + timedelta(hours=3))
            self.assertEqual(5, c.marcar_gasto("orcid.org", ate, "coordenacao"))
            quase = CT.Contador24h(Path(d) / "C.json", agora=lambda: T0 + timedelta(hours=24, minutes=10))
            self.assertEqual(0, quase.livres("orcid.org"))           # o «cedo» ja saiu, mas os 5 EXTERNO nao
            self.assertEqual(ate, datetime.fromisoformat(quase.proximo_livre("orcid.org")))


class Canario(unittest.TestCase):
    def test_sem_canario_nao_ha_dia_e_canario_so_uma_vez(self):
        with tempfile.TemporaryDirectory() as d:
            rcs, e = correr(d, ("--dia", 0), ("--canario", 0), ("--canario", 1))
            self.assertEqual([2, 0, 2], rcs)
            self.assertEqual("POR_PESSOA", e["CANARIO"]["MODO"])          # o csv respondeu 400
            self.assertTrue(e["CANARIO"]["B_LOTE_BUSCA"]["FORMATO_OK"])
            self.assertEqual(3, e["CANARIO"]["PEDIDOS_ORCID"])             # a + b + c (D91: API sem robots)

    def test_d91_api_oficial_nao_le_robots_mesmo_que_proiba(self):
        # o robots.txt REAL de pub.orcid.org (lido por acidente em 26/09) e «User-agent: * / Disallow: /»;
        # pela D91 a API publica oficial segue os termos da API, nao o robots do host
        with tempfile.TemporaryDirectory() as d:
            fx = Path(d) / "fx"
            shutil.copytree(FX, fx)
            r = json.loads((fx / "RESPOSTAS-ORCID.json").read_text(encoding="utf-8"))
            r["https://pub.orcid.org/robots.txt"] = {"TEXTO": "User-agent: *\nDisallow: /"}
            (fx / "RESPOSTAS-ORCID.json").write_text(json.dumps(r), encoding="utf-8")
            rcs, e = correr(Path(d) / "s", ("--canario", 0), fx=fx)
            self.assertEqual("POR_PESSOA", e["CANARIO"]["MODO"])
            self.assertEqual(3, e["CANARIO"]["PEDIDOS_ORCID"])          # a + b + c, sem robots
            ped = json.loads((Path(d) / "s" / "CANARIO-01" / "PEDIDOS.json").read_text(encoding="utf-8"))["PEDIDOS"]
            self.assertFalse([x for x in ped if x["URL"].endswith("robots.txt")])
            self.assertTrue(all(x.get("REGRA", "").startswith("API_PUBLICA_OFICIAL_D91") for x in ped if x["RESULTADO"] == "OK"))

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
            # D91: a API nao gasta pedido no robots -> canario 3, e o resto do 1.o dia sao 2 (identidade + 1 pessoa)
            self.assertEqual([2, 5, 0], [x["PEDIDOS_POR_DOMINIO"].get("orcid.org", 0) for x in e["DIAS"]])
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
            # nao se pede o que se sabe que nao cabe: nem uma linha TETO_24H para orcid.org
            ped = json.loads((Path(d) / e["DIAS"][-1]["PASTA"] / "PEDIDOS.json").read_text(encoding="utf-8"))["PEDIDOS"]
            self.assertFalse([x for x in ped if "orcid.org" in x["URL"]])
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
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(2, S.main(["x", "--rodada=1", "--autorizado", "--pessoas=%s" % (FX / "PESSOAS.json"),
                                        "--saida=%s" % d]))
            self.assertEqual([], list(Path(d).iterdir()))

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
